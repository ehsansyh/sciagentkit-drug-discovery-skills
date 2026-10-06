from __future__ import annotations

from pathlib import Path


def safe_run_output_dir(output_dir: str | Path, *, root: str | Path | None = None) -> Path:
    """Return a normalized output directory under ``runs/`` or raise ValueError.

    MCP clients pass paths as strings. Keep workflow artifacts in a predictable
    project-local run tree instead of trusting arbitrary model-provided paths.
    """
    project_root = Path(root).resolve() if root is not None else Path.cwd().resolve()
    candidate = Path(output_dir)
    if not candidate.is_absolute():
        candidate = project_root / candidate
    resolved = candidate.resolve(strict=False)
    runs_root = (project_root / "runs").resolve(strict=False)
    try:
        resolved.relative_to(runs_root)
    except ValueError as exc:
        raise ValueError(f"SciAgentKit workflow outputs must stay under {runs_root}") from exc
    return resolved
