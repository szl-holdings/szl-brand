"""Live, labeled estate facts for SZL public copy.

Every number a marketing draft may print is fetched from a public API at generation time.
A source that cannot be fetched is recorded as ``UNAVAILABLE`` with the reason; nothing is
guessed, cached from memory, or typed by hand. Anonymous requests are used deliberately so
the counts are what a stranger sees (``visibility: PUBLIC``), never an authenticated view.

The crown artifact is swept across models *and* datasets. The models-only crown is kept as a
diagnostic so the 24x undercount found on 2026-09-30 can never hide again.
"""

from __future__ import annotations

import json
import re
import shutil
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

__all__ = [
    "GITHUB_ORG",
    "HF_AUTHOR",
    "MEASURED",
    "SCHEMA",
    "UNAVAILABLE",
    "Fetcher",
    "default_fetch",
    "fact",
    "factbase",
    "github_facts",
    "hf_facts",
    "product_facts",
    "surface_facts",
    "write_factbase",
]

SCHEMA: Final = "szl.marketing-factbase/v1"
GITHUB_ORG: Final = "szl-holdings"
HF_AUTHOR: Final = "SZLHOLDINGS"
MEASURED: Final = "MEASURED"
UNAVAILABLE: Final = "UNAVAILABLE"

PRODUCT_HONEST_URL: Final = "https://a-11-oy.com/api/a11oy/v1/honest"
SURFACE_PROBES: Final[dict[str, str]] = {
    "product_home": "https://a-11-oy.com/",
    "product_verify": "https://a-11-oy.com/verify",
    "proof_registry": "https://a11oy.net/",
}
_USER_AGENT: Final = "szl-brand-marketing/1.0 (+https://github.com/szl-holdings/szl-brand)"
_NEXT_LINK: Final = re.compile(r"<([^>]+)>\s*;\s*rel=\"next\"")

# (status, parsed JSON body or None, response headers)
Fetcher = Callable[[str], tuple[int, Any, dict[str, str]]]


def default_fetch(url: str, timeout: float = 30.0) -> tuple[int, Any, dict[str, str]]:
    """Anonymous GET. Network and HTTP failures become ``status 0`` / the HTTP code."""
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            raw = response.read()
            headers = {k.lower(): v for k, v in response.headers.items()}
            status = int(response.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code), None, {}
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return 0, None, {}
    body: Any = None
    if "json" in headers.get("content-type", ""):
        try:
            body = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            body = None
    return status, body, headers


def _paginate(fetch: Fetcher, url: str, limit: int = 50) -> list[dict[str, Any]] | None:
    """Follow ``Link: rel="next"`` headers. Any failed page fails the whole source."""
    rows: list[dict[str, Any]] = []
    next_url: str | None = url
    pages = 0
    while next_url and pages < limit:
        status, body, headers = fetch(next_url)
        if status != 200 or not isinstance(body, list):
            return None
        rows.extend(item for item in body if isinstance(item, dict))
        pages += 1
        match = _NEXT_LINK.search(headers.get("link", ""))
        next_url = match.group(1) if match else None
    return rows if next_url is None else None


def _unavailable(reason: str, **extra: Any) -> dict[str, Any]:
    return {"label": UNAVAILABLE, "reason": reason, **extra}


def github_facts(fetch: Fetcher = default_fetch) -> dict[str, Any]:
    """Public repository census of the GitHub organization (anonymous view)."""
    url = f"https://api.github.com/orgs/{GITHUB_ORG}/repos?per_page=100&type=public"
    repos = _paginate(fetch, url)
    if repos is None:
        return _unavailable("github repos endpoint unavailable or paginated incompletely")
    archived = sum(1 for repo in repos if repo.get("archived"))
    return {
        "label": MEASURED,
        "visibility": "PUBLIC",
        "org": GITHUB_ORG,
        "repos": len(repos),
        "archived": archived,
        "active": len(repos) - archived,
        "stars": sum(int(repo.get("stargazers_count") or 0) for repo in repos),
        "source": url,
    }


def _downloads(row: dict[str, Any]) -> int:
    value = row.get("downloads")
    return int(value) if isinstance(value, int | float) and value > 0 else 0


