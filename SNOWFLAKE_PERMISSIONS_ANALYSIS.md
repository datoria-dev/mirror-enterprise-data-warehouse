# Análisis de Permisos Snowflake - SECURITY_ANALYTICS Data Warehouse

## Fecha: October 24, 2025

---

## Permisos Actuales (Lo Que Tenemos)

### ✅ Rol Actual: DEV_DEVELOPER

**Permisos Confirmados**:
- ✅ **DEV_TRANSFORMATION**: Crear schemas, tablas, vistas
- ✅ **DEV_REPORTING**: Crear schemas, vistas
- ✅ **DEV_WH**: Usar warehouse para queries y transformaciones
- ✅ **SSO (Okta)**: Autenticación via externalbrowser

**Limitaciones Encontradas**:
- ❌ **DEV_LANDING**: NO podemos crear schemas (error: insufficient privileges)
- ❌ **ACCOUNTADMIN**: NO podemos crear databases o warehouses
- ❌ **SYSADMIN**: NO podemos transferir ownership de objetos
- ❌ **CREATE TASK**: No sabemos si tenemos este privilegio (no probado)
- ❌ **CREATE PIPE**: No sabemos si tenemos este privilegio (no probado)
- ❌ **CREATE STREAM**: No sabemos si tenemos este privilegio (no probado)

---

## Permisos Necesarios para ServiceNow (Próximas 2 Semanas)

### 🔴 CRÍTICO - BLOQUEANTE

#### 1. **ACCOUNTADMIN** (Temporal - Solo para Instalación)
**Necesidad**: Instalar "Snowflake Connector for ServiceNow" desde Marketplace
**Alternativa**: Que un admin con ACCOUNTADMIN lo instale por nosotros
**Recomendación**: ✅ **Usar alternativa** (email ya preparado para admin)
**Estado**: ⏳ Pendiente (email listo para enviar)

#### 2. **CREATE TASK** en DEV_TRANSFORMATION
**Necesidad**: Crear Snowflake Tasks para transformaciones automáticas (RAW → Transformed)
**Frecuencia**: Tasks cada 15-240 minutos
**Bloqueante**: SÍ - Sin esto no hay automatización
**Prioridad**: 🔴 ALTA
**Estado**: ❌ NO VERIFICADO

#### 3. **EXECUTE TASK** en DEV_TRANSFORMATION
**Necesidad**: Ejecutar y pausar/reanudar tasks
**Bloqueante**: SÍ - Complementa CREATE TASK
**Prioridad**: 🔴 ALTA
**Estado**: ❌ NO VERIFICADO

#### 4. **CREATE SCHEMA** en DEV_LANDING
**Necesidad**: Crear schemas por servicio (SERVICENOW, CROWDSTRIKE, etc.)
**Workaround Actual**: Usamos DEV_TRANSFORMATION como landing + transformation
**Bloqueante**: NO (tenemos workaround)
**Prioridad**: 🟡 MEDIA
**Estado**: ❌ CONFIRMADO que NO lo tenemos

---

## Permisos Deseables (No Bloqueantes)

### 🟡 IMPORTANTE - PARA DESARROLLO COMPLETO

#### 5. **CREATE STREAM** en DEV_TRANSFORMATION
**Necesidad**: Change Data Capture avanzado para transformaciones incrementales
**Beneficio**: Mejor performance, solo procesar cambios
**Bloqueante**: NO (podemos usar MERGE sin streams)
**Prioridad**: 🟡 MEDIA
**Estado**: ❌ NO VERIFICADO

#### 6. **CREATE PIPE** en DEV_LANDING
**Necesidad**: Snowpipe para cargas automáticas desde S3/Azure (si usamos archivos)
**Uso Proyectado**: APIs de archivos CSV/JSON (CrowdStrike, Proofpoint)
**Bloqueante**: NO (Python framework carga directamente)
**Prioridad**: 🟡 MEDIA
**Estado**: ❌ NO VERIFICADO

#### 7. **CREATE FUNCTION** / **CREATE PROCEDURE** en DEV_TRANSFORMATION
**Necesidad**: UDFs y Stored Procedures para lógica compleja
**Uso Proyectado**: Transformaciones complejas, validaciones
**Bloqueante**: NO (podemos usar SQL directo en tasks)
**Prioridad**: 🟢 BAJA
**Estado**: ❌ NO VERIFICADO

#### 8. **CREATE STAGE** en DEV_LANDING
**Necesidad**: External stages para archivos en S3/Azure Blob
**Uso Proyectado**: Si APIs devuelven archivos grandes
**Bloqueante**: NO
**Prioridad**: 🟢 BAJA
**Estado**: ❌ NO VERIFICADO

---

## Permisos para Monitoreo y Debugging

### 🟢 ÚTIL - CALIDAD DE VIDA

#### 9. **MONITOR** en ACCOUNT
**Necesidad**: Ver QUERY_HISTORY, TASK_HISTORY, WAREHOUSE_METERING
**Beneficio**: Debugging, optimización de costos
**Bloqueante**: NO
**Prioridad**: 🟢 BAJA
**Estado**: ❌ NO VERIFICADO

#### 10. **USAGE** en INFORMATION_SCHEMA (todos los databases)
**Necesidad**: Queries de metadata completas
**Beneficio**: Mejor análisis de lineage, documentación
**Bloqueante**: NO (tenemos acceso básico)
**Prioridad**: 🟢 BAJA
**Estado**: ⚠️ PARCIAL (tenemos en DEV_TRANSFORMATION y DEV_REPORTING)

