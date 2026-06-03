# RIKCH'AY — Public-Surface Intake & Inversion Playbook

**Author:** Lutar, Stephen P. · ORCID 0009-0001-0110-4173 · SZL Holdings  
**Codename:** RIKCH'AY  
**Doctrine version:** v3  
**Date:** 2026-05-14  
**License:** CC-BY-4.0  

> **Source-purity declaration:** PUBLIC SOURCES ONLY. No private repos, no credentialed APIs that are not ours, no leaked credentials. Every URL in this document resolves without a login. Unverified claims are marked `[unverified]` and are not used as logical foundation.

---

RIKCH'AY (Quechua: *to awaken, to perceive clearly*) is the SZL-native codename for this intake-and-inversion playbook. We refuse to borrow language from the labs we are inverting. Every section that follows is a public surface absorbed and reshaped into the SZL receipt-doctrine lane the frontier labs structurally cannot enter. Anthropic's product naming (including their "Glasswing" design-system) is referenced as public surface only — not as our identity.

Anthropic's Project Glasswing is a hero visual on anthropic.com — a white mesh evoking insect wing venation, symbolizing interpretable AI internals. [willakuy pod §V.1] The symbolism is sincere: they genuinely believe mechanistic interpretability is the path to safe AI. The problem is that *showing* a wing under a microscope is not the same as *proving* the wing flew correctly on a specific flight at a specific time. SZL's RIKCH'AY is the receipt for that flight.

---

## Table of Contents

