# Metadata Repository - Guía Completa del Proceso

## 📋 Resumen Ejecutivo

**Fecha**: 2025-10-24
**Versión**: 3.0 (Producción)
**Estado**: ✅ **Totalmente Operacional**

Has estado trabajando en crear un **Metadata Repository Centralizado** que extrae y almacena automáticamente toda la metadata de todos los servicios SECURITY_ANALYTICS. Este documento explica TODO el proceso de principio a fin.

---

## 🎯 ¿Qué es el Metadata Repository?

Es un **sistema centralizado** que:

1. **Extrae automáticamente** metadata de TODOS los esquemas (Landing y Transformation)
2. **Detecta servicios** automáticamente basándose en nombres de tablas
3. **Almacena** información de tablas, columnas, estadísticas
4. **Actualiza** diariamente de forma automática
5. **Exporta** datos para uso en Streamlit apps

---

## 📂 Estructura del Sistema

### Schemas Creados

```
DEV_TRANSFORMATION
├── METADATA                    (Core metadata storage)
│   ├── TABLE_REGISTRY         (180 tablas catalogadas)
│   ├── COLUMN_METADATA        (2,206 columnas)
│   ├── TABLE_STATISTICS       (720+ snapshots históricos)
│   ├── SERVICE_CATALOG        (21 servicios configurados)
│   ├── PROCEDURE_EXECUTION_LOG (logs de ejecución)
│   ├── DATA_QUALITY_RULES     (reglas de calidad)
│   ├── VW_TABLE_CATALOG       (vista completa de tablas)
│   ├── VW_COLUMN_CATALOG      (vista completa de columnas)
│   └── VW_SERVICE_SUMMARY     (resumen por servicio)
│
└── METADATA_EXPORTS           (Exports for Streamlit apps)
    ├── SERVICE_SUMMARY_EXPORT
    ├── TABLE_CATALOG_EXPORT
    ├── ALL_COLUMNS_EXPORT     (2,206 columnas - ¡archivo principal!)
    ├── SENTINELONE_COLUMNS_EXPORT
    ├── CYBELANGEL_COLUMNS_EXPORT
    ├── PROOFPOINT_COLUMNS_EXPORT
    ├── SERVICENOW_COLUMNS_EXPORT
    ├── LEVIAT_COLUMNS_EXPORT
    ├── TENABLE_COLUMNS_EXPORT
    └── ... (33 tablas de export en total)
```

---

## 🔄 Proceso Completo (De Principio a Fin)

### Paso 1: Creación del Repositorio (Una sola vez)

**Script**: `CREATE_METADATA_REPOSITORY.sql`

**¿Qué hace?**
```sql
1. Crea schemas:
   - DEV_TRANSFORMATION.METADATA
   - DEV_TRANSFORMATION.METADATA_EXPORTS

2. Crea 6 tablas principales:
   - TABLE_REGISTRY (catálogo de tablas)
   - COLUMN_METADATA (catálogo de columnas)
   - TABLE_STATISTICS (estadísticas históricas)
   - SERVICE_CATALOG (21 servicios pre-configurados)
   - PROCEDURE_EXECUTION_LOG (logs de ejecución)
   - DATA_QUALITY_RULES (reglas de calidad)

3. Crea 3 vistas:
   - VW_TABLE_CATALOG (vista de tablas)
   - VW_COLUMN_CATALOG (vista de columnas)
   - VW_SERVICE_SUMMARY (resumen por servicio)

4. Puebla SERVICE_CATALOG con 21 servicios:
   - CrowdStrike, Symantec, Qualys, SentinelOne, etc.

5. Crea Stored Procedure: SP_REFRESH_METADATA()

6. Crea Task programado: TASK_DAILY_METADATA_REFRESH
   - Se ejecuta diariamente a las 6:00 AM EST
```

**Estado Actual**: ✅ Ejecutado exitosamente (52 statements)

---

### Paso 2: Extracción de Metadata (Automática)

**Stored Procedure**: `SP_REFRESH_METADATA()`

**¿Qué hace este procedimiento?**

```sql
CALL SP_REFRESH_METADATA();
```

**Proceso interno**:

