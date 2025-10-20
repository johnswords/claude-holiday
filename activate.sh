#!/usr/bin/env bash
# Activation script for holiday-media project using uv

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Holiday Media Development Environment${NC}"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${RED}✗ uv is not installed!${NC}"
    echo "Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    uv sync
fi

# Activate virtual environment
source .venv/bin/activate

# Display status
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo -e "Python: $(which python)"
echo -e "Version: $(python --version)"
echo ""
echo -e "${YELLOW}Available commands:${NC}"
echo "  make help       # Show all available commands"
echo "  make test       # Run tests"
echo "  make lint       # Check code quality"
echo "  make format     # Format code"
echo "  deactivate      # Exit virtual environment"
echo ""
echo -e "${BLUE}Happy coding!${NC}"