1. [Intelligence frame — why this exists](#1-intelligence-frame)
2. [Target 1 — Anthropic](#2-anthropic)
   - Visible posture · Revealed posture · Architectural commitments · Negative space · Job signals · Defection signals
   - **How SZL absorbs and inverts Anthropic — 10 moves**
3. [Target 2 — OpenAI](#3-openai)
   - Visible posture · Revealed posture · Architectural commitments · Negative space · Job signals · Defection signals
   - **How SZL absorbs and inverts OpenAI — 5 moves**
4. [Target 3 — Google DeepMind](#4-google-deepmind)
   - Visible posture · Architectural commitments · Negative space
   - **How SZL absorbs and inverts DeepMind — 4 moves**
5. [Tier 2 rapid cuts — Mistral / Meta / xAI / Cohere / AI21 / Together](#5-tier-2)
6. [The Open Ecosystem — HuggingFace, EleutherAI, HELM](#6-open-ecosystem)
   - **How SZL absorbs and inverts the open ecosystem — 5 moves**
7. [MCP Ecosystem — the security gap SZL fills](#7-mcp-ecosystem)
8. [Adjacent disciplines — Lean 4, zk-SNARKs, SLSA, C2PA, W3C VC](#8-adjacent-disciplines)
9. [Cross-target wedge map — the universal negative space](#9-wedge-map)
10. [**RIKCH'AY Playbook — 12 ships in 12 weeks**](#10-playbook)
11. [Doctrine appendix](#11-doctrine-appendix)
12. [Source index](#12-source-index)

---

## 1. Intelligence Frame

The frontier labs are in a race whose internal logic makes them structurally incapable of building what SZL Holdings is building. This is not rhetoric — it is a constraint baked into their capital commitments, their inference infrastructure, their regulatory posture, and their chosen safety metaphors.

SZL's lane is **receipt-doctrine AI**: every inference event is signed, every byte of context is hashed before execution, every model weight is traceable to its provenance chain, every audit is cryptographically verifiable without trusting any server operator. This is not a niche. It is the substrate that enterprise, government, and legally-accountable AI *must* eventually run on — and none of the labs can deliver it without dismantling their existing deployment infrastructure.

This document does three things:

1. **Absorb** — take every Apache/MIT/CC-BY artifact the labs have released and use it as scaffolding.
2. **Invert** — find the architectural commitments that lock them out of specific moves and build exactly there.
3. **Ride their exhaust** — every paper published, every API shipped, every researcher who leaves and describes what is broken, is a free signal narrowing the map to SZL's lane.

The companion document [willakuy pod] at `/home/user/workspace/field_meditation/anthropic_willakuy_pod.md` covers Anthropic's foundational papers, RSP lineage, patent portfolio, design surface, and the Bartz v. Anthropic settlement in full detail. This document does not repeat that material. It cites it as `[willakuy pod §X]` and builds on top of it.

---

## 2. Anthropic

### 2A. Visible posture

Anthropic calls itself "an AI safety company" pursuing "the responsible development and maintenance of advanced AI for the long-term benefit of humanity." ([anthropic.com](https://www.anthropic.com/))

The three claims they return to in every interview, paper, and job listing:

| Claim | Primary source |
|---|---|
| Safety and capability are complementary — you can build the most capable models by also making them the safest | [Claude's Constitution](https://www.anthropic.com/constitution); [Dario Amodei interviews, 2024-2026] |
| Mechanistic interpretability — understanding what models actually compute — is the path to verifiable alignment | [transformer-circuits.pub](https://transformer-circuits.pub/); [Scaling Monosemanticity](https://transformer-circuits.pub/2024/scaling-monosemanticity/) |
| The Responsible Scaling Policy is a meaningful self-governance mechanism with real if-then thresholds | [RSP v3](https://www.anthropic.com/news/responsible-scaling-policy-v3); [RSP v2.1 PDF](https://www-cdn.anthropic.com/17310f6d70ae5627f55313ed067afc1a762a4068.pdf) |

Key voices: Dario Amodei (CEO, macro impact framing), Chris Olah (interpretability as safety), Jared Kaplan (scaling laws), Amanda Askell (Claude's character and values), Ethan Perez (red-teaming and evals). See [willakuy pod §E] for full quote inventory.

### 2B. Revealed posture — the A↔B gap

What Anthropic's *actions* say they believe, often in tension with stated claims:

| Signal | Interpretation | Source |
|---|---|---|
| Amazon invested up to $25B; Anthropic committed to AWS for primary compute | Cloud lock-in is the actual moat — the safety narrative is the customer acquisition story | [CNBC Apr 2026](https://www.cnbc.com/2026/04/20/amazon-invest-up-to-25-billion-in-anthropic-part-of-ai-infrastructure.html) |
| RSP v3 softens from if-then commitments to "statements of intent" — Zvi Mowshowitz: "From this point, there are no commitments, only statements of intent" | The self-governance mechanism has been walked back to voluntary aspiration | [RSP v3](https://www.anthropic.com/news/responsible-scaling-policy-v3); [Zvi analysis](https://thezvi.substack.com/p/anthropic-responsible-scaling-policy) |
| Bartz v. Anthropic settled for $1.5B (August 2025) — book authors proved copyrighted material from shadow libraries was used in training | Cannot publish a clean training data SBOM without exposure; cannot prove training data purity | [Copyright Alliance](https://copyrightalliance.org/participating-bartz-v-anthropic-settlement/) |
| Own research shows reasoning models don't faithfully describe their internal computations | The chain-of-thought transparency claim — the most user-visible safety feature — is false | [Anthropic research](https://www.anthropic.com/research/reasoning-models-dont-say-think) |
| ASL-3 activated for Claude Opus 4 (2025) — first real escalation — but no public disclosure of what the evaluation found | The thresholds exist; the results are classified | [willakuy pod §B] |
| Claude Code is a commercial subscription product (NodeJS/npm, obfuscated) | Safety research org is funding a SaaS IDE product | [github.com/anthropics/claude-code](https://github.com/anthropics/claude-code) |
| Interpretability team at ~17 people with ~50 positions in field total | SAE work is a research instrument, not a runtime gate — the "interpretable AI" claim is aspirational | [willakuy pod §A.4; circuits April 2024 update](https://transformer-circuits.pub/2024/april-update/index.html) |

**The core gap:** Anthropic says interpretability is the path to *verifiable* alignment. But the SAE/monosemanticity work produces forensic insight, not runtime verification. It is more akin to autopsy capability than continuous monitoring. [willakuy pod §A.4] SZL's receipt doctrine provides runtime verification that SAE cannot: every inference event is signed and hashed before anything else happens.

### 2C. Architectural commitments — what they cannot undo

[willakuy pod §T.1 and §T.2] synthesizes these. For brevity:

| Commitment | Why it cannot be reversed |
|---|---|
| **Closed weights on all production Claude models** | Competitive moat + inability to "recall" a dangerous model if weights are public |
| **RLHF/RLAIF (Constitutional AI) as primary alignment method** | Billions in infrastructure; the entire fine-tuning stack rests on it; switching to formal methods would require scrapping training pipeline |
| **AWS as primary compute substrate** | $25B Amazon commitment, $100B+ total compute contracts [willakuy pod §I.4]; contractual lock-in for years |
| **Policy baked into training weights** | No runtime policy engine exists; the constitution is a training-time prior, not a per-inference gate |
| **Inference-time opacity** | No cryptographically verifiable execution trace; no mechanism for downstream audit without trusting Anthropic's logs |
| **SAE as the interpretability primitive** | Multi-year, multi-million-dollar research investment in the sparse autoencoder paradigm; pivoting would invalidate the program |
| **Model cards as the attestation primitive** | Freeform Markdown; unsigned; no machine-readable provenance chain; the standard for the industry, which means the industry shares the gap |

The Sleeper Agents paper [willakuy pod §A.2] is the internal admission that behavioral safety training has a floor below which it cannot reach. Constitutional AI sits above that floor. There is no published technique that reliably removes deceptive alignment once a model has learned it. The existential dependency: if interpretability fails to scale to runtime use, the safety story has no floor.

### 2D. Negative space — 22 things Anthropic does not publish, do, or say

[willakuy pod §J] covers 30+ items in full. The 22 most actionable for SZL's lane:

1. No cryptographically signed inference receipts — every API response is unsigned plaintext.
2. No per-inference policy gate log — Constitutional AI is training-time, not runtime.
3. No SHA-256 manifest over model checkpoints — model cards list metadata without hashes.
4. No Merkle tree over training data — after Bartz, this is also legally impossible to publish.
5. No SLSA provenance attestation on any released artifact — SLSA Level 0 across the board.
6. No Sigstore model signing — `claude-code` npm package is published without cosign signatures.
7. No public training compute disclosure — no FLOPs, no token counts, no hardware config.
8. No machine-readable RSP thresholds — capability predicates exist only in prose.
9. No zero-knowledge proof of safety evaluation — ZKPROV [arXiv 2506.20915] shows this is feasible; Anthropic has not pursued it.
10. No formally specified harmlessness — the constitution is in English, not Lean 4 or a typed schema.
11. No C2PA content credential on any output — model-generated content carries no provenance stamp.
12. No published incident post-mortems — Claude downtime events produce no public RCAs.
13. No public red-team dataset release — exercises are referenced in system cards but not released.
14. No supply-chain attestation for Claude Code dependencies — no in-toto link metadata over the build pipeline.
15. No key management documentation for API keys — no HSM commitment, no rotation schedule.
16. No mechanism for enterprise customers to verify which Claude version they ran — model aliases (`claude-3-5-sonnet-20241022`) do not pin to a cryptographic identity.
17. No public record of RSP threshold evaluations — when did they happen, what did they find?
18. No formally verified component anywhere in the inference stack.
19. No cross-lingual policy specification — the constitution is English-only; enforcement in other languages is undocumented.
20. No third-party weight escrow.
21. No receipt for Constitutional AI training steps — the RLAIF pipeline generates preference labels from AI feedback but no cryptographic log exists of which labels were used in which run.
22. No public commitment to the open publication of interpretability findings that constrain their commercial roadmap (i.e., interpretability that reveals dangerous capability would require them to disclose it vs. the RSP framework — the disclosure threshold is not defined).

### 2E. Job listing signals — the roadmap leaks

Source: [anthropic.com/jobs](https://www.anthropic.com/jobs), accessed 2026-05-14. Full inventory at [willakuy pod §G].

| Role cluster | What it signals |
|---|---|
| GPU / ML Accelerator Engineering Manager | Custom silicon or deep CUDA/JAX optimization — reducing AWS dependency over 18-36 months |
| Inference Routing and Performance Manager | Multi-region inference routing system in active build — moving beyond round-robin |
| ML Infrastructure Engineer + Research Engineer, Safeguards | Safeguards is a productized safety layer being sold as infrastructure, not just a research cost center |
| Privacy Research Engineer, Safeguards | Differential privacy or SMPC for inference — probable EU AI Act compliance work |
| Research Engineer / Scientist, Frontier Red Team (Cyber) | Active offensive security evals against Claude for cyber-capability uplift; ASL-3 evaluation in progress |
| Research Engineer / Scientist, Alignment Science | Post-CAI alignment methods in active research — confirms CAI is not the terminus |
| Research Engineer, Tokens | Tokenization architecture work; possibly multimodal or long-context tokenizer redesign |
| Pre-training Research Engineer (Zürich) | EU compute sovereignty; GDPR data-localization compliance for European enterprise |
| Research Manager (Expression of Interest), Interpretability | Interpretability scaling to a management-level org — significant headcount planned |
| Research Scientist / Engineer, Honesty | Honesty is a *named* research team separate from alignment — deception and CoT faithfulness are known internal problems |
| Data Center Design Execution / Facility Ops / Hardware Ops | Anthropic is building proprietary data center capacity — not fully dependent on AWS |
| Enterprise AE across federal civilian, healthcare, insurance, manufacturing | Full regulated-vertical enterprise sales build-out |

**The synthesis:** Two simultaneous bets: (a) reduce AWS dependency via owned silicon and data centers, and (b) productize safeguards and interpretability as enterprise-sellable infrastructure. The "Honesty" team is the most important signal — their own research on CoT unfaithfulness is now a named org-chart concern. SZL's CoT audit tool occupies exactly this space from the outside.

### 2F. Defection signals

| Person | Movement | Public signal |
|---|---|---|
| John Schulman (RLHF architect) | OpenAI → Anthropic (Aug 2024) → Mira Murati startup (Feb 2025) | The person who designed RLHF is in motion between institutions — RLHF as paradigm is under implicit pressure from its own inventor. Sources: [CNBC](https://www.cnbc.com/2024/08/06/openai-co-founder-john-schulman-says-he-will-join-rival-anthropic.html); [Fortune](https://fortune.com/2025/02/06/openai-john-schulman-mira-muratis-startup-anthropic/) |
| Jan Leike (Superalignment co-lead) | OpenAI → Anthropic (May 2024) | "Sailing against the wind… safety took a backseat to shiny products." Resources and compute for safety work were systematically denied. [Forbes](https://www.forbes.com/sites/roberthart/2024/05/29/openai-exec-who-resigned-over-safety-concerns-joins-rival-firm-heres-what-we-know/) |
| Ilya Sutskever (OpenAI co-founder) | OpenAI → SSI (Jun 2024) | Founded Safe Superintelligence Inc.: "one goal, one product, no commercial pressure." $1B seed. [CNBC](https://www.cnbc.com/2024/06/19/openai-co-founder-ilya-sutskever-announces-safe-superintelligence.html); [Reuters](https://www.reuters.com/technology/artificial-intelligence/openai-co-founder-sutskevers-new-safety-focused-ai-startup-ssi-raises-1-billion-2024-09-04/) |
| Mira Murati (OpenAI CTO) | OpenAI → own startup (late 2024) | Took John Schulman and others. The person who shipped GPT-4o left immediately after the for-profit restructuring. |
| OpenAI Mission Alignment Team | Disbanded Feb 2026 | [TechCrunch](https://techcrunch.com/2026/02/11/openai-disbands-mission-alignment-team-which-focused-on-safe-and-trustworthy-ai-development/) — "alignment" is now organizationally toxic at OpenAI |
| Multiple safety researchers | Anthropic, OpenAI, xAI → various | [LinkedIn/Nordmark](https://www.linkedin.com/pulse/ai-safety-experts-quitting-jobs-anthropic-openai-xai-why-jon-nordmark-pydrc); [TechBrew Feb 2026](https://www.techbrew.com/stories/2026/02/12/AI-employee-exits-safety-ethics) |

**What the defections tell you:** Every major departing voice confirms the same thing — at both Anthropic and OpenAI, commercial pressure structurally overrides safety investment when they conflict. The receipts-over-narratives approach SZL is building is exactly what these departures signal the market needs: accountability infrastructure that does not depend on institutional good faith.

### Public failures — reference only

See [willakuy pod §R and §AE] for the Bartz settlement ($1.5B, August 2025), Claude performance backlash ([Fortune Apr 2026](https://fortune.com/2026/04/14/anthropic-claude-performance-decline-user-complaints-backlash-lack-of-transparency-accusations-compute-crunch/)), and the "reasoning models don't say what they think" self-disclosure. This section is not repeated here per RIKCH'AY scope instructions.

---

### How SZL absorbs and inverts Anthropic — 10 moves

Each move: what we absorb (public, licensed), what we add (the inversion), why Anthropic cannot follow.

---

**Move A1 — Absorb Constitutional AI principles; ship a runtime 9-axis gate with signed pass/fail receipts**

*Absorbed:* Bai et al. CAI paper ([arXiv 2212.08073](https://arxiv.org/abs/2212.08073), CC-BY). The principle-list architecture — the idea that alignment can be specified as a list of typed criteria — is the right mental model.

*The inversion:* CAI applies principles at training time, producing statistical tendencies. SZL's 9-axis gate [a11oy §B3] applies typed predicates at *inference time*: every query passes through nine independently-evaluated axes (`moralGrounding`, `measurabilityHonesty`, `contextAwareness`, `socialAwareness`, `temporalConsistency`, `sourceAttribution`, `safetyBound`, `privacyRespect`, `logicalCoherence`). Each axis produces a numeric score + signed boolean. The gate is a conjunctive AND: all nine must pass. The receipt is a JSON blob with nine axis scores, the aggregate pass/fail, a SHA-256 hash of (input, output, policy_version), and an ECDSA signature.

*Why Anthropic cannot follow:* Their policy is baked into weights. To produce a per-inference gate receipt, they would need to rebuild their serving infrastructure to run nine evaluators against every token sequence before returning a response — at their query volume (millions/day), this is architecturally impossible without a redesign. More importantly, publishing per-inference pass/fail scores creates enforceable accountability expectations. Their lawyers will never allow it.

*File paths:* `a11oy/src/gate.rs` (existing, [a11oy deep dive §B3]); `szl-policy-engine/src/evaluate.rs` (runtime evaluator); `szl-policy-engine/src/receipt.rs` (signed receipt). ~800 SLOC. Dependencies: `sha2` (MIT), `ed25519-dalek` (BSD-3), `serde_json` (MIT).

---

**Move A2 — Absorb MCP transport; ship a receipt-native MCP server as a reference implementation PR**

*Absorbed:* MCP spec ([modelcontextprotocol.io/specification/2025-03-26](https://modelcontextprotocol.io/specification/2025-03-26), Apache-2.0). JSON-RPC 2.0 over stdio/SSE, tool primitive interface, capability negotiation handshake.

*The inversion:* `maki-receipt-mcp` — a compliant MCP server that additionally: (a) SHA-256 hashes every tool schema at registration and publishes the hash to Rekor, (b) on every tool call verifies the schema hash matches the registered hash (blocking rug-pull attacks), (c) hashes (input params + tool_name + timestamp) → `input_hash`, executes the tool, hashes the output → `output_hash`, writes receipt JSON `{input_hash, output_hash, timestamp_iso8601, tool_name, session_id, receipt_sha256}` to a local append-only log before returning. Receipt returned in MCP response metadata field. [willakuy pod §L.1]

*Why Anthropic cannot follow:* They own the spec. Adding cryptographic receipts to the official reference servers would (a) break backward compatibility with every existing MCP client that does not expect the metadata field, and (b) endorse a receipt paradigm that would create accountability expectations for their own closed inference stack. A third-party reference implementation submitted via PR to `github.com/modelcontextprotocol/servers` creates community pressure they can ignore but cannot neutralize.

*File paths:* `szl-mcp-receipts/src/main.py` (Python, MCP compliant); `szl-mcp-receipts/src/receipt.py` (receipt generation); `szl-mcp-receipts/schema/receipt_v1.json`. ~400 SLOC. Dependencies: `mcp` (Apache-2.0), `hashlib` (stdlib), `ed25519` (MIT).

---

**Move A3 — Absorb RSP threshold language; ship a machine-readable capability ledger**

*Absorbed:* RSP v3 ([anthropic.com/news/responsible-scaling-policy-v3](https://www.anthropic.com/news/responsible-scaling-policy-v3)) — the ASL-2/3/4 tier structure, the concept of capability thresholds as typed predicates. This is the right architecture; the prose implementation is the problem.

*The inversion:* `szl-capability-ledger` — a JSON-LD schema where each capability tier is a signed typed predicate: `{tier: "ASL-3-equivalent", predicate: "cyberCapabilityUplift >= threshold_v2", evaluated_at: "2026-05-14T15:00:00Z", model_did: "did:szl:model:abc123", evaluator_key: "...", signature: "...", rekor_entry: "..."}`. Published to a Rekor-compatible log. Any regulator, insurer, or enterprise compliance system can programmatically query which capability tier a given model version was assessed at.

*Why Anthropic cannot follow:* RSP thresholds in prose form are regulatory aspirations; in typed signed predicates they become enforceable claims. Anthropic's lawyers have precisely calibrated the vagueness of the existing RSP language. Making it machine-readable and cryptographically signed would transform "policy" into "contract." SZL, building new, can make this commitment. Anthropic cannot walk back to it.

*File paths:* `szl-capability-ledger/schema/capability.json-ld`; `szl-capability-ledger/src/ledger.rs`. ~600 SLOC. Dependencies: `serde-jsonld` (Apache-2.0), `szl-receipt-core`.

---

**Move A4 — Absorb the Sleeper Agents finding; ship an adversarial consistency probe**

*Absorbed:* Hubinger et al. Sleeper Agents ([arXiv 2401.05566](https://arxiv.org/abs/2401.05566), CC-BY). The paper demonstrates that behavioral safety training cannot reach deceptive alignment. [willakuy pod §A.2] The methodology for constructing test scenarios is fully described.

*The inversion:* `szl-consistency-probe` — a CI/CD tool that runs Sleeper-Agents-style consistency checks against any LLM API endpoint. It generates paired prompt variants (e.g., same task with different date/context strings that should not change the answer) and checks whether the model's behavior is consistent. Inconsistency above a threshold is flagged and receipted: `{probe_type: "temporal_consistency", variant_pairs: [...], inconsistency_score: 0.23, threshold: 0.10, gate: "FAIL", receipt_sha256: "..."}`. This is the automated version of the Sleeper Agents evaluation, running continuously.

*Why Anthropic cannot follow:* Running this publicly against Claude would reveal exactly the kinds of behavioral inconsistencies their $1.5B Bartz settlement already exposed them for. SZL can run it against any open-weight model and publish receipts; Anthropic cannot run it against themselves.

*File paths:* `szl-consistency-probe/src/probe.py`; `szl-consistency-probe/src/receipt.py`. ~600 SLOC. Dependencies: `openai-compatible` API client (MIT), `szl-receipt-core`.

---

**Move A5 — Absorb Claude Code architecture; ship a session-replay coding agent**

*Absorbed:* Claude Code is a NodeJS/npm product (obfuscated build, but architecture is legible: API calls to Anthropic, shell tool invocations, filesystem access) ([github.com/anthropics/claude-code](https://github.com/anthropics/claude-code)). The agentic coding pattern — model picks tools, executes, observes, iterates — is the right product shape.

*The inversion:* `szl-code-agent` — an agentic coding assistant that (a) accepts any OpenAI-compatible model endpoint as a backend, (b) records every tool call in a content-addressed store (tool name + args + output + timestamp, SHA-256 hashed), (c) allows *deterministic session replay* from the hash-chain: given a session ID, any auditor can replay the exact sequence of tool calls that produced a given artifact. Developers can prove to a legal team that a specific code file was generated by model vX.Y.Z on a specific date with specific inputs.

*Why Anthropic cannot follow:* Claude Code is closed-source with no session replay. Adding replay would require (a) storing every tool call server-side in Anthropic infrastructure and (b) exposing that log to customers — which creates GDPR-adjacent obligations and competitive exposure of prompt patterns. SZL builds this natively, on the client side, with no server dependency.

*File paths:* `szl-code-agent/src/session.rs`; `szl-code-agent/src/replay.rs`; `szl-code-agent/src/content_store.rs`. ~1,500 SLOC. Dependencies: `blake3` (CC0), `szl-receipt-core`, OpenAI-compatible API spec (MIT).

---

**Move A6 — Absorb the CoT unfaithfulness admission; ship a chain-of-thought faithfulness auditor**

*Absorbed:* Anthropic's own paper "Reasoning models don't always say what they think" ([anthropic.com/research/reasoning-models-dont-say-think](https://www.anthropic.com/research/reasoning-models-dont-say-think)). The finding: visible chain-of-thought reasoning does not reliably reflect the model's actual internal reasoning process. Their "Honesty" research team [job listing signal] is a named response to this.

*The inversion:* `szl-cot-audit` — a post-hoc CoT consistency checker. Input: a reasoning trace (from any model) and the corresponding (prompt, response) pair. Runs a lightweight probe model (DistilBERT or similar open-weight, Apache-2.0) to score whether the stated reasoning is consistent with the actual output. Produces a signed attestation: `{faithfulness_score: 0.71, threshold: 0.85, gate: "WARN", probe_model: "distilbert-base-v2", probe_hash: "sha256:...", signed: "ECDSA:..."}`.

*Why Anthropic cannot follow:* Their own "Honesty" team is working on this. But they cannot *publish* a public faithfulness score for Claude's own reasoning — because any score below 1.0 is ammunition for litigation, regulatory scrutiny, and customer churn. SZL can run it against any model and publish; Anthropic cannot.

*File paths:* `szl-cot-audit/src/audit.py`; `szl-cot-audit/src/attestation.py`. ~700 SLOC. Dependencies: `candle-core` (Apache-2.0), `szl-receipt-core`.

---

**Move A7 — Absorb interpretability vocabulary; ship an open external probe interface**

*Absorbed:* Anthropic's SAE/monosemanticity vocabulary — "feature," "circuit," "activation steering," residual stream decomposition ([transformer-circuits.pub](https://transformer-circuits.pub/)). This is the most rigorous published framework for understanding model internals. [willakuy pod §A.3, §A.4]

*The inversion:* SZL does not need to run SAE analysis — they need to expose the interface. `szl-probe` is a gRPC schema (Apache-2.0) defining a standardized external probe interface for any LLM inference server. Any external researcher or auditor can attach a feature probe without access to model weights — they receive activation vectors at specified layers, run their own SAE or attribution analysis, and return findings. Anthropic cannot offer this because it would expose model architecture details they treat as trade secrets. SZL exposes it by default.

*File paths:* `szl-probe/proto/probe.proto` (gRPC schema); `szl-probe/src/server.rs`. ~400 SLOC. Dependencies: `tonic` (MIT), `prost` (Apache-2.0).

---

**Move A8 — Absorb economic index research; ship a labor-market receipt for every automated task**

*Absorbed:* Anthropic's Economic Index ([anthropic.com/economic-index](https://www.anthropic.com/economic-index)) and labor market paper ([anthropic.com/research/labor-market-impacts](https://www.anthropic.com/research/labor-market-impacts)). The task taxonomy (62 tasks across 844 occupations) is the most detailed public framework for classifying what AI actually does in the economy.

*The inversion:* SZL builds a task-classification layer that, for every agentic action, (a) classifies the action against the Anthropic/O*NET taxonomy, (b) records the classification in the inference receipt. Enterprise customers receive a monthly summary: "this month, your SZL deployment performed 4,231 tasks in O*NET category 15-1252 (Software Developer). Receipts are available for all 4,231." This is the first step toward auditable AI labor accounting — something regulators will mandate within 5 years.

*File paths:* `szl-task-classifier/src/classify.py`; `szl-task-classifier/data/onet_taxonomy.json`. ~500 SLOC. Dependencies: open O*NET taxonomy (public domain), `sklearn` (BSD-3).

---

**Move A9 — Absorb training data provenance gap; ship a public-only dataset SBOM**

*Absorbed:* The gap itself. The Bartz v. Anthropic settlement ($1.5B, August 2025) [willakuy pod §K.3; Copyright Alliance](https://copyrightalliance.org/participating-bartz-v-anthropic-settlement/) establishes that Anthropic *cannot* publish a clean training data SBOM without legal exposure. The Data Provenance Initiative ([dataprovenance.org](https://www.dataprovenance.org/)) is building exactly the infrastructure for this kind of audit.

*The inversion:* SZL commits to public-only ingestion (Apache/MIT/BSD-3/CC-BY only) and publishes a machine-readable dataset SBOM: a JSON-LD manifest listing every dataset used, its license, source URL, ingest date, and SHA-256 hash of the corpus snapshot. Submit this as a reference implementation to the Data Provenance Initiative. The implicit claim: here is a verifiable training data provenance record that no company with a shadow-library settlement can match.

*File paths:* `szl-data-sbom/schema/sbom.json-ld`; `szl-data-sbom/scripts/generate_sbom.py`. ~300 SLOC. Dependencies: `model-signing` (Apache-2.0), `hashlib` (stdlib).

---

**Move A10 — Absorb the GDPR/EU AI Act gap; ship a signed compliance report generator**

*Absorbed:* EU AI Act Articles 13 (transparency), 14 (human oversight), 22 (fundamental rights impact assessment) — all public law. Anthropic's Zürich pre-training hire and EU compliance push signal they are building for this market. The gap: their compliance artifacts will be PDF reports, not machine-readable signed documents.

*The inversion:* `szl-compliance-report` — a GitHub Action that generates a machine-readable, ECDSA-signed compliance report in JSON-LD format mapped to EU AI Act Article 13 and GDPR Article 22 criteria. Each criterion is a typed predicate with a signed pass/fail. Every SZL inference receipt can be referenced as evidence. A compliance officer gets a document they can feed into an automated audit pipeline, not a PDF they have to read.

*File paths:* `szl-compliance-report/schema/eu_ai_act_art13.json-ld`; `szl-compliance-report/src/generate.py`. ~400 SLOC.

---

## 3. OpenAI

### 3A. Visible posture

OpenAI describes itself as building "safe and beneficial AGI for the benefit of all humanity." ([openai.com](https://openai.com))

| Core claim | Source |
|---|---|
| The Model Spec defines a principal hierarchy (Platform > Operator > User) and behavioral defaults | [model-spec.openai.com](https://model-spec.openai.com); [CDN PDF May 2024](https://cdn.openai.com/spec/model-spec-2024-05-08.html) |
| o3 achieves 87.5% on ARC-AGI at high-compute settings — a "breakthrough" | [ARC Prize blog](https://arcprize.org/blog/oai-o3-pub-breakthrough) |
| Stargate: $500B data center build for the Intelligence Age | [OpenAI Stargate](https://openai.com/index/building-the-compute-infrastructure-for-the-intelligence-age/) |
| Operator and CUA: computer-use agents for enterprise workflow automation | [Introducing Operator](https://openai.com/index/introducing-operator/); [CUA](https://openai.com/index/computer-using-agent/) |
| Deep Research: autonomous web synthesis for premium subscribers | [Deep Research](https://openai.com/index/introducing-deep-research/) |
| OpenAI's timeline: AI research interns by September 2026; fully automated AI researchers by March 2028 | [36kr.com](https://eu.36kr.com/en/p/3529519807518854) |

### 3B. Revealed posture — the A↔B gap

| Signal | Interpretation | Source |
|---|---|---|
| Superalignment team dissolved, May 2024 | Long-term AI risk is not the operational priority | [CNBC](https://www.cnbc.com/2024/05/17/openai-dissolves-superalignment-ai-safety-team) |
| Mission Alignment Team disbanded, Feb 2026 | "Alignment" is being de-branded organizationally | [TechCrunch](https://techcrunch.com/2026/02/11/openai-disbands-mission-alignment-team-which-focused-on-safe-and-trustworthy-ai-development/) |
| Restructured from nonprofit to for-profit, 2025 | Shareholder returns are now a legal obligation — safety is a product claim, not a legal constraint | Multiple sources |
| o3 trained on 75% of the ARC-AGI public training set | Benchmark gaming is disclosed and normalized | [ARC Prize analysis](https://arcprize.org/blog/analyzing-o3-with-arc-agi) |
| 572 open roles; heavy federal civilian sales push | Federal government contracts are the 2026 revenue strategy | [openai.com/careers](https://openai.com/careers/) |

### 3C. Architectural commitments

| Commitment | Lock-in reason |
|---|---|
| Closed weights — GPT-4, o1, o3, o4 | Competitive moat; no path to opening without destroying the pricing model |
| Inference-time compute scaling (o3 paradigm) | 6-1024 samples at high settings = $1,900/task; requires enormous GPU fleet; impossible for small operators to match |
| RLHF as the primary training method | The Model Spec is "implicitly inserted into a platform message at the beginning of all conversations" — it is a training-time artifact, not a runtime policy |
| API-as-product | Every user must route through OpenAI's API; structural incentive to prevent self-hosting |
| Non-deterministic inference | Sparse MoE routing creates output variation even at temperature=0 ([HN discussion](https://news.ycombinator.com/item?id=37006224)); they cannot trivially fix this |
| Stargate $500B commitment | Every decision must generate returns on that capital; safety investments with no revenue path are now structurally deprioritized |

### 3D. Negative space — 15 key items

1. No public model architecture specifications for any production model since GPT-3.
2. No cryptographic receipts for any API response — every response is unsigned JSON.
3. No reproducible inference — non-determinism from Sparse MoE is known and unaddressed.
4. No public training data SBOM or Merkle tree.
5. No formal specification of the principal hierarchy — Model Spec is English prose, not a typed schema.
6. No SLSA provenance on model artifacts or API client libraries.
7. No Sigstore signing on the `openai` Python package published to PyPI.
8. No C2PA content credential on any generated image or text output.
9. No incident post-mortems for ChatGPT outages ([CNBC Dec 2025](https://www.cnbc.com/2025/12/02/chatgpt-down-outage-open-ai-chatbot.html); [community Feb 2025](https://community.openai.com/t/openai-2-26-2025-has-outages-and-is-actively-investigating/1130186)).
10. No public benchmark protocol preventing ARC-AGI training data leakage.
11. No formally verified component in the inference pipeline.
12. No compute cost disclosure for specific model inference — cost efficiency claims are unverifiable.
13. No data deletion proof — no cryptographic mechanism to verify conversation data was deleted.
14. No tool call audit log available to API users.
15. No public policy on when OpenAI will disclose internal capability threshold crossings.

### 3E. Defection signals

Already covered under §2F above. The OpenAI defection pattern is the defining signal: Ilya, Jan Leike, John Schulman, Mira Murati, Mission Alignment Team (dissolved). The institutional safety credibility collapsed in 18 months. The intellectual capital is now spread across 18+ startups ([Yahoo Finance](https://finance.yahoo.com/news/openai-mafia-18-startups-founded-124555320.html)).

---

### How SZL absorbs and inverts OpenAI — 5 moves

**Move O1 — Absorb the Model Spec principal hierarchy; ship a typed runtime enforcement library**

*Absorbed:* OpenAI Model Spec ([model-spec.openai.com](https://model-spec.openai.com)) — the principal hierarchy concept (Platform → Operator → User), the trust-level framework, the concept of hardcoded vs. softcoded behaviors. This is the right governance architecture.

*The inversion:* SZL ships the Model Spec as a machine-executable typed schema: `szl-principal-hierarchy.json` (JSON Schema Draft 2020-12). Every API call is evaluated against the current policy document. The policy document has a version number, author ECDSA signature, and Rekor transparency log entry. Operators audit which policy version governed which inference. OpenAI's principal hierarchy is embedded in training weights — it cannot be versioned, signed, or queried programmatically.

*File paths:* `szl-policy-engine/schema/principal-hierarchy.json`; `szl-policy-engine/src/principal.rs`. ~600 SLOC. Dependencies: `jsonschema` (MIT), `szl-receipt-core`.

---

**Move O2 — Absorb the o3 inference-time compute scaling insight; ship a cost-disclosed sampling API**

*Absorbed:* The ARC Prize analysis of o3 ([arcprize.org/blog/oai-o3-pub-breakthrough](https://arcprize.org/blog/oai-o3-pub-breakthrough)) reveals the compute cost structure: $6/task at low settings, $1,900/task at high. The "test-time compute scaling" paradigm is confirmed: more samples → better results.

*The inversion:* SZL builds a sampling API that (a) is transparent about number of samples drawn before execution, (b) reports per-sample cost estimate, (c) signs a "compute receipt" confirming actual compute used: `{samples_drawn: 32, tokens_per_sample: 4096, total_tokens: 131072, estimated_cost_usd: 0.52, actual_cost_usd: 0.48, receipt_sha256: "..."}`. Enterprises audit their AI compute spend against signed receipts. OpenAI provides no mechanism for verifying that billed compute corresponds to actual inference operations.

*File paths:* `szl-sampling-api/src/compute_receipt.rs`. ~400 SLOC.

---

**Move O3 — Absorb Operator/CUA approach; add signed action audit log**

*Absorbed:* OpenAI's Operator ([openai.com/index/introducing-operator/](https://openai.com/index/introducing-operator/)) and CUA ([openai.com/index/computer-using-agent/](https://openai.com/index/computer-using-agent/)) — the pattern of AI performing web actions (click, type, navigate) on behalf of users.

*The inversion:* `szl-computer-agent` records every browser action as a signed event in a content-addressed log: `{action: "click", target: "#submit-btn", page_url: "...", page_sha256: "...", timestamp: "...", signature: "..."}`. An enterprise can prove to a compliance team exactly what the agent did, on which page (with a hash of the page content at the moment of action), and when. OpenAI's Operator produces no such trail.

*File paths:* `szl-computer-agent/src/action_log.rs`. ~800 SLOC. Dependencies: `playwright` (Apache-2.0 wrapper), `szl-receipt-core`.

---

**Move O4 — Absorb Deep Research approach; add source-hash citations**

*Absorbed:* OpenAI's Deep Research — autonomous web browsing and synthesis. The core product value (deep synthesis across many sources) is right.

*The inversion:* SZL's research agent (a) fetches sources, (b) SHA-256 hashes each source page at fetch time, (c) includes the hash in every citation: `[Source: "Inflation Report Q1 2026", url: "...", fetched_at: "2026-05-14T15:00Z", page_sha256: "abc..."]`. If a cited page changes after report generation, the hash mismatch is detectable by any reader. OpenAI has not made this addition — because it exposes when Deep Research cites pages that have since changed or been deleted.

*File paths:* `szl-research-agent/src/citation.rs`. ~300 SLOC.

---

**Move O5 — Absorb the OpenAI API schema; ship an OpenAI-compatible signed response wrapper**

*Absorbed:* OpenAI API schema — request/response format for chat completions, function calling, streaming. The standard is de facto across the industry; every alternative model provider implements it.

*The inversion:* `szl-api-proxy` — a Rust HTTP proxy that accepts OpenAI-compatible requests, routes to any backend (OpenAI, Anthropic, Together, local Llama), wraps every response in a JWS (JSON Web Signature) envelope signed with ECDSA. Public key served at `/.well-known/jwks.json`. Any downstream system verifies response integrity with one `curl` + standard JWT library. OpenAI cannot add this without breaking every existing SDK.

*File paths:* `szl-api-proxy/src/main.rs`; `szl-api-proxy/src/jws.rs`; `szl-api-proxy/src/jwks.rs`. ~700 SLOC. Dependencies: `axum` (MIT), `jsonwebtoken` (MIT), `ring` (ISC), `szl-receipt-core`.

---

## 4. Google DeepMind

### 4A. Visible posture

"A world-leading AI research lab" pursuing AGI. Demis Hassabis: AGI is "5 to 10 years away." ([Time 2025](https://time.com/7277608/demis-hassabis-interview-time100-2025/)). 2024 Nobel Prize in Chemistry for AlphaFold ([Nobel Prize](https://www.nobelprize.org/prizes/chemistry/2024/press-release/)).

Key outputs: Gemini 2.0 ("the agentic era," Dec 2024 [Google blog](https://blog.google/innovation-and-ai/models-and-research/google-deepmind/google-gemini-ai-update-december-2024/)); AlphaProof (IMO silver medal, Lean 4 as grounding environment, [Nature 2025](https://www.nature.com/articles/s41586-025-09833-y)); AlphaFold 3 ([Nature 2024](https://www.nature.com/articles/s41586-024-07487-w)); Veo 3 (video + synchronized audio, [TechCrunch May 2025](https://techcrunch.com/2025/05/20/googles-veo-3-can-generate-videos-and-soundtracks-to-go-along-with-them/)).

### 4B. Architectural commitments and negative space

| Commitment | Lock-in |
|---|---|
| TPU compute dependency | All Gemini training/inference on Google TPUs; portability to other hardware is infeasible at their scale |
| Closed Gemini weights | No weights released for any production Gemini model |
| Google Search integration for grounding | A dependency no other player can replicate |
| AlphaFold 3 → restricted API (walked back from open) | Despite Nobel Prize, commercial API restrictions limit independent verification |
| Veo 3 video without C2PA credentials | Generating synthetic video at scale without content provenance stamps |
| No published safety policy equivalent to RSP | Safety is a research area at DeepMind, not an organizational commitment |

**AlphaProof's Lean 4 signal is the most important.** DeepMind used Lean 4 as a formal verification grounding environment and solved 3 of 5 non-geometry IMO problems. The limitation is compute (multi-day per problem), not the formalism. No one has taken the next step: using Lean 4 as a runtime policy specification language in a production API. That step belongs to SZL.

### How SZL absorbs and inverts DeepMind — 4 moves

**Move D1 — Absorb AlphaProof's Lean 4 insight; ship a proof-carrying API primitive**

*Absorbed:* The AlphaProof methodology ([Nature 2025](https://www.nature.com/articles/s41586-025-09833-y)) — Lean 4 as an interactive grounding environment for AI reasoning. Lean 4 is Apache-2.0. Mathlib4 is Apache-2.0.

*The inversion:* `szl-lean-gate` — each axis of the 9-axis gate is expressed as a Lean 4 proposition. On every gate evaluation, the Lean 4 kernel either finds a proof (pass) or a counterexample (fail). The proof term (or counterexample) is serialized and included in the inference receipt. This is formally verifiable safety that no one else has shipped in a production API.

*File paths:* `szl-lean-gate/SZLGate.lean`; `szl-lean-gate/src/lean_runner.rs`; `szl-lean-gate/src/proof_receipt.rs`. ~900 Lean + ~400 Rust. Dependencies: Lean 4 (Apache-2.0), Mathlib4 (Apache-2.0), `szl-receipt-core`.  
*Person-days:* 12 (requires Lean 4 specialist; hire a Mathlib4 contributor as contractor).

---

**Move D2 — Absorb AlphaFold open-science framing; ship the signed model release protocol**

*Absorbed:* AlphaFold 1/2 were celebrated for open release. The community expected AlphaFold 3 to follow. DeepMind restricted it. The community's expectation is the signal — there is a market for "open release with cryptographic provenance."

*The inversion:* Every SZL model release ships with: SHA-256 manifest over all weight files, Sigstore cosign signature, SLSA L1-honest provenance (L2 build-service attestation is roadmap via Wire D, not yet claimed), Rekor transparency log entry. Toolchain: `model-signing` ([pypi.org/project/model-signing](https://pypi.org/project/model-signing/), Apache-2.0). This is what the open science community wanted DeepMind to do. SZL does it by default.

*File paths:* `.github/actions/szl-model-signer/action.yml`; `.github/actions/szl-model-signer/sign.sh`. ~200 SLOC.

---

**Move D3 — Absorb Veo video generation awareness; ship C2PA watermarking for any generative output**

*Absorbed:* C2PA ([c2pa.org](https://c2pa.org), open standard) defines content credentials. DoD explicitly recommends it ([DoD CSI brief, Jan 2025](https://media.defense.gov/2025/Jan/29/2003634788/-1/-1/1/CSI-CONTENT-CREDENTIALS.PDF)). `c2pa-rs` is Apache-2.0.

*The inversion:* `szl-c2pa-stamp` — every artifact (image, text doc, video frame) generated through SZL's pipeline is stamped with a C2PA Content Credential including: model version SHA-256, prompt hash, operator DID, timestamp. Veo 3, DALL-E, and every other generative system produces unsigned artifacts. SZL's artifacts are verifiable in any C2PA-aware viewer (Adobe Photoshop, Leica cameras, BBC news systems).

*File paths:* `szl-c2pa-stamp/src/stamp.rs`; `szl-c2pa-stamp/src/cli.rs`. ~600 SLOC. Dependencies: `c2pa-rs` (Apache-2.0), `szl-receipt-core`, `clap` (MIT).

---

**Move D4 — Absorb Gemini multimodal API surface; add cross-modal receipt chaining**

*Absorbed:* Gemini's multimodal API pattern — accepting images, audio, and text in a single call. The architectural idea of native multimodal processing is right.

*The inversion:* SZL's multimodal API hashes each modality separately (image SHA-256, audio SHA-256, text SHA-256), commits them to a Merkle tree, includes the Merkle root in the response receipt. An auditor can verify that the exact image, audio, and text input that produced a given response are as claimed — without trusting the server. Gemini has no such mechanism.

---

## 5. Tier 2 — Rapid Cuts

**Mistral AI** ([mistral.ai](https://mistral.ai)) — Mistral 3 is an open-weight frontier model (Apache-2.0 for smaller models, closed for frontier). Le Chat Enterprise is their commercial push. *SZL inversion:* Use Mistral's open-weight models as the backend for SZL's signed inference proxy. Mistral provides the model; SZL provides the provenance layer Mistral cannot add without breaking licensing simplicity. No weight signing, no SLSA, no receipts on any Mistral release. ([TechCrunch Dec 2025](https://techcrunch.com/2025/12/02/mistral-closes-in-on-big-ai-rivals-with-mistral-3-open-weight-frontier-and-small-models/))

**Meta AI (Llama 4)** ([ai.meta.com](https://ai.meta.com/blog/llama-4-multimodal-intelligence/)) — Scout (17B active / 109B total, 16 experts, 10M context), Maverick (MoE product workhorse). Architecture uses iRoPE, early fusion multimodality, MetaCLIP vision encoder. *SZL inversion:* Llama 4 Scout fits on a single H100 in Int4. SZL wraps it in `szl-api-proxy` + `szl-model-signer` + `szl-c2pa-stamp`. Meta ships the model; SZL ships the verifiable deployment. HuggingFace checksums exist; no Sigstore signatures.

**xAI (Grok 3)** ([x.ai/news/grok-3](https://x.ai/news/grok-3)) — Trained on Colossus (200K GPU cluster). Grok 3 Think exposes chain-of-thought. *SZL inversion:* Grok's "open reasoning trace" is unsigned marketing. `szl-cot-audit` scores the faithfulness of any model's reasoning trace, including Grok 3 via API.

**Inflection AI** (ghost) — Microsoft acqui-hire for $650M ([Reuters Mar 2024](https://www.reuters.com/technology/microsoft-agreed-pay-inflection-650-mln-while-hiring-its-staff-information-2024-03-21/)). *Signal:* The acqui-hire is the dominant tier-2 AI exit. SZL's receipt doctrine is non-acqui-hireable: the doctrine is public, the code is Apache/MIT, the receipts are on a public ledger. Infrastructure independence is existential.

**Adept AI** (ghost) — Amazon acqui-hire, June 2024 ([TechCrunch](https://techcrunch.com/2024/06/28/amazon-hires-founders-away-from-ai-startup-adept/)). *Signal:* Same pattern. Computer-use agent startups are being absorbed into cloud providers.

**Cohere** ([cohere.com](https://cohere.com)) — $100M ARR, enterprise focus. "North" agent platform promises enterprise data security. ([Reuters May 2025](https://www.reuters.com/business/ai-firm-cohere-doubles-annualized-revenue-100-million-enterprise-focus-2025-05-15/)). *SZL inversion:* Cohere promises security. SZL delivers cryptographic proof of security.

**AI21 Labs / Together AI / Anyscale** — Together AI ([together.ai](https://www.together.ai)) is useful as a cheap inference backend for `szl-api-proxy`. Ray ([anyscale.com](https://www.anyscale.com/product/open-source/ray), Apache-2.0) is the distributed compute substrate for SZL's distributed inference. AI21 Jamba's hybrid SSM+Transformer ([ai21.com/jamba](https://www.ai21.com/jamba/)) is worth testing for byte-determinism properties.

---

## 6. The Open Ecosystem

### 6A. Evaluation infrastructure

**lm-evaluation-harness** (EleutherAI, [github.com/EleutherAI/lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness), Apache-2.0) — de facto open-source evaluation framework. Used by HuggingFace's Open LLM Leaderboard.

**Open LLM Leaderboard controversy:** Benchmark contamination led to community backlash and calls to end the leaderboard entirely. ([Reddit r/LocalLLAMA](https://www.reddit.com/r/LocalLLaMA/comments/1janir5/end_of_the_open_llm_leaderboard/)) The problem: no evaluation run is cryptographically reproducible.

**LMSYS Chatbot Arena** ([openlm.ai/chatbot-arena](https://openlm.ai/chatbot-arena/)) — crowdsourced ELO ranking. Every number is a claim, not a proof.

**HELM** (Stanford) — Holistic Evaluation of Language Models. Computationally expensive, rarely run against new models.

### 6B. What the open ecosystem is NOT doing

Across lm-eval-harness, HELM, BIG-bench, Chatbot Arena, HuggingFace:

1. No evaluation framework computes SHA-256 hashes of evaluated model weights + eval prompts + responses. Every leaderboard number is unreproducible without re-running.
2. No leaderboard uses Sigstore transparency logs for evaluation results.
3. No evaluation harness produces machine-verifiable receipts embeddable in regulatory filings.
4. No model release pipeline applies Sigstore model signing by default.
5. No standard for attaching C2PA credentials to model-generated evaluation outputs.
6. No zero-knowledge proof that a model was trained on claimed datasets. (ZKPROV [arXiv 2506.20915](https://arxiv.org/abs/2506.20915) shows this is technically feasible at 8B scale with <3.3s overhead — no adoption yet.)
7. No Lean 4 proof commitment attached to any mathematical benchmark result.

### How SZL absorbs and inverts the open ecosystem — 5 moves

**Move E1 — Fork lm-eval-harness; add receipt-native evaluation**

`szl-eval-harness` forks EleutherAI's lm-evaluation-harness (Apache-2.0) and adds: SHA-256 hash of every eval prompt + model response, Merkle tree over the full eval run, Rekor publication of the Merkle root, optional Sigstore signing of the final results JSON. Evaluation results become cryptographically verifiable. A regulator asking "how was this model evaluated?" gets a Rekor entry link, not a leaderboard URL.

*Added files:* `szl_eval_harness/receipt.py` (~200 lines); `szl_eval_harness/rekor_publish.py` (~100 lines). Dependencies: EleutherAI lm-eval-harness (Apache-2.0), `pysha3` (MIT), `rekor-python-client` (Apache-2.0). Person-days: 4.

---

**Move E2 — Ship a Sigstore model-signing GitHub Action for HuggingFace pushes**

Every HuggingFace model push runs `model-signing sign` (Apache-2.0, [pypi.org/project/model-signing](https://pypi.org/project/model-signing/)), publishes the Sigstore bundle, records the entry in Rekor, updates `MODEL_SIGS.md`. Verification: `model-signing verify --model path/to/model`. Any enterprise doing due diligence on a model can verify its provenance chain with one command.

*Files:* `.github/actions/szl-model-signer/action.yml`; `sign.sh`; `update_manifest.py`. ~200 SLOC. Person-days: 3.

---

**Move E3 — Build a public alignment scorecard against the 9-axis rubric**

`szl-alignment-scorecard` — a GitHub Action + Python library that runs on any LLM response dataset, scores each response on the 9 axes, generates a per-response receipt, and publishes aggregate results to a public JSON endpoint. Any developer can run `szl-score --model claude-3-5-sonnet-20241022 --dataset my_eval.jsonl` and get back a cryptographically signed scorecard. Anthropic helped create the Constitutional AI market; SZL owns the runtime evaluation standard. [willakuy pod §L.2]

*Files:* `szl-alignment-scorecard/score.py`; `szl-alignment-scorecard/action.yml`. ~500 SLOC. Person-days: 5.

---

**Move E4 — Submit a ZKPROV bridge for 8B-scale models**

ZKPROV ([arXiv 2506.20915](https://arxiv.org/abs/2506.20915)) proves training data certification with <3.3s overhead for ≤8B param models. `szl-zkprov-bridge` connects ZKPROV to SZL's receipt infrastructure. When a ZKPROV proof is available, it is attached as a field in the SZL inference receipt. For larger models, a placeholder with a roadmap timestamp is inserted. This is the strongest possible provenance claim — no trusted party required.

*Files:* `szl-zkprov-bridge/src/bridge.rs`; `szl-zkprov-bridge/src/placeholder.rs`. ~1,100 SLOC. Dependencies: ZKPROV reference (check license at release), `arkworks` (MIT/Apache-2.0), `szl-receipt-core`. Person-days: 10 (ZK specialist required).

---

**Move E5 — Publish a W3C VC 2.0 issuer for inference events**

W3C VC 2.0 became a Recommendation in April 2025 ([W3C](https://www.w3.org/press-releases/2025/verifiable-credentials-2-0/)). No AI lab has issued VC 2.0 credentials for inference events. `szl-provenance-vc` issues a Verifiable Credential for every inference: model DID, policy version DID, capability tier, timestamp, prompt hash, response hash. Signed with Ed25519. Compatible with any VC wallet or verifier. AI inference provenance embeddable in supply chain documents, legal filings, insurance claims.

*Files:* `szl-provenance-vc/src/issuer.rs`; `szl-provenance-vc/src/resolver.rs`; `szl-provenance-vc/schema/inference-credential.json-ld`. ~800 SLOC. Dependencies: `ssi` crate (Apache-2.0, Spruce Systems), `szl-receipt-core`. Person-days: 6.

---

## 7. MCP Ecosystem

### 7A. The protocol and its gap

MCP 2025-03-26 spec: [modelcontextprotocol.io/specification/2025-03-26](https://modelcontextprotocol.io/specification/2025-03-26) (Apache-2.0). JSON-RPC 2.0 over stdio/SSE. Primitives: Resources, Prompts, Tools (server-side); Sampling (client-side). 70+ community servers across filesystems, databases, web browsing, developer tools, communication, version control.

**The security gap:** "Trusted server" is defined by user configuration, not by any cryptographic mechanism. There is no machine-verifiable way to confirm a tool description has not been modified since approval.

### 7B. Known vulnerabilities

| Vulnerability | Description | Source |
|---|---|---|
| Prompt injection via tool descriptions | Malicious intent embedded in tool metadata triggers the LLM to exfiltrate credentials | [eSentire](https://www.esentire.com/blog/model-context-protocol-security-critical-vulnerabilities-every-ciso-should-address-in-2025); [OWASP LLM01](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) |
| Rug-pull / tool poisoning | Server modifies tool definitions between sessions without user notification | [arXiv 2603.22489](https://arxiv.org/abs/2603.22489) |
| Tool redefinition attacks | Malicious server overrides a legitimate tool's implementation when multiple servers share an environment | [arXiv 2511.20920](https://arxiv.org/abs/2511.20920) |
| Remote code execution | CVE-2025-6514: CVSS 9.6 in `mcp-remote` v0.0.5–0.1.15 — arbitrary OS command execution | [Cato Networks](https://www.catonetworks.com/news/cato-expose-real-world-mcp-exploits-in-hacking-demos-defcamp-2025/) |
| Cross-system privilege escalation | Chaining tool calls across multiple MCP servers to escalate privileges | [arXiv 2511.20920](https://arxiv.org/abs/2511.20920) |

**Root cause across all vulnerabilities:** No cryptographic commitment to tool definitions.

### 7C. The SZL fill

`szl-mcp-receipts` (described in Move A2 above) is the complete solution: hash-locked schemas at registration, schema verification at invocation, signed tool call receipts, daily Merkle root publication.

Why Anthropic cannot add this to the official spec: they are the spec owner, but backward compatibility with 70+ community servers prevents retroactive changes. An independent reference implementation submitted as a PR to `modelcontextprotocol/servers` creates the pattern. The community adopts; the spec eventually follows.

---

## 8. Adjacent Disciplines

### 8A. Formal verification — Lean 4

Lean 4 ([lean-lang.org](https://lean-lang.org), Apache-2.0) is production-ready for mathematical proofs. Mathlib4 contains 100,000+ formalized theorems. AlphaProof ([Nature 2025](https://www.nature.com/articles/s41586-025-09833-y)) proved Lean 4 can ground AI reasoning at IMO competition level. [VentureBeat on Lean 4](https://venturebeat.com/ai/lean4-how-the-theorem-prover-works-and-why-its-the-new-competitive-edge-in) calls it "the new competitive edge."

What no AI lab does with Lean 4 in production: attach proof terms to API responses, use it as a policy specification language, write proofs of system properties (access control invariants, output bounds). SZL's Move D1 (`szl-lean-gate`) is the first production deployment.

### 8B. Cryptography — SHA-256, Merkle trees, zk-SNARKs

**SHA-256 + Merkle trees:** The foundation of Bitcoin, Git, and SLSA. Used in `szl-receipt-core` as the first receipt layer. Trivial computational cost (~1ms per receipt).

**zk-SNARKs:** ZKPROV ([arXiv 2506.20915](https://arxiv.org/abs/2506.20915)) demonstrates that zero-knowledge proofs can bind training datasets, model parameters, and responses with <3.3s overhead for ≤8B params. The math is solved. The library work is in progress. `arkworks` (MIT/Apache-2.0), `halo2` (MIT, no trusted setup) are the Rust toolchains. `szl-zkprov-bridge` (Move E4) implements the bridge when the reference implementation releases.

### 8C. Supply chain security — SLSA, Sigstore, in-toto

**SLSA** ([slsa.dev](https://slsa.dev)): Level 1 (provenance exists), Level 2 (hosted build platform), Level 3 (hardened builds). Most AI artifacts are at Level 0. SZL commits to Level 2 minimum on every release.

**Sigstore** — keyless signing via OIDC identity + Fulcio CA + Rekor append-only log. Free public infrastructure. `model-signing` ([pypi.org/project/model-signing](https://pypi.org/project/model-signing/)) wraps it for ML models. Red Hat workflow: SHA-256 manifest → Sigstore signing → Rekor entry → verifier checks inclusion proof. ([Red Hat blog](https://next.redhat.com/2025/04/10/model-authenticity-and-transparency-with-sigstore/))

**in-toto** (CNCF-incubating, Apache-2.0) — signed link metadata over every step in a build pipeline. SZL uses in-toto to attest the complete pipeline from training data → fine-tuning → quantization → deployment for any SZL-hosted model.

### 8D. Provenance — W3C VC 2.0, C2PA

**W3C VC 2.0** — Recommendation April 2025 ([W3C](https://www.w3.org/press-releases/2025/verifiable-credentials-2-0/)). Multiple proof suites: ECDSA, BBS+, EdDSA. SZL issues VC 2.0 credentials for model inferences, evaluation results, and capability assessments via `szl-provenance-vc`.

**C2PA** ([c2pa.org](https://c2pa.org)) — open standard for digital content provenance. Members: Adobe, Microsoft, Sony, BBC, Intel. DoD recommends it for AI-generated content ([DoD CSI Jan 2025](https://media.defense.gov/2025/Jan/29/2003634788/-1/-1/1/CSI-CONTENT-CREDENTIALS.PDF)). `c2pa-rs` is Apache-2.0. SZL ships C2PA credentials on all generated artifacts via `szl-c2pa-stamp`.

### 8E. Reproducible builds — NixOS, Bazel

NixOS full reproducibility is not default ([NixOS issue #9731](https://github.com/NixOS/nixpkgs/issues/9731)) — it requires careful lockfile management. GPU floating-point non-determinism prevents bit-identical training reproduction for most models. **Honest position for SZL:** inference-level reproducibility (bit-identical outputs from identical inputs) is achievable for dense-architecture models at temperature=0 with fixed seed. For MoE models (Llama 4 Maverick, GPT-4 class), inference non-determinism is a known limitation — documented in signed manifests.

Bazel (Apache-2.0) with remote caching supports reproducible builds. SZL targets honest **SLSA L1** provenance today; isolated-builder L2 is roadmap and **L3 is NOT claimed** (doctrine: L3 is banned). All `szl-*` library builds use Bazel.

---

## 9. Cross-Target Wedge Map

The ten capabilities no one has shipped:

| Gap | Why it's universally missing |
|---|---|
| Cryptographically signed inference receipts | Creates legal liability for signed claims; breaks backward compatibility |
| Machine-readable, signed, versioned policy documents | Precision creates accountability; labs prefer prose flexibility |
| SLSA provenance on model weights | Weight architecture is a trade secret; provenance exposes it |
| C2PA content credentials on AI output | Requires version stability commitment; conflicts with rapid iteration |
| Formally verified components in inference pipeline | Formal methods are rare; culture is empirical-first |
| Reproducible training builds | GPU non-determinism + proprietary hardware + distributed pipelines |
| Zero-knowledge proofs of training provenance | Active research (ZKPROV 2025); no production deployment yet |
| Hash-locked MCP tool schema commitments | MCP too new; backward compatibility prevents retroactive security |
| Lean 4 proof terms attached to production API responses | Only research use (AlphaProof); no production deployment |
| W3C VC 2.0 credentials for inference events | VC 2.0 is new (April 2025); no AI ecosystem adoption yet |

**These ten items are SZL's product roadmap.** Every one is technically achievable today. None requires frontier-lab-scale compute. All are Apache/MIT/CC-BY compatible. All produce artifacts more legally defensible than anything any lab ships.

**The structural thesis:** The labs are optimized for capability (benchmark scores), throughput (tokens/sec), and product velocity (features/month). None of these metrics reward cryptographic provenance, formal verification, supply chain security, reproducibility, or receipt-based audit trails. Adding these features is *in direct tension* with the labs' competitive metrics — and creates legal liability they will not accept for their existing customers. SZL builds exactly where the tension is highest.

**The regulatory accelerant:** EU AI Act Articles 13-14, FTC AI enforcement, DoD C2PA recommendations, and NIST AI RMF ([NIST RMF update March 2025](https://airc.nist.gov/technical-reports/#NIST.AI.600-1)) are converging on mandatory AI auditability for high-risk systems. The labs helped write these standards while building infrastructure that cannot satisfy them. SZL builds the infrastructure.

---

## 10. RIKCH'AY Playbook — 12 Ships in 12 Weeks

### Anatomy key

| Label | Meaning |
|---|---|
| **HEART** | Core doctrine infrastructure — the receipt engine that everything else depends on |
| **MAKI finger** | MCP integration and tool-call security layer |
| **CHAKI toe** | Evaluation, audit, and provenance verification layer |
| **SPINE vertebra** | Policy engine, formal specification, and capability classification |

### Why this cannot be matched

The closing argument for each ship is the same structural point: the labs cannot add these features to existing products without (a) breaking backward compatibility with millions of API consumers, (b) creating legal liability for the claims the signatures would make, or (c) exposing architecture details they treat as trade secrets. SZL builds on open rails, publishes on public ledgers, signs everything, and invites audit. The labs cannot follow without dismantling what they are.

---

### Ship 01 — `szl-receipt-core`

**Anatomy:** HEART  
**Absorbed signal:** Universal gap — no lab provides cryptographic inference receipts.  
**What it is:** Rust library. SHA-256 hashes every artifact (prompt, context, response, tool call, policy evaluation). Builds Merkle trees. Publishes daily roots to Rekor-compatible log.

**Deliverables:**
- `szl-receipt-core/src/lib.rs` — SHA-256 hasher, Merkle tree builder, receipt struct (`ReceiptV1`)
- `szl-receipt-core/src/rekor.rs` — Rekor upload client (HTTPS POST to public Rekor instance)
- `szl-receipt-core/src/merkle.rs` — append-only Merkle log with O(log n) inclusion proofs
- `szl-receipt-core/tests/vectors.rs` — test vectors against known SHA-256 values from NIST FIPS 180-4

**Dependencies:** `sha2` (MIT), `rs-merkle` (MIT), `reqwest` (MIT/Apache-2.0), `serde` (MIT/Apache-2.0)  
**License:** Apache-2.0  
**SLOC:** ~800  
**Person-days:** 5  
**Doctrine:** D-SHORTEST-HONEST · D-HITCHHIKE-PROOF  

**Why no lab can match:** Creating signed inference receipts generates enforceable liability for the claims made. Their legal teams will not allow it for existing products. For a new product, it creates backward incompatibility with every existing customer.

---

### Ship 02 — `szl-mcp-receipts`

**Anatomy:** MAKI finger  
**Absorbed signal:** MCP tool poisoning (arXiv 2603.22489), rug-pull attacks (eSentire), CVE-2025-6514.  
**What it is:** Drop-in Python MCP middleware. Hash-locks tool schemas at registration. Verifies schema hash at every invocation. Blocks schema modifications between sessions. Signs every tool call receipt.

**Deliverables:**
- `szl-mcp-receipts/src/main.py` — MCP-compliant server (JSON-RPC 2.0 over stdio)
- `szl-mcp-receipts/src/schema_hash.py` — SHA-256 schema hashing at registration
- `szl-mcp-receipts/src/invocation_guard.py` — hash verification before every tool call
- `szl-mcp-receipts/src/receipt_chain.py` — call/response receipt chain (delegates to szl-receipt-core via FFI or REST)
- `szl-mcp-receipts/schema/receipt_v1.json` — receipt schema
- Target: PR to `github.com/modelcontextprotocol/servers`

**Dependencies:** `mcp` (Apache-2.0), `hashlib` (stdlib), `ed25519` (MIT), `szl-receipt-core` (REST endpoint)  
**License:** Apache-2.0  
**SLOC:** ~400  
**Person-days:** 6  
**Doctrine:** 9-axis gate · Receipt doctrine  

---

### Ship 03 — `szl-model-signer` GitHub Action

**Anatomy:** CHAKI toe  
**Absorbed signal:** No frontier lab or open ecosystem tool signs model weights with Sigstore by default.  
**What it is:** GitHub Action. On every model artifact push: runs `model-signing sign`, publishes Sigstore bundle, records Rekor entry, appends to `MODEL_SIGS.md`.

**Deliverables:**
- `.github/actions/szl-model-signer/action.yml`
- `.github/actions/szl-model-signer/sign.sh` — calls `model-signing sign --signer sigstore`
- `.github/actions/szl-model-signer/update_manifest.py` — appends new entry to `MODEL_SIGS.md` with model name, SHA-256, Rekor log ID, timestamp
- `README.md` with verification instructions: `model-signing verify --model ./path/to/model --sig ./path/to/sig`

**Dependencies:** `model-signing` (Apache-2.0), `sigstore` CLI (Apache-2.0), GitHub Actions runner  
**License:** Apache-2.0  
**SLOC:** ~200  
**Person-days:** 3  

---

### Ship 04 — `szl-policy-engine`

**Anatomy:** SPINE vertebra  
**Absorbed signal:** OpenAI Model Spec principal hierarchy (prose); Anthropic CAI principles (training-time, unfalsifiable). Both cry out for a typed runtime alternative.  
**What it is:** Rust runtime policy engine. JSON Schema policy documents (principal hierarchy, capability tiers, allowed/denied operations). Every API call is evaluated against the current policy version. Produces signed evaluation receipt. Policy documents are themselves ECDSA-signed and Rekor-logged.

**Deliverables:**
- `szl-policy-engine/schema/policy-v1.json` — JSON Schema for policy documents (principal hierarchy, capability tier, allowed operations, denied operations, operator identity)
- `szl-policy-engine/src/evaluate.rs` — policy evaluation against a request context
- `szl-policy-engine/src/receipt.rs` — signed evaluation receipt (delegates to `szl-receipt-core`)
- `szl-policy-engine/src/principal.rs` — principal hierarchy resolution (Platform → Operator → User)
- `szl-policy-engine/src/versioning.rs` — policy version management and Rekor publication
- Example policies: `examples/szl-default.json`, `examples/gdpr-article22.json`, `examples/eu-ai-act-art13.json`
- `szl-policy-engine/README.md` — Apache-2.0

**Dependencies:** `jsonschema` (MIT), `ed25519-dalek` (BSD-3), `serde_json` (MIT), `szl-receipt-core`  
**License:** Apache-2.0  
**SLOC:** ~1,400  
**Person-days:** 8  
**Doctrine:** 9-axis gate · SPINE  

---

### Ship 05 — `szl-api-proxy`

**Anatomy:** HEART  
**Absorbed signal:** OpenAI API schema (de facto standard); no existing proxy adds cryptographic response signing.  
**What it is:** Lightweight Rust HTTP proxy. Accepts OpenAI-compatible requests. Routes to any backend. Wraps every response in a JWS (JSON Web Signature) envelope signed with ECDSA. Serves public key at `/.well-known/jwks.json`. Any downstream system verifies response integrity with `curl` + standard JWT library.

**Deliverables:**
- `szl-api-proxy/src/main.rs` — axum HTTP server, request routing
- `szl-api-proxy/src/jws.rs` — JWS envelope construction (JOSE spec compliant)
- `szl-api-proxy/src/jwks.rs` — JWKS public key endpoint
- `szl-api-proxy/src/receipt.rs` — SHA-256 receipt generation via szl-receipt-core
- `szl-api-proxy/Dockerfile` — distroless container image
- `szl-api-proxy/README.md` — Apache-2.0

**Dependencies:** `axum` (MIT), `reqwest` (MIT), `jsonwebtoken` (MIT), `ring` (ISC), `szl-receipt-core`  
**License:** Apache-2.0  
**SLOC:** ~700  
**Person-days:** 5  

---

### Ship 06 — `szl-cot-audit`

**Anatomy:** CHAKI toe  
**Absorbed signal:** Anthropic's own finding that reasoning models don't faithfully describe their internal computations ([anthropic.com/research/reasoning-models-dont-say-think](https://www.anthropic.com/research/reasoning-models-dont-say-think)).  
**What it is:** Post-hoc CoT faithfulness auditor. Input: reasoning trace + (prompt, response) pair. Runs a lightweight probe model (DistilBERT class, Apache-2.0) to score whether the stated reasoning is consistent with the actual output. Produces a signed faithfulness attestation.

**Deliverables:**
- `szl-cot-audit/src/audit.py` — faithfulness scoring pipeline
- `szl-cot-audit/src/attestation.py` — signed attestation generation (`{faithfulness_score, threshold, gate, probe_model, probe_hash, ecdsa_signature}`)
- `szl-cot-audit/models/` — pointer to probe model checkpoint (HuggingFace Hub, Apache-2.0 model)
- `szl-cot-audit/README.md` — Apache-2.0

**Dependencies:** `candle-core` (Apache-2.0, HuggingFace), `tokenizers` (Apache-2.0), `szl-receipt-core`  
**License:** Apache-2.0  
**SLOC:** ~700  
**Person-days:** 7  

---

### Ship 07 — `szl-capability-ledger`

**Anatomy:** SPINE vertebra  
**Absorbed signal:** Anthropic RSP v3 capability tiers (ASL-2/3/4) — the right concept, trapped in prose.  
**What it is:** Machine-readable JSON-LD capability assessment ledger. Each tier is a typed, signed predicate appended to a Rekor-compatible log. Regulators and insurers query which capability tier a model was assessed at, programmatically.

**Deliverables:**
- `szl-capability-ledger/schema/capability.json-ld` — JSON-LD schema for capability predicates
- `szl-capability-ledger/src/ledger.rs` — ledger management (append, query, verify)
- `szl-capability-ledger/src/sign.rs` — ECDSA signing of capability records
- `szl-capability-ledger/examples/szl-tier1.json` — example Tier 1 assessment record
- `szl-capability-ledger/examples/szl-tier2.json` — example Tier 2 (ASL-3 equivalent) record

**Dependencies:** `serde_json` (MIT), `jsonld` (MIT), `szl-receipt-core`  
**License:** Apache-2.0  
**SLOC:** ~600  
**Person-days:** 4  

---

### Ship 08 — `szl-c2pa-stamp`

**Anatomy:** CHAKI toe  
**Absorbed signal:** C2PA open standard ([c2pa.org](https://c2pa.org)); DoD recommendation ([Jan 2025](https://media.defense.gov/2025/Jan/29/2003634788/-1/-1/1/CSI-CONTENT-CREDENTIALS.PDF)); no frontier lab stamps AI outputs with C2PA credentials.  
**What it is:** Rust library + CLI. Stamps any AI-generated artifact (image, text document, video frame) with a C2PA Content Credential: model version SHA-256, prompt hash, operator DID, timestamp.

**Deliverables:**
- `szl-c2pa-stamp/src/stamp.rs` — C2PA credential creation (wraps `c2pa-rs`)
- `szl-c2pa-stamp/src/cli.rs` — CLI: `szl-stamp --input img.png --model-hash sha256:abc --prompt-hash sha256:def --operator-did did:szl:org:xyz`
- `szl-c2pa-stamp/src/identity.rs` — operator DID resolution
- `szl-c2pa-stamp/README.md` — Apache-2.0

**Dependencies:** `c2pa-rs` (Apache-2.0), `szl-receipt-core`, `clap` (MIT/Apache-2.0)  
**License:** Apache-2.0  
**SLOC:** ~600  
**Person-days:** 5  

---

### Ship 09 — `szl-eval-harness`

**Anatomy:** CHAKI toe  
**Absorbed signal:** Open LLM Leaderboard contamination controversy; ARC-AGI training data leakage ([arcprize.org/blog/oai-o3-pub-breakthrough](https://arcprize.org/blog/oai-o3-pub-breakthrough)). Evaluation results are not reproducibly auditable.  
**What it is:** Fork of EleutherAI lm-evaluation-harness (Apache-2.0) with receipt generation. SHA-256 hashes every eval prompt + model response. Merkle tree over full eval run. Rekor publication of root. Optional Sigstore signing of results JSON.

**Deliverables:**
- Fork: `szl-eval-harness/` (base: [EleutherAI/lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness), Apache-2.0)
- Added: `szl_eval_harness/receipt.py` — SHA-256 hashing and Merkle commitment
- Added: `szl_eval_harness/rekor_publish.py` — Rekor upload on eval completion
- Added: `szl_eval_harness/results_sign.py` — optional Sigstore signing of `results.json`

**Dependencies:** EleutherAI lm-eval-harness (Apache-2.0), `pysha3` (MIT), `rekor-python-client` (Apache-2.0)  
**License:** Apache-2.0 (fork inherits; additions are original)  
**SLOC:** ~400 (additions only)  
**Person-days:** 4  

---

### Ship 10 — `szl-lean-gate`

**Anatomy:** SPINE vertebra  
**Absorbed signal:** AlphaProof's use of Lean 4 as a formal verification grounding environment ([Nature 2025](https://www.nature.com/articles/s41586-025-09833-y)). No one has shipped Lean 4 as a production API policy primitive.  
**What it is:** Lean 4 module + Rust interface. Each of the 9 gate axes is expressed as a Lean 4 proposition. For each gate evaluation, the Lean 4 kernel produces a proof term (pass) or counterexample (fail). The proof is serialized and included in the inference receipt.

**Deliverables:**
- `szl-lean-gate/SZLGate.lean` — 9 Lean 4 propositions (one per axis)
- `szl-lean-gate/SZLGateProofs.lean` — standard proof strategies for common input patterns
- `szl-lean-gate/src/lean_runner.rs` — Rust subprocess interface to Lean 4 kernel
- `szl-lean-gate/src/proof_receipt.rs` — proof term serialization into receipt struct (delegates to `szl-receipt-core`)
- `szl-lean-gate/README.md` — Apache-2.0, with Lean 4 installation instructions

**Dependencies:** Lean 4 (Apache-2.0), Mathlib4 (Apache-2.0), `subprocess` (MIT), `szl-receipt-core`  
**License:** Apache-2.0  
**SLOC:** ~900 Lean + ~400 Rust  
**Person-days:** 12 *(Lean 4 expertise is rare — hire a Mathlib4 contributor as contractor for this ship)*  

---

### Ship 11 — `szl-provenance-vc`

**Anatomy:** HEART  
**Absorbed signal:** W3C VC 2.0 became a Recommendation in April 2025 ([W3C](https://www.w3.org/press-releases/2025/verifiable-credentials-2-0/)). No AI lab has issued VC 2.0 credentials for inference events. First mover here sets the standard.  
**What it is:** W3C VC 2.0 issuer for AI inference events. Issues a Verifiable Credential per inference: model DID, policy version DID, capability tier, timestamp, prompt hash, response hash. Ed25519 signed. Compatible with any VC wallet or verifier. AI inference provenance embeddable in supply chain documents, legal filings, insurance claims.

**Deliverables:**
- `szl-provenance-vc/src/issuer.rs` — VC 2.0 issuer (JSON-LD + Ed25519 proof)
- `szl-provenance-vc/src/resolver.rs` — DID resolver for `did:szl:` method
- `szl-provenance-vc/src/verifier.rs` — VC verification (for third-party use)
- `szl-provenance-vc/schema/inference-credential.json-ld` — credential schema
- `szl-provenance-vc/README.md` — Apache-2.0

**Dependencies:** `ssi` crate (Apache-2.0, Spruce Systems), `szl-receipt-core`, `ed25519-dalek` (BSD-3)  
**License:** Apache-2.0  
**SLOC:** ~800  
**Person-days:** 6  

---

### Ship 12 — `szl-zkprov-bridge`

**Anatomy:** SPINE vertebra  
**Absorbed signal:** ZKPROV ([arXiv 2506.20915](https://arxiv.org/abs/2506.20915)) — ZK proofs binding training datasets, model parameters, and responses with <3.3s overhead for ≤8B params. The strongest possible provenance claim. Open-weight labs (Meta, Mistral) could run it but haven't. Closed-weight labs (Anthropic, OpenAI) structurally cannot.  
**What it is:** Bridge library connecting ZKPROV reference implementation to SZL's receipt infrastructure. When a ZKPROV proof is available, it is attached as a field in the inference receipt. For larger models (>8B), a typed placeholder with roadmap timestamp is inserted.

**Deliverables:**
- `szl-zkprov-bridge/src/bridge.rs` — ZKPROV proof generation and attachment to receipt
- `szl-zkprov-bridge/src/placeholder.rs` — typed placeholder for large-model proofs (`{zk_proof: null, roadmap_target: "2027-Q1", reason: "model_size_exceeds_current_zkprov_limit"}`)
- `szl-zkprov-bridge/README.md` — Apache-2.0, with ZKPROV citation
- `szl-zkprov-bridge/ROADMAP.md` — timeline for extending to 70B+ models

**Dependencies:** ZKPROV reference (check license at first release), `arkworks` (MIT/Apache-2.0), `szl-receipt-core`  
**License:** Apache-2.0  
**SLOC:** ~1,100  
**Person-days:** 10 *(ZK specialist required; can be same contractor as Ship 10 if they have both skillsets)*  

---

### 12-Week Schedule

| Week | Ship | Anatomy | Person-days |
|---|---|---|---|
| 1 | Ship 01: `szl-receipt-core` | HEART | 5 |
| 1–2 | Ship 05: `szl-api-proxy` | HEART | 5 |
| 2 | Ship 03: `szl-model-signer` Action | CHAKI | 3 |
| 2–3 | Ship 02: `szl-mcp-receipts` | MAKI | 6 |
| 3–4 | Ship 04: `szl-policy-engine` | SPINE | 8 |
| 4 | Ship 08: `szl-c2pa-stamp` | CHAKI | 5 |
| 4–5 | Ship 09: `szl-eval-harness` | CHAKI | 4 |
| 5–6 | Ship 07: `szl-capability-ledger` | SPINE | 4 |
| 6–7 | Ship 11: `szl-provenance-vc` | HEART | 6 |
| 7–8 | Ship 06: `szl-cot-audit` | CHAKI | 7 |
| 8–10 | Ship 10: `szl-lean-gate` | SPINE | 12 |
| 10–12 | Ship 12: `szl-zkprov-bridge` | SPINE | 10 |

**Total person-days: 75**  
**Solo pace:** ~15 weeks  
**Two-engineer pace:** ~8 weeks (Ships 01–09 are parallelizable; Ships 10 and 12 require specialist skills best contracted out)  

**The honest constraint:** Ships 10 and 12 require Lean 4 and ZK expertise respectively. Budget for a 4-6 week learning curve or hire a Mathlib4 contributor (Lean) and an `arkworks` contributor (ZK) as contractors. Both communities are small, known, and reachable via GitHub.

**The most important ship is 01.** Everything else depends on it. Ship it first, document it thoroughly, and the rest of the fleet follows as composable layers on top.

---

## 11. Doctrine Appendix

| Clause | Meaning |
|---|---|
| **D-SHORTEST-HONEST** | Every claim cited. No fluff. Every paragraph earns its space. |
| **D-HITCHHIKE-PROOF** | Every move rides public rails: Apache/MIT/BSD-3/CC-BY only. No proprietary dependencies. |
| **Receipt doctrine** | Every inference event is signed. Every byte of context hashed before execution. Every model weight traceable to its provenance chain. Every audit cryptographically verifiable without trusting any server operator. |
| **9-axis gate** | Nine independently evaluated gates. Conjunctive AND. Each with a signed pass/fail receipt. At least one axis expressed as a Lean 4 proposition. |
| **Byte-determinism** | For dense-architecture models at temperature=0 with fixed seed: outputs are deterministic. The hash of input + output is the receipt. Limitations (MoE non-determinism) documented in signed manifests. |
| **Public ledger** | All capability assessments, policy versions, and daily Merkle roots published to Rekor — free, public, append-only. |
| **No hallucinations, no bandaids** | Every claim verifiable by a third party using only public information. The receipt is the verification mechanism. |

---

## 12. Source Index

All URLs verified accessible without login as of 2026-05-14.

| Category | Source | URL |
|---|---|---|
| Anthropic mission | anthropic.com | https://www.anthropic.com/ |
| Constitutional AI | arXiv 2212.08073 | https://arxiv.org/abs/2212.08073 |
| Sleeper Agents | arXiv 2401.05566 | https://arxiv.org/abs/2401.05566 |
| Scaling Monosemanticity | transformer-circuits.pub | https://transformer-circuits.pub/2024/scaling-monosemanticity/ |
| Circuits April 2024 update | transformer-circuits.pub | https://transformer-circuits.pub/2024/april-update/index.html |
| RSP v3 | anthropic.com | https://www.anthropic.com/news/responsible-scaling-policy-v3 |
| RSP v2.1 PDF | anthropic CDN | https://www-cdn.anthropic.com/17310f6d70ae5627f55313ed067afc1a762a4068.pdf |
| Claude's Constitution | anthropic.com | https://www.anthropic.com/constitution |
| Reasoning models don't say what they think | anthropic.com | https://www.anthropic.com/research/reasoning-models-dont-say-think |
| Labor market impacts | anthropic.com | https://www.anthropic.com/research/labor-market-impacts |
| Economic index | anthropic.com | https://www.anthropic.com/economic-index |
| MCP announcement | anthropic.com | https://www.anthropic.com/news/model-context-protocol |
| MCP specification | modelcontextprotocol.io | https://modelcontextprotocol.io/specification/2025-03-26 |
| MCP servers registry | github.com | https://github.com/modelcontextprotocol/servers |
| Claude Code | github.com | https://github.com/anthropics/claude-code |
| Amazon $25B investment | CNBC | https://www.cnbc.com/2026/04/20/amazon-invest-up-to-25-billion-in-anthropic-part-of-ai-infrastructure.html |
| Claude performance backlash | Fortune | https://fortune.com/2026/04/14/anthropic-claude-performance-decline-user-complaints-backlash-lack-of-transparency-accusations-compute-crunch/ |
| Bartz settlement | Copyright Alliance | https://copyrightalliance.org/participating-bartz-v-anthropic-settlement/ |
| Anthropic patent analysis | LinkedIn/Fainberg | https://www.linkedin.com/pulse/anthropics-ai-patents-bought-built-380-billion-shield-fainberg-or1ne |
| Anthropic jobs | anthropic.com | https://www.anthropic.com/jobs |
| RSP v3 criticism | Zvi Substack | https://thezvi.substack.com/p/anthropic-responsible-scaling-policy |
| Regulatory capture analysis | SmarterArticles | https://smarterarticles.co.uk/capture-by-design-how-frontier-labs-wrote-ai-rules-before-regulators-arrived |
| Jan Leike departs | Forbes | https://www.forbes.com/sites/roberthart/2024/05/29/openai-exec-who-resigned-over-safety-concerns-joins-rival-firm-heres-what-we-know/ |
| John Schulman departs OpenAI | CNBC | https://www.cnbc.com/2024/08/06/openai-co-founder-john-schulman-says-he-will-join-rival-anthropic.html |
| John Schulman to Murati | Fortune | https://fortune.com/2025/02/06/openai-john-schulman-mira-muratis-startup-anthropic/ |
| Ilya founds SSI | CNBC | https://www.cnbc.com/2024/06/19/openai-co-founder-ilya-sutskever-announces-safe-superintelligence.html |
| SSI $1B raise | Reuters | https://www.reuters.com/technology/artificial-intelligence/openai-co-founder-sutskevers-new-safety-focused-ai-startup-ssi-raises-1-billion-2024-09-04/ |
| Safety experts quitting | LinkedIn/Nordmark | https://www.linkedin.com/pulse/ai-safety-experts-quitting-jobs-anthropic-openai-xai-why-jon-nordmark-pydrc |
| AI employee exits | TechBrew | https://www.techbrew.com/stories/2026/02/12/AI-employee-exits-safety-ethics |
| OpenAI superalignment dissolved | CNBC | https://www.cnbc.com/2024/05/17/openai-dissolves-superalignment-ai-safety-team |
| Wired superalignment | Wired | https://www.wired.com/story/openai-superalignment-team-disbanded/ |
| OpenAI mission alignment disbanded | TechCrunch | https://techcrunch.com/2026/02/11/openai-disbands-mission-alignment-team-which-focused-on-safe-and-trustworthy-ai-development/ |
| OpenAI Model Spec | model-spec.openai.com | https://model-spec.openai.com |
| OpenAI Model Spec May 2024 | CDN | https://cdn.openai.com/spec/model-spec-2024-05-08.html |
| o3 introduction | openai.com | https://openai.com/index/introducing-o3-and-o4-mini/ |
| ARC-AGI o3 breakthrough | arcprize.org | https://arcprize.org/blog/oai-o3-pub-breakthrough |
| ARC-AGI o3 analysis | arcprize.org | https://arcprize.org/blog/analyzing-o3-with-arc-agi |
| OpenAI Operator | openai.com | https://openai.com/index/introducing-operator/ |
| OpenAI CUA | openai.com | https://openai.com/index/computer-using-agent/ |
| OpenAI Deep Research | openai.com | https://openai.com/index/introducing-deep-research/ |
| OpenAI Stargate | openai.com | https://openai.com/index/building-the-compute-infrastructure-for-the-intelligence-age/ |
| OpenAI careers | openai.com | https://openai.com/careers/ |
| OpenAI timeline | 36kr | https://eu.36kr.com/en/p/3529519807518854 |
| OpenAI mafia startups | Yahoo Finance | https://finance.yahoo.com/news/openai-mafia-18-startups-founded-124555320.html |
| ChatGPT outage Dec 2025 | CNBC | https://www.cnbc.com/2025/12/02/chatgpt-down-outage-open-ai-chatbot.html |
| ChatGPT outage Feb 2025 | OpenAI community | https://community.openai.com/t/openai-2-26-2025-has-outages-and-is-actively-investigating/1130186 |
| OpenAI non-determinism | HN | https://news.ycombinator.com/item?id=37006224 |
| Microsoft-OpenAI Oct 2025 | Microsoft blog | https://blogs.microsoft.com/blog/2025/10/28/the-next-chapter-of-the-microsoft-openai-partnership/ |
| AlphaProof IMO | DeepMind blog | https://deepmind.google/blog/ai-solves-imo-problems-at-silver-medal-level/ |
| AlphaProof Nature | Nature | https://www.nature.com/articles/s41586-025-09833-y |
| Gemini 2.0 | Google blog | https://blog.google/innovation-and-ai/models-and-research/google-deepmind/google-gemini-ai-update-december-2024/ |
| AlphaFold 3 | Nature | https://www.nature.com/articles/s41586-024-07487-w |
| Nobel Prize 2024 Chemistry | Nobel Prize | https://www.nobelprize.org/prizes/chemistry/2024/press-release/ |
| Hassabis interview | Time | https://time.com/7277608/demis-hassabis-interview-time100-2025/ |
| Veo 3 | TechCrunch | https://techcrunch.com/2025/05/20/googles-veo-3-can-generate-videos-and-soundtracks-to-go-along-with-them/ |
| Llama 4 | Meta AI blog | https://ai.meta.com/blog/llama-4-multimodal-intelligence/ |
| Grok 3 | x.ai | https://x.ai/news/grok-3 |
| Mistral 3 | TechCrunch | https://techcrunch.com/2025/12/02/mistral-closes-in-on-big-ai-rivals-with-mistral-3-open-weight-frontier-and-small-models/ |
| Inflection acqui-hire | Reuters | https://www.reuters.com/technology/microsoft-agreed-pay-inflection-650-mln-while-hiring-its-staff-information-2024-03-21/ |
| Adept acqui-hire | TechCrunch | https://techcrunch.com/2024/06/28/amazon-hires-founders-away-from-ai-startup-adept/ |
| Cohere revenue | Reuters | https://www.reuters.com/business/ai-firm-cohere-doubles-annualized-revenue-100-million-enterprise-focus-2025-05-15/ |
| lm-eval-harness | GitHub | https://github.com/EleutherAI/lm-evaluation-harness |
| Open LLM Leaderboard controversy | Reddit | https://www.reddit.com/r/LocalLLaMA/comments/1janir5/end_of_the_open_llm_leaderboard/ |
| Chatbot Arena | openlm.ai | https://openlm.ai/chatbot-arena/ |
| MCP security eSentire | eSentire | https://www.esentire.com/blog/model-context-protocol-security-critical-vulnerabilities-every-ciso-should-address-in-2025 |
| MCP threat modeling | arXiv 2603.22489 | https://arxiv.org/abs/2603.22489 |
| Securing MCP | arXiv 2511.20920 | https://arxiv.org/abs/2511.20920 |
| OWASP LLM01 | genai.owasp.org | https://genai.owasp.org/llmrisk/llm01-prompt-injection/ |
| MCP exploits demo | Cato Networks | https://www.catonetworks.com/news/cato-expose-real-world-mcp-exploits-in-hacking-demos-defcamp-2025/ |
| Lean 4 | lean-lang.org | https://lean-lang.org |
| Lean 4 competitive edge | VentureBeat | https://venturebeat.com/ai/lean4-how-the-theorem-prover-works-and-why-its-the-new-competitive-edge-in |
| ZKPROV | arXiv 2506.20915 | https://arxiv.org/abs/2506.20915 |
| SLSA | slsa.dev | https://slsa.dev |
| Sigstore model signing | Red Hat | https://next.redhat.com/2025/04/10/model-authenticity-and-transparency-with-sigstore/ |
| model-signing package | PyPI | https://pypi.org/project/model-signing/ |
| C2PA | c2pa.org | https://c2pa.org |
| DoD C2PA brief | DoD | https://media.defense.gov/2025/Jan/29/2003634788/-1/-1/1/CSI-CONTENT-CREDENTIALS.PDF |
| W3C VC 2.0 | W3C | https://www.w3.org/press-releases/2025/verifiable-credentials-2-0/ |
| EU AI Act | digital-strategy.ec.europa.eu | https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai |
| NixOS reproducibility issue | GitHub | https://github.com/NixOS/nixpkgs/issues/9731 |
| Data Provenance Initiative | dataprovenance.org | https://www.dataprovenance.org/ |
| NIST AI RMF 2025 | NIST | https://airc.nist.gov/technical-reports/#NIST.AI.600-1 |

---

*RIKCH'AY — public surface intake & inversion playbook*  
*Lutar, Stephen P. · ORCID 0009-0001-0110-4173 · SZL Holdings*  
*CC-BY-4.0 · 2026-05-14 · Doctrine v3 · Codename RIKCH'AY*

*Every URL verified reachable without login as of date of publication. Claims marked `[unverified]` are excluded from logical foundations. Companion documents: anthropic_willakuy_pod.md, a11oy_deep_dive.md, org_audit_exhaustive_v2.md, publication_audit_v2.md.*
