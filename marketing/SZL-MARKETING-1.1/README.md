# SZL-MARKETING-1.1 — payload, engine, and public mirrors

This folder holds the marketing payload as filed on 2026-09-30 and points at the code that now
implements it. The engine is the source of truth; the two public Spaces are exact projections
of it.

| What | Where | Notes |
|---|---|---|
| Payload (vision, guardrails, calendar, backlog, upgrades) | `SZL-MARKETING-1.1-2026-09-30.md` | Historical filing; numbers inside are dated observations. For current numbers run the engine. |
| Engine (facts, linter, drafts, plan) | `src/szl_brand/marketing/` · CLI `szl-marketing` | stdlib-only; vendored byte-for-byte into the Space |
| Fact factory Space source | `marketing/space/szl-marketing-1.1/` | Gradio; projected to `SZLHOLDINGS/szl-marketing-1.1` |
| Campaign hub Space source | `marketing/space/szl-brand-campaign/` | Static; numbers fetched live in the visitor's browser; projected to `SZLHOLDINGS/szl-brand-campaign` |
| Projection workflow | `.github/workflows/hf-marketing-spaces.yml` | Builds hashed packages from the exact tested `main` commit, publishes, reads the Hub back |
| Copy guard | `.github/workflows/marketing-copy-guard.yml` | Runs the compliance linter over public copy in this repository on every PR |
| Last filed factbase | `factbase.json` | Snapshot from the filing day; superseded by any `szl-marketing facts` run |
| `factbase_pipeline.py` | shim | Kept for the historical command line; delegates to `szl-marketing facts` |

## Run it

```bash
python -m pip install -e .
szl-marketing facts --out marketing-out            # live, labeled factbase (anonymous pulls)
szl-marketing lint marketing posts README.md       # compliance linter; exit 1 on any violation
szl-marketing compose --facts marketing-out/factbase.json \
  --subject-a "Receipts, not vibes" --subject-b "The honest label" --body essay.md
szl-marketing plan                                 # guardrails, calendar, backlog, KPIs, investor loop
szl-marketing space-build --target szl-marketing-1.1 --source-sha "$(git rev-parse HEAD)" --output dist/space
```

## Discipline

Every printed number maps to a fetched fact or is printed as UNAVAILABLE. The crown artifact
sweeps models and datasets together (the models-only sweep undercounted the real crown 24x on
2026-09-30). A draft with one linter violation does not ship, and there is no override flag.
Λ stays Conjecture 1, advisory. The trust ceiling stays 0.97.
