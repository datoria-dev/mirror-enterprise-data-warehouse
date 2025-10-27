#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Execute Complete SECURITY_ANALYTICS Data Model Implementation
Implements all improvements including validation, monitoring, and performance optimization
"""

import snowflake.connector
from datetime import datetime
import os
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

class CompleteModelImplementer:
    """Complete implementation of all data model improvements"""

    def __init__(self):
        self.config = {
            'account': os.getenv('SNOWFLAKE_ACCOUNT', 'GenericCorp-CRH_EDW'),
            'user': os.getenv('SNOWFLAKE_USER', 'FUAD.ONATE@CompanyX.COM'),
            'authenticator': os.getenv('SNOWFLAKE_AUTHENTICATOR', 'externalbrowser'),
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'DEV_WH'),
            'role': os.getenv('SNOWFLAKE_ROLE', 'DEV_DEVELOPER')
        }
        self.conn = None
        self.cursor = None
        self.results = {
            'validation_views': 0,
            'monitoring_views': 0,
            'procedures': 0,
            'constraints_added': 0,
            'errors': []
        }

    def connect(self):
        """Connect to Snowflake"""
        print("\n" + "="*60)
        print("COMPLETE MODEL IMPLEMENTATION")
        print("="*60)
        print("\n[CONNECTING] Establishing Snowflake connection...")

        try:
            self.conn = snowflake.connector.connect(**self.config)
            self.cursor = self.conn.cursor()
            self.cursor.execute("USE DATABASE DEV_TRANSFORMATION")
            self.cursor.execute("USE SCHEMA SECURITY_ANALYTICS")
            print("[SUCCESS] Connected to Snowflake")
            return True
        except Exception as e:
            print(f"[ERROR] Connection failed: {str(e)}")
            return False

    def createte_validation_views(self):
        """Createte all validation views"""
        print("\n[PHASE 1] Createting Validation Views...")

        validation_views = [
            ('VW_PRIMARY_KEY_VALIDATION', """
                CREATE OR REPLACE VIEW VW_PRIMARY_KEY_VALIDATION AS
                WITH pk_status AS (
                    SELECT
                        t.TABLE_NAME,
                        t.ROW_COUNT,
                        CASE WHEN tc.CONSTRAINT_NAME IS NOT NULL THEN 'YES' ELSE 'NO' END as HAS_PK,
                        tc.CONSTRAINT_NAME as PK_NAME,
                        kcu.COLUMN_NAME as PK_COLUMN
                    FROM INFORMATION_SCHEMA.TABLES t
                    LEFT JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                        ON t.TABLE_NAME = tc.TABLE_NAME
                        AND t.TABLE_SCHEMA = tc.TABLE_SCHEMA
                        AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
                    LEFT JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
                        ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
                        AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
                    WHERE t.TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                    AND t.TABLE_TYPE = 'BASE TABLE'
                    AND t.TABLE_NAME LIKE 'DIM_%'
                )
                SELECT
                    TABLE_NAME,
                    ROW_COUNT,
                    HAS_PK,
                    PK_COLUMN,
                    CASE
                        WHEN HAS_PK = 'NO' AND ROW_COUNT > 0 THEN 'CRITICAL - Add PK'
                        WHEN HAS_PK = 'NO' AND ROW_COUNT = 0 THEN 'WARNING - Empty table needs PK'
                        ELSE 'OK'
                    END as STATUS
                FROM pk_status
                ORDER BY HAS_PK, ROW_COUNT DESC
            """),

            ('VW_FOREIGN_KEY_VALIDATION', """
                CREATE OR REPLACE VIEW VW_FOREIGN_KEY_VALIDATION AS
                WITH fk_status AS (
                    SELECT
                        t.TABLE_NAME as FACT_TABLE,
                        t.ROW_COUNT,
                        COUNT(DISTINCT tc.CONSTRAINT_NAME) as FK_COUNT,
                        LISTAGG(tc.CONSTRAINT_NAME, ', ') WITHIN GROUP (ORDER BY tc.CONSTRAINT_NAME) as FK_NAMES
                    FROM INFORMATION_SCHEMA.TABLES t
                    LEFT JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                        ON t.TABLE_NAME = tc.TABLE_NAME
                        AND t.TABLE_SCHEMA = tc.TABLE_SCHEMA
                        AND tc.CONSTRAINT_TYPE = 'FOREIGN KEY'
                    WHERE t.TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                    AND t.TABLE_TYPE = 'BASE TABLE'
                    AND t.TABLE_NAME LIKE 'FACT_%'
                    GROUP BY t.TABLE_NAME, t.ROW_COUNT
                )
                SELECT
                    FACT_TABLE,
                    ROW_COUNT,
                    FK_COUNT,
                    FK_NAMES,
                    CASE
                        WHEN FK_COUNT = 0 AND ROW_COUNT > 0 THEN 'CRITICAL - No FKs defined'
                        WHEN FK_COUNT = 0 AND ROW_COUNT = 0 THEN 'WARNING - Empty table needs FKs'
                        WHEN FK_COUNT < 2 THEN 'WARNING - May need more FKs'
                        ELSE 'OK'
                    END as STATUS
                FROM fk_status
                ORDER BY FK_COUNT, ROW_COUNT DESC
            """),

            ('VW_REFERENTIAL_INTEGRITY_CHECK', """
                CREATE OR REPLACE VIEW VW_REFERENTIAL_INTEGRITY_CHECK AS
                SELECT
                    'FACT_REMEDIATION_EVENTS' as TABLE_NAME,
                    'HOST_ID -> DIM_HOST' as RELATIONSHIP,
                    COUNT(DISTINCT f.HOST_ID) as FACT_VALUES,
                    COUNT(DISTINCT d.HOST_ID) as DIM_VALUES,
                    COUNT(DISTINCT f.HOST_ID) - COUNT(DISTINCT CASE WHEN d.HOST_ID IS NOT NULL THEN f.HOST_ID END) as ORPHANED_RECORDS
                FROM FACT_REMEDIATION_EVENTS f
                LEFT JOIN DIM_HOST d ON f.HOST_ID = d.HOST_ID
            """)
        ]

        for view_name, view_sql in validation_views:
            try:
                self.cursor.execute(view_sql)
                self.results['validation_views'] += 1
                print(f"  [SUCCESS] Createted {view_name}")
            except Exception as e:
                print(f"  [ERROR] Failed to createte {view_name}: {str(e)[:100]}")
                self.results['errors'].append(f"{view_name}: {str(e)[:100]}")

    def createte_monitoring_views(self):
        """Createte monitoring views"""
        print("\n[PHASE 2] Createting Monitoring Views...")

        monitoring_views = [
            ('VW_DATA_MODEL_HEALTH_DASHBOARD', """
                CREATE OR REPLACE VIEW VW_DATA_MODEL_HEALTH_DASHBOARD AS
                WITH health_metrics AS (
                    SELECT 'Primary Keys' as METRIC_TYPE, COUNT(DISTINCT TABLE_NAME) as COUNT
                    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
                    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS' AND CONSTRAINT_TYPE = 'PRIMARY KEY'
                    UNION ALL
                    SELECT 'Foreign Keys' as METRIC_TYPE, COUNT(DISTINCT TABLE_NAME) as COUNT
                    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
                    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS' AND CONSTRAINT_TYPE = 'FOREIGN KEY'
                    UNION ALL
                    SELECT 'Total Tables' as METRIC_TYPE, COUNT(*) as COUNT
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS' AND TABLE_TYPE = 'BASE TABLE'
                    UNION ALL
                    SELECT 'Empty Tables' as METRIC_TYPE, COUNT(*) as COUNT
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS' AND TABLE_TYPE = 'BASE TABLE' AND ROW_COUNT = 0
                )
                SELECT
                    METRIC_TYPE,
                    COUNT as METRIC_VALUE,
                    CASE
                        WHEN METRIC_TYPE = 'Empty Tables' AND COUNT > 10 THEN 'WARNING'
                        WHEN METRIC_TYPE = 'Primary Keys' AND COUNT < 20 THEN 'CRITICAL'
                        WHEN METRIC_TYPE = 'Foreign Keys' AND COUNT < 10 THEN 'CRITICAL'
                        ELSE 'OK'
                    END as STATUS
                FROM health_metrics
            """),

            ('VW_TABLE_GROWTH_MONITOR', """
                CREATE OR REPLACE VIEW VW_TABLE_GROWTH_MONITOR AS
                SELECT
                    TABLE_NAME,
                    TABLE_TYPE,
                    ROW_COUNT,
                    BYTES / 1024 / 1024 as SIZE_MB,
                    CREATED,
                    LAST_ALTERED,
                    CASE
                        WHEN ROW_COUNT = 0 THEN 'EMPTY'
                        WHEN ROW_COUNT < 1000 THEN 'SMALL'
                        WHEN ROW_COUNT < 100000 THEN 'MEDIUM'
                        WHEN ROW_COUNT < 1000000 THEN 'LARGE'
                        ELSE 'VERY LARGE'
                    END as SIZE_CATEGORY
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                AND TABLE_TYPE = 'BASE TABLE'
                ORDER BY ROW_COUNT DESC
            """),

            ('VW_DATA_QUALITY_MONITOR', """
                CREATE OR REPLACE VIEW VW_DATA_QUALITY_MONITOR AS
                SELECT
                    'NULL_CHECK' as CHECK_TYPE,
                    TABLE_NAME,
                    COLUMN_NAME,
                    IS_NULLABLE,
                    'Check for unexpected NULLs' as ISSUE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                AND TABLE_NAME LIKE 'FACT_%'
                AND COLUMN_NAME LIKE '%_ID'
                AND IS_NULLABLE = 'YES'
            """),

            ('VW_ETL_PIPELINE_STATUS', """
                CREATE OR REPLACE VIEW VW_ETL_PIPELINE_STATUS AS
                SELECT
                    t.TABLE_NAME,
                    t.ROW_COUNT,
                    t.BYTES / 1024 / 1024 as SIZE_MB,
                    t.LAST_ALTERED,
                    DATEDIFF(hour, t.LAST_ALTERED, CURRENT_TIMESTAMP()) as HOURS_SINCE_UPDATE,
                    CASE
                        WHEN t.ROW_COUNT = 0 THEN 'NOT_LOADED'
                        WHEN DATEDIFF(hour, t.LAST_ALTERED, CURRENT_TIMESTAMP()) > 48 THEN 'STALE'
                        WHEN DATEDIFF(hour, t.LAST_ALTERED, CURRENT_TIMESTAMP()) > 24 THEN 'WARNING'
                        ELSE 'CURRENT'
                    END as DATA_STATUS
                FROM INFORMATION_SCHEMA.TABLES t
                WHERE t.TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                AND t.TABLE_TYPE = 'BASE TABLE'
                ORDER BY t.TABLE_NAME
            """),

            ('VW_IMPLEMENTATION_SUMMARY', """
                CREATE OR REPLACE VIEW VW_IMPLEMENTATION_SUMMARY AS
                SELECT
                    'Model Implementation Summary' as REPORT_TITLE,
                    CURRENT_TIMESTAMP() as REPORT_DATE,
                    (SELECT COUNT(DISTINCT TABLE_NAME) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
                     WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS' AND CONSTRAINT_TYPE = 'PRIMARY KEY') as PRIMARY_KEYS,
                    (SELECT COUNT(DISTINCT TABLE_NAME) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
                     WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS' AND CONSTRAINT_TYPE = 'FOREIGN KEY') as FOREIGN_KEYS,
                    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
                     WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS' AND TABLE_TYPE = 'BASE TABLE') as TOTAL_TABLES,
                    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
                     WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS' AND TABLE_TYPE = 'BASE TABLE' AND ROW_COUNT = 0) as EMPTY_TABLES,
                    (SELECT SUM(BYTES) / 1024 / 1024 / 1024 FROM INFORMATION_SCHEMA.TABLES
                     WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS' AND TABLE_TYPE = 'BASE TABLE') as TOTAL_SIZE_GB
            """)
        ]

        for view_name, view_sql in monitoring_views:
            try:
                self.cursor.execute(view_sql)
                self.results['monitoring_views'] += 1
                print(f"  [SUCCESS] Createted {view_name}")
            except Exception as e:
                print(f"  [ERROR] Failed to createte {view_name}: {str(e)[:100]}")
                self.results['errors'].append(f"{view_name}: {str(e)[:100]}")

    def createte_procedures(self):
        """Createte stored procedures"""
        print("\n[PHASE 3] Createting Stored Procedures...")

        procedures = [
            ('SP_DAILY_HEALTH_CHECK', """
                CREATE OR REPLACE PROCEDURE SP_DAILY_HEALTH_CHECK()
                RETURNS VARCHAR
                LANGUAGE SQL
                AS
                $$
                DECLARE
                    v_message VARCHAR DEFAULT '';
                    v_pk_count NUMBER;
                    v_fk_count NUMBER;
                    v_empty_tables NUMBER;
                BEGIN
                    SELECT COUNT(DISTINCT TABLE_NAME) INTO v_pk_count
                    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
                    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                    AND CONSTRAINT_TYPE = 'PRIMARY KEY';

                    SELECT COUNT(DISTINCT TABLE_NAME) INTO v_fk_count
                    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
                    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                    AND CONSTRAINT_TYPE = 'FOREIGN KEY';

                    SELECT COUNT(*) INTO v_empty_tables
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                    AND TABLE_TYPE = 'BASE TABLE'
                    AND ROW_COUNT = 0;

                    v_message := 'HEALTH CHECK: PKs=' || v_pk_count ||
                                 ', FKs=' || v_fk_count ||
                                 ', Empty=' || v_empty_tables;

                    RETURN v_message;
                END;
                $$
            """),

            ('SP_DATA_QUALITY_ALERTS', """
                CREATE OR REPLACE PROCEDURE SP_DATA_QUALITY_ALERTS()
                RETURNS TABLE (ALERT_TYPE VARCHAR, TABLE_NAME VARCHAR, ISSUE VARCHAR, SEVERITY VARCHAR)
                LANGUAGE SQL
                AS
                $$
                DECLARE
                    res RESULTSET;
                BEGIN
                    res := (
                        SELECT
                            'EMPTY_FACT' as ALERT_TYPE,
                            TABLE_NAME,
                            'Fact table has no data' as ISSUE,
                            'HIGH' as SEVERITY
                        FROM INFORMATION_SCHEMA.TABLES
                        WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                        AND TABLE_TYPE = 'BASE TABLE'
                        AND TABLE_NAME LIKE 'FACT_%'
                        AND ROW_COUNT = 0
                    );
                    RETURN TABLE(res);
                END;
                $$
            """)
        ]

        for proc_name, proc_sql in procedures:
            try:
                self.cursor.execute(proc_sql)
                self.results['procedures'] += 1
                print(f"  [SUCCESS] Createted {proc_name}")
            except Exception as e:
                print(f"  [ERROR] Failed to createte {proc_name}: {str(e)[:100]}")
                self.results['errors'].append(f"{proc_name}: {str(e)[:100]}")

    def add_remaining_constraints(self):
        """Add any remaining constraints that were missed"""
        print("\n[PHASE 4] Adding Remaining Constraints...")

        # Get tables without PKs
        self.cursor.execute("""
            SELECT t.TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES t
            WHERE t.TABLE_SCHEMA = 'SECURITY_ANALYTICS'
            AND t.TABLE_TYPE = 'BASE TABLE'
            AND t.TABLE_NAME LIKE 'DIM_%'
            AND NOT EXISTS (
                SELECT 1 FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                WHERE tc.TABLE_NAME = t.TABLE_NAME
                AND tc.TABLE_SCHEMA = t.TABLE_SCHEMA
                AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
            )
        """)

        tables_without_pk = self.cursor.fetchall()

        for (table_name,) in tables_without_pk:
            # Find best PK candidate
            self.cursor.execute(f"""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                AND TABLE_NAME = '{table_name}'
                AND (COLUMN_NAME LIKE '%_ID' OR COLUMN_NAME LIKE '%_KEY' OR COLUMN_NAME = 'ID')
                ORDER BY ORDINAL_POSITION
                LIMIT 1
            """)

            result = self.cursor.fetchone()
            if result:
                pk_column = result[0]
                try:
                    self.cursor.execute(f"""
                        ALTER TABLE {table_name}
                        ADD CONSTRAINT PK_{table_name}
                        PRIMARY KEY ({pk_column}) RELY
                    """)
                    self.results['constraints_added'] += 1
                    print(f"  [SUCCESS] Added PK to {table_name}")
                except Exception as e:
                    if 'already exists' not in str(e).lower():
                        print(f"  [ERROR] Failed to add PK to {table_name}: {str(e)[:100]}")

    def run_validation_queries(self):
        """Run validation queries and display results"""
        print("\n[PHASE 5] Running Validation Queries...")

        # Check implementation summary
        self.cursor.execute("SELECT * FROM VW_IMPLEMENTATION_SUMMARY")
        result = self.cursor.fetchone()

        if result:
            print("\n" + "="*60)
            print("IMPLEMENTATION SUMMARY")
            print("="*60)
            print(f"  Report Date: {result[1]}")
            print(f"  Primary Keys: {result[2]}")
            print(f"  Foreign Keys: {result[3]}")
            print(f"  Total Tables: {result[4]}")
            print(f"  Empty Tables: {result[5]}")
            print(f"  Total Size: {result[6]:.2f} GB")

        # Check health dashboard
        self.cursor.execute("SELECT * FROM VW_DATA_MODEL_HEALTH_DASHBOARD ORDER BY STATUS, METRIC_TYPE")
        health_results = self.cursor.fetchall()

        print("\n" + "="*60)
        print("HEALTH DASHBOARD")
        print("="*60)
        for row in health_results:
            status_icon = "✓" if row[2] == "OK" else "⚠" if row[2] == "WARNING" else "✗"
            print(f"  [{status_icon}] {row[0]}: {row[1]} ({row[2]})")

    def generate_final_report(self):
        """Generate final implementation report"""
        print("\n" + "="*60)
        print("FINAL IMPLEMENTATION REPORT")
        print("="*60)

        print(f"\n[COMPLETED ACTIONS]")
        print(f"  Validation Views Createted: {self.results['validation_views']}")
        print(f"  Monitoring Views Createted: {self.results['monitoring_views']}")
        print(f"  Procedures Createted: {self.results['procedures']}")
        print(f"  Additional Constraints: {self.results['constraints_added']}")

        if self.results['errors']:
            print(f"\n[ERRORS ENCOUNTERED]")
            for error in self.results['errors'][:5]:
                print(f"  - {error}")

        # Save detailed report
        report_file = f"complete_implementation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w') as f:
            f.write("SECURITY_ANALYTICS COMPLETE MODEL IMPLEMENTATION REPORT\n")
            f.write(f"Generated: {datetime.now()}\n\n")
            f.write(f"Validation Views: {self.results['validation_views']}\n")
            f.write(f"Monitoring Views: {self.results['monitoring_views']}\n")
            f.write(f"Procedures: {self.results['procedures']}\n")
            f.write(f"Constraints Added: {self.results['constraints_added']}\n")

            if self.results['errors']:
                f.write("\nErrors:\n")
                for error in self.results['errors']:
                    f.write(f"  - {error}\n")

        print(f"\n[REPORT SAVED] {report_file}")

    def execute(self):
        """Execute complete implementation"""
        if not self.connect():
            return False

        try:
            self.createte_validation_views()
            self.createte_monitoring_views()
            self.createte_procedures()
            self.add_remaining_constraints()
            self.run_validation_queries()
            self.generate_final_report()

            print("\n" + "="*60)
            print("[SUCCESS] COMPLETE IMPLEMENTATION FINISHED")
            print("="*60)

            print("\n[NEXT STEPS]")
            print("1. Review the monitoring views:")
            print("   - VW_DATA_MODEL_HEALTH_DASHBOARD")
            print("   - VW_PRIMARY_KEY_VALIDATION")
            print("   - VW_FOREIGN_KEY_VALIDATION")
            print("   - VW_ETL_PIPELINE_STATUS")
            print("\n2. Run health check procedure:")
            print("   CALL SP_DAILY_HEALTH_CHECK();")
            print("\n3. Check for data quality alerts:")
            print("   CALL SP_DATA_QUALITY_ALERTS();")

            return True

        except Exception as e:
            print(f"\n[ERROR] Implementation failed: {str(e)}")
            return False

        finally:
            if self.conn:
                self.conn.close()


def main():
    """Main execution"""
    implementer = CompleteModelImplementer()
    success = implementer.execute()

    if success:
        print("\n[COMPLETE] All model improvements have been implemented successfully!")
    else:
        print("\n[PARTIAL] Implementation completed with some issues. Review the report.")

    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())