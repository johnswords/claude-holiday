# Troubleshooting Guide

This guide covers common issues you might encounter when working with Claude Holiday and how to resolve them.

---

## FFmpeg Issues

### Issue: `ffmpeg: command not found`

**Cause:** FFmpeg is not installed or not available in your system PATH.

**Solution:**

Install FFmpeg for your platform:

```bash
# macOS (using Homebrew)
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
# Add the bin folder to your system PATH
```

Verify the installation:

```bash
ffmpeg -version
```

---

### Issue: `No such filter: 'drawtext'`

**Cause:** Your FFmpeg build was compiled without libfreetype support, which is required for text overlays.

**Solution:**

Reinstall FFmpeg with full codec support:

```bash
# macOS - Homebrew builds include all filters by default
brew reinstall ffmpeg

# Ubuntu/Debian - install the full version
sudo apt install ffmpeg libavfilter-extra

# Build from source with --enable-libfreetype
./configure --enable-libfreetype --enable-gpl
make && sudo make install
```

Verify drawtext is available:

```bash
ffmpeg -filters 2>/dev/null | grep drawtext
```

You should see output like: `T.. drawtext V->V Draw text on the input video`

---

### Issue: Audio stream detection fails / `ffprobe` errors

**Cause:** FFprobe (part of FFmpeg) is not installed or accessible. The compilation pipeline uses ffprobe to detect whether input videos have audio streams.

**Solution:**

FFprobe is typically installed alongside FFmpeg. Verify it's available:

```bash
ffprobe -version
```

If missing, reinstall FFmpeg completely:

```bash
# macOS
brew reinstall ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

The error message will typically include `ffprobe audio detection failed` with the command that was attempted.

---

### Issue: Video codec errors / `libx264` not found

**Cause:** FFmpeg was compiled without the H.264 encoder (libx264), which is required for MP4 output.

**Solution:**

```bash
# macOS - reinstall with all codecs
brew reinstall ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg libx264-dev

# Verify libx264 is available
ffmpeg -encoders 2>/dev/null | grep libx264
```

Expected output: `V..... libx264 libx264 H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10`

---

## Font Issues

### Issue: Font file not found / Overlay text not rendering

**Cause:** The system cannot locate a suitable font file for FFmpeg's drawtext filter. Claude Holiday searches common paths but may not find fonts on non-standard systems.

**Solution:**

Set the `CH_FONT_PATH` environment variable to point to a valid TrueType font:

```bash
# macOS
export CH_FONT_PATH="/System/Library/Fonts/Supplemental/Arial Unicode.ttf"

# Linux (common paths)
export CH_FONT_PATH="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
# or
export CH_FONT_PATH="/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

# Windows
export CH_FONT_PATH="C:/Windows/Fonts/arial.ttf"
```

Add this to your shell profile (`.bashrc`, `.zshrc`) for persistence.

---

### Issue: Cross-platform font path differences

**Cause:** Font paths vary significantly across operating systems.

**Solution:**

The system automatically searches these paths in order:

| Platform | Default Search Paths |
|----------|---------------------|
| macOS | `/System/Library/Fonts/Supplemental/Arial Unicode.ttf`, `/System/Library/Fonts/Helvetica.ttc`, `/Library/Fonts/Arial.ttf` |
| Linux | `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf`, `/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf`, `/usr/share/fonts/TTF/DejaVuSans.ttf` |
| Windows | `C:/Windows/Fonts/arial.ttf`, `C:/Windows/Fonts/ArialUni.ttf`, `C:/Windows/Fonts/segoeui.ttf` |

If none are found, the system attempts to use `fc-match` (fontconfig) on Unix systems:

```bash
# Test fontconfig fallback
fc-match -f "%{file}" sans
```

---

### Issue: Testing font availability

**Cause:** Unsure which fonts are available on your system.

**Solution:**

```bash
# macOS - list system fonts
ls /System/Library/Fonts/Supplemental/*.ttf 2>/dev/null | head -10

# Linux - use fontconfig
fc-list : file family | head -20

# Windows PowerShell
Get-ChildItem C:\Windows\Fonts\*.ttf | Select-Object -First 10
```

Test a specific font with FFmpeg:

```bash
ffmpeg -f lavfi -i "color=size=640x480:rate=1:color=black" \
  -vf "drawtext=fontfile=/path/to/font.ttf:text='Test':fontsize=48:fontcolor=white:x=100:y=100" \
  -frames:v 1 test_font.png
```

---

## Recipe Validation Errors

### Issue: Schema validation failures

**Cause:** The RCFC recipe YAML is missing required fields or has invalid values. The schema is strictly enforced to ensure reproducibility.

**Solution:**

Check the error message for the specific path and requirement:

```
[VALIDATION ERROR] Recipe validation failed at 'audience_profile': 'tech' is not one of ['general']
Schema requirement: properties.audience_profile.enum
Provided value: tech
```

Compare your recipe against the example:

```bash
# View a working example
cat recipes/prime-2025.yaml
```

Required top-level fields:
- `schema_version` (must be `"0.1.0"`)
- `metadata` (with `title` and `created`)
- `project` (with `name` and `repo_url`)
- `source` (with `commit_sha`)
- `audience_profile` (`"general"`)
- `scope` (with `include_episodes` array)
- `overlays` (with `enabled`, `density`, `theme`)
- `ending` (`"agnostic"` or `"meta"`)
- `captions` (with `track` and `language`)
- `render` (with `fps`, `aspect`, `resolution`)
- `provider` (with `name` and `options`)

---

### Issue: `Invalid audience_profile` - must be "general"

**Cause:** The `audience_profile` field currently only accepts `"general"`.

**Solution:**

```yaml
audience_profile: "general"  # General audience (the default)
```

The profile loads caption tracks and overlay configurations from `scripts/config/audience.general.yaml`.

---

### Issue: Episode not found / Invalid episode_id

**Cause:** The episode ID in `scope.include_episodes` doesn't match an existing episode directory.

**Solution:**

Episode IDs must match directory names in the `episodes/` folder:

```bash
# List available episodes
ls -d episodes/*/

