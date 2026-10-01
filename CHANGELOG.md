# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- Add the `szl_brand.marketing` engine (`szl-marketing` CLI): a live, labeled estate factbase
  (anonymous GitHub and Hugging Face pulls, models+datasets crown sweep, UNAVAILABLE over guessed,
  backup before overwrite), the Part 2 compliance linter as code (sentence-scoped, disclaimer
  aware, context-gated capability rules; one violation blocks a draft, no override), channel
  drafts with two real A/B subject lines (Substack, Medium, X within 280 characters, LinkedIn),
  the operating plan as data (guardrails, 30-day calendar, 12-story backlog, KPIs, investor
  loop), and exact-projection packages with `PUBLICATION_RECEIPT.json` for the two public
  marketing Spaces. 57 tests. `marketing/space/` is the source of `SZLHOLDINGS/szl-marketing-1.1`
  (Gradio fact factory with a vendored, hashed copy of the engine) and
  `SZLHOLDINGS/szl-brand-campaign` (static hub whose numbers are fetched live in the visitor's
  browser). `hf-marketing-spaces.yml` publishes exactly the tested `main` commit and reads the
  Hub back; `marketing-copy-guard.yml` lints `marketing/` and `posts/` on every pull request.
  `marketing/SZL-MARKETING-1.1/factbase_pipeline.py` becomes a shim over the engine (no more
  absolute `/opt` output path).

- KANCHAY 1.1.1: the base `:focus-visible` rule in `kit/tokens/szl-design-system.css` now draws a
  solid focus outline, `outline:2px solid var(--focus); outline-offset:2px`, and keeps the
  `--shadow-focus` halo and `--radius-sm`. The halo alone (`--focus` at 55%) measured 2.81:1 on
  dark `--bg` and 2.32:1 on light `--bg`, below the 3:1 non-text floor; solid `--focus` measures
  6.73:1 and 5.36:1. No color value changed. `kanchay/` is rebuilt as bundle 1.1.1 (only
  `szl-design-system.css` and `SOURCE.json` differ from 1.1.0), the system version is 1.1.1
  everywhere it is declared, and a test fails CI if the rule loses its solid outline or `--focus`
  drops under 3:1 on any ground.
- Make `kanchay/` the vendor bundle of the one KANCHAY token system, v1.1.0 (founder-approved):
  byte-for-byte copies of `kit/tokens/szl-design-system.css`, the new additive operator layer
  `kit/tokens/szl-console.css` 1.0.0, and the orbit logo suite, with a sha256 `SOURCE.json`.
  `szl-brand kanchay-build [--check]` builds it from `kit/`, and a test fails CI when the bundle
  differs from `kit/`, ships a webfont, or references an undefined token.
- Withdraw the gold `kanchay/` 1.0.0 web export added in #122 (its `kanchay.css`,
  `kanchay-components.*`, `tokens.json`, WOFF2 fonts, marks and `kit/kanchay/components.css`).
  It was withdrawn the same day, before any consumer merged it.
- Add the KHIPU Command System contract, responsive and accessible executive/evidence patterns,
  fail-closed disclosure validation, and reusable repository and organization templates.
- Publish KANCHAY design-system contract v1 with deterministic, SHA-256-pinned exports.
- Add a VitePress adapter, fail-closed public metadata schema, evidence cards, and forced-colors support.
- Replace the test stub with executable Python, lint, formatting, determinism, accessibility, and tamper gates.
- Series-A discipline sweep (Doctrine v6).
