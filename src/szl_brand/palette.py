"""SZL Brand Palette — color theory engine with perceptual uniformity.

Provides the canonical brand color system plus utilities for generating
harmonious derivatives, accessibility-checked contrast ratios, and
procedural color sequences seeded by repo identity.
"""

from __future__ import annotations

import colorsys
import hashlib
import math
from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Color:
    """Immutable RGBA color with perceptual utilities."""

    r: int
    g: int
    b: int
    a: int = 255

    @classmethod
    def from_hex(cls, hex_str: str) -> Color:
        h = hex_str.lstrip("#")
        if len(h) == 6:
            return cls(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
        elif len(h) == 8:
            return cls(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16))
        raise ValueError(f"Invalid hex color: {hex_str}")

    @property
    def hex(self) -> str:
        if self.a == 255:
            return f"#{self.r:02x}{self.g:02x}{self.b:02x}"
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}{self.a:02x}"

    @property
    def rgb(self) -> tuple[int, int, int]:
        return (self.r, self.g, self.b)

    @property
    def rgba(self) -> tuple[int, int, int, int]:
        return (self.r, self.g, self.b, self.a)

    @property
    def hsl(self) -> tuple[float, float, float]:
        hue, lightness, sat = colorsys.rgb_to_hls(self.r / 255, self.g / 255, self.b / 255)
        return (hue * 360, sat * 100, lightness * 100)

    @property
    def relative_luminance(self) -> float:
        """WCAG 2.1 relative luminance."""

        def linearize(c: int) -> float:
            s = c / 255
            return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4

        return 0.2126 * linearize(self.r) + 0.7152 * linearize(self.g) + 0.0722 * linearize(self.b)

    def contrast_ratio(self, other: Color) -> float:
        """WCAG 2.1 contrast ratio between two colors."""
        l1 = max(self.relative_luminance, other.relative_luminance)
        l2 = min(self.relative_luminance, other.relative_luminance)
        return (l1 + 0.05) / (l2 + 0.05)

    def meets_aa(self, other: Color, large_text: bool = False) -> bool:
        threshold = 3.0 if large_text else 4.5
        return self.contrast_ratio(other) >= threshold

    def meets_aaa(self, other: Color, large_text: bool = False) -> bool:
        threshold = 4.5 if large_text else 7.0
        return self.contrast_ratio(other) >= threshold

    def lerp(self, other: Color, t: float) -> Color:
        """Linear interpolation between two colors."""
        t = max(0.0, min(1.0, t))
        return Color(
            r=int(self.r + (other.r - self.r) * t),
            g=int(self.g + (other.g - self.g) * t),
            b=int(self.b + (other.b - self.b) * t),
            a=int(self.a + (other.a - self.a) * t),
        )

    def with_alpha(self, alpha: int) -> Color:
        return Color(self.r, self.g, self.b, alpha)

    def lighten(self, amount: float) -> Color:
        hue, lightness, sat = colorsys.rgb_to_hls(self.r / 255, self.g / 255, self.b / 255)
        lightness = min(1.0, lightness + amount)
        r, g, b = colorsys.hls_to_rgb(hue, lightness, sat)
        return Color(int(r * 255), int(g * 255), int(b * 255), self.a)

    def darken(self, amount: float) -> Color:
        return self.lighten(-amount)


# ─── SZL Brand Palette ───────────────────────────────────────────────────────

VOID = Color.from_hex("#0A0A0F")
ABYSS = Color.from_hex("#12121A")
OBSIDIAN = Color.from_hex("#1A1A24")
GRAPHITE = Color.from_hex("#2A2A3A")

ACCENT = Color.from_hex("#805AD5")
ACCENT_BRIGHT = Color.from_hex("#A882FF")
ACCENT_DIM = Color.from_hex("#805AD522")

HYDRA_TEAL = Color.from_hex("#01696F")
GOLD = Color.from_hex("#B08940")
EMBER = Color.from_hex("#E85D3A")
FROST = Color.from_hex("#4ECDC4")

TEXT_PRIMARY = Color.from_hex("#F0F0F0")
TEXT_SECONDARY = Color.from_hex("#B4B4BE")
TEXT_MUTED = Color.from_hex("#6E6E78")

CARD_FILL = Color(255, 255, 255, 8)
CARD_STROKE = Color(255, 255, 255, 14)


class ProcPalette:
    """Deterministic procedural palette seeded by repo name.

    Generates unique but brand-harmonious color sequences for each repo,
    ensuring every social preview has a distinct identity while staying
    within the SZL visual language.
    """

    def __init__(self, seed: str):
        self._hash = hashlib.sha256(seed.encode()).digest()
        self._base_hue = (int.from_bytes(self._hash[:2], "big") % 360) / 360.0

    @property
    def seed_bytes(self) -> bytes:
        return self._hash

    @property
    def primary_hue(self) -> float:
        return self._base_hue * 360

    def accent(self, index: int = 0) -> Color:
        """Generate the nth accent color for this seed."""
        phi = (1 + math.sqrt(5)) / 2
        hue = (self._base_hue + index * (1 / phi)) % 1.0
        r, g, b = colorsys.hls_to_rgb(hue, 0.55, 0.75)
        return Color(int(r * 255), int(g * 255), int(b * 255))

    def gradient_stops(self, n: int = 4) -> list[Color]:
        """Generate n gradient stops for background decoration."""
        stops = []
        for i in range(n):
            t = i / max(n - 1, 1)
            byte_idx = (i * 4 + 4) % 28
            offset = int.from_bytes(self._hash[byte_idx : byte_idx + 2], "big") / 65535
            hue = (self._base_hue + offset * 0.15) % 1.0
            lightness = 0.06 + t * 0.04
            saturation = 0.4 + offset * 0.3
            r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
            stops.append(Color(int(r * 255), int(g * 255), int(b * 255)))
        return stops

    def noise_field(
        self, width: int, height: int, scale: float = 0.02
    ) -> Iterator[tuple[int, int, float]]:
        """Generate a deterministic value-noise field for procedural textures."""
        for y in range(height):
            for x in range(width):
                nx = x * scale
                ny = y * scale
                val = self._value_noise(nx, ny)
                yield (x, y, val)

    def _value_noise(self, x: float, y: float) -> float:
        """Simple deterministic value noise from seed."""
        ix, iy = int(math.floor(x)), int(math.floor(y))
        fx, fy = x - ix, y - iy
        fx = fx * fx * (3 - 2 * fx)
        fy = fy * fy * (3 - 2 * fy)

        def _hash_cell(cx: int, cy: int) -> float:
            data = (
                self._hash + cx.to_bytes(4, "big", signed=True) + cy.to_bytes(4, "big", signed=True)
            )
            h = hashlib.md5(data).digest()
            return int.from_bytes(h[:2], "big") / 65535.0

        v00 = _hash_cell(ix, iy)
        v10 = _hash_cell(ix + 1, iy)
        v01 = _hash_cell(ix, iy + 1)
        v11 = _hash_cell(ix + 1, iy + 1)

        top = v00 + (v10 - v00) * fx
        bottom = v01 + (v11 - v01) * fx
        return top + (bottom - top) * fy
