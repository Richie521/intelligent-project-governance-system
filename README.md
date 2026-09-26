# Project Intelligent Governance System

[简体中文](README.zh-CN.md)

Project Intelligent Governance System is a reusable, documentation-authoritative method for making AI-assisted project folders easier to understand and safer to modify.

It helps an agent inspect a project from local evidence, identify source boundaries, preserve useful project-specific practices, avoid copying private or stale context, and write durable knowledge back to the right place.

## Why It Exists

AI coding agents often work inside projects where authority is scattered across chat history, old handoff notes, source files, generated outputs, runtime state, logs, and personal notes. Without a governance layer, the agent may read too broadly, trust stale files, overwrite local conventions, or lose important decisions between sessions.

This project provides a small set of project-local files and reusable methods that let each project remain itself while still benefiting from a shared governance model.

The system also includes a lightweight global agent bridge. The global bridge helps the agent recognize adopted projects and route into local project files, while the project-local files preserve each project's real context.

## Design Principles

- Central method, local reality.
- Start from the smallest useful context.
- Treat sessions and memories as evidence, not authority.
- Let the user's latest instruction outrank stale plans and summaries.
- Let the user's latest instruction define the current work; do not activate discontinued planning projections.
- Preserve local strengths before adding new structure.
- Verify governance behavior with real routing and source-boundary probes.
- Log only material governance events that change future state or preserve evidence needed to interpret a result; do not log every conversation.
- Keep private data, logs, credentials, and raw conversations out of the reusable method.

## Visual Overview

![Project Intelligent Governance System overview](docs/media/system-architecture-en.svg)

See the [editable DOT source](docs/diagrams/system-architecture-en.dot) for this overview and [docs/flowchart.md](docs/flowchart.md) for additional diagrams.

The overview includes optional global guidance and the structural Skill; basic adoption through the prompt below does not require installing either or any Hook.

## Quick Start

Send the [interactive installation prompt](INSTALL.md) to Codex, select target folders and necessary capabilities, and let it preserve existing content and check minimal adoption. No Skill or runtime installation is required by default.

[Quick Start](QUICKSTART.md) covers optional advanced capabilities. File adoption and actual fresh-session use are verified separately; arbitrary environments are not guaranteed.

## Repository Layout

```text
docs/
  media/
    governance-flow-en.svg
    governance-flow-zh-CN.svg
  core-model.md
  logging-guide.md
  logging-guide.zh-CN.md
  adoption-guide.md
  verification-guide.md
  global-agent-integration.md
  desensitization-map.md
  flowchart.md
templates/
  global-agents-snippet.md
  AGENTS.md
  docs/
.agents/
  skills/
    project-governance/
examples/
  demo-project/
```

## Delivery Form

The documentation project remains the method authority. The public installation includes the `$project-governance` Codex Skill, local project templates, and an optional lightweight global agent bridge. The Windows transaction runner is optional.

`project-governance` handles structural adoption, migration, source authority, synchronization, mechanism repair, explicitly activated layered diagnosis, and governance verification. A dedicated user command such as `启动分层诊断` is required to enter layered diagnosis; ordinary corrections and governance discussion do not activate it. The planning projection and its standalone Skill are discontinued. Historical diagrams or archived materials that still depict that feature do not describe current capability. A real target-project conversation is useful evidence of local activation, but the optional Windows transaction runner is not a default installation dependency.

MCP, plugin, or app packaging should come later, after local source-of-truth, privacy, registry, and live activation behavior are stable.

## Global Agent Bridge

See [docs/global-agent-integration.md](docs/global-agent-integration.md) for the global instruction layer and why it stays separate from project-local governance files.

## Privacy

This public version uses placeholders and sanitized examples. It should not contain local absolute paths, private project names, credentials, runtime logs, raw conversations, account data, or machine-specific state.

## Status

`v0.1.0-preview.2`: interactive minimal adoption with bounded WSL retest evidence. See [onboarding verification](docs/onboarding-verification.md) for the six accepted retest turns, retained failures, costs and platform limits. Earlier [Windows runtime verification](docs/release-verification.md) covers separate optional tools; it is not native Windows onboarding acceptance.

## License

MIT. See [LICENSE](LICENSE).
