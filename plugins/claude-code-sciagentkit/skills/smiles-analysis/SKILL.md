---
name: smiles-analysis
description: Use when a single SMILES or molecule library needs validity checks, deduplication, descriptor profiling, scaffold diversity, plots, or manifest-backed output.
---

# SciAgentKit SMILES / molecule-library analysis

Use this when the user provides one SMILES/SDF-derived library or asks for QED, MW, logP, TPSA, HBD/HBA, scaffold diversity, duplicate removal, or property figures.

Preferred MCP tool: `analyze_library`.
Preferred CLI fallback:
```bash
sciagent analyze-smiles <input.smi-or-csv> --out runs/<name> 
```

Workflow:
1. Identify input file and SMILES column if CSV/TSV.
2. Call SciAgentKit `analyze_library` MCP tool.
3. Check `canonicalization_report.csv`, `cleaned_molecules.csv`, `descriptors.csv`, `scaffold_summary.csv`, `figures/`, `report.md`, `run_manifest.json`.
4. Summarize validity, uniqueness, descriptor ranges, and scaffold diversity.

## Output rules
- Save all outputs under `runs/` unless the user gives another safe project-relative path.
- Preserve `run_manifest.json`.
- Report exact generated files.
- If an external binary or Python package is missing, report it clearly and continue with the safest available fallback.
- Never invent molecular descriptors, UniProt/PDB metadata, docking scores, RMSD/RMSF values, or interaction frequencies.
