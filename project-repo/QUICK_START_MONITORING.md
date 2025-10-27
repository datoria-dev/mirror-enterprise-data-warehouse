# Quick Start: Daily Monitoring System

## Overview
Automated system for daily analysis of Snowflake data model and query performance.

## Prerequisites
- VS Code with integrated terminal
- Python 3.8+ installed
- Snowflake credentials configured

## 1. First Time Setup (5 minutes)

### Install Dependencies
Open VS Code terminal (Ctrl+`) and run:
```bash
pip install snowflake-connector-python pandas python-dotenv
```

### Configure Credentials
Create/update `03_CONFIG/.env` file:
```env
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_WAREHOUSE=DEV_WH
SNOWFLAKE_DATABASE=ITSECKPI_DEV
SNOWFLAKE_SCHEMA=DEV_TRANSFORMATION
SNOWFLAKE_ROLE=ACCOUNTADMIN
```

**Note**: ACCOUNTADMIN role required for ACCOUNT_USAGE views access.

## 2. Daily Execution (2 minutes)

### Run Analysis
In VS Code terminal:
```bash
python 02_PYTHON_SCRIPTS/run_daily_analysis.py
```

**What it does**:
- Executes 13 analysis sections
- Saves results to `06_ANALYSIS_RESULTS/`
- Creates JSON (all data) and CSV (per section) files
- Takes ~30-60 seconds to complete

**Expected Output**:
```
✅ Connected to Snowflake successfully
✅ SQL script loaded
✅ Parsed 13 query sections
  Executing: OBJECT_INVENTORY... ✅ (3 rows)
  Executing: TABLE_SIZE_ANALYSIS... ✅ (142 rows)
  ...
✅ Analysis completed: 13 sections executed
✅ JSON saved: 06_ANALYSIS_RESULTS/daily_analysis_20251022_090000.json
✅ CSV files saved: 13 files
✅ Daily analysis completed successfully!
```

## 3. View Results

### JSON (Complete Data)
```bash
# Open latest JSON in VS Code
code 06_ANALYSIS_RESULTS/daily_analysis_*.json
```

### CSV (Excel-friendly)
Navigate to `06_ANALYSIS_RESULTS/` and open CSV files in Excel or:
```bash
# View in terminal
cat 06_ANALYSIS_RESULTS/daily_analysis_TABLE_SIZE_ANALYSIS_*.csv | head
```

## 4. Historical Trend Analysis

### Weekly Trends
```bash
python 02_PYTHON_SCRIPTS/analyze_historical_results.py --days 7
```

### Monthly Review
```bash
python 02_PYTHON_SCRIPTS/analyze_historical_results.py --days 30
```

**What it shows**:
- Storage growth trends by schema
- Query performance changes
- Slow query patterns
- Task health metrics
- **Automated alerts** for anomalies

**Sample Output**:
```
✅ Loaded 30 result files from last 30 days

STORAGE TREND ANALYSIS
======================
DEV_LANDING:
  Current Size: 145.67 GB
  Growth: 42.18 GB (40.7%)
  Daily Growth: 1.41 GB/day
  Monthly Cost: $3.35

🚨 ALERT: HIGH STORAGE GROWTH: DEV_LANDING grew 40.7% in 30 days

QUERY PERFORMANCE TREND ANALYSIS
=================================
Average Daily Metrics:
  Queries per day: 1247
  Avg query time: 3.42 seconds
  Errors per day: 2.1

✅ Report saved to: 06_ANALYSIS_RESULTS/historical_analysis_report_20251022_090000.txt
```

## 5. Detailed Section Analysis

Analyze specific section in detail:
```bash
# Storage costs
python 02_PYTHON_SCRIPTS/analyze_historical_results.py --section STORAGE_COSTS

# Slow queries
python 02_PYTHON_SCRIPTS/analyze_historical_results.py --section SLOW_QUERIES

# Query performance
python 02_PYTHON_SCRIPTS/analyze_historical_results.py --section QUERY_PERFORMANCE
```

## 6. Available Analysis Sections

| Section | What It Shows |
|---------|--------------|
| `OBJECT_INVENTORY` | Count of tables, views, functions by schema |
| `TABLE_SIZE_ANALYSIS` | Largest tables and growth tracking |
| `QUERY_PERFORMANCE` | Avg execution time by hour and schema |
| `SLOW_QUERIES` | Queries taking > 10 seconds |
| `DATA_QUALITY` | Data freshness and completeness |
| `WAREHOUSE_UTILIZATION` | Compute usage and costs |
| `CONSTRAINT_COVERAGE` | Primary/Foreign key verification |
| `TASK_EXECUTION` | Scheduled task success/failure rates |
| `STORAGE_COSTS` | Storage costs by schema |
| `ERROR_SUMMARY` | Failed queries and error types |
| `MATERIALIZED_VIEW_STATUS` | Materialized view refresh status |
| `USER_ACTIVITY` | Top users by query volume |
| `DAILY_SUMMARY` | High-level dashboard KPIs |

## 7. Scheduled Automation

### Windows (Task Scheduler)
```powershell
# Run daily at 6:00 AM
schtasks /create /tn "Snowflake Daily Analysis" /tr "python C:\path\to\project\02_PYTHON_SCRIPTS\run_daily_analysis.py" /sc daily /st 06:00
```

### Linux/Mac (Cron)
```bash
# Add to crontab (run daily at 6:00 AM)
0 6 * * * cd /path/to/project && python 02_PYTHON_SCRIPTS/run_daily_analysis.py
```

## 8. Troubleshooting

### Error: "Permission denied"
**Solution**: Change role to ACCOUNTADMIN in `.env` file:
```env
SNOWFLAKE_ROLE=ACCOUNTADMIN
```

### Error: "Module not found"
**Solution**: Install dependencies:
```bash
pip install snowflake-connector-python pandas python-dotenv
```

### Slow Execution (>5 minutes)
**Solution**: Increase warehouse size temporarily:
```sql
-- In Snowflake
ALTER WAREHOUSE DEV_WH SET WAREHOUSE_SIZE = 'MEDIUM';
```

### No SLOW_QUERIES results
**Normal**: Means no queries exceeded 10 seconds (good!).

### CSV too large for Excel
**Solution**: Use pandas to analyze:
```python
import pandas as pd
df = pd.read_csv('06_ANALYSIS_RESULTS/daily_analysis_TABLE_SIZE_ANALYSIS_*.csv')
print(df.head(20))
```

## 9. Key Metrics to Watch

| Metric | Threshold | Action |
|--------|-----------|--------|
| Storage Growth | > 5 GB/day | Investigate data ingestion |
| Avg Query Time | > 5 seconds | Review slow queries |
| Error Rate | > 5% | Check error summary |
| Task Success Rate | < 95% | Investigate failed tasks |
| Slow Queries | > 10/day | Optimize queries |

## 10. File Management

### Archive Old Results (Monthly)
```bash
# Move files older than 90 days to archive
mkdir -p 06_ANALYSIS_RESULTS/archive
mv 06_ANALYSIS_RESULTS/*_202501*.* 06_ANALYSIS_RESULTS/archive/
```

### Compress Archives
```bash
# Compress archived files
cd 06_ANALYSIS_RESULTS/archive
tar -czf analysis_2025_Q1.tar.gz *.json *.csv
rm *.json *.csv
```

## 11. Integration with Other Tools

### Power BI
Import CSV files directly:
1. Power BI Desktop > Get Data > CSV
2. Select files from `06_ANALYSIS_RESULTS/`
3. Create time-series visualizations

### Jupyter Notebooks
```python
import pandas as pd
import json

# Load JSON
with open('06_ANALYSIS_RESULTS/daily_analysis_latest.json') as f:
    data = json.load(f)

# Convert section to DataFrame
df = pd.DataFrame(data['results']['TABLE_SIZE_ANALYSIS'])
df.plot(x='TABLE_NAME', y='SIZE_GB', kind='bar')
```

### Excel Pivot Tables
1. Open CSV file in Excel
2. Insert > PivotTable
3. Analyze trends by date/schema

## 12. Next Steps

After running for 7+ days:
1. Review weekly trend reports
2. Set up alerts based on your baseline
3. Optimize identified slow queries
4. Schedule automated execution
5. Share reports with team

## Need Help?

- **Documentation**: `01_SQL_SCRIPTS/06_Monitoring/README.md`
- **SQL Script**: `01_SQL_SCRIPTS/06_Monitoring/DAILY_DATA_MODEL_PERFORMANCE_ANALYSIS.sql`
- **Python Scripts**: `02_PYTHON_SCRIPTS/run_daily_analysis.py` and `analyze_historical_results.py`

## Quick Reference Commands

```bash
# Run daily analysis
python 02_PYTHON_SCRIPTS/run_daily_analysis.py

# Weekly review
python 02_PYTHON_SCRIPTS/analyze_historical_results.py --days 7

# Monthly review with alerts
python 02_PYTHON_SCRIPTS/analyze_historical_results.py --days 30

# Specific section deep dive
python 02_PYTHON_SCRIPTS/analyze_historical_results.py --section STORAGE_COSTS
```

---
**Created**: 2025-10-22
**Version**: 1.0
**For**: VS Code Terminal Execution
