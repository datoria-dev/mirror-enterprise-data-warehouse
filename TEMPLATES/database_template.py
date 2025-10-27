"""
Snowflake Database Utilities for SECURITY_ANALYTICS Streamlit Apps
=========================================================

This module contains database interaction utilities for Snowflake,
including query execution, session management, and error handling.

Usage:
    from database import safe_query, get_session, execute_sql

Author: SECURITY_ANALYTICS Team
Date: 2025-10-27
Version: 1.0
"""

import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
from typing import Optional, Union


# =============================================================================
# Configuration Constants
# =============================================================================

# Cache settings
CACHE_TTL_SECONDS = 300  # 5 minutes cache for queries
DEFAULT_ROW_LIMIT = 10000  # Maximum rows to return by default

# Database context
DATABASE = "DEV_REPORTING"
SCHEMA = "SECURITY_ANALYTICS"
WAREHOUSE = "DEV_WH"
ROLE = "DEV_DEVELOPER"


# =============================================================================
# Session Management
# =============================================================================

def get_session():
    """
    Get active Snowflake session with database context set

    Returns:
        Snowpark Session object

    Example:
        >>> session = get_session()
        >>> df = session.sql("SELECT * FROM MY_TABLE").to_pandas()
    """
    session = get_active_session()

    # Set database context (best effort - don't fail if can't set)
    try:
        session.sql(f"USE DATABASE {DATABASE}").collect()
        session.sql(f"USE SCHEMA {SCHEMA}").collect()
        session.sql(f"USE WAREHOUSE {WAREHOUSE}").collect()
    except Exception as e:
        # Log warning but don't fail
        st.warning(f"Could not set database context: {e}")

    return session


# =============================================================================
# Query Execution Functions
# =============================================================================

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def safe_query(
    sql: str,
    error_message: str = "Failed to load data",
    max_rows: int = DEFAULT_ROW_LIMIT,
    show_query: bool = False
) -> pd.DataFrame:
    """
    Execute Snowflake SQL query with error handling and caching

    This function provides a safe way to execute SQL queries with:
    - Automatic database context setting
    - Row limit enforcement (unless LIMIT already in query)
    - Error handling with user-friendly messages
    - Result caching (5 minute TTL)
    - Empty result warnings

    Args:
        sql: SQL query to execute
        error_message: Custom error message to display on failure
        max_rows: Maximum number of rows to return (default 10,000)
        show_query: If True, display the SQL query in UI (for debugging)

    Returns:
        pandas DataFrame with query results, or empty DataFrame on error

    Examples:
        >>> # Basic usage
        >>> df = safe_query("SELECT * FROM SOPHOS_ALERTS")

        >>> # With custom error message and row limit
        >>> df = safe_query(
        ...     "SELECT * FROM LARGE_TABLE",
        ...     error_message="Failed to load vulnerability data",
        ...     max_rows=5000
        ... )

        >>> # Show query for debugging
        >>> df = safe_query("SELECT COUNT(*) as total FROM EVENTS", show_query=True)
    """
    try:
        # Get session with context
        session = get_session()

        # Add LIMIT clause if not present (case insensitive check)
        if 'LIMIT' not in sql.upper():
            sql = f"{sql.rstrip(';')} LIMIT {max_rows}"

        # Optionally show query
        if show_query:
            with st.expander("🔍 SQL Query"):
                st.code(sql, language="sql")

        # Execute query
        result = session.sql(sql).to_pandas()

        # Check if empty
        if result.empty:
            st.warning(f"⚠️ No data found")
            return pd.DataFrame()

        return result

    except Exception as e:
        # Display error to user
        st.error(f"❌ {error_message}")

        # Show technical details in expander
        with st.expander("🔍 Technical Details"):
            st.code(f"Error: {str(e)}\n\nQuery:\n{sql}", language="text")

        # Return empty DataFrame
        return pd.DataFrame()


