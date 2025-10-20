from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple

import yaml
import jsonschema
from jsonschema import ValidationError

from scripts.rcfc.uri import compute_rcfc_hash, build_cut_uri
from scripts.providers.base import RenderConfig, Provider
from scripts.providers.prebaked import PrebakedProvider
from scripts.providers.dummy import DummyProvider
from scripts.apply_overlays import apply_overlays


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FONT_MAC = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"


def validate_recipe(recipe: Dict[str, Any]) -> None:
    """
    Validate recipe against RCFC schema. Fails fast with clear errors.

    Raises:
        ValidationError: If recipe does not conform to schema
        FileNotFoundError: If schema file is missing
    """
    schema_path = PROJECT_ROOT / "schemas" / "rcfc.schema.json"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    try:
        jsonschema.validate(instance=recipe, schema=schema)
    except ValidationError as e:
        # Build a helpful error message with context
        error_path = ".".join(str(p) for p in e.path) if e.path else "root"
        error_msg = f"Recipe validation failed at '{error_path}': {e.message}"

        # Add schema context if available
        if e.schema_path:
            schema_location = ".".join(str(p) for p in e.schema_path)
            error_msg += f"\nSchema requirement: {schema_location}"

        # Add the failing value for debugging
        if e.instance is not None:
            error_msg += f"\nProvided value: {e.instance}"

        raise ValidationError(error_msg) from e


def load_yaml(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def parse_resolution(res: str) -> Tuple[int, int]:
    w, h = res.split("x")
    return int(w), int(h)


def provider_from_recipe(recipe: Dict[str, Any]) -> Provider:
    name = (recipe.get("provider") or {}).get("name", "prebaked")
    if name == "prebaked":
        return PrebakedProvider()
    if name == "dummy":
        return DummyProvider()
    # Future: Sora provider
    raise ValueError(f"Unsupported provider '{name}' (supported: prebaked, dummy)")


def select_audience_config(audience: str) -> Dict[str, Any]:
    cfg_dir = PROJECT_ROOT / "scripts" / "config"
    path = cfg_dir / f"audience.{audience}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Audience config not found: {path}")
    return load_yaml(path)


def load_series_config() -> Dict[str, Any]:
    cfg_path = PROJECT_ROOT / "scripts" / "config" / "series.yaml"
    return load_yaml(cfg_path)


def load_episode_manifest(episode_id: str) -> Dict[str, Any]:
    path = PROJECT_ROOT / "episodes" / episode_id / "episode.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Episode manifest not found: {path}")
    return load_yaml(path)


