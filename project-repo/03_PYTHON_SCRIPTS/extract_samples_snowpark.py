"""
SECURITY_ANALYTICS Data Sample Extractor (Snowpark Version)

Simplified version using Snowpark for extracting metadata and samples.
Works with existing Snowflake connection configuration.

Usage:
    python extract_samples_snowpark.py
"""

from snowflake.snowpark import Session
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Service to table mapping
SERVICE_TABLES = {
    'SentinelOne': {
        'FACT_SENTINEL_ENDPOINTS': 'transformation',
        'DIM_SENTINEL_VERSIONS': 'transformation',
        'L_SENTINELONE_RAW': 'landing'
    },
    'Tenable': {
        'FACT_TENABLE': 'transformation',
        'DIM_TENABLE_VULN': 'transformation',
        'L_TENABLE_ASSETS': 'landing'
    },
    'CybelAngel': {
        'FACT_CYBELANGEL_THREATS': 'transformation',
        'DIM_CYBELANGEL_ALERTS': 'transformation'
    },
    'Leviat': {
        'DIM_LEVIAT_USERS': 'transformation',
        'DIM_LEVIAT_LIST_USERS': 'transformation',
        'FACT_LEVIAT_SECURITY_EVENTS': 'transformation'
    },
    'ServiceNow': {
        'DIM_SNOW_INCIDENT': 'transformation',
        'DIM_SNOW_DEVICE': 'transformation',
        'DIM_SNOW_CHANGE': 'transformation',
        'L_SNOW_INCIDENTS': 'landing',
        'L_SNOW_CMDB_CI': 'landing',
        'L_SNOW_CHANGES': 'landing'
    },
    'Proofpoint': {
        'L_PROOFPOINT_RAW': 'landing',
        'STG_PROOFPOINT_LOGS': 'landing'
    }
}

# Database mapping
DB_MAP = {
    'landing': 'DEV_LANDING',
    'transformation': 'DEV_TRANSFORMATION'
}

SCHEMA = 'SECURITY_ANALYTICS'
SAMPLE_SIZE = 100


def create_session():
    """Create Snowpark session using default credentials"""
    # This assumes you have snowflake connection configured
    # via config.toml or environment variables
    try:
        connection_parameters = {
            "account": "your_account",
            "user": "your_user",
            "password": "your_password",
            "role": "SECURITY_ANALYTICS",
            "warehouse": "DEV_WH",
            "database": "DEV_TRANSFORMATION",
            "schema": "SECURITY_ANALYTICS"
        }

        session = Session.builder.configs(connection_parameters).create()
        print("✓ Connected to Snowflake")
        return session
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\nPlease update connection_parameters in the script with your credentials.")
        return None


def get_table_metadata(session, database, schema, table_name):
    """Extract metadata for a table"""
    print(f"  Extracting metadata: {database}.{schema}.{table_name}")

    try:
        # Get column information
        query = f"""
            SELECT
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COMMENT
            FROM {database}.INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{schema}'
              AND TABLE_NAME = '{table_name}'
            ORDER BY ORDINAL_POSITION
        """

        df = session.sql(query).to_pandas()

        metadata = {
            'database': database,
            'schema': schema,
            'table_name': table_name,
            'columns': df.to_dict('records'),
            'column_count': len(df),
            'timestamp': datetime.now().isoformat()
        }

        # Get row count
        count_query = f"SELECT COUNT(*) as ROW_COUNT FROM {database}.{schema}.{table_name}"
        count_df = session.sql(count_query).to_pandas()
        metadata['row_count'] = int(count_df['ROW_COUNT'].iloc[0])

        print(f"    ✓ {metadata['column_count']} columns, {metadata['row_count']:,} rows")

        return metadata

    except Exception as e:
        print(f"    ✗ Error: {e}")
        return None


def extract_sample_data(session, database, schema, table_name, limit=100):
    """Extract sample data from a table"""
    print(f"  Extracting sample data: {database}.{schema}.{table_name}")

    try:
        query = f"SELECT * FROM {database}.{schema}.{table_name} LIMIT {limit}"
        df = session.sql(query).to_pandas()

        print(f"    ✓ Extracted {len(df)} rows")
        return df

    except Exception as e:
        print(f"    ✗ Error: {e}")
        return pd.DataFrame()


def main():
    """Main execution"""
    print(f"""
{'='*70}
SECURITY_ANALYTICS Metadata and Sample Data Extractor (Snowpark)
{'='*70}
Sample Size: {SAMPLE_SIZE} rows per table
{'='*70}
    """)

    # Create output directories
    base_dir = Path('./04_METADATA_SAMPLES')
    metadata_dir = base_dir / 'metadata'
    samples_dir = base_dir / 'samples'
    reports_dir = base_dir / 'reports'

    for dir_path in [metadata_dir, samples_dir, reports_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)

    # Connect to Snowflake
    session = create_session()
    if not session:
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    all_metadata = {}

    try:
        # Process each service
        for service_name, tables in SERVICE_TABLES.items():
            print(f"\n{'='*70}")
            print(f"Processing: {service_name}")
            print(f"{'='*70}")

            service_meta = {
                'service_name': service_name,
                'tables': [],
                'total_rows': 0
            }

            for table_name, layer in tables.items():
                database = DB_MAP[layer]

                # Extract metadata
                metadata = get_table_metadata(session, database, SCHEMA, table_name)

                if metadata:
                    service_meta['tables'].append(metadata)
                    service_meta['total_rows'] += metadata['row_count']

                    # Save metadata JSON
                    metadata_file = metadata_dir / f"{service_name}_{table_name}_metadata.json"
                    with open(metadata_file, 'w') as f:
                        json.dump(metadata, f, indent=2, default=str)

                # Extract sample data
                sample_df = extract_sample_data(session, database, SCHEMA, table_name, SAMPLE_SIZE)

                if not sample_df.empty:
                    # Save sample CSV
                    csv_file = samples_dir / f"{service_name}_{table_name}_sample.csv"
                    sample_df.to_csv(csv_file, index=False)
                    print(f"    ✓ Saved: {csv_file.name}")

            all_metadata[service_name] = service_meta

        # Generate summary report
        print(f"\n{'='*70}")
        print("Generating Summary Report")
        print(f"{'='*70}")

        # JSON summary
        summary_file = reports_dir / f"extraction_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(all_metadata, f, indent=2, default=str)
        print(f"✓ Saved: {summary_file.name}")

        # Excel summary
        summary_data = []
        for service, meta in all_metadata.items():
            summary_data.append({
                'Service': service,
                'Table Count': len(meta['tables']),
                'Total Rows': meta['total_rows']
            })

        summary_df = pd.DataFrame(summary_data)
        excel_file = reports_dir / f"extraction_summary_{timestamp}.xlsx"
        summary_df.to_excel(excel_file, index=False, sheet_name='Summary')
        print(f"✓ Saved: {excel_file.name}")

        # Print summary
        print(f"\n{'='*70}")
        print("Extraction Summary")
        print(f"{'='*70}")
        print(summary_df.to_string(index=False))
        print(f"\n{'='*70}")
        print("✓ Extraction Complete!")
        print(f"{'='*70}")
        print(f"Metadata: {metadata_dir}")
        print(f"Samples:  {samples_dir}")
        print(f"Reports:  {reports_dir}")
        print(f"{'='*70}\n")

    finally:
        session.close()
        print("✓ Session closed")


if __name__ == "__main__":
    main()
