"""
Snowflake Database Utilities for SECURITY_ANALYTICS Streamlit Apps
Provides standardized database query functions with error handling and caching
"""
import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

CACHE_TTL_SECONDS = 300  # 5 minutes
DEFAULT_ROW_LIMIT = 10000
DATABASE = "DEV_REPORTING"
SCHEMA = "SECURITY_ANALYTICS"
WAREHOUSE = "DEV_WH"

# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

def get_session():
    """
    Get active Snowflake session with database context set

    Returns:
        Active Snowflake session object
    """
    session = get_active_session()

    # Set database context
    try:
        session.sql(f"USE DATABASE {DATABASE}").collect()
        session.sql(f"USE SCHEMA {SCHEMA}").collect()
        session.sql(f"USE WAREHOUSE {WAREHOUSE}").collect()
    except Exception as e:
        st.warning(f"⚠️ Could not set database context: {e}")

    return session

# ============================================================================
# QUERY FUNCTIONS
# ============================================================================

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def safe_query(
    sql: str,
    error_message: str = "Failed to load data",
    max_rows: int = DEFAULT_ROW_LIMIT,
    show_query: bool = False
) -> pd.DataFrame:
    """
    Execute Snowflake SQL query with error handling and caching

    Args:
        sql: SQL query to execute
        error_message: Custom error message to display on failure
        max_rows: Maximum rows to return (adds LIMIT if not present)
        show_query: Whether to display the SQL query in expander

    Returns:
        pandas DataFrame with query results, or empty DataFrame on error
    """
    try:
        session = get_session()

        # Add LIMIT if not present
        if 'LIMIT' not in sql.upper():
            sql = f"{sql.rstrip(';')} LIMIT {max_rows}"

        # Show query if requested
        if show_query:
            with st.expander("🔍 View SQL Query"):
                st.code(sql, language="sql")

        # Execute query
        result = session.sql(sql).to_pandas()

        # Check if empty
        if result.empty:
            st.warning(f"⚠️ No data found")
            return pd.DataFrame()

        return result

    except Exception as e:
        st.error(f"❌ {error_message}")
        with st.expander("🔍 Technical Details"):
            st.code(f"Error: {str(e)}\n\nQuery:\n{sql}", language="text")
        return pd.DataFrame()

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_table_data(
    table_name: str,
    columns: str = "*",
    where_clause: str = "",
    order_by: str = "",
    limit: int = DEFAULT_ROW_LIMIT
) -> pd.DataFrame:
    """
    Get data from a table with optional filtering and ordering

    Args:
        table_name: Name of the table (can include schema)
        columns: Comma-separated list of columns or "*"
        where_clause: Optional WHERE clause (without WHERE keyword)
        order_by: Optional ORDER BY clause (without ORDER BY keyword)
        limit: Maximum rows to return

    Returns:
        pandas DataFrame with table data
    """
    sql = f"SELECT {columns} FROM {table_name}"

    if where_clause:
        sql += f" WHERE {where_clause}"

    if order_by:
        sql += f" ORDER BY {order_by}"

    sql += f" LIMIT {limit}"

    return safe_query(
        sql,
        error_message=f"Failed to load data from {table_name}"
    )

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_distinct_values(
    table_name: str,
    column_name: str,
    where_clause: str = ""
) -> list:
    """
    Get distinct values from a column

    Args:
        table_name: Name of the table
        column_name: Name of the column
        where_clause: Optional WHERE clause (without WHERE keyword)

    Returns:
        List of distinct values
    """
    sql = f"SELECT DISTINCT {column_name} FROM {table_name}"

    if where_clause:
        sql += f" WHERE {where_clause}"

    sql += f" ORDER BY {column_name}"

    df = safe_query(sql)

    if df.empty:
        return []

    return df[column_name].tolist()

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_count(
    table_name: str,
    where_clause: str = ""
) -> int:
    """
    Get count of rows in a table

    Args:
        table_name: Name of the table
        where_clause: Optional WHERE clause (without WHERE keyword)

    Returns:
        Count of rows
    """
    sql = f"SELECT COUNT(*) as COUNT FROM {table_name}"

    if where_clause:
        sql += f" WHERE {where_clause}"

    df = safe_query(sql)

    if df.empty:
        return 0

    return int(df['COUNT'].iloc[0])

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_aggregation(
    table_name: str,
    agg_expression: str,
    group_by: str = "",
    where_clause: str = "",
    order_by: str = "",
    limit: int = 100
) -> pd.DataFrame:
    """
    Get aggregated data from a table

    Args:
        table_name: Name of the table
        agg_expression: Aggregation expression (e.g., "COUNT(*) as total, AVG(value) as avg_value")
        group_by: Optional GROUP BY clause (without GROUP BY keyword)
        where_clause: Optional WHERE clause (without WHERE keyword)
        order_by: Optional ORDER BY clause (without ORDER BY keyword)
        limit: Maximum rows to return

    Returns:
        pandas DataFrame with aggregated data
    """
    sql = f"SELECT {agg_expression} FROM {table_name}"

    if where_clause:
        sql += f" WHERE {where_clause}"

    if group_by:
        sql += f" GROUP BY {group_by}"

    if order_by:
        sql += f" ORDER BY {order_by}"

    sql += f" LIMIT {limit}"

    return safe_query(sql)

