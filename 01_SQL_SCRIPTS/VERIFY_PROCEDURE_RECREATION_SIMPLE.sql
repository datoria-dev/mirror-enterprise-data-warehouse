/*
================================================================================
Verify Stored Procedure Recreation - Simplified Version
================================================================================

This script verifies that SP_REFRESH_METADATA was successfully re-created
and is working correctly.

IMPORTANT: Execute each section separately (don't run all at once)

Date: 2025-10-24
================================================================================
*/

USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;
USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA METADATA;

-- ============================================================================
-- CHECK 1: Verify Procedure Exists
-- ============================================================================
-- Execute this block separately

SHOW PROCEDURES LIKE 'SP_REFRESH_METADATA';

-- Expected: Should show 1 row
-- Columns: name, arguments, language, etc.
-- If you see SP_REFRESH_METADATA, the procedure exists ✅


-- ============================================================================
-- CHECK 2: View Most Recent Execution Log
-- ============================================================================
-- Execute this block separately

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
    EXECUTED_BY
FROM PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 1;

-- Expected:
-- STATUS: SUCCESS ✅
-- TABLES_PROCESSED: 180 ✅
-- COLUMNS_PROCESSED: 2206 ✅
-- ERROR_MESSAGE: NULL ✅


-- ============================================================================
-- CHECK 3: Execution History
-- ============================================================================
-- Execute this block separately

SELECT
    LOG_ID,
    EXECUTION_START,
    EXECUTION_DURATION_SECONDS,
    STATUS,
    TABLES_PROCESSED,
    COLUMNS_PROCESSED,
    ROWS_PROCESSED,
    EXECUTED_BY
FROM PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 5;

-- Expected: Multiple rows if procedure was run before
-- Latest row should show most recent timestamp


-- ============================================================================
-- CHECK 4: Verify Metadata Tables Are Populated
-- ============================================================================
-- Execute this block separately

SELECT
    'TABLE_REGISTRY' as TABLE_NAME,
    COUNT(*) as ROW_COUNT,
    180 as EXPECTED_COUNT,
    CASE WHEN COUNT(*) = 180 THEN '✅ PASS' ELSE '❌ FAIL' END as STATUS
FROM TABLE_REGISTRY

UNION ALL

SELECT
    'COLUMN_METADATA',
    COUNT(*),
    2206,
    CASE WHEN COUNT(*) = 2206 THEN '✅ PASS' ELSE '❌ FAIL' END
FROM COLUMN_METADATA

UNION ALL

SELECT
    'TABLE_STATISTICS',
    COUNT(*),
    180,
    CASE WHEN COUNT(*) >= 180 THEN '✅ PASS' ELSE '❌ FAIL' END
FROM TABLE_STATISTICS

UNION ALL

SELECT
    'SERVICE_CATALOG',
    COUNT(*),
    21,
    CASE WHEN COUNT(*) = 21 THEN '✅ PASS' ELSE '❌ FAIL' END
FROM SERVICE_CATALOG;

-- Expected: All 4 rows show STATUS = '✅ PASS'


-- ============================================================================
-- CHECK 5: Verify Execution Details (JSON)
-- ============================================================================
-- Execute this block separately

SELECT
    LOG_ID,
    EXECUTION_DETAILS:tables_processed::NUMBER as TABLES_FROM_JSON,
    EXECUTION_DETAILS:columns_processed::NUMBER as COLUMNS_FROM_JSON,
    EXECUTION_DETAILS:stats_processed::NUMBER as STATS_FROM_JSON,
    EXECUTION_DETAILS:duration_seconds::NUMBER as DURATION_FROM_JSON,
    EXECUTION_DETAILS:timestamp::TIMESTAMP_LTZ as TIMESTAMP_FROM_JSON
FROM PROCEDURE_EXECUTION_LOG
WHERE EXECUTION_DETAILS IS NOT NULL
ORDER BY EXECUTION_START DESC
LIMIT 1;

-- Expected:
-- TABLES_FROM_JSON: 180 ✅
-- COLUMNS_FROM_JSON: 2206 ✅
-- STATS_FROM_JSON: 180 ✅


-- ============================================================================
-- CHECK 6: Verify Services Detected
-- ============================================================================
-- Execute this block separately

SELECT
    SERVICE_NAME,
    COUNT(*) as TABLE_COUNT,
    SUM(ROW_COUNT) as TOTAL_ROWS
FROM TABLE_REGISTRY
GROUP BY SERVICE_NAME
ORDER BY TABLE_COUNT DESC;

-- Expected: 20 services with various table counts
-- Top services: Qualys, CybelAngel, SentinelOne, etc.


-- ============================================================================
-- CHECK 7: Verify Views Are Working
-- ============================================================================
-- Execute this block separately

SELECT
    'VW_SERVICE_SUMMARY' as VIEW_NAME,
    COUNT(*) as ROW_COUNT,
    21 as EXPECTED_COUNT,
    CASE WHEN COUNT(*) = 21 THEN '✅ PASS' ELSE '❌ FAIL' END as STATUS
