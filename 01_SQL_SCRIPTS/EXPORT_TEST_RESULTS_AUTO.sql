/*
================================================================================
Automatic Export of Test Results - Stores Everything in Tables
================================================================================

This script automatically stores all test analysis results in tables that can
be exported to CSV/JSON files.

No manual saving required - just query the export tables afterwards!

Date: 2025-10-24
================================================================================
*/

USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;
USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA METADATA;

-- Ensure export schema exists
CREATE SCHEMA IF NOT EXISTS METADATA_EXPORTS;

SELECT '🚀 STARTING AUTOMATIC TEST RESULTS EXPORT...' as STATUS;

-- ============================================================================
-- EXPORT 1: Execution Log
-- ============================================================================

SELECT '📊 EXPORT 1/11: Execution Log' as PROGRESS;

CREATE OR REPLACE TABLE METADATA_EXPORTS.EXPORT_EXECUTION_LOG AS
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
    EXECUTION_DETAILS,
    EXECUTED_BY,
    CREATED_DATE
FROM PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 5;

SELECT '✅ Created: METADATA_EXPORTS.EXPORT_EXECUTION_LOG' as RESULT;


-- ============================================================================
-- EXPORT 2: Success Criteria
-- ============================================================================

SELECT '✅ EXPORT 2/11: Success Criteria' as PROGRESS;

CREATE OR REPLACE TABLE METADATA_EXPORTS.EXPORT_SUCCESS_CRITERIA AS
WITH latest_log AS (
    SELECT
        STATUS,
        TABLES_PROCESSED,
        COLUMNS_PROCESSED,
        EXECUTION_DURATION_SECONDS,
        ERROR_MESSAGE
    FROM PROCEDURE_EXECUTION_LOG
    ORDER BY EXECUTION_START DESC
    LIMIT 1
)
SELECT
    'Execution completed successfully' as CRITERIA,
    'SUCCESS' as EXPECTED_VALUE,
    STATUS as ACTUAL_VALUE,
    CASE WHEN STATUS = 'SUCCESS' THEN '✅ PASS' ELSE '❌ FAIL' END as TEST_RESULT
FROM latest_log
UNION ALL
SELECT
    'Tables processed > 0',
    '> 0',
    TABLES_PROCESSED::VARCHAR,
    CASE WHEN TABLES_PROCESSED > 0 THEN '✅ PASS' ELSE '❌ FAIL' END
FROM latest_log
UNION ALL
SELECT
    'Columns processed > 0',
    '> 0',
    COLUMNS_PROCESSED::VARCHAR,
    CASE WHEN COLUMNS_PROCESSED > 0 THEN '✅ PASS' ELSE '❌ FAIL' END
FROM latest_log
UNION ALL
SELECT
    'Execution duration < 30 seconds',
    '< 30 sec',
    EXECUTION_DURATION_SECONDS::VARCHAR || ' sec',
    CASE WHEN EXECUTION_DURATION_SECONDS < 30 THEN '✅ PASS' ELSE '⚠️  WARNING' END
FROM latest_log
UNION ALL
SELECT
    'No error message',
    'NULL',
    COALESCE(ERROR_MESSAGE, '(none)'),
    CASE WHEN ERROR_MESSAGE IS NULL THEN '✅ PASS' ELSE '❌ FAIL' END
FROM latest_log;

SELECT '✅ Created: METADATA_EXPORTS.EXPORT_SUCCESS_CRITERIA' as RESULT;


-- ============================================================================
-- EXPORT 3: Services Detected
-- ============================================================================

SELECT '🔍 EXPORT 3/11: Services Detected' as PROGRESS;

CREATE OR REPLACE TABLE METADATA_EXPORTS.EXPORT_SERVICES_DETECTED AS
SELECT
    SERVICE_NAME,
    COUNT(*) as TABLE_COUNT,
    DATA_LAYER,
    SUM(ROW_COUNT) as TOTAL_ROWS
FROM TABLE_REGISTRY
GROUP BY SERVICE_NAME, DATA_LAYER
ORDER BY TABLE_COUNT DESC;

SELECT '✅ Created: METADATA_EXPORTS.EXPORT_SERVICES_DETECTED' as RESULT;


-- ============================================================================
-- EXPORT 4: Tables Loaded
-- ============================================================================

SELECT '📋 EXPORT 4/11: Tables Loaded' as PROGRESS;

CREATE OR REPLACE TABLE METADATA_EXPORTS.EXPORT_TABLES_LOADED AS
SELECT
    SERVICE_NAME,
    DATABASE_NAME,
    SCHEMA_NAME,
    TABLE_NAME,
    TABLE_TYPE,
    DATA_LAYER,
    ROW_COUNT,
    LAST_UPDATED
