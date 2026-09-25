# Core Model

The core model is: central method, local reality.

The shared method gives projects a repeatable way to manage agent context, source authority, durable decisions, verification, writeback, and improvement loops. It also provides unified wording, preserves the user's latest direction, and keeps an active long-task plan without making chat history authoritative. Each project still keeps its own local rules, domain knowledge, runtime facts, and privacy boundaries.

The former planning display is discontinued. Historical design material may remain for context, but it does not define current behavior or authorize planning-file reads or writes.

The global agent bridge is the entry signal. It tells the agent to look for project-local governance files when a project adopts this system. The bridge is small by design; it should not store project-specific facts.

## Center, Local System, And Adjacent Work

The Project Intelligent Governance Center is the reusable method source, templates, verification rules, and synchronization protocol. A Project Intelligent Governance System (Local) is the adapted instance that runs inside one target project. The seven governance modules belong to the same product, but most daily execution is local; landing and cross-project synchronization are coordinated by the center.

A project may also contain adjacent work such as a portfolio website, a flowchart-production Skill, public-release preparation, or model-selection tools. Those activities may use governance files or produce presentation assets, but they are not governance modules or default runtime dependencies.

## What The Method Solves

Long-running AI-assisted work fails when current source files, old notes, generated outputs, runtime state, reports, and chat history all compete as context without clear authority.

This method creates a small governance layer so the agent can decide what to read, what to trust, what to ignore, and what to write back.

## Durable Knowledge

Durable knowledge is anything that changes future routing, authority, verification, safety, decisions, or recurring diagnosis.

Raw sessions, memory summaries, and handoff notes are evidence. They do not become authority until distilled into the correct project file.

Daily work may read, update, or generate files. Reuse a fitting owner first; create and route a focused low-impact topic only during authorized work, defer high-impact or unclear destinations, and create no long-term file for one-off content.

Reuse an existing file when its responsibility fits. During authorized work, a focused low-impact topic may be created together with its topic-map route when no existing owner fits. Confirm changes to authority, privacy, topic structure, or long-term governance first. Discussion-only work defers the write, and one-off content does not receive a long-term file. Source-of-truth or manifest records change only when file role or authority changes.

## Layered Diagnosis And Feedback

Self-reflection and layered diagnosis operate throughout project work, not only during initial adoption.

When user dissatisfaction, goal drift, file conflict, failed verification, or repeated friction appears, distinguish two directions. Rules apply top-down: global guidance, project mechanism, then current task. Diagnose failures bottom-up in this order:

1. user input and the current task: goal, information, authorization, and work sequence;
2. the target project's mechanism: entry, routing, authority, verification, and writeback.
3. general agent behavior: global guidance, Skill behavior, and tooling, only when the defect may recur across unrelated projects.

Stop at the first layer that fully explains the failure. If several layers contributed, record their causal connection to one primary root cause. The inspection order is not a layer-by-layer advice outline: record one inspection stop, give non-responsible layers only exclusion or stop reasons, and produce one prevention plan anchored to the primary root. Repair the smallest durable surface, rerun the failed probe, and promote only genuinely reusable local lessons into the central method. Central changes normally return through local discussion and verification rather than bulk replacement; an explicit user authorization for a Governance Center cross-project repair is the narrow exception and still requires per-project adaptation, rollback, and evidence.

If the same class of failure appears again after a claimed repair, pause domain writes, reconstruct the correction and failure sequence, continue beyond the current-task layer, state each contributing layer, and verify the repair in the real task or an equivalent probe. This gate does not create a long-term profile of user expression.

Ordinary project writeback remains local: write durable facts or decisions into a fitting project file, or write nothing for a one-off result. Central promotion is a later self-improvement or sync decision, not a parallel ordinary writeback destination.

## Typical Local Surfaces

- a lightweight global-agent bridge outside the project;
- `AGENTS.md`
- `docs/00-topic-map.md`
- `docs/01-source-of-truth.md`
- `docs/02-context-management.md`
- `docs/04-governance-log.md` as the stable route to the actual project log
- `docs/09-decisions.md`
- focused topic docs that match the project's real work
- a declared wording surface only when the user has approved unified wording

Optional surfaces can include a standalone project wording table, human-readable logs, machine run archive policies, migration notes, or verification checklists when the target project needs them.

The `00–05` numbers are reserved for the shared governance interface; `05` is created only when a project enables unified wording. Project-specific documents start at `10` and use local domain ranges. Human-readable filename stems should stay within six Chinese characters where practical; same-series files share a base number and add a short hyphen suffix. A first-level topic subdirectory appends a child sequence to form a three-digit number; a second-level history or archive directory appends another sequence to form a four-digit number. Machine interfaces, code identifiers, vendor files, historical snapshots, and ecosystem conventions may keep their required names.

Unified wording is optional for long-running, complex, or naming-sensitive projects. The system may recommend it, but it is enabled only after user approval and a local-entry declaration naming the wording surface. Projects that have not enabled it add no declaration, carrier, empty table, or probe. An enabled project uses an existing topic document or a standalone project wording table as its surface. A fresh conversation reads that surface once after the local entry; context-compression recovery reads it once again. The same context refreshes it only after the surface changes or for naming and material wording work. Harmless abbreviations, equivalent expressions, and uniquely correctable voice input are normalized silently. Material meaning, decision, verification, or durable-naming differences trigger one clarification. Write back only after user confirmation, and verify adoption in later real work. Do not retain unconfirmed candidates, raw prompts, expression profiles, or cross-conversation frequency, and do not create an empty table.

Keep machine reproduction material in run archives, human-readable process in concise logs, and stable confirmed choices in decision records. These three responsibilities must not absorb raw conversations, credentials, or unrelated private material.

Governance logs are event-triggered rather than turn-triggered. Record a material event only when it changes future state or preserves evidence needed to interpret a result. Keep current status in its state owner. See `logging-guide.md` for the record, correction, machine evidence, and privacy rules.
