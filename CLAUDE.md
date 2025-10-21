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
