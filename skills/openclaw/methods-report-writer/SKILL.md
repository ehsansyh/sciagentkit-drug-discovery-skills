---
name: methods-report-writer
description: Use when deterministic workflow outputs need manuscript-style methods, reproducibility text, or run reports.
---

# Methods and Report Writer

## When to use

Use when the user asks for methods text, supplementary report, figure caption, or reproducibility summary.

## Required behavior

- Prefer deterministic SciAgentKit tools through MCP, CLI, or Python API.
- Never invent molecular, protein, docking, MD, QSAR, or bibliographic values.
- Write outputs into a run directory and report exact file paths.
- Mention limitations clearly when the available tool only performs an audit or preparation step.

## Workflow

1. Read output CSV/JSON files.
2. Use exact values from files.
3. Write methods text and result summary.
4. Include limitations.
5. Reference `run_manifest.json`.

## Expected outputs

- `methods_section.md`
- `report.md`
- figure captions
- limitations section

## Scientific caveat

This skill supports reproducible computational analysis. It does not prove biological activity or clinical relevance.
