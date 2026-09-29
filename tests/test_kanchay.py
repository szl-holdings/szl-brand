# SPDX-License-Identifier: Apache-2.0
# (c) 2026 Lutar, Stephen P. - SZL Holdings - ORCID 0009-0001-0110-4173
"""Drift, integrity and reference gates for the vendorable KANCHAY web export."""

from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from szl_brand import kanchay

ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "kanchay"
NON_PAYLOAD = {"SOURCE.json", "README.md", "fonts/OFL.txt", "fonts/LICENSE-Syncopate.txt"}


@pytest.fixture
def mirror(tmp_path):
    """A disposable copy of the export and its sources, laid out like the checkout."""

    shutil.copytree(EXPORT, tmp_path / "kanchay")
    shutil.copytree(ROOT / "kit" / "kanchay", tmp_path / "kit" / "kanchay")
    return tmp_path


def _tokens() -> dict:
    return kanchay.load_tokens(ROOT)


def _token(tokens: dict, name: str) -> dict:
    for family in ("color", "spacing", "radius"):
        for token in tokens[family]["tokens"]:
            if token["name"] == name:
                return token
    raise KeyError(name)


def test_committed_export_matches_generator_byte_for_byte():
    built = kanchay.build(ROOT)
    assert set(built) == set(kanchay.GENERATED)
    for name, data in built.items():
        assert (EXPORT / name).read_bytes() == data, (
            f"kanchay/{name} drifted; run `python -m szl_brand kanchay-build`"
        )


def test_source_json_pins_every_payload_file():
    source = json.loads((EXPORT / "SOURCE.json").read_bytes())
    assert source["name"] == "szl-kanchay"
    assert source["version"] == kanchay.VERSION == "1.0.0"
    assert source["canonical"] == "szl-holdings/szl-brand (kanchay/)"
    assert list(source["sha256"]) == kanchay.payload_paths(EXPORT)
    for path, digest in source["sha256"].items():
        assert hashlib.sha256((EXPORT / path).read_bytes()).hexdigest() == digest, path

    shipped = {path.relative_to(EXPORT).as_posix() for path in EXPORT.rglob("*") if path.is_file()}
    assert shipped - set(source["sha256"]) == NON_PAYLOAD


def test_every_token_reference_in_tokens_json_resolves():
    tokens = _tokens()
    references = [
        value
        for token in tokens["color"]["tokens"]
        for value in (
            token["value"].values() if isinstance(token["value"], dict) else [token["value"]]
        )
        if isinstance(value, str) and value.startswith("{")
    ]
    assert len(references) > 20
    assert kanchay.alias_errors(tokens) == []


def test_every_css_variable_reference_is_defined():
    assert kanchay.css_reference_errors(ROOT) == []


def test_fonts_are_local_and_present():
    css = (EXPORT / "kanchay.css").read_text(encoding="utf-8")
    components = (EXPORT / "kanchay-components.css").read_text(encoding="utf-8")
    assert "@import" not in css + components
    assert "googleapis" not in css + components
    urls = re.findall(r"url\('([^']+)'\)", css)
    assert urls == [
        "./fonts/SpaceGrotesk-latin.woff2",
        "./fonts/Inter-latin.woff2",
        "./fonts/JetBrainsMono-latin.woff2",
    ]
    for url in urls:
        assert (EXPORT / url).is_file(), url


def test_dark_is_default_and_light_is_opt_in():
    css = (EXPORT / "kanchay.css").read_text(encoding="utf-8")
    assert ":root {\n  color-scheme: dark;" in css
    assert ':root[data-theme="light"], [data-theme="light"] {\n  color-scheme: light;' in css


def test_check_passes_on_the_committed_tree():
    assert kanchay.check(ROOT) == []


def test_check_fails_when_tokens_change_without_regenerating(mirror):
    tokens_path = mirror / "kanchay" / "tokens.json"
    tokens = json.loads(tokens_path.read_bytes())
    _token(tokens, "radius-sm")["value"] = "5px"
    tokens_path.write_bytes(json.dumps(tokens, indent=1).encode("utf-8"))

    errors = kanchay.check(mirror)
    assert any(error.startswith("kanchay/kanchay.css drifted") for error in errors)
    assert any(error.startswith("kanchay/SOURCE.json drifted") for error in errors)

    kanchay.write(mirror)
    assert kanchay.check(mirror) == []
    assert "--radius-sm: 5px;" in (mirror / "kanchay" / "kanchay.css").read_text(encoding="utf-8")


def test_check_fails_when_component_source_changes(mirror):
    source = mirror / "kit" / "kanchay" / "components.css"
    source.write_bytes(source.read_bytes() + b".kc-new { color: var(--color-a11oy-text); }\n")
    errors = kanchay.check(mirror)
    assert any(error.startswith("kanchay/kanchay-components.css drifted") for error in errors)


def test_check_fails_when_a_payload_file_is_tampered(mirror):
    mark = mirror / "kanchay" / "marks" / "szl-mark.svg"
    mark.write_bytes(mark.read_bytes().replace(b"<svg", b"<svg data-x='1'", 1))
    errors = kanchay.check(mirror)
    assert errors == [
        "kanchay/SOURCE.json drifted from its sources; "
        "run `python -m szl_brand kanchay-build` and commit the result"
    ]


def _break(tokens: dict, case: str) -> None:
    if case == "undefined":
        _token(tokens, "gold")["value"] = "{color-a11oy-nope}"
    elif case == "cycle":
        _token(tokens, "line")["value"] = "{line}"
    elif case == "theme":
        _token(tokens, "color-a11oy-bg")["value"]["sepia"] = "#111111"
    elif case == "malformed":
        _token(tokens, "cream")["value"] = "{color-a11oy-text} 50%"
    elif case == "family":
        tokens["type"]["groups"][0]["family"] = "serif"


@pytest.mark.parametrize(
    ("case", "message"),
    [
        ("undefined", "{color-a11oy-nope} is not a defined token"),
        ("cycle", "reference cycle line -> line"),
        ("theme", "unknown theme(s) sepia"),
        ("malformed", "malformed reference"),
        ("family", "font family 'serif' is not defined"),
    ],
)
def test_alias_check_rejects_unresolvable_references(case, message):
    tokens = copy.deepcopy(_tokens())
    _break(tokens, case)
    errors = kanchay.alias_errors(tokens)
    assert any(message in error for error in errors), errors


def test_components_source_must_open_with_spdx_and_use_lf():
    with pytest.raises(ValueError, match="SPDX"):
        kanchay.render_components_css("body { margin: 0; }\n")
    with pytest.raises(ValueError, match="LF"):
        kanchay.render_components_css("/* SPDX-License-Identifier: Apache-2.0 */\r\nbody {}\r\n")


def test_cli_check_passes_then_reports_drift(mirror):
    command = [sys.executable, "-m", "szl_brand", "kanchay-build", "--check"]
    passed = subprocess.run(command, capture_output=True, text=True)
    assert passed.returncode == 0, passed.stderr
    assert "matches its sources" in passed.stdout

    css = mirror / "kanchay" / "kanchay.css"
    css.write_bytes(css.read_bytes() + b"/* hand edit */\n")
    failed = subprocess.run([*command, "--root", str(mirror)], capture_output=True, text=True)
    assert failed.returncode == 1
    assert "kanchay/kanchay.css drifted" in failed.stderr
