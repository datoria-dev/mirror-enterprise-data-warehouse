# Import packages
import streamlit as st
import pandas as pd
# import plotly.express as px  # Not available in Snowflake
# import plotly.graph_objects as go  # Not available in Snowflake
from plotly.subplots import make_subplots
from snowflake.snowpark.context import get_active_session
from datetime import datetime, timedelta
# import numpy as np  # Not available in Snowflake

# Page config
st.set_page_config(
    page_title="Trellix EDR Dashboard",
    page_icon="🔰",
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
        <span style="font-size: 2.5rem;">🔰</span> Trellix EDR Dashboard
    </h1>
    <p style="text-align: center; margin: 0.75rem 0 0 0; opacity: 0.9; position: relative; z-index: 1; font-size: 1.1rem;">
        Group Information Security - Endpoint Detection & Response Platform
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #0a3d62, #1e5f8e); border-radius: 12px; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(10, 61, 98, 0.2);">
        <h2 style="color: white; margin: 0; font-size: 1.5rem;">🏢 GenericCorp</h2>
        <p style="color: #e8f0f8; font-size: 0.95rem; margin-top: 0.5rem;">Trellix Security Platform</p>
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
    
    # OS filter
    os_filter = st.multiselect(
        "Operating System",
        ["Windows", "Linux", "Mac", "All"],
        default=["All"],
        help="Filter by OS type"
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
    - Agent Health
    - AMCore Compliance
    - Communication Status
    - EDR Coverage
    - Security Alerts
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
agent_health_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_TRELLIX_AGENT_HEALTH ORDER BY SNAPSHOT_DATE DESC"
amcore_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_TRELLIX_AMCORE_COMPLIANCE ORDER BY SNAPSHOT_DATE DESC"
comm_status_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_TRELLIX_COMMUNICATION_STATUS ORDER BY SNAPSHOT_DATE DESC"
coverage_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_TRELLIX_EDR_COVERAGE ORDER BY SNAPSHOT_DATE DESC"
alerts_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_TRELLIX_SECURITY_ALERTS ORDER BY SNAPSHOT_DATE DESC"

df_agent = load_data(agent_health_query)
df_amcore = load_data(amcore_query)
df_comm = load_data(comm_status_query)
df_coverage = load_data(coverage_query)
df_alerts = load_data(alerts_query)

# Calculate KPIs
if not df_coverage.empty:
    total_endpoints = df_coverage['TOTAL_ENDPOINTS'].sum()
    active_endpoints = df_coverage['ACTIVE_ENDPOINTS'].sum()
    coverage_pct = (active_endpoints/total_endpoints*100) if total_endpoints > 0 else 0
else:
    total_endpoints = active_endpoints = coverage_pct = 0

if not df_agent.empty:
    updated_agents = df_agent['UPDATED_AGENTS'].sum()
    avg_update_pct = df_agent['UPDATE_PCT'].mean() if not df_agent['UPDATE_PCT'].isna().all() else 0
else:
    updated_agents = avg_update_pct = 0

if not df_comm.empty:
    active_24h = df_comm['ACTIVE_24H'].sum()
    stale_7d = df_comm['STALE_7D'].sum()
else:
    active_24h = stale_7d = 0

if not df_amcore.empty:
    outdated_endpoints = df_amcore['OUTDATED_COUNT'].sum()
else:
    outdated_endpoints = 0

# KPIs
st.markdown("### 📊 Executive Summary")

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
        <div class="kpi-value">{coverage_pct:.1f}%</div>
        <div class="kpi-label">Coverage Rate</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{active_24h:,}</div>
        <div class="kpi-label">Active (24h)</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{stale_7d:,}</div>
        <div class="kpi-label">Stale (7d)</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{avg_update_pct:.1f}%</div>
        <div class="kpi-label">Update Rate</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col6:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{outdated_endpoints:,}</div>
        <div class="kpi-label">Outdated</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔰 EDR Coverage",
    "💊 Agent Health",
    "📡 Communication Status",
    "🔄 AMCore Compliance",
    "⚠️ Security Alerts",
    "📈 OPCO Analysis"
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

# Tab 1: EDR Coverage
with tab1:
    st.markdown("### EDR Coverage Overview")
    
    if not df_coverage.empty:
        # Coverage metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Active Endpoints", f"{active_endpoints:,}")
        with col2:
            st.metric("Total Endpoints", f"{total_endpoints:,}")
        with col3:
            gap = total_endpoints - active_endpoints
            st.metric("Coverage Gap", f"{gap:,}", f"-{gap}")
        with col4:
            st.metric("Coverage %", f"{coverage_pct:.1f}%")
        
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
            # fig.update_layout(  # Plotly not availableplot_bgcolor='white')
            st.info("Interactive chart not available in Snowflake - view data in table below")
        
        with col2:
            # Coverage gauge
            # fig = go.Figure(  # Plotly not availablego.Indicator(
                mode = "gauge+number+delta",
                value = coverage_pct,
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
            # fig.update_layout(  # Plotly not availableheight=400, paper_bgcolor='white')
            st.info("Interactive chart not available in Snowflake - view data in table below")
        
        # Endpoint distribution
        st.markdown("### Endpoint Distribution")
        
        # fig = go.Figure(  # Plotly not available)
        # fig.add_trace(  # Plotly not availablego.Bar(
            x=df_coverage['OPCO'],
            y=df_coverage['ACTIVE_ENDPOINTS'],
            name='Active',
            marker_color=colors['success']
        ))
        # fig.add_trace(  # Plotly not availablego.Bar(
            x=df_coverage['OPCO'],
            y=df_coverage['TOTAL_ENDPOINTS'] - df_coverage['ACTIVE_ENDPOINTS'],
            name='Inactive',
            marker_color=colors['danger']
        ))
        # fig.update_layout(  # Plotly not available
            barmode='stack',
            title='Active vs Inactive Endpoints',
            plot_bgcolor='white'
        )
        st.info("Interactive chart not available in Snowflake - view data in table below")

