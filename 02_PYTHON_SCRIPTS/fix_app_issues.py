"""
Fix Known Issues in Streamlit Apps
Fixes: np.random.randn errors and download button issues
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

class AppFixer:
    """Fixes common issues in Streamlit apps"""

    def __init__(self, apps_dir: Path):
        self.apps_dir = apps_dir
        self.fixes_applied = {
            "np_random_fixed": [],
            "download_buttons_fixed": [],
            "errors": []
        }

    def fix_np_random_randn(self, content: str, app_name: str) -> tuple:
        """
        Fix ALL np.random.* calls that fail in Snowflake Streamlit
        Snowflake Streamlit has limited numpy support - most np.random functions don't work

        Replacements:
        - np.random.randn(N) -> [random.gauss(0, 1) for _ in range(N)]
        - np.random.standard_normal(N) -> [random.gauss(0, 1) for _ in range(N)]
        - np.random.poisson(lam, N) -> [random.expovariate(1/lam) for _ in range(N)]
        - np.random.uniform(a, b, N) -> [random.uniform(a, b) for _ in range(N)]
        - np.random.randint(a, b, N) -> [random.randint(a, b-1) for _ in range(N)]
        """

        import_added = False
        fixes_count = 0

        # Pattern 1: np.random.randn(N)
        pattern1 = r'np\.random\.randn\((\d+)\)'
        matches1 = re.findall(pattern1, content)
        if matches1:
            content = re.sub(pattern1, r'[random.gauss(0, 1) for _ in range(\1)]', content)
            fixes_count += len(matches1)

        # Pattern 2: np.random.standard_normal(N)
        pattern2 = r'np\.random\.standard_normal\((\d+)\)'
        matches2 = re.findall(pattern2, content)
        if matches2:
            content = re.sub(pattern2, r'[random.gauss(0, 1) for _ in range(\1)]', content)
            fixes_count += len(matches2)

        # Pattern 3: np.random.poisson(lam, N) - Common in Sophos app
        pattern3 = r'np\.random\.poisson\((\d+),\s*(\d+)\)'
        matches3 = re.findall(pattern3, content)
        if matches3:
            # Replace with Poisson approximation using exponential distribution
            # For Poisson with rate lam, use int(random.expovariate(1/lam))
            def replace_poisson(match):
                lam = match.group(1)
                size = match.group(2)
                return f'[int(random.expovariate(1/{lam})) if {lam} > 0 else 0 for _ in range({size})]'
            content = re.sub(pattern3, replace_poisson, content)
            fixes_count += len(matches3)

        # Pattern 4: np.random.uniform(low, high, N)
        pattern4 = r'np\.random\.uniform\(([^,]+),\s*([^,]+),\s*(\d+)\)'
        matches4 = re.findall(pattern4, content)
        if matches4:
            def replace_uniform(match):
                low = match.group(1)
                high = match.group(2)
                size = match.group(3)
                return f'[random.uniform({low}, {high}) for _ in range({size})]'
            content = re.sub(pattern4, replace_uniform, content)
            fixes_count += len(matches4)

        # Pattern 5: np.random.randint(low, high, N)
        pattern5 = r'np\.random\.randint\(([^,]+),\s*([^,]+),\s*(\d+)\)'
        matches5 = re.findall(pattern5, content)
        if matches5:
            def replace_randint(match):
                low = match.group(1)
                high = match.group(2)
                size = match.group(3)
                # numpy randint is exclusive on high, Python randint is inclusive
                return f'[random.randint({low}, {high}-1) for _ in range({size})]'
            content = re.sub(pattern5, replace_randint, content)
            fixes_count += len(matches5)

        # If we made fixes, ensure random module is imported
        if fixes_count > 0:
            if 'import random' not in content and 'from random import' not in content:
                # Add import at the top after other imports
                lines = content.split('\n')
                import_index = 0

                # Find last import statement
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        import_index = i

                # Insert import random after last import
                lines.insert(import_index + 1, 'import random')
                content = '\n'.join(lines)
                import_added = True

            msg = f"  [OK] {app_name}: Fixed {fixes_count} np.random calls"
            if import_added:
                msg += " (added random import)"
            print(msg)
            return content, fixes_count

        return content, 0

    def fix_download_buttons(self, content: str, app_name: str) -> tuple:
        """
        Fix download buttons for Snowflake Streamlit compatibility
        - Adds unique key parameter
        - Ensures mime_type is set correctly
        - Ensures data is properly formatted
        """

        fixes_count = 0
        lines = content.split('\n')
        new_lines = []

        in_download_button = False
        button_start_line = 0
        button_lines = []
        button_counter = 1

        for i, line in enumerate(lines):
            if 'st.download_button(' in line:
                in_download_button = True
                button_start_line = i
                button_lines = [line]
            elif in_download_button:
                button_lines.append(line)

                # Check if this is the closing parenthesis
                if ')' in line and line.strip().endswith(')'):
                    # Reconstruct button
                    button_code = '\n'.join(button_lines)

                    needs_fix = False

                    # Check if key parameter exists
                    if 'key=' not in button_code:
                        needs_fix = True

                    # Check if mime_type is set for CSV
                    if 'mime=' not in button_code and '.csv' in button_code:
                        needs_fix = True

                    if needs_fix:
                        # Get the indentation
                        first_line = button_lines[0]
                        base_indent = len(first_line) - len(first_line.lstrip())
                        param_indent = ' ' * (base_indent + 4)

                        # Parse existing parameters
                        has_key = 'key=' in button_code
                        has_mime = 'mime=' in button_code

                        # Add missing parameters before the closing parenthesis
                        last_line = button_lines[-1]
                        new_params = []

                        if not has_mime and '.csv' in button_code:
                            new_params.append(f'{param_indent}mime="text/csv",')

                        if not has_key:
                            # Remove comma from last parameter if we're adding more
                            if new_params:
                                for idx in range(len(button_lines) - 1, -1, -1):
                                    if '=' in button_lines[idx] and button_lines[idx].strip() not in ['', ')']:
                                        if not button_lines[idx].rstrip().endswith(','):
                                            button_lines[idx] = button_lines[idx].rstrip() + ','
                                        break

                            new_params.append(f'{param_indent}key=f"download_{app_name.lower()}_{button_counter}"')

                        if new_params:
                            # Insert new parameters before closing paren
                            button_lines = button_lines[:-1] + new_params + [last_line]
                            fixes_count += 1
                            button_counter += 1

                    # Add all button lines
                    new_lines.extend(button_lines)
                    in_download_button = False
                    button_lines = []
                    continue

            if not in_download_button:
                new_lines.append(line)

        if fixes_count > 0:
            print(f"  [OK] {app_name}: Fixed {fixes_count} download buttons (added key + mime)")

        return '\n'.join(new_lines), fixes_count

    def fix_app(self, app_name: str) -> bool:
        """Fix issues in a single app"""

        app_file = self.apps_dir / app_name / "streamlit_app.py"

        if not app_file.exists():
            print(f"  [ERROR] {app_name}: streamlit_app.py not found")
            self.fixes_applied["errors"].append(app_name)
            return False

        # Read file
        try:
            with open(app_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"  [ERROR] {app_name}: Error reading file: {e}")
            self.fixes_applied["errors"].append(app_name)
            return False

        original_content = content

        # Apply fixes
        content, np_fixes = self.fix_np_random_randn(content, app_name)
        content, button_fixes = self.fix_download_buttons(content, app_name)

        # Write back if changes were made
        if content != original_content:
            try:
                with open(app_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                if np_fixes > 0:
                    self.fixes_applied["np_random_fixed"].append(app_name)
                if button_fixes > 0:
                    self.fixes_applied["download_buttons_fixed"].append(app_name)

                return True
            except Exception as e:
                print(f"  [ERROR] {app_name}: Error writing file: {e}")
                self.fixes_applied["errors"].append(app_name)
                return False
        else:
            print(f"  [SKIP] {app_name}: No fixes needed")
            return True

    def fix_all_apps(self):
        """Fix all apps"""

        print("="*70)
        print("FIXING STREAMLIT APPS ISSUES")
        print("="*70)
        print("\nIssues to fix:")
        print("  1. ALL np.random.* functions -> Python random module (Snowflake compatible)")
        print("     - randn/standard_normal -> random.gauss()")
        print("     - poisson -> random.expovariate()")
        print("     - uniform -> random.uniform()")
        print("     - randint -> random.randint()")
        print("  2. Download buttons missing key and mime parameters")
        print(f"\nApps to check: {len(APPS_TO_FIX)}")
        print("")

        for app in APPS_TO_FIX:
            self.fix_app(app)

        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)

        print(f"\nApps with np.random fixes: {len(self.fixes_applied['np_random_fixed'])}")
        for app in self.fixes_applied['np_random_fixed']:
            print(f"  [OK] {app}")

        print(f"\nApps with download button fixes: {len(self.fixes_applied['download_buttons_fixed'])}")
        for app in self.fixes_applied['download_buttons_fixed']:
            print(f"  [OK] {app}")

        if self.fixes_applied['errors']:
            print(f"\nApps with errors: {len(self.fixes_applied['errors'])}")
            for app in self.fixes_applied['errors']:
                print(f"  [ERROR] {app}")

        total_fixed = len(set(
            self.fixes_applied['np_random_fixed'] +
            self.fixes_applied['download_buttons_fixed']
        ))

        print(f"\n[OK] Total apps fixed: {total_fixed}/{len(APPS_TO_FIX)}")

        if total_fixed > 0:
            print("\n" + "="*70)
            print("NEXT STEPS")
            print("="*70)
            print("\n1. Redeploy fixed apps:")
            print("   .\\deploy_apps.bat")
            print("\n2. Test in Snowflake:")
            print("   - Test filters + refresh (no np.random error)")
            print("   - Test download buttons (should download CSV)")

def main():
    """Main execution"""

    fixer = AppFixer(APPS_DIR)
    fixer.fix_all_apps()

    return 0

if __name__ == "__main__":
    exit(main())
