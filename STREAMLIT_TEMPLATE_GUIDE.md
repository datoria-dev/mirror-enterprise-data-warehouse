# Streamlit App Template Guide

**Version**: 1.0
**Date**: 2025-10-25
**Based on**: Analysis of 18 production SECURITY_ANALYTICS apps

---

## Overview

This guide explains the standardized Streamlit app template for SECURITY_ANALYTICS security service dashboards. The template is based on patterns identified across all 18 production apps.

---

## Tab Structure Analysis

### Distribution of Tabs Across Apps

| Tab Count | Number of Apps | Services |
|-----------|----------------|----------|
| **4 tabs** | 2 apps | Crowdstrike, Tenable |
| **5 tabs** | 2 apps | Cisco_AMP, Qualys |
| **6 tabs** | 10 apps | Ancon, CybelAngel, Intel_Threats, Leviat, Proofpoint, SentinelOne, Sophos, Splunk, Symantec, Trellix |
| **7 tabs** | 4 apps | BitSight, ServiceNow, Zerofox, Zscaler |

**Most Common**: 6 tabs (56% of apps)

---

## Common Tabs Across All Apps

### Core Tabs (Present in 30%+ of apps)

1. **Overview** - 7/18 apps (39%)
   - Purpose: High-level dashboard with key metrics
   - Contains: Asset distribution, compliance rates, critical findings
   - Used by: Crowdstrike, CybelAngel, Leviat, Proofpoint, SentinelOne, Tenable, ServiceNow

2. **Trends** - 5/18 apps (28%)
   - Purpose: Historical analysis and trending
   - Contains: Time-series data, trend charts, period comparisons
   - Used by: Crowdstrike, CybelAngel, Leviat, Tenable, ServiceNow

3. **Security Alerts** - 4/18 apps (22%)
   - Purpose: Active security alerts and incidents
   - Contains: Alert counts, severity breakdown, response times
   - Used by: Ancon, Sophos, Trellix, Zscaler

4. **OPCO Analysis** - 4/18 apps (22%)
   - Purpose: Organization-level performance analysis
   - Contains: OPCO comparison, coverage metrics, compliance by OPCO
   - Used by: Intel_Threats, Symantec, Trellix, Zerofox

### Frequently Used Tabs (Present in 15-20% of apps)

5. **Endpoint Health** - 3/18 apps (17%)
   - Used by: Sophos, Symantec, Trellix
   - Purpose: Device status and health monitoring

6. **Data Quality** - 3/18 apps (17%)
   - Used by: Crowdstrike, Intel_Threats, Zerofox
   - Purpose: Data completeness and quality metrics

7. **Threat Analysis** - 3/18 apps (17%)
   - Used by: SentinelOne, Symantec, Zscaler
   - Purpose: Threat intelligence and analysis

8. **Executive Dashboard** - 3/18 apps (17%)
   - Used by: Sophos, Splunk, Zscaler
   - Purpose: C-level summary and reporting

---

## Service-Specific Tab Examples

### EDR Services (Trellix, CrowdStrike, SentinelOne)

**Common tabs:**
- EDR Coverage / Overview
- Agent Health / Endpoint Status
- Security Alerts / Threat Analysis
- Trends
- OPCO Analysis

**Example - Trellix (6 tabs):**
1. EDR Coverage
2. Agent Health
3. Communication Status
4. AMCore Compliance
5. Security Alerts
6. OPCO Analysis

### SIEM Services (Splunk)

**Example - Splunk (6 tabs):**
1. Alert Trends
2. Response Times
3. Resolution Effectiveness
4. Log Coverage
5. Alert Analysis
6. Executive Dashboard

### Vulnerability Management (Qualys, Tenable)

**Example - Qualys (5 tabs):**
1. Vulnerability Analysis
2. Host Compliance
3. Patch Management
4. Scan Coverage
5. Trending & Analytics

### Identity & Access (Ancon, Leviat)

**Example - Ancon (6 tabs):**
1. Account Compliance
2. Security Alerts
3. Password Analytics
4. User Activity
5. Risk Assessment
6. Settings & Policies

### Risk Management (BitSight)

**Example - BitSight (7 tabs):**
1. Critical Findings
2. Risk Compliance
3. Risk Trends
4. Risk Vector Analysis
5. Vendor Risk
6. Security Posture
7. Remediation Pipeline

---

## Template Structure

### 1. Standard Components (All Apps)

Every app should include:

```python
# ✅ Dummy objects (for Snowflake compatibility)
# ✅ Page configuration
# ✅ Service metadata
# ✅ Helper functions
# ✅ Database connection
# ✅ Sidebar filters
# ✅ Executive summary
# ✅ Tabs section
# ✅ Footer
```

