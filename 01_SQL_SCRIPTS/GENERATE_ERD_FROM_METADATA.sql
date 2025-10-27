-- ========================================
-- GENERATE ERD DATA FROM METADATA REPOSITORY
-- ========================================
-- Purpose: Extract relationship data from metadata to enhance ERD in Data Model wiki
-- Author: GenericCorp Data Engineering Team
-- Date: 2025-10-24
-- Usage: Execute this script and export results to enhance the Data Model wiki ERD
--
-- This script leverages the metadata repository to automatically generate:
-- 1. Table listings with columns
-- 2. Detected relationships (FK-like patterns)
-- 3. Service groupings for visual organization
-- 4. Data lineage (Landing → Transformation)
-- ========================================

USE ROLE DEV_DEVELOPER;
USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA METADATA;

-- ========================================
-- SECTION 1: TABLE CATALOG FOR ERD
-- ========================================
-- All tables with basic metadata for ERD generation

CREATE OR REPLACE VIEW VW_ERD_TABLE_CATALOG AS
SELECT
    tr.SERVICE_NAME,
    sc.SERVICE_CATEGORY,
    tr.DATABASE_NAME,
    tr.SCHEMA_NAME,
    tr.TABLE_NAME,
    tr.FULL_TABLE_NAME,
    tr.DATA_LAYER,
    tr.TABLE_TYPE,
    ts.COLUMN_COUNT,
    tr.ROW_COUNT,
    ROUND(tr.BYTES / 1024 / 1024, 2) as SIZE_MB,
    -- ERD positioning hints
    CASE tr.DATA_LAYER
        WHEN 'Landing' THEN 1
        WHEN 'Transformation' THEN 2
        ELSE 3
    END as LAYER_ORDER,
    -- Color coding by service category
    CASE sc.SERVICE_CATEGORY
        WHEN 'Endpoint Security' THEN '#FF6B6B'
        WHEN 'Email Security' THEN '#4ECDC4'
        WHEN 'Vulnerability Management' THEN '#95E1D3'
        WHEN 'Threat Intelligence' THEN '#F38181'
        WHEN 'Cloud Security' THEN '#AA96DA'
        WHEN 'SIEM & Monitoring' THEN '#FCBAD3'
        WHEN 'IT Service Management' THEN '#FFFFD2'
        WHEN 'Asset Management' THEN '#A8E6CF'
        ELSE '#DDDDDD'
    END as ERD_COLOR
FROM TABLE_REGISTRY tr
JOIN SERVICE_CATALOG sc ON tr.SERVICE_NAME = sc.SERVICE_NAME
LEFT JOIN TABLE_STATISTICS ts ON tr.TABLE_ID = ts.TABLE_ID
ORDER BY tr.SERVICE_NAME, tr.DATA_LAYER, tr.TABLE_NAME;

-- Export this view for ERD generation
SELECT * FROM VW_ERD_TABLE_CATALOG;


-- ========================================
-- SECTION 2: COLUMN DETAILS FOR ERD
-- ========================================
-- Column-level information for detailed ERD

CREATE OR REPLACE VIEW VW_ERD_COLUMN_DETAILS AS
SELECT
    cm.SERVICE_NAME,
    tr.DATA_LAYER,
    tr.TABLE_NAME,
    tr.FULL_TABLE_NAME,
    cm.COLUMN_NAME,
    cm.DATA_TYPE,
    cm.IS_NULLABLE,
    cm.ORDINAL_POSITION,
    -- Identify potential primary keys
    CASE
        WHEN cm.COLUMN_NAME LIKE '%_ID' AND cm.ORDINAL_POSITION = 1 THEN TRUE
        WHEN cm.COLUMN_NAME IN ('TABLE_ID', 'COLUMN_ID', 'SERVICE_ID', 'EXECUTION_ID', 'RULE_ID', 'STAT_ID') THEN TRUE
        WHEN cm.COLUMN_NAME LIKE '%_KEY' THEN TRUE
        ELSE FALSE
    END as IS_POTENTIAL_PK,
    -- Identify potential foreign keys
    CASE
        WHEN cm.COLUMN_NAME LIKE '%_ID' AND cm.ORDINAL_POSITION > 1 THEN TRUE
        WHEN cm.COLUMN_NAME LIKE 'FK_%' THEN TRUE
        ELSE FALSE
    END as IS_POTENTIAL_FK,
    -- Data type category for ERD styling
    CASE
        WHEN cm.DATA_TYPE LIKE '%CHAR%' THEN 'String'
        WHEN cm.DATA_TYPE LIKE '%NUMBER%' OR cm.DATA_TYPE LIKE '%INT%' THEN 'Numeric'
        WHEN cm.DATA_TYPE LIKE '%TIMESTAMP%' OR cm.DATA_TYPE LIKE '%DATE%' THEN 'DateTime'
        WHEN cm.DATA_TYPE = 'BOOLEAN' THEN 'Boolean'
        WHEN cm.DATA_TYPE IN ('VARIANT', 'ARRAY', 'OBJECT') THEN 'SemiStructured'
        ELSE 'Other'
    END as DATA_TYPE_CATEGORY
