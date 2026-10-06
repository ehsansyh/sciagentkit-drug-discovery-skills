from sciagentkit.core.sequence import apply_mutations, needleman_wunsch, parse_mutation


def test_parse_and_apply_mutation():
    mut = parse_mutation("V3E")
    assert mut.position == 3
    assert apply_mutations("AAVAA", [mut]) == "AAEAA"


def test_alignment_mapping_identity():
    aln = needleman_wunsch("MABCDE", "ABC")
    assert aln.identity >= 0.99
    assert aln.query_to_subject[2] == 1
