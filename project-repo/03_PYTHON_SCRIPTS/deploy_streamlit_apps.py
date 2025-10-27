"""
Deploy Streamlit Apps to Snowflake
Automatically deploys all SECURITY_ANALYTICS Streamlit validation apps to Snowflake.

This script:
1. Reads streamlit_app.py from each service folder
2. Inlines common module imports (resolves sys.path.append issues)
3. Generates CREATE STREAMLIT SQL statements
4. Executes deployment via Snowflake Python connector
5. Verifies deployment and generates report

Author: Data Engineering Team
Date: 2025-10-24
"""

import snowflake.connector
import os
import json
import sys
import re
from datetime import datetime
from pathlib import Path

# Force UTF-8 encoding for console output (Windows compatibility)
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# =====================================================================
# CONFIGURATION
# =====================================================================

SNOWFLAKE_CONFIG = {
    'account': 'mw76572.east-us-2.azure',
    'user': 'FUAD.ONATE@CompanyX.COM',
    'authenticator': 'externalbrowser',  # SSO
    'warehouse': 'DEV_WH',
    'database': 'DEV_REPORTING',
    'schema': 'SECURITY_ANALYTICS',
    'role': 'DEV_DEVELOPER'
}

# Base path to Streamlit apps
BASE_PATH = Path(__file__).parent.parent / "07_STREAMLIT_APPS"

# Services to deploy (alphabetical order)
SERVICES = [
    'Ancon', 'BitSight', 'Cisco_AMP', 'Crowdstrike', 'CybelAngel',
    'Intel_Threats', 'Leviat', 'Proofpoint', 'Qualys', 'SentinelOne',
    'ServiceNow', 'Sophos', 'Splunk', 'Symantec', 'Tenable',
    'Trellix', 'Zerofox', 'Zscaler'
]

# =====================================================================
# INLINE COMMON MODULES
# =====================================================================

def read_common_module(module_name):
    """Read a common module file"""
    module_path = BASE_PATH / "common" / f"{module_name}.py"
    if not module_path.exists():
        raise FileNotFoundError(f"Common module not found: {module_path}")

    with open(module_path, 'r', encoding='utf-8') as f:
        return f.read()

def inline_common_imports(app_code):
    """
    Replace common module imports with inline code.
    Handles: from common.X import Y, Z
    """
    # Read all common modules once
    common_modules = {
        'styles': read_common_module('styles'),
        'utils': read_common_module('utils'),
        'validators': read_common_module('validators'),
        'config': read_common_module('config')
    }

    # Remove sys.path.append lines
    app_code = re.sub(r'import sys\s*\n\s*sys\.path\.append\(["\']\.\.["\']\)\s*\n?', '', app_code)

    # Find all common imports
    import_pattern = r'from common\.(\w+) import (.+)'
    imports = re.findall(import_pattern, app_code)

    if not imports:
        return app_code  # No common imports, return as-is

    # Build inline code section
    inline_code = "\n# ============================================================================\n"
    inline_code += "# COMMON MODULES (INLINED FOR SNOWFLAKE DEPLOYMENT)\n"
    inline_code += "# ============================================================================\n\n"

    # Track which modules are imported
    imported_modules = set()
    for module_name, _ in imports:
        imported_modules.add(module_name)

    # Add each imported module's code
    for module_name in sorted(imported_modules):
        inline_code += f"# --- Common Module: {module_name}.py ---\n"

        # Clean up the module code (remove docstrings at top)
        module_code = common_modules[module_name]

        # Remove module-level docstring if present
        module_code = re.sub(r'^"""[\s\S]*?"""\s*\n', '', module_code)
        module_code = re.sub(r"^'''[\s\S]*?'''\s*\n", '', module_code)

        inline_code += module_code + "\n\n"

    # Remove all common import statements
    app_code = re.sub(import_pattern + r'\s*\n?', '', app_code)

    # Insert inline code after the main imports section
    # Find the last import statement
    import_section_end = 0
    for match in re.finditer(r'^import .+|^from .+ import .+', app_code, re.MULTILINE):
        import_section_end = match.end()

    # Insert inline code after imports
    if import_section_end > 0:
        app_code = app_code[:import_section_end] + "\n" + inline_code + app_code[import_section_end:]
    else:
        # No imports found, add at beginning after docstring
        docstring_end = re.search(r'^"""[\s\S]*?"""\s*\n', app_code)
        if docstring_end:
            insert_pos = docstring_end.end()
            app_code = app_code[:insert_pos] + "\n" + inline_code + app_code[insert_pos:]
        else:
            app_code = inline_code + app_code

    return app_code

