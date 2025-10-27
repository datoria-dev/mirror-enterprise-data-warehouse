#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated execution of SECURITY_ANALYTICS Data Model Improvements
Runs without user interaction for automated deployment
"""

import snowflake.connector
from datetime import datetime
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

def execute_improvements():
    """Execute all data model improvements automatically"""

    print("\n" + "="*60)
    print("AUTOMATED DATA MODEL IMPLEMENTATION")
    print("Starting at:", datetime.now())
    print("="*60)

    # Connection configuration
    config = {
        'account': os.getenv('SNOWFLAKE_ACCOUNT', 'GenericCorp-CRH_EDW'),
        'user': os.getenv('SNOWFLAKE_USER', 'FUAD.ONATE@CompanyX.COM'),
        'authenticator': os.getenv('SNOWFLAKE_AUTHENTICATOR', 'externalbrowser'),
        'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'DEV_WH'),
        'role': os.getenv('SNOWFLAKE_ROLE', 'DEV_DEVELOPER')
    }

    results = {
        'start_time': datetime.now().isoformat(),
        'phases': {},
        'errors': [],
        'summary': {}
    }

    try:
        print("\n[CONNECTING] Establishing Snowflake connection...")
        conn = snowflake.connector.connect(**config)
        cursor = conn.cursor()
        print("[SUCCESS] Connected to Snowflake")

        # Set context
        cursor.execute("USE DATABASE DEV_TRANSFORMATION")
        cursor.execute("USE SCHEMA SECURITY_ANALYTICS")

        # Phase 1: Create backup schema
        print("\n[PHASE 1] Creating backup schema...")
        try:
            cursor.execute("CREATE SCHEMA IF NOT EXISTS ITSECKPI_BACKUP")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ITSECKPI_BACKUP.IMPLEMENTATION_LOG (
                    LOG_ID NUMBER AUTOINCREMENT,
                    EXECUTION_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                    PHASE VARCHAR(100),
                    ACTION VARCHAR(500),
                    STATUS VARCHAR(20)
                )
            """)
            results['phases']['backup'] = 'SUCCESS'
            print("  [SUCCESS] Backup schema created")
        except Exception as e:
            results['phases']['backup'] = f'ERROR: {str(e)}'
            print(f"  [ERROR] {str(e)}")

        # Phase 2: Add Primary Keys to Dimensions
        print("\n[PHASE 2] Adding Primary Keys to Dimension tables...")
        pk_count = 0
        pk_errors = 0

        # Get dimension tables
        cursor.execute("""
            SELECT DISTINCT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
            AND TABLE_TYPE = 'BASE TABLE'
            AND TABLE_NAME LIKE 'DIM_%'
        """)
        dim_tables = cursor.fetchall()

        for (table_name,) in dim_tables:
            try:
                # Find best PK candidate
                cursor.execute(f"""
                    SELECT COLUMN_NAME
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                    AND TABLE_NAME = '{table_name}'
                    AND (
                        COLUMN_NAME = 'ID' OR
                        COLUMN_NAME = '{table_name}_ID' OR
                        COLUMN_NAME LIKE '%_KEY' OR
                        COLUMN_NAME LIKE '%_ID'
                    )
                    ORDER BY ORDINAL_POSITION
                    LIMIT 1
                """)
                result = cursor.fetchone()

                if result:
                    pk_column = result[0]
                    try:
                        cursor.execute(f"""
                            ALTER TABLE {table_name}
                            ADD CONSTRAINT PK_{table_name}
                            PRIMARY KEY ({pk_column}) RELY
                        """)
                        pk_count += 1
                        print(f"  [SUCCESS] Added PK to {table_name}.{pk_column}")
                    except Exception as e:
                        if 'already exists' in str(e).lower():
                            print(f"  [SKIP] PK already exists on {table_name}")
                        else:
                            pk_errors += 1
                            print(f"  [ERROR] Failed to add PK to {table_name}: {str(e)[:100]}")
            except Exception as e:
                pk_errors += 1
                print(f"  [ERROR] Error processing {table_name}: {str(e)[:100]}")

        results['phases']['primary_keys'] = f'Added {pk_count} PKs, {pk_errors} errors'

        # Phase 3: Add Foreign Keys to Facts
        print("\n[PHASE 3] Adding Foreign Keys to Fact tables...")
        fk_count = 0
        fk_errors = 0

        # Define known relationships
        relationships = [
            ("FACT_REMEDIATION_EVENTS", "HOST_ID", "DIM_HOST", "HOST_ID"),
            ("FACT_REMEDIATION_EVENTS", "DATE_KEY", "DIM_DATES", "DATE_KEY"),
            ("FACT_SENTINEL_ENDPOINTS", "DEVICE_ID", "DIM_SNOW_DEVICES", "DEVICE_ID"),
            ("FACT_DEFENDER_THREATS", "DEVICE_ID", "DIM_SNOW_DEVICES", "DEVICE_ID"),
            ("FACT_CYBELANGEL_THREATS", "ALERT_KEY", "DIM_CYBELANGEL_ALERTS", "ALERT_KEY"),
            ("FACT_QUALYS_HOST_SCANS", "HOST_KEY", "DIM_HOST", "HOST_ID"),
            ("FACT_BITSIGHT_FINDINGS", "RISK_VECTOR_ID", "DIM_BITSIGHT_RISK_VECTORS", "RISK_VECTOR_ID"),
            ("FACT_AV_HEALTH", "OPCO_ID", "DIM_AV_OPCO", "OPCO_ID"),
        ]

        for fact_table, fk_column, dim_table, dim_column in relationships:
            try:
                # Check if both columns exist
                cursor.execute(f"""
                    SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                    AND ((TABLE_NAME = '{fact_table}' AND COLUMN_NAME = '{fk_column}')
                    OR (TABLE_NAME = '{dim_table}' AND COLUMN_NAME = '{dim_column}'))
                """)
                if cursor.fetchone()[0] == 2:
                    constraint_name = f"FK_{fact_table}_{dim_table}".replace("FACT_", "").replace("DIM_", "")[:64]
                    try:
                        cursor.execute(f"""
                            ALTER TABLE {fact_table}
                            ADD CONSTRAINT {constraint_name}
                            FOREIGN KEY ({fk_column})
                            REFERENCES {dim_table}({dim_column}) RELY
                        """)
                        fk_count += 1
                        print(f"  [SUCCESS] Added FK: {fact_table}.{fk_column} -> {dim_table}.{dim_column}")
                    except Exception as e:
                        if 'already exists' in str(e).lower():
                            print(f"  [SKIP] FK already exists for {fact_table}")
                        else:
                            fk_errors += 1
                            print(f"  [ERROR] Failed to add FK: {str(e)[:100]}")
            except Exception as e:
                fk_errors += 1
                print(f"  [ERROR] Error processing relationship: {str(e)[:100]}")

        results['phases']['foreign_keys'] = f'Added {fk_count} FKs, {fk_errors} errors'

        # Phase 4: Add Documentation
        print("\n[PHASE 4] Adding documentation to tables...")
        doc_count = 0

        documentation = {
            "DIM_DATES": "Date dimension table containing all calendar dates with various date attributes for time-based analysis",
            "DIM_HOST": "Host dimension containing all servers, workstations, and computing devices in the organization",
            "DIM_ANCON_USERS": "User dimension for Ancon system users including authentication and authorization attributes",
            "DIM_DEFENDER_ENDPOINTS": "Microsoft Defender endpoint dimension with security status and configuration",
            "DIM_SNOW_DEVICES": "ServiceNow CMDB device dimension with asset management information",
            "DIM_CYBELANGEL_ALERTS": "CybelAngel security alert dimension with threat intelligence data",
            "DIM_HARDWARE_INVENTORY": "Hardware inventory dimension with device specifications and lifecycle data",
            "DIM_FIXED_VULNERABILITIES": "Resolved vulnerability dimension tracking remediated security issues",
            "FACT_REMEDIATION_EVENTS": "Fact table tracking vulnerability remediation events. Grain: one row per remediation action",
            "FACT_SENTINEL_ENDPOINTS": "Fact table for Sentinel endpoint security events. Grain: one row per security event",
            "FACT_DEFENDER_THREATS": "Fact table for Microsoft Defender threat detections. Grain: one row per threat",
            "FACT_QUALYS_HOST_SCANS": "Fact table for Qualys vulnerability scan results. Grain: one row per scan"
        }

        for table_name, comment in documentation.items():
            try:
                cursor.execute(f"COMMENT ON TABLE {table_name} IS '{comment}'")
                doc_count += 1
                print(f"  [SUCCESS] Documented {table_name}")
            except Exception as e:
                print(f"  [ERROR] Failed to document {table_name}: {str(e)[:100]}")

        results['phases']['documentation'] = f'Documented {doc_count} tables'

        # Phase 5: Create Validation Views
        print("\n[PHASE 5] Creating validation views...")
        view_count = 0

        validation_views = [
            ("VW_DATA_QUALITY_ORPHANED_FACTS", """
                CREATE OR REPLACE VIEW VW_DATA_QUALITY_ORPHANED_FACTS AS
                SELECT
                    'FACT_REMEDIATION_EVENTS' as FACT_TABLE,
                    'HOST_ID' as FK_COLUMN,
                    COUNT(*) as ORPHANED_COUNT
                FROM FACT_REMEDIATION_EVENTS f
                LEFT JOIN DIM_HOST d ON f.HOST_ID = d.HOST_ID
                WHERE d.HOST_ID IS NULL
            """),
            ("VW_DATA_QUALITY_EMPTY_FACTS", """
                CREATE OR REPLACE VIEW VW_DATA_QUALITY_EMPTY_FACTS AS
                SELECT
                    TABLE_NAME,
                    ROW_COUNT,
                    'EMPTY - Requires ETL population' as ISSUE
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                AND TABLE_NAME LIKE 'FACT_%'
                AND ROW_COUNT = 0
            """),
            ("VW_MODEL_HEALTH_SUMMARY", """
                CREATE OR REPLACE VIEW VW_MODEL_HEALTH_SUMMARY AS
                SELECT
                    'Total Tables' as METRIC,
                    COUNT(*) as VALUE
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                AND TABLE_TYPE = 'BASE TABLE'
            """)
        ]

        for view_name, view_sql in validation_views:
            try:
                cursor.execute(view_sql)
                view_count += 1
                print(f"  [SUCCESS] Created {view_name}")
            except Exception as e:
                print(f"  [ERROR] Failed to create {view_name}: {str(e)[:100]}")

        results['phases']['validation_views'] = f'Created {view_count} views'

        # Final Validation
        print("\n[VALIDATION] Checking implementation results...")

        # Count PKs
        cursor.execute("""
            SELECT COUNT(DISTINCT TABLE_NAME)
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
            WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
            AND CONSTRAINT_TYPE = 'PRIMARY KEY'
        """)
        final_pk_count = cursor.fetchone()[0]

        # Count FKs
        cursor.execute("""
            SELECT COUNT(DISTINCT TABLE_NAME)
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
            WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
            AND CONSTRAINT_TYPE = 'FOREIGN KEY'
        """)
        final_fk_count = cursor.fetchone()[0]

        results['summary'] = {
            'total_primary_keys': final_pk_count,
            'total_foreign_keys': final_fk_count,
            'primary_keys_added': pk_count,
            'foreign_keys_added': fk_count,
            'tables_documented': doc_count,
            'views_created': view_count
        }

        print(f"\n[SUMMARY]")
        print(f"  Total Primary Keys: {final_pk_count}")
        print(f"  Total Foreign Keys: {final_fk_count}")
        print(f"  Tables Documented: {doc_count}")
        print(f"  Validation Views: {view_count}")

        # Close connection
        conn.close()

    except Exception as e:
        results['errors'].append(str(e))
        print(f"\n[CRITICAL ERROR] {str(e)}")
        return False

    # Save results to file
    results['end_time'] = datetime.now().isoformat()
    results_file = f"implementation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n[COMPLETE] Results saved to {results_file}")
    print("="*60)

    return True

if __name__ == "__main__":
    success = execute_improvements()
    print(f"\n{'SUCCESS' if success else 'FAILED'}: Data model improvements {'completed' if success else 'encountered errors'}")
    import sys
    sys.exit(0 if success else 1)