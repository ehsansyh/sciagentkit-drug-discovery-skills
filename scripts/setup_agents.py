#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _bootstrap_src(root: Path) -> None:
    src = root / "src"
    if src.exists():
        sys.path.insert(0, str(src))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate SciAgentKit agent/MCP config files.")
    parser.add_argument("--root", required=True)
    parser.add_argument("--env-name", default="sciagentkit", help="Accepted for backward compatibility; ignored.")
    parser.add_argument("--use-conda", default="1", help="Accepted for backward compatibility; ignored.")
    parser.add_argument("--tools", default="all", help="Comma-separated tools or all. Default: all.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    _bootstrap_src(root)

    from sciagentkit.agent_config import init_agents, repo_root

    resolved = repo_root(root)
    tools = ["all"] if args.tools == "all" else [tool.strip() for tool in args.tools.split(",") if tool.strip()]
    written = init_agents(resolved, tools)
    for tool, paths in written.items():
        print(f"{tool}: wrote {len(paths)} file(s)")
    print("Generated portable SciAgentKit agent, skill, and MCP config files.")


if __name__ == "__main__":
    main()
