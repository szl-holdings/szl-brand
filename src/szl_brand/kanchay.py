# SPDX-License-Identifier: Apache-2.0
# (c) 2026 Lutar, Stephen P. - SZL Holdings - ORCID 0009-0001-0110-4173
"""Build and verify the vendorable KANCHAY web export in ``kanchay/``.

Inputs (edited by hand):

* ``kanchay/tokens.json`` -- the token source of truth, also shipped as-is.
* ``kit/kanchay/components.css`` -- the component stylesheet source.

Outputs (regenerated, never hand-edited):

* ``kanchay/kanchay.css`` -- every token as a CSS custom property, the local
  ``@font-face`` rules, the ``.kc-type-*`` text styles and the reduced-motion rule.
* ``kanchay/kanchay-components.css`` -- the component source under the export header.
* ``kanchay/SOURCE.json`` -- the sha256 of every payload file.

``kanchay-components.js``/``.d.ts``, the fonts and the marks are committed payload; they
are hashed into ``SOURCE.json`` but not rebuilt here. Identical inputs produce
byte-identical outputs on every platform.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Final

VERSION: Final = "1.0.0"
EXPORT_DIR: Final = "kanchay"
COMPONENTS_SOURCE: Final = "kit/kanchay/components.css"
GENERATED: Final = ("kanchay.css", "kanchay-components.css", "SOURCE.json")

# Payload files hashed into SOURCE.json, in manifest order: these top-level files, then
# fonts/*.woff2, then marks/*.svg, each sorted by name. Docs and licence notices are not
# payload and are not hashed.
_TOP_LEVEL: Final = (
    "kanchay-components.css",
    "kanchay-components.d.ts",
    "kanchay-components.js",
    "kanchay.css",
    "tokens.json",
)
_PAYLOAD_GLOBS: Final = (("fonts", "*.woff2"), ("marks", "*.svg"))

_HEADER: Final = """/* SZL Kanchay {what} v{ver}
   SPDX-License-Identifier: Apache-2.0
   (c) 2026 Lutar, Stephen P. - SZL Holdings - ORCID 0009-0001-0110-4173
   Generated from the SZL Kanchay design system (tokens.json v1). Do not hand-edit:
   change tokens.json in szl-holdings/szl-brand and regenerate. */
