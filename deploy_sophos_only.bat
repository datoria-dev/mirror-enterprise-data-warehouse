@echo off
REM ================================================================
REM Deploy Sophos App Only (Quick Fix Test)
REM ================================================================

cd /d "%~dp0"

echo.
echo ========================================
echo Deploy Sophos App Only
echo ========================================
echo.

echo [Step 1/2] Creating deployment SQL script...

python -c "
import json
from pathlib import Path

# Load config
with open('snowflake_config.json') as f:
    config = json.load(f)

# Create SQL script
sql_lines = [
    '-- Deploy Sophos App Only',
    '-- Database: DEV_REPORTING.SECURITY_ANALYTICS',
    '',
    'USE ROLE DEV_DEVELOPER;',
    f\"USE WAREHOUSE {config['warehouse']};\",
    f\"USE DATABASE {config['database']};\",
    f\"USE SCHEMA {config['schema']};\",
    '',
    '-- Create stage if not exists',
    'CREATE STAGE IF NOT EXISTS STREAMLIT_APPS_STAGE;',
    '',
    '-- Upload Sophos files',
    \"PUT 'file://13_STREAMLIT_COMPLETE/Sophos/streamlit_app.py' @STREAMLIT_APPS_STAGE/Sophos/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;\",
    \"PUT 'file://13_STREAMLIT_COMPLETE/Sophos/environment.yml' @STREAMLIT_APPS_STAGE/Sophos/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;\",
    '',
    '-- Drop and recreate Sophos app',
    'DROP STREAMLIT IF EXISTS STREAMLIT_SOPHOS;',
    '',
    'CREATE STREAMLIT STREAMLIT_SOPHOS',
    '  ROOT_LOCATION = @STREAMLIT_APPS_STAGE',
    '  MAIN_FILE = \"/Sophos/streamlit_app.py\"',
    '  QUERY_WAREHOUSE = \"DEV_WH\";',
    '',
    'SELECT ''Sophos deployed successfully'' AS STATUS;'
]

# Write to file
Path('deployment_logs').mkdir(exist_ok=True)
script_file = 'deployment_logs/deploy_sophos.sql'
with open(script_file, 'w') as f:
    f.write('\n'.join(sql_lines))

print(f'SQL script created: {script_file}')
"

echo.
echo [Step 2/2] Executing deployment...
echo.
echo NOTE: Browser will open for SSO authentication (Okta)
echo.

"C:\Program Files\Snowflake SnowSQL\snowsql.exe" ^
    -a GenericCorp-CRH_EDW ^
    -u fuad.onate@CompanyX.com ^
    --authenticator externalbrowser ^
    -f deployment_logs/deploy_sophos.sql

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Test in Snowflake:
echo 1. Go to Snowflake UI
echo 2. Navigate to DEV_REPORTING -^> SECURITY_ANALYTICS -^> Streamlit
echo 3. Open STREAMLIT_SOPHOS
echo 4. Add/remove filters and refresh
echo 5. Should NOT show random.gauss error
echo.
pause
