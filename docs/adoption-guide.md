# Adoption Guide

Adoption means adapting the method to a project's real work. It does not mean copying every file name or rule from this repository.

Classify the project before intake:

- New project: greenfield work with no existing code, data, or runtime state; clarify the objective, scope, privacy boundary, and needs before proposing a minimum local governance layer.
- Existing project: any project with code, data, documents, or runtime state, even when this is its first governance adoption.
- Migration project: work with source and target locations or conversation assets that must be classified before confirmed assets move.

## Phase 0: Select The Governance Language

Use an existing local `AGENTS.md` declaration when it is `zh-CN` or `en`. Without a valid declaration, compare the user's primary interaction language with the existing governance entry language. Select the language when they agree; ask once when they conflict or remain unclear. During authorized execution, persist the confirmed value in the local entry and record the evidence, final value, and declaration path in the intake report.

Use the matching language template. Do not switch because one later turn uses another language, maintain two competing authorities, store per-turn language statistics, or batch-translate business documents, code, vendor files, runtime output, or historical snapshots.

For English projects, start from `templates/AGENTS.md` and the unsuffixed English files under `templates/docs/`. For Chinese projects, start from `templates/AGENTS.zh-CN.md` and the Chinese-named files under `templates/docs/`. Both routes use the matching task and governance-log language files.

## Phase 1: Read-Only Intake

Identify entry files, existing rules, source files, generated files, runtime state, reports, caches, historical notes, private material, and external systems.

Do not edit during intake.

## Phase 2: Preserve Local Strengths

Look for useful existing patterns such as topic maps, naming conventions, decision records, validation scripts, confirmed-wording owners, or log separation.

Do not overwrite working local practices with generic central text.

Central changes still require local adaptation. If the user explicitly authorizes a cross-project repair from the Governance Center, treat that phrase as authorization for the stated governance repair only. A project with the runtime marks its request with `central_repair_sync` and includes an idempotent or changing Task projection; a project without the runtime performs any affected Task update in the same work cycle without claiming a transaction receipt.

## Phase 3: Classify Authority

Classify relevant files as source, generated output, runtime state, report, private note, cache, historical snapshot, handoff draft, external authority, or unknown.

Keep uncertainty visible until verified.

## Phase 4: Design Local Governance

Create the smallest set of local governance files that lets a future agent start safely and find the right context.

Reserve `00–05` for the shared governance interface: topic map, source authority, context management, the disabled `03` slot, governance-log entry, and (when enabled) the project wording surface. Do not create or maintain a planning projection in slot `03`. Keep ecosystem entries unnumbered and start project-specific document ranges at `10`. A monthly or domain log keeps its actual event bodies; `04` is only the stable route. Keep human-readable filename stems within six Chinese characters where practical; same-series files use a shared base number with a short hyphen suffix. First-level topic subdirectories use three-digit child numbers and second-level history or archive directories use four-digit numbers by inheriting the parent prefix. Machine interfaces and historical material may keep necessary names.

Reuse an existing file when its responsibility fits. During authorized work, create a focused topic file and update the local topic map in the same turn only when the role and path are clear and the change does not alter authority, privacy, or long-term governance structure. Confirm those high-impact changes first. Discussion-only work proposes the destination without creating it, and one-off content does not receive a long-term file. Update source-of-truth or manifest records only when file role or authority changes.

The planning projection and its standalone Skill are discontinued. Do not install a planning Skill or create, read, update, or maintain planning files as part of this method. Use `$project-governance` for structural adoption, migration, source authority, synchronization, governance repair, and governance verification. Enter manual layered diagnosis only after a dedicated user command such as `启动分层诊断`; ordinary corrections and governance discussion do not activate it. Public-release and release-readiness work stays outside this governance routing.

Unified wording is optional. Recommend it only for long-running, complex, or naming-sensitive projects, and enable it only after user approval. A project that has not enabled it adds no declaration, carrier, empty table, or probe. When enabled, declare either an existing topic document or a standalone project wording table as its surface. A fresh conversation reads the surface once after the local entry; context-compression recovery reads it once again. The same context refreshes it only after the surface changes or for naming and material wording work. Harmless variation is normalized silently; material meaning, decision, verification, or durable-naming differences trigger one clarification. Write back only after user confirmation, create no empty table, and verify adoption in later real work.

Add project-log, run-archive, or decision surfaces only when the project has the corresponding recurring need. Machine reproduction material, human-readable process, and stable decisions must remain separate; do not copy raw conversations, credentials, or unrelated private material into any of them.

For governance events, first identify an existing development log, troubleshooting history, audit record, or project log that can own the human record. Create a dedicated governance log only when material events recur and no existing owner fits. Connect the trigger through the local entry, router, source boundary, context rules, and probes. Do not create a machine archive for a pure conversation event. See `logging-guide.md`.

## Phase 5: Verify

Use the probes in `verification-guide.md`.

Adoption is complete only when representative questions route correctly in the target project.

Verify that ordinary and merely related conversations do not read the plan at task start, every turn-close preservation candidate is absorbed without activating other items, and completed items leave durable outcomes before removal.

For a Governance Center repair, verify that local adaptations stay within the authorized scope and preserve the target project's adoption state and business boundary.

Also run governance-language probes for existing Chinese and English declarations, consistent inference, one-time conflict handling, and a later single-turn language change that must not alter the declaration.

For human-readable governance Markdown, keep ordinary paragraphs and list continuations on one physical line. Do not introduce fixed-column hard wraps inside unfinished sentences or semantic phrases. Preserve code blocks, math, tables, quoted blocks, explicit hard breaks, and blank-line paragraph boundaries. After landing or changing governance Markdown, run `tools/governance-markdown/reflow_markdown.py check --project-root <project>` before handoff; the probe covers the current `docs/` tree and excludes history, archive, and backup directories.

When a claimed repair is followed by the same class of failure, adoption cannot pass by fixing only the current reply again. Pause domain writes, reconstruct the sequence, inspect the project mechanism and any potentially reusable global or Skill failure, then rerun a real task or equivalent probe.

Ordinary writeback updates a fitting local durable file or nothing for one-off content. Send a lesson to the central method only after self-improvement or synchronization verifies that it is reusable.
