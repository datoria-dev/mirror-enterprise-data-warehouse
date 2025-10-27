"""
Common configuration for Streamlit apps

Centralized configuration for database objects, settings, and constants.
"""

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
