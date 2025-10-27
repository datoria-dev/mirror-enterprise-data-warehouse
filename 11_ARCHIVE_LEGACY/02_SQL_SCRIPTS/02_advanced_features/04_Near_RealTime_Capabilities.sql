-- ============================================================================
-- ENHANCEMENT 4: NEAR REAL-TIME CAPABILITIES
-- ============================================================================
-- Purpose: Implement Snowpipe, Streams, and real-time monitoring for critical events
-- Author: Data Engineering Team
-- Date: 2025-10-07
-- Estimated Effort: 64 hours
-- ============================================================================

USE ROLE ACCOUNTADMIN;  -- Required for Snowpipe and external stage creation
USE WAREHOUSE DEV_WH;
USE DATABASE DEV_LANDING;
USE SCHEMA SECURITY_ANALYTICS;

-- ============================================================================
-- SECTION 1: EXTERNAL STAGES FOR AUTO-INGESTION
-- ============================================================================

-- Stage for EDR Threat Events (AWS S3)
CREATE STAGE IF NOT EXISTS STAGE_EDR_THREATS_REALTIME
    URL = 's3://GenericCorp-security-data/edr-threats/'
    CREDENTIALS = (AWS_KEY_ID = '<AWS_ACCESS_KEY>' AWS_SECRET_KEY = '<AWS_SECRET_KEY>')
    FILE_FORMAT = (
        TYPE = JSON
        STRIP_OUTER_ARRAY = TRUE
        DATE_FORMAT = 'AUTO'
        TIMESTAMP_FORMAT = 'AUTO'
    )
    COMMENT = 'External stage for real-time EDR threat data from S3';

-- Stage for Critical Vulnerabilities (AWS S3)
CREATE STAGE IF NOT EXISTS STAGE_CRITICAL_VULNS_REALTIME
    URL = 's3://GenericCorp-security-data/critical-vulns/'
    CREDENTIALS = (AWS_KEY_ID = '<AWS_ACCESS_KEY>' AWS_SECRET_KEY = '<AWS_SECRET_KEY>')
    FILE_FORMAT = (
        TYPE = JSON
        STRIP_OUTER_ARRAY = TRUE
    )
    COMMENT = 'External stage for real-time critical vulnerability alerts';

-- Stage for Phishing Incidents (AWS S3)
CREATE STAGE IF NOT EXISTS STAGE_PHISHING_INCIDENTS_REALTIME
    URL = 's3://GenericCorp-security-data/phishing-incidents/'
    CREDENTIALS = (AWS_KEY_ID = '<AWS_ACCESS_KEY>' AWS_SECRET_KEY = '<AWS_SECRET_KEY>')
    FILE_FORMAT = (TYPE = JSON)
    COMMENT = 'External stage for real-time phishing incident data';

-- ============================================================================
-- SECTION 2: REAL-TIME LANDING TABLES
-- ============================================================================

-- Real-time EDR Threats
CREATE TABLE IF NOT EXISTS L_EDR_THREATS_REALTIME (
    THREAT_ID VARCHAR(255),
    ENDPOINT_ID VARCHAR(255),
    HOSTNAME VARCHAR(255),
    IP_ADDRESS VARCHAR(50),
    THREAT_NAME VARCHAR(255),
    THREAT_TYPE VARCHAR(100),  -- 'Malware', 'Ransomware', 'Exploit', 'PUA'
    SEVERITY VARCHAR(50),  -- 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    EDR_PLATFORM VARCHAR(50),  -- 'CrowdStrike', 'SentinelOne', 'Cisco AMP'
    DETECTION_TIME TIMESTAMP,
    THREAT_STATUS VARCHAR(50),  -- 'Detected', 'Quarantined', 'Blocked', 'Cleaned'
    FILE_PATH VARCHAR(1000),
    FILE_HASH VARCHAR(256),
    PROCESS_NAME VARCHAR(500),
    OPCO_CODE VARCHAR(50),

    -- Metadata
    INGESTED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    SOURCE_FILE VARCHAR(500),
    RAW_JSON VARIANT
)
COMMENT = 'Real-time landing for EDR threat detections - Auto-ingested via Snowpipe';

