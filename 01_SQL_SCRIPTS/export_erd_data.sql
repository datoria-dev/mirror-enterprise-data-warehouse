-- ============================================
-- Export ERD Data for Wiki Visualization
-- ============================================
-- Purpose: Export ERD data to create visualizations for Data Model wiki
-- Date: 2025-10-24
-- ============================================

USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA METADATA;

-- Export 1: Service Summary
SELECT
    SERVICE_NAME,
    TABLE_COUNT,
    COLUMN_COUNT,
    TOTAL_ROWS,
    SERVICE_COLOR
FROM VW_ERD_BY_SERVICE
ORDER BY TABLE_COUNT DESC;

-- Export 2: Top 10 Largest Tables
SELECT
    SERVICE_NAME,
    TABLE_NAME,
    FULL_TABLE_NAME,
    DATA_LAYER,
    ROW_COUNT,
    COLUMN_COUNT
FROM VW_ERD_TABLE_CATALOG
WHERE ROW_COUNT > 0
ORDER BY ROW_COUNT DESC
LIMIT 10;

-- Export 3: SentinelOne ERD Data
SELECT
    SERVICE_NAME,
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    KEY_INDICATOR,
    ORDINAL_POSITION
FROM VW_ERD_COMPLETE_EXPORT
WHERE SERVICE_NAME = 'SentinelOne'
ORDER BY TABLE_NAME, ORDINAL_POSITION;

-- Export 4: CrowdStrike ERD Data
SELECT
    SERVICE_NAME,
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    KEY_INDICATOR,
    ORDINAL_POSITION
FROM VW_ERD_COMPLETE_EXPORT
WHERE SERVICE_NAME = 'CrowdStrike'
ORDER BY TABLE_NAME, ORDINAL_POSITION;

-- Export 5: Metadata Repository Structure
SELECT
    TABLE_NAME,
    DESCRIPTION,
    ROW_COUNT,
    COLUMN_COUNT
FROM VW_ERD_METADATA_REPOSITORY;
