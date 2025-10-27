/*
================================================================================
SECURITY_ANALYTICS Metadata Extraction - Simplified Execution Guide
================================================================================

This script provides step-by-step execution for metadata extraction.
Execute each section and verify results before proceeding.

Requirements:
- Connected to Snowflake (VS Code extension or Snowflake UI)
- Role: SECURITY_ANALYTICS
- Warehouse: DEV_WH

================================================================================
*/

-- ============================================================================
-- STEP 1: Setup
-- ============================================================================

USE ROLE SECURITY_ANALYTICS;
USE WAREHOUSE DEV_WH;

-- Verify connection
SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE();

-- Create schema for samples
CREATE SCHEMA IF NOT EXISTS DEV_TRANSFORMATION.SAMPLES;

-- Verify schema creation
SHOW SCHEMAS IN DATABASE DEV_TRANSFORMATION;

-- ============================================================================
-- STEP 2: Create Metadata View
-- ============================================================================

CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA AS
SELECT
    c.TABLE_CATALOG as DATABASE_NAME,
    c.TABLE_SCHEMA as SCHEMA_NAME,
    c.TABLE_NAME,
    c.COLUMN_NAME,
    c.ORDINAL_POSITION,
    c.DATA_TYPE,
    c.CHARACTER_MAXIMUM_LENGTH,
    c.NUMERIC_PRECISION,
    c.NUMERIC_SCALE,
    c.IS_NULLABLE,
    c.COLUMN_DEFAULT,
    c.COMMENT as COLUMN_COMMENT,

    -- Table-level info
    t.ROW_COUNT,
    t.BYTES,
    t.CREATED,
    t.LAST_ALTERED,

    -- Categorize by service
    CASE
        WHEN c.TABLE_NAME LIKE '%SENTINELONE%' OR c.TABLE_NAME LIKE '%SENTINEL%' THEN 'SentinelOne'
        WHEN c.TABLE_NAME LIKE '%TENABLE%' THEN 'Tenable'
        WHEN c.TABLE_NAME LIKE '%CYBELANGEL%' THEN 'CybelAngel'
        WHEN c.TABLE_NAME LIKE '%LEVIAT%' THEN 'Leviat'
        WHEN c.TABLE_NAME LIKE '%SNOW%' OR c.TABLE_NAME LIKE '%SERVICENOW%' THEN 'ServiceNow'
        WHEN c.TABLE_NAME LIKE '%PROOFPOINT%' THEN 'Proofpoint'
        WHEN c.TABLE_NAME LIKE '%CROWDSTRIKE%' OR c.TABLE_NAME LIKE '%EDR%' THEN 'CrowdStrike'
        WHEN c.TABLE_NAME LIKE '%QUALYS%' THEN 'Qualys'
        WHEN c.TABLE_NAME LIKE '%BITSIGHT%' THEN 'BitSight'
        WHEN c.TABLE_NAME LIKE '%ZEROFOX%' THEN 'ZeroFox'
        WHEN c.TABLE_NAME LIKE '%SPLUNK%' THEN 'Splunk'
        WHEN c.TABLE_NAME LIKE '%SOPHOS%' THEN 'Sophos'
        WHEN c.TABLE_NAME LIKE '%SYMANTEC%' THEN 'Symantec'
        WHEN c.TABLE_NAME LIKE '%TRELLIX%' THEN 'Trellix'
        WHEN c.TABLE_NAME LIKE '%ANCON%' THEN 'Ancon'
        ELSE 'Other'
    END as SERVICE_NAME,

    -- Categorize by layer
    CASE
        WHEN c.TABLE_CATALOG = 'DEV_LANDING' THEN 'Landing'
        WHEN c.TABLE_CATALOG = 'DEV_TRANSFORMATION' THEN 'Transformation'
        WHEN c.TABLE_CATALOG = 'DEV_REPORTING' THEN 'Reporting'
        ELSE 'Unknown'
    END as DATA_LAYER

FROM (
    SELECT * FROM DEV_LANDING.INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'

    UNION ALL

    SELECT * FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
) c

LEFT JOIN (
    SELECT TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME, ROW_COUNT, BYTES, CREATED, LAST_ALTERED
    FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'

    UNION ALL

    SELECT TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME, ROW_COUNT, BYTES, CREATED, LAST_ALTERED
    FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
) t
ON c.TABLE_CATALOG = t.TABLE_CATALOG
   AND c.TABLE_SCHEMA = t.TABLE_SCHEMA
   AND c.TABLE_NAME = t.TABLE_NAME

ORDER BY SERVICE_NAME, DATA_LAYER, c.TABLE_NAME, c.ORDINAL_POSITION;

-- ============================================================================
-- STEP 3: Verify Metadata View
-- ============================================================================

