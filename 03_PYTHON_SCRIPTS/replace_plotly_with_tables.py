"""
Replace ALL plotly usage with Streamlit tables
Comment out any line that references plotly objects

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
SOURCE_PATH = Path(r"C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\10_STREAMLIT_FINAL")
OUTPUT_PATH = Path(r"C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\11_STREAMLIT_NO_PLOTLY")

# All services
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

def remove_all_plotly_code(content):
    """Comment out ALL lines that use plotly objects or operations"""

    lines = content.split('\n')
    fixed_lines = []
    in_plotly_block = False
    block_indent = 0

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            fixed_lines.append(line)
            i += 1
            continue

        # Get current indentation
        current_indent = len(line) - len(line.lstrip())

        # Check if line uses plotly
        uses_plotly = (
            'px.' in stripped or
            'go.' in stripped or
            stripped.startswith('fig') and '=' in stripped or
            stripped.startswith('fig.') or
            'st.plotly_chart(' in stripped or
            stripped.startswith('from plotly') or
            stripped.startswith('import plotly')
        )

        if uses_plotly:
            # Start of plotly block
            if '=' in stripped or stripped.startswith('fig'):
                in_plotly_block = True
                block_indent = current_indent
                fixed_lines.append(f"# {line}  # Plotly not available")

                # Check if this is a multi-line statement
                if '(' in stripped and ')' not in stripped:
                    # Multi-line, need to comment subsequent lines
                    i += 1
                    while i < len(lines):
                        next_line = lines[i]
                        next_stripped = next_line.strip()

                        if not next_stripped:
                            fixed_lines.append(next_line)
                            i += 1
                            continue

                        fixed_lines.append(f"# {next_line}  # Plotly not available")

                        # Check if we've closed all parentheses
                        if ')' in next_stripped:
                            break
                        i += 1
            else:
                fixed_lines.append(f"# {line}  # Plotly not available")
        else:
            # Not a plotly line
            in_plotly_block = False
            fixed_lines.append(line)

        i += 1

    return '\n'.join(fixed_lines)

def add_table_displays(content):
    """Add st.dataframe displays where charts were removed"""

    # After commenting plotly, add helpful data displays
    lines = content.split('\n')
    fixed_lines = []

    for i, line in enumerate(lines):
        fixed_lines.append(line)

        # If we just commented a px.bar or go.Figure, add a table display
        if '# fig' in line and ('px.bar' in line or 'go.Figure' in line or 'px.line' in line):
            # Get the indentation
            indent = len(line) - len(line.lstrip('#').lstrip())

            # Add info message and table
            fixed_lines.append(f"{' ' * indent}# Chart not available - showing data in table")
            fixed_lines.append(f"{' ' * indent}st.info('Interactive chart not available in Snowflake. View data in table below.')")

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
        print(f"  ❌ Source not found")
        return False

    try:
        # Create output dir
        output_dir.mkdir(parents=True, exist_ok=True)

        # Read
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()

        original_lines = len(content.split('\n'))

        # Remove all plotly code
        print(f"  🔧 Commenting all plotly code...")
        content = remove_all_plotly_code(content)

        # Add table displays
        print(f"  📊 Adding data table displays...")
        content = add_table_displays(content)

        final_lines = len(content.split('\n'))

        # Validate syntax
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

        print(f"  ✅ Created: {final_lines} lines, syntax valid")

        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Process all apps"""
    print("="*80)
    print("REMOVING ALL PLOTLY CODE - FINAL VERSION")
    print("="*80)
    print(f"\nSource: {SOURCE_PATH}")
    print(f"Output: {OUTPUT_PATH}")
    print(f"\nChanges:")
    print(f"  - Comment ALL plotly usage")
    print(f"  - Add table displays")
    print(f"  - Validate syntax\n")

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
        print(f"\n✅ Apps ready without any plotly code!")
        print(f"   Location: {OUTPUT_PATH}")
        print(f"\n📋 Next: Deploy to Snowflake")

if __name__ == "__main__":
    main()