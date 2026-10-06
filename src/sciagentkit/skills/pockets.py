from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import json
import shutil
import subprocess

import pandas as pd

from sciagentkit.core.manifest import write_manifest

WATER_RESNAMES = {"HOH", "WAT", "DOD", "H2O"}
ION_RESNAMES = {"NA", "CL", "K", "MG", "MN", "CA", "ZN", "FE", "CU", "CO", "NI"}


def _parse_pdb_atoms(pdb_file: str | Path) -> list[dict]:
    atoms = []
    for line in Path(pdb_file).read_text(errors="ignore").splitlines():
        if not line.startswith(("ATOM", "HETATM")):
            continue
        try:
            atoms.append({
                "record": line[0:6].strip(), "atom": line[12:16].strip(), "resname": line[17:20].strip(),
                "chain": line[21].strip(), "resseq": int(line[22:26]),
                "x": float(line[30:38]), "y": float(line[38:46]), "z": float(line[46:54]),
            })
        except Exception:
            continue
    return atoms


def crystal_ligand_centers(pdb_file: str | Path) -> pd.DataFrame:
    groups: dict[tuple[str, str, int], list[dict]] = defaultdict(list)
    for atom in _parse_pdb_atoms(pdb_file):
        if atom["record"] != "HETATM" or atom["resname"] in WATER_RESNAMES or atom["resname"] in ION_RESNAMES:
            continue
        groups[(atom["resname"], atom["chain"], atom["resseq"])].append(atom)
    rows = []
    for (resname, chain, resseq), atoms in groups.items():
        rows.append({"ligand_resname": resname, "chain": chain, "resseq": resseq, "n_atoms": len(atoms), "center_x": sum(a["x"] for a in atoms) / len(atoms), "center_y": sum(a["y"] for a in atoms) / len(atoms), "center_z": sum(a["z"] for a in atoms) / len(atoms)})
    return pd.DataFrame(rows).sort_values("n_atoms", ascending=False) if rows else pd.DataFrame(columns=["ligand_resname", "chain", "resseq", "n_atoms", "center_x", "center_y", "center_z"])


def _fpocket_pocket(pdb_file: Path) -> dict:
    if not shutil.which("fpocket"):
        raise RuntimeError("fpocket executable not found")
    result = subprocess.run(["fpocket", "-f", str(pdb_file)], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=3600)
    if result.returncode != 0:
        raise RuntimeError(result.stderr[-2000:])
    return {"source": "fpocket", "note": "fpocket output generated; inspect generated pockets and choose coordinates before docking."}


def _p2rank_executable() -> str:
    path = shutil.which("prank") or shutil.which("p2rank")
    if not path:
        raise RuntimeError("P2Rank executable not found. Install P2Rank/prank or use crystal-ligand/residues/fpocket mode.")
    return path


