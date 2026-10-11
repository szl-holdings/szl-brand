<div align="center">

<img src="./kit/logos/orbit-v2/szl-orbit.svg" alt="SZL Holdings" width="96" height="96" />

# KANCHAY design system

The versioned visual and public-claim system for SZL Holdings.

[Documentation](https://holdings.a-11-oy.com/docs-site/brand.html) · [GitHub organization](https://github.com/szl-holdings) · [Hugging Face](https://huggingface.co/SZLHOLDINGS) · [Security](./SECURITY.md)

</div>

## One system, four guarantees

KANCHAY makes an SZL surface recognizable without letting presentation outrun evidence.

| Contract | What it guarantees |
|---|---|
| **Tokens** | A single color, type, spacing, radius, elevation, and motion vocabulary. |
| **Components** | Accessible buttons, cards, status chips, receipts, control docks, navigation, and evidence panels. |
| **Metadata** | Every public page declares its source, evidence URL, canonical URL, and honest status. |
| **Adapters** | Deterministic framework bundles with SHA-256 integrity and an exact source revision. |

The design system is calm, technical, and evidence-forward. Coral is the decision accent; teal
is the interaction and focus color; gold is reserved for doctrine and premium emphasis. Status is
always written in text and never communicated by color alone.

## Quickstart

The SDK requires Python 3.12 or newer.

```bash
git clone https://github.com/szl-holdings/szl-brand.git
cd szl-brand
python -m pip install -e ".[dev]"
python -m pytest tests -q
```

Export a byte-deterministic design-system bundle from an immutable source revision:

```bash
python -m szl_brand export-system \
  --source-revision "$(git rev-parse HEAD)" \
  --output ./dist/kanchay
```

The export contains:

| File | Purpose |
| --- | --- |
| `manifest.json` | Contract, version, exact source, per-file hashes and bundle root hash. |
| `system.css` | Tokens, components, focus and reduced-motion behavior. |
| `tokens.json` | Typed token source and measured contrast pairs. |
| `metadata.schema.json` | Public metadata convention. |
| `vitepress.css` | Framework adapter. |
| `khipu-command-system.css`, `khipu-command-system.schema.json`, `khipu-command-system.example.json` | Command surface styles, contract and example. |
| `repository-readme-template.md`, `org-card-template.md` | Managed front-door templates. |
| `repository-hero-template.svg`, `org-card-template.svg`, `executive-brief-template.html` | Native presentation templates. |
| `szl-orbit.svg`, `szl-avatar.svg` | Exact approved Orbit v2 master and round-crop avatar projection. |

Identical inputs and the same source SHA produce byte-identical outputs. Checkout exports read the
asset blobs from the canonical repository's exact `HEAD`; wheel exports require build-embedded
revision and per-asset hashes. Mutable refs, mismatched revisions, forks, abbreviated SHAs,
uppercase SHAs, and path-like values are rejected.

[Surface Foundry](./docs/SURFACE_FOUNDRY_V3.md) uses that same bound avatar source for every
generated parent identity. Its Space artwork preserves the supplied operational state;
unknown, deprecated and roadmap contracts remain explicit.

## Vendor bundle (`kanchay/`)

KANCHAY has one token system: [`kit/tokens/szl-design-system.css`](./kit/tokens/szl-design-system.css)
(v1.3.0, founder-approved) and its additive operator layer
[`kit/tokens/szl-console.css`](./kit/tokens/szl-console.css) (v1.2.0).
[`kanchay/`](./kanchay) is the ready-to-vendor bundle of that system: byte-for-byte copies of both
stylesheets and the orbit logo suite, with `SOURCE.json` pinning each file's sha256. Surfaces copy
it into a static folder named `szl/`, link `szl-design-system.css` before their own stylesheet, and
load no webfonts. [`kanchay/README.md`](./kanchay/README.md) has the steps, the dark operator and
light marketing surfaces, and the one-coral-moment rule. The art direction is
[`docs/DESIGN_DIRECTION.md`](./docs/DESIGN_DIRECTION.md).

The [native component specimen](./kit/examples/html/components.html) demonstrates both
polarities, nested panels, readable action states, the silver/teal material edge, explicit sample
evidence, and a graphite terminal. It uses the canonical CSS and existing Orbit SVG directly.

```bash
python -m szl_brand kanchay-build --check  # fail if kanchay/ differs from kit/
```

## Use the system

For a plain web surface:

```html
<link rel="stylesheet" href="/brand/system.css">
```

```html
<article class="evidence-card">
  <header class="evidence-card__header">
    <h2 class="evidence-card__title">Runtime readiness</h2>
    <span class="chip chip-proven">REAL</span>
  </header>
  <dl class="evidence-card__meta">
    <div><dt>Source</dt><dd><code>cad529a2...</code></dd></div>
    <div><dt>Evidence</dt><dd><a href="/evidence">Open verification</a></dd></div>
  </dl>
</article>
```

For VitePress, keep `vitepress.css`, `system.css`, and the manifest together, then import the
adapter from the theme entry point. The adapter consumes only canonical KANCHAY tokens and has no
runtime font or stylesheet dependency.

## Repository map

| Path | Responsibility |
|---|---|
| [`kanchay`](./kanchay) | Vendor bundle of KANCHAY v1.3.0: design system, console layer, logos, `SOURCE.json`. |
| [`kit/tokens`](./kit/tokens) | Canonical typed tokens, component stylesheet, and operator console layer. |
| [`kit/contracts`](./kit/contracts) | Public metadata and truth-label schemas. |
| [`kit/adapters`](./kit/adapters) | Deterministic framework adapters. |
| [`docs/FRONTEND_HARDENING.md`](./docs/FRONTEND_HARDENING.md) | Estate-wide responsive, accessibility, state, performance, and PR acceptance contract. |
| [`src/szl_brand`](./src/szl_brand) | Export, integrity, validation, preview, and CLI implementation. |
| [`tests`](./tests) | Determinism, tamper, accessibility, metadata, CLI, palette, and asset gates. |
| [`social-previews`](./social-previews) | Deterministically generated GitHub preview assets. |
| [`anatomy`](./anatomy) | Visual anatomy source and rendered figures. |
| [`motion`](./motion) | Governed motion studies and exports. |

## Truth and accessibility contract

- Public metadata status vocabulary is exactly `REAL`, `MEASURED`, `MODELED`, `ROADMAP`, or `UNAVAILABLE`.
- Surface Foundry's evidence and operational-state vocabularies are separate, documented contracts.
- Every metadata record requires source and evidence URLs.
- Focus is visible, status has a text label, and forced-colors mode keeps state indicators legible.
- `prefers-reduced-motion: reduce` collapses nonessential animation and transition duration.
- The exported VitePress adapter has no runtime CDN or font download.
- The current supply-chain posture is SLSA L1; stronger levels are not claimed here.
- Front-end consumers follow the [`KANCHAY hardening standard`](./docs/FRONTEND_HARDENING.md),
  including control-dock ownership, safe areas, truthful runtime states, and Core Web Vitals budgets.

See [`kit/brand-bible.md`](./kit/brand-bible.md) for voice and naming, and
[`kit/tokens/COLOR_CONTRAST_REPORT.md`](./kit/tokens/COLOR_CONTRAST_REPORT.md) for measured contrast
pairs.

## Generate and validate social previews

```bash
python -m szl_brand generate --output social-previews
python -m szl_brand validate social-previews
python -m szl_brand manifest social-previews --output brand-manifest.json
python -m szl_brand drift --manifest brand-manifest.json social-previews
```

The GitHub social preview is a repository setting, so generated images remain reviewable artifacts;
this repository does not silently mutate other repositories.

## Governance

Changes use protected pull requests, executable tests, and normal branch
protection. Brand doctrine is additive to the locked proof register and does not change theorem,
axiom, or `sorry` counts.

- Repository content: CC BY 4.0 under [`LICENSE`](./LICENSE) and [`NOTICE`](./NOTICE).
- Trademark reservation: the SZL Holdings name, wordmark, and brand colors are not granted by CC BY 4.0; see [`NOTICE`](./NOTICE).
- Some individual files carry additional SPDX notices; those notices are preserved as file-specific metadata and are not silently recharacterized here.
- Attribution: SZL Holdings, ORCID `0009-0001-0110-4173`.

## Citation

```bibtex
@software{szl_holdings_kanchay_2026,
  title   = {KANCHAY: the SZL Holdings design system},
  author  = {{SZL Holdings}},
  year    = {2026},
  version = {1.3.0},
  doi     = {10.5281/zenodo.20434276},
  url     = {https://github.com/szl-holdings/szl-brand}
}
```
