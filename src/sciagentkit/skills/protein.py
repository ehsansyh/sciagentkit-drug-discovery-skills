from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re
from typing import Any

import pandas as pd

from sciagentkit.core.http import SciAgentHttpError, request_json, request_text
from sciagentkit.core.manifest import write_manifest
from sciagentkit.core.sequence import Mutation, apply_mutations, needleman_wunsch, parse_mutations, write_fasta

UNIPROT_SEARCH_URL = "https://rest.uniprot.org/uniprotkb/search"
UNIPROT_ENTRY_URL = "https://rest.uniprot.org/uniprotkb/{accession}.json"
RCSB_GRAPHQL_URL = "https://data.rcsb.org/graphql"


@dataclass
class UniProtTarget:
    accession: str
    entry_name: str | None
    protein_name: str | None
    gene_name: str | None
    organism: str | None
    sequence: str


@dataclass
class StructureCandidate:
    pdb_id: str
    chain_id: str | None
    method: str | None
    resolution: float | None
    residue_start: int | None
    residue_end: int | None
    pdb_sequence: str | None = None
    description: str | None = None


@dataclass
class RankedStructure:
    pdb_id: str
    chain_id: str | None
    method: str | None
    resolution: float | None
    residue_start: int | None
    residue_end: int | None
    residue_span: int
    identity: float
    target_coverage: float
    pdb_coverage: float
    mutation_match: bool
    selected: bool = False


def _first_gene_name(entry: dict[str, Any]) -> str | None:
    genes = entry.get("genes") or []
    if not genes:
        return None
    return ((genes[0].get("geneName") or {}).get("value"))


def _protein_name(entry: dict[str, Any]) -> str | None:
    return (((entry.get("proteinDescription") or {}).get("recommendedName") or {}).get("fullName") or {}).get("value")


def _entry_to_target(entry: dict[str, Any]) -> UniProtTarget:
    return UniProtTarget(
        accession=entry.get("primaryAccession"), entry_name=entry.get("uniProtkbId"),
        protein_name=_protein_name(entry), gene_name=_first_gene_name(entry),
        organism=(entry.get("organism") or {}).get("scientificName"), sequence=(entry.get("sequence") or {}).get("value", ""),
    )


def resolve_uniprot_target(target: str, organism_id: int = 9606, reviewed: bool = True) -> UniProtTarget:
    target = target.strip()
    if re.fullmatch(r"[A-NR-Z][0-9][A-Z0-9]{3}[0-9](-[0-9]+)?|[A-Z0-9]{6,10}", target):
        try:
            entry = request_json(UNIPROT_ENTRY_URL.format(accession=target))
            if entry and entry.get("sequence"):
                return _entry_to_target(entry)
        except Exception:
            pass
    query = f"(gene_exact:{target} OR protein_name:{target}) AND organism_id:{organism_id}"
    if reviewed:
        query += " AND reviewed:true"
    data = request_json(UNIPROT_SEARCH_URL, params={"query": query, "format": "json", "size": 5})
    results = data.get("results") or []
    if not results:
        raise ValueError(f"No UniProt entry found for target={target!r}, organism_id={organism_id}")
    return _entry_to_target(results[0])


def _parse_resolution(value: str | None) -> float | None:
    if not value:
        return None
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", value)
    return float(match.group(1)) if match else None


def _parse_chains(value: str | None) -> list[tuple[str | None, int | None, int | None]]:
    if not value:
        return [(None, None, None)]
    rows = []
    for piece in re.split(r",\s*", value):
        match = re.search(r"([A-Za-z0-9/]+)?=?\s*([0-9]+)\s*-\s*([0-9]+)", piece)
        if match:
            chains = (match.group(1) or "").split("/") if match.group(1) else [None]
            rows += [(chain or None, int(match.group(2)), int(match.group(3))) for chain in chains]
        else:
            rows.append((piece.strip() or None, None, None))
    return rows or [(None, None, None)]


