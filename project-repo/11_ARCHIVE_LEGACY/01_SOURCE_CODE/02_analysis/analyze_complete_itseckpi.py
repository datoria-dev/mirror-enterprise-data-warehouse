"""
Complete SECURITY_ANALYTICS Analysis - ALL Objects Across 3 Layers
Analyzes: Tables, Views, Stages, File Formats, Sequences, Procedures, Tasks, Functions, etc.
"""

import snowflake.connector
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime
import json

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

def analyze_complete_itseckpi(conn):
    """Complete analysis of all SECURITY_ANALYTICS objects"""
    cursor = conn.cursor()

    print("\n" + "="*80)
    print("COMPLETE SECURITY_ANALYTICS ANALYSIS - ALL OBJECTS ACROSS 3 LAYERS")
    print("="*80)

    all_data = {}

    for database in ['DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING']:
        print(f"\n{'='*80}")
        print(f"ANALYZING {database}.SECURITY_ANALYTICS")
        print(f"{'='*80}")

        layer_data = {
            'database': database,
            'tables': [],
            'views': [],
            'stages': [],
            'file_formats': [],
            'sequences': [],
            'procedures': [],
            'functions': [],
            'tasks': [],
            'streams': [],
            'pipes': [],
            'constraints': [],
            'statistics': {}
        }

        try:
            cursor.execute(f"USE DATABASE {database}")
            cursor.execute("USE SCHEMA SECURITY_ANALYTICS")

            # 1. TABLES
            print(f"\n[1] TABLES...")
            cursor.execute("""
                SELECT
                    TABLE_NAME,
                    TABLE_TYPE,
                    ROW_COUNT,
                    BYTES,
                    CREATED,
                    LAST_ALTERED,
                    COMMENT,
                    CLUSTERING_KEY,
                    AUTO_CLUSTERING_ON
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                    AND TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """)

            for row in cursor.fetchall():
                layer_data['tables'].append({
                    'name': row[0],
                    'type': row[1],
                    'rows': row[2] if row[2] else 0,
                    'bytes': row[3] if row[3] else 0,
                    'size_mb': round(row[3] / (1024*1024), 2) if row[3] else 0,
                    'createted': str(row[4]) if row[4] else '',
                    'modified': str(row[5]) if row[5] else '',
                    'comment': row[6] if row[6] else '',
                    'clustering_key': row[7] if row[7] else '',
                    'auto_clustering': row[8] if row[8] else False
                })

            print(f"  Found {len(layer_data['tables'])} tables")

            # 2. VIEWS
            print(f"[2] VIEWS...")
            cursor.execute("""
                SELECT
                    TABLE_NAME,
                    CREATED,
                    LAST_ALTERED,
                    COMMENT,
                    VIEW_DEFINITION
                FROM INFORMATION_SCHEMA.VIEWS
                WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                ORDER BY TABLE_NAME
            """)

            for row in cursor.fetchall():
                layer_data['views'].append({
                    'name': row[0],
                    'createted': str(row[1]) if row[1] else '',
                    'modified': str(row[2]) if row[2] else '',
                    'comment': row[3] if row[3] else '',
                    'definition_length': len(row[4]) if row[4] else 0
                })

            print(f"  Found {len(layer_data['views'])} views")

            # 3. STAGES
            print(f"[3] STAGES...")
            try:
                cursor.execute("SHOW STAGES IN SCHEMA SECURITY_ANALYTICS")
                for row in cursor.fetchall():
                    if len(row) > 2:
                        layer_data['stages'].append({
                            'name': row[1],
                            'url': row[2] if len(row) > 2 else '',
                            'type': row[3] if len(row) > 3 else '',
                            'owner': row[4] if len(row) > 4 else '',
                            'comment': row[5] if len(row) > 5 else ''
                        })
                print(f"  Found {len(layer_data['stages'])} stages")
            except:
                print(f"  No stages found")

            # 4. FILE FORMATS
            print(f"[4] FILE FORMATS...")
            try:
                cursor.execute("SHOW FILE FORMATS IN SCHEMA SECURITY_ANALYTICS")
                for row in cursor.fetchall():
                    if len(row) > 2:
                        layer_data['file_formats'].append({
                            'name': row[1],
                            'type': row[2] if len(row) > 2 else '',
                            'owner': row[3] if len(row) > 3 else '',
                            'comment': row[4] if len(row) > 4 else ''
                        })
                print(f"  Found {len(layer_data['file_formats'])} file formats")
            except:
                print(f"  No file formats found")

            # 5. SEQUENCES
            print(f"[5] SEQUENCES...")
            try:
                cursor.execute("SHOW SEQUENCES IN SCHEMA SECURITY_ANALYTICS")
                for row in cursor.fetchall():
                    if len(row) > 2:
                        layer_data['sequences'].append({
                            'name': row[1],
                            'next_value': row[2] if len(row) > 2 else '',
                            'interval': row[3] if len(row) > 3 else '',
                            'owner': row[4] if len(row) > 4 else ''
                        })
                print(f"  Found {len(layer_data['sequences'])} sequences")
            except:
                print(f"  No sequences found")

            # 6. PROCEDURES
            print(f"[6] STORED PROCEDURES...")
            try:
                cursor.execute("SHOW PROCEDURES IN SCHEMA SECURITY_ANALYTICS")
                for row in cursor.fetchall():
                    if len(row) > 1:
                        layer_data['procedures'].append({
                            'name': row[1],
                            'schema': row[2] if len(row) > 2 else '',
                            'language': row[5] if len(row) > 5 else '',
                            'createted': str(row[3]) if len(row) > 3 else ''
                        })
                print(f"  Found {len(layer_data['procedures'])} procedures")
            except:
                print(f"  No procedures found")

            # 7. FUNCTIONS
            print(f"[7] FUNCTIONS...")
            try:
                cursor.execute("SHOW FUNCTIONS IN SCHEMA SECURITY_ANALYTICS")
                for row in cursor.fetchall():
                    if len(row) > 1:
                        layer_data['functions'].append({
                            'name': row[1],
                            'language': row[4] if len(row) > 4 else '',
                            'createted': str(row[2]) if len(row) > 2 else ''
                        })
                print(f"  Found {len(layer_data['functions'])} functions")
            except:
                print(f"  No functions found")

            # 8. TASKS
            print(f"[8] SCHEDULED TASKS...")
            try:
                cursor.execute("SHOW TASKS IN SCHEMA SECURITY_ANALYTICS")
                for row in cursor.fetchall():
                    if len(row) > 3:
                        layer_data['tasks'].append({
                            'name': row[1],
                            'state': row[3] if len(row) > 3 else '',
                            'schedule': row[4] if len(row) > 4 else '',
                            'warehouse': row[7] if len(row) > 7 else '',
                            'condition': row[8] if len(row) > 8 else ''
                        })
                print(f"  Found {len(layer_data['tasks'])} tasks")
            except:
                print(f"  No tasks found")

            # 9. STREAMS
            print(f"[9] STREAMS...")
            try:
                cursor.execute("SHOW STREAMS IN SCHEMA SECURITY_ANALYTICS")
                for row in cursor.fetchall():
                    if len(row) > 2:
                        layer_data['streams'].append({
                            'name': row[1],
                            'table_name': row[3] if len(row) > 3 else '',
                            'type': row[2] if len(row) > 2 else '',
                            'stale': row[5] if len(row) > 5 else ''
                        })
                print(f"  Found {len(layer_data['streams'])} streams")
            except:
                print(f"  No streams found")

            # 10. PIPES
            print(f"[10] PIPES...")
            try:
                cursor.execute("SHOW PIPES IN SCHEMA SECURITY_ANALYTICS")
                for row in cursor.fetchall():
                    if len(row) > 2:
                        layer_data['pipes'].append({
                            'name': row[1],
                            'definition': row[3] if len(row) > 3 else '',
                            'owner': row[4] if len(row) > 4 else ''
                        })
                print(f"  Found {len(layer_data['pipes'])} pipes")
            except:
                print(f"  No pipes found")

            # 11. CONSTRAINTS
            print(f"[11] CONSTRAINTS...")
            cursor.execute("""
                SELECT
                    TABLE_NAME,
                    CONSTRAINT_NAME,
                    CONSTRAINT_TYPE,
                    COMMENT
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
                WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                ORDER BY CONSTRAINT_TYPE, TABLE_NAME
            """)

            for row in cursor.fetchall():
                layer_data['constraints'].append({
                    'table': row[0],
                    'name': row[1],
                    'type': row[2],
                    'comment': row[3] if row[3] else ''
                })

            print(f"  Found {len(layer_data['constraints'])} constraints")

            # 12. STATISTICS
            print(f"[12] CALCULATING STATISTICS...")
            total_rows = sum([t['rows'] for t in layer_data['tables']])
            total_bytes = sum([t['bytes'] for t in layer_data['tables']])
            tables_with_data = len([t for t in layer_data['tables'] if t['rows'] > 0])
            empty_tables = len([t for t in layer_data['tables'] if t['rows'] == 0])

            pk_count = len([c for c in layer_data['constraints'] if c['type'] == 'PRIMARY KEY'])
            fk_count = len([c for c in layer_data['constraints'] if c['type'] == 'FOREIGN KEY'])
            unique_count = len([c for c in layer_data['constraints'] if c['type'] == 'UNIQUE'])

            dim_tables = len([t for t in layer_data['tables'] if 'DIM_' in t['name']])
            fact_tables = len([t for t in layer_data['tables'] if 'FACT_' in t['name']])

            layer_data['statistics'] = {
                'total_tables': len(layer_data['tables']),
                'total_views': len(layer_data['views']),
                'total_stages': len(layer_data['stages']),
                'total_file_formats': len(layer_data['file_formats']),
                'total_sequences': len(layer_data['sequences']),
                'total_procedures': len(layer_data['procedures']),
                'total_functions': len(layer_data['functions']),
                'total_tasks': len(layer_data['tasks']),
                'total_streams': len(layer_data['streams']),
                'total_pipes': len(layer_data['pipes']),
                'total_constraints': len(layer_data['constraints']),
                'total_rows': total_rows,
                'total_bytes': total_bytes,
                'total_size_gb': round(total_bytes / (1024**3), 2),
                'tables_with_data': tables_with_data,
                'empty_tables': empty_tables,
                'dimension_tables': dim_tables,
                'fact_tables': fact_tables,
                'primary_keys': pk_count,
                'foreign_keys': fk_count,
                'unique_keys': unique_count
            }

            print(f"\n  STATISTICS:")
            print(f"    Total Objects: {sum([
                layer_data['statistics']['total_tables'],
                layer_data['statistics']['total_views'],
                layer_data['statistics']['total_stages'],
                layer_data['statistics']['total_procedures'],
                layer_data['statistics']['total_tasks']
            ])}")
            print(f"    Total Rows: {total_rows:,}")
            print(f"    Total Size: {layer_data['statistics']['total_size_gb']} GB")
            print(f"    Primary Keys: {pk_count}")
            print(f"    Foreign Keys: {fk_count}")

        except Exception as e:
            print(f"  [ERROR] Could not complete analysis: {str(e)}")

        all_data[database] = layer_data

    # Save complete analysis to JSON
    analysis_file = f"FINAL_DELIVERABLES/itseckpi_complete_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(analysis_file, 'w') as f:
        json.dump(all_data, f, indent=2, default=str)

    print(f"\n{'='*80}")
    print(f"ANALYSIS COMPLETE - Saved to {analysis_file}")
    print(f"{'='*80}")

    cursor.close()
    return all_data

