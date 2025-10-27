/*
================================================================================
Create Stored Procedure SP_REFRESH_METADATA - Standalone Script
================================================================================

This script ONLY creates the stored procedure SP_REFRESH_METADATA.
Use this to update the procedure without re-running the entire metadata repository creation.

Author: GenericCorp Data Engineering Team
Date: 2025-10-24
Version: 1.0
================================================================================
*/

USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;
USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA METADATA;

-- ============================================================================
-- Create Stored Procedure to Refresh Metadata
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
-- Verify Stored Procedure Creation
-- ============================================================================

-- Check procedure exists
SHOW PROCEDURES LIKE 'SP_REFRESH_METADATA';

-- Test the procedure
CALL SP_REFRESH_METADATA();

-- Check execution log
SELECT
    LOG_ID,
    PROCEDURE_NAME,
    EXECUTION_START,
    EXECUTION_END,
    EXECUTION_DURATION_SECONDS,
    STATUS,
    TABLES_PROCESSED,
    COLUMNS_PROCESSED,
    ROWS_PROCESSED
FROM PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 1;

/*
================================================================================
USAGE NOTES
================================================================================

This script can be run independently to:
1. Create the stored procedure from scratch
2. Update the procedure with new logic
3. Fix any issues with the procedure

The stored procedure will:
- Delete and reload all metadata
- Process both DEV_LANDING and DEV_TRANSFORMATION databases
- Create statistics snapshots
- Log execution to PROCEDURE_EXECUTION_LOG

To manually run the procedure:
    CALL SP_REFRESH_METADATA();

To view execution history:
    SELECT * FROM PROCEDURE_EXECUTION_LOG ORDER BY EXECUTION_START DESC;

================================================================================
*/
