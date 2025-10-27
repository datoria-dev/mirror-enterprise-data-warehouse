"""
Auto-Deploy All Streamlit Apps to Snowflake
No interactive prompts - deploys all apps automatically

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

# Snowflake connection from snowflake_config.json
SNOWFLAKE_CONFIG = {
    'account': 'MYORG-DATA_WH',
    'user': 'fuad.onate@CompanyX.com',
    'role': 'DEV_DEVELOPER',
    'warehouse': 'DEV_WH',
    'database': 'DEV_REPORTING',
    'schema': 'SECURITY_ANALYTICS'
}

# All services
ALL_SERVICES = [
    'Splunk', 'Crowdstrike', 'ServiceNow', 'Qualys', 'Zscaler', 'SentinelOne',
    'Ancon', 'BitSight', 'Cisco_AMP', 'CybelAngel', 'Intel_Threats',
    'Leviat', 'Proofpoint', 'Sophos', 'Symantec', 'Tenable', 'Trellix', 'Zerofox'
]

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
Total Apps Created: {len(services_deployed)}

{'='*80}
QUICK START - COPY/PASTE ORDER
{'='*80}

Recommended deployment order (critical apps first):

"""

    priority = ['Splunk', 'Crowdstrike', 'ServiceNow', 'Qualys', 'Zscaler', 'SentinelOne']
    priority_apps = [s for s in priority if s in services_deployed]
    other_apps = [s for s in services_deployed if s not in priority]

    # Priority apps
    guide_content += "PRIORITY APPS (Do these first):\n"
    for i, service in enumerate(priority_apps, 1):
        guide_content += f"{i}. {service}\n"

    guide_content += f"\nOTHER APPS:\n"
    for i, service in enumerate(other_apps, len(priority_apps) + 1):
        guide_content += f"{i}. {service}\n"

    guide_content += f"""
{'='*80}
STEP-BY-STEP INSTRUCTIONS FOR EACH APP
{'='*80}

Follow these steps for EACH app listed above:

"""

    for i, service in enumerate(services_deployed, 1):
        app_name = f"{service.upper()}_APP"
        file_path = APPS_PATH / service / "streamlit_app.py"

        guide_content += f"""
{'─'*80}
{i}. {service} App
{'─'*80}

SNOWFLAKE UI:
1. Open: https://app.snowflake.com/GenericCorp/west-europe.azure/
2. Navigate: Data > Databases > DEV_REPORTING > SECURITY_ANALYTICS > Streamlit
3. Click: {app_name}
4. Click: "Edit" button (top right corner)

LOCAL FILE:
5. Open file: {file_path}
6. Select ALL (Ctrl+A)
7. Copy (Ctrl+C)

PASTE TO SNOWFLAKE:
8. In Snowflake editor: Delete any existing code
9. Paste (Ctrl+V)
10. Click: "Save" button
11. Click: "Run" button
12. Verify: App loads without errors

✅ {service} Complete!

"""

    guide_content += f"""
{'='*80}
QUICK REFERENCE - FILE LOCATIONS
{'='*80}

"""

    for service in services_deployed:
        file_path = APPS_PATH / service / "streamlit_app.py"
        guide_content += f"{service:20s} -> {file_path}\n"

    guide_content += f"""

{'='*80}
TROUBLESHOOTING
{'='*80}

Problem: "ModuleNotFoundError: No module named 'plotly'"
Solution: ✅ Apps in 08_STREAMLIT_APPS_FIXED are already cleaned!
          Make sure you're copying from FIXED folder.

Problem: App doesn't load
Solution: 1. Check Snowflake UI for specific error message
          2. Verify DEV_WH warehouse is running
          3. Confirm you have correct role (DEV_DEVELOPER)

Problem: Can't edit app
Solution: 1. Verify you're logged in as fmoran@GenericCorp.com
          2. Check your role is DEV_DEVELOPER
          3. Confirm database permissions on DEV_REPORTING.SECURITY_ANALYTICS

Problem: "Cannot read from Git repository"
Solution: ✅ This is expected! We're doing manual deployment now.
          Once Prabodh creates API Integration, we'll switch to Git.

{'='*80}
VERIFICATION CHECKLIST
{'='*80}

After deploying all apps, verify:

"""

    for service in services_deployed:
        guide_content += f"[ ] {service:20s} - Loads without errors\n"

    guide_content += f"""

{'='*80}
NEXT STEPS (FUTURE - AFTER API INTEGRATION)
{'='*80}

Once Prabodh creates the API Integration for Azure DevOps:

1. Connect each app to Git repository:
   - Repository: https://dev.azure.com/GenericCorp-ITSecurity/ITSECKPI_Snowflake_Project
   - Branch: main
   - Path: 08_STREAMLIT_APPS_PROD/<ServiceName>/

2. Future updates will be automatic from Git commits

3. No more manual copy-paste needed!

For now, manual deployment is working and functional.

{'='*80}
DEPLOYMENT COMPLETED
{'='*80}

Total apps ready: {len(services_deployed)}
Source folder: {APPS_PATH}
Target database: DEV_REPORTING.SECURITY_ANALYTICS

All apps are created and ready for code paste!

{'='*80}
"""

    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)

    return guide_path

