# SECURITY_ANALYTICS Metadata Repository Guide

## Overview

The Metadata Repository is a centralized system for managing and documenting all data structures in the SECURITY_ANALYTICS Data Warehouse project. It serves as a single source of truth for:

- Table structures and column definitions
- Data statistics and quality metrics
- Service catalogs and documentation
- Historical data trends
- Automated metadata refresh

**Created:** 2025-10-24
**Location:** `DEV_TRANSFORMATION.METADATA`

---

## Architecture

### Schema Structure

```
DEV_TRANSFORMATION.METADATA/
├── Tables
│   ├── TABLE_REGISTRY          # Master table registry
│   ├── COLUMN_METADATA          # Column-level metadata
│   ├── TABLE_STATISTICS         # Historical statistics
│   ├── SERVICE_CATALOG          # Service/source catalog
│   └── DATA_QUALITY_RULES       # Data quality rules
├── Views
│   ├── VW_TABLE_CATALOG         # User-friendly table view
│   ├── VW_COLUMN_CATALOG        # Complete column catalog
│   └── VW_SERVICE_SUMMARY       # Service summary stats
├── Stored Procedures
│   └── SP_REFRESH_METADATA()    # Metadata refresh procedure
└── Tasks
    └── TASK_DAILY_METADATA_REFRESH  # Daily automation
```

---

## Quick Start

### 1. Initial Setup

```sql
-- Execute the setup script
USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;

-- Run the complete setup
@01_SQL_SCRIPTS/CREATE_METADATA_REPOSITORY.sql
```

This will:
- ✅ Create all tables and views
- ✅ Populate service catalog
- ✅ Load initial metadata
- ✅ Set up daily refresh task

### 2. Verify Installation

```sql
-- Check service summary
SELECT * FROM DEV_TRANSFORMATION.METADATA.VW_SERVICE_SUMMARY;

-- Check table count
SELECT SERVICE_NAME, COUNT(*) as TABLES
FROM DEV_TRANSFORMATION.METADATA.VW_TABLE_CATALOG
GROUP BY SERVICE_NAME;

-- Check column count
SELECT COUNT(*) as TOTAL_COLUMNS
FROM DEV_TRANSFORMATION.METADATA.COLUMN_METADATA;
```

Expected results:
- 5-6 services (SentinelOne, CybelAngel, Proofpoint, ServiceNow, Leviat, Tenable)
- 20-30 tables
- 200-300 columns

---

## Common Use Cases

### Use Case 1: Building a Streamlit App

**Goal:** Get all columns for a table to build SQL queries

```sql
-- Get columns for SentinelOne endpoints
SELECT
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION
FROM DEV_TRANSFORMATION.METADATA.VW_COLUMN_CATALOG
WHERE SERVICE_NAME = 'SentinelOne'
  AND TABLE_NAME = 'FACT_SENTINEL_ENDPOINTS'
ORDER BY ORDINAL_POSITION;
```

**Result:** List of 12 columns with types (ENDPOINT_NAME, IP_ADDRESS, LAST_ACTIVE, etc.)

**Use in Streamlit:**
```python
# Now you know the exact column names
query = """
SELECT
    ENDPOINT_NAME,
    IP_ADDRESS,
    LAST_ACTIVE,
    AGENT_VERSION,
    DOMAIN
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_SENTINEL_ENDPOINTS
WHERE LAST_ACTIVE >= DATEADD(day, -30, CURRENT_DATE())
ORDER BY LAST_ACTIVE DESC
LIMIT 100
"""
```

---

### Use Case 2: Generate SELECT Statement

**Goal:** Auto-generate column list for SELECT

```sql
SELECT LISTAGG('    ' || COLUMN_NAME, ',\n')
       WITHIN GROUP (ORDER BY ORDINAL_POSITION) as COLUMN_LIST
FROM DEV_TRANSFORMATION.METADATA.VW_COLUMN_CATALOG
WHERE TABLE_NAME = 'PROOFPOINT_MESSAGE_LOGS';
```

**Result:** Copy-paste ready column list

---

### Use Case 3: Data Quality Monitoring

**Goal:** Find tables that haven't been updated recently

```sql
SELECT
    SERVICE_NAME,
    TABLE_NAME,
    ROW_COUNT,
    LAST_UPDATED,
    DATEDIFF(day, LAST_UPDATED, CURRENT_TIMESTAMP()) as DAYS_STALE
FROM DEV_TRANSFORMATION.METADATA.VW_TABLE_CATALOG
WHERE IS_ACTIVE = TRUE
  AND DATEDIFF(day, LAST_UPDATED, CURRENT_TIMESTAMP()) > 7
ORDER BY DAYS_STALE DESC;
```

