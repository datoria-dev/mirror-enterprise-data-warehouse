# 🚀 Deployment Instructions: Symantec Streamlit App

## ✅ Pre-Deployment Checklist

- ✅ App location: `C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\13_STREAMLIT_COMPLETE\Symantec\streamlit_app.py`
- ✅ Features included:
  - 3 Download buttons (with @st.cache_data pattern)
  - 4 Alert thresholds (colored warnings)
  - Refresh functionality (manual + auto)
- ✅ Syntax verified: No errors
- ✅ Snowflake compatibility: 100%

---

## 📋 Step-by-Step Deployment

### **Step 1: Open SnowSQL or Snowflake Web UI**

Choose one of these options:

**Option A: Using SnowSQL (Command Line)**
```bash
snowsql -a <your_account> -u <your_username>
```

**Option B: Using Snowflake Web UI**
1. Go to Snowflake web interface
2. Open a new Worksheet
3. Select the correct database and schema

---

### **Step 2: Set the Context**

Run these commands first:

```sql
USE DATABASE ITSECKPI_DB;
USE SCHEMA ITSECKPI_SCHEMA;
USE WAREHOUSE COMPUTE_WH;
```

---

### **Step 3: Create Stage (if it doesn't exist)**

```sql
CREATE STAGE IF NOT EXISTS STREAMLIT_APPS_STAGE
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Stage for SECURITY_ANALYTICS Streamlit applications';
```

---

### **Step 4: Upload the Streamlit App File**

**IMPORTANT**: This command must be run from **SnowSQL** (not web UI):

```bash
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Symantec/streamlit_app.py
    @ITSECKPI_DB.ITSECKPI_SCHEMA.STREAMLIT_APPS_STAGE/Symantec/
    OVERWRITE=TRUE
    AUTO_COMPRESS=FALSE;
```

**Expected Output**:
```
streamlit_app.py_c.gz(0.00MB): [##########] 100.00% Done (0.123s, 0.00MB/s).
+------------------+--------------------+-------------+-------------+--------------------+--------------------+----------+---------+
| source           | target             | source_size | target_size | source_compression | target_compression | status   | message |
|------------------+--------------------+-------------+-------------+--------------------+--------------------+----------+---------|
| streamlit_app.py | streamlit_app.py   | 25698       | 25698       | NONE               | NONE               | UPLOADED |         |
+------------------+--------------------+-------------+-------------+--------------------+--------------------+----------+---------+
```

---

### **Step 5: Verify File Upload**

```sql
LIST @STREAMLIT_APPS_STAGE/Symantec/;
```

**Expected Output**: You should see `streamlit_app.py` with size > 0

---

### **Step 6: Create/Update the Streamlit App**

```sql
-- Drop existing app if it exists
DROP STREAMLIT IF EXISTS STREAMLIT_SYMANTEC;

-- Create the new Streamlit app
CREATE STREAMLIT STREAMLIT_SYMANTEC
    ROOT_LOCATION = '@ITSECKPI_DB.ITSECKPI_SCHEMA.STREAMLIT_APPS_STAGE/Symantec'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = 'COMPUTE_WH'
    COMMENT = 'Symantec EDR Dashboard - Endpoint Protection & Response monitoring';
```

**Expected Output**: `STREAMLIT_SYMANTEC successfully created.`

---

### **Step 7: Get the App URL**

```sql
SELECT
    'https://' || CURRENT_ACCOUNT() || '.snowflakecomputing.com/streamlit/' ||
    CURRENT_DATABASE() || '/' || CURRENT_SCHEMA() || '/STREAMLIT_SYMANTEC' AS STREAMLIT_URL;
```

**Copy the URL** and open it in your browser.

---

## 🧪 Testing the Features

Once the app loads, test these features:

### **Tab 1: Coverage Overview (Endpoint Health)**

1. ✅ **Coverage Details Table** - Should show OPCO, TOTAL_ASSETS, PROTECTED_ASSETS, COVERAGE_PCT
2. ✅ **Download Coverage CSV Button** - Click and verify file downloads
3. ✅ **Coverage Alert** - Should show:
   - Red error if < 90%
   - Orange warning if < 95%
   - Green success if ≥ 95%

### **Tab 2: Endpoint Health**

1. ✅ **Health Status Details Table** - Should show endpoint health data
2. ✅ **Download Health Status CSV Button** - Click and verify file downloads

