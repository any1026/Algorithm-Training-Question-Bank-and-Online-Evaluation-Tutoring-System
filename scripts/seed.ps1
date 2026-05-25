$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$env:PYTHONPATH = Join-Path $projectRoot "backend"
Set-Location -LiteralPath $projectRoot

if (!(Test-Path -LiteralPath ".env")) {
    Copy-Item -LiteralPath ".env.example" -Destination ".env"
}

if (Test-Path -LiteralPath $python) {
    & $python -m app.seed
} else {
    py -3.12 -m app.seed
}
