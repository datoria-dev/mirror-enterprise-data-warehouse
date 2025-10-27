"""
Proofpoint Email Security Dashboard

Email security monitoring dashboard for Proofpoint platform,
tracking email threats, phishing attempts, malware, and user behavior.
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
    page_title="Proofpoint Email Security",
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
            st.plotly_chart(fig, use_container_width=True)
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
            st.plotly_chart(fig, use_container_width=True)

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
        st.plotly_chart(fig, use_container_width=True)

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
        st.plotly_chart(fig, use_container_width=True)

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
        st.plotly_chart(fig, use_container_width=True)

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
        st.plotly_chart(fig, use_container_width=True)

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
            st.plotly_chart(fig, use_container_width=True)

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
            st.plotly_chart(fig, use_container_width=True)

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
            campaigns_data.style.background_gradient(
                subset=['DELIVERED_COUNT'],
                cmap='Reds'
            ),
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
            st.plotly_chart(fig, use_container_width=True)

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
            st.plotly_chart(fig, use_container_width=True)

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
            high_risk_users.style.background_gradient(
                subset=['URL_CLICKS'],
                cmap='Reds'
            ),
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
