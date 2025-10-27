-- ============================================================================
-- ENHANCEMENT 2: DATA QUALITY FRAMEWORK
-- ============================================================================
-- Purpose: Comprehensive data quality monitoring and scoring system
-- Author: Data Engineering Team
-- Date: 2025-10-07
-- Estimated Effort: 28 hours
-- ============================================================================

USE ROLE SYSADMIN;
USE WAREHOUSE DEV_WH;
USE DATABASE DEV_REPORTING;
USE SCHEMA SECURITY_ANALYTICS;

-- ============================================================================
-- SECTION 1: DATA QUALITY METRICS STORAGE
-- ============================================================================

CREATE TABLE IF NOT EXISTS TBL_DATA_QUALITY_METRICS (
    METRIC_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    TABLE_NAME VARCHAR(255) NOT NULL,
    LAYER VARCHAR(50),  -- 'LANDING', 'TRANSFORMATION', 'REPORTING'
    METRIC_NAME VARCHAR(100) NOT NULL,  -- 'completeness', 'accuracy', 'freshness', 'consistency', 'validity'
    METRIC_VALUE FLOAT,  -- 0-100 score
    THRESHOLD_VALUE FLOAT,  -- Expected minimum value
    STATUS VARCHAR(20),  -- 'PASS', 'WARNING', 'FAIL'
    ISSUE_COUNT NUMBER DEFAULT 0,
    SAMPLE_ISSUE_IDS ARRAY,  -- Array of sample record IDs with issues
    MEASURED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    MEASURED_DATE DATE DEFAULT CURRENT_DATE(),

    -- Audit
    CREATED_BY VARCHAR(100) DEFAULT CURRENT_USER(),
    CREATED_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'Stores data quality metrics for all tables across all layers';

-- Partitioning by date for performance
ALTER TABLE TBL_DATA_QUALITY_METRICS
    CLUSTER BY (MEASURED_DATE, LAYER, TABLE_NAME);

-- ============================================================================
-- SECTION 2: DATA QUALITY RULES CONFIGURATION
-- ============================================================================

CREATE TABLE IF NOT EXISTS CFG_DATA_QUALITY_RULES (
    RULE_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    TABLE_NAME VARCHAR(255) NOT NULL,
    LAYER VARCHAR(50) NOT NULL,
    RULE_TYPE VARCHAR(50) NOT NULL,  -- 'COMPLETENESS', 'ACCURACY', 'FRESHNESS', 'CONSISTENCY', 'VALIDITY'
    COLUMN_NAME VARCHAR(255),
    RULE_DESCRIPTION VARCHAR(500),
    VALIDATION_SQL VARCHAR(5000),  -- SQL expression that returns TRUE/FALSE
    THRESHOLD FLOAT DEFAULT 95.0,  -- Minimum acceptable percentage
    SEVERITY VARCHAR(20) DEFAULT 'WARNING',  -- 'INFO', 'WARNING', 'CRITICAL'
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    CREATED_BY VARCHAR(100) DEFAULT CURRENT_USER(),
    CREATED_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'Configuration table for data quality validation rules';

-- Sample DQ rules
INSERT INTO CFG_DATA_QUALITY_RULES (TABLE_NAME, LAYER, RULE_TYPE, COLUMN_NAME, RULE_DESCRIPTION, VALIDATION_SQL, THRESHOLD, SEVERITY)
VALUES
    -- Landing Layer Rules
    ('L_QUALYS_SCANS', 'LANDING', 'COMPLETENESS', 'HOST_ID', 'Host ID must not be null', 'HOST_ID IS NOT NULL', 100.0, 'CRITICAL'),
    ('L_QUALYS_SCANS', 'LANDING', 'COMPLETENESS', 'SCAN_DATE', 'Scan date must not be null', 'SCAN_DATE IS NOT NULL', 100.0, 'CRITICAL'),
    ('L_QUALYS_SCANS', 'LANDING', 'FRESHNESS', NULL, 'Data must be less than 7 days old', 'DATEDIFF(''day'', MAX(LOAD_TIMESTAMP), CURRENT_DATE()) <= 7', 95.0, 'WARNING'),

    -- Transformation Layer Rules
    ('DIM_HOST', 'TRANSFORMATION', 'COMPLETENESS', 'HOSTNAME', 'Hostname must not be null', 'HOSTNAME IS NOT NULL', 98.0, 'CRITICAL'),
    ('DIM_HOST', 'TRANSFORMATION', 'ACCURACY', 'IP_ADDRESS', 'IP address must be valid format', 'REGEXP_LIKE(IP_ADDRESS, ''^[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}$'')', 95.0, 'WARNING'),
    ('DIM_HOST', 'TRANSFORMATION', 'CONSISTENCY', 'OPCO_ID', 'OpCo ID must exist in DIM_OPCO', 'OPCO_ID IN (SELECT OPCO_ID FROM DIM_OPCO)', 100.0, 'CRITICAL'),

    ('FACT_QUALYS', 'TRANSFORMATION', 'COMPLETENESS', 'HOST_ID', 'Host ID must not be null', 'HOST_ID IS NOT NULL', 100.0, 'CRITICAL'),
    ('FACT_QUALYS', 'TRANSFORMATION', 'VALIDITY', 'SEVERITY', 'Severity must be valid value', 'SEVERITY IN (''CRITICAL'', ''HIGH'', ''MEDIUM'', ''LOW'', ''INFORMATIONAL'')', 100.0, 'CRITICAL'),
    ('FACT_QUALYS', 'TRANSFORMATION', 'CONSISTENCY', 'HOST_ID', 'Host ID must exist in DIM_HOST', 'HOST_ID IN (SELECT HOST_ID FROM DIM_HOST)', 100.0, 'CRITICAL'),

    -- Reporting Layer Rules
    ('TBL_KPI_MASTER', 'REPORTING', 'COMPLETENESS', 'DATE_KEY', 'Date key must not be null', 'DATE_KEY IS NOT NULL', 100.0, 'CRITICAL'),
    ('TBL_KPI_MASTER', 'REPORTING', 'COMPLETENESS', 'OPCO_ID', 'OpCo ID must not be null', 'OPCO_ID IS NOT NULL', 100.0, 'CRITICAL'),
    ('TBL_KPI_MASTER', 'REPORTING', 'VALIDITY', 'EDR_COVERAGE_ALL_PCT', 'EDR coverage must be between 0-100', 'EDR_COVERAGE_ALL_PCT BETWEEN 0 AND 100', 100.0, 'CRITICAL'),
    ('TBL_KPI_MASTER', 'REPORTING', 'FRESHNESS', NULL, 'KPIs must be updated daily', 'DATEDIFF(''day'', MAX(LOAD_TIMESTAMP), CURRENT_DATE()) <= 1', 100.0, 'CRITICAL')
;

-- ============================================================================
-- SECTION 3: DATA QUALITY CALCULATION PROCEDURES
-- ============================================================================

CREATE OR REPLACE PROCEDURE SP_CALCULATE_DATA_QUALITY_METRICS()
RETURNS VARCHAR
LANGUAGE SQL
COMMENT = 'Calculates comprehensive data quality metrics for all configured tables'
AS
$$
DECLARE
    processed_tables NUMBER DEFAULT 0;
    total_checks NUMBER DEFAULT 0;
BEGIN
    -- Clear today's metrics (idempotent)
    DELETE FROM TBL_DATA_QUALITY_METRICS
    WHERE MEASURED_DATE = CURRENT_DATE();

    -- ========== COMPLETENESS CHECKS ==========
    -- DIM_HOST completeness
    INSERT INTO TBL_DATA_QUALITY_METRICS (TABLE_NAME, LAYER, METRIC_NAME, METRIC_VALUE, THRESHOLD_VALUE, STATUS, ISSUE_COUNT)
    SELECT
        'DIM_HOST' as TABLE_NAME,
        'TRANSFORMATION' as LAYER,
        'completeness_hostname' as METRIC_NAME,
        ROUND((COUNT(*) - COUNT(CASE WHEN HOSTNAME IS NULL THEN 1 END)) * 100.0 / COUNT(*), 2) as METRIC_VALUE,
        98.0 as THRESHOLD_VALUE,
        CASE
            WHEN METRIC_VALUE >= THRESHOLD_VALUE THEN 'PASS'
            WHEN METRIC_VALUE >= (THRESHOLD_VALUE - 5) THEN 'WARNING'
            ELSE 'FAIL'
        END as STATUS,
        COUNT(CASE WHEN HOSTNAME IS NULL THEN 1 END) as ISSUE_COUNT
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST;

    INSERT INTO TBL_DATA_QUALITY_METRICS (TABLE_NAME, LAYER, METRIC_NAME, METRIC_VALUE, THRESHOLD_VALUE, STATUS, ISSUE_COUNT)
    SELECT
        'DIM_HOST',
        'TRANSFORMATION',
        'completeness_ip_address',
        ROUND((COUNT(*) - COUNT(CASE WHEN IP_ADDRESS IS NULL THEN 1 END)) * 100.0 / COUNT(*), 2),
        95.0,
        CASE WHEN METRIC_VALUE >= 95.0 THEN 'PASS' WHEN METRIC_VALUE >= 90.0 THEN 'WARNING' ELSE 'FAIL' END,
        COUNT(CASE WHEN IP_ADDRESS IS NULL THEN 1 END)
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST;

    -- FACT_QUALYS completeness
    INSERT INTO TBL_DATA_QUALITY_METRICS (TABLE_NAME, LAYER, METRIC_NAME, METRIC_VALUE, THRESHOLD_VALUE, STATUS, ISSUE_COUNT)
    SELECT
        'FACT_QUALYS',
        'TRANSFORMATION',
        'completeness_host_id',
        ROUND((COUNT(*) - COUNT(CASE WHEN HOST_ID IS NULL THEN 1 END)) * 100.0 / COUNT(*), 2),
        100.0,
        CASE WHEN METRIC_VALUE = 100.0 THEN 'PASS' ELSE 'FAIL' END,
        COUNT(CASE WHEN HOST_ID IS NULL THEN 1 END)
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_QUALYS;

    -- ========== ACCURACY CHECKS ==========
    -- Valid IP addresses
    INSERT INTO TBL_DATA_QUALITY_METRICS (TABLE_NAME, LAYER, METRIC_NAME, METRIC_VALUE, THRESHOLD_VALUE, STATUS, ISSUE_COUNT)
    SELECT
        'DIM_HOST',
        'TRANSFORMATION',
        'accuracy_ip_address_format',
        ROUND(
            COUNT(CASE WHEN REGEXP_LIKE(IP_ADDRESS, '^[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}$')
                  THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0),
        2),
        95.0,
        CASE WHEN METRIC_VALUE >= 95.0 THEN 'PASS' WHEN METRIC_VALUE >= 90.0 THEN 'WARNING' ELSE 'FAIL' END,
        COUNT(CASE WHEN NOT REGEXP_LIKE(COALESCE(IP_ADDRESS, ''), '^[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}$')
                   AND IP_ADDRESS IS NOT NULL THEN 1 END)
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST;

    -- Valid severity values
    INSERT INTO TBL_DATA_QUALITY_METRICS (TABLE_NAME, LAYER, METRIC_NAME, METRIC_VALUE, THRESHOLD_VALUE, STATUS, ISSUE_COUNT)
    SELECT
        'FACT_QUALYS',
        'TRANSFORMATION',
        'accuracy_severity_values',
        ROUND(
            COUNT(CASE WHEN SEVERITY IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFORMATIONAL')
                  THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0),
        2),
        100.0,
        CASE WHEN METRIC_VALUE = 100.0 THEN 'PASS' ELSE 'FAIL' END,
        COUNT(CASE WHEN SEVERITY NOT IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFORMATIONAL')
                   AND SEVERITY IS NOT NULL THEN 1 END)
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_QUALYS;

    -- ========== FRESHNESS CHECKS ==========
    -- Landing layer freshness
    INSERT INTO TBL_DATA_QUALITY_METRICS (TABLE_NAME, LAYER, METRIC_NAME, METRIC_VALUE, THRESHOLD_VALUE, STATUS, ISSUE_COUNT)
    SELECT
        'L_QUALYS_SCANS',
        'LANDING',
        'freshness_days_since_update',
        CASE
            WHEN DATEDIFF('day', MAX(LOAD_TIMESTAMP), CURRENT_DATE()) <= 1 THEN 100.0
            WHEN DATEDIFF('day', MAX(LOAD_TIMESTAMP), CURRENT_DATE()) <= 3 THEN 80.0
            WHEN DATEDIFF('day', MAX(LOAD_TIMESTAMP), CURRENT_DATE()) <= 7 THEN 50.0
            ELSE 0.0
        END,
        95.0,
        CASE WHEN METRIC_VALUE >= 95.0 THEN 'PASS' WHEN METRIC_VALUE >= 50.0 THEN 'WARNING' ELSE 'FAIL' END,
        DATEDIFF('day', MAX(LOAD_TIMESTAMP), CURRENT_DATE())
    FROM DEV_LANDING.SECURITY_ANALYTICS.L_QUALYS_SCANS;

    -- KPI freshness
    INSERT INTO TBL_DATA_QUALITY_METRICS (TABLE_NAME, LAYER, METRIC_NAME, METRIC_VALUE, THRESHOLD_VALUE, STATUS, ISSUE_COUNT)
    SELECT
        'TBL_KPI_MASTER',
        'REPORTING',
        'freshness_days_since_update',
        CASE
            WHEN DATEDIFF('day', MAX(LOAD_TIMESTAMP), CURRENT_DATE()) = 0 THEN 100.0
            WHEN DATEDIFF('day', MAX(LOAD_TIMESTAMP), CURRENT_DATE()) = 1 THEN 90.0
            ELSE 0.0
        END,
        100.0,
        CASE WHEN METRIC_VALUE = 100.0 THEN 'PASS' WHEN METRIC_VALUE >= 90.0 THEN 'WARNING' ELSE 'FAIL' END,
        DATEDIFF('day', MAX(LOAD_TIMESTAMP), CURRENT_DATE())
    FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_KPI_MASTER;

    -- ========== CONSISTENCY CHECKS ==========
    -- OpCo referential integrity
    INSERT INTO TBL_DATA_QUALITY_METRICS (TABLE_NAME, LAYER, METRIC_NAME, METRIC_VALUE, THRESHOLD_VALUE, STATUS, ISSUE_COUNT)
    SELECT
        'DIM_HOST',
        'TRANSFORMATION',
        'consistency_opco_fk',
        ROUND(
            COUNT(CASE WHEN h.OPCO_ID IN (SELECT OPCO_ID FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_OPCO)
                  THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0),
        2),
        100.0,
        CASE WHEN METRIC_VALUE = 100.0 THEN 'PASS' ELSE 'FAIL' END,
        COUNT(CASE WHEN h.OPCO_ID NOT IN (SELECT OPCO_ID FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_OPCO)
                   AND h.OPCO_ID IS NOT NULL THEN 1 END)
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST h;

    -- Host referential integrity in FACT tables
    INSERT INTO TBL_DATA_QUALITY_METRICS (TABLE_NAME, LAYER, METRIC_NAME, METRIC_VALUE, THRESHOLD_VALUE, STATUS, ISSUE_COUNT)
    SELECT
        'FACT_QUALYS',
        'TRANSFORMATION',
        'consistency_host_fk',
        ROUND(
            COUNT(CASE WHEN f.HOST_ID IN (SELECT HOST_ID FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST)
                  THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0),
        2),
        100.0,
        CASE WHEN METRIC_VALUE = 100.0 THEN 'PASS' ELSE 'FAIL' END,
        COUNT(CASE WHEN f.HOST_ID NOT IN (SELECT HOST_ID FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST)
                   AND f.HOST_ID IS NOT NULL THEN 1 END)
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_QUALYS f;

    -- ========== VALIDITY CHECKS ==========
    -- EDR Coverage percentage range
    INSERT INTO TBL_DATA_QUALITY_METRICS (TABLE_NAME, LAYER, METRIC_NAME, METRIC_VALUE, THRESHOLD_VALUE, STATUS, ISSUE_COUNT)
    SELECT
        'TBL_KPI_MASTER',
        'REPORTING',
        'validity_edr_coverage_range',
        ROUND(
            COUNT(CASE WHEN EDR_COVERAGE_ALL_PCT BETWEEN 0 AND 100 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0),
        2),
        100.0,
        CASE WHEN METRIC_VALUE = 100.0 THEN 'PASS' ELSE 'FAIL' END,
        COUNT(CASE WHEN EDR_COVERAGE_ALL_PCT NOT BETWEEN 0 AND 100
                   AND EDR_COVERAGE_ALL_PCT IS NOT NULL THEN 1 END)
    FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_KPI_MASTER;

    SET total_checks = (SELECT COUNT(*) FROM TBL_DATA_QUALITY_METRICS WHERE MEASURED_DATE = CURRENT_DATE());
    SET processed_tables = (SELECT COUNT(DISTINCT TABLE_NAME) FROM TBL_DATA_QUALITY_METRICS WHERE MEASURED_DATE = CURRENT_DATE());

    RETURN 'Data Quality metrics calculated: ' || :total_checks || ' checks across ' || :processed_tables || ' tables';
END;
$$;

-- ============================================================================
-- SECTION 4: DATA QUALITY SCORING
-- ============================================================================

CREATE TABLE IF NOT EXISTS TBL_DATA_QUALITY_SCORES (
    SCORE_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    DATE_KEY NUMBER,
    OPCO_ID NUMBER,
    TABLE_NAME VARCHAR(255),
    LAYER VARCHAR(50),

    -- Individual dimension scores (0-100)
    COMPLETENESS_SCORE FLOAT,
    ACCURACY_SCORE FLOAT,
    FRESHNESS_SCORE FLOAT,
    CONSISTENCY_SCORE FLOAT,
    VALIDITY_SCORE FLOAT,

    -- Overall score (weighted average)
    OVERALL_DQ_SCORE FLOAT,

    -- Score interpretation
    SCORE_GRADE VARCHAR(10),  -- 'A+', 'A', 'B', 'C', 'D', 'F'
    CONFIDENCE_LEVEL VARCHAR(20),  -- 'High', 'Medium', 'Low'

    -- Audit
    CALCULATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    CALCULATED_DATE DATE DEFAULT CURRENT_DATE()
)
COMMENT = 'Aggregated data quality scores by table, layer, and OpCo';

-- Procedure to calculate DQ scores
CREATE OR REPLACE PROCEDURE SP_CALCULATE_DQ_SCORES()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
    DELETE FROM TBL_DATA_QUALITY_SCORES WHERE CALCULATED_DATE = CURRENT_DATE();

    INSERT INTO TBL_DATA_QUALITY_SCORES (
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
    )
    SELECT
        TABLE_NAME,
        LAYER,
        AVG(CASE WHEN METRIC_NAME LIKE 'completeness%' THEN METRIC_VALUE END) as COMPLETENESS_SCORE,
        AVG(CASE WHEN METRIC_NAME LIKE 'accuracy%' THEN METRIC_VALUE END) as ACCURACY_SCORE,
        AVG(CASE WHEN METRIC_NAME LIKE 'freshness%' THEN METRIC_VALUE END) as FRESHNESS_SCORE,
        AVG(CASE WHEN METRIC_NAME LIKE 'consistency%' THEN METRIC_VALUE END) as CONSISTENCY_SCORE,
        AVG(CASE WHEN METRIC_NAME LIKE 'validity%' THEN METRIC_VALUE END) as VALIDITY_SCORE,

        -- Weighted overall score
        ROUND(
            COALESCE(COMPLETENESS_SCORE, 0) * 0.30 +
            COALESCE(ACCURACY_SCORE, 0) * 0.25 +
            COALESCE(FRESHNESS_SCORE, 0) * 0.20 +
            COALESCE(CONSISTENCY_SCORE, 0) * 0.15 +
            COALESCE(VALIDITY_SCORE, 0) * 0.10,
        2) as OVERALL_DQ_SCORE,

        CASE
            WHEN OVERALL_DQ_SCORE >= 98 THEN 'A+'
            WHEN OVERALL_DQ_SCORE >= 95 THEN 'A'
            WHEN OVERALL_DQ_SCORE >= 85 THEN 'B'
            WHEN OVERALL_DQ_SCORE >= 70 THEN 'C'
            WHEN OVERALL_DQ_SCORE >= 50 THEN 'D'
            ELSE 'F'
        END as SCORE_GRADE,

        CASE
            WHEN OVERALL_DQ_SCORE >= 95 THEN 'High'
            WHEN OVERALL_DQ_SCORE >= 80 THEN 'Medium'
            ELSE 'Low'
        END as CONFIDENCE_LEVEL

    FROM TBL_DATA_QUALITY_METRICS
    WHERE MEASURED_DATE = CURRENT_DATE()
    GROUP BY TABLE_NAME, LAYER;

    RETURN 'DQ Scores calculated for ' || SQLROWCOUNT || ' tables';
END;
$$;

-- ============================================================================
-- SECTION 5: DATA QUALITY DASHBOARD VIEW
-- ============================================================================

CREATE OR REPLACE VIEW VW_DATA_QUALITY_DASHBOARD
COMMENT = 'Executive dashboard for data quality monitoring across all layers'
AS
SELECT
    -- Table identification
    s.TABLE_NAME as "Table Name",
    s.LAYER as "Layer",

    -- Overall quality
    s.OVERALL_DQ_SCORE as "Overall Data Quality Score",
    s.SCORE_GRADE as "Quality Grade",
    s.CONFIDENCE_LEVEL as "Confidence Level",

    -- Dimension scores
    s.COMPLETENESS_SCORE as "Completeness %",
    s.ACCURACY_SCORE as "Accuracy %",
    s.FRESHNESS_SCORE as "Freshness %",
    s.CONSISTENCY_SCORE as "Consistency %",
    s.VALIDITY_SCORE as "Validity %",

    -- Pass/Fail summary
    (SELECT COUNT(*) FROM TBL_DATA_QUALITY_METRICS m
     WHERE m.TABLE_NAME = s.TABLE_NAME AND m.STATUS = 'PASS' AND m.MEASURED_DATE = CURRENT_DATE()) as "Checks Passed",

    (SELECT COUNT(*) FROM TBL_DATA_QUALITY_METRICS m
     WHERE m.TABLE_NAME = s.TABLE_NAME AND m.STATUS = 'WARNING' AND m.MEASURED_DATE = CURRENT_DATE()) as "Warnings",

    (SELECT COUNT(*) FROM TBL_DATA_QUALITY_METRICS m
     WHERE m.TABLE_NAME = s.TABLE_NAME AND m.STATUS = 'FAIL' AND m.MEASURED_DATE = CURRENT_DATE()) as "Failures",

    -- Total issues
    (SELECT SUM(ISSUE_COUNT) FROM TBL_DATA_QUALITY_METRICS m
     WHERE m.TABLE_NAME = s.TABLE_NAME AND m.MEASURED_DATE = CURRENT_DATE()) as "Total Issues",

    -- Status indicator
    CASE
        WHEN s.OVERALL_DQ_SCORE >= 95 THEN '🟢 Excellent'
        WHEN s.OVERALL_DQ_SCORE >= 85 THEN '🟡 Good'
        WHEN s.OVERALL_DQ_SCORE >= 70 THEN '🟠 Fair'
        ELSE '🔴 Poor'
    END as "Status",

    -- Timestamp
    s.CALCULATED_AT as "Last Calculated"

FROM TBL_DATA_QUALITY_SCORES s
WHERE s.CALCULATED_DATE = CURRENT_DATE()
ORDER BY s.LAYER, s.OVERALL_DQ_SCORE DESC;

-- ============================================================================
-- SECTION 6: AUTOMATED DQ WORKFLOW
-- ============================================================================

-- Task to run DQ metrics daily
CREATE OR REPLACE TASK TASK_DAILY_DATA_QUALITY_METRICS
    WAREHOUSE = DEV_WH
    SCHEDULE = 'USING CRON 0 6 * * * UTC'  -- Daily at 6:00 AM UTC
    COMMENT = 'Calculate data quality metrics for all tables'
AS
    CALL SP_CALCULATE_DATA_QUALITY_METRICS();

-- Task to calculate DQ scores (runs after metrics)
CREATE OR REPLACE TASK TASK_DAILY_DATA_QUALITY_SCORES
    WAREHOUSE = DEV_WH
    AFTER TASK_DAILY_DATA_QUALITY_METRICS
    COMMENT = 'Calculate aggregated DQ scores from metrics'
AS
    CALL SP_CALCULATE_DQ_SCORES();

-- Enable tasks
ALTER TASK TASK_DAILY_DATA_QUALITY_SCORES RESUME;
ALTER TASK TASK_DAILY_DATA_QUALITY_METRICS RESUME;

-- ============================================================================
-- SECTION 7: ENHANCED KPI VIEWS WITH DQ SCORES
-- ============================================================================

CREATE OR REPLACE VIEW VW_KPI_WITH_DATA_QUALITY
COMMENT = 'KPI Master with integrated data quality scores for transparency'
AS
SELECT
    k.*,

    -- Add DQ scores
    dq.OVERALL_DQ_SCORE as "Data Quality Score",
    dq.SCORE_GRADE as "Data Quality Grade",
    dq.CONFIDENCE_LEVEL as "Confidence Level",

    -- Visual indicator
    CASE
        WHEN dq.OVERALL_DQ_SCORE >= 95 THEN '🟢'
        WHEN dq.OVERALL_DQ_SCORE >= 80 THEN '🟡'
        ELSE '🔴'
    END || ' ' || k.EDR_COVERAGE_ALL_PCT as "EDR Coverage (with DQ indicator)",

    CASE
        WHEN dq.OVERALL_DQ_SCORE >= 95 THEN '🟢'
        WHEN dq.OVERALL_DQ_SCORE >= 80 THEN '🟡'
        ELSE '🔴'
    END || ' ' || k.VULN_SCAN_COVERAGE_ALL_PCT as "Vuln Coverage (with DQ indicator)"

FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_KPI_MASTER k
LEFT JOIN TBL_DATA_QUALITY_SCORES dq
    ON dq.TABLE_NAME = 'TBL_KPI_MASTER'
    AND dq.CALCULATED_DATE = CURRENT_DATE();

-- ============================================================================
-- SECTION 8: TESTING AND VALIDATION
-- ============================================================================

-- Test 1: Calculate DQ metrics
CALL SP_CALCULATE_DATA_QUALITY_METRICS();

-- Test 2: Calculate DQ scores
CALL SP_CALCULATE_DQ_SCORES();

-- Test 3: View dashboard
SELECT * FROM VW_DATA_QUALITY_DASHBOARD;

-- Test 4: Check metric details
SELECT
    TABLE_NAME,
    LAYER,
    METRIC_NAME,
    METRIC_VALUE,
    STATUS,
    ISSUE_COUNT
FROM TBL_DATA_QUALITY_METRICS
WHERE MEASURED_DATE = CURRENT_DATE()
ORDER BY LAYER, TABLE_NAME, METRIC_NAME;

-- Test 5: Verify task creation
SHOW TASKS LIKE 'TASK_DAILY_DATA_QUALITY%';

-- ============================================================================
-- SUCCESS METRICS
-- ============================================================================
-- ✅ Data quality metrics table created
-- ✅ Configuration rules defined
-- ✅ Calculation procedures implemented
-- ✅ DQ scoring system operational
-- ✅ Dashboard view created
-- ✅ Automated daily tasks scheduled
-- ✅ KPI views enhanced with DQ indicators
-- ============================================================================
