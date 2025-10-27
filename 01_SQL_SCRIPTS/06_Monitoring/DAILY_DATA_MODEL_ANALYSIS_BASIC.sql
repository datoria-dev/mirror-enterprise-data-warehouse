-- =====================================================
-- DAILY DATA MODEL ANALYSIS (BASIC VERSION)
-- =====================================================
-- Purpose: Data model health analysis using INFORMATION_SCHEMA
-- Requirements: Only requires standard database access (no ACCOUNT_USAGE)
-- Works with: DEV_DEVELOPER role
-- Author: Data Engineering Team
-- Last Updated: 2025-10-22
-- =====================================================

-- Set context explicitly
-- Database: DEV_LANDING
-- Schema: SECURITY_ANALYTICS
USE DATABASE DEV_LANDING;
USE SCHEMA SECURITY_ANALYTICS;

-- =====================================================
-- SECTION 1: DATABASE OBJECT INVENTORY
-- =====================================================

SELECT
    'OBJECT_INVENTORY' AS analysis_section,
    CURRENT_TIMESTAMP() AS analysis_timestamp,
    TABLE_CATALOG AS database_name,
    TABLE_SCHEMA AS schema_name,
    TABLE_TYPE AS object_type,
    COUNT(*) AS object_count,
    SUM(ROW_COUNT) AS total_rows,
    ROUND(SUM(BYTES) / POWER(1024, 3), 2) AS total_size_gb,
    ROUND(AVG(BYTES) / POWER(1024, 2), 2) AS avg_size_mb,
    MAX(LAST_ALTERED) AS last_modified_date
FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
GROUP BY
    TABLE_CATALOG,
    TABLE_SCHEMA,
    TABLE_TYPE
ORDER BY
    TABLE_SCHEMA,
    TABLE_TYPE;

-- =====================================================
-- SECTION 2: TOP 50 LARGEST TABLES
-- =====================================================

SELECT
    'TABLE_SIZE_ANALYSIS' AS analysis_section,
    CURRENT_TIMESTAMP() AS analysis_timestamp,
    TABLE_SCHEMA AS schema_name,
    TABLE_NAME,
    TABLE_TYPE,
    ROW_COUNT,
    ROUND(BYTES / POWER(1024, 3), 4) AS size_gb,
    ROUND(BYTES / POWER(1024, 2), 2) AS size_mb,
    LAST_ALTERED,
    DATEDIFF(day, LAST_ALTERED, CURRENT_TIMESTAMP()) AS days_since_modified,
    CASE
        WHEN ROW_COUNT = 0 THEN 'EMPTY'
        WHEN DATEDIFF(day, LAST_ALTERED, CURRENT_TIMESTAMP()) > 30 THEN 'STALE'
        WHEN DATEDIFF(day, LAST_ALTERED, CURRENT_TIMESTAMP()) > 7 THEN 'AGING'
        ELSE 'ACTIVE'
    END AS table_status
FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
    AND TABLE_TYPE IN ('BASE TABLE', 'VIEW')
ORDER BY
    BYTES DESC
LIMIT 50;

-- =====================================================
-- SECTION 3: TABLE GROWTH TRACKING
-- =====================================================

SELECT
    'TABLE_GROWTH' AS analysis_section,
    CURRENT_TIMESTAMP() AS analysis_timestamp,
    TABLE_SCHEMA AS schema_name,
    COUNT(*) AS table_count,
    SUM(ROW_COUNT) AS total_rows,
    ROUND(SUM(BYTES) / POWER(1024, 3), 2) AS total_size_gb,
    ROUND(AVG(ROW_COUNT), 0) AS avg_rows_per_table,
    MAX(LAST_ALTERED) AS most_recent_update,
    MIN(LAST_ALTERED) AS oldest_update
FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
    AND TABLE_TYPE = 'BASE TABLE'
GROUP BY
    TABLE_SCHEMA
ORDER BY
    total_size_gb DESC;

-- =====================================================
-- SECTION 4: DATA FRESHNESS ANALYSIS
-- =====================================================

