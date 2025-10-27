-- Deploy Remaining 11 Streamlit Apps (Manual)
-- Date: 2025-10-27
-- Target: DEV_REPORTING.SECURITY_ANALYTICS
--
-- IMPORTANT: First upload files to stage, then run CREATE STREAMLIT commands
-- This approach avoids multiple Okta popup windows

USE DATABASE DEV_REPORTING;
USE SCHEMA SECURITY_ANALYTICS;
USE WAREHOUSE DEV_WH;
USE ROLE DEV_DEVELOPER;

-- ============================================================================
-- STEP 1: Upload Files to Stage (Run these PUT commands first)
-- ============================================================================
-- Note: You may need to adjust file paths based on your local setup

-- 8. Proofpoint
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Proofpoint/streamlit_app.py @STREAMLIT_APPS_STAGE/Proofpoint/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Proofpoint/environment.yml @STREAMLIT_APPS_STAGE/Proofpoint/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;

-- 9. Qualys
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Qualys/streamlit_app.py @STREAMLIT_APPS_STAGE/Qualys/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Qualys/environment.yml @STREAMLIT_APPS_STAGE/Qualys/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;

-- 10. SentinelOne
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/SentinelOne/streamlit_app.py @STREAMLIT_APPS_STAGE/SentinelOne/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/SentinelOne/environment.yml @STREAMLIT_APPS_STAGE/SentinelOne/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;

-- 11. ServiceNow
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/ServiceNow/streamlit_app.py @STREAMLIT_APPS_STAGE/ServiceNow/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/ServiceNow/environment.yml @STREAMLIT_APPS_STAGE/ServiceNow/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;

-- 12. Sophos (Recently fixed with all np.random and download button fixes)
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Sophos/streamlit_app.py @STREAMLIT_APPS_STAGE/Sophos/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Sophos/environment.yml @STREAMLIT_APPS_STAGE/Sophos/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;

-- 13. Splunk
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Splunk/streamlit_app.py @STREAMLIT_APPS_STAGE/Splunk/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Splunk/environment.yml @STREAMLIT_APPS_STAGE/Splunk/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;

-- 14. Symantec
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Symantec/streamlit_app.py @STREAMLIT_APPS_STAGE/Symantec/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Symantec/environment.yml @STREAMLIT_APPS_STAGE/Symantec/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;

-- 15. Tenable
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Tenable/streamlit_app.py @STREAMLIT_APPS_STAGE/Tenable/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Tenable/environment.yml @STREAMLIT_APPS_STAGE/Tenable/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;

-- 16. Trellix (Fixed syntax error at line 987)
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Trellix/streamlit_app.py @STREAMLIT_APPS_STAGE/Trellix/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Trellix/environment.yml @STREAMLIT_APPS_STAGE/Trellix/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;

-- 17. Zerofox
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Zerofox/streamlit_app.py @STREAMLIT_APPS_STAGE/Zerofox/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Zerofox/environment.yml @STREAMLIT_APPS_STAGE/Zerofox/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;

-- 18. Zscaler
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Zscaler/streamlit_app.py @STREAMLIT_APPS_STAGE/Zscaler/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Zscaler/environment.yml @STREAMLIT_APPS_STAGE/Zscaler/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;


-- ============================================================================
-- STEP 2: Create/Replace Streamlit Apps (Run after files are uploaded)
-- ============================================================================

-- 8. STREAMLIT_PROOFPOINT
CREATE OR REPLACE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_PROOFPOINT
ROOT_LOCATION = '@DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_APPS_STAGE/Proofpoint'
MAIN_FILE = 'streamlit_app.py'
QUERY_WAREHOUSE = DEV_WH
EXTERNAL_ACCESS_INTEGRATIONS = ()
PACKAGES = ()
COMMENT = 'CPR - Proofpoint Email Security';

-- 9. STREAMLIT_QUALYS
CREATE OR REPLACE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_QUALYS
ROOT_LOCATION = '@DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_APPS_STAGE/Qualys'
MAIN_FILE = 'streamlit_app.py'
QUERY_WAREHOUSE = DEV_WH
EXTERNAL_ACCESS_INTEGRATIONS = ()
PACKAGES = ()
COMMENT = 'CPR - Qualys Vulnerability Management';

-- 10. STREAMLIT_SENTINELONE
CREATE OR REPLACE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_SENTINELONE
ROOT_LOCATION = '@DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_APPS_STAGE/SentinelOne'
MAIN_FILE = 'streamlit_app.py'
QUERY_WAREHOUSE = DEV_WH
EXTERNAL_ACCESS_INTEGRATIONS = ()
PACKAGES = ()
COMMENT = 'CPR - SentinelOne Security Platform';

-- 11. STREAMLIT_SERVICENOW
CREATE OR REPLACE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_SERVICENOW
ROOT_LOCATION = '@DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_APPS_STAGE/ServiceNow'
MAIN_FILE = 'streamlit_app.py'
QUERY_WAREHOUSE = DEV_WH
EXTERNAL_ACCESS_INTEGRATIONS = ()
PACKAGES = ()
COMMENT = 'CPR - ServiceNow Security Operations';

