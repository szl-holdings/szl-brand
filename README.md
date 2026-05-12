# szl-brand

**SZL Holdings brand assets.** Source-of-truth for social preview images, logo monograms, and brand guidance applied across the GitHub organization.

## Social previews

Eleven 1280×640 PNG social previews (one per public repo), generated from a deterministic Python builder. These render in link unfurls on Twitter/X, LinkedIn, Slack, iMessage, and the GitHub repo card.

### Catalog

| Repo | Preview | Bytes |
|------|---------|-------|
| [a11oy](https://github.com/szl-holdings/a11oy) | [`social-previews/a11oy.png`](social-previews/a11oy.png) | ~25KB |
| [ouroboros](https://github.com/szl-holdings/ouroboros) | [`social-previews/ouroboros.png`](social-previews/ouroboros.png) | ~28KB |
| [ouroboros-thesis](https://github.com/szl-holdings/ouroboros-thesis) | [`social-previews/ouroboros-thesis.png`](social-previews/ouroboros-thesis.png) | ~28KB |
| [sentra](https://github.com/szl-holdings/sentra) | [`social-previews/sentra.png`](social-previews/sentra.png) | ~24KB |
| [vessels](https://github.com/szl-holdings/vessels) | [`social-previews/vessels.png`](social-previews/vessels.png) | ~24KB |
| [terra](https://github.com/szl-holdings/terra) | [`social-previews/terra.png`](social-previews/terra.png) | ~23KB |
| [counsel](https://github.com/szl-holdings/counsel) | [`social-previews/counsel.png`](social-previews/counsel.png) | ~25KB |
| [carlota-jo](https://github.com/szl-holdings/carlota-jo) | [`social-previews/carlota-jo.png`](social-previews/carlota-jo.png) | ~27KB |
| [amaru](https://github.com/szl-holdings/amaru) | [`social-previews/amaru.png`](social-previews/amaru.png) | ~25KB |
| [szl-cookbook](https://github.com/szl-holdings/szl-cookbook) | [`social-previews/szl-cookbook.png`](social-previews/szl-cookbook.png) | ~25KB |
| [szl-trust](https://github.com/szl-holdings/szl-trust) | [`social-previews/szl-trust.png`](social-previews/szl-trust.png) | ~22KB |

### How to apply (one-time, ~2 min per repo)

GitHub does not expose social-preview upload through the API for this organization's auth proxy — it must be set via the web UI.

For each repo:

1. Open `github.com/szl-holdings/<repo>/settings`
2. Scroll to **Social preview**
3. Click **Edit** → **Upload an image**
4. Pick the matching PNG from this repo's `social-previews/` folder
5. **Save**

After save, verify by visiting `github.com/szl-holdings/<repo>` and watching the OG image render in any link preview.

### Design system

- **Canvas:** 1280×640 (GitHub's recommended OG dimensions)
- **Background:** vertical gradient `#0a0a0f → #12121a`
- **Accent:** SZL purple `#805ad5` (left 6px accent bar + bottom hairline + pill border + stat values + monogram)
- **Type:** DejaVu Sans (system-ui fallback in the SVG variants)
- **Layout:** kicker / title (78px bold) / subtitle (26px regular) / tag pill / three 220×100 stat cards / footer with `github.com/szl-holdings` left and `SZL` monogram right
- **Stat cards:** translucent white fill, hairline stroke, purple stat value, muted label

### Regenerating

```bash
python3 social-previews/gen.py
```

Edits the `REPOS` table at the top of `gen.py` to add new repos or change any of the per-repo content (kicker, title, subtitle, tag, three stat triples).

## License

Brand assets: CC BY 4.0 (attribution required if you remix the design system; the SZL wordmark and color are reserved).
