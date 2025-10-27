/*
================================================================================
Save Column Metadata to Files - Using SQL COPY INTO
================================================================================

This script creates temporary tables with metadata and shows you how to
export them to CSV files using the Snowflake UI.

IMPORTANT: Execute step by step and export each result manually.

Date: 2025-10-24
================================================================================
*/

USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;
USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA SAMPLES;

-- ============================================================================
-- STEP 1: Create Metadata Storage Tables
-- ============================================================================

-- Create schema for metadata storage
CREATE SCHEMA IF NOT EXISTS DEV_TRANSFORMATION.METADATA_EXPORTS;

-- ============================================================================
-- STEP 2: Save SentinelOne Metadata
-- ============================================================================

-- Table 1: FACT_SENTINEL_ENDPOINTS
CREATE OR REPLACE TABLE DEV_TRANSFORMATION.METADATA_EXPORTS.SENTINELONE_ENDPOINTS_COLUMNS AS
SELECT
    'FACT_SENTINEL_ENDPOINTS' as TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    COMMENT,
    CURRENT_TIMESTAMP() as EXTRACTED_AT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE TABLE_NAME = 'FACT_SENTINEL_ENDPOINTS'
ORDER BY ORDINAL_POSITION;

-- View results
SELECT * FROM DEV_TRANSFORMATION.METADATA_EXPORTS.SENTINELONE_ENDPOINTS_COLUMNS;
-- ✅ Execute this query, then: Right-click → Export → Save as CSV
-- Save as: 04_METADATA_SAMPLES/metadata/sentinelone_endpoints_columns.csv

-- Table 2: DIM_SENTINEL_VERSIONS
CREATE OR REPLACE TABLE DEV_TRANSFORMATION.METADATA_EXPORTS.SENTINELONE_VERSIONS_COLUMNS AS
SELECT
    'DIM_SENTINEL_VERSIONS' as TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    COMMENT,
    CURRENT_TIMESTAMP() as EXTRACTED_AT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE TABLE_NAME = 'DIM_SENTINEL_VERSIONS'
ORDER BY ORDINAL_POSITION;

SELECT * FROM DEV_TRANSFORMATION.METADATA_EXPORTS.SENTINELONE_VERSIONS_COLUMNS;
-- Save as: 04_METADATA_SAMPLES/metadata/sentinelone_versions_columns.csv

-- ============================================================================
-- STEP 3: Save CybelAngel Metadata
-- ============================================================================

CREATE OR REPLACE TABLE DEV_TRANSFORMATION.METADATA_EXPORTS.CYBELANGEL_ALERTS_COLUMNS AS
SELECT
    'DIM_CYBELANGEL_ALERTS' as TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    COMMENT,
    CURRENT_TIMESTAMP() as EXTRACTED_AT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE TABLE_NAME = 'DIM_CYBELANGEL_ALERTS'
ORDER BY ORDINAL_POSITION;

SELECT * FROM DEV_TRANSFORMATION.METADATA_EXPORTS.CYBELANGEL_ALERTS_COLUMNS;
-- Save as: 04_METADATA_SAMPLES/metadata/cybelangel_alerts_columns.csv

-- ============================================================================
-- STEP 4: Save Proofpoint Metadata
-- ============================================================================

CREATE OR REPLACE TABLE DEV_TRANSFORMATION.METADATA_EXPORTS.PROOFPOINT_MESSAGES_COLUMNS AS
SELECT
    'PROOFPOINT_MESSAGE_LOGS' as TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    COMMENT,
    CURRENT_TIMESTAMP() as EXTRACTED_AT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE TABLE_NAME = 'PROOFPOINT_MESSAGE_LOGS'
ORDER BY ORDINAL_POSITION;

SELECT * FROM DEV_TRANSFORMATION.METADATA_EXPORTS.PROOFPOINT_MESSAGES_COLUMNS;
-- Save as: 04_METADATA_SAMPLES/metadata/proofpoint_messages_columns.csv

-- ============================================================================
-- STEP 5: Save ServiceNow Metadata
-- ============================================================================

CREATE OR REPLACE TABLE DEV_TRANSFORMATION.METADATA_EXPORTS.SERVICENOW_SNOW_COLUMNS AS
SELECT
    'SNOW' as TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    COMMENT,
    CURRENT_TIMESTAMP() as EXTRACTED_AT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE TABLE_NAME = 'SNOW'
ORDER BY ORDINAL_POSITION;

SELECT * FROM DEV_TRANSFORMATION.METADATA_EXPORTS.SERVICENOW_SNOW_COLUMNS;
-- Save as: 04_METADATA_SAMPLES/metadata/servicenow_snow_columns.csv

-- ============================================================================
-- STEP 6: Save Leviat Metadata
-- ============================================================================

-- Table 1: DIM_LEVIAT_USERS
CREATE OR REPLACE TABLE DEV_TRANSFORMATION.METADATA_EXPORTS.LEVIAT_USERS_COLUMNS AS
SELECT
    'DIM_LEVIAT_USERS' as TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    COMMENT,
    CURRENT_TIMESTAMP() as EXTRACTED_AT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE TABLE_NAME = 'DIM_LEVIAT_USERS'
ORDER BY ORDINAL_POSITION;

SELECT * FROM DEV_TRANSFORMATION.METADATA_EXPORTS.LEVIAT_USERS_COLUMNS;
-- Save as: 04_METADATA_SAMPLES/metadata/leviat_users_columns.csv

