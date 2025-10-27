# ✅ Stored Procedure Recreation - Complete Checklist

## 📋 Pre-Execution Checklist

Before you start, ensure you have:

- [ ] Snowflake account credentials ready
- [ ] Okta MFA device available
- [ ] Browser allows pop-ups for Snowflake
- [ ] Network/VPN connected (if required)
- [ ] File Explorer access to project directory
- [ ] Text editor or Snowflake UI ready

**Estimated Time**: 10-15 minutes

---

## 🔄 Execution Steps

### Phase 1: Preparation (2 minutes)

- [ ] **Step 1.1**: Open Snowflake in browser
  - URL: `https://GenericCorp-CRH_EDW.snowflakecomputing.com`
  - Login with: `fuad.onate@CompanyX.com`
  - Authenticate via Okta MFA

- [ ] **Step 1.2**: Create new worksheet
  - Click **Worksheets** → **+ Worksheet**
  - Name it: `Recreate_SP_REFRESH_METADATA`

- [ ] **Step 1.3**: Set context
  ```sql
  USE ROLE DEV_DEVELOPER;
  USE WAREHOUSE DEV_WH;
  USE DATABASE DEV_TRANSFORMATION;
  USE SCHEMA METADATA;
  ```
  - Select all 4 lines → Click ▶️ Run
  - Verify: No error messages

### Phase 2: Procedure Recreation (5 minutes)

- [ ] **Step 2.1**: Open CREATE_STORED_PROCEDURE_ONLY.sql
  - Location: `C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\01_SQL_SCRIPTS\CREATE_STORED_PROCEDURE_ONLY.sql`
  - Open in text editor or VS Code

- [ ] **Step 2.2**: Copy script content
  - Select all (Ctrl+A)
  - Copy (Ctrl+C)

- [ ] **Step 2.3**: Paste into Snowflake worksheet
  - Go back to Snowflake worksheet
  - Paste below the USE statements (Ctrl+V)

- [ ] **Step 2.4**: Execute the script
  - Select all (Ctrl+A) or just the pasted content
  - Click ▶️ Run
  - Wait for execution to complete (~10-30 seconds)

- [ ] **Step 2.5**: Verify execution
  - Check for "Statement executed successfully"
  - No error messages in red

### Phase 3: Verification (5 minutes)

- [ ] **Step 3.1**: Open VERIFY_PROCEDURE_RECREATION.sql
  - Location: `C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\01_SQL_SCRIPTS\VERIFY_PROCEDURE_RECREATION.sql`
  - Open in new Snowflake worksheet

- [ ] **Step 3.2**: Execute verification script
  - Copy entire content
  - Paste into new worksheet
  - Click ▶️ Run All

- [ ] **Step 3.3**: Review CHECK 1: Procedure Exists
  - Expected: 1 row showing `SP_REFRESH_METADATA`
  - Result: ✅ PASS / ❌ FAIL

- [ ] **Step 3.4**: Review CHECK 2: Procedure Signature
  - Expected: RETURN_TYPE = VARCHAR, LANGUAGE = SQL
  - Result: ✅ PASS / ❌ FAIL

- [ ] **Step 3.5**: Review CHECK 3: Most Recent Execution
  - Expected: STATUS = 'SUCCESS'
  - Expected: TABLES_PROCESSED = 180
  - Expected: COLUMNS_PROCESSED = 2206
  - Result: ✅ PASS / ❌ FAIL

- [ ] **Step 3.6**: Review CHECK 4: Execution History
  - Expected: At least 1-2 executions shown
  - Latest should be most recent timestamp
  - Result: ✅ PASS / ❌ FAIL

- [ ] **Step 3.7**: Review CHECK 5: Metadata Tables Populated
  - Expected: All 4 tables show STATUS = '✅ PASS'
  - TABLE_REGISTRY: 180 rows
  - COLUMN_METADATA: 2206 rows
  - TABLE_STATISTICS: ≥180 rows
  - SERVICE_CATALOG: 21 rows
  - Result: ✅ PASS / ❌ FAIL

