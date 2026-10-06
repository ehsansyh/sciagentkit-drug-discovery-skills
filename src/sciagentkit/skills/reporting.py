from __future__ import annotations

from pathlib import Path


def _fmt(value) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def write_markdown_report(
    out_dir: str | Path,
    title: str,
    summary: dict,
    generated_files: list[str] | None = None,
    interpretation: list[str] | None = None,
) -> Path:
    """Write a structured Markdown report for a workflow run."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    generated_files = generated_files or []
    interpretation = interpretation or []

    lines = [f"# {title}", "", "## Executive summary", ""]
    for key, value in summary.items():
        if isinstance(value, (list, dict)):
            continue
        lines.append(f"- **{key.replace('_', ' ')}**: {_fmt(value)}")

    if interpretation:
        lines.extend(["", "## Automated interpretation", ""])
        for item in interpretation:
            lines.append(f"- {item}")

    if generated_files:
        lines.extend(["", "## Generated files", ""])
        for file in generated_files:
            lines.append(f"- `{file}`")

    lines.extend(
        [
            "",
            "## Scientific reproducibility note",
            "",
            "This report was produced by deterministic SciAgentKit skills. Molecular properties were computed with RDKit and workflow inputs were recorded in `run_manifest.json`. Language models may be used for planning or summarization, but they must not invent molecular descriptors, docking scores, scaffold counts, or novelty values.",
        ]
    )
    path = out_dir / "report.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_methods_stub(out_dir: str | Path) -> Path:
    """Write a reusable methods paragraph for manuscript drafting."""
    text = (
        "Molecular libraries were standardized using RDKit-based canonical SMILES generation. "
        "Invalid structures were excluded and internal canonical duplicates were removed before downstream analysis. "
        "Physicochemical descriptors including molecular weight, cLogP, QED, TPSA, hydrogen-bond donors and acceptors, rotatable bonds, heavy atom count, and ring count were calculated with RDKit. "
        "Bemis-Murcko scaffolds were extracted to summarize scaffold diversity. "
        "When a reference library was provided, exact canonical overlap was used to estimate novelty and cross-duplicate burden. "
        "All workflow inputs and generated files were hashed and recorded in a reproducibility manifest.\n"
    )
    path = Path(out_dir) / "methods_section.md"
    path.write_text(text, encoding="utf-8")
    return path
