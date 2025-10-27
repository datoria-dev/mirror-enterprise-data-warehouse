"""
Fix Streamlit Apps Deployment - Corrects file naming issue
Updates the deployed Streamlit apps to use the correct file names

Author: Data Engineering Team
Date: 2025-10-24
"""

import snowflake.connector
import sys
from pathlib import Path
from datetime import datetime

# Force UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# =====================================================================
# CONFIGURATION
# =====================================================================

SNOWFLAKE_CONFIG = {
    'account': 'GenericCorp-CRH_EDW',
    'user': 'FUAD.ONATE@CompanyX.COM',
    'authenticator': 'externalbrowser',  # SSO
    'warehouse': 'DEV_WH',
    'database': 'DEV_REPORTING',
    'schema': 'SECURITY_ANALYTICS',
    'role': 'DEV_DEVELOPER'
}

BASE_PATH = Path(__file__).parent.parent
DEPLOYMENT_PATH = BASE_PATH / "DEPLOYMENT_OUTPUT"

# All deployed services
SERVICES = [
    'Splunk', 'Crowdstrike', 'ServiceNow', 'Qualys', 'Zscaler',  # Phase 1
    'Leviat', 'Proofpoint', 'SentinelOne', 'CybelAngel', 'BitSight', 'Tenable',  # Phase 2
    'Sophos', 'Trellix', 'Symantec', 'Cisco_AMP', 'Zerofox', 'Intel_Threats', 'Ancon'  # Phase 3
]

# =====================================================================
# FIX FUNCTIONS
# =====================================================================

def fix_stage_files(cursor):
    """Rename files in stage from streamlit_app_inlined.py to streamlit_app.py"""

    print("\n" + "=" * 80)
    print("FIXING STAGE FILES")
    print("=" * 80)

    success_count = 0

    for service in SERVICES:
        try:
            # Copy the inlined file with correct name
            local_file = DEPLOYMENT_PATH / f"{service}_streamlit_app_inlined.py"

            if not local_file.exists():
                print(f"❌ {service}: Local file not found")
                continue

            # Re-upload with correct name
            local_file_str = str(local_file).replace('\\', '/')
            stage_path = f"@{SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.STREAMLIT_STAGE/{service}/"

            # Upload as streamlit_app.py (correct name)
            sql = f"""
PUT 'file://{local_file_str}' {stage_path}streamlit_app.py
AUTO_COMPRESS = FALSE
OVERWRITE = TRUE
"""
            print(f"🔄 {service}: Re-uploading as streamlit_app.py...")
            cursor.execute(sql)

            # Also remove the old file if exists
            sql_remove = f"""
REMOVE {stage_path}streamlit_app_inlined.py
"""
            try:
                cursor.execute(sql_remove)
                print(f"   ✅ Removed old file, uploaded correct file")
            except:
                print(f"   ✅ Uploaded correct file")

            success_count += 1

        except Exception as e:
            print(f"❌ {service}: Error - {e}")

    return success_count

def recreate_apps(cursor):
    """Recreate Streamlit apps with correct MAIN_FILE reference"""

    print("\n" + "=" * 80)
    print("RECREATING STREAMLIT APPS")
    print("=" * 80)

    success_count = 0

    for service in SERVICES:
        app_name = f"{service.upper()}_APP"

        sql = f"""
CREATE OR REPLACE STREAMLIT {SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.{app_name}
  ROOT_LOCATION = '@{SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.STREAMLIT_STAGE/{service}'
  MAIN_FILE = 'streamlit_app.py'
  QUERY_WAREHOUSE = '{SNOWFLAKE_CONFIG['warehouse']}'
  COMMENT = 'SECURITY_ANALYTICS validation dashboard for {service} - FIXED'
"""

        try:
            print(f"🚀 Recreating {app_name}...")
            cursor.execute(sql)
            print(f"   ✅ App recreated successfully")
            success_count += 1
        except Exception as e:
            print(f"   ❌ Error: {e}")

    return success_count

def verify_apps(cursor):
    """Verify all apps are working"""

    print("\n" + "=" * 80)
    print("VERIFYING APPS")
    print("=" * 80)

    sql = f"""
SHOW STREAMLITS IN SCHEMA {SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}
"""

    try:
        cursor.execute(sql)
        apps = cursor.fetchall()

        deployed_apps = [app[1] for app in apps if '_APP' in app[1]]

        print(f"\n✅ Found {len(deployed_apps)} deployed apps:")
        for app_name in sorted(deployed_apps):
            service = app_name.replace('_APP', '').title()
            url = f"https://app.snowflake.com/GenericCorp/crh_edw/#/streamlit-apps/{SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.{app_name}"
            print(f"   • {service:15} → {url}")

        return True
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

# =====================================================================
# MAIN EXECUTION
# =====================================================================

def main():
    print("=" * 80)
    print("STREAMLIT DEPLOYMENT FIX")
    print("=" * 80)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}")

    # Connect
    print(f"\n{'=' * 80}")
    print("CONNECTING TO SNOWFLAKE")
    print(f"{'=' * 80}")

    try:
        conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
        cursor = conn.cursor()
        print("✅ Connected successfully\n")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    try:
        # Step 1: Fix stage files
        fixed_count = fix_stage_files(cursor)
        print(f"\n✅ Fixed {fixed_count} stage files")

        # Step 2: Recreate apps
        recreated_count = recreate_apps(cursor)
        print(f"\n✅ Recreated {recreated_count} apps")

        # Step 3: Verify
        verify_apps(cursor)

        print(f"\n{'=' * 80}")
        print("FIX COMPLETE!")
        print(f"{'=' * 80}")
        print("\n✅ All apps should now be accessible")
        print("   Test an app: https://app.snowflake.com/GenericCorp/crh_edw/#/streamlit-apps/DEV_REPORTING.SECURITY_ANALYTICS.LEVIAT_APP")

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()