# Quick Reference - All Services Column Summary

**Date:** 2025-10-24
**Purpose:** Quick reference for building Streamlit apps with correct table and column names

---

## Services Summary

| Service | Tables with Data | Total Rows | Location |
|---------|-----------------|------------|----------|
| **ServiceNow** | 1 table | 24,650 | DEV_LANDING.SECURITY_ANALYTICS |
| **Proofpoint** | 1 table | 206,794 | DEV_LANDING.SECURITY_ANALYTICS |
| **SentinelOne** | 2 tables | 4,226 total | DEV_TRANSFORMATION.SECURITY_ANALYTICS |
| **CybelAngel** | 1 table | 196 | DEV_TRANSFORMATION.SECURITY_ANALYTICS |
| **Leviat** | 0 tables | 0 (empty) | DEV_TRANSFORMATION.SECURITY_ANALYTICS |
| **Tenable** | 0 tables | - | Not found |

---

## 1. ServiceNow (24,650 rows)

**Table:** `DEV_LANDING.SECURITY_ANALYTICS.SNOW`

### Key Columns (25 total):
```
COMPUTER_NAME              - Text
MANUFACTURER               - Text (Dell Inc., VMware, Lenovo, Microsoft)
MODEL                      - Text
COMPUTERTYPES              - Text (Desktop, Notebook, Virtual Server, Virtual Workstation)
OPERATING_SYSTEM           - Text (Windows 10/11, Linux)
DOMAIN_NAME                - Text
ORGANISATION               - Text
MOST_FREQUENT_USER         - Text (DOMAIN\username)
LAST_SCANNED               - Date (DD/MM/YYYY format as text)
STATUS                     - Text (Active)
CLIENT_VERSION             - Text (7.0.0, 5.3.1)
PROCESSOR_TYPE             - Text
PROCESSORS                 - Number
PROCESSOR_CORES            - Number
LOGICAL_PROCESSORS         - Number
```

### Sample Query:
```sql
SELECT
    COMPUTER_NAME,
    MANUFACTURER,
    MODEL,
    OPERATING_SYSTEM,
    LAST_SCANNED,
    STATUS
FROM DEV_LANDING.SECURITY_ANALYTICS.SNOW
WHERE STATUS = 'Active'
ORDER BY TRY_TO_DATE(LAST_SCANNED, 'DD/MM/YYYY') DESC
LIMIT 100;
```

---

## 2. Proofpoint (206,794 rows)

**Table:** `DEV_LANDING.SECURITY_ANALYTICS.PROOFPOINT_MESSAGE_LOGS`

### To Get Columns:
```sql
SELECT COLUMN_NAME, DATA_TYPE
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME = 'Proofpoint'
  AND TABLE_NAME = 'PROOFPOINT_MESSAGE_LOGS'
ORDER BY ORDINAL_POSITION;
```

### Sample Data View:
```sql
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_PROOFPOINT_MESSAGE_LOGS
LIMIT 10;
```

### Expected Columns (Email Security):
- Message ID
- Sender/Recipient
- Subject
- Timestamp
- Threat indicators
- Action taken
- Message size

---

## 3. SentinelOne (4,226 total rows)

### Table 1: `DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_SENTINEL_ENDPOINTS` (4,188 rows)

**Purpose:** Endpoint inventory and security status

### To Get Columns:
```sql
SELECT COLUMN_NAME, DATA_TYPE
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME = 'SentinelOne'
  AND TABLE_NAME = 'FACT_SENTINEL_ENDPOINTS'
ORDER BY ORDINAL_POSITION;
```

### Sample Data:
```sql
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINEL_ENDPOINTS
LIMIT 10;
```

### Expected Columns (Endpoint Security):
- Endpoint ID/Name
- Agent version
- OS type/version
- Last active date
- Threat count
- Infection status
- Domain/Site

---

### Table 2: `DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_SENTINEL_VERSIONS` (38 rows)

**Purpose:** Agent version reference/lookup

### Sample Data:
```sql
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINEL_VERSIONS;
```

