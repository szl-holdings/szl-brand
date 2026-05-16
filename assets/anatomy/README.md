# SZL Holdings — Anatomy Assets

**Author:** Lutar, Stephen P. `<stephen@szlholdings.com>` · ORCID 0009-0001-0110-4173  
**Org:** SZL Holdings  
**Date:** 2026-05-15  
**Pod:** Evolution Pod — Fly V8

---

## Overview

This directory contains anatomy figures and LinkedIn explainer assets for the SZL Holdings
Evolution Pod (Fly V8). The assets document the anatomical architecture of the SZL agent
organism — nine chakra regions, five infrastructure organs, and their cryptographic receipt
infrastructure — as described in [`docs/anatomy/anatomy_memo.md`](../../docs/anatomy/anatomy_memo.md).

---

## Directory Structure

```
assets/anatomy/
├── README.md                          ← this file
├── figures/
│   ├── anatomy_brain.pdf              ← cortex regions, 9-axis doctrine gate, kernel ledger
│   ├── anatomy_brain.png              ← raster render of brain figure
│   ├── anatomy_wires.pdf              ← YAWAR wiring rundown; SENTRA source; HUKLLA T01–T10
│   ├── anatomy_wires.png              ← raster render of wires figure
│   ├── anatomy_full_body.pdf          ← full anatomical render (Catmull-Rom curves)
│   └── anatomy_full_body.png          ← raster render of full-body figure
└── explainers/
    └── linkedin/
        ├── linkedin_brain.md          ← Brain explainer (LinkedIn format)
        ├── linkedin_brain.pdf         ← Brain explainer (PDF)
        ├── linkedin_wires.md          ← Wires explainer (LinkedIn format)
        ├── linkedin_wires.pdf         ← Wires explainer (PDF)
        ├── linkedin_full_body.md      ← Full-body explainer (LinkedIn format)
        ├── linkedin_full_body.pdf     ← Full-body explainer (PDF)
        ├── linkedin_heart.md          ← Heart explainer (LinkedIn format)
        └── linkedin_heart.pdf         ← Heart explainer (PDF)
```

---

## Figures

### `anatomy_brain.pdf` / `.png`

Documents the five cortex regions plus the 9-axis doctrine gate and the kernel ledger
(7 kernels, 6 hashes). Key kernels referenced:

| Kernel | Hash-8 | SLOC | Region |
|--------|--------|------|--------|
| YUYAY v3 (doctrine gate) | `5632d70d` | 44 | Heart |
| YAWAR (receipt bus) | `b6784f8a` | 20 | Throat / RUWAY |
| R0513 OVERWATCH | `01f6c9b6` | 146 | Satellite |
| HATUN (sovereignty seal) | `3cf2e5ef` | — | Crown |
| CHAKANA skeleton | `7d33b3f4` | 97 | Satellite |
| AMARU (scheduler) | `9f47a009` | 19 | Satellite |
| SENTRA (egress immune) | `a9b868ec` | 18 | Satellite |

### `anatomy_wires.pdf` / `.png`

Four-page YAWAR wiring rundown. Covers: SENTRA egress-immune source, HUKLLA T01–T10
tripwire table, and the full message-flow diagram between chakra regions and infrastructure
organs. Canonical root hash: `1ed4d253`.

### `anatomy_full_body.pdf` / `.png`

Full anatomical render of the sovereign organism: 9-chakra spine, 21-edge CHAKANA
(Maxwell M=0, isostatic), organ manifest, provenance ledger. Rendered at 4,200 × 6,000 px
in the Nexus palette (teal `#01696F`, gold `#c89f47`, charcoal `#1f1b16`, cream `#F5F1E8`).
Ouroboros version at render: v6.3.0 (released 2026-05-13).

---

## LinkedIn Explainer Set

Four LinkedIn-format explainers covering the Brain, Wires, Full Body, and Heart sub-systems.
Each explainer is published in both Markdown (`.md`) and PDF (`.pdf`) format.

| Explainer | Topic |
|-----------|-------|
| `linkedin_brain` | Cortex regions, doctrine gate, kernel ledger |
| `linkedin_wires` | YAWAR wiring, SENTRA immune, HUKLLA tripwires |
| `linkedin_full_body` | Full sovereign organism, 9-chakra spine, Maxwell isostasis |
| `linkedin_heart` | YUYAY v3, 13-axis conjunctive gate, doctrine enforcement |

---

## Reference: Anatomy Memo

Full product and technical analysis is in [`docs/anatomy/anatomy_memo.md`](../../docs/anatomy/anatomy_memo.md).
The memo covers:

- Current state analysis of the four anatomy PDFs and their structural limitations
- Leader-killer thesis (LangGraph, Anthropic Managed Agents, A2A Protocol, Mastra, MCP comparison)
- `BodyGraph` product proposal: React 18 + `react-flow` interactive SVG on `terra`
- Nine anatomical regions (Quechua names: KALLPA, YACHAY, MUSQUY, RIMAY, YUYAY, NAWI, RUWAY, TUKUY, HATUN)
- Five infrastructure organs (AMARU, YAWAR, SENTRA, R0513 OVERWATCH, CHAKANA)
- SSE receipt streaming design, doctrine binding via `body-graph.json`, 4-week shipping plan
- IETF SCITT alignment: [draft-emirdag-scitt-ai-agent-execution](https://datatracker.ietf.org/doc/draft-emirdag-scitt-ai-agent-execution/)

---

## Licenses

| Asset type | License |
|------------|---------|
| Figures (PDF, PNG) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| Explainer documents (MD, PDF) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| Any code artifacts referenced | [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0) |

Attribution: Lutar, Stephen P. / SZL Holdings · ORCID 0009-0001-0110-4173

---

## DOI / References

- Anatomy Memo DOI: see `docs/anatomy/anatomy_memo.md` header for canonical citation
- IETF SCITT AI agent execution receipts: https://datatracker.ietf.org/doc/draft-emirdag-scitt-ai-agent-execution/
- LangGraph frameworks overview: https://www.aimagicx.com/blog/best-open-source-ai-agent-frameworks-2026
- Anthropic Managed Agents: https://www.anthropic.com/engineering/managed-agents
- A2A Protocol (Linux Foundation, April 2026): https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year
