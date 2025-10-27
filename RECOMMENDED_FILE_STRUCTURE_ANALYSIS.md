# Recommended File Structure for Streamlit Apps in Snowflake
## Analysis & Recommendations for SECURITY_ANALYTICS Project

**Date**: 2025-10-27
**Context**: 18 Streamlit apps deployed in DEV_REPORTING.SECURITY_ANALYTICS
**Current Structure**: streamlit_app.py + environment.yml only

---

## 📊 Current State Analysis

### Current File Structure (All 18 Apps)
```
AppName/
├── streamlit_app.py   (~1,000-1,200 lines)
├── environment.yml    (Conda dependencies)
└── __pycache__/       (Auto-generated, not tracked)
```

### App Complexity Metrics
| App | Lines of Code | Complexity | Has Metadata Tab |
|-----|---------------|------------|------------------|
| Zerofox | 1,022 | Medium | No |
| Trellix | 1,136 | High | No |
| Sophos | 1,167 | High | No |
| Leviat | ~1,100 | High | Yes (146 cols) |
| CybelAngel | ~900 | Medium | Yes (112 cols) |
| **Average** | **~1,050** | **Medium-High** | **6 of 18** |

---

## 📁 Recommended Additional Files

### 1. ✅ **ALTAMENTE RECOMENDADO**: `utils.py` o `helpers.py`

**Propósito**: Extraer funciones reutilizables y código repetitivo

**Por qué lo necesitamos**:
- ✅ **Código duplicado**: Las 18 apps tienen ~150 líneas idénticas de dummy classes (_DummyPlotly, _DummyNumpy, etc.)
- ✅ **Mantenibilidad**: Cambios en dummy classes requieren actualizar 18 archivos
- ✅ **Testing**: Difícil testear funciones embebidas en archivos de 1,000+ líneas
- ✅ **Legibilidad**: Archivos de 1,100 líneas son difíciles de mantener

**Beneficio para nuestro proyecto**: ⭐⭐⭐⭐⭐ **CRÍTICO**

**Implementación**:
```python
# utils.py
"""
Shared utilities for SECURITY_ANALYTICS Streamlit apps
"""

class _DummyColors:
    '''Dummy color palettes for Snowflake Streamlit'''
    # ... (150 líneas de código reutilizable)

class _DummyPlotly:
    # ... (código común)

class _DummyNumpy:
    # ... (código común)

def export_csv(df, filename="export"):
    """Add CSV export button for a dataframe"""
    # ... (función común en varias apps)

def safe_query(sql, session, error_message="Failed to load data"):
    """Execute Snowflake query with error handling"""
    # ... (patrón repetido en todas las apps)
```

**Uso en streamlit_app.py**:
```python
# streamlit_app.py
import streamlit as st
from utils import _DummyPlotly, _DummyNumpy, export_csv, safe_query

px = _DummyPlotly()
np = _DummyNumpy()

# Resto del código específico de la app...
```

**Impacto**:
- ❌ **Sin utils.py**: 18 apps × 150 líneas = 2,700 líneas duplicadas
- ✅ **Con utils.py**: 1 archivo × 150 líneas = 150 líneas + imports
- 💾 **Ahorro**: ~95% de código duplicado eliminado

---

### 2. ✅ **RECOMENDADO**: `database.py` o `snowflake_utils.py`

**Propósito**: Centralizar interacción con Snowflake

**Por qué lo necesitamos**:
- ✅ **Patrón repetido**: Todas las apps usan `get_active_session()` de la misma manera
- ✅ **Error handling**: Lógica de manejo de errores SQL está duplicada
- ✅ **Context setting**: Varias apps setean database context (línea 139 de Crowdstrike)
- ✅ **Caching**: Configuración de @st.cache_data se repite

**Beneficio para nuestro proyecto**: ⭐⭐⭐⭐ **MUY ÚTIL**

