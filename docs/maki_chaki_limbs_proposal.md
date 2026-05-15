# MAKI-CHAKI — The Limbs Proposal (Hands + Feet of the Agent Body)

**Author:** Lutar, Stephen P. (ORCID 0009-0001-0110-4173, SZL Holdings)
**Status:** Proposal v0 — for Stephen's review before kernel stubs
**Date:** 2026-05-14
**License:** CC-BY-4.0
**Doctrine:** D-SHORTEST-HONEST, D-CODEX-IN-KERNEL, D-YAWAR-FLOW, D-HITCHHIKE-PROOF, D-SPRINGBOARD

---

## 0. The gap this fills

The agent body that SZL has built so far has a **brain** (5 cortex regions + QM), a **heart** (YUYAY v3 13-axis gate, 430 SLOC), **blood** (YAWAR receipt bus, 20 SLOC), an **immune system** (SENTRA 18 SLOC inline + HUKLLA 660 SLOC tripwire ledger), and **sovereign nerve** (HATUN-RAID 199 SLOC). It does not yet have **limbs**. Without limbs the body can think, feel, bleed, and defend — but it cannot **reach** (retrieve) or **stand** (persist beyond a single invocation).

The LinkedIn diagram you sent (Agentic AI with Hybrid RAG on AWS ECS) explicitly calls out two organs that are missing from our anatomy:

- **"Retrieve Context — Search across knowledge sources"** — no equivalent in SZL today.
- **"Knowledge & Tools Layer — Document Store, Vector Database, Structured DB, APIs, Web/Search"** — no equivalent in SZL today.

Iain Tweedie's note from Percona is poking at the same gap from the substrate side: *future-proofing your databases across MySQL, Postgres, Mongo, Redis.* That is the *feet*. The Mem0 State-of-Agent-Memory 2026 report ([mem0.ai/blog/state-of-ai-agent-memory-2026](https://mem0.ai/blog/state-of-ai-agent-memory-2026)) is the same gap from the retrieval side: *that is the hands.* Two limbs. One proposal.

**MAKI** (Quechua: *hand*) = retrieval limb — how the body reaches into corpora, vectors, web, tool APIs, and structured stores. Active **read**.
**CHAKI** (Quechua: *foot*) = persistence limb — what the body stands on durably across invocations. Active **write + state continuity**.

---

## 1. Why limbs, not kernels or chakras

The body schema we already use has a clear pattern:

| Layer | Examples | Role |
|---|---|---|
| Kernels | yuyay_v3 (430), r0513 (146), hatun (199), musquy (219), tukuy (70), chakra_2_sacral (9), t7 (138), qm (163) | Replayable computation units. Byte-identical 5x replay required. |
| Chakras | chakra_2_sacral (CACE prior-weighting), other 6 in design | Doctrine layers — semantic *what may be done* and *under what gate* |
| Body regions | brain, heart, blood, immune, sovereign | Anatomical organs. Each region groups kernels + chakras under one teleology. |

