"""
Deployment Logs Analyzer
Analyzes deployment logs and generates insights
"""

import json
from pathlib import Path
from datetime import datetime
import sys

LOGS_DIR = Path(__file__).parent.parent / "deployment_logs"

class LogAnalyzer:
    """Analyzes deployment logs"""

    def __init__(self, logs_dir: Path):
        self.logs_dir = logs_dir

    def find_latest_log(self) -> Path:
        """Find the most recent JSON log file"""
        json_files = sorted(self.logs_dir.glob("deployment_*.json"), reverse=True)

        if not json_files:
            print(f"✗ No log files found in {self.logs_dir}")
            return None

        return json_files[0]

    def load_log(self, log_file: Path) -> dict:
        """Load JSON log file"""
        with open(log_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def analyze(self, log_file: Path = None):
        """Perform analysis"""

        if not log_file:
            log_file = self.find_latest_log()
            if not log_file:
                return

        print("="*70)
        print("DEPLOYMENT LOG ANALYSIS")
        print("="*70)
        print(f"\nLog file: {log_file.name}")

        data = self.load_log(log_file)

        # Basic info
        print("\n" + "="*70)
        print("DEPLOYMENT INFO")
        print("="*70)
        print(f"\nStart time: {data.get('start_time', 'N/A')}")
        print(f"End time: {data.get('end_time', 'N/A')}")

        # Configuration
        config = data.get('config', {})
        print(f"\nDatabase: {config.get('database', 'N/A')}")
        print(f"Schema: {config.get('schema', 'N/A')}")
        print(f"Warehouse: {config.get('warehouse', 'N/A')}")
        print(f"User: {config.get('user', 'N/A')}")

        # Summary
        summary = data.get('summary', {})
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"\nTotal apps: {summary.get('total', 0)}")
        print(f"Successful: {summary.get('successful', 0)} ✓")
        print(f"Failed: {summary.get('failed', 0)} ✗")
        print(f"Success rate: {summary.get('success_rate', 0)}%")

        # Apps breakdown
        apps = data.get('apps', [])
        if apps:
            print("\n" + "="*70)
            print("APPS BREAKDOWN")
            print("="*70)

            successful_apps = [app for app in apps if app.get('success')]
            failed_apps = [app for app in apps if not app.get('success')]

            if successful_apps:
                print(f"\n✓ Successful ({len(successful_apps)}):")
                for app in successful_apps:
                    print(f"  • {app['streamlit_name']}")

            if failed_apps:
                print(f"\n✗ Failed ({len(failed_apps)}):")
                for app in failed_apps:
                    error = app.get('error', 'Unknown error')
                    print(f"  • {app['app_name']}: {error}")

        # Steps analysis
        steps = data.get('steps', [])
        if steps:
            print("\n" + "="*70)
            print("DEPLOYMENT STEPS")
            print("="*70)

            for step in steps:
                step_name = step.get('step', 'Unknown')
                status = step.get('status', 'N/A')
                details = step.get('details', {})

                status_icon = "✓" if status == "SUCCESS" else "✗"
                print(f"\n{status_icon} {step_name}: {status}")

                if details:
                    for key, value in details.items():
                        print(f"  • {key}: {value}")

        # Log entries analysis
        logs = data.get('logs', [])
        if logs:
            print("\n" + "="*70)
            print("LOG STATISTICS")
            print("="*70)

            log_levels = {}
            for log in logs:
                level = log.get('level', 'UNKNOWN')
                log_levels[level] = log_levels.get(level, 0) + 1

            print(f"\nTotal log entries: {len(logs)}")
            for level, count in sorted(log_levels.items()):
                print(f"  • {level}: {count}")

            # Show errors
            errors = [log for log in logs if log.get('level') == 'ERROR']
            if errors:
                print(f"\n✗ Errors found ({len(errors)}):")
                for error in errors[:10]:  # Show first 10
                    print(f"  [{error.get('timestamp')}] {error.get('message')}")

        print("\n" + "="*70)
        print("ANALYSIS COMPLETE")
        print("="*70)

    def compare_logs(self):
        """Compare multiple deployment logs"""
        json_files = sorted(self.logs_dir.glob("deployment_*.json"), reverse=True)

        if len(json_files) < 2:
            print("Need at least 2 log files to compare")
            return

        print("="*70)
        print("DEPLOYMENT LOGS COMPARISON")
        print("="*70)
        print(f"\nFound {len(json_files)} deployment logs")
        print("\nComparison:")

        for i, log_file in enumerate(json_files[:5], 1):  # Compare last 5
            data = self.load_log(log_file)
            summary = data.get('summary', {})

            timestamp = data.get('start_time', 'N/A')
            total = summary.get('total', 0)
            successful = summary.get('successful', 0)
            success_rate = summary.get('success_rate', 0)

            print(f"\n{i}. {log_file.name}")
            print(f"   Time: {timestamp}")
            print(f"   Apps: {successful}/{total} ({success_rate}%)")

    def export_summary(self, output_file: Path = None):
        """Export summary to markdown"""

        log_file = self.find_latest_log()
        if not log_file:
            return

        data = self.load_log(log_file)

        if not output_file:
            output_file = self.logs_dir / "DEPLOYMENT_SUMMARY.md"

        lines = []
        lines.append("# Deployment Summary\n")
        lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append(f"**Log file**: {log_file.name}\n")
        lines.append("\n---\n")

        # Deployment info
        lines.append("## Deployment Information\n")
        lines.append(f"- **Start time**: {data.get('start_time', 'N/A')}\n")
        lines.append(f"- **End time**: {data.get('end_time', 'N/A')}\n")

        config = data.get('config', {})
        lines.append(f"- **Database**: {config.get('database', 'N/A')}\n")
        lines.append(f"- **Schema**: {config.get('schema', 'N/A')}\n")
        lines.append(f"- **Warehouse**: {config.get('warehouse', 'N/A')}\n")

        # Summary
        summary = data.get('summary', {})
        lines.append("\n## Summary\n")
        lines.append(f"- **Total apps**: {summary.get('total', 0)}\n")
        lines.append(f"- **Successful**: {summary.get('successful', 0)} ✓\n")
        lines.append(f"- **Failed**: {summary.get('failed', 0)} ✗\n")
        lines.append(f"- **Success rate**: {summary.get('success_rate', 0)}%\n")

        # Apps
        apps = data.get('apps', [])
        if apps:
            lines.append("\n## Deployed Applications\n")

            successful_apps = [app for app in apps if app.get('success')]
            if successful_apps:
                lines.append("\n### ✓ Successful\n")
                for app in successful_apps:
                    lines.append(f"- {app['streamlit_name']}\n")

            failed_apps = [app for app in apps if not app.get('success')]
            if failed_apps:
                lines.append("\n### ✗ Failed\n")
                for app in failed_apps:
                    error = app.get('error', 'Unknown error')
                    lines.append(f"- {app['app_name']}: `{error}`\n")

        # Write file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        print(f"\n✓ Summary exported to: {output_file.name}")

def main():
    """Main execution"""

    if not LOGS_DIR.exists():
        print(f"✗ Logs directory not found: {LOGS_DIR}")
        print("  Run a deployment first: .\\deploy_apps.bat")
        return 1

    analyzer = LogAnalyzer(LOGS_DIR)

    # Menu
    print("="*70)
    print("DEPLOYMENT LOG ANALYZER")
    print("="*70)
    print("\n1. Analyze latest deployment")
    print("2. Compare multiple deployments")
    print("3. Export summary to markdown")
    print("4. Show all log files")

    choice = input("\nEnter your choice (1-4): ").strip()

    if choice == "1":
        analyzer.analyze()
    elif choice == "2":
        analyzer.compare_logs()
    elif choice == "3":
        analyzer.export_summary()
        analyzer.analyze()
    elif choice == "4":
        print(f"\nLog files in {LOGS_DIR}:\n")
        log_files = sorted(LOGS_DIR.glob("deployment_*"), reverse=True)
        for log_file in log_files:
            size_kb = log_file.stat().st_size / 1024
            print(f"  • {log_file.name} ({size_kb:.1f} KB)")
    else:
        print("✗ Invalid choice")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
