"""
Fix indentation errors in all Streamlit apps
Removes orphaned lines from commented plotly code

Author: Data Engineering Team
Date: 2025-10-24
"""

import sys
import re
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

def fix_indentation_errors(content):
    """Fix common indentation errors from commented plotly code"""

    lines = content.split('\n')
    fixed_lines = []
    skip_next = False

    for i, line in enumerate(lines):
        # Skip if marked to skip
        if skip_next:
            skip_next = False
            continue

        # Check for orphaned lines after commented plotly code
        # Pattern: line starts with lots of spaces and contains plotly parameters
        if re.match(r'^\s{12,}(x=|y=|name=|marker_color=|text=|hovertemplate=|mode=|marker=|line=)', line):
            # This is likely an orphaned parameter line
            print(f"    Removing orphaned line: {line.strip()[:50]}...")
            continue

        # Check for standalone closing parenthesis or bracket with weird indentation
        if re.match(r'^\s{8,}\)[\s,]*$', line):
            # Check if previous line was a comment
            if i > 0 and '# Plotly code commented out' in lines[i-1]:
                print(f"    Removing orphaned closing paren")
                continue

        fixed_lines.append(line)

    return '\n'.join(fixed_lines)

def remove_empty_sections(content):
    """Remove sections that only have comments and no real code"""

    lines = content.split('\n')
    fixed_lines = []
    in_empty_section = False
    section_lines = []

    for line in lines:
        # Check if it's a plotly comment
        is_plotly_comment = '# Plotly code commented out' in line or '# fig' in line
        is_whitespace = line.strip() == ''

        if is_plotly_comment:
            # Start collecting potential empty section
            if not in_empty_section:
                in_empty_section = True
                section_lines = [line]
            else:
                section_lines.append(line)
        elif in_empty_section:
            if is_whitespace:
                section_lines.append(line)
            else:
                # Real code found, dump section and reset
                fixed_lines.extend(section_lines)
                fixed_lines.append(line)
                in_empty_section = False
                section_lines = []
        else:
            fixed_lines.append(line)

    # Don't add trailing empty sections

    return '\n'.join(fixed_lines)

def fix_app(service_name):
    """Fix indentation errors in a single app"""
    print(f"\n{service_name}:")

    app_file = APPS_PATH / service_name / "streamlit_app.py"

    if not app_file.exists():
        print(f"  ❌ File not found")
        return False

    try:
        # Read file
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()

        original_lines = len(content.split('\n'))

        # Fix indentation
        print(f"  🔧 Fixing indentation errors...")
        content = fix_indentation_errors(content)

        # Remove empty sections
        print(f"  🔧 Cleaning empty sections...")
        content = remove_empty_sections(content)

        fixed_lines = len(content.split('\n'))

        # Write back
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(content)

        if original_lines != fixed_lines:
            print(f"  ✅ Fixed: {original_lines} → {fixed_lines} lines (removed {original_lines - fixed_lines})")
        else:
            print(f"  ✅ No issues found ({original_lines} lines)")

        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Fix all apps"""
    print("="*80)
    print("FIXING INDENTATION ERRORS IN ALL STREAMLIT APPS")
    print("="*80)

    success_count = 0
    failed_count = 0

    for service in ALL_SERVICES:
        if fix_app(service):
            success_count += 1
        else:
            failed_count += 1

    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Successfully fixed: {success_count}")
    print(f"❌ Failed: {failed_count}")

    if success_count > 0:
        print(f"\n✅ All apps fixed and ready for deployment!")
        print(f"   Location: {APPS_PATH}")

if __name__ == "__main__":
    main()