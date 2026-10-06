---
name: ligand-preparation
description: Use when ligands need 3D preparation from SMILES or SDF before docking, pocket workflows, receptor-ligand setup, or MD planning.
---

# SciAgentKit ligand 3D preparation

Preferred MCP tool: `prepare_ligands`.
Preferred CLI fallback:
```bash
sciagent prepare-ligands <ligands.smi> --ph 7.4 --target-family <family> --out runs/<target>/ligands
```

Decision rule:
- If the user has not specified force field/conformer settings, ask a two-choice question: use SciAgentKit recommended setting, or use a user-specified force field.
- For normal cheminformatics conformers, use RDKit/OpenBabel fallback as available.
- Save ligands as SDF and report failures.

## Output rules
- Save all outputs under `runs/` unless the user gives another safe project-relative path.
- Preserve `run_manifest.json`.
- Report exact generated files.
- If an external binary or Python package is missing, report it clearly and continue with the safest available fallback.
- Never invent molecular descriptors, UniProt/PDB metadata, docking scores, RMSD/RMSF values, or interaction frequencies.
