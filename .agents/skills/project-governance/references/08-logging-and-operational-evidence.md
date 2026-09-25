# Logging And Operational Evidence

Use this reference when a task may create a material governance event, machine evidence, a log correction, or a change to current adoption or sync state.

## Responsibilities

Keep four responsibilities separate:

- governance log: material human-readable event history;
- run archive: reproducible machine inputs, versions, parameters, and outputs;
- decision record: confirmed stable choices;
- state owner: current adoption, verification, synchronization, or release state.

One event may update more than one owner, but no owner replaces another.

## Event Trigger

Log an event only when the actual result changes future governance state or preserves evidence needed to explain a material result. Typical triggers are an adoption or activation change, migration or handoff, method or local-governance change, failed probe and repair, synchronization state change, or release gate.

Do not log routine reads, ordinary discussion, an unchanged probe, one-off command output, or every Skill invocation.

## Event Record

Use `gov-YYYYMMDDTHHMMSS-short-name` and an ISO 8601 timestamp with timezone. Record:

- trigger and objective;
- scope and authorization boundary;
- actual result;
- verification result;
- hard failures and non-blocking risks;
- writeback destination;
- machine evidence or local file references;
- cross-project synchronization impact.

Use the target project's primary human-readable language. Reuse an existing development log, troubleshooting history, audit record, or project log when its responsibility fits. Create a focused governance log only when material events recur and no existing owner fits.

## Machine Evidence

Create a run archive only when scripts, batch probes, diagram generation, release checks, or another execution produce reproducible artifacts. Reuse the project's existing archive or the tool's native evidence package. Pure conversation events receive no empty run directory.

Keep enough provenance to identify the relevant inputs, implementation or configuration version, parameters, status, and result. Distinguish source, artifact, and canonical-content hashes. Keep raw output local only when needed, allowed, and covered by a retention rule.

## Corrections And Privacy

Append completed events. If later evidence changes the meaning, add a new event that references the old identifier. Do not silently rewrite the historical result.

Never record raw conversations, hidden reasoning, user-expression profiles, credentials, account material, full tool output, unrelated private data, or an adopted project's business facts in a central method log.

## Probe

Verify both sides:

1. a no-change read-only task creates no event;
2. a material governance change creates exactly one event in the correct local owner and links any separate decision, state update, or machine evidence.

Missing material evidence, duplicate parallel logs, registry history accumulation, an empty machine archive for conversation-only work, or private material in the wrong owner is a hard failure.