- [ ] **Step 3.8**: Review CHECK 6: Execution Details JSON
  - Expected: All JSON fields populated
  - tables_processed: 180
  - columns_processed: 2206
  - Result: ✅ PASS / ❌ FAIL

- [ ] **Step 3.9**: Review CHECK 7: Services Detected
  - Expected: 20 services listed
  - Various table counts per service
  - Result: ✅ PASS / ❌ FAIL

- [ ] **Step 3.10**: Review CHECK 8: Views Working
  - Expected: SERVICE_COUNT = 21
  - Expected: TABLE_COUNT = 180
  - Expected: COLUMN_COUNT = 2206
  - Result: ✅ PASS / ❌ FAIL

- [ ] **Step 3.11**: Review CHECK 9: Performance Metrics
  - Expected: Average duration 9-15 seconds
  - Expected: Tables/sec 12-20
  - Expected: Columns/sec 150-250
  - Result: ✅ PASS / ❌ FAIL

- [ ] **Step 3.12**: Review CHECK 10: Final Summary
  - Expected: '✅ ALL CHECKS PASSED - PROCEDURE IS WORKING CORRECTLY'
  - Result: ✅ PASS / ❌ FAIL

### Phase 4: Export Results (3 minutes)

- [ ] **Step 4.1**: Export execution log
  - In CHECK 3 results panel
  - Right-click → Download as CSV
  - Save as: `procedure_recreation_execution_log.csv`
  - Location: `C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\04_METADATA_SAMPLES\sql_execution_results\`

- [ ] **Step 4.2**: Export final summary
  - In CHECK 10 results panel
  - Right-click → Download as CSV
  - Save as: `procedure_recreation_final_summary.csv`
  - Same location as above

- [ ] **Step 4.3**: Take screenshots (optional but recommended)
  - Screenshot of CHECK 5 (all PASS)
  - Screenshot of CHECK 10 (final summary)
  - Save to same location

---

## ✅ Success Criteria

All of the following must be TRUE:

### Critical Criteria (Must Pass):
- [x] Procedure exists in SHOW PROCEDURES
- [x] CHECK 3: STATUS = 'SUCCESS'
- [x] CHECK 5: All 4 tables show '✅ PASS'
- [x] CHECK 10: Shows '✅ ALL CHECKS PASSED'
- [x] No error messages during execution

### Important Criteria (Should Pass):
- [x] TABLES_PROCESSED = 180
- [x] COLUMNS_PROCESSED = 2206
- [x] Execution duration < 30 seconds
- [x] 20 services detected
- [x] All views return expected counts

### Optional Criteria (Nice to Have):
- [x] Multiple execution records in history
- [x] Performance metrics within optimal ranges
- [x] JSON details fully populated

---

## 🚨 Troubleshooting Guide

### Issue 1: "Procedure does not exist" in CHECK 1

**Cause**: CREATE PROCEDURE failed

**Solution**:
1. Re-run CREATE_STORED_PROCEDURE_ONLY.sql
2. Check for error messages in red
3. Verify context (USE statements) were executed
4. Try running just the CREATE PROCEDURE statement alone

### Issue 2: CHECK 3 shows STATUS = 'FAILED'

**Cause**: Procedure executed but encountered error

**Solution**:
1. Look at ERROR_MESSAGE column in CHECK 3
2. Check table permissions (DEV_LANDING, DEV_TRANSFORMATION)
3. Verify SECURITY_ANALYTICS schema exists in both databases
4. Re-run procedure: `CALL SP_REFRESH_METADATA();`

### Issue 3: CHECK 5 shows wrong row counts

**Cause**: Data not loaded correctly

**Solution**:
1. Check if tables exist: `SHOW TABLES IN METADATA;`
2. Manually run procedure: `CALL SP_REFRESH_METADATA();`
3. Wait 10-15 seconds and re-run CHECK 5
4. If still wrong, check INFORMATION_SCHEMA access

### Issue 4: Execution takes > 30 seconds

**Cause**: Warehouse size or data volume

**Solution**:
1. This is OK, just slower performance
2. Consider using larger warehouse for refresh
3. Check warehouse status: `SHOW WAREHOUSES LIKE 'DEV_WH';`
4. If suspended, resume it: `ALTER WAREHOUSE DEV_WH RESUME;`

### Issue 5: CHECK 10 shows "SOME CHECKS FAILED"

**Cause**: One or more checks didn't pass

**Solution**:
1. Review each CHECK result panel
2. Identify which specific check failed
3. Follow troubleshooting for that specific check
4. Re-run verification after fixing

---

## 📊 Expected Results Summary

### After Successful Recreation:

**Procedure Details:**
- Name: `SP_REFRESH_METADATA`
- Returns: `VARCHAR`
- Language: `SQL`
- Status: Created/Replaced successfully

**Execution Results:**
- Tables Processed: 180
- Columns Processed: 2,206
- Statistics Created: 180
- Duration: 9-15 seconds (typical)
- Status: SUCCESS

**Metadata Repository:**
- TABLE_REGISTRY: 180 tables across 20 services
- COLUMN_METADATA: 2,206 columns
- TABLE_STATISTICS: 180 snapshots
- SERVICE_CATALOG: 21 services
- All views working correctly

---

## 🎯 Next Steps After Success

Once all checks pass:

1. **Document the recreation**
   - [ ] Note the execution timestamp
   - [ ] Save all exported CSV files
   - [ ] Keep screenshots for reference

2. **Activate Daily Refresh Task**
   - [ ] Run: `ALTER TASK TASK_DAILY_METADATA_REFRESH RESUME;`
   - [ ] Verify: `SHOW TASKS LIKE 'TASK_DAILY_METADATA_REFRESH';`
   - [ ] State should be: `started`

3. **Export Metadata for Streamlit Apps**
   - [ ] Run: `@01_SQL_SCRIPTS\EXPORT_METADATA_RESULTS.sql`
   - [ ] Verify exports created in METADATA_EXPORTS schema

4. **Update Streamlit Applications**
   - [ ] Use VW_COLUMN_CATALOG for correct column names
   - [ ] Reference TABLE_REGISTRY for table metadata
   - [ ] Leverage SERVICE_CATALOG for service information

5. **Set Up Monitoring**
   - [ ] Create dashboard for PROCEDURE_EXECUTION_LOG
   - [ ] Set up alerts for failed executions
   - [ ] Schedule weekly reviews of metadata quality

---

## 📝 Completion Checklist

Mark each section as complete:

- [ ] Phase 1: Preparation - COMPLETE
- [ ] Phase 2: Procedure Recreation - COMPLETE
- [ ] Phase 3: Verification - COMPLETE
- [ ] Phase 4: Export Results - COMPLETE
- [ ] All Success Criteria Met - YES
- [ ] Troubleshooting (if needed) - RESOLVED
- [ ] Next Steps Identified - DOCUMENTED

**Completion Date**: _________________

**Completed By**: Fuad Oñate

**Final Status**: ⬜ SUCCESS ⬜ PARTIAL SUCCESS ⬜ FAILED

**Notes**:
```
[Add any notes, issues encountered, or observations here]
```

---

## 📧 Support

If you encounter issues not covered in this checklist:

1. Review the detailed analysis report:
   `04_METADATA_SAMPLES\sql_execution_results\CREATE_METADATA_REPOSITORY_20251024_023259\FAILURE_ANALYSIS_REPORT.md`

2. Check execution logs:
   ```sql
   SELECT * FROM PROCEDURE_EXECUTION_LOG ORDER BY EXECUTION_START DESC LIMIT 5;
   ```

3. Review error messages:
   ```sql
   SELECT LOG_ID, ERROR_MESSAGE, EXECUTION_DETAILS
   FROM PROCEDURE_EXECUTION_LOG
   WHERE STATUS = 'FAILED';
   ```

---

**Checklist Version**: 1.0
**Last Updated**: 2025-10-24
**Estimated Completion Time**: 10-15 minutes
