---
name: literature-search
description: Use when biomedical evidence, citations, target context, mutation evidence, inhibitor evidence, docking precedent, or MD method support is needed.
---

# SciAgentKit literature search

Use this before claims about target biology, known pockets, known ligands, force-field choices, or experimental context.

Preferred MCP tool: `literature_search`.
Preferred CLI fallback:
```bash
sciagent literature-search "<query>" --out runs/<target>/literature
```

Workflow:
1. Build a specific query including target, mutation, disease, pocket, or method.
2. Run literature search.
3. Use returned title/authors/year/PMID/DOI/source fields only.
4. Do not invent citations or conclusions.

## Output rules
- Save all outputs under `runs/` unless the user gives another safe project-relative path.
- Preserve `run_manifest.json`.
- Report exact generated files.
- If an external binary or Python package is missing, report it clearly and continue with the safest available fallback.
- Never invent molecular descriptors, UniProt/PDB metadata, docking scores, RMSD/RMSF values, or interaction frequencies.
