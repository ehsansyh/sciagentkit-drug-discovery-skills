"""The open-source core must stand on its own.

It ships no licensing code and no paid skills, always serves the free tools, and
keeps serving them when an add-on plugin is broken.
"""
from __future__ import annotations

import asyncio
import importlib.util

FREE_TOOLS = {
    "canonicalize", "descriptors", "bemis_murcko_scaffold", "adme_tox",
    "analyze_library", "compare_libraries", "audit_generated_library",
    "literature_search", "protein_select", "fetch_pdb", "prepare_ligands",
    "prepare_receptor_docking", "prepare_receptor_md", "detect_pocket", "ligand_md_readiness",
}

ENTERPRISE_ONLY_MODULES = [
    "sciagentkit.licensing", "sciagentkit.activation", "sciagentkit.edition",
    "sciagentkit.skills.docking", "sciagentkit.skills.docking_pipeline", "sciagentkit.skills.md_workflow",
    "sciagentkit.skills.trajectory_analysis", "sciagentkit.skills.hit_selection", "sciagentkit.skills.wetlab",
    "sciagentkit.skills.screening_pipeline", "sciagentkit.skills.final_report",
]


def test_core_ships_no_licensing_or_paid_modules():
    for module in ENTERPRISE_ONLY_MODULES:
        assert importlib.util.find_spec(module) is None, module


def test_server_serves_every_free_tool():
    from sciagentkit.servers.rdkit_server import mcp

    names = {tool.name for tool in asyncio.run(mcp.list_tools())}
    assert FREE_TOOLS <= names


def test_broken_plugin_is_reported_and_skipped(monkeypatch, capsys):
    from sciagentkit.servers import rdkit_server

    class BrokenEntryPoint:
        name = "broken"

        def load(self):
            raise ImportError("boom")

    monkeypatch.setattr(rdkit_server, "entry_points", lambda group: [BrokenEntryPoint()])
    assert rdkit_server._load_plugins() == []
    assert "broken" in capsys.readouterr().err
