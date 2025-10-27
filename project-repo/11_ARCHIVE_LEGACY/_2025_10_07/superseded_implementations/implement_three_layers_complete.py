"""
Complete Three-Layer Implementation
Implements improvements for DEV_LANDING, DEV_TRANSFORMATION, and DEV_REPORTING
"""

import snowflake.connector
import os
from dotenv import load_dotenv
from datetime import datetime
import sys

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

load_dotenv()

def get_snowflake_connection():
    return snowflake.connector.connect(
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        user=os.getenv('SNOWFLAKE_USER'),
        authenticator=os.getenv('SNOWFLAKE_AUTHENTICATOR'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        role=os.getenv('SNOWFLAKE_ROLE')
    )

def execute_sql_list(cursor, sql_list, description):
    try:
        print(f"\n[OK] {description}")
        for sql in sql_list:
            sql = sql.strip()
            if sql and not sql.startswith('--'):
                cursor.execute(sql)
        print(f"  SUCCESS")
        return True
    except Exception as e:
        print(f"  WARNING: {str(e)[:300]}")
        return False

def landing_layer_improvements(cursor):
    """Improvements for DEV_LANDING layer"""
    print("\n" + "="*80)
    print("LAYER 1: DEV_LANDING IMPROVEMENTS")
    print("="*80)

    success = 0

    # 1. Landing data quality view
    sqls = [
        "USE DATABASE DEV_LANDING",
        """CREATE OR REPLACE VIEW SECURITY_ANALYTICS.VW_LANDING_DATA_QUALITY AS
        SELECT
            TABLE_NAME,
            ROW_COUNT,
            BYTES / (1024*1024) as SIZE_MB,
            LAST_ALTERED,
            DATEDIFF(hour, LAST_ALTERED, CURRENT_TIMESTAMP()) as HOURS_SINCE_LAST_UPDATE,
            CASE
                WHEN ROW_COUNT = 0 THEN 'EMPTY - No data loaded'
                WHEN DATEDIFF(hour, LAST_ALTERED, CURRENT_TIMESTAMP()) > 48 THEN 'STALE - Not updated >48h'
                WHEN DATEDIFF(hour, LAST_ALTERED, CURRENT_TIMESTAMP()) > 24 THEN 'WARNING - Not updated >24h'
                ELSE 'HEALTHY'
            END as DATA_STATUS
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
            AND TABLE_TYPE = 'BASE TABLE'
        ORDER BY LAST_ALTERED DESC"""
    ]
    if execute_sql_list(cursor, sqls, "Creating VW_LANDING_DATA_QUALITY"):
        success += 1

    # 2. Landing ingestion log table
    sqls = [
        "USE DATABASE DEV_LANDING",
        """CREATE OR REPLACE TABLE SECURITY_ANALYTICS.INGESTION_LOG (
            LOG_ID NUMBER AUTOINCREMENT PRIMARY KEY,
            SOURCE_SYSTEM VARCHAR,
            TABLE_NAME VARCHAR,
            RECORDS_LOADED NUMBER,
            LOAD_START_TIME TIMESTAMP,
            LOAD_END_TIME TIMESTAMP,
            LOAD_DURATION_SECONDS NUMBER,
            STATUS VARCHAR,
            ERROR_MESSAGE VARCHAR,
            CREATED_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
        )"""
    ]
    if execute_sql_list(cursor, sqls, "Creating INGESTION_LOG table"):
        success += 1

    # 3. Source system health check view
    sqls = [
        "USE DATABASE DEV_LANDING",
        """CREATE OR REPLACE VIEW SECURITY_ANALYTICS.VW_SOURCE_SYSTEM_HEALTH AS
        SELECT
            CASE
                WHEN TABLE_NAME LIKE 'L_QUALYS%' THEN 'Qualys'
                WHEN TABLE_NAME LIKE 'L_TENABLE%' THEN 'Tenable'
                WHEN TABLE_NAME LIKE 'L_CROWDSTRIKE%' THEN 'CrowdStrike'
                WHEN TABLE_NAME LIKE 'L_SENTINEL%' THEN 'SentinelOne'
                WHEN TABLE_NAME LIKE 'L_ZEROFOX%' THEN 'ZeroFox'
                WHEN TABLE_NAME LIKE 'L_AZURE%' THEN 'Azure AD'
                WHEN TABLE_NAME LIKE 'L_SERVICENOW%' THEN 'ServiceNow'
                ELSE 'Other'
            END as SOURCE_SYSTEM,
            COUNT(*) as TABLE_COUNT,
            SUM(ROW_COUNT) as TOTAL_RECORDS,
            SUM(BYTES / (1024*1024*1024)) as TOTAL_SIZE_GB,
            MAX(LAST_ALTERED) as LAST_UPDATE,
            COUNT(CASE WHEN ROW_COUNT = 0 THEN 1 END) as EMPTY_TABLES,
            COUNT(CASE WHEN ROW_COUNT > 0 THEN 1 END) as POPULATED_TABLES
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
            AND TABLE_TYPE = 'BASE TABLE'
        GROUP BY SOURCE_SYSTEM
        ORDER BY TOTAL_RECORDS DESC"""
    ]
    if execute_sql_list(cursor, sqls, "Creating VW_SOURCE_SYSTEM_HEALTH"):
        success += 1

    # 4. Landing validation procedure
    sqls = [
        "USE DATABASE DEV_LANDING",
        """CREATE OR REPLACE PROCEDURE SECURITY_ANALYTICS.SP_VALIDATE_LANDING_DATA(P_TABLE_NAME VARCHAR)
        RETURNS VARCHAR
        LANGUAGE SQL
        AS
        $$
        DECLARE
            record_count NUMBER;
            validation_status VARCHAR;
        BEGIN
            -- Get record count
            EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM SECURITY_ANALYTICS.' || :P_TABLE_NAME INTO :record_count;

            -- Determine status
            IF (:record_count = 0) THEN
                SET :validation_status = 'FAILED - No records';
            ELSIF (:record_count < 100) THEN
                SET :validation_status = 'WARNING - Low record count: ' || :record_count;
            ELSE
                SET :validation_status = 'PASSED - ' || :record_count || ' records';
            END IF;

            RETURN :validation_status;
        END;
        $$"""
    ]
    if execute_sql_list(cursor, sqls, "Creating SP_VALIDATE_LANDING_DATA"):
        success += 1

    # 5. Staging area for pre-validation
    sqls = [
        "USE DATABASE DEV_LANDING",
        """CREATE OR REPLACE TABLE SECURITY_ANALYTICS.STAGING_VALIDATION_ERRORS (
            ERROR_ID NUMBER AUTOINCREMENT PRIMARY KEY,
            SOURCE_TABLE VARCHAR,
            RECORD_ID VARCHAR,
            ERROR_TYPE VARCHAR,
            ERROR_DESCRIPTION VARCHAR,
            ERROR_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
        )"""
    ]
    if execute_sql_list(cursor, sqls, "Creating STAGING_VALIDATION_ERRORS"):
        success += 1

    # 6. File ingestion metadata
    sqls = [
        "USE DATABASE DEV_LANDING",
        """CREATE OR REPLACE TABLE SECURITY_ANALYTICS.FILE_INGESTION_METADATA (
            FILE_ID NUMBER AUTOINCREMENT PRIMARY KEY,
            FILE_NAME VARCHAR,
            FILE_PATH VARCHAR,
            FILE_SIZE_BYTES NUMBER,
            SOURCE_SYSTEM VARCHAR,
            TARGET_TABLE VARCHAR,
            INGESTION_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
            RECORDS_IN_FILE NUMBER,
            RECORDS_LOADED NUMBER,
            STATUS VARCHAR
        )"""
    ]
    if execute_sql_list(cursor, sqls, "Creating FILE_INGESTION_METADATA"):
        success += 1

    print(f"\n[DONE] LANDING layer: {success}/6 improvements")
    return success

def transformation_layer_improvements(cursor):
    """Additional improvements for DEV_TRANSFORMATION layer"""
    print("\n" + "="*80)
    print("LAYER 2: DEV_TRANSFORMATION IMPROVEMENTS")
    print("="*80)

    success = 0

    # 1. Transformation quality metrics view
    sqls = [
        "USE DATABASE DEV_TRANSFORMATION",
        """CREATE OR REPLACE VIEW SECURITY_ANALYTICS.VW_TRANSFORMATION_QUALITY_METRICS AS
        SELECT
            TABLE_NAME,
            ROW_COUNT,
            CASE
                WHEN TABLE_NAME LIKE 'DIM_%' THEN 'Dimension'
                WHEN TABLE_NAME LIKE 'FACT_%' THEN 'Fact'
                ELSE 'Other'
            END as TABLE_TYPE,
            CASE
                WHEN tc.CONSTRAINT_TYPE = 'PRIMARY KEY' THEN 'Has PK'
                ELSE 'No PK'
            END as PK_STATUS,
            COUNT(DISTINCT fk.CONSTRAINT_NAME) as FK_COUNT
        FROM INFORMATION_SCHEMA.TABLES t
        LEFT JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
            ON t.TABLE_NAME = tc.TABLE_NAME
            AND t.TABLE_SCHEMA = tc.TABLE_SCHEMA
            AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
        LEFT JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS fk
            ON t.TABLE_NAME = fk.TABLE_NAME
            AND t.TABLE_SCHEMA = fk.TABLE_SCHEMA
            AND fk.CONSTRAINT_TYPE = 'FOREIGN KEY'
        WHERE t.TABLE_SCHEMA = 'SECURITY_ANALYTICS'
            AND t.TABLE_TYPE = 'BASE TABLE'
        GROUP BY t.TABLE_NAME, t.ROW_COUNT, tc.CONSTRAINT_TYPE"""
    ]
    if execute_sql_list(cursor, sqls, "Creating VW_TRANSFORMATION_QUALITY_METRICS"):
        success += 1

    # 2. ETL orchestration log
    sqls = [
        "USE DATABASE DEV_TRANSFORMATION",
        """CREATE OR REPLACE TABLE SECURITY_ANALYTICS.ETL_ORCHESTRATION_LOG (
            ETL_ID NUMBER AUTOINCREMENT PRIMARY KEY,
            PIPELINE_NAME VARCHAR,
            STEP_NAME VARCHAR,
            SOURCE_TABLE VARCHAR,
            TARGET_TABLE VARCHAR,
            RECORDS_READ NUMBER,
            RECORDS_WRITTEN NUMBER,
            RECORDS_UPDATED NUMBER,
            RECORDS_REJECTED NUMBER,
            START_TIME TIMESTAMP,
            END_TIME TIMESTAMP,
            DURATION_SECONDS NUMBER,
            STATUS VARCHAR,
            ERROR_MESSAGE VARCHAR
        )"""
    ]
    if execute_sql_list(cursor, sqls, "Creating ETL_ORCHESTRATION_LOG"):
        success += 1

    # 3. Dimension SCD tracking view
    sqls = [
        "USE DATABASE DEV_TRANSFORMATION",
        """CREATE OR REPLACE VIEW SECURITY_ANALYTICS.VW_DIMENSION_SCD_STATUS AS
        SELECT
            TABLE_NAME,
            ROW_COUNT,
            CASE
                WHEN EXISTS (
                    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS c
                    WHERE c.TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                        AND c.TABLE_NAME = t.TABLE_NAME
                        AND c.COLUMN_NAME IN ('EFFECTIVE_DATE', 'EXPIRATION_DATE', 'IS_CURRENT')
                ) THEN 'SCD Type 2 Enabled'
                ELSE 'SCD Not Implemented'
            END as SCD_STATUS
        FROM INFORMATION_SCHEMA.TABLES t
        WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
            AND TABLE_NAME LIKE 'DIM_%'
        ORDER BY TABLE_NAME"""
    ]
    if execute_sql_list(cursor, sqls, "Creating VW_DIMENSION_SCD_STATUS"):
        success += 1

    # 4. Data freshness monitor
    sqls = [
        "USE DATABASE DEV_TRANSFORMATION",
        """CREATE OR REPLACE VIEW SECURITY_ANALYTICS.VW_DATA_FRESHNESS_MONITOR AS
        SELECT
            t.TABLE_NAME,
            t.ROW_COUNT,
            t.LAST_ALTERED as TABLE_LAST_ALTERED,
            l.LAST_ALTERED as LANDING_LAST_ALTERED,
            DATEDIFF(hour, l.LAST_ALTERED, t.LAST_ALTERED) as HOURS_DELTA,
            CASE
                WHEN DATEDIFF(hour, l.LAST_ALTERED, t.LAST_ALTERED) > 24 THEN 'STALE'
                WHEN DATEDIFF(hour, l.LAST_ALTERED, t.LAST_ALTERED) > 12 THEN 'WARNING'
                ELSE 'FRESH'
            END as FRESHNESS_STATUS
        FROM INFORMATION_SCHEMA.TABLES t
        LEFT JOIN DEV_LANDING.INFORMATION_SCHEMA.TABLES l
            ON REPLACE(t.TABLE_NAME, 'DIM_', 'L_') = l.TABLE_NAME
            OR REPLACE(t.TABLE_NAME, 'FACT_', 'L_') = l.TABLE_NAME
        WHERE t.TABLE_SCHEMA = 'SECURITY_ANALYTICS'
            AND t.TABLE_TYPE = 'BASE TABLE'
        ORDER BY HOURS_DELTA DESC"""
    ]
    if execute_sql_list(cursor, sqls, "Creating VW_DATA_FRESHNESS_MONITOR"):
        success += 1

    # 5. Business rule violations table
    sqls = [
        "USE DATABASE DEV_TRANSFORMATION",
        """CREATE OR REPLACE TABLE SECURITY_ANALYTICS.BUSINESS_RULE_VIOLATIONS (
            VIOLATION_ID NUMBER AUTOINCREMENT PRIMARY KEY,
            TABLE_NAME VARCHAR,
            RULE_NAME VARCHAR,
            RULE_DESCRIPTION VARCHAR,
            RECORD_ID VARCHAR,
            VIOLATION_DETAILS VARCHAR,
            SEVERITY VARCHAR,
            DETECTED_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
            RESOLVED_DATE TIMESTAMP,
            STATUS VARCHAR DEFAULT 'OPEN'
        )"""
    ]
    if execute_sql_list(cursor, sqls, "Creating BUSINESS_RULE_VIOLATIONS"):
        success += 1

    print(f"\n[DONE] TRANSFORMATION layer: {success}/5 improvements")
    return success

def reporting_layer_improvements(cursor):
    """Additional improvements for DEV_REPORTING layer"""
    print("\n" + "="*80)
    print("LAYER 3: DEV_REPORTING IMPROVEMENTS")
    print("="*80)

    success = 0

    # 1. Report execution log
    sqls = [
        "USE DATABASE DEV_REPORTING",
        """CREATE OR REPLACE TABLE SECURITY_ANALYTICS.REPORT_EXECUTION_LOG (
            EXECUTION_ID NUMBER AUTOINCREMENT PRIMARY KEY,
            REPORT_NAME VARCHAR,
            REPORT_TYPE VARCHAR,
            REQUESTED_BY VARCHAR,
            EXECUTION_START TIMESTAMP,
            EXECUTION_END TIMESTAMP,
            RECORDS_RETURNED NUMBER,
            STATUS VARCHAR,
            ERROR_MESSAGE VARCHAR
        )"""
    ]
    if execute_sql_list(cursor, sqls, "Creating REPORT_EXECUTION_LOG"):
        success += 1

    # 2. KPI definitions table
    sqls = [
        "USE DATABASE DEV_REPORTING",
        """CREATE OR REPLACE TABLE SECURITY_ANALYTICS.KPI_DEFINITIONS (
            KPI_ID NUMBER AUTOINCREMENT PRIMARY KEY,
            KPI_NAME VARCHAR,
            KPI_CATEGORY VARCHAR,
            KPI_DESCRIPTION VARCHAR,
            CALCULATION_LOGIC VARCHAR,
            TARGET_VALUE NUMBER,
            WARNING_THRESHOLD NUMBER,
            CRITICAL_THRESHOLD NUMBER,
            UNIT_OF_MEASURE VARCHAR,
            UPDATE_FREQUENCY VARCHAR,
            OWNER VARCHAR
        )"""
    ]
    if execute_sql_list(cursor, sqls, "Creating KPI_DEFINITIONS"):
        success += 1

    # 3. Dashboard access audit
    sqls = [
        "USE DATABASE DEV_REPORTING",
        """CREATE OR REPLACE TABLE SECURITY_ANALYTICS.DASHBOARD_ACCESS_AUDIT (
            ACCESS_ID NUMBER AUTOINCREMENT PRIMARY KEY,
            DASHBOARD_NAME VARCHAR,
            USER_NAME VARCHAR,
            ACCESS_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
            IP_ADDRESS VARCHAR,
            SESSION_DURATION_SECONDS NUMBER,
            REPORTS_VIEWED NUMBER
        )"""
    ]
    if execute_sql_list(cursor, sqls, "Creating DASHBOARD_ACCESS_AUDIT"):
        success += 1

    # 4. Report performance metrics
    sqls = [
        "USE DATABASE DEV_REPORTING",
        """CREATE OR REPLACE VIEW SECURITY_ANALYTICS.VW_REPORT_PERFORMANCE_METRICS AS
        SELECT
            REPORT_NAME,
            COUNT(*) as EXECUTION_COUNT,
            AVG(DATEDIFF(second, EXECUTION_START, EXECUTION_END)) as AVG_EXECUTION_TIME_SEC,
            MAX(DATEDIFF(second, EXECUTION_START, EXECUTION_END)) as MAX_EXECUTION_TIME_SEC,
            AVG(RECORDS_RETURNED) as AVG_RECORDS,
            COUNT(CASE WHEN STATUS = 'SUCCESS' THEN 1 END) * 100.0 / COUNT(*) as SUCCESS_RATE
        FROM SECURITY_ANALYTICS.REPORT_EXECUTION_LOG
        WHERE EXECUTION_START >= DATEADD('day', -30, CURRENT_DATE())
        GROUP BY REPORT_NAME"""
    ]
    if execute_sql_list(cursor, sqls, "Creating VW_REPORT_PERFORMANCE_METRICS"):
        success += 1

    # 5. User favorites/bookmarks
    sqls = [
        "USE DATABASE DEV_REPORTING",
        """CREATE OR REPLACE TABLE SECURITY_ANALYTICS.USER_REPORT_FAVORITES (
            FAVORITE_ID NUMBER AUTOINCREMENT PRIMARY KEY,
            USER_NAME VARCHAR,
            REPORT_NAME VARCHAR,
            DASHBOARD_NAME VARCHAR,
            ADDED_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
            LAST_ACCESSED TIMESTAMP,
            ACCESS_COUNT NUMBER DEFAULT 0
        )"""
    ]
    if execute_sql_list(cursor, sqls, "Creating USER_REPORT_FAVORITES"):
        success += 1

    # 6. Populate sample KPIs
    sqls = [
        "USE DATABASE DEV_REPORTING",
        """INSERT INTO SECURITY_ANALYTICS.KPI_DEFINITIONS
            (KPI_NAME, KPI_CATEGORY, KPI_DESCRIPTION, CALCULATION_LOGIC, TARGET_VALUE, WARNING_THRESHOLD, CRITICAL_THRESHOLD, UNIT_OF_MEASURE, UPDATE_FREQUENCY)
        SELECT * FROM (
            SELECT 'Critical Vulnerabilities', 'Security', 'Number of critical severity vulnerabilities', 'COUNT WHERE SEVERITY=5', 0, 10, 50, 'Count', 'Daily' UNION ALL
            SELECT 'Endpoint Coverage', 'Coverage', 'Percentage of endpoints with security tools', '(Covered/Total)*100', 100, 90, 80, 'Percentage', 'Daily' UNION ALL
            SELECT 'Mean Time to Remediate', 'Performance', 'Average days to fix vulnerabilities', 'AVG(DAYS_TO_FIX)', 7, 14, 30, 'Days', 'Weekly' UNION ALL
            SELECT 'Security Score', 'Compliance', 'Overall security posture score', 'Weighted calculation', 95, 85, 75, 'Score', 'Daily' UNION ALL
            SELECT 'Threat Detection Rate', 'Security', 'Percentage of threats detected', '(Detected/Total)*100', 99, 95, 90, 'Percentage', 'Hourly'
        )"""
    ]
    if execute_sql_list(cursor, sqls, "Populating sample KPIs"):
        success += 1

    print(f"\n[DONE] REPORTING layer: {success}/6 improvements")
    return success

def cross_layer_improvements(cursor):
    """Cross-layer views and procedures"""
    print("\n" + "="*80)
    print("CROSS-LAYER IMPROVEMENTS")
    print("="*80)

    success = 0

    # 1. End-to-end data flow view (in TRANSFORMATION)
    sqls = [
        "USE DATABASE DEV_TRANSFORMATION",
        """CREATE OR REPLACE VIEW SECURITY_ANALYTICS.VW_END_TO_END_DATA_FLOW AS
        SELECT
            'LANDING' as LAYER,
            l.TABLE_NAME,
            l.ROW_COUNT as RECORDS,
            l.LAST_ALTERED,
            'Source' as FLOW_TYPE
        FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES l
        WHERE l.TABLE_SCHEMA = 'SECURITY_ANALYTICS'
        UNION ALL
        SELECT
            'TRANSFORMATION' as LAYER,
            t.TABLE_NAME,
            t.ROW_COUNT as RECORDS,
            t.LAST_ALTERED,
            'Transform' as FLOW_TYPE
        FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES t
        WHERE t.TABLE_SCHEMA = 'SECURITY_ANALYTICS'
        UNION ALL
        SELECT
            'REPORTING' as LAYER,
            r.TABLE_NAME,
            r.ROW_COUNT as RECORDS,
            r.LAST_ALTERED,
            'Report' as FLOW_TYPE
        FROM DEV_REPORTING.INFORMATION_SCHEMA.TABLES r
        WHERE r.TABLE_SCHEMA = 'SECURITY_ANALYTICS'"""
    ]
    if execute_sql_list(cursor, sqls, "Creating VW_END_TO_END_DATA_FLOW"):
        success += 1

    # 2. Three-layer health dashboard (in TRANSFORMATION)
    sqls = [
        "USE DATABASE DEV_TRANSFORMATION",
        """CREATE OR REPLACE VIEW SECURITY_ANALYTICS.VW_THREE_LAYER_HEALTH_DASHBOARD AS
        SELECT
            'LANDING' as LAYER,
            COUNT(*) as TABLE_COUNT,
            SUM(ROW_COUNT) as TOTAL_RECORDS,
            COUNT(CASE WHEN ROW_COUNT = 0 THEN 1 END) as EMPTY_TABLES,
            SUM(BYTES) / (1024*1024*1024) as TOTAL_SIZE_GB,
            MAX(LAST_ALTERED) as LAST_UPDATE
        FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
        UNION ALL
        SELECT
            'TRANSFORMATION' as LAYER,
            COUNT(*) as TABLE_COUNT,
            SUM(ROW_COUNT) as TOTAL_RECORDS,
            COUNT(CASE WHEN ROW_COUNT = 0 THEN 1 END) as EMPTY_TABLES,
            SUM(BYTES) / (1024*1024*1024) as TOTAL_SIZE_GB,
            MAX(LAST_ALTERED) as LAST_UPDATE
        FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
        UNION ALL
        SELECT
            'REPORTING' as LAYER,
            COUNT(*) as TABLE_COUNT,
            SUM(ROW_COUNT) as TOTAL_RECORDS,
            COUNT(CASE WHEN ROW_COUNT = 0 THEN 1 END) as EMPTY_TABLES,
            SUM(BYTES) / (1024*1024*1024) as TOTAL_SIZE_GB,
            MAX(LAST_ALTERED) as LAST_UPDATE
        FROM DEV_REPORTING.INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'"""
    ]
    if execute_sql_list(cursor, sqls, "Creating VW_THREE_LAYER_HEALTH_DASHBOARD"):
        success += 1

    print(f"\n[DONE] Cross-layer improvements: {success}/2")
    return success

def generate_summary(results):
    """Generate implementation summary"""
    print("\n" + "="*80)
    print("THREE-LAYER IMPLEMENTATION SUMMARY")
    print("="*80)

    total = sum(results.values())
    print(f"\n[OK] Total improvements: {total}")
    print("\nBy layer:")
    for layer, count in results.items():
        print(f"  - {layer}: {count} items")

    with open("FINAL_DELIVERABLES/04_SQL_Scripts/THREE_LAYER_COMPLETE.sql", 'w') as f:
        f.write(f"-- SECURITY_ANALYTICS Three-Layer Complete Implementation\n")
        f.write(f"-- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"-- Total Improvements: {total}\n\n")
        for layer, count in results.items():
            f.write(f"-- {layer}: {count} items\n")

    print(f"\n[OK] Summary saved")
    return total

def main():
    print("="*80)
    print("SECURITY_ANALYTICS THREE-LAYER COMPLETE IMPLEMENTATION")
    print("DEV_LANDING + DEV_TRANSFORMATION + DEV_REPORTING")
    print("="*80)
    print(f"\nStart: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}

    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()

        # Layer 1: LANDING
        results["LANDING Layer"] = landing_layer_improvements(cursor)

        # Layer 2: TRANSFORMATION
        results["TRANSFORMATION Layer"] = transformation_layer_improvements(cursor)

        # Layer 3: REPORTING
        results["REPORTING Layer"] = reporting_layer_improvements(cursor)

        # Cross-Layer
        results["Cross-Layer"] = cross_layer_improvements(cursor)

        # Summary
        total = generate_summary(results)

        cursor.close()
        conn.close()

        print(f"\n[OK] Three-layer implementation complete!")
        print(f"End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return True

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
