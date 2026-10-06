from sciagentkit.core.smiles import canonicalize_smiles, clean_canonical_library


def test_canonicalize_valid_smiles():
    record = canonicalize_smiles("CCO")
    assert record.is_valid is True
    assert record.canonical_smiles == "CCO"


def test_canonicalize_invalid_smiles():
    record = canonicalize_smiles("not_a_smiles")
    assert record.is_valid is False
    assert record.canonical_smiles is None


def test_clean_canonical_library_removes_duplicates():
    _, clean = clean_canonical_library(["CCO", "OCC", "CCN"])
    assert len(clean) == 2
