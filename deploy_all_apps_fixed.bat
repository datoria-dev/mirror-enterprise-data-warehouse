@echo off
echo ================================================================================
echo DEPLOYING ALL FIXED STREAMLIT APPS TO SNOWFLAKE
echo ================================================================================
echo.
echo This script will:
echo 1. Upload all 18 app files to Snowflake stage
echo 2. Create/Replace all Streamlit apps with:
echo    - Fixed syntax errors (Trellix, Crowdstrike)
echo    - CPR - prefix in all titles
echo.
echo Target: DEV_REPORTING.SECURITY_ANALYTICS
echo.
pause
echo.

python "02_PYTHON_SCRIPTS\deploy_all_apps_fixed.py"

echo.
echo ================================================================================
echo DEPLOYMENT COMPLETE
echo ================================================================================
echo Check the deployment_logs folder for detailed logs
echo.
pause
