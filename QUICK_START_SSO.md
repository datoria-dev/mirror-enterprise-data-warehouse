# Quick Start - SSO Authentication (Okta)

This guide shows how to quickly set up and run the test results export script using SSO authentication.

## ⚡ 3-Step Setup

### 1. Install Python Dependencies

```bash
pip install snowflake-connector-python pandas
```

### 2. Create Configuration File

Copy and edit the config template:

```bash
copy snowflake_config.json.template snowflake_config.json
```

Edit `snowflake_config.json`:

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

**Replace:**
- `your.email@GenericCorp.com` → Your GenericCorp email address
- `abc12345.us-east-1` → Your Snowflake account identifier

**To find your account identifier:**
1. Look at your Snowflake URL: `https://abc12345.us-east-1.snowflakecomputing.com`
2. Extract: `abc12345.us-east-1`

### 3. Run the Script

```bash
python export_test_results_advanced.py
```

**What happens:**
1. Script starts
2. Browser window opens automatically
3. You authenticate with Okta credentials
4. Script connects and exports all test results
5. Files saved to `04_METADATA_SAMPLES/test_results/`

## 🔐 How SSO Works

```
Python Script → Snowflake Connector → Browser Opens → Okta Login
                                                         ↓
                                               [Enter credentials]
                                                         ↓
                                                  Okta approves
                                                         ↓
                                          Token sent to Python script
                                                         ↓
                                          ✅ Connected to Snowflake
```

**Key Benefits:**
- ✅ No passwords in config files
- ✅ Centralized authentication via Okta
- ✅ Automatic token management
- ✅ Same login as Snowflake web UI

## 🎯 Example Session

```bash
C:\...\Snowflake_ITSECKPI_Project_DEV> python export_test_results_advanced.py

================================================================================
🚀 STARTING TEST RESULTS EXPORT
================================================================================

✅ Loaded configuration from: snowflake_config.json
✅ Output directory: 04_METADATA_SAMPLES/test_results
🔌 Connecting to Snowflake via SSO (Okta)...
   ⏳ A browser window will open for authentication...

   [Browser opens → Login with Okta → Browser shows "Success" page]

✅ Connected successfully!

────────────────────────────────────────────────────────────────────────────────
📊 Executing: execution_log
   ✅ Retrieved 5 rows
   💾 Saved CSV: 04_METADATA_SAMPLES/test_results/execution_log.csv
   💾 Saved JSON: 04_METADATA_SAMPLES/test_results/execution_log.json

[... continues for all 10 queries ...]

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

✅ NO DATA QUALITY ISSUES

================================================================================
✅ Export completed!
   • Successful: 10/10
   • Failed: 0/10
   • Output directory: C:\...\04_METADATA_SAMPLES\test_results
================================================================================

🔌 Snowflake connection closed
```

## ⚠️ Common Issues

### Browser doesn't open

**Solution:**
- Check that your default browser is set
- Try manually opening: `https://your-account.snowflakecomputing.com`
- Ensure no firewall is blocking the connection

### Okta login fails

**Solution:**
- Verify your Okta credentials
- Check if MFA is required (it usually is)
- Ensure you have Okta app/authenticator ready
- Try logging into Snowflake web UI first to verify credentials

### "Access denied" error

**Solution:**
- Verify you have access to `DEV_DEVELOPER` role
- Check that `DEV_WH` warehouse exists and you have access
- Confirm `DEV_TRANSFORMATION` database permissions
- Ask your Snowflake admin to grant access if needed

### Connection timeout

**Solution:**
- Check network connectivity
- Connect to VPN if required
- Verify account identifier is correct
- Try increasing timeout in script (if needed)

## 🔄 Running Multiple Times

The script can be run multiple times:
- SSO token is cached for ~4 hours
- After 4 hours, browser will open again for re-authentication
- Results from each run overwrite previous results
- To keep historical results, rename the output folder before re-running

## 📁 Output Files

After successful run, check:

```
04_METADATA_SAMPLES/test_results/
├── execution_log.csv & .json
├── success_criteria.csv & .json
├── services_detected.csv & .json
├── tables_loaded.csv & .json
├── columns_summary.csv & .json
├── columns_detailed.csv & .json
├── statistics_snapshot.csv & .json
├── overall_summary.csv & .json
├── data_quality_checks.csv & .json
├── expected_vs_actual.csv & .json
└── test_results_complete.json  ← All results combined
```

## 🚀 Next Steps

1. ✅ Review test results in `test_results_complete.json`
2. ✅ Check `success_criteria.csv` - all should show "PASS"
3. ✅ If tests pass, proceed to run `CREATE_METADATA_REPOSITORY.sql`
4. ✅ Use exported CSV/JSON files for documentation

## 💡 Pro Tips

- **First time setup:** Takes ~2-3 minutes (includes browser authentication)
- **Subsequent runs:** Takes ~30 seconds (uses cached token)
- **Token expiry:** Browser re-opens automatically when token expires
- **Keep config safe:** Never commit `snowflake_config.json` to Git
- **Multiple accounts:** Create different config files (e.g., `snowflake_config_prod.json`)

---

**Ready to start?**

```bash
python export_test_results_advanced.py
```

Good luck! 🎉
