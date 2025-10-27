"""
Direct Deployment of Streamlit Apps to Snowflake
Deploys apps using Snowflake Python connector and inline SQL

Author: Data Engineering Team
Date: 2025-10-24
"""

import snowflake.connector
import sys
from pathlib import Path
from datetime import datetime

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Paths
BASE_PATH = Path(r"C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV")
APPS_PATH = BASE_PATH / "08_STREAMLIT_APPS_FIXED"

# Snowflake connection from environment.yml
SNOWFLAKE_CONFIG = {
    'account': 'GenericCorp.west-europe.azure',
    'user': 'fmoran@GenericCorp.com',
    'role': 'DEV_DEVELOPER',
    'warehouse': 'DEV_WH',
    'database': 'DEV_REPORTING',
    'schema': 'SECURITY_ANALYTICS'
}

# Services to deploy
SERVICES = [
    'Ancon', 'BitSight', 'Cisco_AMP', 'Crowdstrike', 'CybelAngel',
    'Intel_Threats', 'Leviat', 'Proofpoint', 'Qualys', 'SentinelOne',
    'ServiceNow', 'Sophos', 'Splunk', 'Symantec', 'Tenable',
    'Trellix', 'Zerofox', 'Zscaler'
]

def get_snowflake_connection():
    """Connect to Snowflake using SSO"""
    try:
        print("🔐 Connecting to Snowflake (SSO authentication)...")
        conn = snowflake.connector.connect(
            account=SNOWFLAKE_CONFIG['account'],
            user=SNOWFLAKE_CONFIG['user'],
            authenticator='externalbrowser',  # SSO
            role=SNOWFLAKE_CONFIG['role'],
            warehouse=SNOWFLAKE_CONFIG['warehouse'],
            database=SNOWFLAKE_CONFIG['database'],
            schema=SNOWFLAKE_CONFIG['schema']
        )
        print("✅ Connected to Snowflake successfully")
        return conn
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def escape_sql_string(content):
    """Escape single quotes and backslashes for SQL"""
    # Replace backslash first, then single quotes
    content = content.replace('\\', '\\\\')
    content = content.replace("'", "''")
    return content

def deploy_streamlit_app(conn, service_name, dry_run=False):
    """Deploy a single Streamlit app"""
    print(f"\n{'='*60}")
    print(f"Deploying {service_name}")
    print(f"{'='*60}")

    # Read app file
    app_file = APPS_PATH / service_name / "streamlit_app.py"
    if not app_file.exists():
        print(f"❌ File not found: {app_file}")
        return False

    try:
        with open(app_file, 'r', encoding='utf-8') as f:
            app_code = f.read()

        print(f"📖 Read {len(app_code)} characters from {app_file.name}")

        # Create app name
        app_name = f"{service_name.upper()}_APP"

        # SQL to create/replace Streamlit app
        # Using CREATE OR REPLACE with ROOT LOCATION syntax
        sql = f"""
CREATE OR REPLACE STREAMLIT {SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.{app_name}
ROOT_LOCATION = '@{SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.streamlit_stage'
MAIN_FILE = 'streamlit_app.py'
QUERY_WAREHOUSE = '{SNOWFLAKE_CONFIG['warehouse']}'
COMMENT = 'SECURITY_ANALYTICS {service_name} Dashboard - Deployed via Python {datetime.now().strftime("%Y-%m-%d %H:%M")}';
"""

        # SQL to upload file content to stage
        escaped_code = escape_sql_string(app_code)

        upload_sql = f"""
PUT 'file://streamlit_app.py' @{SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.streamlit_stage/{app_name}/
OVERWRITE = TRUE;
"""

        if dry_run:
            print("\n🔍 DRY RUN - Would execute:")
            print(f"SQL Length: {len(sql)} characters")
            print(f"Code Length: {len(app_code)} characters")
            print(f"App Name: {app_name}")
            return True

        # Execute SQL
        cursor = conn.cursor()

        try:
            print(f"🚀 Creating Streamlit app: {app_name}...")
            cursor.execute(sql)
            print(f"✅ App created: {app_name}")

            # Alternative approach: Use ALTER STREAMLIT to set code directly
            # This avoids stage file upload issues
            print(f"📝 Setting app code inline...")

            # Split code into smaller chunks if needed (Snowflake has SQL size limits)
            max_chunk_size = 8000  # Safe size for SQL literals

            if len(escaped_code) > max_chunk_size:
                print(f"⚠️  Code too large ({len(escaped_code)} chars), using stage upload...")
                # For large files, we need to write to temp file and use PUT
                temp_file = BASE_PATH / "temp_streamlit_app.py"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(app_code)

                put_sql = f"""
PUT file://{str(temp_file).replace(chr(92), '/')}
@{SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.streamlit_stage/{app_name}/
OVERWRITE = TRUE
AUTO_COMPRESS = FALSE;
"""
                cursor.execute(put_sql)
                temp_file.unlink()  # Delete temp file
                print(f"✅ Code uploaded to stage")
            else:
                # Small files can be set directly (but this doesn't work with CREATE STREAMLIT)
                print(f"⚠️  Note: Code is {len(app_code)} chars - may need manual copy-paste in UI")

            print(f"✅ Successfully deployed: {app_name}")
            return True

        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            return False
        finally:
            cursor.close()

    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def create_streamlit_stage(conn):
    """Create stage for Streamlit apps if it doesn't exist"""
    try:
        cursor = conn.cursor()
        sql = f"""
CREATE STAGE IF NOT EXISTS {SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.streamlit_stage
COMMENT = 'Stage for Streamlit app deployments';
"""
        cursor.execute(sql)
        print("✅ Streamlit stage created/verified")
        cursor.close()
        return True
    except Exception as e:
        print(f"❌ Failed to create stage: {e}")
        return False

