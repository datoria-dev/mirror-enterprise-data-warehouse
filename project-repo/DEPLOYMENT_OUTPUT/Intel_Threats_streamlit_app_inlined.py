# Import packages
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from snowflake.snowpark.context import get_active_session
from datetime import datetime, timedelta
import numpy as np

# Page config
st.set_page_config(
    page_title="Threat Intelligence Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
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
        <span style="font-size: 2.5rem;">🎯</span> Threat Intelligence Dashboard
    </h1>
    <p style="text-align: center; margin: 0.75rem 0 0 0; opacity: 0.9; position: relative; z-index: 1; font-size: 1.1rem;">
        Group Information Security - Threat Intelligence & Response Platform
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #0a3d62, #1e5f8e); border-radius: 12px; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(10, 61, 98, 0.2);">
        <h2 style="color: white; margin: 0; font-size: 1.5rem;">🏢 GenericCorp</h2>
        <p style="color: #e8f0f8; font-size: 0.95rem; margin-top: 0.5rem;">Cyber Threat Intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filters
    st.header("📊 Dashboard Filters")
    
    # Source filter
    source_filter = st.multiselect(
        "Intelligence Sources",
        ["All", "Internal", "External", "OSINT"],
        default=["All"],
        help="Filter by intelligence source"
    )
    
    # Asset type filter
    asset_filter = st.multiselect(
        "Asset Types",
        ["Domain", "IP", "URL", "Email", "All"],
        default=["All"],
        help="Filter by asset type"
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
    - Asset Performance
    - Data Quality
    - Source Analysis
    - Takedown Effectiveness
    - Monthly Trends
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
asset_perf_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_THREATINTEL_ASSET_PERFORMANCE ORDER BY SNAPSHOT_DATE DESC"
data_quality_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_THREATINTEL_DATA_QUALITY ORDER BY SNAPSHOT_DATE DESC"
monthly_trends_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_THREATINTEL_MONTHLY_TRENDS ORDER BY SNAPSHOT_DATE DESC"
source_analysis_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_THREATINTEL_SOURCE_ANALYSIS ORDER BY SNAPSHOT_DATE DESC"
takedown_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_THREATINTEL_TAKEDOWN_EFFECTIVENESS ORDER BY SNAPSHOT_DATE DESC"

df_asset_perf = load_data(asset_perf_query)
df_quality = load_data(data_quality_query)
df_trends = load_data(monthly_trends_query)
df_source = load_data(source_analysis_query)
df_takedown = load_data(takedown_query)

# Calculate KPIs
if not df_asset_perf.empty:
    total_events = df_asset_perf['TOTAL'].sum()
    successful_events = df_asset_perf['SUCCESSFUL'].sum()
    overall_success_rate = (successful_events/total_events*100) if total_events > 0 else 0
    # Handle NaN values in resolution time
    valid_resolution_times = df_asset_perf['AVG_RESOLUTION_HOURS_SUCCESS'].dropna()
    avg_resolution_time = valid_resolution_times.mean() if len(valid_resolution_times) > 0 else 0
else:
    total_events = successful_events = overall_success_rate = avg_resolution_time = 0

if not df_source.empty:
    total_sources = df_source['SOURCE'].nunique()
    affected_opcos = df_source['AFFECTED_OPCOS'].max() if not df_source['AFFECTED_OPCOS'].isna().all() else 0
else:
    total_sources = affected_opcos = 0

if not df_trends.empty:
    # Handle verification rate properly
    valid_verification = df_trends['VERIFICATION_RATE'].dropna()
    verification_rate = valid_verification.mean() if len(valid_verification) > 0 else 0
    # Ensure it's within valid percentage range
    verification_rate = min(100, max(0, verification_rate))
else:
    verification_rate = 0

# KPIs
st.markdown("### 📊 Executive Summary")

kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)

with kpi_col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{total_events:,}</div>
        <div class="kpi-label">Total Events</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{overall_success_rate:.1f}%</div>
        <div class="kpi-label">Success Rate</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    # Format resolution time properly
    if avg_resolution_time > 0:
        resolution_display = f"{avg_resolution_time:.1f}h"
    else:
        resolution_display = "N/A"
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{resolution_display}</div>
        <div class="kpi-label">Avg Resolution</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{total_sources:,}</div>
        <div class="kpi-label">Intel Sources</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{affected_opcos:,}</div>
        <div class="kpi-label">Affected OPCOs</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col6:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{verification_rate:.1f}%</div>
        <div class="kpi-label">Verification Rate</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎯 Asset Performance",
    "📊 Data Quality",
    "🔍 Source Analysis",
    "🚫 Takedown Effectiveness",
    "📈 Monthly Trends",
    "🌍 OPCO Analysis"
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

# Tab 1: Asset Performance
with tab1:
    st.markdown("### Asset Performance Analysis")
    
    if not df_asset_perf.empty:
        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Assets", f"{len(df_asset_perf):,}")
        with col2:
            st.metric("Successful Takedowns", f"{successful_events:,}")
        with col3:
            failed_events = df_asset_perf['FAILED'].sum() if 'FAILED' in df_asset_perf.columns else 0
            st.metric("Failed Takedowns", f"{failed_events:,}")
        with col4:
            avg_failed_time = df_asset_perf['AVG_RESOLUTION_HOURS_FAILED'].dropna().mean() if 'AVG_RESOLUTION_HOURS_FAILED' in df_asset_perf.columns else 0
            if pd.isna(avg_failed_time) or avg_failed_time == 0:
                failed_time_display = "N/A"
            else:
                failed_time_display = f"{avg_failed_time:.1f}h"
            st.metric("Avg Failed Resolution", failed_time_display)
        
        # Performance by asset type
        col1, col2 = st.columns(2)
        
        with col1:
            fig_success = px.bar(
                df_asset_perf,
                x='ASSET_TYPE',
                y='SUCCESS_RATE',
                title='Success Rate by Asset Type',
                color='SUCCESS_RATE',
                color_continuous_scale=[colors['danger'], colors['warning'], colors['success']]
            )
            fig_success.add_hline(y=90, line_dash="dash", line_color=colors['primary'],
                                annotation_text="Target: 90%")
            fig_success.update_layout(plot_bgcolor='white')
            st.plotly_chart(fig_success, use_container_width=True)
        
        with col2:
            # Success vs Failed distribution
            fig_dist = go.Figure()
            fig_dist.add_trace(go.Bar(
                x=df_asset_perf['ASSET_TYPE'],
                y=df_asset_perf['SUCCESSFUL'],
                name='Successful',
                marker_color=colors['success']
            ))
            fig_dist.add_trace(go.Bar(
                x=df_asset_perf['ASSET_TYPE'],
                y=df_asset_perf['FAILED'],
                name='Failed',
                marker_color=colors['danger']
            ))
            fig_dist.update_layout(
                barmode='stack',
                title='Takedown Distribution by Asset Type',
                plot_bgcolor='white'
            )
            st.plotly_chart(fig_dist, use_container_width=True)
        
        # Resolution time comparison
        st.markdown("### Resolution Time Analysis")
        
        fig_resolution = go.Figure()
        fig_resolution.add_trace(go.Bar(
            x=df_asset_perf['ASSET_TYPE'],
            y=df_asset_perf['AVG_RESOLUTION_HOURS_SUCCESS'],
            name='Success Resolution Time',
            marker_color=colors['success']
        ))
        fig_resolution.add_trace(go.Bar(
            x=df_asset_perf['ASSET_TYPE'],
            y=df_asset_perf['AVG_RESOLUTION_HOURS_FAILED'],
            name='Failed Resolution Time',
            marker_color=colors['danger']
        ))
        fig_resolution.update_layout(
            title='Average Resolution Time by Asset Type',
            barmode='group',
            plot_bgcolor='white',
            yaxis_title='Hours'
        )
        st.plotly_chart(fig_resolution, use_container_width=True)

# Tab 2: Data Quality
with tab2:
    st.markdown("### Data Quality Metrics")
    
    if not df_quality.empty:
        # Quality overview
        for _, row in df_quality.iterrows():
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(f"Table: {row['TABLE_NAME']}", "")
            with col2:
                st.metric("Total Records", f"{row['TOTAL_RECORDS']:,}")
            with col3:
                st.metric("Null Dates %", f"{row['PCT_NULL_DATES']:.1f}%")
            with col4:
                null_takedown = row['NULL_TAKEDOWN']
                st.metric("Null Takedowns", f"{null_takedown:,}")
        
        # Quality visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Data completeness gauge
            avg_completeness = 100 - df_quality['PCT_NULL_DATES'].mean()
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = avg_completeness,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Data Completeness"},
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
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col2:
            # Quality issues breakdown
            quality_issues = pd.DataFrame({
                'Issue Type': ['Null Dates', 'Null Takedowns', 'Complete Records'],
                'Count': [
                    df_quality['NULL_DATES'].sum(),
                    df_quality['NULL_TAKEDOWN'].sum(),
                    df_quality['TOTAL_RECORDS'].sum() - df_quality['NULL_DATES'].sum() - df_quality['NULL_TAKEDOWN'].sum()
                ]
            })
            
            fig_issues = px.pie(
                quality_issues,
                values='Count',
                names='Issue Type',
                title='Data Quality Distribution',
                color_discrete_map={
                    'Complete Records': colors['success'],
                    'Null Dates': colors['warning'],
                    'Null Takedowns': colors['danger']
                }
            )
            fig_issues.update_layout(plot_bgcolor='white')
            st.plotly_chart(fig_issues, use_container_width=True)
        
        # Quality details table
        st.markdown("### Data Quality Details")
        st.dataframe(
            df_quality.style.format({
                'PCT_NULL_DATES': '{:.1f}%',
                'TOTAL_RECORDS': '{:,}',
                'NULL_DATES': '{:,}',
                'NULL_TAKEDOWN': '{:,}'
            }),
            use_container_width=True
        )

# Tab 3: Source Analysis
with tab3:
    st.markdown("### Intelligence Source Analysis")
    
    if not df_source.empty:
        # Source metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_sources = df_source['SOURCE'].nunique() if 'SOURCE' in df_source.columns else 0
        total_source_events = df_source['EVENT_COUNT'].sum() if 'EVENT_COUNT' in df_source.columns else 0
        
        # Safe calculation of average failure rate
        if 'FAILURE_RATE' in df_source.columns:
            valid_failure = df_source['FAILURE_RATE'].dropna()
            avg_failure_rate = valid_failure.mean() if len(valid_failure) > 0 else 0
        else:
            avg_failure_rate = 0
            
        max_affected_opcos = df_source['AFFECTED_OPCOS'].max() if 'AFFECTED_OPCOS' in df_source.columns and not df_source['AFFECTED_OPCOS'].isna().all() else 0
        
        with col1:
            st.metric("Total Sources", f"{total_sources:,}")
        with col2:
            st.metric("Total Events", f"{total_source_events:,}")
        with col3:
            st.metric("Avg Failure Rate", f"{avg_failure_rate:.1f}%")
        with col4:
            st.metric("Max OPCOs Affected", f"{max_affected_opcos}")
        
        # Source performance
        col1, col2 = st.columns(2)
        
        with col1:
            # Events by source
            source_events = df_source.groupby('SOURCE')['EVENT_COUNT'].sum().sort_values(ascending=True)
            fig_events = px.bar(
                x=source_events.values[-10:],
                y=source_events.index[-10:],
                orientation='h',
                title='Top 10 Sources by Event Count',
                color=source_events.values[-10:],
                color_continuous_scale='Blues',
                labels={'x': 'Event Count', 'y': 'Source'}
            )
            fig_events.update_layout(plot_bgcolor='white', showlegend=False)
            st.plotly_chart(fig_events, use_container_width=True)
        
        with col2:
            # Failure rate by source - ensure positive sizes
            df_source['PLOT_SIZE'] = df_source['AFFECTED_OPCOS'].clip(lower=5) * 10
            fig_failure = px.scatter(
                df_source,
                x='EVENT_COUNT',
                y='FAILURE_RATE',
                size='PLOT_SIZE',
                color='FAILURE_RATE',
                title='Source Performance Analysis',
                hover_data=['SOURCE', 'ASSET_TYPE', 'AFFECTED_OPCOS'],
                color_continuous_scale='Reds',
                labels={'FAILURE_RATE': 'Failure %', 'EVENT_COUNT': 'Event Count'}
            )
            fig_failure.update_layout(plot_bgcolor='white')
            st.plotly_chart(fig_failure, use_container_width=True)
        
        # Source details
        st.markdown("### Source Performance Details")
        
        # Convert dates for display
        df_source_display = df_source.copy()
        for col in ['FIRST_DETECTED', 'LAST_DETECTED']:
            if col in df_source_display.columns:
                df_source_display[col] = pd.to_datetime(df_source_display[col]).dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            df_source_display[['SOURCE', 'ASSET_TYPE', 'EVENT_COUNT', 'AFFECTED_OPCOS', 
                              'FAILED_TAKEDOWNS', 'FAILURE_RATE']].style.format({
                'FAILURE_RATE': '{:.1f}%',
                'EVENT_COUNT': '{:,}',
                'FAILED_TAKEDOWNS': '{:,}'
            }).background_gradient(subset=['FAILURE_RATE'], cmap='Reds'),
            use_container_width=True
        )

