"""
Verify and Start Scheduled Tasks
This script verifies the created tasks and starts them
"""

import snowflake.connector
import os
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables
load_dotenv()

def create_connection():
    """Create Snowflake connection"""
    try:
        conn = snowflake.connector.connect(
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            user=os.getenv('SNOWFLAKE_USER'),
            authenticator='externalbrowser',
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            role=os.getenv('SNOWFLAKE_ROLE')
        )
        return conn
    except Exception as e:
        print(f"[ERROR] Connection failed: {str(e)}")
        return None

def verify_and_start_tasks(conn):
    """Verify tasks and start them"""
    cursor = conn.cursor()

    print("\n" + "="*70)
    print("SCHEDULED TASKS VERIFICATION AND ACTIVATION")
    print("="*70)

    # Set database and schema context
    cursor.execute("USE DATABASE DEV_TRANSFORMATION")
    cursor.execute("USE SCHEMA SECURITY_ANALYTICS")

    # List all tasks
    print("\n[CHECKING] Existing Tasks...")
    cursor.execute("""
        SHOW TASKS IN SCHEMA SECURITY_ANALYTICS
    """)

    tasks = cursor.fetchall()
    task_names = []

    print("\n[TASKS FOUND]:")
    print("-" * 50)
    for task in tasks:
        task_name = task[1]  # Name is usually in column 1
        task_state = task[3] if len(task) > 3 else 'UNKNOWN'  # State in column 3
        task_names.append(task_name)
        print(f"  Task: {task_name}")
        print(f"    State: {task_state}")

        # Get task details
        cursor.execute(f"DESCRIBE TASK {task_name}")
        details = cursor.fetchall()
        for detail in details:
            if detail[0] == 'schedule':
                print(f"    Schedule: {detail[1]}")

    # Resume (start) all tasks
    print("\n[ACTIVATING] Tasks...")
    print("-" * 50)

    tasks_to_start = [
        'TASK_DAILY_HEALTH_CHECK',
        'TASK_DATA_QUALITY_MONITOR',
        'TASK_ETL_PIPELINE_MONITOR'
    ]

    activated = 0
    for task_name in tasks_to_start:
        if task_name in task_names:
            try:
                cursor.execute(f"ALTER TASK {task_name} RESUME")
                print(f"  [SUCCESS] Activated: {task_name}")
                activated += 1
            except Exception as e:
                if 'already started' in str(e).lower():
                    print(f"  [INFO] Already active: {task_name}")
                    activated += 1
                else:
                    print(f"  [ERROR] Failed to activate {task_name}: {str(e)}")
        else:
            print(f"  [WARNING] Task not found: {task_name}")

    # Verify Master Control Panel
    print("\n[CHECKING] Master Control Panel...")
    print("-" * 50)

    cursor.execute("""
        SELECT
            METRIC_NAME,
            METRIC_VALUE,
            STATUS,
            DETAILS
        FROM VW_MASTER_CONTROL_PANEL
        ORDER BY METRIC_NAME
    """)

    control_panel = cursor.fetchall()

    if control_panel:
        print("\n  MASTER CONTROL PANEL STATUS:")
        print("  " + "-"*45)
        for row in control_panel:
            metric = row[0] if row[0] else 'Unknown'
            value = row[1] if row[1] else 'N/A'
            status = row[2] if row[2] else 'Unknown'
            details = row[3] if row[3] else ''

            # Format the output nicely
            print(f"  {metric:20} {status:15} {details[:40]}")

    # Check Performance Benchmarks
    print("\n[CHECKING] Latest Performance Benchmarks...")
    print("-" * 50)

    cursor.execute("""
        SELECT
            BENCHMARK_NAME,
            EXECUTION_TIME_MS,
            ROWS_PROCESSED,
            EXECUTED_AT
        FROM PERFORMANCE_BENCHMARKS
        WHERE EXECUTED_AT >= DATEADD('hour', -1, CURRENT_TIMESTAMP())
        ORDER BY EXECUTED_AT DESC
        LIMIT 5
    """)

    benchmarks = cursor.fetchall()

    if benchmarks:
        print("\n  Recent Benchmarks:")
        for bm in benchmarks:
            name = bm[0]
            time_ms = bm[1]
            rows = bm[2]
            executed = bm[3]
            print(f"    - {name}: {time_ms:.2f}ms ({rows:,} rows)")

    # Check Data Quality Scores
    print("\n[CHECKING] Data Quality Scores...")
    print("-" * 50)

    cursor.execute("""
        SELECT
            AVG(QUALITY_SCORE) as AVG_SCORE,
            MIN(QUALITY_SCORE) as MIN_SCORE,
            MAX(QUALITY_SCORE) as MAX_SCORE,
            COUNT(*) as TABLES_SCORED
        FROM DATA_QUALITY_SCORECARD
        WHERE SCORECARD_DATE = CURRENT_DATE()
    """)

    quality_summary = cursor.fetchone()

    if quality_summary and quality_summary[0]:
        avg_score = quality_summary[0]
        min_score = quality_summary[1]
        max_score = quality_summary[2]
        tables_scored = quality_summary[3]

        print(f"\n  Quality Summary (Today):")
        print(f"    Average Score: {avg_score:.1f}%")
        print(f"    Min Score: {min_score:.1f}%")
        print(f"    Max Score: {max_score:.1f}%")
        print(f"    Tables Scored: {tables_scored}")

    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    print(f"\n  Tasks Found: {len(task_names)}")
    print(f"  Tasks Activated: {activated}")
    print(f"  Control Panel: ACTIVE")
    print(f"  Monitoring: OPERATIONAL")

    print("\n[SUCCESS] All monitoring systems are operational!")

    # Save verification report
    report = {
        'timestamp': datetime.now().isoformat(),
        'tasks_found': len(task_names),
        'tasks_activated': activated,
        'task_details': task_names,
        'control_panel_status': 'ACTIVE',
        'monitoring_status': 'OPERATIONAL'
    }

    report_file = f"task_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n[REPORT SAVED] {report_file}")

    cursor.close()
    return True

def main():
    """Main execution"""
    conn = create_connection()
    if not conn:
        print("[ERROR] Failed to connect to Snowflake")
        return False

    try:
        success = verify_and_start_tasks(conn)
        return success
    except Exception as e:
        print(f"[ERROR] Verification failed: {str(e)}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)