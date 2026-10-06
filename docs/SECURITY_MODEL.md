# Security Model

## Main risks

- arbitrary file writes
- arbitrary shell execution
- prompt injection through papers, CSV files, or molecule names
- leaking private compound libraries
- tool poisoning in shared agent environments
- unbounded compute cost

## Default rules

- no `eval`
- no arbitrary shell by default
- no reading secrets
- no output outside `runs/`
- no remote fetch without explicit connector/tool permission
- size limits for local workflows
- run manifests for auditability

## Enterprise direction

- secure MCP gateway
- role-based permissions
- per-tool approval
- audit logs
- isolated workspaces
- private deployment
