# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Claude Holiday** is a community-composable media project — an 11-episode vertical micro-series parodying Hallmark holiday rom-coms through the lens of AI companionship. Each episode runs 25 seconds all-in (includes 1s title card). The unique innovation is that there's no single canonical version: each "cut" (compiled interpretation) is equally valid and gets a deterministic Cut URI for reference.

**Core Philosophy:**
- Config-driven compilation via RCFC (Recipe-Cut Format Configuration) YAML recipes
- Reproducible by design — same recipe + commit = same Cut URI
- Community remixing IS the medium — fork, edit YAML, compile, publish
- Two modes: content creators (make episodes) and timeline creators (assemble cuts)

## Development Setup

This project uses **uv** for Python dependency management (10-100x faster than pip).

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- FFmpeg (for video processing)

### Installation
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies (creates .venv automatically)
uv sync

# Install dev dependencies
uv sync --group dev

# Enable git hooks (installs pre-commit-managed lint/type/test checks)
uv run pre-commit install
```

### Running Commands
```bash
# Option 1: Use the unified CLI
./ch compile --recipe recipes/prime-2025.yaml
./ch candidates --recipe <recipe>
./ch select --cut-manifest <manifest>
./ch bundle --cut-manifest <manifest>
./ch ytmeta --cut-manifest <manifest>
./ch cover-art --type all

# Option 2: Use uv directly
uv run python -m scripts.compile_cut --recipe <recipe>
uv run python -m scripts.apply_overlays --input <video>
uv run python -m scripts.pack_release --cut-manifest <manifest>

# Option 3: Use Makefile shortcuts
make test          # Run pytest
make lint          # Run ruff linter
make format        # Auto-format with ruff
make typecheck     # Run mypy
make coverage      # Generate coverage report
make clean         # Remove build artifacts
```

## Architecture

### Key Concepts

**RCFC Recipe (Recipe-Cut Format Configuration):**
- YAML files in `recipes/` that define how to compile a cut
- Specifies episodes, overlays, audience, provider, render settings
- Schema validated against `schemas/rcfc.schema.json`
- Deterministic: same recipe = same Cut URI

**Cut URI:**
- Format: `chcut://{commit_sha}/{rcfc_hash}?audience={profile}&v=0.1`
- BLAKE3 hash of canonicalized recipe (excluding `source.commit_sha`)
- Stable reference for sharing variants
- See `docs/specs/cut-uri.md` for details

**Providers:**
- `prebaked`: Uses existing rendered clips from `episodes/*/renders/final/`
- `dummy`: Generates solid-color placeholder clips via FFmpeg (no API keys needed)
- `sora`: Future support for Sora-2-Pro video generation (requires OpenAI API key)

**Audience Profiles:**
- `dev`: Developer-focused overlays with technical glossary captions
- `general`: General audience with accessible language
- Config files: `scripts/config/audience.{profile}.yaml`

**Overlays:**
- Applied via FFmpeg drawtext filters during compilation
- Density settings: `low`, `medium`, `high` (affects timing and spacing)
- Theme colors normalized from `0xRRGGBBAA` format to `#RRGGBB@alpha`

### Directory Structure

```
claude_holiday/
├── episodes/              # Per-episode production workspace
│   ├── ep00_checking_in/
│   │   ├── episode.yaml   # Episode manifest (scenes, timing, dialogue)
│   │   ├── prompts/       # Sora-2-Pro generation prompts
│   │   ├── renders/       # Video renders (drafts, final, selections)
│   │   └── assets/        # Episode-specific resources
│   └── ... (ep01-11)
├── recipes/               # RCFC recipe files
│   └── examples/          # Example recipes to fork
├── scripts/               # Python automation tools
│   ├── compile_cut.py     # Main recipe compiler
│   ├── apply_overlays.py  # FFmpeg overlay engine
│   ├── pack_release.py    # Bundle releases
│   ├── select_winners.py  # Generate selection templates
│   ├── generate_cover_art.py  # AI cover art generation
│   ├── providers/         # Video provider implementations
│   ├── rcfc/              # Cut URI utilities
│   └── config/            # Audience/series/endings config
├── output/                # Compilation outputs
│   ├── cuts/              # Compiled cuts with manifests
│   ├── episodes/          # Final episode videos
│   ├── releases/          # ZIP bundles
│   └── cover_art/         # Generated cover art assets
├── schemas/               # JSON schema for RCFC validation
├── assets/                # Shared fonts, audio, templates
└── ch                     # Unified CLI entry point
```

### Code Architecture

**Compilation Pipeline (`scripts/compile_cut.py`):**
1. Load and validate RCFC recipe against JSON schema
2. Resolve provider (prebaked/dummy/sora)
3. Load episode manifests from `episodes/*/episode.yaml`
4. Generate or fetch video clips per scene
5. Apply winner selections if available (`episodes/*/renders/selections/<cut_id>.yaml`)
6. Stitch scenes with FFmpeg
7. Apply overlays (density-adjusted timing, color normalization)
8. Generate captions/subtitles
9. Save cut manifest with Cut URI