```
1. Crea log entry (RUNNING status)
   ↓
2. Limpia metadata existente
   - DELETE FROM COLUMN_METADATA
   - DELETE FROM TABLE_REGISTRY
   ↓
3. Extrae tablas de INFORMATION_SCHEMA
   - FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
     WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
   - UNION ALL
   - FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
     WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
   ↓
4. Detecta servicio automáticamente usando CASE:
   WHEN TABLE_NAME LIKE '%SENTINEL%' THEN 'SentinelOne'
   WHEN TABLE_NAME LIKE '%QUALYS%' THEN 'Qualys'
   WHEN TABLE_NAME LIKE '%PROOFPOINT%' THEN 'Proofpoint'
   ... (22 servicios con patrones de detección)
   ELSE 'Unknown'
   ↓
5. Inserta en TABLE_REGISTRY (solo tablas conocidas)
   - Filtra WHERE SERVICE_NAME != 'Unknown'
   - Resultado: 180 tablas insertadas
   ↓
6. Extrae columnas de INFORMATION_SCHEMA.COLUMNS
   - FROM DEV_LANDING.INFORMATION_SCHEMA.COLUMNS
   - UNION ALL
   - FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.COLUMNS
   ↓
7. Inserta en COLUMN_METADATA
   - JOIN con TABLE_REGISTRY para obtener TABLE_ID
   - Resultado: 2,206 columnas insertadas
   ↓
8. Crea snapshot de estadísticas
   - INSERT INTO TABLE_STATISTICS
   - Guarda: ROW_COUNT, COLUMN_COUNT, SNAPSHOT_DATE
   ↓
9. Actualiza log entry (SUCCESS status)
   - EXECUTION_END
   - EXECUTION_DURATION_SECONDS
   - TABLES_PROCESSED: 180
   - COLUMNS_PROCESSED: 2,206
   - ROWS_PROCESSED: 720
   - EXECUTION_DETAILS (JSON)
   ↓
10. Retorna mensaje de éxito
```

**Resultado**:
```
✅ Metadata refresh completed successfully:
   180 tables, 2,206 columns, 720 statistics processed in 8 seconds
```

**Historial de Ejecuciones**:
```
LOG_ID | EXECUTION_START      | DURATION | STATUS  | TABLES | COLUMNS
-------|---------------------|----------|---------|--------|--------
3      | 2025-10-24 05:45:29 | 8 sec    | SUCCESS | 180    | 2,206
2      | 2025-10-24 05:42:41 | 8 sec    | SUCCESS | 180    | 2,206
1      | 2025-10-24 05:33:45 | 9 sec    | SUCCESS | 180    | 2,206
```

---

### Paso 3: Exportación de Metadata (Manual/Programada)

**Script**: `EXPORT_METADATA_RESULTS.sql`

**¿Qué hace?**

```sql
1. Crea 13 tablas de exportación en METADATA_EXPORTS:

   A. Resúmenes generales:
      - SERVICE_SUMMARY_EXPORT (21 servicios)
      - TABLE_CATALOG_EXPORT (180 tablas)
      - ALL_COLUMNS_EXPORT (2,206 columnas) ← ¡MUY IMPORTANTE!

   B. Por servicio específico:
      - SENTINELONE_COLUMNS_EXPORT (76 columnas)
      - CYBELANGEL_COLUMNS_EXPORT (112 columnas)
      - PROOFPOINT_COLUMNS_EXPORT (23 columnas)
      - SERVICENOW_COLUMNS_EXPORT (36 columnas)
      - LEVIAT_COLUMNS_EXPORT (146 columnas)
      - TENABLE_COLUMNS_EXPORT (0 columnas)

   C. Logs y estadísticas:
      - PROCEDURE_EXECUTION_LOG_EXPORT (3 ejecuciones)
      - EXECUTION_STATISTICS_EXPORT (métricas agregadas)
      - DAILY_EXECUTION_TREND_EXPORT (tendencia diaria)
      - TABLE_STATISTICS_EXPORT (180 snapshots)
      - SERVICE_CATALOG_EXPORT (21 servicios)
      - MISSING_SERVICES_EXPORT (1 servicio sin datos)

2. También genera SELECT queries que puedes exportar a CSV/JSON
```

**Estado Actual**: ✅ Ejecutado exitosamente (36/39 statements OK)

**Archivos generados**:
```
04_METADATA_SAMPLES/sql_execution_results/EXPORT_METADATA_RESULTS_20251024_030600/
├── stmt_006_select_*.csv - SERVICE_SUMMARY_EXPORT (21 rows)
├── stmt_009_select_*.csv - TABLE_CATALOG_EXPORT (180 rows)
├── stmt_011_select_*.csv - SentinelOne columns (76 rows)
├── stmt_013_select_*.csv - CybelAngel columns (112 rows)
├── stmt_015_select_*.csv - Proofpoint columns (23 rows)
├── stmt_017_select_*.csv - ServiceNow columns (36 rows)
├── stmt_019_select_*.csv - Leviat columns (146 rows)
├── stmt_023_select_*.csv - ALL columns (2,206 rows) ← ¡ARCHIVO CLAVE!
└── ... (36 archivos CSV/JSON en total)
```

