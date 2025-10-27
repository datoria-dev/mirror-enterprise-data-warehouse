@echo off
REM ================================================================
REM Automated OneDrive Backup and Removal
REM ================================================================

cd /d "%~dp0"

echo.
echo ========================================
echo OneDrive Backup and Removal
echo ========================================
echo.

python 02_PYTHON_SCRIPTS\onedrive_backup_automation.py

echo.
pause
