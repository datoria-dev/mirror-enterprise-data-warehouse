/*
================================================================================
Export Metadata Repository Results to JSON and CSV
================================================================================

This script exports metadata repository results to files for analysis.
Execute each section and save the results as indicated.

IMPORTANT: Always save query results to files for future reference and analysis.

Date: 2025-10-24
================================================================================
*/

USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;
USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA METADATA;

-- ============================================================================
-- EXPORT 1: Service Summary (JSON and CSV)
-- ============================================================================

-- Create table for export
CREATE OR REPLACE TABLE METADATA_EXPORTS.SERVICE_SUMMARY_EXPORT AS
SELECT
    SERVICE_NAME,
    TABLE_COUNT,
    TOTAL_ROWS,
    TOTAL_COLUMNS,
    ACTIVE_TABLES,
    AVG_COLUMNS_PER_TABLE,
    CURRENT_TIMESTAMP() as EXPORTED_AT
FROM VW_SERVICE_SUMMARY
ORDER BY TABLE_COUNT DESC, TOTAL_ROWS DESC;

-- View results
SELECT * FROM METADATA_EXPORTS.SERVICE_SUMMARY_EXPORT;

-- ✅ Save as: 04_METADATA_SAMPLES/json/service_summary_export.json
-- ✅ Save as: 04_METADATA_SAMPLES/metadata/service_summary_export.csv

-- JSON format with nested structure
SELECT
    OBJECT_CONSTRUCT(
        'export_date', CURRENT_TIMESTAMP(),
        'total_services', COUNT(*),
        'services', ARRAY_AGG(
            OBJECT_CONSTRUCT(
                'service_name', SERVICE_NAME,
                'table_count', TABLE_COUNT,
                'total_rows', TOTAL_ROWS,
                'total_columns', TOTAL_COLUMNS,
                'active_tables', ACTIVE_TABLES,
                'avg_columns_per_table', AVG_COLUMNS_PER_TABLE
            )
        )
    ) as SERVICE_SUMMARY_JSON
FROM VW_SERVICE_SUMMARY;

-- ✅ Copy this result and save as: 04_METADATA_SAMPLES/json/service_summary.json

-- ============================================================================
-- EXPORT 2: Complete Table Catalog (CSV)
-- ============================================================================

CREATE OR REPLACE TABLE METADATA_EXPORTS.TABLE_CATALOG_EXPORT AS
SELECT
    SERVICE_NAME,
    DATABASE_NAME,
    SCHEMA_NAME,
    TABLE_NAME,
    TABLE_TYPE,
    DATA_LAYER,
    TOTAL_ROWS,
    TOTAL_COLUMNS,
    IS_ACTIVE,
    LAST_UPDATED,
    FULL_TABLE_NAME,
    CURRENT_TIMESTAMP() as EXPORTED_AT
FROM VW_TABLE_CATALOG
ORDER BY SERVICE_NAME, TABLE_NAME;

SELECT * FROM METADATA_EXPORTS.TABLE_CATALOG_EXPORT;

-- ✅ Save as: 04_METADATA_SAMPLES/metadata/table_catalog_complete.csv

-- ============================================================================
-- EXPORT 3: Complete Column Catalog by Service (CSV)
-- ============================================================================

-- SentinelOne columns
CREATE OR REPLACE TABLE METADATA_EXPORTS.SENTINELONE_COLUMNS_EXPORT AS
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    FULL_TABLE_NAME,
    CURRENT_TIMESTAMP() as EXPORTED_AT
FROM VW_COLUMN_CATALOG
WHERE SERVICE_NAME = 'SentinelOne'
ORDER BY TABLE_NAME, ORDINAL_POSITION;

SELECT * FROM METADATA_EXPORTS.SENTINELONE_COLUMNS_EXPORT;
-- ✅ Save as: 04_METADATA_SAMPLES/metadata/sentinelone_columns.csv

-- CybelAngel columns
CREATE OR REPLACE TABLE METADATA_EXPORTS.CYBELANGEL_COLUMNS_EXPORT AS
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    FULL_TABLE_NAME,
    CURRENT_TIMESTAMP() as EXPORTED_AT
FROM VW_COLUMN_CATALOG
WHERE SERVICE_NAME = 'CybelAngel'
ORDER BY TABLE_NAME, ORDINAL_POSITION;

