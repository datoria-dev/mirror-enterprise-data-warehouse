"""
================================================================================
Execute Verification Scripts with Intelligent Result Export
================================================================================

This script executes SQL verification scripts and automatically:
- Separates SELECT queries from other statements
- Executes each CHECK separately
- Saves all SELECT results to CSV/JSON
- Creates a comprehensive verification report
- Handles SHOW commands specially (like SHOW PROCEDURES)

Perfect for verification scripts that have multiple CHECK sections.

Requirements:
    pip install snowflake-connector-python pandas

Usage:
    python run_verification_script.py --script VERIFY_PROCEDURE_RECREATION.sql
    python run_verification_script.py --script path/to/verify.sql --output my_verification

Date: 2025-10-24
================================================================================
"""

import snowflake.connector
import pandas as pd
import json
import os
import sys
import io

# Fix encoding issues for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import argparse
from datetime import datetime
from pathlib import Path
import re

# ============================================================================
# Configuration
# ============================================================================

CONFIG_FILE = Path('snowflake_config.json')
DEFAULT_OUTPUT_DIR = Path('04_METADATA_SAMPLES/verification_results')

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
        raise


def parse_verification_script(sql_file_path):
    """
    Parse verification script into CHECK sections
    Each CHECK is a logical group of related queries
    """
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"✅ Read SQL file: {sql_file_path}")

        # Split by CHECK headers (lines with multiple ===)
        check_pattern = r'-- =+\s*\n-- (CHECK \d+.*?)\n-- =+'
        checks = re.split(check_pattern, content)

        # Parse into structured format
        parsed_checks = []
        check_num = 0

        # First part is usually USE statements and setup
        if checks[0].strip():
            setup_queries = extract_queries(checks[0])
            if setup_queries:
                parsed_checks.append({
                    'check_num': 0,
                    'check_name': 'SETUP',
                    'queries': setup_queries
                })

        # Process each CHECK section
        for i in range(1, len(checks), 2):
            if i + 1 < len(checks):
                check_name = checks[i].strip()
                check_content = checks[i + 1].strip()

                if check_content:
                    check_num += 1
                    queries = extract_queries(check_content)

                    if queries:
                        parsed_checks.append({
                            'check_num': check_num,
                            'check_name': check_name,
                            'queries': queries
                        })

        print(f"   📄 Parsed {len(parsed_checks)} CHECK sections with {sum(len(c['queries']) for c in parsed_checks)} total queries")
        return parsed_checks

    except Exception as e:
        print(f"❌ Failed to read SQL file: {e}")
        sys.exit(1)


def extract_queries(content):
    """Extract individual SQL queries from content"""
    queries = []
    current_query = []
    in_comment = False

    for line in content.split('\n'):
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            continue

        # Skip single-line comments
        if stripped.startswith('--'):
            continue

        # Skip block comments
        if stripped.startswith('/*'):
            in_comment = True
        if '*/' in stripped:
            in_comment = False
            continue
        if in_comment:
            continue

        # Add line to current query
        current_query.append(line)

        # Check if query ends with semicolon
        if stripped.endswith(';'):
            query_text = '\n'.join(current_query)
            if query_text.strip():
                queries.append(query_text)
            current_query = []

    # Add any remaining query
    if current_query:
        query_text = '\n'.join(current_query)
        if query_text.strip() and not query_text.strip().startswith('--'):
            queries.append(query_text)

    return queries


def classify_query(query):
    """Classify SQL query type"""
    query_upper = query.strip().upper()

    if query_upper.startswith('SELECT'):
        return 'SELECT'
    elif query_upper.startswith('SHOW'):
        return 'SHOW'
    elif query_upper.startswith('USE'):
        return 'USE'
    elif query_upper.startswith('WITH'):
        return 'SELECT'  # CTEs are SELECT queries
    else:
        return 'OTHER'


