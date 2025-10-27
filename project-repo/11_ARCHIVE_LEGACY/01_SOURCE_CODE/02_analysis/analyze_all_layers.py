"""
Comprehensive Analysis of All Three Snowflake Layers
DEV_LANDING, DEV_TRANSFORMATION, DEV_REPORTING
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

def analyze_all_layers(conn):
    """Analyze all three database layers"""
    cursor = conn.cursor()

    print("\n" + "="*70)
    print("ANALYZING ALL THREE SNOWFLAKE LAYERS")
    print("="*70)

    layers = ['DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING']
    all_layer_data = {}

    for layer in layers:
        print(f"\n[ANALYZING] {layer}...")

        try:
            cursor.execute(f"USE DATABASE {layer}")

            # Get all schemas in this database
            cursor.execute("""
                SELECT SCHEMA_NAME, CREATED, COMMENT
                FROM INFORMATION_SCHEMA.SCHEMATA
                WHERE SCHEMA_NAME NOT IN ('INFORMATION_SCHEMA', 'PUBLIC')
                ORDER BY SCHEMA_NAME
            """)

            schemas = cursor.fetchall()
            layer_data = {
                'database': layer,
                'schemas': [],
                'total_tables': 0,
                'total_views': 0,
                'total_rows': 0,
                'constraints': {'PK': 0, 'FK': 0, 'UNIQUE': 0}
            }

            for schema_info in schemas:
                schema_name = schema_info[0]
                print(f"  Analyzing schema: {schema_name}")

                try:
                    cursor.execute(f"USE SCHEMA {schema_name}")

                    # Get tables in this schema
                    cursor.execute("""
                        SELECT
                            TABLE_NAME,
                            TABLE_TYPE,
                            ROW_COUNT,
                            BYTES,
                            CREATED,
                            LAST_ALTERED
                        FROM INFORMATION_SCHEMA.TABLES
                        WHERE TABLE_SCHEMA = %s
                            AND TABLE_TYPE IN ('BASE TABLE', 'VIEW')
                        ORDER BY TABLE_TYPE, TABLE_NAME
                    """, (schema_name,))

                    tables = cursor.fetchall()

                    # Get constraints
                    cursor.execute("""
                        SELECT
                            CONSTRAINT_TYPE,
                            COUNT(*) as COUNT
                        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
                        WHERE TABLE_SCHEMA = %s
                        GROUP BY CONSTRAINT_TYPE
                    """, (schema_name,))

                    constraints = cursor.fetchall()
                    constraint_dict = {row[0]: row[1] for row in constraints}

                    # Calculate schema statistics
                    schema_data = {
                        'schema_name': schema_name,
                        'tables': len([t for t in tables if t[1] == 'BASE TABLE']),
                        'views': len([t for t in tables if t[1] == 'VIEW']),
                        'total_rows': sum([t[2] if t[2] else 0 for t in tables]),
                        'size_bytes': sum([t[3] if t[3] else 0 for t in tables]),
                        'primary_keys': constraint_dict.get('PRIMARY KEY', 0),
                        'foreign_keys': constraint_dict.get('FOREIGN KEY', 0),
                        'unique_keys': constraint_dict.get('UNIQUE', 0),
                        'table_list': [t[0] for t in tables]
                    }

                    layer_data['schemas'].append(schema_data)
                    layer_data['total_tables'] += schema_data['tables']
                    layer_data['total_views'] += schema_data['views']
                    layer_data['total_rows'] += schema_data['total_rows']
                    layer_data['constraints']['PK'] += schema_data['primary_keys']
                    layer_data['constraints']['FK'] += schema_data['foreign_keys']
                    layer_data['constraints']['UNIQUE'] += schema_data['unique_keys']

                except Exception as e:
                    print(f"    [WARNING] Could not analyze schema {schema_name}: {str(e)}")
                    continue

            all_layer_data[layer] = layer_data

            # Print summary for this layer
            print(f"\n  {layer} Summary:")
            print(f"    Schemas: {len(layer_data['schemas'])}")
            print(f"    Tables: {layer_data['total_tables']}")
            print(f"    Views: {layer_data['total_views']}")
            print(f"    Total Rows: {layer_data['total_rows']:,}")
            print(f"    Primary Keys: {layer_data['constraints']['PK']}")
            print(f"    Foreign Keys: {layer_data['constraints']['FK']}")

        except Exception as e:
            print(f"  [ERROR] Could not analyze {layer}: {str(e)}")
            continue

    # Generate comprehensive report
    print("\n" + "="*70)
    print("COMPREHENSIVE ANALYSIS COMPLETE")
    print("="*70)

    # Save detailed analysis
    analysis_file = f"three_layer_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(analysis_file, 'w') as f:
        json.dump(all_layer_data, f, indent=2, default=str)

    print(f"\n[SAVED] Detailed analysis: {analysis_file}")

    # Createte summary report
    print("\n" + "="*70)
    print("THREE-LAYER ARCHITECTURE SUMMARY")
    print("="*70)

    for layer_name, layer_info in all_layer_data.items():
        print(f"\n{layer_name}:")
        print(f"  Schemas: {len(layer_info['schemas'])}")
        print(f"  Tables: {layer_info['total_tables']}")
        print(f"  Views: {layer_info['total_views']}")
        print(f"  Rows: {layer_info['total_rows']:,}")
        print(f"  PKs: {layer_info['constraints']['PK']}")
        print(f"  FKs: {layer_info['constraints']['FK']}")

        if layer_info['schemas']:
            print(f"  Main Schemas:")
            for schema in layer_info['schemas'][:5]:  # Show top 5 schemas
                print(f"    - {schema['schema_name']}: {schema['tables']} tables, {schema['total_rows']:,} rows")

    cursor.close()
    return all_layer_data

def generate_layer_specific_sql(layer_data, layer_name):
    """Generate SQL implementation scripts for each layer"""

    sql_content = f"""-- =====================================================
