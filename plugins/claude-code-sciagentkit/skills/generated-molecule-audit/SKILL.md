---
name: generated-molecule-audit
description: Use when evaluating generated, AI-designed, RL-designed, or proposed molecules against training, reference, known-active, or baseline molecule sets.
---

# SciAgentKit generated molecule audit

Use this when the user has generated molecules plus a training/reference/known-active set.

Preferred MCP tool: `audit_generated_library`.
Preferred CLI fallback:
```bash
sciagent audit-generated <generated.smi-or-csv> <reference.smi-or-csv> --out runs/<audit_name>
```

Workflow:
1. Confirm/generated and reference files.
2. Run generated molecule audit.
3. Inspect `novelty_report.csv`, `cross_duplicates.csv`, `novel_query_molecules.csv`, `descriptor_comparison.csv`, `scaffold_comparison.csv`, `figures/`, `report.md`.
4. Report molecule-level novelty separately from scaffold-level novelty.
5. Warn if novelty is high but scaffold novelty is low.

## Output rules
- Save all outputs under `runs/` unless the user gives another safe project-relative path.
- Preserve `run_manifest.json`.
- Report exact generated files.
- If an external binary or Python package is missing, report it clearly and continue with the safest available fallback.
- Never invent molecular descriptors, UniProt/PDB metadata, docking scores, RMSD/RMSF values, or interaction frequencies.
