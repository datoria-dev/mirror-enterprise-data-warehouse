"""
Historical Analysis Results Analyzer
====================================

Purpose:
    Read and analyze historical daily analysis results to identify trends,
    anomalies, and performance patterns over time.

Usage:
    python analyze_historical_results.py [--days 30] [--section SECTION_NAME]

Features:
    - Trend analysis across multiple days
    - Performance degradation detection
    - Storage growth tracking
    - Query performance patterns
    - Error rate monitoring
    - Automated alerting for anomalies

Author: Data Engineering Team
Last Updated: 2025-10-22
"""

import os
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
import statistics

# Configuration
RESULTS_DIR = Path("05_ANALYSIS_RESULTS")

class HistoricalAnalyzer:
    """Analyze historical analysis results"""

    def __init__(self, days: int = 30):
        """
        Initialize analyzer

        Args:
            days: Number of days of history to analyze
        """
        self.days = days
        self.results_files = []
        self.data = {}
        self.trends = {}
        self.alerts = []

    def load_results(self) -> bool:
        """Load all JSON result files from the specified period"""
        try:
            if not RESULTS_DIR.exists():
                print(f"❌ Results directory not found: {RESULTS_DIR}")
                return False

            # Get all JSON files
            all_files = list(RESULTS_DIR.glob("daily_analysis_*.json"))

            if not all_files:
                print(f"❌ No analysis result files found in {RESULTS_DIR}")
                return False

            # Sort by date (newest first)
            all_files.sort(reverse=True)

            # Filter by date range
            cutoff_date = datetime.now() - timedelta(days=self.days)

            for filepath in all_files:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Check if within date range
                    analysis_date = datetime.fromisoformat(data['metadata']['analysis_date'])
                    if analysis_date >= cutoff_date:
                        self.results_files.append({
                            'filepath': filepath,
                            'date': analysis_date,
                            'data': data
                        })
                except Exception as e:
                    print(f"⚠️  Skipping file {filepath.name}: {e}")

            self.results_files.sort(key=lambda x: x['date'])

            print(f"✅ Loaded {len(self.results_files)} result files from last {self.days} days")
            return True

        except Exception as e:
            print(f"❌ Error loading results: {e}")
            return False

    def analyze_storage_trends(self) -> Dict[str, Any]:
        """Analyze storage growth trends"""
        print("\n" + "="*60)
        print("STORAGE TREND ANALYSIS")
        print("="*60)

        storage_data = []

        for result in self.results_files:
            try:
                storage_section = result['data']['results'].get('STORAGE_COSTS', [])
                if storage_section:
                    for row in storage_section:
                        storage_data.append({
                            'date': result['date'],
                            'schema': row.get('SCHEMA_NAME'),
                            'size_gb': float(row.get('TOTAL_SIZE_GB', 0)),
                            'table_count': int(row.get('TABLE_COUNT', 0)),
                            'monthly_cost': float(row.get('ESTIMATED_MONTHLY_COST_USD', 0))
                        })
            except Exception as e:
                continue

        if not storage_data:
            print("⚠️  No storage data available")
            return {}

        df = pd.DataFrame(storage_data)

        # Calculate growth rates
        trends = {}
        for schema in df['schema'].unique():
            schema_df = df[df['schema'] == schema].sort_values('date')

            if len(schema_df) >= 2:
                first_size = schema_df.iloc[0]['size_gb']
                last_size = schema_df.iloc[-1]['size_gb']
                days_diff = (schema_df.iloc[-1]['date'] - schema_df.iloc[0]['date']).days

                if days_diff > 0 and first_size > 0:
                    daily_growth = (last_size - first_size) / days_diff
                    growth_pct = ((last_size - first_size) / first_size) * 100

                    trends[schema] = {
                        'first_size_gb': round(first_size, 2),
                        'last_size_gb': round(last_size, 2),
                        'growth_gb': round(last_size - first_size, 2),
                        'growth_pct': round(growth_pct, 2),
                        'daily_growth_gb': round(daily_growth, 2),
                        'days_analyzed': days_diff,
                        'current_monthly_cost': round(schema_df.iloc[-1]['monthly_cost'], 2)
                    }

                    print(f"\n{schema}:")
                    print(f"  Current Size: {trends[schema]['last_size_gb']} GB")
                    print(f"  Growth: {trends[schema]['growth_gb']} GB ({trends[schema]['growth_pct']}%)")
                    print(f"  Daily Growth: {trends[schema]['daily_growth_gb']} GB/day")
                    print(f"  Monthly Cost: ${trends[schema]['current_monthly_cost']}")

                    # Alert on high growth
                    if growth_pct > 50 and days_diff >= 7:
                        alert = f"HIGH STORAGE GROWTH: {schema} grew {growth_pct:.1f}% in {days_diff} days"
                        self.alerts.append(alert)
                        print(f"  🚨 ALERT: {alert}")

        return trends

    def analyze_query_performance(self) -> Dict[str, Any]:
        """Analyze query performance trends"""
        print("\n" + "="*60)
        print("QUERY PERFORMANCE TREND ANALYSIS")
        print("="*60)

        perf_data = []

        for result in self.results_files:
            try:
                summary = result['data']['results'].get('DAILY_SUMMARY', [])
                if summary and len(summary) > 0:
                    row = summary[0]
                    perf_data.append({
                        'date': result['date'],
                        'total_queries': int(row.get('TOTAL_QUERIES_24H', 0)),
                        'avg_time_seconds': float(row.get('AVG_QUERY_TIME_SECONDS', 0)),
                        'error_count': int(row.get('ERROR_COUNT_24H', 0)),
                        'storage_gb': float(row.get('TOTAL_STORAGE_GB', 0))
                    })
            except Exception as e:
                continue

        if not perf_data:
            print("⚠️  No performance data available")
            return {}

        df = pd.DataFrame(perf_data).sort_values('date')

        # Calculate statistics
        trends = {
            'avg_queries_per_day': round(df['total_queries'].mean(), 0),
            'avg_query_time': round(df['avg_time_seconds'].mean(), 2),
            'avg_errors_per_day': round(df['error_count'].mean(), 1),
            'total_storage_gb': round(df['storage_gb'].iloc[-1], 2) if len(df) > 0 else 0
        }

        # Calculate trends
        if len(df) >= 7:
            recent_avg_time = df.tail(7)['avg_time_seconds'].mean()
            older_avg_time = df.head(7)['avg_time_seconds'].mean()

            if older_avg_time > 0:
                time_change_pct = ((recent_avg_time - older_avg_time) / older_avg_time) * 100
                trends['query_time_change_pct'] = round(time_change_pct, 2)

                if time_change_pct > 20:
                    alert = f"QUERY PERFORMANCE DEGRADATION: Avg query time increased {time_change_pct:.1f}%"
                    self.alerts.append(alert)
                    print(f"🚨 ALERT: {alert}")

        print(f"\nAverage Daily Metrics:")
        print(f"  Queries per day: {trends['avg_queries_per_day']}")
        print(f"  Avg query time: {trends['avg_query_time']} seconds")
        print(f"  Errors per day: {trends['avg_errors_per_day']}")
        print(f"  Current storage: {trends['total_storage_gb']} GB")

        if 'query_time_change_pct' in trends:
            direction = "increased" if trends['query_time_change_pct'] > 0 else "decreased"
            print(f"  Query time trend: {direction} {abs(trends['query_time_change_pct'])}%")

        return trends

    def analyze_slow_queries(self) -> Dict[str, Any]:
        """Analyze slow query patterns"""
        print("\n" + "="*60)
        print("SLOW QUERY ANALYSIS")
        print("="*60)

        slow_queries = []

        for result in self.results_files:
            try:
                slow_section = result['data']['results'].get('SLOW_QUERIES', [])
                for row in slow_section:
                    slow_queries.append({
                        'date': result['date'],
                        'query_id': row.get('QUERY_ID'),
                        'execution_seconds': float(row.get('EXECUTION_SECONDS', 0)),
                        'schema': row.get('SCHEMA_NAME'),
                        'query_type': row.get('QUERY_TYPE'),
                        'gb_scanned': float(row.get('GB_SCANNED', 0)),
                        'user': row.get('USER_NAME')
                    })
            except Exception as e:
                continue

        if not slow_queries:
            print("✅ No slow queries detected")
            return {}

        df = pd.DataFrame(slow_queries)

        # Top slow query patterns
        print(f"\nTotal slow queries (>10s) in period: {len(df)}")
        print(f"Average slow query time: {df['execution_seconds'].mean():.2f} seconds")
        print(f"Max query time: {df['execution_seconds'].max():.2f} seconds")

        # By schema
        print(f"\nSlow queries by schema:")
        schema_counts = df['schema'].value_counts()
        for schema, count in schema_counts.head(5).items():
            avg_time = df[df['schema'] == schema]['execution_seconds'].mean()
            print(f"  {schema}: {count} queries (avg: {avg_time:.2f}s)")

        # By query type
        print(f"\nSlow queries by type:")
        type_counts = df['query_type'].value_counts()
        for qtype, count in type_counts.head(5).items():
            avg_time = df[df['query_type'] == qtype]['execution_seconds'].mean()
            print(f"  {qtype}: {count} queries (avg: {avg_time:.2f}s)")

        # Alert on excessive slow queries
        slow_per_day = len(df) / max(len(self.results_files), 1)
        if slow_per_day > 10:
            alert = f"HIGH SLOW QUERY RATE: {slow_per_day:.1f} slow queries per day"
            self.alerts.append(alert)
            print(f"\n🚨 ALERT: {alert}")

        return {
            'total_slow_queries': len(df),
            'avg_execution_time': round(df['execution_seconds'].mean(), 2),
            'max_execution_time': round(df['execution_seconds'].max(), 2),
            'slow_queries_per_day': round(slow_per_day, 1)
        }

    def analyze_task_health(self) -> Dict[str, Any]:
        """Analyze task execution health"""
        print("\n" + "="*60)
        print("TASK HEALTH ANALYSIS")
        print("="*60)

        task_data = []

        for result in self.results_files:
            try:
                summary = result['data']['results'].get('DAILY_SUMMARY', [])
                if summary and len(summary) > 0:
                    row = summary[0]
                    task_data.append({
                        'date': result['date'],
                        'successful_tasks': int(row.get('SUCCESSFUL_TASKS_24H', 0)),
                        'failed_tasks': int(row.get('FAILED_TASKS_24H', 0))
                    })
            except Exception as e:
                continue

        if not task_data:
            print("⚠️  No task data available")
            return {}

        df = pd.DataFrame(task_data)

        total_success = df['successful_tasks'].sum()
        total_failure = df['failed_tasks'].sum()
        total_tasks = total_success + total_failure

        if total_tasks > 0:
            success_rate = (total_success / total_tasks) * 100
        else:
            success_rate = 0

        print(f"\nTask Execution Summary:")
        print(f"  Total successful: {total_success}")
        print(f"  Total failed: {total_failure}")
        print(f"  Success rate: {success_rate:.1f}%")
        print(f"  Avg tasks/day: {total_tasks / len(df):.1f}")

        # Alert on low success rate
        if success_rate < 95 and total_tasks > 10:
            alert = f"LOW TASK SUCCESS RATE: {success_rate:.1f}% ({total_failure} failures)"
            self.alerts.append(alert)
            print(f"\n🚨 ALERT: {alert}")

        return {
            'total_successful': int(total_success),
            'total_failed': int(total_failure),
            'success_rate_pct': round(success_rate, 2),
            'avg_tasks_per_day': round(total_tasks / len(df), 1)
        }

    def generate_summary_report(self) -> str:
        """Generate comprehensive summary report"""
        print("\n" + "="*60)
        print("SUMMARY REPORT")
        print("="*60)

        report = []
        report.append(f"\nHistorical Analysis Report")
        report.append(f"Period: Last {self.days} days")
        report.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Files Analyzed: {len(self.results_files)}")
        report.append("\n" + "="*60)

        # Alerts
        if self.alerts:
            report.append(f"\n🚨 ALERTS ({len(self.alerts)}):")
            for i, alert in enumerate(self.alerts, 1):
                report.append(f"  {i}. {alert}")
        else:
            report.append("\n✅ No alerts - all metrics within normal ranges")

        # Trends summary
        if self.trends:
            report.append("\n" + "="*60)
            report.append("KEY TRENDS:")

            for category, data in self.trends.items():
                report.append(f"\n{category.upper()}:")
                for key, value in data.items():
                    report.append(f"  {key}: {value}")

        report_text = "\n".join(report)
        print(report_text)

        # Save to file
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = RESULTS_DIR / f"historical_analysis_report_{timestamp}.txt"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"\n✅ Report saved to: {report_path}")
        except Exception as e:
            print(f"⚠️  Could not save report: {e}")

        return report_text

    def analyze_specific_section(self, section_name: str):
        """Analyze a specific section in detail"""
        print("\n" + "="*60)
        print(f"DETAILED ANALYSIS: {section_name}")
        print("="*60)

        all_data = []

        for result in self.results_files:
            try:
                section_data = result['data']['results'].get(section_name, [])
                for row in section_data:
                    row_copy = row.copy()
                    row_copy['analysis_date'] = result['date'].strftime('%Y-%m-%d')
                    all_data.append(row_copy)
            except Exception as e:
                continue

        if not all_data:
            print(f"⚠️  No data found for section: {section_name}")
            return

        df = pd.DataFrame(all_data)

        print(f"\nTotal records: {len(df)}")
        print(f"\nColumns: {', '.join(df.columns)}")
        print(f"\nFirst few records:")
        print(df.head(10).to_string())

        # Save to CSV
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_path = RESULTS_DIR / f"detailed_analysis_{section_name}_{timestamp}.csv"
            df.to_csv(csv_path, index=False)
            print(f"\n✅ Detailed data saved to: {csv_path}")
        except Exception as e:
            print(f"⚠️  Could not save CSV: {e}")


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Analyze historical daily analysis results'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days of history to analyze (default: 30)'
    )
    parser.add_argument(
        '--section',
        type=str,
        help='Analyze specific section in detail'
    )
    args = parser.parse_args()

    # Initialize analyzer
    analyzer = HistoricalAnalyzer(days=args.days)

    # Load results
    if not analyzer.load_results():
        return

    # Run specific section analysis if requested
    if args.section:
        analyzer.analyze_specific_section(args.section)
        return

    # Run all analyses
    print("\nRunning comprehensive historical analysis...")

    analyzer.trends['storage'] = analyzer.analyze_storage_trends()
    analyzer.trends['performance'] = analyzer.analyze_query_performance()
    analyzer.trends['slow_queries'] = analyzer.analyze_slow_queries()
    analyzer.trends['task_health'] = analyzer.analyze_task_health()

    # Generate summary report
    analyzer.generate_summary_report()


if __name__ == "__main__":
    main()
