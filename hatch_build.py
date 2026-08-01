"""Fail-closed source provenance for built KANCHAY artifacts."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Final

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

_CONTRACT: Final = "szl.design-system-build/v1"
_REPOSITORY: Final = "https://github.com/szl-holdings/szl-brand"
_REVISION_RE: Final = re.compile(r"^[0-9a-f]{40}$")
_ASSETS: Final = {
    "system.css": "kit/tokens/szl-design-system.css",
    "tokens.json": "kit/tokens/COLOR_TOKENS.json",
    "metadata.schema.json": "kit/contracts/public-metadata.schema.json",
    "vitepress.css": "kit/adapters/vitepress.css",
}
_SOURCE_PROVENANCE = "src/szl_brand/design_system/source-provenance.json"
_WHEEL_PROVENANCE = "szl_brand/design_system/source-provenance.json"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _run_git(root: Path, *arguments: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *arguments],
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError("Git source provenance is unavailable") from exc
    return result.stdout


def _require_canonical_repository(root: Path) -> None:
    remote = _run_git(root, "remote", "get-url", "origin").decode("utf-8").strip().rstrip("/")
    normalized = remote.removesuffix(".git")
    accepted = {
        _REPOSITORY,
        "git@github.com:szl-holdings/szl-brand",
        "ssh://git@github.com/szl-holdings/szl-brand",
    }
    if normalized not in accepted:
        raise RuntimeError(f"source repository is not canonical: {remote!r}")


def _from_git(root: Path) -> tuple[dict[str, object], dict[str, bytes]]:
    _require_canonical_repository(root)
    if _run_git(root, "status", "--porcelain=v1", "--untracked-files=all").strip():
        raise RuntimeError("source checkout is not clean; provenance build refused")
    revision = _run_git(root, "rev-parse", "--verify", "HEAD").decode("ascii").strip()
    if not _REVISION_RE.fullmatch(revision):
        raise RuntimeError("Git did not resolve an exact source revision")

    asset_bytes: dict[str, bytes] = {}
    asset_hashes: dict[str, str] = {}
    for export_name, source_path in _ASSETS.items():
        committed_data = _run_git(root, "show", f"{revision}:{source_path}")
        asset_bytes[export_name] = committed_data
        asset_hashes[export_name] = _sha256(committed_data)

    return (
        {
            "contract": _CONTRACT,
            "repository": _REPOSITORY,
            "revision": revision,
            "assets": asset_hashes,
        },
        asset_bytes,
    )


def _from_source_archive(root: Path) -> tuple[dict[str, object], dict[str, bytes]]:
    path = root / _SOURCE_PROVENANCE
    try:
        provenance = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("source archive provenance is unavailable or invalid") from exc
    if not isinstance(provenance, dict):
        raise RuntimeError("source archive provenance root must be an object")
    if provenance.get("contract") != _CONTRACT:
        raise RuntimeError("source archive provenance contract is unsupported")
    if provenance.get("repository") != _REPOSITORY:
        raise RuntimeError("source archive repository is not canonical")
    revision = provenance.get("revision")
    if not isinstance(revision, str) or not _REVISION_RE.fullmatch(revision):
        raise RuntimeError("source archive revision is not immutable")
    assets = provenance.get("assets")
    if not isinstance(assets, dict) or set(assets) != set(_ASSETS):
        raise RuntimeError("source archive provenance asset set is invalid")
    asset_bytes: dict[str, bytes] = {}
    for export_name, source_path in _ASSETS.items():
        try:
            data = (root / source_path).read_bytes()
        except OSError as exc:
            raise RuntimeError(f"source archive asset is unreadable: {source_path}") from exc
        if assets.get(export_name) != _sha256(data):
            raise RuntimeError(f"source archive asset provenance mismatch: {source_path}")
        asset_bytes[export_name] = data
    return provenance, asset_bytes


class CustomBuildHook(BuildHookInterface):
    """Embed exact revision and asset hashes without modifying the source tree."""

    def initialize(self, version: str, build_data: dict[str, object]) -> None:
        root = Path(self.root)
        provenance, assets = (
            _from_git(root) if (root / ".git").exists() else _from_source_archive(root)
        )

        force_include = build_data.setdefault("force_include", {})
        if not isinstance(force_include, dict):
            raise RuntimeError("build target force_include data is invalid")
        self._stages: list[Path] = []

        payload = (json.dumps(provenance, indent=2, sort_keys=True) + "\n").encode("utf-8")
        provenance_destination = (
            _SOURCE_PROVENANCE if self.target_name == "sdist" else _WHEEL_PROVENANCE
        )
        force_include[str(self._stage_bytes(payload, ".json"))] = provenance_destination

        for export_name, data in assets.items():
            destination = (
                _ASSETS[export_name]
                if self.target_name == "sdist"
                else f"szl_brand/design_system/{export_name}"
            )
            force_include[str(self._stage_bytes(data, Path(export_name).suffix))] = destination

    def finalize(self, version: str, build_data: dict[str, object], artifact_path: str) -> None:
        self._cleanup()

    def clean(self, versions: list[str]) -> None:
        self._cleanup()

    def _stage_bytes(self, data: bytes, suffix: str) -> Path:
        descriptor, stage_name = tempfile.mkstemp(prefix="szl-brand-build-", suffix=suffix)
        stage = Path(stage_name)
        self._stages.append(stage)
        with open(descriptor, "wb", closefd=True) as handle:
            handle.write(data)
            handle.flush()
        return stage

    def _cleanup(self) -> None:
        for stage in getattr(self, "_stages", []):
            stage.unlink(missing_ok=True)