FROM TABLE_REGISTRY
ORDER BY SERVICE_NAME, TABLE_NAME;

SELECT '✅ Created: METADATA_EXPORTS.EXPORT_TABLES_LOADED' as RESULT;


-- ============================================================================
-- EXPORT 5: Columns Summary
-- ============================================================================

SELECT '📝 EXPORT 5/11: Columns Summary' as PROGRESS;

CREATE OR REPLACE TABLE METADATA_EXPORTS.EXPORT_COLUMNS_SUMMARY AS
SELECT
    tr.SERVICE_NAME,
    tr.TABLE_NAME,
    COUNT(cm.COLUMN_ID) as COLUMN_COUNT,
    LISTAGG(cm.COLUMN_NAME, ', ') WITHIN GROUP (ORDER BY cm.ORDINAL_POSITION) as COLUMNS
FROM TABLE_REGISTRY tr
LEFT JOIN COLUMN_METADATA cm ON tr.TABLE_ID = cm.TABLE_ID
GROUP BY tr.SERVICE_NAME, tr.TABLE_NAME
ORDER BY tr.SERVICE_NAME, tr.TABLE_NAME;

SELECT '✅ Created: METADATA_EXPORTS.EXPORT_COLUMNS_SUMMARY' as RESULT;


-- ============================================================================
-- EXPORT 6: Columns Detailed
-- ============================================================================

SELECT '📝 EXPORT 6/11: Columns Detailed' as PROGRESS;

CREATE OR REPLACE TABLE METADATA_EXPORTS.EXPORT_COLUMNS_DETAILED AS
SELECT
    tr.SERVICE_NAME,
    tr.TABLE_NAME,
    cm.COLUMN_NAME,
    cm.DATA_TYPE,
    cm.IS_NULLABLE,
    cm.ORDINAL_POSITION,
    cm.COLUMN_DEFAULT,
    cm.COLUMN_COMMENT
FROM COLUMN_METADATA cm
JOIN TABLE_REGISTRY tr ON cm.TABLE_ID = tr.TABLE_ID
ORDER BY tr.SERVICE_NAME, tr.TABLE_NAME, cm.ORDINAL_POSITION;

SELECT '✅ Created: METADATA_EXPORTS.EXPORT_COLUMNS_DETAILED' as RESULT;


-- ============================================================================
-- EXPORT 7: Statistics Snapshot
-- ============================================================================

SELECT '📊 EXPORT 7/11: Statistics Snapshot' as PROGRESS;

CREATE OR REPLACE TABLE METADATA_EXPORTS.EXPORT_STATISTICS_SNAPSHOT AS
SELECT
    ts.SNAPSHOT_DATE,
    tr.SERVICE_NAME,
    tr.TABLE_NAME,
    ts.ROW_COUNT,
    ts.COLUMN_COUNT,
    ts.SIZE_BYTES,
    ts.LAST_MODIFIED
FROM TABLE_STATISTICS ts
JOIN TABLE_REGISTRY tr ON ts.TABLE_ID = tr.TABLE_ID
ORDER BY ts.SNAPSHOT_DATE DESC, tr.SERVICE_NAME, tr.TABLE_NAME;

SELECT '✅ Created: METADATA_EXPORTS.EXPORT_STATISTICS_SNAPSHOT' as RESULT;


-- ============================================================================
-- EXPORT 8: Overall Summary
-- ============================================================================

SELECT '📈 EXPORT 8/11: Overall Summary' as PROGRESS;

CREATE OR REPLACE TABLE METADATA_EXPORTS.EXPORT_OVERALL_SUMMARY AS
SELECT
    'Total Services Detected' as METRIC,
    COUNT(DISTINCT SERVICE_NAME)::VARCHAR as VALUE,
    '' as UNIT
FROM TABLE_REGISTRY
UNION ALL
SELECT
    'Total Tables Loaded',
    COUNT(*)::VARCHAR,
    'tables'
FROM TABLE_REGISTRY
UNION ALL
SELECT
    'Total Columns Loaded',
    COUNT(*)::VARCHAR,
    'columns'
FROM COLUMN_METADATA
UNION ALL
SELECT
    'Total Statistics Created',
    COUNT(*)::VARCHAR,
    'snapshots'
FROM TABLE_STATISTICS
UNION ALL
SELECT
    'Execution Duration',
    (SELECT EXECUTION_DURATION_SECONDS::VARCHAR FROM PROCEDURE_EXECUTION_LOG ORDER BY EXECUTION_START DESC LIMIT 1),
    'seconds'
