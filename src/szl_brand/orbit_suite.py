# SPDX-License-Identifier: Apache-2.0
# (c) 2026 Lutar, Stephen P. - SZL Holdings - ORCID 0009-0001-0110-4173
"""Derive the Orbit v2 asset suite from the approved master vector.

Every vector in ``kit/logos/orbit-v2/suite/`` is computed from the exact bytes of
``kit/logos/orbit-v2/szl-orbit.svg`` (pinned by ``kit/logos/orbit-v2/manifest.json``): the same
letter outlines, orbit angle, node and palette, re-composed for one placement each. Nothing is
redrawn by hand and no font is read. Raster exports (PNG, ICO) are rendered from those vectors
with resvg and pinned by sha256 in ``suite/manifest.json``; ``check`` rebuilds the vectors and
verifies every recorded hash without needing a renderer.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Final

MASTER: Final = "kit/logos/orbit-v2/szl-orbit.svg"
MASTER_MANIFEST: Final = "kit/logos/orbit-v2/manifest.json"
SUITE_DIR: Final = "kit/logos/orbit-v2/suite"
SUITE_VERSION: Final = "1.0.0"

NAVY: Final = "#030F29"
WHITE: Final = "#FFFFFF"
CORAL: Final = "#DF735F"
SILVER_100: Final = "#E9EEF6"
SILVER_300: Final = "#9AA7BD"
SILVER_500: Final = "#5C6B86"
GRAPHITE: Final = "#080B12"

ORBIT_DEGREES: Final = -22.0
# Visual centre of the three letters in the master's 600-unit space.
LETTER_CENTRE: Final = (299.8, 299.1)

# Raster exports: output path -> (source vector, width, height).
RASTERS: Final = {
    "png/szl-orbit-512.png": ("szl-orbit.svg", 512, 512),
    "png/szl-orbit-1024.png": ("szl-orbit.svg", 1024, 1024),
    "png/szl-orbit-mono-navy-1024.png": ("szl-orbit-mono-navy.svg", 1024, 1024),
    "png/szl-orbit-mono-white-1024.png": ("szl-orbit-mono-white.svg", 1024, 1024),
    "png/szl-orbit-holo-1024.png": ("szl-orbit-holo.svg", 1024, 1024),
    "png/favicon-16.png": ("szl-icon-16.svg", 16, 16),
    "png/favicon-32.png": ("szl-icon-32.svg", 32, 32),
    "png/favicon-48.png": ("szl-icon-32.svg", 48, 48),
    "png/apple-touch-icon-180.png": ("szl-avatar.svg", 180, 180),
    "png/icon-192.png": ("szl-avatar.svg", 192, 192),
    "png/icon-512.png": ("szl-avatar.svg", 512, 512),
    "png/icon-maskable-512.png": ("szl-icon-maskable.svg", 512, 512),
    "png/szl-avatar-512.png": ("szl-avatar.svg", 512, 512),
    "png/szl-avatar-1024.png": ("szl-avatar.svg", 1024, 1024),
    "png/szl-social-1200x630.png": ("szl-social-1200x630.svg", 1200, 630),
}
ICO: Final = {"favicon.ico": ("png/favicon-16.png", "png/favicon-32.png", "png/favicon-48.png")}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _master(root: Path) -> tuple[bytes, ET.Element]:
    data = (root / MASTER).read_bytes()
    pinned = json.loads((root / MASTER_MANIFEST).read_text(encoding="utf-8"))["sha256"]
    if hashlib.sha256(data).hexdigest() != pinned:
        raise ValueError(f"{MASTER} does not match the sha256 pinned in {MASTER_MANIFEST}")
    return data, ET.fromstring(data.decode("utf-8"))


def _by_id(tree: ET.Element, element_id: str) -> ET.Element:
    for node in tree.iter():
        if node.attrib.get("id") == element_id:
            return node
    raise ValueError(f"master is missing #{element_id}")


def _letters(tree: ET.Element) -> list[str]:
    return [_by_id(tree, f"letter-{name}").attrib["d"] for name in "SZL"]


def _node(tree: ET.Element) -> tuple[float, float, float]:
    node = _by_id(tree, "orbit-node")
    return float(node.attrib["cx"]), float(node.attrib["cy"]), float(node.attrib["r"])


def _lambda(tree: ET.Element) -> str:
    return _by_id(tree, "lambda-detail").attrib["d"]


def _fmt(value: float) -> str:
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return "0" if text == "-0" else text


def _on_orbit(rx: float, ry: float, degrees: float) -> tuple[float, float]:
    """Point at parameter angle ``degrees`` on the master's rotated orbit, centred at 300,300."""

    t = math.radians(degrees)
    a = math.radians(ORBIT_DEGREES)
    x, y = rx * math.cos(t), ry * math.sin(t)
    return 300 + x * math.cos(a) - y * math.sin(a), 300 + x * math.sin(a) + y * math.cos(a)


