param(
    [string]$RootPath = "C:\Users\27646\OneDrive\Master_Cloud"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $RootPath)) {
    Write-Host "RootPath not found: $RootPath" -ForegroundColor Red
    exit 1
}

$smartDir = Join-Path $RootPath "_SmartSorter"
$venvDir  = Join-Path $smartDir ".venv"
$pythonExe = Join-Path $venvDir "Scripts\python.exe"
$sorterPy = Join-Path $smartDir "sorter.py"

if (-not (Test-Path $smartDir)) {
    New-Item -ItemType Directory -Path $smartDir | Out-Null
}

# 1) Ensure Python venv exists
if (-not (Test-Path $venvDir)) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    # If 'py' doesn't work on this machine, change to 'python'
    py -3 -m venv $venvDir
}

if (-not (Test-Path $pythonExe)) {
    Write-Host "Python executable not found in venv. Something went wrong." -ForegroundColor Red
    exit 1
}

# 2) Ensure required packages are installed
Write-Host "Checking/Installing Python packages..." -ForegroundColor Cyan

& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install pillow imagehash PyPDF2

# 3) Ensure sorter.py exists
if (-not (Test-Path $sorterPy)) {
    Write-Host "ERROR: sorter.py not found at $sorterPy" -ForegroundColor Red
    Write-Host "Please save the Python script as sorter.py in _SmartSorter." -ForegroundColor Yellow
    exit 1
}

# 4) Run sorter
Write-Host "Running smart sorter..." -ForegroundColor Green
& $pythonExe $sorterPy --root "$RootPath"