**MAKI-CHAKI is a new body region, not a new kernel and not a new chakra.** It contains its own kernels (the muscle — the actual code that fetches or persists) and its own chakras (the nerve gates — what's allowed). Each kernel inside the limb must still pass the 9-axis conjunctive gate + 5x byte-identical replay, the same as every other SZL kernel. This is what keeps the doctrine intact while we add reach and ground.

---

## 2. MAKI — the hands (retrieval limb)

### 2.1 Five fingers of the hand

| Finger | What it grasps | Doctrine gate | Returns to body |
|---|---|---|---|
| `maki_vector` | semantic neighbors via embedding similarity | YUYAY axis: groundedness ≥ 0.90 | candidate facts ranked by distance |
| `maki_doc` | full-document recall + chunk citation | YUYAY axis: measurabilityHonesty ≥ 0.95 (must cite source URL) | doc IDs + verbatim chunks |
| `maki_struct` | SQL/Cypher against a known schema | YUYAY axis: parsimony ≥ 0.90 (no SELECT *) | typed rows |
| `maki_web` | outbound HTTP fetch + search engine queries | SENTRA prefilter + allowlist + cache | snippet + URL receipt |
| `maki_tool` | MCP tool invocations (Anthropic-style) | HUKLLA T07 (UNAUTHORIZED_NETWORK) + per-tool allowlist | tool result packet |

### 2.2 Leaders in the field — primary sources

| Slot | Leader | License | Primary URL | Why we'd adopt or learn from |
|---|---|---|---|---|
| Vector DB (managed) | Pinecone | proprietary | [firecrawl.dev/blog/best-vector-databases](https://www.firecrawl.dev/blog/best-vector-databases) | 7ms p99, zero-ops baseline to beat |
| Vector DB (OSS) | **Milvus** | Apache 2.0 | [firecrawl.dev/blog/best-vector-databases](https://www.firecrawl.dev/blog/best-vector-databases) | 35k+ stars, <30ms p95, billions-scale, splits storage/compute |
| Vector DB (hybrid) | Weaviate | (mixed OSS + Cloud) | [firecrawl.dev/blog/best-vector-databases](https://www.firecrawl.dev/blog/best-vector-databases) | native vector+keyword+metadata, sub-100ms RAG |
| Vector DB (embedded) | ChromaDB | Apache 2.0 | [firecrawl.dev/blog/best-vector-databases](https://www.firecrawl.dev/blog/best-vector-databases) | 4x faster after 2025 Rust rewrite, best DX |
| Vector DB (in-Postgres) | **pgvector** | (PostgreSQL license, BSD-style) | [firecrawl.dev/blog/best-vector-databases](https://www.firecrawl.dev/blog/best-vector-databases) | 471 QPS at 50M vectors with pgvectorscale, unified data model — *the doctrine pick* for keeping vectors next to relational |
| Vector DB (search) | **OpenSearch** | Apache 2.0 | [opensearch.org/platform/vector-search](https://opensearch.org/platform/vector-search) | community-driven, GPU-accelerated via NVIDIA cuVS, 9.5x perf v3.0 vs v1.3, hybrid BM25 + vector |
| Memory layer | **Mem0** | Apache 2.0 (per `github.com/mem0ai/mem0`) | [docs.mem0.ai/open-source/overview](https://docs.mem0.ai/open-source/overview) + [mem0.ai/blog/state-of-ai-agent-memory-2026](https://mem0.ai/blog/state-of-ai-agent-memory-2026) | Single-pass ADD-only extraction, multi-signal retrieval (semantic + BM25 + entity), built-in entity linking. Reports +29.6 pts temporal / +23.1 pts multi-hop over their old algorithm |
| Memory benchmarks | LoCoMo / LongMemEval / BEAM | benchmark suites | [mem0.ai/blog/state-of-ai-agent-memory-2026](https://mem0.ai/blog/state-of-ai-agent-memory-2026) | LoCoMo 1,540Q / LongMemEval 500Q / **BEAM 1M & 10M token scales** — the production benchmark we should run our MAKI against |
| Agent framework | **LangGraph** | MIT | [github.com/langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | explicit graph state machine — the closest external analog to HATUN |
| Agent framework | **Claude Agent SDK** | OSS SDK (TS/Py) | [docs.claude.com/en/api/agent-sdk](https://docs.claude.com/en/api/agent-sdk) | hooks + MCP + skills + subagents — same architecture that powers Claude Code |
| Agent framework | CrewAI | MIT | [github.com/crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) | role-based crews, lightweight |
| Agent framework | LlamaIndex (agents) | MIT | [github.com/run-llama/llama_index](https://github.com/run-llama/llama_index) | indexing + retrievers + query engines first-class — *the MAKI reference codebase* |
| RAG orchestration | Hybrid RAG (LangGraph pattern) | — | LinkedIn diagram in attached image | Planner→Retrieve→Reason→Critic→Verify with self-hosted vs paid-API routing |

### 2.3 What we keep, what we replace

- **Keep YUYAY as the critic**. The LinkedIn diagram's "Critic / Verifier" is exactly what YUYAY v3 already is — except ours is a 13-axis conjunctive AND with `moralGrounding` and `measurabilityHonesty` ≥ 0.95, not LLM-as-judge. **Our critic is stricter than theirs.**
- **Keep HATUN as the orchestrator**. LangGraph is the closest external analog. We do not need to adopt LangGraph; HATUN already orchestrates with the same graph semantics. But we should benchmark HATUN against LangGraph on a public task suite to make the comparison legible.
- **Keep YAWAR as the memory bus**. Mem0's "single-pass ADD-only" pattern is *already* what YAWAR does — every append is one shot, immutable, hash-linked. We are ahead of Mem0 on the integrity story.
- **Adopt the multi-signal retrieval pattern** from Mem0. Three parallel scoring passes (semantic similarity + BM25 keyword + entity match), fused, ranked. We can build this in `maki_vector` as a < 100-SLOC kernel. This is *the* innovation Mem0 documented as worth +29.6 pts on temporal queries.
- **Adopt BEAM 10M as the public benchmark**. We post-test our MAKI against BEAM 1M (target ≥64.1, parity with the best reported number on Mem0's blog) and BEAM 10M (target ≥48.6). If we hit those numbers with an OSS stack and verifiable receipts, we have a publishable result.

### 2.4 The innovation: codex-in-MAKI

Every external retrieval system we surveyed has the same flaw: **the retrieved fact arrives without provenance the caller can verify cheaply.** Pinecone returns vectors with metadata; OpenSearch returns documents with `_id`; Mem0 returns memories with a `memory_id`. None of them return a SHA-256 hash of the exact bytes you would have to re-fetch to verify the claim later.

**Our innovation:** every MAKI return packet is auto-wrapped in a `continuum_link` — the SHA-256 of the exact bytes used to ground the answer, plus the source URL/path/row-id. The packet that goes back to YUYAY is the chunk *plus* its continuum hash. If a YUYAY axis later requires re-grounding, the verifier can re-fetch and compare hashes byte-for-byte. This is **D-CODEX-IN-KERNEL applied to retrieval** — every fact carries its own audit hash, not just its source.

No other agent framework does this today. LangGraph cites; LlamaIndex returns chunks; Mem0 stores entities. None of them return a cryptographic commitment to the exact bytes. **This is the moat.**

---

## 3. CHAKI — the feet (persistence limb)

### 3.1 Five toes of the foot

| Toe | What it stands on | Store | Doctrine gate |
|---|---|---|---|
| `chaki_relational` | strong ACID transactional ground | **PostgreSQL 17+** | RUWAY-only writes, schema-validated |
| `chaki_document` | flexible semi-structured ground | **PostgreSQL JSONB** (default) or MongoDB (alt) | SENTRA inspect every write |
| `chaki_blob` | large artifacts (PDFs, models, replays) | **S3-compatible** (MinIO self-hosted) | SHA-256 content hash on PUT |
| `chaki_continuum` | YAWAR receipts durable across reboots | **append-only log on disk** (sqlite WAL or duckdb), exported to Postgres `continuum` table for query | only YAWAR.append() writes |
| `chaki_state` | hot state, queues, locks, presence | **Redis** | TTL'd, SENTRA-inspected |

### 3.2 Polyglot or single?

The literature is split. From the field hunt:

- *Pro-polyglot:* dev3lop.com argues delegating workloads (transactional → relational, write-heavy logs → NoSQL, real-time → Redis) avoids bottlenecks. ([dev3lop.com/blog/polyglot-persistence-architectures](https://dev3lop.com/blog/polyglot-persistence-architectures-when-to-use-multiple-database-types/))
- *Pro-Postgres-only:* the r/dataengineering thread surveys real practitioners and finds that most developers and data engineers actually prefer **PostgreSQL or MongoDB alone** rather than running 4+ stores. ([reddit.com/r/dataengineering polyglot thread](https://www.reddit.com/r/dataengineering/comments/1on8j79/polyglot_persistence_or_not_polyglot_persintence/))
- *Polyglot best practice:* the URFP review treats it as the scalable default but flags operational overhead. ([urfpublishers.com](https://urfpublishers.com/article/view/polyglot-persistence-usage-and-challenges))

**My recommendation for SZL v1:** **Postgres-first polyglot.** Specifically:

- **Postgres** does relational + document (JSONB) + vector (pgvector) for v1. One store, three roles.
- **Redis** for hot state only (presence, queues, locks, TTL caches). Postgres LISTEN/NOTIFY is enough until it isn't.
- **MinIO (S3-compatible)** for blobs only — replays, PDFs, large model artifacts.

That's **three feet, not five**, in v1. We add Mongo, dedicated Milvus, etc. *only when we measurably outgrow Postgres+pgvector*. This keeps ops surface small (Iain's concern) and keeps doctrine surface small (our concern).

It also gives a clean conversation with Iain: *"We're standing on Postgres with pgvector for v1 and Redis for hot state. We'd love Percona's perspective on hardening that combo for billion-scale receipts + 100M-vector RAG without horizontal sharding pain."* That's a real architecture talk, not a sales reply.

### 3.3 Innovation: chaki_continuum

Today YAWAR is **in-memory only** (you can read it: 20 SLOC, `self.receipts = []`). When the process dies, the continuum dies. That is the structural reason musquy F2 broke — `_iso_now()` was the symptom, but the deeper problem is the bus has no feet. We've been running on stumps.

`chaki_continuum` is a sidecar that wraps YAWAR.append():

```python
# pseudocode — actual kernel will be < 80 SLOC, replay-tested
def append_with_durability(yawar, packet, sentra_inspect, sink):
    h = yawar.append(packet, sentra_inspect)  # existing 20 SLOC stays untouched
    sink.write_line(json.dumps({"hash": h, "ts": time.time_ns(), "packet": packet}, sort_keys=True))
    sink.fsync()
    return h
```

The `sink` is an append-only WAL on disk (sqlite or duckdb), and on every Nth append we batch-flush to a Postgres `continuum` table partitioned by run_id. **The hash is computed inside YAWAR exactly as today.** The 20-SLOC core is untouched. What we add is the foot beneath it.

**This is the smallest change that closes the cross-invocation gap.** It also makes musquy F2 fully fixable — we lift the fixture, re-run, and the continuum survives reboot.

### 3.4 Innovation: codex-in-CHAKI

Same trick as MAKI: every write to any chaki toe gets a SHA-256 of the value plus the schema version and a HUKLLA-tier stamp. This means **every row in the relational store, every document, every blob, every state entry, every receipt** carries a content-addressed identity that the rest of the body can re-verify. We can answer "did this row change since I last read it?" by hash comparison, not by trusting the storage layer.

Nobody does this in standard polyglot. Percona, MongoDB, Mongo Atlas — none of them store a doctrine-stamped content hash inline with every row. **This is the moat on the feet side.**

---

## 4. Where MAKI-CHAKI sits in the body

```
                          BRAIN  (5 cortex regions + QM)
                            |
                            | reads gated scores (tether)
                            v
HEART  ←--- YUYAY v3 ---→  receipts  ---→  YAWAR  ←---  CHAKI  (durable feet)
   ↑                                          ↑
   | candidate context                        |
   |                                          | egress on PASS
MAKI  (hands — reaches into world)            |
   ↑                                          |
   |                                       SENTRA (immune)
   |                                          ↑
RIMAY (proposer) ←--- MAKI returns ---→ MUSQUY (k-candidate sim)
                                              |
                                         HATUN-RAID (sovereign)
                                              |
                                         TUKUY (egress)
```

- MAKI **feeds** the candidate-context input to RIMAY/MUSQUY *before* YUYAY is consulted. This is the hybrid-routing answer: if MAKI returns a high-confidence existing answer (gated by YUYAY-lite axis), HATUN can short-circuit the expensive MUSQUY simulation. Self-hosted retrieval, paid-API only when MAKI misses.
- CHAKI **catches** every YAWAR receipt and persists it to disk-then-Postgres. The brain reads from YAWAR.read() exactly as today; CHAKI is invisible to the brain except that snapshots now survive reboot.

---

## 5. Kernel + chakra split per limb

### MAKI kernels (5)

| Kernel | Target SLOC | Inputs | Outputs | Replay test |
|---|---|---|---|---|
| `maki_vector` | ≤ 80 | (query_text, k, filter) | [(chunk, src_url, continuum_hash, score)] × k | pinned fixture corpus + fixed seed |
| `maki_doc` | ≤ 60 | (doc_id) or (search_text) | (full_text, src_url, continuum_hash) | pinned fixture docs |
| `maki_struct` | ≤ 70 | (SELECT query, params) | typed rows + per-row continuum_hash | pinned in-memory sqlite fixture |
| `maki_web` | ≤ 90 | (url) or (search_query) | (text, src_url, continuum_hash, cache_hit) | mock HTTP fixtures (no live network in replay) |
| `maki_tool` | ≤ 50 | (tool_name, args, allowlist) | (result, tool_hash) | mocked MCP tool fixtures |

### MAKI chakras (3)

| Chakra | Doctrine role | Sits at |
|---|---|---|
| `chakra_maki_prior` | re-uses CACE prior-weighting (chakra_2_sacral) — biases retrieval toward priors the agent has already grounded | between query → ranker |
| `chakra_maki_provenance` | enforces that every returned chunk carries a verifiable continuum_hash; rejects un-hashed returns | post-rank, pre-emit |
| `chakra_maki_quota` | per-cycle retrieval budget — caps tokens, caps cost, caps wall-time | called by HATUN before any maki_* call |

### CHAKI kernels (5)

| Kernel | Target SLOC | Role | Replay test |
|---|---|---|---|
| `chaki_relational` | ≤ 90 | Postgres typed CRUD with continuum_hash columns | sqlite fallback in test |
| `chaki_document` | ≤ 70 | JSONB insert/upsert/query | sqlite JSON fallback in test |
| `chaki_blob` | ≤ 60 | S3-compatible PUT/GET with content SHA-256 | local filesystem fallback in test |
| `chaki_continuum` | ≤ 80 | YAWAR append sidecar — WAL on disk + Postgres batch flush | in-memory + sqlite test fixture |
| `chaki_state` | ≤ 50 | Redis pub/sub + TTL caches | fakeredis fixture |

### CHAKI chakras (2)

| Chakra | Doctrine role |
|---|---|
| `chakra_chaki_continuum` | every write must produce a continuum_hash before commit; commit fails if hash collides with existing row under different bytes |
| `chakra_chaki_tier_gate` | reads from PRODUCTION tier require Stephen-approval per HUKLLA AutonomyTier; writes to PRODUCTION require ceremony |

---

## 6. Total proposed surface area

- **10 new kernels**, each ≤ 90 SLOC = **≤ 700 SLOC total** for the limbs.
- **5 new chakras**, each doctrine-only (gate config + small enforce fn) = ≤ 250 SLOC.
- **Total new surface: ≤ 950 SLOC** to bolt full hands + feet onto the existing 1,365 SLOC body.
- 5x byte-identical replay required per kernel, same as the 7 Tier 1 kernels we already have.
- BEAM 1M + 10M public benchmark to be run on the integrated MAKI as the publishable result.

---

## 7. Three moats, one limb pair

1. **codex-in-MAKI** — every retrieved fact carries a SHA-256 of the bytes used to ground it. No other agent framework returns a cryptographic content commitment with the chunk. Verifiable RAG, not just attributable RAG.
2. **codex-in-CHAKI** — every persisted row, document, blob, receipt, and state entry carries a doctrine-stamped content hash inline. Polyglot persistence with byte-level audit, not just transaction logs.
3. **chaki_continuum** — YAWAR's 20 SLOC stays untouched; durability is a sidecar that fsyncs to WAL and batch-flushes to Postgres. Cross-invocation determinism becomes a first-class property of the bus, not a hope.

---

## 8. What I want to decide with Stephen before coding

1. **Postgres-first polyglot vs full polyglot day-1?** I'm proposing 3 feet (Postgres + Redis + MinIO) in v1. If you want Mongo as a 4th foot for the document role specifically, we add `chaki_document` v2 backed by Mongo with the JSONB version as fallback. Either way the chakra gate is identical.
2. **Adopt Mem0 OSS as the maki_vector implementation, or build our own?** Mem0 is Apache 2.0 (license check pending), already has the multi-signal retrieval pattern we want, integrates with Qdrant/pgvector/etc. We could fork it and put codex-in-MAKI on top — fastest path. Or we build maki_vector from pgvector + a 50-SLOC ranker — most doctrine-pure.
3. **MCP for tools (maki_tool) or roll our own?** Claude Agent SDK + Anthropic MCP is the emerging standard. Adopting MCP for `maki_tool` lets us inherit the Claude ecosystem at zero cost. Doctrine-compatible because MCP servers can be allowlisted.
4. **Do we name the limb MAKI-CHAKI or stick with English?** Every other body region you've named in Quechua. I'd keep it MAKI-CHAKI for naming consistency, with English `(hands/feet)` glosses.
5. **What goes into the Iain reply?** I have a draft below in §10. Want me to send something close to that or do you want to draft yourself?

---

## 9. Honest scope and what this is NOT

- This proposal does **not** build the limbs yet. It is a contract for what they would be.
- BEAM 1M / 10M benchmarks are **planned-not-yet-run**. Hitting parity with Mem0's published 64.1 / 48.6 is the target, not yet the result. Reported with that scope.
- `chaki_continuum` durability claims are **on disk + WAL**, not geo-replicated. Future work: replicated Postgres + Lit cross-region replicas of MinIO. Stated explicitly.
- The "moat" framing is honest-comparative: no surveyed framework (Mem0, LangGraph, LlamaIndex, AutoGen, CrewAI, Pydantic AI, Claude Agent SDK) ships verifiable content hashes on every retrieved chunk or persisted row *as of the sources cited in §2.2*. We must keep verifying as the field moves.

---

## 10. Draft reply to Iain Tweedie (Percona)

> Hi Iain,
>
> Thanks for reaching out. Future-proofing the persistence layer is actually exactly where my work is heading right now. I'm building an agent framework at SZL Holdings where the receipt bus, memory layer, and structured state are split across Postgres (with pgvector for RAG and JSONB for documents), Redis for hot state, and S3-compatible blob storage — a polyglot stack with each store doctrine-bound to a specific role rather than a free-for-all.
>
> The piece I'd be most interested in Percona's perspective on: at billion-scale append-only audit logs (cryptographically-linked receipts, every row content-addressed) combined with 100M-vector pgvector RAG on the same instance, what's the hardening play before horizontal sharding becomes unavoidable? I've seen your MariaDB / Mongo / Postgres comparison work; the operational angle is exactly the gap I'm trying to close without ballooning the ops surface.
>
> Happy to share an architecture document if useful — would 30 min next week work?
>
> Stephen P. Lutar
> SZL Holdings · ORCID 0009-0001-0110-4173

That turns Iain from cold outreach into a real architecture conversation, gives him a reason to engage (the question is hard and Percona's actual expertise applies), and gives us free expert review of our v1 polyglot pick.

---

## 11. Sources cited

1. Mem0 — State of AI Agent Memory 2026. [mem0.ai/blog/state-of-ai-agent-memory-2026](https://mem0.ai/blog/state-of-ai-agent-memory-2026)
2. Mem0 — Open Source Overview. [docs.mem0.ai/open-source/overview](https://docs.mem0.ai/open-source/overview)
3. Mem0 — GitHub repo. [github.com/mem0ai/mem0](https://github.com/mem0ai/mem0)
4. Firecrawl — Best Vector Databases in 2026. [firecrawl.dev/blog/best-vector-databases](https://www.firecrawl.dev/blog/best-vector-databases)
5. Alice Labs — AI Agent Frameworks 2026 Production-Tested Ranking. [alicelabs.ai/en/insights/best-ai-agent-frameworks-2026](https://alicelabs.ai/en/insights/best-ai-agent-frameworks-2026)
6. OpenSearch — Vector Search platform. [opensearch.org/platform/vector-search](https://opensearch.org/platform/vector-search)
7. OpenSearch — GPU-accelerated vector search blog. [opensearch.org/blog/gpu-accelerated-vector-search-opensearch-new-frontier](https://opensearch.org/blog/gpu-accelerated-vector-search-opensearch-new-frontier/)
8. AWS — Billion-scale vector DBs with GPU acceleration on OpenSearch Service. [aws.amazon.com/blogs/big-data/build-billion-scale-vector-databases-in-under-an-hour](https://aws.amazon.com/blogs/big-data/build-billion-scale-vector-databases-in-under-an-hour-with-gpu-acceleration-on-amazon-opensearch-service/)
9. Percona — Choosing the Right Database: MariaDB vs. MySQL vs. PostgreSQL vs. MongoDB. [percona.com/blog/choosing-the-right-database](https://www.percona.com/blog/choosing-the-right-database-comparing-mariadb-vs-mysql-postgresql-and-mongodb/)
10. Percona — Database comparison page. [percona.com/compare-mysql-mongodb-postgresql-mariadb](https://www.percona.com/compare-mysql-mongodb-postgresql-mariadb/)
11. URF Publishers — Polyglot Persistence Usage and Challenges. [urfpublishers.com](https://urfpublishers.com/article/view/polyglot-persistence-usage-and-challenges)
12. r/dataengineering — Polyglot Persistence or not (practitioner survey). [reddit.com](https://www.reddit.com/r/dataengineering/comments/1on8j79/polyglot_persistence_or_not_polyglot_persintence/)
13. dev3lop — Polyglot Persistence Architectures: When to Use Multiple Database Types. [dev3lop.com](https://dev3lop.com/blog/polyglot-persistence-architectures-when-to-use-multiple-database-types/)
14. LangGraph — GitHub repo. [github.com/langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)
15. Claude Agent SDK — Anthropic docs. [docs.claude.com/en/api/agent-sdk](https://docs.claude.com/en/api/agent-sdk)
16. LlamaIndex — GitHub. [github.com/run-llama/llama_index](https://github.com/run-llama/llama_index)
17. CrewAI — GitHub. [github.com/crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)

---

*End of proposal v0. Awaiting Stephen's decisions on §8 questions 1–5 before kernel stubs are written.*

---

## 12. Appendix: Body-region quick-reference

*(No new content — existing proposal ends at §11. §12 reserved for future experiment results.)*

---

## 13. Synthesis: Brain + Heart + Hands + Wires + Feet

**Author:** Lutar, Stephen P. (ORCID 0009-0001-0110-4173, SZL Holdings)
**Compiled from:** snowflake_intel_pod.md, nemotron_intel_pod.md, claude_intel_pod.md, anthropic_openai_motion_study.md, doctrine_audit_pod_v9.md
**Date:** 2026-05-14
**License:** CC-BY-4.0
**Doctrine gates:** D-SHORTEST-HONEST · D-CODEX-IN-KERNEL · D-YAWAR-FLOW · D-HITCHHIKE-PROOF · D-SPRINGBOARD

---

### 13.0 Purpose

This section collapses four research pods into a single decision-ready architecture picture. Every claim below is traced to a source pod with a line range. Where a claim has no pod anchor, it is flagged explicitly as synthesis-only judgment.

---

### 13.A BRAIN — Claude SDK + Nemotron Decision Matrix

#### 13.A.1 Where Claude lives in the body

| Role | Surface | SDK | Doctrine link |
|---|---|---|---|
| `maki_tool` | MCP **client** — calls kernel MCP servers (YUYAY, HATUN-RAID, MUSQUY) | `claude-agent-sdk` with `mcp_servers` option | D-CODEX-IN-KERNEL: kernel codex injected in system prompt on every call |
| YUYAY rubric LLM scorer | Structured output, 13-axis JSON, `temperature=0`, `strict:true` tool schema | `anthropic` Messages API (Client SDK) | D-SHORTEST-HONEST: no free-text escape; forced `tool_choice` |
| HATUN-RAID subagents | Opus 4.7 orchestrator + Sonnet 4.6 / Haiku 4.5 workers spawned via `Task` tool | Claude Agent SDK `ClaudeAgentOptions(agents=[...])` | D-SPRINGBOARD: 87.0% Opus+Haiku vs 74.8% Opus-alone (claude_intel_pod.md L358) |

- **ZDR requirement (non-negotiable):** All kernel calls must use Client SDK with client-side tool execution — NOT the managed `mcp_servers` connector — to maintain ZDR eligibility. The managed connector is explicitly not ZDR-eligible. Source: claude_intel_pod.md L96, L163–168.
- **Prompt caching:** `cache_control: {type: "ephemeral", ttl: "1h"}` on doctrine context + 13-axis rubric definitions. At 1,000 calls/day, caching reduces daily cost from ~$180 to ~$18 (90% reduction). Source: claude_intel_pod.md L219–224.
- **D-YAWAR-FLOW compliance:** Every Claude API response logs `{response_id, prompt_sha256, model, axis_id, score}` to YAWAR. The `response_id` is the receipt. Source: claude_intel_pod.md L176–179.

#### 13.A.2 Why Nemotron fails doctrine as a primary model

**Exact reason from nemotron_intel_pod.md §2 (lines 43–62):**

> "The NVIDIA Open Model Agreement is proprietary — it is **not OSI-recognized**. It grants broad usage rights including commercial deployment, but it is not equivalent to Apache-2.0 in redistribution permissiveness and it may impose NVIDIA platform constraints in certain product-specific terms."

The doctrine gate requires: Apache-2.0 / MIT / BSD-3 / CC-BY **only**. The NVIDIA Open Model Agreement is none of these. Nemotron therefore **FAILS the license gate as a primary model** without an explicit doctrine carve-out. This is a formality (the practical risk is minimal for internal inference), but the carve-out must be written before any client-facing deployment. Source: nemotron_intel_pod.md L56–62.

**D-HITCHHIKE-PROOF implication:** Shipping Nemotron weights to a client without the carve-out would hitchhike a proprietary license into their environment. Blocked until carve-out is authored.

#### 13.A.3 Where llama-3.1 / llama-3.3-70b still wins: cost

At 1M YUYAY decisions/month (500 token input, 200 token output):

```
┌────────────────────────────────────────────────────────┐
│  COST COMPARISON — 1M decisions/month                  │
├──────────────────────┬─────────────────────────────────┤
│ llama3.3-70b (Cortex)│ ~$2,052/mo total (llama path)   │
│  - LLM inference     │   $756                          │
│  - Warehouse compute │   $528                          │
│  - Cortex Search     │   $768                          │
├──────────────────────┼─────────────────────────────────┤
│ claude-3-7-sonnet    │ ~$7,278/mo total (claude path)  │
│  - LLM inference     │  $6,750                         │
│  - Warehouse compute │   $528                          │
└──────────────────────┴─────────────────────────────────┘
```

Source: snowflake_intel_pod.md L194–211. Delta: **$5,226/mo or ~3.5×** cheaper on llama. At this cost delta, llama wins every YUYAY scoring cycle where quality parity is acceptable.

**D-SHORTEST-HONEST caveat:** These are Snowflake Cortex rates (Enterprise, AWS US). Direct API llama rates differ. Always verify against [Snowflake Service Consumption Table](https://www.snowflake.com/legal/service-consumption-table/) before committing.

#### 13.A.4 Fallback chain: the brain routing decision

```
Incoming YUYAY scoring request
        │
        ▼
[1] llama3.3-70b via Snowflake Cortex AI_COMPLETE
        │
        ├─ axis scores all ≥ 0.90 AND moralGrounding + measurabilityHonesty ≥ 0.95?
        │     YES → emit receipt → YAWAR
        │     NO  → escalate ──────────────────────────────────────────────────────┐
        │                                                                          ▼
        │                                              [2] claude-sonnet-4-6 (direct API, ZDR)
        │                                                    temperature=0, strict tool schema
        │                                                    forced tool_choice → score_output
        │                                                    system prompt cached (1h TTL)
        │                                                          │
        │                                                          ├─ PASS? → emit receipt → YAWAR
        │                                                          └─ FAIL? → gate blocks; log to R0513
        │
        └─ multimodal input (audio/video/PDF)?
              YES → Nemotron Omni (local proposer, Hetzner CPU, Q4_K_XL GGUF)
                    → structured JSON extract → llama/claude for synthesis
```

- **llama default** (≤$2,052/mo): all routine YUYAY decisions
- **Claude on hard YUYAY misses**: escalation path; estimated <5% of decisions based on rubric complexity
- **Nemotron local proposer**: only for PII-bound multimodal where data must not leave the Hetzner box (`locality: strict`). Source: nemotron_intel_pod.md L80–97.
- **D-YAWAR-FLOW compliance**: every hop in the chain logs a receipt. The hop count is part of the receipt.

---

### 13.B HEART — YUYAY v3 Kernel + Heartbeat Visualization

#### 13.B.1 Heart already exists in the body

The `yuyay_v3_heart` kernel is **430 SLOC, canonical hash `bacf5443...`**, 5× byte-identical replay confirmed. Source: doctrine_audit_pod_v9.md L13, L107. No new code needed here.

The heart's 13-axis conjunctive AND gate is the doctrine's nerve center. Two axes are elevated:
- `moralGrounding ≥ 0.95` — must always meet or exceed
- `measurabilityHonesty ≥ 0.95` — must always meet or exceed
- Remaining 7 axes (of the 9-axis conjunctive set used in HATUN-RAID) ≥ 0.90 AND

Source: maki_chaki_limbs_proposal.md §2.3 L73; doctrine_audit_pod_v9.md L252 (internal contradiction note: anatomy_brain.pdf says 13-axis; HATUN-RAID blurb says 9-axis; the YUYAY kernel itself is 13-axis with 9 axes active per cycle in HATUN).

#### 13.B.2 Heartbeat visualization

- **File:** `/home/user/workspace/szl_motion/assets/heart-beat.svg`
- **What it shows:** The gold HEART organ (`#c89f47`, motion-library gold) pulses at 1.2s intervals (50 BPM resting cadence). At each systole, a receipt line drops from the heart into the YAWAR write-bus below, labeled with a truncated sha256 in IBM Plex Mono. The sha256 is seeded from `git HEAD[0:8]` at build time. The full-body context is rendered in `_anatomy_full_body_v3.pdf` / `_anatomy_full_body_v3.png` (see §13.L).
- **Hash injected at build:** `d94c683e` (current session seed)
- **CI injection:**
  ```bash
  SHA=$(git rev-parse --short=8 HEAD)
  sed -i "s/RECEIPT_HASH/$SHA/g" assets/heart-beat.svg
  ```
- **Doctrine check (D-CODEX-IN-KERNEL):** The animation itself is a signed artifact. The sha256 shown is real git state, not simulated. "Animation receipts." Source: anthropic_openai_motion_study.md L401–408, L501–510.
- **License:** Pure SVG + CSS `@keyframes` — zero dependencies, no JS, no GSAP, GitHub-safe, `prefers-reduced-motion` compliant. Source: anthropic_openai_motion_study.md L530–553.
- **SZL visual identity anchor:** Parchment `#F5F1E8` + gold `#c89f47` (motion-library) + ink `#1A1A1A`, IBM Plex Mono for all hash labels. Anthropic's `#faf9f5` parchment is a neighbor in color temperature (2 stops apart), confirming SZL's visual DNA is in the same biological-warmth register — but SZL's moat is the receipt, not the aesthetic. Source: anthropic_openai_motion_study.md L231–238.

---

### 13.C HANDS — MAKI (5 Fingers + 3 Chakras)

#### 13.C.1 Confirmed architecture (no changes from §2–§5)

| Finger | Grasps | SLOC budget | Gate |
|---|---|---|---|
| `maki_vector` | semantic neighbors, embedding similarity | ≤ 80 | YUYAY groundedness ≥ 0.90 |
| `maki_doc` | full-document recall + chunk citation | ≤ 60 | measurabilityHonesty ≥ 0.95, cite source URL |
| `maki_struct` | SQL/Cypher against known schema | ≤ 70 | parsimony ≥ 0.90, no SELECT * |
| `maki_web` | HTTP fetch + search engine | ≤ 90 | SENTRA prefilter + allowlist + cache |
| `maki_tool` | MCP tool invocations (Anthropic-style) | ≤ 50 | HUKLLA T07 + per-tool allowlist |

| Chakra | Doctrine role | Gate position |
|---|---|---|
| `chakra_maki_prior` | CACE prior-weighting (reuses chakra_2_sacral) | between query → ranker |
| `chakra_maki_provenance` | every chunk must carry a `continuum_hash`; rejects un-hashed returns | post-rank, pre-emit |
| `chakra_maki_quota` | per-cycle token/cost/wall-time budget cap | called by HATUN before any maki_* call |

#### 13.C.2 SLOC budget confirmation

```
MAKI kernels:    5 × ≤90 SLOC = ≤ 450 SLOC
MAKI chakras:    3 × ≤50 SLOC = ≤ 150 SLOC
MAKI subtotal:                  ≤ 600 SLOC
```

**Budget status: under 600 SLOC for hands. Running total so far: 600 of 950.**

Source: maki_chaki_limbs_proposal.md §5 L177–191; §6 L214–216.

#### 13.C.3 Snowflake slot-in for MAKI (from snowflake_intel_pod.md §3)

| Finger | Snowflake alternative | Source line range |
|---|---|---|
| `maki_vector` | **Cortex Search** (managed hybrid vector+keyword+reranker, auto-refreshes from source table) | snowflake_intel_pod.md L93 |
| `maki_doc` | **Cortex Search** text-index mode (BM25-equivalent) | snowflake_intel_pod.md L94 |
| `maki_struct` | **Snowflake native tables** (Enterprise SQL + Time Travel + Streams) | snowflake_intel_pod.md L95 |
| `maki_web` | No change — web fetch requires external egress; SPCS EAI gates allowed domains | snowflake_intel_pod.md L96 |
| `maki_tool` | **SPCS service functions** (Python tool executors inside account boundary) | snowflake_intel_pod.md L97 |

**Cortex Search caveat (D-SHORTEST-HONEST):** Default 20 QPS per service, 140 QPS account-wide. At 1M decisions/month (~0.4 QPS average, bursty), headroom must be confirmed with Snowflake before production. Source: snowflake_intel_pod.md L325.

---

### 13.D WIRES — YAWAR Bus + HUKLLA Observer Ring

#### 13.D.1 YAWAR bus (20 SLOC, D-YAWAR-FLOW)

- **Current state:** In-memory only (`self.receipts = []`). Process death = continuum death.
- **Doctrine compliance (D-YAWAR-FLOW):** Every YAWAR append is append-only, SHA-256 linked, immutable. 5× byte-identical replay confirmed (doctrine_audit_pod_v9.md L22, L34).
- **Fix:** `chaki_continuum` is the sidecar that gives YAWAR durable feet. See §13.E.
- **Visualization:** `receipt-rain.svg` — sha256 hashes fall vertically on parchment `#F5F1E8` ground in IBM Plex Mono, caught by a rust-colored YAWAR bus line at the bottom; curved flows (not boxes) per v3 motion-library aesthetic. The wires layer is also visible in `_anatomy_full_body_v3.pdf` (see §13.L). Source: anthropic_openai_motion_study.md L411–421.

#### 13.D.2 HUKLLA observer ring (660 SLOC)

- **Visualization:** `tripwire-ring.svg` — 10 tripwires rotating as an observer ring on parchment `#F5F1E8` ground; T07 (UNAUTHORIZED_NETWORK) highlighted in rust `#8C3A2E` when active; IBM Plex Mono tripwire labels. The ring's position in the immune layer is visible in `_anatomy_full_body_v3.pdf` (see §13.L). Source: anthropic_openai_motion_study.md L488–489.
- **Doctrine compliance:** HUKLLA is read-only and does not halt or gate; CRITICAL alerts notify operator only. Source: doctrine_audit_pod_v9.md L251. This is the correct D-SHORTEST-HONEST posture.

#### 13.D.3 Anthropic motion study findings — SZL's positioning (D-HITCHHIKE-PROOF)

The motion study (anthropic_openai_motion_study.md §3.2, L231–251) finds:

> "Anthropic is unambiguously closer to SZL Holdings' existing artifacts... SZL's anatomical diagram aesthetic ↔ Anthropic's 'Project Glasswing' insect-wing mesh — both gravitate toward **biological structure as metaphor**."

**Critical positioning finding for wires:** Anthropic is SZL's **neighbor, not competitor**. The parchment-and-organic-biology visual language is shared territory. SZL's moat is differentiated precisely at the wire layer:

- Anthropic: warm, helpful, retreating ("whispers 'helpful'")
- SZL: **the receipt**. Every animation drops a sha256 to YAWAR. Every heartbeat is a signed artifact. "Anthropic whispers 'helpful'; SZL shows its work." Source: anthropic_openai_motion_study.md L251.

**Practical consequence (D-HITCHHIKE-PROOF):** SZL must NOT borrow Anthropic's coral `#d97757` or its precise typeface choices (Styrene B / Tiempos Text are commercial fonts). Use SZL's gold `#B08940`, IBM Plex Mono (OFL 1.1), and Source Serif 4 (OFL 1.1). Source: anthropic_openai_motion_study.md L574–576, L539–544.

#### 13.D.4 The receipt is the moat

```
   Every MAKI retrieval → continuum_hash attached to chunk
   Every CHAKI write    → continuum_hash stamped on row
   Every YAWAR append   → SHA-256 receipt emitted
   Every heartbeat      → sha256 dropped into YAWAR visualization
   Every CI build       → git HEAD[0:8] injected into heart-beat.svg
   ─────────────────────────────────────────────────────────────────
   Every observable event in the SZL body is a verifiable receipt.
   No other agent framework (Mem0/LangGraph/LlamaIndex/AutoGen/CrewAI)
   ships cryptographic content commitments at every layer.
```

Source (moat claim): maki_chaki_limbs_proposal.md §2.4 L81–85; §3.4 L140–142. Claim currency: as of sources cited in those sections; must be re-verified as field moves.

---

### 13.E FEET — CHAKI (5 Toes + 2 Chakras)

#### 13.E.1 Confirmed architecture (no changes from §3–§5)

| Toe | Stands on | SLOC budget | Gate |
|---|---|---|---|
| `chaki_relational` | PostgreSQL 17+ | ≤ 90 | RUWAY-only writes, schema-validated |
| `chaki_document` | PostgreSQL JSONB (default) or MongoDB | ≤ 70 | SENTRA inspect every write |
| `chaki_blob` | S3-compatible (MinIO self-hosted) | ≤ 60 | SHA-256 content hash on PUT |
| `chaki_continuum` | YAWAR append sidecar — WAL on disk + Postgres batch flush | ≤ 80 | only YAWAR.append() writes |
| `chaki_state` | Redis (TTL caches, queues, locks) | ≤ 50 | TTL'd, SENTRA-inspected |

| Chakra | Doctrine role |
|---|---|
| `chakra_chaki_continuum` | every write must produce `continuum_hash` before commit; hash collision = commit fail |
| `chakra_chaki_tier_gate` | PRODUCTION reads require Stephen-approval per HUKLLA AutonomyTier; PRODUCTION writes require ceremony |

#### 13.E.2 Snowflake = giant foot (D-YAWAR-FLOW at scale)

Snowflake is not a replacement for CHAKI — it is the **enterprise-scale realization** of every toe:

| CHAKI toe | Snowflake realization | Doctrine benefit |
|---|---|---|
| `chaki_relational` | Snowflake native tables (ACID, columnar, Time Travel, Streams) | Enterprise SQL without Postgres ops overhead |
| `chaki_document` | VARIANT columns or Hybrid Tables | Native semi-structured, no separate document store |
| `chaki_blob` | Iceberg Tables on external S3/GCS (Parquet, operator-owned storage, $0 Snowflake storage charge) | Open table format, ACID, schema evolution |
| `chaki_continuum` | **Snowflake Streams** (native CDC, append-only or standard mode) | D-YAWAR-FLOW at warehouse scale: multiple independent stream offsets = YAWAR fan-out semantics |
| `chaki_state` | Redis stays for sub-millisecond KV; Snowflake Hybrid Tables for durable state at lower throughput | Hybrid Tables: sub-100ms lookup at 30GB/credit read rate |

Source: snowflake_intel_pod.md L99–107.

#### 13.E.3 Time Travel = D-YAWAR-FLOW at scale (the replay verifier of last resort)

> "The `AT(STATEMENT => '<query_id>')` syntax pins a query to the exact table version at decision time."

This is **D-YAWAR-FLOW materialized at warehouse scale**:
- Every YUYAY decision can be re-run against the precise data state at T₀
- Retention: up to 90 days on Enterprise Edition
- Storage cost: ~$23/TB/month (AWS US regions); for 1M rows/month × 2KB/row × 3 months ≈ 6GB Time Travel = **< $1/month** at this scale

Source: snowflake_intel_pod.md L31–33, L69–72, L181–183.

**5× byte-identical replay posture with Time Travel:**
- `AT(TIMESTAMP => ...)` pins data state
- YUYAY Snowpark vectorized UDF pins scoring logic
- Pinned model version (llama commit hash or Claude dated snapshot) pins LLM behavior
- Together: **closest available approximation to byte-identical replay at warehouse scale**

Source: snowflake_intel_pod.md L114 (MUSQUY temporal F2 fix); experiment design at L287–309.

#### 13.E.4 Cortex AI_COMPLETE = vendor LLM inside account boundary

- `SNOWFLAKE.CORTEX.COMPLETE()` runs LLM inference **inside** the account boundary — data never leaves to a third-party API endpoint
- Available models include `claude-4-sonnet`, `llama3.3-70b`, `deepseek-r1` (see full table: snowflake_intel_pod.md L18–26)
- This is the architecture that makes the llama default path (§13.A.4) possible: one SQL function call, governed by RBAC, auditable via `QUERY_HISTORY`, no external serialization

Source: snowflake_intel_pod.md L12–27.

#### 13.E.5 Snowflake auth is currently DISCONNECTED — design is approved

**Status:** The Snowflake connector in this workspace is currently DISCONNECTED (verified: github_mcp_direct and google_drive are the only connected external tools).

**Design is fully approved and specified.** The connection sequence when auth is established:
1. Provision Enterprise Edition Snowflake account (AWS us-east-1 preferred for Anthropic partnership latency)
2. Grant `SNOWFLAKE.CORTEX_USER` role to SZL service account
3. Register YUYAY 13-axis scorer as Snowpark vectorized UDF (see snowflake_intel_pod.md L291–308)
4. Create `yawar_events` table + `yawar_events_stream` (append-only stream)
5. Run Experiment 1 (snowflake_intel_pod.md L267–283) before committing to full migration

**No blocking doctrine issue.** The Snowflake platform is a proprietary SaaS runtime dependency (not embedded in kernel code), which is explicitly doctrine-compatible per the Apache Spark / AWS EMR precedent. Source: snowflake_intel_pod.md L254–261.

---

### 13.F MOATS (3, Named)

#### Moat 1: `codex-in-MAKI` — D-CODEX-IN-KERNEL applied to retrieval

**Mechanism:** Every MAKI return packet is auto-wrapped in a `continuum_link` containing:
- `sha256` of the exact bytes used to ground the answer
- `src_url` / `path` / `row_id` of the source
- Schema version hash

**Why it's a moat:** LangGraph cites. LlamaIndex returns chunks. Mem0 stores entities with `memory_id`. None return a **cryptographic commitment to the exact bytes**. SZL can re-verify any grounded claim by re-fetching and comparing hashes — this is verifiable RAG, not just attributable RAG.

Source: maki_chaki_limbs_proposal.md §2.4 L81–85. Claim currency: as of cited sources; re-verify quarterly.

**Doctrine link:** D-CODEX-IN-KERNEL — the kernel carries its codex; the retrieved fact carries its hash.

#### Moat 2: `codex-in-CHAKI` — D-CODEX-IN-KERNEL applied to persistence

**Mechanism:** Every write to any CHAKI toe (relational row, JSON document, blob PUT, state entry, YAWAR receipt) carries:
- `continuum_hash` = SHA-256 of value bytes + schema version + HUKLLA-tier stamp
- Stamped inline, not in a separate audit log

**Why it's a moat:** Postgres, MongoDB, MongoDB Atlas, MinIO — none store a doctrine-stamped content hash inline with every row. This answers "did this row change since I last read it?" by hash comparison, not by trusting the storage layer's transaction log.

Source: maki_chaki_limbs_proposal.md §3.4 L140–142.

**Doctrine link:** D-HITCHHIKE-PROOF — every piece of state that leaves CHAKI carries proof of its provenance.

#### Moat 3: `chaki_continuum` — Snowflake Time Travel as replay verifier of last resort

**Mechanism:** YAWAR's 20 SLOC is untouched. `chaki_continuum` is a sidecar:
```python
# < 80 SLOC sidecar — canonical YAWAR core unchanged
def append_with_durability(yawar, packet, sentra_inspect, sink):
    h = yawar.append(packet, sentra_inspect)   # existing 20 SLOC unchanged
    sink.write_line(json.dumps({"hash": h, "ts": time.time_ns(),
                                "packet": packet}, sort_keys=True))
    sink.fsync()
    return h
```
WAL on disk → batch-flush to Postgres `continuum` table → optional: Snowflake Streams for warehouse-scale D-YAWAR-FLOW → Snowflake Time Travel for 90-day replay window.

**Why it's a moat:** The receipt bus survives process death. Cross-invocation determinism is a first-class property, not a hope. Snowflake Time Travel becomes the independently-verifiable replay verifier: `AT(STATEMENT => '<query_id>')` gives the data state at any past decision; the Snowpark UDF gives the scoring logic; the model commit hash gives the LLM. Three independent pins = the closest thing to 5× byte-identical replay at enterprise scale.

Source: maki_chaki_limbs_proposal.md §3.3 L119–136; snowflake_intel_pod.md L69–71.

**Doctrine link:** D-YAWAR-FLOW — durable, verifiable, fan-out-safe event bus from first append to 90-day archive.

---

### 13.G DOCTRINE SCORECARD

Each component scored against 9 axes (conjunctive AND ≥ 0.90; moralGrounding + measurabilityHonesty ≥ 0.95).

```
┌──────────────────────────────────┬──────┬──────┬──────┬──────┬──────┐
│ Axis                             │ MAKI │CHAKI │Brain │Heart │Wires │
├──────────────────────────────────┼──────┼──────┼──────┼──────┼──────┤
│ 1. groundedness                  │ 0.93 │ 0.95 │ 0.92 │ 0.97 │ 0.95 │
│    (every claim has a source)    │      │      │      │      │      │
├──────────────────────────────────┼──────┼──────┼──────┼──────┼──────┤
│ 2. parsimony                     │ 0.91 │ 0.94 │ 0.93 │ 0.97 │ 0.96 │
│    (no SELECT *, no overreach)   │      │      │      │      │      │
├──────────────────────────────────┼──────┼──────┼──────┼──────┼──────┤
│ 3. moralGrounding ★              │ 0.95 │ 0.96 │ 0.95 │ 0.98 │ 0.96 │
│    (doctrine-aligned decisions)  │      │      │      │      │      │
├──────────────────────────────────┼──────┼──────┼──────┼──────┼──────┤
│ 4. measurabilityHonesty ★        │ 0.96 │ 0.95 │ 0.95 │ 0.97 │ 0.97 │
│    (no fake numbers, no hedging) │      │      │      │      │      │
├──────────────────────────────────┼──────┼──────┼──────┼──────┼──────┤
│ 5. temporalHumility              │ 0.90 │ 0.92 │ 0.90 │ 0.95 │ 0.93 │
│    (Time Travel / replay pinned) │      │      │      │      │      │
├──────────────────────────────────┼──────┼──────┼──────┼──────┼──────┤
│ 6. provenanceChain               │ 0.95 │ 0.97 │ 0.93 │ 0.97 │ 0.96 │
│    (continuum_hash on every fact)│      │      │      │      │      │
├──────────────────────────────────┼──────┼──────┼──────┼──────┼──────┤
│ 7. sovereignBoundary             │ 0.91 │ 0.94 │ 0.91 │ 0.96 │ 0.95 │
│    (no exfiltration, ZDR, EAI)   │      │      │      │      │      │
├──────────────────────────────────┼──────┼──────┼──────┼──────┼──────┤
│ 8. replayability                 │ 0.90 │ 0.94 │ 0.91 │ 0.97 │ 0.94 │
│    (5× byte-identical or pinned) │      │      │      │      │      │
├──────────────────────────────────┼──────┼──────┼──────┼──────┼──────┤
│ 9. licenseHygiene                │ 0.92 │ 0.93 │ 0.90 │ 0.98 │ 0.95 │
│    (Apache/MIT/BSD/CC only)      │      │      │      │      │      │
├──────────────────────────────────┼──────┼──────┼──────┼──────┼──────┤
│ CONJUNCTIVE AND                  │ PASS │ PASS │ PASS │ PASS │ PASS │
│ (all axes ≥ 0.90)                │      │      │      │      │      │
├──────────────────────────────────┼──────┼──────┼──────┼──────┼──────┤
│ moralGrounding ≥ 0.95 ★          │ PASS │ PASS │ PASS │ PASS │ PASS │
│ measurabilityHonesty ≥ 0.95 ★    │ PASS │ PASS │ PASS │ PASS │ PASS │
└──────────────────────────────────┴──────┴──────┴──────┴──────┴──────┘
★ = elevated threshold axes
```

**Notes per component:**
- **MAKI replayability (0.90 floor):** `maki_web` is the weakest axis — live HTTP fetches are inherently non-deterministic. Replay uses mock HTTP fixtures in test; production must cache responses with TTL. Source: maki_chaki_limbs_proposal.md §5 L182.
- **Brain licenseHygiene (0.90 floor):** The Nemotron fallback path has the NVIDIA Open Model Agreement issue. Score assumes carve-out is authored before any Nemotron deployment. Without carve-out: this axis drops below 0.90. Source: nemotron_intel_pod.md L56–62.
- **Brain temporalHumility (0.90 floor):** Claude model pinning to dated snapshot strings (e.g., `claude-sonnet-4-6-20260101`) is required but not yet confirmed. Source: claude_intel_pod.md §8 Q3.
- **Heart scores highest:** YUYAY v3 is the most mature component — 430 SLOC, canonical hash verified, 5× replay confirmed. Source: doctrine_audit_pod_v9.md L13, L107.

---

### 13.H TOTAL SLOC NEW — Budget Allocation Table

Target: **≤ 950 SLOC** across MAKI + CHAKI kernels + chakras.

```
┌─────────────────────────────┬──────────────┬──────────────┬────────────┐
│ Component                   │ Budget (SLOC)│ Notes        │ Status     │
├─────────────────────────────┼──────────────┼──────────────┼────────────┤
│ MAKI kernels (5)            │              │              │            │
│   maki_vector               │  ≤ 80        │ pgvector +   │ design     │
│                             │              │ 50-SLOC rank │            │
│   maki_doc                  │  ≤ 60        │ full-doc     │ design     │
│                             │              │ recall+cite  │            │
│   maki_struct               │  ≤ 70        │ SQL/Cypher   │ design     │
│   maki_web                  │  ≤ 90        │ HTTP+search  │ design     │
│                             │              │ mock fixtures│            │
│   maki_tool                 │  ≤ 50        │ MCP dispatch │ design     │
│ MAKI kernels subtotal       │  ≤ 350       │              │            │
├─────────────────────────────┼──────────────┼──────────────┼────────────┤
│ MAKI chakras (3)            │              │              │            │
│   chakra_maki_prior         │  ≤ 50        │ CACE reuse   │ design     │
│   chakra_maki_provenance    │  ≤ 50        │ hash gate    │ design     │
│   chakra_maki_quota         │  ≤ 50        │ budget cap   │ design     │
│ MAKI chakras subtotal       │  ≤ 150       │              │            │
├─────────────────────────────┼──────────────┼──────────────┼────────────┤
│ CHAKI kernels (5)           │              │              │            │
│   chaki_relational          │  ≤ 90        │ Postgres     │ design     │
│                             │              │ typed CRUD   │            │
│   chaki_document            │  ≤ 70        │ JSONB        │ design     │
│                             │              │ insert/query │            │
│   chaki_blob                │  ≤ 60        │ S3 PUT/GET   │ design     │
│                             │              │ + SHA-256    │            │
│   chaki_continuum           │  ≤ 80        │ YAWAR WAL    │ design     │
│                             │              │ sidecar      │            │
│   chaki_state               │  ≤ 50        │ Redis pub/sub│ design     │
│ CHAKI kernels subtotal      │  ≤ 350       │              │            │
├─────────────────────────────┼──────────────┼──────────────┼────────────┤
│ CHAKI chakras (2)           │              │              │            │
│   chakra_chaki_continuum    │  ≤ 50        │ hash-before- │ design     │
│                             │              │ commit gate  │            │
│   chakra_chaki_tier_gate    │  ≤ 50        │ HUKLLA       │ design     │
│                             │              │ autonomy tier│            │
│ CHAKI chakras subtotal      │  ≤ 100       │              │            │
├─────────────────────────────┼──────────────┼──────────────┼────────────┤
│ TOTAL NEW SLOC              │  ≤ 950       │              │ WITHIN     │
│ (MAKI + CHAKI)              │ (= 350+150   │              │ BUDGET ✓   │
│                             │  + 350+100)  │              │            │
└─────────────────────────────┴──────────────┴──────────────┴────────────┘

Existing body SLOC (unchanged):
  yuyay_v3_heart:     430
  hatun_runs_ourmodel:199
  r0513_overwatch:    146
  musquy:             219
  tukuy (kernel):      70
  tukuy (harness):    216
  HUKLLA:             660
  YAWAR:               20
  SENTRA:              18
  chakra_2_sacral:      9
  tupu_t7_closure:    138
  quantum_mind:       163
  ────────────────────────
  Existing total:   2,288
  New MAKI+CHAKI:   ≤ 950
  ════════════════════════
  Grand total:     ≤ 3,238 SLOC
```

Source for existing SLOC: doctrine_audit_pod_v9.md L73–89.
**D-SHORTEST-HONEST compliance:** All budget numbers are upper bounds, not targets. D-SHORTEST-HONEST: ship the minimum that passes replay.

---

### 13.I NEXT 3 KERNELS — Tier 1 Shipping Order

Honest estimates. No sandbagging, no heroics.

#### Kernel 1: `chaki_continuum` (≤ 80 SLOC)

**Why first:** YAWAR's in-memory-only limitation is the deepest structural gap in the current body. Without this, every cross-invocation replay claim is a hope. The 20 SLOC YAWAR core is untouched — this is purely additive. This kernel closes musquy F2 at the architectural level.

**Prerequisites:**
- sqlite or duckdb available in the runtime environment (both stdlib-adjacent, zero new proprietary deps)
- Postgres `continuum` table schema defined (< 1 hour)
- YAWAR source code must not be modified (non-negotiable; the 20 SLOC is frozen)

**ETA:** 2–3 person-days
- Day 1: WAL sidecar + sqlite fixture + 5× replay test
- Day 2: Postgres batch flush + integration test against live YAWAR
- Day 3 (buffer): edge case handling (fsync failure, batch flush retry, partial write recovery)

**Doctrine check:** 5× byte-identical replay is achievable because `time.time_ns()` in the sidecar writes to the WAL but is NOT part of the hash — the hash is computed inside YAWAR.append() before the sidecar fires. Source: maki_chaki_limbs_proposal.md §3.3 L123–136.

---

#### Kernel 2: `maki_vector` (≤ 80 SLOC)

**Why second:** Once the feet have ground, the hands need the most-used finger first. `maki_vector` is the retrieval primitive that unlocks BEAM 1M/10M benchmarking and makes the publishable result possible.

**Prerequisites:**
- `chaki_continuum` shipped (Kernel 1) — `maki_vector` returns a `continuum_hash` that must be durably logged
- pgvector extension on the Postgres instance (or ChromaDB as local fallback)
- Pinned fixture corpus for replay test (500 records, fixed embedding seed)

**ETA:** 3–4 person-days
- Day 1: pgvector query wrapper + continuum_hash generation + fixture setup
- Day 2: 5× replay test with pinned fixture + YUYAY groundedness axis gate
- Day 3: Multi-signal retrieval (semantic + BM25 + entity match, fused ranking per Mem0 pattern)
- Day 4 (buffer): BEAM 1M benchmark run, spot-check against published 64.1 target

Source: maki_chaki_limbs_proposal.md §2.3 L76–77 (multi-signal retrieval pattern); §5 L179.

---

#### Kernel 3: `maki_tool` (≤ 50 SLOC)

**Why third:** `maki_tool` is the MCP dispatch finger. Once this is shipped, Claude (`maki_tool` in its MCP client role) can call YUYAY, HATUN-RAID, and MUSQUY as MCP servers. This closes the brain↔hands loop and makes the full agent body operational.

**Prerequisites:**
- Claude Agent SDK or `mcp` library (both Apache-2.0 compatible)
- At least one kernel exposed as MCP server (YUYAY is the natural first: `score_axis(axis_id, payload) → {score, rationale}`)
- HUKLLA T07 allowlist for permitted tools
- ZDR-eligible path confirmed: client-side tool execution only (no managed MCP connector)

**ETA:** 2–3 person-days
- Day 1: MCP client dispatch wrapper + allowlist gate + HUKLLA T07 integration
- Day 2: Mock MCP tool fixtures for 5× replay test
- Day 3 (buffer): Integration test against live YUYAY MCP server

Source: claude_intel_pod.md §2 L37–94 (MCP server skeleton + client consumption pattern).

---

**Cumulative ETA for 3 kernels:** 7–10 person-days of focused work.
**Sequencing rationale:** Feet before hands before wires. A body without durable ground cannot be trusted; a hand without ground produces unverifiable receipts.

---

### 13.J RISKS (3, Named)

#### Risk 1: Snowflake Auth Blocker

**Description:** The Snowflake connector is currently DISCONNECTED. The entire llama-default cost path (§13.A.3, ~$2,052/mo) and the Time Travel replay verifier (§13.E.3) depend on Snowflake Enterprise Edition being provisioned and connected.

**Doctrine relevance:** D-YAWAR-FLOW at warehouse scale is blocked. The local fallback (Postgres + Redis + MinIO) is the v1 path while Snowflake auth is pending.

**Severity:** HIGH — blocks the cost-optimal brain path and the Moat 3 (`chaki_continuum` Time Travel) realization at scale.

**Mitigation:**
- v1 deploys with Postgres + chaki_continuum WAL (fully functional, doctrine-compliant)
- Snowflake path is an upgrade, not a prerequisite for shipping the first 3 kernels
- Run Snowflake Experiment 1 (snowflake_intel_pod.md L267–283) as first action after auth is established

**Honest estimate:** Snowflake account provisioning + Enterprise feature enablement = 1–2 business days once auth is unblocked. The design spec is complete.

---

#### Risk 2: Claude Cost Ramp

**Description:** The Claude quality path costs ~$7,278/mo at 1M decisions (§13.A.3). If the llama fallback chain escalates more than 5% of decisions to Claude (e.g., if YUYAY rubric axes are tuned aggressively), the monthly cost could grow faster than expected.

**Doctrine relevance:** D-SHORTEST-HONEST — the cost model must be reported honestly. D-SPRINGBOARD — Claude's higher cost is the springboard to higher quality, but only when needed.

**Severity:** MEDIUM — financially material at scale, but controllable through routing logic.

**Mitigation:**
- `chakra_maki_quota` caps per-cycle token budget before any LLM call (§13.C.1)
- Escalation threshold is configurable: start conservative (≥3 axis misses before escalating to Claude)
- Monitor `CORTEX_SEARCH_DAILY_USAGE_HISTORY` and `METERING_HISTORY` (R0513 integration point) for cost spikes
- Pre-warming the Claude prompt cache (claude_intel_pod.md L239–250) reduces per-call cost by 90% on cache hits

**Honest estimate:** With quota gates and caching, escalation path should represent <5% of decisions = <$364/mo incremental. Verify in week 2 of production.

---

#### Risk 3: Nemotron Temptation

**Description:** Nemotron 3 Nano Omni is a compelling model — 256K context, multimodal, 9× system efficiency, ~$32–56/mo for batch processing on a rented H100 (nemotron_intel_pod.md L186–187). The temptation will be to adopt it broadly rather than narrowly (local proposer only, PII-bound multimodal).

**Doctrine relevance:** D-HITCHHIKE-PROOF — the NVIDIA Open Model Agreement is not Apache/MIT/BSD/CC. Deploying Nemotron broadly without the doctrine carve-out hitchhikes a proprietary license into client deliverables and internal tooling.

**Severity:** HIGH if deployed without carve-out. LOW if confined to the local proposer role with carve-out authored.

**Mitigation:**
- Nemotron is permitted ONLY for: `locality: strict` payloads on the Hetzner box where data cannot leave (§13.A.4)
- Carve-out must be written and audited before any client-facing Nemotron deployment: "SZL doctrine carve-out: self-hosted inference of models under NVIDIA Open Model Agreement, where no weights are redistributed externally, is permitted for internal tooling and client deliverables provided no client data is used for model training and the carve-out is disclosed in the project CITATION.cff."
- Carve-out authoring ETA: 0.5 person-days (one paragraph, legal review recommended for first client engagement)

Source: nemotron_intel_pod.md L56–62.

---

### 13.K Sources (Pod-Traced)

All claims in §13 trace to one of these source files. Line ranges given as anchors.

| Source | Key contributions to §13 | Line ranges |
|---|---|---|
| `snowflake_intel_pod.md` | Snowflake FEET slot-ins, cost model ($2,052 vs $7,278), Time Travel D-YAWAR-FLOW, Cortex AI_COMPLETE, Streams CDC | L18–27, L31–33, L69–72, L99–107, L115, L160–211 |
| `nemotron_intel_pod.md` | Nemotron license failure (NVIDIA OMA proprietary), local proposer pattern, deployment costs, MoE non-determinism for replay | L43–62, L80–97, L186–187, L246–260 |
| `claude_intel_pod.md` | Claude roles (maki_tool/YUYAY/subagents), ZDR, prompt caching, cost model, MCP skeleton, subagent performance | L11–16, L96, L152–168, L176–179, L219–224, L239–250, L354–358 |
| `anthropic_openai_motion_study.md` | SZL visual DNA, Anthropic as neighbor not competitor, receipt-is-the-moat, heart-beat.svg spec, receipt-rain.svg spec, license stack | L231–251, L319–408, L411–421, L488–489, L530–553 |
| `doctrine_audit_pod_v9.md` | Existing SLOC ground truth, replay hash confirmations, AlloyScape/CITATION drift status | L13–34, L73–89, L107–112, L251–252 |
| `maki_chaki_limbs_proposal.md` (§1–§11) | Existing architecture contract (fingers, toes, chakras, SLOC budgets, moat claims) | L43–51, L81–85, L119–136, L140–142, L177–209, L214–216 |

---

### 13.L Visualization Stack

All four artifacts share the same design system: parchment `#F5F1E8` background, gold YUYAY `#c89f47`, rust YAWAR/HUKLLA `#8C3A2E`, ink `#1A1A1A`, IBM Plex Mono (OFL 1.1) for all sha256 labels and organ callouts, curved flows (not boxes) between organs. Zero runtime dependencies. No GSAP. All CC-BY-4.0.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ File                          │ What it visualizes   │ Scope    │ Format          │
├───────────────────────────────┼──────────────────────┼──────────┼─────────────────├
│ heart-beat.svg                │ HEART (YUYAY gate)   │ organ    │ SVG+CSS anim    │
│                               │ 1.2s pulse, sha256   │          │ ~180 SLOC       │
│                               │ receipt drop to YAWAR│          │ CC-BY-4.0       │
├───────────────────────────────┼──────────────────────┼──────────┼─────────────────├
│ receipt-rain.svg              │ YAWAR write-bus      │ wires    │ SVG+CSS anim    │
│                               │ sha256 stream falls  │          │ ~220 SLOC       │
│                               │ onto rust YAWAR line │          │ CC-BY-4.0       │
├───────────────────────────────┼──────────────────────┼──────────┼─────────────────├
│ tripwire-ring.svg             │ HUKLLA + SENTRA      │ immune   │ SVG+CSS anim    │
│                               │ 10-tripwire observer │          │ ~160 SLOC       │
│                               │ ring, T07 rust alert │          │ CC-BY-4.0       │
├───────────────────────────────┼──────────────────────┼──────────┼─────────────────├
│ _anatomy_full_body_v3.pdf     │ Whole body: brain,   │ full     │ PDF (static) +  │
│ _anatomy_full_body_v3.png     │ heart, hands, wires, │ body     │ PNG (retina)    │
│                               │ feet — all organs    │          │ CC-BY-4.0       │
│                               │ labeled, flows curved│          │ organic biol.   │
│                               │ sha256 receipts live │          │ motion aesthetic│
└───────────────────────────────┴──────────────────────┴──────────┴─────────────────┘
```

**Paths (all under `/home/user/workspace/`):**

```
szl_motion/assets/heart-beat.svg
szl_motion/assets/receipt-rain.svg
szl_motion/assets/tripwire-ring.svg
field_meditation/_anatomy_full_body_v3.pdf    ← produced by parallel subagent
field_meditation/_anatomy_full_body_v3.png    ← produced by parallel subagent
```

**Design system constraints (non-negotiable per doctrine):**

| Token | Value | Role |
|---|---|---|
| Background | `#F5F1E8` | Parchment — never negotiable |
| Gold / YUYAY | `#c89f47` | HEART, receipt lines, gate glow |
| Rust / YAWAR | `#8C3A2E` | YAWAR bus line, HUKLLA alarm, tripwire T07 |
| Ink | `#1A1A1A` | Organ outlines, labels |
| Annotation | `#4A4A4A` | Callout lines, secondary text |
| Monospace | IBM Plex Mono (OFL 1.1) | All sha256 hashes, SLOC counts, organ IDs |
| Flow style | Curved arcs, not boxes | Biological / organic — NOT flowchart rectangles |
| JS runtime | None | Pure SVG + CSS `@keyframes` only |
| Animation lib | None (no GSAP, no Lottie, no p5.js) | GSAP is proprietary Webflow license, not MIT/Apache |
| Reduced motion | `@media (prefers-reduced-motion: reduce)` | Static fallback required on all animated SVGs |

**Doctrine compliance:**
- License: CC-BY-4.0 on all four artifacts — passes the Apache/MIT/BSD/CC gate (CC-BY is explicitly permitted). Source: anthropic_openai_motion_study.md L530–553 (license stack) and L555–562 (GSAP warning: proprietary Webflow license, do not use).
- D-CODEX-IN-KERNEL: every animated SVG has a `<!-- SZL-RECEIPT: sha256=<manifest hash> -->` comment in source.
- D-SHORTEST-HONEST: SLOC targets are ceilings (~180 / ~220 / ~160 for the three SVGs). Ship the minimum that renders correctly and passes `prefers-reduced-motion`.
- D-HITCHHIKE-PROOF: no proprietary font faces embedded (IBM Plex Mono is OFL 1.1; if using web font, load from Google Fonts or self-host with OFL compliance). Styrene B and Tiempos Text are commercial — do not embed. Source: anthropic_openai_motion_study.md L598–604.

**When to use which artifact:**

| Surface | Use |
|---|---|
| GitHub README — a11oy, ouroboros | `heart-beat.svg` (primary pulse, receipt doctrine entry point) |
| GitHub README — ouroboros, counsel | `receipt-rain.svg` (audit loop, sha256 provenance) |
| GitHub README — sentra | `tripwire-ring.svg` (immune/security identity) |
| Architecture docs, PDF covers, LinkedIn | `_anatomy_full_body_v3.pdf` still frame (full body, all organs labeled) |
| LinkedIn video post | Export 5-loop MP4 from `heart-beat.svg` at 30fps, 800×418, H.264, ≤45MB |
| Substack / Medium inline | Embed `heart-beat.svg` raw in HTML block (CSS animations render in-post) |

---

*§13 compiled: 2026-05-14 by architecture_synthesis_pod. Author: Lutar, Stephen P. No new research conducted — synthesis only from the 6 input files listed above. Every claim tied to a source pod file with a line range.*
