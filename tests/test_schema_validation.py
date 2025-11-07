"""Tests for RCFC schema validation"""

import json
from pathlib import Path

import pytest

# Try importing jsonschema - these tests will be skipped if not available
pytest.importorskip("jsonschema")

from jsonschema import ValidationError, validate  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def rcfc_schema():
    """Load the RCFC schema for validation tests"""
    schema_path = PROJECT_ROOT / "schemas" / "rcfc.schema.json"
    assert schema_path.exists(), f"Schema not found at {schema_path}"

    with open(schema_path) as f:
        return json.load(f)


@pytest.fixture
def base_recipe():
    """Minimal valid recipe template"""
    return {
        "schema_version": "0.1.0",
        "metadata": {"title": "Test", "created": "2025-01-01"},
        "project": {"name": "Test", "repo_url": "https://example.com"},
        "source": {"commit_sha": "abc123"},
        "audience_profile": "general",
        "scope": {"include_episodes": ["ep1"]},
        "overlays": {"enabled": False, "density": "low", "theme": "default"},
        "ending": "agnostic",
        "captions": {"track": "general", "language": "en"},
        "render": {"fps": 24, "aspect": "16:9", "resolution": "1920x1080"},
        "provider": {"name": "dummy", "options": {}},
    }


class TestSchemaValidation:
    """Test suite for RCFC schema validation"""

    def test_schema_exists(self):
        """Verify schema file exists and is valid JSON"""
        schema_path = PROJECT_ROOT / "schemas" / "rcfc.schema.json"
        assert schema_path.exists()

        with open(schema_path) as f:
            schema = json.load(f)

        assert "required" in schema
        assert len(schema["required"]) > 0

    def test_valid_recipe_passes(self, rcfc_schema, base_recipe):
        """A valid recipe should pass validation"""
        # Should not raise
        validate(instance=base_recipe, schema=rcfc_schema)

    def test_missing_required_field_audience_profile(self, rcfc_schema, base_recipe):
        """Missing audience_profile should fail validation"""
        del base_recipe["audience_profile"]

        with pytest.raises(ValidationError) as exc_info:
            validate(instance=base_recipe, schema=rcfc_schema)

        assert "audience_profile" in str(exc_info.value).lower()

    def test_missing_required_field_scope(self, rcfc_schema, base_recipe):
        """Missing scope should fail validation"""
        del base_recipe["scope"]

        with pytest.raises(ValidationError) as exc_info:
            validate(instance=base_recipe, schema=rcfc_schema)

        assert "scope" in str(exc_info.value).lower()

    def test_invalid_enum_value_audience_profile(self, rcfc_schema, base_recipe):
        """Invalid enum value for audience_profile should fail"""
        base_recipe["audience_profile"] = "invalid_value"

        with pytest.raises(ValidationError) as exc_info:
            validate(instance=base_recipe, schema=rcfc_schema)

        # Should mention the invalid value or enum constraint
        error_msg = str(exc_info.value).lower()
        assert "invalid_value" in error_msg or "enum" in error_msg

    def test_invalid_enum_value_ending(self, rcfc_schema, base_recipe):
        """Invalid enum value for ending should fail"""
        base_recipe["ending"] = "not_a_valid_ending"

        with pytest.raises(ValidationError) as exc_info:
            validate(instance=base_recipe, schema=rcfc_schema)

        error_msg = str(exc_info.value).lower()
        assert "ending" in error_msg or "enum" in error_msg

    def test_empty_include_episodes_array(self, rcfc_schema, base_recipe):
        """Empty include_episodes array should fail validation"""
        base_recipe["scope"]["include_episodes"] = []

        with pytest.raises(ValidationError) as exc_info:
            validate(instance=base_recipe, schema=rcfc_schema)

        # Should mention array length or minItems constraint
        assert "minitems" in str(exc_info.value).lower() or "[]" in str(exc_info.value)

    def test_invalid_fps_type(self, rcfc_schema, base_recipe):
        """FPS as string instead of number should fail"""
        base_recipe["render"]["fps"] = "24"

        with pytest.raises(ValidationError) as exc_info:
            validate(instance=base_recipe, schema=rcfc_schema)

        assert "type" in str(exc_info.value).lower()

    def test_missing_provider_name(self, rcfc_schema, base_recipe):
        """Missing provider name should fail"""
        del base_recipe["provider"]["name"]

        with pytest.raises(ValidationError) as exc_info:
            validate(instance=base_recipe, schema=rcfc_schema)

        assert "name" in str(exc_info.value).lower()

    def test_multiple_episodes_valid(self, rcfc_schema, base_recipe):
        """Multiple episodes in scope should be valid"""
        base_recipe["scope"]["include_episodes"] = ["ep1", "ep2", "ep3"]

        # Should not raise
        validate(instance=base_recipe, schema=rcfc_schema)

    def test_overlays_enabled_valid(self, rcfc_schema, base_recipe):
        """Overlays enabled configuration should be valid"""
        base_recipe["overlays"]["enabled"] = True
        base_recipe["overlays"]["density"] = "high"
        base_recipe["overlays"]["theme"] = "festive"

        # Should not raise
        validate(instance=base_recipe, schema=rcfc_schema)
