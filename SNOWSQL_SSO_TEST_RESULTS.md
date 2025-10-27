# Resultados de Prueba - SnowSQL con SSO (Okta)

**Fecha:** 2025-10-25
**Usuario:** fuad.onate@CompanyX.com
**Metodo de Autenticacion:** SSO (Okta) via External Browser

## Estado General
✅ **EXITOSO** - La conexion SSO con Okta funciona correctamente

## Configuracion Utilizada

```json
{
  "user": "fuad.onate@CompanyX.com",
  "authenticator": "externalbrowser",
  "account": "GenericCorp-CRH_EDW",
  "warehouse": "DEV_WH",
  "database": "DEV_TRANSFORMATION",
  "schema": "METADATA",
  "role": "DEV_DEVELOPER"
}
```

## Pruebas Realizadas

### 1. Conexion Basica SSO
**Estado:** ✅ EXITOSO

```bash
snowsql -a GenericCorp-CRH_EDW -u fuad.onate@CompanyX.com --authenticator externalbrowser
```

**Resultado:**
- Usuario autenticado: FUAD.ONATE@CompanyX.COM
- Rol asignado: PRD_DEVELOPER (rol por defecto)
- Warehouse: DEV_WH
- Database: NULL (requiere especificacion)
- Schema: NULL (requiere especificacion)

### 2. Conexion con Parametros Completos
**Estado:** ✅ EXITOSO

```bash
snowsql -a GenericCorp-CRH_EDW -u fuad.onate@CompanyX.com --authenticator externalbrowser \
  -w DEV_WH -d DEV_TRANSFORMATION -s METADATA -r DEV_DEVELOPER
```

**Resultado:**
- Usuario: FUAD.ONATE@CompanyX.COM
- Rol: DEV_DEVELOPER ✅
- Warehouse: DEV_WH ✅
- Database: DEV_TRANSFORMATION ✅
- Schema: METADATA ✅

### 3. Acceso a Tablas METADATA
**Estado:** ✅ EXITOSO

```sql
SHOW TABLES IN SCHEMA DEV_TRANSFORMATION.METADATA;
```

**Tablas Encontradas:**
- COLUMN_METADATA (2,206 rows)
- DATA_QUALITY_RULES (0 rows)
- PROCEDURE_EXECUTION_LOG (3 rows)
- SERVICE_CATALOG (21 rows)
- TABLE_REGISTRY (180 rows)
- TABLE_STATISTICS (720 rows)

### 4. Consulta de Datos
**Estado:** ✅ EXITOSO

```sql
SELECT SERVICE_NAME, TABLE_NAME, ROW_COUNT, LAST_UPDATED
FROM TABLE_REGISTRY
LIMIT 10;
```

**Resultado:** Se obtuvieron 10 registros correctamente, incluyendo datos de:
- Qualys
- Splunk
- Symantec
- SentinelOne
- TrendMicro
- ZeroFox

### 5. Estructura de Tabla
**Estado:** ✅ EXITOSO

```sql
DESCRIBE TABLE TABLE_REGISTRY;
```

**Resultado:** Se obtuvieron 14 columnas con sus definiciones completas.

## Proceso de Autenticacion SSO

1. **Inicio:** SnowSQL inicia el proceso de autenticacion
2. **Redireccion:** Se abre automaticamente el navegador web
3. **URL Okta:** https://GenericCorp-corp.okta-emea.com/app/snowflake/...
4. **Login:** El usuario se autentica en Okta
5. **Callback:** Okta devuelve el token a SnowSQL
6. **Conexion:** SnowSQL establece la sesion con Snowflake

## Ventajas de SSO

✅ **Seguridad:** No se requieren credenciales locales
✅ **Conveniente:** Single Sign-On, una sola autenticacion
✅ **Centralizado:** Gestion de acceso desde Okta
✅ **Cumplimiento:** Alineado con politicas corporativas de GenericCorp

## Script de Conexion Rapida

Se ha creado el archivo `connect_snowsql_sso.bat` para facilitar futuras conexiones:

```batch
"C:\Program Files\Snowflake SnowSQL\snowsql.exe" ^
  -a GenericCorp-CRH_EDW ^
  -u fuad.onate@CompanyX.com ^
  --authenticator externalbrowser ^
  -w DEV_WH ^
  -d DEV_TRANSFORMATION ^
  -s METADATA ^
  -r DEV_DEVELOPER
```

## Comandos Utiles

### Verificar Contexto Actual
```sql
SELECT
  CURRENT_USER(),
  CURRENT_ROLE(),
  CURRENT_WAREHOUSE(),
  CURRENT_DATABASE(),
  CURRENT_SCHEMA();
```

### Listar Tablas
```sql
SHOW TABLES IN SCHEMA DEV_TRANSFORMATION.METADATA;
```

### Consultar Metadata
```sql
-- Ver servicios registrados
SELECT * FROM SERVICE_CATALOG;

-- Ver tablas activas
SELECT * FROM TABLE_REGISTRY WHERE IS_ACTIVE = TRUE;

-- Ver estadisticas
SELECT * FROM TABLE_STATISTICS ORDER BY LAST_UPDATED DESC LIMIT 10;
```

## Proximos Pasos

1. ✅ Configurar archivo de conexion ~/.snowsql/config (opcional)
2. ✅ Crear scripts de consultas comunes
3. ✅ Documentar procedimientos de metadata
4. ⬜ Integrar SnowSQL en scripts de automatizacion
5. ⬜ Configurar exports de datos

## Notas Tecnicas

- **Version SnowSQL:** v1.3.1
- **Ubicacion:** C:\Program Files\Snowflake SnowSQL\snowsql.exe
- **Timeout por defecto:** 60 segundos para autenticacion
- **Navegador:** Se utiliza el navegador por defecto del sistema
- **Token SSO:** Se mantiene activo durante la sesion

## Conclusion

La integracion de SnowSQL con SSO (Okta) esta completamente funcional y lista para uso en produccion. Todos los componentes del sistema de metadata son accesibles y las consultas se ejecutan correctamente.
