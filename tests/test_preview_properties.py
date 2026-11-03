"""Hypothesis property tests for the social-preview renderer.

Adopted from the fix/fuzz-invariants-20261101 branch. Rendering is bounded to eight
examples; the deadline is disabled for image work, not for failures or assertions.
"""

from __future__ import annotations

import tempfile
from dataclasses import replace
from pathlib import Path

from hypothesis import example, given, settings
from hypothesis import strategies as st
from PIL import Image

from szl_brand.preview import PreviewSpec, generate_preview


@settings(max_examples=8, deadline=None)
@given(st.text("abcdefghijklmnopqrstuvwxyz0123456789-_", min_size=1, max_size=24))
@example("a")
def test_preview_is_byte_deterministic_repo_sensitive_and_canonically_sized(repo):
    spec = PreviewSpec(repo, "TEST", "Deterministic", "Generated input check", "SDK")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        first = generate_preview(spec, root / "a.png").read_bytes()
        second = generate_preview(spec, root / "b.png").read_bytes()
        # Repository identity must change geometry and texture even with identical copy.
        other = generate_preview(
            replace(spec, repo=repo + "-distinct"), root / "c.png"
        ).read_bytes()
        with Image.open(root / "a.png") as image:
            size, file_format, mode = image.size, image.format, image.mode

    assert first == second
    assert first != other
    assert (size, file_format, mode) == ((1280, 640), "PNG", "RGB")
