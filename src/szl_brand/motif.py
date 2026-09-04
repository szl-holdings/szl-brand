"""Deterministic class-native visual motifs for the SZL public estate.

Estate class selects information architecture. Surface identity selects a stable
SHA-seeded variant inside that class. The compiler emits local profile, CSS,
accessible SVG, and receipt artifacts only; it grants no deployment authority.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final

from .estate import (
    FLAGSHIP_PRODUCT,
    GOVERNANCE_PROOF,
    HISTORICAL,
    PLATFORM_CONTROL,
    RESEARCH_FORMULA,
    RUNTIME_INFRA,
    UNCLASSIFIED,
)

SCHEMA: Final = "szl.class-motif/v1"
RECEIPT_SCHEMA: Final = "szl.class-motif-receipt/v1"
WIDTH: Final = 1280
HEIGHT: Final = 640
SLUG_RE: Final = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,95}$")
PUBLIC_CLASSES: Final = frozenset(
    {
        FLAGSHIP_PRODUCT,
        PLATFORM_CONTROL,
        RUNTIME_INFRA,
        GOVERNANCE_PROOF,
        RESEARCH_FORMULA,
        HISTORICAL,
        UNCLASSIFIED,
    }
)
THEMES: Final[dict[str, dict[str, str]]] = {
    FLAGSHIP_PRODUCT: {
        "family": "DOMAIN_COMMAND",
        "motif": "decision_graph",
        "density": "HIGH",
        "primary": "#57EBFF",
        "secondary": "#7F8CFF",
        "tertiary": "#F2C96D",
        "interaction": "MAP_GRAPH_TIMELINE",
        "evidence": "PERSISTENT_RIGHT_RAIL",
        "motion": "STATUS_ONLY",
    },
    PLATFORM_CONTROL: {
        "family": "FOUNDRY_CONTROL",
        "motif": "stage_pipeline",
        "density": "HIGH",
        "primary": "#7F8CFF",
        "secondary": "#57EBFF",
        "tertiary": "#72FFA4",
        "interaction": "PIPELINE_QUEUE_MATRIX",
        "evidence": "STAGE_RECEIPT_RAIL",
        "motion": "FLOW_ONLY",
    },
    RUNTIME_INFRA: {
        "family": "SUBSTRATE_RUNTIME",
        "motif": "topology_trace",
        "density": "HIGH",
        "primary": "#72FFA4",
        "secondary": "#57EBFF",
        "tertiary": "#A9C5FF",
        "interaction": "TOPOLOGY_TRACE_CONSOLE",
        "evidence": "TRACE_FOOTER",
        "motion": "PULSE_ONLY",
    },
    GOVERNANCE_PROOF: {
        "family": "PROOF_LEDGER",
        "motif": "receipt_chain",
        "density": "MEDIUM",
        "primary": "#F2C96D",
        "secondary": "#E9EEF6",
        "tertiary": "#57EBFF",
        "interaction": "RECEIPT_TIMELINE_HASH_CHAIN",
        "evidence": "PRIMARY_CANVAS",
        "motion": "NONE",
    },
    RESEARCH_FORMULA: {
        "family": "FORMULA_NOTEBOOK",
        "motif": "derivation_graph",
        "density": "MEDIUM",
        "primary": "#A9C5FF",
        "secondary": "#E9EEF6",
        "tertiary": "#DF735F",
        "interaction": "DERIVATION_CITATION_MATRIX",
        "evidence": "MARGIN_NOTES",
        "motion": "NONE",
    },
    HISTORICAL: {
        "family": "ARCHIVE_MONO",
        "motif": "archive_timeline",
        "density": "LOW",
        "primary": "#9AA7BD",
        "secondary": "#738097",
        "tertiary": "#B6C0CE",
        "interaction": "HISTORY_TIMELINE",
        "evidence": "HISTORICAL_BANNER",
        "motion": "NONE",
    },
    UNCLASSIFIED: {
        "family": "NEUTRAL_REVIEW",
        "motif": "inventory_grid",
        "density": "LOW",
        "primary": "#B6C0CE",
        "secondary": "#71859A",
        "tertiary": "#57EBFF",
        "interaction": "INVENTORY_REVIEW",
        "evidence": "REVIEW_BANNER",
        "motion": "NONE",
    },
}


class MotifContractError(ValueError):
    """A public motif request is malformed or outside the public contract."""


@dataclass(frozen=True)
class MotifRequest:
    slug: str
    display_name: str
    estate_class: str

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> MotifRequest:
        if set(value) != {"slug", "display_name", "estate_class"}:
            raise MotifContractError(
                "motif request keys must be exactly slug, display_name, and estate_class"
            )
        request = cls(**value)
        _validate_request(request)
        return request


@dataclass(frozen=True)
class MotifProfile:
    schema: str
    slug: str
    display_name: str
    estate_class: str
    theme_family: str
    motif: str
    variant: int
    density: str
    primary: str
    secondary: str
    tertiary: str
    interaction: str
    evidence_placement: str
    motion: str
    surface_fingerprint: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, indent=2) + "\n"


@dataclass(frozen=True)
class MotifReceipt:
    schema: str
    surface: str
    profile_sha256: str
    svg_sha256: str
    css_sha256: str
    theme_family: str
    variant: int
    authority: str = "NONE"

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, indent=2) + "\n"


def _validate_request(request: MotifRequest) -> None:
    errors: list[str] = []
    if not SLUG_RE.fullmatch(request.slug):
        errors.append("slug must be 1-96 safe path characters")
    if not request.display_name.strip() or len(request.display_name.strip()) > 72:
        errors.append("display_name must be 1-72 characters")
    if request.estate_class not in PUBLIC_CLASSES:
        errors.append("estate_class is not eligible for a public motif")
    if errors:
        raise MotifContractError("; ".join(errors))


def _seed(request: MotifRequest) -> bytes:
    return hashlib.sha256(f"{request.estate_class}:{request.slug}".encode()).digest()


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def build_profile(request: MotifRequest) -> MotifProfile:
    """Return the deterministic class architecture and surface variant."""
    _validate_request(request)
    theme = THEMES[request.estate_class]
    seed = _seed(request)
    fingerprint = hashlib.sha256(
        f"{request.slug}:{theme['family']}:{seed.hex()}".encode()
    ).hexdigest()[:16]
    return MotifProfile(
        schema=SCHEMA,
        slug=request.slug,
        display_name=request.display_name,
        estate_class=request.estate_class,
        theme_family=theme["family"],
        motif=theme["motif"],
        variant=seed[0] % 8,
        density=theme["density"],
        primary=theme["primary"],
        secondary=theme["secondary"],
        tertiary=theme["tertiary"],
        interaction=theme["interaction"],
        evidence_placement=theme["evidence"],
        motion=theme["motion"],
        surface_fingerprint=fingerprint,
    )


def render_css(profile: MotifProfile) -> str:
    """Render portable class tokens with mobile and accessibility guarantees."""
    return f'''/* SZL class motif {profile.theme_family} / {profile.surface_fingerprint} */
:root {{
  --szl-motif-family: "{profile.theme_family}";
  --szl-motif-variant: {profile.variant};
  --szl-motif-primary: {profile.primary};
  --szl-motif-secondary: {profile.secondary};
  --szl-motif-tertiary: {profile.tertiary};
  --szl-motif-bg: #03070c;
  --szl-motif-panel: rgba(10, 20, 32, .86);
  --szl-motif-line: rgba(169, 197, 255, .16);
  --szl-motif-ink: #f5fbff;
  --szl-motif-touch: 44px;
}}
[data-szl-motif="{profile.theme_family}"] {{
  color-scheme: dark;
  background: var(--szl-motif-bg);
  color: var(--szl-motif-ink);
  max-inline-size: 100%;
  overflow-x: clip;
}}
[data-szl-motif="{profile.theme_family}"] .szl-motif-panel {{
  min-inline-size: 0;
  border: 1px solid var(--szl-motif-line);
  border-radius: 16px;
  background: var(--szl-motif-panel);
}}
[data-szl-motif="{profile.theme_family}"] button,
[data-szl-motif="{profile.theme_family}"] [role="button"],
[data-szl-motif="{profile.theme_family}"] a.szl-motif-action {{
  min-block-size: var(--szl-motif-touch);
  min-inline-size: var(--szl-motif-touch);
}}
[data-szl-motif="{profile.theme_family}"] :focus-visible {{
  outline: 3px solid var(--szl-motif-primary);
  outline-offset: 3px;
}}
@media (pointer: coarse) {{
  [data-szl-motif="{profile.theme_family}"] {{ --szl-motif-touch: 48px; }}
}}
@media (prefers-reduced-motion: reduce) {{
  [data-szl-motif="{profile.theme_family}"] *,
  [data-szl-motif="{profile.theme_family}"] *::before,
  [data-szl-motif="{profile.theme_family}"] *::after {{
    animation-duration: .001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .001ms !important;
    scroll-behavior: auto !important;
  }}
}}
'''


def _text(x: int, y: int, value: str, *, fill: str = "#9FB0C2", size: int = 12) -> str:
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-family="ui-monospace,monospace" '
        f'font-size="{size}">{html.escape(value)}</text>'
    )


def _rect(
    x: int,
    y: int,
    width: int,
    height: int,
    *,
    stroke: str,
    fill: str = "#07101A",
) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="14" '
        f'fill="{fill}" stroke="{stroke}"/>'
    )


def _circle(x: int, y: int, radius: int, *, color: str) -> str:
    return (
        f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{color}" '
        f'fill-opacity=".16" stroke="{color}"/>'
    )


def _line(x1: int, y1: int, x2: int, y2: int, *, color: str) -> str:
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2"/>'


def _header(profile: MotifProfile) -> str:
    return "".join(
        (
            _text(64, 62, f"SZL / {profile.theme_family} / {profile.surface_fingerprint}"),
            _text(64, 128, profile.display_name, fill="#F5FBFF", size=42),
            _text(64, 162, f"{profile.interaction} · {profile.evidence_placement}"),
        )
    )


def _product_body(profile: MotifProfile, seed: bytes) -> str:
    pieces = [
        _rect(64, 218, 690, 312, stroke=profile.primary),
        _text(90, 256, "DECISION / MAP / EVIDENCE", fill=profile.primary),
        _rect(930, 98, 278, 432, stroke=profile.tertiary),
        _text(956, 136, "EVIDENCE RAIL", fill=profile.tertiary),
    ]
    coordinates = [(148, 352), (310, 286), (468, 398), (638, 304)]
    for index, (x, y) in enumerate(coordinates):
        pieces.append(_circle(x, y, 13 + seed[index] % 9, color=profile.primary))
        if index:
            previous_x, previous_y = coordinates[index - 1]
            pieces.append(_line(previous_x, previous_y, x, y, color=profile.secondary))
    return "".join(pieces)


def _control_body(profile: MotifProfile, seed: bytes) -> str:
    pieces: list[str] = []
    for index, label in enumerate(("INGEST", "NORMALIZE", "EVALUATE", "APPROVE", "PUBLISH")):
        x = 64 + index * 232
        y = 278 + (seed[index] % 2) * 34
        pieces.extend(
            (
                _rect(x, y, 184, 92, stroke=profile.primary),
                _text(x + 18, y + 52, label, fill="#F5FBFF"),
            )
        )
        if index:
            pieces.append(_line(x - 48, y + 46, x, y + 46, color=profile.secondary))
    return "".join(pieces)


def _runtime_body(profile: MotifProfile, seed: bytes) -> str:
    pieces = [_rect(64, 214, 1150, 330, stroke=profile.primary)]
    coordinates = [(140, 310), (330, 280), (520, 372), (720, 300), (930, 400), (1110, 292)]
    for index, (x, y) in enumerate(coordinates):
        pieces.append(_circle(x, y, 10 + seed[index] % 12, color=profile.primary))
        pieces.append(_text(x - 32, y + 42, f"NODE-{index + 1}"))
        if index:
            previous_x, previous_y = coordinates[index - 1]
            pieces.append(_line(previous_x, previous_y, x, y, color=profile.secondary))
    pieces.append(_text(90, 252, "TOPOLOGY / TRACE WATERFALL", fill=profile.primary))
    return "".join(pieces)


def _proof_body(profile: MotifProfile, seed: bytes) -> str:
    pieces: list[str] = []
    previous_x = 0
    for index in range(4):
        x = 80 + index * 292
        y = 246 + (seed[index] % 2) * 24
        pieces.extend(
            (
                _rect(x, y, 236, 124, stroke=profile.primary),
                _text(x + 18, y + 38, f"RECEIPT-{index + 1}", fill=profile.primary),
                _text(x + 18, y + 76, f"sha256:{seed.hex()[index * 8 : index * 8 + 12]}"),
            )
        )
        if index:
            pieces.append(_line(previous_x + 236, y + 62, x, y + 62, color=profile.secondary))
        previous_x = x
    return "".join(pieces)


def _formula_body(profile: MotifProfile, seed: bytes) -> str:
    return "".join(
        (
            _rect(64, 210, 742, 344, stroke=profile.primary),
            _text(96, 274, "Λ = f(E, P, A)", fill=profile.primary, size=30),
            _text(96, 326, "DERIVATION OPEN", fill=profile.tertiary),
            _text(96, 376, f"variant = {seed[0] % 8}"),
            _text(96, 416, "proof status = explicit"),
            _rect(848, 210, 360, 344, stroke=profile.secondary),
            _text(878, 254, "CITATIONS / ASSUMPTIONS", fill=profile.secondary),
        )
    )


def _historical_body(profile: MotifProfile, seed: bytes) -> str:
    pieces = [
        _rect(64, 224, 1144, 260, stroke=profile.primary, fill="#090D12"),
        _text(94, 270, "HISTORICAL ARTIFACT · NO LIVE RUNTIME CLAIM", fill=profile.primary),
    ]
    for index in range(6):
        x = 110 + index * 190
        pieces.append(_circle(x, 370 + seed[index] % 18, 6, color=profile.secondary))
        if index:
            pieces.append(_line(x - 190, 378, x, 378, color=profile.secondary))
    return "".join(pieces)


def _neutral_body(profile: MotifProfile, seed: bytes) -> str:
    pieces = [_text(64, 210, "REVIEW REQUIRED · CLASSIFICATION NOT YET PROMOTED")]
    for index in range(8):
        column = index % 4
        row = index // 4
        x = 64 + column * 288
        y = 246 + row * 146
        pieces.append(_rect(x, y, 242, 108, stroke=profile.primary))
        pieces.append(_text(x + 18, y + 46, f"ITEM-{index + 1} / {seed[index]:02X}"))
    return "".join(pieces)


def render_svg(profile: MotifProfile) -> str:
    """Render one accessible SVG with class-native information architecture."""
    request = MotifRequest(profile.slug, profile.display_name, profile.estate_class)
    seed = _seed(request)
    bodies = {
        FLAGSHIP_PRODUCT: _product_body,
        PLATFORM_CONTROL: _control_body,
        RUNTIME_INFRA: _runtime_body,
        GOVERNANCE_PROOF: _proof_body,
        RESEARCH_FORMULA: _formula_body,
        HISTORICAL: _historical_body,
        UNCLASSIFIED: _neutral_body,
    }
    body = bodies[profile.estate_class](profile, seed)
    title = html.escape(f"{profile.display_name} — {profile.theme_family}")
    description = html.escape(
        f"Deterministic {profile.motif} visualization, variant {profile.variant}; "
        "CONTROL BEFORE ACTION; deployment authority NONE."
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" '
        'aria-labelledby="szl-title szl-desc">\n'
        f'<title id="szl-title">{title}</title>\n'
        f'<desc id="szl-desc">{description}</desc>\n'
        '<rect width="1280" height="640" fill="#03070C"/>\n'
        f"{_header(profile)}{body}\n"
        f"{_text(64, 606, 'CONTROL BEFORE ACTION · AUTHORITY NONE', fill=profile.tertiary)}\n"
        "</svg>\n"
    )


def build_receipt(profile: MotifProfile, svg: str, css: str) -> MotifReceipt:
    """Bind the exact profile, SVG, and CSS bytes without claiming a signature."""
    return MotifReceipt(
        schema=RECEIPT_SCHEMA,
        surface=profile.slug,
        profile_sha256=_digest(profile.to_json()),
        svg_sha256=_digest(svg),
        css_sha256=_digest(css),
        theme_family=profile.theme_family,
        variant=profile.variant,
    )


def build_bundle(
    request: MotifRequest,
) -> tuple[MotifProfile, str, str, MotifReceipt]:
    """Build one deterministic in-memory artifact bundle."""
    profile = build_profile(request)
    css = render_css(profile)
    svg = render_svg(profile)
    receipt = build_receipt(profile, svg, css)
    return profile, css, svg, receipt


def write_bundle(
    request: MotifRequest,
    output_dir: str | Path,
) -> dict[str, Path]:
    """Write exactly the four declared public motif artifacts."""
    profile, css, svg, receipt = build_bundle(request)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    paths = {
        "profile": destination / "surface-profile.json",
        "css": destination / "motif.css",
        "svg": destination / "motif.svg",
        "receipt": destination / "motif-receipt.json",
    }
    paths["profile"].write_text(profile.to_json(), encoding="utf-8")
    paths["css"].write_text(css, encoding="utf-8")
    paths["svg"].write_text(svg, encoding="utf-8")
    paths["receipt"].write_text(receipt.to_json(), encoding="utf-8")
    return paths


def load_manifest(path: str | Path) -> list[MotifRequest]:
    """Load and strictly validate a motif manifest."""
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MotifContractError(f"cannot read motif manifest: {type(exc).__name__}") from exc
    if not isinstance(payload, dict) or set(payload) != {"schema", "surfaces"}:
        raise MotifContractError("manifest keys must be exactly schema and surfaces")
    if payload["schema"] != SCHEMA or not isinstance(payload["surfaces"], list):
        raise MotifContractError("manifest schema or surfaces collection is invalid")
    requests = [
        MotifRequest.from_mapping(item) for item in payload["surfaces"] if isinstance(item, dict)
    ]
    if len(requests) != len(payload["surfaces"]):
        raise MotifContractError("every surface must be an object")
    slugs = [request.slug for request in requests]
    if len(slugs) != len(set(slugs)):
        raise MotifContractError("surface slugs must be unique")
    return requests


def generate_motifs(
    requests: list[MotifRequest],
    output_dir: str | Path,
) -> list[Path]:
    """Generate four deterministic artifacts for every manifest surface."""
    root = Path(output_dir)
    paths: list[Path] = []
    for request in requests:
        written = write_bundle(request, root / request.slug)
        paths.extend(written.values())
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic SZL class motifs")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    paths = generate_motifs(load_manifest(args.manifest), args.output)
    print(json.dumps({"schema": SCHEMA, "artifacts": [str(path) for path in paths]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
