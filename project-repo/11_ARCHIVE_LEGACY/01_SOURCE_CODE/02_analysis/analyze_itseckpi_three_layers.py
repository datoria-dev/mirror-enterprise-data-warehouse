"""
SECURITY_ANALYTICS Schema Analysis Across All Three Layers
Focused analysis only on SECURITY_ANALYTICS schema
"""

import snowflake.connector
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables
load_dotenv()

def createte_connection():
    """Createte Snowflake connection"""
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

def analyze_itseckpi_all_layers(conn):
    """Analyze SECURITY_ANALYTICS schema across all three layers"""
    cursor = conn.cursor()

    print("\n" + "="*70)
    print("SECURITY_ANALYTICS SCHEMA - THREE LAYER ANALYSIS")
    print("="*70)

    itseckpi_data = {}

    # Analyze each layer
    for database in ['DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING']:
        print(f"\n[ANALYZING] {database}.SECURITY_ANALYTICS...")

        try:
            cursor.execute(f"USE DATABASE {database}")

            # Check if SECURITY_ANALYTICS schema exists
            cursor.execute("""
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.SCHEMATA
                WHERE SCHEMA_NAME = 'SECURITY_ANALYTICS'
            """)

            if cursor.fetchone()[0] == 0:
                print(f"  [WARNING] SECURITY_ANALYTICS schema not found in {database}")
                continue

            cursor.execute("USE SCHEMA SECURITY_ANALYTICS")

            # Get all tables
            cursor.execute("""
                SELECT
                    TABLE_NAME,
                    TABLE_TYPE,
                    ROW_COUNT,
                    BYTES,
                    CREATED,
                    LAST_ALTERED,
                    COMMENT
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                    AND TABLE_TYPE IN ('BASE TABLE', 'VIEW')
                ORDER BY TABLE_TYPE, TABLE_NAME
            """)

            tables = cursor.fetchall()

            # Get constraints
            cursor.execute("""
                SELECT
                    tc.TABLE_NAME,
                    tc.CONSTRAINT_NAME,
                    tc.CONSTRAINT_TYPE
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                WHERE tc.TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                ORDER BY tc.TABLE_NAME, tc.CONSTRAINT_TYPE
            """)

            constraints = cursor.fetchall()

            # Count constraint types
            pk_count = len([c for c in constraints if c[2] == 'PRIMARY KEY'])
            fk_count = len([c for c in constraints if c[2] == 'FOREIGN KEY'])
            unique_count = len([c for c in constraints if c[2] == 'UNIQUE'])

            # Categorize tables
            dim_tables = [t for t in tables if t[0].startswith('DIM_')]
            fact_tables = [t for t in tables if t[0].startswith('FACT_')]
            other_tables = [t for t in tables if not t[0].startswith('DIM_') and not t[0].startswith('FACT_')]

            # Calculate metrics
            total_rows = sum([t[2] if t[2] else 0 for t in tables])
            total_bytes = sum([t[3] if t[3] else 0 for t in tables])
            base_tables = [t for t in tables if t[1] == 'BASE TABLE']
            views = [t for t in tables if t[1] == 'VIEW']

            layer_info = {
                'database': database,
                'total_tables': len(base_tables),
                'total_views': len(views),
                'dimension_tables': len(dim_tables),
                'fact_tables': len(fact_tables),
                'other_tables': len(other_tables),
                'total_rows': total_rows,
                'size_gb': round(total_bytes / (1024**3), 2) if total_bytes else 0,
                'primary_keys': pk_count,
                'foreign_keys': fk_count,
                'unique_keys': unique_count,
                'tables_with_data': len([t for t in tables if t[2] and t[2] > 0]),
                'empty_tables': len([t for t in tables if not t[2] or t[2] == 0]),
                'table_list': [t[0] for t in base_tables]
            }

            itseckpi_data[database] = layer_info

            # Print summary
            print(f"\n  {database}.SECURITY_ANALYTICS Summary:")
            print(f"    Tables: {layer_info['total_tables']}")
            print(f"    Views: {layer_info['total_views']}")
            print(f"    DIM Tables: {layer_info['dimension_tables']}")
            print(f"    FACT Tables: {layer_info['fact_tables']}")
            print(f"    Total Rows: {layer_info['total_rows']:,}")
            print(f"    Size: {layer_info['size_gb']} GB")
            print(f"    Primary Keys: {layer_info['primary_keys']}")
            print(f"    Foreign Keys: {layer_info['foreign_keys']}")
            print(f"    Tables with Data: {layer_info['tables_with_data']}")
            print(f"    Empty Tables: {layer_info['empty_tables']}")

            # Analyze specific security service tables
            print(f"\n  Security Service Coverage:")

            services = {
                'Crowdstrike': ['CROWDSTRIKE', 'DIM_CROWDSTRIKE'],
                'Qualys': ['QUALYS', 'DIM_QUALYS', 'FACT_QUALYS'],
                'BitSight': ['BITSIGHT', 'DIM_BITSIGHT', 'FACT_BITSIGHT'],
                'CybelAngel': ['CYBELANGEL', 'DIM_CYBELANGEL'],
                'ZeroFox': ['ZEROFOX', 'DIM_ZEROFOX'],
                'Sentinel': ['SENTINEL', 'DIM_SENTINEL'],
                'Splunk': ['SPLUNK', 'DIM_SPLUNK'],
                'Defender': ['DEFENDER', 'DIM_DEFENDER'],
                'McAfee': ['MCAFEE', 'DIM_MCAFEE'],
                'Symantec': ['SYMANTEC', 'DIM_SYMANTEC'],
                'TrendMicro': ['TRENDMICRO', 'DIM_TRENDMICRO'],
                'Sophos': ['SOPHOS', 'DIM_SOPHOS']
            }

            for service, patterns in services.items():
                service_tables = [t[0] for t in tables if any(p in t[0].upper() for p in patterns)]
                if service_tables:
                    total_service_rows = sum([t[2] if t[2] else 0 for t in tables if t[0] in service_tables])
                    print(f"    {service}: {len(service_tables)} tables, {total_service_rows:,} rows")

        except Exception as e:
            print(f"  [ERROR] Could not analyze {database}.SECURITY_ANALYTICS: {str(e)}")
            continue

    # Generate comparison
    print("\n" + "="*70)
    print("SECURITY_ANALYTICS LAYER COMPARISON")
    print("="*70)

    print("\n| Layer | Tables | Views | Rows | PKs | FKs | Empty | Quality |")
    print("|-------|--------|-------|------|-----|-----|-------|---------|")

    for db, info in itseckpi_data.items():
        quality = "EXCELLENT" if info['primary_keys'] > 50 else "GOOD" if info['primary_keys'] > 10 else "POOR"
        print(f"| {db:20} | {info['total_tables']:6} | {info['total_views']:5} | {info['total_rows']:,} | {info['primary_keys']:3} | {info['foreign_keys']:3} | {info['empty_tables']:5} | {quality:9} |")

    # Save detailed analysis
    analysis_file = f"itseckpi_three_layer_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(analysis_file, 'w') as f:
        json.dump(itseckpi_data, f, indent=2, default=str)

    print(f"\n[SAVED] Detailed analysis: {analysis_file}")

    cursor.close()
    return itseckpi_data

