@echo off
REM ================================================================
REM Redeploy Sophos with ALL Fixes Applied
REM - np.random fixes (6 calls)
REM - Database context fix (STAGE GET error)
REM - Download button configuration
REM ================================================================

cd /d "%~dp0"

echo.
echo ========================================
echo Redeploy Sophos - All Fixes Applied
echo ========================================
echo.
echo Fixes included:
echo  [OK] np.random replaced with Python random module
echo  [OK] Database context set (USE DATABASE/SCHEMA)
echo  [OK] Download button properly configured
echo.

python "02_PYTHON_SCRIPTS\deploy_sophos_only.py"

echo.
pause
