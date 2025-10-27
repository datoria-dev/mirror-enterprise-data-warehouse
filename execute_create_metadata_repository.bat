@echo off
REM ============================================================================
REM Execute CREATE_METADATA_REPOSITORY.sql with Auto-Export
REM ============================================================================
REM
REM This batch file executes the metadata repository creation script and
REM automatically saves all results to CSV/JSON files for analysis.
REM
REM Date: 2025-10-24
REM ============================================================================

echo.
echo ================================================================================
echo Execute CREATE_METADATA_REPOSITORY.sql
echo ================================================================================
echo.

REM Get current date/time for output directory
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set timestamp=%datetime:~0,8%_%datetime:~8,6%

REM Execute the script
python run_sql_script.py --script 01_SQL_SCRIPTS\CREATE_METADATA_REPOSITORY.sql --output metadata_repository_%timestamp%

echo.
echo ================================================================================
echo Execution Complete
echo ================================================================================
echo.
echo Results saved to: 04_METADATA_SAMPLES\sql_execution_results\metadata_repository_%timestamp%
echo.
pause
