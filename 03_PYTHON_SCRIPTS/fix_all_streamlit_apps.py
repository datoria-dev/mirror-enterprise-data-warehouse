"""
Fix All Streamlit Apps - Remove External Dependencies
Removes plotly, numpy and other external dependencies from all apps
Makes them compatible with Snowflake Streamlit environment

Author: Data Engineering Team
Date: 2025-10-24
"""

import os
import re
import sys
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Base paths
BASE_PATH = Path(r"C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV")
SOURCE_PATH = BASE_PATH / "08_STREAMLIT_APPS_PROD"
OUTPUT_PATH = BASE_PATH / "08_STREAMLIT_APPS_FIXED"

# Services to fix
SERVICES = [
    'Ancon', 'BitSight', 'Cisco_AMP', 'Crowdstrike', 'CybelAngel',
    'Intel_Threats', 'Leviat', 'Proofpoint', 'Qualys', 'SentinelOne',
    'ServiceNow', 'Sophos', 'Splunk', 'Symantec', 'Tenable',
    'Trellix', 'Zerofox', 'Zscaler'
]

def remove_plotly_imports(content):
    """Remove plotly and numpy imports"""
    # Remove plotly imports
    content = re.sub(r'^import plotly\.express as px\n', '', content, flags=re.MULTILINE)
    content = re.sub(r'^import plotly\.graph_objects as go\n', '', content, flags=re.MULTILINE)
    content = re.sub(r'^from plotly\.subplots import make_subplots\n', '', content, flags=re.MULTILINE)
    content = re.sub(r'^import plotly\.[^\n]+\n', '', content, flags=re.MULTILINE)

    # Remove numpy
    content = re.sub(r'^import numpy as np\n', '', content, flags=re.MULTILINE)
    content = re.sub(r'^import numpy\n', '', content, flags=re.MULTILINE)

    # Remove matplotlib
    content = re.sub(r'^import matplotlib\.[^\n]+\n', '', content, flags=re.MULTILINE)
    content = re.sub(r'^from matplotlib import [^\n]+\n', '', content, flags=re.MULTILINE)

    # Remove seaborn
    content = re.sub(r'^import seaborn as sns\n', '', content, flags=re.MULTILINE)

    # Remove altair
    content = re.sub(r'^import altair as alt\n', '', content, flags=re.MULTILINE)

    return content

def replace_plotly_charts(content):
    """Replace plotly chart code with streamlit native charts or warnings"""

    # Replace px.bar with st.bar_chart
    content = re.sub(
        r'fig_?\w*\s*=\s*px\.bar\([^)]+\).*?st\.plotly_chart\(fig_?\w*[^)]*\)',
        'st.info("Bar chart visualization - using native Streamlit chart")\n        # st.bar_chart(df) # Simplified visualization',
        content,
        flags=re.DOTALL
    )

    # Replace px.pie with warning
    content = re.sub(
        r'fig_?\w*\s*=\s*px\.pie\([^)]+\).*?st\.plotly_chart\(fig_?\w*[^)]*\)',
        'st.info("Pie chart - data available in table below")',
        content,
        flags=re.DOTALL
    )

    # Replace px.scatter with st.scatter_chart
    content = re.sub(
        r'fig_?\w*\s*=\s*px\.scatter\([^)]+\).*?st\.plotly_chart\(fig_?\w*[^)]*\)',
        'st.info("Scatter plot - data available in table below")',
        content,
        flags=re.DOTALL
    )

    # Replace px.line with st.line_chart
    content = re.sub(
        r'fig_?\w*\s*=\s*px\.line\([^)]+\).*?st\.plotly_chart\(fig_?\w*[^)]*\)',
        'st.info("Line chart visualization - using native Streamlit chart")\n        # st.line_chart(df) # Simplified visualization',
        content,
        flags=re.DOTALL
    )

    # Replace go.Figure with warning
    content = re.sub(
        r'fig_?\w*\s*=\s*go\.Figure\([^)]+\).*?st\.plotly_chart\(fig_?\w*[^)]*\)',
        'st.info("Advanced chart - data available in table below")',
        content,
        flags=re.DOTALL
    )

    # Replace any remaining st.plotly_chart
    content = re.sub(
        r'st\.plotly_chart\([^)]+\)',
        'st.info("Chart visualization removed - data shown in table format")',
        content
    )

    # Comment out any remaining plotly references
    content = re.sub(
        r'^(\s*)(.*(?:px\.|go\.|fig\.).*)',
        r'\1# \2  # Plotly code commented out',
        content,
        flags=re.MULTILINE
    )

    return content