SELECT * FROM METADATA_EXPORTS.CYBELANGEL_COLUMNS_EXPORT;
-- ✅ Save as: 04_METADATA_SAMPLES/metadata/cybelangel_columns.csv

-- Proofpoint columns
CREATE OR REPLACE TABLE METADATA_EXPORTS.PROOFPOINT_COLUMNS_EXPORT AS
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    FULL_TABLE_NAME,
    CURRENT_TIMESTAMP() as EXPORTED_AT
FROM VW_COLUMN_CATALOG
WHERE SERVICE_NAME = 'Proofpoint'
ORDER BY TABLE_NAME, ORDINAL_POSITION;

SELECT * FROM METADATA_EXPORTS.PROOFPOINT_COLUMNS_EXPORT;
-- ✅ Save as: 04_METADATA_SAMPLES/metadata/proofpoint_columns.csv

-- ServiceNow columns
CREATE OR REPLACE TABLE METADATA_EXPORTS.SERVICENOW_COLUMNS_EXPORT AS
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    FULL_TABLE_NAME,
    CURRENT_TIMESTAMP() as EXPORTED_AT
FROM VW_COLUMN_CATALOG
WHERE SERVICE_NAME = 'ServiceNow'
ORDER BY TABLE_NAME, ORDINAL_POSITION;

SELECT * FROM METADATA_EXPORTS.SERVICENOW_COLUMNS_EXPORT;
-- ✅ Save as: 04_METADATA_SAMPLES/metadata/servicenow_columns.csv

-- Leviat columns
CREATE OR REPLACE TABLE METADATA_EXPORTS.LEVIAT_COLUMNS_EXPORT AS
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    FULL_TABLE_NAME,
    CURRENT_TIMESTAMP() as EXPORTED_AT
FROM VW_COLUMN_CATALOG
WHERE SERVICE_NAME = 'Leviat'
ORDER BY TABLE_NAME, ORDINAL_POSITION;

SELECT * FROM METADATA_EXPORTS.LEVIAT_COLUMNS_EXPORT;
-- ✅ Save as: 04_METADATA_SAMPLES/metadata/leviat_columns.csv

-- Tenable columns
CREATE OR REPLACE TABLE METADATA_EXPORTS.TENABLE_COLUMNS_EXPORT AS
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    FULL_TABLE_NAME,
    CURRENT_TIMESTAMP() as EXPORTED_AT
FROM VW_COLUMN_CATALOG
WHERE SERVICE_NAME = 'Tenable'
ORDER BY TABLE_NAME, ORDINAL_POSITION;

SELECT * FROM METADATA_EXPORTS.TENABLE_COLUMNS_EXPORT;
-- ✅ Save as: 04_METADATA_SAMPLES/metadata/tenable_columns.csv

-- ============================================================================
-- EXPORT 4: All Columns Combined (CSV)
-- ============================================================================

CREATE OR REPLACE TABLE METADATA_EXPORTS.ALL_COLUMNS_EXPORT AS
SELECT
    SERVICE_NAME,
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    DATABASE_NAME,
    SCHEMA_NAME,
    FULL_TABLE_NAME,
    CURRENT_TIMESTAMP() as EXPORTED_AT
FROM VW_COLUMN_CATALOG
ORDER BY SERVICE_NAME, TABLE_NAME, ORDINAL_POSITION;

SELECT * FROM METADATA_EXPORTS.ALL_COLUMNS_EXPORT;

-- ✅ Save as: 04_METADATA_SAMPLES/metadata/all_columns_complete.csv

-- ============================================================================
-- EXPORT 5: All Columns by Service (JSON)
-- ============================================================================

