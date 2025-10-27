# Snowflake Streamlit: Métodos de Creación de Apps
## Stage-based vs Native Editor

**Pregunta**: ¿Por qué no puedo ver/editar archivos en apps creadas desde Stage, pero sí en apps manuales?

---

## 🎯 Respuesta Rápida

**Razón**: Snowflake tiene **2 modos diferentes** de crear Streamlit apps:

1. **Native/In-Snowflake Mode** (Editable en UI)
   - Creas la app directamente en Snowflake UI
   - Archivos se almacenan internamente en Snowflake
   - ✅ Puedes editar archivos en el browser
   - ✅ Puedes agregar/eliminar archivos
   - ✅ Git integration disponible

2. **Stage-based Mode** (Desde archivos externos)
   - Creas la app apuntando a un Stage
   - Archivos están en `@STAGE/folder/`
   - ❌ No puedes editar en UI (archivos están en Stage)
   - ❌ No puedes ver estructura de archivos
   - ✅ Despliegue automatizado

**Tus apps actuales**: Modo #2 (Stage-based) - Por eso no puedes editarlas en UI

---

## 📊 Comparación Detallada

### Modo 1: Native/In-Snowflake (Creado en UI)

#### Creación:
```sql
-- En Snowflake UI: Streamlit > + Streamlit App
-- O con SQL:
CREATE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.MY_APP;
-- NO especificas ROOT_LOCATION ni MAIN_FILE
```

#### Características:
```
MY_APP (Native)
├── 📝 Editable en UI
├── 📁 Archivos visibles
├── ➕ Puede agregar archivos
├── 🔄 Git integration
└── 💾 Almacenado internamente en Snowflake
```

#### Ventajas:
- ✅ Edición rápida en browser
- ✅ Ver todos los archivos (streamlit_app.py, utils.py, database.py, etc.)
- ✅ Agregar/eliminar archivos fácilmente
- ✅ Git integration nativa
- ✅ Ideal para desarrollo iterativo

#### Desventajas:
- ❌ Difícil deployment automatizado
- ❌ No hay "source of truth" en filesystem local
- ❌ CI/CD más complicado
- ❌ Backup manual necesario

---

### Modo 2: Stage-based (Desde Stage)

#### Creación:
```sql
-- Con SQL (lo que usamos):
CREATE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.MY_APP
ROOT_LOCATION = '@STREAMLIT_APPS_STAGE/MyApp/'
MAIN_FILE = 'streamlit_app.py'
QUERY_WAREHOUSE = DEV_WH;
```

#### Características:
```
MY_APP (Stage-based)
├── 📂 Apunta a @STAGE/MyApp/
├── 🚫 NO editable en UI
├── 🚫 Archivos NO visibles en UI
├── 📦 Archivos en Stage
└── 🔄 Actualizar = PUT nuevo archivo al Stage
```

#### Ventajas:
- ✅ Deployment automatizado (SnowSQL, Python, PowerShell)
- ✅ Source of truth en filesystem local
- ✅ CI/CD fácil (Git → Stage → App)
- ✅ Backup automático (archivos en Git)
- ✅ Multiple ambientes (DEV/PROD con mismo código)

#### Desventajas:
- ❌ No puedes editar en Snowflake UI
- ❌ No ves estructura de archivos en UI
- ❌ Cada cambio requiere PUT al Stage
- ❌ Menos ágil para cambios rápidos

---

## 🤔 ¿Por Qué No Puedes Ver los Archivos?

Cuando usas `CREATE STREAMLIT` con `ROOT_LOCATION`, estás diciendo:

```
"Snowflake, ejecuta esta app usando archivos que están en el Stage,
 no almacenes copias internas de los archivos"
```

**Resultado**:
- Snowflake lee los archivos desde `@STAGE/folder/` cada vez que cargas la app
- NO copia los archivos a un almacenamiento interno editable
- NO muestra los archivos en la UI porque no "posee" los archivos
- Los archivos "viven" en el Stage, no en el objeto STREAMLIT

**Analogía**:
- **Native App** = Libro guardado en tu biblioteca (puedes abrir y editar)
- **Stage-based App** = Libro prestado de otra biblioteca (solo puedes leer, no editar)

---

## 🔄 Cómo Funciona Cada Modo

### Native Mode: Almacenamiento Interno

