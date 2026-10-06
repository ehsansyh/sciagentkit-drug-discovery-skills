"""Deterministic ADME and toxicity/liability profiling.

Everything here is computed by published formulas and RDKit structural catalogs —
never inferred by a language model:

* Aqueous solubility: ESOL (Delaney, J. Chem. Inf. Comput. Sci. 2004).
* Drug-likeness rule sets: Lipinski Ro5, Veber, Ghose, Egan.
* BBB / GI-absorption heuristics: TPSA/MW/HBD-based (labeled as heuristics).
* Structural liability alerts: RDKit FilterCatalog (PAINS + Brenk).
"""
from __future__ import annotations

from typing import Iterable

import pandas as pd
from rdkit import Chem
from rdkit.Chem import Crippen, Descriptors, rdMolDescriptors
from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams

# Build the structural-alert catalogs once, separately so PAINS and Brenk hits
# can be counted independently.
def _catalog(kind) -> FilterCatalog:
    p = FilterCatalogParams()
    p.AddCatalog(kind)
    return FilterCatalog(p)


_PAINS_CATALOG = _catalog(FilterCatalogParams.FilterCatalogs.PAINS)
_BRENK_CATALOG = _catalog(FilterCatalogParams.FilterCatalogs.BRENK)


def _esol_logs(mol, logp: float, mw: float) -> float:
    """ESOL aqueous solubility (log mol/L), Delaney 2004."""
    heavy = mol.GetNumHeavyAtoms()
    aromatic_atoms = sum(1 for a in mol.GetAtoms() if a.GetIsAromatic())
    ap = (aromatic_atoms / heavy) if heavy else 0.0
    rb = rdMolDescriptors.CalcNumRotatableBonds(mol)
    return 0.16 - 0.63 * logp - 0.0062 * mw + 0.066 * rb - 0.74 * ap


def _esol_class(logs: float) -> str:
    if logs > -2:
        return "very soluble"
    if logs > -4:
        return "soluble"
    if logs > -6:
        return "moderately soluble"
    return "poorly soluble"


def calculate_adme_tox(smiles: str) -> dict:
    """Return ADME properties and toxicity/liability alerts for one molecule."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")

    mw = float(Descriptors.MolWt(mol))
    logp = float(Crippen.MolLogP(mol))
    mr = float(Crippen.MolMR(mol))
    tpsa = float(rdMolDescriptors.CalcTPSA(mol))
    hbd = int(rdMolDescriptors.CalcNumHBD(mol))
    hba = int(rdMolDescriptors.CalcNumHBA(mol))
    rb = int(rdMolDescriptors.CalcNumRotatableBonds(mol))
    heavy = int(mol.GetNumHeavyAtoms())
    fcsp3 = float(rdMolDescriptors.CalcFractionCSP3(mol))
    aromatic_rings = int(rdMolDescriptors.CalcNumAromaticRings(mol))

    # --- drug-likeness rule sets ---
    lipinski = int(mw > 500) + int(logp > 5) + int(hbd > 5) + int(hba > 10)
    veber = bool(tpsa <= 140 and rb <= 10)
    ghose = bool(160 <= mw <= 480 and -0.4 <= logp <= 5.6 and 40 <= mr <= 130 and 20 <= heavy <= 70)
    egan = bool(tpsa <= 131.6 and logp <= 5.88)
    druglike_rules_passed = int(lipinski == 0) + int(veber) + int(ghose) + int(egan)

    # --- ADME heuristics ---
    esol = _esol_logs(mol, logp, mw)
    gi_absorption = "High" if (tpsa <= 131.6 and logp <= 5.88) else "Low"  # Egan (BOILED-Egg white)
    # BBB heuristic: small, low-polarity, few donors tend to cross.
    bbb_permeant = bool(tpsa <= 90 and mw <= 450 and hbd <= 3 and 1.0 <= logp <= 4.5)

    # --- toxicity / structural liability alerts ---
    pains_matches = _PAINS_CATALOG.GetMatches(mol)
    brenk_matches = _BRENK_CATALOG.GetMatches(mol)
    pains = len(pains_matches)
    brenk = len(brenk_matches)
    total_alerts = pains + brenk
    example = None
    if pains_matches:
        example = pains_matches[0].GetDescription()
    elif brenk_matches:
        example = brenk_matches[0].GetDescription()

    return {
        "smiles": smiles,
        "mw": mw,
        "logp": logp,
        "tpsa": tpsa,
        "hbd": hbd,
        "hba": hba,
        "rotatable_bonds": rb,
        "fraction_csp3": round(fcsp3, 3),
        "aromatic_rings": aromatic_rings,
        "esol_logS": round(esol, 2),
        "solubility_class": _esol_class(esol),
        "gi_absorption": gi_absorption,
        "bbb_permeant": bbb_permeant,
        "lipinski_violations": lipinski,
        "veber_pass": veber,
        "ghose_pass": ghose,
        "egan_pass": egan,
        "druglike_rules_passed": druglike_rules_passed,
        "pains_alerts": pains,
        "brenk_alerts": brenk,
        "structural_alerts": total_alerts,
        "toxicity_flag": bool(total_alerts > 0),
        "example_alert": example,
    }


_COLUMNS = [
    "smiles", "mw", "logp", "tpsa", "hbd", "hba", "rotatable_bonds", "fraction_csp3",
    "aromatic_rings", "esol_logS", "solubility_class", "gi_absorption", "bbb_permeant",
    "lipinski_violations", "veber_pass", "ghose_pass", "egan_pass", "druglike_rules_passed",
    "pains_alerts", "brenk_alerts", "structural_alerts", "toxicity_flag", "example_alert",
]


def adme_tox_table(smiles_list: Iterable[str]) -> pd.DataFrame:
    """ADME/tox table for valid canonical SMILES (invalid entries are skipped)."""
    rows = []
    for smi in smiles_list:
        try:
            rows.append(calculate_adme_tox(str(smi)))
        except ValueError:
            continue
    return pd.DataFrame(rows, columns=_COLUMNS)


def adme_tox_summary(df: pd.DataFrame) -> dict:
    """Aggregate ADME/tox flags across a library."""
    if df.empty:
        return {"molecules": 0, "bbb_permeant": 0, "high_gi_absorption": 0,
                "with_structural_alerts": 0, "pains_hits": 0, "brenk_hits": 0}
    return {
        "molecules": int(len(df)),
        "bbb_permeant": int(df["bbb_permeant"].sum()),
        "high_gi_absorption": int((df["gi_absorption"] == "High").sum()),
        "with_structural_alerts": int((df["structural_alerts"] > 0).sum()),
        "pains_hits": int((df["pains_alerts"] > 0).sum()),
        "brenk_hits": int((df["brenk_alerts"] > 0).sum()),
        "median_esol_logS": float(df["esol_logS"].median()),
    }
