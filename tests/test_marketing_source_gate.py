"""Source checks around the credential-scoped marketing Space upload step."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from szl_brand.marketing import source_gate

SHA = "a" * 40
MOVED = "b" * 40
ROOT = "c" * 64


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _paths(tmp_path: Path) -> tuple[Path, Path, Path]:
    package = tmp_path / "package"
    _write(
        package / "PUBLICATION_RECEIPT.json",
        {"source": {"sha": SHA}, "root_sha256": ROOT},
    )
    return package, tmp_path / "publish.json", tmp_path / "source-gate.json"


def _check(
    phase: str, package: Path, publish_report: Path, gate_report: Path, main_sha: str | None
) -> bool:
    return source_gate.check_source_gate(
        phase=phase,
        package=package,
        expected_sha=SHA,
        publish_report=publish_report,
        gate_report=gate_report,
        checkout_sha=SHA,
        main_sha=main_sha,
    )


def _published(
    report: Path, *, state: str = "PUBLISHED_CONVERGED", write: str = "COMMIT_RETURNED"
) -> None:
    _write(
        report,
        {
            "state": state,
            "hub_write_state": write,
            "source": {"sha": SHA},
            "root_sha256": ROOT,
            "secrets_recorded": False,
        },
    )


def test_moved_main_before_upload_blocks_without_hub_write(tmp_path: Path) -> None:
    package, report, gate = _paths(tmp_path)
    assert not _check("before", package, report, gate, MOVED)
    saved = _read(report)
    assert saved["state"] == "SOURCE_GATE_FAILED_BEFORE_UPLOAD"
    assert saved["hub_write_state"] == "NOT_ATTEMPTED"
    assert saved["secrets_recorded"] is False
    assert _read(gate)["before"]["failure_codes"] == ["CURRENT_MAIN_MOVED"]
    assert _read(gate)["package_root_sha256"] == ROOT


def test_moved_main_after_upload_marks_nonconvergence_and_preserves_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    package, report, gate = _paths(tmp_path)
    monkeypatch.setenv("HF_TOKEN", "TOKEN-CANARY-DO-NOT-RECORD")
    assert _check("before", package, report, gate, SHA)
    _published(report)

    assert not _check("after", package, report, gate, MOVED)
    saved = _read(report)
    assert saved["state"] == "SOURCE_GATE_FAILED_AFTER_UPLOAD"
    assert saved["provider_state_before_source_gate"] == "PUBLISHED_CONVERGED"
    assert saved["hub_write_state"] == "COMMIT_RETURNED"
    assert saved["release_convergence"] == "NON_CONVERGED_SOURCE_GATE"
    assert saved["source_head_gate"]["failure_codes"] == ["CURRENT_MAIN_MOVED"]
    assert _read(gate)["after"]["observed_main_sha"] == MOVED
    assert "TOKEN-CANARY-DO-NOT-RECORD" not in report.read_text(encoding="utf-8")
    assert "TOKEN-CANARY-DO-NOT-RECORD" not in gate.read_text(encoding="utf-8")


@pytest.mark.parametrize("bad_before", [None, "TOKEN-CANARY", [], 42])
def test_malformed_before_gate_never_leaves_converged_report(
    tmp_path: Path, bad_before: object
) -> None:
    package, report, gate = _paths(tmp_path)
    _write(
        gate,
        {
            "before": bad_before,
            "expected_main_sha": SHA,
            "package_source_sha": SHA,
            "package_root_sha256": ROOT,
            "secrets_recorded": False,
            "extra": "TOKEN-CANARY",
        },
    )
    _published(report)

    assert not _check("after", package, report, gate, SHA)
    saved = _read(report)
    assert saved["state"] == "SOURCE_GATE_FAILED_AFTER_UPLOAD"
    assert saved["hub_write_state"] == "COMMIT_RETURNED"
    assert saved["source_head_gate"]["failure_codes"] == ["BEFORE_GATE_UNBOUND"]
    assert _read(gate)["before"]["result"] == "FAIL"
    assert "TOKEN-CANARY" not in gate.read_text(encoding="utf-8")


def test_unavailable_main_after_provider_failure_retains_uncertain_write(tmp_path: Path) -> None:
    package, report, gate = _paths(tmp_path)
    assert _check("before", package, report, gate, SHA)
    _published(report, state="FAILED", write="UNKNOWN")

    assert not _check("after", package, report, gate, None)
    saved = _read(report)
    assert saved["state"] == "FAILED"
    assert saved["hub_write_state"] == "UNKNOWN"
    assert saved["release_convergence"] == "NON_CONVERGED_SOURCE_GATE"
    assert saved["source_head_gate"]["failure_codes"] == ["CURRENT_MAIN_UNAVAILABLE"]


def test_current_main_after_upload_keeps_hub_convergence(tmp_path: Path) -> None:
    package, report, gate = _paths(tmp_path)
    assert _check("before", package, report, gate, SHA)
    _published(report)

    assert _check("after", package, report, gate, SHA)
    saved = _read(report)
    assert saved["state"] == "PUBLISHED_CONVERGED"
    assert saved["hub_write_state"] == "COMMIT_RETURNED"
    assert saved["source_head_gate"]["result"] == "PASS"
    assert _read(gate)["after"]["result"] == "PASS"


def test_git_children_do_not_inherit_hub_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HF_TOKEN", "TOKEN-CANARY")
    monkeypatch.setenv("HF_TOKEN_SOURCE", "HF_ORG_TOKEN")
    monkeypatch.setenv("HF_ORG_TOKEN", "TOKEN-CANARY")
    monkeypatch.setenv("HUGGING_FACE_HUB_TOKEN", "TOKEN-CANARY")
    monkeypatch.setenv("HF_OIDC_RESOURCE", "spaces/TOKEN-CANARY")
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "TOKEN-CANARY")
    safe = source_gate._git_env()
    assert all(
        name not in safe
        for name in (
            "HF_TOKEN",
            "HF_TOKEN_SOURCE",
            "HF_ORG_TOKEN",
            "HUGGING_FACE_HUB_TOKEN",
            "HF_OIDC_RESOURCE",
            "ACTIONS_ID_TOKEN_REQUEST_TOKEN",
        )
    )
    assert safe["GIT_TERMINAL_PROMPT"] == "0"


def test_workflow_scopes_credential_and_checks_each_side_of_upload() -> None:
    workflow = (
        Path(__file__).resolve().parents[1] / ".github/workflows/hf-marketing-spaces.yml"
    ).read_text(encoding="utf-8")
    build_job, publish_job = workflow.split("  publish:\n", 1)
    publish_step = publish_job.split("      - name: Upload secret-free per-target receipts", 1)[0]
    assert "secrets.HF_ORG_TOKEN" not in workflow
    assert "secrets.HF_TOKEN" not in workflow
    assert workflow.count("          ref: main\n") == 2
    assert "ref: ${{ env.PUBLISH_SHA }}" not in workflow
    assert "id-token: write" not in build_job
    assert "tests/test_marketing_source_gate.py" in build_job
    assert (
        'python -m pip wheel --disable-pip-version-check --wheel-dir dist/publisher-wheels ".[publish]"'
        in build_job
    )
    assert "--no-index --find-links dist/publisher-wheels" in publish_job
    assert 'dist/publisher-wheels "szl-brand[publish]"' in publish_job
    assert 'python -c "from huggingface_hub import get_token"' in publish_job
    assert "id-token: write" in publish_job
    assert publish_job.index(
        "Prove publisher checkout matches qualified current main"
    ) < publish_job.index("Install qualified publisher offline")
    assert "HF_OIDC_RESOURCE: spaces/SZLHOLDINGS/${{ matrix.target }}" in publish_step
    assert "matrix.target" in publish_job
    assert publish_step.count("env -u HF_TOKEN -u HF_TOKEN_SOURCE python -m") == 2
    first_gate = publish_step.index("--phase before")
    upload = publish_step.index("szl-marketing space-publish")
    second_gate = publish_step.index("--phase after")
    assert first_gate < upload < second_gate
