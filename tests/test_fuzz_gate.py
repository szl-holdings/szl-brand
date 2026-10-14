"""Exit-code contract for tools/fuzz_gate.py (the Fuzz workflow gate).

Each case writes an inert fixture suite into tmp_path and runs the real gate
against it, so a failing property test, a collection error and an empty suite
are proven to produce the job exit the workflow relies on.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

GATE = Path(__file__).resolve().parents[1] / "tools" / "fuzz_gate.py"

_INI = "[pytest]\nmarkers =\n    hypothesis: property test\n"

_PASSING = "import pytest\n\n@pytest.mark.hypothesis\ndef test_prop():\n    assert 1 + 1 == 2\n"
_FAILING = "import pytest\n\n@pytest.mark.hypothesis\ndef test_prop():\n    assert 1 + 1 == 3\n"
_BROKEN_IMPORT = "import pytest\nimport szl_fuzz_gate_missing_module  # noqa: F401\n"
_UNMARKED = "def test_plain():\n    assert True\n"


def _load_gate():
    spec = importlib.util.spec_from_file_location("fuzz_gate", GATE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run(tmp_path: Path, files: dict[str, str]) -> subprocess.CompletedProcess[str]:
    (tmp_path / "pytest.ini").write_text(_INI, encoding="utf-8")
    for name, body in files.items():
        (tmp_path / name).write_text(body, encoding="utf-8")
    summary = tmp_path / "summary.md"
    return subprocess.run(
        [sys.executable, str(GATE), "-p", "no:cacheprovider", "-m", "hypothesis", "."],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env={**__import__("os").environ, "GITHUB_STEP_SUMMARY": str(summary)},
        timeout=120,
    )


@pytest.mark.parametrize(
    ("code", "status", "job_exit"),
    [
        (0, "PASS", 0),
        (1, "FAIL", 1),
        (2, "FAIL", 2),
        (3, "FAIL", 3),
        (4, "FAIL", 4),
        (5, "NOT_RUN", 1),
    ],
)
def test_classify(code: int, status: str, job_exit: int) -> None:
    assert _load_gate().classify(code) == (status, job_exit)


def test_passing_property_suite_is_green(tmp_path: Path) -> None:
    result = _run(tmp_path, {"test_ok.py": _PASSING})
    assert result.returncode == 0, result.stdout
    assert "status=PASS pytest_exit=0" in result.stdout


def test_failing_property_test_fails_the_job(tmp_path: Path) -> None:
    result = _run(tmp_path, {"test_bad.py": _FAILING})
    assert result.returncode == 1, result.stdout
    assert "status=FAIL pytest_exit=1" in result.stdout
    assert "No fuzz tests found" not in result.stdout


def test_collection_error_fails_the_job(tmp_path: Path) -> None:
    result = _run(tmp_path, {"test_ok.py": _PASSING, "test_broken.py": _BROKEN_IMPORT})
    assert result.returncode != 0, result.stdout
    assert "status=FAIL" in result.stdout


def test_empty_suite_is_reported_not_run(tmp_path: Path) -> None:
    result = _run(tmp_path, {"test_plain.py": _UNMARKED})
    assert result.returncode == 1, result.stdout
    assert "status=NOT_RUN pytest_exit=5" in result.stdout
    summary = (tmp_path / "summary.md").read_text(encoding="utf-8")
    assert "**NOT_RUN**" in summary