### **Tab 3: High Risk**

1. ✅ **Critical Risk Endpoints Table** - Should show high/critical risk endpoints
2. ✅ **Download Critical Endpoints CSV Button** - Click and verify file downloads
3. ✅ **Critical Endpoints Alert** - Should show:
   - Red error if > 10 critical endpoints
   - Orange warning if > 0 critical endpoints
   - Green success if 0 critical endpoints

### **Sidebar**

1. ✅ **Refresh Now Button** - Click and verify app refreshes
2. ✅ **Auto-refresh Checkbox** - Enable and verify app refreshes every 5 minutes

---

## 🐛 Troubleshooting

### **Problem: File upload fails**

**Solution**:
```sql
-- Check if stage exists
SHOW STAGES LIKE 'STREAMLIT_APPS_STAGE';

-- Check permissions
SHOW GRANTS ON STAGE STREAMLIT_APPS_STAGE;
```

---

### **Problem: Streamlit app doesn't appear**

**Solution**:
```sql
-- Check if app was created
SHOW STREAMLITS LIKE 'STREAMLIT_SYMANTEC';

-- Check warehouse is running
SHOW WAREHOUSES LIKE 'COMPUTE_WH';

-- Try refreshing the app
ALTER STREAMLIT STREAMLIT_SYMANTEC REFRESH;
```

---

### **Problem: Download buttons don't work**

**Possible causes**:
1. Browser cache - Try incognito/private mode
2. Streamlit cache - Use "Clear cache" in app sidebar
3. Network issues - Check browser console (F12) for errors

**Solution**:
```python
# Verify the code has @st.cache_data decorators
# Search for: @st.cache_data
# Should find 3 instances (one for each download button)
```

---

### **Problem: App shows old version**

**Solution**:
```sql
-- Re-upload file with OVERWRITE=TRUE
PUT file://C:/Users/fonat/Documents/MYORG_LOCAL/Snowflake_ITSECKPI_Project_DEV/13_STREAMLIT_COMPLETE/Symantec/streamlit_app.py
    @ITSECKPI_DB.ITSECKPI_SCHEMA.STREAMLIT_APPS_STAGE/Symantec/
    OVERWRITE=TRUE
    AUTO_COMPRESS=FALSE;

-- Force refresh
ALTER STREAMLIT STREAMLIT_SYMANTEC REFRESH;
```

---

## 📊 What to Expect

### **Download Button Behavior**

When you click a download button:

1. **Browser downloads a CSV file** immediately
2. **File naming**:
   - `symantec_coverage.csv`
   - `symantec_health.csv`
   - `symantec_critical.csv`
3. **File content**: CSV format with column headers and data

**Example CSV content**:
```csv
OPCO,TOTAL_ASSETS,PROTECTED_ASSETS,COVERAGE_PCT
GenericCorp Ireland,22571,0,0.0
GenericCorp Americas,15000,14250,95.0
```

---

### **Alert Threshold Behavior**

Alerts appear automatically based on data:

**Coverage Alert Example**:
```
⚠️ Coverage below target: 0.0% (Target: 90%)
```

**Critical Endpoints Alert Example**:
```
⚡ 5 critical risk(s) found - Review needed
```

---

## ✅ Success Indicators

You'll know the deployment worked when:

1. ✅ App loads without errors
2. ✅ All 4 tabs are visible (Coverage, Health, High Risk, Ransomware)
3. ✅ Download buttons appear below tables
4. ✅ Clicking download buttons actually downloads CSV files
5. ✅ Alerts show with colors (red/orange/green)
6. ✅ Refresh Now button works
7. ✅ No console errors in browser (F12)

---

## 📝 Next Steps After Deployment

Once Symantec works:

1. ✅ Deploy remaining 10 apps with download buttons
2. ✅ Deploy 7 apps without download buttons (need manual addition)
3. ✅ Test all apps in Snowflake environment
4. ✅ Document any Snowflake-specific quirks

---

## 📞 Need Help?

If you encounter issues:

1. Check the error message in Snowflake UI
2. Check browser console (F12) for JavaScript errors
3. Verify file size: `LIST @STREAMLIT_APPS_STAGE/Symantec/;`
4. Check warehouse is running: `SHOW WAREHOUSES;`

---

**Good luck with the deployment! 🚀**

The app should work perfectly now with all 3 download buttons functional.
