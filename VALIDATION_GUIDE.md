# RCFC Schema Validation Guide

## Overview

Schema validation has been added to `compile_cut.py` to **fail fast** before any expensive ffmpeg operations. This catches configuration errors like:

- Missing required fields (`audience_profile`, `include_episodes`, etc.)
- Invalid enum values (e.g., `audience_profile: "production"` instead of `"general"`)
- Empty arrays that require items (e.g., `include_episodes: []`)
- Invalid data types or formats

## What Changed

### 1. Dependencies
Added `jsonschema==4.23.0` to `requirements.txt`

### 2. Validation Function
New function in `scripts/compile_cut.py`:

```python
def validate_recipe(recipe: Dict[str, Any]) -> None:
    """
    Validate recipe against RCFC schema. Fails fast with clear errors.
    """
```

This function:
- Loads `schemas/rcfc.schema.json`
- Validates the recipe using `jsonschema.validate()`
- Provides detailed error messages with field paths and expected values

### 3. Integration Point
Validation is called in `compile_cut()` immediately after loading the recipe:

```python
def compile_cut(recipe_path: Path) -> Path:
    recipe = load_yaml(recipe_path)

    # Validate recipe against schema before any expensive operations
    validate_recipe(recipe)

    # ... rest of compilation
```

### 4. Error Handling
Updated `main()` to catch and display validation errors clearly:

```python
except ValidationError as e:
    print(f"[VALIDATION ERROR] {e.message}", file=sys.stderr)
    sys.exit(1)
```

## Installation

Install the new dependency:

```bash
pip install -r requirements.txt
```

Or specifically:

```bash
pip install jsonschema==4.23.0
```

## Testing

### Running Tests

A test script is provided at `test_validation.py`:

```bash
python3 test_validation.py
```

This tests:
1. Missing required fields
2. Invalid enum values
3. Empty arrays where items are required
4. Valid recipes

### Example Invalid Recipes

Three intentionally invalid test recipes are provided in `recipes/examples/`:

1. **INVALID-missing-audience.yaml**
   - Missing required `audience_profile` field
   - Expected error: `'audience_profile' is a required property`

2. **INVALID-empty-episodes.yaml**
   - Empty `include_episodes` array (violates `minItems: 1`)
   - Expected error: `[] is too short`

3. **INVALID-bad-audience.yaml**
   - Invalid enum value for `audience_profile`
   - Expected error: `'production' is not one of ['general', 'dev', 'custom']`

### Manual Testing

Try compiling an invalid recipe (once jsonschema is installed):

```bash
python3 scripts/compile_cut.py --recipe recipes/examples/INVALID-missing-audience.yaml
```

Expected output:
```
[VALIDATION ERROR] Recipe validation failed at 'root': 'audience_profile' is a required property
```

The script will exit with code 1 **before** any ffmpeg operations.

## Bug Fixes Applied

Fixed invalid platform names in example recipes:
- Changed `"youtube-short"` → `"youtube_shorts"` in:
  - `recipes/examples/dev-default.yaml`
  - `recipes/examples/general-default.yaml`
  - `recipes/examples/meta-ending.yaml`

These would have failed validation with the new system.

## Benefits

1. **Fail Fast**: Errors caught immediately, not after minutes of ffmpeg processing
2. **Clear Messages**: Detailed error messages show exactly what's wrong and where
3. **Prevents Bad Data**: Catches typos, missing fields, and invalid values before they cause problems
4. **Schema-Driven**: Single source of truth in `schemas/rcfc.schema.json`
5. **Developer Friendly**: Validation runs automatically on every compile

## Schema Coverage

The schema validates all major sections:

- ✓ Required top-level fields (11 total)
- ✓ Metadata structure
- ✓ Project and source info
- ✓ Audience profile enum values
- ✓ Scope with non-empty episode list
- ✓ Overlays configuration
- ✓ Ending type enum
- ✓ Captions configuration
- ✓ Render settings (fps, resolution, aspect)
- ✓ Provider configuration
- ✓ Social platforms and trims (optional)

## Future Enhancements

Potential improvements:
- Cache schema loading for better performance
- Add validation to other entry points
- Generate TypeScript types from schema
- Add schema versioning checks
- Provide fix suggestions for common errors