# Tab 2: Agent Health
with tab2:
    st.markdown("### Agent Health Monitoring")
    
    if not df_agent.empty:
        # Health metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_agents = df_agent['TOTAL_AGENTS'].sum()
        median_days = df_agent['MEDIAN_DAYS_OUTDATED'].median() if not df_agent['MEDIAN_DAYS_OUTDATED'].isna().all() else 0
        
        with col1:
            st.metric("Total Agents", f"{total_agents:,}")
        with col2:
            st.metric("Updated Agents", f"{updated_agents:,}")
        with col3:
            st.metric("Update Rate", f"{avg_update_pct:.1f}%")
        with col4:
            days_display = f"{median_days:.0f}" if median_days > 0 else "N/A"
            st.metric("Median Days Outdated", days_display)
        
        # Update status by OPCO
        col1, col2 = st.columns(2)
        
        with col1:
            fig_update = px.bar(
                df_agent.sort_values('UPDATE_PCT'),
                x='UPDATE_PCT',
                y='OPCO',
                orientation='h',
                title='Agent Update Rate by OPCO',
                color='UPDATE_PCT',
                color_continuous_scale=[colors['danger'], colors['warning'], colors['success']]
            )
            fig_update.add_vline(x=90, line_dash="dash", line_color=colors['primary'],
                               annotation_text="Target: 90%")
            # fig.update_layout(  # Plotly not availableplot_bgcolor='white')
            st.info("Interactive chart not available in Snowflake - view data in table below")
        
        with col2:
            # Days outdated distribution
            fig_days = px.box(
                df_agent,
                y='MEDIAN_DAYS_OUTDATED',
                x='OPCO',
                title='Days Since Update Distribution',
                color_discrete_sequence=[colors['primary']]
            )
            # fig.update_layout(  # Plotly not availableplot_bgcolor='white')
            st.info("Interactive chart not available in Snowflake - view data in table below")
        
        # Agent health details
        st.markdown("### Agent Health Details")
        st.dataframe(
            df_agent[['OPCO', 'UPDATED_AGENTS', 'TOTAL_AGENTS', 'UPDATE_PCT', 
                     'MEDIAN_DAYS_OUTDATED']].style.format({
                'UPDATE_PCT': '{:.1f}%',
                'MEDIAN_DAYS_OUTDATED': '{:.1f}'
            }).background_gradient(subset=['UPDATE_PCT'], cmap='RdYlGn'),
            use_container_width=True
        )