UNION ALL
SELECT
    'Total Rows in All Tables',
    SUM(ROW_COUNT)::VARCHAR,
    'rows'
FROM TABLE_REGISTRY
UNION ALL
SELECT
    'Execution Status',
    (SELECT STATUS FROM PROCEDURE_EXECUTION_LOG ORDER BY EXECUTION_START DESC LIMIT 1),
    '';

SELECT '✅ Created: METADATA_EXPORTS.EXPORT_OVERALL_SUMMARY' as RESULT;


-- ============================================================================
-- EXPORT 9: Data Quality Checks
-- ============================================================================

SELECT '🔍 EXPORT 9/11: Data Quality Checks' as PROGRESS;

CREATE OR REPLACE TABLE METADATA_EXPORTS.EXPORT_DATA_QUALITY_CHECKS AS
SELECT
    '⚠️  Tables Without Columns' as CHECK_NAME,
    (SELECT COUNT(*)
     FROM TABLE_REGISTRY tr
     LEFT JOIN COLUMN_METADATA cm ON tr.TABLE_ID = cm.TABLE_ID
     WHERE cm.COLUMN_ID IS NULL) as ISSUE_COUNT
UNION ALL
SELECT
    '⚠️  Tables With Zero Rows',
    (SELECT COUNT(*) FROM TABLE_REGISTRY WHERE ROW_COUNT = 0 OR ROW_COUNT IS NULL)
UNION ALL
SELECT
    '⚠️  Columns Without Data Type',
    (SELECT COUNT(*) FROM COLUMN_METADATA WHERE DATA_TYPE IS NULL OR DATA_TYPE = '')
UNION ALL
SELECT
    '⚠️  Unknown Service Tables',
    (SELECT COUNT(*) FROM TABLE_REGISTRY WHERE SERVICE_NAME = 'Unknown')
UNION ALL
SELECT
    '✅ All Checks Status',
    CASE
        WHEN NOT EXISTS (SELECT 1 FROM TABLE_REGISTRY WHERE SERVICE_NAME = 'Unknown')
         AND NOT EXISTS (SELECT 1 FROM TABLE_REGISTRY WHERE ROW_COUNT = 0 OR ROW_COUNT IS NULL)
         AND NOT EXISTS (
             SELECT 1 FROM TABLE_REGISTRY tr
             LEFT JOIN COLUMN_METADATA cm ON tr.TABLE_ID = cm.TABLE_ID
             WHERE cm.COLUMN_ID IS NULL
         )
         AND NOT EXISTS (
             SELECT 1 FROM COLUMN_METADATA
             WHERE DATA_TYPE IS NULL OR DATA_TYPE = ''
         )
        THEN 0 -- All checks passed
        ELSE 1 -- Some checks failed
    END;

SELECT '✅ Created: METADATA_EXPORTS.EXPORT_DATA_QUALITY_CHECKS' as RESULT;


-- ============================================================================
-- EXPORT 10: Expected vs Actual Results
-- ============================================================================

SELECT '📊 EXPORT 10/11: Expected vs Actual' as PROGRESS;

CREATE OR REPLACE TABLE METADATA_EXPORTS.EXPORT_EXPECTED_VS_ACTUAL AS
WITH latest_log AS (
    SELECT
        STATUS,
        TABLES_PROCESSED,
        COLUMNS_PROCESSED,
        EXECUTION_DURATION_SECONDS,
        ERROR_MESSAGE
    FROM PROCEDURE_EXECUTION_LOG
    ORDER BY EXECUTION_START DESC
    LIMIT 1
),
service_count AS (
    SELECT COUNT(DISTINCT SERVICE_NAME) as SERVICE_COUNT
    FROM TABLE_REGISTRY
)
SELECT
    'Execution Status' as CHECK,
    'SUCCESS' as EXPECTED,
    STATUS as ACTUAL,
    CASE WHEN STATUS = 'SUCCESS' THEN '✅ PASS' ELSE '❌ FAIL' END as RESULT
FROM latest_log
UNION ALL
SELECT
    'Tables Processed Range',
    '10-30 tables',
    TABLES_PROCESSED::VARCHAR || ' tables',
    CASE
        WHEN TABLES_PROCESSED BETWEEN 10 AND 30 THEN '✅ PASS'
        WHEN TABLES_PROCESSED > 0 THEN '⚠️  ACCEPTABLE'
        ELSE '❌ FAIL'
    END