### 2. Executive Summary Section (Before Tabs)

**Always present** - Shows high-level KPIs:

```python
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Assets", "1,234")
with col2:
    st.metric("Active Assets", "1,200")
# ... etc
```

**Common metrics:**
- Total Assets
- Active/Compliant Assets
- Critical Issues
- Compliance Percentage
- OPCOs Monitored

### 3. Sidebar Filters (Standard)

**Always include:**
- Date range picker
- OPCO selector
- Service-specific filters (severity, status, etc.)
- Last updated timestamp

### 4. Tab Recommendations

#### Minimum (4 tabs):
1. Overview
2. Trends
3. Analysis (service-specific)
4. Executive Report

#### Recommended (6 tabs):
1. Overview
2. Trends
3. Security Alerts
4. OPCO Analysis
5. Detailed Analysis (service-specific)
6. Executive Report

#### Extended (7+ tabs):
Add service-specific tabs like:
- Vendor Risk (BitSight)
- CMDB Assets (ServiceNow)
- Threat Actors (Zerofox)
- Remediation Pipeline (BitSight)

---

## Customizing the Template

### Step 1: Update Service Configuration

```python
SERVICE_CONFIG = {
    'name': 'Trellix',  # Your service name
    'category': 'EDR',  # Service category
    'icon': '🛡️',  # Choose emoji
    'database': 'DEV_REPORTING',
    'schema': 'SECURITY_ANALYTICS',
    'main_table': 'TRELLIX_EDR_COVERAGE',  # Main view/table
}
```

### Step 2: Customize Tabs

Replace the tab list with service-appropriate tabs:

```python
tabs = st.tabs([
    "🔰 EDR Coverage",      # Service-specific
    "💊 Agent Health",       # Service-specific
    "📡 Communication Status",  # Service-specific
    "⚠️ Security Alerts",    # Common
    "📈 OPCO Analysis",      # Common
    "📋 Executive Report"    # Common
])
```

### Step 3: Update Queries

Modify SQL queries to match your service's data model:

```python
overview_query = f"""
SELECT
    OPCO_NAME,
    COUNT(DISTINCT ENDPOINT_ID) as ENDPOINT_COUNT,  # Your column names
    AVG(HEALTH_SCORE) as AVG_HEALTH,  # Your metrics
    ...
FROM {SERVICE_CONFIG['database']}.{SERVICE_CONFIG['schema']}.TRELLIX_ENDPOINTS
WHERE {where_clause}
GROUP BY OPCO_NAME
"""
```

### Step 4: Add Service-Specific Logic

Each tab should contain service-specific queries and visualizations while following the standard pattern:

```python
with tabs[0]:  # Your first service-specific tab
    st.markdown("### [Tab Title]")

    try:
        # Query data
        df = session.sql(your_query).to_pandas()

        if not df.empty:
            # Show metrics
            col1, col2, col3 = st.columns(3)
            # ... metrics

            # Show info message for charts
            create_info_message("Chart Type")

            # Show data table
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No data available")

    except Exception as e:
        st.error(f"Error: {str(e)}")
```

---

## Best Practices

### 1. Naming Conventions

**Tab Names:**
- Use emoji + descriptive name
- Keep concise (2-3 words)
- Use title case
- Examples: "🔰 EDR Coverage", "⏱️ Response Times", "🎯 Vulnerability Analysis"

**Metrics:**
- Use clear, business-friendly names
- Include units (%, count, days)
- Format consistently

### 2. Data Display

**Always include:**
- Info messages where charts were (Snowflake limitation)
- Data tables below where charts would be
- Proper number formatting (thousands separator, decimals)
- "No data" warnings when appropriate

**Example:**
```python
create_info_message("Trend Chart")  # Info about missing chart
st.dataframe(df.style.format({  # Formatted table
    'COUNT': '{:,.0f}',
    'PERCENTAGE': '{:.1f}%'
}))
```

### 3. Error Handling

Always wrap queries in try/except:

```python
try:
    df = session.sql(query).to_pandas()
    if not df.empty:
        # Display data
    else:
        st.warning("No data available")
except Exception as e:
    st.error(f"Error: {str(e)}")
```

### 4. Performance

- Use `@st.cache_resource` for session
- Limit query results (use LIMIT clause)
- Use efficient WHERE clauses
- Consider caching expensive queries

### 5. Filters

**Common filter pattern:**
```python
where_conditions = ["1=1"]

if selected_opco != 'All':
    where_conditions.append(f"OPCO_NAME = '{selected_opco}'")

where_conditions.append(f"DATA_DATE >= '{start_date}'")
where_conditions.append(f"DATA_DATE <= '{end_date}'")

where_clause = " AND ".join(where_conditions)
```

