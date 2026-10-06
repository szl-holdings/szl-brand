<!-- SPDX-License-Identifier: Apache-2.0
(c) 2026 Lutar, Stephen P. - SZL Holdings - ORCID 0009-0001-0110-4173 -->

# KANCHAY vendor bundle 1.2.0

This folder is the ready-to-vendor bundle of KANCHAY v1.2.0, the founder-approved SZL Holdings
design system. The source of truth is `kit/`. Every file here is a byte-for-byte copy of a kit file,
pinned by sha256 in `SOURCE.json`. Nothing in this folder is generated or edited.

| File | What it is | Kit source |
|---|---|---|
| `szl-design-system.css` | KANCHAY v1.2.0: tokens, both surfaces, base, type scale and components. | `kit/tokens/szl-design-system.css` |
| `szl-console.css` | Operator console layer 1.1.0, additive, on the same tokens. | `kit/tokens/szl-console.css` |
| `logos/` | The orbit mark suite: horizontal, primary, transparent, mono white and navy, favicons. | `kit/logos/`, `kit/logos/png/` |
| `SOURCE.json` | Version, base, layers, `source_commit`, licenses and the sha256 of every file above. | built |

## Vendor it

1. **Copy into one folder named `szl/`** where the surface serves static files, for example
   `assets/szl/`. Copy `szl-design-system.css`, `SOURCE.json`, `szl-console.css` only if the surface
   uses its classes, and only the logo files you use, under `szl/logos/`. Copy byte for byte. Never
   edit a vendored file; override in your own stylesheet with tokens.
2. **Stop Git from rewriting the bytes.** Add `assets/szl/** -text` to the surface's
   `.gitattributes`.
3. **Link it before the surface's own stylesheet**, the design system first:

   ```html
   <link rel="stylesheet" href="/assets/szl/szl-design-system.css">
   <link rel="stylesheet" href="/assets/szl/szl-console.css"> <!-- operator surfaces only -->
   <link rel="stylesheet" href="/assets/app.css">
   ```

4. **Remove every webfont.** Delete Google Fonts and other CDN font links, and any `@font-face`
   for Inter, Space Grotesk, IBM Plex or Syncopate. Also remove files from the withdrawn `kanchay/`
   1.0.0 export: its stylesheets, component bundle and WOFF2 files. The system uses the device's own
   font stacks through `--font-body`, `--font-display` and `--font-mono`.
5. **Check the copy against the manifest.** Files you did not vendor are skipped:

   ```bash
   cd assets/szl && python -c "import hashlib,json,pathlib;m=json.load(open('SOURCE.json'))['sha256'];bad=[p for p,h in m.items() if pathlib.Path(p).exists() and hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()!=h];print('modified: '+', '.join(bad) if bad else 'ok')"
   ```

### Upgrading from 1.1.1

1.2.0 lets a surface be declared on any element (see "Nested surfaces" below). No color value
changes. Replace `szl-design-system.css`, `szl-console.css` and `SOURCE.json` in `szl/`; every logo
file is byte-identical to 1.1.1. If your own stylesheet keys rules on the page polarity, such as
`[data-surface="light"] .thing { color:… }`, move the value into a token declared on both
polarities, because a descendant rule like that also reaches into a nested dark panel.

### Upgrading from 1.1.0

1.1.1 changes only the focus ring (see "Focus" below). Replace `szl-design-system.css` and
`SOURCE.json` in `szl/`. `szl-console.css` and every logo file are byte-identical to 1.1.0, so
their hashes do not change.

## Two surfaces, one token set

- **Dark operator is the default** on `:root`: consoles, dashboards, docs, bench and operator
  Spaces.
- **Light marketing** is `<html data-surface="light">`: the public site, landing pages, decks, the
  blog, and document-like light tools. It uses the same roles with light values.
- Code blocks stay dark on both surfaces. There is no third theme.

### Nested surfaces

From 1.2.0 either polarity can be declared on any element, not only `<html>`. A dark hero, code
panel or specimen card inside a light page carries `data-surface="dark"` on its own root, and a
light card inside a dark console carries `data-surface="light"`:

```html
<html data-surface="light">
  <section class="hero" data-surface="dark">…</section>
</html>
```

Every role (`--text`, `--link`, `--focus`, `--chip-ok` and the rest) re-resolves at that root, the
root takes `color:var(--text)` for its plain text, and `--shadow-focus` follows its `--focus`. The
panel still paints its own background. A surface's own aliases must re-resolve there too: if your
stylesheet maps a local name onto a role on `<html>`, for example `--ink:var(--text)`, declare that
mapping on `[data-surface]` as well, or the nested panel inherits the page's resolved value.

## Color, in short

