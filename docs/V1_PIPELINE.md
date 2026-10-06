# SciAgentKit v1.0 Target Screening Pipeline

SciAgentKit v1.0 turns the original molecule-library audit toolkit into an MCP-native scientific skill layer for target-centric computational drug-discovery workflows.

## What v1.0 can do

1. **Literature MCP**
   - Search Europe PMC and PubMed.
   - Save literature evidence tables.
   - Expose literature search through CLI and MCP.

2. **Protein / PDB / UniProt tools**
   - Resolve a target gene or UniProt accession.
   - Fetch the canonical UniProt sequence.
   - Apply requested point mutations, e.g. `V600E`.
   - List UniProt-linked PDB structures.
   - Fetch PDB chain sequences through RCSB GraphQL when available.
   - Align target or mutated sequence to PDB chain sequences.
   - Rank PDB candidates by mutation match, residue coverage/span, resolution, and sequence identity.
   - Select the widest aligned residue coverage first, and the best resolution within that group.

3. **Ligand preparation**
   - Canonicalize and deduplicate SMILES.
   - Generate 3D ligand conformers.
   - Save ligands as SDF.
   - Use Open Babel for pH-aware protonation/3D generation when available.
   - Fall back to RDKit ETKDG + MMFF/UFF and record the pH as metadata.
   - Recommend force-field defaults or accept user-provided values.

4. **Pocket definition**
   - Detect pocket center from crystallographic ligand HETATM coordinates.
   - Define pocket center from known residues.
   - Optionally call `fpocket` if installed.
   - Write Vina-compatible `pocket.json` with grid center and size.

5. **Docking**
   - Write Vina config files.
   - Run AutoDock Vina when `vina` is installed.
   - Parse docking logs.
   - Rank ligands by best affinity.
   - Select top ligands by `top_n` or `top_fraction`.

6. **MD job generation**
   - Create OpenMM job folders.
   - Generate per-ligand/per-replica seeds.
   - Add water, ions, neutralization, and 0.15 M salt in the generated OpenMM script.
   - Generate 3 replicas automatically when selected ligand count is small.
   - Write `md_jobs.csv`, `md_config.json`, and `run.sh` files.

7. **Trajectory analysis**
   - Analyze RMSD/RMSF with MDAnalysis when installed.
   - Run ProLIF interaction fingerprinting when installed.
   - Write explicit error files if optional dependencies are missing.

8. **Reporting**
   - Assemble `final_report.md`.
   - Optionally generate DOCX/PDF if optional dependencies are installed.

## Important limitation

v1.0 intentionally does **not** pretend to solve receptor preparation, ligand parameterization, protonation-state validation, covalent chemistry, membrane embedding, metal coordination, missing-loop modeling, or full production-quality MD without user review. Those are scientific decisions, not decorations. The tool builds a reproducible workflow and tells users exactly where review is needed.

## Example workflow

```bash
sciagent literature-search "EGFR L858R inhibitor binding pocket" --out runs/egfr/literature

sciagent protein-select EGFR --mutation L858R --out runs/egfr/protein

sciagent prepare-ligands ligands.smi --ph 7.4 --target-family kinase --out runs/egfr/ligands

sciagent detect-pocket receptor.pdb --mode crystal-ligand --out runs/egfr/pocket

sciagent run-docking receptor.pdbqt ligands_pdbqt/ runs/egfr/pocket/pocket.json --top-fraction 0.1 --out runs/egfr/docking

sciagent md-plan complex.pdb runs/egfr/docking/top_ligands.csv --ns 1 --out runs/egfr/md

sciagent analyze-trajectory complex.pdb trajectory.dcd --prolif-ligand-selection "resname LIG" --out runs/egfr/analysis

sciagent write-report runs/egfr --docx --pdf
```

## MCP usage

```bash
python -m sciagentkit.servers.rdkit_server
```

The MCP server exposes molecule, literature, protein, ligand-prep, pocket, docking, MD, trajectory-analysis, and report tools.
