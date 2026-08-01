"""Executable contract tests for the versioned KANCHAY design system."""

from __future__ import annotations

import json

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from szl_brand.palette import Color
from szl_brand.system import CONTRACT, export_system, verify_system

REVISION = "a" * 40


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
    assert manifest["version"] == "1.1.0"
    assert manifest["source"]["revision"] == REVISION
    assert {record["path"] for record in manifest["assets"]} == {
        "system.css",
        "tokens.json",
        "metadata.schema.json",
        "vitepress.css",
    }
    assert verify_system(output) == []


@pytest.mark.parametrize("revision", ["main", "A" * 40, "f" * 39, "../main"])
def test_export_rejects_mutable_or_malformed_revision(tmp_path, revision):
    with pytest.raises(ValueError, match="exact lowercase 40-character Git SHA"):
        export_system(tmp_path / "system", revision)


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
    "bad_url", ["https://", "https://not a url", "http://github.com/szl-holdings"]
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


def test_light_mode_status_and_focus_colors_meet_contrast_contract():
    light_background = Color.from_hex("#f9fafc")
    real_status = Color.from_hex("#116b3d")
    focus_indicator = Color.from_hex("#083f3e")

    assert real_status.contrast_ratio(light_background) >= 4.5
    assert focus_indicator.contrast_ratio(light_background) >= 3.0
