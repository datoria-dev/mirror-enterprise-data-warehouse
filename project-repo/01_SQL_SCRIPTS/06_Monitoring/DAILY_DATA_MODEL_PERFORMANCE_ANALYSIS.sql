-- =====================================================
-- DAILY DATA MODEL AND PERFORMANCE ANALYSIS
-- =====================================================
-- Purpose: Comprehensive daily analysis of data model health and query performance
-- Output: JSON/CSV compatible result sets for automated monitoring
-- Schedule: Run daily via Python automation
-- Author: Data Engineering Team
-- Last Updated: 2025-10-22
-- =====================================================

USE DATABASE ITSECKPI_DEV;
USE SCHEMA DEV_TRANSFORMATION;

-- =====================================================
-- SECTION 1: DATABASE OBJECT INVENTORY
-- =====================================================
-- Track all database objects across the three layers

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
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA IN ('DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING')
GROUP BY
    TABLE_CATALOG,
    TABLE_SCHEMA,
    TABLE_TYPE
ORDER BY
    TABLE_SCHEMA,
    TABLE_TYPE;

-- =====================================================
-- SECTION 2: TABLE SIZE AND GROWTH ANALYSIS
-- =====================================================
-- Monitor table growth and identify largest tables

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
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA IN ('DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING')
    AND TABLE_TYPE IN ('BASE TABLE', 'VIEW')
ORDER BY
    BYTES DESC
LIMIT 50;

-- =====================================================
-- SECTION 3: QUERY PERFORMANCE METRICS (LAST 24 HOURS)
-- =====================================================
-- Analyze query patterns and identify performance issues

