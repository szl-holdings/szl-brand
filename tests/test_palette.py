"""Tests for szl_brand palette module."""

from szl_brand.palette import TEXT_PRIMARY, VOID, Color, ProcPalette


class TestColor:
    def test_from_hex_rgb(self):
        c = Color.from_hex("#FF0000")
        assert c.r == 255
        assert c.g == 0
        assert c.b == 0
        assert c.a == 255

    def test_from_hex_rgba(self):
        c = Color.from_hex("#FF000080")
        assert c.r == 255
        assert c.a == 128

    def test_hex_property(self):
        c = Color(128, 90, 213)
        assert c.hex == "#805ad5"

    def test_hex_with_alpha(self):
        c = Color(128, 90, 213, 128)
        assert c.hex == "#805ad580"

    def test_rgb_tuple(self):
        c = Color(10, 20, 30)
        assert c.rgb == (10, 20, 30)

    def test_relative_luminance_black(self):
        black = Color(0, 0, 0)
        assert black.relative_luminance == 0.0

    def test_relative_luminance_white(self):
        white = Color(255, 255, 255)
        assert abs(white.relative_luminance - 1.0) < 0.001

    def test_contrast_ratio_bw(self):
        black = Color(0, 0, 0)
        white = Color(255, 255, 255)
        ratio = black.contrast_ratio(white)
        assert ratio >= 21.0

    def test_meets_aa(self):
        assert TEXT_PRIMARY.meets_aa(VOID)

    def test_lerp_midpoint(self):
        black = Color(0, 0, 0)
        white = Color(255, 255, 255)
        mid = black.lerp(white, 0.5)
        assert mid.r == 127 or mid.r == 128

    def test_lerp_endpoints(self):
        a = Color(100, 50, 200)
        b = Color(200, 150, 50)
        assert a.lerp(b, 0.0) == a
        assert a.lerp(b, 1.0) == b

    def test_with_alpha(self):
        c = Color(100, 100, 100)
        c2 = c.with_alpha(50)
        assert c2.a == 50
        assert c2.r == 100

    def test_lighten(self):
        c = Color(50, 50, 50)
        lighter = c.lighten(0.2)
        assert lighter.relative_luminance > c.relative_luminance

    def test_darken(self):
        c = Color(200, 200, 200)
        darker = c.darken(0.2)
        assert darker.relative_luminance < c.relative_luminance


class TestProcPalette:
    def test_deterministic(self):
        p1 = ProcPalette("ouroboros")
        p2 = ProcPalette("ouroboros")
        assert p1.accent(0) == p2.accent(0)
        assert p1.gradient_stops(4) == p2.gradient_stops(4)

    def test_different_seeds_produce_different_accents(self):
        p1 = ProcPalette("repo-a")
        p2 = ProcPalette("repo-b")
        assert p1.accent(0) != p2.accent(0)

    def test_accent_sequence_unique(self):
        p = ProcPalette("test-repo")
        accents = [p.accent(i) for i in range(5)]
        assert len(set(accents)) == 5

    def test_gradient_stops_count(self):
        p = ProcPalette("test")
        stops = p.gradient_stops(6)
        assert len(stops) == 6

    def test_primary_hue_range(self):
        p = ProcPalette("anything")
        assert 0 <= p.primary_hue < 360

    def test_noise_field_values_bounded(self):
        p = ProcPalette("noise-test")
        for _x, _y, val in p.noise_field(4, 4, scale=0.1):
            assert 0.0 <= val <= 1.0
