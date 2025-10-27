"""
Automated Script to Fix Numpy Issues in All Streamlit Apps
Applies the numpy fixes from Sophos to the remaining 17 apps
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

# Configuration
BASE_DIR = Path(__file__).parent.parent
APPS_DIR = BASE_DIR / "13_STREAMLIT_COMPLETE"
BACKUP_DIR = BASE_DIR / "backups" / f"numpy_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
LOG_FILE = BASE_DIR / "02_PYTHON_SCRIPTS" / "numpy_fix_log.txt"

# Reference app with correct numpy implementation
REFERENCE_APP = "Sophos"

# Apps to fix (excluding Sophos which is already fixed)
APPS_TO_FIX = [
    "Ancon", "BitSight", "Cisco_AMP", "Crowdstrike", "CybelAngel",
    "Intel_Threats", "Leviat", "Proofpoint", "Qualys", "SentinelOne",
    "ServiceNow", "Splunk", "Symantec", "Tenable", "Trellix",
    "Zerofox", "Zscaler"
]

# The correct _DummyNumpy class (extracted from Sophos)
CORRECT_DUMMY_NUMPY = '''class _DummyNumpy:
    \'\'\'Dummy numpy replacement\'\'\'
    # Constants
    inf = float('inf')

    class random:
        \'\'\'Dummy numpy.random submodule\'\'\'
        @staticmethod
        def standard_normal(size=None):
            \'\'\'Generate standard normal random numbers using Python's random\'\'\'
            import random as py_random
            if size is None:
                return py_random.gauss(0, 1)
            return [py_random.gauss(0, 1) for _ in range(size)]

        @staticmethod
        def randint(low, high=None, size=None):
            \'\'\'Generate random integers\'\'\'
            import random as py_random
            if high is None:
                high = low
                low = 0
            if size is None:
                return py_random.randint(low, high - 1)
            return [py_random.randint(low, high - 1) for _ in range(size)]

        @staticmethod
        def poisson(lam=1.0, size=None):
            \'\'\'Generate Poisson random numbers (approximated with normal distribution)\'\'\'
            import random as py_random
            # Simple approximation: Poisson ≈ Normal(λ, √λ) for large λ
            import math
            if size is None:
                # For single value, use exponential intervals method
                L = math.exp(-lam)
                k = 0
                p = 1.0
                while p > L:
                    k += 1
                    p *= py_random.random()
                return max(0, k - 1)
            else:
                # For array, use simpler approximation
                if lam > 10:
                    # Normal approximation for large lambda
                    return [max(0, int(py_random.gauss(lam, math.sqrt(lam)))) for _ in range(size)]
                else:
                    # Exact method for small lambda
                    result = []
                    L = math.exp(-lam)
                    for _ in range(size):
                        k = 0
                        p = 1.0
                        while p > L:
                            k += 1
                            p *= py_random.random()
                        result.append(max(0, k - 1))
                    return result

    def round(self, *args, **kwargs):
        \'\'\'Dummy round function - returns input as-is\'\'\'
        if args:
            return args[0]  # Return first argument
        return None

    def array(self, *args, **kwargs):
        \'\'\'Dummy array function\'\'\'
        if args:
            return args[0]
        return []

    def arange(self, *args, **kwargs):
        \'\'\'Dummy arange - returns range as list\'\'\'
        if len(args) == 1:
            return list(range(int(args[0])))
        elif len(args) == 2:
            return list(range(int(args[0]), int(args[1])))
        elif len(args) == 3:
            return list(range(int(args[0]), int(args[1]), int(args[2])))
        return []

    def __getattr__(self, name):
        \'\'\'Return dummy function for any numpy method\'\'\'
        def dummy_func(*args, **kwargs):
            if args:
                return args[0]
            return None
        return dummy_func'''

def log(message):
    """Log message to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    # Remove emoji characters for Windows console compatibility
    console_message = log_message.encode('ascii', 'ignore').decode('ascii')
    print(console_message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + '\n')

def create_backup(app_name):
    """Create backup of app before modification"""
    source = APPS_DIR / app_name / "streamlit_app.py"
    if not source.exists():
        log(f"  ⚠️  File not found: {source}")
        return False

    backup_path = BACKUP_DIR / app_name
    backup_path.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, backup_path / "streamlit_app.py")
    log(f"  ✅ Backup created: {backup_path}")
    return True

def extract_dummy_numpy_class(content):
    """Extract the _DummyNumpy class from file content"""
    # Find the start of _DummyNumpy class
    pattern = r'class _DummyNumpy:.*?(?=\nclass |\nif __name__|$)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(0)
    return None

