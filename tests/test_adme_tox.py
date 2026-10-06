from sciagentkit.core.adme_tox import adme_tox_summary, adme_tox_table, calculate_adme_tox


def test_calculate_adme_tox_fields():
    d = calculate_adme_tox("CC(=O)Oc1ccccc1C(=O)O")  # aspirin
    for key in ("esol_logS", "gi_absorption", "bbb_permeant", "druglike_rules_passed",
                "pains_alerts", "brenk_alerts", "structural_alerts", "toxicity_flag"):
        assert key in d
    assert isinstance(d["bbb_permeant"], bool)
    assert d["gi_absorption"] in ("High", "Low")


def test_nicotine_is_bbb_permeant():
    d = calculate_adme_tox("CN1CCC[C@H]1c1cccnc1")  # nicotine crosses the BBB
    assert d["bbb_permeant"] is True


def test_table_skips_invalid_and_summarizes():
    df = adme_tox_table(["CCO", "c1ccccc1CCN", "not_a_smiles"])
    assert len(df) == 2  # invalid dropped
    s = adme_tox_summary(df)
    assert s["molecules"] == 2
    assert "with_structural_alerts" in s and "bbb_permeant" in s


def test_invalid_smiles_raises():
    import pytest
    with pytest.raises(ValueError):
        calculate_adme_tox("xyz123")
