from pathlib import Path

from sciagentkit.skills.ligand_preparation import prepare_ligands_3d


def test_prepare_ligands_rdkit(tmp_path: Path):
    smi = tmp_path / "ligands.smi"
    smi.write_text("CCO\nCC(=O)O\n")
    result = prepare_ligands_3d(smi, tmp_path / "out", use_openbabel_if_available=False)
    assert result["summary"]["unique_ligands"] == 2
    assert (tmp_path / "out" / "ligands_3d.sdf").exists()
