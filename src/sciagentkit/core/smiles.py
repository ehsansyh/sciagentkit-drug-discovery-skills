from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd
from rdkit import Chem


@dataclass(frozen=True)
class SmilesRecord:
    """Canonicalization result for one SMILES string."""

    original_smiles: str
    canonical_smiles: str | None
    is_valid: bool
    error: str | None = None


def canonicalize_smiles(smiles: str, remove_stereo: bool = False) -> SmilesRecord:
    """Convert a SMILES string to an RDKit canonical SMILES string.

    The function is deterministic and does not use a language model.
    """
    original = "" if smiles is None else str(smiles).strip()
    if not original:
        return SmilesRecord(original, None, False, "Empty SMILES")

    try:
        mol = Chem.MolFromSmiles(original)
        if mol is None:
            return SmilesRecord(original, None, False, "RDKit failed to parse SMILES")
        if remove_stereo:
            Chem.RemoveStereochemistry(mol)
        canonical = Chem.MolToSmiles(mol, canonical=True)
        return SmilesRecord(original, canonical, True, None)
    except Exception as exc:  # pragma: no cover - RDKit failures are environment-specific
        return SmilesRecord(original, None, False, str(exc))


def enforce_smiles_limit(n: int, max_molecules: int = 250_000) -> None:
    """Guard against unbounded inputs so an agent cannot exhaust local resources."""
    if n > max_molecules:
        raise ValueError(f"Input contains {n} molecules; limit is {max_molecules} for this local skill.")


def read_smiles_file(
    path: str | Path,
    smiles_column: str = "smiles",
    max_molecules: int = 250_000,
) -> list[str]:
    """Read SMILES from .smi/.txt/.csv/.tsv files.

    For text-like files, the first whitespace-separated token on each line is used.
    For CSV/TSV files, ``smiles_column`` is required. The number of molecules is
    capped by ``max_molecules`` to keep local/agent runs bounded.
    """
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(path)
        if smiles_column not in df.columns:
            raise ValueError(f"Column '{smiles_column}' not found in {path}")
        smiles = df[smiles_column].dropna().astype(str).tolist()
    elif suffix in {".tsv", ".tab"}:
        df = pd.read_csv(path, sep="\t")
        if smiles_column not in df.columns:
            raise ValueError(f"Column '{smiles_column}' not found in {path}")
        smiles = df[smiles_column].dropna().astype(str).tolist()
    else:
        smiles = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            smiles.append(line.split()[0])

    enforce_smiles_limit(len(smiles), max_molecules=max_molecules)
    return smiles


def canonicalization_table(
    smiles_list: Iterable[str],
    remove_stereo: bool = False,
) -> pd.DataFrame:
    """Return a canonicalization report for a SMILES iterable."""
    records = [asdict(canonicalize_smiles(smi, remove_stereo=remove_stereo)) for smi in smiles_list]
    return pd.DataFrame(records, columns=["original_smiles", "canonical_smiles", "is_valid", "error"])


def clean_canonical_library(
    smiles_list: Iterable[str],
    remove_stereo: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Canonicalize, filter invalid structures, and remove internal duplicates.

    Returns
    -------
    report_df:
        Per-input canonicalization table.
    clean_df:
        Valid, canonical-unique molecules. The first occurrence is retained.
    """
    report_df = canonicalization_table(smiles_list, remove_stereo=remove_stereo)
    if report_df.empty:
        clean_df = pd.DataFrame(columns=["canonical_smiles", "first_original_smiles"])
        return report_df, clean_df

    valid = report_df[report_df["is_valid"]].copy()
    valid["first_original_smiles"] = valid["original_smiles"]
    clean_df = (
        valid.drop_duplicates("canonical_smiles")
        .loc[:, ["canonical_smiles", "first_original_smiles"]]
        .reset_index(drop=True)
    )
    return report_df, clean_df


def compute_library_overlap(
    query_smiles: Iterable[str],
    reference_smiles: Iterable[str],
) -> dict:
    """Compute exact canonical overlap and novelty between two molecule sets."""
    qset = set(str(x) for x in query_smiles if pd.notna(x))
    rset = set(str(x) for x in reference_smiles if pd.notna(x))
    overlap = qset & rset
    novel = qset - rset
    return {
        "query_unique": len(qset),
        "reference_unique": len(rset),
        "cross_duplicates": len(overlap),
        "novel_query_molecules": len(novel),
        "novelty_fraction": len(novel) / len(qset) if qset else 0.0,
        "overlap_smiles": sorted(overlap),
        "novel_smiles": sorted(novel),
    }
