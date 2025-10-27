-- ============================================
-- Auto-Generate ERDs from Metadata Repository
-- ============================================
-- Purpose: Create views for automated ERD generation from metadata
-- Author: GenericCorp Data Engineering Team
-- Date: 2025-10-24
-- Fixed Version: Updated to match actual TABLE_REGISTRY and COLUMN_METADATA schema
-- ============================================

USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA METADATA;

-- ============================================
-- View 1: Table Catalog with Service Colors
-- ============================================
-- Purpose: Master list of all tables with color coding by service
CREATE OR REPLACE VIEW VW_ERD_TABLE_CATALOG AS
SELECT
    tr.TABLE_ID,
    tr.SERVICE_NAME,
    tr.DATABASE_NAME || '.' || tr.SCHEMA_NAME || '.' || tr.TABLE_NAME AS FULL_TABLE_NAME,
    tr.TABLE_NAME,
    tr.SCHEMA_NAME,
    tr.DATABASE_NAME,
    tr.TABLE_TYPE,
    tr.DATA_LAYER,
    tr.ROW_COUNT,
    tr.IS_ACTIVE,
    tr.DESCRIPTION,
    -- Calculate column count
    (SELECT COUNT(*)
     FROM COLUMN_METADATA cm
     WHERE cm.TABLE_ID = tr.TABLE_ID) AS COLUMN_COUNT,
    -- Color coding by service category
    CASE
        WHEN tr.SERVICE_NAME IN ('SentinelOne', 'CrowdStrike', 'Microsoft Defender') THEN '#FF6B6B' -- Red for Endpoint Security
        WHEN tr.SERVICE_NAME IN ('Qualys', 'Tenable', 'Rapid7') THEN '#4ECDC4' -- Teal for Vulnerability Management
        WHEN tr.SERVICE_NAME IN ('CybelAngel', 'Recorded Future') THEN '#FFE66D' -- Yellow for Threat Intelligence
        WHEN tr.SERVICE_NAME IN ('Ping', 'Okta', 'Azure AD') THEN '#95E1D3' -- Light Green for Identity
        WHEN tr.SERVICE_NAME IN ('Zscaler', 'Fortinet', 'Palo Alto') THEN '#A8E6CF' -- Mint for Network Security
        WHEN tr.SERVICE_NAME = 'Azure' THEN '#6C5CE7' -- Purple for Cloud
        WHEN tr.SERVICE_NAME = 'ServiceNow' THEN '#74B9FF' -- Blue for ITSM
        ELSE '#CCCCCC' -- Gray for others
    END AS SERVICE_COLOR,
    tr.LAST_UPDATED,
    tr.CREATED_DATE
FROM TABLE_REGISTRY tr
WHERE tr.IS_ACTIVE = TRUE
ORDER BY tr.SERVICE_NAME, tr.TABLE_NAME;

-- ============================================
-- View 2: Column Details with PK/FK Indicators
-- ============================================
-- Purpose: Complete column catalog with relationship indicators
CREATE OR REPLACE VIEW VW_ERD_COLUMN_DETAILS AS
SELECT
    cm.COLUMN_ID,
    cm.TABLE_ID,
    tr.SERVICE_NAME,
    tr.TABLE_NAME,
    tr.DATABASE_NAME || '.' || tr.SCHEMA_NAME || '.' || tr.TABLE_NAME AS FULL_TABLE_NAME,
    cm.COLUMN_NAME,
    cm.DATA_TYPE,
    cm.IS_NULLABLE,
    cm.ORDINAL_POSITION,
    cm.IS_PRIMARY_KEY,
    cm.IS_FOREIGN_KEY,
    cm.COLUMN_COMMENT AS DESCRIPTION,
    cm.DISTINCT_COUNT,
    cm.NULL_COUNT,
    -- Calculate NULL percentage
    CASE
        WHEN tr.ROW_COUNT > 0
        THEN ROUND((cm.NULL_COUNT::FLOAT / tr.ROW_COUNT) * 100, 2)
        ELSE 0
    END AS NULL_PERCENTAGE,
    -- Key type indicator
    CASE
        WHEN cm.IS_PRIMARY_KEY THEN 'PK'
        WHEN cm.IS_FOREIGN_KEY THEN 'FK'
        ELSE NULL
    END AS KEY_TYPE,
    cm.SAMPLE_VALUES,
    cm.CREATED_DATE
