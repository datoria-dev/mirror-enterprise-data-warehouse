"""
================================================================================
Execute SQL Script with Automatic Result Export
================================================================================

Generic Python script to execute SQL scripts and automatically save all results
to CSV/JSON files for analysis.

This implements the best practice of always storing query results for:
- Post-execution analysis
- Audit trail
- Troubleshooting
- Documentation

Requirements:
    pip install snowflake-connector-python pandas

Usage:
    python run_sql_script.py --script CREATE_METADATA_REPOSITORY.sql
    python run_sql_script.py --script path/to/script.sql --output my_results

Date: 2025-10-24
================================================================================
"""

import snowflake.connector
import pandas as pd
import json
import os
import sys
import io
import argparse
from datetime import datetime
from pathlib import Path
import re

# Fix encoding issues for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ============================================================================
# Configuration
# ============================================================================

CONFIG_FILE = Path('snowflake_config.json')
DEFAULT_OUTPUT_DIR = Path('04_METADATA_SAMPLES/sql_execution_results')

# ============================================================================
# Helper Functions
# ============================================================================

def load_config():
    """Load Snowflake configuration from JSON file"""
    if not CONFIG_FILE.exists():
        print(f"❌ Config file not found: {CONFIG_FILE}")
        print(f"📝 Please ensure snowflake_config.json exists")
        sys.exit(1)

    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        print(f"✅ Loaded configuration from: {CONFIG_FILE}")
        return config
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        sys.exit(1)


def create_output_directory(output_dir):
    """Create output directory if it doesn't exist"""
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Output directory: {output_dir}")
    return output_dir


def connect_to_snowflake(config):
    """Establish connection to Snowflake using SSO (Okta)"""
    try:
        print("🔌 Connecting to Snowflake via SSO (Okta)...")
        print("   ⏳ A browser window will open for authentication...")
        conn = snowflake.connector.connect(**config)
        print("✅ Connected successfully!")
        return conn
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Ensure 'authenticator': 'externalbrowser' is in your config")
        print("   2. Check that your browser allows pop-ups from Snowflake")
        print("   3. Verify your Okta credentials are valid")
        raise


def read_sql_file(sql_file_path):
    """Read SQL file and split into individual statements"""
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print(f"✅ Read SQL file: {sql_file_path}")

        # Split by semicolons, but preserve semicolons in string literals and comments
        # This is a simple split - for complex SQL, might need more sophisticated parsing
        statements = []
        current_statement = []
        in_comment = False
        in_block_comment = False

        lines = sql_content.split('\n')
        for line in lines:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                continue

            # Handle comments
            if stripped.startswith('--'):
                continue
            if stripped.startswith('/*'):
                in_block_comment = True
            if '*/' in stripped:
                in_block_comment = False
                continue
            if in_block_comment:
                continue

            # Add line to current statement
            current_statement.append(line)

            # Check if statement ends with semicolon
            if stripped.endswith(';'):
                statement_text = '\n'.join(current_statement)
                if statement_text.strip():
                    statements.append(statement_text)
                current_statement = []

        # Add any remaining statement
        if current_statement:
            statement_text = '\n'.join(current_statement)
            if statement_text.strip():
                statements.append(statement_text)

        print(f"   📄 Parsed {len(statements)} SQL statements")
        return statements

    except Exception as e:
        print(f"❌ Failed to read SQL file: {e}")
        sys.exit(1)


def classify_statement(statement):
    """Classify SQL statement type"""
    statement_upper = statement.strip().upper()

    if statement_upper.startswith('SELECT'):
        return 'SELECT'
    elif statement_upper.startswith('INSERT'):
        return 'INSERT'
    elif statement_upper.startswith('UPDATE'):
        return 'UPDATE'
    elif statement_upper.startswith('DELETE'):
        return 'DELETE'
    elif statement_upper.startswith('CREATE'):
        return 'CREATE'
    elif statement_upper.startswith('DROP'):
        return 'DROP'
    elif statement_upper.startswith('ALTER'):
        return 'ALTER'
    elif statement_upper.startswith('CALL'):
        return 'CALL'
    elif statement_upper.startswith('USE'):
        return 'USE'
    else:
        return 'OTHER'


