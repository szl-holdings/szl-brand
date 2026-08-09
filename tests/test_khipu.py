"""Executable contract tests for the KHIPU Command System."""

from __future__ import annotations

import copy
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from jsonschema import Draft202012Validator

from szl_brand.khipu import (
    CONTRACT,
    MINIMUM_TARGET_CSS_PX,
    REQUIRED_VIEWPORTS,
    REQUIRED_ZOOM_PERCENT,
    validate_surface,
    validate_surface_file,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "kit" / "contracts"
TEMPLATES = ROOT / "kit" / "templates" / "khipu-command-system"
PATTERNS = ROOT / "kit" / "patterns"


def _example() -> dict[str, object]:
    return json.loads((CONTRACTS / "khipu-command-system.example.json").read_text(encoding="utf-8"))


def test_example_matches_json_schema_and_runtime_validator():
    schema = json.loads(
        (CONTRACTS / "khipu-command-system.schema.json").read_text(encoding="utf-8")
    )
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(
        schema,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    example = _example()

    validator.validate(example)
    assert example["contract"] == CONTRACT
    assert validate_surface(example) == []
    assert validate_surface_file(CONTRACTS / "khipu-command-system.example.json") == []


def test_release_refuses_sample_revision_and_manifest_root():
    record = _example()
    record["recordKind"] = "RELEASE"

    assert validate_surface(record) == [
        "$.source.kanchayManifestRoot must not be the sample zero digest for RELEASE",
        "$.source.revision must not be the sample zero revision for RELEASE",
    ]


def test_required_viewports_zoom_and_accessibility_cannot_drift():
    record = _example()
    record["responsive"]["testedViewportsCssPx"] = [390, 768, 1024, 1440]
    record["responsive"]["zoomPercent"] = [200]
    record["accessibility"]["minimumTargetCssPx"] = 40
    record["accessibility"]["reducedMotion"] = False

    errors = validate_surface(record)
    assert f"$.responsive.testedViewportsCssPx must equal {list(REQUIRED_VIEWPORTS)}" in errors
    assert f"$.responsive.zoomPercent must equal {list(REQUIRED_ZOOM_PERCENT)}" in errors
    assert f"$.accessibility.minimumTargetCssPx must equal {MINIMUM_TARGET_CSS_PX!r}" in errors
    assert "$.accessibility.reducedMotion must equal True" in errors


def test_current_operational_state_requires_timestamp():
    record = _example()
    record["evidence"][0]["operationalState"] = "OPERATIONAL"

    assert (
        "$.evidence[0].observedAt is required for current operational states"
        in validate_surface(record)
    )


def test_unknown_fields_and_credentialed_or_insecure_urls_fail_closed():
    record = _example()
    record["unexpected"] = True
    record["links"]["source"] = "http://example.invalid/source"
    record["links"]["evidence"] = "https://user:password@example.invalid/evidence"

    errors = validate_surface(record)
    assert "$.unexpected is not allowed" in errors
    assert "$.links.source must be an absolute HTTPS URL" in errors
    assert "$.links.evidence must not include credentials" in errors


def test_schema_and_runtime_reject_malformed_https_urls_without_format_checker():
    schema = json.loads(
        (CONTRACTS / "khipu-command-system.schema.json").read_text(encoding="utf-8")
    )
    validator = Draft202012Validator(schema)

    for bad_url in (
        "https://",
        "https://not a url",
        "https://foo..example.com",
        "https://foo.-bar.example.com",
        "https://example.com:0/source",
        "https://example.com:00000/source",
        "https://example.com:65536/source",
        "https://example.com:99999/source",
        "https://example.com/%ZZ",
        "https://example.com/raw\\path",
    ):
        record = _example()
        record["links"]["source"] = bad_url
        assert list(validator.iter_errors(record)), bad_url
        assert "$.links.source must be an absolute HTTPS URL" in validate_surface(record)

    for good_url in (
        "https://example.com:1/source",
        "https://example.com:443/source",
        "https://example.com:65535/source",
    ):
        record = _example()
        record["links"]["source"] = good_url
        assert list(validator.iter_errors(record)) == []
        assert validate_surface(record) == []


def test_schema_and_runtime_require_strict_rfc3339_timestamps():
    schema = json.loads(
        (CONTRACTS / "khipu-command-system.schema.json").read_text(encoding="utf-8")
    )
    validator = Draft202012Validator(
        schema,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )

    for bad_timestamp in (
        "2026-01-01 00:00:00+00:00",
        "2026-01-01T00:00:00+0000",
        "2026-01-01T00:00Z",
        "2026-13-01T00:00:00Z",
    ):
        record = _example()
        record["evidence"][0]["operationalState"] = "OPERATIONAL"
        record["evidence"][0]["observedAt"] = bad_timestamp
        assert list(validator.iter_errors(record)), bad_timestamp
        assert "$.evidence[0].observedAt must be an RFC 3339 timestamp" in validate_surface(record)

    for good_timestamp in (
        "2026-01-01T00:00:00Z",
        "2026-01-01T00:00:00.123456+05:30",
    ):
        record = _example()
        record["evidence"][0]["operationalState"] = "OPERATIONAL"
        record["evidence"][0]["observedAt"] = good_timestamp
        assert list(validator.iter_errors(record)) == []
        assert validate_surface(record) == []


def test_schema_and_runtime_reject_untrimmed_or_control_text():
    schema = json.loads(
        (CONTRACTS / "khipu-command-system.schema.json").read_text(encoding="utf-8")
    )
    validator = Draft202012Validator(schema)

    for bad_text in ("   ", " leading", "trailing ", "line one\nline two"):
        record = _example()
        record["executiveBrief"]["outcome"] = bad_text
        assert list(validator.iter_errors(record)), repr(bad_text)
        assert any(
            error.startswith("$.executiveBrief.outcome ") for error in validate_surface(record)
        )


def test_validation_does_not_mutate_the_caller_document():
    record = _example()
    before = copy.deepcopy(record)
    validate_surface(record)
    assert record == before


def test_css_consumes_kanchay_and_encodes_all_acceptance_widths():
    css = (PATTERNS / "khipu-command-system.css").read_text(encoding="utf-8")

    assert "--kcs-target-size: 44px" in css
    assert ":focus-visible" in css
    assert "prefers-reduced-motion: reduce" in css
    assert "forced-colors: active" in css
    assert "@media (max-width: 389px)" in css
    for width in (390, 768, 1024, 1440):
        assert f"@media (min-width: {width}px)" in css
    assert "min-inline-size: var(--kcs-target-size)" in css
    assert "min-block-size: var(--kcs-target-size)" in css
    assert re.search(r"--color-[a-z0-9-]+\s*:", css) is None
    assert "http://" not in css
    assert "https://" not in css


def test_svg_templates_are_responsive_accessible_and_self_contained():
    for name, view_box in (
        ("repository-hero-template.svg", "0 0 1440 720"),
        ("org-card-template.svg", "0 0 1600 800"),
    ):
        path = TEMPLATES / name
        source = path.read_text(encoding="utf-8")
        root = ET.fromstring(source)

        assert root.attrib["role"] == "img"
        assert root.attrib["aria-labelledby"] == "title description"
        assert root.attrib["viewBox"] == view_box
        assert root.attrib["width"] == "100%"
        assert "<title" in source
        assert "<desc" in source
        assert "<script" not in source
        assert "<animate" not in source
        assert "<foreignObject" not in source
        assert "http://" not in source.replace("http://www.w3.org/2000/svg", "")
        assert "https://" not in source


def test_readme_and_org_templates_keep_outcome_and_evidence_paths_visible():
    repository = (TEMPLATES / "repository-readme-template.md").read_text(encoding="utf-8")
    organization = (TEMPLATES / "org-card-template.md").read_text(encoding="utf-8")

    for document in (repository, organization):
        assert 'width="100%"' in document
        assert "Inspect evidence" in document or "Verify the evidence" in document
        assert "Evidence" in document
        assert "UNAVAILABLE" in document
    for heading in (
        "## Executive brief",
        "## Quickstart",
        "## Architecture and trust boundary",
        "## Verification",
        "## Limits and non-goals",
    ):
        assert heading in repository
    assert "## Choose your path" in organization
    assert "investor or buyer" in organization
    assert "builder or integrator" in organization
    assert "verifier or reviewer" in organization


def test_executive_brief_uses_native_landmarks_and_disclosure():
    template = (TEMPLATES / "executive-brief-template.html").read_text(encoding="utf-8")

    assert '<meta name="viewport" content="width=device-width, initial-scale=1">' in template
    assert '<main id="main"' in template
    assert "<nav " in template
    assert "<article " in template
    assert "<details " in template
    assert "<summary>" in template
    assert "<script" not in template
    assert 'target="_blank"' not in template
