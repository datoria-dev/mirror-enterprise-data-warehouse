"""
Common utility functions for Streamlit apps

Provides query execution, error handling, caching, and data export functions.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from snowflake.snowpark.context import get_active_session
import time
from typing import Optional


@st.cache_data(ttl=300)  # 5-minute cache
def safe_query(sql: str, error_message: str = "Failed to load data", max_rows: int = 10000) -> pd.DataFrame:
    """
    Execute Snowflake query with error handling and caching

    Args:
        sql (str): SQL query to execute
        error_message (str): Custom error message to display on failure
        max_rows (int): Maximum rows to return (default: 10,000)

    Returns:
        pd.DataFrame: Query results or empty DataFrame on error
    """
    try:
        session = get_active_session()

        # Add row limit if not present
        if 'LIMIT' not in sql.upper():
            sql = f"{sql.rstrip(';')} LIMIT {max_rows}"

        result = session.sql(sql).to_pandas()

        if result.empty:
            st.warning(f"⚠️ No data found. {error_message}")
            return pd.DataFrame()

        return result

    except Exception as e:
        st.error(f"❌ {error_message}")
        with st.expander("🔍 Technical Details (Click to expand)"):
            st.code(f"Error: {str(e)}\n\nQuery:\n{sql}")
        return pd.DataFrame()


def query_with_metrics(sql: str, error_message: str = "Failed to load data") -> pd.DataFrame:
    """
    Execute query and display performance metrics

    Args:
        sql (str): SQL query to execute
        error_message (str): Custom error message

    Returns:
        pd.DataFrame: Query results
    """
    start_time = time.time()
    result = safe_query(sql, error_message)
    elapsed = time.time() - start_time

    if not result.empty:
        st.caption(f"⏱️ Query executed in {elapsed:.2f}s | {len(result):,} rows returned")

    return result


def export_csv(df: pd.DataFrame, filename: str = "export", button_label: str = "📥 Export to CSV"):
    """
    Add CSV export button for dataframe

    Args:
        df (pd.DataFrame): Dataframe to export
        filename (str): Base filename without extension
        button_label (str): Button label text
    """
    if df.empty:
        st.warning("⚠️ No data to export")
        return

    csv = df.to_csv(index=False).encode('utf-8')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    st.download_button(
        label=button_label,
        data=csv,
        file_name=f"{filename}_{timestamp}.csv",
        mime="text/csv",
        help=f"Export {len(df):,} rows to CSV file"
    )


def show_data_freshness(table_name: str, timestamp_column: str = "INGESTION_TIMESTAMP"):
    """
    Display data freshness indicator

    Args:
        table_name (str): Fully qualified table name
        timestamp_column (str): Column containing timestamp
    """
    sql = f"""
        SELECT
            MAX({timestamp_column}) as LAST_UPDATE,
            DATEDIFF(minute, MAX({timestamp_column}), CURRENT_TIMESTAMP()) as MINUTES_AGO
        FROM {table_name}
    """

    result = safe_query(sql, "Failed to check data freshness")

    if not result.empty:
        minutes_ago = result['MINUTES_AGO'].iloc[0]
        last_update = result['LAST_UPDATE'].iloc[0]

        if minutes_ago < 60:
            st.success(f"✅ Data is fresh (updated {minutes_ago} minutes ago)")
        elif minutes_ago < 1440:  # 24 hours
            hours_ago = minutes_ago // 60
            st.warning(f"⚠️ Data is {hours_ago} hours old (last update: {last_update})")
        else:
            days_ago = minutes_ago // 1440
            st.error(f"❌ Data is stale ({days_ago} days old, last update: {last_update})")
    else:
        st.error("❌ Unable to determine data freshness")


def paginate_dataframe(df: pd.DataFrame, page_size: int = 100, key: str = "page"):
    """
    Add pagination to large dataframes

    Args:
        df (pd.DataFrame): Dataframe to paginate
        page_size (int): Rows per page
        key (str): Unique key for page number input

    Returns:
        pd.DataFrame: Paginated dataframe slice
    """
    if df.empty:
        return df

    total_pages = (len(df) - 1) // page_size + 1

    if total_pages == 1:
        return df  # No pagination needed

    page = st.number_input(
        'Page',
        min_value=1,
        max_value=total_pages,
        value=1,
        key=key,
        help=f"Navigate through {total_pages} pages"
    )

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    st.caption(f"Showing rows {start_idx + 1}-{min(end_idx, len(df))} of {len(df):,} total")

    return df.iloc[start_idx:end_idx]


def format_number(value: float, suffix: str = "", decimals: int = 0) -> str:
    """
    Format large numbers with K, M, B suffixes

    Args:
        value (float): Number to format
        suffix (str): Optional suffix (e.g., '%', 'rows')
        decimals (int): Decimal places

    Returns:
        str: Formatted number
    """
    if pd.isna(value):
        return "N/A"

    if abs(value) >= 1_000_000_000:
        return f"{value/1_000_000_000:.{decimals}f}B{suffix}"
    elif abs(value) >= 1_000_000:
        return f"{value/1_000_000:.{decimals}f}M{suffix}"
    elif abs(value) >= 1_000:
        return f"{value/1_000:.{decimals}f}K{suffix}"
    else:
        return f"{value:.{decimals}f}{suffix}"


def show_alert_threshold(value: float, threshold_warning: float, threshold_critical: float,
                         label: str, higher_is_better: bool = False):
    """
    Display metric with alert threshold coloring

    Args:
        value (float): Current metric value
        threshold_warning (float): Warning threshold
        threshold_critical (float): Critical threshold
        label (str): Metric label
        higher_is_better (bool): If True, higher values are good
    """
    if higher_is_better:
        if value >= threshold_critical:
            st.success(f"✅ {label}: {value:,.0f} (Excellent)")
        elif value >= threshold_warning:
            st.warning(f"⚠️ {label}: {value:,.0f} (Acceptable)")
        else:
            st.error(f"❌ {label}: {value:,.0f} (Below threshold)")
    else:
        if value >= threshold_critical:
            st.error(f"🚨 {label}: {value:,.0f} (Critical - Exceeds threshold of {threshold_critical:,.0f})")
        elif value >= threshold_warning:
            st.warning(f"⚠️ {label}: {value:,.0f} (Warning - Approaching threshold)")
        else:
            st.success(f"✅ {label}: {value:,.0f} (Within acceptable range)")


def create_metric_card(title: str, value: str, delta: Optional[str] = None, help_text: Optional[str] = None):
    """
    Create custom metric card with styling

    Args:
        title (str): Metric title
        value (str): Metric value
        delta (str): Change indicator
        help_text (str): Tooltip help text
    """
    st.metric(
        label=title,
        value=value,
        delta=delta,
        help=help_text
    )


def add_refresh_button(clear_cache: bool = True):
    """
    Add refresh button to sidebar

    Args:
        clear_cache (bool): Whether to clear all cached data
    """
    if st.sidebar.button("🔄 Refresh Data", use_container_width=True, type="primary"):
        if clear_cache:
            st.cache_data.clear()
        st.rerun()


def show_last_refresh():
    """Display timestamp of last dashboard refresh"""
    st.sidebar.markdown("---")
    st.sidebar.caption(f"🕐 Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
