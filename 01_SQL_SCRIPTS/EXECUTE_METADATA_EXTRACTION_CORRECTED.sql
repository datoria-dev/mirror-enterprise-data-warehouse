/*
================================================================================
SECURITY_ANALYTICS Metadata and Sample Data Extraction - CORRECTED VERSION
================================================================================

This script creates views for metadata and sample data using ACTUAL table names
discovered in the database.

IMPORTANT NOTES:
- Uses DEV_DEVELOPER role (not SECURITY_ANALYTICS)
- Uses actual table names found in discovery
- Handles missing services (Tenable has no tables)
- Creates views in DEV_TRANSFORMATION.SAMPLES schema

USAGE:
1. Execute each section step-by-step in VS Code Snowflake extension
2. After each section, verify results with SELECT * FROM view_name LIMIT 10;
3. Download CSV files from query results for offline reference

Based on Discovery Results:
- CybelAngel: DIM_CYBELANGEL_ALERTS (196 rows), FACT_CYBELANGEL_THREATS (0 rows)
- Leviat: Tables exist but mostly empty (0 rows)
- Proofpoint: PROOFPOINT_MESSAGE_LOGS (206,794 rows)
- SentinelOne: FACT_SENTINEL_ENDPOINTS (4,188 rows), DIM_SENTINEL_VERSIONS (38 rows)
- ServiceNow: SNOW (24,650 rows)
- Tenable: NO TABLES FOUND - SKIPPED

Author: GenericCorp Data Engineering Team
Date: 2025-10-24
================================================================================
*/

-- ============================================================================
-- STEP 1: SETUP - Use correct role and warehouse
-- ============================================================================

USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;

-- Create schema for samples if it doesn't exist
CREATE SCHEMA IF NOT EXISTS DEV_TRANSFORMATION.SAMPLES;

-- Verify setup
SELECT CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA();

-- ============================================================================
-- STEP 2: CREATE METADATA VIEWS
-- ============================================================================

-- -----------------------------------------------------------------------------
-- All Tables Metadata View
-- -----------------------------------------------------------------------------

CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA AS
SELECT
    c.TABLE_CATALOG as DATABASE_NAME,
    c.TABLE_SCHEMA as SCHEMA_NAME,
    c.TABLE_NAME,
    c.COLUMN_NAME,
    c.DATA_TYPE,
    c.IS_NULLABLE,
    c.COMMENT,
    c.ORDINAL_POSITION,
    -- Categorize by service based on actual table names
    CASE
        WHEN c.TABLE_NAME LIKE '%SENTINEL%' THEN 'SentinelOne'
        WHEN c.TABLE_NAME LIKE '%CYBELANGEL%' THEN 'CybelAngel'
        WHEN c.TABLE_NAME LIKE '%LEVIAT%' THEN 'Leviat'
        WHEN c.TABLE_NAME LIKE '%PROOFPOINT%' THEN 'Proofpoint'
        WHEN c.TABLE_NAME IN ('SNOW') THEN 'ServiceNow'
        ELSE 'Unknown'
    END as SERVICE_NAME,
    -- Categorize by layer
    CASE
        WHEN c.TABLE_CATALOG = 'DEV_LANDING' THEN 'Landing'
        WHEN c.TABLE_CATALOG = 'DEV_TRANSFORMATION' THEN 'Transformation'
        WHEN c.TABLE_CATALOG = 'DEV_REPORTING' THEN 'Reporting'
        ELSE 'Unknown'
    END as DATA_LAYER
FROM DEV_LANDING.INFORMATION_SCHEMA.COLUMNS c
WHERE c.TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND (
    c.TABLE_NAME LIKE '%SENTINEL%'
    OR c.TABLE_NAME LIKE '%CYBELANGEL%'
    OR c.TABLE_NAME LIKE '%LEVIAT%'
    OR c.TABLE_NAME LIKE '%PROOFPOINT%'
    OR c.TABLE_NAME IN ('SNOW')
  )
