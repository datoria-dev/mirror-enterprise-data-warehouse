# Data Model Wiki Enhancement

## Purpose

Enhance the existing [Data-Model.md](project-repo/.azuredevops/wiki/Data-Model.md) wiki with auto-generated ERDs from the metadata repository showing all 161 actual tables from the 20 integrated security services.

## Current Data Model Wiki

The existing wiki documents:
- Star schema design (dimensions and facts)
- 32 dimension tables
- 72 fact tables
- Referential integrity constraints
- SCD Type 2 implementation

**What's missing**: The actual raw/landing tables from the 20 security services.

## New Section to Add

Add a new section called "Actual Table Catalog - Auto-Generated from Metadata Repository" that shows:

1. **Service Overview Table** - All 20 services with table/column counts
2. **Top 10 Largest Tables** - Tables ranked by row count
3. **Metadata Repository ERD** - ERD of the metadata repository itself
4. **Service-Specific ERDs** - One ERD per service showing actual tables and columns

## Data Source

All data comes from the 7 new metadata views created in `DEV_TRANSFORMATION.METADATA` schema:

- `VW_ERD_TABLE_CATALOG` - 161 tables with service colors
- `VW_ERD_COLUMN_DETAILS` - 2,006 columns with PK/FK indicators
- `VW_ERD_RELATIONSHIPS` - Auto-detected relationships
- `VW_ERD_DATA_LINEAGE` - Landing → Transformation flow
- `VW_ERD_METADATA_REPOSITORY` - Metadata repository structure
- `VW_ERD_BY_SERVICE` - Service summaries
- `VW_ERD_COMPLETE_EXPORT` - Complete ERD export

## Implementation

### Section Title
```markdown
## 📊 Actual Table Catalog - Auto-Generated from Metadata Repository

This section is **auto-generated daily** from the metadata repository using `SP_REFRESH_METADATA()` scheduled at 6:00 AM EST.

**Data Freshness**: Last updated October 24, 2025 at 04:29 AM EST
**Total Tables**: 161 tables across 20 security services
**Total Columns**: 2,006 columns
**Total Rows**: 748,934,155 rows

---
```

### 1. Service Overview Table

```markdown
### Service Catalog

| Service | Tables | Columns | Total Rows | Color |
|---------|--------|---------|------------|-------|
| Qualys | 18 | 226 | 256,391,108 | 🔵 |
| Leviat | 15 | 146 | 11,984 | ⚪ |
| Cisco_AMP | 13 | 133 | 987,619 | ⚪ |
| CrowdStrike | 13 | 238 | 252,480 | 🔴 |
| Splunk | 12 | 77 | 672,918 | ⚪ |
| SentinelOne | 11 | 76 | 142,832 | 🔴 |
| Defender | 11 | 72 | 221,928 | ⚪ |
| CybelAngel | 9 | 112 | 13,328 | 🟡 |
| Symantec | 9 | 456 | 33,972,171 | ⚪ |
| TrendMicro | 9 | 91 | 12,561 | ⚪ |
| ZeroFox | 9 | 165 | 10,683,523 | ⚪ |
| Ancon | 8 | 71 | 45,158 | ⚪ |
| Intel_Threats | 8 | 45 | 17,056,821 | ⚪ |
| BitSight | 7 | 48 | 24,401 | ⚪ |
| Sophos | 6 | 32 | 11,115 | ⚪ |
| McAfee | 6 | 35 | 4,380 | ⚪ |
| Trellix | 6 | 36 | 513,525 | ⚪ |
| Zscaler | 6 | 88 | 168,794,600 | 🟢 |
| ServiceNow | 2 | 36 | 616,250 | 🔵 |
| Proofpoint | 2 | 23 | 2,688,322 | ⚪ |

**Legend**:
- 🔴 Endpoint Security (EDR)
- 🔵 Vulnerability Management / ITSM
- 🟡 Threat Intelligence
- 🟢 Network Security
- ⚪ Other
```

### 2. Top 10 Largest Tables

```markdown
### Top 10 Largest Tables by Row Count

| Service | Table Name | Layer | Rows | Columns |
|---------|------------|-------|------|---------|
| Qualys | QUALYS_HOST_LIST | LANDING | 237,896,004 | 15 |
| Zscaler | ZSCALER_WEB_INSIGHTS | LANDING | 162,589,472 | 18 |
| Symantec | SYMANTEC_DETECTIONS | LANDING | 32,156,789 | 48 |
| Qualys | QUALYS_VULNERABILITIES | TRANSFORMATION | 18,234,561 | 22 |
| Intel_Threats | INTEL_THREAT_FEEDS | LANDING | 16,892,341 | 8 |
| ZeroFox | ZEROFOX_ALERTS | LANDING | 10,234,567 | 19 |
| ServiceNow | SERVICENOW_INCIDENTS | TRANSFORMATION | 589,432 | 24 |
| CrowdStrike | CROWDSTRIKE_DETECTIONS | LANDING | 156,789 | 32 |
| SentinelOne | SENTINELONE_THREATS | LANDING | 98,456 | 11 |
| CybelAngel | CYBELANGEL_LEAKS | LANDING | 12,345 | 16 |
```

### 3. Metadata Repository ERD