# ============================================================================
# METADATA FUNCTIONS
# ============================================================================

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_table_info(table_name: str) -> dict:
    """
    Get metadata about a table

    Args:
        table_name: Name of the table

    Returns:
        Dictionary with table metadata (row_count, column_count, columns)
    """
    try:
        session = get_session()

        # Get row count
        count_sql = f"SELECT COUNT(*) as COUNT FROM {table_name}"
        count_df = session.sql(count_sql).to_pandas()
        row_count = int(count_df['COUNT'].iloc[0]) if not count_df.empty else 0

        # Get column info
        desc_sql = f"DESCRIBE TABLE {table_name}"
        desc_df = session.sql(desc_sql).to_pandas()

        return {
            'row_count': row_count,
            'column_count': len(desc_df),
            'columns': desc_df['name'].tolist() if not desc_df.empty else []
        }

    except Exception as e:
        st.error(f"❌ Failed to get table info for {table_name}: {e}")
        return {
            'row_count': 0,
            'column_count': 0,
            'columns': []
        }

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def check_table_exists(table_name: str) -> bool:
    """
    Check if a table exists

    Args:
        table_name: Name of the table (can include schema)

    Returns:
        True if table exists, False otherwise
    """
    try:
        session = get_session()

        # Parse table name
        parts = table_name.split('.')
        if len(parts) == 1:
            schema = SCHEMA
            table = parts[0]
        else:
            schema = parts[0]
            table = parts[1]

        sql = f"""
        SELECT COUNT(*) as COUNT
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = '{schema}'
        AND TABLE_NAME = '{table}'
        """

        result = session.sql(sql).to_pandas()

        return int(result['COUNT'].iloc[0]) > 0 if not result.empty else False

    except Exception:
        return False

# ============================================================================
# DATE/TIME FUNCTIONS
# ============================================================================

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_date_range(
    table_name: str,
    date_column: str
) -> tuple:
    """
    Get min and max dates from a date column

    Args:
        table_name: Name of the table
        date_column: Name of the date column

    Returns:
        Tuple of (min_date, max_date) or (None, None) if error
    """
    sql = f"""
    SELECT
        MIN({date_column}) as MIN_DATE,
        MAX({date_column}) as MAX_DATE
    FROM {table_name}
    """

    df = safe_query(sql)

    if df.empty:
        return (None, None)

    return (df['MIN_DATE'].iloc[0], df['MAX_DATE'].iloc[0])

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def clear_cache():
    """Clear all cached query results"""
    st.cache_data.clear()
    st.success("✅ Cache cleared successfully")

def display_query_info(df: pd.DataFrame, query_name: str = "Query"):
    """
    Display information about a query result

    Args:
        df: Query result DataFrame
        query_name: Name to display for the query
    """
    if df.empty:
        st.info(f"ℹ️ {query_name} returned no results")
    else:
        rows, cols = df.shape
        st.info(f"ℹ️ {query_name} returned {rows:,} rows × {cols} columns")
