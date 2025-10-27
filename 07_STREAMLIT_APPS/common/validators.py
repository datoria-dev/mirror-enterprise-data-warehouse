"""
Data validation functions for Streamlit apps

Provides environment validation and data quality checks.
"""

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
