# Migration to uv - Complete ✅

This project has been successfully migrated from pip/requirements.txt to **uv**, a modern Python package manager that's 10-100x faster than pip.

## What Changed

### New Files Added
- **`pyproject.toml`** - Modern Python project configuration with all dependencies
- **`uv.lock`** - Deterministic lock file for reproducible installs
- **`Makefile`** - Developer commands and shortcuts
- **`activate.sh`** - Optional activation script for the virtual environment

### Updated Files
- **`.gitignore`** - Added uv-specific entries (uv.lock, .ruff_cache/, etc.)
- **`README.md`** - Updated all commands to use uv instead of pip
- **Scripts** - Auto-formatted and linted with ruff

### Old Files (Can Be Removed)
- **`requirements.txt`** - Kept for backwards compatibility, but no longer needed

## Benefits of This Migration

1. **Speed**: Dependencies install 10-100x faster
2. **Reliability**: Lock file ensures everyone gets exact same versions
3. **Simplicity**: Single tool replaces pip, virtualenv, pip-tools
4. **Modern Tooling**: Integrated with ruff for linting/formatting, mypy for type checking
5. **Better DX**: Simple `make` commands for common tasks

## Quick Start for Developers

```bash
# One-time setup
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project
uv sync

# Run tests
make test

# Run any script
uv run python -m scripts.compile_cut --recipe recipes/my-cut.yaml
```

## For Existing Contributors

If you have an existing clone with pip/virtualenv:

```bash
# Remove old virtual environment
rm -rf venv/ env/ .venv/

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Reinstall with uv
uv sync

# You're ready to go!
```

## Backwards Compatibility

The old `requirements.txt` file is still present for anyone who needs it, but we recommend switching to uv for the best experience.

## Development Workflow

### Common Commands

```bash
make help        # Show all available commands
make install     # Install everything
make test        # Run tests
make lint        # Check code quality
make format      # Auto-format code
make clean       # Clean up artifacts
```

### Running Scripts

Three ways to run scripts:

```bash
# 1. Through uv (recommended)
uv run python -m scripts.compile_cut

# 2. Activate venv first
source .venv/bin/activate
python -m scripts.compile_cut

# 3. Use Makefile shortcuts
make compile-cut
```

## Technical Details

- **Python Version**: 3.11+ required
- **Package Name**: `holiday-media` (avoiding name conflicts with validator)
- **Build System**: hatchling
- **Development Tools**: pytest, ruff, mypy, coverage
- **Dependencies**: PyYAML, blake3, pysubs2

## Questions?

The migration is complete and tested. All existing functionality works as before, just faster and more reliably.

For uv documentation, see: https://docs.astral.sh/uv/