def replace_dummy_numpy_class(content, new_class):
    """Replace old _DummyNumpy class with new one"""
    # Find and replace the _DummyNumpy class
    pattern = r'class _DummyNumpy:.*?(?=\nclass |\Z)'

    # Check if pattern exists
    if not re.search(pattern, content, re.DOTALL):
        log("  ⚠️  Could not find _DummyNumpy class")
        return content, False

    new_content = re.sub(pattern, new_class, content, count=1, flags=re.DOTALL)
    return new_content, True

def fix_numpy_arithmetic_patterns(content):
    """Fix numpy arithmetic patterns that need pd.Series conversion"""
    changes_made = []

    # Pattern 1: Look for np.random.standard_normal(N) * scalar + np.arange(N) * scalar
    # This pattern needs to be converted to pd.Series

    # Find DataFrame creation with numpy operations
    pattern = r"(pd\.DataFrame\(\{[^}]+)'([^']+)':\s*(\d+)\s*\+\s*np\.random\.standard_normal\((\d+)\)\s*\*\s*([\d.]+)\s*\+\s*np\.arange\((\d+)\)\s*\*\s*([\d.]+)"

    def replace_with_series(match):
        prefix = match.group(1)
        col_name = match.group(2)
        base_value = match.group(3)
        size1 = match.group(4)
        multiplier1 = match.group(5)
        size2 = match.group(6)
        multiplier2 = match.group(7)

        # Generate variable names based on column name
        var_name = col_name.lower().replace(' ', '_').replace('%', 'pct')
        random_var = f"random_{var_name}"

        changes_made.append(f"Converted {col_name} to use pd.Series")

        # Return the fixed version (we'll need to add Series creation before DataFrame)
        return match.group(0)  # Keep original for now, manual fix needed

    # For now, just detect patterns that need fixing
    matches = re.findall(pattern, content)
    if matches:
        log(f"  ℹ️  Found {len(matches)} numpy arithmetic patterns that may need pd.Series conversion")
        for match in matches:
            log(f"     - Column: {match[1]}")

    return content, changes_made

def process_app(app_name):
    """Process a single app"""
    log(f"\n{'='*80}")
    log(f"Processing: {app_name}")
    log(f"{'='*80}")

    # Create backup
    if not create_backup(app_name):
        return False

    # Read the file
    file_path = APPS_DIR / app_name / "streamlit_app.py"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        log(f"  ❌ Error reading file: {e}")
        return False

    original_size = len(content)
    log(f"  📄 Original file size: {original_size:,} bytes")

    # Replace _DummyNumpy class
    new_content, replaced = replace_dummy_numpy_class(content, CORRECT_DUMMY_NUMPY)
    if not replaced:
        log(f"  ❌ Failed to replace _DummyNumpy class")
        return False

    log(f"  ✅ Replaced _DummyNumpy class")

    # Check for numpy arithmetic patterns
    new_content, changes = fix_numpy_arithmetic_patterns(new_content)
    if changes:
        for change in changes:
            log(f"  ℹ️  {change}")

    # Write the modified content
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        new_size = len(new_content)
        log(f"  📄 New file size: {new_size:,} bytes (diff: {new_size - original_size:+,} bytes)")
        log(f"  ✅ File updated successfully")
        return True
    except Exception as e:
        log(f"  ❌ Error writing file: {e}")
        return False

def main():
    """Main execution"""
    log("="*80)
    log("AUTOMATED NUMPY FIX FOR ALL STREAMLIT APPS")
    log("="*80)
    log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Base directory: {BASE_DIR}")
    log(f"Apps directory: {APPS_DIR}")
    log(f"Backup directory: {BACKUP_DIR}")
    log(f"Total apps to fix: {len(APPS_TO_FIX)}")
    log("")

    # Create backup directory
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    # Process each app
    success_count = 0
    failed_apps = []

    for app_name in APPS_TO_FIX:
        if process_app(app_name):
            success_count += 1
        else:
            failed_apps.append(app_name)

    # Summary
    log("\n" + "="*80)
    log("SUMMARY")
    log("="*80)
    log(f"Total apps processed: {len(APPS_TO_FIX)}")
    log(f"Successful: {success_count}")
    log(f"Failed: {len(failed_apps)}")

    if failed_apps:
        log(f"\nFailed apps:")
        for app in failed_apps:
            log(f"  - {app}")

    log(f"\nBackups saved to: {BACKUP_DIR}")
    log(f"Log file: {LOG_FILE}")
    log("\n✅ Script execution completed!")

    return success_count == len(APPS_TO_FIX)

if __name__ == "__main__":
    # Clear log file
    if LOG_FILE.exists():
        LOG_FILE.unlink()

    success = main()
    exit(0 if success else 1)
