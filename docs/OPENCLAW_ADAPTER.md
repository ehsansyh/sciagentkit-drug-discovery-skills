# OpenClaw Adapter Strategy

SciAgentKit should publish OpenClaw-style skills as adapters, not as the core product.

## Why

OpenClaw can be a distribution channel, but SciAgentKit should remain usable from any MCP-compatible client, CLI, or Python environment.

## Layout

```text
skills/openclaw/<skill-name>/SKILL.md
```

Each skill should:

- tell the agent when to use the skill
- require deterministic SciAgentKit tool calls
- forbid invented molecular values
- declare expected outputs
- list scientific limitations

## Initial skills

- molecule-library-analysis
- scaffold-diversity
- publication-figure-generator
- qsar-leakage-check
- md-trajectory-analysis
- literature-to-target
- protein-structure-analysis
- methods-report-writer
