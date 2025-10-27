"""
Fix Database Context for All Streamlit Apps
Adds USE DATABASE and USE SCHEMA statements after get_active_session()
to prevent STAGE GET errors
"""

from pathlib import Path
import re

APPS_DIR = Path(__file__).parent.parent / "13_STREAMLIT_COMPLETE"

# Apps to fix
APPS_TO_FIX = [
    "Symantec", "Trellix", "Crowdstrike", "SentinelOne", "Sophos",
    "Qualys", "Splunk", "Proofpoint", "CybelAngel", "Zerofox",
    "Zscaler", "Cisco_AMP", "BitSight", "Intel_Threats",
    "ServiceNow", "Leviat", "Ancon", "Tenable"
]

DATABASE_CONTEXT_CODE = """
# Set database context to avoid STAGE GET errors
try:
    session.sql("USE DATABASE DEV_REPORTING").collect()
    session.sql("USE SCHEMA SECURITY_ANALYTICS").collect()
except Exception as e:
    st.warning(f"Could not set database context: {e}")
"""

class DatabaseContextFixer:
    """Fix database context in Streamlit apps"""

    def __init__(self, apps_dir: Path):
        self.apps_dir = apps_dir
        self.fixes_applied = []
        self.already_fixed = []
        self.errors = []

    def fix_app(self, app_name: str) -> bool:
        """Fix database context in a single app"""

        app_file = self.apps_dir / app_name / "streamlit_app.py"

        if not app_file.exists():
            print(f"  [ERROR] {app_name}: streamlit_app.py not found")
            self.errors.append(app_name)
            return False

        # Read file
        try:
            with open(app_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"  [ERROR] {app_name}: Error reading file: {e}")
            self.errors.append(app_name)
            return False

        # Check if already fixed
        if "USE DATABASE DEV_REPORTING" in content or "Set database context" in content:
            print(f"  [SKIP] {app_name}: Already has database context")
            self.already_fixed.append(app_name)
            return True

        # Find pattern: session = get_active_session()
        pattern = r'(session = get_active_session\(\))\s*\n'

        if not re.search(pattern, content):
            print(f"  [SKIP] {app_name}: No get_active_session() found")
            return True

        # Insert database context after get_active_session()
        new_content = re.sub(
            pattern,
            r'\1\n' + DATABASE_CONTEXT_CODE + '\n',
            content,
            count=1  # Only replace first occurrence
        )

        # Check if replacement was made
        if new_content == content:
            print(f"  [SKIP] {app_name}: Could not insert database context")
            return True

        # Write back
        try:
            with open(app_file, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"  [OK] {app_name}: Added database context")
            self.fixes_applied.append(app_name)
            return True

        except Exception as e:
            print(f"  [ERROR] {app_name}: Error writing file: {e}")
            self.errors.append(app_name)
            return False

    def fix_all_apps(self):
        """Fix all apps"""

        print("="*70)
        print("FIXING DATABASE CONTEXT FOR ALL STREAMLIT APPS")
        print("="*70)
        print("\nIssue: STAGE GET errors due to missing database context")
        print("Fix: Add USE DATABASE and USE SCHEMA after get_active_session()")
        print(f"\nApps to check: {len(APPS_TO_FIX)}")
        print("")

        for app in APPS_TO_FIX:
            self.fix_app(app)

        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)

        print(f"\nApps fixed: {len(self.fixes_applied)}")
        for app in self.fixes_applied:
            print(f"  [OK] {app}")

        print(f"\nApps already fixed: {len(self.already_fixed)}")
        for app in self.already_fixed:
            print(f"  [SKIP] {app}")

        if self.errors:
            print(f"\nApps with errors: {len(self.errors)}")
            for app in self.errors:
                print(f"  [ERROR] {app}")

        total_fixed = len(self.fixes_applied) + len(self.already_fixed)
        print(f"\n[OK] Total apps with database context: {total_fixed}/{len(APPS_TO_FIX)}")

        if len(self.fixes_applied) > 0:
            print("\n" + "="*70)
            print("NEXT STEPS")
            print("="*70)
            print("\n1. Redeploy fixed apps:")
            print("   .\\deploy_apps.bat")
            print("\n2. Test in Snowflake:")
            print("   - Apps should load without STAGE GET errors")
            print("   - Test data display and downloads")

def main():
    """Main execution"""

    fixer = DatabaseContextFixer(APPS_DIR)
    fixer.fix_all_apps()

    return 0

if __name__ == "__main__":
    exit(main())
