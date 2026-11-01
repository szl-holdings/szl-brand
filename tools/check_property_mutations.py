"""Bounded mutation checks for tests/test_properties.py.

Every variant runs in a disposable copy. Production files in the checkout are
never modified. A mutation is killed only by a pytest assertion failure; import
errors, collection errors, and timeouts fail this harness.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MUTATIONS = [
    ("hex_loses_alpha", "palette.py", "if self.a == 255:", "if True:", "hex_roundtrip"),
    (
        "contrast_always_one",
        "palette.py",
        "return (l1 + 0.05) / (l2 + 0.05)",
        "return 1.0",
        "contrast_symmetry",
    ),
    (
        "interpolation_unclamped",
        "palette.py",
        "t = max(0.0, min(1.0, t))",
        "t = t",
        "interpolation_endpoints",
    ),
    (
        "alpha_ignored",
        "palette.py",
        "return Color(self.r, self.g, self.b, alpha)",
        "return self",
        "alpha_replacement",
    ),
    (
        "seed_ignored",
        "palette.py",
        "self._hash = hashlib.sha256(seed.encode()).digest()",
        "self._hash = bytes(32)",
        "repository_seed",
    ),
    (
        "accent_always_first",
        "palette.py",
        "return accents[index % len(accents)]",
        "return accents[0]",
        "repository_seed",
    ),
    (
        "noise_out_of_bounds",
        "palette.py",
        "yield (x, y, val)",
        "yield (x, y, val + 1)",
        "noise_is_reproducible",
    ),
    (
        "manifest_hash_zeroed",
        "validate.py",
        "return h.hexdigest()",
        'return "0" * 64',
        "manifest_tracks",
    ),
    (
        "manifest_root_lost",
        "validate.py",
        'root_hash=d.get("root_hash", ""),',
        'root_hash="",',
        "manifest_tracks",
    ),
    (
        "modified_asset_ignored",
        "validate.py",
        "elif manifest_paths[path] != sha:",
        "elif False:",
        "drift_distinguishes",
    ),
    (
        "preview_wrong_dimensions",
        "preview.py",
        "W, H = 1280, 640",
        "W, H = 1280, 639",
        "preview_is_byte",
    ),
    (
        "preview_depends_on_output_name",
        "preview.py",
        'img.save(output, "PNG", optimize=True)',
        'img.putpixel((0, 0), (ord(output.stem[0]), 0, 0))\n    img.save(output, "PNG", optimize=True)',
        "preview_is_byte",
    ),
    (
        "preview_ignores_repository",
        "preview.py",
        "palette = ProcPalette(spec.repo)",
        'palette = ProcPalette("constant")',
        "preview_is_byte",
    ),
]


def run_variant(name: str, filename: str | None, old: str, new: str, selector: str) -> dict:
    with tempfile.TemporaryDirectory(prefix="szl-brand-mutation-") as directory:
        work = Path(directory)
        shutil.copytree(ROOT / "src", work / "src", ignore=shutil.ignore_patterns("__pycache__"))
        (work / "tests").mkdir()
        shutil.copy2(ROOT / "tests/test_properties.py", work / "tests/test_properties.py")
        (work / "pytest.ini").write_text(
            "[pytest]\nmarkers =\n    hypothesis: generated-input SDK contract tests\n",
            encoding="utf-8",
        )
        if filename:
            target = work / "src/szl_brand" / filename
            original = target.read_text(encoding="utf-8")
            if original.count(old) != 1:
                raise RuntimeError(f"{name}: mutation anchor no longer unique")
            target.write_text(original.replace(old, new, 1), encoding="utf-8")
        command = [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--tb=short",
            "--hypothesis-seed=0",
            "tests/test_properties.py",
        ]
        if selector:
            command += ["-k", selector]
        result = subprocess.run(
            command,
            cwd=work,
            capture_output=True,
            text=True,
            timeout=180,
            env={
                **os.environ,
                "PYTHONPATH": str(work / "src"),
                "PYTEST_ADDOPTS": "",
                "PYTHONDONTWRITEBYTECODE": "1",
            },
        )
        output = result.stdout + result.stderr
        valid_failure = (
            result.returncode == 1
            and re.search(r"(?m)^E\s+(?:AssertionError|assert\b)", output) is not None
            and "FAILED tests/test_properties.py" in output
            and "ERROR collecting" not in output
        )
        return {
            "name": name,
            "pytest_exit": result.returncode,
            "passed": result.returncode == 0 if filename is None else valid_failure,
            "summary": output.splitlines()[-1] if output.splitlines() else "",
        }


def main() -> int:
    results = [run_variant("baseline", None, "", "", "")]
    print(json.dumps(results[-1]), flush=True)
    if not results[0]["passed"]:
        return 1
    for mutation in MUTATIONS:
        result = run_variant(*mutation)
        results.append(result)
        print(json.dumps(result), flush=True)
    return 0 if all(result["passed"] for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
