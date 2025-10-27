-- ============================================================================
-- MASTER SCRIPT: EXECUTE ALL 4 NEW ENHANCEMENTS
-- ============================================================================
-- Purpose: Execute all enhancements in correct order
-- Author: Data Engineering Team
-- Date: 2025-10-07
-- Estimated Time: 10-15 minutes
--
-- INSTRUCTIONS:
-- 1. Make sure you're connected to Snowflake in VS Code
-- 2. Select all (Ctrl+A)
-- 3. Execute all (Ctrl+Enter or right-click > Execute)
-- 4. Watch for any errors in the Results pane
-- ============================================================================

-- Set context
USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;

-- ============================================================================
-- ENHANCEMENT 1: POWER BI INTEGRATION LAYER
-- ============================================================================
-- Estimated time: 2-3 minutes
-- Creates: 6 views, 2 tables, 1 function, 1 procedure, 1 task
-- ============================================================================

USE DATABASE DEV_REPORTING;
USE SCHEMA SECURITY_ANALYTICS;

SELECT '======================================================================' AS STEP;
SELECT 'STARTING ENHANCEMENT 1: POWER BI INTEGRATION LAYER' AS STEP;
SELECT '======================================================================' AS STEP;

-- Execute the Power BI Integration Layer script
!source 02_SQL_SCRIPTS/02_advanced_features/01_PowerBI_Integration_Layer.sql

SELECT '======================================================================' AS STEP;
SELECT 'ENHANCEMENT 1 COMPLETE - Verifying...' AS STEP;
SELECT '======================================================================' AS STEP;

-- Verify Enhancement 1
SELECT 'Power BI Views Created:' AS CHECK_TYPE, COUNT(*) AS COUNT
FROM INFORMATION_SCHEMA.VIEWS
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND TABLE_NAME LIKE 'VW_POWERBI%';

SELECT 'Power BI Tables Created:' AS CHECK_TYPE, COUNT(*) AS COUNT
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND (TABLE_NAME LIKE '%POWERBI%' OR TABLE_NAME LIKE 'CFG_POWERBI%');

-- ============================================================================
-- ENHANCEMENT 2: DATA QUALITY FRAMEWORK
-- ============================================================================
-- Estimated time: 2-3 minutes
-- Creates: 3 tables, 2 procedures, 3 views, 2 tasks
-- ============================================================================

SELECT '======================================================================' AS STEP;
SELECT 'STARTING ENHANCEMENT 2: DATA QUALITY FRAMEWORK' AS STEP;
SELECT '======================================================================' AS STEP;

-- Execute the Data Quality Framework script
!source 02_SQL_SCRIPTS/02_advanced_features/02_Data_Quality_Framework.sql

SELECT '======================================================================' AS STEP;
SELECT 'ENHANCEMENT 2 COMPLETE - Verifying...' AS STEP;
SELECT '======================================================================' AS STEP;

-- Verify Enhancement 2
SELECT 'DQ Tables Created:' AS CHECK_TYPE, COUNT(*) AS COUNT
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND (TABLE_NAME LIKE 'TBL_DATA_QUALITY%' OR TABLE_NAME LIKE 'CFG_DATA_QUALITY%');

SELECT 'DQ Views Created:' AS CHECK_TYPE, COUNT(*) AS COUNT
FROM INFORMATION_SCHEMA.VIEWS
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND TABLE_NAME LIKE '%DATA_QUALITY%';

-- ============================================================================
-- ENHANCEMENT 3: UNIFIED USER DIMENSION
-- ============================================================================
-- Estimated time: 2-3 minutes
-- Creates: 4 tables, 1 dimension (52 columns), 1 staging view, 1 procedure, 3 views, 1 task
-- ============================================================================

USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA SECURITY_ANALYTICS;

SELECT '======================================================================' AS STEP;
SELECT 'STARTING ENHANCEMENT 3: UNIFIED USER DIMENSION' AS STEP;
SELECT '======================================================================' AS STEP;

-- Execute the Unified User Dimension script
!source 02_SQL_SCRIPTS/02_advanced_features/03_Unified_User_Dimension.sql

