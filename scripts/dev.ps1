param(
    [switch]$RunTestsOnly,
    [switch]$RunApiOnly
)

if (-not $RunApiOnly) {
    python -m pytest -q
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

if (-not $RunTestsOnly) {
    python -m uvicorn backend.app.main:app --reload
}
