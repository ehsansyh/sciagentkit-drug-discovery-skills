#!/usr/bin/env python
"""Cross-platform launcher for the SciAgentKit MCP server.

Works on Windows, macOS, and Linux without requiring ``bash``. It mirrors the
behaviour of ``scripts/start_mcp.sh`` so the same ``.mcp.json`` entry can be used
by Claude Code, Codex, Gemini CLI, and Cursor on any operating system.

Interpreter selection priority:
1. ``SCIAGENTKIT_PYTHON`` environment variable (explicit override).
2. A project ``.venv`` if one exists (``.venv/Scripts/python.exe`` on Windows,
   ``.venv/bin/python`` elsewhere).
3. The current interpreter, with ``src/`` injected onto the import path.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

MODULE = "sciagentkit.servers.rdkit_server"


def project_dir() -> Path:
    """Locate the repository root that contains ``src/sciagentkit``."""
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        candidate = Path(env).resolve()
        if (candidate / "src" / "sciagentkit").exists():
            return candidate
    # scripts/ lives one level below the repo root (root and plugin layouts).
    here = Path(__file__).resolve()
    for parent in (here.parent.parent, here.parent.parent.parent):
        if (parent / "src" / "sciagentkit").exists():
            return parent
    return here.parent.parent


def preferred_python(root: Path) -> str | None:
    explicit = os.environ.get("SCIAGENTKIT_PYTHON")
    if explicit:
        return explicit
    if os.name == "nt":
        venv = root / ".venv" / "Scripts" / "python.exe"
    else:
        venv = root / ".venv" / "bin" / "python"
    return str(venv) if venv.exists() else None


def main() -> int:
    root = project_dir()
    src = root / "src"

    chosen = preferred_python(root)
    if chosen and Path(chosen).resolve() != Path(sys.executable).resolve():
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(
            [str(src), env["PYTHONPATH"]] if env.get("PYTHONPATH") else [str(src)]
        )
        env.setdefault("PYTHONUNBUFFERED", "1")
        # Inherit stdio so the MCP stdio transport passes through unchanged.
        return subprocess.call([chosen, "-m", MODULE], cwd=str(root), env=env)

    # Run in-process with the current interpreter.
    sys.path.insert(0, str(src))
    os.chdir(root)
    from sciagentkit.servers.rdkit_server import mcp

    mcp.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
