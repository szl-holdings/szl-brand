"""The marketing operating plan as data: guardrails, calendar, backlog, KPIs, investor loop.

Everything here is text the team edits under creative control. It is kept as structured data
so the Space, the CLI and the payload render the same plan, and so the compliance linter can
be run over every sentence of it in CI.
"""

from __future__ import annotations

import json
from typing import Any, Final

__all__ = [
    "AUDIENCES",
    "BACKLOG",
    "CALENDAR",
    "GUARDRAILS",
    "INVESTOR_MACHINE",
    "KPIS",
    "UPGRADES",
    "VISION",
    "plan_json",
    "plan_text",
    "render_plan",
]

VISION: Final = (
    "SZL Holdings builds governed AI you can verify, not AI you are asked to trust. Every "
    "claim carries an honesty label (MEASURED / REPORTED / ROADMAP / UNAVAILABLE). Every "
    "governed action writes a hash-chained receipt anyone can check offline. The trust ceiling "
    "is 0.97, never 1.0: the company would rather show a truthful BLOCKED than a confident "
    "lie. That refusal is the product, the moat, and the brand."
)

GUARDRAILS: Final[tuple[str, ...]] = (
    "Never quantify killinchu capabilities. Describe the receipt architecture, never detection "
    "ranges, sensor specifics, or deployment details. When in doubt: link the public repo, "
    "describe the governance layer, stop.",
    "szl-quant is advisory-only and paper-only. Any mention carries 'not financial advice'. "
    "Never show returns, never imply performance.",
    "Investor communications describe what exists and what is labeled ROADMAP. Never forecast "
    "revenue, users, or valuation in public content. a11oy.net is the safe harbor: link it "
    "instead of restating it.",
    "Λ discipline: the words 'proven', 'guaranteed' and 'verified trust' about Λ are banned. "
    "Correct form: 'Λ, Conjecture 1, advisory'.",
    "The label rule: every factual claim maps to a factbase key or carries UNAVAILABLE. If the "
    "fact cannot be fetched, the sentence does not ship.",
)

AUDIENCES: Final[tuple[dict[str, str], ...]] = (
    {
        "audience": "AI-safety buyer",
        "pain": "cannot audit what the AI did",
        "message": "every action leaves a receipt you can verify offline",
    },
    {
        "audience": "Developer",
        "pain": "trust theater in AI tooling",
        "message": "open receipt spec, public repos and a Lean kernel: go read it",
    },
    {
        "audience": "Investor",
        "pain": "AI claims are unauditable",
        "message": "our CI machine-bans our own overclaims; the discipline is the moat",
    },
    {
        "audience": "Defense and sovereignty",
        "pain": "air-gapped AI accountability",
        "message": "killinchu, UDS air-gap packaging and SLSA-labeled receipts",
    },
)

CALENDAR: Final[tuple[dict[str, str], ...]] = (
    {
        "week": "1",
        "substack": "Launch essay: Receipts, Not Vibes (thesis)",
        "medium": "—",
        "x": "Account live; pin the verify post",
        "other": "Email capture form on a-11-oy.com, Substack-connected",
    },
    {
        "week": "2",
        "substack": "Watch our AI refuse, and why that is the feature",
        "medium": "—",
        "x": "Proof thread 1: a BLOCKED receipt, walked end to end",
        "other": "Record the refusal demo video (15 s / 30 s / 90 s cuts)",
    },
    {
        "week": "3",
        "substack": "The 0.97 ceiling: we capped our own trust",
        "medium": "Republish week 1 (canonical link to Substack)",
        "x": "Proof thread 2; engage the Lean and formal-methods community",
        "other": "Investor one-pager v1 that links a11oy.net diligence paths",
    },
    {
        "week": "4",
        "substack": "What the public repositories of governed AI actually do",
        "medium": "Republish week 2",
        "x": "Proof thread 3 plus the demo clip",
        "other": "Metrics review; seed the month-2 backlog",
    },
)

BACKLOG: Final[tuple[str, ...]] = (
    "The refusal demo (video-first): a governed action returns BLOCKED with the receipt chain "
    "visible, verified in a second browser.",
    "The 0.97 ceiling: the founder story of capping our own trust.",
    "Khipu, the original receipt: Andean knotted-cord records to hash chains.",
    "We archived our own duplicate repositories and told you why (the hologram honesty story).",
    "The locked Lean kernel for non-mathematicians.",
    "killinchu-osint-corpus: the dataset that out-pulled every model in the estate.",
    "Doctrine v11: the CI that blocks you for overclaiming.",
    "UNAVAILABLE as a design philosophy: make the honest 'no' iconic.",
    "The two-domain architecture: product (a-11-oy.com) versus proof (a11oy.net).",
    "A receipt verification, live, every step screenshotted.",
    "Conjecture 1, and proud of it: the anti-hype theorem essay.",
    "The GovernedAction/v1 open spec: give the format away, sell the control plane.",
)

