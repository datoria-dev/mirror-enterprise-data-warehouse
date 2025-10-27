# Export Test Results - Python Scripts

This directory contains Python scripts to automatically export Snowflake test results to JSON and CSV files.

## 📁 Files

- **`export_test_results.py`** - Basic version with hardcoded credentials
- **`export_test_results_advanced.py`** - Advanced version using config file (recommended)
- **`snowflake_config.json.template`** - Template for Snowflake credentials
- **`requirements.txt`** - Python dependencies

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install snowflake-connector-python pandas
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

### Step 2: Configure Snowflake Credentials (SSO with Okta)

**Option A: Using Config File (Recommended)**

1. Copy the template:
   ```bash
   copy snowflake_config.json.template snowflake_config.json
   ```

2. Edit `snowflake_config.json` with your credentials:
   ```json
   {
     "user": "your.email@GenericCorp.com",
     "authenticator": "externalbrowser",
     "account": "abc12345.us-east-1",
     "warehouse": "DEV_WH",
     "database": "DEV_TRANSFORMATION",
     "schema": "METADATA",
     "role": "DEV_DEVELOPER"
   }
   ```

   **Important:**
   - Use `"authenticator": "externalbrowser"` for SSO/Okta authentication
   - NO password needed - authentication happens via browser
   - Use your full GenericCorp email address

3. Run the advanced script:
   ```bash
   python export_test_results_advanced.py
   ```

4. **A browser window will open** - authenticate with your Okta credentials

**Option B: Edit Script Directly**

1. Edit `export_test_results.py`
2. Update the `SNOWFLAKE_CONFIG` dictionary:
   ```python
   SNOWFLAKE_CONFIG = {
       'user': 'your.email@GenericCorp.com',
       'authenticator': 'externalbrowser',  # SSO via Okta
       'account': 'abc12345.us-east-1',
       'warehouse': 'DEV_WH',
       'database': 'DEV_TRANSFORMATION',
       'schema': 'METADATA',
       'role': 'DEV_DEVELOPER'
   }
   ```
3. Run:
   ```bash
   python export_test_results.py
   ```
4. **Browser window will open** for Okta authentication

### Step 3: View Results

Results are saved to: `04_METADATA_SAMPLES/test_results/`

## 📊 Exported Files

The script creates **20+ files** for each test run:

### CSV Files (10)
- `execution_log.csv` - Execution log from stored procedure
- `success_criteria.csv` - Pass/Fail for each test criterion
- `services_detected.csv` - Services detected and table counts
- `tables_loaded.csv` - All tables loaded with metadata
- `columns_summary.csv` - Column count per table
- `columns_detailed.csv` - Detailed column metadata
- `statistics_snapshot.csv` - Statistics snapshot
- `overall_summary.csv` - Overall summary metrics
- `data_quality_checks.csv` - Data quality issues
- `expected_vs_actual.csv` - Expected vs actual comparison

### JSON Files (11)
- Same as CSV files, plus:
- `test_results_complete.json` - Comprehensive summary with all results

## 🔍 What the Script Does

1. **Connects to Snowflake** using provided credentials
2. **Executes 10 test queries** against the METADATA schema
3. **Saves results** to both CSV and JSON formats
4. **Prints summary** to console with pass/fail status
5. **Creates comprehensive JSON** with all results combined

## ✅ Success Criteria Checked

- ✅ Execution completed successfully (STATUS = 'SUCCESS')
- ✅ Tables processed > 0
- ✅ Columns processed > 0
- ✅ Execution duration < 30 seconds
- ✅ No error messages

## 📈 Console Output Example

