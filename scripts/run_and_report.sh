#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi

TARGET_PATH="${1:-$PROJECT_ROOT}"
TMP_REPORT="/tmp/omni_last_report.txt"

echo "[OMNI] Running format/lint/tests..."
python -m black src tests >/dev/null
python -m ruff check src tests >/dev/null
python -m pytest -q

echo
echo "[OMNI] Running doctor..."
python -m src.terminal.cli doctor | tee "$TMP_REPORT"

echo
echo "[OMNI] Running scan on: $TARGET_PATH"
python -m src.terminal.cli scan "$TARGET_PATH" | tee -a "$TMP_REPORT"

echo
echo "[OMNI] Generating report..."
python -m src.terminal.cli report | tee -a "$TMP_REPORT"

if command -v wl-copy >/dev/null 2>&1; then
  cat "$TMP_REPORT" | wl-copy
  echo
  echo "[OMNI] Copied report output to clipboard via wl-copy."
elif command -v xclip >/dev/null 2>&1; then
  cat "$TMP_REPORT" | xclip -selection clipboard
  echo
  echo "[OMNI] Copied report output to clipboard via xclip."
else
  echo
  echo "[OMNI] Clipboard tool not found. Install one with:"
  echo "sudo apt install -y wl-clipboard"
  echo "or"
  echo "sudo apt install -y xclip"
fi

echo
echo "[OMNI] Combined output saved to: $TMP_REPORT"
echo "[OMNI] Paste that file's contents here when needed."
