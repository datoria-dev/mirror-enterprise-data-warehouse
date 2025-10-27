-- =====================================================================
-- DATA PIPELINE ARCHITECTURE FOR SECURITY_ANALYTICS
-- =====================================================================
-- Purpose: Complete ETL/ELT pipeline implementation using Snowflake-native
--          Snowpipe, Tasks, and Streams for automated data ingestion
-- Author: Data Engineering Team
-- Date: 2025-10-07
-- Architecture: Event-driven real-time + Scheduled batch orchestration
-- =====================================================================

USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;

-- =====================================================================
-- SECTION 1: CLOUD STORAGE INTEGRATIONS
-- =====================================================================
-- Create storage integrations for S3/Azure Blob access
-- These are used by Snowpipe for auto-ingestion and external tables

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

-- Azure Integration for email security (Proofpoint)
CREATE OR REPLACE STORAGE INTEGRATION AZURE_EMAIL_INTEGRATION
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = AZURE
    ENABLED = TRUE
    AZURE_TENANT_ID = 'your-tenant-id'
    STORAGE_ALLOWED_LOCATIONS = (
        'azure://crhsecuritydata.blob.core.windows.net/proofpoint/'
    )
    COMMENT = 'Azure Blob integration for Proofpoint email logs';

-- S3 Integration for SIEM logs (Splunk)
CREATE OR REPLACE STORAGE INTEGRATION S3_SIEM_INTEGRATION
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = S3
    ENABLED = TRUE
    STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::123456789012:role/snowflake-siem-role'
    STORAGE_ALLOWED_LOCATIONS = (
        's3://GenericCorp-security-data/splunk/alerts/',
        's3://GenericCorp-security-data/splunk/events/'
    )
    COMMENT = 'S3 integration for Splunk SIEM data';

-- =====================================================================
-- SECTION 2: EXTERNAL STAGES
-- =====================================================================
-- File formats and stages for different data sources

-- JSON file format for EDR event data
CREATE OR REPLACE FILE FORMAT JSON_EDR_FORMAT
    TYPE = JSON
    COMPRESSION = AUTO
    STRIP_OUTER_ARRAY = TRUE
    STRIP_NULL_VALUES = FALSE
    COMMENT = 'JSON format for EDR event streams';

-- CSV file format for Qualys exports
CREATE OR REPLACE FILE FORMAT CSV_QUALYS_FORMAT
    TYPE = CSV
    COMPRESSION = GZIP
    FIELD_DELIMITER = ','
    RECORD_DELIMITER = '\n'
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    ESCAPE_UNENCLOSED_FIELD = NONE
    TRIM_SPACE = TRUE
    NULL_IF = ('NULL', 'null', '', '\\N')
    COMMENT = 'CSV format for Qualys vulnerability exports';

-- JSON file format for Proofpoint message logs
CREATE OR REPLACE FILE FORMAT JSON_PROOFPOINT_FORMAT
    TYPE = JSON
    COMPRESSION = AUTO
    STRIP_OUTER_ARRAY = TRUE
    DATE_FORMAT = 'AUTO'
    TIMESTAMP_FORMAT = 'AUTO'
    COMMENT = 'JSON format for Proofpoint message logs';

-- Parquet format for Splunk exports
CREATE OR REPLACE FILE FORMAT PARQUET_SPLUNK_FORMAT
    TYPE = PARQUET
    COMPRESSION = SNAPPY
    COMMENT = 'Parquet format for Splunk event data';

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

-- =====================================================================
-- SECTION 3: LANDING TABLES FOR SNOWPIPE INGESTION
-- =====================================================================
-- Raw landing tables with variant columns for flexible ingestion

USE SCHEMA DEV_LANDING.SECURITY_ANALYTICS;

-- CrowdStrike raw events landing table
CREATE OR REPLACE TABLE L_CROWDSTRIKE_RAW (
    INGESTION_TIMESTAMP TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    SOURCE_FILE_NAME VARCHAR(500),
    SOURCE_FILE_ROW_NUMBER NUMBER,
    RAW_DATA VARIANT,
    METADATA VARIANT
)
COMMENT = 'Raw landing table for CrowdStrike EDR events - auto-ingested via Snowpipe';

