# Architecture Synthesis TL;DR — SZL Holdings
**Author:** Lutar, Stephen P. (ORCID 0009-0001-0110-4173)
**Date:** 2026-05-14
**License:** CC-BY-4.0
**Full detail:** `field_meditation/maki_chaki_limbs_proposal.md` §13

---

## What this is

A one-page executive summary of §13, which synthesizes four research pods (Snowflake, Nemotron, Claude SDK, Anthropic/OpenAI motion study) into actionable decisions for the SZL agent body. All numbers sourced from the pods; no new claims introduced here.

---

## The Body, Complete

```
BRAIN  (Claude SDK + llama3.3-70b default + Nemotron local proposer)
  ↓ routes decisions
HEART  (YUYAY v3 — 430 SLOC — 13-axis gate — hash bacf5443...)
  ↓ emits receipts on PASS
WIRES  (YAWAR 20 SLOC bus → receipt-rain.svg + HUKLLA 660 SLOC ring → tripwire-ring.svg)
  ↓ durable via
FEET   (CHAKI: Postgres + Redis + MinIO + chaki_continuum WAL sidecar)
HANDS  (MAKI: 5 fingers for retrieval — every chunk carries a continuum_hash)
  ↑ full body visible in _anatomy_full_body_v3.pdf
```

---

## Five Decisions Made

### 1. Brain routing: llama default → Claude on hard misses

- **Default path:** `llama3.3-70b` via Snowflake Cortex `AI_COMPLETE` — ~$2,052/mo at 1M decisions
- **Escalation:** `claude-sonnet-4-6` (direct API, ZDR, `temperature=0`, strict tool schema) on YUYAY axis misses — ~$7,278/mo if used for 100% of decisions, but estimated <5% escalation rate = <$364/mo incremental
- **Multimodal only:** Nemotron 3 Nano Omni (Hetzner CPU, Q4_K_XL GGUF) for `locality: strict` PII payloads that cannot leave the box — local proposer only, not a primary model
- **Source:** snowflake_intel_pod.md L194–211; claude_intel_pod.md L219–224; nemotron_intel_pod.md L80–97

### 2. Nemotron is gated, not adopted

- **License FAIL:** NVIDIA Open Model Agreement is not OSI-recognized — fails the Apache/MIT/BSD/CC doctrine gate as a primary model
- **Not blocked forever:** A one-paragraph carve-out (0.5 person-days) unlocks Nemotron for the local proposer role. Must be written before first client-facing deployment.
- **D-HITCHHIKE-PROOF:** without the carve-out, any client shipment that touches Nemotron hitchhikes a proprietary license
- **Source:** nemotron_intel_pod.md L43–62

### 3. Snowflake is the enterprise upgrade path, not v1 blocker

- Snowflake connector is currently DISCONNECTED — v1 deploys on Postgres + Redis + MinIO (fully doctrine-compliant)
- When connected: `chaki_continuum` → Snowflake Streams (D-YAWAR-FLOW at warehouse scale); YUYAY → Snowpark vectorized UDF; Snowflake Time Travel becomes the replay verifier of last resort (90-day, `AT(STATEMENT => ...)` syntax)
- Cost gate: Cortex Search serving runs 24/7 regardless of query volume; idle index = ~$768/mo — drop unused services
- **Source:** snowflake_intel_pod.md L267–283 (Experiment 1 — run first after auth established)

### 4. The moat is the receipt, not the aesthetics

- Anthropic is SZL's visual neighbor (same parchment temperature, same biological metaphor), not a competitor
- SZL's differentiation is the cryptographic receipt layer: `continuum_hash` on every retrieved chunk (codex-in-MAKI), every persisted row (codex-in-CHAKI), every YAWAR append — three layers no other agent framework (Mem0/LangGraph/LlamaIndex/AutoGen/CrewAI) implements
- The visualization of this moat: `heart-beat.svg` — gold YUYAY heart pulsing at 1.2s, sha256 receipt dropping to YAWAR bus on every beat, seeded from `git HEAD[0:8]`
- **Source:** anthropic_openai_motion_study.md L231–251; maki_chaki_limbs_proposal.md §2.4, §3.4

