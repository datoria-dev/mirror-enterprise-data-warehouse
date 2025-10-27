/*
================================================================================
Export Metadata and Samples to CSV Files
================================================================================

Execute each query individually and download as CSV from VS Code Snowflake extension.

Instructions:
1. Select a query
2. Execute it (F5 or Run button)
3. Right-click on results → Export Results → Save as CSV
4. Save to: 04_METADATA_SAMPLES/samples/ directory

Date: 2025-10-24
================================================================================
*/

USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;

-- ============================================================================
-- PRIORITY 1: COMPLETE METADATA (ALL SERVICES)
-- ============================================================================

-- Export: Complete metadata for all services and all columns
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
ORDER BY SERVICE_NAME, DATA_LAYER, TABLE_NAME, ORDINAL_POSITION;
-- Save as: metadata_all_services.csv

-- ============================================================================
-- PRIORITY 2: SERVICE SUMMARY
-- ============================================================================

-- Export: Service summary (tables and column counts)
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SERVICE_SUMMARY;
-- Save as: metadata_service_summary.csv

-- ============================================================================
-- PRIORITY 3: SENTINELONE SAMPLES (100 + 38 rows)
-- ============================================================================

-- SentinelOne: Endpoints sample
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINEL_ENDPOINTS;
-- Save as: sample_sentinel_endpoints.csv

-- SentinelOne: Versions sample
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINEL_VERSIONS;
-- Save as: sample_sentinel_versions.csv

-- SentinelOne: Metadata only
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

-- ============================================================================
-- PRIORITY 4: CYBELANGEL SAMPLES (100 rows)
-- ============================================================================

-- CybelAngel: Alerts sample
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_ALERTS;
-- Save as: sample_cybelangel_alerts.csv

-- CybelAngel: Threats sample (empty but shows structure)
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_THREATS;
-- Save as: sample_cybelangel_threats.csv

-- CybelAngel: Metadata only
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

-- ============================================================================
-- PRIORITY 5: PROOFPOINT SAMPLES (100 rows)
-- ============================================================================

-- Proofpoint: Message logs sample
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_PROOFPOINT_MESSAGE_LOGS;
-- Save as: sample_proofpoint_message_logs.csv

-- Proofpoint: Raw data sample (empty but shows structure)
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_PROOFPOINT_RAW;
-- Save as: sample_proofpoint_raw.csv

-- Proofpoint: Metadata only
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

-- ============================================================================
-- PRIORITY 6: SERVICENOW SAMPLES (100 rows)
-- ============================================================================

-- ServiceNow: SNOW table sample
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SERVICENOW_SNOW;
-- Save as: sample_servicenow_snow.csv

-- ServiceNow: Metadata only
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
-- PRIORITY 7: LEVIAT SAMPLES (empty tables but shows structure)
-- ============================================================================

-- Leviat: Users sample (empty)
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_USERS;
-- Save as: sample_leviat_users.csv

-- Leviat: List users sample (empty)
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_LIST_USERS;
-- Save as: sample_leviat_list_users.csv

-- Leviat: Security events sample (empty)
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_SECURITY_EVENTS;
-- Save as: sample_leviat_security_events.csv

-- Leviat: Metadata only
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

-- ============================================================================
-- SUMMARY: FILES TO EXPORT
-- ============================================================================

/*
COMPLETE LIST OF CSV FILES TO CREATE:

METADATA FILES (7):
✓ metadata_all_services.csv         - Complete metadata for all services
✓ metadata_service_summary.csv      - Summary by service
✓ metadata_sentinelone.csv          - SentinelOne columns
✓ metadata_cybelangel.csv           - CybelAngel columns
✓ metadata_proofpoint.csv           - Proofpoint columns
✓ metadata_servicenow.csv           - ServiceNow columns
✓ metadata_leviat.csv               - Leviat columns

SAMPLE DATA FILES (11):
✓ sample_sentinel_endpoints.csv     - 100 rows
✓ sample_sentinel_versions.csv      - 38 rows
✓ sample_cybelangel_alerts.csv      - 100 rows
✓ sample_cybelangel_threats.csv     - 0 rows (structure only)
✓ sample_proofpoint_message_logs.csv - 100 rows
✓ sample_proofpoint_raw.csv         - 0 rows (structure only)
✓ sample_servicenow_snow.csv        - 100 rows
✓ sample_leviat_users.csv           - 0 rows (structure only)
✓ sample_leviat_list_users.csv      - 0 rows (structure only)
✓ sample_leviat_security_events.csv - 0 rows (structure only)

TOTAL: 18 CSV files
*/
