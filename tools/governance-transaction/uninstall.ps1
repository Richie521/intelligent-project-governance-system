param(
    [string]$InstallDir = 'C:\ProgramData\OpenAI\Codex\governance-transaction'
)

$ErrorActionPreference = 'Stop'
Import-Module Microsoft.PowerShell.Utility -ErrorAction Stop
$ResolvedInstall = [System.IO.Path]::GetFullPath($InstallDir)
$recordPath = Join-Path $ResolvedInstall 'installation.json'
if (-not (Test-Path -LiteralPath $recordPath -PathType Leaf)) {
    throw "GOV-TX-UNINSTALL-001 missing installation record: $recordPath"
}
$record = Get-Content -Raw -Encoding utf8 -LiteralPath $recordPath | ConvertFrom-Json
if ([IO.Path]::GetFullPath([string]$record.install_dir) -ne $ResolvedInstall) {
    throw 'GOV-TX-UNINSTALL-002 installation path does not match its record'
}
$parent = [IO.Path]::GetFullPath((Split-Path -Parent $ResolvedInstall))
if ($ResolvedInstall -eq [IO.Path]::GetPathRoot($ResolvedInstall) -or
    -not $ResolvedInstall.StartsWith($parent + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw "GOV-TX-UNINSTALL-003 unsafe install directory: $ResolvedInstall"
}

$allowed = @('cli.py', 'governance_transaction.py', 'run.ps1')
$managedPaths = @()
$seen = @{}
foreach ($entry in @($record.files)) {
    $name = [string]$entry.file
    if ($name -notin $allowed -or $name -match '[\\/:]' -or
        [string]$entry.sha256 -notmatch '^[0-9a-fA-F]{64}$') {
        throw "GOV-TX-UNINSTALL-004 invalid managed-file record: $name"
    }
    if ($seen.ContainsKey($name)) { throw "GOV-TX-UNINSTALL-004 duplicate managed-file record: $name" }
    $seen[$name] = $true
    $path = Join-Path $ResolvedInstall $name
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash
        if ($actual -ine [string]$entry.sha256) {
            throw "GOV-TX-UNINSTALL-005 modified managed file preserved: $path"
        }
        $managedPaths += $path
    }
}
if (@($allowed | Where-Object { -not $seen.ContainsKey($_) }).Count -gt 0) {
    throw 'GOV-TX-UNINSTALL-004 incomplete managed-file record'
}
foreach ($path in $managedPaths) { Remove-Item -LiteralPath $path -Force }

Remove-Item -LiteralPath $recordPath -Force
if ((Get-ChildItem -LiteralPath $ResolvedInstall -Force | Measure-Object).Count -eq 0) {
    Remove-Item -LiteralPath $ResolvedInstall -Force
}
[ordered]@{ status = 'uninstalled'; install_dir = $ResolvedInstall; restart_required = $false } |
    ConvertTo-Json
