"""Hypothesis property tests for Surface Foundry contracts, managed README blocks and SVG output."""

from __future__ import annotations

import json
import re
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import asdict
from pathlib import Path

import pytest
from hypothesis import assume, example, given, settings
from hypothesis import strategies as st

from szl_brand.surface import (
    BANNED_COPY,
    END_MARKER,
    EVIDENCE_LABELS,
    KIND_LABELS,
    KINDS,
    LEGACY_END,
    LEGACY_START,
    OPERATIONAL_STATES,
    SCHEMA,
    SLUG_RE,
    START_MARKER,
    SurfaceContractError,
    SurfaceSpec,
    canonical_contract,
    load_manifest,
    render_readme_block,
    render_surface_svg,
    replace_managed_block,
    safe_output_name,
    visual_variant,
)

BASE = {
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
BLOCK = render_readme_block(SurfaceSpec.from_mapping(BASE))
NORMALIZED_BLOCK = BLOCK.strip() + "\n"
MARKERS = (START_MARKER, END_MARKER, LEGACY_START, LEGACY_END)
SVG_NS = "{http://www.w3.org/2000/svg}"

readme_text = st.text(max_size=200).filter(
    lambda text: (
        not text.startswith(("---\n", "---\r\n")) and not any(marker in text for marker in MARKERS)
    )
)
front_matter_line = st.text("abcdefghijklmnopqrstuvwxyz0123456789:_ '\"", min_size=1, max_size=24)
newline = st.sampled_from(["\n", "\r\n"])
slugs = st.from_regex(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,95}", fullmatch=True)
# XML 1.0 forbids C0/C1 controls (other than tab/newline/CR) and U+FFFE/U+FFFF.
printable = st.characters(exclude_categories=("Cc", "Cs", "Cn"))


def _front_matter(lines: list[str], eol: str) -> str:
    return "---" + eol + "".join(line + eol for line in lines) + "---" + eol


def _assert_single_v3_block(text: str) -> None:
    assert text.count(START_MARKER) == 1
    assert text.count(END_MARKER) == 1
    assert LEGACY_START not in text
    assert LEGACY_END not in text
    assert NORMALIZED_BLOCK in text


def _parse_svg(svg: str) -> ET.Element:
    try:
        return ET.fromstring(svg)
    except ET.ParseError as exc:
        raise AssertionError(f"render_surface_svg emitted malformed XML: {exc}") from exc


@given(readme_text)
def test_managed_block_insert_preserves_readme_and_is_idempotent(readme):
    once = replace_managed_block(readme, BLOCK)

    _assert_single_v3_block(once)
    body = readme.lstrip()
    assert once == NORMALIZED_BLOCK + ("\n" + body if body else "")
    assert replace_managed_block(once, BLOCK) == once


@given(
    readme_text,
    st.text(max_size=80).filter(lambda text: not any(marker in text for marker in MARKERS)),
    readme_text,
    st.sampled_from([(START_MARKER, END_MARKER), (LEGACY_START, LEGACY_END)]),
)
def test_managed_block_replaces_or_migrates_an_existing_block(before, inner, after, markers):
    start, end = markers
    once = replace_managed_block(before + start + inner + end + after, BLOCK)

    _assert_single_v3_block(once)
    assert once.startswith(before.rstrip())
    assert once.endswith(after.lstrip())
    assert replace_managed_block(once, BLOCK) == once


@given(st.lists(front_matter_line, min_size=1, max_size=4), newline, readme_text)
def test_managed_block_lands_after_yaml_front_matter(lines, eol, body):
    front = _front_matter(lines, eol)
    once = replace_managed_block(front + body, BLOCK)

    _assert_single_v3_block(once)
    assert once.startswith(front.rstrip() + "\n\n" + START_MARKER)
    assert replace_managed_block(once, BLOCK) == once


# Empty LF front matter '---\n---\n' used to be refused as unclosed while CRLF passed.
@given(st.lists(front_matter_line, max_size=3), newline, readme_text)
@example([], "\n", "# Title\n")
def test_managed_block_accepts_any_closed_front_matter(lines, eol, body):
    front = _front_matter(lines, eol)
    once = replace_managed_block(front + body, BLOCK)

    assert once.startswith(front.rstrip() + "\n\n" + START_MARKER)


@given(slugs)
def test_output_name_is_one_safe_lowercase_path_component(slug):
    name = safe_output_name(slug)

    assert re.fullmatch(r"[a-z0-9](?:[a-z0-9._-]*[a-z0-9_])?", name), name
    assert name not in {".", ".."}
    assert safe_output_name(name) == name


# safe_output_name folds case, separators and trailing dots, so distinct valid slugs can
# share a directory; load_manifest used to accept these pairs and generate_surfaces then
# silently overwrote one surface's artifacts with the other's.
@given(
    st.from_regex(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,30}", fullmatch=True).flatmap(
        lambda first: st.tuples(
            st.just(first),
            st.one_of(
                slugs,
                st.sampled_from(["/", ".", "-", "./"]).map(lambda tail: first + tail),
                st.just(first.replace("-", "/")),
                st.just(first.replace("/", "-")),
                st.just(first.swapcase()),
            ),
        )
    )
)
@example(("a-b", "a/b"))
@example(("0/", "0-"))
def test_a_manifest_never_maps_two_surfaces_to_one_output_directory(pair):
    first, second = pair
    assume(SLUG_RE.fullmatch(second))
    rows = [{**BASE, "slug": first}, {**BASE, "slug": second}]

    with tempfile.TemporaryDirectory() as directory:
        manifest = Path(directory) / "surfaces.json"
        manifest.write_text(json.dumps({"schema": SCHEMA, "surfaces": rows}), encoding="utf-8")
        if safe_output_name(first) == safe_output_name(second):
            with pytest.raises(SurfaceContractError, match="share output directory"):
                load_manifest(manifest)
        else:
            assert [spec.slug for spec in load_manifest(manifest)] == [first, second]


