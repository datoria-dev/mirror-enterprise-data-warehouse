-- =====================================================================
-- DATA PIPELINE - ACCOUNTADMIN REQUIRED OBJECTS
-- =====================================================================
-- Purpose: Pipeline objects that REQUIRE ACCOUNTADMIN role
-- Author: Data Engineering Team
-- Date: 2025-10-08
-- Prerequisites: PIPELINE_DEV_DEVELOPER_ONLY.sql must be executed first
-- =====================================================================
-- IMPORTANT: This script must be run by a user with ACCOUNTADMIN role
-- =====================================================================

USE ROLE ACCOUNTADMIN;
USE WAREHOUSE DEV_WH;

-- =====================================================================
-- SECTION 1: CLOUD STORAGE INTEGRATIONS
-- =====================================================================
-- Storage integrations can ONLY be created by ACCOUNTADMIN

-- S3 Integration for EDR platforms (CrowdStrike, SentinelOne, Defender)
CREATE OR REPLACE STORAGE INTEGRATION S3_EDR_INTEGRATION
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = S3
    ENABLED = TRUE
    STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::123456789012:role/snowflake-edr-role'
    STORAGE_ALLOWED_LOCATIONS = (
        's3://GenericCorp-security-data/edr/crowdstrike/',
        's3://GenericCorp-security-data/edr/sentinelone/',
        's3://GenericCorp-security-data/edr/defender/',
        's3://GenericCorp-security-data/edr/cisco-amp/'
    )
    COMMENT = 'S3 integration for EDR platform data ingestion';

-- Get IAM user details for AWS trust policy configuration
DESC STORAGE INTEGRATION S3_EDR_INTEGRATION;
-- Note: Copy STORAGE_AWS_IAM_USER_ARN and STORAGE_AWS_EXTERNAL_ID
-- Update AWS IAM Trust Policy with these values

-- S3 Integration for vulnerability scanning (Qualys)
CREATE OR REPLACE STORAGE INTEGRATION S3_VULN_INTEGRATION
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = S3
    ENABLED = TRUE
    STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::123456789012:role/snowflake-vuln-role'
    STORAGE_ALLOWED_LOCATIONS = (
        's3://GenericCorp-security-data/qualys/scans/',
        's3://GenericCorp-security-data/qualys/agents/'
    )
    COMMENT = 'S3 integration for Qualys vulnerability data';

DESC STORAGE INTEGRATION S3_VULN_INTEGRATION;

-- Azure Integration for email security (Proofpoint)
CREATE OR REPLACE STORAGE INTEGRATION AZURE_EMAIL_INTEGRATION
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = AZURE
    ENABLED = TRUE
    AZURE_TENANT_ID = 'your-tenant-id-here' -- REPLACE WITH ACTUAL TENANT ID
    STORAGE_ALLOWED_LOCATIONS = (
        'azure://crhsecuritydata.blob.core.windows.net/proofpoint/'
    )
    COMMENT = 'Azure Blob integration for Proofpoint email logs';

DESC STORAGE INTEGRATION AZURE_EMAIL_INTEGRATION;
-- Note: Copy AZURE_CONSENT_URL and grant consent in Azure portal

-- S3 Integration for SIEM logs (Splunk)
CREATE OR REPLACE STORAGE INTEGRATION S3_SIEM_INTEGRATION
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = S3
    ENABLED = TRUE
    STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::123456789012:role/snowflake-siem-role'
    STORAGE_ALLOWED_LOCATIONS = (
        's3://GenericCorp-security-data/splunk/alerts/',
        's3://GenericCorp-security-data/splunk/events/',
        's3://GenericCorp-security-data/servicenow/incidents/',
        's3://GenericCorp-security-data/archer/exports/',
        's3://GenericCorp-security-data/metacompliance/training/'
    )
    COMMENT = 'S3 integration for Splunk SIEM data and batch sources';

DESC STORAGE INTEGRATION S3_SIEM_INTEGRATION;

-- =====================================================================
-- SECTION 2: EXTERNAL STAGES
-- =====================================================================
-- Grant usage on storage integrations to DEV_DEVELOPER role

