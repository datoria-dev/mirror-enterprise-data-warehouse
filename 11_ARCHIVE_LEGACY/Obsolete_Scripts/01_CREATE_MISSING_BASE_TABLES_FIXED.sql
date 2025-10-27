-- ============================================================================
-- CREATE MISSING BASE TABLES - FIXED VERSION
-- ============================================================================
-- Purpose: Create only the minimum tables needed for the 4 enhancements
-- Author: Data Engineering Team
-- Date: 2025-10-07
-- ============================================================================

USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;

-- ============================================================================
-- SECTION 1: DIM_OPCO (Operating Company Dimension)
-- ============================================================================

USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA SECURITY_ANALYTICS;

SELECT '=== Creating DIM_OPCO ===' AS STEP;

CREATE TABLE IF NOT EXISTS DIM_OPCO (
    OPCO_ID NUMBER PRIMARY KEY,
    OPCO_CODE VARCHAR(50),
    OPCO_NAME VARCHAR(100),
    REGION VARCHAR(50),
    DIVISION VARCHAR(100),
    COUNTRY VARCHAR(100),
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    CREATED_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'Operating Company Dimension - Master list of OpCos';

-- Insert sample data if empty
MERGE INTO DIM_OPCO AS target
USING (
    SELECT 1 AS OPCO_ID, 'OPCO_001' AS OPCO_CODE, 'Sample OpCo 1' AS OPCO_NAME,
           'North America' AS REGION, 'IT Security' AS DIVISION, 'USA' AS COUNTRY
    UNION ALL
    SELECT 2, 'OPCO_002', 'Sample OpCo 2', 'Europe', 'IT Security', 'UK'
    UNION ALL
    SELECT 3, 'OPCO_003', 'Sample OpCo 3', 'Asia Pacific', 'IT Security', 'Australia'
) AS source
ON target.OPCO_ID = source.OPCO_ID
WHEN NOT MATCHED THEN
    INSERT (OPCO_ID, OPCO_CODE, OPCO_NAME, REGION, DIVISION, COUNTRY)
    VALUES (source.OPCO_ID, source.OPCO_CODE, source.OPCO_NAME, source.REGION, source.DIVISION, source.COUNTRY);

SELECT 'DIM_OPCO created with ' || COUNT(*) || ' rows' AS RESULT FROM DIM_OPCO;

-- ============================================================================
-- SECTION 2: Update DIM_HOST to add OPCO_ID if missing
-- ============================================================================

SELECT '=== Updating DIM_HOST ===' AS STEP;

-- Add OPCO_ID column if it doesn't exist (will fail silently if exists)
ALTER TABLE DIM_HOST ADD COLUMN IF NOT EXISTS OPCO_ID NUMBER;
ALTER TABLE DIM_HOST ADD COLUMN IF NOT EXISTS PRIMARY_USER_ID VARCHAR(255);

-- Update existing hosts with a default OPCO_ID if null
UPDATE DIM_HOST
SET OPCO_ID = 1
WHERE OPCO_ID IS NULL;

SELECT 'DIM_HOST updated - ' || COUNT(*) || ' total hosts, ' ||
       COUNT(CASE WHEN OPCO_ID IS NOT NULL THEN 1 END) || ' linked to OpCos' AS RESULT
FROM DIM_HOST;

-- ============================================================================
-- SECTION 3: FACT_EDR (EDR Facts - Simplified)
-- ============================================================================

SELECT '=== Creating FACT_EDR ===' AS STEP;

CREATE TABLE IF NOT EXISTS FACT_EDR (
    EDR_KEY NUMBER AUTOINCREMENT PRIMARY KEY,
    DATE_KEY NUMBER,
    HOST_ID VARCHAR(255),
    ENDPOINT_ID VARCHAR(255),
    EDR_PLATFORM VARCHAR(50),
    AGENT_VERSION VARCHAR(50),
    AGENT_STATUS VARCHAR(50),
    LAST_SEEN_DATE TIMESTAMP,
    THREAT_COUNT NUMBER DEFAULT 0,
    THREAT_NAME VARCHAR(500),
    THREAT_TYPE VARCHAR(100),
    THREAT_STATUS VARCHAR(50),
    DETECTION_TIME TIMESTAMP,
    LOAD_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'EDR Facts - Endpoint protection status';

-- Insert sample data using data from DIM_HOST
INSERT INTO FACT_EDR (DATE_KEY, HOST_ID, ENDPOINT_ID, EDR_PLATFORM, AGENT_STATUS, LAST_SEEN_DATE)
WITH host_sample AS (
    SELECT HOSTNAME AS HOST_ID, ROW_NUMBER() OVER (ORDER BY HOSTNAME) AS rn
    FROM DIM_HOST
    LIMIT 10
)
SELECT
    TO_NUMBER(TO_CHAR(CURRENT_DATE(), 'YYYYMMDD')) AS DATE_KEY,
    HOST_ID,
    HOST_ID || '_EDR' AS ENDPOINT_ID,
    'CrowdStrike' AS EDR_PLATFORM,
    'Healthy' AS AGENT_STATUS,
    CURRENT_TIMESTAMP() AS LAST_SEEN_DATE
FROM host_sample
WHERE NOT EXISTS (SELECT 1 FROM FACT_EDR WHERE FACT_EDR.HOST_ID = host_sample.HOST_ID);

SELECT 'FACT_EDR created with ' || COUNT(*) || ' rows' AS RESULT FROM FACT_EDR;

-- ============================================================================
-- SECTION 4: FACT_QUALYS (Vulnerability Facts - Simplified)
-- ============================================================================

SELECT '=== Creating FACT_QUALYS ===' AS STEP;

CREATE TABLE IF NOT EXISTS FACT_QUALYS (
    QUALYS_KEY NUMBER AUTOINCREMENT PRIMARY KEY,
    DATE_KEY NUMBER,
    HOST_ID VARCHAR(255),
    VULN_ID VARCHAR(255),
    CVE_ID VARCHAR(50),
    VULN_TITLE VARCHAR(500),
    SEVERITY VARCHAR(50),
    CVSS_SCORE FLOAT,
    CRITICAL_VULNS NUMBER DEFAULT 0,
    HIGH_VULNS NUMBER DEFAULT 0,
    MEDIUM_VULNS NUMBER DEFAULT 0,
    LOW_VULNS NUMBER DEFAULT 0,
    TOTAL_VULNERABILITIES NUMBER DEFAULT 0,
    OLDEST_CRITICAL_VULN_AGE_DAYS NUMBER,
    FIRST_DETECTED_DATE DATE,
    IS_EXPLOITED_IN_WILD BOOLEAN DEFAULT FALSE,
    LOAD_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'Qualys Vulnerability Facts';

-- Insert sample data using data from DIM_HOST
INSERT INTO FACT_QUALYS (DATE_KEY, HOST_ID, VULN_ID, SEVERITY, CVSS_SCORE, CRITICAL_VULNS, HIGH_VULNS, TOTAL_VULNERABILITIES, FIRST_DETECTED_DATE)
WITH host_sample AS (
    SELECT HOSTNAME AS HOST_ID, ROW_NUMBER() OVER (ORDER BY HOSTNAME) AS rn
    FROM DIM_HOST
    LIMIT 10
)
SELECT
    TO_NUMBER(TO_CHAR(CURRENT_DATE(), 'YYYYMMDD')),
    HOST_ID,
    'VULN_' || rn,
    'HIGH',
    7.5,
    0,
    1,
    1,
    CURRENT_DATE()
FROM host_sample
WHERE NOT EXISTS (SELECT 1 FROM FACT_QUALYS WHERE FACT_QUALYS.HOST_ID = host_sample.HOST_ID);

SELECT 'FACT_QUALYS created with ' || COUNT(*) || ' rows' AS RESULT FROM FACT_QUALYS;

-- ============================================================================
-- SECTION 5: Additional FACT Tables (Simplified)
-- ============================================================================

SELECT '=== Creating FACT_PATCHES ===' AS STEP;

CREATE TABLE IF NOT EXISTS FACT_PATCHES (
    PATCH_KEY NUMBER AUTOINCREMENT PRIMARY KEY,
    DATE_KEY NUMBER,
    HOST_ID VARCHAR(255),
    OS_PATCH_LEVEL VARCHAR(100),
    MISSING_CRITICAL_PATCHES NUMBER DEFAULT 0,
    LAST_PATCH_DATE DATE,
    LOAD_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'Patch Management Facts';

SELECT 'FACT_PATCHES created' AS RESULT;

SELECT '=== Creating FACT_INCIDENTS ===' AS STEP;

CREATE TABLE IF NOT EXISTS FACT_INCIDENTS (
    INCIDENT_KEY NUMBER AUTOINCREMENT PRIMARY KEY,
    DATE_KEY NUMBER,
    HOST_ID VARCHAR(255),
    INCIDENT_ID VARCHAR(255),
    INCIDENT_TYPE VARCHAR(100),
    SEVERITY VARCHAR(50),
    STATUS VARCHAR(50),
    CREATED_DATE TIMESTAMP,
    RESOLVED_DATE TIMESTAMP,
    LOAD_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'Security Incidents Facts';

SELECT 'FACT_INCIDENTS created' AS RESULT;

-- ============================================================================
-- SECTION 6: TBL_KPI_MASTER (Reporting Layer)
-- ============================================================================

USE DATABASE DEV_REPORTING;
USE SCHEMA SECURITY_ANALYTICS;

SELECT '=== Creating TBL_KPI_MASTER ===' AS STEP;

CREATE TABLE IF NOT EXISTS TBL_KPI_MASTER (
    KPI_KEY NUMBER AUTOINCREMENT PRIMARY KEY,
    DATE_KEY NUMBER,
    OPCO_ID NUMBER,
    HOST_ID VARCHAR(255),

    -- Top 13 Executive Metrics
    CYBER_MATURITY_SCORE FLOAT,
    TOTAL_POLICY_EXCEPTIONS NUMBER,
    OVERDUE_EXCEPTIONS NUMBER,
    VENDOR_RISK_SCORE FLOAT,
    HIGH_RISK_VENDORS NUMBER,
    ACCESS_REVIEWS_COMPLETED_PCT FLOAT,

    EDR_COVERAGE_ALL_PCT FLOAT,
    EDR_COVERAGE_SOX_PCT FLOAT,
    TOTAL_ASSETS NUMBER,
    EDR_PROTECTED_ASSETS NUMBER,
    UNPROTECTED_ASSETS NUMBER,

    EMAIL_DOMAIN_SECURITY_PCT FLOAT,
    DMARC_COMPLIANT_DOMAINS NUMBER,

    PHISHING_CLICK_RATE_PCT FLOAT,
    PHISHING_SIMULATIONS_SENT NUMBER,
    PHISHING_CLICKS NUMBER,

    MEAN_TIME_TO_ENGAGE_HOURS FLOAT,

    VULN_SCAN_COVERAGE_ALL_PCT FLOAT,
    VULN_SCAN_COVERAGE_SOX_PCT FLOAT,
    VULN_SCAN_COVERAGE_SERVERS_PCT FLOAT,
    VULN_SCAN_COVERAGE_WORKSTATIONS_PCT FLOAT,
    VULN_SCAN_COVERAGE_DATABASES_PCT FLOAT,
    VULN_SCAN_COVERAGE_NETWORK_PCT FLOAT,

    -- Audit
    LOAD_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'Master KPI table for all security metrics';

-- Insert sample data if empty
INSERT INTO TBL_KPI_MASTER (
    DATE_KEY, OPCO_ID,
    EDR_COVERAGE_ALL_PCT, TOTAL_ASSETS, EDR_PROTECTED_ASSETS, UNPROTECTED_ASSETS,
    VULN_SCAN_COVERAGE_ALL_PCT, PHISHING_CLICK_RATE_PCT,
    EMAIL_DOMAIN_SECURITY_PCT, ACCESS_REVIEWS_COMPLETED_PCT,
    CYBER_MATURITY_SCORE, MEAN_TIME_TO_ENGAGE_HOURS
)
SELECT
    TO_NUMBER(TO_CHAR(CURRENT_DATE(), 'YYYYMMDD')),
    o.OPCO_ID,
    85.5,  -- EDR Coverage
    100,   -- Total Assets
    86,    -- EDR Protected
    14,    -- Unprotected
    78.2,  -- Vuln Scan Coverage
    3.5,   -- Phishing Click Rate
    92.0,  -- Email Security
    88.0,  -- Access Reviews
    3.2,   -- Cyber Maturity
    0.5    -- MTTE Hours
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_OPCO o
WHERE NOT EXISTS (
    SELECT 1 FROM TBL_KPI_MASTER
    WHERE DATE_KEY = TO_NUMBER(TO_CHAR(CURRENT_DATE(), 'YYYYMMDD'))
    AND OPCO_ID = o.OPCO_ID
);

SELECT 'TBL_KPI_MASTER created with ' || COUNT(*) || ' rows' AS RESULT FROM TBL_KPI_MASTER;

-- ============================================================================
-- SECTION 7: Create TBL_DATA_QUALITY_SCORES placeholder
-- ============================================================================

SELECT '=== Creating TBL_DATA_QUALITY_SCORES placeholder ===' AS STEP;

CREATE TABLE IF NOT EXISTS TBL_DATA_QUALITY_SCORES (
    SCORE_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    DATE_KEY NUMBER,
    OPCO_ID NUMBER,
    TABLE_NAME VARCHAR(255),
    LAYER VARCHAR(50),
    COMPLETENESS_SCORE FLOAT,
    ACCURACY_SCORE FLOAT,
    FRESHNESS_SCORE FLOAT,
    CONSISTENCY_SCORE FLOAT,
    VALIDITY_SCORE FLOAT,
    OVERALL_DQ_SCORE FLOAT,
    SCORE_GRADE VARCHAR(10),
    CONFIDENCE_LEVEL VARCHAR(20),
    CALCULATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    CALCULATED_DATE DATE DEFAULT CURRENT_DATE()
)
COMMENT = 'Placeholder for Data Quality Scores - will be populated by Enhancement 2';

SELECT 'TBL_DATA_QUALITY_SCORES created' AS RESULT;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA SECURITY_ANALYTICS;

SELECT '=== VERIFICATION - Checking all tables ===' AS STEP;

SELECT 'DEV_TRANSFORMATION.SECURITY_ANALYTICS' AS LOCATION, TABLE_NAME, ROW_COUNT
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND TABLE_NAME IN ('DIM_OPCO', 'DIM_HOST', 'FACT_EDR', 'FACT_QUALYS', 'FACT_PATCHES', 'FACT_INCIDENTS')
ORDER BY TABLE_NAME;

USE DATABASE DEV_REPORTING;
USE SCHEMA SECURITY_ANALYTICS;

SELECT 'DEV_REPORTING.SECURITY_ANALYTICS' AS LOCATION, TABLE_NAME, ROW_COUNT
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND TABLE_NAME IN ('TBL_KPI_MASTER', 'TBL_DATA_QUALITY_SCORES')
ORDER BY TABLE_NAME;

SELECT '=== SUCCESS! All base tables created ===' AS STEP;
SELECT 'You can now proceed with the 4 enhancements' AS NEXT_STEP;
SELECT 'Start with: 02_SQL_SCRIPTS\02_advanced_features\01_PowerBI_Integration_Layer.sql' AS NEXT_FILE;

-- ============================================================================
-- END OF BASE TABLES CREATION
-- ============================================================================
