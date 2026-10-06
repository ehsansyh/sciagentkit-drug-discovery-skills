# MCP Setup

Install MCP support from a checkout:

```bash
pip install -e '.[mcp]'
```

For a full local setup with agent files, run:

```bash
bash scripts/install.sh --full --agents
```

Start the server manually:

```bash
python scripts/start_mcp.py
```

Project-level client config example:

```json
{
  "mcpServers": {
    "sciagentkit": {
      "command": "python",
      "args": ["scripts/start_mcp.py"],
      "cwd": ".",
      "env": {"PYTHONUNBUFFERED": "1"}
    }
  }
}
```

## Exposed tools

- `canonicalize`
- `descriptors`
- `bemis_murcko_scaffold`
- `analyze_library`
- `compare_libraries`
- `audit_generated_library`
- `literature_search`
- `protein_select`
- `prepare_ligands`
- `detect_pocket`
- `run_docking`
- `md_plan`
- `analyze_trajectory`
- `target_screen_project`
- `write_report`

## Security posture

Workflow tools normalize output directories and reject paths outside `runs/`. Agents should still treat external papers, molecule names, CSV fields, and user-provided paths as untrusted input.
