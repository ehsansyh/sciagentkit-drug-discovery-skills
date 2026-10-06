"""Ligand-protein MD readiness checks (open-source core).

Building and running ligand MD jobs is part of SciAgentKit Enterprise.
"""
from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import shutil
import subprocess

from sciagentkit.core.manifest import write_manifest


PARAMETERIZATION_PACKAGES = {
    "openff-toolkit": "openff.toolkit",
    "openmmforcefields": "openmmforcefields",
}


def _module_available(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except ModuleNotFoundError:
        return False


def ligand_md_readiness(ligand_file: str | Path, out_dir: str | Path) -> dict:
    ligand_file = Path(ligand_file)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    missing = [label for label, module in PARAMETERIZATION_PACKAGES.items() if not _module_available(module)]
    available_tools = {"obabel": shutil.which("obabel"), "antechamber": shutil.which("antechamber"), "parmchk2": shutil.which("parmchk2")}
    ready = not missing and ligand_file.exists()
    summary = {
        "ready": ready,
        "ligand_file": str(ligand_file),
        "ligand_file_exists": ligand_file.exists(),
        "missing_packages": missing,
        "available_tools": available_tools,
        "recommended_install": "conda install -c conda-forge openff-toolkit openmmforcefields" if missing else None,
        "note": "Ligand-protein production MD requires a bonded ligand file with valid chemistry and an OpenMM-compatible ligand template generator.",
    }
    (out / "ligand_md_readiness.json").write_text(json.dumps(summary, indent=2))
    write_manifest(out, [ligand_file] if ligand_file.exists() else [], command=f"sciagent ligand-md-readiness {ligand_file} --out {out}", parameters={}, workflow_name="ligand_md_readiness")
    return {"output_dir": str(out), "summary": summary, "generated_files": ["ligand_md_readiness.json", "run_manifest.json"]}


def convert_pose_to_sdf(pose_pdb: str | Path, out_sdf: str | Path) -> Path:
    pose_pdb = Path(pose_pdb)
    out_sdf = Path(out_sdf)
    if not shutil.which("obabel"):
        raise RuntimeError("Open Babel (obabel) is required to infer/write docked ligand SDF from a PDB pose")
    out_sdf.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(["obabel", str(pose_pdb), "-O", str(out_sdf)], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(result.stderr[-2000:])
    return out_sdf
