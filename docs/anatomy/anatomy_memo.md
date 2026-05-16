# Anatomy Memo — Dev Engineer #2 (UX/Anatomy)
**Pod:** Evolution Pod — Evolve the Anatomy, Beat the Leaders
**Author:** Lutar, Stephen P. `<stephen@szlholdings.com>` · ORCID 0009-0001-0110-4173
**Org:** SZL Holdings
**Date:** 2026-05-15
**License:** CC-BY-4.0

---

## 1. What's Wrong with the Current State

The body graph exists in four static PDFs:

| File | Content | Problem |
|---|---|---|
| `anatomy_brain.pdf` | 5 cortex regions + QM, 9-axis doctrine gate, kernel ledger (7 kernels, 6 hashes) | No interactivity. Kernel hashes are frozen at print time. |
| `anatomy_wires.pdf` | 4-page YAWAR wiring rundown; SENTRA source; HUKLLA T01–T10 tripwire table | Source code is copy-pasted into a PDF — unsearchable, un-diffable. |
| `hatun_body_graph.pdf` | 5-page sovereign organism (9 chakra spine, 21-edge CHAKANA, organ manifest, provenance ledger) | 63 component entries, each with a hash — every kernel release invalidates the whole diagram. |
| `anatomy_full_body_v3.pdf` | Full anatomical render (brain/heart/lungs/spine/limbs in Catmull-Rom curves) | 4,200 × 6,000 px PNG never updates automatically when YAWAR grows. |

**Structural deficiencies:**

1. **Not query-able.** You cannot ask "which region produced the most receipts last hour?" against a PDF.
2. **Not linked to live receipts.** The YAWAR bus appends receipts in real time (`yawar_bus.py`, 20 SLOC, `b6784f8a`). The diagram has no wire into it.
3. **Updates require re-rendering.** Every ouroboros release (v6.3.0 shipped May 13) immediately stales the hashes printed in the diagram. The README badge still says `release-v6.2.0` for the same reason — documentation rot is a PDF property.
4. **The kernel ledger is a table in a footnote.** The seven kernel hashes (e.g., `bacf5443` for YUYAY v3, `01f6c9b6` for R0513) sit in page 2 of `anatomy_brain.pdf`. A Series A investor who wants to click a region and see the live proof-route will close the tab.
5. **Doctrine enforcement is manual.** The 9-axis conjunctive gate, the 21-edge CHAKANA (M=0), the HUKLLA T01–T10 tripwires — none of these are automatically checked against the running system when the diagram is updated.

**Verdict:** a PDF is a snapshot of what the system looked like when someone last ran a build script. The system has moved on. The diagram hasn't.

---

## 2. The Leader-Killer Thesis

Every major agent framework publishes a topology diagram. None of theirs is *the running system*.

