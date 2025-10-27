# Metadata Repository - Guía de Uso y Monitoreo

## 📋 Resumen

El **Metadata Repository** es un sistema centralizado de gestión de metadatos para el proyecto SECURITY_ANALYTICS que:

- ✅ Almacena información de **22 servicios** (tablas, columnas, tipos de datos)
- ✅ Actualiza automáticamente cada día a las 2 AM UTC
- ✅ Registra logs detallados de todas las ejecuciones
- ✅ Exporta resultados a JSON y CSV para análisis
- ✅ Sirve como referencia para desarrollo de apps Streamlit

---

## 🗂️ Estructura de Archivos

### Scripts SQL

1. **CREATE_METADATA_REPOSITORY.sql** (Principal)
   - Crea el repositorio completo
   - Incluye logging automático
   - Define 22 servicios
   - Configura refresh diario

2. **EXPORT_METADATA_RESULTS.sql**
   - Exporta metadatos a JSON/CSV
   - 12 tipos de exportaciones diferentes
   - Siempre almacena resultados en archivos

3. **VERIFY_METADATA_REPOSITORY.sql**
   - 20 verificaciones de calidad
   - Monitoreo de logs
   - Diagnóstico completo

4. **QUERY_METADATA_REPOSITORY.sql**
   - 20+ queries de ejemplo
   - Uso diario del repositorio

---

## 🚀 Instalación Paso a Paso

### Paso 1: Crear Metadata Repository

```sql
-- Ejecuta el script completo:
@CREATE_METADATA_REPOSITORY.sql

-- Este script:
-- ✅ Crea schemas: METADATA y METADATA_EXPORTS
-- ✅ Crea 6 tablas (incluyendo PROCEDURE_EXECUTION_LOG)
-- ✅ Crea 3 vistas
-- ✅ Crea stored procedure SP_REFRESH_METADATA() con logging
-- ✅ Crea task diario TASK_DAILY_METADATA_REFRESH
-- ✅ Ejecuta carga inicial de metadatos
```

**Resultados Esperados:**
- **TABLE_REGISTRY**: ~10-50 tablas detectadas
- **COLUMN_METADATA**: ~100-500 columnas
- **SERVICE_CATALOG**: 22 servicios definidos
- **PROCEDURE_EXECUTION_LOG**: 1 registro con STATUS='SUCCESS'

### Paso 2: Verificar Instalación

```sql
-- Ejecuta verificaciones:
@VERIFY_METADATA_REPOSITORY.sql

-- Revisa especialmente:
-- ✅ VERIFICATION 1: 22 servicios en catálogo
-- ✅ VERIFICATION 3: Servicios detectados con datos
-- ✅ VERIFICATION 4: Sin tablas "Unknown"
-- ✅ VERIFICATION 9: Log de ejecución exitoso
```

### Paso 3: Exportar Resultados

```sql
-- Ejecuta exportaciones:
@EXPORT_METADATA_RESULTS.sql

-- Guarda los resultados en:
-- 📁 04_METADATA_SAMPLES/json/ (4 archivos JSON)
-- 📁 04_METADATA_SAMPLES/metadata/ (11 archivos CSV)
-- 📁 04_METADATA_SAMPLES/logs/ (3 archivos de logs)
-- 📁 04_METADATA_SAMPLES/reports/ (1 archivo de reportes)
```

### Paso 4: Activar Refresh Diario

```sql
-- Activa la tarea diaria:
ALTER TASK DEV_TRANSFORMATION.METADATA.TASK_DAILY_METADATA_REFRESH RESUME;

-- Verifica estado:
SELECT NAME, STATE, SCHEDULE, NEXT_SCHEDULED_TIME
FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TASKS
WHERE NAME = 'TASK_DAILY_METADATA_REFRESH';

-- Debe mostrar:
-- STATE = 'started'
-- SCHEDULE = 'USING CRON 0 2 * * * UTC'
-- NEXT_SCHEDULED_TIME = próxima ejecución
```

---

## 📊 Tablas del Metadata Repository

### 1. TABLE_REGISTRY
**Propósito**: Registro maestro de todas las tablas

