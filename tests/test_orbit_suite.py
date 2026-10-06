# SPDX-License-Identifier: Apache-2.0
# (c) 2026 Lutar, Stephen P. - SZL Holdings - ORCID 0009-0001-0110-4173
"""Gates for kit/logos/orbit-v2/suite/, the placements derived from the approved Orbit v2 master."""

from __future__ import annotations

import io
import json
import math
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from PIL import Image

from szl_brand import orbit_suite
from szl_brand.palette import Color

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / orbit_suite.SUITE_DIR
MASTER = ROOT / orbit_suite.MASTER
SVG = "{http://www.w3.org/2000/svg}"
VECTORS = sorted(orbit_suite.build_vectors(ROOT))
ALLOWED_TAGS = {
    "svg",
    "title",
    "desc",
    "defs",
    "linearGradient",
    "radialGradient",
    "stop",
    "mask",
    "rect",
    "g",
    "ellipse",
    "path",
    "circle",
}


def _tree(name: str) -> ET.Element:
    return ET.fromstring((SUITE / name).read_text(encoding="utf-8"))


def _master_letters() -> list[str]:
    root = ET.fromstring(MASTER.read_text(encoding="utf-8"))
    return [
        node.attrib["d"] for node in root.iter() if node.attrib.get("id", "").startswith("letter-")
    ]


def _manifest() -> dict:
    return json.loads((SUITE / "manifest.json").read_text(encoding="utf-8"))


def test_committed_suite_matches_its_master_and_manifest():
    assert orbit_suite.check(ROOT) == []
    record = _manifest()
    assert (
        record["master_sha256"]
        == json.loads((ROOT / orbit_suite.MASTER_MANIFEST).read_text(encoding="utf-8"))["sha256"]
    )
    assert record["deployment_status"] == "NOT_ATTESTED"
    assert (SUITE / "szl-orbit.svg").read_bytes() == MASTER.read_bytes()


def test_check_reports_a_hand_edited_vector(tmp_path):
    mirror = tmp_path / "repo"
    for relative in (orbit_suite.MASTER, orbit_suite.MASTER_MANIFEST):
        (mirror / relative).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, mirror / relative)
    shutil.copytree(SUITE, mirror / orbit_suite.SUITE_DIR)
    icon = mirror / orbit_suite.SUITE_DIR / "szl-icon-16.svg"
    icon.write_bytes(icon.read_bytes().replace(b"#DF735F", b"#FF00FF"))
    errors = orbit_suite.check(mirror)
    assert any("szl-icon-16.svg differs" in error for error in errors)
    assert any("szl-icon-16.svg does not match its manifest sha256" in error for error in errors)


@pytest.mark.parametrize("name", VECTORS)
def test_every_vector_is_a_safe_accessible_static_image(name):
    raw = (SUITE / name).read_text(encoding="utf-8")
    assert "<!DOCTYPE" not in raw and "<!ENTITY" not in raw and "<text" not in raw
    root = ET.fromstring(raw)
    assert root.attrib["role"] == "img"
    ids = [node.attrib["id"] for node in root.iter() if "id" in node.attrib]
    assert len(ids) == len(set(ids))
    for ref in root.attrib["aria-labelledby"].split():
        assert root.find(f".//*[@id='{ref}']") is not None
    for node in root.iter():
        assert node.tag.removeprefix(SVG) in ALLOWED_TAGS, node.tag
        for key, value in node.attrib.items():
            assert not key.lower().startswith("on") and not key.lower().endswith("href")
            for target in re.findall(r"url\(#([\w-]+)\)", value):
                assert target in ids
            assert "url(" not in value or re.fullmatch(r"url\(#[\w-]+\)", value)


@pytest.mark.parametrize("name", VECTORS)
def test_every_vector_reuses_the_master_letter_outlines(name):
    raw = (SUITE / name).read_text(encoding="utf-8")
    for d in _master_letters():
        assert f'd="{d}"' in raw