def list_pdb_crossrefs(uniprot_accession: str) -> list[StructureCandidate]:
    entry = request_json(UNIPROT_ENTRY_URL.format(accession=uniprot_accession))
    candidates = []
    for xref in entry.get("uniProtKBCrossReferences") or []:
        if xref.get("database") != "PDB":
            continue
        props = {p.get("key"): p.get("value") for p in xref.get("properties") or []}
        for chain, start, end in _parse_chains(props.get("Chains")):
            candidates.append(StructureCandidate(xref.get("id"), chain, props.get("Method"), _parse_resolution(props.get("Resolution")), start, end))
    return candidates


def fetch_pdb_entity_sequences(pdb_ids: list[str]) -> dict[tuple[str, str], str]:
    if not pdb_ids:
        return {}
    query = """
    query EntrySequences($entry_ids: [String!]!) {
      entries(entry_ids: $entry_ids) {
        rcsb_id
        polymer_entities {
          rcsb_polymer_entity_container_identifiers { auth_asym_ids asym_ids }
          entity_poly { pdbx_seq_one_letter_code_can }
        }
      }
    }
    """
    data = request_json(RCSB_GRAPHQL_URL, method="POST", json_body={"query": query, "variables": {"entry_ids": [p.upper() for p in pdb_ids]}})
    seqs = {}
    for entry in (data.get("data") or {}).get("entries") or []:
        pdb_id = entry.get("rcsb_id")
        for entity in entry.get("polymer_entities") or []:
            seq = ((entity.get("entity_poly") or {}).get("pdbx_seq_one_letter_code_can") or "").replace("\n", "")
            ids = entity.get("rcsb_polymer_entity_container_identifiers") or {}
            for chain in (ids.get("auth_asym_ids") or ids.get("asym_ids") or []):
                seqs[(pdb_id, chain)] = seq
    return seqs


def rank_structures(target_sequence: str, candidates: list[StructureCandidate], mutations: list[Mutation] | None = None, min_identity: float = 0.85) -> list[RankedStructure]:
    mutations = mutations or []
    target_for_alignment = apply_mutations(target_sequence, mutations, strict_wild_type=False) if mutations else target_sequence
    ranked = []
    for cand in candidates:
        subject = cand.pdb_sequence
        if subject:
            aln = needleman_wunsch(target_for_alignment, subject)
            start, end = aln.aligned_query_range
            identity, target_cov, pdb_cov = aln.identity, aln.query_coverage, aln.subject_coverage
            mutation_match = True
            for mut in mutations:
                mapped = aln.query_to_subject.get(mut.position)
                mutation_match = mutation_match and mapped is not None and mapped <= len(subject) and subject[mapped - 1] == mut.mutant
            residue_start = cand.residue_start if cand.residue_start is not None else start
            residue_end = cand.residue_end if cand.residue_end is not None else end
        else:
            # No PDB sequence was retrieved, so identity is unverified. Do not invent a
            # perfect 1.0 that would outrank sequence-verified candidates; leave it at 0.0.
            identity = 0.0
            target_cov = ((cand.residue_end or 0) - (cand.residue_start or 0) + 1) / max(1, len(target_sequence)) if cand.residue_start and cand.residue_end else 0.0
            pdb_cov = 0.0
            mutation_match = not mutations
            residue_start, residue_end = cand.residue_start, cand.residue_end
        span = residue_end - residue_start + 1 if residue_start and residue_end and residue_end >= residue_start else 0
        if identity >= min_identity or not subject:
            ranked.append(RankedStructure(cand.pdb_id, cand.chain_id, cand.method, cand.resolution, residue_start, residue_end, span, identity, target_cov, pdb_cov, mutation_match))
    # Correctness/mutation match first, then widest residue span, then best resolution.
    ranked.sort(key=lambda r: (r.mutation_match, r.residue_span, -(r.resolution or 999.0), r.identity), reverse=True)
    if ranked:
        ranked[0].selected = True
    return ranked


