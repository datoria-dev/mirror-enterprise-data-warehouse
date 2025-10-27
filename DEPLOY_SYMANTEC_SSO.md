# 🚀 Deployment Symantec con SSO/Okta

## 📋 Tu Configuración Snowflake

- **Account**: `GenericCorp-CRH_LEDW` (MW76572)
- **Organization**: `GenericCorp`
- **Account URL**: `GenericCorp-CRH_LEDW.snowflakecomputing.com`
- **Login**: `FUAD.ONATE@CompanyX.COM`
- **Role**: `PRD_DEVELOPER`
- **Cloud Platform**: `AZURE`
- **Edition**: `Business Critical`
- **Authentication**: SSO (Okta)

---

## 🔐 Step 1: Conectar con SnowSQL usando SSO

Abre tu terminal (PowerShell o CMD) y ejecuta:

```bash
snowsql -a GenericCorp-CRH_LEDW -u FUAD.ONATE@CompanyX.COM --authenticator externalbrowser
```

**Qué pasará**:
1. Se abrirá una ventana del navegador
2. Te pedirá autenticarte con Okta
3. Después de autenticarte, la sesión de SnowSQL quedará conectada
4. Verás el prompt de SnowSQL: `FUAD.ONATE@CompanyX.COM#(no warehouse)@(no database).(no schema)>`

---

## 📦 Step 2: Configurar el Contexto

Una vez conectado en SnowSQL, ejecuta estos comandos:

```sql
-- Configurar el contexto
USE ROLE PRD_DEVELOPER;
USE DATABASE ITSECKPI_DB;
USE SCHEMA ITSECKPI_SCHEMA;
USE WAREHOUSE COMPUTE_WH;

-- Verificar que el warehouse esté corriendo
SHOW WAREHOUSES LIKE 'COMPUTE_WH';
```

**Nota**: Si no tienes permisos en `COMPUTE_WH`, usa el warehouse que tengas disponible.

---

## 📤 Step 3: Subir el Archivo Streamlit

**IMPORTANTE**: Este comando solo funciona en **SnowSQL**, no en la Web UI.

```sql
-- Crear el stage si no existe
CREATE STAGE IF NOT EXISTS ITSECKPI_DB.ITSECKPI_SCHEMA.STREAMLIT_APPS_STAGE
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Stage for SECURITY_ANALYTICS Streamlit applications';

-- Subir el archivo (copia y pega todo como un solo comando)
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Symantec/streamlit_app.py @ITSECKPI_DB.ITSECKPI_SCHEMA.STREAMLIT_APPS_STAGE/Symantec/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
```

**Salida esperada**:
```
streamlit_app.py(0.03MB): [##########] 100.00% Done (0.5s)
+------------------+------------------+-------------+-------------+--------------------+--------------------+----------+---------+
| source           | target           | source_size | target_size | source_compression | target_compression | status   | message |
|------------------+------------------+-------------+-------------+--------------------+--------------------+----------|---------|
| streamlit_app.py | streamlit_app.py | 32768       | 32768       | NONE               | NONE               | UPLOADED |         |
+------------------+------------------+-------------+-------------+--------------------+--------------------+----------+---------+
```

---

## ✅ Step 4: Verificar la Subida

```sql
-- Listar archivos en el stage
LIST @ITSECKPI_DB.ITSECKPI_SCHEMA.STREAMLIT_APPS_STAGE/Symantec/;
```

**Deberías ver**: `streamlit_app.py` con un tamaño mayor a 0 bytes

---

## 🎨 Step 5: Crear el Streamlit App

```sql
-- Eliminar app existente si existe
DROP STREAMLIT IF EXISTS ITSECKPI_DB.ITSECKPI_SCHEMA.STREAMLIT_SYMANTEC;

-- Crear el nuevo Streamlit app
CREATE STREAMLIT ITSECKPI_DB.ITSECKPI_SCHEMA.STREAMLIT_SYMANTEC
    ROOT_LOCATION = '@ITSECKPI_DB.ITSECKPI_SCHEMA.STREAMLIT_APPS_STAGE/Symantec'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = 'COMPUTE_WH'
    COMMENT = 'Symantec EDR Dashboard - v2.0 with Download Buttons';
```

**Salida esperada**: `STREAMLIT_SYMANTEC successfully created.`

---

## 🌐 Step 6: Obtener la URL del App

```sql
-- Obtener la URL del Streamlit
SELECT
    'https://' || CURRENT_ACCOUNT() || '.snowflakecomputing.com/streamlit/' ||
    CURRENT_DATABASE() || '/' || CURRENT_SCHEMA() || '/STREAMLIT_SYMANTEC' AS STREAMLIT_URL;
```

**Copiar la URL** y ábrela en tu navegador.

**URL esperada**: `https://GenericCorp-CRH_LEDW.snowflakecomputing.com/streamlit/ITSECKPI_DB/ITSECKPI_SCHEMA/STREAMLIT_SYMANTEC`

---

## 🧪 Step 7: Probar la App

### **Test 1: Abrir la App**
1. Abre la URL en Chrome/Edge
2. Autentica con Okta si te lo pide
3. Espera a que cargue (puede tomar 30-60 segundos la primera vez)

### **Test 2: Verificar Tabs**
Deberías ver 4 tabs:
- 📊 Coverage Overview (Endpoint Health)
- 📊 Endpoint Health
- ⚠️ High Risk
- 🔒 Ransomware

### **Test 3: Probar Download Button**
1. Ve al **Tab 1: Coverage Overview**
2. Scroll abajo hasta ver la tabla "Coverage Details by OPCO"
3. Debajo de la tabla, busca el botón **"📥 Download Coverage CSV"**
4. **CLICK en el botón**
5. **Resultado esperado**: Tu navegador descarga un archivo `symantec_coverage.csv`

