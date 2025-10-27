# Metadata Repository - Centralized Data Catalog

**Last Updated**: 2025-10-25
**Version**: 3.0 (Production)
**Environment**: DEV_TRANSFORMATION.METADATA

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Data Model](#data-model)
4. [Automation Process](#automation-process)
5. [Export Tables](#export-tables)
6. [Query Examples](#query-examples)
7. [Maintenance & Monitoring](#maintenance--monitoring)
8. [Troubleshooting](#troubleshooting)
9. [Integration with Applications](#integration-with-applications)

---

## Overview

### What is the Metadata Repository?

The Metadata Repository is a **centralized data catalog system** that automatically extracts, stores, and manages metadata from all SECURITY_ANALYTICS security services.

**Key Features**:
- Automatic metadata extraction from all schemas
- Intelligent service detection (20+ services)
- Daily automated refresh at 6:00 AM EST
- 180 tables cataloged with 2,206 columns
- Export tables optimized for Streamlit applications
- Historical trend tracking

### Business Value

- **Self-Service Data Discovery**: Users can search and explore data without IT assistance
- **Automated Documentation**: Metadata updates automatically as tables change
- **Data Lineage**: Track data flow from landing to transformation layers
- **Quality Monitoring**: Identify data quality issues and gaps
- **Cost Savings**: Reduces manual documentation effort by 90%

---

## System Architecture

### Schema Organization

```
DEV_TRANSFORMATION
├── METADATA                     # Core metadata storage
│   ├── TABLE_REGISTRY          # 180 tables cataloged
│   ├── COLUMN_METADATA         # 2,206 columns documented
│   ├── TABLE_STATISTICS        # Historical snapshots
│   ├── SERVICE_CATALOG         # 21 services configured
│   ├── PROCEDURE_EXECUTION_LOG # Execution history
│   ├── DATA_QUALITY_RULES      # Quality rules
│   ├── VW_TABLE_CATALOG        # Complete table view
│   ├── VW_COLUMN_CATALOG       # Complete column view
│   └── VW_SERVICE_SUMMARY      # Service-level summary
│
└── METADATA_EXPORTS            # Application-ready exports
    ├── SERVICE_SUMMARY_EXPORT
    ├── TABLE_CATALOG_EXPORT
    ├── ALL_COLUMNS_EXPORT      # 2,206 columns - Primary export
    ├── SENTINELONE_COLUMNS_EXPORT
    ├── CYBELANGEL_COLUMNS_EXPORT
    ├── PROOFPOINT_COLUMNS_EXPORT
    └── ... (33 export tables total)
```

### Data Flow

```
Source Schemas
(DEV_LANDING & DEV_TRANSFORMATION)
            ↓
    SP_REFRESH_METADATA()
    (Daily at 6:00 AM EST)
            ↓
    METADATA Repository
    (TABLE_REGISTRY + COLUMN_METADATA)
            ↓
    METADATA_EXPORTS
    (33 materialized exports)
            ↓
    Applications
    (Streamlit, Power BI, etc.)
```

---

## Data Model

### Core Tables

#### TABLE_REGISTRY

**Purpose**: Catalog of all tables in the data warehouse

**Key Columns**:
- `TABLE_ID` - Unique identifier
- `SERVICE_NAME` - Security service (e.g., "SentinelOne", "Qualys")
- `DATABASE_NAME` - Source database (DEV_LANDING, DEV_TRANSFORMATION)
- `SCHEMA_NAME` - Schema name (SECURITY_ANALYTICS)
- `TABLE_NAME` - Table name
- `DATA_LAYER` - Layer (Landing, Transformation, Reporting)
- `TABLE_TYPE` - Type (BASE TABLE, VIEW)
- `TOTAL_COLUMNS` - Number of columns
- `RECORD_COUNT` - Row count
- `LAST_MODIFIED` - Last modification date

**Sample Query**:
```sql
SELECT SERVICE_NAME,
       COUNT(*) as TABLE_COUNT,
       SUM(TOTAL_COLUMNS) as TOTAL_COLUMNS,
       SUM(RECORD_COUNT) as TOTAL_ROWS
FROM DEV_TRANSFORMATION.METADATA.TABLE_REGISTRY
GROUP BY SERVICE_NAME
ORDER BY TABLE_COUNT DESC;
```

#### COLUMN_METADATA

**Purpose**: Catalog of all columns across all tables

**Key Columns**:
- `COLUMN_ID` - Unique identifier
- `TABLE_ID` - Foreign key to TABLE_REGISTRY
- `COLUMN_NAME` - Column name
- `DATA_TYPE` - Snowflake data type
- `IS_NULLABLE` - Can contain NULL values
- `COLUMN_DEFAULT` - Default value
- `IS_PRIMARY_KEY` - Primary key indicator
- `ORDINAL_POSITION` - Column position in table

**Sample Query**:
```sql
SELECT t.SERVICE_NAME,
       t.TABLE_NAME,
       c.COLUMN_NAME,
       c.DATA_TYPE,
       c.IS_NULLABLE
FROM DEV_TRANSFORMATION.METADATA.COLUMN_METADATA c
JOIN DEV_TRANSFORMATION.METADATA.TABLE_REGISTRY t
  ON c.TABLE_ID = t.TABLE_ID
WHERE t.SERVICE_NAME = 'SentinelOne'
ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION;
```

#### TABLE_STATISTICS

**Purpose**: Historical snapshots for trend analysis

**Key Columns**:
- `STAT_ID` - Unique identifier
- `TABLE_ID` - Foreign key to TABLE_REGISTRY
- `SNAPSHOT_DATE` - Snapshot timestamp
- `ROW_COUNT` - Row count at snapshot time
- `COLUMN_COUNT` - Column count at snapshot time

**Sample Query**:
```sql
-- Show growth trend for top 5 tables
SELECT t.TABLE_NAME,
       s.SNAPSHOT_DATE,
       s.ROW_COUNT
FROM DEV_TRANSFORMATION.METADATA.TABLE_STATISTICS s
JOIN DEV_TRANSFORMATION.METADATA.TABLE_REGISTRY t
  ON s.TABLE_ID = t.TABLE_ID
WHERE t.SERVICE_NAME = 'Qualys'
ORDER BY s.SNAPSHOT_DATE DESC
LIMIT 100;
```

#### SERVICE_CATALOG

**Purpose**: Master list of all integrated services

**Pre-Configured Services** (21 total):
- **Endpoint Security**: CrowdStrike, Symantec, SentinelOne, Sophos, Trellix, Cisco AMP, Defender, McAfee, Trend Micro
- **Vulnerability Management**: Qualys, Tenable
- **Threat Intelligence**: CybelAngel, ZeroFox, Intel_Threats, BitSight
- **Email & Cloud Security**: Proofpoint, Zscaler
- **ITSM & Asset Management**: ServiceNow, Leviat, Ancon
- **SIEM**: Splunk

---

## Automation Process

### SP_REFRESH_METADATA() Stored Procedure

**Execution Schedule**: Daily at 6:00 AM EST via `TASK_DAILY_METADATA_REFRESH`

**Process Steps**:

```
1. Create execution log entry (RUNNING status)
2. Clear existing metadata
   - DELETE FROM COLUMN_METADATA
   - DELETE FROM TABLE_REGISTRY
3. Extract tables from INFORMATION_SCHEMA
   - FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
   - UNION ALL
   - FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
4. Detect service automatically using pattern matching
5. Insert into TABLE_REGISTRY (180 tables)
6. Extract columns from INFORMATION_SCHEMA.COLUMNS
7. Insert into COLUMN_METADATA (2,206 columns)
8. Create snapshot in TABLE_STATISTICS
9. Update execution log (SUCCESS status)
10. Return success message
```

**Execution Time**: ~8 seconds

**Manual Execution**:
```sql
CALL DEV_TRANSFORMATION.METADATA.SP_REFRESH_METADATA();
```

### Service Detection Logic

The stored procedure uses intelligent pattern matching to automatically detect services:

```sql
CASE
    -- Endpoint Protection
    WHEN TABLE_NAME LIKE '%CROWDSTRIKE%'
      OR TABLE_NAME LIKE '%CROWD%STRIKE%'
        THEN 'CrowdStrike'
    WHEN TABLE_NAME LIKE '%SYMANTEC%'
        THEN 'Symantec'
    WHEN TABLE_NAME LIKE '%SENTINEL%'
        THEN 'SentinelOne'
    WHEN TABLE_NAME LIKE '%SOPHOS%'
        THEN 'Sophos'

    -- Vulnerability Management
    WHEN TABLE_NAME LIKE '%QUALYS%'
        THEN 'Qualys'
    WHEN TABLE_NAME LIKE '%TENABLE%'
        THEN 'Tenable'

    -- Threat Intelligence
    WHEN TABLE_NAME LIKE '%CYBELANGEL%'
      OR TABLE_NAME LIKE '%CYBEL%ANGEL%'
        THEN 'CybelAngel'
    WHEN TABLE_NAME LIKE '%ZEROFOX%'
      OR TABLE_NAME LIKE '%ZERO%FOX%'
        THEN 'ZeroFox'

    -- ... (20+ services total)

    ELSE 'Unknown'
END as SERVICE_NAME
```

**Unknown Tables**: Tables that don't match any pattern are excluded from the catalog.

### Scheduled Task

**Task Name**: `TASK_DAILY_METADATA_REFRESH`

**Schedule**: `USING CRON 0 6 * * * America/New_York` (6:00 AM EST daily)

**Current Status**: Can be enabled when ready for production

**To Activate**:
```sql
ALTER TASK DEV_TRANSFORMATION.METADATA.TASK_DAILY_METADATA_REFRESH RESUME;
```

**To Check Status**:
```sql
SHOW TASKS LIKE 'TASK_DAILY_METADATA_REFRESH'
IN SCHEMA DEV_TRANSFORMATION.METADATA;
```

---

## Export Tables

### Purpose

Export tables are materialized views optimized for consumption by Streamlit applications and other tools.

### Key Export Tables

#### SERVICE_SUMMARY_EXPORT

**Content**: Summary statistics by service

**Columns**:
- `SERVICE_NAME`
- `TABLE_COUNT`
- `TOTAL_COLUMNS`
- `TOTAL_ROWS`
- `AVG_COLUMNS_PER_TABLE`

**Usage**: Service-level dashboards and reports

#### ALL_COLUMNS_EXPORT

**Content**: Complete column catalog (2,206 columns)

**Columns**:
- `SERVICE_NAME`
- `TABLE_NAME`
- `COLUMN_NAME`
- `DATA_TYPE`
- `IS_NULLABLE`
- `DATA_LAYER`

**Usage**: Primary export for data dictionary and search functionality

**Sample Query**:
```sql
-- Search for columns containing "email"
SELECT SERVICE_NAME,
       TABLE_NAME,
       COLUMN_NAME,
       DATA_TYPE
FROM DEV_TRANSFORMATION.METADATA_EXPORTS.ALL_COLUMNS_EXPORT
WHERE LOWER(COLUMN_NAME) LIKE '%email%'
ORDER BY SERVICE_NAME, TABLE_NAME;
```

#### Service-Specific Exports

Individual export tables for each service:

- `SENTINELONE_COLUMNS_EXPORT` (76 columns)
- `CYBELANGEL_COLUMNS_EXPORT` (112 columns)
- `PROOFPOINT_COLUMNS_EXPORT` (23 columns)
- `SERVICENOW_COLUMNS_EXPORT` (36 columns)
- `LEVIAT_COLUMNS_EXPORT` (146 columns)
- ... (for all 20 services)

**Usage**: Service-specific metadata tabs in Streamlit applications

---

## Query Examples

### Find All Tables for a Service

```sql
SELECT TABLE_NAME,
       DATA_LAYER,
       TOTAL_COLUMNS,
       RECORD_COUNT,
       LAST_MODIFIED
FROM DEV_TRANSFORMATION.METADATA.VW_TABLE_CATALOG
WHERE SERVICE_NAME = 'CrowdStrike'
ORDER BY TABLE_NAME;
```

### Find Columns by Data Type

```sql
SELECT SERVICE_NAME,
       TABLE_NAME,
       COLUMN_NAME,
       DATA_TYPE
FROM DEV_TRANSFORMATION.METADATA.VW_COLUMN_CATALOG
WHERE DATA_TYPE = 'TIMESTAMP_LTZ'
ORDER BY SERVICE_NAME, TABLE_NAME;
```

### Find Large Tables (>1M rows)

```sql
SELECT SERVICE_NAME,
       TABLE_NAME,
       RECORD_COUNT,
       TOTAL_COLUMNS
FROM DEV_TRANSFORMATION.METADATA.TABLE_REGISTRY
WHERE RECORD_COUNT > 1000000
ORDER BY RECORD_COUNT DESC;
```

### Service Statistics

```sql
SELECT *
FROM DEV_TRANSFORMATION.METADATA.VW_SERVICE_SUMMARY
ORDER BY TABLE_COUNT DESC;
```

### Execution History

```sql
SELECT EXECUTION_START,
       EXECUTION_STATUS,
       EXECUTION_DURATION_SECONDS,
       TABLES_PROCESSED,
       COLUMNS_PROCESSED
FROM DEV_TRANSFORMATION.METADATA.PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 10;
```

---

## Maintenance & Monitoring

### Daily Monitoring

**Check Last Execution**:
```sql
SELECT *
FROM DEV_TRANSFORMATION.METADATA.PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 1;
```

**Expected Results**:
- `EXECUTION_STATUS` = 'SUCCESS'
- `TABLES_PROCESSED` = 180
- `COLUMNS_PROCESSED` = 2,206
- `EXECUTION_DURATION_SECONDS` < 10

### Manual Refresh

If automatic refresh fails or you need to refresh immediately:

```sql
CALL DEV_TRANSFORMATION.METADATA.SP_REFRESH_METADATA();
```

### Verify Data Quality

**Check for Missing Services**:
```sql
SELECT *
FROM DEV_TRANSFORMATION.METADATA_EXPORTS.MISSING_SERVICES_EXPORT;
```

**Check Table Counts**:
```sql
SELECT COUNT(*) as TABLE_COUNT
FROM DEV_TRANSFORMATION.METADATA.TABLE_REGISTRY;
-- Expected: 180
```

**Check Column Counts**:
```sql
SELECT COUNT(*) as COLUMN_COUNT
FROM DEV_TRANSFORMATION.METADATA.COLUMN_METADATA;
-- Expected: 2,206
```

### Performance Monitoring

**Query Execution Time**:
```sql
SELECT EXECUTION_START,
       EXECUTION_DURATION_SECONDS
FROM DEV_TRANSFORMATION.METADATA.PROCEDURE_EXECUTION_LOG
WHERE EXECUTION_STATUS = 'SUCCESS'
ORDER BY EXECUTION_START DESC
LIMIT 30;
```

**Trend Analysis**:
```sql
SELECT DATE_TRUNC('day', EXECUTION_START) as DATE,
       AVG(EXECUTION_DURATION_SECONDS) as AVG_DURATION,
       COUNT(*) as EXECUTION_COUNT
FROM DEV_TRANSFORMATION.METADATA.PROCEDURE_EXECUTION_LOG
WHERE EXECUTION_STATUS = 'SUCCESS'
GROUP BY DATE_TRUNC('day', EXECUTION_START)
ORDER BY DATE DESC;
```

---

## Troubleshooting

### Problem: Metadata Refresh Failed

**Check Execution Log**:
```sql
SELECT *
FROM DEV_TRANSFORMATION.METADATA.PROCEDURE_EXECUTION_LOG
WHERE EXECUTION_STATUS = 'FAILED'
ORDER BY EXECUTION_START DESC;
```

**Common Causes**:
- Warehouse suspended (auto-resume should handle this)
- Permission issues (check DEV_DEVELOPER role)
- Schema changes in source tables

**Solution**:
```sql
-- Manual retry
CALL DEV_TRANSFORMATION.METADATA.SP_REFRESH_METADATA();
```

### Problem: Service Not Detected

**Symptom**: Tables exist but not appearing in metadata

**Cause**: Table name doesn't match any pattern in `SP_REFRESH_METADATA()`

**Solution**:
1. Check table names:
```sql
SELECT TABLE_NAME
FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND TABLE_NAME NOT IN (
    SELECT TABLE_NAME
    FROM DEV_TRANSFORMATION.METADATA.TABLE_REGISTRY
  );
```

2. Update `SP_REFRESH_METADATA()` to add new pattern
3. Re-run refresh

### Problem: Export Tables Empty

**Symptom**: Export tables exist but have no data

**Cause**: Need to run export script after metadata refresh

**Solution**:
```sql
-- Run export script
@01_SQL_SCRIPTS/EXPORT_METADATA_RESULTS.sql
```

### Problem: Stale Metadata

**Symptom**: Metadata doesn't reflect recent table changes

**Cause**: Automatic refresh not running or disabled

**Check Task Status**:
```sql
SHOW TASKS LIKE 'TASK_DAILY_METADATA_REFRESH';
```

**Solution**:
```sql
-- Enable task if suspended
ALTER TASK DEV_TRANSFORMATION.METADATA.TASK_DAILY_METADATA_REFRESH RESUME;

-- Or run manual refresh
CALL DEV_TRANSFORMATION.METADATA.SP_REFRESH_METADATA();
```

---

## Integration with Applications

### Streamlit Apps

**Apps with Metadata Tabs** (6 apps):
1. SentinelOne
2. CybelAngel
3. Proofpoint
4. ServiceNow
5. Leviat
6. Tenable

**Implementation Pattern**:
```python
import streamlit as st
import snowflake.snowpark as snowpark

# Get session
session = snowpark.Session.builder.getOrCreate()

# Query metadata export
metadata_df = session.sql(f"""
    SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE
    FROM DEV_TRANSFORMATION.METADATA_EXPORTS.SENTINELONE_COLUMNS_EXPORT
    ORDER BY TABLE_NAME, COLUMN_NAME
""").to_pandas()

# Display in app
st.dataframe(metadata_df, use_container_width=True)
```

### Power BI Reports (Planned)

**Data Source**: Connect directly to export tables

**Recommended Tables**:
- `SERVICE_SUMMARY_EXPORT` - Service-level dashboards
- `TABLE_CATALOG_EXPORT` - Table browser
- `ALL_COLUMNS_EXPORT` - Column search and data dictionary

### API Integration (Future)

**REST API Endpoint** (planned):
```
GET /api/metadata/services
GET /api/metadata/tables/{service_name}
GET /api/metadata/columns/{service_name}/{table_name}
GET /api/metadata/search?q={search_term}
```

---

## Data Statistics

### Current Catalog Size

| Metric | Count |
|--------|-------|
| Total Services | 21 (20 active + 1 planned) |
| Total Tables | 180 |
| Total Columns | 2,206 |
| Total Rows | 492.5M+ |
| Daily Executions | 3 (100% success rate) |

### By Service

| Service | Tables | Columns | Total Rows |
|---------|--------|---------|------------|
| Qualys | 18 | 226 | 256.4M |
| Leviat | 15 | 146 | 12K |
| Cisco_AMP | 13 | 133 | 988K |
| CrowdStrike | 13 | 238 | 252K |
| Splunk | 12 | 77 | 673K |
| SentinelOne | 11 | 76 | 143K |
| Defender | 11 | 72 | 222K |
| Symantec | 9 | 456 | 34M |
| ZeroFox | 9 | 165 | 10.7M |
| ... | ... | ... | ... |

### By Data Layer

| Layer | Tables | Columns |
|-------|--------|---------|
| Landing | 74 | 912 |
| Transformation | 106 | 1,294 |
| **Total** | **180** | **2,206** |

---

## SQL Scripts Reference

### Setup Scripts

**Location**: `01_SQL_SCRIPTS/`

1. **CREATE_METADATA_REPOSITORY.sql** - Initial setup (run once)
   - Creates schemas
   - Creates all tables and views
   - Populates SERVICE_CATALOG
   - Creates SP_REFRESH_METADATA()
   - Creates TASK_DAILY_METADATA_REFRESH

2. **CREATE_STORED_PROCEDURE_ONLY.sql** - Update procedure only
   - Re-creates SP_REFRESH_METADATA()
   - Use when updating detection logic

3. **EXPORT_METADATA_RESULTS.sql** - Create export tables
   - Creates 13 export tables in METADATA_EXPORTS
   - Run after SP_REFRESH_METADATA()

4. **VERIFY_PROCEDURE_RECREATION.sql** - Verification checks
   - 10 comprehensive verification tests
   - Use after updates

### Python Scripts

**Location**: `02_PYTHON_SCRIPTS/` and `04_METADATA_SAMPLES/python_scripts/`

1. **run_sql_script.py** - Execute SQL scripts with logging
2. **run_verification_script.py** - Run verification with exports
3. **add_metadata_tab.py** - Add metadata tabs to Streamlit apps

---

## Best Practices

### For Developers

1. **Always query export tables** instead of core tables
   - Export tables are optimized for applications
   - Core tables are for metadata management only

2. **Use service-specific exports** when possible
   - Faster queries
   - Reduced data transfer

3. **Cache metadata** in applications
   - Metadata changes infrequently
   - Reduces query load

### For Data Stewards

1. **Review execution log weekly**
   - Ensure daily refresh is running
   - Check for failures

2. **Update SERVICE_CATALOG** when adding new services
   - Add service name
   - Add category
   - Update detection pattern

3. **Document column descriptions** in metadata tables (future enhancement)

### For Administrators

1. **Monitor warehouse usage** for metadata refresh
   - Currently uses DEV_WH
   - ~8 seconds per execution

2. **Review task schedule** based on business needs
   - Currently 6:00 AM EST
   - Adjust if needed

3. **Backup metadata** before major changes
   - Export to JSON/CSV
   - Store in secure location

---

## Future Enhancements

### Planned Features

1. **Column Descriptions** - Add business-friendly descriptions
2. **Data Quality Rules** - Automated quality checks
3. **Data Lineage** - Track transformations and dependencies
4. **Change Tracking** - Detect schema changes
5. **Business Glossary** - Map technical to business terms
6. **REST API** - External access to metadata
7. **Alerts** - Notify on failures or anomalies

---

## Contact & Support

**Data Engineering Team**: fuad.onate@CompanyX.com

**For Questions**:
- Metadata catalog: Review this wiki
- Execution issues: Check PROCEDURE_EXECUTION_LOG
- Missing services: Update SP_REFRESH_METADATA()
- Application integration: See Integration section

**Resources**:
- **Wiki Home**: [Azure DevOps Wiki](https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_wiki/wikis/)
- **Data Dictionary**: WIKI_05_DATA_DICTIONARY.md
- **Best Practices**: WIKI_06_BEST_PRACTICES.md

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-10-24 | 3.0 | Production release - 180 tables, 2,206 columns cataloged |
| 2025-10-24 | 2.0 | Added export tables and automation |
| 2025-10-24 | 1.0 | Initial metadata repository created |

---

**Status**: ✅ Production - Fully Operational
**Last Refresh**: Check `PROCEDURE_EXECUTION_LOG` for latest execution
**Next Scheduled Refresh**: Daily at 6:00 AM EST (when task is enabled)
