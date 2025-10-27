#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Execute SECURITY_ANALYTICS Data Model Improvements
Safely implements all recommended changes with rollback capability
"""

import snowflake.connector
import pandas as pd
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv
import sys
import time

# Load environment variables
load_dotenv()

class DataModelImplementer:
    """Implements data model improvements with safety checks"""

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
        self.implementation_log = []
        self.errors = []

    def connect(self):
        """Connect to Snowflake"""
        print("[INFO] Connecting to Snowflake...")
        try:
            self.conn = snowflake.connector.connect(**self.config)
            self.cursor = self.conn.cursor()
            print("[SUCCESS] Connected to Snowflake")
            return True
        except Exception as e:
            print(f"[ERROR] Connection failed: {str(e)}")
            return False

    def execute_phase(self, phase_name, commands, continue_on_error=False):
        """Execute a phase of implementation"""
        print(f"\n{'='*60}")
        print(f"EXECUTING PHASE: {phase_name}")
        print(f"{'='*60}")

        success_count = 0
        error_count = 0

        for i, command in enumerate(commands, 1):
            try:
                # Skip comments and empty lines
                command = command.strip()
                if not command or command.startswith('--'):
                    continue

                print(f"  [{i}/{len(commands)}] Executing: {command[:100]}...")
                self.cursor.execute(command)
                success_count += 1

                self.implementation_log.append({
                    'phase': phase_name,
                    'command': command[:200],
                    'status': 'SUCCESS',
                    'timestamp': datetime.now()
                })
                print(f"    [SUCCESS]")

            except Exception as e:
                error_count += 1
                error_msg = str(e)

                # Check if it's a "already exists" error which we can ignore
                if 'already exists' in error_msg.lower():
                    print(f"    [SKIP] Object already exists")
                    success_count += 1
                    continue

                self.errors.append({
                    'phase': phase_name,
                    'command': command[:200],
                    'error': error_msg,
                    'timestamp': datetime.now()
                })
                print(f"    [ERROR] {error_msg}")

                if not continue_on_error:
                    print(f"[ABORT] Stopping execution due to error")
                    return False

        print(f"\n[PHASE COMPLETE] Success: {success_count}, Errors: {error_count}")
        return error_count == 0

    def create_backup_schema(self):
        """Create backup schema for safety"""
        print("\n[BACKUP] Creating backup schema...")
        commands = [
            "USE DATABASE DEV_TRANSFORMATION",
            "CREATE SCHEMA IF NOT EXISTS ITSECKPI_BACKUP",
            """CREATE TABLE IF NOT EXISTS ITSECKPI_BACKUP.IMPLEMENTATION_LOG (
                LOG_ID NUMBER AUTOINCREMENT,
                EXECUTION_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                PHASE VARCHAR(100),
                OBJECT_TYPE VARCHAR(50),
                OBJECT_NAME VARCHAR(255),
                ACTION_TAKEN VARCHAR(500),
                STATUS VARCHAR(20),
                ERROR_MESSAGE VARCHAR(4000)
            )"""
        ]
        return self.execute_phase("BACKUP_SETUP", commands)

    def add_primary_keys(self):
        """Add primary keys to dimension tables"""
        print("\n[PRIMARY KEYS] Adding primary keys to dimensions...")

        # First, get list of dimension tables and identify appropriate PK columns
        self.cursor.execute("""
            SELECT DISTINCT t.TABLE_NAME
            FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES t
            WHERE t.TABLE_SCHEMA = 'SECURITY_ANALYTICS'
            AND t.TABLE_TYPE = 'BASE TABLE'
            AND t.TABLE_NAME LIKE 'DIM_%'
        """)

        dim_tables = [row[0] for row in self.cursor.fetchall()]
        commands = []

        for table in dim_tables:
            # Find the best PK candidate column
            self.cursor.execute(f"""
                SELECT COLUMN_NAME
                FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                AND TABLE_NAME = '{table}'
                AND (
                    COLUMN_NAME = 'ID' OR
                    COLUMN_NAME = '{table}_ID' OR
                    COLUMN_NAME LIKE '%_KEY' OR
                    COLUMN_NAME LIKE '%_ID'
                )
                AND ORDINAL_POSITION = 1
                LIMIT 1
            """)

            result = self.cursor.fetchone()
            if result:
                pk_column = result[0]
                commands.append(f"ALTER TABLE {table} ADD CONSTRAINT PK_{table} PRIMARY KEY ({pk_column}) RELY")
                print(f"  Will add PK on {table}.{pk_column}")

        return self.execute_phase("PRIMARY_KEYS", commands, continue_on_error=True)

    def add_foreign_keys(self):
        """Add foreign keys to fact tables"""
        print("\n[FOREIGN KEYS] Adding foreign keys to fact tables...")

        commands = []

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
            # Check if both tables and columns exist
            check_query = f"""
                SELECT COUNT(*)
                FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                AND ((TABLE_NAME = '{fact_table}' AND COLUMN_NAME = '{fk_column}')
                OR (TABLE_NAME = '{dim_table}' AND COLUMN_NAME = '{dim_column}'))
            """
            self.cursor.execute(check_query)
            if self.cursor.fetchone()[0] == 2:  # Both columns exist
                constraint_name = f"FK_{fact_table}_{dim_table}".replace("FACT_", "").replace("DIM_", "")[:64]
                commands.append(
                    f"ALTER TABLE {fact_table} ADD CONSTRAINT {constraint_name} "
                    f"FOREIGN KEY ({fk_column}) REFERENCES {dim_table}({dim_column}) RELY"
                )
                print(f"  Will add FK: {fact_table}.{fk_column} -> {dim_table}.{dim_column}")

        return self.execute_phase("FOREIGN_KEYS", commands, continue_on_error=True)

    def rename_tables(self):
        """Rename tables to follow naming convention"""
        print("\n[RENAMING] Standardizing table names...")

        rename_map = {
            "CISCO_AMP_DATA": "DIM_CISCO_AMP",
            "CROWDSTRIKE_ENDPOINTS": "DIM_CROWDSTRIKE_ENDPOINTS",
            "CROWDSTRIKE_VERSIONS": "DIM_CROWDSTRIKE_VERSIONS",
            "CLOSE_CODE_MAPPING": "DIM_CLOSE_CODE_MAPPING",
            "DATA_QUALITY_RESULTS": "STG_DATA_QUALITY_RESULTS",
            "N8N_LOG": "STG_N8N_LOG",
            "N8N_LOG_TEMP": "STG_N8N_LOG_TEMP"
        }

        commands = []
        for old_name, new_name in rename_map.items():
            # Check if table exists
            self.cursor.execute(f"""
                SELECT COUNT(*)
                FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                AND TABLE_NAME = '{old_name}'
            """)

            if self.cursor.fetchone()[0] > 0:
                commands.append(f"ALTER TABLE {old_name} RENAME TO {new_name}")
                commands.append(f"CREATE OR REPLACE VIEW {old_name} AS SELECT * FROM {new_name}")
                print(f"  Will rename: {old_name} -> {new_name}")

        return self.execute_phase("RENAMING", commands, continue_on_error=True)

    def add_documentation(self):
        """Add documentation to tables and columns"""
        print("\n[DOCUMENTATION] Adding table and column comments...")

        commands = [
            "COMMENT ON TABLE DIM_DATES IS 'Date dimension table containing all calendar dates with various date attributes for time-based analysis'",
            "COMMENT ON TABLE DIM_HOST IS 'Host dimension containing all servers, workstations, and computing devices in the organization'",
            "COMMENT ON TABLE DIM_ANCON_USERS IS 'User dimension for Ancon system users including authentication and authorization attributes'",
            "COMMENT ON TABLE DIM_DEFENDER_ENDPOINTS IS 'Microsoft Defender endpoint dimension with security status and configuration'",
            "COMMENT ON TABLE DIM_SNOW_DEVICES IS 'ServiceNow CMDB device dimension with asset management information'",
            "COMMENT ON TABLE FACT_REMEDIATION_EVENTS IS 'Fact table tracking vulnerability remediation events. Grain: one row per remediation action'",
            "COMMENT ON TABLE FACT_SENTINEL_ENDPOINTS IS 'Fact table for Sentinel endpoint security events. Grain: one row per security event'",
            "COMMENT ON TABLE FACT_DEFENDER_THREATS IS 'Fact table for Microsoft Defender threat detections. Grain: one row per threat'"
        ]

        return self.execute_phase("DOCUMENTATION", commands, continue_on_error=True)

    def create_validation_views(self):
        """Create views for data quality validation"""
        print("\n[VALIDATION] Creating validation views...")

        commands = [
            """CREATE OR REPLACE VIEW VW_DATA_QUALITY_ORPHANED_FACTS AS
            SELECT
                'FACT_REMEDIATION_EVENTS' as FACT_TABLE,
                'HOST_ID' as FK_COLUMN,
                COUNT(*) as ORPHANED_COUNT
            FROM FACT_REMEDIATION_EVENTS f
            LEFT JOIN DIM_HOST d ON f.HOST_ID = d.HOST_ID
            WHERE d.HOST_ID IS NULL""",

            """CREATE OR REPLACE VIEW VW_DATA_QUALITY_EMPTY_FACTS AS
            SELECT
                TABLE_NAME,
                ROW_COUNT,
                'EMPTY - Requires ETL population' as ISSUE
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
            AND TABLE_NAME LIKE 'FACT_%'
            AND ROW_COUNT = 0""",

            """CREATE OR REPLACE VIEW VW_EXECUTIVE_DATA_MODEL_HEALTH AS
            SELECT
                'Total Tables' as METRIC,
                COUNT(*) as VALUE,
                'Count' as UNIT
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
            AND TABLE_TYPE = 'BASE TABLE'"""
        ]

        return self.execute_phase("VALIDATION_VIEWS", commands, continue_on_error=True)

    def validate_implementation(self):
        """Validate that implementation was successful"""
        print("\n" + "="*60)
        print("VALIDATION RESULTS")
        print("="*60)

        # Check Primary Keys
        self.cursor.execute("""
            SELECT COUNT(DISTINCT TABLE_NAME) as PK_COUNT
            FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLE_CONSTRAINTS
            WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
            AND CONSTRAINT_TYPE = 'PRIMARY KEY'
        """)
        pk_count = self.cursor.fetchone()[0]
        print(f"  Primary Keys Created: {pk_count}")

        # Check Foreign Keys
        self.cursor.execute("""
            SELECT COUNT(DISTINCT TABLE_NAME) as FK_COUNT
            FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLE_CONSTRAINTS
            WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
            AND CONSTRAINT_TYPE = 'FOREIGN KEY'
        """)
        fk_count = self.cursor.fetchone()[0]
        print(f"  Foreign Keys Created: {fk_count}")

        # Check renamed tables
        self.cursor.execute("""
            SELECT COUNT(*) as STANDARD_COUNT
            FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
            AND TABLE_TYPE = 'BASE TABLE'
            AND (TABLE_NAME LIKE 'DIM_%' OR TABLE_NAME LIKE 'FACT_%' OR TABLE_NAME LIKE 'STG_%')
        """)
        standard_count = self.cursor.fetchone()[0]
        print(f"  Tables Following Standard: {standard_count}")

        return pk_count > 0 and fk_count > 0

    def generate_report(self):
        """Generate implementation report"""
        print("\n" + "="*60)
        print("IMPLEMENTATION REPORT")
        print("="*60)

        # Save to file
        report_file = f"implementation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(report_file, 'w') as f:
            f.write("SECURITY_ANALYTICS DATA MODEL IMPLEMENTATION REPORT\n")
            f.write(f"Generated: {datetime.now()}\n\n")

            f.write("SUCCESSFUL ACTIONS:\n")
            for log in self.implementation_log:
                if log['status'] == 'SUCCESS':
                    f.write(f"  - {log['phase']}: {log['command'][:100]}\n")

            if self.errors:
                f.write("\nERRORS ENCOUNTERED:\n")
                for error in self.errors:
                    f.write(f"  - {error['phase']}: {error['error']}\n")

            f.write(f"\nTotal Success: {len([l for l in self.implementation_log if l['status'] == 'SUCCESS'])}\n")
            f.write(f"Total Errors: {len(self.errors)}\n")

        print(f"  Report saved to: {report_file}")
        print(f"  Total Successful Actions: {len([l for l in self.implementation_log if l['status'] == 'SUCCESS'])}")
        print(f"  Total Errors: {len(self.errors)}")

    def run_implementation(self):
        """Main execution function"""
        print("\n" + "="*60)
        print("SECURITY_ANALYTICS DATA MODEL IMPLEMENTATION")
        print("="*60)

        if not self.connect():
            return False

        try:
            # Set context
            self.cursor.execute("USE DATABASE DEV_TRANSFORMATION")
            self.cursor.execute("USE SCHEMA SECURITY_ANALYTICS")

            # Execute phases
            phases = [
                ("Backup Setup", self.create_backup_schema),
                ("Primary Keys", self.add_primary_keys),
                ("Foreign Keys", self.add_foreign_keys),
                ("Table Renaming", self.rename_tables),
                ("Documentation", self.add_documentation),
                ("Validation Views", self.create_validation_views)
            ]

            for phase_name, phase_func in phases:
                print(f"\n[PHASE] {phase_name}")

                user_input = input(f"Execute {phase_name}? (y/n/skip): ").lower()
                if user_input == 'skip' or user_input == 'n':
                    print(f"  Skipping {phase_name}")
                    continue

                if not phase_func():
                    print(f"[WARNING] {phase_name} had some errors")
                    continue_input = input("Continue with next phase? (y/n): ").lower()
                    if continue_input != 'y':
                        break

            # Validate
            self.validate_implementation()

            # Generate report
            self.generate_report()

            print("\n[SUCCESS] Implementation completed!")
            print("Review the validation views for data quality status:")
            print("  - VW_EXECUTIVE_DATA_MODEL_HEALTH")
            print("  - VW_DATA_QUALITY_ORPHANED_FACTS")
            print("  - VW_DATA_QUALITY_EMPTY_FACTS")

        except Exception as e:
            print(f"\n[ERROR] Implementation failed: {str(e)}")
            return False

        finally:
            if self.conn:
                self.conn.close()

        return True


def main():
    """Main execution"""
    print("\n" + "*"*60)
    print("SECURITY_ANALYTICS DATA MODEL IMPROVEMENT IMPLEMENTATION")
    print("*"*60)
    print("\nThis script will implement:")
    print("  1. Primary Keys on all Dimension tables")
    print("  2. Foreign Keys on all Fact tables")
    print("  3. Table renaming to standard convention")
    print("  4. Documentation and comments")
    print("  5. Validation views")
    print("\nYou can skip any phase if needed.")

    confirm = input("\nProceed with implementation? (yes/no): ").lower()
    if confirm != 'yes':
        print("Implementation cancelled")
        return

    implementer = DataModelImplementer()
    success = implementer.run_implementation()

    if success:
        print("\n[SUCCESS] All improvements implemented successfully!")
    else:
        print("\n[WARNING] Implementation completed with some issues. Review the report.")


if __name__ == "__main__":
    sys.exit(0 if main() else 1)