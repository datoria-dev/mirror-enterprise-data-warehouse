"""
Check Snowflake Stage Files
Shows where files are stored in Snowflake and their details
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

# Configuration
SNOWSQL_PATH = r"C:\Program Files\Snowflake SnowSQL\snowsql.exe"
CONFIG_FILE = Path(__file__).parent.parent / "snowflake_config.json"

def load_config():
    """Load Snowflake configuration"""
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def execute_query(config: dict, query: str):
    """Execute SnowSQL query"""
    cmd = [
        SNOWSQL_PATH,
        "-a", config["account"],
        "-u", config["user"],
        "--authenticator", config["authenticator"],
        "-w", config["warehouse"],
        "-d", config["database"],
        "-s", config["schema"],
        "-r", config["role"],
        "-q", query
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr

    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Main execution"""
    print("="*70)
    print("SNOWFLAKE STAGE FILES CHECKER")
    print("="*70)

    # Load config
    config = load_config()

    print(f"\nDatabase: {config['database']}")
    print(f"Schema: {config['schema']}")
    print(f"\n⏳ Opening browser for SSO authentication...")

    # Check stage
    print("\n[Step 1/3] Checking stage...")
    query = "SHOW STAGES LIKE 'STREAMLIT_APPS_STAGE';"
    success, output = execute_query(config, query)

    if success:
        print("✓ Stage found: STREAMLIT_APPS_STAGE")
        print(f"\nStage details:\n{output}")
    else:
        print(f"✗ Stage not found or error: {output}")
        return 1

    # List all files in stage
    print("\n[Step 2/3] Listing all files in stage...")
    query = "LIST @STREAMLIT_APPS_STAGE;"
    success, output = execute_query(config, query)

    if success:
        print("✓ Files in stage:")
        print(f"\n{output}")

        # Count files
        lines = output.split('\n')
        file_count = sum(1 for line in lines if 'streamlit_app.py' in line or 'environment.yml' in line)
        print(f"\nTotal files found: {file_count}")
    else:
        print(f"✗ Error listing files: {output}")

    # List files for specific app
    print("\n[Step 3/3] Listing files for Symantec app...")
    query = "LIST @STREAMLIT_APPS_STAGE/Symantec/;"
    success, output = execute_query(config, query)

    if success:
        print("✓ Symantec app files:")
        print(f"\n{output}")
    else:
        print(f"✗ Error: {output}")

    # Show file locations
    print("\n" + "="*70)
    print("FILE LOCATIONS IN SNOWFLAKE")
    print("="*70)
    print("\nStage Location:")
    print(f"  @{config['database']}.{config['schema']}.STREAMLIT_APPS_STAGE/")
    print("\nPer-App Structure:")
    print(f"  @STREAMLIT_APPS_STAGE/Symantec/streamlit_app.py")
    print(f"  @STREAMLIT_APPS_STAGE/Symantec/environment.yml")
    print(f"  @STREAMLIT_APPS_STAGE/Trellix/streamlit_app.py")
    print(f"  @STREAMLIT_APPS_STAGE/Trellix/environment.yml")
    print(f"  ... (for all 18 apps)")

    print("\n" + "="*70)
    print("HOW TO ACCESS IN SNOWFLAKE UI")
    print("="*70)
    print("\n1. Login to Snowflake: https://app.snowflake.com")
    print(f"2. Select Database: {config['database']}")
    print(f"3. Select Schema: {config['schema']}")
    print("4. Navigate to: Data → Databases → Stages")
    print("5. Find stage: STREAMLIT_APPS_STAGE")
    print("6. Browse files by app folder")

    return 0

if __name__ == "__main__":
    exit(main())
