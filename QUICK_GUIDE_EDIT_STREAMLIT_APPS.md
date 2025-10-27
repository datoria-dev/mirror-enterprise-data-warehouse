# Quick Guide: Editar Streamlit Apps en Snowflake

**Pregunta frecuente**: "¿Cómo edito mis apps si no las veo en Snowflake UI?"

---

## 🎯 Respuesta Rápida

Tus apps usan **Stage-based mode** (archivos en `@STAGE`), no **Native mode** (archivos en Snowflake).

**Solución**: Edita local → Sube al Stage → App se actualiza automáticamente

---

## 📝 Método 1: Edición Local + Upload (Recomendado)

### Para una app específica (ej: Sophos):

```bash
# 1. Editar archivo local
code "13_STREAMLIT_COMPLETE/Sophos/streamlit_app.py"

# 2. Subir a Snowflake Stage
snowsql -a GenericCorp-CRH_EDW -u fuad.onate@CompanyX.com \
  --authenticator externalbrowser \
  -q "PUT file://13_STREAMLIT_COMPLETE/Sophos/streamlit_app.py @STREAMLIT_APPS_STAGE/Sophos/ OVERWRITE=TRUE"

# 3. Refrescar app en browser (Ctrl+F5)
```

**Tiempo**: 1-2 minutos por cambio

---

## 📝 Método 2: Crear Versión DEV Editable

### Para testing rápido en UI:

```sql
-- 1. Crear app Native (editable en UI)
CREATE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_SOPHOS_DEV
COMMENT = 'CPR - Sophos (DEV - Editable)';

-- 2. En Snowflake UI:
--    - Abre STREAMLIT_SOPHOS_DEV
--    - Copia contenido de tu streamlit_app.py local
--    - Pega en editor
--    - Save & Run

-- 3. Ahora puedes editar directamente en UI ✅
```

**Ventaja**: Edición rápida en browser
**Desventaja**: Debes copiar cambios de vuelta a código local

---

## 📝 Método 3: Ver Archivos del Stage

### Ver qué archivos hay:

```sql
-- Listar archivos en Stage
LIST @STREAMLIT_APPS_STAGE/Sophos/;

-- Resultado ejemplo:
-- STREAMLIT_APPS_STAGE/Sophos/streamlit_app.py  42827 bytes
-- STREAMLIT_APPS_STAGE/Sophos/environment.yml   150 bytes
```

### Descargar para ver:

```sql
-- En SnowSQL
GET @STREAMLIT_APPS_STAGE/Sophos/streamlit_app.py file://C:/temp/;

-- Ahora puedes ver el archivo en C:/temp/
```

---

## 🔄 Workflow Recomendado

### Para Cambios Pequeños (1-2 líneas):

```
1. Editar en VSCode local
2. PUT al Stage con SnowSQL
3. Ctrl+F5 en browser para ver cambio
```

**Tiempo total**: ~2 minutos

---

### Para Cambios Grandes o Experimentales:

```
1. Crear app DEV en Native mode
2. Editar directamente en Snowflake UI
3. Cuando funcione, copiar código a archivos locales
4. PUT al Stage para actualizar app de producción
```

**Ventaja**: Iteración rápida sin subir/bajar archivos

---

## ⚡ Script PowerShell para Upload Rápido

Crea este archivo: `quick-update-app.ps1`

```powershell
param([string]$AppName)

$file = "13_STREAMLIT_COMPLETE\$AppName\streamlit_app.py"
$stage = "@STREAMLIT_APPS_STAGE/$AppName/"

Write-Host "Uploading $AppName..." -ForegroundColor Cyan

snowsql -a GenericCorp-CRH_EDW `
  -u fuad.onate@CompanyX.com `
  --authenticator externalbrowser `
  -q "PUT file://$file $stage OVERWRITE=TRUE"

Write-Host "Done! Refresh app in browser (Ctrl+F5)" -ForegroundColor Green
```

**Uso**:
```powershell
.\quick-update-app.ps1 -AppName Sophos
```

---

## 📋 Comparación de Métodos

| Método | Velocidad | Facilidad | Mejor Para |
|--------|-----------|-----------|------------|
| **Local + PUT** | ⭐⭐⭐ | ⭐⭐ | Cambios pequeños, producción |
| **Native DEV** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Experimentación, testing |
| **GET + Edit + PUT** | ⭐ | ⭐ | Revisar archivos actuales |

---

## 🎯 Recomendación

**Para tu proyecto**:

1. **Producción**: Mantén Stage-based apps (las actuales)
2. **Desarrollo**: Crea 1-2 apps Native para testing rápido
   - `STREAMLIT_SOPHOS_DEV`
   - `STREAMLIT_ZEROFOX_DEV`
3. **Workflow**: Edita en DEV → Copia a local → Deploy a PROD

---

**Documento completo**: [SNOWFLAKE_STREAMLIT_CREATION_METHODS.md](SNOWFLAKE_STREAMLIT_CREATION_METHODS.md)
