import json
from pathlib import Path

import pytest

from szl_brand.estate import (
    FLAGSHIP_PRODUCT,
    GOVERNANCE_PROOF,
    HISTORICAL,
    PLATFORM_CONTROL,
    RESEARCH_FORMULA,
    RUNTIME_INFRA,
    UNCLASSIFIED,
)
from szl_brand.motif import (
    RECEIPT_SCHEMA,
    SCHEMA,
    MotifContractError,
    MotifRequest,
    build_profile,
    build_receipt,
    generate_motifs,
    load_manifest,
    render_css,
    render_svg,
)


def request(**overrides):
    values = {
        "slug": "a11oy",
        "display_name": "A11oy",
        "estate_class": FLAGSHIP_PRODUCT,
    }
    values.update(overrides)
    return MotifRequest.from_mapping(values)


def test_each_estate_class_has_a_distinct_structural_profile():
    classes = (
        FLAGSHIP_PRODUCT,
        PLATFORM_CONTROL,
        RUNTIME_INFRA,
        GOVERNANCE_PROOF,
        RESEARCH_FORMULA,
        HISTORICAL,
        UNCLASSIFIED,
    )
    profiles = [
        build_profile(
            request(
                slug=f"surface-{index}",
                display_name=f"Surface {index}",
                estate_class=estate_class,
            )
        )
        for index, estate_class in enumerate(classes)
    ]

    assert len({profile.theme_family for profile in profiles}) == len(classes)
    assert len({profile.motif for profile in profiles}) == len(classes)
    assert len({profile.interaction for profile in profiles}) == len(classes)
    assert len({profile.evidence_placement for profile in profiles}) == len(classes)


def test_same_request_is_byte_deterministic():
    first = build_profile(request())
    second = build_profile(request())

    assert first == second
    assert render_svg(first) == render_svg(second)
    assert render_css(first) == render_css(second)


def test_same_class_different_slug_gets_unique_fingerprint_or_variant():
    first = build_profile(request(slug="terra", display_name="Terra"))
    second = build_profile(request(slug="sentra", display_name="Sentra"))

    assert first.theme_family == second.theme_family == "DOMAIN_COMMAND"
    assert first.surface_fingerprint != second.surface_fingerprint
    assert (first.variant, first.surface_fingerprint) != (
        second.variant,
        second.surface_fingerprint,
    )


def test_product_svg_contains_domain_command_geometry():
    profile = build_profile(request())
    svg = render_svg(profile)

    assert "DOMAIN_COMMAND" in svg
    assert "DECISION / MAP / EVIDENCE" in svg
    assert "EVIDENCE RAIL" in svg
    assert 'role="img"' in svg
    assert "CONTROL BEFORE ACTION" in svg


def test_proof_svg_is_receipt_native():
    profile = build_profile(
        request(
            slug="szl-trust",
            display_name="SZL Trust",
            estate_class=GOVERNANCE_PROOF,
        )
    )
    svg = render_svg(profile)

    assert profile.theme_family == "PROOF_LEDGER"
    assert "RECEIPT-1" in svg
    assert "sha256:" in svg
    assert profile.motion == "NONE"


def test_formula_svg_is_not_product_command_geometry():
    profile = build_profile(
        request(
            slug="szl-quant",
            display_name="SZL Quant",
            estate_class=RESEARCH_FORMULA,
        )
    )
    svg = render_svg(profile)

    assert profile.theme_family == "FORMULA_NOTEBOOK"
    assert "Λ = f(E, P, A)" in svg
    assert "DERIVATION OPEN" in svg
    assert "EVIDENCE RAIL" not in svg


def test_archive_surface_is_quiet_and_explicitly_historical():
    profile = build_profile(
        request(
            slug="legacy-demo",
            display_name="Legacy Demo",
            estate_class=HISTORICAL,
        )
    )
    svg = render_svg(profile)

    assert profile.theme_family == "ARCHIVE_MONO"
    assert profile.density == "LOW"
    assert profile.motion == "NONE"
    assert "HISTORICAL ARTIFACT · NO LIVE RUNTIME CLAIM" in svg


def test_css_preserves_mobile_focus_and_reduced_motion_contracts():
    css = render_css(build_profile(request()))

    assert "--szl-motif-touch: 44px" in css
    assert "overflow-x: clip" in css
    assert ":focus-visible" in css
    assert "@media (pointer: coarse)" in css
    assert "--szl-motif-touch: 48px" in css
    assert "@media (prefers-reduced-motion: reduce)" in css


def test_internal_class_is_not_public_motif_eligible():
    with pytest.raises(MotifContractError, match="not eligible"):
        MotifRequest.from_mapping(
            {
                "slug": "private-control",
                "display_name": "Private Control",
                "estate_class": "INTERNAL",
            }
        )


def test_manifest_generation_writes_profile_svg_css_and_receipt(tmp_path: Path):
    manifest = tmp_path / "motifs.json"
    manifest.write_text(
        json.dumps(
            {
                "schema": SCHEMA,
                "surfaces": [
                    {
                        "slug": "hatun-mcp",
                        "display_name": "Hatun MCP",
                        "estate_class": RUNTIME_INFRA,
                    },
                    {
                        "slug": "governance-as-code",
                        "display_name": "Governance as Code",
                        "estate_class": GOVERNANCE_PROOF,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    requests = load_manifest(manifest)
    paths = generate_motifs(requests, tmp_path / "out")

    assert len(paths) == 8
    assert (tmp_path / "out" / "hatun-mcp" / "motif.svg").exists()
    assert (tmp_path / "out" / "hatun-mcp" / "motif.css").exists()
    receipt_path = tmp_path / "out" / "governance-as-code" / "motif-receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["schema"] == RECEIPT_SCHEMA
    assert len(receipt["profile_sha256"]) == 64
    assert len(receipt["svg_sha256"]) == 64
    assert len(receipt["css_sha256"]) == 64


def test_receipt_changes_when_surface_identity_changes():
    first = build_profile(request(slug="terra", display_name="Terra"))
    second = build_profile(request(slug="sentra", display_name="Sentra"))
    first_svg = render_svg(first)
    second_svg = render_svg(second)
    first_css = render_css(first)
    second_css = render_css(second)

    first_receipt = build_receipt(first, first_svg, first_css)
    second_receipt = build_receipt(second, second_svg, second_css)

    assert first_receipt.profile_sha256 != second_receipt.profile_sha256
    assert first_receipt.svg_sha256 != second_receipt.svg_sha256
