<p align="center">
  <img src="https://sciagentkit.com/assets/Sciagentkit_logo.png" alt="SciAgentKit" width="220">
</p>

<p align="center">
  <b>Deterministic scientific tools for AI agents — real computational biology &amp; drug discovery, no invented numbers.</b>
</p>

<p align="center">
  <a href="https://sciagentkit.com">Website</a> ·
  <a href="https://sciagentkit.com/#pricing">Pricing</a> ·
  <a href="https://pypi.org/project/sciagentkit/">PyPI</a> ·
  <a href="mailto:support@sciagentkit.com">Support</a>
</p>

SciAgentKit gives **Claude, Cursor, Gemini CLI and Codex** deterministic tools for drug
discovery — molecule &amp; ADME/tox analysis, target/PDB selection, docking, molecular
dynamics, target-aware hit ranking, wet-lab plans, and signed reports — instead of letting
the model invent descriptors, docking scores, or RMSD values.

> Skills decide the workflow. Deterministic tools run the science. Reports preserve the evidence.

---

## Install

**Open-source core** — free, no account (molecule/ADME/tox/scaffolds, target selection,
ligand and receptor preparation, pocket definition):

```bash
pip install "sciagentkit[mcp]"
```

Or install the latest from GitHub:

```bash
pip install "sciagentkit[mcp] @ git+https://github.com/ehsansyh/sciagentkit-drug-discovery-skills"
```

**Full pipeline** — one conda environment with every open-source engine (RDKit, OpenMM,
AutoDock Vina, Open Babel, fpocket, …), the core, and SciAgentKit Enterprise for docking,
MD, hit ranking, wet-lab plans and reports:

```bash
curl -O https://sciagentkit.com/environment.yml
conda env create -f environment.yml
conda activate sciagentkit
```

Enterprise features need an API key from **https://sciagentkit.com** (free 3-day trial):

```bash
export SCIAGENTKIT_API_KEY=sak_your_key      # Windows: setx SCIAGENTKIT_API_KEY "sak_..."
```

The core never needs a key. When `sciagentkit-enterprise` is installed, its tools appear in
the same MCP server and `sciagent` CLI automatically.

---

## Use it in your AI agent

**Claude Code plugin** (skills + MCP server). After installing the package, inside Claude Code:
```text
/plugin marketplace add ehsansyh/sciagentkit-drug-discovery-skills
/plugin install sciagentkit@sciagentkit
```
Skills then appear as `/sciagentkit:smiles-analysis`, `/sciagentkit:generated-molecule-audit`, …
If `python` on your PATH is not the environment where you installed SciAgentKit, set
`SCIAGENTKIT_PYTHON` to that interpreter's path.

**Claude Code, MCP server only**
```bash
claude mcp add sciagentkit -s user -- python -m sciagentkit.servers.rdkit_server
```
For Enterprise features add `--env SCIAGENTKIT_API_KEY=sak_your_key`.

**Cursor / Gemini CLI / Codex**
```bash
sciagent init-agent cursor       # or: gemini | codex | all
```

Then ask your agent naturally:

> *"Dock these ligands against EGFR L858R, rank target-aware top hits, and write a report."*

Full step-by-step guide (all four agents): see **[USER_GUIDE.md](USER_GUIDE.md)** or
[sciagentkit.com](https://sciagentkit.com/#install).

---

## What it does

- **Molecule libraries** — canonicalization, descriptors (MW, logP, QED, TPSA), scaffold diversity, novelty audits (RDKit)
- **ADME &amp; toxicity** — ESOL solubility, drug-likeness (Lipinski/Veber/Ghose/Egan), GI/BBB heuristics, PAINS/Brenk alerts
- **Targets** — UniProt resolution + mutation-aware PDB ranking
- **Docking** — pocket detection (crystal-ligand / fpocket / P2Rank) + Vina/GNINA/smina, ranked poses
- **Molecular dynamics** — OpenMM setup + trajectory RMSD/RMSF + ProLIF interactions
- **Target-aware hit ranking** — combines docking, MD stability, and ADME/tox (toxicity penalized; BBB up-weighted for CNS targets)
- **Wet-lab validation plans** — staged assays + recommended cell lines for the target
- **Signed, reproducible reports** — Markdown / PDF / DOCX with a `run_manifest.json` (input hashes + tool versions)

Every value is computed by real tools, never inferred by a language model. Outputs are saved
under `runs/` with a reproducibility manifest.

---

## Free vs paid

| | Open source (this repo) | Enterprise trial (3 days) | Enterprise Individual / Team |
|---|---|---|---|
| Molecule analysis, ADME/tox, target selection | ✅ | ✅ | ✅ |
| Ligand/receptor preparation, pocket definition | ✅ | ✅ | ✅ |
| Docking | ❌ | 1 run | ✅ unlimited |
| Molecular dynamics | ❌ | ❌ | ✅ |
| Hit ranking, wet-lab plans, reports | ❌ | ✅ | ✅ |
| Expert review of results | — | — | add-on |

The open-source core is Apache-2.0. Enterprise is a separate, licensed package; manage your
plan at [sciagentkit.com](https://sciagentkit.com).

---

## Scientific limits

SciAgentKit is a workflow and tooling layer, not expert review. Docking scores are ranking
heuristics, not binding free energies; short MD validates setup and analysis plumbing, not
equilibrium stability. Receptor protonation, missing loops, cofactors, metals, membrane
context, and ligand parameterization still require expert review.

---

## Support

Account, docs, and billing: **https://sciagentkit.com** — questions: **support@sciagentkit.com**

© 2026 Istanbulmedchem. The open-source core is licensed under the [Apache License 2.0](LICENSE).
SciAgentKit Enterprise is proprietary and licensed separately.
