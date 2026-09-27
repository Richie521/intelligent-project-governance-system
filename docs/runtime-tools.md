# Optional Windows Runtime Tools

Basic adoption starts with the project-local `AGENTS.md` entry. Organize existing material only when useful, then add the transaction runner only when a project deliberately adopts registered governance projections. Neither the method nor manual diagnosis requires a Hook. A user-issued diagnosis command starts the documented agent process; it does not create a machine-enforced boundary.

The transaction runner is optional and experimental. This guide covers Windows 11; other platforms and long-term host operation have not been accepted. The installer copies files and records their hashes. The runner needs Python 3; `run.ps1` uses `CODEX_PYTHON` when set, otherwise it looks for `python` on `PATH`.

See the [transaction request interface and recovery guide](../tools/governance-transaction/README.en.md) for request fields, operations, receipts, and recovery limits.

Basic adoption has no runtime-tool dependency. Initialize `.codex/governance-runtime.json` from its template only when the project explicitly enables the transaction runner; otherwise do not create it. Once enabled, treat the manifest as read-only during routine work. Some native sandboxes may protect `.codex`; if the host refuses an initial setup or authorized write, report the refusal and complete it through the host's normal authorization flow. Do not bypass host protection.

Keep transaction receipts, journals, and recovery state in the project-local `.governance-state` directory when choosing a state root. Pass the same explicit `--state-root` to `apply`, `recover`, and `benchmark`, so routine machine state does not live under `.codex`:

```powershell
$projectRoot = '<target-project-root>'
$runner = '<installed-transaction-directory>\run.ps1'
$stateRoot = Join-Path $projectRoot '.governance-state'

Get-Content -Raw .\request.json | & $runner --project-root $projectRoot --state-root $stateRoot apply --request-stdin
& $runner --project-root $projectRoot --state-root $stateRoot recover
& $runner --project-root $projectRoot --state-root $stateRoot benchmark
```

## Install And Identify The Version

Keep the downloaded repository: the transaction uninstaller is invoked from its source directory. Back up the existing installation before an upgrade. The installer defaults to `C:\ProgramData\OpenAI\Codex\governance-transaction`; specify `-InstallDir` to use a project-local directory or another location you chose, such as a directory on `G:`:

```powershell
# Project-local
& .\tools\governance-transaction\install.ps1 -InstallDir '<project-root>\.governance-tools\transaction'

# Or an explicitly selected directory on G:
& .\tools\governance-transaction\install.ps1 -InstallDir 'G:\CodexTools\governance-transaction'
```

The transaction installer accepts `-InstallDir`. It does not require a Codex restart. Compare installed files against `release-manifest.json` with SHA-256; the installer writes `installation.json`. Validate a deliberately adapted project manifest using the installed runner:

```powershell
& '<installed-transaction-directory>\run.ps1' --project-root '<project-root>' validate-manifest
```

If Python is not on `PATH`, set `$env:CODEX_PYTHON` to the absolute path of a Python 3 executable before calling `run.ps1`. An unchanged project must not invoke transactions merely to generate governance activity.

## Hook-Based Activation Guard Status

The activation guard and Hook integration are retained as historical source, but installation and host activation are unsupported in this release. Do not use the old installer instructions as current setup guidance. The manual diagnosis path is an explicit user command followed by the documented agent process; artifacts can show what was done, but this path does not guarantee machine enforcement. No Hook is needed for basic adoption or manual diagnosis.

## Restore Or Uninstall The Transaction Runner

Run the transaction uninstaller from the downloaded repository and point it to the chosen installation directory:

```powershell
& .\tools\governance-transaction\uninstall.ps1 -InstallDir '<installed-transaction-directory>'
```

Uninstall verifies managed hashes and preserves unrelated files. If a managed file was edited after installation, stop and reconcile it with the retained backup; do not force-delete the directory. To return to a previous installed version, restore your pre-upgrade backup after checking for subsequent local edits.

## Concurrency And Manual Diagnosis

Windows transaction replacement retains and checks the displaced version. An external-edit conflict fails with recovery paths rather than claiming success. The target may already contain proposed bytes when the conflict is detected; multi-file readers do not get an atomic snapshot. Unknown replacement or incomplete rollback reports an uncertain write count. Preserve the target, journal, temporary file and conflict backup until their content has been reconciled. Do not blindly retry or automatically restore over a later edit.

Only a dedicated user command activates layered diagnosis. Ordinary corrections do not activate it. Repair scope is an agent-followed agreement verified through artifacts, not a general command sandbox or machine-enforced boundary. Isolated lifecycle and tool-argument tests do not prove live host activation, restart loading, or compaction recovery.