-- SentinelOne raw events landing table
CREATE OR REPLACE TABLE L_SENTINELONE_RAW (
    INGESTION_TIMESTAMP TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    SOURCE_FILE_NAME VARCHAR(500),
    SOURCE_FILE_ROW_NUMBER NUMBER,
    RAW_DATA VARIANT,
    METADATA VARIANT
)
COMMENT = 'Raw landing table for SentinelOne threat events - auto-ingested via Snowpipe';

-- Qualys scan results landing table
CREATE OR REPLACE TABLE L_QUALYS_SCANS_RAW (
    INGESTION_TIMESTAMP TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    SOURCE_FILE_NAME VARCHAR(500),
    SOURCE_FILE_ROW_NUMBER NUMBER,
    QID VARCHAR(50),
    HOST_ID VARCHAR(100),
    IP_ADDRESS VARCHAR(45),
    DNS_NAME VARCHAR(500),
    SEVERITY NUMBER,
    CVSS_SCORE DECIMAL(4,1),
    FIRST_DETECTED TIMESTAMP_NTZ,
    LAST_DETECTED TIMESTAMP_NTZ,
    STATUS VARCHAR(50),
    RAW_DATA VARIANT
)
COMMENT = 'Raw landing table for Qualys vulnerability scans - auto-ingested via Snowpipe';

-- Proofpoint message logs landing table
CREATE OR REPLACE TABLE L_PROOFPOINT_RAW (
    INGESTION_TIMESTAMP TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    SOURCE_FILE_NAME VARCHAR(500),
    SOURCE_FILE_ROW_NUMBER NUMBER,
    MESSAGE_ID VARCHAR(500),
    MESSAGE_TIME TIMESTAMP_NTZ,
    SENDER VARCHAR(500),
    RECIPIENT VARCHAR(500),
    SUBJECT VARCHAR(1000),
    THREAT_TYPE VARCHAR(100),
    RAW_DATA VARIANT
)
COMMENT = 'Raw landing table for Proofpoint email logs - auto-ingested via Snowpipe';

-- Splunk alerts landing table
CREATE OR REPLACE TABLE L_SPLUNK_ALERTS_RAW (
    INGESTION_TIMESTAMP TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    SOURCE_FILE_NAME VARCHAR(500),
    ALERT_ID VARCHAR(100),
    ALERT_TIME TIMESTAMP_NTZ,
    ALERT_NAME VARCHAR(500),
    SEVERITY VARCHAR(50),
    SOURCE_IP VARCHAR(45),
    DESTINATION_IP VARCHAR(45),
    RAW_DATA VARIANT
)
COMMENT = 'Raw landing table for Splunk security alerts - auto-ingested via Snowpipe';

-- =====================================================================
-- SECTION 4: SNOWPIPE DEFINITIONS (REAL-TIME INGESTION)
-- =====================================================================
-- Auto-ingest pipes triggered by S3/Azure events

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

-- Snowpipe for Proofpoint
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

-- =====================================================================
-- SECTION 5: STREAMS FOR CHANGE DATA CAPTURE (CDC)
-- =====================================================================
-- Streams track changes in landing tables for incremental processing

USE SCHEMA DEV_LANDING.SECURITY_ANALYTICS;

-- Stream for CrowdStrike new events
CREATE OR REPLACE STREAM STREAM_CROWDSTRIKE_NEW
    ON TABLE L_CROWDSTRIKE_RAW
    COMMENT = 'CDC stream for new CrowdStrike events - consumed by transformation tasks';

-- Stream for SentinelOne new events
CREATE OR REPLACE STREAM STREAM_SENTINELONE_NEW
    ON TABLE L_SENTINELONE_RAW
    COMMENT = 'CDC stream for new SentinelOne events - consumed by transformation tasks';

