Write-Host "Building arbys.exe with PyInstaller..."

$scriptPath = Join-Path $PSScriptRoot 'arbys.py'
$assetsPath = Join-Path $PSScriptRoot 'assets'
$outDir = Join-Path $PSScriptRoot 'dist'

if (-Not (Test-Path $scriptPath)) {
    Write-Error "Could not find arbys.py in $PSScriptRoot"
    exit 1
}

if (-Not (Test-Path $assetsPath)) {
    Write-Error "Could not find assets folder in $PSScriptRoot"
    exit 1
}

pyinstaller --onefile --windowed --add-data "$assetsPath;assets" --name arbys $scriptPath

if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

Write-Host "Build complete. Executable available in dist\arbys.exe"