---

## Common Tab Patterns

### Pattern 1: Metrics + Chart + Table

```python
with tab:
    st.markdown("### [Title]")

    # 1. Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Metric 1", "1,234")
    # ... more metrics

    # 2. Chart placeholder
    st.markdown("#### [Chart Title]")
    create_info_message("Chart Type")

    # 3. Data table
    st.dataframe(df, use_container_width=True)
```

### Pattern 2: Side-by-Side Analysis

```python
with tab:
    st.markdown("### [Title]")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Analysis 1")
        create_info_message("Chart")
        st.dataframe(df1)

    with col2:
        st.markdown("#### Analysis 2")
        create_info_message("Chart")
        st.dataframe(df2)
```

### Pattern 3: Executive Summary

```python
with tab:
    st.markdown("### Executive Report")

    st.markdown(f"""
    ### {SERVICE_CONFIG['name']} - Executive Summary

    **Report Period:** {start_date} to {end_date}

    #### Key Findings
    [Summary text]

    #### Recommendations
    1. [Recommendation 1]
    2. [Recommendation 2]
    """)

    st.dataframe(summary_df)
```

---

## Migration Checklist

When creating a new app from the template:

- [ ] Update `SERVICE_CONFIG` with service details
- [ ] Customize tab names for service type
- [ ] Update all SQL queries with correct table/view names
- [ ] Update column names in queries
- [ ] Customize metrics in Executive Summary
- [ ] Add service-specific filters to sidebar
- [ ] Implement each tab with service-specific logic
- [ ] Test with actual data
- [ ] Validate all queries work in Snowflake
- [ ] Test all filters work correctly
- [ ] Add environment.yml file
- [ ] Deploy to Snowflake and test

---

## File Structure

```
SERVICE_NAME/
├── streamlit_app.py       # Main app (use template)
└── environment.yml        # Snowflake dependencies
```

**environment.yml:**
```yaml
name: streamlit
channels:
  - snowflake
dependencies:
  - streamlit
  - snowflake-snowpark-python
  - pandas
```

---

## Quick Start

### 1. Copy Template
```bash
cp STREAMLIT_APP_TEMPLATE.py 13_STREAMLIT_COMPLETE/YOUR_SERVICE/streamlit_app.py
```

### 2. Update Config
Edit `SERVICE_CONFIG` section

### 3. Customize Tabs
Update tab names and content

### 4. Update Queries
Modify SQL to match your data model

### 5. Test Locally
```python
# Test syntax
python -m py_compile streamlit_app.py
```

### 6. Deploy to Snowflake
Use manual copy-paste method (see FINAL_DEPLOYMENT_GUIDE.md)

---

## Examples by Service Type

### EDR (Endpoint Detection & Response)
**Services**: Trellix, CrowdStrike, SentinelOne, Sophos, Symantec
**Common Tabs**:
- Coverage/Overview
- Agent/Endpoint Health
- Security Alerts
- Threat Analysis
- OPCO Analysis

### SIEM (Security Information & Event Management)
**Services**: Splunk
**Common Tabs**:
- Alert Trends
- Response Times
- Resolution Effectiveness
- Log Coverage
- Executive Dashboard

### VM (Vulnerability Management)
**Services**: Qualys, Tenable
**Common Tabs**:
- Vulnerability Analysis
- Host Compliance
- Patch Management
- Scan Coverage
- Trending

### IAM (Identity & Access Management)
**Services**: Ancon, Leviat
**Common Tabs**:
- Account Compliance
- User Activity
- Access Analysis
- Risk Assessment
- Security Events

### Risk Management
**Services**: BitSight
**Common Tabs**:
- Risk Compliance
- Risk Trends
- Vendor Risk
- Remediation Pipeline
- Security Posture

---

## Summary

### Key Takeaways

1. **Standard Structure**: All apps follow similar pattern with Executive Summary + Tabs
2. **Common Tabs**: Overview (39%), Trends (28%), Security Alerts (22%), OPCO Analysis (22%)
3. **Typical Size**: 6 tabs is most common (56% of apps)
4. **Flexibility**: Add service-specific tabs as needed
5. **Consistency**: Use template for standardized user experience

### Template Benefits

✅ **Consistency**: Same user experience across all services
✅ **Maintainability**: Standard structure easier to update
✅ **Reusability**: Copy template for new services
✅ **Best Practices**: Built-in error handling, formatting, filters
✅ **Snowflake Ready**: Includes dummy objects, no external libraries
✅ **Production Tested**: Based on 18 working apps

---

**Last Updated**: 2025-10-25
**Version**: 1.0
**Status**: Production Ready
