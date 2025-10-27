# Export Guide - Metadata and Samples

## Overview
This guide explains how to export CSV files from Snowflake using VS Code Snowflake extension.

## Directory Structure
```
04_METADATA_SAMPLES/
├── metadata/     <- Metadata files (column structures)
├── samples/      <- Sample data files (100 rows each)
└── README_EXPORT_GUIDE.md
```

## Step-by-Step Export Process

### Prerequisites
✅ Script executed: `EXECUTE_METADATA_EXTRACTION_FINAL.sql`
✅ Views created in: `DEV_TRANSFORMATION.SAMPLES` schema
✅ Connected to Snowflake via VS Code extension

---

## PART 1: Export Metadata Files (7 files)

### 1. Complete Metadata (ALL SERVICES)

**Query:**
```sql
USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;

SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
ORDER BY SERVICE_NAME, DATA_LAYER, TABLE_NAME, ORDINAL_POSITION;
```

**Steps:**
1. Open `01_SQL_SCRIPTS/EXPORT_METADATA_AND_SAMPLES.sql`
2. Select the query above (lines 18-22)
3. Press F5 or click "Execute Query"
4. Wait for results to load
5. Right-click on results grid
6. Select "Export Results" or "Download as CSV"
7. Save as: `04_METADATA_SAMPLES/metadata/metadata_all_services.csv`

---

### 2. Service Summary

**Query:**
```sql
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SERVICE_SUMMARY;
```

**Save as:** `04_METADATA_SAMPLES/metadata/metadata_service_summary.csv`

---

### 3. SentinelOne Metadata

**Query:**
```sql
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    COMMENT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME = 'SentinelOne'
ORDER BY TABLE_NAME, ORDINAL_POSITION;
```

**Save as:** `04_METADATA_SAMPLES/metadata/metadata_sentinelone.csv`

---

### 4. CybelAngel Metadata

**Query:**
```sql
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    COMMENT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME = 'CybelAngel'
ORDER BY TABLE_NAME, ORDINAL_POSITION;
```

**Save as:** `04_METADATA_SAMPLES/metadata/metadata_cybelangel.csv`

---

### 5. Proofpoint Metadata

**Query:**
```sql
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    COMMENT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME = 'Proofpoint'
ORDER BY TABLE_NAME, ORDINAL_POSITION;
```

**Save as:** `04_METADATA_SAMPLES/metadata/metadata_proofpoint.csv`

---

### 6. ServiceNow Metadata

**Query:**
```sql
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    COMMENT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME = 'ServiceNow'
ORDER BY TABLE_NAME, ORDINAL_POSITION;
```

**Save as:** `04_METADATA_SAMPLES/metadata/metadata_servicenow.csv`

---

### 7. Leviat Metadata

**Query:**
```sql
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    COMMENT
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME = 'Leviat'
ORDER BY TABLE_NAME, ORDINAL_POSITION;
```

**Save as:** `04_METADATA_SAMPLES/metadata/metadata_leviat.csv`

---

## PART 2: Export Sample Data Files (11 files)

### SentinelOne Samples (2 files)

#### 1. Sentinel Endpoints (100 rows)
**Query:**
```sql
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINEL_ENDPOINTS;
```
**Save as:** `04_METADATA_SAMPLES/samples/sample_sentinel_endpoints.csv`

#### 2. Sentinel Versions (38 rows)
**Query:**
```sql
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINEL_VERSIONS;
```
**Save as:** `04_METADATA_SAMPLES/samples/sample_sentinel_versions.csv`

---

### CybelAngel Samples (2 files)

#### 3. CybelAngel Alerts (100 rows)
**Query:**
```sql
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_ALERTS;
```
**Save as:** `04_METADATA_SAMPLES/samples/sample_cybelangel_alerts.csv`

#### 4. CybelAngel Threats (0 rows - structure only)
**Query:**
```sql
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_THREATS;
```
**Save as:** `04_METADATA_SAMPLES/samples/sample_cybelangel_threats.csv`

---

### Proofpoint Samples (2 files)

#### 5. Proofpoint Message Logs (100 rows)
**Query:**
```sql
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_PROOFPOINT_MESSAGE_LOGS;
```
**Save as:** `04_METADATA_SAMPLES/samples/sample_proofpoint_message_logs.csv`

