"""
Fixed Streamlit Apps Deployment to Snowflake
Deploys to DEV_REPORTING.SECURITY_ANALYTICS with both streamlit_app.py and environment.yml
Uses single SSO session
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime
import time
import tempfile

# Configuration
SNOWSQL_PATH = r"C:\Program Files\Snowflake SnowSQL\snowsql.exe"
CONFIG_FILE = Path(__file__).parent.parent / "snowflake_config.json"
APPS_DIR = Path(__file__).parent.parent / "13_STREAMLIT_COMPLETE"

# App configurations
APPS = [
    {"name": "Symantec", "title": "Symantec Endpoint Security Dashboard", "priority": 1},
    {"name": "Trellix", "title": "Trellix Security Analytics", "priority": 1},
    {"name": "Crowdstrike", "title": "CrowdStrike Falcon Dashboard", "priority": 1},
    {"name": "SentinelOne", "title": "SentinelOne Security Platform", "priority": 2},
    {"name": "Sophos", "title": "Sophos Security Dashboard", "priority": 2},
    {"name": "Qualys", "title": "Qualys Vulnerability Management", "priority": 2},
    {"name": "Splunk", "title": "Splunk Security Analytics", "priority": 2},
    {"name": "Proofpoint", "title": "Proofpoint Email Security", "priority": 3},
    {"name": "CybelAngel", "title": "CybelAngel Digital Risk Protection", "priority": 3},
    {"name": "Zerofox", "title": "ZeroFox Digital Risk Protection", "priority": 3},
    {"name": "Zscaler", "title": "Zscaler Cloud Security", "priority": 3},
    {"name": "Cisco_AMP", "title": "Cisco Advanced Malware Protection", "priority": 3},
    {"name": "BitSight", "title": "BitSight Security Ratings", "priority": 4},
    {"name": "Intel_Threats", "title": "Threat Intelligence Dashboard", "priority": 4},
    {"name": "ServiceNow", "title": "ServiceNow Security Operations", "priority": 4},
    {"name": "Leviat", "title": "Leviat Security Analytics", "priority": 4},
    {"name": "Ancon", "title": "Ancon Security Monitoring", "priority": 4},
    {"name": "Tenable", "title": "Tenable Vulnerability Management", "priority": 4}
]

class FixedStreamlitDeployer:
    def __init__(self, config_file: Path, apps_dir: Path):
        self.config_file = config_file
        self.apps_dir = apps_dir
        self.config = None
        self.deployment_log = []

    def load_config(self):
        """Load Snowflake configuration"""
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)

        print(f"✓ Configuration loaded")
        print(f"  Account: {self.config['account']}")
        print(f"  Database: {self.config['database']}")
        print(f"  Schema: {self.config['schema']}")
        print(f"  Warehouse: {self.config['warehouse']}")

    def check_app_files(self, app_name: str) -> dict:
        """Check if app files exist"""
        app_dir = self.apps_dir / app_name

        files = {
            "streamlit_app": app_dir / "streamlit_app.py",
            "environment": app_dir / "environment.yml"
        }

        result = {"exists": True, "missing": []}

        for file_type, file_path in files.items():
            if not file_path.exists():
                result["exists"] = False
                result["missing"].append(file_type)

        return result

    def create_deployment_script(self, apps_to_deploy: list) -> Path:
        """Create SQL script for batch deployment with BOTH files"""

        print("\n[Creating Deployment Script]")
        print("Generating SQL commands for all apps...")

        sql_commands = []

        # Create stage
        sql_commands.append("-- Create stage for Streamlit apps")
        sql_commands.append(f"CREATE STAGE IF NOT EXISTS STREAMLIT_APPS_STAGE")
        sql_commands.append(f"  DIRECTORY = (ENABLE = TRUE)")
        sql_commands.append(f"  COMMENT = 'Stage for SECURITY_ANALYTICS Streamlit applications';")
        sql_commands.append("")

        # Deploy each app
        for app in apps_to_deploy:
            app_name = app["name"]
            app_dir = self.apps_dir / app_name

            sql_commands.append(f"-- Deploy {app_name}")
            sql_commands.append("")

            # Upload streamlit_app.py
            streamlit_file = str(app_dir / "streamlit_app.py").replace("\\", "/")
            sql_commands.append(f"PUT 'file://{streamlit_file}'")
            sql_commands.append(f"  @STREAMLIT_APPS_STAGE/{app_name}/")
            sql_commands.append(f"  OVERWRITE=TRUE")
            sql_commands.append(f"  AUTO_COMPRESS=FALSE;")
            sql_commands.append("")

            # Upload environment.yml
            env_file = str(app_dir / "environment.yml").replace("\\", "/")
            sql_commands.append(f"PUT 'file://{env_file}'")
            sql_commands.append(f"  @STREAMLIT_APPS_STAGE/{app_name}/")
            sql_commands.append(f"  OVERWRITE=TRUE")
            sql_commands.append(f"  AUTO_COMPRESS=FALSE;")
            sql_commands.append("")

            # Drop existing app
            streamlit_name = f"STREAMLIT_{app_name.upper()}"
            sql_commands.append(f"DROP STREAMLIT IF EXISTS {streamlit_name};")
            sql_commands.append("")

            # Create Streamlit app
            sql_commands.append(f"CREATE STREAMLIT {streamlit_name}")
            sql_commands.append(f"  ROOT_LOCATION = '@{self.config['database']}.{self.config['schema']}.STREAMLIT_APPS_STAGE/{app_name}'")
            sql_commands.append(f"  MAIN_FILE = 'streamlit_app.py'")
            sql_commands.append(f"  QUERY_WAREHOUSE = '{self.config['warehouse']}'")
            sql_commands.append(f"  TITLE = '{app['title']}';")
            sql_commands.append("")
            sql_commands.append("")

        # Write to temp SQL file
        temp_dir = Path(tempfile.gettempdir())
        sql_file = temp_dir / f"streamlit_deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

        with open(sql_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_commands))

        print(f"✓ Deployment script created: {sql_file.name}")
        print(f"  Apps: {len(apps_to_deploy)}")
        print(f"  Files per app: 2 (streamlit_app.py + environment.yml)")
        print(f"  Total files to upload: {len(apps_to_deploy) * 2}")

        return sql_file

    def execute_deployment_script(self, sql_file: Path) -> tuple:
        """Execute deployment script with SINGLE SSO authentication"""

        print("\n[Executing Deployment]")
        print("⏳ Opening browser for SSO authentication...")
        print("   (You will authenticate ONCE for all deployments)")
        print("")

        cmd = [
            SNOWSQL_PATH,
            "-a", self.config["account"],
            "-u", self.config["user"],
            "--authenticator", self.config["authenticator"],
            "-w", self.config["warehouse"],
            "-d", self.config["database"],
            "-s", self.config["schema"],
            "-r", self.config["role"],
            "-f", str(sql_file)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr

        except subprocess.TimeoutExpired:
            return False, "Deployment timeout"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def parse_deployment_results(self, output: str, apps_to_deploy: list) -> list:
        """Parse deployment output"""
        results = []

        for app in apps_to_deploy:
            app_name = app["name"]
            streamlit_name = f"STREAMLIT_{app_name.upper()}"

            # Check for successful creation
            success = False
            if f"{streamlit_name} successfully created" in output:
                success = True
            elif "successfully created" in output.lower() and app_name.lower() in output.lower():
                success = True

            results.append({
                "app_name": app_name,
                "streamlit_name": streamlit_name,
                "success": success,
                "timestamp": datetime.now().isoformat()
            })

        return results

    def deploy_apps_batch(self, priority_filter: int = None) -> list:
        """Deploy apps in batch"""

        print("\n" + "="*70)
        print("STREAMLIT APPS DEPLOYMENT (FIXED)")
        print("="*70)
        print(f"\n✓ Database: {self.config['database']}")
        print(f"✓ Schema: {self.config['schema']}")
        print(f"✓ Files: streamlit_app.py + environment.yml")

        # Filter apps
        apps_to_deploy = APPS
        if priority_filter:
            apps_to_deploy = [app for app in APPS if app["priority"] == priority_filter]
            print(f"\nDeploying Priority {priority_filter} apps: {len(apps_to_deploy)} apps")
        else:
            print(f"\nTotal apps to deploy: {len(apps_to_deploy)}")

        apps_to_deploy = sorted(apps_to_deploy, key=lambda x: (x["priority"], x["name"]))

        # Show plan
        print("\nDeployment Plan:")
        for i, app in enumerate(apps_to_deploy, 1):
            print(f"  {i}. {app['name']} (Priority {app['priority']})")

        input("\nPress Enter to start deployment (or Ctrl+C to cancel)...")

        # Check files
        print("\n[Step 1/4] Checking app files...")
        all_files_ok = True
        for app in apps_to_deploy:
            check = self.check_app_files(app["name"])
            if check["exists"]:
                print(f"  ✓ {app['name']} (streamlit_app.py + environment.yml)")
            else:
                print(f"  ✗ {app['name']} - Missing: {', '.join(check['missing'])}")
                all_files_ok = False

        if not all_files_ok:
            print("\n✗ Some files are missing. Aborting deployment.")
            return []

        # Create script
        print("\n[Step 2/4] Creating deployment script...")
        sql_file = self.create_deployment_script(apps_to_deploy)

        # Execute
        print("\n[Step 3/4] Executing deployment...")
        start_time = time.time()

        success, output = self.execute_deployment_script(sql_file)
        duration = time.time() - start_time

        if not success:
            print(f"\n✗ Deployment failed!")
            print(f"Error: {output}")
            return []

        print(f"\n✓ Deployment executed in {duration:.1f}s")

        # Parse results
        print("\n[Step 4/4] Parsing results...")
        results = self.parse_deployment_results(output, apps_to_deploy)

        for result in results:
            result["duration_seconds"] = round(duration / len(apps_to_deploy), 2)
            self.deployment_log.append(result)

        # Cleanup
        try:
            sql_file.unlink()
        except:
            pass

        return results

    def save_deployment_log(self):
        """Save deployment log"""
        log_file = Path(__file__).parent.parent / f"deployment_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(log_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "database": self.config["database"],
                "schema": self.config["schema"],
                "total_apps": len(self.deployment_log),
                "successful": sum(1 for r in self.deployment_log if r["success"]),
                "failed": sum(1 for r in self.deployment_log if not r["success"]),
                "deployments": self.deployment_log
            }, f, indent=2)

        print(f"\n✓ Deployment log saved: {log_file.name}")

    def print_summary(self):
        """Print summary"""
        print("\n" + "="*70)
        print("DEPLOYMENT SUMMARY")
        print("="*70)

        total = len(self.deployment_log)
        successful = sum(1 for r in self.deployment_log if r["success"])
        failed = total - successful

        print(f"\nDatabase: {self.config['database']}")
        print(f"Schema: {self.config['schema']}")
        print(f"\nTotal apps: {total}")
        print(f"Successful: {successful} ✓")
        print(f"Failed: {failed} ✗")

        if failed > 0:
            print("\nFailed deployments:")
            for result in self.deployment_log:
                if not result["success"]:
                    print(f"  ✗ {result['app_name']}")

        print("\nSuccessful deployments:")
        for result in self.deployment_log:
            if result["success"]:
                print(f"  ✓ {result['streamlit_name']}")

def main():
    """Main execution"""
    print("="*70)
    print("Streamlit Apps Deployment (FIXED)")
    print("="*70)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n✓ Deploys to: DEV_REPORTING.SECURITY_ANALYTICS")
    print("✓ Uploads: streamlit_app.py + environment.yml")
    print("✓ Single SSO authentication")

    deployer = FixedStreamlitDeployer(CONFIG_FILE, APPS_DIR)

    print("\n[Loading Configuration]")
    try:
        deployer.load_config()
    except Exception as e:
        print(f"✗ Failed: {e}")
        return 1

    # Deployment options
    print("\n" + "="*70)
    print("Deployment Options:")
    print("="*70)
    print("\n1. Deploy Priority 1 apps (Symantec, Trellix, Crowdstrike)")
    print("2. Deploy Priority 2 apps (SentinelOne, Sophos, Qualys, Splunk)")
    print("3. Deploy Priority 3 apps (Proofpoint, CybelAngel, Zerofox, etc.)")
    print("4. Deploy Priority 4 apps (BitSight, Intel_Threats, ServiceNow, etc.)")
    print("5. Deploy ALL apps (18 total)")

    choice = input("\nEnter your choice (1-5): ").strip()

    priority_map = {"1": 1, "2": 2, "3": 3, "4": 4, "5": None}

    if choice not in priority_map:
        print("✗ Invalid choice")
        return 1

    # Deploy
    results = deployer.deploy_apps_batch(priority_filter=priority_map[choice])

    if not results:
        return 1

    deployer.save_deployment_log()
    deployer.print_summary()

    # Next steps
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("\n1. Verify deployment:")
    print("   .\\verify_apps.bat")
    print("\n2. Test in Snowflake:")
    print("   Database: DEV_REPORTING")
    print("   Schema: SECURITY_ANALYTICS")
    print("   Apps: Data → Streamlit")

    failed = sum(1 for r in results if not r["success"])
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())
