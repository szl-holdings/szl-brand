# SPDX-License-Identifier: Apache-2.0
# (c) 2026 Lutar, Stephen P. - SZL Holdings - ORCID 0009-0001-0110-4173
"""Gates for kanchay/, the vendor bundle of the founder-approved KANCHAY design system."""

from __future__ import annotations

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
SOURCE_KEYS = ["name", "version", "base", "layers", "source_commit", "license", "sha256"]


@pytest.fixture
def mirror(tmp_path):
    """A disposable copy of the bundle and its kit sources, laid out like the checkout."""

    shutil.copytree(EXPORT, tmp_path / "kanchay")
    for source in sorted(set(kanchay.BUNDLE.values())):
        destination = tmp_path / source
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / source, destination)
    return tmp_path


def _source() -> dict:
    return json.loads((EXPORT / "SOURCE.json").read_bytes())


def _shipped() -> set[str]:
    return {path.relative_to(EXPORT).as_posix() for path in EXPORT.rglob("*") if path.is_file()}


def test_bundle_files_are_byte_identical_to_kit_sources():
    for path, source in kanchay.BUNDLE.items():
        assert (EXPORT / path).read_bytes() == (ROOT / source).read_bytes(), (
            f"kanchay/{path} differs from {source}; run `python -m szl_brand kanchay-build`"
        )


def test_source_json_has_the_founder_shape_and_pins_every_file():
    source = _source()
    assert list(source) == SOURCE_KEYS
    assert source["name"] == "szl-kanchay"
    assert source["version"] == kanchay.VERSION == "1.3.0"
    assert "KANCHAY v1.3.0, founder-approved" in source["base"]
    assert source["layers"] == {"szl-console.css": "1.2.0 (operator console, additive)"}
    assert re.fullmatch(r"[0-9a-f]{40}", source["source_commit"])
    assert source["license"] == {"code": "Apache-2.0", "brand_assets": "CC BY 4.0"}
    assert list(source["sha256"]) == [*kanchay.BUNDLE, kanchay.TOKENS]
    for path, digest in source["sha256"].items():
        assert hashlib.sha256((EXPORT / path).read_bytes()).hexdigest() == digest, path


def test_committed_bundle_matches_the_build():
    for path, data in kanchay.build(ROOT).items():
        assert (EXPORT / path).read_bytes() == data, path
    assert _shipped() == set(kanchay.BUNDLE) | {kanchay.TOKENS} | kanchay.NON_PAYLOAD


def test_bundle_ships_no_webfont_and_no_withdrawn_gold_token():
    assert not [path for path in _shipped() if path.endswith((".woff", ".woff2", ".ttf", ".otf"))]
    for path in _shipped():
        data = (EXPORT / path).read_bytes()
        assert b"--color-a11oy-gold" not in data, path
    for sheet in ("szl-design-system.css", "szl-console.css"):
        css = (EXPORT / sheet).read_text(encoding="utf-8")
        assert "@font-face" not in css
        assert "@import" not in css


def test_every_console_variable_is_defined_by_the_two_stylesheets():
    assert kanchay.css_reference_errors(ROOT) == []


def test_check_passes_on_the_committed_tree():
    assert kanchay.check(ROOT) == []


def test_check_fails_when_a_kit_source_changes_without_rebuilding(mirror):
    source = mirror / "kit" / "tokens" / "szl-console.css"
    source.write_bytes(source.read_bytes() + b".extra { color: var(--text); }\n")
    errors = kanchay.check(mirror)
    assert any(error.startswith("kanchay/szl-console.css differs") for error in errors)
    assert any(error.startswith("kanchay/SOURCE.json differs") for error in errors)

    kanchay.write(mirror)
    assert kanchay.check(mirror) == []


def test_check_fails_when_a_bundle_file_is_tampered(mirror):
    logo = mirror / "kanchay" / "logos" / "szl_logo_horizontal.svg"
    logo.write_bytes(logo.read_bytes().replace(b"<svg", b"<svg data-x='1'", 1))
    assert kanchay.check(mirror) == [
        "kanchay/logos/szl_logo_horizontal.svg differs from kit/logos/szl_logo_horizontal.svg; "
        "run `python -m szl_brand kanchay-build` and commit the result"
    ]


def test_check_rejects_leftover_files_and_rebuild_removes_them(mirror):
    stray = mirror / "kanchay" / "fonts" / "Inter-latin.woff2"
    stray.parent.mkdir()
    stray.write_bytes(b"wOF2")
    assert kanchay.check(mirror) == ["kanchay/fonts/Inter-latin.woff2 is not part of the bundle"]

    kanchay.write(mirror)
    assert not stray.exists()
    assert kanchay.check(mirror) == []


def test_undefined_console_variable_is_reported(mirror):
    for name in ("kanchay/szl-console.css", "kit/tokens/szl-console.css"):
        path = mirror / name
        path.write_bytes(
            path.read_bytes() + b".x { color: var(--ink-nope); width: var(--w, 1px); }\n"
        )
    kanchay.write(mirror)
    assert kanchay.check(mirror) == ["szl-console.css: var(--ink-nope) is not defined"]


def test_source_commit_must_be_an_exact_sha(mirror):
    with pytest.raises(ValueError, match="40-character"):
        kanchay.write(mirror, "main")


def test_cli_check_passes_then_reports_drift(mirror):
    command = [sys.executable, "-m", "szl_brand", "kanchay-build", "--check"]
    passed = subprocess.run(command, capture_output=True, text=True)
    assert passed.returncode == 0, passed.stderr
    assert "matches kit/" in passed.stdout

    css = mirror / "kanchay" / "szl-design-system.css"
    css.write_bytes(css.read_bytes() + b"/* hand edit */\n")
    failed = subprocess.run([*command, "--root", str(mirror)], capture_output=True, text=True)
    assert failed.returncode == 1
    assert "kanchay/szl-design-system.css differs" in failed.stderr


def test_tokens_file_is_every_design_system_token_and_nothing_else():
    tokens = (EXPORT / kanchay.TOKENS).read_text(encoding="utf-8")
    system = (EXPORT / "szl-design-system.css").read_text(encoding="utf-8")
    assert tokens == kanchay.extract_tokens(system)
    preludes = [prelude for prelude, _ in kanchay._top_level_blocks(tokens)]
    assert preludes and all(kanchay._TOKEN_SELECTOR_RE.fullmatch(p) for p in preludes)
    assert ':root, [data-surface="dark"]' in preludes and '[data-surface="light"]' in preludes
    definitions = re.compile(r"(--[A-Za-z0-9_-]+)\s*:")
    token_blocks = [
        body
        for prelude, body in kanchay._top_level_blocks(system)
        if kanchay._TOKEN_SELECTOR_RE.fullmatch(prelude)
    ]
    expected = {name for body in token_blocks for name in definitions.findall(body)}
    assert set(definitions.findall(tokens)) == expected
    assert "@font-face" not in tokens and "@import" not in tokens


def test_extract_tokens_rejects_a_token_block_with_a_style_declaration():
    with pytest.raises(ValueError, match="non-token declaration"):
        kanchay.extract_tokens(":root { --a: 1px; color: red; }")
