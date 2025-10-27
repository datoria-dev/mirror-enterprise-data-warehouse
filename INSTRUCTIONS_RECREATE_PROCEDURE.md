# Instructions: Re-create SP_REFRESH_METADATA Stored Procedure

## 📋 Overview

This guide will help you re-create the `SP_REFRESH_METADATA` stored procedure using the Snowflake UI to ensure it matches the latest version from `CREATE_METADATA_REPOSITORY.sql`.

## ⚠️ Why Are We Doing This?

The Python script `run_sql_script.py` has a parser limitation with stored procedures that use dollar-quote delimiters (`$$`). The procedure exists from the TEST run, but we want to ensure it's the exact version from `CREATE_METADATA_REPOSITORY.sql`.

## 🚀 Step-by-Step Instructions

### Step 1: Open Snowflake in Browser

1. Navigate to your Snowflake URL
2. Authenticate with Okta SSO using `fuad.onate@CompanyX.com`
3. Wait for browser authentication to complete

### Step 2: Open SQL Worksheet

1. Click on **Worksheets** in the left navigation
2. Click **+ Worksheet** to create a new worksheet
3. Name it: `Recreate SP_REFRESH_METADATA`

### Step 3: Set Context

Copy and paste these commands at the top of your worksheet:

```sql
USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;
USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA METADATA;
```

**Execute these** by selecting all 4 lines and clicking ▶️ Run

### Step 4: Open the SQL Script File

1. Open Windows File Explorer
2. Navigate to: `C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\01_SQL_SCRIPTS\`
3. Open file: `CREATE_STORED_PROCEDURE_ONLY.sql`
4. **Select ALL content** (Ctrl+A)
5. **Copy** (Ctrl+C)

### Step 5: Paste and Execute in Snowflake

1. Go back to your Snowflake worksheet
2. Below the USE statements, **paste** the entire script content (Ctrl+V)
3. **Select ALL** (Ctrl+A) or just select from `CREATE OR REPLACE PROCEDURE` to the end
4. Click **▶️ Run** (or press Ctrl+Enter)

### Step 6: Monitor Execution

You should see several result panels:

1. **CREATE OR REPLACE PROCEDURE** - Should show "Statement executed successfully"
2. **SHOW PROCEDURES** - Should show `SP_REFRESH_METADATA` in the list
3. **CALL SP_REFRESH_METADATA()** - Should execute and return success message
4. **SELECT FROM PROCEDURE_EXECUTION_LOG** - Should show the latest execution

### Step 7: Verify Success

Expected output from the CALL statement:

```
SP_REFRESH_METADATA
-------------------
Metadata refresh completed successfully: 180 tables, 2206 columns, 180 statistics processed in X seconds
```

Expected output from the final SELECT:

| LOG_ID | PROCEDURE_NAME | EXECUTION_START | EXECUTION_END | DURATION | STATUS | TABLES | COLUMNS | ROWS |
|--------|----------------|-----------------|---------------|----------|--------|--------|---------|------|
| 2 or 3 | SP_REFRESH_METADATA | 2025-10-24 ... | 2025-10-24 ... | 9-12 | SUCCESS | 180 | 2206 | 180 |

### Step 8: Save Results

1. In the results panel for the final SELECT query
2. Right-click on the results grid
3. Select **Download as CSV**
4. Save as: `C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\04_METADATA_SAMPLES\sql_execution_results\procedure_recreation_verification.csv`

## ✅ Success Criteria

The procedure was successfully re-created if:

- ✅ No error messages during CREATE PROCEDURE
- ✅ SHOW PROCEDURES lists `SP_REFRESH_METADATA`
- ✅ CALL executes without errors
- ✅ CALL returns message with "completed successfully"
- ✅ Final SELECT shows STATUS = 'SUCCESS'
- ✅ TABLES_PROCESSED = 180
- ✅ COLUMNS_PROCESSED = 2206

## 🔍 Troubleshooting

### Error: "Procedure already exists"

This is OK! The `CREATE OR REPLACE` will overwrite it. This is what we want.

### Error: "Table PROCEDURE_EXECUTION_LOG does not exist"

Run this first:
```sql
USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA METADATA;
```

Then try again.

### Error: "Role DEV_DEVELOPER does not exist"

Check your role assignment with your Snowflake admin.

### Execution takes longer than expected

The procedure scans 180 tables and 2,206 columns. It should complete in 9-15 seconds, but could take up to 30 seconds depending on warehouse size.

## 📊 What to Share Back

After successful execution, please share:

1. **Screenshot** of the CALL result (showing success message)
2. **CSV file** saved from Step 8
3. Any **error messages** if something failed

## 🎯 Next Steps After Success

Once the procedure is successfully re-created:

1. ✅ Verify metadata repository is complete
2. ✅ Activate the daily refresh task
3. ✅ Export metadata for Streamlit apps
4. ✅ Begin using metadata repository in applications

## 📝 Alternative Method: Using SnowSQL CLI

If you prefer command-line execution:

```bash
# Connect to Snowflake
snowsql -a GenericCorp-CRH_EDW -u fuad.onate@CompanyX.com --authenticator externalbrowser

# Execute the script
!source C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\01_SQL_SCRIPTS\CREATE_STORED_PROCEDURE_ONLY.sql
```

---

**Created**: 2025-10-24
**Purpose**: Re-create stored procedure to ensure sync with CREATE_METADATA_REPOSITORY.sql
**Estimated Time**: 5-10 minutes
