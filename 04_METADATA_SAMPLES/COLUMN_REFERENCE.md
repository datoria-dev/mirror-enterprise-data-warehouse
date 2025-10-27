# Column Reference Guide - All Services

This document lists all available columns for each service to help build Streamlit app queries.

**Source:** Extracted from `DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA`

**Date:** 2025-10-24

---

## How to Use This Reference

When building SQL queries in Streamlit apps, use this reference to:
1. Know which columns are available
2. Understand data types for proper filtering
3. Build accurate SELECT statements
4. Create proper GROUP BY clauses

---

## Quick Query Template

```sql
-- Get column list for a service
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME = 'SentinelOne'  -- Change service name here
ORDER BY TABLE_NAME, ORDINAL_POSITION;
```

---

## Services Overview

### Services with Data (Ready to Use):
- ✅ **SentinelOne**: 2 tables (FACT_SENTINEL_ENDPOINTS: 4,188 rows, DIM_SENTINEL_VERSIONS: 38 rows)
- ✅ **CybelAngel**: 1 table with data (DIM_CYBELANGEL_ALERTS: 196 rows)
- ✅ **Proofpoint**: 1 table with data (PROOFPOINT_MESSAGE_LOGS: 206,794 rows)
- ✅ **ServiceNow**: 1 table with data (SNOW: 24,650 rows)

### Services with Empty Tables:
- ⚠️ **Leviat**: 3 tables (all 0 rows - structure exists but no data)
- ⚠️ **CybelAngel**: FACT_CYBELANGEL_THREATS (0 rows)

### Services Missing:
- ❌ **Tenable**: No tables found in database

---

## Table Locations Reference

### SentinelOne
```
DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_SENTINEL_ENDPOINTS (4,188 rows)
DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_SENTINEL_VERSIONS (38 rows)
```

### CybelAngel
```
DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_CYBELANGEL_ALERTS (196 rows)
DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_CYBELANGEL_THREATS (0 rows)
```

### Proofpoint
```
DEV_LANDING.SECURITY_ANALYTICS.PROOFPOINT_MESSAGE_LOGS (206,794 rows)
DEV_LANDING.SECURITY_ANALYTICS.L_PROOFPOINT_RAW (0 rows)
```

### ServiceNow
```
DEV_LANDING.SECURITY_ANALYTICS.SNOW (24,650 rows)
```

### Leviat
```
DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_LEVIAT_USERS (0 rows)
DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_LEVIAT_LIST_USERS (0 rows)
DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_LEVIAT_SECURITY_EVENTS (0 rows)
```

---

## Export Instructions

To get the complete column list for each service, run these queries and export as CSV:

### 1. SentinelOne Columns
```sql
USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;

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
**Export as:** `04_METADATA_SAMPLES/metadata/metadata_sentinelone.csv`

---

### 2. CybelAngel Columns
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
**Export as:** `04_METADATA_SAMPLES/metadata/metadata_cybelangel.csv`

---

### 3. Proofpoint Columns
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
**Export as:** `04_METADATA_SAMPLES/metadata/metadata_proofpoint.csv`

---

### 4. ServiceNow Columns
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
**Export as:** `04_METADATA_SAMPLES/metadata/metadata_servicenow.csv`

---

### 5. Leviat Columns
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
**Export as:** `04_METADATA_SAMPLES/metadata/metadata_leviat.csv`

---

## Sample Data Export

For each service, also export sample data to understand the data structure:

### SentinelOne Sample Data
```sql
-- Endpoints (100 rows)
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINEL_ENDPOINTS;
-- Export as: 04_METADATA_SAMPLES/samples/sample_sentinel_endpoints.csv

-- Versions (38 rows)
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINEL_VERSIONS;
-- Export as: 04_METADATA_SAMPLES/samples/sample_sentinel_versions.csv
```

### CybelAngel Sample Data
```sql
-- Alerts (100 rows)
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_ALERTS;
-- Export as: 04_METADATA_SAMPLES/samples/sample_cybelangel_alerts.csv

-- Threats (0 rows - structure only)
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_THREATS;
-- Export as: 04_METADATA_SAMPLES/samples/sample_cybelangel_threats.csv
```

### Proofpoint Sample Data
```sql
-- Message Logs (100 rows)
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_PROOFPOINT_MESSAGE_LOGS;
-- Export as: 04_METADATA_SAMPLES/samples/sample_proofpoint_message_logs.csv

-- Raw (0 rows - structure only)
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_PROOFPOINT_RAW;
-- Export as: 04_METADATA_SAMPLES/samples/sample_proofpoint_raw.csv
```

### ServiceNow Sample Data
```sql
-- SNOW table (100 rows)
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SERVICENOW_SNOW;
-- Export as: 04_METADATA_SAMPLES/samples/sample_servicenow_snow.csv
```

### Leviat Sample Data
```sql
-- Users (0 rows - structure only)
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_USERS;
-- Export as: 04_METADATA_SAMPLES/samples/sample_leviat_users.csv

-- List Users (0 rows - structure only)
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_LIST_USERS;
-- Export as: 04_METADATA_SAMPLES/samples/sample_leviat_list_users.csv

-- Security Events (0 rows - structure only)
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_LEVIAT_SECURITY_EVENTS;
-- Export as: 04_METADATA_SAMPLES/samples/sample_leviat_security_events.csv
```

---

## Using This Reference in Streamlit Apps

### Example: Building a Query for SentinelOne

Once you have the metadata CSV, you can build queries like:

```python
# In your Streamlit app
query = """
SELECT
    ENDPOINT_ID,
    ENDPOINT_NAME,
    DOMAIN,
    OS_TYPE,
    AGENT_VERSION,
    LAST_ACTIVE_DATE,
    THREAT_COUNT
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_SENTINEL_ENDPOINTS
WHERE LAST_ACTIVE_DATE >= DATEADD(day, -30, CURRENT_DATE())
ORDER BY LAST_ACTIVE_DATE DESC
"""
```

**Important:** Use the exact column names from the metadata CSV!

---

## Common Patterns for Streamlit Apps

### Pattern 1: Get Recent Records
```sql
SELECT *
FROM {table_name}
WHERE {date_column} >= DATEADD(day, -{days}, CURRENT_DATE())
ORDER BY {date_column} DESC
LIMIT {limit}
```

### Pattern 2: Aggregate by Category
```sql
SELECT
    {category_column},
    COUNT(*) as COUNT,
    MAX({date_column}) as LATEST_DATE
FROM {table_name}
GROUP BY {category_column}
ORDER BY COUNT DESC
```

### Pattern 3: Filter by Status/Type
```sql
SELECT *
FROM {table_name}
WHERE {status_column} IN ({selected_statuses})
  AND {date_column} >= {start_date}
  AND {date_column} <= {end_date}
ORDER BY {date_column} DESC
```

---

## Next Steps

1. ✅ Export all metadata CSVs (5 files for 5 services)
2. ✅ Export all sample data CSVs (11 files)
3. ✅ Review CSV files to understand data structure
4. ✅ Use column names from CSVs to build Streamlit app queries
5. ✅ Test queries in Snowflake before adding to Streamlit apps
6. ✅ Update existing Streamlit apps with correct column names

---

## Troubleshooting

### Issue: Column not found in table
**Solution:** Check the metadata CSV to see the exact column name (case-sensitive)

### Issue: Wrong data type
**Solution:** Check DATA_TYPE column in metadata CSV and cast if needed

### Issue: Empty results
**Solution:** Check ROW_COUNT in discovery results - some tables are empty

---

**Last Updated:** 2025-10-24
**Maintained By:** GenericCorp Data Engineering Team
