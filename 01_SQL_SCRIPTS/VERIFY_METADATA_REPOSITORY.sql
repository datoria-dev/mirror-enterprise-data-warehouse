/*
================================================================================
Verify Metadata Repository - Validation and Diagnostics
================================================================================

Execute these queries AFTER running CREATE_METADATA_REPOSITORY.sql to verify:
1. All 22 services are detected
2. Tables are properly categorized
3. Column metadata is complete
4. Daily refresh task is configured
5. No orphaned or "Unknown" tables

Date: 2025-10-24
================================================================================
*/

USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;
USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA METADATA;

-- ============================================================================
-- VERIFICATION 1: Service Catalog Completeness
-- ============================================================================
-- Expected: 22 services across 7 categories

SELECT
    '1. SERVICE CATALOG COMPLETENESS' as VERIFICATION_SECTION,
    COUNT(*) as TOTAL_SERVICES,
    COUNT(CASE WHEN IS_ACTIVE = TRUE THEN 1 END) as ACTIVE_SERVICES,
    COUNT(CASE WHEN IS_ACTIVE = FALSE THEN 1 END) as INACTIVE_SERVICES
FROM SERVICE_CATALOG;

-- Should show 22 total services

-- ============================================================================
-- VERIFICATION 2: Services by Category
-- ============================================================================

SELECT
    '2. SERVICES BY CATEGORY' as VERIFICATION_SECTION,
    SERVICE_CATEGORY,
    COUNT(*) as SERVICE_COUNT,
    LISTAGG(SERVICE_NAME, ', ') WITHIN GROUP (ORDER BY SERVICE_NAME) as SERVICES
FROM SERVICE_CATALOG
GROUP BY SERVICE_CATEGORY
ORDER BY SERVICE_COUNT DESC, SERVICE_CATEGORY;

-- Expected counts:
-- Endpoint Protection: 9
-- Threat Intelligence: 4
-- Vulnerability Management: 2
-- Identity & Access Management: 2
-- Asset Management: 1
-- Email Security: 1
-- SIEM: 1
-- Cloud Security: 1

-- ============================================================================
-- VERIFICATION 3: Detected Services with Data
-- ============================================================================

SELECT
    '3. DETECTED SERVICES WITH DATA' as VERIFICATION_SECTION,
    tr.SERVICE_NAME,
    sc.SERVICE_CATEGORY,
    COUNT(DISTINCT tr.TABLE_NAME) as TABLE_COUNT,
    SUM(tr.TOTAL_ROWS) as TOTAL_ROWS,
    COUNT(DISTINCT cm.COLUMN_NAME) as TOTAL_COLUMNS
FROM TABLE_REGISTRY tr
LEFT JOIN SERVICE_CATALOG sc ON tr.SERVICE_NAME = sc.SERVICE_NAME
LEFT JOIN COLUMN_METADATA cm ON tr.TABLE_ID = cm.TABLE_ID
GROUP BY tr.SERVICE_NAME, sc.SERVICE_CATEGORY
ORDER BY TABLE_COUNT DESC, TOTAL_ROWS DESC;

-- This shows which services have actual tables in the database

-- ============================================================================
-- VERIFICATION 4: Check for "Unknown" Services
-- ============================================================================

SELECT
    '4. UNKNOWN SERVICES (need pattern matching)' as VERIFICATION_SECTION,
    TABLE_NAME,
    DATABASE_NAME,
    SCHEMA_NAME,
    TOTAL_ROWS
FROM TABLE_REGISTRY
WHERE SERVICE_NAME = 'Unknown'
ORDER BY TOTAL_ROWS DESC;

-- Should be empty or minimal
-- If tables appear here, update service detection patterns

-- ============================================================================
-- VERIFICATION 5: Table Registry Statistics
-- ============================================================================

SELECT
    '5. TABLE REGISTRY STATISTICS' as VERIFICATION_SECTION,
    COUNT(DISTINCT TABLE_ID) as TOTAL_TABLES,
    COUNT(DISTINCT DATABASE_NAME) as TOTAL_DATABASES,
    COUNT(DISTINCT SCHEMA_NAME) as TOTAL_SCHEMAS,
    COUNT(DISTINCT SERVICE_NAME) as DETECTED_SERVICES,
    SUM(TOTAL_ROWS) as TOTAL_ROWS_ALL_TABLES,
    AVG(TOTAL_ROWS) as AVG_ROWS_PER_TABLE
FROM TABLE_REGISTRY;

-- ============================================================================
-- VERIFICATION 6: Column Metadata Completeness
-- ============================================================================