-- Generate JSON with all services and their columns
SELECT
    OBJECT_CONSTRUCT(
        'extraction_date', CURRENT_TIMESTAMP(),
        'services', (
            SELECT OBJECT_AGG(
                SERVICE_NAME,
                OBJECT_CONSTRUCT(
                    'service_name', SERVICE_NAME,
                    'tables', (
                        SELECT OBJECT_AGG(
                            TABLE_NAME,
                            OBJECT_CONSTRUCT(
                                'table_name', TABLE_NAME,
                                'full_table_name', FULL_TABLE_NAME,
                                'column_count', COUNT(*),
                                'columns', ARRAY_AGG(
                                    OBJECT_CONSTRUCT(
                                        'name', COLUMN_NAME,
                                        'type', DATA_TYPE,
                                        'nullable', IS_NULLABLE,
                                        'position', ORDINAL_POSITION
                                    ) ORDER BY ORDINAL_POSITION
                                )
                            )
                        )
                        FROM VW_COLUMN_CATALOG c2
                        WHERE c2.SERVICE_NAME = c1.SERVICE_NAME
                        GROUP BY TABLE_NAME, FULL_TABLE_NAME
                    )
                )
            )
            FROM (SELECT DISTINCT SERVICE_NAME FROM VW_COLUMN_CATALOG) c1
        )
    ) as COMPLETE_METADATA_JSON
FROM DUAL;

-- ✅ Copy this result and save as: 04_METADATA_SAMPLES/json/all_services_columns_complete.json

-- ============================================================================
-- EXPORT 6: Stored Procedure Execution Logs (CSV and JSON)
-- ============================================================================

CREATE OR REPLACE TABLE METADATA_EXPORTS.PROCEDURE_EXECUTION_LOG_EXPORT AS
SELECT
    LOG_ID,
    PROCEDURE_NAME,
    EXECUTION_START,
    EXECUTION_END,
    EXECUTION_DURATION_SECONDS,
    STATUS,
    ROWS_PROCESSED,
    TABLES_PROCESSED,
    COLUMNS_PROCESSED,
    ERROR_MESSAGE,
    EXECUTED_BY,
    CREATED_DATE
FROM PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC;

SELECT * FROM METADATA_EXPORTS.PROCEDURE_EXECUTION_LOG_EXPORT;

-- ✅ Save as: 04_METADATA_SAMPLES/logs/procedure_execution_log.csv

-- JSON format for logs
SELECT
    OBJECT_CONSTRUCT(
        'export_date', CURRENT_TIMESTAMP(),
        'total_executions', COUNT(*),
        'executions', ARRAY_AGG(
            OBJECT_CONSTRUCT(
                'log_id', LOG_ID,
                'procedure_name', PROCEDURE_NAME,
                'execution_start', EXECUTION_START,
                'execution_end', EXECUTION_END,
                'duration_seconds', EXECUTION_DURATION_SECONDS,
                'status', STATUS,
                'tables_processed', TABLES_PROCESSED,
                'columns_processed', COLUMNS_PROCESSED,
                'error_message', ERROR_MESSAGE
            ) ORDER BY EXECUTION_START DESC
        )
    ) as EXECUTION_LOG_JSON
FROM PROCEDURE_EXECUTION_LOG;

-- ✅ Copy this result and save as: 04_METADATA_SAMPLES/logs/procedure_execution_log.json

-- ============================================================================
-- EXPORT 7: Execution Log Statistics (CSV)
-- ============================================================================

CREATE OR REPLACE TABLE METADATA_EXPORTS.EXECUTION_STATISTICS_EXPORT AS
SELECT
    PROCEDURE_NAME,
    STATUS,
    COUNT(*) as EXECUTION_COUNT,
    ROUND(AVG(EXECUTION_DURATION_SECONDS), 2) as AVG_DURATION_SECONDS,
    MIN(EXECUTION_DURATION_SECONDS) as MIN_DURATION_SECONDS,
    MAX(EXECUTION_DURATION_SECONDS) as MAX_DURATION_SECONDS,
    SUM(TABLES_PROCESSED) as TOTAL_TABLES_PROCESSED,
    SUM(COLUMNS_PROCESSED) as TOTAL_COLUMNS_PROCESSED,
    MIN(EXECUTION_START) as FIRST_EXECUTION,
    MAX(EXECUTION_START) as LAST_EXECUTION,
    CURRENT_TIMESTAMP() as EXPORTED_AT
FROM PROCEDURE_EXECUTION_LOG
GROUP BY PROCEDURE_NAME, STATUS
ORDER BY PROCEDURE_NAME, STATUS;

SELECT * FROM METADATA_EXPORTS.EXECUTION_STATISTICS_EXPORT;

-- ✅ Save as: 04_METADATA_SAMPLES/logs/execution_statistics.csv

