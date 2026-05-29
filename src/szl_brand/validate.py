"""Asset validation and cryptographic manifest system.

Provides:
- SHA-256 integrity manifests for all brand assets
- Format validation (PNG dimensions, file size bounds)
- Inventory reporting with rich table output
- Drift detection between manifest and filesystem
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from PIL import Image


@dataclass
class AssetRecord:
    """A single asset's manifest entry."""

    path: str
    sha256: str
    size_bytes: int
    format: str
    width: int | None = None
    height: int | None = None
    validated: bool = True
    errors: list[str] = field(default_factory=list)


@dataclass
class Manifest:
    """Cryptographic manifest for brand asset integrity."""

    version: str = "1.0.0"
    generated_at: str = ""
    generator: str = "szl-brand"
    root_hash: str = ""
    assets: list[AssetRecord] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, data: str) -> Manifest:
        d = json.loads(data)
        assets = [AssetRecord(**a) for a in d.get("assets", [])]
        return cls(
            version=d.get("version", "1.0.0"),
            generated_at=d.get("generated_at", ""),
            generator=d.get("generator", "szl-brand"),
            root_hash=d.get("root_hash", ""),
            assets=assets,
        )


VALID_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif", ".pdf"}
SOCIAL_PREVIEW_SIZE = (1280, 640)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def _validate_image(path: Path) -> AssetRecord:
    """Validate a single image asset."""
    errors = []
    sha = _sha256(path)
    size = path.stat().st_size
    ext = path.suffix.lower()

    width, height = None, None

    if ext in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        try:
            with Image.open(path) as img:
                width, height = img.size
                if "social-preview" in str(path) and (width, height) != SOCIAL_PREVIEW_SIZE:
                    errors.append(
                        f"Expected {SOCIAL_PREVIEW_SIZE[0]}x{SOCIAL_PREVIEW_SIZE[1]}, "
                        f"got {width}x{height}"
                    )
        except Exception as e:
            errors.append(f"Failed to open image: {e}")

    if size == 0:
        errors.append("Empty file")

    if size > 5_000_000:
        errors.append(f"File exceeds 5MB limit ({size} bytes)")

    return AssetRecord(
        path=str(path),
        sha256=sha,
        size_bytes=size,
        format=ext.lstrip("."),
        width=width,
        height=height,
        validated=len(errors) == 0,
        errors=errors,
    )


def validate_directory(directory: Path) -> list[AssetRecord]:
    """Validate all brand assets in a directory tree."""
    records = []
    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.suffix.lower() in VALID_EXTENSIONS:
            records.append(_validate_image(path))
    return records


def generate_manifest(directory: Path) -> Manifest:
    """Generate a cryptographic manifest for all assets."""
    records = validate_directory(directory)

    all_hashes = "".join(r.sha256 for r in records)
    root_hash = hashlib.sha256(all_hashes.encode()).hexdigest()

    return Manifest(
        version="1.0.0",
        generated_at=datetime.now(UTC).isoformat(),
        generator="szl-brand",
        root_hash=root_hash,
        assets=records,
    )


def check_drift(manifest_path: Path, directory: Path) -> list[dict]:
    """Compare manifest against current filesystem state.

    Returns a list of drift entries (additions, removals, modifications).
    """
    if not manifest_path.exists():
        return [{"type": "error", "message": "Manifest not found"}]

    manifest = Manifest.from_json(manifest_path.read_text())
    current = {
        str(p): _sha256(p)
        for p in directory.rglob("*")
        if p.is_file() and p.suffix.lower() in VALID_EXTENSIONS
    }

    manifest_paths = {r.path: r.sha256 for r in manifest.assets}
    drifts = []

    for path, sha in current.items():
        if path not in manifest_paths:
            drifts.append({"type": "added", "path": path})
        elif manifest_paths[path] != sha:
            drifts.append(
                {"type": "modified", "path": path, "expected": manifest_paths[path], "actual": sha}
            )

    for path in manifest_paths:
        if path not in current:
            drifts.append({"type": "removed", "path": path})

    return drifts
