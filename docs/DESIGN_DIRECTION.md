# SZL Holdings — Design Direction (KANCHAY)

The art direction every downstream surface builds against. Consumes
`szl-design-system.css` and the logo pack in this folder. **ADDITIVE only** — this
evolves the existing KANCHAY token scales (`yawar`, `yuyay`, `hatun`, `gray`); it
replaces nothing. Brand assets © 2026 SZL Holdings · CC BY 4.0 · code Apache-2.0 ·
attribution ORCID 0009-0001-0110-4173.

---

## 1 · Mood — what it should feel like

Calm, exact, and quietly serious. A reader should feel they are looking at an
instrument, not an advertisement. Three references, blended — never copied:

- **Anthropic** — calm restraint, generous whitespace, serious-but-human, honest
  claims. This is closest to our voice. We borrow the *quiet*: lots of air, few
  elements, every element earned.
- **Ollama** — dev-clean, copy-paste-first, terminal aesthetic, fast. We borrow the
  *directness*: the code block is a first-class citizen and stays dark on every
  surface; commands are meant to be copied, not admired.
- **True Anomaly** — defense-tech gravitas and the **polarities** idea (abstract
  software vs hardware; the light of marketing vs the dark of space). Their logo is
  orbit-derived; **we already have the orbit and the node.** We borrow the *posture*:
  measured confidence, deep-space dark, restraint with one bright point.

What we add that none of them have: **every claim is provable on disk with a walkable
receipt.** The logo, a number, and a Lean theorem are the same artifact at three zoom
levels. That is the differentiator, and the visual system exists to carry it.

Banned by doctrine, on every surface: no generic defaults (no Inter-as-the-font, no
Roboto, no purple gradients), no unbenchmarked superlatives, no mystical framing, no
user-visible product codenames. The agent surface is **Chaski**. Shipping products are
only **a11oy** and **killinchu**; everything else is an honest role.

---

## 2 · The polarities — light marketing vs dark operator

The system ships **two surfaces from one set of tokens**, flipped by a single
attribute (`:root` = dark; `[data-surface="light"]`):

| | **Dark operator surface** (default) | **Light marketing surface** |
|---|---|---|
| Where | `/console`, `/elite`, docs, dashboards, the 3D search | public site, landing, decks, blog |
| Ground | space navy `#030F29` → near-black | near-white `#f5f7fa` |
| Feeling | deep space, instrument, focus | open, editorial, generous air |
| Accent | coral `#DF735F` (one node) | coral `#C4543F` (deeper, for AA) |
| Text | `#f5f7fa` on navy (17.8:1) | `#10151c` on white (17:1) |

This is the True-Anomaly polarity in our own palette: the marketing light is where we
*explain*; the operator dark is where we *operate*. Both are the same brand; the flip
is one line. The code block stays dark on **both** (terminal truth doesn't change with
the page).

---

## 3 · Color discipline — earn every color

- **Mostly neutral.** Squint at any screen: it should read as navy/grey with **one**
  bright moment. That moment is the **coral node**. One primary CTA per view; one node
  per hero; one accent underline on the active nav item. If coral appears twice for
  decoration, remove one.
- **`hatun` gold = premium emphasis**, used sparingly for investor/premium surfaces
  and the rare "this is the important number" glow — never as a second general accent.
- **`yuyay` teal = focus + links + the WCAG-AA focus ring** (`--shadow-focus`). It
  already meets AA (≥3:1 non-text) on both navy and near-white; do not change it.
- **`yawar` red = error/destructive only.** Never decorative.
- **Silver linework** (`#E9EEF6 → #9AA7BD → #5C6B86`) is the orbit. Use it for the
  orbital motif, hairline dividers, and decorative arcs — never for text.
- **Status is never color-only.** Every proof-status chip is also labelled in words
  (PROVEN / Conjecture 1 (open) / sorry-tagged / SAMPLE). Colorblind-safe by
  construction.

WCAG AA is a floor, not a goal: body 4.5:1, large 3:1. The contrast report in
`szl-brand/kit/tokens/COLOR_CONTRAST_REPORT.md` (21/21 AA) governs the existing scales;
new surface pairs were chosen to clear the same bar.

---

## 4 · Typography

Self-hosted, sovereign, instant. **0 runtime CDN — no Google Fonts fetch.** The system
ships a robust native UI stack (`system-ui` → platform sans) so text renders offline on
any OS with no FOUT. The KANCHAY type *scale* is preserved (Major Third 1.25, base
16px). A self-hosted WOFF2 (the open-source families catalogued in
`szl-brand/kit/TYPOGRAPHY.md` — IBM Plex / JetBrains Mono, all SIL OFL) may be layered
later via `@font-face` pointing at the app's **own** `/fonts/` path; until then the
stack needs nothing downloaded.

- **Display/headings:** the native sans, weighted 600–700, tracking tightened
  `-0.011em`. Serious, geometric, no novelty.
