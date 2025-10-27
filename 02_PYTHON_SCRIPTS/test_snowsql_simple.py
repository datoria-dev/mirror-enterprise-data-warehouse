"""
Simple SnowSQL Connection Test with SSO (Okta)
Quick test to verify SnowSQL and SSO authentication work
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime

# Configuration
SNOWSQL_PATH = r"C:\Program Files\Snowflake SnowSQL\snowsql.exe"
CONFIG_FILE = Path(__file__).parent.parent / "snowflake_config.json"

def load_config():
    """Load Snowflake configuration from JSON file"""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}")

    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def check_snowsql_installed():
    """Check if SnowSQL is installed and accessible"""
    if not os.path.exists(SNOWSQL_PATH):
        return False, f"SnowSQL not found at: {SNOWSQL_PATH}"

    try:
        result = subprocess.run(
            [SNOWSQL_PATH, "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            return True, f"SnowSQL installed: {version}"
        else:
            return False, "SnowSQL found but failed to execute"
    except Exception as e:
        return False, f"Error checking SnowSQL: {str(e)}"

def test_connection(config):
    """Test Snowflake connection with SSO - SINGLE QUERY ONLY"""

    # Simple query to test connection
    query = "SELECT CURRENT_USER() AS USER, CURRENT_ROLE() AS ROLE, CURRENT_WAREHOUSE() AS WAREHOUSE, CURRENT_DATABASE() AS DATABASE, CURRENT_SCHEMA() AS SCHEMA;"

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

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Testing connection...")
    print(f"Account: {config['account']}")
    print(f"User: {config['user']}")
    print(f"Warehouse: {config['warehouse']}")
    print(f"Database: {config['database']}")
    print(f"Schema: {config['schema']}")
    print(f"Role: {config['role']}")
    print("\n⏳ Opening browser for SSO authentication...")
    print("   (Please complete Okta login in the browser window)")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=90  # Increased timeout for SSO
        )

        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr

    except subprocess.TimeoutExpired:
        return False, "Connection timeout - SSO authentication may have taken too long"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def main():
    """Main test execution"""
    print("=" * 70)
    print("Snowflake Connection Test (Simple)")
    print("=" * 70)

    # Check SnowSQL installation
    print("\n[Step 1/3] Checking SnowSQL installation...")
    installed, message = check_snowsql_installed()
    print(f"{'✓' if installed else '✗'} {message}")

    if not installed:
        print("\nPlease install SnowSQL first:")
        print("1. Run: reinstall_snowsql.bat (as Administrator)")
        print("2. Or download from: https://developers.snowflake.com/snowsql/")
        return 1

    # Load configuration
    print("\n[Step 2/3] Loading configuration...")
    try:
        config = load_config()
        print(f"✓ Configuration loaded from: {CONFIG_FILE.name}")
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return 1

    # Test connection (SINGLE TEST ONLY)
    print("\n[Step 3/3] Testing Snowflake connection...")
    success, output = test_connection(config)

    print("\n" + "=" * 70)
    print("TEST RESULT")
    print("=" * 70)

    if success:
        print("\n✓ CONNECTION SUCCESSFUL!")
        print("\nConnection details:")
        print(output)
        print("\n✓ SnowSQL and SSO authentication are working correctly!")
        print("\n➡️  You can now proceed to deploy Streamlit apps:")
        print("   .\\deploy_apps.bat")
        return 0
    else:
        print("\n✗ CONNECTION FAILED!")
        print(f"\nError details:\n{output}")
        print("\nTroubleshooting:")
        print("1. Check that you completed Okta authentication in browser")
        print("2. Verify network connection")
        print("3. Check Snowflake permissions for your user")
        print("4. Try running again: .\\test_snowsql_connection.bat")
        return 1

if __name__ == "__main__":
    exit(main())
