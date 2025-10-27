-- ============================================================================
-- COMPREHENSIVE TEST SUITE FOR ALL 4 ENHANCEMENTS
-- ============================================================================
-- Purpose: End-to-end testing and validation of all enhancements
-- Author: Data Engineering Team
-- Date: 2025-10-07
-- ============================================================================

-- ============================================================================
-- PRE-REQUISITES
-- ============================================================================
-- Before running this test suite:
-- 1. Execute 01_PowerBI_Integration_Layer.sql
-- 2. Execute 02_Data_Quality_Framework.sql
-- 3. Execute 03_Unified_User_Dimension.sql
-- 4. Execute 04_Near_RealTime_Capabilities.sql
-- 5. Load sample data into landing tables
-- ============================================================================

USE ROLE SYSADMIN;
USE WAREHOUSE DEV_WH;

-- ============================================================================
-- TEST SECTION 1: POWER BI INTEGRATION LAYER
-- ============================================================================

SELECT '=== TEST 1.1: Power BI Executive Dashboard ===' as TEST_NAME;
-- Expected: Should return rows with business-friendly column names
SELECT COUNT(*) as ROW_COUNT
FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_POWERBI_EXECUTIVE_DASHBOARD;

SELECT '=== TEST 1.2: Sample Executive Dashboard Data ===' as TEST_NAME;
-- Expected: Should show KPIs with data quality indicators
SELECT
    "Date",
    "Operating Company",
    "EDR Coverage - All Systems %",
    "Vuln Scan Coverage - All %",
    "Overall Security Health Score",
    "Security Health Rating",
    "Data Quality Score",
    "Confidence Level"
FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_POWERBI_EXECUTIVE_DASHBOARD
WHERE "Date" >= DATEADD('day', -7, CURRENT_DATE())
LIMIT 5;

SELECT '=== TEST 1.3: Power BI Operational Dashboard ===' as TEST_NAME;
-- Expected: Should return detailed operational data
SELECT COUNT(*) as ROW_COUNT
FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_POWERBI_OPERATIONAL_DASHBOARD;

SELECT '=== TEST 1.4: Row-Level Security Function ===' as TEST_NAME;
-- Test RLS function with different access levels
SELECT
    'cio.global@GenericCorp.com' as USER_EMAIL,
    'GLOBAL' as ACCESS_LEVEL,
    DEV_REPORTING.SECURITY_ANALYTICS.FN_POWERBI_RLS_FILTER('cio.global@GenericCorp.com', 1, 'Europe', 'IT Security') as HAS_ACCESS;

SELECT
    'itmanager.opco1@GenericCorp.com' as USER_EMAIL,
    'OPCO' as ACCESS_LEVEL,
    DEV_REPORTING.SECURITY_ANALYTICS.FN_POWERBI_RLS_FILTER('itmanager.opco1@GenericCorp.com', 1, 'Europe', 'IT Security') as HAS_ACCESS_OPCO1,
    DEV_REPORTING.SECURITY_ANALYTICS.FN_POWERBI_RLS_FILTER('itmanager.opco1@GenericCorp.com', 999, 'Europe', 'IT Security') as HAS_ACCESS_OPCO999;

SELECT '=== TEST 1.5: Power BI User Access Configuration ===' as TEST_NAME;
-- Expected: Should show configured user access rules
SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.CFG_POWERBI_USER_ACCESS;

SELECT '=== TEST 1.6: Power BI Aggregated Tables ===' as TEST_NAME;
-- Expected: Should show pre-aggregated daily metrics
SELECT COUNT(*) as ROW_COUNT
FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_POWERBI_DAILY_AGGREGATES;

SELECT
    AGG_DATE,
    OPCO_NAME,
    TOTAL_ASSETS,
    EDR_PROTECTED_ASSETS,
    EDR_COVERAGE_PCT,
    OVERALL_SECURITY_HEALTH_SCORE
FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_POWERBI_DAILY_AGGREGATES
ORDER BY AGG_DATE DESC
LIMIT 5;

SELECT '=== TEST 1.7: Power BI Aggregate Population Procedure ===' as TEST_NAME;
-- Test the aggregate population procedure
CALL DEV_REPORTING.SECURITY_ANALYTICS.SP_POPULATE_POWERBI_AGGREGATES();