def generate_consolidated_excel(all_data):
    """Generate consolidated Excel with all SECURITY_ANALYTICS data"""
    print("\n" + "="*80)
    print("GENERATING CONSOLIDATED SECURITY_ANALYTICS EXCEL")
    print("="*80)

    excel_file = "FINAL_DELIVERABLES/03_Excel_DataModel/ITSECKPI_COMPLETE_INVENTORY.xlsx"

    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:

        # 1. EXECUTIVE SUMMARY
        print("\n[CREATING] Executive Summary...")
        summary_data = []
        for db, data in all_data.items():
            summary_data.append({
                'Layer': db.replace('DEV_', ''),
                'Tables': data['statistics']['total_tables'],
                'Views': data['statistics']['total_views'],
                'Stages': data['statistics']['total_stages'],
                'Procedures': data['statistics']['total_procedures'],
                'Tasks': data['statistics']['total_tasks'],
                'Total_Rows': f"{data['statistics']['total_rows']:,}",
                'Size_GB': data['statistics']['total_size_gb'],
                'Primary_Keys': data['statistics']['primary_keys'],
                'Foreign_Keys': data['statistics']['foreign_keys']
            })

        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Executive_Summary', index=False)

        # 2-4. TABLES BY LAYER
        for db, data in all_data.items():
            layer_name = db.replace('DEV_', '')
            print(f"[CREATING] {layer_name} Tables...")

            if data['tables']:
                df_tables = pd.DataFrame(data['tables'])
                df_tables.to_excel(writer, sheet_name=f'{layer_name}_Tables', index=False)

        # 5-7. VIEWS BY LAYER
        for db, data in all_data.items():
            layer_name = db.replace('DEV_', '')
            if data['views']:
                print(f"[CREATING] {layer_name} Views...")
                df_views = pd.DataFrame(data['views'])
                df_views.to_excel(writer, sheet_name=f'{layer_name}_Views', index=False)

        # 8. ALL CONSTRAINTS
        print("[CREATING] All Constraints...")
        all_constraints = []
        for db, data in all_data.items():
            for constraint in data['constraints']:
                all_constraints.append({
                    'Layer': db.replace('DEV_', ''),
                    **constraint
                })

        if all_constraints:
            df_constraints = pd.DataFrame(all_constraints)
            df_constraints.to_excel(writer, sheet_name='All_Constraints', index=False)

        # 9. ALL TASKS
        print("[CREATING] All Tasks...")
        all_tasks = []
        for db, data in all_data.items():
            for task in data['tasks']:
                all_tasks.append({
                    'Layer': db.replace('DEV_', ''),
                    **task
                })

        if all_tasks:
            df_tasks = pd.DataFrame(all_tasks)
            df_tasks.to_excel(writer, sheet_name='All_Tasks', index=False)

        # 10. ALL PROCEDURES
        print("[CREATING] All Procedures...")
        all_procedures = []
        for db, data in all_data.items():
            for proc in data['procedures']:
                all_procedures.append({
                    'Layer': db.replace('DEV_', ''),
                    **proc
                })

        if all_procedures:
            df_procedures = pd.DataFrame(all_procedures)
            df_procedures.to_excel(writer, sheet_name='All_Procedures', index=False)
        else:
            # Createte empty sheet with headers
            df_procedures = pd.DataFrame(columns=['Layer', 'name', 'schema', 'language', 'createted'])
            df_procedures.to_excel(writer, sheet_name='All_Procedures', index=False)

        # 11. ALL STAGES
        print("[CREATING] All Stages...")
        all_stages = []
        for db, data in all_data.items():
            for stage in data['stages']:
                all_stages.append({
                    'Layer': db.replace('DEV_', ''),
                    **stage
                })

        if all_stages:
            df_stages = pd.DataFrame(all_stages)
            df_stages.to_excel(writer, sheet_name='All_Stages', index=False)
        else:
            df_stages = pd.DataFrame(columns=['Layer', 'name', 'url', 'type', 'owner'])
            df_stages.to_excel(writer, sheet_name='All_Stages', index=False)

        # 12. STATISTICS COMPARISON
        print("[CREATING] Statistics Comparison...")
        stats_data = []
        for db, data in all_data.items():
            stats = data['statistics']
            stats_data.append({
                'Layer': db.replace('DEV_', ''),
                'Total_Objects': sum([
                    stats['total_tables'], stats['total_views'],
                    stats['total_procedures'], stats['total_tasks']
                ]),
                'Tables': stats['total_tables'],
                'Views': stats['total_views'],
                'DIM_Tables': stats['dimension_tables'],
                'FACT_Tables': stats['fact_tables'],
                'Constraints': stats['total_constraints'],
                'Primary_Keys': stats['primary_keys'],
                'Foreign_Keys': stats['foreign_keys'],
                'Total_Rows': stats['total_rows'],
                'Size_GB': stats['total_size_gb'],
                'Tables_With_Data': stats['tables_with_data'],
                'Empty_Tables': stats['empty_tables']
            })

        df_stats = pd.DataFrame(stats_data)
        df_stats.to_excel(writer, sheet_name='Statistics_Comparison', index=False)

    print(f"\n{'='*80}")
    print(f"CONSOLIDATED EXCEL GENERATED: {excel_file}")
    print(f"{'='*80}")

    return excel_file

def main():
    """Main execution"""
    conn = createte_connection()
    if not conn:
        print("[ERROR] Failed to connect to Snowflake")
        return False

    try:
        # Complete analysis
        all_data = analyze_complete_itseckpi(conn)

        # Generate Excel
        excel_file = generate_consolidated_excel(all_data)

        print("\n[SUCCESS] Complete SECURITY_ANALYTICS analysis finished!")
        print(f"\nGenerated files:")
        print(f"  - JSON: itseckpi_complete_analysis_*.json")
        print(f"  - Excel: {excel_file}")

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