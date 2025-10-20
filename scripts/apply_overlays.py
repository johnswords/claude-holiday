from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def _pos_to_xy(position: str, width: int, height: int, pad: int = 12) -> tuple[str, str]:
    # Returns ffmpeg expressions for x,y
    if position == "top_left":
        return f"{pad}", f"{pad}"
    if position == "top_right":
        return f"w-tw-{pad}", f"{pad}"
    if position == "bottom_left":
        return f"{pad}", f"h-th-{pad}"
    if position == "bottom_right":
        return f"w-tw-{pad}", f"h-th-{pad}"
    # default
    return f"{pad}", f"{pad}"


def parse_overlay_spec(spec_path: Path) -> dict[str, Any]:
    with open(spec_path, encoding="utf-8") as f:
        return json.load(f)


def build_filters(
    overlays: list[dict[str, Any]],
    width: int,
    height: int,
    font_path: str | None = None,
) -> str:
    """
    Build ffmpeg -vf filtergraph string for simple text overlays with timed enable.
    overlays: list of dicts like:
      {
        "name": "rate_limit_ping",
        "type": "text",
        "text": "HTTP 429",
        "position": "top_right",
        "start_sec": 5.0,
        "duration_sec": 2.0,
        "font_size": 28,
        "font_color": "white",
        "bg_color": "0x333333AA",
        "padding": 12
      }
    """
    filters: list[str] = []
    # Optional background box via drawbox is not text-aware; we rely on drawtext box=1 instead
    for ov in overlays:
        if ov.get("type") != "text":
            continue
        text = ov.get("text", "")
        pos = ov.get("position", "top_right")
        start = float(ov.get("start_sec", 0))
        dur = float(ov.get("duration_sec", 2.0))
        enable = f"between(t\\,{start}\\,{start + dur})"
        size = int(ov.get("font_size", 28))
        color = ov.get("font_color", "white")
        bg = ov.get("bg_color", "0x333333AA")
        pad = int(ov.get("padding", 12))
        x_expr, y_expr = _pos_to_xy(pos, width, height, pad=pad)
        # drawtext supports box=1 and boxcolor for background
        font_opt = f":fontfile={font_path}" if font_path else ""
        # Escape colon and backslash in text
        safe_text = text.replace("\\", "\\\\").replace(":", "\\:")
        flt = (
            f"drawtext=text='{safe_text}'{font_opt}"
            f":x={x_expr}:y={y_expr}:fontsize={size}:fontcolor={color}:box=1:boxcolor={bg}:boxborderw=8"
            f":enable='{enable}'"
        )
        filters.append(flt)
    return ",".join(filters)


def apply_overlays(
    in_path: Path,
    overlays: list[dict[str, Any]],
    out_path: Path,
    width: int,
    height: int,
    font_path: str | None = None,
) -> Path:
    if not overlays:
        # Pass-through copy to avoid re-encode
        # But to ensure consistent output, we re-encode lightly
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(in_path),
            "-c",
            "copy",
            str(out_path),
        ]
        try:
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.stderr:
                print(f"[FFMPEG] {result.stderr}", file=sys.stderr)
        except subprocess.CalledProcessError as e:
            error_msg = f"FFmpeg copy failed: {in_path} -> {out_path}\n"
            error_msg += f"Command: {' '.join(cmd)}\n"
            if e.stderr:
                error_msg += f"Error output:\n{e.stderr}"
            raise RuntimeError(error_msg) from e
        return out_path

    vf = build_filters(overlays, width, height, font_path=font_path)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(in_path),
        "-vf",
        vf,
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
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.stderr:
            print(f"[FFMPEG] {result.stderr}", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        error_msg = f"FFmpeg overlay failed: {in_path} -> {out_path}\n"
        error_msg += f"Command: {' '.join(cmd)}\n"
        if e.stderr:
            error_msg += f"Error output:\n{e.stderr}"
        raise RuntimeError(error_msg) from e
    return out_path


if __name__ == "__main__":
    import argparse
    import sys

    p = argparse.ArgumentParser(description="Apply baked overlays to a video (ffmpeg).")
    p.add_argument("--in", dest="inp", required=True, help="Input MP4 path")
    p.add_argument("--spec", dest="spec", required=True, help="Overlay spec JSON path")
    p.add_argument("--out", dest="out", required=True, help="Output MP4 path")
    p.add_argument("--width", type=int, default=1080)
    p.add_argument("--height", type=int, default=1920)
    p.add_argument("--font", dest="font", default=None, help="Font file path (optional)")
    args = p.parse_args()

    spec = parse_overlay_spec(Path(args.spec))
    result = apply_overlays(
        Path(args.inp),
        [spec],
        Path(args.out),
        width=args.width,
        height=args.height,
        font_path=args.font,
    )
    sys.stdout.write(str(result) + "\n")
