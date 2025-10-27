# Verification Script Automation - Auto-Export Results

## 📋 Overview

This automation script executes SQL verification scripts and automatically exports all results to CSV/JSON files for analysis. Perfect for scripts with multiple CHECK sections like `VERIFY_PROCEDURE_RECREATION.sql`.

## 🎯 Key Features

- ✅ **Intelligent Parsing** - Automatically detects CHECK sections
- ✅ **Separate Execution** - Runs each CHECK independently
- ✅ **Auto-Export** - Saves all SELECT results to CSV + JSON
- ✅ **Comprehensive Summary** - Creates verification report
- ✅ **Error Handling** - Continues even if a check fails
- ✅ **SSO Authentication** - Uses Okta for secure connection

## 🚀 Quick Start

### Execute Verification Script

```bash
python run_verification_script.py --script 01_SQL_SCRIPTS\VERIFY_PROCEDURE_RECREATION.sql
```

That's it! The script will:
1. Connect to Snowflake via SSO
2. Parse the SQL file into CHECK sections
3. Execute each CHECK separately
4. Save all results to CSV + JSON
5. Generate comprehensive summary report

## 📁 Output Structure

```
04_METADATA_SAMPLES/verification_results/
└── VERIFY_PROCEDURE_RECREATION_20251024_120530/
    ├── verification_summary.json       # Complete verification report
    ├── verification_summary.csv        # Summary in CSV format
    ├── check_01_SETUP_query_1.csv
    ├── check_01_SETUP_query_1.json
    ├── check_02_PROCEDURE_EXISTS_query_1.csv
    ├── check_02_PROCEDURE_EXISTS_query_1.json
    ├── check_03_MOST_RECENT_EXECUTION_query_1.csv
    ├── check_03_MOST_RECENT_EXECUTION_query_1.json
    └── [... all other CHECK results ...]
```

## 🎯 Usage Examples

### Example 1: Verify Procedure Recreation

```bash
python run_verification_script.py --script 01_SQL_SCRIPTS\VERIFY_PROCEDURE_RECREATION.sql
```

**What happens:**
- Executes all 10 CHECKs from the verification script
- Saves each CHECK's results separately
- Creates summary showing pass/fail for each check
- Exports ~20 files (CSV + JSON for each query with results)

### Example 2: Custom Output Directory

```bash
python run_verification_script.py --script 01_SQL_SCRIPTS\VERIFY_PROCEDURE_RECREATION.sql --output procedure_verification_v1
```

Results saved to: `04_METADATA_SAMPLES/verification_results/procedure_verification_v1/`

### Example 3: Verify After Changes

```bash
# Before changes
python run_verification_script.py --script VERIFY_PROCEDURE_RECREATION.sql --output before_changes

# Make changes to stored procedure

# After changes
python run_verification_script.py --script VERIFY_PROCEDURE_RECREATION.sql --output after_changes

# Compare the two verification_summary.json files
```

## 📊 How It Works

### Step 1: Parsing

The script intelligently parses your SQL file:

```sql
-- ============================================================================
-- CHECK 1: Verify Procedure Exists
-- ============================================================================

SHOW PROCEDURES LIKE 'SP_REFRESH_METADATA';
```

Parsed as:
- **CHECK 1**: "Verify Procedure Exists"
- **Query 1**: SHOW PROCEDURES command
- **Type**: SHOW

### Step 2: Execution

Each CHECK is executed independently:
- Runs all queries in the CHECK
- Captures results from SELECT/SHOW commands
- Continues even if a query fails
- Tracks duration and row counts

### Step 3: Export

All query results are automatically saved:
- **CSV**: For Excel analysis
- **JSON**: For programmatic processing
- Named by CHECK number and name
- Includes row count in console output

### Step 4: Summary

Creates comprehensive summary:
```json
{
  "script_name": "VERIFY_PROCEDURE_RECREATION.sql",
  "execution_timestamp": "2025-10-24T12:05:30",
  "total_checks": 10,
  "total_queries": 15,
  "successful_queries": 15,
  "failed_queries": 0,
  "total_duration_seconds": 5.43,
  "checks": [...]
}
```

## 📈 Console Output Example

