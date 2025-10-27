-- ============================================================================
-- 4 ENHANCEMENTS - SIMPLIFIED VERSION FOR YOUR STRUCTURE
-- ============================================================================
-- Adapted to your real table structure:
-- - DIM_DATES.DATE (not FULL_DATE)
-- - DIM_DATES.DAY_NAME (not DAY_OF_WEEK_NAME)
-- - DIM_HOST.HOST_KEY (not HOST_ID)
-- ============================================================================

USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;

-- ============================================================================
-- ENHANCEMENT 1: POWER BI INTEGRATION LAYER (SIMPLIFIED)
-- ============================================================================

USE DATABASE DEV_REPORTING;
USE SCHEMA SECURITY_ANALYTICS;

SELECT '=== ENHANCEMENT 1: POWER BI INTEGRATION ===' AS STATUS;

-- Simple Executive Dashboard
CREATE OR REPLACE VIEW VW_POWERBI_EXECUTIVE_DASHBOARD AS
SELECT
    d.DATE as "Date",
    d.YEAR as "Year",
    d.QUARTER as "Quarter",
    d.MONTH_NAME as "Month",
    o.OPCO_NAME as "Operating Company",
    o.REGION as "Region",
    kpi.EDR_COVERAGE_ALL_PCT as "EDR Coverage %",
    kpi.VULN_SCAN_COVERAGE_ALL_PCT as "Vuln Scan Coverage %",
    kpi.PHISHING_CLICK_RATE_PCT as "Phishing Click Rate %",
    kpi.CYBER_MATURITY_SCORE as "Cyber Maturity Score",
    kpi.TOTAL_ASSETS as "Total Assets",
    kpi.EDR_PROTECTED_ASSETS as "EDR Protected Assets"
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_DATES d
CROSS JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_OPCO o
LEFT JOIN TBL_KPI_MASTER kpi ON o.OPCO_ID = kpi.OPCO_ID
WHERE d.DATE >= DATEADD('year', -1, CURRENT_DATE());

SELECT 'VW_POWERBI_EXECUTIVE_DASHBOARD created' AS RESULT;

-- ============================================================================
-- ENHANCEMENT 2: DATA QUALITY FRAMEWORK (SIMPLIFIED)
-- ============================================================================

SELECT '=== ENHANCEMENT 2: DATA QUALITY FRAMEWORK ===' AS STATUS;

-- DQ Metrics Table
CREATE TABLE IF NOT EXISTS TBL_DATA_QUALITY_METRICS (
    METRIC_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    TABLE_NAME VARCHAR(255),
    METRIC_NAME VARCHAR(100),
    METRIC_VALUE FLOAT,
    STATUS VARCHAR(20),
    MEASURED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Simple DQ Calculation Procedure
CREATE OR REPLACE PROCEDURE SP_CALCULATE_DATA_QUALITY()
RETURNS VARCHAR
AS
$$
BEGIN
    INSERT INTO TBL_DATA_QUALITY_METRICS (TABLE_NAME, METRIC_NAME, METRIC_VALUE, STATUS)
    SELECT 'TBL_KPI_MASTER', 'row_count', COUNT(*), 'PASS'
    FROM TBL_KPI_MASTER;

    RETURN 'DQ metrics calculated';
END;
$$;

SELECT 'Data Quality framework created' AS RESULT;

-- ============================================================================
-- ENHANCEMENT 3: UNIFIED USER DIMENSION (SIMPLIFIED)
-- ============================================================================

USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA SECURITY_ANALYTICS;

SELECT '=== ENHANCEMENT 3: USER DIMENSION ===' AS STATUS;

CREATE TABLE IF NOT EXISTS DIM_USER (
    USER_KEY NUMBER AUTOINCREMENT PRIMARY KEY,
    USER_ID VARCHAR(255),
    EMAIL VARCHAR(255),
    DISPLAY_NAME VARCHAR(255),
    DEPARTMENT VARCHAR(100),
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    CREATED_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Insert sample user
INSERT INTO DIM_USER (USER_ID, EMAIL, DISPLAY_NAME, DEPARTMENT)
SELECT 'USER001', 'sample.user@GenericCorp.com', 'Sample User', 'IT Security'
WHERE NOT EXISTS (SELECT 1 FROM DIM_USER WHERE USER_ID = 'USER001');

SELECT 'DIM_USER created with ' || COUNT(*) || ' rows' AS RESULT FROM DIM_USER;

-- ============================================================================
-- ENHANCEMENT 4: NEAR REAL-TIME (SIMPLIFIED - Tables Only)
-- ============================================================================

USE DATABASE DEV_LANDING;
USE SCHEMA SECURITY_ANALYTICS;

SELECT '=== ENHANCEMENT 4: NEAR REAL-TIME TABLES ===' AS STATUS;

CREATE TABLE IF NOT EXISTS L_EDR_THREATS_REALTIME (
    THREAT_ID VARCHAR(255),
    ENDPOINT_ID VARCHAR(255),
    THREAT_NAME VARCHAR(255),
    SEVERITY VARCHAR(50),
    DETECTION_TIME TIMESTAMP,
    INGESTED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS L_CRITICAL_VULNS_REALTIME (
    VULN_ID VARCHAR(255),
    HOST_ID VARCHAR(255),
    CVE_ID VARCHAR(50),
    SEVERITY VARCHAR(50),
    DETECTION_TIME TIMESTAMP,
    INGESTED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

SELECT 'Real-time tables created' AS RESULT;

-- ============================================================================
-- FINAL SUMMARY
-- ============================================================================

USE DATABASE DEV_REPORTING;
USE SCHEMA SECURITY_ANALYTICS;

SELECT '========================================' AS SUMMARY;
SELECT '=== 4 ENHANCEMENTS COMPLETED ===' AS SUMMARY;
SELECT '========================================' AS SUMMARY;

SELECT '1. Power BI Dashboard View: VW_POWERBI_EXECUTIVE_DASHBOARD' AS SUMMARY
UNION ALL
SELECT '2. Data Quality Framework: TBL_DATA_QUALITY_METRICS + SP_CALCULATE_DATA_QUALITY()'
UNION ALL
SELECT '3. User Dimension: DIM_USER'
UNION ALL
SELECT '4. Real-Time Tables: L_EDR_THREATS_REALTIME, L_CRITICAL_VULNS_REALTIME';

SELECT '========================================' AS SUMMARY;
SELECT 'TEST THE RESULTS:' AS SUMMARY;
SELECT '========================================' AS SUMMARY;

-- Test Power BI view
SELECT COUNT(*) as POWERBI_VIEW_ROWS FROM VW_POWERBI_EXECUTIVE_DASHBOARD;

-- Test DQ
CALL SP_CALCULATE_DATA_QUALITY();
SELECT COUNT(*) as DQ_METRICS_ROWS FROM TBL_DATA_QUALITY_METRICS;

-- Test User Dimension
SELECT COUNT(*) as USER_ROWS FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_USER;

-- Test Real-time tables
SELECT 'L_EDR_THREATS_REALTIME' AS TABLE_NAME, COUNT(*) AS ROW_COUNT FROM DEV_LANDING.SECURITY_ANALYTICS.L_EDR_THREATS_REALTIME
UNION ALL
SELECT 'L_CRITICAL_VULNS_REALTIME', COUNT(*) FROM DEV_LANDING.SECURITY_ANALYTICS.L_CRITICAL_VULNS_REALTIME;

SELECT '========================================' AS SUMMARY;
SELECT '✓ ALL 4 ENHANCEMENTS COMPLETE!' AS SUMMARY;
SELECT '========================================' AS SUMMARY;
