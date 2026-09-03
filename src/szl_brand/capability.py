"""Deterministic agent-readable capability surfaces for the SZL Holdings estate.

The contract complements Surface Foundry's human-facing card. It generates a
machine-readable capability manifest, a plain-text ``agents.md`` guide, and a
receipt binding both outputs to reviewed source data.

The design is intentionally fail-closed. Discoverability never grants authority,
missing proof endpoints remain explicit, and mutating actions cannot be declared
read-only or approval-free by accident.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final
from urllib.parse import urlsplit

from szl_brand.surface import EVIDENCE_LABELS, KINDS, OPERATIONAL_STATES

SCHEMA: Final = "szl.capability-foundry/v1"
CAPABILITY_SCHEMA: Final = "szl.capabilities/v1"
RECEIPT_SCHEMA: Final = "szl.capability-receipt/v1"

INTERFACES: Final = frozenset({"HTTP", "MCP", "GRADIO", "OPENAI_COMPATIBLE", "DOCUMENT"})
METHODS: Final = frozenset({"GET", "POST", "PUT", "PATCH", "DELETE", "CALL", "READ"})
AUTHORITIES: Final = frozenset({"OBSERVE", "PROPOSE", "BOUNDED_ACTION"})
APPROVAL_POLICIES: Final = frozenset({"REQUIRED", "CONDITIONAL", "NOT_APPLICABLE"})
FAILURE_STATES: Final = (
    "UNAVAILABLE",
    "UNKNOWN",
    "DENIED",
    "REQUIRES_APPROVAL",
    "DEGRADED",
)
MUTATING_METHODS: Final = frozenset({"POST", "PUT", "PATCH", "DELETE", "CALL"})
NAME_RE: Final = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")


class CapabilityContractError(ValueError):
    """Raised when an agent capability contract is ambiguous or unsafe."""


@dataclass(frozen=True)
class CapabilityAction:
    """One callable or inspectable operation exposed by a public surface."""

    name: str
    description: str
    interface: str
    method: str
    endpoint: str
    evidence_label: str
    authority: str
    human_approval: str
    output_claim: str
    schema_url: str | None = None

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> CapabilityAction:
        allowed = set(cls.__dataclass_fields__)
        required = allowed - {"schema_url"}
        unknown = sorted(set(value) - allowed)
        missing = sorted(required - set(value))
        if unknown:
            raise CapabilityContractError(
                "capability contains unknown fields: " + ", ".join(unknown)
            )
        if missing:
            raise CapabilityContractError("capability is missing fields: " + ", ".join(missing))
        action = cls(**value)
        validate_action(action)
        return action


@dataclass(frozen=True)
class CapabilitySurface:
    """Reviewed agent contract for one GitHub or Hugging Face surface."""

    slug: str
    display_name: str
    kind: str
    human_url: str
    source_url: str
    operational_state: str
    limitations: str
    capabilities: tuple[CapabilityAction, ...]
    build_info_url: str | None = None
    receipt_url: str | None = None

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> CapabilitySurface:
        allowed = set(cls.__dataclass_fields__)
        required = allowed - {"build_info_url", "receipt_url"}
        unknown = sorted(set(value) - allowed)
        missing = sorted(required - set(value))
        if unknown:
            raise CapabilityContractError("surface contains unknown fields: " + ", ".join(unknown))
        if missing:
            raise CapabilityContractError("surface is missing fields: " + ", ".join(missing))
        raw_actions = value.get("capabilities")
        if not isinstance(raw_actions, list) or not raw_actions:
            raise CapabilityContractError("capabilities must be a non-empty array")
        actions = tuple(
            CapabilityAction.from_mapping(item)
            if isinstance(item, dict)
            else _raise_action_type(index)
            for index, item in enumerate(raw_actions)
        )
        prepared = dict(value)
        prepared["capabilities"] = actions
        surface = cls(**prepared)
        validate_surface(surface)
        return surface


@dataclass(frozen=True)
class CapabilityReceipt:
    schema: str
    surface: str
    contract_sha256: str
    capabilities_sha256: str
    agents_md_sha256: str
    capability_count: int
    bounded_action_count: int

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, indent=2) + "\n"


def _raise_action_type(index: int) -> CapabilityAction:
    raise CapabilityContractError(f"capability {index} must be an object")


def _is_https_url(value: str) -> bool:
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    return bool(
        parsed.scheme == "https"
        and parsed.netloc
        and parsed.username is None
        and parsed.password is None
    )


def _validate_optional_url(name: str, value: str | None, errors: list[str]) -> None:
    if value is not None and not _is_https_url(value):
        errors.append(f"{name} must be null or an HTTPS URL without credentials")


def validate_action(action: CapabilityAction) -> None:
    """Reject capability declarations that overstate interface or authority."""

    errors: list[str] = []
    if not NAME_RE.fullmatch(action.name):
        errors.append("capability name must be lowercase and path-safe")
    if not action.description.strip() or len(action.description.strip()) > 180:
        errors.append("description must be 1-180 characters")
    if action.interface not in INTERFACES:
        errors.append("interface must be one of: " + ", ".join(sorted(INTERFACES)))
    if action.method not in METHODS:
        errors.append("method must be one of: " + ", ".join(sorted(METHODS)))
    if not _is_https_url(action.endpoint):
        errors.append("endpoint must be an HTTPS URL without credentials")
    if action.evidence_label not in EVIDENCE_LABELS:
        errors.append("evidence_label must use the SZL evidence vocabulary")
    if action.authority not in AUTHORITIES:
        errors.append("authority must be one of: " + ", ".join(sorted(AUTHORITIES)))
    if action.human_approval not in APPROVAL_POLICIES:
        errors.append("human_approval must be one of: " + ", ".join(sorted(APPROVAL_POLICIES)))
    if not action.output_claim.strip() or len(action.output_claim.strip()) > 180:
        errors.append("output_claim must be 1-180 characters")
    _validate_optional_url("schema_url", action.schema_url, errors)

    if action.interface == "DOCUMENT" and action.method != "READ":
        errors.append("DOCUMENT capabilities must use READ")
    if action.interface != "DOCUMENT" and action.method == "READ":
        errors.append("READ is reserved for DOCUMENT capabilities")
    if action.authority == "OBSERVE" and action.method in MUTATING_METHODS:
        errors.append("OBSERVE authority cannot declare a mutating method")
    if action.authority == "BOUNDED_ACTION" and action.method not in MUTATING_METHODS:
        errors.append("BOUNDED_ACTION requires a mutating or callable method")
    if action.authority == "BOUNDED_ACTION" and action.human_approval == "NOT_APPLICABLE":
        errors.append("BOUNDED_ACTION must preserve REQUIRED or CONDITIONAL approval")
    if action.authority == "PROPOSE" and action.human_approval == "NOT_APPLICABLE":
        errors.append("PROPOSE must preserve REQUIRED or CONDITIONAL human review")

    if errors:
        raise CapabilityContractError("; ".join(errors))


def validate_surface(surface: CapabilitySurface) -> None:
    """Validate the public identity, proof boundary, and unique operation names."""

    errors: list[str] = []
    if not surface.slug or len(surface.slug) > 96:
        errors.append("slug must be 1-96 characters")
    if not surface.display_name.strip() or len(surface.display_name.strip()) > 72:
        errors.append("display_name must be 1-72 characters")
    if surface.kind not in KINDS:
        errors.append("kind must use a Surface Foundry kind")
    if not _is_https_url(surface.human_url):
        errors.append("human_url must be an HTTPS URL without credentials")
    if not _is_https_url(surface.source_url):
        errors.append("source_url must be an HTTPS URL without credentials")
    if surface.operational_state not in OPERATIONAL_STATES:
        errors.append("operational_state must use the SZL operational vocabulary")
    if not surface.limitations.strip() or len(surface.limitations.strip()) > 260:
        errors.append("limitations must be 1-260 characters")
    _validate_optional_url("build_info_url", surface.build_info_url, errors)
    _validate_optional_url("receipt_url", surface.receipt_url, errors)

    names = [action.name for action in surface.capabilities]
    if len(names) != len(set(names)):
        errors.append("capability names must be unique within a surface")

    if errors:
        raise CapabilityContractError("; ".join(errors))


def canonical_contract(surface: CapabilitySurface) -> bytes:
    return (json.dumps(asdict(surface), sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def _digest(value: bytes | str) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def capability_document(surface: CapabilitySurface) -> dict[str, Any]:
    """Return the normalized machine-readable public capability contract."""

    validate_surface(surface)
    return {
        "schema": CAPABILITY_SCHEMA,
        "surface": surface.slug,
        "display_name": surface.display_name,
        "kind": surface.kind,
        "operational_state": surface.operational_state,
        "human_url": surface.human_url,
        "source_url": surface.source_url,
        "proof": {
            "build_info_url": surface.build_info_url or "UNAVAILABLE",
            "receipt_url": surface.receipt_url or "UNAVAILABLE",
        },
        "authority_model": {
            "discovery_grants_authority": False,
            "failure_states": list(FAILURE_STATES),
            "bounded_actions_require_review": True,
        },
        "capabilities": [asdict(action) for action in surface.capabilities],
        "limitations": surface.limitations,
    }


def render_capabilities_json(surface: CapabilitySurface) -> str:
    return json.dumps(capability_document(surface), sort_keys=True, indent=2) + "\n"


def _proof_line(label: str, value: str | None) -> str:
    if value is None:
        return f"- {label}: `UNAVAILABLE`"
    return f"- {label}: {value}"


def render_agents_md(surface: CapabilitySurface) -> str:
    """Render agent instructions from the same reviewed capability contract."""

    validate_surface(surface)
    lines = [
        f"# {surface.display_name} — agent interface",
        "",
        f"Surface: `{surface.slug}`",
        f"Operational state: `{surface.operational_state}`",
        f"Human interface: {surface.human_url}",
        f"Canonical source: {surface.source_url}",
        _proof_line("Build identity", surface.build_info_url),
        _proof_line("Receipt / evidence", surface.receipt_url),
        "",
        "## Authority boundary",
        "",
        "Capability discovery does not grant authority. Do not infer permissions from reachability.",
        "Never promote OBSERVE or PROPOSE into execution. BOUNDED_ACTION remains inside its declared scope.",
        "A BOUNDED_ACTION always preserves REQUIRED or CONDITIONAL human review.",
        "If source identity, evidence, or required inputs cannot be verified, return `UNAVAILABLE` or `UNKNOWN` rather than inventing state.",
        "Recognized fail-closed states: `UNAVAILABLE`, `UNKNOWN`, `DENIED`, `REQUIRES_APPROVAL`, `DEGRADED`.",
        "",
        "## Capabilities",
        "",
        "| Capability | Interface | Call | Authority | Human approval | Evidence |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for action in surface.capabilities:
        call = f"`{action.method} {action.endpoint}`"
        lines.append(
            f"| `{action.name}` | `{action.interface}` | {call} | `{action.authority}` | "
            f"`{action.human_approval}` | `{action.evidence_label}` |"
        )
    lines.extend(["", "## Operation detail", ""])
    for action in surface.capabilities:
        lines.extend(
            [
                f"### `{action.name}`",
                "",
                action.description,
                "",
                f"- Endpoint: `{action.method} {action.endpoint}`",
                f"- Interface: `{action.interface}`",
                f"- Authority: `{action.authority}`",
                f"- Human approval: `{action.human_approval}`",
                f"- Evidence class: `{action.evidence_label}`",
                f"- Output claim boundary: {action.output_claim}",
                _proof_line("Schema", action.schema_url),
                "",
            ]
        )
    lines.extend(
        [
            "## Limitations",
            "",
            surface.limitations,
            "",
            "This document describes callability and authority boundaries. It does not establish accuracy, safety, regulatory approval, production suitability, or external validation.",
            "",
        ]
    )
    return "\n".join(lines)


def build_receipt(
    surface: CapabilitySurface,
    capabilities_json: str,
    agents_md: str,
) -> CapabilityReceipt:
    return CapabilityReceipt(
        schema=RECEIPT_SCHEMA,
        surface=surface.slug,
        contract_sha256=_digest(canonical_contract(surface)),
        capabilities_sha256=_digest(capabilities_json),
        agents_md_sha256=_digest(agents_md),
        capability_count=len(surface.capabilities),
        bounded_action_count=sum(
            action.authority == "BOUNDED_ACTION" for action in surface.capabilities
        ),
    )


def load_manifest(path: Path) -> list[CapabilitySurface]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CapabilityContractError(f"manifest is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise CapabilityContractError("manifest root must be an object")
    if set(value) != {"schema", "surfaces"}:
        raise CapabilityContractError("manifest keys must be exactly schema and surfaces")
    if value.get("schema") != SCHEMA:
        raise CapabilityContractError(f"manifest schema must be {SCHEMA}")
    rows = value.get("surfaces")
    if not isinstance(rows, list) or not rows:
        raise CapabilityContractError("manifest surfaces must be a non-empty array")
    surfaces: list[CapabilitySurface] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise CapabilityContractError(f"surface {index} must be an object")
        surface = CapabilitySurface.from_mapping(row)
        folded = surface.slug.casefold()
        if folded in seen:
            raise CapabilityContractError(f"duplicate surface slug: {surface.slug}")
        seen.add(folded)
        surfaces.append(surface)
    return surfaces


def _safe_output_name(slug: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", slug).strip(".-").lower()


def generate_capabilities(
    surfaces: Iterable[CapabilitySurface],
    output: Path,
) -> list[Path]:
    """Generate agent-readable assets locally without provider mutation."""

    created: list[Path] = []
    output.mkdir(parents=True, exist_ok=True)
    for surface in surfaces:
        directory = output / _safe_output_name(surface.slug)
        directory.mkdir(parents=True, exist_ok=True)
        capabilities_json = render_capabilities_json(surface)
        agents_md = render_agents_md(surface)
        receipt = build_receipt(surface, capabilities_json, agents_md)
        artifacts = {
            "capabilities.json": capabilities_json,
            "agents.md": agents_md,
            "capability-receipt.json": receipt.to_json(),
        }
        for name, content in artifacts.items():
            path = directory / name
            path.write_text(content, encoding="utf-8", newline="\n")
            created.append(path)
    return created


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="szl-capability",
        description="Generate fail-closed agent-readable SZL capability surfaces.",
    )
    parser.add_argument("manifest", type=Path, help="Capability Foundry v1 JSON manifest")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output directory")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        surfaces = load_manifest(args.manifest)
        paths = generate_capabilities(surfaces, args.output)
    except (OSError, CapabilityContractError) as exc:
        print(f"error: {exc}")
        return 2
    print(f"generated {len(paths)} artifacts for {len(surfaces)} capability surfaces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
