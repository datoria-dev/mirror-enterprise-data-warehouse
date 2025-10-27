# SQL Execution Best Practice - Auto-Export Results

## 📋 Overview

This best practice ensures that **ALL SQL script executions** automatically save their results to CSV/JSON files for:
- ✅ Post-execution analysis
- ✅ Audit trail and compliance
- ✅ Troubleshooting and debugging
- ✅ Documentation and reporting
- ✅ Historical comparison

## 🚀 Quick Start

### Execute Any SQL Script with Auto-Export

```bash
python run_sql_script.py --script 01_SQL_SCRIPTS\CREATE_METADATA_REPOSITORY.sql
```

That's it! The script will:
1. Connect to Snowflake via SSO (Okta)
2. Execute all SQL statements in the file
3. Automatically save all query results to CSV + JSON
4. Generate execution summary with timing and status
5. Store everything in organized folders

## 📁 Output Structure

```
04_METADATA_SAMPLES/sql_execution_results/
└── CREATE_METADATA_REPOSITORY_20251024_120530/
    ├── execution_summary.json          # Complete execution report
    ├── execution_summary.csv           # Summary in CSV format
    ├── stmt_001_select_20251024_120531.csv
    ├── stmt_001_select_20251024_120531.json
    ├── stmt_015_call_20251024_120545.csv
    ├── stmt_015_call_20251024_120545.json
    └── [... all other results ...]
```

## 🎯 Usage Examples

### Example 1: Execute CREATE_METADATA_REPOSITORY.sql

```bash
python run_sql_script.py --script 01_SQL_SCRIPTS\CREATE_METADATA_REPOSITORY.sql
```

**Output:**
- All CREATE TABLE statements executed
- All SELECT query results saved to CSV/JSON
- Stored procedure execution results saved
- View query results saved
- Complete execution log

### Example 2: Execute with Custom Output Directory

```bash
python run_sql_script.py --script 01_SQL_SCRIPTS\VERIFY_METADATA_REPOSITORY.sql --output verification_results
```

Results saved to: `04_METADATA_SAMPLES/sql_execution_results/verification_results/`

### Example 3: Execute Test Scripts

```bash
python run_sql_script.py --script 01_SQL_SCRIPTS\TEST_STORED_PROCEDURE.sql --output test_run_1
```

### Example 4: Execute Analysis Queries

```bash
python run_sql_script.py --script 01_SQL_SCRIPTS\ANALYZE_DATA_QUALITY.sql --output quality_check
```

## 📊 What Gets Saved

### Automatically Saved Results

The script automatically saves results for:
- ✅ **SELECT** statements - Full result sets
- ✅ **CALL** stored procedures - Returned data
- ✅ **SHOW** commands - Metadata listings
- ✅ **DESCRIBE** commands - Schema information

### Execution Metadata

For ALL statements (including DDL/DML):
- ✅ Statement type (CREATE, INSERT, UPDATE, etc.)
- ✅ Execution duration
- ✅ Success/Failure status
- ✅ Row counts (where applicable)
- ✅ Error messages (if failed)

## 🔍 Console Output Example

