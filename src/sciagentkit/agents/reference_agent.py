from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentStep:
    index: int
    name: str
    tool: str
    purpose: str


MOLECULE_ANALYST_WORKFLOW = [
    AgentStep(1, "Load inputs", "read_smiles_file", "Read generated/query and reference/training SMILES libraries."),
    AgentStep(2, "Canonicalize", "clean_canonical_library", "Validate structures and compute canonical SMILES."),
    AgentStep(3, "Deduplicate", "clean_canonical_library", "Remove internal canonical duplicates in each library."),
    AgentStep(4, "Compare novelty", "compute_library_overlap", "Identify exact cross-duplicates and novel query molecules."),
    AgentStep(5, "Profile descriptors", "calculate_descriptor_table", "Compute MW, cLogP, QED, TPSA, HBD, HBA, rotatable bonds, and related flags."),
    AgentStep(6, "Analyze scaffolds", "scaffold_summary", "Calculate Bemis-Murcko scaffold diversity and scaffold overlap."),
    AgentStep(7, "Generate figures", "make_property_comparison_figures", "Create publication-ready property comparison plots."),
    AgentStep(8, "Write report", "write_markdown_report", "Summarize exact outputs and scientific caveats."),
    AgentStep(9, "Record manifest", "write_manifest", "Hash inputs/outputs and capture environment metadata."),
]


def molecule_analyst_plan() -> list[dict]:
    """Return the reference agent plan without calling an LLM."""
    return [step.__dict__ for step in MOLECULE_ANALYST_WORKFLOW]
