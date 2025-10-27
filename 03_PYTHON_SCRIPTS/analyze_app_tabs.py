"""
Analyze tab structure across all Streamlit apps

Author: Data Engineering Team
Date: 2025-10-25
"""

import sys
import re
from pathlib import Path
from collections import Counter

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SOURCE_PATH = Path(r"C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\13_STREAMLIT_COMPLETE")

ALL_SERVICES = [
    'Ancon', 'BitSight', 'Cisco_AMP', 'Crowdstrike', 'CybelAngel', 'Intel_Threats',
    'Leviat', 'Proofpoint', 'Qualys', 'SentinelOne', 'ServiceNow', 'Sophos',
    'Splunk', 'Symantec', 'Tenable', 'Trellix', 'Zerofox', 'Zscaler'
]

def clean_tab_name(name):
    """Remove emojis from tab names"""
    # Remove emojis by removing characters outside ASCII range
    return re.sub(r'[^\x00-\x7F]+', '', name).strip()

def extract_tabs(service_name):
    """Extract tab names from service app"""
    app_file = SOURCE_PATH / service_name / "streamlit_app.py"

    if not app_file.exists():
        return []

    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find st.tabs([...]) pattern
    pattern = r'st\.tabs\(\[(.*?)\]\)'
    match = re.search(pattern, content, re.DOTALL)

    if match:
        tabs_str = match.group(1)
        # Extract quoted strings
        tab_names = re.findall(r'["\'](.*?)["\']', tabs_str)
        return [clean_tab_name(name) for name in tab_names]

    return []

def main():
    """Analyze all apps"""
    print("="*80)
    print("TAB STRUCTURE ANALYSIS - ALL 18 APPS")
    print("="*80)

    tabs_by_service = {}

    for service in ALL_SERVICES:
        tabs = extract_tabs(service)
        if tabs:
            tabs_by_service[service] = tabs
            print(f"\n{service} ({len(tabs)} tabs):")
            for i, tab in enumerate(tabs, 1):
                print(f"  {i}. {tab}")

    # Find common tab patterns
    all_tabs = []
    for tabs in tabs_by_service.values():
        all_tabs.extend(tabs)

    common_tabs = Counter(all_tabs)

    print("\n" + "="*80)
    print("COMMON TAB PATTERNS")
    print("="*80)

    for tab, count in sorted(common_tabs.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len(tabs_by_service)) * 100
        bar = "=" * int(pct / 5)
        print(f"{tab:40} {count:2}/{len(tabs_by_service):2} apps ({pct:5.1f}%) {bar}")

    # Identify core tabs
    print("\n" + "="*80)
    print("TAB CATEGORIES")
    print("="*80)

    # Common patterns
    core_tabs = [name for name, count in common_tabs.items() if count >= len(tabs_by_service) * 0.3]
    unique_tabs = [name for name, count in common_tabs.items() if count <= 2]

    print(f"\nCORE TABS (in 30%+ of apps): {len(core_tabs)}")
    for tab in sorted(core_tabs):
        print(f"  - {tab}")

    print(f"\nUNIQUE TABS (in 2 or fewer apps): {len(unique_tabs)}")
    for tab in sorted(unique_tabs):
        print(f"  - {tab}")

    # Distribution
    print("\n" + "="*80)
    print("TAB COUNT DISTRIBUTION")
    print("="*80)

    tab_counts = Counter([len(tabs) for tabs in tabs_by_service.values()])
    for count in sorted(tab_counts.keys()):
        services = [s for s, t in tabs_by_service.items() if len(t) == count]
        print(f"{count} tabs: {tab_counts[count]} apps - {', '.join(services)}")

if __name__ == "__main__":
    main()
