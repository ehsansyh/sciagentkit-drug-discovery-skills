from __future__ import annotations

from pathlib import Path

import pandas as pd

from sciagentkit.core.adme_tox import adme_tox_summary, adme_tox_table
from sciagentkit.core.descriptors import (
    calculate_descriptor_table,
    compare_descriptor_summaries,
    descriptor_summary,
)
from sciagentkit.core.manifest import write_manifest
from sciagentkit.core.scaffolds import compare_scaffold_sets, scaffold_summary, scaffold_table
from sciagentkit.core.smiles import clean_canonical_library, compute_library_overlap, read_smiles_file
from sciagentkit.plotting.property_plots import (
    make_default_property_figures,
    make_property_comparison_figures,
)
from sciagentkit.skills.reporting import write_markdown_report, write_methods_stub


def profile_ligand_library(
    smiles_file: str | Path,
    out_dir: str | Path,
    smiles_column: str = "smiles",
    remove_stereo: bool = False,
    make_figures: bool = True,
) -> dict:
    """Clean, deduplicate, profile, plot, and report a ligand library."""
    smiles_file = Path(smiles_file)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_smiles = read_smiles_file(smiles_file, smiles_column=smiles_column)
    report_df, clean_df = clean_canonical_library(raw_smiles, remove_stereo=remove_stereo)
    canonical_smiles = clean_df["canonical_smiles"].tolist() if not clean_df.empty else []

    descriptor_df = calculate_descriptor_table(canonical_smiles)
    summary_df = descriptor_summary(descriptor_df)
    scaffold_df = scaffold_table(canonical_smiles)
    scaffold_stats = scaffold_summary(canonical_smiles)
    adme_df = adme_tox_table(canonical_smiles)
    adme_stats = adme_tox_summary(adme_df)

    report_df.to_csv(out_dir / "canonicalization_report.csv", index=False)
    clean_df.to_csv(out_dir / "cleaned_molecules.csv", index=False)
    descriptor_df.to_csv(out_dir / "descriptors.csv", index=False)
    summary_df.to_csv(out_dir / "descriptor_summary.csv", index=False)
    scaffold_df.to_csv(out_dir / "scaffolds.csv", index=False)
    pd.DataFrame([scaffold_stats]).to_csv(out_dir / "scaffold_summary.csv", index=False)
    adme_df.to_csv(out_dir / "adme_tox.csv", index=False)
    pd.DataFrame([adme_stats]).to_csv(out_dir / "adme_tox_summary.csv", index=False)

    figure_paths: list[Path] = []
    if make_figures and not descriptor_df.empty:
        figure_paths = make_default_property_figures(descriptor_df, out_dir / "figures")

    valid_molecules = int(report_df["is_valid"].sum()) if not report_df.empty else 0
    stats = {
        "input_molecules": len(raw_smiles),
        "valid_molecules": valid_molecules,
        "invalid_molecules": len(raw_smiles) - valid_molecules,
        "canonical_unique_molecules": len(canonical_smiles),
        "internal_duplicates_removed": valid_molecules - len(canonical_smiles),
        **scaffold_stats,
        "adme_bbb_permeant": adme_stats.get("bbb_permeant", 0),
        "adme_high_gi_absorption": adme_stats.get("high_gi_absorption", 0),
        "adme_with_structural_alerts": adme_stats.get("with_structural_alerts", 0),
    }

    interpretation = []
    if stats["invalid_molecules"]:
        interpretation.append("Invalid SMILES were detected and excluded before descriptor calculation.")
    if stats["internal_duplicates_removed"]:
        interpretation.append("Canonical duplicates were present and removed; use the canonicalization report to audit exact entries.")
    if stats["scaffold_diversity"] < 0.1 and stats["total_molecules"] > 100:
        interpretation.append("Scaffold diversity is low for a medium/large library; inspect scaffold clustering before overclaiming novelty.")
    if adme_stats.get("with_structural_alerts"):
        interpretation.append(f"{adme_stats['with_structural_alerts']} molecule(s) carry PAINS/Brenk structural alerts (see adme_tox.csv); review before prioritizing.")

    generated_files = [
        "canonicalization_report.csv",
        "cleaned_molecules.csv",
        "descriptors.csv",
        "descriptor_summary.csv",
        "scaffolds.csv",
        "scaffold_summary.csv",
        "adme_tox.csv",
        "adme_tox_summary.csv",
        *[path.relative_to(out_dir).as_posix() for path in figure_paths],
        "methods_section.md",
        "report.md",
        "run_manifest.json",
    ]

    write_methods_stub(out_dir)
    write_markdown_report(out_dir, "SciAgentKit ligand library profile", stats, generated_files, interpretation)
    write_manifest(
        out_dir,
        [smiles_file],
        command=f"sciagent analyze-smiles {smiles_file} --out {out_dir}",
        parameters={"smiles_column": smiles_column, "remove_stereo": remove_stereo},
        workflow_name="ligand_library_profile",
    )

    return {"output_dir": str(out_dir), "summary": stats, "generated_files": generated_files}


