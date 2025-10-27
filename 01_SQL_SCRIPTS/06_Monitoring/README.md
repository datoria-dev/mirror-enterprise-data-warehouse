# Daily Data Model and Performance Monitoring

## Overview

This monitoring system provides automated daily analysis of the Snowflake SECURITY_ANALYTICS data warehouse, tracking data model health, query performance, storage costs, and operational metrics.

## Components

### 1. SQL Analysis Script
**File**: `DAILY_DATA_MODEL_PERFORMANCE_ANALYSIS.sql`

Comprehensive SQL script that analyzes 13 key areas:

1. **Object Inventory** - Count and size of all database objects
2. **Table Size Analysis** - Growth tracking and largest tables
3. **Query Performance** - Execution times and patterns (24h)
4. **Slow Queries** - Queries requiring optimization (>10s)
5. **Data Quality** - Freshness and completeness metrics
6. **Warehouse Utilization** - Compute resource usage
7. **Constraint Coverage** - Data integrity verification
8. **Task Execution** - Automation health (24h)
9. **Storage Costs** - Cost breakdown by layer
10. **Error Summary** - Query failures and issues (24h)
11. **Materialized Views** - Refresh status
12. **User Activity** - Top users by query volume (24h)
13. **Summary Dashboard** - High-level KPIs

### 2. Python Execution Script
**File**: `02_PYTHON_SCRIPTS/run_daily_analysis.py`

Executes the SQL analysis and saves results in JSON/CSV format.

**Usage**:
```bash
# Run analysis and save both JSON and CSV
python run_daily_analysis.py

# Save only JSON
python run_daily_analysis.py --format json

# Save only CSV
python run_daily_analysis.py --format csv
```

**Output**:
- JSON: Single file with all analysis sections
- CSV: Separate files per analysis section
- Location: `06_ANALYSIS_RESULTS/`

### 3. Historical Analysis Script
**File**: `02_PYTHON_SCRIPTS/analyze_historical_results.py`

Analyzes historical trends and identifies anomalies.

**Usage**:
```bash
# Analyze last 30 days
python analyze_historical_results.py

# Analyze last 90 days
python analyze_historical_results.py --days 90

# Detailed analysis of specific section
python analyze_historical_results.py --section STORAGE_COSTS
```

**Features**:
- Storage growth trend analysis
- Query performance degradation detection
- Slow query pattern identification
- Task health monitoring
- Automated alerting for anomalies
- Comprehensive summary reports

## Setup Instructions

### Prerequisites

1. **Snowflake Access**:
   - ACCOUNTADMIN or role with access to `SNOWFLAKE.ACCOUNT_USAGE` views
   - Permissions to query all three layers (LANDING, TRANSFORMATION, REPORTING)

2. **Python Environment**:
   ```bash
   pip install snowflake-connector-python pandas python-dotenv
   ```

3. **Environment Configuration**:
   Create or update `.env` file:
   ```env
   SNOWFLAKE_USER=your_username
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_ACCOUNT=your_account
   SNOWFLAKE_WAREHOUSE=DEV_WH
   SNOWFLAKE_DATABASE=ITSECKPI_DEV
   SNOWFLAKE_SCHEMA=DEV_TRANSFORMATION
   SNOWFLAKE_ROLE=DEVELOPER  # or ACCOUNTADMIN for ACCOUNT_USAGE access
   ```

### Directory Structure

```
Project Root/
├── 01_SQL_SCRIPTS/
│   └── 06_Monitoring/
│       ├── DAILY_DATA_MODEL_PERFORMANCE_ANALYSIS.sql
│       └── README.md (this file)
├── 02_PYTHON_SCRIPTS/
│   ├── run_daily_analysis.py
│   └── analyze_historical_results.py
├── 03_CONFIG/
│   └── .env
└── 06_ANALYSIS_RESULTS/
    ├── daily_analysis_YYYYMMDD_HHMMSS.json
    ├── daily_analysis_SECTION_NAME_YYYYMMDD_HHMMSS.csv
    └── historical_analysis_report_YYYYMMDD_HHMMSS.txt
```

## Usage Workflow

### Daily Execution

**Recommended Schedule**: Run daily at 6:00 AM (after ETL completes)

1. **Execute Analysis**:
   ```bash
   python 02_PYTHON_SCRIPTS/run_daily_analysis.py
   ```

2. **Review Results**:
   - Check `06_ANALYSIS_RESULTS/` for latest files
   - Review JSON for complete data
   - Open CSV files in Excel/spreadsheet for section-specific analysis

3. **Weekly Trend Analysis**:
   ```bash
   python 02_PYTHON_SCRIPTS/analyze_historical_results.py --days 7
   ```

4. **Monthly Review**:
   ```bash
   python 02_PYTHON_SCRIPTS/analyze_historical_results.py --days 30
   ```

