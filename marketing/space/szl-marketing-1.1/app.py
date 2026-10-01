"""SZL-MARKETING-1.1 — governed marketing fact factory (Hugging Face Space).

This file is an exact projection of szl-holdings/szl-brand ``marketing/space/szl-marketing-1.1``
plus a byte-for-byte vendored copy of ``szl_brand.marketing`` (``szl_marketing/``). The source
revision and per-file hashes are in ``PUBLICATION_RECEIPT.json``. Edit the GitHub source, not
this Space.
"""

from __future__ import annotations

import json
from pathlib import Path

import gradio as gr

from szl_marketing import (
    UNAVAILABLE,
    compose_all,
    fact,
    factbase,
    lint,
    render_plan,
)

RECEIPT = Path(__file__).with_name("PUBLICATION_RECEIPT.json")


def _receipt() -> dict:
    try:
        return json.loads(RECEIPT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def measure() -> tuple[str, str]:
    facts = factbase()
    rows = [
        ("GitHub public repositories", fact(facts, "github.repos"), fact(facts, "github.label")),
        ("GitHub archived (honestly)", fact(facts, "github.archived"), fact(facts, "github.label")),
        ("HF models", fact(facts, "hf.models"), fact(facts, "hf.label")),
        ("HF datasets", fact(facts, "hf.datasets"), fact(facts, "hf.label")),
        ("HF Spaces", fact(facts, "hf.spaces"), fact(facts, "hf.label")),
        ("Crown artifact (models+datasets sweep)", fact(facts, "hf.crown.id"), fact(facts, "hf.label")),
        ("Crown downloads", fact(facts, "hf.crown.downloads"), fact(facts, "hf.label")),
        ("Estate downloads", fact(facts, "hf.downloads.total"), fact(facts, "hf.label")),
        ("Locked formulas (honesty manifest)", fact(facts, "product.locked_formula_count"), fact(facts, "product.label")),
        ("Λ status", fact(facts, "product.lambda"), fact(facts, "product.label")),
        ("Verify door a-11-oy.com/verify", fact(facts, "surfaces.verify_cta"), fact(facts, "surfaces.label")),
        ("Proof registry a11oy.net", fact(facts, "surfaces.proof_cta"), fact(facts, "surfaces.label")),
    ]
    md = [f"## The estate, measured at {facts['generated_at']}", "", "| Metric | Value | Label |", "|---|---|---|"]
    for name, value, label in rows:
        shown = f"{value:,}" if isinstance(value, int) else str(value)
        md.append(f"| {name} | {shown} | {label} |")
    md.append("")
    md.append("Anonymous pulls: these are the numbers a stranger sees. UNAVAILABLE means the source did not answer; nothing is estimated.")
    return "\n".join(md), json.dumps(facts, indent=2, sort_keys=True)


def compose(subject_a: str, subject_b: str, body: str) -> tuple[str, str, str]:
    if not subject_a.strip() or not subject_b.strip() or subject_a.strip() == subject_b.strip():
        return "", "", "BLOCKED - give two distinct subject lines for the A/B test."
    facts = factbase()
    try:
        drafts = compose_all(facts, body or "", (subject_a, subject_b))
    except ValueError as exc:
        return "", "", f"BLOCKED - {exc}"
    verdict = []
    for name, draft in drafts.items():
        if draft.shippable:
            verdict.append(f"- {name}: SHIPPABLE")
        else:
            verdict.append(f"- {name}: BLOCKED")
            verdict.extend(f"  - {v}" for v in draft.violations)
    return drafts["substack"].text, drafts["x"].text, "\n".join(verdict)


def lint_copy(text: str) -> str:
    violations = lint(text or "")
    if not violations:
        return "CLEAN - this copy passes the guardrails."
    return "BLOCKED - fix these before it ships:\n\n" + "\n".join(f"- {v}" for v in violations)


def about() -> str:
    receipt = _receipt()
    sha = receipt.get("source", {}).get("sha", UNAVAILABLE)
    root = receipt.get("root_sha256", UNAVAILABLE)
    return (
        "## Provenance\n\n"
        f"- Source: https://github.com/szl-holdings/szl-brand @ `{sha}`\n"
        f"- Package root SHA-256: `{root}`\n"
        "- Discipline: labels stay; trust ceiling 0.97, never 1.0; Λ stays Conjecture 1, "
        "advisory; a draft with one linter violation does not ship.\n"
    )


with gr.Blocks(title="SZL-MARKETING-1.1 — Governed Fact Factory") as demo:
    gr.Markdown(
        "# SZL-MARKETING-1.1\n"
        "**A marketing pipeline that cannot type a number.** Facts are pulled live and labeled; "
        "a machine linter enforces the house guardrails before any draft exists.\n"
    )
    with gr.Tab("Live facts"):
        measure_btn = gr.Button("Measure the estate (live, anonymous API pull)")
        facts_md = gr.Markdown()
        facts_json = gr.Code(language="json", label="factbase.json")
        measure_btn.click(measure, outputs=[facts_md, facts_json])
    with gr.Tab("Compose + lint"):
        subject_a = gr.Textbox(label="Subject line A", value="Receipts, not vibes")
        subject_b = gr.Textbox(label="Subject line B", value="The honest label")
        body = gr.Textbox(label="Essay body (the team's voice)", lines=8)
        compose_btn = gr.Button("Compose every channel from live facts")
        substack_out = gr.Markdown(label="Substack draft")
        x_out = gr.Markdown(label="X thread")
        verdict_out = gr.Markdown(label="Linter verdict")
        compose_btn.click(compose, inputs=[subject_a, subject_b, body], outputs=[substack_out, x_out, verdict_out])
    with gr.Tab("Lint your own copy"):
        copy_in = gr.Textbox(label="Paste a draft", lines=10)
        lint_btn = gr.Button("Run guardrails")
        lint_out = gr.Markdown()
        lint_btn.click(lint_copy, inputs=copy_in, outputs=lint_out)
    with gr.Tab("Operating plan"):
        gr.Markdown(render_plan())
    with gr.Tab("Provenance"):
        gr.Markdown(about())

if __name__ == "__main__":
    demo.launch()
