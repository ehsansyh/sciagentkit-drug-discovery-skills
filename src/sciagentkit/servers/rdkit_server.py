from __future__ import annotations

import sys
from importlib.metadata import entry_points

from sciagentkit import skills as _skills
from sciagentkit.core.descriptors import calculate_basic_descriptors
from sciagentkit.core.scaffolds import get_bemis_murcko_scaffold
from sciagentkit.core.smiles import canonicalize_smiles
from sciagentkit.core.paths import safe_run_output_dir

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install MCP support with: pip install 'sciagentkit[mcp]'") from exc


mcp = FastMCP("SciAgentKit Scientific Skills")


# Tool names are deliberately consistent: short verb/noun, no `_tool` suffix.
# Skill functions are reached through the module alias to avoid shadowing the
# tool functions that share their name (e.g. literature_search).


@mcp.tool()
def canonicalize(smiles: str, remove_stereo: bool = False) -> dict:
    """Canonicalize one SMILES string with RDKit."""
    return canonicalize_smiles(smiles, remove_stereo=remove_stereo).__dict__


@mcp.tool()
def descriptors(smiles: str) -> dict:
    """Calculate RDKit molecular descriptors for one SMILES string."""
    try:
        return calculate_basic_descriptors(smiles)
    except ValueError as exc:
        return {"smiles": smiles, "error": str(exc)}


@mcp.tool()
def bemis_murcko_scaffold(smiles: str) -> dict:
    """Extract a Bemis-Murcko scaffold from one molecule."""
    return {"smiles": smiles, "scaffold": get_bemis_murcko_scaffold(smiles)}


@mcp.tool()
def adme_tox(smiles: str) -> dict:
    """Compute deterministic ADME (ESOL solubility, drug-likeness, GI/BBB heuristics)
    and toxicity/liability alerts (PAINS/Brenk) for one SMILES string."""
    from sciagentkit.core.adme_tox import calculate_adme_tox
    try:
        return calculate_adme_tox(smiles)
    except ValueError as exc:
        return {"smiles": smiles, "error": str(exc)}


@mcp.tool()
def analyze_library(smiles_file: str, output_dir: str = "runs/mcp_library_profile") -> dict:
    """Clean, deduplicate, profile, plot, and report a molecule library."""
    return _skills.profile_ligand_library(smiles_file, safe_run_output_dir(output_dir))


@mcp.tool()
def compare_libraries(query_file: str, reference_file: str, output_dir: str = "runs/mcp_library_compare") -> dict:
    """Compare a query/generated library against a reference library."""
    return _skills.compare_ligand_libraries(query_file, reference_file, safe_run_output_dir(output_dir))


@mcp.tool()
def audit_generated_library(generated_file: str, training_file: str, output_dir: str = "runs/mcp_generated_audit") -> dict:
    """Audit generated molecules against training or known-active molecules."""
    return _skills.audit_generated_molecules(generated_file, training_file, safe_run_output_dir(output_dir))


@mcp.tool()
def literature_search(query: str, output_dir: str = "runs/mcp_literature", max_results: int = 20, source: str = "europepmc") -> dict:
    """Search biomedical literature through Europe PMC/PubMed and save an evidence table."""
    return _skills.literature_search(query, safe_run_output_dir(output_dir), max_results=max_results, source=source)


@mcp.tool()
def protein_select(target: str, output_dir: str = "runs/mcp_protein", organism_id: int = 9606, mutations: list[str] | None = None, min_identity: float = 0.85) -> dict:
    """Resolve UniProt target, list PDB structures, align sequences, and select best structure."""
    return _skills.select_target_structure(target, safe_run_output_dir(output_dir), organism_id=organism_id, mutations=mutations, min_identity=min_identity)


@mcp.tool()
def fetch_pdb(pdb_id: str, output_dir: str = "runs/mcp_fetch_pdb", file_format: str = "pdb") -> dict:
    """Download a PDB coordinate file from RCSB. protein_select ranks structures but does
    not download coordinates; run this to obtain the atoms before receptor/pocket/docking."""
    return _skills.fetch_pdb_structure(pdb_id, safe_run_output_dir(output_dir), file_format=file_format)


@mcp.tool()
def prepare_ligands(smiles_file: str, output_dir: str = "runs/mcp_ligands", ph: float = 7.4, target_family: str | None = None, conformer_forcefield: str | None = None) -> dict:
    """Prepare 3D SDF ligand conformers with RDKit/Open Babel fallback."""
    return _skills.prepare_ligands_3d(smiles_file, safe_run_output_dir(output_dir), ph=ph, target_family=target_family, conformer_forcefield=conformer_forcefield)


@mcp.tool()
def prepare_receptor_docking(pdb_file: str, output_dir: str = "runs/mcp_receptor_docking", ligand_resname: str | None = None, keep_waters: bool = True, add_hydrogens: bool = True) -> dict:
    """Prepare receptor for docking by removing the pocket ligand while preserving waters by default."""
    return _skills.prepare_receptor_for_docking(pdb_file, safe_run_output_dir(output_dir), ligand_resname=ligand_resname, keep_waters=keep_waters, add_hydrogens=add_hydrogens)


@mcp.tool()
def prepare_receptor_md(pdb_file: str, output_dir: str = "runs/mcp_receptor_md", add_hydrogens: bool = True) -> dict:
    """Prepare protein-only receptor for MD by removing waters and heterogens."""
    return _skills.prepare_receptor_for_md(pdb_file, safe_run_output_dir(output_dir), add_hydrogens=add_hydrogens)


@mcp.tool()
def detect_pocket(pdb_file: str, output_dir: str = "runs/mcp_pocket", mode: str = "crystal-ligand", ligand_resname: str | None = None, residues: list[str] | None = None, grid_size: float = 22.0) -> dict:
    """Define a docking pocket from crystal ligand, residue list, fpocket, P2Rank, or auto fallback."""
    return _skills.detect_pocket(pdb_file, safe_run_output_dir(output_dir), mode=mode, ligand_resname=ligand_resname, residues=residues, grid_size=grid_size)


@mcp.tool()
def ligand_md_readiness(ligand_file: str, output_dir: str = "runs/mcp_ligand_md_readiness") -> dict:
    """Check ligand-protein MD parameterization readiness and missing dependencies."""
    return _skills.ligand_md_readiness(ligand_file, safe_run_output_dir(output_dir))


def _load_plugins() -> list[str]:
    """Let add-on packages (such as SciAgentKit Enterprise) register extra tools.

    An add-on exposes a callable in the ``sciagentkit.mcp_plugins`` entry-point
    group; it receives this FastMCP instance. A broken add-on is reported on stderr
    and skipped, so the free tools keep working.
    """
    loaded = []
    for ep in entry_points(group="sciagentkit.mcp_plugins"):
        try:
            ep.load()(mcp)
            loaded.append(ep.name)
        except Exception as exc:  # noqa: BLE001
            print(f"SciAgentKit: plugin {ep.name!r} failed to load: {exc}", file=sys.stderr)
    return loaded


LOADED_PLUGINS = _load_plugins()


if __name__ == "__main__":
    mcp.run()