FROM COLUMN_METADATA cm
JOIN TABLE_REGISTRY tr ON cm.TABLE_ID = tr.TABLE_ID
ORDER BY cm.SERVICE_NAME, tr.DATA_LAYER, cm.TABLE_NAME, cm.ORDINAL_POSITION;

-- Export for ERD column details
SELECT * FROM VW_ERD_COLUMN_DETAILS;


-- ========================================
-- SECTION 3: DETECTED RELATIONSHIPS
-- ========================================
-- Automatically detect relationships based on column naming patterns

CREATE OR REPLACE VIEW VW_ERD_RELATIONSHIPS AS
WITH potential_fks AS (
    -- Find columns that look like foreign keys
    SELECT DISTINCT
        cm.SERVICE_NAME,
        cm.TABLE_NAME as SOURCE_TABLE,
        cm.COLUMN_NAME as FK_COLUMN,
        -- Infer target table from FK column name
        CASE
            -- Pattern: TABLE_ID references TABLE
            WHEN cm.COLUMN_NAME LIKE '%_ID' THEN REPLACE(cm.COLUMN_NAME, '_ID', '')
            -- Pattern: FK_TABLE references TABLE
            WHEN cm.COLUMN_NAME LIKE 'FK_%' THEN REPLACE(cm.COLUMN_NAME, 'FK_', '')
            ELSE NULL
        END as INFERRED_TARGET_TABLE,
        cm.DATA_TYPE
    FROM COLUMN_METADATA cm
    WHERE cm.COLUMN_NAME LIKE '%_ID'
       OR cm.COLUMN_NAME LIKE 'FK_%'
),
confirmed_relationships AS (
    -- Match inferred FKs with actual tables
    SELECT
        fk.SERVICE_NAME,
        fk.SOURCE_TABLE,
        fk.FK_COLUMN,
        fk.INFERRED_TARGET_TABLE,
        tr.TABLE_NAME as TARGET_TABLE,
        tr.FULL_TABLE_NAME as TARGET_FULL_NAME,
        CASE
            WHEN fk.SOURCE_TABLE LIKE fk.INFERRED_TARGET_TABLE || '%' THEN 'Self-Reference'
            WHEN tr.DATA_LAYER = 'Landing' THEN 'Landing-to-Landing'
            WHEN tr.DATA_LAYER = 'Transformation' THEN 'Within-Transformation'
            ELSE 'Cross-Layer'
        END as RELATIONSHIP_TYPE,
        '1:N' as CARDINALITY  -- Most relationships are one-to-many
    FROM potential_fks fk
    LEFT JOIN TABLE_REGISTRY tr
        ON fk.INFERRED_TARGET_TABLE = tr.TABLE_NAME
           AND fk.SERVICE_NAME = tr.SERVICE_NAME
    WHERE tr.TABLE_NAME IS NOT NULL
)
SELECT
    SERVICE_NAME,
    SOURCE_TABLE,
    FK_COLUMN,
    TARGET_TABLE,
    TARGET_FULL_NAME,
    RELATIONSHIP_TYPE,
    CARDINALITY,
    CONCAT(SOURCE_TABLE, '.', FK_COLUMN, ' -> ', TARGET_TABLE) as RELATIONSHIP_LABEL
FROM confirmed_relationships
ORDER BY SERVICE_NAME, SOURCE_TABLE, FK_COLUMN;

-- Export detected relationships
SELECT * FROM VW_ERD_RELATIONSHIPS;


-- ========================================
-- SECTION 4: METADATA REPOSITORY ERD (SPECIAL)
-- ========================================
-- Dedicated ERD for the metadata repository itself (6 tables, 3 views)

