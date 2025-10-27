# Import python packages
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt
from snowflake.snowpark.context import get_active_session
from datetime import datetime, timedelta
import numpy as np

# Page config
st.set_page_config(
    page_title="CrowdStrike EDR Dashboard",
    page_icon="🛡️",
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
        background: url('data:image/svg+xml;utf8,<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><line x1="0" y1="0" x2="100" y2="100" stroke="rgba(255,255,255,0.05)" stroke-width="0.5"/><line x1="0" y1="25" x2="75" y2="100" stroke="rgba(255,255,255,0.05)" stroke-width="0.5"/><line x1="25" y1="0" x2="100" y2="75" stroke="rgba(255,255,255,0.05)" stroke-width="0.5"/></svg>');
        background-size: 100px 100px;
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
    
    /* Risk level badges - Corporate color variations */
    .risk-critical { color: #c0392b; font-weight: bold; }
    .risk-high { color: #e67e22; font-weight: bold; }
    .risk-medium { color: #f39c12; font-weight: bold; }
    .risk-low { color: #3498db; font-weight: bold; }
    
    /* Status badges */
    .status-active { color: #27ae60; font-weight: bold; }
    .status-inactive { color: #e74c3c; font-weight: bold; }
    .status-eol { color: #e67e22; font-weight: bold; }
    
    /* KPI cards with gradient borders */
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
        transform: translateY(-5px);
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
        <span style="font-size: 2.5rem;">✅</span> CrowdStrike EDR Dashboard
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
        <p style="color: #e8f0f8; font-size: 0.95rem; margin-top: 0.5rem;">Enterprise Security Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filters
    st.header("📊 Dashboard Filters")
    
    # Platform filter
    platform_filter = st.multiselect(
        "Platform",
        ["Windows", "Mac", "Linux", "All"],
        default=["All"],
        help="Select platforms to filter"
    )
    
    # Risk category filter
    risk_filter = st.multiselect(
        "Risk Categories",
        ["Critical", "High Risk", "EOL Version", "Inactive", "Compliant"],
        default=["Critical", "High Risk", "EOL Version", "Inactive", "Compliant"],
        help="Select risk categories to display"
    )
    
    # Date range
    date_range = st.selectbox(
        "Time Period",
        ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 90 Days"],
        index=2,
        help="Select time range for data"
    )
    
    st.markdown("---")
    
    # Refresh controls
    auto_refresh = st.checkbox("🔄 Auto-refresh (2 min)", value=True)
    if st.button("🔄 Refresh Now", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    # Info section
    st.markdown("---")
    st.info("""
    **📊 Monitoring Coverage:**
    - Endpoint Protection
    - Version Compliance
    - User Activity Analysis
    - Risk Assessment
    - Cloud Environment
    """)

# Helper function to query data
@st.cache_data(ttl=120)
def load_data(query):
    try:
        return session.sql(query).to_pandas()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Load all data
coverage_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_CROWDSTRIKE_COVERAGE ORDER BY REPORT_DATE DESC"
cloud_coverage_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_CROWDSTRIKE_CLOUD_COVERAGE"
endpoint_risk_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_CROWDSTRIKE_ENDPOINT_RISK"
user_activity_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_CROWDSTRIKE_USER_ACTIVITY"
version_compliance_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_CROWDSTRIKE_VERSION_COMPLIANCE ORDER BY DAYS_UNTIL_EOL"
compliance_settings_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_CROWDSTRIKE_COMPLIANCE_SETTINGS"

df_coverage = load_data(coverage_query)
df_cloud = load_data(cloud_coverage_query)
df_risk = load_data(endpoint_risk_query)
df_users = load_data(user_activity_query)
df_versions = load_data(version_compliance_query)
df_settings = load_data(compliance_settings_query)

# Executive KPIs Section
st.markdown("### 📊 Executive Summary")

# Get latest coverage data
latest_coverage = df_coverage.iloc[0] if not df_coverage.empty else None
total_endpoints = latest_coverage['TOTAL_ENDPOINTS'] if latest_coverage is not None else 0
active_endpoints = latest_coverage['ACTIVE_COUNT'] if latest_coverage is not None else 0
coverage_pct = latest_coverage['COVERAGE_PCT'] if latest_coverage is not None else 0
gap_to_target = latest_coverage['GAP_TO_TARGET'] if latest_coverage is not None else 0

# Calculate additional metrics
if not df_risk.empty:
    eol_endpoints = len(df_risk[df_risk['RISK_CATEGORY'].str.contains('EOL', case=False, na=False)])
    inactive_endpoints = len(df_risk[df_risk['IS_ACTIVE'] == False])
    critical_risk = len(df_risk[df_risk['RISK_CATEGORY'] == 'Critical'])
else:
    eol_endpoints = inactive_endpoints = critical_risk = 0

# Display KPIs with custom styling
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
        <div class="kpi-label">Active Endpoints</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{coverage_pct:.1f}%</div>
        <div class="kpi-label">Coverage Rate</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    gap_display = f"{abs(gap_to_target):.1f}%" if gap_to_target != 0 else "On Target"
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{gap_display}</div>
        <div class="kpi-label">Gap to 95% Target</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{eol_endpoints:,}</div>
        <div class="kpi-label">EOL Versions</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col6:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{critical_risk:,}</div>
        <div class="kpi-label">Critical Risk</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📡 Coverage Overview",
    "🖥️ Endpoint Risk",
    "📱 Version Compliance", 
    "👥 User Activity",
    "☁️ Cloud Coverage",
    "📈 Trending Analysis"
])

# Define color palette
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
            fig_trend = go.Figure()
            
            # Add coverage percentage line
            fig_trend.add_trace(go.Scatter(
                x=df_coverage['REPORT_DATE'],
                y=df_coverage['COVERAGE_PCT'],
                mode='lines+markers',
                name='Coverage %',
                line=dict(color=corp_colors['secondary'], width=3),
                marker=dict(size=8, color=corp_colors['primary'])
            ))
            
            # Add target line
            fig_trend.add_hline(y=95, line_dash="dash", line_color=corp_colors['primary'],
                              annotation_text="Target: 95%", annotation_font_color=corp_colors['primary'])
            
            # Add compliance status color zones
            fig_trend.add_hrect(y0=0, y1=90, fillcolor=corp_colors['danger'], opacity=0.05)
            fig_trend.add_hrect(y0=90, y1=95, fillcolor=corp_colors['warning'], opacity=0.05)
            fig_trend.add_hrect(y0=95, y1=100, fillcolor=corp_colors['success'], opacity=0.05)
            
            fig_trend.update_layout(
                title='Coverage Percentage Trend',
                xaxis_title='Date',
                yaxis_title='Coverage %',
                yaxis_range=[80, 100],
                height=400,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            # Current status gauge
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = coverage_pct,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Current Coverage", 'font': {'color': corp_colors['primary']}},
                delta = {'reference': 95, 'position': "bottom", 'font': {'color': corp_colors['dark']}},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': corp_colors['secondary'] if coverage_pct >= 95 else corp_colors['warning'] if coverage_pct >= 90 else corp_colors['danger']},
                    'steps': [
                        {'range': [0, 90], 'color': corp_colors['light']},
                        {'range': [90, 95], 'color': '#dfe6e9'}
                    ],
                    'threshold': {
                        'line': {'color': corp_colors['primary'], 'width': 4},
                        'thickness': 0.75,
                        'value': 95
                    }
                }
            ))
            
            fig_gauge.update_layout(
                height=400,
                paper_bgcolor='white'
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Endpoint distribution
        st.markdown("### Endpoint Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Active vs Total endpoints over time
            fig_endpoints = go.Figure()
            
            fig_endpoints.add_trace(go.Bar(
                x=df_coverage['REPORT_DATE'],
                y=df_coverage['TOTAL_ENDPOINTS'],
                name='Total Endpoints',
                marker_color=corp_colors['dark']
            ))
            
            fig_endpoints.add_trace(go.Bar(
                x=df_coverage['REPORT_DATE'],
                y=df_coverage['ACTIVE_COUNT'],
                name='Active Endpoints',
                marker_color=corp_colors['secondary']
            ))
            
            fig_endpoints.update_layout(
                title='Total vs Active Endpoints',
                xaxis_title='Date',
                yaxis_title='Count',
                barmode='overlay',
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig_endpoints, use_container_width=True)
        
        with col2:
            # Compliance status distribution
            compliance_counts = df_coverage['COMPLIANCE_STATUS'].value_counts()
            
            fig_compliance = px.pie(
                values=compliance_counts.values,
                names=compliance_counts.index,
                title='Compliance Status Distribution',
                color_discrete_map={
                    'Compliant': corp_colors['success'],
                    'Warning': corp_colors['warning'],
                    'Non-Compliant': corp_colors['danger']
                }
            )
            
            fig_compliance.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            st.plotly_chart(fig_compliance, use_container_width=True)

# Tab 2: Endpoint Risk
with tab2:
    st.markdown("### Endpoint Risk Assessment")
    
    if not df_risk.empty:
        # Risk summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_endpoints_risk = len(df_risk)
        active_count = len(df_risk[df_risk['IS_ACTIVE'] == True])
        risk_categories = df_risk['RISK_CATEGORY'].value_counts()
        platforms = df_risk['PLATFORM'].value_counts()
        
        with col1:
            st.metric("Total Endpoints", f"{total_endpoints_risk:,}")
        with col2:
            st.metric("Active", f"{active_count:,}", f"{active_count/total_endpoints_risk*100:.1f}%")
        with col3:
            high_risk_count = len(df_risk[df_risk['RISK_CATEGORY'].isin(['Critical', 'High Risk'])])
            st.metric("High Risk", f"{high_risk_count:,}")
        with col4:
            avg_inactive_days = df_risk[df_risk['IS_ACTIVE'] == False]['DAYS_INACTIVE'].mean()
            st.metric("Avg Inactive Days", f"{avg_inactive_days:.0f}" if not pd.isna(avg_inactive_days) else "N/A")
        
        # Risk distribution visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk category distribution
            fig_risk_dist = px.bar(
                x=risk_categories.index,
                y=risk_categories.values,
                title='Endpoints by Risk Category',
                labels={'x': 'Risk Category', 'y': 'Count'},
                color=risk_categories.index,
                color_discrete_map={
                    'Critical': corp_colors['danger'],
                    'High Risk': '#e67e22',
                    'EOL Version': corp_colors['warning'],
                    'Inactive': corp_colors['dark'],
                    'Compliant': corp_colors['success']
                }
            )
            
            fig_risk_dist.update_layout(
                plot_bgcolor='white',
                showlegend=False
            )
            
            st.plotly_chart(fig_risk_dist, use_container_width=True)
        
        with col2:
            # Platform distribution
            fig_platform = px.pie(
                values=platforms.values,
                names=platforms.index,
                title='Endpoints by Platform',
                color_discrete_map={
                    'Windows': '#0078d4',
                    'Mac': '#555555',
                    'Linux': '#ff9500'
                }
            )
            
            fig_platform.update_layout(
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig_platform, use_container_width=True)
        
        # EOL Risk Analysis
        st.markdown("### End-of-Life (EOL) Risk Analysis")
        
        # Filter for EOL risks
        eol_risks = df_risk[df_risk['DAYS_UNTIL_EOL'].notna()].copy()
        
        if not eol_risks.empty:
            # Create EOL urgency categories
            eol_risks['EOL_URGENCY'] = pd.cut(
                eol_risks['DAYS_UNTIL_EOL'],
                bins=[-np.inf, 0, 30, 90, 180, np.inf],
                labels=['Already EOL', '< 30 days', '30-90 days', '90-180 days', '> 180 days']
            )
            
            eol_summary = eol_risks['EOL_URGENCY'].value_counts()
            
            fig_eol = px.bar(
                x=eol_summary.index,
                y=eol_summary.values,
                title='Endpoints by EOL Timeline',
                labels={'x': 'Time to EOL', 'y': 'Count'},
                color=eol_summary.index,
                color_discrete_map={
                    'Already EOL': corp_colors['danger'],
                    '< 30 days': '#e67e22',
                    '30-90 days': corp_colors['warning'],
                    '90-180 days': '#f4d03f',
                    '> 180 days': corp_colors['success']
                }
            )
            
            fig_eol.update_layout(
                plot_bgcolor='white',
                showlegend=False
            )
            
            st.plotly_chart(fig_eol, use_container_width=True)
        
        # Detailed risk table
        st.markdown("### High Risk Endpoints")
        
        high_risk_endpoints = df_risk[df_risk['RISK_CATEGORY'].isin(['Critical', 'High Risk', 'EOL Version'])].copy()
        
        if not high_risk_endpoints.empty:
            display_cols = ['HOSTNAME', 'PLATFORM', 'OS_PRODUCT_NAME', 'SENSOR_VERSION', 
                           'DAYS_UNTIL_EOL', 'DAYS_INACTIVE', 'RISK_CATEGORY', 'REMEDIATION_STATUS']
            
            st.dataframe(
                high_risk_endpoints[display_cols].sort_values('RISK_CATEGORY').head(20).style.apply(
                    lambda x: ['background-color: #ffeef0' if x['RISK_CATEGORY'] == 'Critical' 
                              else 'background-color: #fff4e6' if x['RISK_CATEGORY'] == 'High Risk'
                              else 'background-color: #fffbf0' if x['RISK_CATEGORY'] == 'EOL Version'
                              else '' for _ in x], axis=1
                ),
                use_container_width=True,
                height=400
            )

# Tab 3: Version Compliance
with tab3:
    st.markdown("### Sensor Version Compliance")
    
    if not df_versions.empty:
        # Version compliance overview
        total_versions = len(df_versions)
        supported_versions = len(df_versions[df_versions['SUPPORT_STATUS'] == 'Supported'])
        eol_versions = len(df_versions[df_versions['SUPPORT_STATUS'] != 'Supported'])
        total_endpoints_on_versions = df_versions['ENDPOINT_COUNT'].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Versions", total_versions)
        with col2:
            st.metric("Supported Versions", supported_versions)
        with col3:
            st.metric("EOL Versions", eol_versions, f"-{eol_versions}")
        with col4:
            st.metric("Total Endpoints", f"{total_endpoints_on_versions:,}")
        
        # Version distribution
        col1, col2 = st.columns(2)
        
        with col1:
            # Endpoints by version
            fig_version_dist = px.bar(
                df_versions.sort_values('ENDPOINT_COUNT', ascending=True),
                x='ENDPOINT_COUNT',
                y='VERSION',
                orientation='h',
                title='Endpoints by Sensor Version',
                color='SUPPORT_STATUS',
                color_discrete_map={
                    'Supported': corp_colors['success'],
                    'EOL Soon': corp_colors['warning'],
                    'EOL': corp_colors['danger']
                }
            )
            
            fig_version_dist.update_layout(
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig_version_dist, use_container_width=True)
        
        with col2:
            # Support status pie chart
            support_summary = df_versions.groupby('SUPPORT_STATUS')['ENDPOINT_COUNT'].sum()
            
            fig_support = px.pie(
                values=support_summary.values,
                names=support_summary.index,
                title='Endpoints by Support Status',
                color_discrete_map={
                    'Supported': corp_colors['success'],
                    'EOL Soon': corp_colors['warning'],
                    'EOL': corp_colors['danger']
                }
            )
            
            fig_support.update_layout(
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig_support, use_container_width=True)
        
        # Version timeline visualization
        st.markdown("### Version Support Timeline")
        
        # Prepare timeline data
        timeline_data = df_versions.copy()
        timeline_data['DAYS_UNTIL_EOL'] = timeline_data['DAYS_UNTIL_EOL'].fillna(365)  # Assume 1 year for null values
        
        fig_timeline = px.scatter(
            timeline_data,
            x='DAYS_UNTIL_EOL',
            y='VERSION',
            size='ENDPOINT_COUNT',
            color='COMPLIANCE_STATUS',
            title='Version Support Timeline',
            labels={'DAYS_UNTIL_EOL': 'Days Until End of Support', 'VERSION': 'Sensor Version'},
            color_discrete_map={
                'Compliant': corp_colors['success'],
                'Warning': corp_colors['warning'],
                'Non-Compliant': corp_colors['danger']
            }
        )
        
        # Add vertical line for current date
        fig_timeline.add_vline(x=0, line_dash="dash", line_color=corp_colors['primary'],
                             annotation_text="EOL", annotation_font_color=corp_colors['primary'])
        
        fig_timeline.update_layout(
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Detailed version table
        st.markdown("### Version Details")
        
        display_cols = ['VERSION', 'SUPPORT_DATE', 'DAYS_UNTIL_EOL', 'ENDPOINT_COUNT', 
                       'SUPPORT_STATUS', 'COMPLIANCE_STATUS']
        
        st.dataframe(
            df_versions[display_cols].style.apply(
                lambda x: ['background-color: #ffeef0' if x['SUPPORT_STATUS'] == 'EOL' 
                          else 'background-color: #fff4e6' if x['DAYS_UNTIL_EOL'] < 90
                          else '' for _ in x], axis=1
            ),
            use_container_width=True
        )

# Tab 4: User Activity
with tab4:
    st.markdown("### User Activity Monitoring")
    
    if not df_users.empty:
        # User activity metrics
        total_hosts_with_users = len(df_users)
        active_users = len(df_users[df_users['DAYS_SINCE_LOGIN'] <= 7])
        inactive_users = len(df_users[df_users['DAYS_SINCE_LOGIN'] > 30])
        avg_days_since_login = df_users['DAYS_SINCE_LOGIN'].mean()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Hosts with User Data", f"{total_hosts_with_users:,}")
        with col2:
            st.metric("Active (≤7 days)", f"{active_users:,}")
        with col3:
            st.metric("Inactive (>30 days)", f"{inactive_users:,}")
        with col4:
            st.metric("Avg Days Since Login", f"{avg_days_since_login:.0f}")
        
        # Activity distribution
        col1, col2 = st.columns(2)
        
        with col1:
            # Create activity categories
            df_users['ACTIVITY_STATUS'] = pd.cut(
                df_users['DAYS_SINCE_LOGIN'],
                bins=[-np.inf, 7, 30, 90, np.inf],
                labels=['Active (≤7d)', 'Recent (7-30d)', 'Inactive (30-90d)', 'Very Inactive (>90d)']
            )
            
            activity_dist = df_users['ACTIVITY_STATUS'].value_counts()
            
            fig_activity = px.pie(
                values=activity_dist.values,
                names=activity_dist.index,
                title='User Activity Distribution',
                color_discrete_map={
                    'Active (≤7d)': corp_colors['success'],
                    'Recent (7-30d)': corp_colors['secondary'],
                    'Inactive (30-90d)': corp_colors['warning'],
                    'Very Inactive (>90d)': corp_colors['danger']
                }
            )
            
            fig_activity.update_layout(
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig_activity, use_container_width=True)
        
        with col2:
            # Account status distribution
            account_status_dist = df_users['ACCOUNT_STATUS'].value_counts()
            
            fig_account = px.bar(
                x=account_status_dist.index,
                y=account_status_dist.values,
                title='Account Status Distribution',
                labels={'x': 'Account Status', 'y': 'Count'},
                color=account_status_dist.index,
                color_discrete_sequence=[corp_colors['primary'], corp_colors['secondary'], corp_colors['tertiary']]
            )
            
            fig_account.update_layout(
                plot_bgcolor='white',
                showlegend=False
            )
            
            st.plotly_chart(fig_account, use_container_width=True)
        
        # User activity by OS
        st.markdown("### Activity by Operating System")
        
        os_activity = df_users.groupby('OS_PRODUCT_NAME')['DAYS_SINCE_LOGIN'].agg(['mean', 'count'])
        os_activity = os_activity.reset_index()
        os_activity.columns = ['OS', 'Avg Days Since Login', 'Host Count']
        
        fig_os_activity = px.scatter(
            os_activity,
            x='Avg Days Since Login',
            y='OS',
            size='Host Count',
            color='Avg Days Since Login',
            title='Average User Activity by OS',
            color_continuous_scale=[corp_colors['success'], corp_colors['warning'], corp_colors['danger']]
        )
        
        fig_os_activity.update_layout(
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig_os_activity, use_container_width=True)
        
        # Inactive hosts table
        st.markdown("### Inactive Hosts (>30 days)")
        
        inactive_hosts = df_users[df_users['DAYS_SINCE_LOGIN'] > 30].sort_values('DAYS_SINCE_LOGIN', ascending=False)
        
        if not inactive_hosts.empty:
            display_cols = ['HOSTNAME', 'LAST_LOGGED_IN_USER', 'LAST_USER_LOGIN', 
                           'DAYS_SINCE_LOGIN', 'ACCOUNT_STATUS', 'OS_PRODUCT_NAME']
            
            st.dataframe(
                inactive_hosts[display_cols].head(20),
                use_container_width=True,
                height=400
            )

# Tab 5: Cloud Coverage
with tab5:
    st.markdown("### Cloud Environment Coverage")
    
    if not df_cloud.empty:
        # Cloud metrics overview
        total_cloud_endpoints = df_cloud['TOTAL_ENDPOINTS'].sum()
        total_active_cloud = df_cloud['ACTIVE_ENDPOINTS'].sum()
        total_eol_cloud = df_cloud['EOL_VERSIONS'].sum()
        avg_cloud_coverage = df_cloud['COVERAGE_PCT'].mean()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Cloud Endpoints", f"{total_cloud_endpoints:,}")
        with col2:
            st.metric("Active Cloud Endpoints", f"{total_active_cloud:,}")
        with col3:
            st.metric("EOL Versions", f"{total_eol_cloud:,}")
        with col4:
            st.metric("Avg Cloud Coverage", f"{avg_cloud_coverage:.1f}%")
        
        # Environment comparison
        col1, col2 = st.columns(2)
        
        with col1:
            # Environment metrics comparison
            fig_env_compare = go.Figure()
            
            # Add bars for each metric
            metrics = ['TOTAL_ENDPOINTS', 'ACTIVE_ENDPOINTS', 'EOL_VERSIONS']
            
            for idx, env in df_cloud.iterrows():
                fig_env_compare.add_trace(go.Bar(
                    name=env['ENVIRONMENT'],
                    x=metrics,
                    y=[env['TOTAL_ENDPOINTS'], env['ACTIVE_ENDPOINTS'], env['EOL_VERSIONS']],
                    text=[env['TOTAL_ENDPOINTS'], env['ACTIVE_ENDPOINTS'], env['EOL_VERSIONS']],
                    textposition='auto',
                    marker_color=corp_colors['primary'] if idx == 0 else corp_colors['secondary']
                ))
            
            fig_env_compare.update_layout(
                title='Cloud Environment Comparison',
                xaxis_title='Metric',
                yaxis_title='Count',
                barmode='group',
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig_env_compare, use_container_width=True)
        
        with col2:
            # Coverage percentage by environment
            fig_coverage = px.bar(
                df_cloud,
                x='ENVIRONMENT',
                y='COVERAGE_PCT',
                title='Coverage by Environment',
                color='COVERAGE_PCT',
                color_continuous_scale=[corp_colors['danger'], corp_colors['warning'], corp_colors['success']],
                text='COVERAGE_PCT'
            )
            
            fig_coverage.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_coverage.add_hline(y=95, line_dash="dash", line_color=corp_colors['primary'],
                                 annotation_text="Target: 95%", annotation_font_color=corp_colors['primary'])
            
            fig_coverage.update_layout(
                plot_bgcolor='white',
                showlegend=False
            )
            
            st.plotly_chart(fig_coverage, use_container_width=True)
        
        # EOL analysis
        st.markdown("### EOL Version Analysis by Environment")
        
        # Calculate EOL percentage impact
        df_cloud['EOL_IMPACT'] = (df_cloud['EOL_VERSIONS'] / df_cloud['TOTAL_ENDPOINTS'] * 100).round(1)
        
        fig_eol_impact = go.Figure()
        
        fig_eol_impact.add_trace(go.Bar(
            x=df_cloud['ENVIRONMENT'],
            y=df_cloud['EOL_PCT'],
            name='EOL Percentage',
            marker_color=corp_colors['warning'],
            yaxis='y',
            offsetgroup=1
        ))
        
        fig_eol_impact.add_trace(go.Bar(
            x=df_cloud['ENVIRONMENT'],
            y=df_cloud['EOL_VERSIONS'],
            name='EOL Count',
            marker_color=corp_colors['danger'],
            yaxis='y2',
            offsetgroup=2
        ))
        
        fig_eol_impact.update_layout(
            title='EOL Version Impact by Environment',
            xaxis=dict(title='Environment'),
            yaxis=dict(title='EOL Percentage (%)', side='left'),
            yaxis2=dict(title='EOL Version Count', side='right', overlaying='y'),
            barmode='group',
            bargap=0.15,
            bargroupgap=0.1,
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig_eol_impact, use_container_width=True)

# Tab 6: Trending Analysis
with tab6:
    st.markdown("### Trending & Analytics")
    
    # Compliance Settings Overview
    if not df_settings.empty:
        st.markdown("#### Current Compliance Settings")
        
        settings_display = df_settings[['PARAMETER_NAME', 'PARAMETER_VALUE', 'DESCRIPTION']]
        
        col1, col2, col3, col4 = st.columns(4)
        for idx, setting in df_settings.iterrows():
            if idx < 4:
                with [col1, col2, col3, col4][idx]:
                    st.metric(
                        setting['PARAMETER_NAME'],
                        f"{setting['PARAMETER_VALUE']}%",
                        help=setting['DESCRIPTION']
                    )
    
    # Coverage trend analysis
    if not df_coverage.empty:
        st.markdown("#### Coverage Trend Analysis")
        
        # Calculate moving averages
        df_coverage['MA_7'] = df_coverage['COVERAGE_PCT'].rolling(window=7, min_periods=1).mean()
        df_coverage['MA_30'] = df_coverage['COVERAGE_PCT'].rolling(window=30, min_periods=1).mean()
        
        fig_trend_ma = go.Figure()
        
        # Actual coverage
        fig_trend_ma.add_trace(go.Scatter(
            x=df_coverage['REPORT_DATE'],
            y=df_coverage['COVERAGE_PCT'],
            mode='lines',
            name='Daily Coverage',
            line=dict(color=corp_colors['light'], width=1),
            opacity=0.6
        ))
        
        # 7-day MA
        fig_trend_ma.add_trace(go.Scatter(
            x=df_coverage['REPORT_DATE'],
            y=df_coverage['MA_7'],
            mode='lines',
            name='7-Day Average',
            line=dict(color=corp_colors['tertiary'], width=2)
        ))
        
        # 30-day MA
        fig_trend_ma.add_trace(go.Scatter(
            x=df_coverage['REPORT_DATE'],
            y=df_coverage['MA_30'],
            mode='lines',
            name='30-Day Average',
            line=dict(color=corp_colors['primary'], width=3)
        ))
        
        # Target line
        fig_trend_ma.add_hline(y=95, line_dash="dash", line_color=corp_colors['primary'],
                              annotation_text="Target: 95%", annotation_font_color=corp_colors['primary'])
        
        fig_trend_ma.update_layout(
            title='Coverage Trend with Moving Averages',
            xaxis_title='Date',
            yaxis_title='Coverage %',
            height=500,
            plot_bgcolor='white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig_trend_ma, use_container_width=True)
    
    # Risk Score Card
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Endpoint Risk Matrix")
        
        if not df_risk.empty:
            # Create risk scoring
            risk_matrix = pd.DataFrame({
                'Risk Category': ['Critical', 'High Risk', 'EOL Version', 'Inactive', 'Compliant'],
                'Count': [
                    len(df_risk[df_risk['RISK_CATEGORY'] == 'Critical']),
                    len(df_risk[df_risk['RISK_CATEGORY'] == 'High Risk']),
                    len(df_risk[df_risk['RISK_CATEGORY'] == 'EOL Version']),
                    len(df_risk[df_risk['RISK_CATEGORY'] == 'Inactive']),
                    len(df_risk[df_risk['RISK_CATEGORY'] == 'Compliant'])
                ],
                'Weight': [10, 7, 5, 3, 0]  # Risk weights
            })
            
            risk_matrix['Risk Score'] = risk_matrix['Count'] * risk_matrix['Weight']
            total_risk_score = risk_matrix['Risk Score'].sum()
            
            # Risk score gauge
            fig_risk_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = total_risk_score,
                title = {'text': "Overall Risk Score", 'font': {'color': corp_colors['primary']}},
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [None, 1000]},
                    'bar': {'color': corp_colors['primary']},
                    'steps': [
                        {'range': [0, 200], 'color': '#d5f4e6'},
                        {'range': [200, 500], 'color': '#aed6f1'},
                        {'range': [500, 1000], 'color': '#fadbd8'}
                    ],
                    'threshold': {
                        'line': {'color': corp_colors['secondary'], 'width': 4},
                        'thickness': 0.75,
                        'value': 500
                    }
                }
            ))
            
            fig_risk_gauge.update_layout(
                paper_bgcolor='white'
            )
            
            st.plotly_chart(fig_risk_gauge, use_container_width=True)
    
    with col2:
        st.markdown("#### Health Score Calculation")
        
        # Calculate health score components
        coverage_score = coverage_pct / 100 * 40  # 40% weight
        active_rate = (active_endpoints / total_endpoints * 100) if total_endpoints > 0 else 0
        active_score = active_rate / 100 * 30  # 30% weight
        eol_rate = (100 - (eol_endpoints / total_endpoints * 100)) if total_endpoints > 0 else 100
        eol_score = eol_rate / 100 * 30  # 30% weight
        
        health_score = coverage_score + active_score + eol_score
        
        # Health score breakdown
        health_components = pd.DataFrame({
            'Component': ['Coverage', 'Active Rate', 'Non-EOL Rate'],
            'Score': [coverage_score, active_score, eol_score],
            'Weight': [40, 30, 30]
        })
        
        fig_health = px.bar(
            health_components,
            x='Component',
            y='Score',
            title=f'Health Score Breakdown (Total: {health_score:.1f}/100)',
            color='Component',
            color_discrete_map={
                'Coverage': corp_colors['primary'],
                'Active Rate': corp_colors['secondary'],
                'Non-EOL Rate': corp_colors['tertiary']
            },
            text='Score'
        )
        
        fig_health.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig_health.update_yaxes(range=[0, 45])
        fig_health.update_layout(
            plot_bgcolor='white',
            showlegend=False
        )
        
        st.plotly_chart(fig_health, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1rem;">
    <p><strong>CrowdStrike EDR Dashboard</strong> | Group Information Security</p>
    <p>Data Platform & ETL for Data Management | Real-time monitoring with 2-minute refresh</p>
    <p style="font-size: 0.85rem; margin-top: 0.5rem;">© 2025 GenericCorp Corporation. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)