-- Real-time Critical Vulnerabilities
CREATE TABLE IF NOT EXISTS L_CRITICAL_VULNS_REALTIME (
    VULN_ID VARCHAR(255),
    HOST_ID VARCHAR(255),
    HOSTNAME VARCHAR(255),
    CVE_ID VARCHAR(50),
    VULN_TITLE VARCHAR(500),
    SEVERITY VARCHAR(50),
    CVSS_SCORE FLOAT,
    DETECTION_TIME TIMESTAMP,
    IS_EXPLOITED_IN_WILD BOOLEAN,
    PATCH_AVAILABLE BOOLEAN,
    SCANNER_SOURCE VARCHAR(50),  -- 'Qualys', 'Tenable', 'Rapid7'

    -- Metadata
    INGESTED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    RAW_JSON VARIANT
)
COMMENT = 'Real-time landing for critical vulnerability detections';

-- Real-time Phishing Incidents
CREATE TABLE IF NOT EXISTS L_PHISHING_INCIDENTS_REALTIME (
    INCIDENT_ID VARCHAR(255),
    USER_EMAIL VARCHAR(255),
    SENDER_EMAIL VARCHAR(255),
    SUBJECT VARCHAR(500),
    RECEIVED_TIME TIMESTAMP,
    CLICKED_LINK BOOLEAN,
    REPORTED_BY_USER BOOLEAN,
    MALICIOUS_SCORE FLOAT,
    OPCO_CODE VARCHAR(50),

    -- Metadata
    INGESTED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    RAW_JSON VARIANT
)
COMMENT = 'Real-time landing for phishing incidents';

-- ============================================================================
-- SECTION 3: SNOWPIPE DEFINITIONS (AUTO-INGESTION)
-- ============================================================================

-- Snowpipe for EDR Threats
CREATE OR REPLACE PIPE PIPE_EDR_THREATS_REALTIME
    AUTO_INGEST = TRUE
    AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:123456789012:GenericCorp-edr-threats-topic'
    COMMENT = 'Auto-ingest EDR threat events from S3 to Snowflake'
AS
COPY INTO L_EDR_THREATS_REALTIME (
    THREAT_ID,
    ENDPOINT_ID,
    HOSTNAME,
    IP_ADDRESS,
    THREAT_NAME,
    THREAT_TYPE,
    SEVERITY,
    EDR_PLATFORM,
    DETECTION_TIME,
    THREAT_STATUS,
    FILE_PATH,
    FILE_HASH,
    PROCESS_NAME,
    OPCO_CODE,
    SOURCE_FILE,
    RAW_JSON
)
FROM (
    SELECT
        $1:threat_id::VARCHAR,
        $1:endpoint_id::VARCHAR,
        $1:hostname::VARCHAR,
        $1:ip_address::VARCHAR,
        $1:threat_name::VARCHAR,
        $1:threat_type::VARCHAR,
        $1:severity::VARCHAR,
        $1:edr_platform::VARCHAR,
        $1:detection_time::TIMESTAMP,
        $1:status::VARCHAR,
        $1:file_path::VARCHAR,
        $1:file_hash::VARCHAR,
        $1:process_name::VARCHAR,
        $1:opco_code::VARCHAR,
        METADATA$FILENAME,
        $1
    FROM @STAGE_EDR_THREATS_REALTIME
)
FILE_FORMAT = (TYPE = JSON);

-- Snowpipe for Critical Vulnerabilities
CREATE OR REPLACE PIPE PIPE_CRITICAL_VULNS_REALTIME
    AUTO_INGEST = TRUE
    AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:123456789012:GenericCorp-critical-vulns-topic'
