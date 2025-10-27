/*
================================================================================
Get Main Table Columns - For Streamlit Apps
================================================================================

Execute each query and share the column list results.

Date: 2025-10-24
================================================================================
*/

USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;

-- ============================================================================
-- 1. SENTINELONE - FACT_SENTINEL_ENDPOINTS (Main table - 4,188 rows)
-- ============================================================================

SELECT
    COLUMN_NAME,
    DATA_TYPE,
    ORDINAL_POSITION
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE TABLE_NAME = 'FACT_SENTINEL_ENDPOINTS'
ORDER BY ORDINAL_POSITION;

-- ✅ Share these results

-- ============================================================================
-- 2. SENTINELONE - DIM_SENTINEL_VERSIONS (Lookup table - 38 rows)
-- ============================================================================

SELECT
    COLUMN_NAME,
    DATA_TYPE,
    ORDINAL_POSITION
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE TABLE_NAME = 'DIM_SENTINEL_VERSIONS'
ORDER BY ORDINAL_POSITION;

-- ✅ Share these results

-- ============================================================================
-- 3. CYBELANGEL - DIM_CYBELANGEL_ALERTS (Main table - 196 rows)
-- ============================================================================

SELECT
    COLUMN_NAME,
    DATA_TYPE,
    ORDINAL_POSITION
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE TABLE_NAME = 'DIM_CYBELANGEL_ALERTS'
ORDER BY ORDINAL_POSITION;

-- ✅ Share these results

-- ============================================================================
-- 4. PROOFPOINT - PROOFPOINT_MESSAGE_LOGS (Main table - 206,794 rows)
-- ============================================================================

SELECT
    COLUMN_NAME,
    DATA_TYPE,
    ORDINAL_POSITION
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE TABLE_NAME = 'PROOFPOINT_MESSAGE_LOGS'
ORDER BY ORDINAL_POSITION;

-- ✅ Share these results

-- ============================================================================
-- 5. SERVICENOW - SNOW (Main table - 24,650 rows)
-- ============================================================================

SELECT
    COLUMN_NAME,
    DATA_TYPE,
    ORDINAL_POSITION
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE TABLE_NAME = 'SNOW'
ORDER BY ORDINAL_POSITION;

-- ✅ Share these results

-- ============================================================================
-- 6. LEVIAT - DIM_LEVIAT_USERS (Main table - 0 rows)
-- ============================================================================

SELECT
    COLUMN_NAME,
    DATA_TYPE,
    ORDINAL_POSITION
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE TABLE_NAME = 'DIM_LEVIAT_USERS'
ORDER BY ORDINAL_POSITION;

-- ✅ Share these results

-- ============================================================================
-- 7. LEVIAT - FACT_LEVIAT_SECURITY_EVENTS (Main table - 0 rows)
-- ============================================================================

SELECT
    COLUMN_NAME,
    DATA_TYPE,
    ORDINAL_POSITION
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE TABLE_NAME = 'FACT_LEVIAT_SECURITY_EVENTS'
ORDER BY ORDINAL_POSITION;

-- ✅ Share these results