### VS Code + Integration

**Run from VS Code Terminal**:
1. Open integrated terminal (Ctrl+`)
2. Navigate to project root
3. Execute analysis scripts

**Schedule with Task Scheduler (Windows)**:
```powershell
# Create scheduled task
schtasks /create /tn "Snowflake Daily Analysis" /tr "python C:\path\to\run_daily_analysis.py" /sc daily /st 06:00
```

**Schedule with Cron (Linux/Mac)**:
```bash
# Add to crontab
0 6 * * * cd /path/to/project && python run_daily_analysis.py
```

## Interpreting Results

### Key Metrics to Monitor

**Storage Costs**:
- Alert if daily growth > 5 GB
- Alert if monthly cost increases > 20%

**Query Performance**:
- Target: Avg query time < 5 seconds
- Alert if avg time increases > 20% week-over-week

**Slow Queries**:
- Target: < 5 slow queries per day
- Investigate queries > 30 seconds

**Task Health**:
- Target: > 95% success rate
- Alert on any failed tasks

**Data Freshness**:
- Target: All tables updated within 24 hours
- Alert on tables stale > 48 hours

### Alert Thresholds

The historical analyzer automatically generates alerts for:
- Storage growth > 50% in 7 days
- Query time degradation > 20%
- Slow query rate > 10/day
- Task success rate < 95%

## Example Outputs

### JSON Output Structure
```json
{
  "metadata": {
    "analysis_date": "2025-10-22T06:00:00",
    "database": "ITSECKPI_DEV",
    "sections_count": 13,
    "total_rows": 1247
  },
  "results": {
    "OBJECT_INVENTORY": [...],
    "TABLE_SIZE_ANALYSIS": [...],
    "QUERY_PERFORMANCE": [...],
    ...
  }
}
```

### CSV Output Files
- `daily_analysis_OBJECT_INVENTORY_20251022_060000.csv`
- `daily_analysis_TABLE_SIZE_ANALYSIS_20251022_060000.csv`
- `daily_analysis_QUERY_PERFORMANCE_20251022_060000.csv`
- ... (one per section)

### Historical Report Sample
```
Historical Analysis Report
Period: Last 30 days
Files Analyzed: 30

🚨 ALERTS (2):
  1. HIGH STORAGE GROWTH: DEV_LANDING grew 67.3% in 30 days
  2. LOW TASK SUCCESS RATE: 89.2% (34 failures)

KEY TRENDS:
STORAGE:
  DEV_LANDING: 145.67 GB (+42.18 GB, 40.7% growth)
  DEV_TRANSFORMATION: 89.23 GB (+12.45 GB, 16.2% growth)

PERFORMANCE:
  avg_queries_per_day: 1247
  avg_query_time: 3.42 seconds
  query_time_change_pct: -12.5% (improved)
```

## Troubleshooting

### Common Issues

**Issue**: "Permission denied" error
**Solution**: Ensure role has access to ACCOUNT_USAGE views. May need ACCOUNTADMIN role.

**Issue**: No results for TASK_EXECUTION section
**Solution**: Tasks may not have executed in last 24 hours. Check task schedule.

**Issue**: Slow script execution
**Solution**:
- Run during off-peak hours
- Increase warehouse size temporarily
- Split sections into separate executions

**Issue**: CSV files too large for Excel
**Solution**:
- Use Python pandas to analyze
- Filter results to specific time periods
- Use database query tools instead

### Performance Optimization

**For faster execution**:
1. Use larger warehouse (MEDIUM instead of X-SMALL)
2. Reduce LIMIT clauses if less detail needed
3. Comment out sections not currently needed
4. Run during low-usage periods

**For reduced storage**:
1. Archive old result files (> 90 days)
2. Use JSON only (smaller than CSV)
3. Compress archived files

## Maintenance

### Regular Tasks

**Weekly**:
- Review alerts from historical analysis
- Archive result files > 30 days old
- Verify scheduled tasks are running

**Monthly**:
- Review storage growth trends
- Update alert thresholds if needed
- Clean up result files > 90 days old

**Quarterly**:
- Review and optimize slow queries
- Update SQL script with new metrics
- Document any schema changes

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-22 | Initial release with 13 analysis sections |

## Support

For issues or questions:
1. Check this README
2. Review script comments
3. Contact Data Engineering Team
4. Review Snowflake ACCOUNT_USAGE documentation

## References

- [Snowflake ACCOUNT_USAGE Views](https://docs.snowflake.com/en/sql-reference/account-usage)
- [Query Performance Tuning](https://docs.snowflake.com/en/user-guide/ui-snowsight-query-profile)
- [Task Monitoring](https://docs.snowflake.com/en/user-guide/tasks-intro)
- [Storage Costs](https://docs.snowflake.com/en/user-guide/cost-understanding-compute)
