"""
CrowdStrike EDR Security Dashboard
Standardized Streamlit App for Snowflake

This app provides comprehensive analysis of CrowdStrike endpoint security coverage,
compliance, and threat detection metrics aligned with Top 13 KPIs.
"""

import streamlit as st
import pandas as pd
# import plotly.express as px  # Not available in Snowflake
# import plotly.graph_objects as go  # Not available in Snowflake
from datetime import datetime, timedelta
from snowflake.snowpark.context import get_active_session

# ============================================================================
# EMBEDDED UTILITIES - Configuration
# ============================================================================

DATABASES = {
    'landing': 'DEV_LANDING',
    'transformation': 'DEV_TRANSFORMATION',
    'reporting': 'DEV_REPORTING'
}
SCHEMA = 'SECURITY_ANALYTICS'
CACHE_TTL_SECONDS = 300
DEFAULT_ROW_LIMIT = 10000

# ============================================================================
# EMBEDDED UTILITIES - Styling
# ============================================================================

def get_color_scheme():
    """GenericCorp corporate color scheme"""
    return {
        'primary': '#0A3D62',
        'secondary': '#1E5F8B',
        'accent': '#2E86AB',
        'success': '#27AE60',
        'warning': '#F39C12',
        'danger': '#E74C3C',
        'info': '#3498DB',
        'light': '#ECF0F1',
        'dark': '#2C3E50',
        'bg_light': '#F8F9FA',
        'border': '#DEE2E6'
    }

