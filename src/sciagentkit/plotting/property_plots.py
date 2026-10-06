from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DEFAULT_PROPERTIES = ["qed", "mw", "logp", "tpsa", "hbd", "hba", "rotatable_bonds"]


def _format_label(column: str) -> str:
    labels = {
        "qed": "QED",
        "mw": "Molecular weight",
        "logp": "cLogP",
        "tpsa": "TPSA",
        "hbd": "H-bond donors",
        "hba": "H-bond acceptors",
        "rotatable_bonds": "Rotatable bonds",
    }
    return labels.get(column, column.replace("_", " ").title())


def plot_property_distribution(df: pd.DataFrame, column: str, out_path: str | Path, title: str | None = None) -> Path:
    """Save a clean single-library descriptor distribution plot."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.2, 4.2), dpi=300)
    ax.hist(pd.to_numeric(df[column], errors="coerce").dropna(), bins=40, alpha=0.85)
    ax.set_xlabel(_format_label(column))
    ax.set_ylabel("Molecule count")
    ax.set_title(title or f"{_format_label(column)} distribution")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_property_comparison(
    query_df: pd.DataFrame,
    reference_df: pd.DataFrame,
    column: str,
    out_path: str | Path,
    query_label: str = "Query",
    reference_label: str = "Reference",
) -> Path:
    """Save overlayed query/reference descriptor distribution plot."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.2, 4.2), dpi=300)
    q = pd.to_numeric(query_df[column], errors="coerce").dropna()
    r = pd.to_numeric(reference_df[column], errors="coerce").dropna()
    ax.hist(r, bins=40, alpha=0.45, density=True, label=reference_label)
    ax.hist(q, bins=40, alpha=0.55, density=True, label=query_label)
    ax.set_xlabel(_format_label(column))
    ax.set_ylabel("Density")
    ax.set_title(f"{_format_label(column)} comparison")
    ax.legend(frameon=False, loc="best")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out_path


def make_default_property_figures(df: pd.DataFrame, out_dir: str | Path) -> list[Path]:
    out_dir = Path(out_dir)
    paths = []
    for column in DEFAULT_PROPERTIES:
        if column in df.columns and not df.empty:
            paths.append(plot_property_distribution(df, column, out_dir / f"{column}_distribution.png"))
    return paths


def make_property_comparison_figures(
    query_df: pd.DataFrame,
    reference_df: pd.DataFrame,
    out_dir: str | Path,
) -> list[Path]:
    out_dir = Path(out_dir)
    paths = []
    for column in DEFAULT_PROPERTIES:
        if column in query_df.columns and column in reference_df.columns:
            paths.append(plot_property_comparison(query_df, reference_df, column, out_dir / f"{column}_comparison.png"))
    return paths