SELECT '======================================================================' AS STEP;
SELECT 'ENHANCEMENT 3 COMPLETE - Verifying...' AS STEP;
SELECT '======================================================================' AS STEP;

-- Verify Enhancement 3
SELECT 'User Dimension Created:' AS CHECK_TYPE, COUNT(*) AS COUNT
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND TABLE_NAME = 'DIM_USER';

SELECT 'User Landing Tables Created:' AS CHECK_TYPE, COUNT(*) AS COUNT
FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND (TABLE_NAME LIKE 'L_ACTIVE_DIRECTORY%'
    OR TABLE_NAME LIKE 'L_HR_%'
    OR TABLE_NAME LIKE 'L_PRIVILEGED%');

SELECT 'User Views Created:' AS CHECK_TYPE, COUNT(*) AS COUNT
FROM INFORMATION_SCHEMA.VIEWS
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND TABLE_NAME LIKE 'VW_%USER%';

-- ============================================================================
-- ENHANCEMENT 4: NEAR REAL-TIME CAPABILITIES
-- ============================================================================
-- Estimated time: 3-5 minutes
-- Creates: 3 stages, 3 pipes, 3 streams, 6 tables, 3 procedures, 6 views, 3 tasks
-- NOTE: This requires ACCOUNTADMIN for Snowpipe creation
-- ============================================================================

USE DATABASE DEV_LANDING;
USE SCHEMA SECURITY_ANALYTICS;

SELECT '======================================================================' AS STEP;
SELECT 'STARTING ENHANCEMENT 4: NEAR REAL-TIME CAPABILITIES' AS STEP;
SELECT 'NOTE: Snowpipe creation requires ACCOUNTADMIN role' AS STEP;
SELECT '======================================================================' AS STEP;

-- Check if we have ACCOUNTADMIN
SELECT CURRENT_ROLE() AS CURRENT_ROLE;

-- Execute the Near Real-Time Capabilities script
!source 02_SQL_SCRIPTS/02_advanced_features/04_Near_RealTime_Capabilities.sql

SELECT '======================================================================' AS STEP;
SELECT 'ENHANCEMENT 4 COMPLETE - Verifying...' AS STEP;
SELECT '======================================================================' AS STEP;

-- Verify Enhancement 4
SELECT 'Real-Time Landing Tables Created:' AS CHECK_TYPE, COUNT(*) AS COUNT
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND TABLE_NAME LIKE 'L_%REALTIME';

SELECT 'Alert Tables Created:' AS CHECK_TYPE, COUNT(*) AS COUNT
FROM DEV_REPORTING.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND TABLE_NAME LIKE 'TBL_ALERT%';

-- ============================================================================
-- FINAL VERIFICATION & SUMMARY
-- ============================================================================

USE DATABASE DEV_REPORTING;
USE SCHEMA SECURITY_ANALYTICS;

SELECT '======================================================================' AS STEP;
SELECT 'ALL ENHANCEMENTS COMPLETE - FINAL SUMMARY' AS STEP;
SELECT '======================================================================' AS STEP;

-- Summary of all objects created
WITH all_objects AS (
    -- Views
    SELECT 'VIEWS' AS OBJECT_TYPE, COUNT(*) AS COUNT
    FROM INFORMATION_SCHEMA.VIEWS
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
      AND (TABLE_NAME LIKE 'VW_POWERBI%'
        OR TABLE_NAME LIKE '%DATA_QUALITY%'
        OR TABLE_NAME LIKE '%USER%'
        OR TABLE_NAME LIKE '%REALTIME%')

    UNION ALL

    -- Tables
    SELECT 'TABLES', COUNT(*)
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
      AND (TABLE_NAME LIKE 'TBL_POWERBI%'
        OR TABLE_NAME LIKE 'TBL_DATA_QUALITY%'
        OR TABLE_NAME LIKE 'CFG_%'
        OR TABLE_NAME LIKE 'TBL_ALERT%')

    UNION ALL

    -- Procedures
    SELECT 'PROCEDURES', COUNT(*)
    FROM INFORMATION_SCHEMA.PROCEDURES
    WHERE PROCEDURE_SCHEMA = 'SECURITY_ANALYTICS'
      AND (PROCEDURE_NAME LIKE 'SP_POPULATE_POWERBI%'
        OR PROCEDURE_NAME LIKE 'SP_CALCULATE%'
        OR PROCEDURE_NAME LIKE 'SP_LOAD_DIM_USER%'
        OR PROCEDURE_NAME LIKE 'SP_PROCESS%')
)
SELECT * FROM all_objects;