SELECT
    'QUERY_PERFORMANCE' AS analysis_section,
    CURRENT_TIMESTAMP() AS analysis_timestamp,
    DATE_TRUNC('HOUR', START_TIME) AS query_hour,
    DATABASE_NAME,
    SCHEMA_NAME,
    QUERY_TYPE,
    COUNT(*) AS query_count,
    ROUND(AVG(EXECUTION_TIME) / 1000, 2) AS avg_execution_seconds,
    ROUND(MAX(EXECUTION_TIME) / 1000, 2) AS max_execution_seconds,
    ROUND(MIN(EXECUTION_TIME) / 1000, 2) AS min_execution_seconds,
    ROUND(AVG(BYTES_SCANNED) / POWER(1024, 3), 4) AS avg_gb_scanned,
    ROUND(SUM(BYTES_SCANNED) / POWER(1024, 3), 2) AS total_gb_scanned,
    SUM(CASE WHEN ERROR_CODE IS NOT NULL THEN 1 ELSE 0 END) AS error_count,
    ROUND(SUM(CASE WHEN ERROR_CODE IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS error_rate_pct
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE START_TIME >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
    AND DATABASE_NAME = 'ITSECKPI_DEV'
    AND SCHEMA_NAME IN ('DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING')
    AND QUERY_TYPE NOT IN ('DESCRIBE', 'SHOW', 'USE')
GROUP BY
    DATE_TRUNC('HOUR', START_TIME),
    DATABASE_NAME,
    SCHEMA_NAME,
    QUERY_TYPE
ORDER BY
    query_hour DESC,
    query_count DESC;

-- =====================================================
-- SECTION 4: SLOWEST QUERIES (LAST 24 HOURS)
-- =====================================================
-- Identify queries requiring optimization

SELECT
    'SLOW_QUERIES' AS analysis_section,
    CURRENT_TIMESTAMP() AS analysis_timestamp,
    QUERY_ID,
    START_TIME,
    END_TIME,
    USER_NAME,
    SCHEMA_NAME,
    QUERY_TYPE,
    ROUND(EXECUTION_TIME / 1000, 2) AS execution_seconds,
    ROUND(TOTAL_ELAPSED_TIME / 1000, 2) AS total_elapsed_seconds,
    ROUND(BYTES_SCANNED / POWER(1024, 3), 4) AS gb_scanned,
    ROWS_PRODUCED,
    ROUND(PARTITIONS_SCANNED, 0) AS partitions_scanned,
    WAREHOUSE_NAME,
    WAREHOUSE_SIZE,
    LEFT(QUERY_TEXT, 200) AS query_preview
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE START_TIME >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
    AND DATABASE_NAME = 'ITSECKPI_DEV'
    AND EXECUTION_TIME > 10000  -- Queries taking more than 10 seconds
    AND QUERY_TYPE NOT IN ('DESCRIBE', 'SHOW', 'USE', 'CREATE', 'DROP')
ORDER BY
    EXECUTION_TIME DESC
LIMIT 20;

-- =====================================================
-- SECTION 5: DATA QUALITY METRICS
-- =====================================================
-- Measure data quality across key dimensions

SELECT
    'DATA_QUALITY' AS analysis_section,
    CURRENT_TIMESTAMP() AS analysis_timestamp,
    TABLE_SCHEMA AS schema_name,
    TABLE_NAME,
    ROW_COUNT AS total_rows,
    -- Calculate estimated null percentages (requires actual queries for accuracy)
    CASE
        WHEN ROW_COUNT > 0 THEN 'HAS_DATA'
        ELSE 'EMPTY'
    END AS data_status,
    LAST_ALTERED AS last_updated,
    DATEDIFF(hour, LAST_ALTERED, CURRENT_TIMESTAMP()) AS hours_since_update,
    CASE
        WHEN DATEDIFF(hour, LAST_ALTERED, CURRENT_TIMESTAMP()) <= 24 THEN 'FRESH'
        WHEN DATEDIFF(hour, LAST_ALTERED, CURRENT_TIMESTAMP()) <= 168 THEN 'RECENT'
        WHEN DATEDIFF(hour, LAST_ALTERED, CURRENT_TIMESTAMP()) <= 720 THEN 'AGING'
        ELSE 'STALE'
    END AS freshness_status
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA IN ('DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING')
    AND TABLE_TYPE = 'BASE TABLE'
ORDER BY
    hours_since_update DESC,
    ROW_COUNT DESC
LIMIT 50;

-- =====================================================
-- SECTION 6: WAREHOUSE UTILIZATION (LAST 24 HOURS)
-- =====================================================
-- Monitor compute resource usage

SELECT
    'WAREHOUSE_UTILIZATION' AS analysis_section,
    CURRENT_TIMESTAMP() AS analysis_timestamp,
    DATE_TRUNC('HOUR', START_TIME) AS usage_hour,
    WAREHOUSE_NAME,
    WAREHOUSE_SIZE,
    COUNT(*) AS query_count,
    ROUND(AVG(EXECUTION_TIME) / 1000, 2) AS avg_execution_seconds,
    ROUND(SUM(EXECUTION_TIME) / 1000 / 3600, 2) AS total_execution_hours,
    ROUND(AVG(QUEUED_OVERLOAD_TIME) / 1000, 2) AS avg_queue_seconds,
    SUM(CASE WHEN QUEUED_OVERLOAD_TIME > 0 THEN 1 ELSE 0 END) AS queued_query_count,
    ROUND(SUM(CREDITS_USED_CLOUD_SERVICES), 4) AS cloud_service_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE START_TIME >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
    AND DATABASE_NAME = 'ITSECKPI_DEV'
    AND WAREHOUSE_NAME IS NOT NULL
GROUP BY
    DATE_TRUNC('HOUR', START_TIME),
    WAREHOUSE_NAME,
    WAREHOUSE_SIZE
ORDER BY
    usage_hour DESC,
    total_execution_hours DESC;

-- =====================================================
-- SECTION 7: CONSTRAINT COVERAGE
-- =====================================================
-- Verify data integrity constraints

SELECT
    'CONSTRAINT_COVERAGE' AS analysis_section,
    CURRENT_TIMESTAMP() AS analysis_timestamp,
    tc.TABLE_SCHEMA AS schema_name,
    tc.TABLE_NAME,
    tc.CONSTRAINT_TYPE,
    COUNT(*) AS constraint_count,
    LISTAGG(tc.CONSTRAINT_NAME, ', ') WITHIN GROUP (ORDER BY tc.CONSTRAINT_NAME) AS constraint_names
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
WHERE tc.TABLE_SCHEMA IN ('DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING')
GROUP BY
    tc.TABLE_SCHEMA,
    tc.TABLE_NAME,
    tc.CONSTRAINT_TYPE
ORDER BY
    tc.TABLE_SCHEMA,
    tc.TABLE_NAME,
    tc.CONSTRAINT_TYPE;

-- =====================================================
-- SECTION 8: TASK EXECUTION STATUS (LAST 24 HOURS)
-- =====================================================
-- Monitor scheduled task performance

SELECT
    'TASK_EXECUTION' AS analysis_section,
    CURRENT_TIMESTAMP() AS analysis_timestamp,
    NAME AS task_name,
    DATABASE_NAME,
    SCHEMA_NAME,
    STATE AS task_state,
    SCHEDULE AS task_schedule,
    COUNT(*) AS execution_count,
    SUM(CASE WHEN STATE = 'SUCCEEDED' THEN 1 ELSE 0 END) AS success_count,
    SUM(CASE WHEN STATE = 'FAILED' THEN 1 ELSE 0 END) AS failure_count,
    ROUND(SUM(CASE WHEN STATE = 'SUCCEEDED' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS success_rate_pct,
    MAX(COMPLETED_TIME) AS last_execution,
    ROUND(AVG(DATEDIFF(second, SCHEDULED_TIME, COMPLETED_TIME)), 2) AS avg_duration_seconds
FROM SNOWFLAKE.ACCOUNT_USAGE.TASK_HISTORY
WHERE SCHEDULED_TIME >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
    AND DATABASE_NAME = 'ITSECKPI_DEV'
GROUP BY
    NAME,
    DATABASE_NAME,
    SCHEMA_NAME,
    STATE,
    SCHEDULE
ORDER BY
    failure_count DESC,
    execution_count DESC;

-- =====================================================
-- SECTION 9: STORAGE COSTS BY LAYER
-- =====================================================
-- Calculate storage costs per schema

SELECT
    'STORAGE_COSTS' AS analysis_section,
    CURRENT_TIMESTAMP() AS analysis_timestamp,
    TABLE_SCHEMA AS schema_name,
    COUNT(DISTINCT TABLE_NAME) AS table_count,
    SUM(ROW_COUNT) AS total_rows,
    ROUND(SUM(BYTES) / POWER(1024, 3), 2) AS total_size_gb,
    ROUND(SUM(BYTES) / POWER(1024, 4), 4) AS total_size_tb,
    ROUND((SUM(BYTES) / POWER(1024, 4)) * 23, 2) AS estimated_monthly_cost_usd,  -- $23/TB/month on-demand
    ROUND((SUM(BYTES) / POWER(1024, 4)) * 23 * 12, 2) AS estimated_annual_cost_usd
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA IN ('DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING')
GROUP BY
    TABLE_SCHEMA
ORDER BY
    total_size_gb DESC;

-- =====================================================
-- SECTION 10: ERROR SUMMARY (LAST 24 HOURS)
-- =====================================================
-- Identify and categorize query errors

SELECT
    'ERROR_SUMMARY' AS analysis_section,
    CURRENT_TIMESTAMP() AS analysis_timestamp,
    ERROR_CODE,
    ERROR_MESSAGE,
    SCHEMA_NAME,
    QUERY_TYPE,
    COUNT(*) AS error_count,
    MAX(START_TIME) AS last_occurrence,
    LISTAGG(DISTINCT USER_NAME, ', ') WITHIN GROUP (ORDER BY USER_NAME) AS affected_users
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE START_TIME >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
    AND DATABASE_NAME = 'ITSECKPI_DEV'
    AND ERROR_CODE IS NOT NULL
GROUP BY
    ERROR_CODE,
    ERROR_MESSAGE,
    SCHEMA_NAME,
    QUERY_TYPE
ORDER BY
    error_count DESC
LIMIT 20;

-- =====================================================
-- SECTION 11: MATERIALIZED VIEW REFRESH STATUS
-- =====================================================
-- Monitor materialized view freshness

SELECT
    'MATERIALIZED_VIEW_STATUS' AS analysis_section,
    CURRENT_TIMESTAMP() AS analysis_timestamp,
    TABLE_SCHEMA AS schema_name,
    TABLE_NAME AS view_name,
    IS_MATERIALIZED,
    LAST_ALTERED,
    DATEDIFF(hour, LAST_ALTERED, CURRENT_TIMESTAMP()) AS hours_since_refresh,
    ROW_COUNT,
    ROUND(BYTES / POWER(1024, 2), 2) AS size_mb,
    CASE
        WHEN DATEDIFF(hour, LAST_ALTERED, CURRENT_TIMESTAMP()) <= 24 THEN 'FRESH'
        WHEN DATEDIFF(hour, LAST_ALTERED, CURRENT_TIMESTAMP()) <= 168 THEN 'NEEDS_REFRESH'
        ELSE 'STALE'
    END AS refresh_status
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA IN ('DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING')
    AND TABLE_TYPE = 'VIEW'
    AND IS_MATERIALIZED = 'YES'
ORDER BY
    hours_since_refresh DESC;

-- =====================================================
-- SECTION 12: TOP USERS BY QUERY VOLUME
-- =====================================================
-- Identify most active users in the last 24 hours

SELECT
    'USER_ACTIVITY' AS analysis_section,
    CURRENT_TIMESTAMP() AS analysis_timestamp,
    USER_NAME,
    COUNT(*) AS query_count,
    COUNT(DISTINCT SCHEMA_NAME) AS schemas_accessed,
    ROUND(SUM(EXECUTION_TIME) / 1000 / 3600, 2) AS total_execution_hours,
    ROUND(AVG(EXECUTION_TIME) / 1000, 2) AS avg_execution_seconds,
    SUM(CASE WHEN ERROR_CODE IS NOT NULL THEN 1 ELSE 0 END) AS error_count,
    ROUND(SUM(BYTES_SCANNED) / POWER(1024, 3), 2) AS total_gb_scanned
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE START_TIME >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
    AND DATABASE_NAME = 'ITSECKPI_DEV'
    AND USER_NAME NOT IN ('SYSTEM', 'SNOWFLAKE')
GROUP BY
    USER_NAME
ORDER BY
    query_count DESC
LIMIT 20;

-- =====================================================
-- SECTION 13: SUMMARY DASHBOARD METRICS
-- =====================================================
-- High-level KPIs for daily monitoring dashboard

SELECT
    'DAILY_SUMMARY' AS analysis_section,
    CURRENT_DATE() AS analysis_date,
    CURRENT_TIMESTAMP() AS analysis_timestamp,

    -- Object Counts
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
     WHERE TABLE_SCHEMA = 'DEV_LANDING' AND TABLE_TYPE = 'BASE TABLE') AS landing_tables,
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
     WHERE TABLE_SCHEMA = 'DEV_TRANSFORMATION' AND TABLE_TYPE = 'BASE TABLE') AS transformation_tables,
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
     WHERE TABLE_SCHEMA = 'DEV_REPORTING' AND TABLE_TYPE = 'VIEW') AS reporting_views,

    -- Query Metrics (Last 24 hours)
    (SELECT COUNT(*) FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
     WHERE START_TIME >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
     AND DATABASE_NAME = 'ITSECKPI_DEV') AS total_queries_24h,

    (SELECT ROUND(AVG(EXECUTION_TIME) / 1000, 2) FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
     WHERE START_TIME >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
     AND DATABASE_NAME = 'ITSECKPI_DEV'
     AND EXECUTION_TIME IS NOT NULL) AS avg_query_time_seconds,

    (SELECT COUNT(*) FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
     WHERE START_TIME >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
     AND DATABASE_NAME = 'ITSECKPI_DEV'
     AND ERROR_CODE IS NOT NULL) AS error_count_24h,

    -- Storage Metrics
    (SELECT ROUND(SUM(BYTES) / POWER(1024, 3), 2) FROM INFORMATION_SCHEMA.TABLES
     WHERE TABLE_SCHEMA IN ('DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING')) AS total_storage_gb,

    -- Task Status
    (SELECT COUNT(DISTINCT NAME) FROM SNOWFLAKE.ACCOUNT_USAGE.TASK_HISTORY
     WHERE SCHEDULED_TIME >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
     AND DATABASE_NAME = 'ITSECKPI_DEV'
     AND STATE = 'SUCCEEDED') AS successful_tasks_24h,

    (SELECT COUNT(DISTINCT NAME) FROM SNOWFLAKE.ACCOUNT_USAGE.TASK_HISTORY
     WHERE SCHEDULED_TIME >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
     AND DATABASE_NAME = 'ITSECKPI_DEV'
     AND STATE = 'FAILED') AS failed_tasks_24h;

-- =====================================================
-- END OF ANALYSIS SCRIPT
-- =====================================================
-- Note: Results can be exported to JSON or CSV format
-- Run this script daily and analyze trends over time
-- =====================================================
