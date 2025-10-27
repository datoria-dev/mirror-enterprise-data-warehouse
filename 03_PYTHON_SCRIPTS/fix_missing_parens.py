"""
Fix missing closing parentheses in Streamlit apps

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

def fix_set_page_config(content):
    """Fix st.set_page_config missing closing paren"""

    # Pattern: st.set_page_config( ... initial_sidebar_state="expanded" \n\n
    # Should be: st.set_page_config( ... initial_sidebar_state="expanded"\n)\n\n

    pattern = r'(st\.set_page_config\([^)]*initial_sidebar_state="[^"]+"\s*)\n(\n# )'
    replacement = r'\1\n)\n\2'

    content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)

    return content

def fix_multiselect(content):
    """Fix st.multiselect missing closing paren"""

    # Pattern: st.multiselect( ... help="..." \n    \n
    # Should be: st.multiselect( ... help="..."\n    )\n    \n

    pattern = r'(help="[^"]+"\s*)\n(\s+)(#|[a-z_])'
    replacement = r'\1\n\2)\n\2\3'

    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    return content

def fix_function_defs_before_unclosed(content):
    """Fix cases where function definitions appear after unclosed statements"""

    # Pattern: ... \n\ndef function
    # Add ) before the def

    lines = content.split('\n')
    fixed_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this is a function definition
        if line.startswith('def ') and i > 0:
            prev_line = fixed_lines[-1] if fixed_lines else ''

            # If previous line ends with a value and no closing paren
            if prev_line.strip() and not prev_line.strip().endswith(('),', ')', '}', ']')):
                # Check if it's part of a multiselect or other function call
                if 'key=' in prev_line or 'help=' in prev_line or 'default=' in prev_line:
                    # Add missing closing paren
                    print(f"    Adding ) before function definition at line {i+1}")
                    fixed_lines.append('    )')
                    fixed_lines.append('')

        fixed_lines.append(line)
        i += 1

    return '\n'.join(fixed_lines)

def fix_number_input(content):
    """Fix st.number_input missing closing paren"""

    # Find st.number_input with format parameter but no closing paren
    pattern = r'(st\.number_input\([^)]*format="[^"]+"\s*)\n(\s+)(["\'])'
    replacement = r'\1\n\2),\n\2\3'

    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    return content

def fix_app(service_name):
    """Fix missing parentheses in an app"""
    print(f"\n{service_name}:")

    app_file = APPS_PATH / service_name / "streamlit_app.py"

    if not app_file.exists():
        print(f"  ❌ File not found")
        return False

    try:
        # Read file
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()

        original_length = len(content)

        # Apply fixes
        print(f"  🔧 Fixing st.set_page_config...")
        content = fix_set_page_config(content)

        print(f"  🔧 Fixing st.multiselect...")
        content = fix_multiselect(content)

        print(f"  🔧 Fixing function definitions...")
        content = fix_function_defs_before_unclosed(content)

        print(f"  🔧 Fixing st.number_input...")
        content = fix_number_input(content)

        if len(content) != original_length:
            # Write back
            with open(app_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Fixed and saved")
            return True
        else:
            print(f"  ℹ️  No changes made")
            return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fix all apps"""
    print("="*80)
    print("FIXING MISSING CLOSING PARENTHESES")
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
        print(f"\n✅ All apps processed")
        print(f"   Re-run validation to check syntax")

if __name__ == "__main__":
    main()