**Implementación**:
```python
# database.py
"""
Snowflake database utilities for SECURITY_ANALYTICS Streamlit apps
"""
import streamlit as st
from snowflake.snowpark.context import get_active_session

# Constants
CACHE_TTL_SECONDS = 300  # 5 minutes
DEFAULT_ROW_LIMIT = 10000

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def safe_query(sql: str, error_message: str = "Failed to load data", max_rows: int = DEFAULT_ROW_LIMIT):
    """Execute Snowflake query with error handling and caching"""
    try:
        session = get_active_session()

        # Set database context
        try:
            session.sql("USE DATABASE DEV_REPORTING").collect()
            session.sql("USE SCHEMA SECURITY_ANALYTICS").collect()
        except Exception as e:
            st.warning(f"Could not set database context: {e}")

        # Add LIMIT if not present
        if 'LIMIT' not in sql.upper():
            sql = f"{sql.rstrip(';')} LIMIT {max_rows}"

        result = session.sql(sql).to_pandas()

        if result.empty:
            st.warning(f"⚠️ No data found")
            return pd.DataFrame()

        return result

    except Exception as e:
        st.error(f"❌ {error_message}")
        with st.expander("🔍 Technical Details"):
            st.code(f"Error: {str(e)}\n\nQuery:\n{sql}")
        return pd.DataFrame()

def get_session():
    """Get active Snowflake session with context set"""
    session = get_active_session()
    try:
        session.sql("USE DATABASE DEV_REPORTING").collect()
        session.sql("USE SCHEMA SECURITY_ANALYTICS").collect()
    except:
        pass
    return session
```

**Impacto**:
- Elimina ~50 líneas de código duplicado por app
- 18 apps × 50 líneas = 900 líneas duplicadas → 1 archivo de 100 líneas

---

### 3. ⚠️ **OPCIONAL**: `config.py` o `.streamlit/secrets.toml`

**Propósito**: Configuración y constantes centralizadas

**Por qué podríamos necesitarlo**:
- ⚠️ **Configuración**: Cache TTL, row limits, colores, etc.
- ⚠️ **Secrets**: Actualmente NO lo necesitamos (usamos `get_active_session()` nativo)
- ⚠️ **Constantes**: Alert thresholds, KPI targets

**Beneficio para nuestro proyecto**: ⭐⭐ **BAJA PRIORIDAD**

**Razón**: En Streamlit dentro de Snowflake:
- ❌ No necesitamos credenciales (autenticación automática)
- ❌ No necesitamos `st.secrets` (tenemos session nativa)
- ⚠️ Las constantes ya están en cada app (no muchas)

**Implementación (si decidimos usarlo)**:
```python
# config.py
"""
Configuration constants for SECURITY_ANALYTICS Streamlit apps
"""

# Cache settings
CACHE_TTL_SECONDS = 300  # 5 minutes
DEFAULT_ROW_LIMIT = 10000

# Database
DATABASE = "DEV_REPORTING"
SCHEMA = "SECURITY_ANALYTICS"
WAREHOUSE = "DEV_WH"

# Alert thresholds
ALERT_CRITICAL = 90
ALERT_WARNING = 75
ALERT_INFO = 50

# Color schemes (CPR branding)
CPR_PRIMARY_COLOR = "#e94560"
CPR_SECONDARY_COLOR = "#0f3460"
CPR_ACCENT_COLOR = "#1a1a2e"
```

**Recomendación**: ⚠️ **SKIP por ahora** - Solo agregar si encontramos muchas constantes duplicadas

---

### 4. ❌ **NO RECOMENDADO**: `.gitignore`

**Propósito**: Ignorar archivos en Git

**Por qué NO lo necesitamos (por ahora)**:
- ❌ No tenemos archivos sensibles (no hay secrets.toml)
- ❌ No tenemos datos locales (todo en Snowflake)
- ⚠️ `__pycache__` se puede ignorar pero es menor

**Beneficio para nuestro proyecto**: ⭐ **MUY BAJA PRIORIDAD**

**Recomendación**: ⚠️ **AGREGAR DESPUÉS** cuando tengamos:
- Archivos de desarrollo local
- Secrets o configuraciones locales
- Datos de prueba

**Implementación (futura)**:
```gitignore
# .gitignore
__pycache__/
*.pyc
.streamlit/secrets.toml
*.log
.env
.venv/
```

---

### 5. ❌ **NO RECOMENDADO**: `assets/` o `images/`

**Propósito**: Recursos estáticos (imágenes, logos, CSS)

**Por qué NO lo necesitamos**:
- ❌ Nuestras apps no usan imágenes locales
- ❌ CSS está embebido en streamlit_app.py (funciona bien)
- ❌ No hay logos o iconos externos

**Beneficio para nuestro proyecto**: ⭐ **NO APLICA**

**Recomendación**: ⚠️ **SKIP** - Solo agregar si queremos logos CPR o recursos visuales

---

### 6. ❌ **NO RECOMENDADO**: `pages/` (Multi-page apps)

**Propósito**: Apps de múltiples páginas

**Por qué NO lo necesitamos**:
- ❌ Nuestras apps son single-page con tabs
- ❌ Tabs funcionan bien para nuestra estructura
- ❌ Multi-page complicaría navegación

**Beneficio para nuestro proyecto**: ⭐ **NO APLICA**

**Recomendación**: ❌ **NO IMPLEMENTAR** - Estructura actual con tabs es superior

---