**Result:** List of stale tables requiring attention

---

### Use Case 4: Find Empty Tables

**Goal:** Identify tables with no data

```sql
SELECT
    SERVICE_NAME,
    TABLE_NAME,
    DATA_LAYER,
    COLUMN_COUNT
FROM DEV_TRANSFORMATION.METADATA.VW_TABLE_CATALOG
WHERE ROW_COUNT = 0 OR ROW_COUNT IS NULL
ORDER BY SERVICE_NAME, TABLE_NAME;
```

**Result:** Tables like Leviat (0 rows) and Tenable (no tables)

---

### Use Case 5: Service Overview

**Goal:** Get complete overview of all services

```sql
SELECT
    SERVICE_NAME,
    SERVICE_CATEGORY,
    TABLE_COUNT,
    TOTAL_ROWS,
    TOTAL_COLUMNS,
    REFRESH_FREQUENCY
FROM DEV_TRANSFORMATION.METADATA.VW_SERVICE_SUMMARY
ORDER BY TOTAL_ROWS DESC;
```

**Result:** Summary showing Proofpoint (206K rows), ServiceNow (24K rows), etc.

---

## Automated Refresh

### Daily Task

The metadata repository automatically refreshes every day at 2 AM UTC.

**Check task status:**
```sql
SHOW TASKS LIKE 'TASK_DAILY_METADATA_REFRESH';
```

**Activate task (if suspended):**
```sql
ALTER TASK DEV_TRANSFORMATION.METADATA.TASK_DAILY_METADATA_REFRESH RESUME;
```

**Suspend task:**
```sql
ALTER TASK DEV_TRANSFORMATION.METADATA.TASK_DAILY_METADATA_REFRESH SUSPEND;
```

**View task history:**
```sql
SELECT *
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    TASK_NAME => 'TASK_DAILY_METADATA_REFRESH',
    SCHEMA_NAME => 'METADATA'
))
ORDER BY SCHEDULED_TIME DESC
LIMIT 10;
```

### Manual Refresh

**Refresh metadata on-demand:**
```sql
CALL DEV_TRANSFORMATION.METADATA.SP_REFRESH_METADATA();
```

**Result:** Returns message with number of tables and columns processed

---

## Integration with Streamlit Apps

### Best Practices

1. **Query metadata at app startup** to get current column list
2. **Use exact column names** from metadata (case-sensitive)
3. **Filter by DATA_TYPE** to build appropriate filters/charts
4. **Check ROW_COUNT** before querying large tables

### Example: Dynamic Streamlit App

```python
import streamlit as st
from snowflake.snowpark.context import get_active_session

session = get_active_session()

# Get columns dynamically from metadata
metadata_query = """
SELECT COLUMN_NAME, DATA_TYPE
FROM DEV_TRANSFORMATION.METADATA.VW_COLUMN_CATALOG
WHERE SERVICE_NAME = 'ServiceNow'
  AND TABLE_NAME = 'SNOW'
ORDER BY ORDINAL_POSITION
"""

columns_df = session.sql(metadata_query).to_pandas()

# Build SELECT statement dynamically
column_list = ', '.join(columns_df['COLUMN_NAME'].tolist())

data_query = f"""
SELECT {column_list}
FROM DEV_LANDING.SECURITY_ANALYTICS.SNOW
LIMIT 100
"""

data = session.sql(data_query).to_pandas()
st.dataframe(data)
```

---

## Maintenance

### Regular Tasks

**Weekly:**
- Review stale tables query
- Check for empty tables
- Verify task execution history

**Monthly:**
- Review table statistics trends
- Update service descriptions
- Audit data quality rules

**Quarterly:**
- Archive old statistics
- Review and update documentation
- Performance optimization

### Troubleshooting

**Issue: Metadata not updating**
```sql
-- Check task status
SHOW TASKS LIKE 'TASK_DAILY_METADATA_REFRESH';

-- Check task history for errors
SELECT ERROR_MESSAGE
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE NAME = 'TASK_DAILY_METADATA_REFRESH'
  AND STATE = 'FAILED'
ORDER BY SCHEDULED_TIME DESC;

-- Manual refresh
CALL SP_REFRESH_METADATA();
```