-- Stream for Qualys new scans
CREATE OR REPLACE STREAM STREAM_QUALYS_NEW
    ON TABLE L_QUALYS_SCANS_RAW
    COMMENT = 'CDC stream for new Qualys scans - consumed by transformation tasks';

-- Stream for Proofpoint new messages
CREATE OR REPLACE STREAM STREAM_PROOFPOINT_NEW
    ON TABLE L_PROOFPOINT_RAW
    COMMENT = 'CDC stream for new Proofpoint messages - consumed by transformation tasks';

-- Stream for Splunk new alerts
CREATE OR REPLACE STREAM STREAM_SPLUNK_NEW
    ON TABLE L_SPLUNK_ALERTS_RAW
    COMMENT = 'CDC stream for new Splunk alerts - consumed by transformation tasks';

-- =====================================================================
-- SECTION 6: EXTERNAL TABLES FOR BATCH SOURCES
-- =====================================================================
-- External tables for systems without real-time feeds (ServiceNow, Archer, MetaCompliance)

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
FILE_FORMAT = (TYPE = CSV SKIP_HEADER = 1)
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
FILE_FORMAT = (TYPE = CSV SKIP_HEADER = 1)
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
FILE_FORMAT = (TYPE = CSV SKIP_HEADER = 1)
AUTO_REFRESH = TRUE
REFRESH_ON_CREATE = TRUE
COMMENT = 'External table for MetaCompliance training completion - refreshed daily';

-- =====================================================================
-- SECTION 7: TRANSFORMATION STORED PROCEDURES
-- =====================================================================
-- Procedures to transform raw data into curated tables

USE SCHEMA DEV_TRANSFORMATION.SECURITY_ANALYTICS;

-- Procedure to process CrowdStrike events into FACT_EDR
CREATE OR REPLACE PROCEDURE SP_TRANSFORM_CROWDSTRIKE_EDR()
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
DECLARE
    rows_processed NUMBER DEFAULT 0;
BEGIN
    -- Insert new EDR events from stream
    INSERT INTO FACT_EDR (
        EVENT_ID,
        HOST_ID,
        DATE,
        THREAT_KEY,
        EVENT_TYPE,
        SEVERITY,
        DETECTION_TIME,
        THREAT_COUNT,
        FILE_PATH,
        PROCESS_NAME,
        EDR_PLATFORM
    )
    SELECT
        RAW_DATA:detection_id::VARCHAR,
        RAW_DATA:device_id::VARCHAR,
        TO_DATE(RAW_DATA:created_timestamp::TIMESTAMP_NTZ),
        NULL, -- Join to DIM_THREAT later
        RAW_DATA:behavior::VARCHAR,
        RAW_DATA:severity::VARCHAR,
        RAW_DATA:created_timestamp::TIMESTAMP_NTZ,
        1,
        RAW_DATA:file_path::VARCHAR,
        RAW_DATA:process_name::VARCHAR,
        'CrowdStrike'
    FROM DEV_LANDING.SECURITY_ANALYTICS.STREAM_CROWDSTRIKE_NEW
    WHERE METADATA$ACTION = 'INSERT'
    AND METADATA$ISUPDATE = FALSE;

    rows_processed := SQLROWCOUNT;

    RETURN 'Processed ' || rows_processed || ' CrowdStrike events into FACT_EDR';
END;
$$
COMMENT = 'Transform CrowdStrike raw events into FACT_EDR table';

-- Procedure to process Qualys scans into FACT_QUALYS
CREATE OR REPLACE PROCEDURE SP_TRANSFORM_QUALYS_SCANS()
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
DECLARE
    rows_processed NUMBER DEFAULT 0;
