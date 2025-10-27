/*
================================================================================
Discover Actual Tables in SECURITY_ANALYTICS Schemas
================================================================================

This script discovers what tables actually exist before extracting metadata.
Run this FIRST to see what tables are available.

================================================================================
*/

-- Use correct role
USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;

-- ============================================================================
-- Step 1: Discover Tables in DEV_LANDING
-- ============================================================================

SELECT
    TABLE_CATALOG as DATABASE,
    TABLE_SCHEMA as SCHEMA,
    TABLE_NAME,
    TABLE_TYPE,
    ROW_COUNT,
    ROUND(BYTES / 1024 / 1024, 2) as SIZE_MB,
    CREATED,
    LAST_ALTERED
FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND TABLE_TYPE IN ('BASE TABLE', 'VIEW')
ORDER BY TABLE_NAME;

-- ============================================================================
-- Step 2: Discover Tables in DEV_TRANSFORMATION
-- ============================================================================

SELECT
    TABLE_CATALOG as DATABASE,
    TABLE_SCHEMA as SCHEMA,
    TABLE_NAME,
    TABLE_TYPE,
    ROW_COUNT,
    ROUND(BYTES / 1024 / 1024, 2) as SIZE_MB,
    CREATED,
    LAST_ALTERED
FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND TABLE_TYPE IN ('BASE TABLE', 'VIEW')
ORDER BY TABLE_NAME;

-- ============================================================================
-- Step 3: Filter by Service Keywords
-- ============================================================================

-- SentinelOne tables
SELECT 'SentinelOne' as SERVICE, TABLE_CATALOG, TABLE_NAME, ROW_COUNT
FROM (
    SELECT TABLE_CATALOG, TABLE_NAME, ROW_COUNT
    FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
    UNION ALL
    SELECT TABLE_CATALOG, TABLE_NAME, ROW_COUNT
    FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
)
WHERE TABLE_NAME LIKE '%SENTINEL%'
ORDER BY TABLE_NAME;

-- Tenable tables
SELECT 'Tenable' as SERVICE, TABLE_CATALOG, TABLE_NAME, ROW_COUNT
FROM (
    SELECT TABLE_CATALOG, TABLE_NAME, ROW_COUNT
    FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
    UNION ALL
    SELECT TABLE_CATALOG, TABLE_NAME, ROW_COUNT
    FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
)
WHERE TABLE_NAME LIKE '%TENABLE%'
ORDER BY TABLE_NAME;

-- CybelAngel tables
SELECT 'CybelAngel' as SERVICE, TABLE_CATALOG, TABLE_NAME, ROW_COUNT
FROM (
    SELECT TABLE_CATALOG, TABLE_NAME, ROW_COUNT
    FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
    UNION ALL
    SELECT TABLE_CATALOG, TABLE_NAME, ROW_COUNT
    FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
)
WHERE TABLE_NAME LIKE '%CYBELANGEL%'
ORDER BY TABLE_NAME;

-- Leviat tables
SELECT 'Leviat' as SERVICE, TABLE_CATALOG, TABLE_NAME, ROW_COUNT
FROM (
    SELECT TABLE_CATALOG, TABLE_NAME, ROW_COUNT
    FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
    UNION ALL
    SELECT TABLE_CATALOG, TABLE_NAME, ROW_COUNT
    FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
)
WHERE TABLE_NAME LIKE '%LEVIAT%'
ORDER BY TABLE_NAME;

-- ServiceNow tables
SELECT 'ServiceNow' as SERVICE, TABLE_CATALOG, TABLE_NAME, ROW_COUNT
FROM (
    SELECT TABLE_CATALOG, TABLE_NAME, ROW_COUNT
    FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
    UNION ALL
    SELECT TABLE_CATALOG, TABLE_NAME, ROW_COUNT
    FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
)
WHERE TABLE_NAME LIKE '%SNOW%'
ORDER BY TABLE_NAME;

-- Proofpoint tables
SELECT 'Proofpoint' as SERVICE, TABLE_CATALOG, TABLE_NAME, ROW_COUNT
FROM (
    SELECT TABLE_CATALOG, TABLE_NAME, ROW_COUNT
    FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
    UNION ALL
    SELECT TABLE_CATALOG, TABLE_NAME, ROW_COUNT
    FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
)
WHERE TABLE_NAME LIKE '%PROOFPOINT%'
ORDER BY TABLE_NAME;

-- ============================================================================
-- Step 4: All Tables Summary by Keyword
-- ============================================================================

SELECT
    CASE
        WHEN TABLE_NAME LIKE '%SENTINEL%' THEN 'SentinelOne'
        WHEN TABLE_NAME LIKE '%TENABLE%' THEN 'Tenable'
        WHEN TABLE_NAME LIKE '%CYBELANGEL%' THEN 'CybelAngel'
        WHEN TABLE_NAME LIKE '%LEVIAT%' THEN 'Leviat'
        WHEN TABLE_NAME LIKE '%SNOW%' THEN 'ServiceNow'
        WHEN TABLE_NAME LIKE '%PROOFPOINT%' THEN 'Proofpoint'
        WHEN TABLE_NAME LIKE '%CROWDSTRIKE%' OR TABLE_NAME LIKE '%EDR%' THEN 'CrowdStrike'
        WHEN TABLE_NAME LIKE '%QUALYS%' THEN 'Qualys'
        WHEN TABLE_NAME LIKE '%BITSIGHT%' THEN 'BitSight'
        WHEN TABLE_NAME LIKE '%ZEROFOX%' THEN 'ZeroFox'
        WHEN TABLE_NAME LIKE '%SPLUNK%' THEN 'Splunk'
        WHEN TABLE_NAME LIKE '%SOPHOS%' THEN 'Sophos'
        WHEN TABLE_NAME LIKE '%SYMANTEC%' THEN 'Symantec'
        WHEN TABLE_NAME LIKE '%TRELLIX%' THEN 'Trellix'
        WHEN TABLE_NAME LIKE '%ANCON%' THEN 'Ancon'
        ELSE 'Other'
    END as SERVICE_NAME,
    TABLE_CATALOG as DATABASE,
    TABLE_NAME,
    ROW_COUNT,
    ROUND(BYTES / 1024 / 1024, 2) as SIZE_MB
FROM (
    SELECT TABLE_CATALOG, TABLE_NAME, ROW_COUNT, BYTES
    FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
    UNION ALL
    SELECT TABLE_CATALOG, TABLE_NAME, ROW_COUNT, BYTES
    FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
)
WHERE SERVICE_NAME IN ('SentinelOne', 'Tenable', 'CybelAngel', 'Leviat', 'ServiceNow', 'Proofpoint')
ORDER BY SERVICE_NAME, DATABASE, TABLE_NAME;

/*
================================================================================
NEXT STEPS
================================================================================

After running this script:

1. Review the results to see which tables actually exist
2. Note the exact table names (they might be different from expected)
3. Copy the actual table names
4. We'll create a corrected version of EXECUTE_METADATA_EXTRACTION.sql
   with the real table names

Expected vs Actual:
-------------------
Expected: FACT_TENABLE
Actual:   ? (check results above)

Expected: FACT_SENTINEL_ENDPOINTS
Actual:   ? (check results above)

Expected: FACT_CYBELANGEL_THREATS
Actual:   ? (check results above)

================================================================================
*/
