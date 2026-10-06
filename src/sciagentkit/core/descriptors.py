from __future__ import annotations

from typing import Iterable

import pandas as pd
from rdkit import Chem
from rdkit.Chem import Crippen, Descriptors, QED, rdMolDescriptors


def calculate_basic_descriptors(smiles: str) -> dict:
    """Calculate core cheminformatics descriptors for one molecule."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")

    mw = float(Descriptors.MolWt(mol))
    logp = float(Crippen.MolLogP(mol))
    qed = float(QED.qed(mol))
    tpsa = float(rdMolDescriptors.CalcTPSA(mol))
    hbd = int(rdMolDescriptors.CalcNumHBD(mol))
    hba = int(rdMolDescriptors.CalcNumHBA(mol))
    rotatable = int(rdMolDescriptors.CalcNumRotatableBonds(mol))
    heavy_atoms = int(mol.GetNumHeavyAtoms())
    rings = int(rdMolDescriptors.CalcNumRings(mol))

    return {
        "smiles": smiles,
        "mw": mw,
        "logp": logp,
        "qed": qed,
        "tpsa": tpsa,
        "hbd": hbd,
        "hba": hba,
        "rotatable_bonds": rotatable,
        "heavy_atoms": heavy_atoms,
        "rings": rings,
        "lipinski_violations": lipinski_violations(mw, logp, hbd, hba),
        "veber_pass": bool(tpsa <= 140 and rotatable <= 10),
    }


def lipinski_violations(mw: float, logp: float, hbd: int, hba: int) -> int:
    """Count Lipinski rule-of-five violations."""
    return int(mw > 500) + int(logp > 5) + int(hbd > 5) + int(hba > 10)


def calculate_descriptor_table(smiles_list: Iterable[str]) -> pd.DataFrame:
    """Calculate descriptors for a list of canonical SMILES."""
    rows = []
    for smi in smiles_list:
        rows.append(calculate_basic_descriptors(str(smi)))
    columns = [
        "smiles", "mw", "logp", "qed", "tpsa", "hbd", "hba",
        "rotatable_bonds", "heavy_atoms", "rings", "lipinski_violations", "veber_pass",
    ]
    return pd.DataFrame(rows, columns=columns)


def descriptor_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize descriptor distributions with robust statistics."""
    if df.empty:
        return pd.DataFrame(columns=["descriptor", "count", "mean", "std", "min", "p05", "median", "p95", "max"])

    numeric_cols = [c for c in df.columns if c not in {"smiles", "veber_pass"}]
    rows = []
    for col in numeric_cols:
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        if s.empty:
            continue
        rows.append(
            {
                "descriptor": col,
                "count": int(s.shape[0]),
                "mean": float(s.mean()),
                "std": float(s.std(ddof=1)) if s.shape[0] > 1 else 0.0,
                "min": float(s.min()),
                "p05": float(s.quantile(0.05)),
                "median": float(s.median()),
                "p95": float(s.quantile(0.95)),
                "max": float(s.max()),
            }
        )
    return pd.DataFrame(rows)


def compare_descriptor_summaries(query_df: pd.DataFrame, reference_df: pd.DataFrame) -> pd.DataFrame:
    """Compare query/reference descriptor medians and central ranges."""
    rows = []
    for col in ["mw", "logp", "qed", "tpsa", "hbd", "hba", "rotatable_bonds", "heavy_atoms", "rings"]:
        if col not in query_df.columns or col not in reference_df.columns:
            continue
        q = pd.to_numeric(query_df[col], errors="coerce").dropna()
        r = pd.to_numeric(reference_df[col], errors="coerce").dropna()
        if q.empty or r.empty:
            continue
        rows.append(
            {
                "descriptor": col,
                "query_median": float(q.median()),
                "reference_median": float(r.median()),
                "median_delta_query_minus_reference": float(q.median() - r.median()),
                "query_p05": float(q.quantile(0.05)),
                "query_p95": float(q.quantile(0.95)),
                "reference_p05": float(r.quantile(0.05)),
                "reference_p95": float(r.quantile(0.95)),
            }
        )
    return pd.DataFrame(rows)
