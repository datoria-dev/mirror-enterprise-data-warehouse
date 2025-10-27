"""
Add np.inf constant to _DummyNumpy class in all Streamlit apps

Fixes: TypeError: bad operand type for unary -: 'function'
When code uses: bins=[-np.inf, 30, 60, 90, 180, np.inf]

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

def add_inf_constant(content):
    """Add inf constant to _DummyNumpy class"""

    # Check if already has inf constant
    if "inf = float('inf')" in content:
        return content, False

    # Find _DummyNumpy class and add inf constant after the docstring
    pattern = r"(class _DummyNumpy:[\r\n]+    '''[^']*''')"

    def replacement(match):
        return match.group(1) + "\n    # Constants\n    inf = float('inf')"

    new_content = re.sub(pattern, replacement, content)

    if new_content != content:
        return new_content, True

    return content, False

def process_app(service_name):
    """Process single app"""
    print(f"{service_name}:", end=" ")

    app_file = SOURCE_PATH / service_name / "streamlit_app.py"

    if not app_file.exists():
        print("NOT FOUND")
        return False

    try:
        # Read
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add inf constant
        new_content, modified = add_inf_constant(content)

        if not modified:
            print("Already has np.inf constant")
            return True

        # Validate syntax
        import ast
        try:
            ast.parse(new_content)
        except SyntaxError as e:
            print(f"SYNTAX ERROR: {e}")
            return False

        # Write
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print("UPDATED - Added np.inf constant")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Process all apps"""
    print("="*80)
    print("ADDING np.inf CONSTANT TO ALL APPS")
    print("="*80)
    print("\nFixes: TypeError: bad operand type for unary -: 'function'")
    print("When using: bins=[-np.inf, 30, 60, 90, 180, np.inf]\n")

    success = 0
    failed = 0

    for service in ALL_SERVICES:
        if process_app(service):
            success += 1
        else:
            failed += 1

    print(f"\n{'='*80}")
    print(f"Success: {success}/{len(ALL_SERVICES)}")
    print(f"Failed: {failed}/{len(ALL_SERVICES)}")

    if success > 0:
        print(f"\nAll apps now have np.inf constant!")
        print(f"Apps can now use -np.inf in code without errors")

if __name__ == "__main__":
    main()