def _letter_group(paths: list[str], fill: str, scale: float = 1.0, knockout: float = 0.0) -> str:
    """The three master outlines, optionally scaled about their centre with a navy gap ring."""

    cx, cy = LETTER_CENTRE
    transform = ""
    if scale != 1.0:
        transform = (
            f' transform="translate(300 300) scale({_fmt(scale)}) '
            f'translate({_fmt(-cx)} {_fmt(-cy)})"'
        )
    gap = ""
    if knockout:
        width = _fmt(knockout / scale)
        gap = (
            f'<g fill="{NAVY}" stroke="{NAVY}" stroke-width="{width}" stroke-linejoin="round">'
            + "".join(f'<path d="{d}"/>' for d in paths)
            + "</g>"
        )
    return (
        f"<g{transform}>{gap}"
        + f'<g fill="{fill}">'
        + "".join(f'<path d="{d}"/>' for d in paths)
        + "</g></g>"
    )


def _svg(view_box: str, title: str, desc: str, body: str, *, key: str) -> bytes:
    text = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}" role="img" '
        f'aria-labelledby="{key}-title {key}-desc">'
        f'<title id="{key}-title">{title}</title><desc id="{key}-desc">{desc}</desc>'
        f"{body}</svg>\n"
    )
    return text.encode("utf-8")


def _mono(tree: ET.Element, color: str, key: str, ground: str) -> bytes:
    """One color, no tile. The orbit is masked around the letters so it cannot merge into them."""

    paths = _letters(tree)
    nx, ny, nr = _node(tree)
    gap = (
        f'<mask id="{key}-gap" maskUnits="userSpaceOnUse" x="0" y="0" width="600" height="600">'
        '<rect width="600" height="600" fill="#FFFFFF"/>'
        '<g fill="#000000" stroke="#000000" stroke-width="22" stroke-linejoin="round">'
        + "".join(f'<path d="{d}"/>' for d in paths)
        + "</g></mask>"
    )
    body = (
        f"<defs>{gap}</defs>"
        f'<g mask="url(#{key}-gap)">'
        f'<g transform="rotate({_fmt(ORBIT_DEGREES)} 300 300)" fill="none" stroke="{color}">'
        '<ellipse cx="300" cy="300" rx="250" ry="116" stroke-width="3"/>'
        '<path d="M50 300 A250 116 0 0 0 550 300" stroke-width="9" stroke-linecap="round"/>'
        '<path d="M50 300 A250 116 0 0 1 550 300" stroke-width="5" stroke-linecap="round"/>'
        "</g></g>"
        + _letter_group(paths, color)
        + f'<circle cx="{_fmt(nx)}" cy="{_fmt(ny)}" r="{_fmt(nr)}" fill="{color}"/>'
        + f'<path d="{_lambda(tree)}" fill="{color}"/>'
    )
    return _svg(
        "0 0 600 600",
        "SZL Holdings",
        f"Single-color SZL orbit mark without its tile, for {ground} grounds.",
        body,
        key=key,
    )


