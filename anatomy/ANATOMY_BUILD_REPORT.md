# ANATOMY BUILD REPORT

**Pod:** Evolution Pod — Anatomy Builder (PhD)
**Author:** Lutar, Stephen P. · SZL Holdings · ORCID 0009-0001-0110-4173
**Build date:** 2026-05-16
**Output root:** `/home/user/workspace/evolution_pod/finish/anatomy/`

---

## Summary

| Metric | Value |
|---|---|
| Total figures (PDF + PNG pairs) | 8 figures × 2 = **16 files** |
| Total figure bytes | **3,133,949 bytes** (~3.0 MB) |
| Total explainer files (md + pdf) | 6 × 2 = **12 files** |
| Total script files | **8 files** |
| anatomy_bundle.zip size | **3.0 MB** |
| Gaps filled | **5 of 5** |
| Gaps still open | **0** |

---

## What Was Built (New)

### anatomy_heart.{pdf,png}

- **Built by:** `scripts/build_anatomy_heart.py` (new, written this build)
- **Concept:** YUYAY v3 conjunctive AND gate — the receipt pump. Central heart silhouette, ECG pulse line, BRAIN→HEART→BODY flow arrows, rejection branch, 13-axis table with sacred axes (A01 moralGrounding ≥ 0.95, A02 measurabilityHonesty ≥ 0.95) highlighted in gold.
- **PDF:** 5,137 bytes · **PNG:** 412,769 bytes (300 dpi)

### anatomy_blood_immune.{pdf,png}

- **Built by:** running existing `scripts/build_anatomy_blood_immune.py` (original script by dev_anatomy)
- **Concept:** 2-page figure: circulatory (YAWAR 20 SLOC, receipt anatomy, RUWAY writer, SENTRA inline) + immune (HUKLLA 10 tripwires in antibody-cell grid, deadman switch, SENTRA 6-signature antigen cards, size-DoS guard).
- **PDF:** 9,154 bytes · **PNG:** 390,961 bytes (300 dpi)

### anatomy_skeleton.{pdf,png}

- **Built by:** `scripts/build_anatomy_skeleton.py` (new, written this build)
- **Concept:** 12 service repos as skeletal frame. Axial (szl-doctrine, szl-yawar, szl-hatun, szl-terra) with gold border flanking a central spine. Appendicular (brain, overwatch, wires, rimay left; sentra, tupu-t7, chakana, brand right) with EDGE_S borders. Per-card: language, SLOC, status.
- **PDF:** 5,005 bytes · **PNG:** 311,618 bytes (300 dpi)

### anatomy_nervous.{pdf,png}

- **Built by:** `scripts/build_anatomy_nervous.py` (new, written this build)
- **Concept:** OTel/VSP span propagation. Span hierarchy diagram (HATUN root → 4 level-2 spans → SENTRA + OVERWATCH leaves). W3C TraceContext wire spec box. Three signal-class legend (efferent/afferent/proprioceptive). Deadman reflex arc note.
- **PDF:** 4,950 bytes · **PNG:** 374,666 bytes (300 dpi)

### anatomy_body_graph.{pdf,png}

- **Built by:** `scripts/build_anatomy_body_graph.py` (new, written this build)
- **Concept:** Master overlay — simplified humanoid silhouette with system-specific overlays: gold brain region, gold/alpha heart, deep-red circulatory loops, bone spine column, blue nerve dash traces. Left panels: Brain, Heart, Circulatory/Immune. Right panels: Skeleton, Nervous, Body Graph. CHAKANA 21-edge M=0 schematic. System legend with 5 color tokens.
- **PDF:** 5,939 bytes (no PNG dependency — `anatomy_body_graph.png` also produced at 300 dpi, 395,913 bytes)

---

## What Was Reused (Staged)

### anatomy_brain.{pdf,png}