# Tab 3: Communication Status
with tab3:
    st.markdown("### Communication Status Monitoring")
    
    if not df_comm.empty:
        # Communication metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_comm_endpoints = df_comm['ENDPOINT_COUNT'].sum()
        active_7d = df_comm['ACTIVE_7D'].sum()
        max_inactive = df_comm['MAX_DAYS_INACTIVE'].max() if not df_comm['MAX_DAYS_INACTIVE'].isna().all() else 0
        
        with col1:
            st.metric("Total Endpoints", f"{total_comm_endpoints:,}")
        with col2:
            st.metric("Active (24h)", f"{active_24h:,}")
        with col3:
            st.metric("Active (7d)", f"{active_7d:,}")
        with col4:
            st.metric("Max Days Inactive", f"{max_inactive}")
        
        # Communication by OS Type
        col1, col2 = st.columns(2)
        
        with col1:
            os_summary = df_comm.groupby('OS_TYPE').agg({
                'ENDPOINT_COUNT': 'sum',
                'ACTIVE_24H': 'sum'
            }).reset_index()
            os_summary['ACTIVE_PCT'] = (os_summary['ACTIVE_24H'] / os_summary['ENDPOINT_COUNT'] * 100)
            
            fig_os = px.bar(
                os_summary,
                x='OS_TYPE',
                y='ACTIVE_PCT',
                title='Active Rate by OS Type (24h)',
                color='ACTIVE_PCT',
                color_continuous_scale='Greens'
            )
            # fig.update_layout(  # Plotly not availableplot_bgcolor='white')
            st.info("Interactive chart not available in Snowflake - view data in table below")
        
        with col2:
            # Stale endpoints
            fig_stale = px.scatter(
                df_comm,
                x='ENDPOINT_COUNT',
                y='STALE_7D',
                size='MAX_DAYS_INACTIVE',
                color='OPCO',
                title='Stale Endpoints Analysis',
                labels={'STALE_7D': 'Stale Endpoints (7d)', 'ENDPOINT_COUNT': 'Total Endpoints'}
            )
            # fig.update_layout(  # Plotly not availableplot_bgcolor='white')
            st.info("Interactive chart not available in Snowflake - view data in table below")
        
        # Activity timeline
        st.markdown("### Activity Distribution")
        
        activity_data = pd.DataFrame({
            'Status': ['Active (24h)', 'Active (7d)', 'Stale (>7d)'],
            'Count': [active_24h, active_7d - active_24h, stale_7d]
        })
        
        fig_activity = px.pie(
            activity_data,
            values='Count',
            names='Status',
            title='Endpoint Activity Status',
            color_discrete_map={
                'Active (24h)': colors['success'],
                'Active (7d)': colors['info'],
                'Stale (>7d)': colors['danger']
            }
        )
        # fig.update_layout(  # Plotly not availableplot_bgcolor='white')
        st.info("Interactive chart not available in Snowflake - view data in table below")

