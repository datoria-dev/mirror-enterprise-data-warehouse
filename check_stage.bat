@echo off
REM ================================================================
REM Check Snowflake Stage Files
REM ================================================================

cd /d "%~dp0"

echo.
echo ========================================
echo Snowflake Stage Files Checker
echo ========================================
echo.

python 02_PYTHON_SCRIPTS\check_snowflake_stage.py

echo.
pause
