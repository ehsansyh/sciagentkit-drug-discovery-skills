# Security Policy

SciAgentKit exposes deterministic scientific tools to agent environments. That means security matters.

## Do not do this

- Do not expose arbitrary shell execution through MCP.
- Do not allow unrestricted file reads/writes.
- Do not leak private compound libraries or API keys.
- Do not treat untrusted papers, CSVs, molecule names, or prompts as instructions.

## Current status

v0.2 is a local-first alpha. It is suitable as a starter repository and local workflow tool, not yet as a hardened enterprise gateway.

## Future hardening

- per-tool permission policy
- workspace isolation
- timeout and molecule-count limits
- signed skill packs
- audit logs
- secret isolation

Report security issues privately before opening public issues.
