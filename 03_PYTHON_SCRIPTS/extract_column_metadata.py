"""
================================================================================
Extract Column Metadata to JSON and CSV Files
================================================================================

This script extracts column metadata from Snowflake and saves it to:
- JSON files (for programmatic access)
- CSV files (for manual review)

Author: GenericCorp Data Engineering Team
Date: 2025-10-24
================================================================================
"""

import snowflake.connector
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Configuration
SNOWFLAKE_ACCOUNT = "your_account"  # Update with your account
SNOWFLAKE_USER = "your_user"        # Update with your user
SNOWFLAKE_ROLE = "DEV_DEVELOPER"
SNOWFLAKE_WAREHOUSE = "DEV_WH"
SNOWFLAKE_DATABASE = "DEV_TRANSFORMATION"

# Output directories
OUTPUT_DIR = Path("C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/04_METADATA_SAMPLES")
METADATA_DIR = OUTPUT_DIR / "metadata"
JSON_DIR = OUTPUT_DIR / "json"

# Create directories if they don't exist
METADATA_DIR.mkdir(parents=True, exist_ok=True)
JSON_DIR.mkdir(parents=True, exist_ok=True)

# Main tables to extract
MAIN_TABLES = {
    "SentinelOne": [
        "FACT_SENTINEL_ENDPOINTS",
        "DIM_SENTINEL_VERSIONS"
    ],
    "CybelAngel": [
        "DIM_CYBELANGEL_ALERTS",
        "FACT_CYBELANGEL_THREATS"
    ],
    "Proofpoint": [
        "PROOFPOINT_MESSAGE_LOGS",
        "L_PROOFPOINT_RAW"
    ],
    "ServiceNow": [
        "SNOW"
    ],
    "Leviat": [
        "DIM_LEVIAT_USERS",
        "DIM_LEVIAT_LIST_USERS",
        "FACT_LEVIAT_SECURITY_EVENTS"
    ]
}


def get_snowflake_connection():
    """Create Snowflake connection using credentials from environment or prompt."""
    try:
        # Try to get credentials from environment variables first
        import os
        user = os.getenv('SNOWFLAKE_USER', SNOWFLAKE_USER)
        password = os.getenv('SNOWFLAKE_PASSWORD')

        if not password:
            import getpass
            password = getpass.getpass(f"Enter password for {user}: ")

        conn = snowflake.connector.connect(
            account=SNOWFLAKE_ACCOUNT,
            user=user,
            password=password,
            role=SNOWFLAKE_ROLE,
            warehouse=SNOWFLAKE_WAREHOUSE,
            database=SNOWFLAKE_DATABASE
        )
        print(f"✅ Connected to Snowflake as {user}")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to Snowflake: {e}")
        return None


def extract_table_columns(conn, table_name):
    """Extract column metadata for a specific table."""
    query = f"""
    SELECT
        TABLE_NAME,
        COLUMN_NAME,
        DATA_TYPE,
        IS_NULLABLE,
        ORDINAL_POSITION,
        COMMENT
    FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
    WHERE TABLE_NAME = '{table_name}'
    ORDER BY ORDINAL_POSITION
    """

    try:
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        print(f"❌ Error extracting columns for {table_name}: {e}")
        return None


def extract_service_columns(conn, service_name):
    """Extract all column metadata for a specific service."""
    query = f"""
    SELECT
        TABLE_NAME,
        COLUMN_NAME,
        DATA_TYPE,
        IS_NULLABLE,
        ORDINAL_POSITION,
        COMMENT
    FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
    WHERE SERVICE_NAME = '{service_name}'
    ORDER BY TABLE_NAME, ORDINAL_POSITION
    """

    try:
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        print(f"❌ Error extracting columns for {service_name}: {e}")
        return None


def save_to_json(data_dict, filename):
    """Save data dictionary to JSON file."""
    filepath = JSON_DIR / f"{filename}.json"
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved JSON: {filepath.name}")
        return True
    except Exception as e:
        print(f"❌ Error saving JSON {filename}: {e}")
        return False


def save_to_csv(df, filename):
    """Save DataFrame to CSV file."""
    filepath = METADATA_DIR / f"{filename}.csv"
    try:
        df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"✅ Saved CSV: {filepath.name}")
        return True
    except Exception as e:
        print(f"❌ Error saving CSV {filename}: {e}")
        return False


def main():
    """Main extraction process."""
    print("=" * 80)
    print("Column Metadata Extraction Tool")
    print("=" * 80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Connect to Snowflake
    conn = get_snowflake_connection()
    if not conn:
        print("❌ Failed to connect to Snowflake. Exiting.")
        return

    print()
    print("=" * 80)
    print("Extracting Column Metadata")
    print("=" * 80)
    print()

    all_metadata = {}

    # Process each service
    for service_name, tables in MAIN_TABLES.items():
        print(f"\n📊 Processing {service_name}...")
        print("-" * 80)

        service_metadata = {
            "service_name": service_name,
            "extraction_date": datetime.now().isoformat(),
            "tables": {}
        }

        # Extract all columns for this service
        service_df = extract_service_columns(conn, service_name)
        if service_df is not None and not service_df.empty:
            # Save complete service metadata as CSV
            save_to_csv(service_df, f"metadata_{service_name.lower()}")

            # Process each main table
            for table_name in tables:
                print(f"  📋 Extracting {table_name}...")

                # Filter DataFrame for this table
                table_df = service_df[service_df['TABLE_NAME'] == table_name]

                if not table_df.empty:
                    # Convert to dictionary format
                    columns = []
                    for _, row in table_df.iterrows():
                        columns.append({
                            "name": row['COLUMN_NAME'],
                            "data_type": row['DATA_TYPE'],
                            "is_nullable": row['IS_NULLABLE'],
                            "ordinal_position": int(row['ORDINAL_POSITION']),
                            "comment": row['COMMENT'] if pd.notna(row['COMMENT']) else None
                        })

                    service_metadata["tables"][table_name] = {
                        "column_count": len(columns),
                        "columns": columns
                    }

                    print(f"    ✅ Found {len(columns)} columns")
                else:
                    print(f"    ⚠️  No columns found for {table_name}")

        # Save service metadata as JSON
        if service_metadata["tables"]:
            all_metadata[service_name] = service_metadata
            save_to_json(service_metadata, f"metadata_{service_name.lower()}")

    # Save combined metadata
    print()
    print("-" * 80)
    print("💾 Saving combined metadata...")
    combined_metadata = {
        "extraction_date": datetime.now().isoformat(),
        "services": all_metadata
    }
    save_to_json(combined_metadata, "metadata_all_services")

    # Create summary report
    print()
    print("=" * 80)
    print("📊 EXTRACTION SUMMARY")
    print("=" * 80)
    for service_name, metadata in all_metadata.items():
        print(f"\n{service_name}:")
        for table_name, table_info in metadata["tables"].items():
            print(f"  - {table_name}: {table_info['column_count']} columns")

    # Close connection
    conn.close()
    print()
    print("=" * 80)
    print(f"✅ Extraction completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Files saved to:")
    print(f"   - CSV: {METADATA_DIR}")
    print(f"   - JSON: {JSON_DIR}")
    print("=" * 80)


if __name__ == "__main__":
    main()