def apply_crh_styles():
    """Apply GenericCorp corporate styling to the app"""
    colors = get_color_scheme()
    st.markdown(f"""
    <style>
        /* Main header styling */
        .main-header {{
            background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%);
            color: white;
            padding: 2.5rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 6px 20px rgba(10, 61, 98, 0.25);
            text-align: center;
        }}
        .main-header h1 {{
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        .main-header p {{
            margin: 0.5rem 0 0 0;
            font-size: 1.1rem;
            opacity: 0.95;
        }}

        /* Metric containers */
        div[data-testid="metric-container"] {{
            background: linear-gradient(to bottom, #ffffff, {colors['bg_light']});
            border: 1px solid {colors['border']};
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
        }}
        div[data-testid="metric-container"]:hover {{
            box-shadow: 0 4px 16px rgba(10, 61, 98, 0.15);
            transform: translateY(-2px);
        }}

        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background-color: {colors['bg_light']};
            padding: 10px;
            border-radius: 10px;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
            color: {colors['dark']};
            border: 1px solid {colors['border']};
        }}
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%);
            color: white;
            border-color: {colors['primary']};
        }}

        /* Dataframe styling */
        .dataframe {{
            border: 1px solid {colors['border']} !important;
            border-radius: 8px;
        }}

        /* Section headers */
        .section-header {{
            color: {colors['primary']};
            border-bottom: 3px solid {colors['accent']};
            padding-bottom: 0.5rem;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }}
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# EMBEDDED UTILITIES - Query Functions
# ============================================================================

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def safe_query(sql: str, error_message: str = "Failed to load data", max_rows: int = DEFAULT_ROW_LIMIT):
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
            st.code(f"Error: {str(e)}\n\nQuery:\n{sql}")
        return pd.DataFrame()

def export_csv(df: pd.DataFrame, filename: str = "export"):
    """Add CSV export button for a dataframe"""
    if df.empty:
        return
    csv = df.to_csv(index=False).encode('utf-8')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    st.download_button(
        label="📥 Export to CSV",
        data=csv,
        file_name=f"{filename}_{timestamp}.csv",
        mime="text/csv",
        key=f"export_{filename}_{timestamp}"
    )

def show_data_freshness(view_name: str):
    """Display data freshness indicator"""
    sql = f"""
    SELECT MAX(LAST_UPDATED) as LAST_UPDATE
    FROM {DATABASES['reporting']}.{SCHEMA}.{view_name}
    WHERE LAST_UPDATED IS NOT NULL
    """
    result = safe_query(sql, f"Could not check freshness for {view_name}", max_rows=1)

    if not result.empty and result['LAST_UPDATE'].iloc[0] is not None:
        last_update = pd.to_datetime(result['LAST_UPDATE'].iloc[0])
        hours_ago = (datetime.now() - last_update).total_seconds() / 3600

        if hours_ago < 24:
            color = "🟢"
            status = "Fresh"
        elif hours_ago < 48:
            color = "🟡"
            status = "Acceptable"
        else:
            color = "🔴"
            status = "Stale"

        st.caption(f"{color} **Data Freshness**: {status} - Last updated {last_update.strftime('%Y-%m-%d %H:%M')} ({int(hours_ago)}h ago)")

# ============================================================================
# EMBEDDED UTILITIES - Validation
# ============================================================================

def validate_environment(required_views: list):
    """Check that all required database views exist"""
    session = get_active_session()
    missing = []
    for view in required_views:
        try:
            session.sql(f"SELECT 1 FROM {view} LIMIT 1").collect()
        except Exception:
            missing.append(view)

    if missing:
        st.error("❌ **Missing Required Database Objects**")
        for view in missing:
            st.code(view)
        st.info("💡 Please ensure all required views are created in the database.")
        st.stop()

# ============================================================================
# APP CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="CrowdStrike EDR Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply styling
apply_crh_styles()

# Required views for this app
REQUIRED_VIEWS = [
    f"{DATABASES['reporting']}.{SCHEMA}.VW_CROWDSTRIKE_COVERAGE",
    f"{DATABASES['reporting']}.{SCHEMA}.VW_CROWDSTRIKE_ENDPOINT_RISK",
    f"{DATABASES['reporting']}.{SCHEMA}.VW_CROWDSTRIKE_VERSION_COMPLIANCE",
    f"{DATABASES['reporting']}.{SCHEMA}.VW_CROWDSTRIKE_USER_ACTIVITY",
    f"{DATABASES['reporting']}.{SCHEMA}.VW_CROWDSTRIKE_CLOUD_COVERAGE"
]

# Validate environment
validate_environment(REQUIRED_VIEWS)

# ============================================================================
# HEADER
# ============================================================================

st.markdown("""
<div class="main-header">
    <h1>🛡️ CrowdStrike EDR Security Dashboard</h1>
    <p>Endpoint Detection & Response | Coverage Analysis | Top 13 KPI #4 & #6</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - FILTERS
# ============================================================================

with st.sidebar:
    st.header("⚙️ Filters & Settings")

    # Date range filter
    date_range = st.selectbox(
        "📅 Time Period",
        ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last Year", "All Time"],
        index=1
    )

    # Map date range to days
    days_map = {
        "Last 7 Days": 7,
        "Last 30 Days": 30,
        "Last 90 Days": 90,
        "Last Year": 365,
        "All Time": 9999
    }
    days_back = days_map[date_range]

    # Platform filter
    platform_filter = st.multiselect(
        "🖥️ Platform",
        ["Windows", "Mac", "Linux", "All"],
        default=["All"],
        help="Filter by operating system platform"
    )

    # Risk level filter
    risk_filter = st.multiselect(
        "⚠️ Risk Level",
        ["Critical", "High", "Medium", "Low"],
        default=["Critical", "High", "Medium", "Low"],
        help="Filter by endpoint risk severity"
    )

    st.divider()

    # Refresh controls
    auto_refresh = st.checkbox("🔄 Auto-refresh (5 min)", value=True)
    if st.button("🔄 Refresh Now", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    # KPI Information
    st.info("""
    **Top 13 KPI Alignment:**
    - **KPI #4**: EDR Coverage Rate
    - **KPI #6**: Mean Time to Detect (MTTD)

    Aligned with NIST CSF 2.0
    """)

# ============================================================================
# TAB NAVIGATION
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "📋 Detailed Data",
    "📈 Trends",
    "✅ Data Quality"
])

# ============================================================================
# TAB 1: OVERVIEW
# ============================================================================

