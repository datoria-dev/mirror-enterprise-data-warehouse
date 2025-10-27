/*
================================================================================
Monitor Metadata Repository Logs - Daily Health Check
================================================================================

Quick queries to monitor the health of the metadata repository.
Run these queries daily to ensure everything is working correctly.

Date: 2025-10-24
================================================================================
*/

USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;
USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA METADATA;

-- ============================================================================
-- QUICK HEALTH CHECK - Run This First
-- ============================================================================

SELECT
    '🎯 METADATA REPOSITORY HEALTH CHECK' as SECTION,
    CURRENT_TIMESTAMP() as CHECK_TIME;

-- Latest execution status
SELECT
    '1️⃣ LATEST EXECUTION' as CHECK,
    CASE
        WHEN STATUS = 'SUCCESS' THEN '✅ SUCCESS'
        WHEN STATUS = 'FAILED' THEN '❌ FAILED'
        ELSE '⚠️  ' || STATUS
    END as STATUS,
    EXECUTION_START,
    EXECUTION_DURATION_SECONDS as DURATION_SEC,
    TABLES_PROCESSED,
    COLUMNS_PROCESSED,
    ERROR_MESSAGE
FROM PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 1;

-- Execution count today
SELECT
    '2️⃣ EXECUTIONS TODAY' as CHECK,
    COUNT(*) as TOTAL_EXECUTIONS,
    SUM(CASE WHEN STATUS = 'SUCCESS' THEN 1 ELSE 0 END) as SUCCESS_COUNT,
    SUM(CASE WHEN STATUS = 'FAILED' THEN 1 ELSE 0 END) as FAILED_COUNT,
    ROUND(AVG(EXECUTION_DURATION_SECONDS), 2) as AVG_DURATION_SEC
FROM PROCEDURE_EXECUTION_LOG
WHERE DATE(EXECUTION_START) = CURRENT_DATE();

-- Task status
SELECT
    '3️⃣ TASK STATUS' as CHECK,
    NAME,
    CASE
        WHEN STATE = 'started' THEN '✅ ACTIVE'
        WHEN STATE = 'suspended' THEN '⚠️  SUSPENDED'
        ELSE '❌ ' || STATE
    END as STATE,
    NEXT_SCHEDULED_TIME
FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TASKS
WHERE NAME = 'TASK_DAILY_METADATA_REFRESH';

-- Data freshness
SELECT
    '4️⃣ DATA FRESHNESS' as CHECK,
    COUNT(*) as TOTAL_SERVICES,
    COUNT(DISTINCT SERVICE_NAME) as UNIQUE_SERVICES,
    SUM(TABLE_COUNT) as TOTAL_TABLES,
    SUM(TOTAL_ROWS) as TOTAL_ROWS,
    SUM(TOTAL_COLUMNS) as TOTAL_COLUMNS
FROM VW_SERVICE_SUMMARY;

-- ============================================================================
-- EXECUTION LOG ANALYSIS
-- ============================================================================

-- Last 10 executions
SELECT
    '📊 LAST 10 EXECUTIONS' as SECTION,
    CURRENT_TIMESTAMP() as REPORT_TIME;

SELECT
    ROW_NUMBER() OVER (ORDER BY EXECUTION_START DESC) as EXECUTION_NUM,
    EXECUTION_START,
    CASE
        WHEN STATUS = 'SUCCESS' THEN '✅'
        WHEN STATUS = 'FAILED' THEN '❌'
        ELSE '⚠️'
    END as STATUS_ICON,
    STATUS,
    EXECUTION_DURATION_SECONDS as DURATION,
    TABLES_PROCESSED as TABLES,
    COLUMNS_PROCESSED as COLUMNS,
    SUBSTRING(ERROR_MESSAGE, 1, 50) as ERROR_PREVIEW
FROM PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 10;

-- ============================================================================
-- PERFORMANCE TRENDS (Last 7 Days)
-- ============================================================================

SELECT
    '📈 PERFORMANCE TREND (7 DAYS)' as SECTION,
    CURRENT_TIMESTAMP() as REPORT_TIME;

SELECT
    DATE(EXECUTION_START) as EXECUTION_DATE,
    COUNT(*) as EXECUTIONS,
    SUM(CASE WHEN STATUS = 'SUCCESS' THEN 1 ELSE 0 END) as SUCCESS,
    SUM(CASE WHEN STATUS = 'FAILED' THEN 1 ELSE 0 END) as FAILED,
    ROUND(AVG(EXECUTION_DURATION_SECONDS), 2) as AVG_DURATION,
    MIN(EXECUTION_DURATION_SECONDS) as MIN_DURATION,
    MAX(EXECUTION_DURATION_SECONDS) as MAX_DURATION,
    ROUND(AVG(TABLES_PROCESSED), 0) as AVG_TABLES,
    ROUND(AVG(COLUMNS_PROCESSED), 0) as AVG_COLUMNS