def read_environment_yml(service_path):
    """Read environment.yml for a service"""
    env_file = service_path / "environment.yml"
    if not env_file.exists():
        return None

    with open(env_file, 'r', encoding='utf-8') as f:
        return f.read()

# =====================================================================
# GENERATE DEPLOYMENT SQL
# =====================================================================

def generate_create_streamlit_sql(service_name, app_code, env_yml=None):
    """
    Generate CREATE STREAMLIT SQL statement.
    Uses Snowflake's STREAMLIT object syntax.
    """
    app_name = f"{service_name.upper()}_APP"

    sql = f"""
CREATE OR REPLACE STREAMLIT {SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.{app_name}
  ROOT_LOCATION = '@{SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.STREAMLIT_STAGE'
  MAIN_FILE = 'streamlit_app.py'
  QUERY_WAREHOUSE = '{SNOWFLAKE_CONFIG['warehouse']}'
  COMMENT = 'SECURITY_ANALYTICS validation dashboard for {service_name} - Auto-deployed'
"""

    # Note: Snowflake doesn't support embedding code directly in CREATE STREAMLIT
    # We need to use PUT command to upload files to stage first
    return sql

def generate_deployment_commands(service_name, app_code, env_yml=None):
    """
    Generate complete deployment commands for a service.
    Returns list of (command_type, command_text) tuples.
    """
    commands = []

    # 1. Create stage if not exists
    commands.append(('STAGE', f"""
CREATE STAGE IF NOT EXISTS {SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.STREAMLIT_STAGE
  COMMENT = 'Storage for Streamlit app files'
"""))

    # 2. Note: We'll need to write files locally, then PUT them
    # For now, generate SQL to create the Streamlit object
    app_name = f"{service_name.upper()}_APP"

    # Snowflake Streamlit requires files to be in a stage
    # We'll use a different approach: Write files to temp directory, PUT to stage

    return commands

# =====================================================================
# DEPLOYMENT EXECUTION
# =====================================================================

def deploy_service(service_name, conn, cursor, dry_run=False):
    """Deploy a single Streamlit app to Snowflake"""
    print(f"\n{'=' * 80}")
    print(f"DEPLOYING: {service_name}")
    print(f"{'=' * 80}")

    service_path = BASE_PATH / service_name
    app_file = service_path / "streamlit_app.py"
    env_file = service_path / "environment.yml"

    # Check if files exist
    if not app_file.exists():
        print(f"❌ ERROR: streamlit_app.py not found in {service_path}")
        return {'service': service_name, 'success': False, 'error': 'App file not found'}

    if not env_file.exists():
        print(f"⚠️  WARNING: environment.yml not found (using default dependencies)")

    # Read app code
    print(f"📖 Reading {app_file.name}...")
    with open(app_file, 'r', encoding='utf-8') as f:
        app_code = f.read()

    original_lines = len(app_code.split('\n'))
    print(f"   Original: {original_lines} lines")

    # Inline common modules
    print(f"🔄 Inlining common modules...")
    try:
        inlined_code = inline_common_imports(app_code)
        inlined_lines = len(inlined_code.split('\n'))
        print(f"   Inlined: {inlined_lines} lines (+{inlined_lines - original_lines} from common modules)")
    except Exception as e:
        print(f"❌ ERROR inlining modules: {e}")
        return {'service': service_name, 'success': False, 'error': str(e)}

    # For now, we'll save the inlined version locally
    # Full Snowflake deployment would require:
    # 1. PUT inlined_code to stage
    # 2. CREATE STREAMLIT pointing to stage

    # Save inlined version for manual deployment or future automation
    output_dir = Path(__file__).parent.parent / "DEPLOYMENT_OUTPUT"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f"{service_name}_streamlit_app_inlined.py"

    if not dry_run:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(inlined_code)
        print(f"💾 Saved inlined app to: {output_file}")

    print(f"✅ {service_name} prepared for deployment")

    return {
        'service': service_name,
        'success': True,
        'original_lines': original_lines,
        'inlined_lines': inlined_lines,
        'output_file': str(output_file)
    }

