"""Local native presentation only; no provider fetch, operational math or publisher."""

from __future__ import annotations

import base64
import hashlib
import html
import json
import os
import re
import stat
from datetime import datetime
from pathlib import Path

from szl_marketing import UNAVAILABLE, fact

ROOT = Path(__file__).resolve().parent
_BOUND = {
    "tokens": (
        "szl-tokens.css",
        "81f7c9baeef0b435e6e3f9d0c4e0d70e40fa17df5d1f30697f623cd3ef5f8eab",
    ),
    "icon": ("szl-icon-32.svg", "6e2b7d72a3af3d9602b79de41df0194ede6496a9661f057108ec224c0efc92e6"),
    "favicon": (
        "szl-icon-16.svg",
        "6e2dc7c9794dc452fbccb44ffadbd168c2584361904e8bcaeba542427d9e1a3a",
    ),
    "holo": (
        "szl-orbit-holo.svg",
        "66bbf937cb3cd257ec4ab5e7b016e4c09b5d6ea97f735453833a04c534a63b37",
    ),
    "source": ("SOURCE.json", "967a77235227f1d75852fb61873e46336e67403cbc0e7e12b141e31c83fbd93d"),
}


def _read_fd(fd: int, limit: int) -> bytes:
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
        raise ValueError("local presentation file is not a bounded regular file")
    chunks = []
    remaining = limit + 1
    while remaining:
        chunk = os.read(fd, min(remaining, 65536))
        if not chunk:
            break
        chunks.append(chunk)
        remaining -= len(chunk)
    data = b"".join(chunks)
    if len(data) > limit:
        raise ValueError("local presentation file exceeded its bound")
    return data


