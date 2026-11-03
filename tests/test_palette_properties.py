"""Hypothesis property tests for the palette codec, WCAG contrast math and ProcPalette.

Every property states an invariant of the documented palette contract. A property that
once exposed a defect keeps its minimal failing input pinned with ``@example``, so the
regression is replayed on every run under any seed.
"""

from __future__ import annotations

import colorsys
import hashlib
import string

import pytest
from hypothesis import example, given
from hypothesis import strategies as st

from szl_brand.palette import (
    ACCENT,
    ACCENT_BRIGHT,
    GOLD,
    PROOF_TEAL,
    Color,
    ProcPalette,
)

BYTE = st.integers(min_value=0, max_value=255)
COLORS = st.builds(Color, BYTE, BYTE, BYTE, BYTE)
OPAQUE = st.builds(Color, BYTE, BYTE, BYTE)
UNIT = st.floats(min_value=0.0, max_value=1.0)
HEX_DIGITS = "0123456789abcdefABCDEF"
HEX_PAYLOADS = st.text(HEX_DIGITS, min_size=6, max_size=6) | st.text(
    HEX_DIGITS, min_size=8, max_size=8
)
BLACK = Color(0, 0, 0)
WHITE = Color(255, 255, 255)
GOVERNED_ACCENTS = (ACCENT, PROOF_TEAL, GOLD, ACCENT_BRIGHT)
# Floating-point slack for sums of WCAG coefficients (0.2126 + 0.7152 + 0.0722).
EPS = 1e-9


def _channels(color: Color) -> tuple[int, int, int, int]:
    return color.rgba


class TestHexCodec:
    @given(COLORS)
    def test_hex_round_trips_every_rgba_color(self, color):
        encoded = color.hex

        assert Color.from_hex(encoded) == color
        assert encoded == encoded.lower()
        assert len(encoded) == (7 if color.a == 255 else 9)

    @given(HEX_PAYLOADS, st.booleans())
    def test_from_hex_parses_well_formed_hex_case_insensitively(self, digits, hashed):
        color = Color.from_hex(("#" if hashed else "") + digits)
        expected = [int(digits[i : i + 2], 16) for i in range(0, len(digits), 2)]

        assert list(color.rgba[: len(expected)]) == expected
        if len(digits) == 6:
            assert color.a == 255
        canonical = "#" + digits.lower()
        if canonical.endswith("ff") and len(digits) == 8:
            canonical = canonical[:7]
        assert color.hex == canonical

    @given(
        st.text(HEX_DIGITS, max_size=12).filter(lambda digits: len(digits) not in (6, 8)),
        st.booleans(),
    )
    def test_from_hex_rejects_wrong_digit_count(self, digits, hashed):
        with pytest.raises(ValueError, match="Invalid hex color"):
            Color.from_hex(("#" if hashed else "") + digits)

    # int(pair, 16) alone accepts a sign, surrounding whitespace and non-ASCII digits, and
    # lstrip("#") accepted any number of leading '#': each pinned input used to parse.
    @given(
        st.text(HEX_DIGITS + "#+- \t١１xg", min_size=6, max_size=8).map(
            lambda payload: "#" + payload
        )
    )
    @example("#-10000")
    @example("#00000 ")
    @example("#١١١١١١")
    @example("##000000")
    def test_from_hex_accepts_only_hex_digits_and_returns_byte_channels(self, text):
        try:
            color = Color.from_hex(text)
        except ValueError:
            return
        assert all(character in string.hexdigits for character in text[1:]), (text, color)
        assert all(0 <= channel <= 255 for channel in _channels(color)), (text, color)


