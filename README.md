# szl-brand

> Brand assets, logos, social-preview templates, and visual doctrine for SZL Holdings

[![CI](https://github.com/szl-holdings/szl-brand/actions/workflows/ci.yml/badge.svg)](https://github.com/szl-holdings/szl-brand/actions/workflows/ci.yml)
[![CodeQL](https://github.com/szl-holdings/szl-brand/actions/workflows/codeql.yml/badge.svg)](https://github.com/szl-holdings/szl-brand/actions/workflows/codeql.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/szl-holdings/szl-brand/badge)](https://securityscorecards.dev/viewer/?uri=github.com/szl-holdings/szl-brand)
[![License](https://img.shields.io/badge/license-CC--BY--4.0-2DA44E?style=flat-square)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![uv](https://img.shields.io/badge/uv-managed-7C3AED?style=flat-square)](https://github.com/astral-sh/uv)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20434276-805AD5?style=flat-square&logo=doi&logoColor=white)](https://doi.org/10.5281/zenodo.20434276)
[![Series-A Engineering](https://img.shields.io/badge/Series--A-Engineering-28251D?style=flat-square)](https://szlholdings.com)
[![Doctrine v6](https://img.shields.io/badge/Doctrine-v6-01696F?style=flat-square)](https://github.com/szl-holdings/platform/blob/main/docs/doctrine/szl-doctrine.md)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0001--0110--4173-A6CE39?style=flat-square&logo=orcid&logoColor=white)](https://orcid.org/0009-0001-0110-4173)

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