- **Body:** native sans, 16px floor, 1.6 leading, measure 45–75ch.
- **Mono:** `ui-monospace` (SF Mono / Cascadia / the OS dev mono) for **every hash,
  receipt root, count, and Lean snippet** — because `0/O` and `1/l/I` must be
  unambiguous in audit data. Exact numbers use `tabular-nums lining-nums`.

The monogram in the logo is **not** set in any font — it is hand-authored `<path>`
outlines, so the mark is identical everywhere with zero dependency.

---

## 5 · The orbital / khipu motif — how it recurs

The orbit is the **receipt chain (khipu)** rendered as a path you could fly through;
the node is **one claim** on it; the Λ is the **Λ-Spine** aggregator. The motif recurs
at predictable rhythm, never as random decoration:

1. **Logo** — the canonical mark: tilted (−22°) silver ellipse, one coral node
   upper-right, small Λ on the lower arc.
2. **Hero** (`.hero__orbit` + `.hero__node`) — one faint silver arc, one coral node
   that drifts slowly (24s, `prefers-reduced-motion` honored).
3. **Section dividers** (`.orbit-rule`) — a silver hairline that fades in/out around a
   single small node, instead of a plain `<hr>`.
4. **Cards** (`.card-orbit`) — an optional thin orbit arc clipped into a corner at the
   same −22° tilt.
5. **3D search** (downstream) — the orbit becomes literal: the receipt DAG / khipu
   chain you fly through. The 2D motif is the promise; the 3D surface is the payoff.

**Rule:** the orbit tilt is always −22°. The node is always coral, always singular in a
given frame. Never add a second node for balance.

---

## 6 · Motion principles

Calm, precise, "systems." Motion reveals information; it never performs.

- **Durations:** 75ms (hover tint) · 150ms (buttons) · 250ms (dropdowns) · 400ms
  (modals) · 600ms (route) · 24s (the one slow orbital drift). Tokens in the CSS.
- **Easing:** `--ease-standard` for most; `--ease-emphasized` for hero/large;
  `--ease-orbit` for the drift.
- **Numbers count up; bars grow; lines draw.** Audit values animate on appear (600–800ms)
  so a changing count reads as a measurement, not a flourish.
- **`prefers-reduced-motion: reduce` is respected globally** (the orbit stops, all
  transitions collapse to ~0). Accessibility is not optional.
- No parallax-for-its-own-sake, no bounce, no confetti, no spinners where a skeleton or
  a receipt-state dot would tell the truth better.

---

## 7 · Components (in `szl-design-system.css`)

Buttons (primary coral / secondary / ghost / premium-hatun), cards (+ orbit variant),
badges, **proof-status chips**, the **receipt/proof chip** (the signature component — a
SHA root + a verify-state dot you can read), code block, sticky nav, hero, orbit
divider, audit table, skip-link. All dark-first, all AA, all token-driven. Use the
receipt chip wherever a claim is shown — it is the brand thesis as UI.

---

## 8 · Do / Don't

**Do**
- Lead with whitespace; let one accent carry the eye.
- Show honest dual counts (456 source-declared / 749 doctrine-claimed) side by side.
- Label proof status in words + a status chip; keep `Conjecture 1 (open)`,
  `sorry-tagged`, `SLSA L1`, `DSSE PLACEHOLDER`, `in-process only` verbatim where their
  claim is made.
- Keep the code block dark and copy-paste-first on every surface.
- Reuse the existing `yuyay` focus ring and the `hatun`/`yawar`/`gray` scales as-is.

**Don't**
- Don't introduce a second accent, a purple gradient, or Inter/Roboto as the font.
- Don't enlarge the Λ or imply Λ-uniqueness is settled — it is **Conjecture 1 (open)**.
- Don't use coral for backgrounds, large fills, or more than one moment per frame.
- Don't claim "zero sorries", "fully verified", "SLSA L3", "100% proven", or any
  unbenchmarked superlative — these hard-fail the KANCHAY ship gate.
- Don't surface retired codenames as live products, or render organ names lowercase.
- Don't add decorative illustration, stock imagery, or clip art. Type, whitespace, and
  the orbit motif are the visual language.

---

## 9 · How a downstream dev uses this

1. Link `szl-design-system.css` (self-hosted, no CDN). Default `:root` is the dark
   operator theme; add `data-surface="light"` to the `<html>` for marketing pages.
2. Use the logo from this folder: `szl_logo_horizontal.svg` in nav/footers,
   `szl_favicon_32/180/512.png` for icons, `szl_logo_primary.svg` for covers, the
   `mono_*` versions for one-color contexts. Follow `LOGO_USAGE.md` (clear space =
   one cap-height; min full logo 120px).
3. Build with the component classes; encode meaning with color, never decorate.
4. Wherever a claim renders, render a `.receipt` next to it. Provenance is the product.

— Design Lead, SZL Holdings · ADDITIVE only · CC BY 4.0 · ORCID 0009-0001-0110-4173