# Tab 4: Takedown Effectiveness
with tab4:
    st.markdown("### Takedown Effectiveness")
    
    if not df_takedown.empty:
        # Effectiveness overview
        total_takedowns = df_takedown['TOTAL_EVENTS'].sum()
        successful_takedowns = df_takedown['SUCCESSFUL_TAKEDOWNS'].sum()
        overall_effectiveness = (successful_takedowns/total_takedowns*100) if total_takedowns > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Takedown Events", f"{total_takedowns:,}")
        with col2:
            st.metric("Successful Takedowns", f"{successful_takedowns:,}")
        with col3:
            st.metric("Overall Success Rate", f"{overall_effectiveness:.1f}%")
        
        # Effectiveness by source and asset
        col1, col2 = st.columns(2)
        
        with col1:
            # Success rate by source
            source_effectiveness = df_takedown.groupby('SOURCE').agg({
                'SUCCESS_RATE': 'mean'
            }).sort_values('SUCCESS_RATE', ascending=True)
            
            fig_source_eff = px.bar(
                x=source_effectiveness['SUCCESS_RATE'].values[-10:],
                y=source_effectiveness.index[-10:],
                orientation='h',
                title='Top 10 Sources by Success Rate',
                color=source_effectiveness['SUCCESS_RATE'].values[-10:],
                color_continuous_scale=[colors['danger'], colors['warning'], colors['success']],
                labels={'x': 'Success Rate %', 'y': 'Source'}
            )
            fig_source_eff.update_layout(plot_bgcolor='white', showlegend=False)
            st.plotly_chart(fig_source_eff, use_container_width=True)
        
        with col2:
            # Success rate by asset type
            asset_effectiveness = df_takedown.groupby('ASSET_TYPE').agg({
                'SUCCESS_RATE': 'mean',
                'TOTAL_EVENTS': 'sum'
            })
            
            fig_asset_eff = px.scatter(
                asset_effectiveness,
                x='TOTAL_EVENTS',
                y='SUCCESS_RATE',
                size='TOTAL_EVENTS',
                color='SUCCESS_RATE',
                title='Asset Type Effectiveness',
                text=asset_effectiveness.index,
                color_continuous_scale='Greens',
                labels={'SUCCESS_RATE': 'Success Rate %', 'TOTAL_EVENTS': 'Total Events'}
            )
            fig_asset_eff.update_traces(textposition='top center')
            fig_asset_eff.update_layout(plot_bgcolor='white')
            st.plotly_chart(fig_asset_eff, use_container_width=True)
        
        # Effectiveness heatmap
        st.markdown("### Takedown Effectiveness Matrix")
        
        pivot_table = df_takedown.pivot_table(
            index='ASSET_TYPE',
            columns='SOURCE',
            values='SUCCESS_RATE',
            aggfunc='mean'
        )
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=pivot_table.values,
            x=pivot_table.columns,
            y=pivot_table.index,
            colorscale=[[0, colors['danger']], [0.5, colors['warning']], [1, colors['success']]],
            text=np.round(pivot_table.values, 1),
            texttemplate="%{text}%",
            textfont={"size": 10}
        ))
        
        fig_heatmap.update_layout(
            title='Success Rate Matrix: Asset Type vs Source',
            xaxis_title='Source',
            yaxis_title='Asset Type',
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)