def execute_check(conn, check, output_dir):
    """Execute a single CHECK section and save results"""
    check_num = check['check_num']
    check_name = check['check_name']
    queries = check['queries']

    print(f"\n{'═'*80}")
    print(f"🔍 {check_name}")
    print(f"{'═'*80}")

    check_results = []
    last_show_query_id = None

    for query_idx, query in enumerate(queries, 1):
        query_type = classify_query(query)
        query_preview = query.strip()[:100].replace('\n', ' ')

        print(f"\n   Query {query_idx}/{len(queries)}: {query_type}")
        print(f"   Preview: {query_preview}...")

        try:
            cursor = conn.cursor()
            start_time = datetime.now()

            # Execute query
            cursor.execute(query)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Try to fetch results
            try:
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []

                if results and columns:
                    df = pd.DataFrame(results, columns=columns)
                    row_count = len(df)

                    print(f"   ✅ Retrieved {row_count} rows in {duration:.2f}s")

                    # Save results
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    safe_check_name = re.sub(r'[^\w\s-]', '', check_name).replace(' ', '_')[:50]
                    base_filename = f"check_{check_num:02d}_{safe_check_name}_query_{query_idx}"

                    csv_path = output_dir / f"{base_filename}.csv"
                    json_path = output_dir / f"{base_filename}.json"

                    df.to_csv(csv_path, index=False, encoding='utf-8')
                    df.to_json(json_path, orient='records', indent=2, date_format='iso')

                    print(f"   💾 Saved: {csv_path.name}")
                    print(f"   💾 Saved: {json_path.name}")

                    check_results.append({
                        'check_num': check_num,
                        'check_name': check_name,
                        'query_num': query_idx,
                        'query_type': query_type,
                        'status': 'SUCCESS',
                        'duration': duration,
                        'rows': row_count,
                        'columns': len(columns),
                        'csv_file': csv_path.name,
                        'json_file': json_path.name,
                        'preview': query_preview
                    })

                    # Store query ID for potential RESULT_SCAN
                    if query_type == 'SHOW':
                        last_show_query_id = cursor.sfqid

                else:
                    print(f"   ✅ Executed successfully in {duration:.2f}s (no results)")
                    check_results.append({
                        'check_num': check_num,
                        'check_name': check_name,
                        'query_num': query_idx,
                        'query_type': query_type,
                        'status': 'SUCCESS',
                        'duration': duration,
                        'rows': 0,
                        'preview': query_preview
                    })

            except Exception as e:
                # Query executed but no results (DDL/DML)
                print(f"   ✅ Executed successfully in {duration:.2f}s")
                check_results.append({
                    'check_num': check_num,
                    'check_name': check_name,
                    'query_num': query_idx,
                    'query_type': query_type,
                    'status': 'SUCCESS',
                    'duration': duration,
                    'preview': query_preview
                })

            cursor.close()

        except Exception as e:
            print(f"   ❌ Execution failed: {e}")
            check_results.append({
                'check_num': check_num,
                'check_name': check_name,
                'query_num': query_idx,
                'query_type': query_type,
                'status': 'FAILED',
                'error': str(e),
                'preview': query_preview
            })

    return check_results


