#!/usr/bin/env python
"""Cross-platform launcher for the SciAgentKit MCP server (Claude Code plugin).

Works on Windows, macOS, and Linux without requiring ``bash``. The plugin is
installed outside the repository, so the repository root is resolved primarily
from ``CLAUDE_PROJECT_DIR`` (the directory Claude Code was launched in).

Interpreter selection priority:
1. ``SCIAGENTKIT_PYTHON`` environment variable (explicit override).
2. A project ``.venv`` if one exists.
3. The current interpreter, with ``src/`` injected onto the import path.

The server always runs in the user's project directory, so relative inputs and
``runs/`` outputs resolve there, never inside the plugin's install location.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

MODULE = "sciagentkit.servers.rdkit_server"


def project_dir() -> Path:
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        candidate = Path(env).resolve()
        if (candidate / "src" / "sciagentkit").exists():
            return candidate
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "src" / "sciagentkit").exists():
            return parent
    return Path.cwd()


def preferred_python(root: Path) -> str | None:
    explicit = os.environ.get("SCIAGENTKIT_PYTHON")
    if explicit:
        return explicit
    if os.name == "nt":
        venv = root / ".venv" / "Scripts" / "python.exe"
    else:
        venv = root / ".venv" / "bin" / "python"
    return str(venv) if venv.exists() else None


def work_dir() -> Path:
    """The user's project: where relative paths and ``runs/`` resolve."""
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    return Path(env).resolve() if env else Path.cwd()


def main() -> int:
    root = project_dir()
    src = root / "src"
    workdir = work_dir()

    chosen = preferred_python(workdir)
    if chosen and Path(chosen).resolve() != Path(sys.executable).resolve():
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(
            [str(src), env["PYTHONPATH"]] if env.get("PYTHONPATH") else [str(src)]
        )
        env.setdefault("PYTHONUNBUFFERED", "1")
        return subprocess.call([chosen, "-m", MODULE], cwd=str(workdir), env=env)

    sys.path.insert(0, str(src))
    os.chdir(workdir)
    from sciagentkit.servers.rdkit_server import mcp

    mcp.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
