# Streamlit in Snowflake (SiS) - Deployment Strategy

## 🎯 Updated Approach for Snowflake Deployment

After reviewing Snowflake's Streamlit architecture, we need to adjust our strategy from "shared library" to "self-contained apps with embedded utilities".

---

## 🏗️ Architecture Understanding

### Snowflake Streamlit (SiS) Environment

```
Snowflake Account
├── STREAMLIT APP: ITSEC_CROWDSTRIKE
│   ├── streamlit_app.py (main)
│   ├── utils.py (optional)
│   └── environment.yml
│
├── STREAMLIT APP: ITSEC_QUALYS
│   ├── streamlit_app.py (main)
│   ├── utils.py (optional)  ← This is SEPARATE from above
│   └── environment.yml
│
└── ... (11 more apps)
```

**Key Constraints:**
- ❌ No shared file system across apps
- ❌ Cannot import from sibling directories
- ❌ Each app is an isolated container
- ✅ Each app CAN have multiple files internally
- ✅ Native Snowflake session via `get_active_session()`

---

## 💡 Recommended Strategy: Self-Contained Apps

### Approach: Embedded Utilities Pattern

Each app includes common utilities **embedded directly** in the main file or as companion files within the same app.

### Two Deployment Options:

#### **Option A: Single-File Apps** (Simplest)
Everything in one `streamlit_app.py`:

```python
# ============================================================================
# STREAMLIT APP: ITSEC_CROWDSTRIKE
# Version: 1.0.0
# Last Updated: 2025-10-08
# ============================================================================

import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

# ----------------------------------------------------------------------------
# EMBEDDED UTILITIES (Version 1.0.0)
# These utilities are copied from our standard template
# ----------------------------------------------------------------------------

@st.cache_data(ttl=300)
def safe_query(sql: str, error_message: str = "Failed to load data"):
    """Execute query with error handling"""
    try:
        session = get_active_session()
        result = session.sql(sql).to_pandas()
        return result if not result.empty else pd.DataFrame()
    except Exception as e:
        st.error(f"❌ {error_message}")
        return pd.DataFrame()

def export_csv(df, filename):
    """Export dataframe to CSV"""
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Export", csv, f"{filename}.csv", "text/csv")

def apply_styles():
    """Apply GenericCorp corporate styles"""
    st.markdown("""<style>
        .main-header { background: linear-gradient(135deg, #0a3d62, #1e5f8e); }
        /* ... more styles ... */
    </style>""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# APP-SPECIFIC CODE STARTS HERE
# ----------------------------------------------------------------------------

st.set_page_config(page_title="CrowdStrike EDR", layout="wide")
apply_styles()

# ... rest of app ...
```

**Pros:**
- ✅ Works perfectly in SiS
- ✅ Single file to upload/edit
- ✅ Self-contained, no dependencies
- ✅ Easy to deploy

**Cons:**
- ⚠️ Code duplication (~200 lines of utilities per app)
- ⚠️ Updates require modifying each app
- ⚠️ Larger file size (~500-800 lines per app)

#### **Option B: Multi-File Apps** (More Organized)
Separate files within each app:

```
ITSEC_CROWDSTRIKE/
├── streamlit_app.py (main - 300 lines)
├── common_utils.py (utilities - 200 lines)
└── environment.yml
```

**streamlit_app.py:**
```python
import streamlit as st
from common_utils import safe_query, export_csv, apply_styles

st.set_page_config(page_title="CrowdStrike EDR", layout="wide")
apply_styles()

# App code here...
df = safe_query("SELECT * FROM ...")
export_csv(df, "data")
```

**common_utils.py:**
```python
import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

@st.cache_data(ttl=300)
def safe_query(sql, error_msg="Error"):
    # ... implementation ...

def export_csv(df, filename):
    # ... implementation ...

def apply_styles():
    # ... implementation ...
```

**Pros:**
- ✅ Clean separation of concerns
- ✅ Main app file is focused (~300 lines)
- ✅ Utilities organized separately
- ✅ Works in SiS

**Cons:**
- ⚠️ Must upload 2 files per app
- ⚠️ Still duplicated across apps
- ⚠️ Slightly more complex deployment

---

## 🚀 Deployment Workflow

### For New Apps (Using Template)

1. **Generate from Template**
   ```bash
   # Use our generator script
   python generate_streamlit_app.py --name "Fortinet" --icon "🛡️"
   ```

2. **Review Generated Code**
   - Single file: `Fortinet/streamlit_app.py` (ready to deploy)
   - OR Multi-file: `streamlit_app.py` + `common_utils.py`

3. **Upload to Snowflake**
   ```sql
   -- Create app in Snowsight
   CREATE STREAMLIT ITSEC_FORTINET
       ROOT_LOCATION = '@streamlit_stage/fortinet'
       MAIN_FILE = 'streamlit_app.py'
       QUERY_WAREHOUSE = 'DEV_REPORTING_WH';
   ```

4. **Test & Deploy**
   - Test in Snowsight editor
   - Grant access to roles
   - Publish

### For Existing Apps (Update Utilities)