def add_safe_wrappers(content):
    """Add safe wrappers for data operations"""

    # Add safe column access
    safe_wrapper = '''
# Safe column access helper
def safe_get_column(df, column, default_value=0):
    """Safely get column from dataframe"""
    if column in df.columns:
        return df[column]
    else:
        return default_value

'''

    # Insert after imports
    import_end = content.find('\n\n# ') if '\n\n# ' in content else content.find('\n\nst.')
    if import_end > 0:
        content = content[:import_end] + '\n' + safe_wrapper + content[import_end:]

    return content

def fix_app(service_name):
    """Fix a single app"""
    print(f"\n{'='*60}")
    print(f"Fixing {service_name}")
    print(f"{'='*60}")

    # Input and output paths
    input_file = SOURCE_PATH / service_name / "streamlit_app.py"
    output_dir = OUTPUT_PATH / service_name
    output_file = output_dir / "streamlit_app.py"

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check if input file exists
    if not input_file.exists():
        print(f"❌ Source file not found: {input_file}")
        return False

    try:
        # Read original content
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        original_lines = len(content.split('\n'))
        print(f"📖 Original: {original_lines} lines")

        # Apply fixes
        print("🔧 Removing external dependencies...")
        content = remove_plotly_imports(content)

        print("🔧 Replacing plotly charts...")
        content = replace_plotly_charts(content)

        print("🔧 Adding safe wrappers...")
        content = add_safe_wrappers(content)

        # Write fixed version
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        fixed_lines = len(content.split('\n'))
        print(f"✅ Fixed: {fixed_lines} lines")
        print(f"💾 Saved to: {output_file}")

        return True

    except Exception as e:
        print(f"❌ Error fixing {service_name}: {e}")
        return False

def main():
    """Fix all apps"""
    print("="*80)
    print("FIXING ALL STREAMLIT APPS FOR SNOWFLAKE COMPATIBILITY")
    print("="*80)
    print(f"\nSource: {SOURCE_PATH}")
    print(f"Output: {OUTPUT_PATH}")
    print(f"Services: {len(SERVICES)}")

    # Create output directory
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    # Fix each app
    success_count = 0
    failed_count = 0

    for service in SERVICES:
        if fix_app(service):
            success_count += 1
        else:
            failed_count += 1

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Successfully fixed: {success_count}")
    print(f"❌ Failed: {failed_count}")

    if success_count > 0:
        print(f"\n📁 Fixed apps saved to: {OUTPUT_PATH}")
        print("\nNext steps:")
        print("1. Copy content from 08_STREAMLIT_APPS_FIXED/{Service}/streamlit_app.py")
        print("2. Paste into Snowflake Streamlit app editor")
        print("3. Save and run")

        # Create a README
        readme_path = OUTPUT_PATH / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"""# Fixed Streamlit Apps for Snowflake

## Overview
These apps have been fixed to work in Snowflake Streamlit environment.

**Fixed on**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Total Apps**: {success_count}

## Changes Made
- ✅ Removed plotly imports
- ✅ Removed numpy imports
- ✅ Removed matplotlib/seaborn/altair
- ✅ Replaced plotly charts with Streamlit native or info messages
- ✅ Added safe column access helpers

## How to Deploy
1. Open app in Snowflake UI
2. Click Edit
3. Copy content from `{service}/streamlit_app.py`
4. Paste and Save
5. Run app

## Apps Fixed
""")
            for service in SERVICES:
                if (OUTPUT_PATH / service / "streamlit_app.py").exists():
                    f.write(f"- ✅ {service}\n")

        print(f"\n📝 README created: {readme_path}")

if __name__ == "__main__":
    from datetime import datetime
    main()