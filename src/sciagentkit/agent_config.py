"""One-command agent setup for SciAgentKit.

This module is the single source of truth for wiring SciAgentKit into AI coding
agents (Claude Code, OpenAI Codex, Gemini CLI, Cursor). It also defines the
canonical skill location and a sync helper so every tool gets the *same* skill
files instead of hand-maintained copies that silently drift apart.

Canonical skills live in ``.claude/skills/``. Everything else is generated.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

SUPPORTED_TOOLS = ("claude", "codex", "gemini", "cursor")

AGENT_INSTRUCTIONS = """# SciAgentKit Agent Instructions

Use SciAgentKit MCP tools for computational biology, cheminformatics, target-selection, docking-preparation, MD-planning, trajectory-analysis, and reporting tasks.

Never invent molecular descriptors, QED, MW, logP, TPSA, scaffold diversity, docking scores, UniProt sequences, PDB rankings, RMSD, RMSF, residue interaction frequencies, literature metadata, or citations.

Core workflow rules:
1. For one molecule library, use `analyze_library` (also emits ADME/toxicity: ESOL solubility, drug-likeness, GI/BBB heuristics, PAINS/Brenk alerts).
2. For generated vs reference molecules, use `audit_generated_library`. For ADME/tox of a single molecule, use `adme_tox`.
3. For target and PDB structure selection, use `protein_select`. It ranks structures but does not download coordinates; use `fetch_pdb` to download the selected PDB's coordinate file from RCSB before receptor/pocket/docking steps.
4. For ligand 3D preparation, use `prepare_ligands`.
5. For pocket definition, use `detect_pocket` (crystal-ligand, residues, fpocket, P2Rank, or auto).
6. For receptor preparation, use `prepare_receptor_docking` (docking) or `prepare_receptor_md` (MD) before docking or MD.
7. For docking, use `run_docking` only after receptor and ligand PDBQT files exist (convert prepared PDB/SDF to PDBQT with Open Babel/Meeko first). To run the whole chain from a target name (or PDB id) in one step — `protein_select` -> `fetch_pdb` -> `prepare_ligands` -> `detect_pocket` -> `prepare_receptor_docking` -> PDBQT conversion -> `run_docking` — use `dock_to_target`; it stops gracefully with a `next_action` if Open Babel or a docking engine is missing.
8. To build a protein-ligand complex from a docked pose, use `assemble_docked_complex`.
9. For MD, use `md_plan` (protein/apo) or `ligand_md_plan` (protein-ligand); do not claim MD was run unless trajectory files exist and were analyzed.
10. For trajectory analysis, use `analyze_trajectory`.
11. To rank docked ligands into target-aware best hits (weighting toxicity, drug-likeness, and BBB permeability for CNS targets), use `select_top_hits`.
12. To propose target-aware wet-lab validation experiments (biochemical assay, cell lines, ADME/DMPK, safety) for a ligand/target, use `wet_lab_plan`. These are advisory experimental templates, not results.
13. For final output, use `write_report` (includes a "Recommended wet-lab validation" section).

Note: `protein_select` ranks PDB structures but does not download coordinate files; use `fetch_pdb` (or `dock_to_target`, which calls it) to obtain the PDB before docking or MD.

Pipeline order and mid-pipeline entry: the stages run in the order above. If a request starts mid-pipeline (e.g. "dock these ligands to EGFR"), run the prerequisite earlier stages first — resolve the target/structure (`protein_select`), download it (`fetch_pdb`), prepare ligands, define the pocket, and prepare the receptor — before `run_docking`. Prefer `dock_to_target` to do this backfill automatically.

