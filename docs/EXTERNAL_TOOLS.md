# External Tools

SciAgentKit v1.0 is local-first and open-source, but some workflow stages require external scientific software.

## Optional binaries

| Stage | Tool | Why |
|---|---|---|
| pH-aware ligand preparation | Open Babel (`obabel`) | Protonation and 3D ligand generation |
| Pocket detection | `fpocket` | Pocket detection from receptor geometry |
| Docking | AutoDock Vina (`vina`) | Free-source molecular docking |
| Receptor/ligand PDBQT prep | Open Babel / Meeko | Format conversion and docking input preparation |

## Optional Python packages

| Stage | Package |
|---|---|
| Literature/online APIs | `requests` |
| OpenMM MD | `openmm`, `pdbfixer` |
| ligand parameterization | `openff-toolkit`, `openmmforcefields` |
| trajectory analysis | `mdanalysis` |
| protein-ligand interactions | `prolif` |
| DOCX reports | `python-docx` |
| PDF reports | `reportlab` |

## One-command install

From a SciAgentKit checkout, use:

```bash
bash scripts/install.sh --all
```

This installs the full Python extras (`mcp`, `protein`, `docking`, `md`, `reports`), including `prolif`, `python-docx`, and `reportlab` through pip, and installs/attempts scientific conda-forge packages such as Open Babel, AutoDock Vina, fpocket, PDBFixer, OpenFF Toolkit, and OpenMMForceFields when conda/mamba is available. External CLI tools are attempted one by one with a bounded conda solve; any tool that cannot be installed automatically is reported with its manual installation link.

## Manual installation links

If external binaries cannot be installed automatically, install them from their upstream or package-manager sources:

- Open Babel: https://openbabel.org/docs/Installation/install.html
- AutoDock Vina: https://vina.scripps.edu/downloads/
- fpocket: https://github.com/Discngine/fpocket
- conda-forge Open Babel: https://anaconda.org/conda-forge/openbabel
- conda-forge AutoDock Vina: https://anaconda.org/conda-forge/vina
- conda-forge fpocket: https://anaconda.org/conda-forge/fpocket

Direct conda install for fpocket:

```bash
conda install conda-forge::fpocket
```

## AutoDock Vina from source

If conda-forge cannot install `vina` on the target machine, build the official Scripps AutoDock Vina repository manually. The upstream repository is `ccsb-scripps/AutoDock-Vina` and its project documentation is linked from the repository README.

```bash
git clone https://github.com/ccsb-scripps/AutoDock-Vina
cd AutoDock-Vina/build/python
python -m pip install .
```

For older environments where the package metadata does not support direct pip installation, this legacy command may also work:

```bash
python setup.py build install
```

After installation, verify that SciAgentKit can see the binary or Python package:

```bash
sciagent doctor
python -c "import vina; print(vina.__version__)"
```

Python package fallback:

```bash
pip install 'sciagentkit[mcp,protein,docking,md,reports]'
pip install prolif python-docx reportlab
```

Some dependencies are intentionally optional to keep the base install lightweight and easier to reproduce.


## Ligand-protein MD dependencies

For ligand-protein OpenMM MD, install the OpenFF/OpenMMForceFields path with mamba when possible:

```bash
mamba install -c conda-forge openff-toolkit openmmforcefields pdbfixer prolif
```

`openmmforcefields` is a real OpenMM ecosystem package that provides additional AMBER/CHARMM force fields and small-molecule template generators for OpenMM. `pdbfixer` is used for receptor repair before docking/MD.
