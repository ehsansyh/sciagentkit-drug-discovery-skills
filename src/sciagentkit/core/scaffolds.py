from __future__ import annotations

from collections import Counter
from typing import Iterable

import pandas as pd
from rdkit import Chem
from rdkit.Chem.Scaffolds import MurckoScaffold


def get_bemis_murcko_scaffold(smiles: str) -> str | None:
    """Return canonical Bemis-Murcko scaffold SMILES.

    Acyclic molecules return an empty scaffold string, following RDKit behavior.
    """
    mol = Chem.MolFromSmiles(str(smiles))
    if mol is None:
        return None
    scaffold = MurckoScaffold.GetScaffoldForMol(mol)
    if scaffold is None or scaffold.GetNumAtoms() == 0:
        return ""
    return Chem.MolToSmiles(scaffold, canonical=True)


def scaffold_table(smiles_list: Iterable[str]) -> pd.DataFrame:
    rows = []
    for smi in smiles_list:
        rows.append({"smiles": smi, "bemis_murcko_scaffold": get_bemis_murcko_scaffold(str(smi))})
    return pd.DataFrame(rows, columns=["smiles", "bemis_murcko_scaffold"])


def scaffold_summary(smiles_list: Iterable[str]) -> dict:
    smiles = [str(s) for s in smiles_list]
    scaffolds = [get_bemis_murcko_scaffold(s) for s in smiles]
    scaffolds = [s for s in scaffolds if s is not None]
    counts = Counter(scaffolds)
    total_molecules = len(smiles)
    unique_scaffolds = len(counts)
    singleton_scaffolds = sum(1 for v in counts.values() if v == 1)
    largest_cluster = max(counts.values()) if counts else 0
    return {
        "total_molecules": total_molecules,
        "unique_scaffolds": unique_scaffolds,
        "scaffold_diversity": unique_scaffolds / total_molecules if total_molecules else 0.0,
        "singleton_scaffold_fraction": singleton_scaffolds / unique_scaffolds if unique_scaffolds else 0.0,
        "largest_scaffold_cluster": largest_cluster,
    }


def compare_scaffold_sets(query_scaffolds: Iterable[str], reference_scaffolds: Iterable[str]) -> dict:
    q = set(str(x) for x in query_scaffolds if pd.notna(x))
    r = set(str(x) for x in reference_scaffolds if pd.notna(x))
    overlap = q & r
    novel = q - r
    return {
        "query_unique_scaffolds": len(q),
        "reference_unique_scaffolds": len(r),
        "overlapping_scaffolds": len(overlap),
        "novel_query_scaffolds": len(novel),
        "novel_scaffold_fraction": len(novel) / len(q) if q else 0.0,
    }
