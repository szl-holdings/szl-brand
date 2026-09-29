# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
