"""
Add 'CPR - ' prefix to all Streamlit app titles
"""

import os
import re
from pathlib import Path

# Base directory
BASE_DIR = Path(r"C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\13_STREAMLIT_COMPLETE")

# All apps
APPS = [
    "Ancon", "BitSight", "Cisco_AMP", "Crowdstrike", "CybelAngel",
    "Intel_Threats", "Leviat", "Proofpoint", "Qualys", "SentinelOne",
    "ServiceNow", "Sophos", "Splunk", "Symantec", "Tenable",
    "Trellix", "Zerofox", "Zscaler"
]

def add_cpr_prefix_to_title(file_path):
    """Add CPR - prefix to page_title if not present"""
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find page_title
        pattern = r'(page_title\s*=\s*["\'])([^"\']+)(["\'])'
        match = re.search(pattern, content)

        if not match:
            return False, "page_title not found"

        current_title = match.group(2)

        # Check if already has CPR prefix
        if current_title.startswith("CPR - "):
            return False, f"Already has prefix: '{current_title}'"

        # Add CPR prefix
        new_title = f"CPR - {current_title}"
        new_content = re.sub(
            pattern,
            rf'\g<1>{new_title}\g<3>',
            content
        )

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True, f"'{current_title}' -> '{new_title}'"

    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    print("=" * 80)
    print("ADDING CPR PREFIX TO ALL STREAMLIT APPS")
    print("=" * 80)
    print()

    updated = 0
    skipped = 0
    errors = 0

    for app_name in APPS:
        app_path = BASE_DIR / app_name / "streamlit_app.py"

        if not app_path.exists():
            print(f"[ERROR] {app_name}: File not found")
            errors += 1
            continue

        success, message = add_cpr_prefix_to_title(app_path)

        if success:
            print(f"[UPDATED] {app_name}")
            print(f"          {message}")
            updated += 1
        else:
            if "Already has prefix" in message:
                print(f"[SKIP] {app_name}")
                print(f"       {message}")
                skipped += 1
            else:
                print(f"[ERROR] {app_name}")
                print(f"        {message}")
                errors += 1

        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Updated: {updated}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")
    print(f"Total: {len(APPS)}")

if __name__ == "__main__":
    main()
