-- =====================================================
-- ServiceNow Connector - Verification Queries
-- =====================================================
-- Purpose: Verify schemas and tracking table were created successfully
-- Author: GenericCorp Data Engineering Team
-- Date: 2025-10-24
-- =====================================================

USE DATABASE DEV_TRANSFORMATION;

-- =====================================================
-- 1. Verify Schemas Created
-- =====================================================

SELECT
    schema_name,
    schema_owner,
    retention_time,
    comment,
    created AS schema_created_timestamp
FROM INFORMATION_SCHEMA.SCHEMATA
WHERE schema_name IN ('RAW_DATA', 'CONNECTOR_METADATA')
ORDER BY schema_name;

-- =====================================================
-- 2. Verify Installation Log Table
-- =====================================================

USE SCHEMA CONNECTOR_METADATA;

-- Check table exists and structure
DESCRIBE TABLE CONNECTOR_INSTALLATION_LOG;

-- View installation log entries
SELECT
    log_id,
    installation_step,
    step_status,
    execution_timestamp,
    executed_by,
    notes
FROM CONNECTOR_INSTALLATION_LOG
ORDER BY log_id DESC;

-- =====================================================
-- 3. Verify Permissions
-- =====================================================

-- Check grants on RAW_DATA schema
SHOW GRANTS ON SCHEMA DEV_TRANSFORMATION.RAW_DATA;

-- Check grants on CONNECTOR_METADATA schema
SHOW GRANTS ON SCHEMA DEV_TRANSFORMATION.CONNECTOR_METADATA;

-- =====================================================
-- 4. Summary Status
-- =====================================================

SELECT
    '✅ RAW_DATA schema created' AS verification_item,
    CASE
        WHEN EXISTS (
            SELECT 1
            FROM INFORMATION_SCHEMA.SCHEMATA
            WHERE schema_name = 'RAW_DATA'
        ) THEN 'PASS ✅'
        ELSE 'FAIL ❌'
    END AS status
UNION ALL
SELECT
    '✅ CONNECTOR_METADATA schema created' AS verification_item,
    CASE
        WHEN EXISTS (
            SELECT 1
            FROM INFORMATION_SCHEMA.SCHEMATA
            WHERE schema_name = 'CONNECTOR_METADATA'
        ) THEN 'PASS ✅'
        ELSE 'FAIL ❌'
    END AS status
UNION ALL
SELECT
    '✅ CONNECTOR_INSTALLATION_LOG table created' AS verification_item,
    CASE
        WHEN EXISTS (
            SELECT 1
            FROM INFORMATION_SCHEMA.TABLES
            WHERE table_schema = 'CONNECTOR_METADATA'
              AND table_name = 'CONNECTOR_INSTALLATION_LOG'
        ) THEN 'PASS ✅'
        ELSE 'FAIL ❌'
    END AS status
UNION ALL
SELECT
    '✅ Installation log has records' AS verification_item,
    CASE
        WHEN (
            SELECT COUNT(*)
            FROM DEV_TRANSFORMATION.CONNECTOR_METADATA.CONNECTOR_INSTALLATION_LOG
        ) >= 4 THEN 'PASS ✅ (' || (
            SELECT COUNT(*)
            FROM DEV_TRANSFORMATION.CONNECTOR_METADATA.CONNECTOR_INSTALLATION_LOG
        ) || ' records)'
        ELSE 'FAIL ❌'
    END AS status;
