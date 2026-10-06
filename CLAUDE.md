# SciAgentKit Agent Instructions

Use SciAgentKit MCP tools for computational biology, cheminformatics, target-selection, docking-preparation, MD-planning, trajectory-analysis, and reporting tasks.

Never invent molecular descriptors, QED, MW, logP, TPSA, scaffold diversity, docking scores, UniProt sequences, PDB rankings, RMSD, RMSF, residue interaction frequencies, literature metadata, or citations.

Core workflow rules:
1. For one molecule library, use `analyze_library` (also emits ADME/toxicity: ESOL solubility, drug-likeness, GI/BBB heuristics, PAINS/Brenk alerts).
2. For generated vs reference molecules, use `audit_generated_library`. For ADME/tox of a single molecule, use `adme_tox`.
3. For target and PDB structure selection, use `protein_select`. It ranks structures but does not download coordinates; use `fetch_pdb` to download the selected PDB's coordinate file from RCSB before receptor/pocket/docking steps.
4. For ligand 3D preparation, use `prepare_ligands`.
5. For pocket definition, use `detect_pocket` (crystal-ligand, residues, fpocket, P2Rank, or auto).
6. For receptor preparation, use `prepare_receptor_docking` (docking) or `prepare_receptor_md` (MD) before docking or MD.
7. For docking, use `run_docking` only after receptor and ligand PDBQT files exist (convert prepared PDB/SDF to PDBQT with Open Babel/Meeko first). To run the whole chain from a target name (or PDB id) in one step — `protein_select` → `fetch_pdb` → `prepare_ligands` → `detect_pocket` → `prepare_receptor_docking` → PDBQT conversion → `run_docking` — use `dock_to_target`; it stops gracefully with a `next_action` if Open Babel or a docking engine is missing.
8. To build a protein-ligand complex from a docked pose, use `assemble_docked_complex`.
9. For MD, use `md_plan` (protein/apo) or `ligand_md_plan` (protein-ligand); do not claim MD was run unless trajectory files exist and were analyzed.
10. For trajectory analysis, use `analyze_trajectory`.
11. To rank docked ligands into target-aware best hits (weighting toxicity, drug-likeness, and BBB permeability for CNS targets), use `select_top_hits`.
12. To propose target-aware wet-lab validation experiments (biochemical assay, cell lines, ADME/DMPK, safety) for a ligand/target, use `wet_lab_plan`. These are advisory experimental templates, not results.
13. For final output, use `write_report` (includes a "Recommended wet-lab validation" section).

Note: `protein_select` ranks PDB structures but does not download coordinate files; use `fetch_pdb` (or `dock_to_target`, which calls it) to obtain the PDB before docking or MD.

Pipeline order and mid-pipeline entry: the stages run in the order above. If a request starts mid-pipeline (e.g. "dock these ligands to EGFR"), run the prerequisite earlier stages first — resolve the target/structure (`protein_select`), download it (`fetch_pdb`), prepare ligands, define the pocket, and prepare the receptor — before `run_docking`. Prefer `dock_to_target` to do this backfill automatically.

Enterprise tools: `run_docking`, `dock_to_target`, `assemble_docked_complex`, `md_plan`, `ligand_md_plan`, `ligand_md_run`, `md_run_smoke`, `analyze_trajectory`, `select_top_hits`, `wet_lab_plan`, `target_screen_project`, and `write_report` come from SciAgentKit Enterprise (https://sciagentkit.com). If one of them is not in your tool list, tell the user that step requires SciAgentKit Enterprise and stop there. Never simulate, estimate, or describe its output as if it had run.

Always save workflow outputs under `runs/`.
Always preserve `run_manifest.json`.
Clearly report missing external tools such as OpenBabel, AutoDock Vina, fpocket, OpenMM, MDAnalysis, or ProLIF.
