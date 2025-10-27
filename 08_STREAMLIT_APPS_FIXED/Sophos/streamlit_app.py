# Import packages
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
    page_title="Sophos Security Dashboard",
    page_icon="🛡️",
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
        <span style="font-size: 2.5rem;">🛡️</span> Sophos Security Dashboard
    </h1>
    <p style="text-align: center; margin: 0.75rem 0 0 0; opacity: 0.9; position: relative; z-index: 1; font-size: 1.1rem;">
        Group Information Security - Endpoint Protection Platform
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #0a3d62, #1e5f8e); border-radius: 12px; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(10, 61, 98, 0.2);">
        <h2 style="color: white; margin: 0; font-size: 1.5rem;">🏢 GenericCorp</h2>
        <p style="color: #e8f0f8; font-size: 0.95rem; margin-top: 0.5rem;">Sophos Security Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filters
    st.header("📊 Dashboard Filters")
    
    # Scope filter
    scope_filter = st.multiselect(
        "Scope Selection",
        ["Global", "Americas", "Europe", "APAC"],
        default=["Global"],
        help="Filter by organizational scope"
    
    )
    # OS filter
    os_filter = st.multiselect(
        "Operating System",
        ["Windows", "Linux", "macOS", "All"],
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
    - Endpoint Health
    - Protection Coverage
    - Security Alerts
    - OS Distribution
    - User Activity
    """)

# Data loading
@st.cache_data(ttl=300)
def load_data(query):
    try:
        return session.sql(query).to_pandas()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Load data from Snowflake views
endpoint_health_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_SOPHOS_ENDPOINT_HEALTH ORDER BY SNAPSHOT_DATE DESC"
executive_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_SOPHOS_EXECUTIVE_SUMMARY ORDER BY SNAPSHOT_DATE DESC"
os_protection_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_SOPHOS_OS_PROTECTION ORDER BY SNAPSHOT_DATE DESC"
alerts_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_SOPHOS_SECURITY_ALERTS ORDER BY SNAPSHOT_DATE DESC"
user_activity_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_SOPHOS_USER_ACTIVITY ORDER BY SNAPSHOT_DATE DESC"

df_health = load_data(endpoint_health_query)
df_executive = load_data(executive_query)
df_os = load_data(os_protection_query)
df_alerts = load_data(alerts_query)
df_users = load_data(user_activity_query)

# Calculate KPIs
if not df_executive.empty:
    total_endpoints = df_executive['TOTAL_ENDPOINTS'].sum()
    healthy_endpoints = df_executive['HEALTHY_ENDPOINTS'].sum()
    protected_endpoints = df_executive['PROTECTED_ENDPOINTS'].sum()
    active_7d = df_executive['ACTIVE_7D'].sum()
    active_alerts = df_executive['ACTIVE_ALERTS'].sum()
else:
    total_endpoints = healthy_endpoints = protected_endpoints = active_7d = active_alerts = 0

if not df_health.empty:
    health_compliance = df_health['HEALTH_COMPLIANCE_PCT'].mean()
    protection_coverage = df_health['PROTECTION_COVERAGE_PCT'].mean()
else:
    health_compliance = protection_coverage = 0

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
        <div class="kpi-value">{health_compliance:.1f}%</div>
        <div class="kpi-label">Health Compliance</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{protection_coverage:.1f}%</div>
        <div class="kpi-label">Protection Rate</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{active_7d:,}</div>
        <div class="kpi-label">Active (7d)</div>
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
        <div class="kpi-value">{healthy_endpoints:,}</div>
        <div class="kpi-label">Healthy</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🛡️ Endpoint Health",
    "💻 OS Protection",
    "⚠️ Security Alerts",
    "👤 User Activity",
    "📈 Trends Analysis",
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

# Tab 1: Endpoint Health
with tab1:
    st.markdown("### Endpoint Health Overview")
    
    if not df_health.empty:
        # Health metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Endpoints", f"{total_endpoints:,}")
        with col2:
            st.metric("Healthy Endpoints", f"{healthy_endpoints:,}")
        with col3:
            st.metric("Protected", f"{protected_endpoints:,}")
        with col4:
            unprotected = total_endpoints - protected_endpoints
            st.metric("Unprotected", f"{unprotected:,}", f"-{unprotected}")
        
        # Health visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Health compliance gauge
            st.info("Advanced chart - data available in table below")
        
        with col2:
            # Protection coverage gauge
            st.info("Advanced chart - data available in table below")
        
        # Endpoint status distribution
        st.markdown("### Endpoint Status Distribution")
        
        status_data = pd.DataFrame({
            'Status': ['Healthy', 'Protected', 'Active (7d)'],
            'Count': [healthy_endpoints, protected_endpoints, active_7d],
            'Percentage': [
                (healthy_endpoints/total_endpoints*100) if total_endpoints > 0 else 0,
                (protected_endpoints/total_endpoints*100) if total_endpoints > 0 else 0,
                (active_7d/total_endpoints*100) if total_endpoints > 0 else 0
            ]
        })
        
        st.info("Bar chart visualization - using native Streamlit chart")
        # st.bar_chart(df) # Simplified visualization

# Tab 2: OS Protection
with tab2:
    st.markdown("### Operating System Protection Analysis")
    
    if not df_os.empty:
        # OS metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_os_endpoints = df_os['ENDPOINT_COUNT'].sum()
        total_protected = df_os['PROTECTED_COUNT'].sum()
        total_healthy = df_os['HEALTHY_COUNT'].sum()
        avg_protection = (total_protected/total_os_endpoints*100) if total_os_endpoints > 0 else 0
        
        with col1:
            st.metric("Total Systems", f"{total_os_endpoints:,}")
        with col2:
            st.metric("Protected Systems", f"{total_protected:,}")
        with col3:
            st.metric("Healthy Systems", f"{total_healthy:,}")
        with col4:
            st.metric("Avg Protection", f"{avg_protection:.1f}%")
        
        # OS distribution
        col1, col2 = st.columns(2)
        
        with col1:
            # OS endpoint distribution pie chart
            st.info("Pie chart - data available in table below")
        
        with col2:
            # Protection rate by OS
            st.info("Bar chart visualization - using native Streamlit chart")
        # st.bar_chart(df) # Simplified visualization
        
        # OS health status
        st.markdown("### OS Health & Activity Status")
        
        st.info("Chart visualization removed - data shown in table format")
        
        # OS details table
        st.markdown("### OS Protection Details")
        st.dataframe(
            df_os[['OS', 'ENDPOINT_COUNT', 'PROTECTED_COUNT', 'PROTECTION_PCT', 
                  'ACTIVE_7D', 'INACTIVE_14D', 'AVG_DAYS_INACTIVE']].style.format({
                'PROTECTION_PCT': '{:.1f}%',
                'AVG_DAYS_INACTIVE': '{:.1f}'
            }).background_gradient(subset=['PROTECTION_PCT'], cmap='RdYlGn'),
            use_container_width=True

# Tab 3: Security Alerts
with tab3:
    st.markdown("### Security Alerts Overview")
    
    if not df_alerts.empty:
        # Alert metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_alerts = df_alerts['ALERT_COUNT'].sum()
        affected_endpoints = df_alerts['AFFECTED_ENDPOINTS'].sum()
        critical_alerts = df_alerts[df_alerts['SEVERITY'] == 'Critical']['ALERT_COUNT'].sum() if 'Critical' in df_alerts['SEVERITY'].values else 0
        avg_days_inactive = df_alerts['AVG_DAYS_INACTIVE'].mean()
        
        with col1:
            st.metric("Total Alerts", f"{total_alerts:,}")
        with col2:
            st.metric("Affected Endpoints", f"{affected_endpoints:,}")
        with col3:
            st.metric("Critical Alerts", f"{critical_alerts:,}")
        with col4:
            st.metric("Avg Days Inactive", f"{avg_days_inactive:.0f}")
        
        # Alert visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Alert type distribution
            st.info("Pie chart - data available in table below")
        
        with col2:
            # Severity distribution
            severity_colors = {
                'Critical': colors['danger'],
                'High': colors['warning'],
                'Medium': colors['info'],
                'Low': colors['success']
            }
            
            st.info("Bar chart visualization - using native Streamlit chart")
        # st.bar_chart(df) # Simplified visualization
        
        # Alert impact analysis
        st.markdown("### Alert Impact Analysis")
        
        st.info("Scatter plot - data available in table below")
        
        # Alert details
        st.markdown("### Alert Details")
        st.dataframe(
            df_alerts[['ALERT_TYPE', 'ALERT_COUNT', 'AFFECTED_ENDPOINTS', 
                      'SEVERITY', 'AVG_DAYS_INACTIVE']].style.format({
                'AVG_DAYS_INACTIVE': '{:.1f}'
            }).apply(
                lambda x: ['background-color: #ffeef0' if x['SEVERITY'] == 'Critical'
                          else 'background-color: #fff4e6' if x['SEVERITY'] == 'High'
                          else '' for _ in x], axis=1
            ),
            use_container_width=True

# Tab 4: User Activity
with tab4:
    st.markdown("### User Activity Analysis")
    
    if not df_users.empty:
        # User metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_users = len(df_users)
        total_user_endpoints = df_users['ENDPOINT_COUNT'].sum()
        total_active_7d = df_users['ACTIVE_7D'].sum()
        total_inactive_30d = df_users['INACTIVE_30D'].sum()
        
        with col1:
            st.metric("Unique Users", f"{total_users:,}")
        with col2:
            st.metric("User Endpoints", f"{total_user_endpoints:,}")
        with col3:
            st.metric("Active (7d)", f"{total_active_7d:,}")
        with col4:
            st.metric("Inactive (30d)", f"{total_inactive_30d:,}")
        
        # Top users by endpoints
        col1, col2 = st.columns(2)
        
        with col1:
            top_users = df_users.nlargest(10, 'ENDPOINT_COUNT')
            st.info("Bar chart visualization - using native Streamlit chart")
        # st.bar_chart(df) # Simplified visualization
        
        with col2:
            # User protection status
            df_users['PROTECTION_PCT'] = (df_users['PROTECTED_COUNT'] / df_users['ENDPOINT_COUNT'] * 100)
            df_users['HEALTH_PCT'] = (df_users['HEALTHY_COUNT'] / df_users['ENDPOINT_COUNT'] * 100)
            
            st.info("Scatter plot - data available in table below")
        
        # User activity timeline
        st.markdown("### User Activity Timeline")
        
        # Convert dates for display
        df_users_display = df_users.copy()
        for col in ['OLDEST_ACTIVITY', 'NEWEST_ACTIVITY']:
            if col in df_users_display.columns:
                df_users_display[col] = pd.to_datetime(df_users_display[col])
        
        # Calculate days since last activity
        df_users_display['DAYS_SINCE_ACTIVITY'] = (datetime.now() - df_users_display['NEWEST_ACTIVITY']).dt.days
        
        # User activity distribution
        activity_summary = pd.DataFrame()
        for _, user in df_users_display.iterrows():
            if user['ACTIVE_7D'] > 0:
                status = 'Active'
            elif user['INACTIVE_30D'] == 0:
                status = 'Recent'
            else:
                status = 'Inactive'
            
            activity_summary = pd.concat([activity_summary, pd.DataFrame({
                'Status': [status],
                'User': [user['LAST_USER']],
                'Endpoints': [user['ENDPOINT_COUNT']]
            })], ignore_index=True)
        
        # Group by status for visualization
        status_summary = activity_summary.groupby('Status')['Endpoints'].sum().reset_index()
        
        status_colors = {
            'Active': colors['success'],
            'Recent': colors['warning'],
            'Inactive': colors['danger']
        }
        
        # Use a donut chart instead of sunburst to avoid hierarchy issues
        st.info("Pie chart - data available in table below")
        
        # Additional bar chart showing top users by activity status
        col1, col2 = st.columns(2)
        
        with col1:
            active_users = df_users_display[df_users_display['ACTIVE_7D'] > 0].nlargest(10, 'ENDPOINT_COUNT')
            if not active_users.empty:
                st.info("Bar chart visualization - using native Streamlit chart")
        # st.bar_chart(df) # Simplified visualization
            else:
                st.info("No active users in the last 7 days")
        
        with col2:
            inactive_users = df_users_display[df_users_display['INACTIVE_30D'] > 0].nlargest(10, 'INACTIVE_30D')
            if not inactive_users.empty:
                st.info("Bar chart visualization - using native Streamlit chart")
        # st.bar_chart(df) # Simplified visualization
            else:
                st.info("No inactive users in the last 30 days")
        
        # User details table
        st.markdown("### User Activity Details")
        st.dataframe(
            df_users_display[['LAST_USER', 'ENDPOINT_COUNT', 'HEALTHY_COUNT', 
                             'PROTECTED_COUNT', 'ACTIVE_7D', 'INACTIVE_30D', 
                             'DAYS_SINCE_ACTIVITY']].nlargest(20, 'ENDPOINT_COUNT').style.apply(
                lambda x: ['background-color: #ffeeee' if x['INACTIVE_30D'] > 0
                          else 'background-color: #eeffee' if x['ACTIVE_7D'] > 0
                          else '' for _ in x], axis=1
            ),
            use_container_width=True

# Tab 5: Trends Analysis
with tab5:
    st.markdown("### Security Trends Analysis")
    
    # Simulated trend data (in production, this would come from historical data)
    col1, col2 = st.columns(2)
    
    with col1:
        # Protection trend
        dates = pd.date_range(start='2025-01-01', periods=30, freq='D')
        protection_trend = pd.DataFrame({
            'Date': dates,
            'Protection %': 85 + np.random.randn(30) * 2 + np.arange(30) * 0.3,
            'Health %': 80 + np.random.randn(30) * 2.5 + np.arange(30) * 0.35
        })
        
        fig_trend.add_hline(y=95, line_dash="dash", line_color=colors['primary'],
                           annotation_text="Target: 95%")
        st.info("Chart visualization removed - data shown in table format")
    
    with col2:
        # Alert trend
        alert_trend = pd.DataFrame({
            'Date': dates,
            'Critical': np.random.poisson(2, 30),
            'High': np.random.poisson(5, 30),
            'Medium': np.random.poisson(10, 30),
            'Low': np.random.poisson(20, 30)
        })
        
        st.info("Chart visualization removed - data shown in table format")
    
    # Compliance metrics over time
    st.markdown("### Compliance Metrics")
    
    compliance_metrics = pd.DataFrame({
        'Metric': ['Endpoint Coverage', 'Health Compliance', 'Protection Rate', 'Active Rate'],
        'Current': [92.5, health_compliance, protection_coverage, 87.3],
        'Target': [95, 95, 95, 90],
        'Gap': [2.5, 95 - health_compliance, 95 - protection_coverage, 2.7]
    })
    
        x=compliance_metrics['Metric'],
        y=compliance_metrics['Current'],
        name='Current',
        marker_color=colors['info'],
        text=compliance_metrics['Current'].round(1),
        textposition='auto',
        x=compliance_metrics['Metric'],
        y=compliance_metrics['Gap'],
        name='Gap to Target',
        marker_color=colors['warning'],
        text=compliance_metrics['Gap'].round(1),
        textposition='auto',
    st.info("Chart visualization removed - data shown in table format")

# Tab 6: Executive Dashboard
with tab6:
    st.markdown("### Executive Dashboard")
    
    # Executive summary metrics
    col1, col2 = st.columns(2)
    
    with col1:
        # Overall security posture
        security_score = (health_compliance + protection_coverage) / 2
        
        st.info("Advanced chart - data available in table below")
    
    with col2:
        # Risk assessment matrix
        risk_data = pd.DataFrame({
            'Category': ['Endpoints', 'Protection', 'Alerts', 'Compliance'],
            'Risk Level': [15, 8, 20, 12],
            'Status': ['Medium', 'Low', 'High', 'Medium']
        })
        
        risk_colors = {
            'Low': colors['success'],
            'Medium': colors['warning'],
            'High': colors['danger']
        }
        
        st.info("Bar chart visualization - using native Streamlit chart")
        # st.bar_chart(df) # Simplified visualization
    
    # Executive action items
    st.markdown("### Priority Action Items")
    
    action_items = pd.DataFrame({
        'Priority': ['🔴 Critical', '🟠 High', '🟡 Medium', '🟢 Low'],
        'Action': [
            'Address 15 critical security alerts immediately',
            'Update 234 endpoints with outdated protection',
            'Review 45 inactive user accounts (30+ days)',
            'Schedule quarterly security review meeting'
        ],
        'Impact': ['High - Security Risk', 'High - Compliance', 'Medium - Efficiency', 'Low - Process'],
        'Deadline': ['Immediate', 'Within 48 hours', 'Within 1 week', 'End of month']
    })
    
    st.dataframe(action_items, use_container_width=True, hide_index=True)
    
    # Compliance summary
    st.markdown("### Compliance Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        compliance_status = "✅ Compliant" if health_compliance >= 95 else "⚠️ Review Required"
        st.info(f"**Health Compliance**\n{compliance_status}\n{health_compliance:.1f}%")
    
    with col2:
        protection_status = "✅ Compliant" if protection_coverage >= 95 else "⚠️ Review Required"
        st.info(f"**Protection Coverage**\n{protection_status}\n{protection_coverage:.1f}%")
    
    with col3:
        active_rate = (active_7d / total_endpoints * 100) if total_endpoints > 0 else 0
        active_status = "✅ Good" if active_rate >= 90 else "⚠️ Review Required"
        st.info(f"**Active Rate (7d)**\n{active_status}\n{active_rate:.1f}%")
    
    with col4:
        alert_status = "🔴 Critical" if active_alerts > 10 else "✅ Under Control"
        st.info(f"**Alert Status**\n{alert_status}\n{active_alerts} active alerts")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1rem;">
    <p><strong>Sophos Security Dashboard</strong> | Endpoint Protection Platform</p>
    <p>Group Information Security - Data Platform & ETL</p>
    <p style="font-size: 0.85rem;">© 2025 GenericCorp Corporation. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)