FROM PROCEDURE_EXECUTION_LOG
WHERE EXECUTION_START >= DATEADD(day, -7, CURRENT_DATE())
GROUP BY DATE(EXECUTION_START)
ORDER BY EXECUTION_DATE DESC;

-- ============================================================================
-- ERROR DETECTION
-- ============================================================================

SELECT
    '🚨 RECENT ERRORS' as SECTION,
    CURRENT_TIMESTAMP() as REPORT_TIME;

SELECT
    LOG_ID,
    EXECUTION_START,
    EXECUTION_DURATION_SECONDS as DURATION,
    TABLES_PROCESSED,
    COLUMNS_PROCESSED,
    ERROR_MESSAGE,
    EXECUTION_DETAILS
FROM PROCEDURE_EXECUTION_LOG
WHERE STATUS = 'FAILED'
  AND EXECUTION_START >= DATEADD(day, -7, CURRENT_DATE())
ORDER BY EXECUTION_START DESC;

-- If no errors, show success message
SELECT
    CASE
        WHEN COUNT(*) = 0 THEN '✅ NO ERRORS IN LAST 7 DAYS'
        ELSE '⚠️  ' || COUNT(*) || ' ERRORS FOUND'
    END as ERROR_STATUS
FROM PROCEDURE_EXECUTION_LOG
WHERE STATUS = 'FAILED'
  AND EXECUTION_START >= DATEADD(day, -7, CURRENT_DATE());

-- ============================================================================
-- TASK EXECUTION HISTORY
-- ============================================================================

SELECT
    '⏰ TASK EXECUTION HISTORY' as SECTION,
    CURRENT_TIMESTAMP() as REPORT_TIME;

SELECT
    SCHEDULED_TIME,
    COMPLETED_TIME,
    CASE
        WHEN STATE = 'SUCCEEDED' THEN '✅'
        WHEN STATE = 'FAILED' THEN '❌'
        ELSE '⚠️'
    END as STATUS_ICON,
    STATE,
    DATEDIFF(second, SCHEDULED_TIME, COMPLETED_TIME) as DURATION_SEC,
    RETURN_VALUE,
    ERROR_CODE,
    SUBSTRING(ERROR_MESSAGE, 1, 100) as ERROR_MESSAGE
FROM TABLE(DEV_TRANSFORMATION.INFORMATION_SCHEMA.TASK_HISTORY())
WHERE NAME = 'TASK_DAILY_METADATA_REFRESH'
  AND SCHEDULED_TIME >= DATEADD(day, -7, CURRENT_DATE())
ORDER BY SCHEDULED_TIME DESC
LIMIT 10;

-- ============================================================================
-- STATISTICS SUMMARY
-- ============================================================================

SELECT
    '📊 EXECUTION STATISTICS' as SECTION,
    CURRENT_TIMESTAMP() as REPORT_TIME;

SELECT
    'Total Executions' as METRIC,
    COUNT(*) as VALUE,
    '' as UNIT
FROM PROCEDURE_EXECUTION_LOG
UNION ALL
SELECT
    'Success Count',
    COUNT(*),
    ''
FROM PROCEDURE_EXECUTION_LOG
WHERE STATUS = 'SUCCESS'
UNION ALL
SELECT
    'Failed Count',
    COUNT(*),
    ''
FROM PROCEDURE_EXECUTION_LOG
WHERE STATUS = 'FAILED'
UNION ALL
SELECT
    'Success Rate',
    ROUND(100.0 * COUNT(CASE WHEN STATUS = 'SUCCESS' THEN 1 END) / COUNT(*), 2),
    '%'
FROM PROCEDURE_EXECUTION_LOG
UNION ALL
SELECT
    'Avg Duration',
    ROUND(AVG(EXECUTION_DURATION_SECONDS), 2),
    'sec'
FROM PROCEDURE_EXECUTION_LOG
WHERE STATUS = 'SUCCESS'
UNION ALL
SELECT
    'Min Duration',
    MIN(EXECUTION_DURATION_SECONDS),
    'sec'
FROM PROCEDURE_EXECUTION_LOG
WHERE STATUS = 'SUCCESS'
UNION ALL
SELECT
    'Max Duration',
    MAX(EXECUTION_DURATION_SECONDS),
    'sec'
