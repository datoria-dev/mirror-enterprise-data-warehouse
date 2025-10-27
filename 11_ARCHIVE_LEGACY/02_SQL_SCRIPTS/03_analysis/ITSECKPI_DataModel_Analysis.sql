-- =====================================================
-- SECURITY_ANALYTICS DATA MODEL ANALYSIS - COMPLETE SQL DOCUMENTATION
-- =====================================================
-- Propósito: Documentación completa del modelo de datos SECURITY_ANALYTICS en Snowflake
-- Fecha: 2024
-- Esquema: SECURITY_ANALYTICS
-- Bases de datos: DEV_LANDING, DEV_TRANSFORMATION, DEV_REPORTING
-- =====================================================

-- =====================================================
-- SECCIÓN 1: CONFIGURACIÓN INICIAL
-- =====================================================

-- 1.1 Configurar el contexto de trabajo
USE ROLE ACCOUNTADMIN; -- Cambiar según tu rol
USE WAREHOUSE COMPUTE_WH; -- Tu warehouse

-- =====================================================
-- SECCIÓN 2: INVENTARIO DE OBJETOS
-- =====================================================

-- 2.1 Vista consolidada de todas las tablas en SECURITY_ANALYTICS
CREATE OR REPLACE VIEW ITSECKPI_INVENTORY AS
WITH all_objects AS (
    -- DEV_LANDING
    SELECT
        'DEV_LANDING' as LAYER,
        TABLE_CATALOG as DATABASE_NAME,
        TABLE_SCHEMA as SCHEMA_NAME,
        TABLE_NAME,
        TABLE_TYPE,
        ROW_COUNT,
        BYTES,
        CREATED,
        LAST_ALTERED,
        COMMENT
    FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'

    UNION ALL

    -- DEV_TRANSFORMATION
    SELECT
        'DEV_TRANSFORMATION' as LAYER,
        TABLE_CATALOG,
        TABLE_SCHEMA,
        TABLE_NAME,
        TABLE_TYPE,
        ROW_COUNT,
        BYTES,
        CREATED,
        LAST_ALTERED,
        COMMENT
    FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'

    UNION ALL

    -- DEV_REPORTING
    SELECT
        'DEV_REPORTING' as LAYER,
        TABLE_CATALOG,
        TABLE_SCHEMA,
        TABLE_NAME,
        TABLE_TYPE,
        ROW_COUNT,
        BYTES,
        CREATED,
        LAST_ALTERED,
        COMMENT
    FROM DEV_REPORTING.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
)
SELECT
    LAYER,
    DATABASE_NAME,
    SCHEMA_NAME,
    TABLE_NAME,
    TABLE_TYPE,
    ROW_COUNT,
    ROUND(BYTES/1024/1024, 2) as SIZE_MB,
    CREATED,
    LAST_ALTERED,
    DATEDIFF(day, LAST_ALTERED, CURRENT_DATE()) as DAYS_SINCE_UPDATE,
    COMMENT
FROM all_objects
ORDER BY LAYER, TABLE_NAME;

-- Ejecutar para ver el inventario
SELECT * FROM ITSECKPI_INVENTORY;

-- =====================================================
-- SECCIÓN 3: ESTRUCTURA DE COLUMNAS
-- =====================================================

