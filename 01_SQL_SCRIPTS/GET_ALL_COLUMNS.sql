/*
================================================================================
Get All Columns for Each Service - Execute and Share Results
================================================================================

Execute each query and share the results with me so I can update the apps.

Date: 2025-10-24
================================================================================
*/

USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;

-- ============================================================================
-- QUERY 1: SentinelOne Columns (2 tables)
-- ============================================================================

SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    ORDINAL_POSITION
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME = 'SentinelOne'
ORDER BY TABLE_NAME, ORDINAL_POSITION;

-- ✅ Copy and paste the results after executing this query

-- ============================================================================
-- QUERY 2: CybelAngel Columns
-- ============================================================================

SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    ORDINAL_POSITION
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME = 'CybelAngel'
ORDER BY TABLE_NAME, ORDINAL_POSITION;

-- ✅ Copy and paste the results after executing this query

-- ============================================================================
-- QUERY 3: Proofpoint Columns
-- ============================================================================

SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    ORDINAL_POSITION
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME = 'Proofpoint'
ORDER BY TABLE_NAME, ORDINAL_POSITION;

-- ✅ Copy and paste the results after executing this query

-- ============================================================================
-- QUERY 4: ServiceNow Columns
-- ============================================================================

SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    ORDINAL_POSITION
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME = 'ServiceNow'
ORDER BY TABLE_NAME, ORDINAL_POSITION;

-- ✅ Copy and paste the results after executing this query

-- ============================================================================
-- QUERY 5: Leviat Columns (empty tables but structure exists)
-- ============================================================================

SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    ORDINAL_POSITION
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME = 'Leviat'
ORDER BY TABLE_NAME, ORDINAL_POSITION;

-- ✅ Copy and paste the results after executing this query

-- ============================================================================
-- SUMMARY QUERY: All Services Overview
-- ============================================================================

SELECT
    SERVICE_NAME,
    TABLE_NAME,
    COUNT(DISTINCT COLUMN_NAME) as COLUMN_COUNT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
GROUP BY SERVICE_NAME, TABLE_NAME
ORDER BY SERVICE_NAME, TABLE_NAME;

-- ✅ This gives us a quick overview of all services
