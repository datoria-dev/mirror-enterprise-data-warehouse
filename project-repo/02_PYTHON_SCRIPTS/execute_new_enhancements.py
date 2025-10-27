"""
Execute New Enhancements in Snowflake
======================================
This script executes the 4 new enhancements:
1. Power BI Integration Layer
2. Data Quality Framework
3. Unified User Dimension
4. Near Real-Time Capabilities

Author: Data Engineering Team
Date: 2025-10-07
"""

import snowflake.connector
import os
import sys
from pathlib import Path
import time

# ANSI color codes for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}[OK] {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}[ERROR] {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}[INFO] {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}[WARN] {text}{Colors.ENDC}")

def get_snowflake_connection():
    """
    Get Snowflake connection using SSO or username/password
    """
    print_header("SNOWFLAKE CONNECTION")

    # Try to use environment variables first
    account = os.getenv('SNOWFLAKE_ACCOUNT')
    user = os.getenv('SNOWFLAKE_USER')

    if not account:
        print_info("Enter your Snowflake connection details:")
        account = input("Account (e.g., xy12345.us-east-1): ").strip()
        user = input("Username: ").strip()

        # Save for next time
        with open('.env', 'a') as f:
            f.write(f"\nSNOWFLAKE_ACCOUNT={account}")
            f.write(f"\nSNOWFLAKE_USER={user}")

    print_info(f"Connecting to Snowflake account: {account}")
    print_info(f"User: {user}")
    print_info("Authentication: SSO (Browser will open)")

    try:
        conn = snowflake.connector.connect(
            account=account,
            user=user,
            authenticator='externalbrowser',  # SSO via browser
            warehouse='DEV_WH',
            database='DEV_REPORTING',
            schema='SECURITY_ANALYTICS'
        )
        print_success(f"Connected to Snowflake as {user}")
        return conn
    except Exception as e:
        print_error(f"Connection failed: {str(e)}")
        return None

def execute_sql_file(conn, file_path, enhancement_name):
    """
    Execute SQL file and track progress
    """
    print_header(f"EXECUTING: {enhancement_name}")
    print_info(f"File: {file_path}")

    if not os.path.exists(file_path):
        print_error(f"File not found: {file_path}")
        return False

    # Read SQL file
    with open(file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Split by statement (simple split by semicolon - may need refinement)
    statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]

    print_info(f"Found {len(statements)} SQL statements to execute")

    cursor = conn.cursor()
    executed = 0
    failed = 0

    for i, statement in enumerate(statements, 1):
        # Skip comments and empty statements
        if not statement or statement.startswith('--') or statement.startswith('/*'):
            continue

        # Print progress for major operations
        if any(keyword in statement.upper() for keyword in ['CREATE TABLE', 'CREATE VIEW', 'CREATE PROCEDURE', 'CREATE TASK', 'CREATE PIPE', 'CREATE STREAM']):
            # Extract object name
            lines = statement.split('\n')
            for line in lines:
                if 'CREATE' in line.upper():
                    print_info(f"[{i}/{len(statements)}] {line.strip()[:80]}...")
                    break

        try:
            cursor.execute(statement)
            executed += 1
        except Exception as e:
            error_msg = str(e)
            # Ignore "already exists" errors
            if 'already exists' in error_msg.lower():
                print_warning(f"Object already exists (skipping)")
                executed += 1
            else:
                print_error(f"Failed to execute statement {i}: {error_msg[:200]}")
                failed += 1
                # Ask if continue
                if failed >= 3:
                    response = input(f"\n{Colors.WARNING}Multiple errors detected. Continue? (yes/no): {Colors.ENDC}").lower()
                    if response != 'yes':
                        print_error("Execution aborted by user")
                        return False

    cursor.close()

    print(f"\n{Colors.BOLD}Summary:{Colors.ENDC}")
    print_success(f"Executed: {executed} statements")
    if failed > 0:
        print_error(f"Failed: {failed} statements")

    return failed == 0

def verify_implementation(conn, enhancement_name, verification_queries):
    """
    Verify that objects were created successfully
    """
    print_info(f"Verifying {enhancement_name}...")
    cursor = conn.cursor()

    all_passed = True
    for description, query in verification_queries.items():
        try:
            cursor.execute(query)
            result = cursor.fetchone()
            if result and result[0] > 0:
                print_success(f"{description}: {result[0]} objects found")
            else:
                print_warning(f"{description}: No objects found")
                all_passed = False
        except Exception as e:
            print_error(f"{description}: Verification failed - {str(e)}")
            all_passed = False

    cursor.close()
    return all_passed