-- 3.1 Detalle de todas las columnas con metadata enriquecida
CREATE OR REPLACE VIEW ITSECKPI_COLUMNS_DETAIL AS
WITH all_columns AS (
    -- DEV_LANDING columns
    SELECT
        'DEV_LANDING' as LAYER,
        TABLE_CATALOG as DATABASE_NAME,
        TABLE_SCHEMA as SCHEMA_NAME,
        TABLE_NAME,
        COLUMN_NAME,
        ORDINAL_POSITION,
        COLUMN_DEFAULT,
        IS_NULLABLE,
        DATA_TYPE,
        CHARACTER_MAXIMUM_LENGTH,
        NUMERIC_PRECISION,
        NUMERIC_SCALE,
        COMMENT
    FROM DEV_LANDING.INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'

    UNION ALL

    -- DEV_TRANSFORMATION columns
    SELECT
        'DEV_TRANSFORMATION',
        TABLE_CATALOG,
        TABLE_SCHEMA,
        TABLE_NAME,
        COLUMN_NAME,
        ORDINAL_POSITION,
        COLUMN_DEFAULT,
        IS_NULLABLE,
        DATA_TYPE,
        CHARACTER_MAXIMUM_LENGTH,
        NUMERIC_PRECISION,
        NUMERIC_SCALE,
        COMMENT
    FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'

    UNION ALL

    -- DEV_REPORTING columns
    SELECT
        'DEV_REPORTING',
        TABLE_CATALOG,
        TABLE_SCHEMA,
        TABLE_NAME,
        COLUMN_NAME,
        ORDINAL_POSITION,
        COLUMN_DEFAULT,
        IS_NULLABLE,
        DATA_TYPE,
        CHARACTER_MAXIMUM_LENGTH,
        NUMERIC_PRECISION,
        NUMERIC_SCALE,
        COMMENT
    FROM DEV_REPORTING.INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
)
SELECT
    LAYER,
    DATABASE_NAME || '.' || SCHEMA_NAME || '.' || TABLE_NAME as FULL_TABLE_NAME,
    COLUMN_NAME,
    ORDINAL_POSITION as COL_POSITION,
    DATA_TYPE,
    CASE
        WHEN CHARACTER_MAXIMUM_LENGTH IS NOT NULL THEN DATA_TYPE || '(' || CHARACTER_MAXIMUM_LENGTH || ')'
        WHEN NUMERIC_PRECISION IS NOT NULL THEN DATA_TYPE || '(' || NUMERIC_PRECISION || ',' || COALESCE(NUMERIC_SCALE, 0) || ')'
        ELSE DATA_TYPE
    END as FULL_DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    -- Identificar posibles claves
    CASE
        WHEN UPPER(COLUMN_NAME) LIKE '%_ID' OR UPPER(COLUMN_NAME) LIKE '%_KEY' THEN 'POSSIBLE_KEY'
        WHEN UPPER(COLUMN_NAME) LIKE '%_SK' OR UPPER(COLUMN_NAME) LIKE '%_PK' THEN 'POSSIBLE_KEY'
        WHEN UPPER(COLUMN_NAME) = 'ID' THEN 'POSSIBLE_PK'
        ELSE NULL
    END as KEY_INDICATOR,
    COMMENT
FROM all_columns
ORDER BY LAYER, FULL_TABLE_NAME, ORDINAL_POSITION;

-- Ejecutar para ver detalles de columnas
SELECT * FROM ITSECKPI_COLUMNS_DETAIL;

-- =====================================================
-- SECCIÓN 4: ANÁLISIS DE RELACIONES
-- =====================================================

-- 4.1 Identificar posibles relaciones basadas en nombres de columnas
CREATE OR REPLACE VIEW ITSECKPI_POTENTIAL_RELATIONSHIPS AS
WITH key_columns AS (
    SELECT
        LAYER,
        DATABASE_NAME || '.' || SCHEMA_NAME || '.' || TABLE_NAME as FULL_TABLE_NAME,
        TABLE_NAME,
        COLUMN_NAME,
        DATA_TYPE,
        REGEXP_REPLACE(UPPER(COLUMN_NAME), '(_ID|_KEY|_CODE|_SK|_FK|_PK)$', '') as BASE_NAME
    FROM ITSECKPI_COLUMNS_DETAIL
    WHERE KEY_INDICATOR IS NOT NULL
),
potential_relationships AS (
    SELECT DISTINCT
        k1.LAYER as FROM_LAYER,
        k1.FULL_TABLE_NAME as FROM_TABLE,
        k1.COLUMN_NAME as FROM_COLUMN,
        k2.LAYER as TO_LAYER,
        k2.FULL_TABLE_NAME as TO_TABLE,
        k2.COLUMN_NAME as TO_COLUMN,
        CASE
            WHEN k1.BASE_NAME = UPPER(k2.TABLE_NAME) THEN 'HIGH'
            WHEN k1.BASE_NAME LIKE '%' || UPPER(k2.TABLE_NAME) || '%' THEN 'MEDIUM'
            WHEN UPPER(k2.TABLE_NAME) LIKE '%' || k1.BASE_NAME || '%' THEN 'MEDIUM'
            ELSE 'LOW'
        END as CONFIDENCE_LEVEL
    FROM key_columns k1
    JOIN key_columns k2
        ON k1.BASE_NAME = k2.BASE_NAME
        OR k1.BASE_NAME = UPPER(k2.TABLE_NAME)
        OR UPPER(k2.TABLE_NAME) LIKE '%' || k1.BASE_NAME || '%'
    WHERE k1.FULL_TABLE_NAME != k2.FULL_TABLE_NAME
        AND k1.DATA_TYPE = k2.DATA_TYPE
)
SELECT
    FROM_LAYER,
    FROM_TABLE,
    FROM_COLUMN,
    '→' as RELATION,
    TO_LAYER,
    TO_TABLE,
    TO_COLUMN,
    CONFIDENCE_LEVEL,
    FROM_LAYER || ' → ' || TO_LAYER as LAYER_FLOW
