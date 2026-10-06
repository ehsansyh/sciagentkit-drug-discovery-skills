from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from sciagentkit.agents import molecule_analyst_plan
from sciagentkit.skills import (
    audit_generated_molecules,
    compare_ligand_libraries,
    detect_pocket,
    fetch_pdb_structure,
    ligand_md_readiness,
    literature_search,
    prepare_ligands_3d,
    prepare_receptor_for_docking,
    prepare_receptor_for_md,
    profile_ligand_library,
    select_target_structure,
)

app = typer.Typer(help="SciAgentKit: reproducible scientific skills for AI agents.")
console = Console()


def _module_available(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except ModuleNotFoundError:
        return False


def _print_summary(title: str, summary: dict, output_dir: str) -> None:
    table = Table(title=title)
    table.add_column("Metric", style="bold")
    table.add_column("Value")
    for key, value in summary.items():
        if isinstance(value, (list, dict)):
            continue
        table.add_row(str(key).replace("_", " "), f"{value:.4f}" if isinstance(value, float) else str(value))
    console.print(table)
    console.print(f"[green]Saved outputs to:[/green] {output_dir}")


@app.command("analyze-smiles")
def analyze_smiles(input_file: Path, smiles_column: str = "smiles", out: Path = Path("runs/smiles_analysis"), remove_stereo: bool = False, no_figures: bool = False):
    """Clean, deduplicate, profile, plot, and report a molecule library."""
    result = profile_ligand_library(input_file, out, smiles_column, remove_stereo, not no_figures)
    _print_summary("SciAgentKit Molecule Library Analysis", result["summary"], result["output_dir"])


@app.command("compare-libraries")
def compare_libraries(query_file: Path, reference_file: Path, out: Path = Path("runs/library_comparison"), query_smiles_column: str = "smiles", reference_smiles_column: str = "smiles", remove_stereo: bool = False, no_figures: bool = False):
    """Compare query molecules against a reference library and estimate novelty."""
    result = compare_ligand_libraries(query_file, reference_file, out, query_smiles_column, reference_smiles_column, remove_stereo, not no_figures)
    _print_summary("SciAgentKit Molecule Library Comparison", result["summary"], result["output_dir"])


@app.command("audit-generated")
def audit_generated(generated_file: Path, training_file: Path, out: Path = Path("runs/generated_audit"), generated_smiles_column: str = "smiles", training_smiles_column: str = "smiles", remove_stereo: bool = False, no_figures: bool = False):
    """Audit AI-generated molecules against training/reference molecules."""
    result = audit_generated_molecules(generated_file, training_file, out, generated_smiles_column, training_smiles_column, remove_stereo, not no_figures)
    _print_summary("SciAgentKit Generated Molecule Audit", result["summary"], result["output_dir"])


@app.command("literature-search")
def literature_search_cmd(query: str, out: Path = Path("runs/literature"), max_results: int = 20, source: str = "europepmc"):
    """Search Europe PMC/PubMed and save evidence table."""
    result = literature_search(query, out, max_results=max_results, source=source)
    _print_summary("SciAgentKit Literature MCP", result["summary"], result["output_dir"])


@app.command("protein-select")
def protein_select(target: str, out: Path = Path("runs/protein_selection"), organism_id: int = 9606, mutation: list[str] = typer.Option(None, "--mutation", "-m", help="Mutation such as V600E; repeat for multiple mutations"), min_identity: float = 0.85):
    """Fetch UniProt sequence, list PDB structures, align sequences, and rank best structure."""
    result = select_target_structure(target, out, organism_id=organism_id, mutations=mutation, min_identity=min_identity)
    _print_summary("SciAgentKit Protein Structure Selection", result["summary"], result["output_dir"])


@app.command("fetch-pdb")
def fetch_pdb_cmd(pdb_id: str, out: Path = Path("runs/pdb"), file_format: str = "pdb"):
    """Download a PDB coordinate file from RCSB (protein-select ranks but does not download)."""
    result = fetch_pdb_structure(pdb_id, out, file_format=file_format)
    _print_summary("SciAgentKit Fetch PDB", result["summary"], result["output_dir"])


@app.command("prepare-ligands")
def prepare_ligands(smiles_file: Path, out: Path = Path("runs/ligand_prep"), smiles_column: str = "smiles", ph: float = 7.4, forcefield_mode: str = typer.Option("recommend", help="recommend, user, or prompt"), conformer_forcefield: str | None = None, target_family: str | None = None):
    """Generate 3D ligand SDF using Open Babel when available or RDKit fallback."""
    if forcefield_mode == "prompt" and conformer_forcefield is None:
        use_rec = typer.confirm("Use SciAgentKit recommended conformer force field?", default=True)
        if not use_rec:
            conformer_forcefield = typer.prompt("Enter conformer force field", default="MMFF94")
    result = prepare_ligands_3d(smiles_file, out, smiles_column=smiles_column, ph=ph, forcefield_mode=forcefield_mode, conformer_forcefield=conformer_forcefield, target_family=target_family)
    _print_summary("SciAgentKit Ligand 3D Preparation", result["summary"], result["output_dir"])


@app.command("prepare-receptor-docking")
def prepare_receptor_docking_cmd(pdb_file: Path, out: Path = Path("runs/receptor_docking"), ligand_resname: str | None = None, keep_waters: bool = True, add_hydrogens: bool = True):
    """Prepare receptor for docking: remove pocket ligand, preserve waters by default, repair hydrogens/atoms when possible."""
    result = prepare_receptor_for_docking(pdb_file, out, ligand_resname=ligand_resname, keep_waters=keep_waters, add_hydrogens=add_hydrogens)
    _print_summary("SciAgentKit Docking Receptor Preparation", result["summary"], result["output_dir"])


@app.command("prepare-receptor-md")
def prepare_receptor_md_cmd(pdb_file: Path, out: Path = Path("runs/receptor_md"), add_hydrogens: bool = True):
    """Prepare protein-only receptor for MD: remove waters/heterogens, repair hydrogens/atoms when possible."""
    result = prepare_receptor_for_md(pdb_file, out, add_hydrogens=add_hydrogens)
    _print_summary("SciAgentKit MD Receptor Preparation", result["summary"], result["output_dir"])


@app.command("detect-pocket")
def detect_pocket_cmd(pdb_file: Path, out: Path = Path("runs/pocket"), mode: str = "crystal-ligand", ligand_resname: str | None = None, residue: list[str] = typer.Option(None, "--residue", "-r", help="Pocket residue like A:123; repeat"), grid_size: float = 22.0):
    """Detect/define docking pocket from crystal ligand, residue list, fpocket, P2Rank, or auto fallback."""
    result = detect_pocket(pdb_file, out, mode=mode, ligand_resname=ligand_resname, residues=residue, grid_size=grid_size)
    _print_summary("SciAgentKit Pocket Definition", result["summary"], result["output_dir"])


@app.command("ligand-md-readiness")
def ligand_md_readiness_cmd(ligand_file: Path, out: Path = Path("runs/ligand_md_readiness")):
    """Check whether ligand-protein MD parameterization dependencies and ligand input are ready."""
    result = ligand_md_readiness(ligand_file, out)
    _print_summary("SciAgentKit Ligand MD Readiness", result["summary"], result["output_dir"])


@app.command("demo")
def demo(out: Path = Path("runs/demo_hiv_generated_audit")):
    """Run the bundled HIV-protease-flavored molecule audit demo."""
    candidates = [Path.cwd(), Path(__file__).resolve().parents[2], Path(__file__).resolve().parents[3]]
    root = next((candidate for candidate in candidates if (candidate / "examples" / "hiv_demo").exists()), None)
    if root is None:
        raise typer.BadParameter("Could not locate bundled examples/hiv_demo directory.")
    query = root / "examples" / "hiv_demo" / "generated_molecules.smi"
    reference = root / "examples" / "hiv_demo" / "known_actives.smi"
    result = audit_generated_molecules(query, reference, out)
    _print_summary("SciAgentKit Demo", result["summary"], result["output_dir"])


@app.command("agent-plan")
def agent_plan(json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON")):
    """Print the reference Molecule Analyst agent plan."""
    plan = molecule_analyst_plan()
    if json_output:
        console.print(json.dumps(plan, indent=2))
        return
    table = Table(title="Reference Molecule Analyst Agent Plan")
    table.add_column("#"); table.add_column("Step"); table.add_column("Tool"); table.add_column("Purpose")
    for step in plan:
        table.add_row(str(step["index"]), step["name"], step["tool"], step["purpose"])
    console.print(table)


@app.command("doctor")
def doctor():
    """Check Python packages, optional external tools, and basic SciAgentKit readiness."""
    python_packages = [
        "rdkit",
        "pandas",
        "numpy",
        "matplotlib",
        "Bio",
        "mcp",
        "openmm",
        "pdbfixer",
        "MDAnalysis",
        "prolif",
        "openff.toolkit",
        "openmmforcefields",
        "docx",
        "reportlab",
    ]
    binaries = ["obabel", "vina", "gnina", "smina", "fpocket", "prank", "p2rank"]

    table = Table(title="SciAgentKit Doctor")
    table.add_column("Component", style="bold")
    table.add_column("Type")
    table.add_column("Status")

    hard_missing = []
    for package in python_packages:
        ok = _module_available(package)
        status = "available" if ok else "missing"
        if package in {"rdkit", "pandas", "numpy", "matplotlib"} and not ok:
            hard_missing.append(package)
        table.add_row(package, "python", status)

    for binary in binaries:
        path = shutil.which(binary)
        table.add_row(binary, "binary", path or "missing")

    console.print(table)
    if hard_missing:
        raise typer.Exit(code=1)
    console.print("[green]Core SciAgentKit dependencies are ready.[/green]")


@app.command("mcp-info")
def mcp_info():
    """Print MCP server startup instructions."""
    console.print("Start the SciAgentKit MCP server with:")
    console.print("[bold]python -m sciagentkit.servers.rdkit_server[/bold]")
    console.print("Install MCP support with: pip install 'sciagentkit[mcp]'", markup=False)


@app.command("init-agent")
def init_agent(
    tool: str = typer.Argument("all", help="claude, codex, gemini, cursor, or all"),
    root: Path = typer.Option(Path("."), help="Repository root (auto-detected if it contains src/sciagentkit)"),
):
    """Wire SciAgentKit into an AI coding agent: MCP config, instructions, and skills."""
    from sciagentkit.agent_config import SUPPORTED_TOOLS, init_agents, repo_root

    resolved = repo_root(root)
    tools = ["all"] if tool == "all" else [t.strip().lower() for t in tool.split(",") if t.strip()]
    try:
        written = init_agents(resolved, tools)
    except (ValueError, FileNotFoundError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    table = Table(title=f"SciAgentKit agent setup ({', '.join(written)})")
    table.add_column("Tool", style="bold")
    table.add_column("Files written")
    for name, paths in written.items():
        rels = []
        for p in paths:
            try:
                rels.append(str(p.relative_to(resolved)))
            except ValueError:
                rels.append(str(p))
        table.add_row(name, str(len(paths)) + ": " + ", ".join(sorted(set(rels))[:6]) + (" …" if len(rels) > 6 else ""))
    console.print(table)
    console.print(f"[green]Done.[/green] Restart the agent so it picks up the new config. Supported tools: {', '.join(SUPPORTED_TOOLS)}.")


@app.command("sync-skills")
def sync_skills_cmd(root: Path = typer.Option(Path("."), help="Repository root")):
    """Regenerate every skill copy from the canonical .claude/skills source."""
    from sciagentkit.agent_config import canonical_skills_dir, repo_root, sync_skills

    resolved = repo_root(root)
    targets = [resolved / "plugins" / "claude-code-sciagentkit" / "skills"]
    gemini = resolved / ".gemini" / "skills"
    if gemini.exists():
        targets.append(gemini)
    written = sync_skills(resolved, targets)
    console.print(f"Canonical source: [bold]{canonical_skills_dir(resolved)}[/bold]")
    console.print(f"[green]Synced[/green] {len(written)} skill directories to: {', '.join(str(t) for t in targets)}")


def _load_cli_plugins() -> None:
    """Let add-on packages register extra commands (``sciagentkit.cli_plugins`` group)."""
    from importlib.metadata import entry_points

    for ep in entry_points(group="sciagentkit.cli_plugins"):
        try:
            ep.load()(app)
        except Exception as exc:  # noqa: BLE001
            console.print(f"[yellow]SciAgentKit: plugin {ep.name!r} failed to load:[/yellow] {exc}")


_load_cli_plugins()


def main() -> None:
    """Console entry point."""
    app()


if __name__ == "__main__":
    main()
