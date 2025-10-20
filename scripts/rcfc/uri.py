from __future__ import annotations

import base64
import json
from typing import Any

from blake3 import blake3

CANON_EXCLUDE_PATHS = [
    ["source", "commit_sha"],  # exclude commit sha from rcfc hash
]


def _deep_copy(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _deep_copy(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_deep_copy(x) for x in obj]
    return obj


def _delete_path(d: dict[str, Any], path: list[str]) -> None:
    cur = d
    for p in path[:-1]:
        if not isinstance(cur, dict) or p not in cur:
            return
        cur = cur[p]
    if isinstance(cur, dict):
        cur.pop(path[-1], None)


def canonicalize_recipe(recipe: dict[str, Any]) -> dict[str, Any]:
    """Return a deep-copied, canonicalized version of the recipe suitable for hashing."""
    c = _deep_copy(recipe)

    # Exclude paths
    for path in CANON_EXCLUDE_PATHS:
        _delete_path(c, path)

    # Sort dict keys deterministically by serializing with sort_keys=True
    # Consumers should serialize with separators for stable hashing.
    return c


def compute_rcfc_hash(recipe: dict[str, Any]) -> str:
    c = canonicalize_recipe(recipe)
    data = json.dumps(c, sort_keys=True, separators=(",", ":")).encode("utf-8")
    h = blake3(data).digest()
    # Return first 10 chars of base32 encoding for compact, human-safe IDs
    return base64.b32encode(h).decode('ascii').rstrip('=')[:10]


def build_cut_uri(commit_sha: str, rcfc_hash: str, audience: str, version: str = "0.1") -> str:
    return f"chcut://{commit_sha}/{rcfc_hash}?audience={audience}&v={version}"
