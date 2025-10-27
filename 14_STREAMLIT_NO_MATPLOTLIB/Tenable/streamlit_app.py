"""
Tenable Vulnerability Management Dashboard

Vulnerability scanning and management dashboard for Tenable.io/Nessus,
tracking asset vulnerabilities, scan coverage, and remediation status.
"""

# Import python packages
import streamlit as st
import pandas as pd
# import plotly.express as px  # Not available in Snowflake
# import plotly.graph_objects as go  # Not available in Snowflake
from snowflake.snowpark.context import get_active_session
from datetime import datetime, timedelta

# Import common components
import sys
sys.path.append('..')
from common.styles import apply_common_styles, create_header, create_sidebar_branding
from common.utils import (
    safe_query,
    query_with_metrics,
    export_csv,
    show_data_freshness,
    add_refresh_button,
    show_last_refresh,
    show_alert_threshold
)
from common.validators import validate_environment
from common.config import get_view_name, get_table_name, SEVERITY_LEVELS, DATE_RANGES

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Tenable Vulnerability Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply common styles
apply_common_styles()

# ============================================================================
# ENVIRONMENT VALIDATION
# ============================================================================

# Define required objects for this app
REQUIRED_OBJECTS = [
    get_table_name('FACT_TENABLE', 'transformation'),
    get_table_name('DIM_TENABLE_VULN', 'transformation'),
    get_table_name('L_TENABLE_ASSETS', 'landing')
]

# Validate that all required objects exist
validate_environment(REQUIRED_OBJECTS)

# Get Snowflake session
session = get_active_session()

# ============================================================================
# HEADER
# ============================================================================

create_header(
    title="Tenable Vulnerability Management",
    subtitle="Vulnerability Scanning & Asset Risk Assessment",
    icon="🔍"
)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    # Branding
    create_sidebar_branding()

    st.markdown("---")

    # Filters
    st.header("📊 Dashboard Filters")

    # Date range filter
    date_range = st.selectbox(
        "Time Period",
        list(DATE_RANGES.keys()),
        index=2,  # Default to "Last 30 Days"
        help="Select time range for vulnerability data"
    )
    days = DATE_RANGES[date_range]

    # Severity filter
    severity_filter = st.multiselect(
        "Vulnerability Severity",
        ['Critical', 'High', 'Medium', 'Low', 'Info'],
        default=['Critical', 'High'],
        help="Filter by vulnerability severity (CVSS-based)"
    )

    # Status filter
    status_filter = st.multiselect(
        "Remediation Status",
        ['Open', 'In Progress', 'Remediated', 'Accepted Risk'],
        default=['Open', 'In Progress'],
        help="Filter by vulnerability remediation status"
    )

    # CVSS score filter
    cvss_min = st.slider(
        "Minimum CVSS Score",
        min_value=0.0,
        max_value=10.0,
        value=7.0,
        step=0.1,
        help="Filter vulnerabilities by minimum CVSS score"
    )

    st.markdown("---")

    # Refresh button
    add_refresh_button()

    # Info section
    st.info("""
    **📊 Data Source:**
    Tenable.io / Nessus Pro

    **📈 Metrics Tracked:**
    - Active vulnerabilities (CVE)
    - Asset scan coverage
    - CVSS risk scores
    - Remediation SLA compliance
    - Patch priority recommendations
    """)

    # Last refresh timestamp
    show_last_refresh()

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Tab layout
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "🔍 Vulnerability Details",
    "💻 Asset Analysis",
    "📈 Trends & Metrics"
])

# ---------------------------------------------------------------------------
# TAB 1: OVERVIEW
# ---------------------------------------------------------------------------