CREATE OR REPLACE VIEW VW_ERD_METADATA_REPOSITORY AS
SELECT
    'METADATA_REPOSITORY' as DIAGRAM_NAME,
    TABLE_NAME,
    'Metadata Repository' as CATEGORY,
    CASE
        WHEN TABLE_NAME LIKE 'VW_%' THEN 'View'
        ELSE 'Table'
    END as OBJECT_TYPE,
    COLUMN_COUNT,
    ROW_COUNT,
    -- Relationships within metadata repository
    CASE TABLE_NAME
        WHEN 'TABLE_REGISTRY' THEN 'Core - Referenced by COLUMN_METADATA, TABLE_STATISTICS'
        WHEN 'COLUMN_METADATA' THEN 'Child of TABLE_REGISTRY (FK: TABLE_ID)'
        WHEN 'TABLE_STATISTICS' THEN 'Child of TABLE_REGISTRY (FK: TABLE_ID)'
        WHEN 'SERVICE_CATALOG' THEN 'Core - Referenced by TABLE_REGISTRY'
        WHEN 'PROCEDURE_EXECUTION_LOG' THEN 'Standalone - Audit Trail'
        WHEN 'DATA_QUALITY_RULES' THEN 'Standalone - Quality Management'
        WHEN 'VW_TABLE_CATALOG' THEN 'View - Joins TABLE_REGISTRY + SERVICE_CATALOG + TABLE_STATISTICS'
        WHEN 'VW_COLUMN_CATALOG' THEN 'View - Joins COLUMN_METADATA + TABLE_REGISTRY'
        WHEN 'VW_SERVICE_SUMMARY' THEN 'View - Aggregates TABLE_REGISTRY + COLUMN_METADATA'
        ELSE 'Unknown'
    END as ERD_NOTES
FROM TABLE_REGISTRY
WHERE DATABASE_NAME = 'DEV_TRANSFORMATION'
  AND SCHEMA_NAME = 'METADATA'
ORDER BY OBJECT_TYPE, TABLE_NAME;

-- Export metadata repository ERD
SELECT * FROM VW_ERD_METADATA_REPOSITORY;


-- ========================================
-- SECTION 5: DATA LINEAGE (LANDING → TRANSFORMATION)
-- ========================================
-- Show data flow from Landing to Transformation layers

CREATE OR REPLACE VIEW VW_ERD_DATA_LINEAGE AS
WITH landing_tables AS (
    SELECT
        SERVICE_NAME,
        TABLE_NAME,
        FULL_TABLE_NAME,
        ROW_COUNT
    FROM TABLE_REGISTRY
    WHERE DATA_LAYER = 'Landing'
),
transformation_tables AS (
    SELECT
        SERVICE_NAME,
        TABLE_NAME,
        FULL_TABLE_NAME,
        ROW_COUNT
    FROM TABLE_REGISTRY
    WHERE DATA_LAYER = 'Transformation'
)
SELECT
    l.SERVICE_NAME,
    l.TABLE_NAME as LANDING_TABLE,
    l.FULL_TABLE_NAME as LANDING_FULL_NAME,
    l.ROW_COUNT as LANDING_ROWS,
    t.TABLE_NAME as TRANSFORMATION_TABLE,
    t.FULL_TABLE_NAME as TRANSFORMATION_FULL_NAME,
    t.ROW_COUNT as TRANSFORMATION_ROWS,
    -- Infer transformation pattern
    CASE
        WHEN t.TABLE_NAME LIKE l.TABLE_NAME || '%TRANSFORMED%' THEN 'Direct Transformation'
        WHEN t.TABLE_NAME LIKE l.TABLE_NAME || '%' THEN 'Enriched/Denormalized'
        WHEN t.TABLE_NAME LIKE '%' || l.TABLE_NAME || '%' THEN 'Aggregated'
        ELSE 'Unknown Pattern'
    END as TRANSFORMATION_PATTERN,
    -- Data completeness check
    CASE
        WHEN t.ROW_COUNT = 0 AND l.ROW_COUNT > 0 THEN 'Missing Transformation'
        WHEN t.ROW_COUNT > 0 AND l.ROW_COUNT = 0 THEN 'No Source Data'
        WHEN t.ROW_COUNT > l.ROW_COUNT THEN 'Expanded (Denormalized)'
        WHEN t.ROW_COUNT < l.ROW_COUNT THEN 'Filtered/Aggregated'
        WHEN t.ROW_COUNT = l.ROW_COUNT THEN '1:1 Mapping'
        ELSE 'Unknown'
    END as DATA_FLOW_TYPE