def _holo(master: bytes) -> bytes:
    """The master with a restrained silver material: a quiet plane, edge light and a node glint."""

    text = master.decode("utf-8")
    nx, ny = 484.263, 166.817
    defs = (
        '<radialGradient id="holo-plane" cx="0.28" cy="0.2" r="0.9">'
        f'<stop offset="0" stop-color="{SILVER_100}" stop-opacity="0.16"/>'
        f'<stop offset="0.5" stop-color="{SILVER_300}" stop-opacity="0.05"/>'
        f'<stop offset="1" stop-color="{NAVY}" stop-opacity="0"/>'
        "</radialGradient>"
        f'<linearGradient id="holo-edge" x1="75" y1="440" x2="490" y2="145" gradientUnits="userSpaceOnUse">'
        f'<stop stop-color="{WHITE}"/><stop offset="0.35" stop-color="{SILVER_100}"/>'
        f'<stop offset="0.7" stop-color="{SILVER_500}"/><stop offset="1" stop-color="{SILVER_100}"/>'
        "</linearGradient>"
        f'<radialGradient id="holo-glint" cx="{nx}" cy="{ny}" r="44" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="{CORAL}" stop-opacity="0.45"/>'
        f'<stop offset="1" stop-color="{CORAL}" stop-opacity="0"/>'
        "</radialGradient>"
    )
    text = re.sub(r'<linearGradient id="orbit-silver".*?</linearGradient>', "", text, flags=re.S)
    text = text.replace("<defs>", "<defs>" + defs, 1)
    text = text.replace("url(#orbit-silver)", "url(#holo-edge)")
    text = text.replace(
        '<g id="orbit-ring"',
        '<rect id="holo-plane-fill" width="600" height="600" rx="88" fill="url(#holo-plane)"/>'
        '<g id="orbit-ring"',
        1,
    )
    text = text.replace(
        '<circle id="orbit-node"',
        f'<circle id="node-glint" cx="{nx}" cy="{ny}" r="44" fill="url(#holo-glint)"/>'
        '<circle id="orbit-node"',
        1,
    )
    text = re.sub(
        r'aria-labelledby="szl-orbit-title szl-orbit-desc"',
        'aria-labelledby="szl-orbit-holo-title szl-orbit-holo-desc"',
        text,
    )
    text = text.replace('id="szl-orbit-title"', 'id="szl-orbit-holo-title"')
    text = re.sub(
        r'<desc id="szl-orbit-desc">[^<]*</desc>',
        '<desc id="szl-orbit-holo-desc">The SZL orbit mark with a restrained silver material: '
        "a quiet light plane on the tile, silver edge light on the orbit and a warm glint at the "
        "coral node. For hero and feature placements only.</desc>",
        text,
    )
    return text.encode("utf-8")


def _icon(tree: ET.Element, *, size: int) -> bytes:
    paths = _letters(tree)
    if size == 16:
        nx, ny = _on_orbit(262, 122, -62)
        body = (
            f'<rect width="600" height="600" rx="132" fill="{NAVY}"/>'
            + _letter_group(paths, WHITE, scale=1.34)
            + f'<circle cx="{_fmt(nx)}" cy="{_fmt(ny)}" r="44" fill="{CORAL}"/>'
        )
        desc = "SZL letters and the coral node, for placements of 20 pixels and smaller."
    else:
        nx, ny = _on_orbit(262, 122, -62)
        body = (
            f'<rect width="600" height="600" rx="120" fill="{NAVY}"/>'
            f'<ellipse cx="300" cy="300" rx="262" ry="122" fill="none" stroke="{SILVER_300}" '
            f'stroke-width="22" transform="rotate({_fmt(ORBIT_DEGREES)} 300 300)"/>'
            + _letter_group(paths, WHITE, scale=1.2, knockout=22)
            + f'<circle cx="{_fmt(nx)}" cy="{_fmt(ny)}" r="30" fill="{CORAL}"/>'
        )
        desc = "SZL letters, one orbit and the coral node, for placements of 24 to 48 pixels."
    return _svg("0 0 600 600", "SZL Holdings", desc, body, key=f"szl-icon-{size}")