**Issue: Missing tables**
```sql
-- Verify tables exist in INFORMATION_SCHEMA
SELECT TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME
FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND TABLE_NAME LIKE '%SENTINEL%';

-- If tables exist but not in metadata, refresh
CALL SP_REFRESH_METADATA();
```

**Issue: Incorrect row counts**
```sql
-- Row counts come from INFORMATION_SCHEMA
-- May be outdated, run table maintenance:
-- ALTER TABLE <table_name> RECALCULATE STATISTICS;
```

---

## Advanced Features

### Data Quality Rules (Future Enhancement)

The `DATA_QUALITY_RULES` table is designed for automated data quality monitoring:

```sql
-- Example: Add rule for null checks
INSERT INTO DATA_QUALITY_RULES (
    TABLE_ID,
    RULE_NAME,
    RULE_TYPE,
    RULE_EXPRESSION,
    SEVERITY
)
SELECT
    TABLE_ID,
    'No null IP addresses',
    'NOT_NULL',
    'IP_ADDRESS IS NOT NULL',
    'Critical'
FROM TABLE_REGISTRY
WHERE TABLE_NAME = 'FACT_SENTINEL_ENDPOINTS';
```

### Historical Trends

```sql
-- View row count trends over time
SELECT
    tr.TABLE_NAME,
    ts.SNAPSHOT_DATE,
    ts.ROW_COUNT,
    ts.ROW_COUNT - LAG(ts.ROW_COUNT) OVER (
        PARTITION BY tr.TABLE_NAME
        ORDER BY ts.SNAPSHOT_DATE
    ) as DAILY_CHANGE
FROM TABLE_STATISTICS ts
JOIN TABLE_REGISTRY tr ON ts.TABLE_ID = tr.TABLE_ID
WHERE tr.SERVICE_NAME = 'Proofpoint'
ORDER BY ts.SNAPSHOT_DATE DESC;
```

---

## API Reference

### Tables

#### TABLE_REGISTRY
Master registry of all tables
- **Primary Key:** TABLE_ID
- **Unique Key:** (DATABASE_NAME, SCHEMA_NAME, TABLE_NAME)
- **Key Columns:** SERVICE_NAME, TABLE_NAME, ROW_COUNT, LAST_UPDATED

#### COLUMN_METADATA
Column-level metadata for all tables
- **Primary Key:** COLUMN_ID
- **Foreign Key:** TABLE_ID → TABLE_REGISTRY
- **Key Columns:** COLUMN_NAME, DATA_TYPE, ORDINAL_POSITION

#### SERVICE_CATALOG
Catalog of all data services
- **Primary Key:** SERVICE_ID
- **Unique Key:** SERVICE_NAME
- **Key Columns:** SERVICE_CATEGORY, REFRESH_FREQUENCY, IS_ACTIVE

### Views

#### VW_TABLE_CATALOG
Complete table catalog with statistics
- **Includes:** Service info, row counts, column counts, last update
- **Use for:** Building app table lists, monitoring data freshness

#### VW_COLUMN_CATALOG
Complete column catalog with table context
- **Includes:** Full column details with service/table context
- **Use for:** Building SQL queries, app development

#### VW_SERVICE_SUMMARY
Summary statistics by service
- **Includes:** Table count, total rows, total columns per service
- **Use for:** Service overview dashboards

### Stored Procedures

#### SP_REFRESH_METADATA()
Refreshes all metadata from INFORMATION_SCHEMA
- **Returns:** Success message with counts
- **Schedule:** Daily at 2 AM UTC (via task)
- **Manual execution:** `CALL SP_REFRESH_METADATA();`

---

## Files Reference

| File | Purpose | Location |
|------|---------|----------|
| CREATE_METADATA_REPOSITORY.sql | Setup script | 01_SQL_SCRIPTS/ |
| QUERY_METADATA_REPOSITORY.sql | Helper queries | 01_SQL_SCRIPTS/ |
| METADATA_REPOSITORY_GUIDE.md | This guide | 04_METADATA_SAMPLES/ |
| all_services_columns.json | Exported metadata | 04_METADATA_SAMPLES/json/ |

---

## Support

**Questions?** Contact GenericCorp Data Engineering Team

**Issues?** Create ticket in Azure DevOps

**Enhancements?** Submit PR with proposed changes

---

**Last Updated:** 2025-10-24
**Version:** 1.0
**Maintained By:** GenericCorp Data Engineering Team
