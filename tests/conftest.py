"""Pytest configuration and shared fixtures for Claude Holiday tests.

This module provides reusable test fixtures for:
- RCFC recipe validation
- Episode manifest handling
- Overlay configuration testing (general audience)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import yaml

# Project root and fixtures directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = Path(__file__).parent / "fixtures"


# =============================================================================
# Path Fixtures
# =============================================================================


@pytest.fixture
def fixtures_dir() -> Path:
    """Path to the test fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture
def project_root() -> Path:
    """Path to the project root directory."""
    return PROJECT_ROOT


# =============================================================================
# RCFC Schema Fixtures
# =============================================================================


@pytest.fixture
def rcfc_schema() -> dict[str, Any]:
    """Load the RCFC schema for validation tests."""
    schema_path = PROJECT_ROOT / "schemas" / "rcfc.schema.json"
    assert schema_path.exists(), f"Schema not found at {schema_path}"
    with open(schema_path) as f:
        return json.load(f)


@pytest.fixture
def base_recipe() -> dict[str, Any]:
    """Minimal valid RCFC recipe template."""
    return {
        "schema_version": "0.1.0",
        "metadata": {"title": "Test Recipe", "created": "2025-01-01"},
        "project": {"name": "Test Project", "repo_url": "https://example.com"},
        "source": {"commit_sha": "abc123"},
        "audience_profile": "general",
        "scope": {"include_episodes": ["ep1"]},
        "overlays": {"enabled": False, "density": "low", "theme": "default"},
        "ending": "agnostic",
        "captions": {"track": "general", "language": "en"},
        "render": {"fps": 24, "aspect": "16:9", "resolution": "1920x1080"},
        "provider": {"name": "dummy", "options": {}},
    }


# =============================================================================
# Overlay Fixtures - Valid Cases (General Audience)
# =============================================================================


@pytest.fixture
def valid_overlay_single() -> dict[str, Any]:
    """A single valid overlay configuration (episode manifest format)."""
    return {
        "spec": "scene_title",
        "text": "The First Meeting",
        "start_sec": 2.0,
        "duration_sec": 2.5,
        "position": "bottom_left",
        "track": "general",
    }


@pytest.fixture
def valid_overlay_for_ffmpeg() -> dict[str, Any]:
    """A single valid overlay in FFmpeg-ready format (for apply_overlays)."""
    return {
        "name": "scene_title",
        "type": "text",
        "text": "Chapter One",
        "position": "top_right",
        "start_sec": 5.0,
        "duration_sec": 2.0,
        "font_size": 28,
        "font_color": "white",
        "bg_color": "0x333333AA",
        "padding": 12,
    }


@pytest.fixture
def valid_overlay_multiple() -> list[dict[str, Any]]:
    """Multiple valid overlays on the same scene (episode manifest format)."""
    return [
        {
            "spec": "scene_intro",
            "text": "The Journey Begins",
            "start_sec": 2.0,
            "duration_sec": 2.5,
            "position": "bottom_left",
            "track": "general",
        },
        {
            "spec": "location",
            "text": "Pinecrest Inn",
            "start_sec": 6.0,
            "duration_sec": 2.0,
            "position": "bottom_right",
            "track": "general",
        },
        {
            "spec": "time_indicator",
            "text": "December 23rd",
            "start_sec": 4.0,
            "duration_sec": 3.0,
            "position": "top_right",
            "track": "general",
        },
    ]


@pytest.fixture
def valid_overlay_all_positions() -> list[dict[str, Any]]:
    """Overlays covering all valid position values."""
    positions = ["top_left", "top_right", "bottom_left", "bottom_right"]
    return [
        {
            "spec": f"pos_{pos}",
            "text": f"Position: {pos}",
            "start_sec": i * 2.0,
            "duration_sec": 1.5,
            "position": pos,
            "track": "general",
        }
        for i, pos in enumerate(positions)
    ]


# =============================================================================
# Overlay Fixtures - Invalid Cases
# =============================================================================


