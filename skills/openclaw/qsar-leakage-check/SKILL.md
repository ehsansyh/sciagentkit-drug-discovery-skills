---
name: qsar-leakage-check
description: Use when QSAR datasets need duplicate, split, scaffold, or train-test leakage checks before modeling.
---

# QSAR Leakage Check

## When to use

Use when the user asks whether a QSAR/ML dataset split is valid or may contain leakage.

## Required behavior

- Prefer deterministic SciAgentKit tools through MCP, CLI, or Python API.
- Never invent molecular, protein, docking, MD, QSAR, or bibliographic values.
- Write outputs into a run directory and report exact file paths.
- Mention limitations clearly when the available tool only performs an audit or preparation step.

## Workflow

1. Canonicalize train/validation/test molecules.
2. Detect exact cross-split duplicates.
3. Compare scaffold overlap.
4. Summarize class balance and property drift when activity labels are available.
5. Flag risky claims.

## Expected outputs

- duplicate report
- scaffold overlap report
- dataset audit report
- recommendations

## Scientific caveat

This skill supports reproducible computational analysis. It does not prove biological activity or clinical relevance.