```bash
PS C:\...\Snowflake_ITSECKPI_Project_DEV> python run_sql_script.py --script 01_SQL_SCRIPTS\CREATE_METADATA_REPOSITORY.sql

================================================================================
🚀 SQL SCRIPT EXECUTION WITH AUTO-EXPORT
================================================================================

✅ Loaded configuration from: snowflake_config.json
✅ Output directory: 04_METADATA_SAMPLES\sql_execution_results\CREATE_METADATA_REPOSITORY_20251024_120530
✅ Read SQL file: 01_SQL_SCRIPTS\CREATE_METADATA_REPOSITORY.sql
   📄 Parsed 45 SQL statements
🔌 Connecting to Snowflake via SSO (Okta)...
   ⏳ A browser window will open for authentication...
✅ Connected successfully!

────────────────────────────────────────────────────────────────────────────────
📊 Statement 1: USE
   Preview: USE ROLE DEV_DEVELOPER...
   ✅ Executed successfully in 0.15s

────────────────────────────────────────────────────────────────────────────────
📊 Statement 2: USE
   Preview: USE WAREHOUSE DEV_WH...
   ✅ Executed successfully in 0.12s

────────────────────────────────────────────────────────────────────────────────
📊 Statement 3: CREATE
   Preview: CREATE SCHEMA IF NOT EXISTS DEV_TRANSFORMATION.METADATA...
   ✅ Executed successfully in 0.45s

[... continues for all statements ...]

────────────────────────────────────────────────────────────────────────────────
📊 Statement 43: SELECT
   Preview: SELECT * FROM VW_SERVICE_SUMMARY ORDER BY SERVICE_NAME...
   ✅ Retrieved 20 rows in 0.32s
   💾 Saved CSV: stmt_043_select_20251024_120615.csv
   💾 Saved JSON: stmt_043_select_20251024_120615.json

────────────────────────────────────────────────────────────────────────────────
📊 Statement 44: SELECT
   Preview: SELECT * FROM VW_TABLE_CATALOG ORDER BY SERVICE_NAME, TABLE_NAME...
   ✅ Retrieved 180 rows in 0.28s
   💾 Saved CSV: stmt_044_select_20251024_120616.csv
   💾 Saved JSON: stmt_044_select_20251024_120616.json

✅ Created execution summary: execution_summary.json
✅ Created execution summary CSV: execution_summary.csv

================================================================================
📈 EXECUTION SUMMARY
================================================================================

📄 Script: CREATE_METADATA_REPOSITORY.sql
🕐 Timestamp: 2025-10-24T12:06:20
⏱️  Total Duration: 45.67 seconds

📊 Statement Summary:
   • Total Statements: 45
   • ✅ Successful: 45
   • ❌ Failed: 0

💾 STATEMENTS WITH SAVED RESULTS (8):
   Statement 43: 20 rows
      CSV: stmt_043_select_20251024_120615.csv
      JSON: stmt_043_select_20251024_120615.json
   Statement 44: 180 rows
      CSV: stmt_044_select_20251024_120616.csv
      JSON: stmt_044_select_20251024_120616.json
   [... etc ...]

================================================================================
✅ All statements executed successfully!
   📁 Results saved to: C:\...\04_METADATA_SAMPLES\sql_execution_results\CREATE_METADATA_REPOSITORY_20251024_120530
================================================================================

🔌 Snowflake connection closed
```

## 📝 Execution Summary Files

### execution_summary.json

Complete execution report with all details:

```json
{
  "script_name": "CREATE_METADATA_REPOSITORY.sql",
  "execution_timestamp": "2025-10-24T12:06:20",
  "total_statements": 45,
  "successful_statements": 45,
  "failed_statements": 0,
  "total_duration_seconds": 45.67,
  "statements": [
    {
      "statement_num": 1,
      "type": "USE",
      "status": "SUCCESS",
      "duration": 0.15,
      "rows": null,
      "preview": "USE ROLE DEV_DEVELOPER"
    },
    {
      "statement_num": 43,
      "type": "SELECT",
      "status": "SUCCESS",
      "duration": 0.32,
      "rows": 20,
      "csv_file": "stmt_043_select_20251024_120615.csv",
      "json_file": "stmt_043_select_20251024_120615.json",
      "preview": "SELECT * FROM VW_SERVICE_SUMMARY ORDER BY SERVICE_NAME"
    }
  ]
}
```

### execution_summary.csv

Quick reference in spreadsheet format:

| statement_num | type | status | duration | rows | csv_file | preview |
|--------------|------|--------|----------|------|----------|---------|
| 1 | USE | SUCCESS | 0.15 | | | USE ROLE DEV_DEVELOPER |
| 43 | SELECT | SUCCESS | 0.32 | 20 | stmt_043_select... | SELECT * FROM VW_SERVICE_SUMMARY |

## 🎯 Benefits

### 1. Audit Trail
- Every execution is logged with timestamp
- All results preserved for compliance
- Easy to trace what was executed and when

### 2. Troubleshooting
- Failed statements clearly identified
- Error messages captured
- Easy to re-run specific statements

### 3. Analysis & Reporting
- Results available in both CSV (Excel) and JSON (programmatic)
- Historical comparison across runs
- Data-driven decision making

### 4. Documentation
- Automatic evidence of script execution
- Results can be shared with stakeholders
- No manual export needed

