"""
Automated Streamlit Apps Deployment to Snowflake
Deploys all 18 SECURITY_ANALYTICS Streamlit apps to Snowflake using SnowSQL
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime
import time

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
        "priority": 1  # Deploy first for testing
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

class StreamlitDeployer:
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

    def execute_snowsql(self, query: str, description: str = "") -> tuple:
        """Execute SnowSQL query"""
        if description:
            print(f"  {description}...")

        cmd = [
            SNOWSQL_PATH,
            "-a", self.config["account"],
            "-u", self.config["user"],
            "--authenticator", self.config["authenticator"],
            "-w", self.config["warehouse"],
            "-d", self.config["database"],
            "-s", self.config["schema"],
            "-r", self.config["role"],
            "-q", query
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr

        except subprocess.TimeoutExpired:
            return False, "Query timeout"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def create_stage(self) -> bool:
        """Create Snowflake stage for Streamlit apps"""
        print("\n[Creating Snowflake Stage]")

        stage_name = "STREAMLIT_APPS_STAGE"

        # Check if stage exists
        check_query = f"SHOW STAGES LIKE '{stage_name}';"
        success, output = self.execute_snowsql(check_query, "Checking for existing stage")

        if success and stage_name in output:
            print(f"  ✓ Stage already exists: {stage_name}")
            return True

        # Create stage
        create_query = f"""
        CREATE STAGE IF NOT EXISTS {stage_name}
        DIRECTORY = (ENABLE = TRUE)
        COMMENT = 'Stage for SECURITY_ANALYTICS Streamlit applications';
        """

        success, output = self.execute_snowsql(create_query, "Creating stage")

        if success:
            print(f"  ✓ Stage created: {stage_name}")
            return True
        else:
            print(f"  ✗ Failed to create stage: {output}")
            return False

    def upload_app(self, app_name: str) -> bool:
        """Upload streamlit_app.py to Snowflake stage"""
        app_dir = self.apps_dir / app_name
        app_file = app_dir / "streamlit_app.py"

        # Convert Windows path to proper format for SnowSQL
        app_file_str = str(app_file).replace("\\", "/")

        # PUT command to upload file
        put_query = f"""
        PUT 'file://{app_file_str}'
        @STREAMLIT_APPS_STAGE/{app_name}/
        OVERWRITE=TRUE
        AUTO_COMPRESS=FALSE;
        """

        success, output = self.execute_snowsql(put_query, f"Uploading {app_name}/streamlit_app.py")

        if success:
            print(f"    ✓ File uploaded successfully")
            return True
        else:
            print(f"    ✗ Upload failed: {output}")
            return False

    def deploy_app(self, app_info: dict) -> dict:
        """Deploy a single Streamlit app to Snowflake"""
        app_name = app_info["name"]
        start_time = time.time()

        print(f"\n{'='*70}")
        print(f"Deploying: {app_name}")
        print(f"{'='*70}")

        result = {
            "app_name": app_name,
            "start_time": datetime.now().isoformat(),
            "success": False,
            "steps": {},
            "error": None
        }

        # Step 1: Check app exists
        print(f"\n[Step 1/4] Checking app files...")
        if not self.check_app_exists(app_name):
            result["error"] = "App files not found"
            return result

        print(f"  ✓ App files found")
        result["steps"]["check_files"] = True

        # Step 2: Upload app
        print(f"\n[Step 2/4] Uploading to Snowflake stage...")
        if not self.upload_app(app_name):
            result["error"] = "Upload failed"
            return result

        result["steps"]["upload"] = True

        # Step 3: Drop existing app (if exists)
        print(f"\n[Step 3/4] Checking for existing Streamlit app...")
        streamlit_name = f"STREAMLIT_{app_name.upper()}"

        drop_query = f"DROP STREAMLIT IF EXISTS {streamlit_name};"
        success, output = self.execute_snowsql(drop_query, "Dropping existing app")

        if success:
            print(f"  ✓ Ready to create app")

        result["steps"]["drop_existing"] = True

        # Step 4: Create Streamlit app
        print(f"\n[Step 4/4] Creating Streamlit app...")

        create_query = f"""
        CREATE STREAMLIT {streamlit_name}
        ROOT_LOCATION = '@{self.config['database']}.{self.config['schema']}.STREAMLIT_APPS_STAGE/{app_name}'
        MAIN_FILE = 'streamlit_app.py'
        QUERY_WAREHOUSE = '{self.config['warehouse']}'
        TITLE = '{app_info['title']}'
        COMMENT = '{app_info['description']}';
        """

        success, output = self.execute_snowsql(create_query, "Creating Streamlit app")

        if success:
            print(f"  ✓ Streamlit app created: {streamlit_name}")
            result["steps"]["create_app"] = True
            result["success"] = True
        else:
            print(f"  ✗ Failed to create app: {output}")
            result["error"] = f"Create failed: {output}"

        # Calculate duration
        duration = time.time() - start_time
        result["duration_seconds"] = round(duration, 2)
        result["end_time"] = datetime.now().isoformat()

        if result["success"]:
            print(f"\n{'='*70}")
            print(f"✓ {app_name} deployed successfully in {duration:.1f}s")
            print(f"{'='*70}")
        else:
            print(f"\n{'='*70}")
            print(f"✗ {app_name} deployment failed")
            print(f"{'='*70}")

        return result

    def deploy_all_apps(self, priority_filter: int = None) -> list:
        """Deploy all apps or filter by priority"""
        print("\n" + "="*70)
        print("STREAMLIT APPS DEPLOYMENT")
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

        # Deploy each app
        results = []
        for app in apps_to_deploy:
            result = self.deploy_app(app)
            results.append(result)
            self.deployment_log.append(result)

            # Pause between deployments
            if app != apps_to_deploy[-1]:  # Not last app
                print("\nWaiting 3 seconds before next deployment...")
                time.sleep(3)

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
                    print(f"  ✗ {result['app_name']}: {result['error']}")

        print("\nSuccessful deployments:")
        for result in self.deployment_log:
            if result["success"]:
                print(f"  ✓ {result['app_name']} ({result['duration_seconds']}s)")

def main():
    """Main deployment execution"""
    print("="*70)
    print("Streamlit Apps Deployment to Snowflake")
    print("="*70)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize deployer
    deployer = StreamlitDeployer(CONFIG_FILE, APPS_DIR)

    # Load configuration
    print("\n[Loading Configuration]")
    try:
        deployer.load_config()
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return 1

    # Create stage
    if not deployer.create_stage():
        print("\n✗ Failed to create stage. Deployment aborted.")
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
    results = deployer.deploy_all_apps(priority_filter=priority)

    # Save log
    deployer.save_deployment_log()

    # Print summary
    deployer.print_summary()

    # Return success/failure
    failed = sum(1 for r in results if not r["success"])
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())
