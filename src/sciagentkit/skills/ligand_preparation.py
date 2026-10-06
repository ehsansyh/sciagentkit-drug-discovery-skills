from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem, SDWriter

from sciagentkit.core.manifest import write_manifest
from sciagentkit.core.smiles import clean_canonical_library, read_smiles_file
from sciagentkit.skills.forcefields import recommend_forcefield


def _embed_rdkit_molecule(smiles: str, name: str, forcefield: str = "MMFF94", seed: int = 61453) -> Chem.Mol | None:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    mol = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = seed
    status = AllChem.EmbedMolecule(mol, params)
    if status != 0:
        status = AllChem.EmbedMolecule(mol, randomSeed=seed, useRandomCoords=True)
    if status != 0:
        return None
    if forcefield.upper().startswith("MMFF") and AllChem.MMFFHasAllMoleculeParams(mol):
        AllChem.MMFFOptimizeMolecule(mol, mmffVariant="MMFF94", maxIters=1000)
    else:
        AllChem.UFFOptimizeMolecule(mol, maxIters=1000)
    mol.SetProp("_Name", name)
    mol.SetProp("sciagentkit_conformer_forcefield", forcefield)
    return mol


def prepare_ligands_3d(
    smiles_file: str | Path,
    out_dir: str | Path,
    smiles_column: str = "smiles",
    ph: float = 7.4,
    forcefield_mode: str = "recommend",
    conformer_forcefield: str | None = None,
    target_family: str | None = None,
    use_openbabel_if_available: bool = True,
) -> dict:
    smiles_file = Path(smiles_file)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    raw = read_smiles_file(smiles_file, smiles_column=smiles_column)
    canon_report, clean = clean_canonical_library(raw)
    canon_report.to_csv(out / "canonicalization_report.csv", index=False)
    clean.to_csv(out / "cleaned_ligands.csv", index=False)
    recommendation = recommend_forcefield(target_family)
    ff = conformer_forcefield or recommendation["conformer_forcefield"]
    sdf_path = out / "ligands_3d.sdf"
    failures: list[dict] = []
    used_engine = "rdkit"

    if use_openbabel_if_available and shutil.which("obabel"):
        smi_path = out / "cleaned_ligands.smi"
        with smi_path.open("w") as handle:
            for idx, smi in enumerate(clean["canonical_smiles"].tolist(), start=1):
                handle.write(f"{smi} ligand_{idx}\n")
        cmd = ["obabel", str(smi_path), "-O", str(sdf_path), "--gen3d", "-p", str(ph)]
        result = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=3600)
        if result.returncode == 0 and sdf_path.exists():
            used_engine = "openbabel"
        else:
            failures.append({"engine": "openbabel", "error": result.stderr[-1000:]})

    if used_engine == "rdkit":
        writer = SDWriter(str(sdf_path))
        for idx, smi in enumerate(clean["canonical_smiles"].tolist(), start=1):
            mol = _embed_rdkit_molecule(smi, f"ligand_{idx}", forcefield=ff)
            if mol is None:
                failures.append({"ligand_index": idx, "smiles": smi, "error": "RDKit embedding failed"})
                continue
            mol.SetProp("sciagentkit_preparation_pH_recorded", str(ph))
            mol.SetProp("sciagentkit_note", "RDKit fallback records pH but does not perform rigorous pH-state enumeration.")
            writer.write(mol)
        writer.close()

    pd.DataFrame(failures).to_csv(out / "ligand_preparation_failures.csv", index=False)
    pd.DataFrame([recommendation]).to_csv(out / "forcefield_recommendation.csv", index=False)
    write_manifest(out, [smiles_file], command=f"sciagent prepare-ligands {smiles_file} --out {out}", parameters={"ph": ph, "forcefield_mode": forcefield_mode, "conformer_forcefield": ff, "target_family": target_family, "used_engine": used_engine}, workflow_name="ligand_3d_preparation")
    return {"output_dir": str(out), "summary": {"input_molecules": len(raw), "unique_ligands": len(clean), "engine": used_engine, "pH": ph, "conformer_forcefield": ff, "failures": len(failures)}, "generated_files": ["ligands_3d.sdf", "cleaned_ligands.csv", "forcefield_recommendation.csv", "ligand_preparation_failures.csv", "run_manifest.json"]}
