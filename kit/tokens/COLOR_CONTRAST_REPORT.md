# COLOR_TOKENS — WCAG Contrast Verification

SZL Holdings / KANCHAY palette. Ratios computed per WCAG 2.1 relative-luminance formula
([W3C WCAG 2.1 §1.4.3](https://www.w3.org/TR/WCAG21/#contrast-minimum)).
AA threshold: 4.5:1 normal text, 3:1 large text. AAA: 7:1 / 4.5:1.

| Pair | FG | BG | Ratio | AA | AAA | Large |
|---|---|---|---:|:--:|:--:|:--:|
| text on bg | `#f5f7fa` | `#0a0f1e` | 17.79 | PASS | PASS | no |
| text on surface | `#f5f7fa` | `#1b222c` | 14.92 | PASS | PASS | no |
| text-sub on bg | `#c9d2df` | `#0a0f1e` | 12.52 | PASS | PASS | no |
| text-ghost on bg (lg) | `#76859b` | `#0a0f1e` | 5.09 | PASS | PASS | yes |
| yuyay-300 on bg | `#5cc4bf` | `#0a0f1e` | 9.19 | PASS | PASS | no |
| yuyay-200 on bg | `#8fd9d5` | `#0a0f1e` | 11.87 | PASS | PASS | no |
| hatun-300 on bg | `#d7b96b` | `#0a0f1e` | 10.04 | PASS | PASS | no |
| hatun-200 on bg | `#e4cf99` | `#0a0f1e` | 12.44 | PASS | PASS | no |
| yawar-300 on bg | `#e57373` | `#0a0f1e` | 6.39 | PASS | — | no |
| success(light) on bg | `#3fce82` | `#0a0f1e` | 9.42 | PASS | PASS | no |
| warning(light) on bg | `#e4cf99` | `#0a0f1e` | 12.44 | PASS | PASS | no |
| error(light) on bg | `#f0a3a3` | `#0a0f1e` | 9.52 | PASS | PASS | no |
| info(light) on bg | `#7cb8e0` | `#0a0f1e` | 8.9 | PASS | PASS | no |
| gray-900 on gray-50 | `#10151c` | `#f5f7fa` | 17.07 | PASS | PASS | no |
| gray-700 on gray-50 | `#2a3340` | `#f5f7fa` | 11.89 | PASS | PASS | no |
| yuyay-700 on gray-50 | `#0b5957` | `#f5f7fa` | 7.58 | PASS | PASS | no |
| yawar-600 on gray-50 | `#a32a1f` | `#f5f7fa` | 6.73 | PASS | — | no |
| hatun-700 on gray-50 | `#825a18` | `#f5f7fa` | 5.71 | PASS | — | no |
| white on yuyay-600 | `#ffffff` | `#0f726e` | 5.75 | PASS | — | no |
| white on yawar-600 | `#ffffff` | `#a32a1f` | 7.22 | PASS | PASS | no |
| gray-950 on hatun-400 | `#0a0f1e` | `#cda64a` | 8.32 | PASS | PASS | no |

**Result: 21/21 pairs pass WCAG AA (17/21 also pass AAA).**

Apache-2.0 · ORCID 0009-0001-0110-4173 · — Yachay, 2026-06-01

## KANCHAY 1.3.0 semantic roles (2026-10-06)

The table above measures palette scales from an earlier ground (`#0a0f1e`). These are the 1.3.0
semantic roles on their own grounds, computed with the WCAG 2 formula on the token values.
`tests/test_system.py` enforces the floors: text-ghost ≥4.5:1, focus and control-edge ≥3:1 on
every ground, and chip inks ≥4.5:1.

| Surface | Pair | FG | BG | Ratio |
|---|---|---|---|---:|
| dark | text on bg | `#F1F4F8` | `#080B12` | 17.84 |
| dark | text on surface | `#F1F4F8` | `#111722` | 16.28 |
| dark | text-sub on bg | `#AAB7C9` | `#080B12` | 9.68 |
| dark | text-sub on surface-raised | `#AAB7C9` | `#182232` | 7.86 |
| dark | text-ghost on bg | `#8B98AC` | `#080B12` | 6.73 |
| dark | text-ghost on surface-raised | `#8B98AC` | `#182232` | 5.47 |
| dark | link on surface | `#8fd9d5` | `#111722` | 11.16 |
| dark | focus on surface-raised | `#34aaa4` | `#182232` | 5.66 |
| dark | control-edge on surface-raised | `#71829B` | `#182232` | 4.09 |
| dark | accent (coral-400) on bg | `#DF735F` | `#080B12` | 6.33 |
| dark | color-error as text on bg | `#c0392b` | `#080B12` | 3.62 |
| dark | ink-bad (error-light) on bg | `#f0a3a3` | `#080B12` | 9.82 |
| dark | separator on bg (decorative only) | `#2B3749` | `#080B12` | 1.64 |
| light | text on bg | `#111722` | `#F5F3EE` | 16.19 |
| light | text on surface-alt | `#111722` | `#EBEEF2` | 15.43 |
| light | text-sub on bg | `#516075` | `#F5F3EE` | 5.77 |
| light | text-ghost on surface-alt | `#5E6A7C` | `#EBEEF2` | 4.71 |
| light | link on bg | `#0b5957` | `#F5F3EE` | 7.34 |
| light | focus on surface-alt | `#0f726e` | `#EBEEF2` | 4.94 |
| light | control-edge on surface-alt | `#6E7A8C` | `#EBEEF2` | 3.74 |
| light | accent (coral-500) as text on bg | `#C4543F` | `#F5F3EE` | 4.04 |
| light | white on btn-primary (coral-500) | `#FFFFFF` | `#C4543F` | 4.48 |
| light | separator on bg (decorative only) | `#D6DBE3` | `#F5F3EE` | 1.25 |

Separators are decorative and never the only outline of an essential control. Coral and
`--color-error` stay below 4.5:1 as text in the noted cases: use them for large text, marks or
fills, or switch to `--ink-bad`.
