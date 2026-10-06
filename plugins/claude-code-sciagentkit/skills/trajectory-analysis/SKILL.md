---
name: trajectory-analysis
description: Use when MD trajectory files need RMSD, RMSF, ligand interaction fingerprints, residue summaries, or trajectory-derived report outputs.
---

> **Requires SciAgentKit Enterprise.** The docking, MD, trajectory, hit-ranking, wet-lab and report tools this skill relies on are part of SciAgentKit Enterprise (https://sciagentkit.com). If they are not in your tool list, run only the free steps, tell the user the rest requires Enterprise, and never simulate the missing results.


# SciAgentKit trajectory analysis

Preferred MCP tool: `analyze_trajectory`.
Preferred CLI fallback:
```bash
sciagent analyze-trajectory <topology.pdb> <trajectory.dcd> --prolif-ligand-selection "resname LIG" --out runs/<target>/analysis
```

Workflow:
1. Confirm topology and trajectory files exist.
2. Run RMSD/RMSF analysis.
3. Run ProLIF interaction fingerprint if ligand selection and ProLIF are available.
4. Report interaction frequency by residue and interaction type.

## Output rules
- Save all outputs under `runs/` unless the user gives another safe project-relative path.
- Preserve `run_manifest.json`.
- Report exact generated files.
- If an external binary or Python package is missing, report it clearly and continue with the safest available fallback.
- Never invent molecular descriptors, UniProt/PDB metadata, docking scores, RMSD/RMSF values, or interaction frequencies.
