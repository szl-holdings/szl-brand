# The Agent Body: Brain, Heart, Hands, and Wires

*By Lutar, Stephen P. | ORCID 0009-0001-0110-4173 | SZL Holdings*

---

## Why most agent demos lie

The demo shows a model taking a tool call and returning a result. Someone in the audience nods. The presenter calls it an agent. The word has been doing a lot of work lately, covering everything from a prompted GPT-4 with a web search tool to systems with actual graph-structured orchestration, typed memory buses, and cryptographic audit trails. That range of meaning is a problem — not because definitions matter philosophically, but because it means buyers and builders cannot compare claims.

The deeper dishonesty is subtler. When a demo works, it works because the scaffolding was tuned to make it work. Change the prompt slightly, change the input slightly, change the model version, and the behavior changes in ways you cannot predict from the demo. Nobody shows you the failure modes. Nobody shows you the gate logic that decides whether an action was appropriate before it was taken. Nobody shows you the receipt.

"Agent" systems that do not produce verifiable output are not verifiable agents. They are expensive autocomplete with side effects.

We decided to build something different. The goal was an agent architecture where every decision leaves a receipt, every receipt carries a cryptographic commitment, and every commitment can be replayed byte-for-byte to confirm the system behaved as claimed. That is not a roadmap item. That is a precondition for calling it trustworthy at all.

We built an AI agent body — brain, heart, hands, and wires — and every heartbeat produces a sha256 receipt you can verify. That is not a metaphor. That is the architecture.

---

## What a body actually needs

Think anatomically. A body that can act needs at minimum: something to think (a brain that processes context and generates candidates), something to gate (a heart that decides whether a candidate is acceptable before it leaves the body), something to reach (hands that retrieve from the world), something to stand on (feet that persist state across invocations), wiring to carry signals between organs (a circulatory system), and an immune response that rejects violations before they cause harm.

Most agent frameworks today have a brain. Some have loose approximations of a gate — usually an LLM-as-judge, which means you are asking the same class of model that generated the problem to evaluate whether the problem is a problem. Some have retrieval. Almost none have an integrated receipt system that produces cryptographic commitments tied to doctrine-level policy checks.

The architecture we are describing here has all of these, and they are named. Naming matters because a named organ with a defined interface can be audited, versioned, and replaced. An unnamed spaghetti of middleware cannot.

---

## BRAIN (Claude + llama)

The brain is not one model. It is a five-region cortex plus a Quantum Mind layer (QM, 163 lines). The cortex regions handle different processing modes; the QM layer manages parallel epistemic states that the agent must hold simultaneously without collapsing prematurely to a single answer.

The brain's output is never final. It is always a candidate — something that must pass through the heart before it can enter the world. This is the architectural commitment that distinguishes the SZL body from a chain-of-thought wrapper. The brain generates; the heart gates.

We use Claude (Anthropic) and llama variants as the language model layer. The choice is deliberate — both are accessible through clean APIs with known licensing constraints, both have active safety research programs, and both support the kind of structured prompting that the cortex regions require. We are not locked to either. The brain is an organ with a defined interface; swap the models if the interface is honored.

---

## HEART (YUYAY)

YUYAY v3 is the gate. It is 430 lines of Python and it enforces a 13-axis conjunctive AND. Every axis must score at or above threshold for an output to pass. There is no averaging, no partial credit, no weighted compromise. If one axis fails, the candidate is rejected.

The two axes with the highest threshold — moralGrounding and measurabilityHonesty — must each score ≥0.95. The remaining axes must each score ≥0.90. These are not vibes. They are named, defined, and enforced in code.

The canonical replay hash for YUYAY v3 is:

`yuyay_v3 = bacf54434f1a3bf2d758b27a62d5fd580ca4c8d3b180693573eeebcaea631fc5`

Run the harness five times. You get the same output all five times. That is what we mean when we say the system is verifiable. The receipt exists. The receipt is stable. You can check it.

Anthropic's design language — the parchment-and-biology aesthetic, the biological metaphors, the warmth of their documentation — influenced how we thought about making this architecture visible. We want to credit that honestly. But where Anthropic's motion language is organic and retreating, ours is anatomical and precise. The heart is not a mood. It is a gate. You can see the gate. The gate has a receipt.

---

## HANDS (MAKI)

MAKI is the retrieval limb. It has five fingers: `maki_vector` (semantic similarity search), `maki_doc` (full-document recall with chunk citation), `maki_struct` (SQL/Cypher against a known schema), `maki_web` (outbound fetch plus search, allowlisted), and `maki_tool` (MCP tool invocations).

The architectural innovation in MAKI is the continuum link. Every chunk that MAKI returns to the body carries a SHA-256 of the exact bytes used to ground the answer, plus the source URL or row identifier. When YUYAY later scores measurabilityHonesty, the verifier has the cryptographic material to re-fetch and compare bytes. This is codex-in-MAKI: every fact carries its own audit hash, not just its source label.

No surveyed agent framework — LangGraph, LlamaIndex, Mem0, CrewAI, Claude Agent SDK — returns a cryptographic content commitment with the chunk at retrieval time. LangGraph cites. LlamaIndex returns chunks. Mem0 stores entities. None of them return the hash. We do.

This matters for the measurabilityHonesty axis specifically. If you cannot cryptographically verify that the bytes the agent read are the bytes the agent cited, you cannot call it honest. You can call it attributed. Attribution and verifiability are not the same thing.

