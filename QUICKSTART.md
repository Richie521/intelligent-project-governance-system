# Quick Start

Start with the [interactive installation prompt](INSTALL.md) in Codex. Supply target paths or let it ask for necessary choices. Basic adoption preserves existing content and adds only the needed local entry; no Skill, Git, Python, or runtime installation is required.

File-adoption checks and actual use in a fresh session are separate outcomes. Unsupported or conflicting targets must be reported incomplete.

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

The Windows governance transaction runner is optional and experimental. It is not required to install or use the Skill:

```powershell
& ".\tools\governance-transaction\install.ps1"
```

The runner needs no Codex restart. Use it only when the target project has deliberately adopted the runtime; it is not a default dependency. The optional activation-guard installer requires Python 3.11 or newer because it parses TOML with `tomllib`; the measured release environment uses Python 3.14.2. The host guard is experimental and is not installed by the command above.

See [runtime installation and recovery](docs/runtime-tools.md) before enabling either optional tool.

## 2. Optionally Add The Global Bridge

For cross-project entry routing, optionally add `templates/global-agents-snippet.md` to your global `AGENTS.md`. It is not a prerequisite for single-project use. Keep the bridge small: it routes into project-local governance and does not store local business facts or private paths.

## 3. Choose The Target Project Path

For a new project, copy and then adapt these files:

```text
AGENTS.md
docs/00-topic-map.md
docs/01-source-of-truth.md
docs/02-context-management.md
docs/04-governance-log.md
docs/10-decisions.md
```

Reserve `00–05` for the shared governance interface: topic map, source of truth, context management, the disabled `03` slot, governance-log entry, and optional project wording surface. Do not create or maintain a `03` planning projection. Start project-specific document ranges at `10`. Keep human-readable filename stems within six Chinese characters where practical; same-series files share a base number and add a short hyphen suffix. At deeper levels, use three-digit child numbers and four-digit history or archive numbers by appending a child sequence to the parent number. Copy the source template `templates/docs/09-decisions.md` to the target path `docs/10-decisions.md`; source numbering does not set the target path.

Use the files in `templates/` as the starting point. First accept an existing `zh-CN` or `en` declaration. Without one, compare the user's primary interaction language with the existing governance entry language; select when they agree and ask once when they conflict. Persist the confirmed value in `AGENTS.md`, and do not switch it because a later turn uses another language.

English projects start from `templates/AGENTS.md` and the unsuffixed English files under `templates/docs/`. Chinese projects start from `templates/AGENTS.zh-CN.md` and the Chinese-named files. Select the matching governance-log template; never mix two authoritative languages in one project.

Only when the project explicitly adopts the optional Windows transaction runner, adapt `templates/governance-runtime.json` into `.codex/governance-runtime.json`. Runtime setup, hash registration, and manifest validation are unnecessary for ordinary Skill-based governance adoption. If using the runner, the template's zero hashes are placeholders; record actual SHA-256, byte count, and modification time for the entry, topic map, source authority, and context rules, then validate with the installed runner:

```powershell
& "<installed-governance-runner-path>" `
  --project-root "<absolute-target-project-path>" validate-manifest
```

An authority-source change invalidates the manifest. Refresh its records only as an explicitly authorized governance adaptation, never silently.

For an existing project, do not overwrite its working files. Start with `$project-governance` read-only intake, classify existing responsibilities, and merge stable rules into the files that already own them.

For a project migration or long-conversation handoff, start with the migration asset map. Separate active files, historical evidence, runtime or generated state, private material, conversation handoff material, and durable conclusions before copying anything.

## 4. Start With Read-Only Intake

Ask the agent to begin with a read-only pass:

```text
Read this project's AGENTS.md first. Do not modify files yet.
Identify the smallest useful context, source boundaries, private material,
runtime state, generated output, historical material, and durable knowledge
candidates. Then propose a local governance shape before editing anything.
```

Use the installed Skill explicitly for the first run:

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

The `03` planning projection is discontinued. Do not install a planning Skill or create, read, update, or maintain a planning file as part of this method. Determine the current work from the user's latest instruction. Use `$project-governance` for structural governance; ordinary corrections and governance discussion do not activate manual layered diagnosis.

Do not copy a governance-log template alone. Inspect existing development logs, troubleshooting histories, and run archives first. Use `templates/docs/governance-log.en.md` only when material governance events recur and no existing owner fits. See `docs/logging-guide.md` for triggers, corrections, machine evidence, and privacy.

## 6. Optional Local Verification

Use `docs/verification-guide.md` when the project needs a local governance verification. The Windows transaction runner and live activation are not prerequisites for installing the Skill or adapting templates.

Minimum probes:

- Can a new conversation start from the local entry file?
- Can a source conflict route to the right authority?
- Are old handoff notes treated as evidence instead of active rules?
- Manual activation: do ordinary corrections, drift reports, file conflicts, and writeback discussion stay in normal task handling, while a dedicated command such as `启动分层诊断` opens layered diagnosis?
- Does an ordinary no-change task stay unlogged while a material governance change is recorded exactly once in the correct local owner?
- Does an ordinary no-change task perform zero governance-file reads, writes, and governance-tool calls?
- If the project explicitly enabled the optional transaction runner, does a defined multi-projection transaction use exactly one `apply` without loading Skills, memory, or cold-path governance docs?

Keep wording and verbosity improvements as non-blocking risks only when behavior still passes.

## 7. Keep The Method Small

Only write durable knowledge when it changes future routing, authority, verification, safety, decisions, recurring diagnosis, pattern status, sync status, or release position.
