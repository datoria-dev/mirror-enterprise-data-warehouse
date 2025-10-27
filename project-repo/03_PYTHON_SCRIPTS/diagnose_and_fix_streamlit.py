"""
Diagnose and Fix Streamlit Deployment Issues
Checks stage structure and fixes deployment problems

Author: Data Engineering Team
Date: 2025-10-24
"""

import snowflake.connector
import sys
from pathlib import Path
from datetime import datetime

# Force UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

SNOWFLAKE_CONFIG = {
    'account': 'GenericCorp-CRH_EDW',
    'user': 'FUAD.ONATE@CompanyX.COM',
    'authenticator': 'externalbrowser',
    'warehouse': 'DEV_WH',
    'database': 'DEV_REPORTING',
    'schema': 'SECURITY_ANALYTICS',
    'role': 'DEV_DEVELOPER'
}

def diagnose_stage(cursor):
    """Check what's in the stage"""
    print("\n" + "=" * 80)
    print("DIAGNOSING STAGE STRUCTURE")
    print("=" * 80)

    # List stage contents
    sql = f"""
LIST @{SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.STREAMLIT_STAGE
"""

    try:
        cursor.execute(sql)
        files = cursor.fetchall()

        print(f"\n📁 Found {len(files)} files in stage:")
        for file in files[:20]:  # Show first 20
            name = file[0]
            size = file[1]
            print(f"   {name} ({size} bytes)")

        return files
    except Exception as e:
        print(f"❌ Error listing stage: {e}")
        return []

def check_specific_service(cursor, service):
    """Check files for a specific service"""
    print(f"\n🔍 Checking {service} files:")

    sql = f"""
LIST @{SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.STREAMLIT_STAGE/{service}/
"""

    try:
        cursor.execute(sql)
        files = cursor.fetchall()

        if files:
            for file in files:
                name = file[0]
                size = file[1]
                print(f"   ✅ {name} ({size} bytes)")
        else:
            print(f"   ❌ No files found for {service}")

        return files
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return []

def fix_deployment_method1(cursor, service):
    """Method 1: Put file directly without subdirectory"""
    print(f"\n🔧 Fix Method 1: Direct PUT for {service}")

    local_file = Path(__file__).parent.parent / "DEPLOYMENT_OUTPUT" / f"{service}_streamlit_app_inlined.py"

    if not local_file.exists():
        print(f"   ❌ Local file not found")
        return False

    try:
        # Remove existing files
        sql_remove = f"""
REMOVE @{SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.STREAMLIT_STAGE/{service}/
"""
        try:
            cursor.execute(sql_remove)
            print(f"   🗑️ Removed old files")
        except:
            pass

        # Put file directly
        local_file_str = str(local_file).replace('\\', '/')
        sql = f"""
PUT 'file://{local_file_str}'
  @{SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.STREAMLIT_STAGE
  AUTO_COMPRESS = FALSE
  OVERWRITE = TRUE
"""

        cursor.execute(sql)
        print(f"   ✅ Uploaded file directly to stage root")

        # Rename in stage
        sql_cp = f"""
COPY FILES
  INTO @{SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.STREAMLIT_STAGE/{service}/streamlit_app.py
  FROM @{SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.STREAMLIT_STAGE/{service}_streamlit_app_inlined.py
"""

        try:
            cursor.execute(sql_cp)
            print(f"   ✅ Renamed to streamlit_app.py")
        except Exception as e:
            print(f"   ⚠️ Copy failed (may need manual fix): {e}")

        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def recreate_app_simple(cursor, service):
    """Recreate app with simplified approach"""
    app_name = f"{service.upper()}_APP"

    print(f"\n🚀 Recreating {app_name} (simplified)...")

    # Method 1: Try with subdirectory
    sql1 = f"""
CREATE OR REPLACE STREAMLIT {SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.{app_name}
  ROOT_LOCATION = '@{SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.STREAMLIT_STAGE/{service}/'
  MAIN_FILE = 'streamlit_app.py'
  QUERY_WAREHOUSE = '{SNOWFLAKE_CONFIG['warehouse']}'
"""

    try:
        cursor.execute(sql1)
        print(f"   ✅ Created with subdirectory structure")
        return True
    except Exception as e:
        print(f"   ⚠️ Subdirectory method failed: {e}")

    # Method 2: Try without subdirectory
    sql2 = f"""
CREATE OR REPLACE STREAMLIT {SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.{app_name}
  ROOT_LOCATION = '@{SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}.STREAMLIT_STAGE'
  MAIN_FILE = '{service}_streamlit_app.py'
  QUERY_WAREHOUSE = '{SNOWFLAKE_CONFIG['warehouse']}'
"""

    try:
        cursor.execute(sql2)
        print(f"   ✅ Created with flat structure")
        return True
    except Exception as e:
        print(f"   ❌ Both methods failed: {e}")
        return False

def create_git_deployment_approach(service):
    """Generate Git-based deployment approach"""
    print(f"\n📚 Git Deployment Alternative for {service}:")
    print(f"""
    1. Push code to Git repository (GitHub/GitLab/Azure Repos)
    2. In Snowflake UI:
       - Go to the Streamlit app
       - Click 'Connect Git Repository'
       - Enter repository URL
       - Select branch (main/master)
       - Path to streamlit_app.py
    3. Benefits:
       - Version control
       - CI/CD integration
       - Easier updates
       - No stage management issues
    """)

def main():
    print("=" * 80)
    print("STREAMLIT DEPLOYMENT DIAGNOSTICS")
    print("=" * 80)

    # Connect
    try:
        conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
        cursor = conn.cursor()
        print("✅ Connected to Snowflake\n")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    try:
        # Diagnose
        files = diagnose_stage(cursor)

        # Check specific services
        test_services = ['Ancon', 'Zerofox', 'Leviat']
        for service in test_services:
            check_specific_service(cursor, service)

        # Try to fix one as test
        print("\n" + "=" * 80)
        print("ATTEMPTING FIX")
        print("=" * 80)

        # Fix Ancon as test
        if fix_deployment_method1(cursor, 'Ancon'):
            recreate_app_simple(cursor, 'Ancon')

        # Show Git alternative
        create_git_deployment_approach('Ancon')

        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)
        print("""
        ✅ BEST APPROACH: Use Git-based deployment
           - Push inlined files to Azure DevOps repo
           - Connect apps to Git repository
           - Automatic updates on push

        🔧 QUICK FIX: Manual upload in UI
           - Copy content from DEPLOYMENT_OUTPUT/*_inlined.py
           - Paste directly in Snowflake Streamlit editor
           - Save and run

        📁 STAGE FIX: Restructure stage files
           - Each app needs its own subdirectory
           - File must be named exactly 'streamlit_app.py'
           - No compression, correct permissions
        """)

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()