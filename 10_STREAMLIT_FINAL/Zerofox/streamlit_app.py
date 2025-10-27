# Import packages
import streamlit as st
import pandas as pd
# import plotly.express as px  # Not available in Snowflake
# import plotly.graph_objects as go  # Not available in Snowflake
# from plotly.subplots import make_subplots  # Not available in Snowflake
from snowflake.snowpark.context import get_active_session
from datetime import datetime, timedelta
# import numpy as np  # Not available in Snowflake

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
            rgba(255,255,255,0.02) 20px,
            rgba(255,255,255,0.02) 40px
        );
    }
    
    .main-header::after {
        content: "🔐";
        position: absolute;
        right: 40px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 6rem;
        opacity: 0.1;
    }
    
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff 0%, #f5f6fa 100%);
        border: 1px solid #dfe4ea;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(26, 26, 46, 0.15);
        border-color: #e94560;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: linear-gradient(90deg, #f5f6fa 0%, #dfe4ea 100%);
        padding: 0.75rem;
        border-radius: 12px;
        box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.75rem 1.25rem;
        background: white;
        border: 1px solid #dfe4ea;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #fff5f5 0%, #ffe8ec 100%);
        border-color: #e94560;
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #e94560 0%, #0f3460 100%);
        color: white;
        border: none;
        box-shadow: 0 4px 15px rgba(233, 69, 96, 0.3);
    }
    
    .kpi-card {
        background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
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
        background: linear-gradient(135deg, #e94560, #0f3460);
    }
    
    .kpi-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 15px 35px rgba(233, 69, 96, 0.2);
    }
    
    .kpi-value {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #e94560 0%, #0f3460 100%);
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
    
    .alert-badge {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .badge-high {
        background: linear-gradient(135deg, #ff4757 0%, #c44569 100%);
        color: white;
    }
    
    .badge-medium {
        background: linear-gradient(135deg, #ffa502 0%, #ff6348 100%);
        color: white;
    }
    
    .badge-low {
        background: linear-gradient(135deg, #ffd32c 0%, #ffb142 100%);
        color: #2c2c54;
    }
    
    h3 {
        color: #1a1a2e;
        border-bottom: 3px solid transparent;
        border-image: linear-gradient(to right, #e94560, #0f3460, transparent) 1;
        padding-bottom: 0.75rem;
        margin-top: 2rem;
        font-weight: 600;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #e94560 0%, #0f3460 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(233, 69, 96, 0.3);
    }
    
    .data-issue-warning {
        background: linear-gradient(135deg, #fff5f5 0%, #ffe8ec 100%);
        border-left: 4px solid #e94560;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .data-issue-warning h4 {
        color: #e94560;
        margin: 0 0 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Get session
session = get_active_session()

# Header
st.markdown("""
<div class="main-header">
    <h1 style="text-align: center; margin: 0; position: relative; z-index: 1;">
        ZeroFox Digital Risk Protection Platform
    </h1>
    <p style="text-align: center; margin: 0.75rem 0 0 0; opacity: 0.9; position: relative; z-index: 1; font-size: 1.1rem;">
        External Threat Intelligence & Brand Protection Monitoring
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #e94560, #0f3460); border-radius: 12px; margin-bottom: 1.5rem; box-shadow: 0 6px 20px rgba(233, 69, 96, 0.3);">
        <h2 style="color: white; margin: 0; font-size: 1.5rem;">🔐 ZeroFox</h2>
        <p style="color: #ffe8ec; font-size: 0.95rem; margin-top: 0.5rem;">Digital Risk Protection</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filters
    st.header("🎯 Dashboard Filters")
    
    # OPCO filter
    opco_filter = st.multiselect(
        "OPCO Selection",
        ["All OPCOs", "Americas", "Europe", "APAC", "AGTEST", "AMG", "ANIMAS", "APAC1"],
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
    auto_refresh = st.checkbox("🔄 Auto-refresh (5 min)", value=True)
    if st.button("🔄 Refresh Now", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.info("""
    **📊 Monitoring:**
    - Asset Exposure
    - Domain Protection
    - Alert Trends
    - Threat Actors
    - Response Performance
    """)

# Data loading
@st.cache_data(ttl=300)
def load_data(query):
    try:
        return session.sql(query).to_pandas()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Load data from views
asset_exposure_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_ZEROFOX_ASSET_EXPOSURE ORDER BY ALERT_COUNT_90D DESC"
domain_protection_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_ZEROFOX_DOMAIN_PROTECTION ORDER BY TOTAL_ALERTS DESC"
data_quality_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_ZEROFOX_DATA_QUALITY"
alert_trends_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_ZEROFOX_ALERT_TRENDS ORDER BY ALERT_DATE DESC"
response_perf_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_ZEROFOX_RESPONSE_PERFORMANCE"
threat_actors_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_ZEROFOX_THREAT_ACTORS ORDER BY ALERT_COUNT DESC"

df_asset_exposure = load_data(asset_exposure_query)
df_domain_protection = load_data(domain_protection_query)
df_data_quality = load_data(data_quality_query)
df_alert_trends = load_data(alert_trends_query)
df_response_perf = load_data(response_perf_query)
df_threat_actors = load_data(threat_actors_query)

# Calculate KPIs
if not df_asset_exposure.empty:
    total_assets = len(df_asset_exposure)
    high_exposure_assets = len(df_asset_exposure[df_asset_exposure['EXPOSURE_LEVEL'] == 'High'])
    total_alerts_90d = df_asset_exposure['ALERT_COUNT_90D'].sum()
    open_alerts = df_asset_exposure['OPEN_ALERTS'].sum()
else:
    total_assets = high_exposure_assets = total_alerts_90d = open_alerts = 0

if not df_domain_protection.empty:
    protected_domains = df_domain_protection['PROTECTED_DOMAIN'].nunique()
    avg_removal_rate = df_domain_protection['REMOVAL_RATE'].mean()
    live_alerts = df_domain_protection['LIVE_ALERTS'].sum()
else:
    protected_domains = live_alerts = 0
    avg_removal_rate = 0

# KPIs
st.markdown("### 📊 Executive Summary")

kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)

with kpi_col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{total_assets:,}</div>
        <div class="kpi-label">Protected Assets</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{total_alerts_90d:,}</div>
        <div class="kpi-label">Alerts (90d)</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{open_alerts:,}</div>
        <div class="kpi-label">Open Alerts</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{protected_domains:,}</div>
        <div class="kpi-label">Domains</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{avg_removal_rate:.1f}%</div>
        <div class="kpi-label">Removal Rate</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col6:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{high_exposure_assets:,}</div>
        <div class="kpi-label">High Risk</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Color palette
colors = {
    'primary': '#e94560',
    'secondary': '#0f3460',
    'success': '#26de81',
    'warning': '#ffa502',
    'danger': '#ff4757',
    'info': '#54a0ff',
    'dark': '#1a1a2e',
    'light': '#f5f6fa'
}

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🎯 Asset Exposure",
    "🌐 Domain Protection", 
    "📈 Alert Trends",
    "👥 Threat Actors",
    "⚡ Response Performance",
    "📊 OPCO Analysis",
    "✅ Data Quality"
])

# Tab 1: Asset Exposure
with tab1:
    st.markdown("### Asset Exposure Overview")
    
    if not df_asset_exposure.empty:
        # Exposure metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Assets", f"{total_assets:,}")
        with col2:
            st.metric("High Risk Assets", f"{high_exposure_assets:,}")
        with col3:
            avg_alerts_per_asset = total_alerts_90d / total_assets if total_assets > 0 else 0
            st.metric("Avg Alerts/Asset", f"{avg_alerts_per_asset:.1f}")
        with col4:
            high_risk_pct = (high_exposure_assets/total_assets*100) if total_assets > 0 else 0
            st.metric("High Risk %", f"{high_risk_pct:.1f}%")
        
        # Asset exposure by type
        col1, col2 = st.columns(2)
        
        with col1:
            # Group by asset type
            asset_by_type = df_asset_exposure.groupby('ASSET_TYPE').agg({
                'ASSET_ID': 'count',
                'ALERT_COUNT_90D': 'sum'
            }).reset_index()
            asset_by_type.columns = ['Asset Type', 'Count', 'Total Alerts']
            
            fig_asset_type = px.bar(
                asset_by_type,
                x='Asset Type',
                y='Count',
                title='Assets by Type',
                color='Total Alerts',
                color_continuous_scale='Reds',
                text='Count'
            )
            fig_asset_type.update_layout(plot_bgcolor='white')
            st.plotly_chart(fig_asset_type, use_container_width=True)
        
        with col2:
            # Exposure level distribution
            exposure_dist = df_asset_exposure['EXPOSURE_LEVEL'].value_counts()
            
            fig_exposure = px.pie(
                values=exposure_dist.values,
                names=exposure_dist.index,
                title='Asset Exposure Distribution',
                color_discrete_map={
                    'High': colors['danger'],
                    'Medium': colors['warning'],
                    'Low': colors['success']
                }
            )
            st.plotly_chart(fig_exposure, use_container_width=True)
        
        # Top exposed assets
        st.markdown("### 🚨 Top Exposed Assets")
        
        top_exposed = df_asset_exposure.nlargest(10, 'ALERT_COUNT_90D')
        
        fig_top_assets = px.bar(
            top_exposed,
            y='ASSET_NAME',
            x='ALERT_COUNT_90D',
            orientation='h',
            title='Top 10 Assets by Alert Count (90 days)',
            color='EXPOSURE_LEVEL',
            color_discrete_map={
                'High': colors['danger'],
                'Medium': colors['warning'],
                'Low': colors['success']
            },
            text='ALERT_COUNT_90D'
        )
        fig_top_assets.update_layout(
            plot_bgcolor='white',
            yaxis={'categoryorder': 'total ascending'}
        )
        st.plotly_chart(fig_top_assets, use_container_width=True)
        
        # Asset details table
        st.markdown("### Asset Details")
        
        display_cols = ['ASSET_NAME', 'OPCO', 'ASSET_TYPE', 'ALERT_COUNT_90D', 
                       'HIGH_SEVERITY_COUNT', 'OPEN_ALERTS', 'EXPOSURE_LEVEL']
        
        st.dataframe(
            df_asset_exposure[display_cols].style.apply(
                lambda x: ['background-color: #ffebee' if x['EXPOSURE_LEVEL'] == 'High'
                          else 'background-color: #fff8e1' if x['EXPOSURE_LEVEL'] == 'Medium'
                          else '' for _ in x], axis=1
            ),
            use_container_width=True
        )
    else:
        st.warning("No asset exposure data available")

# Tab 2: Domain Protection
with tab2:
    st.markdown("### Domain Protection Status")
    
    if not df_domain_protection.empty:
        # Domain metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_domain_alerts = df_domain_protection['TOTAL_ALERTS'].sum()
        removed_alerts = df_domain_protection['REMOVED_ALERTS'].sum()
        
        with col1:
            st.metric("Protected Domains", f"{protected_domains:,}")
        with col2:
            st.metric("Total Alerts", f"{total_domain_alerts:,}")
        with col3:
            st.metric("Removed Alerts", f"{removed_alerts:,}")
        with col4:
            st.metric("Live Alerts", f"{live_alerts:,}")
        
        # Domain protection by OPCO
        col1, col2 = st.columns(2)
        
        with col1:
            opco_domains = df_domain_protection.groupby('OPCO').agg({
                'PROTECTED_DOMAIN': 'count',
                'TOTAL_ALERTS': 'sum',
                'REMOVAL_RATE': 'mean'
            }).reset_index()
            
            fig_opco_domains = px.bar(
                opco_domains,
                x='OPCO',
                y='PROTECTED_DOMAIN',
                title='Protected Domains by OPCO',
                color='REMOVAL_RATE',
                color_continuous_scale='RdYlGn',
                text='PROTECTED_DOMAIN'
            )
            fig_opco_domains.update_layout(plot_bgcolor='white')
            st.plotly_chart(fig_opco_domains, use_container_width=True)
        
        with col2:
            # Removal effectiveness
            fig_removal = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = avg_removal_rate,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Content Removal Rate"},
                delta = {'reference': 75},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': colors['primary']},
                    'steps': [
                        {'range': [0, 50], 'color': 'lightgray'},
                        {'range': [50, 75], 'color': 'gray'}
                    ],
                    'threshold': {
                        'line': {'color': 'red', 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig_removal.update_layout(height=400, paper_bgcolor='white')
            st.plotly_chart(fig_removal, use_container_width=True)
        
        # Top targeted domains
        st.markdown("### 🎯 Most Targeted Domains")
        
        top_domains = df_domain_protection.nlargest(10, 'TOTAL_ALERTS')
        
        fig_targeted = px.scatter(
            top_domains,
            x='TOTAL_ALERTS',
            y='REMOVAL_RATE',
            size='LIVE_ALERTS',
            color='OPCO',
            hover_data=['PROTECTED_DOMAIN'],
            title='Domain Alert Volume vs Removal Rate',
            labels={'TOTAL_ALERTS': 'Total Alerts', 'REMOVAL_RATE': 'Removal Rate (%)'}
        )
        fig_targeted.update_layout(plot_bgcolor='white')
        st.plotly_chart(fig_targeted, use_container_width=True)
        
        # Domain details
        st.markdown("### Domain Protection Details")
        st.dataframe(
            df_domain_protection[['OPCO', 'PROTECTED_DOMAIN', 'TOTAL_ALERTS', 
                                 'REMOVED_ALERTS', 'LIVE_ALERTS', 'REMOVAL_RATE']].style.format({
                'REMOVAL_RATE': '{:.1f}%'
            }).background_gradient(subset=['REMOVAL_RATE'], cmap='RdYlGn'),
            use_container_width=True
        )
    else:
        st.warning("No domain protection data available")

# Tab 3: Alert Trends
with tab3:
    st.markdown("### Alert Trend Analysis")
    
    if not df_alert_trends.empty:
        # Trend visualizations would go here
        st.info("Alert trends data available - visualizations ready for implementation")
    else:
        st.markdown("""
        <div class="data-issue-warning">
            <h4>⚠️ No Alert Trend Data Available</h4>
            <p>The alert trends view is currently empty. This is likely because:</p>
            <ul>
                <li>The <code>fact_zerofox_alerts</code> table has no data</li>
                <li>No alerts have been ingested in the last 3 months</li>
                <li>There may be an issue with the data pipeline</li>
            </ul>
            <p><strong>Recommended Action:</strong> Check the data ingestion pipeline and ensure alerts are being properly loaded into <code>DEV_TRANSFORMATION.SECURITY_ANALYTICS.fact_zerofox_alerts</code></p>
        </div>
        """, unsafe_allow_html=True)

# Tab 4: Threat Actors
with tab4:
    st.markdown("### Threat Actor Intelligence")
    
    if not df_threat_actors.empty:
        # Threat actor analysis would go here
        st.info("Threat actor data available - visualizations ready for implementation")
    else:
        st.markdown("""
        <div class="data-issue-warning">
            <h4>⚠️ No Threat Actor Data Available</h4>
            <p>The threat actors view is currently empty because the <code>fact_zerofox_alerts</code> table has no data.</p>
            <p>Once alerts are ingested, this section will show:</p>
            <ul>
                <li>Top threat actors by alert volume</li>
                <li>Affected OPCOs per threat actor</li>
                <li>Platform usage patterns</li>
                <li>Threat actor timeline analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# Tab 5: Response Performance
with tab5:
    st.markdown("### Response Performance Metrics")
    
    if not df_response_perf.empty:
        # Response performance metrics would go here
        st.info("Response performance data available - visualizations ready for implementation")
    else:
        st.markdown("""
        <div class="data-issue-warning">
            <h4>⚠️ No Response Performance Data Available</h4>
            <p>The response performance view requires data from <code>fact_zerofox_alerts</code>, which is currently empty.</p>
            <p>Once populated, this section will display:</p>
            <ul>
                <li>Average response time by alert type</li>
                <li>P90 response time metrics</li>
                <li>Success rate by OPCO</li>
                <li>Stale alert tracking</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# Tab 6: OPCO Analysis
with tab6:
    st.markdown("### OPCO Performance Analysis")
    
    if not df_asset_exposure.empty or not df_domain_protection.empty:
        # Compile OPCO metrics
        opco_metrics = pd.DataFrame()
        
        # Get unique OPCOs
        all_opcos = set()
        if not df_asset_exposure.empty:
            all_opcos.update(df_asset_exposure['OPCO'].unique())
        if not df_domain_protection.empty:
            all_opcos.update(df_domain_protection['OPCO'].unique())
        
        # Remove nulls and standardize
        all_opcos = {str(opco).strip().upper() for opco in all_opcos if pd.notna(opco) and str(opco).strip()}
        
        if all_opcos:
            # Create metrics dataframe
            opco_list = sorted(list(all_opcos))
            opco_metrics = pd.DataFrame(index=opco_list)
            
            # Add asset exposure metrics
            if not df_asset_exposure.empty:
                asset_metrics = df_asset_exposure.groupby('OPCO').agg({
                    'ASSET_ID': 'count',
                    'ALERT_COUNT_90D': 'sum',
                    'HIGH_SEVERITY_COUNT': 'sum',
                    'OPEN_ALERTS': 'sum'
                })
                asset_metrics.columns = ['Asset_Count', 'Total_Alerts', 'High_Severity', 'Open_Alerts']
                opco_metrics = opco_metrics.join(asset_metrics, how='left')
            
            # Add domain protection metrics
            if not df_domain_protection.empty:
                domain_metrics = df_domain_protection.groupby('OPCO').agg({
                    'PROTECTED_DOMAIN': 'count',
                    'REMOVAL_RATE': 'mean',
                    'LIVE_ALERTS': 'sum'
                })
                domain_metrics.columns = ['Protected_Domains', 'Avg_Removal_Rate', 'Live_Alerts']
                opco_metrics = opco_metrics.join(domain_metrics, how='left')
            
            opco_metrics = opco_metrics.fillna(0)
            
            # OPCO Scorecard
            st.markdown("### OPCO Risk Scorecard")
            
            for opco in opco_metrics.index[:5]:
                metrics = opco_metrics.loc[opco]
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric(f"{opco}", "")
                with col2:
                    assets = int(metrics.get('Asset_Count', 0))
                    st.metric("Assets", f"{assets:,}")
                with col3:
                    alerts = int(metrics.get('Total_Alerts', 0))
                    st.metric("Alerts (90d)", f"{alerts:,}")
                with col4:
                    removal = float(metrics.get('Avg_Removal_Rate', 0))
                    st.metric("Removal %", f"{removal:.1f}%")
                with col5:
                    open_alerts = int(metrics.get('Open_Alerts', 0))
                    st.metric("Open", f"{open_alerts:,}")
            
            # Performance comparison
            st.markdown("### OPCO Comparison")
            
            fig_comparison = go.Figure()
            
            if 'Total_Alerts' in opco_metrics.columns:
                # Normalize for comparison
                max_alerts = opco_metrics['Total_Alerts'].max()
                if max_alerts > 0:
                    normalized_alerts = (opco_metrics['Total_Alerts'] / max_alerts * 100)
                    
                    fig_comparison.add_trace(go.Bar(
                        x=opco_metrics.index,
                        y=normalized_alerts,
                        name='Alert Volume',
                        marker_color=colors['danger']
                    ))
            
            if 'Avg_Removal_Rate' in opco_metrics.columns:
                fig_comparison.add_trace(go.Bar(
                    x=opco_metrics.index,
                    y=opco_metrics['Avg_Removal_Rate'],
                    name='Removal Rate %',
                    marker_color=colors['success']
                ))
            
            fig_comparison.update_layout(
                title='OPCO Security Metrics Comparison',
                barmode='group',
                plot_bgcolor='white',
                yaxis_title='Score / Percentage'
            )
            st.plotly_chart(fig_comparison, use_container_width=True)
            
            # Risk heatmap
            st.markdown("### OPCO Risk Heatmap")
            
            # Calculate risk scores
            risk_matrix = pd.DataFrame(index=opco_metrics.index)
            
            # Alert volume risk (normalized)
            if 'Total_Alerts' in opco_metrics.columns:
                max_alerts = opco_metrics['Total_Alerts'].max()
                if max_alerts > 0:
                    risk_matrix['Alert Risk'] = (opco_metrics['Total_Alerts'] / max_alerts * 100)
                else:
                    risk_matrix['Alert Risk'] = 0
            
            # Open alerts risk
            if 'Open_Alerts' in opco_metrics.columns:
                max_open = opco_metrics['Open_Alerts'].max()
                if max_open > 0:
                    risk_matrix['Open Alert Risk'] = (opco_metrics['Open_Alerts'] / max_open * 100)
                else:
                    risk_matrix['Open Alert Risk'] = 0
            
            # Removal effectiveness (inverted - low removal = high risk)
            if 'Avg_Removal_Rate' in opco_metrics.columns:
                risk_matrix['Removal Risk'] = 100 - opco_metrics['Avg_Removal_Rate']
            
            if not risk_matrix.empty:
                fig_heatmap = go.Figure(data=go.Heatmap(
                    z=risk_matrix.T.values,
                    x=risk_matrix.index,
                    y=risk_matrix.columns,
                    colorscale=[[0, colors['success']], [0.5, colors['warning']], [1, colors['danger']]],
                    text=np.round(risk_matrix.T.values, 1),
                    texttemplate="%{text}",
                    textfont={"size": 10}
                ))
                
                fig_heatmap.update_layout(
                    title='OPCO Risk Assessment (0=Low Risk, 100=High Risk)',
                    xaxis_title='OPCO',
                    yaxis_title='Risk Category',
                    plot_bgcolor='white'
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.warning("No data available for OPCO analysis")

# Tab 7: Data Quality
with tab7:
    st.markdown("### Data Quality Monitoring")
    
    if not df_data_quality.empty:
        # Data quality metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Data Completeness")
            
            for _, row in df_data_quality.iterrows():
                st.write(f"**{row['TABLE_NAME']}**")
                st.write(f"- Total Records: {row['TOTAL_RECORDS']:,}")
                
                # Check for null percentages
                null_cols = [col for col in df_data_quality.columns if col.startswith('PCT_NULL_')]
                for col in null_cols:
                    if pd.notna(row[col]) and row[col] > 0:
                        field_name = col.replace('PCT_NULL_', '')
                        st.write(f"- {field_name} Null %: {row[col]:.1f}%")
        
        with col2:
            # Visualize data quality
            if 'TOTAL_RECORDS' in df_data_quality.columns:
                fig_records = px.bar(
                    df_data_quality,
                    x='TABLE_NAME',
                    y='TOTAL_RECORDS',
                    title='Record Count by Table',
                    color='TOTAL_RECORDS',
                    color_continuous_scale='Blues'
                )
                fig_records.update_layout(plot_bgcolor='white')
                st.plotly_chart(fig_records, use_container_width=True)
        
        # Data pipeline status check
        st.markdown("### 🔍 Data Pipeline Health Check")
        
        # Check for fact_zerofox_alerts
        st.markdown("""
        <div class="data-issue-warning">
            <h4>⚠️ Critical Data Issue Detected</h4>
            <p><strong>fact_zerofox_alerts</strong> table is empty</p>
            <p>This affects the following views:</p>
            <ul>
                <li>VW_GOLD_ZEROFOX_ALERT_TRENDS</li>
                <li>VW_GOLD_ZEROFOX_RESPONSE_PERFORMANCE</li>
                <li>VW_GOLD_ZEROFOX_THREAT_ACTORS</li>
            </ul>
            <p><strong>Action Required:</strong> Verify ZeroFox API integration and data ingestion pipeline</p>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.warning("No data quality information available")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1rem;">
    <p><strong>ZeroFox Digital Risk Protection</strong> | External Threat Intelligence</p>
    <p>Group Information Security - Threat Intelligence Platform</p>
    <p style="font-size: 0.85rem;">© 2025 GenericCorp Corporation. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)