def ffmpeg_concat(clips: List[Path], out_path: Path, fps: int, width: int, height: int) -> None:
    # Re-encode to ensure consistent stream parameters
    concat_file = out_path.parent / "concat.txt"
    concat_file.parent.mkdir(parents=True, exist_ok=True)
    with open(concat_file, "w", encoding="utf-8") as f:
        for clip in clips:
            f.write(f"file '{clip.as_posix()}'\n")

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-r",
        str(fps),
        "-vf",
        f"scale={width}:{height}",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        str(out_path),
    ]
    try:
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Log ffmpeg stderr (contains progress and warnings even on success)
        if result.stderr:
            print(f"[FFMPEG] {result.stderr}", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        error_msg = f"FFmpeg concat failed for {out_path}\n"
        error_msg += f"Command: {' '.join(cmd)}\n"
        if e.stderr:
            error_msg += f"Error output:\n{e.stderr}"
        raise RuntimeError(error_msg) from e


def compile_episode(
    episode_id: str,
    recipe: Dict[str, Any],
    render_cfg: RenderConfig,
    audience_cfg: Dict[str, Any],
    cut_id: str,
    font_path: str | None = None,
) -> Path:
    manifest = load_episode_manifest(episode_id)
    scenes = manifest.get("scenes") or []
    provider = provider_from_recipe(recipe)

    tmp_dir = PROJECT_ROOT / "output" / "tmp" / cut_id / episode_id
    tmp_dir.mkdir(parents=True, exist_ok=True)

    ov_enabled = bool((recipe.get("overlays") or {}).get("enabled", False))
    # Determine number of candidates to generate per scene (default 1)
    num_candidates = int(((recipe.get("provider") or {}).get("options") or {}).get("num_candidates", 1))
    # Selections file (optional): episodes/{episode_id}/renders/selections/{cut_id}.yaml
    selections_path = PROJECT_ROOT / "episodes" / episode_id / "renders" / "selections" / f"{cut_id}.yaml"
    selections_map: Dict[str, Any] = {}
    if selections_path.exists():
        try:
            selections_map = load_yaml(selections_path)
        except Exception:
            selections_map = {}

    # Collect scene output paths for concat (if not candidates-only)
    scene_outputs: List[Path] = []

    for scene in scenes:
        scene_id = scene.get("id", "scene")
        scene_dir = tmp_dir / scene_id
        scene_dir.mkdir(parents=True, exist_ok=True)

        # 1) Generate or resolve scene candidates
        candidates: List[Dict[str, Any]] = []
        for idx in range(1, max(1, num_candidates) + 1):
            cand_dir = scene_dir / f"cand{idx}"
            cand_dir.mkdir(parents=True, exist_ok=True)
            # Provider writes to cand_dir / f"{scene_id}.mp4"
            clip_path = Path(
                provider.generate_scene(
                    episode_id,
                    scene,
                    str(cand_dir),
                    render_cfg,
                    seed=idx,  # varying seed by candidate index
                )
            )
            # Normalize to relative path for manifests
            rel_clip = clip_path.resolve()
            candidates.append(
                {
                    "index": idx,
                    "path": str(rel_clip.relative_to(PROJECT_ROOT)),
                    "duration_sec": int(scene.get("duration_sec") or 1),
                }
            )

        # 2) Write per-scene candidates manifest
        cand_manifest_path = scene_dir / "candidates.json"
        with open(cand_manifest_path, "w", encoding="utf-8") as cf:
            json.dump({"scene_id": scene_id, "candidates": candidates}, cf, indent=2)

        # 3) If candidates-only mode, do not append to outputs (skip overlays & concat)
        if os.environ.get("CH_CANDIDATES_ONLY") == "1":
            continue

        # 4) Choose winner: from selections (if present), else default to 1
        winner_index = 1
        if selections_map:
            # Support formats:
            # scenes:
            #   s1: 2
            #   s2: { winner_index: 3 }
            sm_scenes = selections_map.get("scenes") or {}
            s_val = sm_scenes.get(scene_id)
            if isinstance(s_val, int):
                winner_index = int(s_val)
            elif isinstance(s_val, dict):
                winner_index = int(s_val.get("winner_index", 1))
        # Bounds check
        if winner_index < 1 or winner_index > len(candidates):
            winner_index = 1
        chosen_rel = candidates[winner_index - 1]["path"]
        chosen_path = PROJECT_ROOT / chosen_rel

        # 5) Apply overlays to the chosen candidate if enabled
        overlays_instances = []
        if ov_enabled:
            for ov in scene.get("overlays", []):
                if "spec" in ov:
                    spec_name = ov["spec"]
                    spec_path = PROJECT_ROOT / "assets" / "templates" / "overlays" / f"{spec_name}.json"
                    if spec_path.exists():
                        import json as _json
                        with open(spec_path, "r", encoding="utf-8") as f:
                            spec_data = _json.load(f)
                        spec_data["start_sec"] = ov.get("start_sec", 0.5)
                        spec_data["duration_sec"] = ov.get("duration_sec", 2.0)
                        spec_data["position"] = ov.get("position", spec_data.get("position", "top_right"))
                        overlays_instances.append(spec_data)
                elif "type" in ov:
                    overlays_instances.append(ov)

        if ov_enabled and overlays_instances:
            overlaid = scene_dir / f"{scene_id}_ov.mp4"
            apply_overlays(
                in_path=chosen_path,
                overlays=overlays_instances,
                out_path=overlaid,
                width=render_cfg.width,
                height=render_cfg.height,
                font_path=font_path,
            )
            scene_outputs.append(overlaid)
        else:
            scene_outputs.append(chosen_path)

    # 6) Concatenate scene clips into an episode file (unless candidates-only)
    out_dir = PROJECT_ROOT / "output" / "episodes" / episode_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{episode_id}__{cut_id}.mp4"

    if os.environ.get("CH_CANDIDATES_ONLY") == "1":
        # Write episode-level candidates marker for discoverability
        ready_flag = tmp_dir / "_candidates_ready.txt"
        ready_flag.write_text("candidates generated; use select_winners.py to create selections and recompile\n", encoding="utf-8")
        return ready_flag

    ffmpeg_concat(scene_outputs, out_path, fps=render_cfg.fps, width=render_cfg.width, height=render_cfg.height)
    return out_path


def compile_cut(recipe_path: Path) -> Path:
    recipe = load_yaml(recipe_path)

    # Validate recipe against schema before any expensive operations
    validate_recipe(recipe)

    series_cfg = load_series_config()
    audience = recipe.get("audience_profile", "general")
    audience_cfg = select_audience_config(audience)

    fps = int((recipe.get("render") or {}).get("fps", series_cfg.get("fps", 24)))
    resolution = (recipe.get("render") or {}).get("resolution", series_cfg.get("resolution", "1080x1920"))
    aspect = (recipe.get("render") or {}).get("aspect", series_cfg.get("aspect", "9:16"))
    width, height = parse_resolution(resolution)
    render_cfg = RenderConfig.from_strings(resolution=resolution, fps=fps, aspect=aspect)

    # Compute rcfc hash and cut id
    rcfc_hash = compute_rcfc_hash(recipe)
    cut_id = rcfc_hash  # compact id
    commit_sha = (recipe.get("source") or {}).get("commit_sha", "HEAD")
    cut_uri = build_cut_uri(commit_sha=commit_sha, rcfc_hash=rcfc_hash, audience=audience)

    # Determine font (optional, for drawtext)
    font_path = None
    if Path(DEFAULT_FONT_MAC).exists():
        font_path = DEFAULT_FONT_MAC

    # Compile episodes (or just generate candidates)
    include_eps = (recipe.get("scope") or {}).get("include_episodes", [])
    episode_outputs: List[Dict[str, Any]] = []
    for ep in include_eps:
        ep_out = compile_episode(
            episode_id=ep,
            recipe=recipe,
            render_cfg=render_cfg,
            audience_cfg=audience_cfg,
            cut_id=cut_id,
            font_path=font_path,
        )
        # Only include in manifest when not candidates-only (ep_out is a flag file otherwise)
        if os.environ.get("CH_CANDIDATES_ONLY") != "1":
            episode_outputs.append(
                {
                    "episode_id": ep,
                    "video_path": str(ep_out.relative_to(PROJECT_ROOT)),
                }
            )

    # Optional: Stitch series (not strictly required for MVP)
    # For now, skip series stitch; episodes are compiled individually.

    # Timeline (optional)
    timeline = recipe.get("timeline") or (recipe.get("metadata") or {}).get("timeline") or "Prime"

    # Write manifest
    manifest = {
        "cut_id": cut_id,
        "cut_uri": cut_uri,
        "rcfc_hash": rcfc_hash,
        "commit_sha": commit_sha,
        "timeline": timeline,
        "recipe_snapshot": recipe,
        "episodes": episode_outputs if os.environ.get("CH_CANDIDATES_ONLY") != "1" else [],
        "created": datetime.utcnow().isoformat() + "Z",
        "render": {
            "fps": fps,
            "resolution": resolution,
            "aspect": aspect,
        },
    }
    # Help reviewers locate candidates when in candidates-only mode
    if os.environ.get("CH_CANDIDATES_ONLY") == "1":
        manifest["candidates_root"] = str((PROJECT_ROOT / "output" / "tmp" / cut_id).relative_to(PROJECT_ROOT))

    manifest_path = PROJECT_ROOT / "output" / "cuts" / cut_id / "manifest" / "cut.manifest.json"
    save_json(manifest_path, manifest)
    print(f"[OK] Cut compiled: {manifest['cut_uri']}")
    print(f"[MANIFEST] {manifest_path}")
    if os.environ.get("CH_CANDIDATES_ONLY") == "1":
        print(f"[CANDIDATES] Root: {manifest['candidates_root']}")
    else:
        for e in episode_outputs:
            print(f"[EPISODE] {e['episode_id']} -> {e['video_path']}")
    return manifest_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile a Claude Holiday cut from an RCFC recipe.")
    parser.add_argument("--recipe", required=True, help="Path to RCFC recipe YAML")
    parser.add_argument("--candidates-only", action="store_true", help="Generate candidates per scene and skip stitching")
    args = parser.parse_args()
    recipe_path = Path(args.recipe)
    if not recipe_path.exists():
        print(f"Recipe not found: {recipe_path}", file=sys.stderr)
        sys.exit(1)
    if args.candidates_only:
        os.environ["CH_CANDIDATES_ONLY"] = "1"
    try:
        compile_cut(recipe_path)
    except ValidationError as e:
        # Schema validation failed - fail fast with clear error
        print(f"[VALIDATION ERROR] {e.message}", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        # Surface ffmpeg errors nicely
        sys.stderr.write(e.stderr.decode("utf-8", errors="ignore") if e.stderr else str(e) + "\n")
        sys.exit(2)


if __name__ == "__main__":
    main()