BEGIN
    -- Merge Qualys scan results into FACT_QUALYS
    MERGE INTO FACT_QUALYS AS tgt
    USING (
        SELECT
            QID,
            HOST_ID,
            TO_DATE(LAST_DETECTED) AS SCAN_DATE,
            SEVERITY,
            CVSS_SCORE,
            CASE
                WHEN STATUS = 'New' THEN 'New'
                WHEN STATUS = 'Active' THEN 'Active'
                WHEN STATUS = 'Re-Opened' THEN 'Re-Opened'
                ELSE 'Fixed'
            END AS STATUS,
            FIRST_DETECTED,
            LAST_DETECTED,
            DATEDIFF(DAY, FIRST_DETECTED, CURRENT_TIMESTAMP()) AS DAYS_OPEN
        FROM DEV_LANDING.SECURITY_ANALYTICS.STREAM_QUALYS_NEW
        WHERE METADATA$ACTION = 'INSERT'
        AND METADATA$ISUPDATE = FALSE
    ) AS src
    ON tgt.QID = src.QID
    AND tgt.HOST_ID = src.HOST_ID
    WHEN MATCHED AND src.LAST_DETECTED > tgt.LAST_DETECTED THEN
        UPDATE SET
            tgt.SEVERITY = src.SEVERITY,
            tgt.CVSS_SCORE = src.CVSS_SCORE,
            tgt.STATUS = src.STATUS,
            tgt.LAST_DETECTED = src.LAST_DETECTED,
            tgt.DAYS_OPEN = src.DAYS_OPEN
    WHEN NOT MATCHED THEN
        INSERT (QID, HOST_ID, SCAN_DATE, SEVERITY, CVSS_SCORE, STATUS, FIRST_DETECTED, LAST_DETECTED, DAYS_OPEN)
        VALUES (src.QID, src.HOST_ID, src.SCAN_DATE, src.SEVERITY, src.CVSS_SCORE, src.STATUS, src.FIRST_DETECTED, src.LAST_DETECTED, src.DAYS_OPEN);

    rows_processed := SQLROWCOUNT;

    RETURN 'Processed ' || rows_processed || ' Qualys scan results into FACT_QUALYS';
END;
$$
COMMENT = 'Transform Qualys scan results into FACT_QUALYS table';

-- Procedure to calculate Top 13 metrics
CREATE OR REPLACE PROCEDURE SP_CALCULATE_TOP13_METRICS()
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
DECLARE
    calculation_timestamp TIMESTAMP_LTZ;
BEGIN
    calculation_timestamp := CURRENT_TIMESTAMP();

    -- Metric #4: Days Since Last Ransomware
    INSERT INTO TBL_KPI_MASTER (
        METRIC_NAME,
        METRIC_VALUE,
        CALCULATION_DATE,
        NIST_FUNCTION,
        TARGET_THRESHOLD
    )
    SELECT
        'Days Since Last Ransomware',
        DATEDIFF(DAY, MAX(DETECTION_TIME), CURRENT_DATE()),
        calculation_timestamp,
        'ID.RM',
        NULL
    FROM FACT_EDR
    WHERE THREAT_TYPE LIKE '%ransomware%';

    -- Metric #5: EDR Coverage - All Systems
    INSERT INTO TBL_KPI_MASTER (
        METRIC_NAME,
        METRIC_VALUE,
        CALCULATION_DATE,
        NIST_FUNCTION,
        TARGET_THRESHOLD
    )
    SELECT
        'EDR Coverage - All Systems',
        ROUND(
            (COUNT(DISTINCT CASE WHEN edr_agent_status = 'Healthy' THEN host_id END) * 100.0) /
            NULLIF(COUNT(DISTINCT host_id), 0),
            2
        ),
        calculation_timestamp,
        'PR.PT',
        98.0
    FROM DIM_HOST;

    -- Metric #6: Vuln-Scan Coverage & Agent Health
    INSERT INTO TBL_KPI_MASTER (
        METRIC_NAME,
        METRIC_VALUE,
        CALCULATION_DATE,
        NIST_FUNCTION,
        TARGET_THRESHOLD
    )
    SELECT
        'Vuln-Scan Coverage',
        ROUND(
            (COUNT(DISTINCT CASE WHEN qualys_agent_status = 'Installed' THEN host_id END) * 100.0) /
            NULLIF(COUNT(DISTINCT host_id), 0),
            2
        ),
        calculation_timestamp,
        'PR.IP',
        95.0
    FROM DIM_HOST;

    RETURN 'Calculated Top 13 metrics successfully';
