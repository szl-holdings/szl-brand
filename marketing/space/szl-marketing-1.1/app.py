"""Source-owned Gradio presentation for the governed marketing fact factory.

The package writer supplies the byte-exact vendored engine and native assets.
Provider reads occur only in the two explicit fact/compose callbacks. This app
does not publish drafts or reinterpret the engine's evidence labels.
"""

from __future__ import annotations

import json

import gradio as gr
from native_presentation import (
    footer,
    header,
    initial_observation,
    native_head,
    native_js,
    observation,
    provenance,
)
from szl_marketing import compose_all, factbase, lint, render_plan


def measure() -> tuple[str, str]:
    """Return an escaped presentation and the original engine JSON."""
    try:
        facts = factbase()
        if not isinstance(facts, dict):
            raise ValueError("factbase must be an object")
        raw = json.dumps(facts, indent=2, sort_keys=True, allow_nan=False)
    except (OSError, TypeError, ValueError, TimeoutError):
        return observation({}), json.dumps(
            {"label": "UNAVAILABLE", "reason": "fact collection failed"}
        )
    return observation(facts), raw


def compose(subject_a: str, subject_b: str, body: str) -> tuple[str, str, str]:
    if not subject_a.strip() or not subject_b.strip() or subject_a.strip() == subject_b.strip():
        return "", "", "BLOCKED - give two distinct subject lines for the A/B test."
    try:
        facts = factbase()
        if not isinstance(facts, dict):
            raise ValueError("fact collection unavailable")
        drafts = compose_all(facts, body or "", (subject_a, subject_b))
    except (OSError, TypeError, ValueError, TimeoutError):
        return (
            "",
            "",
            (
                "BLOCKED - the current factbase or channel draft could not be assembled. "
                "Read public facts to inspect source availability; check the channel length limits. "
                "No previous draft is retained in these outputs."
            ),
        )
    verdict = []
    for name, draft in drafts.items():
        if draft.shippable:
            verdict.append(f"{name}: SHIPPABLE — passes the house linter only")
        else:
            verdict.append(f"{name}: BLOCKED")
            verdict.extend(f"  - {v}" for v in draft.violations)
    return drafts["substack"].text, drafts["x"].text, "\n".join(verdict)


def lint_copy(text: str) -> str:
    violations = lint(text or "")
    if not violations:
        return "CLEAN - this copy passes the house guardrails. This is not publication approval."
    return "BLOCKED - resolve the following house-rule findings:\n\n" + "\n".join(
        f"- {v}" for v in violations
    )


def about() -> str:
    return provenance()


def native_theme() -> gr.themes.Base:
    """Use local font stacks and bind both Gradio polarities to KANCHAY roles."""
    theme = gr.themes.Base(
        font=["system-ui", "-apple-system", "Segoe UI", "sans-serif"],
        font_mono=["ui-monospace", "SFMono-Regular", "Consolas", "monospace"],
    )
    roles = {
        "body_background_fill": "var(--bg)",
        "body_text_color": "var(--text)",
        "body_text_color_subdued": "var(--text-sub)",
        "background_fill_primary": "var(--surface)",
        "background_fill_secondary": "var(--surface-alt)",
        "border_color_primary": "var(--border)",
        "border_color_accent": "var(--focus)",
        "border_color_accent_subdued": "var(--control-edge)",
        "link_text_color": "var(--link)",
        "link_text_color_hover": "var(--link-hover)",
        "link_text_color_active": "var(--link-hover)",
        "link_text_color_visited": "var(--link)",
        "block_background_fill": "var(--surface)",
        "block_border_color": "var(--border)",
        "block_info_text_color": "var(--text-sub)",
        "block_label_background_fill": "var(--surface)",
        "block_label_text_color": "var(--text)",
        "block_title_text_color": "var(--text)",
        "input_background_fill": "var(--surface)",
        "input_background_fill_focus": "var(--surface)",
        "input_border_color": "var(--control-edge)",
        "input_border_color_focus": "var(--focus)",
        "input_placeholder_color": "var(--text-ghost)",
        "button_primary_background_fill": "var(--action-bg)",
        "button_primary_background_fill_hover": "var(--action-hover-bg)",
        "button_primary_text_color": "var(--action-ink)",
        "button_primary_text_color_hover": "var(--action-ink)",
        "button_secondary_background_fill": "var(--surface)",
        "button_secondary_background_fill_hover": "var(--surface-alt)",
        "button_secondary_text_color": "var(--text)",
        "button_secondary_text_color_hover": "var(--text)",
        "button_secondary_border_color": "var(--control-edge)",
        "accordion_text_color": "var(--text)",
        "table_text_color": "var(--text)",
        "panel_background_fill": "var(--surface)",
        "panel_border_color": "var(--border)",
    }
    return theme.set(
        **roles,
        **{f"{name}_dark": value for name, value in roles.items()},
        color_accent="var(--focus)",
        body_text_size="16px",
        prose_text_size="16px",
        button_large_text_size="16px",
        block_label_text_size="14px",
        block_info_text_size="14px",
        block_radius="12px",
        block_padding="20px",
        input_radius="8px",
        button_large_radius="8px",
        layout_gap="24px",
    )


