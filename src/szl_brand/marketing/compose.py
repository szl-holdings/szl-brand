"""Channel drafts assembled from a labeled factbase and linted before they exist.

The team owns the essay. The fact block, the labels, the A/B subject lines and the CTA are
machine-written from the factbase so a draft can never carry a typed number. Every draft is
linted on construction; a draft with violations reports them and is not shippable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final

from .facts import UNAVAILABLE, fact
from .lint import Violation, lint

__all__ = [
    "X_LIMIT",
    "Draft",
    "compose_all",
    "fact_block",
    "linkedin_draft",
    "medium_draft",
    "substack_draft",
    "verification_links",
    "x_thread",
]

X_LIMIT: Final = 280
PRODUCT_VERIFY: Final = "https://a-11-oy.com/verify"
PROOF_REGISTRY: Final = "https://a11oy.net"


@dataclass(frozen=True)
class Draft:
    channel: str
    title: str
    text: str
    subject_a: str | None = None
    subject_b: str | None = None
    violations: list[Violation] = field(default_factory=list)

    @property
    def shippable(self) -> bool:
        return not self.violations


def _num(value: Any) -> str:
    return f"{value:,}" if isinstance(value, int) else str(UNAVAILABLE)


def verification_links(facts: dict[str, Any]) -> list[str]:
    """Only doors that answered 200 at generation time are offered to the reader."""
    links: list[str] = []
    if fact(facts, "surfaces.verify_cta") == "AVAILABLE":
        links.append(f"Verify a receipt yourself: {PRODUCT_VERIFY}")
    if fact(facts, "surfaces.proof_cta") == "AVAILABLE":
        links.append(f"Proof registry: {PROOF_REGISTRY}")
    return links


def fact_block(facts: dict[str, Any]) -> str:
    """The labeled estate block every long-form draft opens with."""
    generated = fact(facts, "generated_at")
    gh_label = fact(facts, "github.label")
    hf_label = fact(facts, "hf.label")
    crown_id = fact(facts, "hf.crown.id")
    crown_dl = fact(facts, "hf.crown.downloads")
    crown_kind = fact(facts, "hf.crown.kind")
    kind_word = {"models": "model", "datasets": "dataset"}.get(crown_kind, UNAVAILABLE)
    locked = fact(facts, "product.locked_formula_count")
    lam = fact(facts, "product.lambda")
    gh_line = (
        f"- GitHub: {_num(fact(facts, 'github.repos'))} public repositories, "
        f"{_num(fact(facts, 'github.archived'))} honestly archived [{gh_label}]"
    )
    hf_line = (
        f"- Hugging Face: {_num(fact(facts, 'hf.models'))} models, "
        f"{_num(fact(facts, 'hf.datasets'))} datasets, {_num(fact(facts, 'hf.spaces'))} Spaces "
        f"[{hf_label}]"
    )
    crown_line = (
        f"- Most-downloaded public artifact: {crown_id} ({_num(crown_dl)} downloads; "
        f"a {kind_word}, swept across models and datasets) [{hf_label}]"
    )
    downloads_line = f"- Estate downloads: {_num(fact(facts, 'hf.downloads.total'))} [{hf_label}]"
    product_line = (
        f"- Locked formulas in the product's honesty manifest: {_num(locked)}; "
        f"Λ status: {lam} [{fact(facts, 'product.label')}]"
    )
    footer = (
        "Every number above was fetched from a public API at generation time. "
        "A source that did not answer is printed as UNAVAILABLE, not estimated."
    )
    lines = [
        f"## The estate, measured (fetched {generated})",
        "",
        gh_line,
        hf_line,
        crown_line,
        downloads_line,
        product_line,
        "",
        footer,
    ]
    return "\n".join(lines)


def _tail(facts: dict[str, Any]) -> str:
    links = verification_links(facts)
    if not links:
        return "\n\n---\n\nVerification links: UNAVAILABLE at generation time (not printed).\n"
    return "\n\n---\n\n" + "  ·  ".join(links) + "\n"


def substack_draft(
    facts: dict[str, Any], essay_body: str, subjects: tuple[str, str] | list[str]
) -> Draft:
    """Weekly essay skeleton with two real subject lines for an A/B test."""
    if len(subjects) < 2 or subjects[0].strip() == subjects[1].strip():
        raise ValueError("A/B needs two distinct subject lines")
    subject_a, subject_b = subjects[0].strip(), subjects[1].strip()
    text = (
        f"<!-- SUBJECT A: {subject_a} -->\n<!-- SUBJECT B: {subject_b} -->\n"
        f"# {subject_a}\n\n{fact_block(facts)}\n\n{essay_body.strip()}{_tail(facts)}"
    )
    return Draft("substack", subject_a, text, subject_a, subject_b, lint(text))


def medium_draft(facts: dict[str, Any], title: str, essay_body: str, canonical_url: str) -> Draft:
    """Republish skeleton: canonical link back to Substack, same fact block, same tail."""
    text = (
        f"# {title.strip()}\n\n"
        f"*Originally published on Substack; canonical: {canonical_url}*\n\n"
        f"{fact_block(facts)}\n\n{essay_body.strip()}{_tail(facts)}"
    )
    return Draft("medium", title.strip(), text, violations=lint(text))


def linkedin_draft(facts: dict[str, Any], hook: str, essay_body: str) -> Draft:
    """Short-form professional post: hook, three labeled facts, one door."""
    links = verification_links(facts)
    door = links[0] if links else "Verification links: UNAVAILABLE at generation time."
    text = (
        f"{hook.strip()}\n\n{essay_body.strip()}\n\n"
        f"Measured {fact(facts, 'generated')}: {_num(fact(facts, 'hf.models'))} models, "
        f"{_num(fact(facts, 'hf.datasets'))} datasets, "
        f"{_num(fact(facts, 'github.repos'))} public repositories "
        f"[{fact(facts, 'hf.label')}].\n\n{door}"
    )
    return Draft("linkedin", hook.strip()[:80], text, violations=lint(text))


def x_thread(facts: dict[str, Any]) -> Draft:
    """Proof-thread skeleton. Every post is checked against the 280-character limit."""
    crown_id = fact(facts, "hf.crown.id")
    crown_dl = _num(fact(facts, "hf.crown.downloads"))
    posts = [
        f"We publish {_num(fact(facts, 'hf.models'))} models and "
        f"{_num(fact(facts, 'hf.datasets'))} datasets. The loaded ones are labeled SOFTWARE; "
        "the empty ones are labeled ROADMAP. The label is the product.",
        f"Our most-downloaded public artifact is a dataset, not a model: {crown_id} "
        f"({crown_dl} downloads, swept across models and datasets, {fact(facts, 'generated')}).",
        f"Locked formulas in the honesty manifest: {_num(fact(facts, 'product.locked_formula_count'))}. "
        f"Λ stays {fact(facts, 'product.lambda')}. Trust ceiling 0.97, never 1.0.",
    ]
    links = verification_links(facts)
    posts.append(
        ("Verify this thread the way you would verify our AI. " + " ".join(links))
        if links
        else "Verification links were UNAVAILABLE when this thread was generated; not printed."
    )
    for post in posts:
        if len(post) > X_LIMIT:
            raise ValueError(f"post exceeds {X_LIMIT} characters: {post[:60]}...")
    text = "\n\n---\n\n".join(posts)
    return Draft("x", posts[0][:80], text, violations=lint(text))


def compose_all(
    facts: dict[str, Any],
    essay_body: str,
    subjects: tuple[str, str] | list[str],
    canonical_url: str = "https://substack.com",
    linkedin_hook: str | None = None,
) -> dict[str, Draft]:
    """One call, every channel. Callers must check ``shippable`` before writing anything."""
    drafts = {
        "substack": substack_draft(facts, essay_body, subjects),
        "medium": medium_draft(facts, subjects[0], essay_body, canonical_url),
        "x": x_thread(facts),
        "linkedin": linkedin_draft(facts, linkedin_hook or subjects[0], essay_body),
    }
    return drafts
