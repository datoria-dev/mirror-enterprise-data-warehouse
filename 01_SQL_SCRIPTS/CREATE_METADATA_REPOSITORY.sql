/*
================================================================================
SECURITY_ANALYTICS Metadata Repository - Central Metadata Management
================================================================================

This script creates a centralized metadata repository that will:
1. Store column metadata for all services
2. Track table statistics (row counts, last updated, etc.)
3. Serve as reference for Streamlit apps and dashboards
4. Enable automated documentation
5. Support data quality monitoring

Author: GenericCorp Data Engineering Team
Date: 2025-10-24
Version: 1.0
================================================================================
*/

USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;
USE DATABASE DEV_TRANSFORMATION;

-- ============================================================================
-- STEP 1: Create Metadata Schemas
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS DEV_TRANSFORMATION.METADATA
    COMMENT = 'Centralized metadata repository for SECURITY_ANALYTICS project';

CREATE SCHEMA IF NOT EXISTS DEV_TRANSFORMATION.METADATA_EXPORTS
    COMMENT = 'Storage for metadata exports (CSV/JSON results)';

USE SCHEMA METADATA;

-- ============================================================================
-- STEP 2: Create Metadata Tables
-- ============================================================================

-- -----------------------------------------------------------------------------
-- Table: TABLE_REGISTRY
-- Purpose: Master registry of all tables in the SECURITY_ANALYTICS project
-- -----------------------------------------------------------------------------

CREATE OR REPLACE TABLE TABLE_REGISTRY (
    TABLE_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    SERVICE_NAME VARCHAR(100) NOT NULL,
    DATABASE_NAME VARCHAR(100) NOT NULL,
    SCHEMA_NAME VARCHAR(100) NOT NULL,
    TABLE_NAME VARCHAR(200) NOT NULL,
    TABLE_TYPE VARCHAR(50),  -- TABLE, VIEW, MATERIALIZED VIEW
    DATA_LAYER VARCHAR(50),  -- Landing, Transformation, Reporting
    DESCRIPTION TEXT,
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    ROW_COUNT NUMBER,
    LAST_UPDATED TIMESTAMP_LTZ,
    CREATED_DATE TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    MODIFIED_DATE TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CREATED_BY VARCHAR(100) DEFAULT CURRENT_USER(),
    CONSTRAINT UK_TABLE_REGISTRY UNIQUE (DATABASE_NAME, SCHEMA_NAME, TABLE_NAME)
)
COMMENT = 'Master registry of all tables in SECURITY_ANALYTICS project';

-- -----------------------------------------------------------------------------
-- Table: COLUMN_METADATA
-- Purpose: Detailed column-level metadata
-- -----------------------------------------------------------------------------

CREATE OR REPLACE TABLE COLUMN_METADATA (
    COLUMN_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    TABLE_ID NUMBER NOT NULL,
    COLUMN_NAME VARCHAR(200) NOT NULL,
    DATA_TYPE VARCHAR(100) NOT NULL,
    IS_NULLABLE VARCHAR(3),  -- YES, NO
    ORDINAL_POSITION NUMBER NOT NULL,
    COLUMN_DEFAULT TEXT,
    COLUMN_COMMENT TEXT,
    IS_PRIMARY_KEY BOOLEAN DEFAULT FALSE,
    IS_FOREIGN_KEY BOOLEAN DEFAULT FALSE,
    SAMPLE_VALUES VARIANT,  -- Store sample values as JSON array
    DISTINCT_COUNT NUMBER,
    NULL_COUNT NUMBER,
    MIN_VALUE VARCHAR(500),
    MAX_VALUE VARCHAR(500),
    CREATED_DATE TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    MODIFIED_DATE TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CONSTRAINT FK_COLUMN_TABLE FOREIGN KEY (TABLE_ID) REFERENCES TABLE_REGISTRY(TABLE_ID)
)
COMMENT = 'Column-level metadata for all tables';

