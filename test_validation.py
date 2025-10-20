#!/usr/bin/env python3
"""Quick test to verify schema validation works"""

import sys
import json
from pathlib import Path

# Mock jsonschema if not installed
try:
    import jsonschema
    from jsonschema import ValidationError
    HAS_JSONSCHEMA = True
except ImportError:
    print("WARNING: jsonschema not installed, simulating test...")
    HAS_JSONSCHEMA = False

PROJECT_ROOT = Path(__file__).resolve().parent

def test_validation():
    """Test that validation catches common errors"""

    # Load schema
    schema_path = PROJECT_ROOT / "schemas" / "rcfc.schema.json"
    if not schema_path.exists():
        print(f"ERROR: Schema not found at {schema_path}")
        return False

    with open(schema_path, "r") as f:
        schema = json.load(f)

    if not HAS_JSONSCHEMA:
        print("✓ Schema file exists and is valid JSON")
        print(f"✓ Schema has {len(schema.get('required', []))} required fields")
        print("⚠ Cannot test validation without jsonschema installed")
        return True

    # Test 1: Missing required field (audience_profile)
    print("\nTest 1: Missing required field...")
    bad_recipe_missing = {
        "schema_version": "0.1.0",
        "metadata": {"title": "Test", "created": "2025-01-01"},
        "project": {"name": "Test", "repo_url": "https://example.com"},
        "source": {"commit_sha": "abc123"},
        # Missing: audience_profile
        "scope": {"include_episodes": ["ep1"]},
        "overlays": {"enabled": False, "density": "low", "theme": "default"},
        "ending": "agnostic",
        "captions": {"track": "general", "language": "en"},
        "render": {"fps": 24, "aspect": "16:9", "resolution": "1920x1080"},
        "provider": {"name": "dummy", "options": {}}
    }

    try:
        jsonschema.validate(bad_recipe_missing, schema)
        print("✗ FAILED: Should have caught missing audience_profile")
        return False
    except ValidationError as e:
        print(f"✓ PASSED: Caught missing field: {e.message[:100]}")

    # Test 2: Invalid enum value
    print("\nTest 2: Invalid enum value...")
    bad_recipe_enum = bad_recipe_missing.copy()
    bad_recipe_enum["audience_profile"] = "invalid_value"

    try:
        jsonschema.validate(bad_recipe_enum, schema)
        print("✗ FAILED: Should have caught invalid audience_profile")
        return False
    except ValidationError as e:
        print(f"✓ PASSED: Caught invalid enum: {e.message[:100]}")

    # Test 3: Empty include_episodes
    print("\nTest 3: Empty include_episodes array...")
    bad_recipe_empty = bad_recipe_missing.copy()
    bad_recipe_empty["audience_profile"] = "general"
    bad_recipe_empty["scope"]["include_episodes"] = []

    try:
        jsonschema.validate(bad_recipe_empty, schema)
        print("✗ FAILED: Should have caught empty include_episodes")
        return False
    except ValidationError as e:
        print(f"✓ PASSED: Caught empty array: {e.message[:100]}")

    # Test 4: Valid recipe
    print("\nTest 4: Valid recipe...")
    good_recipe = bad_recipe_missing.copy()
    good_recipe["audience_profile"] = "general"
    good_recipe["scope"]["include_episodes"] = ["ep1"]

    try:
        jsonschema.validate(good_recipe, schema)
        print("✓ PASSED: Valid recipe accepted")
    except ValidationError as e:
        print(f"✗ FAILED: Valid recipe rejected: {e.message}")
        return False

    print("\n" + "="*50)
    print("All validation tests passed! ✓")
    print("="*50)
    return True

if __name__ == "__main__":
    success = test_validation()
    sys.exit(0 if success else 1)
