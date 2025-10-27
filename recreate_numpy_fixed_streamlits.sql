-- ============================================================================
-- Recreate Streamlit Objects for Numpy-Fixed Apps
-- This forces Snowflake to reload the updated streamlit_app.py files
-- ============================================================================

USE WAREHOUSE DEV_WH;
USE DATABASE DEV_REPORTING;
USE SCHEMA SECURITY_ANALYTICS;

-- 1. Ancon
CREATE OR REPLACE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_ANCON
ROOT_LOCATION = '@DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_APPS_STAGE/Ancon/'
MAIN_FILE = 'streamlit_app.py'
QUERY_WAREHOUSE = 'DEV_WH'
TITLE = 'CPR - Ancon Security Dashboard'
COMMENT = 'CPR - Ancon security monitoring and compliance dashboard';

-- 2. Cisco_AMP
CREATE OR REPLACE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_CISCO_AMP
ROOT_LOCATION = '@DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_APPS_STAGE/Cisco_AMP/'
MAIN_FILE = 'streamlit_app.py'
QUERY_WAREHOUSE = 'DEV_WH'
TITLE = 'CPR - Cisco AMP Dashboard'
COMMENT = 'CPR - Cisco Advanced Malware Protection monitoring dashboard';

-- 3. Intel_Threats
CREATE OR REPLACE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_INTEL_THREATS
ROOT_LOCATION = '@DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_APPS_STAGE/Intel_Threats/'
MAIN_FILE = 'streamlit_app.py'
QUERY_WAREHOUSE = 'DEV_WH'
TITLE = 'CPR - Threat Intelligence Dashboard'
COMMENT = 'CPR - Threat intelligence and security analysis dashboard';

-- 4. Qualys
CREATE OR REPLACE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_QUALYS
ROOT_LOCATION = '@DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_APPS_STAGE/Qualys/'
MAIN_FILE = 'streamlit_app.py'
QUERY_WAREHOUSE = 'DEV_WH'
TITLE = 'CPR - Qualys Vulnerability Dashboard'
COMMENT = 'CPR - Qualys vulnerability management and scanning dashboard';

-- 5. Splunk
CREATE OR REPLACE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_SPLUNK
ROOT_LOCATION = '@DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_APPS_STAGE/Splunk/'
MAIN_FILE = 'streamlit_app.py'
QUERY_WAREHOUSE = 'DEV_WH'
TITLE = 'CPR - Splunk SIEM Dashboard'
COMMENT = 'CPR - Splunk security information and event management dashboard';

-- 6. Symantec
CREATE OR REPLACE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_SYMANTEC
ROOT_LOCATION = '@DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_APPS_STAGE/Symantec/'
MAIN_FILE = 'streamlit_app.py'
QUERY_WAREHOUSE = 'DEV_WH'
TITLE = 'CPR - Symantec Endpoint Dashboard'
COMMENT = 'CPR - Symantec endpoint protection and security dashboard';

-- 7. Trellix
CREATE OR REPLACE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_TRELLIX
ROOT_LOCATION = '@DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_APPS_STAGE/Trellix/'
MAIN_FILE = 'streamlit_app.py'
QUERY_WAREHOUSE = 'DEV_WH'
TITLE = 'CPR - Trellix EDR Dashboard'
COMMENT = 'CPR - Trellix endpoint detection and response dashboard';

-- 8. Zerofox
CREATE OR REPLACE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_ZEROFOX
ROOT_LOCATION = '@DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_APPS_STAGE/Zerofox/'
MAIN_FILE = 'streamlit_app.py'
QUERY_WAREHOUSE = 'DEV_WH'
TITLE = 'CPR - ZeroFox Threat Intelligence Dashboard'
COMMENT = 'CPR - ZeroFox external threat intelligence and digital risk protection dashboard';

-- 9. Zscaler
CREATE OR REPLACE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_ZSCALER
ROOT_LOCATION = '@DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_APPS_STAGE/Zscaler/'
MAIN_FILE = 'streamlit_app.py'
QUERY_WAREHOUSE = 'DEV_WH'
TITLE = 'CPR - Zscaler Cloud Security Dashboard'
COMMENT = 'CPR - Zscaler cloud security and web gateway dashboard';

-- Verification: Show all Streamlit apps
SHOW STREAMLITS IN SCHEMA DEV_REPORTING.SECURITY_ANALYTICS;