-- List all new views
SELECT '======================================================================' AS STEP;
SELECT 'NEW VIEWS CREATED:' AS STEP;
SELECT '======================================================================' AS STEP;

SELECT TABLE_NAME, TABLE_TYPE
FROM INFORMATION_SCHEMA.VIEWS
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND (TABLE_NAME LIKE 'VW_POWERBI%'
    OR TABLE_NAME LIKE 'VW_DATA_QUALITY%'
    OR TABLE_NAME LIKE 'VW_%USER%'
    OR TABLE_NAME LIKE 'VW_REALTIME%'
    OR TABLE_NAME LIKE 'VW_KPI_WITH%')
ORDER BY TABLE_NAME;

-- List all new tables
SELECT '======================================================================' AS STEP;
SELECT 'NEW TABLES CREATED:' AS STEP;
SELECT '======================================================================' AS STEP;

SELECT TABLE_NAME, TABLE_TYPE, ROW_COUNT
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND (TABLE_NAME LIKE 'TBL_POWERBI%'
    OR TABLE_NAME LIKE 'TBL_DATA_QUALITY%'
    OR TABLE_NAME LIKE 'TBL_ALERT%'
    OR TABLE_NAME LIKE 'CFG_%')
ORDER BY TABLE_NAME;

-- Show tasks created
SELECT '======================================================================' AS STEP;
SELECT 'NEW TASKS CREATED:' AS STEP;
SELECT '======================================================================' AS STEP;

SHOW TASKS LIKE '%POWERBI%' IN SCHEMA SECURITY_ANALYTICS;
SHOW TASKS LIKE '%DATA_QUALITY%' IN SCHEMA SECURITY_ANALYTICS;
SHOW TASKS LIKE '%USER%' IN DATABASE DEV_TRANSFORMATION SCHEMA SECURITY_ANALYTICS;

-- ============================================================================
-- NEXT STEPS
-- ============================================================================

SELECT '======================================================================' AS STEP;
SELECT 'IMPLEMENTATION COMPLETE! NEXT STEPS:' AS STEP;
SELECT '======================================================================' AS STEP;

SELECT '1. Run Initial Data Quality Calculations:' AS NEXT_STEP
UNION ALL
SELECT '   CALL SP_CALCULATE_DATA_QUALITY_METRICS();'
UNION ALL
SELECT '   CALL SP_CALCULATE_DQ_SCORES();'
UNION ALL
SELECT ''
UNION ALL
SELECT '2. Populate Power BI Aggregates:'
UNION ALL
SELECT '   CALL SP_POPULATE_POWERBI_AGGREGATES();'
UNION ALL
SELECT ''
UNION ALL
SELECT '3. Load User Dimension (requires source data):'
UNION ALL
SELECT '   CALL SP_LOAD_DIM_USER();'
UNION ALL
SELECT ''
UNION ALL
SELECT '4. Review Data Quality Dashboard:'
UNION ALL
SELECT '   SELECT * FROM VW_DATA_QUALITY_DASHBOARD;'
UNION ALL
SELECT ''
UNION ALL
SELECT '5. Test Power BI Views:'
UNION ALL
SELECT '   SELECT * FROM VW_POWERBI_EXECUTIVE_DASHBOARD LIMIT 10;'
UNION ALL
SELECT ''
UNION ALL
SELECT '6. Configure AWS S3/SNS for Snowpipe (see documentation)'
UNION ALL
SELECT ''
UNION ALL
SELECT '7. Run Full Test Suite:'
UNION ALL
SELECT '   !source 02_SQL_SCRIPTS/02_advanced_features/00_Test_All_Enhancements.sql';

-- ============================================================================
-- END OF MASTER SCRIPT
-- ============================================================================
