# Import python packages
import streamlit as st
import pandas as pd
# import plotly.express as px  # Not available in Snowflake
# import plotly.graph_objects as go  # Not available in Snowflake
# from plotly.subplots import make_subplots  # Not available in Snowflake
import altair as alt
from snowflake.snowpark.context import get_active_session
from datetime import datetime, timedelta
# import numpy as np  # Not available in Snowflake

# Page config
st.set_page_config(
    page_title="Ancon Security Dashboard",
    page_icon="🔐",
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
    .status-compliant { color: #27ae60; font-weight: bold; }
    .status-warning { color: #f39c12; font-weight: bold; }
    .status-critical { color: #e74c3c; font-weight: bold; }
    .status-info { color: #3498db; font-weight: bold; }
    
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
        <span style="font-size: 2.5rem;">🔐</span> Ancon Security Dashboard
    </h1>
    <p style="text-align: center; margin: 0.75rem 0 0 0; opacity: 0.9; position: relative; z-index: 1; font-size: 1.1rem;">
        Group Information Security - Identity & Access Management
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar with controls
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #0a3d62, #1e5f8e); border-radius: 12px; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(10, 61, 98, 0.2);">
        <h2 style="color: white; margin: 0; font-size: 1.5rem;">🏢 GenericCorp</h2>
        <p style="color: #e8f0f8; font-size: 0.95rem; margin-top: 0.5rem;">Identity Security</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filters
    st.header("📊 Dashboard Filters")
    
    # Compliance filter
    compliance_filter = st.multiselect(
        "Compliance Status",
        ["Compliant", "Warning", "Critical", "All"],
        default=["All"],
        help="Filter by compliance status"
    )
    
    # Alert type filter
    alert_filter = st.multiselect(
        "Alert Types",
        ["Password Expiry", "Account Lockout", "Failed Login", "All"],
        default=["All"],
        help="Filter by alert types"
    )
    
    # Date range
    date_range = st.selectbox(
        "Time Period",
        ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 90 Days"],
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
    - Account Compliance
    - Password Policies
    - Login Activity
    - Security Alerts
    - Access Controls
    """)

# Query data
@st.cache_data(ttl=300)
def load_data(query):
    try:
        return session.sql(query).to_pandas()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Load all data
account_compliance_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_ANCON_ACCOUNT_COMPLIANCE ORDER BY SNAPSHOT_TS DESC"
security_alerts_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_ANCON_SECURITY_ALERTS ORDER BY ALERT_GENERATED_TIME DESC"
security_metrics_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_ANCON_SECURITY_METRICS ORDER BY METRIC_DATE DESC"
compliance_settings_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_ANCON_COMPLIANCE_SETTINGS"

df_accounts = load_data(account_compliance_query)
df_alerts = load_data(security_alerts_query)
df_metrics = load_data(security_metrics_query)
df_settings = load_data(compliance_settings_query)

# Executive KPIs Section
st.markdown("### 📊 Executive Summary")

# Calculate key metrics
if not df_accounts.empty:
    total_accounts = len(df_accounts)
    compliant_accounts = len(df_accounts[df_accounts['COMPLIANCE_STATUS'] == 'Compliant'])
    disabled_accounts = len(df_accounts[df_accounts['IS_ACCOUNT_DISABLED'] == True])
    locked_accounts = len(df_accounts[df_accounts['IS_LOCKED_OUT'] == True])
    avg_password_age = df_accounts['PASSWORD_AGE_DAYS'].mean()
    compliance_rate = (compliant_accounts / total_accounts * 100) if total_accounts > 0 else 0
else:
    total_accounts = compliant_accounts = disabled_accounts = locked_accounts = 0
    avg_password_age = compliance_rate = 0

# Get alert counts
if not df_alerts.empty:
    critical_alerts = len(df_alerts[df_alerts['ALERT_TYPE'].str.contains('Critical', case=False, na=False)])
    total_alerts_24h = len(df_alerts)  # Assuming data is filtered for last 24h
else:
    critical_alerts = total_alerts_24h = 0

# Display KPIs
kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)

with kpi_col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{total_accounts:,}</div>
        <div class="kpi-label">Total Accounts</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{compliance_rate:.1f}%</div>
        <div class="kpi-label">Compliance Rate</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{locked_accounts:,}</div>
        <div class="kpi-label">Locked Accounts</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{int(avg_password_age)}</div>
        <div class="kpi-label">Avg Password Age</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{critical_alerts:,}</div>
        <div class="kpi-label">Critical Alerts</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col6:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{total_alerts_24h:,}</div>
        <div class="kpi-label">Alerts (24h)</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔐 Account Compliance",
    "⚠️ Security Alerts",
    "📈 Password Analytics",
    "👥 User Activity",
    "📊 Risk Assessment",
    "⚙️ Settings & Policies"
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

# Tab 1: Account Compliance
with tab1:
    st.markdown("### Account Compliance Overview")
    
    if not df_accounts.empty:
        # Compliance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        # Calculate metrics
        expired_passwords = len(df_accounts[df_accounts['PASSWORD_AGE_DAYS'] > 90])
        inactive_accounts = len(df_accounts[df_accounts['DAYS_SINCE_LAST_LOGIN'] > 30])
        high_risk_accounts = len(df_accounts[df_accounts['BAD_PASSWORD_ATTEMPTS'] >= 5])
        
        with col1:
            st.metric("Compliant Accounts", f"{compliant_accounts:,}", 
                     f"{compliance_rate:.1f}%", delta_color="normal")
        with col2:
            st.metric("Expired Passwords", f"{expired_passwords:,}",
                     f"-{expired_passwords/total_accounts*100:.1f}%", delta_color="inverse")
        with col3:
            st.metric("Inactive Accounts", f"{inactive_accounts:,}",
                     f"{inactive_accounts/total_accounts*100:.1f}%", delta_color="inverse")
        with col4:
            st.metric("High Risk", f"{high_risk_accounts:,}",
                     f"{high_risk_accounts/total_accounts*100:.1f}%", delta_color="inverse")
        
        # Compliance distribution
        col1, col2 = st.columns(2)
        
        with col1:
            # Compliance status pie chart
            compliance_counts = df_accounts['COMPLIANCE_STATUS'].value_counts()
            
            fig_compliance = px.pie(
                values=compliance_counts.values,
                names=compliance_counts.index,
                title='Account Compliance Status',
                color_discrete_map={
                    'Compliant': corp_colors['success'],
                    'Warning': corp_colors['warning'],
                    'Critical': corp_colors['danger']
                }
            )
            
            fig_compliance.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            st.plotly_chart(fig_compliance, use_container_width=True)
        
        with col2:
            # Account status breakdown
            status_data = pd.DataFrame({
                'Status': ['Active', 'Disabled', 'Locked'],
                'Count': [
                    len(df_accounts[(df_accounts['IS_ACCOUNT_DISABLED'] == False) & 
                                  (df_accounts['IS_LOCKED_OUT'] == False)]),
                    disabled_accounts,
                    locked_accounts
                ]
            })
            
            fig_status = px.bar(
                status_data,
                x='Status',
                y='Count',
                title='Account Status Distribution',
                color='Status',
                color_discrete_map={
                    'Active': corp_colors['success'],
                    'Disabled': corp_colors['warning'],
                    'Locked': corp_colors['danger']
                }
            )
            
            fig_status.update_layout(
                plot_bgcolor='white',
                showlegend=False
            )
            
            st.plotly_chart(fig_status, use_container_width=True)
        
        # Password age analysis
        st.markdown("### Password Age Analysis")
        
        # Create password age categories
        df_accounts['PASSWORD_AGE_CATEGORY'] = pd.cut(
            df_accounts['PASSWORD_AGE_DAYS'],
            bins=[-np.inf, 30, 60, 90, 180, np.inf],
            labels=['< 30 days', '30-60 days', '60-90 days', '90-180 days', '> 180 days']
        )
        
        age_summary = df_accounts['PASSWORD_AGE_CATEGORY'].value_counts()
        
        fig_age = px.bar(
            x=age_summary.index,
            y=age_summary.values,
            title='Accounts by Password Age',
            labels={'x': 'Password Age', 'y': 'Account Count'},
            color=age_summary.index,
            color_discrete_map={
                '< 30 days': corp_colors['success'],
                '30-60 days': corp_colors['secondary'],
                '60-90 days': corp_colors['tertiary'],
                '90-180 days': corp_colors['warning'],
                '> 180 days': corp_colors['danger']
            }
        )
        
        fig_age.update_layout(
            plot_bgcolor='white',
            showlegend=False
        )
        
        st.plotly_chart(fig_age, use_container_width=True)
        
        # Non-compliant accounts table
        st.markdown("### Non-Compliant Accounts")
        
        non_compliant = df_accounts[df_accounts['COMPLIANCE_STATUS'] != 'Compliant'].copy()
        
        if not non_compliant.empty:
            display_cols = ['USER_ID', 'EMAIL_ADDRESS', 'PASSWORD_AGE_DAYS', 
                           'DAYS_SINCE_LAST_LOGIN', 'BAD_PASSWORD_ATTEMPTS', 
                           'IS_LOCKED_OUT', 'COMPLIANCE_STATUS']
            
            st.dataframe(
                non_compliant[display_cols].sort_values('COMPLIANCE_STATUS').head(20).style.apply(
                    lambda x: ['background-color: #ffeef0' if x['COMPLIANCE_STATUS'] == 'Critical' 
                              else 'background-color: #fff4e6' if x['COMPLIANCE_STATUS'] == 'Warning'
                              else '' for _ in x], axis=1
                ),
                use_container_width=True,
                height=400
            )

# Tab 2: Security Alerts
with tab2:
    st.markdown("### Security Alerts Overview")
    
    if not df_alerts.empty:
        # Alert summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        # Group alerts by type
        alert_counts = df_alerts['ALERT_TYPE'].value_counts()
        
        # Get top alert types
        top_alert_type = alert_counts.index[0] if not alert_counts.empty else "N/A"
        top_alert_count = alert_counts.iloc[0] if not alert_counts.empty else 0
        
        with col1:
            st.metric("Total Alerts", f"{len(df_alerts):,}")
        with col2:
            st.metric("Unique Users", f"{df_alerts['USERNAME'].nunique():,}")
        with col3:
            st.metric("Top Alert Type", top_alert_type)
        with col4:
            st.metric("Critical Alerts", f"{critical_alerts:,}")
        
        # Alert distribution visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Alerts by type
            fig_alert_types = px.bar(
                x=alert_counts.index[:10],
                y=alert_counts.values[:10],
                title='Top 10 Alert Types',
                labels={'x': 'Alert Type', 'y': 'Count'},
                color=alert_counts.values[:10],
                color_continuous_scale=[corp_colors['tertiary'], corp_colors['warning'], corp_colors['danger']]
            )
            
            fig_alert_types.update_layout(
                plot_bgcolor='white',
                showlegend=False
            )
            
            st.plotly_chart(fig_alert_types, use_container_width=True)
        
        with col2:
            # Alert timeline
            df_alerts['ALERT_DATE'] = pd.to_datetime(df_alerts['ALERT_GENERATED_TIME']).dt.date
            alert_timeline = df_alerts.groupby('ALERT_DATE').size().reset_index(name='COUNT')
            
            fig_timeline = px.line(
                alert_timeline,
                x='ALERT_DATE',
                y='COUNT',
                title='Alert Trend Over Time',
                markers=True,
                line_shape='spline'
            )
            
            fig_timeline.update_traces(
                line_color=corp_colors['primary'],
                marker_color=corp_colors['secondary']
            )
            
            fig_timeline.update_layout(
                plot_bgcolor='white',
                xaxis_title='Date',
                yaxis_title='Alert Count'
            )
            
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # User alert analysis
        st.markdown("### Top Users by Alert Count")
        
        user_alerts = df_alerts.groupby('USERNAME').agg({
            'ALERT_TYPE': 'count',
            'EMAIL_ADDRESS': 'first'
        }).rename(columns={'ALERT_TYPE': 'ALERT_COUNT'}).sort_values('ALERT_COUNT', ascending=False)
        
        fig_user_alerts = px.bar(
            x=user_alerts.index[:15],
            y=user_alerts['ALERT_COUNT'][:15],
            title='Top 15 Users with Most Alerts',
            labels={'x': 'Username', 'y': 'Alert Count'},
            color=user_alerts['ALERT_COUNT'][:15],
            color_continuous_scale='Reds'
        )
        
        fig_user_alerts.update_layout(
            plot_bgcolor='white',
            showlegend=False
        )
        
        st.plotly_chart(fig_user_alerts, use_container_width=True)
        
        # Recent alerts table
        st.markdown("### Recent Security Alerts")
        
        display_cols = ['USERNAME', 'EMAIL_ADDRESS', 'ALERT_TYPE', 'DESCRIPTION', 'ALERT_GENERATED_TIME']
        
        st.dataframe(
            df_alerts[display_cols].head(20),
            use_container_width=True,
            height=400
        )

# Tab 3: Password Analytics
with tab3:
    st.markdown("### Password Security Analytics")
    
    if not df_accounts.empty:
        # Password metrics overview
        col1, col2, col3, col4 = st.columns(4)
        
        # Calculate password metrics
        avg_password_age = df_accounts['PASSWORD_AGE_DAYS'].mean()
        max_password_age = df_accounts['PASSWORD_AGE_DAYS'].max()
        passwords_expiring_soon = len(df_accounts[(df_accounts['PASSWORD_AGE_DAYS'] >= 75) & 
                                                 (df_accounts['PASSWORD_AGE_DAYS'] < 90)])
        never_changed = len(df_accounts[df_accounts['PASSWORD_AGE_DAYS'] > 365])
        
        with col1:
            st.metric("Avg Password Age", f"{avg_password_age:.0f} days")
        with col2:
            st.metric("Max Password Age", f"{max_password_age:.0f} days")
        with col3:
            st.metric("Expiring Soon (<15d)", f"{passwords_expiring_soon:,}")
        with col4:
            st.metric("Never Changed (>365d)", f"{never_changed:,}")
        
        # Password age distribution
        col1, col2 = st.columns(2)
        
        with col1:
            # Histogram of password ages
            fig_hist = px.histogram(
                df_accounts,
                x='PASSWORD_AGE_DAYS',
                nbins=30,
                title='Password Age Distribution',
                labels={'PASSWORD_AGE_DAYS': 'Days Since Last Change'},
                color_discrete_sequence=[corp_colors['primary']]
            )
            
            # Add policy line at 90 days
            fig_hist.add_vline(x=90, line_dash="dash", line_color=corp_colors['danger'],
                             annotation_text="Policy: 90 days")
            
            fig_hist.update_layout(
                plot_bgcolor='white',
                showlegend=False
            )
            
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Password strength gauge
            password_strength_score = 100 - (expired_passwords / total_accounts * 100)
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = password_strength_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Password Policy Compliance", 'font': {'color': corp_colors['primary']}},
                delta = {'reference': 95, 'position': "bottom", 'font': {'color': corp_colors['dark']}},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': corp_colors['secondary'] if password_strength_score >= 90 else 
                           corp_colors['warning'] if password_strength_score >= 70 else corp_colors['danger']},
                    'steps': [
                        {'range': [0, 70], 'color': corp_colors['light']},
                        {'range': [70, 90], 'color': '#dfe6e9'}
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
        
        # Failed login attempts analysis
        st.markdown("### Failed Login Attempts Analysis")
        
        # Create categories for failed attempts
        df_accounts['ATTEMPT_CATEGORY'] = pd.cut(
            df_accounts['BAD_PASSWORD_ATTEMPTS'].fillna(0),
            bins=[-np.inf, 0, 3, 5, 10, np.inf],
            labels=['None', '1-3 attempts', '4-5 attempts', '6-10 attempts', '> 10 attempts']
        )
        
        attempt_summary = df_accounts['ATTEMPT_CATEGORY'].value_counts()
        
        fig_attempts = px.pie(
            values=attempt_summary.values,
            names=attempt_summary.index,
            title='Failed Login Attempt Distribution',
            color_discrete_map={
                'None': corp_colors['success'],
                '1-3 attempts': corp_colors['secondary'],
                '4-5 attempts': corp_colors['tertiary'],
                '6-10 attempts': corp_colors['warning'],
                '> 10 attempts': corp_colors['danger']
            }
        )
        
        fig_attempts.update_layout(
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig_attempts, use_container_width=True)

# Tab 4: User Activity
with tab4:
    st.markdown("### User Activity Monitoring")
    
    if not df_accounts.empty:
        # Activity metrics
        col1, col2, col3, col4 = st.columns(4)
        
        # Calculate activity metrics
        active_users = len(df_accounts[df_accounts['DAYS_SINCE_LAST_LOGIN'] <= 7])
        inactive_30d = len(df_accounts[df_accounts['DAYS_SINCE_LAST_LOGIN'] > 30])
        inactive_90d = len(df_accounts[df_accounts['DAYS_SINCE_LAST_LOGIN'] > 90])
        avg_days_since_login = df_accounts['DAYS_SINCE_LAST_LOGIN'].mean()
        
        with col1:
            st.metric("Active Users (7d)", f"{active_users:,}",
                     f"{active_users/total_accounts*100:.1f}%")
        with col2:
            st.metric("Inactive (>30d)", f"{inactive_30d:,}",
                     f"{inactive_30d/total_accounts*100:.1f}%")
        with col3:
            st.metric("Inactive (>90d)", f"{inactive_90d:,}",
                     f"{inactive_90d/total_accounts*100:.1f}%")
        with col4:
            st.metric("Avg Days Since Login", f"{avg_days_since_login:.0f}")
        
        # Activity distribution
        col1, col2 = st.columns(2)
        
        with col1:
            # Login activity categories
            df_accounts['ACTIVITY_CATEGORY'] = pd.cut(
                df_accounts['DAYS_SINCE_LAST_LOGIN'].fillna(999),
                bins=[-np.inf, 7, 30, 90, 180, np.inf],
                labels=['Active (≤7d)', 'Recent (7-30d)', 'Inactive (30-90d)', 
                       'Dormant (90-180d)', 'Abandoned (>180d)']
            )
            
            activity_dist = df_accounts['ACTIVITY_CATEGORY'].value_counts()
            
            fig_activity = px.bar(
                x=activity_dist.index,
                y=activity_dist.values,
                title='User Activity Distribution',
                labels={'x': 'Activity Status', 'y': 'User Count'},
                color=activity_dist.index,
                color_discrete_map={
                    'Active (≤7d)': corp_colors['success'],
                    'Recent (7-30d)': corp_colors['secondary'],
                    'Inactive (30-90d)': corp_colors['tertiary'],
                    'Dormant (90-180d)': corp_colors['warning'],
                    'Abandoned (>180d)': corp_colors['danger']
                }
            )
            
            fig_activity.update_layout(
                plot_bgcolor='white',
                showlegend=False
            )
            
            st.plotly_chart(fig_activity, use_container_width=True)
        
        with col2:
            # Account status vs activity
            activity_status = df_accounts.groupby(['IS_LOCKED_OUT', 'IS_ACCOUNT_DISABLED']).size().reset_index(name='COUNT')
            
            # Create labels for combinations
            activity_status['STATUS'] = activity_status.apply(
                lambda x: 'Locked' if x['IS_LOCKED_OUT'] else ('Disabled' if x['IS_ACCOUNT_DISABLED'] else 'Active'),
                axis=1
            )
            
            fig_status_pie = px.pie(
                activity_status,
                values='COUNT',
                names='STATUS',
                title='Account Status Breakdown',
                color_discrete_map={
                    'Active': corp_colors['success'],
                    'Disabled': corp_colors['warning'],
                    'Locked': corp_colors['danger']
                }
            )
            
            fig_status_pie.update_layout(
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig_status_pie, use_container_width=True)
        
        # Inactive users table
        st.markdown("### Inactive Users (>30 days)")
        
        inactive_users = df_accounts[df_accounts['DAYS_SINCE_LAST_LOGIN'] > 30].copy()
        inactive_users = inactive_users.sort_values('DAYS_SINCE_LAST_LOGIN', ascending=False)
        
        if not inactive_users.empty:
            display_cols = ['USER_ID', 'EMAIL_ADDRESS', 'DAYS_SINCE_LAST_LOGIN', 
                           'PASSWORD_AGE_DAYS', 'IS_LOCKED_OUT', 'COMPLIANCE_STATUS']
            
            st.dataframe(
                inactive_users[display_cols].head(20),
                use_container_width=True,
                height=400
            )

# Tab 5: Risk Assessment
with tab5:
    st.markdown("### Security Risk Assessment")
    
    # Risk Score Calculation
    if not df_accounts.empty:
        # Calculate risk scores for each account
        df_accounts['RISK_SCORE'] = 0
        df_accounts.loc[df_accounts['PASSWORD_AGE_DAYS'] > 90, 'RISK_SCORE'] += 30
        df_accounts.loc[df_accounts['PASSWORD_AGE_DAYS'] > 180, 'RISK_SCORE'] += 20
        df_accounts.loc[df_accounts['DAYS_SINCE_LAST_LOGIN'] > 30, 'RISK_SCORE'] += 20
        df_accounts.loc[df_accounts['DAYS_SINCE_LAST_LOGIN'] > 90, 'RISK_SCORE'] += 10
        df_accounts.loc[df_accounts['BAD_PASSWORD_ATTEMPTS'] >= 5, 'RISK_SCORE'] += 20
        df_accounts.loc[df_accounts['IS_LOCKED_OUT'] == True, 'RISK_SCORE'] += 10
        
        # Risk categories
        df_accounts['RISK_CATEGORY'] = pd.cut(
            df_accounts['RISK_SCORE'],
            bins=[-np.inf, 20, 40, 60, np.inf],
            labels=['Low', 'Medium', 'High', 'Critical']
        )
        
        # Risk overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        risk_dist = df_accounts['RISK_CATEGORY'].value_counts()
        
        with col1:
            critical_risk_count = risk_dist.get('Critical', 0)
            st.metric("Critical Risk", f"{critical_risk_count:,}")
        with col2:
            high_risk_count = risk_dist.get('High', 0)
            st.metric("High Risk", f"{high_risk_count:,}")
        with col3:
            avg_risk_score = df_accounts['RISK_SCORE'].mean()
            st.metric("Avg Risk Score", f"{avg_risk_score:.1f}")
        with col4:
            max_risk_score = df_accounts['RISK_SCORE'].max()
            st.metric("Max Risk Score", f"{max_risk_score:.0f}")
        
        # Risk visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk distribution
            fig_risk_dist = px.pie(
                values=risk_dist.values,
                names=risk_dist.index,
                title='Account Risk Distribution',
                color_discrete_map={
                    'Low': corp_colors['success'],
                    'Medium': corp_colors['warning'],
                    'High': '#e67e22',
                    'Critical': corp_colors['danger']
                }
            )
            
            fig_risk_dist.update_layout(
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig_risk_dist, use_container_width=True)
        
        with col2:
            # Risk score histogram
            fig_risk_hist = px.histogram(
                df_accounts,
                x='RISK_SCORE',
                nbins=20,
                title='Risk Score Distribution',
                labels={'RISK_SCORE': 'Risk Score'},
                color_discrete_sequence=[corp_colors['primary']]
            )
            
            fig_risk_hist.update_layout(
                plot_bgcolor='white',
                showlegend=False
            )
            
            st.plotly_chart(fig_risk_hist, use_container_width=True)
        
        # Risk matrix heatmap
        st.markdown("### Risk Matrix: Password Age vs Login Activity")
        
        # Create risk matrix data
        risk_matrix = pd.crosstab(
            pd.cut(df_accounts['PASSWORD_AGE_DAYS'], 
                  bins=[0, 30, 60, 90, 180, np.inf],
                  labels=['0-30', '30-60', '60-90', '90-180', '>180']),
            pd.cut(df_accounts['DAYS_SINCE_LAST_LOGIN'].fillna(999),
                  bins=[0, 7, 30, 90, np.inf],
                  labels=['0-7', '7-30', '30-90', '>90'])
        )
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=risk_matrix.values,
            x=risk_matrix.columns,
            y=risk_matrix.index,
            colorscale=[[0, corp_colors['success']], 
                       [0.5, corp_colors['warning']], 
                       [1, corp_colors['danger']]],
            text=risk_matrix.values,
            texttemplate="%{text}",
            textfont={"size": 12}
        ))
        
        fig_heatmap.update_layout(
            title='Risk Heatmap: Password Age vs Days Since Login',
            xaxis_title='Days Since Last Login',
            yaxis_title='Password Age (Days)',
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # High risk accounts table
        st.markdown("### High Risk Accounts")
        
        high_risk = df_accounts[df_accounts['RISK_CATEGORY'].isin(['Critical', 'High'])].copy()
        high_risk = high_risk.sort_values('RISK_SCORE', ascending=False)
        
        if not high_risk.empty:
            display_cols = ['USER_ID', 'EMAIL_ADDRESS', 'RISK_SCORE', 'RISK_CATEGORY',
                           'PASSWORD_AGE_DAYS', 'DAYS_SINCE_LAST_LOGIN', 'BAD_PASSWORD_ATTEMPTS']
            
            st.dataframe(
                high_risk[display_cols].head(20).style.apply(
                    lambda x: ['background-color: #ffeef0' if x['RISK_CATEGORY'] == 'Critical' 
                              else 'background-color: #fff4e6' if x['RISK_CATEGORY'] == 'High'
                              else '' for _ in x], axis=1
                ),
                use_container_width=True,
                height=400
            )

# Tab 6: Settings & Policies
with tab6:
    st.markdown("### Security Settings & Policies")
    
    # Display compliance settings
    if not df_settings.empty:
        st.markdown("#### Current Policy Settings")
        
        col1, col2, col3 = st.columns(3)
        
        for idx, setting in df_settings.iterrows():
            with [col1, col2, col3][idx % 3]:
                st.info(f"**{setting['PARAMETER_NAME']}**\n\n"
                       f"Value: {setting['PARAMETER_VALUE']}\n\n"
                       f"{setting['DESCRIPTION']}")
    
    # Security metrics overview
    if not df_metrics.empty:
        st.markdown("#### Security Metrics Summary")
        
        latest_metrics = df_metrics.iloc[0] if not df_metrics.empty else None
        
        if latest_metrics is not None:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Metric Category", latest_metrics['METRIC_CATEGORY'])
            with col2:
                st.metric("Expired Passwords", f"{latest_metrics['EXPIRED_PASSWORDS']:,}")
            with col3:
                st.metric("Never Changed", f"{latest_metrics['NEVER_CHANGED_PASSWORDS']:,}")
            with col4:
                # Convert date to string to avoid type error
                metric_date = latest_metrics['METRIC_DATE']
                if hasattr(metric_date, 'strftime'):
                    metric_date = metric_date.strftime('%Y-%m-%d')
                else:
                    metric_date = str(metric_date)
                st.metric("Metric Date", metric_date)
        
        # Metrics trend
        if len(df_metrics) > 1:
            fig_trend = go.Figure()
            
            fig_trend.add_trace(go.Scatter(
                x=df_metrics['METRIC_DATE'],
                y=df_metrics['EXPIRED_PASSWORDS'],
                mode='lines+markers',
                name='Expired Passwords',
                line=dict(color=corp_colors['danger'], width=2)
            ))
            
            fig_trend.add_trace(go.Scatter(
                x=df_metrics['METRIC_DATE'],
                y=df_metrics['NEVER_CHANGED_PASSWORDS'],
                mode='lines+markers',
                name='Never Changed',
                line=dict(color=corp_colors['warning'], width=2)
            ))
            
            fig_trend.update_layout(
                title='Security Metrics Trend',
                xaxis_title='Date',
                yaxis_title='Count',
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
    
    # Recommendations
    st.markdown("#### Security Recommendations")
    
    recommendations = []
    
    if expired_passwords > total_accounts * 0.1:
        recommendations.append("⚠️ **High number of expired passwords**: Implement automated password expiration notifications")
    
    if inactive_30d > total_accounts * 0.2:
        recommendations.append("⚠️ **Many inactive accounts**: Consider implementing automatic account deactivation policy")
    
    if locked_accounts > total_accounts * 0.05:
        recommendations.append("⚠️ **High lockout rate**: Review password complexity requirements and user training")
    
    if avg_password_age > 60:
        recommendations.append("ℹ️ **Consider shorter password rotation**: Current average age exceeds 60 days")
    
    if critical_alerts > 10:
        recommendations.append("🚨 **High critical alert volume**: Investigate root causes and implement preventive measures")
    
    if recommendations:
        for rec in recommendations:
            st.markdown(rec)
    else:
        st.success("✅ All security metrics are within acceptable thresholds")
    
    # Compliance dashboard summary
    st.markdown("#### Compliance Dashboard Summary")
    
    summary_data = {
        'Metric': ['Total Accounts', 'Compliance Rate', 'Average Password Age', 
                  'Locked Accounts', 'Critical Alerts', 'High Risk Accounts'],
        'Value': [f"{total_accounts:,}", f"{compliance_rate:.1f}%", f"{avg_password_age:.0f} days",
                 f"{locked_accounts:,}", f"{critical_alerts:,}", 
                 f"{len(df_accounts[df_accounts['RISK_SCORE'] > 60]) if not df_accounts.empty else 0:,}"],
        'Status': ['ℹ️ Info', 
                  '✅ Good' if compliance_rate > 90 else '⚠️ Warning' if compliance_rate > 70 else '🚨 Critical',
                  '✅ Good' if avg_password_age < 60 else '⚠️ Warning' if avg_password_age < 90 else '🚨 Critical',
                  '✅ Good' if locked_accounts < 5 else '⚠️ Warning' if locked_accounts < 10 else '🚨 Critical',
                  '✅ Good' if critical_alerts < 5 else '⚠️ Warning' if critical_alerts < 15 else '🚨 Critical',
                  '✅ Good' if len(df_accounts[df_accounts['RISK_SCORE'] > 60]) < 10 else '🚨 Critical']
    }
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1rem;">
    <p><strong>Alcon Security Dashboard</strong> | Identity & Access Management</p>
    <p>Group Information Security - Analytics Group</p>
    <p style="font-size: 0.85rem; margin-top: 0.5rem;">© 2025 GenericCorp Corporation. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)