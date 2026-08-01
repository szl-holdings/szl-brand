"""Versioned, deterministic exports for the KANCHAY design system."""

from __future__ import annotations

import hashlib
import json
import re
from importlib import resources
from pathlib import Path
from typing import Final

from szl_brand import __version__

CONTRACT: Final = "szl.design-system/v1"
_REVISION_RE: Final = re.compile(r"^[0-9a-f]{40}$")
_SOURCE_REPOSITORY: Final = "https://github.com/szl-holdings/szl-brand"
_ASSETS: Final = (
    ("system.css", "kit/tokens/szl-design-system.css"),
    ("tokens.json", "kit/tokens/COLOR_TOKENS.json"),
    ("metadata.schema.json", "kit/contracts/public-metadata.schema.json"),
    ("vitepress.css", "kit/adapters/vitepress.css"),
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_asset(export_name: str, source_path: str) -> bytes:
    """Read from a source checkout, falling back to wheel package data."""

    checkout_path = _repo_root() / source_path
    if checkout_path.is_file():
        return checkout_path.read_bytes()

    packaged = resources.files("szl_brand").joinpath("design_system", export_name)
    if not packaged.is_file():
        raise FileNotFoundError(f"design-system asset unavailable: {export_name}")
    return packaged.read_bytes()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def export_system(output: Path, source_revision: str) -> Path:
    """Export an immutable design-system bundle and return its manifest path.

    The manifest deliberately omits timestamps. Identical inputs and the same pinned
    source revision therefore produce byte-identical output on every platform.
    """

    if not _REVISION_RE.fullmatch(source_revision):
        raise ValueError("source_revision must be an exact lowercase 40-character Git SHA")

    output.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, str | int]] = []
    root_material = bytearray()

    for export_name, source_path in _ASSETS:
        data = _read_asset(export_name, source_path)
        destination = output / export_name
        destination.write_bytes(data)
        digest = _sha256(data)
        records.append(
            {
                "path": export_name,
                "source_path": source_path,
                "sha256": digest,
                "bytes": len(data),
            }
        )
        root_material.extend(f"{export_name}\0{digest}\0".encode())

    manifest = {
        "$schema": "urn:szl:design-system-bundle:v1",
        "contract": CONTRACT,
        "name": "KANCHAY",
        "version": __version__,
        "source": {
            "repository": _SOURCE_REPOSITORY,
            "revision": source_revision,
        },
        "integrity": {
            "algorithm": "sha256",
            "root": _sha256(bytes(root_material)),
        },
        "assets": records,
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest_path


def verify_system(directory: Path) -> list[str]:
    """Return fail-closed integrity errors for an exported bundle."""

    manifest_path = directory / "manifest.json"
    if not manifest_path.is_file():
        return ["manifest.json is missing"]

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"manifest.json is unreadable: {exc}"]
    if not isinstance(manifest, dict):
        return ["manifest.json root must be an object"]

    errors: list[str] = []
    if manifest.get("contract") != CONTRACT:
        errors.append(f"unsupported contract: {manifest.get('contract')!r}")
    if manifest.get("version") != __version__:
        errors.append(f"version mismatch: {manifest.get('version')!r}")
    source = manifest.get("source")
    if not isinstance(source, dict):
        errors.append("source must be an object")
    else:
        if source.get("repository") != _SOURCE_REPOSITORY:
            errors.append(f"source repository mismatch: {source.get('repository')!r}")
        revision = source.get("revision")
        if not isinstance(revision, str) or not _REVISION_RE.fullmatch(revision):
            errors.append(f"source revision is not immutable: {revision!r}")
    integrity = manifest.get("integrity")
    if not isinstance(integrity, dict) or integrity.get("algorithm") != "sha256":
        errors.append("integrity algorithm must be sha256")

    records = manifest.get("assets")
    if not isinstance(records, list):
        return [*errors, "assets must be an array"]

    root_material = bytearray()
    seen: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            errors.append(f"asset record must be an object: {record!r}")
            continue
        name = record.get("path")
        if not isinstance(name, str) or Path(name).name != name:
            errors.append(f"unsafe asset path: {name!r}")
            continue
        if name in seen:
            errors.append(f"duplicate asset: {name}")
            continue
        seen.add(name)
        asset_path = directory / name
        if not asset_path.is_file():
            errors.append(f"missing asset: {name}")
            continue
        data = asset_path.read_bytes()
        digest = _sha256(data)
        if digest != record.get("sha256"):
            errors.append(f"hash mismatch: {name}")
        if len(data) != record.get("bytes"):
            errors.append(f"size mismatch: {name}")
        root_material.extend(f"{name}\0{digest}\0".encode())

    expected_assets = {name for name, _source_path in _ASSETS}
    if seen != expected_assets:
        errors.append(f"asset set mismatch: expected {sorted(expected_assets)}, got {sorted(seen)}")
    expected_root = integrity.get("root") if isinstance(integrity, dict) else None
    if _sha256(bytes(root_material)) != expected_root:
        errors.append("bundle root mismatch")
    return errors