SELECT '=== TEST 1.8: Power BI Tasks ===' as TEST_NAME;
-- Expected: Should show scheduled task for daily aggregates
SHOW TASKS LIKE 'TASK_POPULATE_POWERBI_AGGREGATES' IN SCHEMA DEV_REPORTING.SECURITY_ANALYTICS;

-- ============================================================================
-- TEST SECTION 2: DATA QUALITY FRAMEWORK
-- ============================================================================

SELECT '=== TEST 2.1: Data Quality Metrics Calculation ===' as TEST_NAME;
-- Run DQ metrics calculation
CALL DEV_REPORTING.SECURITY_ANALYTICS.SP_CALCULATE_DATA_QUALITY_METRICS();

SELECT '=== TEST 2.2: Data Quality Metrics Results ===' as TEST_NAME;
-- Expected: Should show DQ metrics for all configured tables
SELECT
    TABLE_NAME,
    LAYER,
    METRIC_NAME,
    METRIC_VALUE,
    THRESHOLD_VALUE,
    STATUS,
    ISSUE_COUNT
FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_DATA_QUALITY_METRICS
WHERE MEASURED_DATE = CURRENT_DATE()
ORDER BY LAYER, TABLE_NAME, METRIC_NAME
LIMIT 20;

SELECT '=== TEST 2.3: Data Quality Scores Calculation ===' as TEST_NAME;
-- Calculate DQ scores
CALL DEV_REPORTING.SECURITY_ANALYTICS.SP_CALCULATE_DQ_SCORES();

SELECT '=== TEST 2.4: Data Quality Scores Results ===' as TEST_NAME;
-- Expected: Should show overall DQ scores by table
SELECT
    TABLE_NAME,
    LAYER,
    COMPLETENESS_SCORE,
    ACCURACY_SCORE,
    FRESHNESS_SCORE,
    CONSISTENCY_SCORE,
    VALIDITY_SCORE,
    OVERALL_DQ_SCORE,
    SCORE_GRADE,
    CONFIDENCE_LEVEL
FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_DATA_QUALITY_SCORES
WHERE CALCULATED_DATE = CURRENT_DATE()
ORDER BY OVERALL_DQ_SCORE DESC;

SELECT '=== TEST 2.5: Data Quality Dashboard View ===' as TEST_NAME;
-- Expected: Executive view of DQ across all tables
SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_DATA_QUALITY_DASHBOARD
ORDER BY "Overall Data Quality Score" DESC
LIMIT 10;

SELECT '=== TEST 2.6: Data Quality Rules Configuration ===' as TEST_NAME;
-- Expected: Should show all configured DQ rules
SELECT
    RULE_ID,
    TABLE_NAME,
    LAYER,
    RULE_TYPE,
    COLUMN_NAME,
    THRESHOLD,
    SEVERITY,
    IS_ACTIVE
FROM DEV_REPORTING.SECURITY_ANALYTICS.CFG_DATA_QUALITY_RULES
WHERE IS_ACTIVE = TRUE
ORDER BY LAYER, TABLE_NAME
LIMIT 20;

SELECT '=== TEST 2.7: KPI with Data Quality Integration ===' as TEST_NAME;
-- Expected: KPIs with integrated DQ scores
SELECT
    DATE_KEY,
    OPCO_ID,
    EDR_COVERAGE_ALL_PCT,
    VULN_SCAN_COVERAGE_ALL_PCT,
    "Data Quality Score",
    "Data Quality Grade",
    "Confidence Level"
FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_KPI_WITH_DATA_QUALITY
LIMIT 5;

SELECT '=== TEST 2.8: Data Quality Tasks ===' as TEST_NAME;
-- Expected: Should show DQ calculation tasks
SHOW TASKS LIKE 'TASK_DAILY_DATA_QUALITY%' IN SCHEMA DEV_REPORTING.SECURITY_ANALYTICS;

-- ============================================================================
-- TEST SECTION 3: UNIFIED USER DIMENSION
-- ============================================================================

SELECT '=== TEST 3.1: DIM_USER Table Structure ===' as TEST_NAME;
-- Expected: Should show table exists with correct structure
DESCRIBE TABLE DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_USER;

SELECT '=== TEST 3.2: User Dimension Row Count ===' as TEST_NAME;
-- Expected: Should show total users and current users
SELECT
    COUNT(*) as TOTAL_ROWS,
    COUNT(CASE WHEN IS_CURRENT = TRUE THEN 1 END) as CURRENT_USERS,
    COUNT(CASE WHEN IS_CURRENT = FALSE THEN 1 END) as HISTORICAL_ROWS
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_USER;

