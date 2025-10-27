/*
================================================================================
Analyze and Export Test Results - TEST_STORED_PROCEDURE.sql
================================================================================

This script queries and exports the results from the TEST_STORED_PROCEDURE.sql
execution for later analysis.

IMPORTANT: Save all query results to CSV/JSON files for analysis.

Date: 2025-10-24
================================================================================
*/

USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;
USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA METADATA;

-- ============================================================================
-- STEP 1: Execution Log Analysis
-- ============================================================================

SELECT '📊 STEP 1: EXECUTION LOG ANALYSIS' as SECTION;

-- Query the execution log
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

-- ✅ SAVE THIS RESULT AS: 04_METADATA_SAMPLES/test_results/execution_log.csv


-- ============================================================================
-- STEP 2: Verify Success Criteria
-- ============================================================================

SELECT '✅ STEP 2: SUCCESS CRITERIA VERIFICATION' as SECTION;

SELECT
    CASE
        WHEN STATUS = 'SUCCESS' THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as TEST_1_STATUS,
    'Execution completed successfully' as CRITERIA,
    STATUS as ACTUAL_VALUE
FROM PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 1

UNION ALL

SELECT
    CASE
        WHEN TABLES_PROCESSED > 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END,
    'Tables processed > 0',
    TABLES_PROCESSED::VARCHAR
FROM PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 1

UNION ALL

SELECT
    CASE
        WHEN COLUMNS_PROCESSED > 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END,
    'Columns processed > 0',
    COLUMNS_PROCESSED::VARCHAR
FROM PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 1

UNION ALL

SELECT
    CASE
        WHEN EXECUTION_DURATION_SECONDS < 30 THEN '✅ PASS'
        ELSE '⚠️  WARNING'
    END,
    'Execution duration < 30 seconds',
    EXECUTION_DURATION_SECONDS::VARCHAR || ' sec'
FROM PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 1

UNION ALL

SELECT
    CASE
        WHEN ERROR_MESSAGE IS NULL THEN '✅ PASS'
        ELSE '❌ FAIL'
    END,
    'No error message',
    COALESCE(ERROR_MESSAGE, '(none)')
FROM PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 1;

-- ✅ SAVE THIS RESULT AS: 04_METADATA_SAMPLES/test_results/success_criteria.csv


-- ============================================================================
-- STEP 3: Services Detected
-- ============================================================================

SELECT '🔍 STEP 3: SERVICES DETECTED' as SECTION;

SELECT
    SERVICE_NAME,
    COUNT(*) as TABLE_COUNT,
    DATA_LAYER,
    SUM(ROW_COUNT) as TOTAL_ROWS
FROM TABLE_REGISTRY
GROUP BY SERVICE_NAME, DATA_LAYER
ORDER BY TABLE_COUNT DESC;

-- ✅ SAVE THIS RESULT AS: 04_METADATA_SAMPLES/test_results/services_detected.csv


-- ============================================================================
-- STEP 4: Tables Loaded
-- ============================================================================

SELECT '📋 STEP 4: TABLES LOADED' as SECTION;

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

-- ✅ SAVE THIS RESULT AS: 04_METADATA_SAMPLES/test_results/tables_loaded.csv


-- ============================================================================
-- STEP 5: Columns Loaded
-- ============================================================================

SELECT '📝 STEP 5: COLUMNS LOADED SUMMARY' as SECTION;

SELECT
    tr.SERVICE_NAME,
    tr.TABLE_NAME,
    COUNT(cm.COLUMN_ID) as COLUMN_COUNT,
    LISTAGG(cm.COLUMN_NAME, ', ') WITHIN GROUP (ORDER BY cm.ORDINAL_POSITION) as COLUMNS
FROM TABLE_REGISTRY tr
LEFT JOIN COLUMN_METADATA cm ON tr.TABLE_ID = cm.TABLE_ID
GROUP BY tr.SERVICE_NAME, tr.TABLE_NAME
ORDER BY tr.SERVICE_NAME, tr.TABLE_NAME;

-- ✅ SAVE THIS RESULT AS: 04_METADATA_SAMPLES/test_results/columns_summary.csv


-- Detailed column metadata
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

-- ✅ SAVE THIS RESULT AS: 04_METADATA_SAMPLES/test_results/columns_detailed.csv


-- ============================================================================
-- STEP 6: Statistics Created
-- ============================================================================

SELECT '📊 STEP 6: STATISTICS CREATED' as SECTION;

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

-- ✅ SAVE THIS RESULT AS: 04_METADATA_SAMPLES/test_results/statistics_snapshot.csv


-- ============================================================================
-- STEP 7: Overall Summary
-- ============================================================================