def hf_facts(fetch: Fetcher = default_fetch) -> dict[str, Any]:
    """Public Hugging Face census with a models+datasets crown sweep."""
    rows: dict[str, list[dict[str, Any]]] = {}
    for kind in ("models", "datasets", "spaces"):
        url = f"https://huggingface.co/api/{kind}?author={HF_AUTHOR}&limit=1000"
        page = _paginate(fetch, url)
        if page is None:
            return _unavailable(f"huggingface {kind} endpoint unavailable")
        rows[kind] = page
    swept = [("models", row) for row in rows["models"]] + [
        ("datasets", row) for row in rows["datasets"]
    ]
    facts: dict[str, Any] = {
        "label": MEASURED,
        "visibility": "PUBLIC",
        "author": HF_AUTHOR,
        "models": len(rows["models"]),
        "datasets": len(rows["datasets"]),
        "spaces": len(rows["spaces"]),
        "downloads": {
            "models": sum(_downloads(r) for r in rows["models"]),
            "datasets": sum(_downloads(r) for r in rows["datasets"]),
        },
    }
    facts["downloads"]["total"] = facts["downloads"]["models"] + facts["downloads"]["datasets"]
    if swept:
        kind, top = max(swept, key=lambda pair: _downloads(pair[1]))
        facts["crown"] = {
            "id": str(top.get("id", UNAVAILABLE)),
            "kind": kind,
            "downloads": _downloads(top),
            "sweep": "models+datasets",
        }
    else:
        facts["crown"] = _unavailable("no public models or datasets")
    if rows["models"]:
        top_model = max(rows["models"], key=_downloads)
        facts["models_only_crown_diagnostic"] = {
            "id": str(top_model.get("id", UNAVAILABLE)),
            "downloads": _downloads(top_model),
            "note": "diagnostic only; never print — the printable crown sweeps datasets too",
        }
    return facts


def product_facts(fetch: Fetcher = default_fetch) -> dict[str, Any]:
    """The product's own honesty manifest: locked formula count and the Λ label."""
    status, body, _ = fetch(PRODUCT_HONEST_URL)
    if status != 200 or not isinstance(body, dict):
        return _unavailable("product honesty manifest unavailable", source=PRODUCT_HONEST_URL)
    lock = body.get("doctrine_lock") if isinstance(body.get("doctrine_lock"), dict) else {}
    locked = body.get("locked_formula_count", lock.get("locked_formula_count"))
    return {
        "label": MEASURED,
        "source": PRODUCT_HONEST_URL,
        "locked_formula_count": int(locked) if isinstance(locked, int) else UNAVAILABLE,
        "locked_formula_ids": list(body.get("locked_formula_ids") or []),
        "doctrine": str(lock.get("doctrine", UNAVAILABLE)),
        "lambda": str(lock.get("lambda", UNAVAILABLE)),
        "git_sha": str(body.get("git_sha", UNAVAILABLE)),
    }


def surface_facts(fetch: Fetcher = default_fetch) -> dict[str, Any]:
    """Reachability of the public doors a draft may link. A dead CTA is never printed."""
    probes: dict[str, Any] = {}
    for name, url in SURFACE_PROBES.items():
        status, _, _ = fetch(url)
        probes[name] = {"url": url, "status": status, "label": MEASURED if status else UNAVAILABLE}
    verify_ok = probes["product_verify"]["status"] == 200
    proof_ok = probes["proof_registry"]["status"] == 200
    return {
        "label": MEASURED,
        "probes": probes,
        "verify_cta": "AVAILABLE" if verify_ok else UNAVAILABLE,
        "proof_cta": "AVAILABLE" if proof_ok else UNAVAILABLE,
    }


def factbase(
    fetch: Fetcher = default_fetch, now: Callable[[], datetime] | None = None
) -> dict[str, Any]:
    """Pull every source. Each section carries its own label so partial outages stay honest."""
    stamp = (now or (lambda: datetime.now(UTC)))()
    return {
        "schema": SCHEMA,
        "generated_at": stamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated": stamp.strftime("%Y-%m-%d"),
        "discipline": "live anonymous pull; UNAVAILABLE over guessed; never typed from memory",
        "github": github_facts(fetch),
        "hf": hf_facts(fetch),
        "product": product_facts(fetch),
        "surfaces": surface_facts(fetch),
    }


def fact(facts: dict[str, Any], dotted: str, default: Any = UNAVAILABLE) -> Any:
    """Dotted lookup that degrades to ``UNAVAILABLE`` instead of raising."""
    node: Any = facts
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    if isinstance(node, dict) and node.get("label") == UNAVAILABLE:
        return default
    return node


def write_factbase(facts: dict[str, Any], target: Path) -> Path:
    """Write deterministic JSON; keep a timestamped backup of any previous factbase."""
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        backup = target.with_name(f"{target.name}.bak.{int(time.time())}")
        shutil.copy2(target, backup)
    target.write_text(json.dumps(facts, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target
