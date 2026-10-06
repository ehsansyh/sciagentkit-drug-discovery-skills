---
name: report
description: Use when SciAgentKit run outputs need to become a reproducible markdown, DOCX, or PDF report.
---

> **Requires SciAgentKit Enterprise.** The docking, MD, trajectory, hit-ranking, wet-lab and report tools this skill relies on are part of SciAgentKit Enterprise (https://sciagentkit.com). If they are not in your tool list, run only the free steps, tell the user the rest requires Enterprise, and never simulate the missing results.


# SciAgentKit final report

Preferred MCP tool: `write_report`.
Preferred CLI fallback:
```bash
sciagent write-report <project_dir> --docx --pdf
```

Workflow:
1. Collect existing SciAgentKit outputs under the project directory.
2. Write final report from actual files.
3. Include limitations and missing stages explicitly.

## Output rules
- Save all outputs under `runs/` unless the user gives another safe project-relative path.
- Preserve `run_manifest.json`.
- Report exact generated files.
- If an external binary or Python package is missing, report it clearly and continue with the safest available fallback.
- Never invent molecular descriptors, UniProt/PDB metadata, docking scores, RMSD/RMSF values, or interaction frequencies.
