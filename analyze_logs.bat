@echo off
REM ================================================================
REM Analyze Deployment Logs
REM ================================================================

cd /d "%~dp0"

echo.
echo ========================================
echo Deployment Log Analyzer
echo ========================================
echo.

python 02_PYTHON_SCRIPTS\analyze_deployment_logs.py

echo.
pause