@pytest.fixture
def invalid_overlay_missing_text() -> dict[str, Any]:
    """Overlay missing required 'text' field."""
    return {
        "spec": "missing_text",
        # "text" is missing
        "start_sec": 2.0,
        "duration_sec": 2.5,
        "position": "bottom_left",
        "track": "general",
    }


@pytest.fixture
def invalid_overlay_missing_position() -> dict[str, Any]:
    """Overlay missing required 'position' field."""
    return {
        "spec": "missing_position",
        "text": "Some overlay text",
        "start_sec": 2.0,
        "duration_sec": 2.5,
        # "position" is missing
        "track": "general",
    }


@pytest.fixture
def invalid_overlay_missing_timing() -> dict[str, Any]:
    """Overlay missing required timing fields."""
    return {
        "spec": "missing_timing",
        "text": "Some overlay text",
        # "start_sec" and "duration_sec" are missing
        "position": "bottom_left",
        "track": "general",
    }


@pytest.fixture
def invalid_overlay_bad_position() -> dict[str, Any]:
    """Overlay with invalid position value."""
    return {
        "spec": "bad_position",
        "text": "Some overlay text",
        "start_sec": 2.0,
        "duration_sec": 2.5,
        "position": "center",  # Invalid: must be top_left, top_right, bottom_left, bottom_right
        "track": "general",
    }


@pytest.fixture
def invalid_overlay_negative_timing() -> dict[str, Any]:
    """Overlay with negative timing values."""
    return {
        "spec": "negative_timing",
        "text": "Some overlay text",
        "start_sec": -1.0,  # Invalid: negative start time
        "duration_sec": 2.5,
        "position": "bottom_left",
        "track": "general",
    }


@pytest.fixture
def invalid_overlay_zero_duration() -> dict[str, Any]:
    """Overlay with zero duration."""
    return {
        "spec": "zero_duration",
        "text": "Some overlay text",
        "start_sec": 2.0,
        "duration_sec": 0,  # Invalid: zero duration
        "position": "bottom_left",
        "track": "general",
    }


# =============================================================================
# Episode Manifest Fixtures
# =============================================================================


@pytest.fixture
def episode_manifest_with_overlays() -> dict[str, Any]:
    """Complete episode manifest with overlays on multiple scenes."""
    return {
        "episode_id": "test_ep_overlays",
        "title": "Test Episode - Overlay Testing",
        "scenes": [
            {
                "id": "s1",
                "title": "Scene with single overlay",
                "duration_sec": 10,
                "sora_prompt": "Test prompt for scene 1",
                "overlays": [
                    {
                        "spec": "scene_title",
                        "text": "The First Meeting",
                        "start_sec": 2.0,
                        "duration_sec": 2.5,
                        "position": "bottom_left",
                        "track": "general",
                    }
                ],
            },
            {
                "id": "s2",
                "title": "Scene with multiple overlays",
                "duration_sec": 12,
                "sora_prompt": "Test prompt for scene 2",
                "overlays": [
                    {
                        "spec": "location",
                        "text": "Pinecrest Inn",
                        "start_sec": 1.0,
                        "duration_sec": 2.0,
                        "position": "bottom_right",
                        "track": "general",
                    },
                    {
                        "spec": "time_indicator",
                        "text": "December 23rd, Evening",
                        "start_sec": 5.0,
                        "duration_sec": 3.0,
                        "position": "top_right",
                        "track": "general",
                    },
                ],
            },
            {
                "id": "s3",
                "title": "Scene without overlays",
                "duration_sec": 8,
                "sora_prompt": "Test prompt for scene 3",
                "overlays": [],
            },
        ],
        "captions_cues": [],
    }


@pytest.fixture
def episode_manifest_without_overlays() -> dict[str, Any]:
    """Episode manifest with no overlays on any scene."""
    return {
        "episode_id": "test_ep_no_overlays",
        "title": "Test Episode - No Overlays",
        "scenes": [
            {
                "id": "s1",
                "title": "First scene",
                "duration_sec": 8,
                "sora_prompt": "Test prompt for scene 1",
                "overlays": [],
            },
            {
                "id": "s2",
                "title": "Second scene",
                "duration_sec": 10,
                "sora_prompt": "Test prompt for scene 2",
                "overlays": [],
            },
        ],
        "captions_cues": [],
    }


