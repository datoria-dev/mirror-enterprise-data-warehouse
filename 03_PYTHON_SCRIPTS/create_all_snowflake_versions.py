"""
Create Snowflake versions for ALL apps
ONLY comments imports - no other changes

Author: Data Engineering Team
Date: 2025-10-24
"""

import sys
import ast
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Paths
SOURCE_PATH = Path(r"C:\Users\fonat\OneDrive\Documents\GenericCorp\Snowflake_ITSECKPI_Project_DEV\07_STREAMLIT_APPS")
OUTPUT_PATH = Path(r"C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\10_STREAMLIT_FINAL")

# All services
ALL_SERVICES = [
    'Splunk', 'Crowdstrike', 'ServiceNow', 'Qualys', 'Zscaler', 'SentinelOne',
    'Ancon', 'BitSight', 'Cisco_AMP', 'CybelAngel', 'Intel_Threats',
    'Leviat', 'Proofpoint', 'Sophos', 'Symantec', 'Tenable', 'Trellix', 'Zerofox'
]

ENV_YML_CONTENT = """name: streamlit
channels:
  - snowflake
dependencies:
  - streamlit
  - snowflake-snowpark-python
  - pandas
"""

def comment_imports_only(content):
    """Comment ONLY the import lines that cause problems"""

    lines = content.split('\n')
    fixed_lines = []

    for line in lines:
        # Check if this is an import line we need to comment
        if line.strip().startswith('import plotly'):
            fixed_lines.append(f"# {line}  # Not available in Snowflake")
        elif line.strip().startswith('from plotly'):
            fixed_lines.append(f"# {line}  # Not available in Snowflake")
        elif line.strip().startswith('import numpy'):
            fixed_lines.append(f"# {line}  # Not available in Snowflake")
        elif line.strip().startswith('from numpy'):
            fixed_lines.append(f"# {line}  # Not available in Snowflake")
        elif line.strip().startswith('import matplotlib'):
            fixed_lines.append(f"# {line}  # Not available in Snowflake")
        elif line.strip().startswith('from matplotlib'):
            fixed_lines.append(f"# {line}  # Not available in Snowflake")
        elif line.strip().startswith('import seaborn'):
            fixed_lines.append(f"# {line}  # Not available in Snowflake")
        else:
            # Keep line exactly as is
            fixed_lines.append(line)

    return '\n'.join(fixed_lines)

def process_app(service_name):
    """Process a single app"""
    print(f"\n{service_name}:")

    # Paths
    source_file = SOURCE_PATH / service_name / "streamlit_app.py"
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

        # Comment imports only
        content = comment_imports_only(content)

        # Validate syntax
        try:
            ast.parse(content)
        except SyntaxError as e:
            print(f"  ❌ Syntax error after processing: {e}")
            return False

        # Write app file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        # Write environment.yml
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(ENV_YML_CONTENT)

        print(f"  ✅ Created: {original_lines} lines, syntax valid")

        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Process all apps"""
    print("="*80)
    print("CREATING SNOWFLAKE VERSIONS FOR ALL 18 APPS")
    print("="*80)
    print(f"\nSource: {SOURCE_PATH}")
    print(f"Output: {OUTPUT_PATH}")
    print(f"\nChanges: ONLY comment plotly/numpy imports")
    print(f"Everything else: UNCHANGED\n")

    # Create output directory
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    success_count = 0
    failed_count = 0
    failed_apps = []

    for service in ALL_SERVICES:
        if process_app(service):
            success_count += 1
        else:
            failed_count += 1
            failed_apps.append(service)

    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Successfully created: {success_count}")
    print(f"❌ Failed: {failed_count}")

    if failed_apps:
        print(f"\nFailed apps:")
        for app in failed_apps:
            print(f"  - {app}")

    if success_count > 0:
        print(f"\n✅ Snowflake-compatible apps ready!")
        print(f"   Location: {OUTPUT_PATH}")
        print(f"\n   Each app contains:")
        print(f"     - streamlit_app.py (imports commented)")
        print(f"     - environment.yml (minimal)")
        print(f"\n📋 Next step:")
        print(f"   Deploy to Snowflake by copying each streamlit_app.py")

if __name__ == "__main__":
    main()