FROM latest_log
UNION ALL
SELECT
    'Columns Processed Range',
    '100-500 columns',
    COLUMNS_PROCESSED::VARCHAR || ' columns',
    CASE
        WHEN COLUMNS_PROCESSED BETWEEN 100 AND 500 THEN '✅ PASS'
        WHEN COLUMNS_PROCESSED > 0 THEN '⚠️  ACCEPTABLE'
        ELSE '❌ FAIL'
    END
FROM latest_log
UNION ALL
SELECT
    'Execution Duration',
    '< 30 seconds',
    EXECUTION_DURATION_SECONDS::VARCHAR || ' seconds',
    CASE
        WHEN EXECUTION_DURATION_SECONDS < 30 THEN '✅ PASS'
        ELSE '⚠️  WARNING'
    END
FROM latest_log
UNION ALL
SELECT
    'Error Message',
    'NULL (no errors)',
    COALESCE(ERROR_MESSAGE, 'NULL'),
    CASE WHEN ERROR_MESSAGE IS NULL THEN '✅ PASS' ELSE '❌ FAIL' END
FROM latest_log
UNION ALL
SELECT
    'Services Detected',
    '> 0 services',
    SERVICE_COUNT::VARCHAR || ' services',
    CASE WHEN SERVICE_COUNT > 0 THEN '✅ PASS' ELSE '❌ FAIL' END
FROM service_count;

SELECT '✅ Created: METADATA_EXPORTS.EXPORT_EXPECTED_VS_ACTUAL' as RESULT;


-- ============================================================================
-- EXPORT 11: Complete JSON Export
-- ============================================================================

SELECT '💾 EXPORT 11/11: Complete JSON' as PROGRESS;

CREATE OR REPLACE TABLE METADATA_EXPORTS.EXPORT_TEST_RESULTS_JSON AS
SELECT
    CURRENT_TIMESTAMP() as EXPORT_TIMESTAMP,
    OBJECT_CONSTRUCT(
        'test_name', 'TEST_STORED_PROCEDURE',
        'test_date', CURRENT_DATE(),
        'execution_log', (
            SELECT OBJECT_CONSTRUCT(
                'log_id', LOG_ID,
                'procedure_name', PROCEDURE_NAME,
                'execution_start', EXECUTION_START,
                'execution_end', EXECUTION_END,
                'duration_seconds', EXECUTION_DURATION_SECONDS,
                'status', STATUS,
                'tables_processed', TABLES_PROCESSED,
                'columns_processed', COLUMNS_PROCESSED,
                'rows_processed', ROWS_PROCESSED,
                'error_message', ERROR_MESSAGE,
                'execution_details', EXECUTION_DETAILS,
                'executed_by', EXECUTED_BY
            )
            FROM PROCEDURE_EXECUTION_LOG
            ORDER BY EXECUTION_START DESC
            LIMIT 1
        ),
        'services_detected', (
            SELECT ARRAY_AGG(
                OBJECT_CONSTRUCT(
                    'service_name', SERVICE_NAME,
                    'table_count', TABLE_COUNT,
                    'data_layer', DATA_LAYER,
                    'total_rows', TOTAL_ROWS
                )
            )
            FROM (
                SELECT
                    SERVICE_NAME,
                    COUNT(*) as TABLE_COUNT,
                    DATA_LAYER,
                    SUM(ROW_COUNT) as TOTAL_ROWS
                FROM TABLE_REGISTRY
                GROUP BY SERVICE_NAME, DATA_LAYER
            )
        ),
        'tables_loaded', (
            SELECT ARRAY_AGG(
                OBJECT_CONSTRUCT(
                    'service_name', SERVICE_NAME,
                    'database_name', DATABASE_NAME,
                    'schema_name', SCHEMA_NAME,
                    'table_name', TABLE_NAME,
                    'table_type', TABLE_TYPE,
                    'data_layer', DATA_LAYER,
                    'row_count', ROW_COUNT
                )
            )
            FROM TABLE_REGISTRY
        ),
        'summary', (
            SELECT OBJECT_CONSTRUCT(
                'total_services', (SELECT COUNT(DISTINCT SERVICE_NAME) FROM TABLE_REGISTRY),
                'total_tables', (SELECT COUNT(*) FROM TABLE_REGISTRY),
                'total_columns', (SELECT COUNT(*) FROM COLUMN_METADATA),
                'total_statistics', (SELECT COUNT(*) FROM TABLE_STATISTICS),
                'total_rows', (SELECT SUM(ROW_COUNT) FROM TABLE_REGISTRY)
            )
        )
    ) as TEST_RESULTS
FROM (SELECT 1); -- DUAL equivalent in Snowflake

SELECT '✅ Created: METADATA_EXPORTS.EXPORT_TEST_RESULTS_JSON' as RESULT;


