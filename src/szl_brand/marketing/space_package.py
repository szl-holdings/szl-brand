"""Exact-projection packages for the two public marketing Spaces.

GitHub ``main`` is the source of truth. A package is built from a named source revision,
hashed file by file, linted, and recorded in ``PUBLICATION_RECEIPT.json`` as
``PACKAGE_BUILT_NOT_PUBLISHED``. Publication is a separate step that needs a credential
supplied by the environment, writes exactly the package (stale files are removed), reads the
Hub back, and records ``PUBLISHED_CONVERGED`` or fails closed. Secrets are never written to
a receipt.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

from .lint import lint, strip_html

__all__ = [
    "RECEIPT_NAME",
    "TARGETS",
    "build_package",
    "package_root_hash",
    "publish_package",
]

RECEIPT_NAME: Final = "PUBLICATION_RECEIPT.json"
RECEIPT_SCHEMA: Final = "szl.marketing-space-publication/v1"
_SHA_RE: Final = re.compile(r"^[0-9a-f]{40}$")
_MODULE_DIR: Final = Path(__file__).resolve().parent
_VENDOR_NAME: Final = "szl_marketing"
_VENDORED_FILES: Final = ("__init__.py", "facts.py", "lint.py", "compose.py", "plan.py")

TARGETS: Final[dict[str, dict[str, Any]]] = {
    "szl-marketing-1.1": {
        "repo_id": "SZLHOLDINGS/szl-marketing-1.1",
        "source_dir": "marketing/space/szl-marketing-1.1",
        "vendor_module": True,
        "extra_files": {},
        "lint_files": ("README.md",),
    },
    "szl-brand-campaign": {
        "repo_id": "SZLHOLDINGS/szl-brand-campaign",
        "source_dir": "marketing/space/szl-brand-campaign",
        "vendor_module": False,
        "extra_files": {"kanchay/szl-design-system.css": "szl-design-system.css"},
        "lint_files": ("README.md", "index.html"),
    },
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_root_hash(files: dict[str, str]) -> str:
    """Order-independent root hash over ``path:sha256`` lines."""
    lines = "\n".join(f"{path}:{files[path]}" for path in sorted(files))
    return hashlib.sha256(lines.encode("utf-8")).hexdigest()


def _copy_tree(source: Path, dest: Path) -> None:
    for path in sorted(source.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            target = dest / path.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def _space_metadata_violations(text: str) -> list[str]:
    """Check the Hub's short-description limit before attempting publication."""
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return ["Space README must start with YAML front matter"]
    try:
        end = lines.index("---", 1)
    except ValueError:
        return ["Space README front matter is not closed"]
    descriptions = [
        line.partition(":")[2].strip()
        for line in lines[1:end]
        if line.startswith("short_description:")
    ]
    if len(descriptions) != 1 or not descriptions[0]:
        return ["Space README needs one nonempty short_description"]
    if len(descriptions[0]) > 60:
        return ["Space short_description exceeds the Hugging Face 60-character limit"]
    return []


def build_package(target: str, repo_root: Path, source_sha: str, output: Path) -> dict[str, Any]:
    """Assemble ``output`` for ``target`` from ``repo_root`` and write the receipt."""
    if target not in TARGETS:
        raise ValueError(f"unknown target {target!r}; known: {sorted(TARGETS)}")
    if not _SHA_RE.match(source_sha):
        raise ValueError("source_sha must be a full 40-hex commit SHA")
    spec = TARGETS[target]
    source_dir = repo_root / spec["source_dir"]
    if not source_dir.is_dir():
        raise FileNotFoundError(f"source directory missing: {source_dir}")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    _copy_tree(source_dir, output)
    for src_rel, dest_rel in spec["extra_files"].items():
        src = repo_root / src_rel
        if not src.is_file():
            raise FileNotFoundError(f"extra file missing: {src}")
        (output / dest_rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, output / dest_rel)
    vendored: dict[str, str] = {}
    if spec["vendor_module"]:
        vendor_dir = output / _VENDOR_NAME
        vendor_dir.mkdir()
        for name in _VENDORED_FILES:
            shutil.copy2(_MODULE_DIR / name, vendor_dir / name)
            vendored[f"{_VENDOR_NAME}/{name}"] = _sha256(_MODULE_DIR / name)
    violations: dict[str, list[str]] = {}
    for rel in spec["lint_files"]:
        path = output / rel
        if not path.is_file():
            violations[rel] = ["required file missing"]
            continue
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() in {".html", ".htm"}:
            text = strip_html(text)
        found = lint(text)
        errors = [str(v) for v in found]
        if rel == "README.md":
            errors.extend(_space_metadata_violations(text))
        if errors:
            violations[rel] = errors
    if violations:
        shutil.rmtree(output)
        raise ValueError("package blocked by compliance linter: " + json.dumps(violations))
    files = {
        str(p.relative_to(output)).replace(os.sep, "/"): _sha256(p)
        for p in sorted(output.rglob("*"))
        if p.is_file()
    }
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "state": "PACKAGE_BUILT_NOT_PUBLISHED",
        "target": {"name": target, "repository": spec["repo_id"], "repo_type": "space"},
        "source": {
            "repository": "szl-holdings/szl-brand",
            "sha": source_sha,
            "directory": spec["source_dir"],
        },
        "vendored_module": vendored,
        "files": files,
        "root_sha256": package_root_hash(files),
        "lint": "CLEAN",
        "secrets_recorded": False,
        "built_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    (output / RECEIPT_NAME).write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return receipt