KPIS: Final[dict[str, tuple[str, ...]]] = {
    "primary": (
        "Substack subscribers",
        "Click-through to the verify door (a-11-oy.com/verify)",
        "Refusal-demo video completion rate",
    ),
    "secondary": (
        "Medium reads",
        "X engagement inside technical threads",
        "GitHub stars delta on the spec and kernel repositories",
    ),
    "investor": (
        "One-pager opens",
        "Diligence-path starts from a11oy.net",
        "Which proof asset moved each conversation (logged per call)",
    ),
    "anti_metric": (
        "Growth attributable to hype language counts as a failure even when the numbers rise; "
        "the doctrine is the only thing competitors cannot copy.",
    ),
}

INVESTOR_MACHINE: Final[dict[str, Any]] = {
    "cadence": "monthly",
    "audiences": (
        "defense-tech funds",
        "AI-safety funds",
        "formal-methods investors",
        "sovereign-AI and air-gap infrastructure investors",
    ),
    "asset": "a one-pager that links the a11oy.net diligence paths and never restates claims",
    "hook": "our CI machine-bans our own overclaims; ask us to show you",
    "demo": "a live receipt verification during every pitch",
    "tracking": "every conversation logged with the proof asset that moved it",
    "escalation": "any metric flat for four weeks authorizes a creative pivot",
    "hard_floor": "the doctrine never pivots: labels stay, Λ stays Conjecture 1",
}

UPGRADES: Final[tuple[str, ...]] = (
    "The refusal demo is the number-one asset; produce it in week 1 and cut it three ways.",
    "Email capture before anything else: one Substack-connected form, live on day one.",
    "Make UNAVAILABLE iconic with a four-tier label color system across every channel.",
    "The khipu story is the brand mythology: a company named after receipts in two languages.",
    "GitHub stars are investor social proof; the Medium funnel always ends at a repository.",
    "A recurring 'Denied by our own CI' screenshot series: inexhaustible, funny, and the moat "
    "on display.",
    "Never build an investor PDF; a11oy.net already is the dated, checkable diligence path.",
    "One anti-metric protects the brand: hype-driven growth is a failure even if numbers rise.",
)


def plan_json() -> dict[str, Any]:
    return {
        "schema": "szl.marketing-plan/v1",
        "vision": VISION,
        "guardrails": list(GUARDRAILS),
        "audiences": list(AUDIENCES),
        "calendar": list(CALENDAR),
        "backlog": list(BACKLOG),
        "kpis": {key: list(value) for key, value in KPIS.items()},
        "investor_machine": {
            key: (list(value) if isinstance(value, tuple) else value)
            for key, value in INVESTOR_MACHINE.items()
        },
        "upgrades": list(UPGRADES),
    }


def render_plan() -> str:
    """Markdown rendering shared by the CLI, the payload and the Space."""
    out: list[str] = ["# SZL marketing operating plan", "", VISION, "", "## Guardrails", ""]
    out += [f"{i}. {rule}" for i, rule in enumerate(GUARDRAILS, 1)]
    out += ["", "## Audiences", "", "| Audience | Pain | Message |", "|---|---|---|"]
    out += [f"| {a['audience']} | {a['pain']} | {a['message']} |" for a in AUDIENCES]
    out += ["", "## 30-day launch calendar", "", "| Week | Substack | Medium | X | Other |"]
    out += ["|---|---|---|---|---|"]
    out += [
        f"| {w['week']} | {w['substack']} | {w['medium']} | {w['x']} | {w['other']} |"
        for w in CALENDAR
    ]
    out += ["", "## Story backlog (ranked)", ""]
    out += [f"{i}. {story}" for i, story in enumerate(BACKLOG, 1)]
    out += ["", "## KPIs", ""]
    for key, items in KPIS.items():
        out.append(f"- {key.replace('_', ' ')}: " + "; ".join(items))
    out += ["", "## Investor machine", ""]
    for key, value in INVESTOR_MACHINE.items():
        rendered = ", ".join(value) if isinstance(value, tuple) else str(value)
        out.append(f"- {key.replace('_', ' ')}: {rendered}")
    out += ["", "## Upgrades", ""]
    out += [f"{i}. {item}" for i, item in enumerate(UPGRADES, 1)]
    return "\n".join(out) + "\n"


def plan_text() -> str:
    """All plan prose as one string, for linting."""
    return json.dumps(plan_json(), ensure_ascii=False, indent=1)