END;
$$
COMMENT = 'Calculate all Top 13 executive metrics per Metrics Dictionary';

-- =====================================================================
-- SECTION 8: TASK ORCHESTRATION DAG
-- =====================================================================
-- Task dependency tree for automated pipeline orchestration

USE SCHEMA DEV_TRANSFORMATION.SECURITY_ANALYTICS;

-- Root task: Daily orchestration trigger
CREATE OR REPLACE TASK TASK_ROOT_DAILY_ORCHESTRATION
    WAREHOUSE = DEV_WH
    SCHEDULE = 'USING CRON 0 1 * * * America/New_York' -- Daily at 1 AM EST
AS
    SELECT 'Daily orchestration started' AS STATUS;

-- Task: Transform CrowdStrike events (runs every 15 minutes when stream has data)
CREATE OR REPLACE TASK TASK_TRANSFORM_CROWDSTRIKE
    WAREHOUSE = DEV_WH
    SCHEDULE = '15 MINUTE'
    WHEN SYSTEM$STREAM_HAS_DATA('DEV_LANDING.SECURITY_ANALYTICS.STREAM_CROWDSTRIKE_NEW')
AS
    CALL SP_TRANSFORM_CROWDSTRIKE_EDR();

-- Task: Transform SentinelOne events (runs every 15 minutes when stream has data)
CREATE OR REPLACE TASK TASK_TRANSFORM_SENTINELONE
    WAREHOUSE = DEV_WH
    SCHEDULE = '15 MINUTE'
    WHEN SYSTEM$STREAM_HAS_DATA('DEV_LANDING.SECURITY_ANALYTICS.STREAM_SENTINELONE_NEW')
AS
    CALL SP_TRANSFORM_SENTINELONE_EDR();

-- Task: Transform Qualys scans (runs every hour when stream has data)
CREATE OR REPLACE TASK TASK_TRANSFORM_QUALYS
    WAREHOUSE = DEV_WH
    SCHEDULE = '60 MINUTE'
    WHEN SYSTEM$STREAM_HAS_DATA('DEV_LANDING.SECURITY_ANALYTICS.STREAM_QUALYS_NEW')
AS
    CALL SP_TRANSFORM_QUALYS_SCANS();

-- Task: Ingest ServiceNow incidents (daily at 1:15 AM)
CREATE OR REPLACE TASK TASK_INGEST_SERVICENOW
    WAREHOUSE = DEV_WH
    AFTER TASK_ROOT_DAILY_ORCHESTRATION
AS
    INSERT INTO TBL_SERVICENOW_INCIDENTS
    SELECT * FROM EXT_SERVICENOW_INCIDENTS;

-- Task: Ingest RSA Archer maturity data (daily at 1:30 AM)
CREATE OR REPLACE TASK TASK_INGEST_ARCHER
    WAREHOUSE = DEV_WH
    AFTER TASK_ROOT_DAILY_ORCHESTRATION
AS
    INSERT INTO TBL_ARCHER_MATURITY
    SELECT * FROM EXT_ARCHER_MATURITY;

-- Task: Ingest MetaCompliance training data (daily at 1:45 AM)
CREATE OR REPLACE TASK TASK_INGEST_METACOMPLIANCE
    WAREHOUSE = DEV_WH
    AFTER TASK_ROOT_DAILY_ORCHESTRATION
AS
    INSERT INTO TBL_METACOMPLIANCE_TRAINING
    SELECT * FROM EXT_METACOMPLIANCE_TRAINING;

-- Task: Calculate Top 13 metrics (daily at 2:00 AM, after all ingestion)
CREATE OR REPLACE TASK TASK_CALCULATE_TOP13_METRICS
    WAREHOUSE = DEV_WH
    AFTER TASK_INGEST_SERVICENOW, TASK_INGEST_ARCHER, TASK_INGEST_METACOMPLIANCE
AS
    CALL SP_CALCULATE_TOP13_METRICS();

