from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def get_git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], stdin=subprocess.DEVNULL, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def package_version(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def write_manifest(
    out_dir: str | Path,
    input_files: list[str | Path],
    command: str,
    parameters: dict | None = None,
    workflow_name: str | None = None,
) -> Path:
    """Write a reproducibility manifest with input hashes and package versions."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    parameters = parameters or {}

    outputs = []
    for path in sorted(out_dir.rglob("*")):
        if path.is_file() and path.name != "run_manifest.json":
            outputs.append({"path": path.relative_to(out_dir).as_posix(), "sha256": file_sha256(path)})

    manifest = {
        "schema_version": "sciagentkit.manifest.v1",
        "workflow_name": workflow_name,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": command,
        "parameters": parameters,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "git_commit": get_git_commit(),
        "packages": {
            "sciagentkit": package_version("sciagentkit"),
            "rdkit": package_version("rdkit"),
            "pandas": package_version("pandas"),
            "numpy": package_version("numpy"),
            "matplotlib": package_version("matplotlib"),
        },
        "input_files": [
            {"path": str(Path(path)), "sha256": file_sha256(Path(path))}
            for path in input_files
            if Path(path).exists()
        ],
        "output_files": outputs,
        "note": "Molecular values were computed by deterministic tools, not inferred by an LLM.",
    }
    path = out_dir / "run_manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path
