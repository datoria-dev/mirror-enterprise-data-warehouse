@echo off
REM ============================================================================
REM Upload utils.py and database.py to all 18 Streamlit app folders
REM Uses a single SQL script to upload all files with ONE SSO authentication
REM ============================================================================

echo ============================================================================
echo Creating SQL script for uploading utils.py and database.py to all apps
echo ============================================================================
echo.

REM Create temporary SQL script
echo -- Upload utils.py and database.py to all 18 Streamlit app folders > upload_shared_files_temp.sql
echo. >> upload_shared_files_temp.sql
echo -- Set context >> upload_shared_files_temp.sql
echo USE WAREHOUSE DEV_WH; >> upload_shared_files_temp.sql
echo USE DATABASE DEV_REPORTING; >> upload_shared_files_temp.sql
echo USE SCHEMA SECURITY_ANALYTICS; >> upload_shared_files_temp.sql
echo. >> upload_shared_files_temp.sql

REM Add PUT commands for all 18 apps
echo -- Ancon >> upload_shared_files_temp.sql
echo PUT file://utils.py @STREAMLIT_APPS_STAGE/Ancon/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo PUT file://database.py @STREAMLIT_APPS_STAGE/Ancon/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo. >> upload_shared_files_temp.sql

echo -- BitSight >> upload_shared_files_temp.sql
echo PUT file://BitSight/utils.py @STREAMLIT_APPS_STAGE/BitSight/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo PUT file://database.py @STREAMLIT_APPS_STAGE/BitSight/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo. >> upload_shared_files_temp.sql

echo -- Cisco_AMP >> upload_shared_files_temp.sql
echo PUT file://utils.py @STREAMLIT_APPS_STAGE/Cisco_AMP/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo PUT file://database.py @STREAMLIT_APPS_STAGE/Cisco_AMP/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo. >> upload_shared_files_temp.sql

echo -- Crowdstrike >> upload_shared_files_temp.sql
echo PUT file://utils.py @STREAMLIT_APPS_STAGE/Crowdstrike/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo PUT file://database.py @STREAMLIT_APPS_STAGE/Crowdstrike/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo. >> upload_shared_files_temp.sql

echo -- CybelAngel >> upload_shared_files_temp.sql
echo PUT file://utils.py @STREAMLIT_APPS_STAGE/CybelAngel/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo PUT file://database.py @STREAMLIT_APPS_STAGE/CybelAngel/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo. >> upload_shared_files_temp.sql

echo -- Intel_Threats >> upload_shared_files_temp.sql
echo PUT file://utils.py @STREAMLIT_APPS_STAGE/Intel_Threats/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo PUT file://database.py @STREAMLIT_APPS_STAGE/Intel_Threats/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo. >> upload_shared_files_temp.sql

echo -- Leviat >> upload_shared_files_temp.sql
echo PUT file://utils.py @STREAMLIT_APPS_STAGE/Leviat/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo PUT file://database.py @STREAMLIT_APPS_STAGE/Leviat/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo. >> upload_shared_files_temp.sql

echo -- Proofpoint >> upload_shared_files_temp.sql
echo PUT file://utils.py @STREAMLIT_APPS_STAGE/Proofpoint/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo PUT file://database.py @STREAMLIT_APPS_STAGE/Proofpoint/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo. >> upload_shared_files_temp.sql

echo -- Qualys >> upload_shared_files_temp.sql
echo PUT file://utils.py @STREAMLIT_APPS_STAGE/Qualys/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo PUT file://database.py @STREAMLIT_APPS_STAGE/Qualys/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo. >> upload_shared_files_temp.sql

echo -- SentinelOne >> upload_shared_files_temp.sql
echo PUT file://utils.py @STREAMLIT_APPS_STAGE/SentinelOne/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo PUT file://database.py @STREAMLIT_APPS_STAGE/SentinelOne/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo. >> upload_shared_files_temp.sql

echo -- ServiceNow >> upload_shared_files_temp.sql
echo PUT file://utils.py @STREAMLIT_APPS_STAGE/ServiceNow/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo PUT file://database.py @STREAMLIT_APPS_STAGE/ServiceNow/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo. >> upload_shared_files_temp.sql

echo -- Sophos >> upload_shared_files_temp.sql
echo PUT file://utils.py @STREAMLIT_APPS_STAGE/Sophos/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo PUT file://database.py @STREAMLIT_APPS_STAGE/Sophos/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo. >> upload_shared_files_temp.sql

echo -- Splunk >> upload_shared_files_temp.sql
echo PUT file://utils.py @STREAMLIT_APPS_STAGE/Splunk/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo PUT file://database.py @STREAMLIT_APPS_STAGE/Splunk/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo. >> upload_shared_files_temp.sql

echo -- Symantec >> upload_shared_files_temp.sql
echo PUT file://utils.py @STREAMLIT_APPS_STAGE/Symantec/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo PUT file://database.py @STREAMLIT_APPS_STAGE/Symantec/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo. >> upload_shared_files_temp.sql

echo -- Tenable >> upload_shared_files_temp.sql
echo PUT file://utils.py @STREAMLIT_APPS_STAGE/Tenable/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo PUT file://database.py @STREAMLIT_APPS_STAGE/Tenable/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo. >> upload_shared_files_temp.sql

echo -- Trellix >> upload_shared_files_temp.sql
echo PUT file://utils.py @STREAMLIT_APPS_STAGE/Trellix/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo PUT file://database.py @STREAMLIT_APPS_STAGE/Trellix/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo. >> upload_shared_files_temp.sql

echo -- Zerofox >> upload_shared_files_temp.sql
echo PUT file://utils.py @STREAMLIT_APPS_STAGE/Zerofox/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo PUT file://database.py @STREAMLIT_APPS_STAGE/Zerofox/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo. >> upload_shared_files_temp.sql

echo -- Zscaler >> upload_shared_files_temp.sql
echo PUT file://utils.py @STREAMLIT_APPS_STAGE/Zscaler/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo PUT file://database.py @STREAMLIT_APPS_STAGE/Zscaler/ OVERWRITE=TRUE; >> upload_shared_files_temp.sql
echo. >> upload_shared_files_temp.sql

echo -- List files to verify upload >> upload_shared_files_temp.sql
echo LIST @STREAMLIT_APPS_STAGE; >> upload_shared_files_temp.sql

echo SQL script created: upload_shared_files_temp.sql
echo.
echo ============================================================================
echo Executing SnowSQL with single SSO authentication
echo ============================================================================
echo This will open your browser ONCE for Okta SSO authentication
echo.

"C:\Program Files\Snowflake SnowSQL\snowsql.exe" -a GenericCorp-CRH_EDW -u fuad.onate@CompanyX.com --authenticator externalbrowser -w DEV_WH -d DEV_REPORTING -s SECURITY_ANALYTICS -r DEV_DEVELOPER -f upload_shared_files_temp.sql

echo.
echo ============================================================================
echo Upload Complete
echo ============================================================================
echo Each app now has 4 files:
echo   - streamlit_app.py
echo   - environment.yml
echo   - utils.py [NEW]
echo   - database.py [NEW]
echo ============================================================================
echo.
echo Temporary SQL script: upload_shared_files_temp.sql
echo (You can delete this file after verification)
echo.

pause