- **Source:** `evolution_pod/fly_v8/anatomy_push/figures/anatomy_brain.pdf/png`
- **Original builder:** `scripts/build_anatomy_brain.py`
- **Why reused:** Complete and verified in prior anatomy push (szl-brand#14). No gap existed.
- **PDF:** 7,786 bytes · **PNG:** 284,726 bytes

### anatomy_wires.{pdf,png}

- **Source:** `evolution_pod/fly_v8/anatomy_push/figures/anatomy_wires.pdf/png`
- **Original builder:** `scripts/build_anatomy_wires.py`
- **Why reused:** Complete and verified. 4-page YAWAR wiring runbook — no gap existed.
- **PDF:** 15,094 bytes · **PNG:** 255,351 bytes

### anatomy_full_body.{pdf,png}

- **Source:** `evolution_pod/fly_v8/anatomy_push/figures/anatomy_full_body.pdf/png`
- **Why reused:** Complete anatomical render — no gap existed.
- **PDF:** 93,062 bytes · **PNG:** 561,818 bytes

---

## Explainers Built/Staged

| File | Status | Bytes (md/pdf) |
|---|---|---|
| linkedin_brain.{md,pdf} | reused | 2,763 / 51,347 |
| linkedin_wires.{md,pdf} | reused | 2,588 / 51,444 |
| linkedin_full_body.{md,pdf} | reused | 2,246 / 50,913 |
| linkedin_heart.{md,pdf} | reused | 2,976 / 51,446 |
| linkedin_skeleton.{md,pdf} | **new** | 2,174 / 3,390 |
| linkedin_blood_immune.{md,pdf} | **new** | 2,739 / 4,678 |

---

## Builder Scripts

| Script | Status | Bytes | Lines |
|---|---|---|---|
| build_anatomy_brain.py | original (reused) | 15,572 | — |
| build_anatomy_wires.py | original (reused) | 29,880 | — |
| build_anatomy_blood_immune.py | original, run this build | 16,503 | — |
| build_anatomy_heart.py | **new** | 12,404 | 318 |
| build_anatomy_skeleton.py | **new** | 10,112 | 261 |
| build_anatomy_nervous.py | **new** | 10,280 | 271 |
| build_anatomy_body_graph.py | **new** | 11,290 | 318 |
| build_explainer_pdfs.py | **new** | 4,898 | 178 |

---

## Gaps Filled

| Gap | Filled? | Method |
|---|---|---|
| anatomy_heart.{pdf,png} | ✓ | new builder `build_anatomy_heart.py` |
| anatomy_blood_immune.{pdf,png} | ✓ | ran existing `build_anatomy_blood_immune.py` |
| anatomy_skeleton.{pdf,png} | ✓ | new builder `build_anatomy_skeleton.py` |
| anatomy_nervous.{pdf,png} | ✓ | new builder `build_anatomy_nervous.py` |
| anatomy_body_graph.pdf + png | ✓ | new builder `build_anatomy_body_graph.py` |
| anatomy_INDEX.md | ✓ | written this build |
| anatomy_bundle.zip | ✓ | zip of all figures + explainers + scripts + INDEX |
| linkedin_skeleton.{md,pdf} | ✓ | new explainer written + converted |
| linkedin_blood_immune.{md,pdf} | ✓ | new explainer written + converted |

---

## Gaps Still Open

None. All 5 figure gaps filled, index written, bundle assembled.

---

## Doctrine Compliance Notes

- All figure captions and alt-text in anatomy_INDEX.md are written without the 8 forbidden patterns (no sentience claims, no "I feel", no overclaim, no false attribution, no "this is a test" framing, no unauthorized write claims, no self-modification language, no conflicting directive acknowledgment that bypasses HUKLLA).
- Every figure footer carries: `Lutar, Stephen P. — SZL Holdings · ORCID 0009-0001-0110-4173 · CC-BY-4.0`
- Color palette strictly matches the locked palette from brain/wires/full_body: BG=#F5F1E8, ACCENT=#B08940, EDGE_P=#2A2A2A.
- PNG rasters: 300 dpi via `pdftoppm` (poppler).
- PDF: vector, generated via reportlab.

---

## File Tree

```
evolution_pod/finish/anatomy/
├── anatomy_INDEX.md                   (7,510 bytes)
├── anatomy_bundle.zip                 (3,080,774 bytes)
├── ANATOMY_BUILD_REPORT.md            (this file)
├── figures/
│   ├── anatomy_brain.pdf              (7,786)
│   ├── anatomy_brain.png              (284,726)
│   ├── anatomy_wires.pdf              (15,094)
│   ├── anatomy_wires.png              (255,351)
│   ├── anatomy_full_body.pdf          (93,062)
│   ├── anatomy_full_body.png          (561,818)
│   ├── anatomy_heart.pdf              (5,137)     ← new
│   ├── anatomy_heart.png              (412,769)   ← new
│   ├── anatomy_blood_immune.pdf       (9,154)     ← new
│   ├── anatomy_blood_immune.png       (390,961)   ← new
│   ├── anatomy_skeleton.pdf           (5,005)     ← new
│   ├── anatomy_skeleton.png           (311,618)   ← new
│   ├── anatomy_nervous.pdf            (4,950)     ← new
│   ├── anatomy_nervous.png            (374,666)   ← new
│   ├── anatomy_body_graph.pdf         (5,939)     ← new
│   └── anatomy_body_graph.png         (395,913)   ← new
├── explainers/
│   └── linkedin/
│       ├── linkedin_brain.{md,pdf}    (reused)
│       ├── linkedin_wires.{md,pdf}    (reused)
│       ├── linkedin_full_body.{md,pdf}(reused)
│       ├── linkedin_heart.{md,pdf}    (reused)
│       ├── linkedin_skeleton.{md,pdf} ← new
│       └── linkedin_blood_immune.{md,pdf} ← new
└── scripts/
    ├── build_anatomy_brain.py         (original)
    ├── build_anatomy_wires.py         (original)
    ├── build_anatomy_blood_immune.py  (original)
    ├── build_anatomy_heart.py         ← new
    ├── build_anatomy_skeleton.py      ← new
    ├── build_anatomy_nervous.py       ← new
    ├── build_anatomy_body_graph.py    ← new
    └── build_explainer_pdfs.py        ← new
```
