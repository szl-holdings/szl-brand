"""Fail-closed validation for KHIPU Command System surface disclosures."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Final
from urllib.parse import urlparse

CONTRACT: Final = "szl.khipu-command-system/v1"
REQUIRED_VIEWPORTS: Final = (360, 390, 768, 1024, 1440)
REQUIRED_ZOOM_PERCENT: Final = (200, 400)
MINIMUM_TARGET_CSS_PX: Final = 44
EVIDENCE_CLASSES: Final = frozenset({"REAL", "MEASURED", "MODELED", "ROADMAP", "UNAVAILABLE"})
OPERATIONAL_STATES: Final = frozenset(
    {"OPERATIONAL", "PARTIAL", "DEGRADED", "UNAVAILABLE", "HISTORICAL"}
)
AUDIENCES: Final = frozenset({"EXECUTIVE", "OPERATOR", "BUILDER", "VERIFIER"})

_SURFACE_ID_RE: Final = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_REVISION_RE: Final = re.compile(r"^[0-9a-f]{40}$")
_DIGEST_RE: Final = re.compile(r"^[0-9a-f]{64}$")
_HTTPS_URL_RE: Final = re.compile(
    r"^https://(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"[A-Za-z]{2,63}"
    r"(?::(?:[1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|"
    r"65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5]))?"
    r"(?:/(?:[A-Za-z0-9._~!$&'()*+,;=:@-]|%[0-9A-Fa-f]{2})*)*"
    r"(?:\?(?:[A-Za-z0-9._~!$&'()*+,;=:@/?-]|%[0-9A-Fa-f]{2})*)?"
    r"(?:#(?:[A-Za-z0-9._~!$&'()*+,;=:@/?-]|%[0-9A-Fa-f]{2})*)?$"
)
_RFC3339_RE: Final = re.compile(
    r"^[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])"
    r"T(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]"
    r"(?:\.[0-9]+)?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])$"
)
_ZERO_REVISION: Final = "0" * 40
_ZERO_DIGEST: Final = "0" * 64


def _keys(
    value: object,
    *,
    path: str,
    required: set[str],
    optional: set[str] | None = None,
) -> tuple[Mapping[str, object] | None, list[str]]:
    if not isinstance(value, Mapping):
        return None, [f"{path} must be an object"]
    optional = optional or set()
    actual = set(value)
    errors = [f"{path}.{name} is required" for name in sorted(required - actual)]
    errors.extend(f"{path}.{name} is not allowed" for name in sorted(actual - required - optional))
    return value, errors


def _text(value: object, *, path: str, minimum: int, maximum: int) -> list[str]:
    if not isinstance(value, str):
        return [f"{path} must be a string"]
    if not minimum <= len(value) <= maximum:
        return [f"{path} length must be between {minimum} and {maximum}"]
    if value != value.strip() or any(
        ord(character) < 32 or ord(character) == 127 for character in value
    ):
        return [f"{path} must be trimmed printable text"]
    return []


def _https_url(value: object, *, path: str) -> list[str]:
    if not isinstance(value, str):
        return [f"{path} must be a string"]
    try:
        parsed = urlparse(value)
        _ = parsed.port
    except ValueError:
        return [f"{path} must be an absolute HTTPS URL"]
    if parsed.username or parsed.password:
        return [f"{path} must not include credentials"]
    if not _HTTPS_URL_RE.fullmatch(value):
        return [f"{path} must be an absolute HTTPS URL"]
    return []


def _timestamp(value: object, *, path: str) -> list[str]:
    if not isinstance(value, str) or not _RFC3339_RE.fullmatch(value):
        return [f"{path} must be an RFC 3339 timestamp"]
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return [f"{path} must be an RFC 3339 timestamp"]
    if parsed.tzinfo is None:
        return [f"{path} must include a timezone"]
    return []


def validate_surface(document: object) -> list[str]:
    """Return deterministic contract violations for a decoded disclosure."""

    root, errors = _keys(
        document,
        path="$",
        required={
            "contract",
            "recordKind",
            "surfaceId",
            "audience",
            "source",
            "responsive",
            "accessibility",
            "executiveBrief",
            "evidence",
            "links",
        },
    )
    if root is None:
        return errors

    if root.get("contract") != CONTRACT:
        errors.append("$.contract is unsupported")

    record_kind = root.get("recordKind")
    if record_kind not in {"SAMPLE", "RELEASE"}:
        errors.append("$.recordKind must be SAMPLE or RELEASE")

    surface_id = root.get("surfaceId")
    if not isinstance(surface_id, str) or not _SURFACE_ID_RE.fullmatch(surface_id):
        errors.append("$.surfaceId must be lowercase kebab-case")
    elif not 3 <= len(surface_id) <= 64:
        errors.append("$.surfaceId length must be between 3 and 64")

    if root.get("audience") not in AUDIENCES:
        errors.append(f"$.audience must be one of {sorted(AUDIENCES)}")

    source, source_errors = _keys(
        root.get("source"),
        path="$.source",
        required={"repository", "revision", "kanchayManifestRoot"},
    )
    errors.extend(source_errors)
    if source is not None:
        errors.extend(_https_url(source.get("repository"), path="$.source.repository"))
        revision = source.get("revision")
        digest = source.get("kanchayManifestRoot")
        if not isinstance(revision, str) or not _REVISION_RE.fullmatch(revision):
            errors.append("$.source.revision must be an exact lowercase Git SHA")
        if not isinstance(digest, str) or not _DIGEST_RE.fullmatch(digest):
            errors.append("$.source.kanchayManifestRoot must be a lowercase SHA-256 digest")
        if record_kind == "RELEASE" and revision == _ZERO_REVISION:
            errors.append("$.source.revision must not be the sample zero revision for RELEASE")
        if record_kind == "RELEASE" and digest == _ZERO_DIGEST:
            errors.append(
                "$.source.kanchayManifestRoot must not be the sample zero digest for RELEASE"
            )

    responsive, responsive_errors = _keys(
        root.get("responsive"),
        path="$.responsive",
        required={"testedViewportsCssPx", "zoomPercent", "bodyMeasureCh"},
    )
    errors.extend(responsive_errors)
    if responsive is not None:
        if responsive.get("testedViewportsCssPx") != list(REQUIRED_VIEWPORTS):
            errors.append(
                f"$.responsive.testedViewportsCssPx must equal {list(REQUIRED_VIEWPORTS)}"
            )
        if responsive.get("zoomPercent") != list(REQUIRED_ZOOM_PERCENT):
            errors.append(f"$.responsive.zoomPercent must equal {list(REQUIRED_ZOOM_PERCENT)}")
        measure = responsive.get("bodyMeasureCh")
        if not isinstance(measure, int) or isinstance(measure, bool) or not 60 <= measure <= 78:
            errors.append("$.responsive.bodyMeasureCh must be an integer from 60 through 78")

    accessibility, accessibility_errors = _keys(
        root.get("accessibility"),
        path="$.accessibility",
        required={
            "minimumTargetCssPx",
            "focusVisible",
            "keyboardOnly",
            "reducedMotion",
            "nonColorStatus",
            "semanticLandmarks",
        },
    )
    errors.extend(accessibility_errors)
    if accessibility is not None:
        expected = {
            "minimumTargetCssPx": MINIMUM_TARGET_CSS_PX,
            "focusVisible": True,
            "keyboardOnly": True,
            "reducedMotion": True,
            "nonColorStatus": True,
            "semanticLandmarks": True,
        }
        for name, expected_value in expected.items():
            if accessibility.get(name) != expected_value:
                errors.append(f"$.accessibility.{name} must equal {expected_value!r}")

    brief, brief_errors = _keys(
        root.get("executiveBrief"),
        path="$.executiveBrief",
        required={
            "category",
            "primaryAudience",
            "outcome",
            "primaryAction",
            "evidenceAction",
            "boundary",
        },
    )
    errors.extend(brief_errors)
    if brief is not None:
        for name in (
            "category",
            "primaryAudience",
            "outcome",
            "primaryAction",
            "evidenceAction",
        ):
            errors.extend(
                _text(brief.get(name), path=f"$.executiveBrief.{name}", minimum=3, maximum=180)
            )
        errors.extend(
            _text(
                brief.get("boundary"),
                path="$.executiveBrief.boundary",
                minimum=12,
                maximum=240,
            )
        )

    evidence = root.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("$.evidence must be a non-empty array")
    else:
        for index, item in enumerate(evidence):
            path = f"$.evidence[{index}]"
            record, record_errors = _keys(
                item,
                path=path,
                required={
                    "claim",
                    "evidenceClass",
                    "operationalState",
                    "sourceUrl",
                    "scope",
                    "limitations",
                },
                optional={"observedAt"},
            )
            errors.extend(record_errors)
            if record is None:
                continue
            errors.extend(_text(record.get("claim"), path=f"{path}.claim", minimum=8, maximum=240))
            if record.get("evidenceClass") not in EVIDENCE_CLASSES:
                errors.append(f"{path}.evidenceClass must be one of {sorted(EVIDENCE_CLASSES)}")
            state = record.get("operationalState")
            if state not in OPERATIONAL_STATES:
                errors.append(
                    f"{path}.operationalState must be one of {sorted(OPERATIONAL_STATES)}"
                )
            errors.extend(_https_url(record.get("sourceUrl"), path=f"{path}.sourceUrl"))
            errors.extend(_text(record.get("scope"), path=f"{path}.scope", minimum=8, maximum=300))
            limitations = record.get("limitations")
            if not isinstance(limitations, list) or not limitations:
                errors.append(f"{path}.limitations must be a non-empty array")
            else:
                for limitation_index, limitation in enumerate(limitations):
                    errors.extend(
                        _text(
                            limitation,
                            path=f"{path}.limitations[{limitation_index}]",
                            minimum=8,
                            maximum=240,
                        )
                    )
            if state in {"OPERATIONAL", "PARTIAL", "DEGRADED"}:
                if "observedAt" not in record:
                    errors.append(f"{path}.observedAt is required for current operational states")
                else:
                    errors.extend(_timestamp(record.get("observedAt"), path=f"{path}.observedAt"))
            elif "observedAt" in record:
                errors.extend(_timestamp(record.get("observedAt"), path=f"{path}.observedAt"))

    links, link_errors = _keys(
        root.get("links"),
        path="$.links",
        required={"product", "documentation", "source", "evidence"},
    )
    errors.extend(link_errors)
    if links is not None:
        for name in ("product", "documentation", "source", "evidence"):
            errors.extend(_https_url(links.get(name), path=f"$.links.{name}"))

    return sorted(set(errors))


def validate_surface_file(path: Path) -> list[str]:
    """Load a JSON disclosure and return fail-closed validation errors."""

    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"contract file is unreadable: {exc}"]
    return validate_surface(document)