# Example output:
# episodes/ep00_checking_in/
# episodes/ep01_the_prompt/
```

In your recipe:

```yaml
scope:
  include_episodes:
    - "ep00_checking_in"  # Must match directory name exactly
    - "ep01_the_prompt"
```

Each episode directory must contain an `episode.yaml` manifest.

---

### Issue: Provider configuration errors

**Cause:** Invalid provider name or missing required options.

**Solution:**

Valid providers are `prebaked`, `dummy`, or `sora`:

```yaml
# Using dummy provider (for development/testing)
provider:
  name: "dummy"
  options:
    num_candidates: 3

# Using prebaked provider (uses pre-rendered footage)
provider:
  name: "prebaked"
  options: {}

# Using sora provider (requires OPENAI_API_KEY)
provider:
  name: "sora"
  options:
    num_candidates: 1
```

---

## Dependency Issues

### Issue: `ModuleNotFoundError: No module named 'X'`

**Cause:** Python dependencies are not installed or the virtual environment is not activated.

**Solution:**

```bash
# Install all dependencies using uv
uv sync

# For development dependencies (pytest, ruff, mypy)
uv sync --group dev

# Verify installation
uv run python -c "import yaml; import blake3; import jsonschema; print('OK')"
```

---

### Issue: `Command not found: uv`

**Cause:** The uv package manager is not installed.

**Solution:**

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Reload your shell
source ~/.bashrc  # or ~/.zshrc

# Verify installation
uv --version
```

On Windows:

```powershell
# PowerShell
irm https://astral.sh/uv/install.ps1 | iex
```

---

### Issue: Lock file conflicts / dependency resolution errors

**Cause:** The `uv.lock` file is out of sync with `pyproject.toml` or corrupted.

**Solution:**

```bash
# Remove the lock file and regenerate
rm uv.lock
uv sync

# If issues persist, also clear the virtual environment
rm -rf .venv
uv sync
```

---

### Issue: Python version requirements (3.11+)

**Cause:** Claude Holiday requires Python 3.11 or later for modern type hints and features.

**Solution:**

```bash
# Check your Python version
python --version

# Install Python 3.11+ using pyenv (recommended)
pyenv install 3.11.7
pyenv local 3.11.7

# Or use system package manager
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt install python3.11 python3.11-venv

# Then reinitialize the environment
rm -rf .venv
uv sync
```

---

## Sora Provider Issues

### Issue: `OPENAI_API_KEY not set` / `ValueError: OPENAI_API_KEY environment variable is required`

**Cause:** The Sora provider requires an OpenAI API key but none was found.

**Solution:**