def select_target_structure(target: str, out_dir: str | Path, organism_id: int = 9606, mutations: list[str] | None = None, min_identity: float = 0.85) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    parsed = parse_mutations(mutations)
    target_entry = resolve_uniprot_target(target, organism_id=organism_id)
    mutated_sequence = apply_mutations(target_entry.sequence, parsed, strict_wild_type=False) if parsed else target_entry.sequence
    candidates = list_pdb_crossrefs(target_entry.accession)
    try:
        seq_map = fetch_pdb_entity_sequences(sorted({c.pdb_id for c in candidates if c.pdb_id}))
    except Exception:
        seq_map = {}
    for cand in candidates:
        if cand.chain_id:
            cand.pdb_sequence = seq_map.get((cand.pdb_id.upper(), cand.chain_id))
    ranked = rank_structures(target_entry.sequence, candidates, parsed, min_identity=min_identity)
    pd.DataFrame([asdict(target_entry)]).to_csv(out / "uniprot_target.csv", index=False)
    write_fasta(out / "target_sequence.fasta", [(target_entry.accession, target_entry.sequence), (f"{target_entry.accession}_mutated", mutated_sequence)])
    pd.DataFrame([asdict(c) for c in candidates]).to_csv(out / "pdb_candidates.csv", index=False)
    pd.DataFrame([asdict(r) for r in ranked]).to_csv(out / "ranked_structures.csv", index=False)
    selected = asdict(ranked[0]) if ranked else None
    write_manifest(out, [], command=f"sciagent protein-select {target} --out {out}", parameters={"target": target, "organism_id": organism_id, "mutations": mutations or [], "min_identity": min_identity}, workflow_name="protein_structure_selection")
    return {"output_dir": str(out), "summary": {"target": target, "uniprot": target_entry.accession, "pdb_candidates": len(candidates), "ranked_structures": len(ranked), "selected_pdb": selected.get("pdb_id") if selected else None, "selected_chain": selected.get("chain_id") if selected else None}, "selected": selected, "generated_files": ["uniprot_target.csv", "target_sequence.fasta", "pdb_candidates.csv", "ranked_structures.csv", "run_manifest.json"]}


def fetch_pdb_structure(pdb_id: str, out_dir: str | Path, file_format: str = "pdb") -> dict:
    """Download a PDB coordinate file from RCSB.

    ``protein_select`` ranks structures but does not download coordinates; this
    fetches the actual atoms so the downstream receptor/pocket/docking steps can
    run. Tries the requested format (``pdb`` by default) and falls back to mmCIF
    for large structures that RCSB no longer serves as legacy PDB.
    """
    pdb_id = pdb_id.strip().upper()
    if not re.fullmatch(r"[0-9A-Z]{4}", pdb_id):
        raise ValueError(f"Invalid PDB id {pdb_id!r}; expected a 4-character code like '1M17'.")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ext = "cif" if file_format.lower() in ("cif", "mmcif") else "pdb"
    used_ext = ext
    try:
        text = request_text(f"https://files.rcsb.org/download/{pdb_id}.{ext}")
    except SciAgentHttpError:
        if ext == "pdb":  # legacy PDB not available (too large) -> mmCIF
            used_ext = "cif"
            text = request_text(f"https://files.rcsb.org/download/{pdb_id}.cif")
        else:
            raise
    path = out / f"{pdb_id}.{used_ext}"
    path.write_text(text, encoding="utf-8")
    n_atoms = sum(1 for ln in text.splitlines() if ln.startswith(("ATOM", "HETATM")))
    write_manifest(out, [], command=f"sciagent fetch-pdb {pdb_id} --out {out}", parameters={"pdb_id": pdb_id, "file_format": used_ext}, workflow_name="fetch_pdb_structure")
    return {"output_dir": str(out), "pdb_id": pdb_id, "path": str(path), "format": used_ext,
            "summary": {"pdb_id": pdb_id, "downloaded_file": path.name, "format": used_ext, "atom_records": n_atoms},
            "generated_files": [path.name, "run_manifest.json"]}
