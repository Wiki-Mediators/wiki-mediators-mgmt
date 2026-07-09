param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$SearchArgs
)

$ErrorActionPreference = "Stop"

$ToolDir = Split-Path -Parent $PSCommandPath
$VaultRoot = Resolve-Path (Join-Path $ToolDir "..\..")
$ScriptPath = Join-Path $ToolDir "vault_search.py"

$PythonCandidates = @(
    (Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe")
)

$Python = $null
foreach ($Candidate in $PythonCandidates) {
    if ($Candidate -and (Test-Path -LiteralPath $Candidate)) {
        $Python = $Candidate
        break
    }
}

if (-not $Python) {
    $Command = Get-Command python -ErrorAction SilentlyContinue
    if ($Command) {
        $Python = $Command.Source
    }
}

if (-not $Python) {
    $Command = Get-Command py -ErrorAction SilentlyContinue
    if ($Command) {
        $Python = $Command.Source
    }
}

if (-not $Python) {
    Write-Error "No Python runtime found. Expected bundled runtime under $env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe."
    exit 1
}

Push-Location $VaultRoot
try {
    & $Python $ScriptPath @SearchArgs
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
