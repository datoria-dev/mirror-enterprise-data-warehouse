"""
Create simplified environment.yml files for all Streamlit apps
Minimal and efficient - only essential libraries

Author: Data Engineering Team
Date: 2025-10-24
"""

import sys
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Paths
BASE_PATH = Path(r"C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV")
APPS_PATH = BASE_PATH / "08_STREAMLIT_APPS_FIXED"

# All services
ALL_SERVICES = [
    'Splunk', 'Crowdstrike', 'ServiceNow', 'Qualys', 'Zscaler', 'SentinelOne',
    'Ancon', 'BitSight', 'Cisco_AMP', 'CybelAngel', 'Intel_Threats',
    'Leviat', 'Proofpoint', 'Sophos', 'Symantec', 'Tenable', 'Trellix', 'Zerofox'
]

# Simplified environment.yml - only essentials
SIMPLE_ENVIRONMENT = """name: streamlit
channels:
  - snowflake
dependencies:
  - streamlit
  - snowflake-snowpark-python
  - pandas
"""

def create_simple_environment(service_name):
    """Create simplified environment.yml for a service"""

    service_dir = APPS_PATH / service_name
    if not service_dir.exists():
        print(f"  ❌ Directory not found")
        return False

    env_file = service_dir / "environment.yml"

    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(SIMPLE_ENVIRONMENT)

        print(f"  ✅ Created simple environment.yml")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Create simplified environment.yml for all apps"""
    print("="*80)
    print("CREATING SIMPLIFIED ENVIRONMENT.YML FILES")
    print("="*80)
    print("\nLibraries included:")
    print("  ✅ streamlit")
    print("  ✅ snowflake-snowpark-python")
    print("  ✅ pandas")
    print("\nNo comments, no extras - just what works!\n")

    success_count = 0
    failed_count = 0

    for service in ALL_SERVICES:
        print(f"{service}:")
        if create_simple_environment(service):
            success_count += 1
        else:
            failed_count += 1

    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Successfully created: {success_count}")
    print(f"❌ Failed: {failed_count}")

    if success_count > 0:
        print(f"\n✅ All environment.yml files simplified!")
        print(f"   Size: ~4 lines each (minimal)")
        print(f"   Location: {APPS_PATH}\\<Service>\\environment.yml")

if __name__ == "__main__":
    main()