UNION ALL
SELECT
    c.TABLE_CATALOG as DATABASE_NAME,
    c.TABLE_SCHEMA as SCHEMA_NAME,
    c.TABLE_NAME,
    c.COLUMN_NAME,
    c.DATA_TYPE,
    c.IS_NULLABLE,
    c.COMMENT,
    c.ORDINAL_POSITION,
    CASE
        WHEN c.TABLE_NAME LIKE '%SENTINEL%' THEN 'SentinelOne'
        WHEN c.TABLE_NAME LIKE '%CYBELANGEL%' THEN 'CybelAngel'
        WHEN c.TABLE_NAME LIKE '%LEVIAT%' THEN 'Leviat'
        WHEN c.TABLE_NAME LIKE '%PROOFPOINT%' THEN 'Proofpoint'
        WHEN c.TABLE_NAME IN ('SNOW') THEN 'ServiceNow'
        ELSE 'Unknown'
    END as SERVICE_NAME,
    CASE
        WHEN c.TABLE_CATALOG = 'DEV_LANDING' THEN 'Landing'
        WHEN c.TABLE_CATALOG = 'DEV_TRANSFORMATION' THEN 'Transformation'
        WHEN c.TABLE_CATALOG = 'DEV_REPORTING' THEN 'Reporting'
        ELSE 'Unknown'
    END as DATA_LAYER
FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.COLUMNS c
WHERE c.TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND (
    c.TABLE_NAME LIKE '%SENTINEL%'
    OR c.TABLE_NAME LIKE '%CYBELANGEL%'
    OR c.TABLE_NAME LIKE '%LEVIAT%'
    OR c.TABLE_NAME LIKE '%PROOFPOINT%'
    OR c.TABLE_NAME IN ('SNOW')
  );

-- Verify metadata view
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
ORDER BY SERVICE_NAME, DATA_LAYER, TABLE_NAME, ORDINAL_POSITION
LIMIT 100;

-- Count columns by service
SELECT
    SERVICE_NAME,
    DATA_LAYER,
    TABLE_NAME,
    COUNT(*) as COLUMN_COUNT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
GROUP BY SERVICE_NAME, DATA_LAYER, TABLE_NAME
ORDER BY SERVICE_NAME, DATA_LAYER, TABLE_NAME;

-- ============================================================================
-- STEP 3: CREATE SAMPLE DATA VIEWS (100 rows per table)
-- ============================================================================

-- -----------------------------------------------------------------------------
-- SENTINELONE SAMPLES
-- -----------------------------------------------------------------------------

-- SentinelOne: FACT_SENTINEL_ENDPOINTS (4,188 rows)
CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINEL_ENDPOINTS AS
SELECT * FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_SENTINEL_ENDPOINTS
LIMIT 100;

-- SentinelOne: DIM_SENTINEL_VERSIONS (38 rows)
CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINEL_VERSIONS AS
SELECT * FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_SENTINEL_VERSIONS
LIMIT 100;

-- Verify SentinelOne samples
SELECT 'FACT_SENTINEL_ENDPOINTS' as TABLE_NAME, COUNT(*) as SAMPLE_COUNT
FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINEL_ENDPOINTS
UNION ALL
SELECT 'DIM_SENTINEL_VERSIONS', COUNT(*)
FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINEL_VERSIONS;

-- -----------------------------------------------------------------------------
-- CYBELANGEL SAMPLES
-- -----------------------------------------------------------------------------

-- CybelAngel: DIM_CYBELANGEL_ALERTS (196 rows)
CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_ALERTS AS
SELECT * FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_CYBELANGEL_ALERTS
LIMIT 100;

-- CybelAngel: FACT_CYBELANGEL_THREATS (0 rows)
CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_THREATS AS
SELECT * FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_CYBELANGEL_THREATS
LIMIT 100;

-- Verify CybelAngel samples
SELECT 'DIM_CYBELANGEL_ALERTS' as TABLE_NAME, COUNT(*) as SAMPLE_COUNT
FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_ALERTS
UNION ALL
SELECT 'FACT_CYBELANGEL_THREATS', COUNT(*)
FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_THREATS;

-- -----------------------------------------------------------------------------
-- LEVIAT SAMPLES
-- -----------------------------------------------------------------------------