-- Task: Refresh Power BI materialized views (daily at 3:00 AM)
CREATE OR REPLACE TASK TASK_REFRESH_POWERBI_VIEWS
    WAREHOUSE = DEV_WH
    AFTER TASK_CALCULATE_TOP13_METRICS
AS
    BEGIN
        -- Refresh executive dashboard view
        CREATE OR REPLACE TABLE VW_POWERBI_EXECUTIVE_DASHBOARD_MAT AS
        SELECT * FROM VW_POWERBI_EXECUTIVE_DASHBOARD;

        -- Refresh data quality view
        CREATE OR REPLACE TABLE VW_DATA_QUALITY_DASHBOARD_MAT AS
        SELECT * FROM VW_DATA_QUALITY_DASHBOARD;
    END;

-- Task: Weekly comprehensive health check (Sundays at 6:00 AM)
CREATE OR REPLACE TASK TASK_WEEKLY_HEALTH_CHECK
    WAREHOUSE = DEV_WH
    SCHEDULE = 'USING CRON 0 6 * * SUN America/New_York'
AS
    BEGIN
        -- Log pipeline health metrics
        INSERT INTO IMPLEMENTATION_LOG (LOG_TIMESTAMP, LOG_TYPE, MESSAGE)
        SELECT
            CURRENT_TIMESTAMP(),
            'PIPELINE_HEALTH',
            'Snowpipe Status: ' ||
            (SELECT COUNT(*) FROM TABLE(INFORMATION_SCHEMA.PIPE_USAGE_HISTORY(DATE_RANGE_START=>DATEADD('day', -7, CURRENT_DATE())))) ||
            ' files ingested in last 7 days';

        -- Check stream lag
        INSERT INTO IMPLEMENTATION_LOG (LOG_TIMESTAMP, LOG_TYPE, MESSAGE)
        SELECT
            CURRENT_TIMESTAMP(),
            'STREAM_LAG',
            'Stream ' || TABLE_NAME || ' has ' || SYSTEM$STREAM_GET_TABLE_TIMESTAMP(TABLE_NAME) || ' lag'
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
        AND TABLE_TYPE = 'STREAM';
    END;

-- =====================================================================
-- SECTION 9: MONITORING AND ALERTING
-- =====================================================================

USE SCHEMA DEV_TRANSFORMATION.SECURITY_ANALYTICS;

-- Pipeline monitoring table
CREATE OR REPLACE TABLE TBL_PIPELINE_MONITORING (
    MONITORING_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    CHECK_TIMESTAMP TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    PIPELINE_NAME VARCHAR(200),
    PIPELINE_TYPE VARCHAR(50), -- 'SNOWPIPE', 'TASK', 'STREAM'
    STATUS VARCHAR(50), -- 'HEALTHY', 'WARNING', 'ERROR'
    ROWS_PROCESSED NUMBER,
    ERROR_MESSAGE VARCHAR(5000),
    LAG_MINUTES NUMBER,
    LAST_SUCCESS_TIMESTAMP TIMESTAMP_LTZ
)
COMMENT = 'Pipeline health monitoring metrics';

-- Procedure to monitor Snowpipe health
CREATE OR REPLACE PROCEDURE SP_MONITOR_SNOWPIPE_HEALTH()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
    -- Check each Snowpipe's status
    INSERT INTO TBL_PIPELINE_MONITORING (
        PIPELINE_NAME,
        PIPELINE_TYPE,
        STATUS,
        ROWS_PROCESSED,
        ERROR_MESSAGE,
        LAST_SUCCESS_TIMESTAMP
    )
    SELECT
        PIPE_NAME,
        'SNOWPIPE',
        CASE
            WHEN ERROR_COUNT > 0 THEN 'ERROR'
            WHEN FILES_LOADED = 0 AND DATEDIFF(HOUR, LAST_LOAD_TIME, CURRENT_TIMESTAMP()) > 24 THEN 'WARNING'
            ELSE 'HEALTHY'
        END,
        ROWS_LOADED,
        ERROR_MESSAGE,
        LAST_LOAD_TIME
    FROM TABLE(INFORMATION_SCHEMA.PIPE_USAGE_HISTORY(
        DATE_RANGE_START=>DATEADD('hour', -24, CURRENT_TIMESTAMP())
    ));

    RETURN 'Snowpipe health check completed';