# Tab 4: AMCore Compliance
with tab4:
    st.markdown("### AMCore Compliance Status")
    
    if not df_amcore.empty:
        # Compliance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_amcore_endpoints = df_amcore['ENDPOINT_COUNT'].sum()
        avg_outdated_pct = df_amcore['OUTDATED_PCT'].mean() if not df_amcore['OUTDATED_PCT'].isna().all() else 0
        major_versions = df_amcore['MAJOR_VERSION'].nunique()
        
        with col1:
            st.metric("Total Endpoints", f"{total_amcore_endpoints:,}")
        with col2:
            st.metric("Outdated Endpoints", f"{outdated_endpoints:,}")
        with col3:
            st.metric("Avg Outdated %", f"{avg_outdated_pct:.1f}%")
        with col4:
            st.metric("Major Versions", f"{major_versions}")
        
        # Version distribution
        col1, col2 = st.columns(2)
        
        with col1:
            version_summary = df_amcore.groupby('MAJOR_VERSION').agg({
                'ENDPOINT_COUNT': 'sum',
                'OUTDATED_COUNT': 'sum'
            }).reset_index()
            
            # fig = go.Figure(  # Plotly not available)
            # fig.add_trace(  # Plotly not availablego.Bar(
                x=version_summary['MAJOR_VERSION'],
                y=version_summary['ENDPOINT_COUNT'] - version_summary['OUTDATED_COUNT'],
                name='Current',
                marker_color=colors['success']
            ))
            # fig.add_trace(  # Plotly not availablego.Bar(
                x=version_summary['MAJOR_VERSION'],
                y=version_summary['OUTDATED_COUNT'],
                name='Outdated',
                marker_color=colors['danger']
            ))
            # fig.update_layout(  # Plotly not available
                barmode='stack',
                title='Version Distribution',
                xaxis_title='Major Version',
                yaxis_title='Endpoint Count',
                plot_bgcolor='white'
            )
            st.info("Interactive chart not available in Snowflake - view data in table below")
        
        with col2:
            # Outdated percentage by OPCO
            opco_outdated = df_amcore.groupby('OPCO')['OUTDATED_PCT'].mean().sort_values()
            
            fig_outdated = px.bar(
                x=opco_outdated.values,
                y=opco_outdated.index,
                orientation='h',
                title='Outdated Percentage by OPCO',
                color=opco_outdated.values,
                color_continuous_scale='Reds',
                labels={'x': 'Outdated %', 'y': 'OPCO'}
            )
            # fig.update_layout(  # Plotly not availableplot_bgcolor='white', showlegend=False)
            st.info("Interactive chart not available in Snowflake - view data in table below")
        
        # Version timeline
        st.markdown("### Version Age Analysis")
        
        # Convert dates for display
        df_amcore_display = df_amcore.copy()
        for col in ['OLDEST_VERSION_DATE', 'NEWEST_VERSION_DATE']:
            if col in df_amcore_display.columns:
                df_amcore_display[col] = pd.to_datetime(df_amcore_display[col])
                df_amcore_display[f'{col}_STR'] = df_amcore_display[col].dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            df_amcore_display[['OPCO', 'MAJOR_VERSION', 'ENDPOINT_COUNT', 
                              'OUTDATED_COUNT', 'OUTDATED_PCT']].style.format({
                'OUTDATED_PCT': '{:.1f}%'
            }).background_gradient(subset=['OUTDATED_PCT'], cmap='Reds'),
            use_container_width=True
        )