AS
COPY INTO L_CRITICAL_VULNS_REALTIME
FROM (
    SELECT
        $1:vuln_id::VARCHAR,
        $1:host_id::VARCHAR,
        $1:hostname::VARCHAR,
        $1:cve_id::VARCHAR,
        $1:title::VARCHAR,
        $1:severity::VARCHAR,
        $1:cvss_score::FLOAT,
        $1:detection_time::TIMESTAMP,
        $1:exploited_in_wild::BOOLEAN,
        $1:patch_available::BOOLEAN,
        $1:scanner::VARCHAR,
        $1
    FROM @STAGE_CRITICAL_VULNS_REALTIME
)
FILE_FORMAT = (TYPE = JSON);

-- Snowpipe for Phishing Incidents
CREATE OR REPLACE PIPE PIPE_PHISHING_INCIDENTS_REALTIME
    AUTO_INGEST = TRUE
    AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:123456789012:GenericCorp-phishing-topic'
AS
COPY INTO L_PHISHING_INCIDENTS_REALTIME
FROM (
    SELECT
        $1:incident_id::VARCHAR,
        $1:user_email::VARCHAR,
        $1:sender_email::VARCHAR,
        $1:subject::VARCHAR,
        $1:received_time::TIMESTAMP,
        $1:clicked_link::BOOLEAN,
        $1:reported::BOOLEAN,
        $1:score::FLOAT,
        $1:opco_code::VARCHAR,
        $1
    FROM @STAGE_PHISHING_INCIDENTS_REALTIME
)
FILE_FORMAT = (TYPE = JSON);

-- Show Snowpipe status and copy history
-- SHOW PIPES;
-- SELECT * FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(TABLE_NAME=>'L_EDR_THREATS_REALTIME', START_TIME=>DATEADD(hours, -1, CURRENT_TIMESTAMP())));

-- ============================================================================
-- SECTION 4: STREAMS FOR CHANGE DATA CAPTURE
-- ============================================================================

USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA SECURITY_ANALYTICS;

-- Stream on FACT_QUALYS to detect new critical vulnerabilities
CREATE OR REPLACE STREAM STREAM_NEW_CRITICAL_VULNS
    ON TABLE FACT_QUALYS
    COMMENT = 'Captures new critical vulnerabilities in real-time';

-- Stream on FACT_EDR to detect new threat events
CREATE OR REPLACE STREAM STREAM_NEW_EDR_THREATS
    ON TABLE FACT_EDR
    COMMENT = 'Captures new EDR threat detections in real-time';

-- Stream on DIM_HOST to detect new assets
CREATE OR REPLACE STREAM STREAM_NEW_ASSETS
    ON TABLE DIM_HOST
    COMMENT = 'Captures new assets added to inventory';

-- ============================================================================
-- SECTION 5: REAL-TIME ALERT TABLES
-- ============================================================================

USE DATABASE DEV_REPORTING;
USE SCHEMA SECURITY_ANALYTICS;

-- Critical Vulnerability Alerts
CREATE TABLE IF NOT EXISTS TBL_ALERT_CRITICAL_VULNERABILITIES (
    ALERT_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    ALERT_TIME TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    HOST_ID VARCHAR(255),
    HOSTNAME VARCHAR(255),
    OPCO_ID NUMBER,
    VULN_ID VARCHAR(255),
    CVE_ID VARCHAR(50),
    VULN_TITLE VARCHAR(500),
    SEVERITY VARCHAR(50),
    CVSS_SCORE FLOAT,
    IS_EXPLOITED_IN_WILD BOOLEAN,
    DAYS_SINCE_DETECTION NUMBER,
    ALERT_STATUS VARCHAR(50) DEFAULT 'OPEN',  -- 'OPEN', 'ACKNOWLEDGED', 'RESOLVED'
    ACKNOWLEDGED_BY VARCHAR(255),
    ACKNOWLEDGED_AT TIMESTAMP,
    RESOLVED_AT TIMESTAMP
)
COMMENT = 'Real-time alerts for critical vulnerabilities requiring immediate attention';

