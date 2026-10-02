"""Tests for szl_brand.marketing — facts, linter, drafts, plan, Space packages."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

from szl_brand.marketing import (
    MEASURED,
    RULES,
    UNAVAILABLE,
    compose_all,
    fact,
    fact_block,
    factbase,
    github_facts,
    hf_facts,
    lint,
    lint_paths,
    plan_json,
    plan_text,
    product_facts,
    render_plan,
    strip_html,
    substack_draft,
    surface_facts,
    write_factbase,
    x_thread,
)
from szl_brand.marketing.compose import X_LIMIT
from szl_brand.marketing.space_package import (
    RECEIPT_NAME,
    TARGETS,
    build_package,
    package_root_hash,
    publish_package,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SHA = "a" * 40


# --------------------------------------------------------------------------- fixtures
def _link(next_url: str | None) -> dict[str, str]:
    return {"link": f'<{next_url}>; rel="next"'} if next_url else {}


class FakeHub:
    """Deterministic stand-in for GitHub + Hugging Face + product + domains."""

    def __init__(self, *, dataset_wins: bool = True, product_down: bool = False):
        self.calls: list[str] = []
        self.dataset_wins = dataset_wins
        self.product_down = product_down

    def __call__(self, url: str):
        self.calls.append(url)
        if "api.github.com/orgs/szl-holdings/repos" in url:
            if "page=2" in url:
                return 200, [{"archived": True, "stargazers_count": 3}], {}
            rows = [{"archived": False, "stargazers_count": 1} for _ in range(100)]
            return 200, rows, _link(url + "&page=2")
        if "huggingface.co/api/models" in url:
            return (
                200,
                [{"id": "SZLHOLDINGS/chaski", "downloads": 3070}, {"id": "x", "downloads": 5}],
                {},
            )
        if "huggingface.co/api/datasets" in url:
            crown = 74157 if self.dataset_wins else 10
            return 200, [{"id": "SZLHOLDINGS/killinchu-osint-corpus", "downloads": crown}], {}
        if "huggingface.co/api/spaces" in url:
            return 200, [{"id": f"SZLHOLDINGS/s{i}"} for i in range(33)], {}
        if url.endswith("/api/a11oy/v1/honest"):
            if self.product_down:
                return 503, None, {}
            body = {
                "git_sha": "abc",
                "locked_formula_count": 8,
                "locked_formula_ids": ["F1", "F4"],
                "doctrine_lock": {"doctrine": "v11", "lambda": "Conjecture 1"},
            }
            return 200, body, {}
        if url in ("https://a-11-oy.com/", "https://a-11-oy.com/verify", "https://a11oy.net/"):
            return 200, None, {}
        return 404, None, {}


def _facts(**kwargs):
    return factbase(FakeHub(**kwargs), now=lambda: datetime(2026, 9, 30, 21, 0, tzinfo=UTC))


# --------------------------------------------------------------------------- facts
def test_github_pagination_follows_link_header_and_counts_archived():
    facts = github_facts(FakeHub())
    assert facts["label"] == MEASURED
    assert facts["visibility"] == "PUBLIC"
    assert (facts["repos"], facts["archived"], facts["active"]) == (101, 1, 100)
    assert facts["stars"] == 103


def test_github_unavailable_when_a_page_fails():
    def fetch(url):
        return 500, None, {}

    facts = github_facts(fetch)
    assert facts["label"] == UNAVAILABLE
    assert "reason" in facts


def test_crown_sweeps_models_and_datasets():
    facts = hf_facts(FakeHub())
    assert facts["crown"] == {
        "id": "SZLHOLDINGS/killinchu-osint-corpus",
        "kind": "datasets",
        "downloads": 74157,
        "sweep": "models+datasets",
    }
    assert facts["models_only_crown_diagnostic"]["id"] == "SZLHOLDINGS/chaski"
    assert facts["downloads"] == {"models": 3075, "datasets": 74157, "total": 77232}
    assert (facts["models"], facts["datasets"], facts["spaces"]) == (2, 1, 33)


def test_crown_falls_back_to_model_when_it_leads():
    facts = hf_facts(FakeHub(dataset_wins=False))
    assert facts["crown"]["kind"] == "models"
    assert facts["crown"]["id"] == "SZLHOLDINGS/chaski"


def test_product_and_surfaces_are_labeled():
    facts = _facts()
    assert facts["product"]["locked_formula_count"] == 8
    assert facts["product"]["lambda"] == "Conjecture 1"
    assert facts["surfaces"]["verify_cta"] == "AVAILABLE"
    assert facts["schema"] == "szl.marketing-factbase/v1"
    assert facts["generated"] == "2026-09-30"


def test_product_outage_is_unavailable_not_guessed():
    facts = product_facts(FakeHub(product_down=True))
    assert facts["label"] == UNAVAILABLE
    assert fact({"product": facts}, "product.locked_formula_count") == UNAVAILABLE


def test_surface_probe_failure_hides_the_cta():
    def fetch(url):
        return 0, None, {}

    facts = surface_facts(fetch)
    assert facts["verify_cta"] == UNAVAILABLE
    assert facts["proof_cta"] == UNAVAILABLE


def test_write_factbase_is_deterministic_and_backs_up(tmp_path):
    facts = _facts()
    target = tmp_path / "factbase.json"
    write_factbase(facts, target)
    first = target.read_bytes()
    write_factbase(facts, target)
    assert target.read_bytes() == first
    assert len(list(tmp_path.glob("factbase.json.bak.*"))) == 1
    assert json.loads(first) == json.loads(json.dumps(facts, sort_keys=True))


# --------------------------------------------------------------------------- linter
@pytest.mark.parametrize(
    "text,rule_id",
    [
        ("Our aggregator is proven.", "lambda-proven"),
        ("Users get verified trust from day one.", "lambda-verified-trust"),
        ("We guarantee every receipt.", "guarantee"),
        ("Our models are 100% safe.", "ceiling-percent"),
        ("Trust score: 1.0 across the board.", "ceiling-score"),
        ("A state-of-the-art governed model.", "superlative"),
        ("Zero hallucinations, every time.", "absolute"),
        ("Detection range 3 km in the maritime demo.", "capability-distance"),
        ("It detects targets at 5 miles.", "capability-distance"),
        ("Kilometer-scale drone tracking.", "capability-scale"),
        ("Our strategy delivers strong returns.", "quant-returns"),
        ("Returns of 40% last quarter.", "quant-returns"),
        ("12% annual yield on the paper book.", "quant-returns"),
        ("Projected revenue doubles next year.", "investor-forecast"),
        ("Visit khipu.alloyszlholdings.com today.", "dead-dns"),
        ("Verify at a11oy.com/verify.", "unhyphenated-domain"),
    ],
)
def test_linter_blocks_each_rule(text, rule_id):
    ids = {v.rule_id for v in lint(text)}
    assert rule_id in ids, ids


@pytest.mark.parametrize(
    "text",
    [
        "Λ is Conjecture 1, advisory — never proven.",
        "The words 'proven', 'guaranteed' and 'verified trust' about Λ are banned.",
        "The venue is 3 km from the hotel.",
        "Trust ceiling 0.97, never 1.0.",
        "Verify a receipt yourself: https://a-11-oy.com/verify · Proof registry: https://a11oy.net",
        "Returns are not shown: szl-quant is advisory-only and this is not financial advice.",
        "Describe what exists and what is labeled ROADMAP; a11oy.net is the safe harbor.",
        "We machine-ban our own overclaims in CI.",
    ],
)
def test_linter_passes_the_doctrine_itself(text):
    assert lint(text) == []


def test_linter_is_sentence_scoped():
    text = "Λ is Conjecture 1, advisory. Separately, our ranking is proven."
    violations = lint(text)
    assert [v.rule_id for v in violations] == ["lambda-proven"]
    assert violations[0].sentence.startswith("Separately")


def test_unhyphenated_domain_is_not_excused_by_a_disclaimer():
    assert {v.rule_id for v in lint("Advisory: see a11oy.com for details.")} == {
        "unhyphenated-domain"
    }


def test_rule_ids_are_unique_and_patterns_compile():
    ids = [rule.id for rule in RULES]
    assert len(ids) == len(set(ids))
    for rule in RULES:
        re.compile(rule.pattern)
        if rule.context:
            re.compile(rule.context)


def test_strip_html_and_lint_paths(tmp_path):
    page = tmp_path / "index.html"
    page.write_text("<style>.x{}</style><p>We <b>guarantee</b> it &amp; more.</p>", "utf-8")
    clean = tmp_path / "ok.md"
    clean.write_text("Receipts, not vibes.", "utf-8")
    assert "guarantee" in strip_html(page.read_text("utf-8"))
    report = lint_paths([tmp_path])
    assert [v.rule_id for v in report[str(page)]] == ["guarantee"]
    assert report[str(clean)] == []


def test_lint_paths_reports_missing_file(tmp_path):
    report = lint_paths([tmp_path / "missing.md"])
    assert report[str(tmp_path / "missing.md")][0].rule_id == "unreadable"


# --------------------------------------------------------------------------- drafts
def test_fact_block_carries_labels_and_dataset_crown():
    block = fact_block(_facts())
    assert "121" not in block  # nothing typed; fixture numbers only
    assert "101 public repositories, 1 honestly archived [MEASURED]" in block
    assert "SZLHOLDINGS/killinchu-osint-corpus (74,157 downloads; a dataset" in block
    assert "Λ status: Conjecture 1 [MEASURED]" in block


def test_fact_block_prints_unavailable_for_a_down_source():
    block = fact_block(_facts(product_down=True))
    assert "Locked formulas in the product's honesty manifest: UNAVAILABLE" in block
    assert "[UNAVAILABLE]" in block


def test_substack_has_two_real_subject_lines():
    draft = substack_draft(_facts(), "Body.", ("Receipts, not vibes", "The honest label"))
    assert draft.subject_a == "Receipts, not vibes"
    assert draft.subject_b == "The honest label"
    assert "<!-- SUBJECT A: Receipts, not vibes -->" in draft.text
    assert "<!-- SUBJECT B: The honest label -->" in draft.text
    assert "['" not in draft.text  # never a list repr
    assert draft.shippable


def test_substack_rejects_identical_subjects():
    with pytest.raises(ValueError):
        substack_draft(_facts(), "Body.", ("Same", "Same"))


def test_drafts_with_banned_body_are_not_shippable():
    drafts = compose_all(_facts(), "Our receipts are proven and guaranteed.", ("A", "B"))
    for name in ("substack", "medium", "linkedin"):
        assert not drafts[name].shippable, name
        assert {v.rule_id for v in drafts[name].violations} >= {"lambda-proven", "guarantee"}
    assert drafts["x"].shippable  # the thread carries no team body


def test_x_thread_respects_limit_and_cta_availability():
    draft = x_thread(_facts())
    posts = draft.text.split("\n\n---\n\n")
    assert len(posts) == 4
    assert all(len(p) <= X_LIMIT for p in posts)
    assert "https://a-11-oy.com/verify" in posts[-1]

    def dead(url):
        hub = FakeHub()
        status, body, headers = hub(url)
        if urllib.parse.urlsplit(url).hostname in {"a-11-oy.com", "a11oy.net"}:
            return 0, None, {}
        return status, body, headers

    down = x_thread(factbase(dead))
    assert "UNAVAILABLE" in down.text.split("\n\n---\n\n")[-1]
    assert "a-11-oy.com/verify" not in down.text.split("\n\n---\n\n")[-1]


def test_every_machine_written_template_passes_the_linter():
    drafts = compose_all(_facts(), "", ("A", "B"))
    for name, draft in drafts.items():
        assert draft.shippable, (name, draft.violations)


# --------------------------------------------------------------------------- plan
def test_plan_prose_passes_the_linter_and_renders():
    assert lint(plan_text()) == []
    rendered = render_plan()
    assert lint(rendered) == []
    assert rendered.count("| ") > 10
    data = plan_json()
    assert len(data["backlog"]) == 12
    assert len(data["calendar"]) == 4
    assert len(data["guardrails"]) == 5
    assert set(data["kpis"]) == {"primary", "secondary", "investor", "anti_metric"}
    assert "Conjecture 1" in data["investor_machine"]["hard_floor"]


def test_plan_has_no_typed_estate_counts():
    text = plan_text()
    for typed in (
        "130 repos",
        "120 repos",
        "49 models",
        "50 models",
        "44 datasets",
        "74K",
        "74,157",
    ):
        assert typed not in text, typed


# --------------------------------------------------------------------------- repository copy
def test_checked_in_marketing_copy_is_clean():
    report = lint_paths([REPO_ROOT / "marketing"])
    dirty = {path: [str(v) for v in vs] for path, vs in report.items() if vs}
    assert dirty == {}


# --------------------------------------------------------------------------- space packages
@pytest.mark.parametrize("target", sorted(TARGETS))
def test_space_package_builds_with_receipt(tmp_path, target):
    out = tmp_path / target
    receipt = build_package(target, REPO_ROOT, SHA, out)
    assert receipt["state"] == "PACKAGE_BUILT_NOT_PUBLISHED"
    assert receipt["source"]["sha"] == SHA
    assert receipt["secrets_recorded"] is False
    assert receipt["root_sha256"] == package_root_hash(receipt["files"])
    assert (out / RECEIPT_NAME).is_file()
    assert (out / "README.md").is_file()
    for rel in receipt["files"]:
        assert (out / rel).is_file()
    if TARGETS[target]["vendor_module"]:
        assert (out / "szl_marketing" / "lint.py").read_bytes() == (
            REPO_ROOT / "src/szl_brand/marketing/lint.py"
        ).read_bytes()
        assert (out / "app.py").is_file()
    else:
        assert (out / "index.html").is_file()
        assert (out / "szl-design-system.css").is_file()
        assert (out / "live.js").is_file()


def test_space_package_rejects_bad_sha_and_unknown_target(tmp_path):
    with pytest.raises(ValueError):
        build_package("szl-marketing-1.1", REPO_ROOT, "main", tmp_path / "x")
    with pytest.raises(ValueError):
        build_package("nope", REPO_ROOT, SHA, tmp_path / "y")


@pytest.mark.parametrize("target", sorted(TARGETS))
def test_space_package_rejects_hub_short_description_over_60_chars(tmp_path, target):
    root = tmp_path / "repo"
    spec = TARGETS[target]
    source = root / spec["source_dir"]
    shutil.copytree(REPO_ROOT / spec["source_dir"], source)
    for extra in spec["extra_files"]:
        path = root / extra
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / extra, path)
    readme = source / "README.md"
    original = readme.read_text(encoding="utf-8")
    output = tmp_path / "package"

    readme.write_text(
        re.sub(r"(?m)^short_description:.*$", "short_description: " + "x" * 60, original),
        encoding="utf-8",
    )
    assert build_package(target, root, SHA, output)["state"] == "PACKAGE_BUILT_NOT_PUBLISHED"

    readme.write_text(
        re.sub(r"(?m)^short_description:.*$", "short_description: " + "x" * 61, original),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="short_description exceeds"):
        build_package(target, root, SHA, output)
    assert not output.exists()


def test_space_package_blocks_banned_copy(tmp_path):
    root = tmp_path / "repo"
    src = root / TARGETS["szl-brand-campaign"]["source_dir"]
    src.mkdir(parents=True)
    (src / "README.md").write_text("---\nsdk: static\n---\nWe guarantee it.\n", "utf-8")
    (src / "index.html").write_text("<p>fine</p>", "utf-8")
    (root / "kanchay").mkdir()
    (root / "kanchay" / "szl-design-system.css").write_text("body{}", "utf-8")
    with pytest.raises(ValueError, match="compliance linter"):
        build_package("szl-brand-campaign", root, SHA, tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_publish_fails_closed_without_token(tmp_path, monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    package = tmp_path / "pkg"
    build_package("szl-brand-campaign", REPO_ROOT, SHA, package)
    report_path = tmp_path / "report.json"
    report = publish_package(package, report_path)
    assert report["state"] == UNAVAILABLE
    assert report["reason"].startswith("NO_TOKEN")
    assert report["secrets_recorded"] is False
    assert json.loads(report_path.read_text("utf-8"))["state"] == UNAVAILABLE


def test_publish_refuses_drifted_package(tmp_path, monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "not-a-real-token")
    package = tmp_path / "pkg"
    build_package("szl-brand-campaign", REPO_ROOT, SHA, package)
    (package / "index.html").write_text("tampered", "utf-8")
    with pytest.raises(ValueError, match="drifted"):
        publish_package(package, tmp_path / "report.json")


@pytest.mark.parametrize(
    ("failure_phase", "expected_write_state", "expected_uploads"),
    [
        ("client_initialization", "NOT_ATTEMPTED", 0),
        ("token_identity", "NOT_ATTEMPTED", 0),
        ("pre_upload_file_inventory", "NOT_ATTEMPTED", 0),
        ("upload_folder", "UNKNOWN", 1),
        ("post_upload_file_inventory", "COMMIT_RETURNED", 1),
    ],
)
def test_publish_records_safe_provider_failure(
    tmp_path, monkeypatch, failure_phase, expected_write_state, expected_uploads
):
    canary = "TOKEN-CANARY-DO-NOT-RECORD"
    package = tmp_path / "pkg"
    build_package("szl-brand-campaign", REPO_ROOT, SHA, package)
    uploads = []
    inventories = []

    class ProviderFailure(Exception):
        def __init__(self):
            super().__init__(f"response body includes {canary}")
            self.response = SimpleNamespace(
                status_code=400, text=canary, headers={"Authorization": canary}
            )

    class FakeApi:
        def __init__(self, token):
            assert token == canary
            if failure_phase == "client_initialization":
                raise ProviderFailure()

        def whoami(self):
            if failure_phase == "token_identity":
                raise ProviderFailure()
            return {"name": "publisher"}

        def list_repo_files(self, *_args, **_kwargs):
            inventories.append(True)
            if failure_phase == "pre_upload_file_inventory" or (
                failure_phase == "post_upload_file_inventory" and len(inventories) == 2
            ):
                raise ProviderFailure()
            return ["README.md"]

        def upload_folder(self, **_kwargs):
            uploads.append(True)
            if failure_phase == "upload_folder":
                raise ProviderFailure()
            return SimpleNamespace(commit_url="https://huggingface.co/spaces/example/commit/test")

    fake_hub = ModuleType("huggingface_hub")
    fake_hub.HfApi = FakeApi
    monkeypatch.setitem(sys.modules, "huggingface_hub", fake_hub)
    report_path = tmp_path / "report.json"
    report = publish_package(package, report_path, token=canary)

    assert report["state"] == "FAILED"
    assert report["failure_phase"] == failure_phase
    assert report["failure_type"] == "ProviderFailure"
    assert report["failure_http_status"] == 400
    assert report["hub_write_state"] == expected_write_state
    assert len(report["reason"]) <= 400
    assert len(uploads) == expected_uploads
    assert report.get("publisher") == (
        None if failure_phase in {"client_initialization", "token_identity"} else "publisher"
    )
    assert canary not in report_path.read_text(encoding="utf-8")
    assert "response body" not in report_path.read_text(encoding="utf-8")
    assert "Authorization" not in report_path.read_text(encoding="utf-8")


def test_vendored_space_app_imports_without_network(tmp_path):
    gradio = pytest.importorskip("gradio")
    package = tmp_path / "pkg"
    build_package("szl-marketing-1.1", REPO_ROOT, SHA, package)
    code = (
        "import importlib.util, sys; sys.path.insert(0, sys.argv[1]); "
        "spec = importlib.util.spec_from_file_location('space_app', sys.argv[1] + '/app.py'); "
        "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); "
        "print(type(m.demo).__name__); print(m.lint_copy('We guarantee it.'))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code, str(package)], capture_output=True, text=True, timeout=120
    )
    assert result.returncode == 0, result.stderr
    assert "Blocks" in result.stdout
    assert "BLOCKED" in result.stdout
    assert gradio is not None


# --------------------------------------------------------------------------- cli
def _cli(*args: str, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "szl_brand.marketing.cli", *args],
        capture_output=True,
        text=True,
        timeout=120,
        **kwargs,
    )


def test_cli_lint_text_exit_codes():
    assert _cli("lint", "--text", "Receipts, not vibes.").returncode == 0
    blocked = _cli("lint", "--text", "We guarantee it.")
    assert blocked.returncode == 1
    assert "guarantee" in blocked.stdout


def test_cli_compose_from_fixture_factbase(tmp_path):
    facts_path = tmp_path / "factbase.json"
    facts_path.write_text(json.dumps(_facts()), "utf-8")
    out = tmp_path / "out"
    result = _cli(
        "compose",
        "--facts",
        str(facts_path),
        "--subject-a",
        "Receipts, not vibes",
        "--subject-b",
        "The honest label",
        "--body-text",
        "The team's essay goes here.",
        "--out",
        str(out),
    )
    assert result.returncode == 0, result.stderr
    written = sorted(p.name for p in out.glob("*.md"))
    assert written == [
        "linkedin_2026-09-30.md",
        "medium_2026-09-30.md",
        "substack_2026-09-30.md",
        "x_2026-09-30.md",
    ]
    blocked = _cli(
        "compose",
        "--facts",
        str(facts_path),
        "--subject-a",
        "A",
        "--subject-b",
        "B",
        "--body-text",
        "Guaranteed.",
        "--out",
        str(out / "blocked"),
    )
    assert blocked.returncode == 1
    assert not list((out / "blocked").glob("substack_*.md"))


def test_cli_plan_json():
    result = _cli("plan", "--json")
    assert result.returncode == 0
    assert json.loads(result.stdout)["schema"] == "szl.marketing-plan/v1"


@pytest.mark.skipif(os.environ.get("SZL_LIVE_TESTS") != "1", reason="network smoke test")
def test_live_factbase_smoke():
    facts = factbase()
    assert facts["hf"]["label"] == MEASURED
    assert facts["hf"]["crown"]["sweep"] == "models+datasets"
