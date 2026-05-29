"""Procedural social preview generator — deterministic generative identity.

Each repo gets a unique visual fingerprint generated from its name hash,
while maintaining strict brand consistency. Features:
- Seeded procedural noise backgrounds
- Geometric accent patterns (unique per repo)
- Dynamic stat cards with glassmorphic styling
- Accessibility-checked contrast ratios
- Pixel-perfect 1280×640 output
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from szl_brand.palette import (
    CARD_FILL,
    CARD_STROKE,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    Color,
    ProcPalette,
)

W, H = 1280, 640

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


@dataclass
class StatCard:
    """A metric card displayed on the banner."""

    value: str
    label: str


@dataclass
class PreviewSpec:
    """Specification for a single social preview banner."""

    repo: str
    kicker: str
    title: str
    subtitle: str
    tag: str
    stats: list[StatCard] = field(default_factory=list)


def _vgradient(w: int, h: int, stops: list[Color]) -> Image.Image:
    """Multi-stop vertical gradient."""
    img = Image.new("RGB", (w, h))
    px = img.load()
    n = len(stops) - 1
    for y in range(h):
        t = y / (h - 1)
        seg = min(int(t * n), n - 1)
        local_t = (t * n) - seg
        c = stops[seg].lerp(stops[seg + 1], local_t)
        for x in range(w):
            px[x, y] = c.rgb
    return img


def _draw_geometric_accent(img: Image.Image, palette: ProcPalette) -> None:
    """Draw unique geometric patterns based on repo seed."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    seed = palette.seed_bytes
    pattern_type = seed[0] % 4

    accent = palette.accent(0)
    accent_dim = accent.with_alpha(18)

    if pattern_type == 0:
        num_circles = 3 + (seed[1] % 4)
        for i in range(num_circles):
            cx = W - 200 + (seed[2 + i] % 160) - 80
            cy = 100 + (seed[6 + i] % 400)
            radius = 40 + (seed[10 + i] % 120)
            draw.ellipse(
                [cx - radius, cy - radius, cx + radius, cy + radius],
                outline=accent_dim.rgba,
                width=2,
            )
    elif pattern_type == 1:
        num_lines = 5 + (seed[1] % 6)
        for i in range(num_lines):
            x_start = W - 350 + (seed[2 + i] % 300)
            y_start = seed[8 + i] % H
            length = 80 + (seed[14 + i] % 200)
            angle = (seed[20 + i] % 180) * math.pi / 180
            x_end = int(x_start + length * math.cos(angle))
            y_end = int(y_start + length * math.sin(angle))
            draw.line([(x_start, y_start), (x_end, y_end)], fill=accent_dim.rgba, width=1)
    elif pattern_type == 2:
        num_rects = 2 + (seed[1] % 3)
        for i in range(num_rects):
            x = W - 300 + (seed[2 + i * 3] % 200)
            y = 50 + (seed[3 + i * 3] % 500)
            w = 40 + (seed[4 + i * 3] % 100)
            h_r = 40 + (seed[5 + i * 3] % 100)
            draw.rectangle([x, y, x + w, y + h_r], outline=accent_dim.rgba, width=1)
    else:
        cx, cy = W - 200, H // 2
        num_points = 6 + (seed[1] % 5)
        points = []
        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points + (seed[2] % 100) / 100
            r = 80 + (seed[3 + i] % 80)
            points.append((int(cx + r * math.cos(angle)), int(cy + r * math.sin(angle))))
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                if (seed[i + j] % 3) != 0:
                    draw.line([points[i], points[j]], fill=accent_dim.rgba, width=1)

    img.paste(overlay, (0, 0), overlay)