-- EDR Threat Alerts
CREATE TABLE IF NOT EXISTS TBL_ALERT_EDR_THREATS (
    ALERT_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    ALERT_TIME TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    THREAT_ID VARCHAR(255),
    ENDPOINT_ID VARCHAR(255),
    HOSTNAME VARCHAR(255),
    OPCO_ID NUMBER,
    THREAT_NAME VARCHAR(255),
    THREAT_TYPE VARCHAR(100),
    SEVERITY VARCHAR(50),
    EDR_PLATFORM VARCHAR(50),
    DETECTION_TIME TIMESTAMP,
    THREAT_STATUS VARCHAR(50),
    ALERT_STATUS VARCHAR(50) DEFAULT 'OPEN',
    ACKNOWLEDGED_BY VARCHAR(255),
    ACKNOWLEDGED_AT TIMESTAMP
)
COMMENT = 'Real-time alerts for EDR threat detections';

-- Asset Coverage Gaps
CREATE TABLE IF NOT EXISTS TBL_ALERT_ASSET_COVERAGE_GAPS (
    ALERT_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    ALERT_TIME TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    HOST_ID VARCHAR(255),
    HOSTNAME VARCHAR(255),
    OPCO_ID NUMBER,
    MISSING_EDR BOOLEAN DEFAULT FALSE,
    MISSING_VULN_SCAN BOOLEAN DEFAULT FALSE,
    MISSING_PATCH_MGMT BOOLEAN DEFAULT FALSE,
    DAYS_UNPROTECTED NUMBER,
    ALERT_STATUS VARCHAR(50) DEFAULT 'OPEN'
)
COMMENT = 'Alerts for new assets missing critical security controls';

-- ============================================================================
-- SECTION 6: REAL-TIME PROCESSING PROCEDURES
-- ============================================================================

-- Procedure to process new critical vulnerabilities
CREATE OR REPLACE PROCEDURE SP_PROCESS_NEW_CRITICAL_VULNS()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
DECLARE
    processed_count NUMBER DEFAULT 0;
BEGIN
    -- Insert alerts for new critical vulnerabilities
    INSERT INTO TBL_ALERT_CRITICAL_VULNERABILITIES (
        ALERT_TIME, HOST_ID, HOSTNAME, OPCO_ID, VULN_ID, CVE_ID, VULN_TITLE,
        SEVERITY, CVSS_SCORE, IS_EXPLOITED_IN_WILD, DAYS_SINCE_DETECTION
    )
    SELECT
        CURRENT_TIMESTAMP(),
        s.HOST_ID,
        h.HOSTNAME,
        h.OPCO_ID,
        s.VULN_ID,
        s.CVE_ID,
        s.VULN_TITLE,
        s.SEVERITY,
        s.CVSS_SCORE,
        s.IS_EXPLOITED_IN_WILD,
        DATEDIFF('day', s.FIRST_DETECTED_DATE, CURRENT_DATE())
    FROM STREAM_NEW_CRITICAL_VULNS s
    LEFT JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST h ON s.HOST_ID = h.HOST_ID
    WHERE s.METADATA$ACTION = 'INSERT'
      AND s.SEVERITY = 'CRITICAL'
      AND s.CVSS_SCORE >= 9.0;

    SET processed_count = SQLROWCOUNT;
    RETURN 'Processed ' || :processed_count || ' new critical vulnerability alerts';
END;
$$;

-- Procedure to process new EDR threats
CREATE OR REPLACE PROCEDURE SP_PROCESS_NEW_EDR_THREATS()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
DECLARE
    processed_count NUMBER DEFAULT 0;
BEGIN
    INSERT INTO TBL_ALERT_EDR_THREATS (
        ALERT_TIME, THREAT_ID, ENDPOINT_ID, HOSTNAME, OPCO_ID, THREAT_NAME,
        THREAT_TYPE, SEVERITY, EDR_PLATFORM, DETECTION_TIME, THREAT_STATUS
    )
    SELECT
        CURRENT_TIMESTAMP(),
        s.THREAT_ID,
        s.ENDPOINT_ID,
        h.HOSTNAME,
        h.OPCO_ID,
        s.THREAT_NAME,
        s.THREAT_TYPE,
        s.SEVERITY,
        s.EDR_PLATFORM,
        s.DETECTION_TIME,
        s.THREAT_STATUS
    FROM STREAM_NEW_EDR_THREATS s
    LEFT JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST h ON s.ENDPOINT_ID = h.HOST_ID
    WHERE s.METADATA$ACTION = 'INSERT'
      AND s.SEVERITY IN ('CRITICAL', 'HIGH')
      AND s.THREAT_TYPE IN ('Malware', 'Ransomware', 'Exploit');

    SET processed_count = SQLROWCOUNT;
    RETURN 'Processed ' || :processed_count || ' new EDR threat alerts';