FROM COLUMN_METADATA cm
INNER JOIN TABLE_REGISTRY tr ON cm.TABLE_ID = tr.TABLE_ID
WHERE tr.IS_ACTIVE = TRUE
ORDER BY tr.SERVICE_NAME, tr.TABLE_NAME, cm.ORDINAL_POSITION;

-- ============================================
-- View 3: Auto-Detected Relationships
-- ============================================
-- Purpose: Identify relationships based on column naming patterns
CREATE OR REPLACE VIEW VW_ERD_RELATIONSHIPS AS
WITH potential_fks AS (
    SELECT
        cm.TABLE_ID,
        tr.TABLE_NAME AS source_table,
        tr.SERVICE_NAME AS source_service,
        cm.COLUMN_NAME,
        cm.IS_FOREIGN_KEY,
        -- Try to identify target table from column name
        CASE
            WHEN cm.COLUMN_NAME LIKE '%_ID' AND cm.COLUMN_NAME != UPPER(tr.TABLE_NAME) || '_ID'
            THEN REPLACE(cm.COLUMN_NAME, '_ID', '')
            WHEN cm.COLUMN_NAME LIKE '%_KEY'
            THEN REPLACE(cm.COLUMN_NAME, '_KEY', '')
            ELSE NULL
        END AS inferred_target_table,
        cm.DATA_TYPE
    FROM COLUMN_METADATA cm
    INNER JOIN TABLE_REGISTRY tr ON cm.TABLE_ID = tr.TABLE_ID
    WHERE tr.IS_ACTIVE = TRUE
      AND (cm.IS_FOREIGN_KEY = TRUE OR cm.COLUMN_NAME LIKE '%_ID' OR cm.COLUMN_NAME LIKE '%_KEY')
)
SELECT
    fk.source_service || '.' || fk.source_table AS source_table,
    fk.COLUMN_NAME AS source_column,
    fk.inferred_target_table AS target_table,
    fk.inferred_target_table || '_ID' AS target_column,
    CASE
        WHEN fk.IS_FOREIGN_KEY THEN 'EXPLICIT'
        ELSE 'INFERRED'
    END AS relationship_type,
    '1:N' AS cardinality,
    fk.DATA_TYPE
FROM potential_fks fk
WHERE fk.inferred_target_table IS NOT NULL
ORDER BY fk.source_service, fk.source_table, fk.COLUMN_NAME;

-- ============================================
-- View 4: Data Lineage (Landing → Transformation)
-- ============================================
-- Purpose: Track data flow between landing and transformation layers
CREATE OR REPLACE VIEW VW_ERD_DATA_LINEAGE AS
SELECT
    l.SERVICE_NAME,
    l.TABLE_NAME AS landing_table,
    l.DATABASE_NAME || '.' || l.SCHEMA_NAME || '.' || l.TABLE_NAME AS landing_full_name,
    t.TABLE_NAME AS transformation_table,
    t.DATABASE_NAME || '.' || t.SCHEMA_NAME || '.' || t.TABLE_NAME AS transformation_full_name,
    l.ROW_COUNT AS landing_row_count,
    t.ROW_COUNT AS transformation_row_count,
    -- Calculate data loss/gain percentage
    CASE
        WHEN l.ROW_COUNT > 0
        THEN ROUND(((t.ROW_COUNT - l.ROW_COUNT)::FLOAT / l.ROW_COUNT) * 100, 2)
        ELSE 0
    END AS row_change_percentage,
    l.LAST_UPDATED AS landing_last_updated,
    t.LAST_UPDATED AS transformation_last_updated
FROM TABLE_REGISTRY l
LEFT JOIN TABLE_REGISTRY t
    ON l.SERVICE_NAME = t.SERVICE_NAME
    AND l.TABLE_NAME = t.TABLE_NAME
    AND t.DATA_LAYER = 'TRANSFORMATION'
WHERE l.DATA_LAYER = 'LANDING'
  AND l.IS_ACTIVE = TRUE
ORDER BY l.SERVICE_NAME, l.TABLE_NAME;

-- ============================================
-- View 5: Metadata Repository ERD
-- ============================================
-- Purpose: ERD of the metadata repository itself
CREATE OR REPLACE VIEW VW_ERD_METADATA_REPOSITORY AS
SELECT
    'TABLE_REGISTRY' AS table_name,
    'Core metadata catalog table' AS description,
    (SELECT COUNT(*) FROM TABLE_REGISTRY) AS row_count,
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
     WHERE TABLE_SCHEMA = 'METADATA' AND TABLE_NAME = 'TABLE_REGISTRY') AS column_count
