<div align="center">

# 🜂 szl-brand

**brand**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20434276.svg)](https://doi.org/10.5281/zenodo.20434276) [![ORCID](https://img.shields.io/badge/ORCID-0009--0001--0110--4173-a6ce39?style=flat-square&logo=orcid&logoColor=white)](https://orcid.org/0009-0001-0110-4173) [![Doctrine](https://img.shields.io/badge/Doctrine-v7-7c5cff?style=flat-square)](https://github.com/szl-holdings/.github/blob/main/DOCTRINE_V7.md) [![SLSA](https://img.shields.io/badge/SLSA-L1_honest-22c55e?style=flat-square)](https://slsa.dev/spec/v1.0/levels)

[Hugging Face](https://huggingface.co/SZLHOLDINGS) · [Demo](https://szlholdings-readme.static.hf.space/) · [GitHub Org](https://github.com/szl-holdings)

`receipts.in ≡ receipts.out`

</div>

---
# szl-brand

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-0B1F3A.svg?style=flat-square&logo=creativecommons&logoColor=00D4FF)](https://creativecommons.org/licenses/by/4.0/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20434276.svg)](https://doi.org/10.5281/zenodo.20434276)
[![CI](https://github.com/szl-holdings/szl-brand/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/szl-holdings/szl-brand/actions/workflows/ci.yml)
[![Tests](https://github.com/szl-holdings/szl-brand/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/szl-holdings/szl-brand/actions/workflows/tests.yml)
[![CodeQL](https://github.com/szl-holdings/szl-brand/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/szl-holdings/szl-brand/actions/workflows/codeql.yml)
[![GHAS Code Security](https://img.shields.io/badge/GHAS-Code_Security-2DA44E.svg?style=flat-square&logo=github)](https://github.com/szl-holdings/szl-brand/security/code-scanning)
[![Secret Protection](https://img.shields.io/badge/GHAS-Secret_Protection-2DA44E.svg?style=flat-square&logo=github)](https://github.com/szl-holdings/szl-brand/security/secret-scanning)
[![SBOM](https://github.com/szl-holdings/szl-brand/actions/workflows/sbom.yml/badge.svg?branch=main)](https://github.com/szl-holdings/szl-brand/actions/workflows/sbom.yml)
[![SLSA L1 (SBOM + DCO)](https://img.shields.io/badge/SLSA-L1_(SBOM_%2B_DCO)-0B1F3A.svg?style=flat-square)](https://slsa.dev/spec/v1.0/levels)
[![DCO](https://github.com/szl-holdings/szl-brand/actions/workflows/dco.yml/badge.svg?branch=main)](https://github.com/szl-holdings/szl-brand/actions/workflows/dco.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/szl-holdings/szl-brand/badge)](https://securityscorecards.dev/viewer/?uri=github.com/szl-holdings/szl-brand)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0001--0110--4173-A6CE39.svg?style=flat-square&logo=orcid&logoColor=white)](https://orcid.org/0009-0001-0110-4173)

> Brand assets, logos, social-preview templates, and visual doctrine for SZL Holdings


> **Frontier Capability:** First brand SDK governed by Doctrine v6 with monosemantic governance feature decomposition — `szl-interp` visual-layer integration target (v18.0 Frontier 3 · [Ouroboros Thesis DOI 10.5281/zenodo.20434276](https://doi.org/10.5281/zenodo.20434276)).

`szl-brand` is the authoritative source for SZL Holdings brand assets: social-preview images (1280×640 PNG), logo monograms, visual identity doctrine, and the Python SDK for programmatic brand asset generation. All brand artifacts deployed across the SZL org originate from this repository.

---

## On Hugging Face

This repository's dataset mirror and org showcase live on the [SZLHOLDINGS Hugging Face org](https://huggingface.co/SZLHOLDINGS):

| Surface | Hugging Face artifact |
|---------|---------------------|
| **Source mirror** | [szl-visual-identity](https://huggingface.co/datasets/SZLHOLDINGS/szl-visual-identity) |
| **Org showcase** | [SZLHOLDINGS on Hugging Face](https://huggingface.co/SZLHOLDINGS) — 24 datasets · 19+ Spaces · 2 models |

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


> **NOTE:** SLSA Level 1 (source + build provenance documented). L2/L3 require Sigstore + isolated builders (roadmap).

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
- [`lutar-lean`](https://github.com/szl-holdings/lutar-lean) — Lean 4 + Mathlib v4.13.0 kernel proofs (32 GREEN modules)
- [`ouroboros`](https://github.com/szl-holdings/ouroboros) — bounded-recursion runtime
- [`ouroboros-thesis`](https://github.com/szl-holdings/ouroboros-thesis) — DOI-pinned thesis substrate (v3 → v18)
- [`platform`](https://github.com/szl-holdings/platform) — composing monorepo (76 packages, 1,220 tests)
- [`szl-brand`](https://github.com/szl-holdings/szl-brand) — anatomy + visual doctrine (PDFs hosted in-repo)
- [`szl-cookbook`](https://github.com/szl-holdings/szl-cookbook) — governed-AI recipes
- [`agi-forecast`](https://github.com/szl-holdings/agi-forecast) — PAC-Bayes + Bekenstein governance-trajectory forecasts
- [`vsp-otel`](https://github.com/szl-holdings/vsp-otel) — OpenTelemetry exporter for Λ-axis spans

Org page: [github.com/szl-holdings](https://github.com/szl-holdings) · Doctrine v6 · 11 axioms · 32 GREEN modules · v18.0 DOI [`10.5281/zenodo.20434276`](https://doi.org/10.5281/zenodo.20434276)


---

## What szl-brand Is NOT

Doctrine v6 honest scoping:

- **Not a design system for external use.** Brand assets are SZL Holdings proprietary; no license for third-party reuse without written permission.
- **Not a component library.** This repo ships PDFs, SVGs, and doctrine documents, not React/CSS components.
- **Not a marketing agency brief.** Brand doctrine is founder-governed; external agencies must use approved assets only.
- **Not complete.** Ongoing evolution tracked in ROADMAP.md; Doctrine v6 is the current baseline.