GRANT USAGE ON INTEGRATION S3_EDR_INTEGRATION TO ROLE DEV_DEVELOPER;
GRANT USAGE ON INTEGRATION S3_VULN_INTEGRATION TO ROLE DEV_DEVELOPER;
GRANT USAGE ON INTEGRATION AZURE_EMAIL_INTEGRATION TO ROLE DEV_DEVELOPER;
GRANT USAGE ON INTEGRATION S3_SIEM_INTEGRATION TO ROLE DEV_DEVELOPER;

-- Switch to DEV_DEVELOPER to create stages (best practice: non-admin creates stages)
USE ROLE DEV_DEVELOPER;
USE SCHEMA DEV_LANDING.SECURITY_ANALYTICS;

-- External stage for CrowdStrike EDR
CREATE OR REPLACE STAGE STG_CROWDSTRIKE_EDR
    STORAGE_INTEGRATION = S3_EDR_INTEGRATION
    URL = 's3://GenericCorp-security-data/edr/crowdstrike/'
    FILE_FORMAT = JSON_EDR_FORMAT
    COMMENT = 'Stage for CrowdStrike detection events';

-- External stage for SentinelOne
CREATE OR REPLACE STAGE STG_SENTINELONE_EDR
    STORAGE_INTEGRATION = S3_EDR_INTEGRATION
    URL = 's3://GenericCorp-security-data/edr/sentinelone/'
    FILE_FORMAT = JSON_EDR_FORMAT
    COMMENT = 'Stage for SentinelOne threat events';

-- External stage for Qualys scans
CREATE OR REPLACE STAGE STG_QUALYS_SCANS
    STORAGE_INTEGRATION = S3_VULN_INTEGRATION
    URL = 's3://GenericCorp-security-data/qualys/scans/'
    FILE_FORMAT = CSV_QUALYS_FORMAT
    COMMENT = 'Stage for Qualys vulnerability scan results';

-- External stage for Proofpoint
CREATE OR REPLACE STAGE STG_PROOFPOINT_LOGS
    STORAGE_INTEGRATION = AZURE_EMAIL_INTEGRATION
    URL = 'azure://crhsecuritydata.blob.core.windows.net/proofpoint/'
    FILE_FORMAT = JSON_PROOFPOINT_FORMAT
    COMMENT = 'Stage for Proofpoint email message logs';

-- External stage for Splunk
CREATE OR REPLACE STAGE STG_SPLUNK_ALERTS
    STORAGE_INTEGRATION = S3_SIEM_INTEGRATION
    URL = 's3://GenericCorp-security-data/splunk/alerts/'
    FILE_FORMAT = PARQUET_SPLUNK_FORMAT
    COMMENT = 'Stage for Splunk security alerts';

-- External stage for ServiceNow exports
CREATE OR REPLACE STAGE STG_SERVICENOW_EXPORTS
    STORAGE_INTEGRATION = S3_SIEM_INTEGRATION
    URL = 's3://GenericCorp-security-data/servicenow/incidents/'
    FILE_FORMAT = CSV_SERVICENOW_FORMAT
    COMMENT = 'Stage for ServiceNow incident exports';

-- External stage for RSA Archer exports
CREATE OR REPLACE STAGE STG_ARCHER_EXPORTS
    STORAGE_INTEGRATION = S3_SIEM_INTEGRATION
    URL = 's3://GenericCorp-security-data/archer/exports/'
    FILE_FORMAT = CSV_ARCHER_FORMAT
    COMMENT = 'Stage for RSA Archer GRC exports';

-- External stage for MetaCompliance exports
CREATE OR REPLACE STAGE STG_METACOMPLIANCE_EXPORTS
    STORAGE_INTEGRATION = S3_SIEM_INTEGRATION
    URL = 's3://GenericCorp-security-data/metacompliance/training/'
    FILE_FORMAT = CSV_METACOMPLIANCE_FORMAT
    COMMENT = 'Stage for MetaCompliance training exports';

-- =====================================================================
-- SECTION 3: VERIFY STAGE ACCESS
-- =====================================================================
-- Test that stages can list files (will be empty if no data uploaded yet)

