"""Versioned, deterministic exports for the KANCHAY design system."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
from importlib import resources
from pathlib import Path
from typing import Final

from szl_brand import __version__

CONTRACT: Final = "szl.design-system/v1"
_REVISION_RE: Final = re.compile(r"^[0-9a-f]{40}$")
_SOURCE_REPOSITORY: Final = "https://github.com/szl-holdings/szl-brand"
_SOURCE_PROVENANCE_CONTRACT: Final = "szl.design-system-build/v1"
_ASSETS: Final = (
    ("system.css", "kit/tokens/szl-design-system.css"),
    ("tokens.json", "kit/tokens/COLOR_TOKENS.json"),
    ("metadata.schema.json", "kit/contracts/public-metadata.schema.json"),
    ("vitepress.css", "kit/adapters/vitepress.css"),
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _git(root: Path, *arguments: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *arguments],
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError("source checkout provenance is unavailable") from exc
    return result.stdout


def _require_canonical_repository(root: Path) -> None:
    remote = _git(root, "remote", "get-url", "origin").decode("utf-8").strip().rstrip("/")
    normalized = remote.removesuffix(".git")
    accepted = {
        _SOURCE_REPOSITORY,
        "git@github.com:szl-holdings/szl-brand",
        "ssh://git@github.com/szl-holdings/szl-brand",
    }
    if normalized not in accepted:
        raise ValueError(f"source repository is not canonical: {remote!r}")


def _checkout_source(root: Path) -> tuple[dict[str, bytes], str]:
    _require_canonical_repository(root)
    revision = _git(root, "rev-parse", "--verify", "HEAD").decode("ascii").strip()
    if not _REVISION_RE.fullmatch(revision):
        raise ValueError("source checkout did not resolve to an exact Git revision")

    assets: dict[str, bytes] = {}
    for export_name, source_path in _ASSETS:
        assets[export_name] = _git(root, "show", f"{revision}:{source_path}")
    return assets, revision


def _packaged_source() -> tuple[dict[str, bytes], str]:
    package_root = resources.files("szl_brand").joinpath("design_system")
    provenance_path = package_root.joinpath("source-provenance.json")
    try:
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("wheel source provenance is unavailable or invalid") from exc
    if not isinstance(provenance, dict):
        raise ValueError("wheel source provenance root must be an object")
    if provenance.get("contract") != _SOURCE_PROVENANCE_CONTRACT:
        raise ValueError("wheel source provenance contract is unsupported")
    if provenance.get("repository") != _SOURCE_REPOSITORY:
        raise ValueError("wheel source repository is not canonical")
    revision = provenance.get("revision")
    if not isinstance(revision, str) or not _REVISION_RE.fullmatch(revision):
        raise ValueError("wheel source revision is not immutable")
    recorded_assets = provenance.get("assets")
    expected_assets = {name for name, _source_path in _ASSETS}
    if not isinstance(recorded_assets, dict) or set(recorded_assets) != expected_assets:
        raise ValueError("wheel source provenance asset set is invalid")

    assets: dict[str, bytes] = {}
    for export_name in sorted(expected_assets):
        packaged = package_root.joinpath(export_name)
        try:
            data = packaged.read_bytes()
        except OSError as exc:
            raise ValueError(f"packaged design-system asset is unreadable: {export_name}") from exc
        if recorded_assets.get(export_name) != _sha256(data):
            raise ValueError(f"packaged design-system asset provenance mismatch: {export_name}")
        assets[export_name] = data
    return assets, revision


def _source_bundle() -> tuple[dict[str, bytes], str]:
    """Load assets bound to an exact checkout or wheel build revision."""

    root = _repo_root()
    checkout_paths = [root / source_path for _name, source_path in _ASSETS]
    present = [path.is_file() for path in checkout_paths]
    if all(present):
        return _checkout_source(root)
    if any(present):
        raise ValueError("source checkout is incomplete; wheel fallback refused")
    return _packaged_source()


def _atomic_write(destination: Path, data: bytes) -> None:
    """Publish completed bytes without following or writing through the final path."""

    descriptor, stage_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    stage = Path(stage_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(stage, destination)
    finally:
        stage.unlink(missing_ok=True)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def export_system(output: Path, source_revision: str) -> Path:
    """Export an immutable design-system bundle and return its manifest path.

    The manifest deliberately omits timestamps. Identical inputs and the same pinned
    source revision therefore produce byte-identical output on every platform.
    """

    if not _REVISION_RE.fullmatch(source_revision):
        raise ValueError("source_revision must be an exact lowercase 40-character Git SHA")

    assets, bound_revision = _source_bundle()
    if source_revision != bound_revision:
        raise ValueError(
            f"source_revision does not match exported source: expected {bound_revision}"
        )

    if output.is_symlink():
        raise ValueError("output directory symlink is forbidden")
    output.mkdir(parents=True, exist_ok=True)
    if not output.is_dir() or output.is_symlink():
        raise ValueError("output must be a real directory")

    final_paths = [output / name for name, _source_path in _ASSETS]
    final_paths.append(output / "manifest.json")
    for destination in final_paths:
        if destination.is_symlink():
            raise ValueError(f"output symlink is forbidden: {destination.name}")

    records: list[dict[str, str | int]] = []
    root_material = bytearray()

    for export_name, source_path in _ASSETS:
        data = assets[export_name]
        destination = output / export_name
        _atomic_write(destination, data)
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
    _atomic_write(
        manifest_path,
        (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    return manifest_path


def verify_system(directory: Path) -> list[str]:
    """Return fail-closed integrity errors for an exported bundle."""

    manifest_path = directory / "manifest.json"
    if manifest_path.is_symlink():
        return ["manifest.json symlink is forbidden"]
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

    expected_assets = {name for name, _source_path in _ASSETS}
    expected_entries = {*expected_assets, "manifest.json"}
    try:
        actual_entries = {entry.name for entry in directory.iterdir()}
    except OSError as exc:
        return [*errors, f"bundle directory is unreadable: {exc}"]
    for unexpected in sorted(actual_entries - expected_entries):
        errors.append(f"unexpected bundle entry: {unexpected}")

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
        if asset_path.is_symlink():
            errors.append(f"symlink asset is forbidden: {name}")
            continue
        try:
            data = asset_path.read_bytes()
        except OSError:
            errors.append(f"asset is unreadable: {name}")
            continue
        digest = _sha256(data)
        if digest != record.get("sha256"):
            errors.append(f"hash mismatch: {name}")
        if len(data) != record.get("bytes"):
            errors.append(f"size mismatch: {name}")
        root_material.extend(f"{name}\0{digest}\0".encode())

    if seen != expected_assets:
        errors.append(f"asset set mismatch: expected {sorted(expected_assets)}, got {sorted(seen)}")
    expected_root = integrity.get("root") if isinstance(integrity, dict) else None
    if _sha256(bytes(root_material)) != expected_root:
        errors.append("bundle root mismatch")
    return errors
