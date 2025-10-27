# Streamlit Apps - Standardization & Enhancement Plan

## 🎯 Objective

1. **Standardize code format** across all 12 apps
2. **Review current data model** and available views
3. **Update apps** with new views and enhancements from recent model improvements
4. **Add missing functionality** based on available data

---

## 📋 Current State Assessment

### Apps Inventory (12 Total)
1. ✅ Ancon - IAM & Identity
2. ✅ BitSight - Security Ratings
3. ✅ Cisco_AMP - Malware Protection
4. ✅ Crowdstrike - EDR
5. ✅ Intel_Threats - Threat Intelligence
6. ✅ Qualys - Vulnerability Management
7. ✅ Sophos - Endpoint Protection
8. ✅ Splunk - SIEM
9. ✅ Symantec - Endpoint Security
10. ✅ Trellix - EDR & Threat Detection
11. ✅ Zerofox - External Threats
12. ✅ Zscaler - Cloud Security

### Recent Data Model Enhancements
From `EXECUTE_4_ENHANCEMENTS_WORKING.sql`:
- ✅ Top 13 Executive Metrics (NIST CSF 2.0 aligned)
- ✅ Data Quality Framework
- ✅ Data Lineage Catalog
- ✅ Monitoring & Alerting tables

---

## 🏗️ Standard App Structure

### Proposed Template Format

```python
"""
===============================================================================
SECURITY_ANALYTICS Streamlit App: [APP_NAME]
===============================================================================
Purpose: [Brief description]
Data Source: [Source system]
Version: 1.0.0
Last Updated: 2025-10-08
Maintained By: GenericCorp Data Engineering Team
===============================================================================
"""

# ============================================================================
# IMPORTS
# ============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from snowflake.snowpark.context import get_active_session
from datetime import datetime, timedelta
import numpy as np

# ============================================================================
# EMBEDDED UTILITIES (Version 1.0.0)
# These functions provide common functionality across all apps
# Source: 07_STREAMLIT_APPS/common/ (master templates)
# ============================================================================

@st.cache_data(ttl=300)
def safe_query(sql: str, error_message: str = "Failed to load data", max_rows: int = 10000):
    """Execute Snowflake query with error handling and caching"""
    try:
        session = get_active_session()
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
            st.code(f"Error: {str(e)}\\n\\nQuery:\\n{sql}")
        return pd.DataFrame()

def export_csv(df: pd.DataFrame, filename: str = "export"):
    """Add CSV export button"""
    if df.empty:
        return
    csv = df.to_csv(index=False).encode('utf-8')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    st.download_button(
        label="📥 Export to CSV",
        data=csv,
        file_name=f"{filename}_{timestamp}.csv",
        mime="text/csv"
    )

def apply_crh_styles():
    """Apply GenericCorp corporate styling"""
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #0a3d62 0%, #1e5f8e 100%);
            color: white;
            padding: 2.5rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 6px 20px rgba(10, 61, 98, 0.25);
        }
        div[data-testid="metric-container"] {
            background: linear-gradient(to bottom, #ffffff, #f8f9fa);
            border: 1px solid #e0e4e8;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(10, 61, 98, 0.08);
            transition: all 0.3s ease;
        }
        div[data-testid="metric-container"]:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(10, 61, 98, 0.15);
        }
    </style>
    """, unsafe_allow_html=True)

def show_data_freshness(table_name: str):
    """Display data freshness indicator"""
    sql = f"""
        SELECT
            MAX(INGESTION_TIMESTAMP) as LAST_UPDATE,
            DATEDIFF(minute, MAX(INGESTION_TIMESTAMP), CURRENT_TIMESTAMP()) as MINUTES_AGO
        FROM {table_name}
    """
    result = safe_query(sql, "Failed to check freshness")
    if not result.empty:
        mins = result['MINUTES_AGO'].iloc[0]
        if mins < 60:
            st.success(f"✅ Data is fresh ({mins} min ago)")
        elif mins < 1440:
            st.warning(f"⚠️ Data is {mins//60} hours old")
        else:
            st.error(f"❌ Data is stale ({mins//1440} days old)")

# ============================================================================
# APP CONFIGURATION
# ============================================================================

# Database & schema configuration
DB_LANDING = 'DEV_LANDING'
DB_TRANSFORMATION = 'DEV_TRANSFORMATION'
DB_REPORTING = 'DEV_REPORTING'
SCHEMA = 'SECURITY_ANALYTICS'

# App-specific views (customize per app)
VIEWS = {
    'summary': f'{DB_REPORTING}.{SCHEMA}.VW_[APP]_SUMMARY',
    'details': f'{DB_REPORTING}.{SCHEMA}.VW_[APP]_DETAILS',
    'trends': f'{DB_REPORTING}.{SCHEMA}.VW_[APP]_TRENDS',
    # Add more as needed
}

# Severity levels
SEVERITY_LEVELS = ['Critical', 'High', 'Medium', 'Low', 'Informational']

# ============================================================================
# PAGE SETUP
# ============================================================================

st.set_page_config(
    page_title="[APP NAME] Dashboard",
    page_icon="[ICON]",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_crh_styles()
session = get_active_session()

# ============================================================================
# HEADER
# ============================================================================

st.markdown("""
<div class="main-header">
    <h1 style="text-align: center; margin: 0;">
        <span style="font-size: 2.5rem;">[ICON]</span> [APP NAME] Dashboard
    </h1>
    <p style="text-align: center; margin: 0.75rem 0 0 0; opacity: 0.9; font-size: 1.1rem;">
        [Subtitle/Description]
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    # Branding
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #0a3d62, #1e5f8e);
         border-radius: 12px; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(10, 61, 98, 0.2);">
        <h2 style="color: white; margin: 0; font-size: 1.5rem;">🏢 GenericCorp</h2>
        <p style="color: #e8f0f8; font-size: 0.95rem; margin-top: 0.5rem;">Security Dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Filters
    st.header("📊 Dashboard Filters")

    days = st.selectbox(
        "Time Period",
        [1, 7, 30, 90],
        index=1,
        format_func=lambda x: f"Last {x} Days"
    )

    severity = st.multiselect(
        "Severity",
        SEVERITY_LEVELS,
        default=['Critical', 'High']
    )

    st.markdown("---")

    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()

    # Info
    st.info("""
    **📊 Data Source:** [Source System]
    **🔄 Refresh:** 5-minute cache
    **📈 Metrics:** Real-time
    """)

    # Last refresh
    st.markdown("---")
    st.caption(f"🕐 Last refresh: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ============================================================================
# MAIN CONTENT - TAB LAYOUT
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "📋 Detailed Data",
    "📈 Trends",
    "🔍 Data Quality"
])

# ----------------------------------------------------------------------------
# TAB 1: OVERVIEW
# ----------------------------------------------------------------------------

with tab1:
    st.subheader("Overview Metrics")

    # Data freshness
    show_data_freshness(VIEWS['summary'])

    # KPI Metrics (4 columns)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Metric 1 query
        pass

    # Visualizations
    st.markdown("---")
    st.subheader("Key Charts")

# ----------------------------------------------------------------------------
# TAB 2: DETAILED DATA
# ----------------------------------------------------------------------------

with tab2:
    st.subheader("Detailed Records")

    # Query and display
    # Add export button

# ----------------------------------------------------------------------------
# TAB 3: TRENDS
# ----------------------------------------------------------------------------

with tab3:
    st.subheader("Trend Analysis")

    # Time series charts

# ----------------------------------------------------------------------------
# TAB 4: DATA QUALITY
# ----------------------------------------------------------------------------

with tab4:
    st.subheader("Data Quality Metrics")

    # Quality checks
    # Completeness
    # Freshness
    # Volume trends

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("""
**Data Source:** [System] | **Database:** DEV_REPORTING.SECURITY_ANALYTICS |
**Contact:** Data Engineering Team | **Version:** 1.0.0
""")
```

