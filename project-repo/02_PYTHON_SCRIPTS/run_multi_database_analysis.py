"""
Multi-Database Analysis Runner
==============================

Purpose:
    Execute analysis across all three databases:
    - DEV_LANDING.SECURITY_ANALYTICS
    - DEV_TRANSFORMATION.SECURITY_ANALYTICS
    - DEV_REPORTING.SECURITY_ANALYTICS

Usage:
    python run_multi_database_analysis.py [--format json|csv|both]

Author: Data Engineering Team
Last Updated: 2025-10-22
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import snowflake.connector
from dotenv import load_dotenv
import pandas as pd

# Load environment
env_paths = [Path('.env'), Path('03_CONFIG/.env')]
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded environment from: {env_path}\n")
        break

# Configuration
OUTPUT_DIR = Path("05_ANALYSIS_RESULTS")
SQL_SCRIPT_PATH = Path("01_SQL_SCRIPTS/06_Monitoring/DAILY_DATA_MODEL_ANALYSIS_BASIC.sql")

# Databases to analyze
DATABASES = ['DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING']
SCHEMA = 'SECURITY_ANALYTICS'

class MultiDatabaseAnalyzer:
    """Analyze multiple databases"""

    def __init__(self):
        self.connection = None
        self.cursor = None
        self.all_results = {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def connect(self):
        """Connect to Snowflake via SSO"""
        account = os.getenv('SNOWFLAKE_ACCOUNT')
        user = os.getenv('SNOWFLAKE_USER')

        if not account:
            print("ERROR: Missing SNOWFLAKE_ACCOUNT in .env")
            return False

        try:
            print("Connecting to Snowflake via SSO...")

            connection_params = {
                'account': account,
                'authenticator': 'externalbrowser',
                'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'QA_WH'),
                'role': os.getenv('SNOWFLAKE_ROLE', 'DEV_DEVELOPER')
            }

            if user:
                connection_params['user'] = user

            self.connection = snowflake.connector.connect(**connection_params)
            self.cursor = self.connection.cursor()

            # Get user info
            self.cursor.execute("SELECT CURRENT_USER(), CURRENT_ROLE()")
            result = self.cursor.fetchone()
            print(f"Connected as: {result[0]}, Role: {result[1]}\n")

            return True

        except Exception as e:
            print(f"ERROR connecting: {e}")
            return False

    def read_sql_script(self):
        """Read SQL script"""
        try:
            with open(SQL_SCRIPT_PATH, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"ERROR reading SQL: {e}")
            return None

    def execute_query(self, sql, section_name):
        """Execute single query"""
        try:
            self.cursor.execute(sql)
            columns = [desc[0] for desc in self.cursor.description]
            rows = self.cursor.fetchall()

            results = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    row_dict[col] = value
                results.append(row_dict)

            return results
        except Exception as e:
            print(f"    ERROR: {str(e)[:80]}")
            return None

    def analyze_database(self, database):
        """Analyze single database"""
        print(f"\n{'='*60}")
        print(f"Analyzing: {database}.{SCHEMA}")
        print(f"{'='*60}\n")

        try:
            # Set context
            self.cursor.execute(f"USE DATABASE {database}")
            self.cursor.execute(f"USE SCHEMA {SCHEMA}")
            print(f"  Context set: {database}.{SCHEMA}")

            # Read and parse SQL
            sql_content = self.read_sql_script()
            if not sql_content:
                return {}

            # Replace DEV_LANDING with current database name
            sql_content = sql_content.replace('DEV_LANDING.INFORMATION_SCHEMA', f'{database}.INFORMATION_SCHEMA')
            print(f"  SQL adapted for {database}")

            # Parse queries (simplified - split by SELECT)
            queries = []
            current = []
            for line in sql_content.split('\n'):
                if line.strip().upper().startswith('SELECT'):
                    if current:
                        queries.append('\n'.join(current))
                        current = []
                current.append(line)
                if line.strip().endswith(';'):
                    queries.append('\n'.join(current))
                    current = []

            # Execute each query
            results = {}
            for i, sql in enumerate(queries, 1):
                if not sql.strip() or 'USE DATABASE' in sql or 'USE SCHEMA' in sql:
                    continue

                # Extract section name
                section_name = f"Section_{i}"
                for line in sql.split('\n'):
                    if 'AS analysis_section' in line:
                        section_name = line.split("'")[1]
                        break

                print(f"  Executing: {section_name}...", end='')
                result = self.execute_query(sql, section_name)

                if result is not None:
                    results[section_name] = result
                    print(f" OK ({len(result)} rows)")
                else:
                    print()

            return results

        except Exception as e:
            print(f"  ERROR analyzing {database}: {e}")
            return {}

    def run_all_analyses(self):
        """Run analysis for all databases"""
        print(f"\n{'='*60}")
        print(f"Multi-Database Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        for database in DATABASES:
            results = self.analyze_database(database)
            if results:
                self.all_results[database] = results

        print(f"\nAnalyzed {len(self.all_results)} databases")
        return len(self.all_results) > 0

    def save_results(self, format='both'):
        """Save results to files"""
        print(f"\n{'='*60}")
        print("Saving Results")
        print(f"{'='*60}\n")

        OUTPUT_DIR.mkdir(exist_ok=True)

        # Save JSON
        if format in ['json', 'both']:
            filename = f"multi_database_analysis_{self.timestamp}.json"
            filepath = OUTPUT_DIR / filename

            output = {
                'metadata': {
                    'analysis_date': datetime.now().isoformat(),
                    'databases_analyzed': list(self.all_results.keys()),
                    'schema': SCHEMA,
                    'sections_per_db': {db: len(sections) for db, sections in self.all_results.items()}
                },
                'results': self.all_results
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, default=str)

            print(f"JSON saved: {filepath}")

        # Save CSV per database
        if format in ['csv', 'both']:
            saved_count = 0
            for database, sections in self.all_results.items():
                for section_name, data in sections.items():
                    if not data:
                        continue

                    clean_name = section_name.replace(' ', '_').replace('/', '_')
                    filename = f"analysis_{database}_{clean_name}_{self.timestamp}.csv"
                    filepath = OUTPUT_DIR / filename

                    df = pd.DataFrame(data)
                    df.to_csv(filepath, index=False, encoding='utf-8')
                    saved_count += 1

            print(f"CSV files saved: {saved_count} files")

    def close(self):
        """Close connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("\nConnection closed")


def main():
    parser = argparse.ArgumentParser(
        description='Run multi-database analysis across DEV_LANDING, DEV_TRANSFORMATION, DEV_REPORTING'
    )
    parser.add_argument(
        '--format',
        choices=['json', 'csv', 'both'],
        default='both',
        help='Output format (default: both)'
    )
    args = parser.parse_args()

    analyzer = MultiDatabaseAnalyzer()

    try:
        if not analyzer.connect():
            sys.exit(1)

        if not analyzer.run_all_analyses():
            sys.exit(1)

        analyzer.save_results(args.format)

        print(f"\n{'='*60}")
        print("Multi-database analysis completed!")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)
    finally:
        analyzer.close()


if __name__ == "__main__":
    main()