with tab1:
    st.subheader("Vulnerability Management Overview")

    # Data freshness indicator
    show_data_freshness(
        get_table_name('FACT_TENABLE', 'transformation'),
        timestamp_column='SCAN_DATE'
    )

    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Total vulnerabilities
        vuln_sql = f"""
            SELECT COUNT(DISTINCT VULN_ID) as TOTAL_VULNS
            FROM {get_table_name('FACT_TENABLE', 'transformation')}
            WHERE SCAN_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
              AND STATUS IN ('Open', 'In Progress')
        """
        vuln_data = safe_query(vuln_sql, "Failed to load vulnerabilities")

        if not vuln_data.empty:
            st.metric(
                "Active Vulnerabilities",
                f"{vuln_data['TOTAL_VULNS'].iloc[0]:,}",
                help="Total open and in-progress vulnerabilities"
            )

    with col2:
        # Critical/High count
        critical_sql = f"""
            SELECT COUNT(*) as CRITICAL_HIGH
            FROM {get_table_name('FACT_TENABLE', 'transformation')}
            WHERE SCAN_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
              AND SEVERITY IN ('Critical', 'High')
              AND STATUS IN ('Open', 'In Progress')
        """
        critical_data = safe_query(critical_sql, "Failed to load critical vulns")

        if not critical_data.empty:
            critical_count = critical_data['CRITICAL_HIGH'].iloc[0]
            st.metric(
                "Critical/High",
                f"{critical_count:,}",
                delta=f"🔴 {critical_count}",
                delta_color="inverse",
                help="Critical and High severity vulnerabilities requiring immediate action"
            )

    with col3:
        # Average CVSS score
        cvss_sql = f"""
            SELECT ROUND(AVG(CVSS_SCORE), 1) as AVG_CVSS
            FROM {get_table_name('FACT_TENABLE', 'transformation')}
            WHERE SCAN_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
              AND STATUS IN ('Open', 'In Progress')
              AND CVSS_SCORE > 0
        """
        cvss_data = safe_query(cvss_sql, "Failed to load CVSS data")

        if not cvss_data.empty and cvss_data['AVG_CVSS'].iloc[0] is not None:
            avg_cvss = cvss_data['AVG_CVSS'].iloc[0]
            st.metric(
                "Avg CVSS Score",
                f"{avg_cvss}",
                delta=f"{avg_cvss - 5.0:+.1f}",
                delta_color="inverse",
                help="Average CVSS score of active vulnerabilities (0-10 scale)"
            )

    with col4:
        # Assets scanned
        assets_sql = f"""
            SELECT COUNT(DISTINCT ASSET_ID) as SCANNED_ASSETS
            FROM {get_table_name('FACT_TENABLE', 'transformation')}
            WHERE SCAN_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
        """
        assets_data = safe_query(assets_sql, "Failed to load assets")

        if not assets_data.empty:
            st.metric(
                "Assets Scanned",
                f"{assets_data['SCANNED_ASSETS'].iloc[0]:,}",
                help="Total number of assets scanned in selected period"
            )

    st.markdown("---")

    # Visualization row
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Vulnerability Severity Distribution")

        severity_sql = f"""
            SELECT
                SEVERITY,
                COUNT(*) as VULN_COUNT
            FROM {get_table_name('FACT_TENABLE', 'transformation')}
            WHERE SCAN_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
              AND STATUS IN ('Open', 'In Progress')
              AND SEVERITY IS NOT NULL
            GROUP BY SEVERITY
            ORDER BY
                CASE SEVERITY
                    WHEN 'Critical' THEN 1
                    WHEN 'High' THEN 2
                    WHEN 'Medium' THEN 3
                    WHEN 'Low' THEN 4
                    WHEN 'Info' THEN 5
                    ELSE 6
                END
        """

        severity_data = safe_query(severity_sql, "Failed to load severity distribution")

        if not severity_data.empty:
            colors = {
                'Critical': '#e74c3c',
                'High': '#e67e22',
                'Medium': '#f39c12',
                'Low': '#3498db',
                'Info': '#95a5a6'
            }
            fig = px
            st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top 10 CVEs by Asset Count")

        cve_sql = f"""
            SELECT
                CVE_ID,
                COUNT(DISTINCT ASSET_ID) as AFFECTED_ASSETS,
                MAX(CVSS_SCORE) as MAX_CVSS
            FROM {get_table_name('FACT_TENABLE', 'transformation')}
            WHERE SCAN_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
              AND STATUS IN ('Open', 'In Progress')
              AND CVE_ID IS NOT NULL
            GROUP BY CVE_ID
            ORDER BY AFFECTED_ASSETS DESC
            LIMIT 10
        """

        cve_data = safe_query(cve_sql, "Failed to load CVE data")

        if not cve_data.empty:
            fig = px
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Remediation SLA status
    st.subheader("Remediation SLA Status")

    sla_sql = f"""
        SELECT
            CASE
                WHEN DAYS_OPEN <= 30 THEN 'Within SLA (≤30 days)'
                WHEN DAYS_OPEN <= 60 THEN 'Near SLA Breach (31-60 days)'
                WHEN DAYS_OPEN <= 90 THEN 'SLA Breach (61-90 days)'
                ELSE 'Critical Overdue (>90 days)'
            END as SLA_STATUS,
            COUNT(*) as VULN_COUNT
        FROM (
            SELECT DATEDIFF(day, FIRST_DETECTED, CURRENT_DATE()) as DAYS_OPEN
            FROM {get_table_name('FACT_TENABLE', 'transformation')}
            WHERE STATUS IN ('Open', 'In Progress')
              AND SEVERITY IN ('Critical', 'High')
        )
        GROUP BY SLA_STATUS
        ORDER BY
            CASE
                WHEN SLA_STATUS = 'Within SLA (≤30 days)' THEN 1
                WHEN SLA_STATUS = 'Near SLA Breach (31-60 days)' THEN 2
                WHEN SLA_STATUS = 'SLA Breach (61-90 days)' THEN 3
                ELSE 4
            END
    """

    sla_data = safe_query(sla_sql, "Failed to load SLA data")

    if not sla_data.empty:
        colors = {
            'Within SLA (≤30 days)': '#27ae60',
            'Near SLA Breach (31-60 days)': '#f39c12',
            'SLA Breach (61-90 days)': '#e67e22',
            'Critical Overdue (>90 days)': '#e74c3c'
        }
        fig = px
        st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# TAB 2: VULNERABILITY DETAILS
