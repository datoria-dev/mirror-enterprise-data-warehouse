# Import packages - Snowflake compatible only
import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="ZeroFox Digital Risk Protection",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(26, 26, 46, 0.3);
    }

    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff 0%, #f5f6fa 100%);
        border: 1px solid #dfe4ea;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: linear-gradient(90deg, #f5f6fa 0%, #dfe4ea 100%);
        padding: 0.75rem;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.75rem 1.25rem;
        background: white;
        border: 1px solid #dfe4ea;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #e94560 0%, #0f3460 100%);
        color: white;
        border: none;
    }

    h3 {
        color: #1a1a2e;
        border-bottom: 3px solid #e94560;
        padding-bottom: 0.75rem;
        margin-top: 2rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Get session
try:
    session = get_active_session()
except:
    st.error("❌ Could not establish Snowflake session. Please check your connection.")
    st.stop()

# Header
st.markdown("""
<div class="main-header">
    <h1 style="text-align: center; margin: 0;">
        ZeroFox Digital Risk Protection Platform
    </h1>
    <p style="text-align: center; margin: 0.75rem 0 0 0; opacity: 0.9;">
        External Threat Intelligence & Brand Protection Monitoring
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🔐 ZeroFox")
    st.markdown("Digital Risk Protection")
    st.markdown("---")

    # Filters
    st.header("🎯 Dashboard Filters")

    # OPCO filter
    opco_filter = st.multiselect(
        "OPCO Selection",
        ["All OPCOs", "Americas", "Europe", "APAC"],
        default=["All OPCOs"],
        help="Filter by operating company"
    )

    # Alert type filter
    alert_type_filter = st.multiselect(
        "Alert Types",
        ["All Types", "Impersonation", "Data Leakage", "Phishing", "Brand Abuse"],
        default=["All Types"],
        help="Filter by alert type"
    )

    # Date range
    date_range = st.selectbox(
        "Time Period",
        ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last 6 Months"],
        index=1,
        help="Select analysis time range"
    )

    # Severity filter
    severity_filter = st.multiselect(
        "Alert Severity",
        ["High", "Medium", "Low"],
        default=["High", "Medium", "Low"],
        help="Filter by alert severity"
    )

    st.markdown("---")

    # Refresh
    if st.button("🔄 Refresh Now", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()

# Data loading
@st.cache_data(ttl=300)
def load_data(query):
    try:
        df = session.sql(query).to_pandas()
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Helper function to safely execute queries
def safe_query(sql, error_msg="Error loading data"):
    try:
        return session.sql(sql).to_pandas()
    except Exception as e:
        st.error(f"{error_msg}: {str(e)}")
        return pd.DataFrame()

# Load data from views
st.markdown("### 📊 Loading Data...")

try:
    # Try to load data from views
    asset_exposure_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_ZEROFOX_ASSET_EXPOSURE ORDER BY ALERT_COUNT_90D DESC LIMIT 1000"
    domain_protection_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_ZEROFOX_DOMAIN_PROTECTION ORDER BY TOTAL_ALERTS DESC LIMIT 1000"

    df_asset_exposure = load_data(asset_exposure_query)
    df_domain_protection = load_data(domain_protection_query)

    # Calculate KPIs
    if not df_asset_exposure.empty:
        total_assets = len(df_asset_exposure)
        high_exposure_assets = len(df_asset_exposure[df_asset_exposure.get('EXPOSURE_LEVEL', '') == 'High'])
        total_alerts_90d = df_asset_exposure.get('ALERT_COUNT_90D', pd.Series([0])).sum()
        open_alerts = df_asset_exposure.get('OPEN_ALERTS', pd.Series([0])).sum()
    else:
        total_assets = high_exposure_assets = total_alerts_90d = open_alerts = 0

    if not df_domain_protection.empty:
        protected_domains = df_domain_protection.get('PROTECTED_DOMAIN', pd.Series([])).nunique()
        avg_removal_rate = df_domain_protection.get('REMOVAL_RATE', pd.Series([0])).mean()
        live_alerts = df_domain_protection.get('LIVE_ALERTS', pd.Series([0])).sum()
    else:
        protected_domains = live_alerts = 0
        avg_removal_rate = 0

except Exception as e:
    st.warning(f"Could not load some data views: {str(e)}")
    total_assets = high_exposure_assets = total_alerts_90d = open_alerts = 0
    protected_domains = live_alerts = 0
    avg_removal_rate = 0
    df_asset_exposure = pd.DataFrame()
    df_domain_protection = pd.DataFrame()

# KPIs
st.markdown("### 📊 Executive Summary")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("Protected Assets", f"{total_assets:,}")

with col2:
    st.metric("Alerts (90d)", f"{int(total_alerts_90d):,}" if total_alerts_90d else "0")

with col3:
    st.metric("Open Alerts", f"{int(open_alerts):,}" if open_alerts else "0")

with col4:
    st.metric("Domains", f"{protected_domains:,}")

with col5:
    st.metric("Removal Rate", f"{avg_removal_rate:.1f}%" if avg_removal_rate else "N/A")

with col6:
    st.metric("High Risk", f"{high_exposure_assets:,}")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Asset Exposure",
    "🌐 Domain Protection",
    "📈 Alert Trends",
    "👥 Threat Actors",
    "⚡ Response Performance"
])

# Tab 1: Asset Exposure
with tab1:
    st.markdown("### Asset Exposure Overview")

    if not df_asset_exposure.empty:
        # Metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Assets", f"{total_assets:,}")
        with col2:
            st.metric("High Risk Assets", f"{high_exposure_assets:,}")
        with col3:
            avg_alerts = total_alerts_90d / total_assets if total_assets > 0 else 0
            st.metric("Avg Alerts/Asset", f"{avg_alerts:.1f}")
        with col4:
            high_risk_pct = (high_exposure_assets/total_assets*100) if total_assets > 0 else 0
            st.metric("High Risk %", f"{high_risk_pct:.1f}%")

        # Show data table
        st.markdown("### Asset Details")

        # Select columns that exist
        available_cols = df_asset_exposure.columns.tolist()
        display_cols = [col for col in ['ASSET_NAME', 'OPCO', 'ASSET_TYPE', 'ALERT_COUNT_90D',
                                       'HIGH_SEVERITY_COUNT', 'OPEN_ALERTS', 'EXPOSURE_LEVEL']
                       if col in available_cols]

        if display_cols:
            st.dataframe(df_asset_exposure[display_cols].head(100), use_container_width=True)
        else:
            st.dataframe(df_asset_exposure.head(100), use_container_width=True)

        # Simple bar chart using Streamlit native
        if 'ASSET_NAME' in df_asset_exposure.columns and 'ALERT_COUNT_90D' in df_asset_exposure.columns:
            st.markdown("### Top 10 Assets by Alert Count")
            top_assets = df_asset_exposure.nlargest(10, 'ALERT_COUNT_90D')[['ASSET_NAME', 'ALERT_COUNT_90D']]
            st.bar_chart(top_assets.set_index('ASSET_NAME'))
    else:
        st.warning("No asset exposure data available. This could be because:")
        st.write("- The view `VW_GOLD_ZEROFOX_ASSET_EXPOSURE` is empty")
        st.write("- No data has been ingested yet")
        st.write("- There's an issue with data pipeline")

# Tab 2: Domain Protection
with tab2:
    st.markdown("### Domain Protection Status")

    if not df_domain_protection.empty:
        # Metrics
        col1, col2, col3, col4 = st.columns(4)

        total_domain_alerts = df_domain_protection.get('TOTAL_ALERTS', pd.Series([0])).sum()
        removed_alerts = df_domain_protection.get('REMOVED_ALERTS', pd.Series([0])).sum()

        with col1:
            st.metric("Protected Domains", f"{protected_domains:,}")
        with col2:
            st.metric("Total Alerts", f"{int(total_domain_alerts):,}")
        with col3:
            st.metric("Removed Alerts", f"{int(removed_alerts):,}")
        with col4:
            st.metric("Live Alerts", f"{int(live_alerts):,}")

        # Show data table
        st.markdown("### Domain Protection Details")

        # Select columns that exist
        available_cols = df_domain_protection.columns.tolist()
        display_cols = [col for col in ['OPCO', 'PROTECTED_DOMAIN', 'TOTAL_ALERTS',
                                       'REMOVED_ALERTS', 'LIVE_ALERTS', 'REMOVAL_RATE']
                       if col in available_cols]

        if display_cols:
            st.dataframe(df_domain_protection[display_cols].head(100), use_container_width=True)
        else:
            st.dataframe(df_domain_protection.head(100), use_container_width=True)
    else:
        st.warning("No domain protection data available")

# Tab 3: Alert Trends
with tab3:
    st.markdown("### Alert Trend Analysis")

    # Try to load alert trends
    try:
        alert_trends_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_ZEROFOX_ALERT_TRENDS ORDER BY ALERT_DATE DESC LIMIT 1000"
        df_alert_trends = load_data(alert_trends_query)

        if not df_alert_trends.empty:
            st.dataframe(df_alert_trends.head(100), use_container_width=True)
        else:
            st.info("Alert trends data is currently empty. This view depends on fact_zerofox_alerts table.")
    except:
        st.warning("Alert trends view not available or empty")

# Tab 4: Threat Actors
with tab4:
    st.markdown("### Threat Actor Intelligence")

    # Try to load threat actors
    try:
        threat_actors_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_ZEROFOX_THREAT_ACTORS ORDER BY ALERT_COUNT DESC LIMIT 1000"
        df_threat_actors = load_data(threat_actors_query)

        if not df_threat_actors.empty:
            st.dataframe(df_threat_actors.head(100), use_container_width=True)
        else:
            st.info("Threat actors data is currently empty. This view depends on fact_zerofox_alerts table.")
    except:
        st.warning("Threat actors view not available or empty")

# Tab 5: Response Performance
with tab5:
    st.markdown("### Response Performance Metrics")

    # Try to load response performance
    try:
        response_perf_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_ZEROFOX_RESPONSE_PERFORMANCE LIMIT 1000"
        df_response_perf = load_data(response_perf_query)

        if not df_response_perf.empty:
            st.dataframe(df_response_perf.head(100), use_container_width=True)
        else:
            st.info("Response performance data is currently empty. This view depends on fact_zerofox_alerts table.")
    except:
        st.warning("Response performance view not available or empty")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1rem;">
    <p><strong>ZeroFox Digital Risk Protection</strong> | External Threat Intelligence</p>
    <p>Group Information Security - Threat Intelligence Platform</p>
    <p style="font-size: 0.85rem;">© 2025 GenericCorp Corporation. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)