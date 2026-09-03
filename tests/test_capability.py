import json
from pathlib import Path

import pytest

from szl_brand.capability import (
    CAPABILITY_SCHEMA,
    RECEIPT_SCHEMA,
    SCHEMA,
    CapabilityContractError,
    CapabilitySurface,
    build_receipt,
    generate_capabilities,
    load_manifest,
    render_agents_md,
    render_capabilities_json,
)


def surface(**overrides):
    values = {
        "slug": "terra",
        "display_name": "Terra",
        "kind": "space",
        "human_url": "https://szlholdings-terra.hf.space/",
        "source_url": "https://github.com/szl-holdings/szl-real-estate",
        "build_info_url": "https://szlholdings-terra.hf.space/api/build-info",
        "receipt_url": None,
        "operational_state": "OPERATIONAL",
        "limitations": "Public runtime evidence does not authorize acquisition, outreach, or financial action.",
        "capabilities": [
            {
                "name": "build-info",
                "description": "Read the immutable deployment and source identity exposed by the live surface.",
                "interface": "HTTP",
                "method": "GET",
                "endpoint": "https://szlholdings-terra.hf.space/api/build-info",
                "schema_url": None,
                "evidence_label": "MEASURED",
                "authority": "OBSERVE",
                "human_approval": "NOT_APPLICABLE",
                "output_claim": "Reports deployment identity only; it does not establish business outcome quality.",
            },
            {
                "name": "live-evidence",
                "description": "Read the governed public evidence projection without granting downstream authority.",
                "interface": "HTTP",
                "method": "GET",
                "endpoint": "https://szlholdings-terra.hf.space/api/live",
                "schema_url": None,
                "evidence_label": "REPORTED",
                "authority": "OBSERVE",
                "human_approval": "NOT_APPLICABLE",
                "output_claim": "Returns the current public projection and explicit availability state.",
            },
        ],
    }
    values.update(overrides)
    return CapabilitySurface.from_mapping(values)


def test_capabilities_json_is_deterministic_and_fail_closed():
    item = surface()
    first = render_capabilities_json(item)
    second = render_capabilities_json(item)
    payload = json.loads(first)

    assert first == second
    assert payload["schema"] == CAPABILITY_SCHEMA
    assert payload["authority_model"]["discovery_grants_authority"] is False
    assert payload["authority_model"]["bounded_actions_require_review"] is True
    assert payload["proof"]["receipt_url"] == "UNAVAILABLE"
    assert "DENIED" in payload["authority_model"]["failure_states"]
    assert payload["capabilities"][0]["authority"] == "OBSERVE"


def test_agents_md_exposes_callability_authority_evidence_and_proof():
    text = render_agents_md(surface())

    assert "Capability discovery does not grant authority" in text
    assert "BOUNDED_ACTION" in text
    assert "REQUIRES_APPROVAL" in text
    assert "`GET https://szlholdings-terra.hf.space/api/build-info`" in text
    assert "`MEASURED`" in text
    assert "Build identity" in text
    assert "Receipt / evidence: `UNAVAILABLE`" in text


def test_observe_cannot_hide_a_mutating_method():
    bad = surface().__dict__.copy()
    actions = [dict(item) for item in bad["capabilities"]]
    actions[0].update({"method": "POST", "authority": "OBSERVE"})
    bad["capabilities"] = actions

    with pytest.raises(CapabilityContractError, match="OBSERVE authority"):
        CapabilitySurface.from_mapping(bad)


def test_bounded_action_requires_review():
    bad = surface().__dict__.copy()
    actions = [dict(item) for item in bad["capabilities"]]
    actions[0].update(
        {
            "method": "POST",
            "authority": "BOUNDED_ACTION",
            "human_approval": "NOT_APPLICABLE",
        }
    )
    bad["capabilities"] = actions

    with pytest.raises(CapabilityContractError, match="BOUNDED_ACTION must preserve"):
        CapabilitySurface.from_mapping(bad)


