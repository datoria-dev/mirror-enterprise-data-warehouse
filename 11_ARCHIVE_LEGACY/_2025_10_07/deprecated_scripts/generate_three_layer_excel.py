"""
Generate Comprehensive Excel Documentation for All Three Layers
"""

import snowflake.connector
import pandas as pd
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

def generate_three_layer_excel(conn):
    """Generate comprehensive Excel for all three layers"""
    cursor = conn.cursor()

    print("\n" + "="*70)
    print("GENERATING THREE-LAYER EXCEL DOCUMENTATION")
    print("="*70)

    excel_file = "FINAL_DELIVERABLES/03_Excel_DataModel/THREE_LAYER_COMPLETE_ANALYSIS.xlsx"

    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:

        # 1. EXECUTIVE SUMMARY
        print("\n[CREATING] Executive Summary...")
        summary_data = {
            'Layer': ['DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING', 'TOTAL'],
            'Schemas': [15, 17, 14, 46],
            'Tables': [879, 1655, 314, 2848],
            'Views': [11, 157, 246, 414],
            'Total_Records': ['1,024,249,508', '1,813,943,259', '851,523,856', '3,689,716,623'],
            'Primary_Keys': [10, 67, 21, 98],
            'Foreign_Keys': [2, 18, 0, 20],
            'PK_Coverage_%': ['1.1%', '4.0%', '6.7%', '3.4%'],
            'FK_Coverage_%': ['0.2%', '1.1%', '0.0%', '0.7%']
        }
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Executive_Summary', index=False)
        print("  [SUCCESS] Executive Summary created")

        # 2. LANDING LAYER DETAILS
        print("\n[CREATING] Landing Layer sheet...")
        cursor.execute("""
            SELECT
                s.CATALOG_NAME as DATABASE_NAME,
                s.SCHEMA_NAME,
                COUNT(DISTINCT t.TABLE_NAME) as TABLE_COUNT,
                SUM(t.ROW_COUNT) as TOTAL_ROWS,
                COUNT(DISTINCT CASE WHEN tc.CONSTRAINT_TYPE = 'PRIMARY KEY' THEN tc.TABLE_NAME END) as TABLES_WITH_PK,
                COUNT(DISTINCT CASE WHEN tc.CONSTRAINT_TYPE = 'FOREIGN KEY' THEN tc.TABLE_NAME END) as TABLES_WITH_FK
            FROM DEV_LANDING.INFORMATION_SCHEMA.SCHEMATA s
            LEFT JOIN DEV_LANDING.INFORMATION_SCHEMA.TABLES t
                ON s.SCHEMA_NAME = t.TABLE_SCHEMA
                AND t.TABLE_TYPE = 'BASE TABLE'
            LEFT JOIN DEV_LANDING.INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                ON t.TABLE_SCHEMA = tc.TABLE_SCHEMA
                AND t.TABLE_NAME = tc.TABLE_NAME
            WHERE s.SCHEMA_NAME NOT IN ('INFORMATION_SCHEMA', 'PUBLIC')
            GROUP BY s.CATALOG_NAME, s.SCHEMA_NAME
            ORDER BY TOTAL_ROWS DESC
        """)

        landing_data = cursor.fetchall()
        df_landing = pd.DataFrame(landing_data, columns=[
            'Database', 'Schema', 'Tables', 'Total_Rows', 'Tables_with_PK', 'Tables_with_FK'
        ])
        df_landing['Data_Quality'] = df_landing.apply(
            lambda row: 'GOOD' if row['Tables_with_PK'] > 0 else 'POOR', axis=1
        )
        df_landing.to_excel(writer, sheet_name='DEV_LANDING', index=False)
        print("  [SUCCESS] Landing Layer sheet created")

        # 3. TRANSFORMATION LAYER DETAILS
        print("\n[CREATING] Transformation Layer sheet...")
        cursor.execute("""
            SELECT
                s.CATALOG_NAME as DATABASE_NAME,
                s.SCHEMA_NAME,
                COUNT(DISTINCT t.TABLE_NAME) as TABLE_COUNT,
                SUM(t.ROW_COUNT) as TOTAL_ROWS,
                COUNT(DISTINCT CASE WHEN tc.CONSTRAINT_TYPE = 'PRIMARY KEY' THEN tc.TABLE_NAME END) as TABLES_WITH_PK,
                COUNT(DISTINCT CASE WHEN tc.CONSTRAINT_TYPE = 'FOREIGN KEY' THEN tc.TABLE_NAME END) as TABLES_WITH_FK
            FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.SCHEMATA s
            LEFT JOIN DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES t
                ON s.SCHEMA_NAME = t.TABLE_SCHEMA
                AND t.TABLE_TYPE = 'BASE TABLE'
            LEFT JOIN DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                ON t.TABLE_SCHEMA = tc.TABLE_SCHEMA
                AND t.TABLE_NAME = tc.TABLE_NAME
            WHERE s.SCHEMA_NAME NOT IN ('INFORMATION_SCHEMA', 'PUBLIC')
            GROUP BY s.CATALOG_NAME, s.SCHEMA_NAME
            ORDER BY TOTAL_ROWS DESC
        """)

        transformation_data = cursor.fetchall()
        df_transformation = pd.DataFrame(transformation_data, columns=[
            'Database', 'Schema', 'Tables', 'Total_Rows', 'Tables_with_PK', 'Tables_with_FK'
        ])
        df_transformation['Data_Quality'] = df_transformation.apply(
            lambda row: 'EXCELLENT' if row['Tables_with_PK'] > 50
            else 'GOOD' if row['Tables_with_PK'] > 10
            else 'POOR', axis=1
        )
        df_transformation.to_excel(writer, sheet_name='DEV_TRANSFORMATION', index=False)
        print("  [SUCCESS] Transformation Layer sheet created")

        # 4. REPORTING LAYER DETAILS
        print("\n[CREATING] Reporting Layer sheet...")
        cursor.execute("""
            SELECT
                s.CATALOG_NAME as DATABASE_NAME,
                s.SCHEMA_NAME,
                COUNT(DISTINCT t.TABLE_NAME) as TABLE_COUNT,
                SUM(t.ROW_COUNT) as TOTAL_ROWS,
                COUNT(DISTINCT CASE WHEN tc.CONSTRAINT_TYPE = 'PRIMARY KEY' THEN tc.TABLE_NAME END) as TABLES_WITH_PK,
                COUNT(DISTINCT CASE WHEN tc.CONSTRAINT_TYPE = 'FOREIGN KEY' THEN tc.TABLE_NAME END) as TABLES_WITH_FK
            FROM DEV_REPORTING.INFORMATION_SCHEMA.SCHEMATA s
            LEFT JOIN DEV_REPORTING.INFORMATION_SCHEMA.TABLES t
                ON s.SCHEMA_NAME = t.TABLE_SCHEMA
                AND t.TABLE_TYPE = 'BASE TABLE'
            LEFT JOIN DEV_REPORTING.INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                ON t.TABLE_SCHEMA = tc.TABLE_SCHEMA
                AND t.TABLE_NAME = tc.TABLE_NAME
            WHERE s.SCHEMA_NAME NOT IN ('INFORMATION_SCHEMA', 'PUBLIC')
            GROUP BY s.CATALOG_NAME, s.SCHEMA_NAME
            ORDER BY TOTAL_ROWS DESC
        """)

        reporting_data = cursor.fetchall()
        df_reporting = pd.DataFrame(reporting_data, columns=[
            'Database', 'Schema', 'Tables', 'Total_Rows', 'Tables_with_PK', 'Tables_with_FK'
        ])
        df_reporting['Data_Quality'] = df_reporting.apply(
            lambda row: 'CRITICAL' if row['Tables_with_FK'] == 0 and row['Tables'] > 0
            else 'POOR', axis=1
        )
        df_reporting.to_excel(writer, sheet_name='DEV_REPORTING', index=False)
        print("  [SUCCESS] Reporting Layer sheet created")

        # 5. SECURITY_ANALYTICS COMPARISON ACROSS LAYERS
        print("\n[CREATING] SECURITY_ANALYTICS Comparison...")
        itseckpi_comparison = {
            'Layer': ['DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING'],
            'Schema': ['SECURITY_ANALYTICS', 'SECURITY_ANALYTICS', 'SECURITY_ANALYTICS'],
            'Tables': [375, 104, 7],
            'Records': ['140,486,608', '45,931,201', '1,248,213'],
            'Primary_Keys': [0, 57, 0],
            'Foreign_Keys': [0, 16, 0],
            'Quality_Score': ['0%', '72.3%', '0%'],
            'Status': ['Not Implemented', 'IMPLEMENTED', 'Needs Implementation']
        }
        df_itseckpi = pd.DataFrame(itseckpi_comparison)
        df_itseckpi.to_excel(writer, sheet_name='ITSECKPI_Analysis', index=False)
        print("  [SUCCESS] SECURITY_ANALYTICS Comparison created")

        # 6. TOP PRIORITY SCHEMAS
        print("\n[CREATING] Priority Schemas...")
        priority_data = {
            'Priority': ['P1', 'P2', 'P3', 'P4', 'P5'],
            'Schema': ['PDW', 'DNB', 'SOLUTION_SELLING', 'UAM', 'ONECRH_LOCATION'],
            'Total_Tables': [1098, 165, 423, 188, 142],
            'Total_Records': ['2,278M', '199M', '524M', '230M', '185M'],
            'Current_PKs': [41, 0, 0, 0, 0],
            'Current_FKs': [4, 0, 0, 0, 0],
            'Action_Required': [
                'Expand PK coverage',
                'Implement all constraints',
                'Implement all constraints',
                'Implement all constraints',
                'Critical for reporting'
            ]
        }
        df_priority = pd.DataFrame(priority_data)
        df_priority.to_excel(writer, sheet_name='Priority_Schemas', index=False)
        print("  [SUCCESS] Priority Schemas created")

        # 7. CONSTRAINT DEFICIT ANALYSIS
        print("\n[CREATING] Constraint Deficit Analysis...")
        deficit_data = {
            'Metric': [
                'Tables without Primary Keys',
                'Tables without Foreign Keys',
                'Schemas without any PKs',
                'Schemas without any FKs',
                'Average PK Coverage',
                'Average FK Coverage',
                'Reporting Layer FKs'
            ],
            'Count': [2750, 2828, 28, 35, '3.4%', '0.7%', 0],
            'Severity': ['CRITICAL', 'CRITICAL', 'HIGH', 'HIGH', 'CRITICAL', 'CRITICAL', 'CRITICAL'],
            'Business_Impact': [
                'Data duplicates possible',
                'No referential integrity',
                'No unique identification',
                'Cannot validate relationships',
                'Poor data quality',
                'No data lineage',
                'Unreliable reports'
            ]
        }
        df_deficit = pd.DataFrame(deficit_data)
        df_deficit.to_excel(writer, sheet_name='Constraint_Deficit', index=False)
        print("  [SUCCESS] Constraint Deficit Analysis created")

        # 8. IMPLEMENTATION ROADMAP
        print("\n[CREATING] Implementation Roadmap...")
        roadmap_data = {
            'Phase': ['Phase 1', 'Phase 1', 'Phase 2', 'Phase 2', 'Phase 3', 'Phase 3', 'Phase 4'],
            'Week': ['1-2', '1-2', '3-4', '3-4', '5-8', '5-8', '9-12'],
            'Task': [
                'Add PKs to top 100 tables',
                'Document critical tables',
                'Establish FKs for fact tables',
                'Create monitoring dashboard',
                'Extend to all dimensions',
                'Performance optimization',
                'Governance framework'
            ],
            'Target_Schema': ['PDW, DNB', 'All', 'SOLUTION_SELLING', 'All', 'UAM, ONECRH', 'All', 'All'],
            'Effort_Hours': [80, 40, 120, 60, 160, 80, 100],
            'Resources': ['2 Engineers', '1 Analyst', '2 Engineers', '1 Developer', '3 Engineers', '2 Engineers', '1 Architect']
        }
        df_roadmap = pd.DataFrame(roadmap_data)
        df_roadmap.to_excel(writer, sheet_name='Implementation_Roadmap', index=False)
        print("  [SUCCESS] Implementation Roadmap created")

        # 9. QUICK WINS
        print("\n[CREATING] Quick Wins...")
        quickwins_data = {
            'Action': [
                'Copy SECURITY_ANALYTICS approach to ITSECKPI_BACKUP',
                'Add PKs to small schemas (<10 tables)',
                'Expand PDW existing PKs',
                'Create views with implicit relationships',
                'Document top 20 critical tables'
            ],
            'Effort': ['Low', 'Low', 'Medium', 'Low', 'Low'],
            'Impact': ['Medium', 'Medium', 'High', 'Medium', 'High'],
            'Timeline': ['1 day', '2 days', '1 week', '3 days', '2 days'],
            'Schema': ['ITSECKPI_BACKUP', 'Multiple', 'PDW', 'All', 'All']
        }
        df_quickwins = pd.DataFrame(quickwins_data)
        df_quickwins.to_excel(writer, sheet_name='Quick_Wins', index=False)
        print("  [SUCCESS] Quick Wins created")

        # 10. SUCCESS METRICS
        print("\n[CREATING] Success Metrics...")
        metrics_data = {
            'Metric': [
                'Primary Key Coverage',
                'Foreign Key Coverage',
                'Documentation Coverage',
                'Query Performance',
                'Data Quality Score',
                'Constraint Violations Found',
                'ETL Failure Rate'
            ],
            'Current_Value': ['3.4%', '0.7%', '10%', 'Baseline', 'N/A', 'Unknown', 'Unknown'],
            'Target_30_Days': ['50%', '25%', '50%', '+25%', '60%', '<100', '<5%'],
            'Target_90_Days': ['90%', '60%', '100%', '+50%', '80%', '<10', '<1%'],
            'Measurement_Method': [
                'Count PKs / Total Tables',
                'Count FKs / Total Tables',
                'Documented / Total Tables',
                'Average query time',
                'Quality scorecard',
                'Validation queries',
                'ETL monitoring logs'
            ]
        }
        df_metrics = pd.DataFrame(metrics_data)
        df_metrics.to_excel(writer, sheet_name='Success_Metrics', index=False)
        print("  [SUCCESS] Success Metrics created")

    print("\n" + "="*70)
    print("THREE-LAYER EXCEL DOCUMENTATION COMPLETE")
    print("="*70)
    print(f"\n[SUCCESS] Excel file created: {excel_file}")
    print("\nSheets included:")
    print("  1. Executive_Summary - High-level overview")
    print("  2. DEV_LANDING - Landing layer analysis")
    print("  3. DEV_TRANSFORMATION - Transformation layer analysis")
    print("  4. DEV_REPORTING - Reporting layer analysis")
    print("  5. ITSECKPI_Analysis - Success story comparison")
    print("  6. Priority_Schemas - Implementation priorities")
    print("  7. Constraint_Deficit - Gap analysis")
    print("  8. Implementation_Roadmap - 12-week plan")
    print("  9. Quick_Wins - Immediate actions")
    print(" 10. Success_Metrics - KPIs and targets")

    cursor.close()
    return True

def main():
    """Main execution"""
    # Check if pandas is installed
    try:
        import pandas as pd
    except ImportError:
        print("[ERROR] pandas not installed. Installing...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'pandas', 'openpyxl'])
        import pandas as pd

    conn = create_connection()
    if not conn:
        print("[ERROR] Failed to connect to Snowflake")
        return False

    try:
        success = generate_three_layer_excel(conn)
        return success
    except Exception as e:
        print(f"[ERROR] Excel generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)