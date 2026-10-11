<!-- SPDX-License-Identifier: Apache-2.0
(c) 2026 Lutar, Stephen P. - SZL Holdings - ORCID 0009-0001-0110-4173 -->

# KANCHAY vendor bundle 1.3.0

This folder is the ready-to-vendor bundle of KANCHAY v1.3.0, the founder-approved SZL Holdings
design system. The source of truth is `kit/`. Stylesheets and logos are byte-for-byte copies of
their kit sources; the tokens-only CSS and manifest are derived by the canonical builder.
`SOURCE.json` pins every payload by sha256. Do not hand-edit a payload in this folder.

| File | What it is | Kit source |
|---|---|---|
| `szl-design-system.css` | KANCHAY v1.3.0: tokens, both surfaces, base, type scale and components. | `kit/tokens/szl-design-system.css` |
| `szl-console.css` | Operator console layer 1.2.0, additive, on the same tokens. | `kit/tokens/szl-console.css` |
| `szl-tokens.css` | Derived: only the custom properties of `szl-design-system.css` (palette, both polarities, type, spacing, radius, shadow, motion, z). No element or class rules. | built from `kit/tokens/szl-design-system.css` |
| `logos/` | The orbit mark suite: horizontal, primary, transparent, mono white and navy, favicons. | `kit/logos/`, `kit/logos/png/` |
| `SOURCE.json` | Version, base, layers, `source_commit`, licenses and the sha256 of every file above. | built |

## Vendor it

1. **Copy into one folder named `szl/`** where the surface serves static files, for example
   `assets/szl/`. Copy `szl-design-system.css`, `SOURCE.json`, `szl-console.css` only if the surface
   uses its classes, and only the logo files you use, under `szl/logos/`. Copy byte for byte. Never
   edit a vendored file; override in your own stylesheet with tokens.
2. **Stop Git from rewriting the bytes.** Add `assets/szl/** -text` to the surface's
   `.gitattributes`.
3. **Tokens only?** If the surface keeps its own component CSS and its class names (for example
   `.card`, `.chip`, `.hero`) would collide with KANCHAY's, vendor `szl-tokens.css` instead of
   `szl-design-system.css`. It carries every token and both polarities, including nested
   `data-surface` panels, but no element or class rules. The surface then sets its own `color` on
   nested panels.
4. **Link it before the surface's own stylesheet**, the design system first:

   ```html
   <link rel="stylesheet" href="/assets/szl/szl-design-system.css">
   <link rel="stylesheet" href="/assets/szl/szl-console.css"> <!-- operator surfaces only -->
   <link rel="stylesheet" href="/assets/app.css">
   ```

5. **Remove every webfont.** Delete Google Fonts and other CDN font links, and any `@font-face`
   for Inter, Space Grotesk, IBM Plex or Syncopate. Also remove files from the withdrawn `kanchay/`
   1.0.0 export: its stylesheets, component bundle and WOFF2 files. The system uses the device's own
   font stacks through `--font-body`, `--font-display` and `--font-mono`.
6. **Check the copy against the manifest.** Files you did not vendor are skipped:

   ```bash
   cd assets/szl && python -c "import hashlib,json,pathlib;m=json.load(open('SOURCE.json'))['sha256'];bad=[p for p,h in m.items() if pathlib.Path(p).exists() and hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()!=h];print('modified: '+', '.join(bad) if bad else 'ok')"
   ```

### Component refinements on 1.3.0

Replace all three CSS exports and `SOURCE.json` together, using the exact reviewed source revision.
The primitive palette, Orbit identity and versioned component class names are preserved.

- Primary controls now use `--action-bg`, `--action-hover-bg`, `--action-press-bg` and `--action-ink`.
  These roles meet the small-text contrast floor in both polarities. Existing decorative `--accent`
  roles stay unchanged. Custom primary components should adopt the action roles for all states.
- Receipt marks, console dots, meter fills and sparklines use the nearest surface's status inks.
  Always pair them with a visible status word, label or equivalent data description.
- `.code` paints a graphite terminal on either page polarity. The exported `--code-*` roles cover
  its ground, text, syntax, control edge and focus. Give a scrolling code region `tabindex="0"` and
  an accessible label; use `.code--copyable` when it contains `.code__copy` so the control has space.
- `.nav` wraps its links and moves into normal document flow at 640 CSS pixels and below, including
  narrow zoomed views. Links remain present without a JavaScript menu. Buttons and receipts wrap
  long text; nested grids can shrink to the space actually available inside a panel.
- `.surface-holo` is an opt-in silver/teal foil edge for `.card` and `.evidence-card`. Its reading
  ground stays opaque. It adds no coral, animation or required JavaScript, and has a solid boundary
  in forced colors. The `--holo-edge` gradient re-resolves at every polarity root. Use material as
  a quiet framing device, never as a claim of interaction or verification.
- Card elevation uses polarity-local `--shadow-card` and `--shadow-card-hover`, keeping editorial
  shadows light while retaining the existing graphite depth.
- `.hero` uses a polarity-local `--hero-atmosphere`: a navy wash in dark and a quiet silver wash
  in light. Headings balance lines while long identifiers can break inside their bounds.

