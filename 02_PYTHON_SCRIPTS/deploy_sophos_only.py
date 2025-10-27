"""
Deploy Sophos App Only - Quick Test Deployment
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Configuration
CONFIG_FILE = Path(__file__).parent.parent / "snowflake_config.json"
APPS_DIR = Path(__file__).parent.parent / "13_STREAMLIT_COMPLETE"
APP_NAME = "Sophos"
LOG_DIR = Path(__file__).parent.parent / "deployment_logs"

def load_config():
    """Load Snowflake configuration"""
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def create_deployment_sql(config):
    """Create SQL deployment script"""

    app_dir = APPS_DIR / APP_NAME
    streamlit_file = app_dir / "streamlit_app.py"
    env_file = app_dir / "environment.yml"

    if not streamlit_file.exists():
        raise FileNotFoundError(f"streamlit_app.py not found: {streamlit_file}")
    if not env_file.exists():
        raise FileNotFoundError(f"environment.yml not found: {env_file}")

    # Convert paths to Windows format for SnowSQL
    streamlit_path = str(streamlit_file.absolute()).replace('\\', '/')
    env_path = str(env_file.absolute()).replace('\\', '/')

    sql_commands = [
        f"-- Deploy {APP_NAME} App Only",
        f"-- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "USE ROLE DEV_DEVELOPER;",
        f"USE WAREHOUSE {config['warehouse']};",
        f"USE DATABASE {config['database']};",
        f"USE SCHEMA {config['schema']};",
        "",
        "-- Create stage if not exists",
        "CREATE STAGE IF NOT EXISTS STREAMLIT_APPS_STAGE;",
        "",
        f"-- Upload {APP_NAME} files",
        f"PUT 'file://{streamlit_path}' @STREAMLIT_APPS_STAGE/{APP_NAME}/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;",
        f"PUT 'file://{env_path}' @STREAMLIT_APPS_STAGE/{APP_NAME}/ OVERWRITE=TRUE AUTO_COMPRESS=FALSE;",
        "",
        f"-- Verify files uploaded",
        f"LIST @STREAMLIT_APPS_STAGE/{APP_NAME}/;",
        "",
        f"-- Drop and recreate {APP_NAME} app",
        f"DROP STREAMLIT IF EXISTS STREAMLIT_{APP_NAME.upper()};",
        "",
        f"CREATE STREAMLIT STREAMLIT_{APP_NAME.upper()}",
        f"  ROOT_LOCATION = '@{config['database']}.{config['schema']}.STREAMLIT_APPS_STAGE'",
        f"  MAIN_FILE = '/{APP_NAME}/streamlit_app.py'",
        f"  QUERY_WAREHOUSE = '{config['warehouse']}'",
        f"  TITLE = '{APP_NAME} Security Dashboard';",
        "",
        f"SELECT '{APP_NAME} deployed successfully at ' || CURRENT_TIMESTAMP() AS STATUS;",
    ]

    return '\n'.join(sql_commands)

def deploy():
    """Execute deployment"""

    print("="*70)
    print(f"DEPLOY {APP_NAME} APP ONLY")
    print("="*70)
    print()

    # Load config
    print("[1/4] Loading configuration...")
    config = load_config()
    print(f"      Database: {config['database']}")
    print(f"      Schema: {config['schema']}")
    print(f"      Warehouse: {config['warehouse']}")
    print()

    # Create SQL script
    print("[2/4] Creating deployment SQL script...")
    sql_script = create_deployment_sql(config)

    # Save SQL script
    LOG_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    sql_file = LOG_DIR / f"deploy_{APP_NAME.lower()}_{timestamp}.sql"

    with open(sql_file, 'w') as f:
        f.write(sql_script)

    print(f"      SQL script saved: {sql_file}")
    print()

    # Execute deployment
    print("[3/4] Executing deployment...")
    print("      NOTE: Browser will open for SSO authentication (Okta)")
    print()

    snowsql_cmd = [
        r"C:\Program Files\Snowflake SnowSQL\snowsql.exe",
        "-a", "GenericCorp-CRH_EDW",
        "-u", config['user'],
        "--authenticator", "externalbrowser",
        "-f", str(sql_file)
    ]

    try:
        result = subprocess.run(
            snowsql_cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )

        # Save output
        log_file = LOG_DIR / f"deploy_{APP_NAME.lower()}_{timestamp}.log"
        with open(log_file, 'w') as f:
            f.write("=== STDOUT ===\n")
            f.write(result.stdout)
            f.write("\n\n=== STDERR ===\n")
            f.write(result.stderr)

        print(f"      Log saved: {log_file}")
        print()

        # Check result
        if result.returncode == 0:
            print("[4/4] Deployment Status: SUCCESS")
            print()
            print("="*70)
            print("DEPLOYMENT COMPLETE!")
            print("="*70)
            print()
            print(f"App deployed: STREAMLIT_{APP_NAME.upper()}")
            print(f"Location: {config['database']}.{config['schema']}")
            print()
            print("Next Steps:")
            print("1. Go to Snowflake UI")
            print(f"2. Navigate to {config['database']} -> {config['schema']} -> Streamlit")
            print(f"3. Open STREAMLIT_{APP_NAME.upper()}")
            print("4. Test:")
            print("   - Add/remove filters and refresh (no np.random errors)")
            print("   - Click download button (should download CSV)")
            print()
            return 0
        else:
            print("[4/4] Deployment Status: FAILED")
            print()
            print("="*70)
            print("DEPLOYMENT FAILED!")
            print("="*70)
            print()
            print("Error output:")
            print(result.stderr)
            print()
            print(f"Check log file for details: {log_file}")
            return 1

    except subprocess.TimeoutExpired:
        print("[4/4] Deployment Status: TIMEOUT")
        print()
        print("Deployment timed out after 5 minutes")
        return 1
    except Exception as e:
        print(f"[4/4] Deployment Status: ERROR")
        print()
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    exit(deploy())