---

## 📊 Phase 1: Inventory & Analysis

### Step 1.1: Extract Available Views
Query Snowflake to get all available views:

```sql
-- Run this to get current views
SELECT
    TABLE_CATALOG || '.' || TABLE_SCHEMA || '.' || TABLE_NAME as FULL_VIEW_NAME,
    TABLE_NAME,
    COMMENT
FROM DEV_REPORTING.INFORMATION_SCHEMA.VIEWS
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND TABLE_NAME LIKE 'VW_%'
ORDER BY TABLE_NAME;
```

### Step 1.2: Map Views to Apps

Create mapping document:

| App | Current Views Used | Available New Views | Missing Views Needed |
|-----|-------------------|---------------------|---------------------|
| Crowdstrike | ? | VW_EDR_THREATS, VW_ENDPOINT_COVERAGE | ? |
| Qualys | ? | VW_VULNERABILITY_TRENDS, VW_PATCH_COMPLIANCE | ? |
| Splunk | ? | VW_SIEM_ALERTS, VW_LOG_SOURCE_HEALTH | ? |
| ... | | | |

### Step 1.3: Identify Top 13 KPIs Integration

From `EXECUTE_4_ENHANCEMENTS_WORKING.sql`, these views are available:
- `VW_POWERBI_EXECUTIVE_DASHBOARD` - All 13 metrics
- Individual KPI tables (TOP13_KPI_01 through TOP13_KPI_13)

**Which apps should show which KPIs?**

