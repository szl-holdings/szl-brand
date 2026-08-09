# KHIPU Command System templates

These templates turn the KANCHAY token system into a consistent command-surface
front door for executives, operators, builders, and verifiers. They are original
SZL compositions: a bounded action path is paired with an evidence path, like two
cords tied to the same decision record.

The templates do not create evidence, operational status, regulatory approval,
or production readiness. Replace every placeholder with a reviewed value and
link each status to its source.

## Package

| File | Use |
| --- | --- |
| `repository-hero-template.svg` | Responsive repository hero with no external assets or motion |
| `org-card-template.svg` | Organization or portfolio card for a public profile |
| `repository-readme-template.md` | Repository front door for outcome, maturity, quickstart, and limits |
| `org-card-template.md` | Organization profile narrative with three audience routes |
| `executive-brief-template.html` | Semantic executive brief and evidence disclosure pattern |

The exported bundle also includes:

- `khipu-command-system.css`, loaded after `system.css`;
- `khipu-command-system.schema.json`, the fail-closed surface contract; and
- `khipu-command-system.example.json`, an explicitly non-operational sample.

## Required viewport evidence

Every adoption records review at 360, 390, 768, 1024, and 1440 CSS pixels. It
also records keyboard-only operation, 200 and 400 percent zoom, visible focus,
44 CSS-pixel targets, reduced motion, non-color state labels, and semantic
landmarks. A passing automated test does not replace manual interaction review.

## Template rules

1. Lead with one user outcome, not a module inventory.
2. Pair the primary product action with an evidence action in the first view.
3. Keep body copy between 60 and 78 characters per line when layout permits.
4. Use one responsive hero, not a badge wall or decorative card wall.
5. Render evidence class and operational state as separate visible text.
6. Put supporting detail in the evidence disclosure, not above the outcome.
7. Preserve `SAMPLE`, `MODELED`, `ROADMAP`, and `UNAVAILABLE` labels.
8. Never substitute a successful HTTP response for capability evidence.

## Adoption

Copy the relevant template into a consumer repository, replace placeholders,
and keep the generated hero local to that repository or pinned to an immutable
KANCHAY revision. Do not hotlink a mutable branch or an unrelated hosted asset.

For web surfaces, load the exported styles in this order:

```html
<link rel="stylesheet" href="/brand/system.css">
<link rel="stylesheet" href="/brand/khipu-command-system.css">
```

Validate the associated JSON disclosure against
`khipu-command-system.schema.json` before publication.
