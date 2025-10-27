@echo off
REM ================================================================
REM Verify Streamlit Apps Deployment
REM ================================================================

cd /d "%~dp0"

echo.
echo ========================================
echo Deployment Verification
echo ========================================
echo.

python 02_PYTHON_SCRIPTS\verify_deployments.py

echo.
pause
