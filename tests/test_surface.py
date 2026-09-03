import json
from pathlib import Path

import pytest

from szl_brand.surface import (
    END_MARKER,
    LEGACY_END,
    LEGACY_START,
    RECEIPT_SCHEMA,
    SCHEMA,
    START_MARKER,
    SurfaceContractError,
    SurfaceSpec,
    build_receipt,
    generate_surfaces,
    load_manifest,
    render_avatar_svg,
    render_readme_block,
    render_surface_svg,
    replace_managed_block,
    visual_variant,
)


def spec(**overrides):
    values = {
        "slug": "a11oy",
        "display_name": "A11oy",
        "kind": "platform",
        "one_liner": "Governed execution with bounded authority and portable evidence.",
        "decision_path": "See what the system controls, what remains unavailable, and why it matters.",
        "builder_path": "Start from source, the API contract, and independently verifiable receipts.",
        "primary_url": "https://a-11-oy.com",
        "source_url": "https://github.com/szl-holdings/a11oy",
        "evidence_url": "https://a11oy.net",
        "evidence_label": "MEASURED",
        "operational_state": "PARTIAL",
        "limitations": "Public demonstrations do not establish production authorization",
        "image_url": "./assets/surface-card.svg",
    }
    values.update(overrides)
    return SurfaceSpec.from_mapping(values)


def test_svg_is_deterministic_accessible_and_self_contained():
    item = spec()
    first = render_surface_svg(item)
    second = render_surface_svg(item)

    assert first == second
    assert '<title id="title">' in first
    assert '<desc id="description">' in first
    assert 'role="img"' in first
    assert "<defs>" in first
    assert "url(#surface)" in first
    assert "url(#glow)" in first
    assert item.display_name in first


def test_different_slugs_produce_different_visual_identity():
    first = spec(slug="a11oy")
    second = spec(slug="killinchu", display_name="Killinchu")

    assert render_surface_svg(first) != render_surface_svg(second)
    assert visual_variant(first) in range(6)
    assert visual_variant(second) in range(6)


def test_user_copy_is_escaped_in_svg_and_markdown_attributes():
    item = spec(
        display_name='A11oy <Control> & "Proof"',
        one_liner="Bounded <action> & evidence.",
    )
    svg = render_surface_svg(item)
    block = render_readme_block(item)

    assert "&lt;Control&gt;" in svg
    assert "&amp;" in svg
    assert "<Control>" not in svg
    assert "&quot;Proof&quot;" in block


def test_avatar_has_complete_gradients_and_small_size_safe_geometry():
    item = spec(kind="org", slug="szl-holdings", display_name="SZL Holdings")
    avatar = render_avatar_svg(item)

    assert 'id="orbit"' in avatar
    assert 'id="node"' in avatar
    assert "url(#orbit)" in avatar
    assert "url(#node)" in avatar
    assert 'width="1024" height="1024"' in avatar
    assert "SZL Holdings organization mark" in avatar


def test_profile_avatar_is_distinct_from_org_avatar():
    org = render_avatar_svg(spec(kind="org", slug="szl-holdings"))
    profile = render_avatar_svg(
        spec(kind="profile", slug="betterwithage", display_name="Stephen P. Lutar Jr."),
        profile=True,
    )

    assert org != profile
    assert "Founder profile mark" in profile


def test_readme_block_has_two_audiences_truth_and_limitations():
    block = render_readme_block(spec())

    assert block.startswith(START_MARKER)
    assert block.rstrip().endswith(END_MARKER)
    assert "What a non-technical reader gets" in block
    assert "Where a builder starts" in block
    assert "MEASURED" in block
    assert "PARTIAL" in block
    assert "does not prove accuracy" in block