def test_propose_requires_human_review():
    bad = surface().__dict__.copy()
    actions = [dict(item) for item in bad["capabilities"]]
    actions[0].update(
        {
            "method": "POST",
            "authority": "PROPOSE",
            "human_approval": "NOT_APPLICABLE",
        }
    )
    bad["capabilities"] = actions

    with pytest.raises(CapabilityContractError, match="PROPOSE must preserve"):
        CapabilitySurface.from_mapping(bad)


def test_document_interface_is_read_only():
    bad = surface().__dict__.copy()
    actions = [dict(item) for item in bad["capabilities"]]
    actions[0].update({"interface": "DOCUMENT", "method": "GET"})
    bad["capabilities"] = actions

    with pytest.raises(CapabilityContractError, match="DOCUMENT capabilities must use READ"):
        CapabilitySurface.from_mapping(bad)


def test_duplicate_capability_names_fail_closed():
    bad = surface().__dict__.copy()
    actions = [dict(item) for item in bad["capabilities"]]
    actions[1]["name"] = actions[0]["name"]
    bad["capabilities"] = actions

    with pytest.raises(CapabilityContractError, match="unique"):
        CapabilitySurface.from_mapping(bad)


def test_missing_proof_urls_stay_explicitly_unavailable():
    item = surface(build_info_url=None, receipt_url=None)
    payload = json.loads(render_capabilities_json(item))
    agents = render_agents_md(item)

    assert payload["proof"] == {
        "build_info_url": "UNAVAILABLE",
        "receipt_url": "UNAVAILABLE",
    }
    assert "Build identity: `UNAVAILABLE`" in agents
    assert "Receipt / evidence: `UNAVAILABLE`" in agents


def test_generation_writes_agent_contract_and_receipt(tmp_path: Path):
    manifest = tmp_path / "capabilities.json"
    raw = surface().__dict__.copy()
    raw["capabilities"] = [dict(item) for item in raw["capabilities"]]
    manifest.write_text(
        json.dumps({"schema": SCHEMA, "surfaces": [raw]}),
        encoding="utf-8",
    )

    rows = load_manifest(manifest)
    paths = generate_capabilities(rows, tmp_path / "out")

    assert len(paths) == 3
    directory = tmp_path / "out" / "terra"
    assert (directory / "agents.md").exists()
    assert (directory / "capabilities.json").exists()
    receipt = json.loads(
        (directory / "capability-receipt.json").read_text(encoding="utf-8")
    )
    assert receipt["schema"] == RECEIPT_SCHEMA
    assert receipt["capability_count"] == 2
    assert receipt["bounded_action_count"] == 0
    assert len(receipt["contract_sha256"]) == 64
    assert len(receipt["capabilities_sha256"]) == 64
    assert len(receipt["agents_md_sha256"]) == 64


def test_receipt_changes_when_authority_contract_changes():
    observed = surface()
    raw = observed.__dict__.copy()
    actions = [dict(item) for item in raw["capabilities"]]
    actions[0].update(
        {
            "method": "POST",
            "authority": "PROPOSE",
            "human_approval": "REQUIRED",
        }
    )
    raw["capabilities"] = actions
    proposed = CapabilitySurface.from_mapping(raw)

    observed_json = render_capabilities_json(observed)
    proposed_json = render_capabilities_json(proposed)
    observed_md = render_agents_md(observed)
    proposed_md = render_agents_md(proposed)
    observed_receipt = build_receipt(observed, observed_json, observed_md)
    proposed_receipt = build_receipt(proposed, proposed_json, proposed_md)

    assert observed_receipt.contract_sha256 != proposed_receipt.contract_sha256
    assert observed_receipt.capabilities_sha256 != proposed_receipt.capabilities_sha256
    assert observed_receipt.agents_md_sha256 != proposed_receipt.agents_md_sha256
