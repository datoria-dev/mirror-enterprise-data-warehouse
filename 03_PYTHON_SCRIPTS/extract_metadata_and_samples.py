"""
SECURITY_ANALYTICS Metadata and Data Sample Extractor

This script extracts comprehensive metadata and data samples from Snowflake tables
to help build and validate Streamlit applications.

Outputs:
- Table metadata (columns, types, constraints)
- Data samples (first 100 rows per table)
- Summary report in JSON and Excel formats
- CSV files organized by service

Author: GenericCorp Data Engineering Team
Date: October 2025
"""

import snowflake.connector
import pandas as pd
import json
import os
from datetime import datetime
from pathlib import Path
import sys

# Configuration
CONFIG = {
    'account': 'your_account',
    'user': 'your_user',
    'password': 'your_password',
    'warehouse': 'DEV_WH',
    'role': 'SECURITY_ANALYTICS',
    'databases': {
        'landing': 'DEV_LANDING',
        'transformation': 'DEV_TRANSFORMATION'
    },
    'schema': 'SECURITY_ANALYTICS',
    'sample_size': 100,
    'output_dir': './04_METADATA_SAMPLES'
}

# Service mapping - tables/views belonging to each service
SERVICE_MAPPING = {
    'SentinelOne': {
        'landing': ['L_SENTINELONE_RAW'],
        'transformation': ['FACT_SENTINEL_ENDPOINTS', 'DIM_SENTINEL_VERSIONS']
    },
    'Tenable': {
        'landing': ['L_TENABLE_ASSETS'],
        'transformation': ['FACT_TENABLE', 'DIM_TENABLE_VULN']
    },
    'CybelAngel': {
        'landing': [],
        'transformation': ['FACT_CYBELANGEL_THREATS', 'DIM_CYBELANGEL_ALERTS']
    },
    'Leviat': {
        'landing': [],
        'transformation': ['DIM_LEVIAT_USERS', 'DIM_LEVIAT_LIST_USERS', 'FACT_LEVIAT_SECURITY_EVENTS']
    },
    'ServiceNow': {
        'landing': ['L_SNOW_INCIDENTS', 'L_SNOW_CMDB_CI', 'L_SNOW_CHANGES', 'L_SNOW_USERS', 'L_SNOW_PROBLEMS'],
        'transformation': ['DIM_SNOW_INCIDENT', 'DIM_SNOW_DEVICE', 'DIM_SNOW_CHANGE']
    },
    'Proofpoint': {
        'landing': ['L_PROOFPOINT_RAW', 'STG_PROOFPOINT_LOGS'],
        'transformation': []
    },
    'CrowdStrike': {
        'landing': ['L_CROWDSTRIKE_EVENTS'],
        'transformation': ['FACT_EDR', 'DIM_CROWDSTRIKE']
    },
    'Qualys': {
        'landing': ['L_QUALYS_VULNERABILITIES'],
        'transformation': ['FACT_QUALYS', 'DIM_QUALYS_VULN']
    },
    'BitSight': {
        'landing': ['L_BITSIGHT_RATINGS'],
        'transformation': ['FACT_BITSIGHT', 'DIM_BITSIGHT']
    },
    'ZeroFox': {
        'landing': ['L_ZEROFOX_ALERTS'],
        'transformation': ['FACT_ZEROFOX', 'DIM_ZEROFOX']
    },
    'Splunk': {
        'landing': ['L_SPLUNK_LOGS'],
        'transformation': ['FACT_SPLUNK', 'DIM_SPLUNK']
    },
    'Sophos': {
        'landing': ['L_SOPHOS_EVENTS'],
        'transformation': ['FACT_SOPHOS', 'DIM_SOPHOS']
    },
    'Symantec': {
        'landing': ['L_SYMANTEC_EVENTS'],
        'transformation': ['FACT_SYMANTEC', 'DIM_SYMANTEC']
    },
    'Trellix': {
        'landing': ['L_TRELLIX_EVENTS'],
        'transformation': ['FACT_TRELLIX', 'DIM_TRELLIX']
    },
    'Ancon': {
        'landing': ['L_ANCON_USERS'],
        'transformation': ['DIM_ANCON_USERS', 'FACT_ANCON']
    }
}


