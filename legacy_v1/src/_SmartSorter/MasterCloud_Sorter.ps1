param(
    [string]$RootPath = "C:\Users\27646\OneDrive\Master_Cloud"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $RootPath)) {
    Write-Host "RootPath not found: $RootPath" -ForegroundColor Red
    exit 1
}

# --- Setup log folder ---
$logRoot   = Join-Path $RootPath "_SortLogs"
New-Item -ItemType Directory -Force -Path $logRoot | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$global:LogFile = Join-Path $logRoot "moves_$timestamp.csv"

"Timestamp,OriginalPath,NewPath" | Out-File $LogFile -Encoding UTF8

function Write-MoveLog {
    param(
        [string]$Source,
        [string]$Destination
    )
    $line = '"{0}","{1}","{2}"' -f (Get-Date).ToString("s"), $Source, $Destination
    Add-Content -Path $LogFile -Value $line
}

# --- Category root folders ---
$categories = @{
    "Studies"   = "01_Studies"
    "People"    = "02_People"
    "Photos"    = "03_Photos"
    "Videos"    = "04_Videos"
    "Projects"  = "05_Projects"
    "Installers"= "06_Installers"
    "Documents" = "07_Documents"
    "Backups"   = "08_Backups"
    "Archive"   = "99_Archive"
}

foreach ($cat in $categories.GetEnumerator()) {
    $path = Join-Path $RootPath $cat.Value
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path | Out-Null
    }
}

# --- Helper: safe move with folders + logging ---
function Move-WithLog {
    param(
        [string]$Source,
        [string]$DestinationFolder
    )

    if (-not (Test-Path $Source)) { return }

    if (-not (Test-Path $DestinationFolder)) {
        New-Item -ItemType Directory -Path $DestinationFolder | Out-Null
    }

    $destPath = Join-Path $DestinationFolder ([IO.Path]::GetFileName($Source))

    # If file exists, add suffix
    if (Test-Path $destPath) {
        $name  = [IO.Path]::GetFileNameWithoutExtension($destPath)
        $ext   = [IO.Path]::GetExtension($destPath)
        $i = 1
        do {
            $destPath = Join-Path $DestinationFolder ("{0}__{1}{2}" -f $name, $i, $ext)
            $i++
        } while (Test-Path $destPath)
    }

    Move-Item -LiteralPath $Source -Destination $destPath
    Write-MoveLog -Source $Source -Destination $destPath
}

# --- Classification logic ---
function Get-Category {
    param(
        [IO.FileInfo]$File
    )

    $ext = $File.Extension.ToLowerInvariant()
    $name = $File.Name.ToLowerInvariant()
    $full = $File.FullName.ToLowerInvariant()

    $imageExt = ".jpg",".jpeg",".png",".gif",".heic",".webp",".tif",".tiff",".bmp"
    $videoExt = ".mp4",".mov",".mkv",".avi",".wmv",".flv",".m4v",".3gp"
    $docExt   = ".pdf",".doc",".docx",".xls",".xlsx",".ppt",".pptx",".odt",".ods",".rtf",".txt"
    $codeExt  = ".py",".ps1",".psm1",".java",".cs",".cpp",".h",".js",".ts",".html",".css",".json",".yml",".yaml",".gradle",".kts"
    $installerExt = ".exe",".msi",".msix",".apk",".iso",".img",".dmg",".cab",".msixbundle",".zip"

    # 1) Installers
    if ($installerExt -contains $ext -or $full -like "*\installers\*") {
        return "Installers"
    }

    # 2) Photos (generic)
    if ($imageExt -contains $ext) {
        # Screenshots special case into Photos as well
        return "Photos"
    }

    # 3) Videos
    if ($videoExt -contains $ext) {
        return "Videos"
    }

    # 4) Studies (UNISA etc.)
    $studyPatterns = @(
        "unisa","assignment","ass1","ass2","ass3",
        "exam","portfolio","age","anh","soc","dva","cls"
    )
    if ($docExt -contains $ext) {
        foreach ($p in $studyPatterns) {
            if ($name -like "*$p*") { return "Studies" }
        }
    }

    # 5) Projects (code / dev)
    if ($codeExt -contains $ext -or $full -like "*\dev\*" -or $full -like "*\battery_pro*" -or $full -like "*\uilnes*" -or $full -like "*\minecraft*") {
        return "Projects"
    }

    # 6) Backups (old phones, SD card dumps, recoveries)
    if ($full -like "*backup*" -or $full -like "*whatsapp*" -or $full -like "*recover*" -or $full -like "*sdcard*" -or $full -like "*ouma hardeskyf*") {
        return "Backups"
    }

    # 7) Documents (generic office/pdf/text not already caught)
    if ($docExt -contains $ext) {
        return "Documents"
    }

    # 8) Fallback → Archive
    return "Archive"
}

