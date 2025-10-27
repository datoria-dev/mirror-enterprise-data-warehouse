"""
SentinelOne EDR Dashboard

Endpoint Detection & Response monitoring dashboard for SentinelOne agents,
threats, and security events.
"""

# Import python packages
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from snowflake.snowpark.context import get_active_session
from datetime import datetime, timedelta

# ============================================================================
# COMMON MODULES (INLINED FOR SNOWFLAKE DEPLOYMENT)
# ============================================================================

# --- Common Module: config.py ---
# Database configuration
DATABASES = {
    'landing': 'DEV_LANDING',
    'transformation': 'DEV_TRANSFORMATION',
    'reporting': 'DEV_REPORTING'
}

SCHEMA = 'SECURITY_ANALYTICS'

# Warehouses
WAREHOUSES = {
    'default': 'DEV_WH',
    'reporting': 'DEV_REPORTING_WH'
}

# Cache settings
CACHE_TTL_SECONDS = 300  # 5 minutes

# Query limits
DEFAULT_ROW_LIMIT = 10000
MAX_EXPORT_ROWS = 50000

# Data freshness thresholds (in minutes)
FRESHNESS_THRESHOLDS = {
    'fresh': 60,        # < 1 hour
    'acceptable': 1440, # < 24 hours
    'stale': 1440       # >= 24 hours
}

# Severity levels
SEVERITY_LEVELS = ['Critical', 'High', 'Medium', 'Low', 'Informational']

# Color scheme (matches styles.py)
COLORS = {
    'primary': '#0a3d62',
    'secondary': '#1e5f8e',
    'accent': '#3498db',
    'success': '#27ae60',
    'warning': '#f39c12',
    'error': '#e74c3c',
}

# Common date ranges
DATE_RANGES = {
    'Last 24 Hours': 1,
    'Last 7 Days': 7,
    'Last 30 Days': 30,
    'Last 90 Days': 90,
    'Last 12 Months': 365
}

# Pagination
DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 1000

# App metadata
APP_VERSION = "1.0.0"
APP_AUTHOR = "GenericCorp Data Engineering Team"
APP_UPDATED = "2025-10-08"


def get_view_name(view_short_name: str, database: str = 'reporting') -> str:
    """
    Get fully qualified view name

    Args:
        view_short_name (str): View name without database/schema
        database (str): Database type ('reporting', 'transformation', 'landing')

    Returns:
        str: Fully qualified view name
    """
    db = DATABASES.get(database, DATABASES['reporting'])
    return f"{db}.{SCHEMA}.{view_short_name}"


def get_table_name(table_short_name: str, database: str = 'landing') -> str:
    """
    Get fully qualified table name

    Args:
        table_short_name (str): Table name without database/schema
        database (str): Database type ('reporting', 'transformation', 'landing')

    Returns:
        str: Fully qualified table name
    """
    db = DATABASES.get(database, DATABASES['landing'])
    return f"{db}.{SCHEMA}.{table_short_name}"


# --- Common Module: styles.py ---
import streamlit as st


def get_color_scheme():
    """
    Get GenericCorp corporate color scheme

    Returns:
        dict: Color scheme with primary, secondary, and accent colors
    """
    return {
        'primary': '#0a3d62',
        'secondary': '#1e5f8e',
        'accent': '#3498db',
        'success': '#27ae60',
        'warning': '#f39c12',
        'error': '#e74c3c',
        'info': '#3498db',
        'bg_light': '#f8f9fa',
        'bg_medium': '#f0f4f8',
        'border': '#e0e4e8',
        'text_muted': '#64748b'
    }