def _p2rank_predictions_file(work_dir: Path, pdb_file: Path) -> Path:
    candidates = [
        work_dir / f"{pdb_file.name}_predictions.csv",
        work_dir / f"{pdb_file.stem}.pdb_predictions.csv",
        work_dir / f"{pdb_file.stem}_predictions.csv",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    found = sorted(work_dir.glob("*_predictions.csv"))
    if found:
        return found[0]
    raise RuntimeError("P2Rank completed but no *_predictions.csv file was found")


def p2rank_pocket(pdb_file: str | Path, out_dir: str | Path, grid_size: float = 22.0) -> dict:
    pdb_file = Path(pdb_file)
    work_dir = Path(out_dir) / "p2rank"
    work_dir.mkdir(parents=True, exist_ok=True)
    executable = _p2rank_executable()
    result = subprocess.run([executable, "predict", "-f", str(pdb_file), "-o", str(work_dir)], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=7200)
    if result.returncode != 0:
        raise RuntimeError(result.stderr[-2000:])
    predictions = pd.read_csv(_p2rank_predictions_file(work_dir, pdb_file))
    if predictions.empty:
        raise RuntimeError("P2Rank produced an empty predictions table")
    row = predictions.iloc[0]
    return {
        "center_x": float(row["center_x"]),
        "center_y": float(row["center_y"]),
        "center_z": float(row["center_z"]),
        "size_x": grid_size,
        "size_y": grid_size,
        "size_z": grid_size,
        "source": "p2rank",
        "rank": int(row["rank"]) if "rank" in row and pd.notna(row["rank"]) else 1,
        "score": float(row["score"]) if "score" in row and pd.notna(row["score"]) else None,
        "probability": float(row["probability"]) if "probability" in row and pd.notna(row["probability"]) else None,
        "predictions_file": str(_p2rank_predictions_file(work_dir, pdb_file)),
    }


def residue_pocket_center(pdb_file: str | Path, residues: list[str]) -> dict:
    wanted = set()
    for token in residues:
        token = token.strip()
        if ":" in token:
            chain, resi = token.split(":", 1)
            wanted.add((chain, int(resi)))
        else:
            wanted.add((None, int(token)))
    atoms = [a for a in _parse_pdb_atoms(pdb_file) if a["record"] == "ATOM" and ((a["chain"], a["resseq"]) in wanted or (None, a["resseq"]) in wanted)]
    if not atoms:
        raise ValueError("No atoms found for requested pocket residues")
    xs, ys, zs = [a["x"] for a in atoms], [a["y"] for a in atoms], [a["z"] for a in atoms]
    return {"center_x": sum(xs)/len(xs), "center_y": sum(ys)/len(ys), "center_z": sum(zs)/len(zs), "size_x": max(18.0, max(xs)-min(xs)+8.0), "size_y": max(18.0, max(ys)-min(ys)+8.0), "size_z": max(18.0, max(zs)-min(zs)+8.0), "source": "residue_list", "n_atoms": len(atoms)}


def detect_pocket(pdb_file: str | Path, out_dir: str | Path, mode: str = "crystal-ligand", ligand_resname: str | None = None, residues: list[str] | None = None, grid_size: float = 22.0) -> dict:
    pdb_file = Path(pdb_file)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    generated_files = []
    errors = []
    if mode in {"crystal-ligand", "auto"}:
        centers = crystal_ligand_centers(pdb_file)
        centers.to_csv(out / "crystal_ligand_centers.csv", index=False)
        generated_files.append("crystal_ligand_centers.csv")
        if not centers.empty:
            row = centers.iloc[0] if not ligand_resname else centers[centers["ligand_resname"].str.upper() == ligand_resname.upper()].iloc[0]
            pocket = {"center_x": float(row.center_x), "center_y": float(row.center_y), "center_z": float(row.center_z), "size_x": grid_size, "size_y": grid_size, "size_z": grid_size, "source": "crystal_ligand", "ligand_resname": row.ligand_resname, "chain": row.chain, "resseq": int(row.resseq)}
        elif mode == "crystal-ligand":
            raise ValueError("No non-water/non-ion crystal ligand found. Use --mode residues, --mode fpocket, --mode p2rank, or --mode auto.")
        else:
            pocket = None
            errors.append("crystal-ligand: no non-water/non-ion crystal ligand found")
    elif mode == "residues":
        if not residues:
            raise ValueError("Residue mode requires residues such as A:123 A:456")
        pocket = residue_pocket_center(pdb_file, residues)
    elif mode == "fpocket":
        pocket = _fpocket_pocket(pdb_file)
    elif mode == "p2rank":
        pocket = p2rank_pocket(pdb_file, out, grid_size)
    else:
        raise ValueError(f"Unknown pocket mode: {mode}")

    if mode == "auto" and pocket is None:
        for fallback in (_fpocket_pocket, lambda pdb: p2rank_pocket(pdb, out, grid_size)):
            try:
                pocket = fallback(pdb_file)
                break
            except RuntimeError as exc:
                errors.append(str(exc))
        if pocket is None:
            raise RuntimeError("No automatic pocket fallback succeeded: " + "; ".join(errors))

    with (out / "pocket.json").open("w") as handle:
        json.dump(pocket, handle, indent=2)
    write_manifest(out, [pdb_file], command=f"sciagent detect-pocket {pdb_file} --out {out}", parameters={"mode": mode, "ligand_resname": ligand_resname, "residues": residues or []}, workflow_name="pocket_detection")
    return {"output_dir": str(out), "summary": pocket, "generated_files": [*generated_files, "pocket.json", "run_manifest.json"]}
