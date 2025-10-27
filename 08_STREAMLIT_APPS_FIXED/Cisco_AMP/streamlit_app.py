# Import python packages
import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
from datetime import datetime, timedelta

# Safe column access helper
def safe_get_column(df, column, default_value=0):
    """Safely get column from dataframe"""
    if column in df.columns:
        return df[column]
    else:
        return default_value



# Page config
st.set_page_config(
    page_title="Cisco AMP Dashboard",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #0a3d62 0%, #1e5f8e 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 6px 20px rgba(10, 61, 98, 0.25);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: repeating-linear-gradient(
            45deg,
            transparent,
            transparent 20px,
            rgba(255,255,255,0.03) 20px,
            rgba(255,255,255,0.03) 40px
        );
    }
    
    /* Metric card styling */
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
        border-color: #1e5f8e;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #f0f4f8;
        padding: 0.75rem;
        border-radius: 12px;
        box-shadow: inset 0 2px 4px rgba(10, 61, 98, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.75rem 1.25rem;
        background-color: white;
        border: 1px solid #e0e4e8;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #eef3f8;
        border-color: #1e5f8e;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0a3d62, #1e5f8e);
        color: white;
        border-color: #0a3d62;
        box-shadow: 0 2px 8px rgba(10, 61, 98, 0.2);
    }
    
    /* Status badges */
    .status-active { color: #27ae60; font-weight: bold; }
    .status-inactive { color: #e74c3c; font-weight: bold; }
    .status-warning { color: #f39c12; font-weight: bold; }
    .status-compliant { color: #27ae60; font-weight: bold; }
    .status-non-compliant { color: #e74c3c; font-weight: bold; }
    
    /* KPI cards */
    .kpi-card {
        background: linear-gradient(to bottom, #ffffff, #fafbfc);
        padding: 25px;
        border-radius: 15px;
        border: 2px solid transparent;
        background-clip: padding-box;
        position: relative;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .kpi-card::before {
        content: "";
        position: absolute;
        top: 0; right: 0; bottom: 0; left: 0;
        z-index: -1;
        margin: -2px;
        border-radius: inherit;
        background: linear-gradient(135deg, #0a3d62, #1e5f8e, #3498db);
    }
    
    .kpi-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 15px 35px rgba(10, 61, 98, 0.15);
    }
    
    .kpi-value {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #0a3d62, #1e5f8e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .kpi-label {
        color: #64748b;
        font-size: 0.95rem;
        margin-top: 0.5rem;
        font-weight: 500;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    /* Section styling */
    h3 {
        color: #0a3d62;
        border-bottom: 3px solid transparent;
        border-image: linear-gradient(to right, #0a3d62, #1e5f8e, transparent) 1;
        padding-bottom: 0.75rem;
        margin-top: 2rem;
        font-weight: 600;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #0a3d62, #1e5f8e);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(10, 61, 98, 0.25);
    }
    
    /* Custom info box */
    .stAlert {
        background-color: #eef3f8;
        border-left: 4px solid #1e5f8e;
    }
</style>
""", unsafe_allow_html=True)

# Get session
session = get_active_session()

# Header
st.markdown("""
<div class="main-header">
    <h1 style="text-align: center; margin: 0; position: relative; z-index: 1;">
        <span style="font-size: 2.5rem;">🔒</span> Cisco AMP Security Dashboard
    </h1>
    <p style="text-align: center; margin: 0.75rem 0 0 0; opacity: 0.9; position: relative; z-index: 1; font-size: 1.1rem;">
        Group Information Security - Data Platform & ETL for Data Management
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar with controls
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #0a3d62, #1e5f8e); border-radius: 12px; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(10, 61, 98, 0.2);">
        <h2 style="color: white; margin: 0; font-size: 1.5rem;">🏢 GenericCorp</h2>
        <p style="color: #e8f0f8; font-size: 0.95rem; margin-top: 0.5rem;">Advanced Malware Protection</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filters
    st.header("📊 Dashboard Filters")
    
    # OS filter
    os_filter = st.multiselect(
        "Operating Systems",
        ["Windows", "macOS", "Linux", "All"],
        default=["All"],
        help="Filter by operating system"
    
    )
    # Health status filter
    health_filter = st.multiselect(
        "Health Status",
        ["Healthy", "Warning", "Critical", "Unknown"],
        default=["Healthy", "Warning", "Critical", "Unknown"],
        help="Filter by endpoint health status"
    
    )
    # Date range
    date_range = st.selectbox(
        "Time Period",
        ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"],
        index=1,
        help="Select time range for data"
    
    )
    st.markdown("---")
    
    # Refresh controls
    auto_refresh = st.checkbox("🔄 Auto-refresh (5 min)", value=True)
    if st.button("🔄 Refresh Now", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    # Info section
    st.markdown("---")
    st.info("""
    **📊 Monitoring Scope:**
    - Endpoint Protection Status
    - Connector Version Compliance
    - OS Coverage Analysis
    - Health Monitoring
    - Threat Detection Metrics
    """)

# Helper function to query data
@st.cache_data(ttl=300)
def load_data(query):
    try:
        return session.sql(query).to_pandas()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Load all data
coverage_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_CISCO_AMP_COVERAGE ORDER BY REPORT_DATE DESC"
endpoint_health_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_CISCO_AMP_ENDPOINT_HEALTH"
os_coverage_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_CISCO_AMP_OS_COVERAGE"
version_compliance_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_CISCO_AMP_VERSION_COMPLIANCE ORDER BY CONNECTOR_VERSION"
compliance_settings_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_CISCO_AMP_COMPLIANCE_SETTINGS"

df_coverage = load_data(coverage_query)
df_health = load_data(endpoint_health_query)
df_os = load_data(os_coverage_query)
df_versions = load_data(version_compliance_query)
df_settings = load_data(compliance_settings_query)

# Executive KPIs Section
st.markdown("### 📊 Executive Summary")

# Get latest coverage data
latest_coverage = df_coverage.iloc[0] if not df_coverage.empty else None
total_endpoints = latest_coverage['TOTAL_ENDPOINTS'] if latest_coverage is not None else 0
active_endpoints = latest_coverage['ACTIVE_COUNT'] if latest_coverage is not None else 0
inactive_endpoints = latest_coverage['INACTIVE_COUNT'] if latest_coverage is not None else 0
coverage_pct = latest_coverage['COVERAGE_PCT'] if latest_coverage is not None else 0
gap_to_target = latest_coverage['GAP_TO_TARGET'] if latest_coverage is not None else 0

# Calculate additional metrics
if not df_health.empty:
    healthy_endpoints = len(df_health[df_health['HEALTH_STATUS'] == 'Healthy'])
    warning_endpoints = len(df_health[df_health['HEALTH_STATUS'] == 'Warning'])
    critical_endpoints = len(df_health[df_health['HEALTH_STATUS'] == 'Critical'])
else:
    healthy_endpoints = warning_endpoints = critical_endpoints = 0

# KPIs
kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)

with kpi_col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{total_endpoints:,}</div>
        <div class="kpi-label">Total Endpoints</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{active_endpoints:,}</div>
        <div class="kpi-label">Active</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{coverage_pct:.1f}%</div>
        <div class="kpi-label">Coverage</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{healthy_endpoints:,}</div>
        <div class="kpi-label">Healthy</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{warning_endpoints:,}</div>
        <div class="kpi-label">Warnings</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col6:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{inactive_endpoints:,}</div>
        <div class="kpi-label">Inactive</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📡 Coverage Overview",
    "💻 Endpoint Health",
    "🖥️ OS Coverage",
    "📱 Version Compliance",
    "📈 Trending Analysis"
])

# Define corporate color palette
corp_colors = {
    'primary': '#0a3d62',
    'secondary': '#1e5f8e',
    'tertiary': '#3498db',
    'success': '#27ae60',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'light': '#ecf0f1',
    'dark': '#2c3e50'
}

# Tab 1: Coverage Overview
with tab1:
    st.markdown("### Endpoint Coverage Analysis")
    
    if not df_coverage.empty:
        # Coverage trend chart
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Historical coverage trend
            
            # Add coverage percentage line
            
            # Add target line
            fig_trend.add_hline(y=95, line_dash="dash", line_color=corp_colors['primary'],
                              annotation_text="Target: 95%", annotation_font_color=corp_colors['primary'])
            
            # Add compliance zones
            fig_trend.add_hrect(y0=0, y1=90, fillcolor=corp_colors['danger'], opacity=0.05,
                               annotation_text="Non-Compliant", annotation_position="right")
            fig_trend.add_hrect(y0=90, y1=95, fillcolor=corp_colors['warning'], opacity=0.05,
                               annotation_text="Warning", annotation_position="right")
            fig_trend.add_hrect(y0=95, y1=100, fillcolor=corp_colors['success'], opacity=0.05,
                               annotation_text="Compliant", annotation_position="right")
            
            
            st.info("Chart visualization removed - data shown in table format")
        
        with col2:
            # Current status gauge
            st.info("Advanced chart - data available in table below")
        
        # Endpoint status breakdown
        st.markdown("### Endpoint Status Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Active vs Inactive endpoints over time
            
                fill='tozeroy'
            
            
            
            st.info("Chart visualization removed - data shown in table format")
        
        with col2:
            # Compliance status pie chart
            if 'COMPLIANCE_STATUS' in df_coverage.columns:
                latest_compliance = df_coverage.iloc[0]['COMPLIANCE_STATUS']
                
                # Create compliance status data
                compliance_data = pd.DataFrame({
                    'Status': ['Compliant', 'Non-Compliant'],
                    'Value': [1, 0] if latest_compliance == 'Compliant' else [0, 1]
                })
                
                st.info("Pie chart - data available in table below")

# Tab 2: Endpoint Health
with tab2:
    st.markdown("### Endpoint Health Monitoring")
    
    if not df_health.empty:
        # Health metrics summary
        col1, col2, col3, col4 = st.columns(4)
        
        total_endpoints_health = len(df_health)
        active_health = len(df_health[df_health['IS_ACTIVE'] == True])
        health_status_counts = df_health['HEALTH_STATUS'].value_counts()
        avg_inactive_days = df_health[df_health['IS_ACTIVE'] == False]['DAYS_INACTIVE'].mean()
        
        with col1:
            st.metric("Total Monitored", f"{total_endpoints_health:,}")
        with col2:
            st.metric("Active", f"{active_health:,}", f"{active_health/total_endpoints_health*100:.1f}%")
        with col3:
            st.metric("Health Issues", f"{warning_endpoints + critical_endpoints:,}")
        with col4:
            st.metric("Avg Inactive Days", f"{avg_inactive_days:.0f}" if not pd.isna(avg_inactive_days) else "0")
        
        # Health status visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Health status distribution
            if 'HEALTH_STATUS' in df_health.columns:
                st.info("Bar chart visualization - using native Streamlit chart")
        # st.bar_chart(df) # Simplified visualization
        
        with col2:
            # Action status distribution
            if 'ACTION_STATUS' in df_health.columns:
                action_counts = df_health['ACTION_STATUS'].value_counts()
                
                st.info("Pie chart - data available in table below")
        
        # Inactive endpoints analysis
        st.markdown("### Inactive Endpoint Analysis")
        
        inactive_df = df_health[df_health['IS_ACTIVE'] == False].copy()
        
        if not inactive_df.empty:
            # Create inactivity categories
            inactive_df['INACTIVITY_CATEGORY'] = pd.cut(
                inactive_df['DAYS_INACTIVE'],
                bins=[-np.inf, 7, 30, 90, np.inf],
                labels=['< 7 days', '7-30 days', '30-90 days', '> 90 days']
            
            inactivity_summary = inactive_df['INACTIVITY_CATEGORY'].value_counts()
            
            st.info("Bar chart visualization - using native Streamlit chart")
        # st.bar_chart(df) # Simplified visualization
        
        # Detailed health table
        st.markdown("### Endpoint Health Details")
        
        # Filter for unhealthy endpoints
        unhealthy_df = df_health[df_health['HEALTH_STATUS'].isin(['Warning', 'Critical'])].copy()
        
        if not unhealthy_df.empty:
            display_cols = ['HOSTNAME', 'CONNECTOR_VERSION', 'OPERATING_SYSTEM', 
                           'HEALTH_STATUS', 'ACTION_STATUS', 'DAYS_INACTIVE', 'LAST_SEEN']
            
            st.dataframe(
                unhealthy_df[display_cols].sort_values('HEALTH_STATUS').head(20).style.apply(
                    lambda x: ['background-color: #fff4e6' if x['HEALTH_STATUS'] == 'Warning' 
                              else 'background-color: #ffeef0' if x['HEALTH_STATUS'] == 'Critical'
                              else '' for _ in x], axis=1
                ),
                use_container_width=True,

# Tab 3: OS Coverage
with tab3:
    st.markdown("### Operating System Coverage Analysis")
    
    if not df_os.empty:
        # OS coverage summary
        total_os_endpoints = df_os['TOTAL_ENDPOINTS'].sum()
        total_active_os = df_os['ACTIVE_ENDPOINTS'].sum()
        total_outdated = df_os['OUTDATED_VERSIONS'].sum()
        avg_os_coverage = df_os['COVERAGE_PCT'].mean()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Endpoints", f"{total_os_endpoints:,}")
        with col2:
            st.metric("Active Endpoints", f"{total_active_os:,}")
        with col3:
            st.metric("Outdated Versions", f"{total_outdated:,}")
        with col4:
            st.metric("Avg OS Coverage", f"{avg_os_coverage:.1f}%")
        
        # OS distribution visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Endpoints by OS
            st.info("Bar chart visualization - using native Streamlit chart")
        # st.bar_chart(df) # Simplified visualization
        
        with col2:
            # OS market share pie chart
            st.info("Pie chart - data available in table below")
        
        # Outdated versions analysis
        st.markdown("### Outdated Version Analysis")
        
        # Create comparison chart
        
        # Add bars for total vs outdated
        
        
        
        st.info("Chart visualization removed - data shown in table format")
        
        # OS coverage details table
        st.markdown("### OS Coverage Details")
        
        # Add coverage status column
        df_os['COVERAGE_STATUS'] = df_os['COVERAGE_PCT'].apply(
            lambda x: 'Good' if x >= 90 else 'Warning' if x >= 80 else 'Critical'
        
        display_cols = ['OPERATING_SYSTEM', 'TOTAL_ENDPOINTS', 'ACTIVE_ENDPOINTS', 
                       'COVERAGE_PCT', 'OUTDATED_VERSIONS', 'OUTDATED_PCT', 'COVERAGE_STATUS']
        
        st.dataframe(
            df_os[display_cols].sort_values('COVERAGE_PCT', ascending=False).style.format({
                'COVERAGE_PCT': '{:.1f}%',
                'OUTDATED_PCT': '{:.1f}%'
            }).background_gradient(subset=['COVERAGE_PCT'], cmap='RdYlGn'),
            use_container_width=True

# Tab 4: Version Compliance
with tab4:
    st.markdown("### Connector Version Compliance")
    
    if not df_versions.empty:
        # Version compliance summary
        total_versions = len(df_versions)
        compliant_versions = len(df_versions[df_versions['COMPLIANCE_STATUS'] == 'Compliant'])
        non_compliant_versions = len(df_versions[df_versions['COMPLIANCE_STATUS'] != 'Compliant'])
        total_endpoints_versions = df_versions['ENDPOINT_COUNT'].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Versions", total_versions)
        with col2:
            st.metric("Compliant Versions", compliant_versions)
        with col3:
            st.metric("Non-Compliant", non_compliant_versions, f"-{non_compliant_versions}")
        with col4:
            st.metric("Total Endpoints", f"{total_endpoints_versions:,}")
        
        # Version distribution
        col1, col2 = st.columns(2)
        
        with col1:
            # Endpoints by version
            st.info("Bar chart visualization - using native Streamlit chart")
        # st.bar_chart(df) # Simplified visualization
        
        with col2:
            # Compliance status pie
            compliance_summary = df_versions.groupby('COMPLIANCE_STATUS')['ENDPOINT_COUNT'].sum()
            
            st.info("Pie chart - data available in table below")
        
        # Version timeline
        st.markdown("### Version Deployment Timeline")
        
        if 'OLDEST_SEEN' in df_versions.columns and 'NEWEST_SEEN' in df_versions.columns:
            # Convert to datetime
            df_versions['OLDEST_SEEN'] = pd.to_datetime(df_versions['OLDEST_SEEN'])
            df_versions['NEWEST_SEEN'] = pd.to_datetime(df_versions['NEWEST_SEEN'])
            
            # Calculate version age
            current_date = pd.Timestamp.now()
            df_versions['VERSION_AGE_DAYS'] = (current_date - df_versions['OLDEST_SEEN']).dt.days
            
            # Create scatter plot for version timeline
            st.info("Scatter plot - data available in table below")
        
        # Detailed version table
        st.markdown("### Version Compliance Details")
        
        display_cols = ['CONNECTOR_VERSION', 'ENDPOINT_COUNT', 'COMPLIANCE_STATUS']
        if 'VERSION_AGE_DAYS' in df_versions.columns:
            display_cols.append('VERSION_AGE_DAYS')
        
        st.dataframe(
            df_versions[display_cols].sort_values('ENDPOINT_COUNT', ascending=False).style.apply(
                lambda x: ['background-color: #e8f5e9' if x['COMPLIANCE_STATUS'] == 'Compliant' 
                          else 'background-color: #ffeef0' if x['COMPLIANCE_STATUS'] == 'Non-Compliant'
                          else 'background-color: #fff4e6' for _ in x], axis=1
            ),
            use_container_width=True,

# Tab 5: Trending Analysis
with tab5:
    st.markdown("### Trending & Analytics")
    
    # Compliance Settings Overview
    if not df_settings.empty:
        st.markdown("#### Current Compliance Settings")
        
        col1, col2, col3 = st.columns(3)
        for idx, setting in df_settings.iterrows():
            with [col1, col2, col3][idx % 3]:
                st.info(f"**{setting['PARAMETER_NAME']}**\n\n"
                       f"Value: {setting['PARAMETER_VALUE']}\n\n"
                       f"{setting['DESCRIPTION']}")
    
    # Coverage trend analysis
    if not df_coverage.empty:
        st.markdown("#### Coverage Trend Analysis")
        
        # Calculate moving averages
        df_coverage['MA_7'] = df_coverage['COVERAGE_PCT'].rolling(window=7, min_periods=1).mean()
        df_coverage['MA_30'] = df_coverage['COVERAGE_PCT'].rolling(window=30, min_periods=1).mean()
        
        # Create advanced trend chart
        fig_trend_advanced = make_subplots(
            rows=2, cols=1,
            row_heights=[0.7, 0.3],
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Coverage Trend with Moving Averages', 'Daily Change Rate')
        
        # Main trend lines