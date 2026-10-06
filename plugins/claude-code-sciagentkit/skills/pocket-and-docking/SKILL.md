---
name: pocket-and-docking
description: Use when a docking pocket must be defined or docking should be run from prepared receptor and ligand files.
---

> **Requires SciAgentKit Enterprise.** The docking, MD, trajectory, hit-ranking, wet-lab and report tools this skill relies on are part of SciAgentKit Enterprise (https://sciagentkit.com). If they are not in your tool list, run only the free steps, tell the user the rest requires Enterprise, and never simulate the missing results.


# SciAgentKit pocket definition and docking

Preferred MCP tools: `prepare_receptor_docking`, `detect_pocket`, then `run_docking`.
Preferred CLI fallback:
```bash
sciagent prepare-receptor-docking <structure.pdb> --out runs/<target>/receptor_docking
sciagent detect-pocket <receptor.pdb> --mode crystal-ligand --out runs/<target>/pocket
# Convert prepared receptor + ligands to PDBQT (Open Babel/Meeko) before docking:
obabel runs/<target>/receptor_docking/docking_receptor_prepared.pdb -O runs/<target>/receptor.pdbqt -xr
sciagent run-docking runs/<target>/receptor.pdbqt <ligands_pdbqt_dir> runs/<target>/pocket/pocket.json --out runs/<target>/docking
sciagent assemble-docked-complex <receptor.pdb> runs/<target>/docking/<lig>/<lig>_docked.pdbqt --out runs/<target>/complex
```

Workflow:
1. Prepare the receptor first with `prepare_receptor_docking` (removes the pocket ligand, keeps waters by default, repairs atoms/hydrogens via PDBFixer when available).
2. Choose pocket source and mode: `crystal-ligand` center, user-provided `residues`, `fpocket`, `p2rank`, or `auto` (crystal → fpocket → P2Rank fallback).
3. Generate pocket/grid JSON with `detect_pocket`.
4. Convert the prepared receptor and each prepared ligand to PDBQT (Open Babel or Meeko). `run_docking` requires PDBQT inputs and a docking engine (Vina/GNINA/smina) on PATH.
5. Only run docking if receptor PDBQT, ligand PDBQT directory, and the docking engine all exist; otherwise stop and report exactly what is missing.
6. Rank by docking score, but never call docking proof of biological activity.
7. Optionally assemble the top pose into a protein-ligand complex PDB with `assemble_docked_complex` for downstream MD.

## Output rules
- Save all outputs under `runs/` unless the user gives another safe project-relative path.
- Preserve `run_manifest.json`.
- Report exact generated files.
- If an external binary or Python package is missing, report it clearly and continue with the safest available fallback.
- Never invent molecular descriptors, UniProt/PDB metadata, docking scores, RMSD/RMSF values, or interaction frequencies.