- **One coral moment per view.** `--accent` marks one thing only: the single primary action
  (`.btn-primary`), the one hero node, or the active-nav marker. Its hover is `--accent-hover`, its
  press state `--accent-press`, and text on it `--accent-ink`. Coral is never a background, a large
  fill, a heading color, a card border or decoration.
- **Gold is premium only.** `--premium`, `.btn-premium`, `.badge-premium` and
  `--shadow-glow-hatun` mark premium or investor emphasis, or the one important number.
- **Teal is links and focus**: `--link`, `--link-hover`, `--focus` and `--shadow-focus`.
- **Focus is a solid ring.** From 1.1.1 the base `:focus-visible` rule draws a 2px solid
  `--focus` outline, offset 2px, around the `--shadow-focus` halo. The outline measures 6.73:1 on
  dark `--bg` and 5.36:1 on light `--bg`. The 55% halo alone measured 2.81:1 and 2.32:1, below
  the 3:1 floor for non-text contrast. Do not remove the outline in surface CSS unless a solid
  `--focus` edge replaces it, as the console layer's `.input` and `.select` border does.
- **Red is errors and destructive actions only.** Use `--color-error`, and `--ink-bad` from the
  console layer for red text.
- **Silver linework** (`--hairline`, `--color-silver-*`) draws the orbit, `.orbit-rule` dividers
  and orbit arcs. It is never used for text.
- **Neutrals carry everything else**: `--bg`, `--bg-deep`, `--surface`, `--surface-alt`,
  `--surface-raised`, `--border`, `--border-subtle`, `--text`, `--text-sub` and `--text-ghost`.
- **Status is never color alone.** Use the proof-status chips (`.chip-proven`,
  `.chip-conjecture`, `.chip-sorry`, …) and status dots with a word.
- **Use the component classes** instead of re-deriving them: `.btn`, `.card`, `.badge`,
  `.chip-*`, `.receipt`, `.code`, `.nav`, `.hero`, `.orbit-rule`, `.evidence-card`, `.metric`,
  `.table` and `.skip-link`.

These pairs were measured with the WCAG 2 formula on the token values. They fall below 4.5:1
for normal text, so put small text where it passes rather than patching the vendored file:

- Light surface, `--accent` as text on `--bg`: 4.17:1. Do not set coral text on light.
- Light surface, white on `.btn-primary`: 4.48:1. On its hover: 3.11:1.
- Dark surface, `--text-ghost` on `--surface`: 4.27:1. On `--bg` it reaches 5.07:1.
- Dark surface, `--color-error` as text on `--bg`: 3.50:1. Use `--ink-bad` (9.48:1).

## Where the rules live

- [`docs/DESIGN_DIRECTION.md`](../docs/DESIGN_DIRECTION.md): the founder art direction. It governs.
- [`kit/logos/LOGO_USAGE.md`](../kit/logos/LOGO_USAGE.md): clear space, minimum sizes and which
  logo goes where.
- [`kit/tokens/COLOR_CONTRAST_REPORT.md`](../kit/tokens/COLOR_CONTRAST_REPORT.md): measured
  contrast for the scales.
- [`kit/brand-bible.md`](../kit/brand-bible.md): voice, naming and banned claims.
- [`docs/FRONTEND_HARDENING.md`](../docs/FRONTEND_HARDENING.md): responsive, accessibility and
  state standard.

## Maintain it

Edit the kit source, never this folder, then rebuild and commit both:

```bash
python -m szl_brand kanchay-build --source-commit <szl-brand main SHA you built on>
python -m szl_brand kanchay-build --check   # fails if kanchay/ differs from kit/
```

`tests/test_kanchay.py` runs the same check in CI. It fails when any of these hold:

- a bundle file is not byte-identical to its kit source;
- a `SOURCE.json` hash is wrong, or a stray file sits in `kanchay/`;
- a webfont or the withdrawn gold token appears in the bundle;
- a `var(--…)` without a fallback is undefined in the two stylesheets.

`source_commit` is the szl-brand main commit the bundle was cut from. For 1.2.0 that is
`20b551b`; the nested-surface change to both kit stylesheets was made in the change that cut 1.2.0,
on top of that commit, and the logos already had these bytes there. For 1.1.1 it was
`a0a27f0`. The focus-outline change to `kit/tokens/szl-design-system.css` was made in the change
that cut 1.1.1, on top of that commit; `szl-console.css` and the logos already had these bytes
there. For 1.1.0 it was `168c53a`, and `szl-console.css` 1.0.0 was added to `kit/tokens/` in the
change that created the bundle.

## Licenses

Code is Apache-2.0 and brand assets are CC BY 4.0, as each stylesheet header says. The SZL
Holdings name, wordmark and brand colors are trademarks of SZL Holdings and are not licensed by
either. See the repository [`NOTICE`](../NOTICE).
