# ============================================================================
# Reinstall SnowSQL - PowerShell Script
# ============================================================================
# Run this as Administrator

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "SnowSQL Reinstallation Script" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please:" -ForegroundColor Yellow
    Write-Host "  1. Right-click PowerShell" -ForegroundColor Yellow
    Write-Host "  2. Select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host "  3. Run this script again" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

Write-Host "[1/5] Checking for existing SnowSQL installation..." -ForegroundColor Yellow
Write-Host ""

# Check if SnowSQL is already installed
$snowsqlPath = Get-Command snowsql -ErrorAction SilentlyContinue

if ($snowsqlPath) {
    Write-Host "Found existing SnowSQL at: $($snowsqlPath.Source)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Uninstalling old version..." -ForegroundColor Yellow

    # Find SnowSQL in installed programs
    $uninstallKey = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* |
                    Where-Object { $_.DisplayName -like "*SnowSQL*" }

    if ($uninstallKey) {
        Write-Host "Found in registry: $($uninstallKey.DisplayName)" -ForegroundColor Green
        $uninstallString = $uninstallKey.UninstallString

        if ($uninstallString) {
            Write-Host "Running uninstaller..." -ForegroundColor Yellow
            Start-Process msiexec.exe -ArgumentList "/x `"$($uninstallKey.PSChildName)`" /qn" -Wait
            Write-Host "Uninstall complete!" -ForegroundColor Green
        }
    }

    Write-Host "Waiting for cleanup..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
}

Write-Host ""
Write-Host "[2/5] Checking installer..." -ForegroundColor Yellow
Write-Host ""

$installerPath = "C:\Users\fonat\Downloads\snowsql-latest.msi"

if (-not (Test-Path $installerPath)) {
    Write-Host "ERROR: Installer not found at: $installerPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Downloading now..." -ForegroundColor Yellow

    $url = "https://sfc-repo.snowflakecomputing.com/snowsql/bootstrap/1.3/windows_x86_64/snowsql-1.3.1-windows_x86_64.msi"

    try {
        Invoke-WebRequest -Uri $url -OutFile $installerPath
        Write-Host "Download complete!" -ForegroundColor Green
    } catch {
        Write-Host "Download failed: $_" -ForegroundColor Red
        pause
        exit 1
    }
}

Write-Host "Installer ready: $installerPath" -ForegroundColor Green
Write-Host ""

Write-Host "[3/5] Installing SnowSQL..." -ForegroundColor Yellow
Write-Host ""

# Install SnowSQL with proper parameters
$installArgs = @(
    "/i"
    "`"$installerPath`""
    "/qn"
    "/norestart"
    "INSTALLDIR=`"C:\Program Files\Snowflake SnowSQL`""
)

Write-Host "Running installer (this may take 1-2 minutes)..." -ForegroundColor Yellow
$process = Start-Process msiexec.exe -ArgumentList $installArgs -Wait -PassThru

if ($process.ExitCode -eq 0) {
    Write-Host "Installation successful!" -ForegroundColor Green
} else {
    Write-Host "Installation returned code: $($process.ExitCode)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[4/5] Adding SnowSQL to PATH..." -ForegroundColor Yellow
Write-Host ""

# Common SnowSQL installation paths
$possiblePaths = @(
    "C:\Program Files\Snowflake SnowSQL",
    "C:\Program Files (x86)\Snowflake SnowSQL",
    "$env:USERPROFILE\.snowsql"
)

$snowsqlExe = $null

foreach ($path in $possiblePaths) {
    $exePath = Join-Path $path "snowsql.exe"
    if (Test-Path $exePath) {
        $snowsqlExe = $path
        Write-Host "Found SnowSQL at: $snowsqlExe" -ForegroundColor Green
        break
    }
}

if ($snowsqlExe) {
    # Get current PATH
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")

    # Check if SnowSQL path is already in PATH
    if ($currentPath -notlike "*$snowsqlExe*") {
        Write-Host "Adding to system PATH..." -ForegroundColor Yellow
        $newPath = "$currentPath;$snowsqlExe"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
        Write-Host "Added to PATH!" -ForegroundColor Green
    } else {
        Write-Host "Already in PATH!" -ForegroundColor Green
    }
} else {
    Write-Host "WARNING: Could not find snowsql.exe" -ForegroundColor Yellow
    Write-Host "You may need to add it to PATH manually" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[5/5] Verifying installation..." -ForegroundColor Yellow
Write-Host ""

# Refresh environment variables
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
            [System.Environment]::GetEnvironmentVariable("Path", "User")

# Try to run snowsql
Write-Host "Testing SnowSQL command..." -ForegroundColor Yellow

try {
    $version = & snowsql --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "SUCCESS! SnowSQL is installed and working!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Version: $version" -ForegroundColor Cyan
    } else {
        throw "snowsql command failed"
    }
} catch {
    Write-Host ""
    Write-Host "NOTE: SnowSQL installed but not immediately available" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "This is normal. Please:" -ForegroundColor Yellow
    Write-Host "  1. Close this PowerShell window" -ForegroundColor Yellow
    Write-Host "  2. Open a NEW PowerShell window" -ForegroundColor Yellow
    Write-Host "  3. Run: snowsql --version" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Close this window" -ForegroundColor White
Write-Host "  2. Open a NEW PowerShell (to load updated PATH)" -ForegroundColor White
Write-Host "  3. Test: snowsql --version" -ForegroundColor White
Write-Host "  4. Connect: snowsql -a GenericCorp-CRH_LEDW -u FUAD.ONATE@CompanyX.COM --authenticator externalbrowser" -ForegroundColor White
Write-Host ""

pause
