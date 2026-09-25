# Context Management

This project should remain easy for a future agent session to resume.

## Task Lifecycle

```text
classify task
-> declare read scope and exclusions
-> read the smallest relevant context
-> act only after authorization when changes are needed
-> verify behavior
-> report writeback result
```

## Do Not Read By Default

- logs
- caches
- generated output
- private notes
- raw conversations
- historical snapshots
- machine run archives

Read those only when the task needs them as evidence.

## Unified Wording

This section applies only after the user approves unified wording for the project. When enabled, the local entry declares either an existing topic document or a justified standalone project wording table as the surface. When not enabled, omit this section and do not create a carrier, empty table, or probe.

An enabled project's new conversation reads the declared surface once after the local entry; context-compression recovery reads it once again. The same context does not reread it every turn and refreshes it only after the surface changes or for naming and material wording work. Use confirmed wording silently for harmless abbreviations, equivalent expressions, and uniquely correctable voice input. Raise only differences that can change meaning, decisions, verification, or durable naming. Propose one unified expression after checking meaning and usage boundaries; write back only after user confirmation, and verify adoption in a later real task. Store no unconfirmed candidates, raw prompts, expression profiles, or cross-conversation frequency.

## Durable Knowledge

Write durable knowledge when it changes future routing, authority, verification, safety, decisions, or recurring diagnosis.

## Governance Language

Use the `zh-CN` or `en` value declared in `AGENTS.md`. If no valid declaration exists during adoption, compare the user's primary interaction language with the existing governance entry language. Select when they agree and ask once when they conflict or remain unclear. Persist the confirmed value during authorized execution. Do not switch it because one later turn uses another language.

The choice applies only to human-readable governance files and entries. Do not batch-translate business documents, code, vendor files, runtime output, or historical snapshots.

## Durable Destinations

Prefer an existing file when its responsibility fits. During authorized execution, create a focused topic file and update `docs/00-topic-map.md` in the same turn when its role and path are clear and it does not change source authority, privacy, or long-term governance structure. Explain and confirm those high-impact changes first. During discussion-only work, report deferred writeback. One-off content stays in the conversation.

Update the source-of-truth document or manifest only when a new file changes a file role or authority. File creation is decided by the active conversation; it is not background monitoring.

## Governance Event Logging

`docs/04-governance-log.md` is the fixed entry. When a project stores events by month or domain, this file routes to the actual owner and must not duplicate event bodies.

Record only material events that change future governance state or preserve evidence needed to interpret a result. Reuse an existing local development log, troubleshooting history, audit record, or project log when it fits. Create a focused governance log only when such events recur and no existing owner fits.

Leave ordinary reads, discussion, unchanged probes, and every Skill invocation unlogged. Create a machine run archive only when reproducible artifacts exist; keep stable decisions and current state in their own owners. Use `gov-YYYYMMDDTHHMMSS-short-name` to link separate owners when needed.
