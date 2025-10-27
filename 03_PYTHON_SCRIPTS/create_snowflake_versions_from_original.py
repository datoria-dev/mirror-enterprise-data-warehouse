"""
Create Snowflake-compatible versions from original apps
Simple approach: comment plotly imports and replace charts with messages

Author: Data Engineering Team
Date: 2025-10-24
"""

import sys
import re
import shutil
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Paths
BASE_PATH = Path(r"C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV")
SOURCE_PATH = Path(r"C:\Users\fonat\OneDrive\Documents\GenericCorp\Snowflake_ITSECKPI_Project_DEV\07_STREAMLIT_APPS")
OUTPUT_PATH = BASE_PATH / "09_STREAMLIT_APPS_CLEAN"

# Services to process
ALL_SERVICES = [
    'Splunk', 'Crowdstrike', 'ServiceNow', 'Qualys', 'Zscaler', 'SentinelOne',
    'Ancon', 'BitSight', 'Cisco_AMP', 'CybelAngel', 'Intel_Threats',
    'Leviat', 'Proofpoint', 'Sophos', 'Symantec', 'Tenable', 'Trellix', 'Zerofox'
]

def make_snowflake_compatible(content):
    """Make code Snowflake compatible - minimal changes"""

    # Step 1: Comment out plotly imports
    content = re.sub(
        r'^import plotly\..*$',
        r'# \g<0>  # Not available in Snowflake',
        content,
        flags=re.MULTILINE
    )

    # Step 2: Comment out numpy imports
    content = re.sub(
        r'^import numpy.*$',
        r'# \g<0>  # Not available in Snowflake',
        content,
        flags=re.MULTILINE
    )

    # Step 3: Replace st.plotly_chart() with info message
    content = re.sub(
        r'st\.plotly_chart\([^,]+,\s*use_container_width=True\)',
        'st.info("Interactive chart not available in Snowflake - view data in table below")',
        content
    )

    # Step 4: Comment out fig = go.Figure() lines
    content = re.sub(
        r'^(\s*)fig.*=.*go\.Figure\(',
        r'\1# fig = go.Figure(  # Plotly not available',
        content,
        flags=re.MULTILINE
    )

    #Step 5: Comment out fig.add_trace lines
    content = re.sub(
        r'^(\s*)fig.*\.add_trace\(',
        r'\1# fig.add_trace(  # Plotly not available',
        content,
        flags=re.MULTILINE
    )

    # Step 6: Comment out fig.update_layout lines
    content = re.sub(
        r'^(\s*)fig.*\.update_layout\(',
        r'\1# fig.update_layout(  # Plotly not available',
        content,
        flags=re.MULTILINE
    )

    # Step 7: Comment out fig.update_xaxes/yaxes lines
    content = re.sub(
        r'^(\s*)fig.*\.update_(x|y)axes\(',
        r'\1# fig.update_\2axes(  # Plotly not available',
        content,
        flags=re.MULTILINE
    )

    return content

def create_simple_environment_yml():
    """Create simple environment.yml"""
    return"""name: streamlit
channels:
  - snowflake
dependencies:
  - streamlit
  - snowflake-snowpark-python
  - pandas
"""

def process_app(service_name):
    """Process a single app"""
    print(f"\n{service_name}:")

    # Source
    source_dir = SOURCE_PATH / service_name
    source_file = source_dir / "streamlit_app.py"

    # Output
    output_dir = OUTPUT_PATH / service_name
    output_file = output_dir / "streamlit_app.py"
    env_file = output_dir / "environment.yml"

    if not source_file.exists():
        print(f"  ❌ Source not found: {source_file}")
        return False

    try:
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Read original
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()

        original_lines = len(content.split('\n'))

        # Make Snowflake compatible
        print(f"  🔧 Making Snowflake compatible...")
        content = make_snowflake_compatible(content)

        final_lines = len(content.split('\n'))

        # Write app file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        # Write environment.yml
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(create_simple_environment_yml())

        print(f"  ✅ Created: {final_lines} lines")
        print(f"     App: {output_file.name}")
        print(f"     Env: {env_file.name}")

        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Process all apps"""
    print("="*80)
    print("CREATING SNOWFLAKE-COMPATIBLE VERSIONS FROM ORIGINALS")
    print("="*80)
    print(f"\nSource: {SOURCE_PATH}")
    print(f"Output: {OUTPUT_PATH}")
    print(f"\nStrategy:")
    print("  1. Copy original files")
    print("  2. Comment plotly imports")
    print("  3. Replace st.plotly_chart() with info messages")
    print("  4. Comment fig.* operations")
    print("  5. Keep ALL other code intact\n")

    # Create output directory
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    success_count = 0
    failed_count = 0

    for service in ALL_SERVICES:
        if process_app(service):
            success_count += 1
        else:
            failed_count += 1

    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Successfully created: {success_count}")
    print(f"❌ Failed: {failed_count}")

    if success_count > 0:
        print(f"\n✅ Snowflake-compatible apps created!")
        print(f"   Location: {OUTPUT_PATH}")
        print(f"\n   Each app contains:")
        print(f"     - streamlit_app.py (Snowflake compatible)")
        print(f"     - environment.yml (minimal)")

if __name__ == "__main__":
    main()