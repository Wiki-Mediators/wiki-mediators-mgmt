param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CaptureArgs
)

$ErrorActionPreference = "Stop"
$ToolDir = Split-Path -Parent $PSCommandPath
$BundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$Python = if (Test-Path -LiteralPath $BundledPython) {
    $BundledPython
} else {
    (Get-Command python -ErrorAction Stop).Source
}

$env:PYTHONPATH = (Join-Path $ToolDir "vendor")
& $Python (Join-Path $ToolDir "capture_kit.py") @CaptureArgs
exit $LASTEXITCODE
