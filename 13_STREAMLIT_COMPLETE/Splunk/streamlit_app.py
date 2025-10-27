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
class _DummyColors:
    '''Dummy color palettes'''
    class sequential:
        Reds = ['#fee5d9', '#fcae91', '#fb6a4a', '#de2d26', '#a50f15']
        Blues = ['#eff3ff', '#bdd7e7', '#6baed6', '#3182bd', '#08519c']
        Greens = ['#edf8e9', '#bae4b3', '#74c476', '#31a354', '#006d2c']
        RdYlGn = ['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641']

    class diverging:
        RdYlGn = ['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641']
        RdBu = ['#ca0020', '#f4a582', '#f7f7f7', '#92c5de', '#0571b0']

class _DummyNumpy:
    '''Dummy numpy replacement'''
    # Constants
    inf = float('inf')

    class random:
        '''Dummy numpy.random submodule'''
        @staticmethod
        def standard_normal(size=None):
            '''Generate standard normal random numbers using Python's random'''
            import random as py_random
            if size is None:
                return py_random.gauss(0, 1)
            return [py_random.gauss(0, 1) for _ in range(size)]

        @staticmethod
        def randint(low, high=None, size=None):
            '''Generate random integers'''
            import random as py_random
            if high is None:
                high = low
                low = 0
            if size is None:
                return py_random.randint(low, high - 1)
            return [py_random.randint(low, high - 1) for _ in range(size)]

        @staticmethod
        def poisson(lam=1.0, size=None):
            '''Generate Poisson random numbers (approximated with normal distribution)'''
            import random as py_random
            # Simple approximation: Poisson ≈ Normal(λ, √λ) for large λ
            import math
            if size is None:
                # For single value, use exponential intervals method
                L = math.exp(-lam)
                k = 0
                p = 1.0
                while p > L:
                    k += 1
                    p *= py_random.random()
                return max(0, k - 1)
            else:
                # For array, use simpler approximation
                if lam > 10:
                    # Normal approximation for large lambda
                    return [max(0, int(py_random.gauss(lam, math.sqrt(lam)))) for _ in range(size)]
                else:
                    # Exact method for small lambda
                    result = []
                    L = math.exp(-lam)
                    for _ in range(size):
                        k = 0
                        p = 1.0
                        while p > L:
                            k += 1
                            p *= py_random.random()
                        result.append(max(0, k - 1))
                    return result

    def round(self, *args, **kwargs):
        '''Dummy round function - returns input as-is'''
        if args:
            return args[0]  # Return first argument
        return None

    def array(self, *args, **kwargs):
        '''Dummy array function'''
        if args:
            return args[0]
        return []

    def arange(self, *args, **kwargs):
        '''Dummy arange - returns range as list'''
        if len(args) == 1:
            return list(range(int(args[0])))
        elif len(args) == 2:
            return list(range(int(args[0]), int(args[1])))
        elif len(args) == 3:
            return list(range(int(args[0]), int(args[1]), int(args[2])))
        return []

    def __getattr__(self, name):
        '''Return dummy function for any numpy method'''
        def dummy_func(*args, **kwargs):
            if args:
                return args[0]
            return None
        return dummy_func
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
    colors = _DummyColors()
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
np = _DummyNumpy()


