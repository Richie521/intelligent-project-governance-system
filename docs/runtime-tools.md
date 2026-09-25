# Optional Windows Runtime Tools

The method and Skill can be used without these tools. The transaction runner handles registered governance projections; the activation guard is an experimental host integration. Measured platform: Windows 11, Python 3.14.2. The guard installer requires Python 3.11+ and PowerShell. Other platforms and long-term host operation have not been accepted.

## Install And Identify The Version

Keep the downloaded repository: the transaction uninstaller is invoked from its source directory. Back up the existing installation and requirements file before an upgrade. Run from the repository root, using a Python executable that exists on your machine:

```powershell
& .\tools\governance-transaction\install.ps1
# Only if you explicitly want the experimental host guard:
& .\tools\governance-activation-guard\install.ps1 -PythonPath '<absolute-python-path>'
```

Both installers accept `-InstallDir`; the guard also accepts `-RequirementsPath`. Defaults are the Codex ProgramData managed locations. The guard requires Python and installation paths without whitespace. The transaction tool needs no restart; the guard requires a new Codex host process to load its configuration. Updating files does not prove a currently running Desktop process has reloaded hooks.

Compare installed files against `release-manifest.json` with SHA-256. The transaction writes `installation.json`; the guard writes `install-record.json`, including the requirements hash and backup path. Validate a deliberately adapted project manifest with the installed `cli.py --project-root <project-root> validate-manifest` using Python. An unchanged project must not invoke transactions merely to generate governance activity.

## Restore Or Uninstall

```powershell
& .\tools\governance-transaction\uninstall.ps1 -InstallDir '<installed-transaction-directory>'
& .\tools\governance-activation-guard\uninstall.ps1 -InstallDir '<installed-guard-directory>' -RequirementsPath '<requirements.toml-path>'
```

Uninstall verifies managed hashes and preserves unrelated files. If a managed file or requirements configuration was edited after installation, stop and reconcile it with the retained backup; do not force-delete the directory. The guard refuses an ambiguous merge with existing features/hooks tables. An unchanged new installation can restore the exact original requirements bytes. A legacy installation without an original backup can preserve only the currently observable unmanaged remainder, recorded as `legacy_unmanaged_remainder_only`. It cannot recover configuration an older installer already destroyed. To return to a previous installed version, restore your pre-upgrade backup after checking for subsequent local edits.

## Concurrency And Manual Diagnosis

Windows transaction replacement retains and checks the displaced version. An external-edit conflict fails with recovery paths rather than claiming success. The target may already contain proposed bytes when the conflict is detected; multi-file readers do not get an atomic snapshot. Unknown replacement or incomplete rollback reports an uncertain write count. Preserve the target, journal, temporary file and conflict backup until their content has been reconciled. Do not blindly retry or automatically restore over a later edit.

Only a dedicated manual command activates layered diagnosis. Ordinary corrections do not activate it. Repair scope is an agent-followed agreement verified through artifacts, not a general command sandbox. Isolated lifecycle and tool-argument tests do not prove live host activation, restart loading, or compaction recovery. Keep the guard experimental until those host paths are separately verified.
