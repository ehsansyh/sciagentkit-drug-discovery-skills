"""No subprocess started from package code may inherit stdin.

Under an MCP stdio server on Windows, a child process that inherits the server's
stdin pipe blocks while the server's reader thread is waiting on that pipe, so the
tool call never returns. Passing ``stdin=subprocess.DEVNULL`` (or ``input=...``)
avoids it.
"""
from __future__ import annotations

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
SPAWNERS = {"run", "check_output", "check_call", "call", "Popen"}


def test_subprocess_calls_do_not_inherit_stdin():
    offenders = []
    for path in sorted(SRC.rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "subprocess"
                and node.func.attr in SPAWNERS
                and not {k.arg for k in node.keywords} & {"stdin", "input"}
            ):
                offenders.append(f"{path.relative_to(SRC).as_posix()}:{node.lineno}")
    assert not offenders, f"pass stdin=subprocess.DEVNULL: {offenders}"