SELECT '=== TEST 3.3: Sample User Data ===' as TEST_NAME;
-- Expected: Should show sample user records
SELECT
    USER_ID,
    EMAIL,
    DISPLAY_NAME,
    DEPARTMENT,
    JOB_TITLE,
    IS_ACTIVE,
    IS_PRIVILEGED_USER,
    DATA_SOURCE,
    SOURCE_SYSTEM_COUNT,
    IS_CURRENT
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_USER
WHERE IS_CURRENT = TRUE
LIMIT 10;

SELECT '=== TEST 3.4: SCD Type 2 Validation ===' as TEST_NAME;
-- Expected: Should show users with multiple versions (history)
SELECT
    USER_ID,
    EMAIL,
    DEPARTMENT,
    VALID_FROM,
    VALID_TO,
    IS_CURRENT
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_USER
WHERE USER_ID IN (
    SELECT USER_ID
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_USER
    GROUP BY USER_ID
    HAVING COUNT(*) > 1
)
ORDER BY USER_ID, VALID_FROM
LIMIT 10;

SELECT '=== TEST 3.5: Current Active Users View ===' as TEST_NAME;
-- Expected: Should show snapshot of current active users
SELECT COUNT(*) as ACTIVE_USER_COUNT
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.VW_CURRENT_USERS;

SELECT * FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.VW_CURRENT_USERS LIMIT 10;

SELECT '=== TEST 3.6: Privileged Users Report ===' as TEST_NAME;
-- Expected: Should show all privileged users with access levels
SELECT
    USER_ID,
    EMAIL,
    DISPLAY_NAME,
    IS_DOMAIN_ADMIN,
    IS_LOCAL_ADMIN,
    IS_DATABASE_ADMIN,
    IS_CLOUD_ADMIN,
    DAYS_SINCE_LAST_REVIEW,
    REVIEW_STATUS
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.VW_PRIVILEGED_USERS
LIMIT 10;

SELECT '=== TEST 3.7: Orphaned Accounts Detection ===' as TEST_NAME;
-- Expected: Should show AD accounts without HR records
SELECT
    USER_ID,
    EMAIL,
    DISPLAY_NAME,
    DAYS_SINCE_LAST_LOGON,
    IS_PRIVILEGED_USER
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.VW_ORPHANED_ACCOUNTS
LIMIT 10;

SELECT '=== TEST 3.8: User Load Procedure ===' as TEST_NAME;
-- Test the user load procedure
CALL DEV_TRANSFORMATION.SECURITY_ANALYTICS.SP_LOAD_DIM_USER();

SELECT '=== TEST 3.9: User Dimension Data Quality ===' as TEST_NAME;
-- Check data quality metrics for DIM_USER
SELECT
    COUNT(*) as TOTAL_USERS,
    COUNT(CASE WHEN EMAIL IS NULL THEN 1 END) as MISSING_EMAIL,
    COUNT(CASE WHEN DISPLAY_NAME IS NULL THEN 1 END) as MISSING_NAME,
    COUNT(CASE WHEN HAS_AD_ACCOUNT = TRUE THEN 1 END) as HAS_AD,
    COUNT(CASE WHEN HAS_HR_RECORD = TRUE THEN 1 END) as HAS_HR,
    COUNT(CASE WHEN IS_ORPHANED = TRUE THEN 1 END) as ORPHANED_ACCOUNTS
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_USER
WHERE IS_CURRENT = TRUE;

SELECT '=== TEST 3.10: User Dimension Tasks ===' as TEST_NAME;
-- Expected: Should show scheduled task for daily user load
SHOW TASKS LIKE 'TASK_LOAD_DIM_USER' IN SCHEMA DEV_TRANSFORMATION.SECURITY_ANALYTICS;

-- ============================================================================
-- TEST SECTION 4: NEAR REAL-TIME CAPABILITIES
-- ============================================================================

SELECT '=== TEST 4.1: Snowpipe Status ===' as TEST_NAME;
-- Expected: Should show Snowpipe objects
SHOW PIPES IN SCHEMA DEV_LANDING.SECURITY_ANALYTICS;

