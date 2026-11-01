"""Generated input checks for the public SDK contracts.

These tests exercise production functions. Temporary directories are created
inside each generated example so cases cannot share files or fixture state.
Rendering is bounded to eight examples; deadlines are disabled for filesystem
and image work, not failures or assertions.
"""

from __future__ import annotations

import hashlib
import tempfile
from dataclasses import replace
from pathlib import Path

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st
from PIL import Image

from szl_brand.palette import Color, ProcPalette
from szl_brand.preview import PreviewSpec, generate_preview
from szl_brand.validate import Manifest, check_drift, generate_manifest, validate_directory

pytestmark = pytest.mark.hypothesis

CHANNEL = st.integers(min_value=0, max_value=255)
COLORS = st.builds(Color, CHANNEL, CHANNEL, CHANNEL, CHANNEL)
SEEDS = st.text(alphabet=st.characters(blacklist_categories=("Cs",)), max_size=40)
FINITE_T = st.floats(min_value=-2, max_value=3, allow_nan=False, allow_infinity=False)


@given(color=COLORS)
def test_color_hex_roundtrip_preserves_every_channel(color: Color) -> None:
    assert Color.from_hex(color.hex) == color
    assert Color.from_hex(color.hex.upper()) == color
    assert color.rgba == (color.r, color.g, color.b, color.a)
    assert len(color.hex) == (7 if color.a == 255 else 9)


@given(left=COLORS, right=COLORS)
def test_contrast_symmetry_identity_and_extremes(left: Color, right: Color) -> None:
    ratio = left.contrast_ratio(right)
    assert 1 <= ratio <= 21
    assert ratio == right.contrast_ratio(left)
    assert left.contrast_ratio(left) == 1
    assert Color(0, 0, 0).contrast_ratio(Color(255, 255, 255)) == 21
    # Published luminance weights at the RGB primaries, independent of hex parsing.
    assert Color(255, 0, 0).relative_luminance == pytest.approx(0.2126)
    assert Color(0, 255, 0).relative_luminance == pytest.approx(0.7152)
    assert Color(0, 0, 255).relative_luminance == pytest.approx(0.0722)


@given(left=COLORS, right=COLORS, t=FINITE_T)
def test_interpolation_endpoints_clamping_and_channel_bounds(
    left: Color, right: Color, t: float
) -> None:
    assert left.lerp(right, 0) == left
    assert left.lerp(right, 1) == right
    assert left.lerp(right, -1) == left
    assert left.lerp(right, 2) == right
    result = left.lerp(right, t)
    for a, b, value in zip(left.rgba, right.rgba, result.rgba, strict=True):
        assert min(a, b) <= value <= max(a, b)
    midpoint = left.lerp(right, 0.5)
    assert midpoint.rgba == tuple((a + b) // 2 for a, b in zip(left.rgba, right.rgba, strict=True))


@given(color=COLORS, alpha=CHANNEL)
def test_alpha_replacement_does_not_change_rgb(color: Color, alpha: int) -> None:
    changed = color.with_alpha(alpha)
    assert changed.rgb == color.rgb
    assert changed.a == alpha
    assert color.with_alpha(color.a) == color


@given(seed=SEEDS, index=st.integers(min_value=-1000, max_value=1000))
def test_repository_seed_preserves_governed_accent_cycle(seed: str, index: int) -> None:
    palette = ProcPalette(seed)
    assert palette.seed_bytes == hashlib.sha256(seed.encode("utf-8")).digest()
    assert palette.seed_bytes != ProcPalette(seed + "\0").seed_bytes
    expected = ("#df735f", "#5cc4bf", "#d7b96b", "#f0917e")
    assert palette.accent(index).hex == expected[index % 4]
    assert palette.accent(index + 4) == palette.accent(index)


@given(
    seed=SEEDS,
    width=st.integers(min_value=0, max_value=12),
    height=st.integers(min_value=0, max_value=12),
)
def test_noise_is_reproducible_bounded_and_covers_the_grid(
    seed: str, width: int, height: int
) -> None:
    first = list(ProcPalette(seed).noise_field(width, height, scale=0.125))
    assert first == list(ProcPalette(seed).noise_field(width, height, scale=0.125))
    assert [(x, y) for x, y, _ in first] == [(x, y) for y in range(height) for x in range(width)]
    assert all(0 <= value <= 1 for _, _, value in first)


@given(
    width=st.integers(min_value=1, max_value=32),
    height=st.integers(min_value=1, max_value=32),
    color=COLORS,
)
@settings(max_examples=30, deadline=None)
def test_manifest_tracks_real_png_bytes_and_roundtrips(
    width: int, height: int, color: Color
) -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        asset = root / "asset.png"
        Image.new("RGBA", (width, height), color.rgba).save(asset)
        raw = asset.read_bytes()
        records = validate_directory(root)
        assert len(records) == 1
        record = records[0]
        assert record.validated and not record.errors
        assert (record.width, record.height) == (width, height)
        assert record.sha256 == hashlib.sha256(raw).hexdigest()
        assert record.size_bytes == len(raw)
        manifest = generate_manifest(root)
        assert Manifest.from_json(manifest.to_json()) == manifest
        assert manifest.assets == records
        assert manifest.root_hash == hashlib.sha256(record.sha256.encode()).hexdigest()
        repeat = generate_manifest(root)
        assert repeat.assets == manifest.assets
        assert repeat.root_hash == manifest.root_hash


@given(payload=st.binary(min_size=0, max_size=128))
@settings(max_examples=30, deadline=None)
def test_drift_distinguishes_add_remove_modify_and_ignores_untracked_suffixes(
    payload: bytes,
) -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        asset = root / "original.svg"
        asset.write_bytes(b"<svg/>")
        manifest_file = root / "manifest.json"
        manifest_file.write_text(generate_manifest(root).to_json(), encoding="utf-8")
        assert check_drift(manifest_file, root) == []
        (root / "notes.txt").write_bytes(payload)
        assert check_drift(manifest_file, root) == []
        asset.write_bytes(b"<svg/>\n" + payload)
        expected = hashlib.sha256(b"<svg/>").hexdigest()
        actual = hashlib.sha256(asset.read_bytes()).hexdigest()
        assert check_drift(manifest_file, root) == [
            {"type": "modified", "path": str(asset), "expected": expected, "actual": actual}
        ]
        asset.unlink()
        assert check_drift(manifest_file, root) == [{"type": "removed", "path": str(asset)}]
        added = root / "added.svg"
        added.write_bytes(b"<svg/>")
        assert {tuple(sorted(item.items())) for item in check_drift(manifest_file, root)} == {
            tuple(sorted({"type": "added", "path": str(added)}.items())),
            tuple(sorted({"type": "removed", "path": str(asset)}.items())),
        }


@given(seed=st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789-_", min_size=1, max_size=24))
@example(seed="a")
@settings(max_examples=8, deadline=None)
def test_preview_is_byte_deterministic_and_has_canonical_dimensions(seed: str) -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        spec = PreviewSpec(seed, "TEST", "Deterministic", "Generated input check", "SDK")
        first = generate_preview(spec, root / "a.png")
        second = generate_preview(spec, root / "b.png")
        assert first.read_bytes() == second.read_bytes()
        # Repo identity must affect geometry/texture even with identical visible copy.
        alternate = generate_preview(replace(spec, repo=seed + "-distinct"), root / "c.png")
        assert first.read_bytes() != alternate.read_bytes()
        with Image.open(first) as image:
            assert image.size == (1280, 640)
            assert image.format == "PNG"
            assert image.mode == "RGB"
