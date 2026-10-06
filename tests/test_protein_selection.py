from sciagentkit.core.sequence import parse_mutations
from sciagentkit.skills.protein import StructureCandidate, rank_structures


def test_rank_structures_prefers_span_then_resolution():
    target = "M" + "A" * 100
    candidates = [
        StructureCandidate("1AAA", "A", "X-ray", 1.2, 10, 80, pdb_sequence="A" * 71),
        StructureCandidate("2BBB", "A", "X-ray", 2.0, 1, 100, pdb_sequence="M" + "A" * 99),
        StructureCandidate("3CCC", "A", "X-ray", 1.0, 1, 60, pdb_sequence="M" + "A" * 59),
    ]
    ranked = rank_structures(target, candidates, min_identity=0.5)
    assert ranked[0].pdb_id == "2BBB"
    assert ranked[0].selected is True


def test_rank_structures_mutation_match():
    target = "AAVAA"
    muts = parse_mutations(["V3E"])
    candidates = [
        StructureCandidate("WT", "A", "X-ray", 1.0, 1, 5, pdb_sequence="AAVAA"),
        StructureCandidate("MUT", "A", "X-ray", 2.0, 1, 5, pdb_sequence="AAEAA"),
    ]
    ranked = rank_structures(target, candidates, mutations=muts, min_identity=0.5)
    assert ranked[0].pdb_id == "MUT"
    assert ranked[0].mutation_match is True