END;
$$;

-- Procedure to check new assets for coverage gaps
CREATE OR REPLACE PROCEDURE SP_CHECK_NEW_ASSET_COVERAGE()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
DECLARE
    processed_count NUMBER DEFAULT 0;
BEGIN
    INSERT INTO TBL_ALERT_ASSET_COVERAGE_GAPS (
        ALERT_TIME, HOST_ID, HOSTNAME, OPCO_ID,
        MISSING_EDR, MISSING_VULN_SCAN, MISSING_PATCH_MGMT, DAYS_UNPROTECTED
    )
    SELECT
        CURRENT_TIMESTAMP(),
        s.HOST_ID,
        s.HOSTNAME,
        s.OPCO_ID,
        NOT EXISTS (SELECT 1 FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_EDR e WHERE e.HOST_ID = s.HOST_ID AND e.AGENT_STATUS = 'Healthy') as MISSING_EDR,
        NOT EXISTS (SELECT 1 FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_QUALYS q WHERE q.HOST_ID = s.HOST_ID) as MISSING_VULN_SCAN,
        NOT EXISTS (SELECT 1 FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_PATCHES p WHERE p.HOST_ID = s.HOST_ID) as MISSING_PATCH_MGMT,
        DATEDIFF('day', s.CREATED_DATE, CURRENT_DATE())
    FROM STREAM_NEW_ASSETS s
    WHERE s.METADATA$ACTION = 'INSERT'
    HAVING (MISSING_EDR OR MISSING_VULN_SCAN);

    SET processed_count = SQLROWCOUNT;
    RETURN 'Identified ' || :processed_count || ' new assets with coverage gaps';
END;
$$;

-- ============================================================================
-- SECTION 7: REAL-TIME MONITORING VIEWS
-- ============================================================================

-- View: Threats detected in last 15 minutes
CREATE OR REPLACE VIEW VW_REALTIME_THREATS_LAST_15MIN
COMMENT = 'Real-time view of threats detected in the last 15 minutes'
AS
SELECT
    t.THREAT_ID,
    t.HOSTNAME,
    o.OPCO_NAME,
    o.REGION,
    t.THREAT_NAME,
    t.THREAT_TYPE,
    t.SEVERITY,
    t.EDR_PLATFORM,
    t.DETECTION_TIME,
    DATEDIFF('minute', t.DETECTION_TIME, CURRENT_TIMESTAMP()) as MINUTES_AGO,
    t.THREAT_STATUS,
    CASE
        WHEN t.SEVERITY = 'CRITICAL' AND t.THREAT_TYPE = 'Ransomware' THEN 100
        WHEN t.SEVERITY = 'CRITICAL' THEN 90
        WHEN t.SEVERITY = 'HIGH' THEN 75
        ELSE 50
    END as RISK_SCORE,
    CASE
        WHEN RISK_SCORE >= 90 THEN '🔴 CRITICAL'
        WHEN RISK_SCORE >= 75 THEN '🟠 HIGH'
        ELSE '🟡 MEDIUM'
    END as PRIORITY
FROM DEV_LANDING.SECURITY_ANALYTICS.L_EDR_THREATS_REALTIME t
LEFT JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST h ON t.ENDPOINT_ID = h.HOST_ID
LEFT JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_OPCO o ON h.OPCO_ID = o.OPCO_ID
WHERE t.DETECTION_TIME >= DATEADD('minute', -15, CURRENT_TIMESTAMP())
ORDER BY RISK_SCORE DESC, t.DETECTION_TIME DESC;

