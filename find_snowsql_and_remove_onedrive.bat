@echo off
REM ============================================================================
REM Find SnowSQL Installation and Remove OneDrive
REM ============================================================================

echo.
echo ============================================================================
echo Task 1: Find SnowSQL Installation
echo ============================================================================
echo.

echo Searching for snowsql.exe in common locations...
echo.

REM Search in Program Files
echo [1/4] Checking Program Files...
dir "C:\Program Files\*snowsql*" /s /b 2>nul
if exist "C:\Program Files\Snowflake SnowSQL\snowsql.exe" (
    echo ✓ Found in Program Files!
    set SNOWSQL_PATH=C:\Program Files\Snowflake SnowSQL
    goto found_snowsql
)

REM Search in Program Files (x86)
echo [2/4] Checking Program Files (x86)...
dir "C:\Program Files (x86)\*snowsql*" /s /b 2>nul
if exist "C:\Program Files (x86)\Snowflake SnowSQL\snowsql.exe" (
    echo ✓ Found in Program Files (x86)!
    set SNOWSQL_PATH=C:\Program Files (x86)\Snowflake SnowSQL
    goto found_snowsql
)

REM Search in User folder
echo [3/4] Checking User AppData...
dir "C:\Users\fonat\AppData\*snowsql*" /s /b 2>nul

REM Search in User local folder
echo [4/4] Checking User .snowsql folder...
if exist "C:\Users\fonat\.snowsql" (
    dir "C:\Users\fonat\.snowsql\snowsql.exe" /s /b 2>nul
)

echo.
echo ✗ SnowSQL not found in standard locations.
echo.
echo Possible reasons:
echo   - Installation failed silently
echo   - SnowSQL installed in custom location
echo   - Installation was cancelled
echo.

echo Checking if SnowSQL is in Windows registry...
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" /s /f "SnowSQL" 2>nul
reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" /s /f "SnowSQL" 2>nul

goto check_onedrive

:found_snowsql
echo.
echo ============================================================================
echo SnowSQL Found!
echo ============================================================================
echo.
echo Location: %SNOWSQL_PATH%
echo.
echo Adding to PATH...
setx PATH "%PATH%;%SNOWSQL_PATH%" >nul 2>&1
echo.
echo ✓ Added to PATH
echo.
echo IMPORTANT: Close this window and open a NEW PowerShell to use snowsql
echo.

:check_onedrive
echo.
echo ============================================================================
echo Task 2: Check OneDrive and Plan Removal
echo ============================================================================
echo.

echo Do you want to proceed with OneDrive removal analysis?
choice /C YN /M "Analyze OneDrive removal"
if %ERRORLEVEL%==2 goto end

echo.
echo Checking OneDrive installation...
echo.

REM Check if OneDrive is installed
if exist "C:\Users\fonat\OneDrive" (
    echo ✓ OneDrive folder found: C:\Users\fonat\OneDrive

    REM Check size
    echo.
    echo Calculating OneDrive folder size...
    for /f "tokens=3" %%a in ('dir "C:\Users\fonat\OneDrive" /-c ^| findstr /C:"bytes"') do set ONEDRIVE_SIZE=%%a
    echo Size: %ONEDRIVE_SIZE% bytes
    echo.
) else (
    echo ✗ OneDrive folder not found
)

REM Check OneDrive process
echo Checking if OneDrive is running...
tasklist | findstr /i "OneDrive.exe" >nul
if %ERRORLEVEL%==0 (
    echo ✓ OneDrive is currently running
    echo.
    echo To stop OneDrive:
    echo   taskkill /f /im OneDrive.exe
    echo.
) else (
    echo ✗ OneDrive is not running
)

REM Check OneDrive installation path
echo.
echo Checking OneDrive installation...
if exist "C:\Users\fonat\AppData\Local\Microsoft\OneDrive\OneDrive.exe" (
    echo ✓ OneDrive installed at: C:\Users\fonat\AppData\Local\Microsoft\OneDrive\
)