FROM PROCEDURE_EXECUTION_LOG
WHERE STATUS = 'SUCCESS'
UNION ALL
SELECT
    'Avg Tables Processed',
    ROUND(AVG(TABLES_PROCESSED), 0),
    'tables'
FROM PROCEDURE_EXECUTION_LOG
WHERE STATUS = 'SUCCESS'
UNION ALL
SELECT
    'Avg Columns Processed',
    ROUND(AVG(COLUMNS_PROCESSED), 0),
    'columns'
FROM PROCEDURE_EXECUTION_LOG
WHERE STATUS = 'SUCCESS'
ORDER BY METRIC;

-- ============================================================================
-- DATA QUALITY CHECKS
-- ============================================================================

SELECT
    '🔍 DATA QUALITY CHECKS' as SECTION,
    CURRENT_TIMESTAMP() as REPORT_TIME;

-- Check for stale data (not updated in last 7 days)
SELECT
    'Stale Tables (>7 days)' as CHECK,
    COUNT(*) as COUNT,
    LISTAGG(SERVICE_NAME || '.' || TABLE_NAME, ', ') WITHIN GROUP (ORDER BY SERVICE_NAME) as TABLES
FROM VW_TABLE_CATALOG
WHERE DATEDIFF(day, LAST_UPDATED, CURRENT_TIMESTAMP()) > 7
  AND IS_ACTIVE = TRUE
GROUP BY 1;

-- Check for empty tables
SELECT
    'Empty Active Tables' as CHECK,
    COUNT(*) as COUNT,
    LISTAGG(SERVICE_NAME || '.' || TABLE_NAME, ', ') WITHIN GROUP (ORDER BY SERVICE_NAME) as TABLES
FROM VW_TABLE_CATALOG
WHERE TOTAL_ROWS = 0
  AND IS_ACTIVE = TRUE
GROUP BY 1;

-- Check for "Unknown" service tables
SELECT
    'Unknown Service Tables' as CHECK,
    COUNT(*) as COUNT,
    LISTAGG(TABLE_NAME, ', ') WITHIN GROUP (ORDER BY TABLE_NAME) as TABLES
FROM TABLE_REGISTRY
WHERE SERVICE_NAME = 'Unknown'
GROUP BY 1;

-- ============================================================================
-- EXPORT STATUS
-- ============================================================================

SELECT
    '📤 EXPORT TABLES STATUS' as SECTION,
    CURRENT_TIMESTAMP() as REPORT_TIME;

SELECT
    TABLE_NAME,
    ROW_COUNT,
    BYTES / (1024 * 1024) as SIZE_MB,
    CREATED
FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'METADATA_EXPORTS'
  AND TABLE_TYPE = 'BASE TABLE'
ORDER BY CREATED DESC
LIMIT 20;

-- ============================================================================
-- ALERTS AND RECOMMENDATIONS
-- ============================================================================

SELECT
    '⚡ ALERTS AND RECOMMENDATIONS' as SECTION,
    CURRENT_TIMESTAMP() as REPORT_TIME;

-- Alert 1: Recent failures
SELECT
    '🚨 ALERT' as TYPE,
    'Recent execution failures detected' as MESSAGE,
    COUNT(*) as COUNT,
    'Review error logs immediately' as ACTION
FROM PROCEDURE_EXECUTION_LOG
WHERE STATUS = 'FAILED'
  AND EXECUTION_START >= DATEADD(day, -1, CURRENT_DATE())
HAVING COUNT(*) > 0

UNION ALL

-- Alert 2: Task suspended
SELECT
    '⚠️  WARNING',
    'Daily refresh task is suspended',
    1,
    'Resume task: ALTER TASK TASK_DAILY_METADATA_REFRESH RESUME'
FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TASKS
WHERE NAME = 'TASK_DAILY_METADATA_REFRESH'
  AND STATE = 'suspended'

UNION ALL

-- Alert 3: No execution today
SELECT
    '⚠️  WARNING',
    'No metadata refresh executed today',
    1,
    'Manually run: CALL SP_REFRESH_METADATA()'
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1
    FROM PROCEDURE_EXECUTION_LOG
    WHERE DATE(EXECUTION_START) = CURRENT_DATE()
)

UNION ALL

-- Alert 4: Slow execution
SELECT
    '⚠️  WARNING',
    'Recent execution took longer than usual',
    EXECUTION_DURATION_SECONDS,
    'Monitor performance and optimize if needed'
FROM PROCEDURE_EXECUTION_LOG
WHERE EXECUTION_START = (SELECT MAX(EXECUTION_START) FROM PROCEDURE_EXECUTION_LOG)
  AND EXECUTION_DURATION_SECONDS > 60

