"""
Snowflake Connection Test with SSO (Okta)
Automates SnowSQL connection testing and validation
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

def test_connection(config, query="SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA();"):
    """Test Snowflake connection with SSO"""

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
    print("\nOpening browser for SSO authentication...")

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

    except subprocess.TimeoutExpired:
        return False, "Connection timeout - SSO authentication may have failed"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def test_metadata_access(config):
    """Test access to metadata tables"""

    queries = [
        ("List tables", "SHOW TABLES IN SCHEMA DEV_TRANSFORMATION.METADATA;"),
        ("Count TABLE_REGISTRY", "SELECT COUNT(*) as TOTAL_TABLES FROM TABLE_REGISTRY;"),
        ("Count COLUMN_METADATA", "SELECT COUNT(*) as TOTAL_COLUMNS FROM COLUMN_METADATA;"),
        ("Count SERVICE_CATALOG", "SELECT COUNT(*) as TOTAL_SERVICES FROM SERVICE_CATALOG;")
    ]

    results = {}

    for test_name, query in queries:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Testing: {test_name}")
        success, output = test_connection(config, query)
        results[test_name] = {
            "success": success,
            "output": output if success else f"ERROR: {output}"
        }

        if success:
            print(f"✓ {test_name} - SUCCESS")
        else:
            print(f"✗ {test_name} - FAILED")

    return results

def main():
    """Main test execution"""
    print("=" * 60)
    print("Snowflake Connection Test with SSO (Okta)")
    print("=" * 60)

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
        print(f"✓ Configuration loaded from: {CONFIG_FILE}")
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return 1

    # Test connection
    print("\n[Step 3/3] Testing Snowflake connection...")
    success, output = test_connection(config)

    if success:
        print("\n✓ Connection successful!")
        print("\nConnection details:")
        print(output)

        # Test metadata access
        print("\n" + "=" * 60)
        print("Testing Metadata Access")
        print("=" * 60)
        results = test_metadata_access(config)

        # Summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)

        total_tests = len(results) + 1  # +1 for connection test
        passed_tests = sum(1 for r in results.values() if r["success"]) + 1

        print(f"\nTotal tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")

        if passed_tests == total_tests:
            print("\n✓ All tests passed! Snowflake connection is ready.")
            return 0
        else:
            print("\n⚠ Some tests failed. Check output above for details.")
            return 1
    else:
        print("\n✗ Connection failed!")
        print(f"\nError details:\n{output}")
        return 1

if __name__ == "__main__":
    exit(main())
