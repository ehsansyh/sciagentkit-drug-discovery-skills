from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import json

from sciagentkit.core.manifest import write_manifest

WATER_RESNAMES = {"HOH", "WAT", "DOD", "H2O"}
ION_RESNAMES = {"NA", "CL", "K", "MG", "MN", "CA", "ZN", "FE", "CU", "CO", "NI"}


def _is_atom(line: str) -> bool:
    return line.startswith(("ATOM", "HETATM"))


def _residue_key(line: str) -> tuple[str, str, str, str]:
    return (line[17:20].strip(), line[21].strip(), line[22:26].strip(), line[26].strip())


def _resname(line: str) -> str:
    return line[17:20].strip()


def _find_pocket_ligand(lines: list[str], ligand_resname: str | None = None) -> tuple[str, str, str, str] | None:
    groups: dict[tuple[str, str, str, str], int] = defaultdict(int)
    for line in lines:
        if not line.startswith("HETATM"):
            continue
        resname = _resname(line)
        if resname in WATER_RESNAMES or resname in ION_RESNAMES:
            continue
        key = _residue_key(line)
        if ligand_resname and resname.upper() != ligand_resname.upper():
            continue
        groups[key] += 1
    if not groups:
        return None
    return max(groups, key=groups.get)


def _write_pdb(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = [line.rstrip("\n") for line in lines if _is_atom(line)]
    path.write_text("\n".join(body + ["END", ""]))


def _try_pdbfixer(input_pdb: Path, output_pdb: Path, add_hydrogens: bool = True) -> tuple[bool, str | None]:
    try:
        from pdbfixer import PDBFixer
        from openmm.app import PDBFile
    except Exception as exc:
        return False, f"PDBFixer unavailable: {exc}"
    try:
        fixer = PDBFixer(filename=str(input_pdb))
        fixer.findMissingResidues()
        fixer.findMissingAtoms()
        fixer.addMissingAtoms()
        if add_hydrogens:
            fixer.addMissingHydrogens(7.4)
        with output_pdb.open("w") as handle:
            PDBFile.writeFile(fixer.topology, fixer.positions, handle)
        return True, None
    except Exception as exc:
        return False, f"PDBFixer failed: {exc}"


def prepare_receptor_for_docking(pdb_file: str | Path, out_dir: str | Path, ligand_resname: str | None = None, keep_waters: bool = True, add_hydrogens: bool = True) -> dict:
    pdb_file = Path(pdb_file)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    lines = pdb_file.read_text(errors="ignore").splitlines()
    ligand_key = _find_pocket_ligand(lines, ligand_resname)
    receptor_lines = []
    ligand_lines = []
    waters_kept = Counter()
    heterogens_removed = Counter()
    for line in lines:
        if not _is_atom(line):
            continue
        key = _residue_key(line)
        resname = _resname(line)
        if ligand_key and key == ligand_key:
            ligand_lines.append(line)
            continue
        if line.startswith("HETATM") and resname in WATER_RESNAMES:
            if keep_waters:
                receptor_lines.append(line)
                waters_kept[key] += 1
            continue
        if line.startswith("HETATM") and resname not in ION_RESNAMES:
            heterogens_removed[key] += 1
            continue
        receptor_lines.append(line)
    raw_receptor = out / "docking_receptor_raw.pdb"
    prepared = out / "docking_receptor_prepared.pdb"
    ligand = out / "pocket_ligand.pdb"
    _write_pdb(raw_receptor, receptor_lines)
    if ligand_lines:
        _write_pdb(ligand, ligand_lines)
    fixed, fixer_note = _try_pdbfixer(raw_receptor, prepared, add_hydrogens=add_hydrogens)
    if not fixed:
        prepared.write_text(raw_receptor.read_text())
    report = {
        "input_pdb": str(pdb_file),
        "prepared_receptor_pdb": str(prepared),
        "pocket_ligand_pdb": str(ligand) if ligand_lines else None,
        "pocket_ligand_key": ligand_key,
        "waters_kept": len(waters_kept),
        "heterogens_removed": len(heterogens_removed),
        "pdbfixer_used": fixed,
        "pdbfixer_note": fixer_note,
        "mode": "docking",
    }
    (out / "receptor_preparation.json").write_text(json.dumps(report, indent=2))
    write_manifest(out, [pdb_file], command=f"sciagent prepare-receptor-docking {pdb_file} --out {out}", parameters={"ligand_resname": ligand_resname, "keep_waters": keep_waters, "add_hydrogens": add_hydrogens}, workflow_name="receptor_preparation_docking")
    return {"output_dir": str(out), "prepared_receptor_pdb": str(prepared), "pocket_ligand_pdb": str(ligand) if ligand_lines else None, "summary": report, "generated_files": ["docking_receptor_raw.pdb", "docking_receptor_prepared.pdb", "pocket_ligand.pdb", "receptor_preparation.json", "run_manifest.json"]}


def prepare_receptor_for_md(pdb_file: str | Path, out_dir: str | Path, add_hydrogens: bool = True) -> dict:
    pdb_file = Path(pdb_file)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    lines = pdb_file.read_text(errors="ignore").splitlines()
    receptor_lines = []
    waters_removed = Counter()
    heterogens_removed = Counter()
    ions_removed = Counter()
    for line in lines:
        if not _is_atom(line):
            continue
        if line.startswith("HETATM"):
            resname = _resname(line)
            key = _residue_key(line)
            if resname in WATER_RESNAMES:
                waters_removed[key] += 1
            elif resname in ION_RESNAMES:
                ions_removed[key] += 1
            else:
                heterogens_removed[key] += 1
            continue
        receptor_lines.append(line)
    raw_receptor = out / "md_receptor_raw.pdb"
    prepared = out / "md_receptor_prepared.pdb"
    _write_pdb(raw_receptor, receptor_lines)
    fixed, fixer_note = _try_pdbfixer(raw_receptor, prepared, add_hydrogens=add_hydrogens)
    if not fixed:
        prepared.write_text(raw_receptor.read_text())
    report = {
        "input_pdb": str(pdb_file),
        "prepared_receptor_pdb": str(prepared),
        "waters_removed": len(waters_removed),
        "heterogens_removed": len(heterogens_removed),
        "ions_removed": len(ions_removed),
        "pdbfixer_used": fixed,
        "pdbfixer_note": fixer_note,
        "mode": "md",
    }
    (out / "receptor_preparation.json").write_text(json.dumps(report, indent=2))
    write_manifest(out, [pdb_file], command=f"sciagent prepare-receptor-md {pdb_file} --out {out}", parameters={"add_hydrogens": add_hydrogens}, workflow_name="receptor_preparation_md")
    return {"output_dir": str(out), "prepared_receptor_pdb": str(prepared), "summary": report, "generated_files": ["md_receptor_raw.pdb", "md_receptor_prepared.pdb", "receptor_preparation.json", "run_manifest.json"]}
