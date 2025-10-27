"""
Remove matplotlib-dependent styling from Streamlit apps
Fixes: background_gradient, highlight_max, highlight_min, etc.

Author: Data Engineering Team
Date: 2025-10-25
"""

import sys
import re
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Paths
SOURCE_PATH = Path(r"C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\13_STREAMLIT_COMPLETE")
OUTPUT_PATH = Path(r"C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\14_STREAMLIT_NO_MATPLOTLIB")

ALL_SERVICES = [
    'Splunk', 'Crowdstrike', 'ServiceNow', 'Qualys', 'Zscaler', 'SentinelOne',
    'Ancon', 'BitSight', 'Cisco_AMP', 'CybelAngel', 'Intel_Threats',
    'Leviat', 'Proofpoint', 'Sophos', 'Symantec', 'Tenable', 'Trellix', 'Zerofox'
]

ENV_YML = """name: streamlit
channels:
  - snowflake
dependencies:
  - streamlit
  - snowflake-snowpark-python
  - pandas
"""

def remove_matplotlib_styling(content):
    """Remove all matplotlib-dependent styling methods"""

    # Pattern 1: .background_gradient(...)
    # Replace with plain dataframe
    content = re.sub(
        r'\.background_gradient\([^)]+\)',
        '',
        content
    )

    # Pattern 2: .highlight_max(...)
    content = re.sub(
        r'\.highlight_max\([^)]+\)',
        '',
        content
    )

    # Pattern 3: .highlight_min(...)
    content = re.sub(
        r'\.highlight_min\([^)]+\)',
        '',
        content
    )

    # Pattern 4: .bar(...)
    content = re.sub(
        r'\.bar\([^)]+\)',
        '',
        content
    )

    # Pattern 5: Remove trailing commas after style removal
    content = re.sub(
        r'\}\)\s*,\s*\n\s*use_container_width',
        '}),\n            use_container_width',
        content
    )

    return content

def process_app(service_name):
    """Process single app"""
    print(f"\n{service_name}:")

    source_file = SOURCE_PATH / service_name / "streamlit_app.py"
    output_dir = OUTPUT_PATH / service_name
    output_file = output_dir / "streamlit_app.py"
    env_file = output_dir / "environment.yml"

    if not source_file.exists():
        print(f"  ❌ Not found")
        return False

    try:
        output_dir.mkdir(parents=True, exist_ok=True)

        # Read
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content

        # Remove matplotlib styling
        print(f"  🔧 Removing matplotlib-dependent styling...")
        content = remove_matplotlib_styling(content)

        if content != original:
            changes = original.count('.background_gradient') + original.count('.highlight_max') + original.count('.highlight_min')
            print(f"     Removed {changes} styling calls")

        # Validate
        import ast
        try:
            ast.parse(content)
        except SyntaxError as e:
            print(f"  ❌ Syntax error: {e}")
            return False

        # Write
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(ENV_YML)

        lines = len(content.split('\n'))
        print(f"  ✅ Created: {lines} lines, syntax valid")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Process all apps"""
    print("="*80)
    print("REMOVING MATPLOTLIB-DEPENDENT STYLING")
    print("="*80)
    print(f"\nRemoving:")
    print(f"  - .background_gradient()")
    print(f"  - .highlight_max()")
    print(f"  - .highlight_min()")
    print(f"  - .bar()\n")

    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    success = 0
    failed = 0

    for service in ALL_SERVICES:
        if process_app(service):
            success += 1
        else:
            failed += 1

    print(f"\n{'='*80}")
    print(f"✅ Success: {success}")
    print(f"❌ Failed: {failed}")

    if success > 0:
        print(f"\n✅ Apps ready in: {OUTPUT_PATH}")
        print(f"\nDataframes will display without styling")
        print(f"but all data will be visible!")

if __name__ == "__main__":
    main()