SELECT '📈 STEP 7: OVERALL TEST SUMMARY' as SECTION;

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
    EXECUTION_DURATION_SECONDS::VARCHAR,
    'seconds'
FROM PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 1

UNION ALL

SELECT
    'Total Rows in All Tables',
    SUM(ROW_COUNT)::VARCHAR,
    'rows'
FROM TABLE_REGISTRY

UNION ALL

SELECT
    'Execution Status',
    STATUS,
    ''
FROM PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 1;

-- ✅ SAVE THIS RESULT AS: 04_METADATA_SAMPLES/test_results/overall_summary.csv


-- ============================================================================
-- STEP 8: Export to JSON (for programmatic analysis)
-- ============================================================================

SELECT '💾 STEP 8: CREATE JSON EXPORT' as SECTION;

-- Create JSON export table
CREATE OR REPLACE TABLE METADATA_EXPORTS.TEST_RESULTS_JSON AS
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
FROM DUAL;

-- View JSON export
SELECT TEST_RESULTS FROM METADATA_EXPORTS.TEST_RESULTS_JSON;

-- ✅ SAVE THIS RESULT AS: 04_METADATA_SAMPLES/test_results/test_results.json


-- ============================================================================
-- STEP 9: Data Quality Checks
-- ============================================================================

SELECT '🔍 STEP 9: DATA QUALITY CHECKS' as SECTION;

-- Check for tables without columns
SELECT
    '⚠️  Tables Without Columns' as CHECK_NAME,
    COUNT(*) as ISSUE_COUNT
FROM TABLE_REGISTRY tr
LEFT JOIN COLUMN_METADATA cm ON tr.TABLE_ID = cm.TABLE_ID
WHERE cm.COLUMN_ID IS NULL

UNION ALL

-- Check for tables with 0 rows
SELECT
    '⚠️  Tables With Zero Rows',
    COUNT(*)
FROM TABLE_REGISTRY
WHERE ROW_COUNT = 0 OR ROW_COUNT IS NULL

UNION ALL

-- Check for columns without data type
SELECT
    '⚠️  Columns Without Data Type',
    COUNT(*)
FROM COLUMN_METADATA
WHERE DATA_TYPE IS NULL OR DATA_TYPE = ''

UNION ALL

-- Check for "Unknown" service tables
SELECT
    '⚠️  Unknown Service Tables',
    COUNT(*)
FROM TABLE_REGISTRY
WHERE SERVICE_NAME = 'Unknown'

UNION ALL

-- Success message if all checks pass
SELECT
    '✅ All Data Quality Checks Passed',
    0
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM TABLE_REGISTRY WHERE SERVICE_NAME = 'Unknown')
  AND NOT EXISTS (SELECT 1 FROM TABLE_REGISTRY WHERE ROW_COUNT = 0 OR ROW_COUNT IS NULL)
  AND NOT EXISTS (
      SELECT 1 FROM TABLE_REGISTRY tr
      LEFT JOIN COLUMN_METADATA cm ON tr.TABLE_ID = cm.TABLE_ID
      WHERE cm.COLUMN_ID IS NULL
  )
  AND NOT EXISTS (
      SELECT 1 FROM COLUMN_METADATA
      WHERE DATA_TYPE IS NULL OR DATA_TYPE = ''
  );

-- ✅ SAVE THIS RESULT AS: 04_METADATA_SAMPLES/test_results/data_quality_checks.csv


-- ============================================================================
-- STEP 10: Comparison with Expected Results
-- ============================================================================

SELECT '📊 STEP 10: EXPECTED VS ACTUAL RESULTS' as SECTION;

SELECT
    'Execution Status' as CHECK,
    'SUCCESS' as EXPECTED,
    (SELECT STATUS FROM PROCEDURE_EXECUTION_LOG ORDER BY EXECUTION_START DESC LIMIT 1) as ACTUAL,
    CASE
        WHEN (SELECT STATUS FROM PROCEDURE_EXECUTION_LOG ORDER BY EXECUTION_START DESC LIMIT 1) = 'SUCCESS'
        THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as RESULT

UNION ALL

SELECT
    'Tables Processed Range',
    '10-30 tables',
    (SELECT TABLES_PROCESSED::VARCHAR FROM PROCEDURE_EXECUTION_LOG ORDER BY EXECUTION_START DESC LIMIT 1) || ' tables',
    CASE
        WHEN (SELECT TABLES_PROCESSED FROM PROCEDURE_EXECUTION_LOG ORDER BY EXECUTION_START DESC LIMIT 1) BETWEEN 10 AND 30
        THEN '✅ PASS'
        WHEN (SELECT TABLES_PROCESSED FROM PROCEDURE_EXECUTION_LOG ORDER BY EXECUTION_START DESC LIMIT 1) > 0
        THEN '⚠️  ACCEPTABLE'
        ELSE '❌ FAIL'
    END