UNION ALL
SELECT
    'COLUMN_METADATA' AS table_name,
    'Column-level metadata and statistics' AS description,
    (SELECT COUNT(*) FROM COLUMN_METADATA) AS row_count,
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
     WHERE TABLE_SCHEMA = 'METADATA' AND TABLE_NAME = 'COLUMN_METADATA') AS column_count;

-- ============================================
-- View 6: ERD Data by Service
-- ============================================
-- Purpose: Service-level summary for generating service-specific ERDs
CREATE OR REPLACE VIEW VW_ERD_BY_SERVICE AS
SELECT
    tr.SERVICE_NAME,
    COUNT(DISTINCT tr.TABLE_ID) AS table_count,
    COUNT(DISTINCT cm.COLUMN_ID) AS column_count,
    SUM(tr.ROW_COUNT) AS total_rows,
    COUNT(DISTINCT CASE WHEN cm.IS_PRIMARY_KEY THEN cm.COLUMN_ID END) AS pk_count,
    COUNT(DISTINCT CASE WHEN cm.IS_FOREIGN_KEY THEN cm.COLUMN_ID END) AS fk_count,
    MAX(tr.LAST_UPDATED) AS last_updated,
    -- Service color for ERD visualization
    CASE
        WHEN tr.SERVICE_NAME IN ('SentinelOne', 'CrowdStrike', 'Microsoft Defender') THEN '#FF6B6B'
        WHEN tr.SERVICE_NAME IN ('Qualys', 'Tenable', 'Rapid7') THEN '#4ECDC4'
        WHEN tr.SERVICE_NAME IN ('CybelAngel', 'Recorded Future') THEN '#FFE66D'
        WHEN tr.SERVICE_NAME IN ('Ping', 'Okta', 'Azure AD') THEN '#95E1D3'
        WHEN tr.SERVICE_NAME IN ('Zscaler', 'Fortinet', 'Palo Alto') THEN '#A8E6CF'
        WHEN tr.SERVICE_NAME = 'Azure' THEN '#6C5CE7'
        WHEN tr.SERVICE_NAME = 'ServiceNow' THEN '#74B9FF'
        ELSE '#CCCCCC'
    END AS service_color
FROM TABLE_REGISTRY tr
INNER JOIN COLUMN_METADATA cm ON tr.TABLE_ID = cm.TABLE_ID
WHERE tr.IS_ACTIVE = TRUE
GROUP BY tr.SERVICE_NAME
ORDER BY table_count DESC, tr.SERVICE_NAME;

-- ============================================
-- View 7: Complete ERD Export
-- ============================================
-- Purpose: Comprehensive export for ERD generation tools
CREATE OR REPLACE VIEW VW_ERD_COMPLETE_EXPORT AS
SELECT
    tr.SERVICE_NAME,
    tr.TABLE_NAME,
    tr.DATABASE_NAME || '.' || tr.SCHEMA_NAME || '.' || tr.TABLE_NAME AS full_table_name,
    tr.DATA_LAYER,
    cm.COLUMN_NAME,
    cm.DATA_TYPE,
    cm.ORDINAL_POSITION,
    cm.IS_PRIMARY_KEY,
    cm.IS_FOREIGN_KEY,
    cm.IS_NULLABLE,
    CASE
        WHEN cm.IS_PRIMARY_KEY THEN 'PK'
        WHEN cm.IS_FOREIGN_KEY THEN 'FK'
        ELSE ''
    END AS key_indicator,
    cm.COLUMN_COMMENT AS description,
    tr.ROW_COUNT AS table_row_count,
    CASE
        WHEN tr.SERVICE_NAME IN ('SentinelOne', 'CrowdStrike', 'Microsoft Defender') THEN '#FF6B6B'
        WHEN tr.SERVICE_NAME IN ('Qualys', 'Tenable', 'Rapid7') THEN '#4ECDC4'
        WHEN tr.SERVICE_NAME IN ('CybelAngel', 'Recorded Future') THEN '#FFE66D'
        WHEN tr.SERVICE_NAME IN ('Ping', 'Okta', 'Azure AD') THEN '#95E1D3'
        WHEN tr.SERVICE_NAME IN ('Zscaler', 'Fortinet', 'Palo Alto') THEN '#A8E6CF'
        WHEN tr.SERVICE_NAME = 'Azure' THEN '#6C5CE7'
        WHEN tr.SERVICE_NAME = 'ServiceNow' THEN '#74B9FF'
        ELSE '#CCCCCC'
    END AS table_color
