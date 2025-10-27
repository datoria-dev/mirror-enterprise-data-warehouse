"""
Proofpoint Email Security Dashboard

Email security monitoring dashboard for Proofpoint platform,
tracking email threats, phishing attempts, malware, and user behavior.
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
    page_title="CPR - Proofpoint Email Security",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply common styles
apply_common_styles()

# ============================================================================
# ENVIRONMENT VALIDATION
# ============================================================================

REQUIRED_OBJECTS = [
    get_table_name('L_PROOFPOINT_RAW', 'landing'),
    get_table_name('STG_PROOFPOINT_LOGS', 'landing')
]

validate_environment(REQUIRED_OBJECTS)
session = get_active_session()

# Set database context to avoid STAGE GET errors
try:
    session.sql("USE DATABASE DEV_REPORTING").collect()
    session.sql("USE SCHEMA SECURITY_ANALYTICS").collect()
except Exception as e:
    st.warning(f"Could not set database context: {e}")

# ============================================================================
# HEADER
# ============================================================================

create_header(
    title="Proofpoint Email Security",
    subtitle="Email Threat Detection & Protection Monitoring",
    icon="📧"
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
        index=1,
        help="Select time range for email analysis"
    )
    days = DATE_RANGES[date_range]

    threat_filter = st.multiselect(
        "Threat Type",
        ['Phishing', 'Malware', 'Spam', 'Impostor', 'Suspicious URL', 'Attachment'],
        default=['Phishing', 'Malware', 'Impostor'],
        help="Filter by email threat type"
    )

    action_filter = st.multiselect(
        "Action Taken",
        ['Quarantined', 'Blocked', 'Delivered', 'Deleted'],
        default=['Quarantined', 'Blocked'],
        help="Filter by action taken on email"
    )

    st.markdown("---")
    add_refresh_button()

    st.info("""
    **📊 Data Source:**
    Proofpoint Email Protection

    **📈 Metrics Tracked:**
    - Phishing detection rate
    - Malware blocked
    - Impostor email attempts
    - Suspicious URL clicks
    - User risk behavior
    - Email volume analysis
    """)

    show_last_refresh()

# ============================================================================
# MAIN CONTENT
# ============================================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview",
    "📧 Email Threats",
    "👥 User Risk Analysis",
    "📈 Trends",
    "🎣 Phishing Campaign Analysis",
    "⚡ Response Performance"
])

# ---------------------------------------------------------------------------
# TAB 1: OVERVIEW
# ---------------------------------------------------------------------------

with tab1:
    st.subheader("Email Security Overview")

    show_data_freshness(
        get_table_name('L_PROOFPOINT_RAW', 'landing'),
        timestamp_column='MESSAGE_TIME'
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_emails_sql = f"""
            SELECT COUNT(*) as TOTAL_EMAILS
            FROM {get_table_name('L_PROOFPOINT_RAW', 'landing')}
            WHERE MESSAGE_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
        """
        emails_data = safe_query(total_emails_sql, "Failed to load email count")

        if not emails_data.empty:
            st.metric(
                "Total Emails",
                f"{emails_data['TOTAL_EMAILS'].iloc[0]:,}",
                help="Total emails processed by Proofpoint"
            )

    with col2:
        threats_sql = f"""
            SELECT COUNT(*) as THREATS_DETECTED
            FROM {get_table_name('L_PROOFPOINT_RAW', 'landing')}
            WHERE MESSAGE_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
              AND THREAT_TYPE IS NOT NULL
        """
        threats_data = safe_query(threats_sql, "Failed to load threats")

        if not threats_data.empty:
            threats_count = threats_data['THREATS_DETECTED'].iloc[0]
            st.metric(
                "Threats Detected",
                f"{threats_count:,}",
                delta=f"🔴 {threats_count}",
                delta_color="inverse",
                help="Total email threats detected"
            )

    with col3:
        blocked_sql = f"""
            SELECT COUNT(*) as BLOCKED_EMAILS
            FROM {get_table_name('L_PROOFPOINT_RAW', 'landing')}
            WHERE MESSAGE_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
              AND RAW_DATA:action::STRING IN ('quarantined', 'blocked')
        """
        blocked_data = safe_query(blocked_sql, "Failed to load blocked emails")

        if not blocked_data.empty:
            blocked_count = blocked_data['BLOCKED_EMAILS'].iloc[0]
            st.metric(
                "Blocked/Quarantined",
                f"{blocked_count:,}",
                help="Emails blocked or quarantined"
            )

    with col4:
        phishing_sql = f"""
            SELECT COUNT(*) as PHISHING_ATTEMPTS
            FROM {get_table_name('L_PROOFPOINT_RAW', 'landing')}
            WHERE MESSAGE_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
              AND THREAT_TYPE LIKE '%phishing%'
        """
        phishing_data = safe_query(phishing_sql, "Failed to load phishing")

        if not phishing_data.empty:
            phishing_count = phishing_data['PHISHING_ATTEMPTS'].iloc[0]
            st.metric(
                "Phishing Attempts",
                f"{phishing_count:,}",
                delta=f"🎣 {phishing_count}",
                delta_color="inverse",
                help="Phishing emails detected"
            )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Threat Type Distribution")

        threat_dist_sql = f"""
            SELECT
                THREAT_TYPE,
                COUNT(*) as THREAT_COUNT
            FROM {get_table_name('L_PROOFPOINT_RAW', 'landing')}
            WHERE MESSAGE_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
              AND THREAT_TYPE IS NOT NULL
            GROUP BY THREAT_TYPE
            ORDER BY THREAT_COUNT DESC
            LIMIT 10
        """

        threat_dist = safe_query(threat_dist_sql, "Failed to load threat distribution")

        if not threat_dist.empty:
            fig = px.pie(threat_dist, values='THREAT_COUNT', names='THREAT_TYPE')
        else:
            st.info("No threat data available")

    with col2:
        st.subheader("Top Sender Domains (Threats)")

        sender_sql = f"""
            SELECT
                RAW_DATA:sender_domain::STRING as SENDER_DOMAIN,
                COUNT(*) as THREAT_COUNT
            FROM {get_table_name('L_PROOFPOINT_RAW', 'landing')}
            WHERE MESSAGE_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
              AND THREAT_TYPE IS NOT NULL
              AND RAW_DATA:sender_domain::STRING IS NOT NULL
            GROUP BY SENDER_DOMAIN
            ORDER BY THREAT_COUNT DESC
            LIMIT 10
        """

        sender_data = safe_query(sender_sql, "Failed to load sender domains")

        if not sender_data.empty:
            fig = px.bar(sender_data, x='THREAT_COUNT', y='SENDER_DOMAIN', orientation='h')
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})

    st.markdown("---")

    # Protection effectiveness
    st.subheader("Email Protection Effectiveness")

    effectiveness_sql = f"""
        SELECT
            CASE
                WHEN RAW_DATA:action::STRING IN ('quarantined', 'blocked') THEN 'Protected'
                WHEN RAW_DATA:action::STRING = 'delivered' AND THREAT_TYPE IS NULL THEN 'Clean Delivered'
                WHEN RAW_DATA:action::STRING = 'delivered' AND THREAT_TYPE IS NOT NULL THEN 'Threat Delivered'
                ELSE 'Other'
            END as OUTCOME,
            COUNT(*) as EMAIL_COUNT
        FROM {get_table_name('L_PROOFPOINT_RAW', 'landing')}
        WHERE MESSAGE_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
        GROUP BY OUTCOME
    """

    effectiveness_data = safe_query(effectiveness_sql, "Failed to load effectiveness data")

    if not effectiveness_data.empty:
        colors = {
            'Protected': '#27ae60',
            'Clean Delivered': '#3498db',
            'Threat Delivered': '#e74c3c',
            'Other': '#95a5a6'
        }
        fig = px.bar(effectiveness_data, x='OUTCOME', y='EMAIL_COUNT', color='OUTCOME', color_discrete_map=colors)

# ---------------------------------------------------------------------------
# TAB 2: EMAIL THREATS
# ---------------------------------------------------------------------------

with tab2:
    st.subheader("Detailed Email Threat Records")

    threat_filter_sql = "','".join(threat_filter) if threat_filter else ""
    threat_where = f"AND THREAT_TYPE IN ('{threat_filter_sql}')" if threat_filter_sql else "AND THREAT_TYPE IS NOT NULL"

    threats_detail_sql = f"""
        SELECT
            MESSAGE_TIME,
            SENDER,
            RECIPIENT,
            SUBJECT,
            THREAT_TYPE,
            RAW_DATA:action::STRING as ACTION_TAKEN,
            RAW_DATA:threat_score::NUMBER as THREAT_SCORE
        FROM {get_table_name('L_PROOFPOINT_RAW', 'landing')}
        WHERE MESSAGE_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
          {threat_where}
        ORDER BY MESSAGE_TIME DESC
        LIMIT 1000
    """

    threats_detail = query_with_metrics(threats_detail_sql, "Failed to load threat details")

    if not threats_detail.empty:
        search_term = st.text_input("🔍 Search threats (sender, recipient, subject)", "")

        if search_term:
            threats_detail = threats_detail[
                threats_detail.astype(str).apply(
                    lambda x: x.str.contains(search_term, case=False, na=False)
                ).any(axis=1)
            ]

        st.dataframe(threats_detail, use_container_width=True, height=500)
        # Download button
        @st.cache_data
        def convert_to_csv_0(df):
            return df.to_csv(index=False).encode('utf-8')

        csv_data = convert_to_csv_0(threats_detail)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name="proofpoint_data.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_proofpoint_1"
        )
        export_csv(threats_detail, "proofpoint_email_threats")
        st.caption(f"Showing {len(threats_detail):,} threat emails")
    else:
        st.info("✅ No email threats found matching selected filters")

# ---------------------------------------------------------------------------
# TAB 3: USER RISK ANALYSIS
# ---------------------------------------------------------------------------

with tab3:
    st.subheader("User Risk Behavior Analysis")

    # Top targeted users
    st.subheader("Most Targeted Recipients")

    targeted_sql = f"""
        SELECT
            RECIPIENT,
            COUNT(*) as THREAT_COUNT,
            COUNT(DISTINCT THREAT_TYPE) as UNIQUE_THREAT_TYPES
        FROM {get_table_name('L_PROOFPOINT_RAW', 'landing')}
        WHERE MESSAGE_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
          AND THREAT_TYPE IS NOT NULL
          AND RECIPIENT IS NOT NULL
        GROUP BY RECIPIENT
        ORDER BY THREAT_COUNT DESC
        LIMIT 20
    """

    targeted_data = safe_query(targeted_sql, "Failed to load targeted users")

    if not targeted_data.empty:
        st.dataframe(targeted_data, use_container_width=True, height=400)
        # Download button
        @st.cache_data
        def convert_to_csv_1(df):
            return df.to_csv(index=False).encode('utf-8')

        csv_data = convert_to_csv_1(targeted_data)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name="proofpoint_data.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_proofpoint_2"
        )
        export_csv(targeted_data, "proofpoint_targeted_users")

        st.markdown("---")

        # Visualization
        fig = px.bar(
            targeted_data.head(10),
            x='THREAT_COUNT',
            y='RECIPIENT',
            orientation='h',
            title="Top 10 Most Targeted Users",
            color='UNIQUE_THREAT_TYPES',
            color_continuous_scale='Reds'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})

# ---------------------------------------------------------------------------
# TAB 4: TRENDS
# ---------------------------------------------------------------------------

with tab4:
    st.subheader("Email Threat Trends Over Time")

    # Daily email volume and threats
    trend_sql = f"""
        SELECT
            DATE_TRUNC('day', MESSAGE_TIME) as DAY,
            COUNT(*) as TOTAL_EMAILS,
            SUM(CASE WHEN THREAT_TYPE IS NOT NULL THEN 1 ELSE 0 END) as THREATS,
            SUM(CASE WHEN RAW_DATA:action::STRING IN ('quarantined', 'blocked') THEN 1 ELSE 0 END) as BLOCKED
        FROM {get_table_name('L_PROOFPOINT_RAW', 'landing')}
        WHERE MESSAGE_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
        GROUP BY DAY
        ORDER BY DAY
    """

    trend_data = safe_query(trend_sql, "Failed to load trend data")

    if not trend_data.empty:
        # Reshape data for plotting
        trend_melted = trend_data.melt(id_vars=['DAY'], value_vars=['TOTAL_EMAILS', 'THREATS', 'BLOCKED'],
                                       var_name='METRIC', value_name='COUNT')

        fig = px.line(
            trend_melted,
            x='DAY',
            y='COUNT',
            color='METRIC',
            title="Daily Email Volume and Threat Detection",
            labels={'DAY': 'Date', 'COUNT': 'Count', 'METRIC': 'Metric'}
        )

    st.markdown("---")

    # Threat type trends
    st.subheader("Threat Type Trends")

    threat_trend_sql = f"""
        SELECT
            DATE_TRUNC('day', MESSAGE_TIME) as DAY,
            THREAT_TYPE,
            COUNT(*) as THREAT_COUNT
        FROM {get_table_name('L_PROOFPOINT_RAW', 'landing')}
        WHERE MESSAGE_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
          AND THREAT_TYPE IS NOT NULL
        GROUP BY DAY, THREAT_TYPE
        ORDER BY DAY
    """

    threat_trend = safe_query(threat_trend_sql, "Failed to load threat trend")

    if not threat_trend.empty:
        fig = px.area(
            threat_trend,
            x='DAY',
            y='THREAT_COUNT',
            color='THREAT_TYPE',
            title="Threat Types Over Time"
        )

# ---------------------------------------------------------------------------
# TAB 5: PHISHING CAMPAIGN ANALYSIS
# ---------------------------------------------------------------------------

with tab5:
    st.subheader("Phishing Campaign Detection & Analysis")

    # Phishing KPIs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        phishing_total_sql = f"""
            SELECT COUNT(*) as PHISHING_COUNT
            FROM {get_table_name('L_PROOFPOINT_RAW', 'landing')}
            WHERE MESSAGE_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
              AND THREAT_TYPE LIKE '%phishing%'
        """
        phishing_total = safe_query(phishing_total_sql, "Failed to load phishing count")

        if not phishing_total.empty:
            st.metric(
                "Total Phishing",
                f"{phishing_total['PHISHING_COUNT'].iloc[0]:,}",
                help="Total phishing attempts detected"
            )

    with col2:
        blocked_phishing_sql = f"""
            SELECT COUNT(*) as BLOCKED_PHISHING
            FROM {get_table_name('L_PROOFPOINT_RAW', 'landing')}
            WHERE MESSAGE_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
              AND THREAT_TYPE LIKE '%phishing%'
              AND RAW_DATA:action::STRING IN ('quarantined', 'blocked')
        """
        blocked_phishing = safe_query(blocked_phishing_sql, "Failed to load blocked phishing")

        if not blocked_phishing.empty:
            blocked_count = blocked_phishing['BLOCKED_PHISHING'].iloc[0]
            total_count = phishing_total['PHISHING_COUNT'].iloc[0] if not phishing_total.empty else 0
            block_rate = (blocked_count / total_count * 100) if total_count > 0 else 0
            st.metric(
                "Blocked Rate",
                f"{block_rate:.1f}%",
                help="Percentage of phishing emails blocked"
            )

    with col3:
        delivered_phishing_sql = f"""
            SELECT COUNT(*) as DELIVERED_PHISHING
            FROM {get_table_name('L_PROOFPOINT_RAW', 'landing')}
            WHERE MESSAGE_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
              AND THREAT_TYPE LIKE '%phishing%'
              AND RAW_DATA:action::STRING = 'delivered'
        """
        delivered_phishing = safe_query(delivered_phishing_sql, "Failed to load delivered phishing")

        if not delivered_phishing.empty:
            delivered_count = delivered_phishing['DELIVERED_PHISHING'].iloc[0]
            st.metric(
                "Delivered (Risk)",
                f"{delivered_count:,}",
                delta=f"🔴 {delivered_count}",
                delta_color="inverse",
                help="Phishing emails that were delivered to users"
            )

    with col4:
        url_clicks_sql = f"""
            SELECT COUNT(*) as URL_CLICKS
            FROM {get_table_name('STG_PROOFPOINT_LOGS', 'landing')}
            WHERE EVENT_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
              AND EVENT_TYPE = 'url_click'
              AND THREAT_TYPE LIKE '%phishing%'
        """
        url_clicks = safe_query(url_clicks_sql, "Failed to load URL clicks")

        if not url_clicks.empty:
            click_count = url_clicks['URL_CLICKS'].iloc[0]
            st.metric(
                "Malicious URL Clicks",
                f"{click_count:,}",
                delta=f"⚠️ {click_count}",
                delta_color="inverse",
                help="Users who clicked on malicious URLs"
            )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Phishing Campaign Sources")

        campaign_sources_sql = f"""
            SELECT
                RAW_DATA:sender_domain::STRING as DOMAIN,
                COUNT(*) as PHISHING_COUNT,
                COUNT(DISTINCT RECIPIENT) as TARGETED_USERS
            FROM {get_table_name('L_PROOFPOINT_RAW', 'landing')}
            WHERE MESSAGE_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
              AND THREAT_TYPE LIKE '%phishing%'
              AND RAW_DATA:sender_domain::STRING IS NOT NULL
            GROUP BY DOMAIN
            ORDER BY PHISHING_COUNT DESC
            LIMIT 15
        """

        campaign_sources = safe_query(campaign_sources_sql, "Failed to load campaign sources")

        if not campaign_sources.empty:
            fig = px.scatter(
                campaign_sources,
                x='PHISHING_COUNT',
                y='TARGETED_USERS',
                size='PHISHING_COUNT',
                text='DOMAIN',
                title="Phishing Campaign Volume vs Targeted Users",
                labels={'PHISHING_COUNT': 'Emails Sent', 'TARGETED_USERS': 'Users Targeted'}
            )

    with col2:
        st.markdown("#### Phishing Subject Keywords")

        keywords_sql = f"""
            SELECT
                CASE
                    WHEN LOWER(SUBJECT) LIKE '%urgent%' THEN 'Urgent'
                    WHEN LOWER(SUBJECT) LIKE '%password%' OR LOWER(SUBJECT) LIKE '%account%' THEN 'Password/Account'
                    WHEN LOWER(SUBJECT) LIKE '%invoice%' OR LOWER(SUBJECT) LIKE '%payment%' THEN 'Invoice/Payment'
                    WHEN LOWER(SUBJECT) LIKE '%suspended%' OR LOWER(SUBJECT) LIKE '%verify%' THEN 'Suspended/Verify'
                    WHEN LOWER(SUBJECT) LIKE '%security%' THEN 'Security'
                    ELSE 'Other'
                END as KEYWORD_CATEGORY,
                COUNT(*) as PHISHING_COUNT
            FROM {get_table_name('L_PROOFPOINT_RAW', 'landing')}
            WHERE MESSAGE_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
              AND THREAT_TYPE LIKE '%phishing%'
              AND SUBJECT IS NOT NULL
            GROUP BY KEYWORD_CATEGORY
            ORDER BY PHISHING_COUNT DESC
        """

        keywords_data = safe_query(keywords_sql, "Failed to load keywords")

        if not keywords_data.empty:
            fig = px.bar(
                keywords_data,
                x='KEYWORD_CATEGORY',
                y='PHISHING_COUNT',
                title="Common Phishing Subject Patterns",
                color='PHISHING_COUNT',
                color_continuous_scale='Reds'
            )

    # High-risk phishing campaigns
    st.markdown("---")
    st.markdown("#### Active Phishing Campaigns (High Risk)")

    campaigns_sql = f"""
        SELECT
            RAW_DATA:sender_domain::STRING as CAMPAIGN_SOURCE,
            COUNT(*) as EMAIL_COUNT,
            COUNT(DISTINCT RECIPIENT) as USERS_TARGETED,
            SUM(CASE WHEN RAW_DATA:action::STRING = 'delivered' THEN 1 ELSE 0 END) as DELIVERED_COUNT,
            MAX(MESSAGE_TIME) as LAST_SEEN
        FROM {get_table_name('L_PROOFPOINT_RAW', 'landing')}
        WHERE MESSAGE_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
          AND THREAT_TYPE LIKE '%phishing%'
          AND RAW_DATA:sender_domain::STRING IS NOT NULL
        GROUP BY CAMPAIGN_SOURCE
        HAVING COUNT(*) >= 5
        ORDER BY EMAIL_COUNT DESC
        LIMIT 25
    """

    campaigns_data = safe_query(campaigns_sql, "Failed to load campaigns")

    if not campaigns_data.empty:
        st.dataframe(
            campaigns_data.style,
            use_container_width=True
        )
        export_csv(campaigns_data, "proofpoint_phishing_campaigns")
    else:
        st.success("✅ No active phishing campaigns detected")

# ---------------------------------------------------------------------------
# TAB 6: RESPONSE PERFORMANCE
# ---------------------------------------------------------------------------

with tab6:
    st.subheader("Email Security Response Metrics")

    # Response time KPIs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        block_rate_sql = f"""
            SELECT
                ROUND(SUM(CASE WHEN RAW_DATA:action::STRING IN ('quarantined', 'blocked') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as BLOCK_RATE
            FROM {get_table_name('L_PROOFPOINT_RAW', 'landing')}
            WHERE MESSAGE_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
              AND THREAT_TYPE IS NOT NULL
        """
        block_rate = safe_query(block_rate_sql, "Failed to load block rate")

        if not block_rate.empty and block_rate['BLOCK_RATE'].iloc[0] is not None:
            rate = block_rate['BLOCK_RATE'].iloc[0]
            st.metric(
                "Threat Block Rate",
                f"{rate:.1f}%",
                delta=f"{rate - 95:+.1f}%",
                help="Percentage of threats blocked/quarantined"
            )

    with col2:
        false_positive_sql = f"""
            SELECT COUNT(*) as FALSE_POSITIVES
            FROM {get_table_name('L_PROOFPOINT_RAW', 'landing')}
            WHERE MESSAGE_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
              AND RAW_DATA:action::STRING IN ('quarantined', 'blocked')
              AND THREAT_TYPE IS NULL
        """
        false_positives = safe_query(false_positive_sql, "Failed to load false positives")

        if not false_positives.empty:
            fp_count = false_positives['FALSE_POSITIVES'].iloc[0]
            st.metric(
                "Potential False Positives",
                f"{fp_count:,}",
                help="Clean emails that were blocked/quarantined"
            )

    with col3:
        avg_detection_sql = f"""
            SELECT ROUND(AVG(RAW_DATA:detection_time_ms::NUMBER) / 1000, 2) as AVG_DETECTION_SEC
            FROM {get_table_name('L_PROOFPOINT_RAW', 'landing')}
            WHERE MESSAGE_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
              AND THREAT_TYPE IS NOT NULL
              AND RAW_DATA:detection_time_ms::NUMBER IS NOT NULL
        """
        avg_detection = safe_query(avg_detection_sql, "Failed to load detection time")

        if not avg_detection.empty and avg_detection['AVG_DETECTION_SEC'].iloc[0] is not None:
            st.metric(
                "Avg Detection Time",
                f"{avg_detection['AVG_DETECTION_SEC'].iloc[0]:.2f}s",
                help="Average time to detect threats"
            )

    with col4:
        malware_blocked_sql = f"""
            SELECT COUNT(*) as MALWARE_BLOCKED
            FROM {get_table_name('L_PROOFPOINT_RAW', 'landing')}
            WHERE MESSAGE_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
              AND THREAT_TYPE LIKE '%malware%'
              AND RAW_DATA:action::STRING IN ('quarantined', 'blocked')
        """
        malware_blocked = safe_query(malware_blocked_sql, "Failed to load malware blocked")

        if not malware_blocked.empty:
            st.metric(
                "Malware Blocked",
                f"{malware_blocked['MALWARE_BLOCKED'].iloc[0]:,}",
                help="Malware attachments blocked"
            )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Protection Effectiveness by Threat Type")

        effectiveness_by_type_sql = f"""
            SELECT
                THREAT_TYPE,
                COUNT(*) as TOTAL,
                SUM(CASE WHEN RAW_DATA:action::STRING IN ('quarantined', 'blocked') THEN 1 ELSE 0 END) as BLOCKED,
                ROUND(SUM(CASE WHEN RAW_DATA:action::STRING IN ('quarantined', 'blocked') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as BLOCK_RATE_PCT
            FROM {get_table_name('L_PROOFPOINT_RAW', 'landing')}
            WHERE MESSAGE_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
              AND THREAT_TYPE IS NOT NULL
            GROUP BY THREAT_TYPE
            ORDER BY TOTAL DESC
            LIMIT 10
        """

        effectiveness_by_type = safe_query(effectiveness_by_type_sql, "Failed to load effectiveness by type")

        if not effectiveness_by_type.empty:
            fig = px.bar(
                effectiveness_by_type,
                x='THREAT_TYPE',
                y='BLOCK_RATE_PCT',
                text='BLOCK_RATE_PCT',
                title="Block Rate % by Threat Type",
                color='BLOCK_RATE_PCT',
                color_continuous_scale='RdYlGn',
                range_color=[0, 100]
            )
            fig.add_hline(y=95, line_dash="dash", line_color="red", annotation_text="95% Target")

    with col2:
        st.markdown("#### User Click-Through Rate (High Risk)")

        click_through_sql = f"""
            SELECT
                DATE_TRUNC('day', MESSAGE_TIME) as DAY,
                COUNT(*) as PHISHING_DELIVERED,
                (SELECT COUNT(*)
                 FROM {get_table_name('STG_PROOFPOINT_LOGS', 'landing')} l
                 WHERE DATE_TRUNC('day', l.EVENT_TIME) = DATE_TRUNC('day', p.MESSAGE_TIME)
                   AND l.EVENT_TYPE = 'url_click'
                   AND l.THREAT_TYPE LIKE '%phishing%') as URL_CLICKS
            FROM {get_table_name('L_PROOFPOINT_RAW', 'landing')} p
            WHERE MESSAGE_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
              AND THREAT_TYPE LIKE '%phishing%'
              AND RAW_DATA:action::STRING = 'delivered'
            GROUP BY DAY
            ORDER BY DAY
        """

        click_through = safe_query(click_through_sql, "Failed to load click-through")

        if not click_through.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                name='Phishing Delivered',
                x=click_through['DAY'],
                y=click_through['PHISHING_DELIVERED'],
                mode='lines+markers',
                marker_color='#e67e22'
            ))
            fig.add_trace(go.Scatter(
                name='URL Clicks',
                x=click_through['DAY'],
                y=click_through['URL_CLICKS'],
                mode='lines+markers',
                marker_color='#e74c3c'
            ))
            fig.update_layout(
                title="Phishing Delivery vs User Click-Through",
                yaxis_title="Count"
            )

    # High-risk users
    st.markdown("---")
    st.markdown("#### High-Risk Users (URL Click Behavior)")

    high_risk_users_sql = f"""
        SELECT
            l.RECIPIENT as USER_EMAIL,
            COUNT(*) as URL_CLICKS,
            COUNT(DISTINCT DATE_TRUNC('day', l.EVENT_TIME)) as DAYS_WITH_CLICKS,
            MAX(l.EVENT_TIME) as LAST_CLICK
        FROM {get_table_name('STG_PROOFPOINT_LOGS', 'landing')} l
        WHERE l.EVENT_TIME >= DATEADD(day, -{days}, CURRENT_DATE())
          AND l.EVENT_TYPE = 'url_click'
          AND l.THREAT_TYPE LIKE '%phishing%'
        GROUP BY USER_EMAIL
        HAVING COUNT(*) >= 2
        ORDER BY URL_CLICKS DESC
        LIMIT 30
    """

    high_risk_users = safe_query(high_risk_users_sql, "Failed to load high-risk users")

    if not high_risk_users.empty:
        st.dataframe(
            high_risk_users.style,
            use_container_width=True
        )
        export_csv(high_risk_users, "proofpoint_high_risk_users")
        st.warning(f"⚠️ Found {len(high_risk_users)} users with multiple malicious URL clicks - consider security awareness training")
    else:
        st.success("✅ No high-risk user behavior detected")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("""
**Data Source:** Proofpoint Email Protection via Snowflake
**Refresh Rate:** 5-minute cache
**Contact:** GenericCorp Data Engineering Team
""")