def test_managed_block_insert_preserves_hugging_face_front_matter():
    readme = "---\nsdk: static\nemoji: 🛡️\n---\n\n# Existing\nBody\n"
    block = render_readme_block(spec())
    result = replace_managed_block(readme, block)

    assert result.startswith("---\nsdk: static\nemoji: 🛡️\n---\n\n" + START_MARKER)
    assert result.endswith("# Existing\nBody\n")


def test_v2_migration_rewrites_only_explicit_managed_range():
    before = "# Product\n\n"
    legacy = f"{LEGACY_START}\nold card\n{LEGACY_END}"
    after = "\n\n## Proof\nKeep this byte-for-byte.\n"
    block = render_readme_block(spec())

    result = replace_managed_block(before + legacy + after, block)

    assert LEGACY_START not in result
    assert LEGACY_END not in result
    assert START_MARKER in result
    assert result.startswith(before.rstrip() + "\n\n")
    assert result.endswith("## Proof\nKeep this byte-for-byte.\n")


def test_v3_replacement_is_idempotent():
    block = render_readme_block(spec())
    first = replace_managed_block("# Existing\n", block)
    second = replace_managed_block(first, block)

    assert first == second
    assert first.count(START_MARKER) == 1
    assert first.count(END_MARKER) == 1


def test_unclosed_managed_block_fails_closed():
    with pytest.raises(SurfaceContractError, match="exactly once"):
        replace_managed_block(START_MARKER + "\nbroken", render_readme_block(spec()))


def test_duplicate_managed_markers_fail_closed():
    malformed = (
        START_MARKER
        + "\none\n"
        + END_MARKER
        + "\n"
        + START_MARKER
        + "\ntwo\n"
        + END_MARKER
    )
    with pytest.raises(SurfaceContractError, match="exactly once"):
        replace_managed_block(malformed, render_readme_block(spec()))


def test_orphan_closing_marker_fails_closed():
    with pytest.raises(SurfaceContractError, match="exactly once"):
        replace_managed_block(END_MARKER + "\n", render_readme_block(spec()))


def test_manifest_generation_writes_receipted_assets(tmp_path: Path):
    manifest = tmp_path / "surfaces.json"
    manifest.write_text(
        json.dumps({"schema": SCHEMA, "surfaces": [spec().__dict__]}),
        encoding="utf-8",
    )

    specs = load_manifest(manifest)
    paths = generate_surfaces(specs, tmp_path / "out")

    assert len(paths) == 5
    directory = tmp_path / "out" / "a11oy"
    assert (directory / "surface-card.svg").exists()
    assert (directory / "avatar.svg").exists()
    receipt = json.loads((directory / "receipt.json").read_text(encoding="utf-8"))
    assert receipt["schema"] == RECEIPT_SCHEMA
    assert len(receipt["contract_sha256"]) == 64
    assert len(receipt["svg_sha256"]) == 64
    assert len(receipt["readme_block_sha256"]) == 64


def test_receipt_changes_when_reviewed_copy_changes():
    first = spec()
    second = spec(one_liner="A different reviewed sentence with the same identity.")
    first_svg = render_surface_svg(first)
    second_svg = render_surface_svg(second)

    first_receipt = build_receipt(first, first_svg, render_readme_block(first))
    second_receipt = build_receipt(second, second_svg, render_readme_block(second))

    assert first_receipt.contract_sha256 != second_receipt.contract_sha256
    assert first_receipt.svg_sha256 != second_receipt.svg_sha256


@pytest.mark.parametrize(
    "changes, message",
    [
        ({"kind": "unknown"}, "kind must be"),
        ({"primary_url": "http://example.com"}, "primary_url must be"),
        ({"evidence_label": "REAL"}, "evidence_label must be"),
        ({"operational_state": "PERFECT"}, "operational_state must be"),
        ({"accent": "purple"}, "accent must be"),
        ({"one_liner": "The best in the world."}, "unsupported promotional claim"),
    ],
)
def test_invalid_contracts_fail_closed(changes, message):
    with pytest.raises(SurfaceContractError, match=message):
        spec(**changes)
