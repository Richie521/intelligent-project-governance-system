[CmdletBinding()]
param(
    [string]$InstallDir = 'C:\ProgramData\OpenAI\Codex\governance-activation-guard',
    [string]$RequirementsPath = 'C:\ProgramData\OpenAI\Codex\requirements.toml'
)

$ErrorActionPreference = 'Stop'
Import-Module Microsoft.PowerShell.Utility -ErrorAction Stop
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding

$recordPath = Join-Path $InstallDir 'install-record.json'
$resolved = [IO.Path]::GetFullPath($InstallDir)
if (-not (Test-Path -LiteralPath $recordPath -PathType Leaf)) {
    throw "GOV-GATE-UNINSTALL-001 missing install record: $recordPath"
}
$record = Get-Content -Raw -Encoding utf8 -LiteralPath $recordPath | ConvertFrom-Json
if ([IO.Path]::GetFullPath([string]$record.install_dir) -ne $resolved) {
    throw 'GOV-GATE-UNINSTALL-002 install path does not match its record'
}
$parent = [IO.Path]::GetFullPath((Split-Path -Parent $resolved))
if ($resolved -eq [IO.Path]::GetPathRoot($resolved) -or
    -not $resolved.StartsWith($parent + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw "GOV-GATE-UNINSTALL-003 unsafe install directory: $resolved"
}

$allowed = @('governance_guard.py', 'hook_entry.py', 'receipt_entry.py', 'run-hook.ps1', 'uninstall.ps1')
$managed = @()
foreach ($entry in @($record.files)) {
    $recordedPath = [string]$entry.path
    $name = [IO.Path]::GetFileName($recordedPath)
    if ($name -notin $allowed -or
        [string]$entry.sha256 -notmatch '^[0-9a-fA-F]{64}$') {
        throw "GOV-GATE-UNINSTALL-004 invalid managed-file record: $name"
    }
    $path = Join-Path $resolved $name
    if ([IO.Path]::GetFullPath([string]$entry.path) -ne [IO.Path]::GetFullPath($path)) {
        throw "GOV-GATE-UNINSTALL-004 managed-file path escaped install directory: $name"
    }
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash
        if ($actual -ine [string]$entry.sha256) {
            throw "GOV-GATE-UNINSTALL-005 modified managed file preserved: $path"
        }
        $managed += $path
    }
}

$requirementsExists = Test-Path -LiteralPath $RequirementsPath -PathType Leaf
if ($requirementsExists) {
    $currentHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $RequirementsPath).Hash.ToLowerInvariant()
    if ($currentHash -ne [string]$record.requirements_sha256) {
        throw 'GOV-GATE-UNINSTALL-006 requirements.toml was changed after install; preserving it and the original backup'
    }
    if ([bool]$record.original_requirements_existed) {
        $backup = [string]$record.backup_path
        if (-not $backup -or -not (Test-Path -LiteralPath $backup -PathType Leaf) -or
            (Get-FileHash -Algorithm SHA256 -LiteralPath $backup).Hash -ine [string]$record.requirements_backup_sha256) {
            throw 'GOV-GATE-UNINSTALL-007 original requirements backup is missing or changed'
        }
        $temporary = "$RequirementsPath.governance-restore.$([guid]::NewGuid().ToString('N')).tmp"
        $captured = "$RequirementsPath.governance-restore.$([guid]::NewGuid().ToString('N')).conflict"
        Copy-Item -LiteralPath $backup -Destination $temporary
        [IO.File]::Replace($temporary, $RequirementsPath, $captured, $true)
        if ((Get-FileHash -Algorithm SHA256 -LiteralPath $captured).Hash -ine $currentHash) {
            throw "GOV-GATE-UNINSTALL-008 concurrent requirements version preserved at $captured"
        }
        Remove-Item -LiteralPath $captured -Force
        Remove-Item -LiteralPath $backup -Force
    }
    else {
        $captured = "$RequirementsPath.governance-uninstall.$([guid]::NewGuid().ToString('N')).conflict"
        [IO.File]::Move($RequirementsPath, $captured)
        if ((Get-FileHash -Algorithm SHA256 -LiteralPath $captured).Hash -ne $currentHash) {
            throw "GOV-GATE-UNINSTALL-009 concurrent requirements version preserved at $captured"
        }
        Remove-Item -LiteralPath $captured -Force
        if ($record.backup_path -and (Test-Path -LiteralPath $record.backup_path -PathType Leaf)) {
            if ((Get-FileHash -Algorithm SHA256 -LiteralPath $record.backup_path).Hash -ine [string]$record.requirements_backup_sha256) {
                throw 'GOV-GATE-UNINSTALL-010 legacy requirements remainder backup changed'
            }
            Remove-Item -LiteralPath $record.backup_path -Force
        }
    }
}

foreach ($path in $managed) { Remove-Item -LiteralPath $path -Force }
Remove-Item -LiteralPath $recordPath -Force
if ((Get-ChildItem -LiteralPath $resolved -Force | Measure-Object).Count -eq 0) {
    Remove-Item -LiteralPath $resolved -Force
}

Write-Output 'GOV-GATE-UNINSTALLED-RESTART-REQUIRED'
