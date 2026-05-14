# Building a Verifiable AI Agent Body: Receipts, Replay, and the Architecture Behind SZL Holdings

*Lutar, Stephen P. | ORCID 0009-0001-0110-4173 | SZL Holdings*

---

## The problem with non-deterministic agents

An agent that produces different outputs on different runs — given identical inputs, identical model versions, and identical tool states — cannot be audited. This is not a performance problem. It is an architectural problem, and most agent systems accept it as an immutable property of LLMs and move on.

We did not accept it. The architecture described here enforces byte-identical replay at the kernel level: run the harness five times, get the same SHA-256 hash five times. Every kernel that fails this test is not eligible for production use in the body. This is not aspirational. It is the gate.

The second problem is the gate itself. Most agent architectures gate on "did the model return something parseable." We gate on policy. Specifically: does this output satisfy thirteen named axes simultaneously, with two of them (moralGrounding and measurabilityHonesty) at ≥0.95? If any axis fails, the output is rejected at the heart before it reaches the egress layer.

We built an AI agent body — brain, heart, hands, and wires — and every heartbeat produces a sha256 receipt you can verify. That is not a metaphor. That is the architecture.

---

## Spec: byte-identical replay

The replay requirement is simple to state and non-trivial to enforce. For any kernel K and any fixed input I, the following must hold:

```
sha256(K(I)) == sha256(K(I)) == sha256(K(I)) == sha256(K(I)) == sha256(K(I))
```

across five independent process invocations, with a cold start between each. This rules out: `time.time()`, `uuid4()`, random seeds not pinned at call time, hash maps with non-deterministic iteration order in Python ≤3.6 behavior that leaks through, and any external I/O not fully mocked in the test fixture.

The canonical replay hash for YUYAY v3 (the heart kernel, 430 lines):

`bacf54434f1a3bf2d758b27a62d5fd580ca4c8d3b180693573eeebcaea631fc5`

This hash is the Family C hash — the SHA-256 of the test harness's stdout stream when run against the pinned fixture. It is distinct from the file content hash (Family A) and from any intermediate computation hash (Family B). The distinction matters: the file hash changes when the file is edited; the replay hash changes when the kernel's behavior changes on the pinned input. They are different contracts.

The harness pattern is uniform across all eight Tier 1 kernels:

```python
# canonical harness pattern — simplified
import hashlib, subprocess, sys

EXPECTED = "bacf5443..."  # Family C hash, pinned at acceptance time

def run_once():
    result = subprocess.run(
        [sys.executable, "03_kernel.py"],
        capture_output=True, text=True
    )
    return result.stdout

hashes = []
for i in range(5):
    output = run_once()
    h = hashlib.sha256(output.encode()).hexdigest()
    hashes.append(h)

assert len(set(hashes)) == 1, f"Non-determinism detected: {set(hashes)}"
assert hashes[0].startswith(EXPECTED[:8]), f"Hash drift: {hashes[0]}"
print(f"PASS — 5x byte-identical: {hashes[0]}")
```

Every kernel that passes this test earns its canonical hash. Every canonical hash is published in the kernel's `00_RESULT.md`. Every published hash is auditable against a fresh run of the harness.

---

## How YUYAY scoring works

YUYAY v3 (430 lines, canonical hash `bacf5443…`) implements the conjunctive AND gate. The input is a candidate output packet from the brain. The output is either PASS with a receipt or REJECT with a reason code.

The 13 axes, simplified, cover: `moralGrounding`, `measurabilityHonesty`, `parsimony`, `groundedness`, `harmAvoidance`, `reversibility`, `humanOverridePreservation`, `publicOnlyIngestion`, `autonomyTierRespect`, `receiptProductionObligated`, `replayability`, `doctrineCompliance`, and `contextualFit`. The first two have the ≥0.95 threshold; the remaining eleven are ≥0.90. All must pass simultaneously.

The scoring is implemented as a series of named checks, not a weighted sum. There is no path to PASS that bypasses a failing axis. The architecture is deliberately brittle in this direction: a weighted average that achieves 0.91 overall while scoring 0.40 on measurabilityHonesty would pass a threshold-on-mean gate and fail this one.

This property — that the gate is conjunctive — is what makes the receipt meaningful. A receipt from YUYAY certifies that all thirteen checks passed for this specific input. Not that the output scored well on average. That all thirteen passed.

---

## Tripwires as code, not slogans

HUKLLA is the tripwire ledger. It is 660 lines. It maintains ten named alarms:

