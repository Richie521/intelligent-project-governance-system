# Quick Start

Start with the [interactive installation prompt](INSTALL.md) in Codex. Say whether this is a new project, in-place adoption of an existing one, or a move to a separate new folder; provide known paths and choices or let it ask for missing scope decisions together. A new project gets only the needed entry, and an existing project may select bounded material review. A move reads the [migration guide](MIGRATE.md) only when selected. Basic adoption needs no Hook, Skill, Git, Python or runtime installation. The preview.5 package includes the migration guide; running a project script or starting a service still requires the current user's explicit authorization.

File-adoption checks and actual use in a fresh session are separate outcomes. Unsupported or conflicting targets must be reported incomplete.

## Existing projects: organize material when needed

With the installation prompt, choose organization of existing material and provide selected folders and conversation links or exports. Basic adoption remains available on its own. Codex clarifies missing scope, indexes sources and destinations, preserves originals and distills stable decisions. Unavailable conversations remain explicit gaps.

Start ordinary work directly in a fresh conversation. To continue an old one, send: "First read only this project’s current entry, then follow its routes to read the latest decisions and actual state needed in this turn. Do not substitute earlier conversation content for current files or consult personal memory. Reuse text already read in this turn, then continue working." This does not reinstall or reload all history. Even if every native page was read, missing original user messages require an export or an explicit gap. Distinguish saved material from actual resumed-session and fresh-session adoption, which require task evidence.

## Existing projects: move into a separate new folder

Start the move from the old project or downloaded package folder, giving the installation prompt the old folder, proposed new folder, material scope and working capabilities to retain. The target need not be opened in Codex first, since the host may create placeholder content there. Codex first presents an item-by-item selection and recovery plan. It copies only after unresolved choices that affect material or capabilities are confirmed. Existing content in a first-run target, including hidden content, stops the write; do not delete or silently merge it, and choose another separate empty folder when appropriate. Inspect the inventory, source and target hashes, separately recorded path edits, and functional checks in the new folder. Preserve the old project. Historical citations can point back to old sources, while ordinary work must not depend on an undeclared old-folder path.

Start future work in a new conversation attached to the new folder. Call an old conversation transferred only after the host actually switches its working directory and verifies the new entry; where the current desktop host cannot choose that folder, use a new conversation in it to carry selected context. The target's source index records created items and final file hashes for this move. On recovery or undo, a new conversation checks that receipt and later edits before removing only unchanged ordinary files created in this operation; preserve the index as evidence by default. If permissions prevent the host from entering the target, report copying and conversation availability separately, do not alter permissions on your own or claim completion; the user may create another separate empty folder and continue after rechecking it. Preserve conflicts for review. See the [migration guide](MIGRATE.md).

## Advanced adoption (optional)

The following Skill, bridge, and templates are for projects explicitly needing extra capabilities, not prerequisites for basic adoption. Do not mechanically create the full file set.

## 1. Install The Codex Skill

After cloning or downloading this repository, run one of these commands from its root.

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME\.agents\skills" | Out-Null
Copy-Item -Recurse -Force ".\.agents\skills\project-governance" "$HOME\.agents\skills\"
```

macOS or Linux:

```bash
mkdir -p "$HOME/.agents/skills"
cp -R ./.agents/skills/project-governance "$HOME/.agents/skills/"
```

Codex normally detects Skill changes automatically. Restart Codex if `$project-governance` does not appear. The checked-in copy remains reviewable under `.agents/skills/`; global installation makes it available in other projects.

The Windows governance transaction runner is optional and experimental. It is not required to install or use the Skill. For a project that has deliberately adopted the runtime, choose a project-local or other explicit install directory:

```powershell
& ".\tools\governance-transaction\install.ps1" -InstallDir "<project-root>\.governance-tools\transaction"
```

The runner needs no Codex restart. Use it only when the target project has deliberately adopted the runtime; it is not a default dependency. Hook-based activation guard setup is historical and unsupported in this release. Manual diagnosis starts from the user's explicit command and follows the documented agent process without a Hook or a machine-enforced boundary.

See [runtime installation and recovery](docs/runtime-tools.md) before enabling the optional runner.

## 2. Optionally Add The Global Bridge

For cross-project entry routing, optionally add `templates/global-agents-snippet.md` to your global `AGENTS.md`. It is not a prerequisite for single-project use. Keep the bridge small: it routes into project-local governance and does not store local business facts or private paths.

## 3. Choose The Target Project Path

For a new project, start with the local `AGENTS.md` entry produced by the installation prompt. Add a topic map, source-authority or context document only when the project needs that separate owner; do not copy the whole template set by default. Reserve `00–05` for the shared governance interface, with `03` disabled and `05` optional. Do not create or maintain a `03` planning projection. Start project-specific document ranges at `10`. Keep human-readable filename stems within six Chinese characters where practical; same-series files share a base number and add a short hyphen suffix. At deeper levels, use three-digit child numbers and four-digit history or archive numbers by appending a child sequence to the parent number. When a decision document is needed, adapt `templates/docs/09-decisions.md` to `docs/10-decisions.md`; source numbering does not set the target path.

Use the files in `templates/` as the starting point. First accept an existing `zh-CN` or `en` declaration. Without one, compare the user's primary interaction language with the existing governance entry language; select when they agree and ask once when they conflict. Persist the confirmed value in `AGENTS.md`, and do not switch it because a later turn uses another language.

English projects start from `templates/AGENTS.md` and the unsuffixed English files under `templates/docs/`. Chinese projects start from `templates/AGENTS.zh-CN.md` and the Chinese-named files. Select the matching governance-log template; never mix two authoritative languages in one project.

Only when the project explicitly adopts the optional Windows transaction runner, initialize `.codex/governance-runtime.json` from `templates/governance-runtime.json`. Keep this manifest read-only during routine work. Runtime setup, hash registration, and manifest validation are unnecessary for basic governance adoption. If using the runner, the template's zero hashes are placeholders; record actual SHA-256, byte count, and modification time for the entry, topic map, source authority, and context rules, then validate with the installed runner:

```powershell
& "<installed-transaction-directory>\run.ps1" `
  --project-root "<absolute-target-project-path>" validate-manifest
```

