"""
ServiceNow ITSM Dashboard

IT Service Management dashboard for ServiceNow platform,
monitoring incidents, changes, CMDB, and ITSM KPIs.
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
    show_last_refresh
)
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
            st.plotly_chart(fig, use_container_width=True)

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
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

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
            st.plotly_chart(fig, use_container_width=True)

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
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

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
        st.plotly_chart(fig, use_container_width=True)

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
            st.plotly_chart(fig, use_container_width=True)

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
            st.plotly_chart(fig, use_container_width=True)

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
        st.plotly_chart(fig, use_container_width=True)

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
        st.plotly_chart(fig, use_container_width=True)
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
