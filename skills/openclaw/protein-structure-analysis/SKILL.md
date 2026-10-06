---
name: protein-structure-analysis
description: Use when protein metadata, structure source choices, mutation context, or preparation decisions need to be organized.
---

# Protein Structure Analysis

## When to use

Use when the user asks about PDB, UniProt, AlphaFold, mutations, domains, missing residues, or structure preparation.

## Required behavior

- Prefer deterministic SciAgentKit tools through MCP, CLI, or Python API.
- Never invent molecular, protein, docking, MD, QSAR, or bibliographic values.
- Write outputs into a run directory and report exact file paths.
- Mention limitations clearly when the available tool only performs an audit or preparation step.

## Workflow

1. Fetch/inspect protein identifiers.
2. Map sequence, domains, mutations, and structure source.
3. Flag missing loops, low-confidence regions, ligands, cofactors, and chain choices.
4. Prepare handoff to docking or MD workflows.

## Expected outputs

- protein metadata summary
- structure preparation checklist
- caveats

## Scientific caveat

This skill supports reproducible computational analysis. It does not prove biological activity or clinical relevance.