with tab1:
    # KPI Metrics Row
    st.markdown("### Key Performance Indicators")

    # Load coverage data
    coverage_sql = f"""
    SELECT
        TOTAL_ENDPOINTS,
        ACTIVE_COUNT,
        COVERAGE_PCT,
        GAP_TO_TARGET
    FROM {DATABASES['reporting']}.{SCHEMA}.VW_CROWDSTRIKE_COVERAGE
    WHERE REPORT_DATE >= DATEADD(day, -{days_back}, CURRENT_DATE())
    ORDER BY REPORT_DATE DESC
    LIMIT 1
    """
    coverage_data = safe_query(coverage_sql, "Failed to load coverage metrics")

    # Load risk summary
    risk_summary_sql = f"""
    SELECT
        COUNT(*) as TOTAL_RISK_ENDPOINTS,
        SUM(CASE WHEN RISK_CATEGORY = 'Critical' THEN 1 ELSE 0 END) as CRITICAL_RISK,
        SUM(CASE WHEN RISK_CATEGORY LIKE '%EOL%' THEN 1 ELSE 0 END) as EOL_ENDPOINTS,
        SUM(CASE WHEN IS_ACTIVE = FALSE THEN 1 ELSE 0 END) as INACTIVE_ENDPOINTS
    FROM {DATABASES['reporting']}.{SCHEMA}.VW_CROWDSTRIKE_ENDPOINT_RISK
    """
    risk_summary = safe_query(risk_summary_sql, "Failed to load risk summary")

    if not coverage_data.empty:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total = coverage_data['TOTAL_ENDPOINTS'].iloc[0]
            st.metric(
                "Total Endpoints",
                f"{total:,}",
                help="Total number of endpoints in the environment"
            )

        with col2:
            active = coverage_data['ACTIVE_COUNT'].iloc[0]
            coverage_pct = coverage_data['COVERAGE_PCT'].iloc[0]
            st.metric(
                "EDR Coverage (KPI #4)",
                f"{coverage_pct:.1f}%",
                f"{active:,} active",
                delta=f"{coverage_pct - 95:.1f}%" if coverage_pct < 95 else None,
                delta_color="inverse" if coverage_pct < 95 else "normal",
                help="Percentage of endpoints with active EDR agents - Target: 95%"
            )

        with col3:
            if not risk_summary.empty:
                eol = risk_summary['EOL_ENDPOINTS'].iloc[0]
                st.metric(
                    "EOL Versions",
                    f"{eol:,}",
                    help="Endpoints running end-of-life software versions"
                )

        with col4:
            if not risk_summary.empty:
                critical = risk_summary['CRITICAL_RISK'].iloc[0]
                st.metric(
                    "Critical Risk",
                    f"{critical:,}",
                    help="Endpoints with critical security risks"
                )

    st.divider()

    # Two-column layout for charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎯 Coverage Trend")

        coverage_trend_sql = f"""
        SELECT
            REPORT_DATE,
            COVERAGE_PCT,
            TOTAL_ENDPOINTS,
            ACTIVE_COUNT
        FROM {DATABASES['reporting']}.{SCHEMA}.VW_CROWDSTRIKE_COVERAGE
        WHERE REPORT_DATE >= DATEADD(day, -{days_back}, CURRENT_DATE())
        ORDER BY REPORT_DATE
        """
        coverage_trend = safe_query(coverage_trend_sql, "Failed to load coverage trend")

        if not coverage_trend.empty:
            colors = get_color_scheme()
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=coverage_trend['REPORT_DATE'],
                y=coverage_trend['COVERAGE_PCT'],
                mode='lines+markers',
                name='Coverage %',
                line=dict(color=colors['secondary'], width=3),
                marker=dict(size=8, color=colors['primary'])
            ))

            fig.add_hline(
                y=95,
                line_dash="dash",
                line_color=colors['primary'],
                annotation_text="Target: 95%"
            )

            # Add color zones
            fig.add_hrect(y0=0, y1=90, fillcolor=colors['danger'], opacity=0.05)
            fig.add_hrect(y0=90, y1=95, fillcolor=colors['warning'], opacity=0.05)
            fig.add_hrect(y0=95, y1=100, fillcolor=colors['success'], opacity=0.05)

            fig.update_layout(
                height=400,
                xaxis_title="Date",
                yaxis_title="Coverage %",
                yaxis_range=[80, 100],
                plot_bgcolor='white',
                showlegend=False
            )

            if fig: st.info("Chart not available in Snowflake - view data in table") # st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No coverage trend data available")

    with col2:
        st.markdown("### ⚠️ Risk Distribution")

        risk_dist_sql = f"""
        SELECT
            RISK_CATEGORY,
            COUNT(*) as ENDPOINT_COUNT
        FROM {DATABASES['reporting']}.{SCHEMA}.VW_CROWDSTRIKE_ENDPOINT_RISK
        WHERE RISK_CATEGORY IN ({','.join([f"'{s}'" for s in risk_filter])})
        GROUP BY RISK_CATEGORY
        ORDER BY
            CASE RISK_CATEGORY
                WHEN 'Critical' THEN 1
                WHEN 'High Risk' THEN 2
                WHEN 'Medium' THEN 3
                WHEN 'Low' THEN 4
                ELSE 5
            END
        """
        risk_dist = safe_query(risk_dist_sql, "Failed to load risk distribution")

        if not risk_dist.empty:
            colors_map = {
                'Critical': '#E74C3C',
                'High Risk': '#E67E22',
                'Medium': '#F39C12',
                'Low': '#27AE60',
                'Compliant': '#3498DB'
            }
            fig = px.pie(
                risk_dist,
                values='ENDPOINT_COUNT',
                names='RISK_CATEGORY',
                color='RISK_CATEGORY',
                color_discrete_map=colors_map
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            if fig: st.info("Chart not available in Snowflake - view data in table") # st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No risk data available")

    st.divider()

    # Version Compliance Section
    st.markdown("### 🔄 Agent Version Compliance")

    version_sql = f"""
    SELECT
        VERSION,
        ENDPOINT_COUNT,
        SUPPORT_STATUS,
        DAYS_UNTIL_EOL
    FROM {DATABASES['reporting']}.{SCHEMA}.VW_CROWDSTRIKE_VERSION_COMPLIANCE
    ORDER BY ENDPOINT_COUNT DESC
    LIMIT 10
    """
    version_data = safe_query(version_sql, "Failed to load version data")

    if not version_data.empty:
        # Color code based on support status
        def highlight_version(row):
            if row['SUPPORT_STATUS'] == 'Supported':
                return ['background-color: #D5F4E6'] * len(row)
            elif row['SUPPORT_STATUS'] == 'EOL':
                return ['background-color: #FADBD8'] * len(row)
            else:
                return ['background-color: #FCF3CF'] * len(row)

        styled_df = version_data.style.apply(highlight_version, axis=1)
        st.dataframe(styled_df, use_container_width=True, height=350)
        export_csv(version_data, "crowdstrike_version_compliance")
    else:
        st.info("No version compliance data available")

    show_data_freshness("VW_CROWDSTRIKE_VERSION_COMPLIANCE")

# ============================================================================
# TAB 2: DETAILED DATA
# ============================================================================

with tab2:
    st.markdown("### 📋 Detailed Endpoint Analysis")

    # Data selector
    data_view = st.selectbox(
        "Select Data View",
        ["Endpoint Risk Details", "User Activity", "Cloud Coverage", "Compliance Settings"]
    )

    if data_view == "Endpoint Risk Details":
        st.markdown("#### High-Risk Endpoints Requiring Attention")

        endpoint_risk_sql = f"""
        SELECT
            HOSTNAME,
            PLATFORM,
            OS_PRODUCT_NAME,
            SENSOR_VERSION,
            DAYS_UNTIL_EOL,
            DAYS_INACTIVE,
            RISK_CATEGORY,
            REMEDIATION_STATUS
        FROM {DATABASES['reporting']}.{SCHEMA}.VW_CROWDSTRIKE_ENDPOINT_RISK
        WHERE RISK_CATEGORY IN ({','.join([f"'{s}'" for s in risk_filter if s in ['Critical', 'High']])})
        ORDER BY
            CASE RISK_CATEGORY
                WHEN 'Critical' THEN 1
                WHEN 'High Risk' THEN 2
                ELSE 3
            END,
            DAYS_INACTIVE DESC
        LIMIT 500
        """
        endpoint_risk = safe_query(endpoint_risk_sql, "Failed to load endpoint risk details")

        if not endpoint_risk.empty:
            st.dataframe(endpoint_risk, use_container_width=True, height=500)
            export_csv(endpoint_risk, "endpoint_risk_details")

            # Summary stats
            col1, col2, col3 = st.columns(3)
            with col1:
                critical_count = len(endpoint_risk[endpoint_risk['RISK_CATEGORY'] == 'Critical'])
                st.metric("Critical Risk Endpoints", critical_count)
            with col2:
                eol_count = len(endpoint_risk[endpoint_risk['DAYS_UNTIL_EOL'] <= 0])
                st.metric("Already EOL", eol_count)
            with col3:
                inactive_count = len(endpoint_risk[endpoint_risk['DAYS_INACTIVE'] > 30])
                st.metric("Inactive >30 days", inactive_count)
        else:
            st.info("No high-risk endpoint data available for selected filters")

        show_data_freshness("VW_CROWDSTRIKE_ENDPOINT_RISK")

    elif data_view == "User Activity":
        st.markdown("#### User Activity Analysis")

        user_activity_sql = f"""
        SELECT
            HOSTNAME,
            LAST_LOGGED_IN_USER,
            LAST_USER_LOGIN,
            DAYS_SINCE_LOGIN,
            ACCOUNT_STATUS,
            OS_PRODUCT_NAME
        FROM {DATABASES['reporting']}.{SCHEMA}.VW_CROWDSTRIKE_USER_ACTIVITY
        WHERE DAYS_SINCE_LOGIN >= 0
        ORDER BY DAYS_SINCE_LOGIN DESC
        LIMIT 500
        """
        user_activity = safe_query(user_activity_sql, "Failed to load user activity")

        if not user_activity.empty:
            st.dataframe(user_activity, use_container_width=True, height=500)
            export_csv(user_activity, "user_activity")

            # Activity distribution
            col1, col2, col3 = st.columns(3)
            with col1:
                active = len(user_activity[user_activity['DAYS_SINCE_LOGIN'] <= 7])
                st.metric("Active (≤7 days)", f"{active:,}")
            with col2:
                inactive = len(user_activity[user_activity['DAYS_SINCE_LOGIN'] > 30])
                st.metric("Inactive (>30 days)", f"{inactive:,}")
            with col3:
                avg_days = user_activity['DAYS_SINCE_LOGIN'].mean()
                st.metric("Avg Days Since Login", f"{avg_days:.1f}")
        else:
            st.info("No user activity data available")

        show_data_freshness("VW_CROWDSTRIKE_USER_ACTIVITY")

    elif data_view == "Cloud Coverage":
        st.markdown("#### Cloud Workload Coverage")

        cloud_sql = f"""
        SELECT
            ENVIRONMENT,
            TOTAL_ENDPOINTS,
            ACTIVE_ENDPOINTS,
            COVERAGE_PCT,
            EOL_VERSIONS,
            EOL_PCT
        FROM {DATABASES['reporting']}.{SCHEMA}.VW_CROWDSTRIKE_CLOUD_COVERAGE
        ORDER BY TOTAL_ENDPOINTS DESC
        """
        cloud_data = safe_query(cloud_sql, "Failed to load cloud coverage")

        if not cloud_data.empty:
            st.dataframe(cloud_data, use_container_width=True, height=500)
            export_csv(cloud_data, "cloud_coverage")

            # Cloud environment comparison
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=cloud_data['ENVIRONMENT'],
                y=cloud_data['COVERAGE_PCT'],
                name='Coverage %',
                marker_color='#0A3D62',
                text=cloud_data['COVERAGE_PCT'],
                texttemplate='%{text:.1f}%',
                textposition='outside'
            ))
            fig.add_hline(y=95, line_dash="dash", line_color="green", annotation_text="Target: 95%")
            fig.update_layout(
                height=350,
                xaxis_title="Environment",
                yaxis_title="Coverage %",
                plot_bgcolor='white'
            )
            if fig: st.info("Chart not available in Snowflake - view data in table") # st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No cloud coverage data available")

        show_data_freshness("VW_CROWDSTRIKE_CLOUD_COVERAGE")

    else:  # Compliance Settings
        st.markdown("#### Compliance Configuration")

        settings_sql = f"""
        SELECT
            PARAMETER_NAME,
            PARAMETER_VALUE,
            DESCRIPTION
        FROM {DATABASES['reporting']}.{SCHEMA}.VW_CROWDSTRIKE_COMPLIANCE_SETTINGS
        """
        settings_data = safe_query(settings_sql, "Failed to load compliance settings")

        if not settings_data.empty:
            st.dataframe(settings_data, use_container_width=True, height=500)

            # Display as metrics
            st.markdown("#### Current Thresholds")
            cols = st.columns(len(settings_data))
            for idx, row in settings_data.iterrows():
                with cols[idx]:
                    st.metric(
                        row['PARAMETER_NAME'],
                        f"{row['PARAMETER_VALUE']}%",
                        help=row['DESCRIPTION']
                    )
        else:
            st.info("No compliance settings data available")

