-- ============================================================================
-- Upload Numpy-Fixed Apps to Snowflake Stage
-- Apps: Ancon, Cisco_AMP, Intel_Threats, Qualys, Splunk, Symantec, Trellix, Zerofox, Zscaler
-- ============================================================================

USE WAREHOUSE DEV_WH;
USE DATABASE DEV_REPORTING;
USE SCHEMA SECURITY_ANALYTICS;

-- Ancon
PUT file://13_STREAMLIT_COMPLETE/Ancon/streamlit_app.py @STREAMLIT_APPS_STAGE/Ancon/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

-- Cisco_AMP
PUT file://13_STREAMLIT_COMPLETE/Cisco_AMP/streamlit_app.py @STREAMLIT_APPS_STAGE/Cisco_AMP/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

-- Intel_Threats
PUT file://13_STREAMLIT_COMPLETE/Intel_Threats/streamlit_app.py @STREAMLIT_APPS_STAGE/Intel_Threats/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

-- Qualys
PUT file://13_STREAMLIT_COMPLETE/Qualys/streamlit_app.py @STREAMLIT_APPS_STAGE/Qualys/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

-- Splunk
PUT file://13_STREAMLIT_COMPLETE/Splunk/streamlit_app.py @STREAMLIT_APPS_STAGE/Splunk/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

-- Symantec
PUT file://13_STREAMLIT_COMPLETE/Symantec/streamlit_app.py @STREAMLIT_APPS_STAGE/Symantec/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

-- Trellix
PUT file://13_STREAMLIT_COMPLETE/Trellix/streamlit_app.py @STREAMLIT_APPS_STAGE/Trellix/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

-- Zerofox
PUT file://13_STREAMLIT_COMPLETE/Zerofox/streamlit_app.py @STREAMLIT_APPS_STAGE/Zerofox/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

-- Zscaler
PUT file://13_STREAMLIT_COMPLETE/Zscaler/streamlit_app.py @STREAMLIT_APPS_STAGE/Zscaler/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

-- Verify uploads
LIST @STREAMLIT_APPS_STAGE/Trellix/;