def execute_sql(
    sql: str,
    return_results: bool = False
) -> Optional[pd.DataFrame]:
    """
    Execute SQL statement (for INSERT, UPDATE, DELETE, CREATE, etc.)

    Unlike safe_query(), this function is designed for SQL statements
    that don't return results (DDL/DML operations).

    Args:
        sql: SQL statement to execute
        return_results: If True, attempt to return results as DataFrame

    Returns:
        DataFrame if return_results=True and query returns data, else None

    Examples:
        >>> # Create a temp table
        >>> execute_sql("CREATE TEMP TABLE test (id INT, name STRING)")

        >>> # Insert data
        >>> execute_sql("INSERT INTO test VALUES (1, 'Alice'), (2, 'Bob')")

        >>> # Update with results
        >>> result = execute_sql("UPDATE test SET name = 'Charlie' WHERE id = 1", return_results=True)
    """
    try:
        session = get_session()
        result = session.sql(sql).collect()

        if return_results and result:
            return pd.DataFrame(result)

        st.success("✅ SQL statement executed successfully")
        return None

    except Exception as e:
        st.error(f"❌ Failed to execute SQL statement")
        with st.expander("🔍 Technical Details"):
            st.code(f"Error: {str(e)}\n\nSQL:\n{sql}", language="text")
        return None


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_table_list(schema: str = SCHEMA, pattern: str = None) -> pd.DataFrame:
    """
    Get list of tables in a schema

    Args:
        schema: Schema name (default: SECURITY_ANALYTICS)
        pattern: Optional pattern to filter table names (SQL LIKE syntax)

    Returns:
        DataFrame with table information

    Examples:
        >>> # Get all tables
        >>> tables = get_table_list()

        >>> # Get tables matching pattern
        >>> sophos_tables = get_table_list(pattern="SOPHOS%")
    """
    sql = f"SHOW TABLES IN SCHEMA {DATABASE}.{schema}"

    if pattern:
        sql += f" LIKE '{pattern}'"

    return safe_query(sql, error_message=f"Failed to list tables in {schema}")


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_table_columns(table_name: str, schema: str = SCHEMA) -> pd.DataFrame:
    """
    Get column information for a table

    Args:
        table_name: Name of the table
        schema: Schema name (default: SECURITY_ANALYTICS)

    Returns:
        DataFrame with column information (name, type, nullable, etc.)

    Examples:
        >>> # Get columns for SOPHOS_ALERTS table
        >>> cols = get_table_columns("SOPHOS_ALERTS")
        >>> print(cols[['column_name', 'data_type']])
    """
    sql = f"DESCRIBE TABLE {DATABASE}.{schema}.{table_name}"
    return safe_query(sql, error_message=f"Failed to describe table {table_name}")


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_row_count(table_name: str, schema: str = SCHEMA, where_clause: str = None) -> int:
    """
    Get row count for a table with optional filter

    Args:
        table_name: Name of the table
        schema: Schema name (default: SECURITY_ANALYTICS)
        where_clause: Optional WHERE clause (without "WHERE" keyword)

    Returns:
        Number of rows

    Examples:
        >>> # Total rows
        >>> total = get_row_count("SOPHOS_ALERTS")

        >>> # Filtered count
        >>> critical = get_row_count("SOPHOS_ALERTS", where_clause="SEVERITY = 'Critical'")
    """
    sql = f"SELECT COUNT(*) as ROW_COUNT FROM {DATABASE}.{schema}.{table_name}"

    if where_clause:
        sql += f" WHERE {where_clause}"

    df = safe_query(sql, error_message=f"Failed to count rows in {table_name}")

    if not df.empty:
        return int(df.iloc[0]['ROW_COUNT'])

    return 0


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def check_table_exists(table_name: str, schema: str = SCHEMA) -> bool:
    """
    Check if a table exists in the schema

    Args:
        table_name: Name of the table to check
        schema: Schema name (default: SECURITY_ANALYTICS)

    Returns:
        True if table exists, False otherwise

    Examples:
        >>> if check_table_exists("SOPHOS_ALERTS"):
        ...     print("Table exists!")
    """
    try:
        sql = f"""
        SELECT COUNT(*) as TABLE_COUNT
        FROM {DATABASE}.INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = '{schema}'
        AND TABLE_NAME = '{table_name}'
        """
        df = safe_query(sql, error_message=f"Failed to check if {table_name} exists")

        if not df.empty:
            return int(df.iloc[0]['TABLE_COUNT']) > 0

        return False

    except:
        return False