UNION ALL

SELECT
    'Columns Processed Range',
    '100-500 columns',
    (SELECT COLUMNS_PROCESSED::VARCHAR FROM PROCEDURE_EXECUTION_LOG ORDER BY EXECUTION_START DESC LIMIT 1) || ' columns',
    CASE
        WHEN (SELECT COLUMNS_PROCESSED FROM PROCEDURE_EXECUTION_LOG ORDER BY EXECUTION_START DESC LIMIT 1) BETWEEN 100 AND 500
        THEN '✅ PASS'
        WHEN (SELECT COLUMNS_PROCESSED FROM PROCEDURE_EXECUTION_LOG ORDER BY EXECUTION_START DESC LIMIT 1) > 0
        THEN '⚠️  ACCEPTABLE'
        ELSE '❌ FAIL'
    END

UNION ALL

SELECT
    'Execution Duration',
    '< 30 seconds',
    (SELECT EXECUTION_DURATION_SECONDS::VARCHAR FROM PROCEDURE_EXECUTION_LOG ORDER BY EXECUTION_START DESC LIMIT 1) || ' seconds',
    CASE
        WHEN (SELECT EXECUTION_DURATION_SECONDS FROM PROCEDURE_EXECUTION_LOG ORDER BY EXECUTION_START DESC LIMIT 1) < 30
        THEN '✅ PASS'
        ELSE '⚠️  WARNING'
    END

UNION ALL

SELECT
    'Error Message',
    'NULL (no errors)',
    COALESCE((SELECT ERROR_MESSAGE FROM PROCEDURE_EXECUTION_LOG ORDER BY EXECUTION_START DESC LIMIT 1), 'NULL'),
    CASE
        WHEN (SELECT ERROR_MESSAGE FROM PROCEDURE_EXECUTION_LOG ORDER BY EXECUTION_START DESC LIMIT 1) IS NULL
        THEN '✅ PASS'
        ELSE '❌ FAIL'
    END

UNION ALL

SELECT
    'Services Detected',
    '> 0 services',
    (SELECT COUNT(DISTINCT SERVICE_NAME)::VARCHAR FROM TABLE_REGISTRY) || ' services',
    CASE
        WHEN (SELECT COUNT(DISTINCT SERVICE_NAME) FROM TABLE_REGISTRY) > 0
        THEN '✅ PASS'
        ELSE '❌ FAIL'
    END;

-- ✅ SAVE THIS RESULT AS: 04_METADATA_SAMPLES/test_results/expected_vs_actual.csv


/*
================================================================================
INSTRUCTIONS FOR SAVING RESULTS
================================================================================

After running this script, save each query result to the indicated file path:

1. Create directory structure:
   04_METADATA_SAMPLES/
   └── test_results/
       ├── execution_log.csv
       ├── success_criteria.csv
       ├── services_detected.csv
       ├── tables_loaded.csv
       ├── columns_summary.csv
       ├── columns_detailed.csv
       ├── statistics_snapshot.csv
       ├── overall_summary.csv
       ├── test_results.json
       ├── data_quality_checks.csv
       └── expected_vs_actual.csv

2. In VS Code Snowflake extension, after each query executes:
   - Right-click on results grid
   - Select "Export to CSV" or "Export to JSON"
   - Save to the indicated file path

3. Once all files are saved, you'll have a complete analysis package for:
   - Reference in documentation
   - Comparison with future test runs
   - Troubleshooting if issues arise
   - Sharing with the team

================================================================================
NEXT STEPS AFTER TEST ANALYSIS
================================================================================

If all tests pass (all checks show ✅ PASS):

1. ✅ Review saved test results files
2. ✅ Execute CREATE_METADATA_REPOSITORY.sql
3. ✅ Run VERIFY_METADATA_REPOSITORY.sql
4. ✅ Export full metadata with EXPORT_METADATA_RESULTS.sql
5. ✅ Activate daily task: ALTER TASK TASK_DAILY_METADATA_REFRESH RESUME;
6. ✅ Update Streamlit apps using metadata repository

If any tests fail (any checks show ❌ FAIL):

1. ❌ Review ERROR_MESSAGE in execution_log.csv
2. ❌ Check data_quality_checks.csv for specific issues
3. ❌ Review FIXES_APPLIED.md for troubleshooting steps
4. ❌ Re-run TEST_STORED_PROCEDURE.sql after fixes

================================================================================
*/

-- Final message
SELECT
    '🎉 TEST ANALYSIS COMPLETE' as MESSAGE,
    'Review all saved CSV/JSON files in 04_METADATA_SAMPLES/test_results/' as NEXT_ACTION;