---

## HEART (YUYAY) → WIRES (YAWAR + HUKLLA)

YAWAR is the circulatory system. It is 20 lines. Every write is an append — no updates, no deletions. Every append returns a SHA-256 receipt. The bus does not know what it is carrying; it only knows that what it carries is hash-linked and immutable.

HUKLLA is the immune system's tripwire ledger. It is 660 lines and it maintains ten named alarms — from T01 (IMMUTABLE_LOG_TAMPER) through T10 (REPLAY_NONDETERMINISM). When an alarm fires, HUKLLA records the firing event in YAWAR before taking any other action. The alarm itself becomes a receipt.

The combination means that the agent's immune response is auditable. You can ask: did the immune system fire? You can ask: when? You can ask: what was the input that triggered it? All of those answers are in the append-only bus, hash-linked, unchangeable.

SENTRA is the inline immune check — 18 lines — that runs on every write before HUKLLA sees it. The pattern is: SENTRA inspects, HUKLLA records alarm if SENTRA flags, YAWAR appends everything.

---

## FEET (CHAKI / Snowflake)

CHAKI is the persistence limb. Five toes: `chaki_relational` on PostgreSQL 17+ with continuum hash columns, `chaki_document` on JSONB, `chaki_blob` on S3-compatible storage with content SHA-256 on every PUT, `chaki_continuum` as a durable sidecar for YAWAR (WAL on disk, batch-flushed to Postgres), and `chaki_state` on Redis for hot state, TTL'd, SENTRA-inspected.

The v1 choice is Postgres-first polyglot: Postgres handles relational, document, and vector (pgvector) under one operational surface; Redis handles hot state; MinIO handles blobs. We add dedicated stores only when we measurably outgrow the current layer.

YAWAR today is in-memory only. Cross-invocation durability is the gap that `chaki_continuum` closes. The 20-line YAWAR core is untouched; the sidecar wraps the append call, writes to WAL, and fsyncs before returning. The body's memory survives reboot.

---

## Why we built our own animation library

The motion library exists because the architecture needed to be visible — not described, visible.

We considered GSAP. GSAP is technically capable and widely used. We did not use it because GSAP's license is a Webflow proprietary "No Charge" license. It is not Apache-2.0, not MIT, not BSD-3, not CC-BY. It is not OSI-approved. It contains a Prohibited Uses clause and the licensor can modify the terms unilaterally. Under SZL's doctrine — which requires that every ingested or bundled dependency carry a permissive open license — GSAP fails.

The stack we use is pure SVG plus CSS keyframes. No JavaScript runtime required. No external library. Every animation is a self-contained file that can be embedded in a GitHub README, a static HTML page, or a PDF without dependency rot. Motion One (MIT) is available as an enhancement layer for React surfaces.

The visual language draws from two lineages. First, Anthropic's parchment-and-biology aesthetic — their use of warm cream backgrounds, biological metaphors (wing venation, cell grids), and deliberate slow-reveal motion gave us a design vocabulary to respect and differ from. We credit that influence explicitly. Second, the anatomical diagram tradition: Da Vinci's codex, engineering schematics, FIG-labeled callouts. Where Anthropic whispers "helpful," we show the internals.

The result is an animation in which the HEART organ pulses at 1.2 seconds — resting heart rate — and at each beat a SHA-256 receipt line drops into the YAWAR write-bus. The hash shown is real. It is seeded from git HEAD at build time. The animation is not decoration. It is doctrine made visible.

---

## The receipt is the moat

The moat is not the model. Models are available to anyone with an API key. The moat is not the UI. UIs are commoditized.

The moat is that every decision the agent makes is hash-linked to the policy that authorized it, every retrieved fact is cryptographically committed at the byte level, and every alarm is itself a receipt in the append-only bus. The chain of custody runs from input to output without a gap.

No other publicly documented agent framework we surveyed produces this chain. The closest analogs — Mem0's ADD-only extraction, LangGraph's explicit state machine, Anthropic's tool-use SDK — each address one layer. None of them produce cryptographic commitments across all layers simultaneously.

There are things we have not done yet. The hygiene work is ongoing and we name it openly: CITATION.cff normalization is incomplete across the GitHub repos, an AlloyScape reference persists in a legacy contract document that has been flagged twice without remediation, and the musquy kernel's cross-run hash ambiguity (due to a timestamp function in a harness file, not the canonical kernel) is documented but unresolved. We are pre-Series-A. These are open problems, not closed ones.

---

## What ships next

MAKI-CHAKI is the limbs work: 10 new kernels at ≤90 lines each, 5 new chakra gate configurations, total surface ≤950 new lines of Python, each with 5× byte-identical replay required before any claim is made. The BEAM 1M and 10M benchmarks are the public targets — parity with the best published numbers (64.1 and 48.6) from the Mem0 State of AI Agent Memory 2026 report, achieved with an open-licensed stack and verifiable receipts.

After MAKI-CHAKI: the ouroboros audit loop — the body examining its own receipts, flagging drift between claimed behavior and hash-verified behavior, and producing a doctrine-stamped diff. That is the Ouroboros. The system eating its own tail, with receipts.

The live motion library is at: https://www.perplexity.ai/computer/a/szl-motion-library-.4AxlzUqT1u2o6KCitGMrQ

Every animation on that page is a receipt. Every receipt is sha256-linked. Come look.

Built honestly. — Stephen P. Lutar