LIST @STG_CROWDSTRIKE_EDR;
LIST @STG_SENTINELONE_EDR;
LIST @STG_QUALYS_SCANS;
LIST @STG_PROOFPOINT_LOGS;
LIST @STG_SPLUNK_ALERTS;
LIST @STG_SERVICENOW_EXPORTS;
LIST @STG_ARCHER_EXPORTS;
LIST @STG_METACOMPLIANCE_EXPORTS;

-- =====================================================================
-- SECTION 4: SNOWPIPE DEFINITIONS (AUTO-INGEST)
-- =====================================================================

USE SCHEMA DEV_LANDING.SECURITY_ANALYTICS;

-- Snowpipe for CrowdStrike
CREATE OR REPLACE PIPE PIPE_CROWDSTRIKE_EDR
    AUTO_INGEST = TRUE
    AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:123456789012:snowpipe-crowdstrike'
AS
    COPY INTO L_CROWDSTRIKE_RAW (
        SOURCE_FILE_NAME,
        SOURCE_FILE_ROW_NUMBER,
        RAW_DATA,
        METADATA
    )
    FROM (
        SELECT
            METADATA$FILENAME,
            METADATA$FILE_ROW_NUMBER,
            $1,
            OBJECT_CONSTRUCT(
                'INGESTED_BY', 'SNOWPIPE',
                'PIPE_NAME', 'PIPE_CROWDSTRIKE_EDR',
                'FILE_SIZE_BYTES', METADATA$FILE_CONTENT_KEY,
                'FILE_LAST_MODIFIED', METADATA$FILE_LAST_MODIFIED
            )
        FROM @STG_CROWDSTRIKE_EDR
    )
    FILE_FORMAT = JSON_EDR_FORMAT
    ON_ERROR = CONTINUE
    COMMENT = 'Auto-ingest pipe for CrowdStrike EDR events';

-- Get SQS queue ARN for SNS subscription
SHOW PIPES LIKE 'PIPE_CROWDSTRIKE_EDR';
DESC PIPE PIPE_CROWDSTRIKE_EDR;
-- Note: Copy notification_channel value for SNS subscription

-- Snowpipe for SentinelOne
CREATE OR REPLACE PIPE PIPE_SENTINELONE_EDR
    AUTO_INGEST = TRUE
    AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:123456789012:snowpipe-sentinelone'
AS
    COPY INTO L_SENTINELONE_RAW (
        SOURCE_FILE_NAME,
        SOURCE_FILE_ROW_NUMBER,
        RAW_DATA,
        METADATA
    )
    FROM (
        SELECT
            METADATA$FILENAME,
            METADATA$FILE_ROW_NUMBER,
            $1,
            OBJECT_CONSTRUCT(
                'INGESTED_BY', 'SNOWPIPE',
                'PIPE_NAME', 'PIPE_SENTINELONE_EDR',
                'FILE_SIZE_BYTES', METADATA$FILE_CONTENT_KEY,
                'FILE_LAST_MODIFIED', METADATA$FILE_LAST_MODIFIED
            )
        FROM @STG_SENTINELONE_EDR
    )
    FILE_FORMAT = JSON_EDR_FORMAT
    ON_ERROR = CONTINUE
    COMMENT = 'Auto-ingest pipe for SentinelOne threat events';

DESC PIPE PIPE_SENTINELONE_EDR;

-- Snowpipe for Qualys
CREATE OR REPLACE PIPE PIPE_QUALYS_SCANS
    AUTO_INGEST = TRUE
    AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:123456789012:snowpipe-qualys'
AS
    COPY INTO L_QUALYS_SCANS_RAW (
        SOURCE_FILE_NAME,
        SOURCE_FILE_ROW_NUMBER,
        QID,
        HOST_ID,
        IP_ADDRESS,
        DNS_NAME,
        SEVERITY,
        CVSS_SCORE,
        FIRST_DETECTED,
        LAST_DETECTED,
        STATUS,
        RAW_DATA
    )
    FROM (
        SELECT
            METADATA$FILENAME,
            METADATA$FILE_ROW_NUMBER,
            $1, -- QID
            $2, -- HOST_ID
            $3, -- IP_ADDRESS
            $4, -- DNS_NAME
            $5, -- SEVERITY
            $6, -- CVSS_SCORE
            $7, -- FIRST_DETECTED
            $8, -- LAST_DETECTED
            $9, -- STATUS
            OBJECT_CONSTRUCT(
                'PORT', $10,
                'PROTOCOL', $11,
                'SERVICE', $12
            )
        FROM @STG_QUALYS_SCANS
    )
    FILE_FORMAT = CSV_QUALYS_FORMAT
    ON_ERROR = CONTINUE
    COMMENT = 'Auto-ingest pipe for Qualys vulnerability scans';

