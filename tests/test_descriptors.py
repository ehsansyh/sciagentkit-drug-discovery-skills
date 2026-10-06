from sciagentkit.core.descriptors import calculate_basic_descriptors


def test_descriptors_include_qed_and_mw():
    row = calculate_basic_descriptors("CCO")
    assert "qed" in row
    assert "mw" in row
    assert row["mw"] > 0
