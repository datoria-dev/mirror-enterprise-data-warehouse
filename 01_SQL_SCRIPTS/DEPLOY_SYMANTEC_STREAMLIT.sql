/*
================================================================================
DEPLOY SYMANTEC STREAMLIT APP
================================================================================
Description: Deploy or update the Symantec EDR Dashboard Streamlit app
Author: Claude Code
Date: 2025-01-25

Features included:
- 3 Download buttons (Coverage, Health Status, Critical Endpoints)
- 4 Alert thresholds (Coverage warnings, Critical endpoint alerts)
- Refresh functionality (manual + auto)
- Snowflake Streamlit compatibility (@st.cache_data pattern)

Prerequisites:
1. Streamlit stage must exist
2. COMPUTE_WH warehouse must be available
3. File must be uploaded to stage first
================================================================================
*/

-- Use the correct database and schema
USE DATABASE ITSECKPI_DB;
USE SCHEMA ITSECKPI_SCHEMA;

-- Step 1: Create stage if it doesn't exist
CREATE STAGE IF NOT EXISTS STREAMLIT_APPS_STAGE
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Stage for SECURITY_ANALYTICS Streamlit applications';

-- Step 2: List files currently in Symantec folder (for verification)
LIST @STREAMLIT_APPS_STAGE/Symantec/;

-- Step 3: Upload the Streamlit app file
-- NOTE: This command needs to be run from SnowSQL or Snowflake UI, not from this script
-- PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Symantec/streamlit_app.py
--     @ITSECKPI_DB.ITSECKPI_SCHEMA.STREAMLIT_APPS_STAGE/Symantec/
--     OVERWRITE=TRUE
--     AUTO_COMPRESS=FALSE;

-- Step 4: Drop existing Streamlit app if it exists
DROP STREAMLIT IF EXISTS STREAMLIT_SYMANTEC;

-- Step 5: Create the Streamlit app
CREATE STREAMLIT STREAMLIT_SYMANTEC
    ROOT_LOCATION = '@ITSECKPI_DB.ITSECKPI_SCHEMA.STREAMLIT_APPS_STAGE/Symantec'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = 'COMPUTE_WH'
    COMMENT = 'Symantec EDR Dashboard - Endpoint Protection & Response monitoring';

-- Step 6: Grant permissions (adjust roles as needed)
-- GRANT USAGE ON STREAMLIT STREAMLIT_SYMANTEC TO ROLE ITSECKPI_ROLE;

-- Step 7: Show the Streamlit app details
SHOW STREAMLITS LIKE 'STREAMLIT_SYMANTEC';

-- Step 8: Get the Streamlit URL
SELECT
    'https://' || CURRENT_ACCOUNT() || '.snowflakecomputing.com/streamlit/' ||
    CURRENT_DATABASE() || '/' || CURRENT_SCHEMA() || '/STREAMLIT_SYMANTEC' AS STREAMLIT_URL;

/*
================================================================================
MANUAL DEPLOYMENT STEPS
================================================================================

1. Open SnowSQL or Snowflake Worksheets

2. Upload the file using PUT command:

   PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Symantec/streamlit_app.py
       @ITSECKPI_DB.ITSECKPI_SCHEMA.STREAMLIT_APPS_STAGE/Symantec/
       OVERWRITE=TRUE
       AUTO_COMPRESS=FALSE;

3. Run this script to create/update the Streamlit app

4. Access the app via the URL provided by the last SELECT statement

5. Test the following features:
   - Tab 1: Coverage Overview
     ✓ Download Coverage CSV button
     ✓ Coverage alert (red/orange/green based on percentage)

   - Tab 2: Endpoint Health
     ✓ Download Health Status CSV button

   - Tab 3: High Risk
     ✓ Download Critical Endpoints CSV button
     ✓ Critical endpoints alert (red/orange/green based on count)

   - Sidebar:
     ✓ Refresh Now button
     ✓ Auto-refresh checkbox

================================================================================
TROUBLESHOOTING
================================================================================

If the app doesn't update:
1. Verify file was uploaded: LIST @STREAMLIT_APPS_STAGE/Symantec/;
2. Check file size is > 0
3. Try refreshing: ALTER STREAMLIT STREAMLIT_SYMANTEC REFRESH;
4. Check warehouse is running: SHOW WAREHOUSES LIKE 'COMPUTE_WH';

If download buttons don't work:
1. Check browser console for errors
2. Verify @st.cache_data is present in code
3. Try in incognito/private mode
4. Clear Streamlit cache in app sidebar

================================================================================
*/