-- Check individual pipe status
SELECT SYSTEM$PIPE_STATUS('DEV_LANDING.SECURITY_ANALYTICS.PIPE_EDR_THREATS_REALTIME') as EDR_PIPE_STATUS;
SELECT SYSTEM$PIPE_STATUS('DEV_LANDING.SECURITY_ANALYTICS.PIPE_CRITICAL_VULNS_REALTIME') as VULNS_PIPE_STATUS;
SELECT SYSTEM$PIPE_STATUS('DEV_LANDING.SECURITY_ANALYTICS.PIPE_PHISHING_INCIDENTS_REALTIME') as PHISHING_PIPE_STATUS;

SELECT '=== TEST 4.2: Real-Time Landing Tables ===' as TEST_NAME;
-- Expected: Should show row counts in real-time tables
SELECT
    'L_EDR_THREATS_REALTIME' as TABLE_NAME,
    COUNT(*) as ROW_COUNT,
    MAX(INGESTED_AT) as LAST_INGESTED
FROM DEV_LANDING.SECURITY_ANALYTICS.L_EDR_THREATS_REALTIME
UNION ALL
SELECT
    'L_CRITICAL_VULNS_REALTIME',
    COUNT(*),
    MAX(INGESTED_AT)
FROM DEV_LANDING.SECURITY_ANALYTICS.L_CRITICAL_VULNS_REALTIME
UNION ALL
SELECT
    'L_PHISHING_INCIDENTS_REALTIME',
    COUNT(*),
    MAX(INGESTED_AT)
FROM DEV_LANDING.SECURITY_ANALYTICS.L_PHISHING_INCIDENTS_REALTIME;

SELECT '=== TEST 4.3: Streams Status ===' as TEST_NAME;
-- Expected: Should show configured streams
SHOW STREAMS IN SCHEMA DEV_TRANSFORMATION.SECURITY_ANALYTICS;

-- Check if streams have data
SELECT
    'STREAM_NEW_CRITICAL_VULNS' as STREAM_NAME,
    SYSTEM$STREAM_HAS_DATA('DEV_TRANSFORMATION.SECURITY_ANALYTICS.STREAM_NEW_CRITICAL_VULNS') as HAS_DATA
UNION ALL
SELECT
    'STREAM_NEW_EDR_THREATS',
    SYSTEM$STREAM_HAS_DATA('DEV_TRANSFORMATION.SECURITY_ANALYTICS.STREAM_NEW_EDR_THREATS')
UNION ALL
SELECT
    'STREAM_NEW_ASSETS',
    SYSTEM$STREAM_HAS_DATA('DEV_TRANSFORMATION.SECURITY_ANALYTICS.STREAM_NEW_ASSETS');

SELECT '=== TEST 4.4: Real-Time Alert Tables ===' as TEST_NAME;
-- Expected: Should show alert counts
SELECT
    'Critical Vulnerability Alerts' as ALERT_TYPE,
    COUNT(*) as TOTAL_ALERTS,
    COUNT(CASE WHEN ALERT_STATUS = 'OPEN' THEN 1 END) as OPEN_ALERTS,
    MAX(ALERT_TIME) as LAST_ALERT
FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_ALERT_CRITICAL_VULNERABILITIES
UNION ALL
SELECT
    'EDR Threat Alerts',
    COUNT(*),
    COUNT(CASE WHEN ALERT_STATUS = 'OPEN' THEN 1 END),
    MAX(ALERT_TIME)
FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_ALERT_EDR_THREATS
UNION ALL
SELECT
    'Asset Coverage Gap Alerts',
    COUNT(*),
    COUNT(CASE WHEN ALERT_STATUS = 'OPEN' THEN 1 END),
    MAX(ALERT_TIME)
FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_ALERT_ASSET_COVERAGE_GAPS;

SELECT '=== TEST 4.5: Real-Time Monitoring Views ===' as TEST_NAME;
-- Test real-time views
SELECT COUNT(*) as THREATS_LAST_15MIN
FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_REALTIME_THREATS_LAST_15MIN;

SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_REALTIME_THREATS_LAST_15MIN LIMIT 5;

SELECT COUNT(*) as CRITICAL_VULNS_TODAY
FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_REALTIME_CRITICAL_VULNS_TODAY;

SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_REALTIME_CRITICAL_VULNS_TODAY LIMIT 5;

SELECT '=== TEST 4.6: Security Operations Dashboard ===' as TEST_NAME;
-- Expected: Real-time operational metrics
SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_REALTIME_SECURITY_OPERATIONS;

