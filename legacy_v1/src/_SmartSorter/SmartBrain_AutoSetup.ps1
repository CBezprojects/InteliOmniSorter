$ErrorActionPreference = "Stop"

# === PATHS ===
$RootPath    = "C:\Users\27646\OneDrive\Master_Cloud"
$SmartDir    = Join-Path $RootPath "_SmartSorter"
$LogDir      = Join-Path $RootPath "_SortLogs"
$ErrorLog    = Join-Path $LogDir "smartbrain_setup_errors.log"
$Venv311     = Join-Path $SmartDir ".venv311"
$FinalVenv   = Join-Path $SmartDir ".venv"
$BrainPy     = Join-Path $SmartDir "smartbrain.py"

# Ensure folders exist
if (-not (Test-Path $SmartDir)) { New-Item -ItemType Directory -Path $SmartDir | Out-Null }
if (-not (Test-Path $LogDir))   { New-Item -ItemType Directory -Path $LogDir | Out-Null }

function LogError($msg) {
    $ts = (Get-Date).ToString("s")
    "$ts `t $msg" | Out-File -Append -FilePath $ErrorLog -Encoding UTF8
}

Write-Host "`n=== SMARTBRAIN AUTO-INSTALLER STARTED ===`n" -ForegroundColor Cyan

# === STEP 1: Install Python 3.11 if missing ===
Write-Host "Checking Python 3.11..." -ForegroundColor Cyan
try {
    py -3.11 --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Python 3.11 not found. Installing..." -ForegroundColor Yellow
        winget install Python.Python.3.11 --silent
    } else {
        Write-Host "Python 3.11 already installed." -ForegroundColor Green
    }
} catch {
    LogError "PY311_CHECK_FAIL: $_"
}

# === STEP 2: Create venv311 ===
Write-Host "Creating Python 3.11 venv..." -ForegroundColor Cyan
try {
    py -3.11 -m venv $Venv311
} catch {
    LogError "VENV311_CREATE_FAIL: $_"
    exit 1
}

$PythonExe = Join-Path $Venv311 "Scripts\python.exe"
$PipExe    = Join-Path $Venv311 "Scripts\pip.exe"

if (-not (Test-Path $PythonExe)) {
    Write-Host "ERROR: Python 3.11 venv did not create properly." -ForegroundColor Red
    LogError "VENV311_PYTHON_MISSING"
    exit 1
}

Write-Host "Python 3.11 venv created.`n" -ForegroundColor Green

# === STEP 3: Install required packages ===
Write-Host "Installing base Python dependencies..." -ForegroundColor Cyan
try {
    & $PipExe install --upgrade pip
    & $PipExe install pillow tqdm imagehash PyPDF2 packaging pytesseract
} catch {
    LogError "BASE_PIP_INSTALL_FAIL: $_"
}

# === STEP 4: Install CMake ===
Write-Host "Checking CMake installation..." -ForegroundColor Cyan
try {
    cmake --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "CMake not found. Installing..." -ForegroundColor Yellow
        winget install Kitware.CMake --silent
    } else {
        Write-Host "CMake already installed." -ForegroundColor Green
    }
} catch {
    LogError "CMAKE_CHECK_FAIL: $_"
}

Start-Sleep -Seconds 2

# === STEP 5: Download dlib wheel automatically ===
Write-Host "Downloading prebuilt dlib wheel for Python 3.11..." -ForegroundColor Cyan

$dlibUrl = "https://download.lfd.uci.edu/pythonlibs/r2tscw2k/dlib-19.24.2-cp311-cp311-win_amd64.whl"
$dlibWheel = Join-Path $SmartDir "dlib311.whl"

try {
    Invoke-WebRequest -Uri $dlibUrl -OutFile $dlibWheel -UseBasicParsing
    Write-Host "dlib wheel downloaded." -ForegroundColor Green
} catch {
    LogError "DLIB_WHEEL_DOWNLOAD_FAIL: $_"
    Write-Host "FAILED to download dlib wheel. Check log file." -ForegroundColor Red
    exit 1
}

# === STEP 6: Install dlib ===
Write-Host "Installing dlib..." -ForegroundColor Cyan
try {
    & $PipExe install $dlibWheel
    Write-Host "dlib installed successfully." -ForegroundColor Green
} catch {
    LogError "DLIB_INSTALL_FAIL: $_"
    Write-Host "FAILED to install dlib." -ForegroundColor Red
    exit 1
}

# === STEP 7: Install face_recognition ===
Write-Host "Installing face_recognition..." -ForegroundColor Cyan
try {
    & $PipExe install face-recognition
    & $PipExe install face-recognition-models
    Write-Host "face_recognition installed successfully." -ForegroundColor Green
} catch {
    LogError "FACE_RECOGNITION_INSTALL_FAIL: $_"
}

# === STEP 8: Replace old .venv with .venv311 ===
Write-Host "Replacing old .venv with .venv311..." -ForegroundColor Cyan
try {
    if (Test-Path $FinalVenv) {
        Rename-Item $FinalVenv "$FinalVenv.old" -Force
    }
    Rename-Item $Venv311 $FinalVenv -Force
    Write-Host "Python 3.11 SmartBrain environment is now active." -ForegroundColor Green
} catch {
    LogError "VENV_SWITCH_FAIL: $_"
}

# === STEP 9: Detect external tools (PS5-compatible method) ===
Write-Host "Detecting external tools..." -ForegroundColor Cyan

function SafeGetCommand($cmd) {
    try {
        $c = Get-Command $cmd -ErrorAction SilentlyContinue
        if ($c) { return $c.Source }
        else { return "" }
    } catch { return "" }
}

$ExifToolPath = SafeGetCommand "exiftool"
$FfprobePath  = SafeGetCommand "ffprobe"
$TessPath     = SafeGetCommand "tesseract"

if ($ExifToolPath -ne "") { Write-Host "ExifTool found: $ExifToolPath" -ForegroundColor Green }
else { Write-Host "ExifTool NOT found" -ForegroundColor Yellow; LogError "EXIFTOOL_NOT_FOUND" }

if ($FfprobePath -ne "") { Write-Host "ffprobe found: $FfprobePath" -ForegroundColor Green }
else { Write-Host "ffprobe NOT found" -ForegroundColor Yellow; LogError "FFPROBE_NOT_FOUND" }

if ($TessPath -ne "") { Write-Host "Tesseract found: $TessPath" -ForegroundColor Green }
else { Write-Host "Tesseract NOT found" -ForegroundColor Yellow; LogError "TESSERACT_NOT_FOUND" }

# === STEP 10: Run SmartBrain ===
if (Test-Path $BrainPy) {
    Write-Host "`nLaunching SmartBrain..." -ForegroundColor Cyan
    & "$FinalVenv\Scripts\python.exe" $BrainPy --root "$RootPath"
} else {
    Write-Host "smartbrain.py does not exist. Cannot launch." -ForegroundColor Red
}

Write-Host "`n=== SMARTBRAIN SETUP COMPLETE ===" -ForegroundColor Cyan
