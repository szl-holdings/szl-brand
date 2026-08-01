# KANCHAY frontend hardening standard

This document is the estate-wide implementation contract for investor, developer, evidence, and
operator front ends that consume KANCHAY. It extends the existing KANCHAY tokens and components; it
does not create another design system, replace locked doctrine, or authorize new product claims.

## 1. Responsive control ownership

- A viewport may have one persistent control dock. The `.control-dock` element is the sole owner of
  fixed positioning for its docked controls. Children remain inside that stacking context.
- Do not place independent fixed controls in the same corner. Use one dock, explicit gaps, and one
  responsive collapse or reflow rule.
- At widths of 640 CSS pixels or less, the canonical dock spans between safe inline insets. A product
  may collapse it to one labelled launcher when every action remains keyboard accessible.
- Layouts must support 320, 375, 768, 1024, 1440, and 2560 CSS pixels, browser text enlargement, and
  200% and 400% zoom without overlap, clipping, lost controls, or horizontal page overflow.
- Sticky or fixed content must not entirely obscure a focused component. Reserve content space or
  move the dock when focus would otherwise be covered.

Use `.control-dock` for the owner, `.control-target` for non-button interactive targets, and
`.safe-area-inline` or `.safe-area-block-end` where a surface reaches a viewport edge.

## 2. Safe areas and z-index

KANCHAY exports `--safe-area-top`, `--safe-area-right`, `--safe-area-bottom`, and
`--safe-area-left`. Consumers must use these tokens instead of reading `env(safe-area-inset-*)`
again under product-specific names.

The existing z-index scale remains authoritative:

| Layer | Token | Ownership |
|---|---|---|
| Document | `--z-base`, `--z-raised` | normal content and local elevation |
| Navigation | `--z-dropdown`, `--z-sticky` | menus, headers, sidebars |
| Blocking | `--z-overlay`, `--z-modal` | scrims, dialogs, drawers |
| Floating | `--z-popover` | popovers, tooltips, and the control dock |
| Notification | `--z-toast` | transient notices above the dock |
| Accessibility | `--z-max` | skip links and critical accessibility overlays only |

`--z-control-dock` aliases `--z-popover`; it does not introduce another layer. Literal z-index
values outside a component's local stacking context require an explanation in the pull request.

## 3. Accessibility acceptance

WCAG 2.2 Level AA is the minimum, including keyboard operation, visible focus, focus not obscured,
reflow, contrast, labels, names and roles, and non-color status cues.

- Every action uses a native interactive element unless a documented platform limitation requires
  ARIA. Navigation uses links; actions use buttons.
- Every focusable element has a visible `:focus-visible` treatment and remains visible when focused.
- Pointer targets are at least 24 by 24 CSS pixels or satisfy the WCAG spacing exception. KANCHAY
  uses 44 by 44 CSS pixels for coarse pointers through `--target-size-coarse`.
- Icon-only controls have an accessible name. Async state changes use a restrained `aria-live`
  region and do not move focus unless the interaction requires it.
- Essential behavior works with keyboard alone. Motion honors `prefers-reduced-motion`; visual
  states remain legible in forced-colors mode and at browser-defined text sizes.
- Automated checks supplement, but do not replace, keyboard, zoom, screen-reader, and touch review.

## 4. Truthful component states

Operational presentation state is separate from KANCHAY's existing public claim vocabulary
`REAL`, `MEASURED`, `MODELED`, `ROADMAP`, and `UNAVAILABLE`. When both apply, render both as text.
Never infer evidence class from color, transport reachability, HTTP acceptance, or an animation.

| Component state | Permitted meaning | Required boundary |
|---|---|---|
| `LIVE` | A current runtime observation succeeded. | Show the source and observation time; do not imply uptime, quality, or evidence class. |
| `SAMPLE` | Static example, fixture, or illustrative payload. | Must not appear to execute a production action or present current data. |
| `SIMULATED` | Output came from a simulation or analytical model. | Pair claims with `MODELED`; never promote simulated output to `MEASURED` or `REAL`. |
| `UNAVAILABLE` | The required source or dependency could not be inspected. | Preserve the last verified artifact separately; do not replace failure with zero, empty, or cached-live claims. |

Use `.chip-live`, `.chip-sample`, `.chip-simulated`, and `.chip-unavailable` with the exact visible
state text. `CHECKING` is the neutral loading label until an observation resolves. `PARTIAL` is
allowed only for an aggregate where some named sources returned and others did not.

## 5. Core Web Vitals budgets

Public routes must target Google's "good" field thresholds at the 75th percentile:

| Metric | Budget |
|---|---|
| Largest Contentful Paint | 2.5 seconds or less |
| Interaction to Next Paint | 200 milliseconds or less |
| Cumulative Layout Shift | 0.1 or less |

Field data is authoritative and should be segmented by route class and mobile or desktop. Lab data
may guard a new route or regression, but must not be described as passing production Core Web
Vitals. Reserve media dimensions, keep loading placeholders geometrically stable, avoid main-thread
animation, and disclose when a route has insufficient field data.

## 6. Pull request acceptance checks

A front-end pull request is not ready until its description records:

- the exact pinned KANCHAY source or exported manifest and confirmation that no parallel tokens were
  introduced;
- responsive evidence at the required widths, plus 200% and 400% zoom;
- keyboard order, visible and unobscured focus, target size, screen-reader labels, reduced motion,
  forced colors, and coarse-pointer behavior;
- control-dock ownership, safe-area behavior, and use of named z-index layers;
- loading, success, failure, degraded or partial, empty, and long-content states that apply;
- the source and timestamp behind every `LIVE` state, and clear `SAMPLE`, `SIMULATED`, or
  `UNAVAILABLE` labels where applicable;
- Core Web Vitals field evidence or an explicit `FIELD DATA UNAVAILABLE` statement with provisional
  lab evidence; and
- focused automated checks, visual evidence, and any checks not run.

No pull request may introduce an unmeasured metric, silently relabel a modeled result, disable zoom,
hide focus, or use a successful network response as proof of capability.

## Primary sources

- [W3C Web Content Accessibility Guidelines 2.2](https://www.w3.org/TR/WCAG22/)
- [CSS Environment Variables safe-area insets](https://drafts.csswg.org/css-env-1/#safe-area-insets)
- [Google Core Web Vitals thresholds](https://web.dev/articles/defining-core-web-vitals-thresholds)
- [Vercel Web Interface Guidelines](https://vercel.com/design/guidelines)
- [GitHub Primer responsive foundations](https://primer.style/product/getting-started/foundations/responsive)

These sources define the external accessibility, platform, performance, and interaction baseline.
KANCHAY's evidence labels, visual language, tokens, and governance remain the estate-specific layer.