-- Leviat: DIM_LEVIAT_USERS (0 rows)
CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_USERS AS
SELECT * FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_LEVIAT_USERS
LIMIT 100;

-- Leviat: DIM_LEVIAT_LIST_USERS (0 rows)
CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_LIST_USERS AS
SELECT * FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_LEVIAT_LIST_USERS
LIMIT 100;

-- Leviat: FACT_LEVIAT_SECURITY_EVENTS (0 rows)
CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_SECURITY_EVENTS AS
SELECT * FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_LEVIAT_SECURITY_EVENTS
LIMIT 100;

-- Verify Leviat samples
SELECT 'DIM_LEVIAT_USERS' as TABLE_NAME, COUNT(*) as SAMPLE_COUNT
FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_USERS
UNION ALL
SELECT 'DIM_LEVIAT_LIST_USERS', COUNT(*)
FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_LIST_USERS
UNION ALL
SELECT 'FACT_LEVIAT_SECURITY_EVENTS', COUNT(*)
FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_SECURITY_EVENTS;

-- -----------------------------------------------------------------------------
-- PROOFPOINT SAMPLES
-- -----------------------------------------------------------------------------

-- Proofpoint: PROOFPOINT_MESSAGE_LOGS (206,794 rows)
CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_PROOFPOINT_MESSAGE_LOGS AS
SELECT * FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.PROOFPOINT_MESSAGE_LOGS
LIMIT 100;

-- Proofpoint: L_PROOFPOINT_RAW (0 rows in landing)
CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_PROOFPOINT_RAW AS
SELECT * FROM DEV_LANDING.SECURITY_ANALYTICS.L_PROOFPOINT_RAW
LIMIT 100;

-- Verify Proofpoint samples
SELECT 'PROOFPOINT_MESSAGE_LOGS' as TABLE_NAME, COUNT(*) as SAMPLE_COUNT
FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_PROOFPOINT_MESSAGE_LOGS
UNION ALL
SELECT 'L_PROOFPOINT_RAW', COUNT(*)
FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_PROOFPOINT_RAW;

-- -----------------------------------------------------------------------------
-- SERVICENOW SAMPLES
-- -----------------------------------------------------------------------------

-- ServiceNow: SNOW (24,650 rows)
CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SERVICENOW_SNOW AS
SELECT * FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.SNOW
LIMIT 100;

-- Verify ServiceNow samples
SELECT 'SNOW' as TABLE_NAME, COUNT(*) as SAMPLE_COUNT
FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SERVICENOW_SNOW;

-- ============================================================================
-- STEP 4: CREATE SUMMARY VIEWS
-- ============================================================================

-- -----------------------------------------------------------------------------
-- Service Summary View
-- -----------------------------------------------------------------------------

CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SERVICE_SUMMARY AS
SELECT
    SERVICE_NAME,
    DATA_LAYER,
    TABLE_NAME,
    COUNT(DISTINCT COLUMN_NAME) as COLUMN_COUNT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
GROUP BY SERVICE_NAME, DATA_LAYER, TABLE_NAME
ORDER BY SERVICE_NAME, DATA_LAYER, TABLE_NAME;

-- View service summary
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SERVICE_SUMMARY;

-- -----------------------------------------------------------------------------
-- Data Type Distribution View
-- -----------------------------------------------------------------------------

CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_DATATYPE_DISTRIBUTION AS
SELECT
    SERVICE_NAME,
    DATA_TYPE,
    COUNT(*) as COLUMN_COUNT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
GROUP BY SERVICE_NAME, DATA_TYPE
ORDER BY SERVICE_NAME, DATA_TYPE;

-- View data type distribution
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_DATATYPE_DISTRIBUTION;

-- ============================================================================
-- STEP 5: EXPORT QUERIES - Run these to download CSV files
-- ============================================================================

-- NOTE: Execute each query below individually and download results as CSV
-- In VS Code Snowflake extension: Run query → Right-click results → Export to CSV

-- -----------------------------------------------------------------------------
-- Export Metadata
-- -----------------------------------------------------------------------------

