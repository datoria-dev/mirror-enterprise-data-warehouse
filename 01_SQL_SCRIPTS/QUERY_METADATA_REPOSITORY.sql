/*
================================================================================
Query Metadata Repository - Helper Queries
================================================================================

Useful queries to explore and use the metadata repository for building
Streamlit apps, dashboards, and documentation.

Date: 2025-10-24
================================================================================
*/

USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;
USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA METADATA;

-- ============================================================================
-- QUICK REFERENCE QUERIES
-- ============================================================================

-- -----------------------------------------------------------------------------
-- Q1: Get all columns for a specific table (for Streamlit app development)
-- -----------------------------------------------------------------------------

SELECT
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    COLUMN_COMMENT
FROM VW_COLUMN_CATALOG
WHERE SERVICE_NAME = 'SentinelOne'          -- Change service name
  AND TABLE_NAME = 'FACT_SENTINEL_ENDPOINTS' -- Change table name
ORDER BY ORDINAL_POSITION;

-- -----------------------------------------------------------------------------
-- Q2: Get all tables for a service with statistics
-- -----------------------------------------------------------------------------

SELECT
    TABLE_NAME,
    DATA_LAYER,
    TABLE_TYPE,
    ROW_COUNT,
    COLUMN_COUNT,
    LAST_UPDATED
FROM VW_TABLE_CATALOG
WHERE SERVICE_NAME = 'Proofpoint'  -- Change service name
ORDER BY ROW_COUNT DESC NULLS LAST;

-- -----------------------------------------------------------------------------
-- Q3: Service overview - all services summary
-- -----------------------------------------------------------------------------

SELECT
    SERVICE_NAME,
    SERVICE_CATEGORY,
    TABLE_COUNT,
    TOTAL_ROWS,
    TOTAL_COLUMNS,
    LAST_DATA_UPDATE,
    REFRESH_FREQUENCY,
    IS_ACTIVE
FROM VW_SERVICE_SUMMARY
ORDER BY SERVICE_NAME;

-- -----------------------------------------------------------------------------
-- Q4: Find tables containing a specific column name
-- -----------------------------------------------------------------------------

SELECT DISTINCT
    SERVICE_NAME,
    TABLE_NAME,
    DATA_LAYER,
    COLUMN_NAME,
    DATA_TYPE
FROM VW_COLUMN_CATALOG
WHERE COLUMN_NAME LIKE '%EMAIL%'  -- Change search term
ORDER BY SERVICE_NAME, TABLE_NAME;

-- -----------------------------------------------------------------------------
-- Q5: Get full table definition (CREATE TABLE equivalent)
-- -----------------------------------------------------------------------------

SELECT
    SERVICE_NAME,
    DATABASE_NAME || '.' || SCHEMA_NAME || '.' || TABLE_NAME as FULL_TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION
FROM VW_COLUMN_CATALOG
WHERE TABLE_NAME = 'PROOFPOINT_MESSAGE_LOGS'  -- Change table name
ORDER BY ORDINAL_POSITION;

-- ============================================================================
-- STREAMLIT APP DEVELOPMENT QUERIES
-- ============================================================================

-- -----------------------------------------------------------------------------
-- Q6: Generate SQL column list for SELECT statement
-- -----------------------------------------------------------------------------

SELECT
    'SELECT\n' ||
    LISTAGG(
        '    ' || COLUMN_NAME,
        ',\n'
    ) WITHIN GROUP (ORDER BY ORDINAL_POSITION) ||
    '\nFROM ' || MAX(DATABASE_NAME || '.' || SCHEMA_NAME || '.' || TABLE_NAME) as SQL_TEMPLATE
FROM VW_COLUMN_CATALOG
WHERE TABLE_NAME = 'SNOW';  -- Change table name

-- -----------------------------------------------------------------------------
-- Q7: Get columns by data type (useful for filter building)
-- -----------------------------------------------------------------------------

SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE
FROM VW_COLUMN_CATALOG
WHERE SERVICE_NAME = 'ServiceNow'
  AND DATA_TYPE IN ('DATE', 'TIMESTAMP_NTZ', 'TIMESTAMP_LTZ')  -- Date/Time columns
ORDER BY TABLE_NAME, ORDINAL_POSITION;

-- -----------------------------------------------------------------------------
-- Q8: Get all TEXT columns (for search/filter functionality)
-- -----------------------------------------------------------------------------

SELECT
    TABLE_NAME,
    COLUMN_NAME,
    ORDINAL_POSITION
FROM VW_COLUMN_CATALOG
WHERE SERVICE_NAME = 'CybelAngel'
  AND DATA_TYPE = 'TEXT'
ORDER BY TABLE_NAME, ORDINAL_POSITION;

-- -----------------------------------------------------------------------------
-- Q9: Get NUMBER/BOOLEAN columns (for metrics and aggregations)
-- -----------------------------------------------------------------------------

SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE
FROM VW_COLUMN_CATALOG
WHERE SERVICE_NAME = 'ServiceNow'
  AND DATA_TYPE IN ('NUMBER', 'BOOLEAN')
