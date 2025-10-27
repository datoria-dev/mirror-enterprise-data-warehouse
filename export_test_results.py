"""
================================================================================
Export Test Results to JSON/CSV Files
================================================================================

This Python script connects to Snowflake, executes test queries, and
automatically saves results to JSON and CSV files.

Requirements:
    pip install snowflake-connector-python pandas

Usage:
    python export_test_results.py

Date: 2025-10-24
================================================================================
"""

import snowflake.connector
import pandas as pd
import json
import os
from datetime import datetime
from pathlib import Path

# ============================================================================
# Configuration
# ============================================================================

# Snowflake connection parameters (SSO with Okta)
SNOWFLAKE_CONFIG = {
    'user': 'YOUR_EMAIL@GenericCorp.com',  # Replace with your GenericCorp email
    'authenticator': 'externalbrowser',  # SSO authentication via Okta
    'account': 'YOUR_ACCOUNT',  # Replace with your account identifier (e.g., 'abc12345.us-east-1')
    'warehouse': 'DEV_WH',
    'database': 'DEV_TRANSFORMATION',
    'schema': 'METADATA',
    'role': 'DEV_DEVELOPER'
}

# Output directory for test results
OUTPUT_DIR = Path('04_METADATA_SAMPLES/test_results')

# ============================================================================
# Test Queries
# ============================================================================