-- Count total columns extracted
SELECT COUNT(*) as TOTAL_COLUMNS_EXTRACTED
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA;

-- Count by service
SELECT
    SERVICE_NAME,
    COUNT(DISTINCT TABLE_NAME) as TABLE_COUNT,
    COUNT(*) as COLUMN_COUNT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
GROUP BY SERVICE_NAME
ORDER BY SERVICE_NAME;

-- ============================================================================
-- STEP 4: Create Service Summary View
-- ============================================================================

CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SERVICE_SUMMARY AS
SELECT
    SERVICE_NAME,
    DATA_LAYER,
    COUNT(DISTINCT TABLE_NAME) as TABLE_COUNT,
    SUM(ROW_COUNT) as TOTAL_ROWS,
    ROUND(SUM(BYTES) / 1024 / 1024 / 1024, 2) as TOTAL_SIZE_GB,
    COUNT(DISTINCT COLUMN_NAME) as TOTAL_COLUMNS
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
GROUP BY SERVICE_NAME, DATA_LAYER
ORDER BY SERVICE_NAME, DATA_LAYER;

-- View summary
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SERVICE_SUMMARY;

-- ============================================================================
-- STEP 5: Create Table Profile Report
-- ============================================================================

CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_TABLE_PROFILE_REPORT AS
SELECT
    DATABASE_NAME,
    SCHEMA_NAME,
    TABLE_NAME,
    SERVICE_NAME,
    DATA_LAYER,
    MAX(ROW_COUNT) as ROW_COUNT,
    ROUND(MAX(BYTES) / 1024 / 1024, 2) as SIZE_MB,
    COUNT(DISTINCT COLUMN_NAME) as COLUMN_COUNT,

    -- Column types summary
    LISTAGG(DISTINCT DATA_TYPE, ', ') WITHIN GROUP (ORDER BY DATA_TYPE) as DATA_TYPES_USED,

    -- Key columns
    LISTAGG(
        CASE
            WHEN COLUMN_NAME LIKE '%_KEY' OR COLUMN_NAME LIKE '%_ID' THEN COLUMN_NAME
            ELSE NULL
        END,
        ', '
    ) WITHIN GROUP (ORDER BY ORDINAL_POSITION) as KEY_COLUMNS,

    MAX(CREATED) as TABLE_CREATED,
    MAX(LAST_ALTERED) as LAST_MODIFIED

FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
GROUP BY DATABASE_NAME, SCHEMA_NAME, TABLE_NAME, SERVICE_NAME, DATA_LAYER
ORDER BY SERVICE_NAME, DATA_LAYER, TABLE_NAME;

-- View profiles
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_TABLE_PROFILE_REPORT
ORDER BY SERVICE_NAME, TABLE_NAME;

-- ============================================================================
-- STEP 6: Create Sample Data Views for NEW Services
-- ============================================================================

-- SentinelOne Samples
CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINELONE_ENDPOINTS AS
SELECT * FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_SENTINEL_ENDPOINTS LIMIT 100;

CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINEL_VERSIONS AS
SELECT * FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_SENTINEL_VERSIONS LIMIT 100;

-- Tenable Samples
CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_TENABLE_FACT AS
SELECT * FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_TENABLE LIMIT 100;

CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_TENABLE_VULN AS
SELECT * FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_TENABLE_VULN LIMIT 100;

-- CybelAngel Samples
CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_THREATS AS
SELECT * FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_CYBELANGEL_THREATS LIMIT 100;

CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_ALERTS AS
SELECT * FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_CYBELANGEL_ALERTS LIMIT 100;

-- Leviat Samples (may be empty)
CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_USERS AS
SELECT * FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_LEVIAT_USERS LIMIT 100;

CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_EVENTS AS
SELECT * FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_LEVIAT_SECURITY_EVENTS LIMIT 100;

-- ServiceNow Samples
CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SNOW_INCIDENT AS
SELECT * FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_SNOW_INCIDENT LIMIT 100;

CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SNOW_DEVICE AS
SELECT * FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_SNOW_DEVICE LIMIT 100;

CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SNOW_CHANGE AS
SELECT * FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_SNOW_CHANGE LIMIT 100;

-- Proofpoint Samples
CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_PROOFPOINT_RAW AS
SELECT * FROM DEV_LANDING.SECURITY_ANALYTICS.L_PROOFPOINT_RAW LIMIT 100;

-- ============================================================================
-- STEP 7: Verify All Sample Views
-- ============================================================================

-- List all created sample views
SHOW VIEWS IN SCHEMA DEV_TRANSFORMATION.SAMPLES;