-- View: Critical vulnerabilities discovered today
CREATE OR REPLACE VIEW VW_REALTIME_CRITICAL_VULNS_TODAY
COMMENT = 'Critical vulnerabilities discovered today with exploit status'
AS
SELECT
    v.VULN_ID,
    v.CVE_ID,
    v.HOSTNAME,
    o.OPCO_NAME,
    v.VULN_TITLE,
    v.CVSS_SCORE,
    v.IS_EXPLOITED_IN_WILD,
    v.PATCH_AVAILABLE,
    v.DETECTION_TIME,
    DATEDIFF('hour', v.DETECTION_TIME, CURRENT_TIMESTAMP()) as HOURS_SINCE_DETECTION,
    CASE
        WHEN v.IS_EXPLOITED_IN_WILD THEN '🔴 ACTIVELY EXPLOITED'
        WHEN v.CVSS_SCORE >= 9.5 THEN '🟠 CRITICAL'
        ELSE '🟡 HIGH'
    END as URGENCY
FROM DEV_LANDING.SECURITY_ANALYTICS.L_CRITICAL_VULNS_REALTIME v
LEFT JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST h ON v.HOST_ID = h.HOST_ID
LEFT JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_OPCO o ON h.OPCO_ID = o.OPCO_ID
WHERE v.DETECTION_TIME >= CURRENT_DATE()
ORDER BY v.IS_EXPLOITED_IN_WILD DESC, v.CVSS_SCORE DESC;

-- View: Real-time security operations dashboard
CREATE OR REPLACE VIEW VW_REALTIME_SECURITY_OPERATIONS
COMMENT = 'Real-time security operations dashboard - Last 24 hours'
AS
SELECT
    -- Threats
    (SELECT COUNT(*) FROM DEV_LANDING.SECURITY_ANALYTICS.L_EDR_THREATS_REALTIME
     WHERE INGESTED_AT >= DATEADD('hour', -24, CURRENT_TIMESTAMP())) as "Total Threats (24h)",

    (SELECT COUNT(*) FROM DEV_LANDING.SECURITY_ANALYTICS.L_EDR_THREATS_REALTIME
     WHERE INGESTED_AT >= DATEADD('hour', -24, CURRENT_TIMESTAMP())
       AND SEVERITY = 'CRITICAL') as "Critical Threats (24h)",

    -- Vulnerabilities
    (SELECT COUNT(*) FROM DEV_LANDING.SECURITY_ANALYTICS.L_CRITICAL_VULNS_REALTIME
     WHERE INGESTED_AT >= DATEADD('hour', -24, CURRENT_TIMESTAMP())) as "New Critical Vulns (24h)",

    (SELECT COUNT(*) FROM DEV_LANDING.SECURITY_ANALYTICS.L_CRITICAL_VULNS_REALTIME
     WHERE INGESTED_AT >= DATEADD('hour', -24, CURRENT_TIMESTAMP())
       AND IS_EXPLOITED_IN_WILD = TRUE) as "Exploited Vulns (24h)",

    -- Phishing
    (SELECT COUNT(*) FROM DEV_LANDING.SECURITY_ANALYTICS.L_PHISHING_INCIDENTS_REALTIME
     WHERE INGESTED_AT >= DATEADD('hour', -24, CURRENT_TIMESTAMP())) as "Phishing Incidents (24h)",

    (SELECT COUNT(*) FROM DEV_LANDING.SECURITY_ANALYTICS.L_PHISHING_INCIDENTS_REALTIME
     WHERE INGESTED_AT >= DATEADD('hour', -24, CURRENT_TIMESTAMP())
       AND CLICKED_LINK = TRUE) as "Phishing Clicks (24h)",

    -- Alerts
    (SELECT COUNT(*) FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_ALERT_CRITICAL_VULNERABILITIES
     WHERE ALERT_TIME >= DATEADD('hour', -24, CURRENT_TIMESTAMP())
       AND ALERT_STATUS = 'OPEN') as "Open Critical Vuln Alerts",

    (SELECT COUNT(*) FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_ALERT_EDR_THREATS
     WHERE ALERT_TIME >= DATEADD('hour', -24, CURRENT_TIMESTAMP())
       AND ALERT_STATUS = 'OPEN') as "Open Threat Alerts",

    -- Latency metrics
    (SELECT AVG(DATEDIFF('second', DETECTION_TIME, INGESTED_AT))
     FROM DEV_LANDING.SECURITY_ANALYTICS.L_EDR_THREATS_REALTIME
     WHERE INGESTED_AT >= DATEADD('hour', -1, CURRENT_TIMESTAMP())) as "Avg Ingestion Latency (sec)",

    CURRENT_TIMESTAMP() as "Dashboard Updated";

