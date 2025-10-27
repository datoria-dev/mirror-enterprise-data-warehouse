"""
Remove ALL .background_gradient() calls from Streamlit apps

Fixes: ImportError: background_gradient requires matplotlib

Author: Data Engineering Team
Date: 2025-10-25
"""

import sys
import re
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

SOURCE_PATH = Path(r"C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\13_STREAMLIT_COMPLETE")

ALL_SERVICES = [
    'Ancon', 'BitSight', 'Cisco_AMP', 'Crowdstrike', 'CybelAngel', 'Intel_Threats',
    'Leviat', 'Proofpoint', 'Qualys', 'SentinelOne', 'ServiceNow', 'Sophos',
    'Splunk', 'Symantec', 'Tenable', 'Trellix', 'Zerofox', 'Zscaler'
]

def remove_background_gradient(content):
    """Remove .background_gradient() calls"""

    original = content
    modifications = []

    # Pattern 1: .background_gradient(...),
    # Replace with ),  # background_gradient removed
    pattern1 = r'\.background_gradient\([^)]*\),(\s*)'
    def replacement1(match):
        modifications.append(f"Removed .background_gradient(...),")
        return f'),  # background_gradient removed - requires matplotlib{match.group(1)}'

    content = re.sub(pattern1, replacement1, content)

    # Pattern 2: .style.background_gradient(...) at end of chain
    # Replace with .style
    pattern2 = r'\.style\.background_gradient\([^)]*\)(\s*[,\)])'
    def replacement2(match):
        modifications.append(f"Removed .style.background_gradient(...)")
        return f'.style  # background_gradient removed - requires matplotlib{match.group(1)}'

    content = re.sub(pattern2, replacement2, content)

    # Pattern 3: Multiple chained .background_gradient() calls
    # Remove all instances
    while '.background_gradient(' in content and content != original:
        original = content
        content = re.sub(r'\.background_gradient\([^)]*\)', '', content)
        modifications.append("Removed chained .background_gradient()")

    return content, modifications

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
            print("  ✅ No background_gradient found")
            return True

        # Count occurrences
        count = content.count('.background_gradient(')
        print(f"  🔧 Found {count} .background_gradient() call(s)")

        # Remove
        new_content, modifications = remove_background_gradient(content)

        # Validate syntax
        import ast
        try:
            ast.parse(new_content)
        except SyntaxError as e:
            print(f"  ❌ SYNTAX ERROR: {e}")
            return False

        # Write
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"  ✅ Removed {count} instances")
        for mod in set(modifications[:3]):  # Show first 3 unique modifications
            print(f"     - {mod}")

        return True

    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Process all apps"""
    print("="*80)
    print("REMOVING ALL .background_gradient() CALLS")
    print("="*80)
    print("\nFixes: ImportError: background_gradient requires matplotlib")
    print("Matplotlib is not available in Snowflake Streamlit\n")

    success = 0
    failed = 0
    modified = 0

    for service in ALL_SERVICES:
        app_file = SOURCE_PATH / service / "streamlit_app.py"
        if app_file.exists():
            with open(app_file, 'r', encoding='utf-8') as f:
                if '.background_gradient(' in f.read():
                    modified += 1

        if process_app(service):
            success += 1
        else:
            failed += 1

    print(f"\n{'='*80}")
    print(f"✅ Success: {success}/{len(ALL_SERVICES)}")
    print(f"❌ Failed: {failed}/{len(ALL_SERVICES)}")
    print(f"🔧 Modified: {modified} apps")

    if success > 0:
        print(f"\n✅ All .background_gradient() calls removed!")
        print(f"   Apps will now work in Snowflake without matplotlib")

if __name__ == "__main__":
    main()