def _avatar(tree: ET.Element, master: bytes, *, maskable: bool) -> bytes:
    """Full-bleed square; content stays inside the round crop (and the maskable safe zone)."""

    text = master.decode("utf-8")
    inner = text.split("</defs>", 1)[1].rsplit("</svg>", 1)[0]
    inner = re.sub(r'<rect id="navy-tile"[^>]*/>', "", inner)
    inner = re.sub(r'<path id="lambda-detail"[^>]*/>', "", inner)
    defs = text.split("<defs>", 1)[1].split("</defs>", 1)[0]
    scale = 0.82 if maskable else 1.0
    if scale != 1.0:
        inner = f'<g transform="translate(300 300) scale({_fmt(scale)}) translate(-300 -300)">{inner}</g>'
    key = "szl-icon-maskable" if maskable else "szl-avatar"
    desc = (
        "Full-bleed SZL orbit mark sized for the maskable-icon safe zone."
        if maskable
        else "Full-bleed SZL orbit mark for platform avatars. Every element stays inside the "
        "round crop."
    )
    body = f"<defs>{defs}</defs>" + f'<rect width="600" height="600" fill="{NAVY}"/>' + inner
    return _svg("0 0 600 600", "SZL Holdings", desc, body, key=key)


def _social(master: bytes) -> bytes:
    text = master.decode("utf-8")
    inner = text.split("<svg", 1)[1].split(">", 1)[1].rsplit("</svg>", 1)[0]
    inner = re.sub(r"<title[^>]*>[^<]*</title>|<desc[^>]*>[^<]*</desc>", "", inner)
    gx, gy = _on_orbit_large(-38)
    body = (
        f'<rect width="1200" height="630" fill="{GRAPHITE}"/>'
        f'<g fill="none" transform="rotate(-12 600 315)">'
        f'<ellipse cx="600" cy="315" rx="560" ry="196" stroke="{SILVER_500}" stroke-opacity="0.55" stroke-width="2"/>'
        f'<ellipse cx="600" cy="315" rx="430" ry="150" stroke="{SILVER_500}" stroke-opacity="0.3" stroke-width="1.5"/>'
        "</g>"
        f'<circle cx="{_fmt(gx)}" cy="{_fmt(gy)}" r="7" fill="{CORAL}"/>'
        f'<svg x="435" y="150" width="330" height="330" viewBox="0 0 600 600">{inner}</svg>'
    )
    return _svg(
        "0 0 1200 630",
        "SZL Holdings",
        "The SZL orbit mark centred on a graphite field crossed by two quiet silver orbits.",
        body,
        key="szl-social",
    )


def _on_orbit_large(degrees: float) -> tuple[float, float]:
    t, a = math.radians(degrees), math.radians(-12)
    x, y = 560 * math.cos(t), 196 * math.sin(t)
    return 600 + x * math.cos(a) - y * math.sin(a), 315 + x * math.sin(a) + y * math.cos(a)


def build_vectors(root: Path | None = None) -> dict[str, bytes]:
    """Return every suite vector, keyed by its path inside ``suite/``."""

    root = repo_root() if root is None else root
    master, tree = _master(root)
    return {
        "szl-orbit.svg": master,
        "szl-orbit-mono-navy.svg": _mono(tree, NAVY, "szl-orbit-mono-navy", "light"),
        "szl-orbit-mono-white.svg": _mono(tree, WHITE, "szl-orbit-mono-white", "dark"),
        "szl-orbit-holo.svg": _holo(master),
        "szl-icon-32.svg": _icon(tree, size=32),
        "szl-icon-16.svg": _icon(tree, size=16),
        "szl-avatar.svg": _avatar(tree, master, maskable=False),
        "szl-icon-maskable.svg": _avatar(tree, master, maskable=True),
        "szl-social-1200x630.svg": _social(master),
    }