-- Count rows in each sample view
SELECT 'SentinelOne Endpoints' as VIEW_NAME, COUNT(*) as ROW_COUNT
FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINELONE_ENDPOINTS
UNION ALL
SELECT 'Tenable Facts', COUNT(*)
FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_TENABLE_FACT
UNION ALL
SELECT 'CybelAngel Threats', COUNT(*)
FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_THREATS
UNION ALL
SELECT 'Leviat Users', COUNT(*)
FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_USERS
UNION ALL
SELECT 'ServiceNow Incidents', COUNT(*)
FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SNOW_INCIDENT
UNION ALL
SELECT 'Proofpoint Raw', COUNT(*)
FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_PROOFPOINT_RAW;

-- ============================================================================
-- STEP 8: Download Data for Offline Use
-- ============================================================================

-- Instructions to download as CSV:
-- 1. Run each query below
-- 2. Click "Download" or "Export" button in Snowflake UI
-- 3. Save as CSV with descriptive name

-- QUERY 1: Complete Metadata (most important)
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME IN ('SentinelOne', 'Tenable', 'CybelAngel', 'Leviat', 'ServiceNow', 'Proofpoint')
ORDER BY SERVICE_NAME, TABLE_NAME, ORDINAL_POSITION;
-- Save as: metadata_new_services.csv

-- QUERY 2: Service Summary
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SERVICE_SUMMARY
WHERE SERVICE_NAME IN ('SentinelOne', 'Tenable', 'CybelAngel', 'Leviat', 'ServiceNow', 'Proofpoint');
-- Save as: service_summary.csv

-- QUERY 3: Table Profiles
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_TABLE_PROFILE_REPORT
WHERE SERVICE_NAME IN ('SentinelOne', 'Tenable', 'CybelAngel', 'Leviat', 'ServiceNow', 'Proofpoint');
-- Save as: table_profiles.csv

-- QUERY 4: Sample Data - SentinelOne
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINELONE_ENDPOINTS;
-- Save as: sample_sentinelone_endpoints.csv

-- QUERY 5: Sample Data - Tenable
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_TENABLE_FACT;
-- Save as: sample_tenable_fact.csv

-- QUERY 6: Sample Data - CybelAngel
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_THREATS;
-- Save as: sample_cybelangel_threats.csv

-- QUERY 7: Sample Data - Leviat
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_USERS;
-- Save as: sample_leviat_users.csv

-- QUERY 8: Sample Data - ServiceNow
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SNOW_INCIDENT;
-- Save as: sample_servicenow_incidents.csv

-- QUERY 9: Sample Data - Proofpoint
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_PROOFPOINT_RAW;
-- Save as: sample_proofpoint_raw.csv

-- ============================================================================
-- STEP 9: Quick Metadata Lookup by Service
-- ============================================================================

-- Get all columns for SentinelOne tables
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_COMMENT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME = 'SentinelOne'
ORDER BY TABLE_NAME, ORDINAL_POSITION;

-- Get all columns for Tenable tables
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_COMMENT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME = 'Tenable'
ORDER BY TABLE_NAME, ORDINAL_POSITION;

-- Get all columns for CybelAngel tables
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_COMMENT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME = 'CybelAngel'
ORDER BY TABLE_NAME, ORDINAL_POSITION;

-- ============================================================================
-- STEP 10: Execution Summary
-- ============================================================================

SELECT '✓ Metadata Extraction Complete' as STATUS;

SELECT
    'Total Services' as METRIC,
    COUNT(DISTINCT SERVICE_NAME) as VALUE
FROM DEV_TRANSFORMATION.SAMPLES.VW_SERVICE_SUMMARY
UNION ALL
SELECT
    'Total Tables',
    COUNT(DISTINCT TABLE_NAME)
FROM DEV_TRANSFORMATION.SAMPLES.VW_TABLE_PROFILE_REPORT
UNION ALL
SELECT
    'Total Columns Documented',
    COUNT(*)
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
UNION ALL
SELECT
    'Sample Views Created',
    COUNT(*)
FROM INFORMATION_SCHEMA.VIEWS
WHERE TABLE_SCHEMA = 'SAMPLES'
  AND TABLE_NAME LIKE 'VW_SAMPLE%';

/*
================================================================================
NEXT STEPS
================================================================================

1. Download CSV files from queries above
2. Save them to: 04_METADATA_SAMPLES/samples/
3. Review sample data to understand structure
4. Use metadata to update Streamlit apps
5. Reference actual column names in queries

Example Usage in Streamlit:
---------------------------
From metadata, you now know exact column names:
- FACT_SENTINEL_ENDPOINTS has: EVENT_TIMESTAMP, THREAT_SEVERITY, ENDPOINT_NAME
- FACT_TENABLE has: SCAN_DATE, CVSS_SCORE, ASSET_HOSTNAME
- FACT_CYBELANGEL_THREATS has: DETECTION_DATE, THREAT_TYPE, SEVERITY

Use these in your Streamlit queries instead of guessing!

================================================================================
*/