#### 6. Proofpoint Raw (0 rows - structure only)
**Query:**
```sql
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_PROOFPOINT_RAW;
```
**Save as:** `04_METADATA_SAMPLES/samples/sample_proofpoint_raw.csv`

---

### ServiceNow Samples (1 file)

#### 7. ServiceNow SNOW (100 rows)
**Query:**
```sql
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SERVICENOW_SNOW;
```
**Save as:** `04_METADATA_SAMPLES/samples/sample_servicenow_snow.csv`

---

### Leviat Samples (3 files - all empty, structure only)

#### 8. Leviat Users (0 rows)
**Query:**
```sql
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_USERS;
```
**Save as:** `04_METADATA_SAMPLES/samples/sample_leviat_users.csv`

#### 9. Leviat List Users (0 rows)
**Query:**
```sql
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_LIST_USERS;
```
**Save as:** `04_METADATA_SAMPLES/samples/sample_leviat_list_users.csv`

#### 10. Leviat Security Events (0 rows)
**Query:**
```sql
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_SECURITY_EVENTS;
```
**Save as:** `04_METADATA_SAMPLES/samples/sample_leviat_security_events.csv`

---

## Quick Reference: VS Code Snowflake Export Options

### Method 1: Right-click Menu
1. Execute query
2. Right-click on results grid
3. Select "Export Results" or "Download as CSV"
4. Choose location and filename

### Method 2: Results Panel Toolbar
1. Execute query
2. Look for download/export icon in results panel
3. Click icon
4. Choose CSV format
5. Choose location and filename

### Method 3: Command Palette
1. Execute query
2. Press `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)
3. Type "Snowflake: Export Results"
4. Select CSV format
5. Choose location and filename

---

## Troubleshooting

### Issue: "Export Results" option not available
**Solution:** Make sure you have executed the query and results are displayed in the results panel.

### Issue: Results showing "No data"
**Solution:**
- Verify you're using `USE ROLE DEV_DEVELOPER`
- Check that views were created successfully
- Run verification query:
  ```sql
  SELECT TABLE_NAME FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
  WHERE TABLE_SCHEMA = 'SAMPLES';
  ```

### Issue: Query times out
**Solution:**
- Verify warehouse is running: `USE WAREHOUSE DEV_WH;`
- Check warehouse size and resume if suspended

---

## Priority Order for Export

If you want to export files in priority order (most useful first):

### HIGH PRIORITY (Must have):
1. `metadata_all_services.csv` - Complete metadata
2. `sample_sentinel_endpoints.csv` - 100 rows with data
3. `sample_proofpoint_message_logs.csv` - 100 rows with data
4. `sample_servicenow_snow.csv` - 100 rows with data
5. `sample_cybelangel_alerts.csv` - 100 rows with data

### MEDIUM PRIORITY (Nice to have):
6. `metadata_sentinelone.csv`
7. `metadata_proofpoint.csv`
8. `metadata_servicenow.csv`
9. `metadata_cybelangel.csv`
10. `sample_sentinel_versions.csv` - 38 rows with data

### LOW PRIORITY (Structure only, no data):
11. All Leviat samples (0 rows)
12. `sample_cybelangel_threats.csv` (0 rows)
13. `sample_proofpoint_raw.csv` (0 rows)

---

## Verification

After exporting all files, verify with:

```bash
# Count files in metadata directory (should be 7)
ls 04_METADATA_SAMPLES/metadata/*.csv | wc -l

# Count files in samples directory (should be 11)
ls 04_METADATA_SAMPLES/samples/*.csv | wc -l
```

Expected result:
- 7 metadata files
- 11 sample files
- **Total: 18 CSV files**

---

## Next Steps After Export

Once all CSV files are exported:

1. ✅ Verify file sizes (files with data should be > 1KB)
2. ✅ Open a few CSV files to verify data looks correct
3. ✅ Use metadata CSVs to update Streamlit app SQL queries
4. ✅ Use sample CSVs to understand data structure and types
5. ✅ Update Streamlit apps with accurate column names

---

## Contact

For issues or questions about this export process, contact the GenericCorp Data Engineering Team.

Date: 2025-10-24
