# szl-brand

**SZL Holdings brand assets.** Source-of-truth for social preview images, logo monograms, and brand guidance applied across the GitHub organization. Updated 2026-05-12.

[![Banners](https://img.shields.io/badge/banners-14%20%C2%B7%201280×640%20PNG-2DA44E?style=flat-square)](#catalog-14-banners)
[![Brand](https://img.shields.io/badge/accent-%23805ad5-805AD5?style=flat-square)](#design-system)
[![License](https://img.shields.io/badge/license-CC%20BY%204.0-blue?style=flat-square)](./LICENSE)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/szl-holdings/szl-brand/badge)](https://securityscorecards.dev/viewer/?uri=github.com/szl-holdings/szl-brand)

## Social previews

Fourteen 1280×640 PNG social previews — one per public org repo plus the founder's personal profile — generated from a single deterministic Python builder. These render in link unfurls on Twitter/X, LinkedIn, Slack, iMessage, and the GitHub repo card.

### Catalog (14 banners)

| # | Repo / profile | Preview | Why this asset |
|---|----------------|---------|----------------|
| 1 | [a11oy](https://github.com/szl-holdings/a11oy) | [`social-previews/a11oy.png`](social-previews/a11oy.png) | Orchestration + Decision Fabric + Trust Plane |
| 2 | [sentra](https://github.com/szl-holdings/sentra) | [`social-previews/sentra.png`](social-previews/sentra.png) | Governed adversary loop |
| 3 | [vessels](https://github.com/szl-holdings/vessels) | [`social-previews/vessels.png`](social-previews/vessels.png) | Maritime fleet intelligence |
| 4 | [terra](https://github.com/szl-holdings/terra) | [`social-previews/terra.png`](social-previews/terra.png) | Real estate deal pipeline |
| 5 | [counsel](https://github.com/szl-holdings/counsel) | [`social-previews/counsel.png`](social-previews/counsel.png) | Policy-gated legal workflows |
| 6 | [carlota-jo](https://github.com/szl-holdings/carlota-jo) | [`social-previews/carlota-jo.png`](social-previews/carlota-jo.png) | Concierge advisory operations |
| 7 | [amaru](https://github.com/szl-holdings/amaru) | [`social-previews/amaru.png`](social-previews/amaru.png) | Convergent multi-source data sync |
| 8 | [ouroboros](https://github.com/szl-holdings/ouroboros) | [`social-previews/ouroboros.png`](social-previews/ouroboros.png) | Bounded-loop runtime — Λ invariant |
| 9 | [ouroboros-thesis](https://github.com/szl-holdings/ouroboros-thesis) | [`social-previews/ouroboros-thesis.png`](social-previews/ouroboros-thesis.png) | Lutar Invariant Family v1→v11 (11 papers) |
| 10 | [szl-cookbook](https://github.com/szl-holdings/szl-cookbook) | [`social-previews/szl-cookbook.png`](social-previews/szl-cookbook.png) | 9 SKILL.md, Apache 2.0 |
| 11 | [szl-trust](https://github.com/szl-holdings/szl-trust) | [`social-previews/szl-trust.png`](social-previews/szl-trust.png) | Covenant Proof Standard reference run |
| 12 | [szl-brand](https://github.com/szl-holdings/szl-brand) | [`social-previews/szl-brand.png`](social-previews/szl-brand.png) | This repo — deterministic banner builder |
| 13 | [.github (org profile)](https://github.com/szl-holdings/.github) | [`social-previews/org-profile.png`](social-previews/org-profile.png) (= `.github.png`) | SZL Holdings org profile card |
| 14 | [stephenlutar2-hash (founder profile)](https://github.com/stephenlutar2-hash) | [`social-previews/stephenlutar2-hash.png`](social-previews/stephenlutar2-hash.png) | Personal profile OG image |

> Note: The `.github` banner is also published as `org-profile.png` for tools that won't accept dot-prefixed filenames in their upload widget. Both files are byte-identical.

### Data sources for every stat shown on the banners (post-hallucination-sweep)

Each banner shows three "stat cards." Every value is sourced from a real file in the platform monorepo, re-verified on 2026-05-11:

| Banner stat | Source of truth |
|---|---|
| `7 Surfaces` (a11oy, .github) | `SOURCE_OF_TRUTH.md`, `dossier/v2/APEX_v2_Operational_Briefing.md` (post-PR-145) |
| `Λ Invariant` (a11oy, stephen) | `THESIS_PUBLICATIONS.md` — Lutar Invariant Family |
| `≤0.59ms Λ p99` (ouroboros) | v11 paper, §"Performance" — 24,800 calls measured |
| `76 Packages` (ouroboros, platform) | `ls packages/` in `szl-holdings/platform` (private) — verified 2026-05-12 against full-sweep-2b.log |
| `218 Tests` (ouroboros) | `pnpm test` in [szl-holdings/ouroboros](https://github.com/szl-holdings/ouroboros) — verified 2026-05-12 against commit `f31d749` |
| `1,220 Tests` (platform) | full-sweep-2b.log across 76 packages (private platform) — verified 2026-05-12 |
| `27/27 e2e` (mcp gateway, platform) | `packages/substrate-mcp-gateway/test/e2e/` (private) |
| `11 Papers` (ouroboros-thesis, .github) | v1-v11 on Zenodo, concept DOI `10.5281/zenodo.19944926`, v11 per-version `20119582` |
| `v11 Latest` (ouroboros-thesis) | `szl-holdings/ouroboros-thesis` tag `paper-v11-1.0.0` |
| `v12 in review` (ouroboros-thesis) | [thesis PR #25](https://github.com/szl-holdings/ouroboros-thesis/pull/25) on branch `paper-v12-thesis` |
| `9 Skills` (szl-cookbook) | `ls szl-cookbook/skills/` |
| `11 Artifacts` (szl-trust) | `szl-trust/runs/E4-codex-kernel-2026-04-29/` |
| `9 Formal Axes` (stephen) | `THESIS_PUBLICATIONS.md` |
| `44 Innovations` (.github) | `THESIS_PUBLICATIONS.md` count |

If any of these values change in the source of truth, update `social-previews/gen.py` and regenerate.

### How to apply (one-time, ~2 min per repo)

GitHub does not expose social-preview upload through its REST API. The asset must be uploaded via the web UI per repo:

1. Open `github.com/szl-holdings/<repo>/settings` (or `github.com/<username>/<username>/settings` for personal profile)
2. Scroll to **Social preview**
3. Click **Edit** → **Upload an image**
4. Pick the matching PNG from this repo's `social-previews/` folder
5. **Save**

After save, verify by visiting the repo and watching the OG image render in any link preview tool (e.g. https://www.opengraph.xyz/url/https%3A%2F%2Fgithub.com%2Fszl-holdings%2F<repo>).

There are 14 banners; budget ~25 minutes for the full upload pass.

### Design system

- **Canvas:** 1280×640 (GitHub's recommended OG dimensions)
- **Background:** vertical gradient `#0a0a0f → #12121a`
- **Accent:** SZL purple `#805ad5` (left 6px accent bar + bottom hairline + pill border + stat values + monogram)
- **Type:** DejaVu Sans (system-ui fallback in the SVG variants)
- **Layout:** kicker / title (auto-shrinking 50–82 px bold) / subtitle (26px regular) / tag pill / three 220×100 stat cards / footer with `github.com/szl-holdings` left and `SZL` monogram right
- **Stat cards:** translucent white fill, hairline stroke, purple stat value, muted label. Value font auto-shrinks (18-34 px) to fit when the value text is long.

### Regenerating

```bash
python3 social-previews/gen.py
```

Edit the `REPOS` table at the top of `gen.py` to add a new repo or change any of the per-repo content (kicker, title, subtitle, tag, three stat triples). Output is deterministic — same inputs always produce the same PNG bytes.

## Anatomy of the SZL Agent Body

[![Heart](https://img.shields.io/badge/anatomy-heart-01696F?style=flat-square)](anatomy/heart.pdf)
[![Brain](https://img.shields.io/badge/anatomy-brain-01696F?style=flat-square)](anatomy/brain.pdf)
[![Wires](https://img.shields.io/badge/anatomy-wires-01696F?style=flat-square)](anatomy/wires.pdf)
[![Full Body](https://img.shields.io/badge/anatomy-full--body-01696F?style=flat-square)](anatomy/full_body.pdf)

Four anatomy PDFs documenting the canonical SZL audit-closure AI agent — Heart (yuyay_v3, 13-axis conjunctive AND), Brain (5 cortical regions + Quantum Mind), Blood (YAWAR append-only receipt bus, 20 SLOC), Immune (SENTRA inline + HUKLLA 10 tripwires). See [`anatomy/README.md`](anatomy/README.md) for the full catalog including originals.

**Author:** Lutar, Stephen P. · ORCID [0009-0001-0110-4173](https://orcid.org/0009-0001-0110-4173)

## License

Brand assets: CC BY 4.0 (attribution required if you remix the design system). The "SZL Holdings" name, the SZL wordmark, and the SZL Holdings brand colors are trademarks of SZL Holdings and are not licensed under CC BY 4.0 — see [`NOTICE`](NOTICE).
