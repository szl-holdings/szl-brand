"""Deterministic estate-wide surface planning for SZL Holdings.

The planner converts GitHub repository metadata into a reviewed presentation and
agent-interface plan. It deliberately does not mutate GitHub, Hugging Face, DNS,
or deployment state. Private repositories are never eligible for public output,
archived repositories are always historical, and unknown public repositories are
never promoted to flagship status by naming heuristics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final

SNAPSHOT_SCHEMA: Final = "szl.github-estate-snapshot/v1"
PLAN_SCHEMA: Final = "szl.estate-surface-plan/v1"
RECEIPT_SCHEMA: Final = "szl.estate-surface-plan-receipt/v1"

FLAGSHIP_PRODUCT: Final = "FLAGSHIP_PRODUCT"
PLATFORM_CONTROL: Final = "PLATFORM_CONTROL"
RUNTIME_INFRA: Final = "RUNTIME_INFRA"
GOVERNANCE_PROOF: Final = "GOVERNANCE_PROOF"
RESEARCH_FORMULA: Final = "RESEARCH_FORMULA"
INTERNAL: Final = "INTERNAL"
HISTORICAL: Final = "HISTORICAL"
UNCLASSIFIED: Final = "UNCLASSIFIED"

ESTATE_CLASSES: Final = frozenset(
    {
        FLAGSHIP_PRODUCT,
        PLATFORM_CONTROL,
        RUNTIME_INFRA,
        GOVERNANCE_PROOF,
        RESEARCH_FORMULA,
        INTERNAL,
        HISTORICAL,
        UNCLASSIFIED,
    }
)

# Reviewed public-active registry. Absence from this table is intentionally
# conservative: a public repo becomes UNCLASSIFIED, never a flagship by guess.
CLASS_OVERRIDES: Final[dict[str, str]] = {
    # Public products / front doors.
    "a11oy": FLAGSHIP_PRODUCT,
    "a11oy-net": FLAGSHIP_PRODUCT,
    "david-leads": FLAGSHIP_PRODUCT,
    "killinchu": FLAGSHIP_PRODUCT,
    "lyte-lattice": FLAGSHIP_PRODUCT,
    "nexus": FLAGSHIP_PRODUCT,
    "puriq-live": FLAGSHIP_PRODUCT,
    "szl-holdings.github.io": FLAGSHIP_PRODUCT,
    "szl-real-estate": FLAGSHIP_PRODUCT,
    # Control planes / product assembly.
    "anatomy": PLATFORM_CONTROL,
    "a11oy-factory": PLATFORM_CONTROL,
    "ayllu": PLATFORM_CONTROL,
    "evidence-studio": PLATFORM_CONTROL,
    "immune": PLATFORM_CONTROL,
    "platform": PLATFORM_CONTROL,
    "szl-command-lab": PLATFORM_CONTROL,
    "szl-forge": PLATFORM_CONTROL,
    "szl-frontier": PLATFORM_CONTROL,
    "szl-second-brain": PLATFORM_CONTROL,
    "szl-sovereign-os": PLATFORM_CONTROL,
    # Runtime / serving / data substrate.
    "hatun-mcp": RUNTIME_INFRA,
    "khipu-consensus": RUNTIME_INFRA,
    "khipu-sda-core": RUNTIME_INFRA,
    "lyte-services": RUNTIME_INFRA,
    "szl-gpu-bridge": RUNTIME_INFRA,
    "szl-kernels": RUNTIME_INFRA,
    "szl-khipu": RUNTIME_INFRA,
    "szl-lake": RUNTIME_INFRA,
    "szl-nemo": RUNTIME_INFRA,
    "szl-serve": RUNTIME_INFRA,
    "szl-substrate": RUNTIME_INFRA,
    # Governance / proof / receipts.
    "evidence-doctrine": GOVERNANCE_PROOF,
    "governance-as-code": GOVERNANCE_PROOF,
    "governed-receipt-spec": GOVERNANCE_PROOF,
    "szl-doctrine": GOVERNANCE_PROOF,
    "szl-energy-attest": GOVERNANCE_PROOF,
    "szl-gov": GOVERNANCE_PROOF,
    "szl-govsign": GOVERNANCE_PROOF,
    "szl-guardrail-receipt": GOVERNANCE_PROOF,
    "szl-invariants": GOVERNANCE_PROOF,
    "szl-lambda-gate": GOVERNANCE_PROOF,
    "szl-provctl": GOVERNANCE_PROOF,
    "szl-receipt": GOVERNANCE_PROOF,
    "szl-trust": GOVERNANCE_PROOF,
    # Research / mathematical and formula surfaces.
    "lutar-lean": RESEARCH_FORMULA,
    "sda": RESEARCH_FORMULA,
    "szl-block-kv": RESEARCH_FORMULA,
    "szl-formulas": RESEARCH_FORMULA,
    "szl-maskmod": RESEARCH_FORMULA,
    "szl-ouroboros": RESEARCH_FORMULA,
    "szl-papers": RESEARCH_FORMULA,
    "szl-quant": RESEARCH_FORMULA,
    "szl-quant-witness": RESEARCH_FORMULA,
    "szl-receipt-attn": RESEARCH_FORMULA,
    "yarqa": RESEARCH_FORMULA,
    "YARQA-ATTN": RESEARCH_FORMULA,
}

THEME_FAMILY: Final = {
    FLAGSHIP_PRODUCT: "DOMAIN_COMMAND",
    PLATFORM_CONTROL: "FOUNDRY_CONTROL",
    RUNTIME_INFRA: "SUBSTRATE_RUNTIME",
    GOVERNANCE_PROOF: "PROOF_LEDGER",
    RESEARCH_FORMULA: "FORMULA_NOTEBOOK",
    INTERNAL: "INTERNAL_ONLY",
    HISTORICAL: "ARCHIVE_MONO",
    UNCLASSIFIED: "NEUTRAL_REVIEW",
}

SURFACE_KIND: Final = {
    FLAGSHIP_PRODUCT: "platform",
    PLATFORM_CONTROL: "platform",
    RUNTIME_INFRA: "repo",
    GOVERNANCE_PROOF: "proof",
    RESEARCH_FORMULA: "repo",
    INTERNAL: "repo",
    HISTORICAL: "archived",
    UNCLASSIFIED: "repo",
}


class EstatePlanError(ValueError):
    """Raised when a repository snapshot is malformed or unsafe to classify."""


@dataclass(frozen=True)
class RepositoryRecord:
    name: str
    full_name: str
    visibility: str
    archived: bool
    default_branch: str = "main"

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> RepositoryRecord:
        allowed = set(cls.__dataclass_fields__)
        required = allowed - {"default_branch"}
        unknown = sorted(set(value) - allowed)
        missing = sorted(required - set(value))
        if unknown:
            raise EstatePlanError("repository has unknown fields: " + ", ".join(unknown))
        if missing:
            raise EstatePlanError("repository is missing fields: " + ", ".join(missing))
        record = cls(**value)
        validate_repository(record)
        return record


@dataclass(frozen=True)
class SurfacePlanRow:
    repository: str
    name: str
    estate_class: str
    theme_family: str
    surface_kind: str
    evidence_label: str
    runtime_state: str
    human_surface: bool
    agent_surface: bool
    public_artifact_eligible: bool
    automatic_provider_write: bool
    reason: str


@dataclass(frozen=True)
class EstatePlanReceipt:
    schema: str
    snapshot_sha256: str
    plan_sha256: str
    repository_count: int
    public_artifact_count: int
    agent_surface_count: int
    class_counts: dict[str, int]

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, indent=2) + "\n"


def validate_repository(record: RepositoryRecord) -> None:
    errors: list[str] = []
    if not record.name.strip() or len(record.name) > 100:
        errors.append("name must be 1-100 characters")
    if not record.full_name.strip() or "/" not in record.full_name:
        errors.append("full_name must include owner/repository")
    if record.full_name.rsplit("/", 1)[-1] != record.name:
        errors.append("full_name repository component must equal name")
    if record.visibility not in {"public", "private", "internal"}:
        errors.append("visibility must be public, private, or internal")
    if not isinstance(record.archived, bool):
        errors.append("archived must be boolean")
    if not record.default_branch.strip():
        errors.append("default_branch must be non-empty")
    if errors:
        raise EstatePlanError("; ".join(errors))


def _classify(record: RepositoryRecord) -> tuple[str, str]:
    # Privacy wins over every naming/classification rule. A private repo is never
    # made public merely because its name resembles a public flagship.
    if record.visibility != "public":
        return INTERNAL, "non-public repository; public surface generation is forbidden"
    if record.archived:
        return HISTORICAL, "GitHub metadata marks the repository archived"
    estate_class = CLASS_OVERRIDES.get(record.name)
    if estate_class is None:
        return UNCLASSIFIED, "active public repository has no reviewed class override"
    return estate_class, "active public repository has a reviewed class override"


def plan_repository(record: RepositoryRecord) -> SurfacePlanRow:
    """Return the fail-closed presentation plan for one repository."""

    validate_repository(record)
    estate_class, reason = _classify(record)
    active_classified = estate_class not in {INTERNAL, HISTORICAL, UNCLASSIFIED}
    public_artifact_eligible = record.visibility == "public"
    human_surface = public_artifact_eligible
    agent_surface = active_classified

    if estate_class == INTERNAL:
        evidence_label = "UNAVAILABLE"
        runtime_state = "UNAVAILABLE"
    elif estate_class == HISTORICAL:
        evidence_label = "REPORTED"
        runtime_state = "HISTORICAL"
    else:
        # Classification is not operational proof. The generated plan never
        # promotes a repo to OPERATIONAL without a separate live/evidence receipt.
        evidence_label = "UNKNOWN"
        runtime_state = "UNKNOWN"

    return SurfacePlanRow(
        repository=record.full_name,
        name=record.name,
        estate_class=estate_class,
        theme_family=THEME_FAMILY[estate_class],
        surface_kind=SURFACE_KIND[estate_class],
        evidence_label=evidence_label,
        runtime_state=runtime_state,
        human_surface=human_surface,
        agent_surface=agent_surface,
        public_artifact_eligible=public_artifact_eligible,
        automatic_provider_write=False,
        reason=reason,
    )


def plan_estate(records: list[RepositoryRecord]) -> list[SurfacePlanRow]:
    """Classify the estate deterministically and reject duplicate identities."""

    names = [record.full_name.casefold() for record in records]
    duplicates = sorted(name for name, count in Counter(names).items() if count > 1)
    if duplicates:
        raise EstatePlanError("duplicate repositories in snapshot: " + ", ".join(duplicates))
    return sorted((plan_repository(record) for record in records), key=lambda row: row.repository.casefold())


def canonical_snapshot(records: list[RepositoryRecord]) -> bytes:
    value = [asdict(record) for record in sorted(records, key=lambda row: row.full_name.casefold())]
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def render_plan_json(records: list[RepositoryRecord]) -> str:
    rows = plan_estate(records)
    payload = {
        "schema": PLAN_SCHEMA,
        "policy": {
            "private_publication": "FORBIDDEN",
            "archived_agent_surface": "FORBIDDEN",
            "unknown_flagship_promotion": "FORBIDDEN",
            "automatic_provider_write": False,
            "classification_is_operational_proof": False,
        },
        "repositories": [asdict(row) for row in rows],
    }
    return json.dumps(payload, sort_keys=True, indent=2) + "\n"


def build_receipt(records: list[RepositoryRecord], plan_json: str) -> EstatePlanReceipt:
    rows = plan_estate(records)
    counts = Counter(row.estate_class for row in rows)
    return EstatePlanReceipt(
        schema=RECEIPT_SCHEMA,
        snapshot_sha256=hashlib.sha256(canonical_snapshot(records)).hexdigest(),
        plan_sha256=hashlib.sha256(plan_json.encode("utf-8")).hexdigest(),
        repository_count=len(rows),
        public_artifact_count=sum(row.public_artifact_eligible for row in rows),
        agent_surface_count=sum(row.agent_surface for row in rows),
        class_counts={name: counts.get(name, 0) for name in sorted(ESTATE_CLASSES)},
    )


def load_snapshot(path: Path) -> list[RepositoryRecord]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise EstatePlanError(f"snapshot is not valid JSON: {exc}") from exc
    if not isinstance(value, dict) or set(value) != {"schema", "repositories"}:
        raise EstatePlanError("snapshot root keys must be exactly schema and repositories")
    if value.get("schema") != SNAPSHOT_SCHEMA:
        raise EstatePlanError(f"snapshot schema must be {SNAPSHOT_SCHEMA}")
    rows = value.get("repositories")
    if not isinstance(rows, list) or not rows:
        raise EstatePlanError("repositories must be a non-empty array")
    records: list[RepositoryRecord] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise EstatePlanError(f"repository {index} must be an object")
        records.append(RepositoryRecord.from_mapping(row))
    plan_estate(records)
    return records


def generate_plan(records: list[RepositoryRecord], output: Path) -> list[Path]:
    """Write a deterministic plan and receipt without any provider mutation."""

    output.mkdir(parents=True, exist_ok=True)
    plan_json = render_plan_json(records)
    receipt = build_receipt(records, plan_json)
    plan_path = output / "estate-surface-plan.json"
    receipt_path = output / "estate-surface-plan.receipt.json"
    plan_path.write_text(plan_json, encoding="utf-8", newline="\n")
    receipt_path.write_text(receipt.to_json(), encoding="utf-8", newline="\n")
    return [plan_path, receipt_path]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="szl-estate-plan",
        description="Classify GitHub estate surfaces with fail-closed public/agent boundaries.",
    )
    parser.add_argument("snapshot", type=Path, help="GitHub estate snapshot JSON")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output directory")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        records = load_snapshot(args.snapshot)
        paths = generate_plan(records, args.output)
    except (OSError, EstatePlanError) as exc:
        print(f"error: {exc}")
        return 2
    print(f"generated {len(paths)} estate-plan artifacts for {len(records)} repositories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