FROM VW_SERVICE_SUMMARY

UNION ALL

SELECT
    'VW_TABLE_CATALOG',
    COUNT(*),
    180,
    CASE WHEN COUNT(*) = 180 THEN '✅ PASS' ELSE '❌ FAIL' END
FROM VW_TABLE_CATALOG

UNION ALL

SELECT
    'VW_COLUMN_CATALOG',
    COUNT(*),
    2206,
    CASE WHEN COUNT(*) = 2206 THEN '✅ PASS' ELSE '❌ FAIL' END
FROM VW_COLUMN_CATALOG;

-- Expected: All 3 views show STATUS = '✅ PASS'


-- ============================================================================
-- CHECK 8: Performance Metrics
-- ============================================================================
-- Execute this block separately

SELECT
    'Average Execution Duration' as METRIC,
    ROUND(AVG(EXECUTION_DURATION_SECONDS), 2) as VALUE,
    'seconds' as UNIT
FROM PROCEDURE_EXECUTION_LOG
WHERE STATUS = 'SUCCESS'

UNION ALL

SELECT
    'Latest Execution Duration',
    (SELECT EXECUTION_DURATION_SECONDS FROM PROCEDURE_EXECUTION_LOG
     WHERE STATUS = 'SUCCESS' ORDER BY EXECUTION_START DESC LIMIT 1),
    'seconds'

UNION ALL

SELECT
    'Tables Per Second (Latest)',
    ROUND((SELECT TABLES_PROCESSED::FLOAT / NULLIF(EXECUTION_DURATION_SECONDS, 0)
           FROM PROCEDURE_EXECUTION_LOG
           WHERE STATUS = 'SUCCESS' ORDER BY EXECUTION_START DESC LIMIT 1), 2),
    'tables/sec'

UNION ALL

SELECT
    'Columns Per Second (Latest)',
    ROUND((SELECT COLUMNS_PROCESSED::FLOAT / NULLIF(EXECUTION_DURATION_SECONDS, 0)
           FROM PROCEDURE_EXECUTION_LOG
           WHERE STATUS = 'SUCCESS' ORDER BY EXECUTION_START DESC LIMIT 1), 2),
    'columns/sec';

-- Expected:
-- Average Duration: 9-15 seconds ✅
-- Tables/sec: 12-20 ✅
-- Columns/sec: 150-250 ✅


-- ============================================================================
-- CHECK 9: Final Summary
-- ============================================================================
-- Execute this block separately

WITH latest_execution AS (
    SELECT
        STATUS,
        TABLES_PROCESSED,
        COLUMNS_PROCESSED,
        ROWS_PROCESSED,
        EXECUTION_DURATION_SECONDS
    FROM PROCEDURE_EXECUTION_LOG
    ORDER BY EXECUTION_START DESC
    LIMIT 1
)
SELECT
    CASE
        WHEN STATUS = 'SUCCESS'
         AND TABLES_PROCESSED = 180
         AND COLUMNS_PROCESSED = 2206
         AND ROWS_PROCESSED >= 180
         AND EXECUTION_DURATION_SECONDS < 30
        THEN '✅ ALL CHECKS PASSED - PROCEDURE IS WORKING CORRECTLY'
        ELSE '❌ SOME CHECKS FAILED - REVIEW RESULTS ABOVE'
    END as OVERALL_STATUS,
    STATUS,
    TABLES_PROCESSED,
    COLUMNS_PROCESSED,
    ROWS_PROCESSED,
    EXECUTION_DURATION_SECONDS || ' seconds' as DURATION
FROM latest_execution;

-- Expected: OVERALL_STATUS = '✅ ALL CHECKS PASSED - PROCEDURE IS WORKING CORRECTLY'


/*
================================================================================
SUMMARY OF WHAT TO CHECK
================================================================================

Execute each CHECK section above separately and verify:

✅ CHECK 1: Procedure SP_REFRESH_METADATA appears in results
✅ CHECK 2: Latest execution shows STATUS = 'SUCCESS'
✅ CHECK 3: Multiple execution records visible
✅ CHECK 4: All 4 tables show '✅ PASS'
✅ CHECK 5: All JSON fields populated with correct values
✅ CHECK 6: 20 services detected
✅ CHECK 7: All 3 views show '✅ PASS'
✅ CHECK 8: Performance metrics within expected ranges
✅ CHECK 9: Final summary shows '✅ ALL CHECKS PASSED'

================================================================================
NEXT STEPS
================================================================================

If ALL CHECKS PASSED:
  ✅ Stored procedure successfully re-created
  ✅ Metadata repository fully operational
  ✅ Ready to activate daily refresh task
  ✅ Ready to use in Streamlit apps

  Next action: Activate the task
  ALTER TASK TASK_DAILY_METADATA_REFRESH RESUME;

If ANY CHECK FAILED:
  ❌ Review the specific check that failed
  ❌ Check PROCEDURE_EXECUTION_LOG for error details
  ❌ May need to re-run CREATE_STORED_PROCEDURE_ONLY.sql

================================================================================
*/
