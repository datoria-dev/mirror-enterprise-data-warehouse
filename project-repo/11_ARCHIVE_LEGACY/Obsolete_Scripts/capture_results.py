"""
Snowflake Query Results Capturer
=================================
This script executes SQL files and saves results to JSON for later review.

Usage:
    python capture_results.py VERIFY_SIMPLE.sql
"""

import snowflake.connector
import os
import sys
import json
from datetime import datetime
from pathlib import Path

def execute_and_capture(sql_file):
    """Execute SQL file and capture all results"""

    # Read connection info
    account = os.getenv('SNOWFLAKE_ACCOUNT', 'GenericCorp-CRH_LEDW')
    user = os.getenv('SNOWFLAKE_USER', 'FUAD.ONATE@CompanyX.COM')

    print(f"Connecting to Snowflake...")
    print(f"Account: {account}")
    print(f"User: {user}")

    try:
        # Connect with SSO
        conn = snowflake.connector.connect(
            account=account,
            user=user,
            authenticator='externalbrowser',
            warehouse='DEV_WH',
            database='DEV_REPORTING',
            schema='SECURITY_ANALYTICS'
        )
        print("✓ Connected successfully")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return None

    # Read SQL file
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Split into statements
    statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]

    print(f"\nExecuting {len(statements)} SQL statements...")

    results = {
        'file': sql_file,
        'executed_at': datetime.now().isoformat(),
        'account': account,
        'user': user,
        'statements': []
    }

    cursor = conn.cursor()

    for i, stmt in enumerate(statements, 1):
        if not stmt or stmt.startswith('--'):
            continue

        print(f"\n[{i}/{len(statements)}] Executing...")

        stmt_result = {
            'statement_number': i,
            'sql': stmt[:200] + '...' if len(stmt) > 200 else stmt,
            'success': False,
            'rows': [],
            'row_count': 0,
            'columns': [],
            'error': None
        }

        try:
            cursor.execute(stmt)

            # Get column names
            if cursor.description:
                stmt_result['columns'] = [col[0] for col in cursor.description]

                # Fetch all rows
                rows = cursor.fetchall()
                stmt_result['row_count'] = len(rows)

                # Convert rows to list of dicts (limit to 100 rows)
                for row in rows[:100]:
                    row_dict = {}
                    for col_name, value in zip(stmt_result['columns'], row):
                        # Convert datetime to string
                        if hasattr(value, 'isoformat'):
                            row_dict[col_name] = value.isoformat()
                        else:
                            row_dict[col_name] = str(value) if value is not None else None
                    stmt_result['rows'].append(row_dict)

                if len(rows) > 100:
                    stmt_result['note'] = f'Showing first 100 of {len(rows)} rows'

            stmt_result['success'] = True
            print(f"  ✓ Success - {stmt_result['row_count']} rows")

        except Exception as e:
            stmt_result['error'] = str(e)
            print(f"  ✗ Error: {e}")

        results['statements'].append(stmt_result)

    cursor.close()
    conn.close()

    # Save to JSON
    output_file = f"results_{Path(sql_file).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_path = Path('QUERY_RESULTS') / output_file
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Results saved to: {output_path}")

    # Also save a summary
    summary_file = Path('QUERY_RESULTS') / 'latest_summary.txt'
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"=== Execution Summary ===\n")
        f.write(f"File: {sql_file}\n")
        f.write(f"Executed: {results['executed_at']}\n")
        f.write(f"Total Statements: {len(statements)}\n")
        f.write(f"Successful: {sum(1 for s in results['statements'] if s['success'])}\n")
        f.write(f"Failed: {sum(1 for s in results['statements'] if not s['success'])}\n\n")

        for stmt in results['statements']:
            f.write(f"\n--- Statement {stmt['statement_number']} ---\n")
            f.write(f"SQL: {stmt['sql']}\n")
            f.write(f"Status: {'✓ SUCCESS' if stmt['success'] else '✗ FAILED'}\n")
            if stmt['success']:
                f.write(f"Rows returned: {stmt['row_count']}\n")
                if stmt['rows']:
                    f.write(f"First row: {stmt['rows'][0]}\n")
            else:
                f.write(f"Error: {stmt['error']}\n")

    print(f"✓ Summary saved to: {summary_file}")

    return output_path

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python capture_results.py <sql_file>")
        sys.exit(1)

    sql_file = sys.argv[1]

    if not os.path.exists(sql_file):
        print(f"Error: File not found: {sql_file}")
        sys.exit(1)

    result = execute_and_capture(sql_file)

    if result:
        print(f"\n✓ Done! Results saved to: {result}")
        sys.exit(0)
    else:
        sys.exit(1)