# ---------------------------------------------------------------------------

with tab2:
    st.subheader("Detailed Vulnerability Records")

    # Build filters for SQL
    severity_filter_sql = "','".join(severity_filter) if severity_filter else "'Critical','High','Medium','Low','Info'"
    status_filter_sql = "','".join(status_filter) if status_filter else "'Open','In Progress'"

    # Query vulnerability details
    vuln_detail_sql = f"""
        SELECT
            t.CVE_ID,
            d.VULN_NAME,
            t.SEVERITY,
            t.CVSS_SCORE,
            t.ASSET_HOSTNAME,
            t.ASSET_IP,
            t.STATUS,
            t.FIRST_DETECTED,
            DATEDIFF(day, t.FIRST_DETECTED, CURRENT_DATE()) as DAYS_OPEN,
            d.DESCRIPTION,
            d.SOLUTION
        FROM {get_table_name('FACT_TENABLE', 'transformation')} t
        LEFT JOIN {get_table_name('DIM_TENABLE_VULN', 'transformation')} d
            ON t.VULN_ID = d.VULN_ID
        WHERE t.SCAN_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
          AND t.SEVERITY IN ('{severity_filter_sql}')
          AND t.STATUS IN ('{status_filter_sql}')
          AND t.CVSS_SCORE >= {cvss_min}
        ORDER BY t.CVSS_SCORE DESC, t.FIRST_DETECTED ASC
        LIMIT 1000
    """

    vuln_detail = query_with_metrics(vuln_detail_sql, "Failed to load vulnerability details")

    if not vuln_detail.empty:
        # Search functionality
        search_term = st.text_input("🔍 Search vulnerabilities (CVE, hostname, description)", "")

        if search_term:
            vuln_detail = vuln_detail[
                vuln_detail.astype(str).apply(
                    lambda x: x.str.contains(search_term, case=False, na=False)
                ).any(axis=1)
            ]

        # Display dataframe
        st.dataframe(
            vuln_detail,
            use_container_width=True,
            height=500,
            column_config={
                "CVSS_SCORE": st.column_config.ProgressColumn(
                    "CVSS Score",
                    min_value=0,
                    max_value=10,
                    format="%.1f"
                ),
                "DAYS_OPEN": st.column_config.NumberColumn(
                    "Days Open",
                    format="%d days"
                )
            }
        )

        # Export button
        export_csv(vuln_detail, "tenable_vulnerabilities")

        # Summary stats
        st.caption(f"Showing {len(vuln_detail):,} vulnerability records")
    else:
        st.info("✅ No vulnerabilities found matching selected filters")

# ---------------------------------------------------------------------------
# TAB 3: ASSET ANALYSIS
# ---------------------------------------------------------------------------

