# szl-brand

> Brand assets, logos, social-preview templates, and visual doctrine for SZL Holdings

[![CI](https://github.com/szl-holdings/szl-brand/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/szl-holdings/szl-brand/actions/workflows/ci.yml)
[![uv-managed](https://img.shields.io/badge/uv-managed-28251D?style=flat-square)](https://github.com/szl-holdings/szl-brand)
[![CodeQL](https://github.com/szl-holdings/szl-brand/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/szl-holdings/szl-brand/actions/workflows/codeql.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/szl-holdings/szl-brand/badge)](https://scorecard.dev/viewer/?uri=github.com/szl-holdings/szl-brand)
[![License](https://img.shields.io/badge/license-CC--BY--4.0-2DA44E?style=flat-square)](./LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20434276.svg)](https://doi.org/10.5281/zenodo.20434276)
[![Concept DOI](https://img.shields.io/badge/concept%20DOI-10.5281%2Fzenodo.19944926-01696F?style=flat-square&logo=doi&logoColor=white)](https://doi.org/10.5281/zenodo.19944926)
[![Series-A Engineering](https://img.shields.io/badge/Series--A-Engineering-success?style=flat-square)](https://github.com/szl-holdings)
[![Brand doctrine](https://img.shields.io/badge/Frontier-Brand%20doctrine-28251D?style=flat-square)](https://doi.org/10.5281/zenodo.20434276)
[![Doctrine v6](https://img.shields.io/badge/Doctrine--v6-passing-success?style=flat-square)](https://github.com/szl-holdings/platform/blob/main/docs/doctrine/szl-doctrine.md)

> **Frontier Capability:** First brand SDK governed by Doctrine v6 with monosemantic governance feature decomposition — `szl-interp` visual-layer integration target (v18.0 Frontier 3 · [Ouroboros Thesis DOI 10.5281/zenodo.20434276](https://doi.org/10.5281/zenodo.20434276)).

`szl-brand` is the authoritative source for SZL Holdings brand assets: social-preview images (1280×640 PNG), logo monograms, visual identity doctrine, and the Python SDK for programmatic brand asset generation. All brand artifacts deployed across the SZL org originate from this repository.

---

## Contents

| Path | Purpose |
|------|---------|
| `anatomy/` | Logo monograms and anatomical brand components |
| `mockups/` | Mockup templates for product and marketing surfaces |
| `motion/` | Motion design assets and animation specifications |
| `posts/` | Social media post templates |
| `social-previews/` | Repository social-preview images (1280×640 PNG, per-repo) |
| `docs/` | Visual identity doctrine and brand guidelines |

---

## Quick Start

```bash
# Clone and install (Python SDK)
git clone https://github.com/szl-holdings/szl-brand.git
cd szl-brand

# With uv (recommended)
uv sync
uv run python -m szl_brand --help

# With pip
pip install -e .
python -m szl_brand --help
```

**To generate a social preview for a new repo:**

```bash
uv run python -m szl_brand generate-preview \
  --repo my-new-repo \
  --title "My Repo Title" \
  --subtitle "Short description" \
  --output social-previews/my-new-repo.png
```

Upload the output to: GitHub repo Settings → Social preview.

---

## Visual Identity

### Social Preview Specification

All SZL repo social previews conform to:
- **Dimensions:** 1280×640 px (2:1 aspect ratio, GitHub recommended)
- **Format:** PNG, lossless
- **Color system:** SZL brand palette (Hydra Teal `#01696F`, Dark `#28251D`)
- **Typography:** Consistent monogram + repo name + tagline layout

### Logo Monograms

The SZL monogram system is defined in `anatomy/`. Three variants:
- **Primary** — full color, light backgrounds
- **Reversed** — white, dark backgrounds
- **Mono** — single-color for print/embossing

---

## Security and Governance

- OpenSSF Scorecard: **7.0** (as of 2026-05-28) — see [scorecard report](https://securityscorecards.dev/viewer/?uri=github.com/szl-holdings/szl-brand)
- CodeQL scanning on every push
- Brand asset changes require PR review — unauthorized derivative works are not permitted under CC-BY-4.0 without attribution

---

## How to Cite

```bibtex
@software{szl_holdings_brand_2026,
  title  = {szl-brand — SZL Holdings Brand Assets and Visual Doctrine},
  author = {{SZL Holdings}},
  year   = {2026},
  doi    = {10.5281/zenodo.20434276},
  url    = {https://github.com/szl-holdings/szl-brand}
}
```

[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20434276-805AD5?style=flat-square&logo=doi&logoColor=white)](https://doi.org/10.5281/zenodo.20434276)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Brand asset changes require one reviewer approval. Doctrine v6 visual standards required.

Related: [`szl-holdings/platform`](https://github.com/szl-holdings/platform) · [`szl-holdings/szl-cookbook`](https://github.com/szl-holdings/szl-cookbook)

---

## License

CC-BY-4.0 — See [LICENSE](./LICENSE). Brand assets may be used with attribution to SZL Holdings. Copyright (c) 2024-2026 SZL Holdings.

---

## Related repositories in the SZL substrate

The 13 substrate repos cross-link reciprocally. This footer is maintained by GH Admin #1 (org-wide).

- [`a11oy`](https://github.com/szl-holdings/a11oy) — vertical alignment substrate (policy · measurement · knowledge · QEC-integrity)
- [`amaru`](https://github.com/szl-holdings/amaru) — Shor-encoded receipt minting (Cardano-anchored)
- [`rosie`](https://github.com/szl-holdings/rosie) — CSS-ingress receipt orchestration
- [`sentra`](https://github.com/szl-holdings/sentra) — Kitaev-surface drift detection on audit fibers
- [`uds-mesh`](https://github.com/szl-holdings/uds-mesh) — UDS span schemas + governance receipts
- [`lutar-lean`](https://github.com/szl-holdings/lutar-lean) — Lean 4 + Mathlib v4.13.0 kernel proofs (30 GREEN modules)
- [`ouroboros`](https://github.com/szl-holdings/ouroboros) — bounded-recursion runtime
- [`ouroboros-thesis`](https://github.com/szl-holdings/ouroboros-thesis) — DOI-pinned thesis substrate (v3 → v18)
- [`platform`](https://github.com/szl-holdings/platform) — composing monorepo (76 packages, 1,220 tests)
- [`szl-brand`](https://github.com/szl-holdings/szl-brand) — anatomy + visual doctrine (PDFs hosted in-repo)
- [`szl-cookbook`](https://github.com/szl-holdings/szl-cookbook) — governed-AI recipes
- [`agi-forecast`](https://github.com/szl-holdings/agi-forecast) — PAC-Bayes + Bekenstein governance-trajectory forecasts
- [`vsp-otel`](https://github.com/szl-holdings/vsp-otel) — OpenTelemetry exporter for Λ-axis spans

Org page: [github.com/szl-holdings](https://github.com/szl-holdings) · Doctrine v6 · 11 axioms · 30 GREEN modules · v18.0 DOI [`10.5281/zenodo.20434276`](https://doi.org/10.5281/zenodo.20434276)
