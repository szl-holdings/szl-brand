"""Offline checks for the founder-requested matched SZL orbital logo."""

import hashlib
import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / "kit/logos/orbit-v2/szl-orbit.svg"
NS = {"s": "http://www.w3.org/2000/svg"}


def test_orbit_manifest_matches_exact_source_bytes():
    manifest = json.loads(ASSET.with_name("manifest.json").read_text(encoding="utf-8"))
    assert manifest["master"] == ASSET.relative_to(ROOT).as_posix()
    assert manifest["sha256"] == hashlib.sha256(ASSET.read_bytes()).hexdigest()
    assert manifest["deployment_status"] == "NOT_ATTESTED"


def test_orbit_is_accessible_self_contained_static_vector():
    raw = ASSET.read_text(encoding="utf-8")
    assert len(ASSET.read_bytes()) < 6000
    assert "<!DOCTYPE" not in raw and "<!ENTITY" not in raw
    root = ET.fromstring(raw)
    assert root.attrib["viewBox"] == "0 0 600 600"
    assert root.attrib["role"] == "img"
    ids = [node.attrib["id"] for node in root.iter() if "id" in node.attrib]
    assert len(ids) == len(set(ids))
    for ref in root.attrib["aria-labelledby"].split():
        element = root.find(f".//*[@id='{ref}']")
        assert element is not None and element.text and element.text.strip()
    allowed = {
        "svg",
        "title",
        "desc",
        "defs",
        "linearGradient",
        "stop",
        "rect",
        "g",
        "ellipse",
        "path",
        "circle",
    }
    for node in root.iter():
        assert node.tag.removeprefix("{http://www.w3.org/2000/svg}") in allowed
        for key, value in node.attrib.items():
            assert not key.lower().startswith("on")
            assert not key.lower().endswith("href")
            assert "javascript:" not in value.lower()
            if "url(" in value:
                match = re.fullmatch(r"url\(#([A-Za-z][\w-]*)\)", value)
                assert match and match[1] in ids


def test_matching_letters_and_preserved_house_identity():
    root = ET.parse(ASSET).getroot()
    letters = root.find(".//*[@id='matched-szl']")
    assert letters is not None
    assert letters.attrib["fill"] == "#FFFFFF"
    assert letters.attrib["data-cap-height"] == "156"
    assert letters.attrib["data-baseline"] == "376"
    assert [node.attrib["id"] for node in letters] == ["letter-S", "letter-Z", "letter-L"]
    assert all(node.tag == "{http://www.w3.org/2000/svg}path" for node in letters)
    assert all("transform" not in node.attrib for node in letters)
    assert root.find(".//*[@id='navy-tile']").attrib["fill"] == "#030F29"
    assert root.find(".//*[@id='lambda-detail']") is not None


def test_one_node_is_on_the_authored_orbit():
    root = ET.parse(ASSET).getroot()
    ring = root.find(".//*[@id='orbit-ring']")
    assert ring.attrib["transform"] == "rotate(-22 300 300)"
    nodes = root.findall("s:circle", NS)
    assert len(nodes) == 1
    node = nodes[0]
    assert node.attrib["fill"] == "#DF735F"
    dx, dy = float(node.attrib["cx"]) - 300, float(node.attrib["cy"]) - 300
    angle = math.radians(22)
    x = dx * math.cos(angle) - dy * math.sin(angle)
    y = dx * math.sin(angle) + dy * math.cos(angle)
    assert abs((x / 250) ** 2 + (y / 116) ** 2 - 1) < 0.00002
