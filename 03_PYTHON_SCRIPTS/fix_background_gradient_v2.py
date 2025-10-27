"""
Remove .background_gradient() calls - Version 2 (Better handling)

Author: Data Engineering Team
Date: 2025-10-25
"""

import sys
import re
from pathlib import Path

# Fix encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

SOURCE_PATH = Path(r"C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\13_STREAMLIT_COMPLETE")

ALL_SERVICES = [
    'BitSight', 'Cisco_AMP', 'CybelAngel', 'Intel_Threats',
    'Leviat', 'Proofpoint', 'Qualys', 'SentinelOne', 'ServiceNow',
    'Sophos', 'Zerofox', 'Zscaler'
]

def fix_background_gradient(content):
    """
    Remove .background_gradient() calls
    Handles patterns like:
    - df.style.background_gradient(subset=['COL'], cmap='Reds'),
    - df.style.format({...}).background_gradient(...)
    """

    # Pattern: .style.background_gradient(...) followed by comma or parenthesis
    # Replace with just .style
    pattern = r'\.style\.background_gradient\([^)]*\)'

    new_content = re.sub(pattern, '.style', content)

    # Pattern 2: .background_gradient(...) in a chain (after .style.format())
    # Replace with nothing (remove the call)
    pattern2 = r'\.background_gradient\([^)]*\)'

    new_content = re.sub(pattern2, '', new_content)

    return new_content

def process_app(service_name):
    """Process single app"""
    print(f"\n{service_name}:")

    app_file = SOURCE_PATH / service_name / "streamlit_app.py"

    if not app_file.exists():
        print("  NOT FOUND")
        return False

    try:
        # Read
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if has background_gradient
        if '.background_gradient(' not in content:
            print("  ✅ Already clean")
            return True

        # Count
        count = content.count('.background_gradient(')
        print(f"  🔧 Found {count} instance(s)")

        # Fix
        new_content = fix_background_gradient(content)

        # Verify it's removed
        remaining = new_content.count('.background_gradient(')
        if remaining > 0:
            print(f"  ⚠️ Warning: {remaining} instances still remain")

        # Validate syntax
        import ast
        try:
            ast.parse(new_content)
        except SyntaxError as e:
            print(f"  ❌ SYNTAX ERROR: {e}")
            # Show the problematic line
            lines = new_content.split('\n')
            if hasattr(e, 'lineno') and e.lineno:
                print(f"     Line {e.lineno}: {lines[e.lineno-1] if e.lineno-1 < len(lines) else 'N/A'}")
            return False

        # Write
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"  ✅ Fixed - removed {count} instance(s)")
        return True

    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False

def main():
    """Process all apps with background_gradient issues"""
    print("="*80)
    print("FIXING .background_gradient() CALLS - V2")
    print("="*80)

    success = 0
    failed = 0

    for service in ALL_SERVICES:
        if process_app(service):
            success += 1
        else:
            failed += 1

    print(f"\n{'='*80}")
    print(f"✅ Success: {success}/{len(ALL_SERVICES)}")
    print(f"❌ Failed: {failed}/{len(ALL_SERVICES)}")

if __name__ == "__main__":
    main()
