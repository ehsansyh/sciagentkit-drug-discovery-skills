---
name: full-target-screening
description: Use when a user asks for a complete target-to-report computational biology workflow or wants multiple SciAgentKit stages coordinated in one project.
---

> **Requires SciAgentKit Enterprise.** The docking, MD, trajectory, hit-ranking, wet-lab and report tools this skill relies on are part of SciAgentKit Enterprise (https://sciagentkit.com). If they are not in your tool list, run only the free steps, tell the user the rest requires Enterprise, and never simulate the missing results.


# SciAgentKit full target-screening workflow

Use this when the user explicitly asks for the complete target-to-report pipeline. This skill is manual-invoked by default because it can be heavy.

Preferred staged workflow:
1. `literature_search` for target/mutation/pocket context.
2. `protein_select` for UniProt sequence, PDB listing, mutation-aware alignment, coverage/resolution ranking. This ranks structures only; download the selected PDB coordinates from RCSB before docking/MD.
3. `prepare_ligands` for pH-aware 3D SDF ligand preparation. `analyze_library` (or `adme_tox`) additionally profiles ADME (ESOL solubility, drug-likeness, GI/BBB) and toxicity/liability alerts (PAINS/Brenk).
4. `prepare_receptor_docking` to strip the pocket ligand and repair the receptor (and `prepare_receptor_md` for the MD system).
5. `detect_pocket` using crystal ligand, known residues, `fpocket`, `p2rank`, or `auto` fallback.
6. Convert the prepared receptor and ligands to PDBQT (Open Babel/Meeko), then `run_docking` (Vina/GNINA/smina) — only after PDBQT inputs and a docking engine exist.
7. `assemble_docked_complex` to build a protein-ligand complex from the top pose.
8. `md_plan` (apo/protein) or `ligand_md_plan` (protein-ligand) for OpenMM jobs, solvation, ions, salt, NVT/NPT/equilibration, short MD and replicas.
9. `analyze_trajectory` only after trajectories exist.
10. `select_top_hits` to rank ligands into target-aware best hits, weighting docking score, MD stability, and ADME/tox (toxicity penalized; BBB up-weighted for CNS targets).
11. `wet_lab_plan` to propose target-aware validation experiments (biochemical assay, cell lines, ADME/DMPK, safety) for the top hit.
12. `write_report` for the final markdown/DOCX/PDF report (includes top-hit ranking and a "Recommended wet-lab validation" section).

Alternatively, `target_screen_project` scaffolds steps 2-3 plus an MD skeleton in one call; note it writes `md/RECEPTOR_REQUIRED.txt` and skips MD-job generation until a prepared receptor PDB is supplied.

Stop at the first missing scientific input or missing external binary and report exactly what is missing. Do not fake completed docking or MD.

## Output rules
- Save all outputs under `runs/` unless the user gives another safe project-relative path.
- Preserve `run_manifest.json`.
- Report exact generated files.
- If an external binary or Python package is missing, report it clearly and continue with the safest available fallback.
- Never invent molecular descriptors, UniProt/PDB metadata, docking scores, RMSD/RMSF values, or interaction frequencies.
