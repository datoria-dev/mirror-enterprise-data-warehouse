@echo off
REM ================================================================
REM Deploy Sophos App Only - With All Fixes Applied
REM ================================================================

cd /d "%~dp0"

echo.
echo ========================================
echo Deploy Sophos App (Fixed Version)
echo ========================================
echo.
echo This will deploy the FIXED version of Sophos with:
echo - ALL np.random calls replaced with Python random module
echo - Download button properly configured
echo.

python "02_PYTHON_SCRIPTS\deploy_sophos_only.py"

echo.
pause
