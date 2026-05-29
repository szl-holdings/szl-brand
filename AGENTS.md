# AGENTS.md

## Cursor Cloud specific instructions

This is a **brand asset generation toolkit** (not a running web service). It contains Python scripts that produce social-preview PNGs and anatomy PDFs.

### Services & scripts

| Script | Purpose | Command |
|--------|---------|---------|
| `social-previews/gen.py` | Generate 14 social-preview banners (1280×640 PNG) | `python3 social-previews/gen.py` |
| `anatomy/scripts/rebuild_all.sh` | Rebuild all anatomy figure PDFs/PNGs | `bash anatomy/scripts/rebuild_all.sh` |

### Linting

```bash
ruff check .          # lint (config in pyproject.toml)
ruff format --check . # format check
```

### Key dependencies

- **Python 3.12** — required runtime
- **Pillow** — PNG banner generation (`social-previews/gen.py`)
- **ReportLab** — PDF figure generation (`anatomy/scripts/build_anatomy_*.py`)
- **poppler-utils** (`pdftoppm`) — some anatomy scripts convert PDF→PNG
- **DejaVu fonts** — referenced by `gen.py` at `/usr/share/fonts/truetype/dejavu/`
- **Ruff** — linting/formatting
- **pre-commit** — git hooks (trailing whitespace, YAML checks, ruff)

### Non-obvious caveats

1. **Anatomy scripts write to hard-coded absolute paths** outside the repo (e.g. `/home/user/workspace/field_meditation/` and `/home/user/workspace/evolution_pod/finish/anatomy/figures/`). You must create these directories before running `rebuild_all.sh`:
   ```bash
   sudo mkdir -p /home/user/workspace/field_meditation
   sudo mkdir -p /home/user/workspace/evolution_pod/finish/anatomy/figures
   sudo chmod -R 777 /home/user/workspace
   ```
2. **`build_explainer_pdfs.py`** requires markdown source files from external paths and will fail unless those files exist — this is expected in isolation.
3. **No `[project]` table in `pyproject.toml`** — the repo has no installable package. Install deps directly with `pip install Pillow reportlab ruff pre-commit`.
4. **The CI workflow** (`.github/workflows/ci.yml`) only validates that asset files exist and are valid; it does not run the generation scripts.
