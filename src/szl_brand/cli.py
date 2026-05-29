"""SZL Brand CLI — command center for brand asset generation and governance.

Usage:
    python -m szl_brand generate        Generate all social previews
    python -m szl_brand generate-one    Generate a single preview
    python -m szl_brand validate        Validate all brand assets
    python -m szl_brand manifest        Generate integrity manifest
    python -m szl_brand inventory       Show asset inventory
    python -m szl_brand serve           Start live preview gallery
    python -m szl_brand drift           Check manifest drift
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from szl_brand import __version__

BANNER = f"""\033[38;5;141m
  ███████╗ ███████╗ ██╗
  ██╔════╝ ╚══███╔╝ ██║
  ███████╗   ███╔╝  ██║
  ╚════██║  ███╔╝   ██║
  ███████║ ███████╗ ███████╗
  ╚══════╝ ╚══════╝ ╚══════╝\033[0m
  \033[2mszl-brand v{__version__} — Deterministic Brand SDK\033[0m
"""


def cmd_generate(args: argparse.Namespace) -> int:
    """Generate all registered social previews."""
    from szl_brand.preview import generate_all

    output = Path(args.output)
    print(BANNER)
    print(f"  \033[1mGenerating social previews → {output}\033[0m\n")

    start = time.time()
    paths = generate_all(output)
    elapsed = time.time() - start

    for p in paths:
        size_kb = p.stat().st_size / 1024
        print(f"  \033[32m✓\033[0m {p.name:30s} {size_kb:6.1f} KB")

    print(f"\n  \033[1m{len(paths)} banners\033[0m generated in \033[1m{elapsed:.2f}s\033[0m")
    return 0


def cmd_generate_one(args: argparse.Namespace) -> int:
    """Generate a single social preview."""
    from szl_brand.preview import PreviewSpec, StatCard, generate_preview

    output = Path(args.output)
    stats = []
    if args.stats:
        for pair in args.stats:
            parts = pair.split(":", 1)
            if len(parts) == 2:
                stats.append(StatCard(value=parts[0], label=parts[1]))

    spec = PreviewSpec(
        repo=args.repo,
        kicker=args.kicker or args.repo.upper(),
        title=args.title,
        subtitle=args.subtitle,
        tag=args.tag or "CUSTOM",
        stats=stats,
    )

    print(BANNER)
    print(f"  \033[1mGenerating preview for '{args.repo}'\033[0m\n")

    start = time.time()
    result = generate_preview(spec, output)
    elapsed = time.time() - start

    size_kb = result.stat().st_size / 1024
    print(f"  \033[32m✓\033[0m {result} ({size_kb:.1f} KB, {elapsed:.2f}s)")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate all brand assets."""
    from szl_brand.validate import validate_directory

    directory = Path(args.directory)
    print(BANNER)
    print(f"  \033[1mValidating assets in {directory}\033[0m\n")

    if not directory.exists():
        print(f"  \033[31m✗\033[0m Directory not found: {directory}")
        return 1

    records = validate_directory(directory)
    passed = sum(1 for r in records if r.validated)
    failed = sum(1 for r in records if not r.validated)

    for r in records:
        status = "\033[32m✓\033[0m" if r.validated else "\033[31m✗\033[0m"
        name = Path(r.path).name
        dims = f"{r.width}×{r.height}" if r.width else "—"
        print(f"  {status} {name:35s} {dims:12s} {r.size_bytes:>8,} B  {r.sha256[:12]}")
        for err in r.errors:
            print(f"      \033[31m└─ {err}\033[0m")

    print(f"\n  \033[1m{passed} passed\033[0m, ", end="")
    if failed:
        print(f"\033[31m{failed} failed\033[0m")
        return 1
    print("0 failed")
    return 0


def cmd_manifest(args: argparse.Namespace) -> int:
    """Generate cryptographic integrity manifest."""
    from szl_brand.validate import generate_manifest

    directory = Path(args.directory)
    output = Path(args.output)
    print(BANNER)
    print(f"  \033[1mGenerating manifest for {directory}\033[0m\n")

    if not directory.exists():
        print(f"  \033[31m✗\033[0m Directory not found: {directory}")
        return 1

    manifest = generate_manifest(directory)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(manifest.to_json())

    print(f"  \033[32m✓\033[0m {len(manifest.assets)} assets indexed")
    print(f"  \033[32m✓\033[0m Root hash: {manifest.root_hash[:16]}…")
    print(f"  \033[32m✓\033[0m Written to: {output}")
    return 0


def cmd_inventory(args: argparse.Namespace) -> int:
    """Show asset inventory with statistics."""
    from szl_brand.validate import validate_directory

    directory = Path(args.directory)
    print(BANNER)
    print(f"  \033[1mAsset Inventory — {directory}\033[0m\n")

    if not directory.exists():
        print(f"  \033[31m✗\033[0m Directory not found: {directory}")
        return 1

    records = validate_directory(directory)
    if not records:
        print("  No assets found.")
        return 0

    total_size = sum(r.size_bytes for r in records)
    by_format: dict[str, int] = {}
    for r in records:
        by_format[r.format] = by_format.get(r.format, 0) + 1

    print(f"  {'Format':<10} {'Count':>6}")
    print(f"  {'─' * 10} {'─' * 6}")
    for fmt, count in sorted(by_format.items()):
        print(f"  {fmt:<10} {count:>6}")
    print(f"  {'─' * 10} {'─' * 6}")
    print(f"  {'Total':<10} {len(records):>6}")
    print(f"\n  Total size: {total_size / 1024:.1f} KB ({total_size:,} bytes)")
    return 0


def cmd_drift(args: argparse.Namespace) -> int:
    """Check for drift between manifest and filesystem."""
    from szl_brand.validate import check_drift

    manifest_path = Path(args.manifest)
    directory = Path(args.directory)
    print(BANNER)
    print("  \033[1mDrift Detection\033[0m\n")

    drifts = check_drift(manifest_path, directory)
    if not drifts:
        print("  \033[32m✓\033[0m No drift detected — all assets match manifest.")
        return 0

    for d in drifts:
        if d["type"] == "error":
            print(f"  \033[31m✗\033[0m {d['message']}")
        elif d["type"] == "added":
            print(f"  \033[33m+\033[0m {Path(d['path']).name} (new, not in manifest)")
        elif d["type"] == "removed":
            print(f"  \033[31m-\033[0m {Path(d['path']).name} (missing from filesystem)")
        elif d["type"] == "modified":
            print(f"  \033[33m~\033[0m {Path(d['path']).name} (content changed)")

    print(f"\n  \033[33m{len(drifts)} drift(s) detected\033[0m")
    return 1


def cmd_serve(args: argparse.Namespace) -> int:
    """Start the live asset gallery server."""
    from szl_brand.server import serve

    dirs = [Path(d) for d in args.dirs] if args.dirs else None
    print(BANNER)
    serve(port=args.port, asset_dirs=dirs)
    return 0


def app() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="szl-brand",
        description="SZL Holdings Brand SDK — Deterministic asset generation & governance",
    )
    parser.add_argument("--version", action="version", version=f"szl-brand {__version__}")
    sub = parser.add_subparsers(dest="command")

    p_gen = sub.add_parser("generate", help="Generate all social previews")
    p_gen.add_argument("-o", "--output", default="social-previews", help="Output directory")

    p_one = sub.add_parser("generate-one", help="Generate a single preview")
    p_one.add_argument(
        "--repo", required=True, help="Repository name (seed for procedural generation)"
    )
    p_one.add_argument("--title", required=True, help="Banner title")
    p_one.add_argument("--subtitle", required=True, help="Banner subtitle")
    p_one.add_argument("--kicker", help="Kicker text (default: repo name uppercase)")
    p_one.add_argument("--tag", help="Tag pill text")
    p_one.add_argument("--stats", nargs="*", help="Stats as value:label pairs")
    p_one.add_argument("-o", "--output", required=True, help="Output PNG path")

    p_val = sub.add_parser("validate", help="Validate brand assets")
    p_val.add_argument(
        "directory", nargs="?", default="social-previews", help="Directory to validate"
    )

    p_man = sub.add_parser("manifest", help="Generate integrity manifest")
    p_man.add_argument("directory", nargs="?", default="social-previews", help="Directory to index")
    p_man.add_argument("-o", "--output", default="brand-manifest.json", help="Output manifest path")

    p_inv = sub.add_parser("inventory", help="Show asset inventory")
    p_inv.add_argument("directory", nargs="?", default="social-previews", help="Directory to scan")

    p_drift = sub.add_parser("drift", help="Check manifest drift")
    p_drift.add_argument("--manifest", default="brand-manifest.json", help="Manifest file path")
    p_drift.add_argument(
        "directory", nargs="?", default="social-previews", help="Directory to check"
    )

    p_serve = sub.add_parser("serve", help="Start live asset gallery")
    p_serve.add_argument("-p", "--port", type=int, default=8742, help="Server port")
    p_serve.add_argument("--dirs", nargs="*", help="Directories to serve")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    handlers = {
        "generate": cmd_generate,
        "generate-one": cmd_generate_one,
        "validate": cmd_validate,
        "manifest": cmd_manifest,
        "inventory": cmd_inventory,
        "drift": cmd_drift,
        "serve": cmd_serve,
    }

    sys.exit(handlers[args.command](args))
