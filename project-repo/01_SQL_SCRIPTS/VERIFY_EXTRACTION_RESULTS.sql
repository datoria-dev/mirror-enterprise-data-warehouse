/*
================================================================================
Verify Metadata Extraction Results
================================================================================

Quick verification queries to check extraction success
Run after executing EXECUTE_METADATA_EXTRACTION.sql

================================================================================
*/

USE ROLE SECURITY_ANALYTICS;
USE WAREHOUSE DEV_WH;
USE SCHEMA DEV_TRANSFORMATION.SAMPLES;

-- ============================================================================
-- Check 1: Verify Schema Exists
-- ============================================================================

SHOW SCHEMAS LIKE 'SAMPLES' IN DATABASE DEV_TRANSFORMATION;

-- ============================================================================
-- Check 2: List All Created Views
-- ============================================================================

SHOW VIEWS IN SCHEMA DEV_TRANSFORMATION.SAMPLES;

-- ============================================================================
-- Check 3: Metadata Extraction Summary
-- ============================================================================

SELECT
    'Metadata View' as OBJECT_TYPE,
    'VW_ALL_TABLE_METADATA' as VIEW_NAME,
    COUNT(*) as TOTAL_ROWS
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
UNION ALL
SELECT
    'Summary View',
    'VW_SERVICE_SUMMARY',
    COUNT(*)
FROM DEV_TRANSFORMATION.SAMPLES.VW_SERVICE_SUMMARY
UNION ALL
SELECT
    'Profile View',
    'VW_TABLE_PROFILE_REPORT',
    COUNT(*)
FROM DEV_TRANSFORMATION.SAMPLES.VW_TABLE_PROFILE_REPORT;

-- ============================================================================
-- Check 4: Services Detected
-- ============================================================================

SELECT
    SERVICE_NAME,
    COUNT(DISTINCT TABLE_NAME) as TABLES,
    SUM(TOTAL_ROWS) as TOTAL_ROWS,
    SUM(TOTAL_SIZE_GB) as SIZE_GB
FROM DEV_TRANSFORMATION.SAMPLES.VW_SERVICE_SUMMARY
GROUP BY SERVICE_NAME
ORDER BY SERVICE_NAME;

-- ============================================================================
-- Check 5: NEW Services Data Availability
-- ============================================================================

SELECT
    'SentinelOne' as SERVICE,
    'FACT_SENTINEL_ENDPOINTS' as TABLE_NAME,
    (SELECT COUNT(*) FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINELONE_ENDPOINTS) as SAMPLE_ROWS,
    (SELECT MAX(ROW_COUNT) FROM DEV_TRANSFORMATION.SAMPLES.VW_TABLE_PROFILE_REPORT
     WHERE TABLE_NAME = 'FACT_SENTINEL_ENDPOINTS') as TOTAL_ROWS

UNION ALL

SELECT
    'Tenable',
    'FACT_TENABLE',
    (SELECT COUNT(*) FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_TENABLE_FACT),
    (SELECT MAX(ROW_COUNT) FROM DEV_TRANSFORMATION.SAMPLES.VW_TABLE_PROFILE_REPORT
     WHERE TABLE_NAME = 'FACT_TENABLE')

UNION ALL

SELECT
    'CybelAngel',
    'FACT_CYBELANGEL_THREATS',
    (SELECT COUNT(*) FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_THREATS),
    (SELECT MAX(ROW_COUNT) FROM DEV_TRANSFORMATION.SAMPLES.VW_TABLE_PROFILE_REPORT
     WHERE TABLE_NAME = 'FACT_CYBELANGEL_THREATS')

UNION ALL

SELECT
    'Leviat',
    'DIM_LEVIAT_USERS',
    (SELECT COUNT(*) FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_USERS),
    (SELECT MAX(ROW_COUNT) FROM DEV_TRANSFORMATION.SAMPLES.VW_TABLE_PROFILE_REPORT
     WHERE TABLE_NAME = 'DIM_LEVIAT_USERS')

UNION ALL

