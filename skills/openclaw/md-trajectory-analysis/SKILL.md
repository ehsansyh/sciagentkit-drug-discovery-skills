---
name: md-trajectory-analysis
description: Use when MD trajectory analysis needs planning, metric selection, reproducibility notes, or future MDAnalysis-backed summaries.
---

# MD Trajectory Analysis

## When to use

Use when the user asks about RMSD, RMSF, radius of gyration, H-bonds, contact frequency, or replica-level MD reporting.

## Required behavior

- Prefer deterministic SciAgentKit tools through MCP, CLI, or Python API.
- Never invent molecular, protein, docking, MD, QSAR, or bibliographic values.
- Write outputs into a run directory and report exact file paths.
- Mention limitations clearly when the available tool only performs an audit or preparation step.

## Workflow

1. Confirm topology/trajectory files.
2. Align replicas consistently.
3. Exclude flexible/disordered regions when scientifically justified.
4. Compute RMSD/RMSF/contact summaries with deterministic tools.
5. Write replica-level and pooled summaries.

## Expected outputs

- RMSD/RMSF tables
- contact frequency tables
- replica summary report
- methods text

## Scientific caveat

This skill supports reproducible computational analysis. It does not prove biological activity or clinical relevance.
