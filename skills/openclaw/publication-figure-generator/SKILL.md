---
name: publication-figure-generator
description: Use when molecular property distributions, comparisons, or workflow outputs need publication-ready figures.
---

# Publication Figure Generator

## When to use

Use when the user asks for Nature/JCIM-style descriptor figures or clear property comparison plots.

## Required behavior

- Prefer deterministic SciAgentKit tools through MCP, CLI, or Python API.
- Never invent molecular, protein, docking, MD, QSAR, or bibliographic values.
- Write outputs into a run directory and report exact file paths.
- Mention limitations clearly when the available tool only performs an audit or preparation step.

## Workflow

1. Load descriptor table.
2. Plot QED, MW, cLogP, TPSA, HBD, HBA, rotatable bonds.
3. Avoid overlapping legends and labels.
4. Save high-DPI PNG outputs.

## Expected outputs

- `figures/qed_distribution.png`
- `figures/mw_distribution.png`
- `figures/logp_distribution.png`
- comparison figures when reference data exists

## Scientific caveat

This skill supports reproducible computational analysis. It does not prove biological activity or clinical relevance.
