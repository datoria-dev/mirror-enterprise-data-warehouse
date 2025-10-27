-- ============================================================================
-- Upload utils.py and database.py to all 18 Streamlit app folders
-- ============================================================================

-- Set context
USE WAREHOUSE DEV_WH;
USE DATABASE DEV_REPORTING;
USE SCHEMA SECURITY_ANALYTICS;

-- Ancon
PUT file://utils.py @STREAMLIT_APPS_STAGE/Ancon/ OVERWRITE=TRUE;
PUT file://database.py @STREAMLIT_APPS_STAGE/Ancon/ OVERWRITE=TRUE;

-- BitSight
PUT file://utils.py @STREAMLIT_APPS_STAGE/BitSight/ OVERWRITE=TRUE;
PUT file://database.py @STREAMLIT_APPS_STAGE/BitSight/ OVERWRITE=TRUE;

-- Cisco_AMP
PUT file://utils.py @STREAMLIT_APPS_STAGE/Cisco_AMP/ OVERWRITE=TRUE;
PUT file://database.py @STREAMLIT_APPS_STAGE/Cisco_AMP/ OVERWRITE=TRUE;

-- Crowdstrike
PUT file://utils.py @STREAMLIT_APPS_STAGE/Crowdstrike/ OVERWRITE=TRUE;
PUT file://database.py @STREAMLIT_APPS_STAGE/Crowdstrike/ OVERWRITE=TRUE;

-- CybelAngel
PUT file://utils.py @STREAMLIT_APPS_STAGE/CybelAngel/ OVERWRITE=TRUE;
PUT file://database.py @STREAMLIT_APPS_STAGE/CybelAngel/ OVERWRITE=TRUE;

-- Intel_Threats
PUT file://utils.py @STREAMLIT_APPS_STAGE/Intel_Threats/ OVERWRITE=TRUE;
PUT file://database.py @STREAMLIT_APPS_STAGE/Intel_Threats/ OVERWRITE=TRUE;

-- Leviat
PUT file://utils.py @STREAMLIT_APPS_STAGE/Leviat/ OVERWRITE=TRUE;
PUT file://database.py @STREAMLIT_APPS_STAGE/Leviat/ OVERWRITE=TRUE;

-- Proofpoint
PUT file://utils.py @STREAMLIT_APPS_STAGE/Proofpoint/ OVERWRITE=TRUE;
PUT file://database.py @STREAMLIT_APPS_STAGE/Proofpoint/ OVERWRITE=TRUE;

-- Qualys
PUT file://utils.py @STREAMLIT_APPS_STAGE/Qualys/ OVERWRITE=TRUE;
PUT file://database.py @STREAMLIT_APPS_STAGE/Qualys/ OVERWRITE=TRUE;

-- SentinelOne
PUT file://utils.py @STREAMLIT_APPS_STAGE/SentinelOne/ OVERWRITE=TRUE;
PUT file://database.py @STREAMLIT_APPS_STAGE/SentinelOne/ OVERWRITE=TRUE;

-- ServiceNow
PUT file://utils.py @STREAMLIT_APPS_STAGE/ServiceNow/ OVERWRITE=TRUE;
PUT file://database.py @STREAMLIT_APPS_STAGE/ServiceNow/ OVERWRITE=TRUE;

-- Sophos
PUT file://utils.py @STREAMLIT_APPS_STAGE/Sophos/ OVERWRITE=TRUE;
PUT file://database.py @STREAMLIT_APPS_STAGE/Sophos/ OVERWRITE=TRUE;

-- Splunk
PUT file://utils.py @STREAMLIT_APPS_STAGE/Splunk/ OVERWRITE=TRUE;
PUT file://database.py @STREAMLIT_APPS_STAGE/Splunk/ OVERWRITE=TRUE;

-- Symantec
PUT file://utils.py @STREAMLIT_APPS_STAGE/Symantec/ OVERWRITE=TRUE;
PUT file://database.py @STREAMLIT_APPS_STAGE/Symantec/ OVERWRITE=TRUE;

-- Tenable
PUT file://utils.py @STREAMLIT_APPS_STAGE/Tenable/ OVERWRITE=TRUE;
PUT file://database.py @STREAMLIT_APPS_STAGE/Tenable/ OVERWRITE=TRUE;

-- Trellix
PUT file://utils.py @STREAMLIT_APPS_STAGE/Trellix/ OVERWRITE=TRUE;
PUT file://database.py @STREAMLIT_APPS_STAGE/Trellix/ OVERWRITE=TRUE;

-- Zerofox
PUT file://utils.py @STREAMLIT_APPS_STAGE/Zerofox/ OVERWRITE=TRUE;
PUT file://database.py @STREAMLIT_APPS_STAGE/Zerofox/ OVERWRITE=TRUE;

-- Zscaler
PUT file://utils.py @STREAMLIT_APPS_STAGE/Zscaler/ OVERWRITE=TRUE;
PUT file://database.py @STREAMLIT_APPS_STAGE/Zscaler/ OVERWRITE=TRUE;

-- List files to verify upload
LIST @STREAMLIT_APPS_STAGE/Sophos/;