```
================================================================================
🚀 STARTING TEST RESULTS EXPORT
================================================================================

✅ Loaded configuration from: snowflake_config.json
✅ Output directory: 04_METADATA_SAMPLES/test_results
🔌 Connecting to Snowflake via SSO (Okta)...
   ⏳ A browser window will open for authentication...
✅ Connected successfully!

────────────────────────────────────────────────────────────────────────────────
📊 Executing: execution_log
   ✅ Retrieved 5 rows
   💾 Saved CSV: 04_METADATA_SAMPLES/test_results/execution_log.csv
   💾 Saved JSON: 04_METADATA_SAMPLES/test_results/execution_log.json

────────────────────────────────────────────────────────────────────────────────
📊 Executing: success_criteria
   ✅ Retrieved 5 rows
   💾 Saved CSV: 04_METADATA_SAMPLES/test_results/success_criteria.csv
   💾 Saved JSON: 04_METADATA_SAMPLES/test_results/success_criteria.json

[... continues for all 10 queries ...]

────────────────────────────────────────────────────────────────────────────────
📦 Creating comprehensive summary...
✅ Created comprehensive summary: test_results_complete.json

================================================================================
📈 TEST RESULTS SUMMARY
================================================================================

✅ SUCCESS CRITERIA:
   ✅ Execution completed successfully: SUCCESS
   ✅ Tables processed > 0: 15
   ✅ Columns processed > 0: 234
   ✅ Execution duration < 30 seconds: 12 sec
   ✅ No error message: (none)

📊 OVERALL STATISTICS:
   • Total Services Detected: 6 services
   • Total Tables Loaded: 15 tables
   • Total Columns Loaded: 234 columns
   • Total Statistics Created: 15 snapshots
   • Execution Duration: 12 seconds
   • Total Rows in All Tables: 45678 rows
   • Execution Status: SUCCESS

✅ NO DATA QUALITY ISSUES

================================================================================

================================================================================
✅ Export completed!
   • Successful: 10/10
   • Failed: 0/10
   • Output directory: C:\Users\...\04_METADATA_SAMPLES\test_results
================================================================================

🔌 Snowflake connection closed
```

## 🔒 Security Notes

- **DO NOT commit** `snowflake_config.json` to Git
- The `.gitignore` file already excludes `snowflake_config.json`
- **SSO (Okta) authentication** is used - no passwords in config files
- Browser-based authentication via `externalbrowser` authenticator
- Session tokens are managed securely by Snowflake connector
- For production deployments, consider using key-pair authentication or service accounts

## 🛠️ Troubleshooting

### Error: Module not found

```bash
pip install snowflake-connector-python pandas
```

### Error: Config file not found

```
❌ Config file not found: snowflake_config.json
📝 Please copy snowflake_config.json.template to snowflake_config.json
```

**Solution:** Copy the template and edit with your credentials

### Error: Connection failed

**Common SSO/Okta Issues:**
- Ensure `"authenticator": "externalbrowser"` is in your config
- Allow pop-ups in your browser for Snowflake authentication
- Verify your Okta credentials are valid
- Check network connectivity (VPN if required)
- Ensure you have access to the specified role and warehouse
- Try closing all browser windows and running the script again

**Account Identifier Issues:**
- Use format: `account_locator.region` (e.g., `abc12345.us-east-1`)
- Check your Snowflake account URL for the correct identifier
- Do NOT include `https://` or `.snowflakecomputing.com`

### Error: Query failed

- Ensure you ran `TEST_STORED_PROCEDURE.sql` first
- Verify the METADATA schema exists
- Check that tables (PROCEDURE_EXECUTION_LOG, TABLE_REGISTRY, etc.) exist

## 📝 Next Steps After Export

1. ✅ Review the CSV/JSON files in `04_METADATA_SAMPLES/test_results/`
2. ✅ Check `success_criteria.csv` for any failures
3. ✅ If all tests pass, run `CREATE_METADATA_REPOSITORY.sql`
4. ✅ Use the exported files for documentation and analysis

## 🔄 Running Regularly

You can run this script:
- After each test execution
- Daily to track metadata changes
- As part of a CI/CD pipeline
- Before/after major schema changes

## 📧 Support

For issues or questions:
- Check the Snowflake connection parameters
- Review error messages in console output
- Verify SQL queries in the script match your schema

---

**Created:** 2025-10-24
**Purpose:** Export test results to avoid manual CSV/JSON export from Snowflake UI
