from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ForceFieldRecommendation:
    protein_forcefield: str
    water_model: str
    ligand_forcefield: str
    conformer_forcefield: str
    rationale: str
    caveats: str


DEFAULT_RECOMMENDATIONS = {
    "general": ForceFieldRecommendation(
        protein_forcefield="amber14/protein.ff14SB.xml",
        water_model="amber14/tip3p.xml",
        ligand_forcefield="openff-2.2.0",
        conformer_forcefield="MMFF94",
        rationale="Balanced default for soluble globular proteins and small-molecule ligands in OpenMM-compatible workflows.",
        caveats="Metalloproteins, covalent inhibitors, membranes, glycoproteins, cofactors, and unusual protonation states need expert review.",
    ),
    "kinase": ForceFieldRecommendation(
        protein_forcefield="amber14/protein.ff14SB.xml",
        water_model="amber14/tip3p.xml",
        ligand_forcefield="openff-2.2.0",
        conformer_forcefield="MMFF94",
        rationale="Practical kinase-ligand default. Validate active/inactive conformation, DFG state, cofactors, and crystallographic waters.",
        caveats="Force fields do not fix a wrong receptor conformation. Yes, biology remains annoying.",
    ),
    "membrane": ForceFieldRecommendation(
        protein_forcefield="charmm36.xml",
        water_model="charmm36/water.xml",
        ligand_forcefield="openff-2.2.0 or CGenFF",
        conformer_forcefield="MMFF94",
        rationale="Membrane proteins usually need lipid-aware force fields and explicit membrane placement.",
        caveats="SciAgentKit v1.0 creates a plan; specialized membrane preparation still needs manual validation.",
    ),
}


def recommend_forcefield(target_family: str | None = None) -> dict:
    key = (target_family or "general").lower()
    if key not in DEFAULT_RECOMMENDATIONS:
        key = "general"
    return asdict(DEFAULT_RECOMMENDATIONS[key])
