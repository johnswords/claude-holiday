from __future__ import annotations

import argparse
import base64
import json
import subprocess
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_yaml(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)


def extract_thumbnail(video_path: Path, timestamp: str = "00:00:01") -> str | None:
    """Extract a frame from video and return as base64 data URI."""
    if not video_path.exists():
        return None

    try:
        cmd = [
            "ffmpeg",
            "-ss",
            timestamp,
            "-i",
            str(video_path),
            "-vframes",
            "1",
            "-f",
            "image2pipe",
            "-vcodec",
            "png",
            "-",
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        b64 = base64.b64encode(result.stdout).decode("utf-8")
        return f"data:image/png;base64,{b64}"
    except Exception:
        return None


def generate_contact_sheet(cut_id: str, episode_selections: list[dict[str, Any]]) -> None:
    """Generate HTML contact sheet showing all candidates for visual review."""
    html_parts = [
        "<!DOCTYPE html>",
        "<html><head>",
        "<meta charset='utf-8'>",
        f"<title>Candidate Review - {cut_id}</title>",
        "<style>",
        "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; ",
        "       background: #1a1a1a; color: #fff; padding: 20px; }",
        "h1 { color: #4a9eff; }",
        "h2 { color: #7cb342; margin-top: 40px; border-bottom: 2px solid #333; padding-bottom: 10px; }",
        "h3 { color: #ffa726; margin-top: 30px; }",
        ".episode { margin-bottom: 50px; }",
        ".scene { margin-bottom: 40px; background: #2a2a2a; padding: 20px; border-radius: 8px; }",
        ".candidates { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); ",
        "              gap: 20px; margin-top: 20px; }",
        ".candidate { background: #333; padding: 15px; border-radius: 8px; text-align: center; }",
        ".candidate.winner { border: 3px solid #4a9eff; background: #1a3a5a; }",
        ".candidate img { max-width: 100%; height: auto; border-radius: 4px; ",
        "                 box-shadow: 0 4px 8px rgba(0,0,0,0.3); }",
        ".candidate-label { font-weight: bold; color: #4a9eff; margin-bottom: 10px; font-size: 18px; }",
        ".candidate.winner .candidate-label { color: #7cb342; }",
        ".path { font-size: 11px; color: #888; margin-top: 8px; word-break: break-all; }",
        ".no-video { padding: 40px; background: #444; border-radius: 4px; color: #999; }",
        ".instructions { background: #2a3a4a; padding: 20px; border-radius: 8px; margin-bottom: 30px; ",
        "                border-left: 4px solid #4a9eff; }",
        ".instructions code { background: #1a2a3a; padding: 2px 6px; border-radius: 3px; ",
        "                     color: #7cb342; font-family: 'Monaco', 'Courier New', monospace; }",
        "</style>",
        "</head><body>",
        f"<h1>Candidate Review: {cut_id}</h1>",
        "<div class='instructions'>",
        "<strong>How to use:</strong><br>",
        "1. Review candidates for each scene below<br>",
        "2. Note which candidate index you prefer (1-based)<br>",
        f"3. Edit <code>episodes/&lt;ep&gt;/renders/selections/{cut_id}.yaml</code><br>",
        "4. Set <code>winner_index: N</code> for each scene<br>",
        "5. Re-run <code>compile_cut.py</code> without <code>--candidates-only</code> to generate final cut",
        "</div>",
    ]

    for ep_sel in episode_selections:
        ep_id = ep_sel["episode_id"]
        scenes = ep_sel["scenes"]

        html_parts.append(f"<div class='episode'>")
        html_parts.append(f"<h2>Episode: {ep_id}</h2>")

        for scene_id, scene_data in scenes.items():
            winner_idx = scene_data.get("winner_index", 1)
            candidates = scene_data.get("candidates", [])

            html_parts.append(f"<div class='scene'>")
            html_parts.append(f"<h3>Scene: {scene_id}</h3>")
            html_parts.append(f"<div class='candidates'>")

            for cand in candidates:
                idx = cand["index"]
                rel_path = cand["path"]
                video_path = PROJECT_ROOT / rel_path
                is_winner = idx == winner_idx

                winner_class = " winner" if is_winner else ""
                html_parts.append(f"<div class='candidate{winner_class}'>")

                label = f"Candidate {idx}"
                if is_winner:
                    label += " ⭐ (Current Winner)"
                html_parts.append(f"<div class='candidate-label'>{label}</div>")

                # Extract thumbnail
                thumb = extract_thumbnail(video_path)
                if thumb:
                    html_parts.append(f"<img src='{thumb}' alt='Candidate {idx}'>")
                else:
                    html_parts.append(f"<div class='no-video'>Video not found or could not extract frame</div>")

                html_parts.append(f"<div class='path'>{rel_path}</div>")
                html_parts.append(f"</div>")

            html_parts.append("</div>")  # end candidates grid
            html_parts.append("</div>")  # end scene

        html_parts.append("</div>")  # end episode

    html_parts.append("</body></html>")

    # Save HTML
    output_path = PROJECT_ROOT / "output" / "cuts" / cut_id / "review.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(html_parts), encoding="utf-8")
    print(f"[REVIEW] Contact sheet: {output_path}")


def build_episode_selections(cut_manifest_path: Path) -> list[Path]:
    manifest = load_json(cut_manifest_path)
    cut_id = manifest["cut_id"]
    recipe = manifest.get("recipe_snapshot", {})
    scope = recipe.get("scope") or {}
    include_eps = scope.get("include_episodes") or []

    selections_files: list[Path] = []
    episode_selections: list[dict[str, Any]] = []

    for ep in include_eps:
        ep_manifest_path = PROJECT_ROOT / "episodes" / ep / "episode.yaml"
        if not ep_manifest_path.exists():
            print(f"[WARN] Episode manifest not found: {ep_manifest_path}")
            continue
        ep_manifest = load_yaml(ep_manifest_path)
        scenes = ep_manifest.get("scenes") or []

        out_doc: dict[str, Any] = {"episode_id": ep, "cut_id": cut_id, "scenes": {}}
        for scene in scenes:
            sid = scene.get("id", "scene")
            cand_dir = PROJECT_ROOT / "output" / "tmp" / cut_id / ep / sid
            cand_meta = cand_dir / "candidates.json"
            candidates: list[dict[str, Any]] = []
            if cand_meta.exists():
                try:
                    meta = load_json(cand_meta)
                    candidates = meta.get("candidates") or []
                except Exception:
                    candidates = []
            # Default winner_index = 1; include candidates list for reference
            out_doc["scenes"][sid] = {
                "winner_index": 1,
                "candidates": candidates,
            }

        sel_path = PROJECT_ROOT / "episodes" / ep / "renders" / "selections" / f"{cut_id}.yaml"
        save_yaml(sel_path, out_doc)
        selections_files.append(sel_path)
        episode_selections.append(out_doc)
        print(f"[SELECT] Wrote selections template: {sel_path}")

    # Generate HTML contact sheet for visual review
    if episode_selections:
        generate_contact_sheet(cut_id, episode_selections)

    return selections_files


def main() -> None:
    p = argparse.ArgumentParser(description="Generate per-episode selections YAML from cut candidates.")
    p.add_argument(
        "--cut-manifest",
        required=True,
        help="Path to output/cuts/<id>/manifest/cut.manifest.json generated with --candidates-only",
    )
    args = p.parse_args()
    build_episode_selections(Path(args.cut_manifest))


if __name__ == "__main__":
    main()
