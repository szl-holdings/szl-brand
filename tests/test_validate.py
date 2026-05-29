"""Tests for szl_brand validation and manifest system."""

from pathlib import Path

from PIL import Image

from szl_brand.validate import (
    Manifest,
    check_drift,
    generate_manifest,
    validate_directory,
)


def _create_test_png(path: Path, width: int = 1280, height: int = 640) -> None:
    """Create a test PNG file."""
    img = Image.new("RGB", (width, height), (128, 90, 213))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG")


class TestValidateDirectory:
    def test_validates_valid_png(self, tmp_path):
        png = tmp_path / "test.png"
        _create_test_png(png)
        records = validate_directory(tmp_path)
        assert len(records) == 1
        assert records[0].validated is True
        assert records[0].width == 1280
        assert records[0].height == 640

    def test_detects_wrong_dimensions_in_social_previews(self, tmp_path):
        sp_dir = tmp_path / "social-previews"
        sp_dir.mkdir()
        _create_test_png(sp_dir / "bad.png", 800, 400)
        records = validate_directory(sp_dir)
        assert len(records) == 1
        assert records[0].validated is False
        assert "Expected 1280x640" in records[0].errors[0]

    def test_empty_directory(self, tmp_path):
        records = validate_directory(tmp_path)
        assert records == []

    def test_ignores_non_image_files(self, tmp_path):
        (tmp_path / "readme.txt").write_text("hello")
        (tmp_path / "data.json").write_text("{}")
        records = validate_directory(tmp_path)
        assert records == []

    def test_sha256_is_hex_string(self, tmp_path):
        _create_test_png(tmp_path / "hash.png")
        records = validate_directory(tmp_path)
        assert len(records[0].sha256) == 64
        int(records[0].sha256, 16)


class TestManifest:
    def test_generate_manifest(self, tmp_path):
        _create_test_png(tmp_path / "a.png")
        _create_test_png(tmp_path / "b.png", 100, 100)
        manifest = generate_manifest(tmp_path)
        assert len(manifest.assets) == 2
        assert manifest.root_hash
        assert manifest.generated_at

    def test_manifest_round_trip(self, tmp_path):
        _create_test_png(tmp_path / "test.png")
        manifest = generate_manifest(tmp_path)
        json_str = manifest.to_json()
        restored = Manifest.from_json(json_str)
        assert restored.root_hash == manifest.root_hash
        assert len(restored.assets) == len(manifest.assets)

    def test_manifest_deterministic(self, tmp_path):
        _create_test_png(tmp_path / "det.png")
        m1 = generate_manifest(tmp_path)
        m2 = generate_manifest(tmp_path)
        assert m1.root_hash == m2.root_hash


class TestDriftDetection:
    def test_no_drift(self, tmp_path):
        _create_test_png(tmp_path / "stable.png")
        manifest = generate_manifest(tmp_path)
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(manifest.to_json())
        drifts = check_drift(manifest_path, tmp_path)
        assert drifts == []

    def test_detects_addition(self, tmp_path):
        _create_test_png(tmp_path / "original.png")
        manifest = generate_manifest(tmp_path)
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(manifest.to_json())
        _create_test_png(tmp_path / "new.png", 100, 100)
        drifts = check_drift(manifest_path, tmp_path)
        added = [d for d in drifts if d["type"] == "added"]
        assert len(added) == 1

    def test_detects_removal(self, tmp_path):
        png = tmp_path / "will_delete.png"
        _create_test_png(png)
        manifest = generate_manifest(tmp_path)
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(manifest.to_json())
        png.unlink()
        drifts = check_drift(manifest_path, tmp_path)
        removed = [d for d in drifts if d["type"] == "removed"]
        assert len(removed) == 1

    def test_detects_modification(self, tmp_path):
        png = tmp_path / "modified.png"
        _create_test_png(png)
        manifest = generate_manifest(tmp_path)
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(manifest.to_json())
        _create_test_png(png, 500, 500)
        drifts = check_drift(manifest_path, tmp_path)
        modified = [d for d in drifts if d["type"] == "modified"]
        assert len(modified) == 1

    def test_missing_manifest(self, tmp_path):
        drifts = check_drift(tmp_path / "nope.json", tmp_path)
        assert drifts[0]["type"] == "error"
