"""
Streamlit Apps Deployment with Progress Tracking and Detailed Logging
Deploys to DEV_REPORTING.SECURITY_ANALYTICS with real-time progress and comprehensive logs
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime
import time
import tempfile
import threading
import sys

# Configuration
SNOWSQL_PATH = r"C:\Program Files\Snowflake SnowSQL\snowsql.exe"
CONFIG_FILE = Path(__file__).parent.parent / "snowflake_config.json"
APPS_DIR = Path(__file__).parent.parent / "13_STREAMLIT_COMPLETE"
LOGS_DIR = Path(__file__).parent.parent / "deployment_logs"

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

class DeploymentLogger:
    """Handles all logging operations"""

    def __init__(self, logs_dir: Path):
        self.logs_dir = logs_dir
        self.logs_dir.mkdir(exist_ok=True)

        # Create timestamped log files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = self.logs_dir / f"deployment_{timestamp}.log"
        self.json_file = self.logs_dir / f"deployment_{timestamp}.json"
        self.sql_file = self.logs_dir / f"deployment_{timestamp}.sql"

        # Log data
        self.log_entries = []
        self.deployment_data = {
            "start_time": datetime.now().isoformat(),
            "config": {},
            "apps": [],
            "steps": [],
            "summary": {}
        }

    def log(self, message: str, level: str = "INFO"):
        """Write to console and log file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"

        # Print to console
        print(message)

        # Write to log file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')

        # Store in memory
        self.log_entries.append({
            "timestamp": timestamp,
            "level": level,
            "message": message
        })

    def log_step(self, step_name: str, status: str, details: dict = None):
        """Log a deployment step"""
        step = {
            "step": step_name,
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "details": details or {}
        }
        self.deployment_data["steps"].append(step)

    def save_json(self):
        """Save deployment data as JSON"""
        self.deployment_data["end_time"] = datetime.now().isoformat()
        self.deployment_data["logs"] = self.log_entries

        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.deployment_data, f, indent=2)

        self.log(f"✓ JSON log saved: {self.json_file.name}")

    def save_sql_script(self, sql_content: str):
        """Save SQL script for reference"""
        with open(self.sql_file, 'w', encoding='utf-8') as f:
            f.write(sql_content)

        self.log(f"✓ SQL script saved: {self.sql_file.name}")

class ProgressIndicator:
    """Animated progress indicator"""

    def __init__(self):
        self.running = False
        self.thread = None
        self.current_step = ""
        self.counter = 0

    def start(self, step_name: str):
        """Start progress animation"""
        self.current_step = step_name
        self.counter = 0
        self.running = True
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """Stop progress animation"""
        self.running = False
        if self.thread:
            self.thread.join()
        sys.stdout.write('\r' + ' ' * 100 + '\r')
        sys.stdout.flush()

    def _animate(self):
        """Animation loop"""
        spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        idx = 0

        while self.running:
            sys.stdout.write(f'\r{spinner[idx]} {self.current_step} ({self.counter}s)')
            sys.stdout.flush()
            idx = (idx + 1) % len(spinner)
            self.counter += 1
            time.sleep(1)