DESC PIPE PIPE_QUALYS_SCANS;

-- Snowpipe for Proofpoint (Azure Event Grid)
CREATE OR REPLACE PIPE PIPE_PROOFPOINT_LOGS
    AUTO_INGEST = TRUE
    INTEGRATION = 'AZURE_EMAIL_INTEGRATION'
AS
    COPY INTO L_PROOFPOINT_RAW (
        SOURCE_FILE_NAME,
        SOURCE_FILE_ROW_NUMBER,
        MESSAGE_ID,
        MESSAGE_TIME,
        SENDER,
        RECIPIENT,
        SUBJECT,
        THREAT_TYPE,
        RAW_DATA
    )
    FROM (
        SELECT
            METADATA$FILENAME,
            METADATA$FILE_ROW_NUMBER,
            $1:messageId::VARCHAR,
            $1:messageTime::TIMESTAMP_NTZ,
            $1:sender::VARCHAR,
            $1:recipient::VARCHAR,
            $1:subject::VARCHAR,
            $1:threatType::VARCHAR,
            $1
        FROM @STG_PROOFPOINT_LOGS
    )
    FILE_FORMAT = JSON_PROOFPOINT_FORMAT
    ON_ERROR = CONTINUE
    COMMENT = 'Auto-ingest pipe for Proofpoint email message logs';

DESC PIPE PIPE_PROOFPOINT_LOGS;
-- Note: For Azure, copy notification_channel for Event Grid subscription

-- Snowpipe for Splunk
CREATE OR REPLACE PIPE PIPE_SPLUNK_ALERTS
    AUTO_INGEST = TRUE
    AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:123456789012:snowpipe-splunk'
AS
    COPY INTO L_SPLUNK_ALERTS_RAW (
        SOURCE_FILE_NAME,
        ALERT_ID,
        ALERT_TIME,
        ALERT_NAME,
        SEVERITY,
        SOURCE_IP,
        DESTINATION_IP,
        RAW_DATA
    )
    FROM (
        SELECT
            METADATA$FILENAME,
            $1:alert_id::VARCHAR,
            $1:timestamp::TIMESTAMP_NTZ,
            $1:alert_name::VARCHAR,
            $1:severity::VARCHAR,
            $1:src_ip::VARCHAR,
            $1:dest_ip::VARCHAR,
            $1
        FROM @STG_SPLUNK_ALERTS
    )
    FILE_FORMAT = PARQUET_SPLUNK_FORMAT
    ON_ERROR = CONTINUE
    COMMENT = 'Auto-ingest pipe for Splunk security alerts';

DESC PIPE PIPE_SPLUNK_ALERTS;

-- =====================================================================
-- SECTION 5: EXTERNAL TABLES (BATCH SOURCES)
-- =====================================================================

USE SCHEMA DEV_LANDING.SECURITY_ANALYTICS;

-- ServiceNow incident exports (daily batch)
CREATE OR REPLACE EXTERNAL TABLE EXT_SERVICENOW_INCIDENTS (
    INCIDENT_ID VARCHAR AS (VALUE:c1::VARCHAR),
    INCIDENT_NUMBER VARCHAR AS (VALUE:c2::VARCHAR),
    OPENED_AT TIMESTAMP_NTZ AS (VALUE:c3::TIMESTAMP_NTZ),
    CLOSED_AT TIMESTAMP_NTZ AS (VALUE:c4::TIMESTAMP_NTZ),
    PRIORITY VARCHAR AS (VALUE:c5::VARCHAR),
    CATEGORY VARCHAR AS (VALUE:c6::VARCHAR),
    ASSIGNED_TO VARCHAR AS (VALUE:c7::VARCHAR),
    SHORT_DESCRIPTION VARCHAR AS (VALUE:c8::VARCHAR),
    STATE VARCHAR AS (VALUE:c9::VARCHAR),
    RESOLUTION_CODE VARCHAR AS (VALUE:c10::VARCHAR)
)
LOCATION = @STG_SERVICENOW_EXPORTS
FILE_FORMAT = CSV_SERVICENOW_FORMAT
AUTO_REFRESH = TRUE
REFRESH_ON_CREATE = TRUE
COMMENT = 'External table for ServiceNow incident exports - refreshed daily';