Open [`kit/examples/html/components.html`](../kit/examples/html/components.html) for the native
component specimen. It loads canonical CSS directly, includes light→dark→light and
dark→light→dark panels, and labels every illustrative command or evidence state as a sample.
The page has no production connection. Its preview button only changes local text; its copy
button copies a sample command and never executes it.

### Upgrading from 1.2.0

1.3.0 changes the neutral values of both polarities. Accents, the type scale, spacing and component
classes stay the same.

- **Dark** becomes the graphite operational surface: `--bg` `#080B12`, `--surface` `#111722`,
  `--surface-raised` `#182232`, `--text` `#F1F4F8`, `--text-sub` `#AAB7C9`.
- **Light** becomes the warm editorial surface: `--bg` `#F5F3EE`, `--surface` white,
  `--surface-alt` `#EBEEF2`, `--text` `#111722`, `--text-sub` `#516075`.
- **New token `--control-edge`.** It moves from the console layer into both polarities, as the
  outline of essential controls (3:1 or more on every ground). `--border` is now a decorative
  separator only, and `.btn-secondary` uses `--control-edge`.
- **`--text-ghost`** now reaches 4.5:1 on every ground in both polarities.

To upgrade, replace `szl-design-system.css`, `szl-console.css` and `SOURCE.json`. Logos are
unchanged. Anything you outlined with `--border` that a person must find and operate (inputs,
toggles, outline buttons) should switch to `--control-edge`.

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

- **Dark operator is the default** on `:root`: a graphite canvas (`#080B12`) for consoles,
  dashboards, docs, bench and operator Spaces.
- **Light editorial** is `<html data-surface="light">`: a warm paper canvas (`#F5F3EE`) for the
  public site, landing pages, decks, the blog, and document-like light tools. It uses the same
  roles with light values.
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
root takes `color:var(--text)` for its plain text (only the values `dark` and `light` act as a
surface; `data-surface` used as a label elsewhere is ignored), and `--shadow-focus` follows its `--focus`. The
panel still paints its own background. A surface's own aliases must re-resolve there too: if your
stylesheet maps a local name onto a role on `<html>`, for example `--ink:var(--text)`, declare that
mapping on `[data-surface]` as well, or the nested panel inherits the page's resolved value.

## Color, in short

- **One coral moment per view.** Reserve coral for the single primary action (`.btn-primary`),
  the one hero node, or the active-nav marker. Buttons use the `--action-*` roles; decorative
  accents use `--accent`. Coral is never a page background, a heading color or a card border.
- **Gold is premium only.** `--premium`, `.btn-premium`, `.badge-premium` and
  `--shadow-glow-hatun` mark premium or investor emphasis, or the one important number.
- **Teal is links and focus**: `--link`, `--link-hover`, `--focus` and `--shadow-focus`.
- **Focus is a solid ring.** From 1.1.1 the base `:focus-visible` rule draws a 2px solid
  `--focus` outline, offset 2px, around the `--shadow-focus` halo. In 1.3.0 the outline measures
  6.97:1 on dark `--bg` and 5.18:1 on light `--bg`. In 1.1.1 the 55% halo alone measured 2.81:1
  and 2.32:1, below the 3:1 floor for non-text contrast. Keep the solid outline in surface CSS.
  Console `.input` and `.select` controls retain both the outline and a solid focused border.
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

- Light surface, `--accent` as text on `--bg`: 4.04:1. Do not set coral text on light.
- Dark surface, `--color-error` as text on `--bg`: 3.62:1. Use `--ink-bad` (9.82:1).

Earlier primary buttons used white directly on coral-500 (4.48:1) and coral-400 on hover
(3.11:1). The action roles correct those states without changing either primitive. Regression
tests check every action state, terminal ink and console signal against its actual token ground;
rendered component checks are still required when a consumer adds its own CSS.

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

Edit and commit the kit source, then rebuild and commit the generated payload:

```bash
python -m szl_brand kanchay-build --source-commit <exact commit containing the kit source>
python -m szl_brand kanchay-build --check   # fails if kanchay/ differs from kit/
```

`tests/test_kanchay.py` runs the same check in CI. It fails when any of these hold:

- a bundle file is not byte-identical to its kit source;
- a `SOURCE.json` hash is wrong, or a stray file sits in `kanchay/`;
- a webfont or the withdrawn gold token appears in the bundle;
- a `var(--…)` without a fallback is undefined in the two stylesheets.

For a reviewed change, `source_commit` should identify the immutable commit that actually contains
the copied kit bytes; commit the source first and the generated bundle second. A pull-request
bundle is a review candidate until the normal protected release path accepts it. A released
bundle must trace to accepted source on `szl-brand` main. The builder checks byte equality against
the working tree and records hashes; it does not independently compare that tree with the supplied
Git commit. Verify the pinned source bytes before downstream promotion.

Historical bundles through the initial 1.3.0 cut recorded the base main revision the change was
built on. Their per-file hashes identify the payload, but that base revision alone does not prove
that the subsequent CSS changes were already present there. Do not infer source equality from
the revision label alone.

## Licenses

Code is Apache-2.0 and brand assets are CC BY 4.0, as each stylesheet header says. The SZL
Holdings name, wordmark and brand colors are trademarks of SZL Holdings and are not licensed by
either. See the repository [`NOTICE`](../NOTICE).
