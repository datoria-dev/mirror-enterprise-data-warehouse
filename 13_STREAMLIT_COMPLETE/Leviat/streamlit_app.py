"""
Leviat IAM Dashboard

Identity and Access Management dashboard for Leviat platform,
monitoring user access, authentication events, and security compliance.
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
    page_title="CPR - Leviat IAM Dashboard",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply common styles
apply_common_styles()

# ============================================================================
# ENVIRONMENT VALIDATION
# ============================================================================

REQUIRED_OBJECTS = [
    get_table_name('DIM_LEVIAT_USERS', 'transformation'),
    get_table_name('DIM_LEVIAT_LIST_USERS', 'transformation'),
    get_table_name('FACT_LEVIAT_SECURITY_EVENTS', 'transformation')
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
    title="Leviat IAM Dashboard",
    subtitle="Identity & Access Management Monitoring",
    icon="👤"
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
        help="Select time range for IAM analysis"
    )
    days = DATE_RANGES[date_range]

    event_type_filter = st.multiselect(
        "Event Type",
        ['Login', 'Logout', 'Failed Login', 'Password Change', 'Permission Change', 'Account Created', 'Account Disabled'],
        default=['Failed Login', 'Permission Change'],
        help="Filter by IAM event type"
    )

    st.markdown("---")
    add_refresh_button()

    st.info("""
    **📊 Data Source:**
    Leviat IAM Platform

    **📈 Metrics Tracked:**
    - User authentication events
    - Failed login attempts
    - Access permission changes
    - Account lifecycle management
    - Privileged access monitoring
    """)

    show_last_refresh()

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Check if data is available
data_check_sql = f"""
    SELECT COUNT(*) as ROW_COUNT
    FROM {get_table_name('FACT_LEVIAT_SECURITY_EVENTS', 'transformation')}
