@echo off
REM ================================================================
REM SnowSQL Reinstallation Script
REM ================================================================
echo.
echo ========================================
echo SnowSQL Reinstallation
echo ========================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script requires Administrator privileges.
    echo.
    echo Please right-click this file and select "Run as Administrator"
    echo.
    pause
    exit /b 1
)

echo [Step 1/5] Checking for existing SnowSQL installation...
echo.

REM Try to find existing SnowSQL installation
set SNOWSQL_FOUND=0
where snowsql >nul 2>&1
if %errorLevel% equ 0 (
    echo Found SnowSQL in PATH
    set SNOWSQL_FOUND=1
)

if exist "C:\Program Files\Snowflake SnowSQL\snowsql.exe" (
    echo Found SnowSQL in C:\Program Files\Snowflake SnowSQL\
    set SNOWSQL_FOUND=1
)

if %SNOWSQL_FOUND% equ 1 (
    echo.
    echo [Step 2/5] Uninstalling existing SnowSQL...
    echo.

    REM Find and uninstall via registry
    for /f "tokens=*" %%a in ('reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" /s /f "SnowSQL" 2^>nul ^| findstr "UninstallString"') do (
        set UNINSTALL_CMD=%%a
    )

    REM Try standard uninstall
    msiexec /x {SNOWSQL-GUID} /qn /norestart 2>nul

    REM Remove directory if it still exists
    if exist "C:\Program Files\Snowflake SnowSQL" (
        echo Removing old installation directory...
        rmdir /s /q "C:\Program Files\Snowflake SnowSQL" 2>nul
    )

    echo Old installation removed.
) else (
    echo No existing installation found.
    echo [Step 2/5] Skipping uninstall...
)

echo.
echo [Step 3/5] Installing SnowSQL 1.3.1...
echo.

REM Check if installer exists
set INSTALLER_PATH=C:\Users\fonat\Downloads\snowsql-latest.msi
if not exist "%INSTALLER_PATH%" (
    echo ERROR: Installer not found at %INSTALLER_PATH%
    echo.
    echo Please download SnowSQL from:
    echo https://sfc-repo.snowflakecomputing.com/snowsql/bootstrap/1.3/windows_x86_64/snowsql-1.3.1-windows_x86_64.msi
    echo.
    pause
    exit /b 1
)

REM Install SnowSQL
echo Installing from: %INSTALLER_PATH%
msiexec /i "%INSTALLER_PATH%" /qn /norestart INSTALLDIR="C:\Program Files\Snowflake SnowSQL"

REM Wait for installation to complete
timeout /t 5 /nobreak >nul

echo.
echo [Step 4/5] Adding SnowSQL to system PATH...
echo.

REM Add to PATH using setx (system-wide)
setx /M PATH "%PATH%;C:\Program Files\Snowflake SnowSQL" >nul 2>&1

REM Also add to current session
set PATH=%PATH%;C:\Program Files\Snowflake SnowSQL

echo PATH updated.

echo.
echo [Step 5/5] Verifying installation...
echo.

REM Verify installation
if exist "C:\Program Files\Snowflake SnowSQL\snowsql.exe" (
    echo SUCCESS! SnowSQL installed at: C:\Program Files\Snowflake SnowSQL\snowsql.exe
    echo.
    echo To verify, close this window and open a NEW PowerShell window, then run:
    echo   snowsql --version
    echo.
    echo Then you can deploy Symantec with:
    echo   cd "C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV"
    echo   .\deploy_symantec.bat
) else (
    echo ERROR: Installation completed but snowsql.exe not found.
    echo Please try manual installation from:
    echo https://docs.snowflake.com/en/user-guide/snowsql-install-config.html
)

echo.
echo ========================================
echo Installation Complete
echo ========================================
echo.
pause