with gr.Blocks(
    title="SZL Marketing — Governed Fact Factory", analytics_enabled=False, fill_width=True
) as demo:
    gr.HTML(header(), elem_id="factory-header", js_on_load=None, apply_default_css=False)
    with gr.Column(elem_id="factory-workspace", min_width=0):
        with gr.Tabs(elem_id="factory-tabs", overflow_behavior="wrap"):
            with gr.Tab("Public facts", id="facts", elem_id="factory-panel-facts"):
                gr.Markdown(
                    "## Start with an observation\n\n"
                    "Read the public GitHub and Hugging Face sources through the existing fact "
                    "engine. Values keep their source labels and timestamp. This view covers "
                    "public repositories, models, datasets and Spaces; private assets, native "
                    "kernels, collections and buckets are outside this engine's census.",
                    elem_classes="factory-intro",
                )
                measure_btn = gr.Button(
                    "Read public facts", variant="primary", elem_id="measure-facts"
                )
                facts_html = gr.HTML(
                    initial_observation(),
                    elem_id="fact-observation",
                    js_on_load=None,
                    apply_default_css=False,
                )
                with gr.Accordion(
                    "Inspect the raw factbase JSON", open=False, elem_id="raw-factbase"
                ):
                    facts_json = gr.Textbox(
                        label="Exact engine output",
                        info="Read-only JSON from this request.",
                        lines=12,
                        max_lines=22,
                        interactive=False,
                        buttons=["copy"],
                        elem_classes="factory-code",
                    )
                measure_btn.click(measure, outputs=[facts_html, facts_json], api_name=False)
            with gr.Tab("Draft studio", id="drafts", elem_id="factory-panel-drafts"):
                gr.Markdown(
                    "## Your voice, with labeled facts\n\n"
                    "Write two distinct subject lines and the essay body. Compose requests a new "
                    "public factbase, runs the existing channel composers and reports each house "
                    "linter result. A SHIPPABLE result means the house rules passed; it is not "
                    "independent fact verification or permission to publish.",
                    elem_classes="factory-intro",
                )
                with gr.Row(equal_height=False):
                    with gr.Column(scale=4, min_width=260):
                        subject_a = gr.Textbox(label="Subject line A", value="Receipts, not vibes")
                        subject_b = gr.Textbox(label="Subject line B", value="The honest label")
                        body = gr.Textbox(
                            label="Essay body",
                            info="Your original wording, kept as plain text.",
                            placeholder="What should the reader understand?",
                            lines=10,
                        )
                        compose_btn = gr.Button(
                            "Compose from fresh public facts",
                            variant="primary",
                            elem_id="compose-drafts",
                        )
                        verdict_out = gr.Textbox(
                            label="House linter verdict",
                            lines=6,
                            max_lines=14,
                            interactive=False,
                            elem_id="compose-verdict",
                        )
                    with gr.Column(scale=5, min_width=260):
                        substack_out = gr.Textbox(
                            label="Substack draft · source text",
                            lines=14,
                            max_lines=24,
                            interactive=False,
                            buttons=["copy"],
                            elem_id="substack-draft",
                            elem_classes="factory-code",
                        )
                        x_out = gr.Textbox(
                            label="X thread · source text",
                            lines=10,
                            max_lines=18,
                            interactive=False,
                            buttons=["copy"],
                            elem_id="x-draft",
                            elem_classes="factory-code",
                        )
                compose_btn.click(
                    compose,
                    inputs=[subject_a, subject_b, body],
                    outputs=[substack_out, x_out, verdict_out],
                    api_name=False,
                )
            with gr.Tab("Copy review", id="review", elem_id="factory-panel-review"):
                gr.Markdown(
                    "## Check the words before they travel\n\n"
                    "This local house-rule check flags restricted claims and wording. It does "
                    "not contact the public fact APIs or verify every statement in your copy.",
                    elem_classes="factory-intro",
                )
                with gr.Row(equal_height=False):
                    with gr.Column(min_width=260):
                        copy_in = gr.Textbox(label="Draft to review", lines=12)
                        lint_btn = gr.Button(
                            "Review house guardrails", variant="primary", elem_id="review-copy"
                        )
                    with gr.Column(min_width=260):
                        lint_out = gr.Textbox(
                            label="House-rule findings",
                            lines=12,
                            max_lines=22,
                            interactive=False,
                            elem_id="lint-findings",
                        )
                lint_btn.click(lint_copy, inputs=copy_in, outputs=lint_out, api_name=False)
            with gr.Tab("Operating plan", id="plan", elem_id="factory-panel-plan"):
                gr.Markdown(render_plan(), elem_id="factory-plan")
            with gr.Tab("Source & package", id="source", elem_id="factory-panel-source"):
                gr.HTML(
                    about(), elem_id="factory-provenance", js_on_load=None, apply_default_css=False
                )
    gr.HTML(footer(), elem_id="factory-footer", js_on_load=None, apply_default_css=False)


def launch(**kwargs):
    """The owned page head preserves root tokens before Gradio scopes component CSS."""
    return demo.launch(
        theme=native_theme(),
        js=native_js(),
        head=native_head(),
        footer_links=[],
        **kwargs,
    )


if __name__ == "__main__":
    launch()
