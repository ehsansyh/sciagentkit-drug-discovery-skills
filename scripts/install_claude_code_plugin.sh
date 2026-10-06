#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGIN_SRC="$ROOT_DIR/plugins/claude-code-sciagentkit"
PLUGIN_DST="$HOME/.claude/skills/sciagentkit"

if [[ ! -d "$PLUGIN_SRC" ]]; then
  echo "Plugin source not found: $PLUGIN_SRC" >&2
  exit 1
fi

mkdir -p "$HOME/.claude/skills"
rm -rf "$PLUGIN_DST"
cp -R "$PLUGIN_SRC" "$PLUGIN_DST"

# Make the MCP launcher executable after copy.
chmod +x "$PLUGIN_DST/scripts/start_mcp.sh" || true

cat <<EOF
SciAgentKit Claude Code plugin installed at:
  $PLUGIN_DST

Next:
  1. Start Claude Code in your SciAgentKit project:
       cd "$ROOT_DIR"
       claude

  2. Inside Claude Code:
       /reload-plugins
       /plugin list
       /mcp

  3. Use skills:
       /sciagentkit:smiles-analysis
       /sciagentkit:generated-molecule-audit
       /sciagentkit:protein-structure-selection
       /sciagentkit:ligand-preparation
       /sciagentkit:pocket-and-docking
       /sciagentkit:md-workflow
       /sciagentkit:trajectory-analysis
       /sciagentkit:full-target-screening

The plugin bundles both skills and a SciAgentKit MCP server config.
EOF
