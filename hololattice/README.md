# hololattice

SZL Holdings signature 3D holographic substrate module — shared across all SZL Spaces.

The hologram is **not decoration**: its geometry is bound to real measured counts
(locked formulas, tests, Lean declarations, measured joules). The module auto-selects
the fastest available renderer: **WebGPU + TSL GPGPU** khipu compute-particle field,
with an automatic silent fallback to the **WebGL2 ShaderMaterial** path.

---

## Public API

```js
import { mountHololattice } from './hololattice.js';

const handle = mountHololattice(container, {
  nodes:  749,        // required: REAL measured count bound to verified data
  accent: 0x36e6d0,   // optional: override core colour (hex number)
  state:  'green',    // optional: 'green' | 'advisory' | 'blocked'  (default 'green')
  label:  'SZL',      // optional: descriptive label string
});
```

### `mountHololattice(container, opts)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `container` | `HTMLElement` | — | DOM element to render into (fills it). |
| `opts.nodes` | `number` | `749` | Node count **must** be a real measured value — never fabricated. Clamped to `[64, 60000]` internally. |
| `opts.accent` | `number \| null` | `null` | Optional hex colour override for the core particle in green state. |
| `opts.state` | `string` | `'green'` | Lattice state — see semantics below. |
| `opts.label` | `string` | `''` | Descriptive label (passed through; use in surrounding UI). |

**Returns** a handle object:

| Property / Method | Description |
|-------------------|-------------|
| `handle.backend` | `'webgpu'` \| `'webgl2'` \| `'webgpu-pending'` — active renderer. |
| `handle.setState(state)` | Transitions the live lattice to a new state without remounting. |
| `handle.destroy()` | Tears down renderer, removes canvas, disconnects observers. |

---

## State semantics

| State | Colour | Meaning |
|-------|--------|---------|
| `'green'` | Teal `#36e6d0` / `#6cf2ff` | All checks pass; lattice tight and ordered. |
| `'advisory'` | Amber `#f4b13e` / `#ffd27a` | Λ advisory flag; lattice gently scattered. Use whenever Λ (Conjecture 1) is the signal — **never** say "proven trust". |
| `'blocked'` | Red `#ff4d5e` / `#ff8a96` | A hard gate failure; lattice visibly broken/scattered. **Honest BLOCKED beats fake green.** |

---

## Importmap (Three.js r0.183.0)

Place this in your `<head>` before any `<script type="module">` that imports from `hololattice.js`:

```html
<script type="importmap">
{
  "imports": {
    "three":           "https://cdn.jsdelivr.net/npm/three@0.183.0/build/three.module.js",
    "three/webgpu":    "https://cdn.jsdelivr.net/npm/three@0.183.0/build/three.webgpu.js",
    "three/tsl":       "https://cdn.jsdelivr.net/npm/three@0.183.0/build/three.tsl.js",
    "three/addons/":   "https://cdn.jsdelivr.net/npm/three@0.183.0/examples/jsm/"
  }
}
</script>
```

---

## Doctrine

- **Nodes must bind to a real measured count.** Never pass a fabricated or rounded-up number. Examples: `749` (Lean declarations), `165` (governed-norm tests), `50` (lambda-gate tests), `67` (energy-attest tests).
- **Λ is advisory — Conjecture 1, uniqueness OPEN.** State `'advisory'` must be used whenever Λ is the signal. Never render `'green'` to mean "proven trust".
- **Honest BLOCKED beats fake green.** If a gate fails, set state `'blocked'`.
- **No fabricated number.** Measured-only. This doctrine is binding across all SZL Holdings outputs.

---

## Live Spaces

| Space | Nodes | State |
|-------|-------|-------|
| [szl-substrate](https://huggingface.co/spaces/SZLHOLDINGS/szl-substrate) | 749 | flagship hub |
| [governed-norm-holo](https://huggingface.co/spaces/SZLHOLDINGS/governed-norm-holo) | 165 | green |
| [lambda-gate-holo](https://huggingface.co/spaces/SZLHOLDINGS/lambda-gate-holo) | 50 | advisory |
| [energy-attest-holo](https://huggingface.co/spaces/SZLHOLDINGS/energy-attest-holo) | 67 | green |

---

## Example

```html
<!DOCTYPE html>
<html>
<head>
  <script type="importmap">
  {
    "imports": {
      "three":        "https://cdn.jsdelivr.net/npm/three@0.183.0/build/three.module.js",
      "three/webgpu": "https://cdn.jsdelivr.net/npm/three@0.183.0/build/three.webgpu.js",
      "three/tsl":    "https://cdn.jsdelivr.net/npm/three@0.183.0/build/three.tsl.js",
      "three/addons/":"https://cdn.jsdelivr.net/npm/three@0.183.0/examples/jsm/"
    }
  }
  </script>
</head>
<body>
  <div id="lattice" style="width:100vw;height:100vh"></div>
  <script type="module">
    import { mountHololattice } from './hololattice.js';
    const h = mountHololattice(document.getElementById('lattice'), {
      nodes: 749, state: 'green', label: 'SZL Substrate'
    });
    // Later: h.setState('advisory');  h.destroy();
  </script>
</body>
</html>
```

---

License: CC-BY-4.0 — Copyright 2026 SZL Holdings.
