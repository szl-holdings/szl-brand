"""Stage the actual fixed Space package and serve it with synthetic callbacks.

Only this qualification process replaces factbase(). Python DNS and connect
calls are restricted to loopback before importing the app. Nothing is published.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from szl_brand.marketing.space_package import build_package  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535 or not args.out.is_dir() or args.out.is_symlink():
        raise ValueError("a private existing output directory and unprivileged port are required")
    source = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    package = args.out / "package"
    if package.exists() or package.is_symlink():
        raise ValueError("fixture package path already exists")
    receipt = build_package("szl-marketing-1.1", ROOT, source, package)
    original_connect = socket.socket.connect
    original_connect_ex = socket.socket.connect_ex
    original_dns = socket.getaddrinfo
    loopback = {"127.0.0.1", "::1", "localhost", None}

    def denied() -> None:
        print("FIXTURE_REMOTE_DENIED", flush=True)

    def connect(self, address):
        if isinstance(address, tuple) and address[0] not in loopback:
            denied()
            raise OSError("qualification permits only loopback transport")
        return original_connect(self, address)

    def connect_ex(self, address):
        if isinstance(address, tuple) and address[0] not in loopback:
            denied()
            return 101
        return original_connect_ex(self, address)

    def getaddrinfo(host, *rest, **kwargs):
        if host not in loopback:
            denied()
            raise OSError("qualification permits only loopback DNS")
        return original_dns(host, *rest, **kwargs)

    socket.socket.connect = connect
    socket.socket.connect_ex = connect_ex
    socket.getaddrinfo = getaddrinfo
    sys.path.insert(0, str(package))
    spec = importlib.util.spec_from_file_location("factory_app", package / "app.py")
    app = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app)
    good = {
        "schema": "szl.marketing-factbase/v1",
        "generated_at": "2026-10-11T12:00:00Z",
        "generated": "2026-10-11",
        "test_fixture": True,
        "github": {"label": "MEASURED", "repos": 12, "archived": 2},
        "hf": {
            "label": "MEASURED",
            "models": 5,
            "datasets": 3,
            "spaces": 4,
            "downloads": {"total": 1200},
            "crown": {"id": "SZLHOLDINGS/fixture-data", "downloads": 800, "kind": "datasets"},
        },
        "product": {
            "label": "MEASURED",
            "locked_formula_count": 6,
            "lambda": "Conjecture 1, advisory",
        },
        "surfaces": {"label": "MEASURED", "verify_cta": "AVAILABLE", "proof_cta": "UNAVAILABLE"},
    }
    partial = {"github": {"label": "MEASURED", "repos": 0}, "hf": {"label": "UNAVAILABLE"}}
    hostile = {
        "generated_at": "invalid date",
        "hf": {
            "label": "MEASURED",
            "crown": {
                "id": '<img src="https://invalid.example/probe" onerror="window.injected=1">'
            },
        },
        "product": {"label": {"invalid": "shape"}},
    }
    calls = 0

    def fixture_facts():
        nonlocal calls
        calls += 1
        print(f"FIXTURE_FACTBASE_CALL:{calls}", flush=True)
        return copy.deepcopy([good, partial, hostile, None][calls - 1] if calls <= 4 else good)

    app.factbase = fixture_facts
    _, address, _ = app.launch(
        server_name="127.0.0.1",
        server_port=args.port,
        quiet=True,
        prevent_thread_lock=True,
        ssr_mode=False,
    )
    print(
        "FIXTURE_READY:"
        + json.dumps(
            {
                "source": source,
                "url": address,
                "package_root_sha256": receipt["root_sha256"],
                "file_count": len(receipt["files"]),
                "gradio": app.gr.__version__,
                "classification": "UNSIGNED_LOCAL_RENDERED_FIXTURE",
            }
        ),
        flush=True,
    )
    try:
        app.demo.block_thread()
    finally:
        app.demo.close()


if __name__ == "__main__":
    main()
