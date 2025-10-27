"""
CybelAngel Threat Intelligence Dashboard

External threat monitoring dashboard for CybelAngel platform,
tracking data leaks, brand infringement, and cyber threats.
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
    show_last_refresh
)
from common.validators import validate_environment
from common.config import get_view_name, get_table_name, DATE_RANGES

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="CybelAngel Threat Intelligence",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply common styles
apply_common_styles()

# ============================================================================
# ENVIRONMENT VALIDATION
# ============================================================================

REQUIRED_OBJECTS = [
    get_table_name('FACT_CYBELANGEL_THREATS', 'transformation'),
    get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')
]

validate_environment(REQUIRED_OBJECTS)
session = get_active_session()

# ============================================================================
# HEADER
# ============================================================================

create_header(
    title="CybelAngel Threat Intelligence",
    subtitle="External Threat Monitoring & Data Leak Detection",
    icon="🌐"
)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    create_sidebar_branding()
    st.markdown("---")
    st.header("📊 Dashboard Filters")

    date_range = st.selectbox(
        "Time Period",
        list(DATE_RANGES.keys()),
        index=2,
        help="Select time range for threat analysis"
    )
    days = DATE_RANGES[date_range]

    severity_filter = st.multiselect(
        "Severity",
        ['Critical', 'High', 'Medium', 'Low'],
        default=['Critical', 'High'],
        help="Filter by threat severity"
    )

    category_query = f"""
        SELECT DISTINCT CATEGORY
        FROM {get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')}
        WHERE CATEGORY IS NOT NULL
        ORDER BY CATEGORY
    """
    category_data = safe_query(category_query, "Failed to load categories")

    if not category_data.empty:
        categories = category_data['CATEGORY'].tolist()
        category_filter = st.multiselect(
            "Threat Category",
            categories,
            default=categories[:3] if len(categories) >= 3 else categories,
            help="Filter by threat category"
        )
    else:
        category_filter = []

    st.markdown("---")
    add_refresh_button()

    st.info("""
    **📊 Data Source:**
    CybelAngel Platform

    **📈 Metrics Tracked:**
    - Data leakage alerts
    - Brand infringement
    - Dark web mentions
    - Exposed credentials
    - Phishing domains
    """)

    show_last_refresh()

# ============================================================================
# MAIN CONTENT
# ============================================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview",
    "🔍 Threat Details",
    "📈 Trends",
    "🌍 Source Analysis",
    "🔒 Data Leak Analysis",
    "⚡ Response Metrics"
])

# ---------------------------------------------------------------------------
# TAB 1: OVERVIEW
# ---------------------------------------------------------------------------

with tab1:
    st.subheader("Threat Intelligence Overview")

    show_data_freshness(
        get_table_name('FACT_CYBELANGEL_THREATS', 'transformation'),
        timestamp_column='DETECTION_DATE'
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_threats_sql = f"""
            SELECT COUNT(*) as TOTAL_THREATS
            FROM {get_table_name('FACT_CYBELANGEL_THREATS', 'transformation')}
            WHERE DETECTION_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
        """
        threats_data = safe_query(total_threats_sql, "Failed to load threats")

        if not threats_data.empty:
            st.metric(
                "Total Threats",
                f"{threats_data['TOTAL_THREATS'].iloc[0]:,}",
                help="Total external threats detected by CybelAngel"
            )

    with col2:
        critical_sql = f"""
            SELECT COUNT(*) as CRITICAL_THREATS
            FROM {get_table_name('FACT_CYBELANGEL_THREATS', 'transformation')} t
            JOIN {get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')} d
                ON t.ALERT_KEY = d.ALERT_KEY
            WHERE t.DETECTION_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
              AND d.SEVERITY = 'Critical'
              AND d.STATUS != 'Closed'
        """
        critical_data = safe_query(critical_sql, "Failed to load critical threats")

        if not critical_data.empty:
            critical_count = critical_data['CRITICAL_THREATS'].iloc[0]
            st.metric(
                "Critical Threats",
                f"{critical_count:,}",
                delta=f"🔴 {critical_count}",
                delta_color="inverse",
                help="Critical severity threats requiring immediate action"
            )

    with col3:
        active_sql = f"""
            SELECT COUNT(*) as ACTIVE_ALERTS
            FROM {get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')}
            WHERE STATUS IN ('Open', 'In Progress', 'New')
        """
        active_data = safe_query(active_sql, "Failed to load active alerts")

        if not active_data.empty:
            st.metric(
                "Active Alerts",
                f"{active_data['ACTIVE_ALERTS'].iloc[0]:,}",
                help="Currently active threat alerts"
            )

    with col4:
        data_leaks_sql = f"""
            SELECT COUNT(*) as DATA_LEAKS
            FROM {get_table_name('FACT_CYBELANGEL_THREATS', 'transformation')} t
            JOIN {get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')} d
                ON t.ALERT_KEY = d.ALERT_KEY
            WHERE t.DETECTION_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
              AND d.CATEGORY LIKE '%Data Leak%'
        """
        leaks_data = safe_query(data_leaks_sql, "Failed to load data leaks")

        if not leaks_data.empty:
            st.metric(
                "Data Leaks",
                f"{leaks_data['DATA_LEAKS'].iloc[0]:,}",
                help="Detected data leakage incidents"
            )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Threat Severity Distribution")

        severity_sql = f"""
            SELECT
                d.SEVERITY,
                COUNT(*) as THREAT_COUNT
            FROM {get_table_name('FACT_CYBELANGEL_THREATS', 'transformation')} t
            JOIN {get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')} d
                ON t.ALERT_KEY = d.ALERT_KEY
            WHERE t.DETECTION_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
              AND d.SEVERITY IS NOT NULL
            GROUP BY d.SEVERITY
        """

        severity_data = safe_query(severity_sql, "Failed to load severity data")

        if not severity_data.empty:
            colors = {'Critical': '#e74c3c', 'High': '#e67e22', 'Medium': '#f39c12', 'Low': '#3498db'}
            fig = px.pie(
                severity_data,
                values='THREAT_COUNT',
                names='SEVERITY',
                color='SEVERITY',
                color_discrete_map=colors
            )
            st.info("Interactive chart not available in Snowflake - view data in table below")

    with col2:
        st.subheader("Top Threat Categories")

        category_sql = f"""
            SELECT
                d.CATEGORY,
                COUNT(*) as COUNT
            FROM {get_table_name('FACT_CYBELANGEL_THREATS', 'transformation')} t
            JOIN {get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')} d
                ON t.ALERT_KEY = d.ALERT_KEY
            WHERE t.DETECTION_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
              AND d.CATEGORY IS NOT NULL
            GROUP BY d.CATEGORY
            ORDER BY COUNT DESC
            LIMIT 10
        """

        category_data = safe_query(category_sql, "Failed to load categories")

        if not category_data.empty:
            fig = px.bar(
                category_data,
                x='COUNT',
                y='CATEGORY',
                orientation='h'
            )
            # fig.update_layout(  # Plotly not availableyaxis={'categoryorder': 'total ascending'})
            st.info("Interactive chart not available in Snowflake - view data in table below")

# ---------------------------------------------------------------------------
# TAB 2: THREAT DETAILS
# ---------------------------------------------------------------------------

with tab2:
    st.subheader("Detailed Threat Records")

    severity_filter_sql = "','".join(severity_filter) if severity_filter else "'Critical','High','Medium','Low'"
    category_filter_sql = "','".join(category_filter) if category_filter else ""

    category_where = f"AND d.CATEGORY IN ('{category_filter_sql}')" if category_filter_sql else ""

    details_sql = f"""
        SELECT
            t.THREAT_ID,
            d.ALERT_TYPE,
            d.CATEGORY,
            d.SEVERITY,
            d.SOURCE as THREAT_SOURCE,
            t.DETECTION_DATE,
            d.STATUS,
            d.DESCRIPTION
        FROM {get_table_name('FACT_CYBELANGEL_THREATS', 'transformation')} t
        JOIN {get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')} d
            ON t.ALERT_KEY = d.ALERT_KEY
        WHERE t.DETECTION_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
          AND d.SEVERITY IN ('{severity_filter_sql}')
          {category_where}
        ORDER BY t.DETECTION_DATE DESC
        LIMIT 1000
    """

    details_data = query_with_metrics(details_sql, "Failed to load threat details")

    if not details_data.empty:
        search_term = st.text_input("🔍 Search threats", "")

        if search_term:
            details_data = details_data[
                details_data.astype(str).apply(
                    lambda x: x.str.contains(search_term, case=False, na=False)
                ).any(axis=1)
            ]

        st.dataframe(details_data, use_container_width=True, height=500)
        export_csv(details_data, "cybelangel_threats")
        st.caption(f"Showing {len(details_data):,} threats")
    else:
        st.info("✅ No threats found matching selected filters")

# ---------------------------------------------------------------------------
# TAB 3: TRENDS
# ---------------------------------------------------------------------------

with tab3:
    st.subheader("Threat Detection Trends")

    trend_sql = f"""
        SELECT
            DATE_TRUNC('day', t.DETECTION_DATE) as DAY,
            d.SEVERITY,
            COUNT(*) as THREAT_COUNT
        FROM {get_table_name('FACT_CYBELANGEL_THREATS', 'transformation')} t
        JOIN {get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')} d
            ON t.ALERT_KEY = d.ALERT_KEY
        WHERE t.DETECTION_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
          AND d.SEVERITY IN ('Critical', 'High', 'Medium')
        GROUP BY DAY, d.SEVERITY
        ORDER BY DAY
    """

    trend_data = safe_query(trend_sql, "Failed to load trend data")

    if not trend_data.empty:
        fig = px.line(
            trend_data,
            x='DAY',
            y='THREAT_COUNT',
            color='SEVERITY',
            title="Daily Threat Detections",
            color_discrete_map={'Critical': '#e74c3c', 'High': '#e67e22', 'Medium': '#f39c12'}
        )
        st.info("Interactive chart not available in Snowflake - view data in table below")

# ---------------------------------------------------------------------------
# TAB 4: SOURCE ANALYSIS
# ---------------------------------------------------------------------------

with tab4:
    st.subheader("Threat Source Analysis")

    source_sql = f"""
        SELECT
            d.SOURCE,
            COUNT(*) as THREAT_COUNT,
            SUM(CASE WHEN d.SEVERITY = 'Critical' THEN 1 ELSE 0 END) as CRITICAL_COUNT
        FROM {get_table_name('FACT_CYBELANGEL_THREATS', 'transformation')} t
        JOIN {get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')} d
            ON t.ALERT_KEY = d.ALERT_KEY
        WHERE t.DETECTION_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
          AND d.SOURCE IS NOT NULL
        GROUP BY d.SOURCE
        ORDER BY THREAT_COUNT DESC
        LIMIT 20
    """

    source_data = safe_query(source_sql, "Failed to load source data")

    if not source_data.empty:
        fig = px.bar(
            source_data,
            x='SOURCE',
            y='THREAT_COUNT',
            color='CRITICAL_COUNT',
            title="Threats by Source",
            color_continuous_scale='Reds'
        )
        st.info("Interactive chart not available in Snowflake - view data in table below")

        st.dataframe(source_data, use_container_width=True)

# ---------------------------------------------------------------------------
# TAB 5: DATA LEAK ANALYSIS
# ---------------------------------------------------------------------------

with tab5:
    st.subheader("Data Leak Detection & Analysis")

    # Data leak KPIs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_leaks_sql = f"""
            SELECT COUNT(*) as TOTAL_LEAKS
            FROM {get_table_name('FACT_CYBELANGEL_THREATS', 'transformation')} t
            JOIN {get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')} d
                ON t.ALERT_KEY = d.ALERT_KEY
            WHERE t.DETECTION_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
              AND d.CATEGORY LIKE '%Data Leak%'
        """
        leaks_data = safe_query(total_leaks_sql, "Failed to load data leaks")

        if not leaks_data.empty:
            st.metric(
                "Total Data Leaks",
                f"{leaks_data['TOTAL_LEAKS'].iloc[0]:,}",
                help="Total data leak incidents detected"
            )

    with col2:
        credential_leaks_sql = f"""
            SELECT COUNT(*) as CREDENTIAL_LEAKS
            FROM {get_table_name('FACT_CYBELANGEL_THREATS', 'transformation')} t
            JOIN {get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')} d
                ON t.ALERT_KEY = d.ALERT_KEY
            WHERE t.DETECTION_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
              AND (d.CATEGORY LIKE '%Credential%' OR d.CATEGORY LIKE '%Password%')
        """
        creds_data = safe_query(credential_leaks_sql, "Failed to load credential leaks")

        if not creds_data.empty:
            cred_count = creds_data['CREDENTIAL_LEAKS'].iloc[0]
            st.metric(
                "Credential Exposures",
                f"{cred_count:,}",
                delta=f"🔴 {cred_count}",
                delta_color="inverse",
                help="Exposed credentials detected"
            )

    with col3:
        darkweb_sql = f"""
            SELECT COUNT(*) as DARKWEB_MENTIONS
            FROM {get_table_name('FACT_CYBELANGEL_THREATS', 'transformation')} t
            JOIN {get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')} d
                ON t.ALERT_KEY = d.ALERT_KEY
            WHERE t.DETECTION_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
              AND d.SOURCE LIKE '%Dark Web%'
        """
        darkweb_data = safe_query(darkweb_sql, "Failed to load dark web mentions")

        if not darkweb_data.empty:
            st.metric(
                "Dark Web Mentions",
                f"{darkweb_data['DARKWEB_MENTIONS'].iloc[0]:,}",
                help="Mentions found on dark web"
            )

    with col4:
        brand_abuse_sql = f"""
            SELECT COUNT(*) as BRAND_ABUSE
            FROM {get_table_name('FACT_CYBELANGEL_THREATS', 'transformation')} t
            JOIN {get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')} d
                ON t.ALERT_KEY = d.ALERT_KEY
            WHERE t.DETECTION_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
              AND d.CATEGORY LIKE '%Brand%'
        """
        brand_data = safe_query(brand_abuse_sql, "Failed to load brand abuse")

        if not brand_data.empty:
            st.metric(
                "Brand Abuse Cases",
                f"{brand_data['BRAND_ABUSE'].iloc[0]:,}",
                help="Brand infringement incidents"
            )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Data Leak Types")

        leak_types_sql = f"""
            SELECT
                CASE
                    WHEN d.CATEGORY LIKE '%Credential%' THEN 'Credentials'
                    WHEN d.CATEGORY LIKE '%Database%' THEN 'Database'
                    WHEN d.CATEGORY LIKE '%Document%' THEN 'Documents'
                    WHEN d.CATEGORY LIKE '%Source Code%' THEN 'Source Code'
                    WHEN d.CATEGORY LIKE '%PII%' THEN 'Personal Info'
                    ELSE 'Other Data Leak'
                END as LEAK_TYPE,
                COUNT(*) as LEAK_COUNT,
                SUM(CASE WHEN d.SEVERITY IN ('Critical', 'High') THEN 1 ELSE 0 END) as HIGH_SEVERITY_COUNT
            FROM {get_table_name('FACT_CYBELANGEL_THREATS', 'transformation')} t
            JOIN {get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')} d
                ON t.ALERT_KEY = d.ALERT_KEY
            WHERE t.DETECTION_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
              AND d.CATEGORY LIKE '%Data Leak%'
            GROUP BY LEAK_TYPE
            ORDER BY LEAK_COUNT DESC
        """

        leak_types = safe_query(leak_types_sql, "Failed to load leak types")

        if not leak_types.empty:
            fig = px.bar(
                leak_types,
                x='LEAK_TYPE',
                y='LEAK_COUNT',
                color='HIGH_SEVERITY_COUNT',
                title="Data Leak Distribution",
                color_continuous_scale='Reds',
                text='LEAK_COUNT'
            )
            st.info("Interactive chart not available in Snowflake - view data in table below")

    with col2:
        st.markdown("#### Exposure Locations")

        exposure_loc_sql = f"""
            SELECT
                d.SOURCE,
                COUNT(*) as EXPOSURE_COUNT
            FROM {get_table_name('FACT_CYBELANGEL_THREATS', 'transformation')} t
            JOIN {get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')} d
                ON t.ALERT_KEY = d.ALERT_KEY
            WHERE t.DETECTION_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
              AND d.CATEGORY LIKE '%Data Leak%'
              AND d.SOURCE IS NOT NULL
            GROUP BY d.SOURCE
            ORDER BY EXPOSURE_COUNT DESC
            LIMIT 10
        """

        exposure_loc = safe_query(exposure_loc_sql, "Failed to load exposure locations")

        if not exposure_loc.empty:
            fig = px.pie(
                exposure_loc,
                values='EXPOSURE_COUNT',
                names='SOURCE',
                title="Data Exposure by Source",
                hole=0.4
            )
            st.info("Interactive chart not available in Snowflake - view data in table below")

    # Critical data leaks
    st.markdown("---")
    st.markdown("#### Critical Data Leak Incidents")

    critical_leaks_sql = f"""
        SELECT
            t.THREAT_ID,
            d.ALERT_TYPE,
            d.CATEGORY,
            d.SEVERITY,
            d.SOURCE,
            t.DETECTION_DATE,
            d.STATUS,
            d.DESCRIPTION,
            d.AFFECTED_ASSETS
        FROM {get_table_name('FACT_CYBELANGEL_THREATS', 'transformation')} t
        JOIN {get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')} d
            ON t.ALERT_KEY = d.ALERT_KEY
        WHERE t.DETECTION_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
          AND d.CATEGORY LIKE '%Data Leak%'
          AND d.SEVERITY IN ('Critical', 'High')
          AND d.STATUS != 'Closed'
        ORDER BY
            CASE d.SEVERITY
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
            END,
            t.DETECTION_DATE DESC
        LIMIT 50
    """

    critical_leaks = safe_query(critical_leaks_sql, "Failed to load critical leaks")

    if not critical_leaks.empty:
        st.dataframe(
            critical_leaks.style.apply(
                lambda x: ['background-color: #ffebee' if x['SEVERITY'] == 'Critical'
                          else 'background-color: #fff3e0' if x['SEVERITY'] == 'High'
                          else '' for _ in x], axis=1
            ),
            use_container_width=True,
            height=400
        )
        export_csv(critical_leaks, "cybelangel_critical_leaks")
    else:
        st.success("✅ No critical data leaks detected")

# ---------------------------------------------------------------------------
# TAB 6: RESPONSE METRICS
# ---------------------------------------------------------------------------

with tab6:
    st.subheader("Threat Response Performance")

    # Response time KPIs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_response_sql = f"""
            SELECT ROUND(AVG(DATEDIFF(hour, t.DETECTION_DATE, d.FIRST_RESPONSE_DATE)), 1) as AVG_RESPONSE_HRS
            FROM {get_table_name('FACT_CYBELANGEL_THREATS', 'transformation')} t
            JOIN {get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')} d
                ON t.ALERT_KEY = d.ALERT_KEY
            WHERE t.DETECTION_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
              AND d.FIRST_RESPONSE_DATE IS NOT NULL
        """
        response_data = safe_query(avg_response_sql, "Failed to load response time")

        if not response_data.empty and response_data['AVG_RESPONSE_HRS'].iloc[0] is not None:
            avg_hrs = response_data['AVG_RESPONSE_HRS'].iloc[0]
            st.metric(
                "Avg Response Time",
                f"{avg_hrs:.1f} hrs",
                delta=f"{avg_hrs - 24:+.1f} hrs",
                delta_color="inverse",
                help="Average time to first response"
            )

    with col2:
        avg_resolution_sql = f"""
            SELECT ROUND(AVG(DATEDIFF(hour, t.DETECTION_DATE, d.RESOLUTION_DATE)), 1) as AVG_RESOLUTION_HRS
            FROM {get_table_name('FACT_CYBELANGEL_THREATS', 'transformation')} t
            JOIN {get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')} d
                ON t.ALERT_KEY = d.ALERT_KEY
            WHERE t.DETECTION_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
              AND d.RESOLUTION_DATE IS NOT NULL
        """
        resolution_data = safe_query(avg_resolution_sql, "Failed to load resolution time")

        if not resolution_data.empty and resolution_data['AVG_RESOLUTION_HRS'].iloc[0] is not None:
            st.metric(
                "Avg Resolution Time",
                f"{resolution_data['AVG_RESOLUTION_HRS'].iloc[0]:.1f} hrs",
                help="Average time to resolve threats"
            )

    with col3:
        resolution_rate_sql = f"""
            SELECT
                ROUND(SUM(CASE WHEN d.STATUS = 'Closed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as RESOLUTION_RATE
            FROM {get_table_name('FACT_CYBELANGEL_THREATS', 'transformation')} t
            JOIN {get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')} d
                ON t.ALERT_KEY = d.ALERT_KEY
            WHERE t.DETECTION_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
        """
        rate_data = safe_query(resolution_rate_sql, "Failed to load resolution rate")

        if not rate_data.empty and rate_data['RESOLUTION_RATE'].iloc[0] is not None:
            rate = rate_data['RESOLUTION_RATE'].iloc[0]
            st.metric(
                "Resolution Rate",
                f"{rate:.1f}%",
                delta=f"{rate - 80:+.1f}%",
                help="Percentage of threats resolved"
            )

    with col4:
        overdue_sql = f"""
            SELECT COUNT(*) as OVERDUE_COUNT
            FROM {get_table_name('FACT_CYBELANGEL_THREATS', 'transformation')} t
            JOIN {get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')} d
                ON t.ALERT_KEY = d.ALERT_KEY
            WHERE d.STATUS IN ('Open', 'In Progress')
              AND DATEDIFF(day, t.DETECTION_DATE, CURRENT_DATE()) > 7
        """
        overdue_data = safe_query(overdue_sql, "Failed to load overdue threats")

        if not overdue_data.empty:
            overdue_count = overdue_data['OVERDUE_COUNT'].iloc[0]
            st.metric(
                "Overdue (>7 days)",
                f"{overdue_count:,}",
                delta=f"⚠️ {overdue_count}",
                delta_color="inverse",
                help="Open threats older than 7 days"
            )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Response Time by Severity")

        response_by_severity_sql = f"""
            SELECT
                d.SEVERITY,
                COUNT(*) as THREAT_COUNT,
                ROUND(AVG(DATEDIFF(hour, t.DETECTION_DATE, d.FIRST_RESPONSE_DATE)), 1) as AVG_RESPONSE_HRS,
                ROUND(AVG(DATEDIFF(hour, t.DETECTION_DATE, d.RESOLUTION_DATE)), 1) as AVG_RESOLUTION_HRS
            FROM {get_table_name('FACT_CYBELANGEL_THREATS', 'transformation')} t
            JOIN {get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')} d
                ON t.ALERT_KEY = d.ALERT_KEY
            WHERE t.DETECTION_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
              AND d.FIRST_RESPONSE_DATE IS NOT NULL
            GROUP BY d.SEVERITY
            ORDER BY
                CASE d.SEVERITY
                    WHEN 'Critical' THEN 1
                    WHEN 'High' THEN 2
                    WHEN 'Medium' THEN 3
                    ELSE 4
                END
        """

        response_by_sev = safe_query(response_by_severity_sql, "Failed to load response by severity")

        if not response_by_sev.empty:
            # fig = go.Figure(  # Plotly not available)
            # fig.add_trace(  # Plotly not availablego.Bar(
                name='Avg Response Time',
                x=response_by_sev['SEVERITY'],
                y=response_by_sev['AVG_RESPONSE_HRS'],
                marker_color='#3498db'
            ))
            # fig.add_trace(  # Plotly not availablego.Bar(
                name='Avg Resolution Time',
                x=response_by_sev['SEVERITY'],
                y=response_by_sev['AVG_RESOLUTION_HRS'],
                marker_color='#e74c3c'
            ))
            # fig.update_layout(  # Plotly not available
                title="Response & Resolution Time by Severity",
                barmode='group',
                yaxis_title="Hours"
            )
            st.info("Interactive chart not available in Snowflake - view data in table below")

    with col2:
        st.markdown("#### Threat Status Distribution")

        status_dist_sql = f"""
            SELECT
                d.STATUS,
                COUNT(*) as THREAT_COUNT
            FROM {get_table_name('FACT_CYBELANGEL_THREATS', 'transformation')} t
            JOIN {get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')} d
                ON t.ALERT_KEY = d.ALERT_KEY
            WHERE t.DETECTION_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
            GROUP BY d.STATUS
            ORDER BY THREAT_COUNT DESC
        """

        status_dist = safe_query(status_dist_sql, "Failed to load status distribution")

        if not status_dist.empty:
            colors_map = {
                'Closed': '#27ae60',
                'In Progress': '#f39c12',
                'Open': '#e74c3c',
                'New': '#e67e22'
            }
            fig = px.pie(
                status_dist,
                values='THREAT_COUNT',
                names='STATUS',
                title="Threat Status Overview",
                color='STATUS',
                color_discrete_map=colors_map
            )
            st.info("Interactive chart not available in Snowflake - view data in table below")

    # Overdue threats details
    st.markdown("---")
    st.markdown("#### Overdue Threat Alerts (>7 Days Open)")

    overdue_threats_sql = f"""
        SELECT
            t.THREAT_ID,
            d.ALERT_TYPE,
            d.CATEGORY,
            d.SEVERITY,
            t.DETECTION_DATE,
            DATEDIFF(day, t.DETECTION_DATE, CURRENT_DATE()) as DAYS_OPEN,
            d.STATUS,
            d.ASSIGNED_TO,
            d.DESCRIPTION
        FROM {get_table_name('FACT_CYBELANGEL_THREATS', 'transformation')} t
        JOIN {get_table_name('DIM_CYBELANGEL_ALERTS', 'transformation')} d
            ON t.ALERT_KEY = d.ALERT_KEY
        WHERE d.STATUS IN ('Open', 'In Progress', 'New')
          AND DATEDIFF(day, t.DETECTION_DATE, CURRENT_DATE()) > 7
        ORDER BY DAYS_OPEN DESC,
            CASE d.SEVERITY
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                ELSE 4
            END
        LIMIT 50
    """

    overdue_threats = safe_query(overdue_threats_sql, "Failed to load overdue threats")

    if not overdue_threats.empty:
        st.dataframe(
            overdue_threats.style.background_gradient(
                subset=['DAYS_OPEN'],
                cmap='Reds'
            ),
            use_container_width=True
        )
        export_csv(overdue_threats, "cybelangel_overdue_threats")
        st.caption(f"Found {len(overdue_threats):,} overdue threats requiring attention")
    else:
        st.success("✅ No overdue threats - all threats being addressed within SLA")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("""
**Data Source:** CybelAngel Platform via Snowflake
**Refresh Rate:** 5-minute cache
**Contact:** GenericCorp Data Engineering Team
""")