SELECT
    'DATA_FRESHNESS' AS analysis_section,
    CURRENT_TIMESTAMP() AS analysis_timestamp,
    TABLE_SCHEMA AS schema_name,
    TABLE_NAME,
    ROW_COUNT AS total_rows,
    LAST_ALTERED AS last_updated,
    DATEDIFF(hour, LAST_ALTERED, CURRENT_TIMESTAMP()) AS hours_since_update,
    CASE
        WHEN DATEDIFF(hour, LAST_ALTERED, CURRENT_TIMESTAMP()) <= 24 THEN 'FRESH'
        WHEN DATEDIFF(hour, LAST_ALTERED, CURRENT_TIMESTAMP()) <= 168 THEN 'RECENT'
        WHEN DATEDIFF(hour, LAST_ALTERED, CURRENT_TIMESTAMP()) <= 720 THEN 'AGING'
        ELSE 'STALE'
    END AS freshness_status,
    CASE
        WHEN ROW_COUNT > 0 THEN 'HAS_DATA'
        ELSE 'EMPTY'
    END AS data_status
FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
    AND TABLE_TYPE = 'BASE TABLE'
ORDER BY
    hours_since_update DESC
LIMIT 50;

-- =====================================================
-- SECTION 5: COLUMN ANALYSIS
-- =====================================================

SELECT
    'COLUMN_ANALYSIS' AS analysis_section,
    CURRENT_TIMESTAMP() AS analysis_timestamp,
    TABLE_SCHEMA AS schema_name,
    COUNT(DISTINCT TABLE_NAME) AS table_count,
    COUNT(*) AS total_columns,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT TABLE_NAME), 1) AS avg_columns_per_table,
    COUNT(CASE WHEN IS_NULLABLE = 'YES' THEN 1 END) AS nullable_columns,
    COUNT(CASE WHEN IS_NULLABLE = 'NO' THEN 1 END) AS not_null_columns,
    ROUND(COUNT(CASE WHEN IS_NULLABLE = 'NO' THEN 1 END) * 100.0 / COUNT(*), 1) AS not_null_pct
FROM DEV_LANDING.INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
GROUP BY
    TABLE_SCHEMA
ORDER BY
    TABLE_SCHEMA;

-- =====================================================
-- SECTION 6: DATA TYPE DISTRIBUTION
-- =====================================================

SELECT
    'DATA_TYPE_DISTRIBUTION' AS analysis_section,
    CURRENT_TIMESTAMP() AS analysis_timestamp,
    TABLE_SCHEMA AS schema_name,
    DATA_TYPE,
    COUNT(*) AS column_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY TABLE_SCHEMA), 1) AS percentage
FROM DEV_LANDING.INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
GROUP BY
    TABLE_SCHEMA,
    DATA_TYPE
ORDER BY
    TABLE_SCHEMA,
    column_count DESC;

-- =====================================================
-- SECTION 7: CONSTRAINT COVERAGE
-- =====================================================

SELECT
    'CONSTRAINT_COVERAGE' AS analysis_section,
    CURRENT_TIMESTAMP() AS analysis_timestamp,
    tc.TABLE_SCHEMA AS schema_name,
    tc.TABLE_NAME,
    tc.CONSTRAINT_TYPE,
    COUNT(*) AS constraint_count,
    LISTAGG(tc.CONSTRAINT_NAME, ', ') WITHIN GROUP (ORDER BY tc.CONSTRAINT_NAME) AS constraint_names
FROM DEV_LANDING.INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
WHERE tc.TABLE_SCHEMA = 'SECURITY_ANALYTICS'
GROUP BY
    tc.TABLE_SCHEMA,
    tc.TABLE_NAME,
    tc.CONSTRAINT_TYPE
ORDER BY
    tc.TABLE_SCHEMA,
    tc.TABLE_NAME,
    tc.CONSTRAINT_TYPE;

-- =====================================================
-- SECTION 8: VIEW ANALYSIS
-- =====================================================

SELECT
    'VIEW_ANALYSIS' AS analysis_section,
    CURRENT_TIMESTAMP() AS analysis_timestamp,
    TABLE_SCHEMA AS schema_name,
    COUNT(*) AS view_count,
    ROUND(SUM(BYTES) / POWER(1024, 2), 2) AS total_size_mb,
    MAX(LAST_ALTERED) AS last_modified
FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
    AND TABLE_TYPE = 'VIEW'
GROUP BY
    TABLE_SCHEMA
ORDER BY
    TABLE_SCHEMA;

-- =====================================================
-- SECTION 9: SCHEMA FUNCTIONS
-- =====================================================