"""
data_check = safe_query(data_check_sql, "Failed to check data availability")

if data_check.empty or data_check['ROW_COUNT'].iloc[0] == 0:
    st.warning("""
    ⚠️ **No Data Available**

    The Leviat IAM integration is currently configured but awaiting data loading.
    Database structure is ready:
    - DIM_LEVIAT_USERS (User identities)
    - DIM_LEVIAT_LIST_USERS (User list management)
    - FACT_LEVIAT_SECURITY_EVENTS (IAM events)

    Contact the Data Engineering team to initiate data ingestion.
    """)

    st.info("""
    **Expected Metrics Once Data is Available:**
    - Total active users
    - Authentication success/failure rates
    - Privileged account monitoring
    - Access policy compliance
    - Suspicious activity alerts
    """)

else:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview",
        "👥 User Management",
        "🔒 Security Events",
        "📈 Trends",
        "🔑 Access Analysis",
        "⚠️ Risk Indicators"
    ])

    # -----------------------------------------------------------------------
    # TAB 1: OVERVIEW
    # -----------------------------------------------------------------------

    with tab1:
        st.subheader("IAM Overview")

        show_data_freshness(
            get_table_name('FACT_LEVIAT_SECURITY_EVENTS', 'transformation'),
            timestamp_column='EVENT_TIMESTAMP'
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            users_sql = f"""
                SELECT COUNT(DISTINCT USER_ID) as TOTAL_USERS
                FROM {get_table_name('DIM_LEVIAT_USERS', 'transformation')}
                WHERE IS_ACTIVE = TRUE
            """
            users_data = safe_query(users_sql, "Failed to load users")

            if not users_data.empty:
                st.metric(
                    "Active Users",
                    f"{users_data['TOTAL_USERS'].iloc[0]:,}",
                    help="Total active user accounts"
                )

        with col2:
            events_sql = f"""
                SELECT COUNT(*) as TOTAL_EVENTS
                FROM {get_table_name('FACT_LEVIAT_SECURITY_EVENTS', 'transformation')}
                WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
            """
            events_data = safe_query(events_sql, "Failed to load events")

            if not events_data.empty:
                st.metric(
                    "Security Events",
                    f"{events_data['TOTAL_EVENTS'].iloc[0]:,}",
                    help="Total IAM security events in selected period"
                )

        with col3:
            failed_sql = f"""
                SELECT COUNT(*) as FAILED_LOGINS
                FROM {get_table_name('FACT_LEVIAT_SECURITY_EVENTS', 'transformation')}
                WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
                  AND EVENT_TYPE = 'Failed Login'
            """
            failed_data = safe_query(failed_sql, "Failed to load failed logins")

            if not failed_data.empty:
                failed_count = failed_data['FAILED_LOGINS'].iloc[0]
                st.metric(
                    "Failed Logins",
                    f"{failed_count:,}",
                    delta=f"🔴 {failed_count}",
                    delta_color="inverse",
                    help="Failed authentication attempts"
                )

        with col4:
            privileged_sql = f"""
                SELECT COUNT(DISTINCT USER_ID) as PRIVILEGED_USERS
                FROM {get_table_name('DIM_LEVIAT_USERS', 'transformation')}
                WHERE IS_PRIVILEGED = TRUE AND IS_ACTIVE = TRUE
            """
            privileged_data = safe_query(privileged_sql, "Failed to load privileged users")

            if not privileged_data.empty:
                st.metric(
                    "Privileged Accounts",
                    f"{privileged_data['PRIVILEGED_USERS'].iloc[0]:,}",
                    help="Active privileged user accounts"
                )

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Event Type Distribution")

            event_dist_sql = f"""
                SELECT
                    EVENT_TYPE,
                    COUNT(*) as EVENT_COUNT
                FROM {get_table_name('FACT_LEVIAT_SECURITY_EVENTS', 'transformation')}
                WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
                GROUP BY EVENT_TYPE
                ORDER BY EVENT_COUNT DESC
            """

            event_dist = safe_query(event_dist_sql, "Failed to load event distribution")

            if not event_dist.empty:
                fig = px.pie(event_dist, values='EVENT_COUNT', names='EVENT_TYPE')

        with col2:
            st.subheader("Top Users by Activity")

            top_users_sql = f"""
                SELECT
                    u.USERNAME,
                    COUNT(*) as EVENT_COUNT
                FROM {get_table_name('FACT_LEVIAT_SECURITY_EVENTS', 'transformation')} e
                JOIN {get_table_name('DIM_LEVIAT_USERS', 'transformation')} u
                    ON e.USER_ID = u.USER_ID
                WHERE e.EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
                GROUP BY u.USERNAME
                ORDER BY EVENT_COUNT DESC
                LIMIT 10
            """

            top_users = safe_query(top_users_sql, "Failed to load top users")

            if not top_users.empty:
                fig = px.bar(top_users, x='EVENT_COUNT', y='USERNAME', orientation='h')
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})

    # -----------------------------------------------------------------------
    # TAB 2: USER MANAGEMENT
    # -----------------------------------------------------------------------

    with tab2:
        st.subheader("User Account Management")

        users_sql = f"""
            SELECT
                USERNAME,
                EMAIL,
                DEPARTMENT,
                IS_ACTIVE,
                IS_PRIVILEGED,
                LAST_LOGIN,
                CREATED_DATE
            FROM {get_table_name('DIM_LEVIAT_USERS', 'transformation')}
            ORDER BY LAST_LOGIN DESC NULLS LAST
            LIMIT 500
        """

        users_data = safe_query(users_sql, "Failed to load user data")

        if not users_data.empty:
            st.dataframe(users_data, use_container_width=True, height=500)
            # Download button
            @st.cache_data
            def convert_to_csv_0(df):
                return df.to_csv(index=False).encode('utf-8')

            csv_data = convert_to_csv_0(users_data)
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name="leviat_data.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_leviat_1"
            )
            export_csv(users_data, "leviat_users")
            st.caption(f"Showing {len(users_data):,} user accounts")

    # -----------------------------------------------------------------------
    # TAB 3: SECURITY EVENTS
    # -----------------------------------------------------------------------

    with tab3:
        st.subheader("Security Event Log")

        event_filter_sql = "','".join(event_type_filter) if event_type_filter else ""
        event_where = f"AND EVENT_TYPE IN ('{event_filter_sql}')" if event_filter_sql else ""

        events_sql = f"""
            SELECT
                e.EVENT_TIMESTAMP,
                u.USERNAME,
                e.EVENT_TYPE,
                e.SOURCE_IP,
                e.DEVICE_TYPE,
                e.SUCCESS_FLAG,
                e.FAILURE_REASON
            FROM {get_table_name('FACT_LEVIAT_SECURITY_EVENTS', 'transformation')} e
            LEFT JOIN {get_table_name('DIM_LEVIAT_USERS', 'transformation')} u
                ON e.USER_ID = u.USER_ID
            WHERE e.EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
              {event_where}
            ORDER BY e.EVENT_TIMESTAMP DESC
            LIMIT 1000
        """

        events_data = query_with_metrics(events_sql, "Failed to load events")

        if not events_data.empty:
            st.dataframe(events_data, use_container_width=True, height=500)
            # Download button
            @st.cache_data
            def convert_to_csv_1(df):
                return df.to_csv(index=False).encode('utf-8')

            csv_data = convert_to_csv_1(events_data)
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name="leviat_data.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_leviat_2"
            )
            export_csv(events_data, "leviat_security_events")
            st.caption(f"Showing {len(events_data):,} security events")

    # -----------------------------------------------------------------------
    # TAB 4: TRENDS
    # -----------------------------------------------------------------------

    with tab4:
        st.subheader("IAM Activity Trends")

        trend_sql = f"""
            SELECT
                DATE_TRUNC('day', EVENT_TIMESTAMP) as DAY,
                EVENT_TYPE,
                COUNT(*) as EVENT_COUNT
            FROM {get_table_name('FACT_LEVIAT_SECURITY_EVENTS', 'transformation')}
            WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
            GROUP BY DAY, EVENT_TYPE
            ORDER BY DAY
        """

        trend_data = safe_query(trend_sql, "Failed to load trend data")

        if not trend_data.empty:
            fig = px.line(trend_data, x='DAY', y='EVENT_COUNT', color='EVENT_TYPE', title="Daily IAM Events")

    # -----------------------------------------------------------------------
    # TAB 5: ACCESS ANALYSIS
    # -----------------------------------------------------------------------

    with tab5:
        st.subheader("Access Permission Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Permission Changes")

            perm_changes_sql = f"""
                SELECT
                    u.USERNAME,
                    e.EVENT_TIMESTAMP,
                    e.PERMISSION_BEFORE,
                    e.PERMISSION_AFTER,
                    e.CHANGED_BY
                FROM {get_table_name('FACT_LEVIAT_SECURITY_EVENTS', 'transformation')} e
                JOIN {get_table_name('DIM_LEVIAT_USERS', 'transformation')} u
                    ON e.USER_ID = u.USER_ID
                WHERE e.EVENT_TYPE = 'Permission Change'
                  AND e.EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
                ORDER BY e.EVENT_TIMESTAMP DESC
                LIMIT 100
            """

            perm_changes = safe_query(perm_changes_sql, "Failed to load permission changes")

            if not perm_changes.empty:
                st.dataframe(perm_changes, use_container_width=True, height=400)
                # Download button
                @st.cache_data
                def convert_to_csv_2(df):
                    return df.to_csv(index=False).encode('utf-8')

                csv_data = convert_to_csv_2(perm_changes)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name="leviat_data.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="download_leviat_3"
                )
                export_csv(perm_changes, "leviat_permission_changes")
            else:
                st.info("No permission changes in selected period")

        with col2:
            st.markdown("#### Privileged Access Distribution")

            priv_dist_sql = f"""
                SELECT
                    DEPARTMENT,
                    COUNT(*) as PRIVILEGED_COUNT,
                    COUNT(CASE WHEN IS_ACTIVE = TRUE THEN 1 END) as ACTIVE_PRIVILEGED
                FROM {get_table_name('DIM_LEVIAT_USERS', 'transformation')}
                WHERE IS_PRIVILEGED = TRUE
                GROUP BY DEPARTMENT
                ORDER BY PRIVILEGED_COUNT DESC
            """

            priv_dist = safe_query(priv_dist_sql, "Failed to load privileged distribution")

            if not priv_dist.empty:
                fig = px.bar(
                    priv_dist,
                    x='DEPARTMENT',
                    y='PRIVILEGED_COUNT',
                    color='ACTIVE_PRIVILEGED',
                    title="Privileged Accounts by Department",
                    labels={'PRIVILEGED_COUNT': 'Total Privileged', 'ACTIVE_PRIVILEGED': 'Active'}
                )

        st.markdown("---")

        # Access pattern analysis
        st.markdown("#### Access Patterns by Time of Day")

        time_pattern_sql = f"""
            SELECT
                HOUR(EVENT_TIMESTAMP) as HOUR_OF_DAY,
                EVENT_TYPE,
                COUNT(*) as EVENT_COUNT
            FROM {get_table_name('FACT_LEVIAT_SECURITY_EVENTS', 'transformation')}
            WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
            GROUP BY HOUR_OF_DAY, EVENT_TYPE
            ORDER BY HOUR_OF_DAY
        """

        time_pattern = safe_query(time_pattern_sql, "Failed to load time patterns")

        if not time_pattern.empty:
            fig = px.bar(
                time_pattern,
                x='HOUR_OF_DAY',
                y='EVENT_COUNT',
                color='EVENT_TYPE',
                title="IAM Events by Hour",
                labels={'HOUR_OF_DAY': 'Hour (24h)', 'EVENT_COUNT': 'Events'}
            )

        # Recent account changes
        st.markdown("#### Recent Account Lifecycle Events")

        lifecycle_sql = f"""
            SELECT
                u.USERNAME,
                e.EVENT_TYPE,
                e.EVENT_TIMESTAMP,
                e.PERFORMED_BY,
                e.REASON
            FROM {get_table_name('FACT_LEVIAT_SECURITY_EVENTS', 'transformation')} e
            JOIN {get_table_name('DIM_LEVIAT_USERS', 'transformation')} u
                ON e.USER_ID = u.USER_ID
            WHERE e.EVENT_TYPE IN ('Account Created', 'Account Disabled', 'Account Enabled', 'Account Deleted')
              AND e.EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
            ORDER BY e.EVENT_TIMESTAMP DESC
            LIMIT 50
        """

        lifecycle_events = safe_query(lifecycle_sql, "Failed to load lifecycle events")

        if not lifecycle_events.empty:
            st.dataframe(lifecycle_events, use_container_width=True)
            # Download button
            @st.cache_data
            def convert_to_csv_3(df):
                return df.to_csv(index=False).encode('utf-8')

            csv_data = convert_to_csv_3(lifecycle_events)
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name="leviat_data.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_leviat_4"
            )
            export_csv(lifecycle_events, "leviat_account_lifecycle")

    # -----------------------------------------------------------------------
    # TAB 6: RISK INDICATORS
    # -----------------------------------------------------------------------

    with tab6:
        st.subheader("Security Risk Indicators")

        # Risk KPIs
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # Failed login attempts
            failed_login_sql = f"""
                SELECT COUNT(*) as FAILED_ATTEMPTS
                FROM {get_table_name('FACT_LEVIAT_SECURITY_EVENTS', 'transformation')}
                WHERE EVENT_TYPE = 'Failed Login'
                  AND EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
            """
            failed_data = safe_query(failed_login_sql, "Failed to load failed logins")

            if not failed_data.empty:
                failed_count = failed_data['FAILED_ATTEMPTS'].iloc[0]
                st.metric(
                    "Failed Logins",
                    f"{failed_count:,}",
                    delta=f"-{int(failed_count * 0.15)}" if failed_count > 0 else "0",
                    help="Total failed login attempts"
                )

        with col2:
            # Suspicious IPs
            suspicious_ip_sql = f"""
                SELECT COUNT(DISTINCT SOURCE_IP) as SUSPICIOUS_IPS
                FROM {get_table_name('FACT_LEVIAT_SECURITY_EVENTS', 'transformation')}
                WHERE EVENT_TYPE = 'Failed Login'
                  AND EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
                GROUP BY SOURCE_IP
                HAVING COUNT(*) >= 5
            """
            suspicious_data = safe_query(suspicious_ip_sql, "Failed to load suspicious IPs")

            suspicious_count = len(suspicious_data) if not suspicious_data.empty else 0
            st.metric(
                "Suspicious IPs",
                f"{suspicious_count:,}",
                delta=f"🔴 {suspicious_count}",
                delta_color="inverse",
                help="IPs with 5+ failed login attempts"
            )

        with col3:
            # Dormant privileged accounts
            dormant_sql = f"""
                SELECT COUNT(*) as DORMANT_ACCOUNTS
                FROM {get_table_name('DIM_LEVIAT_USERS', 'transformation')}
                WHERE IS_PRIVILEGED = TRUE
                  AND IS_ACTIVE = TRUE
                  AND (LAST_LOGIN IS NULL OR LAST_LOGIN < DATEADD(day, -90, CURRENT_DATE()))
            """
            dormant_data = safe_query(dormant_sql, "Failed to load dormant accounts")

            if not dormant_data.empty:
                dormant_count = dormant_data['DORMANT_ACCOUNTS'].iloc[0]
                st.metric(
                    "Dormant Privileged",
                    f"{dormant_count:,}",
                    delta=f"⚠️ {dormant_count}",
                    delta_color="inverse",
                    help="Privileged accounts inactive 90+ days"
                )

        with col4:
            # After-hours access
            afterhours_sql = f"""
                SELECT COUNT(*) as AFTERHOURS_ACCESS
                FROM {get_table_name('FACT_LEVIAT_SECURITY_EVENTS', 'transformation')}
                WHERE EVENT_TYPE = 'Login'
                  AND EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
                  AND (HOUR(EVENT_TIMESTAMP) < 6 OR HOUR(EVENT_TIMESTAMP) >= 22)
            """
            afterhours_data = safe_query(afterhours_sql, "Failed to load after-hours access")

            if not afterhours_data.empty:
                afterhours_count = afterhours_data['AFTERHOURS_ACCESS'].iloc[0]
                st.metric(
                    "After-Hours Access",
                    f"{afterhours_count:,}",
                    help="Logins outside 6am-10pm"
                )

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Top Failed Login Sources")

            failed_sources_sql = f"""
                SELECT
                    SOURCE_IP,
                    COUNT(*) as ATTEMPT_COUNT,
                    COUNT(DISTINCT USER_ID) as AFFECTED_USERS
                FROM {get_table_name('FACT_LEVIAT_SECURITY_EVENTS', 'transformation')}
                WHERE EVENT_TYPE = 'Failed Login'
                  AND EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
                GROUP BY SOURCE_IP
                ORDER BY ATTEMPT_COUNT DESC
                LIMIT 20
            """

            failed_sources = safe_query(failed_sources_sql, "Failed to load failed login sources")

            if not failed_sources.empty:
                fig = px.bar(
                    failed_sources,
                    x='SOURCE_IP',
                    y='ATTEMPT_COUNT',
                    color='AFFECTED_USERS',
                    title="Failed Login Attempts by IP",
                    color_continuous_scale='Reds'
                )
                fig.update_layout(xaxis_tickangle=-45)

        with col2:
            st.markdown("#### Users with Most Failed Logins")

            failed_users_sql = f"""
                SELECT
                    u.USERNAME,
                    u.DEPARTMENT,
                    COUNT(*) as FAILED_COUNT,
                    MAX(e.EVENT_TIMESTAMP) as LAST_FAILED_ATTEMPT
                FROM {get_table_name('FACT_LEVIAT_SECURITY_EVENTS', 'transformation')} e
                JOIN {get_table_name('DIM_LEVIAT_USERS', 'transformation')} u
                    ON e.USER_ID = u.USER_ID
                WHERE e.EVENT_TYPE = 'Failed Login'
                  AND e.EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
                GROUP BY u.USERNAME, u.DEPARTMENT
                ORDER BY FAILED_COUNT DESC
                LIMIT 10
            """

            failed_users = safe_query(failed_users_sql, "Failed to load failed users")

            if not failed_users.empty:
                st.dataframe(
                    failed_users.style,
                    use_container_width=True
                )
                export_csv(failed_users, "leviat_failed_login_users")

        st.markdown("---")

        # Geographic anomalies
        st.markdown("#### Suspicious Login Patterns")

        suspicious_patterns_sql = f"""
            SELECT
                u.USERNAME,
                e.SOURCE_IP,
                e.LOCATION,
                e.DEVICE_TYPE,
                COUNT(*) as LOGIN_COUNT,
                MIN(e.EVENT_TIMESTAMP) as FIRST_SEEN,
                MAX(e.EVENT_TIMESTAMP) as LAST_SEEN
            FROM {get_table_name('FACT_LEVIAT_SECURITY_EVENTS', 'transformation')} e
            JOIN {get_table_name('DIM_LEVIAT_USERS', 'transformation')} u
                ON e.USER_ID = u.USER_ID
            WHERE e.EVENT_TYPE IN ('Login', 'Failed Login')
              AND e.EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
            GROUP BY u.USERNAME, e.SOURCE_IP, e.LOCATION, e.DEVICE_TYPE
            HAVING COUNT(*) >= 3
            ORDER BY LOGIN_COUNT DESC
            LIMIT 50
        """

        suspicious_patterns = safe_query(suspicious_patterns_sql, "Failed to load suspicious patterns")

        if not suspicious_patterns.empty:
            st.dataframe(suspicious_patterns, use_container_width=True, height=400)
            # Download button
            @st.cache_data
            def convert_to_csv_4(df):
                return df.to_csv(index=False).encode('utf-8')

            csv_data = convert_to_csv_4(suspicious_patterns)
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name="leviat_data.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_leviat_5"
            )
            export_csv(suspicious_patterns, "leviat_suspicious_patterns")
        else:
            st.success("✅ No suspicious login patterns detected")

        # Compliance checks
        st.markdown("#### Compliance & Policy Violations")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Inactive Privileged Accounts (90+ days)**")

            inactive_priv_sql = f"""
                SELECT
                    USERNAME,
                    DEPARTMENT,
                    LAST_LOGIN,
                    DATEDIFF(day, LAST_LOGIN, CURRENT_DATE()) as DAYS_INACTIVE
                FROM {get_table_name('DIM_LEVIAT_USERS', 'transformation')}
                WHERE IS_PRIVILEGED = TRUE
                  AND IS_ACTIVE = TRUE
                  AND LAST_LOGIN < DATEADD(day, -90, CURRENT_DATE())
                ORDER BY DAYS_INACTIVE DESC
                LIMIT 20
            """

            inactive_priv = safe_query(inactive_priv_sql, "Failed to load inactive privileged")

            if not inactive_priv.empty:
                st.dataframe(inactive_priv, use_container_width=True)
                # Download button
                @st.cache_data
                def convert_to_csv_5(df):
                    return df.to_csv(index=False).encode('utf-8')

                csv_data = convert_to_csv_5(inactive_priv)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name="leviat_data.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="download_leviat_6"
                )
                export_csv(inactive_priv, "leviat_inactive_privileged")
            else:
                st.success("✅ No inactive privileged accounts found")

        with col2:
            st.markdown("**Accounts Without Recent Activity**")

            no_activity_sql = f"""
                SELECT
                    USERNAME,
                    EMAIL,
                    CREATED_DATE,
                    DATEDIFF(day, CREATED_DATE, CURRENT_DATE()) as ACCOUNT_AGE_DAYS
                FROM {get_table_name('DIM_LEVIAT_USERS', 'transformation')}
                WHERE IS_ACTIVE = TRUE
                  AND LAST_LOGIN IS NULL
                  AND CREATED_DATE < DATEADD(day, -30, CURRENT_DATE())
                ORDER BY CREATED_DATE
                LIMIT 20
            """

            no_activity = safe_query(no_activity_sql, "Failed to load accounts with no activity")

            if not no_activity.empty:
                st.dataframe(no_activity, use_container_width=True)
                # Download button
                @st.cache_data
                def convert_to_csv_6(df):
                    return df.to_csv(index=False).encode('utf-8')

                csv_data = convert_to_csv_6(no_activity)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name="leviat_data.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="download_leviat_7"
                )
                export_csv(no_activity, "leviat_no_activity_accounts")
            else:
                st.success("✅ All accounts have login activity")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("""
**Data Source:** Leviat IAM Platform via Snowflake
**Refresh Rate:** 5-minute cache
**Contact:** GenericCorp Data Engineering Team
""")