def _draw_noise_texture(img: Image.Image, palette: ProcPalette, intensity: float = 0.03) -> None:
    """Apply subtle procedural noise texture for depth."""
    noise = Image.new("RGBA", (W // 4, H // 4), (0, 0, 0, 0))
    px = noise.load()
    for x, y, val in palette.noise_field(W // 4, H // 4, scale=0.08):
        alpha = int(val * intensity * 255)
        px[x, y] = (255, 255, 255, alpha)
    noise = noise.resize((W, H), Image.NEAREST)
    img.paste(noise, (0, 0), noise)


def _draw_accent_bar(img: Image.Image, palette: ProcPalette) -> None:
    """Left accent bar + bottom glow line."""
    draw = ImageDraw.Draw(img)
    accent = palette.accent(0)
    draw.rectangle([0, 0, 5, H], fill=accent.rgb)

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle([0, H - 4, W, H], fill=accent.with_alpha(60).rgba)
    img.paste(overlay, (0, 0), overlay)


def _draw_stat_card(
    img: Image.Image,
    x: int,
    y: int,
    w: int,
    h: int,
    stat: StatCard,
    palette: ProcPalette,
) -> None:
    """Glassmorphic stat card with procedural accent."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle(
        [x, y, x + w, y + h],
        radius=12,
        fill=CARD_FILL.rgba,
        outline=CARD_STROKE.rgba,
        width=1,
    )
    img.paste(overlay, (0, 0), overlay)

    draw = ImageDraw.Draw(img)
    accent_color = palette.accent(0)

    for size in (34, 30, 26, 22, 18):
        f_val = ImageFont.truetype(FONT_BOLD, size)
        bb = draw.textbbox((0, 0), stat.value, font=f_val)
        if bb[2] - bb[0] <= w - 24:
            break

    f_lbl = ImageFont.truetype(FONT_REG, 13)
    bb = draw.textbbox((0, 0), stat.value, font=f_val)
    vw = bb[2] - bb[0]
    draw.text((x + w // 2 - vw // 2, y + 18), stat.value, fill=accent_color.rgb, font=f_val)

    bb2 = draw.textbbox((0, 0), stat.label, font=f_lbl)
    lw = bb2[2] - bb2[0]
    draw.text((x + w // 2 - lw // 2, y + h - 30), stat.label, fill=TEXT_MUTED.rgb, font=f_lbl)


def _draw_tag_pill(
    draw: ImageDraw.ImageDraw, img: Image.Image, tag: str, palette: ProcPalette
) -> None:
    """Accent-colored tag pill."""
    f_pill = ImageFont.truetype(FONT_BOLD, 13)
    pill_w = max(100, draw.textbbox((0, 0), tag, font=f_pill)[2] + 36)

    accent = palette.accent(0)
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle(
        [80, 295, 80 + pill_w, 295 + 30],
        radius=4,
        fill=accent.with_alpha(22).rgba,
        outline=accent.rgba,
        width=1,
    )
    img.paste(overlay, (0, 0), overlay)

    bb = draw.textbbox((0, 0), tag, font=f_pill)
    tw = bb[2] - bb[0]
    draw.text((80 + pill_w // 2 - tw // 2, 302), tag, fill=accent.rgb, font=f_pill)


def generate_preview(spec: PreviewSpec, output: Path) -> Path:
    """Generate a single social preview banner.

    Returns the path to the generated PNG file.
    """
    palette = ProcPalette(spec.repo)
    stops = palette.gradient_stops(4)

    img = _vgradient(W, H, stops)
    _draw_noise_texture(img, palette, intensity=0.025)
    _draw_geometric_accent(img, palette)
    _draw_accent_bar(img, palette)

    draw = ImageDraw.Draw(img)

    f_kick = ImageFont.truetype(FONT_REG, 16)
    draw.text((80, 80), spec.kicker, fill=TEXT_MUTED.rgb, font=f_kick)

    for tsize in (78, 70, 62, 54, 48, 42):
        f_title = ImageFont.truetype(FONT_BOLD, tsize)
        if draw.textbbox((0, 0), spec.title, font=f_title)[2] <= W - 180:
            break
    draw.text((80, 130), spec.title, fill=TEXT_PRIMARY.rgb, font=f_title)

    f_sub = ImageFont.truetype(FONT_REG, 24)
    draw.text((80, 240), spec.subtitle, fill=TEXT_SECONDARY.rgb, font=f_sub)

    _draw_tag_pill(draw, img, spec.tag, palette)

    if spec.stats:
        card_w = 210
        card_h = 96
        card_y = 380
        gap = 20
        for i, stat in enumerate(spec.stats[:3]):
            _draw_stat_card(img, 80 + i * (card_w + gap), card_y, card_w, card_h, stat, palette)

    f_foot = ImageFont.truetype(FONT_REG, 14)
    draw.text((80, H - 48), "github.com/szl-holdings", fill=TEXT_MUTED.rgb, font=f_foot)
    f_mono = ImageFont.truetype(FONT_MONO, 22)
    bb_m = draw.textbbox((0, 0), "SZL", font=f_mono)
    mw = bb_m[2] - bb_m[0]
    draw.text((W - 80 - mw, H - 50), "SZL", fill=palette.accent(0).rgb, font=f_mono)

    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(output, "PNG", optimize=True)
    return output


# ─── Default repo registry ────────────────────────────────────────────────────

REGISTRY: list[PreviewSpec] = [
    PreviewSpec(
        "a11oy",
        "GOVERNED EXECUTION",
        "A11oy",
        "Orchestration + Decision Fabric + Trust Plane",
        "PLATFORM",
        [StatCard("7", "Surfaces"), StatCard("Λ", "Invariant"), StatCard("CPS", "Standard")],
    ),
    PreviewSpec(
        "sentra",
        "CYBER",
        "Sentra",
        "Governed adversary loop, typed receipts",
        "CYBER",
        [StatCard("6", "Proof Steps"), StatCard("0", "Drift"), StatCard("24/7", "Posture")],
    ),
    PreviewSpec(
        "vessels",
        "MARITIME",
        "Vessels",
        "Fleet intelligence & sanctions screening",
        "MARITIME",
        [StatCard("AIS", "Live"), StatCard("OFAC", "Screening"), StatCard("Dark", "Detect")],
    ),
    PreviewSpec(
        "terra",
        "REAL ESTATE",
        "Terra",
        "Deal pipeline & portfolio analytics",
        "REAL ESTATE",
        [StatCard("Deal", "Scoring"), StatCard("Mkt", "Signals"), StatCard("Port", "Analytics")],
    ),
    PreviewSpec(
        "counsel",
        "LEGAL",
        "Counsel",
        "Policy-gated legal workflows",
        "LEGAL",
        [StatCard("Pol", "Gated"), StatCard("Doc", "Review"), StatCard("Obli", "Mapping")],
    ),
    PreviewSpec(
        "carlota-jo",
        "ADVISORY",
        "Carlota Jo",
        "Concierge advisory operations",
        "ADVISORY",
        [StatCard("MP", "Approval"), StatCard("CPS", "Delivery"), StatCard("Conc", "Workflow")],
    ),
    PreviewSpec(
        "amaru",
        "DATA SYNC",
        "Amaru",
        "Convergent multi-source data sync",
        "DATA",
        [
            StatCard("Δ", "Append-Only"),
            StatCard("Hash", "Verified"),
            StatCard("10+", "Innovations"),
        ],
    ),
    PreviewSpec(
        "ouroboros",
        "RUNTIME",
        "Ouroboros",
        "Bounded-loop runtime — Λ invariant",
        "RUNTIME",
        [StatCard("≤0.59ms", "Λ p99"), StatCard("28", "Packages"), StatCard("62", "Guardrails")],
    ),
    PreviewSpec(
        "ouroboros-thesis",
        "RESEARCH",
        "Ouroboros Thesis",
        "Lutar Invariant Family v1→v11",
        "RESEARCH",
        [StatCard("11", "Papers"), StatCard("v11", "Latest"), StatCard("DOI", "Zenodo")],
    ),
    PreviewSpec(
        "szl-cookbook",
        "ENGINEERING",
        "szl-cookbook",
        "Anthropic skills pattern — 9 SKILL.md",
        "OSS",
        [StatCard("9", "Skills"), StatCard("MD", "SKILL.md"), StatCard("Apache", "2.0")],
    ),
    PreviewSpec(
        "szl-trust",
        "PUBLIC TRUST",
        "szl-trust",
        "Covenant Proof Standard artifacts",
        "TRUST",
        [StatCard("11", "Artifacts"), StatCard("0", "Mocked"), StatCard("Det", "Replay")],
    ),
    PreviewSpec(
        ".github",
        "SZL HOLDINGS",
        "SZL Holdings",
        "Governed decision infrastructure",
        "ORG",
        [StatCard("7", "Surfaces"), StatCard("11", "Papers"), StatCard("44", "Innovations")],
    ),
    PreviewSpec(
        "stephenlutar2-hash",
        "FOUNDER & CEO",
        "Stephen P. Lutar Jr.",
        "Founder, SZL Holdings · The Lutar Invariant",
        "PROFILE",
        [StatCard("SZL", "Holdings"), StatCard("Λ", "Author"), StatCard("9", "Formal Axes")],
    ),
    PreviewSpec(
        "szl-brand",
        "BRAND",
        "szl-brand",
        "Brand assets & deterministic banners",
        "BRAND",
        [StatCard("14", "Banners"), StatCard("CC", "BY 4.0"), StatCard("Det", "Builder")],
    ),
]


def generate_all(output_dir: Path) -> list[Path]:
    """Generate all registered social previews."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for spec in REGISTRY:
        out = output_dir / f"{spec.repo}.png"
        generate_preview(spec, out)
        paths.append(out)
    return paths
