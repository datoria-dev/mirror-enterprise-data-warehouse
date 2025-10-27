"""
SECURITY_ANALYTICS Streamlit App Template
Standardized template for all security service apps

Based on analysis of 18 production apps:
- Common tabs: Overview (39%), Trends (28%), Security Alerts (22%), OPCO Analysis (22%)
- Typical structure: 4-7 tabs per app (most common: 6 tabs)
- Standard components: Executive Summary, KPIs, Data Tables, Filters

Author: Data Engineering Team
Date: 2025-10-25
Version: 1.0 (Production Template)
"""

import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
from datetime import datetime, timedelta

# ============================================================================
# DUMMY OBJECTS FOR SNOWFLAKE COMPATIBILITY
# ============================================================================
# Snowflake Streamlit doesn't support plotly, numpy, matplotlib
# These dummy classes allow code to run without errors

class _DummyColors:
    '''Dummy color palettes'''
    class sequential:
        Reds = ['#fee5d9', '#fcae91', '#fb6a4a', '#de2d26', '#a50f15']
        Blues = ['#eff3ff', '#bdd7e7', '#6baed6', '#3182bd', '#08519c']
        Greens = ['#edf8e9', '#bae4b3', '#74c476', '#31a354', '#006d2c']
        RdYlGn = ['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641']
        Oranges = ['#feedde', '#fdbe85', '#fd8d3c', '#e6550d', '#a63603']

    class diverging:
        RdYlGn = ['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641']
        RdBu = ['#ca0020', '#f4a582', '#f7f7f7', '#92c5de', '#0571b0']

class _DummyNumpy:
    '''Dummy numpy replacement'''
    def round(self, *args, **kwargs):
        if args:
            return args[0]
        return None

    def array(self, *args, **kwargs):
        if args:
            return args[0]
        return []

    def __getattr__(self, name):
        def dummy_func(*args, **kwargs):
            if args:
                return args[0]
            return None
        return dummy_func

class _DummyFigure:
    '''Dummy Figure class that accepts any method call'''
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        def dummy_method(*args, **kwargs):
            return self
        return dummy_method

class _DummyGO:
    '''Dummy plotly.graph_objects'''
    def Figure(self, *args, **kwargs):
        return _DummyFigure()

    def __getattr__(self, name):
        def dummy_trace(*args, **kwargs):
            return _DummyFigure()
        return dummy_trace

class _DummySubplots:
    '''Dummy make_subplots function'''
    def __call__(self, *args, **kwargs):
        return _DummyFigure()

class _DummyPlotly:
    '''Dummy plotly.express'''
    colors = _DummyColors()

    def __getattr__(self, name):
        def dummy_chart(*args, **kwargs):
            return _DummyFigure()
        return dummy_chart

# Create dummy objects
px = _DummyPlotly()
go = _DummyGO()
make_subplots = _DummySubplots()
np = _DummyNumpy()

# ============================================================================
# CONFIGURATION
# ============================================================================

