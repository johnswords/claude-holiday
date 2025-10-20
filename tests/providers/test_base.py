import pytest
from scripts.providers.base import RenderConfig


class TestRenderConfig:
    """Tests for RenderConfig dataclass parsing"""

    def test_from_strings_valid_resolution(self):
        """Test parsing a valid resolution string"""
        cfg = RenderConfig.from_strings(resolution="1080x1920", fps=30, aspect="9:16")

        assert cfg.width == 1080
        assert cfg.height == 1920
        assert cfg.fps == 30
        assert cfg.aspect == "9:16"
        assert cfg.resolution == "1080x1920"

    def test_from_strings_different_resolution(self):
        """Test parsing different valid resolution formats"""
        cfg = RenderConfig.from_strings(resolution="1920x1080", fps=60, aspect="16:9")

        assert cfg.width == 1920
        assert cfg.height == 1080
        assert cfg.fps == 60
        assert cfg.aspect == "16:9"
        assert cfg.resolution == "1920x1080"

    def test_from_strings_small_resolution(self):
        """Test parsing small resolution values"""
        cfg = RenderConfig.from_strings(resolution="640x480", fps=24, aspect="4:3")

        assert cfg.width == 640
        assert cfg.height == 480
        assert cfg.fps == 24
        assert cfg.aspect == "4:3"

    def test_from_strings_large_resolution(self):
        """Test parsing large resolution values (4K)"""
        cfg = RenderConfig.from_strings(resolution="3840x2160", fps=60, aspect="16:9")

        assert cfg.width == 3840
        assert cfg.height == 2160

    def test_from_strings_invalid_format_no_x(self):
        """Test that resolution without 'x' separator raises ValueError"""
        with pytest.raises(ValueError, match="Invalid resolution.*Expected WIDTHxHEIGHT"):
            RenderConfig.from_strings(resolution="1080-1920", fps=30, aspect="9:16")

    def test_from_strings_invalid_format_missing_height(self):
        """Test that resolution missing height raises ValueError"""
        with pytest.raises(ValueError, match="Invalid resolution.*Expected WIDTHxHEIGHT"):
            RenderConfig.from_strings(resolution="1080x", fps=30, aspect="9:16")

    def test_from_strings_invalid_format_missing_width(self):
        """Test that resolution missing width raises ValueError"""
        with pytest.raises(ValueError, match="Invalid resolution.*Expected WIDTHxHEIGHT"):
            RenderConfig.from_strings(resolution="x1920", fps=30, aspect="9:16")

    def test_from_strings_invalid_format_letters(self):
        """Test that resolution with letters raises ValueError"""
        with pytest.raises(ValueError, match="Invalid resolution.*Expected WIDTHxHEIGHT"):
            RenderConfig.from_strings(resolution="1080xABC", fps=30, aspect="9:16")

    def test_from_strings_invalid_format_empty(self):
        """Test that empty resolution string raises ValueError"""
        with pytest.raises(ValueError, match="Invalid resolution.*Expected WIDTHxHEIGHT"):
            RenderConfig.from_strings(resolution="", fps=30, aspect="9:16")

    def test_from_strings_invalid_format_only_x(self):
        """Test that resolution with only 'x' raises ValueError"""
        with pytest.raises(ValueError, match="Invalid resolution.*Expected WIDTHxHEIGHT"):
            RenderConfig.from_strings(resolution="x", fps=30, aspect="9:16")

    def test_from_strings_invalid_format_extra_characters(self):
        """Test that resolution with extra characters raises ValueError"""
        with pytest.raises(ValueError, match="Invalid resolution.*Expected WIDTHxHEIGHT"):
            RenderConfig.from_strings(resolution="1080x1920px", fps=30, aspect="9:16")

    def test_direct_instantiation(self):
        """Test creating RenderConfig directly via constructor"""
        cfg = RenderConfig(width=1920, height=1080, fps=30, aspect="16:9", resolution="1920x1080")

        assert cfg.width == 1920
        assert cfg.height == 1080
        assert cfg.fps == 30
        assert cfg.aspect == "16:9"
        assert cfg.resolution == "1920x1080"

    def test_dataclass_equality(self):
        """Test that two RenderConfig instances with same values are equal"""
        cfg1 = RenderConfig.from_strings("1080x1920", 30, "9:16")
        cfg2 = RenderConfig.from_strings("1080x1920", 30, "9:16")

        assert cfg1 == cfg2

    def test_dataclass_inequality(self):
        """Test that RenderConfig instances with different values are not equal"""
        cfg1 = RenderConfig.from_strings("1080x1920", 30, "9:16")
        cfg2 = RenderConfig.from_strings("1920x1080", 30, "16:9")

        assert cfg1 != cfg2
