# Import packages
import streamlit as st
import pandas as pd
# import plotly.express as px  # Not available in Snowflake
# import plotly.graph_objects as go  # Not available in Snowflake
# from plotly.subplots import make_subplots  # Not available in Snowflake
from snowflake.snowpark.context import get_active_session
from datetime import datetime, timedelta
# import numpy as np  # Not available in Snowflake


# Complete dummy plotly objects to prevent ALL NameErrors and AttributeErrors
class _DummyFigure:
    '''Dummy Figure class that accepts any method call and does nothing'''
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        '''Return a dummy method for any attribute access'''
        def dummy_method(*args, **kwargs):
            return self
        return dummy_method

    # Explicitly define common methods for clarity
    def add_trace(self, *args, **kwargs):
        return self
    def update_layout(self, *args, **kwargs):
        return self
    def update_xaxes(self, *args, **kwargs):
        return self
    def update_yaxes(self, *args, **kwargs):
        return self
    def add_hline(self, *args, **kwargs):
        return self
    def add_vline(self, *args, **kwargs):
        return self
    def add_shape(self, *args, **kwargs):
        return self
    def add_annotation(self, *args, **kwargs):
        return self
    def show(self, *args, **kwargs):
        pass

class _DummyPlotly:
    '''Dummy plotly.express that returns dummy figures'''
    def __getattr__(self, name):
        '''Return a function that creates dummy figures'''
        def dummy_chart(*args, **kwargs):
            return _DummyFigure()
        return dummy_chart

    # Explicitly define common chart types
    def bar(self, *args, **kwargs):
        return _DummyFigure()
    def line(self, *args, **kwargs):
        return _DummyFigure()
    def scatter(self, *args, **kwargs):
        return _DummyFigure()
    def pie(self, *args, **kwargs):
        return _DummyFigure()
    def histogram(self, *args, **kwargs):
        return _DummyFigure()
    def box(self, *args, **kwargs):
        return _DummyFigure()
    def area(self, *args, **kwargs):
        return _DummyFigure()
    def treemap(self, *args, **kwargs):
        return _DummyFigure()
    def sunburst(self, *args, **kwargs):
        return _DummyFigure()
    def funnel(self, *args, **kwargs):
        return _DummyFigure()

class _DummyGO:
    '''Dummy plotly.graph_objects'''
    def __getattr__(self, name):
        '''Return appropriate dummy for any attribute'''
        if name == 'Figure':
            return lambda *args, **kwargs: _DummyFigure()
        else:
            # For trace types (Bar, Scatter, etc.), return empty dict
            return lambda *args, **kwargs: {}

    def Figure(self, *args, **kwargs):
        return _DummyFigure()
    def Bar(self, *args, **kwargs):
        return {}
    def Scatter(self, *args, **kwargs):
        return {}
    def Pie(self, *args, **kwargs):
        return {}
    def Histogram(self, *args, **kwargs):
        return {}
    def Box(self, *args, **kwargs):
        return {}
    def Heatmap(self, *args, **kwargs):
        return {}

class _DummySubplots:
    '''Dummy make_subplots function'''
    def __call__(self, *args, **kwargs):
        return _DummyFigure()

# Create dummy objects
px = _DummyPlotly()
go = _DummyGO()
make_subplots = _DummySubplots()


