#!/usr/bin/env python3
"""
Script to execute analysis queries and export results
Generates complete documentation of the SECURITY_ANALYTICS data model
"""

import snowflake.connector
import pandas as pd
import json
from datetime import datetime
import os

class SnowflakeMetadataExporter:
    def __init__(self, connection_params):
        """Initialize the exporter with connection parameters"""
        self.connection_params = connection_params
        self.results = {}
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    def connect(self):
        """Establish connection with Snowflake"""
        try:
            self.conn = snowflake.connector.connect(**self.connection_params)
            self.cursor = self.conn.cursor()
            print("Connected to Snowflake")
            return True
        except Exception as e:
            print(f"Error connecting: {e}")
            return False

    def execute_query(self, query_name, query):
        """Execute a query and store results"""
        try:
            print(f"Executing: {query_name}...")
            self.cursor.execute(query)
            columns = [col[0] for col in self.cursor.description]
            data = self.cursor.fetchall()
            df = pd.DataFrame(data, columns=columns)
            self.results[query_name] = df
            print(f"  {len(df)} records retrieved")
            return df
        except Exception as e:
            print(f"  Error: {e}")
            return None

    def run_analysis(self):
        """Execute all analysis queries"""

        print("\n" + "="*60)
        print("STARTING SECURITY_ANALYTICS DATA MODEL ANALYSIS")
        print("="*60)

        # 1. Object inventory
        inventory_query = """
        WITH all_objects AS (
            SELECT
                'DEV_LANDING' as LAYER,
                TABLE_CATALOG as DATABASE_NAME,
                TABLE_SCHEMA as SCHEMA_NAME,
                TABLE_NAME,
                TABLE_TYPE,
                ROW_COUNT,
                BYTES/1024/1024 as SIZE_MB,
                CREATED,
                LAST_ALTERED
            FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'

            UNION ALL

            SELECT
                'DEV_TRANSFORMATION',
                TABLE_CATALOG,
                TABLE_SCHEMA,
                TABLE_NAME,
                TABLE_TYPE,
                ROW_COUNT,
                BYTES/1024/1024,
                CREATED,
                LAST_ALTERED
            FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'

            UNION ALL

            SELECT
                'DEV_REPORTING',
                TABLE_CATALOG,
                TABLE_SCHEMA,
                TABLE_NAME,
                TABLE_TYPE,
                ROW_COUNT,
                BYTES/1024/1024,
                CREATED,
                LAST_ALTERED
            FROM DEV_REPORTING.INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
        )
        SELECT * FROM all_objects ORDER BY LAYER, TABLE_NAME
        """
        self.execute_query("inventory", inventory_query)

        # 2. Column details
        columns_query = """
        WITH all_columns AS (
            SELECT
                'DEV_LANDING' as LAYER,
                TABLE_CATALOG as DATABASE_NAME,
                TABLE_NAME,
                COLUMN_NAME,
                ORDINAL_POSITION,
                DATA_TYPE,
                IS_NULLABLE
            FROM DEV_LANDING.INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'

            UNION ALL

            SELECT
                'DEV_TRANSFORMATION',
                TABLE_CATALOG,
                TABLE_NAME,
                COLUMN_NAME,
                ORDINAL_POSITION,
                DATA_TYPE,
                IS_NULLABLE
            FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'

            UNION ALL

            SELECT
                'DEV_REPORTING',
                TABLE_CATALOG,
                TABLE_NAME,
                COLUMN_NAME,
                ORDINAL_POSITION,
                DATA_TYPE,
                IS_NULLABLE
            FROM DEV_REPORTING.INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
        )
        SELECT * FROM all_columns ORDER BY LAYER, TABLE_NAME, ORDINAL_POSITION
        """
        self.execute_query("columns", columns_query)

        # 3. Potential relationships analysis
        relationships_query = """
        WITH key_columns AS (
            SELECT DISTINCT
                TABLE_CATALOG || '.' || TABLE_SCHEMA || '.' || TABLE_NAME as FULL_TABLE,
                TABLE_NAME,
                COLUMN_NAME,
                DATA_TYPE
            FROM (
                SELECT * FROM DEV_LANDING.INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                UNION ALL
                SELECT * FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                UNION ALL
                SELECT * FROM DEV_REPORTING.INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
            )
            WHERE COLUMN_NAME LIKE '%_ID'
               OR COLUMN_NAME LIKE '%_KEY'
               OR COLUMN_NAME LIKE '%_CODE'
        )
        SELECT
            k1.FULL_TABLE as FROM_TABLE,
            k1.COLUMN_NAME as FROM_COLUMN,
            k2.FULL_TABLE as TO_TABLE,
            REGEXP_REPLACE(k1.COLUMN_NAME, '(_ID|_KEY|_CODE)$', '') as RELATIONSHIP_BASE
        FROM key_columns k1
        CROSS JOIN key_columns k2
        WHERE k1.FULL_TABLE != k2.FULL_TABLE
          AND UPPER(k2.TABLE_NAME) LIKE '%' || REGEXP_REPLACE(UPPER(k1.COLUMN_NAME), '(_ID|_KEY|_CODE)$', '') || '%'
        """
        self.execute_query("relationships", relationships_query)

    def export_to_excel(self, filename=None):
        """Export all results to an Excel file"""
        if not filename:
            filename = f"ITSECKPI_DataModel_{self.timestamp}.xlsx"

        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = self.create_summary()
                summary_data.to_excel(writer, sheet_name='Summary', index=False)

                # Export each result to a sheet
                for sheet_name, df in self.results.items():
                    if df is not None and not df.empty:
                        df.to_excel(writer, sheet_name=sheet_name.capitalize(), index=False)

            print(f"\nResults exported to: {filename}")
            return filename
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return None

    def export_to_json(self, filename=None):
        """Export results to JSON"""
        if not filename:
            filename = f"ITSECKPI_DataModel_{self.timestamp}.json"

        try:
            export_data = {
                'metadata': {
                    'timestamp': self.timestamp,
                    'schema': 'SECURITY_ANALYTICS',
                    'databases': ['DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING']
                },
                'results': {}
            }

            for name, df in self.results.items():
                if df is not None:
                    export_data['results'][name] = df.to_dict(orient='records')

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)

            print(f"Results exported to: {filename}")
            return filename
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return None

    def export_to_markdown(self, filename=None):
        """Generate Markdown documentation"""
        if not filename:
            filename = f"ITSECKPI_Documentation_{self.timestamp}.md"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# SECURITY_ANALYTICS Data Model Documentation\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                # Summary
                f.write("## Executive Summary\n\n")
                if 'inventory' in self.results:
                    inv_df = self.results['inventory']
                    f.write(f"- Total Objects: {len(inv_df)}\n")
                    f.write(f"- Tables: {len(inv_df[inv_df['TABLE_TYPE'] == 'BASE TABLE'])}\n")
                    f.write(f"- Views: {len(inv_df[inv_df['TABLE_TYPE'] == 'VIEW'])}\n\n")

                # Inventory by layer
                f.write("## Objects by Layer\n\n")
                if 'inventory' in self.results:
                    for layer in ['DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING']:
                        layer_df = inv_df[inv_df['LAYER'] == layer]
                        if not layer_df.empty:
                            f.write(f"### {layer}\n\n")
                            f.write("| Table Name | Type | Row Count | Size (MB) |\n")
                            f.write("|------------|------|-----------|----------|\n")
                            for _, row in layer_df.iterrows():
                                f.write(f"| {row['TABLE_NAME']} | {row['TABLE_TYPE']} | ")
                                f.write(f"{row['ROW_COUNT']:,} | {row['SIZE_MB']:.2f} |\n")
                            f.write("\n")

                # Relationships
                f.write("## Identified Relationships\n\n")
                if 'relationships' in self.results and not self.results['relationships'].empty:
                    rel_df = self.results['relationships']
                    f.write("| From Table | Column | To Table |\n")
                    f.write("|------------|--------|----------|\n")
                    for _, row in rel_df.head(20).iterrows():
                        f.write(f"| {row['FROM_TABLE'].split('.')[-1]} | ")
                        f.write(f"{row['FROM_COLUMN']} | ")
                        f.write(f"{row['TO_TABLE'].split('.')[-1]} |\n")

            print(f"Documentation generated: {filename}")
            return filename
        except Exception as e:
            print(f"Error generating documentation: {e}")
            return None

    def create_summary(self):
        """create a DataFrame with executive summary"""
        summary = []

        if 'inventory' in self.results:
            inv_df = self.results['inventory']
            summary.append({
                'Metric': 'Total Objects',
                'Value': len(inv_df)
            })
            summary.append({
                'Metric': 'Total Tables',
                'Value': len(inv_df[inv_df['TABLE_TYPE'] == 'BASE TABLE'])
            })
            summary.append({
                'Metric': 'Total Views',
                'Value': len(inv_df[inv_df['TABLE_TYPE'] == 'VIEW'])
            })
            summary.append({
                'Metric': 'Total Size (MB)',
                'Value': f"{inv_df['SIZE_MB'].sum():.2f}"
            })

        if 'columns' in self.results:
            col_df = self.results['columns']
            summary.append({
                'Metric': 'Total Columns',
                'Value': len(col_df)
            })

        if 'relationships' in self.results:
            rel_df = self.results['relationships']
            summary.append({
                'Metric': 'Potential Relationships',
                'Value': len(rel_df)
            })

        return pd.DataFrame(summary)

    def close(self):
        """Close the connection"""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()
        print("Connection closed")


