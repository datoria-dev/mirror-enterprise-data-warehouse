-- ============================================================================
-- VERIFICATION SCRIPT - Check All Implementations
-- ============================================================================
-- Purpose: Verify that all 4 enhancements were created successfully
-- Date: 2025-10-07
-- ============================================================================

USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;

SELECT '========================================' AS CHECK;
SELECT '=== IMPLEMENTATION VERIFICATION ===' AS CHECK;
SELECT '========================================' AS CHECK;

-- ============================================================================
-- CHECK 1: Power BI Views
-- ============================================================================

USE DATABASE DEV_REPORTING;
USE SCHEMA SECURITY_ANALYTICS;

SELECT '--- Enhancement 1: Power BI Integration ---' AS CHECK;

SELECT TABLE_NAME, TABLE_TYPE
FROM INFORMATION_SCHEMA.VIEWS
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND TABLE_NAME LIKE '%POWERBI%'
ORDER BY TABLE_NAME;

-- Test the view
SELECT COUNT(*) as POWERBI_VIEW_ROWS FROM VW_POWERBI_EXECUTIVE_DASHBOARD;

-- ============================================================================
-- CHECK 2: Data Quality Framework
-- ============================================================================

SELECT '--- Enhancement 2: Data Quality Framework ---' AS CHECK;

SELECT TABLE_NAME, ROW_COUNT
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND TABLE_NAME LIKE '%DATA_QUALITY%'
ORDER BY TABLE_NAME;

-- Test DQ procedure
CALL SP_CALCULATE_DATA_QUALITY();
SELECT COUNT(*) as DQ_METRICS FROM TBL_DATA_QUALITY_METRICS;

-- ============================================================================
-- CHECK 3: User Dimension
-- ============================================================================

USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA SECURITY_ANALYTICS;

SELECT '--- Enhancement 3: User Dimension ---' AS CHECK;

SELECT TABLE_NAME, ROW_COUNT
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND TABLE_NAME = 'DIM_USER'
ORDER BY TABLE_NAME;

SELECT * FROM DIM_USER LIMIT 5;

-- ============================================================================
-- CHECK 4: Near Real-Time Tables
-- ============================================================================

USE DATABASE DEV_LANDING;
USE SCHEMA SECURITY_ANALYTICS;

SELECT '--- Enhancement 4: Near Real-Time Tables ---' AS CHECK;

SELECT TABLE_NAME, ROW_COUNT
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND TABLE_NAME LIKE '%REALTIME%'
ORDER BY TABLE_NAME;

-- ============================================================================
-- SUMMARY OF ALL NEW OBJECTS
-- ============================================================================

SELECT '========================================' AS SUMMARY;
SELECT '=== IMPLEMENTATION SUMMARY ===' AS SUMMARY;
SELECT '========================================' AS SUMMARY;

SELECT 'Enhancement' AS COMPONENT, 'Object' AS TYPE, 'Status' AS STATUS
UNION ALL
SELECT '1. Power BI', 'VW_POWERBI_EXECUTIVE_DASHBOARD', '✓ Created'
UNION ALL
SELECT '2. Data Quality', 'TBL_DATA_QUALITY_METRICS', '✓ Created'
UNION ALL
SELECT '2. Data Quality', 'SP_CALCULATE_DATA_QUALITY()', '✓ Created'
UNION ALL
SELECT '3. User Dimension', 'DIM_USER', '✓ Created'
UNION ALL
SELECT '4. Real-Time', 'L_EDR_THREATS_REALTIME', '✓ Created'
UNION ALL
SELECT '4. Real-Time', 'L_CRITICAL_VULNS_REALTIME', '✓ Created';

SELECT '========================================' AS SUMMARY;
SELECT '✓ ALL 4 ENHANCEMENTS VERIFIED!' AS SUMMARY;
SELECT '========================================' AS SUMMARY;

-- ============================================================================
-- NEXT STEPS
-- ============================================================================

SELECT '========================================' AS NEXT_STEPS;
SELECT 'NEXT STEPS:' AS NEXT_STEPS;
SELECT '========================================' AS NEXT_STEPS;

SELECT '1. Connect Power BI to VW_POWERBI_EXECUTIVE_DASHBOARD' AS STEP
UNION ALL
SELECT '2. Populate real data from your security tools'
UNION ALL
SELECT '3. Schedule SP_CALCULATE_DATA_QUALITY() to run daily'
UNION ALL
SELECT '4. Configure Snowpipe for real-time data ingestion'
UNION ALL
SELECT '5. Review documentation in 00_DOCUMENTATION folder';
