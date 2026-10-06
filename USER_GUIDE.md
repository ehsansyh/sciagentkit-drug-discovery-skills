# SciAgentKit — User Guide

SciAgentKit gives your AI coding agent (Claude, Cursor, Gemini CLI, Codex) **deterministic
scientific tools** for drug discovery — molecule & ADME/tox analysis, target/PDB selection,
docking, molecular dynamics, target-aware hit ranking, wet-lab plans, and signed reports —
instead of letting the model invent numbers.

- **Free trial (3 days):** analysis tools + ADME/toxicity + **1 docking run** (no MD).
- **Individual / Team:** full docking + molecular dynamics + target-aware hit ranking + wet-lab plans + reports.
- **Expert review add-on:** a specialist evaluates your run's results.

---

## 1. Get your API key

1. Go to **https://sciagentkit.com** → **Start free trial** (enter your email).
2. Open **My account** → copy your **API key** (`sak_…`).
3. To unlock paid tools, click **Upgrade** and choose Individual or Team (with Expert review if you want).

Your API key activates the toolkit locally — the science runs on **your** machine; only a
license check is sent to our server.

---

## 2. Install the toolkit

Docking and molecular dynamics rely on open-source engines (AutoDock Vina, Open Babel,
OpenMM, fpocket, …) that are **not pip-installable** — they come from conda-forge. So there
are two install paths:

### A) Full pipeline — conda (recommended)

One command installs every scientific engine + the toolkit:

```bash
curl -O https://sciagentkit.com/environment.yml
conda env create -f environment.yml
conda activate sciagentkit
```

Or step by step:
```bash
conda create -n sciagentkit python=3.12 -y
conda activate sciagentkit
conda install -c conda-forge rdkit openbabel autodock-vina fpocket openmm pdbfixer mdanalysis prolif -y
pip install "sciagentkit[mcp]" sciagentkit-enterprise
```

`sciagentkit-enterprise` adds docking, MD, trajectory analysis, hit ranking, wet-lab plans
and reports to the same MCP server and CLI. It needs an API key (step 3).

### B) Analysis only — pip

For molecule analysis, ADME/tox, scaffolds, target selection, and literature (no docking/MD):
```bash
pip install "sciagentkit[mcp]"
```

Check what's available any time:
```bash
sciagent doctor
```
It lists which Python packages and external binaries (Vina, OpenMM, Open Babel, …) are
installed, so you know which tools are ready.

---

## 3. Set your API key

Only needed for SciAgentKit Enterprise features. The open-source core runs without a key.

**macOS / Linux:**
```bash
export SCIAGENTKIT_API_KEY=sak_your_key_here
```

**Windows (PowerShell):**
```powershell
setx SCIAGENTKIT_API_KEY "sak_your_key_here"
```
(Reopen the terminal after `setx`.)

Verify:
```bash
sciagent license-verify
```

---

## 4. Connect it to your AI agent

### Claude Code (recommended)

Register the MCP server (passes your key to the server process):
```bash
claude mcp add sciagentkit -s user \
  --env SCIAGENTKIT_API_KEY=sak_your_key_here \
  -- python -m sciagentkit.servers.rdkit_server
```
Restart Claude Code, then:
```
/mcp
```
You should see **sciagentkit — connected**, exposing tools like `analyze_library`,
`adme_tox`, `protein_select`, `run_docking`, `md_plan`, `select_top_hits`, `wet_lab_plan`,
`write_report`.

Add the guided **skills** (optional but recommended):
```bash
sciagent init-agent claude
```
Then in Claude you can invoke, e.g.:
```
/sciagentkit:smiles-analysis Analyze examples/egfr_demo/ligands.smi and save to runs/egfr.
/sciagentkit:full-target-screening Run an EGFR L858R screening for these ligands.
```
…or just ask in plain language — the MCP tools work with or without the skills.

### Cursor
```bash
sciagent init-agent cursor
```
This writes `.cursor/rules/sciagentkit.mdc` and the MCP config. Restart Cursor from the project.

### Gemini CLI
```bash
sciagent init-agent gemini
```
Writes `GEMINI.md`, `.gemini/settings.json`, and skills. In Gemini: `/mcp`, `/skills`.

### Codex
```bash
sciagent init-agent codex
```
Writes `AGENTS.md`, `.codex/` config, and skills. In Codex: `/mcp`, `/skills`, or `$smiles-analysis …`.

> `sciagent init-agent all` sets up every tool at once. Restart the agent so it reloads the config.

---

## 5. Use it — example prompts

Ask your agent naturally; it will call the deterministic tools:

- *"Profile this SMILES library — give me descriptors, scaffold diversity, and ADME/toxicity flags."*
- *"Select the best PDB structure for EGFR with the L858R mutation."*
- *"Prepare these ligands, dock them, then rank target-aware top hits for a CNS target."*
- *"Write a report with the top hits and a recommended wet-lab validation plan."*

Every run is saved under `runs/` with a `run_manifest.json` (input hashes + tool versions) so
results are reproducible and auditable.

---

## 6. What's free vs paid

| Feature | Trial | Individual / Team |
|---|---|---|
| Molecule analysis, ADME/tox, scaffolds, target selection, literature | ✅ | ✅ |
| Docking | **1 run** | ✅ unlimited |
| Molecular dynamics | ❌ | ✅ |
| Target-aware hit ranking, wet-lab plans, reports | ✅ | ✅ |
| Expert review of results | — | Add-on |

Team plans are **per seat** (max 5); each teammate installs the toolkit and uses their own seat.

---

## 7. Troubleshooting

- **`sciagent doctor`** — shows which Python packages and external binaries (Vina, OpenMM, …) are installed.
- **"License required" / activation errors** — check `SCIAGENTKIT_API_KEY` is set and your subscription is active; run `sciagent license-verify`. Activation needs occasional internet (a grace window allows short offline use).
- **A docking/MD tool says a binary is missing** — install it via conda (see step 2) or run the lighter analysis tools.
- **Seat limit reached** — you've activated the toolkit on more machines than your plan allows; free a seat or upgrade.

Need help? **support@sciagentkit.com**