# =============================================================================
# Metadata Helper Functions
# =============================================================================

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_metadata_for_service(service_name: str) -> pd.DataFrame:
    """
    Get metadata from TABLE_REGISTRY for a specific service

    Args:
        service_name: Name of the service (e.g., 'Sophos', 'CrowdStrike')

    Returns:
        DataFrame with metadata (service name, table name, columns, record count)

    Examples:
        >>> metadata = get_metadata_for_service("Sophos")
        >>> print(metadata[['TABLE_NAME', 'TOTAL_COLUMNS', 'RECORD_COUNT']])
    """
    sql = f"""
    SELECT
        SERVICE_NAME,
        TABLE_NAME,
        TOTAL_COLUMNS,
        RECORD_COUNT,
        LAST_UPDATED
    FROM {DATABASE}.METADATA.TABLE_REGISTRY
    WHERE UPPER(SERVICE_NAME) = UPPER('{service_name}')
    ORDER BY TABLE_NAME
    """

    return safe_query(sql, error_message=f"Failed to load metadata for {service_name}")


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_column_metadata(table_name: str) -> pd.DataFrame:
    """
    Get detailed column metadata for a table

    Args:
        table_name: Name of the table

    Returns:
        DataFrame with column details from COLUMN_REGISTRY

    Examples:
        >>> columns = get_column_metadata("SOPHOS_EXPORT_ALERTS")
        >>> print(columns[['COLUMN_NAME', 'DATA_TYPE', 'IS_NULLABLE']])
    """
    sql = f"""
    SELECT
        COLUMN_NAME,
        DATA_TYPE,
        IS_NULLABLE,
        COLUMN_DEFAULT,
        ORDINAL_POSITION
    FROM {DATABASE}.METADATA.COLUMN_REGISTRY
    WHERE TABLE_NAME = '{table_name}'
    ORDER BY ORDINAL_POSITION
    """

    return safe_query(sql, error_message=f"Failed to load column metadata for {table_name}")


# =============================================================================
# Data Quality Helper Functions
# =============================================================================

def get_data_freshness(table_name: str, date_column: str, schema: str = SCHEMA) -> dict:
    """
    Get data freshness information for a table

    Args:
        table_name: Name of the table
        date_column: Name of the date/timestamp column
        schema: Schema name (default: SECURITY_ANALYTICS)

    Returns:
        Dictionary with min_date, max_date, and days_old

    Examples:
        >>> freshness = get_data_freshness("SOPHOS_ALERTS", "CREATED_DATE")
        >>> st.write(f"Data is {freshness['days_old']} days old")
    """
    sql = f"""
    SELECT
        MIN({date_column}) as MIN_DATE,
        MAX({date_column}) as MAX_DATE,
        DATEDIFF(day, MAX({date_column}), CURRENT_DATE()) as DAYS_OLD
    FROM {DATABASE}.{schema}.{table_name}
    """

    df = safe_query(sql, error_message=f"Failed to check data freshness for {table_name}")

    if not df.empty:
        return {
            'min_date': df.iloc[0]['MIN_DATE'],
            'max_date': df.iloc[0]['MAX_DATE'],
            'days_old': int(df.iloc[0]['DAYS_OLD']) if df.iloc[0]['DAYS_OLD'] else None
        }

    return {'min_date': None, 'max_date': None, 'days_old': None}


# =============================================================================
# Module metadata
# =============================================================================

__version__ = "1.0.0"
__author__ = "SECURITY_ANALYTICS Team"
__all__ = [
    'get_session',
    'safe_query',
    'execute_sql',
    'get_table_list',
    'get_table_columns',
    'get_row_count',
    'check_table_exists',
    'get_metadata_for_service',
    'get_column_metadata',
    'get_data_freshness'
]