FROM TABLE_REGISTRY tr
INNER JOIN COLUMN_METADATA cm ON tr.TABLE_ID = cm.TABLE_ID
WHERE tr.IS_ACTIVE = TRUE
ORDER BY tr.SERVICE_NAME, tr.TABLE_NAME, cm.ORDINAL_POSITION;

-- ============================================
-- Query 1: Generate Mermaid ERD for SentinelOne Service
-- ============================================
-- Purpose: Example query to generate Mermaid syntax for a specific service
-- Note: Execute separately and copy output to wiki
SELECT
    'erDiagram' AS mermaid_code
UNION ALL
SELECT
    '    ' || TABLE_NAME || ' {' AS mermaid_code
FROM TABLE_REGISTRY
WHERE SERVICE_NAME = 'SentinelOne' AND IS_ACTIVE = TRUE
UNION ALL
SELECT
    '        ' || cm.DATA_TYPE || ' ' || cm.COLUMN_NAME ||
    CASE WHEN cm.IS_PRIMARY_KEY THEN ' PK'
         WHEN cm.IS_FOREIGN_KEY THEN ' FK'
         ELSE '' END AS mermaid_code
FROM COLUMN_METADATA cm
INNER JOIN TABLE_REGISTRY tr ON cm.TABLE_ID = tr.TABLE_ID
WHERE tr.SERVICE_NAME = 'SentinelOne' AND tr.IS_ACTIVE = TRUE
ORDER BY tr.TABLE_NAME, cm.ORDINAL_POSITION
UNION ALL
SELECT
    '    }' AS mermaid_code
FROM TABLE_REGISTRY
WHERE SERVICE_NAME = 'SentinelOne' AND IS_ACTIVE = TRUE;

-- ============================================
-- Query 2: Service Summary for ERD Planning
-- ============================================
-- Purpose: Overview of all services to plan ERD generation
SELECT
    SERVICE_NAME,
    table_count,
    column_count,
    total_rows,
    pk_count,
    fk_count,
    service_color
FROM VW_ERD_BY_SERVICE
ORDER BY table_count DESC;

-- ============================================
-- Query 3: Tables with Most Relationships
-- ============================================
-- Purpose: Identify central tables for ERD focus
SELECT
    tr.SERVICE_NAME,
    tr.TABLE_NAME,
    tr.DATABASE_NAME || '.' || tr.SCHEMA_NAME || '.' || tr.TABLE_NAME AS full_table_name,
    COUNT(DISTINCT CASE WHEN cm.IS_PRIMARY_KEY THEN cm.COLUMN_ID END) AS pk_count,
    COUNT(DISTINCT CASE WHEN cm.IS_FOREIGN_KEY THEN cm.COLUMN_ID END) AS fk_count,
    (SELECT COUNT(*) FROM COLUMN_METADATA cm2 WHERE cm2.TABLE_ID = tr.TABLE_ID) AS total_columns,
    tr.ROW_COUNT
FROM TABLE_REGISTRY tr
LEFT JOIN COLUMN_METADATA cm ON tr.TABLE_ID = cm.TABLE_ID
WHERE tr.IS_ACTIVE = TRUE
GROUP BY tr.TABLE_ID, tr.SERVICE_NAME, tr.TABLE_NAME, tr.DATABASE_NAME, tr.SCHEMA_NAME, tr.ROW_COUNT
HAVING pk_count > 0 OR fk_count > 0
ORDER BY fk_count DESC, pk_count DESC, tr.SERVICE_NAME, tr.TABLE_NAME
LIMIT 50;

-- ============================================
-- SUCCESS MESSAGE
-- ============================================
SELECT
    '✅ ERD views created successfully!' AS status,
    'Total of 7 views created in DEV_TRANSFORMATION.METADATA schema' AS details,
    'Views: VW_ERD_TABLE_CATALOG, VW_ERD_COLUMN_DETAILS, VW_ERD_RELATIONSHIPS, VW_ERD_DATA_LINEAGE, VW_ERD_METADATA_REPOSITORY, VW_ERD_BY_SERVICE, VW_ERD_COMPLETE_EXPORT' AS view_list,
    'Use these views to generate ERDs for Azure DevOps Data Model wiki' AS next_step;
