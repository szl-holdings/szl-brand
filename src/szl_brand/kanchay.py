# SPDX-License-Identifier: Apache-2.0
# (c) 2026 Lutar, Stephen P. - SZL Holdings - ORCID 0009-0001-0110-4173
"""Build and verify ``kanchay/``, the ready-to-vendor bundle of the KANCHAY design system.

KANCHAY has one token system: the founder-approved ``kit/tokens/szl-design-system.css``
(v1.3.0) plus the additive operator layer ``kit/tokens/szl-console.css``. The bundle is a
byte-for-byte copy of those two files and the orbit logo suite from ``kit/logos``, with a
``SOURCE.json`` that records the sha256 of every copied file. Nothing in the bundle is
generated or edited; change the kit source and rebuild.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Final

VERSION: Final = "1.3.0"
EXPORT_DIR: Final = "kanchay"

# Bundle path -> kit source path. Order is the SOURCE.json manifest order.
BUNDLE: Final = {
    "szl-console.css": "kit/tokens/szl-console.css",
    "szl-design-system.css": "kit/tokens/szl-design-system.css",
    "logos/szl_favicon.svg": "kit/logos/szl_favicon.svg",
    "logos/szl_favicon_180.png": "kit/logos/png/szl_favicon_180.png",
    "logos/szl_favicon_32.png": "kit/logos/png/szl_favicon_32.png",
    "logos/szl_favicon_512.png": "kit/logos/png/szl_favicon_512.png",
    "logos/szl_favicon_square.svg": "kit/logos/szl_favicon_square.svg",
    "logos/szl_logo_horizontal.svg": "kit/logos/szl_logo_horizontal.svg",
    "logos/szl_logo_mono_navy.svg": "kit/logos/szl_logo_mono_navy.svg",
    "logos/szl_logo_mono_white.svg": "kit/logos/szl_logo_mono_white.svg",
    "logos/szl_logo_primary.svg": "kit/logos/szl_logo_primary.svg",
    "logos/szl_logo_transparent.svg": "kit/logos/szl_logo_transparent.svg",
}
# Derived payload: the custom properties of the design system only (no element or class rules),
# for surfaces that keep their own component CSS and need the tokens without the components.
TOKENS: Final = "szl-tokens.css"
TOKENS_SOURCE: Final = "kit/tokens/szl-design-system.css"
# Files in kanchay/ that are documentation or the manifest itself, not copied payload.
NON_PAYLOAD: Final = frozenset({"README.md", "SOURCE.json"})

_BASE: Final = (
    "szl-holdings/szl-brand kit/tokens/szl-design-system.css (KANCHAY v1.3.0, founder-approved)"
)
_LAYERS: Final = {"szl-console.css": "1.2.0 (operator console, additive)"}
_LICENSE: Final = {"code": "Apache-2.0", "brand_assets": "CC BY 4.0"}
_COMMIT_RE: Final = re.compile(r"^[0-9a-f]{40}$")
_CSS_DEFINITION_RE: Final = re.compile(r"--([A-Za-z0-9_-]+)\s*:")
# A reference with a fallback (``var(--heat, 8%)``) is a per-element input, not a token.
_CSS_REFERENCE_RE: Final = re.compile(r"var\(\s*--([A-Za-z0-9_-]+)\s*([,)])")


def repo_root() -> Path:
    """Return the checkout root when running from a source tree."""

    return Path(__file__).resolve().parents[2]


def render_source_json(payload: dict[str, bytes], source_commit: str) -> str:
    """Render ``SOURCE.json`` for the bundle bytes, in manifest order."""

    if not _COMMIT_RE.fullmatch(source_commit):
        raise ValueError("source_commit must be an exact lowercase 40-character Git SHA")
    source = {
        "name": "szl-kanchay",
        "version": VERSION,
        "base": _BASE,
        "layers": _LAYERS,
        "source_commit": source_commit,
        "license": _LICENSE,
        "sha256": {path: hashlib.sha256(data).hexdigest() for path, data in payload.items()},
    }
    return json.dumps(source, indent=2, ensure_ascii=False) + "\n"


_TOKEN_SELECTOR_RE: Final = re.compile(
    r'(?::root|\[data-surface="(?:dark|light)"\])'
    r'(?:\s*,\s*(?::root|\[data-surface="(?:dark|light)"\]))*'
)
_TOKEN_DECLARATION_RE: Final = re.compile(r"\s*(?:--[A-Za-z0-9_-]+|color-scheme)\s*:")


def _top_level_blocks(css: str) -> list[tuple[str, str]]:
    """Return ``(prelude, body)`` for every top-level rule, skipping comments and at-rules' insides."""

    blocks: list[tuple[str, str]] = []
    depth, start, prelude_start, i = 0, 0, 0, 0
    prelude = ""
    while i < len(css):
        if css.startswith("/*", i):
            end = css.find("*/", i + 2)
            if end < 0:
                raise ValueError("unterminated CSS comment")
            if depth == 0:
                prelude_start = end + 2
            i = end + 2
            continue
        char = css[i]
        if char == "{":
            if depth == 0:
                prelude, start = css[prelude_start:i].strip(), i + 1
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                raise ValueError("unbalanced CSS braces")
            if depth == 0:
                blocks.append((prelude, css[start:i]))
                prelude_start = i + 1
        i += 1
    if depth:
        raise ValueError("unbalanced CSS braces")
    return blocks