def create_verification_summary(all_results, output_dir, script_name):
    """Create comprehensive verification summary"""
    try:
        summary = {
            'script_name': script_name,
            'execution_timestamp': datetime.now().isoformat(),
            'total_checks': len(set(r['check_num'] for r in all_results)),
            'total_queries': len(all_results),
            'successful_queries': len([r for r in all_results if r['status'] == 'SUCCESS']),
            'failed_queries': len([r for r in all_results if r['status'] == 'FAILED']),
            'total_duration_seconds': sum(r.get('duration', 0) for r in all_results),
            'checks': []
        }

        # Group by check
        checks = {}
        for result in all_results:
            check_num = result['check_num']
            if check_num not in checks:
                checks[check_num] = {
                    'check_num': check_num,
                    'check_name': result['check_name'],
                    'queries': [],
                    'total_queries': 0,
                    'successful_queries': 0,
                    'failed_queries': 0
                }

            checks[check_num]['queries'].append(result)
            checks[check_num]['total_queries'] += 1
            if result['status'] == 'SUCCESS':
                checks[check_num]['successful_queries'] += 1
            else:
                checks[check_num]['failed_queries'] += 1

        summary['checks'] = list(checks.values())

        # Save summary
        summary_path = output_dir / 'verification_summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, default=str)

        print(f"\n✅ Created verification summary: {summary_path}")

        # Create summary DataFrame
        summary_df = pd.DataFrame(all_results)
        summary_csv = output_dir / 'verification_summary.csv'
        summary_df.to_csv(summary_csv, index=False, encoding='utf-8')

        print(f"✅ Created verification summary CSV: {summary_csv}")

        return summary

    except Exception as e:
        print(f"❌ Failed to create summary: {e}")
        return None


def print_verification_summary(summary):
    """Print verification summary to console"""
    print("\n" + "="*80)
    print("📊 VERIFICATION SUMMARY")
    print("="*80)

    print(f"\n📄 Script: {summary['script_name']}")
    print(f"🕐 Timestamp: {summary['execution_timestamp']}")
    print(f"⏱️  Total Duration: {summary['total_duration_seconds']:.2f} seconds")

    print(f"\n📊 Overall Results:")
    print(f"   • Total CHECKs: {summary['total_checks']}")
    print(f"   • Total Queries: {summary['total_queries']}")
    print(f"   • ✅ Successful: {summary['successful_queries']}")
    print(f"   • ❌ Failed: {summary['failed_queries']}")

    # Show each CHECK
    print(f"\n📋 CHECK Details:")
    for check in summary['checks']:
        status_icon = "✅" if check['failed_queries'] == 0 else "❌"
        print(f"\n   {status_icon} {check['check_name']}")
        print(f"      Queries: {check['successful_queries']}/{check['total_queries']} successful")

        # Show saved results
        results_with_files = [q for q in check['queries'] if 'csv_file' in q]
        if results_with_files:
            print(f"      Saved results: {len(results_with_files)} files")
            for result in results_with_files:
                print(f"         → {result['csv_file']} ({result['rows']} rows)")

    # Show failures if any
    failures = [r for c in summary['checks'] for r in c['queries'] if r['status'] == 'FAILED']
    if failures:
        print(f"\n❌ FAILED QUERIES ({len(failures)}):")
        for failure in failures:
            print(f"   • {failure['check_name']} - Query {failure['query_num']}")
            print(f"     Error: {failure.get('error', 'Unknown error')}")

    print("\n" + "="*80)


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Main execution function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Execute verification script and save results')
    parser.add_argument('--script', required=True, help='Path to SQL verification script')
    parser.add_argument('--output', help='Output directory name (optional)')
    args = parser.parse_args()

    print("\n" + "="*80)
    print("🔍 VERIFICATION SCRIPT EXECUTION WITH AUTO-EXPORT")
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
        script_name = script_path.stem
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = DEFAULT_OUTPUT_DIR / f"{script_name}_{timestamp}"

    create_output_directory(output_dir)

    # Load configuration
    config = load_config()

    # Parse verification script
    checks = parse_verification_script(script_path)

    # Connect to Snowflake
    conn = None
    try:
        conn = connect_to_snowflake(config)

        # Execute all checks
        all_results = []
        for check in checks:
            check_results = execute_check(conn, check, output_dir)
            all_results.extend(check_results)

        # Create verification summary
        summary = create_verification_summary(all_results, output_dir, script_path.name)

        # Print summary
        if summary:
            print_verification_summary(summary)

        # Final status
        print(f"\n{'='*80}")
        if summary['failed_queries'] == 0:
            print(f"✅ All verification checks passed!")
        else:
            print(f"⚠️  Verification completed with {summary['failed_queries']} failure(s)")
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
