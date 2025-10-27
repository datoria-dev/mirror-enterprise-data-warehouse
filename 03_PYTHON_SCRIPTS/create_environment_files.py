"""
Create environment.yml files for all Streamlit apps
Uses only Snowflake-supported libraries

Author: Data Engineering Team
Date: 2025-10-24
"""

import sys
from pathlib import Path
from datetime import datetime

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

# Environment.yml content optimized for Snowflake Streamlit
ENVIRONMENT_TEMPLATE = """# Snowflake Streamlit Environment for {service_name}
# Only includes libraries that are supported in Snowflake Streamlit
# Generated: {timestamp}

name: streamlit
channels:
  - snowflake

dependencies:
  # Core Streamlit - REQUIRED
  - streamlit

  # Snowflake connector - REQUIRED
  - snowflake-snowpark-python

  # Data manipulation - SUPPORTED
  - pandas

  # Additional supported libraries (optional)
  # Uncomment if needed:
  # - altair  # Alternative charts (may work in some environments)
  # - pillow  # Image processing
  # - pyarrow  # Fast data processing

# IMPORTANT NOTES:
# ================
# Snowflake Streamlit has LIMITED library support compared to local Streamlit.
#
# ❌ NOT SUPPORTED (do not add):
#   - plotly (interactive charts)
#   - matplotlib (static charts)
#   - seaborn (statistical visualization)
#   - numpy (numerical computing)
#   - scipy (scientific computing)
#   - scikit-learn (machine learning)
#   - tensorflow, pytorch (deep learning)
#
# ✅ SUPPORTED (can use):
#   - streamlit (native charts: st.bar_chart, st.line_chart, st.area_chart)
#   - pandas (data manipulation)
#   - snowflake-snowpark-python (database queries)
#   - altair (MAY work - test first)
#   - pillow (image processing)
#   - pyarrow (data processing)
#
# For visualization, use Streamlit's native charting:
#   - st.bar_chart(data)
#   - st.line_chart(data)
#   - st.area_chart(data)
#   - st.scatter_chart(data)
#   - st.map(data)
#   - st.dataframe(data)
#   - st.metric(label, value, delta)
#
# Current app uses only: streamlit, pandas, snowflake-snowpark-python
"""

def create_environment_file(service_name):
    """Create environment.yml for a service"""

    # Create service directory if it doesn't exist
    service_dir = APPS_PATH / service_name
    if not service_dir.exists():
        print(f"  ❌ Directory not found: {service_dir}")
        return False

    # Create environment.yml
    env_file = service_dir / "environment.yml"

    content = ENVIRONMENT_TEMPLATE.format(
        service_name=service_name,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✅ Created: {env_file.name}")
        return True

    except Exception as e:
        print(f"  ❌ Failed to create {env_file}: {e}")
        return False

def main():
    """Create environment.yml for all apps"""
    print("="*80)
    print("CREATING ENVIRONMENT.YML FILES FOR ALL STREAMLIT APPS")
    print("="*80)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {APPS_PATH}")
    print(f"Total Apps: {len(ALL_SERVICES)}")

    print(f"\n{'='*80}")
    print("CREATING ENVIRONMENT FILES")
    print(f"{'='*80}")

    success_count = 0
    failed_count = 0

    for service in ALL_SERVICES:
        print(f"\n{service}:")
        if create_environment_file(service):
            success_count += 1
        else:
            failed_count += 1

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Successfully created: {success_count}")
    print(f"❌ Failed: {failed_count}")

    if success_count > 0:
        print(f"\n{'='*80}")
        print("ENVIRONMENT FILES CREATED")
        print(f"{'='*80}")
        print(f"\nLocation: {APPS_PATH}\\<ServiceName>\\environment.yml")

        print(f"\n📋 Libraries included:")
        print(f"   ✅ streamlit (required)")
        print(f"   ✅ snowflake-snowpark-python (required)")
        print(f"   ✅ pandas (supported)")

        print(f"\n❌ Libraries NOT included (not supported by Snowflake):")
        print(f"   ❌ plotly")
        print(f"   ❌ matplotlib")
        print(f"   ❌ seaborn")
        print(f"   ❌ numpy")
        print(f"   ❌ scipy")

        print(f"\n💡 IMPORTANT:")
        print(f"   These environment.yml files are for FUTURE use with Git integration.")
        print(f"   For now, manual deployment doesn't require environment.yml.")
        print(f"   Once API Integration is set up, these files will be used automatically.")

        print(f"\n📁 Each app directory now contains:")
        print(f"   ├── streamlit_app.py (ready for deployment)")
        print(f"   └── environment.yml (for future Git integration)")

    print(f"\n✅ Script completed successfully")
    print(f"{'='*80}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()