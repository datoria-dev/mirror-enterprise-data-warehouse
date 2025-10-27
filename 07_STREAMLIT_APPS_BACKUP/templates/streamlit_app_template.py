"""
SECURITY_ANALYTICS Streamlit App Template

This template provides a starting point for creating new validation dashboards.
Replace [APP_NAME], [ICON], and [DATA_SOURCE] with appropriate values.

Example:
  APP_NAME: CrowdStrike EDR Dashboard
  ICON: 🦅
  DATA_SOURCE: CrowdStrike Falcon
"""

# Import python packages
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from snowflake.snowpark.context import get_active_session
from datetime import datetime, timedelta

# Import common components
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
    page_title="[APP_NAME]",  # e.g., "CrowdStrike EDR Dashboard"
    page_icon="[ICON]",       # e.g., "🦅"
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply common styles
apply_common_styles()

# ============================================================================
# ENVIRONMENT VALIDATION
# ============================================================================

# Define required views for this app
REQUIRED_VIEWS = [
    get_view_name('VW_[APP]_SUMMARY'),      # e.g., VW_CROWDSTRIKE_SUMMARY
    get_view_name('VW_[APP]_DETAILS'),      # e.g., VW_EDR_THREATS
    # Add more required views as needed
]

# Validate that all required views exist
validate_environment(REQUIRED_VIEWS)

# Get Snowflake session
session = get_active_session()

# ============================================================================
# HEADER
# ============================================================================

create_header(
    title="[APP_NAME]",
    subtitle="[Data Source Description]",  # e.g., "Endpoint Detection & Response"
    icon="[ICON]"
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

    # Severity filter (if applicable)
    severity_filter = st.multiselect(
        "Severity",
        SEVERITY_LEVELS,
        default=['Critical', 'High'],
        help="Filter by severity level"
    )

    # Custom filters for this app
    # Add app-specific filters here

    st.markdown("---")

    # Refresh button
    add_refresh_button()

    # Info section
    st.info("""
    **📊 Data Source:**
    [DATA_SOURCE]

    **📈 Metrics Tracked:**
    - Metric 1
    - Metric 2
    - Metric 3
    """)

    # Last refresh timestamp
    show_last_refresh()

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Tab layout
tab1, tab2, tab3 = st.tabs([
    "📊 Overview",
    "📋 Detailed Data",
    "📈 Trends"
])

# ---------------------------------------------------------------------------
# TAB 1: OVERVIEW
# ---------------------------------------------------------------------------

with tab1:
    st.subheader("Overview Metrics")

    # Data freshness indicator
    show_data_freshness(
        get_view_name('VW_[APP]_SUMMARY'),
        timestamp_column='INGESTION_TIMESTAMP'
    )

    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Example metric 1
        metric1_sql = f"""
            SELECT COUNT(*) as TOTAL_RECORDS
            FROM {get_view_name('VW_[APP]_SUMMARY')}
            WHERE DATE >= DATEADD(day, -{days}, CURRENT_DATE())
        """
        metric1_data = safe_query(metric1_sql, "Failed to load metric 1")

        if not metric1_data.empty:
            st.metric(
                "Total Records",
                f"{metric1_data['TOTAL_RECORDS'].iloc[0]:,}",
                help="Total number of records in selected time range"
            )

    with col2:
        # Example metric 2
        st.metric(
            "Metric 2",
            "0",
            delta="0",
            help="Description of metric 2"
        )

    with col3:
        # Example metric 3
        st.metric(
            "Metric 3",
            "0%",
            delta="+0%",
            help="Description of metric 3"
        )

    with col4:
        # Example metric 4
        st.metric(
            "Metric 4",
            "0",
            help="Description of metric 4"
        )

    st.markdown("---")

    # Visualization example
    st.subheader("Distribution Chart")

    chart_sql = f"""
        SELECT
            CATEGORY,
            COUNT(*) as COUNT
        FROM {get_view_name('VW_[APP]_DETAILS')}
        WHERE DATE >= DATEADD(day, -{days}, CURRENT_DATE())
        GROUP BY CATEGORY
        ORDER BY COUNT DESC
        LIMIT 10
    """

    chart_data = safe_query(chart_sql, "Failed to load chart data")

    if not chart_data.empty:
        fig = px.bar(
            chart_data,
            x='CATEGORY',
            y='COUNT',
            title="Top 10 Categories",
            labels={'CATEGORY': 'Category', 'COUNT': 'Count'}
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# TAB 2: DETAILED DATA
# ---------------------------------------------------------------------------

with tab2:
    st.subheader("Detailed Records")

    # Query detailed data
    details_sql = f"""
        SELECT *
        FROM {get_view_name('VW_[APP]_DETAILS')}
        WHERE DATE >= DATEADD(day, -{days}, CURRENT_DATE())
          AND SEVERITY IN ('{"','".join(severity_filter)}')
        ORDER BY DATE DESC
    """

    details_data = query_with_metrics(details_sql, "Failed to load detailed data")

    if not details_data.empty:
        # Display dataframe
        st.dataframe(
            details_data,
            use_container_width=True,
            height=400
        )

        # Export button
        export_csv(details_data, "[app_name]_details")

        # Summary stats
        st.caption(f"Showing {len(details_data):,} records")
    else:
        st.warning("⚠️ No data found for selected filters")

# ---------------------------------------------------------------------------
# TAB 3: TRENDS
# ---------------------------------------------------------------------------

with tab3:
    st.subheader("Trend Analysis")

    # Time series query
    trend_sql = f"""
        SELECT
            DATE_TRUNC('day', DATE) as DAY,
            COUNT(*) as DAILY_COUNT
        FROM {get_view_name('VW_[APP]_DETAILS')}
        WHERE DATE >= DATEADD(day, -{days}, CURRENT_DATE())
        GROUP BY DAY
        ORDER BY DAY
    """

    trend_data = safe_query(trend_sql, "Failed to load trend data")

    if not trend_data.empty:
        fig = px.line(
            trend_data,
            x='DAY',
            y='DAILY_COUNT',
            title="Daily Trend",
            labels={'DAY': 'Date', 'DAILY_COUNT': 'Count'}
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("""
**Data Source:** [DATA_SOURCE] via Snowflake
**Refresh Rate:** 5-minute cache
**Contact:** Data Engineering Team
""")
