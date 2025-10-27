"""
Optimized Streamlit Apps Deployment to Snowflake
Uses single SSO session to avoid multiple browser authentications
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
    {
        "name": "Symantec",
        "title": "Symantec Endpoint Security Dashboard",
        "description": "Monitor endpoint protection coverage, health status, and critical security alerts",
        "priority": 1
    },
    {
        "name": "Trellix",
        "title": "Trellix Security Analytics",
        "description": "Comprehensive security monitoring and threat detection analytics",
        "priority": 1
    },
    {
        "name": "Crowdstrike",
        "title": "CrowdStrike Falcon Dashboard",
        "description": "Endpoint detection and response monitoring with threat intelligence",
        "priority": 1
    },
    {
        "name": "SentinelOne",
        "title": "SentinelOne Security Platform",
        "description": "Autonomous endpoint protection and response analytics",
        "priority": 2
    },
    {
        "name": "Sophos",
        "title": "Sophos Security Dashboard",
        "description": "Next-generation endpoint protection monitoring",
        "priority": 2
    },
    {
        "name": "Qualys",
        "title": "Qualys Vulnerability Management",
        "description": "Vulnerability assessment and compliance monitoring",
        "priority": 2
    },
    {
        "name": "Splunk",
        "title": "Splunk Security Analytics",
        "description": "Security information and event management analytics",
        "priority": 2
    },
    {
        "name": "Proofpoint",
        "title": "Proofpoint Email Security",
        "description": "Email threat protection and compliance monitoring",
        "priority": 3
    },
    {
        "name": "CybelAngel",
        "title": "CybelAngel Digital Risk Protection",
        "description": "External threat and data leak detection monitoring",
        "priority": 3
    },
    {
        "name": "Zerofox",
        "title": "ZeroFox Digital Risk Protection",
        "description": "Social media and digital asset threat monitoring",
        "priority": 3
    },
    {
        "name": "Zscaler",
        "title": "Zscaler Cloud Security",
        "description": "Cloud security and zero trust network access analytics",
        "priority": 3
    },
    {
        "name": "Cisco_AMP",
        "title": "Cisco Advanced Malware Protection",
        "description": "Advanced malware detection and threat intelligence",
        "priority": 3
    },
    {
        "name": "BitSight",
        "title": "BitSight Security Ratings",
        "description": "Security posture and third-party risk monitoring",
        "priority": 4
    },
    {
        "name": "Intel_Threats",
        "title": "Threat Intelligence Dashboard",
        "description": "Consolidated threat intelligence and IOC monitoring",
        "priority": 4
    },
    {
        "name": "ServiceNow",
        "title": "ServiceNow Security Operations",
        "description": "Security incident and vulnerability management tracking",
        "priority": 4
    },
    {
        "name": "Leviat",
        "title": "Leviat Security Analytics",
        "description": "Security analytics and monitoring dashboard",
        "priority": 4
    },
    {
        "name": "Ancon",
        "title": "Ancon Security Monitoring",
        "description": "Security monitoring and analytics platform",
        "priority": 4
    },
    {
        "name": "Tenable",
        "title": "Tenable Vulnerability Management",
        "description": "Vulnerability assessment and risk-based remediation",
        "priority": 4
    }
]

class OptimizedStreamlitDeployer:
    def __init__(self, config_file: Path, apps_dir: Path):
        self.config_file = config_file
        self.apps_dir = apps_dir
        self.config = None
        self.deployment_log = []

    def load_config(self):
        """Load Snowflake configuration"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_file}")

        with open(self.config_file, 'r') as f:
            self.config = json.load(f)

        print(f"✓ Configuration loaded")
        print(f"  Account: {self.config['account']}")
        print(f"  Database: {self.config['database']}")
        print(f"  Schema: {self.config['schema']}")
        print(f"  Warehouse: {self.config['warehouse']}")

    def check_app_exists(self, app_name: str) -> bool:
        """Check if app directory and streamlit_app.py exist"""
        app_dir = self.apps_dir / app_name
        app_file = app_dir / "streamlit_app.py"

        if not app_dir.exists():
            print(f"  ✗ App directory not found: {app_dir}")
            return False

        if not app_file.exists():
            print(f"  ✗ streamlit_app.py not found: {app_file}")
            return False

        return True

    def create_deployment_script(self, apps_to_deploy: list) -> Path:
        """Create a single SQL script file for batch deployment"""

        print("\n[Creating Deployment Script]")
        print("Generating SQL commands for all apps...")

        sql_commands = []

        # Create stage (if not exists)
        sql_commands.append("-- Create stage for Streamlit apps")
        sql_commands.append(f"CREATE STAGE IF NOT EXISTS STREAMLIT_APPS_STAGE")
        sql_commands.append(f"  DIRECTORY = (ENABLE = TRUE)")
        sql_commands.append(f"  COMMENT = 'Stage for SECURITY_ANALYTICS Streamlit applications';")
        sql_commands.append("")

        # For each app, generate PUT and CREATE commands
        for app in apps_to_deploy:
            app_name = app["name"]
            app_dir = self.apps_dir / app_name
            app_file = app_dir / "streamlit_app.py"

            # Convert Windows path to proper format for SnowSQL
            app_file_str = str(app_file).replace("\\", "/")

            sql_commands.append(f"-- Deploy {app_name}")

            # PUT command to upload file
            sql_commands.append(f"PUT 'file://{app_file_str}'")
            sql_commands.append(f"  @STREAMLIT_APPS_STAGE/{app_name}/")
            sql_commands.append(f"  OVERWRITE=TRUE")
            sql_commands.append(f"  AUTO_COMPRESS=FALSE;")
            sql_commands.append("")

            # DROP existing app
            streamlit_name = f"STREAMLIT_{app_name.upper()}"
            sql_commands.append(f"DROP STREAMLIT IF EXISTS {streamlit_name};")
            sql_commands.append("")

            # CREATE Streamlit app
            sql_commands.append(f"CREATE STREAMLIT {streamlit_name}")
            sql_commands.append(f"  ROOT_LOCATION = '@{self.config['database']}.{self.config['schema']}.STREAMLIT_APPS_STAGE/{app_name}'")
            sql_commands.append(f"  MAIN_FILE = 'streamlit_app.py'")
            sql_commands.append(f"  QUERY_WAREHOUSE = '{self.config['warehouse']}'")
            sql_commands.append(f"  TITLE = '{app['title']}'")
            sql_commands.append(f"  COMMENT = '{app['description']}';")
            sql_commands.append("")
            sql_commands.append("")

        # Write to temporary SQL file
        temp_dir = Path(tempfile.gettempdir())
        sql_file = temp_dir / f"streamlit_deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

        with open(sql_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_commands))

        print(f"✓ Deployment script created: {sql_file}")
        print(f"  Total commands: {len([cmd for cmd in sql_commands if cmd and not cmd.startswith('--')])} SQL statements")

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
            "-f", str(sql_file)  # Execute SQL file
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout for all deployments
            )

            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr

        except subprocess.TimeoutExpired:
            return False, "Deployment timeout - script took longer than 10 minutes"
        except Exception as e:
            return False, f"Deployment error: {str(e)}"

    def parse_deployment_results(self, output: str, apps_to_deploy: list) -> list:
        """Parse SnowSQL output to determine which apps deployed successfully"""

        results = []

        for app in apps_to_deploy:
            app_name = app["name"]
            streamlit_name = f"STREAMLIT_{app_name.upper()}"

            result = {
                "app_name": app_name,
                "success": False,
                "error": None
            }

            # Check if CREATE STREAMLIT command succeeded
            if f"{streamlit_name} successfully created" in output or \
               f"STREAMLIT {streamlit_name} successfully created" in output or \
               "successfully created" in output.lower():
                result["success"] = True
            elif "error" in output.lower() and app_name.lower() in output.lower():
                # Extract error message
                lines = output.split('\n')
                for i, line in enumerate(lines):
                    if app_name.lower() in line.lower() and 'error' in line.lower():
                        result["error"] = line.strip()
                        break
            else:
                # Assume success if no error found
                result["success"] = True

            results.append(result)

        return results

    def deploy_apps_batch(self, priority_filter: int = None) -> list:
        """Deploy apps in a single batch with one SSO authentication"""

        print("\n" + "="*70)
        print("STREAMLIT APPS DEPLOYMENT (OPTIMIZED)")
        print("="*70)

        # Filter apps by priority if specified
        apps_to_deploy = APPS
        if priority_filter:
            apps_to_deploy = [app for app in APPS if app["priority"] == priority_filter]
            print(f"\nDeploying Priority {priority_filter} apps: {len(apps_to_deploy)} apps")
        else:
            print(f"\nTotal apps to deploy: {len(apps_to_deploy)}")

        # Sort by priority
        apps_to_deploy = sorted(apps_to_deploy, key=lambda x: (x["priority"], x["name"]))

        # Show deployment plan
        print("\nDeployment Plan:")
        for i, app in enumerate(apps_to_deploy, 1):
            print(f"  {i}. {app['name']} (Priority {app['priority']})")

        input("\nPress Enter to start deployment (or Ctrl+C to cancel)...")

        # Check all app files exist
        print("\n[Step 1/4] Checking app files...")
        for app in apps_to_deploy:
            if not self.check_app_exists(app["name"]):
                print(f"✗ Aborting: {app['name']} files not found")
                return []
            print(f"  ✓ {app['name']}")

        # Create deployment script
        print("\n[Step 2/4] Creating deployment script...")
        sql_file = self.create_deployment_script(apps_to_deploy)

        # Execute deployment (SINGLE SSO authentication)
        print("\n[Step 3/4] Executing deployment...")
        start_time = time.time()

        success, output = self.execute_deployment_script(sql_file)

        duration = time.time() - start_time

        if not success:
            print(f"\n✗ Deployment failed!")
            print(f"Error: {output}")
            return []

        print(f"\n✓ Deployment script executed in {duration:.1f}s")

        # Parse results
        print("\n[Step 4/4] Parsing deployment results...")
        results = self.parse_deployment_results(output, apps_to_deploy)

        # Store results
        for i, result in enumerate(results):
            result["timestamp"] = datetime.now().isoformat()
            result["duration_seconds"] = round(duration / len(apps_to_deploy), 2)
            self.deployment_log.append(result)

        # Clean up temp file
        try:
            sql_file.unlink()
        except:
            pass

        return results

    def save_deployment_log(self):
        """Save deployment log to JSON file"""
        log_file = Path(__file__).parent.parent / f"deployment_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(log_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_apps": len(self.deployment_log),
                "successful": sum(1 for r in self.deployment_log if r["success"]),
                "failed": sum(1 for r in self.deployment_log if not r["success"]),
                "deployments": self.deployment_log
            }, f, indent=2)

        print(f"\n✓ Deployment log saved: {log_file}")
        return log_file

    def print_summary(self):
        """Print deployment summary"""
        print("\n" + "="*70)
        print("DEPLOYMENT SUMMARY")
        print("="*70)

        total = len(self.deployment_log)
        successful = sum(1 for r in self.deployment_log if r["success"])
        failed = total - successful

        print(f"\nTotal apps: {total}")
        print(f"Successful: {successful} ✓")
        print(f"Failed: {failed} ✗")

        if failed > 0:
            print("\nFailed deployments:")
            for result in self.deployment_log:
                if not result["success"]:
                    error_msg = result.get("error", "Unknown error")
                    print(f"  ✗ {result['app_name']}: {error_msg}")

        print("\nSuccessful deployments:")
        for result in self.deployment_log:
            if result["success"]:
                print(f"  ✓ {result['app_name']}")