def test_small_icons_drop_detail_that_cannot_render():
    icon16 = (SUITE / "szl-icon-16.svg").read_text(encoding="utf-8")
    icon32 = (SUITE / "szl-icon-32.svg").read_text(encoding="utf-8")
    lambda_d = (
        ET.fromstring(MASTER.read_text(encoding="utf-8"))
        .find(f".//{SVG}path[@id='lambda-detail']")
        .attrib["d"]
    )
    for icon in (icon16, icon32):
        assert lambda_d not in icon
        assert "Gradient" not in icon
        assert icon.count(orbit_suite.CORAL) == 1
    assert "<ellipse" not in icon16
    assert icon32.count("<ellipse") == 1


def test_avatars_are_full_bleed_and_keep_content_inside_the_round_crop():
    for name, limit in (("szl-avatar.svg", 300), ("szl-icon-maskable.svg", 240)):
        root = _tree(name)
        ground = root.find(f"{SVG}rect")
        assert ground.attrib == {"width": "600", "height": "600", "fill": orbit_suite.NAVY}
        scale = 0.82 if "maskable" in name else 1.0
        # Furthest drawn points from the centre: the orbit's outer edge and the node.
        orbit_edge = (250 + 9 / 2) * scale
        node = math.dist((484.263, 166.817), (300, 300)) * scale + 9 * scale
        letters = math.dist((92.4, 220.0), (299.8, 299.1)) * scale
        for radius in (orbit_edge, node, letters):
            assert radius < limit, (name, radius)
    for name in ("szl-avatar.svg", "szl-icon-maskable.svg"):
        assert 'id="lambda-detail"' not in (SUITE / name).read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("name", "color"),
    [
        ("szl-orbit-mono-navy.svg", orbit_suite.NAVY),
        ("szl-orbit-mono-white.svg", orbit_suite.WHITE),
    ],
)
def test_mono_variants_use_one_color_and_mask_the_orbit_around_the_letters(name, color):
    root = _tree(name)
    mask = root.find(f".//{SVG}mask")
    assert mask is not None
    painted = {
        value.upper()
        for node in root.iter()
        if node not in set(mask.iter())
        for key, value in node.attrib.items()
        if key in {"fill", "stroke"} and value.startswith("#")
    }
    assert painted == {color}
    assert root.find(f"{SVG}rect") is None


def test_holographic_variant_stays_inside_the_house_palette():
    raw = (SUITE / "szl-orbit-holo.svg").read_text(encoding="utf-8")
    allowed = {
        orbit_suite.NAVY,
        orbit_suite.WHITE,
        orbit_suite.CORAL,
        orbit_suite.SILVER_100,
        orbit_suite.SILVER_300,
        orbit_suite.SILVER_500,
    }
    assert {hex_.upper() for hex_ in re.findall(r"#[0-9A-Fa-f]{6}", raw)} <= allowed


@pytest.mark.parametrize(
    ("ground", "variant"),
    [
        ("#F5F3EE", orbit_suite.NAVY),
        ("#FFFFFF", orbit_suite.NAVY),
        ("#080B12", orbit_suite.WHITE),
        ("#111722", orbit_suite.WHITE),
    ],
)
def test_mono_variants_clear_three_to_one_on_their_grounds(ground, variant):
    assert Color.from_hex(variant).contrast_ratio(Color.from_hex(ground)) >= 3.0


def test_rasters_match_their_declared_sizes_and_transparency():
    record = _manifest()["files"]
    for path, (source, width, height) in orbit_suite.RASTERS.items():
        assert record[path]["from"] == source
        image = Image.open(SUITE / path)
        assert image.size == (width, height), path
        corner = image.convert("RGBA").getpixel((0, 0))[3]
        if source in {"szl-orbit.svg", "szl-orbit-holo.svg", "szl-icon-16.svg", "szl-icon-32.svg"}:
            assert corner == 0, f"{path} should keep the tile's transparent corners"
        elif source.startswith("szl-orbit-mono"):
            assert corner == 0
        else:
            assert corner == 255, f"{path} should be full-bleed"
    ico = Image.open(io.BytesIO((SUITE / "favicon.ico").read_bytes()))
    assert sorted(ico.info["sizes"]) == [(16, 16), (32, 32), (48, 48)]
