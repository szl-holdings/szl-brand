# AGENTS.md

## Cursor Cloud specific instructions

This is the **SZL Brand SDK** — a Python package for deterministic brand asset generation, validation, and governance.

### Quick reference

```bash
# Install the package (editable, with dev dependencies)
pip install -e ".[dev]"

# CLI entry point
python3 -m szl_brand --help
szl-brand --help

# Generate all 14 social previews
szl-brand generate -o social-previews

# Generate a custom preview
szl-brand generate-one --repo my-repo --title "Title" --subtitle "Sub" -o out.png

# Validate assets (dimensions, integrity)
szl-brand validate social-previews

# Generate SHA-256 integrity manifest
szl-brand manifest social-previews -o brand-manifest.json

# Check drift against manifest
szl-brand drift --manifest brand-manifest.json social-previews

# Show inventory
szl-brand inventory social-previews

# Start live gallery server (port 8742)
szl-brand serve
```

### Running tests & lint

```bash
python3 -m pytest tests/ -v
ruff check src/ tests/
ruff format --check src/ tests/
```

### Key dependencies

- **Python 3.12** — required runtime
- **Pillow** — PNG banner generation
- **ReportLab** — PDF anatomy figure generation
- **poppler-utils** (`pdftoppm`) — PDF→PNG conversion for legacy anatomy scripts
- **Pillow bundled font** — portable preview rendering with no host-font dependency
- **Ruff** — lint/format
- **pytest** — test suite

### Repository and execution boundaries

1. The supported SDK workflows above operate from the repository checkout and must not require privileged filesystem changes.
2. Several historical scripts under `anatomy/scripts/` still contain hard-coded `/home/user/workspace/...` paths from the original build environment. **Do not create, chmod, mount, or otherwise mutate those external paths automatically. Do not run those legacy scripts in automation as if they were portable build steps.** Treat their checked-in outputs and reports as historical artifacts unless a separate reviewed portability repair removes the external-path dependency.
3. `build_explainer_pdfs.py` also expects historical markdown inputs outside its own source directory. Missing external inputs are an explicit unavailable condition, not permission to synthesize replacements or broaden filesystem access.
4. The `social-previews/gen.py` script is the legacy generator. The SDK (`python3 -m szl_brand generate`) is the canonical supported path for social-preview generation.
5. Procedural SDK generation is intended to be deterministic for identical declared inputs. Verify byte equality in tests rather than promoting that intent into an unmeasured runtime claim.
6. Never weaken CI, integrity checks, accessibility assertions, evidence labels, license/trademark notices, or source-revision validation to make a change pass.
