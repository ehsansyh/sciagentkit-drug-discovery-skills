#!/usr/bin/env bash
set -euo pipefail

# SciAgentKit one-command installer.
# Usage:
#   bash scripts/install.sh --all
#   curl -fsSL https://raw.githubusercontent.com/ehsansyh/sciagentkit-drug-discovery-skills/main/scripts/install_from_github.sh | bash -s -- --all

MODE="core"
ENV_NAME="sciagentkit"
WITH_AGENTS="0"
WITH_EXTERNAL="0"
WITH_CLAUDE_PLUGIN="0"
RUN_TESTS="1"
RUN_DEMO="1"
FORCE_VENV="0"
PYTHON_BIN="python3"

print_help() {
  cat <<'HELP'
SciAgentKit installer

Options:
  --core              Install core molecule-audit stack only. Default.
  --full              Install MCP + protein + docking + MD + report Python dependencies.
  --all               Install full Python stack, agent files, external tools, and Claude Code plugin.
  --dev               Install full stack plus developer/test tools.
  --agents            Generate AGENTS.md, CLAUDE.md, Cursor rule, and MCP config templates.
  --external          Try to install external CLI tools via conda-forge: openbabel, vina, fpocket.
  --claude-plugin     Install SciAgentKit as a Claude Code plugin with skills + bundled MCP.
  --env NAME          Conda/venv environment name. Default: sciagentkit.
  --venv              Force local .venv instead of conda.
  --no-tests          Skip pytest health tests.
  --no-demo           Skip bundled demo run.
  --python PATH       Python executable for venv mode. Default: python3.
  -h, --help          Show this help.

Recommended:
  bash scripts/install.sh --all
HELP
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --core) MODE="core"; shift ;;
    --full) MODE="full"; shift ;;
    --all) MODE="full"; WITH_AGENTS="1"; WITH_EXTERNAL="1"; WITH_CLAUDE_PLUGIN="1"; shift ;;
    --dev) MODE="dev"; shift ;;
    --agents) WITH_AGENTS="1"; shift ;;
    --external) WITH_EXTERNAL="1"; MODE="full"; shift ;;
    --claude-plugin) WITH_CLAUDE_PLUGIN="1"; WITH_AGENTS="1"; shift ;;
    --env) ENV_NAME="$2"; shift 2 ;;
    --venv) FORCE_VENV="1"; shift ;;
    --no-tests) RUN_TESTS="0"; shift ;;
    --no-demo) RUN_DEMO="0"; shift ;;
    --python) PYTHON_BIN="$2"; shift 2 ;;
    -h|--help) print_help; exit 0 ;;
    *) echo "Unknown option: $1"; print_help; exit 1 ;;
  esac
done

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

msg() { printf '\n\033[1;36m%s\033[0m\n' "$1"; }
warn() { printf '\n\033[1;33m%s\033[0m\n' "$1"; }

msg "SciAgentKit installer"
echo "Project: $ROOT_DIR"
echo "Mode:    $MODE"
echo "Env:     $ENV_NAME"

EXTRAS=""
if [[ "$MODE" == "core" ]]; then
  EXTRAS=""
elif [[ "$MODE" == "full" ]]; then
  EXTRAS="[mcp,protein,docking,md,reports]"
elif [[ "$MODE" == "dev" ]]; then
  EXTRAS="[mcp,protein,docking,md,reports,dev]"
else
  echo "Invalid mode: $MODE"; exit 1
fi

USE_CONDA="0"
if [[ "$FORCE_VENV" == "0" ]] && command -v conda >/dev/null 2>&1; then
  USE_CONDA="1"
fi

