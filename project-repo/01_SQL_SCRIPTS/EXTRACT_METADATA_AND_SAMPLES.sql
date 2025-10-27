/*
================================================================================
SECURITY_ANALYTICS Metadata and Sample Data Extraction
================================================================================

Purpose: Extract table metadata and create sample datasets for Streamlit development

This script:
1. Extracts comprehensive metadata for all service tables
2. Creates views with sample data (100 rows per table)
3. Generates summary statistics
4. Outputs can be downloaded as CSV for reference

Usage:
1. Run this script in Snowflake Worksheet
2. Download query results as CSV
3. Use metadata to build Streamlit apps

Author: GenericCorp Data Engineering Team
Date: October 2025
================================================================================
*/

USE ROLE SECURITY_ANALYTICS;
USE WAREHOUSE DEV_WH;

-- Create a temporary schema for samples
CREATE SCHEMA IF NOT EXISTS DEV_TRANSFORMATION.SAMPLES;

/*
================================================================================
SECTION 1: Extract Complete Metadata
================================================================================
*/

-- Comprehensive metadata for all SECURITY_ANALYTICS tables
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

    -- Categorize by service (based on table naming convention)
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

-- Query to view metadata
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
ORDER BY SERVICE_NAME, TABLE_NAME, ORDINAL_POSITION;

/*
================================================================================
SECTION 2: Service-Level Summary
================================================================================
*/

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

/*
================================================================================
SECTION 3: Column Statistics by Service
================================================================================
*/

CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_SERVICE_COLUMN_STATS AS
SELECT
    SERVICE_NAME,
    TABLE_NAME,
    COUNT(*) as COLUMN_COUNT,
    SUM(CASE WHEN IS_NULLABLE = 'YES' THEN 1 ELSE 0 END) as NULLABLE_COLUMNS,
    SUM(CASE WHEN DATA_TYPE LIKE '%VARCHAR%' THEN 1 ELSE 0 END) as TEXT_COLUMNS,
    SUM(CASE WHEN DATA_TYPE IN ('NUMBER', 'INTEGER', 'BIGINT', 'FLOAT') THEN 1 ELSE 0 END) as NUMERIC_COLUMNS,
    SUM(CASE WHEN DATA_TYPE IN ('DATE', 'TIMESTAMP', 'TIMESTAMP_NTZ', 'TIMESTAMP_TZ') THEN 1 ELSE 0 END) as DATE_COLUMNS,
    SUM(CASE WHEN DATA_TYPE = 'VARIANT' THEN 1 ELSE 0 END) as VARIANT_COLUMNS,
    SUM(CASE WHEN DATA_TYPE = 'BOOLEAN' THEN 1 ELSE 0 END) as BOOLEAN_COLUMNS
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
GROUP BY SERVICE_NAME, TABLE_NAME
ORDER BY SERVICE_NAME, TABLE_NAME;

-- View column stats
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SERVICE_COLUMN_STATS;

/*
================================================================================
SECTION 4: Create Sample Views (100 rows per table)
================================================================================
*/

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

-- Leviat Samples
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

/*
================================================================================
SECTION 5: Generate Table Profile Report
================================================================================
*/

CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SAMPLES.VW_TABLE_PROFILE_REPORT AS
SELECT
    DATABASE_NAME,
    SCHEMA_NAME,
    TABLE_NAME,
    SERVICE_NAME,
    DATA_LAYER,
    MAX(ROW_COUNT) as ROW_COUNT,
    MAX(BYTES) / 1024 / 1024 as SIZE_MB,
    COUNT(DISTINCT COLUMN_NAME) as COLUMN_COUNT,

    -- Column types summary
    LISTAGG(DISTINCT DATA_TYPE, ', ') WITHIN GROUP (ORDER BY DATA_TYPE) as DATA_TYPES_USED,

    -- Key columns (likely PKs or important fields)
    LISTAGG(
        CASE
            WHEN COLUMN_NAME LIKE '%_KEY' OR COLUMN_NAME LIKE '%_ID' THEN COLUMN_NAME
            ELSE NULL
        END,
        ', '
    ) WITHIN GROUP (ORDER BY ORDINAL_POSITION) as KEY_COLUMNS,

    -- Date columns
    LISTAGG(
        CASE
            WHEN DATA_TYPE LIKE '%TIMESTAMP%' OR DATA_TYPE LIKE '%DATE%' THEN COLUMN_NAME
            ELSE NULL
        END,
        ', '
    ) WITHIN GROUP (ORDER BY ORDINAL_POSITION) as DATE_COLUMNS,

    MAX(CREATED) as TABLE_CREATED,
    MAX(LAST_ALTERED) as LAST_MODIFIED

FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
GROUP BY DATABASE_NAME, SCHEMA_NAME, TABLE_NAME, SERVICE_NAME, DATA_LAYER
ORDER BY SERVICE_NAME, DATA_LAYER, TABLE_NAME;

-- View table profiles
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_TABLE_PROFILE_REPORT;

/*
================================================================================
SECTION 6: Export Instructions
================================================================================
*/

-- To export metadata for Streamlit development:

-- 1. Complete metadata for all tables
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA;
-- Download as: metadata_all_tables.csv

-- 2. Service summary
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SERVICE_SUMMARY;
-- Download as: service_summary.csv

-- 3. Table profile report (most useful for Streamlit development)
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_TABLE_PROFILE_REPORT;
-- Download as: table_profiles.csv

-- 4. Sample data for each service (query individual sample views)
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINELONE_ENDPOINTS;
-- Download as: sample_sentinelone_endpoints.csv

SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_TENABLE_FACT;
-- Download as: sample_tenable_fact.csv

-- ... repeat for other services

/*
================================================================================
SECTION 7: Cleanup (Optional)
================================================================================
*/

-- To remove sample schema after extraction:
-- DROP SCHEMA DEV_TRANSFORMATION.SAMPLES CASCADE;

/*
================================================================================
END OF SCRIPT
================================================================================

Next Steps:
1. Run each section sequentially
2. Download query results as CSV files
3. Use metadata to understand table structures
4. Reference sample data when building Streamlit queries
5. Update Streamlit apps with correct column names and data types

Notes:
- All views are created in DEV_TRANSFORMATION.SAMPLES schema
- Sample views contain only 100 rows for performance
- Metadata views provide complete schema information
- Export CSVs can be used offline for development reference
================================================================================
*/
