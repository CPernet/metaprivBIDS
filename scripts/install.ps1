$ErrorActionPreference = 'Stop'

$repositoryRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repositoryRoot

$condaCandidates = @(
    $env:CONDA_EXE,
    (Get-Command conda.exe -ErrorAction SilentlyContinue).Source,
    (Join-Path $env:USERPROFILE 'miniforge3\Scripts\conda.exe'),
    (Join-Path $env:LOCALAPPDATA 'miniforge3\Scripts\conda.exe'),
    (Join-Path $env:USERPROFILE 'mambaforge\Scripts\conda.exe'),
    (Join-Path $env:USERPROFILE 'anaconda3\Scripts\conda.exe'),
    (Join-Path $env:USERPROFILE 'miniconda3\Scripts\conda.exe')
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -Unique

if (-not $condaCandidates) {
    throw 'Conda was not found. Install Miniforge, then run this script again.'
}

$conda = $condaCandidates[0]
Write-Host "Using Conda: $conda"

& $conda run --name metaprivbids python --version *> $null
if ($LASTEXITCODE -eq 0) {
    Write-Host 'Updating the existing metaprivbids environment...'
    & $conda env update --name metaprivbids --file environment.yml
} else {
    Write-Host 'Creating the metaprivbids environment...'
    & $conda env create --file environment.yml
}
if ($LASTEXITCODE -ne 0) { throw 'Conda environment setup failed.' }

& $conda run --name metaprivbids uv pip install -e .
if ($LASTEXITCODE -ne 0) { throw 'Python application installation failed.' }

Write-Host ''
Write-Host 'Installation complete.' -ForegroundColor Green
Write-Host 'Start the GUI with:'
Write-Host "& '$conda' run --name metaprivbids metaprivBIDS-gui"