### **Test 4: Verificar Alert**
1. En el mismo Tab 1, debajo del botón de download
2. **Resultado esperado**: Deberías ver un mensaje de alerta:
   - Si coverage < 90%: 🔴 **"⚠️ Coverage below target: X.X% (Target: 90%)"**
   - Si coverage < 95%: 🟠 **"⚡ Coverage needs improvement: X.X%"**
   - Si coverage ≥ 95%: 🟢 **"✅ Coverage meets target: X.X%"**

### **Test 5: Probar Otros Downloads**
- **Tab 2**: Busca **"📥 Download Health Status CSV"**
- **Tab 3**: Busca **"📥 Download Critical Endpoints CSV"**

### **Test 6: Probar Refresh**
1. En el **sidebar** (panel izquierdo)
2. Click en **"🔄 Refresh Now"**
3. La app debería recargar los datos

---

## 🐛 Troubleshooting

### **Problema: "Permission denied" al crear stage**

**Solución**: Pide al admin que te otorgue permisos:
```sql
GRANT CREATE STAGE ON SCHEMA ITSECKPI_SCHEMA TO ROLE PRD_DEVELOPER;
GRANT USAGE ON STAGE STREAMLIT_APPS_STAGE TO ROLE PRD_DEVELOPER;
```

---

### **Problema: "COMPUTE_WH does not exist or not authorized"**

**Solución**: Lista los warehouses disponibles y usa uno:
```sql
SHOW WAREHOUSES;

-- Usa uno de los disponibles
USE WAREHOUSE <nombre_disponible>;
```

---

### **Problema: "PUT file:// command failed"**

**Causa**: Estás en Web UI, no en SnowSQL.

**Solución**: Debes usar SnowSQL desde terminal:
```bash
snowsql -a GenericCorp-CRH_LEDW -u FUAD.ONATE@CompanyX.COM --authenticator externalbrowser
```

---

### **Problema: El download button no funciona**

**Posibles causas**:
1. **Cache del navegador**: Prueba en modo incógnito
2. **Pop-up blocker**: Permite pop-ups para Snowflake
3. **Extensiones del navegador**: Desactiva AdBlockers temporalmente

**Solución**:
1. Abre las DevTools (F12)
2. Ve a la pestaña "Console"
3. Click en el download button
4. Busca errores en rojo
5. Copia el error y podemos debuggear

---

### **Problema: La app muestra la versión antigua**

**Solución**: Forzar refresh del Streamlit:
```sql
ALTER STREAMLIT ITSECKPI_DB.ITSECKPI_SCHEMA.STREAMLIT_SYMANTEC REFRESH;
```

Luego refresca el navegador (Ctrl+F5 para limpiar cache).

---

## 📝 Comandos Rápidos (Copy-Paste Todo)

Si quieres copiar y pegar todos los comandos de una vez:

```sql
-- 1. Configurar contexto
USE ROLE PRD_DEVELOPER;
USE DATABASE ITSECKPI_DB;
USE SCHEMA ITSECKPI_SCHEMA;
USE WAREHOUSE COMPUTE_WH;

-- 2. Crear stage
CREATE STAGE IF NOT EXISTS STREAMLIT_APPS_STAGE
    DIRECTORY = (ENABLE = TRUE);

-- 3. Subir archivo (solo en SnowSQL, no Web UI)
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Symantec/streamlit_app.py @ITSECKPI_DB.ITSECKPI_SCHEMA.STREAMLIT_APPS_STAGE/Symantec/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;

-- 4. Verificar subida
LIST @STREAMLIT_APPS_STAGE/Symantec/;

-- 5. Crear Streamlit
DROP STREAMLIT IF EXISTS STREAMLIT_SYMANTEC;

CREATE STREAMLIT STREAMLIT_SYMANTEC
    ROOT_LOCATION = '@ITSECKPI_DB.ITSECKPI_SCHEMA.STREAMLIT_APPS_STAGE/Symantec'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = 'COMPUTE_WH';

-- 6. Obtener URL
SELECT 'https://' || CURRENT_ACCOUNT() || '.snowflakecomputing.com/streamlit/' || CURRENT_DATABASE() || '/' || CURRENT_SCHEMA() || '/STREAMLIT_SYMANTEC' AS URL;
```

---

## ✅ Checklist Final

Antes de decir que funciona, verifica:

- [ ] App abre sin errores
- [ ] Se ven 4 tabs claramente
- [ ] Tab 1 muestra tabla de Coverage
- [ ] Download button "📥 Download Coverage CSV" aparece
- [ ] **Click en download button descarga el archivo CSV**
- [ ] Alert de coverage aparece con color (rojo/naranja/verde)
- [ ] Tab 2 tiene download button "📥 Download Health Status CSV"
- [ ] Tab 3 tiene download button "📥 Download Critical Endpoints CSV"
- [ ] Sidebar tiene botón "Refresh Now"
- [ ] Sidebar tiene checkbox "Auto-refresh"

Si **TODOS** estos checkboxes están marcados: **¡ÉXITO! 🎉**

---

## 🎯 Si Todo Funciona

Una vez que Symantec funcione perfectamente, podemos:

1. ✅ Desplegar las otras 10 apps con download buttons
2. ✅ Agregar download buttons a las 7 apps restantes
3. ✅ Crear un script batch para deployment masivo
4. ✅ Documentar cualquier quirk específico de Snowflake

---

**¡Buena suerte con el deployment! 🚀**

Avísame cuando termines y dime:
1. ¿La app cargó correctamente?
2. ¿Los download buttons funcionan (descargan CSV)?
3. ¿Las alerts aparecen con colores?