# Tab 5: Security Alerts
with tab5:
    st.markdown("### Security Alerts")
    
    if not df_alerts.empty:
        # Alert metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_alerts = len(df_alerts)
        unique_systems = df_alerts['SYSTEM_NAME'].nunique()
        alert_types = df_alerts['ALERT_TYPE'].nunique()
        
        # Calculate average days
        avg_days_comm = df_alerts['DAYS_SINCE_COMM'].mean() if not df_alerts['DAYS_SINCE_COMM'].isna().all() else 0
        
        with col1:
            st.metric("Total Alerts", f"{total_alerts:,}")
        with col2:
            st.metric("Affected Systems", f"{unique_systems:,}")
        with col3:
            st.metric("Alert Types", f"{alert_types}")
        with col4:
            st.metric("Avg Days Since Comm", f"{avg_days_comm:.0f}")
        
        # Alerts by type
        col1, col2 = st.columns(2)
        
        with col1:
            alert_type_counts = df_alerts['ALERT_TYPE'].value_counts()
            
            fig_alert_types = px.pie(
                values=alert_type_counts.values,
                names=alert_type_counts.index,
                title='Alert Type Distribution',
                color_discrete_sequence=px.colors.sequential.Reds
            )
            # fig.update_layout(  # Plotly not availableplot_bgcolor='white')
            st.info("Interactive chart not available in Snowflake - view data in table below")
        
        with col2:
            # Alerts by OPCO
            opco_alerts = df_alerts['OPCO'].value_counts()
            
            fig_opco_alerts = px.bar(
                x=opco_alerts.index,
                y=opco_alerts.values,
                title='Alerts by OPCO',
                color=opco_alerts.values,
                color_continuous_scale='Reds',
                labels={'x': 'OPCO', 'y': 'Alert Count'}
            )
            # fig.update_layout(  # Plotly not availableplot_bgcolor='white', showlegend=False)
            st.info("Interactive chart not available in Snowflake - view data in table below")
        
        # Critical alerts table
        st.markdown("### Recent Critical Alerts")
        
        # Convert dates for display
        df_alerts_display = df_alerts.copy()
        for col in ['LAST_COMMUNICATION', 'AMCORE_DATE']:
            if col in df_alerts_display.columns:
                df_alerts_display[col] = pd.to_datetime(df_alerts_display[col]).dt.strftime('%Y-%m-%d')
        
        display_cols = ['SYSTEM_NAME', 'OPCO', 'OS_TYPE', 'DAYS_SINCE_COMM', 
                       'ALERT_TYPE', 'ALERT_DESCRIPTION']
        
        st.dataframe(
            df_alerts_display[display_cols].head(20).style.apply(
                lambda x: ['background-color: #ffeef0' if x['DAYS_SINCE_COMM'] > 30 
                          else 'background-color: #fff4e6' if x['DAYS_SINCE_COMM'] > 7
                          else '' for _ in x], axis=1
            ),
            use_container_width=True
        )