FROM potential_relationships
WHERE CONFIDENCE_LEVEL IN ('HIGH', 'MEDIUM')
ORDER BY CONFIDENCE_LEVEL DESC, FROM_TABLE, FROM_COLUMN;

-- Ejecutar para ver relaciones potenciales
SELECT * FROM ITSECKPI_POTENTIAL_RELATIONSHIPS;

-- =====================================================
-- SECCIÓN 5: ESTADÍSTICAS DE CALIDAD DE DATOS
-- =====================================================

-- 5.1 Análisis de calidad por tabla
-- Nota: Esta query es dinámica y debe ejecutarse para cada tabla específica

-- Template para análisis de calidad de una tabla
-- Reemplazar {DATABASE}, {SCHEMA}, {TABLE} con valores reales
/*
SELECT
    '{DATABASE}' as DATABASE_NAME,
    '{SCHEMA}' as SCHEMA_NAME,
    '{TABLE}' as TABLE_NAME,
    COUNT(*) as TOTAL_ROWS,
    COUNT(DISTINCT {primary_key_column}) as UNIQUE_ROWS,
    TOTAL_ROWS - UNIQUE_ROWS as DUPLICATE_ROWS,
    SUM(CASE WHEN {column_to_check} IS NULL THEN 1 ELSE 0 END) as NULL_COUNT,
    ROUND(NULL_COUNT * 100.0 / TOTAL_ROWS, 2) as NULL_PERCENTAGE,
    MIN({date_column}) as MIN_DATE,
    MAX({date_column}) as MAX_DATE,
    DATEDIFF(day, MIN_DATE, MAX_DATE) as DATE_RANGE_DAYS
FROM {DATABASE}.{SCHEMA}.{TABLE};
*/

-- =====================================================
-- SECCIÓN 6: ANÁLISIS DE DEPENDENCIAS
-- =====================================================

-- 6.1 Views y sus tablas base
CREATE OR REPLACE VIEW ITSECKPI_VIEW_DEPENDENCIES AS
SELECT
    v.TABLE_CATALOG as VIEW_DATABASE,
    v.TABLE_SCHEMA as VIEW_SCHEMA,
    v.TABLE_NAME as VIEW_NAME,
    d.REFERENCED_DATABASE_NAME,
    d.REFERENCED_SCHEMA_NAME,
    d.REFERENCED_OBJECT_NAME as REFERENCED_TABLE,
    d.REFERENCED_OBJECT_TYPE
FROM INFORMATION_SCHEMA.VIEWS v
LEFT JOIN (
    SELECT * FROM DEV_LANDING.INFORMATION_SCHEMA.OBJECT_DEPENDENCIES
    UNION ALL
    SELECT * FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.OBJECT_DEPENDENCIES
    UNION ALL
    SELECT * FROM DEV_REPORTING.INFORMATION_SCHEMA.OBJECT_DEPENDENCIES
) d
    ON v.TABLE_CATALOG = d.REFERENCING_DATABASE_NAME
    AND v.TABLE_SCHEMA = d.REFERENCING_SCHEMA_NAME
    AND v.TABLE_NAME = d.REFERENCING_OBJECT_NAME
