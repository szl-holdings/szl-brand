"""Run the Hypothesis property suite and report its pytest exit code honestly.

The old fuzz workflow ran ``pytest ... || echo "No fuzz tests found yet"``,
which turned every failure, collection error and usage error green.  This
gate passes real failures through unchanged and reports only pytest exit
code 5 ("no tests collected") as an explicit NOT_RUN.

NOT_RUN fails the job too: a green "Fuzz" check must never mean "nothing was
fuzzed".  Usage: ``python tools/fuzz_gate.py [pytest args...]``.
"""

from __future__ import annotations

import os
import subprocess
import sys

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


def _summary(status: str, code: int, args: list[str]) -> None:
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
    ]
    if status == "NOT_RUN":
        lines.append(
            "- No property tests were collected, so nothing was fuzzed. "
            "This job stays red until a Hypothesis suite exists."
        )
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main(argv: list[str]) -> int:
    args = argv or ["-m", "hypothesis", "tests"]
    code = subprocess.call([sys.executable, "-m", "pytest", *args])
    status, exit_code = classify(code)
    if status == "NOT_RUN":
        print("::error title=Fuzz NOT_RUN::pytest exit 5: no property tests collected; nothing was fuzzed.")
    elif status == "FAIL":
        print(f"::error title=Fuzz FAIL::pytest exit {code}: {_LABELS.get(code, 'unexpected exit')}")
    print(f"fuzz_gate: status={status} pytest_exit={code} job_exit={exit_code}")
    _summary(status, code, args)
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