FROM landing_tables l
LEFT JOIN transformation_tables t
    ON l.SERVICE_NAME = t.SERVICE_NAME
    AND (
        t.TABLE_NAME LIKE l.TABLE_NAME || '%'
        OR t.TABLE_NAME LIKE '%' || l.TABLE_NAME || '%'
    )
ORDER BY l.SERVICE_NAME, l.TABLE_NAME;

-- Export data lineage
SELECT * FROM VW_ERD_DATA_LINEAGE;


-- ========================================
-- SECTION 6: SERVICE-GROUPED ERD DATA
-- ========================================
-- Tables grouped by service for modular ERD diagrams

CREATE OR REPLACE VIEW VW_ERD_BY_SERVICE AS
SELECT
    tr.SERVICE_NAME,
    sc.SERVICE_CATEGORY,
    COUNT(DISTINCT tr.TABLE_ID) as TABLE_COUNT,
    COUNT(DISTINCT CASE WHEN tr.DATA_LAYER = 'Landing' THEN tr.TABLE_ID END) as LANDING_TABLES,
    COUNT(DISTINCT CASE WHEN tr.DATA_LAYER = 'Transformation' THEN tr.TABLE_ID END) as TRANSFORMATION_TABLES,
    SUM(ts.COLUMN_COUNT) as TOTAL_COLUMNS,
    SUM(tr.ROW_COUNT) as TOTAL_ROWS,
    ROUND(SUM(tr.BYTES) / 1024 / 1024, 2) as TOTAL_SIZE_MB,
    -- Complexity score for ERD (higher = more complex diagram)
    (COUNT(DISTINCT tr.TABLE_ID) * 2) + (SUM(ts.COLUMN_COUNT) * 0.5) as COMPLEXITY_SCORE,
    -- ERD recommendation
    CASE
        WHEN COUNT(DISTINCT tr.TABLE_ID) <= 3 THEN 'Simple - Single Diagram'
        WHEN COUNT(DISTINCT tr.TABLE_ID) <= 10 THEN 'Moderate - Separate Landing/Transformation'
        ELSE 'Complex - Multiple Diagrams Recommended'
    END as ERD_RECOMMENDATION
FROM TABLE_REGISTRY tr
JOIN SERVICE_CATALOG sc ON tr.SERVICE_NAME = sc.SERVICE_NAME
LEFT JOIN TABLE_STATISTICS ts ON tr.TABLE_ID = ts.TABLE_ID
GROUP BY tr.SERVICE_NAME, sc.SERVICE_CATEGORY
ORDER BY TOTAL_ROWS DESC;

-- Export service summary for ERD planning
SELECT * FROM VW_ERD_BY_SERVICE;


-- ========================================
-- SECTION 7: ERD MERMAID GENERATION
-- ========================================
-- Generate Mermaid ERD syntax for markdown wikis

-- Example for a single service (SentinelOne)
-- This demonstrates the pattern - can be templated for all services

SELECT
    'erDiagram' as MERMAID_HEADER
UNION ALL
SELECT
    '    ' || TABLE_NAME || ' {' as MERMAID_LINE
FROM TABLE_REGISTRY
WHERE SERVICE_NAME = 'SentinelOne'
  AND DATA_LAYER = 'Landing'
ORDER BY MERMAID_HEADER DESC;

-- Column definitions for Mermaid
SELECT
    '        ' || DATA_TYPE || ' ' || COLUMN_NAME as MERMAID_COLUMN
FROM VW_ERD_COLUMN_DETAILS
WHERE SERVICE_NAME = 'SentinelOne'
  AND DATA_LAYER = 'Landing'
  AND TABLE_NAME = 'SENTINELONE_AGENTS'
ORDER BY ORDINAL_POSITION;

-- Relationship syntax
SELECT
    '    ' || SOURCE_TABLE || ' ||--o{ ' || TARGET_TABLE || ' : "' || FK_COLUMN || '"' as MERMAID_RELATIONSHIP
FROM VW_ERD_RELATIONSHIPS
WHERE SERVICE_NAME = 'SentinelOne';


-- ========================================
-- SECTION 8: COMPREHENSIVE ERD EXPORT
-- ========================================
-- Single comprehensive export for ERD generation tools