```
User → Snowflake UI → Create Streamlit
                   ↓
    ┌──────────────────────────────┐
    │   STREAMLIT Object           │
    │  ┌────────────────────────┐  │
    │  │ streamlit_app.py       │  │ ← Archivos almacenados
    │  │ utils.py               │  │   DENTRO del objeto
    │  │ database.py            │  │
    │  └────────────────────────┘  │
    └──────────────────────────────┘
              ↓
    User puede editar en UI ✅
```

---

### Stage-based Mode: Referencia Externa

```
User → SnowSQL PUT → @STAGE/MyApp/
                          │
                          ├── streamlit_app.py
                          ├── utils.py
                          └── database.py
                          ↓
    ┌──────────────────────────────┐
    │   STREAMLIT Object           │
    │  ┌────────────────────────┐  │
    │  │ ROOT_LOCATION =        │  │ ← Solo guarda
    │  │ '@STAGE/MyApp/'        │  │   REFERENCIA
    │  │ MAIN_FILE =            │  │   no archivos
    │  │ 'streamlit_app.py'     │  │
    │  └────────────────────────┘  │
    └──────────────────────────────┘
              ↓
    Snowflake lee desde Stage cada vez
    User NO puede editar en UI ❌
```

---

## 🛠️ Cómo Ver/Editar Archivos en Stage-based Apps

### Opción 1: Listar Archivos en el Stage

```sql
-- Ver archivos en el stage
LIST @STREAMLIT_APPS_STAGE/Sophos/;

-- Resultado:
-- name                                          size    md5
-- STREAMLIT_APPS_STAGE/Sophos/streamlit_app.py 42827   abc123...
-- STREAMLIT_APPS_STAGE/Sophos/environment.yml  150     def456...
```

### Opción 2: Descargar Archivo del Stage para Editar

```sql
-- Descargar archivo del stage (en SnowSQL)
GET @STREAMLIT_APPS_STAGE/Sophos/streamlit_app.py file://C:/temp/;

-- Editar localmente
-- Luego subir de nuevo:
PUT file://C:/temp/streamlit_app.py @STREAMLIT_APPS_STAGE/Sophos/ OVERWRITE=TRUE;
```

### Opción 3: Editar Local y Re-subir (Recomendado)

```bash
# 1. Editar archivo local
notepad "13_STREAMLIT_COMPLETE/Sophos/streamlit_app.py"

# 2. Subir a Stage
snowsql -q "PUT file://13_STREAMLIT_COMPLETE/Sophos/streamlit_app.py @STREAMLIT_APPS_STAGE/Sophos/ OVERWRITE=TRUE"

# 3. App se actualiza automáticamente (usa nuevo archivo del Stage)
```

---

## 🔄 ¿Cómo Migrar a Native Mode? (Si lo deseas)

### Paso 1: Crear App en Native Mode

```sql
-- Opción A: En Snowflake UI
-- Ir a: Streamlit > + Streamlit App > Create from scratch
-- Nombre: STREAMLIT_SOPHOS_NATIVE

-- Opción B: Con SQL
CREATE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_SOPHOS_NATIVE
COMMENT = 'CPR - Sophos Security Dashboard (Native Mode)';
```

### Paso 2: Copiar Contenido de Archivos

**Manualmente en UI**:
1. Abre la nueva app en Snowflake UI
2. Copia el contenido de tu archivo local streamlit_app.py
3. Pega en el editor
4. Si necesitas utils.py:
   - Click "+ Add file"
   - Nombra "utils.py"
   - Pega contenido

**Resultado**: Ahora puedes editar en UI ✅

---

### Paso 3: Decidir Cuál Mantener

**Mantener Stage-based** si:
- ✅ Quieres CI/CD automatizado
- ✅ Usas Git como source of truth
- ✅ Deployment scriptado es prioridad
- ✅ Múltiples ambientes (DEV/PROD)

**Migrar a Native** si:
- ✅ Edición rápida en UI es importante
- ✅ Quieres ver archivos en browser
- ✅ Desarrollo iterativo/experimental
- ✅ No necesitas deployment automatizado

---

## 💡 Recomendación para Tu Proyecto

### Enfoque Híbrido (Mejor de Ambos Mundos)

**Para Desarrollo/Testing**:
- Crea versiones Native de 1-2 apps clave (ej: Sophos, ZeroFox)
- Usa para testing rápido y experimentos
- Nombres: `STREAMLIT_SOPHOS_DEV`, `STREAMLIT_ZEROFOX_DEV`

