# Python packages
import streamlit as st
import pandas as pd
# import plotly.express as px  # Not available in Snowflake
# import plotly.graph_objects as go  # Not available in Snowflake
# from plotly.subplots import make_subplots  # Not available in Snowflake
import altair as alt
from snowflake.snowpark.context import get_active_session
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="BitSight Security Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
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
        transition: transform 0.3s;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
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
        background-color: #1e3c72;
        color: white;
    }
    
    /* Section headers */
    h3 {
        color: #1e3c72;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
    }
    
    /* Risk level badges */
    .risk-high { color: #dc3545; font-weight: bold; }
    .risk-medium { color: #ffc107; font-weight: bold; }
    .risk-low { color: #28a745; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Get session
session = get_active_session()

# Header
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.markdown("""
    <div class="main-header">
        <h1 style="text-align: center; margin: 0;">
            <span style="font-size: 2.5rem;">🛡️</span> BitSight Security Dashboard
        </h1>
        <p style="text-align: center; margin: 0.5rem 0 0 0; opacity: 0.9;">
            Group Information Security - Data Platform & ETL for Data Management
        </p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar with branding
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <h2 style="color: #1e3c72;">🏢 GenericCorp</h2>
        <p style="color: #666; font-size: 0.9rem;">Enterprise Security Monitoring</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filters
    st.header("Filters")
    
    # Date range filter
    date_range = st.date_input(
        "Date Range",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        key="date_range"
    )
    
    # Risk level filter
    risk_levels = st.multiselect(
        "Risk Levels",
        ["HIGH", "MEDIUM", "LOW", "ABOVE_TARGET", "BELOW_TARGET"],
        default=["HIGH", "MEDIUM", "LOW", "ABOVE_TARGET", "BELOW_TARGET"]
    )
    
    st.markdown("---")
    
    # Refresh controls
    auto_refresh = st.checkbox("Auto-refresh (10 min)", value=True)
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Helper function
@st.cache_data(ttl=600)
def load_data(query):
    try:
        return session.sql(query).to_pandas()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Key Metrics Overview - Top of page
st.markdown("### 📊 Executive Summary")
metrics_col1, metrics_col2, metrics_col3, metrics_col4, metrics_col5 = st.columns(5)

# Load summary data
critical_count_query = """
SELECT COUNT(*) as count 
FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_BITSIGHT_CRITICAL_FINDINGS
WHERE FINDING_STATUS = 'OPEN'
"""
critical_count = load_data(critical_count_query)

vendor_risk_query = """
SELECT COUNT(DISTINCT DOMAIN_NAME) as high_risk_vendors
FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_BITSIGHT_VENDOR_RISK
WHERE RISK_RATING = 'HIGH'
"""
vendor_risk = load_data(vendor_risk_query)

with metrics_col1:
    critical_val = critical_count['COUNT'].iloc[0] if not critical_count.empty else 0
    st.metric("Critical Findings", critical_val, "⚠️")

with metrics_col2:
    high_risk_val = vendor_risk['HIGH_RISK_VENDORS'].iloc[0] if not vendor_risk.empty else 0
    st.metric("High Risk Vendors", high_risk_val, "🚨")

with metrics_col3:
    st.metric("Overall Risk Score", "742", "+12")

with metrics_col4:
    st.metric("Compliance Rate", "87%", "+3%")

with metrics_col5:
    st.metric("Last Updated", datetime.now().strftime("%H:%M"), "✅")

st.markdown("---")

# Views
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🚨 Critical Findings",
    "📊 Risk Compliance",
    "📈 Risk Trends",
    "🔍 Risk Vector Analysis",
    "🏢 Vendor Risk",
    "🎯 Security Posture",
    "📋 Remediation Pipeline"
])

# Define color schemes
risk_color_map = {
    'HIGH': '#dc3545',
    'MEDIUM': '#ffc107', 
    'LOW': '#28a745',
    'CRITICAL': '#721c24',
    'ABOVE_TARGET': '#28a745',
    'BELOW_TARGET': '#dc3545'
}

# Tab 1: Critical Findings
with tab1:
    st.markdown("### Critical Security Findings Overview")
    
    # Query critical findings
    critical_findings_query = """
    SELECT * 
    FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_BITSIGHT_CRITICAL_FINDINGS
    ORDER BY LAST_SEEN DESC
    LIMIT 500
    """
    
    df_critical = load_data(critical_findings_query)
    
    if not df_critical.empty:
        # Findings by category and severity
        col1, col2 = st.columns(2)
        
        with col1:
            # Category distribution
            if 'CATEGORY' in df_critical.columns:
                category_counts = df_critical['CATEGORY'].value_counts().reset_index()
                category_counts.columns = ['Category', 'Count']
                
                fig_category = px.pie(
                    category_counts,
                    values='Count',
                    names='Category',
                    title='Findings by Category',
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                fig_category.update_traces(textposition='inside', textinfo='percent+label')
                st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_category, use_container_width=True)
        
        with col2:
            # Severity distribution
            if 'SEVERITY' in df_critical.columns:
                severity_counts = df_critical['SEVERITY'].value_counts().reset_index()
                severity_counts.columns = ['Severity', 'Count']
                
                fig_severity = px
                st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_severity, use_container_width=True)
        
        # Risk Vector Label analysis
        if 'RISK_VECTOR_LABEL' in df_critical.columns:
            st.markdown("### Risk Vector Analysis")
            vector_counts = df_critical['RISK_VECTOR_LABEL'].value_counts().head(10)
            
            fig_vectors = px
            st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_vectors, use_container_width=True)
        
        # Detailed findings table
        st.markdown("### Detailed Findings")
        
        # Select relevant columns
        display_columns = ['DOMAIN_NAME', 'CATEGORY', 'FINDING', 'SEVERITY', 'LAST_SEEN', 'FINDING_STATUS']
        available_columns = [col for col in display_columns if col in df_critical.columns]
        
        if available_columns:
            st.dataframe(
                df_critical[available_columns].head(50),
                use_container_width=True,
                height=400
            )

# Tab 2: Risk Compliance
with tab2:
    st.markdown("### Risk Compliance Status")
    
    compliance_query = """
    SELECT * 
    FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_BITSIGHT_RISK_COMPLIANCE
    ORDER BY LAST_FINDING_DATE DESC
    LIMIT 500
    """
    
    df_compliance = load_data(compliance_query)
    
    if not df_compliance.empty:
        # Risk Rating distribution
        col1, col2 = st.columns(2)
        
        with col1:
            if 'RISK_RATING' in df_compliance.columns:
                rating_counts = df_compliance['RISK_RATING'].value_counts()
                
                fig_rating = px.pie(
                    values=rating_counts.values,
                    names=rating_counts.index,
                    title='Risk Rating Distribution',
                    color_discrete_map=risk_color_map
                )
                fig_rating.update_traces(textposition='inside', textinfo='percent+label')
                st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_rating, use_container_width=True)
        
        with col2:
            if 'TARGET_STATUS' in df_compliance.columns:
                target_counts = df_compliance['TARGET_STATUS'].value_counts()
                
                fig_target = px
                st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_target, use_container_width=True)
        
        # Action Status Overview
        if 'ACTION_STATUS' in df_compliance.columns:
            st.markdown("### Action Status Overview")
            action_counts = df_compliance['ACTION_STATUS'].value_counts()
            
            fig_actions = px
            st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_actions, use_container_width=True)

# Tab 3: Risk Trends
with tab3:
    st.markdown("### Risk Score Trends")
    
    trends_query = """
    SELECT * 
    FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_BITSIGHT_RISK_TREND
    ORDER BY MONTH DESC
    LIMIT 12
    """
    
    df_trends = load_data(trends_query)
    
    if not df_trends.empty:
        # Monthly trends chart
        if 'MONTH' in df_trends.columns and 'CRITICAL_FINDINGS' in df_trends.columns:
            # Create multi-metric trend chart
            fig_trends = go.Figure()
            
            # Critical findings line
            fig_trends.add_trace(go.Scatter(
                x=df_trends['MONTH'],
                y=df_trends['CRITICAL_FINDINGS'],
                mode='lines+markers',
                name='Critical Findings',
                line=dict(color='#dc3545', width=3),
                marker=dict(size=8)
            ))
            
            # Vendors affected
            if 'VENDORS_AFFECTED' in df_trends.columns:
                fig_trends.add_trace(go.Scatter(
                    x=df_trends['MONTH'],
                    y=df_trends['VENDORS_AFFECTED'],
                    mode='lines+markers',
                    name='Vendors Affected',
                    line=dict(color='#ffc107', width=3),
                    marker=dict(size=8),
                    yaxis='y2'
                ))
            
            fig_trends.update_layout(
                title='Security Metrics Trend Analysis',
                xaxis_title='Month',
                yaxis_title='Critical Findings',
                yaxis2=dict(
                    title='Vendors Affected',
                    overlaying='y',
                    side='right'
                ),
                hovermode='x unified',
                height=500
            )
            
            st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_trends, use_container_width=True)
        
        # Category breakdown over time
        if 'CATEGORY' in df_trends.columns:
            st.markdown("### Findings by Category Over Time")
            
            category_pivot = df_trends.pivot_table(
                values='CRITICAL_FINDINGS',
                index='MONTH',
                columns='CATEGORY',
                aggfunc='sum',
                fill_value=0
            )
            
            fig_category_trend = px.area(
                category_pivot,
                title='Critical Findings by Category',
                labels={'value': 'Number of Findings', 'index': 'Month'},
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_category_trend, use_container_width=True)

# Tab 4: Risk Vector Analysis
with tab4:
    st.markdown("### Risk Vector Analysis")
    
    vector_query = """
    SELECT * 
    FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_BITSIGHT_RISK_VECTOR_ANALYSIS
    ORDER BY TOTAL_FINDINGS DESC
    LIMIT 100
    """
    
    df_vector = load_data(vector_query)
    
    if not df_vector.empty:
        # Create treemap for risk vectors
        if all(col in df_vector.columns for col in ['CATEGORY', 'RISK_VECTOR_LABEL', 'TOTAL_FINDINGS']):
            fig_treemap = px.treemap(
                df_vector,
                path=['CATEGORY', 'RISK_VECTOR_LABEL'],
                values='TOTAL_FINDINGS',
                title='Risk Vector Hierarchy',
                color='AVG_SEVERITY_SCORE' if 'AVG_SEVERITY_SCORE' in df_vector.columns else 'TOTAL_FINDINGS',
                color_continuous_scale='RdYlBu_r',
                hover_data=['AFFECTED_VENDORS'] if 'AFFECTED_VENDORS' in df_vector.columns else None
            )
            fig_treemap.update_layout(height=600)
            st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_treemap, use_container_width=True)
        
        # Severity score heatmap
        if 'AVG_SEVERITY_SCORE' in df_vector.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                # Top risk vectors by severity
                top_severe = df_vector.nlargest(10, 'AVG_SEVERITY_SCORE')[['RISK_VECTOR_LABEL', 'AVG_SEVERITY_SCORE']]
                
                fig_severity = px
                st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_severity, use_container_width=True)
            
            with col2:
                # Affected vendors distribution
                if 'AFFECTED_VENDORS' in df_vector.columns:
                    top_affected = df_vector.nlargest(10, 'AFFECTED_VENDORS')[['RISK_VECTOR_LABEL', 'AFFECTED_VENDORS']]
                    
                    fig_vendors = px
                    st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_vendors, use_container_width=True)

# Tab 5: Vendor Risk
with tab5:
    st.markdown("### Vendor Risk Assessment")
    
    vendor_query = """
    SELECT * 
    FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_BITSIGHT_VENDOR_RISK
    ORDER BY CRITICAL_FINDINGS DESC, HIGH_FINDINGS DESC
    LIMIT 500
    """
    
    df_vendor = load_data(vendor_query)
    
    if not df_vendor.empty:
        # Risk summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_vendors = len(df_vendor['DOMAIN_NAME'].unique()) if 'DOMAIN_NAME' in df_vendor.columns else 0
            st.metric("Total Vendors", total_vendors)
        
        with col2:
            critical_vendors = len(df_vendor[df_vendor['CRITICAL_FINDINGS'] > 0]) if 'CRITICAL_FINDINGS' in df_vendor.columns else 0
            st.metric("Vendors with Critical Issues", critical_vendors)
        
        with col3:
            high_risk_vendors = len(df_vendor[df_vendor['RISK_RATING'] == 'HIGH']) if 'RISK_RATING' in df_vendor.columns else 0
            st.metric("High Risk Vendors", high_risk_vendors)
        
        with col4:
            above_target = len(df_vendor[df_vendor['TARGET_STATUS'] == 'ABOVE_TARGET']) if 'TARGET_STATUS' in df_vendor.columns else 0
            st.metric("Above Target", above_target)
        
        # Vendor risk matrix
        if all(col in df_vendor.columns for col in ['CRITICAL_FINDINGS', 'HIGH_FINDINGS', 'MEDIUM_FINDINGS', 'DOMAIN_NAME']):
            # Calculate total findings
            df_vendor['TOTAL_FINDINGS'] = df_vendor['CRITICAL_FINDINGS'] + df_vendor['HIGH_FINDINGS'] + df_vendor['MEDIUM_FINDINGS']
            
            # Top risky vendors
            top_vendors = df_vendor.nlargest(15, 'TOTAL_FINDINGS')
            
            # Create stacked bar chart
            fig_vendor_stack = go.Figure()
            
            fig_vendor_stack.add_trace(go.Bar(
                name='Critical',
                y=top_vendors['DOMAIN_NAME'],
                x=top_vendors['CRITICAL_FINDINGS'],
                orientation='h',
                marker_color='#dc3545'
            ))
            
            fig_vendor_stack.add_trace(go.Bar(
                name='High',
                y=top_vendors['DOMAIN_NAME'],
                x=top_vendors['HIGH_FINDINGS'],
                orientation='h',
                marker_color='#ffc107'
            ))
            
            fig_vendor_stack.add_trace(go.Bar(
                name='Medium',
                y=top_vendors['DOMAIN_NAME'],
                x=top_vendors['MEDIUM_FINDINGS'],
                orientation='h',
                marker_color='#28a745'
            ))
            
            fig_vendor_stack.update_layout(
                barmode='stack',
                title='Top 15 Vendors by Finding Severity',
                xaxis_title='Number of Findings',
                yaxis_title='Vendor',
                height=600,
                showlegend=True
            )
            
            st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_vendor_stack, use_container_width=True)
        
        # Risk rating distribution
        if 'RISK_RATING' in df_vendor.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                rating_dist = df_vendor['RISK_RATING'].value_counts()
                
                fig_rating = px.pie(
                    values=rating_dist.values,
                    names=rating_dist.index,
                    title='Vendor Risk Rating Distribution',
                    color_discrete_map=risk_color_map
                )
                st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_rating, use_container_width=True)
            
            with col2:
                if 'TARGET_STATUS' in df_vendor.columns:
                    target_dist = df_vendor['TARGET_STATUS'].value_counts()
                    
                    fig_target = px
                    st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig_target, use_container_width=True)

# ---------------------------------------------------------------------------
# TAB 6: SECURITY POSTURE
# ---------------------------------------------------------------------------

with tab6:
    st.subheader("Security Posture Assessment")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        score_sql = f"""
            SELECT AVG(SECURITY_RATING) as AVG_SCORE
            FROM {get_table_name('DIM_BITSIGHT_SCORES', 'transformation')}
            WHERE RATING_DATE >= DATEADD(day, -{days_filter}, CURRENT_DATE())
        """
        score_data = safe_query(score_sql, "Failed to load security score")
        if not score_data.empty and score_data['AVG_SCORE'].iloc[0]:
            avg_score = score_data['AVG_SCORE'].iloc[0]
            st.metric("Avg Security Rating", f"{avg_score:.0f}/900",
                     delta=f"{avg_score - 700:+.0f}", help="BitSight security rating")

    with col2:
        botnet_sql = f"""
            SELECT COUNT(*) as BOTNET_COUNT
            FROM {get_table_name('FACT_BITSIGHT_FINDINGS', 'transformation')}
            WHERE FINDING_DATE >= DATEADD(day, -{days_filter}, CURRENT_DATE())
              AND RISK_CATEGORY = 'Botnet Infections'
              AND STATUS != 'REMEDIATED'
        """
        botnet_data = safe_query(botnet_sql, "Failed to load botnet")
        if not botnet_data.empty:
            st.metric("Active Botnets", f"{botnet_data['BOTNET_COUNT'].iloc[0]:,}",
                     delta=f"🔴 {botnet_data['BOTNET_COUNT'].iloc[0]}", delta_color="inverse")

    with col3:
        ssl_sql = f"""
            SELECT COUNT(*) as SSL_ISSUES
            FROM {get_table_name('FACT_BITSIGHT_FINDINGS', 'transformation')}
            WHERE FINDING_DATE >= DATEADD(day, -{days_filter}, CURRENT_DATE())
              AND RISK_CATEGORY LIKE '%SSL%'
              AND STATUS != 'REMEDIATED'
        """
        ssl_data = safe_query(ssl_sql, "Failed to load SSL issues")
        if not ssl_data.empty:
            st.metric("SSL/TLS Issues", f"{ssl_data['SSL_ISSUES'].iloc[0]:,}")

    with col4:
        patching_sql = f"""
            SELECT ROUND(AVG(PATCHING_CADENCE_DAYS), 1) as AVG_PATCH_DAYS
            FROM {get_table_name('DIM_BITSIGHT_SCORES', 'transformation')}
            WHERE RATING_DATE >= DATEADD(day, -{days_filter}, CURRENT_DATE())
        """
        patch_data = safe_query(patching_sql, "Failed to load patching")
        if not patch_data.empty and patch_data['AVG_PATCH_DAYS'].iloc[0]:
            st.metric("Avg Patch Time", f"{patch_data['AVG_PATCH_DAYS'].iloc[0]:.1f} days")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Rating by Risk Category")
        category_rating_sql = f"""
            SELECT RISK_CATEGORY, AVG(RATING_SCORE) as AVG_RATING
            FROM {get_table_name('DIM_BITSIGHT_SCORES', 'transformation')} s
            JOIN {get_table_name('FACT_BITSIGHT_FINDINGS', 'transformation')} f
                ON DATE_TRUNC('month', s.RATING_DATE) = DATE_TRUNC('month', f.FINDING_DATE)
            WHERE s.RATING_DATE >= DATEADD(day, -{days_filter}, CURRENT_DATE())
            GROUP BY RISK_CATEGORY
            ORDER BY AVG_RATING
        """
        category_rating = safe_query(category_rating_sql, "Failed to load category ratings")
        if not category_rating.empty:
            fig = px
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Industry Benchmark Comparison")
        benchmark_sql = f"""
            SELECT
                'Our Score' as CATEGORY, AVG(SECURITY_RATING) as SCORE
            FROM {get_table_name('DIM_BITSIGHT_SCORES', 'transformation')}
            WHERE RATING_DATE >= DATEADD(day, -30, CURRENT_DATE())
            UNION ALL
            SELECT 'Industry Avg' as CATEGORY, 720 as SCORE
            UNION ALL
            SELECT 'Top Quartile' as CATEGORY, 800 as SCORE
        """
        benchmark_data = safe_query(benchmark_sql, "Failed to load benchmarks")
        if not benchmark_data.empty:
            fig = px
            fig.add_hline(y=700, line_dash="dash", line_color="orange", annotation_text="Target: 700")
            st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Security Control Effectiveness")

    control_effectiveness_sql = f"""
        SELECT
            CASE
                WHEN RISK_CATEGORY LIKE '%Botnet%' THEN 'Network Security'
                WHEN RISK_CATEGORY LIKE '%SSL%' OR RISK_CATEGORY LIKE '%Certificate%' THEN 'Encryption'
                WHEN RISK_CATEGORY LIKE '%Vulnerability%' THEN 'Patch Management'
                WHEN RISK_CATEGORY LIKE '%DMARC%' OR RISK_CATEGORY LIKE '%SPF%' THEN 'Email Security'
                ELSE 'Other Controls'
            END as CONTROL_AREA,
            COUNT(*) as TOTAL_FINDINGS,
            SUM(CASE WHEN STATUS = 'REMEDIATED' THEN 1 ELSE 0 END) as REMEDIATED,
            ROUND(SUM(CASE WHEN STATUS = 'REMEDIATED' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as REMEDIATION_RATE
        FROM {get_table_name('FACT_BITSIGHT_FINDINGS', 'transformation')}
        WHERE FINDING_DATE >= DATEADD(day, -{days_filter}, CURRENT_DATE())
        GROUP BY CONTROL_AREA
        ORDER BY TOTAL_FINDINGS DESC
    """
    control_effectiveness = safe_query(control_effectiveness_sql, "Failed to load control effectiveness")
    if not control_effectiveness.empty:
        st.dataframe(control_effectiveness.style,
                    use_container_width=True)
        export_csv(control_effectiveness, "bitsight_control_effectiveness")

# ---------------------------------------------------------------------------
# TAB 7: REMEDIATION PIPELINE
# ---------------------------------------------------------------------------

with tab7:
    st.subheader("Remediation Pipeline & Progress")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        open_findings_sql = f"""
            SELECT COUNT(*) as OPEN_FINDINGS
            FROM {get_table_name('FACT_BITSIGHT_FINDINGS', 'transformation')}
            WHERE STATUS IN ('OPEN', 'IN_PROGRESS')
        """
        open_data = safe_query(open_findings_sql, "Failed to load open findings")
        if not open_data.empty:
            st.metric("Open Findings", f"{open_data['OPEN_FINDINGS'].iloc[0]:,}",
                     delta=f"🔴 {open_data['OPEN_FINDINGS'].iloc[0]}", delta_color="inverse")

    with col2:
        in_progress_sql = f"""
            SELECT COUNT(*) as IN_PROGRESS
            FROM {get_table_name('FACT_BITSIGHT_FINDINGS', 'transformation')}
            WHERE STATUS = 'IN_PROGRESS'
        """
        progress_data = safe_query(in_progress_sql, "Failed to load in-progress")
        if not progress_data.empty:
            st.metric("In Progress", f"{progress_data['IN_PROGRESS'].iloc[0]:,}")

    with col3:
        remediation_rate_sql = f"""
            SELECT ROUND(SUM(CASE WHEN STATUS = 'REMEDIATED' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as REMEDIATION_RATE
            FROM {get_table_name('FACT_BITSIGHT_FINDINGS', 'transformation')}
            WHERE FINDING_DATE >= DATEADD(day, -{days_filter}, CURRENT_DATE())
        """
        rate_data = safe_query(remediation_rate_sql, "Failed to load remediation rate")
        if not rate_data.empty and rate_data['REMEDIATION_RATE'].iloc[0]:
            rate = rate_data['REMEDIATION_RATE'].iloc[0]
            st.metric("Remediation Rate", f"{rate:.1f}%", delta=f"{rate - 80:+.1f}%")

    with col4:
        avg_remediation_sql = f"""
            SELECT ROUND(AVG(DATEDIFF(day, FINDING_DATE, REMEDIATION_DATE)), 1) as AVG_DAYS
            FROM {get_table_name('FACT_BITSIGHT_FINDINGS', 'transformation')}
            WHERE REMEDIATION_DATE IS NOT NULL
              AND FINDING_DATE >= DATEADD(day, -{days_filter}, CURRENT_DATE())
        """
        avg_rem_data = safe_query(avg_remediation_sql, "Failed to load avg remediation time")
        if not avg_rem_data.empty and avg_rem_data['AVG_DAYS'].iloc[0]:
            st.metric("Avg Remediation Time", f"{avg_rem_data['AVG_DAYS'].iloc[0]:.1f} days")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Remediation Progress by Severity")
        remediation_progress_sql = f"""
            SELECT SEVERITY,
                   COUNT(*) as TOTAL,
                   SUM(CASE WHEN STATUS = 'REMEDIATED' THEN 1 ELSE 0 END) as REMEDIATED,
                   SUM(CASE WHEN STATUS = 'IN_PROGRESS' THEN 1 ELSE 0 END) as IN_PROGRESS,
                   SUM(CASE WHEN STATUS = 'OPEN' THEN 1 ELSE 0 END) as OPEN
            FROM {get_table_name('FACT_BITSIGHT_FINDINGS', 'transformation')}
            WHERE FINDING_DATE >= DATEADD(day, -{days_filter}, CURRENT_DATE())
            GROUP BY SEVERITY
            ORDER BY
                CASE SEVERITY
                    WHEN 'HIGH' THEN 1
                    WHEN 'MEDIUM' THEN 2
                    ELSE 3
                END
        """
        remediation_progress = safe_query(remediation_progress_sql, "Failed to load remediation progress")
        if not remediation_progress.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Open', x=remediation_progress['SEVERITY'], y=remediation_progress['OPEN'], marker_color='#dc3545'))
            fig.add_trace(go.Bar(name='In Progress', x=remediation_progress['SEVERITY'], y=remediation_progress['IN_PROGRESS'], marker_color='#ffc107'))
            fig.add_trace(go.Bar(name='Remediated', x=remediation_progress['SEVERITY'], y=remediation_progress['REMEDIATED'], marker_color='#28a745'))
            fig.update_layout(barmode='stack', title="Remediation Pipeline by Severity")
            st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Remediation Velocity (Last 30 Days)")
        velocity_sql = f"""
            SELECT DATE_TRUNC('week', REMEDIATION_DATE) as WEEK,
                   COUNT(*) as REMEDIATED_COUNT
            FROM {get_table_name('FACT_BITSIGHT_FINDINGS', 'transformation')}
            WHERE REMEDIATION_DATE >= DATEADD(day, -30, CURRENT_DATE())
            GROUP BY WEEK
            ORDER BY WEEK
        """
        velocity_data = safe_query(velocity_sql, "Failed to load remediation velocity")
        if not velocity_data.empty:
            fig = px.line(velocity_data, x='WEEK', y='REMEDIATED_COUNT', markers=True,
                         title="Weekly Remediation Velocity")
            st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("#### High Priority Findings Awaiting Remediation")

    high_priority_sql = f"""
        SELECT FINDING_ID, RISK_CATEGORY, SEVERITY, FINDING_DATE,
               DATEDIFF(day, FINDING_DATE, CURRENT_DATE()) as AGE_DAYS,
               STATUS, ASSIGNED_TO
        FROM {get_table_name('FACT_BITSIGHT_FINDINGS', 'transformation')}
        WHERE SEVERITY = 'HIGH'
          AND STATUS IN ('OPEN', 'IN_PROGRESS')
        ORDER BY AGE_DAYS DESC
        LIMIT 30
    """
    high_priority = safe_query(high_priority_sql, "Failed to load high priority findings")
    if not high_priority.empty:
        st.dataframe(high_priority.style,
                    use_container_width=True)
        export_csv(high_priority, "bitsight_high_priority_findings")
        st.warning(f"⚠️ {len(high_priority)} high-severity findings require attention")
    else:
        st.success("✅ No high-priority findings pending")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>BitSight Security Dashboard | Group Information Security | Data refreshed every 10 minutes</p>
    <p style="font-size: 0.8rem;">© 2025 GenericCorp Corporation. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)


#COMMENTS
#Security Testing Dashboard for BitSight
#Visual Risk Tracking – Shows security issues, vendor risks, and compliance status.
#Alerts & Trends – Highlights critical problems and trends over time (red = bad, green = good).
#Auto-Updates – Pulls live data every 10 mins.
#For quick, at-a-glance security monitoring.