"""
Simple Streamlit App Deployment to Snowflake
Creates apps and provides instructions for manual code paste

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
SERVICES = {
    'Priority': ['Splunk', 'Crowdstrike', 'ServiceNow', 'Qualys', 'Zscaler', 'SentinelOne'],
    'Standard': ['Ancon', 'BitSight', 'Cisco_AMP', 'CybelAngel', 'Intel_Threats',
                 'Leviat', 'Proofpoint', 'Sophos', 'Symantec', 'Tenable', 'Trellix', 'Zerofox']
}

def get_snowflake_connection():
    """Connect to Snowflake using SSO"""
    try:
        print("🔐 Connecting to Snowflake (SSO authentication)...")
        print("   A browser window will open for authentication...")
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

def create_streamlit_app_structure(conn, service_name):
    """Create empty Streamlit app in Snowflake"""
    app_name = f"{service_name.upper()}_APP"

    try:
        cursor = conn.cursor()

        # Drop existing app if it exists
        drop_sql = f"""
DROP STREAMLIT IF EXISTS {SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.{app_name};
"""
        print(f"  🗑️  Dropping existing {app_name} (if exists)...")
        cursor.execute(drop_sql)

        # Create new app
        create_sql = f"""
CREATE STREAMLIT {SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.{app_name}
QUERY_WAREHOUSE = '{SNOWFLAKE_CONFIG['warehouse']}'
COMMENT = 'SECURITY_ANALYTICS {service_name} Dashboard - Deployed {datetime.now().strftime("%Y-%m-%d %H:%M")}';
"""
        print(f"  ✅ Creating {app_name}...")
        cursor.execute(create_sql)

        print(f"  ✅ App created successfully: {app_name}")
        cursor.close()
        return True

    except Exception as e:
        print(f"  ❌ Failed to create {app_name}: {e}")
        return False

def generate_deployment_guide(services_deployed):
    """Generate step-by-step deployment guide"""
    guide_path = BASE_PATH / "DEPLOYMENT_GUIDE.txt"

    guide_content = f"""
{'='*80}
STREAMLIT APPS DEPLOYMENT GUIDE
{'='*80}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Apps: {len(services_deployed)}

{'='*80}
STEP-BY-STEP INSTRUCTIONS
{'='*80}

The Streamlit apps have been created in Snowflake, but you need to add the code
manually. Follow these steps for each app:

"""

    for i, service in enumerate(services_deployed, 1):
        app_name = f"{service.upper()}_APP"
        file_path = APPS_PATH / service / "streamlit_app.py"

        guide_content += f"""
{'─'*80}
{i}. {service} App
{'─'*80}

1. Open Snowflake UI in browser:
   https://app.snowflake.com/GenericCorp/west-europe.azure/

2. Navigate to:
   Data > Databases > DEV_REPORTING > SECURITY_ANALYTICS > Streamlit > {app_name}

3. Click the {app_name} to open it

4. Click "Edit" button (top right)

5. Open this file on your computer:
   {file_path}

6. Select ALL content (Ctrl+A) and Copy (Ctrl+C)

7. In Snowflake editor:
   - Delete any existing code
   - Paste the copied content (Ctrl+V)
   - Click "Save" button
   - Click "Run" button to test

8. Verify the app loads without errors

"""

    guide_content += f"""
{'='*80}
QUICK REFERENCE - FILE PATHS
{'='*80}

"""

    for service in services_deployed:
        file_path = APPS_PATH / service / "streamlit_app.py"
        guide_content += f"{service:20s} -> {file_path}\n"

    guide_content += f"""
{'='*80}
TROUBLESHOOTING
{'='*80}

If you see "ModuleNotFoundError":
  ✅ The apps in 08_STREAMLIT_APPS_FIXED are already cleaned
  ✅ Make sure you're copying from the FIXED folder, not the original

If the app doesn't load:
  1. Check Snowflake UI for error messages
  2. Verify the warehouse DEV_WH is running
  3. Check the app has correct database permissions

If you can't edit the app:
  1. Make sure you're using DEV_DEVELOPER role
  2. Verify you have write permissions on DEV_REPORTING.SECURITY_ANALYTICS

{'='*80}
NEXT STEPS (AFTER API INTEGRATION)
{'='*80}

Once Prabodh creates the API Integration:
  1. We'll connect apps to Azure DevOps Git repository
  2. Future updates will be automatic from Git
  3. No more manual copy-paste needed

For now, manual deployment is the only option.

{'='*80}
"""

    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)

    return guide_path

def main():
    """Main deployment function"""
    print("="*80)
    print("STREAMLIT APPS DEPLOYMENT - SNOWFLAKE")
    print("="*80)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Source: {APPS_PATH}")
    print(f"Target: {SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}")

    # Check apps exist
    print(f"\n📁 Checking app files...")
    all_services = SERVICES['Priority'] + SERVICES['Standard']
    available_services = []

    for service in all_services:
        app_file = APPS_PATH / service / "streamlit_app.py"
        if app_file.exists():
            size = app_file.stat().st_size
            available_services.append(service)
            status = "✅"
        else:
            size = 0
            status = "❌"

        print(f"  {status} {service:20s} {size:6,} bytes")

    if len(available_services) == 0:
        print("\n❌ No app files found. Cannot proceed.")
        return

    print(f"\n✅ Found {len(available_services)} apps ready for deployment")

    # Ask user what to deploy
    print(f"\n{'='*80}")
    print("DEPLOYMENT OPTIONS")
    print(f"{'='*80}")
    print("1. Priority Apps Only (Splunk, Crowdstrike, ServiceNow, Qualys, Zscaler, SentinelOne)")
    print("2. All Available Apps")
    print("3. Exit")

    choice = input("\nSelect option (1/2/3): ").strip()

    if choice == '1':
        deploy_services = [s for s in SERVICES['Priority'] if s in available_services]
    elif choice == '2':
        deploy_services = available_services
    else:
        print("Cancelled.")
        return

    if not deploy_services:
        print("No services to deploy.")
        return

    print(f"\n📋 Will deploy {len(deploy_services)} apps:")
    for service in deploy_services:
        print(f"   - {service}")

    confirm = input("\nProceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return

    # Connect to Snowflake
    conn = get_snowflake_connection()
    if not conn:
        print("\n❌ Cannot proceed without Snowflake connection")
        return

    # Deploy apps
    print(f"\n{'='*80}")
    print(f"CREATING STREAMLIT APPS IN SNOWFLAKE")
    print(f"{'='*80}")

    success_count = 0
    failed_count = 0
    failed_apps = []

    for service in deploy_services:
        print(f"\n{service}:")
        if create_streamlit_app_structure(conn, service):
            success_count += 1
        else:
            failed_count += 1
            failed_apps.append(service)

    # Close connection
    conn.close()

    # Generate deployment guide
    print(f"\n{'='*80}")
    print("GENERATING DEPLOYMENT GUIDE")
    print(f"{'='*80}")

    guide_path = generate_deployment_guide([s for s in deploy_services if s not in failed_apps])
    print(f"✅ Guide created: {guide_path}")

    # Summary
    print(f"\n{'='*80}")
    print("DEPLOYMENT SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Apps created in Snowflake: {success_count}")
    print(f"❌ Failed: {failed_count}")

    if failed_apps:
        print(f"\nFailed apps:")
        for app in failed_apps:
            print(f"  - {app}")

    if success_count > 0:
        print(f"\n{'='*80}")
        print("NEXT STEPS")
        print(f"{'='*80}")
        print(f"1. Open the deployment guide:")
        print(f"   {guide_path}")
        print(f"\n2. Follow the step-by-step instructions to paste code into each app")
        print(f"\n3. Apps are ready in Snowflake UI at:")
        print(f"   https://app.snowflake.com/GenericCorp/west-europe.azure/")
        print(f"   → Data → DEV_REPORTING → SECURITY_ANALYTICS → Streamlit")
        print(f"\n4. Each app needs code pasted from:")
        print(f"   {APPS_PATH}\\<ServiceName>\\streamlit_app.py")

        print(f"\n{'='*80}")
        print("💡 TIP: Keep the deployment guide open while working")
        print(f"{'='*80}")

    print(f"\n✅ Deployment script completed successfully")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()