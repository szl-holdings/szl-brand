"""Deterministic front-door assets for the SZL Holdings public estate.

Surface Foundry turns a small, reviewed JSON contract into:

* a unique, accessible 1280 x 640 SVG hero;
* an idempotent README/model-card lead block; and
* a machine-readable receipt binding the copy to the visual output.

The same contract works for GitHub repositories and Hugging Face models,
kernels, datasets, Spaces, organization cards, and profile front doors.
Generation is offline and deterministic: a surface slug and contract always
produce identical bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import textwrap
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final, Iterable
from urllib.parse import urlsplit

SCHEMA: Final = "szl.surface-foundry/v3"
RECEIPT_SCHEMA: Final = "szl.surface-receipt/v1"
WIDTH: Final = 1280
HEIGHT: Final = 640
START_MARKER: Final = "<!-- SZL-SURFACE-CARD:v3:START -->"
END_MARKER: Final = "<!-- SZL-SURFACE-CARD:v3:END -->"
LEGACY_START: Final = "<!-- SZL-ESTATE-CARD:v2:START -->"
LEGACY_END: Final = "<!-- SZL-ESTATE-CARD:v2:END -->"

KINDS: Final = frozenset(
    {
        "org",
        "profile",
        "platform",
        "repo",
        "model",
        "kernel",
        "dataset",
        "space",
        "proof",
        "archived",
    }
)
EVIDENCE_LABELS: Final = frozenset(
    {
        "PROVED",
        "MEASURED",
        "REPORTED",
        "MODELED",
        "CONJECTURE",
        "ROADMAP",
        "UNKNOWN",
        "UNAVAILABLE",
    }
)
OPERATIONAL_STATES: Final = frozenset(
    {"OPERATIONAL", "PARTIAL", "DEGRADED", "UNAVAILABLE", "HISTORICAL"}
)
SLUG_RE: Final = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,95}$")
HEX_RE: Final = re.compile(r"^#[0-9A-Fa-f]{6}$")
BANNED_COPY: Final = (
    "best in the world",
    "world-class",
    "revolutionary",
    "unmatched",
    "guaranteed",
    "fully autonomous",
)

# One restrained palette per artifact family. The hash selects geometry, not a
# random rainbow, so the estate reads as one company rather than 100 microsites.
PALETTES: Final[dict[str, tuple[str, str, str]]] = {
    "org": ("#47D7C4", "#D7B55E", "#A9C5FF"),
    "profile": ("#E9EEF6", "#DF735F", "#9AA7BD"),
    "platform": ("#47D7C4", "#A9C5FF", "#D7B55E"),
    "repo": ("#9AA7BD", "#47D7C4", "#E9EEF6"),
    "model": ("#7CE8DA", "#A9C5FF", "#E9EEF6"),
    "kernel": ("#D7B55E", "#DF735F", "#E9EEF6"),
    "dataset": ("#A9C5FF", "#D7B55E", "#7CE8DA"),
    "space": ("#47D7C4", "#EFD694", "#A9C5FF"),
    "proof": ("#E9EEF6", "#47D7C4", "#D7B55E"),
    "archived": ("#738097", "#9AA7BD", "#B6C0CE"),
}

KIND_LABELS: Final = {
    "org": "ORGANIZATION",
    "profile": "FOUNDER PROFILE",
    "platform": "COMMAND PLATFORM",
    "repo": "SOURCE REPOSITORY",
    "model": "MODEL",
    "kernel": "GOVERNED KERNEL",
    "dataset": "DATASET",
    "space": "LIVE SURFACE",
    "proof": "PROOF SURFACE",
    "archived": "HISTORICAL ARTIFACT",
}


class SurfaceContractError(ValueError):
    """Raised when a surface contract is unsafe, ambiguous, or incomplete."""


@dataclass(frozen=True)
class SurfaceSpec:
    """Reviewed disclosure and navigation contract for one public surface."""

    slug: str
    display_name: str
    kind: str
    one_liner: str
    decision_path: str
    builder_path: str
    primary_url: str
    source_url: str
    evidence_url: str
    evidence_label: str
    operational_state: str
    limitations: str
    image_url: str = "./assets/surface-card.svg"
    accent: str | None = None

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "SurfaceSpec":
        allowed = set(cls.__dataclass_fields__)
        unknown = sorted(set(value) - allowed)
        required = {
            "slug",
            "display_name",
            "kind",
            "one_liner",
            "decision_path",
            "builder_path",
            "primary_url",
            "source_url",
            "evidence_url",
            "evidence_label",
            "operational_state",
            "limitations",
        }
        missing = sorted(required - set(value))
        if unknown:
            raise SurfaceContractError(
                "surface contains unknown fields: " + ", ".join(unknown)
            )
        if missing:
            raise SurfaceContractError(
                "surface is missing fields: " + ", ".join(missing)
            )
        spec = cls(**value)
        validate_surface(spec)
        return spec


@dataclass(frozen=True)
class SurfaceReceipt:
    schema: str
    surface: str
    kind: str
    contract_sha256: str
    svg_sha256: str
    readme_block_sha256: str
    visual_variant: int
    evidence_label: str
    operational_state: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, indent=2) + "\n"


def _is_https_url(value: str) -> bool:
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    return bool(
        parsed.scheme == "https"
        and parsed.netloc
        and parsed.username is None
        and parsed.password is None
    )


def validate_surface(spec: SurfaceSpec) -> None:
    """Fail closed on copy, navigation, state, and palette ambiguity."""

    errors: list[str] = []
    if not SLUG_RE.fullmatch(spec.slug):
        errors.append("slug must be 1-96 safe path characters")
    if spec.kind not in KINDS:
        errors.append("kind must be one of: " + ", ".join(sorted(KINDS)))
    if not (1 <= len(spec.display_name.strip()) <= 72):
        errors.append("display_name must be 1-72 characters")
    for name, value, maximum in (
        ("one_liner", spec.one_liner, 150),
        ("decision_path", spec.decision_path, 120),
        ("builder_path", spec.builder_path, 120),
        ("limitations", spec.limitations, 220),
    ):
        if not value.strip() or len(value.strip()) > maximum:
            errors.append(f"{name} must be 1-{maximum} characters")
    for name, value in (
        ("primary_url", spec.primary_url),
        ("source_url", spec.source_url),
        ("evidence_url", spec.evidence_url),
    ):
        if not _is_https_url(value):
            errors.append(f"{name} must be an HTTPS URL without credentials")
    try:
        image_parts = urlsplit(spec.image_url)
    except ValueError:
        image_parts = None
    if (
        image_parts is None
        or spec.image_url.startswith("//")
        or (image_parts.scheme and not _is_https_url(spec.image_url))
        or (image_parts.netloc and not _is_https_url(spec.image_url))
    ):
        errors.append("image_url must be a relative path or HTTPS URL")
    if spec.evidence_label not in EVIDENCE_LABELS:
        errors.append(
            "evidence_label must be one of: "
            + ", ".join(sorted(EVIDENCE_LABELS))
        )
    if spec.operational_state not in OPERATIONAL_STATES:
        errors.append(
            "operational_state must be one of: "
            + ", ".join(sorted(OPERATIONAL_STATES))
        )
    if spec.accent is not None and not HEX_RE.fullmatch(spec.accent):
        errors.append("accent must be a six-digit hexadecimal color")

    copy = " ".join(
        [
            spec.display_name,
            spec.one_liner,
            spec.decision_path,
            spec.builder_path,
            spec.limitations,
        ]
    ).casefold()
    for phrase in BANNED_COPY:
        if phrase in copy:
            errors.append(f"unsupported promotional claim is forbidden: {phrase}")

    if errors:
        raise SurfaceContractError("; ".join(errors))


def canonical_contract(spec: SurfaceSpec) -> bytes:
    """Return stable JSON bytes for hashing and receipts."""

    return (
        json.dumps(asdict(spec), sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def _digest(value: bytes | str) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def _seed(spec: SurfaceSpec) -> bytes:
    return hashlib.sha256(f"{spec.kind}:{spec.slug}".encode("utf-8")).digest()


def visual_variant(spec: SurfaceSpec) -> int:
    return _seed(spec)[0] % 6


def _palette(spec: SurfaceSpec) -> tuple[str, str, str]:
    primary, secondary, tertiary = PALETTES[spec.kind]
    return spec.accent or primary, secondary, tertiary


def _escape(value: str) -> str:
    return html.escape(value, quote=True)


def _wrap_svg_text(value: str, width: int, max_lines: int) -> list[str]:
    lines = textwrap.wrap(
        " ".join(value.split()),
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    )
    if not lines:
        return [""]
    if len(lines) <= max_lines:
        return lines
    kept = lines[:max_lines]
    last = kept[-1]
    kept[-1] = last[: max(1, width - 1)].rstrip() + "…"
    return kept


def _pattern(spec: SurfaceSpec, primary: str, secondary: str, tertiary: str) -> str:
    seed = _seed(spec)
    variant = visual_variant(spec)
    opacity = 0.16
    pieces: list[str] = [
        '<g aria-hidden="true" fill="none" stroke-linecap="round" '
        'stroke-linejoin="round">'
    ]

    if variant == 0:
        for i, radius in enumerate((92, 156, 226, 302)):
            color = (primary, tertiary, secondary, primary)[i]
            pieces.append(
                f'<circle cx="1002" cy="310" r="{radius}" stroke="{color}" '
                f'stroke-width="{2 if i < 2 else 1}" opacity="{opacity + i * 0.02:.2f}"/>'
            )
        for angle in range(0, 360, 45):
            pieces.append(
                f'<path d="M1002 310 l{230 + seed[angle // 45] % 80} 0" '
                f'transform="rotate({angle} 1002 310)" stroke="{tertiary}" '
                'stroke-width="1" opacity="0.10"/>'
            )
        pieces.append(
            f'<rect x="974" y="230" width="56" height="160" rx="20" '
            f'fill="{primary}" fill-opacity="0.18" stroke="{primary}" stroke-width="2"/>'
        )
    elif variant == 1:
        for i in range(8):
            y = 130 + i * 52 + seed[i] % 17
            bend = 32 + seed[i + 8] % 70
            color = (primary, tertiary, secondary)[i % 3]
            pieces.append(
                f'<path d="M780 {y} H930 q{bend} 0 {bend} {bend} H1180" '
                f'stroke="{color}" stroke-width="{1 + i % 2}" '
                f'opacity="{0.10 + i * 0.014:.3f}"/>'
            )
        for i in range(7):
            x = 864 + i * 47
            y = 140 + seed[20 + i] % 310
            pieces.append(
                f'<circle cx="{x}" cy="{y}" r="{4 + seed[(27 + i) % len(seed)] % 6}" '
                f'fill="{primary}" fill-opacity="0.32" stroke="none"/>'
            )
    elif variant == 2:
        for i in range(7):
            x = 820 + i * 55
            pieces.append(
                f'<path d="M{x} 100 V520" stroke="{tertiary}" stroke-width="1" '
                'opacity="0.12"/>'
            )
            for j in range(3):
                y = 150 + j * 118 + seed[(i * 3 + j) % len(seed)] % 66
                radius = 5 + seed[(i * 3 + j + 11) % len(seed)] % 8
                color = (primary, secondary, tertiary)[(i + j) % 3]
                pieces.append(
                    f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{color}" '
                    'fill-opacity="0.31" stroke="none"/>'
                )
        pieces.append(
            f'<path d="M770 112 H1190" stroke="{secondary}" stroke-width="2" opacity="0.23"/>'
        )
    elif variant == 3:
        pieces.extend(
            [
                f'<path d="M812 314 C812 166 964 108 1080 182 C1198 258 1178 432 1047 492 C905 557 781 454 812 314Z" stroke="{primary}" stroke-width="2" opacity="0.24"/>',
                f'<path d="M856 314 C856 216 952 172 1032 213 C1117 257 1112 376 1030 420 C941 468 849 411 856 314Z" stroke="{tertiary}" stroke-width="1" opacity="0.20"/>',
                f'<path d="M1118 190 l36 5 -18 31" stroke="{secondary}" stroke-width="3" opacity="0.48"/>',
                f'<circle cx="1032" cy="314" r="28" fill="{primary}" fill-opacity="0.16" stroke="none"/>',
            ]
        )
    elif variant == 4:
        points: list[tuple[int, int]] = []
        for i in range(11):
            x = 790 + (seed[i] * 360 // 255)
            y = 110 + (seed[i + 11] * 410 // 255)
            points.append((x, y))
        for i, (x1, y1) in enumerate(points):
            for j in range(i + 1, len(points)):
                if seed[(i + j + 22) % len(seed)] % 4 == 0:
                    x2, y2 = points[j]
                    pieces.append(
                        f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{tertiary}" '
                        'stroke-width="1" opacity="0.09"/>'
                    )
            color = (primary, secondary, tertiary)[i % 3]
            pieces.append(
                f'<circle cx="{x1}" cy="{y1}" r="{5 + seed[(i + 7) % 32] % 7}" '
                f'fill="{color}" fill-opacity="0.34" stroke="none"/>'
            )
    else:
        for row in range(4):
            for col in range(3):
                i = row * 3 + col
                x = 790 + col * 126 + seed[i] % 15
                y = 112 + row * 104 + seed[i + 12] % 15
                w = 94 + seed[(i + 5) % 32] % 24
                h = 70 + seed[(i + 19) % 32] % 20
                color = (primary, secondary, tertiary)[(row + col) % 3]
                pieces.append(
                    f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" '
                    f'stroke="{color}" stroke-width="1" opacity="0.17"/>'
                )
                pieces.append(
                    f'<path d="M{x + 15} {y + 22} H{x + w - 15} M{x + 15} {y + 40} H{x + w - 28}" '
                    f'stroke="{color}" stroke-width="2" opacity="0.18"/>'
                )
    pieces.append("</g>")
    return "\n".join(pieces)


def render_surface_svg(spec: SurfaceSpec) -> str:
    """Render one deterministic, self-contained, accessible SVG front door."""

    validate_surface(spec)
    primary, secondary, tertiary = _palette(spec)
    seed = _seed(spec)
    variant = visual_variant(spec)
    title_lines = _wrap_svg_text(spec.display_name, width=23, max_lines=2)
    lede_lines = _wrap_svg_text(spec.one_liner, width=62, max_lines=3)
    kind_label = KIND_LABELS[spec.kind]
    surface_id = _digest(canonical_contract(spec))[:12]

    title_tspans = [
        f'<tspan x="74" dy="{0 if index == 0 else 78}">{_escape(line)}</tspan>'
        for index, line in enumerate(title_lines)
    ]
    lede_tspans = [
        f'<tspan x="76" dy="{0 if index == 0 else 31}">{_escape(line)}</tspan>'
        for index, line in enumerate(lede_lines)
    ]

    core_y = 158
    lede_y = core_y + 94 + (len(title_lines) - 1) * 78
    path_y = min(468, lede_y + 82)

    micro_marks = []
    for i in range(17):
        x = 62 + i * 66 + seed[i % 32] % 18
        opacity = 0.06 + (seed[(i + 8) % 32] % 8) / 100
        micro_marks.append(
            f'<circle cx="{x}" cy="593" r="1.5" fill="{tertiary}" opacity="{opacity:.2f}"/>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title description">
  <title id="title">{_escape(spec.display_name)} — {kind_label.title()}</title>
  <desc id="description">{_escape(spec.one_liner)} Evidence label: {_escape(spec.evidence_label)}. Operational state: {_escape(spec.operational_state)}.</desc>
  <defs>
    <linearGradient id="surface" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#030F29"/><stop offset="0.56" stop-color="#071421"/><stop offset="1" stop-color="#0A1724"/></linearGradient>
    <radialGradient id="glow" cx="82%" cy="42%" r="57%"><stop offset="0" stop-color="{primary}" stop-opacity="0.16"/><stop offset="0.55" stop-color="{tertiary}" stop-opacity="0.06"/><stop offset="1" stop-color="#030F29" stop-opacity="0"/></radialGradient>
    <linearGradient id="hairline" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{primary}" stop-opacity="0.72"/><stop offset="0.52" stop-color="{secondary}" stop-opacity="0.46"/><stop offset="1" stop-color="{tertiary}" stop-opacity="0.08"/></linearGradient>
    <filter id="soft-glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="7" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <rect width="1280" height="640" rx="30" fill="url(#surface)"/>
  <rect width="1280" height="640" rx="30" fill="url(#glow)"/>
  <rect x="1" y="1" width="1278" height="638" rx="29" fill="none" stroke="#9AA7BD" stroke-opacity="0.18"/>
  <path d="M0 0 H1280" stroke="url(#hairline)" stroke-width="4"/>
  <path d="M56 58 H1224" stroke="#9AA7BD" stroke-opacity="0.14"/>
  <circle cx="75" cy="58" r="5" fill="{primary}" filter="url(#soft-glow)"/>
  <text x="94" y="64" fill="#B6C0CE" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15" font-weight="700" letter-spacing="2.2">SZL / {kind_label} / {surface_id}</text>
  {_pattern(spec, primary, secondary, tertiary)}
  <g font-family="Aptos, system-ui, -apple-system, Segoe UI, sans-serif">
    <text x="74" y="{core_y}" fill="#F4F6F8" font-size="68" font-weight="750" letter-spacing="-2.7">{''.join(title_tspans)}</text>
    <text x="76" y="{lede_y}" fill="#C9D3DF" font-size="24" font-weight="430">{''.join(lede_tspans)}</text>
    <g transform="translate(74 {path_y})"><rect width="222" height="46" rx="23" fill="{primary}" fill-opacity="0.11" stroke="{primary}" stroke-opacity="0.48"/><circle cx="23" cy="23" r="5" fill="{primary}"/><text x="39" y="29" fill="#E9EEF6" font-size="14" font-weight="700" letter-spacing="1.1">{_escape(spec.evidence_label)}</text></g>
    <g transform="translate(310 {path_y})"><rect width="232" height="46" rx="23" fill="#101824" stroke="#9AA7BD" stroke-opacity="0.35"/><path d="M22 16 v14 M15 23 h14" stroke="{secondary}" stroke-width="2"/><text x="42" y="29" fill="#E9EEF6" font-size="14" font-weight="700" letter-spacing="1.1">{_escape(spec.operational_state)}</text></g>
  </g>
  <g font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="13"><text x="75" y="566" fill="#8592A5">CONTROL BEFORE ACTION</text><path d="M264 561 H282 M276 555 L282 561 L276 567" fill="none" stroke="{primary}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><text x="294" y="566" fill="#8592A5">EVIDENCE AFTER</text><text x="1206" y="566" text-anchor="end" fill="#8592A5">{_escape(spec.primary_url.removeprefix('https://'))}</text></g>
  {''.join(micro_marks)}
  <circle cx="1192" cy="58" r="6" fill="{secondary}" filter="url(#soft-glow)"/>
  <text x="1211" y="64" fill="#9AA7BD" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="13">V{variant + 1}</text>
</svg>
'''


def render_avatar_svg(spec: SurfaceSpec, *, profile: bool = False) -> str:
    """Render a high-resolution, small-size-safe vector avatar."""

    validate_surface(spec)
    primary, secondary, tertiary = _palette(spec)
    seed = _seed(spec)
    rotation = -18 - seed[2] % 10
    core = (
        '<path d="M402 332 C365 291 238 299 229 367 C220 430 342 438 365 476 C395 525 338 574 251 561" fill="none" stroke="#F4F6F8" stroke-width="72" stroke-linecap="round"/>'
        '<path d="M420 303 H642 V378 L532 516 H642 V594 H420 V520 L531 381 H420Z" fill="#F4F6F8"/>'
        '<path d="M677 303 H754 V516 H881 L816 594 H677Z" fill="#F4F6F8"/>'
    )
    if profile:
        core = (
            '<path d="M470 334 C432 292 292 300 282 370 C273 435 397 444 421 485 C450 535 388 589 295 574" fill="none" stroke="#F4F6F8" stroke-width="74" stroke-linecap="round"/>'
            '<path d="M548 306 H638 V554 H823 L750 642 H548Z" fill="#F4F6F8"/>'
        )
    label = "Founder profile mark" if profile else "SZL Holdings organization mark"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024" role="img" aria-labelledby="avatar-title avatar-desc">
  <title id="avatar-title">{_escape(label)}</title>
  <desc id="avatar-desc">High-resolution KANCHAY mark designed to remain legible at small avatar sizes.</desc>
  <defs>
    <linearGradient id="orbit" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E9EEF6"/><stop offset="0.52" stop-color="{tertiary}"/><stop offset="1" stop-color="#5C6B86"/></linearGradient>
    <radialGradient id="node" cx="38%" cy="34%" r="75%"><stop offset="0" stop-color="#F4B0A2"/><stop offset="0.55" stop-color="{secondary}"/><stop offset="1" stop-color="#C4543F"/></radialGradient>
    <radialGradient id="field" cx="50%" cy="42%" r="70%"><stop offset="0" stop-color="#0D2540"/><stop offset="1" stop-color="#030F29"/></radialGradient>
    <filter id="avatar-glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="12" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <rect width="1024" height="1024" rx="196" fill="url(#field)"/>
  <rect x="18" y="18" width="988" height="988" rx="180" fill="none" stroke="#9AA7BD" stroke-opacity="0.18" stroke-width="4"/>
  <g transform="rotate({rotation} 512 470)"><ellipse cx="512" cy="470" rx="370" ry="214" fill="none" stroke="url(#orbit)" stroke-width="15" opacity="0.95"/></g>
  <circle cx="824" cy="245" r="31" fill="url(#node)" filter="url(#avatar-glow)"/>
  {core}
  <path d="M512 750 L558 858 H534 L512 793 L490 858 H466Z" fill="url(#orbit)" opacity="0.96"/>
  <circle cx="512" cy="470" r="294" fill="none" stroke="{primary}" stroke-opacity="0.08" stroke-width="3"/>
</svg>
'''


def _markdown_cell(value: str) -> str:
    return html.escape(" ".join(value.split()), quote=False).replace("|", "\\|")


def render_readme_block(spec: SurfaceSpec) -> str:
    """Render an investor-readable and developer-usable managed lead block."""

    validate_surface(spec)
    alt = f"{spec.display_name} — {spec.one_liner}"
    one_liner = _markdown_cell(spec.one_liner)
    decision_path = _markdown_cell(spec.decision_path)
    builder_path = _markdown_cell(spec.builder_path)
    limitations = _markdown_cell(spec.limitations.rstrip(".")) + "."
    return f'''{START_MARKER}
<p align="center">
  <a href="{spec.primary_url}">
    <img src="{spec.image_url}" alt="{html.escape(alt, quote=True)}" width="100%" />
  </a>
</p>

> {one_liner}

| Path | What a non-technical reader gets | Where a builder starts |
| --- | --- | --- |
| **Understand** | {decision_path} | [Open the primary surface]({spec.primary_url}) |
| **Build** | {builder_path} | [Inspect source]({spec.source_url}) |
| **Verify** | `{spec.evidence_label}` evidence · `{spec.operational_state}` runtime | [Inspect evidence]({spec.evidence_url}) |

<sub>{limitations} A signature proves scoped integrity and origin; it does not prove accuracy, safety, performance, compliance, or authorization.</sub>
{END_MARKER}
'''


def _managed_range(text: str, start: str, end: str) -> tuple[int, int] | None:
    starts = text.count(start)
    ends = text.count(end)
    if starts == 0 and ends == 0:
        return None
    if starts != 1 or ends != 1:
        raise SurfaceContractError(
            f"managed block markers must occur exactly once: {start!r}={starts}, {end!r}={ends}"
        )
    begin = text.find(start)
    finish = text.find(end, begin + len(start))
    if finish < begin:
        raise SurfaceContractError(f"managed block closes before it opens: {start!r}")
    return begin, finish + len(end)


def _front_matter_end(text: str) -> int:
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return 0
    match = re.search(r"\r?\n---\r?\n", text[4:])
    if match is None:
        raise SurfaceContractError("README starts YAML front matter but never closes it")
    return 4 + match.end()


def replace_managed_block(readme: str, block: str) -> str:
    """Idempotently insert v3 or migrate the legacy v2 managed block."""

    normalized = block.strip() + "\n"
    current = _managed_range(readme, START_MARKER, END_MARKER)
    legacy = _managed_range(readme, LEGACY_START, LEGACY_END)
    if current and legacy:
        raise SurfaceContractError("README contains both v2 and v3 managed blocks")
    target = current or legacy
    if target:
        before, after = target
        prefix = readme[:before].rstrip()
        suffix = readme[after:].lstrip()
        if prefix and suffix:
            return prefix + "\n\n" + normalized + "\n" + suffix
        if prefix:
            return prefix + "\n\n" + normalized
        if suffix:
            return normalized + "\n" + suffix
        return normalized

    offset = _front_matter_end(readme)
    prefix = readme[:offset].rstrip()
    suffix = readme[offset:].lstrip()
    if prefix and suffix:
        return prefix + "\n\n" + normalized + "\n" + suffix
    if prefix:
        return prefix + "\n\n" + normalized
    if suffix:
        return normalized + "\n" + suffix
    return normalized


def build_receipt(spec: SurfaceSpec, svg: str, readme_block: str) -> SurfaceReceipt:
    return SurfaceReceipt(
        schema=RECEIPT_SCHEMA,
        surface=spec.slug,
        kind=spec.kind,
        contract_sha256=_digest(canonical_contract(spec)),
        svg_sha256=_digest(svg),
        readme_block_sha256=_digest(readme_block),
        visual_variant=visual_variant(spec),
        evidence_label=spec.evidence_label,
        operational_state=spec.operational_state,
    )


def load_manifest(path: Path) -> list[SurfaceSpec]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SurfaceContractError(f"manifest is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise SurfaceContractError("manifest root must be an object")
    if set(value) != {"schema", "surfaces"}:
        raise SurfaceContractError("manifest keys must be exactly schema and surfaces")
    if value.get("schema") != SCHEMA:
        raise SurfaceContractError(f"manifest schema must be {SCHEMA}")
    rows = value.get("surfaces")
    if not isinstance(rows, list) or not rows:
        raise SurfaceContractError("manifest surfaces must be a non-empty array")
    specs: list[SurfaceSpec] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise SurfaceContractError(f"surface {index} must be an object")
        spec = SurfaceSpec.from_mapping(row)
        folded = spec.slug.casefold()
        if folded in seen:
            raise SurfaceContractError(f"duplicate surface slug: {spec.slug}")
        seen.add(folded)
        specs.append(spec)
    return specs


def safe_output_name(slug: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", slug).strip(".-").lower()


def generate_surfaces(specs: Iterable[SurfaceSpec], output: Path) -> list[Path]:
    """Generate reviewed assets without touching any remote provider."""

    created: list[Path] = []
    output.mkdir(parents=True, exist_ok=True)
    for spec in specs:
        directory = output / safe_output_name(spec.slug)
        directory.mkdir(parents=True, exist_ok=True)
        svg = render_surface_svg(spec)
        avatar = render_avatar_svg(spec, profile=spec.kind == "profile")
        block = render_readme_block(spec)
        receipt = build_receipt(spec, svg, block)
        artifacts = {
            "surface-card.svg": svg,
            "avatar.svg": avatar,
            "README.block.md": block,
            "surface.json": json.dumps(asdict(spec), sort_keys=True, indent=2) + "\n",
            "receipt.json": receipt.to_json(),
        }
        for name, content in artifacts.items():
            path = directory / name
            path.write_text(content, encoding="utf-8", newline="\n")
            created.append(path)
    return created


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="szl-surface",
        description="Generate deterministic SZL Holdings GitHub and Hugging Face front doors.",
    )
    parser.add_argument("manifest", type=Path, help="Surface Foundry v3 JSON manifest")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output directory")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        specs = load_manifest(args.manifest)
        paths = generate_surfaces(specs, args.output)
    except (OSError, SurfaceContractError) as exc:
        print(f"error: {exc}")
        return 2
    print(f"generated {len(paths)} artifacts for {len(specs)} surfaces in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
