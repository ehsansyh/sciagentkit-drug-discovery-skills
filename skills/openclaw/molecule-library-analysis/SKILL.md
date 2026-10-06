---
name: molecule-library-analysis
description: Use when molecular libraries need cleaning, deduplication, descriptor profiling, scaffold analysis, or reproducible reports.
---

# Molecule Library Analysis

## When to use

Use when the user asks to analyze a SMILES library, generated molecules, known actives, or chemical dataset.

## Required behavior

- Prefer deterministic SciAgentKit tools through MCP, CLI, or Python API.
- Never invent molecular, protein, docking, MD, QSAR, or bibliographic values.
- Write outputs into a run directory and report exact file paths.
- Mention limitations clearly when the available tool only performs an audit or preparation step.

## Workflow

1. Validate and canonicalize SMILES.
2. Remove internal canonical duplicates.
3. Calculate descriptors.
4. Extract Bemis-Murcko scaffolds.
5. Generate figures.
6. Write report and manifest.

## Expected outputs

- `canonicalization_report.csv`
- `cleaned_molecules.csv`
- `descriptors.csv`
- `scaffold_summary.csv`
- `figures/`
- `report.md`
- `run_manifest.json`

## Scientific caveat

This skill supports reproducible computational analysis. It does not prove biological activity or clinical relevance.
