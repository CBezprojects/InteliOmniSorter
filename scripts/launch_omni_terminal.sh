#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$HOME/Projects/omni"

cd "$PROJECT_DIR"

if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi

python -m src.terminal.cli shell
