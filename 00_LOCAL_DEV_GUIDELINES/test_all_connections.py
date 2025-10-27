"""
Test All Connections - Quick Connection Validator

Purpose: Test connections to Snowflake, Git, and Python Snowpark
Usage: python test_all_connections.py
"""

import subprocess
import sys
import os

def test_snowsql():
    """Test SnowSQL connection"""
    print("\n[1/3] Testing SnowSQL connection...")
    print("      Browser will open for SSO authentication...")

    try:
        result = subprocess.run([
            "snowsql",
            "-a", "GenericCorp-CRH_EDW",
            "-u", "fuad.onate@CompanyX.com",
            "--authenticator", "externalbrowser",
            "-w", "DEV_WH",
            "-d", "DEV_REPORTING",
            "-s", "SECURITY_ANALYTICS",
            "-r", "DEV_DEVELOPER",
            "-q", "SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE();"
        ], capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            print("      ✅ SnowSQL connection successful")
            print(f"      Output: {result.stdout.strip()}")
            return True
        else:
            print("      ❌ SnowSQL connection failed")
            print(f"      Error: {result.stderr}")
            return False
    except FileNotFoundError:
        print("      ❌ SnowSQL not found - is it installed?")
        print("      Install: https://docs.snowflake.com/en/user-guide/snowsql-install-config")
        return False
    except subprocess.TimeoutExpired:
        print("      ❌ SnowSQL connection timeout (SSO authentication not completed)")
        return False
    except Exception as e:
        print(f"      ❌ SnowSQL error: {e}")
        return False

def test_git():
    """Test Git connection"""
    print("\n[2/3] Testing Git connection...")

    try:
        # Check if in git repo
        result_check = subprocess.run([
            "git", "rev-parse", "--git-dir"
        ], capture_output=True, text=True)

        if result_check.returncode != 0:
            print("      ❌ Not in a Git repository")
            return False

        # Check remotes
        result = subprocess.run([
            "git", "remote", "-v"
        ], capture_output=True, text=True)

        if "dev.azure.com" in result.stdout:
            print("      ✅ Git configured for Azure DevOps")
            print(f"      Remote: origin -> Azure DevOps")
            return True
        else:
            print("      ⚠️  Git remote not configured for Azure DevOps")
            print(f"      Current remotes:\n{result.stdout}")
            return False
    except FileNotFoundError:
        print("      ❌ Git not found - is it installed?")
        return False
    except Exception as e:
        print(f"      ❌ Git error: {e}")
        return False

def test_snowpark():
    """Test Snowpark connection"""
    print("\n[3/3] Testing Python Snowpark...")
    print("      Browser will open for SSO authentication...")

    try:
        from snowflake.snowpark import Session

        connection_parameters = {
            "account": "GenericCorp-CRH_EDW",
            "user": "fuad.onate@CompanyX.com",
            "authenticator": "externalbrowser",
            "warehouse": "DEV_WH",
            "database": "DEV_REPORTING",
            "schema": "SECURITY_ANALYTICS",
            "role": "DEV_DEVELOPER"
        }

        session = Session.builder.configs(connection_parameters).create()
        result = session.sql("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_DATABASE()").collect()
        session.close()

        print("      ✅ Snowpark connection successful")
        print(f"      User: {result[0][0]}, Role: {result[0][1]}, Database: {result[0][2]}")
        return True
    except ImportError:
        print("      ❌ Snowpark not installed")
        print("      Install: pip install snowflake-snowpark-python")
        return False
    except Exception as e:
        print(f"      ❌ Snowpark error: {e}")
        return False

def test_snowflake_config():
    """Test if snowflake_config.json exists"""
    print("\n[BONUS] Checking snowflake_config.json...")

    config_path = "snowflake_config.json"

    if os.path.exists(config_path):
        print(f"      ✅ snowflake_config.json found at {os.path.abspath(config_path)}")

        try:
            import json
            with open(config_path, 'r') as f:
                config = json.load(f)

            required_keys = ["account", "user", "authenticator", "warehouse", "database", "schema", "role"]
            missing_keys = [key for key in required_keys if key not in config]

            if missing_keys:
                print(f"      ⚠️  Missing keys: {', '.join(missing_keys)}")
                return False
            else:
                print(f"      ✅ All required keys present")
                print(f"      Account: {config.get('account')}")
                print(f"      Database: {config.get('database')}")
                print(f"      Schema: {config.get('schema')}")
                return True
        except json.JSONDecodeError:
            print("      ❌ Invalid JSON format")
            return False
        except Exception as e:
            print(f"      ❌ Error reading config: {e}")
            return False
    else:
        print("      ⚠️  snowflake_config.json not found")
        print(f"      Create it from template: snowflake_config.json.template")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("CONNECTION TESTS - SECURITY_ANALYTICS Data Warehouse")
    print("=" * 70)
    print("\nTesting connections to all platforms...")
    print("Note: Browser will open twice for SSO authentication (SnowSQL and Snowpark)")

    results = []
    results.append(("SnowSQL", test_snowsql()))
    results.append(("Git", test_git()))
    results.append(("Snowpark", test_snowpark()))

    # Bonus test
    config_result = test_snowflake_config()

    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:15} {status}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print("-" * 70)
    print(f"Total: {passed}/{total} connections successful")

    if config_result:
        print("Config: ✅ snowflake_config.json valid")
    else:
        print("Config: ⚠️  snowflake_config.json issue")

    print("=" * 70)

    if all(result for _, result in results):
        print("\n🎉 SUCCESS! All connections working!")
        print("\nYou're ready to start development:")
        print("  - Snowflake: snowsql or Python Snowpark")
        print("  - Git: Push/pull to Azure DevOps")
        print("  - Scripts: Run deployment scripts")
        sys.exit(0)
    else:
        print("\n⚠️  WARNING! Some connections failed")
        print("\nTroubleshooting:")
        print("  - SnowSQL: Check installation and SSO authentication")
        print("  - Git: Verify you're in project directory")
        print("  - Snowpark: pip install snowflake-snowpark-python")
        print("\nSee QUICK_CONNECTION_GUIDE.md for detailed help")
        sys.exit(1)