"""
_LATIN: Final = (
    "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, "
    "U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD"
)
_FONT_FACES: Final = (
    ("Space Grotesk", "SpaceGrotesk-latin.woff2", "300 700"),
    ("Inter", "Inter-latin.woff2", "400 600"),
    ("JetBrains Mono", "JetBrainsMono-latin.woff2", "400 700"),
)
_SCALAR_FAMILIES: Final = (
    "spacing",
    "radius",
    "shadow",
    "borderWidth",
    "zIndex",
    "duration",
    "easing",
    "layout",
)
_UPPERCASE_STYLES: Final = frozenset({"eyebrow", "label-mono", "nav-section", "chip"})
_REDUCED_MOTION: Final = (
    "@media (prefers-reduced-motion: reduce) {\n"
    "  *, *::before, *::after { animation-duration: .01ms !important;"
    " transition-duration: .01ms !important; }\n"
    "}"
)
_SOURCE_JSON_META: Final = {
    "name": "szl-kanchay",
    "canonical": "szl-holdings/szl-brand (kanchay/)",
    "license": {
        "code": "Apache-2.0",
        "fonts": "SIL Open Font License 1.1 (Inter, JetBrains Mono, Space Grotesk)",
    },
}
_ALIAS_RE: Final = re.compile(r"^\{([^{}]+)\}$")
_CSS_DEFINITION_RE: Final = re.compile(r"--([A-Za-z0-9_-]+)\s*:")
_CSS_REFERENCE_RE: Final = re.compile(r"var\(\s*--([A-Za-z0-9_-]+)")


def repo_root() -> Path:
    """Return the checkout root when running from a source tree."""

    return Path(__file__).resolve().parents[2]


def _css_value(value: Any) -> Any:
    if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
        return f"var(--{value[1:-1]})"
    return value


def _theme_value(token: dict[str, Any], theme: str, default_theme: str) -> Any:
    value = token["value"]
    if isinstance(value, dict):
        return value.get(theme, value.get(default_theme))
    return value


def render_tokens_css(tokens: dict[str, Any]) -> str:
    """Render ``kanchay.css`` from a parsed ``tokens.json``."""

    themes = [theme["id"] for theme in tokens["color"]["themes"]]
    default_theme = themes[0]
    color_tokens = tokens["color"]["tokens"]

    lines = [_HEADER.format(what="tokens", ver=VERSION)]
    for family, filename, weight in _FONT_FACES:
        lines.append(
            f"@font-face {{ font-family: '{family}'; font-style: normal; font-weight: {weight};"
            " font-display: swap;\n"
            f"  src: url('./fonts/{filename}') format('woff2'); unicode-range: {_LATIN}; }}"
        )
    lines.append("")

    root = [":root {", f"  color-scheme: {default_theme};"]
    for token in color_tokens:
        root.append(
            f"  --{token['name']}: {_css_value(_theme_value(token, default_theme, default_theme))};"
        )
    for family in _SCALAR_FAMILIES:
        for token in tokens[family]["tokens"]:
            root.append(
                f"  --{token['name']}: "
                f"{_css_value(_theme_value(token, default_theme, default_theme))};"
            )
    for key, stack in tokens["type"]["families"].items():
        root.append(f"  --font-{key}: {stack};")
    root.append("}")
    lines += root
    lines.append("")

    for theme in themes[1:]:
        block = [
            f':root[data-theme="{theme}"], [data-theme="{theme}"] {{',
            f"  color-scheme: {theme};",
        ]
        for token in color_tokens:
            if isinstance(token["value"], dict):
                default_value = _theme_value(token, default_theme, default_theme)
                themed_value = _theme_value(token, theme, default_theme)
                if default_value != themed_value:
                    block.append(f"  --{token['name']}: {_css_value(themed_value)};")
        # Plain aliases must re-resolve inside the themed scope.
        for token in color_tokens:
            value = token["value"]
            if isinstance(value, str) and value.startswith("{"):
                block.append(f"  --{token['name']}: {_css_value(value)};")
        block.append("}")
        lines += block
        lines.append("")

    for group in tokens["type"]["groups"]:
        for style in group["styles"]:
            family = style.get("family", group["family"])
            declarations = [
                f"font-family: var(--font-{family})",
                f"font-size: {style['fontSize']}",
                f"font-weight: {style['fontWeight']}",
            ]
            if "lineHeight" in style:
                declarations.append(f"line-height: {style['lineHeight']}")
            if "letterSpacing" in style:
                declarations.append(f"letter-spacing: {style['letterSpacing']}")
            if style["name"] in _UPPERCASE_STYLES:
                declarations.append("text-transform: uppercase")
            if style["name"] == "stat-value":
                declarations.append("font-variant-numeric: tabular-nums")
            lines.append(f".kc-type-{style['name']} {{ {'; '.join(declarations)}; }}")
    lines.append("")
    lines.append(_REDUCED_MOTION)
    return "\n".join(lines) + "\n"


def render_components_css(source: str) -> str:
    """Render ``kanchay-components.css`` from the component stylesheet source.

    The source opens with its own SPDX comment; the build swaps that comment for the
    versioned export header and keeps every other byte.
    """

    if "\r" in source:
        raise ValueError(f"{COMPONENTS_SOURCE} must use LF line endings")
    if not source.startswith("/* SPDX-License-Identifier:"):
        raise ValueError(f"{COMPONENTS_SOURCE} must open with its SPDX comment")
    end = source.find("*/\n")
    if end < 0:
        raise ValueError(f"{COMPONENTS_SOURCE} SPDX comment is not terminated")
    return _HEADER.format(what="components", ver=VERSION) + source[end + len("*/\n") :]


def payload_paths(export_dir: Path) -> list[str]:
    """Return the payload paths hashed into ``SOURCE.json``, in manifest order."""

    paths = list(_TOP_LEVEL)
    for directory, pattern in _PAYLOAD_GLOBS:
        names = sorted(path.name for path in (export_dir / directory).glob(pattern))
        paths += [f"{directory}/{name}" for name in names]
    return paths


def render_source_json(payload: dict[str, bytes]) -> str:
    """Render ``SOURCE.json`` for payload bytes given in manifest order."""

    manifest = {path: hashlib.sha256(data).hexdigest() for path, data in payload.items()}
    source = {
        "name": _SOURCE_JSON_META["name"],
        "version": VERSION,
        "canonical": _SOURCE_JSON_META["canonical"],
        "license": _SOURCE_JSON_META["license"],
        "sha256": manifest,
    }
    return json.dumps(source, indent=2)


def load_tokens(root: Path) -> dict[str, Any]:
    return json.loads((root / EXPORT_DIR / "tokens.json").read_bytes().decode("utf-8"))


def build(root: Path | None = None) -> dict[str, bytes]:
    """Return the generated export files, keyed by path inside ``kanchay/``."""

    root = repo_root() if root is None else root
    export_dir = root / EXPORT_DIR
    tokens_css = render_tokens_css(load_tokens(root)).encode("utf-8")
    components_source = (root / COMPONENTS_SOURCE).read_bytes().decode("utf-8")
    components_css = render_components_css(components_source).encode("utf-8")

    generated = {"kanchay.css": tokens_css, "kanchay-components.css": components_css}
    payload = {
        path: generated[path] if path in generated else (export_dir / path).read_bytes()
        for path in payload_paths(export_dir)
    }
    generated["SOURCE.json"] = render_source_json(payload).encode("utf-8")
    return generated


def write(root: Path | None = None) -> dict[str, bytes]:
    """Regenerate the export in place and return what was written."""

    root = repo_root() if root is None else root
    outputs = build(root)
    for name, data in outputs.items():
        (root / EXPORT_DIR / name).write_bytes(data)
    return outputs


def alias_errors(tokens: dict[str, Any]) -> list[str]:
    """Return every token reference in ``tokens.json`` that does not resolve.

    A reference is a whole-value ``{token-name}``. It must name a defined token, resolve in
    every theme to a literal without a cycle, and themed values may only use declared
    themes. Type styles must name a declared font family.
    """

    errors: list[str] = []
    themes = [theme["id"] for theme in tokens["color"]["themes"]]
    default_theme = themes[0]
    table: dict[str, Any] = {}
    for family in ("color", *_SCALAR_FAMILIES):
        for token in tokens[family]["tokens"]:
            name = token["name"]
            if name in table:
                errors.append(f"{name}: defined more than once")
            table[name] = token["value"]

    def value_in(name: str, theme: str) -> Any:
        value = table[name]
        if isinstance(value, dict):
            return value.get(theme, value.get(default_theme))
        return value

    for name, raw in table.items():
        if isinstance(raw, dict):
            unknown = sorted(set(raw) - set(themes))
            if unknown:
                errors.append(f"{name}: unknown theme(s) {', '.join(unknown)}")
            if default_theme not in raw:
                errors.append(f"{name}: no value for the default theme {default_theme!r}")
        for theme in themes:
            chain = [name]
            value = value_in(name, theme)
            while isinstance(value, str) and "{" in value:
                match = _ALIAS_RE.fullmatch(value)
                if match is None:
                    errors.append(f"{name} ({theme}): malformed reference {value!r}")
                    break
                target = match.group(1)
                if target not in table:
                    errors.append(f"{name} ({theme}): {{{target}}} is not a defined token")
                    break
                if target in chain:
                    errors.append(
                        f"{name} ({theme}): reference cycle {' -> '.join([*chain, target])}"
                    )
                    break
                chain.append(target)
                value = value_in(target, theme)
            if value is None:
                errors.append(f"{name} ({theme}): resolves to no value")

    families = tokens["type"]["families"]
    for group in tokens["type"]["groups"]:
        for style in group["styles"]:
            family = style.get("family", group["family"])
            if family not in families:
                errors.append(f"type style {style['name']}: font family {family!r} is not defined")
    return errors


def css_reference_errors(root: Path | None = None) -> list[str]:
    """Return ``var(--x)`` references in the export CSS that no custom property defines."""

    root = repo_root() if root is None else root
    export_dir = root / EXPORT_DIR
    tokens_css = (export_dir / "kanchay.css").read_bytes().decode("utf-8")
    components_css = (export_dir / "kanchay-components.css").read_bytes().decode("utf-8")
    defined = set(_CSS_DEFINITION_RE.findall(tokens_css))
    defined |= set(_CSS_DEFINITION_RE.findall(components_css))
    errors = []
    for filename, css in (("kanchay.css", tokens_css), ("kanchay-components.css", components_css)):
        for name in sorted(set(_CSS_REFERENCE_RE.findall(css)) - defined):
            errors.append(f"{filename}: var(--{name}) is not defined")
    return errors


def check(root: Path | None = None) -> list[str]:
    """Return fail-closed errors when the committed export drifts from its sources."""

    root = repo_root() if root is None else root
    export_dir = root / EXPORT_DIR
    errors = [f"tokens.json: {error}" for error in alias_errors(load_tokens(root))]
    for name, data in build(root).items():
        path = export_dir / name
        if not path.is_file():
            errors.append(f"{EXPORT_DIR}/{name} is missing")
        elif path.read_bytes() != data:
            errors.append(
                f"{EXPORT_DIR}/{name} drifted from its sources; "
                "run `python -m szl_brand kanchay-build` and commit the result"
            )
    if not errors:
        errors += css_reference_errors(root)
    return errors