### 5. Reproducibility
- Complete record of what was executed
- Results can be verified later
- Easy to compare before/after changes

## 🔧 Advanced Features

### Feature 1: Statement Classification

The script automatically identifies statement types:
- **DDL**: CREATE, DROP, ALTER (schema changes)
- **DML**: INSERT, UPDATE, DELETE (data changes)
- **DQL**: SELECT (queries)
- **DCL**: GRANT, REVOKE (permissions)
- **TCL**: COMMIT, ROLLBACK (transactions)
- **Procedures**: CALL (stored procedure execution)

### Feature 2: Smart Result Export

Only statements that return results get saved:
- SELECT queries → CSV + JSON
- CALL procedures → CSV + JSON (if returns data)
- SHOW commands → CSV + JSON
- DDL/DML → Execution metadata only (no empty files)

### Feature 3: Error Handling

- Script continues even if a statement fails (configurable)
- Failed statements clearly marked in summary
- Error messages captured for debugging

### Feature 4: Performance Tracking

- Execution duration for each statement
- Total script execution time
- Identify slow queries automatically

## 🚨 Common Issues

### Issue 1: Large Result Sets

**Problem**: Query returns millions of rows, creating huge files

**Solution**: Add LIMIT clause to queries in your SQL script:
```sql
SELECT * FROM LARGE_TABLE LIMIT 10000;
```

Or modify the script to add automatic row limits.

### Issue 2: Long-Running Scripts

**Problem**: Script takes hours to complete

**Solution**: Break into smaller scripts:
```bash
python run_sql_script.py --script part1_create_tables.sql
python run_sql_script.py --script part2_load_data.sql
python run_sql_script.py --script part3_verify.sql
```

### Issue 3: Permission Errors

**Problem**: Cannot create output directory

**Solution**: Ensure you have write permissions to the output directory, or specify a custom location:
```bash
python run_sql_script.py --script my_script.sql --output C:\temp\my_results
```

## 📚 Best Practices

### 1. Always Use This Script for Production Deployments

```bash
# Bad: Running directly in Snowflake UI
# No audit trail, no saved results

# Good: Using Python script
python run_sql_script.py --script PRODUCTION_DEPLOY.sql --output prod_deploy_$(date +%Y%m%d)
```

### 2. Name Output Directories Descriptively

```bash
# Bad
python run_sql_script.py --script test.sql --output test1

# Good
python run_sql_script.py --script test.sql --output metadata_test_2025_10_24_pre_prod
```

### 3. Archive Results for Important Executions

```bash
# After successful execution, archive the results
tar -czf results_archive_2025_10_24.tar.gz 04_METADATA_SAMPLES/sql_execution_results/CREATE_METADATA_REPOSITORY_20251024_120530/
```

### 4. Review Execution Summary Before Proceeding

Always check `execution_summary.json` for:
- Any failed statements
- Unexpected row counts
- Execution times (performance issues)

### 5. Store Summaries in Version Control

The execution summaries are small - commit them to Git:
```bash
git add 04_METADATA_SAMPLES/sql_execution_results/*/execution_summary.json
git commit -m "Add execution summary for metadata repository creation"
```

## 🔄 Integration with CI/CD

Example GitHub Actions workflow:

```yaml
- name: Execute SQL Script with Auto-Export
  run: |
    python run_sql_script.py --script 01_SQL_SCRIPTS/CREATE_METADATA_REPOSITORY.sql --output ci_run_${{ github.run_number }}

- name: Upload Results
  uses: actions/upload-artifact@v2
  with:
    name: sql-execution-results
    path: 04_METADATA_SAMPLES/sql_execution_results/
```

## 📖 Related Scripts

- **run_sql_script.py** - Main execution script (this one)
- **export_test_results_advanced.py** - Export test results for analysis
- **snowflake_config.json** - Snowflake connection configuration

## 🤝 Contributing

When adding new SQL scripts to the project:
1. Always test with `run_sql_script.py` first
2. Review the execution summary
3. Commit both the SQL script and execution summary
4. Document any specific requirements in the SQL file header

---

**Created**: 2025-10-24
**Purpose**: Establish best practice for SQL script execution with automatic result export
**Maintainer**: GenericCorp Data Engineering Team
