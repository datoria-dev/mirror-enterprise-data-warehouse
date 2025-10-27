# SnowSQL No Detectado - Soluciones Alternativas

## 🔍 Problema

SnowSQL se instaló pero no se puede encontrar en el PATH del sistema.

---

## ✅ Solución 1: Usar Snowflake Web UI (RECOMENDADO)

**No necesitas SnowSQL** para desplegar apps de Streamlit!

### Pasos Rápidos:

1. **Abre Snowflake Web UI**: https://app.snowflake.com
2. **Login con Okta**: FUAD.ONATE@CompanyX.COM
3. **Ve a "Streamlit"** en el menú lateral
4. **Click "+ Streamlit App"**
5. **Copia el código** de `13_STREAMLIT_COMPLETE/Symantec/streamlit_app.py`
6. **Pega en el editor** de Snowflake
7. **Configura**:
   - Name: `STREAMLIT_SYMANTEC`
   - Database: `ITSECKPI_DB`
   - Schema: `ITSECKPI_SCHEMA`
   - Warehouse: `COMPUTE_WH`
8. **Click "Run"**

**Ventajas**:
- ✅ No requiere SnowSQL
- ✅ Más rápido
- ✅ Editor con syntax highlighting
- ✅ Deploy inmediato

---

## ✅ Solución 2: Buscar SnowSQL Manualmente

SnowSQL podría estar instalado en alguna de estas ubicaciones:

```
C:\Users\fonat\.snowsql\
C:\Program Files\Snowflake SnowSQL\
C:\Program Files (x86)\Snowflake SnowSQL\
C:\Users\fonat\AppData\Local\Programs\Snowflake\
```

### Para buscar manualmente:

1. Abre File Explorer
2. Ve a "Este equipo" / "This PC"
3. Busca: `snowsql.exe`
4. Anota la ruta completa

### Si lo encuentras:

**Agregar al PATH manualmente**:

1. Windows Search → "Environment Variables"
2. Click "Environment Variables"
3. En "User variables", selecciona "Path"
4. Click "Edit"
5. Click "New"
6. Agrega la ruta donde está `snowsql.exe`
7. Click "OK" en todas las ventanas
8. **Cierra y abre de nuevo PowerShell**

---

## ✅ Solución 3: Reinstalar SnowSQL con Configuración Manual

### Paso 1: Desinstalar SnowSQL actual

1. Windows Search → "Add or Remove Programs"
2. Busca "SnowSQL"
3. Click "Uninstall"

### Paso 2: Reinstalar desde el MSI

```powershell
# Ejecutar con permisos de admin
Start-Process msiexec.exe -Wait -ArgumentList '/i "C:\Users\fonat\Downloads\snowsql-windows.msi" /passive'
```

### Paso 3: Verificar instalación

```powershell
# Cerrar y abrir de nuevo PowerShell, luego:
snowsql --version
```

---

## ✅ Solución 4: Usar Snowflake Connector desde Python

Si realmente necesitas ejecutar SQL desde scripts, puedes usar el conector de Python:

### Instalar el conector:

```powershell
pip install snowflake-connector-python
```

### Script de ejemplo:

```python
import snowflake.connector

# Conectar
conn = snowflake.connector.connect(
    user='FUAD.ONATE@CompanyX.COM',
    account='GenericCorp-CRH_LEDW',
    authenticator='externalbrowser',  # Para SSO/Okta
    warehouse='COMPUTE_WH',
    database='ITSECKPI_DB',
    schema='ITSECKPI_SCHEMA'
)

# Ejecutar query
cursor = conn.cursor()
cursor.execute("SELECT CURRENT_VERSION()")
print(cursor.fetchone())

# Cerrar
cursor.close()
conn.close()
```

---

## 🎯 Recomendación

**Para deployment de Streamlit apps**: Usa **Solución 1 (Web UI)**

**Ventajas**:
- No requiere instalación de nada
- Funciona inmediatamente
- Más visual y fácil de usar
- Mismo resultado que con SnowSQL

**SnowSQL es útil para**:
- Scripting automatizado
- Batch operations
- CI/CD pipelines

Pero para desplegar 1-2 apps manualmente, **Web UI es más práctico**.

---

## 📝 Siguiente Paso

**Recomendado**: Ignora el problema de SnowSQL por ahora y despliega Symantec usando Web UI:

1. Abre `DEPLOY_SYMANTEC_WEB_UI.md`
2. Sigue los pasos (5 minutos)
3. Prueba los download buttons
4. Si funciona, continúa con las otras apps

**Después**, si realmente necesitas SnowSQL:
- Intenta Solución 2 (buscar manualmente)
- O Solución 3 (reinstalar)

---

## ✅ ¿Necesitas SnowSQL?

**Para tu caso**: Probablemente NO

**Razones**:
- Solo vas a desplegar ~18 apps
- Web UI es más fácil para deployment manual
- Puedes editar y actualizar apps directamente en Web UI
- No necesitas scripting automatizado (por ahora)

**Cuando SÍ lo necesitarías**:
- CI/CD automation
- Deploying 100+ apps
- Scheduled batch operations
- Integration con otros sistemas

---

**Conclusión**: Procede con Web UI deployment y olvídate de SnowSQL por ahora! 🚀
