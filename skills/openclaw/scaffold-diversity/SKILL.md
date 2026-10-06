---
name: scaffold-diversity
description: Use when Bemis-Murcko scaffold diversity, scaffold overlap, or library scaffold coverage needs to be assessed.
---

# Scaffold Diversity

## When to use

Use when the user asks about scaffold diversity, scaffold novelty, chemical diversity, or train/test split leakage by scaffold.

## Required behavior

- Prefer deterministic SciAgentKit tools through MCP, CLI, or Python API.
- Never invent molecular, protein, docking, MD, QSAR, or bibliographic values.
- Write outputs into a run directory and report exact file paths.
- Mention limitations clearly when the available tool only performs an audit or preparation step.

## Workflow

1. Use canonical molecules.
2. Extract Bemis-Murcko scaffolds.
3. Count unique scaffolds.
4. Report singleton fraction and largest scaffold cluster.
5. If reference data exists, compute scaffold overlap.

## Expected outputs

- `scaffolds.csv`
- `scaffold_summary.csv`
- `scaffold_comparison.csv`

## Scientific caveat

This skill supports reproducible computational analysis. It does not prove biological activity or clinical relevance.
