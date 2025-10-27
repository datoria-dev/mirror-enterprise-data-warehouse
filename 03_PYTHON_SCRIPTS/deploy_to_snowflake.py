"""
Deploy Streamlit Apps to Snowflake - Full Automation
Uploads inlined Python files and creates Streamlit apps in Snowflake

This script completes the deployment by:
1. Creating a stage for Streamlit files
2. Uploading inlined Python files to the stage
3. Creating Streamlit apps pointing to the stage
4. Verifying deployment

Author: Data Engineering Team
Date: 2025-10-24
"""

import snowflake.connector
import os
import sys
from pathlib import Path
from datetime import datetime

# Force UTF-8 encoding for console output (Windows compatibility)
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# =====================================================================
# CONFIGURATION
# =====================================================================

SNOWFLAKE_CONFIG = {
    'account': 'GenericCorp-CRH_EDW',  # Or use: 'MW76572.east-us-2.azure'
    'user': 'FUAD.ONATE@CompanyX.COM',
    'authenticator': 'externalbrowser',  # SSO
    'warehouse': 'DEV_WH',
    'database': 'DEV_REPORTING',
    'schema': 'SECURITY_ANALYTICS',
    'role': 'DEV_DEVELOPER'
}

# Paths
BASE_PATH = Path(__file__).parent.parent
DEPLOYMENT_PATH = BASE_PATH / "DEPLOYMENT_OUTPUT"

# Services to deploy
SERVICES = [
    'Leviat', 'ServiceNow', 'CybelAngel', 'Proofpoint', 'SentinelOne', 'BitSight',  # Expanded apps
    'Ancon', 'Cisco_AMP', 'Crowdstrike', 'Intel_Threats', 'Qualys',  # Other apps
    'Sophos', 'Splunk', 'Symantec', 'Tenable', 'Trellix', 'Zerofox', 'Zscaler'
]

# =====================================================================
# DEPLOYMENT FUNCTIONS
# =====================================================================

def create_stage(cursor):
    """Create stage for Streamlit files if it doesn't exist"""
    print("\n" + "=" * 80)
    print("CREATING STAGE FOR STREAMLIT FILES")
    print("=" * 80)

    sql = f"""
CREATE STAGE IF NOT EXISTS {SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.STREAMLIT_STAGE
  DIRECTORY = (ENABLE = TRUE)
  COMMENT = 'Storage for SECURITY_ANALYTICS Streamlit validation apps'
"""

    try:
        cursor.execute(sql)
        print("✅ Stage created/verified: STREAMLIT_STAGE")
        return True
    except Exception as e:
        print(f"❌ Error creating stage: {e}")
        return False

def upload_file_to_stage(cursor, service_name, local_file_path):
    """Upload a Python file to Snowflake stage"""

    # Snowflake PUT command expects forward slashes even on Windows
    local_file_str = str(local_file_path).replace('\\', '/')

    # Target path in stage
    stage_path = f"@{SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.STREAMLIT_STAGE/{service_name}/"

    sql = f"""
PUT 'file://{local_file_str}' {stage_path}
AUTO_COMPRESS = FALSE
OVERWRITE = TRUE
"""

    try:
        print(f"📤 Uploading {service_name}/streamlit_app.py...")
        cursor.execute(sql)
        result = cursor.fetchall()

        # Check upload status
        if result and len(result) > 0:
            status = result[0][6] if len(result[0]) > 6 else 'UNKNOWN'
            if status == 'UPLOADED':
                print(f"   ✅ Uploaded successfully")
                return True
            else:
                print(f"   ⚠️  Upload status: {status}")
                return True  # Sometimes SKIPPED means already exists
        return True
    except Exception as e:
        print(f"   ❌ Upload failed: {e}")
        return False

def create_streamlit_app(cursor, service_name):
    """Create Streamlit app in Snowflake"""

    app_name = f"{service_name.upper()}_APP"

    # Get app description based on service
    descriptions = {
        'Leviat': 'IAM and identity management monitoring',
        'ServiceNow': 'ITSM tickets and incident tracking',
        'CybelAngel': 'External data leak and threat detection',
        'Proofpoint': 'Email security and phishing analysis',
        'SentinelOne': 'Endpoint protection and threat hunting',
        'BitSight': 'Security ratings and vendor risk',
        'Ancon': 'Security analytics and insights',
        'Cisco_AMP': 'Advanced malware protection',
        'Crowdstrike': 'EDR and threat intelligence',
        'Intel_Threats': 'Threat intelligence feeds',
        'Qualys': 'Vulnerability scanning and assessment',
        'Sophos': 'Endpoint protection platform',
        'Splunk': 'SIEM and security monitoring',
        'Symantec': 'Antivirus and endpoint security',
        'Tenable': 'Vulnerability management',
        'Trellix': 'EDR and endpoint protection',
        'Zerofox': 'Digital risk protection',
        'Zscaler': 'Cloud security and SASE'
    }

    description = descriptions.get(service_name, 'SECURITY_ANALYTICS validation dashboard')

    sql = f"""
CREATE OR REPLACE STREAMLIT {SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.{app_name}
  ROOT_LOCATION = '@{SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.STREAMLIT_STAGE/{service_name}'
  MAIN_FILE = 'streamlit_app_inlined.py'
  QUERY_WAREHOUSE = '{SNOWFLAKE_CONFIG['warehouse']}'
  COMMENT = 'SECURITY_ANALYTICS - {description}'
"""

    try:
        print(f"🚀 Creating Streamlit app: {app_name}...")
        cursor.execute(sql)
        print(f"   ✅ App created successfully")
        return True
    except Exception as e:
        print(f"   ❌ App creation failed: {e}")
        return False