def extract_tokens(css: str) -> str:
    """Return the token blocks of the design system: custom properties on :root and surfaces."""

    kept = []
    for prelude, body in _top_level_blocks(css):
        if not _TOKEN_SELECTOR_RE.fullmatch(prelude):
            continue
        plain = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
        declarations = [part for part in plain.split(";") if part.strip()]
        if not all(_TOKEN_DECLARATION_RE.match(part) for part in declarations):
            raise ValueError(f"token block {prelude!r} carries a non-token declaration")
        kept.append(f"{prelude} {{{body}}}")
    header = "\n".join(
        (
            f"/* KANCHAY tokens v{VERSION} (derived): only the custom properties of",
            "   szl-design-system.css. Palette, both polarities (on :root and on any",
            "   [data-surface] element), type, spacing, radius, shadow, motion and z tokens.",
            "   No element or class rules. Built by `szl-brand kanchay-build`; never edit by",
            "   hand. Use it when a surface keeps its own component CSS.",
            "   Brand assets (c) 2026 SZL Holdings, CC BY 4.0; code Apache-2.0. */",
        )
    )
    return header + "\n" + "\n".join(kept) + "\n"


def recorded_source_commit(root: Path | None = None) -> str:
    """Return the ``source_commit`` recorded in the committed ``SOURCE.json``."""

    root = repo_root() if root is None else root
    source = json.loads((root / EXPORT_DIR / "SOURCE.json").read_bytes().decode("utf-8"))
    commit = source.get("source_commit") if isinstance(source, dict) else None
    if not isinstance(commit, str) or not _COMMIT_RE.fullmatch(commit):
        raise ValueError("kanchay/SOURCE.json source_commit is not an exact Git SHA")
    return commit


def build(root: Path | None = None, source_commit: str | None = None) -> dict[str, bytes]:
    """Return every bundle file, keyed by its path inside ``kanchay/``.

    ``source_commit`` is the szl-brand main commit the bundle is cut from; it defaults
    to the one already recorded in ``kanchay/SOURCE.json``.
    """

    root = repo_root() if root is None else root
    commit = recorded_source_commit(root) if source_commit is None else source_commit
    outputs = {path: (root / source).read_bytes() for path, source in BUNDLE.items()}
    outputs[TOKENS] = extract_tokens((root / TOKENS_SOURCE).read_bytes().decode("utf-8")).encode(
        "utf-8"
    )
    outputs["SOURCE.json"] = render_source_json(outputs, commit).encode("utf-8")
    return outputs


def write(root: Path | None = None, source_commit: str | None = None) -> dict[str, bytes]:
    """Rebuild the bundle in place, remove anything that is not part of it, and return it."""

    root = repo_root() if root is None else root
    outputs = build(root, source_commit)
    export_dir = root / EXPORT_DIR
    for path in _unexpected_files(export_dir, outputs):
        (export_dir / path).unlink()
    for path, data in outputs.items():
        destination = export_dir / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    return outputs


def _unexpected_files(export_dir: Path, outputs: dict[str, bytes]) -> list[str]:
    allowed = set(outputs) | NON_PAYLOAD
    shipped = (path.relative_to(export_dir).as_posix() for path in export_dir.rglob("*"))
    return sorted(path for path in shipped if (export_dir / path).is_file() and path not in allowed)


def css_reference_errors(root: Path | None = None) -> list[str]:
    """Return ``var(--x)`` references without a fallback that neither stylesheet defines."""

    root = repo_root() if root is None else root
    export_dir = root / EXPORT_DIR
    sheets = {
        name: (export_dir / name).read_bytes().decode("utf-8")
        for name in ("szl-design-system.css", "szl-console.css")
    }
    defined: set[str] = set()
    for css in sheets.values():
        defined |= set(_CSS_DEFINITION_RE.findall(css))
    errors = []
    for name, css in sheets.items():
        missing = {ref for ref, end in _CSS_REFERENCE_RE.findall(css) if end == ")"} - defined
        errors += [f"{name}: var(--{ref}) is not defined" for ref in sorted(missing)]
    return errors


def check(root: Path | None = None) -> list[str]:
    """Return fail-closed errors when ``kanchay/`` differs from the kit it bundles."""

    root = repo_root() if root is None else root
    export_dir = root / EXPORT_DIR
    try:
        outputs = build(root)
    except (OSError, ValueError) as exc:
        return [str(exc)]
    errors = []
    for path, data in outputs.items():
        destination = export_dir / path
        if not destination.is_file():
            errors.append(f"{EXPORT_DIR}/{path} is missing")
        elif destination.read_bytes() != data:
            source = BUNDLE.get(path, TOKENS_SOURCE if path == TOKENS else "its kit sources")
            errors.append(
                f"{EXPORT_DIR}/{path} differs from {source}; "
                "run `python -m szl_brand kanchay-build` and commit the result"
            )
    errors += [
        f"{EXPORT_DIR}/{path} is not part of the bundle"
        for path in _unexpected_files(export_dir, outputs)
    ]
    if not errors:
        errors += css_reference_errors(root)
    return errors