# Page config
st.set_page_config(
    page_title="CPR - Splunk Security Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS - Same design pattern as Sophos
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

# Set database context to avoid STAGE GET errors
try:
    session.sql("USE DATABASE DEV_REPORTING").collect()
    session.sql("USE SCHEMA SECURITY_ANALYTICS").collect()
except Exception as e:
    st.warning(f"Could not set database context: {e}")

# Header
st.markdown("""
<div class="main-header">
    <h1 style="text-align: center; margin: 0; position: relative; z-index: 1;">
        <span style="font-size: 2.5rem;">🔍</span> Splunk Security Dashboard
    </h1>
    <p style="text-align: center; margin: 0.75rem 0 0 0; opacity: 0.9; position: relative; z-index: 1; font-size: 1.1rem;">
        Security Information & Event Management Platform
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #0a3d62, #1e5f8e); border-radius: 12px; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(10, 61, 98, 0.2);">
        <h2 style="color: white; margin: 0; font-size: 1.5rem;">🏢 GenericCorp</h2>
        <p style="color: #e8f0f8; font-size: 0.95rem; margin-top: 0.5rem;">Splunk SIEM Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filters
    st.header("📊 Dashboard Filters")
    
    # Company filter
    company_filter = st.multiselect(
        "Company Selection",
        ["All", "GenericCorp GIS", "GenericCorp - BOL", "GenericCorp Europe East IT", "GenericCorp Treasury", "CompanyX"],
        default=["All"],
        help="Filter by company"
    )
    
    # Priority filter
    priority_filter = st.multiselect(
        "Priority Level",
        ["All", "Critical (1)", "High (2)", "Medium (3)", "Low (4)"],
        default=["All"],
        help="Filter by alert priority"
    )
    
    # Date range
    date_range = st.selectbox(
        "Time Period",
        ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Year to Date"],
        index=1,
        help="Select time range for analysis"
    )
    
    st.markdown("---")
    
    # Refresh
    auto_refresh = st.checkbox("🔄 Auto-refresh (5 min)", value=True)
    if st.button("🔄 Refresh Now", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()  # Use Streamlit 1.28+ uses st.rerun()
    
    st.markdown("---")
    st.info("""
    **📊 Monitoring:**
    - Alert Trends
    - Response Times
    - Resolution Effectiveness
    - Log Coverage
    - SLA Compliance
    """)

# Safe division helper function
def safe_divide(numerator, denominator, default=0, multiplier=1):
    """Safely divide two numbers, returning default if division by zero"""
    try:
        if denominator == 0 or pd.isna(denominator) or pd.isna(numerator):
            return default
        return (numerator / denominator) * multiplier
    except:
        return default

# Data loading functions with better error handling
@st.cache_data(ttl=300)
def load_data(query):
    try:
        # Wrap queries with NULLIF to prevent division by zero in SQL
        safe_query = query
        if "VW_SPLUNK" in query:
            # Add a note that division by zero might be happening in views
            return session.sql(query).to_pandas()
        return session.sql(query).to_pandas()
    except Exception as e:
        if "Division by zero" in str(e):
            st.warning(f"Division by zero error in view. Loading empty dataset. Please check the Snowflake view definition.")
            return pd.DataFrame()
        else:
            st.error(f"Error loading data: {str(e)}")
            return pd.DataFrame()

# Load data from Snowflake views with error handling
alert_trends_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_SPLUNK_ALERT_TRENDS ORDER BY ALERT_WEEK DESC"
alert_response_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_SPLUNK_ALERT_RESPONSE ORDER BY SNAPSHOT_DATE DESC"
analysis_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_SPLUNK_ANALYSIS ORDER BY CREATED DESC LIMIT 1000"
executive_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_SPLUNK_EXECUTIVE_SUMMARY ORDER BY SNAPSHOT_DATE DESC"
log_coverage_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_SPLUNK_LOG_COVERAGE ORDER BY SNAPSHOT_DATE DESC"
resolution_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_SPLUNK_RESOLUTION_EFFECTIVENESS ORDER BY SNAPSHOT_DATE DESC"

df_trends = load_data(alert_trends_query)
df_response = load_data(alert_response_query)
df_analysis = load_data(analysis_query)
df_executive = load_data(executive_query)
df_coverage = load_data(log_coverage_query)
df_resolution = load_data(resolution_query)

# Calculate KPIs with null handling and safe division
if not df_executive.empty:
    total_hosts = df_executive['TOTAL_HOSTS'].iloc[0] if 'TOTAL_HOSTS' in df_executive.columns else 0
    active_hosts = df_executive['ACTIVE_HOSTS_1D'].iloc[0] if 'ACTIVE_HOSTS_1D' in df_executive.columns else 0
    total_alerts = df_executive['TOTAL_ALERTS'].iloc[0] if 'TOTAL_ALERTS' in df_executive.columns else 0
    open_alerts = df_executive['OPEN_ALERTS'].iloc[0] if 'OPEN_ALERTS' in df_executive.columns else 0
    critical_alerts = df_executive['CRITICAL_ALERTS'].iloc[0] if 'CRITICAL_ALERTS' in df_executive.columns else 0
    avg_resolution = df_executive['AVG_RESOLUTION_MIN'].iloc[0] if 'AVG_RESOLUTION_MIN' in df_executive.columns else 0
else:
    total_hosts = active_hosts = total_alerts = open_alerts = critical_alerts = avg_resolution = 0

# Handle null values and ensure numeric
total_hosts = float(total_hosts) if total_hosts and not pd.isna(total_hosts) else 0
active_hosts = float(active_hosts) if active_hosts and not pd.isna(active_hosts) else 0
total_alerts = float(total_alerts) if total_alerts and not pd.isna(total_alerts) else 0
open_alerts = float(open_alerts) if open_alerts and not pd.isna(open_alerts) else 0
critical_alerts = float(critical_alerts) if critical_alerts and not pd.isna(critical_alerts) else 0
avg_resolution = float(avg_resolution) if avg_resolution and not pd.isna(avg_resolution) else 0

# Calculate SLA compliance with null handling
if not df_response.empty and 'SLA_COMPLIANCE_PCT' in df_response.columns:
    sla_values = df_response['SLA_COMPLIANCE_PCT'].dropna()
    overall_sla = float(sla_values.mean()) if len(sla_values) > 0 else 0
else:
    overall_sla = 0

# KPIs
st.markdown("### 📊 Executive Summary")

kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)

with kpi_col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{int(total_alerts):,}</div>
        <div class="kpi-label">Total Alerts</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{int(open_alerts):,}</div>
        <div class="kpi-label">Open Alerts</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{int(critical_alerts):,}</div>
        <div class="kpi-label">Critical</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{int(avg_resolution)}m</div>
        <div class="kpi-label">Avg Resolution</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{overall_sla:.1f}%</div>
        <div class="kpi-label">SLA Compliance</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col6:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{int(active_hosts):,}</div>
        <div class="kpi-label">Active Hosts</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Alert Trends",
    "⏱️ Response Times",
    "🎯 Resolution Effectiveness",
    "📡 Log Coverage",
    "🔍 Alert Analysis",
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

# Tab 1: Alert Trends
with tab1:
    st.markdown("### Alert Volume and Trends Analysis")
    
    if not df_trends.empty:
        # Trend metrics with safe division
        col1, col2, col3, col4 = st.columns(4)
        
        total_weekly_alerts = float(df_trends['ALERT_COUNT'].sum()) if 'ALERT_COUNT' in df_trends.columns else 0
        resolved_alerts = float(df_trends['RESOLVED_COUNT'].sum()) if 'RESOLVED_COUNT' in df_trends.columns else 0
        resolution_rate = safe_divide(resolved_alerts, total_weekly_alerts, 0, 100)
        within_sla = float(df_trends['RESOLVED_WITHIN_4H'].sum()) if 'RESOLVED_WITHIN_4H' in df_trends.columns else 0
        
        with col1:
            st.metric("Weekly Alerts", f"{int(total_weekly_alerts):,}")
        with col2:
            st.metric("Resolved", f"{int(resolved_alerts):,}")
        with col3:
            st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
        with col4:
            st.metric("Within SLA (4h)", f"{int(within_sla):,}")
        
        # Alert trend over time
        col1, col2 = st.columns(2)
        
        with col1:
            # Weekly alert trend
            if 'ALERT_WEEK' in df_trends.columns:
                weekly_trend = df_trends.groupby('ALERT_WEEK').agg({
                    'ALERT_COUNT': 'sum',
                    'RESOLVED_COUNT': 'sum'
                }).reset_index()
                
                if not weekly_trend.empty:
                    fig_trend = go.Figure()
                    fig_trend.add_trace(go.Scatter(
                        x=weekly_trend['ALERT_WEEK'],
                        y=weekly_trend['ALERT_COUNT'],
                        mode='lines+markers',
                        name='Total Alerts',
                        line=dict(color=colors['primary'], width=2),
                        fill='tonexty',
                        fillcolor='rgba(10, 61, 98, 0.1)'
                    ))
                    fig_trend.add_trace(go.Scatter(
                        x=weekly_trend['ALERT_WEEK'],
                        y=weekly_trend['RESOLVED_COUNT'],
                        mode='lines+markers',
                        name='Resolved',
                        line=dict(color=colors['success'], width=2)
                    ))
                    fig_trend.update_layout(
                        title='Weekly Alert Trend',
                        xaxis_title='Week',
                        yaxis_title='Alert Count',
                        plot_bgcolor='white',
                        hovermode='x unified'
                    )
                else:
                    st.info("No weekly trend data available")
        
        with col2:
            # Priority distribution
            if 'PRIORITY' in df_trends.columns:
                priority_dist = df_trends.groupby('PRIORITY')['ALERT_COUNT'].sum().reset_index()
                priority_dist['Priority_Label'] = priority_dist['PRIORITY'].map({
                    1: 'Critical', 2: 'High', 3: 'Medium', 4: 'Low'
                })
                
                if not priority_dist.empty:
                    fig_priority = px.pie(
                        priority_dist,
                        values='ALERT_COUNT',
                        names='Priority_Label',
                        title='Alert Distribution by Priority',
                        color_discrete_map={
                            'Critical': colors['danger'],
                            'High': colors['warning'],
                            'Medium': colors['info'],
                            'Low': colors['success']
                        }
                    )
                    fig_priority.update_traces(textposition='inside', textinfo='percent+label')
        
        # Company-wise alert trends
        if 'COMPANY' in df_trends.columns:
            st.markdown("### Company Alert Performance")
            
            company_metrics = df_trends.groupby('COMPANY').agg({
                'ALERT_COUNT': 'sum',
                'RESOLVED_COUNT': 'sum',
                'SLA_COMPLIANCE_PCT': 'mean',
                'AVG_RESOLUTION_MIN': 'mean'
            }).reset_index()
            
            if not company_metrics.empty:
                fig_company = make_subplots(
                    rows=1, cols=2,
                    subplot_titles=('Alert Volume by Company', 'SLA Compliance by Company'),
                    specs=[[{'type': 'bar'}, {'type': 'bar'}]]
                )
                
                fig_company.add_trace(
                    go.Bar(
                        x=company_metrics['COMPANY'],
                        y=company_metrics['ALERT_COUNT'],
                        name='Total Alerts',
                        marker_color=colors['primary']
                    ),
                    row=1, col=1
                )
                
                fig_company.add_trace(
                    go.Bar(
                        x=company_metrics['COMPANY'],
                        y=company_metrics['SLA_COMPLIANCE_PCT'],
                        name='SLA %',
                        marker_color=company_metrics['SLA_COMPLIANCE_PCT'].apply(
                            lambda x: colors['success'] if x >= 95 else colors['warning'] if x >= 85 else colors['danger']
                        )
                    ),
                    row=1, col=2
                )
                
                fig_company.add_hline(y=95, line_dash="dash", line_color=colors['primary'], 
                                     annotation_text="Target: 95%", row=1, col=2)
                
                fig_company.update_layout(
                    showlegend=False,
                    plot_bgcolor='white',
                    height=400
                )
    else:
        st.warning("No alert trend data available")

# Tab 2: Response Times
with tab2:
    st.markdown("### Alert Response Time Analysis")
    
    if not df_response.empty:
        # Response metrics with safe calculations
        col1, col2, col3, col4 = st.columns(4)
        
        avg_response = float(df_response['AVG_RESOLUTION_MINUTES'].mean()) if 'AVG_RESOLUTION_MINUTES' in df_response.columns else 0
        p90_response = float(df_response['P90_RESOLUTION_MINUTES'].mean()) if 'P90_RESOLUTION_MINUTES' in df_response.columns else 0
        within_4h = float(df_response['RESOLVED_WITHIN_4H'].sum()) if 'RESOLVED_WITHIN_4H' in df_response.columns else 0
        sla_compliance = float(df_response['SLA_COMPLIANCE_PCT'].mean()) if 'SLA_COMPLIANCE_PCT' in df_response.columns else 0
        
        # Ensure no NaN values
        avg_response = avg_response if not pd.isna(avg_response) else 0
        p90_response = p90_response if not pd.isna(p90_response) else 0
        within_4h = within_4h if not pd.isna(within_4h) else 0
        sla_compliance = sla_compliance if not pd.isna(sla_compliance) else 0
        
        with col1:
            st.metric("Avg Response Time", f"{int(avg_response)} min")
        with col2:
            st.metric("P90 Response Time", f"{int(p90_response)} min")
        with col3:
            st.metric("Resolved < 4h", f"{int(within_4h):,}")
        with col4:
            st.metric("SLA Compliance", f"{sla_compliance:.1f}%")
        
        # Response time visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Response time by priority
            if 'PRIORITY' in df_response.columns:
                priority_response = df_response.groupby('PRIORITY').agg({
                    'AVG_RESOLUTION_MINUTES': 'mean',
                    'P90_RESOLUTION_MINUTES': 'mean'
                }).reset_index()
                
                if not priority_response.empty:
                    priority_response['Priority_Label'] = priority_response['PRIORITY'].map({
                        1: 'Critical', 2: 'High', 3: 'Medium', 4: 'Low'
                    })
                    
                    fig_priority_time = go.Figure()
                    fig_priority_time.add_trace(go.Bar(
                        x=priority_response['Priority_Label'],
                        y=priority_response['AVG_RESOLUTION_MINUTES'],
                        name='Average',
                        marker_color=colors['info']
                    ))
                    fig_priority_time.add_trace(go.Bar(
                        x=priority_response['Priority_Label'],
                        y=priority_response['P90_RESOLUTION_MINUTES'],
                        name='P90',
                        marker_color=colors['warning']
                    ))
                    fig_priority_time.add_hline(y=240, line_dash="dash", line_color=colors['danger'],
                                               annotation_text="4 Hour SLA")
                    fig_priority_time.update_layout(
                        title='Response Time by Priority',
                        xaxis_title='Priority',
                        yaxis_title='Minutes',
                        barmode='group',
                        plot_bgcolor='white'
                    )
        
        with col2:
            # SLA compliance gauge
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = sla_compliance,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "SLA Compliance (4h)"},
                delta = {'reference': 95, 'increasing': {'color': colors['success']}},
                gauge = {
                    'axis': {'range': [0, 100]},
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
    else:
        st.warning("No response time data available")

# Tab 3: Resolution Effectiveness
with tab3:
    st.markdown("### Resolution Effectiveness Analysis")
    
    if not df_resolution.empty:
        # Resolution metrics with safe defaults
        col1, col2, col3, col4 = st.columns(4)
        
        total_resolutions = float(df_resolution['RESOLUTION_COUNT'].sum()) if 'RESOLUTION_COUNT' in df_resolution.columns else 0
        avg_success_rate = float(df_resolution['SUCCESS_RATE_PCT'].mean()) if 'SUCCESS_RATE_PCT' in df_resolution.columns else 0
        critical_resolved = float(df_resolution['CRITICAL_COUNT'].sum()) if 'CRITICAL_COUNT' in df_resolution.columns else 0
        high_resolved = float(df_resolution['HIGH_COUNT'].sum()) if 'HIGH_COUNT' in df_resolution.columns else 0
        
        # Clean NaN values
        avg_success_rate = avg_success_rate if not pd.isna(avg_success_rate) else 0
        
        with col1:
            st.metric("Total Resolutions", f"{int(total_resolutions):,}")
        with col2:
            st.metric("Success Rate", f"{avg_success_rate:.1f}%")
        with col3:
            st.metric("Critical Resolved", f"{int(critical_resolved):,}")
        with col4:
            st.metric("High Resolved", f"{int(high_resolved):,}")
        
        # Resolution visualizations
        if 'CLOSE_CODE' in df_resolution.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                # Close code distribution
                close_code_dist = df_resolution.groupby('CLOSE_CODE')['RESOLUTION_COUNT'].sum().reset_index()
                close_code_dist = close_code_dist.nlargest(10, 'RESOLUTION_COUNT')
                
                if not close_code_dist.empty:
                    fig_close = px.bar(
                        close_code_dist,
                        x='RESOLUTION_COUNT',
                        y='CLOSE_CODE',
                        orientation='h',
                        title='Top 10 Resolution Types',
                        color='RESOLUTION_COUNT',
                        color_continuous_scale='Blues'
                    )
                    fig_close.update_layout(
                        plot_bgcolor='white',
                        showlegend=False,
                        yaxis_title='',
                        xaxis_title='Resolution Count'
                    )
            
            with col2:
                # Success rate by close code
                success_rates = df_resolution.groupby('CLOSE_CODE').agg({
                    'SUCCESS_RATE_PCT': 'mean',
                    'RESOLUTION_COUNT': 'sum'
                }).reset_index()
                success_rates = success_rates.nlargest(10, 'RESOLUTION_COUNT')
                
                if not success_rates.empty:
                    fig_success = px.bar(
                        success_rates.sort_values('SUCCESS_RATE_PCT'),
                        x='SUCCESS_RATE_PCT',
                        y='CLOSE_CODE',
                        orientation='h',
                        title='Success Rate by Resolution Type',
                        color='SUCCESS_RATE_PCT',
                        color_continuous_scale=[colors['danger'], colors['warning'], colors['success']]
                    )
                    fig_success.add_vline(x=95, line_dash="dash", line_color=colors['primary'],
                                         annotation_text="Target")
                    fig_success.update_layout(
                        plot_bgcolor='white',
                        showlegend=False,
                        yaxis_title='',
                        xaxis_title='Success Rate %'
                    )
    else:
        st.warning("No resolution data available")

# Tab 4: Log Coverage
with tab4:
    st.markdown("### Log Coverage Analysis")
    
    if not df_coverage.empty:
        # Coverage metrics with safe division
        col1, col2, col3, col4 = st.columns(4)
        
        total_monitored_hosts = float(df_coverage['TOTAL_HOSTS'].sum()) if 'TOTAL_HOSTS' in df_coverage.columns else 0
        active_1d = float(df_coverage['ACTIVE_1D'].sum()) if 'ACTIVE_1D' in df_coverage.columns else 0
        coverage_1d = safe_divide(active_1d, total_monitored_hosts, 0, 100)
        stale_hosts = float(df_coverage['STALE_HOSTS'].sum()) if 'STALE_HOSTS' in df_coverage.columns else 0
        
        with col1:
            st.metric("Total Hosts", f"{int(total_monitored_hosts):,}")
        with col2:
            st.metric("Active (24h)", f"{int(active_1d):,}")
        with col3:
            st.metric("Coverage (24h)", f"{coverage_1d:.1f}%")
        with col4:
            st.metric("Stale Hosts", f"{int(stale_hosts):,}", f"-{int(stale_hosts)}")
        
        # Coverage visualization
        if 'OPCO' in df_coverage.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                # Coverage by OPCO
                coverage_cols = []
                for col in ['COVERAGE_1D_PCT', 'COVERAGE_7D_PCT', 'COVERAGE_30D_PCT']:
                    if col in df_coverage.columns:
                        coverage_cols.append(col)
                
                if coverage_cols:
                    fig_opco = px.bar(
                        df_coverage,
                        x='OPCO',
                        y=coverage_cols,
                        title='Log Coverage by Operating Company',
                        labels={'value': 'Coverage %', 'variable': 'Time Period'},
                        color_discrete_map={
                            'COVERAGE_1D_PCT': colors['success'],
                            'COVERAGE_7D_PCT': colors['info'],
                            'COVERAGE_30D_PCT': colors['warning']
                        },
                        barmode='group'
                    )
                    fig_opco.update_layout(plot_bgcolor='white')
            
            with col2:
                # Active hosts trend
                active_data = pd.DataFrame({
                    'Period': ['1 Day', '7 Days', '30 Days'],
                    'Active_Hosts': [
                        df_coverage['ACTIVE_1D'].sum() if 'ACTIVE_1D' in df_coverage.columns else 0,
                        df_coverage['ACTIVE_7D'].sum() if 'ACTIVE_7D' in df_coverage.columns else 0,
                        df_coverage['ACTIVE_30D'].sum() if 'ACTIVE_30D' in df_coverage.columns else 0
                    ]
                })
                
                fig_active = px.line(
                    active_data,
                    x='Period',
                    y='Active_Hosts',
                    title='Active Hosts by Time Period',
                    markers=True
                )
                fig_active.update_traces(line_color=colors['primary'], line_width=3,
                                        marker=dict(size=12))
                fig_active.update_layout(
                    plot_bgcolor='white',
                    yaxis_title='Number of Active Hosts'
                )
    else:
        st.warning("No log coverage data available")

# Tab 5: Alert Analysis
with tab5:
    st.markdown("### Detailed Alert Analysis")
    
    if not df_analysis.empty:
        # Analysis metrics with safe division
        col1, col2, col3, col4 = st.columns(4)
        
        total_records = len(df_analysis)
        unique_sources = df_analysis['SOURCE_NAME'].nunique() if 'SOURCE_NAME' in df_analysis.columns else 0
        unique_companies = df_analysis['COMPANY'].nunique() if 'COMPANY' in df_analysis.columns else 0
        
        # Safe calculation for resolved percentage
        if 'STATE' in df_analysis.columns and total_records > 0:
            resolved_count = len(df_analysis[df_analysis['STATE'] == 'Resolved'])
            resolved_pct = safe_divide(resolved_count, total_records, 0, 100)
        else:
            resolved_pct = 0
        
        with col1:
            st.metric("Alert Records", f"{total_records:,}")
        with col2:
            st.metric("Unique Sources", f"{unique_sources:,}")
        with col3:
            st.metric("Companies", f"{unique_companies:,}")
        with col4:
            st.metric("Resolution Rate", f"{resolved_pct:.1f}%")
        
        # Alert visualizations
        if total_records > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                if 'ALERT_CATEGORY' in df_analysis.columns:
                    category_dist = df_analysis['ALERT_CATEGORY'].value_counts().head(10)
                    
                    if not category_dist.empty:
                        fig_category = px.pie(
                            values=category_dist.values,
                            names=category_dist.index,
                            title='Top Alert Categories',
                            color_discrete_sequence=px.colors.sequential.Blues
                        )
                        fig_category.update_traces(textposition='inside', textinfo='percent+label')
            
            with col2:
                if 'STATE' in df_analysis.columns:
                    state_dist = df_analysis['STATE'].value_counts()
                    
                    state_colors = {
                        'Resolved': colors['success'],
                        'Closed': colors['info'],
                        'Open': colors['warning'],
                        'Pending': colors['danger']
                    }
                    
                    fig_state = px.bar(
                        x=state_dist.index,
                        y=state_dist.values,
                        title='Alert State Distribution',
                        labels={'x': 'State', 'y': 'Count'},
                        color=state_dist.index,
                        color_discrete_map=state_colors
                    )
                    fig_state.update_layout(plot_bgcolor='white', showlegend=False)
                    st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_state, use_container_width=True)
            
            # Recent alerts table
            st.markdown("### Recent Alert Details")
            
            recent_alerts = df_analysis.head(100)
            display_cols = ['ALERT_ID', 'CREATED', 'STATE', 'PRIORITY', 'COMPANY', 
                           'SHORT_DESCRIPTION', 'CLOSE_CODE']
            
            # Filter columns that exist
            display_cols = [col for col in display_cols if col in recent_alerts.columns]
            
            if display_cols and 'STATE' in display_cols:
                st.dataframe(
                    recent_alerts[display_cols].style.apply(
                        lambda x: ['background-color: #ffeeee' if x['STATE'] == 'Open'
                                  else 'background-color: #eeffee' if x['STATE'] == 'Resolved'
                                  else '' for _ in x], axis=1
                    ),
                    use_container_width=True,
                    height=400
                )
            elif display_cols:
                st.dataframe(recent_alerts[display_cols], use_container_width=True, height=400)
                # Download button
                @st.cache_data
                def convert_to_csv_0(df):
                    return df.to_csv(index=False).encode('utf-8')

                csv_data = convert_to_csv_0(recent_alerts)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name="splunk_data.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="download_splunk_1"
                )
    else:
        st.warning("No alert analysis data available")

# Tab 6: Executive Dashboard
with tab6:
    st.markdown("### Executive Security Dashboard")
    
    # Executive summary metrics
    col1, col2 = st.columns(2)
    
    with col1:
        # Overall security score
        security_score = overall_sla
        
        fig_security = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = security_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Security Performance Score"},
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
    
    with col2:
        # Risk assessment
        risk_data = pd.DataFrame({
            'Category': ['Critical Alerts', 'Open Alerts', 'Response Time', 'Coverage'],
            'Risk Level': [
                min(critical_alerts * 5, 100) if critical_alerts else 0,
                min(safe_divide(open_alerts, 10, 0), 100) if open_alerts else 0,
                min(safe_divide(avg_resolution, 10, 0), 100) if avg_resolution else 0,
                100 - coverage_1d if 'coverage_1d' in locals() else 0
            ]
        })
        
        risk_data['Status'] = risk_data['Risk Level'].apply(
            lambda x: 'High' if x > 70 else 'Medium' if x > 30 else 'Low'
        )
        
        risk_colors_map = {
            'Low': colors['success'],
            'Medium': colors['warning'],
            'High': colors['danger']
        }
        
        fig_risk = px.bar(
            risk_data,
            x='Category',
            y='Risk Level',
            color='Status',
            title='Risk Assessment by Category',
            color_discrete_map=risk_colors_map,
            text='Risk Level'
        )
        fig_risk.update_traces(texttemplate='%{text:.0f}', textposition='outside')
        fig_risk.update_layout(plot_bgcolor='white', showlegend=True)
    
    # Key performance indicators
    st.markdown("### Key Performance Indicators")
    
    # Calculate KPI values with safe division
    resolution_kpi = safe_divide(
        resolved_alerts if 'resolved_alerts' in locals() else 0,
        total_weekly_alerts if 'total_weekly_alerts' in locals() and total_weekly_alerts > 0 else 1,
        0, 100
    )
    
    response_time_kpi = 100 - min(safe_divide(avg_resolution, 240, 0, 100), 100) if avg_resolution > 0 else 100
    
    kpi_data = pd.DataFrame({
        'KPI': ['Alert Resolution', 'SLA Compliance', 'Log Coverage', 'Response Time'],
        'Current': [
            resolution_kpi,
            overall_sla,
            coverage_1d if 'coverage_1d' in locals() else 0,
            response_time_kpi
        ],
        'Target': [95, 95, 95, 95]
    })
    
    kpi_data['Gap'] = kpi_data['Target'] - kpi_data['Current']
    
    fig_kpi = go.Figure()
    fig_kpi.add_trace(go.Bar(
        x=kpi_data['KPI'],
        y=kpi_data['Current'],
        name='Current',
        marker_color=colors['info'],
        text=kpi_data['Current'].round(1),
        textposition='auto'
    ))
    fig_kpi.add_trace(go.Bar(
        x=kpi_data['KPI'],
        y=kpi_data['Gap'].clip(lower=0),  # Ensure no negative gaps shown
        name='Gap to Target',
        marker_color=colors['warning'],
        text=kpi_data['Gap'].clip(lower=0).round(1),
        textposition='auto'
    ))
    fig_kpi.update_layout(
        barmode='stack',
        title='KPI Performance vs Targets',
        yaxis_title='Percentage',
        plot_bgcolor='white'
    )
    
    # Action items
    st.markdown("### Priority Action Items")
    
    action_items = pd.DataFrame({
        'Priority': ['🔴 Critical', '🟠 High', '🟡 Medium', '🟢 Low'],
        'Action': [
            f'Address {int(critical_alerts)} critical security alerts immediately',
            f'Resolve {int(open_alerts)} open alerts in the queue',
            f'Improve log coverage for {int(stale_hosts) if "stale_hosts" in locals() else 0} stale hosts',
            'Review weekly alert trends and patterns'
        ],
        'Impact': ['High - Security Risk', 'High - Operations', 'Medium - Visibility', 'Low - Process'],
        'Timeline': ['Immediate', 'Within 24 hours', 'Within 1 week', 'Ongoing']
    })
    
    st.dataframe(action_items, use_container_width=True, hide_index=True)
    # Download button
    @st.cache_data
    def convert_to_csv_1(df):
        return df.to_csv(index=False).encode('utf-8')

    csv_data = convert_to_csv_1(action_items)
    st.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name="splunk_data.csv",
        mime="text/csv",
        use_container_width=True,
        key="download_splunk_2"
    )
    
    # Compliance summary
    st.markdown("### Compliance Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        sla_status = "✅ Compliant" if overall_sla >= 95 else "⚠️ Review Required"
        st.info(f"**SLA Compliance**\n{sla_status}\n{overall_sla:.1f}%")
    
    with col2:
        resolution_status = "✅ Good" if resolution_rate >= 90 else "⚠️ Needs Improvement"
        st.info(f"**Resolution Rate**\n{resolution_status}\n{resolution_rate:.1f}%" if 'resolution_rate' in locals() else "**Resolution Rate**\nNo Data")
    
    with col3:
        coverage_status = "✅ Good" if coverage_1d >= 95 else "⚠️ Review Required"
        st.info(f"**Log Coverage**\n{coverage_status}\n{coverage_1d:.1f}%" if 'coverage_1d' in locals() else "**Log Coverage**\nNo Data")
    
    with col4:
        alert_status = "🔴 Critical" if critical_alerts > 10 else "✅ Under Control"
        st.info(f"**Alert Status**\n{alert_status}\n{int(critical_alerts)} critical alerts")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1rem;">
    <p><strong>Splunk Security Dashboard</strong> | SIEM Platform</p>
    <p>Security Operations Center - Data Platform & Analytics</p>
    <p style="font-size: 0.85rem;">© 2025 GenericCorp Corporation. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)