```bash
PS C:\...\Snowflake_ITSECKPI_Project_DEV> python run_verification_script.py --script 01_SQL_SCRIPTS\VERIFY_PROCEDURE_RECREATION.sql

================================================================================
🔍 VERIFICATION SCRIPT EXECUTION WITH AUTO-EXPORT
================================================================================

✅ Loaded configuration from: snowflake_config.json
✅ Output directory: 04_METADATA_SAMPLES\verification_results\VERIFY_PROCEDURE_RECREATION_20251024_120530
✅ Read SQL file: 01_SQL_SCRIPTS\VERIFY_PROCEDURE_RECREATION.sql
   📄 Parsed 10 CHECK sections with 15 total queries
🔌 Connecting to Snowflake via SSO (Okta)...
   ⏳ A browser window will open for authentication...
✅ Connected successfully!

════════════════════════════════════════════════════════════════════════════════
🔍 CHECK 1: Verify Procedure Exists
════════════════════════════════════════════════════════════════════════════════

   Query 1/1: SHOW
   Preview: SHOW PROCEDURES LIKE 'SP_REFRESH_METADATA';...
   ✅ Retrieved 1 rows in 0.25s
   💾 Saved: check_01_Verify_Procedure_Exists_query_1.csv
   💾 Saved: check_01_Verify_Procedure_Exists_query_1.json

════════════════════════════════════════════════════════════════════════════════
🔍 CHECK 2: Verify Procedure Signature
════════════════════════════════════════════════════════════════════════════════

   Query 1/1: SELECT
   Preview: SELECT name as PROCEDURE_NAME, arguments as ARGUMENTS...
   ✅ Retrieved 1 rows in 0.18s
   💾 Saved: check_02_Verify_Procedure_Signature_query_1.csv
   💾 Saved: check_02_Verify_Procedure_Signature_query_1.json

[... continues for all 10 CHECKs ...]

✅ Created verification summary: verification_summary.json
✅ Created verification summary CSV: verification_summary.csv

================================================================================
📊 VERIFICATION SUMMARY
================================================================================

📄 Script: VERIFY_PROCEDURE_RECREATION.sql
🕐 Timestamp: 2025-10-24T12:05:30
⏱️  Total Duration: 5.43 seconds

📊 Overall Results:
   • Total CHECKs: 10
   • Total Queries: 15
   • ✅ Successful: 15
   • ❌ Failed: 0

📋 CHECK Details:

   ✅ CHECK 1: Verify Procedure Exists
      Queries: 1/1 successful
      Saved results: 1 files
         → check_01_Verify_Procedure_Exists_query_1.csv (1 rows)

   ✅ CHECK 2: Verify Procedure Signature
      Queries: 1/1 successful
      Saved results: 1 files
         → check_02_Verify_Procedure_Signature_query_1.csv (1 rows)

   ✅ CHECK 3: View Most Recent Execution Log
      Queries: 1/1 successful
      Saved results: 1 files
         → check_03_View_Most_Recent_Execution_Log_query_1.csv (1 rows)

   [... all CHECKs listed ...]

================================================================================
✅ All verification checks passed!
   📁 Results saved to: C:\...\04_METADATA_SAMPLES\verification_results\VERIFY_PROCEDURE_RECREATION_20251024_120530
================================================================================

🔌 Snowflake connection closed
```

## 🔍 Analyzing Results

### Method 1: Excel Analysis

1. Open any CSV file in Excel
2. Review the data
3. Apply filters, charts, pivots
4. Compare with previous runs

### Method 2: Python Analysis

```python
import pandas as pd
import json

# Load summary
with open('verification_summary.json') as f:
    summary = json.load(f)

# Check overall status
if summary['failed_queries'] == 0:
    print("✅ All checks passed!")
else:
    print(f"❌ {summary['failed_queries']} checks failed")

# Load specific check results
df = pd.read_csv('check_03_View_Most_Recent_Execution_Log_query_1.csv')
print(f"Latest execution status: {df['STATUS'][0]}")
print(f"Tables processed: {df['TABLES_PROCESSED'][0]}")
```

### Method 3: Automated Validation

```python
import json

with open('verification_summary.json') as f:
    summary = json.load(f)

# Define expected results
expected = {
    'total_checks': 10,
    'successful_queries': 15,
    'failed_queries': 0
}

# Validate
for key, expected_value in expected.items():
    actual_value = summary[key]
    if actual_value == expected_value:
        print(f"✅ {key}: {actual_value} (expected {expected_value})")
    else:
        print(f"❌ {key}: {actual_value} (expected {expected_value})")
```

## 🎯 Benefits

### 1. Automation
- No manual copy/paste from Snowflake UI
- No manual file creation
- No manual result organization
- Saves 10-15 minutes per verification

### 2. Consistency
- Same format every time
- Same file naming convention
- Easy to compare across runs
- Standardized reporting

### 3. Audit Trail
- Complete history of verifications
- Timestamp for each run
- Easy to prove compliance
- Documentation for changes

### 4. Analysis
- CSV for Excel users
- JSON for programmers
- Easy to process programmatically
- Can feed into dashboards