**Para Producción**:
- Mantén Stage-based apps (las actuales)
- Deployment automatizado desde Git
- Source of truth en filesystem local
- Nombres: `STREAMLIT_SOPHOS`, `STREAMLIT_ZEROFOX`

**Flujo de Trabajo**:
```
1. Editar código local (VSCode)
   ↓
2. Testear en Native app (editar en UI si necesario)
   ↓
3. Copiar cambios de vuelta a código local
   ↓
4. Commit a Git
   ↓
5. Deploy a Stage-based app (production)
```

---

## 📋 Tabla Comparativa: ¿Cuál Usar?

| Aspecto | Native (UI) | Stage-based | Ganador |
|---------|-------------|-------------|---------|
| **Edición rápida** | ✅ En browser | ❌ Requiere PUT | Native |
| **Ver archivos** | ✅ Todos visibles | ❌ No visible | Native |
| **Agregar archivos** | ✅ Fácil | ⚠️ Requiere PUT | Native |
| **CI/CD** | ❌ Difícil | ✅ Fácil | Stage |
| **Git integration** | ✅ Built-in | ✅ Manual | Empate |
| **Source of truth** | ⚠️ Snowflake | ✅ Filesystem | Stage |
| **Backup** | ⚠️ Manual | ✅ Git auto | Stage |
| **Multi-ambiente** | ❌ Difícil | ✅ Fácil | Stage |
| **Learning curve** | ✅ Fácil | ⚠️ Requiere SnowSQL | Native |

---

## 🚀 Acción Recomendada

### Para Ti (SECURITY_ANALYTICS Project):

**Opción 1: Mantener Stage-based** (Recomendado para producción)
- ✅ Ya lo tienes configurado
- ✅ Scripts de deployment listos
- ✅ Git como source of truth
- ✅ Fácil rollback si hay problemas

**Ventaja adicional**: Cuando implementes utils.py y database.py, solo subes 3 archivos al Stage y todas las apps los usan.

**Edición**:
```bash
# 1. Editar local
code 13_STREAMLIT_COMPLETE/Sophos/streamlit_app.py

# 2. Subir
snowsql -q "PUT file://13_STREAMLIT_COMPLETE/Sophos/streamlit_app.py @STREAMLIT_APPS_STAGE/Sophos/ OVERWRITE=TRUE"

# 3. Refresh app en browser (Ctrl+F5)
```

---

**Opción 2: Crear versiones DEV en Native mode** (Para testing rápido)
- ✅ Crea `STREAMLIT_SOPHOS_DEV` en Native mode
- ✅ Usa para testing/experimentos
- ✅ Cuando estés satisfecho, copia a archivos locales
- ✅ Deploy a Stage-based production

---

## 📝 Cómo Crear App Native con Múltiples Archivos

### Paso a Paso:

1. **En Snowflake UI**: Streamlit > + Streamlit App

2. **Main File**: Edita streamlit_app.py con contenido base

3. **Agregar utils.py**:
   ```
   Click: "+ Add file" (esquina superior derecha)
   Filename: utils.py
   Pega contenido del template
   Save
   ```

4. **Agregar database.py**:
   ```
   Click: "+ Add file"
   Filename: database.py
   Pega contenido del template
   Save
   ```

5. **Actualizar imports** en streamlit_app.py:
   ```python
   from utils import px, go, np, export_csv
   from database import safe_query, get_session
   ```

6. **Run**: La app ahora usa los 3 archivos

---

## 🎯 Resumen

**Tu pregunta**: ¿Por qué no veo archivos en apps creadas desde Stage?

**Respuesta**: Porque usas **Stage-based mode** donde:
- Archivos están en `@STAGE/folder/`
- Snowflake solo tiene una REFERENCIA
- NO copia archivos internamente
- Por eso NO puedes editar en UI

**Solución si quieres editar en UI**:
1. Crea una versión Native de la app
2. O sigue editando local + PUT al Stage

**Recomendación**: Mantén Stage-based para producción (mejor para CI/CD y deployment automatizado)

---

**¿Quieres que te muestre cómo crear una app Native con múltiples archivos?**
O **¿prefieres quedarte con Stage-based y optimizar el workflow de edición?** 😊
