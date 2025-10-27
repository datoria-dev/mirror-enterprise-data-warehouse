@echo off
REM ============================================================================
REM Install SnowSQL - Manual Installation Script
REM ============================================================================

echo.
echo ============================================================================
echo SnowSQL Installation Script
echo ============================================================================
echo.

REM Check if SnowSQL is already installed
where snowsql >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo SnowSQL is already installed!
    snowsql --version
    echo.
    echo If you want to reinstall, uninstall first from Control Panel.
    pause
    exit /b 0
)

echo [1/3] Checking if installer is downloaded...
echo.

set INSTALLER_PATH=C:\Users\fonat\Downloads\snowsql-windows.msi

if not exist "%INSTALLER_PATH%" (
    echo Installer not found. Downloading now...
    echo.
    curl -L -o "%INSTALLER_PATH%" https://sfc-repo.snowflakecomputing.com/snowsql/bootstrap/1.2/windows_x86_64/snowsql-1.2.28-windows_x86_64.msi

    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Download failed.
        echo Please download manually from:
        echo https://developers.snowflake.com/snowsql/
        pause
        exit /b 1
    )
)

echo [2/3] Installer found: %INSTALLER_PATH%
echo.

echo [3/3] Launching installer...
echo.
echo Please follow the installation wizard.
echo.
echo IMPORTANT: During installation:
echo   - Accept the license agreement
echo   - Use default installation path
echo   - Let it add SnowSQL to PATH
echo.

pause

REM Launch the installer
start "" "%INSTALLER_PATH%"

echo.
echo ============================================================================
echo Waiting for installation to complete...
echo ============================================================================
echo.
echo Please wait for the installation wizard to finish.
echo After installation completes, press any key to verify.
echo.

pause

echo.
echo Verifying SnowSQL installation...
echo.

where snowsql >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ SnowSQL installed successfully!
    echo.
    snowsql --version
    echo.
    echo You can now use SnowSQL from any command prompt.
    echo.
    echo Next steps:
    echo   1. Close this window
    echo   2. Open a NEW PowerShell window
    echo   3. Run: snowsql -a GenericCorp-CRH_LEDW -u FUAD.ONATE@CompanyX.COM --authenticator externalbrowser
    echo.
) else (
    echo ✗ SnowSQL not found in PATH.
    echo.
    echo This might be because:
    echo   1. Installation is still in progress
    echo   2. You need to close and reopen your terminal
    echo   3. Installation failed
    echo.
    echo Try closing this window and opening a NEW PowerShell, then run:
    echo   snowsql --version
    echo.
)

pause
