@echo off
REM ================================================================
REM Deploy Streamlit Apps to Snowflake
REM ================================================================

cd /d "%~dp0"

echo.
echo ========================================
echo Streamlit Apps Deployment
echo ========================================
echo.

python 02_PYTHON_SCRIPTS\deploy_with_progress.py

echo.
pause