-- ============================================================================
-- EXPORT 8: Daily Execution Trend (CSV)
-- ============================================================================

CREATE OR REPLACE TABLE METADATA_EXPORTS.DAILY_EXECUTION_TREND_EXPORT AS
SELECT
    DATE(EXECUTION_START) as EXECUTION_DATE,
    COUNT(*) as EXECUTION_COUNT,
    COUNT(CASE WHEN STATUS = 'SUCCESS' THEN 1 END) as SUCCESS_COUNT,
    COUNT(CASE WHEN STATUS = 'FAILED' THEN 1 END) as FAILED_COUNT,
    ROUND(AVG(EXECUTION_DURATION_SECONDS), 2) as AVG_DURATION_SECONDS,
    ROUND(AVG(TABLES_PROCESSED), 0) as AVG_TABLES_PROCESSED,
    ROUND(AVG(COLUMNS_PROCESSED), 0) as AVG_COLUMNS_PROCESSED,
    CURRENT_TIMESTAMP() as EXPORTED_AT
FROM PROCEDURE_EXECUTION_LOG
GROUP BY DATE(EXECUTION_START)
ORDER BY EXECUTION_DATE DESC;

SELECT * FROM METADATA_EXPORTS.DAILY_EXECUTION_TREND_EXPORT;

-- ✅ Save as: 04_METADATA_SAMPLES/logs/daily_execution_trend.csv

-- ============================================================================
-- EXPORT 9: Table Statistics History (CSV)
-- ============================================================================

CREATE OR REPLACE TABLE METADATA_EXPORTS.TABLE_STATISTICS_EXPORT AS
SELECT
    tr.SERVICE_NAME,
    tr.TABLE_NAME,
    ts.SNAPSHOT_DATE,
    ts.ROW_COUNT,
    ts.COLUMN_COUNT,
    ts.SIZE_BYTES,
    CURRENT_TIMESTAMP() as EXPORTED_AT
FROM TABLE_STATISTICS ts
JOIN TABLE_REGISTRY tr ON ts.TABLE_ID = tr.TABLE_ID
ORDER BY tr.SERVICE_NAME, tr.TABLE_NAME, ts.SNAPSHOT_DATE DESC;

SELECT * FROM METADATA_EXPORTS.TABLE_STATISTICS_EXPORT;

-- ✅ Save as: 04_METADATA_SAMPLES/metadata/table_statistics_history.csv

-- ============================================================================
-- EXPORT 10: Data Quality Dashboard Summary (JSON)
-- ============================================================================

SELECT
    OBJECT_CONSTRUCT(
        'export_date', CURRENT_TIMESTAMP(),
        'summary', OBJECT_CONSTRUCT(
            'total_services', (SELECT COUNT(DISTINCT SERVICE_NAME) FROM VW_SERVICE_SUMMARY),
            'total_tables', (SELECT COUNT(*) FROM TABLE_REGISTRY),
            'total_columns', (SELECT COUNT(*) FROM COLUMN_METADATA),
            'total_rows', (SELECT SUM(TOTAL_ROWS) FROM VW_TABLE_CATALOG),
            'active_tables', (SELECT COUNT(*) FROM TABLE_REGISTRY WHERE IS_ACTIVE = TRUE),
            'last_refresh', (SELECT MAX(EXECUTION_END) FROM PROCEDURE_EXECUTION_LOG WHERE STATUS = 'SUCCESS')
        ),
        'services', (
            SELECT ARRAY_AGG(
                OBJECT_CONSTRUCT(
                    'service_name', SERVICE_NAME,
                    'table_count', TABLE_COUNT,
                    'total_rows', TOTAL_ROWS,
                    'total_columns', TOTAL_COLUMNS
                ) ORDER BY TABLE_COUNT DESC
            )
            FROM VW_SERVICE_SUMMARY
        ),
        'execution_stats', OBJECT_CONSTRUCT(
            'total_executions', (SELECT COUNT(*) FROM PROCEDURE_EXECUTION_LOG),
            'success_count', (SELECT COUNT(*) FROM PROCEDURE_EXECUTION_LOG WHERE STATUS = 'SUCCESS'),
            'failed_count', (SELECT COUNT(*) FROM PROCEDURE_EXECUTION_LOG WHERE STATUS = 'FAILED'),
            'avg_duration_seconds', (SELECT ROUND(AVG(EXECUTION_DURATION_SECONDS), 2) FROM PROCEDURE_EXECUTION_LOG WHERE STATUS = 'SUCCESS'),
            'last_execution', (SELECT MAX(EXECUTION_END) FROM PROCEDURE_EXECUTION_LOG)
        )
    ) as DASHBOARD_SUMMARY_JSON
