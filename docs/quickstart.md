# Quickstart

```bash
pip install -e '.[dev]'
sciagent demo
```

Analyze one library:

```bash
sciagent analyze-smiles examples/egfr_demo/ligands.smi --out runs/egfr_profile
```

Audit generated molecules:

```bash
sciagent audit-generated examples/hiv_demo/generated_molecules.smi examples/hiv_demo/known_actives.smi --out runs/hiv_audit
```

Start MCP:

```bash
pip install -e '.[mcp]'
python -m sciagentkit.servers.rdkit_server
```
