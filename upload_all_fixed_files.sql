-- Upload All Fixed Streamlit App Files to Stage
-- Date: 2025-10-27
-- All files uploaded in single SnowSQL session (only 1 Okta login)

USE DATABASE DEV_REPORTING;
USE SCHEMA SECURITY_ANALYTICS;
USE WAREHOUSE DEV_WH;
USE ROLE DEV_DEVELOPER;

-- Upload all streamlit_app.py files (with CPR prefix and syntax fixes)
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Ancon/streamlit_app.py @STREAMLIT_APPS_STAGE/Ancon/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/BitSight/streamlit_app.py @STREAMLIT_APPS_STAGE/BitSight/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Cisco_AMP/streamlit_app.py @STREAMLIT_APPS_STAGE/Cisco_AMP/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Crowdstrike/streamlit_app.py @STREAMLIT_APPS_STAGE/Crowdstrike/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/CybelAngel/streamlit_app.py @STREAMLIT_APPS_STAGE/CybelAngel/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Intel_Threats/streamlit_app.py @STREAMLIT_APPS_STAGE/Intel_Threats/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Leviat/streamlit_app.py @STREAMLIT_APPS_STAGE/Leviat/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Proofpoint/streamlit_app.py @STREAMLIT_APPS_STAGE/Proofpoint/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Qualys/streamlit_app.py @STREAMLIT_APPS_STAGE/Qualys/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/SentinelOne/streamlit_app.py @STREAMLIT_APPS_STAGE/SentinelOne/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/ServiceNow/streamlit_app.py @STREAMLIT_APPS_STAGE/ServiceNow/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Sophos/streamlit_app.py @STREAMLIT_APPS_STAGE/Sophos/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Splunk/streamlit_app.py @STREAMLIT_APPS_STAGE/Splunk/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Symantec/streamlit_app.py @STREAMLIT_APPS_STAGE/Symantec/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Tenable/streamlit_app.py @STREAMLIT_APPS_STAGE/Tenable/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Trellix/streamlit_app.py @STREAMLIT_APPS_STAGE/Trellix/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Zerofox/streamlit_app.py @STREAMLIT_APPS_STAGE/Zerofox/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Zscaler/streamlit_app.py @STREAMLIT_APPS_STAGE/Zscaler/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
