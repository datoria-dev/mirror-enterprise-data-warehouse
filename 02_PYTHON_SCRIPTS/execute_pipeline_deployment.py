"""
Execute Data Pipeline Deployment for SECURITY_ANALYTICS
Deploys Snowpipe, Tasks, Streams, and External Tables to Snowflake

Author: Data Engineering Team
Date: 2025-10-07
"""

import snowflake.connector
import json
import sys
from datetime import datetime

# Force UTF-8 encoding for console output (Windows compatibility)
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# =====================================================================
# SNOWFLAKE CONNECTION PARAMETERS
# =====================================================================

SNOWFLAKE_CONFIG = {
    'account': 'mw76572.east-us-2.azure',
    'user': 'FUAD.ONATE@CompanyX.COM',
    'authenticator': 'externalbrowser',  # SSO
    'warehouse': 'DEV_WH',
    'database': 'DEV_TRANSFORMATION',
    'schema': 'SECURITY_ANALYTICS',
    'role': 'DEV_DEVELOPER'
}

# =====================================================================
# SMART SQL STATEMENT PARSER
# =====================================================================

def smart_split_sql(sql_content):
    """
    Split SQL into statements while respecting stored procedure bodies.
    Handles CREATE PROCEDURE, CREATE FUNCTION, and nested BEGIN/END blocks.
    """
    statements = []
    current_stmt = []
    in_procedure = False
    begin_count = 0
    in_string = False
    string_char = None

    lines = sql_content.split('\n')

    for line in lines:
        # Skip pure comment lines
        if line.strip().startswith('--'):
            continue

        # Skip multi-line comment blocks
        if line.strip().startswith('/*') or line.strip().endswith('*/'):
            continue

        # Skip empty lines
        if not line.strip():
            continue

        upper_line = line.upper()

        # Track if we're starting a procedure/function
        if 'CREATE OR REPLACE PROCEDURE' in upper_line or 'CREATE PROCEDURE' in upper_line:
            in_procedure = True
        elif 'CREATE OR REPLACE FUNCTION' in upper_line or 'CREATE FUNCTION' in upper_line:
            in_procedure = True
        elif 'CREATE OR REPLACE TASK' in upper_line or 'CREATE TASK' in upper_line:
            in_procedure = True  # Tasks can have AS BEGIN...END blocks

        # Track BEGIN/END depth
        if 'BEGIN' in upper_line and not in_string:
            begin_count += upper_line.count('BEGIN')
        if 'END;' in upper_line and not in_string:
            begin_count -= upper_line.count('END')

        # Add line to current statement
        current_stmt.append(line)

        # Check if statement is complete
        if ';' in line:
            # Only split on semicolon if we're not in a procedure or all BEGINs are closed
            if not in_procedure or begin_count == 0:
                stmt_text = '\n'.join(current_stmt).strip()
                if stmt_text and not stmt_text.startswith('--'):
                    statements.append(stmt_text)
                current_stmt = []
                in_procedure = False
                begin_count = 0

    # Add any remaining statement
    if current_stmt:
        stmt_text = '\n'.join(current_stmt).strip()
        if stmt_text and not stmt_text.startswith('--'):
            statements.append(stmt_text)

    return statements

# =====================================================================
# EXECUTE SQL WITH DETAILED LOGGING
# =====================================================================