ORDER BY TABLE_NAME, COLUMN_NAME;

-- ============================================================================
-- DATA QUALITY & MONITORING QUERIES
-- ============================================================================

-- -----------------------------------------------------------------------------
-- Q10: Check for tables with no recent updates
-- -----------------------------------------------------------------------------

SELECT
    SERVICE_NAME,
    TABLE_NAME,
    ROW_COUNT,
    LAST_UPDATED,
    DATEDIFF(day, LAST_UPDATED, CURRENT_TIMESTAMP()) as DAYS_STALE
FROM VW_TABLE_CATALOG
WHERE IS_ACTIVE = TRUE
  AND LAST_UPDATED IS NOT NULL
  AND DATEDIFF(day, LAST_UPDATED, CURRENT_TIMESTAMP()) > 7  -- More than 7 days old
ORDER BY DAYS_STALE DESC;

-- -----------------------------------------------------------------------------
-- Q11: Find empty tables
-- -----------------------------------------------------------------------------

SELECT
    SERVICE_NAME,
    TABLE_NAME,
    DATA_LAYER,
    COLUMN_COUNT,
    CREATED_DATE
FROM VW_TABLE_CATALOG
WHERE ROW_COUNT = 0 OR ROW_COUNT IS NULL
ORDER BY SERVICE_NAME, TABLE_NAME;

-- -----------------------------------------------------------------------------
-- Q12: Row count trends (historical data)
-- -----------------------------------------------------------------------------

SELECT
    tr.SERVICE_NAME,
    tr.TABLE_NAME,
    ts.SNAPSHOT_DATE,
    ts.ROW_COUNT,
    LAG(ts.ROW_COUNT) OVER (PARTITION BY tr.TABLE_NAME ORDER BY ts.SNAPSHOT_DATE) as PREV_ROW_COUNT,
    ts.ROW_COUNT - LAG(ts.ROW_COUNT) OVER (PARTITION BY tr.TABLE_NAME ORDER BY ts.SNAPSHOT_DATE) as ROW_CHANGE
FROM TABLE_STATISTICS ts
JOIN TABLE_REGISTRY tr ON ts.TABLE_ID = tr.TABLE_ID
WHERE tr.SERVICE_NAME = 'Proofpoint'  -- Change service
ORDER BY tr.TABLE_NAME, ts.SNAPSHOT_DATE DESC;

-- ============================================================================
-- DOCUMENTATION GENERATION QUERIES
-- ============================================================================

-- -----------------------------------------------------------------------------
-- Q13: Generate Markdown table documentation
-- -----------------------------------------------------------------------------

SELECT
    '| ' || COLUMN_NAME ||
    ' | ' || DATA_TYPE ||
    ' | ' || IS_NULLABLE ||
    ' | ' || COALESCE(COLUMN_COMMENT, '') ||
    ' |' as MARKDOWN_ROW
FROM VW_COLUMN_CATALOG
WHERE TABLE_NAME = 'DIM_CYBELANGEL_ALERTS'
ORDER BY ORDINAL_POSITION;

-- Copy results and paste with this header:
-- | Column Name | Data Type | Nullable | Description |
-- |-------------|-----------|----------|-------------|

-- -----------------------------------------------------------------------------
-- Q14: Generate data dictionary for all services
-- -----------------------------------------------------------------------------

SELECT
    SERVICE_NAME,
    TABLE_NAME,
    DATA_LAYER,
    COUNT(DISTINCT COLUMN_NAME) as COLUMNS,
    LISTAGG(DISTINCT DATA_TYPE, ', ') WITHIN GROUP (ORDER BY DATA_TYPE) as DATA_TYPES_USED
FROM VW_COLUMN_CATALOG
GROUP BY SERVICE_NAME, TABLE_NAME, DATA_LAYER
ORDER BY SERVICE_NAME, TABLE_NAME;

-- ============================================================================
-- ADVANCED QUERIES
-- ============================================================================

-- -----------------------------------------------------------------------------
-- Q15: Find potential JOIN keys (columns with same names across tables)
-- -----------------------------------------------------------------------------

SELECT
    c1.TABLE_NAME as TABLE_1,
    c2.TABLE_NAME as TABLE_2,
    c1.COLUMN_NAME as COMMON_COLUMN,
    c1.DATA_TYPE as TYPE_1,
    c2.DATA_TYPE as TYPE_2
FROM VW_COLUMN_CATALOG c1
JOIN VW_COLUMN_CATALOG c2
    ON c1.COLUMN_NAME = c2.COLUMN_NAME
    AND c1.TABLE_NAME < c2.TABLE_NAME
WHERE c1.SERVICE_NAME = 'SentinelOne'  -- Change service
  AND c2.SERVICE_NAME = 'SentinelOne'
ORDER BY c1.COLUMN_NAME, c1.TABLE_NAME, c2.TABLE_NAME;