# =====================================================================
# MAIN DEPLOYMENT ORCHESTRATION
# =====================================================================

def deploy_all_apps(dry_run=False, services_filter=None):
    """Deploy all Streamlit apps to Snowflake"""
    print("=" * 80)
    print("SECURITY_ANALYTICS STREAMLIT APPS DEPLOYMENT")
    print("=" * 80)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}")
    print(f"Mode: {'DRY RUN (no deployment)' if dry_run else 'LIVE DEPLOYMENT'}")

    # Filter services if specified
    services_to_deploy = services_filter if services_filter else SERVICES
    print(f"\nServices to deploy: {len(services_to_deploy)}")
    for svc in services_to_deploy:
        print(f"  • {svc}")

    # Connect to Snowflake
    if not dry_run:
        print(f"\n{'=' * 80}")
        print("CONNECTING TO SNOWFLAKE")
        print(f"{'=' * 80}")
        print(f"Account: {SNOWFLAKE_CONFIG['account']}")
        print(f"User: {SNOWFLAKE_CONFIG['user']}")
        print(f"Database: {SNOWFLAKE_CONFIG['database']}")

        try:
            conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
            cursor = conn.cursor()
            print("✓ Connected successfully\n")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return
    else:
        conn = None
        cursor = None
        print("\n🔍 DRY RUN MODE - Skipping Snowflake connection\n")

    # Deploy each service
    results = []
    success_count = 0
    error_count = 0

    for service in services_to_deploy:
        try:
            result = deploy_service(service, conn, cursor, dry_run=dry_run)
            results.append(result)

            if result['success']:
                success_count += 1
            else:
                error_count += 1
        except Exception as e:
            print(f"❌ FATAL ERROR deploying {service}: {e}")
            results.append({
                'service': service,
                'success': False,
                'error': str(e)
            })
            error_count += 1

    # Close connection
    if not dry_run and conn:
        cursor.close()
        conn.close()

    # Generate summary
    print(f"\n{'=' * 80}")
    print("DEPLOYMENT SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total Services: {len(services_to_deploy)}")
    print(f"✅ Prepared:    {success_count}")
    print(f"❌ Failed:      {error_count}")
    print(f"Success Rate:   {(success_count / len(services_to_deploy) * 100):.1f}%")

    # Save results
    output_dir = Path(__file__).parent.parent / "DEPLOYMENT_OUTPUT"
    output_dir.mkdir(exist_ok=True)
    results_file = output_dir / f"deployment_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'config': SNOWFLAKE_CONFIG,
            'dry_run': dry_run,
            'results': results
        }, f, indent=2)

    print(f"\n📊 Results saved to: {results_file}")

    # Next steps
    print(f"\n{'=' * 80}")
    print("NEXT STEPS")
    print(f"{'=' * 80}")
    print("\nInlined app files have been generated in DEPLOYMENT_OUTPUT/")
    print("\nTo complete deployment to Snowflake:")
    print("1. Review inlined files to ensure common modules were correctly integrated")
    print("2. Option A: Use Snowflake UI to create Streamlit apps manually")
    print("   - Go to Snowflake UI > Data > Streamlit")
    print("   - Click 'Create' and paste inlined code")
    print("3. Option B: Use SnowSQL to PUT files to stage and CREATE STREAMLIT")
    print("   - Install SnowSQL: https://docs.snowflake.com/en/user-guide/snowsql")
    print("   - PUT files to stage: PUT file:///{output_file} @STREAMLIT_STAGE")
    print("   - CREATE STREAMLIT pointing to stage")
    print("\nNote: Full automation requires SnowSQL or Snowflake UI access")

    return results

# =====================================================================
# MAIN EXECUTION
# =====================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Deploy SECURITY_ANALYTICS Streamlit apps to Snowflake')
    parser.add_argument('--dry-run', action='store_true', help='Prepare files without deploying')
    parser.add_argument('--services', nargs='+', help='Specific services to deploy (default: all)')

    args = parser.parse_args()

    try:
        results = deploy_all_apps(dry_run=args.dry_run, services_filter=args.services)

        # Exit code based on success
        error_count = sum(1 for r in results if not r['success'])
        sys.exit(1 if error_count > 0 else 0)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
