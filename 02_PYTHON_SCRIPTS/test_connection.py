"""
Snowflake Connection Test and Database Discovery
================================================

Purpose: Test connection and discover available databases/schemas
"""

import os
import snowflake.connector
from dotenv import load_dotenv
from pathlib import Path

# Load environment
env_paths = [
    Path('.env'),
    Path('03_CONFIG/.env'),
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        print(f"📝 Loaded environment from: {env_path}\n")
        break

try:
    print("🔌 Connecting to Snowflake via SSO...")

    connection = snowflake.connector.connect(
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        user=os.getenv('SNOWFLAKE_USER'),
        authenticator='externalbrowser',
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE', 'DEV_WH'),
        role=os.getenv('SNOWFLAKE_ROLE', 'DEV_DEVELOPER')
    )

    cursor = connection.cursor()

    print("✅ Connected!\n")

    # Get current context
    print("="*60)
    print("CURRENT CONTEXT")
    print("="*60)
    cursor.execute("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE()")
    result = cursor.fetchone()
    print(f"User: {result[0]}")
    print(f"Role: {result[1]}")
    print(f"Warehouse: {result[2]}")

    # List available databases
    print("\n" + "="*60)
    print("AVAILABLE DATABASES")
    print("="*60)
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    print(f"\nFound {len(databases)} databases:\n")
    for i, db in enumerate(databases, 1):
        print(f"{i}. {db[1]}")  # db[1] is the database name

    # List schemas in each database
    print("\n" + "="*60)
    print("SCHEMAS IN EACH DATABASE")
    print("="*60)
    for db in databases:
        db_name = db[1]
        try:
            cursor.execute(f"SHOW SCHEMAS IN DATABASE {db_name}")
            schemas = cursor.fetchall()
            print(f"\n{db_name}:")
            for schema in schemas:
                print(f"  - {schema[1]}")  # schema[1] is the schema name
        except Exception as e:
            print(f"\n{db_name}:")
            print(f"  ⚠️  Cannot access: {str(e)[:100]}")

    # Try to find SECURITY_ANALYTICS or similar
    print("\n" + "="*60)
    print("LOOKING FOR SECURITY_ANALYTICS DATABASE")
    print("="*60)

    itseckpi_found = False
    for db in databases:
        db_name = db[1]
        if 'SECURITY_ANALYTICS' in db_name.upper() or 'KPI' in db_name.upper():
            print(f"\n✅ Found potential match: {db_name}")
            itseckpi_found = True

            # Try to use it and show schemas
            try:
                cursor.execute(f"USE DATABASE {db_name}")
                cursor.execute(f"SHOW SCHEMAS")
                schemas = cursor.fetchall()
                print(f"   Schemas in {db_name}:")
                for schema in schemas:
                    schema_name = schema[1]
                    print(f"     - {schema_name}")

                    # Check if it matches our expected schemas
                    if schema_name in ['DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING']:
                        print(f"       ✅ This matches expected schema!")
            except Exception as e:
                print(f"   ⚠️  Cannot access: {e}")

    if not itseckpi_found:
        print("\n⚠️  No database matching 'SECURITY_ANALYTICS' found.")
        print("Please check with your admin or provide the correct database name.")

    cursor.close()
    connection.close()

    print("\n" + "="*60)
    print("✅ Test completed successfully!")
    print("="*60)

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nPlease complete authentication in your browser if prompted.")