def main():
    print_header("SECURITY_ANALYTICS NEW ENHANCEMENTS IMPLEMENTATION")
    print(f"{Colors.BOLD}This script will implement:{Colors.ENDC}")
    print("  1. Power BI Integration Layer")
    print("  2. Data Quality Framework")
    print("  3. Unified User Dimension")
    print("  4. Near Real-Time Capabilities")
    print()

    # Get project root
    project_root = Path(__file__).parent
    sql_dir = project_root / '02_SQL_SCRIPTS' / '02_advanced_features'

    # SQL files to execute
    enhancements = [
        {
            'name': '1. Power BI Integration Layer',
            'file': sql_dir / '01_PowerBI_Integration_Layer.sql',
            'verify': {
                'Views': "SELECT COUNT(*) FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS' AND TABLE_NAME LIKE 'VW_POWERBI%'",
                'Tables': "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS' AND TABLE_NAME LIKE '%POWERBI%'",
                'Tasks': "SHOW TASKS LIKE 'TASK_POPULATE_POWERBI%' IN SCHEMA SECURITY_ANALYTICS"
            }
        },
        {
            'name': '2. Data Quality Framework',
            'file': sql_dir / '02_Data_Quality_Framework.sql',
            'verify': {
                'DQ Tables': "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS' AND TABLE_NAME LIKE '%DATA_QUALITY%'",
                'DQ Views': "SELECT COUNT(*) FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS' AND TABLE_NAME LIKE '%DATA_QUALITY%'",
                'DQ Tasks': "SHOW TASKS LIKE 'TASK_DAILY_DATA_QUALITY%' IN SCHEMA SECURITY_ANALYTICS"
            }
        },
        {
            'name': '3. Unified User Dimension',
            'file': sql_dir / '03_Unified_User_Dimension.sql',
            'verify': {
                'DIM_USER Table': "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS' AND TABLE_NAME = 'DIM_USER'",
                'User Views': "SELECT COUNT(*) FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS' AND TABLE_NAME LIKE 'VW_%USER%'",
                'User Task': "SHOW TASKS LIKE 'TASK_LOAD_DIM_USER' IN SCHEMA SECURITY_ANALYTICS"
            }
        },
        {
            'name': '4. Near Real-Time Capabilities',
            'file': sql_dir / '04_Near_RealTime_Capabilities.sql',
            'verify': {
                'Real-Time Tables': "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS' AND TABLE_NAME LIKE '%REALTIME%'",
                'Alert Tables': "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS' AND TABLE_NAME LIKE 'TBL_ALERT%'",
                'Pipes': "SHOW PIPES IN SCHEMA SECURITY_ANALYTICS"
            }
        }
    ]

    # Connect to Snowflake
    conn = get_snowflake_connection()
    if not conn:
        print_error("Failed to connect to Snowflake")
        return False

    # Execute each enhancement
    results = {}
    for enhancement in enhancements:
        print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
        response = input(f"\nExecute {enhancement['name']}? (yes/no/skip): ").lower()

        if response == 'skip':
            print_warning(f"Skipping {enhancement['name']}")
            results[enhancement['name']] = 'SKIPPED'
            continue
        elif response != 'yes':
            print_warning("Aborting execution")
            break

        success = execute_sql_file(conn, enhancement['file'], enhancement['name'])

        if success:
            # Verify
            verify_implementation(conn, enhancement['name'], enhancement['verify'])
            results[enhancement['name']] = 'SUCCESS'
        else:
            results[enhancement['name']] = 'FAILED'
            response = input(f"\n{Colors.WARNING}Enhancement failed. Continue with next? (yes/no): {Colors.ENDC}").lower()
            if response != 'yes':
                break

    # Close connection
    conn.close()

    # Final summary
    print_header("IMPLEMENTATION SUMMARY")
    for name, status in results.items():
        if status == 'SUCCESS':
            print_success(f"{name}: {status}")
        elif status == 'FAILED':
            print_error(f"{name}: {status}")
        else:
            print_warning(f"{name}: {status}")

    print(f"\n{Colors.BOLD}Next Steps:{Colors.ENDC}")
    print("1. Run test suite: @02_SQL_SCRIPTS/02_advanced_features/00_Test_All_Enhancements.sql")
    print("2. Configure AWS S3 and SNS for Snowpipe (see documentation)")
    print("3. Connect Power BI to VW_POWERBI_EXECUTIVE_DASHBOARD_SECURE")
    print("4. Review Data Quality Dashboard")

    return all(status == 'SUCCESS' for status in results.values())

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Execution interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.FAIL}Unexpected error: {str(e)}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
