from sciagentkit.core.scaffolds import scaffold_summary


def test_scaffold_summary_runs():
    summary = scaffold_summary(["c1ccccc1", "Cc1ccccc1", "CCO"])
    assert summary["total_molecules"] == 3
    assert summary["unique_scaffolds"] >= 1
