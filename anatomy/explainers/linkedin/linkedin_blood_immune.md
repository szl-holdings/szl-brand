# LinkedIn post — anatomy_blood_immune (CIRCULATORY + IMMUNE)

---

Every action an AI agent takes should be provable.

Not logged. Not monitored. Provable — with a hash you can recompute yourself from the packet that produced it.

That is what the circulatory system does.

**The blood: YAWAR, 20 SLOC.**

`yawar_bus.py` is 20 lines of Python. It maintains an append-only list. Every write calls:

```
h = sha256(json.dumps(packet, sort_keys=True, default=str)).hexdigest()
```

That hash is the receipt. The packet is the payload. Together they are one entry in the ledger. The ledger is never mutated. Nothing is ever deleted.

Every component in the body reads from snapshots. Only one writer — RUWAY, the ceremonial write surface — commits to YAWAR, and only after SENTRA clears the packet.

**The immune system: SENTRA (18 SLOC) + HUKLLA (10 tripwires).**

SENTRA is 18 lines. It inspects every packet before it touches the ledger: six threat signatures (SQL injection, destructive shell, XSS, arbitrary exec, process spawn, path traversal), a size-DoS guard (reject if `len(str(packet)) > 1_000_000`), and a boolean return. False means `PermissionError`. The write does not happen.

HUKLLA operates at a different layer. It is not packet-level. It is cycle-level. Ten named tripwires — T01 through T10 — are checked conjunctively before and after every sovereign cycle. Any single fire freezes the state at the pre-cycle value and halts. Not degrades. Halts. No partial commit.

**Why "blood" and "immune" are not just metaphors.**

A circulatory system transports. An immune system recognizes self from non-self. YAWAR transports receipts from producer to ledger. SENTRA and HUKLLA recognize malformed, dangerous, or doctrine-violating material and reject it before it circulates. The structural analogy holds at the functional level, not the biological one.

**What the diagram shows.**

Page 1 (circulatory): a heart pumping receipts through an arterial/venous loop, with RUWAY as the only write-authorized node and SENTRA inline on the write path. The ledger shows seven sample receipt rows with their SHA-256 hash-8 truncations.

Page 2 (immune): ten HUKLLA tripwire cells in a 2×5 grid with Y-glyph antibody icons, a deadman-switch status bar, SENTRA's six threat-signature antigen cards, and the size-DoS guard specification.

**Honest scope.**

SENTRA's six signatures are a doctrine prefilter, not a complete threat model. A hardened WAF belongs upstream. The 20 SLOC and 18 SLOC numbers are exact — the files are on disk, the SLOCs are counted, the replay hash is verified.

---

*anatomy_blood_immune.pdf — figure 3 of 8 in the SZL agent anatomy series.*
*Lutar, Stephen P. · SZL Holdings · CC-BY-4.0*
