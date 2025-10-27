/*
================================================================================
Verify Stored Procedure Recreation - Comprehensive Checks
================================================================================

This script verifies that SP_REFRESH_METADATA was successfully re-created
and is working correctly.

Run this AFTER executing CREATE_STORED_PROCEDURE_ONLY.sql

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

-- First, show the procedures
SHOW PROCEDURES LIKE 'SP_REFRESH_METADATA';

-- Expected: Should show 1 row with procedure details
-- Note: Execute this separately, then execute CHECK 2 below


-- ============================================================================
-- CHECK 2: Verify Procedure Signature
-- ============================================================================

-- Alternative approach: Query INFORMATION_SCHEMA.PROCEDURES directly
-- This avoids RESULT_SCAN issues when running in automated scripts
SELECT
    '✅ PROCEDURE DETAILS' as CHECK_NAME,
    PROCEDURE_NAME,
    ARGUMENT_SIGNATURE as ARGUMENTS,
    PROCEDURE_DEFINITION as DEFINITION_PREVIEW,
    PROCEDURE_LANGUAGE as LANGUAGE,
    CREATED as CREATED_ON,
    LAST_ALTERED as LAST_ALTERED_ON
FROM INFORMATION_SCHEMA.PROCEDURES
WHERE PROCEDURE_SCHEMA = 'METADATA'
  AND PROCEDURE_NAME = 'SP_REFRESH_METADATA';

-- Expected:
-- PROCEDURE_NAME: SP_REFRESH_METADATA
-- ARGUMENTS: () RETURN VARCHAR
-- LANGUAGE: SQL


-- ============================================================================
-- CHECK 3: View Most Recent Execution Log
-- ============================================================================

SELECT '✅ CHECK 3: MOST RECENT EXECUTION' as CHECK_NAME;

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
-- STATUS: SUCCESS
-- TABLES_PROCESSED: 180
-- COLUMNS_PROCESSED: 2206
-- ERROR_MESSAGE: NULL


-- ============================================================================
-- CHECK 4: Compare Execution History
-- ============================================================================

SELECT '✅ CHECK 4: EXECUTION HISTORY' as CHECK_NAME;

SELECT
    LOG_ID,
    EXECUTION_START,
    EXECUTION_DURATION_SECONDS,
    STATUS,
    TABLES_PROCESSED,
    COLUMNS_PROCESSED,
    ROWS_PROCESSED,
    CASE
        WHEN EXECUTION_START = (SELECT MAX(EXECUTION_START) FROM PROCEDURE_EXECUTION_LOG)
        THEN '🆕 LATEST'
        ELSE '📜 PREVIOUS'
    END as EXECUTION_TYPE,
    EXECUTED_BY
FROM PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 5;

-- Expected: Multiple rows if procedure was run before
-- Latest row should show recent timestamp


-- ============================================================================
-- CHECK 5: Verify Metadata Tables Are Populated
-- ============================================================================

SELECT '✅ CHECK 5: METADATA TABLES POPULATED' as CHECK_NAME;

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

-- Expected: All rows show STATUS = '✅ PASS'


-- ============================================================================
-- CHECK 6: Verify Execution Details (JSON)
-- ============================================================================

SELECT '✅ CHECK 6: EXECUTION DETAILS JSON' as CHECK_NAME;

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

-- Expected: All JSON fields populated with correct values


-- ============================================================================
-- CHECK 7: Verify Services Detected
-- ============================================================================

SELECT '✅ CHECK 7: SERVICES DETECTED' as CHECK_NAME;

SELECT
    SERVICE_NAME,
    COUNT(*) as TABLE_COUNT,
    SUM(ROW_COUNT) as TOTAL_ROWS
FROM TABLE_REGISTRY
GROUP BY SERVICE_NAME
ORDER BY TABLE_COUNT DESC;

-- Expected: 20 services with various table counts


-- ============================================================================
-- CHECK 8: Verify Views Are Working
-- ============================================================================

SELECT '✅ CHECK 8: VIEWS WORKING' as CHECK_NAME;

-- Test VW_SERVICE_SUMMARY
SELECT COUNT(*) as SERVICE_COUNT FROM VW_SERVICE_SUMMARY;
-- Expected: 21 services

-- Test VW_TABLE_CATALOG
SELECT COUNT(*) as TABLE_COUNT FROM VW_TABLE_CATALOG;
-- Expected: 180 tables

-- Test VW_COLUMN_CATALOG
SELECT COUNT(*) as COLUMN_COUNT FROM VW_COLUMN_CATALOG;
-- Expected: 2206 columns


-- ============================================================================
-- CHECK 9: Performance Check
-- ============================================================================

SELECT '✅ CHECK 9: PERFORMANCE METRICS' as CHECK_NAME;

WITH latest_execution AS (
    SELECT
        TABLES_PROCESSED,
        COLUMNS_PROCESSED,
        EXECUTION_DURATION_SECONDS
    FROM PROCEDURE_EXECUTION_LOG
    WHERE STATUS = 'SUCCESS'
    ORDER BY EXECUTION_START DESC
    LIMIT 1
),
aggregate_stats AS (
    SELECT
        AVG(EXECUTION_DURATION_SECONDS) as AVG_DURATION,
        MIN(EXECUTION_DURATION_SECONDS) as MIN_DURATION,
        MAX(EXECUTION_DURATION_SECONDS) as MAX_DURATION
    FROM PROCEDURE_EXECUTION_LOG
    WHERE STATUS = 'SUCCESS'
)
SELECT
    'Average Execution Duration' as METRIC,
    ROUND(AVG_DURATION, 2) as VALUE,
    'seconds' as UNIT
FROM aggregate_stats

UNION ALL

SELECT
    'Min Execution Duration',
    MIN_DURATION,
    'seconds'
FROM aggregate_stats

UNION ALL

SELECT
    'Max Execution Duration',
    MAX_DURATION,
    'seconds'
FROM aggregate_stats

UNION ALL

SELECT
    'Tables Per Second (Latest)',
    ROUND(TABLES_PROCESSED::FLOAT / NULLIF(EXECUTION_DURATION_SECONDS, 0), 2),
    'tables/sec'
FROM latest_execution

UNION ALL

SELECT
    'Columns Per Second (Latest)',
    ROUND(COLUMNS_PROCESSED::FLOAT / NULLIF(EXECUTION_DURATION_SECONDS, 0), 2),
    'columns/sec'
FROM latest_execution;

-- Expected: All metrics within reasonable ranges
-- Duration: 9-15 seconds
-- Tables/sec: 12-20
-- Columns/sec: 150-250


-- ============================================================================
-- CHECK 10: Final Summary
-- ============================================================================

SELECT '📊 FINAL SUMMARY' as CHECK_NAME;

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


/*
================================================================================
INTERPRETATION GUIDE
================================================================================

✅ ALL CHECKS PASSED IF:
─────────────────────────
1. CHECK 1: Shows procedure SP_REFRESH_METADATA
2. CHECK 2: Returns VARCHAR, language SQL
3. CHECK 3: STATUS = 'SUCCESS', TABLES = 180, COLUMNS = 2206
4. CHECK 4: Shows at least 1-2 execution records
5. CHECK 5: All 4 tables show STATUS = '✅ PASS'
6. CHECK 6: All JSON fields populated
7. CHECK 7: Shows 20 services
8. CHECK 8: All 3 view counts correct
9. CHECK 9: All metrics within expected ranges
10. CHECK 10: Shows '✅ ALL CHECKS PASSED'

❌ INVESTIGATION NEEDED IF:
──────────────────────────
- Any check shows '❌ FAIL'
- STATUS != 'SUCCESS'
- Table counts don't match expected
- Error messages present
- Duration > 30 seconds

NEXT STEPS:
──────────
If all checks pass:
  ✅ Stored procedure successfully re-created
  ✅ Metadata repository fully operational
  ✅ Ready to activate daily refresh task
  ✅ Ready to use in Streamlit apps

If any checks fail:
  ❌ Review error messages
  ❌ Check PROCEDURE_EXECUTION_LOG for details
  ❌ Re-run CREATE_STORED_PROCEDURE_ONLY.sql
  ❌ Contact support if issues persist

================================================================================
*/
