# Project Rules

This project uses the Project Intelligent Governance Center as its method source and runs a local Project Intelligent Governance System.

Authoritative governance language: `en`.

Reserve `docs/00-topic-map.md`, `docs/01-source-of-truth.md`, `docs/02-context-management.md`, the disabled `03` slot, and `docs/04-governance-log.md` for the shared governance interface. Do not create or maintain a planning projection in slot `03`. When events are stored by month or domain, `04` is a stable router rather than a duplicate event body. Start project-specific document ranges at `10`; keep human-readable filename stems within six Chinese characters where practical, use short suffixes for same-series files, and append child sequences for three-digit first-level and four-digit second-level history or archive numbers.

This declaration controls human-readable governance files and project entries. Do not switch it because one conversation turn uses another language. Ecosystem filenames, identifiers, commands, and machine interfaces may stay in English. Do not batch-translate business documents, code, vendor files, runtime output, or historical snapshots.

## Scope

Describe what this project is for, what it is not for, and which files or systems are outside the agent's default scope.

## Reading Rules

Start from this file.

If the task is unclear, read `docs/00-topic-map.md`.

Do not add unified wording by default. If the user explicitly approves it for this project, declare here that it is enabled and name either an existing topic document or a justified standalone project wording table as its surface. A project that has not enabled it adds no declaration, carrier, empty table, or probe. When enabled, read the surface once after this entry in a new conversation and once again after context compression. Within the same context, refresh it only after the surface changes or for naming and material wording work. Normalize harmless abbreviations, equivalent wording, and uniquely correctable voice input silently; raise only differences that can change meaning, decisions, verification, or durable naming. Write back only after user confirmation.

Determine and perform the current task from the user's latest instruction. Do not read or use discontinued planning files as task routes, recovery sources, or execution authority. Historical planning materials remain historical evidence only.

Only projects that explicitly enable the optional governance runtime use this transaction path. For those projects, decide from the conversation whether a material governance event or explicitly authorized state change occurred. When there is no change, do not read the runtime manifest or projection files and do not call governance tools. Otherwise, submit only the authorized active projections through one governance transaction. When the current task already specifies the projections, target owners, and authorization, use the lightweight runtime path: do not load `$project-governance`, memory, the topic map, or full verification docs. Pre-read an affected owner at most once only when an exact operation needs its current text, call `apply` once, and use its terminal receipt as the unified verification and sole writeback result.

Central-method changes normally require local discussion. When the user explicitly authorizes a cross-project repair from the Project Intelligent Governance Center, adapt that repair locally without treating it as business-work or adoption-status authorization. Mark each local runtime request with `contract_tags: ["central_repair_sync"]`. A project without the governance runtime must not claim a transaction receipt.

Handle ordinary corrections in the current task. Enter layered diagnosis only after a dedicated user command such as `启动分层诊断`; ordinary corrections and governance discussion do not activate it. Use `$project-governance` for structural governance, not for executing an already-defined transaction. Public-release and release-readiness work stays outside this local governance routing.

Use the smallest useful context. Do not read logs, generated output, caches, private notes, or historical handoff files unless the task needs that evidence.

For a material governance event, route through `docs/04-governance-log.md` to the project's actual log owner.

## Source Boundaries

Read `docs/01-source-of-truth.md` when authority is unclear or conflicting. When the target and its role are already known, read that target directly without first loading the authority guide.

Treat sessions, memory, old notes, and reports as evidence until their durable value is written into the right project file. Verify facts against their authority, while preserving the existing result the user chose to maintain. A generated artifact can be the maintenance baseline; compare authorized changes and retained content rather than treating a passing build as proof.

The user's latest instruction outranks old plans and assistant summaries. Historical planning materials never override the current request.

## Daily File Maintenance

When starting file maintenance, judge from its actual use whether it holds lasting work and whether replacement would lose content that should be retained. This also applies to later new material; the user need not register files or issue a separate backup command. By default preserve the version before each independent maintenance task; assess intermediate edits within that task by actual risk rather than backing up every tool write. Prefer a declared, verifiable recovery method that covers the complete current content. Git alone is insufficient: assess uncommitted and untracked content separately. Without a reliable method, create a byte-identical copy only when protection is first needed, under project-local `.backups/<recovery-point>/<original-relative-path>`, or reuse an existing suitable location. Retain previous recovery points without overwriting them; preserve complete content, encoding and line endings, with enough path and task-state identity for a new session to recover it. An index, summary or backup claim alone is insufficient. Authorized maintenance includes necessary local backups; confirm only extra scope, external storage or material selection decisions. Read-only work, no-change tasks and reliably reproducible temporary outputs need no extra backups; do not duplicate a reliable recovery point. New material does not automatically trigger a library scan, governance log, transaction or governance Skill. If backup or recovery fails, access is denied or concurrent changes appear, stop the affected overwrite and report the actual state. Check later edits before recovery; restore old content to a separate inspection file when appropriate and never overwrite later work by others. These are agent instructions, not machine-enforced interception or atomic protection against arbitrary external editors.

## Human-Readable Markdown Layout

Keep ordinary governance paragraphs and list continuations on one physical line. Do not hard-wrap an unfinished sentence or semantic phrase at a fixed column width. Preserve code blocks, math, tables, quoted blocks, explicit hard breaks, and blank-line paragraph boundaries. Run the governance Markdown checker before closing work that changes governance Markdown.

## Writeback

At task close, report one writeback result:

```text
Writeback: none
Writeback: updated <path>
Writeback: deferred because <reason>
```

Write back only when the task changes future routing, authority, verification, safety, decisions, or recurring diagnosis.

Prefer an existing file whose responsibility fits. During authorized execution, create a focused topic file and update `docs/00-topic-map.md` in the same turn when its role and path are clear and it does not change authority, privacy, or long-term governance structure. Confirm those high-impact changes first. During discussion-only work, report the proposed file as deferred; do not create a long-term file for one-off content. Update source-of-truth or manifest records only when file role or authority changes.

Move durable decisions, open questions, and governance events into the files that own them.

Record a governance event only when the actual result changes future governance state or preserves evidence needed to interpret a material result. Reuse an existing local log owner when it fits; do not log routine reads, ordinary discussion, unchanged probes, or every Skill invocation. Keep machine evidence, stable decisions, and current state in their separate owners.
