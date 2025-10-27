"""
Audit and Fix All Streamlit Apps
- Check for syntax errors
- Add 'CPR - ' prefix to titles
- Standardize structure based on ZeroFox template
"""

import os
import re
import ast
import sys
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

def check_syntax(file_path):
    """Check if Python file has valid syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)

def check_title_prefix(file_path):
    """Check if app title has 'CPR - ' prefix"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for page_title in st.set_page_config
        match = re.search(r'page_title\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            title = match.group(1)
            has_prefix = title.startswith("CPR - ")
            return title, has_prefix
        return None, False
    except Exception as e:
        return None, False

def audit_all_apps():
    """Audit all Streamlit apps"""
    print("=" * 80)
    print("STREAMLIT APPS AUDIT")
    print("=" * 80)
    print()

    results = []

    for app_name in APPS:
        app_path = BASE_DIR / app_name / "streamlit_app.py"

        if not app_path.exists():
            print(f"[ERROR] {app_name}: File not found")
            results.append({
                'app': app_name,
                'exists': False,
                'syntax_ok': False,
                'has_prefix': False,
                'title': None,
                'error': 'File not found'
            })
            continue

        # Check syntax
        syntax_ok, syntax_error = check_syntax(app_path)

        # Check title prefix
        title, has_prefix = check_title_prefix(app_path)

        if syntax_ok and has_prefix:
            status = "[OK]"
        elif syntax_ok:
            status = "[WARN]"
        else:
            status = "[ERROR]"

        print(f"{status} {app_name}")
        print(f"   Path: {app_path}")
        print(f"   Syntax: {'OK' if syntax_ok else 'ERROR'}")
        if not syntax_ok:
            print(f"   Error: {syntax_error}")
        print(f"   Title: {title if title else 'Not found'}")
        print(f"   Has CPR prefix: {'Yes' if has_prefix else 'No'}")
        print()

        results.append({
            'app': app_name,
            'exists': True,
            'syntax_ok': syntax_ok,
            'has_prefix': has_prefix,
            'title': title,
            'error': syntax_error if not syntax_ok else None
        })

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    total = len(results)
    exists_count = sum(1 for r in results if r['exists'])
    syntax_ok_count = sum(1 for r in results if r['syntax_ok'])
    has_prefix_count = sum(1 for r in results if r['has_prefix'])

    print(f"Total apps: {total}")
    print(f"Files found: {exists_count}/{total}")
    print(f"Valid syntax: {syntax_ok_count}/{exists_count}")
    print(f"Has CPR prefix: {has_prefix_count}/{exists_count}")
    print()

    # Apps needing fixes
    syntax_errors = [r for r in results if r['exists'] and not r['syntax_ok']]
    missing_prefix = [r for r in results if r['exists'] and r['syntax_ok'] and not r['has_prefix']]

    if syntax_errors:
        print("APPS WITH SYNTAX ERRORS:")
        for r in syntax_errors:
            print(f"  [ERROR] {r['app']}: {r['error']}")
        print()

    if missing_prefix:
        print("APPS MISSING CPR PREFIX:")
        for r in missing_prefix:
            print(f"  [WARN] {r['app']}: '{r['title']}'")
        print()

    if not syntax_errors and not missing_prefix:
        print("[OK] All apps are in good condition!")

    return results

if __name__ == "__main__":
    audit_all_apps()