SELECT
    '6. COLUMN METADATA COMPLETENESS' as VERIFICATION_SECTION,
    COUNT(DISTINCT COLUMN_ID) as TOTAL_COLUMNS,
    COUNT(DISTINCT TABLE_ID) as TABLES_WITH_COLUMNS,
    COUNT(DISTINCT DATA_TYPE) as UNIQUE_DATA_TYPES,
    AVG(columns_per_table) as AVG_COLUMNS_PER_TABLE
FROM (
    SELECT
        TABLE_ID,
        COUNT(*) as columns_per_table
    FROM COLUMN_METADATA
    GROUP BY TABLE_ID
);

-- ============================================================================
-- VERIFICATION 7: Data Type Distribution
-- ============================================================================

SELECT
    '7. DATA TYPE DISTRIBUTION' as VERIFICATION_SECTION,
    DATA_TYPE,
    COUNT(*) as COLUMN_COUNT,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as PERCENTAGE
FROM COLUMN_METADATA
GROUP BY DATA_TYPE
ORDER BY COLUMN_COUNT DESC;

-- ============================================================================
-- VERIFICATION 8: Table Statistics History
-- ============================================================================

SELECT
    '8. TABLE STATISTICS HISTORY' as VERIFICATION_SECTION,
    COUNT(*) as SNAPSHOT_COUNT,
    MIN(SNAPSHOT_DATE) as FIRST_SNAPSHOT,
    MAX(SNAPSHOT_DATE) as LAST_SNAPSHOT,
    COUNT(DISTINCT TABLE_ID) as TABLES_TRACKED
FROM TABLE_STATISTICS;

-- Should show 1 snapshot after initial load
-- Will grow daily after task activation

-- ============================================================================
-- VERIFICATION 9: Stored Procedure Execution Logs
-- ============================================================================

-- Most recent execution
SELECT
    '9A. MOST RECENT EXECUTION' as VERIFICATION_SECTION,
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

-- Should show SUCCESS status for initial load

-- All executions today
SELECT
    '9B. EXECUTIONS TODAY' as VERIFICATION_SECTION,
    LOG_ID,
    EXECUTION_START,
    EXECUTION_DURATION_SECONDS,
    STATUS,
    TABLES_PROCESSED,
    COLUMNS_PROCESSED,
    ERROR_MESSAGE
FROM PROCEDURE_EXECUTION_LOG
WHERE DATE(EXECUTION_START) = CURRENT_DATE()
ORDER BY EXECUTION_START DESC;

-- Execution statistics
SELECT
    '9C. EXECUTION STATISTICS' as VERIFICATION_SECTION,
    STATUS,
    COUNT(*) as EXECUTION_COUNT,
    ROUND(AVG(EXECUTION_DURATION_SECONDS), 2) as AVG_DURATION,
    MIN(EXECUTION_DURATION_SECONDS) as MIN_DURATION,
    MAX(EXECUTION_DURATION_SECONDS) as MAX_DURATION
FROM PROCEDURE_EXECUTION_LOG
GROUP BY STATUS;

-- ============================================================================
-- VERIFICATION 9D: Stored Procedure Status
-- ============================================================================

SELECT
    '9D. STORED PROCEDURE STATUS' as VERIFICATION_SECTION,
    PROCEDURE_NAME,
    PROCEDURE_SCHEMA,
    CREATED,
    LAST_ALTERED
FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.PROCEDURES
WHERE PROCEDURE_SCHEMA = 'METADATA'
  AND PROCEDURE_NAME = 'SP_REFRESH_METADATA'
ORDER BY CREATED DESC;

-- Should show SP_REFRESH_METADATA created today

-- ============================================================================
-- VERIFICATION 10: Task Configuration
-- ============================================================================

SELECT
    '10. TASK CONFIGURATION' as VERIFICATION_SECTION,
    NAME as TASK_NAME,
    DATABASE_NAME,
    SCHEMA_NAME,
    SCHEDULE,
    STATE,
    CREATED_ON,
    LAST_COMMITTED_ON,
    NEXT_SCHEDULED_TIME
FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TASKS
WHERE SCHEMA_NAME = 'METADATA'
  AND NAME = 'TASK_DAILY_METADATA_REFRESH'
ORDER BY CREATED_ON DESC;

-- STATE should show "suspended" (not activated yet)
-- SCHEDULE should show "USING CRON 0 2 * * * UTC"

-- ============================================================================
-- VERIFICATION 11: Top 10 Largest Tables
-- ============================================================================