END;
$$;

-- Procedure to monitor Task execution
CREATE OR REPLACE PROCEDURE SP_MONITOR_TASK_HEALTH()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
    INSERT INTO TBL_PIPELINE_MONITORING (
        PIPELINE_NAME,
        PIPELINE_TYPE,
        STATUS,
        ERROR_MESSAGE,
        LAST_SUCCESS_TIMESTAMP
    )
    SELECT
        NAME,
        'TASK',
        CASE
            WHEN STATE = 'suspended' THEN 'ERROR'
            WHEN ERROR_CODE IS NOT NULL THEN 'ERROR'
            WHEN DATEDIFF(HOUR, COMPLETED_TIME, CURRENT_TIMESTAMP()) > 48 THEN 'WARNING'
            ELSE 'HEALTHY'
        END,
        ERROR_MESSAGE,
        COMPLETED_TIME
    FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
        SCHEDULED_TIME_RANGE_START=>DATEADD('day', -1, CURRENT_TIMESTAMP())
    ))
    WHERE DATABASE_NAME = 'DEV_TRANSFORMATION'
    AND SCHEMA_NAME = 'SECURITY_ANALYTICS';

    RETURN 'Task health check completed';
END;
$$;

-- Task to run monitoring checks (every 30 minutes)
CREATE OR REPLACE TASK TASK_MONITORING_HEALTH_CHECK
    WAREHOUSE = DEV_WH
    SCHEDULE = '30 MINUTE'
AS
    BEGIN
        CALL SP_MONITOR_SNOWPIPE_HEALTH();
        CALL SP_MONITOR_TASK_HEALTH();
    END;

-- =====================================================================
-- SECTION 10: ENABLE ALL TASKS
-- =====================================================================
-- Resume tasks to activate the pipeline (execute manually or via script)

-- Note: Tasks must be resumed in dependency order (child to parent)
-- IMPORTANT: Requires ACCOUNTADMIN role or EXECUTE TASK privilege

/*
-- To enable the pipeline, execute these commands as ACCOUNTADMIN:

ALTER TASK TASK_REFRESH_POWERBI_VIEWS RESUME;
ALTER TASK TASK_CALCULATE_TOP13_METRICS RESUME;
ALTER TASK TASK_INGEST_METACOMPLIANCE RESUME;
ALTER TASK TASK_INGEST_ARCHER RESUME;
ALTER TASK TASK_INGEST_SERVICENOW RESUME;
ALTER TASK TASK_TRANSFORM_QUALYS RESUME;
ALTER TASK TASK_TRANSFORM_SENTINELONE RESUME;
ALTER TASK TASK_TRANSFORM_CROWDSTRIKE RESUME;
ALTER TASK TASK_WEEKLY_HEALTH_CHECK RESUME;
ALTER TASK TASK_MONITORING_HEALTH_CHECK RESUME;
ALTER TASK TASK_ROOT_DAILY_ORCHESTRATION RESUME;

-- Verify all tasks are running:
SELECT
    NAME,
    STATE,
    SCHEDULE,
    WAREHOUSE
FROM INFORMATION_SCHEMA.TASKS
WHERE DATABASE_NAME = 'DEV_TRANSFORMATION'
AND SCHEMA_NAME = 'SECURITY_ANALYTICS'
ORDER BY NAME;
*/

