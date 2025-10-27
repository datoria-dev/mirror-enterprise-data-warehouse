"""
Daily Data Model and Performance Analysis Runner
================================================

Purpose:
    Execute daily analysis SQL script and save results to JSON/CSV files
    for historical tracking and trending analysis.

Usage:
    python run_daily_analysis.py [--format json|csv|both]

Requirements:
    - Snowflake connection configured in .env file
    - Sufficient permissions to query ACCOUNT_USAGE views
    - Output directory with write permissions

Author: Data Engineering Team
Last Updated: 2025-10-22
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import snowflake.connector
from dotenv import load_dotenv
import pandas as pd

# Load environment variables from multiple possible locations
env_paths = [
    Path('.env'),
    Path('03_CONFIG/.env'),
    Path('../03_CONFIG/.env'),
    Path('.') / '03_CONFIG' / '.env'
]

env_loaded = False
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        env_loaded = True
        print(f"📝 Loaded environment from: {env_path}")
        break

if not env_loaded:
    print("⚠️  No .env file found. Trying environment variables...")

# Configuration
OUTPUT_DIR = Path("05_ANALYSIS_RESULTS")
# Use BASIC version that doesn't require ACCOUNT_USAGE access
SQL_SCRIPT_PATH = Path("01_SQL_SCRIPTS/06_Monitoring/DAILY_DATA_MODEL_ANALYSIS_BASIC.sql")

class SnowflakeAnalysisRunner:
    """Execute Snowflake analysis queries and save results"""

    def __init__(self):
        """Initialize Snowflake connection"""
        self.connection = None
        self.cursor = None
        self.results = {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def connect(self) -> bool:
        """Establish connection to Snowflake using SSO (browser-based authentication)"""
        # Get authentication method (default to SSO)
        auth_method = os.getenv('SNOWFLAKE_AUTH_METHOD', 'sso').lower()

        # Validate required environment variables
        account = os.getenv('SNOWFLAKE_ACCOUNT')
        user = os.getenv('SNOWFLAKE_USER')

        if not account:
            print(f"❌ Missing required environment variable: SNOWFLAKE_ACCOUNT")
            print(f"\n📋 Please create a .env file with at minimum:")
            print(f"   SNOWFLAKE_ACCOUNT=GenericCorp-CRH_EDW")
            print(f"   SNOWFLAKE_USER=your.email@CompanyX.com")
            print(f"\n💡 You can copy 03_CONFIG/.env.example to 03_CONFIG/.env")
            return False

        try:
            # Show connection details
            print(f"🔌 Connecting to Snowflake via SSO (Okta)...")
            print(f"   Account: {account}")
            print(f"   User: {user or 'Will prompt in browser'}")
            print(f"   Warehouse: {os.getenv('SNOWFLAKE_WAREHOUSE', 'QA_WH')}")
            print(f"   Database: {os.getenv('SNOWFLAKE_DATABASE', 'DEV_LANDING')}")
            print(f"   Schema: {os.getenv('SNOWFLAKE_SCHEMA', 'SECURITY_ANALYTICS')}")
            print(f"   Role: {os.getenv('SNOWFLAKE_ROLE', 'DEV_DEVELOPER')}")
            print(f"\n🌐 Opening browser for Okta authentication...")
            print(f"   Please complete authentication in your browser window...")

            # Connection parameters for SSO
            connection_params = {
                'account': account,
                'authenticator': 'externalbrowser',  # This triggers SSO via browser
                'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'QA_WH'),
                'database': os.getenv('SNOWFLAKE_DATABASE', 'DEV_LANDING'),
                'schema': os.getenv('SNOWFLAKE_SCHEMA', 'SECURITY_ANALYTICS'),
                'role': os.getenv('SNOWFLAKE_ROLE', 'DEV_DEVELOPER')
            }

            # Add user if provided (optional for SSO)
            if user:
                connection_params['user'] = user

            self.connection = snowflake.connector.connect(**connection_params)
            self.cursor = self.connection.cursor()

            # Set database and schema context explicitly
            database = os.getenv('SNOWFLAKE_DATABASE', 'DEV_LANDING')
            schema = os.getenv('SNOWFLAKE_SCHEMA', 'SECURITY_ANALYTICS')

            print(f"   Setting context: {database}.{schema}")
            self.cursor.execute(f"USE DATABASE {database}")
            self.cursor.execute(f"USE SCHEMA {schema}")

            # Get actual user and context after successful SSO
            self.cursor.execute("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
            result = self.cursor.fetchone()
            actual_user = result[0] if result else 'Unknown'
            actual_role = result[1] if result else 'Unknown'
            actual_db = result[2] if result else 'Unknown'
            actual_schema = result[3] if result else 'Unknown'

            print(f"✅ Connected to Snowflake successfully!")
            print(f"   Authenticated as: {actual_user}")
            print(f"   Using role: {actual_role}")
            print(f"   Context: {actual_db}.{actual_schema}\n")
            return True

        except Exception as e:
            print(f"❌ Error connecting to Snowflake: {e}")
            print(f"\n💡 Common issues:")
            print(f"   - Browser popup may be blocked - check your browser")
            print(f"   - Verify you have access to Snowflake via Okta")
            print(f"   - Check account identifier: GenericCorp-CRH_EDW")
            print(f"   - Ensure role has necessary permissions for ACCOUNT_USAGE views")
            print(f"   - Try closing any existing Snowflake browser sessions")
            return False

    def read_sql_script(self) -> Optional[str]:
        """Read the SQL script file"""
        try:
            with open(SQL_SCRIPT_PATH, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            print(f"✅ SQL script loaded: {SQL_SCRIPT_PATH}")
            return sql_content
        except Exception as e:
            print(f"❌ Error reading SQL script: {e}")
            return None

    def parse_sql_sections(self, sql_content: str) -> List[Dict[str, str]]:
        """
        Parse SQL script into individual query sections
        Each section starts with a SELECT statement
        """
        queries = []
        current_query = []
        in_query = False

        for line in sql_content.split('\n'):
            line_stripped = line.strip()

            # Skip empty lines and comment-only lines
            if not line_stripped or line_stripped.startswith('--'):
                if in_query:
                    current_query.append(line)
                continue

            # Detect start of a new query
            if line_stripped.upper().startswith('SELECT'):
                if current_query:
                    # Save previous query
                    query_text = '\n'.join(current_query)
                    queries.append({'sql': query_text})
                    current_query = []
                in_query = True

            if in_query:
                current_query.append(line)

                # Detect end of query (semicolon on its own line or at end)
                if line_stripped.endswith(';'):
                    query_text = '\n'.join(current_query)
                    queries.append({'sql': query_text})
                    current_query = []
                    in_query = False

        # Add last query if exists
        if current_query:
            query_text = '\n'.join(current_query)
            queries.append({'sql': query_text})

        print(f"✅ Parsed {len(queries)} query sections")
        return queries

    def execute_query(self, sql: str, section_name: str = "Unknown") -> Optional[List[Dict]]:
        """Execute a single query and return results as list of dicts"""
        try:
            print(f"  Executing: {section_name}...", end='')
            self.cursor.execute(sql)

            # Get column names
            columns = [desc[0] for desc in self.cursor.description]

            # Fetch all results
            rows = self.cursor.fetchall()

            # Convert to list of dicts
            results = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # Convert datetime objects to strings
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    row_dict[col] = value
                results.append(row_dict)

            print(f" ✅ ({len(results)} rows)")
            return results

        except Exception as e:
            print(f" ❌ Error: {str(e)[:100]}")
            return None

    def run_analysis(self) -> bool:
        """Execute all analysis queries and collect results"""
        print(f"\n{'='*60}")
        print(f"Starting Daily Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        # Read SQL script
        sql_content = self.read_sql_script()
        if not sql_content:
            return False

        # Parse into sections
        queries = self.parse_sql_sections(sql_content)

        # Execute each query
        for i, query_dict in enumerate(queries, 1):
            sql = query_dict['sql']

            # Extract section name from first row if it includes analysis_section
            section_name = f"Section_{i}"
            if 'analysis_section' in sql.lower():
                # Try to extract section name from SELECT
                for line in sql.split('\n'):
                    if 'AS analysis_section' in line:
                        section_name = line.split("'")[1]
                        break

            # Execute query
            results = self.execute_query(sql, section_name)

            if results is not None:
                # Store results
                if results:  # Only store if we got results
                    self.results[section_name] = results
                else:
                    self.results[section_name] = []

        print(f"\n✅ Analysis completed: {len(self.results)} sections executed")
        return True

    def save_to_json(self) -> str:
        """Save results to JSON file"""
        try:
            OUTPUT_DIR.mkdir(exist_ok=True)
            filename = f"daily_analysis_{self.timestamp}.json"
            filepath = OUTPUT_DIR / filename

            # Add metadata
            output = {
                'metadata': {
                    'analysis_date': datetime.now().isoformat(),
                    'database': os.getenv('SNOWFLAKE_DATABASE', 'ITSECKPI_DEV'),
                    'sections_count': len(self.results),
                    'total_rows': sum(len(v) for v in self.results.values())
                },
                'results': self.results
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, default=str)

            print(f"✅ JSON saved: {filepath}")
            return str(filepath)

        except Exception as e:
            print(f"❌ Error saving JSON: {e}")
            return ""

    def save_to_csv(self) -> List[str]:
        """Save each section to a separate CSV file"""
        saved_files = []
        try:
            OUTPUT_DIR.mkdir(exist_ok=True)

            for section_name, data in self.results.items():
                if not data:  # Skip empty sections
                    continue

                # Clean section name for filename
                clean_name = section_name.replace(' ', '_').replace('/', '_')
                filename = f"daily_analysis_{clean_name}_{self.timestamp}.csv"
                filepath = OUTPUT_DIR / filename

                # Convert to DataFrame and save
                df = pd.DataFrame(data)
                df.to_csv(filepath, index=False, encoding='utf-8')

                saved_files.append(str(filepath))

            print(f"✅ CSV files saved: {len(saved_files)} files")
            return saved_files

        except Exception as e:
            print(f"❌ Error saving CSV: {e}")
            return []

    def close(self):
        """Close Snowflake connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("✅ Connection closed")


def main():
    """Main execution function"""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Run daily Snowflake data model and performance analysis'
    )
    parser.add_argument(
        '--format',
        choices=['json', 'csv', 'both'],
        default='both',
        help='Output format (default: both)'
    )
    args = parser.parse_args()

    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Initialize runner
    runner = SnowflakeAnalysisRunner()

    try:
        # Connect to Snowflake
        if not runner.connect():
            sys.exit(1)

        # Run analysis
        if not runner.run_analysis():
            sys.exit(1)

        # Save results
        print(f"\n{'='*60}")
        print("Saving Results")
        print(f"{'='*60}\n")

        if args.format in ['json', 'both']:
            runner.save_to_json()

        if args.format in ['csv', 'both']:
            runner.save_to_csv()

        print(f"\n{'='*60}")
        print(f"✅ Daily analysis completed successfully!")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        sys.exit(1)

    finally:
        runner.close()


if __name__ == "__main__":
    main()
