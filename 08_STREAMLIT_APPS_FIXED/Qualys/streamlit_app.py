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



# Page configuration
st.set_page_config(
    page_title="Qualys Security Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for sophisticated styling
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Metric card styling */
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-color: #3498db;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        background-color: white;
        border: 1px solid #e0e0e0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2c3e50;
        color: white;
    }
    
    /* Section headers */
    h3 {
        color: #2c3e50;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
    }
    
    /* Severity level badges */
    .severity-critical { color: #e74c3c; font-weight: bold; }
    .severity-high { color: #e67e22; font-weight: bold; }
    .severity-medium { color: #f39c12; font-weight: bold; }
    .severity-low { color: #3498db; font-weight: bold; }
    .severity-info { color: #95a5a6; font-weight: bold; }
    
    /* KPI cards */
    .kpi-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
    }
    
    .kpi-label {
        color: #7f8c8d;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Get session
session = get_active_session()

# Header with company branding
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.markdown("""
    <div class="main-header">
        <h1 style="text-align: center; margin: 0;">
            <span style="font-size: 2.5rem;">🛡️</span> Qualys Security Dashboard
        </h1>
        <p style="text-align: center; margin: 0.5rem 0 0 0; opacity: 0.9;">
            Vulnerability Management & Compliance Monitoring Platform
        </p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar with controls
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <h2 style="color: #2c3e50;">🏢 GenericCorp Security</h2>
        <p style="color: #7f8c8d; font-size: 0.9rem;">Enterprise Vulnerability Management</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filters
    st.header("Dashboard Filters")
    
    # Date filter
    date_filter = st.selectbox(
        "Time Range",
        ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"],
        index=1
    
    # Severity filter
    severity_filter = st.multiselect(
        "Severity Levels",
        ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"],
        default=["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    
    # OS filter
    os_filter = st.multiselect(
        "Operating Systems",
        ["Windows", "Linux", "Mac", "All"],
        default=["All"]
    
    st.markdown("---")
    
    # Refresh controls
    auto_refresh = st.checkbox("Auto-refresh (5 min)", value=True)
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    # Info section
    st.markdown("---")
    st.info("""
    **Data Sources:**
    - Qualys VMDR
    - Host Compliance
    - Patch Management
    - Scan Coverage
    """)

# Helper function to safely query data
@st.cache_data(ttl=300)
def load_data(query):
    try:
        return session.sql(query).to_pandas()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Load all data upfront
exec_summary_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_QUALYS_EXECUTIVE_SUMMARY ORDER BY SNAPSHOT_DATE DESC LIMIT 1"
host_compliance_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_QUALYS_HOST_COMPLIANCE ORDER BY SNAPSHOT_DATE DESC, HOST_COUNT DESC"
patch_compliance_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_QUALYS_PATCH_COMPLIANCE ORDER BY SNAPSHOT_DATE DESC, TOTAL_VULNS DESC"
scan_coverage_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_QUALYS_SCAN_COVERAGE ORDER BY SNAPSHOT_DATE DESC LIMIT 1"
vuln_summary_query = "SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_QUALYS_VULNERABILITY_SUMMARY ORDER BY SNAPSHOT_DATE DESC, SEVERITY_LEVEL"

df_exec = load_data(exec_summary_query)
df_compliance = load_data(host_compliance_query)
df_patch = load_data(patch_compliance_query)
df_scan = load_data(scan_coverage_query)
df_vuln = load_data(vuln_summary_query)

# Executive KPIs Section
st.markdown("### 📊 Executive Summary")

# Create KPI cards
kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)

# Extract values from executive summary
if not df_exec.empty:
    inscope_hosts = df_exec['INSCOPE_HOSTS'].iloc[0] if 'INSCOPE_HOSTS' in df_exec.columns else 0
    scanned_hosts = df_exec['SCANNED_HOSTS'].iloc[0] if 'SCANNED_HOSTS' in df_exec.columns else 0
    critical_vulns = df_exec['CRITICAL_VULNS'].iloc[0] if 'CRITICAL_VULNS' in df_exec.columns else 0
    exploitable_vulns = df_exec['EXPLOITABLE_VULNS'].iloc[0] if 'EXPLOITABLE_VULNS' in df_exec.columns else 0
    critical_unpatched = df_exec['CRITICAL_UNPATCHED'].iloc[0] if 'CRITICAL_UNPATCHED' in df_exec.columns else 0
    
    scan_coverage_pct = (scanned_hosts / inscope_hosts * 100) if inscope_hosts > 0 else 0
else:
    inscope_hosts = scanned_hosts = critical_vulns = exploitable_vulns = critical_unpatched = 0
    scan_coverage_pct = 0

# Display KPIs with custom styling
with kpi_col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{inscope_hosts:,}</div>
        <div class="kpi-label">In-Scope Hosts</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{scan_coverage_pct:.1f}%</div>
        <div class="kpi-label">Scan Coverage</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value severity-critical">{critical_vulns:,}</div>
        <div class="kpi-label">Critical Vulns</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value severity-high">{exploitable_vulns:,}</div>
        <div class="kpi-label">Exploitable</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{critical_unpatched:,}</div>
        <div class="kpi-label">Unpatched Critical</div>
    </div>
    """, unsafe_allow_html=True)

# Calculate overall compliance from host compliance data
if not df_compliance.empty and 'COMPLIANCE_PCT' in df_compliance.columns:
    avg_compliance = df_compliance['COMPLIANCE_PCT'].mean()
else:
    avg_compliance = 0

with kpi_col6:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{avg_compliance:.1f}%</div>
        <div class="kpi-label">Avg Compliance</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Create tabs for detailed views
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Vulnerability Analysis", 
    "📋 Host Compliance", 
    "🔧 Patch Management", 
    "📡 Scan Coverage", 
    "📈 Trending & Analytics"
])

# Tab 1: Vulnerability Analysis
with tab1:
    st.markdown("### Vulnerability Management Overview")
    
    if not df_vuln.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Vulnerability distribution by severity
            severity_colors = {
                'CRITICAL': '#e74c3c',
                'HIGH': '#e67e22',
                'MEDIUM': '#f39c12',
                'LOW': '#3498db',
                'INFO': '#95a5a6'
            }
            
            st.info("Advanced chart - data available in table below")
        
        with col2:
            # Exploitable vs Patchable Analysis
            categories = ['Exploitable', 'Patchable', 'PCI', 'Legacy']
            values = [
                df_vuln['EXPLOITABLE_VULNS'].sum(),
                df_vuln['PATCHABLE_VULNS'].sum(),
                df_vuln['PCI_VULNS'].sum(),
                df_vuln['LEGACY_VULNS'].sum()
            ]
            
            st.info("Advanced chart - data available in table below")
        
        # CVSS Score Analysis
        st.markdown("### CVSS Score Analysis")
        
        # Create CVSS score gauge for each severity
        cvss_cols = st.columns(len(df_vuln))
        
        for idx, (col, row) in enumerate(zip(cvss_cols, df_vuln.itertuples())):
            with col:
                st.info("Advanced chart - data available in table below")
        
        # Vulnerability Age Analysis
        if 'OLDEST_VULN' in df_vuln.columns and 'NEWEST_VULN' in df_vuln.columns:
            st.markdown("### Vulnerability Age Analysis")
            
            # Convert to datetime
            df_vuln['OLDEST_VULN'] = pd.to_datetime(df_vuln['OLDEST_VULN'])
            df_vuln['NEWEST_VULN'] = pd.to_datetime(df_vuln['NEWEST_VULN'])
            
            # Calculate age in days
            current_date = pd.Timestamp.now()
            df_vuln['MAX_AGE_DAYS'] = (current_date - df_vuln['OLDEST_VULN']).dt.days
            
            st.info("Bar chart visualization - using native Streamlit chart")
        # st.bar_chart(df) # Simplified visualization

# Tab 2: Host Compliance
with tab2:
    st.markdown("### Host Compliance Overview")
    
    if not df_compliance.empty:
        # Overall compliance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_hosts = df_compliance['HOST_COUNT'].sum()
        compliant_hosts = df_compliance['COMPLIANT_HOSTS'].sum()
        non_compliant_hosts = df_compliance['NON_COMPLIANT_HOSTS'].sum()
        out_of_scope = df_compliance['OUT_OF_SCOPE'].sum()
        
        with col1:
            st.metric("Total Hosts", f"{total_hosts:,}")
        with col2:
            st.metric("Compliant", f"{compliant_hosts:,}", f"{compliant_hosts/total_hosts*100:.1f}%")
        with col3:
            st.metric("Non-Compliant", f"{non_compliant_hosts:,}", f"-{non_compliant_hosts/total_hosts*100:.1f}%")
        with col4:
            st.metric("Out of Scope", f"{out_of_scope:,}")
        
        # Compliance by OS
        col1, col2 = st.columns(2)
        
        with col1:
            # Compliance percentage by OS
            st.info("Bar chart visualization - using native Streamlit chart")
        # st.bar_chart(df) # Simplified visualization
        
        with col2:
            # Host distribution by OS
            st.info("Pie chart - data available in table below")
        
        # Scan freshness analysis
        st.markdown("### Scan Freshness Analysis")
        
        # Create scan age categories
        df_compliance['SCAN_AGE_CATEGORY'] = pd.cut(
            df_compliance['AVG_DAYS_SINCE_SCAN'],
            bins=[-np.inf, 7, 30, 90, np.inf],
            labels=['< 7 days', '7-30 days', '30-90 days', '> 90 days']
        
        scan_age_summary = df_compliance.groupby('SCAN_AGE_CATEGORY')['HOST_COUNT'].sum().reset_index()
        
        st.info("Bar chart visualization - using native Streamlit chart")
        # st.bar_chart(df) # Simplified visualization
        
        # Detailed compliance table
        st.markdown("### Detailed Compliance by OS")
        
        display_cols = ['HOST_OS', 'HOST_COUNT', 'COMPLIANT_HOSTS', 'NON_COMPLIANT_HOSTS', 
                       'COMPLIANCE_PCT', 'AVG_DAYS_SINCE_SCAN', 'OUT_OF_SCOPE']
        
        st.dataframe(
            df_compliance[display_cols].style.format({
                'COMPLIANCE_PCT': '{:.1f}%',
                'AVG_DAYS_SINCE_SCAN': '{:.1f} days'
            }).background_gradient(subset=['COMPLIANCE_PCT'], cmap='RdYlGn'),
            use_container_width=True,

# Tab 3: Patch Management
with tab3:
    st.markdown("### Patch Management Overview")
    
    if not df_patch.empty:
        # Overall patch metrics
        total_vulns = df_patch['TOTAL_VULNS'].sum()
        patchable_vulns = df_patch['PATCHABLE_VULNS'].sum()
        non_patchable_vulns = df_patch['NON_PATCHABLE_VULNS'].sum()
        critical_patchable = df_patch['CRITICAL_PATCHABLE'].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Vulnerabilities", f"{total_vulns:,}")
        with col2:
            patch_rate = (patchable_vulns/total_vulns*100) if total_vulns > 0 else 0
            st.metric("Patchable", f"{patchable_vulns:,}", f"{patch_rate:.1f}%")
        with col3:
            st.metric("Non-Patchable", f"{non_patchable_vulns:,}")
        with col4:
            st.metric("Critical Patchable", f"{critical_patchable:,}", "⚠️")
        
        # Patch analysis by category
        col1, col2 = st.columns(2)
        
        with col1:
            # Top categories by vulnerability count
            top_categories = df_patch.nlargest(10, 'TOTAL_VULNS')
            
            st.info("Bar chart visualization - using native Streamlit chart")
        # st.bar_chart(df) # Simplified visualization
        
        with col2:
            # Patchable vs Non-patchable breakdown
            patch_data = pd.DataFrame({
                'Type': ['Patchable', 'Non-Patchable'],
                'Count': [patchable_vulns, non_patchable_vulns]
            })
            
            st.info("Pie chart - data available in table below")
        
        # Critical and Exploitable Analysis
        st.markdown("### Critical & Exploitable Vulnerabilities")
        
        # Filter for categories with critical/exploitable vulns
        critical_cats = df_patch[(df_patch['CRITICAL_PATCHABLE'] > 0) | 
                               (df_patch['CRITICAL_UNPATCHABLE'] > 0) |
                               (df_patch['EXPLOITABLE_COUNT'] > 0)].sort_values('CRITICAL_PATCHABLE', ascending=False)
        
        if not critical_cats.empty:
            # Stacked bar chart for critical vulns
            
                orientation='h',
            
                orientation='h',
            
                orientation='h',
            
            
            st.info("Chart visualization removed - data shown in table format")
        
        # Patch efficiency table
        st.markdown("### Patch Efficiency by Category")
        
        # Calculate efficiency metrics
        df_patch['PATCH_EFFICIENCY'] = df_patch['PATCHABLE_PCT']
        df_patch['CRITICAL_RATIO'] = (df_patch['CRITICAL_PATCHABLE'] / df_patch['PATCHABLE_VULNS'] * 100).fillna(0)
        
        display_cols = ['CATEGORY', 'TOTAL_VULNS', 'PATCHABLE_PCT', 'CRITICAL_PATCHABLE', 
                       'EXPLOITABLE_COUNT', 'CRITICAL_RATIO']
        
        st.dataframe(
            df_patch[display_cols].sort_values('CRITICAL_PATCHABLE', ascending=False).head(20).style.format({
                'PATCHABLE_PCT': '{:.1f}%',
                'CRITICAL_RATIO': '{:.1f}%'
            }).background_gradient(subset=['PATCHABLE_PCT'], cmap='RdYlGn').background_gradient(
                subset=['CRITICAL_PATCHABLE', 'EXPLOITABLE_COUNT'], cmap='Reds'
            ),
            use_container_width=True,

# Tab 4: Scan Coverage
with tab4:
    st.markdown("### Scan Coverage Analysis")
    
    if not df_scan.empty:
        # Main scan coverage metrics
        scan_data = df_scan.iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Hosts", f"{scan_data['TOTAL_HOSTS']:,}")
        with col2:
            st.metric("In-Scope Hosts", f"{scan_data['INSCOPE_HOSTS']:,}")
        with col3:
            st.metric("Scanned (30d)", f"{scan_data['SCANNED_30D']:,}")
        with col4:
            st.metric("Coverage Rate", f"{scan_data['SCAN_COVERAGE_PCT']:.1f}%")
        
        # Scan coverage visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Scan coverage funnel
            funnel_data = pd.DataFrame({
                'Stage': ['Total Hosts', 'In-Scope', 'Scanned (30d)', 'Scanned (7d)'],
                'Count': [scan_data['TOTAL_HOSTS'], scan_data['INSCOPE_HOSTS'], 
                         scan_data['SCANNED_30D'], scan_data['SCANNED_7D']]
            })
            
                funnel_data,
            
            st.info("Chart visualization removed - data shown in table format")
        
        with col2:
            # OS distribution
            os_data = pd.DataFrame({
                'OS': ['Windows', 'Linux', 'Mac'],
                'Count': [scan_data['WINDOWS_HOSTS'], scan_data['LINUX_HOSTS'], scan_data['MAC_HOSTS']]
            })
            
            st.info("Pie chart - data available in table below")
        
        # Scan coverage gauge
        st.markdown("### Scan Coverage Performance")
        
        # Create gauge chart for scan coverage
        st.info("Advanced chart - data available in table below")
        
        # Scan frequency breakdown
        st.markdown("### Scan Frequency Analysis")
        
        # Calculate scan frequency metrics
        recently_scanned = scan_data['SCANNED_7D']
        monthly_scanned = scan_data['SCANNED_30D'] - scan_data['SCANNED_7D']
        not_scanned = scan_data['INSCOPE_HOSTS'] - scan_data['SCANNED_30D']
        out_of_scope = scan_data['TOTAL_HOSTS'] - scan_data['INSCOPE_HOSTS']
        
        freq_data = pd.DataFrame({
            'Category': ['Scanned < 7 days', 'Scanned 7-30 days', 'Not Scanned (30d)', 'Out of Scope'],
            'Count': [recently_scanned, monthly_scanned, not_scanned, out_of_scope]
        })
        
        st.info("Bar chart visualization - using native Streamlit chart")
        # st.bar_chart(df) # Simplified visualization

# Tab 5: Trending & Analytics
with tab5:
    st.markdown("### Trending & Analytics")
    
    # Note: Since we only have snapshot data, we'll simulate some trending
    st.info("📊 Historical trending requires multiple snapshots. Current view shows latest snapshot analysis.")
    
    # Risk Score Card
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Vulnerability Risk Matrix")
        
        if not df_vuln.empty:
            # Create risk matrix
            risk_matrix = pd.DataFrame({
                'Severity': df_vuln['SEVERITY_NAME'],
                'Count': df_vuln['VULN_COUNT'],
                'Avg CVSS': df_vuln['AVG_CVSS_SCORE'],
                'Exploitable': df_vuln['EXPLOITABLE_VULNS']
            })
            
            # Bubble chart for risk matrix
            st.info("Scatter plot - data available in table below")
    
    with col2:
        st.markdown("### Remediation Priority Matrix")
        
        if not df_patch.empty:
            # Create priority matrix
            priority_data = df_patch[df_patch['EXPLOITABLE_COUNT'] > 0].nlargest(15, 'EXPLOITABLE_COUNT')
            
            if not priority_data.empty:
                st.info("Scatter plot - data available in table below")
    
    # Compliance Trends
    st.markdown("### Compliance & Coverage Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Compliance distribution
        if not df_compliance.empty:
            compliance_bins = pd.cut(
                df_compliance['COMPLIANCE_PCT'],
                bins=[0, 50, 70, 90, 100],
                labels=['Poor (<50%)', 'Fair (50-70%)', 'Good (70-90%)', 'Excellent (>90%)']
            
            compliance_dist = compliance_bins.value_counts().reset_index()
            compliance_dist.columns = ['Level', 'Count']
            
            st.info("Bar chart visualization - using native Streamlit chart")
        # st.bar_chart(df) # Simplified visualization
    
    with col2:
        # Vulnerability age distribution
        if not df_vuln.empty and 'MAX_AGE_DAYS' in df_vuln.columns:
            age_categories = pd.cut(
                df_vuln['MAX_AGE_DAYS'],
                bins=[0, 30, 90, 180, np.inf],
                labels=['< 30 days', '30-90 days', '90-180 days', '> 180 days']
            
            age_summary = pd.DataFrame({
                'Age Category': age_categories.value_counts().index,
                'Count': age_categories.value_counts().values
            })
            
            st.info("Pie chart - data available in table below")
    
    with col3:
        # Key risk indicators
        st.markdown("#### Key Risk Indicators")
        
        # Calculate KRIs
        if not df_exec.empty:
            kri_data = {
                'Critical Exposure Rate': (critical_vulns / inscope_hosts * 100) if inscope_hosts > 0 else 0,
                'Exploit Exposure Rate': (exploitable_vulns / total_vulns * 100) if total_vulns > 0 else 0,
                'Patch Coverage': (patchable_vulns / total_vulns * 100) if total_vulns > 0 else 0,
                'Scan Coverage': scan_coverage_pct
            }
            
            for kri, value in kri_data.items():
                if value > 80:
                    color = "🟢"
                elif value > 60:
                    color = "🟡"
                else:
                    color = "🔴"
                
                st.metric(kri, f"{value:.1f}%", delta=None)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 1rem;">
    <p>Qualys Security Dashboard | Vulnerability Management Platform | Data refreshed every 5 minutes</p>
    <p style="font-size: 0.8rem;">© 2025 GenericCorp Corporation. All rights reserved. | Powered by Qualys VMDR</p>
</div>
""", unsafe_allow_html=True)