if [[ "$USE_CONDA" == "1" ]]; then
  msg "Creating/updating conda environment: $ENV_NAME"
  if ! conda env list | awk '{print $1}' | grep -qx "$ENV_NAME"; then
    conda create -n "$ENV_NAME" python=3.11 -y
  fi

  CONDA_INSTALL=(conda install -n "$ENV_NAME" -c conda-forge -y)
  if command -v mamba >/dev/null 2>&1; then
    CONDA_INSTALL=(mamba install -n "$ENV_NAME" -c conda-forge -y)
  fi

  msg "Installing reliable scientific base packages from conda-forge"
  "${CONDA_INSTALL[@]}" \
    pip rdkit pandas numpy matplotlib scikit-learn requests typer rich pydantic pytest

  if [[ "$MODE" != "core" ]]; then
    "${CONDA_INSTALL[@]}" biopython openmm pdbfixer mdanalysis prolif openff-toolkit openmmforcefields || true
  fi

  if [[ "$WITH_EXTERNAL" == "1" ]]; then
    msg "Installing optional external CLI tools from conda-forge"
    CONDA_TOOL_TIMEOUT="${SCIAGENTKIT_CONDA_TIMEOUT:-180}"

    install_external_tool() {
      local package="$1"
      local label="$2"
      local url="$3"
      local cmd=("${CONDA_INSTALL[@]}" --freeze-installed "$package")

      echo "Installing $label ($package)"
      if command -v timeout >/dev/null 2>&1; then
        if timeout "$CONDA_TOOL_TIMEOUT" "${cmd[@]}"; then
          return 0
        fi
      elif "${cmd[@]}"; then
        return 0
      fi

      warn "$label could not be installed automatically."
      warn "Manual install link: $url"
    }

    install_external_tool "openbabel" "Open Babel" "https://openbabel.org/docs/Installation/install.html"
    install_external_tool "vina" "AutoDock Vina" "https://vina.scripps.edu/downloads/"
    install_external_tool "conda-forge::fpocket" "fpocket" "https://github.com/Discngine/fpocket"
  fi

  msg "Installing SciAgentKit package"
  conda run -n "$ENV_NAME" python -m pip install --upgrade pip
  conda run -n "$ENV_NAME" python -m pip install -e ".$EXTRAS"

  RUN_PY=(conda run -n "$ENV_NAME" python)
  RUN_SCI=(conda run -n "$ENV_NAME" sciagent)
  ACTIVATE_HINT="conda activate $ENV_NAME"
else
  msg "Creating/updating local virtual environment: .venv"
  "$PYTHON_BIN" -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  python -m pip install --upgrade pip
  python -m pip install -e ".$EXTRAS"
  RUN_PY=(.venv/bin/python)
  RUN_SCI=(.venv/bin/sciagent)
  ACTIVATE_HINT="source .venv/bin/activate"

  if [[ "$WITH_EXTERNAL" == "1" ]]; then
    warn "External tools requested, but venv mode cannot install system binaries."
    warn "Use conda or install manually: Open Babel https://openbabel.org/docs/Installation/install.html | AutoDock Vina https://vina.scripps.edu/downloads/ | fpocket https://github.com/Discngine/fpocket"
  fi
fi

msg "Writing local helper files"
cat > .sciagentkit.env <<EOT
SCIAGENTKIT_ROOT=$ROOT_DIR
SCIAGENTKIT_MODE=$MODE
SCIAGENTKIT_ENV=$ENV_NAME
SCIAGENTKIT_ACTIVATE=$ACTIVATE_HINT
SCIAGENTKIT_MCP_COMMAND=python -m sciagentkit.servers.rdkit_server
EOT

cat > scripts/activate.sh <<EOT
#!/usr/bin/env bash
cd "$ROOT_DIR"
$ACTIVATE_HINT
EOT
chmod +x scripts/activate.sh

if [[ "$WITH_AGENTS" == "1" ]]; then
  msg "Generating agent/MCP configuration templates"
  "${RUN_PY[@]}" scripts/setup_agents.py --root "$ROOT_DIR" --env-name "$ENV_NAME" --use-conda "$USE_CONDA"
fi

if [[ "$WITH_CLAUDE_PLUGIN" == "1" ]]; then
  msg "Installing Claude Code plugin: skills + MCP"
  bash scripts/install_claude_code_plugin.sh
fi

msg "Running SciAgentKit doctor"
"${RUN_SCI[@]}" doctor || true

if [[ "$RUN_TESTS" == "1" ]]; then
  msg "Running tests"
  if [[ "$USE_CONDA" == "1" ]]; then
    conda run -n "$ENV_NAME" pytest -q
  else
    .venv/bin/pytest -q
  fi
fi

if [[ "$RUN_DEMO" == "1" ]]; then
  msg "Running bundled demo"
  "${RUN_SCI[@]}" demo --out runs/install_demo
fi

msg "Installation complete"
echo "Activate environment: $ACTIVATE_HINT"
echo "Run demo:             sciagent demo"
echo "Start MCP server:     python -m sciagentkit.servers.rdkit_server"
echo "Health check:         sciagent doctor"
echo "External tools:       Open Babel https://openbabel.org/docs/Installation/install.html | AutoDock Vina https://vina.scripps.edu/downloads/ | fpocket https://github.com/Discngine/fpocket"
if [[ "$WITH_AGENTS" == "1" ]]; then
  echo "Agent files:          AGENTS.md, CLAUDE.md, GEMINI.md, .codex/skills, .gemini/skills, .cursor/rules/sciagentkit.mdc, .mcp/sciagentkit.json"
fi
if [[ "$WITH_CLAUDE_PLUGIN" == "1" ]]; then
  echo "Claude plugin:        ~/.claude/skills/sciagentkit"
  echo "Claude skills:        /sciagentkit:generated-molecule-audit, /sciagentkit:full-target-screening"
fi