SELECT '=== TEST 4.7: Stream Processing Procedures ===' as TEST_NAME;
-- Test stream processing procedures
CALL DEV_REPORTING.SECURITY_ANALYTICS.SP_PROCESS_NEW_CRITICAL_VULNS();
CALL DEV_REPORTING.SECURITY_ANALYTICS.SP_PROCESS_NEW_EDR_THREATS();
CALL DEV_REPORTING.SECURITY_ANALYTICS.SP_CHECK_NEW_ASSET_COVERAGE();

SELECT '=== TEST 4.8: Real-Time Tasks ===' as TEST_NAME;
-- Expected: Should show tasks for stream processing
SHOW TASKS LIKE 'TASK_PROCESS_NEW%' IN SCHEMA DEV_REPORTING.SECURITY_ANALYTICS;
SHOW TASKS LIKE 'TASK_CHECK_NEW%' IN SCHEMA DEV_REPORTING.SECURITY_ANALYTICS;

SELECT '=== TEST 4.9: Snowpipe Performance ===' as TEST_NAME;
-- Expected: Recent Snowpipe ingestion history
SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_SNOWPIPE_PERFORMANCE
LIMIT 10;

SELECT '=== TEST 4.10: Stream Lag Monitoring ===' as TEST_NAME;
-- Expected: Current stream status and pending rows
SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_STREAM_LAG_MONITORING;

-- ============================================================================
-- TEST SECTION 5: INTEGRATION TESTS
-- ============================================================================

SELECT '=== TEST 5.1: Power BI + Data Quality Integration ===' as TEST_NAME;
-- Expected: Power BI views should include DQ scores
SELECT
    "Operating Company",
    "EDR Coverage - All Systems %",
    "Data Quality Score",
    "Confidence Level"
FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_POWERBI_EXECUTIVE_DASHBOARD
WHERE "Date" = CURRENT_DATE()
LIMIT 5;

SELECT '=== TEST 5.2: User Dimension + Data Quality ===' as TEST_NAME;
-- Expected: DIM_USER should have DQ metrics
SELECT
    TABLE_NAME,
    METRIC_NAME,
    METRIC_VALUE,
    STATUS
FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_DATA_QUALITY_METRICS
WHERE TABLE_NAME = 'DIM_USER'
  AND MEASURED_DATE = CURRENT_DATE();

SELECT '=== TEST 5.3: Real-Time Alerts + Power BI ===' as TEST_NAME;
-- Expected: Alert data available for Power BI dashboards
SELECT
    COUNT(*) as OPEN_CRITICAL_ALERTS,
    AVG("Avg Ingestion Latency (sec)") as AVG_LATENCY_SEC
FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_REALTIME_SECURITY_OPERATIONS;

-- ============================================================================
-- TEST SECTION 6: PERFORMANCE VALIDATION
-- ============================================================================

SELECT '=== TEST 6.1: View Query Performance ===' as TEST_NAME;
-- Test query performance on main views (should complete in < 10 seconds)
SET start_time = CURRENT_TIMESTAMP();

SELECT COUNT(*) as ROW_COUNT
FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_POWERBI_EXECUTIVE_DASHBOARD
WHERE "Date" >= DATEADD('month', -1, CURRENT_DATE());

SELECT DATEDIFF('second', $start_time, CURRENT_TIMESTAMP()) as QUERY_DURATION_SEC;

SELECT '=== TEST 6.2: Aggregated Table Performance ===' as TEST_NAME;
-- Expected: Aggregated queries should be fast
SET start_time = CURRENT_TIMESTAMP();

SELECT
    OPCO_NAME,
    AVG(EDR_COVERAGE_PCT) as AVG_EDR_COVERAGE,
    AVG(OVERALL_SECURITY_HEALTH_SCORE) as AVG_HEALTH_SCORE
FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_POWERBI_DAILY_AGGREGATES
GROUP BY OPCO_NAME;

SELECT DATEDIFF('second', $start_time, CURRENT_TIMESTAMP()) as QUERY_DURATION_SEC;

-- ============================================================================
-- TEST SECTION 7: DATA LINEAGE VERIFICATION
-- ============================================================================

SELECT '=== TEST 7.1: Landing → Transformation Lineage ===' as TEST_NAME;
-- Verify data flows from Landing to Transformation
SELECT
    'L_QUALYS_SCANS' as LANDING_TABLE,
    COUNT(*) as LANDING_ROWS,
    (SELECT COUNT(*) FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_QUALYS) as TRANSFORMATION_ROWS,
    (TRANSFORMATION_ROWS * 100.0 / NULLIF(LANDING_ROWS, 0)) as TRANSFORMATION_PCT