1. **Identify Version**
   ```python
   # Check embedded utility version in each app
   # EMBEDDED UTILITIES (Version 1.0.0)
   ```

2. **Update Utilities Section**
   - Copy new utilities from template
   - Paste into existing app
   - Preserve app-specific code

3. **Test & Deploy**

---

## 📦 What We Keep from Our Work

### ✅ Still Valuable:

1. **`common/` as Template Source**
   - Keep as "master copy" of utilities
   - Generate apps from this source
   - Single source of truth for development

2. **Template Generator**
   - Automated app creation
   - Embeds utilities automatically
   - Consistent structure

3. **Documentation**
   - Usage examples
   - Best practices
   - Deployment guides

### 🔄 What Changes:

1. **Deployment Model**
   - FROM: Shared imports (`from common import ...`)
   - TO: Embedded code (copy-paste into each app)

2. **Update Process**
   - FROM: Update once, affects all
   - TO: Update template, regenerate/update apps

3. **File Organization**
   - FROM: `common/` as importable library
   - TO: `common/` as template source for generation

---

## 🛠️ Implementation Plan

### Phase 1: Create Generator (1-2 hours)
```bash
07_STREAMLIT_APPS/
├── common/              # Master templates (keep)
├── templates/           # Keep as-is
├── generator/           # NEW
│   ├── generate_app.py  # Generator script
│   └── config.yaml      # App configurations
```

**Generator Features:**
- Reads from `common/` master files
- Embeds utilities into single file OR multi-file
- Customizes with app name, icon, views
- Produces ready-to-deploy code

### Phase 2: Update Template (30 min)
- Add version tracking
- Add update instructions
- Clear "embedded utilities" section

### Phase 3: Generate All 12 Apps (2-3 hours)
- Run generator for each app
- Customize app-specific queries
- Test locally (if possible)
- Ready for Snowflake upload

### Phase 4: Deploy to Snowflake (1-2 hours)
- Upload via Snowsight
- Configure warehouses
- Grant permissions
- Test in production

---

## 📊 Comparison: Shared vs Embedded

| Aspect | Shared Library | Embedded Utilities |
|--------|----------------|-------------------|
| **Works in SiS?** | ❌ No | ✅ Yes |
| **Code Duplication** | ✅ None | ⚠️ ~200 lines per app |
| **Update Process** | ✅ Update once | ⚠️ Update each app |
| **Deployment** | ❌ Complex | ✅ Simple |
| **Maintenance** | ✅ Easy | ⚠️ Moderate |
| **File Count** | ❌ Many | ✅ 1-2 per app |
| **Snowflake Native** | ❌ No | ✅ Yes |

**Winner for SiS: Embedded Utilities** ✅

---

## 💡 Best Practices for SiS

### 1. Version Your Embedded Code
```python
# ============================================================================
# EMBEDDED UTILITIES - Version 1.0.0
# Last Updated: 2025-10-08
# DO NOT MODIFY - Use template generator to update
# ============================================================================
```

### 2. Use Generator for Consistency
Don't manually copy-paste. Use automated generation.

### 3. Document Which Apps Need Updates
```python
# App last generated: 2025-10-08
# Template version: 1.0.0
# Next update due: When template reaches v1.1.0
```

### 4. Test Before Mass Updates
- Update 1 app first
- Test thoroughly
- Then update remaining apps

### 5. Keep Template as Source of Truth
```bash
common/          # This is the master
├── styles.py    # Edit this
├── utils.py     # Edit this
└── validators.py

# Then regenerate apps:
python generator/generate_app.py --all --update-utilities
```

---

## 🎯 Recommended Approach

**Use Option A (Single-File) with Generator:**

1. Keep `common/` as master template
2. Create generator that embeds utilities
3. Each app = 1 self-contained file (~600 lines)
4. Easy to deploy to Snowflake
5. Updates via regeneration

**Why?**
- ✅ Simplest deployment (1 file)
- ✅ Works perfectly in SiS
- ✅ No import issues
- ✅ Generator maintains consistency
- ✅ Version tracking easy

**Trade-off Accepted:**
- Code duplication (but managed via generator)
- Slightly larger files
- Manual updates (but via generator)

---

## 📝 Next Steps

1. **Create Generator Script** (`generator/generate_app.py`)
2. **Update Template** with embedded pattern
3. **Generate Test App** (e.g., CrowdStrike)
4. **Deploy to Snowflake** and validate
5. **Generate Remaining Apps** if successful
6. **Document Deployment** process

---

## ✅ Summary

**For Snowflake Streamlit, we use:**
- ✅ Self-contained apps with embedded utilities
- ✅ Generator for consistency and updates
- ✅ `common/` as template source (not import library)
- ✅ Single-file apps for simplest deployment
- ✅ Version tracking in comments

**This approach:**
- Works natively in Snowflake
- Maintains code quality via generator
- Easy to deploy and maintain
- Trades duplication for simplicity (acceptable)

---

**Strategy Status**: ✅ Updated for Snowflake Reality
**Next Action**: Create generator script
**Expected Outcome**: 12 production-ready SiS apps