-- Table 2: FACT_LEVIAT_SECURITY_EVENTS
CREATE OR REPLACE TABLE DEV_TRANSFORMATION.METADATA_EXPORTS.LEVIAT_EVENTS_COLUMNS AS
SELECT
    'FACT_LEVIAT_SECURITY_EVENTS' as TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    COMMENT,
    CURRENT_TIMESTAMP() as EXTRACTED_AT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE TABLE_NAME = 'FACT_LEVIAT_SECURITY_EVENTS'
ORDER BY ORDINAL_POSITION;

SELECT * FROM DEV_TRANSFORMATION.METADATA_EXPORTS.LEVIAT_EVENTS_COLUMNS;
-- Save as: 04_METADATA_SAMPLES/metadata/leviat_events_columns.csv

-- ============================================================================
-- STEP 7: Create Combined Metadata View
-- ============================================================================

CREATE OR REPLACE TABLE DEV_TRANSFORMATION.METADATA_EXPORTS.ALL_SERVICES_METADATA AS
SELECT
    SERVICE_NAME,
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    COMMENT,
    CURRENT_TIMESTAMP() as EXTRACTED_AT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME IN ('SentinelOne', 'CybelAngel', 'Proofpoint', 'ServiceNow', 'Leviat')
  AND TABLE_NAME IN (
    'FACT_SENTINEL_ENDPOINTS',
    'DIM_SENTINEL_VERSIONS',
    'DIM_CYBELANGEL_ALERTS',
    'FACT_CYBELANGEL_THREATS',
    'PROOFPOINT_MESSAGE_LOGS',
    'L_PROOFPOINT_RAW',
    'SNOW',
    'DIM_LEVIAT_USERS',
    'DIM_LEVIAT_LIST_USERS',
    'FACT_LEVIAT_SECURITY_EVENTS'
  )
ORDER BY SERVICE_NAME, TABLE_NAME, ORDINAL_POSITION;

SELECT * FROM DEV_TRANSFORMATION.METADATA_EXPORTS.ALL_SERVICES_METADATA;
-- Save as: 04_METADATA_SAMPLES/metadata/all_services_metadata.csv

-- ============================================================================
-- STEP 8: Create Summary Statistics
-- ============================================================================

CREATE OR REPLACE TABLE DEV_TRANSFORMATION.METADATA_EXPORTS.METADATA_SUMMARY AS
SELECT
    SERVICE_NAME,
    TABLE_NAME,
    COUNT(DISTINCT COLUMN_NAME) as COLUMN_COUNT,
    MIN(DATA_TYPE) as SAMPLE_DATA_TYPE,
    CURRENT_TIMESTAMP() as EXTRACTED_AT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME IN ('SentinelOne', 'CybelAngel', 'Proofpoint', 'ServiceNow', 'Leviat')
GROUP BY SERVICE_NAME, TABLE_NAME
ORDER BY SERVICE_NAME, TABLE_NAME;

SELECT * FROM DEV_TRANSFORMATION.METADATA_EXPORTS.METADATA_SUMMARY;
-- Save as: 04_METADATA_SAMPLES/metadata/metadata_summary.csv

-- ============================================================================
-- STEP 9: Verify All Tables Created
-- ============================================================================

SELECT
    TABLE_NAME,
    ROW_COUNT,
    CREATED
FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'METADATA_EXPORTS'
ORDER BY TABLE_NAME;

-- ============================================================================
-- STEP 10: Quick JSON Export (Copy result to .json file)
-- ============================================================================

-- Get column list as JSON for each service
SELECT
    SERVICE_NAME,
    TABLE_NAME,
    ARRAY_AGG(
        OBJECT_CONSTRUCT(
            'column_name', COLUMN_NAME,
            'data_type', DATA_TYPE,
            'is_nullable', IS_NULLABLE,
            'ordinal_position', ORDINAL_POSITION
        )
    ) WITHIN GROUP (ORDER BY ORDINAL_POSITION) as COLUMNS
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME IN ('SentinelOne', 'CybelAngel', 'Proofpoint', 'ServiceNow', 'Leviat')
  AND TABLE_NAME IN (
    'FACT_SENTINEL_ENDPOINTS',
    'DIM_SENTINEL_VERSIONS',
    'DIM_CYBELANGEL_ALERTS',
    'PROOFPOINT_MESSAGE_LOGS',
    'SNOW',
    'DIM_LEVIAT_USERS',
    'FACT_LEVIAT_SECURITY_EVENTS'
  )
GROUP BY SERVICE_NAME, TABLE_NAME
ORDER BY SERVICE_NAME, TABLE_NAME;

-- Copy result and save as: 04_METADATA_SAMPLES/json/services_metadata.json

-- ============================================================================
-- CLEANUP (Optional - run only if you want to remove temporary tables)
-- ============================================================================

/*
DROP SCHEMA IF EXISTS DEV_TRANSFORMATION.METADATA_EXPORTS CASCADE;
*/

-- ============================================================================
-- SUMMARY
-- ============================================================================

/*
FILES TO EXPORT (9 CSV files):

1. sentinelone_endpoints_columns.csv
2. sentinelone_versions_columns.csv
3. cybelangel_alerts_columns.csv
4. proofpoint_messages_columns.csv
5. servicenow_snow_columns.csv
6. leviat_users_columns.csv
7. leviat_events_columns.csv
8. all_services_metadata.csv (combined)
9. metadata_summary.csv (statistics)

NEXT STEPS:
1. Execute each CREATE TABLE and SELECT statement
2. Export each result as CSV
3. Use these CSV files to update Streamlit apps with correct column names
*/