def execute_statement(conn, statement, statement_num, output_dir):
    """Execute a single SQL statement and save results if applicable"""
    try:
        stmt_type = classify_statement(statement)
        stmt_preview = statement.strip()[:100].replace('\n', ' ')

        print(f"\n{'─'*80}")
        print(f"📊 Statement {statement_num}: {stmt_type}")
        print(f"   Preview: {stmt_preview}...")

        cursor = conn.cursor()

        # Execute statement
        start_time = datetime.now()
        cursor.execute(statement)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Check if statement returns results
        if stmt_type in ['SELECT', 'CALL', 'SHOW', 'DESCRIBE', 'DESC']:
            try:
                # Fetch results
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []

                if results and columns:
                    # Create DataFrame
                    df = pd.DataFrame(results, columns=columns)
                    row_count = len(df)

                    print(f"   ✅ Retrieved {row_count} rows in {duration:.2f}s")

                    # Save to CSV and JSON
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    base_filename = f"stmt_{statement_num:03d}_{stmt_type.lower()}_{timestamp}"

                    csv_path = output_dir / f"{base_filename}.csv"
                    json_path = output_dir / f"{base_filename}.json"

                    df.to_csv(csv_path, index=False, encoding='utf-8')
                    df.to_json(json_path, orient='records', indent=2, date_format='iso')

                    print(f"   💾 Saved CSV: {csv_path.name}")
                    print(f"   💾 Saved JSON: {json_path.name}")

                    return {
                        'statement_num': statement_num,
                        'type': stmt_type,
                        'status': 'SUCCESS',
                        'duration': duration,
                        'rows': row_count,
                        'csv_file': csv_path.name,
                        'json_file': json_path.name,
                        'preview': stmt_preview
                    }
                else:
                    print(f"   ✅ Executed successfully in {duration:.2f}s (no results)")
                    return {
                        'statement_num': statement_num,
                        'type': stmt_type,
                        'status': 'SUCCESS',
                        'duration': duration,
                        'rows': 0,
                        'preview': stmt_preview
                    }
            except Exception as e:
                # Statement executed but didn't return results (DDL/DML)
                print(f"   ✅ Executed successfully in {duration:.2f}s")
                return {
                    'statement_num': statement_num,
                    'type': stmt_type,
                    'status': 'SUCCESS',
                    'duration': duration,
                    'rows': None,
                    'preview': stmt_preview
                }
        else:
            # DDL/DML statements
            row_count = cursor.rowcount if cursor.rowcount >= 0 else None
            print(f"   ✅ Executed successfully in {duration:.2f}s")
            if row_count is not None and row_count > 0:
                print(f"   📝 Affected rows: {row_count}")

            return {
                'statement_num': statement_num,
                'type': stmt_type,
                'status': 'SUCCESS',
                'duration': duration,
                'rows': row_count,
                'preview': stmt_preview
            }

    except Exception as e:
        print(f"   ❌ Execution failed: {e}")
        return {
            'statement_num': statement_num,
            'type': stmt_type,
            'status': 'FAILED',
            'duration': 0,
            'error': str(e),
            'preview': stmt_preview
        }
    finally:
        cursor.close()


def create_execution_summary(execution_results, output_dir, script_name):
    """Create a comprehensive execution summary"""
    try:
        summary = {
            'script_name': script_name,
            'execution_timestamp': datetime.now().isoformat(),
            'total_statements': len(execution_results),
            'successful_statements': len([r for r in execution_results if r['status'] == 'SUCCESS']),
            'failed_statements': len([r for r in execution_results if r['status'] == 'FAILED']),
            'total_duration_seconds': sum(r['duration'] for r in execution_results),
            'statements': execution_results
        }

        # Save summary as JSON
        summary_path = output_dir / 'execution_summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, default=str)

        print(f"\n✅ Created execution summary: {summary_path}")

        # Create summary DataFrame
        summary_df = pd.DataFrame(execution_results)
        summary_csv = output_dir / 'execution_summary.csv'
        summary_df.to_csv(summary_csv, index=False, encoding='utf-8')

        print(f"✅ Created execution summary CSV: {summary_csv}")

        return summary

    except Exception as e:
        print(f"❌ Failed to create summary: {e}")
        return None