def main():
    """Main deployment execution"""
    print("="*70)
    print("Streamlit Apps Deployment to Snowflake (OPTIMIZED)")
    print("="*70)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🚀 This optimized version uses a SINGLE SSO authentication")
    print("   No more browser popups for each step!")

    # Initialize deployer
    deployer = OptimizedStreamlitDeployer(CONFIG_FILE, APPS_DIR)

    # Load configuration
    print("\n[Loading Configuration]")
    try:
        deployer.load_config()
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return 1

    # Choose deployment mode
    print("\n" + "="*70)
    print("Deployment Options:")
    print("="*70)
    print("\n1. Deploy Priority 1 apps only (Symantec, Trellix, Crowdstrike)")
    print("2. Deploy Priority 2 apps only (SentinelOne, Sophos, Qualys, Splunk)")
    print("3. Deploy Priority 3 apps only (Proofpoint, CybelAngel, Zerofox, etc.)")
    print("4. Deploy Priority 4 apps only (BitSight, Intel_Threats, ServiceNow, etc.)")
    print("5. Deploy ALL apps (18 total)")

    choice = input("\nEnter your choice (1-5): ").strip()

    priority_map = {
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": None  # All apps
    }

    if choice not in priority_map:
        print("✗ Invalid choice. Aborting.")
        return 1

    # Deploy apps
    priority = priority_map[choice]
    results = deployer.deploy_apps_batch(priority_filter=priority)

    if not results:
        print("\n✗ Deployment failed or no apps deployed.")
        return 1

    # Save log
    deployer.save_deployment_log()

    # Print summary
    deployer.print_summary()

    # Next steps
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("\n1. Verify deployment:")
    print("   .\\verify_apps.bat")
    print("\n2. Test apps in Snowflake:")
    print("   - Login: https://app.snowflake.com")
    print("   - Navigate: Data → Streamlit")
    print("   - Test download buttons, alerts, refresh")
    print("\n3. Deploy remaining apps:")
    print("   .\\deploy_apps.bat")

    # Return success/failure
    failed = sum(1 for r in results if not r["success"])
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())
