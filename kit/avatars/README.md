# SZL avatar masters

These vector masters are designed for small profile and organization placements. They remove the long wordmark and thin detail that caused the old marks to appear pixelated.

## Files

- `szl-holdings-org-avatar.svg` — organization mark for GitHub and Hugging Face.
- `stephen-lutar-profile-avatar.svg` — founder monogram for the public profile.

## Export

Use a square PNG with no additional crop. Recommended exports:

```bash
python - <<'PY'
from pathlib import Path
import cairosvg

for source in Path("kit/avatars").glob("*.svg"):
    for size in (512, 1024):
        target = source.with_name(f"{source.stem}-{size}.png")
        cairosvg.svg2png(
            bytestring=source.read_bytes(),
            write_to=str(target),
            output_width=size,
            output_height=size,
        )
PY
```

Before upload, verify the PNG is under the provider's current file-size limit and preview it at 32×32 pixels.

The organization avatar and organization card are separate controls. Replacing an avatar does not publish a Hugging Face organization card, and changing a Space `emoji:` field does not replace the organization avatar.