def apply_common_styles():
    """
    Apply common CSS styles to Streamlit app

    This should be called once at the beginning of each app
    after st.set_page_config()
    """
    colors = get_color_scheme()

    st.markdown(f"""
    <style>
        /* Main header styling */
        .main-header {{
            background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%);
            color: white;
            padding: 2.5rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 6px 20px rgba(10, 61, 98, 0.25);
            position: relative;
            overflow: hidden;
        }}

        .main-header::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: repeating-linear-gradient(
                45deg,
                transparent,
                transparent 20px,
                rgba(255,255,255,0.03) 20px,
                rgba(255,255,255,0.03) 40px
            );
        }}

        /* Metric card styling */
        div[data-testid="metric-container"] {{
            background: linear-gradient(to bottom, #ffffff, {colors['bg_light']});
            border: 1px solid {colors['border']};
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(10, 61, 98, 0.08);
            transition: all 0.3s ease;
        }}

        div[data-testid="metric-container"]:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(10, 61, 98, 0.15);
            border-color: {colors['secondary']};
        }}

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 10px;
            background-color: {colors['bg_medium']};
            padding: 0.75rem;
            border-radius: 12px;
            box-shadow: inset 0 2px 4px rgba(10, 61, 98, 0.05);
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: 10px;
            padding: 0.75rem 1.25rem;
            background-color: white;
            border: 1px solid {colors['border']};
            font-weight: 500;
            transition: all 0.2s ease;
        }}

        .stTabs [data-baseweb="tab"]:hover {{
            background-color: #eef3f8;
            border-color: {colors['secondary']};
        }}

        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, {colors['primary']}, {colors['secondary']});
            color: white;
            border-color: {colors['primary']};
            box-shadow: 0 2px 8px rgba(10, 61, 98, 0.2);
        }}

        /* Status badges */
        .status-compliant {{ color: {colors['success']}; font-weight: bold; }}
        .status-warning {{ color: {colors['warning']}; font-weight: bold; }}
        .status-critical {{ color: {colors['error']}; font-weight: bold; }}
        .status-info {{ color: {colors['info']}; font-weight: bold; }}

        /* Risk level badges */
        .risk-critical {{ color: #c0392b; font-weight: bold; }}
        .risk-high {{ color: #e67e22; font-weight: bold; }}
        .risk-medium {{ color: {colors['warning']}; font-weight: bold; }}
        .risk-low {{ color: {colors['info']}; font-weight: bold; }}

        /* KPI cards with gradient borders */
        .kpi-card {{
            background: linear-gradient(to bottom, #ffffff, #fafbfc);
            padding: 25px;
            border-radius: 15px;
            border: 2px solid transparent;
            background-clip: padding-box;
            position: relative;
            text-align: center;
            transition: all 0.3s ease;
        }}

        .kpi-card::before {{
            content: "";
            position: absolute;
            top: 0; right: 0; bottom: 0; left: 0;
            z-index: -1;
            margin: -2px;
            border-radius: inherit;
            background: linear-gradient(135deg, {colors['primary']}, {colors['secondary']}, {colors['accent']});
        }}

        .kpi-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(10, 61, 98, 0.15);
        }}

        .kpi-value {{
            font-size: 2.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, {colors['primary']}, {colors['secondary']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .kpi-label {{
            color: {colors['text_muted']};
            font-size: 0.95rem;
            margin-top: 0.5rem;
            font-weight: 500;
            letter-spacing: 0.5px;
        }}

        /* Section styling */
        h3 {{
            color: {colors['primary']};
            border-bottom: 3px solid transparent;
            border-image: linear-gradient(to right, {colors['primary']}, {colors['secondary']}, transparent) 1;
            padding-bottom: 0.75rem;
            margin-top: 2rem;
            font-weight: 600;
        }}

        /* Button styling */
        .stButton > button {{
            background: linear-gradient(135deg, {colors['primary']}, {colors['secondary']});
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}

        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(10, 61, 98, 0.25);
        }}

        /* Custom info box */
        .stAlert {{
            background-color: #eef3f8;
            border-left: 4px solid {colors['secondary']};
        }}

        /* Data table styling */
        .dataframe {{
            font-size: 0.9rem;
        }}

        .dataframe th {{
            background-color: {colors['bg_medium']};
            color: {colors['primary']};
            font-weight: 600;
        }}
    </style>
    """, unsafe_allow_html=True)


def create_header(title: str, subtitle: str = "", icon: str = "🔐"):
    """
    Create styled header for dashboard

    Args:
        title (str): Dashboard title
        subtitle (str): Optional subtitle
        icon (str): Emoji icon (default: 🔐)
    """
    subtitle_html = f"""
    <p style="text-align: center; margin: 0.75rem 0 0 0; opacity: 0.9; position: relative; z-index: 1; font-size: 1.1rem;">
        {subtitle}
    </p>
    """ if subtitle else ""

    st.markdown(f"""
    <div class="main-header">
        <h1 style="text-align: center; margin: 0; position: relative; z-index: 1;">
            <span style="font-size: 2.5rem;">{icon}</span> {title}
        </h1>
        {subtitle_html}
    </div>
    """, unsafe_allow_html=True)