An authority-source change invalidates the manifest. Refresh its records only as an explicitly authorized governance adaptation, never silently.

For an existing project, do not overwrite its working files. Basic adoption can add the needed local entry without a Skill. If reviewing old project context would help, make it optional and bounded: you choose the relevant native conversations, or provide exports when those conversations are unavailable. Record every in-scope item, its review status, source, and destination. Keep original files and conversations in place; write durable decisions into the project file that owns them.

For a project move, use the separate-folder path and migration guide above. For a long-conversation handoff, distill only necessary decisions from selected, obtainable material; an old chat or summary is not a working entry for the new folder.

When resuming a selected old conversation, use this one-line instruction: “First read only this project’s current entry, then follow its routes to read the latest decisions and actual state needed in this turn. Do not substitute earlier conversation content for current files or consult personal memory. Reuse text already read in this turn, then continue working.” Leave original materials in place and keep any selected conclusions traceable to their source.

After adoption, start ordinary work directly. When maintaining later important files, the agent protects the needed pre-task state under the local entry; you need not register files or issue a separate backup command.

## 4. Start With Read-Only Intake

For optional structural work, ask the agent to begin with a read-only pass:

```text
Read this project's AGENTS.md first. Do not modify files yet.
Identify the smallest useful context, source boundaries, private material,
runtime state, generated output, historical material, and durable knowledge
candidates. Then propose a local governance shape before editing anything.
```

If you installed the optional Skill, you may call it explicitly:

```text
Use $project-governance. Start read-only, identify whether this is a new,
existing, or migrating project, and propose the smallest local landing plan.
```

## 5. Adapt The Complete Local Mechanism

Do not paste generic rules blindly. The target project should answer:

- What is the local entry file?
- Which files are authoritative?
- Which files are generated, runtime state, reports, caches, or historical evidence?
- What should never be committed or published?
- What local strengths already exist?
- What needs writeback after a task?

The `03` planning projection is discontinued. Do not install a planning Skill or create, read, update, or maintain a planning file as part of this method. Determine the current work from the user's latest instruction. When installed, the optional `$project-governance` Skill can support structural governance; ordinary corrections and governance discussion do not activate manual layered diagnosis.

Do not copy a governance-log template alone. Inspect existing development logs, troubleshooting histories, and run archives first. Use `templates/docs/governance-log.en.md` only when material governance events recur and no existing owner fits. See `docs/logging-guide.md` for triggers, corrections, machine evidence, and privacy.

## 6. Optional Local Verification

Use `docs/verification-guide.md` when the project needs a local governance verification. The Windows transaction runner and live activation are not prerequisites for installing the Skill or adapting templates.

Minimum probes:

- Can a new conversation start its normal task from the local entry file when relevant?
- Can a source conflict route to the right authority?
- Are old handoff notes treated as evidence instead of active rules?
- Manual activation: do ordinary corrections, drift reports, file conflicts, and writeback discussion stay in normal task handling, while a dedicated command such as `启动分层诊断` opens layered diagnosis?
- Does an ordinary no-change task stay unlogged while a material governance change is recorded exactly once in the correct local owner?
- Does an ordinary no-change task perform zero governance-file reads, writes, and governance-tool calls?
- If the project explicitly enabled the optional transaction runner, does a defined multi-projection transaction use exactly one `apply` without loading Skills, memory, or cold-path governance docs?

Keep wording and verbosity improvements as non-blocking risks only when behavior still passes.

Do not report an overall pass until the required acceptance evidence is present. An unverified or unavailable item stays pending or incomplete.

## 7. Keep The Method Small

Only write durable knowledge when it changes future routing, authority, verification, safety, decisions, recurring diagnosis, pattern status, sync status, or release position.
