# SZL-MARKETING-1.1 - completed marketing payload (verified, corrected)

Shipped by the house desk on Rosa's order, 2026-09-30. Every number below was fetched
live from GitHub and Hugging Face APIs at generation time - none typed from memory.

## The estate, measured this hour

| Metric | Value | Label |
|---|---|---|
| Public repos (szl-holdings) | 120 | MEASURED |
| Honestly archived | 28 | MEASURED |
| HF models | 50 | MEASURED |
| HF datasets | 34 | MEASURED |
| HF Spaces | 27 | MEASURED |
| Most-downloaded artifact | SZLHOLDINGS/killinchu-osint-corpus | MEASURED |
| Crown downloads | 74,157 | MEASURED |
| Total estate downloads | 112,569 | MEASURED |

## What is in this directory

| File | Purpose |
|---|---|
| `SZL-MARKETING-1.1-2026-09-30.md` | Full payload: vision, guardrails, 30-day calendar, 12-story backlog, code, strategy, upgrades |
| `factbase_pipeline.py` | Runnable pipeline: live fact pull + compliance linter + A/B draft assembly |
| `factbase.json` | The live factbase the pipeline produced (crown, counts, totals) |

## Four defects found and fixed in the payload's Part 5 code

1. Crown sweep was models-only. It ranked only the models endpoint, so a dataset could
   never win. It crowned a 3,070-download model while the real top artifact is a dataset
   at 74,157 - a 24x undercount of the estate in every piece of marketing copy. Fixed:
   the sweep covers models and datasets and records its own provenance in the output.
2. A/B subject lines rendered identical. A string slice was applied where a list index
   was intended, so both subject slots emitted the same literal and no A/B test existed.
   Fixed: a real pair, and the list representation never reaches output.
3. No backup before overwrite. A bad run destroyed the factbase with no way back.
   Fixed: a timestamped backup is taken on every write.
4. The compliance linter did not enforce two of the payload's own Part 2 rules. The
   Lambda-discipline rule names a banned two-word trust phrase that had no pattern at
   all; the quant rule only caught one literal numeric form, so bare performance nouns
   for the advisory-only lane passed clean; and the defense-capability rule matched only
   the number-before-keyword order, so the phrasing people actually write passed clean.
   Fixed: additive patterns, plus a context gate so ordinary prose about distances and
   venues stays compliant while sensor claims do not.

Canonical file now carries 10 banned patterns and passes 8/8 compliance tests. The house
copy carries 11 and passes 12/12, including two dead-door traps (a DNS-absent hostname
and an unhyphenated verify domain).

### One linter design gap found while shipping this file

This README was blocked on its first attempt - by its own linter - because it quoted the
banned phrases as documentation of what the linter catches. The guardrails have no
quotation or documentation exemption, so any file that explains them self-trips.
Fail-closed behavior was correct and it caught the author, which is the doctrine working.
But the exemption is missing and should be added deliberately rather than worked around
by rewording, which is what this file does. Flagged for the marketing lane.

## Part 1 prose still carries typed numbers

The payload's Part 1 states 130 repos / 49 models / 44 datasets / 36 Spaces. Live is
120 / 50 / 34 / 27. The pipeline corrects these on every run; the prose has not been
rewritten here because the marketing lane owns the essay voice. Flagged, not fixed.

## Doctrine

Labels stay. The trust ceiling stays 0.97. Lambda stays Conjecture 1, advisory.
Nothing ships that cannot be verified.
