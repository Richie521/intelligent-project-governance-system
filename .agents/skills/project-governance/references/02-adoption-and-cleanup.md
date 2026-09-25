# Adoption And Cleanup

Use this reference for new project adoption and existing project governance cleanup.

## New Projects

Use this category only for greenfield work without existing code, data, documents, or runtime state. Clarify the objective, scope, privacy boundary, and expected work before proposing files. If existing assets are present, use the existing-project path even when governance is new.

Resolve the authoritative governance language before selecting templates. Accept an existing `zh-CN` or `en` declaration. Without one, compare the user's primary interaction language with the existing governance entry language; select when they agree and ask once when they conflict or remain unclear. Persist the result in the local entry during authorized execution and do not switch it because a later turn uses another language. This applies only to human-readable governance files and entries, not business documents, code, vendor files, runtime output, or historical snapshots.

Create the smallest useful local governance layer. Prefer:

- fixed public governance slots `00` topic map, `01` source authority, `02` context management, disabled `03`, `04` governance-log entry, and optional `05` project wording surface; do not create a planning projection in slot `03`;

- local `AGENTS.md`;
- topic map;
- source-of-truth or authority-boundary document;
- context-management and writeback rules;
- selective context loading, source verification, and bounded scope expansion;
- decision record;
- verification guide or checklist.

Keep ecosystem entry filenames unnumbered. Start project-specific document ranges at `10`. Human-readable filename stems should stay within six Chinese characters where practical; same-series files share a base number and add a short hyphen suffix. Machine interfaces, code identifiers, vendor files, and historical snapshots may keep required names. When logs are stored by month or domain, `04` is a stable router and must not duplicate event bodies. Existing projects with conflicts need an old-to-new map, collision checks, current-reference updates, and preserved historical path meaning.

Unified wording is optional for long-running, complex, or naming-sensitive projects and requires explicit user approval. Projects that have not enabled it add no declaration, carrier, empty table, or probe. An enabled project declares an existing topic document or a justified standalone project wording table as its surface. A fresh conversation reads that surface once after the local entry; context-compression recovery reads it once again. The same context refreshes it only after the surface changes or for naming and material wording work. Harmless variation is normalized silently; material meaning, decision, verification, or durable-naming differences trigger one clarification. Write back only after user confirmation, create no empty table, and verify later real adoption.

Add human-readable log, machine run archive, or decision surfaces only when the project has the corresponding recurring need. Do not create empty files as adoption ceremony. Machine reproduction material, human process, and stable decisions must remain separate and exclude raw conversations, credentials, and unrelated privacy.

Do not copy central wording blindly. Adapt rules to the target project's actual files, tests, data, privacy risks, and work habits.

Prefer an existing file when its responsibility fits. During authorized execution, create a focused topic file and update the topic map in the same turn when its role and path are clear and authority, privacy, and long-term governance structure do not change. Explain and confirm those high-impact changes first. During read-only or discussion-only work, report the candidate destination as deferred. Do not create a long-term file for one-off content, and update source-of-truth or manifest records only when file role or authority changes.

The planning projection and its standalone Skill are discontinued. Do not install a planning Skill or create, read, update, or maintain planning files as part of this method. Determine the current work from the latest user instruction. Migration, handoff, and long-work recovery use relevant evidence and project authority.

## Existing Projects

This category includes every project with existing code, data, documents, or runtime state, including first-time governance adoption.

Before proposing changes, classify files:

- current execution authority;
- current reference;
- historical evidence;
- generated or runtime output;
- stage plan;
- discussion draft;
- private or non-public material.

When the project is being renamed, moved, or cleaned before migration, produce a migration asset map before copying files. Use the language-matched `assets/migration-asset-map.zh-CN.md` or `assets/migration-asset-map.en.md` to separate both file assets and conversation assets:

- migrate into the clean target project;
- keep only as historical evidence;
- leave in the old source location;
- do not migrate;
- ask the user before deciding.

For conversations, do not equate "useful" with "write into files." Classify each relevant conversation as long-term file material, handoff prompt material, source-index-only, out of scope, or needing user confirmation.

Keep local strengths. If an existing file already owns a responsibility, merge stable rules there instead of creating a parallel governance file.

Keep raw logs, run archives, long conversations, large document collections, private material, and historical corpora outside the default working context. Use retrieval only to locate candidate evidence. Require a provenance path back to the local source-of-truth, current implementation, current runtime, or external primary source, plus a bounded expansion route when evidence is insufficient or conflicting.

Ask before deleting, moving, renaming, merging, or large-scale rewriting.

## Completion

Adoption is not complete until representative probes pass, including a manual activation probe. Ordinary correction, execution-drift, file-conflict, and writeback language must remain inactive unless the user sends the dedicated activation command.