class EnhancedDeployer:
    """Streamlit deployer with progress tracking and logging"""

    def __init__(self, config_file: Path, apps_dir: Path):
        self.config_file = config_file
        self.apps_dir = apps_dir
        self.config = None
        self.logger = DeploymentLogger(LOGS_DIR)
        self.progress = ProgressIndicator()

    def load_config(self):
        """Load Snowflake configuration"""
        self.logger.log("Loading configuration...", "INFO")

        with open(self.config_file, 'r') as f:
            self.config = json.load(f)

        self.logger.deployment_data["config"] = self.config

        self.logger.log(f"✓ Configuration loaded", "SUCCESS")
        self.logger.log(f"  Account: {self.config['account']}")
        self.logger.log(f"  Database: {self.config['database']}")
        self.logger.log(f"  Schema: {self.config['schema']}")
        self.logger.log(f"  Warehouse: {self.config['warehouse']}")

        self.logger.log_step("load_config", "SUCCESS", self.config)

    def check_app_files(self, app_name: str) -> dict:
        """Check if app files exist"""
        app_dir = self.apps_dir / app_name

        files = {
            "streamlit_app": app_dir / "streamlit_app.py",
            "environment": app_dir / "environment.yml"
        }

        result = {"exists": True, "missing": [], "files": {}}

        for file_type, file_path in files.items():
            if file_path.exists():
                result["files"][file_type] = {
                    "path": str(file_path),
                    "size": file_path.stat().st_size
                }
            else:
                result["exists"] = False
                result["missing"].append(file_type)

        return result

    def create_deployment_script(self, apps_to_deploy: list) -> tuple:
        """Create SQL script for deployment"""

        self.logger.log("\n[Creating Deployment Script]", "INFO")
        self.logger.log("Generating SQL commands...", "INFO")

        sql_commands = []

        # Header
        sql_commands.append("-- ================================================================")
        sql_commands.append("-- Streamlit Apps Deployment Script")
        sql_commands.append(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sql_commands.append(f"-- Database: {self.config['database']}")
        sql_commands.append(f"-- Schema: {self.config['schema']}")
        sql_commands.append(f"-- Apps: {len(apps_to_deploy)}")
        sql_commands.append("-- ================================================================")
        sql_commands.append("")

        # Create stage
        sql_commands.append("-- Create stage for Streamlit apps")
        sql_commands.append(f"CREATE STAGE IF NOT EXISTS STREAMLIT_APPS_STAGE")
        sql_commands.append(f"  DIRECTORY = (ENABLE = TRUE)")
        sql_commands.append(f"  COMMENT = 'Stage for SECURITY_ANALYTICS Streamlit applications';")
        sql_commands.append("")

        # Deploy each app
        for i, app in enumerate(apps_to_deploy, 1):
            app_name = app["name"]
            app_dir = self.apps_dir / app_name

            sql_commands.append(f"-- ================================================================")
            sql_commands.append(f"-- App {i}/{len(apps_to_deploy)}: {app_name}")
            sql_commands.append(f"-- ================================================================")
            sql_commands.append("")

            # Upload streamlit_app.py
            streamlit_file = str(app_dir / "streamlit_app.py").replace("\\", "/")
            sql_commands.append(f"-- Upload streamlit_app.py")
            sql_commands.append(f"PUT 'file://{streamlit_file}'")
            sql_commands.append(f"  @STREAMLIT_APPS_STAGE/{app_name}/")
            sql_commands.append(f"  OVERWRITE=TRUE")
            sql_commands.append(f"  AUTO_COMPRESS=FALSE;")
            sql_commands.append("")

            # Upload environment.yml
            env_file = str(app_dir / "environment.yml").replace("\\", "/")
            sql_commands.append(f"-- Upload environment.yml")
            sql_commands.append(f"PUT 'file://{env_file}'")
            sql_commands.append(f"  @STREAMLIT_APPS_STAGE/{app_name}/")
            sql_commands.append(f"  OVERWRITE=TRUE")
            sql_commands.append(f"  AUTO_COMPRESS=FALSE;")
            sql_commands.append("")

            # Drop existing app
            streamlit_name = f"STREAMLIT_{app_name.upper()}"
            sql_commands.append(f"-- Drop existing app (if exists)")
            sql_commands.append(f"DROP STREAMLIT IF EXISTS {streamlit_name};")
            sql_commands.append("")

            # Create Streamlit app
            sql_commands.append(f"-- Create Streamlit app")
            sql_commands.append(f"CREATE STREAMLIT {streamlit_name}")
            sql_commands.append(f"  ROOT_LOCATION = '@{self.config['database']}.{self.config['schema']}.STREAMLIT_APPS_STAGE/{app_name}'")
            sql_commands.append(f"  MAIN_FILE = 'streamlit_app.py'")
            sql_commands.append(f"  QUERY_WAREHOUSE = '{self.config['warehouse']}'")
            sql_commands.append(f"  TITLE = '{app['title']}';")
            sql_commands.append("")
            sql_commands.append("")

        sql_content = '\n'.join(sql_commands)

        # Write to temp file
        temp_dir = Path(tempfile.gettempdir())
        sql_file = temp_dir / f"streamlit_deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

        with open(sql_file, 'w', encoding='utf-8') as f:
            f.write(sql_content)

        # Save to logs
        self.logger.save_sql_script(sql_content)

        self.logger.log(f"✓ Deployment script created", "SUCCESS")
        self.logger.log(f"  Apps: {len(apps_to_deploy)}")
        self.logger.log(f"  Files per app: 2 (streamlit_app.py + environment.yml)")
        self.logger.log(f"  Total files to upload: {len(apps_to_deploy) * 2}")
        self.logger.log(f"  SQL commands: {len([c for c in sql_commands if c and not c.startswith('--')])}")

        self.logger.log_step("create_script", "SUCCESS", {
            "apps_count": len(apps_to_deploy),
            "files_count": len(apps_to_deploy) * 2,
            "sql_file": str(sql_file)
        })

        return sql_file, sql_content

    def execute_deployment_script(self, sql_file: Path, apps_count: int) -> tuple:
        """Execute deployment with progress tracking"""

        self.logger.log("\n[Executing Deployment]", "INFO")
        self.logger.log("⏳ Opening browser for SSO authentication...", "INFO")
        self.logger.log(f"   Deploying {apps_count} apps with single authentication", "INFO")
        self.logger.log("")

        cmd = [
            SNOWSQL_PATH,
            "-a", self.config["account"],
            "-u", self.config["user"],
            "--authenticator", self.config["authenticator"],
            "-w", self.config["warehouse"],
            "-d", self.config["database"],
            "-s", self.config["schema"],
            "-r", self.config["role"],
            "-f", str(sql_file),
            "-o", "log_level=DEBUG"
        ]

        # Start progress indicator
        self.progress.start(f"Deploying {apps_count} apps")

        start_time = time.time()

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )

            duration = time.time() - start_time

            # Stop progress indicator
            self.progress.stop()

            if result.returncode == 0:
                self.logger.log(f"\n✓ Deployment executed successfully", "SUCCESS")
                self.logger.log(f"  Duration: {duration:.1f}s")
                self.logger.log(f"  Average per app: {duration/apps_count:.1f}s")

                self.logger.log_step("execute_deployment", "SUCCESS", {
                    "duration_seconds": round(duration, 2),
                    "apps_count": apps_count,
                    "avg_per_app": round(duration/apps_count, 2)
                })

                return True, result.stdout, duration
            else:
                self.logger.log(f"\n✗ Deployment failed", "ERROR")
                self.logger.log(f"  Error: {result.stderr}", "ERROR")

                self.logger.log_step("execute_deployment", "FAILED", {
                    "error": result.stderr
                })

                return False, result.stderr, duration

        except subprocess.TimeoutExpired:
            self.progress.stop()
            error = "Deployment timeout (>10 minutes)"
            self.logger.log(f"\n✗ {error}", "ERROR")
            self.logger.log_step("execute_deployment", "TIMEOUT", {"error": error})
            return False, error, 600

        except Exception as e:
            self.progress.stop()
            error = f"Error: {str(e)}"
            self.logger.log(f"\n✗ {error}", "ERROR")
            self.logger.log_step("execute_deployment", "ERROR", {"error": error})
            return False, error, 0

    def parse_deployment_results(self, output: str, apps_to_deploy: list) -> list:
        """Parse deployment output with detailed analysis"""

        self.logger.log("\n[Parsing Results]", "INFO")

        results = []

        for app in apps_to_deploy:
            app_name = app["name"]
            streamlit_name = f"STREAMLIT_{app_name.upper()}"

            # Analyze output for this app
            app_output = []
            for line in output.split('\n'):
                if app_name.lower() in line.lower() or streamlit_name in line:
                    app_output.append(line)

            # Determine success
            success = False
            error = None

            if f"{streamlit_name} successfully created" in output:
                success = True
            elif "successfully created" in output.lower() and app_name.lower() in output.lower():
                success = True
            elif "error" in output.lower() and app_name.lower() in output.lower():
                # Extract error
                for line in app_output:
                    if "error" in line.lower():
                        error = line.strip()
                        break

            result = {
                "app_name": app_name,
                "streamlit_name": streamlit_name,
                "success": success,
                "error": error,
                "timestamp": datetime.now().isoformat()
            }

            results.append(result)

            # Log result
            status = "✓" if success else "✗"
            level = "SUCCESS" if success else "ERROR"
            self.logger.log(f"  {status} {app_name}", level)
            if error:
                self.logger.log(f"     Error: {error}", "ERROR")

        # Store in deployment data
        self.logger.deployment_data["apps"] = results

        self.logger.log_step("parse_results", "SUCCESS", {
            "total": len(results),
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"])
        })

        return results

    def deploy_apps_batch(self, priority_filter: int = None) -> list:
        """Deploy apps in batch with progress tracking"""

        self.logger.log("\n" + "="*70, "INFO")
        self.logger.log("STREAMLIT APPS DEPLOYMENT (ENHANCED)", "INFO")
        self.logger.log("="*70, "INFO")
        self.logger.log(f"\n✓ Database: {self.config['database']}")
        self.logger.log(f"✓ Schema: {self.config['schema']}")
        self.logger.log(f"✓ Files: streamlit_app.py + environment.yml")
        self.logger.log(f"✓ Logging: {self.logger.logs_dir}")

        # Filter apps
        apps_to_deploy = APPS
        if priority_filter:
            apps_to_deploy = [app for app in APPS if app["priority"] == priority_filter]
            self.logger.log(f"\nDeploying Priority {priority_filter} apps: {len(apps_to_deploy)} apps")
        else:
            self.logger.log(f"\nTotal apps to deploy: {len(apps_to_deploy)}")

        apps_to_deploy = sorted(apps_to_deploy, key=lambda x: (x["priority"], x["name"]))

        # Show plan
        self.logger.log("\nDeployment Plan:")
        for i, app in enumerate(apps_to_deploy, 1):
            self.logger.log(f"  {i}. {app['name']} (Priority {app['priority']})")

        input("\nPress Enter to start deployment (or Ctrl+C to cancel)...")

        # Step 1: Check files
        self.logger.log("\n[Step 1/4] Checking app files...", "INFO")
        all_files_ok = True

        for app in apps_to_deploy:
            check = self.check_app_files(app["name"])
            if check["exists"]:
                self.logger.log(f"  ✓ {app['name']} (2 files, {sum(f['size'] for f in check['files'].values())} bytes)")
            else:
                self.logger.log(f"  ✗ {app['name']} - Missing: {', '.join(check['missing'])}", "ERROR")
                all_files_ok = False

        if not all_files_ok:
            self.logger.log("\n✗ Some files are missing. Aborting.", "ERROR")
            self.logger.save_json()
            return []

        self.logger.log_step("check_files", "SUCCESS", {"apps_count": len(apps_to_deploy)})

        # Step 2: Create script
        self.logger.log("\n[Step 2/4] Creating deployment script...", "INFO")
        sql_file, sql_content = self.create_deployment_script(apps_to_deploy)

        # Step 3: Execute
        self.logger.log("\n[Step 3/4] Executing deployment...", "INFO")
        success, output, duration = self.execute_deployment_script(sql_file, len(apps_to_deploy))

        if not success:
            self.logger.log(f"\n✗ Deployment failed!", "ERROR")
            self.logger.save_json()
            return []

        # Step 4: Parse results
        self.logger.log("\n[Step 4/4] Parsing results...", "INFO")
        results = self.parse_deployment_results(output, apps_to_deploy)

        # Add duration to results
        for result in results:
            result["duration_seconds"] = round(duration / len(apps_to_deploy), 2)

        # Cleanup temp file
        try:
            sql_file.unlink()
        except:
            pass

        return results

    def print_summary(self, results: list):
        """Print deployment summary"""

        self.logger.log("\n" + "="*70, "INFO")
        self.logger.log("DEPLOYMENT SUMMARY", "INFO")
        self.logger.log("="*70, "INFO")

        total = len(results)
        successful = sum(1 for r in results if r["success"])
        failed = total - successful

        # Summary data
        summary = {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": round((successful / total * 100), 2) if total > 0 else 0
        }

        self.logger.deployment_data["summary"] = summary

        self.logger.log(f"\nDatabase: {self.config['database']}")
        self.logger.log(f"Schema: {self.config['schema']}")
        self.logger.log(f"\nTotal apps: {total}")
        self.logger.log(f"Successful: {successful} ✓", "SUCCESS")
        self.logger.log(f"Failed: {failed} ✗", "ERROR" if failed > 0 else "INFO")
        self.logger.log(f"Success rate: {summary['success_rate']}%")

        if failed > 0:
            self.logger.log("\nFailed deployments:", "ERROR")
            for result in results:
                if not result["success"]:
                    error = result.get("error", "Unknown error")
                    self.logger.log(f"  ✗ {result['app_name']}: {error}", "ERROR")

        self.logger.log("\nSuccessful deployments:", "SUCCESS")
        for result in results:
            if result["success"]:
                self.logger.log(f"  ✓ {result['streamlit_name']}")

        # Save final JSON log
        self.logger.save_json()

        self.logger.log(f"\n📁 Log files saved in: {self.logger.logs_dir}")
        self.logger.log(f"  - Detailed log: {self.logger.log_file.name}")
        self.logger.log(f"  - JSON data: {self.logger.json_file.name}")
        self.logger.log(f"  - SQL script: {self.logger.sql_file.name}")

def main():
    """Main execution"""
    print("="*70)
    print("Streamlit Apps Deployment (ENHANCED)")
    print("="*70)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n✓ Real-time progress tracking")
    print("✓ Detailed logging for analysis")
    print("✓ Single SSO authentication")
    print("✓ Deploys to: DEV_REPORTING.SECURITY_ANALYTICS")

    deployer = EnhancedDeployer(CONFIG_FILE, APPS_DIR)

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

    # Print summary
    deployer.print_summary(results)

    # Next steps
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("\n1. Analyze logs:")
    print(f"   cd {deployer.logger.logs_dir}")
    print(f"   notepad {deployer.logger.log_file.name}")
    print("\n2. Verify deployment:")
    print("   .\\verify_apps.bat")
    print("\n3. Test in Snowflake:")
    print("   Database: DEV_REPORTING → Schema: SECURITY_ANALYTICS")

    failed = sum(1 for r in results if not r["success"])
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())
