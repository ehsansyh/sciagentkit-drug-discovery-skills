from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class Mutation:
    wild_type: str
    position: int
    mutant: str


def parse_mutation(token: str) -> Mutation:
    clean = token.strip().replace("p.", "")
    match = re.fullmatch(r"([A-Z])([0-9]+)([A-Z])", clean)
    if not match:
        raise ValueError(f"Unsupported mutation format: {token}. Use one-letter format, e.g. V600E.")
    return Mutation(match.group(1), int(match.group(2)), match.group(3))


def parse_mutations(tokens: list[str] | tuple[str, ...] | None) -> list[Mutation]:
    if not tokens:
        return []
    return [parse_mutation(token) for token in tokens if str(token).strip()]


def apply_mutations(sequence: str, mutations: list[Mutation], *, strict_wild_type: bool = True) -> str:
    seq = list(sequence.strip().upper())
    for mutation in mutations:
        idx = mutation.position - 1
        if idx < 0 or idx >= len(seq):
            raise ValueError(f"Mutation {mutation} is outside sequence length {len(seq)}")
        observed = seq[idx]
        if strict_wild_type and observed != mutation.wild_type:
            raise ValueError(
                f"Mutation {mutation.wild_type}{mutation.position}{mutation.mutant} expects {mutation.wild_type} at {mutation.position}, observed {observed}"
            )
        seq[idx] = mutation.mutant
    return "".join(seq)


@dataclass
class AlignmentResult:
    query_aligned: str
    subject_aligned: str
    score: int
    identity: float
    query_coverage: float
    subject_coverage: float
    query_to_subject: dict[int, int | None]
    subject_to_query: dict[int, int | None]
    aligned_query_range: tuple[int | None, int | None]
    aligned_subject_range: tuple[int | None, int | None]


def needleman_wunsch(query: str, subject: str, match_score: int = 2, mismatch_score: int = -1, gap_score: int = -2) -> AlignmentResult:
    q = query.strip().upper()
    s = subject.strip().upper()
    n, m = len(q), len(s)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    pointer = [[""] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        dp[i][0] = i * gap_score
        pointer[i][0] = "U"
    for j in range(1, m + 1):
        dp[0][j] = j * gap_score
        pointer[0][j] = "L"
    for i in range(1, n + 1):
        qi = q[i - 1]
        for j in range(1, m + 1):
            diag = dp[i - 1][j - 1] + (match_score if qi == s[j - 1] else mismatch_score)
            up = dp[i - 1][j] + gap_score
            left = dp[i][j - 1] + gap_score
            best = max(diag, up, left)
            dp[i][j] = best
            pointer[i][j] = "D" if best == diag else ("U" if best == up else "L")
    i, j = n, m
    qa, sa = [], []
    while i > 0 or j > 0:
        move = pointer[i][j]
        if move == "D":
            qa.append(q[i - 1]); sa.append(s[j - 1]); i -= 1; j -= 1
        elif move == "U":
            qa.append(q[i - 1]); sa.append("-"); i -= 1
        else:
            qa.append("-"); sa.append(s[j - 1]); j -= 1
    qa = qa[::-1]
    sa = sa[::-1]
    query_to_subject: dict[int, int | None] = {}
    subject_to_query: dict[int, int | None] = {}
    qi = sj = matches = 0
    aligned_q, aligned_s = [], []
    for a, b in zip(qa, sa):
        qpos = spos = None
        if a != "-":
            qi += 1; qpos = qi
        if b != "-":
            sj += 1; spos = sj
        if qpos is not None:
            query_to_subject[qpos] = spos
        if spos is not None:
            subject_to_query[spos] = qpos
        if qpos is not None and spos is not None:
            aligned_q.append(qpos); aligned_s.append(spos)
            if a == b:
                matches += 1
    aligned_pairs = max(1, len(aligned_q))
    q_range = (min(aligned_q), max(aligned_q)) if aligned_q else (None, None)
    s_range = (min(aligned_s), max(aligned_s)) if aligned_s else (None, None)
    return AlignmentResult(
        "".join(qa), "".join(sa), dp[n][m], matches / aligned_pairs,
        len(set(aligned_q)) / n if n else 0.0,
        len(set(aligned_s)) / m if m else 0.0,
        query_to_subject, subject_to_query, q_range, s_range,
    )


def write_fasta(path: str | Path, records: list[tuple[str, str]]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        for name, seq in records:
            handle.write(f">{name}\n")
            for i in range(0, len(seq), 80):
                handle.write(seq[i:i+80] + "\n")
    return path