class SnowflakeMetadataExtractor:
    """Extract metadata and data samples from Snowflake tables"""

    def __init__(self, config):
        self.config = config
        self.conn = None
        self.cursor = None
        self.metadata = {}
        self.samples = {}
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Create output directories
        self.base_dir = Path(config['output_dir'])
        self.metadata_dir = self.base_dir / 'metadata'
        self.samples_dir = self.base_dir / 'samples'
        self.reports_dir = self.base_dir / 'reports'

        for dir_path in [self.metadata_dir, self.samples_dir, self.reports_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def connect(self):
        """Establish Snowflake connection"""
        try:
            self.conn = snowflake.connector.connect(
                account=self.config['account'],
                user=self.config['user'],
                password=self.config['password'],
                warehouse=self.config['warehouse'],
                role=self.config['role']
            )
            self.cursor = self.conn.cursor()
            print(f"✓ Connected to Snowflake as {self.config['user']}")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to Snowflake: {e}")
            return False

    def disconnect(self):
        """Close Snowflake connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("✓ Disconnected from Snowflake")

    def get_table_metadata(self, database, schema, table_name):
        """Extract metadata for a specific table"""
        print(f"  Extracting metadata for {database}.{schema}.{table_name}...")

        metadata = {
            'database': database,
            'schema': schema,
            'table_name': table_name,
            'columns': [],
            'row_count': 0,
            'constraints': [],
            'sample_query': None
        }

        try:
            # Get column information
            column_query = f"""
                SELECT
                    COLUMN_NAME,
                    DATA_TYPE,
                    CHARACTER_MAXIMUM_LENGTH,
                    NUMERIC_PRECISION,
                    NUMERIC_SCALE,
                    IS_NULLABLE,
                    COLUMN_DEFAULT,
                    COMMENT
                FROM {database}.INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = '{schema}'
                  AND TABLE_NAME = '{table_name}'
                ORDER BY ORDINAL_POSITION
            """

            self.cursor.execute(column_query)
            columns = self.cursor.fetchall()

            for col in columns:
                metadata['columns'].append({
                    'name': col[0],
                    'data_type': col[1],
                    'max_length': col[2],
                    'numeric_precision': col[3],
                    'numeric_scale': col[4],
                    'nullable': col[5] == 'YES',
                    'default_value': col[6],
                    'comment': col[7]
                })

            # Get row count
            count_query = f"SELECT COUNT(*) FROM {database}.{schema}.{table_name}"
            self.cursor.execute(count_query)
            metadata['row_count'] = self.cursor.fetchone()[0]

            # Get primary key constraints
            pk_query = f"""
                SELECT COLUMN_NAME
                FROM {database}.INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                JOIN {database}.INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
                    ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
                WHERE tc.TABLE_SCHEMA = '{schema}'
                  AND tc.TABLE_NAME = '{table_name}'
                  AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
            """

            try:
                self.cursor.execute(pk_query)
                pk_columns = [row[0] for row in self.cursor.fetchall()]
                if pk_columns:
                    metadata['constraints'].append({
                        'type': 'PRIMARY KEY',
                        'columns': pk_columns
                    })
            except:
                pass  # No primary key

            # Create sample query
            column_names = [col['name'] for col in metadata['columns']]
            metadata['sample_query'] = f"SELECT {', '.join(column_names)} FROM {database}.{schema}.{table_name} LIMIT {self.config['sample_size']}"

            print(f"    ✓ Found {len(metadata['columns'])} columns, {metadata['row_count']:,} rows")

        except Exception as e:
            print(f"    ✗ Error extracting metadata: {e}")
            metadata['error'] = str(e)

        return metadata

    def extract_data_sample(self, database, schema, table_name):
        """Extract sample data from a table"""
        print(f"  Extracting sample data from {database}.{schema}.{table_name}...")

        try:
            query = f"SELECT * FROM {database}.{schema}.{table_name} LIMIT {self.config['sample_size']}"

            # Use pandas for easy CSV export
            df = pd.read_sql(query, self.conn)

            print(f"    ✓ Extracted {len(df)} rows, {len(df.columns)} columns")

            return df

        except Exception as e:
            print(f"    ✗ Error extracting sample: {e}")
            return pd.DataFrame()

    def process_service(self, service_name, service_config):
        """Process all tables for a specific service"""
        print(f"\n{'='*60}")
        print(f"Processing Service: {service_name}")
        print(f"{'='*60}")

        service_metadata = {
            'service_name': service_name,
            'landing_tables': [],
            'transformation_tables': [],
            'total_tables': 0,
            'total_rows': 0
        }

        # Process landing tables
        for table_name in service_config.get('landing', []):
            db = self.config['databases']['landing']
            schema = self.config['schema']

            # Extract metadata
            metadata = self.get_table_metadata(db, schema, table_name)
            service_metadata['landing_tables'].append(metadata)
            service_metadata['total_rows'] += metadata.get('row_count', 0)

            # Extract sample
            sample_df = self.extract_data_sample(db, schema, table_name)

            if not sample_df.empty:
                # Save sample to CSV
                csv_path = self.samples_dir / f"{service_name}_LANDING_{table_name}.csv"
                sample_df.to_csv(csv_path, index=False)
                print(f"    ✓ Saved sample to {csv_path.name}")

            # Save metadata to JSON
            metadata_path = self.metadata_dir / f"{service_name}_LANDING_{table_name}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)

        # Process transformation tables
        for table_name in service_config.get('transformation', []):
            db = self.config['databases']['transformation']
            schema = self.config['schema']

            # Extract metadata
            metadata = self.get_table_metadata(db, schema, table_name)
            service_metadata['transformation_tables'].append(metadata)
            service_metadata['total_rows'] += metadata.get('row_count', 0)

            # Extract sample
            sample_df = self.extract_data_sample(db, schema, table_name)

            if not sample_df.empty:
                # Save sample to CSV
                csv_path = self.samples_dir / f"{service_name}_TRANSFORMATION_{table_name}.csv"
                sample_df.to_csv(csv_path, index=False)
                print(f"    ✓ Saved sample to {csv_path.name}")

            # Save metadata to JSON
            metadata_path = self.metadata_dir / f"{service_name}_TRANSFORMATION_{table_name}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)

        service_metadata['total_tables'] = len(service_metadata['landing_tables']) + len(service_metadata['transformation_tables'])

        return service_metadata

    def generate_summary_report(self, all_metadata):
        """Generate comprehensive summary report"""
        print(f"\n{'='*60}")
        print("Generating Summary Report")
        print(f"{'='*60}")

        # JSON report
        json_path = self.reports_dir / f"metadata_summary_{self.timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(all_metadata, f, indent=2, default=str)
        print(f"✓ Saved JSON report: {json_path.name}")

        # Excel report with multiple sheets
        excel_path = self.reports_dir / f"metadata_summary_{self.timestamp}.xlsx"

        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = []
            for service_name, service_meta in all_metadata.items():
                summary_data.append({
                    'Service': service_name,
                    'Landing Tables': len(service_meta.get('landing_tables', [])),
                    'Transformation Tables': len(service_meta.get('transformation_tables', [])),
                    'Total Tables': service_meta.get('total_tables', 0),
                    'Total Rows': service_meta.get('total_rows', 0)
                })

            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # Detailed sheets for each service
            for service_name, service_meta in all_metadata.items():
                # Landing tables details
                if service_meta.get('landing_tables'):
                    landing_details = []
                    for table in service_meta['landing_tables']:
                        landing_details.append({
                            'Table': table['table_name'],
                            'Row Count': table.get('row_count', 0),
                            'Column Count': len(table.get('columns', [])),
                            'Has PK': any(c['type'] == 'PRIMARY KEY' for c in table.get('constraints', []))
                        })

                    if landing_details:
                        df = pd.DataFrame(landing_details)
                        sheet_name = f"{service_name[:20]}_Landing"
                        df.to_excel(writer, sheet_name=sheet_name, index=False)

                # Transformation tables details
                if service_meta.get('transformation_tables'):
                    transform_details = []
                    for table in service_meta['transformation_tables']:
                        transform_details.append({
                            'Table': table['table_name'],
                            'Row Count': table.get('row_count', 0),
                            'Column Count': len(table.get('columns', [])),
                            'Has PK': any(c['type'] == 'PRIMARY KEY' for c in table.get('constraints', []))
                        })

                    if transform_details:
                        df = pd.DataFrame(transform_details)
                        sheet_name = f"{service_name[:20]}_Transform"
                        df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"✓ Saved Excel report: {excel_path.name}")

        # Create README
        readme_path = self.base_dir / 'README.md'
        readme_content = f"""# SECURITY_ANALYTICS Metadata and Data Samples

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

This directory contains metadata and data samples extracted from Snowflake for all SECURITY_ANALYTICS services.

## Directory Structure

```
04_METADATA_SAMPLES/
├── metadata/          # JSON metadata files for each table
├── samples/           # CSV sample data (first {self.config['sample_size']} rows)
├── reports/           # Summary reports (JSON and Excel)
└── README.md          # This file
```

## Services Processed

{len(all_metadata)} services with data:

"""

        for service_name, service_meta in sorted(all_metadata.items()):
            readme_content += f"- **{service_name}**: {service_meta['total_tables']} tables, {service_meta['total_rows']:,} total rows\n"

        readme_content += f"""

## Files Generated

### Metadata Files
Located in `metadata/` directory. Each file contains:
- Column names and data types
- Nullability and constraints
- Row counts
- Primary key information

### Sample Data Files
Located in `samples/` directory. Contains:
- First {self.config['sample_size']} rows of each table
- CSV format for easy analysis
- Actual data values for understanding structure

### Reports
Located in `reports/` directory:
- `metadata_summary_{self.timestamp}.json` - Complete metadata in JSON format
- `metadata_summary_{self.timestamp}.xlsx` - Summary and details in Excel format

## Usage for Streamlit Development

1. Review sample CSV files to understand data structure
2. Check metadata JSON for column types and constraints
3. Use samples to build test cases and validation logic
4. Reference actual column names and data types in queries

## Example: Building a Streamlit Query

```python
# Example for SentinelOne based on extracted metadata
query = \"\"\"
    SELECT
        EVENT_TIMESTAMP,
        THREAT_SEVERITY,
        ENDPOINT_NAME,
        THREAT_TYPE
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_SENTINEL_ENDPOINTS
    WHERE EVENT_TIMESTAMP >= DATEADD(day, -7, CURRENT_DATE())
    ORDER BY EVENT_TIMESTAMP DESC
    LIMIT 1000
\"\"\"
```

---

**Note**: Sample data is limited to {self.config['sample_size']} rows per table for analysis purposes.
"""

        with open(readme_path, 'w') as f:
            f.write(readme_content)

        print(f"✓ Created README: {readme_path.name}")

    def run(self):
        """Main execution flow"""
        print(f"""
{'='*60}
SECURITY_ANALYTICS Metadata and Data Sample Extractor
{'='*60}
Output Directory: {self.config['output_dir']}
Sample Size: {self.config['sample_size']} rows per table
Timestamp: {self.timestamp}
{'='*60}
""")

        if not self.connect():
            return

        try:
            all_metadata = {}

            # Process each service
            for service_name, service_config in SERVICE_MAPPING.items():
                try:
                    service_metadata = self.process_service(service_name, service_config)
                    all_metadata[service_name] = service_metadata
                except Exception as e:
                    print(f"✗ Error processing {service_name}: {e}")
                    all_metadata[service_name] = {'error': str(e)}

            # Generate summary report
            self.generate_summary_report(all_metadata)

            print(f"\n{'='*60}")
            print("✓ Extraction Complete!")
            print(f"{'='*60}")
            print(f"Metadata files: {self.metadata_dir}")
            print(f"Sample CSV files: {self.samples_dir}")
            print(f"Reports: {self.reports_dir}")
            print(f"{'='*60}\n")

        finally:
            self.disconnect()


def main():
    """Main entry point"""
    # Note: Update CONFIG with your Snowflake credentials
    print("""
WARNING: Before running this script, update the CONFIG dictionary with your Snowflake credentials.

Required configuration:
- account: Your Snowflake account identifier
- user: Your Snowflake username
- password: Your password (or use key-pair authentication)
- warehouse: DEV_WH (or your warehouse)
- role: SECURITY_ANALYTICS (or your role)
""")

    response = input("Have you updated the credentials? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Please update credentials in CONFIG and run again.")
        return

    extractor = SnowflakeMetadataExtractor(CONFIG)
    extractor.run()


if __name__ == "__main__":
    main()
