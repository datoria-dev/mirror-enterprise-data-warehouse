"""
Cleanup Old Streamlit Apps
===========================
Removes all old/duplicate Streamlit apps from Snowflake, keeping only STREAMLIT_* apps.

Apps to DELETE:
- All *_APP apps (18 old apps from 2025-10-24)
- All test apps with random names (12 apps from September)

Apps to KEEP:
- All STREAMLIT_* apps (18 correct apps from 2025-10-25)
"""

import subprocess
import json
import os
from datetime import datetime

# Configuration
SNOWFLAKE_CONFIG_PATH = "snowflake_config.json"

# Apps to DELETE (old naming convention)
APPS_TO_DELETE = [
    # Old *_APP convention (from 2025-10-24)
    "ANCON_APP",
    "BITSIGHT_APP",
    "CISCO_AMP_APP",
    "CROWDSTRIKE_APP",
    "CYBELANGEL_APP",
    "INTEL_THREATS_APP",
    "LEVIAT_APP",
    "PROOFPOINT_APP",
    "QUALYS_APP",
    "SENTINELONE_APP",
    "SERVICENOW_APP",
    "SOPHOS_APP",
    "SPLUNK_APP",
    "SYMANTEC_APP",
    "TENABLE_APP",
    "TRELLIX_APP",
    "ZEROFOX_APP",
    "ZSCALER_APP",

    # Test apps with random names (from September)
    "A65QT5DNLGVXTYLG",  # Intel Threats test
    "C1PCO0GG96WB8HKM",  # Trellix test
    "F2P8MTG3YRH3BQP2",  # Splunk test
    "FRHR_23PS3FJYE9P",  # CrowdStrike test
    "FTLB9_WFD4T7OZR_",  # Zerofox test
    "H7T18OIRZFF9QT89",  # Zscaler test
    "JNPMMKSV3LRYL3DN",  # Qualys test
    "PW0ZM2KZUCKRHITV",  # Symantec test
    "WDUIS6GO66HXW3UJ",  # Sophos test
    "W_UL633G006NYIN2",  # Cisco AMP test
    "YETW6KIAFOBICJZN",  # BitSight test
    "ZEE42_PN_2W77DLW",  # Alcon test
]

# Apps to KEEP (correct naming)
APPS_TO_KEEP = [
    "STREAMLIT_ANCON",
    "STREAMLIT_BITSIGHT",
    "STREAMLIT_CISCO_AMP",
    "STREAMLIT_CROWDSTRIKE",
    "STREAMLIT_CYBELANGEL",
    "STREAMLIT_INTEL_THREATS",
    "STREAMLIT_LEVIAT",
    "STREAMLIT_PROOFPOINT",
    "STREAMLIT_QUALYS",
    "STREAMLIT_SENTINELONE",
    "STREAMLIT_SERVICENOW",
    "STREAMLIT_SOPHOS",
    "STREAMLIT_SPLUNK",
    "STREAMLIT_SYMANTEC",
    "STREAMLIT_TENABLE",
    "STREAMLIT_TRELLIX",
    "STREAMLIT_ZEROFOX",
    "STREAMLIT_ZSCALER",
]

def load_config():
    """Load Snowflake configuration"""
    with open(SNOWFLAKE_CONFIG_PATH, 'r') as f:
        return json.load(f)

