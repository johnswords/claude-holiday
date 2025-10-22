"""Smoke tests ensuring modules import with external dependencies."""

from __future__ import annotations

from importlib import import_module, metadata
from itertools import takewhile


def _version_prefix_tuple(version_string: str) -> tuple[int, ...]:
    """Extract leading numeric segments from a version string."""

    segments: list[int] = []
    for part in version_string.split("."):
        numeric = "".join(takewhile(str.isdigit, part))
        if not numeric:
            break
        segments.append(int(numeric))
    return tuple(segments)


def test_requests_dependency_meets_minimum_version() -> None:
    """Ensure the installed requests version satisfies the declared minimum."""

    installed_version = metadata.version("requests")
    assert _version_prefix_tuple(installed_version) >= (2, 31)


def test_generate_cover_art_module_imports() -> None:
    """The cover art module should import successfully with its dependencies."""

    import_module("scripts.generate_cover_art")
