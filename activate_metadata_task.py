"""
Activate Daily Metadata Refresh Task

This script activates the daily scheduled task in Snowflake and verifies
that it's running correctly.

Usage:
    python activate_metadata_task.py

Date: 2025-10-24
"""

import snowflake.connector
import pandas as pd
import json
import sys
import io

# Fix encoding issues for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def load_config():
    """Load Snowflake configuration from JSON file"""
    try:
        with open('snowflake_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Configuration file not found: snowflake_config.json")
        sys.exit(1)
    except json.JSONDecodeError:
        print("❌ Invalid JSON in configuration file")
        sys.exit(1)

def connect_to_snowflake(config):
    """Establish connection to Snowflake using SSO"""
    try:
        print("🔌 Connecting to Snowflake via SSO (Okta)...")
        print("   ⏳ A browser window will open for authentication...")
        conn = snowflake.connector.connect(**config)
        print("✅ Connected successfully!")
        return conn
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)

def execute_query(conn, query, description):
    """Execute a query and return results as DataFrame"""
    try:
        cursor = conn.cursor()
        cursor.execute(query)

        # Check if query returns results
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            results = cursor.fetchall()
            df = pd.DataFrame(results, columns=columns)
            return df
        else:
            # No results (e.g., ALTER command)
            return pd.DataFrame({'STATUS': ['Success']})
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return pd.DataFrame()

def main():
    """Main execution function"""

    print("=" * 80)
    print("🚀 ACTIVATING DAILY METADATA REFRESH TASK")
    print("=" * 80)
    print()

    # Load configuration
    config = load_config()

    # Connect to Snowflake
    conn = connect_to_snowflake(config)

    try:
        # Set context
        print("\n📋 Setting context...")
        execute_query(conn, "USE ROLE DEV_DEVELOPER", "Use role")
        execute_query(conn, "USE WAREHOUSE DEV_WH", "Use warehouse")
        execute_query(conn, "USE DATABASE DEV_TRANSFORMATION", "Use database")
        execute_query(conn, "USE SCHEMA METADATA", "Use schema")
        print("✅ Context set successfully")

        # Check current task status
        print("\n🔍 Checking current task status...")
        task_before = execute_query(
            conn,
            "SHOW TASKS LIKE 'TASK_DAILY_METADATA_REFRESH'",
            "Show tasks before"
        )

        if not task_before.empty:
            state_before = task_before['state'].iloc[0] if 'state' in task_before.columns else 'Unknown'
            print(f"   Current state: {state_before}")
        else:
            print("❌ Task not found! Please create the metadata repository first.")
            return

        # Activate the task
        print("\n🔄 Activating task...")
        execute_query(
            conn,
            "ALTER TASK TASK_DAILY_METADATA_REFRESH RESUME",
            "Activate task"
        )
        print("✅ Task activation command executed")

        # Verify task is active
        print("\n✅ Verifying task status...")
        task_after = execute_query(
            conn,
            "SHOW TASKS LIKE 'TASK_DAILY_METADATA_REFRESH'",
            "Show tasks after"
        )

        if not task_after.empty:
            state_after = task_after['state'].iloc[0] if 'state' in task_after.columns else 'Unknown'
            schedule = task_after['schedule'].iloc[0] if 'schedule' in task_after.columns else 'Unknown'

            print(f"\n📊 Task Status:")
            print(f"   Name: TASK_DAILY_METADATA_REFRESH")
            print(f"   State: {state_after}")
            print(f"   Schedule: {schedule}")

            if state_after.lower() == 'started':
                print("\n" + "=" * 80)
                print("✅ SUCCESS! Task is now active and will run daily at 6:00 AM EST")
                print("=" * 80)
            else:
                print("\n⚠️  Warning: Task state is not 'started'. Current state:", state_after)

        # Check recent executions
        print("\n📜 Recent executions:")
        recent_logs = execute_query(
            conn,
            """
            SELECT
                LOG_ID,
                EXECUTION_START,
                EXECUTION_DURATION_SECONDS,
                STATUS,
                TABLES_PROCESSED,
                COLUMNS_PROCESSED
            FROM PROCEDURE_EXECUTION_LOG
            WHERE PROCEDURE_NAME = 'SP_REFRESH_METADATA'
            ORDER BY EXECUTION_START DESC
            LIMIT 5
            """,
            "Get recent logs"
        )

        if not recent_logs.empty:
            print("\n   Last 5 executions:")
            print(recent_logs.to_string(index=False))

            # Calculate success rate
            total_executions = len(recent_logs)
            successful = len(recent_logs[recent_logs['STATUS'] == 'SUCCESS'])
            success_rate = (successful / total_executions * 100) if total_executions > 0 else 0

            print(f"\n   Success Rate: {successful}/{total_executions} ({success_rate:.1f}%)")
        else:
            print("   No execution history found")

        # Display next steps
        print("\n" + "=" * 80)
        print("📋 NEXT STEPS")
        print("=" * 80)
        print()
        print("1. ✅ Task will run automatically tomorrow at 6:00 AM EST")
        print("2. 📊 Monitor executions in PROCEDURE_EXECUTION_LOG table")
        print("3. 🔍 Check Streamlit apps to see updated metadata")
        print("4. 📧 Set up email alerts for failed executions (optional)")
        print()
        print("To monitor executions:")
        print("   SELECT * FROM PROCEDURE_EXECUTION_LOG")
        print("   WHERE PROCEDURE_NAME = 'SP_REFRESH_METADATA'")
        print("   ORDER BY EXECUTION_START DESC;")
        print()
        print("To manually trigger refresh:")
        print("   CALL SP_REFRESH_METADATA();")
        print()
        print("To pause task:")
        print("   ALTER TASK TASK_DAILY_METADATA_REFRESH SUSPEND;")
        print()

    finally:
        # Close connection
        conn.close()
        print("🔌 Snowflake connection closed")
        print("\n" + "=" * 80)
        print("✅ Task activation process completed!")
        print("=" * 80)

if __name__ == "__main__":
    main()
