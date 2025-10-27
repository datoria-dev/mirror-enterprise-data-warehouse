"""
ServiceNow ITSM Dashboard

IT Service Management dashboard for ServiceNow platform,
monitoring incidents, changes, CMDB, and ITSM KPIs.
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
    page_title="ServiceNow ITSM Dashboard",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply common styles
apply_common_styles()

# ============================================================================
# ENVIRONMENT VALIDATION
# ============================================================================

REQUIRED_OBJECTS = [
    get_table_name('DIM_SNOW_INCIDENT', 'transformation'),
    get_table_name('DIM_SNOW_DEVICE', 'transformation'),
    get_table_name('DIM_SNOW_CHANGE', 'transformation'),
    get_view_name('VW_SERVICENOW_KPI_SUMMARY', 'reporting')
]

validate_environment(REQUIRED_OBJECTS)
session = get_active_session()

# ============================================================================
# HEADER
# ============================================================================

create_header(
    title="ServiceNow ITSM Dashboard",
    subtitle="IT Service Management & CMDB Monitoring",
    icon="🎫"
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
        help="Select time range for ITSM analysis"
    )
    days = DATE_RANGES[date_range]

    priority_filter = st.multiselect(
        "Incident Priority",
        ['1 - Critical', '2 - High', '3 - Medium', '4 - Low'],
        default=['1 - Critical', '2 - High'],
        help="Filter by incident priority"
    )

    state_filter = st.multiselect(
        "Incident State",
        ['New', 'In Progress', 'On Hold', 'Resolved', 'Closed'],
        default=['New', 'In Progress', 'On Hold'],
        help="Filter by incident state"
    )

    st.markdown("---")
    add_refresh_button()

    st.info("""
    **📊 Data Source:**
    ServiceNow ITSM Platform

    **📈 Metrics Tracked:**
    - Incident management (MTTR)
    - Change management success rate
    - CMDB asset inventory
    - Problem records
    - SLA compliance
    """)

    show_last_refresh()

# ============================================================================
# MAIN CONTENT
# ============================================================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Overview",
    "🎫 Incidents",
    "🔄 Changes",
    "💻 CMDB Assets",
    "📈 KPIs",
    "⏱️ SLA Compliance",
    "📉 Trends & Analytics"
])

# ---------------------------------------------------------------------------
# TAB 1: OVERVIEW
# ---------------------------------------------------------------------------

with tab1:
    st.subheader("ServiceNow ITSM Overview")

    show_data_freshness(
        get_table_name('DIM_SNOW_INCIDENT', 'transformation'),
        timestamp_column='OPENED_DATE'
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        incidents_sql = f"""
            SELECT COUNT(*) as OPEN_INCIDENTS
            FROM {get_table_name('DIM_SNOW_INCIDENT', 'transformation')}
            WHERE STATE IN ('New', 'In Progress', 'On Hold')
              AND OPENED_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
        """
        incidents_data = safe_query(incidents_sql, "Failed to load incidents")

        if not incidents_data.empty:
            st.metric(
                "Open Incidents",
                f"{incidents_data['OPEN_INCIDENTS'].iloc[0]:,}",
                help="Total open incidents"
            )

    with col2:
        critical_sql = f"""
            SELECT COUNT(*) as CRITICAL_INCIDENTS
            FROM {get_table_name('DIM_SNOW_INCIDENT', 'transformation')}
            WHERE PRIORITY = '1 - Critical'
              AND STATE IN ('New', 'In Progress', 'On Hold')
        """
        critical_data = safe_query(critical_sql, "Failed to load critical incidents")

        if not critical_data.empty:
            critical_count = critical_data['CRITICAL_INCIDENTS'].iloc[0]
            st.metric(
                "Critical Incidents",
                f"{critical_count:,}",
                delta=f"🔴 {critical_count}",
                delta_color="inverse",
                help="Priority 1 incidents requiring immediate attention"
            )

    with col3:
        mttr_sql = f"""
            SELECT
                ROUND(AVG(DATEDIFF(hour, OPENED_DATE, RESOLVED_DATE)), 1) as AVG_MTTR
            FROM {get_table_name('DIM_SNOW_INCIDENT', 'transformation')}
            WHERE RESOLVED_DATE IS NOT NULL
              AND OPENED_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
        """
        mttr_data = safe_query(mttr_sql, "Failed to load MTTR")

        if not mttr_data.empty and mttr_data['AVG_MTTR'].iloc[0] is not None:
            mttr_hours = mttr_data['AVG_MTTR'].iloc[0]
            st.metric(
                "Avg MTTR",
                f"{mttr_hours} hrs",
                delta=f"{mttr_hours - 24:+.1f} hrs",
                delta_color="inverse",
                help="Mean Time To Resolve (hours)"
            )

    with col4:
        assets_sql = f"""
            SELECT COUNT(*) as TOTAL_ASSETS
            FROM {get_table_name('DIM_SNOW_DEVICE', 'transformation')}
            WHERE IS_ACTIVE = TRUE
        """
        assets_data = safe_query(assets_sql, "Failed to load assets")

        if not assets_data.empty:
            st.metric(
                "CMDB Assets",
                f"{assets_data['TOTAL_ASSETS'].iloc[0]:,}",
                help="Total active assets in CMDB"
            )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Incident Priority Distribution")

        priority_sql = f"""
            SELECT
                PRIORITY,
                COUNT(*) as INCIDENT_COUNT
            FROM {get_table_name('DIM_SNOW_INCIDENT', 'transformation')}
            WHERE OPENED_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
              AND STATE IN ('New', 'In Progress', 'On Hold')
            GROUP BY PRIORITY
            ORDER BY PRIORITY
        """

        priority_data = safe_query(priority_sql, "Failed to load priority data")

        if not priority_data.empty:
            colors = {
                '1 - Critical': '#e74c3c',
                '2 - High': '#e67e22',
                '3 - Medium': '#f39c12',
                '4 - Low': '#3498db'
            }
            fig = px.pie(priority_data, values='INCIDENT_COUNT', names='PRIORITY', color='PRIORITY', color_discrete_map=colors)
            st.info("Interactive chart not available in Snowflake - view data in table below")

    with col2:
        st.subheader("Top Assignment Groups")

        assignment_sql = f"""
            SELECT
                ASSIGNMENT_GROUP,
                COUNT(*) as INCIDENT_COUNT
            FROM {get_table_name('DIM_SNOW_INCIDENT', 'transformation')}
            WHERE OPENED_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
              AND STATE IN ('New', 'In Progress', 'On Hold')
              AND ASSIGNMENT_GROUP IS NOT NULL
            GROUP BY ASSIGNMENT_GROUP
            ORDER BY INCIDENT_COUNT DESC
            LIMIT 10
        """

        assignment_data = safe_query(assignment_sql, "Failed to load assignment data")

        if not assignment_data.empty:
            fig = px.bar(assignment_data, x='INCIDENT_COUNT', y='ASSIGNMENT_GROUP', orientation='h')
            # fig.update_layout(  # Plotly not availableyaxis={'categoryorder': 'total ascending'})
            st.info("Interactive chart not available in Snowflake - view data in table below")

# ---------------------------------------------------------------------------
# TAB 2: INCIDENTS
# ---------------------------------------------------------------------------

with tab2:
    st.subheader("Incident Records")

    priority_filter_sql = "','".join(priority_filter) if priority_filter else "'1 - Critical','2 - High','3 - Medium','4 - Low'"
    state_filter_sql = "','".join(state_filter) if state_filter else "'New','In Progress','On Hold'"

    incidents_detail_sql = f"""
        SELECT
            NUMBER as INCIDENT_NUMBER,
            PRIORITY,
            STATE,
            OPENED_DATE,
            SHORT_DESCRIPTION,
            ASSIGNMENT_GROUP,
            ASSIGNED_TO,
            CATEGORY,
            SUBCATEGORY
        FROM {get_table_name('DIM_SNOW_INCIDENT', 'transformation')}
        WHERE OPENED_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
          AND PRIORITY IN ('{priority_filter_sql}')
          AND STATE IN ('{state_filter_sql}')
        ORDER BY OPENED_DATE DESC
        LIMIT 1000
    """

    incidents_detail = query_with_metrics(incidents_detail_sql, "Failed to load incidents")

    if not incidents_detail.empty:
        search_term = st.text_input("🔍 Search incidents", "")

        if search_term:
            incidents_detail = incidents_detail[
                incidents_detail.astype(str).apply(
                    lambda x: x.str.contains(search_term, case=False, na=False)
                ).any(axis=1)
            ]

        st.dataframe(incidents_detail, use_container_width=True, height=500)
        export_csv(incidents_detail, "servicenow_incidents")
        st.caption(f"Showing {len(incidents_detail):,} incidents")

# ---------------------------------------------------------------------------
# TAB 3: CHANGES
# ---------------------------------------------------------------------------

with tab3:
    st.subheader("Change Management")

    changes_sql = f"""
        SELECT
            CHANGE_NUMBER,
            CHANGE_TYPE,
            RISK_LEVEL,
            STATE,
            SCHEDULED_START,
            SCHEDULED_END,
            SHORT_DESCRIPTION,
            REQUESTED_BY
        FROM {get_table_name('DIM_SNOW_CHANGE', 'transformation')}
        WHERE SCHEDULED_START >= DATEADD(day, -{days}, CURRENT_DATE())
        ORDER BY SCHEDULED_START DESC
        LIMIT 500
    """

    changes_data = safe_query(changes_sql, "Failed to load changes")

    if not changes_data.empty:
        st.dataframe(changes_data, use_container_width=True, height=500)
        export_csv(changes_data, "servicenow_changes")
        st.caption(f"Showing {len(changes_data):,} change requests")
    else:
        st.info("No change requests found in selected period")

# ---------------------------------------------------------------------------
# TAB 4: CMDB ASSETS
# ---------------------------------------------------------------------------

with tab4:
    st.subheader("CMDB Asset Inventory")

    assets_sql = f"""
        SELECT
            DEVICE_NAME,
            DEVICE_CLASS,
            MANUFACTURER,
            MODEL,
            OPERATING_SYSTEM,
            IP_ADDRESS,
            LOCATION,
            IS_ACTIVE,
            LAST_DISCOVERED
        FROM {get_table_name('DIM_SNOW_DEVICE', 'transformation')}
        WHERE IS_ACTIVE = TRUE
        ORDER BY LAST_DISCOVERED DESC NULLS LAST
        LIMIT 500
    """

    assets_data = safe_query(assets_sql, "Failed to load assets")

    if not assets_data.empty:
        st.dataframe(assets_data, use_container_width=True, height=500)
        export_csv(assets_data, "servicenow_cmdb_assets")
        st.caption(f"Showing {len(assets_data):,} CMDB assets")

# ---------------------------------------------------------------------------
# TAB 5: KPIs
# ---------------------------------------------------------------------------

with tab5:
    st.subheader("ServiceNow KPI Summary")

    kpi_sql = f"""
        SELECT *
        FROM {get_view_name('VW_SERVICENOW_KPI_SUMMARY', 'reporting')}
    """

    kpi_data = safe_query(kpi_sql, "Failed to load KPIs")

    if not kpi_data.empty:
        st.dataframe(kpi_data, use_container_width=True)
    else:
        st.info("KPI summary not available")

# ---------------------------------------------------------------------------
# TAB 6: SLA COMPLIANCE
# ---------------------------------------------------------------------------

with tab6:
    st.subheader("SLA Compliance Monitoring")

    # SLA KPIs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        sla_met_sql = f"""
            SELECT
                COUNT(*) as SLA_MET_COUNT,
                ROUND(COUNT(*) * 100.0 / NULLIF((
                    SELECT COUNT(*) FROM {get_table_name('DIM_SNOW_INCIDENT', 'transformation')}
                    WHERE RESOLVED_DATE IS NOT NULL
                      AND OPENED_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
                ), 0), 1) as SLA_MET_PCT
            FROM {get_table_name('DIM_SNOW_INCIDENT', 'transformation')}
            WHERE RESOLVED_DATE IS NOT NULL
              AND SLA_MET = TRUE
              AND OPENED_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
        """
        sla_met_data = safe_query(sla_met_sql, "Failed to load SLA met data")

        if not sla_met_data.empty:
            sla_pct = sla_met_data['SLA_MET_PCT'].iloc[0] if sla_met_data['SLA_MET_PCT'].iloc[0] is not None else 0
            st.metric(
                "SLA Compliance",
                f"{sla_pct:.1f}%",
                delta=f"{sla_pct - 95:+.1f}%",
                help="Percentage of incidents resolved within SLA"
            )

    with col2:
        sla_breached_sql = f"""
            SELECT COUNT(*) as BREACHED_COUNT
            FROM {get_table_name('DIM_SNOW_INCIDENT', 'transformation')}
            WHERE SLA_MET = FALSE
              AND RESOLVED_DATE IS NOT NULL
              AND OPENED_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
        """
        sla_breached_data = safe_query(sla_breached_sql, "Failed to load SLA breached")

        if not sla_breached_data.empty:
            breached_count = sla_breached_data['BREACHED_COUNT'].iloc[0]
            st.metric(
                "SLA Breaches",
                f"{breached_count:,}",
                delta=f"🔴 {breached_count}",
                delta_color="inverse",
                help="Incidents that exceeded SLA targets"
            )

    with col3:
        at_risk_sql = f"""
            SELECT COUNT(*) as AT_RISK_COUNT
            FROM {get_table_name('DIM_SNOW_INCIDENT', 'transformation')}
            WHERE STATE IN ('New', 'In Progress', 'On Hold')
              AND DATEDIFF(hour, OPENED_DATE, CURRENT_TIMESTAMP()) > (SLA_TARGET_HOURS * 0.75)
              AND OPENED_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
        """
        at_risk_data = safe_query(at_risk_sql, "Failed to load at-risk incidents")

        if not at_risk_data.empty:
            at_risk_count = at_risk_data['AT_RISK_COUNT'].iloc[0]
            st.metric(
                "At Risk (>75% SLA)",
                f"{at_risk_count:,}",
                delta=f"⚠️ {at_risk_count}",
                delta_color="inverse",
                help="Open incidents approaching SLA deadline"
            )

    with col4:
        avg_resolution_sql = f"""
            SELECT ROUND(AVG(DATEDIFF(hour, OPENED_DATE, RESOLVED_DATE)), 1) as AVG_RESOLUTION_TIME
            FROM {get_table_name('DIM_SNOW_INCIDENT', 'transformation')}
            WHERE RESOLVED_DATE IS NOT NULL
              AND OPENED_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
        """
        avg_resolution_data = safe_query(avg_resolution_sql, "Failed to load avg resolution")

        if not avg_resolution_data.empty and avg_resolution_data['AVG_RESOLUTION_TIME'].iloc[0] is not None:
            avg_hours = avg_resolution_data['AVG_RESOLUTION_TIME'].iloc[0]
            st.metric(
                "Avg Resolution Time",
                f"{avg_hours:.1f} hrs",
                help="Average time to resolve incidents"
            )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### SLA Compliance by Priority")

        sla_by_priority_sql = f"""
            SELECT
                PRIORITY,
                COUNT(*) as TOTAL_INCIDENTS,
                SUM(CASE WHEN SLA_MET = TRUE THEN 1 ELSE 0 END) as SLA_MET_COUNT,
                ROUND(SUM(CASE WHEN SLA_MET = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as COMPLIANCE_PCT
            FROM {get_table_name('DIM_SNOW_INCIDENT', 'transformation')}
            WHERE RESOLVED_DATE IS NOT NULL
              AND OPENED_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
            GROUP BY PRIORITY
            ORDER BY PRIORITY
        """

        sla_by_priority = safe_query(sla_by_priority_sql, "Failed to load SLA by priority")

        if not sla_by_priority.empty:
            fig = px.bar(
                sla_by_priority,
                x='PRIORITY',
                y='COMPLIANCE_PCT',
                text='COMPLIANCE_PCT',
                title="SLA Compliance % by Priority",
                color='COMPLIANCE_PCT',
                color_continuous_scale='RdYlGn',
                range_color=[0, 100]
            )
            fig.add_hline(y=95, line_dash="dash", line_color="red", annotation_text="95% Target")
            st.info("Interactive chart not available in Snowflake - view data in table below")

    with col2:
        st.markdown("#### SLA Breaches by Assignment Group")

        breaches_by_group_sql = f"""
            SELECT
                ASSIGNMENT_GROUP,
                COUNT(*) as BREACH_COUNT
            FROM {get_table_name('DIM_SNOW_INCIDENT', 'transformation')}
            WHERE SLA_MET = FALSE
              AND RESOLVED_DATE IS NOT NULL
              AND OPENED_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
              AND ASSIGNMENT_GROUP IS NOT NULL
            GROUP BY ASSIGNMENT_GROUP
            ORDER BY BREACH_COUNT DESC
            LIMIT 10
        """

        breaches_by_group = safe_query(breaches_by_group_sql, "Failed to load breaches by group")

        if not breaches_by_group.empty:
            fig = px.bar(
                breaches_by_group,
                x='BREACH_COUNT',
                y='ASSIGNMENT_GROUP',
                orientation='h',
                title="Top 10 Groups by SLA Breaches",
                color='BREACH_COUNT',
                color_continuous_scale='Reds'
            )
            # fig.update_layout(  # Plotly not availableyaxis={'categoryorder': 'total ascending'})
            st.info("Interactive chart not available in Snowflake - view data in table below")

    # Critical incidents at risk
    st.markdown("#### Critical Incidents At Risk of SLA Breach")

    critical_at_risk_sql = f"""
        SELECT
            NUMBER as INCIDENT_NUMBER,
            PRIORITY,
            STATE,
            OPENED_DATE,
            SHORT_DESCRIPTION,
            ASSIGNMENT_GROUP,
            ASSIGNED_TO,
            SLA_TARGET_HOURS,
            DATEDIFF(hour, OPENED_DATE, CURRENT_TIMESTAMP()) as HOURS_OPEN,
            ROUND((DATEDIFF(hour, OPENED_DATE, CURRENT_TIMESTAMP()) * 100.0 / SLA_TARGET_HOURS), 1) as SLA_CONSUMED_PCT
        FROM {get_table_name('DIM_SNOW_INCIDENT', 'transformation')}
        WHERE PRIORITY IN ('1 - Critical', '2 - High')
          AND STATE IN ('New', 'In Progress', 'On Hold')
          AND DATEDIFF(hour, OPENED_DATE, CURRENT_TIMESTAMP()) > (SLA_TARGET_HOURS * 0.75)
        ORDER BY SLA_CONSUMED_PCT DESC
        LIMIT 50
    """

    critical_at_risk = safe_query(critical_at_risk_sql, "Failed to load critical at-risk")

    if not critical_at_risk.empty:
        st.dataframe(
            critical_at_risk.style.background_gradient(
                subset=['SLA_CONSUMED_PCT'],
                cmap='Reds',
                vmin=75,
                vmax=100
            ),
            use_container_width=True
        )
        export_csv(critical_at_risk, "servicenow_critical_at_risk")
    else:
        st.success("✅ No critical incidents at risk of SLA breach")

# ---------------------------------------------------------------------------
# TAB 7: TRENDS & ANALYTICS
# ---------------------------------------------------------------------------

with tab7:
    st.subheader("Incident Trends & Analytics")

    # Daily incident trend
    st.markdown("#### Daily Incident Volume")

    daily_trend_sql = f"""
        SELECT
            DATE_TRUNC('day', OPENED_DATE) as DAY,
            PRIORITY,
            COUNT(*) as INCIDENT_COUNT
        FROM {get_table_name('DIM_SNOW_INCIDENT', 'transformation')}
        WHERE OPENED_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
        GROUP BY DAY, PRIORITY
        ORDER BY DAY
    """

    daily_trend = safe_query(daily_trend_sql, "Failed to load daily trend")

    if not daily_trend.empty:
        fig = px.line(
            daily_trend,
            x='DAY',
            y='INCIDENT_COUNT',
            color='PRIORITY',
            title="Daily Incident Trend by Priority",
            markers=True
        )
        st.info("Interactive chart not available in Snowflake - view data in table below")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Top Incident Categories")

        category_trend_sql = f"""
            SELECT
                CATEGORY,
                COUNT(*) as INCIDENT_COUNT,
                ROUND(AVG(DATEDIFF(hour, OPENED_DATE, RESOLVED_DATE)), 1) as AVG_RESOLUTION_HRS
            FROM {get_table_name('DIM_SNOW_INCIDENT', 'transformation')}
            WHERE OPENED_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
              AND CATEGORY IS NOT NULL
            GROUP BY CATEGORY
            ORDER BY INCIDENT_COUNT DESC
            LIMIT 10
        """

        category_trend = safe_query(category_trend_sql, "Failed to load category trend")

        if not category_trend.empty:
            fig = px.scatter(
                category_trend,
                x='INCIDENT_COUNT',
                y='AVG_RESOLUTION_HRS',
                size='INCIDENT_COUNT',
                text='CATEGORY',
                title="Incident Volume vs Resolution Time",
                labels={'INCIDENT_COUNT': 'Incidents', 'AVG_RESOLUTION_HRS': 'Avg Resolution (hrs)'}
            )
            st.info("Interactive chart not available in Snowflake - view data in table below")

    with col2:
        st.markdown("#### Resolution Time Distribution")

        resolution_dist_sql = f"""
            SELECT
                CASE
                    WHEN DATEDIFF(hour, OPENED_DATE, RESOLVED_DATE) <= 4 THEN '0-4 hours'
                    WHEN DATEDIFF(hour, OPENED_DATE, RESOLVED_DATE) <= 8 THEN '4-8 hours'
                    WHEN DATEDIFF(hour, OPENED_DATE, RESOLVED_DATE) <= 24 THEN '8-24 hours'
                    WHEN DATEDIFF(hour, OPENED_DATE, RESOLVED_DATE) <= 72 THEN '1-3 days'
                    ELSE '3+ days'
                END as RESOLUTION_TIME_BUCKET,
                COUNT(*) as INCIDENT_COUNT
            FROM {get_table_name('DIM_SNOW_INCIDENT', 'transformation')}
            WHERE RESOLVED_DATE IS NOT NULL
              AND OPENED_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
            GROUP BY RESOLUTION_TIME_BUCKET
            ORDER BY
                CASE RESOLUTION_TIME_BUCKET
                    WHEN '0-4 hours' THEN 1
                    WHEN '4-8 hours' THEN 2
                    WHEN '8-24 hours' THEN 3
                    WHEN '1-3 days' THEN 4
                    ELSE 5
                END
        """

        resolution_dist = safe_query(resolution_dist_sql, "Failed to load resolution distribution")

        if not resolution_dist.empty:
            fig = px.pie(
                resolution_dist,
                values='INCIDENT_COUNT',
                names='RESOLUTION_TIME_BUCKET',
                title="Resolution Time Distribution",
                hole=0.4
            )
            st.info("Interactive chart not available in Snowflake - view data in table below")

    # Change success rate trend
    st.markdown("---")
    st.markdown("#### Change Management Success Rate")

    change_success_sql = f"""
        SELECT
            DATE_TRUNC('week', SCHEDULED_START) as WEEK,
            RISK_LEVEL,
            COUNT(*) as TOTAL_CHANGES,
            SUM(CASE WHEN STATE = 'Successful' THEN 1 ELSE 0 END) as SUCCESSFUL_CHANGES,
            ROUND(SUM(CASE WHEN STATE = 'Successful' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as SUCCESS_RATE
        FROM {get_table_name('DIM_SNOW_CHANGE', 'transformation')}
        WHERE SCHEDULED_START >= DATEADD(day, -{days}, CURRENT_DATE())
        GROUP BY WEEK, RISK_LEVEL
        ORDER BY WEEK
    """

    change_success = safe_query(change_success_sql, "Failed to load change success")

    if not change_success.empty:
        fig = px.line(
            change_success,
            x='WEEK',
            y='SUCCESS_RATE',
            color='RISK_LEVEL',
            title="Weekly Change Success Rate by Risk Level",
            markers=True
        )
        fig.add_hline(y=95, line_dash="dash", line_color="green", annotation_text="95% Target")
        st.info("Interactive chart not available in Snowflake - view data in table below")

    # Asset discovery trend
    st.markdown("---")
    st.markdown("#### CMDB Asset Discovery Trend")

    asset_discovery_sql = f"""
        SELECT
            DATE_TRUNC('day', LAST_DISCOVERED) as DISCOVERY_DATE,
            DEVICE_CLASS,
            COUNT(*) as ASSETS_DISCOVERED
        FROM {get_table_name('DIM_SNOW_DEVICE', 'transformation')}
        WHERE LAST_DISCOVERED >= DATEADD(day, -{days}, CURRENT_DATE())
          AND LAST_DISCOVERED IS NOT NULL
        GROUP BY DISCOVERY_DATE, DEVICE_CLASS
        ORDER BY DISCOVERY_DATE
    """

    asset_discovery = safe_query(asset_discovery_sql, "Failed to load asset discovery")

    if not asset_discovery.empty:
        fig = px.bar(
            asset_discovery,
            x='DISCOVERY_DATE',
            y='ASSETS_DISCOVERED',
            color='DEVICE_CLASS',
            title="Daily CMDB Asset Discovery",
            barmode='stack'
        )
        st.info("Interactive chart not available in Snowflake - view data in table below")
    else:
        st.info("No recent asset discovery data available")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("""
**Data Source:** ServiceNow ITSM Platform via Snowflake
**Refresh Rate:** 5-minute cache
**Contact:** GenericCorp Data Engineering Team
""")
