# Using SciAgentKit with Claude Code

SciAgentKit should be used in Claude Code as **both** a plugin/skills package and an MCP server.

- Skills decide **which stage** to run: SMILES analysis, generated-molecule audit, literature, protein/PDB selection, ligand preparation, pocket/docking, MD planning, trajectory analysis, or full pipeline.
- MCP tools do the actual computation through SciAgentKit.

## One-command install

```bash
bash scripts/install.sh --full --agents --external --claude-plugin
```

or after SciAgentKit is already installed:

```bash
bash scripts/install_claude_code_plugin.sh
```

Then open Claude Code from the project root:

```bash
claude
```

Inside Claude Code:

```text
/reload-plugins
/plugin list
/mcp
```

## Skill commands

The Claude Code plugin provides:

```text
/sciagentkit:smiles-analysis
/sciagentkit:generated-molecule-audit
/sciagentkit:literature-search
/sciagentkit:protein-structure-selection
/sciagentkit:ligand-preparation
/sciagentkit:pocket-and-docking
/sciagentkit:md-workflow
/sciagentkit:trajectory-analysis
/sciagentkit:report
/sciagentkit:full-target-screening
```

Use natural language after the command. Example:

```text
/sciagentkit:generated-molecule-audit Audit examples/hiv_demo/generated_molecules.smi against examples/hiv_demo/known_actives.smi and save to runs/claude_hiv_audit.
```

## MCP server

The plugin bundles `.mcp.json`. Claude Code starts the SciAgentKit MCP server automatically when the plugin is enabled. The server launcher tries, in order:

1. `SCIAGENTKIT_PYTHON`
2. project `.venv/bin/python`
3. conda env `sciagentkit`
4. system `python3` / `python`

## Important scientific behavior

Claude should never invent molecular descriptors, PDB rankings, docking scores, MD metrics, or ProLIF interactions. It must call SciAgentKit MCP tools or CLI commands and report exact output files.
