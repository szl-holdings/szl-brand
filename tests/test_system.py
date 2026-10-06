"""Executable contract tests for the versioned KANCHAY design system."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

import szl_brand.system as system_module
from szl_brand.palette import Color

CONTRACT = system_module.CONTRACT
export_system = system_module.export_system
verify_system = system_module.verify_system

REVISION = "a" * 40


@pytest.fixture(autouse=True)
def _bind_test_assets_to_revision(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    assets = {
        export_name: (root / source_path).read_bytes()
        for export_name, source_path in system_module._ASSETS
    }
    monkeypatch.setattr(system_module, "_source_bundle", lambda: (assets, REVISION))


def _snapshot(directory):
    return {path.name: path.read_bytes() for path in sorted(directory.iterdir())}


def test_export_is_byte_deterministic(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    export_system(first, REVISION)
    export_system(second, REVISION)
    assert _snapshot(first) == _snapshot(second)


def test_manifest_pins_source_and_every_asset(tmp_path):
    output = tmp_path / "system"
    manifest_path = export_system(output, REVISION)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["contract"] == CONTRACT
    assert manifest["version"] == "1.2.0"
    assert manifest["source"]["revision"] == REVISION
    assert {record["path"] for record in manifest["assets"]} == {
        "system.css",
        "tokens.json",
        "metadata.schema.json",
        "vitepress.css",
        "khipu-command-system.css",
        "khipu-command-system.schema.json",
        "khipu-command-system.example.json",
        "repository-readme-template.md",
        "org-card-template.md",
        "repository-hero-template.svg",
        "org-card-template.svg",
        "executive-brief-template.html",
    }
    assert verify_system(output) == []


@pytest.mark.parametrize("revision", ["main", "A" * 40, "f" * 39, "../main"])
def test_export_rejects_mutable_or_malformed_revision(tmp_path, revision):
    with pytest.raises(ValueError, match="exact lowercase 40-character Git SHA"):
        export_system(tmp_path / "system", revision)


def test_export_rejects_well_formed_revision_not_bound_to_assets(tmp_path):
    with pytest.raises(ValueError, match="does not match exported source"):
        export_system(tmp_path / "system", "b" * 40)


def test_checkout_source_reads_only_canonical_revision_bytes(tmp_path, monkeypatch):
    committed: dict[str, bytes] = {}
    for export_name, source_path in system_module._ASSETS:
        data = f"{export_name}\n".encode()
        path = tmp_path / source_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        committed[source_path] = data

    def fake_git(_root, *arguments):
        if arguments == ("remote", "get-url", "origin"):
            return b"https://github.com/szl-holdings/szl-brand.git\n"
        if arguments == ("rev-parse", "--verify", "HEAD"):
            return f"{REVISION}\n".encode()
        if arguments[0] == "show":
            return committed[arguments[1].split(":", 1)[1]]
        raise AssertionError(arguments)

    monkeypatch.setattr(system_module, "_git", fake_git)
    assets, revision = system_module._checkout_source(tmp_path)
    assert revision == REVISION
    assert assets["system.css"] == b"system.css\n"

    (tmp_path / system_module._ASSETS[0][1]).write_bytes(b"dirty")
    assets, _revision = system_module._checkout_source(tmp_path)
    assert assets["system.css"] == b"system.css\n"


def test_checkout_source_rejects_noncanonical_repository(tmp_path, monkeypatch):
    monkeypatch.setattr(
        system_module,
        "_git",
        lambda _root, *arguments: b"https://github.com/example/fork.git\n",
    )
    with pytest.raises(ValueError, match="source repository is not canonical"):
        system_module._checkout_source(tmp_path)


def test_packaged_source_requires_hash_bound_provenance(tmp_path, monkeypatch):
    package_root = tmp_path / "package"
    design_system = package_root / "design_system"
    design_system.mkdir(parents=True)
    recorded: dict[str, str] = {}
    for export_name, _source_path in system_module._ASSETS:
        data = f"packaged {export_name}\n".encode()
        (design_system / export_name).write_bytes(data)
        recorded[export_name] = system_module._sha256(data)
    (design_system / "source-provenance.json").write_text(
        json.dumps(
            {
                "contract": system_module._SOURCE_PROVENANCE_CONTRACT,
                "repository": system_module._SOURCE_REPOSITORY,
                "revision": REVISION,
                "assets": recorded,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(system_module.resources, "files", lambda _package: package_root)

    assets, revision = system_module._packaged_source()
    assert revision == REVISION
    assert set(assets) == recorded.keys()

    (design_system / "system.css").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="asset provenance mismatch: system.css"):
        system_module._packaged_source()


def test_export_refuses_asset_symlink_without_touching_target(tmp_path):
    output = tmp_path / "system"
    output.mkdir()
    outside = tmp_path / "outside.css"
    outside.write_text("guarded", encoding="utf-8")
    destination = output / "system.css"
    try:
        destination.symlink_to(outside)
    except OSError:
        pytest.skip("symlink creation is unavailable on this platform")

    with pytest.raises(ValueError, match="output symlink is forbidden: system.css"):
        export_system(output, REVISION)

    assert outside.read_text(encoding="utf-8") == "guarded"


def test_verifier_detects_tamper(tmp_path):
    output = tmp_path / "system"
    export_system(output, REVISION)
    (output / "system.css").write_text("tampered", encoding="utf-8")
    assert verify_system(output) == [
        "hash mismatch: system.css",
        "size mismatch: system.css",
        "bundle root mismatch",
    ]


def test_verifier_fails_closed_on_malformed_manifest(tmp_path):
    output = tmp_path / "system"
    manifest_path = export_system(output, REVISION)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["source"]["revision"] = "main"
    manifest["assets"] = {"path": "system.css"}
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    assert verify_system(output) == [
        "source revision is not immutable: 'main'",
        "assets must be an array",
    ]


def test_verifier_rejects_unmanifested_entry(tmp_path):
    output = tmp_path / "system"
    export_system(output, REVISION)
    (output / "injected.js").write_text("alert('not admitted')", encoding="utf-8")

    assert verify_system(output) == ["unexpected bundle entry: injected.js"]


def test_verifier_rejects_symlinked_manifest(tmp_path, monkeypatch):
    output = tmp_path / "system"
    manifest_path = export_system(output, REVISION)
    original_is_symlink = Path.is_symlink
    monkeypatch.setattr(
        Path,
        "is_symlink",
        lambda path: path == manifest_path or original_is_symlink(path),
    )

    assert verify_system(output) == ["manifest.json symlink is forbidden"]


def test_verifier_reports_unreadable_asset(tmp_path, monkeypatch):
    output = tmp_path / "system"
    export_system(output, REVISION)
    original_read_bytes = Path.read_bytes

    def read_bytes(path):
        if path.name == "system.css":
            raise OSError("simulated read failure")
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", read_bytes)

    assert verify_system(output) == [
        "asset is unreadable: system.css",
        "bundle root mismatch",
    ]


def test_accessibility_and_network_contracts_are_explicit(tmp_path):
    output = tmp_path / "system"
    export_system(output, REVISION)
    system_css = (output / "system.css").read_text(encoding="utf-8")
    adapter_css = (output / "vitepress.css").read_text(encoding="utf-8")

    assert "prefers-reduced-motion: reduce" in system_css
    assert ":focus-visible" in system_css
    assert "forced-colors: active" in adapter_css
    assert "http://" not in adapter_css
    assert "https://" not in adapter_css


def test_metadata_schema_requires_truth_and_evidence(tmp_path):
    output = tmp_path / "system"
    export_system(output, REVISION)
    schema = json.loads((output / "metadata.schema.json").read_text(encoding="utf-8"))

    assert schema["additionalProperties"] is False
    assert {"status", "sourceUrl", "evidenceUrl"} <= set(schema["required"])
    assert schema["properties"]["status"]["enum"] == [
        "REAL",
        "MEASURED",
        "MODELED",
        "ROADMAP",
        "UNAVAILABLE",
    ]
    Draft202012Validator.check_schema(schema)


def test_metadata_schema_accepts_evidenced_surface_and_rejects_overclaim(tmp_path):
    output = tmp_path / "system"
    export_system(output, REVISION)
    schema = json.loads((output / "metadata.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)
    record = {
        "title": "KANCHAY design system documentation",
        "description": "Versioned components and evidence conventions for SZL public surfaces.",
        "canonicalUrl": "https://holdings.a-11-oy.com/docs-site/brand.html",
        "surface": "documentation",
        "status": "REAL",
        "sourceUrl": "https://github.com/szl-holdings/szl-brand",
        "evidenceUrl": "https://github.com/szl-holdings/szl-brand/actions",
    }
    validator.validate(record)

    record["status"] = "FULLY VERIFIED"
    with pytest.raises(ValidationError):
        validator.validate(record)


@pytest.mark.parametrize(
    "bad_url",
    [
        "https://",
        "https://not a url",
        "http://github.com/szl-holdings",
        "https://foo..example.com",
        "https://foo.-bar.example.com",
        "https://foo.bar-.example.com",
        "https://example.com/%ZZ",
        "https://example.com/<script>",
        "https://example.com/raw\\path",
    ],
)
def test_metadata_schema_rejects_invalid_urls_without_format_checker(tmp_path, bad_url):
    output = tmp_path / "system"
    export_system(output, REVISION)
    schema = json.loads((output / "metadata.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    record = {
        "title": "KANCHAY design system documentation",
        "description": "Versioned components and evidence conventions for SZL public surfaces.",
        "canonicalUrl": bad_url,
        "surface": "documentation",
        "status": "REAL",
        "sourceUrl": "https://github.com/szl-holdings/szl-brand",
        "evidenceUrl": "https://github.com/szl-holdings/szl-brand/actions",
    }
    with pytest.raises(ValidationError):
        validator.validate(record)


def test_metadata_schema_accepts_valid_escaped_path_without_format_checker(tmp_path):
    output = tmp_path / "system"
    export_system(output, REVISION)
    schema = json.loads((output / "metadata.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    validator.validate(
        {
            "title": "KANCHAY design system documentation",
            "description": "Versioned components and evidence conventions for SZL public surfaces.",
            "canonicalUrl": "https://example.com/evidence/receipt%20one?view=full#integrity",
            "surface": "documentation",
            "status": "REAL",
            "sourceUrl": "https://github.com/szl-holdings/szl-brand",
            "evidenceUrl": "https://github.com/szl-holdings/szl-brand/actions",
        }
    )


def test_light_mode_status_and_focus_colors_meet_contrast_contract():
    light_background = Color.from_hex("#fbfcfe")
    status_colors = {
        "live": Color.from_hex("#116b3d"),
        "simulated": Color.from_hex("#6b4f00"),
        "unavailable": Color.from_hex("#9f281e"),
    }
    focus_indicator = Color.from_hex("#083f3e")

    for status, color in status_colors.items():
        assert color.contrast_ratio(light_background) >= 4.5, status
    assert focus_indicator.contrast_ratio(light_background) >= 3.0

    css = (Path(__file__).resolve().parents[1] / "kit/tokens/szl-design-system.css").read_text(
        encoding="utf-8"
    )
    light = _surface_tokens(css, "light")
    assert _resolve_hex(light, "chip-ok") == status_colors["live"]
    assert _resolve_hex(light, "chip-warn") == status_colors["simulated"]
    assert _resolve_hex(light, "chip-bad") == status_colors["unavailable"]
    assert ".chip-live       { color:var(--chip-ok); }" in css
    assert ".chip-simulated  { color:var(--chip-warn); }" in css
    assert ".chip-unavailable { color:var(--chip-bad); }" in css


FOCUS_SELECTOR = ":where(a,button,input,select,textarea,[tabindex]):focus-visible"
# Grounds a focusable control can sit on. The outline is offset outside the control, so it
# is drawn against the ground, not against the control's own fill.
FOCUS_GROUNDS = ("bg", "bg-deep", "surface", "surface-alt", "surface-raised")


def _custom_properties(css: str, selector: str) -> dict[str, str]:
    """Return every ``--name: value`` declared in the top-level blocks for ``selector``."""

    blocks = re.findall(rf"(?m)^{re.escape(selector)}\s*\{{(?P<body>[^}}]*)\}}", css)
    assert blocks, selector
    return {
        name: value.strip()
        for body in blocks
        for name, value in re.findall(r"--([\w-]+)\s*:\s*([^;]+);", body)
    }


DARK_POLARITY = ':root, [data-surface="dark"]'
LIGHT_POLARITY = '[data-surface="light"]'


def _surface_tokens(css: str, surface: str) -> dict[str, str]:
    """Return the tokens an element on ``surface`` resolves: the palette plus that polarity."""

    palette = _custom_properties(css, ":root")
    dark = {**palette, **_custom_properties(css, DARK_POLARITY)}
    if surface == "dark":
        return dark
    return {**dark, **_custom_properties(css, LIGHT_POLARITY)}


def _resolve_hex(tokens: dict[str, str], name: str) -> Color:
    value = tokens[name]
    while reference := re.fullmatch(r"var\(--([\w-]+)\)", value):
        value = tokens[reference.group(1)]
    assert re.fullmatch(r"#[0-9A-Fa-f]{6}", value), f"--{name} does not resolve to an opaque hex"
    return Color.from_hex(value)


@pytest.mark.parametrize(
    "path", ["kit/tokens/szl-design-system.css", "kanchay/szl-design-system.css"]
)
def test_base_focus_rule_draws_a_solid_outline_that_meets_3_to_1(path):
    css = (Path(__file__).resolve().parents[1] / path).read_text(encoding="utf-8")

    assert css.count(f"{FOCUS_SELECTOR} {{") == 1
    body = css.split(f"{FOCUS_SELECTOR} {{", 1)[1].split("}", 1)[0]
    rule = dict(
        (name.strip(), value.strip())
        for name, value in (part.split(":", 1) for part in body.split(";") if part.strip())
    )
    # The 55% --shadow-focus halo alone measures 2.81:1 on dark --bg and 2.32:1 on light --bg,
    # under the 3:1 non-text floor, so the indicator is a solid --focus outline and the halo
    # only softens it.
    assert rule == {
        "outline": "2px solid var(--focus)",
        "outline-offset": "2px",
        "box-shadow": "var(--shadow-focus)",
        "border-radius": "var(--radius-sm)",
    }

    for surface in ("dark", "light"):
        tokens = _surface_tokens(css, surface)
        focus = _resolve_hex(tokens, "focus")
        for ground in FOCUS_GROUNDS:
            ratio = focus.contrast_ratio(_resolve_hex(tokens, ground))
            assert ratio >= 3.0, f"{surface} --focus on --{ground}: {ratio:.2f}:1"


@pytest.mark.parametrize(
    "path", ["kit/tokens/szl-design-system.css", "kanchay/szl-design-system.css"]
)
def test_a_surface_declared_on_any_element_re_resolves_every_role(path):
    css = (Path(__file__).resolve().parents[1] / path).read_text(encoding="utf-8")
    dark = _custom_properties(css, DARK_POLARITY)
    light = _custom_properties(css, LIGHT_POLARITY)

    # A dark panel inside a light page, or the reverse, must not inherit any role from the
    # page around it, so both polarities declare the same roles.
    assert set(dark) == set(light)
    # Roles derived from a polarity token re-resolve on every surface root.
    derived = _custom_properties(css, ':root, [data-surface="dark"], [data-surface="light"]')
    assert derived["shadow-focus"].startswith("0 0 0 3px color-mix(in srgb, var(--focus)")
    assert "shadow-focus" not in _custom_properties(css, ":root")
    assert ':where([data-surface="dark"], [data-surface="light"]) { color:var(--text); }' in css
    # A descendant rule keyed on the page polarity would leak into a nested surface.
    assert not re.search(r'\[data-surface="(?:light|dark)"\]\s+[^\s{,]', css)

    for surface in ("dark", "light"):
        tokens = _surface_tokens(css, surface)
        for ink in ("chip-ok", "chip-warn", "chip-bad"):
            for ground in ("bg", "surface", "surface-alt"):
                ratio = _resolve_hex(tokens, ink).contrast_ratio(_resolve_hex(tokens, ground))
                assert ratio >= 4.5, f"{surface} --{ink} on --{ground}: {ratio:.2f}:1"


@pytest.mark.parametrize("path", ["kit/tokens/szl-console.css", "kanchay/szl-console.css"])
def test_console_status_inks_follow_the_nearest_surface(path):
    css = (Path(__file__).resolve().parents[1] / path).read_text(encoding="utf-8")
    dark = _custom_properties(css, DARK_POLARITY)
    light = _custom_properties(css, LIGHT_POLARITY)

    assert set(dark) == set(light) >= {"ink-good", "ink-warn", "ink-bad", "ink-info"}
    assert not re.search(r"(?m)^:root\s*\{", css)
    assert not re.search(r'\[data-surface="(?:light|dark)"\]\s+[^\s{,]', css)


def test_control_target_uses_a_sizable_display_mode():
    css = (Path(__file__).resolve().parents[1] / "kit/tokens/szl-design-system.css").read_text(
        encoding="utf-8"
    )
    rule = re.search(r"\.control-target\s*\{(?P<body>[^}]*)\}", css)

    assert rule is not None
    assert "display:inline-flex" in rule.group("body")
    assert "min-inline-size:var(--target-size-min)" in rule.group("body")
    assert "min-block-size:var(--target-size-min)" in rule.group("body")
