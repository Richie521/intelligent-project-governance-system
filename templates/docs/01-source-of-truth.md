# Source Of Truth

Define which files or systems are authoritative for this project.

## Authority Layers

| Layer | Examples | Authority |
| --- | --- | --- |
| Source | current implementation, canonical data, product rules | authoritative for behavior |
| Project docs | topic docs, decisions, architecture notes | authoritative when current |
| Governance language | `AGENTS.md` declaration `zh-CN` or `en` | authoritative for human-readable governance files and entries |
| Confirmed wording, only when unified wording is user-approved | declared existing topic document or optional standalone project wording table | local wording authority only after the local entry declares the capability enabled and names that carrier |
| Governance-log entry | `docs/04-governance-log.md` | stable log router; may point to monthly, development, or domain logs without duplicating event bodies |
| Generated output | build output, exports, reports | evidence unless explicitly authoritative |
| Runtime state | databases, logs, process state | evidence for live behavior |
| Governance event history | existing project log or approved focused governance log | material process evidence, not current state or stable decisions |
| Historical material | handoff notes, old sessions, snapshots | evidence only |
| Private material | credentials, account data, personal notes | not default context |

## Conflict Rule

When materials disagree, state which layer is authoritative and why. Keep uncertainty visible until verified. Fact authority does not select the maintenance baseline: retain the existing result chosen by the user, even if generated, and compare authorized changes with content that must remain.

The user's latest instruction determines the current work. Historical plans and handoff notes are evidence only and cannot override it.