**Candidate Review Workflow:**
1. `./ch candidates` — Generate multiple renders per scene (no stitching)
2. `./ch select` — Create selection YAML templates + HTML contact sheet
3. Edit YAMLs to set `winner_index` (1-based) per scene
4. `./ch compile` — Recompile using winner selections

**Provider Interface (`scripts/providers/base.py`):**
- Abstract `Provider` class with `render()` method
- `RenderConfig` dataclass for render parameters
- Implementations: `PrebakedProvider`, `DummyProvider`, `SoraProvider`

**Overlay Engine (`scripts/apply_overlays.py`):**
- FFmpeg drawtext filter chain builder
- Position calculations (`top_left`, `top_right`, etc.)
- Color normalization (`0xRRGGBBAA` → `#RRGGBB@alpha`)
- Density-based timing adjustments
- Audio stream detection and preservation

## Common Development Tasks

### Create a New Cut
```bash
# Copy example recipe
cp recipes/examples/general-default.yaml recipes/my-cut.yaml

# Edit YAML (episodes, overlays, audience, provider)
# ... edit recipes/my-cut.yaml ...

# Compile
./ch compile --recipe recipes/my-cut.yaml

# Find your Cut URI in:
# output/cuts/<cut_id>/manifest/cut.manifest.json
```

### Generate Cover Art (Requires OPENAI_API_KEY)
```bash
export OPENAI_API_KEY="your-key-here"
./ch cover-art --type all
# Outputs: thumbnails, banners, title cards, social media assets
# Location: output/cover_art/
```

### Review Candidates Before Final Compile
```bash
# Generate candidates
./ch candidates --recipe recipes/my-cut.yaml
# Note the cut_id from output

# Create selection templates + HTML review sheet
./ch select --cut-manifest output/cuts/<cut_id>/manifest/cut.manifest.json
# Open: output/cuts/<cut_id>/review.html

# Edit selection YAMLs (set winner_index)
# Location: episodes/*/renders/selections/<cut_id>.yaml

# Recompile with selections
./ch compile --recipe recipes/my-cut.yaml
```

### Run Tests and Linting
```bash
make test        # Run full test suite
make lint        # Check code quality
make format      # Auto-format code
make typecheck   # Type checking with mypy
make coverage    # Coverage report
make check       # All checks (lint + typecheck + test)
```

### Bundle for Release
```bash
./ch bundle --cut-manifest output/cuts/<cut_id>/manifest/cut.manifest.json
# Creates: output/releases/ClaudeHoliday_<cut_id>.zip
# Includes: videos, manifests, metadata, recipe snapshot
```

## Important Notes

### FFmpeg Dependencies
- Overlays use FFmpeg drawtext filters
- Font paths: defaults to `/System/Library/Fonts/Supplemental/Arial Unicode.ttf` on macOS
- Audio stream detection: `ffprobe` used to check for audio before processing
- Preflight checks: FFmpeg/FFprobe availability validated before compilation

### RCFC Schema Validation
- All recipes validated against `schemas/rcfc.schema.json` before compilation
- Validation errors include path, schema requirement, and provided value
- Required fields: `schema_version`, `metadata`, `audience_profile`, `scope`, `render`, `provider`

### Episode Manifests
- YAML files at `episodes/*/episode.yaml`
- Define scenes, dialogue, timing, camera directions
- Used by providers to generate or fetch clips
- Not part of RCFC recipe (content vs. configuration separation)

### Winner Selections
- Path pattern: `episodes/<ep_id>/renders/selections/<cut_id>.yaml`
- Winner index is 1-based (1 = first candidate, 2 = second, etc.)
- Default: `winner_index: 1` for all scenes
- Applied automatically during compilation if files exist

### Git Workflow
- Project uses standard git workflow (no special branch requirements)
- Commit SHA included in Cut URI for reproducibility
- Recipe `source.commit_sha` can be "HEAD" for active development

## Code Quality Standards

### Python Style
- Target: Python 3.11+
- Linter: ruff (configured in `pyproject.toml`)
- Type checking: mypy with `check_untyped_defs`
- Formatter: ruff format (120 char line length)
- Line ending: auto-detected

### Testing
- Framework: pytest
- Test location: `tests/`
- Run: `make test` or `uv run pytest`
- Coverage: `make coverage` (outputs to `htmlcov/`)

### Type Hints
- Use `from __future__ import annotations` for forward references
- Type all function signatures
- Use `dict[str, Any]` for flexible structures
- Mypy strict mode enabled

## References

- **RCFC Spec**: `docs/specs/rcfc.md`
- **Cut URI Spec**: `docs/specs/cut-uri.md`
- **Community Charter**: `docs/charter.md`
- **Full Script**: `docs/master_script.md`
- **Example Recipes**: `recipes/examples/`
- **JSON Schema**: `schemas/rcfc.schema.json`

## CLI Command Reference

