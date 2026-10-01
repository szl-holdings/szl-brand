"""``szl-marketing`` — the marketing engine from the command line.

Exit codes: 0 clean, 1 blocked by the linter or by drift, 2 unavailable (network, token,
missing input). Nothing here writes to GitHub, Hugging Face or DNS except ``space-publish``,
which needs ``HF_TOKEN`` in the environment and records what it did in a secret-free report.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .compose import compose_all
from .facts import UNAVAILABLE, factbase, write_factbase
from .lint import lint, lint_paths
from .plan import plan_json, render_plan
from .space_package import TARGETS, build_package, publish_package

__all__ = ["main"]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def cmd_facts(args: argparse.Namespace) -> int:
    facts = factbase()
    target = write_factbase(facts, Path(args.out) / "factbase.json")
    print(json.dumps(facts, indent=2, sort_keys=True))
    print(f"\nfactbase written: {target}", file=sys.stderr)
    sections = ("github", "hf", "product", "surfaces")
    unavailable = [s for s in sections if facts[s].get("label") == UNAVAILABLE]
    if unavailable:
        print(f"UNAVAILABLE sections: {', '.join(unavailable)}", file=sys.stderr)
        return 2 if args.strict else 0
    return 0


def cmd_lint(args: argparse.Namespace) -> int:
    if args.text is not None:
        violations = lint(args.text)
        report = {"<text>": violations}
    else:
        report = lint_paths(Path(p) for p in args.paths)
    total = sum(len(v) for v in report.values())
    if args.json:
        print(
            json.dumps(
                {k: [vars(v) for v in vs] for k, vs in report.items()}, indent=2, sort_keys=True
            )
        )
    else:
        for path, violations in sorted(report.items()):
            for violation in violations:
                print(f"{path}: {violation}")
        print(f"linted {len(report)} input(s): {total} violation(s)", file=sys.stderr)
    return 1 if total else 0


def cmd_compose(args: argparse.Namespace) -> int:
    facts = _load_json(Path(args.facts)) if args.facts else factbase()
    body = Path(args.body).read_text(encoding="utf-8") if args.body else args.body_text or ""
    drafts = compose_all(
        facts,
        body,
        (args.subject_a, args.subject_b),
        canonical_url=args.canonical,
        linkedin_hook=args.hook,
    )
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    blocked = 0
    for name, draft in drafts.items():
        if draft.shippable:
            path = out / f"{name}_{facts.get('generated', 'draft')}.md"
            path.write_text(draft.text, encoding="utf-8")
            print(f"{name}: SHIPPABLE -> {path}")
        else:
            blocked += 1
            print(f"{name}: BLOCKED")
            for violation in draft.violations:
                print(f"  {violation}")
    return 1 if blocked else 0


def cmd_plan(args: argparse.Namespace) -> int:
    text = json.dumps(plan_json(), indent=2, ensure_ascii=False) if args.json else render_plan()
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"plan written: {args.out}", file=sys.stderr)
    else:
        print(text, end="")
    return 0


def cmd_space_build(args: argparse.Namespace) -> int:
    receipt = build_package(args.target, Path(args.repo_root), args.source_sha, Path(args.output))
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


def cmd_space_publish(args: argparse.Namespace) -> int:
    report = publish_package(Path(args.package), Path(args.report))
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["state"] == "PUBLISHED_CONVERGED":
        return 0
    return 2 if report["state"] == "UNAVAILABLE" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="szl-marketing", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("facts", help="pull the live labeled factbase")
    p.add_argument("--out", default="marketing-out")
    p.add_argument("--strict", action="store_true", help="exit 2 if any source is UNAVAILABLE")
    p.set_defaults(func=cmd_facts)

    p = sub.add_parser("lint", help="run the compliance linter over files, directories or text")
    p.add_argument("paths", nargs="*")
    p.add_argument("--text", help="lint this string instead of paths")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_lint)

    p = sub.add_parser("compose", help="draft every channel from a factbase; lint or block")
    p.add_argument("--facts", help="factbase.json (default: live pull)")
    p.add_argument("--body", help="markdown file with the team's essay body")
    p.add_argument("--body-text", help="essay body as a string")
    p.add_argument("--subject-a", required=True)
    p.add_argument("--subject-b", required=True)
    p.add_argument("--hook", help="LinkedIn hook (default: subject A)")
    p.add_argument("--canonical", default="https://substack.com")
    p.add_argument("--out", default="marketing-out")
    p.set_defaults(func=cmd_compose)

    p = sub.add_parser("plan", help="render the operating plan")
    p.add_argument("--json", action="store_true")
    p.add_argument("--out")
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("space-build", help="build an exact Space projection package")
    p.add_argument("--target", required=True, choices=sorted(TARGETS))
    p.add_argument("--source-sha", required=True)
    p.add_argument("--repo-root", default=".")
    p.add_argument("--output", required=True)
    p.set_defaults(func=cmd_space_build)

    p = sub.add_parser("space-publish", help="publish a built package (needs HF_TOKEN)")
    p.add_argument("--package", required=True)
    p.add_argument("--report", required=True)
    p.set_defaults(func=cmd_space_publish)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