SELECT
    'FUNCTION_ANALYSIS' AS analysis_section,
    CURRENT_TIMESTAMP() AS analysis_timestamp,
    FUNCTION_SCHEMA AS schema_name,
    COUNT(*) AS function_count,
    COUNT(CASE WHEN DATA_TYPE = 'TABLE' THEN 1 END) AS table_functions,
    COUNT(CASE WHEN DATA_TYPE != 'TABLE' THEN 1 END) AS scalar_functions
FROM DEV_LANDING.INFORMATION_SCHEMA.FUNCTIONS
WHERE FUNCTION_SCHEMA = 'SECURITY_ANALYTICS'
GROUP BY
    FUNCTION_SCHEMA
ORDER BY
    FUNCTION_SCHEMA;

-- =====================================================
-- SECTION 10: PROCEDURE ANALYSIS
-- =====================================================

SELECT
    'PROCEDURE_ANALYSIS' AS analysis_section,
    CURRENT_TIMESTAMP() AS analysis_timestamp,
    PROCEDURE_SCHEMA AS schema_name,
    PROCEDURE_NAME,
    CREATED AS created_date,
    LAST_ALTERED AS last_modified,
    DATEDIFF(day, LAST_ALTERED, CURRENT_TIMESTAMP()) AS days_since_modified
FROM DEV_LANDING.INFORMATION_SCHEMA.PROCEDURES
WHERE PROCEDURE_SCHEMA = 'SECURITY_ANALYTICS'
ORDER BY
    PROCEDURE_SCHEMA,
    PROCEDURE_NAME;

-- =====================================================
-- SECTION 11: STORAGE COST ESTIMATION
-- =====================================================

SELECT
    'STORAGE_COSTS' AS analysis_section,
    CURRENT_TIMESTAMP() AS analysis_timestamp,
    TABLE_SCHEMA AS schema_name,
    COUNT(DISTINCT TABLE_NAME) AS table_count,
    SUM(ROW_COUNT) AS total_rows,
    ROUND(SUM(BYTES) / POWER(1024, 3), 2) AS total_size_gb,
    ROUND(SUM(BYTES) / POWER(1024, 4), 4) AS total_size_tb,
    ROUND((SUM(BYTES) / POWER(1024, 4)) * 23, 2) AS estimated_monthly_cost_usd,
    ROUND((SUM(BYTES) / POWER(1024, 4)) * 23 * 12, 2) AS estimated_annual_cost_usd
FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
GROUP BY
    TABLE_SCHEMA
ORDER BY
    total_size_gb DESC;

-- =====================================================
-- SECTION 12: EMPTY TABLES
-- =====================================================

SELECT
    'EMPTY_TABLES' AS analysis_section,
    CURRENT_TIMESTAMP() AS analysis_timestamp,
    TABLE_SCHEMA AS schema_name,
    TABLE_NAME,
    TABLE_TYPE,
    CREATED AS created_date,
    LAST_ALTERED AS last_modified,
    DATEDIFF(day, CREATED, CURRENT_TIMESTAMP()) AS days_since_created
FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
    AND TABLE_TYPE = 'BASE TABLE'
    AND (ROW_COUNT = 0 OR ROW_COUNT IS NULL)
ORDER BY
    days_since_created DESC;

-- =====================================================
-- SECTION 13: DAILY SUMMARY DASHBOARD
-- =====================================================

SELECT
    'DAILY_SUMMARY' AS analysis_section,
    CURRENT_DATE() AS analysis_date,
    CURRENT_TIMESTAMP() AS analysis_timestamp,

    -- Schema Statistics
    (SELECT COUNT(*) FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
     WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS' AND TABLE_TYPE = 'BASE TABLE') AS total_tables,

    (SELECT COUNT(*) FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
     WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS' AND TABLE_TYPE = 'VIEW') AS total_views,

    (SELECT SUM(ROW_COUNT) FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
     WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS') AS total_rows,

    (SELECT ROUND(SUM(BYTES) / POWER(1024, 3), 2) FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
     WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS') AS total_storage_gb,

    (SELECT COUNT(*) FROM DEV_LANDING.INFORMATION_SCHEMA.COLUMNS
     WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS') AS total_columns,

    (SELECT COUNT(*) FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
     WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
     AND TABLE_TYPE = 'BASE TABLE'
     AND (ROW_COUNT = 0 OR ROW_COUNT IS NULL)) AS empty_tables;

-- =====================================================
-- END OF BASIC ANALYSIS SCRIPT
-- =====================================================