# ============================================================================
# TAB 3: TRENDS
# ============================================================================

with tab3:
    st.markdown("### 📈 Historical Trends & Analytics")

    # Trend selector
    trend_type = st.selectbox(
        "Select Trend Analysis",
        ["Coverage Trends", "Endpoint Growth", "Platform Distribution", "Mean Time to Detect (MTTD)"]
    )

    if trend_type == "Coverage Trends":
        st.markdown("#### EDR Coverage Over Time (KPI #4)")

        coverage_trend_sql = f"""
        SELECT
            REPORT_DATE,
            COVERAGE_PCT,
            TOTAL_ENDPOINTS,
            ACTIVE_COUNT,
            COMPLIANCE_STATUS
        FROM {DATABASES['reporting']}.{SCHEMA}.VW_CROWDSTRIKE_COVERAGE
        WHERE REPORT_DATE >= DATEADD(day, -{days_back}, CURRENT_DATE())
        ORDER BY REPORT_DATE
        """
        coverage_trend = safe_query(coverage_trend_sql, "Failed to load coverage trends")

        if not coverage_trend.empty:
            # Calculate moving averages
            coverage_trend['MA_7'] = coverage_trend['COVERAGE_PCT'].rolling(window=7, min_periods=1).mean()
            coverage_trend['MA_30'] = coverage_trend['COVERAGE_PCT'].rolling(window=30, min_periods=1).mean()

            colors = get_color_scheme()
            fig = go.Figure()

            # Daily coverage (light)
            fig.add_trace(go.Scatter(
                x=coverage_trend['REPORT_DATE'],
                y=coverage_trend['COVERAGE_PCT'],
                mode='lines',
                name='Daily Coverage',
                line=dict(color=colors['light'], width=1),
                opacity=0.6
            ))

            # 7-day MA
            fig.add_trace(go.Scatter(
                x=coverage_trend['REPORT_DATE'],
                y=coverage_trend['MA_7'],
                mode='lines',
                name='7-Day Average',
                line=dict(color=colors['accent'], width=2)
            ))

            # 30-day MA
            fig.add_trace(go.Scatter(
                x=coverage_trend['REPORT_DATE'],
                y=coverage_trend['MA_30'],
                mode='lines',
                name='30-Day Average',
                line=dict(color=colors['primary'], width=3)
            ))

            fig.add_hline(y=95, line_dash="dash", line_color=colors['primary'], annotation_text="Target: 95%")

            fig.update_layout(
                height=500,
                xaxis_title="Date",
                yaxis_title="Coverage %",
                hovermode='x unified',
                plot_bgcolor='white',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            if fig: st.info("Chart not available in Snowflake - view data in table") # st.plotly_chart(fig, use_container_width=True)

            # Trend summary
            col1, col2, col3 = st.columns(3)
            with col1:
                trend_change = coverage_trend['COVERAGE_PCT'].iloc[-1] - coverage_trend['COVERAGE_PCT'].iloc[0]
                st.metric("Coverage Change", f"{trend_change:+.1f}%", help=f"Change over {date_range}")
            with col2:
                avg_coverage = coverage_trend['COVERAGE_PCT'].mean()
                st.metric("Average Coverage", f"{avg_coverage:.1f}%")
            with col3:
                current_coverage = coverage_trend['COVERAGE_PCT'].iloc[-1]
                st.metric("Current Coverage", f"{current_coverage:.1f}%")
        else:
            st.info("No coverage trend data available")

    elif trend_type == "Endpoint Growth":
        st.markdown("#### Total vs Active Endpoints Over Time")

        growth_sql = f"""
        SELECT
            REPORT_DATE,
            TOTAL_ENDPOINTS,
            ACTIVE_COUNT
        FROM {DATABASES['reporting']}.{SCHEMA}.VW_CROWDSTRIKE_COVERAGE
        WHERE REPORT_DATE >= DATEADD(day, -{days_back}, CURRENT_DATE())
        ORDER BY REPORT_DATE
        """
        growth_data = safe_query(growth_sql, "Failed to load growth data")

        if not growth_data.empty:
            colors = get_color_scheme()
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=growth_data['REPORT_DATE'],
                y=growth_data['TOTAL_ENDPOINTS'],
                name='Total Endpoints',
                marker_color=colors['dark']
            ))

            fig.add_trace(go.Bar(
                x=growth_data['REPORT_DATE'],
                y=growth_data['ACTIVE_COUNT'],
                name='Active Endpoints',
                marker_color=colors['secondary']
            ))

            fig.update_layout(
                height=450,
                xaxis_title="Date",
                yaxis_title="Endpoint Count",
                barmode='overlay',
                plot_bgcolor='white'
            )

            if fig: st.info("Chart not available in Snowflake - view data in table") # st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No endpoint growth data available")

    elif trend_type == "Platform Distribution":
        st.markdown("#### Endpoints by Platform Over Time")

        platform_sql = f"""
        SELECT
            PLATFORM,
            COUNT(*) as ENDPOINT_COUNT
        FROM {DATABASES['reporting']}.{SCHEMA}.VW_CROWDSTRIKE_ENDPOINT_RISK
        GROUP BY PLATFORM
        ORDER BY ENDPOINT_COUNT DESC
        """
        platform_data = safe_query(platform_sql, "Failed to load platform data")

        if not platform_data.empty:
            colors_map = {
                'Windows': '#0078D4',
                'Mac': '#555555',
                'Linux': '#FF9500'
            }
            fig = px.pie(
                platform_data,
                values='ENDPOINT_COUNT',
                names='PLATFORM',
                title='Endpoint Platform Distribution',
                color='PLATFORM',
                color_discrete_map=colors_map
            )
            fig.update_traces(textposition='inside', textinfo='percent+label+value')
            fig.update_layout(height=450)
            if fig: st.info("Chart not available in Snowflake - view data in table") # st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No platform distribution data available")

    else:  # MTTD
        st.markdown("#### Mean Time to Detect (MTTD) - KPI #6")
        st.info("📊 **KPI #6**: Measures average time from threat occurrence to detection. Target: < 15 minutes")

        st.warning("⚠️ **MTTD View Not Yet Implemented**")
        st.code("""
-- Create MTTD view:
CREATE OR REPLACE VIEW DEV_REPORTING.SECURITY_ANALYTICS.VW_CROWDSTRIKE_MTTD AS
SELECT
    DATE_TRUNC('day', DETECTION_TIME) as DATE,
    AVG(DATEDIFF('minute', EVENT_TIME, DETECTION_TIME)) as AVG_MTTD_MINUTES,
    MEDIAN(DATEDIFF('minute', EVENT_TIME, DETECTION_TIME)) as MEDIAN_MTTD_MINUTES,
    MIN(DATEDIFF('minute', EVENT_TIME, DETECTION_TIME)) as MIN_MTTD_MINUTES,
    MAX(DATEDIFF('minute', EVENT_TIME, DETECTION_TIME)) as MAX_MTTD_MINUTES,
    COUNT(*) as DETECTIONS_COUNT
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_EDR_DETECTIONS
WHERE DETECTION_TIME >= DATEADD(day, -90, CURRENT_DATE())
GROUP BY DATE_TRUNC('day', DETECTION_TIME);
        """)

