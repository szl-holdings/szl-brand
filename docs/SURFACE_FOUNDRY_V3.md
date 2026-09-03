# Surface Foundry v3

Surface Foundry is the controlled visual and information architecture for the public SZL Holdings estate. It generates one coherent company system while giving each GitHub repository and Hugging Face model, kernel, dataset, Space, organization card, and profile a distinct visual fingerprint.

The aim is not to make every page louder. The aim is to make every first screen answer three questions quickly:

1. What is this in plain language?
2. Where does a builder start?
3. What evidence exists, and what does it not prove?

## Design stance

The reference set includes Anthropic, NVIDIA, True Anomaly, New Relic, Kimi, and Boss Technologies. Surface Foundry borrows patterns, not proprietary assets:

- editorial restraint and human-readable hierarchy;
- product-family navigation instead of an undifferentiated asset wall;
- calm mission-control depth rather than decorative cyberpunk noise;
- obvious onboarding and quick-start paths;
- technical depth paired with explicit intended use and limitations.

The result stays recognizably SZL: deep navy, KANCHAY orbit geometry, one luminous node, restrained teal/gold/coral/silver accents, and evidence labels separated from runtime state.

## One company, unique artifacts

Every surface shares:

- the same typography hierarchy and truth language;
- the same investor, builder, and verification paths;
- the same accessibility and mobile rules;
- the same managed README markers;
- the same deterministic receipt format.

Every surface varies deterministically by `kind + slug`:

- one of six geometric systems: aperture, signal lanes, khipu knots, bounded loop, evidence graph, or receipt blocks;
- a family palette for org, profile, platform, repository, model, kernel, dataset, Space, proof, or archive;
- local copy, links, state, evidence label, and limitation disclosure;
- a stable 12-character contract identifier.

A model does not look like a dataset. A proof surface does not look like a product. Archived artifacts are visually quiet. The variation is generated from a reviewed contract, not invented manually on every repository.

## Outputs

For each surface, the generator writes:

- `surface-card.svg` — 1280×640 accessible hero, suitable for README and model-card leads;
- `avatar.svg` — 1024×1024 small-size-safe mark;
- `README.block.md` — investor-readable and developer-usable managed lead;
- `surface.json` — normalized disclosure contract;
- `receipt.json` — SHA-256 binding for the contract, SVG, and README block.

Run:

```bash
szl-surface examples/surfaces.flagship.json --output generated
```

or:

```bash
python -m szl_brand.surface examples/surfaces.flagship.json --output generated
```

Generation is offline and deterministic. It performs no GitHub, Hugging Face, DNS, or deployment write.

## Managed README policy

The generated block is bounded by:

```text
<!-- SZL-SURFACE-CARD:v3:START -->
<!-- SZL-SURFACE-CARD:v3:END -->
```

`replace_managed_block` may replace only that range. It can migrate the legacy `SZL-ESTATE-CARD:v2` range, and it preserves Hugging Face YAML front matter. It refuses malformed or double-managed files.

Repository-specific lead contracts remain authoritative. A source repository may deliberately keep its first screen free of marketing art. In that case the v3 block belongs below the protected lead boundary, not above it.

## Avatar policy

Avatars are not emoji and are not README art. At 24–96 pixels, fine type and thin gradients turn into mush. The avatar system therefore uses:

- a 1024×1024 source;
- a large safe zone;
- no wordmark or tiny copy;
- thick geometry and a single focal node;
- related but distinct organization and founder marks.

The repository stores vector masters. Platform uploads should use exported PNGs because GitHub and Hugging Face profile settings rasterize or crop uploaded images.

## Required card information by artifact type

### Models

- model role and family;
- intended uses and non-uses;
- pinned revision and reproducible inference example;
- architecture and training provenance when known;
- evaluation table with dataset, metric, date, hardware, and revision;
- limitations, license, and safety notes;
- evidence label separate from operational state.

### Kernels

- input/output contract and supported shapes/dtypes;
- hardware and software compatibility;
- benchmark methodology and raw evidence;
- deterministic reference path and known unsupported cases;
- failure behavior and verification command.

### Datasets

- purpose, schema, sample row, and loading command;
- source lineage, refresh date, checksums, and license;
- known gaps, jurisdiction/freshness limits, and consequential-use warning;
- viewer status and reproducibility notes.

### Spaces

- one-sentence outcome;
- operational state and last verified revision;
- input/output example;
- source and evidence links;
- clear SIMULATED, DEMO, PARTIAL, DEGRADED, or UNAVAILABLE disclosure where applicable.

### GitHub repositories

- what the tree is and why it exists;
- product origin and proof origin when relevant;
- five-minute start for builders;
- architecture and ownership boundaries;
- test, security, release, and evidence paths;
- plain-language investor/operator outcome;
- archive or bind status where applicable.

## Workcells

The rollout is divided into parallel workcells with one controller contract:

| Workcell | Responsibility | Exit evidence |
| --- | --- | --- |
| Visual systems | avatars, heroes, responsive art, contrast, crop safety | generated assets, pixel-size previews, accessibility checks |
| Developer experience | quick starts, architecture maps, API examples, reproducibility | commands executed in CI, links checked, examples tested |
| Investor narrative | plain-language outcome, portfolio role, boundaries | first-screen review at 320, 768, and 1440 widths |
| Model and data documentation | model cards, kernel cards, dataset cards, evaluations | required-section census and evidence links |
| Publication | GitHub/Hugging Face deployment, visibility, source binding | immutable revision, live readback, public visibility check |
| Truth and accessibility | claim labels, limitations, keyboard/mobile/readability | policy test, WCAG contrast review, no hidden overflow |

No workcell may silently rewrite another repository's protected lead or turn a failed check green by weakening it.

## Rollout order

1. Restore and harden the public `SZLHOLDINGS/README` organization card.
2. Replace the organization and founder raster avatars with the high-resolution exports.
3. Issue v3 assets to the canonical flagship set: SZL Holdings, A11oy, Killinchu, SZL Kernels, Khipu model family, SZL Lake, and Receipt Verifier.
4. Generate manifests from the complete public estate census and patch active GitHub/Hugging Face cards by pull request.
5. Move duplicates, binds, and historical artifacts to the quiet archive treatment.
6. Add drift checks so every new public surface must declare kind, state, evidence, limitations, source, and proof paths.

## Definition of done

A surface is complete only when:

- its avatar is sharp at 32, 64, 128, and 512 pixels;
- its first screen works at 320, 375, 768, and 1440 CSS pixels;
- a non-technical reader can identify the outcome and boundary in under one minute;
- a developer can find a tested first command and source path;
- evidence and operational state are distinct;
- limitations are visible without expanding a hidden panel;
- links and generated hashes pass CI;
- the live provider page is publicly readable without authentication;
- the deployed revision is recorded.
