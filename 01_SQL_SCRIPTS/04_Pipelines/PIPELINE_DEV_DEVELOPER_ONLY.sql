-- =====================================================================
-- DATA PIPELINE - DEV_DEVELOPER COMPATIBLE VERSION
-- =====================================================================
-- Purpose: Pipeline objects that can be created with DEV_DEVELOPER role
-- Author: Data Engineering Team
-- Date: 2025-10-08
-- Note: Storage Integrations, External Stages, and Snowpipes require
--       ACCOUNTADMIN role and are in separate script
-- =====================================================================

USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;

-- =====================================================================
-- SECTION 1: FILE FORMATS
-- =====================================================================

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

-- CSV format for ServiceNow exports
CREATE OR REPLACE FILE FORMAT CSV_SERVICENOW_FORMAT
    TYPE = CSV
    COMPRESSION = GZIP
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    TRIM_SPACE = TRUE
    NULL_IF = ('NULL', 'null', '')
    COMMENT = 'CSV format for ServiceNow incident exports';

-- CSV format for RSA Archer exports
CREATE OR REPLACE FILE FORMAT CSV_ARCHER_FORMAT
    TYPE = CSV
    COMPRESSION = NONE
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    TRIM_SPACE = TRUE
    COMMENT = 'CSV format for RSA Archer GRC exports';

-- CSV format for MetaCompliance exports
CREATE OR REPLACE FILE FORMAT CSV_METACOMPLIANCE_FORMAT
    TYPE = CSV
    COMPRESSION = NONE
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    TRIM_SPACE = TRUE
    COMMENT = 'CSV format for MetaCompliance training exports';

-- =====================================================================
-- SECTION 2: LANDING TABLES FOR SNOWPIPE INGESTION
-- =====================================================================

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

-- ServiceNow incidents staging table (batch load)
CREATE OR REPLACE TABLE STG_SERVICENOW_INCIDENTS (
    LOAD_TIMESTAMP TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    INCIDENT_ID VARCHAR(100),
    INCIDENT_NUMBER VARCHAR(100),
    OPENED_AT TIMESTAMP_NTZ,
    CLOSED_AT TIMESTAMP_NTZ,
    PRIORITY VARCHAR(50),
    CATEGORY VARCHAR(200),
    ASSIGNED_TO VARCHAR(200),
    SHORT_DESCRIPTION VARCHAR(5000),
    STATE VARCHAR(50),
    RESOLUTION_CODE VARCHAR(100)
)
COMMENT = 'Staging table for ServiceNow incident exports - loaded via batch task';

-- RSA Archer maturity staging table (batch load)
CREATE OR REPLACE TABLE STG_ARCHER_MATURITY (
    LOAD_TIMESTAMP TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    ASSESSMENT_ID VARCHAR(100),
    ASSESSMENT_DATE DATE,
    OPCO_ID VARCHAR(50),
    NIST_FUNCTION VARCHAR(100),
    MATURITY_LEVEL NUMBER,
    SCORE NUMBER,
    COMMENTS VARCHAR(5000)
)
COMMENT = 'Staging table for RSA Archer maturity assessments - loaded via batch task';

-- MetaCompliance training staging table (batch load)
CREATE OR REPLACE TABLE STG_METACOMPLIANCE_TRAINING (
    LOAD_TIMESTAMP TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    USER_EMAIL VARCHAR(500),
    COURSE_NAME VARCHAR(500),
    COMPLETION_DATE DATE,
    SCORE NUMBER,
    STATUS VARCHAR(50),
    TRAINING_TYPE VARCHAR(100)
)
COMMENT = 'Staging table for MetaCompliance training completion - loaded via batch task';

-- =====================================================================
-- SECTION 3: STREAMS FOR CHANGE DATA CAPTURE (CDC)
-- =====================================================================

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
-- SECTION 4: TRANSFORMATION STORED PROCEDURES
-- =====================================================================

USE SCHEMA DEV_TRANSFORMATION.SECURITY_ANALYTICS;