| Columna | Descripción |
|---------|-------------|
| TABLE_ID | ID único autoincremental |
| SERVICE_NAME | Nombre del servicio (SentinelOne, Proofpoint, etc.) |
| DATABASE_NAME | Database de Snowflake |
| SCHEMA_NAME | Schema de Snowflake |
| TABLE_NAME | Nombre de la tabla |
| TABLE_TYPE | TABLE, VIEW, MATERIALIZED VIEW |
| DATA_LAYER | Landing, Transformation, Reporting |
| ROW_COUNT | Número de filas |
| LAST_UPDATED | Última modificación |

### 2. COLUMN_METADATA
**Propósito**: Metadatos detallados de columnas

| Columna | Descripción |
|---------|-------------|
| COLUMN_ID | ID único autoincremental |
| TABLE_ID | FK a TABLE_REGISTRY |
| COLUMN_NAME | Nombre de la columna |
| DATA_TYPE | Tipo de dato (TEXT, NUMBER, etc.) |
| IS_NULLABLE | YES/NO |
| ORDINAL_POSITION | Posición en la tabla |

### 3. PROCEDURE_EXECUTION_LOG 🆕
**Propósito**: Log de todas las ejecuciones del stored procedure

| Columna | Descripción |
|---------|-------------|
| LOG_ID | ID único del log |
| PROCEDURE_NAME | Nombre del procedimiento ejecutado |
| EXECUTION_START | Inicio de ejecución |
| EXECUTION_END | Fin de ejecución |
| EXECUTION_DURATION_SECONDS | Duración en segundos |
| STATUS | SUCCESS, FAILED, RUNNING |
| TABLES_PROCESSED | Número de tablas procesadas |
| COLUMNS_PROCESSED | Número de columnas procesadas |
| ROWS_PROCESSED | Número de estadísticas procesadas |
| ERROR_MESSAGE | Mensaje de error (si falló) |
| EXECUTION_DETAILS | JSON con detalles completos |
| EXECUTED_BY | Usuario que ejecutó |

### 4. TABLE_STATISTICS
**Propósito**: Historial de estadísticas de tablas

| Columna | Descripción |
|---------|-------------|
| STAT_ID | ID único |
| TABLE_ID | FK a TABLE_REGISTRY |
| SNAPSHOT_DATE | Fecha del snapshot |
| ROW_COUNT | Número de filas en esa fecha |
| COLUMN_COUNT | Número de columnas |

### 5. SERVICE_CATALOG
**Propósito**: Catálogo de los 22 servicios

| Columna | Descripción |
|---------|-------------|
| SERVICE_ID | ID único |
| SERVICE_NAME | Nombre del servicio |
| SERVICE_DESCRIPTION | Descripción |
| SERVICE_CATEGORY | Categoría (Endpoint Protection, etc.) |
| IS_ACTIVE | TRUE/FALSE |
| REFRESH_FREQUENCY | Hourly, Daily |

### 6. DATA_QUALITY_RULES
**Propósito**: Reglas de calidad de datos (para uso futuro)

---

## 🔍 Monitoreo de Logs

### Ver Última Ejecución

```sql
SELECT
    LOG_ID,
    PROCEDURE_NAME,
    EXECUTION_START,
    EXECUTION_END,
    EXECUTION_DURATION_SECONDS,
    STATUS,
    TABLES_PROCESSED,
    COLUMNS_PROCESSED,
    ERROR_MESSAGE
FROM DEV_TRANSFORMATION.METADATA.PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 1;
```

### Ver Historial Completo (Últimos 30 días)

```sql
SELECT
    DATE(EXECUTION_START) as FECHA,
    COUNT(*) as EJECUCIONES,
    SUM(CASE WHEN STATUS = 'SUCCESS' THEN 1 ELSE 0 END) as EXITOSAS,
    SUM(CASE WHEN STATUS = 'FAILED' THEN 1 ELSE 0 END) as FALLIDAS,
    ROUND(AVG(EXECUTION_DURATION_SECONDS), 2) as DURACION_PROMEDIO,
    ROUND(AVG(TABLES_PROCESSED), 0) as TABLAS_PROMEDIO
FROM DEV_TRANSFORMATION.METADATA.PROCEDURE_EXECUTION_LOG
WHERE EXECUTION_START >= DATEADD(day, -30, CURRENT_DATE())
GROUP BY DATE(EXECUTION_START)
ORDER BY FECHA DESC;
```