```bash
# Set the environment variable
export OPENAI_API_KEY="sk-your-key-here"

# For persistence, add to your shell profile
echo 'export OPENAI_API_KEY="sk-your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

To use a different provider (no API key required):

```yaml
provider:
  name: "dummy"  # or "prebaked"
  options: {}
```

---

### Issue: Rate limits / API throttling

**Cause:** OpenAI's API has rate limits that may be exceeded during high-volume generation.

**Solution:**

The Sora provider automatically falls back to generating placeholder clips when API calls fail. If you're hitting rate limits:

1. Reduce `num_candidates` in your recipe
2. Wait and retry after the rate limit window resets
3. Check your OpenAI account for quota limits
4. Use the `dummy` provider for testing/development

```yaml
provider:
  name: "sora"
  options:
    num_candidates: 1  # Reduce from 3 to 1
```

---

### Issue: Resolution/FPS validation errors

**Cause:** The requested resolution or FPS may not be supported by the Sora API.

**Solution:**

Use standard video specifications:

```yaml
render:
  fps: 24        # Standard: 24, 30, or 60
  aspect: "9:16" # Vertical video
  resolution: "1080x1920"  # Standard mobile vertical
```

Supported resolutions typically include:
- `1080x1920` (vertical HD)
- `720x1280` (vertical 720p)
- `1920x1080` (horizontal HD)

---

## Output Issues

### Issue: Output directory not found / Permission denied

**Cause:** The output directory structure doesn't exist or you don't have write permissions.

**Solution:**

Output directories are auto-created during compilation, but check permissions:

```bash
# Verify you can write to the project directory
touch output/test.txt && rm output/test.txt

# If permission denied, check ownership
ls -la output/

# Fix permissions if needed
chmod -R u+w output/
```

The default output structure:
```
output/
  cuts/{cut_id}/manifest/cut.manifest.json
  episodes/{episode_id}/{episode_id}__{cut_id}.mp4
  tmp/{cut_id}/           # Temporary files during compilation
  releases/               # Bundled releases
```

---

### Issue: Disk space requirements for video output

**Cause:** Video compilation requires significant disk space for intermediate and final files.

**Solution:**

Estimate space requirements:
- Each episode: ~50-200MB depending on duration and quality
- Candidates (if num_candidates > 1): multiply by candidate count
- Temporary files: ~2x final output size during processing

```bash
# Check available space
df -h .

# Clean up temporary files
rm -rf output/tmp/

# Clean up old cuts (preserves manifests)
find output/cuts/ -name "*.mp4" -mtime +7 -delete
```

Minimum recommended: 5GB free space for a single episode compilation with 3 candidates.

---

### Issue: Cut manifest not generated / Compilation appears to hang

**Cause:** Compilation may fail silently or take longer than expected for various reasons.

**Solution:**

1. Check compilation logs for errors:
```bash
./ch compile --recipe recipes/my-cut.yaml 2>&1 | tee compile.log
```

2. Verify input files exist:
```bash
# Check episode manifest exists
ls episodes/ep00_checking_in/episode.yaml

# Check prebaked footage (if using prebaked provider)
ls episodes/ep00_checking_in/renders/final/
```

3. Run with verbose output:
```bash
# Check FFmpeg is being called correctly
PYTHONUNBUFFERED=1 ./ch compile --recipe recipes/my-cut.yaml
```

4. Look for partial outputs:
```bash
# Check if temporary files were created
ls -la output/tmp/

# Check if cut directory was created
ls -la output/cuts/
```

---

## Quick Diagnostic Commands

Run these to diagnose common issues:

```bash
# Check all prerequisites
echo "=== Python ===" && python --version
echo "=== uv ===" && uv --version
echo "=== FFmpeg ===" && ffmpeg -version 2>&1 | head -1
echo "=== FFprobe ===" && ffprobe -version 2>&1 | head -1
echo "=== Dependencies ===" && uv run python -c "import yaml, blake3, jsonschema; print('OK')"
echo "=== Font ===" && uv run python -c "from scripts.utils.fonts import resolve_font; print(resolve_font() or 'NOT FOUND')"
```

---

## Getting Help

If your issue isn't covered here:

1. Search existing GitHub issues
2. Check the [RCFC Spec](specs/rcfc.md) for recipe format details
3. Check the [Cut URI Spec](specs/cut-uri.md) for URI format details
4. Open a new issue with:
   - Your operating system and version
   - Python version (`python --version`)
   - FFmpeg version (`ffmpeg -version | head -1`)
   - The full error message
   - The recipe YAML you're using (redact any API keys)
