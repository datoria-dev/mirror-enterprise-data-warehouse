# SECURITY_ANALYTICS Data Warehouse - Metadata Extraction & Automation

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Centralized Metadata Extraction](#centralized-metadata-extraction)
- [Automatic Service Detection](#automatic-service-detection)
- [Metadata Repository Schema](#metadata-repository-schema)
- [Scheduled Automation](#scheduled-automation)
- [Export Process](#export-process)
- [Integration with Applications](#integration-with-applications)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Deployment Guide](#deployment-guide)
- [Troubleshooting](#troubleshooting)

---

## Overview

The SECURITY_ANALYTICS Data Warehouse implements a **centralized metadata extraction system** that automatically discovers, catalogs, and maintains metadata for all security service tables across the data warehouse.

### Key Features

- **Centralized Extraction**: Single stored procedure (`SP_REFRESH_METADATA`) processes all schemas
- **Automatic Service Detection**: Intelligent pattern matching identifies 20+ security services
- **Scheduled Automation**: Daily refresh task maintains up-to-date metadata
- **Export Integration**: Materialized exports feed Streamlit apps and Power BI
- **Complete Coverage**: 180 tables, 2,206 columns across DEV_LANDING and DEV_TRANSFORMATION

### Business Value

- **Self-Service Analytics**: Users can browse data catalog without manual documentation
- **Data Governance**: Centralized view of all data assets and their lineage
- **Application Integration**: Metadata tabs in Streamlit apps provide instant documentation
- **Automated Maintenance**: No manual updates required as new tables are added
- **Quality Monitoring**: Built-in statistics tracking for data quality

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    METADATA EXTRACTION FLOW                  │
└─────────────────────────────────────────────────────────────┘

1. SOURCE SCHEMAS
   ├── DEV_LANDING.SECURITY_ANALYTICS (Raw data tables)
   └── DEV_TRANSFORMATION.SECURITY_ANALYTICS (Processed data tables)
              ↓
2. EXTRACTION PROCEDURE
   └── SP_REFRESH_METADATA()
       ├── Queries INFORMATION_SCHEMA.TABLES
       ├── Queries INFORMATION_SCHEMA.COLUMNS
       ├── Applies service detection logic
       └── Calculates statistics
              ↓
3. METADATA REPOSITORY (DEV_TRANSFORMATION.METADATA)
   ├── TABLE_REGISTRY (180 tables)
   ├── COLUMN_METADATA (2,206 columns)
   ├── TABLE_STATISTICS (row counts, sizes)
   ├── SERVICE_CATALOG (21 services)
   ├── PROCEDURE_EXECUTION_LOG (audit trail)
   └── DATA_QUALITY_RULES (validation rules)
              ↓
4. EXPORT PROCESS (EXPORT_METADATA_RESULTS.sql)
   └── Creates 13 export tables in METADATA_EXPORTS schema
              ↓
5. CONSUMPTION LAYER
   ├── Streamlit Apps (6 services with metadata tabs)
   ├── Power BI Reports (planned)
   └── Ad-hoc Queries (VW_TABLE_CATALOG, VW_COLUMN_CATALOG)
```

### Automation Schedule

- **Daily Execution**: 6:00 AM EST (2:00 AM UTC)
- **Trigger**: Snowflake Task (`TASK_DAILY_METADATA_REFRESH`)
- **Duration**: ~8 seconds average
- **Process**: Extract → Validate → Update → Export → Log

---

## Centralized Metadata Extraction

### SP_REFRESH_METADATA Stored Procedure

The core component is the **SP_REFRESH_METADATA** stored procedure, which serves as the centralized metadata extraction engine.

#### Location
```
Database: DEV_TRANSFORMATION
Schema: METADATA
Procedure: SP_REFRESH_METADATA()
```

#### What It Does

1. **Clears existing metadata** (truncate TABLE_REGISTRY and COLUMN_METADATA)
2. **Extracts table metadata** from both DEV_LANDING and DEV_TRANSFORMATION schemas
3. **Applies automatic service detection** to classify tables by security service
4. **Extracts column metadata** for all detected tables
5. **Calculates statistics** (row counts, last modified dates, sizes)
6. **Logs execution** with metrics and status
7. **Returns summary** of processing results

#### Execution Example

```sql
-- Manual execution (when needed)
USE ROLE DEV_DEVELOPER;
USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA METADATA;

CALL SP_REFRESH_METADATA();

-- Expected output:
-- "✅ Metadata refresh completed. Tables: 180, Columns: 2206, Duration: 8 seconds"
```

#### Performance Metrics

| Metric | Value |
|--------|-------|
| Tables Processed | 180 |
| Columns Processed | 2,206 |
| Average Duration | 8 seconds |
| Tables per Second | 22.5 |
| Services Detected | 20 |

---

## Automatic Service Detection

### Service Detection Logic

The procedure uses **pattern matching** to automatically classify tables by their source security service. This eliminates manual tagging and ensures consistency.

#### Pattern Matching Rules

```sql
CASE
    -- Endpoint Security
    WHEN TABLE_NAME LIKE '%SENTINEL%' THEN 'SentinelOne'
    WHEN TABLE_NAME LIKE '%CROWDSTRIKE%' THEN 'CrowdStrike'

    -- Email Security
    WHEN TABLE_NAME LIKE '%PROOFPOINT%' THEN 'Proofpoint'
    WHEN TABLE_NAME LIKE '%MIMECAST%' THEN 'Mimecast'

    -- Vulnerability Management
    WHEN TABLE_NAME LIKE '%QUALYS%' THEN 'Qualys'
    WHEN TABLE_NAME LIKE '%TENABLE%' THEN 'Tenable'

    -- Identity & Access
    WHEN TABLE_NAME LIKE '%OKTA%' THEN 'Okta'
    WHEN TABLE_NAME LIKE '%AZURE%AD%' OR TABLE_NAME LIKE '%AZUREAD%' THEN 'Azure AD'

    -- SIEM & Monitoring
    WHEN TABLE_NAME LIKE '%SPLUNK%' THEN 'Splunk'
    WHEN TABLE_NAME LIKE '%CYBELANGEL%' THEN 'CybelAngel'

    -- Cloud Security
    WHEN TABLE_NAME LIKE '%PRISMA%' OR TABLE_NAME LIKE '%PALO%ALTO%' THEN 'Prisma Cloud'
    WHEN TABLE_NAME LIKE '%CLOUDFLARE%' THEN 'Cloudflare'

    -- IT Service Management
    WHEN TABLE_NAME LIKE '%SERVICENOW%' OR TABLE_NAME LIKE '%SNOW%' THEN 'ServiceNow'
    WHEN TABLE_NAME LIKE '%JIRA%' THEN 'Jira'

    -- Asset Management
    WHEN TABLE_NAME LIKE '%LEVIAT%' THEN 'Leviat'
    WHEN TABLE_NAME LIKE '%TANIUM%' THEN 'Tanium'

    -- Network Security
    WHEN TABLE_NAME LIKE '%ZSCALER%' THEN 'Zscaler'
    WHEN TABLE_NAME LIKE '%FORTINET%' THEN 'Fortinet'

    -- Data Protection
    WHEN TABLE_NAME LIKE '%VARONIS%' THEN 'Varonis'
    WHEN TABLE_NAME LIKE '%NETSKOPE%' THEN 'Netskope'

    ELSE 'Unknown'
END as SERVICE_NAME
```

### Services Catalog

21 pre-configured services in `SERVICE_CATALOG` table:

| Service Name | Category | Tables | Columns |
|-------------|----------|--------|---------|
| SentinelOne | Endpoint Security | 4 | 76 |
| CybelAngel | Threat Intelligence | 3 | 112 |
| Proofpoint | Email Security | 2 | 23 |
| ServiceNow | ITSM | 2 | 36 |
| Leviat | Asset Management | 5 | 146 |
| Tenable | Vulnerability Mgmt | 0 | 0 |
| Qualys | Vulnerability Mgmt | (varies) | (varies) |
| Azure AD | Identity & Access | (varies) | (varies) |
| ... | ... | ... | ... |

**Note**: Table and column counts are examples; actual values updated daily by procedure.

---

## Metadata Repository Schema

### Core Tables

#### 1. TABLE_REGISTRY
Stores metadata for all discovered tables.

```sql
CREATE TABLE TABLE_REGISTRY (
    TABLE_ID NUMBER AUTOINCREMENT,
    SERVICE_NAME VARCHAR(100),          -- Auto-detected service
    DATABASE_NAME VARCHAR(100),         -- DEV_LANDING or DEV_TRANSFORMATION
    SCHEMA_NAME VARCHAR(100),           -- Usually 'SECURITY_ANALYTICS'
    TABLE_NAME VARCHAR(255),
    FULL_TABLE_NAME VARCHAR(500),       -- Fully qualified name
    TABLE_TYPE VARCHAR(50),             -- BASE TABLE, VIEW, etc.
    DATA_LAYER VARCHAR(50),             -- Landing or Transformation
    ROW_COUNT NUMBER,
    BYTES NUMBER,
    LAST_ALTERED TIMESTAMP_LTZ,
    CREATED_DATE TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    LAST_UPDATED TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (TABLE_ID)
);
```

**Current Stats**: 180 tables cataloged

#### 2. COLUMN_METADATA
Stores column-level metadata for all tables.

```sql
CREATE TABLE COLUMN_METADATA (
    COLUMN_ID NUMBER AUTOINCREMENT,
    TABLE_ID NUMBER,                    -- FK to TABLE_REGISTRY
    SERVICE_NAME VARCHAR(100),
    TABLE_NAME VARCHAR(255),
    COLUMN_NAME VARCHAR(255),
    ORDINAL_POSITION NUMBER,
    DATA_TYPE VARCHAR(100),
    IS_NULLABLE VARCHAR(3),
    CHARACTER_MAXIMUM_LENGTH NUMBER,
    NUMERIC_PRECISION NUMBER,
    NUMERIC_SCALE NUMBER,
    CREATED_DATE TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    LAST_UPDATED TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (COLUMN_ID),
    FOREIGN KEY (TABLE_ID) REFERENCES TABLE_REGISTRY(TABLE_ID)
);
```

**Current Stats**: 2,206 columns cataloged

#### 3. TABLE_STATISTICS
Aggregated statistics per table.

```sql
CREATE TABLE TABLE_STATISTICS (
    STAT_ID NUMBER AUTOINCREMENT,
    TABLE_ID NUMBER,
    SERVICE_NAME VARCHAR(100),
    TABLE_NAME VARCHAR(255),
    COLUMN_COUNT NUMBER,
    ROW_COUNT NUMBER,
    TOTAL_SIZE_MB NUMBER,
    LAST_ANALYZED TIMESTAMP_LTZ,
    PRIMARY KEY (STAT_ID),
    FOREIGN KEY (TABLE_ID) REFERENCES TABLE_REGISTRY(TABLE_ID)
);
```

#### 4. SERVICE_CATALOG
Master list of all security services.

```sql
CREATE TABLE SERVICE_CATALOG (
    SERVICE_ID NUMBER AUTOINCREMENT,
    SERVICE_NAME VARCHAR(100) UNIQUE,
    SERVICE_CATEGORY VARCHAR(100),      -- e.g., "Endpoint Security"
    DESCRIPTION VARCHAR(500),
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    CREATED_DATE TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (SERVICE_ID)
);
```

**Current Stats**: 21 services defined

#### 5. PROCEDURE_EXECUTION_LOG
Audit trail of all metadata refresh executions.

```sql
CREATE TABLE PROCEDURE_EXECUTION_LOG (
    EXECUTION_ID NUMBER AUTOINCREMENT,
    PROCEDURE_NAME VARCHAR(255),
    EXECUTION_START TIMESTAMP_LTZ,
    EXECUTION_END TIMESTAMP_LTZ,
    STATUS VARCHAR(50),                 -- SUCCESS, FAILED, RUNNING
    ERROR_MESSAGE VARCHAR(5000),
    TABLES_PROCESSED NUMBER,
    COLUMNS_PROCESSED NUMBER,
    ROWS_PROCESSED NUMBER,
    EXECUTION_DURATION_SECONDS NUMBER,
    PRIMARY KEY (EXECUTION_ID)
);
```

#### 6. DATA_QUALITY_RULES
Validation rules for data quality checks.

```sql
CREATE TABLE DATA_QUALITY_RULES (
    RULE_ID NUMBER AUTOINCREMENT,
    SERVICE_NAME VARCHAR(100),
    TABLE_NAME VARCHAR(255),
    RULE_TYPE VARCHAR(100),             -- NOT_NULL, UNIQUE, RANGE, etc.
    RULE_DEFINITION VARCHAR(5000),
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    CREATED_DATE TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (RULE_ID)
);
```

### Convenience Views

#### VW_TABLE_CATALOG
Complete table catalog with service information.

```sql
CREATE OR REPLACE VIEW VW_TABLE_CATALOG AS
SELECT
    tr.SERVICE_NAME,
    sc.SERVICE_CATEGORY,
    tr.DATABASE_NAME,
    tr.SCHEMA_NAME,
    tr.TABLE_NAME,
    tr.FULL_TABLE_NAME,
    tr.DATA_LAYER,
    ts.COLUMN_COUNT,
    tr.ROW_COUNT,
    ROUND(tr.BYTES / 1024 / 1024, 2) as SIZE_MB,
    tr.LAST_ALTERED
FROM TABLE_REGISTRY tr
JOIN SERVICE_CATALOG sc ON tr.SERVICE_NAME = sc.SERVICE_NAME
LEFT JOIN TABLE_STATISTICS ts ON tr.TABLE_ID = ts.TABLE_ID
ORDER BY tr.SERVICE_NAME, tr.TABLE_NAME;
```

#### VW_COLUMN_CATALOG
Complete column catalog with table context.

```sql
CREATE OR REPLACE VIEW VW_COLUMN_CATALOG AS
SELECT
    cm.SERVICE_NAME,
    cm.TABLE_NAME,
    tr.FULL_TABLE_NAME,
    cm.COLUMN_NAME,
    cm.DATA_TYPE,
    cm.IS_NULLABLE,
    cm.ORDINAL_POSITION
FROM COLUMN_METADATA cm
JOIN TABLE_REGISTRY tr ON cm.TABLE_ID = tr.TABLE_ID
ORDER BY cm.SERVICE_NAME, cm.TABLE_NAME, cm.ORDINAL_POSITION;
```

#### VW_SERVICE_SUMMARY
Service-level summary statistics.

```sql
CREATE OR REPLACE VIEW VW_SERVICE_SUMMARY AS
SELECT
    tr.SERVICE_NAME,
    sc.SERVICE_CATEGORY,
    COUNT(DISTINCT tr.TABLE_ID) as TABLE_COUNT,
    COUNT(DISTINCT cm.COLUMN_ID) as COLUMN_COUNT,
    SUM(tr.ROW_COUNT) as TOTAL_ROWS,
    ROUND(SUM(tr.BYTES) / 1024 / 1024, 2) as TOTAL_SIZE_MB
FROM TABLE_REGISTRY tr
JOIN SERVICE_CATALOG sc ON tr.SERVICE_NAME = sc.SERVICE_NAME
LEFT JOIN COLUMN_METADATA cm ON tr.TABLE_ID = cm.TABLE_ID
GROUP BY tr.SERVICE_NAME, sc.SERVICE_CATEGORY
ORDER BY TABLE_COUNT DESC;
```

---

## Scheduled Automation

### TASK_DAILY_METADATA_REFRESH

Snowflake Task that executes SP_REFRESH_METADATA on a daily schedule.

#### Task Configuration

```sql
CREATE OR REPLACE TASK TASK_DAILY_METADATA_REFRESH
    WAREHOUSE = 'DEV_WH'
    SCHEDULE = 'USING CRON 0 2 * * * America/New_York'  -- 2:00 AM UTC = 6:00 AM EST
    COMMENT = 'Daily metadata refresh - extracts and updates metadata for all SECURITY_ANALYTICS tables'
AS
    CALL SP_REFRESH_METADATA();
```

#### Task Details

| Property | Value |
|----------|-------|
| Name | TASK_DAILY_METADATA_REFRESH |
| Database | DEV_TRANSFORMATION |
| Schema | METADATA |
| Warehouse | DEV_WH |
| Schedule | Daily at 6:00 AM EST |
| Owner | DEV_DEVELOPER role |
| State | Started (after privilege grant) |

#### Task Privileges Required

```sql
-- Must be executed by ACCOUNTADMIN
USE ROLE ACCOUNTADMIN;

GRANT EXECUTE TASK ON ACCOUNT TO ROLE DEV_DEVELOPER;
GRANT EXECUTE MANAGED TASK ON ACCOUNT TO ROLE DEV_DEVELOPER;

-- Then activate task
USE ROLE DEV_DEVELOPER;
ALTER TASK TASK_DAILY_METADATA_REFRESH RESUME;
```

#### Task Management Commands

```sql
-- Check task status
SHOW TASKS LIKE 'TASK_DAILY_METADATA_REFRESH';

-- Activate task
ALTER TASK TASK_DAILY_METADATA_REFRESH RESUME;

-- Suspend task
ALTER TASK TASK_DAILY_METADATA_REFRESH SUSPEND;

-- View task execution history
SELECT *
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    TASK_NAME => 'TASK_DAILY_METADATA_REFRESH'
))
ORDER BY SCHEDULED_TIME DESC
LIMIT 10;

-- View procedure execution log
SELECT
    EXECUTION_START,
    STATUS,
    TABLES_PROCESSED,
    COLUMNS_PROCESSED,
    EXECUTION_DURATION_SECONDS,
    ERROR_MESSAGE
FROM PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 10;
```

---

## Export Process

### EXPORT_METADATA_RESULTS.sql

After metadata is refreshed, the export script creates **materialized tables** in the `METADATA_EXPORTS` schema for consumption by applications.

#### Export Tables Created

| Export Table | Purpose | Rows |
|-------------|---------|------|
| SERVICE_SUMMARY_EXPORT | Service-level statistics | 21 |
| TABLE_CATALOG_EXPORT | Complete table catalog | 180 |
| ALL_COLUMNS_EXPORT | All columns across services | 2,206 |
| SENTINELONE_COLUMNS_EXPORT | SentinelOne columns only | 76 |
| CYBELANGEL_COLUMNS_EXPORT | CybelAngel columns only | 112 |
| PROOFPOINT_COLUMNS_EXPORT | Proofpoint columns only | 23 |
| SERVICENOW_COLUMNS_EXPORT | ServiceNow columns only | 36 |
| LEVIAT_COLUMNS_EXPORT | Leviat columns only | 146 |
| TENABLE_COLUMNS_EXPORT | Tenable columns only | 0 |
| TABLE_STATISTICS_EXPORT | Table-level statistics | 180 |
| PROCEDURE_EXECUTION_LOG_EXPORT | Execution history | 3+ |
| EXECUTION_STATISTICS_EXPORT | Performance metrics | 1 |
| DAILY_EXECUTION_TREND_EXPORT | Trend analysis | 1 |

#### Execution

```sql
-- Run export process (creates/replaces all export tables)
USE ROLE DEV_DEVELOPER;
USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA METADATA_EXPORTS;

-- Execute EXPORT_METADATA_RESULTS.sql
-- (36 SQL statements executed automatically)
```

#### Python Automation

```bash
# Execute export script with automatic CSV/JSON export
python run_sql_script.py --script 01_SQL_SCRIPTS/EXPORT_METADATA_RESULTS.sql

# Results stored in:
# 04_METADATA_SAMPLES/sql_execution_results/EXPORT_METADATA_RESULTS_YYYYMMDD_HHMMSS/
```

#### Export Schedule

- **Frequency**: Daily (after metadata refresh task completes)
- **Trigger**: Manual execution or additional scheduled task
- **Duration**: ~30 seconds
- **Output**: 13 export tables + CSV/JSON files

---

## Integration with Applications

### Streamlit Apps

**6 services** now have integrated Metadata tabs powered by METADATA_EXPORTS:

1. **SentinelOne** → `SENTINELONE_COLUMNS_EXPORT`
2. **CybelAngel** → `CYBELANGEL_COLUMNS_EXPORT`
3. **Proofpoint** → `PROOFPOINT_COLUMNS_EXPORT`
4. **ServiceNow** → `SERVICENOW_COLUMNS_EXPORT`
5. **Leviat** → `LEVIAT_COLUMNS_EXPORT`
6. **Tenable** → `TENABLE_COLUMNS_EXPORT`

#### Metadata Tab Features

```python
# Example query used by Streamlit apps
metadata_sql = """
    SELECT
        TABLE_NAME,
        COLUMN_NAME,
        DATA_TYPE,
        IS_NULLABLE,
        ORDINAL_POSITION,
        FULL_TABLE_NAME
    FROM DEV_TRANSFORMATION.METADATA_EXPORTS.{SERVICE}_COLUMNS_EXPORT
    ORDER BY TABLE_NAME, ORDINAL_POSITION
"""

# Features provided:
# - Table selector dropdown
# - Column details grid with sorting/filtering
# - Search by column name
# - Data type filtering
# - Export to CSV
# - Copy to clipboard
```

#### User Benefits

- **Self-Service**: Users can browse table structures without SQL knowledge
- **Documentation**: Always up-to-date with daily refresh
- **Discovery**: Easy to find columns across multiple tables
- **Integration**: Seamless experience within existing apps

### Power BI Integration (Planned)

- **Data Catalog Report**: Browse all tables/columns via Power BI
- **Service Dashboard**: Summary cards per security service
- **Column Search**: Full-text search across all metadata
- **Data Lineage**: Visual representation of data flow

---

## Monitoring & Maintenance

### Monitoring Queries

#### Check Latest Execution Status

```sql
SELECT
    EXECUTION_START,
    EXECUTION_END,
    STATUS,
    TABLES_PROCESSED,
    COLUMNS_PROCESSED,
    EXECUTION_DURATION_SECONDS,
    ERROR_MESSAGE
FROM PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 1;
```

#### Execution Trend (Last 7 Days)

```sql
SELECT
    DATE(EXECUTION_START) as EXECUTION_DATE,
    COUNT(*) as EXECUTIONS,
    AVG(EXECUTION_DURATION_SECONDS) as AVG_DURATION,
    SUM(CASE WHEN STATUS = 'SUCCESS' THEN 1 ELSE 0 END) as SUCCESSFUL,
    SUM(CASE WHEN STATUS = 'FAILED' THEN 1 ELSE 0 END) as FAILED
FROM PROCEDURE_EXECUTION_LOG
WHERE EXECUTION_START >= DATEADD(day, -7, CURRENT_DATE())
GROUP BY DATE(EXECUTION_START)
ORDER BY EXECUTION_DATE DESC;
```

#### Service Coverage Check

```sql
-- Services with no tables detected
SELECT
    sc.SERVICE_NAME,
    sc.SERVICE_CATEGORY,
    COALESCE(COUNT(tr.TABLE_ID), 0) as TABLE_COUNT
FROM SERVICE_CATALOG sc
LEFT JOIN TABLE_REGISTRY tr ON sc.SERVICE_NAME = tr.SERVICE_NAME
GROUP BY sc.SERVICE_NAME, sc.SERVICE_CATEGORY
HAVING COUNT(tr.TABLE_ID) = 0
ORDER BY sc.SERVICE_NAME;
```

#### Tables Not Updated Recently

```sql
SELECT
    SERVICE_NAME,
    TABLE_NAME,
    LAST_ALTERED,
    DATEDIFF(day, LAST_ALTERED, CURRENT_DATE()) as DAYS_SINCE_UPDATE
FROM TABLE_REGISTRY
WHERE LAST_ALTERED < DATEADD(day, -30, CURRENT_DATE())
ORDER BY LAST_ALTERED;
```

### Maintenance Tasks

#### Weekly Review
- Check PROCEDURE_EXECUTION_LOG for failures
- Review services with 0 tables (may need pattern updates)
- Validate export table row counts

#### Monthly Review
- Update SERVICE_CATALOG with new services
- Review and optimize service detection patterns
- Archive old execution logs (if needed)

#### Ad-Hoc Maintenance

```sql
-- Manually refresh metadata
CALL SP_REFRESH_METADATA();

-- Re-run exports
-- Execute EXPORT_METADATA_RESULTS.sql

-- Add new service to catalog
INSERT INTO SERVICE_CATALOG (SERVICE_NAME, SERVICE_CATEGORY, DESCRIPTION)
VALUES ('NewService', 'Category', 'Description');

-- Update service detection pattern (requires procedure recreation)
-- Edit CREATE_STORED_PROCEDURE_ONLY.sql and re-deploy
```

---

## Deployment Guide

### Initial Setup (One-Time)

#### Step 1: Create Metadata Repository

```bash
# Execute in Snowflake UI (due to stored procedure with dollar-quotes)
# File: 01_SQL_SCRIPTS/CREATE_METADATA_REPOSITORY.sql
```

This creates:
- `METADATA` schema with 6 tables, 3 views
- `METADATA_EXPORTS` schema (empty until exports run)
- `SP_REFRESH_METADATA()` stored procedure
- `TASK_DAILY_METADATA_REFRESH` task (suspended)

#### Step 2: Grant Task Privileges

```bash
# Must be executed by user with ACCOUNTADMIN role
# File: 01_SQL_SCRIPTS/GRANT_TASK_PRIVILEGES.sql
```

```sql
USE ROLE ACCOUNTADMIN;
GRANT EXECUTE TASK ON ACCOUNT TO ROLE DEV_DEVELOPER;
GRANT EXECUTE MANAGED TASK ON ACCOUNT TO ROLE DEV_DEVELOPER;
```

#### Step 3: Activate Daily Task

```bash
# Option A: Python script
python activate_metadata_task.py

# Option B: SQL command
USE ROLE DEV_DEVELOPER;
ALTER TASK TASK_DAILY_METADATA_REFRESH RESUME;
```

#### Step 4: Initial Metadata Refresh

```sql
-- Run manually to populate metadata immediately
CALL SP_REFRESH_METADATA();
```

#### Step 5: Create Export Tables

```bash
# Execute export script
python run_sql_script.py --script 01_SQL_SCRIPTS/EXPORT_METADATA_RESULTS.sql
```

#### Step 6: Verify Deployment

```bash
# Run comprehensive verification
python run_verification_script.py --script 01_SQL_SCRIPTS/VERIFY_PROCEDURE_RECREATION.sql

# Check results in:
# 04_METADATA_SAMPLES/verification_results/VERIFY_PROCEDURE_RECREATION_*/
```

Expected: 24/24 checks passed

### Updates and Changes

#### Updating Service Detection Patterns

1. Edit [CREATE_STORED_PROCEDURE_ONLY.sql](01_SQL_SCRIPTS/CREATE_STORED_PROCEDURE_ONLY.sql)
2. Locate the service detection CASE statement
3. Add new pattern:
   ```sql
   WHEN TABLE_NAME LIKE '%NEWSERVICE%' THEN 'NewServiceName'
   ```
4. Execute script in Snowflake UI
5. Run manual refresh: `CALL SP_REFRESH_METADATA();`

#### Adding New Services to Catalog

```sql
INSERT INTO SERVICE_CATALOG (SERVICE_NAME, SERVICE_CATEGORY, DESCRIPTION)
VALUES
    ('NewService1', 'Security Category', 'Description of service'),
    ('NewService2', 'Another Category', 'Description of service');
```

#### Creating New Export Tables

Edit [EXPORT_METADATA_RESULTS.sql](01_SQL_SCRIPTS/EXPORT_METADATA_RESULTS.sql) and add:

```sql
-- Export for new service
CREATE OR REPLACE TABLE METADATA_EXPORTS.NEWSERVICE_COLUMNS_EXPORT AS
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    FULL_TABLE_NAME
FROM VW_COLUMN_CATALOG
WHERE SERVICE_NAME = 'NewServiceName'
ORDER BY TABLE_NAME, ORDINAL_POSITION;
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Task Won't Start

**Error**: `Cannot execute task, EXECUTE TASK privilege must be granted to owner role`

**Solution**:
```sql
-- Execute with ACCOUNTADMIN role
USE ROLE ACCOUNTADMIN;
GRANT EXECUTE TASK ON ACCOUNT TO ROLE DEV_DEVELOPER;
GRANT EXECUTE MANAGED TASK ON ACCOUNT TO ROLE DEV_DEVELOPER;

-- Then activate
USE ROLE DEV_DEVELOPER;
ALTER TASK TASK_DAILY_METADATA_REFRESH RESUME;
```

#### Issue 2: No Tables Detected for Service

**Symptom**: Service has 0 tables in TABLE_REGISTRY

**Diagnosis**:
```sql
-- Check if tables exist
SELECT TABLE_NAME
FROM DEV_LANDING.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND TABLE_NAME LIKE '%SERVICEPATTERN%';
```

**Solution**: Update service detection pattern in CREATE_STORED_PROCEDURE_ONLY.sql

#### Issue 3: Procedure Execution Fails

**Diagnosis**:
```sql
SELECT *
FROM PROCEDURE_EXECUTION_LOG
WHERE STATUS = 'FAILED'
ORDER BY EXECUTION_START DESC
LIMIT 5;
```

**Common Causes**:
- Schema permissions changed
- Tables dropped or renamed
- Warehouse suspended/resized

**Solution**: Check ERROR_MESSAGE column for specific error details

#### Issue 4: Export Tables Empty

**Symptom**: Export tables created but have 0 rows

**Diagnosis**:
```sql
-- Check if metadata repository has data
SELECT COUNT(*) FROM TABLE_REGISTRY;
SELECT COUNT(*) FROM COLUMN_METADATA;
```

**Solution**:
1. Run `CALL SP_REFRESH_METADATA();` first
2. Then run EXPORT_METADATA_RESULTS.sql

#### Issue 5: Outdated Metadata in Streamlit Apps

**Symptom**: Apps showing old table structures

**Solution**:
```sql
-- Check last export update
SELECT TABLE_NAME, CREATED_DATE
FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'METADATA_EXPORTS'
ORDER BY CREATED_DATE DESC;

-- If outdated, re-run export
-- Execute: EXPORT_METADATA_RESULTS.sql
```

### Support Contacts

| Area | Contact |
|------|---------|
| Snowflake Administration | IT Data Engineering Team |
| Metadata Issues | Data Warehouse Team |
| Streamlit App Integration | Analytics Team |
| Task Scheduling | DevOps Team |

---

## Appendix

### File Locations

```
Project Root: C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV

SQL Scripts:
├── 01_SQL_SCRIPTS/
│   ├── CREATE_METADATA_REPOSITORY.sql          (Complete setup)
│   ├── CREATE_STORED_PROCEDURE_ONLY.sql        (Procedure only)
│   ├── VERIFY_PROCEDURE_RECREATION.sql         (Verification)
│   ├── EXPORT_METADATA_RESULTS.sql             (Export creation)
│   └── GRANT_TASK_PRIVILEGES.sql               (Privilege grants)

Python Scripts:
├── run_sql_script.py                           (Execute SQL with exports)
├── run_verification_script.py                  (Run verification checks)
└── activate_metadata_task.py                   (Activate scheduled task)

Configuration:
└── snowflake_config.json                       (Connection settings)

Results:
├── 04_METADATA_SAMPLES/
│   ├── sql_execution_results/                  (Export executions)
│   └── verification_results/                   (Verification results)
```

### Related Documentation

- [WIKI_01_STREAMLIT_APPS.md](WIKI_01_STREAMLIT_APPS.md) - Streamlit application catalog
- [WIKI_02_POWER_BI.md](WIKI_02_POWER_BI.md) - Power BI implementation plan
- [METADATA_REPOSITORY_COMPLETE_GUIDE.md](METADATA_REPOSITORY_COMPLETE_GUIDE.md) - Technical deep dive

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-24 | Initial deployment with 180 tables, 2,206 columns |

---

**Document Status**: Production Release v1.0
**Last Updated**: 2025-10-24
**Author**: GenericCorp Data Engineering Team
**Maintained By**: IT Data Warehouse Team