def compare_ligand_libraries(
    query_file: str | Path,
    reference_file: str | Path,
    out_dir: str | Path,
    query_smiles_column: str = "smiles",
    reference_smiles_column: str = "smiles",
    remove_stereo: bool = False,
    make_figures: bool = True,
) -> dict:
    """Compare a query/generated molecule set against a reference library."""
    query_file = Path(query_file)
    reference_file = Path(reference_file)
    out_dir = Path(out_dir)
    query_dir = out_dir / "query"
    reference_dir = out_dir / "reference"
    out_dir.mkdir(parents=True, exist_ok=True)

    query_result = profile_ligand_library(
        query_file,
        query_dir,
        smiles_column=query_smiles_column,
        remove_stereo=remove_stereo,
        make_figures=make_figures,
    )
    reference_result = profile_ligand_library(
        reference_file,
        reference_dir,
        smiles_column=reference_smiles_column,
        remove_stereo=remove_stereo,
        make_figures=make_figures,
    )

    query_clean = pd.read_csv(query_dir / "cleaned_molecules.csv")
    reference_clean = pd.read_csv(reference_dir / "cleaned_molecules.csv")
    overlap = compute_library_overlap(query_clean["canonical_smiles"], reference_clean["canonical_smiles"])

    pd.DataFrame(
        {
            "metric": ["query_unique", "reference_unique", "cross_duplicates", "novel_query_molecules", "novelty_fraction"],
            "value": [
                overlap["query_unique"],
                overlap["reference_unique"],
                overlap["cross_duplicates"],
                overlap["novel_query_molecules"],
                overlap["novelty_fraction"],
            ],
        }
    ).to_csv(out_dir / "novelty_report.csv", index=False)
    pd.DataFrame({"canonical_smiles": overlap["overlap_smiles"]}).to_csv(out_dir / "cross_duplicates.csv", index=False)
    pd.DataFrame({"canonical_smiles": overlap["novel_smiles"]}).to_csv(out_dir / "novel_query_molecules.csv", index=False)

    query_desc = pd.read_csv(query_dir / "descriptors.csv")
    reference_desc = pd.read_csv(reference_dir / "descriptors.csv")
    descriptor_comparison = compare_descriptor_summaries(query_desc, reference_desc)
    descriptor_comparison.to_csv(out_dir / "descriptor_comparison.csv", index=False)

    query_scaffolds = pd.read_csv(query_dir / "scaffolds.csv")
    reference_scaffolds = pd.read_csv(reference_dir / "scaffolds.csv")
    scaffold_comparison = compare_scaffold_sets(
        query_scaffolds["bemis_murcko_scaffold"],
        reference_scaffolds["bemis_murcko_scaffold"],
    )
    pd.DataFrame([scaffold_comparison]).to_csv(out_dir / "scaffold_comparison.csv", index=False)

    comparison_figures: list[Path] = []
    if make_figures and not query_desc.empty and not reference_desc.empty:
        comparison_figures = make_property_comparison_figures(query_desc, reference_desc, out_dir / "figures")

    stats = {
        "query_unique": overlap["query_unique"],
        "reference_unique": overlap["reference_unique"],
        "cross_duplicates": overlap["cross_duplicates"],
        "novel_query_molecules": overlap["novel_query_molecules"],
        "novelty_fraction": overlap["novelty_fraction"],
        **scaffold_comparison,
    }

    interpretation = []
    if stats["cross_duplicates"]:
        interpretation.append("Exact canonical cross-duplicates were found between query and reference libraries.")
    if stats["novelty_fraction"] < 0.8 and stats["query_unique"] > 10:
        interpretation.append("Novelty fraction is below 0.80; inspect training/reference leakage before making generation claims.")
    if stats["novel_scaffold_fraction"] < 0.5 and stats["query_unique_scaffolds"] > 10:
        interpretation.append("Many query scaffolds overlap with the reference set; scaffold-level novelty should be reported separately from molecule-level novelty.")

    generated_files = [
        "query/",
        "reference/",
        "novelty_report.csv",
        "cross_duplicates.csv",
        "novel_query_molecules.csv",
        "descriptor_comparison.csv",
        "scaffold_comparison.csv",
        *[path.relative_to(out_dir).as_posix() for path in comparison_figures],
        "report.md",
        "run_manifest.json",
    ]

    write_markdown_report(out_dir, "SciAgentKit ligand library comparison", stats, generated_files, interpretation)
    write_manifest(
        out_dir,
        [query_file, reference_file],
        command=f"sciagent compare-libraries {query_file} {reference_file} --out {out_dir}",
        parameters={"remove_stereo": remove_stereo},
        workflow_name="ligand_library_comparison",
    )

    return {
        "output_dir": str(out_dir),
        "summary": stats,
        "query_result": query_result,
        "reference_result": reference_result,
        "generated_files": generated_files,
    }


def audit_generated_molecules(
    generated_file: str | Path,
    training_file: str | Path,
    out_dir: str | Path,
    generated_smiles_column: str = "smiles",
    training_smiles_column: str = "smiles",
    remove_stereo: bool = False,
    make_figures: bool = True,
) -> dict:
    """Audit generated molecules against training/known-active molecules.

    This is the first paid-product-shaped workflow: validity, uniqueness,
    novelty, scaffold overlap, property drift, publication figures, methods,
    and a reproducibility manifest in one deterministic run.
    """
    return compare_ligand_libraries(
        query_file=generated_file,
        reference_file=training_file,
        out_dir=out_dir,
        query_smiles_column=generated_smiles_column,
        reference_smiles_column=training_smiles_column,
        remove_stereo=remove_stereo,
        make_figures=make_figures,
    )