def main():
    """Main function"""
    print("="*60)
    print(" SNOWFLAKE METADATA EXPORTER - SECURITY_ANALYTICS")
    print("="*60)

    # Connection configuration
    print("\nConfigure your Snowflake connection:")
    print("(Press Enter to use default values)")

    account = input("Account [your_account.region]: ").strip() or os.getenv('SNOWFLAKE_ACCOUNT')
    user = input("User: ").strip() or os.getenv('SNOWFLAKE_USER')
    password = input("Password: ").strip() or os.getenv('SNOWFLAKE_PASSWORD')
    warehouse = input("Warehouse [COMPUTE_WH]: ").strip() or 'COMPUTE_WH'
    role = input("Role [optional]: ").strip() or None

    connection_params = {
        'account': account,
        'user': user,
        'password': password,
        'warehouse': warehouse
    }
    if role:
        connection_params['role'] = role

    # create exporter
    exporter = SnowflakeMetadataExporter(connection_params)

    # Connect and execute analysis
    if exporter.connect():
        exporter.run_analysis()

        # Export results
        print("\n" + "="*60)
        print("EXPORTING RESULTS")
        print("="*60)

        # create output folder
        output_dir = f"ITSECKPI_Export_{exporter.timestamp}"
        os.makedirs(output_dir, exist_ok=True)

        # Export in multiple formats
        excel_file = exporter.export_to_excel(os.path.join(output_dir, "DataModel.xlsx"))
        json_file = exporter.export_to_json(os.path.join(output_dir, "DataModel.json"))
        md_file = exporter.export_to_markdown(os.path.join(output_dir, "Documentation.md"))

        print("\n" + "="*60)
        print("PROCESS COMPLETED")
        print("="*60)
        print(f"\nFiles generated in: {output_dir}/")
        print("  - DataModel.xlsx - Complete analysis in Excel")
        print("  - DataModel.json - Data in JSON format")
        print("  - Documentation.md - Documentation in Markdown")

        # Close connection
        exporter.close()
    else:
        print("\nCould not establish connection with Snowflake")


if __name__ == "__main__":
    main()