-- -----------------------------------------------------------------------------
-- Q16: Generate Python code for Streamlit query
-- -----------------------------------------------------------------------------

WITH columns AS (
    SELECT
        COLUMN_NAME,
        DATA_TYPE,
        ORDINAL_POSITION
    FROM VW_COLUMN_CATALOG
    WHERE TABLE_NAME = 'FACT_SENTINEL_ENDPOINTS'
    ORDER BY ORDINAL_POSITION
)
SELECT
    '# Query for ' || MAX(TABLE_NAME) || '\n' ||
    'query = """\n' ||
    'SELECT\n' ||
    LISTAGG(
        '    ' || COLUMN_NAME ||
        CASE
            WHEN DATA_TYPE IN ('DATE', 'TIMESTAMP_NTZ', 'TIMESTAMP_LTZ')
            THEN '  -- ' || DATA_TYPE
            ELSE ''
        END,
        ',\n'
    ) WITHIN GROUP (ORDER BY ORDINAL_POSITION) ||
    '\nFROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.' || MAX(TABLE_NAME) ||
    '\nLIMIT 1000\n"""' as PYTHON_CODE
FROM columns
CROSS JOIN (SELECT 'FACT_SENTINEL_ENDPOINTS' as TABLE_NAME);

-- -----------------------------------------------------------------------------
-- Q17: Compare schemas across environments (if you have PROD)
-- -----------------------------------------------------------------------------

-- This query would compare DEV vs PROD table structures
-- Useful when promoting changes between environments

SELECT
    SERVICE_NAME,
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    'DEV_TRANSFORMATION' as ENVIRONMENT
FROM VW_COLUMN_CATALOG
WHERE TABLE_NAME = 'SNOW';

-- In production, run the same query against PROD_TRANSFORMATION.METADATA

-- ============================================================================
-- EXPORT QUERIES (For CSV/JSON export)
-- ============================================================================

-- -----------------------------------------------------------------------------
-- Q18: Export complete metadata for a service (for JSON file)
-- -----------------------------------------------------------------------------

SELECT
    SERVICE_NAME,
    TABLE_NAME,
    OBJECT_AGG(
        COLUMN_NAME,
        OBJECT_CONSTRUCT(
            'data_type', DATA_TYPE,
            'nullable', IS_NULLABLE,
            'position', ORDINAL_POSITION,
            'comment', COLUMN_COMMENT
        )
    ) as COLUMNS
FROM VW_COLUMN_CATALOG
WHERE SERVICE_NAME = 'Proofpoint'
GROUP BY SERVICE_NAME, TABLE_NAME;

-- ============================================================================
-- MAINTENANCE QUERIES
-- ============================================================================

-- -----------------------------------------------------------------------------
-- Q19: Refresh metadata manually
-- -----------------------------------------------------------------------------

CALL SP_REFRESH_METADATA();

-- -----------------------------------------------------------------------------
-- Q20: Check when metadata was last refreshed
-- -----------------------------------------------------------------------------

SELECT
    MAX(CREATED_DATE) as LAST_METADATA_REFRESH,
    COUNT(DISTINCT TABLE_ID) as TABLES_TRACKED,
    COUNT(*) as TOTAL_COLUMNS
FROM COLUMN_METADATA;

-- -----------------------------------------------------------------------------
-- Q21: View task execution history
-- -----------------------------------------------------------------------------

SELECT
    NAME,
    STATE,
    SCHEDULED_TIME,
    COMPLETED_TIME,
    RETURN_VALUE
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    TASK_NAME => 'TASK_DAILY_METADATA_REFRESH'
))
ORDER BY SCHEDULED_TIME DESC
LIMIT 10;

-- ============================================================================
-- QUICK COPY-PASTE TEMPLATES
-- ============================================================================

/*
-- Template 1: Get columns for Streamlit app
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, ORDINAL_POSITION
FROM VW_COLUMN_CATALOG
WHERE SERVICE_NAME = '___SERVICE___'
  AND TABLE_NAME = '___TABLE___'
ORDER BY ORDINAL_POSITION;

-- Template 2: Build SELECT statement
SELECT LISTAGG('    ' || COLUMN_NAME, ',\n') WITHIN GROUP (ORDER BY ORDINAL_POSITION)
FROM VW_COLUMN_CATALOG
WHERE TABLE_NAME = '___TABLE___';

-- Template 3: Get all tables for service
SELECT TABLE_NAME, ROW_COUNT, COLUMN_COUNT, LAST_UPDATED
FROM VW_TABLE_CATALOG
WHERE SERVICE_NAME = '___SERVICE___'
ORDER BY TABLE_NAME;

-- Template 4: Check data freshness
SELECT SERVICE_NAME, TABLE_NAME, LAST_UPDATED,
       DATEDIFF(day, LAST_UPDATED, CURRENT_TIMESTAMP()) as DAYS_OLD
FROM VW_TABLE_CATALOG
WHERE IS_ACTIVE = TRUE
ORDER BY DAYS_OLD DESC;
*/