## 🎯 Recomendaciones Finales para Nuestro Proyecto

### Estructura Recomendada (Fase 1 - INMEDIATA)

```
AppName/
├── streamlit_app.py      # App principal (~600-700 líneas después de refactor)
├── utils.py              # NEW: Dummy classes y funciones comunes (~200 líneas)
├── database.py           # NEW: Interacción con Snowflake (~100 líneas)
└── environment.yml       # Dependencias (sin cambios)
```

**Beneficios**:
- ✅ Elimina ~2,700 líneas de código duplicado (utils.py)
- ✅ Elimina ~900 líneas de código duplicado (database.py)
- ✅ Archivos más pequeños (~600 líneas vs 1,100)
- ✅ Más fácil de mantener y testear
- ✅ Cambios en dummy classes se hacen 1 vez, no 18 veces

**Esfuerzo**: ~4-6 horas para refactorizar las 18 apps

---

### Estructura Futura (Fase 2 - OPCIONAL)

```
AppName/
├── streamlit_app.py      # App principal (~500 líneas)
├── utils.py              # Funciones comunes
├── database.py           # Snowflake utilities
├── config.py             # NEW: Constantes centralizadas (~50 líneas)
├── .gitignore            # NEW: Si usamos Git
└── environment.yml       # Dependencias
```

**Agregar solo si**:
- Encontramos muchas constantes duplicadas
- Queremos mover a repositorio Git
- Necesitamos configuración más compleja

---

## 📋 Plan de Implementación

### Paso 1: Crear `utils.py` Compartido ⭐⭐⭐⭐⭐

1. Extraer dummy classes comunes (_DummyPlotly, _DummyNumpy, etc.)
2. Extraer función `export_csv()` (común en varias apps)
3. Poner en ubicación compartida o copiar a cada app

**Opciones de implementación**:

**Opción A - Un utils.py por app** (Más fácil, recomendado inicialmente):
```
Zerofox/
├── streamlit_app.py
├── utils.py          # Copia del utils.py común
├── environment.yml

Trellix/
├── streamlit_app.py
├── utils.py          # Copia del utils.py común
├── environment.yml
```
- ✅ Fácil de desplegar (no requiere cambios en Snowflake)
- ✅ Cada app es independiente
- ⚠️ Duplicación entre apps (pero menos que ahora)

**Opción B - Un utils.py compartido** (Más avanzado):
```
shared/
└── utils.py          # Compartido por todas las apps

Zerofox/
├── streamlit_app.py  # from shared.utils import ...
├── environment.yml
```
- ✅ Zero duplicación
- ❌ Requiere configurar Python path en Snowflake
- ❌ Más complejo de mantener

**Recomendación**: ⭐ **Opción A** - Un utils.py por app (es lo que hacen la mayoría de proyectos)

---

### Paso 2: Crear `database.py` ⭐⭐⭐⭐

1. Extraer función `safe_query()` común
2. Extraer lógica de database context
3. Copiar a cada app

**Beneficio**: Cada app queda ~200-250 líneas más pequeña

---

### Paso 3: Refactorizar Apps Gradualmente ⭐⭐⭐

**Prioridad de refactorización**:

1. **Fase 1 - Apps complejas** (3 apps):
   - Sophos (1,167 líneas) → ~600 líneas
   - Trellix (1,136 líneas) → ~650 líneas
   - Leviat (~1,100 líneas) → ~600 líneas

2. **Fase 2 - Apps con más descargas** (4 apps):
   - Crowdstrike (7 download buttons)
   - Leviat (7 download buttons)
   - Symantec (3 download buttons)
   - ServiceNow (4 download buttons)

3. **Fase 3 - Resto de apps** (11 apps):
   - Resto en orden alfabético

**Estimado**: ~20 min por app × 18 apps = ~6 horas total

---

## 🎬 Ejemplo: Antes vs Después

### ANTES (Zerofox - 1,022 líneas)

```python
# streamlit_app.py (TODO EN UN ARCHIVO)

import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

# 150 líneas de dummy classes
class _DummyPlotly:
    # ... 50 líneas
class _DummyNumpy:
    # ... 50 líneas
# etc.

# 50 líneas de funciones comunes
@st.cache_data(ttl=300)
def safe_query(sql, error_message="Failed"):
    # ... 30 líneas

def export_csv(df, filename):
    # ... 20 líneas

# 800 líneas de código específico de la app
st.set_page_config(...)
st.markdown("""<style>...</style>""")
# ... resto del código
```

---

### DESPUÉS (Zerofox - ~600 líneas)

