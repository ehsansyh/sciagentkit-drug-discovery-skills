---
name: literature-to-target
description: Use when literature or biomedical text must be converted into target-selection evidence for computational biology workflows.
---

# Literature to Target

## When to use

Use when the user provides a paper, target gene, disease, or asks for a literature-grounded computational pipeline.

## Required behavior

- Prefer deterministic SciAgentKit tools through MCP, CLI, or Python API.
- Never invent molecular, protein, docking, MD, QSAR, or bibliographic values.
- Write outputs into a run directory and report exact file paths.
- Mention limitations clearly when the available tool only performs an audit or preparation step.

## Workflow

1. Search literature with approved connectors.
2. Extract target, disease, ligand, assay, and model details.
3. Separate direct evidence from inference.
4. Produce target summary and citations.
5. Hand off molecules/proteins to downstream skills.

## Expected outputs

- target summary
- evidence table
- citation list
- downstream workflow plan

## Scientific caveat

This skill supports reproducible computational analysis. It does not prove biological activity or clinical relevance.
