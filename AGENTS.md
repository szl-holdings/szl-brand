# AGENTS.md

## Cursor Cloud specific instructions

### Overview

This is a **brand asset repository** (not a runnable web application). The "application" consists of Python scripts that generate social-preview banner images (1280×640 PNG) and anatomy PDF figures.

### Key commands

| Task | Command |
|------|---------|
| Lint | `ruff check .` |
| Format check | `ruff format --check .` |
| Generate social previews | `python3 social-previews/gen.py` (outputs to `/tmp/social-previews/`) |
| Rebuild anatomy figures | `bash anatomy/scripts/rebuild_all.sh` |

### Dependencies

- **Python 3.12** (system Python)
- **Pillow** — image generation for `social-previews/gen.py`
- **reportlab** — PDF generation for `anatomy/scripts/`
- **ruff** — linting/formatting (configured in `pyproject.toml`)
- **pre-commit** — hooks defined in `.pre-commit-config.yaml`

Install all with: `pip install pillow reportlab ruff pre-commit`

### Non-obvious caveats

1. **No `pyproject.toml` `[project]` section** — dependencies are not formally declared. The `pyproject.toml` only configures ruff/black/mypy tools.
2. **Anatomy scripts have hardcoded output paths** to `/home/user/workspace/evolution_pod/finish/anatomy/figures/`. To run them locally, create that directory: `sudo mkdir -p /home/user/workspace/evolution_pod/finish/anatomy/figures && sudo chmod 777 /home/user`.
3. **PNG conversion in anatomy scripts** requires `pdftoppm` (from `poppler-utils`). This is optional — the PDF output is the primary artifact.
4. **DejaVu fonts** (`/usr/share/fonts/truetype/dejavu/`) are required for `gen.py` text rendering. These are pre-installed on Ubuntu.
5. **The CI workflow** (`ci.yml`) only validates file existence and extensions — it does not run Python scripts or linters.
6. **Pre-existing lint issues** — `ruff check .` reports ~262 errors in the current codebase. These are pre-existing and not blockers.
