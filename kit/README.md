# szl-holdings/brand-kit

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Doctrine v11 LOCKED](https://img.shields.io/badge/Doctrine-v11_LOCKED-d4a444.svg)](https://github.com/szl-holdings/lutar-lean)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19944926.svg)](https://doi.org/10.5281/zenodo.19944926)
[![CI](https://github.com/szl-holdings/brand-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/szl-holdings/brand-kit/actions)
[![Security Policy](https://img.shields.io/badge/Security-Policy-red.svg)](SECURITY.md)


<!-- CII-BEST-PRACTICES-BADGE: PENDING — replace 'PENDING' with the project id once founder registers this repo at https://bestpractices.coreinfrastructure.org/ -->
[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/PENDING/badge)](https://bestpractices.coreinfrastructure.org/)

> The KANCHAY brand kit for SZL Holdings — design tokens, logo suite, typography, and
> ready-to-paste component examples. Consumed by every flagship (a11oy, amaru, sentra,
> killinchu, rosie).

**KANCHAY** is the SZL brand organ (*kanchay* = "light / radiance" in Quechua). It is the
calibrated output stage of a governed reasoning system: what we *show* never exceeds what the
anatomy can *prove*. See [`brand-bible.md`](./brand-bible.md) for mission, voice, naming, and
the lock list.

- **License:** code & tokens **Apache-2.0**; brand assets (logos, type specimens) **CC BY 4.0**.
- **Attribution:** ORCID 0009-0001-0110-4173.
- **Fonts:** open-source only (SIL OFL 1.1) — Inter, IBM Plex Sans/Mono, JetBrains Mono.

## Install / use the tokens

Drop the CSS custom properties into your app once at the root:

```css
@import "tokens/COLOR_TOKENS.css";
@import "tokens/COMPONENT_TOKENS.css";
```

```css
.btn-primary { background: var(--color-yuyay-600); color: #fff; border-radius: var(--radius-md); }
.receipt    { font-family: var(--font-mono); color: var(--color-yuyay-300); }
```

Tailwind:

```js
// tailwind.config.js
const szl = require("./tokens/COLOR_TOKENS.tailwind.config.js");
module.exports = { presets: [szl], /* ... */ };
```

SCSS map and a typed JSON source are also provided (`tokens/COLOR_TOKENS.scss`,
`tokens/COLOR_TOKENS.json`).

## Palette (brand)

| Token | Hex | Meaning |
|---|---|---|
| `yuyay-600` (primary) | `#0f726e` | *yuyay* = thought / wisdom — teal, primary interactive |
| `yawar-600` (alert) | `#a32a1f` | *yawar* = blood — red, alerts / circulatory |
| `hatun-400` (accent) | `#cda64a` | *hatun* = great — gold, premium accent |
| `gray-950` (bg) | `#0a0f1e` | navy base (dark-theme-first) |

10-step neutral scale, semantic success/warning/error/info, and dark-theme surfaces are in
[`tokens/`](./tokens). **Accessibility:** all 21 surface pairs pass WCAG AA (17 also AAA) —
see [`tokens/COLOR_CONTRAST_REPORT.md`](./tokens/COLOR_CONTRAST_REPORT.md).

## Logos

[`logos/`](./logos) — primary, monochrome, favicon, and horizontal lockup, plus 3 alternates.
The glyph is a stylized **khipu knot intertwined with a lambda (Λ)**: the Λ-SPINE aggregator
and the khipu receipt DAG, the two halves of the SZL thesis. PNG renders at
16/32/64/128/256/512/1024px in [`logos/png/`](./logos/png). Rationale: [`logos/LOGO_SUITE.md`](./logos/LOGO_SUITE.md).

## Typography & components

- [`TYPOGRAPHY.md`](./TYPOGRAPHY.md) — families, modular scale (Major Third, base 16px),
  `@font-face`, fallback chains.
- [`COMPONENT_TOKENS.md`](./COMPONENT_TOKENS.md) — spacing (4px grid), radii, shadows, motion,
  z-index.
- [`examples/`](./examples) — button, card, alert in **HTML/CSS**, **React**, and **Vue**.

## Voice (one rule)

Math-grounded, story-aware, never mystical, never marketing-fluff. Claim only what is on disk;
label proof status honestly (PROVEN / SORRY / AXIOM / **Conjecture 1**); receipt signatures are
**DSSE PLACEHOLDER**; supply chain is **SLSA L1**. The full lock list lives in `brand-bible.md`.

— Yachay, 2026-06-01. ADDITIVE only; no v11 LOCKED number changed; no mystical content.

## SZL Holdings

![SZL Holdings](./branding/szl-avatar-animated.gif)

*Amaru — the Inca avatar of SZL Holdings. Animated mark (400×400, 16fps loop). Signed Yachay.*