Enterprise tools: `run_docking`, `dock_to_target`, `assemble_docked_complex`, `md_plan`, `ligand_md_plan`, `ligand_md_run`, `md_run_smoke`, `analyze_trajectory`, `select_top_hits`, `wet_lab_plan`, `target_screen_project`, and `write_report` come from SciAgentKit Enterprise (https://sciagentkit.com). If one of them is not in your tool list, tell the user that step requires SciAgentKit Enterprise and stop there. Never simulate, estimate, or describe its output as if it had run.

Always save workflow outputs under `runs/`.
Always preserve `run_manifest.json`.
Clearly report missing external tools such as OpenBabel, AutoDock Vina, fpocket, OpenMM, MDAnalysis, or ProLIF.
"""

CURSOR_RULE = """---
description: SciAgentKit scientific-agent rules
alwaysApply: true
---

Use the local `sciagentkit` MCP server for scientific calculations. Do not estimate molecular descriptors, scaffold statistics, PDB rankings, docking scores, MD metrics, or literature metadata manually.

Workflow: `analyze_library`/`adme_tox` for molecules; `protein_select` then `fetch_pdb` to obtain a structure; `prepare_ligands`, `detect_pocket`, `prepare_receptor_docking`, then `run_docking`. For a target-to-docking run in one step (backfilling earlier stages when a request enters mid-pipeline), use `dock_to_target`. Then `select_top_hits`, `wet_lab_plan`, and `write_report`. MD via `md_plan`/`ligand_md_plan` + `analyze_trajectory`. Docking, MD, trajectory, hit ranking, wet-lab plans and reports need SciAgentKit Enterprise; if those tools are missing, say so and never simulate their output. Save outputs under `runs/` and preserve `run_manifest.json`.
"""


# --------------------------------------------------------------------------- #
# Paths and shared config
# --------------------------------------------------------------------------- #
def repo_root(start: Path | str | None = None) -> Path:
    """Find the repository root (the directory that contains ``src/sciagentkit``)."""
    here = Path(start).resolve() if start else Path.cwd().resolve()
    for candidate in (here, *here.parents):
        if (candidate / "src" / "sciagentkit").exists():
            return candidate
    return here


def canonical_skills_dir(root: Path) -> Path:
    """The single source of truth for skill definitions."""
    return root / ".claude" / "skills"


def _launcher(root: Path) -> Path:
    return root / "scripts" / "start_mcp.py"


def mcp_server_config(root: Path, *, relative: bool = False) -> dict:
    """Cross-platform MCP server entry (uses the bash-free Python launcher)."""
    if relative:
        launcher, cwd = "scripts/start_mcp.py", "."
    else:
        launcher, cwd = str(_launcher(root)), str(root)
    return {
        "command": "python",
        "args": [launcher],
        "cwd": cwd,
        "env": {"PYTHONUNBUFFERED": "1"},
    }


def codex_config_fragment() -> str:
    """Portable project-local Codex MCP fragment."""
    return (
        "[mcp_servers.sciagentkit]\n"
        'command = "python"\n'
        'args = ["scripts/start_mcp.py"]\n'
        'cwd = "."\n'
        'env = { PYTHONUNBUFFERED = "1" }\n'
    )


# --------------------------------------------------------------------------- #
# Skill sync
# --------------------------------------------------------------------------- #
def sync_skills(root: Path, targets: list[Path]) -> list[Path]:
    """Mirror canonical skills into each target directory. Returns written dirs."""
    source = canonical_skills_dir(root)
    if not source.exists():
        raise FileNotFoundError(f"Canonical skills not found at {source}")
    skill_dirs = sorted(p for p in source.iterdir() if p.is_dir() and (p / "SKILL.md").exists())
    written: list[Path] = []
    for target in targets:
        target.mkdir(parents=True, exist_ok=True)
        for skill in skill_dirs:
            dest = target / skill.name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(skill, dest)
            written.append(dest)
    return written


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _write_json(path: Path, data: dict) -> Path:
    return _write(path, json.dumps(data, indent=2) + "\n")


def _merge_mcp_settings(path: Path, server_cfg: dict) -> Path:
    """Insert/refresh the ``sciagentkit`` server in a JSON settings file."""
    existing: dict = {}
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
    existing.setdefault("mcpServers", {})["sciagentkit"] = server_cfg
    return _write_json(path, existing)


# --------------------------------------------------------------------------- #
# Per-tool initialisers
# --------------------------------------------------------------------------- #
def init_claude(root: Path) -> list[Path]:
    written = [_write(root / "CLAUDE.md", AGENT_INSTRUCTIONS)]
    written.append(_write_json(root / ".mcp.json", {"mcpServers": {"sciagentkit": mcp_server_config(root, relative=True)}}))
    plugin_skills = root / "plugins" / "claude-code-sciagentkit" / "skills"
    if plugin_skills.parent.exists():
        written.extend(sync_skills(root, [plugin_skills]))
    return written


def init_codex(root: Path) -> list[Path]:
    written = [_write(root / "AGENTS.md", AGENT_INSTRUCTIONS)]
    fragment = codex_config_fragment()
    written.append(_write(root / "codex_config.fragment.toml", fragment))
    written.append(_write(root / ".codex" / "config.toml", fragment))
    written.extend(sync_skills(root, [root / ".agents" / "skills", root / ".codex" / "skills"]))
    return written


def init_gemini(root: Path) -> list[Path]:
    written = [_write(root / "GEMINI.md", AGENT_INSTRUCTIONS)]
    written.append(_merge_mcp_settings(root / ".gemini" / "settings.json", mcp_server_config(root, relative=True)))
    written.extend(sync_skills(root, [root / ".gemini" / "skills"]))
    return written


def init_cursor(root: Path) -> list[Path]:
    written = [_write(root / ".cursor" / "rules" / "sciagentkit.mdc", CURSOR_RULE)]
    written.append(_write_json(root / ".mcp" / "sciagentkit.json", {"mcpServers": {"sciagentkit": mcp_server_config(root, relative=True)}}))
    return written


_INITIALISERS = {
    "claude": init_claude,
    "codex": init_codex,
    "gemini": init_gemini,
    "cursor": init_cursor,
}


def init_agents(root: Path, tools: list[str]) -> dict[str, list[Path]]:
    """Run the initialiser(s) for the requested tool(s)."""
    if tools == ["all"]:
        tools = list(SUPPORTED_TOOLS)
    unknown = [t for t in tools if t not in _INITIALISERS]
    if unknown:
        raise ValueError(f"Unknown tool(s): {', '.join(unknown)}. Choose from: {', '.join(SUPPORTED_TOOLS)} or 'all'.")
    return {tool: _INITIALISERS[tool](root) for tool in tools}