@pytest.fixture
def episode_manifest_minimal() -> dict[str, Any]:
    """Minimal valid episode manifest (omitting optional overlays key)."""
    return {
        "episode_id": "test_ep_minimal",
        "title": "Test Episode - Minimal",
        "scenes": [
            {
                "id": "s1",
                "title": "Single scene",
                "duration_sec": 5,
                "sora_prompt": "Test prompt",
                # Note: 'overlays' key is optional and omitted here
            }
        ],
    }


# =============================================================================
# FFmpeg Overlay Spec Fixtures (JSON format for apply_overlays)
# =============================================================================


@pytest.fixture
def ffmpeg_overlay_spec_empty() -> dict[str, Any]:
    """Empty overlay spec for FFmpeg processing."""
    return {"overlays": []}


@pytest.fixture
def ffmpeg_overlay_spec_single() -> dict[str, Any]:
    """Single overlay spec in FFmpeg format."""
    return {
        "overlays": [
            {
                "name": "scene_title",
                "type": "text",
                "text": "Chapter One",
                "position": "top_right",
                "start_sec": 5.0,
                "duration_sec": 2.0,
                "font_size": 28,
                "font_color": "white",
                "bg_color": "0x333333AA",
                "padding": 12,
            }
        ]
    }


@pytest.fixture
def ffmpeg_overlay_spec_multiple() -> dict[str, Any]:
    """Multiple overlays spec in FFmpeg format."""
    return {
        "overlays": [
            {
                "name": "scene_title",
                "type": "text",
                "text": "The Beginning",
                "position": "top_right",
                "start_sec": 2.0,
                "duration_sec": 2.0,
                "font_size": 28,
                "font_color": "white",
                "bg_color": "0x333333AA",
                "padding": 12,
            },
            {
                "name": "location",
                "type": "text",
                "text": "Pinecrest Village",
                "position": "bottom_left",
                "start_sec": 6.0,
                "duration_sec": 3.0,
                "font_size": 24,
                "font_color": "yellow",
                "bg_color": "0x222222CC",
                "padding": 8,
            },
        ]
    }


@pytest.fixture
def ffmpeg_overlay_spec_special_chars() -> dict[str, Any]:
    """Overlay with special characters requiring escaping."""
    return {
        "overlays": [
            {
                "name": "special_chars",
                "type": "text",
                "text": "Error: Can't parse 'config:settings' - check \\ path",
                "position": "bottom_left",
                "start_sec": 1.0,
                "duration_sec": 3.0,
                "font_size": 28,
                "font_color": "white",
                "bg_color": "0x333333AA",
                "padding": 12,
            }
        ]
    }


# =============================================================================
# Helper Functions for Tests
# =============================================================================


@pytest.fixture
def load_fixture_yaml(fixtures_dir: Path):
    """Factory fixture to load YAML files from fixtures directory."""

    def _load(relative_path: str) -> dict[str, Any]:
        path = fixtures_dir / relative_path
        assert path.exists(), f"Fixture file not found: {path}"
        with open(path) as f:
            return yaml.safe_load(f)

    return _load


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Create a temporary output directory for test artifacts."""
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


# =============================================================================
# Valid Position Values (for parametrized tests)
# =============================================================================

VALID_POSITIONS = ["top_left", "top_right", "bottom_left", "bottom_right"]
INVALID_POSITIONS = ["center", "middle", "left", "right", "top", "bottom", ""]


@pytest.fixture(params=VALID_POSITIONS)
def valid_position(request) -> str:
    """Parametrized fixture for all valid position values."""
    return request.param


@pytest.fixture(params=INVALID_POSITIONS)
def invalid_position(request) -> str:
    """Parametrized fixture for invalid position values."""
    return request.param
