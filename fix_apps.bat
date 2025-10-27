@echo off
REM ================================================================
REM Fix Streamlit Apps Issues
REM ================================================================

cd /d "%~dp0"

echo.
echo ========================================
echo Fix Streamlit Apps Issues
echo ========================================
echo.

python 02_PYTHON_SCRIPTS\fix_app_issues.py

echo.
pause
