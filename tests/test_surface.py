import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from szl_brand.surface import (
    END_MARKER,
    KINDS,
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
    main,
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


@pytest.mark.parametrize("kind", sorted(KINDS))
def test_avatar_is_the_exact_approved_projection_for_every_surface_kind(kind):
    root = Path(__file__).resolve().parents[1]
    approved = (root / "kit/logos/orbit-v2/suite/szl-avatar.svg").read_bytes()
    item = spec(kind=kind, slug=f"sample-{kind}", accent="#DF735F")
    avatar = render_avatar_svg(item, profile=kind == "profile")

    assert avatar.encode("utf-8") == approved
    tree = ET.fromstring(avatar)
    assert tree.attrib["viewBox"] == "0 0 600 600"
    assert tree.attrib["role"] == "img"
    assert tree.find("{http://www.w3.org/2000/svg}title").text == "SZL Holdings"


def test_profile_flag_cannot_redraw_or_recolor_the_parent_mark():
    org = render_avatar_svg(spec(kind="org", slug="szl-holdings"))
    profile = render_avatar_svg(
        spec(kind="profile", slug="betterwithage", display_name="Stephen P. Lutar Jr."),
        profile=True,
    )

    assert org == profile


def test_avatar_refuses_unavailable_source_instead_of_drawing_a_fallback(monkeypatch):
    def unavailable():
        raise ValueError("simulated invalid packaged provenance")

    monkeypatch.setattr("szl_brand.surface._source_bundle", unavailable)
    with pytest.raises(SurfaceContractError, match="approved Orbit avatar source is unavailable"):
        render_avatar_svg(spec())


@pytest.mark.parametrize(
    "state, label",
    [
        ("OPERATIONAL", "OPERATIONAL SPACE"),
        ("PARTIAL", "PARTIAL SPACE"),
        ("DEGRADED", "DEGRADED SPACE"),
        ("UNAVAILABLE", "UNAVAILABLE SPACE"),
        ("HISTORICAL", "HISTORICAL SPACE"),
        ("UNKNOWN", "UNKNOWN SPACE"),
        ("DEPRECATED", "DEPRECATED SPACE"),
        ("ROADMAP", "ROADMAP SPACE"),
    ],
)
def test_space_label_preserves_supplied_state_without_implying_liveness(state, label):
    item = spec(kind="space", operational_state=state, evidence_label="UNKNOWN")
    svg = render_surface_svg(item)
    block = render_readme_block(item)
    tree = ET.fromstring(svg)
    title = tree.find("{http://www.w3.org/2000/svg}title").text
    texts = [node.text for node in tree.iter("{http://www.w3.org/2000/svg}text")]

    assert title == f"A11oy — {label.title()}"
    assert any(text and f"SZL / {label} / " in text for text in texts)
    assert "LIVE SURFACE" not in svg
    assert f"`UNKNOWN` evidence · `{state}` runtime" in block
    receipt = build_receipt(item, svg, block)
    assert receipt.operational_state == state
    assert receipt.evidence_label == "UNKNOWN"


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


@pytest.mark.parametrize("eol", ["\n", "\r\n"])
def test_empty_front_matter_is_closed_for_lf_and_crlf(eol):
    # Regression: "---\n---\n" was refused as unclosed front matter while CRLF passed.
    front = f"---{eol}---{eol}"
    block = render_readme_block(spec())

    result = replace_managed_block(front + "# Title\n", block)

    assert result == "---" + eol + "---\n\n" + block.strip() + "\n\n# Title\n"


def test_unclosed_managed_block_fails_closed():
    with pytest.raises(SurfaceContractError, match="exactly once"):
        replace_managed_block(START_MARKER + "\nbroken", render_readme_block(spec()))


def test_duplicate_managed_markers_fail_closed():
    malformed = START_MARKER + "\none\n" + END_MARKER + "\n" + START_MARKER + "\ntwo\n" + END_MARKER
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


@pytest.mark.parametrize(
    "field, value",
    [
        ("display_name", "\x00"),
        ("one_liner", "Governed\x1bexecution."),
        ("limitations", "Bounded\uffff"),
        ("primary_url", "https://a-11-oy.com/\x00"),
    ],
)
def test_control_characters_fail_closed(field, value):
    # Regression: display_name="\x00" passed validation and rendered malformed SVG XML.
    with pytest.raises(SurfaceContractError, match=f"{field} must not contain control characters"):
        spec(**{field: value})


def _write_manifest(path: Path, rows: list[dict]) -> Path:
    path.write_text(json.dumps({"schema": SCHEMA, "surfaces": rows}), encoding="utf-8")
    return path


@pytest.mark.parametrize("slugs", [("a-b", "a/b"), ("0/", "0-"), ("a11oy", "A11oy")])
def test_manifest_refuses_slugs_that_share_an_output_directory(tmp_path: Path, slugs):
    # Regression: "a-b" and "a/b" both wrote to out/a-b, so one surface overwrote the other.
    rows = [{**spec().__dict__, "slug": slug} for slug in slugs]
    manifest = _write_manifest(tmp_path / "surfaces.json", rows)

    with pytest.raises(SurfaceContractError, match="duplicate surface slug: .* share output"):
        load_manifest(manifest)


def test_generation_refuses_colliding_surfaces_before_writing(tmp_path: Path):
    output = tmp_path / "out"

    with pytest.raises(SurfaceContractError, match="share output directory 'a-b'"):
        generate_surfaces([spec(slug="a-b"), spec(slug="a/b")], output)
    assert not output.exists()


def test_generation_writes_every_surface_to_its_own_directory(tmp_path: Path):
    paths = generate_surfaces([spec(slug="a-b"), spec(slug="killinchu")], tmp_path / "out")

    assert len(paths) == len(set(paths)) == 10
    assert {path.parent.name for path in paths} == {"a-b", "killinchu"}


@pytest.mark.parametrize("field, value", [("display_name", 7), ("slug", None), ("accent", 1)])
def test_non_string_fields_raise_the_contract_error(field, value):
    with pytest.raises(SurfaceContractError, match=f"surface fields must be strings: {field}"):
        SurfaceSpec.from_mapping({**spec().__dict__, field: value})


def test_cli_exits_2_on_a_non_string_field(tmp_path: Path, capsys):
    # Regression: from_mapping raised AttributeError, so the CLI crashed instead of exiting 2.
    manifest = _write_manifest(tmp_path / "surfaces.json", [{**spec().__dict__, "slug": 7}])

    assert main([str(manifest), "--output", str(tmp_path / "out")]) == 2
    assert "surface fields must be strings: slug" in capsys.readouterr().out
