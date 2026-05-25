$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot

if (!(Test-Path -LiteralPath ".env")) {
    Copy-Item -LiteralPath ".env.example" -Destination ".env"
}

docker compose up -d mysql redis
$python = ".\.venv\Scripts\python.exe"

if (Test-Path -LiteralPath $python) {
    & $python -m uvicorn app.main:app --app-dir backend --reload
} else {
    py -3.12 -m uvicorn app.main:app --app-dir backend --reload
}
