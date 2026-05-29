"""Tests for szl_brand preview generator."""

from szl_brand.preview import (
    REGISTRY,
    PreviewSpec,
    StatCard,
    generate_all,
    generate_preview,
)


class TestPreviewSpec:
    def test_registry_not_empty(self):
        assert len(REGISTRY) > 0

    def test_registry_has_14_repos(self):
        assert len(REGISTRY) == 14

    def test_all_specs_have_required_fields(self):
        for spec in REGISTRY:
            assert spec.repo
            assert spec.title
            assert spec.subtitle
            assert spec.kicker
            assert spec.tag


class TestGeneratePreview:
    def test_generates_png(self, tmp_path):
        spec = PreviewSpec(
            repo="test-repo",
            kicker="TEST",
            title="Test Repo",
            subtitle="A test repository",
            tag="TEST",
            stats=[StatCard("42", "Tests"), StatCard("100%", "Coverage")],
        )
        output = tmp_path / "test-repo.png"
        result = generate_preview(spec, output)
        assert result.exists()
        assert result.suffix == ".png"
        assert result.stat().st_size > 0

    def test_correct_dimensions(self, tmp_path):
        from PIL import Image

        spec = PreviewSpec(
            repo="dim-test",
            kicker="SIZE",
            title="Dimension Test",
            subtitle="Should be 1280x640",
            tag="CHECK",
        )
        output = tmp_path / "dim-test.png"
        generate_preview(spec, output)

        with Image.open(output) as img:
            assert img.size == (1280, 640)

    def test_deterministic_output(self, tmp_path):
        spec = PreviewSpec(
            repo="deterministic",
            kicker="DET",
            title="Same Every Time",
            subtitle="Identical output for identical input",
            tag="SEED",
        )
        out1 = tmp_path / "det1.png"
        out2 = tmp_path / "det2.png"
        generate_preview(spec, out1)
        generate_preview(spec, out2)
        assert out1.read_bytes() == out2.read_bytes()

    def test_different_repos_different_output(self, tmp_path):
        spec1 = PreviewSpec(repo="aaa", kicker="A", title="A", subtitle="a", tag="A")
        spec2 = PreviewSpec(repo="bbb", kicker="B", title="B", subtitle="b", tag="B")
        out1 = tmp_path / "a.png"
        out2 = tmp_path / "b.png"
        generate_preview(spec1, out1)
        generate_preview(spec2, out2)
        assert out1.read_bytes() != out2.read_bytes()

    def test_generate_all(self, tmp_path):
        paths = generate_all(tmp_path)
        assert len(paths) == 14
        for p in paths:
            assert p.exists()
            assert p.stat().st_size > 1000

    def test_creates_output_directory(self, tmp_path):
        nested = tmp_path / "deep" / "nested" / "dir"
        spec = PreviewSpec(repo="nested", kicker="N", title="Nested", subtitle="test", tag="T")
        result = generate_preview(spec, nested / "test.png")
        assert result.exists()