# --- Auto sorter ---
function Invoke-AutoSorter {

    Write-Host "Scanning files in $RootPath ..." -ForegroundColor Cyan

    $allFiles = Get-ChildItem -Path $RootPath -Recurse -File -ErrorAction SilentlyContinue |
                Where-Object {
                    # Do not re-sort files that are already in category roots or log folder
                    $_.DirectoryName -notlike (Join-Path $RootPath "01_Studies*") -and
                    $_.DirectoryName -notlike (Join-Path $RootPath "02_People*")  -and
                    $_.DirectoryName -notlike (Join-Path $RootPath "03_Photos*")  -and
                    $_.DirectoryName -notlike (Join-Path $RootPath "04_Videos*")  -and
                    $_.DirectoryName -notlike (Join-Path $RootPath "05_Projects*")-and
                    $_.DirectoryName -notlike (Join-Path $RootPath "06_Installers*") -and
                    $_.DirectoryName -notlike (Join-Path $RootPath "07_Documents*")  -and
                    $_.DirectoryName -notlike (Join-Path $RootPath "08_Backups*")    -and
                    $_.DirectoryName -notlike (Join-Path $RootPath "99_Archive*")    -and
                    $_.DirectoryName -notlike (Join-Path $RootPath "_SortLogs*")
                }

    $total = $allFiles.Count
    if ($total -eq 0) {
        Write-Host "No files found to sort. Exiting." -ForegroundColor Yellow
        return
    }

    Write-Host "Found $total files to classify and move..." -ForegroundColor Green

    $i = 0
    foreach ($f in $allFiles) {
        $i++
        $percent = [int](($i / $total) * 100)
        Write-Progress -Activity "Sorting files" -Status "$i / $total" -PercentComplete $percent

        try {
            $cat = Get-Category -File $f
            $catFolderName = $categories[$cat]
            $destFolder = Join-Path $RootPath $catFolderName

            Move-WithLog -Source $f.FullName -DestinationFolder $destFolder
        }
        catch {
            Write-Host "Error sorting $($f.FullName): $_" -ForegroundColor Red
        }
    }

    Write-Progress -Activity "Sorting files" -Completed
    Write-Host "Auto sorting completed. Log file: $LogFile" -ForegroundColor Cyan
}

# --- Undo last run (uses the CSV log) ---
function Undo-LastSort {
    $lastLog = Get-ChildItem $logRoot -Filter "moves_*.csv" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $lastLog) {
        Write-Host "No move log found to undo." -ForegroundColor Yellow
        return
    }

    Write-Host "Using log: $($lastLog.FullName)" -ForegroundColor Cyan
    $rows = Import-Csv $lastLog.FullName

    $total = $rows.Count
    $i = 0
    foreach ($row in $rows) {
        $i++
        $percent = [int](($i / $total) * 100)
        Write-Progress -Activity "Undoing moves" -Status "$i / $total" -PercentComplete $percent

        $src = $row.NewPath
        $dst = $row.OriginalPath

        try {
            if (Test-Path $src) {
                $dstFolder = Split-Path $dst -Parent
                if (-not (Test-Path $dstFolder)) {
                    New-Item -ItemType Directory -Path $dstFolder | Out-Null
                }

                Move-Item -LiteralPath $src -Destination $dst
            }
        }
        catch {
            Write-Host "Error undoing move for $src : $_" -ForegroundColor Red
        }
    }

    Write-Progress -Activity "Undoing moves" -Completed
    Write-Host "Undo complete (as far as possible)." -ForegroundColor Green
}