WHERE v.TABLE_SCHEMA = 'SECURITY_ANALYTICS'
ORDER BY VIEW_DATABASE, VIEW_NAME, REFERENCED_TABLE;

-- =====================================================
-- SECCIÓN 7: TASKS Y PIPELINES
-- =====================================================

-- 7.1 Listar todos los tasks en el esquema
SELECT
    DATABASE_NAME,
    SCHEMA_NAME,
    NAME as TASK_NAME,
    STATE,
    SCHEDULE,
    WAREHOUSE,
    DEFINITION,
    CREATED,
    LAST_SUCCESSFUL_RUN,
    NEXT_SCHEDULED_TIME
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE SCHEMA_NAME = 'SECURITY_ANALYTICS'
ORDER BY DATABASE_NAME, TASK_NAME;

-- =====================================================
-- SECCIÓN 8: STAGES Y FILE FORMATS
-- =====================================================

-- 8.1 Listar stages
SHOW STAGES IN SCHEMA DEV_LANDING.SECURITY_ANALYTICS;
SHOW STAGES IN SCHEMA DEV_TRANSFORMATION.SECURITY_ANALYTICS;
SHOW STAGES IN SCHEMA DEV_REPORTING.SECURITY_ANALYTICS;

-- 8.2 Listar file formats
SHOW FILE FORMATS IN SCHEMA DEV_LANDING.SECURITY_ANALYTICS;
SHOW FILE FORMATS IN SCHEMA DEV_TRANSFORMATION.SECURITY_ANALYTICS;
SHOW FILE FORMATS IN SCHEMA DEV_REPORTING.SECURITY_ANALYTICS;

-- =====================================================
-- SECCIÓN 9: MÉTRICAS DE USO Y PERFORMANCE
-- =====================================================

-- 9.1 Análisis de uso de tablas (últimos 30 días)
SELECT
    DATABASE_NAME,
    SCHEMA_NAME,
    TABLE_NAME,
    COUNT(*) as QUERY_COUNT,
    COUNT(DISTINCT USER_NAME) as UNIQUE_USERS,
    AVG(TOTAL_ELAPSED_TIME)/1000 as AVG_QUERY_TIME_SEC,
    MAX(TOTAL_ELAPSED_TIME)/1000 as MAX_QUERY_TIME_SEC,
    SUM(ROWS_PRODUCED) as TOTAL_ROWS_PRODUCED
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE SCHEMA_NAME = 'SECURITY_ANALYTICS'
    AND QUERY_TYPE = 'SELECT'
    AND START_TIME > DATEADD(day, -30, CURRENT_DATE())
GROUP BY DATABASE_NAME, SCHEMA_NAME, TABLE_NAME
ORDER BY QUERY_COUNT DESC;

-- =====================================================
-- SECCIÓN 10: GENERACIÓN DE DOCUMENTACIÓN
-- =====================================================

-- 10.1 Generar DDL de todas las tablas para documentación
-- Para cada tabla, ejecutar:
-- SELECT GET_DDL('TABLE', 'DEV_LANDING.SECURITY_ANALYTICS.{table_name}');