-- Export: Complete metadata for all services
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
ORDER BY SERVICE_NAME, DATA_LAYER, TABLE_NAME, ORDINAL_POSITION;
-- Save as: metadata_all_services.csv

-- Export: Service summary
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SERVICE_SUMMARY;
-- Save as: metadata_service_summary.csv

-- -----------------------------------------------------------------------------
-- Export SentinelOne Samples
-- -----------------------------------------------------------------------------

SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINEL_ENDPOINTS;
-- Save as: sample_sentinel_endpoints.csv

SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINEL_VERSIONS;
-- Save as: sample_sentinel_versions.csv

-- -----------------------------------------------------------------------------
-- Export CybelAngel Samples
-- -----------------------------------------------------------------------------

SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_ALERTS;
-- Save as: sample_cybelangel_alerts.csv

SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_THREATS;
-- Save as: sample_cybelangel_threats.csv (will be empty)

-- -----------------------------------------------------------------------------
-- Export Leviat Samples
-- -----------------------------------------------------------------------------

SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_USERS;
-- Save as: sample_leviat_users.csv (will be empty)

SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_LIST_USERS;
-- Save as: sample_leviat_list_users.csv (will be empty)

SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_SECURITY_EVENTS;
-- Save as: sample_leviat_security_events.csv (will be empty)

-- -----------------------------------------------------------------------------
-- Export Proofpoint Samples
-- -----------------------------------------------------------------------------

SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_PROOFPOINT_MESSAGE_LOGS;
-- Save as: sample_proofpoint_message_logs.csv

SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_PROOFPOINT_RAW;
-- Save as: sample_proofpoint_raw.csv (will be empty)

-- -----------------------------------------------------------------------------
-- Export ServiceNow Samples
-- -----------------------------------------------------------------------------

SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SERVICENOW_SNOW;
-- Save as: sample_servicenow_snow.csv

-- ============================================================================
-- STEP 6: DETAILED METADATA BY SERVICE
-- ============================================================================

-- Get detailed metadata for each service to help build Streamlit apps

-- -----------------------------------------------------------------------------
-- SentinelOne Metadata
-- -----------------------------------------------------------------------------

SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    COMMENT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME = 'SentinelOne'
ORDER BY TABLE_NAME, ORDINAL_POSITION;
-- Save as: metadata_sentinelone.csv

-- -----------------------------------------------------------------------------
-- CybelAngel Metadata
-- -----------------------------------------------------------------------------

SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    COMMENT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME = 'CybelAngel'
ORDER BY TABLE_NAME, ORDINAL_POSITION;
-- Save as: metadata_cybelangel.csv

-- -----------------------------------------------------------------------------
-- Leviat Metadata
-- -----------------------------------------------------------------------------

SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    COMMENT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME = 'Leviat'
ORDER BY TABLE_NAME, ORDINAL_POSITION;
-- Save as: metadata_leviat.csv

-- -----------------------------------------------------------------------------
-- Proofpoint Metadata
-- -----------------------------------------------------------------------------

SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    COMMENT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME = 'Proofpoint'
ORDER BY TABLE_NAME, ORDINAL_POSITION;
-- Save as: metadata_proofpoint.csv

-- -----------------------------------------------------------------------------
-- ServiceNow Metadata
-- -----------------------------------------------------------------------------

SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    COMMENT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME = 'ServiceNow'
ORDER BY TABLE_NAME, ORDINAL_POSITION;
-- Save as: metadata_servicenow.csv

-- ============================================================================
-- STEP 7: VERIFICATION & VALIDATION
-- ============================================================================

-- Check all sample views were created
SELECT
    TABLE_SCHEMA,
    TABLE_NAME,
    TABLE_TYPE,
    ROW_COUNT,
    CREATED
FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SAMPLES'
  AND TABLE_NAME LIKE 'VW_SAMPLE_%'
ORDER BY TABLE_NAME;

-- Check metadata views
SELECT
    TABLE_SCHEMA,
    TABLE_NAME,
    TABLE_TYPE,
    CREATED
FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SAMPLES'
  AND TABLE_NAME LIKE 'VW_%'
ORDER BY TABLE_NAME;