-- ============================================================================
-- Summary of All Exports
-- ============================================================================

SELECT '🎉 ALL EXPORTS COMPLETED!' as STATUS;

SELECT
    '📊 EXPORT SUMMARY' as SECTION,
    '11 tables created in METADATA_EXPORTS schema' as RESULT;

-- List all export tables
SELECT
    TABLE_NAME,
    ROW_COUNT,
    CREATED as CREATED_TIMESTAMP
FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'METADATA_EXPORTS'
  AND TABLE_NAME LIKE 'EXPORT_%'
ORDER BY TABLE_NAME;


/*
================================================================================
HOW TO EXPORT THE RESULTS TO FILES
================================================================================

Now you can easily export any table to CSV or JSON:

METHOD 1: Export individual tables to CSV
------------------------------------------
In VS Code Snowflake extension:

1. Run these SELECT queries one by one:
   SELECT * FROM METADATA_EXPORTS.EXPORT_EXECUTION_LOG;
   SELECT * FROM METADATA_EXPORTS.EXPORT_SUCCESS_CRITERIA;
   SELECT * FROM METADATA_EXPORTS.EXPORT_SERVICES_DETECTED;
   SELECT * FROM METADATA_EXPORTS.EXPORT_TABLES_LOADED;
   SELECT * FROM METADATA_EXPORTS.EXPORT_COLUMNS_SUMMARY;
   SELECT * FROM METADATA_EXPORTS.EXPORT_COLUMNS_DETAILED;
   SELECT * FROM METADATA_EXPORTS.EXPORT_STATISTICS_SNAPSHOT;
   SELECT * FROM METADATA_EXPORTS.EXPORT_OVERALL_SUMMARY;
   SELECT * FROM METADATA_EXPORTS.EXPORT_DATA_QUALITY_CHECKS;
   SELECT * FROM METADATA_EXPORTS.EXPORT_EXPECTED_VS_ACTUAL;

2. Right-click results → "Export to CSV"
3. Save to: 04_METADATA_SAMPLES/test_results/

METHOD 2: Export JSON
---------------------
   SELECT TEST_RESULTS FROM METADATA_EXPORTS.EXPORT_TEST_RESULTS_JSON;

   Right-click → "Export to JSON"
   Save as: 04_METADATA_SAMPLES/test_results/test_results.json

METHOD 3: Use Snowflake COPY INTO (for automated exports)
----------------------------------------------------------
   -- Export to internal stage, then download
   COPY INTO @~/test_results/execution_log.csv
   FROM METADATA_EXPORTS.EXPORT_EXECUTION_LOG
   FILE_FORMAT = (TYPE = CSV FIELD_OPTIONALLY_ENCLOSED_BY = '"' HEADER = TRUE);

================================================================================
VERIFY TEST RESULTS
================================================================================
*/

-- Quick verification: Did the test pass?
SELECT
    '🔍 QUICK TEST VERIFICATION' as SECTION;

SELECT
    CHECK,
    EXPECTED,
    ACTUAL,
    RESULT
FROM METADATA_EXPORTS.EXPORT_EXPECTED_VS_ACTUAL
ORDER BY
    CASE RESULT
        WHEN '❌ FAIL' THEN 1
        WHEN '⚠️  WARNING' THEN 2
        WHEN '⚠️  ACCEPTABLE' THEN 3
        WHEN '✅ PASS' THEN 4
    END;

-- Show any data quality issues
SELECT
    '⚠️  DATA QUALITY ISSUES (if any)' as SECTION;

SELECT *
FROM METADATA_EXPORTS.EXPORT_DATA_QUALITY_CHECKS
WHERE ISSUE_COUNT > 0
  AND CHECK_NAME != '✅ All Checks Status';

-- Show execution summary
SELECT
    '📈 EXECUTION SUMMARY' as SECTION;

SELECT * FROM METADATA_EXPORTS.EXPORT_OVERALL_SUMMARY;

/*
================================================================================
NEXT STEPS
================================================================================

✅ If all tests PASS:
   1. Export the tables to CSV/JSON files
   2. Run CREATE_METADATA_REPOSITORY.sql
   3. Verify with VERIFY_METADATA_REPOSITORY.sql
   4. Activate the daily task

❌ If any tests FAIL:
   1. Check EXPORT_EXPECTED_VS_ACTUAL for failures
   2. Review EXPORT_DATA_QUALITY_CHECKS for issues
   3. Check EXPORT_EXECUTION_LOG for error messages
   4. Fix issues and re-run TEST_STORED_PROCEDURE.sql

================================================================================
*/
