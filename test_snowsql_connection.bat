@echo off
REM ================================================================
REM Automated SnowSQL Connection Test
REM ================================================================

cd /d "%~dp0"

echo.
echo ========================================
echo Snowflake Connection Test (SSO/Okta)
echo ========================================
echo.

python 02_PYTHON_SCRIPTS\test_snowsql_simple.py

echo.
pause