# Page config
st.set_page_config(
    page_title="[SERVICE NAME] Dashboard - SECURITY_ANALYTICS",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Service metadata (customize per service)
SERVICE_CONFIG = {
    'name': '[SERVICE_NAME]',  # e.g., 'Trellix', 'Splunk', 'CrowdStrike'
    'category': '[CATEGORY]',  # e.g., 'EDR', 'SIEM', 'Vulnerability Management'
    'icon': '🔒',  # Choose appropriate emoji
    'database': 'DEV_REPORTING',
    'schema': 'SECURITY_ANALYTICS',
    'main_table': '[SERVICE]_[MAIN_VIEW]',  # e.g., 'TRELLIX_EDR_COVERAGE'
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def safe_divide(numerator, denominator, default=0, multiplier=1):
    """Safe division to avoid division by zero"""
    try:
        if denominator == 0 or pd.isna(denominator):
            return default
        result = (float(numerator) / float(denominator)) * multiplier
        return result if not pd.isna(result) else default
    except:
        return default

def format_metric(value, metric_type='number'):
    """Format metrics consistently"""
    if pd.isna(value):
        return "N/A"

    if metric_type == 'percentage':
        return f"{value:.1f}%"
    elif metric_type == 'number':
        return f"{int(value):,}"
    elif metric_type == 'decimal':
        return f"{value:.2f}"
    else:
        return str(value)

def get_trend_indicator(current, previous):
    """Get trend indicator with color"""
    if pd.isna(current) or pd.isna(previous) or previous == 0:
        return "→", "gray"

    change = ((current - previous) / previous) * 100

    if change > 5:
        return "↑", "red"
    elif change < -5:
        return "↓", "green"
    else:
        return "→", "gray"

def create_info_message(chart_type="Chart"):
    """Create info message for missing charts"""
    st.info(f"📊 {chart_type} not available in Snowflake - view data in table below")

# ============================================================================
# DATABASE CONNECTION
# ============================================================================

@st.cache_resource
def get_session():
    """Get Snowflake session"""
    return get_active_session()

session = get_session()

# ============================================================================
# SIDEBAR - FILTERS
# ============================================================================

st.sidebar.title(f"{SERVICE_CONFIG['icon']} {SERVICE_CONFIG['name']}")
st.sidebar.markdown(f"**Category:** {SERVICE_CONFIG['category']}")
st.sidebar.markdown("---")

# Date range filter
st.sidebar.subheader("📅 Date Range")
end_date = datetime.now().date()
start_date = end_date - timedelta(days=30)

date_range = st.sidebar.date_input(
    "Select date range",
    value=(start_date, end_date),
    max_value=end_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date - timedelta(days=30)

# OPCO filter (common across most apps)
st.sidebar.subheader("🏢 OPCO Filter")

# Query available OPCOs from your service table
try:
    opcos_query = f"""
    SELECT DISTINCT OPCO_NAME
    FROM {SERVICE_CONFIG['database']}.{SERVICE_CONFIG['schema']}.{SERVICE_CONFIG['main_table']}
    WHERE OPCO_NAME IS NOT NULL
    ORDER BY OPCO_NAME
    """
    df_opcos = session.sql(opcos_query).to_pandas()
    available_opcos = ['All'] + df_opcos['OPCO_NAME'].tolist()
except:
    available_opcos = ['All']

selected_opco = st.sidebar.selectbox(
    "Select OPCO",
    options=available_opcos,
    index=0
)

# Additional filters (customize based on service)
st.sidebar.subheader("🔍 Additional Filters")

# Example: Severity filter (common for security tools)
severity_filter = st.sidebar.multiselect(
    "Severity",
    options=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
    default=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
)

# Example: Status filter
status_filter = st.sidebar.multiselect(
    "Status",
    options=['Active', 'Resolved', 'In Progress', 'Pending'],
    default=['Active', 'Resolved', 'In Progress', 'Pending']
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# ============================================================================
# MAIN HEADER
# ============================================================================

st.title(f"{SERVICE_CONFIG['icon']} {SERVICE_CONFIG['name']} - Security Monitoring Dashboard")
st.markdown(f"**{SERVICE_CONFIG['category']}** | Data Warehouse: SECURITY_ANALYTICS")
st.markdown("---")

# ============================================================================
# EXECUTIVE SUMMARY (Always first)
# ============================================================================

st.markdown("## 📊 Executive Summary")

# Build WHERE clause for filters
where_conditions = ["1=1"]

if selected_opco != 'All':
    where_conditions.append(f"OPCO_NAME = '{selected_opco}'")

where_conditions.append(f"DATA_DATE >= '{start_date}'")
where_conditions.append(f"DATA_DATE <= '{end_date}'")

where_clause = " AND ".join(where_conditions)

# Query executive metrics (customize based on your service)
try:
    exec_query = f"""
    SELECT
        COUNT(DISTINCT ASSET_ID) as TOTAL_ASSETS,
        COUNT(DISTINCT CASE WHEN STATUS = 'Active' THEN ASSET_ID END) as ACTIVE_ASSETS,
        COUNT(DISTINCT CASE WHEN SEVERITY IN ('CRITICAL', 'HIGH') THEN ISSUE_ID END) as CRITICAL_ISSUES,
        AVG(COMPLIANCE_PCT) as AVG_COMPLIANCE,
        COUNT(DISTINCT OPCO_NAME) as TOTAL_OPCOS
    FROM {SERVICE_CONFIG['database']}.{SERVICE_CONFIG['schema']}.{SERVICE_CONFIG['main_table']}
    WHERE {where_clause}
    """

    df_exec = session.sql(exec_query).to_pandas()

    if not df_exec.empty:
        # Display metrics in columns
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            total_assets = int(df_exec['TOTAL_ASSETS'].iloc[0]) if 'TOTAL_ASSETS' in df_exec.columns else 0
            st.metric("Total Assets", f"{total_assets:,}")

        with col2:
            active_assets = int(df_exec['ACTIVE_ASSETS'].iloc[0]) if 'ACTIVE_ASSETS' in df_exec.columns else 0
            st.metric("Active Assets", f"{active_assets:,}")

        with col3:
            critical_issues = int(df_exec['CRITICAL_ISSUES'].iloc[0]) if 'CRITICAL_ISSUES' in df_exec.columns else 0
            st.metric("Critical Issues", f"{critical_issues:,}")

        with col4:
            avg_compliance = float(df_exec['AVG_COMPLIANCE'].iloc[0]) if 'AVG_COMPLIANCE' in df_exec.columns else 0
            st.metric("Avg Compliance", f"{avg_compliance:.1f}%")

        with col5:
            total_opcos = int(df_exec['TOTAL_OPCOS'].iloc[0]) if 'TOTAL_OPCOS' in df_exec.columns else 0
            st.metric("OPCOs Monitored", f"{total_opcos}")
    else:
        st.warning("No data available for selected filters")

except Exception as e:
    st.error(f"Error loading executive summary: {str(e)}")

st.markdown("---")

# ============================================================================
# TABS SECTION
# ============================================================================

# Define tabs based on service type
# Customize this list for each service
tabs = st.tabs([
    "📊 Overview",           # Tab 1: Common across 39% of apps
    "📈 Trends",             # Tab 2: Common across 28% of apps
    "⚠️ Security Alerts",    # Tab 3: Common across 22% of apps
    "🏢 OPCO Analysis",      # Tab 4: Common across 22% of apps
    "🔍 Detailed Analysis",  # Tab 5: Service-specific
    "📋 Executive Report"    # Tab 6: Summary/reporting
])

# ============================================================================
# TAB 1: OVERVIEW
# ============================================================================

with tabs[0]:
    st.markdown("### Overview Dashboard")

    try:
        # Query overview data
        overview_query = f"""
        SELECT
            OPCO_NAME,
            COUNT(DISTINCT ASSET_ID) as ASSET_COUNT,
            AVG(COMPLIANCE_PCT) as COMPLIANCE_PCT,
            COUNT(DISTINCT CASE WHEN SEVERITY = 'CRITICAL' THEN ISSUE_ID END) as CRITICAL_COUNT
        FROM {SERVICE_CONFIG['database']}.{SERVICE_CONFIG['schema']}.{SERVICE_CONFIG['main_table']}
        WHERE {where_clause}
        GROUP BY OPCO_NAME
        ORDER BY ASSET_COUNT DESC
        """

        df_overview = session.sql(overview_query).to_pandas()

        if not df_overview.empty:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Asset Distribution by OPCO")
                create_info_message("Bar Chart")

                # Display as table
                st.dataframe(
                    df_overview[['OPCO_NAME', 'ASSET_COUNT']].style.format({
                        'ASSET_COUNT': '{:,.0f}'
                    }),
                    use_container_width=True
                )

            with col2:
                st.markdown("#### Compliance by OPCO")
                create_info_message("Line Chart")

                # Display as table
                st.dataframe(
                    df_overview[['OPCO_NAME', 'COMPLIANCE_PCT']].style.format({
                        'COMPLIANCE_PCT': '{:.1f}%'
                    }),
                    use_container_width=True
                )

            st.markdown("#### Complete Overview Data")
            st.dataframe(
                df_overview.style.format({
                    'ASSET_COUNT': '{:,.0f}',
                    'COMPLIANCE_PCT': '{:.1f}%',
                    'CRITICAL_COUNT': '{:,.0f}'
                }),
                use_container_width=True
            )
        else:
            st.warning("No overview data available")

    except Exception as e:
        st.error(f"Error loading overview: {str(e)}")

# ============================================================================
# TAB 2: TRENDS
# ============================================================================

with tabs[1]:
    st.markdown("### Trend Analysis")

    try:
        # Query trend data
        trends_query = f"""
        SELECT
            DATA_DATE,
            COUNT(DISTINCT ASSET_ID) as ASSET_COUNT,
            AVG(COMPLIANCE_PCT) as COMPLIANCE_PCT,
            COUNT(DISTINCT ISSUE_ID) as ISSUE_COUNT
        FROM {SERVICE_CONFIG['database']}.{SERVICE_CONFIG['schema']}.{SERVICE_CONFIG['main_table']}
        WHERE {where_clause}
        GROUP BY DATA_DATE
        ORDER BY DATA_DATE
        """

        df_trends = session.sql(trends_query).to_pandas()

        if not df_trends.empty:
            st.markdown("#### Key Metrics Over Time")
            create_info_message("Trend Chart")

            # Display metrics
            col1, col2, col3 = st.columns(3)

            with col1:
                current_assets = int(df_trends['ASSET_COUNT'].iloc[-1])
                prev_assets = int(df_trends['ASSET_COUNT'].iloc[0])
                delta = current_assets - prev_assets
                st.metric("Current Assets", f"{current_assets:,}", delta=f"{delta:+,}")

            with col2:
                current_compliance = float(df_trends['COMPLIANCE_PCT'].iloc[-1])
                prev_compliance = float(df_trends['COMPLIANCE_PCT'].iloc[0])
                delta = current_compliance - prev_compliance
                st.metric("Current Compliance", f"{current_compliance:.1f}%", delta=f"{delta:+.1f}%")

            with col3:
                current_issues = int(df_trends['ISSUE_COUNT'].iloc[-1])
                prev_issues = int(df_trends['ISSUE_COUNT'].iloc[0])
                delta = current_issues - prev_issues
                st.metric("Current Issues", f"{current_issues:,}", delta=f"{delta:+,}")

            st.markdown("#### Trend Data")
            st.dataframe(
                df_trends.style.format({
                    'DATA_DATE': lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else '',
                    'ASSET_COUNT': '{:,.0f}',
                    'COMPLIANCE_PCT': '{:.1f}%',
                    'ISSUE_COUNT': '{:,.0f}'
                }),
                use_container_width=True
            )
        else:
            st.warning("No trend data available")

    except Exception as e:
        st.error(f"Error loading trends: {str(e)}")

# ============================================================================
# TAB 3: SECURITY ALERTS
# ============================================================================

with tabs[2]:
    st.markdown("### Security Alerts")

    try:
        # Query security alerts
        alerts_query = f"""
        SELECT
            ALERT_ID,
            ALERT_SEVERITY,
            ALERT_TYPE,
            AFFECTED_ASSET,
            OPCO_NAME,
            ALERT_DATE,
            STATUS
        FROM {SERVICE_CONFIG['database']}.{SERVICE_CONFIG['schema']}.{SERVICE_CONFIG['main_table']}_ALERTS
        WHERE {where_clause}
        ORDER BY ALERT_DATE DESC
        LIMIT 1000
        """

        df_alerts = session.sql(alerts_query).to_pandas()

        if not df_alerts.empty:
            # Alert summary metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                critical_alerts = len(df_alerts[df_alerts['ALERT_SEVERITY'] == 'CRITICAL'])
                st.metric("Critical Alerts", f"{critical_alerts:,}")

            with col2:
                high_alerts = len(df_alerts[df_alerts['ALERT_SEVERITY'] == 'HIGH'])
                st.metric("High Alerts", f"{high_alerts:,}")

            with col3:
                active_alerts = len(df_alerts[df_alerts['STATUS'] == 'Active'])
                st.metric("Active Alerts", f"{active_alerts:,}")

            with col4:
                total_alerts = len(df_alerts)
                st.metric("Total Alerts", f"{total_alerts:,}")

            st.markdown("#### Alert Distribution by Severity")
            create_info_message("Pie Chart")

            severity_counts = df_alerts['ALERT_SEVERITY'].value_counts()
            st.dataframe(severity_counts, use_container_width=True)

            st.markdown("#### Recent Alerts")
            st.dataframe(
                df_alerts.head(100),
                use_container_width=True
            )
        else:
            st.info("No security alerts for selected period")

    except Exception as e:
        st.error(f"Error loading security alerts: {str(e)}")

# ============================================================================
# TAB 4: OPCO ANALYSIS
# ============================================================================

with tabs[3]:
    st.markdown("### OPCO Analysis")

    try:
        # Query OPCO data
        opco_query = f"""
        SELECT
            OPCO_NAME,
            COUNT(DISTINCT ASSET_ID) as TOTAL_ASSETS,
            COUNT(DISTINCT CASE WHEN STATUS = 'Active' THEN ASSET_ID END) as ACTIVE_ASSETS,
            AVG(COMPLIANCE_PCT) as COMPLIANCE_PCT,
            COUNT(DISTINCT ISSUE_ID) as TOTAL_ISSUES,
            COUNT(DISTINCT CASE WHEN SEVERITY IN ('CRITICAL', 'HIGH') THEN ISSUE_ID END) as CRITICAL_ISSUES
        FROM {SERVICE_CONFIG['database']}.{SERVICE_CONFIG['schema']}.{SERVICE_CONFIG['main_table']}
        WHERE {where_clause}
        GROUP BY OPCO_NAME
        ORDER BY TOTAL_ASSETS DESC
        """

        df_opco = session.sql(opco_query).to_pandas()

        if not df_opco.empty:
            st.markdown("#### OPCO Performance Summary")

            # Add calculated columns
            df_opco['COVERAGE_PCT'] = df_opco.apply(
                lambda row: safe_divide(row['ACTIVE_ASSETS'], row['TOTAL_ASSETS'], 0, 100),
                axis=1
            )

            # Display table
            st.dataframe(
                df_opco.style.format({
                    'TOTAL_ASSETS': '{:,.0f}',
                    'ACTIVE_ASSETS': '{:,.0f}',
                    'COMPLIANCE_PCT': '{:.1f}%',
                    'TOTAL_ISSUES': '{:,.0f}',
                    'CRITICAL_ISSUES': '{:,.0f}',
                    'COVERAGE_PCT': '{:.1f}%'
                }),
                use_container_width=True
            )

            # OPCO comparison chart
            st.markdown("#### OPCO Comparison")
            create_info_message("Comparison Chart")

        else:
            st.warning("No OPCO data available")

    except Exception as e:
        st.error(f"Error loading OPCO analysis: {str(e)}")

# ============================================================================
# TAB 5: DETAILED ANALYSIS (Service-specific)
# ============================================================================

with tabs[4]:
    st.markdown("### Detailed Analysis")
    st.info("Customize this tab based on service-specific requirements")

    # Example: Asset details
    try:
        details_query = f"""
        SELECT *
        FROM {SERVICE_CONFIG['database']}.{SERVICE_CONFIG['schema']}.{SERVICE_CONFIG['main_table']}
        WHERE {where_clause}
        LIMIT 500
        """

        df_details = session.sql(details_query).to_pandas()

        if not df_details.empty:
            st.markdown(f"#### Detailed Data ({len(df_details)} records)")
            st.dataframe(df_details, use_container_width=True)

            # Download button
            csv = df_details.to_csv(index=False)
            st.download_button(
                label="📥 Download Data as CSV",
                data=csv,
                file_name=f"{SERVICE_CONFIG['name']}_detailed_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No detailed data available")

    except Exception as e:
        st.error(f"Error loading detailed analysis: {str(e)}")

# ============================================================================
# TAB 6: EXECUTIVE REPORT
# ============================================================================

with tabs[5]:
    st.markdown("### Executive Report")

    st.markdown(f"""
    ### {SERVICE_CONFIG['name']} - Executive Summary

    **Report Period:** {start_date} to {end_date}
    **OPCO:** {selected_opco}
    **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

    ---

    #### Key Findings

    This report provides a comprehensive overview of {SERVICE_CONFIG['name']} monitoring data.

    **Report Sections:**
    1. Executive Summary - High-level KPIs
    2. Overview - Asset distribution and compliance
    3. Trends - Historical performance metrics
    4. Security Alerts - Active threats and issues
    5. OPCO Analysis - Performance by organization
    6. Detailed Analysis - Granular data view

    ---

    #### Recommendations

    Based on the data analysis:

    1. **Critical Issues**: Address critical severity items immediately
    2. **Compliance**: Focus on OPCOs with <80% compliance
    3. **Coverage**: Expand monitoring to uncovered assets
    4. **Trends**: Monitor negative trends for early intervention

    ---

    #### Next Steps

    - Review detailed findings in each tab
    - Export data for further analysis
    - Schedule follow-up reviews for critical items
    """)

    # Summary table
    st.markdown("#### Summary Metrics")
    try:
        summary_query = f"""
        SELECT
            '{SERVICE_CONFIG['name']}' as SERVICE,
            COUNT(DISTINCT OPCO_NAME) as TOTAL_OPCOS,
            COUNT(DISTINCT ASSET_ID) as TOTAL_ASSETS,
            AVG(COMPLIANCE_PCT) as AVG_COMPLIANCE,
            COUNT(DISTINCT ISSUE_ID) as TOTAL_ISSUES
        FROM {SERVICE_CONFIG['database']}.{SERVICE_CONFIG['schema']}.{SERVICE_CONFIG['main_table']}
        WHERE {where_clause}
        """

        df_summary = session.sql(summary_query).to_pandas()

        if not df_summary.empty:
            st.dataframe(
                df_summary.style.format({
                    'TOTAL_OPCOS': '{:,.0f}',
                    'TOTAL_ASSETS': '{:,.0f}',
                    'AVG_COMPLIANCE': '{:.1f}%',
                    'TOTAL_ISSUES': '{:,.0f}'
                }),
                use_container_width=True
            )
    except Exception as e:
        st.error(f"Error loading summary: {str(e)}")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: gray; font-size: 12px;'>
    <p>SECURITY_ANALYTICS Data Warehouse - {SERVICE_CONFIG['name']} Dashboard</p>
    <p>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
    Database: {SERVICE_CONFIG['database']}.{SERVICE_CONFIG['schema']}</p>
</div>
""", unsafe_allow_html=True)
