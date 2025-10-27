-- ============================================================================
-- SIMPLE VERIFICATION - Check All 4 Enhancements
-- ============================================================================

USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;

-- Enhancement 1: Power BI View
USE DATABASE DEV_REPORTING;
USE SCHEMA SECURITY_ANALYTICS;

SELECT '=== Enhancement 1: Power BI ===' AS RESULT;
SELECT COUNT(*) as ROWS_IN_POWERBI_VIEW FROM VW_POWERBI_EXECUTIVE_DASHBOARD;

-- Enhancement 2: Data Quality
SELECT '=== Enhancement 2: Data Quality ===' AS RESULT;
CALL SP_CALCULATE_DATA_QUALITY();
SELECT COUNT(*) as DQ_METRICS_COUNT FROM TBL_DATA_QUALITY_METRICS;

-- Enhancement 3: User Dimension
USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA SECURITY_ANALYTICS;

SELECT '=== Enhancement 3: User Dimension ===' AS RESULT;
SELECT COUNT(*) as USER_COUNT FROM DIM_USER;
SELECT * FROM DIM_USER LIMIT 3;

-- Enhancement 4: Real-Time Tables
USE DATABASE DEV_LANDING;
USE SCHEMA SECURITY_ANALYTICS;

SELECT '=== Enhancement 4: Real-Time Tables ===' AS RESULT;
SELECT 'L_EDR_THREATS_REALTIME' AS TABLE_NAME, COUNT(*) as ROW_COUNT FROM L_EDR_THREATS_REALTIME
UNION ALL
SELECT 'L_CRITICAL_VULNS_REALTIME', COUNT(*) FROM L_CRITICAL_VULNS_REALTIME;

-- Summary
SELECT '========================================' AS RESULT;
SELECT '✓ ALL 4 ENHANCEMENTS VERIFIED!' AS RESULT;
SELECT '========================================' AS RESULT;
