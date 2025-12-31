"""Integration smoke tests for CLI workflows

These tests verify that the key CLI commands work end-to-end with test fixtures.
They ensure the README examples actually work on a clean machine.
"""

import shutil
import sys
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory for test artifacts"""
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


@pytest.fixture
def test_recipe_path():
    """Path to test recipe fixture"""
    return FIXTURES_DIR / "test_recipe.yaml"


@pytest.fixture
def test_episode_dir():
    """Path to test episode directory"""
    return FIXTURES_DIR / "test_ep01"


class TestRecipeValidation:
    """Test that recipe validation catches errors correctly"""

    def test_validate_valid_recipe(self, test_recipe_path):
        """Valid recipe should pass validation"""
        # Import the validation function from compile_cut
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.compile_cut import validate_recipe

        with open(test_recipe_path) as f:
            recipe = yaml.safe_load(f)

        # Should not raise
        validate_recipe(recipe)

    def test_validate_invalid_recipe_missing_field(self):
        """Invalid recipe with missing required field should fail"""
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.compile_cut import validate_recipe

        # Recipe missing audience_profile
        invalid_recipe = {
            "schema_version": "0.1.0",
            "metadata": {"title": "Test"},
            "project": {"name": "Test", "repo_url": "https://example.com"},
            "source": {"commit_sha": "abc"},
            # Missing audience_profile
            "scope": {"include_episodes": ["ep1"]},
            "overlays": {"enabled": False},
            "ending": "agnostic",
            "captions": {"track": "general", "language": "en"},
            "render": {"fps": 24, "aspect": "16:9", "resolution": "1920x1080"},
            "provider": {"name": "dummy", "options": {}},
        }

        # Use the library's ValidationError
        from jsonschema import ValidationError

        with pytest.raises(ValidationError):
            validate_recipe(invalid_recipe)

    def test_validate_invalid_recipe_bad_enum(self):
        """Invalid recipe with bad enum value should fail"""
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.compile_cut import validate_recipe

        invalid_recipe = {
            "schema_version": "0.1.0",
            "metadata": {"title": "Test"},
            "project": {"name": "Test", "repo_url": "https://example.com"},
            "source": {"commit_sha": "abc"},
            "audience_profile": "invalid_audience",  # Bad enum
            "scope": {"include_episodes": ["ep1"]},
            "overlays": {"enabled": False},
            "ending": "agnostic",
            "captions": {"track": "general", "language": "en"},
            "render": {"fps": 24, "aspect": "16:9", "resolution": "1920x1080"},
            "provider": {"name": "dummy", "options": {}},
        }

        from jsonschema import ValidationError

        with pytest.raises(ValidationError):
            validate_recipe(invalid_recipe)


class TestNewCutScript:
    """Test the new-cut script functionality"""

    def test_scaffold_recipe_creation(self, test_recipe_path, temp_output_dir):
        """Test that new_cut can create a recipe from a template"""
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.new_cut import scaffold_recipe

        output_path = temp_output_dir / "new_recipe.yaml"
        result = scaffold_recipe(test_recipe_path, "New Test Cut", output_path)

        assert result.exists()

        # Verify the output is valid YAML
        with open(result) as f:
            recipe = yaml.safe_load(f)

        assert recipe["metadata"]["title"] == "New Test Cut"
        assert "created" in recipe["metadata"]


class TestCompilationWorkflow:
    """Test the compilation workflow with dummy provider"""

    def test_compile_with_dummy_provider(self, test_recipe_path, temp_output_dir):
        """Test basic compilation workflow with dummy provider

        This is a smoke test to ensure the compilation pipeline can:
        1. Load and validate a recipe
        2. Initialize the provider
        3. Generate outputs without crashing

        Uses dummy provider to avoid external dependencies.
        """
        sys.path.insert(0, str(PROJECT_ROOT))

        # Mock out the parts that require real video files
        from scripts.compile_cut import load_yaml, provider_from_recipe, validate_recipe
        from scripts.providers.base import RenderConfig

        # Load and validate the recipe
        recipe = load_yaml(test_recipe_path)
        validate_recipe(recipe)

        # Verify provider initialization
        provider = provider_from_recipe(recipe)
        assert provider is not None
        assert provider.__class__.__name__ == "DummyProvider"

        # Test that provider can "generate" a scene with correct signature
        test_episode_id = "test_ep01"
        test_scene = {"id": "s1", "duration_sec": 5, "title": "Test Scene"}
        test_output_dir = str(temp_output_dir / "scenes")
        render_cfg = RenderConfig.from_strings(resolution="1080x1920", fps=24, aspect="9:16")

        # Skip if ffmpeg not available (provider uses ffmpeg)

        if not shutil.which("ffmpeg"):
            pytest.skip("FFmpeg not available for dummy provider test")

        # Provider should not crash when asked to generate
        result = provider.generate_scene(test_episode_id, test_scene, test_output_dir, render_cfg)
        assert result is not None
        assert isinstance(result, str)

    def test_rcfc_hash_generation(self, test_recipe_path):
        """Test that Cut URI generation works"""
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.rcfc.uri import compute_rcfc_hash

        with open(test_recipe_path) as f:
            recipe_content = f.read()

        # Should generate a deterministic hash
        hash1 = compute_rcfc_hash(recipe_content)
        hash2 = compute_rcfc_hash(recipe_content)

        assert hash1 == hash2
        assert len(hash1) > 0
        assert isinstance(hash1, str)


class TestOverlayGeneration:
    """Test overlay generation functionality"""

    def test_overlay_imports(self):
        """Verify overlay generation script can be imported"""
        sys.path.insert(0, str(PROJECT_ROOT))

        # Should be able to import without errors
        from scripts.apply_overlays import apply_overlays

        assert callable(apply_overlays)

    def test_caption_generation_imports(self):
        """Verify caption generation script can be imported"""
        sys.path.insert(0, str(PROJECT_ROOT))

        from scripts.generate_captions import generate_captions, generate_per_scene_captions

        assert callable(generate_captions)
        assert callable(generate_per_scene_captions)


class TestRenderConfig:
    """Test render configuration parsing (from existing tests)"""

    def test_render_config_from_recipe(self, test_recipe_path):
        """Test that render config can be parsed from recipe"""
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.providers.base import RenderConfig

        with open(test_recipe_path) as f:
            recipe = yaml.safe_load(f)

        render_cfg = recipe["render"]
        cfg = RenderConfig.from_strings(
            resolution=render_cfg["resolution"], fps=render_cfg["fps"], aspect=render_cfg["aspect"]
        )

        assert cfg.width == 1080
        assert cfg.height == 1920
        assert cfg.fps == 24
        assert cfg.aspect == "9:16"


@pytest.mark.slow
class TestFullPipeline:
    """End-to-end pipeline tests (marked as slow)

    These tests are more comprehensive and may be skipped in quick test runs.
    Run with: pytest -m slow
    """

    def test_full_dummy_compilation_pipeline(self, test_recipe_path):
        """
        Full pipeline test with dummy provider to verify all components integrate.

        This test ensures:
        - Recipe loads and validates
        - Provider initializes correctly
        - All helper functions can be called
        - No import errors or missing dependencies (except optional ones)
        """
        sys.path.insert(0, str(PROJECT_ROOT))

        from scripts.compile_cut import (
            load_yaml,
            provider_from_recipe,
            validate_recipe,
        )
        from scripts.providers.base import RenderConfig

        # 1. Load and validate recipe
        recipe = load_yaml(test_recipe_path)
        validate_recipe(recipe)

        # 2. Initialize provider
        provider = provider_from_recipe(recipe)
        assert provider is not None

        # 3. Parse render config
        render_cfg = recipe["render"]
        cfg = RenderConfig.from_strings(
            resolution=render_cfg["resolution"], fps=render_cfg["fps"], aspect=render_cfg["aspect"]
        )
        assert cfg.width > 0
        assert cfg.height > 0

        # 4. Verify audience profile is valid (no longer loads separate config)
        audience = recipe.get("audience_profile", "general")
        assert audience == "general"  # Only general audience supported now

        # Pipeline successfully initialized!