def _copy(maximum: int) -> st.SearchStrategy[str]:
    return st.text(printable, min_size=1, max_size=maximum).filter(
        lambda text: 1 <= len(text.strip()) <= maximum
    )


urls = st.builds(
    "https://{}.com/{}".format,
    st.from_regex(r"[a-z0-9]{1,20}", fullmatch=True),
    st.from_regex(r"[a-z0-9/_-]{0,20}", fullmatch=True),
)


@st.composite
def surface_fields(draw):
    fields = {
        "slug": draw(slugs),
        "display_name": draw(_copy(72)),
        "kind": draw(st.sampled_from(sorted(KINDS))),
        "one_liner": draw(_copy(150)),
        "decision_path": draw(_copy(120)),
        "builder_path": draw(_copy(120)),
        "primary_url": draw(urls),
        "source_url": draw(urls),
        "evidence_url": draw(urls),
        "evidence_label": draw(st.sampled_from(sorted(EVIDENCE_LABELS))),
        "operational_state": draw(st.sampled_from(sorted(OPERATIONAL_STATES))),
        "limitations": draw(_copy(220)),
        "image_url": draw(
            st.sampled_from(["./assets/surface-card.svg", "https://cdn.example.com/c.svg"])
        ),
        "accent": draw(st.none() | st.from_regex(r"#[0-9A-Fa-f]{6}", fullmatch=True)),
    }
    copy = " ".join(
        fields[name]
        for name in ("display_name", "one_liner", "decision_path", "builder_path", "limitations")
    ).casefold()
    assume(not any(phrase in copy for phrase in BANNED_COPY))
    return fields


@given(surface_fields())
def test_canonical_contract_is_a_reloadable_fixed_point(fields):
    spec = SurfaceSpec.from_mapping(fields)
    canonical = canonical_contract(spec)
    decoded = json.loads(canonical)

    assert canonical.endswith(b"\n")
    assert decoded == asdict(spec)
    assert SurfaceSpec.from_mapping(decoded) == spec
    assert canonical_contract(SurfaceSpec.from_mapping(decoded)) == canonical
    assert visual_variant(spec) in range(6)


@settings(deadline=None)
@given(surface_fields())
def test_svg_is_deterministic_well_formed_and_carries_the_contract_copy(fields):
    spec = SurfaceSpec.from_mapping(fields)
    svg = render_surface_svg(spec)
    root = _parse_svg(svg)

    assert svg == render_surface_svg(spec)
    assert root.tag == f"{SVG_NS}svg"
    assert (root.get("width"), root.get("height")) == ("1280", "640")
    title = root.find(f"{SVG_NS}title")
    desc = root.find(f"{SVG_NS}desc")
    assert title is not None and desc is not None
    label = KIND_LABELS[spec.kind]
    if spec.kind == "space":
        label = f"{spec.operational_state} {label}"
    assert title.text == f"{spec.display_name} — {label.title()}"
    assert desc.text.startswith(spec.one_liner + " Evidence label: ")


# validate_surface used to accept control characters, which html.escape keeps, so
# display_name='\x00' (or a URL path carrying one) rendered SVG that no XML parser accepts.
@settings(deadline=None)
@given(
    st.sampled_from(["display_name", "one_liner", "primary_url"]), st.text(min_size=1, max_size=72)
)
@example("display_name", "\x00")
@example("display_name", "\uffff")
@example("primary_url", "\x00")
def test_every_accepted_svg_field_renders_well_formed_svg(field, text):
    value = BASE["primary_url"] + "/" + text if field == "primary_url" else text
    try:
        spec = SurfaceSpec.from_mapping({**BASE, field: value})
    except SurfaceContractError:
        return
    _parse_svg(render_surface_svg(spec))


# Anything json.loads can return; from_mapping used to raise AttributeError or TypeError
# (so the CLI crashed instead of exiting 2) when a field was not a string.
json_values = st.recursive(
    st.none() | st.booleans() | st.integers() | st.floats() | st.text(max_size=24),
    lambda children: (
        st.lists(children, max_size=3) | st.dictionaries(st.text(max_size=8), children, max_size=3)
    ),
    max_leaves=8,
)


@given(st.sampled_from(sorted(SurfaceSpec.__dataclass_fields__)), json_values)
@example("display_name", 7)
@example("slug", None)
@example("accent", None)
def test_from_mapping_refuses_any_bad_field_value_with_the_contract_error(field, value):
    try:
        spec = SurfaceSpec.from_mapping({**BASE, field: value})
    except SurfaceContractError:
        return

    assert isinstance(value, str) or (field == "accent" and value is None)
    assert getattr(spec, field) == value