```bash
ch compile --recipe <path>              # Compile cut from recipe
ch candidates --recipe <path>           # Generate candidates (no stitch)
ch select --cut-manifest <path>         # Create selection templates
ch bundle --cut-manifest <path>         # Pack release bundle
ch ytmeta --cut-manifest <path>         # Generate YouTube metadata
ch cover-art [--type all|thumbnail|...] # Generate cover art (OPENAI_API_KEY)
```

See `./ch --help` or `./ch <command> --help` for detailed usage.
# Claude Holiday — Developer Guide

This document provides technical context for working on the Claude Holiday project.

## Dependency Management

This project uses **uv** for Python dependency management. All dependencies are declared in `pyproject.toml`.

### Why uv?

- **Fast**: 10-100x faster than pip
- **Deterministic**: Lock file ensures reproducible builds
- **Simple**: One tool replaces pip, virtualenv, pip-tools
- **Cross-platform**: Consistent behavior everywhere

### Core Dependencies

**Production (runtime):**
- `PyYAML>=6.0.2` — RCFC recipe parsing and episode manifests
- `blake3>=0.4.1` — Fast, cryptographically-secure cut URI hashing
- `pysubs2>=1.6.1` — Caption and subtitle generation
- `jsonschema>=4.23.0` — Recipe validation (critical for runtime)
- `openai>=1.0.0` — Sora-2-Pro video generation API

**Development (optional):**
- `pytest>=7.4.3` — Test framework
- `pytest-cov>=4.1.0` — Code coverage reporting
- `ruff>=0.8.6` — Fast Python linter and formatter
- `mypy>=1.11.2` — Static type checking
- `types-PyYAML` — Type stubs for PyYAML

### Common Commands

```bash
# Install all dependencies
uv sync

# Install with dev dependencies
uv sync --group dev

# Add a new production dependency
uv add package-name

# Add a new dev dependency
uv add --group dev package-name

# Update all dependencies
uv sync --upgrade

# Run scripts via uv
uv run python -m scripts.compile_cut --recipe recipes/my-cut.yaml

# Activate the virtual environment (optional)
source .venv/bin/activate
```

### External Dependencies

**FFmpeg** (required for video processing):
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Verify installation
ffmpeg -version
```

## Project Structure

```
claude_holiday/
├── pyproject.toml          # Dependency definitions, build config, tool settings
├── uv.lock                 # Locked dependency versions (committed to git)
├── .venv/                  # Virtual environment (auto-created by uv)
├── requirements.txt        # Reference only (deprecated, use pyproject.toml)
├── scripts/                # Python modules for cut compilation
│   ├── compile_cut.py      # Main recipe compiler
│   ├── apply_overlays.py   # Overlay engine
│   └── ...
├── recipes/                # RCFC recipe files
├── episodes/               # Per-episode production workspaces
└── output/                 # Generated cuts and releases
```

## Development Workflow

1. **Setup**: `uv sync`
2. **Make changes**: Edit code, add features
3. **Test**: `make test` or `uv run pytest`
4. **Lint**: `make lint` or `uv run ruff check .`
5. **Format**: `make format` or `uv run ruff format .`
6. **Type check**: `make typecheck` or `uv run mypy scripts/`

## Recipe Validation

The `jsonschema` dependency is **critical** for validating RCFC recipes at runtime. Without it:
- Recipe parsing will fail
- No validation of user-provided YAML
- Silent errors in malformed recipes

The schema is defined in `scripts/` and validates:
- Episode lists and identifiers
- Overlay configurations
- Provider options (prebaked vs. sora)
- Timeline metadata

## Sora Integration

The `openai` dependency is required **only** if using the Sora-2-Pro provider for video generation. It's safe to have installed even if using prebaked footage.

API key setup:
```bash
export OPENAI_API_KEY="your-key-here"
```

## Adding New Dependencies

When adding a new dependency, follow this pattern:

```bash
# For runtime dependencies (needed to run the app)
uv add package-name

# For development tools only
uv add --group dev package-name

# Commit both pyproject.toml and uv.lock
git add pyproject.toml uv.lock
git commit -m "Add package-name for <feature>"
```

**Important**: Always commit the `uv.lock` file. It ensures everyone has the same dependency versions.

## Migration from requirements.txt

The project has migrated from `requirements.txt` to `pyproject.toml`:

**Before:**
```bash
pip install -r requirements.txt
```

**After:**
```bash
uv sync
```

The old `requirements.txt` is kept for reference but is no longer the source of truth.

## Troubleshooting

**"Module not found" errors:**
```bash
# Ensure dependencies are installed
uv sync

# Verify you're using the right Python
uv run python --version
```

**"Command not found: uv":**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Reload your shell
source ~/.zshrc  # or ~/.bashrc
```

**Dependency conflicts:**
```bash
# Remove lock file and recreate
rm uv.lock
uv sync
```

## CI/CD Considerations

For GitHub Actions or other CI:

```yaml
- name: Install uv
  run: curl -LsSf https://astral.sh/uv/install.sh | sh

- name: Install dependencies
  run: uv sync

- name: Run tests
  run: uv run pytest
```

uv is designed for CI environments and caches aggressively for fast builds.

---

**Questions?** See the main [README.md](README.md) or open an issue.