class TestWcagContrast:
    @given(COLORS)
    def test_relative_luminance_is_in_unit_interval(self, color):
        assert 0.0 <= color.relative_luminance <= 1.0 + EPS

    @given(OPAQUE)
    def test_relative_luminance_weights_channels_by_the_wcag_coefficients(self, color):
        # A gray's luminance is its linearized channel (the weights sum to 1), so this pins
        # each channel's weight and their additivity without re-deriving the sRGB curve.
        def gray(channel: int) -> float:
            return Color(channel, channel, channel).relative_luminance

        expected = 0.2126 * gray(color.r) + 0.7152 * gray(color.g) + 0.0722 * gray(color.b)

        assert color.relative_luminance == pytest.approx(expected, abs=EPS)

    @given(OPAQUE, st.sampled_from("rgb"), BYTE)
    def test_relative_luminance_is_monotone_in_every_channel(self, color, channel, value):
        values = {"r": color.r, "g": color.g, "b": color.b}
        values[channel] = max(values[channel], value)
        brighter = Color(**values)

        assert brighter.relative_luminance >= color.relative_luminance

    @given(COLORS, COLORS)
    def test_contrast_ratio_is_symmetric_and_bounded(self, first, second):
        ratio = first.contrast_ratio(second)

        assert ratio == second.contrast_ratio(first)
        assert 1.0 <= ratio <= 21.0 + EPS

    @given(COLORS)
    def test_color_has_unit_contrast_with_itself(self, color):
        assert color.contrast_ratio(color) == 1.0

    @given(COLORS)
    def test_every_color_meets_aa_against_black_or_white(self, color):
        # (L + 0.05) / 0.05 and 1.05 / (L + 0.05) multiply to 21, so the larger of the two
        # ratios is at least sqrt(21) ~= 4.58 > 4.5 for every color.
        assert color.meets_aa(BLACK) or color.meets_aa(WHITE)

    @given(COLORS, COLORS, st.booleans())
    def test_wcag_levels_follow_wcag_thresholds_and_nest(self, foreground, background, large):
        ratio = foreground.contrast_ratio(background)
        aa = foreground.meets_aa(background, large_text=large)
        aaa = foreground.meets_aaa(background, large_text=large)

        assert aa == (ratio >= (3.0 if large else 4.5))
        assert aaa == (ratio >= (4.5 if large else 7.0))
        assert not aaa or aa
        assert aa == background.meets_aa(foreground, large_text=large)
        if foreground.meets_aa(background):
            assert foreground.meets_aa(background, large_text=True)
        if foreground.meets_aaa(background):
            assert foreground.meets_aaa(background, large_text=True)

    @given(COLORS)
    def test_hsl_components_are_in_range(self, color):
        hue, saturation, lightness = color.hsl

        assert 0.0 <= hue < 360.0
        assert 0.0 <= saturation <= 100.0 + EPS
        assert 0.0 <= lightness <= 100.0 + EPS


