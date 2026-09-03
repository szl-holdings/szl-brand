"""Class-native visual motif compiler for the SZL Holdings public estate.

A reviewed estate class determines information architecture; the stable surface
slug determines a deterministic variation inside that class. Generation is
provider-neutral and produces only local SVG/CSS/profile/receipt artifacts.
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

from szl_brand.estate import (
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
    """Raised when a public motif request is malformed or unsafe."""


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
        validate_request(request)
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

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, indent=2) + "\n"


def validate_request(request: MotifRequest) -> None:
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


def build_profile(request: MotifRequest) -> MotifProfile:
    validate_request(request)
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
    """Render portable class tokens with mobile/accessibility guarantees."""

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
  --szl-motif-gutter: clamp(14px, 3vw, 32px);
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


def _svg_header(profile: MotifProfile) -> str:
    pieces = [
        f'<text x="64" y="68" fill="#B6C0CE" font-family="ui-monospace,monospace" '
        f'font-size="14">SZL / {profile.theme_family} / {profile.surface_fingerprint}</text>',
        f'<text x="64" y="142" fill="#F5FBFF" font-family="system-ui,sans-serif" '
        f'font-size="54" font-weight="720">{html.escape(profile.display_name, quote=True)}</text>',
        f'<text x="64" y="178" fill="#9FB0C2" font-family="ui-monospace,monospace" '
        f'font-size="13">{profile.interaction} · {profile.evidence_placement}</text>',
    ]
    return "".join(pieces)


def _domain_command(profile: MotifProfile, seed: bytes) -> str:
    pieces = [
        '<rect x="64" y="238" width="500" height="250" rx="18" fill="#07101A" '
        'stroke="#203142"/>',
        f'<path d="M92 430 C180 340 255 446 342 318 S490 366 536 286" fill="none" '
        f'stroke="{profile.primary}" stroke-width="3"/>',
        '<text x="90" y="276" fill="#9FB0C2" font-family="ui-monospace,monospace" '
        'font-size="12">DECISION / MAP / EVIDENCE</text>',
        '<rect x="970" y="104" width="240" height="404" rx="18" fill="#07101A" '
        'stroke="#203142"/>',
        '<text x="996" y="140" fill="#9FB0C2" font-family="ui-monospace,monospace" '
        'font-size="12">EVIDENCE RAIL</text>',
    ]
    for index in range(6):
        x = 680 + (seed[index] % 5) * 92
        y = 120 + index * 70
        color = (profile.primary, profile.secondary, profile.tertiary)[index % 3]
        pieces.append(
            f'<circle cx="{x}" cy="{y}" r="{10 + seed[index + 8] % 9}" '
            f'fill="{color}" fill-opacity=".18" stroke="{color}"/>'
        )
    return "".join(pieces)


def _foundry_control(profile: MotifProfile, seed: bytes) -> str:
    pieces: list[str] = []
    labels = ("INGEST", "TRANSFORM", "EVALUATE", "APPROVE", "PUBLISH")
    for index, label in enumerate(labels):
        x = 78 + index * 232
        y = 286 + (seed[index] % 2) * 24
        pieces.extend(
            [
                f'<rect x="{x}" y="{y}" width="174" height="86" rx="14" fill="#07101A" '
                f'stroke="{profile.primary}" stroke-opacity=".34"/>',
                f'<text x="{x + 18}" y="{y + 47}" fill="#E9EEF6" '
                f'font-family="ui-monospace,monospace" font-size="13">{label}</text>',
            ]
        )
    return "".join(pieces)


def _substrate_runtime(profile: MotifProfile, seed: bytes) -> str:
    pieces = [
        '<rect x="960" y="226" width="250" height="300" rx="16" fill="#050C14" '
        'stroke="#203142"/>',
        '<text x="986" y="254" fill="#9FB0C2" font-family="ui-monospace,monospace" '
        'font-size="12">TOPOLOGY</text>',
    ]
    for index in range(6):
        y = 250 + index * 46
        offset = 60 + seed[index] % 130
        width = 380 + seed[index + 10] % 260
        pieces.extend(
            [
                f'<text x="70" y="{y + 10}" fill="#9FB0C2" '
                f'font-family="ui-monospace,monospace" font-size="11">SPAN-{index + 1:02d}</text>',
                f'<rect x="{220 + offset}" y="{y}" width="{width}" height="14" rx="7" '
                f'fill="{profile.primary}" fill-opacity=".20"/>',
            ]
        )
    return "".join(pieces)


def _proof_ledger(profile: MotifProfile, seed: bytes) -> str:
    pieces: list[str] = []
    for index in range(5):
        y = 246 + index * 64
        digest = hashlib.sha256(seed + bytes([index])).hexdigest()[:12]
        pieces.extend(
            [
                f'<circle cx="110" cy="{y}" r="9" fill="{profile.primary}"/>',
                f'<rect x="204" y="{y - 22}" width="700" height="44" rx="10" '
                'fill="#07101A" stroke="#203142"/>',
                f'<text x="226" y="{y + 5}" fill="#D7E0EA" '
                f'font-family="ui-monospace,monospace" font-size="12">RECEIPT-{index + 1} · '
                f"sha256:{digest}</text>",
            ]
        )
    return "".join(pieces)


def _formula_notebook(profile: MotifProfile, seed: bytes) -> str:
    pieces: list[str] = []
    equations = ("Λ = f(E, P, A)", "τ = Σ wᵢ·eᵢ", "R = H(receipt)", "Δ = observed − modeled")
    for index, equation in enumerate(equations):
        y = 260 + index * 70
        pieces.extend(
            [
                f'<text x="94" y="{y}" fill="#E9EEF6" font-family="Georgia,serif" '
                f'font-size="26">{html.escape(equation)}</text>',
                f'<text x="520" y="{y}" fill="#8294A8" font-family="ui-monospace,monospace" '
                f'font-size="11">NOTE {seed[index] % 97:02d} · DERIVATION OPEN</text>',
            ]
        )
    return "".join(pieces)


def _archive_mono(profile: MotifProfile, seed: bytes) -> str:
    pieces = [
        '<rect x="64" y="232" width="1148" height="72" rx="14" fill="#0A1018" '
        'stroke="#4C596A"/>',
        '<text x="90" y="276" fill="#B6C0CE" font-family="ui-monospace,monospace" '
        'font-size="14">HISTORICAL ARTIFACT · NO LIVE RUNTIME CLAIM</text>',
    ]
    for index in range(6):
        x = 100 + index * 190
        y = 400 + (seed[index] % 3) * 18
        pieces.extend(
            [
                f'<circle cx="{x}" cy="{y}" r="7" fill="#9AA7BD"/>',
                f'<path d="M{x + 7} {y} H{x + 175}" stroke="#738097"/>',
            ]
        )
    return "".join(pieces)


def _neutral_review(profile: MotifProfile, seed: bytes) -> str:
    pieces: list[str] = []
    for index in range(8):
        row, column = divmod(index, 4)
        x = 68 + column * 286
        y = 244 + row * 142
        pieces.extend(
            [
                f'<rect x="{x}" y="{y}" width="248" height="108" rx="14" '
                'fill="#07101A" stroke="#203142"/>',
                f'<circle cx="{x + 28}" cy="{y + 30}" r="6" fill="{profile.primary}" '
                f'fill-opacity=".{3 + seed[index] % 5}"/>',
            ]
        )
    return "".join(pieces)


def render_svg(profile: MotifProfile) -> str:
    """Render an accessible hero whose structure is native to the estate class."""

    request = MotifRequest(profile.slug, profile.display_name, profile.estate_class)
    validate_request(request)
    seed = _seed(request)
    if profile.estate_class == FLAGSHIP_PRODUCT:
        body = _domain_command(profile, seed)
    elif profile.estate_class == PLATFORM_CONTROL:
        body = _foundry_control(profile, seed)
    elif profile.estate_class == RUNTIME_INFRA:
        body = _substrate_runtime(profile, seed)
    elif profile.estate_class == GOVERNANCE_PROOF:
        body = _proof_ledger(profile, seed)
    elif profile.estate_class == RESEARCH_FORMULA:
        body = _formula_notebook(profile, seed)
    elif profile.estate_class == HISTORICAL:
        body = _archive_mono(profile, seed)
    else:
        body = _neutral_review(profile, seed)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title description">
<title id="title">{html.escape(profile.display_name)} — {profile.theme_family}</title>
<desc id="description">SZL Holdings {profile.theme_family} motif. Interaction family: {profile.interaction}. Evidence placement: {profile.evidence_placement}. Variant {profile.variant}.</desc>
<rect width="1280" height="640" rx="28" fill="#03070C"/>
<rect x="1" y="1" width="1278" height="638" rx="27" fill="none" stroke="#203142"/>
<path d="M0 0 H1280" stroke="{profile.primary}" stroke-width="4" opacity=".72"/>
{_svg_header(profile)}{body}
<text x="64" y="596" fill="#71859A" font-family="ui-monospace,monospace" font-size="12">CONTROL BEFORE ACTION · EVIDENCE AFTER · V{profile.variant + 1}</text>
</svg>
'''


def build_receipt(profile: MotifProfile, svg: str, css: str) -> MotifReceipt:
    return MotifReceipt(
        schema=RECEIPT_SCHEMA,
        surface=profile.slug,
        profile_sha256=hashlib.sha256(profile.to_json().encode()).hexdigest(),
        svg_sha256=hashlib.sha256(svg.encode()).hexdigest(),
        css_sha256=hashlib.sha256(css.encode()).hexdigest(),
        theme_family=profile.theme_family,
        variant=profile.variant,
    )


def load_manifest(path: Path) -> list[MotifRequest]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MotifContractError(f"manifest is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict) or set(payload) != {"schema", "surfaces"}:
        raise MotifContractError("manifest root keys must be exactly schema and surfaces")
    if payload.get("schema") != SCHEMA:
        raise MotifContractError(f"manifest schema must be {SCHEMA}")
    rows = payload.get("surfaces")
    if not isinstance(rows, list) or not rows:
        raise MotifContractError("surfaces must be a non-empty array")
    requests: list[MotifRequest] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise MotifContractError(f"surface {index} must be an object")
        request = MotifRequest.from_mapping(row)
        folded = request.slug.casefold()
        if folded in seen:
            raise MotifContractError(f"duplicate surface slug: {request.slug}")
        seen.add(folded)
        requests.append(request)
    return requests


def _safe_name(slug: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", slug).strip(".-").lower()


def generate_motifs(requests: list[MotifRequest], output: Path) -> list[Path]:
    """Write deterministic motif artifacts without remote-provider mutation."""

    output.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    for request in requests:
        profile = build_profile(request)
        svg = render_svg(profile)
        css = render_css(profile)
        receipt = build_receipt(profile, svg, css)
        directory = output / _safe_name(request.slug)
        directory.mkdir(parents=True, exist_ok=True)
        artifacts = {
            "surface-profile.json": profile.to_json(),
            "motif.svg": svg,
            "motif.css": css,
            "motif-receipt.json": receipt.to_json(),
        }
        for name, content in artifacts.items():
            path = directory / name
            path.write_text(content, encoding="utf-8", newline="\n")
            created.append(path)
    return created


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="szl-motif",
        description="Generate class-native SZL motif assets from reviewed estate classes.",
    )
    parser.add_argument("manifest", type=Path, help="Class motif v1 JSON manifest")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output directory")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        requests = load_manifest(args.manifest)
        paths = generate_motifs(requests, args.output)
    except (OSError, MotifContractError) as exc:
        print(f"error: {exc}")
        return 2
    print(f"generated {len(paths)} motif artifacts for {len(requests)} surfaces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