```python
# utils.py (~200 líneas) - NUEVO
"""Shared utilities for SECURITY_ANALYTICS Streamlit apps"""

class _DummyPlotly:
    # ... 50 líneas

class _DummyNumpy:
    # ... 50 líneas

def export_csv(df, filename="export"):
    # ... 20 líneas

# ... más funciones comunes
```

```python
# database.py (~100 líneas) - NUEVO
"""Snowflake utilities for SECURITY_ANALYTICS apps"""

import streamlit as st
from snowflake.snowpark.context import get_active_session

@st.cache_data(ttl=300)
def safe_query(sql, error_message="Failed", max_rows=10000):
    # ... 50 líneas

def get_session():
    # ... 20 líneas
```

```python
# streamlit_app.py (~600 líneas) - REFACTORIZADO
import streamlit as st
import pandas as pd
from utils import _DummyPlotly, _DummyNumpy, export_csv
from database import safe_query, get_session

# Crear objetos dummy
px = _DummyPlotly()
np = _DummyNumpy()

# 600 líneas de código específico de ZeroFox
st.set_page_config(
    page_title="CPR - ZeroFox Digital Risk Protection",
    page_icon="🔐",
    layout="wide"
)

st.markdown("""<style>...</style>""")

# Load data
df = safe_query("SELECT * FROM ZEROFOX_DATA")

# Display dashboard
# ... código específico de ZeroFox
```

**Mejoras**:
- ✅ streamlit_app.py: 1,022 → 600 líneas (41% reducción)
- ✅ Código reutilizable en utils.py y database.py
- ✅ Más fácil de leer y mantener
- ✅ Cambios en dummy classes: 1 archivo vs 18 archivos

---

## 💡 Otras Consideraciones

### Testing (Futuro)
Si queremos agregar tests unitarios:
```
AppName/
├── streamlit_app.py
├── utils.py
├── database.py
├── environment.yml
└── tests/
    ├── test_utils.py
    └── test_database.py
```

Beneficio: ⭐⭐⭐ **ÚTIL** pero no crítico ahora

---

### Documentation (Futuro)
```
AppName/
├── streamlit_app.py
├── utils.py
├── database.py
├── environment.yml
└── README.md          # Descripción de la app, cómo usarla
```

Beneficio: ⭐⭐ **ÚTIL** para onboarding de nuevos desarrolladores

---

## 🎯 Decisión Final: ¿Qué hacer?

### ✅ IMPLEMENTAR AHORA (Alta prioridad):

1. **utils.py** en cada app
   - Extraer dummy classes
   - Extraer export_csv()
   - **Impacto**: Ahorra ~150 líneas por app × 18 = 2,700 líneas

2. **database.py** en cada app
   - Extraer safe_query()
   - Extraer get_session()
   - **Impacto**: Ahorra ~50 líneas por app × 18 = 900 líneas

**Total ahorro**: ~3,600 líneas de código duplicado eliminadas

---

### ⚠️ CONSIDERAR DESPUÉS (Media prioridad):

3. **config.py** - Solo si vemos muchas constantes duplicadas
4. **.gitignore** - Cuando movamos a Git repository
5. **README.md** - Para documentación de cada app

---

### ❌ NO IMPLEMENTAR (Baja/ninguna prioridad):

6. **assets/** - No usamos imágenes
7. **pages/** - Tabs son mejor para nuestro caso
8. **.streamlit/secrets.toml** - No necesitamos (auth automática en Snowflake)

---

## 📊 Resumen Ejecutivo

| Archivo | Prioridad | Beneficio | Esfuerzo | Recomendación |
|---------|-----------|-----------|----------|---------------|
| **utils.py** | ⭐⭐⭐⭐⭐ | MUY ALTO | 4 hrs | **IMPLEMENTAR YA** |
| **database.py** | ⭐⭐⭐⭐ | ALTO | 2 hrs | **IMPLEMENTAR YA** |
| **config.py** | ⭐⭐ | MEDIO | 1 hr | Después |
| **.gitignore** | ⭐⭐ | BAJO | 10 min | Cuando usemos Git |
| **README.md** | ⭐⭐ | BAJO | 30 min/app | Opcional |
| **assets/** | ⭐ | NINGUNO | N/A | No necesario |
| **pages/** | ⭐ | NINGUNO | N/A | No necesario |
| **secrets.toml** | ⭐ | NINGUNO | N/A | No necesario |

---

## 🚀 Próximo Paso Recomendado

**Crear archivos base**:
1. `utils.py` - Template con dummy classes
2. `database.py` - Template con safe_query()
3. Refactorizar 1 app como prueba (Zerofox)
4. Si funciona bien, aplicar a las demás 17 apps

**¿Quieres que cree estos archivos base ahora?** 😊