-- Count rows in all sample views
SELECT 'VW_SAMPLE_SENTINEL_ENDPOINTS' as VIEW_NAME, COUNT(*) as ROW_COUNT FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINEL_ENDPOINTS
UNION ALL SELECT 'VW_SAMPLE_SENTINEL_VERSIONS', COUNT(*) FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINEL_VERSIONS
UNION ALL SELECT 'VW_SAMPLE_CYBELANGEL_ALERTS', COUNT(*) FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_ALERTS
UNION ALL SELECT 'VW_SAMPLE_CYBELANGEL_THREATS', COUNT(*) FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_THREATS
UNION ALL SELECT 'VW_SAMPLE_LEVIAT_USERS', COUNT(*) FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_USERS
UNION ALL SELECT 'VW_SAMPLE_LEVIAT_LIST_USERS', COUNT(*) FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_LIST_USERS
UNION ALL SELECT 'VW_SAMPLE_LEVIAT_SECURITY_EVENTS', COUNT(*) FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_SECURITY_EVENTS
UNION ALL SELECT 'VW_SAMPLE_PROOFPOINT_MESSAGE_LOGS', COUNT(*) FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_PROOFPOINT_MESSAGE_LOGS
UNION ALL SELECT 'VW_SAMPLE_PROOFPOINT_RAW', COUNT(*) FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_PROOFPOINT_RAW
UNION ALL SELECT 'VW_SAMPLE_SERVICENOW_SNOW', COUNT(*) FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SERVICENOW_SNOW
ORDER BY VIEW_NAME;

-- ============================================================================
-- STEP 8: CLEANUP (Optional - only if you want to remove everything)
-- ============================================================================

-- Uncomment below to drop all sample views and schema
/*
DROP SCHEMA IF EXISTS DEV_TRANSFORMATION.SAMPLES CASCADE;
*/

-- ============================================================================
-- NOTES FOR TENABLE
-- ============================================================================

/*
TENABLE SERVICE: NO TABLES FOUND

The discovery query found NO tables with "TENABLE" in the name.
This service appears to have no data loaded yet.

Expected tables (based on Streamlit app):
- DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_TENABLE
- DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_TENABLE_VULN
- DEV_LANDING.SECURITY_ANALYTICS.L_TENABLE_ASSETS

ACTION NEEDED:
1. Verify if Tenable integration is active
2. Check if data loading pipeline is configured
3. Confirm table naming conventions with data engineering team
4. Update Streamlit app once tables are created

For now, Tenable has been SKIPPED in this extraction script.
*/

-- ============================================================================
-- EXECUTION SUMMARY
-- ============================================================================

/*
WHAT THIS SCRIPT DOES:

1. Creates DEV_TRANSFORMATION.SAMPLES schema
2. Creates metadata view (VW_ALL_TABLE_METADATA) with all columns from all tables
3. Creates sample views (VW_SAMPLE_*) with 100 rows from each table
4. Creates summary views (VW_SERVICE_SUMMARY, VW_DATATYPE_DISTRIBUTION)
5. Provides export queries to download CSV files

TABLES PROCESSED:
✓ SentinelOne: FACT_SENTINEL_ENDPOINTS, DIM_SENTINEL_VERSIONS
✓ CybelAngel: DIM_CYBELANGEL_ALERTS, FACT_CYBELANGEL_THREATS
✓ Leviat: DIM_LEVIAT_USERS, DIM_LEVIAT_LIST_USERS, FACT_LEVIAT_SECURITY_EVENTS
✓ Proofpoint: PROOFPOINT_MESSAGE_LOGS, L_PROOFPOINT_RAW
✓ ServiceNow: SNOW
✗ Tenable: NO TABLES FOUND - SKIPPED

NEXT STEPS:
1. Run export queries in Step 5 and download CSV files
2. Save CSV files to 04_METADATA_SAMPLES/samples/ directory
3. Use metadata CSVs to update Streamlit apps with accurate column names
4. Review empty tables (Leviat, FACT_CYBELANGEL_THREATS) - may need sample data
5. Contact data engineering about Tenable integration status
*/
