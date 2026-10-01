#!/usr/bin/env python3
"""Historical entry point for the SZL-MARKETING-1.1 fact pipeline.

The pipeline and the Aegis Shield corrections of 2026-09-30 (crown sweep across models and
datasets, real A/B subject lines, backup before overwrite, sentence-scoped linter) now live in
``szl_brand.marketing`` and are tested in ``tests/test_marketing.py``. This file only forwards
to ``szl-marketing facts`` so the old command keeps working; it no longer writes to an absolute
``/opt`` path.
"""

from __future__ import annotations

import sys

from szl_brand.marketing.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["facts", *sys.argv[1:]]))