# Page config
st.set_page_config(
    page_title="Zscaler Security Dashboard",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS - Same color palette and design
st.markdown("""
<style>
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
    
    h3 {
        color: #0a3d62;
        border-bottom: 3px solid transparent;
        border-image: linear-gradient(to right, #0a3d62, #1e5f8e, transparent) 1;
        padding-bottom: 0.75rem;
        margin-top: 2rem;
        font-weight: 600;
    }
    
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
</style>
""", unsafe_allow_html=True)

# Get session
session = get_active_session()

# Header
st.markdown("""
<div class="main-header">
    <h1 style="text-align: center; margin: 0; position: relative; z-index: 1;">
        <span style="font-size: 2.5rem;">🔐</span> Zscaler Security Dashboard
    </h1>
    <p style="text-align: center; margin: 0.75rem 0 0 0; opacity: 0.9; position: relative; z-index: 1; font-size: 1.1rem;">
        Cloud Security Platform - Zero Trust Network Access
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #0a3d62, #1e5f8e); border-radius: 12px; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(10, 61, 98, 0.2);">
        <h2 style="color: white; margin: 0; font-size: 1.5rem;">🏢 GenericCorp</h2>
        <p style="color: #e8f0f8; font-size: 0.95rem; margin-top: 0.5rem;">Zscaler Security Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filters
    st.header("📊 Dashboard Filters")
    
    # Domain filter
    domain_filter = st.multiselect(
        "Domain Selection",
        ["All Domains", "leviat.com", "CompanyX.com", "primex.com"],
        default=["All Domains"],
        help="Filter by email domain"
    )
    
    # Severity filter
    severity_filter = st.multiselect(
        "Threat Severity",
        ["Critical", "High", "Medium", "Low", "All"],
        default=["All"],
        help="Filter by threat severity"
    )
    
    # Date range
    date_range = st.selectbox(
        "Time Period",
        ["Last 7 Days", "Last 30 Days", "Last 90 Days"],
        index=1,
        help="Select time range for analysis"
    )
    
    st.markdown("---")
    
    # Refresh
    auto_refresh = st.checkbox("🔄 Auto-refresh (5 min)", value=True)
    if st.button("🔄 Refresh Now", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.info("""
    **📊 Monitoring:**
    - Agent Health
    - Threat Analysis
    - Endpoint Risk
    - Deployment Coverage
    - Security Alerts
    - Compliance Status
    """)

# Data loading functions
@st.cache_data(ttl=300)
def load_data(query):
    try:
        return session.sql(query).to_pandas()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Load data from Snowflake views
agent_health_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_ZSCALER_AGENT_HEALTH"
threat_analysis_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_ZSCALER_ANALYSIS LIMIT 1000"
compliance_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_ZSCALER_COMPLIANCE_SETTINGS"
coverage_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_ZSCALER_DEPLOYMENT_COVERAGE"
risk_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_ZSCALER_ENDPOINT_RISK LIMIT 500"
alerts_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_ZSCALER_SECURITY_ALERTS LIMIT 500"
threat_summary_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_ZSCALER_THREAT_SUMMARY"

df_health = load_data(agent_health_query)
df_analysis = load_data(threat_analysis_query)
df_compliance = load_data(compliance_query)
df_coverage = load_data(coverage_query)
df_risk = load_data(risk_query)
df_alerts = load_data(alerts_query)
df_threat_summary = load_data(threat_summary_query)

# Calculate KPIs
if not df_health.empty:
    total_agents = df_health['TOTAL_AGENTS'].sum()
    healthy_agents = df_health['HEALTHY_AGENTS'].sum() if 'HEALTHY_AGENTS' in df_health.columns else 0
    health_pct = df_health['HEALTH_PCT'].mean() if 'HEALTH_PCT' in df_health.columns else 0
    non_compliant_pct = df_health['NON_COMPLIANT_PCT'].mean() if 'NON_COMPLIANT_PCT' in df_health.columns else 0
else:
    total_agents = healthy_agents = health_pct = non_compliant_pct = 0

if not df_coverage.empty:
    total_devices = df_coverage['TOTAL_DEVICES'].sum()
    covered_devices = df_coverage['COVERED_DEVICES'].sum() if 'COVERED_DEVICES' in df_coverage.columns else 0
    coverage_pct = df_coverage['COVERAGE_PCT'].mean() if 'COVERAGE_PCT' in df_coverage.columns else 0
else:
    total_devices = covered_devices = coverage_pct = 0

if not df_threat_summary.empty:
    total_threats = df_threat_summary['THREAT_COUNT'].sum()
    affected_devices = df_threat_summary['AFFECTED_DEVICES'].sum()
else:
    total_threats = affected_devices = 0

if not df_alerts.empty:
    active_alerts = len(df_alerts)
else:
    active_alerts = 0

# KPIs
st.markdown("### 📊 Executive Summary")

kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)

with kpi_col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{total_agents:,}</div>
        <div class="kpi-label">Total Agents</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{health_pct:.1f}%</div>
        <div class="kpi-label">Agent Health</div>
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
        <div class="kpi-value">{total_threats:,}</div>
        <div class="kpi-label">Total Threats</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{active_alerts:,}</div>
        <div class="kpi-label">Active Alerts</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col6:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{affected_devices:,}</div>
        <div class="kpi-label">Affected Devices</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🛡️ Agent Health",
    "🔍 Threat Analysis", 
    "⚠️ Endpoint Risk",
    "📈 Coverage & Deployment",
    "🚨 Security Alerts",
    "📊 Threat Trends",
    "🌐 Executive Dashboard"
])

# Color palette
colors = {
    'primary': '#0a3d62',
    'secondary': '#1e5f8e',
    'success': '#27ae60',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'info': '#3498db'
}

# Tab 1: Agent Health
with tab1:
    st.markdown("### Zscaler Agent Health Overview")
    
    if not df_health.empty:
        # Health metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Agents", f"{total_agents:,}")
        with col2:
            st.metric("Healthy Agents", f"{healthy_agents:,}")
        with col3:
            st.metric("Health Rate", f"{health_pct:.1f}%")
        with col4:
            st.metric("Non-Compliant", f"{non_compliant_pct:.1f}%", f"-{non_compliant_pct:.1f}%")
        
        # Health visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Health compliance gauge
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = health_pct,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Agent Health Compliance"},
                delta = {'reference': 95},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': colors['secondary']},
                    'steps': [
                        {'range': [0, 85], 'color': 'lightgray'},
                        {'range': [85, 95], 'color': 'gray'}
                    ],
                    'threshold': {
                        'line': {'color': 'red', 'width': 4},
                        'thickness': 0.75,
                        'value': 95
                    }
                }
            ))
            fig_gauge.update_layout(height=400, paper_bgcolor='white')
            st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col2:
            # Agent health by scope
            if 'HEALTH_SCOPE' in df_health.columns:
                fig_scope = px
                fig_scope.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig_scope.update_layout(plot_bgcolor='white', showlegend=False)
                st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_scope, use_container_width=True)
            else:
                st.info("Health scope data not available")
        
        # Agent health details
        st.markdown("### Agent Health Details")
        st.dataframe(
            df_health.style.format({
                'HEALTH_PCT': '{:.1f}%',
                'NON_COMPLIANT_PCT': '{:.1f}%'
            }),
            use_container_width=True
        )

# Tab 2: Threat Analysis
with tab2:
    st.markdown("### Threat Analysis & Intelligence")
    
    if not df_analysis.empty:
        # Threat metrics
        col1, col2, col3, col4 = st.columns(4)
        
        unique_threats = df_analysis['THREAT_NAME'].nunique() if 'THREAT_NAME' in df_analysis.columns else 0
        unique_devices = df_analysis['DEVICE_HOSTNAME'].nunique() if 'DEVICE_HOSTNAME' in df_analysis.columns else 0
        unique_users = df_analysis['USER'].nunique() if 'USER' in df_analysis.columns else 0
        unique_domains = df_analysis['DOMAIN'].nunique() if 'DOMAIN' in df_analysis.columns else 0
        
        with col1:
            st.metric("Unique Threats", f"{unique_threats:,}")
        with col2:
            st.metric("Affected Devices", f"{unique_devices:,}")
        with col3:
            st.metric("Affected Users", f"{unique_users:,}")
        with col4:
            st.metric("Domains", f"{unique_domains:,}")
        
        # Threat visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Threat severity distribution
            if 'SEVERITY' in df_analysis.columns:
                severity_counts = df_analysis['SEVERITY'].value_counts()
                fig_severity = px.pie(
                    values=severity_counts.values,
                    names=severity_counts.index,
                    title='Threat Severity Distribution',
                    color_discrete_map={
                        'Critical': colors['danger'],
                        'High': colors['warning'],
                        'Medium': colors['info'],
                        'Low': colors['success']
                    }
                )
                fig_severity.update_layout(plot_bgcolor='white')
                st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_severity, use_container_width=True)
        
        with col2:
            # Top threat reasons
            if 'REASON' in df_analysis.columns:
                reason_counts = df_analysis['REASON'].value_counts().head(10)
                fig_reasons = px
                fig_reasons.update_layout(plot_bgcolor='white', showlegend=False,
                                         yaxis_title='', xaxis_title='Count')
                st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_reasons, use_container_width=True)
        
        # Threat timeline
        st.markdown("### Threat Activity Timeline")
        
        if 'DATE_SEEN' in df_analysis.columns:
            # Convert DATE_SEEN to datetime if it's not already
            df_analysis_copy = df_analysis.copy()
            df_analysis_copy['DATE_SEEN_PARSED'] = pd.to_datetime(df_analysis_copy['DATE_SEEN'], 
                                                                   format='%d-%m-%Y %H:%M', errors='coerce')
            
            if not df_analysis_copy['DATE_SEEN_PARSED'].isna().all():
                df_analysis_copy['DATE'] = df_analysis_copy['DATE_SEEN_PARSED'].dt.date
                daily_threats = df_analysis_copy.groupby('DATE').size().reset_index(name='Count')
                
                fig_timeline = px.line(
                    daily_threats,
                    x='DATE',
                    y='Count',
                    title='Daily Threat Activity',
                    markers=True
                )
                fig_timeline.update_layout(plot_bgcolor='white')
                st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Top affected devices
        st.markdown("### Most Affected Resources")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'DEVICE_HOSTNAME' in df_analysis.columns:
                top_devices = df_analysis['DEVICE_HOSTNAME'].value_counts().head(10)
                fig_devices = px
                fig_devices.update_layout(plot_bgcolor='white', showlegend=False,
                                         yaxis_title='', xaxis_title='Threat Count')
                st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_devices, use_container_width=True)
        
        with col2:
            if 'USER' in df_analysis.columns:
                top_users = df_analysis['USER'].value_counts().head(10)
                fig_users = px
                fig_users.update_layout(plot_bgcolor='white', showlegend=False,
                                       yaxis_title='', xaxis_title='Threat Count')
                st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_users, use_container_width=True)

# Tab 3: Endpoint Risk
with tab3:
    st.markdown("### Endpoint Risk Assessment")
    
    if not df_risk.empty:
        # Risk metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_endpoints = len(df_risk)
        high_risk = len(df_risk[df_risk['RISK_LEVEL'] == 'High']) if 'RISK_LEVEL' in df_risk.columns else 0
        medium_risk = len(df_risk[df_risk['RISK_LEVEL'] == 'Medium']) if 'RISK_LEVEL' in df_risk.columns else 0
        low_risk = len(df_risk[df_risk['RISK_LEVEL'] == 'Low']) if 'RISK_LEVEL' in df_risk.columns else 0
        
        with col1:
            st.metric("Total Endpoints", f"{total_endpoints:,}")
        with col2:
            st.metric("High Risk", f"{high_risk:,}", f"{high_risk/total_endpoints*100:.1f}%")
        with col3:
            st.metric("Medium Risk", f"{medium_risk:,}", f"{medium_risk/total_endpoints*100:.1f}%")
        with col4:
            st.metric("Low Risk", f"{low_risk:,}", f"{low_risk/total_endpoints*100:.1f}%")
        
        # Risk visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk level distribution
            if 'RISK_LEVEL' in df_risk.columns:
                risk_counts = df_risk['RISK_LEVEL'].value_counts()
                fig_risk_dist = px.pie(
                    values=risk_counts.values,
                    names=risk_counts.index,
                    title='Risk Level Distribution',
                    color_discrete_map={
                        'High': colors['danger'],
                        'Medium': colors['warning'],
                        'Low': colors['success']
                    }
                )
                fig_risk_dist.update_layout(plot_bgcolor='white')
                st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_risk_dist, use_container_width=True)
        
        with col2:
            # Risk by device type
            if 'DEVICE_TYPE' in df_risk.columns and 'RISK_LEVEL' in df_risk.columns:
                risk_by_type = df_risk.groupby(['DEVICE_TYPE', 'RISK_LEVEL']).size().reset_index(name='Count')
                fig_risk_type = px
                fig_risk_type.update_layout(plot_bgcolor='white')
                st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_risk_type, use_container_width=True)
        
        # Risk factors analysis
        st.markdown("### Risk Factor Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Days inactive vs threat count scatter
            if 'DAYS_INACTIVE' in df_risk.columns and 'THREAT_COUNT_30D' in df_risk.columns:
                fig_scatter = px.scatter(
                    df_risk,
                    x='DAYS_INACTIVE',
                    y='THREAT_COUNT_30D',
                    color='RISK_LEVEL',
                    title='Inactivity vs Threat Exposure',
                    color_discrete_map={
                        'High': colors['danger'],
                        'Medium': colors['warning'],
                        'Low': colors['success']
                    },
                    labels={'DAYS_INACTIVE': 'Days Inactive', 'THREAT_COUNT_30D': 'Threats (30d)'}
                )
                fig_scatter.update_layout(plot_bgcolor='white')
                st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_scatter, use_container_width=True)
        
        with col2:
            # OS version risk
            if 'OS_VERSION' in df_risk.columns:
                os_risk = df_risk.groupby('OS_VERSION')['RISK_LEVEL'].value_counts().unstack(fill_value=0)
                if not os_risk.empty:
                    fig_os_risk = px
                    fig_os_risk.update_layout(plot_bgcolor='white')
                    st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_os_risk, use_container_width=True)
        
        # High risk endpoints table
        st.markdown("### High Risk Endpoints")
        if 'RISK_LEVEL' in df_risk.columns:
            high_risk_df = df_risk[df_risk['RISK_LEVEL'] == 'High'].head(20)
            if not high_risk_df.empty:
                display_cols = ['DEVICE_HOSTNAME', 'USER_EMAIL', 'DEVICE_TYPE', 'DAYS_INACTIVE', 
                               'THREAT_COUNT_30D', 'RISK_LEVEL']
                display_cols = [col for col in display_cols if col in high_risk_df.columns]
                st.dataframe(
                    high_risk_df[display_cols].style.apply(
                        lambda x: ['background-color: #ffeef0' for _ in x], axis=1
                    ),
                    use_container_width=True
                )

# Tab 4: Coverage & Deployment
with tab4:
    st.markdown("### Deployment Coverage Analysis")
    
    if not df_coverage.empty:
        # Coverage metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Devices", f"{total_devices:,}")
        with col2:
            st.metric("Covered Devices", f"{covered_devices:,}")
        with col3:
            st.metric("Coverage Rate", f"{coverage_pct:.1f}%")
        with col4:
            gap_pct = 100 - coverage_pct
            st.metric("Coverage Gap", f"{gap_pct:.1f}%", f"-{gap_pct:.1f}%")
        
        # Coverage visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Coverage gauge
            fig_coverage = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = coverage_pct,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Deployment Coverage"},
                delta = {'reference': 95},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': colors['success']},
                    'steps': [
                        {'range': [0, 70], 'color': 'lightgray'},
                        {'range': [70, 90], 'color': 'gray'}
                    ],
                    'threshold': {
                        'line': {'color': 'red', 'width': 4},
                        'thickness': 0.75,
                        'value': 95
                    }
                }
            ))
            fig_coverage.update_layout(height=400, paper_bgcolor='white')
            st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_coverage, use_container_width=True)
        
        with col2:
            # Coverage by scope
            if 'COVERAGE_SCOPE' in df_coverage.columns:
                fig_scope_coverage = px
                fig_scope_coverage.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig_scope_coverage.add_hline(y=95, line_dash="dash", line_color=colors['primary'],
                                            annotation_text="Target: 95%")
                fig_scope_coverage.update_layout(plot_bgcolor='white', showlegend=False)
                st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_scope_coverage, use_container_width=True)
        
        # Compliance settings
        if not df_compliance.empty:
            st.markdown("### Compliance Configuration")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Compliance parameters
                fig_compliance = px
                fig_compliance.update_layout(plot_bgcolor='white', showlegend=False,
                                           yaxis_title='', xaxis_title='Value')
                st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_compliance, use_container_width=True)
            
            with col2:
                # Compliance settings table
                st.markdown("#### Parameter Details")
                st.dataframe(df_compliance, use_container_width=True)

# Tab 5: Security Alerts
with tab5:
    st.markdown("### Security Alert Management")
    
    if not df_alerts.empty:
        # Alert metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_alerts = len(df_alerts)
        critical_alerts = len(df_alerts[df_alerts['ALERT_TYPE'].str.contains('Critical', case=False, na=False)]) if 'ALERT_TYPE' in df_alerts.columns else 0
        unique_devices_alerts = df_alerts['DEVICE_HOSTNAME'].nunique() if 'DEVICE_HOSTNAME' in df_alerts.columns else 0
        avg_days_inactive = df_alerts['DAYS_INACTIVE'].mean() if 'DAYS_INACTIVE' in df_alerts.columns else 0
        
        with col1:
            st.metric("Active Alerts", f"{total_alerts:,}")
        with col2:
            st.metric("Critical Alerts", f"{critical_alerts:,}")
        with col3:
            st.metric("Affected Devices", f"{unique_devices_alerts:,}")
        with col4:
            st.metric("Avg Days Inactive", f"{avg_days_inactive:.0f}")
        
        # Alert visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Alert type distribution
            if 'ALERT_TYPE' in df_alerts.columns:
                alert_types = df_alerts['ALERT_TYPE'].value_counts().head(10)
                fig_alert_types = px.pie(
                    values=alert_types.values,
                    names=alert_types.index,
                    title='Alert Type Distribution',
                    color_discrete_sequence=px.colors.sequential.Reds
                )
                fig_alert_types.update_layout(plot_bgcolor='white')
                st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_alert_types, use_container_width=True)
        
        with col2:
            # Days inactive distribution
            if 'DAYS_INACTIVE' in df_alerts.columns:
                fig_inactive = px.histogram(
                    df_alerts,
                    x='DAYS_INACTIVE',
                    nbins=20,
                    title='Alert Distribution by Days Inactive',
                    color_discrete_sequence=[colors['warning']]
                )
                fig_inactive.update_layout(plot_bgcolor='white', showlegend=False,
                                         xaxis_title='Days Inactive', yaxis_title='Alert Count')
                st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_inactive, use_container_width=True)
        
        # Alert details
        st.markdown("### Recent Security Alerts")
        
        # Convert LAST_CONNECTED to datetime for sorting
        if 'LAST_CONNECTED' in df_alerts.columns:
            df_alerts_sorted = df_alerts.copy()
            df_alerts_sorted['LAST_CONNECTED'] = pd.to_datetime(df_alerts_sorted['LAST_CONNECTED'])
            df_alerts_sorted = df_alerts_sorted.sort_values('LAST_CONNECTED', ascending=False)
            
            display_cols = ['ALERT_TYPE', 'DEVICE_HOSTNAME', 'USER_EMAIL', 'LAST_CONNECTED', 
                           'DAYS_INACTIVE', 'DESCRIPTION']
            display_cols = [col for col in display_cols if col in df_alerts_sorted.columns]
            
            st.dataframe(
                df_alerts_sorted[display_cols].head(20).style.apply(
                    lambda x: ['background-color: #ffeef0' if x['DAYS_INACTIVE'] > 30
                              else 'background-color: #fff4e6' if x['DAYS_INACTIVE'] > 7
                              else '' for _ in x], axis=1
                ),
                use_container_width=True
            )

# Tab 6: Threat Trends
with tab6:
    st.markdown("### Threat Trend Analysis")
    
    if not df_threat_summary.empty:
        # Trend metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Threats", f"{total_threats:,}")
        with col2:
            st.metric("Affected Devices", f"{affected_devices:,}")
        with col3:
            avg_threat_pct = df_threat_summary['THREAT_PERCENTAGE'].mean() if 'THREAT_PERCENTAGE' in df_threat_summary.columns else 0
            st.metric("Avg Threat %", f"{avg_threat_pct:.2f}%")
        with col4:
            unique_categories = df_threat_summary['THREAT_CATEGORY'].nunique() if 'THREAT_CATEGORY' in df_threat_summary.columns else 0
            st.metric("Threat Categories", f"{unique_categories:,}")
        
        # Threat timeline
        if 'THREAT_DAY' in df_threat_summary.columns:
            df_summary_copy = df_threat_summary.copy()
            df_summary_copy['THREAT_DAY'] = pd.to_datetime(df_summary_copy['THREAT_DAY'], errors='coerce')
            
            if not df_summary_copy['THREAT_DAY'].isna().all():
                daily_summary = df_summary_copy.groupby('THREAT_DAY').agg({
                    'THREAT_COUNT': 'sum',
                    'AFFECTED_DEVICES': 'sum'
                }).reset_index()
                
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(
                    x=daily_summary['THREAT_DAY'],
                    y=daily_summary['THREAT_COUNT'],
                    mode='lines+markers',
                    name='Threat Count',
                    line=dict(color=colors['danger'], width=2)
                ))
                fig_trend.add_trace(go.Scatter(
                    x=daily_summary['THREAT_DAY'],
                    y=daily_summary['AFFECTED_DEVICES'],
                    mode='lines+markers',
                    name='Affected Devices',
                    line=dict(color=colors['info'], width=2),
                    yaxis='y2'
                ))
                fig_trend.update_layout(
                    title='Threat Activity Trend',
                    xaxis_title='Date',
                    yaxis_title='Threat Count',
                    yaxis2=dict(
                        title='Affected Devices',
                        overlaying='y',
                        side='right'
                    ),
                    plot_bgcolor='white'
                )
                st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_trend, use_container_width=True)
        
        # Threat analysis by category
        col1, col2 = st.columns(2)
        
        with col1:
            if 'THREAT_CATEGORY' in df_threat_summary.columns:
                category_summary = df_threat_summary.groupby('THREAT_CATEGORY')['THREAT_COUNT'].sum().sort_values(ascending=False).head(10)
                fig_category = px
                fig_category.update_layout(plot_bgcolor='white', showlegend=False,
                                         yaxis_title='', xaxis_title='Threat Count')
                st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_category, use_container_width=True)
        
        with col2:
            if 'DEVICE_TYPE' in df_threat_summary.columns:
                device_summary = df_threat_summary.groupby('DEVICE_TYPE')['THREAT_COUNT'].sum().sort_values(ascending=False)
                fig_device = px.pie(
                    values=device_summary.values,
                    names=device_summary.index,
                    title='Threats by Device Type',
                    color_discrete_sequence=px.colors.sequential.Blues
                )
                fig_device.update_layout(plot_bgcolor='white')
                st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_device, use_container_width=True)

# Tab 7: Executive Dashboard
with tab7:
    st.markdown("### Executive Security Dashboard")
    
    # Executive summary metrics
    col1, col2 = st.columns(2)
    
    with col1:
        # Overall security posture
        security_score = (health_pct + coverage_pct) / 2 if (health_pct + coverage_pct) > 0 else 0
        
        fig_security = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = security_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Overall Security Score"},
            delta = {'reference': 95},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': colors['primary']},
                'steps': [
                    {'range': [0, 70], 'color': '#ffeeee'},
                    {'range': [70, 85], 'color': '#fff4e6'},
                    {'range': [85, 95], 'color': '#ffffee'},
                    {'range': [95, 100], 'color': '#eeffee'}
                ],
                'threshold': {
                    'line': {'color': colors['danger'], 'width': 4},
                    'thickness': 0.75,
                    'value': 95
                }
            }
        ))
        fig_security.update_layout(height=400, paper_bgcolor='white')
        st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_security, use_container_width=True)
    
    with col2:
        # Risk assessment matrix
        risk_data = pd.DataFrame({
            'Category': ['Agent Health', 'Coverage', 'Threats', 'Compliance'],
            'Risk Level': [
                100 - health_pct if health_pct > 0 else 100,
                100 - coverage_pct if coverage_pct > 0 else 100,
                min(total_threats / 100, 100) if total_threats > 0 else 0,
                non_compliant_pct if non_compliant_pct > 0 else 0
            ],
            'Status': [
                'High' if health_pct < 85 else 'Medium' if health_pct < 95 else 'Low',
                'High' if coverage_pct < 85 else 'Medium' if coverage_pct < 95 else 'Low',
                'High' if total_threats > 1000 else 'Medium' if total_threats > 100 else 'Low',
                'High' if non_compliant_pct > 15 else 'Medium' if non_compliant_pct > 5 else 'Low'
            ]
        })
        
        risk_colors = {
            'Low': colors['success'],
            'Medium': colors['warning'],
            'High': colors['danger']
        }
        
        fig_risk = px
        fig_risk.update_traces(texttemplate='%{text:.0f}', textposition='outside')
        fig_risk.update_layout(plot_bgcolor='white', showlegend=True)
        st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_risk, use_container_width=True)
    
    # Executive action items
    st.markdown("### Priority Action Items")
    
    action_items = pd.DataFrame({
        'Priority': ['🔴 Critical', '🟠 High', '🟡 Medium', '🟢 Low'],
        'Action': [
            f'Address {active_alerts} active security alerts',
            f'Improve agent health from {health_pct:.1f}% to 95%',
            f'Increase coverage from {coverage_pct:.1f}% to target 95%',
            'Schedule quarterly security review'
        ],
        'Impact': ['High - Security Risk', 'High - Compliance', 'Medium - Coverage', 'Low - Process'],
        'Deadline': ['Immediate', 'Within 48 hours', 'Within 1 week', 'End of month']
    })
    
    st.dataframe(action_items, use_container_width=True, hide_index=True)
    
    # Compliance summary
    st.markdown("### Compliance Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        health_status = "✅ Compliant" if health_pct >= 95 else "⚠️ Review Required"
        st.info(f"**Agent Health**\n{health_status}\n{health_pct:.1f}%")
    
    with col2:
        coverage_status = "✅ Compliant" if coverage_pct >= 95 else "⚠️ Review Required"
        st.info(f"**Deployment Coverage**\n{coverage_status}\n{coverage_pct:.1f}%")
    
    with col3:
        threat_status = "🔴 Critical" if total_threats > 1000 else "⚠️ Elevated" if total_threats > 100 else "✅ Normal"
        st.info(f"**Threat Level**\n{threat_status}\n{total_threats:,} threats")
    
    with col4:
        alert_status = "🔴 Critical" if active_alerts > 100 else "⚠️ Elevated" if active_alerts > 10 else "✅ Under Control"
        st.info(f"**Alert Status**\n{alert_status}\n{active_alerts} active alerts")
    
    # Key insights
    st.markdown("### Key Security Insights")
    
    insights = []
    
    if health_pct < 95:
        insights.append(f"⚠️ Agent health is below target at {health_pct:.1f}%. Immediate action required to reach 95% compliance.")
    
    if coverage_pct < 95:
        insights.append(f"⚠️ Deployment coverage is {coverage_pct:.1f}%, below the 95% target. {100-coverage_pct:.1f}% of devices remain unprotected.")
    
    if total_threats > 100:
        insights.append(f"🔴 High threat activity detected with {total_threats:,} threats affecting {affected_devices:,} devices.")
    
    if active_alerts > 10:
        insights.append(f"⚠️ {active_alerts} active security alerts require immediate attention.")
    
    if insights:
        for insight in insights:
            st.warning(insight)
    else:
        st.success("✅ All security metrics are within acceptable ranges.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1rem;">
    <p><strong>Zscaler Security Dashboard</strong> | Cloud Security Platform</p>
    <p>Group Information Security - Zero Trust Network Access</p>
    <p style="font-size: 0.85rem;">© 2025 GenericCorp Corporation. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)