| KPI | Metric Name | Relevant Apps |
|-----|-------------|---------------|
| KPI #1 | Asset Inventory Completeness | All apps |
| KPI #2 | Critical Asset Coverage | Crowdstrike, Symantec, Sophos |
| KPI #3 | Patch Compliance Rate | Qualys |
| KPI #4 | EDR Coverage | Crowdstrike, Trellix |
| KPI #5 | MFA Adoption | Ancon |
| KPI #6 | Mean Time to Detect | Splunk, Crowdstrike |
| KPI #7 | Security Alert Volume | Splunk |
| KPI #8 | Mean Time to Respond | Splunk |
| KPI #9 | Incident Response Rate | Splunk |
| KPI #10 | Mean Time to Recover | Splunk |
| KPI #11 | Vuln Remediation Time | Qualys |
| KPI #12 | Policy Compliance Score | All apps |
| KPI #13 | Security Training | Ancon |

---

## 🔧 Phase 2: Standardization Process

### For Each App:

1. **Backup Original**
   ```bash
   cp AppName/streamlit_app.py AppName/streamlit_app_original.py
   ```

2. **Apply Standard Template**
   - Copy template structure
   - Preserve app-specific queries
   - Add standard utilities
   - Add 4-tab layout

3. **Update Imports Section**
   - Standardize import order
   - Add version comments

4. **Add Embedded Utilities**
   - safe_query()
   - export_csv()
   - apply_crh_styles()
   - show_data_freshness()

5. **Restructure Content**
   - Move to tab layout
   - Add Data Quality tab
   - Standardize metrics display

6. **Test Locally** (if possible)
   ```python
   streamlit run streamlit_app.py
   ```

---

## 🚀 Phase 3: Enhancement Process

### For Each App:

1. **Add New Views** from data model
2. **Integrate Top 13 KPIs** (relevant ones)
3. **Add Data Quality Tab**
   - Row counts
   - Null percentages
   - Data freshness
   - Schema validation

4. **Add Export Functionality**
   - CSV export on all data tables

5. **Add Performance Metrics**
   - Query execution time
   - Row counts returned
   - Cache hit indicators

6. **Improve Visualizations**
   - Add trend charts
   - Add distribution charts
   - Add comparison charts (vs previous period)

---

## 📋 Execution Checklist

### Per App (30-45 min each):

- [ ] Backup original
- [ ] Apply standard format
- [ ] Add embedded utilities
- [ ] Restructure to 4 tabs
- [ ] Add new views from model
- [ ] Integrate relevant KPIs
- [ ] Add Data Quality tab
- [ ] Add export buttons
- [ ] Test queries
- [ ] Document changes
- [ ] Update README.md

### Quality Checks:
- [ ] All queries use safe_query()
- [ ] All queries have row limits
- [ ] All tables have export buttons
- [ ] Error handling in place
- [ ] Data freshness indicator present
- [ ] Consistent styling applied
- [ ] Comments and documentation added

---

## 📊 Expected Results

### Before Standardization:
- Inconsistent structure across apps
- Different styling approaches
- No error handling
- No export functionality
- Missing new views/metrics
- Variable code quality

### After Standardization:
- ✅ Consistent structure (all apps identical format)
- ✅ Uniform GenericCorp styling
- ✅ Comprehensive error handling
- ✅ Export on all data tables
- ✅ Latest views integrated
- ✅ Top 13 KPIs included (where relevant)
- ✅ Data Quality tab on all apps
- ✅ Professional documentation

---

## 🎯 Timeline

### Week 1:
- **Day 1**: Inventory & Analysis (Phase 1)
- **Day 2-3**: Standardize first 6 apps
- **Day 4-5**: Standardize remaining 6 apps

### Week 2:
- **Day 1-2**: Add enhancements to first 6 apps
- **Day 3-4**: Add enhancements to remaining 6 apps
- **Day 5**: Testing & documentation

**Total Effort**: 8-10 days (can be parallelized)

---

## 📝 Next Immediate Steps

1. **Extract View Inventory** from Snowflake
2. **Review one app** (e.g., Crowdstrike) in detail
3. **Create standardized version** of that one app
4. **Test and validate** approach
5. **Apply to remaining apps** if successful

---

## 🔍 What We Need to Review

1. **Current Views Available** in DEV_REPORTING.SECURITY_ANALYTICS
2. **Top 13 KPI Views** structure and usage
3. **Data Quality Views** (from enhancements)
4. **Data Lineage Views** (from enhancements)
5. **App-specific requirements** and customizations

---

**Ready to Start?** Let's begin with Phase 1: Inventory & Analysis!

**Status**: 📋 Plan Ready - Awaiting Execution
**Next Action**: Query Snowflake for available views or start with one app
