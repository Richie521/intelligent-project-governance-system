[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding

function Write-FailClosedResult {
    param(
        [AllowNull()]
        [object]$Event,
        [string]$Reason
    )

    $eventName = if ($Event) { [string]$Event.hook_event_name } else { '' }
    if ($eventName -eq 'PreToolUse') {
        $result = @{
            hookSpecificOutput = @{
                hookEventName = 'PreToolUse'
                permissionDecision = 'deny'
                permissionDecisionReason = $Reason
            }
        }
    }
    elseif ($eventName -eq 'SessionStart' -or $eventName -eq 'PostCompact') {
        $result = @{
            continue = $false
            stopReason = $Reason
            systemMessage = $Reason
        }
    }
    else {
        $result = @{
            decision = 'block'
            reason = $Reason
        }
    }

    [Console]::Out.WriteLine(($result | ConvertTo-Json -Depth 8 -Compress))
}

$rawInput = [Console]::In.ReadToEnd()
$event = $null
try {
    $event = $rawInput | ConvertFrom-Json
}
catch {
    Write-FailClosedResult -Event $null -Reason "GOV-GATE-001 $PSScriptRoot\uninstall.ps1"
    exit 0
}

$python = if ($env:GOVERNANCE_GUARD_PYTHON) {
    $env:GOVERNANCE_GUARD_PYTHON
}
else {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) { $pythonCommand.Source } else { $null }
}

$entrypoint = Join-Path $PSScriptRoot 'hook_entry.py'
if (-not $python -or -not (Test-Path -LiteralPath $python) -or -not (Test-Path -LiteralPath $entrypoint)) {
    Write-FailClosedResult -Event $event -Reason "GOV-GATE-002 $PSScriptRoot\uninstall.ps1"
    exit 0
}

try {
    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $python
    $startInfo.Arguments = '"' + ($entrypoint -replace '"', '\"') + '"'
    $startInfo.UseShellExecute = $false
    $startInfo.RedirectStandardInput = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.CreateNoWindow = $true
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    [void]$process.Start()
    $process.StandardInput.Write($rawInput)
    $process.StandardInput.Close()
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()

    if ($process.ExitCode -ne 0) {
        $detail = if ($stderr) { $stderr.Trim() } else { [string]$process.ExitCode }
        Write-FailClosedResult -Event $event -Reason "GOV-GATE-003 $detail $PSScriptRoot\uninstall.ps1"
        exit 0
    }

    if ($stdout) {
        try {
            $null = $stdout | ConvertFrom-Json
        }
        catch {
            Write-FailClosedResult -Event $event -Reason "GOV-GATE-004 $PSScriptRoot\uninstall.ps1"
            exit 0
        }
        [Console]::Out.Write($stdout)
    }
    exit 0
}
catch {
    Write-FailClosedResult -Event $event -Reason "GOV-GATE-005 $($_.Exception.Message) $PSScriptRoot\uninstall.ps1"
    exit 0
}