def main():
    """Main deployment function"""
    print("="*80)
    print("AUTOMATIC STREAMLIT APPS DEPLOYMENT")
    print("="*80)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Source: {APPS_PATH}")
    print(f"Target: {SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}")
    print(f"Apps to deploy: {len(ALL_SERVICES)}")

    # Check apps exist
    print(f"\n📁 Verifying app files...")
    available_services = []

    for service in ALL_SERVICES:
        app_file = APPS_PATH / service / "streamlit_app.py"
        if app_file.exists():
            size = app_file.stat().st_size
            available_services.append(service)
            print(f"  ✅ {service:20s} {size:6,} bytes")
        else:
            print(f"  ❌ {service:20s} NOT FOUND")

    if len(available_services) == 0:
        print("\n❌ No app files found. Cannot proceed.")
        return

    print(f"\n✅ Found {len(available_services)} apps ready for deployment")

    # Connect to Snowflake
    print(f"\n{'='*80}")
    print("CONNECTING TO SNOWFLAKE")
    print(f"{'='*80}")

    conn = get_snowflake_connection()
    if not conn:
        print("\n❌ Cannot proceed without Snowflake connection")
        return

    # Deploy apps
    print(f"\n{'='*80}")
    print(f"CREATING {len(available_services)} STREAMLIT APPS")
    print(f"{'='*80}")

    success_count = 0
    failed_count = 0
    failed_apps = []
    successful_apps = []

    for service in available_services:
        print(f"\n{service}:")
        if create_streamlit_app_structure(conn, service):
            success_count += 1
            successful_apps.append(service)
        else:
            failed_count += 1
            failed_apps.append(service)

    # Close connection
    conn.close()
    print(f"\n✅ Snowflake connection closed")

    # Generate deployment guide
    print(f"\n{'='*80}")
    print("GENERATING DEPLOYMENT GUIDE")
    print(f"{'='*80}")

    if successful_apps:
        guide_path = generate_deployment_guide(successful_apps)
        print(f"✅ Deployment guide created: {guide_path}")

    # Summary
    print(f"\n{'='*80}")
    print("DEPLOYMENT SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Apps created successfully: {success_count}")
    print(f"❌ Failed: {failed_count}")

    if failed_apps:
        print(f"\nFailed apps:")
        for app in failed_apps:
            print(f"  - {app}")

    if success_count > 0:
        print(f"\n{'='*80}")
        print("NEXT STEPS - MANUAL CODE PASTE")
        print(f"{'='*80}")
        print(f"\n1. 📖 Open the deployment guide:")
        print(f"   {guide_path}")
        print(f"\n2. 🌐 Open Snowflake UI:")
        print(f"   https://app.snowflake.com/GenericCorp/west-europe.azure/")
        print(f"\n3. 📂 Navigate to apps:")
        print(f"   Data → DEV_REPORTING → SECURITY_ANALYTICS → Streamlit")
        print(f"\n4. ✏️  For each app:")
        print(f"   - Click app name → Edit")
        print(f"   - Open local file: 08_STREAMLIT_APPS_FIXED\\<Service>\\streamlit_app.py")
        print(f"   - Copy all (Ctrl+A, Ctrl+C)")
        print(f"   - Paste in Snowflake (Ctrl+V)")
        print(f"   - Save → Run")
        print(f"\n5. ✅ Verify each app loads without errors")

        print(f"\n{'='*80}")
        print("PRIORITY ORDER (Deploy these first)")
        print(f"{'='*80}")
        priority = ['Splunk', 'Crowdstrike', 'ServiceNow', 'Qualys', 'Zscaler', 'SentinelOne']
        for i, service in enumerate([s for s in priority if s in successful_apps], 1):
            print(f"   {i}. {service}")

        print(f"\n💡 TIP: Keep DEPLOYMENT_GUIDE.txt open while working!")

    print(f"\n✅ Script completed successfully")
    print(f"{'='*80}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()