def _load_receipt(package: Path) -> dict[str, Any]:
    receipt_path = package / RECEIPT_NAME
    if not receipt_path.is_file():
        raise FileNotFoundError(f"{RECEIPT_NAME} missing in {package}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("schema") != RECEIPT_SCHEMA or receipt.get("state") != (
        "PACKAGE_BUILT_NOT_PUBLISHED"
    ):
        raise ValueError("package receipt is not a built, unpublished package")
    files = {
        str(p.relative_to(package)).replace(os.sep, "/"): _sha256(p)
        for p in sorted(package.rglob("*"))
        if p.is_file() and p.name != RECEIPT_NAME
    }
    if files != receipt.get("files"):
        raise ValueError("package bytes drifted from the receipt; rebuild before publishing")
    return receipt


def _oidc_error_diagnostic(exc: Exception) -> dict[str, Any]:
    """Return identifier-only exception metadata, never provider text or token data."""
    name = type(exc).__name__
    module = type(exc).__module__
    # Exception identifiers are defined by code, unlike messages and response
    # bodies. Keep only short Python identifiers and reject credential shapes.
    forbidden = ("hf_jwt_", "hf_oauth_", "sk_", "ghp_", "canary")
    kind = name if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,63}", name) else "OTHER_ERROR"
    source = module if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]{0,127}", module) else "OTHER_ERROR"
    if any(marker in kind.lower() for marker in forbidden):
        kind = "OTHER_ERROR"
    if any(marker in source.lower() for marker in forbidden):
        source = "OTHER_ERROR"
    response = getattr(exc, "response", None)
    status = getattr(response, "status_code", None)
    status = status if isinstance(status, int) and 100 <= status <= 599 else None
    oauth_error = None
    if response is not None:
        try:
            payload = response.json()
            code = payload.get("error") if isinstance(payload, dict) else None
            if code in {"invalid_grant", "invalid_request"}:
                oauth_error = code
        except Exception:  # noqa: BLE001 - provider body is untrusted and never recorded
            pass
    return {
        "failure_type": kind,
        "failure_module": source,
        "failure_http_status": status,
        "oauth_error": oauth_error,
    }


def _exchange_oidc_token(resource: str) -> tuple[str | None, dict[str, Any]]:
    """Exchange this GitHub job's OIDC identity without exposing token bytes."""
    if (
        os.environ.get("GITHUB_ACTIONS") != "true"
        or not os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL")
        or not os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN")
    ):
        return None, {"failure_type": "MISSING_GITHUB_IDENTITY"}
    if os.environ.get("HF_OIDC_RESOURCE") != resource:
        return None, {"failure_type": "OIDC_RESOURCE_MISMATCH"}
    try:
        from huggingface_hub import get_token

        token = get_token()
    except Exception as exc:  # noqa: BLE001 - fail closed and record only allow-listed structure
        return None, _oidc_error_diagnostic(exc)
    # A repo Trusted Publisher receives hf_jwt_, never a human PAT. Reject any
    # ambient-token fallback even if a future Hub client changes its precedence.
    if not token or not token.startswith("hf_jwt_") or any(char.isspace() for char in token):
        return None, {"failure_type": "INVALID_OIDC_TOKEN_SHAPE"}
    return token, {}


