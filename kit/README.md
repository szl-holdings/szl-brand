# KANCHAY kit

This directory is the canonical, versioned design-system source consumed by the `szl-brand` SDK.

| Directory | Contract |
|---|---|
| [`tokens`](./tokens) | Color, typography, spacing, radius, elevation, motion, components, and contrast evidence. |
| [`contracts`](./contracts) | Fail-closed metadata conventions for truthful public surfaces. |
| [`adapters`](./adapters) | Framework mappings generated into consumer repositories. |
| [`logos`](./logos) | Primary, horizontal, monochrome, favicon, and glyph assets. |
| [`fonts`](./fonts) | Font licenses and self-hosting guidance. |
| [`examples`](./examples) | Plain HTML, React, and Vue examples. |

Generate a consumer bundle from the repository root:

```bash
python -m szl_brand export-system \
  --source-revision "$(git rev-parse HEAD)" \
  --output ./dist/kanchay
```

Consumers must pin the generated `manifest.json`, keep the four exported assets together, and
verify their SHA-256 hashes before publication. The initial production adapter targets VitePress;
other adapters remain outside the v1 contract until they have executable consumer tests.

The exporter binds checkout bytes to the canonical repository's exact `HEAD`. Built wheels carry
that revision plus per-asset hashes as generated build provenance, so a caller-supplied SHA cannot
relabel either source mode.

The codenames `amaru`, `sentra`, and `rosie` are retired product names. The serpent remains a visual
motif only. See [`brand-bible.md`](./brand-bible.md) for the full naming and public-claim lock list.
