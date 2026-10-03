---
title: SZL-MARKETING-1.1 Governed Fact Factory
emoji: 🛡️
colorFrom: gray
colorTo: blue
sdk: gradio
sdk_version: 6.29.0
app_file: app.py
pinned: false
license: apache-2.0
short_description: Live estate facts and a compliance linter.
tags:
- governed-ai
- compliance
- factbase
- szl-holdings
---

# SZL-MARKETING-1.1 — Governed Fact Factory

A marketing pipeline that cannot type a number. Every figure is fetched anonymously from the
GitHub and Hugging Face APIs at generation time and carries a label (MEASURED or UNAVAILABLE).
A machine linter enforces the house guardrails before any draft exists; a draft with one
violation does not ship.

## Tabs

- **Live facts** — measure the estate now; see the labeled table and the raw factbase JSON
- **Compose + lint** — two real A/B subject lines plus the team's essay body become a Substack
  draft and an X thread, assembled from live facts and linted before display
- **Lint your own copy** — paste any draft and run the guardrails against it
- **Operating plan** — guardrails, 30-day calendar, story backlog, KPIs, investor loop
- **Provenance** — the exact GitHub source revision and package hash this Space was built from

## Why the crown sweeps datasets

The first pipeline ranked only the models endpoint, so a dataset could never be the estate's
most-downloaded artifact. The fix sweeps models and datasets together and records the sweep
method in the output so it cannot regress silently.

## Source of truth

This Space is an exact projection of
[szl-holdings/szl-brand](https://github.com/szl-holdings/szl-brand) (`marketing/space/szl-marketing-1.1`
plus a vendored, hashed copy of `szl_brand.marketing`). `PUBLICATION_RECEIPT.json` names the
source commit and every file hash. Edit the GitHub source; do not edit the Space.

The 2026-09-30 `PAYLOAD-SZL-MARKETING-1.1.md`, `factbase.json`, and
`factbase_pipeline.py` are retained byte for byte from the earlier public Space revision
`77b3e70533e0116ba6b6b434c18e34e322ef3b3b` for provenance. They are historical
snapshots; the active app uses the vendored engine and fetches fresh facts.

Doctrine: labels stay. The trust ceiling stays 0.97, never 1.0. Λ stays Conjecture 1, advisory.
