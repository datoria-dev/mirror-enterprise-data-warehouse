"""
Deploy All Fixed Streamlit Apps to Snowflake
- Fixed syntax errors in Trellix and Crowdstrike
- Added 'CPR - ' prefix to all titles
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configuration
SNOWSQL_PATH = r"C:\Program Files\Snowflake SnowSQL\snowsql.exe"
ACCOUNT = "MYORG-DATA_WH"
USER = "fuad.onate@CompanyX.com"
WAREHOUSE = "DEV_WH"
DATABASE = "DEV_REPORTING"
SCHEMA = "SECURITY_ANALYTICS"
ROLE = "DEV_DEVELOPER"

# Base directory
BASE_DIR = Path(r"C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\13_STREAMLIT_COMPLETE")

# All apps with their Snowflake names
APPS = [
    ("Ancon", "STREAMLIT_ANCON", "Ancon Security Monitoring"),
    ("BitSight", "STREAMLIT_BITSIGHT", "BitSight Security Ratings"),
    ("Cisco_AMP", "STREAMLIT_CISCO_AMP", "Cisco Advanced Malware Protection"),
    ("Crowdstrike", "STREAMLIT_CROWDSTRIKE", "CrowdStrike Falcon Dashboard"),
    ("CybelAngel", "STREAMLIT_CYBELANGEL", "CybelAngel Digital Risk Protection"),
    ("Intel_Threats", "STREAMLIT_INTEL_THREATS", "Threat Intelligence Dashboard"),
    ("Leviat", "STREAMLIT_LEVIAT", "Leviat Security Analytics"),
    ("Proofpoint", "STREAMLIT_PROOFPOINT", "Proofpoint Email Security"),
    ("Qualys", "STREAMLIT_QUALYS", "Qualys Vulnerability Management"),
    ("SentinelOne", "STREAMLIT_SENTINELONE", "SentinelOne Security Platform"),
    ("ServiceNow", "STREAMLIT_SERVICENOW", "ServiceNow Security Operations"),
    ("Sophos", "STREAMLIT_SOPHOS", "Sophos Security Dashboard"),
    ("Splunk", "STREAMLIT_SPLUNK", "Splunk Security Analytics"),
    ("Symantec", "STREAMLIT_SYMANTEC", "Symantec Endpoint Security Dashboard"),
    ("Tenable", "STREAMLIT_TENABLE", "Tenable Vulnerability Management"),
    ("Trellix", "STREAMLIT_TRELLIX", "Trellix Security Analytics"),
    ("Zerofox", "STREAMLIT_ZEROFOX", "ZeroFox Digital Risk Protection"),
    ("Zscaler", "STREAMLIT_ZSCALER", "Zscaler Cloud Security"),
]

# Log file
LOG_DIR = Path(r"C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\deployment_logs")
LOG_DIR.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = LOG_DIR / f"deploy_all_apps_{timestamp}.log"
SQL_FILE = LOG_DIR / f"deploy_all_apps_{timestamp}.sql"

def log(message):
    """Log message to console and file"""
    print(message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{message}\n")

def deploy_app(folder_name, streamlit_name, title):
    """Deploy a single Streamlit app"""
    app_dir = BASE_DIR / folder_name

    if not app_dir.exists():
        log(f"  [ERROR] Directory not found: {app_dir}")
        return False

    streamlit_file = app_dir / "streamlit_app.py"
    env_file = app_dir / "environment.yml"

    if not streamlit_file.exists():
        log(f"  [ERROR] streamlit_app.py not found in {folder_name}")
        return False

    # Build SQL command to create/replace Streamlit
    sql_parts = [
        f"CREATE OR REPLACE STREAMLIT {DATABASE}.{SCHEMA}.{streamlit_name}",
        f"ROOT_LOCATION = '@{DATABASE}.{SCHEMA}.STREAMLIT_APPS_STAGE/{folder_name}'",
        f"MAIN_FILE = 'streamlit_app.py'",
        f"QUERY_WAREHOUSE = {WAREHOUSE}"
    ]

    if env_file.exists():
        sql_parts.append(f"EXTERNAL_ACCESS_INTEGRATIONS = ()")
        sql_parts.append(f"PACKAGES = ()")
        sql_parts.append(f"COMMENT = 'CPR - {title}'")
    else:
        sql_parts.append(f"COMMENT = 'CPR - {title}'")

    sql = "\n".join(sql_parts) + ";"

    # Log SQL
    with open(SQL_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n-- {streamlit_name}\n")
        f.write(f"{sql}\n")

    # Upload files to stage
    log(f"  Uploading files to stage...")

    # Upload streamlit_app.py
    put_cmd_streamlit = f'PUT file://{str(streamlit_file).replace(chr(92), "/")} @{DATABASE}.{SCHEMA}.STREAMLIT_APPS_STAGE/{folder_name}/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;'

    result = subprocess.run(
        [
            SNOWSQL_PATH,
            "-a", ACCOUNT,
            "-u", USER,
            "--authenticator", "externalbrowser",
            "-w", WAREHOUSE,
            "-d", DATABASE,
            "-s", SCHEMA,
            "-r", ROLE,
            "-q", put_cmd_streamlit
        ],
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:
        log(f"  [ERROR] Failed to upload streamlit_app.py")
        log(f"  {result.stderr}")
        return False

    # Upload environment.yml if exists
    if env_file.exists():
        put_cmd_env = f'PUT file://{str(env_file).replace(chr(92), "/")} @{DATABASE}.{SCHEMA}.STREAMLIT_APPS_STAGE/{folder_name}/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;'

        result = subprocess.run(
            [
                SNOWSQL_PATH,
                "-a", ACCOUNT,
                "-u", USER,
                "--authenticator", "externalbrowser",
                "-w", WAREHOUSE,
                "-d", DATABASE,
                "-s", SCHEMA,
                "-r", ROLE,
                "-q", put_cmd_env
            ],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            log(f"  [WARN] Failed to upload environment.yml (continuing anyway)")

    # Create/Replace Streamlit
    log(f"  Creating Streamlit in Snowflake...")

    result = subprocess.run(
        [
            SNOWSQL_PATH,
            "-a", ACCOUNT,
            "-u", USER,
            "--authenticator", "externalbrowser",
            "-w", WAREHOUSE,
            "-d", DATABASE,
            "-s", SCHEMA,
            "-r", ROLE,
            "-q", sql
        ],
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:
        log(f"  [ERROR] Failed to create Streamlit")
        log(f"  {result.stderr}")
        return False

    log(f"  [SUCCESS] Deployed successfully")
    return True

def main():
    log("=" * 80)
    log("DEPLOYING ALL FIXED STREAMLIT APPS")
    log("=" * 80)
    log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Target: {DATABASE}.{SCHEMA}")
    log(f"Total apps: {len(APPS)}")
    log(f"Log file: {LOG_FILE}")
    log(f"SQL file: {SQL_FILE}")
    log("=" * 80)
    log("")  # Empty line for readability

    # Write SQL file header
    with open(SQL_FILE, 'w', encoding='utf-8') as f:
        f.write(f"-- Deploy All Fixed Streamlit Apps\n")
        f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"-- Target: {DATABASE}.{SCHEMA}\n")
        f.write(f"-- Total apps: {len(APPS)}\n")
        f.write(f"\nUSE DATABASE {DATABASE};\n")
        f.write(f"USE SCHEMA {SCHEMA};\n")
        f.write(f"USE WAREHOUSE {WAREHOUSE};\n")
        f.write(f"USE ROLE {ROLE};\n\n")

    successful = 0
    failed = 0

    for idx, (folder_name, streamlit_name, title) in enumerate(APPS, 1):
        log(f"[{idx}/{len(APPS)}] Deploying {streamlit_name}...")
        log(f"  Folder: {folder_name}")
        log(f"  Title: CPR - {title}")

        success = deploy_app(folder_name, streamlit_name, title)

        if success:
            successful += 1
        else:
            failed += 1

        log("")

    # Summary
    log("=" * 80)
    log("DEPLOYMENT SUMMARY")
    log("=" * 80)
    log(f"Successful: {successful}")
    log(f"Failed: {failed}")
    log(f"Total: {len(APPS)}")
    log(f"Success rate: {(successful/len(APPS)*100):.1f}%")
    log("")
    log(f"Log file: {LOG_FILE}")
    log(f"SQL file: {SQL_FILE}")
    log("=" * 80)

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