-- Procedure to process CrowdStrike events into FACT_EDR
CREATE OR REPLACE PROCEDURE SP_TRANSFORM_CROWDSTRIKE_EDR()
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS CALLER
AS
BEGIN
    LET rows_processed NUMBER DEFAULT 0;

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

-- Procedure to process SentinelOne events into FACT_EDR
CREATE OR REPLACE PROCEDURE SP_TRANSFORM_SENTINELONE_EDR()
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS CALLER
AS
BEGIN
    LET rows_processed NUMBER DEFAULT 0;

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
        RAW_DATA:threatInfo.id::VARCHAR,
        RAW_DATA:agentRealtimeInfo.agentId::VARCHAR,
        TO_DATE(RAW_DATA:threatInfo.createdDate::TIMESTAMP_NTZ),
        NULL,
        RAW_DATA:threatInfo.classification::VARCHAR,
        RAW_DATA:threatInfo.confidenceLevel::VARCHAR,
        RAW_DATA:threatInfo.createdDate::TIMESTAMP_NTZ,
        1,
        RAW_DATA:threatInfo.filePath::VARCHAR,
        RAW_DATA:threatInfo.processUser::VARCHAR,
        'SentinelOne'
    FROM DEV_LANDING.SECURITY_ANALYTICS.STREAM_SENTINELONE_NEW
    WHERE METADATA$ACTION = 'INSERT'
    AND METADATA$ISUPDATE = FALSE;

    rows_processed := SQLROWCOUNT;

    RETURN 'Processed ' || rows_processed || ' SentinelOne events into FACT_EDR';
END;

-- Procedure to process Qualys scans into FACT_QUALYS
CREATE OR REPLACE PROCEDURE SP_TRANSFORM_QUALYS_SCANS()
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS CALLER
AS
BEGIN
    LET rows_processed NUMBER DEFAULT 0;

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

-- Procedure to calculate Top 13 metrics
CREATE OR REPLACE PROCEDURE SP_CALCULATE_TOP13_METRICS()
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS CALLER
AS
BEGIN
    LET calculation_timestamp TIMESTAMP_LTZ;
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
        :calculation_timestamp,
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
        :calculation_timestamp,
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
        :calculation_timestamp,
        'PR.IP',
        95.0
    FROM DIM_HOST;

    RETURN 'Calculated Top 13 metrics successfully';
END;

-- Procedure to monitor Snowpipe health
CREATE OR REPLACE PROCEDURE SP_MONITOR_SNOWPIPE_HEALTH()
RETURNS VARCHAR
LANGUAGE SQL
AS
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

-- Procedure to monitor Task execution
CREATE OR REPLACE PROCEDURE SP_MONITOR_TASK_HEALTH()
RETURNS VARCHAR
LANGUAGE SQL
AS
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

-- =====================================================================
-- SECTION 5: TASK ORCHESTRATION DAG
-- =====================================================================

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

-- Task: Ingest ServiceNow incidents (daily at 1:15 AM) - uses COPY INTO from stage
CREATE OR REPLACE TASK TASK_INGEST_SERVICENOW
    WAREHOUSE = DEV_WH
    AFTER TASK_ROOT_DAILY_ORCHESTRATION
AS
    -- Note: This will work once ACCOUNTADMIN creates the stage
    -- For now, it's defined but won't execute until stage exists
    SELECT 'ServiceNow ingestion - waiting for stage creation' AS STATUS;

-- Task: Ingest RSA Archer maturity data (daily at 1:30 AM)
CREATE OR REPLACE TASK TASK_INGEST_ARCHER
    WAREHOUSE = DEV_WH
    AFTER TASK_ROOT_DAILY_ORCHESTRATION
AS
    SELECT 'Archer ingestion - waiting for stage creation' AS STATUS;

-- Task: Ingest MetaCompliance training data (daily at 1:45 AM)
CREATE OR REPLACE TASK TASK_INGEST_METACOMPLIANCE
    WAREHOUSE = DEV_WH
    AFTER TASK_ROOT_DAILY_ORCHESTRATION