### 5. Visualization stack: v3, not v2

| Artifact | Scope | Format |
|---|---|---|
| `heart-beat.svg` | HEART organ — pulse + receipt drop | SVG+CSS, ~180 SLOC, CC-BY-4.0 |
| `receipt-rain.svg` | YAWAR write-bus — sha256 stream | SVG+CSS, ~220 SLOC, CC-BY-4.0 |
| `tripwire-ring.svg` | HUKLLA + SENTRA immune ring | SVG+CSS, ~160 SLOC, CC-BY-4.0 |
| `_anatomy_full_body_v3.pdf` + `.png` | Whole body, all organs, curved flows, sha256 receipts visible | PDF+PNG, CC-BY-4.0 |

All on parchment `#F5F1E8`, gold `#c89f47`, rust `#8C3A2E`, IBM Plex Mono (OFL 1.1). Zero GSAP (proprietary Webflow license). Zero JS runtime. `prefers-reduced-motion` fallback required.

---

## Three Risks

| Risk | Severity | Fix |
|---|---|---|
| **Snowflake auth blocker** — Cortex, Time Travel, Streams all blocked until account connected | HIGH | v1 on Postgres; Snowflake is upgrade path, not prerequisite |
| **Claude cost ramp** — escalation path is $7,278/mo at full volume | MEDIUM | `chakra_maki_quota` gate + 1h prompt cache (90% cost reduction) + conservative escalation threshold (≥3 axis misses) |
| **Nemotron temptation** — compelling model, 3.5× cheaper than Claude, but proprietary license | HIGH if uncarved | Restrict to `locality: strict` local proposer only until carve-out is written |

---

## Next 3 Kernels (7–10 person-days total)

| # | Kernel | SLOC | ETA | Why |
|---|---|---|---|---|
| 1 | `chaki_continuum` | ≤ 80 | 2–3 days | Closes the cross-invocation gap — YAWAR gets durable feet; 20 SLOC YAWAR core untouched |
| 2 | `maki_vector` | ≤ 80 | 3–4 days | First retrieval finger; unlocks BEAM 1M/10M benchmark (publishable result) |
| 3 | `maki_tool` | ≤ 50 | 2–3 days | MCP dispatch — closes brain↔hands loop; Claude can call YUYAY/HATUN/MUSQUY as MCP servers |

**Sequencing principle:** feet before hands before wires. A body without durable ground cannot be trusted.

---

## SLOC Budget: Still Clean

```
New MAKI + CHAKI:  ≤ 950 SLOC  (≤ 350 kernels + ≤ 150 chakras for MAKI;
                                  ≤ 350 kernels + ≤ 100 chakras for CHAKI)
Existing body:      2,288 SLOC  (all Tier 1 kernels verified by doctrine_audit_pod_v9)
Grand total:       ≤ 3,238 SLOC
```

All 9 doctrine axes ≥ 0.90 across all components. `moralGrounding` and `measurabilityHonesty` ≥ 0.95 across all components. Weakest axis: Brain `licenseHygiene` at 0.90 — conditional on Nemotron carve-out being authored.

---

## Open Items (not blocked, but must not be forgotten)

- [ ] ZDR contract with Anthropic — contact sales; required before `maki_tool` goes to production
- [ ] Nemotron doctrine carve-out — 0.5 person-days; unlocks local proposer role
- [ ] Snowflake auth — provision Enterprise Edition; run Experiment 1 (streams CDC validation) first
- [ ] Claude model pinning — use dated snapshot strings (`claude-sonnet-4-6-20260101`) to prevent silent score drift in YUYAY
- [ ] AlloyScape removal — 6 file copies still contain the string in ouroboros-runtime-contract.v3.json (doctrine_audit_pod_v9.md L35–39); unrelated to §13 but flagged as persistent open item

---

*TL;DR compiled: 2026-05-14. Author: Lutar, Stephen P. Synthesis only — no new claims. Full §13 at field_meditation/maki_chaki_limbs_proposal.md.*
