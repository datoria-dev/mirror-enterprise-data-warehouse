"""
Verify Streamlit Apps Deployment
Checks which apps are deployed and accessible in Snowflake
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

# Configuration
SNOWSQL_PATH = r"C:\Program Files\Snowflake SnowSQL\snowsql.exe"
CONFIG_FILE = Path(__file__).parent.parent / "snowflake_config.json"

# Expected apps
EXPECTED_APPS = [
    "STREAMLIT_SYMANTEC",
    "STREAMLIT_TRELLIX",
    "STREAMLIT_CROWDSTRIKE",
    "STREAMLIT_SENTINELONE",
    "STREAMLIT_SOPHOS",
    "STREAMLIT_QUALYS",
    "STREAMLIT_SPLUNK",
    "STREAMLIT_PROOFPOINT",
    "STREAMLIT_CYBELANGEL",
    "STREAMLIT_ZEROFOX",
    "STREAMLIT_ZSCALER",
    "STREAMLIT_CISCO_AMP",
    "STREAMLIT_BITSIGHT",
    "STREAMLIT_INTEL_THREATS",
    "STREAMLIT_SERVICENOW",
    "STREAMLIT_LEVIAT",
    "STREAMLIT_ANCON",
    "STREAMLIT_TENABLE"
]

class DeploymentVerifier:
    def __init__(self, config_file: Path):
        self.config_file = config_file
        self.config = None

    def load_config(self):
        """Load Snowflake configuration"""
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)

    def execute_snowsql(self, query: str) -> tuple:
        """Execute SnowSQL query"""
        cmd = [
            SNOWSQL_PATH,
            "-a", self.config["account"],
            "-u", self.config["user"],
            "--authenticator", self.config["authenticator"],
            "-w", self.config["warehouse"],
            "-d", self.config["database"],
            "-s", self.config["schema"],
            "-r", self.config["role"],
            "-q", query,
            "-o", "output_format=json"
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

    def get_deployed_streamlit_apps(self) -> list:
        """Get list of deployed Streamlit apps"""
        query = "SHOW STREAMLITS;"

        success, output = self.execute_snowsql(query)

        if not success:
            print(f"✗ Failed to get Streamlit apps: {output}")
            return []

        # Parse output to get app names
        deployed_apps = []
        for line in output.split('\n'):
            if 'STREAMLIT_' in line:
                # Extract app name from output
                for expected_app in EXPECTED_APPS:
                    if expected_app in line:
                        deployed_apps.append(expected_app)

        return deployed_apps

    def verify_deployments(self):
        """Verify all expected apps are deployed"""
        print("="*70)
        print("STREAMLIT APPS DEPLOYMENT VERIFICATION")
        print("="*70)
        print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        print("\n[Loading Configuration]")
        self.load_config()
        print(f"✓ Configuration loaded")
        print(f"  Database: {self.config['database']}")
        print(f"  Schema: {self.config['schema']}")

        print("\n[Checking Deployed Apps]")
        deployed_apps = self.get_deployed_streamlit_apps()

        if not deployed_apps:
            print("✗ No Streamlit apps found or query failed")
            return

        print(f"✓ Found {len(deployed_apps)} deployed Streamlit apps")

        # Compare with expected apps
        print("\n" + "="*70)
        print("DEPLOYMENT STATUS")
        print("="*70)

        deployed_set = set(deployed_apps)
        expected_set = set(EXPECTED_APPS)

        deployed_count = 0
        missing_count = 0

        for app in EXPECTED_APPS:
            app_short_name = app.replace("STREAMLIT_", "")

            if app in deployed_set:
                print(f"  ✓ {app_short_name}")
                deployed_count += 1
            else:
                print(f"  ✗ {app_short_name} (NOT DEPLOYED)")
                missing_count += 1

        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"\nExpected apps: {len(EXPECTED_APPS)}")
        print(f"Deployed: {deployed_count} ✓")
        print(f"Missing: {missing_count} ✗")

        completion_pct = (deployed_count / len(EXPECTED_APPS)) * 100
        print(f"\nDeployment completion: {completion_pct:.1f}%")

        if missing_count == 0:
            print("\n✓ All apps successfully deployed!")
        else:
            print(f"\n⚠ {missing_count} apps still need to be deployed")

        # Show next steps
        if missing_count > 0:
            print("\n" + "="*70)
            print("NEXT STEPS")
            print("="*70)
            print("\nTo deploy missing apps, run:")
            print("  python 02_PYTHON_SCRIPTS\\deploy_streamlit_apps.py")
            print("\nor use the batch file:")
            print("  .\\deploy_apps.bat")

def main():
    """Main verification execution"""
    verifier = DeploymentVerifier(CONFIG_FILE)
    verifier.verify_deployments()

if __name__ == "__main__":
    main()
