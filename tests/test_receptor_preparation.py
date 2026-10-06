from pathlib import Path

from sciagentkit.skills.receptor_preparation import prepare_receptor_for_docking, prepare_receptor_for_md


PDB = """\
ATOM      1  N   ALA A   1      10.000  10.000  10.000  1.00 20.00           N\nATOM      2  CA  ALA A   1      11.000  10.000  10.000  1.00 20.00           C\nHETATM    3  O   HOH A 201      12.000  10.000  10.000  1.00 20.00           O\nHETATM    4  C1  LIG A 301      20.000  20.000  20.000  1.00 20.00           C\nHETATM    5  C2  LIG A 301      21.000  20.000  20.000  1.00 20.00           C\nEND\n"""


def test_prepare_receptor_for_docking_removes_pocket_ligand_and_keeps_water(tmp_path: Path):
    pdb = tmp_path / "complex.pdb"
    pdb.write_text(PDB)

    result = prepare_receptor_for_docking(pdb, tmp_path / "dock_receptor")

    receptor = Path(result["prepared_receptor_pdb"]).read_text()
    ligand = Path(result["pocket_ligand_pdb"]).read_text()
    assert "HOH" in receptor
    assert "LIG" not in receptor
    assert "LIG" in ligand
    assert result["summary"]["waters_kept"] == 1
    assert (tmp_path / "dock_receptor" / "run_manifest.json").exists()


def test_prepare_receptor_for_md_removes_waters_and_heterogens(tmp_path: Path):
    pdb = tmp_path / "complex.pdb"
    pdb.write_text(PDB)

    result = prepare_receptor_for_md(pdb, tmp_path / "md_receptor")

    receptor = Path(result["prepared_receptor_pdb"]).read_text()
    assert "HOH" not in receptor
    assert "LIG" not in receptor
    assert "ALA" in receptor
    assert result["summary"]["waters_removed"] == 1
    assert result["summary"]["heterogens_removed"] == 1
