"""Run the Hypothesis property suite and report its pytest exit code honestly.

The old fuzz workflow ran ``pytest ... || echo "No fuzz tests found yet"``,
which turned every failure, collection error and usage error green.  This
gate passes real failures through unchanged and reports only pytest exit
code 5 ("no tests collected") as an explicit NOT_RUN. A successful pytest
exit also needs at least one completed, passing test case; collect-only,
all-skipped and all-xfailed suites are NOT_RUN.

NOT_RUN fails the job too: a green "Fuzz" check must never mean "nothing was
fuzzed".  Usage: ``python tools/fuzz_gate.py [pytest args...]``.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

# pytest.ExitCode values, kept literal so this module imports without pytest.
OK, TESTS_FAILED, INTERRUPTED, INTERNAL_ERROR, USAGE_ERROR, NO_TESTS_COLLECTED = range(6)

_LABELS = {
    OK: "PASS",
    TESTS_FAILED: "FAIL (property tests failed)",
    INTERRUPTED: "FAIL (interrupted, e.g. collection or import error)",
    INTERNAL_ERROR: "FAIL (pytest internal error)",
    USAGE_ERROR: "FAIL (pytest usage error)",
    NO_TESTS_COLLECTED: "NOT_RUN (no property tests collected)",
}


def classify(code: int) -> tuple[str, int]:
    """Map a pytest exit code to (status, job exit code). Only 0 is green."""
    if code == OK:
        return "PASS", 0
    if code == NO_TESTS_COLLECTED:
        return "NOT_RUN", 1
    return "FAIL", code if code > 0 else 1


def _passing_cases(report_path: Path) -> int:
    """Count completed cases, excluding skipped/xfail, failure and error reports."""
    root = ET.parse(report_path).getroot()
    if root.tag not in {"testsuite", "testsuites"}:
        raise ValueError("unexpected pytest report root")
    return sum(
        1
        for case in root.iter("testcase")
        if not any(case.find(tag) is not None for tag in ("skipped", "failure", "error"))
    )


def _summary(status: str, code: int, args: list[str], passed: int | None, reason: str) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    label = _LABELS.get(code, f"FAIL (unexpected pytest exit {code})")
    lines = [
        "## Fuzz (Hypothesis)",
        "",
        f"- status: **{status}**",
        f"- pytest exit code: `{code}` ({label})",
        f"- command: `python -m pytest {' '.join(args)}`",
        f"- completed passing cases: `{passed if passed is not None else 'unavailable'}`",
        f"- detail: {reason}",
    ]
    if status == "NOT_RUN":
        lines.append(
            "- No completed passing property test was observed. "
            "This job stays red until the selected suite actually runs."
        )
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main(argv: list[str]) -> int:
    args = argv or ["-m", "hypothesis", "tests"]
    passed = None
    reason = "pytest did not complete successfully"
    with tempfile.TemporaryDirectory(prefix="szl-fuzz-report-") as directory:
        report_path = Path(directory) / "pytest.xml"
        # Append the gate-owned report option so an earlier caller option cannot
        # replace the execution evidence used for this decision.
        code = subprocess.call([sys.executable, "-m", "pytest", *args, f"--junitxml={report_path}"])
        status, exit_code = classify(code)
        if code == OK:
            try:
                passed = _passing_cases(report_path)
            except (OSError, ET.ParseError, ValueError):
                status, exit_code = "FAIL", 1
                reason = "pytest execution report missing or unreadable"
            else:
                reason = f"{passed} completed passing test cases"
                if passed == 0:
                    status, exit_code = "NOT_RUN", 1
    if status == "NOT_RUN":
        print(
            f"::error title=Fuzz NOT_RUN::pytest exit {code}: no completed passing property tests."
        )
    elif status == "FAIL":
        print(f"::error title=Fuzz FAIL::pytest exit {code}: {reason}")
    print(f"fuzz_gate: status={status} pytest_exit={code} job_exit={exit_code}")
    _summary(status, code, args, passed, reason)
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