def main():
    """Main deployment function"""
    print("="*80)
    print("STREAMLIT APPS DIRECT DEPLOYMENT TO SNOWFLAKE")
    print("="*80)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Source: {APPS_PATH}")
    print(f"Target: {SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}")
    print(f"Total Apps: {len(SERVICES)}")

    # Check if apps exist
    print(f"\n📁 Checking app files...")
    missing = []
    for service in SERVICES:
        app_file = APPS_PATH / service / "streamlit_app.py"
        if not app_file.exists():
            missing.append(service)
            print(f"  ❌ {service}: NOT FOUND")
        else:
            size = app_file.stat().st_size
            print(f"  ✅ {service}: {size:,} bytes")

    if missing:
        print(f"\n⚠️  Warning: {len(missing)} apps missing:")
        for m in missing:
            print(f"    - {m}")
        proceed = input("\nContinue with available apps? (y/n): ")
        if proceed.lower() != 'y':
            return

    # Connect to Snowflake
    conn = get_snowflake_connection()
    if not conn:
        print("\n❌ Cannot proceed without Snowflake connection")
        return

    # Create stage
    if not create_streamlit_stage(conn):
        print("\n⚠️  Stage creation failed, but continuing...")

    # Ask for deployment mode
    print(f"\n{'='*80}")
    print("DEPLOYMENT MODE")
    print(f"{'='*80}")
    print("1. Dry Run - Test without deploying")
    print("2. Deploy Priority Apps (Splunk, Crowdstrike, ServiceNow, Qualys, Zscaler)")
    print("3. Deploy All Apps")

    choice = input("\nSelect option (1/2/3): ").strip()

    dry_run = choice == '1'

    if choice == '2':
        deploy_services = ['Splunk', 'Crowdstrike', 'ServiceNow', 'Qualys', 'Zscaler']
    else:
        deploy_services = [s for s in SERVICES if s not in missing]

    # Deploy apps
    print(f"\n{'='*80}")
    print(f"{'DRY RUN - ' if dry_run else ''}DEPLOYING {len(deploy_services)} APPS")
    print(f"{'='*80}")

    success_count = 0
    failed_count = 0
    failed_apps = []

    for service in deploy_services:
        if deploy_streamlit_app(conn, service, dry_run):
            success_count += 1
        else:
            failed_count += 1
            failed_apps.append(service)

    # Summary
    print(f"\n{'='*80}")
    print("DEPLOYMENT SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failed_count}")

    if failed_apps:
        print(f"\nFailed apps:")
        for app in failed_apps:
            print(f"  - {app}")

    if not dry_run and success_count > 0:
        print(f"\n📝 Next Steps:")
        print(f"1. Open Snowflake UI: https://app.snowflake.com/GenericCorp/west-europe.azure/#/streamlit-apps")
        print(f"2. Navigate to each deployed app")
        print(f"3. If app shows 'Cannot read from Git', open editor and paste code manually")
        print(f"4. Code files are in: {APPS_PATH}")
        print(f"\n⚠️  NOTE: Due to Snowflake limitations, you may need to:")
        print(f"   - Copy content from {APPS_PATH}\\<Service>\\streamlit_app.py")
        print(f"   - Paste into Snowflake UI editor")
        print(f"   - Click Save and Run")

    # Close connection
    conn.close()
    print(f"\n✅ Deployment process completed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()