def render(vectors: dict[str, bytes]) -> dict[str, bytes]:
    """Render the raster exports with resvg (``pip install resvg-py``) and Pillow for the ICO."""

    import resvg_py
    from PIL import Image

    rasters: dict[str, bytes] = {}
    for path, (source, width, height) in RASTERS.items():
        png = resvg_py.svg_to_bytes(
            svg_string=vectors[source].decode("utf-8"),
            width=width,
            height=height,
            skip_system_fonts=True,
        )
        rasters[path] = bytes(png)
    for path, sources in ICO.items():
        frames = [Image.open(io.BytesIO(rasters[source])).convert("RGBA") for source in sources]
        buffer = io.BytesIO()
        frames[-1].save(
            buffer, format="ICO", sizes=[frame.size for frame in frames], append_images=frames[:-1]
        )
        rasters[path] = buffer.getvalue()
    return rasters


def manifest(
    root: Path, vectors: dict[str, bytes], rasters: dict[str, bytes], renderer: str
) -> bytes:
    master_sha = hashlib.sha256(vectors["szl-orbit.svg"]).hexdigest()
    record = {
        "schema": "szl.logo-suite.v1",
        "version": SUITE_VERSION,
        "source_repository": "szl-holdings/szl-brand",
        "master": MASTER,
        "master_sha256": master_sha,
        "generator": "src/szl_brand/orbit_suite.py",
        "renderer": renderer,
        "deployment_status": "NOT_ATTESTED",
        "license": {"code": "Apache-2.0", "brand_assets": "CC BY 4.0"},
        "trademark": "The SZL Holdings name, mark and brand colors are trademarks of SZL Holdings "
        "and are not licensed by either license.",
        "files": {
            path: {
                "sha256": hashlib.sha256(data).hexdigest(),
                **(
                    {
                        "from": RASTERS[path][0],
                        "width": RASTERS[path][1],
                        "height": RASTERS[path][2],
                    }
                    if path in RASTERS
                    else {"from": list(ICO[path])}
                    if path in ICO
                    else {}
                ),
            }
            for path, data in {**vectors, **rasters}.items()
        },
    }
    return (json.dumps(record, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def write(root: Path | None = None) -> dict[str, bytes]:
    """Rebuild vectors and rasters in ``suite/`` and write ``suite/manifest.json``."""

    import resvg_py

    root = repo_root() if root is None else root
    vectors = build_vectors(root)
    rasters = render(vectors)
    renderer = f"resvg-py {getattr(resvg_py, '__version__', 'unknown')}; Pillow ICO"
    outputs = {**vectors, **rasters, "manifest.json": manifest(root, vectors, rasters, renderer)}
    suite = root / SUITE_DIR
    for path, data in outputs.items():
        destination = suite / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    return outputs


def check(root: Path | None = None) -> list[str]:
    """Rebuild the vectors and verify every file recorded in ``suite/manifest.json``."""

    root = repo_root() if root is None else root
    suite = root / SUITE_DIR
    errors: list[str] = []
    try:
        vectors = build_vectors(root)
    except (OSError, ValueError, KeyError) as exc:
        return [str(exc)]
    for path, data in vectors.items():
        if not (suite / path).is_file() or (suite / path).read_bytes() != data:
            errors.append(f"{SUITE_DIR}/{path} differs from the build; run `szl-brand orbit-suite`")
    record = json.loads((suite / "manifest.json").read_text(encoding="utf-8"))
    expected = set(vectors) | set(RASTERS) | set(ICO)
    if set(record["files"]) != expected:
        errors.append("suite/manifest.json does not list exactly the suite files")
    for path, entry in record["files"].items():
        file = suite / path
        if not file.is_file():
            errors.append(f"{SUITE_DIR}/{path} is missing")
        elif hashlib.sha256(file.read_bytes()).hexdigest() != entry["sha256"]:
            errors.append(f"{SUITE_DIR}/{path} does not match its manifest sha256")
    shipped = {p.relative_to(suite).as_posix() for p in suite.rglob("*") if p.is_file()}
    for stray in sorted(shipped - expected - {"manifest.json", "README.md"}):
        errors.append(f"{SUITE_DIR}/{stray} is not part of the suite")
    return errors