FROM DUAL;

-- ✅ Copy this result and save as: 04_METADATA_SAMPLES/json/dashboard_summary.json

-- ============================================================================
-- EXPORT 11: Service Catalog (CSV)
-- ============================================================================

CREATE OR REPLACE TABLE METADATA_EXPORTS.SERVICE_CATALOG_EXPORT AS
SELECT
    SERVICE_NAME,
    SERVICE_DESCRIPTION,
    SERVICE_CATEGORY,
    IS_ACTIVE,
    REFRESH_FREQUENCY,
    CREATED_DATE,
    CURRENT_TIMESTAMP() as EXPORTED_AT
FROM SERVICE_CATALOG
ORDER BY SERVICE_CATEGORY, SERVICE_NAME;

SELECT * FROM METADATA_EXPORTS.SERVICE_CATALOG_EXPORT;

-- ✅ Save as: 04_METADATA_SAMPLES/metadata/service_catalog.csv

-- ============================================================================
-- EXPORT 12: Missing Services Report (CSV)
-- ============================================================================

CREATE OR REPLACE TABLE METADATA_EXPORTS.MISSING_SERVICES_EXPORT AS
SELECT
    sc.SERVICE_NAME,
    sc.SERVICE_CATEGORY,
    sc.SERVICE_DESCRIPTION,
    sc.IS_ACTIVE,
    sc.REFRESH_FREQUENCY,
    CASE
        WHEN tr.SERVICE_NAME IS NULL THEN 'No tables found'
        ELSE 'Has tables'
    END as DATA_STATUS,
    CURRENT_TIMESTAMP() as EXPORTED_AT
FROM SERVICE_CATALOG sc
LEFT JOIN TABLE_REGISTRY tr ON sc.SERVICE_NAME = tr.SERVICE_NAME
WHERE tr.SERVICE_NAME IS NULL
ORDER BY sc.SERVICE_CATEGORY, sc.SERVICE_NAME;

SELECT * FROM METADATA_EXPORTS.MISSING_SERVICES_EXPORT;

-- ✅ Save as: 04_METADATA_SAMPLES/reports/missing_services_report.csv

-- ============================================================================
-- VERIFICATION: List All Exported Tables
-- ============================================================================

SELECT
    TABLE_NAME,
    ROW_COUNT,
    CREATED as CREATED_DATE
FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'METADATA_EXPORTS'
  AND TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;

/*
================================================================================
SUMMARY OF EXPORTS
================================================================================

JSON FILES (save to: 04_METADATA_SAMPLES/json/):
1. service_summary.json - Service summary with nested structure
2. all_services_columns_complete.json - All services with columns
3. procedure_execution_log.json - Execution log history
4. dashboard_summary.json - Complete dashboard summary

CSV FILES (save to: 04_METADATA_SAMPLES/metadata/):
1. service_summary_export.csv - Service summary
2. table_catalog_complete.csv - Complete table catalog
3. sentinelone_columns.csv - SentinelOne columns
4. cybelangel_columns.csv - CybelAngel columns
5. proofpoint_columns.csv - Proofpoint columns
6. servicenow_columns.csv - ServiceNow columns
7. leviat_columns.csv - Leviat columns
8. tenable_columns.csv - Tenable columns
9. all_columns_complete.csv - All columns combined
10. table_statistics_history.csv - Historical statistics
11. service_catalog.csv - Service catalog

LOG FILES (save to: 04_METADATA_SAMPLES/logs/):
1. procedure_execution_log.csv - Execution log
2. execution_statistics.csv - Execution statistics
3. daily_execution_trend.csv - Daily trends

REPORT FILES (save to: 04_METADATA_SAMPLES/reports/):
1. missing_services_report.csv - Services without data

NEXT STEPS:
1. Execute each section and save results as indicated
2. Use these files to build Streamlit apps
3. Share files for team review and analysis
================================================================================
*/