class TestBlending:
    @given(COLORS, COLORS)
    def test_lerp_hits_both_endpoints(self, start, end):
        assert start.lerp(end, 0.0) == start
        assert start.lerp(end, 1.0) == end

    @given(COLORS, COLORS, st.floats(allow_nan=False))
    def test_lerp_never_leaves_the_segment_between_endpoints(self, start, end, t):
        mixed = start.lerp(end, t)

        for low, high, value in zip(
            _channels(start), _channels(end), _channels(mixed), strict=True
        ):
            assert min(low, high) <= value <= max(low, high)

    @given(COLORS, COLORS, st.floats(allow_nan=False))
    def test_lerp_clamps_t_and_stays_within_one_unit_of_the_exact_mix(self, start, end, t):
        clamped = max(0.0, min(1.0, t))
        mixed = start.lerp(end, t)

        assert mixed == start.lerp(end, clamped)
        if t <= 0.0:
            assert mixed == start
        if t >= 1.0:
            assert mixed == end
        for first, last, value in zip(
            _channels(start), _channels(end), _channels(mixed), strict=True
        ):
            assert abs(value - (first + (last - first) * clamped)) < 1

    @given(COLORS, BYTE)
    def test_with_alpha_replaces_only_alpha(self, color, alpha):
        result = color.with_alpha(alpha)

        assert result.rgb == color.rgb
        assert result.a == alpha

    @given(COLORS, UNIT)
    def test_lighten_returns_byte_channels_and_keeps_alpha(self, color, amount):
        result = color.lighten(amount)

        assert all(0 <= channel <= 255 for channel in result.rgb)
        assert result.a == color.a

    @given(COLORS, UNIT)
    def test_darken_never_brightens_a_channel_and_keeps_alpha(self, color, amount):
        result = color.darken(amount)

        assert all(new <= old for new, old in zip(result.rgb, color.rgb, strict=True))
        assert result.a == color.a

    # Truncating the HLS round trip with int() used to lower channels on these inputs.
    @given(COLORS, UNIT)
    @example(Color(0, 1, 1), 0.0)
    @example(Color(0, 0, 255), 0.001)
    def test_lighten_never_darkens_a_channel(self, color, amount):
        # With hue and saturation fixed, every RGB channel is non-decreasing in HLS lightness.
        result = color.lighten(amount)

        assert all(new >= old for new, old in zip(result.rgb, color.rgb, strict=True)), (
            color,
            amount,
            result,
        )

    # Lightness used to be clamped only at 1.0: this darkened to Color(-2, -2, -2).
    @given(COLORS, UNIT)
    @example(Color(0, 0, 0), 0.01)
    def test_darken_returns_byte_channels(self, color, amount):
        result = color.darken(amount)

        assert all(0 <= channel <= 255 for channel in result.rgb), (color, amount, result)


class TestProcPaletteProperties:
    @given(st.text(max_size=64), st.integers(min_value=0, max_value=16))
    def test_same_seed_produces_identical_output(self, seed, count):
        first, second = ProcPalette(seed), ProcPalette(seed)

        assert first.seed_bytes == second.seed_bytes == hashlib.sha256(seed.encode()).digest()
        assert first.gradient_stops(count) == second.gradient_stops(count)
        assert first.primary_hue == ACCENT.hsl[0]

    @given(st.text(max_size=64), st.text(max_size=64), st.integers(-1000, 1000))
    def test_accents_stay_in_the_governed_set_for_every_seed(self, seed, other, index):
        accent = ProcPalette(seed).accent(index)

        assert accent == GOVERNED_ACCENTS[index % len(GOVERNED_ACCENTS)]
        assert accent == ProcPalette(other).accent(index)
        assert ProcPalette(seed).accent(0) == ACCENT

    @given(st.text(max_size=64), st.integers(min_value=0, max_value=16))
    def test_gradient_stops_stay_in_the_deep_blue_gamut_for_every_seed(self, seed, count):
        stops = ProcPalette(seed).gradient_stops(count)

        assert len(stops) == count
        for stop in stops:
            hue, saturation, lightness = stop.hsl
            assert 200 <= hue <= 235, stop
            assert saturation >= 20, stop
            assert lightness <= 15, stop
            assert stop.a == 255

    @given(
        st.text(max_size=32),
        st.integers(min_value=0, max_value=6),
        st.integers(min_value=0, max_value=6),
        st.floats(min_value=-4.0, max_value=4.0),
    )
    def test_noise_field_covers_the_grid_with_unit_values(self, seed, width, height, scale):
        field = list(ProcPalette(seed).noise_field(width, height, scale=scale))

        assert [(x, y) for x, y, _value in field] == [
            (x, y) for y in range(height) for x in range(width)
        ]
        assert all(0.0 <= value <= 1.0 for _x, _y, value in field)
        assert field == list(ProcPalette(seed).noise_field(width, height, scale=scale))


@given(UNIT, UNIT, UNIT, UNIT)
def test_hls_channels_are_monotone_in_lightness(hue, saturation, first, second):
    """Pin the math the lighten/darken properties rely on, independent of Color."""

    low, high = sorted((first, second))
    darker = colorsys.hls_to_rgb(hue, low, saturation)
    lighter = colorsys.hls_to_rgb(hue, high, saturation)

    assert all(new >= old - EPS for new, old in zip(lighter, darker, strict=True))