CREATE OR REPLACE VIEW VW_ERD_COMPLETE_EXPORT AS
SELECT
    tr.SERVICE_NAME,
    sc.SERVICE_CATEGORY,
    tr.DATA_LAYER,
    tr.TABLE_NAME,
    tr.FULL_TABLE_NAME,
    cm.COLUMN_NAME,
    cm.DATA_TYPE,
    cm.IS_NULLABLE,
    cm.ORDINAL_POSITION,
    -- Identify keys
    CASE
        WHEN cm.COLUMN_NAME LIKE '%_ID' AND cm.ORDINAL_POSITION = 1 THEN 'PK'
        WHEN cm.COLUMN_NAME LIKE '%_ID' AND cm.ORDINAL_POSITION > 1 THEN 'FK'
        WHEN cm.COLUMN_NAME LIKE '%_KEY' THEN 'PK'
        ELSE NULL
    END as KEY_TYPE,
    -- Table metadata
    tr.ROW_COUNT as TABLE_ROWS,
    ts.COLUMN_COUNT as TABLE_COLUMNS,
    ROUND(tr.BYTES / 1024 / 1024, 2) as TABLE_SIZE_MB
FROM TABLE_REGISTRY tr
JOIN SERVICE_CATALOG sc ON tr.SERVICE_NAME = sc.SERVICE_NAME
JOIN COLUMN_METADATA cm ON tr.TABLE_ID = cm.TABLE_ID
LEFT JOIN TABLE_STATISTICS ts ON tr.TABLE_ID = ts.TABLE_ID
ORDER BY tr.SERVICE_NAME, tr.DATA_LAYER, tr.TABLE_NAME, cm.ORDINAL_POSITION;

-- Final comprehensive export
SELECT * FROM VW_ERD_COMPLETE_EXPORT;


-- ========================================
-- SUMMARY STATISTICS FOR ERD
-- ========================================

SELECT
    '=== ERD GENERATION SUMMARY ===' as SECTION,
    '' as VALUE
UNION ALL
SELECT 'Total Services', CAST(COUNT(DISTINCT SERVICE_NAME) AS VARCHAR)
FROM TABLE_REGISTRY
UNION ALL
SELECT 'Total Tables', CAST(COUNT(*) AS VARCHAR)
FROM TABLE_REGISTRY
UNION ALL
SELECT 'Total Columns', CAST(COUNT(*) AS VARCHAR)
FROM COLUMN_METADATA
UNION ALL
SELECT 'Detected Relationships', CAST(COUNT(*) AS VARCHAR)
FROM VW_ERD_RELATIONSHIPS
UNION ALL
SELECT 'Landing Tables', CAST(COUNT(*) AS VARCHAR)
FROM TABLE_REGISTRY WHERE DATA_LAYER = 'Landing'
UNION ALL
SELECT 'Transformation Tables', CAST(COUNT(*) AS VARCHAR)
FROM TABLE_REGISTRY WHERE DATA_LAYER = 'Transformation'
UNION ALL
SELECT 'Metadata Repository Tables', CAST(COUNT(*) AS VARCHAR)
FROM TABLE_REGISTRY
WHERE DATABASE_NAME = 'DEV_TRANSFORMATION'
  AND SCHEMA_NAME = 'METADATA';


-- ========================================
-- USAGE INSTRUCTIONS
-- ========================================
/*

To use these ERD generation queries:

1. Execute this entire script to create all views

2. Export specific views based on your ERD needs:
   - VW_ERD_TABLE_CATALOG: Overall table structure
   - VW_ERD_COLUMN_DETAILS: Detailed column information
   - VW_ERD_RELATIONSHIPS: Detected relationships
   - VW_ERD_DATA_LINEAGE: Landing → Transformation flow
   - VW_ERD_BY_SERVICE: Service-grouped summaries
   - VW_ERD_COMPLETE_EXPORT: Single comprehensive export

3. Use the export with ERD tools:
   - dbdiagram.io (paste Mermaid syntax)
   - draw.io / Lucidchart (import CSV)
   - ERDPlus (import schema definitions)
   - Mermaid Live Editor (use Mermaid syntax output)

4. For Azure DevOps wiki, use Mermaid syntax:
   ```mermaid
   erDiagram
       [paste generated Mermaid code]
   ```

5. Update Data Model wiki with:
   - Service-specific ERDs (one per major service)
   - Overall architecture diagram (Landing → Transformation)
   - Metadata repository ERD (foundational)
   - Data lineage diagrams

*/

-- ========================================
-- END OF SCRIPT
-- ========================================