-- RSA Archer GRC exports (daily batch)
CREATE OR REPLACE EXTERNAL TABLE EXT_ARCHER_MATURITY (
    ASSESSMENT_ID VARCHAR AS (VALUE:c1::VARCHAR),
    ASSESSMENT_DATE DATE AS (VALUE:c2::DATE),
    OPCO_ID VARCHAR AS (VALUE:c3::VARCHAR),
    NIST_FUNCTION VARCHAR AS (VALUE:c4::VARCHAR),
    MATURITY_LEVEL NUMBER AS (VALUE:c5::NUMBER),
    SCORE NUMBER AS (VALUE:c6::NUMBER),
    COMMENTS VARCHAR AS (VALUE:c7::VARCHAR)
)
LOCATION = @STG_ARCHER_EXPORTS
FILE_FORMAT = CSV_ARCHER_FORMAT
AUTO_REFRESH = TRUE
REFRESH_ON_CREATE = TRUE
COMMENT = 'External table for RSA Archer maturity assessments - refreshed daily';

-- MetaCompliance awareness training (daily batch)
CREATE OR REPLACE EXTERNAL TABLE EXT_METACOMPLIANCE_TRAINING (
    USER_EMAIL VARCHAR AS (VALUE:c1::VARCHAR),
    COURSE_NAME VARCHAR AS (VALUE:c2::VARCHAR),
    COMPLETION_DATE DATE AS (VALUE:c3::DATE),
    SCORE NUMBER AS (VALUE:c4::NUMBER),
    STATUS VARCHAR AS (VALUE:c5::VARCHAR),
    TRAINING_TYPE VARCHAR AS (VALUE:c6::VARCHAR)
)
LOCATION = @STG_METACOMPLIANCE_EXPORTS
FILE_FORMAT = CSV_METACOMPLIANCE_FORMAT
AUTO_REFRESH = TRUE
REFRESH_ON_CREATE = TRUE
COMMENT = 'External table for MetaCompliance training completion - refreshed daily';

-- =====================================================================
-- SECTION 6: UPDATE BATCH INGESTION TASKS
-- =====================================================================
-- Now update the placeholder tasks with actual COPY statements

USE ROLE DEV_DEVELOPER;
USE SCHEMA DEV_TRANSFORMATION.SECURITY_ANALYTICS;

-- Update ServiceNow ingestion task
CREATE OR REPLACE TASK TASK_INGEST_SERVICENOW
    WAREHOUSE = DEV_WH
    AFTER TASK_ROOT_DAILY_ORCHESTRATION
AS
    INSERT INTO DEV_LANDING.SECURITY_ANALYTICS.STG_SERVICENOW_INCIDENTS (
        INCIDENT_ID,
        INCIDENT_NUMBER,
        OPENED_AT,
        CLOSED_AT,
        PRIORITY,
        CATEGORY,
        ASSIGNED_TO,
        SHORT_DESCRIPTION,
        STATE,
        RESOLUTION_CODE
    )
    SELECT
        INCIDENT_ID,
        INCIDENT_NUMBER,
        OPENED_AT,
        CLOSED_AT,
        PRIORITY,
        CATEGORY,
        ASSIGNED_TO,
        SHORT_DESCRIPTION,
        STATE,
        RESOLUTION_CODE
    FROM DEV_LANDING.SECURITY_ANALYTICS.EXT_SERVICENOW_INCIDENTS;

-- Update RSA Archer ingestion task
CREATE OR REPLACE TASK TASK_INGEST_ARCHER
    WAREHOUSE = DEV_WH
    AFTER TASK_ROOT_DAILY_ORCHESTRATION