def print_execution_summary(summary):
    """Print execution summary to console"""
    print("\n" + "="*80)
    print("📈 EXECUTION SUMMARY")
    print("="*80)

    print(f"\n📄 Script: {summary['script_name']}")
    print(f"🕐 Timestamp: {summary['execution_timestamp']}")
    print(f"⏱️  Total Duration: {summary['total_duration_seconds']:.2f} seconds")

    print(f"\n📊 Statement Summary:")
    print(f"   • Total Statements: {summary['total_statements']}")
    print(f"   • ✅ Successful: {summary['successful_statements']}")
    print(f"   • ❌ Failed: {summary['failed_statements']}")

    # Show failures if any
    failed = [s for s in summary['statements'] if s['status'] == 'FAILED']
    if failed:
        print(f"\n❌ FAILED STATEMENTS:")
        for stmt in failed:
            print(f"   Statement {stmt['statement_num']}: {stmt['type']}")
            print(f"   Error: {stmt.get('error', 'Unknown error')}")
            print(f"   Preview: {stmt['preview']}")

    # Show statements with results
    with_results = [s for s in summary['statements'] if s.get('csv_file')]
    if with_results:
        print(f"\n💾 STATEMENTS WITH SAVED RESULTS ({len(with_results)}):")
        for stmt in with_results:
            print(f"   Statement {stmt['statement_num']}: {stmt['rows']} rows")
            print(f"      CSV: {stmt['csv_file']}")
            print(f"      JSON: {stmt['json_file']}")

    print("\n" + "="*80)


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Main execution function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Execute SQL script and save results')
    parser.add_argument('--script', required=True, help='Path to SQL script file')
    parser.add_argument('--output', help='Output directory name (optional)')
    args = parser.parse_args()

    print("\n" + "="*80)
    print("🚀 SQL SCRIPT EXECUTION WITH AUTO-EXPORT")
    print("="*80 + "\n")

    # Setup
    script_path = Path(args.script)
    if not script_path.exists():
        print(f"❌ SQL script not found: {script_path}")
        sys.exit(1)

    # Create output directory
    if args.output:
        output_dir = DEFAULT_OUTPUT_DIR / args.output
    else:
        # Use script name and timestamp as directory name
        script_name = script_path.stem
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = DEFAULT_OUTPUT_DIR / f"{script_name}_{timestamp}"

    create_output_directory(output_dir)

    # Load configuration
    config = load_config()

    # Read SQL file
    statements = read_sql_file(script_path)

    # Connect to Snowflake
    conn = None
    try:
        conn = connect_to_snowflake(config)

        # Execute all statements
        execution_results = []
        for i, statement in enumerate(statements, 1):
            result = execute_statement(conn, statement, i, output_dir)
            execution_results.append(result)

            # Stop if critical failure (optional - can be configured)
            # if result['status'] == 'FAILED':
            #     print("\n❌ Stopping execution due to failure")
            #     break

        # Create execution summary
        summary = create_execution_summary(execution_results, output_dir, script_path.name)

        # Print summary
        if summary:
            print_execution_summary(summary)

        # Final status
        print(f"\n{'='*80}")
        if summary['failed_statements'] == 0:
            print(f"✅ All statements executed successfully!")
        else:
            print(f"⚠️  Execution completed with {summary['failed_statements']} failure(s)")
        print(f"   📁 Results saved to: {output_dir.absolute()}")
        print(f"{'='*80}\n")

    except Exception as e:
        print(f"\n❌ Execution error: {e}")
        sys.exit(1)

    finally:
        if conn:
            conn.close()
            print("🔌 Snowflake connection closed")


if __name__ == "__main__":
    main()