### Alertas de Errores

```sql
-- Ver ejecuciones fallidas
SELECT
    LOG_ID,
    EXECUTION_START,
    EXECUTION_DURATION_SECONDS,
    ERROR_MESSAGE,
    EXECUTION_DETAILS
FROM DEV_TRANSFORMATION.METADATA.PROCEDURE_EXECUTION_LOG
WHERE STATUS = 'FAILED'
ORDER BY EXECUTION_START DESC;
```

### Ver Detalles JSON de Ejecución

```sql
SELECT
    LOG_ID,
    EXECUTION_START,
    STATUS,
    EXECUTION_DETAILS
FROM DEV_TRANSFORMATION.METADATA.PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 1;

-- EXECUTION_DETAILS contiene JSON como:
-- {
--   "tables_processed": 15,
--   "columns_processed": 250,
--   "stats_processed": 15,
--   "duration_seconds": 12,
--   "timestamp": "2025-10-24T10:30:45.123Z"
-- }
```

---

## 📤 Exportación de Resultados

### Siempre Guardar Resultados en Archivos

**IMPORTANTE**: Siguiendo la mejor práctica, **SIEMPRE** ejecuta queries y guarda los resultados:

#### Opción 1: Usar EXPORT_METADATA_RESULTS.sql

```sql
-- Este script ya incluye todas las exportaciones necesarias
@EXPORT_METADATA_RESULTS.sql

-- Sigue las instrucciones para guardar cada resultado en:
-- ✅ JSON: 04_METADATA_SAMPLES/json/
-- ✅ CSV: 04_METADATA_SAMPLES/metadata/
-- ✅ Logs: 04_METADATA_SAMPLES/logs/
```

#### Opción 2: Exportar Manualmente desde VS Code

1. Ejecuta la query en Snowflake extension de VS Code
2. Click derecho en resultados → "Export"
3. Selecciona formato (CSV o JSON)
4. Guarda en la carpeta correspondiente

#### Archivos de Exportación Recomendados

| Archivo | Descripción | Ubicación |
|---------|-------------|-----------|
| service_summary.json | Resumen de servicios | json/ |
| all_services_columns_complete.json | Todos los metadatos | json/ |
| dashboard_summary.json | Dashboard completo | json/ |
| procedure_execution_log.json | Logs en JSON | logs/ |
| service_summary_export.csv | Resumen de servicios | metadata/ |
| all_columns_complete.csv | Todas las columnas | metadata/ |
| procedure_execution_log.csv | Logs en CSV | logs/ |
| execution_statistics.csv | Estadísticas de ejecución | logs/ |
| daily_execution_trend.csv | Tendencia diaria | logs/ |

---

## 🔧 Uso Diario

### Para Desarrolladores de Streamlit Apps

```sql
-- 1. Obtener columnas para un servicio específico
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION
FROM DEV_TRANSFORMATION.METADATA.VW_COLUMN_CATALOG
WHERE SERVICE_NAME = 'SentinelOne'
  AND TABLE_NAME = 'FACT_SENTINEL_ENDPOINTS'
ORDER BY ORDINAL_POSITION;

-- 2. Generar lista de columnas para SELECT
SELECT LISTAGG('    ' || COLUMN_NAME, ',\n')
       WITHIN GROUP (ORDER BY ORDINAL_POSITION) as COLUMN_LIST
FROM DEV_TRANSFORMATION.METADATA.VW_COLUMN_CATALOG
WHERE TABLE_NAME = 'PROOFPOINT_MESSAGE_LOGS';

-- 3. Ver todas las tablas de un servicio
SELECT
    TABLE_NAME,
    TOTAL_ROWS,
    TOTAL_COLUMNS,
    FULL_TABLE_NAME
FROM DEV_TRANSFORMATION.METADATA.VW_TABLE_CATALOG
WHERE SERVICE_NAME = 'Proofpoint'
ORDER BY TOTAL_ROWS DESC;
```