-- ============================================================================
-- SECTION 8: AUTOMATED TASKS FOR STREAM PROCESSING
-- ============================================================================

-- Task to process new critical vulnerabilities every 5 minutes
CREATE OR REPLACE TASK TASK_PROCESS_NEW_CRITICAL_VULNS
    WAREHOUSE = DEV_WH
    SCHEDULE = '5 MINUTE'
    WHEN SYSTEM$STREAM_HAS_DATA('STREAM_NEW_CRITICAL_VULNS')
    COMMENT = 'Process new critical vulnerabilities from stream every 5 minutes'
AS
    CALL SP_PROCESS_NEW_CRITICAL_VULNS();

-- Task to process new EDR threats every 5 minutes
CREATE OR REPLACE TASK TASK_PROCESS_NEW_EDR_THREATS
    WAREHOUSE = DEV_WH
    SCHEDULE = '5 MINUTE'
    WHEN SYSTEM$STREAM_HAS_DATA('STREAM_NEW_EDR_THREATS')
AS
    CALL SP_PROCESS_NEW_EDR_THREATS();

-- Task to check new assets for coverage gaps every 15 minutes
CREATE OR REPLACE TASK TASK_CHECK_NEW_ASSET_COVERAGE
    WAREHOUSE = DEV_WH
    SCHEDULE = '15 MINUTE'
    WHEN SYSTEM$STREAM_HAS_DATA('STREAM_NEW_ASSETS')
AS
    CALL SP_CHECK_NEW_ASSET_COVERAGE();

-- Enable tasks
ALTER TASK TASK_PROCESS_NEW_CRITICAL_VULNS RESUME;
ALTER TASK TASK_PROCESS_NEW_EDR_THREATS RESUME;
ALTER TASK TASK_CHECK_NEW_ASSET_COVERAGE RESUME;

-- ============================================================================
-- SECTION 9: NOTIFICATION INTEGRATION (OPTIONAL)
-- ============================================================================

-- Email notification for critical alerts
-- CREATE NOTIFICATION INTEGRATION EMAIL_INTEGRATION
--     TYPE = EMAIL
--     ENABLED = TRUE;

-- Slack notification (requires setup)
-- CREATE NOTIFICATION INTEGRATION SLACK_INTEGRATION
--     TYPE = WEBHOOK
--     ENABLED = TRUE
--     WEBHOOK_URL = 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL';

-- ============================================================================
-- SECTION 10: TESTING AND VALIDATION
-- ============================================================================

-- Test 1: Check Snowpipe status
SHOW PIPES;
SELECT SYSTEM$PIPE_STATUS('PIPE_EDR_THREATS_REALTIME');

-- Test 2: Verify streams are created
SHOW STREAMS;

-- Test 3: Check real-time views
SELECT * FROM VW_REALTIME_THREATS_LAST_15MIN LIMIT 10;
SELECT * FROM VW_REALTIME_CRITICAL_VULNS_TODAY LIMIT 10;
SELECT * FROM VW_REALTIME_SECURITY_OPERATIONS;

-- Test 4: Manually trigger stream processing
CALL SP_PROCESS_NEW_CRITICAL_VULNS();
CALL SP_PROCESS_NEW_EDR_THREATS();
CALL SP_CHECK_NEW_ASSET_COVERAGE();

