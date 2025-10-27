@echo off
REM ============================================================================
REM Mark OneDrive Repository as LEGACY
REM ============================================================================

echo.
echo ============================================================================
echo Mark OneDrive Repository as LEGACY
echo ============================================================================
echo.

set OLD_PATH=C:\Users\fonat\OneDrive\Documents\GenericCorp\Snowflake_ITSECKPI_Project_DEV
set NEW_PATH=C:\Users\fonat\OneDrive\Documents\GenericCorp\LEGACY_Snowflake_ITSECKPI_Project_DEV

echo This script will:
echo   1. Close any programs using the OneDrive folder
echo   2. Rename the folder to LEGACY_Snowflake_ITSECKPI_Project_DEV
echo   3. Verify the LEGACY_README.md file is present
echo.

pause

echo.
echo [1/3] Checking if folder exists...
echo.

if not exist "%OLD_PATH%" (
    if exist "%NEW_PATH%" (
        echo ✓ Folder already renamed to LEGACY!
        echo.
        goto verify_readme
    ) else (
        echo ✗ Folder not found at either location.
        echo.
        pause
        exit /b 1
    )
)

echo ✓ Found: %OLD_PATH%
echo.

echo [2/3] Renaming folder...
echo.
echo IMPORTANT: If you get an error "file is being used":
echo   1. Close File Explorer windows
echo   2. Close VSCode or any editor
echo   3. Wait a few seconds for OneDrive to finish syncing
echo   4. Run this script again
echo.

ren "%OLD_PATH%" "LEGACY_Snowflake_ITSECKPI_Project_DEV"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ✗ Failed to rename folder.
    echo.
    echo Common causes:
    echo   - File Explorer window is open in that folder
    echo   - VSCode or editor has files open from that folder
    echo   - OneDrive is syncing files
    echo   - Another program is accessing the folder
    echo.
    echo Please close all programs and try again.
    echo.
    pause
    exit /b 1
)

echo ✓ Folder renamed successfully!
echo.

:verify_readme
echo [3/3] Verifying LEGACY_README.md...
echo.

if exist "%NEW_PATH%\LEGACY_README.md" (
    echo ✓ LEGACY_README.md found!
    echo.
) else (
    echo ⚠ LEGACY_README.md not found.
    echo Creating it now...
    echo.

    REM Create the README if it doesn't exist
    echo # ⚠️ LEGACY REPOSITORY - DO NOT USE > "%NEW_PATH%\LEGACY_README.md"
    echo. >> "%NEW_PATH%\LEGACY_README.md"
    echo ## This repository is deprecated. >> "%NEW_PATH%\LEGACY_README.md"
    echo. >> "%NEW_PATH%\LEGACY_README.md"
    echo Please use: C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\ >> "%NEW_PATH%\LEGACY_README.md"

    echo ✓ LEGACY_README.md created!
    echo.
)

echo.
echo ============================================================================
echo SUCCESS! OneDrive repository marked as LEGACY
echo ============================================================================
echo.
echo The folder has been renamed to:
echo   %NEW_PATH%
echo.
echo From now on, ALWAYS use:
echo   ✅ C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\
echo.
echo NOT:
echo   ❌ %NEW_PATH%
echo.
echo ============================================================================
echo.

echo Recommendations:
echo.
echo 1. Update any shortcuts or bookmarks to point to MYORG_LOCAL
echo 2. Close any terminals that were in the old OneDrive folder
echo 3. Open a new terminal in MYORG_LOCAL
echo.

echo.
echo Do you want to open File Explorer at the MYORG_LOCAL folder?
choice /C YN /M "Open MYORG_LOCAL folder now"

if %ERRORLEVEL%==1 (
    start "" "C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV"
)

echo.
echo Script completed.
echo.
pause
