"""Hypothesis property tests for asset validation, the manifest serializer and drift checks.

The filesystem properties are adopted from the fix/fuzz-invariants-20261101 branch: each
example works in its own temporary directory, so cases share no files.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st
from PIL import Image

from szl_brand.validate import (
    AssetRecord,
    Manifest,
    check_drift,
    generate_manifest,
    validate_directory,
)

sizes = st.integers(min_value=0, max_value=2**53)
dimensions = st.none() | st.integers(min_value=0, max_value=65535)
records = st.builds(
    AssetRecord,
    path=st.text(max_size=80),
    sha256=st.from_regex(r"[0-9a-f]{64}", fullmatch=True),
    size_bytes=sizes,
    format=st.sampled_from(["png", "jpg", "jpeg", "svg", "webp", "gif", "pdf"]),
    width=dimensions,
    height=dimensions,
    validated=st.booleans(),
    errors=st.lists(st.text(max_size=60), max_size=3),
)
manifests = st.builds(
    Manifest,
    version=st.text(max_size=12),
    generated_at=st.text(max_size=40),
    generator=st.text(max_size=20),
    root_hash=st.from_regex(r"[0-9a-f]{64}", fullmatch=True) | st.just(""),
    assets=st.lists(records, max_size=5),
)


@given(manifests)
def test_manifest_json_round_trips_exactly(manifest):
    text = manifest.to_json()

    assert Manifest.from_json(text) == manifest
    assert Manifest.from_json(text).to_json() == text


@given(manifests)
def test_manifest_json_is_plain_json_with_every_asset_in_order(manifest):
    decoded = json.loads(manifest.to_json())

    assert [asset["path"] for asset in decoded["assets"]] == [a.path for a in manifest.assets]
    assert [asset["sha256"] for asset in decoded["assets"]] == [a.sha256 for a in manifest.assets]
    assert decoded["root_hash"] == manifest.root_hash


BYTE = st.integers(min_value=0, max_value=255)


@settings(max_examples=30, deadline=None)
@given(
    st.integers(min_value=1, max_value=32),
    st.integers(min_value=1, max_value=32),
    st.tuples(BYTE, BYTE, BYTE, BYTE),
)
def test_manifest_tracks_real_png_bytes_and_round_trips(width, height, rgba):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        asset = root / "asset.png"
        Image.new("RGBA", (width, height), rgba).save(asset)
        raw = asset.read_bytes()

        records = validate_directory(root)
        manifest = generate_manifest(root)
        repeat = generate_manifest(root)

    assert len(records) == 1
    record = records[0]
    assert record.validated and not record.errors
    assert (record.width, record.height) == (width, height)
    assert record.sha256 == hashlib.sha256(raw).hexdigest()
    assert record.size_bytes == len(raw)
    assert manifest.assets == records
    assert manifest.root_hash == hashlib.sha256(record.sha256.encode()).hexdigest()
    assert Manifest.from_json(manifest.to_json()) == manifest
    assert (repeat.assets, repeat.root_hash) == (manifest.assets, manifest.root_hash)


@settings(max_examples=30, deadline=None)
@given(st.binary(max_size=128))
def test_drift_distinguishes_add_remove_modify_and_ignores_untracked_suffixes(payload):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        asset = root / "original.svg"
        asset.write_bytes(b"<svg/>")
        manifest_file = root / "manifest.json"
        manifest_file.write_text(generate_manifest(root).to_json(), encoding="utf-8")
        assert check_drift(manifest_file, root) == []

        (root / "notes.txt").write_bytes(payload)
        assert check_drift(manifest_file, root) == []

        asset.write_bytes(b"<svg/>\n" + payload)
        assert check_drift(manifest_file, root) == [
            {
                "type": "modified",
                "path": str(asset),
                "expected": hashlib.sha256(b"<svg/>").hexdigest(),
                "actual": hashlib.sha256(asset.read_bytes()).hexdigest(),
            }
        ]

        asset.unlink()
        assert check_drift(manifest_file, root) == [{"type": "removed", "path": str(asset)}]

        added = root / "added.svg"
        added.write_bytes(b"<svg/>")
        drift = check_drift(manifest_file, root)

    assert sorted(drift, key=lambda entry: entry["type"]) == [
        {"type": "added", "path": str(added)},
        {"type": "removed", "path": str(asset)},
    ]
