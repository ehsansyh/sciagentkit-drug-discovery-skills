from pathlib import Path

from sciagentkit.skills.pockets import crystal_ligand_centers, detect_pocket

PDB = """\
ATOM      1  N   ALA A   1      10.000  10.000  10.000  1.00 20.00           N\nATOM      2  CA  ALA A   1      11.000  10.000  10.000  1.00 20.00           C\nHETATM    3  C1  LIG A 101      20.000  20.000  20.000  1.00 20.00           C\nHETATM    4  C2  LIG A 101      22.000  20.000  20.000  1.00 20.00           C\nEND\n"""


def test_crystal_ligand_center(tmp_path: Path):
    pdb = tmp_path / "test.pdb"
    pdb.write_text(PDB)
    centers = crystal_ligand_centers(pdb)
    assert centers.iloc[0]["ligand_resname"] == "LIG"
    result = detect_pocket(pdb, tmp_path / "pocket")
    assert result["summary"]["center_x"] == 21.0


def test_detect_pocket_auto_falls_back_to_p2rank(monkeypatch, tmp_path: Path):
    pdb = tmp_path / "apo.pdb"
    pdb.write_text(
        "ATOM      1  N   ALA A   1      10.000  10.000  10.000  1.00 20.00           N\n"
        "ATOM      2  CA  ALA A   1      11.000  10.000  10.000  1.00 20.00           C\n"
        "END\n"
    )
    out = tmp_path / "pocket"

    monkeypatch.setattr("sciagentkit.skills.pockets.shutil.which", lambda name: "/usr/bin/prank" if name == "prank" else None)

    def fake_run(cmd, stdin, capture_output, text, timeout):
        predictions = out / "p2rank" / f"{pdb.stem}.pdb_predictions.csv"
        predictions.parent.mkdir(parents=True, exist_ok=True)
        predictions.write_text(
            "rank,score,probability,center_x,center_y,center_z,sas_points,surf_atoms\n"
            "1,12.5,0.91,1.0,2.0,3.0,44,19\n",
            encoding="utf-8",
        )

        class Result:
            returncode = 0
            stdout = "ok"
            stderr = ""

        return Result()

    monkeypatch.setattr("sciagentkit.skills.pockets.subprocess.run", fake_run)

    result = detect_pocket(pdb, out, mode="auto")

    assert result["summary"]["source"] == "p2rank"
    assert result["summary"]["center_x"] == 1.0
    assert (out / "pocket.json").exists()
