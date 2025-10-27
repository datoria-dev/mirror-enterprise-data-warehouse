/*
================================================================================
Test Stored Procedure - SP_REFRESH_METADATA
================================================================================

This script tests the stored procedure before executing the complete script.
Useful for debugging and validation.

Date: 2025-10-24
================================================================================
*/

USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;
USE DATABASE DEV_TRANSFORMATION;

-- ============================================================================
-- TEST 1: Create minimal schemas and tables for testing
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS DEV_TRANSFORMATION.METADATA;
CREATE SCHEMA IF NOT EXISTS DEV_TRANSFORMATION.METADATA_EXPORTS;

USE SCHEMA METADATA;

-- Create execution log table
CREATE OR REPLACE TABLE PROCEDURE_EXECUTION_LOG (
    LOG_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    PROCEDURE_NAME VARCHAR(200) NOT NULL,
    EXECUTION_START TIMESTAMP_LTZ NOT NULL,
    EXECUTION_END TIMESTAMP_LTZ,
    EXECUTION_DURATION_SECONDS NUMBER,
    STATUS VARCHAR(50),
    ROWS_PROCESSED NUMBER,
    TABLES_PROCESSED NUMBER,
    COLUMNS_PROCESSED NUMBER,
    ERROR_MESSAGE TEXT,
    EXECUTION_DETAILS VARIANT,
    EXECUTED_BY VARCHAR(100) DEFAULT CURRENT_USER(),
    CREATED_DATE TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create table registry
CREATE OR REPLACE TABLE TABLE_REGISTRY (
    TABLE_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    SERVICE_NAME VARCHAR(100) NOT NULL,
    DATABASE_NAME VARCHAR(100) NOT NULL,
    SCHEMA_NAME VARCHAR(100) NOT NULL,
    TABLE_NAME VARCHAR(200) NOT NULL,
    TABLE_TYPE VARCHAR(50),
    DATA_LAYER VARCHAR(50),
    DESCRIPTION TEXT,
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    ROW_COUNT NUMBER,
    LAST_UPDATED TIMESTAMP_LTZ,
    CREATED_DATE TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    MODIFIED_DATE TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CREATED_BY VARCHAR(100) DEFAULT CURRENT_USER(),
    CONSTRAINT UK_TABLE_REGISTRY UNIQUE (DATABASE_NAME, SCHEMA_NAME, TABLE_NAME)
);

-- Create column metadata table
CREATE OR REPLACE TABLE COLUMN_METADATA (
    COLUMN_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    TABLE_ID NUMBER NOT NULL,
    COLUMN_NAME VARCHAR(200) NOT NULL,
    DATA_TYPE VARCHAR(100) NOT NULL,
    IS_NULLABLE VARCHAR(3),
    ORDINAL_POSITION NUMBER NOT NULL,
    COLUMN_DEFAULT TEXT,
    COLUMN_COMMENT TEXT,
    IS_PRIMARY_KEY BOOLEAN DEFAULT FALSE,
    IS_FOREIGN_KEY BOOLEAN DEFAULT FALSE,
    SAMPLE_VALUES VARIANT,
    DISTINCT_COUNT NUMBER,
    NULL_COUNT NUMBER,
    MIN_VALUE VARCHAR(500),
    MAX_VALUE VARCHAR(500),
    CREATED_DATE TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    MODIFIED_DATE TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CONSTRAINT FK_COLUMN_TABLE FOREIGN KEY (TABLE_ID) REFERENCES TABLE_REGISTRY(TABLE_ID)
);

-- Create statistics table
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
);

-- ============================================================================
-- TEST 2: Create simplified stored procedure
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
-- TEST 3: Execute stored procedure
-- ============================================================================

SELECT '🧪 TEST: Executing SP_REFRESH_METADATA()' as TEST_STEP;

CALL SP_REFRESH_METADATA();

-- ============================================================================
-- TEST 4: Verify results
-- ============================================================================

SELECT '✅ VERIFICATION: Check execution log' as TEST_STEP;

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
    ERROR_MESSAGE,
    EXECUTION_DETAILS
FROM PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 1;

-- Expected:
-- STATUS = 'SUCCESS'
-- TABLES_PROCESSED > 0
-- COLUMNS_PROCESSED > 0
-- ERROR_MESSAGE = NULL

SELECT '✅ VERIFICATION: Tables loaded' as TEST_STEP;

SELECT
    SERVICE_NAME,
    COUNT(*) as TABLE_COUNT
FROM TABLE_REGISTRY
GROUP BY SERVICE_NAME
ORDER BY TABLE_COUNT DESC;

SELECT '✅ VERIFICATION: Columns loaded' as TEST_STEP;

SELECT
    COUNT(*) as TOTAL_COLUMNS,
    COUNT(DISTINCT TABLE_ID) as TABLES_WITH_COLUMNS
FROM COLUMN_METADATA;

SELECT '✅ VERIFICATION: Statistics created' as TEST_STEP;

SELECT
    COUNT(*) as STATS_COUNT,
    SNAPSHOT_DATE
FROM TABLE_STATISTICS
GROUP BY SNAPSHOT_DATE
ORDER BY SNAPSHOT_DATE DESC;

/*
================================================================================
EXPECTED RESULTS:

1. Log entry with STATUS = 'SUCCESS'
2. TABLES_PROCESSED between 10-30
3. COLUMNS_PROCESSED between 100-500
4. EXECUTION_DURATION_SECONDS < 30
5. No ERROR_MESSAGE

If all tests pass, the CREATE_METADATA_REPOSITORY.sql script should work correctly.

Next steps:
1. If tests pass → Run CREATE_METADATA_REPOSITORY.sql
2. If tests fail → Review error in PROCEDURE_EXECUTION_LOG.ERROR_MESSAGE
================================================================================
*/