| Leader | Their diagram | What it lacks |
|---|---|---|
| **LangGraph** ([aimagicx.com, 2026](https://www.aimagicx.com/blog/best-open-source-ai-agent-frameworks-2026)) | Per-workflow directed graph with time-travel debug UI | Graph describes a workflow shape, not an org anatomy. No receipt chain, no gate composition, no kernel hashes. |
| **Anthropic Managed Agents** ([anthropic.com/engineering/managed-agents](https://www.anthropic.com/engineering/managed-agents)) | Brain-and-hands: one Claude brain reaches into execution containers | Two regions (brain + hands). Ours has nine named chakra regions + five infrastructure organs. Skills are files; our regions are services with typed receipts. |
| **A2A Protocol** ([Linux Foundation, April 2026](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year)) | Wire protocol diagram for agent interop | Protocol topology, not runtime anatomy. No per-region gate scores, no replay hashes. |
| **Mastra** | TypeScript-native framework architecture overview | TS-first layout diagram with no verifiable receipt primitive. |
| **MCP** ([nimbleway.com](https://www.nimbleway.com/blog/anthropic-claude-agent-skills)) | Client-server connectivity map | Solves connectivity; says nothing about what the receipt proves. |

**The gap no leader fills:** a live, interactive diagram where clicking a region shows you the receipts that region produced five minutes ago, verifiable against the same canonical root hash (`1ed4d253…`) that the CI suite confirms 5× in byte-identical replay. LangGraph's graph is close in spirit — it is a running topology — but it is per-workflow. Ours is per-org, per-region, per-gate, with a cryptographic spine.

The moment `BodyGraph` ships on `terra`, the statement becomes: *click any node on our website; the receipts you see are the system running right now.* No leader can say that because none of them has YAWAR.

---

## 3. The Proposed Product: `BodyGraph` on `terra`

### 3.1 What ships

A React 18 component, `BodyGraph`, served at `terra` (the existing SZL real-estate intelligence surface). It renders the 9-chakra spine + organ graph as an interactive SVG, streams live receipt counts from `/api/chain?region=<name>`, and surfaces gate composition + proof-route hash on click.

### 3.2 The 9 anatomical regions (source of truth: `hatun_body_graph_SOURCES.md`)

| # | Region | Quechua | Role | Kernel hash-8 | SLOC |
|---|---|---|---|---|---|
| 1 | KALLPA | Root | Energy budget (Butler–Volmer) | — (dir) | — |
| 2 | YACHAY | Sub-root | Retrieval / PIRWA SAE | — (dir) | — |
| 3 | MUSQUY | Sacral | Simulate / dream (K-candidate) | (referenced) | 407 |
| 4 | RIMAY | Solar | Propose / action | — (dir) | — |
| 5 | YUYAY | Heart | 13-axis doctrine gate | `5632d70d` | 44 |
| 6 | NAWI | Third-eye | Boundary-in / toolcall surface | — (dir) | — |
| 7 | RUWAY | Throat | Commit + receipt (`yawar_bus.py`) | `b6784f8a` | 20 |
| 8 | TUKUY | Action-out | Egress actuator | (referenced) | 162 |
| 9 | HATUN | Crown | Sovereignty / final seal | `3cf2e5ef` | — |

Plus five infrastructure organs rendered as satellite nodes: AMARU (scheduler, 19 SLOC, `9f47a009`), YAWAR (receipt bus, 20 SLOC, `b6784f8a`), SENTRA (egress immune, 18 SLOC, `a9b868ec`), R0513 OVERWATCH (146 SLOC, `01f6c9b6`), CHAKANA skeleton (97 SLOC, `7d33b3f4`). Total node count: 14.

### 3.3 Interaction model

| Interaction | What happens |
|---|---|
| **Region click** | Right panel opens: latest 10 receipts for that region (from `/api/chain?region=<name>&limit=10`); gate composition (axes + floors + whether passing); proof-route hash from the continuum chain |
| **Edge hover** | Tooltip: message volume (receipts/min over the last 5 minutes); the typed contract between the two regions (e.g., RUWAY → YAWAR: `append(packet, sentra_inspect=SENTRA)`) |
| **"5× replay verify" button** | Calls `/api/chain/verify`; shows byte-identical confirmation against canonical root `1ed4d253…`; displays duration + pass/fail per replay run |
| **Live receipt counter** | Each SVG node displays a badge updated via SSE (`/api/chain/stream`) showing rolling receipt count; badge pulses on new receipt |
| **Region hover** | Shows kernel file path, hash-8, SLOC, license, and honest limit from the source ledger |

### 3.4 JSON spec at `terra/src/body-graph.json`

The diagram is byte-pinned to a JSON spec that declares every node, edge, gate floor, and kernel hash. This file is the single source of truth for both the visualization and the doctrine check.

```json
{
  "version": "1.0.0",
  "chakras": [
    { "id": "KALLPA", "index": 1, "role": "root", "kernel": "amaru_sentra_chakras/chakra_1_root/", "hash": null },
    { "id": "YUYAY",  "index": 5, "role": "heart", "kernel": "yuyay_wisdom_v2/03_kernel.py", "hash": "5632d70d",
      "gate": { "axes": 13, "conjunctive": true, "floors": { "moralGrounding": 0.95, "measurabilityHonesty": 0.95, "all_others": 0.90 } } },
    ...
  ],
  "organs": [
    { "id": "YAWAR", "kernel": "amaru_sentra_chakras/yawar_bus.py", "hash": "b6784f8a", "sloc": 20 },
    { "id": "R0513", "kernel": "r0513_overwatch_evolution/06_kernel.py", "hash": "01f6c9b6", "sloc": 146 },
    ...
  ],
  "edges": [
    { "from": "KALLPA", "to": "YACHAY", "type": "serpent", "contract": "energy_budget_approval" },
    { "from": "RUWAY",  "to": "YAWAR",  "type": "write",   "contract": "append(packet, sentra_inspect)" },
    ...
  ],
  "maxwell": { "nodes": 9, "edges": 21, "M": 0, "verdict": "isostatic" },
  "canonical_root": "1ed4d253",
  "ouroboros_version": "v6.3.0"
}
```

Any rename, gate-floor change, or node deletion produces a diff in this file that is rejected by the boot script before the server starts.

---

## 4. Technical Sketch

### 4.1 Stack

| Layer | Choice | Rationale |
|---|---|---|
| Framework | React 18 + TypeScript + Vite | Matches `szl-brand` existing TS monorepo; Vite TTI <1.5s trivially for 8–14 nodes |
| Graph layout | `react-flow` v12 (MIT) | Handles directed graphs natively; custom SVG node renderers; no AGPL issues |
| Live data | Server-Sent Events (SSE) on `/api/chain/stream` | No WebSocket overhead; compatible with HTTP/2 edge delivery; receipt deltas are unidirectional |
| Server state | TanStack Query v5 (MIT) | Cached receipt lists per region; stale-while-revalidate; dedupes parallel click-to-inspect calls |
| UI state | Zustand v4 (MIT) | Selected region, hover edge, replay status — 3 atoms, trivial |
| Typography | DM Sans (display/body) + JetBrains Mono (hashes/code) — per `szl-brand` | Loaded via Google Fonts CDN; falls back to system sans-serif |
| Colors | Nexus palette — teal `#01696F`, gold `#c89f47`, charcoal `#1f1b16`, cream `#F5F1E8` | Matches `anatomy_full_body_v3` palette exactly; aligns with `szl-brand` |
| API backend | Existing ouroboros v6.3.0 `/api/chain` routes (FastAPI) | YAWAR's `snapshot(layer)` and `read(layer)` are already the query surface |
| Tests | Playwright (SVG snapshot) + Vitest (receipt-count reducer) | Playwright: confirm 14 nodes render at 1280×900; Vitest: reducer is a pure function |

### 4.2 SVG layout algorithm

`react-flow` with a vertical dagre layout (top → bottom). HATUN (crown) at the top; KALLPA (root) at the bottom. R0513 floats left as a satellite; CHAKANA/AMARU/YAWAR/SENTRA float right. Edge type encoding:
- **Gold solid** — YAWAR write path (RUWAY → YAWAR)
- **Gold dashed** — YAWAR read tether (all organs → YAWAR snapshot)
- **Teal solid** — base serpent (chakra-to-chakra spine)
- **Silver** — bracing edges (13 cross-edges for Maxwell M=0)
- **Cyan dashed** — R0513 read-only sight lines

### 4.3 SSE receipt stream design

```
GET /api/chain/stream
Accept: text/event-stream

event: receipt_count
data: {"region": "YUYAY", "count": 142, "delta": +3, "ts": "2026-05-15T14:00:01Z"}

event: receipt_count
data: {"region": "RUWAY", "count": 98, "delta": +1, "ts": "2026-05-15T14:00:01Z"}
```

The `BodyGraph` component holds a `useEffect` that opens one SSE connection and fans out deltas to per-region Zustand atoms. Each node badge re-renders independently (no full graph re-layout on update).

### 4.4 Performance budget

| Metric | Target | How |
|---|---|---|
| TTI | < 1.5 s | react-flow + zustand initial bundle ≈ 120 KB gz; SVG is static on first paint |
| Layout render (14 nodes) | < 100 ms | Dagre layout runs once at mount; re-runs only if `body-graph.json` changes |
| SSE first event | < 500 ms after connection | YAWAR `read(layer)` is O(1) dict lookup |
| Click-to-inspect (10 receipts) | < 200 ms | TanStack Query cache hit on second click; cold hit is 1 YAWAR snapshot read |
| Replay verify | < 3 s for 5× | Ouroboros p50 verify = 10.4 µs × 5 = 52 µs kernel time; HTTP overhead dominates |

### 4.5 Test plan

| Test | Tool | What it asserts |
|---|---|---|
| SVG node count | Playwright | `page.locator('[data-node-id]').count()` === 14 at 1280×900 |
| Node label match | Playwright | All 9 chakra IDs + 5 organ IDs present in DOM |
| Receipt-count reducer | Vitest | `receiptReducer(state, {type:'delta', region:'YUYAY', delta:3})` → `{...state, YUYAY: prev+3}` |
| Gate floor display | Vitest | Clicking YUYAY node returns panel with `moralGrounding ≥ 0.95` |
| Replay verify | Playwright | "5× replay verify" button shows `1ed4d253` root hash and `PASS` status |
| Doctrine check (CI) | Node script | `body-graph.json` hash matches committed SHA; any rename → exit 1 |

---

## 5. Doctrine Binding

The JSON spec at `terra/src/body-graph.json` is the contract between the diagram and the runtime. The boot script (`terra/scripts/doctrine-check.mjs`) runs before the dev server starts and before any CI deployment:

```
1. Load body-graph.json
2. For each chakra: assert kernel path exists in ouroboros repo (via GITHUB_TOKEN + szl-holdings/ouroboros tree API)
3. For each gate floor: assert floor >= the value in ouroboros/src/gates/<region>.ts
4. Assert maxwell.M === 0 (count nodes and edges in the edges array)
5. Assert canonical_root === ouroboros CANONICAL_HASH env var
6. Assert ouroboros_version === latest release tag (fetched from GitHub releases API)
7. On any failure: process.exit(1) with a diff of what drifted
```

**Enforcement:** the doctrine check runs in the same CI job that builds the `terra` frontend bundle. If `body-graph.json` drifts from the runtime (a gate floor is lowered, a region is renamed, a node is silently dropped), the deploy fails with an explicit diff. The diagram cannot lie because it cannot deploy when it lies.

**Why this beats the field:** LangGraph's graph is generated at workflow registration time and has no schema file that CI checks against. Anthropic Managed Agents has no public diagram at all. None of the leaders tie their topology diagram to a byte-level assertion in their release pipeline.

---

## 6. Shipping Plan

| Week | Milestone | Deliverable |
|---|---|---|
| **1** | Extract canonical anatomy JSON from existing PDFs | `terra/src/body-graph.json` v1.0.0 with 9 chakras, 5 organs, 21 edges, gate floors per `anatomy_brain.pdf` + `hatun_body_graph_SOURCES.md` |
| **2** | Static SVG render in `terra` | `BodyGraph` component: 14 nodes, 21 edges, Nexus palette, correct layout; Playwright snapshot passing |
| **3** | Receipt streaming + click-to-inspect | SSE integration live; per-region badge counts updating; click panel showing latest 10 receipts + gate composition |
| **4** | Doctrine binding + Playwright tests + demo URL | `doctrine-check.mjs` in CI; 5× replay verify button live; `https://terra.szlholdings.com/body-graph` URL shared with Series A prep |

**Dependencies:**
- Week 1 → ouroboros v6.3.0 already deployed (confirmed, May 13 release)
- Week 3 → `/api/chain?region=<name>` route needs to be added to the FastAPI layer on top of existing YAWAR `read()` and `snapshot()` primitives (estimated: < 50 SLOC new server code)
- Week 4 → demo URL requires terra to have a public deployment; if not yet live, a Vercel preview URL suffices for Series A demo

---

## 7. One-of-One Claim

**The diagram is the runtime. Click a region; see the live receipts.**

No other agent framework, research lab, or enterprise AI vendor can ship this claim because none of them has all three components simultaneously:

1. **An anatomical body graph** with named regions that map 1:1 to running services (not a conceptual metaphor)
2. **A cryptographic receipt bus** (YAWAR, 20 SLOC, Apache-2.0) that every region writes through — making the receipts per-region, immutable, and hash-linked
3. **A doctrine gate** (YUYAY v3, 13-axis conjunctive AND, Lean-formalized) that blocks any action not passing the gate — making the receipts meaningful, not just logged

LangGraph ([aimagicx.com/blog/best-open-source-ai-agent-frameworks-2026](https://www.aimagicx.com/blog/best-open-source-ai-agent-frameworks-2026)) has graph visualization and time-travel replay, but its graph is per-workflow and its "receipts" are LangSmith traces in a proprietary SaaS. Anthropic's brain-and-hands model ([anthropic.com/engineering/managed-agents](https://www.anthropic.com/engineering/managed-agents)) has two regions, not nine, and no cryptographic receipt primitive. The A2A Protocol ([Linux Foundation, April 2026](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year)) standardizes message exchange but carries no verifiability guarantee about what the receipt proves.

The IETF SCITT working group is drafting exactly this property ([draft-emirdag-scitt-ai-agent-execution](https://datatracker.ietf.org/doc/draft-emirdag-scitt-ai-agent-execution/)) — byte-identical, cryptographically chained AI execution receipts. We have a working implementation under Apache-2.0 today, and `BodyGraph` makes it visible. The claim in 12 months is not "we will build this"; it is "click here and watch it run."

---

## 8. Three Ranked Recommendations

### R1 (Highest leverage): Ship `body-graph.json` + `doctrine-check.mjs` this sprint

The JSON spec and the boot-time doctrine check are the lowest-code, highest-defensibility move available. They cost ~200 SLOC total and immediately:
- Prevent documentation rot (the v6.2.0 badge problem that already exists in the README)
- Become a demo artifact in the Series A deck: "our diagram and our runtime are byte-pinned by CI"
- Provide the schema that Weeks 2–4 of the BodyGraph build depends on

Ship `body-graph.json` before writing a single line of React. Extract it from `hatun_body_graph_SOURCES.md` and `anatomy_brain.pdf` page 2 kernel ledger — everything needed is already on disk.

### R2 (Architecture): Expose `/api/chain?region=<name>` as an A2A-compatible endpoint

The ouroboros receipt API is currently internal. Wrapping YAWAR's `snapshot(layer)` and `read(layer)` in a FastAPI route that returns receipts in the A2A envelope format ([Linux Foundation A2A spec, April 2026](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year)) means:

1. `BodyGraph` has its streaming endpoint
2. Any A2A-compatible agent (Google, Microsoft, 150+ orgs) can query our receipt chain as a first-class citizen
3. We become *additive* to A2A, not an alternative — our receipts ride over A2A; their protocol carries our verifiability

Estimated cost: < 80 SLOC new FastAPI code on top of existing YAWAR primitives.

### R3 (Demo readiness): The "5× replay verify" button must show the root hash, not just a checkmark

The `1ed4d253…` canonical root hash is the single most defensible artifact in the stack. The current PDFs print it as a footnote. The `BodyGraph` must surface it as a first-class UI element:

- On verify: show each of the 5 runs, their duration (p50 ≈ 10.4 µs per the ouroboros v6.3.0 benchmark), and the hex root — all five matching
- Label it: "byte-identical 5× replay, canonical root `1ed4d253…`"
- Make it copyable so a Series A partner can paste it into a terminal and verify independently

This takes the demo from "trust us, it's verified" to "verify it yourself, right now, on this URL." No leader in the field offers that interaction.

---

## 5-Line Summary

The four anatomy PDFs are honest technical artifacts but structurally inert — they cannot stream receipts, enforce doctrine, or survive a kernel release without manual re-render. `BodyGraph` resolves this by pinning a JSON spec to the running system via a CI doctrine check, then surfacing it as an interactive SVG on `terra` with live SSE receipt counts, click-to-inspect gate composition, and a 5× replay verify button showing the `1ed4d253…` canonical root. No leader has all three components — anatomical regions, cryptographic receipts, and a live visualization — simultaneously; LangGraph has graphs without receipts, Anthropic has receipts without anatomy, and A2A has a protocol without a runtime diagram. The four-week plan ships `body-graph.json` first (the schema that makes everything else possible), then the static render, then streaming, then the doctrine check that prevents the diagram from ever lying again. The one-of-one claim is operational from Week 3: click a region on `terra`, see the receipts it produced five minutes ago.