SELECT
    'ServiceNow',
    'DIM_SNOW_INCIDENT',
    (SELECT COUNT(*) FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SNOW_INCIDENT),
    (SELECT MAX(ROW_COUNT) FROM DEV_TRANSFORMATION.SAMPLES.VW_TABLE_PROFILE_REPORT
     WHERE TABLE_NAME = 'DIM_SNOW_INCIDENT')

UNION ALL

SELECT
    'Proofpoint',
    'L_PROOFPOINT_RAW',
    (SELECT COUNT(*) FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_PROOFPOINT_RAW),
    (SELECT MAX(ROW_COUNT) FROM DEV_TRANSFORMATION.SAMPLES.VW_TABLE_PROFILE_REPORT
     WHERE TABLE_NAME = 'L_PROOFPOINT_RAW');

-- ============================================================================
-- Check 6: Sample Data Preview
-- ============================================================================

-- SentinelOne - First 3 rows
SELECT 'SentinelOne' as SERVICE, * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINELONE_ENDPOINTS LIMIT 3;

-- Tenable - First 3 rows
SELECT 'Tenable' as SERVICE, * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_TENABLE_FACT LIMIT 3;

-- CybelAngel - First 3 rows
SELECT 'CybelAngel' as SERVICE, * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_THREATS LIMIT 3;

-- ============================================================================
-- Check 7: Column Details for Key Tables
-- ============================================================================

-- SentinelOne columns
SELECT
    'SentinelOne - FACT_SENTINEL_ENDPOINTS' as TABLE_INFO,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE TABLE_NAME = 'FACT_SENTINEL_ENDPOINTS'
ORDER BY ORDINAL_POSITION
LIMIT 10;

-- Tenable columns
SELECT
    'Tenable - FACT_TENABLE' as TABLE_INFO,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE TABLE_NAME = 'FACT_TENABLE'
ORDER BY ORDINAL_POSITION
LIMIT 10;

-- ============================================================================
-- Check 8: Extraction Status Summary
-- ============================================================================

SELECT
    '================================' as SEPARATOR
UNION ALL
SELECT
    'METADATA EXTRACTION VERIFICATION'
UNION ALL
SELECT
    '================================'
UNION ALL
SELECT
    CONCAT('Total Services: ', COUNT(DISTINCT SERVICE_NAME))
FROM DEV_TRANSFORMATION.SAMPLES.VW_SERVICE_SUMMARY
UNION ALL
SELECT
    CONCAT('Total Tables: ', COUNT(DISTINCT TABLE_NAME))
FROM DEV_TRANSFORMATION.SAMPLES.VW_TABLE_PROFILE_REPORT
UNION ALL
SELECT
    CONCAT('Total Columns: ', COUNT(*))
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
UNION ALL
SELECT
    CONCAT('Sample Views: ', COUNT(*))
FROM INFORMATION_SCHEMA.VIEWS
WHERE TABLE_SCHEMA = 'SAMPLES' AND TABLE_NAME LIKE 'VW_SAMPLE%'
UNION ALL
SELECT
    '================================'
UNION ALL
SELECT
    '✓ Extraction Complete!';

/*
================================================================================
INTERPRETATION
================================================================================

If all checks pass:
- ✅ Schema SAMPLES exists
- ✅ 3+ metadata views created (VW_ALL_TABLE_METADATA, VW_SERVICE_SUMMARY, VW_TABLE_PROFILE_REPORT)
- ✅ 6+ sample views created (one per service)
- ✅ Services detected with row counts
- ✅ Sample data available (or 0 rows for empty tables like Leviat)

Next Steps:
1. Download CSVs from STEP 8 in EXECUTE_METADATA_EXTRACTION.sql
2. Use metadata to build/update Streamlit apps
3. Reference actual column names and data types

If any check fails:
- Rerun EXECUTE_METADATA_EXTRACTION.sql
- Check permissions (SECURITY_ANALYTICS role)
- Verify tables exist in DEV_TRANSFORMATION.SECURITY_ANALYTICS

================================================================================
*/