### Para Analistas de Datos

```sql
-- 1. Ver resumen de todos los servicios
SELECT * FROM DEV_TRANSFORMATION.METADATA.VW_SERVICE_SUMMARY
ORDER BY TOTAL_ROWS DESC;

-- 2. Buscar columnas específicas en todo el proyecto
SELECT
    SERVICE_NAME,
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    FULL_TABLE_NAME
FROM DEV_TRANSFORMATION.METADATA.VW_COLUMN_CATALOG
WHERE COLUMN_NAME LIKE '%EMAIL%'
ORDER BY SERVICE_NAME, TABLE_NAME;

-- 3. Detectar tablas vacías
SELECT
    SERVICE_NAME,
    TABLE_NAME,
    TOTAL_COLUMNS,
    FULL_TABLE_NAME
FROM DEV_TRANSFORMATION.METADATA.VW_TABLE_CATALOG
WHERE TOTAL_ROWS = 0
ORDER BY SERVICE_NAME, TABLE_NAME;
```

---

## 🔄 Mantenimiento

### Refresh Manual (cuando sea necesario)

```sql
-- Ejecutar refresh manual
CALL DEV_TRANSFORMATION.METADATA.SP_REFRESH_METADATA();

-- Ver resultado del log inmediatamente
SELECT
    STATUS,
    TABLES_PROCESSED,
    COLUMNS_PROCESSED,
    EXECUTION_DURATION_SECONDS,
    ERROR_MESSAGE
FROM DEV_TRANSFORMATION.METADATA.PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 1;
```

### Monitorear Task Diaria

```sql
-- Ver historial de ejecuciones de la tarea
SELECT
    NAME,
    DATABASE_NAME,
    SCHEMA_NAME,
    STATE,
    SCHEDULED_TIME,
    COMPLETED_TIME,
    RETURN_VALUE,
    ERROR_CODE,
    ERROR_MESSAGE
FROM TABLE(DEV_TRANSFORMATION.INFORMATION_SCHEMA.TASK_HISTORY())
WHERE NAME = 'TASK_DAILY_METADATA_REFRESH'
ORDER BY SCHEDULED_TIME DESC
LIMIT 10;
```

### Pausar/Reanudar Task

```sql
-- Pausar tarea diaria
ALTER TASK DEV_TRANSFORMATION.METADATA.TASK_DAILY_METADATA_REFRESH SUSPEND;

-- Reanudar tarea diaria
ALTER TASK DEV_TRANSFORMATION.METADATA.TASK_DAILY_METADATA_REFRESH RESUME;

-- Verificar estado
SHOW TASKS LIKE 'TASK_DAILY_METADATA_REFRESH' IN DEV_TRANSFORMATION.METADATA;
```

---

## 🚨 Troubleshooting

### Problema 1: Stored Procedure Falla

**Síntoma**: STATUS = 'FAILED' en PROCEDURE_EXECUTION_LOG

**Solución**:
```sql
-- 1. Ver el error exacto
SELECT ERROR_MESSAGE, EXECUTION_DETAILS
FROM DEV_TRANSFORMATION.METADATA.PROCEDURE_EXECUTION_LOG
WHERE STATUS = 'FAILED'
ORDER BY EXECUTION_START DESC
LIMIT 1;

-- 2. Verificar permisos
SHOW GRANTS ON SCHEMA DEV_TRANSFORMATION.METADATA;
SHOW GRANTS ON SCHEMA DEV_LANDING.SECURITY_ANALYTICS;

-- 3. Ejecutar manualmente para debugging
CALL DEV_TRANSFORMATION.METADATA.SP_REFRESH_METADATA();
```

### Problema 2: Task No Se Ejecuta

**Síntoma**: No hay nuevos logs diarios