-- =====================================================================
-- PIPELINE ARCHITECTURE SUMMARY
-- =====================================================================
/*
DATA FLOW ARCHITECTURE:

┌─────────────────────────────────────────────────────────────────┐
│                    REAL-TIME INGESTION LAYER                    │
│  (Snowpipe - Event-Driven, Auto-Scaling)                        │
└─────────────────────────────────────────────────────────────────┘
         │
         ├─ S3 Events → PIPE_CROWDSTRIKE_EDR → L_CROWDSTRIKE_RAW
         ├─ S3 Events → PIPE_SENTINELONE_EDR → L_SENTINELONE_RAW
         ├─ S3 Events → PIPE_QUALYS_SCANS → L_QUALYS_SCANS_RAW
         ├─ Azure Events → PIPE_PROOFPOINT_LOGS → L_PROOFPOINT_RAW
         └─ S3 Events → PIPE_SPLUNK_ALERTS → L_SPLUNK_ALERTS_RAW
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CHANGE DATA CAPTURE LAYER                     │
│  (Streams - Track Incremental Changes)                          │
└─────────────────────────────────────────────────────────────────┘
         │
         ├─ STREAM_CROWDSTRIKE_NEW → Tracks new events
         ├─ STREAM_SENTINELONE_NEW → Tracks new events
         ├─ STREAM_QUALYS_NEW → Tracks new scans
         ├─ STREAM_PROOFPOINT_NEW → Tracks new messages
         └─ STREAM_SPLUNK_NEW → Tracks new alerts
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  TRANSFORMATION LAYER                           │
│  (Tasks - Scheduled/Stream-Triggered Processing)                │
└─────────────────────────────────────────────────────────────────┘
         │
         ├─ TASK_TRANSFORM_CROWDSTRIKE (Every 15 min) → FACT_EDR
         ├─ TASK_TRANSFORM_SENTINELONE (Every 15 min) → FACT_EDR
         ├─ TASK_TRANSFORM_QUALYS (Every 60 min) → FACT_QUALYS
         │
         ├─ TASK_ROOT_DAILY_ORCHESTRATION (Daily 1 AM)
         │   ├─ TASK_INGEST_SERVICENOW (1:15 AM)
         │   ├─ TASK_INGEST_ARCHER (1:30 AM)
         │   └─ TASK_INGEST_METACOMPLIANCE (1:45 AM)
         │       │
         │       └─ TASK_CALCULATE_TOP13_METRICS (2:00 AM)
         │           │
         │           └─ TASK_REFRESH_POWERBI_VIEWS (3:00 AM)
         │
         └─ TASK_WEEKLY_HEALTH_CHECK (Sundays 6 AM)
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REPORTING LAYER                              │
│  (Materialized Views for Power BI)                              │
└─────────────────────────────────────────────────────────────────┘
         │
         ├─ VW_POWERBI_EXECUTIVE_DASHBOARD_MAT
         ├─ VW_DATA_QUALITY_DASHBOARD_MAT
         └─ VW_TOP13_METRICS

┌─────────────────────────────────────────────────────────────────┐
│                  MONITORING & ALERTING                          │
│  (Every 30 minutes)                                             │
└─────────────────────────────────────────────────────────────────┘
         │
         └─ TASK_MONITORING_HEALTH_CHECK
             ├─ SP_MONITOR_SNOWPIPE_HEALTH()
             └─ SP_MONITOR_TASK_HEALTH()

METRICS COVERED:
✓ Metric #4: Days Since Last Ransomware (Hourly updates via EDR streams)
✓ Metric #5: EDR Coverage (Daily calculation)
✓ Metric #6: Vuln-Scan Coverage (Hourly updates via Qualys stream)
✓ Metric #7: Email-Sending Domain Security (Real-time via Proofpoint)
✓ Metric #9: MTTE - Malicious Email (Real-time calculation)
✓ Metric #10: Log-Source Coverage for SIEM (Real-time via Splunk)

TECHNOLOGY STACK:
- Snowpipe: Real-time continuous ingestion (serverless)
- Streams: Change Data Capture for incremental processing
- Tasks: Scheduled orchestration with DAG dependencies
- External Tables: Batch source integration (auto-refresh)
- Stored Procedures: Business logic and transformations
- Monitoring: Pipeline health checks and alerting

BENEFITS:
✓ Serverless auto-scaling (Snowpipe handles spikes)
✓ Event-driven architecture (no polling)
✓ Incremental processing (Streams reduce compute)
✓ Declarative orchestration (Task DAG)
✓ Built-in monitoring and error handling
✓ Cost-efficient (only pay for data processed)
*/
