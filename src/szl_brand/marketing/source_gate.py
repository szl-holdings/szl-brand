"""Fail-closed protected-main checks around each marketing Space upload.

Only immutable source identifiers and fixed status codes enter the public receipts.
The Hub token is removed from this process by the workflow and from Git children here.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

_SHA40 = re.compile(r"[0-9a-f]{40}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_FETCH_REF = "+refs/heads/main:refs/remotes/origin/main"


def _safe_sha(value: Any, pattern: re.Pattern[str]) -> str | None:
    return value if isinstance(value, str) and pattern.fullmatch(value) else None


def _load(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _git_env() -> dict[str, str]:
    env = os.environ.copy()
    for name in (
        "HF_TOKEN",
        "HF_TOKEN_SOURCE",
        "HF_ORG_TOKEN",
        "HUGGING_FACE_HUB_TOKEN",
        "HF_OIDC_RESOURCE",
        "HF_OIDC_ID_TOKEN",
        "ACTIONS_ID_TOKEN_REQUEST_URL",
        "ACTIONS_ID_TOKEN_REQUEST_TOKEN",
    ):
        env.pop(name, None)
    env["GIT_TERMINAL_PROMPT"] = "0"
    return env


def _git_sha(ref: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", ref],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            env=_git_env(),
        )
    except OSError:
        return None
    return _safe_sha(result.stdout.strip(), _SHA40) if result.returncode == 0 else None


def _current_main() -> str | None:
    try:
        result = subprocess.run(
            ["git", "fetch", "--no-tags", "--depth=1", "origin", _FETCH_REF],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=_git_env(),
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return _git_sha("refs/remotes/origin/main")


def check_source_gate(
    *,
    phase: str,
    package: Path,
    expected_sha: str,
    publish_report: Path,
    gate_report: Path,
    checkout_sha: str | None,
    main_sha: str | None,
) -> bool:
    """Record a point-in-time source gate; preserve possible Hub writes on failure."""
    if phase not in {"before", "after"}:
        raise ValueError("phase must be before or after")

    package_receipt = _load(package / "PUBLICATION_RECEIPT.json")
    source = package_receipt.get("source") if package_receipt else None
    package_sha = _safe_sha(source.get("sha"), _SHA40) if isinstance(source, dict) else None
    package_root = (
        _safe_sha(package_receipt.get("root_sha256"), _SHA256) if package_receipt else None
    )
    expected = _safe_sha(expected_sha, _SHA40)
    checkout = _safe_sha(checkout_sha, _SHA40)
    main = _safe_sha(main_sha, _SHA40)

    failures: list[str] = []
    if expected is None or package_sha != expected or package_root is None:
        failures.append("PACKAGE_SOURCE_UNBOUND")
    if checkout != expected:
        failures.append("CHECKOUT_SOURCE_MOVED")
    if main is None:
        failures.append("CURRENT_MAIN_UNAVAILABLE")
    elif main != expected:
        failures.append("CURRENT_MAIN_MOVED")

    previous_gate = _load(gate_report) if phase == "after" else None
    provider_report = _load(publish_report) if phase == "after" else None
    previous_before = previous_gate.get("before") if previous_gate else None
    before_is_bound = (
        isinstance(previous_before, dict)
        and previous_before.get("result") == "PASS"
        and previous_before.get("failure_codes") == []
        and previous_before.get("checkout_sha") == expected
        and previous_before.get("observed_main_sha") == expected
        and previous_gate.get("schema") == "szl-brand-source-gate-v1"
        and previous_gate.get("expected_main_sha") == expected
        and previous_gate.get("package_source_sha") == package_sha
        and previous_gate.get("package_root_sha256") == package_root
        and previous_gate.get("secrets_recorded") is False
    )
    if phase == "after":
        if not before_is_bound:
            failures.append("BEFORE_GATE_UNBOUND")
        provider_source = provider_report.get("source") if provider_report else None
        if (
            provider_report is None
            or not isinstance(provider_source, dict)
            or provider_source.get("sha") != package_sha
            or provider_report.get("root_sha256") != package_root
            or provider_report.get("secrets_recorded") is not False
            or provider_report.get("hub_write_state")
            not in {"NOT_ATTEMPTED", "UNKNOWN", "COMMIT_RETURNED"}
        ):
            failures.append("PUBLISH_REPORT_UNBOUND")

    observation = {
        "result": "FAIL" if failures else "PASS",
        "failure_codes": failures,
        "checkout_sha": checkout,
        "observed_main_sha": main,
    }
    gate = {
        "schema": "szl-brand-source-gate-v1",
        "expected_main_sha": expected,
        "package_source_sha": package_sha,
        "package_root_sha256": package_root,
        "secrets_recorded": False,
    }
    if phase == "after":
        # Reconstruct only fixed fields; malformed prior JSON must not pass
        # through to an Actions artifact or leave a converged publish receipt.
        gate["before"] = {
            "result": "PASS" if before_is_bound else "FAIL",
            "failure_codes": [] if before_is_bound else ["BEFORE_GATE_UNBOUND"],
            "checkout_sha": expected if before_is_bound else None,
            "observed_main_sha": expected if before_is_bound else None,
        }
    gate[phase] = observation
    _write(gate_report, gate)

    if phase == "before" and failures:
        _write(
            publish_report,
            {
                "state": "SOURCE_GATE_FAILED_BEFORE_UPLOAD",
                "hub_write_state": "NOT_ATTEMPTED",
                "source": {"sha": package_sha},
                "root_sha256": package_root,
                "source_head_gate": observation,
                "secrets_recorded": False,
            },
        )
    elif phase == "after":
        if provider_report is None:
            provider_report = {
                "state": "SOURCE_GATE_FAILED_AFTER_UPLOAD",
                "hub_write_state": "UNKNOWN",
                "source": {"sha": package_sha},
                "root_sha256": package_root,
                "secrets_recorded": False,
            }
        provider_report["source_head_gate"] = observation
        if failures:
            provider_report["release_convergence"] = "NON_CONVERGED_SOURCE_GATE"
            if provider_report.get("state") == "PUBLISHED_CONVERGED":
                provider_report["provider_state_before_source_gate"] = "PUBLISHED_CONVERGED"
                provider_report["state"] = "SOURCE_GATE_FAILED_AFTER_UPLOAD"
        _write(publish_report, provider_report)

    return not failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("before", "after"), required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--publish-report", type=Path, required=True)
    parser.add_argument("--gate-report", type=Path, required=True)
    args = parser.parse_args()
    passed = check_source_gate(
        phase=args.phase,
        package=args.package,
        expected_sha=args.expected_sha,
        publish_report=args.publish_report,
        gate_report=args.gate_report,
        checkout_sha=_git_sha("HEAD"),
        main_sha=_current_main(),
    )
    print(f"source gate {args.phase}: {'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
