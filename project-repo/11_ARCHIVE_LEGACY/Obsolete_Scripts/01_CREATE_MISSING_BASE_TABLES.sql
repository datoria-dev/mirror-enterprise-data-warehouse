-- ============================================================================
-- CREATE MISSING BASE TABLES (MINIMUM REQUIRED FOR ENHANCEMENTS)
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
INSERT INTO DIM_OPCO (OPCO_ID, OPCO_CODE, OPCO_NAME, REGION, DIVISION, COUNTRY)
SELECT 1, 'OPCO_001', 'Sample OpCo 1', 'North America', 'IT Security', 'USA'
WHERE NOT EXISTS (SELECT 1 FROM DIM_OPCO);

INSERT INTO DIM_OPCO (OPCO_ID, OPCO_CODE, OPCO_NAME, REGION, DIVISION, COUNTRY)
SELECT 2, 'OPCO_002', 'Sample OpCo 2', 'Europe', 'IT Security', 'UK'
WHERE NOT EXISTS (SELECT 1 FROM DIM_OPCO WHERE OPCO_ID = 2);

INSERT INTO DIM_OPCO (OPCO_ID, OPCO_CODE, OPCO_NAME, REGION, DIVISION, COUNTRY)
SELECT 3, 'OPCO_003', 'Sample OpCo 3', 'Asia Pacific', 'IT Security', 'Australia'
WHERE NOT EXISTS (SELECT 1 FROM DIM_OPCO WHERE OPCO_ID = 3);

SELECT 'DIM_OPCO created with ' || COUNT(*) || ' rows' AS RESULT FROM DIM_OPCO;

-- ============================================================================
-- SECTION 2: FACT_EDR (EDR Facts - Simplified)
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
    LOAD_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'EDR Facts - Endpoint protection status';

-- Insert sample data if empty
INSERT INTO FACT_EDR (DATE_KEY, HOST_ID, ENDPOINT_ID, EDR_PLATFORM, AGENT_STATUS, LAST_SEEN_DATE)
SELECT
    TO_NUMBER(TO_CHAR(CURRENT_DATE(), 'YYYYMMDD')),
    h.HOST_ID,
    h.HOST_ID || '_EDR',
    'CrowdStrike',
    'Healthy',
    CURRENT_TIMESTAMP()
FROM DIM_HOST h
WHERE NOT EXISTS (SELECT 1 FROM FACT_EDR)
LIMIT 10;

SELECT 'FACT_EDR created with ' || COUNT(*) || ' rows' AS RESULT FROM FACT_EDR;

-- ============================================================================
-- SECTION 3: FACT_QUALYS (Vulnerability Facts - Simplified)
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

-- Insert sample data if empty
INSERT INTO FACT_QUALYS (DATE_KEY, HOST_ID, VULN_ID, SEVERITY, CVSS_SCORE, CRITICAL_VULNS, HIGH_VULNS, TOTAL_VULNERABILITIES, FIRST_DETECTED_DATE)
SELECT
    TO_NUMBER(TO_CHAR(CURRENT_DATE(), 'YYYYMMDD')),
    h.HOST_ID,
    'VULN_' || UNIFORM(1000, 9999, RANDOM()),
    'HIGH',
    7.5,
    0,
    1,
    1,
    CURRENT_DATE()
FROM DIM_HOST h
WHERE NOT EXISTS (SELECT 1 FROM FACT_QUALYS)
LIMIT 10;

SELECT 'FACT_QUALYS created with ' || COUNT(*) || ' rows' AS RESULT FROM FACT_QUALYS;

-- ============================================================================
-- SECTION 4: Additional FACT Tables (Simplified)
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

-- ============================================================================
-- SECTION 5: TBL_KPI_MASTER (Reporting Layer)
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
    EDR_COVERAGE_ALL_PCT, TOTAL_ASSETS, EDR_PROTECTED_ASSETS,
    VULN_SCAN_COVERAGE_ALL_PCT, PHISHING_CLICK_RATE_PCT,
    EMAIL_DOMAIN_SECURITY_PCT, ACCESS_REVIEWS_COMPLETED_PCT,
    CYBER_MATURITY_SCORE
)
SELECT
    TO_NUMBER(TO_CHAR(CURRENT_DATE(), 'YYYYMMDD')),
    o.OPCO_ID,
    85.5,  -- EDR Coverage
    100,   -- Total Assets
    86,    -- EDR Protected
    78.2,  -- Vuln Scan Coverage
    3.5,   -- Phishing Click Rate
    92.0,  -- Email Security
    88.0,  -- Access Reviews
    3.2    -- Cyber Maturity
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_OPCO o
WHERE NOT EXISTS (SELECT 1 FROM TBL_KPI_MASTER);

SELECT 'TBL_KPI_MASTER created with ' || COUNT(*) || ' rows' AS RESULT FROM TBL_KPI_MASTER;

-- ============================================================================
-- SECTION 6: Link DIM_HOST with DIM_OPCO (if not already linked)
-- ============================================================================

USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA SECURITY_ANALYTICS;

SELECT '=== Updating DIM_HOST with OPCO_ID ===' AS STEP;

-- Check if OPCO_ID column exists in DIM_HOST
ALTER TABLE DIM_HOST ADD COLUMN OPCO_ID NUMBER;

-- Update existing hosts with a default OPCO_ID if null
UPDATE DIM_HOST
SET OPCO_ID = 1
WHERE OPCO_ID IS NULL
  AND EXISTS (SELECT 1 FROM DIM_OPCO WHERE OPCO_ID = 1);

SELECT 'DIM_HOST updated - ' || COUNT(*) || ' hosts linked to OpCos' AS RESULT
FROM DIM_HOST WHERE OPCO_ID IS NOT NULL;

-- ============================================================================
-- SECTION 7: Create PRIMARY_USER_ID column in DIM_HOST (for Enhancement 3)
-- ============================================================================

SELECT '=== Adding PRIMARY_USER_ID to DIM_HOST ===' AS STEP;

ALTER TABLE DIM_HOST ADD COLUMN PRIMARY_USER_ID VARCHAR(255);

-- ============================================================================
-- VERIFICATION
-- ============================================================================

SELECT '=== VERIFICATION - Checking all tables ===' AS STEP;

SELECT 'DIM_OPCO' AS TABLE_NAME, COUNT(*) AS ROW_COUNT FROM DIM_OPCO
UNION ALL
SELECT 'DIM_HOST', COUNT(*) FROM DIM_HOST
UNION ALL
SELECT 'FACT_EDR', COUNT(*) FROM FACT_EDR
UNION ALL
SELECT 'FACT_QUALYS', COUNT(*) FROM FACT_QUALYS
UNION ALL
SELECT 'FACT_PATCHES', COUNT(*) FROM FACT_PATCHES
UNION ALL
SELECT 'FACT_INCIDENTS', COUNT(*) FROM FACT_INCIDENTS
UNION ALL
SELECT 'TBL_KPI_MASTER', COUNT(*) FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_KPI_MASTER;

SELECT '=== SUCCESS! All base tables created ===' AS STEP;
SELECT 'You can now proceed with the 4 enhancements' AS NEXT_STEP;

-- ============================================================================
-- END OF BASE TABLES CREATION
-- ============================================================================