-- -----------------------------------------------------------------------------
-- Table: PROCEDURE_EXECUTION_LOG
-- Purpose: Log all stored procedure executions for monitoring and debugging
-- -----------------------------------------------------------------------------

CREATE OR REPLACE TABLE PROCEDURE_EXECUTION_LOG (
    LOG_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    PROCEDURE_NAME VARCHAR(200) NOT NULL,
    EXECUTION_START TIMESTAMP_LTZ NOT NULL,
    EXECUTION_END TIMESTAMP_LTZ,
    EXECUTION_DURATION_SECONDS NUMBER,
    STATUS VARCHAR(50),  -- SUCCESS, FAILED, RUNNING
    ROWS_PROCESSED NUMBER,
    TABLES_PROCESSED NUMBER,
    COLUMNS_PROCESSED NUMBER,
    ERROR_MESSAGE TEXT,
    EXECUTION_DETAILS VARIANT,  -- JSON with detailed metrics
    EXECUTED_BY VARCHAR(100) DEFAULT CURRENT_USER(),
    CREATED_DATE TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'Execution log for all stored procedures in metadata repository';

-- -----------------------------------------------------------------------------
-- Table: TABLE_STATISTICS
-- Purpose: Historical statistics for tables
-- -----------------------------------------------------------------------------

CREATE OR REPLACE TABLE TABLE_STATISTICS (
    STAT_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    TABLE_ID NUMBER NOT NULL,
    SNAPSHOT_DATE DATE NOT NULL,
    ROW_COUNT NUMBER,
    SIZE_BYTES NUMBER,
    COLUMN_COUNT NUMBER,
    LAST_MODIFIED TIMESTAMP_LTZ,
    CREATED_DATE TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CONSTRAINT FK_STATS_TABLE FOREIGN KEY (TABLE_ID) REFERENCES TABLE_REGISTRY(TABLE_ID),
    CONSTRAINT UK_TABLE_STATS UNIQUE (TABLE_ID, SNAPSHOT_DATE)
)
COMMENT = 'Historical statistics tracking for tables';

-- -----------------------------------------------------------------------------
-- Table: SERVICE_CATALOG
-- Purpose: Catalog of all services/sources
-- -----------------------------------------------------------------------------

CREATE OR REPLACE TABLE SERVICE_CATALOG (
    SERVICE_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    SERVICE_NAME VARCHAR(100) NOT NULL UNIQUE,
    SERVICE_DESCRIPTION TEXT,
    SERVICE_CATEGORY VARCHAR(100),  -- EDR, Email Security, Asset Management, etc.
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    PRIMARY_CONTACT VARCHAR(200),
    DOCUMENTATION_URL VARCHAR(500),
    REFRESH_FREQUENCY VARCHAR(50),  -- Daily, Hourly, Real-time
    LAST_REFRESH TIMESTAMP_LTZ,
    CREATED_DATE TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    MODIFIED_DATE TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'Catalog of all data services/sources';

-- -----------------------------------------------------------------------------
-- Table: DATA_QUALITY_RULES
-- Purpose: Store data quality rules for monitoring
-- -----------------------------------------------------------------------------

CREATE OR REPLACE TABLE DATA_QUALITY_RULES (
    RULE_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    TABLE_ID NUMBER,
    COLUMN_ID NUMBER,
    RULE_NAME VARCHAR(200) NOT NULL,
    RULE_TYPE VARCHAR(50),  -- NOT_NULL, RANGE, FORMAT, UNIQUENESS, etc.
    RULE_EXPRESSION TEXT,
    THRESHOLD_VALUE VARIANT,
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    SEVERITY VARCHAR(20),  -- Critical, Warning, Info
    CREATED_DATE TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    MODIFIED_DATE TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'Data quality rules and thresholds';

-- ============================================================================
-- STEP 3: Create Metadata Views
-- ============================================================================

-- -----------------------------------------------------------------------------
-- View: VW_TABLE_CATALOG
-- Purpose: User-friendly view of all tables
-- -----------------------------------------------------------------------------

CREATE OR REPLACE VIEW VW_TABLE_CATALOG AS
SELECT
    tr.TABLE_ID,
    sc.SERVICE_NAME,
    sc.SERVICE_CATEGORY,
    tr.DATABASE_NAME,
    tr.SCHEMA_NAME,
    tr.TABLE_NAME,
    tr.TABLE_TYPE,
    tr.DATA_LAYER,
    tr.DESCRIPTION,
    tr.ROW_COUNT as TOTAL_ROWS,
    tr.LAST_UPDATED,
    tr.IS_ACTIVE,
    COUNT(cm.COLUMN_ID) as TOTAL_COLUMNS,
    tr.DATABASE_NAME || '.' || tr.SCHEMA_NAME || '.' || tr.TABLE_NAME as FULL_TABLE_NAME,
    sc.REFRESH_FREQUENCY,
    sc.LAST_REFRESH,
    tr.CREATED_DATE
FROM TABLE_REGISTRY tr
LEFT JOIN SERVICE_CATALOG sc ON tr.SERVICE_NAME = sc.SERVICE_NAME
LEFT JOIN COLUMN_METADATA cm ON tr.TABLE_ID = cm.TABLE_ID
GROUP BY
    tr.TABLE_ID, sc.SERVICE_NAME, sc.SERVICE_CATEGORY,
    tr.DATABASE_NAME, tr.SCHEMA_NAME, tr.TABLE_NAME,
    tr.TABLE_TYPE, tr.DATA_LAYER, tr.DESCRIPTION,
    tr.ROW_COUNT, tr.LAST_UPDATED, tr.IS_ACTIVE,
    sc.REFRESH_FREQUENCY, sc.LAST_REFRESH, tr.CREATED_DATE;

-- -----------------------------------------------------------------------------
-- View: VW_COLUMN_CATALOG
-- Purpose: Complete column catalog with table context
-- -----------------------------------------------------------------------------

CREATE OR REPLACE VIEW VW_COLUMN_CATALOG AS
SELECT
    tr.SERVICE_NAME,
    tr.DATABASE_NAME,
    tr.SCHEMA_NAME,
    tr.TABLE_NAME,
    tr.DATA_LAYER,
    cm.COLUMN_NAME,
    cm.DATA_TYPE,
    cm.IS_NULLABLE,
    cm.ORDINAL_POSITION,
    cm.COLUMN_COMMENT,
    cm.IS_PRIMARY_KEY,
    cm.IS_FOREIGN_KEY,
    cm.DISTINCT_COUNT,
    cm.NULL_COUNT,
    cm.SAMPLE_VALUES,
    tr.DATABASE_NAME || '.' || tr.SCHEMA_NAME || '.' || tr.TABLE_NAME as FULL_TABLE_NAME
FROM COLUMN_METADATA cm
JOIN TABLE_REGISTRY tr ON cm.TABLE_ID = tr.TABLE_ID
WHERE tr.IS_ACTIVE = TRUE
ORDER BY tr.SERVICE_NAME, tr.TABLE_NAME, cm.ORDINAL_POSITION;

-- -----------------------------------------------------------------------------
-- View: VW_SERVICE_SUMMARY
-- Purpose: Summary statistics by service
-- -----------------------------------------------------------------------------

CREATE OR REPLACE VIEW VW_SERVICE_SUMMARY AS
SELECT
    sc.SERVICE_NAME,
    sc.SERVICE_CATEGORY,
    sc.SERVICE_DESCRIPTION,
    COUNT(DISTINCT tr.TABLE_ID) as TABLE_COUNT,
    SUM(tr.ROW_COUNT) as TOTAL_ROWS,
    COUNT(DISTINCT cm.COLUMN_ID) as TOTAL_COLUMNS,
    COUNT(DISTINCT CASE WHEN tr.IS_ACTIVE = TRUE THEN tr.TABLE_ID END) as ACTIVE_TABLES,
    ROUND(COUNT(DISTINCT cm.COLUMN_ID)::FLOAT / NULLIF(COUNT(DISTINCT tr.TABLE_ID), 0), 2) as AVG_COLUMNS_PER_TABLE,
    MAX(tr.LAST_UPDATED) as LAST_DATA_UPDATE,
    sc.REFRESH_FREQUENCY,
    sc.IS_ACTIVE
FROM SERVICE_CATALOG sc
LEFT JOIN TABLE_REGISTRY tr ON sc.SERVICE_NAME = tr.SERVICE_NAME AND tr.IS_ACTIVE = TRUE
LEFT JOIN COLUMN_METADATA cm ON tr.TABLE_ID = cm.TABLE_ID
GROUP BY
    sc.SERVICE_NAME, sc.SERVICE_CATEGORY, sc.SERVICE_DESCRIPTION,
    sc.REFRESH_FREQUENCY, sc.IS_ACTIVE;

-- ============================================================================
-- STEP 4: Populate Service Catalog
-- ============================================================================

INSERT INTO SERVICE_CATALOG (
    SERVICE_NAME,
    SERVICE_DESCRIPTION,
    SERVICE_CATEGORY,
    IS_ACTIVE,
    REFRESH_FREQUENCY
)
VALUES
    -- Endpoint Protection
    ('CrowdStrike', 'Endpoint Detection and Response (EDR) platform', 'Endpoint Protection', TRUE, 'Hourly'),
    ('Symantec', 'Antivirus and endpoint protection', 'Endpoint Protection', TRUE, 'Hourly'),
    ('McAfee', 'Endpoint security and threat protection', 'Endpoint Protection', TRUE, 'Hourly'),
    ('Sophos', 'Endpoint protection and EDR', 'Endpoint Protection', TRUE, 'Hourly'),
    ('TrendMicro', 'Threat protection and endpoint security', 'Endpoint Protection', TRUE, 'Hourly'),
    ('SentinelOne', 'Endpoint Detection and Response (EDR)', 'Endpoint Protection', TRUE, 'Hourly'),
    ('Defender', 'Microsoft Defender endpoint security', 'Endpoint Protection', FALSE, 'Hourly'),
    ('Trellix', 'EDR and threat detection', 'Endpoint Protection', TRUE, 'Hourly'),
    ('Cisco_AMP', 'Advanced malware protection', 'Endpoint Protection', TRUE, 'Hourly'),
    -- Vulnerability Management
    ('Qualys', 'Vulnerability scanning and assessment', 'Vulnerability Management', TRUE, 'Daily'),
    ('Tenable', 'Vulnerability assessment and management', 'Vulnerability Management', FALSE, 'Daily'),
    -- Threat Intelligence
    ('BitSight', 'Security posture rating and benchmarking', 'Threat Intelligence', TRUE, 'Daily'),
    ('CybelAngel', 'Cyber threat intelligence and data leak detection', 'Threat Intelligence', TRUE, 'Daily'),
    ('ZeroFox', 'External threat monitoring and brand protection', 'Threat Intelligence', TRUE, 'Daily'),
    ('Intel_Threats', 'Aggregated threat intelligence', 'Threat Intelligence', TRUE, 'Daily'),
    -- Identity & Access Management
    ('Ancon', 'Identity and access management', 'Identity & Access', TRUE, 'Daily'),
    ('Leviat', 'Privileged access and user monitoring', 'Identity & Access', TRUE, 'Daily'),
    -- SIEM
    ('Splunk', 'Security Information and Event Management', 'SIEM', FALSE, 'Real-time'),
    -- Cloud Security
    ('Zscaler', 'Secure web gateway and cloud security', 'Cloud Security', FALSE, 'Hourly'),
    -- Email Security
    ('Proofpoint', 'Email security and threat protection', 'Email Security', TRUE, 'Hourly'),
    -- Asset Management
    ('ServiceNow', 'IT Service Management and asset inventory', 'Asset Management', TRUE, 'Daily');

-- ============================================================================
-- STEP 5: Create Stored Procedure to Refresh Metadata
-- ============================================================================

CREATE OR REPLACE PROCEDURE SP_REFRESH_METADATA()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
DECLARE
    v_log_id NUMBER;
    v_start_time TIMESTAMP_LTZ := CURRENT_TIMESTAMP();
    v_end_time TIMESTAMP_LTZ;
    v_duration NUMBER;
    v_tables_processed NUMBER;
    v_columns_processed NUMBER;
    v_stats_processed NUMBER;
    v_result VARCHAR;
    v_status VARCHAR;
BEGIN
    -- Create log entry for this execution
    INSERT INTO PROCEDURE_EXECUTION_LOG (
        PROCEDURE_NAME,
        EXECUTION_START,
        STATUS
    )
    VALUES (
        'SP_REFRESH_METADATA',
        CURRENT_TIMESTAMP(),
        'RUNNING'
    );

    v_log_id := (SELECT MAX(LOG_ID) FROM PROCEDURE_EXECUTION_LOG);

    -- Clear existing metadata (keep registry structure)
    DELETE FROM COLUMN_METADATA;
    DELETE FROM TABLE_REGISTRY;

    -- Insert tables from INFORMATION_SCHEMA
    INSERT INTO TABLE_REGISTRY (
        SERVICE_NAME,
        DATABASE_NAME,
        SCHEMA_NAME,
        TABLE_NAME,
        TABLE_TYPE,
        DATA_LAYER,
        ROW_COUNT,
        LAST_UPDATED
    )
    SELECT
        CASE
            -- Endpoint Protection
            WHEN TABLE_NAME LIKE '%CROWDSTRIKE%' OR TABLE_NAME LIKE '%CROWD%STRIKE%' THEN 'CrowdStrike'
            WHEN TABLE_NAME LIKE '%SYMANTEC%' THEN 'Symantec'
            WHEN TABLE_NAME LIKE '%MCAFEE%' THEN 'McAfee'
            WHEN TABLE_NAME LIKE '%SOPHOS%' THEN 'Sophos'
            WHEN TABLE_NAME LIKE '%TRENDMICRO%' OR TABLE_NAME LIKE '%TREND%MICRO%' THEN 'TrendMicro'
            WHEN TABLE_NAME LIKE '%SENTINEL%' THEN 'SentinelOne'
            WHEN TABLE_NAME LIKE '%DEFENDER%' THEN 'Defender'
            WHEN TABLE_NAME LIKE '%TRELLIX%' THEN 'Trellix'
            WHEN TABLE_NAME LIKE '%CISCO%AMP%' OR TABLE_NAME LIKE '%AMP%' THEN 'Cisco_AMP'
            -- Vulnerability Management
            WHEN TABLE_NAME LIKE '%QUALYS%' THEN 'Qualys'
            WHEN TABLE_NAME LIKE '%TENABLE%' THEN 'Tenable'
            -- Threat Intelligence
            WHEN TABLE_NAME LIKE '%BITSIGHT%' OR TABLE_NAME LIKE '%BIT%SIGHT%' THEN 'BitSight'
            WHEN TABLE_NAME LIKE '%CYBELANGEL%' OR TABLE_NAME LIKE '%CYBEL%ANGEL%' THEN 'CybelAngel'
            WHEN TABLE_NAME LIKE '%ZEROFOX%' OR TABLE_NAME LIKE '%ZERO%FOX%' THEN 'ZeroFox'
            WHEN TABLE_NAME LIKE '%INTEL%THREAT%' OR TABLE_NAME LIKE '%THREAT%INTEL%' THEN 'Intel_Threats'
            -- Identity & Access Management
            WHEN TABLE_NAME LIKE '%ANCON%' THEN 'Ancon'
            WHEN TABLE_NAME LIKE '%LEVIAT%' THEN 'Leviat'
            -- SIEM
            WHEN TABLE_NAME LIKE '%SPLUNK%' THEN 'Splunk'
            -- Cloud Security
            WHEN TABLE_NAME LIKE '%ZSCALER%' THEN 'Zscaler'
            -- Email Security
            WHEN TABLE_NAME LIKE '%PROOFPOINT%' THEN 'Proofpoint'
            -- Asset Management
            WHEN TABLE_NAME IN ('SNOW') OR TABLE_NAME LIKE '%SERVICENOW%' THEN 'ServiceNow'
            ELSE 'Unknown'
        END as SERVICE_NAME,
        TABLE_CATALOG as DATABASE_NAME,
        TABLE_SCHEMA as SCHEMA_NAME,
        TABLE_NAME,
        TABLE_TYPE,
        CASE
            WHEN TABLE_CATALOG = 'DEV_LANDING' THEN 'Landing'
            WHEN TABLE_CATALOG = 'DEV_TRANSFORMATION' THEN 'Transformation'
            WHEN TABLE_CATALOG = 'DEV_REPORTING' THEN 'Reporting'
            ELSE 'Unknown'
        END as DATA_LAYER,
        ROW_COUNT,
        LAST_ALTERED
    FROM (
        SELECT * FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
        UNION ALL
        SELECT * FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
    )
    WHERE SERVICE_NAME != 'Unknown';

    v_tables_processed := (SELECT COUNT(*) FROM TABLE_REGISTRY);

    -- Insert columns from INFORMATION_SCHEMA
    INSERT INTO COLUMN_METADATA (
        TABLE_ID,
        COLUMN_NAME,
        DATA_TYPE,
        IS_NULLABLE,
        ORDINAL_POSITION,
        COLUMN_DEFAULT,
        COLUMN_COMMENT
    )
    SELECT
        tr.TABLE_ID,
        c.COLUMN_NAME,
        c.DATA_TYPE,
        c.IS_NULLABLE,
        c.ORDINAL_POSITION,
        c.COLUMN_DEFAULT,
        c.COMMENT
    FROM (
        SELECT * FROM DEV_LANDING.INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
        UNION ALL
        SELECT * FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
    ) c
    JOIN TABLE_REGISTRY tr
        ON c.TABLE_CATALOG = tr.DATABASE_NAME
        AND c.TABLE_SCHEMA = tr.SCHEMA_NAME
        AND c.TABLE_NAME = tr.TABLE_NAME;

    v_columns_processed := (SELECT COUNT(*) FROM COLUMN_METADATA);

    -- Insert statistics snapshot
    INSERT INTO TABLE_STATISTICS (TABLE_ID, SNAPSHOT_DATE, ROW_COUNT, COLUMN_COUNT)
    SELECT
        tr.TABLE_ID,
        CURRENT_DATE(),
        tr.ROW_COUNT,
        COUNT(cm.COLUMN_ID)
    FROM TABLE_REGISTRY tr
    LEFT JOIN COLUMN_METADATA cm ON tr.TABLE_ID = cm.TABLE_ID
    GROUP BY tr.TABLE_ID, tr.ROW_COUNT;

    v_stats_processed := (SELECT COUNT(*) FROM TABLE_STATISTICS WHERE SNAPSHOT_DATE = CURRENT_DATE());

    -- Calculate execution duration
    v_end_time := CURRENT_TIMESTAMP();
    v_duration := DATEDIFF(second, v_start_time, v_end_time);
    v_status := 'SUCCESS';

    -- Build result message
    v_result := 'Metadata refresh completed successfully: ' ||
                v_tables_processed || ' tables, ' ||
                v_columns_processed || ' columns, ' ||
                v_stats_processed || ' statistics processed in ' ||
                v_duration || ' seconds';

    -- Update log entry with success using direct values
    UPDATE PROCEDURE_EXECUTION_LOG
    SET
        EXECUTION_END = CURRENT_TIMESTAMP(),
        EXECUTION_DURATION_SECONDS = DATEDIFF(second, EXECUTION_START, CURRENT_TIMESTAMP()),
        STATUS = 'SUCCESS',
        TABLES_PROCESSED = (SELECT COUNT(*) FROM TABLE_REGISTRY),
        COLUMNS_PROCESSED = (SELECT COUNT(*) FROM COLUMN_METADATA),
        ROWS_PROCESSED = (SELECT COUNT(*) FROM TABLE_STATISTICS WHERE SNAPSHOT_DATE = CURRENT_DATE()),
        EXECUTION_DETAILS = OBJECT_CONSTRUCT(
            'tables_processed', (SELECT COUNT(*) FROM TABLE_REGISTRY),
            'columns_processed', (SELECT COUNT(*) FROM COLUMN_METADATA),
            'stats_processed', (SELECT COUNT(*) FROM TABLE_STATISTICS WHERE SNAPSHOT_DATE = CURRENT_DATE()),
            'duration_seconds', DATEDIFF(second, EXECUTION_START, CURRENT_TIMESTAMP()),
            'timestamp', CURRENT_TIMESTAMP()
        )
    WHERE LOG_ID = (SELECT MAX(LOG_ID) FROM PROCEDURE_EXECUTION_LOG);

    RETURN v_result;
END;
$$;

-- ============================================================================
-- STEP 6: Create Task for Daily Metadata Refresh
-- ============================================================================

CREATE OR REPLACE TASK TASK_DAILY_METADATA_REFRESH
    WAREHOUSE = DEV_WH
    SCHEDULE = 'USING CRON 0 2 * * * UTC'  -- Daily at 2 AM UTC
    COMMENT = 'Daily metadata refresh for SECURITY_ANALYTICS tables'
AS
    CALL SP_REFRESH_METADATA();

-- Note: Task starts in SUSPENDED state, activate with:
-- ALTER TASK TASK_DAILY_METADATA_REFRESH RESUME;

-- ============================================================================
-- STEP 7: Initial Metadata Load
-- ============================================================================

-- Run the stored procedure to populate metadata
CALL SP_REFRESH_METADATA();

-- ============================================================================
-- STEP 8: Verify Metadata Repository
-- ============================================================================

-- View service summary
SELECT * FROM VW_SERVICE_SUMMARY
ORDER BY SERVICE_NAME;

-- View table catalog
SELECT * FROM VW_TABLE_CATALOG
ORDER BY SERVICE_NAME, TABLE_NAME;

-- View column catalog (limited)
SELECT * FROM VW_COLUMN_CATALOG
WHERE SERVICE_NAME = 'SentinelOne'
ORDER BY TABLE_NAME, ORDINAL_POSITION
LIMIT 100;

-- ============================================================================
-- STEP 9: Monitor Stored Procedure Execution Logs
-- ============================================================================

-- View most recent execution log
SELECT
    LOG_ID,
    PROCEDURE_NAME,
    EXECUTION_START,
    EXECUTION_END,
    EXECUTION_DURATION_SECONDS,
    STATUS,
    TABLES_PROCESSED,
    COLUMNS_PROCESSED,
    ROWS_PROCESSED,
    ERROR_MESSAGE
FROM PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 1;

-- View execution history (last 10 runs)
SELECT
    LOG_ID,
    PROCEDURE_NAME,
    EXECUTION_START,
    EXECUTION_DURATION_SECONDS,
    STATUS,
    TABLES_PROCESSED,
    COLUMNS_PROCESSED,
    ERROR_MESSAGE
FROM PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 10;

-- View execution statistics
SELECT
    STATUS,
    COUNT(*) as EXECUTION_COUNT,
    AVG(EXECUTION_DURATION_SECONDS) as AVG_DURATION_SECONDS,
    MIN(EXECUTION_DURATION_SECONDS) as MIN_DURATION_SECONDS,
    MAX(EXECUTION_DURATION_SECONDS) as MAX_DURATION_SECONDS,
    SUM(TABLES_PROCESSED) as TOTAL_TABLES_PROCESSED,
    SUM(COLUMNS_PROCESSED) as TOTAL_COLUMNS_PROCESSED
FROM PROCEDURE_EXECUTION_LOG
GROUP BY STATUS
ORDER BY STATUS;

-- Check statistics
SELECT
    sc.SERVICE_NAME,
    COUNT(DISTINCT tr.TABLE_ID) as TABLES,
    COUNT(DISTINCT cm.COLUMN_ID) as COLUMNS,
    SUM(tr.ROW_COUNT) as TOTAL_ROWS
FROM SERVICE_CATALOG sc
LEFT JOIN TABLE_REGISTRY tr ON sc.SERVICE_NAME = tr.SERVICE_NAME
LEFT JOIN COLUMN_METADATA cm ON tr.TABLE_ID = cm.TABLE_ID
GROUP BY sc.SERVICE_NAME
ORDER BY sc.SERVICE_NAME;

-- ============================================================================
-- USAGE EXAMPLES
-- ============================================================================

/*
-- Example 1: Get all columns for SentinelOne endpoints table
SELECT
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION
FROM VW_COLUMN_CATALOG
WHERE SERVICE_NAME = 'SentinelOne'
  AND TABLE_NAME = 'FACT_SENTINEL_ENDPOINTS'
ORDER BY ORDINAL_POSITION;

-- Example 2: Get table statistics for a service
SELECT
    TABLE_NAME,
    ROW_COUNT,
    COLUMN_COUNT,
    LAST_UPDATED
FROM VW_TABLE_CATALOG
WHERE SERVICE_NAME = 'Proofpoint'
ORDER BY ROW_COUNT DESC;

-- Example 3: Find tables with specific column
SELECT DISTINCT
    SERVICE_NAME,
    TABLE_NAME,
    DATA_LAYER
FROM VW_COLUMN_CATALOG
WHERE COLUMN_NAME LIKE '%TIMESTAMP%'
ORDER BY SERVICE_NAME, TABLE_NAME;

-- Example 4: Get historical row count trends
SELECT
    tr.SERVICE_NAME,
    tr.TABLE_NAME,
    ts.SNAPSHOT_DATE,
    ts.ROW_COUNT
FROM TABLE_STATISTICS ts
JOIN TABLE_REGISTRY tr ON ts.TABLE_ID = tr.TABLE_ID
WHERE tr.SERVICE_NAME = 'Proofpoint'
ORDER BY tr.TABLE_NAME, ts.SNAPSHOT_DATE;

-- Example 5: Check data freshness by service
SELECT
    SERVICE_NAME,
    TABLE_NAME,
    ROW_COUNT,
    LAST_UPDATED,
    DATEDIFF(day, LAST_UPDATED, CURRENT_TIMESTAMP()) as DAYS_SINCE_UPDATE
FROM VW_TABLE_CATALOG
WHERE IS_ACTIVE = TRUE
ORDER BY DAYS_SINCE_UPDATE DESC;
*/

-- ============================================================================
-- MAINTENANCE QUERIES
-- ============================================================================

/*
-- Manual metadata refresh
CALL SP_REFRESH_METADATA();

-- Activate daily task
ALTER TASK TASK_DAILY_METADATA_REFRESH RESUME;

-- Suspend daily task
ALTER TASK TASK_DAILY_METADATA_REFRESH SUSPEND;

-- Check task status
SHOW TASKS LIKE 'TASK_DAILY_METADATA_REFRESH';

-- View task history
SELECT *
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    TASK_NAME => 'TASK_DAILY_METADATA_REFRESH'
))
ORDER BY SCHEDULED_TIME DESC
LIMIT 10;
*/