SELECT
    '11. TOP 10 LARGEST TABLES' as VERIFICATION_SECTION,
    SERVICE_NAME,
    TABLE_NAME,
    TOTAL_ROWS,
    TOTAL_COLUMNS,
    FULL_TABLE_NAME
FROM VW_TABLE_CATALOG
WHERE TOTAL_ROWS > 0
ORDER BY TOTAL_ROWS DESC
LIMIT 10;

-- ============================================================================
-- VERIFICATION 12: Empty Tables (Structure Only)
-- ============================================================================

SELECT
    '12. EMPTY TABLES (STRUCTURE ONLY)' as VERIFICATION_SECTION,
    SERVICE_NAME,
    TABLE_NAME,
    TOTAL_COLUMNS,
    FULL_TABLE_NAME
FROM VW_TABLE_CATALOG
WHERE TOTAL_ROWS = 0
ORDER BY SERVICE_NAME, TABLE_NAME;

-- Expected: Leviat tables, possibly others

-- ============================================================================
-- VERIFICATION 13: Services with Most Tables
-- ============================================================================

SELECT
    '13. SERVICES WITH MOST TABLES' as VERIFICATION_SECTION,
    SERVICE_NAME,
    TABLE_COUNT,
    TOTAL_ROWS,
    TOTAL_COLUMNS
FROM VW_SERVICE_SUMMARY
ORDER BY TABLE_COUNT DESC, TOTAL_ROWS DESC;

-- ============================================================================
-- VERIFICATION 14: Schema Coverage
-- ============================================================================

SELECT
    '14. SCHEMA COVERAGE' as VERIFICATION_SECTION,
    DATABASE_NAME,
    SCHEMA_NAME,
    COUNT(DISTINCT TABLE_NAME) as TABLE_COUNT,
    COUNT(DISTINCT SERVICE_NAME) as SERVICE_COUNT,
    SUM(TOTAL_ROWS) as TOTAL_ROWS
FROM TABLE_REGISTRY
GROUP BY DATABASE_NAME, SCHEMA_NAME
ORDER BY TABLE_COUNT DESC;

-- Shows which schemas contain the most tables

-- ============================================================================
-- VERIFICATION 15: Missing Services (Defined but No Data)
-- ============================================================================

SELECT
    '15. MISSING SERVICES (DEFINED BUT NO DATA)' as VERIFICATION_SECTION,
    sc.SERVICE_NAME,
    sc.SERVICE_CATEGORY,
    sc.IS_ACTIVE,
    CASE
        WHEN tr.SERVICE_NAME IS NULL THEN 'No tables found'
        ELSE 'Has tables'
    END as DATA_STATUS
FROM SERVICE_CATALOG sc
LEFT JOIN TABLE_REGISTRY tr ON sc.SERVICE_NAME = tr.SERVICE_NAME
WHERE tr.SERVICE_NAME IS NULL
ORDER BY sc.SERVICE_CATEGORY, sc.SERVICE_NAME;

-- Shows which services are defined but don't have tables yet
-- Useful for future pipeline development

-- ============================================================================
-- VERIFICATION 16: Data Quality Rules Status
-- ============================================================================

SELECT
    '16. DATA QUALITY RULES STATUS' as VERIFICATION_SECTION,
    COUNT(*) as TOTAL_RULES,
    COUNT(CASE WHEN IS_ACTIVE = TRUE THEN 1 END) as ACTIVE_RULES,
    COUNT(DISTINCT TABLE_ID) as TABLES_WITH_RULES
FROM DATA_QUALITY_RULES;

-- Should be 0 after initial setup (rules added later)

-- ============================================================================
-- VERIFICATION 17: Column Name Frequency Analysis
-- ============================================================================

SELECT
    '17. MOST COMMON COLUMN NAMES' as VERIFICATION_SECTION,
    COLUMN_NAME,
    COUNT(*) as FREQUENCY,
    COUNT(DISTINCT TABLE_ID) as TABLE_COUNT,
    LISTAGG(DISTINCT DATA_TYPE, ', ') WITHIN GROUP (ORDER BY DATA_TYPE) as DATA_TYPES_USED
FROM COLUMN_METADATA
GROUP BY COLUMN_NAME
HAVING COUNT(*) > 5
ORDER BY FREQUENCY DESC
LIMIT 20;

-- Shows common column patterns across tables

-- ============================================================================
-- VERIFICATION 18: Metadata Repository Size
-- ============================================================================

SELECT
    '18. METADATA REPOSITORY SIZE' as VERIFICATION_SECTION,
    TABLE_NAME,
    ROW_COUNT,
    BYTES / (1024 * 1024) as SIZE_MB
FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'METADATA'
  AND TABLE_TYPE = 'BASE TABLE'
ORDER BY ROW_COUNT DESC;

-- ============================================================================
-- VERIFICATION 19: View Functionality Test
-- ============================================================================

-- Test VW_TABLE_CATALOG
SELECT
    '19A. VW_TABLE_CATALOG TEST' as VERIFICATION_SECTION,
    COUNT(*) as TOTAL_RECORDS
FROM VW_TABLE_CATALOG;

-- Test VW_COLUMN_CATALOG
SELECT
    '19B. VW_COLUMN_CATALOG TEST' as VERIFICATION_SECTION,
    COUNT(*) as TOTAL_RECORDS
FROM VW_COLUMN_CATALOG;

-- Test VW_SERVICE_SUMMARY
SELECT
    '19C. VW_SERVICE_SUMMARY TEST' as VERIFICATION_SECTION,
    COUNT(*) as TOTAL_RECORDS
FROM VW_SERVICE_SUMMARY;

-- All three should return results without errors

-- ============================================================================
-- VERIFICATION 20: Complete Service Coverage Report
-- ============================================================================

SELECT
    '20. COMPLETE SERVICE COVERAGE REPORT' as VERIFICATION_SECTION,
    sc.SERVICE_CATEGORY,
    sc.SERVICE_NAME,
    sc.IS_ACTIVE as CATALOG_ACTIVE,
    COALESCE(ss.TABLE_COUNT, 0) as TABLES_FOUND,
    COALESCE(ss.TOTAL_ROWS, 0) as TOTAL_ROWS,
    COALESCE(ss.TOTAL_COLUMNS, 0) as TOTAL_COLUMNS,
    CASE
        WHEN ss.SERVICE_NAME IS NOT NULL THEN '✅ Has Data'
        WHEN sc.IS_ACTIVE = TRUE THEN '⚠️  Active but No Data'
        ELSE '❌ Inactive'
    END as STATUS
FROM SERVICE_CATALOG sc
LEFT JOIN VW_SERVICE_SUMMARY ss ON sc.SERVICE_NAME = ss.SERVICE_NAME
ORDER BY
    sc.SERVICE_CATEGORY,
    CASE
        WHEN ss.SERVICE_NAME IS NOT NULL THEN 1
        WHEN sc.IS_ACTIVE = TRUE THEN 2
        ELSE 3
    END,
    sc.SERVICE_NAME;

-- ============================================================================
-- SUMMARY REPORT
-- ============================================================================

SELECT
    '=' as DIVIDER,
    'METADATA REPOSITORY VERIFICATION SUMMARY' as REPORT_TITLE,
    '=' as DIVIDER;

SELECT
    'Total Services Defined' as METRIC,
    COUNT(*) as VALUE
FROM SERVICE_CATALOG
UNION ALL
SELECT
    'Services with Data',
    COUNT(DISTINCT SERVICE_NAME)
FROM TABLE_REGISTRY
WHERE SERVICE_NAME != 'Unknown'
UNION ALL
SELECT
    'Total Tables',
    COUNT(*)
FROM TABLE_REGISTRY
UNION ALL
SELECT
    'Total Columns',
    COUNT(*)
FROM COLUMN_METADATA
UNION ALL
SELECT
    'Total Rows (All Tables)',
    SUM(TOTAL_ROWS)
FROM TABLE_REGISTRY
UNION ALL
SELECT
    'Statistics Snapshots',
    COUNT(*)
FROM TABLE_STATISTICS
ORDER BY METRIC;

-- ============================================================================
-- NEXT STEPS
-- ============================================================================

/*
NEXT STEPS AFTER VERIFICATION:

1. Review "Unknown" tables (Verification 4)
   - If any tables show as "Unknown", update service detection patterns

2. Activate Daily Refresh Task (if all looks good)
   - ALTER TASK TASK_DAILY_METADATA_REFRESH RESUME;

3. Test Metadata Refresh Manually
   - CALL SP_REFRESH_METADATA();
   - Check execution time and results

4. Review Missing Services (Verification 15)
   - Plan data pipeline development for services without data

5. Start Using Metadata Repository
   - Begin rewriting Streamlit apps using VW_COLUMN_CATALOG
   - Reference QUERY_METADATA_REPOSITORY.sql for common queries

6. Monitor Daily Execution
   - Check TASK_HISTORY for daily refresh status
   - SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
     WHERE NAME = 'TASK_DAILY_METADATA_REFRESH'
     ORDER BY SCHEDULED_TIME DESC
     LIMIT 10;
*/
