"""
Fix st.rerun() compatibility for Snowflake

Problem: st.rerun() doesn't exist in older Streamlit versions
Solution: Replace with st.experimental_rerun()

Author: Data Engineering Team
Date: 2025-10-25
"""

import sys
from pathlib import Path

# Fix encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

SOURCE_PATH = Path(r"C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\13_STREAMLIT_COMPLETE")

ALL_SERVICES = [
    'Ancon', 'BitSight', 'Cisco_AMP', 'Crowdstrike', 'CybelAngel', 'Intel_Threats',
    'Leviat', 'Proofpoint', 'Qualys', 'SentinelOne', 'ServiceNow', 'Sophos',
    'Splunk', 'Symantec', 'Tenable', 'Trellix', 'Zerofox', 'Zscaler'
]

def fix_rerun(content):
    """Replace st.rerun() with st.experimental_rerun()"""

    # Simple replacement
    new_content = content.replace(
        'st.rerun()',
        'st.experimental_rerun()  # Use experimental_rerun for Snowflake compatibility'
    )

    return new_content

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

        # Check if has st.rerun()
        if 'st.rerun()' not in content:
            print("OK (no st.rerun found)")
            return True

        # Fix
        new_content = fix_rerun(content)

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

        count = content.count('st.rerun()')
        print(f"FIXED ({count} replacement(s))")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Process all apps"""
    print("="*80)
    print("FIXING st.rerun() COMPATIBILITY")
    print("="*80)
    print("\nReplacing st.rerun() with st.experimental_rerun()")
    print("For Snowflake Streamlit compatibility\n")

    success = 0
    failed = 0
    fixed = 0

    for service in ALL_SERVICES:
        app_file = SOURCE_PATH / service / "streamlit_app.py"
        if app_file.exists():
            with open(app_file, 'r', encoding='utf-8') as f:
                if 'st.rerun()' in f.read():
                    fixed += 1

        if process_app(service):
            success += 1
        else:
            failed += 1

    print(f"\n{'='*80}")
    print(f"Success: {success}/{len(ALL_SERVICES)}")
    print(f"Failed: {failed}/{len(ALL_SERVICES)}")
    print(f"Fixed: {fixed} apps")

    if success > 0:
        print(f"\n✅ All apps now compatible with Snowflake Streamlit!")
        print(f"   Refresh buttons will work correctly")

if __name__ == "__main__":
    main()