def execute_pipeline_deployment(sql_file_path, output_json_path):
    """
    Execute pipeline deployment SQL and save detailed results
    """
    print("=" * 80)
    print("DATA PIPELINE DEPLOYMENT FOR SECURITY_ANALYTICS")
    print("=" * 80)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"SQL File: {sql_file_path}")
    print(f"Output JSON: {output_json_path}")

    # Read SQL file
    print(f"\nReading SQL file: {sql_file_path}")
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Parse SQL into statements
    print("Parsing SQL statements...")
    statements = smart_split_sql(sql_content)
    print(f"Found {len(statements)} SQL statements to execute")

    # Connect to Snowflake
    print(f"\n{'=' * 80}")
    print("CONNECTING TO SNOWFLAKE")
    print(f"{'=' * 80}")
    print(f"Account: {SNOWFLAKE_CONFIG['account']}")
    print(f"User: {SNOWFLAKE_CONFIG['user']}")
    print(f"Warehouse: {SNOWFLAKE_CONFIG['warehouse']}")
    print(f"Database: {SNOWFLAKE_CONFIG['database']}")
    print(f"Schema: {SNOWFLAKE_CONFIG['schema']}")

    try:
        conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
        cursor = conn.cursor()
        print("✓ Connected successfully")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return

    # Execute statements
    results = {
        'file': sql_file_path,
        'executed_at': datetime.now().isoformat(),
        'connection': SNOWFLAKE_CONFIG,
        'statements': []
    }

    success_count = 0
    error_count = 0
    warning_count = 0

    print(f"\n{'=' * 80}")
    print("EXECUTING PIPELINE DEPLOYMENT")
    print(f"{'=' * 80}\n")

    for idx, stmt in enumerate(statements, 1):
        # Extract statement type for logging
        stmt_upper = stmt.upper().strip()
        stmt_type = "UNKNOWN"

        if "CREATE OR REPLACE STORAGE INTEGRATION" in stmt_upper:
            stmt_type = "STORAGE_INTEGRATION"
        elif "CREATE OR REPLACE FILE FORMAT" in stmt_upper:
            stmt_type = "FILE_FORMAT"
        elif "CREATE OR REPLACE STAGE" in stmt_upper:
            stmt_type = "STAGE"
        elif "CREATE OR REPLACE EXTERNAL TABLE" in stmt_upper:
            stmt_type = "EXTERNAL_TABLE"
        elif "CREATE OR REPLACE TABLE" in stmt_upper:
            stmt_type = "TABLE"
        elif "CREATE OR REPLACE PIPE" in stmt_upper:
            stmt_type = "SNOWPIPE"
        elif "CREATE OR REPLACE STREAM" in stmt_upper:
            stmt_type = "STREAM"
        elif "CREATE OR REPLACE PROCEDURE" in stmt_upper:
            stmt_type = "PROCEDURE"
        elif "CREATE OR REPLACE TASK" in stmt_upper:
            stmt_type = "TASK"
        elif "ALTER TASK" in stmt_upper and "RESUME" in stmt_upper:
            stmt_type = "TASK_RESUME"
        elif "USE ROLE" in stmt_upper:
            stmt_type = "USE_ROLE"
        elif "USE WAREHOUSE" in stmt_upper:
            stmt_type = "USE_WAREHOUSE"
        elif "USE DATABASE" in stmt_upper:
            stmt_type = "USE_DATABASE"
        elif "USE SCHEMA" in stmt_upper:
            stmt_type = "USE_SCHEMA"

        print(f"[{idx}/{len(statements)}] Executing {stmt_type}...")

        # Show snippet of SQL
        stmt_preview = stmt[:100].replace('\n', ' ')
        if len(stmt) > 100:
            stmt_preview += "..."
        print(f"    SQL: {stmt_preview}")

        try:
            cursor.execute(stmt)

            # Fetch results if available
            rows = []
            try:
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    for row in cursor:
                        row_dict = dict(zip(columns, row))
                        # Convert datetime objects to strings
                        for key, value in row_dict.items():
                            if hasattr(value, 'isoformat'):
                                row_dict[key] = value.isoformat()
                        rows.append(row_dict)
            except Exception:
                pass

            row_count = cursor.rowcount if cursor.rowcount >= 0 else len(rows)

            # Determine if this is a DDL statement (no rows expected)
            is_ddl = stmt_type in ['STORAGE_INTEGRATION', 'FILE_FORMAT', 'STAGE',
                                   'TABLE', 'EXTERNAL_TABLE', 'SNOWPIPE', 'STREAM',
                                   'PROCEDURE', 'TASK', 'TASK_RESUME']

            if is_ddl:
                print(f"    ✓ SUCCESS - {stmt_type} created/modified")
            else:
                print(f"    ✓ SUCCESS - {row_count} rows affected")

            results['statements'].append({
                'num': idx,
                'type': stmt_type,
                'sql': stmt[:500],  # Truncate for JSON size
                'success': True,
                'rows': rows[:100] if rows else [],  # Limit rows in JSON
                'row_count': row_count,
                'error': None
            })

            success_count += 1

        except Exception as e:
            error_msg = str(e)
            print(f"    ✗ ERROR: {error_msg}")

            results['statements'].append({
                'num': idx,
                'type': stmt_type,
                'sql': stmt[:500],
                'success': False,
                'rows': [],
                'row_count': 0,
                'error': error_msg
            })

            error_count += 1

            # Check if this is a critical error or expected warning
            if "already exists" in error_msg.lower():
                warning_count += 1
            elif "does not exist" in error_msg.lower() and "DROP" in stmt_upper:
                warning_count += 1

        print()  # Blank line between statements

    # Close connection
    cursor.close()
    conn.close()

    # Save results to JSON
    print(f"{'=' * 80}")
    print("SAVING RESULTS")
    print(f"{'=' * 80}")
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"✓ Results saved to: {output_json_path}")

    # Print summary
    print(f"\n{'=' * 80}")
    print("DEPLOYMENT SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total Statements:  {len(statements)}")
    print(f"✓ Successful:      {success_count}")
    print(f"✗ Failed:          {error_count}")
    print(f"⚠ Warnings:        {warning_count}")
    print(f"Success Rate:      {(success_count / len(statements) * 100):.1f}%")

    # Object type breakdown
    print(f"\n{'=' * 80}")
    print("OBJECTS DEPLOYED")
    print(f"{'=' * 80}")

    object_counts = {}
    for stmt_result in results['statements']:
        stmt_type = stmt_result['type']
        if stmt_type not in object_counts:
            object_counts[stmt_type] = {'success': 0, 'failed': 0}

        if stmt_result['success']:
            object_counts[stmt_type]['success'] += 1
        else:
            object_counts[stmt_type]['failed'] += 1

    for obj_type, counts in sorted(object_counts.items()):
        total = counts['success'] + counts['failed']
        status = "✓" if counts['failed'] == 0 else "⚠"
        print(f"{status} {obj_type:20} {counts['success']}/{total} successful")

    print(f"\n{'=' * 80}")
    print("PIPELINE DEPLOYMENT COMPLETE")
    print(f"{'=' * 80}")

    if error_count > 0:
        print(f"\n⚠ WARNING: {error_count} errors occurred. Review the JSON output for details.")
        print(f"\nCommon issues:")
        print(f"  - Storage Integrations require ACCOUNTADMIN role")
        print(f"  - External Stages require valid S3/Azure credentials")
        print(f"  - Snowpipes require SNS topic configuration")
        print(f"  - Tasks require EXECUTE TASK privilege")
    else:
        print(f"\n✓ All pipeline objects deployed successfully!")
        print(f"\nNext steps:")
        print(f"  1. Configure S3/Azure event notifications for Snowpipe")
        print(f"  2. Resume tasks (requires ACCOUNTADMIN or EXECUTE TASK privilege)")
        print(f"  3. Verify Snowpipe ingestion: SELECT * FROM TABLE(INFORMATION_SCHEMA.PIPE_USAGE_HISTORY())")
        print(f"  4. Monitor task execution: SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())")

    return results

# =====================================================================
# MAIN EXECUTION
# =====================================================================

if __name__ == "__main__":
    # Accept SQL file as command-line argument, default to full architecture
    if len(sys.argv) > 1:
        sql_file = sys.argv[1]
    else:
        sql_file = "DATA_PIPELINE_ARCHITECTURE.sql"

    # Accept output file as second argument, or generate timestamp-based name
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        base_name = sql_file.replace('.sql', '').replace('PIPELINE_', '').replace('_', '')
        output_file = f"QUERY_RESULTS/results_{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    try:
        results = execute_pipeline_deployment(sql_file, output_file)

        # Return exit code based on success
        if results:
            error_count = sum(1 for stmt in results['statements'] if not stmt['success'])
            sys.exit(1 if error_count > 0 else 0)
        else:
            sys.exit(1)

    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
