# SPDX-License-Identifier: Apache-2.0
"""Contract tests for class-native SZL motifs."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from szl_brand.estate import (
    FLAGSHIP_PRODUCT,
    GOVERNANCE_PROOF,
    HISTORICAL,
    PLATFORM_CONTROL,
    RESEARCH_FORMULA,
    RUNTIME_INFRA,
    UNCLASSIFIED,
)
from szl_brand.motif import (
    MotifContractError,
    MotifRequest,
    build_bundle,
    build_profile,
    render_css,
    render_svg,
    write_bundle,
)


class MotifCompilerV2Test(unittest.TestCase):
    def test_every_public_class_has_a_distinct_information_architecture(self) -> None:
        expected = {
            FLAGSHIP_PRODUCT: "DOMAIN_COMMAND",
            PLATFORM_CONTROL: "FOUNDRY_CONTROL",
            RUNTIME_INFRA: "SUBSTRATE_RUNTIME",
            GOVERNANCE_PROOF: "PROOF_LEDGER",
            RESEARCH_FORMULA: "FORMULA_NOTEBOOK",
            HISTORICAL: "ARCHIVE_MONO",
            UNCLASSIFIED: "NEUTRAL_REVIEW",
        }
        observed = {}
        for estate_class, family in expected.items():
            profile = build_profile(
                MotifRequest(
                    slug=f"surface-{estate_class.lower()}",
                    display_name=estate_class,
                    estate_class=estate_class,
                )
            )
            observed[estate_class] = profile.theme_family
            self.assertEqual(profile.theme_family, family)
        self.assertEqual(len(set(observed.values())), len(expected))

    def test_same_surface_is_byte_deterministic(self) -> None:
        request = MotifRequest(
            slug="terra",
            display_name="Terra Command",
            estate_class=FLAGSHIP_PRODUCT,
        )
        first = build_bundle(request)
        second = build_bundle(request)
        self.assertEqual(first, second)

    def test_different_slugs_receive_stable_non_identical_variants(self) -> None:
        terra = build_profile(
            MotifRequest("terra", "Terra", FLAGSHIP_PRODUCT)
        )
        sentra = build_profile(
            MotifRequest("sentra", "Sentra", FLAGSHIP_PRODUCT)
        )
        self.assertNotEqual(terra.surface_fingerprint, sentra.surface_fingerprint)
        self.assertEqual(terra.theme_family, sentra.theme_family)

    def test_css_preserves_mobile_and_accessibility_contracts(self) -> None:
        profile = build_profile(
            MotifRequest("lyte", "Lyte", FLAGSHIP_PRODUCT)
        )
        css = render_css(profile)
        self.assertIn("--szl-motif-touch: 44px", css)
        self.assertIn("pointer: coarse", css)
        self.assertIn("--szl-motif-touch: 48px", css)
        self.assertIn(":focus-visible", css)
        self.assertIn("prefers-reduced-motion: reduce", css)
        self.assertIn("overflow-x: clip", css)

    def test_svg_is_accessible_escaped_and_class_native(self) -> None:
        profile = build_profile(
            MotifRequest(
                "proof-ledger",
                "Proof <Ledger>",
                GOVERNANCE_PROOF,
            )
        )
        svg = render_svg(profile)
        self.assertIn('role="img"', svg)
        self.assertIn('aria-labelledby="szl-title szl-desc"', svg)
        self.assertIn("Proof &lt;Ledger&gt;", svg)
        self.assertIn("RECEIPT-1", svg)
        self.assertNotIn("<Ledger>", svg)

    def test_historical_surface_cannot_imply_live_runtime(self) -> None:
        profile = build_profile(
            MotifRequest("archive", "Archive", HISTORICAL)
        )
        svg = render_svg(profile)
        self.assertIn("NO LIVE RUNTIME CLAIM", svg)
        self.assertEqual(profile.motion, "NONE")

    def test_bundle_receipt_binds_exact_artifact_bytes(self) -> None:
        request = MotifRequest(
            "substrate",
            "Substrate Runtime",
            RUNTIME_INFRA,
        )
        profile, css, svg, receipt = build_bundle(request)
        self.assertEqual(
            receipt.profile_sha256,
            hashlib.sha256(profile.to_json().encode("utf-8")).hexdigest(),
        )
        self.assertEqual(
            receipt.css_sha256,
            hashlib.sha256(css.encode("utf-8")).hexdigest(),
        )
        self.assertEqual(
            receipt.svg_sha256,
            hashlib.sha256(svg.encode("utf-8")).hexdigest(),
        )
        self.assertEqual(receipt.authority, "NONE")

    def test_bundle_writes_only_the_four_declared_artifacts(self) -> None:
        request = MotifRequest(
            "formula-lab",
            "Formula Lab",
            RESEARCH_FORMULA,
        )
        with tempfile.TemporaryDirectory(prefix="szl-motif-") as root:
            paths = write_bundle(request, root)
            self.assertEqual(
                set(paths), {"profile", "css", "svg", "receipt"}
            )
            self.assertEqual(
                {path.name for path in Path(root).iterdir()},
                {
                    "surface-profile.json",
                    "motif.css",
                    "motif.svg",
                    "motif-receipt.json",
                },
            )
            receipt = json.loads(paths["receipt"].read_text(encoding="utf-8"))
            self.assertEqual(receipt["authority"], "NONE")

    def test_invalid_or_internal_class_fails_closed(self) -> None:
        with self.assertRaises(MotifContractError):
            build_profile(MotifRequest("internal", "Internal", "INTERNAL"))
        with self.assertRaises(MotifContractError):
            MotifRequest.from_mapping(
                {
                    "slug": "../unsafe",
                    "display_name": "Unsafe",
                    "estate_class": FLAGSHIP_PRODUCT,
                }
            )
        with self.assertRaises(MotifContractError):
            MotifRequest.from_mapping(
                {
                    "slug": "valid",
                    "display_name": "Valid",
                    "estate_class": FLAGSHIP_PRODUCT,
                    "extra": True,
                }
            )


if __name__ == "__main__":
    unittest.main()
