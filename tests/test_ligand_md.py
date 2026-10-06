from pathlib import Path

from sciagentkit.skills.ligand_md import ligand_md_readiness


PROTEIN = """\
ATOM      1  N   ALA A   1      10.000  10.000  10.000  1.00 20.00           N\nATOM      2  CA  ALA A   1      11.000  10.000  10.000  1.00 20.00           C\nEND\n"""

PDBQT = """\
MODEL 1\nROOT\nATOM      1  C   UNL     1       5.656  11.441   4.060  0.00  0.00    +0.000 C \nATOM      2  O   UNL     1       6.712  11.114   4.920  0.00  0.00    +0.000 OA\nENDROOT\nENDMDL\nMODEL 2\nATOM      1  C   UNL     1       9.000   9.000   9.000  0.00  0.00    +0.000 C \nENDMDL\n"""


def test_ligand_md_readiness_reports_missing_parameterization_packages(monkeypatch, tmp_path: Path):
    def missing_spec(name):
        if name == "openff.toolkit":
            raise ModuleNotFoundError("No module named openff")
        return None

    monkeypatch.setattr("sciagentkit.skills.ligand_md.importlib.util.find_spec", missing_spec)

    result = ligand_md_readiness(tmp_path / "ligand.sdf", tmp_path / "readiness")

    assert result["summary"]["ready"] is False
    assert "openff-toolkit" in result["summary"]["missing_packages"]
    assert "openmmforcefields" in result["summary"]["missing_packages"]
    assert (tmp_path / "readiness" / "ligand_md_readiness.json").exists()