def main():
    """Main execution"""
    conn = createte_connection()
    if not conn:
        print("[ERROR] Failed to connect to Snowflake")
        return False

    try:
        itseckpi_data = analyze_itseckpi_all_layers(conn)

        print("\n" + "="*70)
        print("SECURITY_ANALYTICS ANALYSIS COMPLETE")
        print("="*70)

        # Generate recommendations
        print("\n[RECOMMENDATIONS]")

        if 'DEV_LANDING' in itseckpi_data:
            landing = itseckpi_data['DEV_LANDING']
            if landing['primary_keys'] == 0:
                print("\n1. DEV_LANDING.SECURITY_ANALYTICS:")
                print("   - Add Primary Keys to all dimension tables")
                print("   - Consider data validation constraints")
                print(f"   - {landing['empty_tables']} empty tables need data loading")

        if 'DEV_TRANSFORMATION' in itseckpi_data:
            transform = itseckpi_data['DEV_TRANSFORMATION']
            print("\n2. DEV_TRANSFORMATION.SECURITY_ANALYTICS:")
            print(f"   - Already has {transform['primary_keys']} PKs and {transform['foreign_keys']} FKs")
            print("   - Continue as template for other schemas")
            if transform['empty_tables'] > 0:
                print(f"   - {transform['empty_tables']} empty tables need ETL implementation")

        if 'DEV_REPORTING' in itseckpi_data:
            reporting = itseckpi_data['DEV_REPORTING']
            if reporting['foreign_keys'] == 0:
                print("\n3. DEV_REPORTING.SECURITY_ANALYTICS:")
                print("   - CRITICAL: Add Foreign Keys for data lineage")
                print("   - Add Primary Keys to fact tables")
                print("   - Createte aggregated views for performance")

        return True

    except Exception as e:
        print(f"[ERROR] Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)