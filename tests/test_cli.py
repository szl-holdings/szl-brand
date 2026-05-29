"""Tests for szl_brand CLI."""

import subprocess
import sys


class TestCLI:
    def test_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "szl_brand", "--help"], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "szl-brand" in result.stdout

    def test_version(self):
        result = subprocess.run(
            [sys.executable, "-m", "szl_brand", "--version"], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "1.0.0" in result.stdout

    def test_generate(self, tmp_path):
        result = subprocess.run(
            [sys.executable, "-m", "szl_brand", "generate", "-o", str(tmp_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "14 banners" in result.stdout
        pngs = list(tmp_path.glob("*.png"))
        assert len(pngs) == 14

    def test_generate_one(self, tmp_path):
        out = tmp_path / "custom.png"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "szl_brand",
                "generate-one",
                "--repo",
                "my-project",
                "--title",
                "My Project",
                "--subtitle",
                "A custom project",
                "-o",
                str(out),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert out.exists()

    def test_validate(self, tmp_path):
        from PIL import Image

        img = Image.new("RGB", (1280, 640), (0, 0, 0))
        (tmp_path / "social-previews").mkdir()
        img.save(tmp_path / "social-previews" / "test.png")
        result = subprocess.run(
            [sys.executable, "-m", "szl_brand", "validate", str(tmp_path / "social-previews")],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "1 passed" in result.stdout

    def test_manifest(self, tmp_path):
        from PIL import Image

        img = Image.new("RGB", (100, 100), (0, 0, 0))
        img.save(tmp_path / "asset.png")
        manifest_out = tmp_path / "manifest.json"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "szl_brand",
                "manifest",
                str(tmp_path),
                "-o",
                str(manifest_out),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert manifest_out.exists()
        assert "Root hash" in result.stdout

    def test_inventory(self, tmp_path):
        from PIL import Image

        img = Image.new("RGB", (100, 100), (0, 0, 0))
        img.save(tmp_path / "a.png")
        img.save(tmp_path / "b.png")
        result = subprocess.run(
            [sys.executable, "-m", "szl_brand", "inventory", str(tmp_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "png" in result.stdout