with tab3:
    st.subheader("Asset Vulnerability Analysis")

    # Top vulnerable assets
    st.subheader("Top 20 Most Vulnerable Assets")

    top_assets_sql = f"""
        SELECT
            ASSET_HOSTNAME,
            ASSET_IP,
            COUNT(*) as TOTAL_VULNS,
            SUM(CASE WHEN SEVERITY = 'Critical' THEN 1 ELSE 0 END) as CRITICAL_COUNT,
            SUM(CASE WHEN SEVERITY = 'High' THEN 1 ELSE 0 END) as HIGH_COUNT,
            ROUND(AVG(CVSS_SCORE), 1) as AVG_CVSS,
            MAX(SCAN_DATE) as LAST_SCAN
        FROM {get_table_name('FACT_TENABLE', 'transformation')}
        WHERE SCAN_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
          AND STATUS IN ('Open', 'In Progress')
        GROUP BY ASSET_HOSTNAME, ASSET_IP
        ORDER BY CRITICAL_COUNT DESC, HIGH_COUNT DESC, TOTAL_VULNS DESC
        LIMIT 20
    """

    top_assets = safe_query(top_assets_sql, "Failed to load asset data")

    if not top_assets.empty:
        st.dataframe(
            top_assets,
            use_container_width=True,
            height=400,
            column_config={
                "CRITICAL_COUNT": st.column_config.NumberColumn(
                    "Critical",
                    format="🔴 %d"
                ),
                "HIGH_COUNT": st.column_config.NumberColumn(
                    "High",
                    format="🟠 %d"
                )
            }
        )

        export_csv(top_assets, "tenable_vulnerable_assets")

    st.markdown("---")

    # Asset risk distribution
    st.subheader("Asset Risk Distribution")

    risk_dist_sql = f"""
        SELECT
            CASE
                WHEN MAX(CVSS_SCORE) >= 9.0 THEN 'Critical Risk (CVSS ≥9.0)'
                WHEN MAX(CVSS_SCORE) >= 7.0 THEN 'High Risk (CVSS 7.0-8.9)'
                WHEN MAX(CVSS_SCORE) >= 4.0 THEN 'Medium Risk (CVSS 4.0-6.9)'
                WHEN MAX(CVSS_SCORE) > 0 THEN 'Low Risk (CVSS <4.0)'
                ELSE 'No Vulnerabilities'
            END as RISK_LEVEL,
            COUNT(DISTINCT ASSET_ID) as ASSET_COUNT
        FROM {get_table_name('FACT_TENABLE', 'transformation')}
        WHERE SCAN_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
        GROUP BY ASSET_ID
        GROUP BY RISK_LEVEL
    """

    risk_dist = safe_query(risk_dist_sql, "Failed to load risk distribution")

    if not risk_dist.empty:
        colors = {
            'Critical Risk (CVSS ≥9.0)': '#e74c3c',
            'High Risk (CVSS 7.0-8.9)': '#e67e22',
            'Medium Risk (CVSS 4.0-6.9)': '#f39c12',
            'Low Risk (CVSS <4.0)': '#3498db',
            'No Vulnerabilities': '#27ae60'
        }
        fig = px.pie(
            risk_dist,
            values='ASSET_COUNT',
            names='RISK_LEVEL',
            title="Assets by Risk Level",
            color='RISK_LEVEL',
            color_discrete_map=colors
        )
        st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# TAB 4: TRENDS & METRICS
# ---------------------------------------------------------------------------

with tab4:
    st.subheader("Vulnerability Trends Over Time")

    # Daily vulnerability trend
    trend_sql = f"""
        SELECT
            DATE_TRUNC('day', SCAN_DATE) as DAY,
            SEVERITY,
            COUNT(*) as VULN_COUNT
        FROM {get_table_name('FACT_TENABLE', 'transformation')}
        WHERE SCAN_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
          AND STATUS IN ('Open', 'In Progress')
          AND SEVERITY IN ('Critical', 'High', 'Medium')
        GROUP BY DAY, SEVERITY
        ORDER BY DAY, SEVERITY
    """

    trend_data = safe_query(trend_sql, "Failed to load trend data")

    if not trend_data.empty:
        fig = px.line(
            trend_data,
            x='DAY',
            y='VULN_COUNT',
            color='SEVERITY',
            title="Open Vulnerabilities Trend",
            labels={'DAY': 'Date', 'VULN_COUNT': 'Count', 'SEVERITY': 'Severity'},
            color_discrete_map={'Critical': '#e74c3c', 'High': '#e67e22', 'Medium': '#f39c12'}
        )
        st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Remediation rate
    st.subheader("Remediation Progress")

    remediation_sql = f"""
        SELECT
            DATE_TRUNC('day', REMEDIATION_DATE) as DAY,
            COUNT(*) as REMEDIATED_COUNT
        FROM {get_table_name('FACT_TENABLE', 'transformation')}
        WHERE REMEDIATION_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
          AND STATUS = 'Remediated'
        GROUP BY DAY
        ORDER BY DAY
    """

    remediation_data = safe_query(remediation_sql, "Failed to load remediation data")

    if not remediation_data.empty:
        fig = px
        st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("""
**Data Source:** Tenable.io / Nessus via Snowflake
**Refresh Rate:** 5-minute cache
**Contact:** GenericCorp Data Engineering Team
""")