TEST_QUERIES = {
    'execution_log': """
        SELECT
            LOG_ID,
            PROCEDURE_NAME,
            EXECUTION_START,
            EXECUTION_END,
            EXECUTION_DURATION_SECONDS,
            STATUS,
            TABLES_PROCESSED,
            COLUMNS_PROCESSED,
            ROWS_PROCESSED,
            ERROR_MESSAGE,
            EXECUTION_DETAILS,
            EXECUTED_BY,
            CREATED_DATE
        FROM PROCEDURE_EXECUTION_LOG
        ORDER BY EXECUTION_START DESC
        LIMIT 5
    """,

    'success_criteria': """
        WITH latest_log AS (
            SELECT
                STATUS,
                TABLES_PROCESSED,
                COLUMNS_PROCESSED,
                EXECUTION_DURATION_SECONDS,
                ERROR_MESSAGE
            FROM PROCEDURE_EXECUTION_LOG
            ORDER BY EXECUTION_START DESC
            LIMIT 1
        )
        SELECT
            'Execution completed successfully' as CRITERIA,
            'SUCCESS' as EXPECTED_VALUE,
            STATUS as ACTUAL_VALUE,
            CASE WHEN STATUS = 'SUCCESS' THEN '✅ PASS' ELSE '❌ FAIL' END as TEST_RESULT
        FROM latest_log
        UNION ALL
        SELECT
            'Tables processed > 0',
            '> 0',
            TABLES_PROCESSED::VARCHAR,
            CASE WHEN TABLES_PROCESSED > 0 THEN '✅ PASS' ELSE '❌ FAIL' END
        FROM latest_log
        UNION ALL
        SELECT
            'Columns processed > 0',
            '> 0',
            COLUMNS_PROCESSED::VARCHAR,
            CASE WHEN COLUMNS_PROCESSED > 0 THEN '✅ PASS' ELSE '❌ FAIL' END
        FROM latest_log
        UNION ALL
        SELECT
            'Execution duration < 30 seconds',
            '< 30 sec',
            EXECUTION_DURATION_SECONDS::VARCHAR || ' sec',
            CASE WHEN EXECUTION_DURATION_SECONDS < 30 THEN '✅ PASS' ELSE '⚠️  WARNING' END
        FROM latest_log
        UNION ALL
        SELECT
            'No error message',
            'NULL',
            COALESCE(ERROR_MESSAGE, '(none)'),
            CASE WHEN ERROR_MESSAGE IS NULL THEN '✅ PASS' ELSE '❌ FAIL' END
        FROM latest_log
    """,

    'services_detected': """
        SELECT
            SERVICE_NAME,
            COUNT(*) as TABLE_COUNT,
            DATA_LAYER,
            SUM(ROW_COUNT) as TOTAL_ROWS
        FROM TABLE_REGISTRY
        GROUP BY SERVICE_NAME, DATA_LAYER
        ORDER BY TABLE_COUNT DESC
    """,

    'tables_loaded': """
        SELECT
            SERVICE_NAME,
            DATABASE_NAME,
            SCHEMA_NAME,
            TABLE_NAME,
            TABLE_TYPE,
            DATA_LAYER,
            ROW_COUNT,
            LAST_UPDATED
        FROM TABLE_REGISTRY
        ORDER BY SERVICE_NAME, TABLE_NAME
    """,

    'columns_summary': """
        SELECT
            tr.SERVICE_NAME,
            tr.TABLE_NAME,
            COUNT(cm.COLUMN_ID) as COLUMN_COUNT,
            LISTAGG(cm.COLUMN_NAME, ', ') WITHIN GROUP (ORDER BY cm.ORDINAL_POSITION) as COLUMNS
        FROM TABLE_REGISTRY tr
        LEFT JOIN COLUMN_METADATA cm ON tr.TABLE_ID = cm.TABLE_ID
        GROUP BY tr.SERVICE_NAME, tr.TABLE_NAME
        ORDER BY tr.SERVICE_NAME, tr.TABLE_NAME
    """,

    'columns_detailed': """
        SELECT
            tr.SERVICE_NAME,
            tr.TABLE_NAME,
            cm.COLUMN_NAME,
            cm.DATA_TYPE,
            cm.IS_NULLABLE,
            cm.ORDINAL_POSITION,
            cm.COLUMN_DEFAULT,
            cm.COLUMN_COMMENT
        FROM COLUMN_METADATA cm
        JOIN TABLE_REGISTRY tr ON cm.TABLE_ID = tr.TABLE_ID
        ORDER BY tr.SERVICE_NAME, tr.TABLE_NAME, cm.ORDINAL_POSITION
    """,

    'statistics_snapshot': """
        SELECT
            ts.SNAPSHOT_DATE,
            tr.SERVICE_NAME,
            tr.TABLE_NAME,
            ts.ROW_COUNT,
            ts.COLUMN_COUNT,
            ts.SIZE_BYTES,
            ts.LAST_MODIFIED
        FROM TABLE_STATISTICS ts
        JOIN TABLE_REGISTRY tr ON ts.TABLE_ID = tr.TABLE_ID
        ORDER BY ts.SNAPSHOT_DATE DESC, tr.SERVICE_NAME, tr.TABLE_NAME
    """,

    'overall_summary': """
        SELECT
            'Total Services Detected' as METRIC,
            COUNT(DISTINCT SERVICE_NAME)::VARCHAR as VALUE,
            '' as UNIT
        FROM TABLE_REGISTRY
        UNION ALL
        SELECT
            'Total Tables Loaded',
            COUNT(*)::VARCHAR,
            'tables'
        FROM TABLE_REGISTRY
        UNION ALL
        SELECT
            'Total Columns Loaded',
            COUNT(*)::VARCHAR,
            'columns'
        FROM COLUMN_METADATA
        UNION ALL
        SELECT
            'Total Statistics Created',
            COUNT(*)::VARCHAR,
            'snapshots'
        FROM TABLE_STATISTICS
        UNION ALL
        SELECT
            'Execution Duration',
            (SELECT EXECUTION_DURATION_SECONDS::VARCHAR
             FROM PROCEDURE_EXECUTION_LOG
             ORDER BY EXECUTION_START DESC LIMIT 1),
            'seconds'
        UNION ALL
        SELECT
            'Total Rows in All Tables',
            SUM(ROW_COUNT)::VARCHAR,
            'rows'
        FROM TABLE_REGISTRY
        UNION ALL
        SELECT
            'Execution Status',
            (SELECT STATUS FROM PROCEDURE_EXECUTION_LOG
             ORDER BY EXECUTION_START DESC LIMIT 1),
            ''
    """,

    'data_quality_checks': """
        SELECT
            '⚠️  Tables Without Columns' as CHECK_NAME,
            (SELECT COUNT(*)
             FROM TABLE_REGISTRY tr
             LEFT JOIN COLUMN_METADATA cm ON tr.TABLE_ID = cm.TABLE_ID
             WHERE cm.COLUMN_ID IS NULL) as ISSUE_COUNT
        UNION ALL
        SELECT
            '⚠️  Tables With Zero Rows',
            (SELECT COUNT(*) FROM TABLE_REGISTRY WHERE ROW_COUNT = 0 OR ROW_COUNT IS NULL)
        UNION ALL
        SELECT
            '⚠️  Columns Without Data Type',
            (SELECT COUNT(*) FROM COLUMN_METADATA WHERE DATA_TYPE IS NULL OR DATA_TYPE = '')
        UNION ALL
        SELECT
            '⚠️  Unknown Service Tables',
            (SELECT COUNT(*) FROM TABLE_REGISTRY WHERE SERVICE_NAME = 'Unknown')
    """,

    'expected_vs_actual': """
        WITH latest_log AS (
            SELECT
                STATUS,
                TABLES_PROCESSED,
                COLUMNS_PROCESSED,
                EXECUTION_DURATION_SECONDS,
                ERROR_MESSAGE
            FROM PROCEDURE_EXECUTION_LOG
            ORDER BY EXECUTION_START DESC
            LIMIT 1
        ),
        service_count AS (
            SELECT COUNT(DISTINCT SERVICE_NAME) as SERVICE_COUNT
            FROM TABLE_REGISTRY
        )
        SELECT
            'Execution Status' as CHECK,
            'SUCCESS' as EXPECTED,
            STATUS as ACTUAL,
            CASE WHEN STATUS = 'SUCCESS' THEN '✅ PASS' ELSE '❌ FAIL' END as RESULT
        FROM latest_log
        UNION ALL
        SELECT
            'Tables Processed Range',
            '10-30 tables',
            TABLES_PROCESSED::VARCHAR || ' tables',
            CASE
                WHEN TABLES_PROCESSED BETWEEN 10 AND 30 THEN '✅ PASS'
                WHEN TABLES_PROCESSED > 0 THEN '⚠️  ACCEPTABLE'
                ELSE '❌ FAIL'
            END
        FROM latest_log
        UNION ALL
        SELECT
            'Columns Processed Range',
            '100-500 columns',
            COLUMNS_PROCESSED::VARCHAR || ' columns',
            CASE
                WHEN COLUMNS_PROCESSED BETWEEN 100 AND 500 THEN '✅ PASS'
                WHEN COLUMNS_PROCESSED > 0 THEN '⚠️  ACCEPTABLE'
                ELSE '❌ FAIL'
            END
        FROM latest_log
        UNION ALL
        SELECT
            'Execution Duration',
            '< 30 seconds',
            EXECUTION_DURATION_SECONDS::VARCHAR || ' seconds',
            CASE
                WHEN EXECUTION_DURATION_SECONDS < 30 THEN '✅ PASS'
                ELSE '⚠️  WARNING'
            END
        FROM latest_log
        UNION ALL
        SELECT
            'Error Message',
            'NULL (no errors)',
            COALESCE(ERROR_MESSAGE, 'NULL'),
            CASE WHEN ERROR_MESSAGE IS NULL THEN '✅ PASS' ELSE '❌ FAIL' END
        FROM latest_log
        UNION ALL
        SELECT
            'Services Detected',
            '> 0 services',
            SERVICE_COUNT::VARCHAR || ' services',
            CASE WHEN SERVICE_COUNT > 0 THEN '✅ PASS' ELSE '❌ FAIL' END
        FROM service_count
    """
}