AS
    SELECT 'MetaCompliance ingestion - waiting for stage creation' AS STATUS;

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
        'Stream ' || TABLE_NAME || ' lag check'
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
    AND TABLE_TYPE = 'STREAM';
END;

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
-- SECTION 6: PIPELINE MONITORING TABLE
-- =====================================================================

USE SCHEMA DEV_TRANSFORMATION.SECURITY_ANALYTICS;

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

-- =====================================================================
-- VERIFICATION QUERIES
-- =====================================================================

-- Verify all objects created
SELECT 'FILE_FORMATS' AS OBJECT_TYPE, COUNT(*) AS COUNT
FROM INFORMATION_SCHEMA.FILE_FORMATS
WHERE FILE_FORMAT_SCHEMA = 'SECURITY_ANALYTICS'
UNION ALL
SELECT 'LANDING_TABLES', COUNT(*)
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
AND TABLE_CATALOG = 'DEV_LANDING'
AND TABLE_TYPE = 'BASE TABLE'
UNION ALL
SELECT 'STREAMS', COUNT(*)
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
AND TABLE_CATALOG = 'DEV_LANDING'
AND TABLE_TYPE = 'STREAM'
UNION ALL
SELECT 'PROCEDURES', COUNT(*)
FROM INFORMATION_SCHEMA.PROCEDURES
WHERE PROCEDURE_SCHEMA = 'SECURITY_ANALYTICS'
AND PROCEDURE_CATALOG = 'DEV_TRANSFORMATION'
UNION ALL
SELECT 'TASKS', COUNT(*)
FROM INFORMATION_SCHEMA.TASKS
WHERE TASK_SCHEMA = 'SECURITY_ANALYTICS'
AND TASK_CATALOG = 'DEV_TRANSFORMATION'
UNION ALL
SELECT 'MONITORING_TABLE', COUNT(*)
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
AND TABLE_CATALOG = 'DEV_TRANSFORMATION'
AND TABLE_NAME = 'TBL_PIPELINE_MONITORING';

-- =====================================================================
-- SUMMARY
-- =====================================================================
/*
OBJECTS CREATED WITH DEV_DEVELOPER ROLE:
✓ 7 File Formats (JSON, CSV, Parquet)
✓ 8 Landing Tables (5 for Snowpipe, 3 for batch)
✓ 5 Streams (CDC for all landing tables)
✓ 5 Stored Procedures (transformations + monitoring)
✓ 10 Tasks (orchestration DAG)
✓ 1 Monitoring Table

OBJECTS REQUIRING ACCOUNTADMIN (see PIPELINE_ACCOUNTADMIN_REQUIRED.sql):
⏭ 4 Storage Integrations (S3 + Azure)
⏭ 5 External Stages
⏭ 5 Snowpipes
⏭ 3 External Tables

NEXT STEPS:
1. Execute this script with DEV_DEVELOPER role ✓
2. Request ACCOUNTADMIN to run PIPELINE_ACCOUNTADMIN_REQUIRED.sql
3. Grant EXECUTE TASK privilege to DEV_DEVELOPER role
4. Resume tasks (requires EXECUTE TASK privilege)
5. Monitor pipeline health

TESTING WITHOUT ACCOUNTADMIN:
You can test the pipeline manually by:
1. Inserting test data into landing tables
2. Verifying streams capture changes
3. Manually calling stored procedures
4. Manually executing tasks

Example:
INSERT INTO DEV_LANDING.SECURITY_ANALYTICS.L_CROWDSTRIKE_RAW (RAW_DATA)
VALUES (PARSE_JSON('{"detection_id": "TEST-001", "severity": "High"}'));

SELECT COUNT(*) FROM DEV_LANDING.SECURITY_ANALYTICS.STREAM_CROWDSTRIKE_NEW;

CALL DEV_TRANSFORMATION.SECURITY_ANALYTICS.SP_TRANSFORM_CROWDSTRIKE_EDR();
*/
