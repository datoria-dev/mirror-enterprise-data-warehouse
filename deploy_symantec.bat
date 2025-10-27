@echo off
REM ============================================================================
REM Deploy Symantec Streamlit App to Snowflake
REM ============================================================================
REM Author: Claude Code
REM Date: 2025-01-25
REM Description: Automates the deployment of Symantec EDR Dashboard
REM ============================================================================

echo.
echo ============================================================================
echo Symantec Streamlit App - Deployment Script
echo ============================================================================
echo.
echo This script will help you deploy the Symantec EDR Dashboard to Snowflake.
echo.
echo Prerequisites:
echo   1. SnowSQL installed and configured
echo   2. SSO/Okta authentication working
echo   3. PRD_DEVELOPER role with necessary permissions
echo.
echo ============================================================================
echo.

REM Check if SnowSQL is installed
where snowsql >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: SnowSQL not found in PATH
    echo Please install SnowSQL from: https://docs.snowflake.com/en/user-guide/snowsql-install-config.html
    pause
    exit /b 1
)

echo [1/5] SnowSQL found: OK
echo.

REM Set variables
set ACCOUNT=MYORG-DATA_WH
set USER=FUAD.ONATE@CompanyX.COM
set APP_FILE=C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Symantec/streamlit_app.py

REM Check if file exists
if not exist "%APP_FILE%" (
    echo ERROR: Streamlit app file not found at:
    echo %APP_FILE%
    pause
    exit /b 1
)

echo [2/5] Streamlit app file found: OK
echo.

echo ============================================================================
echo STEP 1: Connecting to Snowflake with SSO
echo ============================================================================
echo.
echo A browser window will open for Okta authentication...
echo Please authenticate and then return to this window.
echo.
pause

REM Create SQL script for deployment
set SQL_SCRIPT=%TEMP%\deploy_symantec.sql

echo -- Deployment script for Symantec Streamlit > "%SQL_SCRIPT%"
echo USE ROLE PRD_DEVELOPER; >> "%SQL_SCRIPT%"
echo USE DATABASE ITSECKPI_DB; >> "%SQL_SCRIPT%"
echo USE SCHEMA ITSECKPI_SCHEMA; >> "%SQL_SCRIPT%"
echo USE WAREHOUSE COMPUTE_WH; >> "%SQL_SCRIPT%"
echo. >> "%SQL_SCRIPT%"
echo -- Create stage >> "%SQL_SCRIPT%"
echo CREATE STAGE IF NOT EXISTS STREAMLIT_APPS_STAGE DIRECTORY = (ENABLE = TRUE); >> "%SQL_SCRIPT%"
echo. >> "%SQL_SCRIPT%"
echo -- Upload file >> "%SQL_SCRIPT%"
echo PUT file://%APP_FILE% @ITSECKPI_DB.ITSECKPI_SCHEMA.STREAMLIT_APPS_STAGE/Symantec/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE; >> "%SQL_SCRIPT%"
echo. >> "%SQL_SCRIPT%"
echo -- Verify upload >> "%SQL_SCRIPT%"
echo LIST @STREAMLIT_APPS_STAGE/Symantec/; >> "%SQL_SCRIPT%"
echo. >> "%SQL_SCRIPT%"
echo -- Create Streamlit app >> "%SQL_SCRIPT%"
echo DROP STREAMLIT IF EXISTS STREAMLIT_SYMANTEC; >> "%SQL_SCRIPT%"
echo CREATE STREAMLIT STREAMLIT_SYMANTEC ROOT_LOCATION = '@ITSECKPI_DB.ITSECKPI_SCHEMA.STREAMLIT_APPS_STAGE/Symantec' MAIN_FILE = 'streamlit_app.py' QUERY_WAREHOUSE = 'COMPUTE_WH'; >> "%SQL_SCRIPT%"
echo. >> "%SQL_SCRIPT%"
echo -- Get URL >> "%SQL_SCRIPT%"
echo SELECT 'https://' ^|^| CURRENT_ACCOUNT() ^|^| '.snowflakecomputing.com/streamlit/' ^|^| CURRENT_DATABASE() ^|^| '/' ^|^| CURRENT_SCHEMA() ^|^| '/STREAMLIT_SYMANTEC' AS STREAMLIT_URL; >> "%SQL_SCRIPT%"

echo [3/5] SQL script created: OK
echo.

echo ============================================================================
echo STEP 2: Executing deployment commands
echo ============================================================================
echo.

snowsql -a %ACCOUNT% -u %USER% --authenticator externalbrowser -f "%SQL_SCRIPT%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Deployment failed. Check the error messages above.
    echo.
    echo Common issues:
    echo   - Warehouse COMPUTE_WH not available: Use a different warehouse
    echo   - Permission denied: Contact your Snowflake admin
    echo   - Authentication failed: Check your Okta credentials
    echo.
    pause
    exit /b 1
)

echo.
echo [4/5] Deployment commands executed: OK
echo.

echo ============================================================================
echo STEP 3: Deployment Complete!
echo ============================================================================
echo.
echo The Symantec Streamlit app has been deployed successfully.
echo.
echo App URL: https://MYORG-DATA_WH.snowflakecomputing.com/streamlit/ITSECKPI_DB/ITSECKPI_SCHEMA/STREAMLIT_SYMANTEC
echo.
echo Next steps:
echo   1. Open the URL above in your browser
echo   2. Authenticate with Okta if prompted
echo   3. Test the download buttons in each tab
echo   4. Verify the alert thresholds appear with colors
echo.
echo [5/5] All steps completed: OK
echo.

echo ============================================================================
echo Testing Checklist:
echo ============================================================================
echo.
echo [ ] App loads without errors
echo [ ] Tab 1: Download Coverage CSV button works
echo [ ] Tab 1: Coverage alert appears (red/orange/green)
echo [ ] Tab 2: Download Health Status CSV button works
echo [ ] Tab 3: Download Critical Endpoints CSV button works
echo [ ] Tab 3: Critical endpoints alert appears
echo [ ] Sidebar: Refresh Now button works
echo [ ] Sidebar: Auto-refresh checkbox works
echo.
echo ============================================================================
echo.

REM Open browser with the app URL
choice /C YN /M "Do you want to open the app in your browser now"
if %ERRORLEVEL%==1 (
    start https://MYORG-DATA_WH.snowflakecomputing.com/streamlit/ITSECKPI_DB/ITSECKPI_SCHEMA/STREAMLIT_SYMANTEC
)

echo.
echo Deployment script finished.
echo.
pause
