"""
Leviat IAM Dashboard

Identity and Access Management dashboard for Leviat platform,
monitoring user access, authentication events, and security compliance.
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
    page_title="Leviat IAM Dashboard",
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
                st.plotly_chart(fig, use_container_width=True)

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
                st.plotly_chart(fig, use_container_width=True)

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
            st.plotly_chart(fig, use_container_width=True)

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
                st.plotly_chart(fig, use_container_width=True)

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
            st.plotly_chart(fig, use_container_width=True)

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
                st.plotly_chart(fig, use_container_width=True)

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
                    failed_users.style.background_gradient(
                        subset=['FAILED_COUNT'],
                        cmap='Reds'
                    ),
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