# ============================================================================
# TAB 4: DATA QUALITY
# ============================================================================

with tab4:
    st.markdown("### ✅ Data Quality & Validation")

    # Data completeness checks
    st.markdown("#### Data Completeness")

    quality_checks = []

    for view in REQUIRED_VIEWS:
        view_name = view.split('.')[-1]

        # Row count
        count_sql = f"SELECT COUNT(*) as ROW_COUNT FROM {view}"
        count_result = safe_query(count_sql, f"Failed to check {view_name}", max_rows=1)

        if not count_result.empty:
            row_count = count_result['ROW_COUNT'].iloc[0]

            # Freshness check
            freshness_sql = f"""
            SELECT MAX(LAST_UPDATED) as LAST_UPDATE
            FROM {view}
            WHERE LAST_UPDATED IS NOT NULL
            """
            freshness_result = safe_query(freshness_sql, f"Failed to check freshness for {view_name}", max_rows=1)

            if not freshness_result.empty and freshness_result['LAST_UPDATE'].iloc[0] is not None:
                last_update = pd.to_datetime(freshness_result['LAST_UPDATE'].iloc[0])
                hours_ago = (datetime.now() - last_update).total_seconds() / 3600
                freshness_status = "✅ Fresh" if hours_ago < 24 else "⚠️ Stale" if hours_ago < 48 else "❌ Old"
            else:
                last_update = None
                freshness_status = "⚠️ Unknown"

            quality_checks.append({
                'View': view_name,
                'Row Count': f"{row_count:,}",
                'Last Updated': last_update.strftime('%Y-%m-%d %H:%M') if last_update else 'N/A',
                'Status': freshness_status
            })

    if quality_checks:
        quality_df = pd.DataFrame(quality_checks)
        st.dataframe(quality_df, use_container_width=True, height=300)

    st.divider()

    # Data validation rules
    st.markdown("#### Data Validation Rules")

    validation_results = []

    # Rule 1: Coverage percentage should be between 0 and 100
    validation_sql = f"""
    SELECT COUNT(*) as VIOLATIONS
    FROM {DATABASES['reporting']}.{SCHEMA}.VW_CROWDSTRIKE_COVERAGE
    WHERE COVERAGE_PCT < 0 OR COVERAGE_PCT > 100
    """
    result = safe_query(validation_sql, "Validation check failed", max_rows=1)
    if not result.empty:
        violations = result['VIOLATIONS'].iloc[0]
        validation_results.append({
            'Rule': 'Coverage % between 0-100',
            'Status': '✅ Pass' if violations == 0 else f'❌ Fail ({violations} violations)',
            'Severity': 'High'
        })

    # Rule 2: No null hostnames
    validation_sql = f"""
    SELECT COUNT(*) as VIOLATIONS
    FROM {DATABASES['reporting']}.{SCHEMA}.VW_CROWDSTRIKE_ENDPOINT_RISK
    WHERE HOSTNAME IS NULL
    """
    result = safe_query(validation_sql, "Validation check failed", max_rows=1)
    if not result.empty:
        violations = result['VIOLATIONS'].iloc[0]
        validation_results.append({
            'Rule': 'No null hostnames',
            'Status': '✅ Pass' if violations == 0 else f'❌ Fail ({violations} violations)',
            'Severity': 'Medium'
        })

    # Rule 3: Latest data within 7 days
    validation_sql = f"""
    SELECT DATEDIFF('day', MAX(REPORT_DATE), CURRENT_DATE()) as DAYS_OLD
    FROM {DATABASES['reporting']}.{SCHEMA}.VW_CROWDSTRIKE_COVERAGE
    """
    result = safe_query(validation_sql, "Validation check failed", max_rows=1)
    if not result.empty:
        days_old = result['DAYS_OLD'].iloc[0]
        validation_results.append({
            'Rule': 'Latest data within 7 days',
            'Status': '✅ Pass' if days_old <= 7 else f'⚠️ Warning ({days_old} days old)',
            'Severity': 'Low'
        })

    if validation_results:
        validation_df = pd.DataFrame(validation_results)
        st.dataframe(validation_df, use_container_width=True, height=250)

    st.divider()

    # Data refresh schedule
    st.markdown("#### Data Refresh Schedule")
    st.info("""
    **Automated Data Pipeline:**
    - **Real-time Ingestion**: Snowpipe auto-ingest from CrowdStrike API
    - **Transformation**: Snowflake Tasks run hourly
    - **View Refresh**: Materialized on query (no refresh needed)
    - **Expected Latency**: < 30 minutes from source to reporting layer

    For pipeline status and monitoring, check the Data Pipeline Dashboard.
    """)

    # Quick diagnostics
    with st.expander("🔧 Quick Diagnostics"):
        st.markdown("**Database Connection:**")
        try:
            session = get_active_session()
            st.success("✅ Connected to Snowflake")
            current_db = session.sql("SELECT CURRENT_DATABASE()").collect()[0][0]
            current_schema = session.sql("SELECT CURRENT_SCHEMA()").collect()[0][0]
            current_warehouse = session.sql("SELECT CURRENT_WAREHOUSE()").collect()[0][0]

            st.code(f"""
Database: {current_db}
Schema: {current_schema}
Warehouse: {current_warehouse}
            """)
        except Exception as e:
            st.error(f"❌ Connection error: {str(e)}")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.caption("🛡️ CrowdStrike EDR Dashboard | GenericCorp Security Operations | Data updated automatically via Snowpipe")
st.caption(f"Dashboard generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Aligned with NIST CSF 2.0 Framework")
