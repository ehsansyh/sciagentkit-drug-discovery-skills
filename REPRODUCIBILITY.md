# Reproducibility

Every SciAgentKit workflow should produce:

- input file hashes
- output file hashes
- package versions
- command and parameters
- generated reports and figures

The canonical output is `run_manifest.json`.

## Rule

If a number is going into a manuscript, it must be traceable to a deterministic file output. Language models may summarize results, not create them from vibes. The vibes industry has enough funding already.
