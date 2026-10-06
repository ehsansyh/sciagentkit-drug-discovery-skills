import json
from pathlib import Path

import pandas as pd

from sciagentkit.skills.drug_discovery import audit_generated_molecules, profile_ligand_library


def test_profile_ligand_library_outputs(tmp_path: Path):
    smi = tmp_path / "mols.smi"
    smi.write_text("CCO\nOCC\nCCN\nnot_a_smiles\n")
    result = profile_ligand_library(smi, tmp_path / "out", make_figures=False)
    assert result["summary"]["input_molecules"] == 4
    assert result["summary"]["canonical_unique_molecules"] == 2
    assert (tmp_path / "out" / "run_manifest.json").exists()


def test_audit_generated_molecules_reports_novelty(tmp_path: Path):
    generated = tmp_path / "generated.smi"
    ref = tmp_path / "ref.smi"
    generated.write_text("CCO\nCCN\nc1ccccc1\n")
    ref.write_text("CCO\nCCCl\n")
    result = audit_generated_molecules(generated, ref, tmp_path / "audit", make_figures=False)
    assert result["summary"]["query_unique"] == 3
    assert result["summary"]["cross_duplicates"] == 1
    novelty = pd.read_csv(tmp_path / "audit" / "novelty_report.csv")
    assert "novelty_fraction" in novelty["metric"].tolist()