AS
    INSERT INTO DEV_LANDING.SECURITY_ANALYTICS.STG_ARCHER_MATURITY (
        ASSESSMENT_ID,
        ASSESSMENT_DATE,
        OPCO_ID,
        NIST_FUNCTION,
        MATURITY_LEVEL,
        SCORE,
        COMMENTS
    )
    SELECT
        ASSESSMENT_ID,
        ASSESSMENT_DATE,
        OPCO_ID,
        NIST_FUNCTION,
        MATURITY_LEVEL,
        SCORE,
        COMMENTS
    FROM DEV_LANDING.SECURITY_ANALYTICS.EXT_ARCHER_MATURITY;

-- Update MetaCompliance ingestion task
CREATE OR REPLACE TASK TASK_INGEST_METACOMPLIANCE
    WAREHOUSE = DEV_WH
    AFTER TASK_ROOT_DAILY_ORCHESTRATION
AS
    INSERT INTO DEV_LANDING.SECURITY_ANALYTICS.STG_METACOMPLIANCE_TRAINING (
        USER_EMAIL,
        COURSE_NAME,
        COMPLETION_DATE,
        SCORE,
        STATUS,
        TRAINING_TYPE
    )
    SELECT
        USER_EMAIL,
        COURSE_NAME,
        COMPLETION_DATE,
        SCORE,
        STATUS,
        TRAINING_TYPE
    FROM DEV_LANDING.SECURITY_ANALYTICS.EXT_METACOMPLIANCE_TRAINING;

-- =====================================================================
-- SECTION 7: GRANT EXECUTE TASK PRIVILEGE
-- =====================================================================

USE ROLE ACCOUNTADMIN;

-- Grant EXECUTE TASK privilege to DEV_DEVELOPER role
GRANT EXECUTE TASK ON ACCOUNT TO ROLE DEV_DEVELOPER;

-- Verify grant
SHOW GRANTS TO ROLE DEV_DEVELOPER;

-- =====================================================================
-- SECTION 8: RESUME TASKS (ACTIVATE PIPELINE)
-- =====================================================================
-- Tasks must be resumed in reverse dependency order (children first)

USE ROLE DEV_DEVELOPER;
USE SCHEMA DEV_TRANSFORMATION.SECURITY_ANALYTICS;

-- Resume child tasks first
ALTER TASK TASK_REFRESH_POWERBI_VIEWS RESUME;
ALTER TASK TASK_CALCULATE_TOP13_METRICS RESUME;
ALTER TASK TASK_INGEST_METACOMPLIANCE RESUME;
ALTER TASK TASK_INGEST_ARCHER RESUME;
ALTER TASK TASK_INGEST_SERVICENOW RESUME;

-- Resume stream-triggered tasks
ALTER TASK TASK_TRANSFORM_QUALYS RESUME;
ALTER TASK TASK_TRANSFORM_SENTINELONE RESUME;
ALTER TASK TASK_TRANSFORM_CROWDSTRIKE RESUME;

-- Resume monitoring tasks
ALTER TASK TASK_WEEKLY_HEALTH_CHECK RESUME;
ALTER TASK TASK_MONITORING_HEALTH_CHECK RESUME;

-- Resume root task LAST
ALTER TASK TASK_ROOT_DAILY_ORCHESTRATION RESUME;

-- =====================================================================
-- SECTION 9: VERIFICATION
-- =====================================================================

-- Check all tasks are running
SELECT
    NAME,
    STATE,
    SCHEDULE,
    WAREHOUSE,
    PREDECESSORS
FROM INFORMATION_SCHEMA.TASKS
WHERE DATABASE_NAME = 'DEV_TRANSFORMATION'
AND SCHEMA_NAME = 'SECURITY_ANALYTICS'
ORDER BY NAME;

-- Check pipes are defined
SHOW PIPES IN SCHEMA DEV_LANDING.SECURITY_ANALYTICS;

-- Check storage integrations
USE ROLE ACCOUNTADMIN;
SHOW INTEGRATIONS;

-- =====================================================================
-- SECTION 10: AWS/AZURE CONFIGURATION OUTPUTS
-- =====================================================================
-- Run these queries and provide outputs to cloud team

USE ROLE ACCOUNTADMIN;

