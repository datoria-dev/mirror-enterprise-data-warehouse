"""
Snowflake Query Results Capturer - FIXED for Azure
"""

import snowflake.connector
import json
import sys
from datetime import datetime
from pathlib import Path

# Your Snowflake connection details
ACCOUNT = 'mw76572.east-us-2.azure'  # From your screenshot: Account locator + region
USER = 'FUAD.ONATE@CompanyX.COM'

def execute_and_capture(sql_file):
    print(f"Connecting to Snowflake...")
    print(f"Account: {ACCOUNT}")
    print(f"User: {USER}")

    try:
        conn = snowflake.connector.connect(
            account=ACCOUNT,
            user=USER,
            authenticator='externalbrowser',  # SSO
            warehouse='DEV_WH',
            role='DEV_DEVELOPER'
        )
        print("✓ Connected successfully\n")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return None

    # Read SQL
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]

    print(f"Executing {len(statements)} statements...\n")

    results = {
        'file': sql_file,
        'executed_at': datetime.now().isoformat(),
        'statements': []
    }

    cursor = conn.cursor()

    for i, stmt in enumerate(statements, 1):
        print(f"[{i}/{len(statements)}]", end=" ")

        stmt_result = {
            'num': i,
            'sql': stmt[:100] + '...' if len(stmt) > 100 else stmt,
            'success': False,
            'rows': [],
            'error': None
        }

        try:
            cursor.execute(stmt)

            if cursor.description:
                cols = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

                # Convert to dicts (max 50 rows)
                for row in rows[:50]:
                    row_dict = {}
                    for col, val in zip(cols, row):
                        if hasattr(val, 'isoformat'):
                            row_dict[col] = val.isoformat()
                        else:
                            row_dict[col] = str(val) if val is not None else None
                    stmt_result['rows'].append(row_dict)

                stmt_result['row_count'] = len(rows)

            stmt_result['success'] = True
            print(f"✓ {stmt_result.get('row_count', 0)} rows")

        except Exception as e:
            stmt_result['error'] = str(e)
            print(f"✗ {e}")

        results['statements'].append(stmt_result)

    cursor.close()
    conn.close()

    # Save JSON
    output_dir = Path('QUERY_RESULTS')
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f"results_{Path(sql_file).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Results saved: {output_file}")

    # Summary
    summary = output_dir / 'latest_summary.txt'
    with open(summary, 'w', encoding='utf-8') as f:
        f.write(f"File: {sql_file}\n")
        f.write(f"Time: {results['executed_at']}\n")
        f.write(f"Success: {sum(1 for s in results['statements'] if s['success'])}/{len(statements)}\n\n")

        for s in results['statements']:
            f.write(f"\n[{s['num']}] {'✓' if s['success'] else '✗'}\n")
            f.write(f"SQL: {s['sql']}\n")
            if s['success'] and s['rows']:
                f.write(f"Rows: {s.get('row_count', 0)}\n")
                f.write(f"Sample: {s['rows'][0]}\n")
            elif not s['success']:
                f.write(f"Error: {s['error']}\n")

    print(f"✓ Summary saved: {summary}\n")
    return output_file

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python capture_results_fixed.py VERIFY_SIMPLE.sql")
        sys.exit(1)

    execute_and_capture(sys.argv[1])