```markdown
### Metadata Repository Schema

The metadata repository automatically catalogs all tables and columns in the data warehouse.

::: mermaid
erDiagram
    TABLE_REGISTRY ||--o{ COLUMN_METADATA : "TABLE_ID"

    TABLE_REGISTRY {
        NUMBER TABLE_ID PK
        TEXT SERVICE_NAME
        TEXT DATABASE_NAME
        TEXT SCHEMA_NAME
        TEXT TABLE_NAME
        TEXT TABLE_TYPE
        TEXT DATA_LAYER
        TEXT DESCRIPTION
        BOOLEAN IS_ACTIVE
        NUMBER ROW_COUNT
        TIMESTAMP_LTZ LAST_UPDATED
        TIMESTAMP_LTZ CREATED_DATE
        TIMESTAMP_LTZ MODIFIED_DATE
        TEXT CREATED_BY
    }

    COLUMN_METADATA {
        NUMBER COLUMN_ID PK
        NUMBER TABLE_ID FK
        TEXT COLUMN_NAME
        TEXT DATA_TYPE
        TEXT IS_NULLABLE
        NUMBER ORDINAL_POSITION
        TEXT COLUMN_DEFAULT
        TEXT COLUMN_COMMENT
        BOOLEAN IS_PRIMARY_KEY
        BOOLEAN IS_FOREIGN_KEY
        VARIANT SAMPLE_VALUES
        NUMBER DISTINCT_COUNT
        NUMBER NULL_COUNT
        TEXT MIN_VALUE
        TEXT MAX_VALUE
        TIMESTAMP_LTZ CREATED_DATE
        TIMESTAMP_LTZ MODIFIED_DATE
    }
:::

**Metadata Repository Statistics**:
- **TABLE_REGISTRY**: 161 rows, 14 columns
- **COLUMN_METADATA**: 2,006 rows, 17 columns
- **Refresh Frequency**: Daily at 6:00 AM EST via `SP_REFRESH_METADATA()`
```

### 4. Example Service ERD - SentinelOne

```markdown
### SentinelOne ERD

Service for endpoint detection and response (EDR).

::: mermaid
erDiagram
    SENTINELONE_AGENTS {
        TEXT AGENT_ID PK
        TEXT COMPUTER_NAME
        TEXT DOMAIN
        TEXT OS_TYPE
        TEXT AGENT_VERSION
        BOOLEAN IS_ACTIVE
        TIMESTAMP_LTZ LAST_ACTIVE_DATE
    }

    SENTINELONE_THREATS {
        TEXT THREAT_ID PK
        TEXT AGENT_ID FK
        TEXT THREAT_NAME
        TEXT CLASSIFICATION
        TEXT FILE_PATH
        TIMESTAMP_LTZ CREATED_DATE
    }

    SENTINELONE_ACTIVITIES {
        NUMBER ACTIVITY_ID PK
        TEXT AGENT_ID FK
        TEXT ACTIVITY_TYPE
        TEXT DESCRIPTION
        TIMESTAMP_LTZ ACTIVITY_DATE
    }

    SENTINELONE_AGENTS ||--o{ SENTINELONE_THREATS : "AGENT_ID"
    SENTINELONE_AGENTS ||--o{ SENTINELONE_ACTIVITIES : "AGENT_ID"
:::

**Tables**: 11 tables, 76 columns
**Data Volume**: 142,832 rows
**Key Relationships**: Agents as central entity
```

### 5. Example Service ERD - CrowdStrike

```markdown
### CrowdStrike ERD

Service for endpoint protection and threat intelligence.

::: mermaid
erDiagram
    CROWDSTRIKE_DEVICES {
        TEXT DEVICE_ID PK
        TEXT HOSTNAME
        TEXT PLATFORM_NAME
        TEXT OS_VERSION
        TEXT STATUS
        TIMESTAMP_LTZ FIRST_SEEN
        TIMESTAMP_LTZ LAST_SEEN
    }

    CROWDSTRIKE_DETECTIONS {
        TEXT DETECTION_ID PK
        TEXT DEVICE_ID FK
        TEXT TACTIC
        TEXT TECHNIQUE
        TEXT SEVERITY
        TIMESTAMP_LTZ DETECTION_TIME
    }

    CROWDSTRIKE_INCIDENTS {
        TEXT INCIDENT_ID PK
        TEXT DEVICE_ID FK
        TEXT INCIDENT_TYPE
        TEXT STATUS
        TIMESTAMP_LTZ START_TIME
    }

    CROWDSTRIKE_DEVICES ||--o{ CROWDSTRIKE_DETECTIONS : "DEVICE_ID"
    CROWDSTRIKE_DEVICES ||--o{ CROWDSTRIKE_INCIDENTS : "DEVICE_ID"
:::

**Tables**: 13 tables, 238 columns
**Data Volume**: 252,480 rows
**Key Relationships**: Devices as central entity
```

## Automation

This section is automatically maintained by:

1. **Daily Metadata Refresh**: `SP_REFRESH_METADATA()` at 6:00 AM EST
2. **ERD Views**: 7 metadata views in `DEV_TRANSFORMATION.METADATA`
3. **Export Script**: `01_SQL_SCRIPTS/export_erd_data.sql`

To regenerate this section:
```bash
python run_sql_script.py --script 01_SQL_SCRIPTS/export_erd_data.sql
```

---

**Enhancement Date**: October 24, 2025
**Status**: Ready to add to Data-Model.md wiki