-- Get AWS IAM details for S3 EDR integration
DESC STORAGE INTEGRATION S3_EDR_INTEGRATION;
-- Provide: STORAGE_AWS_IAM_USER_ARN, STORAGE_AWS_EXTERNAL_ID

-- Get AWS IAM details for S3 VULN integration
DESC STORAGE INTEGRATION S3_VULN_INTEGRATION;

-- Get AWS IAM details for S3 SIEM integration
DESC STORAGE INTEGRATION S3_SIEM_INTEGRATION;

-- Get Azure consent URL
DESC STORAGE INTEGRATION AZURE_EMAIL_INTEGRATION;
-- Provide: AZURE_CONSENT_URL (open in browser to grant permissions)

-- Get Snowpipe SQS queue ARNs
USE ROLE DEV_DEVELOPER;
DESC PIPE DEV_LANDING.SECURITY_ANALYTICS.PIPE_CROWDSTRIKE_EDR;
-- Provide notification_channel to AWS team for SNS subscription

DESC PIPE DEV_LANDING.SECURITY_ANALYTICS.PIPE_SENTINELONE_EDR;
DESC PIPE DEV_LANDING.SECURITY_ANALYTICS.PIPE_QUALYS_SCANS;
DESC PIPE DEV_LANDING.SECURITY_ANALYTICS.PIPE_SPLUNK_ALERTS;

DESC PIPE DEV_LANDING.SECURITY_ANALYTICS.PIPE_PROOFPOINT_LOGS;
-- Provide notification_channel to Azure team for Event Grid subscription

-- =====================================================================
-- SUMMARY
-- =====================================================================
/*
OBJECTS CREATED WITH ACCOUNTADMIN ROLE:
✓ 4 Storage Integrations (S3 x3, Azure x1)
✓ 8 External Stages (5 real-time, 3 batch)
✓ 5 Snowpipes (auto-ingest for EDR, Qualys, Proofpoint, Splunk)
✓ 3 External Tables (ServiceNow, Archer, MetaCompliance)
✓ EXECUTE TASK privilege granted to DEV_DEVELOPER
✓ All tasks resumed and activated

PIPELINE STATUS: FULLY DEPLOYED

NEXT STEPS FOR CLOUD/INFRASTRUCTURE TEAM:

1. AWS S3 Configuration:
   - Update IAM Trust Policies with Snowflake IAM user ARNs
   - Create SNS topics for each Snowpipe
   - Configure S3 event notifications → SNS
   - Subscribe Snowflake SQS queues to SNS topics

2. Azure Blob Configuration:
   - Open Azure consent URL and grant permissions
   - Create Event Grid subscription
   - Configure blob created events → Snowflake webhook

3. Data Source Configuration:
   - Configure CrowdStrike to export to S3
   - Configure SentinelOne to export to S3
   - Configure Qualys scheduled exports to S3
   - Configure Proofpoint log aggregation to Azure
   - Configure Splunk S3 exports
   - Configure ServiceNow/Archer/MetaCompliance daily exports

4. Testing:
   - Upload test files to each S3 bucket
   - Verify Snowpipe ingestion
   - Check stream offsets
   - Monitor task execution
   - Validate data quality

MONITORING QUERIES:

-- Snowpipe status
SELECT * FROM TABLE(INFORMATION_SCHEMA.PIPE_USAGE_HISTORY(
    DATE_RANGE_START => DATEADD('day', -1, CURRENT_TIMESTAMP())
));

-- Task execution history
SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    SCHEDULED_TIME_RANGE_START => DATEADD('day', -1, CURRENT_TIMESTAMP())
))
WHERE DATABASE_NAME = 'DEV_TRANSFORMATION'
ORDER BY COMPLETED_TIME DESC;

-- Stream lag
SELECT
    TABLE_NAME,
    SYSTEM$STREAM_HAS_DATA(TABLE_NAME) AS HAS_DATA
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
AND TABLE_TYPE = 'STREAM';

DOCUMENTATION:
- Full setup guide: PIPELINE_INFRASTRUCTURE_SETUP_GUIDE.md
- Developer guide: PIPELINE_DEV_DEVELOPER_ONLY.sql
- This script: PIPELINE_ACCOUNTADMIN_REQUIRED.sql
*/