def publish_package(package: Path, report: Path, token: str | None = None) -> dict[str, Any]:
    """Publish exactly one package and prove Hub convergence. Fails closed without a token."""
    receipt = _load_receipt(package)
    repo_id = receipt["target"]["repository"]
    out: dict[str, Any] = {
        "schema": RECEIPT_SCHEMA,
        "target": receipt["target"],
        "source": receipt["source"],
        "root_sha256": receipt["root_sha256"],
        "secrets_recorded": False,
        "attempted_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    oidc_selected = "HF_OIDC_RESOURCE" in os.environ
    oidc_resource = os.environ.get("HF_OIDC_RESOURCE", "")
    explicit_token = bool(token)
    if oidc_selected:
        out["auth_mode"] = "HF_OIDC"
        if explicit_token or oidc_resource != f"spaces/{repo_id}":
            out.update(
                state="UNAVAILABLE",
                reason="OIDC_RESOURCE_MISMATCH: no Hub write attempted",
                failure_phase="oidc_exchange",
                hub_write_state="NOT_ATTEMPTED",
            )
            _write(report, out)
            return out
        token, diagnostic = _exchange_oidc_token(oidc_resource)
        if not token:
            out.update(
                state="UNAVAILABLE",
                reason="OIDC_EXCHANGE_UNAVAILABLE: no Hub write attempted",
                failure_phase="oidc_exchange",
                hub_write_state="NOT_ATTEMPTED",
                oidc_diagnostic=diagnostic,
            )
            _write(report, out)
            return out
    else:
        token = token or os.environ.get("HF_TOKEN")
    if not token:
        out.update(state="UNAVAILABLE", reason="NO_TOKEN: HF_TOKEN not supplied; nothing written")
        _write(report, out)
        return out
    try:
        from huggingface_hub import HfApi
    except ImportError:  # pragma: no cover - exercised only without the optional dependency
        out.update(state="UNAVAILABLE", reason="huggingface_hub not installed; nothing written")
        _write(report, out)
        return out
    phase = "client_initialization"
    hub_write_state = "NOT_ATTEMPTED"
    try:
        api = HfApi(token=token)
        if oidc_selected:
            phase = "target_write_authorization"
            api.auth_check(repo_id, repo_type="space", write=True)
            out["publisher"] = "HF_OIDC"
        else:
            phase = "token_identity"
            identity = api.whoami()
            out["publisher"] = str(identity.get("name", "UNAVAILABLE"))
        phase = "pre_upload_file_inventory"
        existing = set(api.list_repo_files(repo_id, repo_type="space"))
        wanted = set(receipt["files"]) | {RECEIPT_NAME}
        stale = sorted(f for f in existing - wanted if f != ".gitattributes")
        phase = "upload_folder"
        # A failed upload call may have written to the Hub before returning an error.
        hub_write_state = "UNKNOWN"
        commit = api.upload_folder(
            repo_id=repo_id,
            repo_type="space",
            folder_path=str(package),
            commit_message=f"exact projection of szl-brand@{receipt['source']['sha'][:12]}",
            delete_patterns=stale or None,
        )
        hub_write_state = "COMMIT_RETURNED"
        out["commit_url"] = str(getattr(commit, "commit_url", commit))
        out["removed_stale_files"] = stale
        phase = "post_upload_file_inventory"
        remote = set(api.list_repo_files(repo_id, repo_type="space"))
        missing = sorted(wanted - remote)
        extra = sorted(f for f in remote - wanted if f != ".gitattributes")
        phase = "receipt_readback"
        remote_receipt = api.hf_hub_download(
            repo_id, RECEIPT_NAME, repo_type="space", force_download=True
        )
        remote_root = json.loads(Path(remote_receipt).read_text(encoding="utf-8")).get(
            "root_sha256"
        )
        converged = not missing and not extra and remote_root == receipt["root_sha256"]
        out.update(
            state="PUBLISHED_CONVERGED" if converged else "PUBLISHED_DIVERGED",
            hub_write_state=hub_write_state,
            readback={"missing": missing, "extra": extra, "remote_root_sha256": remote_root},
        )
        try:
            runtime = api.get_space_runtime(repo_id)
            out["runtime_stage"] = str(getattr(runtime, "stage", "UNAVAILABLE"))
        except Exception as exc:  # noqa: BLE001 - runtime stage is informational
            out["runtime_stage"] = f"UNAVAILABLE: {type(exc).__name__}"
    except Exception as exc:  # noqa: BLE001 - every provider failure must land in the receipt
        # Provider exception strings can contain response bodies, headers, or credentials.
        # Record only bounded, structural diagnostics in the public Actions artifact.
        status = getattr(getattr(exc, "response", None), "status_code", None)
        status = status if isinstance(status, int) and 100 <= status <= 599 else None
        error_type = type(exc).__name__[:120]
        out.update(
            state="FAILED",
            failure_phase=phase,
            failure_type=error_type,
            failure_http_status=status,
            hub_write_state=hub_write_state,
            reason=(
                f"{error_type} HTTP {status} at {phase}"
                if status is not None
                else f"{error_type} at {phase}"
            )[:400],
        )
        if phase == "token_identity":
            # Only fixed labels and booleans enter the public receipt. Never
            # record token bytes, length, a fingerprint, or provider content.
            if oidc_selected:
                out["credential_diagnostic"] = {"selected_binding": "HF_OIDC"}
            else:
                binding = os.environ.get("HF_TOKEN_SOURCE", "")
                if explicit_token:
                    binding = "EXPLICIT_ARGUMENT"
                elif binding not in {"HF_ORG_TOKEN", "HF_TOKEN"}:
                    binding = "UNDECLARED"
                out["credential_diagnostic"] = {
                    "selected_binding": binding,
                    "starts_with_hf_prefix": token.startswith("hf_"),
                    "contains_whitespace": any(char.isspace() for char in token),
                    "contains_non_ascii": not token.isascii(),
                }
    _write(report, out)
    return out


def _write(report: Path, payload: dict[str, Any]) -> None:
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
