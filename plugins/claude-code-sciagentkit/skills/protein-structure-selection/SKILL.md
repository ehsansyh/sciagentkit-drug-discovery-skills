---
name: protein-structure-selection
description: Use when choosing or ranking PDB structures for a UniProt target, protein variant, mutation set, or docking-ready receptor workflow.
---

# SciAgentKit protein/PDB selection

Use this when the user asks which PDB structure to use for a target or mutant protein.

Preferred MCP tool: `protein_select`.
Preferred CLI fallback:
```bash
sciagent protein-select <target-or-uniprot> --mutation <MUT> --out runs/<target>/protein
```

Ranking policy:
1. If mutation is requested, prefer structures/chains matching the mutated sequence or compatible after in silico mutation.
2. Rank by mutation match, residue coverage/span, lower resolution, then sequence identity.
3. Report selected PDB ID, chain, residue span, coverage, resolution, sequence identity, and limitations.
4. If no suitable PDB exists, recommend AlphaFold/modeling path instead of pretending.

## Output rules
- Save all outputs under `runs/` unless the user gives another safe project-relative path.
- Preserve `run_manifest.json`.
- Report exact generated files.
- If an external binary or Python package is missing, report it clearly and continue with the safest available fallback.
- Never invent molecular descriptors, UniProt/PDB metadata, docking scores, RMSD/RMSF values, or interaction frequencies.
