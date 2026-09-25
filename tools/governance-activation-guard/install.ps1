[CmdletBinding()]
param(
    [string]$InstallDir = 'C:\ProgramData\OpenAI\Codex\governance-activation-guard',
    [string]$RequirementsPath = 'C:\ProgramData\OpenAI\Codex\requirements.toml',
    [string]$PythonPath = ''
)

$ErrorActionPreference = 'Stop'
Import-Module Microsoft.PowerShell.Utility -ErrorAction Stop
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding

$sourceDir = $PSScriptRoot
if (-not $PythonPath) {
    if ($env:GOVERNANCE_GUARD_PYTHON) {
        $PythonPath = $env:GOVERNANCE_GUARD_PYTHON
    }
    else {
        $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
        if ($pythonCommand) {
            $PythonPath = $pythonCommand.Source
        }
    }
}
if (-not $PythonPath -or -not (Test-Path -LiteralPath $PythonPath)) {
    throw 'GOV-GATE-INSTALL-000 Python 3 executable not found'
}
$PythonPath = [System.IO.Path]::GetFullPath($PythonPath)
$InstallDir = [System.IO.Path]::GetFullPath($InstallDir)
if ($PythonPath -match '\s' -or $InstallDir -match '\s') {
    throw 'GOV-GATE-INSTALL-004 PythonPath and InstallDir must not contain whitespace'
}

$requiredFiles = @(
    'governance_guard.py',
    'hook_entry.py',
    'receipt_entry.py',
    'run-hook.ps1',
    'uninstall.ps1'
)
foreach ($name in $requiredFiles) {
    $sourcePath = Join-Path $sourceDir $name
    if (-not (Test-Path -LiteralPath $sourcePath)) {
        throw "GOV-GATE-INSTALL-001 $sourcePath"
    }
}

$requirementsDir = Split-Path -Parent $RequirementsPath
$backupPath = $null
$priorRecordPath = Join-Path $InstallDir 'install-record.json'
$priorRecord = $null
if (Test-Path -LiteralPath $priorRecordPath) {
    $priorRecord = Get-Content -Raw -Encoding utf8 -LiteralPath $priorRecordPath | ConvertFrom-Json
    if ($priorRecord.backup_path) {
        $backupPath = [string]$priorRecord.backup_path
    }
}
$template = Get-Content -Raw -Encoding utf8 -LiteralPath (Join-Path $sourceDir 'requirements.toml.template')
$tomlInstallDir = $InstallDir -replace "'", "''"
$tomlPythonPath = $PythonPath -replace "'", "''"
$rendered = $template.Replace('__INSTALL_DIR__', $tomlInstallDir).Replace('__PYTHON_EXE__', $tomlPythonPath).TrimEnd("`r", "`n")
$existing = if (Test-Path -LiteralPath $RequirementsPath -PathType Leaf) { [IO.File]::ReadAllText($RequirementsPath, [Text.Encoding]::UTF8) } else { '' }
$originalExists = [bool](Test-Path -LiteralPath $RequirementsPath -PathType Leaf)
$markerPattern = '(?ms)^# BEGIN managed governance activation guard\r?\n.*?^# END managed governance activation guard\r?\n?'
$currentHash = if ($originalExists) { (Get-FileHash -Algorithm SHA256 -LiteralPath $RequirementsPath).Hash.ToLowerInvariant() } else { $null }

