#!/usr/bin/env bash
set -euo pipefail

# Start SciAgentKit MCP server for Claude Code.
# Priority:
# 1. SCIAGENTKIT_PYTHON if user explicitly provides it
# 2. project .venv python
# 3. conda env named sciagentkit
# 4. active/system python3 or python

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
export PYTHONPATH="$PROJECT_DIR/src:${PYTHONPATH:-}"

if [[ -n "${SCIAGENTKIT_PYTHON:-}" ]]; then
  exec "$SCIAGENTKIT_PYTHON" -m sciagentkit.servers.rdkit_server
fi

if [[ -x "$PROJECT_DIR/.venv/bin/python" ]]; then
  exec "$PROJECT_DIR/.venv/bin/python" -m sciagentkit.servers.rdkit_server
fi

if command -v conda >/dev/null 2>&1; then
  if conda env list | awk '{print $1}' | grep -qx "sciagentkit"; then
    exec conda run -n sciagentkit python -m sciagentkit.servers.rdkit_server
  fi
fi

if command -v python3 >/dev/null 2>&1; then
  exec python3 -m sciagentkit.servers.rdkit_server
fi

exec python -m sciagentkit.servers.rdkit_server