# ============================================================================
# Helper Functions
# ============================================================================

def create_output_directory():
    """Create output directory if it doesn't exist"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ Output directory: {OUTPUT_DIR}")


def connect_to_snowflake():
    """Establish connection to Snowflake"""
    try:
        print("🔌 Connecting to Snowflake...")
        conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
        print("✅ Connected successfully!")
        return conn
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        raise


def execute_query(conn, query_name, query_sql):
    """Execute a query and return results as DataFrame"""
    try:
        print(f"📊 Executing: {query_name}")
        df = pd.read_sql(query_sql, conn)
        print(f"   ✅ Retrieved {len(df)} rows")
        return df
    except Exception as e:
        print(f"   ❌ Query failed: {e}")
        return None


def save_to_csv(df, filename):
    """Save DataFrame to CSV file"""
    try:
        filepath = OUTPUT_DIR / f"{filename}.csv"
        df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"   💾 Saved: {filepath}")
        return True
    except Exception as e:
        print(f"   ❌ Failed to save CSV: {e}")
        return False


def save_to_json(df, filename):
    """Save DataFrame to JSON file"""
    try:
        filepath = OUTPUT_DIR / f"{filename}.json"
        df.to_json(filepath, orient='records', indent=2, date_format='iso')
        print(f"   💾 Saved: {filepath}")
        return True
    except Exception as e:
        print(f"   ❌ Failed to save JSON: {e}")
        return False


def create_summary_json(all_results):
    """Create a comprehensive summary JSON file"""
    try:
        summary = {
            'export_timestamp': datetime.now().isoformat(),
            'test_name': 'TEST_STORED_PROCEDURE',
            'results': {}
        }

        for query_name, df in all_results.items():
            if df is not None:
                summary['results'][query_name] = {
                    'row_count': len(df),
                    'columns': list(df.columns),
                    'data': df.to_dict(orient='records')
                }

        filepath = OUTPUT_DIR / 'test_results_complete.json'
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, default=str)

        print(f"✅ Created comprehensive summary: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Failed to create summary: {e}")
        return False


def print_test_summary(all_results):
    """Print a summary of test results to console"""
    print("\n" + "="*80)
    print("📈 TEST RESULTS SUMMARY")
    print("="*80)

    # Check if success criteria passed
    if 'success_criteria' in all_results and all_results['success_criteria'] is not None:
        df = all_results['success_criteria']
        print("\n✅ SUCCESS CRITERIA:")
        for _, row in df.iterrows():
            status_icon = "✅" if "PASS" in str(row['TEST_RESULT']) else "❌"
            print(f"   {status_icon} {row['CRITERIA']}: {row['ACTUAL_VALUE']}")

    # Print overall summary
    if 'overall_summary' in all_results and all_results['overall_summary'] is not None:
        df = all_results['overall_summary']
        print("\n📊 OVERALL STATISTICS:")
        for _, row in df.iterrows():
            print(f"   • {row['METRIC']}: {row['VALUE']} {row['UNIT']}")

    # Check data quality issues
    if 'data_quality_checks' in all_results and all_results['data_quality_checks'] is not None:
        df = all_results['data_quality_checks']
        issues = df[df['ISSUE_COUNT'] > 0]
        if len(issues) > 0:
            print("\n⚠️  DATA QUALITY ISSUES:")
            for _, row in issues.iterrows():
                print(f"   ⚠️  {row['CHECK_NAME']}: {row['ISSUE_COUNT']} issues")
        else:
            print("\n✅ NO DATA QUALITY ISSUES")

    print("\n" + "="*80)


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("🚀 STARTING TEST RESULTS EXPORT")
    print("="*80 + "\n")

    # Create output directory
    create_output_directory()

    # Connect to Snowflake
    conn = None
    try:
        conn = connect_to_snowflake()

        # Execute all queries and save results
        all_results = {}
        successful_exports = 0
        failed_exports = 0

        for query_name, query_sql in TEST_QUERIES.items():
            print(f"\n{'─'*80}")
            df = execute_query(conn, query_name, query_sql)

            if df is not None:
                all_results[query_name] = df

                # Save to both CSV and JSON
                csv_success = save_to_csv(df, query_name)
                json_success = save_to_json(df, query_name)

                if csv_success and json_success:
                    successful_exports += 1
                else:
                    failed_exports += 1
            else:
                failed_exports += 1
                all_results[query_name] = None

        # Create comprehensive summary JSON
        print(f"\n{'─'*80}")
        print("📦 Creating comprehensive summary...")
        create_summary_json(all_results)

        # Print summary to console
        print_test_summary(all_results)

        # Final status
        print(f"\n{'='*80}")
        print(f"✅ Export completed!")
        print(f"   • Successful: {successful_exports}/{len(TEST_QUERIES)}")
        print(f"   • Failed: {failed_exports}/{len(TEST_QUERIES)}")
        print(f"   • Output directory: {OUTPUT_DIR.absolute()}")
        print(f"{'='*80}\n")

    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        raise

    finally:
        if conn:
            conn.close()
            print("🔌 Snowflake connection closed")


if __name__ == "__main__":
    main()