def get_app_url(service_name):
    """Generate Snowflake UI URL for the app"""
    app_name = f"{service_name.upper()}_APP"
    return f"https://app.snowflake.com/GenericCorp/crh_edw/#/streamlit-apps/{SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.{app_name}"

def verify_deployment(cursor):
    """Verify all deployed apps"""
    print("\n" + "=" * 80)
    print("VERIFYING DEPLOYMENT")
    print("=" * 80)

    sql = f"""
SHOW STREAMLITS IN SCHEMA {SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}
"""

    try:
        cursor.execute(sql)
        apps = cursor.fetchall()

        print(f"\n✅ Found {len(apps)} Streamlit apps in {SNOWFLAKE_CONFIG['schema']}:")
        for app in apps:
            app_name = app[1]  # name column
            print(f"   • {app_name}")

        return True
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

# =====================================================================
# MAIN DEPLOYMENT
# =====================================================================

def deploy_all(services_filter=None):
    """Deploy all Streamlit apps to Snowflake"""

    print("=" * 80)
    print("STREAMLIT APPS DEPLOYMENT TO SNOWFLAKE")
    print("=" * 80)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}")

    # Filter services
    services_to_deploy = services_filter if services_filter else SERVICES
    print(f"\nServices to deploy: {len(services_to_deploy)}")

    # Connect to Snowflake
    print(f"\n{'=' * 80}")
    print("CONNECTING TO SNOWFLAKE")
    print(f"{'=' * 80}")
    print(f"Account: {SNOWFLAKE_CONFIG['account']}")
    print(f"User: {SNOWFLAKE_CONFIG['user']}")
    print(f"Database: {SNOWFLAKE_CONFIG['database']}")

    try:
        conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
        cursor = conn.cursor()
        print("✅ Connected successfully\n")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    # Create stage
    if not create_stage(cursor):
        print("❌ Failed to create stage. Aborting.")
        return

    # Deploy each service
    results = []
    success_count = 0
    failed_count = 0

    for service in services_to_deploy:
        print(f"\n{'=' * 80}")
        print(f"DEPLOYING: {service}")
        print(f"{'=' * 80}")

        # Check if inlined file exists
        inlined_file = DEPLOYMENT_PATH / f"{service}_streamlit_app_inlined.py"

        if not inlined_file.exists():
            print(f"❌ Inlined file not found: {inlined_file}")
            failed_count += 1
            results.append({'service': service, 'success': False, 'error': 'File not found'})
            continue

        # Upload file
        upload_success = upload_file_to_stage(cursor, service, inlined_file)

        if not upload_success:
            failed_count += 1
            results.append({'service': service, 'success': False, 'error': 'Upload failed'})
            continue

        # Create app
        app_success = create_streamlit_app(cursor, service)

        if app_success:
            success_count += 1
            url = get_app_url(service)
            print(f"   🔗 URL: {url}")
            results.append({'service': service, 'success': True, 'url': url})
        else:
            failed_count += 1
            results.append({'service': service, 'success': False, 'error': 'App creation failed'})

    # Verify
    verify_deployment(cursor)

    # Close connection
    cursor.close()
    conn.close()

    # Summary
    print(f"\n{'=' * 80}")
    print("DEPLOYMENT SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total Services: {len(services_to_deploy)}")
    print(f"✅ Successful:  {success_count}")
    print(f"❌ Failed:      {failed_count}")
    print(f"Success Rate:   {(success_count / len(services_to_deploy) * 100):.1f}%")

    # Print URLs
    if success_count > 0:
        print(f"\n{'=' * 80}")
        print("APP URLS")
        print(f"{'=' * 80}")
        for result in results:
            if result['success']:
                print(f"✅ {result['service']:15} {result['url']}")

    print(f"\n{'=' * 80}")
    print("DEPLOYMENT COMPLETE!")
    print(f"{'=' * 80}")

    return results

# =====================================================================
# MAIN EXECUTION
# =====================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Deploy Streamlit apps to Snowflake')
    parser.add_argument('--services', nargs='+', help='Specific services to deploy')
    parser.add_argument('--phase', type=int, choices=[1, 2, 3], help='Deploy by phase (1=critical, 2=expanded, 3=remaining)')

    args = parser.parse_args()

    # Phase-based deployment
    if args.phase == 1:
        services_filter = ['Splunk', 'Crowdstrike', 'ServiceNow', 'Qualys', 'Zscaler']
    elif args.phase == 2:
        services_filter = ['Leviat', 'Proofpoint', 'SentinelOne', 'CybelAngel', 'BitSight', 'Tenable']
    elif args.phase == 3:
        services_filter = ['Sophos', 'Trellix', 'Symantec', 'Cisco_AMP', 'Zerofox', 'Intel_Threats', 'Ancon']
    else:
        services_filter = args.services

    try:
        results = deploy_all(services_filter)

        # Exit code
        failed = sum(1 for r in results if not r['success'])
        sys.exit(1 if failed > 0 else 0)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
