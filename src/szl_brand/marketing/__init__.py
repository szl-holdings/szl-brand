"""SZL marketing engine: live labeled facts, a compliance linter, channel drafts, the plan.

Doctrine in one line: a draft ships only when every number maps to a fetched fact (or is
printed as UNAVAILABLE) and the linter returns no violation. This package is stdlib-only so
it can be vendored byte-for-byte into the public Space (see ``space_package``).
"""

from __future__ import annotations

from .compose import (
    Draft,
    compose_all,
    fact_block,
    linkedin_draft,
    medium_draft,
    substack_draft,
    verification_links,
    x_thread,
)
from .facts import (
    MEASURED,
    UNAVAILABLE,
    default_fetch,
    fact,
    factbase,
    github_facts,
    hf_facts,
    product_facts,
    surface_facts,
    write_factbase,
)
from .lint import RULES, Rule, Violation, lint, lint_paths, lint_text_files, strip_html
from .plan import (
    AUDIENCES,
    BACKLOG,
    CALENDAR,
    GUARDRAILS,
    INVESTOR_MACHINE,
    KPIS,
    UPGRADES,
    VISION,
    plan_json,
    plan_text,
    render_plan,
)

__all__ = [
    "AUDIENCES",
    "BACKLOG",
    "CALENDAR",
    "GUARDRAILS",
    "INVESTOR_MACHINE",
    "KPIS",
    "MEASURED",
    "RULES",
    "UNAVAILABLE",
    "UPGRADES",
    "VISION",
    "Draft",
    "Rule",
    "Violation",
    "compose_all",
    "default_fetch",
    "fact",
    "fact_block",
    "factbase",
    "github_facts",
    "hf_facts",
    "linkedin_draft",
    "lint",
    "lint_paths",
    "lint_text_files",
    "medium_draft",
    "plan_json",
    "plan_text",
    "product_facts",
    "render_plan",
    "strip_html",
    "substack_draft",
    "surface_facts",
    "verification_links",
    "write_factbase",
    "x_thread",
]