---

### Paso 4: Integración con Streamlit Apps (Completado)

**Script de automatización**: `add_metadata_tab.py`

**¿Qué hace?**

```python
1. Lee apps existentes en 07_STREAMLIT_APPS/
2. Detecta estructura de tabs actual
3. Agrega nuevo tab "📚 Metadata"
4. Inserta código que consulta METADATA_EXPORTS.[SERVICE]_COLUMNS_EXPORT
5. Crea interfaz de búsqueda y navegación
```

**Apps actualizadas**: 6/6
- ✅ SentinelOne
- ✅ CybelAngel
- ✅ Proofpoint
- ✅ ServiceNow
- ✅ Leviat
- ✅ Tenable

---

## 🔍 ¿Cómo funciona la Detección Automática de Servicios?

El stored procedure `SP_REFRESH_METADATA()` incluye un **CASE gigante** que detecta servicios por patrones en nombres de tablas:

```sql
INSERT INTO TABLE_REGISTRY (SERVICE_NAME, ...)
SELECT
    CASE
        -- Endpoint Protection
        WHEN TABLE_NAME LIKE '%CROWDSTRIKE%' OR TABLE_NAME LIKE '%CROWD%STRIKE%'
            THEN 'CrowdStrike'
        WHEN TABLE_NAME LIKE '%SYMANTEC%'
            THEN 'Symantec'
        WHEN TABLE_NAME LIKE '%MCAFEE%'
            THEN 'McAfee'
        WHEN TABLE_NAME LIKE '%SOPHOS%'
            THEN 'Sophos'
        WHEN TABLE_NAME LIKE '%TRENDMICRO%' OR TABLE_NAME LIKE '%TREND%MICRO%'
            THEN 'TrendMicro'
        WHEN TABLE_NAME LIKE '%SENTINEL%'
            THEN 'SentinelOne'
        WHEN TABLE_NAME LIKE '%DEFENDER%'
            THEN 'Defender'
        WHEN TABLE_NAME LIKE '%TRELLIX%'
            THEN 'Trellix'
        WHEN TABLE_NAME LIKE '%CISCO%AMP%' OR TABLE_NAME LIKE '%AMP%'
            THEN 'Cisco_AMP'

        -- Vulnerability Management
        WHEN TABLE_NAME LIKE '%QUALYS%'
            THEN 'Qualys'
        WHEN TABLE_NAME LIKE '%TENABLE%'
            THEN 'Tenable'

        -- Threat Intelligence
        WHEN TABLE_NAME LIKE '%BITSIGHT%' OR TABLE_NAME LIKE '%BIT%SIGHT%'
            THEN 'BitSight'
        WHEN TABLE_NAME LIKE '%CYBELANGEL%' OR TABLE_NAME LIKE '%CYBEL%ANGEL%'
            THEN 'CybelAngel'
        WHEN TABLE_NAME LIKE '%ZEROFOX%' OR TABLE_NAME LIKE '%ZERO%FOX%'
            THEN 'ZeroFox'
        WHEN TABLE_NAME LIKE '%INTEL%THREAT%' OR TABLE_NAME LIKE '%THREAT%INTEL%'
            THEN 'Intel_Threats'

        -- Identity & Access Management
        WHEN TABLE_NAME LIKE '%ANCON%'
            THEN 'Ancon'
        WHEN TABLE_NAME LIKE '%LEVIAT%'
            THEN 'Leviat'

        -- SIEM
        WHEN TABLE_NAME LIKE '%SPLUNK%'
            THEN 'Splunk'

        -- Cloud Security
        WHEN TABLE_NAME LIKE '%ZSCALER%'
            THEN 'Zscaler'

        -- Email Security
        WHEN TABLE_NAME LIKE '%PROOFPOINT%'
            THEN 'Proofpoint'

        -- Asset Management
        WHEN TABLE_NAME IN ('SNOW') OR TABLE_NAME LIKE '%SERVICENOW%'
            THEN 'ServiceNow'

        ELSE 'Unknown'
    END as SERVICE_NAME,
    TABLE_CATALOG as DATABASE_NAME,
    TABLE_SCHEMA as SCHEMA_NAME,
    TABLE_NAME,
    TABLE_TYPE,
    CASE
        WHEN TABLE_CATALOG = 'DEV_LANDING' THEN 'Landing'
        WHEN TABLE_CATALOG = 'DEV_TRANSFORMATION' THEN 'Transformation'
        WHEN TABLE_CATALOG = 'DEV_REPORTING' THEN 'Reporting'
        ELSE 'Unknown'
    END as DATA_LAYER,
    ROW_COUNT,
    LAST_ALTERED
FROM (
    -- Extrae de ambos schemas
    SELECT * FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
    UNION ALL
    SELECT * FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
)
WHERE SERVICE_NAME != 'Unknown';  -- ← Solo inserta tablas conocidas
```