---

## Verificación de Permisos Actuales

### Script de Verificación

```sql
-- Ver todos los privilegios del rol actual
SHOW GRANTS TO ROLE DEV_DEVELOPER;

-- Ver roles asignados al usuario
SHOW GRANTS TO USER CURRENT_USER();

-- Ver privilegios específicos de TASK
SHOW GRANTS ON ACCOUNT;

-- Ver privilegios en databases
SHOW GRANTS ON DATABASE DEV_LANDING;
SHOW GRANTS ON DATABASE DEV_TRANSFORMATION;
SHOW GRANTS ON DATABASE DEV_REPORTING;

-- Intentar crear task (prueba)
USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA SERVICENOW;
CREATE OR REPLACE TASK TEST_TASK_PERMISSION
  WAREHOUSE = DEV_WH
  SCHEDULE = '1440 MINUTE'  -- Diario
AS
SELECT 'Permission test';

-- Si funciona, eliminar
DROP TASK IF EXISTS TEST_TASK_PERMISSION;
```

---

## Recomendaciones de Permisos a Solicitar

### 🔴 PRIORIDAD ALTA (Solicitar AHORA)

#### Permiso #1: CREATE TASK + EXECUTE TASK
**Justificación**:
- Necesario para automatización de transformaciones ServiceNow
- Sin esto, tendríamos que ejecutar transformaciones manualmente
- Bloqueante para Week 2 de implementación

**Email**: ✅ Preparar email separado

---

#### Permiso #2: CREATE SCHEMA en DEV_LANDING
**Justificación**:
- Seguir arquitectura medallion correcta (Landing → Transformation → Reporting)
- Separar datos raw de datos transformados
- Mejor organización y governance

**Workaround Actual**: Usamos DEV_TRANSFORMATION como landing
**Email**: ✅ Preparar email separado

---

### 🟡 PRIORIDAD MEDIA (Solicitar LUEGO)

#### Permiso #3: CREATE STREAM
**Justificación**:
- Mejor performance para transformaciones incrementales
- Reducción de costos de compute
- No bloqueante (podemos vivir sin esto)

**Email**: ⏳ Esperar a semana 2

---

#### Permiso #4: CREATE PIPE
**Justificación**:
- Snowpipe para cargas automáticas de archivos
- Solo si APIs devuelven archivos grandes
- No bloqueante (Python framework suficiente)

**Email**: ⏳ Esperar a necesidad real

---

### 🟢 PRIORIDAD BAJA (No Urgente)

- CREATE FUNCTION / PROCEDURE
- CREATE STAGE
- MONITOR en ACCOUNT
- USAGE extendido en INFORMATION_SCHEMA

---

## Impacto si NO Obtenemos Permisos

### Sin CREATE TASK:
- ❌ No hay automatización de transformaciones
- ❌ Tendríamos que ejecutar SQL manualmente cada 15-30 minutos
- ❌ Riesgo de datos desactualizados
- ❌ Mayor carga operacional
- **Solución**: Usar Python con cron jobs (más complejo)

### Sin CREATE SCHEMA en DEV_LANDING:
- ⚠️ Arquitectura no ideal (mezclar raw + transformed)
- ⚠️ Peor separación de concerns
- ⚠️ Documentación menos clara
- **Solución**: ✅ Workaround actual funciona (usamos DEV_TRANSFORMATION)

### Sin CREATE STREAM:
- ⚠️ Performance subóptima en transformaciones
- ⚠️ Mayor costo de compute (procesamos todo vs solo cambios)
- **Solución**: ✅ MERGE statements funcionan (menos eficiente pero OK)

### Sin CREATE PIPE:
- ⚠️ No hay Snowpipe (auto-ingest de archivos)
- **Solución**: ✅ Python framework carga via API directamente

---

## Timeline de Solicitud de Permisos

### HOY (Oct 24)
- ✅ Email a Daragh (ServiceNow OAuth)
- ✅ Email a Snowflake Admin (Connector installation)
- ✅ **Email para CREATE TASK** (nuevo)
- ⏳ **Email para CREATE SCHEMA en DEV_LANDING** (nuevo)

### Próxima Semana (Oct 28-31)
- Recibir respuestas de permisos
- Probar CREATE TASK con permiso nuevo
- Si tenemos CREATE SCHEMA, reestructurar a 3-layer completo

### Semana 2 (Nov 4-8)
- Si necesitamos CREATE STREAM, solicitarlo
- Si necesitamos CREATE PIPE, solicitarlo

---

## Conclusión

### ✅ Permisos CRÍTICOS a Solicitar AHORA:

1. **CREATE TASK + EXECUTE TASK** en DEV_TRANSFORMATION
   - **Razón**: Automatización de transformaciones (bloqueante Week 2)
   - **Email**: ✅ PREPARAR

2. **CREATE SCHEMA** en DEV_LANDING
   - **Razón**: Arquitectura medallion correcta
   - **Email**: ✅ PREPARAR
   - **Alternativa**: Workaround actual funciona

### ⏳ Permisos DESEABLES (No Urgentes):
- CREATE STREAM (performance)
- CREATE PIPE (Snowpipe)
- CREATE FUNCTION/PROCEDURE (UDFs)
- MONITOR (debugging)

### ❌ Permisos que NO Necesitamos:
- ACCOUNTADMIN (admin lo instalará)
- SYSADMIN (no necesitamos transferir ownership)

---

**Siguiente Paso**: Crear emails para solicitar CREATE TASK y CREATE SCHEMA en DEV_LANDING.