### 5. Error Detection
- Automatically identifies failed checks
- Captures error messages
- Continues execution for full picture
- Clear summary of what passed/failed

## 📝 File Naming Convention

### Pattern
```
check_{CHECK_NUMBER:02d}_{CHECK_NAME}_{query_{QUERY_NUMBER}}.{csv|json}
```

### Examples
- `check_01_SETUP_query_1.csv` - Setup queries
- `check_03_MOST_RECENT_EXECUTION_query_1.csv` - Execution log
- `check_05_METADATA_TABLES_POPULATED_query_1.csv` - Table counts
- `check_10_FINAL_SUMMARY_query_1.csv` - Final verification status

### Benefits
- **Sortable** - Files appear in CHECK order
- **Descriptive** - Know what each file contains
- **Unique** - No file name collisions
- **Searchable** - Easy to find specific checks

## 🔄 Comparison Workflow

### Compare Before/After Changes

```bash
# 1. Run before changes
python run_verification_script.py --script VERIFY_PROCEDURE_RECREATION.sql --output before

# 2. Make changes (e.g., update stored procedure)

# 3. Run after changes
python run_verification_script.py --script VERIFY_PROCEDURE_RECREATION.sql --output after

# 4. Compare summaries
diff 04_METADATA_SAMPLES/verification_results/before/verification_summary.json \
     04_METADATA_SAMPLES/verification_results/after/verification_summary.json

# 5. Compare specific checks
diff 04_METADATA_SAMPLES/verification_results/before/check_05_*.csv \
     04_METADATA_SAMPLES/verification_results/after/check_05_*.csv
```

## 🚨 Troubleshooting

### Issue 1: Script fails to parse CHECK sections

**Solution**: Ensure your SQL script has clear CHECK headers:
```sql
-- ============================================================================
-- CHECK 1: Description Here
-- ============================================================================
```

The parser looks for lines with `-- ===` and `CHECK \d+`

### Issue 2: Some queries don't save results

**Cause**: DDL/DML statements don't return result sets

**This is normal**: Only SELECT and SHOW commands save results. Other statements are logged in the summary but don't create CSV/JSON files.

### Issue 3: Connection timeout

**Solution**:
- Check network/VPN
- Verify Snowflake account is active
- Try increasing timeout in config

## 🎓 Best Practices

### 1. Descriptive CHECK Names

```sql
-- Good
-- CHECK 1: Verify Procedure Exists and Has Correct Signature

-- Bad
-- CHECK 1: Check proc
```

### 2. One Logical Check Per Section

Each CHECK should verify one aspect:
- CHECK 1: Procedure exists
- CHECK 2: Latest execution successful
- CHECK 3: All tables populated
- etc.

### 3. Include Expected Values in Comments

```sql
SELECT COUNT(*) as ROW_COUNT FROM TABLE_REGISTRY;
-- Expected: 180
```

This helps during manual review of results.

### 4. Use Custom Output Names for Important Runs

```bash
# Good - descriptive
--output production_deploy_verification_2025_10_24

# Bad - generic
--output test1
```

### 5. Archive Important Results

```bash
# Archive critical verifications
tar -czf verification_results_archive_2025_10.tar.gz 04_METADATA_SAMPLES/verification_results/
```

## 📊 Integration with CI/CD

### GitHub Actions Example

```yaml
- name: Run Verification Script
  run: |
    python run_verification_script.py \
      --script 01_SQL_SCRIPTS/VERIFY_PROCEDURE_RECREATION.sql \
      --output ci_run_${{ github.run_number }}

- name: Check Verification Results
  run: |
    python -c "
    import json
    with open('04_METADATA_SAMPLES/verification_results/ci_run_${{ github.run_number }}/verification_summary.json') as f:
        summary = json.load(f)
    if summary['failed_queries'] > 0:
        exit(1)
    "

- name: Upload Results
  uses: actions/upload-artifact@v2
  with:
    name: verification-results
    path: 04_METADATA_SAMPLES/verification_results/
```

## 🔗 Related Scripts

- **run_sql_script.py** - Execute complete SQL scripts (for deployment)
- **export_test_results_advanced.py** - Export test results
- **run_verification_script.py** - This script (for verification)

## 📞 Support

### Quick Reference

```bash
# Basic usage
python run_verification_script.py --script path/to/verify.sql

# With custom output
python run_verification_script.py --script path/to/verify.sql --output my_verification

# Check results
cat 04_METADATA_SAMPLES/verification_results/*/verification_summary.json
```

---

**Created**: 2025-10-24
**Purpose**: Automate verification script execution and result export
**Estimated Time Saved**: 10-15 minutes per verification run