**Solución**:
```sql
-- 1. Verificar estado del task
SELECT NAME, STATE, NEXT_SCHEDULED_TIME
FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TASKS
WHERE NAME = 'TASK_DAILY_METADATA_REFRESH';

-- 2. Verificar warehouse activo
SHOW WAREHOUSES LIKE 'DEV_WH';

-- 3. Activar si está suspendido
ALTER TASK DEV_TRANSFORMATION.METADATA.TASK_DAILY_METADATA_REFRESH RESUME;
```

### Problema 3: Tablas Aparecen como "Unknown"

**Síntoma**: SERVICE_NAME = 'Unknown' en TABLE_REGISTRY

**Solución**:
```sql
-- 1. Ver qué tablas no se detectaron
SELECT TABLE_NAME, DATABASE_NAME, SCHEMA_NAME
FROM DEV_TRANSFORMATION.METADATA.TABLE_REGISTRY
WHERE SERVICE_NAME = 'Unknown';

-- 2. Actualizar patrón de detección en CREATE_METADATA_REPOSITORY.sql
-- Agregar nuevo WHEN clause en el CASE statement de SP_REFRESH_METADATA

-- 3. Re-ejecutar refresh
CALL DEV_TRANSFORMATION.METADATA.SP_REFRESH_METADATA();
```

---

## 📈 Métricas de Performance

### Dashboard de Performance

```sql
SELECT
    'Total Services' as METRIC,
    COUNT(DISTINCT SERVICE_NAME)::VARCHAR as VALUE
FROM DEV_TRANSFORMATION.METADATA.VW_SERVICE_SUMMARY
UNION ALL
SELECT
    'Total Tables',
    COUNT(*)::VARCHAR
FROM DEV_TRANSFORMATION.METADATA.TABLE_REGISTRY
UNION ALL
SELECT
    'Total Columns',
    COUNT(*)::VARCHAR
FROM DEV_TRANSFORMATION.METADATA.COLUMN_METADATA
UNION ALL
SELECT
    'Avg Refresh Duration (sec)',
    ROUND(AVG(EXECUTION_DURATION_SECONDS), 2)::VARCHAR
FROM DEV_TRANSFORMATION.METADATA.PROCEDURE_EXECUTION_LOG
WHERE STATUS = 'SUCCESS'
UNION ALL
SELECT
    'Success Rate %',
    ROUND(
        100.0 * COUNT(CASE WHEN STATUS = 'SUCCESS' THEN 1 END) / COUNT(*),
        2
    )::VARCHAR
FROM DEV_TRANSFORMATION.METADATA.PROCEDURE_EXECUTION_LOG;
```

---

## 🎯 Mejores Prácticas

### ✅ DO (Hacer)

1. **Siempre guarda resultados de queries en archivos** (JSON o CSV)
2. **Revisa logs diariamente** para detectar problemas temprano
3. **Exporta metadatos semanalmente** para análisis offline
4. **Usa las vistas** (VW_*) en lugar de tablas directamente
5. **Documenta nuevos servicios** en SERVICE_CATALOG cuando se agreguen

### ❌ DON'T (No Hacer)

1. **No edites directamente** TABLE_REGISTRY o COLUMN_METADATA
2. **No borres logs** antiguos (se usan para tendencias)
3. **No desactives el task** sin documentar el motivo
4. **No ignores ejecuciones fallidas**
5. **No uses queries sin guardar resultados**

---

## 📞 Soporte

### Recursos
- **Script principal**: CREATE_METADATA_REPOSITORY.sql
- **Guía de queries**: QUERY_METADATA_REPOSITORY.sql
- **Verificación**: VERIFY_METADATA_REPOSITORY.sql
- **Exportación**: EXPORT_METADATA_RESULTS.sql

### Contacto
- **Equipo**: GenericCorp Data Engineering Team
- **Fecha de creación**: 2025-10-24
- **Versión**: 1.0

---

## 📝 Changelog

### v1.0 - 2025-10-24
- ✅ Repositorio inicial con 22 servicios
- ✅ Sistema de logging completo
- ✅ Exportación automática a JSON/CSV
- ✅ Task diaria configurada
- ✅ Vistas de consulta optimizadas
- ✅ Documentación completa
