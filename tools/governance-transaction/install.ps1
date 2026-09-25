param(
    [string]$InstallDir = 'C:\ProgramData\OpenAI\Codex\governance-transaction'
)

$ErrorActionPreference = 'Stop'
Import-Module Microsoft.PowerShell.Utility -ErrorAction Stop
$Source = $PSScriptRoot
$Files = @('cli.py', 'governance_transaction.py', 'run.ps1')
$ResolvedInstall = [System.IO.Path]::GetFullPath($InstallDir)
New-Item -ItemType Directory -Force -Path $ResolvedInstall | Out-Null

foreach ($File in $Files) {
    Copy-Item -LiteralPath (Join-Path $Source $File) -Destination (Join-Path $ResolvedInstall $File) -Force
}

$Hashes = foreach ($File in $Files) {
    $Installed = Join-Path $ResolvedInstall $File
    [ordered]@{
        file = $File
        sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $Installed).Hash.ToLowerInvariant()
    }
}
$Record = [ordered]@{
    schema_version = 1
    installed_at = [DateTimeOffset]::Now.ToString('o')
    install_dir = $ResolvedInstall
    files = $Hashes
}
$Record | ConvertTo-Json -Depth 4 | Set-Content -Encoding utf8 -LiteralPath (Join-Path $ResolvedInstall 'installation.json')

[ordered]@{
    status = 'installed'
    install_dir = $ResolvedInstall
    restart_required = $false
    files = $Hashes
} | ConvertTo-Json -Depth 4
