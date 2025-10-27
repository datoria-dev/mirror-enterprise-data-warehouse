# 🌐 Deployment Symantec - Usando Web UI (Sin SnowSQL)

Ya que no tienes SnowSQL instalado, puedes desplegar usando **Snowflake Web UI**.

---

## 📋 Pasos para Deployment

### **Paso 1: Abrir Snowflake Web UI**

1. Abre tu navegador
2. Ve a: **https://app.snowflake.com**
3. Autentica con Okta usando `FUAD.ONATE@CompanyX.COM`
4. Selecciona tu cuenta: `GenericCorp-CRH_LEDW`

---

### **Paso 2: Crear un Stage (Si no existe)**

1. En Snowflake Web UI, ve a **Worksheets**
2. Crea un nuevo Worksheet
3. Ejecuta estos comandos:

```sql
USE ROLE PRD_DEVELOPER;
USE DATABASE ITSECKPI_DB;
USE SCHEMA ITSECKPI_SCHEMA;
USE WAREHOUSE COMPUTE_WH;

-- Crear stage si no existe
CREATE STAGE IF NOT EXISTS STREAMLIT_APPS_STAGE
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Stage for SECURITY_ANALYTICS Streamlit applications';

-- Verificar que el stage existe
SHOW STAGES LIKE 'STREAMLIT_APPS_STAGE';
```

---

### **Paso 3: Subir el Archivo por Web UI**

**IMPORTANTE**: Ya que no tienes SnowSQL, usaremos la Web UI para subir:

1. En Snowflake Web UI, ve a **Data** → **Databases**
2. Navega a: `ITSECKPI_DB` → `ITSECKPI_SCHEMA` → `Stages`
3. Click en `STREAMLIT_APPS_STAGE`
4. Click en **"+ Files"** o **"Upload Files"**
5. Navega a: `C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\13_STREAMLIT_COMPLETE\Symantec\`
6. Selecciona `streamlit_app.py`
7. En "Upload to" ingresa: `Symantec/` (con la barra al final)
8. Click **"Upload"**

**Alternativa - Crear carpeta primero**:
Si no te deja especificar la carpeta, puedes:
1. Subir el archivo a la raíz del stage
2. Luego moverlo con SQL:

```sql
-- Primero subir a raíz, luego ejecutar:
COPY FILES INTO '@STREAMLIT_APPS_STAGE/Symantec/'
FROM '@STREAMLIT_APPS_STAGE/'
FILES = ('streamlit_app.py');

-- Luego eliminar el archivo de la raíz
REMOVE '@STREAMLIT_APPS_STAGE/streamlit_app.py';
```

---

### **Paso 4: Verificar la Subida**

```sql
-- Listar archivos en el stage
LIST @STREAMLIT_APPS_STAGE/Symantec/;
```

**Deberías ver**: Una fila con `streamlit_app.py` y tamaño > 0 bytes

---

### **Paso 5: Crear el Streamlit App**

```sql
-- Eliminar app existente si existe
DROP STREAMLIT IF EXISTS STREAMLIT_SYMANTEC;

-- Crear el nuevo Streamlit app
CREATE STREAMLIT STREAMLIT_SYMANTEC
    ROOT_LOCATION = '@ITSECKPI_DB.ITSECKPI_SCHEMA.STREAMLIT_APPS_STAGE/Symantec'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = 'COMPUTE_WH'
    COMMENT = 'Symantec EDR Dashboard - v2.1 with fixes';
```

---

### **Paso 6: Obtener la URL**

```sql
-- Obtener la URL del Streamlit
SELECT 'https://' || CURRENT_ACCOUNT() || '.snowflakecomputing.com/streamlit/'
       || CURRENT_DATABASE() || '/' || CURRENT_SCHEMA() || '/STREAMLIT_SYMANTEC' AS STREAMLIT_URL;
```

**Copiar la URL** y ábrela en una nueva pestaña del navegador.

---

## 🎯 Método Alternativo: Usar Streamlit UI Directamente

Snowflake tiene una interfaz para crear Streamlit apps sin SQL:

### **Opción 1: Desde Streamlit Section**

1. En Snowflake Web UI, ve a **Streamlit** (menú lateral izquierdo)
2. Click en **"+ Streamlit App"**
3. Completa el formulario:
   - **Name**: `STREAMLIT_SYMANTEC`
   - **Database**: `ITSECKPI_DB`
   - **Schema**: `ITSECKPI_SCHEMA`
   - **Warehouse**: `COMPUTE_WH`
4. Se abrirá un editor
5. **Copia y pega** todo el contenido de `streamlit_app.py`
6. Click en **"Run"** o **"Deploy"**

**Ventaja**: No necesitas stages ni upload de archivos! ✨

---

## 📝 Código Completo para Copy-Paste

Si quieres todo en un solo bloque SQL:

```sql
-- Setup
USE ROLE PRD_DEVELOPER;
USE DATABASE ITSECKPI_DB;
USE SCHEMA ITSECKPI_SCHEMA;
USE WAREHOUSE COMPUTE_WH;