UNION ALL

-- Success message if no alerts
SELECT
    '✅ SUCCESS',
    'All systems operational',
    0,
    'No action required'
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM PROCEDURE_EXECUTION_LOG
    WHERE STATUS = 'FAILED'
      AND EXECUTION_START >= DATEADD(day, -1, CURRENT_DATE())
)
AND EXISTS (
    SELECT 1 FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TASKS
    WHERE NAME = 'TASK_DAILY_METADATA_REFRESH'
      AND STATE = 'started'
)
AND EXISTS (
    SELECT 1 FROM PROCEDURE_EXECUTION_LOG
    WHERE DATE(EXECUTION_START) = CURRENT_DATE()
);

-- ============================================================================
-- QUICK ACTIONS
-- ============================================================================

/*
QUICK ACTIONS - Copy and execute as needed:

1. Manual refresh:
   CALL DEV_TRANSFORMATION.METADATA.SP_REFRESH_METADATA();

2. Resume task:
   ALTER TASK DEV_TRANSFORMATION.METADATA.TASK_DAILY_METADATA_REFRESH RESUME;

3. Suspend task:
   ALTER TASK DEV_TRANSFORMATION.METADATA.TASK_DAILY_METADATA_REFRESH SUSPEND;

4. View latest log details:
   SELECT * FROM DEV_TRANSFORMATION.METADATA.PROCEDURE_EXECUTION_LOG
   ORDER BY EXECUTION_START DESC LIMIT 1;

5. Export latest results:
   @EXPORT_METADATA_RESULTS.sql

6. Full verification:
   @VERIFY_METADATA_REPOSITORY.sql
*/

-- ============================================================================
-- SAVE RESULTS
-- ============================================================================

/*
💾 IMPORTANT: Save these monitoring results to file!

After running this script, save the results:
- File: 04_METADATA_SAMPLES/logs/daily_health_check_YYYY-MM-DD.csv
- Or:   04_METADATA_SAMPLES/logs/daily_health_check_YYYY-MM-DD.json

This creates a historical record of system health.
*/

-- Create export table for today's health check
CREATE OR REPLACE TABLE DEV_TRANSFORMATION.METADATA_EXPORTS.DAILY_HEALTH_CHECK AS
SELECT
    CURRENT_DATE() as CHECK_DATE,
    CURRENT_TIMESTAMP() as CHECK_TIMESTAMP,
    (SELECT COUNT(*) FROM PROCEDURE_EXECUTION_LOG WHERE DATE(EXECUTION_START) = CURRENT_DATE()) as EXECUTIONS_TODAY,
    (SELECT COUNT(*) FROM PROCEDURE_EXECUTION_LOG WHERE STATUS = 'FAILED' AND DATE(EXECUTION_START) = CURRENT_DATE()) as FAILURES_TODAY,
    (SELECT AVG(EXECUTION_DURATION_SECONDS) FROM PROCEDURE_EXECUTION_LOG WHERE DATE(EXECUTION_START) = CURRENT_DATE()) as AVG_DURATION_TODAY,
    (SELECT STATUS FROM PROCEDURE_EXECUTION_LOG ORDER BY EXECUTION_START DESC LIMIT 1) as LATEST_STATUS,
    (SELECT EXECUTION_START FROM PROCEDURE_EXECUTION_LOG ORDER BY EXECUTION_START DESC LIMIT 1) as LATEST_EXECUTION,
    (SELECT STATE FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TASKS WHERE NAME = 'TASK_DAILY_METADATA_REFRESH') as TASK_STATE,
    (SELECT COUNT(*) FROM VW_SERVICE_SUMMARY) as TOTAL_SERVICES,
    (SELECT SUM(TABLE_COUNT) FROM VW_SERVICE_SUMMARY) as TOTAL_TABLES,
    (SELECT SUM(TOTAL_COLUMNS) FROM VW_SERVICE_SUMMARY) as TOTAL_COLUMNS,
    (SELECT SUM(TOTAL_ROWS) FROM VW_SERVICE_SUMMARY) as TOTAL_ROWS;

-- View the health check summary
SELECT * FROM DEV_TRANSFORMATION.METADATA_EXPORTS.DAILY_HEALTH_CHECK;

-- ✅ Save this result as: 04_METADATA_SAMPLES/logs/health_check_YYYY-MM-DD.csv

/*
================================================================================
END OF HEALTH CHECK

Recommended frequency: Daily (every morning)
Expected execution time: <10 seconds
Next steps:
1. Review alerts and take action if needed
2. Save results to file
3. Share with team if issues found
================================================================================
*/