-- 12. STREAMLIT_SOPHOS (Recently fixed - all np.random errors resolved)
CREATE OR REPLACE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_SOPHOS
ROOT_LOCATION = '@DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_APPS_STAGE/Sophos'
MAIN_FILE = 'streamlit_app.py'
QUERY_WAREHOUSE = DEV_WH
EXTERNAL_ACCESS_INTEGRATIONS = ()
PACKAGES = ()
COMMENT = 'CPR - Sophos Security Dashboard';

-- 13. STREAMLIT_SPLUNK
CREATE OR REPLACE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_SPLUNK
ROOT_LOCATION = '@DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_APPS_STAGE/Splunk'
MAIN_FILE = 'streamlit_app.py'
QUERY_WAREHOUSE = DEV_WH
EXTERNAL_ACCESS_INTEGRATIONS = ()
PACKAGES = ()
COMMENT = 'CPR - Splunk Security Analytics';

-- 14. STREAMLIT_SYMANTEC
CREATE OR REPLACE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_SYMANTEC
ROOT_LOCATION = '@DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_APPS_STAGE/Symantec'
MAIN_FILE = 'streamlit_app.py'
QUERY_WAREHOUSE = DEV_WH
EXTERNAL_ACCESS_INTEGRATIONS = ()
PACKAGES = ()
COMMENT = 'CPR - Symantec Endpoint Security Dashboard';

-- 15. STREAMLIT_TENABLE
CREATE OR REPLACE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_TENABLE
ROOT_LOCATION = '@DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_APPS_STAGE/Tenable'
MAIN_FILE = 'streamlit_app.py'
QUERY_WAREHOUSE = DEV_WH
EXTERNAL_ACCESS_INTEGRATIONS = ()
PACKAGES = ()
COMMENT = 'CPR - Tenable Vulnerability Management';

-- 16. STREAMLIT_TRELLIX (FIXED: Syntax error at line 987 - st.metric parameter order)
CREATE OR REPLACE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_TRELLIX
ROOT_LOCATION = '@DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_APPS_STAGE/Trellix'
MAIN_FILE = 'streamlit_app.py'
QUERY_WAREHOUSE = DEV_WH
EXTERNAL_ACCESS_INTEGRATIONS = ()
PACKAGES = ()
COMMENT = 'CPR - Trellix Security Analytics';

-- 17. STREAMLIT_ZEROFOX
CREATE OR REPLACE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_ZEROFOX
ROOT_LOCATION = '@DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_APPS_STAGE/Zerofox'
MAIN_FILE = 'streamlit_app.py'
QUERY_WAREHOUSE = DEV_WH
EXTERNAL_ACCESS_INTEGRATIONS = ()
PACKAGES = ()
COMMENT = 'CPR - ZeroFox Digital Risk Protection';

-- 18. STREAMLIT_ZSCALER
CREATE OR REPLACE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_ZSCALER
ROOT_LOCATION = '@DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_APPS_STAGE/Zscaler'
MAIN_FILE = 'streamlit_app.py'
QUERY_WAREHOUSE = DEV_WH
EXTERNAL_ACCESS_INTEGRATIONS = ()
PACKAGES = ()
COMMENT = 'CPR - Zscaler Cloud Security';


-- ============================================================================
-- STEP 3: Verify Deployment
-- ============================================================================

-- Check all apps are deployed
SHOW STREAMLITS IN SCHEMA DEV_REPORTING.SECURITY_ANALYTICS;

-- Expected: 18 apps with STREAMLIT_* naming
-- All should have CPR - prefix in titles
-- All should have created_on timestamps from today

-- ============================================================================
-- Deployment Summary
-- ============================================================================
-- Already Deployed (7 apps):
--   1. STREAMLIT_ANCON
--   2. STREAMLIT_BITSIGHT
--   3. STREAMLIT_CISCO_AMP
--   4. STREAMLIT_CROWDSTRIKE (Fixed syntax error)
--   5. STREAMLIT_CYBELANGEL
--   6. STREAMLIT_INTEL_THREATS
--   7. STREAMLIT_LEVIAT
--
-- This Script Deploys (11 apps):
--   8. STREAMLIT_PROOFPOINT
--   9. STREAMLIT_QUALYS
--  10. STREAMLIT_SENTINELONE
--  11. STREAMLIT_SERVICENOW
--  12. STREAMLIT_SOPHOS (All np.random fixes applied)
--  13. STREAMLIT_SPLUNK
--  14. STREAMLIT_SYMANTEC
--  15. STREAMLIT_TENABLE
--  16. STREAMLIT_TRELLIX (Fixed syntax error at line 987)
--  17. STREAMLIT_ZEROFOX
--  18. STREAMLIT_ZSCALER
--
-- Total: 18 Streamlit Apps
-- All with CPR - prefix
-- All syntax errors fixed
-- All production-ready
-- ============================================================================