# --- People face-labelling GUI (manual, image-by-image) ---
function Invoke-PeopleLabeler {

    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing

    $peopleRoot = Join-Path $RootPath $categories["People"]
    if (-not (Test-Path $peopleRoot)) {
        New-Item -ItemType Directory -Path $peopleRoot | Out-Null
    }

    # Get all image files currently NOT already inside 02_People
    $imageExt = ".jpg",".jpeg",".png",".gif",".heic",".webp",".tif",".tiff",".bmp"
    $images = Get-ChildItem -Path $RootPath -Recurse -File -ErrorAction SilentlyContinue |
              Where-Object {
                    $imageExt -contains $_.Extension.ToLowerInvariant() -and
                    $_.DirectoryName -notlike "$peopleRoot*"
              }

    if ($images.Count -eq 0) {
        [System.Windows.Forms.MessageBox]::Show("No images found to label (outside 02_People).","People Labeler")
        return
    }

    $index = 0

    # --- Build Form ---
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "People Labeler"
    $form.Width = 900
    $form.Height = 700
    $form.StartPosition = "CenterScreen"

    $pictureBox = New-Object System.Windows.Forms.PictureBox
    $pictureBox.Left = 10
    $pictureBox.Top = 10
    $pictureBox.Width = 640
    $pictureBox.Height = 640
    $pictureBox.SizeMode = "Zoom"

    $labelPath = New-Object System.Windows.Forms.Label
    $labelPath.Left = 660
    $labelPath.Top = 20
    $labelPath.Width = 200
    $labelPath.Height = 60

    $labelName = New-Object System.Windows.Forms.Label
    $labelName.Left = 660
    $labelName.Top = 90
    $labelName.Width = 200
    $labelName.Text = "Name for this person (folder):"

    $textName = New-Object System.Windows.Forms.TextBox
    $textName.Left = 660
    $textName.Top = 110
    $textName.Width = 200

    $btnSave = New-Object System.Windows.Forms.Button
    $btnSave.Left = 660
    $btnSave.Top = 150
    $btnSave.Width = 95
    $btnSave.Text = "Save && Next"

    $btnSkip = New-Object System.Windows.Forms.Button
    $btnSkip.Left = 765
    $btnSkip.Top = 150
    $btnSkip.Width = 95
    $btnSkip.Text = "Skip"

    $btnQuit = New-Object System.Windows.Forms.Button
    $btnQuit.Left = 660
    $btnQuit.Top = 190
    $btnQuit.Width = 200
    $btnQuit.Text = "Quit"

    $form.Controls.AddRange(@($pictureBox,$labelPath,$labelName,$textName,$btnSave,$btnSkip,$btnQuit))

    function Show-ImageAtIndex {
        param([int]$i)

        if ($i -ge $images.Count) {
            [System.Windows.Forms.MessageBox]::Show("All images processed.","People Labeler")
            $form.Close()
            return
        }

        $current = $images[$i]
        $labelPath.Text = $current.Name
        $textName.Text = ""

        # Load image
        try {
            if ($pictureBox.Image) {
                $pictureBox.Image.Dispose()
            }
            $img = [System.Drawing.Image]::FromFile($current.FullName)
            $pictureBox.Image = $img
        }
        catch {
            $pictureBox.Image = $null
        }
    }

    # --- Button handlers ---
    $btnSave.Add_Click({
        $name = $textName.Text.Trim()
        if ([string]::IsNullOrWhiteSpace($name)) {
            [System.Windows.Forms.MessageBox]::Show("Please enter a name (or click Skip).","People Labeler")
            return
        }

        $current = $images[$index]
        $personFolder = Join-Path $peopleRoot $name
        Move-WithLog -Source $current.FullName -DestinationFolder $personFolder

        $index++
        Show-ImageAtIndex -i $index
    })

    $btnSkip.Add_Click({
        $index++
        Show-ImageAtIndex -i $index
    })

    $btnQuit.Add_Click({
        $form.Close()
    })

    # Start on first image
    Show-ImageAtIndex -i 0
    [void]$form.ShowDialog()
}

# --- Simple menu ---
function Show-Menu {
    Write-Host ""
    Write-Host "=== Master_Cloud Super Sorter ===" -ForegroundColor Cyan
    Write-Host "Root: $RootPath"
    Write-Host ""
    Write-Host "1) Run auto sorter (moves files into categories)"
    Write-Host "2) Run People labeler GUI (01 photo at a time)"
    Write-Host "3) Undo last sort (using last moves_*.csv)"
    Write-Host "0) Exit"
    Write-Host ""
}

do {
    Show-Menu
    $choice = Read-Host "Choose an option"

    switch ($choice) {
        "1" { Invoke-AutoSorter }
        "2" { Invoke-PeopleLabeler }
        "3" { Undo-LastSort }
        "0" { break }
        Default { Write-Host "Invalid choice." -ForegroundColor Yellow }
    }

} while ($true)
