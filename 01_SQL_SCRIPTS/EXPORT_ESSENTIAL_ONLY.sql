/*
================================================================================
Export ESSENTIAL Metadata and Samples - PRIORITY FILES ONLY
================================================================================

Execute these queries ONE BY ONE and export each result as CSV.

Total: 10 files (most important ones)

Date: 2025-10-24
================================================================================
*/

USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;

-- ============================================================================
-- FILE 1: Complete Metadata (ALL SERVICES) - MOST IMPORTANT
-- ============================================================================

SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
ORDER BY SERVICE_NAME, DATA_LAYER, TABLE_NAME, ORDINAL_POSITION;

-- Save as: 04_METADATA_SAMPLES/metadata/metadata_all_services.csv
-- ✅ After saving, select next query

-- ============================================================================
-- FILE 2: SentinelOne Metadata
-- ============================================================================

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

-- Save as: 04_METADATA_SAMPLES/metadata/metadata_sentinelone.csv
-- ✅ After saving, select next query

-- ============================================================================
-- FILE 3: CybelAngel Metadata
-- ============================================================================

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

-- Save as: 04_METADATA_SAMPLES/metadata/metadata_cybelangel.csv
-- ✅ After saving, select next query

-- ============================================================================
-- FILE 4: Proofpoint Metadata
-- ============================================================================

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

-- Save as: 04_METADATA_SAMPLES/metadata/metadata_proofpoint.csv
-- ✅ After saving, select next query

-- ============================================================================
-- FILE 5: ServiceNow Metadata
-- ============================================================================

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

-- Save as: 04_METADATA_SAMPLES/metadata/metadata_servicenow.csv
-- ✅ After saving, select next query

-- ============================================================================
-- FILE 6: Leviat Metadata
-- ============================================================================

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

-- Save as: 04_METADATA_SAMPLES/metadata/metadata_leviat.csv
-- ✅ After saving, select next query

-- ============================================================================
-- FILE 7: SentinelOne Sample - Endpoints (100 rows)
-- ============================================================================

SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINEL_ENDPOINTS;

-- Save as: 04_METADATA_SAMPLES/samples/sample_sentinel_endpoints.csv
-- ✅ After saving, select next query

-- ============================================================================
-- FILE 8: CybelAngel Sample - Alerts (100 rows)
-- ============================================================================

SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_ALERTS;

-- Save as: 04_METADATA_SAMPLES/samples/sample_cybelangel_alerts.csv
-- ✅ After saving, select next query

-- ============================================================================
-- FILE 9: Proofpoint Sample - Message Logs (100 rows)
-- ============================================================================

SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_PROOFPOINT_MESSAGE_LOGS;

-- Save as: 04_METADATA_SAMPLES/samples/sample_proofpoint_message_logs.csv
-- ✅ After saving, select next query

-- ============================================================================
-- FILE 10: ServiceNow Sample - SNOW (100 rows)
-- ============================================================================

SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SERVICENOW_SNOW;

-- Save as: 04_METADATA_SAMPLES/samples/sample_servicenow_snow.csv
-- ✅ DONE! All essential files exported

-- ============================================================================
-- SUMMARY
-- ============================================================================

/*
FILES EXPORTED (10 total):

METADATA (6 files):
✓ metadata_all_services.csv         - Complete metadata for all services
✓ metadata_sentinelone.csv          - SentinelOne columns
✓ metadata_cybelangel.csv           - CybelAngel columns
✓ metadata_proofpoint.csv           - Proofpoint columns
✓ metadata_servicenow.csv           - ServiceNow columns
✓ metadata_leviat.csv               - Leviat columns

SAMPLES (4 files - only tables with data):
✓ sample_sentinel_endpoints.csv     - 100 rows
✓ sample_cybelangel_alerts.csv      - 100 rows
✓ sample_proofpoint_message_logs.csv - 100 rows
✓ sample_servicenow_snow.csv        - 100 rows

NEXT STEP:
Use these CSV files to build/update Streamlit apps with accurate column names!
*/
