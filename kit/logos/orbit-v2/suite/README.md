<!-- SPDX-License-Identifier: Apache-2.0
(c) 2026 Lutar, Stephen P. - SZL Holdings - ORCID 0009-0001-0110-4173 -->

# Orbit v2 asset suite

One placement per file, all derived from the approved master
[`../szl-orbit.svg`](../szl-orbit.svg). The generator `src/szl_brand/orbit_suite.py` reuses the
master's exact letter outlines, orbit angle, node and palette. Nothing here is redrawn by hand,
and no font is read. `manifest.json` pins every file by sha256 next to the master's sha256.

## Which file goes where

| Placement | File | Notes |
|---|---|---|
| Hero, card header, about page (64 px and up) | `szl-orbit.svg` | The master, byte for byte. |
| Feature or hero moment on a dark field | `szl-orbit-holo.svg` | Restrained silver material: a quiet light plane, silver edge light and a warm glint at the node. Use it once per page at most. |
| Light ground with no tile | `szl-orbit-mono-navy.svg` | One color. The orbit is cut around the letters so it cannot merge into them. |
| Dark ground with no tile | `szl-orbit-mono-white.svg` | Same, in white. |
| UI marks of 24 to 48 px | `szl-icon-32.svg`, `png/favicon-32.png`, `png/favicon-48.png` | Larger letters, one orbit with a gap around the letters, the node, and no lambda. |
| 20 px and smaller | `szl-icon-16.svg`, `png/favicon-16.png` | Letters and the coral node only. An orbit cannot render at this size. |
| Browser tab | `favicon.ico` (16, 32 and 48 px) plus `szl-icon-32.svg` as the SVG icon | |
| GitHub and Hugging Face organization avatar | `png/szl-avatar-1024.png` (or `-512`) | Full-bleed square. Everything stays inside the round crop, so no platform cut touches the mark. |
| Apple touch icon, PWA icons | `png/apple-touch-icon-180.png`, `png/icon-192.png`, `png/icon-512.png` | Full bleed; the platform applies its own corner shape. |
| PWA maskable icon | `png/icon-maskable-512.png` | Content sits inside the central 80% safe zone. |
| Social preview (Open Graph, X, LinkedIn) | `png/szl-social-1200x630.png` | The mark on a graphite field with two quiet silver orbits. |
| Print or large raster | `png/szl-orbit-1024.png`, `png/szl-orbit-holo-1024.png`, mono 1024 PNGs | Transparent outside the tile. |

## Rules

- Use the master at 64 px and up, `szl-icon-32` from 24 to 48 px, and `szl-icon-16` at 20 px and
  below. Never scale the master below 64 px.
- Keep clear space of at least one quarter of the mark's width on every side, and never place text
  or other marks inside it.
- Do not recolor, rotate, stretch, outline, add shadows, or re-letter the mark. Use the provided
  single-color variants instead of recoloring.
- Coral appears once: the node. Do not add coral elsewhere in the same mark.
- The lambda is identity artwork. It does not assert that Conjecture 1 is proved.
- Brand badges carry identity; status badges carry state. Never use the mark as a status indicator.
- Account avatars and repository social-preview images are platform settings, not repository
  files. Publishing this suite does not change them; record each settings change separately.

## Rebuild or check

```bash
pip install resvg-py          # only needed to render the PNG and ICO exports
szl-brand orbit-suite         # rebuild every vector and raster, and manifest.json
szl-brand orbit-suite --check # rebuild vectors and verify every recorded hash (no renderer needed)
```

`tests/test_orbit_suite.py` runs the check in CI. It fails if any of these is true:

- a vector differs from the build, or a file differs from its manifest hash;
- a vector loses the master's letter outlines or its accessible name;
- a small icon keeps detail that cannot render at its size;
- avatar content leaves the round crop or the maskable safe zone;
- a single-color variant uses a second color;
- the holographic variant leaves the house palette.

## Status

`deployment_status` is `NOT_ATTESTED`. A placement is live only after the consumer's own source
change is merged, published, and read back at its exact revision.
