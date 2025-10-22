from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def _pos_to_xy(position: str, _width: int, _height: int, pad: int = 12) -> tuple[str, str]:
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


def _normalize_color(color: str) -> str:
    """
    Convert 0xRRGGBBAA format to #RRGGBB@alpha for better ffmpeg compatibility.
    If color doesn't match 0x format, return as-is (e.g., named colors like 'white').
    """
    if color.startswith("0x") and len(color) == 10:  # 0xRRGGBBAA
        try:
            # Extract components
            hex_str = color[2:]  # Remove '0x'
            r, g, b, a = hex_str[0:2], hex_str[2:4], hex_str[4:6], hex_str[6:8]
            # Convert alpha from 0-255 to 0.0-1.0
            alpha_decimal = int(a, 16) / 255.0
            return f"#{r}{g}{b}@{alpha_decimal:.2f}"
        except (ValueError, IndexError):
            # If parsing fails, return original
            return color
    return color


def _apply_density_timing(start: float, duration: float, density: str) -> tuple[float, float]:
    """
    Adjust overlay timing based on density setting.
    - low: longer duration, more spacing
    - medium: no change (default)
    - high: shorter duration, tighter spacing
    """
    if density == "low":
        return start * 1.3, duration * 1.5
    elif density == "high":
        return start * 0.8, duration * 0.7
    else:  # medium or unrecognized
        return start, duration


def _has_audio_stream(path: Path) -> bool:
    audio_probe = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "a",
        "-show_entries",
        "stream=index",
        "-of",
        "csv=p=0",
        str(path),
    ]

    try:
        probe_result = subprocess.run(
            audio_probe,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        error_msg = f"ffprobe audio detection failed for {path}\n"
        error_msg += f"Command: {' '.join(audio_probe)}\n"
        if e.stderr:
            error_msg += f"Error output:\n{e.stderr}"
        raise RuntimeError(error_msg) from e

    return bool(probe_result.stdout.strip())


def parse_overlay_spec(spec_path: Path) -> dict[str, Any]:
    with open(spec_path, encoding="utf-8") as f:
        return json.load(f)


def build_filters(
    overlays: list[dict[str, Any]],
    width: int,
    height: int,
    font_path: str | None = None,
    density: str = "medium",
    theme: str | None = None,
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
    density: "low" | "medium" | "high" - adjusts timing/spacing of overlays
    theme: color scheme name (reserved for future color palette mapping)
    """
    filters: list[str] = []
    # Note: theme parameter reserved for future color palette implementation
    _ = theme
    # Optional background box via drawbox is not text-aware; we rely on drawtext box=1 instead
    for ov in overlays:
        if ov.get("type") != "text":
            continue
        text = ov.get("text", "")
        pos = ov.get("position", "top_right")
        start_raw = float(ov.get("start_sec", 0))
        dur_raw = float(ov.get("duration_sec", 2.0))
        # Apply density timing adjustments
        start, dur = _apply_density_timing(start_raw, dur_raw, density)
        enable = f"between(t\\,{start}\\,{start + dur})"
        size = int(ov.get("font_size", 28))
        color = ov.get("font_color", "white")
        bg = _normalize_color(ov.get("bg_color", "0x333333AA"))
        pad = int(ov.get("padding", 12))
        x_expr, y_expr = _pos_to_xy(pos, width, height, pad=pad)
        # drawtext supports box=1 and boxcolor for background
        font_opt = f":fontfile={font_path}" if font_path else ""
        # Escape colon, backslash, and single quotes in text
        safe_text = text.replace("\\", "\\\\").replace(":", "\\:").replace("'", r"\'")
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
    density: str = "medium",
    theme: str | None = None,
    fps: int = 24,
) -> Path:
    if not overlays:
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(in_path),
            "-r",
            str(fps),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
        ]

        if _has_audio_stream(in_path):
            cmd.extend(["-c:a", "aac", "-b:a", "128k"])
        else:
            cmd.append("-an")

        cmd.append(str(out_path))

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            if result.stderr:
                print(f"[FFMPEG] {result.stderr}", file=sys.stderr)
        except subprocess.CalledProcessError as e:
            error_msg = f"FFmpeg normalization failed: {in_path} -> {out_path}\n"
            error_msg += f"Command: {' '.join(cmd)}\n"
            if e.stderr:
                error_msg += f"Error output:\n{e.stderr}"
            raise RuntimeError(error_msg) from e
        return out_path

    vf = build_filters(overlays, width, height, font_path=font_path, density=density, theme=theme)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(in_path),
        "-vf",
        vf,
        "-r",
        str(fps),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
    ]

    if _has_audio_stream(in_path):
        cmd.extend(["-c:a", "aac", "-b:a", "128k"])
    else:
        cmd.append("-an")

    cmd.append(str(out_path))
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stderr:
            print(f"[FFMPEG] {result.stderr}", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        error_msg = f"FFmpeg overlay failed: {in_path} -> {out_path}\n"
        error_msg += f"Command: {' '.join(cmd)}\n"
        if e.stderr:
            error_msg += f"Error output:\n{e.stderr}"
        raise RuntimeError(error_msg) from e
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Apply baked overlays to a video (ffmpeg).")
    parser.add_argument("--in", dest="inp", required=True, help="Input MP4 path")
    parser.add_argument("--spec", dest="spec", required=True, help="Overlay spec JSON path")
    parser.add_argument("--out", dest="out", required=True, help="Output MP4 path")
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1920)
    parser.add_argument("--font", dest="font", default=None, help="Font file path (optional)")
    parser.add_argument(
        "--density",
        choices=["low", "medium", "high"],
        default="medium",
        help="Overlay density",
    )
    parser.add_argument("--theme", default=None, help="Color theme (optional)")
    parser.add_argument("--fps", type=int, default=24, help="Output frames per second")
    args = parser.parse_args(argv)

    spec = parse_overlay_spec(Path(args.spec))
    overlays: list[dict[str, Any]] = spec["overlays"] if isinstance(spec.get("overlays"), list) else [spec]

    result = apply_overlays(
        Path(args.inp),
        overlays,
        Path(args.out),
        width=args.width,
        height=args.height,
        font_path=args.font,
        density=args.density,
        theme=args.theme,
        fps=args.fps,
    )
    sys.stdout.write(f"{result}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
