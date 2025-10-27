"""
Snowflake Query Results Capturer - Enhanced to handle stored procedures correctly
"""

import snowflake.connector
import json
import sys
import re
from datetime import datetime
from pathlib import Path

# Your Snowflake connection details
ACCOUNT = 'mw76572.east-us-2.azure'  # From your screenshot: Account locator + region
USER = 'FUAD.ONATE@CompanyX.COM'

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
        stripped = line.strip()
        if stripped.startswith('--') and not current_stmt:
            continue

        # Track if we're starting a procedure/function
        upper_line = line.upper().strip()
        if not in_procedure and (
            'CREATE OR REPLACE PROCEDURE' in upper_line or
            'CREATE PROCEDURE' in upper_line or
            'CREATE OR REPLACE FUNCTION' in upper_line or
            'CREATE FUNCTION' in upper_line
        ):
            in_procedure = True

        # Add line to current statement
        current_stmt.append(line)

        # Track BEGIN/END blocks and strings
        i = 0
        while i < len(line):
            char = line[i]

            # Handle string literals
            if char in ("'", '"'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    # Check if it's escaped
                    if i + 1 < len(line) and line[i + 1] == char:
                        i += 1  # Skip escaped quote
                    else:
                        in_string = False
                        string_char = None

            # Only count BEGIN/END outside of strings
            if not in_string:
                # Check for BEGIN keyword
                if i + 5 <= len(line):
                    word = line[i:i+5].upper()
                    if word == 'BEGIN':
                        # Make sure it's a whole word
                        before_ok = (i == 0 or not line[i-1].isalnum())
                        after_ok = (i + 5 >= len(line) or not line[i+5].isalnum())
                        if before_ok and after_ok:
                            begin_count += 1
                            i += 4  # Skip ahead

                # Check for END keyword
                if i + 3 <= len(line):
                    word = line[i:i+3].upper()
                    if word == 'END':
                        # Make sure it's a whole word
                        before_ok = (i == 0 or not line[i-1].isalnum())
                        after_ok = (i + 3 >= len(line) or not line[i+3].isalnum())
                        if before_ok and after_ok:
                            begin_count -= 1

                # Check for semicolon - statement separator
                if char == ';':
                    # If we're in a procedure and still have open BEGIN blocks, don't split
                    if in_procedure and begin_count > 0:
                        pass  # Keep going, this is an internal semicolon
                    else:
                        # This is a statement terminator
                        stmt_text = '\n'.join(current_stmt).strip()
                        if stmt_text:
                            statements.append(stmt_text)
                        current_stmt = []
                        in_procedure = False
                        begin_count = 0

            i += 1

    # Add any remaining statement
    if current_stmt:
        stmt_text = '\n'.join(current_stmt).strip()
        if stmt_text and not stmt_text.startswith('--'):
            statements.append(stmt_text)

    return statements


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

    # Use smart split that handles procedures
    statements = smart_split_sql(sql_content)

    print(f"Executing {len(statements)} statements...\n")

    results = {
        'file': sql_file,
        'executed_at': datetime.now().isoformat(),
        'statements': []
    }

    cursor = conn.cursor()

    for i, stmt in enumerate(statements, 1):
        # Show first line of statement for context
        first_line = stmt.split('\n')[0][:80]
        print(f"[{i}/{len(statements)}] {first_line}...", end=" ")

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
        print("Usage: python capture_results_enhanced.py EXECUTE_4_ENHANCEMENTS_WORKING.sql")
        sys.exit(1)

    execute_and_capture(sys.argv[1])
