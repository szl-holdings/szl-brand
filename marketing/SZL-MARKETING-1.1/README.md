---
title: SZL-MARKETING-1.1 Governed Fact Factory
emoji: 🛡️
colorFrom: gray
colorTo: blue
sdk: gradio
sdk_version: 5.9.1
app_file: app.py
pinned: false
license: apache-2.0
tags:
- governed-ai
- compliance
- factbase
---

# SZL-MARKETING-1.1 - Governed Fact Factory

A marketing pipeline that cannot lie. Every number is fetched live from the GitHub and
Hugging Face APIs at generation time, and a machine linter enforces the house compliance
guardrails before any draft is allowed to ship.

## Why this exists

Marketing copy rots. A number typed into a document in September is wrong by October, and
nobody notices until a reader does. This Space pulls the estate live instead: model counts,
dataset counts, Space counts, the most-downloaded artifact, and the estate download total.

It also enforces the guardrails as code rather than as a checklist somebody is trusted to
read. A draft that trips a banned pattern is blocked, fail-closed.

## The crown-sweep lesson

The original pipeline ranked only the models endpoint, so a dataset could never win the
crown. It reported a 3,070-download model as the estate's top artifact while the real top
artifact was a dataset with 74,157 downloads - a 24x undercount that would have landed in
every piece of marketing copy. The fix sweeps models and datasets together and records its
own provenance in the output, so the sweep method is auditable rather than assumed.

## Tabs

- **Live facts** - measure the estate now, see the raw factbase JSON
- **Compose + lint** - assemble a compliant draft from live facts, linted before display
- **Lint your own copy** - paste any draft and run the guardrails against it

## Doctrine

Labels stay. The trust ceiling stays 0.97, never 1.0. Lambda stays Conjecture 1, advisory
only. Nothing ships that cannot be verified.

Shipped by the house desk on Rosa's order, 2026-09-30.