-- Test 5: Check alerts
SELECT COUNT(*) FROM TBL_ALERT_CRITICAL_VULNERABILITIES WHERE ALERT_STATUS = 'OPEN';
SELECT COUNT(*) FROM TBL_ALERT_EDR_THREATS WHERE ALERT_STATUS = 'OPEN';
SELECT COUNT(*) FROM TBL_ALERT_ASSET_COVERAGE_GAPS WHERE ALERT_STATUS = 'OPEN';

-- Test 6: Monitor Snowpipe ingestion history
SELECT *
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
    TABLE_NAME => 'L_EDR_THREATS_REALTIME',
    START_TIME => DATEADD(hours, -1, CURRENT_TIMESTAMP())
));

-- ============================================================================
-- SECTION 11: PERFORMANCE MONITORING
-- ============================================================================

-- View: Snowpipe performance metrics
CREATE OR REPLACE VIEW VW_SNOWPIPE_PERFORMANCE
AS
SELECT
    PIPE_NAME,
    FILE_NAME,
    FIRST_COMMIT_TIME,
    LAST_COMMIT_TIME,
    ROWS_PARSED,
    ROWS_LOADED,
    ERROR_COUNT,
    DATEDIFF('second', FIRST_COMMIT_TIME, LAST_COMMIT_TIME) as LOAD_DURATION_SEC
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
    START_TIME => DATEADD(hours, -24, CURRENT_TIMESTAMP())
))
ORDER BY LAST_COMMIT_TIME DESC;

-- View: Stream lag monitoring
CREATE OR REPLACE VIEW VW_STREAM_LAG_MONITORING
AS
SELECT
    'STREAM_NEW_CRITICAL_VULNS' as STREAM_NAME,
    SYSTEM$STREAM_HAS_DATA('STREAM_NEW_CRITICAL_VULNS') as HAS_DATA,
    (SELECT COUNT(*) FROM STREAM_NEW_CRITICAL_VULNS) as PENDING_ROWS
UNION ALL
SELECT
    'STREAM_NEW_EDR_THREATS',
    SYSTEM$STREAM_HAS_DATA('STREAM_NEW_EDR_THREATS'),
    (SELECT COUNT(*) FROM STREAM_NEW_EDR_THREATS)
UNION ALL
SELECT
    'STREAM_NEW_ASSETS',
    SYSTEM$STREAM_HAS_DATA('STREAM_NEW_ASSETS'),
    (SELECT COUNT(*) FROM STREAM_NEW_ASSETS);

-- ============================================================================
-- SUCCESS METRICS
-- ============================================================================
-- ✅ Snowpipe configured for auto-ingestion from S3
-- ✅ Real-time landing tables created
-- ✅ Streams configured for change data capture
-- ✅ Real-time alert tables and procedures implemented
-- ✅ Near real-time monitoring views created
-- ✅ Automated tasks scheduled for stream processing
-- ✅ Performance monitoring views created
-- ============================================================================

-- ============================================================================
-- CONFIGURATION NOTES FOR DEPLOYMENT
-- ============================================================================
/*
TO COMPLETE SETUP:

1. AWS S3 Configuration:
   - Create S3 buckets: GenericCorp-security-data/edr-threats/, /critical-vulns/, /phishing-incidents/
   - Configure S3 event notifications to SNS topics
   - Update AWS credentials in stage definitions

2. SNS Topic Configuration:
   - Create SNS topics in AWS
   - Subscribe Snowflake SQS queues (auto-created by Snowpipe)
   - Get SNS ARNs from: SHOW PIPES; (notification_channel column)

3. Data Source Configuration:
   - Configure EDR platforms to export JSON to S3
   - Configure vulnerability scanners to export critical findings
   - Set up phishing platform integrations

4. Notification Setup (Optional):
   - Configure email integration for critical alerts
   - Set up Slack webhook for real-time notifications

5. Testing:
   - Upload sample JSON files to S3
   - Verify auto-ingestion via: SELECT SYSTEM$PIPE_STATUS('PIPE_EDR_THREATS_REALTIME');
   - Monitor: SELECT * FROM VW_SNOWPIPE_PERFORMANCE;
*/
