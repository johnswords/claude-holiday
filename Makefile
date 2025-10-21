# Holiday Media Project Makefile

.DEFAULT_GOAL := help
.PHONY: help install sync dev test lint format typecheck clean build run-tests coverage

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Holiday Media Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Quick Start:$(NC)"
	@echo "  make preflight  # Check all prerequisites"
	@echo "  make install    # Set up development environment"
	@echo "  make test       # Run tests"
	@echo "  make lint       # Check code quality"

preflight: ## Check all required dependencies (Python, uv, FFmpeg)
	@echo "$(BLUE)Checking prerequisites...$(NC)"
	@echo ""
	@echo -n "Python 3.11+: "
	@python3 --version 2>/dev/null | grep -E 'Python 3\.(1[1-9]|[2-9][0-9])' > /dev/null && echo "$(GREEN)✓$(NC)" || (echo "$(RED)✗ (Python 3.11+ required)$(NC)" && exit 1)
	@echo -n "uv package manager: "
	@uv --version > /dev/null 2>&1 && echo "$(GREEN)✓$(NC)" || (echo "$(RED)✗ (install: curl -LsSf https://astral.sh/uv/install.sh | sh)$(NC)" && exit 1)
	@echo -n "FFmpeg: "
	@ffmpeg -version > /dev/null 2>&1 && echo "$(GREEN)✓$(NC)" || (echo "$(RED)✗ (install: brew install ffmpeg or apt install ffmpeg)$(NC)" && exit 1)
	@echo ""
	@echo "$(GREEN)✓ All prerequisites met!$(NC)"
	@echo "$(YELLOW)Next step: make install$(NC)"

install: ## Install project with all dependencies using uv
	@echo "$(BLUE)Installing project with uv...$(NC)"
	uv sync --all-groups
	@echo "$(GREEN)✓ Installation complete$(NC)"

sync: ## Sync dependencies to match pyproject.toml/lockfile
	@echo "$(BLUE)Syncing dependencies...$(NC)"
	uv sync
	@echo "$(GREEN)✓ Dependencies synced$(NC)"

dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	uv sync --group dev
	@echo "$(GREEN)✓ Dev dependencies installed$(NC)"

test: ## Run tests with pytest
	@echo "$(BLUE)Running tests...$(NC)"
	uv run pytest

lint: ## Run ruff linter
	@echo "$(BLUE)Running linter...$(NC)"
	uv run ruff check scripts tests
	@echo "$(GREEN)✓ Linting complete$(NC)"

format: ## Format code with ruff
	@echo "$(BLUE)Formatting code...$(NC)"
	uv run ruff format scripts tests
	@echo "$(GREEN)✓ Formatting complete$(NC)"

typecheck: ## Run type checking with mypy
	@echo "$(BLUE)Running type checker...$(NC)"
	uv run mypy scripts
	@echo "$(GREEN)✓ Type checking complete$(NC)"

clean: ## Clean up build artifacts and cache
	@echo "$(BLUE)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf dist/ build/ *.egg-info 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

build: ## Build distribution packages
	@echo "$(BLUE)Building packages...$(NC)"
	uv build
	@echo "$(GREEN)✓ Build complete$(NC)"

coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	uv run pytest --cov=scripts --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)✓ Coverage report generated$(NC)"
	@echo "Open htmlcov/index.html to view detailed report"

# Script commands
new-cut: ## Create a new cut
	uv run python -m scripts.new_cut

compile-cut: ## Compile a cut
	uv run python -m scripts.compile_cut

apply-overlays: ## Apply overlays to video
	uv run python -m scripts.apply_overlays

pack-release: ## Pack a release
	uv run python -m scripts.pack_release

select-winners: ## Select winners
	uv run python -m scripts.select_winners

# Development workflow commands
check: lint typecheck test ## Run all checks (lint, typecheck, test)
	@echo "$(GREEN)✓ All checks passed$(NC)"

fix: format ## Auto-fix code issues
	@echo "$(GREEN)✓ Code fixes applied$(NC)"

update: ## Update all dependencies to latest versions
	@echo "$(BLUE)Updating dependencies...$(NC)"
	uv lock --upgrade
	uv sync
	@echo "$(GREEN)✓ Dependencies updated$(NC)"

# Virtual environment management
venv: ## Activate virtual environment (informational)
	@echo "$(YELLOW)To activate the virtual environment:$(NC)"
	@echo "  source .venv/bin/activate"
	@echo ""
	@echo "$(YELLOW)Or run commands through uv:$(NC)"
	@echo "  uv run python script.py"

python: ## Launch Python REPL with project environment
	uv run python

shell: ## Launch shell with project environment
	uv run bash