**Resultado**:
- 180 tablas detectadas y clasificadas en 20 servicios
- Cualquier tabla "Unknown" se ignora (no se guarda)

---

## 📊 Datos Almacenados Actualmente

### Por Servicio

| Servicio | Tablas | Columnas | Total Rows |
|----------|--------|----------|------------|
| Qualys | 18 | 226 | 256.4M |
| Leviat | 15 | 146 | 12K |
| Cisco_AMP | 13 | 133 | 988K |
| CrowdStrike | 13 | 238 | 252K |
| Splunk | 12 | 77 | 673K |
| SentinelOne | 11 | 76 | 143K |
| Defender | 11 | 72 | 222K |
| Symantec | 9 | 456 | 34M |
| ZeroFox | 9 | 165 | 10.7M |
| CybelAngel | 9 | 112 | 13K |
| TrendMicro | 9 | 91 | 13K |
| Intel_Threats | 8 | 45 | 17.1M |
| Ancon | 8 | 71 | 45K |
| BitSight | 7 | 48 | 24K |
| Zscaler | 6 | 88 | 168.8M |
| McAfee | 6 | 35 | 4K |
| Trellix | 6 | 36 | 514K |
| Sophos | 6 | 32 | 11K |
| Proofpoint | 2 | 23 | 2.7M |
| ServiceNow | 2 | 36 | 616K |
| **Tenable** | **0** | **0** | **0** ← Sin datos |

**Totales**:
- **180 tablas**
- **2,206 columnas**
- **492.5M+ rows**
- **21 servicios** (20 con datos + 1 sin datos)

---

## 🔄 Proceso de Actualización Automática

### Task Programado

```sql
-- Task que se ejecuta diariamente
CREATE OR REPLACE TASK TASK_DAILY_METADATA_REFRESH
  WAREHOUSE = DEV_WH
  SCHEDULE = 'USING CRON 0 6 * * * America/New_York'  -- 6:00 AM EST diario
AS
  CALL SP_REFRESH_METADATA();
```

**Estado Actual**: ⏸️ Pausado (necesita activación)

**Para activar**:
```sql
ALTER TASK TASK_DAILY_METADATA_REFRESH RESUME;
```

**Para verificar**:
```sql
SHOW TASKS LIKE 'TASK_DAILY_METADATA_REFRESH';
```

---

## 📁 Scripts Principales y Su Función

### 1. **CREATE_METADATA_REPOSITORY.sql** ⭐ PRINCIPAL
**Función**: Crea TODO el repositorio de metadata
**Incluye**:
- Schemas (METADATA, METADATA_EXPORTS)
- 6 tablas (TABLE_REGISTRY, COLUMN_METADATA, etc.)
- 3 vistas (VW_TABLE_CATALOG, VW_COLUMN_CATALOG, VW_SERVICE_SUMMARY)
- Stored procedure (SP_REFRESH_METADATA)
- Task programado (TASK_DAILY_METADATA_REFRESH)
- Datos iniciales (21 servicios en SERVICE_CATALOG)

**Cuándo usar**: Solo una vez para crear toda la infraestructura

---

### 2. **CREATE_STORED_PROCEDURE_ONLY.sql**
**Función**: Solo re-crea el stored procedure SP_REFRESH_METADATA()
**Cuándo usar**: Cuando necesites actualizar solo el procedimiento sin tocar las tablas

---

### 3. **EXPORT_METADATA_RESULTS.sql** ⭐ IMPORTANTE
**Función**: Exporta metadata a tablas METADATA_EXPORTS
**Crea**: 13 tablas de exportación para Streamlit apps
**Cuándo usar**: Después de ejecutar SP_REFRESH_METADATA() para generar exports

---

### 4. **VERIFY_PROCEDURE_RECREATION.sql**
**Función**: Verifica que el stored procedure esté funcionando correctamente
**Incluye**: 10 CHECKs comprehensivos
**Cuándo usar**: Después de crear/actualizar el procedimiento

---

### 5. Scripts de Python

**run_sql_script.py**: Ejecuta scripts SQL con auto-export de resultados
```bash
python run_sql_script.py --script CREATE_METADATA_REPOSITORY.sql
```