### Expected Columns:
- Version ID
- Version number
- Release date
- Support status

---

## 4. CybelAngel (196 rows)

**Table:** `DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_CYBELANGEL_ALERTS`

**Purpose:** Cyber threat alerts and data leak detection

### To Get Columns:
```sql
SELECT COLUMN_NAME, DATA_TYPE
FROM DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
WHERE SERVICE_NAME = 'CybelAngel'
  AND TABLE_NAME = 'DIM_CYBELANGEL_ALERTS'
ORDER BY ORDINAL_POSITION;
```

### Sample Data:
```sql
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_ALERTS
LIMIT 10;
```

### Expected Columns (Threat Intelligence):
- Alert ID
- Severity
- Category
- Description
- Detection date
- Source
- Status

---

## 5. Leviat (0 rows - EMPTY)

**Tables:** All tables exist but are empty (0 rows)

```
DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_LEVIAT_USERS (0 rows)
DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_LEVIAT_LIST_USERS (0 rows)
DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_LEVIAT_SECURITY_EVENTS (0 rows)
```

**Action:** Structure exists but no data loaded yet. Cannot build functional app until data is available.

---

## 6. Tenable (NOT FOUND)

**Status:** No tables with "TENABLE" in name found in database

**Expected Tables (based on app):**
- DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_TENABLE
- DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_TENABLE_VULN
- DEV_LANDING.SECURITY_ANALYTICS.L_TENABLE_ASSETS

**Action:** Verify if Tenable integration is active. Cannot build app without tables.

---

## How to Get Complete Column Lists

### Method 1: Query Metadata View
```sql
USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;

-- Get all columns for a specific service
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

### Method 2: Query Sample Views
```sql
-- See actual data to understand structure
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINEL_ENDPOINTS LIMIT 10;
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_ALERTS LIMIT 10;
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_PROOFPOINT_MESSAGE_LOGS LIMIT 10;
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SERVICENOW_SNOW LIMIT 10;
```

### Method 3: Use Exported CSV Files
Look at the CSV files in:
- `04_METADATA_SAMPLES/metadata/metadata_{service}.csv` - Column lists
- `04_METADATA_SAMPLES/samples/sample_{table}.csv` - Sample data

---

## Streamlit App Development Priority

### Priority 1: Apps with Good Data (Update/Create)
1. ✅ **ServiceNow** - 24,650 rows - Asset inventory
2. ✅ **Proofpoint** - 206,794 rows - Email security
3. ✅ **SentinelOne** - 4,188 rows - Endpoint security

### Priority 2: Apps with Limited Data
4. ⚠️ **CybelAngel** - 196 rows - Threat intelligence (small dataset)

### Priority 3: Cannot Build Yet
5. ❌ **Leviat** - 0 rows - No data
6. ❌ **Tenable** - No tables - Integration missing

---

## Next Steps

1. **Export all metadata CSV files** from the queries in `EXPORT_ESSENTIAL_ONLY.sql`
2. **Review sample data** to understand structure
3. **Update existing Streamlit apps** with correct column names
4. **Build new apps** for services that don't have apps yet
5. **Test all apps** with real queries

---

## Important Notes

### Data Type Conversions
- **Dates stored as text:** Use `TRY_TO_DATE(column, 'DD/MM/YYYY')` or appropriate format
- **Booleans as text:** Convert 'true'/'false' strings to actual boolean if needed
- **Numbers as text:** Use `TRY_TO_NUMBER()` if stored as text

### Common Patterns
- **Filter by date range:** `WHERE date_column >= DATEADD(day, -{days}, CURRENT_DATE())`
- **Group by category:** `GROUP BY category_column ORDER BY COUNT(*) DESC`
- **Top N results:** `ORDER BY relevant_column LIMIT {n}`

### Performance Tips
- Always use `LIMIT` for large tables (Proofpoint has 206K rows)
- Add indexes on frequently filtered columns (if possible)
- Use `WHERE` clauses to reduce data scanned
- Consider creating aggregated views for dashboards

---

**Created:** 2025-10-24
**Maintained By:** GenericCorp Data Engineering Team
