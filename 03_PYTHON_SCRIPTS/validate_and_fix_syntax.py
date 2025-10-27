"""
Validate Python syntax and fix common errors in Streamlit apps

Author: Data Engineering Team
Date: 2025-10-24
"""

import sys
import ast
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

def validate_syntax(content, filename):
    """Validate Python syntax"""
    try:
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, e

def fix_common_errors(content):
    """Fix common syntax errors"""

    # Fix 1: st.set_page_config missing closing paren
    content = re.sub(
        r'(st\.set_page_config\([^)]+)\n\n(# CSS|# Page|# Get)',
        r'\1)\n\n\2',
        content,
        flags=re.MULTILINE
    )

    # Fix 2: Remove standalone )) or )
    lines = content.split('\n')
    fixed_lines = []
    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip lines that are ONLY closing parens
        if stripped in [')', '))', ')))', '))))', ')))))']:
            # Check context - if previous line is not a real code line, skip
            if i > 0 and (not fixed_lines or fixed_lines[-1].strip().startswith('#') or fixed_lines[-1].strip() == ''):
                print(f"    Skipping orphaned: {stripped}")
                continue

        fixed_lines.append(line)

    content = '\n'.join(fixed_lines)

    # Fix 3: Remove unmatched closing parens at end of blocks
    content = re.sub(r'\n\s+\)\s*\n(#|\n)', r'\n\1', content)

    return content

def validate_and_fix_app(service_name):
    """Validate and fix syntax errors in an app"""
    print(f"\n{service_name}:")

    app_file = APPS_PATH / service_name / "streamlit_app.py"

    if not app_file.exists():
        print(f"  ❌ File not found")
        return False

    try:
        # Read file
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Initial validation
        valid, error = validate_syntax(content, str(app_file))

        if valid:
            print(f"  ✅ Syntax valid")
            return True

        print(f"  ❌ Syntax error: {error.msg} at line {error.lineno}")

        # Try to fix
        print(f"  🔧 Attempting to fix...")
        original_content = content
        content = fix_common_errors(content)

        # Validate again
        valid, error = validate_syntax(content, str(app_file))

        if valid:
            # Save fixed version
            with open(app_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Fixed and saved")
            return True
        else:
            print(f"  ❌ Still has errors: {error.msg} at line {error.lineno}")
            print(f"  📝 Manual fix needed")

            # Show context around error
            lines = content.split('\n')
            start = max(0, error.lineno - 3)
            end = min(len(lines), error.lineno + 2)

            print(f"\n  Context (lines {start+1}-{end+1}):")
            for i in range(start, end):
                marker = "  >>>" if i == error.lineno - 1 else "     "
                print(f"{marker} {i+1:4d}: {lines[i]}")

            return False

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Validate and fix all apps"""
    print("="*80)
    print("VALIDATING AND FIXING PYTHON SYNTAX")
    print("="*80)

    success_count = 0
    failed_count = 0
    failed_apps = []

    for service in ALL_SERVICES:
        if validate_and_fix_app(service):
            success_count += 1
        else:
            failed_count += 1
            failed_apps.append(service)

    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Valid syntax: {success_count}")
    print(f"❌ Invalid syntax: {failed_count}")

    if failed_apps:
        print(f"\nApps with syntax errors:")
        for app in failed_apps:
            print(f"  - {app}")
        print(f"\nThese apps need manual review.")
    else:
        print(f"\n✅ All apps have valid Python syntax!")

if __name__ == "__main__":
    main()