-- 10.2 Script para generar todos los DDLs
SELECT
    'SELECT GET_DDL(''' || TABLE_TYPE || ''', ''' ||
    DATABASE_NAME || '.' || SCHEMA_NAME || '.' || TABLE_NAME ||
    ''') as DDL_' || TABLE_NAME || ';' as GENERATE_DDL_COMMAND
FROM ITSECKPI_INVENTORY
ORDER BY LAYER, TABLE_NAME;

-- =====================================================
-- SECCIÓN 11: REPORTE EJECUTIVO
-- =====================================================

-- 11.1 Resumen ejecutivo del modelo de datos
WITH summary AS (
    SELECT
        COUNT(DISTINCT DATABASE_NAME) as TOTAL_DATABASES,
        COUNT(DISTINCT TABLE_NAME) as TOTAL_OBJECTS,
        COUNT(DISTINCT CASE WHEN TABLE_TYPE = 'BASE TABLE' THEN TABLE_NAME END) as TOTAL_TABLES,
        COUNT(DISTINCT CASE WHEN TABLE_TYPE = 'VIEW' THEN TABLE_NAME END) as TOTAL_VIEWS,
        SUM(SIZE_MB) as TOTAL_SIZE_MB,
        MAX(ROW_COUNT) as MAX_ROW_COUNT,
        MIN(CREATED) as OLDEST_OBJECT_DATE,
        MAX(LAST_ALTERED) as NEWEST_UPDATE_DATE
    FROM ITSECKPI_INVENTORY
),
layer_summary AS (
    SELECT
        LAYER,
        COUNT(*) as OBJECT_COUNT,
        SUM(SIZE_MB) as LAYER_SIZE_MB
    FROM ITSECKPI_INVENTORY
    GROUP BY LAYER
)
SELECT
    'SECURITY_ANALYTICS Schema Analysis Report' as REPORT_TITLE,
    CURRENT_TIMESTAMP() as REPORT_DATE,
    s.TOTAL_DATABASES,
    s.TOTAL_OBJECTS,
    s.TOTAL_TABLES,
    s.TOTAL_VIEWS,
    ROUND(s.TOTAL_SIZE_MB, 2) as TOTAL_SIZE_MB,
    s.MAX_ROW_COUNT,
    s.OLDEST_OBJECT_DATE,
    s.NEWEST_UPDATE_DATE,
    LISTAGG(l.LAYER || ': ' || l.OBJECT_COUNT || ' objects (' ||
            ROUND(l.LAYER_SIZE_MB, 2) || ' MB)', ' | ')
        WITHIN GROUP (ORDER BY l.LAYER) as LAYER_DISTRIBUTION
FROM summary s
CROSS JOIN layer_summary l
GROUP BY ALL;

-- =====================================================
-- SECCIÓN 12: SCRIPTS DE MANTENIMIENTO
-- =====================================================

-- 12.1 Identificar tablas sin estadísticas actualizadas
SELECT
    DATABASE_NAME,
    SCHEMA_NAME,
    TABLE_NAME,
    ROW_COUNT,
    LAST_ALTERED,
    DATEDIFF(day, LAST_ALTERED, CURRENT_DATE()) as DAYS_SINCE_UPDATE
FROM ITSECKPI_INVENTORY
WHERE DAYS_SINCE_UPDATE > 7
ORDER BY DAYS_SINCE_UPDATE DESC;

-- 12.2 Generar comandos para actualizar estadísticas
SELECT
    'ANALYZE TABLE ' || DATABASE_NAME || '.' || SCHEMA_NAME || '.' ||
    TABLE_NAME || ' COMPUTE STATISTICS;' as ANALYZE_COMMAND
FROM ITSECKPI_INVENTORY
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY DATABASE_NAME, TABLE_NAME;

-- =====================================================
-- SECCIÓN 13: EXPORTAR RESULTADOS
-- =====================================================

-- 13.1 Crear tabla temporal con todos los resultados para exportación
CREATE OR REPLACE TEMPORARY TABLE ITSECKPI_EXPORT AS
SELECT
    'INVENTORY' as REPORT_TYPE,
    OBJECT_CONSTRUCT(*) as DATA
FROM ITSECKPI_INVENTORY
UNION ALL
SELECT
    'COLUMNS' as REPORT_TYPE,
    OBJECT_CONSTRUCT(*) as DATA
FROM ITSECKPI_COLUMNS_DETAIL
UNION ALL
SELECT
    'RELATIONSHIPS' as REPORT_TYPE,
    OBJECT_CONSTRUCT(*) as DATA
FROM ITSECKPI_POTENTIAL_RELATIONSHIPS;

-- 13.2 Exportar a archivo (ajustar path según tu stage)
-- COPY INTO @my_stage/itseckpi_model_export.json
-- FROM ITSECKPI_EXPORT
-- FILE_FORMAT = (TYPE = JSON);

-- =====================================================
-- FIN DEL SCRIPT DE ANÁLISIS
-- =====================================================

-- Notas de uso:
-- 1. Ejecutar las secciones según necesidad
-- 2. Las vistas creadas quedan disponibles para consultas futuras
-- 3. Ajustar nombres de bases de datos y esquemas según tu entorno
-- 4. Documentar cambios en el modelo de datos
-- 5. Ejecutar periódicamente para mantener documentación actualizada