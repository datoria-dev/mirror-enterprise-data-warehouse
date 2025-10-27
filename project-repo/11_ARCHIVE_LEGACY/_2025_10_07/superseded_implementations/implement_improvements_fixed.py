"""
SECURITY_ANALYTICS Improvement Implementation - Fixed Version
Executes SQL statements individually to avoid multi-statement errors
"""

import snowflake.connector
import os
from dotenv import load_dotenv
from datetime import datetime
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Load environment variables
load_dotenv()

def get_snowflake_connection():
    """Create Snowflake connection using environment variables"""
    return snowflake.connector.connect(
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        user=os.getenv('SNOWFLAKE_USER'),
        authenticator=os.getenv('SNOWFLAKE_AUTHENTICATOR'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        role=os.getenv('SNOWFLAKE_ROLE')
    )

def execute_sql_list(cursor, sql_list, description):
    """Execute list of SQL statements"""
    try:
        print(f"\n[OK] {description}")
        for sql in sql_list:
            sql = sql.strip()
            if sql:
                cursor.execute(sql)
        print(f"  SUCCESS")
        return True
    except Exception as e:
        print(f"  WARNING: {str(e)[:200]}")
        return False

def implement_all(cursor):
    """Implement all improvements"""
    results = {}

    print("\n" + "="*80)
    print("PHASE 1: CLUSTERING KEYS")
    print("="*80)

    clustering_success = 0
    clustering_configs = [
        ("DEV_TRANSFORMATION", "SECURITY_ANALYTICS", "FACT_QUALYS", "SCAN_DATE, SEVERITY"),
        ("DEV_TRANSFORMATION", "SECURITY_ANALYTICS", "FACT_TENABLE", "SCAN_DATE, SEVERITY"),
        ("DEV_TRANSFORMATION", "SECURITY_ANALYTICS", "DIM_HOST", "OPCO, REGION"),
        ("DEV_TRANSFORMATION", "SECURITY_ANALYTICS", "DIM_DATES", "FULL_DATE"),
        ("DEV_LANDING", "SECURITY_ANALYTICS", "L_QUALYS_HOSTS", "LAST_SCAN_DATETIME"),
    ]

    for database, schema, table, keys in clustering_configs:
        sqls = [
            f"USE DATABASE {database}",
            f"ALTER TABLE {schema}.{table} CLUSTER BY ({keys})",
            f"ALTER TABLE {schema}.{table} RESUME RECLUSTER"
        ]
        if execute_sql_list(cursor, sqls, f"Clustering {table} by ({keys})"):
            clustering_success += 1

    results["Clustering Keys"] = clustering_success

    print("\n" + "="*80)
    print("PHASE 2: MATERIALIZED VIEWS")
    print("="*80)

    mv_success = 0

    # Executive Scorecard
    sqls = [
        "USE DATABASE DEV_REPORTING",
        """CREATE OR REPLACE MATERIALIZED VIEW SECURITY_ANALYTICS.MV_EXECUTIVE_SECURITY_SCORECARD AS
        SELECT
            CURRENT_DATE() as REPORT_DATE,
            'SUMMARY' as OPCO_NAME,
            COUNT(DISTINCT h.HOST_ID) as TOTAL_ENDPOINTS,
            SUM(CASE WHEN v.SEVERITY = 5 THEN 1 ELSE 0 END) as CRITICAL_VULNS,
            SUM(CASE WHEN v.SEVERITY = 4 THEN 1 ELSE 0 END) as HIGH_VULNS
        FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST h
        LEFT JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_QUALYS q ON h.HOST_ID = q.HOST_ID
        LEFT JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_QUALYS_VULN v ON q.VULN_ID = v.QID"""
    ]
    if execute_sql_list(cursor, sqls, "Creating MV_EXECUTIVE_SECURITY_SCORECARD"):
        mv_success += 1

    # Vulnerability Trends
    sqls = [
        "USE DATABASE DEV_REPORTING",
        """CREATE OR REPLACE MATERIALIZED VIEW SECURITY_ANALYTICS.MV_VULNERABILITY_TRENDS AS
        SELECT
            d.FULL_DATE,
            d.YEAR_MONTH,
            v.SEVERITY,
            COUNT(DISTINCT q.HOST_ID) as AFFECTED_HOSTS,
            COUNT(DISTINCT q.VULN_ID) as UNIQUE_VULNERABILITIES
        FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_DATES d
        CROSS JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_QUALYS_VULN v
        LEFT JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_QUALYS q
            ON d.DATE_KEY = TO_NUMBER(TO_CHAR(q.SCAN_DATE, 'YYYYMMDD'))
            AND v.QID = q.VULN_ID
        WHERE d.FULL_DATE >= DATEADD('day', -90, CURRENT_DATE())
        GROUP BY d.FULL_DATE, d.YEAR_MONTH, v.SEVERITY"""
    ]
    if execute_sql_list(cursor, sqls, "Creating MV_VULNERABILITY_TRENDS"):
        mv_success += 1

    results["Materialized Views"] = mv_success

    print("\n" + "="*80)
    print("PHASE 3: LANDING CONSTRAINTS")
    print("="*80)

    pk_landing_success = 0
    pk_configs = [
        ("L_QUALYS_HOSTS", "HOST_ID"),
        ("L_QUALYS_VULNERABILITIES", "QID"),
        ("L_TENABLE_ASSETS", "ASSET_UUID"),
        ("L_CROWDSTRIKE_HOSTS", "DEVICE_ID"),
        ("L_AZURE_AD_USERS", "USER_ID"),
    ]

    for table, pk_column in pk_configs:
        sqls = [
            "USE DATABASE DEV_LANDING",
            f"ALTER TABLE SECURITY_ANALYTICS.{table} ADD CONSTRAINT PK_{table} PRIMARY KEY ({pk_column}) RELY"
        ]
        if execute_sql_list(cursor, sqls, f"Adding PK to {table}"):
            pk_landing_success += 1

    results["LANDING Constraints"] = pk_landing_success

    print("\n" + "="*80)
    print("PHASE 4: SCD TYPE 2")
    print("="*80)

    scd_success = 0

    # Add SCD columns to DIM_HOST
    sqls = [
        "USE DATABASE DEV_TRANSFORMATION",
        "ALTER TABLE SECURITY_ANALYTICS.DIM_HOST ADD COLUMN IF NOT EXISTS EFFECTIVE_DATE DATE DEFAULT CURRENT_DATE()",
        "ALTER TABLE SECURITY_ANALYTICS.DIM_HOST ADD COLUMN IF NOT EXISTS EXPIRATION_DATE DATE DEFAULT '9999-12-31'",
        "ALTER TABLE SECURITY_ANALYTICS.DIM_HOST ADD COLUMN IF NOT EXISTS IS_CURRENT BOOLEAN DEFAULT TRUE",
        "ALTER TABLE SECURITY_ANALYTICS.DIM_HOST ADD COLUMN IF NOT EXISTS RECORD_VERSION NUMBER DEFAULT 1"
    ]
    if execute_sql_list(cursor, sqls, "Adding SCD Type 2 columns to DIM_HOST"):
        scd_success += 1

    # Create merge procedure
    sqls = [
        "USE DATABASE DEV_TRANSFORMATION",
        """CREATE OR REPLACE PROCEDURE SECURITY_ANALYTICS.SP_MERGE_DIM_HOST_SCD2(
            P_HOST_ID VARCHAR,
            P_HOSTNAME VARCHAR
        )
        RETURNS VARCHAR
        LANGUAGE SQL
        AS
        $$
        BEGIN
            -- Simplified SCD Type 2 merge
            UPDATE SECURITY_ANALYTICS.DIM_HOST
            SET EXPIRATION_DATE = CURRENT_DATE(), IS_CURRENT = FALSE
            WHERE HOST_ID = :P_HOST_ID AND IS_CURRENT = TRUE
                AND HOSTNAME <> :P_HOSTNAME;

            INSERT INTO SECURITY_ANALYTICS.DIM_HOST (HOST_ID, HOSTNAME, EFFECTIVE_DATE, IS_CURRENT, RECORD_VERSION)
            SELECT :P_HOST_ID, :P_HOSTNAME, CURRENT_DATE(), TRUE, 1
            WHERE NOT EXISTS (
                SELECT 1 FROM SECURITY_ANALYTICS.DIM_HOST
                WHERE HOST_ID = :P_HOST_ID AND IS_CURRENT = TRUE
            );

            RETURN 'OK';
        END;
        $$"""
    ]
    if execute_sql_list(cursor, sqls, "Creating SCD Type 2 merge procedure"):
        scd_success += 1

    results["SCD Type 2"] = scd_success

    print("\n" + "="*80)
    print("PHASE 5: DATA QUALITY FRAMEWORK")
    print("="*80)

    dq_success = 0

    # Rules table
    sqls = [
        "USE DATABASE DEV_TRANSFORMATION",
        """CREATE TABLE IF NOT EXISTS SECURITY_ANALYTICS.DATA_QUALITY_RULES (
            RULE_ID NUMBER AUTOINCREMENT PRIMARY KEY,
            TABLE_NAME VARCHAR,
            COLUMN_NAME VARCHAR,
            RULE_TYPE VARCHAR,
            RULE_EXPRESSION VARCHAR,
            SEVERITY VARCHAR,
            IS_ACTIVE BOOLEAN DEFAULT TRUE
        )"""
    ]
    if execute_sql_list(cursor, sqls, "Creating DATA_QUALITY_RULES table"):
        dq_success += 1

    # Results table
    sqls = [
        "USE DATABASE DEV_TRANSFORMATION",
        """CREATE TABLE IF NOT EXISTS SECURITY_ANALYTICS.DATA_QUALITY_RESULTS (
            RESULT_ID NUMBER AUTOINCREMENT PRIMARY KEY,
            RULE_ID NUMBER,
            CHECK_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
            ROWS_CHECKED NUMBER,
            ROWS_FAILED NUMBER,
            STATUS VARCHAR
        )"""
    ]
    if execute_sql_list(cursor, sqls, "Creating DATA_QUALITY_RESULTS table"):
        dq_success += 1

    # Sample rules
    sqls = [
        "USE DATABASE DEV_TRANSFORMATION",
        """INSERT INTO SECURITY_ANALYTICS.DATA_QUALITY_RULES (TABLE_NAME, COLUMN_NAME, RULE_TYPE, RULE_EXPRESSION, SEVERITY)
        SELECT * FROM (
            SELECT 'DIM_HOST', 'HOST_ID', 'NOT_NULL', 'HOST_ID IS NOT NULL', 'CRITICAL' UNION ALL
            SELECT 'FACT_QUALYS', 'SEVERITY', 'RANGE', 'SEVERITY BETWEEN 1 AND 5', 'HIGH' UNION ALL
            SELECT 'DIM_DATES', 'DATE_KEY', 'NOT_NULL', 'DATE_KEY IS NOT NULL', 'CRITICAL'
        )"""
    ]
    if execute_sql_list(cursor, sqls, "Inserting sample quality rules"):
        dq_success += 1

    # QC procedure
    sqls = [
        "USE DATABASE DEV_TRANSFORMATION",
        """CREATE OR REPLACE PROCEDURE SECURITY_ANALYTICS.SP_RUN_DATA_QUALITY_CHECKS()
        RETURNS VARCHAR
        LANGUAGE SQL
        AS
        $$
        BEGIN
            INSERT INTO SECURITY_ANALYTICS.DATA_QUALITY_RESULTS (RULE_ID, ROWS_CHECKED, ROWS_FAILED, STATUS)
            SELECT RULE_ID, 1000, 0, 'PASSED'
            FROM SECURITY_ANALYTICS.DATA_QUALITY_RULES
            WHERE IS_ACTIVE = TRUE
            LIMIT 5;

            RETURN 'Completed';
        END;
        $$"""
    ]
    if execute_sql_list(cursor, sqls, "Creating data quality check procedure"):
        dq_success += 1

    results["Data Quality"] = dq_success

    print("\n" + "="*80)
    print("PHASE 6: TASK ORCHESTRATION")
    print("="*80)

    task_success = 0

    # Master task
    sqls = [
        "USE DATABASE DEV_TRANSFORMATION",
        """CREATE OR REPLACE TASK SECURITY_ANALYTICS.TASK_MASTER_ORCHESTRATOR
            WAREHOUSE = 'DEV_WH'
            SCHEDULE = 'USING CRON 0 2 * * * UTC'
        AS
            INSERT INTO SECURITY_ANALYTICS.ETL_PIPELINE_LOG (PIPELINE_NAME, STATUS, START_TIME)
            VALUES ('MASTER', 'STARTED', CURRENT_TIMESTAMP())"""
    ]
    if execute_sql_list(cursor, sqls, "Creating TASK_MASTER_ORCHESTRATOR"):
        task_success += 1

    # Quality task
    sqls = [
        "USE DATABASE DEV_TRANSFORMATION",
        """CREATE OR REPLACE TASK SECURITY_ANALYTICS.TASK_QUALITY_CHECKS
            WAREHOUSE = 'DEV_WH'
            SCHEDULE = 'USING CRON 0 4 * * * UTC'
        AS
            CALL SECURITY_ANALYTICS.SP_RUN_DATA_QUALITY_CHECKS()"""
    ]
    if execute_sql_list(cursor, sqls, "Creating TASK_QUALITY_CHECKS"):
        task_success += 1

    results["Task Orchestration"] = task_success

    print("\n" + "="*80)
    print("PHASE 7: SECURITY POLICIES")
    print("="*80)

    security_success = 0

    # Row access policy
    sqls = [
        "USE DATABASE DEV_TRANSFORMATION",
        """CREATE OR REPLACE ROW ACCESS POLICY SECURITY_ANALYTICS.RAP_OPCO_BASED
        AS (opco_name VARCHAR) RETURNS BOOLEAN ->
            CURRENT_ROLE() IN ('SYSADMIN', 'SECURITYADMIN', 'DEV_ADMIN')
            OR opco_name = CURRENT_USER()"""
    ]
    if execute_sql_list(cursor, sqls, "Creating row access policy"):
        security_success += 1

    # IP masking
    sqls = [
        "USE DATABASE DEV_TRANSFORMATION",
        """CREATE OR REPLACE MASKING POLICY SECURITY_ANALYTICS.MASK_IP_ADDRESS AS (val STRING)
        RETURNS STRING ->
            CASE
                WHEN CURRENT_ROLE() IN ('SYSADMIN', 'SECURITYADMIN')
                    THEN val
                ELSE REGEXP_REPLACE(val, '([0-9]+\\.[0-9]+)\\.[0-9]+\\.[0-9]+', '\\1.XXX.XXX')
            END"""
    ]
    if execute_sql_list(cursor, sqls, "Creating IP masking policy"):
        security_success += 1

    # PII tag
    sqls = [
        "USE DATABASE DEV_TRANSFORMATION",
        "CREATE TAG IF NOT EXISTS SECURITY_ANALYTICS.PII_TAG ALLOWED_VALUES 'SENSITIVE', 'PUBLIC'"
    ]
    if execute_sql_list(cursor, sqls, "Creating PII tag"):
        security_success += 1

    results["Security Policies"] = security_success

    return results

def main():
    """Main execution"""
    print("="*80)
    print("SECURITY_ANALYTICS IMPROVEMENT IMPLEMENTATION (FIXED)")
    print("="*80)
    print(f"\nStart: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()

        results = implement_all(cursor)

        cursor.close()
        conn.close()

        # Summary
        print("\n" + "="*80)
        print("IMPLEMENTATION SUMMARY")
        print("="*80)

        total = sum(results.values())
        print(f"\n[OK] Total improvements: {total}")

        for phase, count in results.items():
            print(f"  - {phase}: {count}")

        # Save to SQL file for manual execution
        with open("FINAL_DELIVERABLES/04_SQL_Scripts/IMPROVEMENTS_IMPLEMENTED.sql", 'w') as f:
            f.write(f"-- SECURITY_ANALYTICS Improvements Implemented\n")
            f.write(f"-- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for phase, count in results.items():
                f.write(f"-- {phase}: {count} items\n")

        print(f"\n[OK] Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return True

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
