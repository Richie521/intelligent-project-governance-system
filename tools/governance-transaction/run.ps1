$ErrorActionPreference = 'Stop'
[Console]::InputEncoding = [Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding

$Python = $env:CODEX_PYTHON
if (-not $Python) {
    $Command = Get-Command python -ErrorAction SilentlyContinue
    if (-not $Command) {
        throw 'Python 3 is required. Set CODEX_PYTHON to the Python executable path.'
    }
    $Python = $Command.Source
}

$Entrypoint = Join-Path $PSScriptRoot 'cli.py'
$QuotedArguments = @($Entrypoint) + $args | ForEach-Object {
    '"' + ([string]$_ -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1') + '"'
}
$StartInfo = [Diagnostics.ProcessStartInfo]::new()
$StartInfo.FileName = $Python
$StartInfo.Arguments = $QuotedArguments -join ' '
$StartInfo.UseShellExecute = $false
$StartInfo.RedirectStandardInput = $true
$StartInfo.RedirectStandardOutput = $true
$StartInfo.RedirectStandardError = $true
$StartInfo.CreateNoWindow = $true

$Process = [Diagnostics.Process]::new()
$Process.StartInfo = $StartInfo
[void]$Process.Start()

$PipelineParts = @($input)
$RawInput = if ($PipelineParts.Count) {
    $PipelineParts -join [Environment]::NewLine
}
else {
    [Console]::In.ReadToEnd()
}
if ($RawInput) {
    $Process.StandardInput.Write($RawInput)
}
$Process.StandardInput.Close()
$Stdout = $Process.StandardOutput.ReadToEnd()
$Stderr = $Process.StandardError.ReadToEnd()
$Process.WaitForExit()

if ($Stdout) {
    [Console]::Out.Write($Stdout)
}
if ($Stderr) {
    [Console]::Error.Write($Stderr)
}
exit $Process.ExitCode
