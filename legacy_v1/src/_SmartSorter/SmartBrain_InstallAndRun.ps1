param(
    [string]$RootPath = "C:\Users\27646\OneDrive\Master_Cloud"
)

$ErrorActionPreference = "Stop"

# ----------------- BASIC SETUP -----------------
if (-not (Test-Path $RootPath)) {
    Write-Host "RootPath not found: $RootPath" -ForegroundColor Red
    exit 1
}

$SmartDir   = Join-Path $RootPath "_SmartSorter"
$VenvDir    = Join-Path $SmartDir ".venv"
$PythonExe  = Join-Path $VenvDir "Scripts\python.exe"
$BrainPy    = Join-Path $SmartDir "smartbrain.py"
$LogDir     = Join-Path $RootPath "_SortLogs"
$ErrorLog   = Join-Path $LogDir "smartbrain_errors.log"

if (-not (Test-Path $SmartDir)) {
    New-Item -ItemType Directory -Path $SmartDir | Out-Null
}
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

function Write-ErrorLog {
    param([string]$Message)
    $timestamp = (Get-Date).ToString("s")
    "$timestamp `t $Message" | Out-File -FilePath $ErrorLog -Append -Encoding UTF8
}

# ----------------- PYTHON VENV -----------------
if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    try {
        # adjust to 'python' if 'py' is not installed
        py -3 -m venv $VenvDir
    } catch {
        Write-Host "Failed to create venv: $_" -ForegroundColor Red
        Write-ErrorLog "VENV_CREATE_FAILED: $_"
        exit 1
    }
}

if (-not (Test-Path $PythonExe)) {
    Write-Host "Python executable not found in venv." -ForegroundColor Red
    Write-ErrorLog "PYTHON_EXE_MISSING_IN_VENV"
    exit 1
}

# ----------------- PYTHON PACKAGES -----------------
Write-Host "Checking / installing Python packages..." -ForegroundColor Cyan
try {
    & $PythonExe -m pip install --upgrade pip
    & $PythonExe -m pip install pillow imagehash PyPDF2 tqdm
    # Heavy ones (will log errors if build fails)
    & $PythonExe -m pip install face_recognition pytesseract || Write-ErrorLog "PIP_WARN: face_recognition or pytesseract may have failed to install"
} catch {
    Write-Host "Pip install error: $_" -ForegroundColor Yellow
    Write-ErrorLog "PIP_INSTALL_ERROR: $_"
}

# ----------------- EXTERNAL TOOLS DETECTION -----------------
$env:SMARTBRAIN_EXIFTOOL = ""
$env:SMARTBRAIN_FFPROBE  = ""
$env:SMARTBRAIN_TESSERACT= ""

try {
    $exifCmd = Get-Command exiftool -ErrorAction SilentlyContinue
    if ($exifCmd) {
        $env:SMARTBRAIN_EXIFTOOL = $exifCmd.Source
        Write-Host "ExifTool found at $($exifCmd.Source)" -ForegroundColor Green
    } else {
        Write-Host "ExifTool not found in PATH." -ForegroundColor Yellow
        Write-ErrorLog "EXIFTOOL_NOT_FOUND"
    }
} catch {
    Write-ErrorLog "EXIFTOOL_DETECT_ERROR: $_"
}

try {
    $ffpCmd = Get-Command ffprobe -ErrorAction SilentlyContinue
    if ($ffpCmd) {
        $env:SMARTBRAIN_FFPROBE = $ffpCmd.Source
        Write-Host "ffprobe found at $($ffpCmd.Source)" -ForegroundColor Green
    } else {
        Write-Host "ffprobe not found in PATH." -ForegroundColor Yellow
        Write-ErrorLog "FFPROBE_NOT_FOUND"
    }
} catch {
    Write-ErrorLog "FFPROBE_DETECT_ERROR: $_"
}

try {
    $tessCmd = Get-Command tesseract -ErrorAction SilentlyContinue
    if ($tessCmd) {
        $env:SMARTBRAIN_TESSERACT = $tessCmd.Source
        Write-Host "Tesseract found at $($tessCmd.Source)" -ForegroundColor Green
    } else {
        Write-Host "Tesseract not found in PATH." -ForegroundColor Yellow
        Write-ErrorLog "TESSERACT_NOT_FOUND"
    }
} catch {
    Write-ErrorLog "TESSERACT_DETECT_ERROR: $_"
}

# ----------------- SMARTBRAIN SCRIPT PRESENCE -----------------
if (-not (Test-Path $BrainPy)) {
    Write-Host "smartbrain.py not found at $BrainPy" -ForegroundColor Red
    Write-Host "Save the Python module as smartbrain.py in _SmartSorter and re-run." -ForegroundColor Yellow
    Write-ErrorLog "SMARTBRAIN_PY_MISSING"
    exit 1
}

# ----------------- RUN SMARTBRAIN -----------------
Write-Host "Launching SmartBrain (Level 3)..." -ForegroundColor Cyan
try {
    & $PythonExe $BrainPy --root "$RootPath"
} catch {
    Write-Host "SmartBrain crashed: $_" -ForegroundColor Red
    Write-ErrorLog "SMARTBRAIN_CRASH: $_"
}