-- {layer_name} Layer Implementation Script
-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- =====================================================

USE DATABASE {layer_name};

"""

    for schema_info in layer_data.get('schemas', []):
        schema_name = schema_info['schema_name']

        if schema_info['tables'] > 0 and schema_info['primary_keys'] == 0:
            sql_content += f"""
-- =====================================================
-- Schema: {schema_name}
-- Tables without Primary Keys: {schema_info['tables']}
-- =====================================================

USE SCHEMA {schema_name};

"""
            # Add sample PK createtion for main tables
            for table in schema_info.get('table_list', [])[:10]:  # First 10 tables
                if 'DIM_' in table:
                    sql_content += f"""-- Add Primary Key to {table}
-- ALTER TABLE {table} ADD CONSTRAINT PK_{table} PRIMARY KEY (ID_COLUMN) RELY;

"""
                elif 'FACT_' in table:
                    sql_content += f"""-- Add composite key or surrogate key to {table}
-- ALTER TABLE {table} ADD CONSTRAINT PK_{table} PRIMARY KEY (FACT_ID) RELY;

"""

    return sql_content

def main():
    """Main execution"""
    conn = createte_connection()
    if not conn:
        print("[ERROR] Failed to connect to Snowflake")
        return False

    try:
        # Analyze all layers
        layer_data = analyze_all_layers(conn)

        # Generate implementation scripts for each layer
        print("\n[GENERATING] Layer-specific implementation scripts...")

        for layer_name, data in layer_data.items():
            if data['total_tables'] > 0:
                sql_content = generate_layer_specific_sql(data, layer_name)
                sql_file = f"FINAL_DELIVERABLES/04_SQL_Scripts/{layer_name}_implementation.sql"

                with open(sql_file, 'w') as f:
                    f.write(sql_content)

                print(f"  [CREATED] {sql_file}")

        print("\n[SUCCESS] All layer analysis complete!")
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