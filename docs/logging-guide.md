# Logging And Operational Evidence Guide

The Project Intelligent Governance Center defines material-event logging. Each local Project Intelligent Governance System uses it, and does not log every conversation or governance Skill invocation.

## Four Responsibilities

| Responsibility | Content |
| --- | --- |
| Governance log | Material governance events people still need to understand |
| Machine run archive | Evidence needed to reproduce scripts, batch probes, diagrams, or release checks |
| Decision record | Confirmed stable choices |
| State owner | Current adoption, verification, synchronization, or release state |

One event may update several owners, but each result stays in the owner that matches its responsibility. The state owner is not a history log.

## When To Record

Record an event when adoption, migration, live activation, local governance, failed-probe repair, synchronization state, or a release gate changes materially. Do not log routine reads, ordinary discussion, unchanged probes, or one-off commands.

Use `gov-YYYYMMDDTHHMMSS-short-name` and an ISO 8601 timestamp with timezone. See `templates/docs/governance-log.en.md` for the record shape.

## Choose A Local Owner

Inspect existing development logs, troubleshooting histories, audit records, and run archives first. Reuse a fitting owner. Create a dedicated governance log only when material governance events recur and no existing owner fits. Projects do not need identical file names or directories.

Create a machine run archive only when scripts, batch probes, diagram generation, release checks, or another execution produce reproducible artifacts. A pure conversation event does not receive an empty run directory.

## Correction And Privacy

Append completed events. When later evidence changes an older conclusion, add a correcting event that references the original identifier instead of silently rewriting its meaning.

Do not store raw conversations, hidden reasoning, user-expression profiles, credentials, account material, full tool output, or unrelated private data. Central method files must not absorb an adopted project's business facts. A public repository contains only method, templates, and sanitized examples.

## Verification

Run two opposite probes:

1. an ordinary no-change read-only task creates no governance event;
2. a material governance change creates exactly one event in the correct local owner and references any separate decision, state update, or machine evidence.

Missing a material event, duplicating one event across parallel logs, keeping history in the active plan or state owner, creating a machine archive for a pure conversation, or writing private content to the wrong owner is a hard failure.