```python
TRIPWIRES = {
    "T01": "IMMUTABLE_LOG_TAMPER",
    "T02": "UNAUTHORIZED_EGRESS",
    "T03": "POLICY_AXIS_SUPPRESSION",
    "T04": "REPLAY_FIXTURE_MISMATCH",
    "T05": "AUTONOMY_TIER_VIOLATION",
    "T06": "HALLUCINATION_UNGROUNDED_CLAIM",
    "T07": "UNAUTHORIZED_NETWORK",
    "T08": "SCHEMA_VIOLATION",
    "T09": "COST_BUDGET_EXCEEDED",
    "T10": "REPLAY_NONDETERMINISM",
}
```

When a tripwire fires, HUKLLA writes the alarm event to YAWAR before taking any other action. The alarm itself is a receipt in the append-only bus. This is architecturally significant: you cannot suppress the evidence of a tripwire firing without tampering with the immutable log, which would itself fire T01. The alarms are self-entangling.

YAWAR (20 lines) is the receipt bus underneath this:

```python
# yawar_bus.py — 20 lines, complete
import hashlib, json

class YAWAR:
    def __init__(self):
        self.receipts = []

    def append(self, packet: dict, sentra_inspect=None) -> str:
        if sentra_inspect:
            sentra_inspect(packet)  # raises on violation
        payload = json.dumps(packet, sort_keys=True, ensure_ascii=False)
        h = hashlib.sha256(payload.encode()).hexdigest()
        self.receipts.append({"hash": h, "payload": packet})
        return h

    def read(self):
        return list(self.receipts)
```

The bus is 20 lines. The hash is deterministic because `sort_keys=True` and `ensure_ascii=False` are pinned. Every append returns the hash of what was appended. Every downstream verifier has the hash before it needs it.

---

## Animation as honesty signal (why we skipped GSAP)

The motion library ships alongside the architecture because architecture needs to be legible, not just documented.

GSAP is the obvious choice for a motion library of this kind. It is powerful, mature, and widely deployed. We did not use it. GSAP's license is a Webflow proprietary "No Charge" license — not Apache-2.0, not MIT, not BSD-3, not CC-BY. It is not OSI-approved. It carries a Prohibited Uses clause. Under SZL doctrine, every bundled dependency must carry a permissive open license from the approved list. GSAP fails that check.

The approved stack is pure SVG plus CSS `@keyframes`. Motion One (MIT) is available as an enhancement layer for React-rendered surfaces. No runtime required for the static animations.

The primary animation — the beating heart — is a gold HEART organ pulsing at 1.2 seconds per cycle. At each beat, a SHA-256 receipt line drops into the YAWAR write-bus below it, and 8 characters of the hash reveal via a typewriter animation. The hash displayed is real. It is injected from git HEAD at build time via a single `sed` call in CI:

```bash
SHA=$(git rev-parse --short=8 HEAD)
sed -i "s/RECEIPT_HASH/$SHA/g" assets/heart-beat.svg
```

The animation is doctrine made visible. Every element on screen corresponds to a named architectural component. The gold color is the HEART color token (`#B08940`). The cream background is the parchment ground (`#F5F1E8`). The monospace receipt line uses IBM Plex Mono (SIL OFL 1.1). Nothing on screen is decorative without a referent.

The visual language is influenced by Anthropic's parchment-and-biology aesthetic — we credit that lineage openly. But the SZL motion language goes further into engineering precision: FIG-labeled diagrams, anatomical callouts, sha256 hashes shown verbatim. Where Anthropic's visual idiom communicates warmth and thoughtfulness, ours communicates verifiability and accountability. Both are legitimate stances. They are not the same stance.

---

## Open invitation: try the kernels

The Tier 1 kernels are in public GitHub repositories under the szl-holdings organization. The replay harnesses are included. Run them:

```bash
# clone any Tier 1 kernel repo
# run the replay test
python 05_test_replay.py

# expected output for yuyay_v3:
# PASS — 5x byte-identical: bacf54434f1a3bf2d758b27a62d5fd580ca4c8d3b180693573eeebcaea631fc5
```

If your run produces a different hash, that is a finding. File it. We want to know. The replay requirement is not a claim we make and move past; it is an ongoing contract with anyone who runs the harness.

We are pre-Series-A. The hygiene work is ongoing. Known open items: CITATION.cff normalization across the org's repositories is incomplete, a legacy AlloyScape reference persists in an ouroboros contract document, and the musquy kernel has a cross-run hash ambiguity due to a timestamp function in the harness file (not the canonical kernel, but the ambiguity should be resolved). These are documented, not hidden. The doctrine_audit_pod_v9 report is in the workspace.

The live motion library and a visual demonstration of the architecture are at:

https://www.perplexity.ai/computer/a/szl-motion-library-.4AxlzUqT1u2o6KCitGMrQ

Every animation on that page carries a receipt. Pull the hash. Verify it. That is the whole point.

Built honestly. — Stephen P. Lutar
