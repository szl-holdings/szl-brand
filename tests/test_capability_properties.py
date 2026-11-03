"""Hypothesis property tests: Capability Foundry writes every surface to its own directory."""

from __future__ import annotations

import string
import tempfile
from pathlib import Path

import pytest
from hypothesis import example, given
from hypothesis import strategies as st

from szl_brand.capability import (
    CapabilityContractError,
    CapabilitySurface,
    generate_capabilities,
)
from szl_brand.surface import safe_output_name

BASE = {
    "slug": "terra",
    "display_name": "Terra",
    "kind": "space",
    "human_url": "https://szlholdings-terra.hf.space/",
    "source_url": "https://github.com/szl-holdings/szl-real-estate",
    "build_info_url": None,
    "receipt_url": None,
    "operational_state": "OPERATIONAL",
    "limitations": "Public runtime evidence does not authorize financial action.",
    "capabilities": [
        {
            "name": "build-info",
            "description": "Read the deployment and source identity exposed by the surface.",
            "interface": "HTTP",
            "method": "GET",
            "endpoint": "https://szlholdings-terra.hf.space/api/build-info",
            "schema_url": None,
            "evidence_label": "MEASURED",
            "authority": "OBSERVE",
            "human_approval": "NOT_APPLICABLE",
            "output_claim": "Reports deployment identity only.",
        }
    ],
}
# Path-shaped text: separators, dots and case variants collide most often.
slug_text = st.text(string.ascii_letters + string.digits + "._/- \\é", max_size=12) | st.text(
    max_size=12
)


def _accepted(slug: str) -> CapabilitySurface | None:
    try:
        return CapabilitySurface.from_mapping({**BASE, "slug": slug})
    except CapabilityContractError:
        return None


# Only the slug length used to be checked, so ".." (or "/", "日本") mapped to the empty
# directory name and generate_capabilities wrote into the output root itself.
@given(slug_text)
@example("..")
@example("日本")
def test_every_accepted_slug_writes_inside_its_own_subdirectory(slug):
    accepted = _accepted(slug)
    if accepted is None:
        return

    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory)
        paths = generate_capabilities([accepted], output)
        folders = {path.parent for path in paths}

    assert folders == {output / safe_output_name(slug)}
    assert output not in folders
    assert all(path.parent.parent == output for path in paths)


@given(slug_text, slug_text)
@example("a-b", "a/b")
@example("Terra", "terra")
def test_two_surfaces_never_share_an_output_directory(first, second):
    surfaces = [_accepted(first), _accepted(second)]
    if None in surfaces:
        return

    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory)
        if safe_output_name(first) == safe_output_name(second):
            with pytest.raises(CapabilityContractError, match="share output directory"):
                generate_capabilities(surfaces, output)
            assert list(output.iterdir()) == []
            return
        paths = generate_capabilities(surfaces, output)

    assert len(paths) == len(set(paths)) == 6
    assert {path.parent.name for path in paths} == {
        safe_output_name(first),
        safe_output_name(second),
    }
