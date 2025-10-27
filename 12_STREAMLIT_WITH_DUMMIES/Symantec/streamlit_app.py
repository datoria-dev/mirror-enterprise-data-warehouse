# Import packages
import streamlit as st
import pandas as pd
# import plotly.express as px  # Not available in Snowflake
# import plotly.graph_objects as go  # Not available in Snowflake
# from plotly.subplots import make_subplots  # Not available in Snowflake
from snowflake.snowpark.context import get_active_session
from datetime import datetime, timedelta
# import numpy as np  # Not available in Snowflake


# Dummy plotly objects to prevent NameErrors in Snowflake
class _DummyFigure:
    '''Dummy Figure class that does nothing'''
    def add_trace(self, *args, **kwargs):
        pass
    def update_layout(self, *args, **kwargs):
        pass
    def update_xaxes(self, *args, **kwargs):
        pass
    def update_yaxes(self, *args, **kwargs):
        pass
    def show(self, *args, **kwargs):
        pass

class _DummyPlotly:
    '''Dummy plotly.express replacement'''
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

class _DummyGO:
    '''Dummy plotly.graph_objects replacement'''
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

# Create dummy objects
px = _DummyPlotly()
go = _DummyGO()


# Page config
st.set_page_config(
    page_title="Symantec EDR Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS styling
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
        <span style="font-size: 2.5rem;">🛡️</span> Symantec EDR Dashboard
    </h1>
    <p style="text-align: center; margin: 0.75rem 0 0 0; opacity: 0.9; position: relative; z-index: 1; font-size: 1.1rem;">
        Group Information Security - Endpoint Detection & Response
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #0a3d62, #1e5f8e); border-radius: 12px; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(10, 61, 98, 0.2);">
        <h2 style="color: white; margin: 0; font-size: 1.5rem;">🏢 GenericCorp</h2>
        <p style="color: #e8f0f8; font-size: 0.95rem; margin-top: 0.5rem;">Endpoint Protection</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filters
    st.header("📊 Dashboard Filters")
    
    # OPCO filter
    opco_filter = st.multiselect(
        "OPCO Selection",
        ["All", "Americas", "Europe", "APAC"],
        default=["All"],
        help="Filter by operating company"
    )
    
    # Risk level filter
    risk_filter = st.multiselect(
        "Risk Levels",
        ["Critical", "High", "Medium", "Low"],
        default=["Critical", "High"],
        help="Filter by risk level"
    )
    
    # Date range
    date_range = st.selectbox(
        "Time Period",
        ["Last 7 Days", "Last 30 Days", "Last 90 Days"],
        index=1,
        help="Select time range"
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
    - EDR Coverage
    - Endpoint Health
    - Threat Detection
    - Ransomware Protection
    - Risk Assessment
    """)

# Data loading
@st.cache_data(ttl=300)
def load_data(query):
    try:
        return session.sql(query).to_pandas()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Load data
coverage_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_SYMANTEC_EDR_COVERAGE ORDER BY SNAPSHOT_DATE DESC"
health_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_SYMANTEC_ENDPOINT_HEALTH ORDER BY SNAPSHOT_DATE DESC"
risk_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_SYMANTEC_HIGH_RISK_ENDPOINTS ORDER BY SNAPSHOT_DATE DESC"
ransomware_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_SYMANTEC_RANSOMWARE_TIMELINE ORDER BY THREAT_DAY DESC"
threat_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_SYMANTEC_THREAT_SUMMARY ORDER BY SNAPSHOT_DATE DESC"

df_coverage = load_data(coverage_query)
df_health = load_data(health_query)
df_risk = load_data(risk_query)
df_ransomware = load_data(ransomware_query)
df_threats = load_data(threat_query)

# Calculate KPIs
if not df_coverage.empty:
    total_assets = df_coverage['TOTAL_ASSETS'].sum()
    protected_assets = df_coverage['PROTECTED_ASSETS'].sum()
    avg_coverage = df_coverage['COVERAGE_PCT'].mean()
else:
    total_assets = protected_assets = avg_coverage = 0

if not df_health.empty:
    stale_agents = df_health['STALE_AGENTS'].sum()
    avg_stale_pct = df_health['STALE_PCT'].mean()
else:
    stale_agents = avg_stale_pct = 0

if not df_risk.empty:
    high_risk_count = len(df_risk[df_risk['RISK_LEVEL'].isin(['Critical', 'High'])])
    total_threats = df_risk['THREAT_COUNT_30D'].sum()
else:
    high_risk_count = total_threats = 0

if not df_ransomware.empty:
    ransomware_incidents = df_ransomware['RANSOMWARE_COUNT'].sum()
else:
    ransomware_incidents = 0

# KPIs
st.markdown("### 📊 Executive Summary")

kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)

with kpi_col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{total_assets:,}</div>
        <div class="kpi-label">Total Assets</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{avg_coverage:.1f}%</div>
        <div class="kpi-label">Coverage Rate</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{high_risk_count:,}</div>
        <div class="kpi-label">High Risk</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{stale_agents:,}</div>
        <div class="kpi-label">Stale Agents</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{total_threats:,}</div>
        <div class="kpi-label">Threats (30d)</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col6:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{ransomware_incidents:,}</div>
        <div class="kpi-label">Ransomware</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🛡️ Coverage Overview",
    "💻 Endpoint Health",
    "⚠️ High Risk Endpoints",
    "🔒 Ransomware Protection",
    "📈 Threat Analysis",
    "📊 OPCO Analysis"
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

# Tab 1: Coverage
with tab1:
    st.markdown("### EDR Coverage Analysis")
    
    if not df_coverage.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Protected Assets", f"{protected_assets:,}")
        with col2:
            st.metric("Total Assets", f"{total_assets:,}")
        with col3:
            coverage_pct = (protected_assets/total_assets*100) if total_assets > 0 else 0
            st.metric("Coverage %", f"{coverage_pct:.1f}%")
        with col4:
            gap = total_assets - protected_assets
            st.metric("Coverage Gap", f"{gap:,}", f"-{gap}")
        
        # Coverage by OPCO
        col1, col2 = st.columns(2)
        
        with col1:
            fig_coverage = px.bar(
                df_coverage,
                x='OPCO',
                y='COVERAGE_PCT',
                title='Coverage by OPCO',
                color='COVERAGE_PCT',
                color_continuous_scale=[colors['danger'], colors['warning'], colors['success']]
            )
            fig_coverage.add_hline(y=95, line_dash="dash", line_color=colors['primary'],
                                  annotation_text="Target: 95%")
            fig_coverage.update_layout(plot_bgcolor='white')
            if fig: st.info("Chart not available in Snowflake - view data in table") # st.plotly_chart(fig_coverage, use_container_width=True)
        
        with col2:
            # Coverage gauge
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = avg_coverage,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Overall Coverage"},
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
            if fig: st.info("Chart not available in Snowflake - view data in table") # st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Assets distribution
        st.markdown("### Assets Distribution by OPCO")
        
        fig_assets = go.Figure()
        fig_assets.add_trace(go.Bar(
            x=df_coverage['OPCO'],
            y=df_coverage['PROTECTED_ASSETS'],
            name='Protected',
            marker_color=colors['success']
        ))
        fig_assets.add_trace(go.Bar(
            x=df_coverage['OPCO'],
            y=df_coverage['TOTAL_ASSETS'] - df_coverage['PROTECTED_ASSETS'],
            name='Unprotected',
            marker_color=colors['danger']
        ))
        fig_assets.update_layout(
            barmode='stack',
            title='Protected vs Unprotected Assets',
            xaxis_title='OPCO',
            yaxis_title='Assets',
            plot_bgcolor='white'
        )
        if fig: st.info("Chart not available in Snowflake - view data in table") # st.plotly_chart(fig_assets, use_container_width=True)

# Tab 2: Endpoint Health
with tab2:
    st.markdown("### Endpoint Health Status")
    
    if not df_health.empty:
        # Health metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_endpoints = df_health['ENDPOINT_COUNT'].sum()
        avg_days_scan = df_health['AVG_DAYS_SINCE_SCAN'].mean()
        
        with col1:
            st.metric("Total Endpoints", f"{total_endpoints:,}")
        with col2:
            st.metric("Stale Agents", f"{stale_agents:,}")
        with col3:
            st.metric("Avg Stale %", f"{avg_stale_pct:.1f}%")
        with col4:
            st.metric("Avg Days Since Scan", f"{avg_days_scan:.1f}")
        
        # Security status distribution
        col1, col2 = st.columns(2)
        
        with col1:
            status_summary = df_health.groupby('DEVICE_SECURITY_STATUS')['ENDPOINT_COUNT'].sum()
            fig_status = px.pie(
                values=status_summary.values,
                names=status_summary.index,
                title='Device Security Status',
                color_discrete_map={
                    'Secured': colors['success'],
                    'At Risk': colors['warning'],
                    'Critical': colors['danger'],
                    'Unknown': 'gray'
                }
            )
            fig_status.update_layout(plot_bgcolor='white')
            if fig: st.info("Chart not available in Snowflake - view data in table") # st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            # Stale agents by OPCO
            fig_stale = px.bar(
                df_health,
                x='OPCO',
                y='STALE_PCT',
                title='Stale Agent Percentage by OPCO',
                color='STALE_PCT',
                color_continuous_scale='Reds'
            )
            fig_stale.add_hline(y=5, line_dash="dash", line_color='red',
                               annotation_text="Threshold: 5%")
            fig_stale.update_layout(plot_bgcolor='white')
            if fig: st.info("Chart not available in Snowflake - view data in table") # st.plotly_chart(fig_stale, use_container_width=True)
        
        # Health details table
        st.markdown("### Health Status Details")
        display_df = df_health[['OPCO', 'DEVICE_SECURITY_STATUS', 'ENDPOINT_COUNT', 
                               'AVG_DAYS_SINCE_SCAN', 'STALE_AGENTS', 'STALE_PCT']]
        st.dataframe(
            display_df.style.format({
                'STALE_PCT': '{:.1f}%',
                'AVG_DAYS_SINCE_SCAN': '{:.1f}'
            }).background_gradient(subset=['STALE_PCT'], cmap='Reds'),
            use_container_width=True
        )

# Tab 3: High Risk
with tab3:
    st.markdown("### High Risk Endpoints")
    
    if not df_risk.empty:
        # Risk overview
        risk_levels = df_risk['RISK_LEVEL'].value_counts()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            critical_count = risk_levels.get('Critical', 0)
            st.metric("Critical Risk", f"{critical_count:,}")
        with col2:
            high_count = risk_levels.get('High', 0)
            st.metric("High Risk", f"{high_count:,}")
        with col3:
            recent_threats = df_risk['LATEST_THREAT'].notna().sum()
            st.metric("Recent Threats", f"{recent_threats:,}")
        
        # Risk distribution
        col1, col2 = st.columns(2)
        
        with col1:
            fig_risk = px.bar(
                x=risk_levels.index,
                y=risk_levels.values,
                title='Risk Level Distribution',
                color=risk_levels.index,
                color_discrete_map={
                    'Critical': colors['danger'],
                    'High': '#e67e22',
                    'Medium': colors['warning'],
                    'Low': colors['info']
                },
                labels={'x': 'Risk Level', 'y': 'Count'}
            )
            fig_risk.update_layout(plot_bgcolor='white', showlegend=False)
            if fig: st.info("Chart not available in Snowflake - view data in table") # st.plotly_chart(fig_risk, use_container_width=True)
        
        with col2:
            # Threats by OPCO
            threats_by_opco = df_risk.groupby('OPCO')['THREAT_COUNT_30D'].sum()
            fig_threats = px.pie(
                values=threats_by_opco.values,
                names=threats_by_opco.index,
                title='Threats by OPCO (30 days)',
                color_discrete_sequence=px.colors.sequential.Reds
            )
            fig_threats.update_layout(plot_bgcolor='white')
            if fig: st.info("Chart not available in Snowflake - view data in table") # st.plotly_chart(fig_threats, use_container_width=True)
        
        # Critical endpoints table
        st.markdown("### Critical Risk Endpoints")
        critical_df = df_risk[df_risk['RISK_LEVEL'].isin(['Critical', 'High'])].copy()
        
        if not critical_df.empty:
            # Convert dates for display
            for col in ['LAST_SCAN_TIME', 'LAST_UPDATE_TIME']:
                if col in critical_df.columns:
                    critical_df[col] = pd.to_datetime(critical_df[col]).dt.strftime('%Y-%m-%d')
            
            display_cols = ['COMPUTER_NAME', 'OPCO', 'DEVICE_SECURITY_STATUS', 
                          'THREAT_COUNT_30D', 'RISK_LEVEL', 'LAST_SCAN_TIME']
            
            st.dataframe(
                critical_df[display_cols].head(20).style.apply(
                    lambda x: ['background-color: #ffeef0' if x['RISK_LEVEL'] == 'Critical' 
                              else 'background-color: #fff4e6' if x['RISK_LEVEL'] == 'High'
                              else '' for _ in x], axis=1
                ),
                use_container_width=True
            )

# Tab 4: Ransomware
with tab4:
    st.markdown("### Ransomware Protection Status")
    
    if not df_ransomware.empty:
        # Ransomware metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_incidents = df_ransomware['RANSOMWARE_COUNT'].sum()
        recent_incidents = df_ransomware[df_ransomware['DAYS_SINCE_LAST'] <= 7]['RANSOMWARE_COUNT'].sum()
        avg_days_since = df_ransomware['DAYS_SINCE_LAST'].min()
        affected_opcos = df_ransomware['OPCO'].nunique()
        
        with col1:
            st.metric("Total Incidents", f"{total_incidents:,}")
        with col2:
            st.metric("Recent (7d)", f"{recent_incidents:,}")
        with col3:
            st.metric("Days Since Last", f"{avg_days_since}")
        with col4:
            st.metric("Affected OPCOs", f"{affected_opcos}")
        
        # Timeline
        st.markdown("### Ransomware Detection Timeline")
        
        # Convert date for display
        df_ransomware['THREAT_DAY'] = pd.to_datetime(df_ransomware['THREAT_DAY'])
        
        fig_timeline = px.line(
            df_ransomware.groupby('THREAT_DAY')['RANSOMWARE_COUNT'].sum().reset_index(),
            x='THREAT_DAY',
            y='RANSOMWARE_COUNT',
            title='Ransomware Incidents Over Time',
            markers=True
        )
        fig_timeline.update_traces(
            line_color=colors['danger'],
            marker_color=colors['danger']
        )
        fig_timeline.update_layout(
            plot_bgcolor='white',
            xaxis_title='Date',
            yaxis_title='Incident Count'
        )
        if fig: st.info("Chart not available in Snowflake - view data in table") # st.plotly_chart(fig_timeline, use_container_width=True)
        
        # By OPCO
        col1, col2 = st.columns(2)
        
        with col1:
            opco_ransomware = df_ransomware.groupby('OPCO')['RANSOMWARE_COUNT'].sum()
            fig_opco = px.bar(
                x=opco_ransomware.index,
                y=opco_ransomware.values,
                title='Ransomware by OPCO',
                color=opco_ransomware.values,
                color_continuous_scale='Reds',
                labels={'x': 'OPCO', 'y': 'Count'}
            )
            fig_opco.update_layout(plot_bgcolor='white', showlegend=False)
            if fig: st.info("Chart not available in Snowflake - view data in table") # st.plotly_chart(fig_opco, use_container_width=True)
        
        with col2:
            # Days since last incident
            last_incident = df_ransomware.groupby('OPCO')['DAYS_SINCE_LAST'].min()
            fig_days = px.bar(
                x=last_incident.index,
                y=last_incident.values,
                title='Days Since Last Incident',
                color=last_incident.values,
                color_continuous_scale='RdYlGn',
                labels={'x': 'OPCO', 'y': 'Days'}
            )
            fig_days.update_layout(plot_bgcolor='white', showlegend=False)
            if fig: st.info("Chart not available in Snowflake - view data in table") # st.plotly_chart(fig_days, use_container_width=True)

# Tab 5: Threat Analysis
with tab5:
    st.markdown("### Threat Analysis")
    
    if not df_threats.empty:
        # Threat summary
        total_threat_count = df_threats['THREAT_COUNT'].sum()
        affected_endpoints = df_threats['AFFECTED_ENDPOINTS'].sum()
        threat_types = df_threats['THREAT_TYPE'].nunique()
        avg_detection_time = df_threats['AVG_HOURS_SINCE_DETECTION'].mean()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Threats", f"{total_threat_count:,}")
        with col2:
            st.metric("Affected Endpoints", f"{affected_endpoints:,}")
        with col3:
            st.metric("Threat Types", f"{threat_types}")
        with col4:
            st.metric("Avg Detection Time", f"{avg_detection_time:.1f}h")
        
        # Threats by type
        col1, col2 = st.columns(2)
        
        with col1:
            threat_by_type = df_threats.groupby('THREAT_TYPE')['THREAT_COUNT'].sum().sort_values(ascending=False)
            fig_types = px.bar(
                x=threat_by_type.values[:10],
                y=threat_by_type.index[:10],
                orientation='h',
                title='Top 10 Threat Types',
                color=threat_by_type.values[:10],
                color_continuous_scale='Reds',
                labels={'x': 'Count', 'y': 'Threat Type'}
            )
            fig_types.update_layout(plot_bgcolor='white', showlegend=False)
            if fig: st.info("Chart not available in Snowflake - view data in table") # st.plotly_chart(fig_types, use_container_width=True)
        
        with col2:
            # Detection time by threat type
            detection_times = df_threats.groupby('THREAT_TYPE')['AVG_HOURS_SINCE_DETECTION'].mean().sort_values()
            fig_detection = px.bar(
                x=detection_times.values[:10],
                y=detection_times.index[:10],
                orientation='h',
                title='Fastest Detection Times',
                color=detection_times.values[:10],
                color_continuous_scale='Greens',
                labels={'x': 'Hours', 'y': 'Threat Type'}
            )
            fig_detection.update_layout(plot_bgcolor='white', showlegend=False)
            if fig: st.info("Chart not available in Snowflake - view data in table") # st.plotly_chart(fig_detection, use_container_width=True)
        
        # Threat details
        st.markdown("### Threat Details")
        display_df = df_threats[['THREAT_TYPE', 'OPCO', 'THREAT_COUNT', 
                                'AFFECTED_ENDPOINTS', 'AVG_HOURS_SINCE_DETECTION']]
        st.dataframe(
            display_df.sort_values('THREAT_COUNT', ascending=False).head(20).style.format({
                'AVG_HOURS_SINCE_DETECTION': '{:.1f}h'
            }),
            use_container_width=True
        )

# Tab 6: OPCO Analysis
with tab6:
    st.markdown("### OPCO Performance Analysis")
    
    if not df_coverage.empty and not df_health.empty:
        # OPCO comparison
        opco_metrics = pd.DataFrame()
        
        if not df_coverage.empty:
            coverage_metrics = df_coverage.groupby('OPCO').agg({
                'COVERAGE_PCT': 'mean',
                'PROTECTED_ASSETS': 'sum',
                'TOTAL_ASSETS': 'sum'
            })
            opco_metrics = coverage_metrics
        
        if not df_health.empty:
            health_metrics = df_health.groupby('OPCO').agg({
                'STALE_PCT': 'mean',
                'ENDPOINT_COUNT': 'sum'
            })
            opco_metrics = opco_metrics.join(health_metrics, how='outer')
        
        if not df_risk.empty:
            risk_metrics = df_risk.groupby('OPCO')['THREAT_COUNT_30D'].sum()
            opco_metrics = opco_metrics.join(risk_metrics, how='outer')
        
        # Metrics overview
        st.markdown("### OPCO Scorecard")
        
        for opco in opco_metrics.index[:5]:  # Top 5 OPCOs
            col1, col2, col3, col4, col5 = st.columns(5)
            
            metrics = opco_metrics.loc[opco]
            
            with col1:
                st.metric(f"{opco}", "")
            with col2:
                coverage = metrics.get('COVERAGE_PCT', 0)
                st.metric("Coverage", f"{coverage:.1f}%")
            with col3:
                stale = metrics.get('STALE_PCT', 0)
                st.metric("Stale %", f"{stale:.1f}%")
            with col4:
                endpoints = metrics.get('ENDPOINT_COUNT', 0)
                st.metric("Endpoints", f"{int(endpoints):,}")
            with col5:
                threats = metrics.get('THREAT_COUNT_30D', 0)
                st.metric("Threats", f"{int(threats):,}")
        
        # Comparison chart
        st.markdown("### OPCO Comparison")
        
        fig_comparison = go.Figure()
        
        # Normalize metrics for comparison
        if 'COVERAGE_PCT' in opco_metrics.columns:
            fig_comparison.add_trace(go.Bar(
                x=opco_metrics.index,
                y=opco_metrics['COVERAGE_PCT'],
                name='Coverage %',
                marker_color=colors['success']
            ))
        
        if 'STALE_PCT' in opco_metrics.columns:
            fig_comparison.add_trace(go.Bar(
                x=opco_metrics.index,
                y=opco_metrics['STALE_PCT'],
                name='Stale %',
                marker_color=colors['danger']
            ))
        
        fig_comparison.update_layout(
            title='OPCO Key Metrics Comparison',
            xaxis_title='OPCO',
            yaxis_title='Percentage',
            barmode='group',
            plot_bgcolor='white'
        )
        
        if fig: st.info("Chart not available in Snowflake - view data in table") # st.plotly_chart(fig_comparison, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1rem;">
    <p><strong>Symantec EDR Dashboard</strong> | Endpoint Detection & Response</p>
    <p>Group Information Security - Analytics Group</p>
    <p style="font-size: 0.85rem;">© 2025 GenericCorp Corporation. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)