def create_sidebar_branding(company: str = "GenericCorp", department: str = "Security Dashboard"):
    """
    Create branded sidebar header

    Args:
        company (str): Company name
        department (str): Department or team name
    """
    st.markdown(f"""
    <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #0a3d62, #1e5f8e);
         border-radius: 12px; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(10, 61, 98, 0.2);">
        <h2 style="color: white; margin: 0; font-size: 1.5rem;">🏢 {company}</h2>
        <p style="color: #e8f0f8; font-size: 0.95rem; margin-top: 0.5rem;">{department}</p>
    </div>
    """, unsafe_allow_html=True)


# --- Common Module: utils.py ---
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


# --- Common Module: validators.py ---
import streamlit as st
from snowflake.snowpark.context import get_active_session
from typing import List


def validate_environment(required_views: List[str]):
    """
    Check that all required database views exist

    Args:
        required_views (List[str]): List of fully qualified view names

    Raises:
        SystemExit: If required views are missing
    """
    session = get_active_session()
    missing = []

    for view in required_views:
        try:
            session.sql(f"SELECT 1 FROM {view} LIMIT 1").collect()
        except Exception:
            missing.append(view)

    if missing:
        st.error("❌ **Missing Required Database Objects**")
        st.write("The following views are required but not found:")

        for view in missing:
            st.code(view)

        st.info("""
        **Next Steps:**
        1. Verify you have access to the DEV_REPORTING database
        2. Check that views have been created by running base implementation scripts
        3. Contact Data Engineering if views are missing
        """)

        st.stop()


def check_required_views(views: List[str]) -> dict:
    """
    Check which views exist and return status

    Args:
        views (List[str]): List of fully qualified view names

    Returns:
        dict: Status of each view {view_name: exists (bool)}
    """
    session = get_active_session()
    status = {}

    for view in views:
        try:
            session.sql(f"SELECT 1 FROM {view} LIMIT 1").collect()
            status[view] = True
        except Exception:
            status[view] = False

    return status


def validate_data_completeness(table_name: str, required_columns: List[str]) -> bool:
    """
    Validate that table has required columns

    Args:
        table_name (str): Fully qualified table name
        required_columns (List[str]): List of required column names

    Returns:
        bool: True if all columns exist
    """
    try:
        session = get_active_session()
        sql = f"DESCRIBE TABLE {table_name}"
        result = session.sql(sql).to_pandas()

        existing_columns = set(result['name'].str.upper())
        required = set(col.upper() for col in required_columns)
        missing = required - existing_columns

        if missing:
            st.warning(f"⚠️ Missing columns in {table_name}: {', '.join(missing)}")
            return False

        return True

    except Exception as e:
        st.error(f"❌ Failed to validate {table_name}: {str(e)}")
        return False


def check_data_quality(df, checks: dict) -> dict:
    """
    Run data quality checks on dataframe

    Args:
        df (pd.DataFrame): Dataframe to check
        checks (dict): Quality checks to perform
            Example: {
                'null_threshold': 0.1,  # Max 10% nulls
                'duplicate_check': True,
                'row_min': 1
            }

    Returns:
        dict: Quality check results
    """
    results = {
        'passed': True,
        'issues': []
    }

    # Check minimum rows
    if 'row_min' in checks:
        if len(df) < checks['row_min']:
            results['passed'] = False
            results['issues'].append(f"Row count ({len(df)}) below minimum ({checks['row_min']})")

    # Check null percentage
    if 'null_threshold' in checks:
        null_pct = df.isnull().sum() / len(df)
        high_null_cols = null_pct[null_pct > checks['null_threshold']].index.tolist()

        if high_null_cols:
            results['passed'] = False
            results['issues'].append(f"High null percentage in columns: {', '.join(high_null_cols)}")

    # Check duplicates
    if checks.get('duplicate_check', False):
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            results['passed'] = False
            results['issues'].append(f"Found {duplicates} duplicate rows")

    return results


def show_validation_results(results: dict):
    """
    Display validation results with appropriate styling

    Args:
        results (dict): Results from check_data_quality()
    """
    if results['passed']:
        st.success("✅ All data quality checks passed")
    else:
        st.warning("⚠️ Data quality issues found:")
        for issue in results['issues']:
            st.write(f"- {issue}")




# Import common components
safe_query,
    query_with_metrics,
    export_csv,
    show_data_freshness,
    add_refresh_button,
    show_last_refresh,
    show_alert_threshold
)
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