echo.
echo ============================================================================
echo OneDrive Removal Plan
echo ============================================================================
echo.
echo BEFORE removing OneDrive, you should:
echo.
echo 1. ✓ BACKUP IMPORTANT FILES from OneDrive folder
echo    Location: C:\Users\fonat\OneDrive\
echo.
echo 2. ✓ VERIFY MYORG_LOCAL has all your latest work
echo    Location: C:\Users\fonat\Documents\MYORG_LOCAL\
echo.
echo 3. ✓ MARK OneDrive repo as LEGACY
echo    Run: mark_onedrive_as_legacy.bat
echo.

echo Do you want to see the OneDrive removal steps now?
choice /C YN /M "Show OneDrive removal steps"
if %ERRORLEVEL%==2 goto end

echo.
echo ============================================================================
echo Steps to Remove OneDrive
echo ============================================================================
echo.
echo STEP 1: Stop OneDrive
echo -----------------------
echo taskkill /f /im OneDrive.exe
echo.
echo STEP 2: Uninstall OneDrive (Personal)
echo -----------------------
echo %LOCALAPPDATA%\Microsoft\OneDrive\OneDriveSetup.exe /uninstall
echo.
echo STEP 3: Uninstall OneDrive (Business) - If installed
echo -----------------------
echo %PROGRAMFILES%\Microsoft OneDrive\OneDriveSetup.exe /uninstall
echo %PROGRAMFILES(X86)%\Microsoft OneDrive\OneDriveSetup.exe /uninstall
echo.
echo STEP 4: Clean up registry (Optional, Advanced)
echo -----------------------
echo reg delete "HKCU\Software\Microsoft\OneDrive" /f
echo reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Desktop\NameSpace\{018D5C66-4533-4307-9B53-224DE2ED1FE6}" /f
echo.
echo STEP 5: Remove OneDrive folder
echo -----------------------
echo rd "C:\Users\fonat\OneDrive" /s /q
echo.
echo STEP 6: Prevent OneDrive from auto-starting
echo -----------------------
echo reg add "HKLM\Software\Policies\Microsoft\Windows\OneDrive" /v "DisableFileSyncNGSC" /t REG_DWORD /d 1 /f
echo.

echo.
echo ⚠️  WARNING: These steps will PERMANENTLY remove OneDrive
echo.
echo Make sure you have:
echo   ✓ Backed up all files from OneDrive
echo   ✓ Moved work to MYORG_LOCAL
echo   ✓ Marked OneDrive repo as LEGACY
echo.

echo Do you want to create a removal script?
choice /C YN /M "Create OneDrive removal script"
if %ERRORLEVEL%==2 goto end

echo.
echo Creating remove_onedrive.bat...
echo.

(
echo @echo off
echo REM OneDrive Removal Script
echo echo WARNING: This will remove OneDrive completely!
echo pause
echo echo Stopping OneDrive...
echo taskkill /f /im OneDrive.exe
echo timeout /t 3
echo echo Uninstalling OneDrive...
echo %%LOCALAPPDATA%%\Microsoft\OneDrive\OneDriveSetup.exe /uninstall
echo timeout /t 5
echo echo Removing OneDrive folder...
echo rd "C:\Users\fonat\OneDrive" /s /q
echo echo Preventing OneDrive from auto-starting...
echo reg add "HKLM\Software\Policies\Microsoft\Windows\OneDrive" /v "DisableFileSyncNGSC" /t REG_DWORD /d 1 /f
echo echo Done!
echo pause
) > remove_onedrive.bat

echo ✓ Created: remove_onedrive.bat
echo.
echo To execute it, run as Administrator:
echo   Right-click remove_onedrive.bat → Run as Administrator
echo.

:end
echo.
echo ============================================================================
echo Summary
echo ============================================================================
echo.
echo SnowSQL: Use Web UI for deployment (no SnowSQL needed)
echo OneDrive: remove_onedrive.bat created if you want to remove it
echo.
echo RECOMMENDATION:
echo   1. Deploy Symantec using Web UI first
echo   2. Then remove OneDrive if desired
echo.
pause
