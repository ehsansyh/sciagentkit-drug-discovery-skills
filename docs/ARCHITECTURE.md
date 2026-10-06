# Architecture

SciAgentKit follows a skill-native architecture.

## Layer 1: deterministic scientific skills

These are pure Python functions that should work without an LLM:

- `profile_ligand_library`
- `compare_ligand_libraries`
- `audit_generated_molecules`
- canonicalization, descriptors, scaffold analysis, plotting, reports, manifests

## Layer 2: MCP tools

MCP exposes the deterministic skills to agent clients.

## Layer 3: adapters

Adapters teach different agent environments how to use the same skills:

- OpenClaw `SKILL.md`
- Claude/Cursor/Codex instructions
- OpenAI Agents SDK reference wrappers

## Layer 4: reference agents

The reference agents are product demos and onboarding tools. They are not the scientific source of truth. They plan workflows and call tools.

## Design rule

Any value that could appear in a manuscript table must come from a deterministic tool, not from a language model.