def create_cleanup_sql(config):
    """Create SQL script to delete old apps"""
    sql_lines = [
        "-- =====================================================",
        "-- CLEANUP OLD STREAMLIT APPS",
        f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "-- =====================================================",
        "",
        f"USE DATABASE {config['database']};",
        f"USE SCHEMA {config['schema']};",
        f"USE WAREHOUSE {config['warehouse']};",
        "",
        "-- Delete old apps with *_APP naming convention",
        "-- (Deployed 2025-10-24, replaced by STREAMLIT_* versions)",
        ""
    ]

    # Group apps by type
    app_suffix_apps = [app for app in APPS_TO_DELETE if app.endswith("_APP")]
    test_apps = [app for app in APPS_TO_DELETE if not app.endswith("_APP")]

    # Add *_APP deletions
    for app in app_suffix_apps:
        sql_lines.append(f"DROP STREAMLIT IF EXISTS {app};")

    sql_lines.extend([
        "",
        "-- Delete test apps with random names",
        "-- (Created in September for testing)",
        ""
    ])

    # Add test app deletions
    for app in test_apps:
        sql_lines.append(f"DROP STREAMLIT IF EXISTS {app};")

    sql_lines.extend([
        "",
        "-- Verify cleanup - should only show STREAMLIT_* apps",
        "SHOW STREAMLITS IN SCHEMA;",
        ""
    ])

    return "\n".join(sql_lines)

def save_sql_script(sql_content, config):
    """Save SQL script to deployment_logs"""
    os.makedirs("deployment_logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"deployment_logs/cleanup_streamlit_apps_{timestamp}.sql"

    with open(filename, 'w') as f:
        f.write(sql_content)

    return filename

def execute_cleanup(config, sql_file):
    """Execute cleanup via SnowSQL"""
    snowsql_path = r"C:\Program Files\Snowflake SnowSQL\snowsql.exe"

    cmd = [
        snowsql_path,
        "-a", config["account"],
        "-u", config["user"],
        "--authenticator", "externalbrowser",
        "-w", config["warehouse"],
        "-d", config["database"],
        "-s", config["schema"],
        "-r", config["role"],
        "-f", sql_file
    ]

    print("\n[EXECUTING] Cleanup script...")
    print(f"[NOTE] Browser will open for SSO authentication (Okta)\n")

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Save log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"deployment_logs/cleanup_streamlit_apps_{timestamp}.log"
    with open(log_file, 'w') as f:
        f.write(result.stdout)
        if result.stderr:
            f.write("\n\n=== ERRORS ===\n")
            f.write(result.stderr)

    print(f"[LOG] Saved to: {log_file}\n")

    return result.returncode == 0

def main():
    print("=" * 70)
    print("CLEANUP OLD STREAMLIT APPS")
    print("=" * 70)

    # Load config
    print("\n[1/4] Loading configuration...")
    config = load_config()
    print(f"      Database: {config['database']}")
    print(f"      Schema: {config['schema']}")

    # Create SQL
    print("\n[2/4] Creating cleanup SQL script...")
    sql_content = create_cleanup_sql(config)
    sql_file = save_sql_script(sql_content, config)
    print(f"      SQL script: {sql_file}")

    # Summary
    print("\n[3/4] Cleanup Summary:")
    print(f"      Apps to DELETE: {len(APPS_TO_DELETE)}")
    print(f"        - *_APP convention: {len([a for a in APPS_TO_DELETE if a.endswith('_APP')])}")
    print(f"        - Test apps: {len([a for a in APPS_TO_DELETE if not a.endswith('_APP')])}")
    print(f"      Apps to KEEP: {len(APPS_TO_KEEP)} (STREAMLIT_* format)")

    # Execute
    print("\n[4/4] Executing cleanup...")
    success = execute_cleanup(config, sql_file)

    print("\n" + "=" * 70)
    if success:
        print("CLEANUP COMPLETE!")
        print("=" * 70)
        print(f"\n✅ Deleted {len(APPS_TO_DELETE)} old apps")
        print(f"✅ Kept {len(APPS_TO_KEEP)} correct apps (STREAMLIT_* format)")
        print("\nNext Steps:")
        print("1. Go to Snowflake UI")
        print("2. Navigate to DEV_REPORTING -> SECURITY_ANALYTICS -> Streamlit")
        print("3. Verify you see only 18 apps with STREAMLIT_* names")
    else:
        print("CLEANUP FAILED - Check logs for details")
        print("=" * 70)

if __name__ == "__main__":
    main()
