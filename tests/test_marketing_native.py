"""Presentation and delivery regressions; every factbase here is synthetic."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

from szl_brand.marketing.space_package import TARGETS, build_package

ROOT = Path(__file__).resolve().parents[1]
SHA = "a" * 40


@pytest.fixture
def native(tmp_path, monkeypatch):
    package = tmp_path / "package"
    build_package("szl-marketing-1.1", ROOT, SHA, package)
    monkeypatch.syspath_prepend(str(package))
    for name in list(sys.modules):
        if name == "szl_marketing" or name.startswith("szl_marketing."):
            monkeypatch.delitem(sys.modules, name)
    spec = importlib.util.spec_from_file_location(
        "native_presentation", package / "native_presentation.py"
    )
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "native_presentation", module)
    spec.loader.exec_module(module)
    return module, package


def test_native_package_closes_exact_asset_projection(native):
    module, package = native
    receipt = json.loads((package / "PUBLICATION_RECEIPT.json").read_text())
    projection = json.loads((package / "native/PROJECTION.json").read_text())
    installed = TARGETS["szl-marketing-1.1"]["extra_files"]
    assert {row["source_path"]: row["installed_path"] for row in projection["assets"]} == installed
    for row in projection["assets"]:
        actual = (package / row["installed_path"]).read_bytes()
        assert actual == (ROOT / row["source_path"]).read_bytes()
        assert (
            hashlib.sha256(actual).hexdigest()
            == row["sha256"]
            == receipt["files"][row["installed_path"]]
        )
    assert module.native_css().startswith((ROOT / "kanchay/szl-tokens.css").read_text())
    assert len(receipt["files"]) == 20
    assert "UNSIGNED_LOCAL_PROJECTION_METADATA" == projection["classification"]
    assert module._native("icon") == (package / "native/szl-icon-32.svg").read_bytes()


def test_native_read_rejects_tamper_symlinks_and_unknown_names(native, tmp_path):
    module, package = native
    with pytest.raises(ValueError, match="unknown native asset"):
        module._native("../../README.md")
    with pytest.raises(ValueError, match="unknown presentation file"):
        module._local("../factory.css")
    asset = package / "native/szl-icon-32.svg"
    original = asset.read_bytes()
    asset.write_bytes(original + b" ")
    with pytest.raises(ValueError, match="accepted projection"):
        module._native("icon")
    asset.unlink()
    outside = tmp_path / "outside.svg"
    outside.write_bytes(original)
    asset.symlink_to(outside)
    with pytest.raises(OSError):
        module._native("icon")
    asset.unlink()
    asset.write_bytes(original)
    directory = package / "native"
    directory.rename(package / "moved-native")
    directory.symlink_to(package / "moved-native", target_is_directory=True)
    with pytest.raises(OSError):
        module._native("icon")


def test_same_descriptor_reader_rejects_nonregular_and_oversized_files(native):
    module, package = native
    descriptor = os.open(package, os.O_RDONLY | os.O_DIRECTORY)
    try:
        with pytest.raises(ValueError, match="bounded regular"):
            module._read_fd(descriptor, 16)
    finally:
        os.close(descriptor)
    (package / "factory.css").write_bytes(b"a" * 262145)
    with pytest.raises(ValueError, match="bounded regular"):
        module.native_css()


def test_observation_preserves_zero_missing_and_source_labels(native):
    module, _ = native
    shown = module.observation(
        {
            "generated_at": "2026-10-11T12:00:00Z",
            "github": {"label": "MEASURED", "repos": 0, "archived": True},
            "hf": {"label": {"invalid": "shape"}, "models": 5},
            "surfaces": {"label": "MEASURED", "verify_cta": "UNAVAILABLE"},
        }
    )
    assert "<dd>0</dd>" in shown
    assert "<dd>True</dd>" not in shown
    assert "VALUE UNAVAILABLE · SOURCE: MEASURED" in shown
    assert 'data-state="unavailable"' in shown
    assert "SOURCE: UNAVAILABLE" in shown
    assert "2026-10-11T12:00:00Z" in shown
    assert 'Engine timestamp: <span class="mf-mono">UNAVAILABLE' in module.observation(
        {"generated_at": "yesterday"}
    )


def test_observation_escapes_provider_markup_and_does_not_reuse_timestamp(native):
    module, _ = native
    attack = '<img src="https://invalid.example/probe" onerror="alert(1)">'
    good = module.observation({"generated_at": "2026-10-11T12:00:00Z"})
    partial = module.observation({"hf": {"label": "MEASURED", "crown": {"id": attack}}})
    assert "2026-10-11T12:00:00Z" in good
    assert "2026-10-11T12:00:00Z" not in partial
    assert "&lt;img" in partial
    assert "<img" not in partial
    assert 'src="https://invalid.example/probe"' not in partial


@pytest.mark.parametrize(
    "record",
    [
        [],
        None,
        {"source": []},
        {"source": {"sha": "javascript:alert(1)"}},
        {
            "source": {
                "repository": "elsewhere",
                "directory": "marketing/space/szl-marketing-1.1",
                "sha": SHA,
            }
        },
    ],
)
def test_invalid_source_metadata_does_not_create_a_link(native, record):
    module, package = native
    (package / "PUBLICATION_RECEIPT.json").write_text(json.dumps(record))
    shown = module.provenance()
    assert "Declared source link: UNAVAILABLE" in shown
    assert "/commit/" not in shown
    assert "javascript:" not in shown


def test_provenance_retains_package_stage_without_runtime_inference(native):
    module, _ = native
    shown = module.provenance()
    assert "/commit/" + SHA in shown
    assert "PACKAGE_BUILT_NOT_PUBLISHED" in shown
    assert "does not independently verify" in shown
    assert "PUBLISHED_CONVERGED" not in shown


def test_receipt_for_another_target_does_not_borrow_its_source_or_package(native):
    module, package = native
    record = json.loads((package / "PUBLICATION_RECEIPT.json").read_text())
    record["target"]["repository"] = "SZLHOLDINGS/szl-brand-campaign"
    (package / "PUBLICATION_RECEIPT.json").write_text(json.dumps(record))
    shown = module.provenance()
    assert SHA not in shown
    assert record["root_sha256"] not in shown
    assert "PACKAGE_BUILT_NOT_PUBLISHED" not in shown


def test_preserved_card_body_and_pinned_runtime(native):
    _, package = native
    readme = (package / "README.md").read_bytes()
    body = readme.split(b"<!-- SZL-PRESERVED-TECHNICAL-BODY:START -->", 1)[1].split(
        b"<!-- SZL-PRESERVED-TECHNICAL-BODY:END -->", 1
    )[0]
    assert (
        hashlib.sha256(body).hexdigest()
        == "f66bb6fa76c6cc1cee38f7eecb123049692c5226ebdc14382739ea0a0b1dcd99"
    )
    assert b"sdk_version: 6.29.0" in readme
    assert (package / "requirements.txt").read_text().strip() == "gradio==6.29.0"


def test_actual_gradio_callbacks_are_passive_and_keep_literal_draft_text(native, monkeypatch):
    pytest.importorskip("gradio")
    _, package = native
    monkeypatch.setenv("GRADIO_ANALYTICS_ENABLED", "False")
    spec = importlib.util.spec_from_file_location("factory_app", package / "app.py")
    app = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app)
    calls = []

    def unavailable():
        calls.append(True)
        return {"generated_at": "2026-10-11T12:00:00Z"}

    monkeypatch.setattr(app, "factbase", unavailable)
    assert type(app.demo).__name__ == "Blocks"
    assert type(app.native_theme()).__name__ == "Base"
    assert "BLOCKED" in app.lint_copy("We guarantee it.")
    assert calls == []
    assert app.compose("same", "same", "body")[:2] == ("", "")
    assert calls == []
    shown, raw = app.measure()
    assert json.loads(raw) == unavailable()
    assert "UNAVAILABLE" in shown

    class Draft:
        text = '<img src="https://invalid.example/probe">'
        shippable = True
        violations = []

    monkeypatch.setattr(app, "compose_all", lambda *args: {"substack": Draft(), "x": Draft()})
    result = app.compose("first", "second", "body")
    assert result[:2] == (Draft.text, Draft.text)
    assert "house linter only" in result[2]
    monkeypatch.setattr(app, "factbase", lambda: None)
    assert app.compose("first", "second", "body")[:2] == ("", "")
    assert json.loads(app.measure()[1])["label"] == "UNAVAILABLE"