-- Crear stage
CREATE STAGE IF NOT EXISTS STREAMLIT_APPS_STAGE
    DIRECTORY = (ENABLE = TRUE);

-- Verificar stage
SHOW STAGES LIKE 'STREAMLIT_APPS_STAGE';

-- Después de subir el archivo manualmente por Web UI, ejecutar:
LIST @STREAMLIT_APPS_STAGE/Symantec/;

-- Crear Streamlit
DROP STREAMLIT IF EXISTS STREAMLIT_SYMANTEC;

CREATE STREAMLIT STREAMLIT_SYMANTEC
    ROOT_LOCATION = '@ITSECKPI_DB.ITSECKPI_SCHEMA.STREAMLIT_APPS_STAGE/Symantec'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = 'COMPUTE_WH';

-- Obtener URL
SELECT 'https://' || CURRENT_ACCOUNT() || '.snowflakecomputing.com/streamlit/'
       || CURRENT_DATABASE() || '/' || CURRENT_SCHEMA() || '/STREAMLIT_SYMANTEC' AS URL;
```

---

## ⚡ Método MÁS RÁPIDO (Recomendado)

### **Usar el Editor de Streamlit Directamente**:

1. **Ve a Streamlit en el menú lateral**
2. **Click "+ Streamlit App"**
3. **Copia TODA la app**:

```bash
# Abre el archivo en Notepad o VSCode:
C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\13_STREAMLIT_COMPLETE\Symantec\streamlit_app.py
```

4. **Selecciona todo (Ctrl+A) y copia (Ctrl+C)**
5. **Pega en el editor de Snowflake Streamlit**
6. **Configura**:
   - Name: `STREAMLIT_SYMANTEC`
   - Database: `ITSECKPI_DB`
   - Schema: `ITSECKPI_SCHEMA`
   - Warehouse: `COMPUTE_WH`
7. **Click "Run"**

**¡LISTO!** La app se desplegará automáticamente. 🎉

---

## 🐛 Troubleshooting

### **Problema: No encuentro la sección Streamlit**

**Solución**: Puede estar bajo "Projects" o "Apps" dependiendo de tu versión de Snowflake UI.

Busca en el menú lateral izquierdo:
- **Streamlit** (nombre directo)
- **Projects** → **Streamlit Apps**
- **Apps** → **Streamlit**

---

### **Problema: No puedo crear Streamlit apps**

**Causa**: Faltan permisos en tu rol `PRD_DEVELOPER`

**Solución**: Pide al admin que ejecute:
```sql
GRANT CREATE STREAMLIT ON SCHEMA ITSECKPI_SCHEMA TO ROLE PRD_DEVELOPER;
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE PRD_DEVELOPER;
```

---

### **Problema: El archivo no se sube correctamente**

**Solución**: Usa el método del **editor directo** (más arriba). Es más simple y no requiere stages.

---

## ✅ Testing Checklist

Después de desplegar:

### **Test 1: Refresh Button**
- [ ] Click en "🔄 Refresh Now" en sidebar
- [ ] **Resultado esperado**: App recarga sin error
- [ ] ✅ **NO debería ver**: `AttributeError: experimental_rerun`

### **Test 2: Download Buttons**
- [ ] **Tab 1**: Click "📥 Download Coverage CSV"
- [ ] **Tab 2**: Click "📥 Download Health Status CSV"
- [ ] **Tab 3**: Click "📥 Download Critical Endpoints CSV"
- [ ] **Resultado esperado**: Archivos CSV se descargan
- [ ] **Verificar**: Archivos se pueden abrir en Excel

### **Test 3: Alerts**
- [ ] **Tab 1**: Ver alert de coverage con color
- [ ] **Tab 3**: Ver alert de critical endpoints
- [ ] **Resultado esperado**: Mensajes aparecen con colores (rojo/naranja/verde)

---

## 🎯 Resumen

**Método Recomendado** (Sin SnowSQL):
1. Ve a **Streamlit** en Snowflake Web UI
2. Click **"+ Streamlit App"**
3. Copia y pega todo el código de `streamlit_app.py`
4. Configura nombre, database, schema, warehouse
5. Click **"Run"**
6. ✅ **¡Listo!**

**Ventajas**:
- ✅ No necesitas SnowSQL
- ✅ No necesitas subir archivos manualmente
- ✅ Más rápido y directo
- ✅ El editor tiene syntax highlighting

---

**¿Necesitas ayuda con algún paso específico?** 🚀

Avísame cuando hayas desplegado y probado los download buttons!