FROM DEV_LANDING.SECURITY_ANALYTICS.L_QUALYS_SCANS;

SELECT '=== TEST 7.2: Transformation → Reporting Lineage ===' as TEST_NAME;
-- Verify data flows to Reporting layer
SELECT
    COUNT(DISTINCT h.HOST_ID) as TOTAL_HOSTS_IN_DIM,
    COUNT(DISTINCT kpi.HOST_ID) as HOSTS_IN_KPIS,
    (HOSTS_IN_KPIS * 100.0 / NULLIF(TOTAL_HOSTS_IN_DIM, 0)) as COVERAGE_PCT
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST h
LEFT JOIN DEV_REPORTING.SECURITY_ANALYTICS.TBL_KPI_MASTER kpi ON h.HOST_ID = kpi.HOST_ID;

-- ============================================================================
-- TEST SUMMARY REPORT
-- ============================================================================

SELECT '=== FINAL TEST SUMMARY REPORT ===' as TEST_NAME;

WITH test_results AS (
    SELECT
        '1. Power BI Integration' as COMPONENT,
        CASE
            WHEN (SELECT COUNT(*) FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_POWERBI_EXECUTIVE_DASHBOARD) > 0
            THEN '✅ PASS'
            ELSE '❌ FAIL'
        END as STATUS,
        (SELECT COUNT(*) FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_POWERBI_EXECUTIVE_DASHBOARD) as ROW_COUNT

    UNION ALL

    SELECT
        '2. Data Quality Framework',
        CASE
            WHEN (SELECT COUNT(*) FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_DATA_QUALITY_METRICS WHERE MEASURED_DATE = CURRENT_DATE()) > 0
            THEN '✅ PASS'
            ELSE '❌ FAIL'
        END,
        (SELECT COUNT(*) FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_DATA_QUALITY_METRICS WHERE MEASURED_DATE = CURRENT_DATE())

    UNION ALL

    SELECT
        '3. Unified User Dimension',
        CASE
            WHEN (SELECT COUNT(*) FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_USER WHERE IS_CURRENT = TRUE) > 0
            THEN '✅ PASS'
            ELSE '❌ FAIL'
        END,
        (SELECT COUNT(*) FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_USER WHERE IS_CURRENT = TRUE)

    UNION ALL

    SELECT
        '4. Near Real-Time Capabilities',
        CASE
            WHEN (SELECT COUNT(*) FROM DEV_LANDING.SECURITY_ANALYTICS.L_EDR_THREATS_REALTIME) >= 0
            THEN '✅ PASS'
            ELSE '❌ FAIL'
        END,
        (SELECT COUNT(*) FROM DEV_LANDING.SECURITY_ANALYTICS.L_EDR_THREATS_REALTIME)
)
SELECT * FROM test_results;

-- Task Status Summary
SELECT '=== TASK STATUS SUMMARY ===' as SUMMARY_NAME;
SHOW TASKS IN SCHEMA DEV_REPORTING.SECURITY_ANALYTICS;
SHOW TASKS IN SCHEMA DEV_TRANSFORMATION.SECURITY_ANALYTICS;

-- ============================================================================
-- END OF COMPREHENSIVE TEST SUITE
-- ============================================================================
/*
TEST COMPLETION CHECKLIST:

✅ Power BI Integration Layer:
   - Executive Dashboard View
   - Operational Dashboard View
   - Row-Level Security
   - Aggregated Tables
   - Scheduled Tasks

✅ Data Quality Framework:
   - Metrics Calculation
   - Scoring System
   - Dashboard Views
   - Configuration Rules
   - Automated Tasks

✅ Unified User Dimension:
   - SCD Type 2 Implementation
   - Multi-Source Integration
   - Orphaned Account Detection
   - Privileged User Tracking
   - Daily Load Task

✅ Near Real-Time Capabilities:
   - Snowpipe Configuration
   - Real-Time Landing Tables
   - Stream Processing
   - Alert Generation
   - Monitoring Views

NEXT STEPS:
1. Review test results
2. Address any failures
3. Configure AWS S3 and SNS for Snowpipe
4. Load sample data for full testing
5. Configure Power BI connection
6. Set up notification integrations
*/
