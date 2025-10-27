"""
Remove misleading "Chart not available" messages where no table exists below

Problem: Messages say "view data in table below" but there's no table
Solution: Remove message if no st.dataframe() appears within next 10 lines

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
    'Ancon', 'BitSight', 'Cisco_AMP', 'Crowdstrike', 'CybelAngel', 'Intel_Threats',
    'Leviat', 'Proofpoint', 'Qualys', 'SentinelOne', 'ServiceNow', 'Sophos',
    'Splunk', 'Symantec', 'Tenable', 'Trellix', 'Zerofox', 'Zscaler'
]

def has_table_after(lines, start_idx, lookahead=15):
    """
    Check if there's a st.dataframe() within next N lines
    """
    for i in range(start_idx + 1, min(start_idx + lookahead, len(lines))):
        if 'st.dataframe(' in lines[i] or 'st.table(' in lines[i]:
            return True
    return False

def remove_misleading_messages(content):
    """
    Remove 'Chart not available' messages that don't have tables below
    """
    lines = content.split('\n')
    modified_lines = []
    removed_count = 0
    kept_count = 0

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this is a chart message line
        if 'Chart not available in Snowflake' in line and 'st.info(' in line:
            # Check if there's a table in the next few lines
            if has_table_after(lines, i, lookahead=15):
                # Keep the message - there IS a table below
                modified_lines.append(line)
                kept_count += 1
            else:
                # Remove the message - NO table below
                removed_count += 1
                # Skip this line entirely
        else:
            # Not a chart message, keep the line
            modified_lines.append(line)

        i += 1

    return '\n'.join(modified_lines), removed_count, kept_count

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

        # Count existing messages
        total_messages = content.count('Chart not available in Snowflake')

        if total_messages == 0:
            print("  ✅ No chart messages found")
            return True

        print(f"  📊 Found {total_messages} chart message(s)")

        # Remove misleading ones
        new_content, removed, kept = remove_misleading_messages(content)

        if removed == 0:
            print(f"  ✅ All {kept} messages have tables below - no changes needed")
            return True

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

        print(f"  ✅ Removed {removed} misleading message(s), kept {kept} valid message(s)")
        return True

    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Process all apps"""
    print("="*80)
    print("REMOVING MISLEADING 'CHART NOT AVAILABLE' MESSAGES")
    print("="*80)
    print("\nProblem: Messages say 'view data in table below' but no table exists")
    print("Solution: Remove message if no st.dataframe() within next 15 lines\n")

    success = 0
    failed = 0
    total_removed = 0
    total_kept = 0

    for service in ALL_SERVICES:
        if process_app(service):
            success += 1
        else:
            failed += 1

    print(f"\n{'='*80}")
    print(f"✅ Success: {success}/{len(ALL_SERVICES)}")
    print(f"❌ Failed: {failed}/{len(ALL_SERVICES)}")

    if success > 0:
        print(f"\n✅ User experience improved!")
        print(f"   Messages now only appear where tables actually exist")

if __name__ == "__main__":
    main()
