"""
SentinelOne EDR Dashboard

Endpoint Detection & Response monitoring dashboard for SentinelOne agents,
threats, and security events.
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
    page_title="SentinelOne EDR Dashboard",
    page_icon="🛡️",
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
    get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation'),
    get_table_name('DIM_SENTINEL_VERSIONS', 'transformation'),
    get_table_name('L_SENTINELONE_RAW', 'landing')
]

# Validate that all required objects exist
validate_environment(REQUIRED_OBJECTS)

# Get Snowflake session
session = get_active_session()

# ============================================================================
# HEADER
# ============================================================================

create_header(
    title="SentinelOne EDR Dashboard",
    subtitle="Endpoint Detection & Response Monitoring",
    icon="🛡️"
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
        index=1,  # Default to "Last 7 Days"
        help="Select time range for data analysis"
    )
    days = DATE_RANGES[date_range]

    # Severity filter
    severity_filter = st.multiselect(
        "Threat Severity",
        ['Critical', 'High', 'Medium', 'Low'],
        default=['Critical', 'High'],
        help="Filter by threat severity level"
    )

    # Agent version filter
    version_query = f"""
        SELECT DISTINCT AGENT_VERSION
        FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
        ORDER BY AGENT_VERSION DESC
        LIMIT 10
    """
    version_data = safe_query(version_query, "Failed to load versions")

    if not version_data.empty:
        all_versions = version_data['AGENT_VERSION'].tolist()
        version_filter = st.multiselect(
            "Agent Version",
            all_versions,
            default=all_versions[:3] if len(all_versions) > 0 else [],
            help="Filter by SentinelOne agent version"
        )
    else:
        version_filter = []

    st.markdown("---")

    # Refresh button
    add_refresh_button()

    # Info section
    st.info("""
    **📊 Data Source:**
    SentinelOne EDR Platform

    **📈 Metrics Tracked:**
    - Endpoint threats detected
    - Agent version compliance
    - Detection & response times
    - Endpoint protection status
    """)

    # Last refresh timestamp
    show_last_refresh()

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Tab layout
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview",
    "🔍 Threat Analysis",
    "💻 Endpoint Status",
    "📈 Trends",
    "🎯 Threat Hunting",
    "⚡ Remediation Tracking"
])

# ---------------------------------------------------------------------------
# TAB 1: OVERVIEW
# ---------------------------------------------------------------------------

with tab1:
    st.subheader("SentinelOne EDR Overview")

    # Data freshness indicator
    show_data_freshness(
        get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation'),
        timestamp_column='EVENT_TIMESTAMP'
    )

    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Total threats
        threats_sql = f"""
            SELECT COUNT(DISTINCT THREAT_ID) as TOTAL_THREATS
            FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
            WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
        """
        threats_data = safe_query(threats_sql, "Failed to load threats")

        if not threats_data.empty:
            st.metric(
                "Total Threats",
                f"{threats_data['TOTAL_THREATS'].iloc[0]:,}",
                help="Total threats detected by SentinelOne in selected period"
            )

    with col2:
        # Active endpoints
        endpoints_sql = f"""
            SELECT COUNT(DISTINCT ENDPOINT_ID) as ACTIVE_ENDPOINTS
            FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
            WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
        """
        endpoints_data = safe_query(endpoints_sql, "Failed to load endpoints")

        if not endpoints_data.empty:
            st.metric(
                "Active Endpoints",
                f"{endpoints_data['ACTIVE_ENDPOINTS'].iloc[0]:,}",
                help="Number of endpoints reporting to SentinelOne"
            )

    with col3:
        # Critical threats
        critical_sql = f"""
            SELECT COUNT(*) as CRITICAL_THREATS
            FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
            WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
              AND THREAT_SEVERITY = 'Critical'
        """
        critical_data = safe_query(critical_sql, "Failed to load critical threats")

        if not critical_data.empty:
            critical_count = critical_data['CRITICAL_THREATS'].iloc[0]
            st.metric(
                "Critical Threats",
                f"{critical_count:,}",
                delta=f"🔴 {critical_count}",
                delta_color="inverse",
                help="Critical severity threats requiring immediate attention"
            )

    with col4:
        # Agent compliance
        compliance_sql = f"""
            SELECT
                ROUND(
                    COUNT(DISTINCT CASE WHEN IS_LATEST_VERSION = TRUE THEN ENDPOINT_ID END) * 100.0 /
                    NULLIF(COUNT(DISTINCT ENDPOINT_ID), 0),
                    1
                ) as COMPLIANCE_PCT
            FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
            WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
        """
        compliance_data = safe_query(compliance_sql, "Failed to load compliance")

        if not compliance_data.empty and compliance_data['COMPLIANCE_PCT'].iloc[0] is not None:
            compliance_pct = compliance_data['COMPLIANCE_PCT'].iloc[0]
            st.metric(
                "Agent Compliance",
                f"{compliance_pct}%",
                delta=f"+{compliance_pct-90:.1f}%" if compliance_pct > 90 else f"{compliance_pct-90:.1f}%",
                help="Percentage of endpoints running latest agent version"
            )

    st.markdown("---")

    # Threat severity distribution
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Threat Severity Distribution")

        severity_sql = f"""
            SELECT
                THREAT_SEVERITY,
                COUNT(*) as THREAT_COUNT
            FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
            WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
              AND THREAT_SEVERITY IS NOT NULL
            GROUP BY THREAT_SEVERITY
            ORDER BY
                CASE THREAT_SEVERITY
                    WHEN 'Critical' THEN 1
                    WHEN 'High' THEN 2
                    WHEN 'Medium' THEN 3
                    WHEN 'Low' THEN 4
                    ELSE 5
                END
        """

        severity_data = safe_query(severity_sql, "Failed to load severity data")

        if not severity_data.empty:
            colors = {'Critical': '#e74c3c', 'High': '#e67e22', 'Medium': '#f39c12', 'Low': '#3498db'}
            fig = px.pie(
                severity_data,
                values='THREAT_COUNT',
                names='THREAT_SEVERITY',
                title="",
                color='THREAT_SEVERITY',
                color_discrete_map=colors
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top 10 Threat Types")

        threat_type_sql = f"""
            SELECT
                THREAT_TYPE,
                COUNT(*) as COUNT
            FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
            WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
              AND THREAT_TYPE IS NOT NULL
            GROUP BY THREAT_TYPE
            ORDER BY COUNT DESC
            LIMIT 10
        """

        threat_type_data = safe_query(threat_type_sql, "Failed to load threat types")

        if not threat_type_data.empty:
            fig = px.bar(
                threat_type_data,
                x='COUNT',
                y='THREAT_TYPE',
                orientation='h',
                title=""
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# TAB 2: THREAT ANALYSIS
# ---------------------------------------------------------------------------

with tab2:
    st.subheader("Detailed Threat Analysis")

    # Build severity filter for SQL
    severity_filter_sql = "','".join(severity_filter) if severity_filter else "'Critical','High','Medium','Low'"

    # Query threat details
    threats_detail_sql = f"""
        SELECT
            EVENT_TIMESTAMP,
            ENDPOINT_NAME,
            THREAT_TYPE,
            THREAT_SEVERITY,
            THREAT_STATUS,
            THREAT_CLASSIFICATION,
            FILE_PATH,
            MITIGATION_ACTION
        FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
        WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
          AND THREAT_SEVERITY IN ('{severity_filter_sql}')
        ORDER BY EVENT_TIMESTAMP DESC
        LIMIT 1000
    """

    threats_detail = query_with_metrics(threats_detail_sql, "Failed to load threat details")

    if not threats_detail.empty:
        # Add search box
        search_term = st.text_input("🔍 Search threats (endpoint, file path, type)", "")

        if search_term:
            threats_detail = threats_detail[
                threats_detail.astype(str).apply(
                    lambda x: x.str.contains(search_term, case=False, na=False)
                ).any(axis=1)
            ]

        # Display dataframe with color coding
        st.dataframe(
            threats_detail,
            use_container_width=True,
            height=500
        )

        # Export button
        export_csv(threats_detail, "sentinelone_threats")

        # Summary stats
        st.caption(f"Showing {len(threats_detail):,} threat events")
    else:
        st.info("✅ No threats detected in selected time period with current filters")

# ---------------------------------------------------------------------------
# TAB 3: ENDPOINT STATUS
# ---------------------------------------------------------------------------

with tab3:
    st.subheader("Endpoint Protection Status")

    # Agent version distribution
    st.subheader("Agent Version Distribution")

    version_dist_sql = f"""
        SELECT
            AGENT_VERSION,
            COUNT(DISTINCT ENDPOINT_ID) as ENDPOINT_COUNT,
            IS_LATEST_VERSION
        FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
        WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
        GROUP BY AGENT_VERSION, IS_LATEST_VERSION
        ORDER BY ENDPOINT_COUNT DESC
        LIMIT 15
    """

    version_dist = safe_query(version_dist_sql, "Failed to load version distribution")

    if not version_dist.empty:
        fig = px.bar(
            version_dist,
            x='AGENT_VERSION',
            y='ENDPOINT_COUNT',
            color='IS_LATEST_VERSION',
            title="Agent Versions Across Endpoints",
            labels={'AGENT_VERSION': 'Version', 'ENDPOINT_COUNT': 'Endpoints'},
            color_discrete_map={True: '#27ae60', False: '#e67e22'}
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Endpoint details table
    st.subheader("Endpoint Details")

    endpoint_sql = f"""
        SELECT
            ENDPOINT_NAME,
            AGENT_VERSION,
            OS_TYPE,
            LAST_SEEN,
            TOTAL_THREATS,
            PROTECTION_STATUS
        FROM (
            SELECT
                ENDPOINT_NAME,
                AGENT_VERSION,
                OS_TYPE,
                MAX(EVENT_TIMESTAMP) as LAST_SEEN,
                COUNT(DISTINCT THREAT_ID) as TOTAL_THREATS,
                MAX(PROTECTION_STATUS) as PROTECTION_STATUS,
                ROW_NUMBER() OVER (PARTITION BY ENDPOINT_NAME ORDER BY MAX(EVENT_TIMESTAMP) DESC) as rn
            FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
            WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
            GROUP BY ENDPOINT_NAME, AGENT_VERSION, OS_TYPE
        )
        WHERE rn = 1
        ORDER BY LAST_SEEN DESC
        LIMIT 500
    """

    endpoint_data = safe_query(endpoint_sql, "Failed to load endpoint data")

    if not endpoint_data.empty:
        st.dataframe(endpoint_data, use_container_width=True, height=400)
        export_csv(endpoint_data, "sentinelone_endpoints")
        st.caption(f"Showing {len(endpoint_data):,} endpoints")

# ---------------------------------------------------------------------------
# TAB 4: TRENDS
# ---------------------------------------------------------------------------

with tab4:
    st.subheader("Threat Trends Over Time")

    # Daily threat trend
    trend_sql = f"""
        SELECT
            DATE_TRUNC('day', EVENT_TIMESTAMP) as DAY,
            THREAT_SEVERITY,
            COUNT(*) as THREAT_COUNT
        FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
        WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
          AND THREAT_SEVERITY IS NOT NULL
        GROUP BY DAY, THREAT_SEVERITY
        ORDER BY DAY, THREAT_SEVERITY
    """

    trend_data = safe_query(trend_sql, "Failed to load trend data")

    if not trend_data.empty:
        fig = px.line(
            trend_data,
            x='DAY',
            y='THREAT_COUNT',
            color='THREAT_SEVERITY',
            title="Daily Threat Detections by Severity",
            labels={'DAY': 'Date', 'THREAT_COUNT': 'Threats', 'THREAT_SEVERITY': 'Severity'},
            color_discrete_map={'Critical': '#e74c3c', 'High': '#e67e22', 'Medium': '#f39c12', 'Low': '#3498db'}
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Mitigation action trends
    st.subheader("Mitigation Actions Over Time")

    mitigation_sql = f"""
        SELECT
            DATE_TRUNC('day', EVENT_TIMESTAMP) as DAY,
            MITIGATION_ACTION,
            COUNT(*) as ACTION_COUNT
        FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
        WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
          AND MITIGATION_ACTION IS NOT NULL
        GROUP BY DAY, MITIGATION_ACTION
        ORDER BY DAY
    """

    mitigation_data = safe_query(mitigation_sql, "Failed to load mitigation data")

    if not mitigation_data.empty:
        fig = px.area(
            mitigation_data,
            x='DAY',
            y='ACTION_COUNT',
            color='MITIGATION_ACTION',
            title="Automated Mitigation Actions",
            labels={'DAY': 'Date', 'ACTION_COUNT': 'Actions'}
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# TAB 5: THREAT HUNTING
# ---------------------------------------------------------------------------

with tab5:
    st.subheader("Threat Hunting & Investigation")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        ioc_sql = f"""
            SELECT COUNT(DISTINCT IOC_HASH) as IOC_COUNT
            FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
            WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
              AND IOC_HASH IS NOT NULL
        """
        ioc_data = safe_query(ioc_sql, "Failed to load IOCs")
        if not ioc_data.empty:
            st.metric("Unique IOCs", f"{ioc_data['IOC_COUNT'].iloc[0]:,}")

    with col2:
        process_sql = f"""
            SELECT COUNT(DISTINCT PROCESS_NAME) as PROCESS_COUNT
            FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
            WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
              AND THREAT_ID IS NOT NULL
        """
        process_data = safe_query(process_sql, "Failed to load processes")
        if not process_data.empty:
            st.metric("Malicious Processes", f"{process_data['PROCESS_COUNT'].iloc[0]:,}")

    with col3:
        lateral_sql = f"""
            SELECT COUNT(*) as LATERAL_MOVEMENT
            FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
            WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
              AND THREAT_CATEGORY = 'Lateral Movement'
        """
        lateral_data = safe_query(lateral_sql, "Failed to load lateral movement")
        if not lateral_data.empty:
            st.metric("Lateral Movement", f"{lateral_data['LATERAL_MOVEMENT'].iloc[0]:,}",
                     delta=f"⚠️ {lateral_data['LATERAL_MOVEMENT'].iloc[0]}", delta_color="inverse")

    with col4:
        persistence_sql = f"""
            SELECT COUNT(*) as PERSISTENCE_ATTEMPTS
            FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
            WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
              AND THREAT_CATEGORY = 'Persistence'
        """
        persistence_data = safe_query(persistence_sql, "Failed to load persistence")
        if not persistence_data.empty:
            st.metric("Persistence Attempts", f"{persistence_data['PERSISTENCE_ATTEMPTS'].iloc[0]:,}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Threat Classification (MITRE ATT&CK)")
        mitre_sql = f"""
            SELECT MITRE_TACTIC, COUNT(*) as THREAT_COUNT
            FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
            WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
              AND MITRE_TACTIC IS NOT NULL
            GROUP BY MITRE_TACTIC
            ORDER BY THREAT_COUNT DESC
            LIMIT 10
        """
        mitre_data = safe_query(mitre_sql, "Failed to load MITRE tactics")
        if not mitre_data.empty:
            fig = px.bar(mitre_data, x='THREAT_COUNT', y='MITRE_TACTIC', orientation='h',
                        color='THREAT_COUNT', color_continuous_scale='Reds')
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Attack Progression Timeline")
        attack_chain_sql = f"""
            SELECT THREAT_ID, MIN(EVENT_TIMESTAMP) as FIRST_SEEN, MAX(EVENT_TIMESTAMP) as LAST_SEEN,
                   COUNT(DISTINCT ENDPOINT_ID) as AFFECTED_ENDPOINTS,
                   DATEDIFF(minute, MIN(EVENT_TIMESTAMP), MAX(EVENT_TIMESTAMP)) as DURATION_MINUTES
            FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
            WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
              AND THREAT_ID IS NOT NULL
            GROUP BY THREAT_ID
            HAVING COUNT(DISTINCT ENDPOINT_ID) >= 2
            ORDER BY AFFECTED_ENDPOINTS DESC
            LIMIT 10
        """
        attack_chain = safe_query(attack_chain_sql, "Failed to load attack chains")
        if not attack_chain.empty:
            st.dataframe(attack_chain.style.background_gradient(subset=['AFFECTED_ENDPOINTS'], cmap='Reds'),
                        use_container_width=True)
            export_csv(attack_chain, "sentinelone_attack_chains")

    st.markdown("---")
    st.markdown("#### Suspicious Process Execution")

    suspicious_processes_sql = f"""
        SELECT PROCESS_NAME, COUNT(*) as EXECUTION_COUNT, COUNT(DISTINCT ENDPOINT_ID) as ENDPOINT_COUNT,
               MAX(EVENT_TIMESTAMP) as LAST_SEEN
        FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
        WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
          AND THREAT_ID IS NOT NULL
        GROUP BY PROCESS_NAME
        ORDER BY EXECUTION_COUNT DESC
        LIMIT 20
    """
    suspicious_processes = safe_query(suspicious_processes_sql, "Failed to load suspicious processes")
    if not suspicious_processes.empty:
        st.dataframe(suspicious_processes, use_container_width=True)
        export_csv(suspicious_processes, "sentinelone_suspicious_processes")

# ---------------------------------------------------------------------------
# TAB 6: REMEDIATION TRACKING
# ---------------------------------------------------------------------------

with tab6:
    st.subheader("Remediation & Response Performance")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        auto_remediation_sql = f"""
            SELECT ROUND(SUM(CASE WHEN IS_AUTO_REMEDIATED = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as AUTO_RATE
            FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
            WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
              AND THREAT_ID IS NOT NULL
        """
        auto_data = safe_query(auto_remediation_sql, "Failed to load auto remediation")
        if not auto_data.empty and auto_data['AUTO_RATE'].iloc[0]:
            st.metric("Auto-Remediation Rate", f"{auto_data['AUTO_RATE'].iloc[0]:.1f}%")

    with col2:
        avg_response_sql = f"""
            SELECT ROUND(AVG(DATEDIFF(minute, EVENT_TIMESTAMP, REMEDIATION_TIMESTAMP)), 1) as AVG_RESPONSE_MIN
            FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
            WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
              AND REMEDIATION_TIMESTAMP IS NOT NULL
        """
        response_data = safe_query(avg_response_sql, "Failed to load response time")
        if not response_data.empty and response_data['AVG_RESPONSE_MIN'].iloc[0]:
            st.metric("Avg Response Time", f"{response_data['AVG_RESPONSE_MIN'].iloc[0]:.1f} min")

    with col3:
        quarantined_sql = f"""
            SELECT COUNT(*) as QUARANTINED_COUNT
            FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
            WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
              AND MITIGATION_ACTION = 'quarantine'
        """
        quarantined_data = safe_query(quarantined_sql, "Failed to load quarantined")
        if not quarantined_data.empty:
            st.metric("Endpoints Quarantined", f"{quarantined_data['QUARANTINED_COUNT'].iloc[0]:,}")

    with col4:
        rollback_sql = f"""
            SELECT COUNT(*) as ROLLBACK_COUNT
            FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
            WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
              AND MITIGATION_ACTION = 'rollback'
        """
        rollback_data = safe_query(rollback_sql, "Failed to load rollbacks")
        if not rollback_data.empty:
            st.metric("Rollbacks Performed", f"{rollback_data['ROLLBACK_COUNT'].iloc[0]:,}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Remediation Success Rate by Action Type")
        success_rate_sql = f"""
            SELECT MITIGATION_ACTION, COUNT(*) as TOTAL,
                   SUM(CASE WHEN REMEDIATION_STATUS = 'success' THEN 1 ELSE 0 END) as SUCCESSFUL,
                   ROUND(SUM(CASE WHEN REMEDIATION_STATUS = 'success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as SUCCESS_RATE
            FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
            WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
              AND MITIGATION_ACTION IS NOT NULL
            GROUP BY MITIGATION_ACTION
            ORDER BY TOTAL DESC
        """
        success_rate = safe_query(success_rate_sql, "Failed to load success rates")
        if not success_rate.empty:
            fig = px.bar(success_rate, x='MITIGATION_ACTION', y='SUCCESS_RATE', text='SUCCESS_RATE',
                        color='SUCCESS_RATE', color_continuous_scale='RdYlGn', range_color=[0,100])
            fig.add_hline(y=95, line_dash="dash", line_color="red", annotation_text="95% Target")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Response Time Distribution")
        response_dist_sql = f"""
            SELECT
                CASE
                    WHEN DATEDIFF(minute, EVENT_TIMESTAMP, REMEDIATION_TIMESTAMP) <= 5 THEN '0-5 min'
                    WHEN DATEDIFF(minute, EVENT_TIMESTAMP, REMEDIATION_TIMESTAMP) <= 15 THEN '5-15 min'
                    WHEN DATEDIFF(minute, EVENT_TIMESTAMP, REMEDIATION_TIMESTAMP) <= 60 THEN '15-60 min'
                    ELSE '60+ min'
                END as TIME_BUCKET,
                COUNT(*) as THREAT_COUNT
            FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
            WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
              AND REMEDIATION_TIMESTAMP IS NOT NULL
            GROUP BY TIME_BUCKET
        """
        response_dist = safe_query(response_dist_sql, "Failed to load response distribution")
        if not response_dist.empty:
            fig = px.pie(response_dist, values='THREAT_COUNT', names='TIME_BUCKET',
                        title="Remediation Response Time", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Pending Remediation Actions")

    pending_sql = f"""
        SELECT ENDPOINT_NAME, THREAT_NAME, EVENT_TIMESTAMP, SEVERITY,
               DATEDIFF(hour, EVENT_TIMESTAMP, CURRENT_TIMESTAMP()) as HOURS_PENDING,
               RECOMMENDED_ACTION
        FROM {get_table_name('FACT_SENTINEL_ENDPOINTS', 'transformation')}
        WHERE REMEDIATION_STATUS IS NULL OR REMEDIATION_STATUS = 'pending'
          AND EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
        ORDER BY SEVERITY DESC, HOURS_PENDING DESC
        LIMIT 30
    """
    pending_data = safe_query(pending_sql, "Failed to load pending remediations")
    if not pending_data.empty:
        st.dataframe(pending_data.style.background_gradient(subset=['HOURS_PENDING'], cmap='Reds'),
                    use_container_width=True)
        export_csv(pending_data, "sentinelone_pending_remediation")
        st.warning(f"⚠️ {len(pending_data)} threats awaiting manual remediation")
    else:
        st.success("✅ No pending remediation actions")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("""
**Data Source:** SentinelOne EDR Platform via Snowflake
**Refresh Rate:** 5-minute cache
**Contact:** GenericCorp Data Engineering Team
""")
