---
name: md-workflow
description: Use when molecular dynamics jobs need to be planned from prepared receptors, ligands, docking outputs, or selected protein-ligand systems.
---

> **Requires SciAgentKit Enterprise.** The docking, MD, trajectory, hit-ranking, wet-lab and report tools this skill relies on are part of SciAgentKit Enterprise (https://sciagentkit.com). If they are not in your tool list, run only the free steps, tell the user the rest requires Enterprise, and never simulate the missing results.


# SciAgentKit MD workflow planning

Preferred MCP tool: `md_plan`.
Preferred CLI fallback:
```bash
sciagent md-plan <complex_or_protein.pdb> <top_ligands.csv> --ns 1 --out runs/<target>/md
```

Workflow:
1. Use top docked ligands selected by total count or top fraction.
2. If top ligand count is small, use 3 replicas with different seeds.
3. Use neutralization and 0.15 M salt defaults unless user specifies otherwise.
4. Create OpenMM job folders and scripts; do not claim MD was completed until trajectories exist.
5. Ask force-field choice if not known: recommended literature/default option versus user-specified force field.

## Output rules
- Save all outputs under `runs/` unless the user gives another safe project-relative path.
- Preserve `run_manifest.json`.
- Report exact generated files.
- If an external binary or Python package is missing, report it clearly and continue with the safest available fallback.
- Never invent molecular descriptors, UniProt/PDB metadata, docking scores, RMSD/RMSF values, or interaction frequencies.
