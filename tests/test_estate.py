import json
from pathlib import Path

import pytest

from szl_brand.estate import (
    FLAGSHIP_PRODUCT,
    GOVERNANCE_PROOF,
    HISTORICAL,
    INTERNAL,
    PLAN_SCHEMA,
    RECEIPT_SCHEMA,
    RESEARCH_FORMULA,
    RUNTIME_INFRA,
    SNAPSHOT_SCHEMA,
    UNCLASSIFIED,
    EstatePlanError,
    RepositoryRecord,
    build_receipt,
    generate_plan,
    load_snapshot,
    plan_estate,
    plan_repository,
    render_plan_json,
)


def repo(**overrides):
    values = {
        "name": "a11oy",
        "full_name": "szl-holdings/a11oy",
        "visibility": "public",
        "archived": False,
        "default_branch": "main",
    }
    values.update(overrides)
    return RepositoryRecord.from_mapping(values)


def test_private_repo_can_never_become_public_flagship():
    record = repo(visibility="private")
    row = plan_repository(record)

    assert row.estate_class == INTERNAL
    assert row.public_artifact_eligible is False
    assert row.human_surface is False
    assert row.agent_surface is False
    assert row.automatic_provider_write is False
    assert row.evidence_label == "UNAVAILABLE"


def test_archived_repo_is_always_historical_even_if_name_matches_flagship():
    row = plan_repository(repo(archived=True))

    assert row.estate_class == HISTORICAL
    assert row.surface_kind == "archived"
    assert row.theme_family == "ARCHIVE_MONO"
    assert row.runtime_state == "HISTORICAL"
    assert row.agent_surface is False
    assert row.public_artifact_eligible is True


def test_unknown_public_repo_never_promotes_itself_by_name_shape():
    row = plan_repository(
        repo(name="next-world-platform", full_name="szl-holdings/next-world-platform")
    )

    assert row.estate_class == UNCLASSIFIED
    assert row.theme_family == "NEUTRAL_REVIEW"
    assert row.evidence_label == "UNKNOWN"
    assert row.runtime_state == "UNKNOWN"
    assert row.human_surface is True
    assert row.agent_surface is False


def test_reviewed_public_classes_receive_distinct_theme_contracts():
    rows = {
        item.name: item
        for item in (
            plan_repository(repo()),
            plan_repository(
                repo(
                    name="hatun-mcp",
                    full_name="szl-holdings/hatun-mcp",
                )
            ),
            plan_repository(
                repo(
                    name="szl-trust",
                    full_name="szl-holdings/szl-trust",
                )
            ),
            plan_repository(
                repo(
                    name="szl-quant",
                    full_name="szl-holdings/szl-quant",
                )
            ),
        )
    }

    assert rows["a11oy"].estate_class == FLAGSHIP_PRODUCT
    assert rows["a11oy"].theme_family == "DOMAIN_COMMAND"
    assert rows["hatun-mcp"].estate_class == RUNTIME_INFRA
    assert rows["hatun-mcp"].theme_family == "SUBSTRATE_RUNTIME"
    assert rows["szl-trust"].estate_class == GOVERNANCE_PROOF
    assert rows["szl-trust"].theme_family == "PROOF_LEDGER"
    assert rows["szl-quant"].estate_class == RESEARCH_FORMULA
    assert rows["szl-quant"].theme_family == "FORMULA_NOTEBOOK"
    assert len({row.theme_family for row in rows.values()}) == 4


def test_classification_never_claims_runtime_operational_status():
    row = plan_repository(repo())

    assert row.estate_class == FLAGSHIP_PRODUCT
    assert row.evidence_label == "UNKNOWN"
    assert row.runtime_state == "UNKNOWN"
    assert row.automatic_provider_write is False


def test_duplicate_repository_identity_fails_closed():
    with pytest.raises(EstatePlanError, match="duplicate repositories"):
        plan_estate([repo(), repo()])


def test_plan_json_exposes_non_bypassable_rollout_policy():
    payload = json.loads(render_plan_json([repo()]))

    assert payload["schema"] == PLAN_SCHEMA
    assert payload["policy"]["private_publication"] == "FORBIDDEN"
    assert payload["policy"]["archived_agent_surface"] == "FORBIDDEN"
    assert payload["policy"]["unknown_flagship_promotion"] == "FORBIDDEN"
    assert payload["policy"]["automatic_provider_write"] is False
    assert payload["policy"]["classification_is_operational_proof"] is False


def test_receipt_is_deterministic_and_binds_snapshot_and_plan():
    records = [
        repo(),
        repo(name="szl-trust", full_name="szl-holdings/szl-trust"),
    ]
    first_plan = render_plan_json(records)
    second_plan = render_plan_json(list(reversed(records)))
    first = build_receipt(records, first_plan)
    second = build_receipt(list(reversed(records)), second_plan)

    assert first.schema == RECEIPT_SCHEMA
    assert first.snapshot_sha256 == second.snapshot_sha256
    assert first.plan_sha256 == second.plan_sha256
    assert first.repository_count == 2
    assert first.public_artifact_count == 2
    assert first.agent_surface_count == 2


def test_snapshot_generation_writes_only_plan_and_receipt(tmp_path: Path):
    snapshot = tmp_path / "snapshot.json"
    snapshot.write_text(
        json.dumps(
            {
                "schema": SNAPSHOT_SCHEMA,
                "repositories": [
                    {
                        "name": "a11oy",
                        "full_name": "szl-holdings/a11oy",
                        "visibility": "public",
                        "archived": False,
                        "default_branch": "main",
                    },
                    {
                        "name": "secret-control",
                        "full_name": "szl-holdings/secret-control",
                        "visibility": "private",
                        "archived": False,
                        "default_branch": "main",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    records = load_snapshot(snapshot)
    paths = generate_plan(records, tmp_path / "out")

    assert len(paths) == 2
    plan = json.loads((tmp_path / "out" / "estate-surface-plan.json").read_text())
    receipt = json.loads((tmp_path / "out" / "estate-surface-plan.receipt.json").read_text())
    assert receipt["schema"] == RECEIPT_SCHEMA
    assert plan["repositories"][0]["repository"] == "szl-holdings/a11oy"
    private = next(row for row in plan["repositories"] if row["name"] == "secret-control")
    assert private["estate_class"] == INTERNAL
    assert private["public_artifact_eligible"] is False