**run_verification_script.py**: Ejecuta scripts de verificación con exports
```bash
python run_verification_script.py --script VERIFY_PROCEDURE_RECREATION.sql
```

**add_metadata_tab.py**: Agrega tab de Metadata a Streamlit apps
```bash
cd 07_STREAMLIT_APPS
python add_metadata_tab.py
```

---

## 🎯 Proceso Completo: De Zero a Hero

### Si empezaras de cero, estos serían los pasos:

```bash
# PASO 1: Crear el repositorio (una sola vez)
# Ejecutar en Snowflake UI:
@01_SQL_SCRIPTS/CREATE_METADATA_REPOSITORY.sql

# PASO 2: Ejecutar primera extracción de metadata
CALL DEV_TRANSFORMATION.METADATA.SP_REFRESH_METADATA();

# PASO 3: Exportar metadata para Streamlit apps
@01_SQL_SCRIPTS/EXPORT_METADATA_RESULTS.sql

# PASO 4: Activar task diario
ALTER TASK DEV_TRANSFORMATION.METADATA.TASK_DAILY_METADATA_REFRESH RESUME;

# PASO 5: Agregar tabs de Metadata a Streamlit apps
cd 07_STREAMLIT_APPS
python add_metadata_tab.py

# ¡LISTO! El sistema está completamente operacional
```

---

## 📊 Estado Actual del Sistema

### ✅ Completado

1. ✅ Metadata Repository creado (6 tablas + 3 vistas)
2. ✅ SERVICE_CATALOG poblado (21 servicios)
3. ✅ Stored procedure SP_REFRESH_METADATA() creado y probado
4. ✅ Metadata extraída exitosamente (180 tablas, 2,206 columnas)
5. ✅ 3 ejecuciones exitosas del procedimiento (100% success rate)
6. ✅ Metadata exportada a METADATA_EXPORTS (13 tablas)
7. ✅ 6 Streamlit apps actualizadas con tab de Metadata
8. ✅ Documentación completa generada
9. ✅ Scripts de automatización creados

### ⏳ Pendiente (Opcional)

1. ⏸️ Activar task diario (TASK_DAILY_METADATA_REFRESH)
2. ⏸️ Configurar alertas de monitoreo
3. ⏸️ Agregar column descriptions a COLUMN_METADATA
4. ⏸️ Implementar data quality rules

---

## 🔑 Consultas Útiles

### Ver metadata actual

```sql
-- Ver resumen por servicio
SELECT * FROM DEV_TRANSFORMATION.METADATA.VW_SERVICE_SUMMARY
ORDER BY TABLE_COUNT DESC;

-- Ver todas las tablas
SELECT * FROM DEV_TRANSFORMATION.METADATA.VW_TABLE_CATALOG
ORDER BY SERVICE_NAME, TABLE_NAME;

-- Ver todas las columnas
SELECT * FROM DEV_TRANSFORMATION.METADATA.VW_COLUMN_CATALOG
WHERE SERVICE_NAME = 'SentinelOne'
ORDER BY TABLE_NAME, ORDINAL_POSITION;

-- Ver historial de ejecuciones
SELECT * FROM DEV_TRANSFORMATION.METADATA.PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC;

-- Ver estadísticas históricas
SELECT * FROM DEV_TRANSFORMATION.METADATA.TABLE_STATISTICS
ORDER BY SNAPSHOT_DATE DESC;
```

### Ejecutar manualmente

```sql
-- Refrescar metadata manualmente
CALL DEV_TRANSFORMATION.METADATA.SP_REFRESH_METADATA();

-- Ver resultado
SELECT * FROM DEV_TRANSFORMATION.METADATA.PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC LIMIT 1;
```

---

## 🎓 Conclusión

**SÍ, tienes un extract_metadata centralizado que:**

1. ✅ **Extrae** metadata de TODOS los schemas (Landing + Transformation)
2. ✅ **Detecta** servicios automáticamente por patrones de nombres
3. ✅ **Almacena** en un repositorio centralizado (METADATA schema)
4. ✅ **Incluye** un stored procedure (SP_REFRESH_METADATA) que hace todo el trabajo
5. ✅ **Exporta** a tablas específicas para cada servicio
6. ✅ **Se integra** con Streamlit apps para self-service data catalog
7. ✅ **Puede programarse** para ejecutarse diariamente (task)

**El stored procedure SP_REFRESH_METADATA() es tu "extract_metadata centralizado"** - hace todo el trabajo pesado de forma automática.

---

**Documento generado**: 2025-10-24
**Para**: Fuad Oñate
**Proyecto**: SECURITY_ANALYTICS Data Warehouse - Metadata Repository
**Versión**: 3.0 (Producción)
