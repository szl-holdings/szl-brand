<!-- SPDX-License-Identifier: Apache-2.0
(c) 2026 Lutar, Stephen P. - SZL Holdings - ORCID 0009-0001-0110-4173 -->

# KANCHAY web export 1.0.0

This folder is the vendorable KANCHAY export that SZL web surfaces copy into their own
repositories: every token as a CSS custom property, the component classes, the React bundle,
local fonts, the SZL mark and an integrity manifest. `szl-holdings/szl-brand` at `kanchay/` is its
canonical home.

| File | What it is |
|---|---|
| `kanchay.css` | Every token as a custom property (dark on `:root`, light under `[data-theme="light"]`), `@font-face` for Space Grotesk, Inter and JetBrains Mono from `./fonts/`, the `.kc-type-*` text styles and the reduced-motion rule. |
| `kanchay-components.css` | Component classes: `kc-btn`, `kc-badge`, `kc-stat`, `kc-fcard`, `kc-input`, `kc-select`, `kc-sidebar`, `kc-site-header`, `kc-eyebrow`, `kc-output`, `kc-drawer` and the rest. Load after `kanchay.css`. |
| `kanchay-components.js`, `.d.ts` | The React bundle. Reads `window.React` (React 18), assigns `window.Kanchay`. React surfaces only. |
| `tokens.json` | The token source of truth. |
| `fonts/` | Latin-subset WOFF2 files, with `OFL.txt` (Inter, JetBrains Mono, Space Grotesk) and `LICENSE-Syncopate.txt` (Syncopate, Apache-2.0). |
| `marks/` | `szl-mark.svg`, `szl-mark-gold.svg`, `szl-mark-ink.svg`. |
| `SOURCE.json` | Version and the sha256 of every payload file above. |

## Vendor it

1. **Copy this folder** into the directory your surface serves static files from, keeping the
   name `kanchay/` (for example `assets/kanchay/` or `static/kanchay/`). If two surfaces in one
   repository serve from different roots, vendor once per root. To trim, keep `kanchay.css`,
   `SOURCE.json` and the three `fonts/` files it loads plus `OFL.txt`; add
   `kanchay-components.css` if you use any `kc-` class, `marks/` if you show the mark, and the
   `.js`/`.d.ts` pair only on a React surface.
2. **Link `kanchay.css` first**, then the components, then your own stylesheet. Fonts resolve
   relative to `kanchay.css`, so keep the folder layout. Remove every Google Fonts or CDN font link.

   ```html
   <link rel="stylesheet" href="/assets/kanchay/kanchay.css">
   <link rel="stylesheet" href="/assets/kanchay/kanchay-components.css">
   <link rel="stylesheet" href="/assets/app.css">
   ```

3. **Never edit vendored files.** Override in your own stylesheet with `var(--…)` tokens. To
   upgrade, copy the folder again from a newer revision of this repository. Keep Git from
   rewriting line endings (for example `assets/kanchay/** -text` in `.gitattributes`), then check
   the copy against the manifest; files you did not vendor are skipped:

   ```bash
   cd assets/kanchay && python -c "import hashlib,json,pathlib;m=json.load(open('SOURCE.json'))['sha256'];bad=[p for p,h in m.items() if pathlib.Path(p).exists() and hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()!=h];print('modified: '+', '.join(bad) if bad else 'ok')"
   ```

4. **Dark is the default.** Tokens resolve to the dark theme on `:root`. A document-like tool
   may set `<html data-theme="light">` (or `data-theme="light"` on a subtree) for the same roles
   with light values. There is no third theme.

Syncopate (`fonts/Syncopate-400.woff2`, `fonts/Syncopate-700.woff2`) ships in `fonts/`, but
`kanchay.css` 1.0.0 does not declare it; a surface that uses it adds its own `@font-face` and
vendors `fonts/LICENSE-Syncopate.txt` with it.

## Token roles in short

- **Ground and depth.** `--color-a11oy-bg` is the page; recess with `--color-a11oy-deep`, raise
  with `--color-a11oy-surface`, and use `--color-a11oy-overlay` for hover and pressed fills.
- **Text.** `--color-a11oy-text` for primary copy and numbers, `--color-a11oy-text-sub` for
  paragraphs, `--color-a11oy-text-ghost` for metadata (14px or larger on surface). Never `--dim`
  or `--color-gray-500` for text on dark.
- **Gold is the only accent.** `--color-a11oy-gold` marks the primary action, eyebrows, active
  navigation and card titles. One gold fill per view; its label is `--color-on-accent` and its
  hover `--gold-bright`.
- **Teal is proof.** `--color-focus` for focus rings, `--color-ink-signal` for verified hashes and
  proof links, `--teal-line` for proof hairlines.
- **Danger and status.** `--color-error` fills; `--color-ink-danger` and `--color-ink-caution`
  are the text colors. Marks use `--color-success`, `--color-warning`, `--color-error` and
  `--color-info`. Status is never color alone: pair it with a word.
- **Edges.** `--color-a11oy-border-subtle` for cards, `--color-a11oy-border` between regions,
  `--color-control-border` for every input and select.
- **Type.** `--font-display` (Space Grotesk) for headlines, `--font-sans` (Inter) for what people
  read and operate, `--font-mono` (JetBrains Mono) for labels, receipts, hashes and code. The
  `.kc-type-*` classes carry the scale.
- **Shape, depth and motion.** A 4px `--space-*` scale; `--radius-sm` for controls, `--radius-md`
  for cards, `--radius-lg` for dialogs, `--radius-full` for pills. Hairline borders
  (`--border-hairline`), shadows only on floating things (`--shadow-lg`, `--shadow-xl`),
  `--duration-*` and `--ease-*` for motion.
- **Focus and targets.** `outline: var(--border-focus) solid var(--color-focus); outline-offset: 2px`
  on `:focus-visible`; tappable things at least `--szl-touch-target` (44px).

Measured with the WCAG 2 contrast formula on the token values in this version (dark / light):
`--color-a11oy-text` on `--color-a11oy-bg` 17.79 / 17.07; `--color-a11oy-text-ghost` on
`--color-a11oy-surface` 4.27 / 6.48 (hence the 14px floor on dark); `--color-on-accent` on
`--color-a11oy-gold` 10.04 / 5.71; `--color-focus` on `--color-a11oy-surface` 5.67 / 5.75;
`--color-ink-danger` on `--color-a11oy-bg` 6.39 / 6.73.

## Maintain it

Edit `tokens.json` or the component source `kit/kanchay/components.css`, then regenerate and commit:

```bash
python -m szl_brand kanchay-build          # rewrites kanchay.css, kanchay-components.css, SOURCE.json
python -m szl_brand kanchay-build --check  # fails if the committed export drifted
```

`tests/test_kanchay.py` runs the same check in CI and fails when a generated file or a
`SOURCE.json` hash drifts, or when a token reference in `tokens.json` does not resolve.
`kanchay-components.js`, `.d.ts`, the fonts and the marks are committed as built and hashed, not
rebuilt here. Change `VERSION` in `src/szl_brand/kanchay.py` whenever the payload changes.
`README.md` and the license notices in `fonts/` are documentation, not payload, and are not hashed.

## Licenses

`SOURCE.json` declares Apache-2.0 for the code, and the two stylesheets carry
`SPDX-License-Identifier: Apache-2.0` headers. The fonts keep their own licenses (see `fonts/`).
The SZL mark is a trademark of SZL Holdings and no code or font license grants it; see the
repository [`NOTICE`](../NOTICE).