# Tab 6: OPCO Analysis - FIXED VERSION
with tab6:
    st.markdown("### OPCO Performance Analysis")
    
    # Debug section - uncomment to see raw data
    with st.expander("🔍 Debug: View Raw Data"):
        st.write("Coverage Data Sample:")
        if not df_coverage.empty:
            st.write(df_coverage[['OPCO', 'COVERAGE_PCT', 'ACTIVE_ENDPOINTS']].head())
        else:
            st.write("No coverage data")
            
        st.write("Agent Data Sample:")
        if not df_agent.empty:
            st.write(df_agent[['OPCO', 'UPDATE_PCT', 'MEDIAN_DAYS_OUTDATED']].head())
        else:
            st.write("No agent data")
            
        st.write("Communication Data Sample:")
        if not df_comm.empty:
            st.write(df_comm[['OPCO', 'STALE_7D', 'ENDPOINT_COUNT']].head())
        else:
            st.write("No communication data")
    
    # Create OPCO metrics with better error handling
    opco_metrics = pd.DataFrame()
    
    try:
        # Get unique OPCOs from all dataframes
        all_opcos = set()
        
        if not df_coverage.empty:
            # Clean OPCO names - remove whitespace and standardize case
            df_coverage['OPCO'] = df_coverage['OPCO'].str.strip().str.upper()
            all_opcos.update(df_coverage['OPCO'].unique())
            
        if not df_agent.empty:
            df_agent['OPCO'] = df_agent['OPCO'].str.strip().str.upper()
            all_opcos.update(df_agent['OPCO'].unique())
            
        if not df_comm.empty:
            df_comm['OPCO'] = df_comm['OPCO'].str.strip().str.upper()
            all_opcos.update(df_comm['OPCO'].unique())
        
        # Remove any null or empty OPCO values
        all_opcos = {opco for opco in all_opcos if opco and opco != 'NAN' and opco != ''}
        
        # Create base dataframe with all OPCOs
        opco_metrics = pd.DataFrame(index=sorted(list(all_opcos)))
        
        # Add coverage metrics
        if not df_coverage.empty:
            coverage_metrics = df_coverage.groupby('OPCO').agg({
                'COVERAGE_PCT': 'mean',  # Use mean if multiple records per OPCO
                'ACTIVE_ENDPOINTS': 'sum'
            })
            opco_metrics = opco_metrics.join(coverage_metrics, how='left')
        
        # Add agent metrics
        if not df_agent.empty:
            agent_metrics = df_agent.groupby('OPCO').agg({
                'UPDATE_PCT': 'mean',
                'MEDIAN_DAYS_OUTDATED': 'mean'
            })
            opco_metrics = opco_metrics.join(agent_metrics, how='left')
        
        # Add communication metrics
        if not df_comm.empty:
            comm_summary = df_comm.groupby('OPCO').agg({
                'STALE_7D': 'sum',
                'ENDPOINT_COUNT': 'sum'
            })
            # Calculate stale percentage with zero division check
            comm_summary['STALE_PCT'] = comm_summary.apply(
                lambda x: (x['STALE_7D'] / x['ENDPOINT_COUNT'] * 100) if x['ENDPOINT_COUNT'] > 0 else 0, 
                axis=1
            )
            opco_metrics = opco_metrics.join(comm_summary[['STALE_PCT']], how='left')
        
        # Fill NaN values with 0 for display
        opco_metrics = opco_metrics.fillna(0)
        
        # Debug: Show merged data
        st.write("Debug: Merged OPCO Metrics")
        st.dataframe(opco_metrics.head())
        
    except Exception as e:
        st.error(f"Error processing OPCO metrics: {str(e)}")
        st.write("Debug - Exception details:", e)
    
    # Only proceed if we have data
    if not opco_metrics.empty and len(opco_metrics) > 0:
        # OPCO Scorecard
        st.markdown("### OPCO Scorecard")
        
        # Display up to 5 OPCOs
        for idx, opco in enumerate(opco_metrics.index[:5]):
            if pd.isna(opco) or opco == '':
                continue
                
            metrics = opco_metrics.loc[opco]
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric(f"{opco}", "")
            with col2:
                coverage = float(metrics.get('COVERAGE_PCT', 0))
                st.metric("Coverage", f"{coverage:.1f}%", 
                         delta=f"{coverage-95:.1f}%" if coverage > 0 else None)
            with col3:
                update = float(metrics.get('UPDATE_PCT', 0))
                st.metric("Update Rate", f"{update:.1f}%",
                         delta=f"{update-90:.1f}%" if update > 0 else None)
            with col4:
                stale = float(metrics.get('STALE_PCT', 0))
                st.metric("Stale %", f"{stale:.1f}%",
                         delta=f"-{stale:.1f}%" if stale > 5 else None)
            with col5:
                endpoints = int(metrics.get('ACTIVE_ENDPOINTS', 0))
                st.metric("Active", f"{endpoints:,}")
        
        # Performance Comparison Chart
        st.markdown("### OPCO Performance Comparison")
        
        # fig = go.Figure(  # Plotly not available)
        
        # Add traces only if data exists
        if 'COVERAGE_PCT' in opco_metrics.columns and opco_metrics['COVERAGE_PCT'].sum() > 0:
            # fig.add_trace(  # Plotly not availablego.Bar(
                x=opco_metrics.index,
                y=opco_metrics['COVERAGE_PCT'],
                name='Coverage %',
                marker_color=colors['success'],
                text=opco_metrics['COVERAGE_PCT'].round(1),
                textposition='auto',
            ))
        
        if 'UPDATE_PCT' in opco_metrics.columns and opco_metrics['UPDATE_PCT'].sum() > 0:
            # fig.add_trace(  # Plotly not availablego.Bar(
                x=opco_metrics.index,
                y=opco_metrics['UPDATE_PCT'],
                name='Update %',
                marker_color=colors['info'],
                text=opco_metrics['UPDATE_PCT'].round(1),
                textposition='auto',
            ))
        
        if 'STALE_PCT' in opco_metrics.columns:
            # fig.add_trace(  # Plotly not availablego.Bar(
                x=opco_metrics.index,
                y=opco_metrics['STALE_PCT'],
                name='Stale %',
                marker_color=colors['danger'],
                text=opco_metrics['STALE_PCT'].round(1),
                textposition='auto',
            ))
        
        # fig.update_layout(  # Plotly not available
            title='OPCO Key Metrics',
            barmode='group',
            plot_bgcolor='white',
            showlegend=True,
            yaxis=dict(range=[0, 100])
        )
        st.info("Interactive chart not available in Snowflake - view data in table below")
        
        # Risk Heatmap
        st.markdown("### OPCO Risk Assessment Heatmap")
        
        # Calculate risk scores (0 = good, 100 = bad)
        risk_metrics = pd.DataFrame(index=opco_metrics.index)
        
        # Coverage Risk: Lower coverage = higher risk
        risk_metrics['Coverage Risk'] = 100 - opco_metrics.get('COVERAGE_PCT', 0)
        
        # Update Risk: Lower update rate = higher risk
        risk_metrics['Update Risk'] = 100 - opco_metrics.get('UPDATE_PCT', 0)
        
        # Stale Risk: Higher stale percentage = higher risk
        risk_metrics['Stale Risk'] = opco_metrics.get('STALE_PCT', 0)
        
        # Only create heatmap if we have valid risk data
        if risk_metrics.notna().any().any() and (risk_metrics != 100).any().any():
            # fig = go.Figure(  # Plotly not availabledata=go.Heatmap(
                z=risk_metrics.T.values,
                x=risk_metrics.index,
                y=risk_metrics.columns,
                colorscale=[[0, colors['success']], [0.5, colors['warning']], [1, colors['danger']]],
                text=np.round(risk_metrics.T.values, 1),
                texttemplate="%{text}%",
                textfont={"size": 10},
                colorbar=dict(title="Risk %")
            ))
            
            # fig.update_layout(  # Plotly not available
                title='OPCO Risk Assessment Heatmap (0% = Low Risk, 100% = High Risk)',
                xaxis_title='OPCO',
                yaxis_title='Risk Category',
                plot_bgcolor='white',
                height=400
            )
            st.info("Interactive chart not available in Snowflake - view data in table below")
        else:
            st.warning("⚠️ Insufficient data to generate risk heatmap. Please check data sources.")
    
    else:
        st.error("""
        ### ❌ No OPCO Data Available
        
        The OPCO Analysis cannot be displayed due to missing or invalid data.
        
        **Possible causes:**
        1. Data is not loading from Snowflake views
        2. OPCO field names don't match between tables
        3. No data exists for the selected time period
        
        **Troubleshooting steps:**
        1. Check if data exists in the source views
        2. Verify OPCO naming consistency across tables
        3. Review the debug information above
        """)
    
    # Additional debugging section
    with st.expander("📊 Data Quality Check"):
        st.write("### Data Availability")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Coverage Data:**")
            st.write(f"- Records: {len(df_coverage)}")
            st.write(f"- Unique OPCOs: {df_coverage['OPCO'].nunique() if not df_coverage.empty else 0}")
            
            st.write("**Agent Data:**")
            st.write(f"- Records: {len(df_agent)}")
            st.write(f"- Unique OPCOs: {df_agent['OPCO'].nunique() if not df_agent.empty else 0}")
            
        with col2:
            st.write("**Communication Data:**")
            st.write(f"- Records: {len(df_comm)}")
            st.write(f"- Unique OPCOs: {df_comm['OPCO'].nunique() if not df_comm.empty else 0}")
            
            st.write("**Alerts Data:**")
            st.write(f"- Records: {len(df_alerts)}")
            st.write(f"- Unique OPCOs: {df_alerts['OPCO'].nunique() if not df_alerts.empty else 0}")
        

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1rem;">
    <p><strong>Trellix EDR Dashboard</strong> | Endpoint Detection & Response</p>
    <p>Group Information Security - Data Platform & ETL</p>
    <p style="font-size: 0.85rem;">© 2025 GenericCorp Corporation. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)