def _native(key: str) -> bytes:
    """Keys select literal source-owned files; no manifest controls a read path."""
    if key not in _BOUND:
        raise ValueError("unknown native asset")
    filename, expected = _BOUND[key]
    directory = os.open(ROOT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        native = os.open("native", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
        try:
            descriptor = os.open(filename, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=native)
            try:
                data = _read_fd(descriptor, 262144)
            finally:
                os.close(descriptor)
        finally:
            os.close(native)
    finally:
        os.close(directory)
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError("native asset differs from its accepted projection")
    return data


def _local(filename: str) -> bytes:
    if filename not in {"factory.css", "factory.js", "PUBLICATION_RECEIPT.json"}:
        raise ValueError("unknown presentation file")
    directory = os.open(ROOT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        descriptor = os.open(filename, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
        try:
            return _read_fd(descriptor, 262144)
        finally:
            os.close(descriptor)
    finally:
        os.close(directory)


def _svg(key: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(_native(key)).decode("ascii")


def native_css() -> str:
    _native("source")
    return _native("tokens").decode("utf-8") + "\n" + _local("factory.css").decode("utf-8")


def native_js() -> str:
    return _local("factory.js").decode("utf-8")


def native_head() -> str:
    return (
        '<meta name="description" content="Public estate observations, original drafts and SZL house-rule review.">'
        + f'<link rel="icon" type="image/svg+xml" href="{_svg("favicon")}">'
        + '<style id="factory-native-style">'
        + native_css()
        + "</style>"
    )


def _text(value: object) -> str:
    shown = (
        str(value)
        if isinstance(value, (str, int, float)) and not isinstance(value, bool)
        else UNAVAILABLE
    )
    if len(shown) > 1024:
        shown = shown[:1024] + "… [display shortened; exact value in raw JSON]"
    return html.escape(shown, quote=True)


def header() -> str:
    return f'''
<a class="mf-skip" href="#factory-workspace">Skip to the workspace</a>
<header class="mf-header">
  <a class="mf-brand" href="https://huggingface.co/spaces/SZLHOLDINGS/szl-command-lab">
    <img src="{_svg("icon")}" width="40" height="40" alt="SZL Holdings">
    <span>SZL <strong>Marketing</strong></span>
  </a>
  <nav aria-label="SZL ecosystem" class="mf-nav">
    <a href="https://a-11-oy.com">Product</a>
    <a href="https://a11oy.net">Proof registry</a>
    <button id="factory-theme-toggle" type="button" aria-label="Switch color theme">Theme</button>
  </nav>
</header>
<section class="mf-hero" aria-labelledby="factory-title">
  <div class="mf-hero-copy">
    <p class="mf-eyebrow">Governed fact factory</p>
    <h1 id="factory-title">Facts first.<br><span>Words with provenance.</span></h1>
    <p class="mf-lead">Turn public observations into clear, original drafts. Keep the source
      labels close, the house rules visible, and the final editorial decision yours.</p>
    <ol class="mf-steps" aria-label="The working sequence">
      <li><span>01</span> Observe</li><li><span>02</span> Compose</li><li><span>03</span> Review</li>
    </ol>
  </div>
  <aside class="mf-specimen" data-surface="dark" aria-label="Working discipline">
    <img src="{_svg("holo")}" width="600" height="600" alt="" aria-hidden="true" class="mf-orbit">
    <div class="mf-specimen-copy"><p class="mf-eyebrow">Working discipline</p>
      <h2>Every claim<br>keeps its label.</h2>
      <p>MEASURED records a source observation. UNAVAILABLE preserves a gap.</p>
      <p class="mf-specimen-note">Λ remains Conjecture 1, advisory.<br>Trust ceiling: 0.97, never 1.0.</p>
    </div>
  </aside>
</section>'''


def initial_observation() -> str:
    return """<section class="mf-empty" role="status"><span class="mf-status">NOT REQUESTED</span>
<h3>No observation yet</h3><p>Choose “Read public facts” to make an anonymous request.
Opening a tab does not collect a factbase.</p></section>"""


def _metric(facts: dict, name: str, path: str, section: str, numeric: bool = False) -> str:
    value = fact(facts, path)
    label = fact(facts, f"{section}.label")
    label = (
        label if isinstance(label, str) and label in {"MEASURED", "UNAVAILABLE"} else "UNAVAILABLE"
    )
    valid = (
        (isinstance(value, int) and not isinstance(value, bool) and value >= 0)
        if numeric
        else (isinstance(value, str) and bool(value.strip()) and value != UNAVAILABLE)
    )
    shown = f"{value:,}" if numeric and valid else value if valid else UNAVAILABLE
    state = "measured" if label == "MEASURED" and valid else "unavailable"
    status = f"SOURCE: {label}" if valid else f"VALUE UNAVAILABLE · SOURCE: {label}"
    return f'<div class="mf-metric" data-state="{state}"><dt>{name}</dt><dd>{_text(shown)}</dd><span class="mf-status">{status}</span></div>'


def observation(facts: dict) -> str:
    groups = [
        (
            "GitHub · public repositories",
            [
                ("Repositories", "github.repos", "github", True),
                ("Archived repositories", "github.archived", "github", True),
            ],
        ),
        (
            "Hugging Face · public catalog",
            [
                ("Models", "hf.models", "hf", True),
                ("Datasets", "hf.datasets", "hf", True),
                ("Spaces", "hf.spaces", "hf", True),
                ("Model + dataset downloads", "hf.downloads.total", "hf", True),
                ("Most-downloaded artifact · models + datasets", "hf.crown.id", "hf", False),
                ("Artifact downloads", "hf.crown.downloads", "hf", True),
            ],
        ),
        (
            "Product · reported honesty manifest",
            [
                ("Locked formulas", "product.locked_formula_count", "product", True),
                ("Λ label from the source", "product.lambda", "product", False),
            ],
        ),
        (
            "Public doors · response observation",
            [
                ("a-11-oy.com/verify", "surfaces.verify_cta", "surfaces", False),
                ("a11oy.net", "surfaces.proof_cta", "surfaces", False),
            ],
        ),
    ]
    stamp = fact(facts, "generated_at")
    try:
        parsed = datetime.fromisoformat(stamp) if isinstance(stamp, str) else None
        if parsed is None or parsed.tzinfo is None:
            stamp = UNAVAILABLE
    except ValueError:
        stamp = UNAVAILABLE
    parts = [
        f'<section class="mf-observation"><div class="mf-observation-heading" role="status"><h3>Current engine observation</h3><p>Engine timestamp: <span class="mf-mono">{_text(stamp)}</span></p></div>'
    ]
    for title, metrics in groups:
        parts.append(f'<section class="mf-fact-group"><h4>{title}</h4><dl class="mf-fact-grid">')
        parts.extend(_metric(facts, *metric) for metric in metrics)
        parts.append("</dl></section>")
    parts.append(
        '<p class="mf-boundary">Source labels belong to the engine. A missing field remains UNAVAILABLE even when its source responded. Download figures retain the source\'s reporting window; a responding door is not a readiness verdict. Inspect the JSON for the complete returned record.</p></section>'
    )
    return "".join(parts)


def provenance() -> str:
    try:
        receipt = json.loads(_local("PUBLICATION_RECEIPT.json"))
    except (OSError, UnicodeDecodeError, ValueError):
        receipt = {}
    if not isinstance(receipt, dict):
        receipt = {}
    source = receipt.get("source")
    source = source if isinstance(source, dict) else {}
    target = receipt.get("target")
    target = target if isinstance(target, dict) else {}
    valid = (
        receipt.get("schema") == "szl.marketing-space-publication/v1"
        and target.get("repository") == "SZLHOLDINGS/szl-marketing-1.1"
        and target.get("repo_type") == "space"
        and source.get("repository") == "szl-holdings/szl-brand"
        and source.get("directory") == "marketing/space/szl-marketing-1.1"
    )
    sha = source.get("sha") if valid else None
    sha = sha if isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{40}", sha) else UNAVAILABLE
    root = receipt.get("root_sha256") if valid else None
    root = root if isinstance(root, str) and re.fullmatch(r"[0-9a-f]{64}", root) else UNAVAILABLE
    state = receipt.get("state") if valid else None
    state = state if state == "PACKAGE_BUILT_NOT_PUBLISHED" else UNAVAILABLE
    link = (
        f'<a href="https://github.com/szl-holdings/szl-brand/commit/{sha}">Inspect the declared source commit</a>'
        if sha != UNAVAILABLE
        else "Declared source link: UNAVAILABLE"
    )
    return f"""<section class="mf-provenance"><p class="mf-eyebrow">Source &amp; package</p>
<h2>Trace the presentation to its source.</h2>
<p>The installed package record declares a GitHub revision and file hashes. This panel displays
that local metadata; it does not independently verify a signature, current deployment or runtime readiness.</p>
<dl class="mf-provenance-grid"><div><dt>Declared source revision</dt><dd class="mf-mono">{sha}</dd></div>
<div><dt>Declared package root SHA-256</dt><dd class="mf-mono">{root}</dd></div>
<div><dt>Recorded package-stage state</dt><dd class="mf-mono">{state}</dd></div></dl>
<p>{link}</p><p>The package-stage statement remains as built. Publication is a separate guarded workflow with its own readback.</p>
<div class="mf-source-note"><h3>The boundaries stay visible</h3>
<ul><li>The fact, compose and lint engine is vendored from the canonical source.</li>
<li>September 30 payload and factbase files are retained historical snapshots.</li>
<li>Draft outputs are plain source text; the house linter does not distribute them.</li>
<li>Orbit v2 artwork: © 2026 Lutar, Stephen P. · SZL Holdings · ORCID 0009-0001-0110-4173. The repository CC BY 4.0 license, trademark notice and file-specific notices continue to apply.</li></ul></div></section>"""


def footer() -> str:
    return """<footer class="mf-footer"><p>SZL Holdings · Governed marketing tools</p>
<nav aria-label="Factory sources"><a href="https://github.com/szl-holdings/szl-brand/tree/main/marketing/space/szl-marketing-1.1">Source</a>
<a href="https://github.com/szl-holdings/szl-brand/actions/workflows/hf-marketing-spaces.yml">Publication workflow</a>
<a href="https://github.com/szl-holdings/szl-brand/blob/main/NOTICE">Trademark notice</a></nav></footer>"""