if ($existing -match 'BEGIN managed governance activation guard') {
    if (-not $priorRecord -or -not $priorRecord.requirements_sha256 -or $currentHash -ne [string]$priorRecord.requirements_sha256) {
        throw 'GOV-GATE-INSTALL-002 existing managed block is unowned or was modified; preserving requirements.toml'
    }
    if ($existing -notmatch $markerPattern -or [regex]::Matches($existing, '# BEGIN managed governance activation guard').Count -ne 1) {
        throw 'GOV-GATE-INSTALL-003 managed block markers are malformed'
    }
    $prefix = [regex]::Replace($existing, $markerPattern, '')
    if ($backupPath) {
        if (-not (Test-Path -LiteralPath $backupPath -PathType Leaf) -or
            (Get-FileHash -Algorithm SHA256 -LiteralPath $backupPath).Hash -ine [string]$priorRecord.requirements_backup_sha256) {
            throw 'GOV-GATE-INSTALL-004 original requirements backup is missing or changed'
        }
        $originalExists = [bool]$priorRecord.original_requirements_existed
        $recoveryKind = [string]$priorRecord.requirements_recovery
    }
    else {
        # Legacy releases replaced the whole file and stored no pre-install backup.
        # Preserve only the exact unmanaged remainder that exists now; do not
        # claim that it represents the configuration from before that release.
        $backupPath = "$RequirementsPath.legacy-remainder.$([guid]::NewGuid().ToString('N')).bak"
        [IO.File]::WriteAllText($backupPath, $prefix, [Text.UTF8Encoding]::new($false))
        $originalExists = ($prefix.Length -gt 0)
        $recoveryKind = 'legacy_unmanaged_remainder_only'
    }
}
else {
    if ($priorRecord -and $priorRecord.backup_path) {
        throw 'GOV-GATE-INSTALL-005 installed managed block is missing; preserving requirements.toml'
    }
    if ($existing -match '(?m)^\s*\[{1,2}(?:features|hooks)(?:\s*\]|\.)') {
        throw 'GOV-GATE-INSTALL-006 requirements.toml already defines [features] or [hooks]; refusing an ambiguous TOML merge'
    }
    $prefix = $existing
    if ($originalExists) {
        $backupPath = "$RequirementsPath.governance-activation-guard.$([guid]::NewGuid().ToString('N')).bak"
        Copy-Item -LiteralPath $RequirementsPath -Destination $backupPath
    }
    $recoveryKind = 'original_file_backup'
}

$candidate = if ($prefix.Length -gt 0) { $prefix.TrimEnd("`r", "`n") + "`n" + $rendered + "`n" } else { $rendered + "`n" }
$candidatePath = Join-Path $env:TEMP "governance-guard-requirements-$([guid]::NewGuid().ToString('N')).toml"
[IO.File]::WriteAllText($candidatePath, $candidate, [Text.UTF8Encoding]::new($false))
try {
    & $PythonPath -c "import pathlib,sys,tomllib; tomllib.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8-sig'))" $candidatePath
    if ($LASTEXITCODE -ne 0) { throw 'GOV-GATE-INSTALL-007 merged requirements TOML is invalid' }
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
    New-Item -ItemType Directory -Force -Path $requirementsDir | Out-Null
    foreach ($name in $requiredFiles) {
        Copy-Item -LiteralPath (Join-Path $sourceDir $name) -Destination (Join-Path $InstallDir $name) -Force
    }
    if ($originalExists -or (Test-Path -LiteralPath $RequirementsPath)) {
        $writeBackup = "$RequirementsPath.governance-write.$([guid]::NewGuid().ToString('N')).bak"
        $temporaryPath = "$RequirementsPath.governance-write.$([guid]::NewGuid().ToString('N')).tmp"
        [IO.File]::WriteAllBytes($temporaryPath, [IO.File]::ReadAllBytes($candidatePath))
        [IO.File]::Replace($temporaryPath, $RequirementsPath, $writeBackup, $true)
        if ((Get-FileHash -Algorithm SHA256 -LiteralPath $writeBackup).Hash -ine $currentHash) {
            throw "GOV-GATE-INSTALL-008 requirements.toml changed during install; recoverable copy: $writeBackup"
        }
        Remove-Item -LiteralPath $writeBackup -Force
        Remove-Item -LiteralPath $temporaryPath -Force -ErrorAction SilentlyContinue
    }
    else {
        [IO.File]::Move($candidatePath, $RequirementsPath)
    }
}
finally {
    Remove-Item -LiteralPath $candidatePath -Force -ErrorAction SilentlyContinue
}

$installedFiles = $requiredFiles | ForEach-Object {
    $path = Join-Path $InstallDir $_
    [ordered]@{
        path = $path
        sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant()
    }
}
$record = [ordered]@{
    schema_version = 1
    installed_at = (Get-Date).ToString('o')
    source_dir = $sourceDir
    install_dir = $InstallDir
    requirements_path = $RequirementsPath
    requirements_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $RequirementsPath).Hash.ToLowerInvariant()
    original_requirements_existed = $originalExists
    requirements_recovery = $recoveryKind
    requirements_backup_sha256 = if ($backupPath -and (Test-Path -LiteralPath $backupPath)) { (Get-FileHash -Algorithm SHA256 -LiteralPath $backupPath).Hash.ToLowerInvariant() } else { $null }
    python_path = $PythonPath
    python_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $PythonPath).Hash.ToLowerInvariant()
    backup_path = $backupPath
    files = $installedFiles
}
$record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $InstallDir 'install-record.json') -Encoding utf8

Write-Output "GOV-GATE-INSTALLED $InstallDir"
Write-Output 'GOV-GATE-RESTART-REQUIRED'