# Tab 5: Monthly Trends
with tab5:
    st.markdown("### Monthly Trend Analysis")
    
    if not df_trends.empty:
        # Trend overview
        col1, col2, col3, col4 = st.columns(4)
        
        total_monthly_events = df_trends['TOTAL_EVENTS'].sum() if 'TOTAL_EVENTS' in df_trends.columns else 0
        verified_events = df_trends['VERIFIED_EVENTS'].sum() if 'VERIFIED_EVENTS' in df_trends.columns else 0
        
        # Safe calculation of average verification rate
        if 'VERIFICATION_RATE' in df_trends.columns:
            valid_verification = df_trends['VERIFICATION_RATE'].dropna()
            avg_verification = valid_verification.mean() if len(valid_verification) > 0 else 0
            avg_verification = min(100, max(0, avg_verification))  # Ensure valid percentage
        else:
            avg_verification = 0
            
        unique_opcos = df_trends['OPCO'].nunique() if 'OPCO' in df_trends.columns else 0
        
        with col1:
            st.metric("Total Monthly Events", f"{total_monthly_events:,}")
        with col2:
            st.metric("Verified Events", f"{verified_events:,}")
        with col3:
            st.metric("Avg Verification Rate", f"{avg_verification:.1f}%")
        with col4:
            st.metric("Unique OPCOs", f"{unique_opcos}")
        
        # Monthly event trend
        monthly_summary = df_trends.groupby('MONTH_YEAR').agg({
            'TOTAL_EVENTS': 'sum',
            'VERIFIED_EVENTS': 'sum',
            'VERIFICATION_RATE': 'mean'
        }).reset_index()
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=monthly_summary['MONTH_YEAR'],
            y=monthly_summary['TOTAL_EVENTS'],
            mode='lines+markers',
            name='Total Events',
            line=dict(color=colors['primary'], width=2)
        ))
        fig_trend.add_trace(go.Scatter(
            x=monthly_summary['MONTH_YEAR'],
            y=monthly_summary['VERIFIED_EVENTS'],
            mode='lines+markers',
            name='Verified Events',
            line=dict(color=colors['success'], width=2)
        ))
        fig_trend.update_layout(
            title='Monthly Event Trend',
            xaxis_title='Month',
            yaxis_title='Event Count',
            plot_bgcolor='white'
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # OPCO and Source breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            # Events by OPCO
            opco_events = df_trends.groupby('OPCO')['TOTAL_EVENTS'].sum().sort_values(ascending=False)
            fig_opco = px.pie(
                values=opco_events.values,
                names=opco_events.index,
                title='Event Distribution by OPCO',
                color_discrete_sequence=px.colors.sequential.Blues
            )
            fig_opco.update_layout(plot_bgcolor='white')
            st.plotly_chart(fig_opco, use_container_width=True)
        
        with col2:
            # Verification rate by source
            source_verification = df_trends.groupby('SOURCE')['VERIFICATION_RATE'].mean().sort_values()
            fig_verification = px.bar(
                x=source_verification.values,
                y=source_verification.index,
                orientation='h',
                title='Verification Rate by Source',
                color=source_verification.values,
                color_continuous_scale='Greens',
                labels={'x': 'Verification Rate %', 'y': 'Source'}
            )
            fig_verification.update_layout(plot_bgcolor='white', showlegend=False)
            st.plotly_chart(fig_verification, use_container_width=True)

# Tab 6: OPCO Analysis
with tab6:
    st.markdown("### OPCO Performance Analysis")
    
    if not df_trends.empty and not df_source.empty:
        # OPCO metrics
        opco_metrics = df_trends.groupby('OPCO').agg({
            'TOTAL_EVENTS': 'sum',
            'VERIFIED_EVENTS': 'sum',
            'VERIFICATION_RATE': 'mean'
        }).reset_index()
        
        # Add affected sources
        if not df_source.empty:
            opco_sources = df_source.groupby('SOURCE')['AFFECTED_OPCOS'].max()
            opco_metrics['AFFECTED_SOURCES'] = len(opco_sources)
        
        # OPCO scorecard
        st.markdown("### OPCO Scorecard")
        
        for idx, opco in enumerate(opco_metrics['OPCO'].unique()[:5]):
            metrics = opco_metrics[opco_metrics['OPCO'] == opco].iloc[0]
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric(f"{opco}", "")
            with col2:
                st.metric("Events", f"{int(metrics['TOTAL_EVENTS']):,}")
            with col3:
                st.metric("Verified", f"{int(metrics['VERIFIED_EVENTS']):,}")
            with col4:
                st.metric("Verification %", f"{metrics['VERIFICATION_RATE']:.1f}%")
            with col5:
                sources_count = metrics.get('AFFECTED_SOURCES', 0)
                st.metric("Sources", f"{int(sources_count)}")
        
        # OPCO comparison chart
        st.markdown("### OPCO Comparison")
        
        fig_comparison = go.Figure()
        
        fig_comparison.add_trace(go.Bar(
            x=opco_metrics['OPCO'],
            y=opco_metrics['VERIFICATION_RATE'],
            name='Verification Rate %',
            marker_color=colors['success'],
            yaxis='y'
        ))
        
        fig_comparison.add_trace(go.Scatter(
            x=opco_metrics['OPCO'],
            y=opco_metrics['TOTAL_EVENTS'],
            name='Total Events',
            marker_color=colors['primary'],
            yaxis='y2',
            mode='lines+markers'
        ))
        
        fig_comparison.update_layout(
            title='OPCO Performance Metrics',
            xaxis_title='OPCO',
            yaxis=dict(title='Verification Rate %', side='left'),
            yaxis2=dict(title='Total Events', side='right', overlaying='y'),
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Risk assessment by OPCO
        st.markdown("### OPCO Risk Assessment")
        
        # Calculate risk score - ensure positive values
        verification_component = (100 - opco_metrics['VERIFICATION_RATE'].clip(0, 100)) * 0.5
        events_normalized = (opco_metrics['TOTAL_EVENTS'] / opco_metrics['TOTAL_EVENTS'].max() * 100) if opco_metrics['TOTAL_EVENTS'].max() > 0 else 0
        opco_metrics['RISK_SCORE'] = abs(verification_component + events_normalized * 0.5)
        
        # Ensure minimum size for visibility
        opco_metrics['PLOT_SIZE'] = opco_metrics['RISK_SCORE'].clip(lower=10) + 10
        
        fig_risk = px.scatter(
            opco_metrics,
            x='VERIFICATION_RATE',
            y='TOTAL_EVENTS',
            size='PLOT_SIZE',
            color='RISK_SCORE',
            text='OPCO',
            title='OPCO Risk Matrix',
            color_continuous_scale='Reds',
            labels={'VERIFICATION_RATE': 'Verification Rate %', 'TOTAL_EVENTS': 'Total Events'}
        )
        fig_risk.update_traces(textposition='top center')
        fig_risk.update_layout(plot_bgcolor='white')
        
        st.plotly_chart(fig_risk, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1rem;">
    <p><strong>Threat Intelligence Dashboard</strong> | Cyber Threat Intelligence Platform</p>
    <p>Group Information Security - Data Platform & ETL</p>
    <p style="font-size: 0.85rem;">© 2025 GenericCorp Corporation. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)