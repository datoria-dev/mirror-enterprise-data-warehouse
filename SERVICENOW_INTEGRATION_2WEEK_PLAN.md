# ServiceNow Integration - 2-Week Implementation Plan

## Project Overview

**Duration**: 2 weeks (October 24 - November 7, 2025)
**Objective**: Implement production-ready ServiceNow integration using Snowflake Native Connector
**Approach**: Use Snowflake's native ServiceNow connector instead of custom Python API scripts
**Documentation Reference**: https://docs.snowflake.com/en/connectors/servicenow/about

---

## 🎯 Why Snowflake Native Connector?

### Advantages Over Custom API Integration

| Aspect | Custom Python API | Snowflake Native Connector |
|--------|-------------------|----------------------------|
| **Maintenance** | Manual updates needed | Managed by Snowflake |
| **Authentication** | Manual OAuth refresh | Automatic token management |
| **Incremental Loads** | Custom logic required | Built-in CDC support |
| **Error Handling** | Custom retry logic | Built-in resilience |
| **Monitoring** | Custom logging | Native Snowflake monitoring |
| **Schema Evolution** | Manual updates | Automatic schema detection |
| **Performance** | Depends on implementation | Optimized by Snowflake |
| **Cost** | Compute + maintenance | Connector fee + compute |

**Recommendation**: Use native connector for production (managed, reliable, scalable)

---

## 📋 Week 1: Setup & Configuration (Oct 24 - Oct 31)

### Day 1-2: Prerequisites & Planning

#### Tasks:
- [ ] Verify ServiceNow instance accessibility (not behind VPN)
- [ ] Confirm ACCOUNTADMIN access to Snowflake
- [ ] Document current ServiceNow tables in scope
- [ ] Create project timeline with stakeholders
- [ ] Set up change management approval

#### ServiceNow Instance Verification

```sql
-- Check if we can reach ServiceNow instance
-- Run this from a machine with network access
curl -I https://yourinstance.service-now.com
```

**Key Requirements**:
- ServiceNow instance must be publicly accessible
- NOT hidden behind VPN
- IP address access control must allow Snowflake's network
- OAuth 2.0 or Basic Auth credentials ready

#### Current DW Context

Based on our data warehouse:
- **Current ServiceNow tables**: 2 tables (SERVICENOW_INCIDENTS, SERVICENOW_CHANGES)
- **Current data volume**: ~616,250 records
- **Current refresh**: Custom Python scripts (manual)
- **Target state**: Native connector with automated incremental refresh

---

### Day 3-4: Snowflake Connector Installation

#### Installation Method: Snowsight (Recommended)

**Step 1: Access Snowflake Marketplace**

```sql
-- Login as ACCOUNTADMIN
USE ROLE ACCOUNTADMIN;

-- Navigate to: Data Products > Marketplace
-- Search for: "Snowflake Connector for ServiceNow"
```

**Step 2: Install Connector**

1. Go to Snowsight → Marketplace
2. Search: "Snowflake Connector for ServiceNow"
3. Click "Get" → "Install"
4. Follow installation wizard

**Step 3: Configure Database Objects**

```sql
-- Create dedicated database for ServiceNow data
CREATE DATABASE IF NOT EXISTS SERVICENOW_CONNECTOR
    COMMENT = 'ServiceNow data ingested via Snowflake Native Connector';

-- Create schema for raw ServiceNow data
CREATE SCHEMA IF NOT EXISTS SERVICENOW_CONNECTOR.RAW_DATA
    COMMENT = 'Raw ServiceNow tables synced by connector';

-- Create schema for connector metadata
CREATE SCHEMA IF NOT EXISTS SERVICENOW_CONNECTOR.CONNECTOR_METADATA
    COMMENT = 'Connector configuration and sync metadata';

-- Grant necessary permissions
GRANT USAGE ON DATABASE SERVICENOW_CONNECTOR TO ROLE DEV_DEVELOPER;
GRANT USAGE ON SCHEMA SERVICENOW_CONNECTOR.RAW_DATA TO ROLE DEV_DEVELOPER;
GRANT SELECT ON ALL TABLES IN SCHEMA SERVICENOW_CONNECTOR.RAW_DATA TO ROLE DEV_DEVELOPER;
```

**Step 4: Configure Virtual Warehouse**

```sql
-- Create dedicated warehouse for ServiceNow connector
CREATE WAREHOUSE IF NOT EXISTS SERVICENOW_WH
    WAREHOUSE_SIZE = 'SMALL'
    AUTO_SUSPEND = 300  -- 5 minutes
    AUTO_RESUME = TRUE  -- REQUIRED for connector
    INITIALLY_SUSPENDED = FALSE
    COMMENT = 'Warehouse for ServiceNow connector background ingestion';

-- Grant usage to connector
GRANT USAGE ON WAREHOUSE SERVICENOW_WH TO APPLICATION SERVICENOW_CONNECTOR;
```

**Important**:
- `AUTO_RESUME = TRUE` is **mandatory**
- Serverless compute is **not supported**
- `AUTOCOMMIT` parameter must be enabled (default)

---

### Day 5-6: ServiceNow OAuth Configuration

#### Option 1: OAuth 2.0 (Recommended)

**Step 1: Create OAuth Application in ServiceNow**

1. Login to ServiceNow instance
2. Navigate to: **System OAuth** → **Application Registry**
3. Click **New** → **Create an OAuth API endpoint for external clients**

**Configuration**:
- **Name**: `Snowflake Data Connector`
- **Client ID**: Auto-generated (copy this)
- **Client Secret**: Auto-generated (copy this)
- **Redirect URL**: `https://yourinstance.service-now.com/oauth_redirect.do`
- **Access Token Lifespan**: 600 seconds (minimum)
- **Refresh Token Lifespan**: 7776000 seconds (90 days - recommended)

**Step 2: Assign Permissions**

Create or use existing ServiceNow user with:
- **Role**: `rest_service` (minimum)
- **Role**: `itil` (for incident/change access)
- **Role**: `cmdb_read` (for configuration items)

**Step 3: Configure in Snowflake**

```sql
-- Run connector configuration procedure
CALL SERVICENOW_CONNECTOR.PUBLIC.SET_CONNECTION_CONFIGURATION(
    servicenow_instance => 'yourinstance',  -- Just the instance name, not full URL
    auth_type => 'OAUTH',
    client_id => 'your_client_id_here',
    client_secret => 'your_client_secret_here',
    username => 'integration_user@CompanyX.com',
    password => 'user_password_here'
);

-- Test connection
CALL SERVICENOW_CONNECTOR.PUBLIC.TEST_CONNECTION();
```

#### Option 2: Basic Authentication (Simpler, Less Secure)

```sql
-- Configure with Basic Auth
CALL SERVICENOW_CONNECTOR.PUBLIC.SET_CONNECTION_CONFIGURATION(
    servicenow_instance => 'yourinstance',
    auth_type => 'BASIC',
    username => 'integration_user@CompanyX.com',
    password => 'user_password_here'
);
```

**Note**: OAuth is recommended for production environments.

---

### Day 7: Table Selection & Enablement

#### Step 1: Get Available Tables

```sql
-- List all available ServiceNow tables
CALL SERVICENOW_CONNECTOR.PUBLIC.GET_AVAILABLE_TABLES();

-- Result will show tables like:
-- incident, change_request, sys_user, cmdb_ci, sys_user_group, etc.
```

#### Step 2: Enable Priority Tables

Based on SECURITY_ANALYTICS DW requirements:

```sql
-- Enable Incidents table
CALL SERVICENOW_CONNECTOR.PUBLIC.ENABLE_TABLE(
    table_name => 'incident',
    destination_schema => 'RAW_DATA',
    destination_table => 'SERVICENOW_INCIDENTS'
);

-- Enable Change Requests table
CALL SERVICENOW_CONNECTOR.PUBLIC.ENABLE_TABLE(
    table_name => 'change_request',
    destination_schema => 'RAW_DATA',
    destination_table => 'SERVICENOW_CHANGES'
);

-- Enable Users table (for joins)
CALL SERVICENOW_CONNECTOR.PUBLIC.ENABLE_TABLE(
    table_name => 'sys_user',
    destination_schema => 'RAW_DATA',
    destination_table => 'SERVICENOW_USERS'
);

-- Enable User Groups table
CALL SERVICENOW_CONNECTOR.PUBLIC.ENABLE_TABLE(
    table_name => 'sys_user_group',
    destination_schema => 'RAW_DATA',
    destination_table => 'SERVICENOW_USER_GROUPS'
);

-- Enable CMDB Configuration Items
CALL SERVICENOW_CONNECTOR.PUBLIC.ENABLE_TABLE(
    table_name => 'cmdb_ci',
    destination_schema => 'RAW_DATA',
    destination_table => 'SERVICENOW_CMDB_CI'
);

-- Enable CMDB Servers
CALL SERVICENOW_CONNECTOR.PUBLIC.ENABLE_TABLE(
    table_name => 'cmdb_ci_server',
    destination_schema => 'RAW_DATA',
    destination_table => 'SERVICENOW_CMDB_SERVERS'
);

-- Enable Security Incidents (if available)
CALL SERVICENOW_CONNECTOR.PUBLIC.ENABLE_TABLE(
    table_name => 'sn_si_incident',
    destination_schema => 'RAW_DATA',
    destination_table => 'SERVICENOW_SECURITY_INCIDENTS'
);
```

**Priority Tables for SECURITY_ANALYTICS**:
1. `incident` - IT incidents (security-related)
2. `change_request` - Change requests
3. `sys_user` - User accounts
4. `sys_user_group` - User groups/teams
5. `cmdb_ci` - Configuration items
6. `cmdb_ci_server` - Server inventory
7. `sn_si_incident` - Security incidents (if Security Incident Response module is enabled)

---

## 📊 Week 2: Data Transformation & Integration (Nov 1 - Nov 7)

### Day 8-9: Initial Data Load & Validation

#### Step 1: Trigger Initial Load

```sql
-- Finalize connector configuration (triggers initial load)
CALL SERVICENOW_CONNECTOR.PUBLIC.FINALIZE_CONNECTOR_CONFIGURATION();

-- Monitor ingestion progress
SELECT *
FROM SERVICENOW_CONNECTOR.CONNECTOR_METADATA.INGESTION_STATUS
ORDER BY LAST_UPDATED DESC;

-- Check table row counts
SELECT
    table_name,
    row_count,
    last_ingestion_timestamp
FROM SERVICENOW_CONNECTOR.CONNECTOR_METADATA.TABLE_METADATA
ORDER BY table_name;
```

#### Step 2: Validate Data Quality

```sql
-- Check incidents data
SELECT
    COUNT(*) AS total_incidents,
    COUNT(DISTINCT sys_id) AS unique_incidents,
    MIN(sys_created_on) AS oldest_incident,
    MAX(sys_created_on) AS newest_incident,
    COUNT(CASE WHEN category = 'security' THEN 1 END) AS security_incidents
FROM SERVICENOW_CONNECTOR.RAW_DATA.SERVICENOW_INCIDENTS;

-- Check for NULL critical fields
SELECT
    'incident' AS table_name,
    COUNT(*) AS total_rows,
    COUNT(CASE WHEN number IS NULL THEN 1 END) AS null_number,
    COUNT(CASE WHEN state IS NULL THEN 1 END) AS null_state,
    COUNT(CASE WHEN priority IS NULL THEN 1 END) AS null_priority,
    COUNT(CASE WHEN opened_at IS NULL THEN 1 END) AS null_opened_at
FROM SERVICENOW_CONNECTOR.RAW_DATA.SERVICENOW_INCIDENTS;

-- Compare with existing data (reconciliation)
SELECT
    'Connector' AS source,
    COUNT(*) AS incident_count
FROM SERVICENOW_CONNECTOR.RAW_DATA.SERVICENOW_INCIDENTS
UNION ALL
SELECT
    'Legacy Python' AS source,
    COUNT(*) AS incident_count
FROM DEV_TRANSFORMATION.SERVICENOW.SERVICENOW_INCIDENTS;
```

---

### Day 10-11: Transformation Pipeline Setup

#### Create Transformation Views/Tables

```sql
-- Create transformation schema
CREATE SCHEMA IF NOT EXISTS DEV_TRANSFORMATION.SERVICENOW_V2
    COMMENT = 'Transformed ServiceNow data from native connector';

-- Transformation table for incidents
CREATE OR REPLACE TABLE DEV_TRANSFORMATION.SERVICENOW_V2.INCIDENTS AS
SELECT
    -- Primary Key
    sys_id AS incident_id,

    -- Incident Details
    number AS incident_number,
    short_description,
    description,

    -- Classification
    TRY_CAST(priority AS INTEGER) AS priority,
    CASE priority
        WHEN '1' THEN 'Critical'
        WHEN '2' THEN 'High'
        WHEN '3' THEN 'Medium'
        WHEN '4' THEN 'Low'
        WHEN '5' THEN 'Planning'
        ELSE 'Unknown'
    END AS priority_name,

    TRY_CAST(state AS INTEGER) AS state,
    CASE state
        WHEN '1' THEN 'New'
        WHEN '2' THEN 'In Progress'
        WHEN '3' THEN 'On Hold'
        WHEN '6' THEN 'Resolved'
        WHEN '7' THEN 'Closed'
        WHEN '8' THEN 'Canceled'
        ELSE 'Unknown'
    END AS state_name,

    category,
    subcategory,

    -- Assignment
    assigned_to,
    assignment_group,

    -- Severity & Impact
    TRY_CAST(severity AS INTEGER) AS severity,
    TRY_CAST(impact AS INTEGER) AS impact,
    TRY_CAST(urgency AS INTEGER) AS urgency,

    -- Dates
    TRY_CAST(opened_at AS TIMESTAMP_LTZ) AS opened_at,
    TRY_CAST(closed_at AS TIMESTAMP_LTZ) AS closed_at,
    TRY_CAST(resolved_at AS TIMESTAMP_LTZ) AS resolved_at,

    -- Calculate metrics
    DATEDIFF(hour, TRY_CAST(opened_at AS TIMESTAMP_LTZ),
                   COALESCE(TRY_CAST(resolved_at AS TIMESTAMP_LTZ), CURRENT_TIMESTAMP())) AS hours_to_resolve,

    -- Flags
    CASE WHEN category = 'security' THEN TRUE ELSE FALSE END AS is_security_incident,
    CASE WHEN state IN ('6', '7') THEN TRUE ELSE FALSE END AS is_closed,

    -- Metadata
    TRY_CAST(sys_created_on AS TIMESTAMP_LTZ) AS sys_created_on,
    TRY_CAST(sys_updated_on AS TIMESTAMP_LTZ) AS sys_updated_on,
    sys_created_by,
    sys_updated_by,

    CURRENT_TIMESTAMP() AS dw_created_date,
    CURRENT_TIMESTAMP() AS dw_modified_date
FROM SERVICENOW_CONNECTOR.RAW_DATA.SERVICENOW_INCIDENTS
WHERE sys_id IS NOT NULL;  -- Ensure valid records

-- Create materialized view for real-time queries
CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SERVICENOW_V2.VW_INCIDENTS_CURRENT AS
SELECT *
FROM DEV_TRANSFORMATION.SERVICENOW_V2.INCIDENTS
WHERE is_closed = FALSE
ORDER BY priority, opened_at;

-- Transformation table for changes
CREATE OR REPLACE TABLE DEV_TRANSFORMATION.SERVICENOW_V2.CHANGES AS
SELECT
    sys_id AS change_id,
    number AS change_number,
    short_description,
    description,

    -- Classification
    type AS change_type,
    TRY_CAST(risk AS INTEGER) AS risk_level,
    TRY_CAST(priority AS INTEGER) AS priority,
    TRY_CAST(state AS INTEGER) AS state,

    -- Dates
    TRY_CAST(start_date AS TIMESTAMP_LTZ) AS planned_start_date,
    TRY_CAST(end_date AS TIMESTAMP_LTZ) AS planned_end_date,
    TRY_CAST(work_start AS TIMESTAMP_LTZ) AS actual_start_date,
    TRY_CAST(work_end AS TIMESTAMP_LTZ) AS actual_end_date,

    -- Assignment
    assigned_to,
    assignment_group,

    -- Results
    close_code,
    close_notes,

    -- Metadata
    TRY_CAST(sys_created_on AS TIMESTAMP_LTZ) AS sys_created_on,
    TRY_CAST(sys_updated_on AS TIMESTAMP_LTZ) AS sys_updated_on,

    CURRENT_TIMESTAMP() AS dw_created_date,
    CURRENT_TIMESTAMP() AS dw_modified_date
FROM SERVICENOW_CONNECTOR.RAW_DATA.SERVICENOW_CHANGES
WHERE sys_id IS NOT NULL;
```

---

### Day 12: Incremental Refresh Configuration

#### Configure Refresh Schedule

```sql
-- Create task for incremental refresh
CREATE OR REPLACE TASK servicenow_incidents_refresh_task
    WAREHOUSE = DEV_WH
    SCHEDULE = '15 MINUTE'  -- Refresh every 15 minutes
AS
    MERGE INTO DEV_TRANSFORMATION.SERVICENOW_V2.INCIDENTS tgt
    USING (
        SELECT
            sys_id AS incident_id,
            number AS incident_number,
            short_description,
            description,
            -- [all transformation logic from above]
        FROM SERVICENOW_CONNECTOR.RAW_DATA.SERVICENOW_INCIDENTS
        WHERE TRY_CAST(sys_updated_on AS TIMESTAMP_LTZ) >= DATEADD(minute, -20, CURRENT_TIMESTAMP())
    ) src
    ON tgt.incident_id = src.incident_id
    WHEN MATCHED THEN
        UPDATE SET
            tgt.incident_number = src.incident_number,
            tgt.short_description = src.short_description,
            tgt.state = src.state,
            tgt.state_name = src.state_name,
            tgt.closed_at = src.closed_at,
            tgt.resolved_at = src.resolved_at,
            tgt.sys_updated_on = src.sys_updated_on,
            tgt.dw_modified_date = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN
        INSERT (incident_id, incident_number, short_description, [all columns])
        VALUES (src.incident_id, src.incident_number, src.short_description, [all values]);

-- Start the task
ALTER TASK servicenow_incidents_refresh_task RESUME;

-- Monitor task execution
SELECT *
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    TASK_NAME => 'SERVICENOW_INCIDENTS_REFRESH_TASK',
    SCHEDULED_TIME_RANGE_START => DATEADD(day, -1, CURRENT_TIMESTAMP())
))
ORDER BY SCHEDULED_TIME DESC;
```

**Connector Incremental Sync**:

The connector automatically handles incremental updates:
- Uses `sys_updated_on` field for CDC (Change Data Capture)
- No manual configuration needed
- Syncs only changed/new records
- Default sync frequency: configurable (recommend 15-30 minutes)

```sql
-- Check connector sync status
SELECT
    table_name,
    last_sync_timestamp,
    next_sync_timestamp,
    sync_status,
    records_ingested_last_sync,
    error_message
FROM SERVICENOW_CONNECTOR.CONNECTOR_METADATA.SYNC_STATUS
ORDER BY last_sync_timestamp DESC;
```

---

### Day 13: Integration with Existing DW

#### Update Metadata Repository

```sql
-- Add ServiceNow connector tables to metadata registry
INSERT INTO DEV_TRANSFORMATION.METADATA.TABLE_REGISTRY (
    SERVICE_NAME,
    DATABASE_NAME,
    SCHEMA_NAME,
    TABLE_NAME,
    TABLE_TYPE,
    DATA_LAYER,
    DESCRIPTION,
    IS_ACTIVE
)
VALUES
    ('ServiceNow', 'SERVICENOW_CONNECTOR', 'RAW_DATA', 'SERVICENOW_INCIDENTS', 'TABLE', 'LANDING', 'ServiceNow incidents synced via native connector', TRUE),
    ('ServiceNow', 'SERVICENOW_CONNECTOR', 'RAW_DATA', 'SERVICENOW_CHANGES', 'TABLE', 'LANDING', 'ServiceNow change requests synced via native connector', TRUE),
    ('ServiceNow', 'DEV_TRANSFORMATION', 'SERVICENOW_V2', 'INCIDENTS', 'TABLE', 'TRANSFORMATION', 'Transformed ServiceNow incidents', TRUE),
    ('ServiceNow', 'DEV_TRANSFORMATION', 'SERVICENOW_V2', 'CHANGES', 'TABLE', 'TRANSFORMATION', 'Transformed ServiceNow changes', TRUE);

-- Refresh metadata
CALL DEV_TRANSFORMATION.METADATA.SP_REFRESH_METADATA();
```

#### Create Unified View (Bridge Old and New)

```sql
-- Create unified view combining legacy and connector data
CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SERVICENOW.VW_INCIDENTS_UNIFIED AS
SELECT
    'CONNECTOR' AS data_source,
    incident_id,
    incident_number,
    short_description,
    priority,
    priority_name,
    state,
    state_name,
    category,
    opened_at,
    closed_at,
    resolved_at,
    is_security_incident
FROM DEV_TRANSFORMATION.SERVICENOW_V2.INCIDENTS
UNION ALL
SELECT
    'LEGACY' AS data_source,
    incident_id,
    incident_number,
    short_description,
    priority,
    priority_name,
    state,
    state_name,
    category,
    opened_at,
    closed_at,
    resolved_at,
    CASE WHEN category = 'security' THEN TRUE ELSE FALSE END AS is_security_incident
FROM DEV_TRANSFORMATION.SERVICENOW.SERVICENOW_INCIDENTS
WHERE incident_id NOT IN (
    SELECT incident_id FROM DEV_TRANSFORMATION.SERVICENOW_V2.INCIDENTS
);

-- Verify no duplicates
SELECT
    incident_number,
    COUNT(*) AS duplicate_count
FROM DEV_TRANSFORMATION.SERVICENOW.VW_INCIDENTS_UNIFIED
GROUP BY incident_number
HAVING COUNT(*) > 1;
```

---

### Day 14: Monitoring, Documentation & Cutover

#### Monitoring Dashboard

```sql
-- Create monitoring views
CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SERVICENOW_V2.VW_CONNECTOR_HEALTH AS
SELECT
    'ServiceNow Connector Health' AS dashboard_name,

    -- Connection Status
    (SELECT connection_status FROM SERVICENOW_CONNECTOR.CONNECTOR_METADATA.CONNECTION_INFO) AS connection_status,

    -- Last Sync
    (SELECT MAX(last_sync_timestamp) FROM SERVICENOW_CONNECTOR.CONNECTOR_METADATA.SYNC_STATUS) AS last_successful_sync,
    DATEDIFF(minute, (SELECT MAX(last_sync_timestamp) FROM SERVICENOW_CONNECTOR.CONNECTOR_METADATA.SYNC_STATUS), CURRENT_TIMESTAMP()) AS minutes_since_last_sync,

    -- Data Freshness
    (SELECT MAX(sys_updated_on) FROM SERVICENOW_CONNECTOR.RAW_DATA.SERVICENOW_INCIDENTS) AS last_incident_update,

    -- Record Counts
    (SELECT COUNT(*) FROM SERVICENOW_CONNECTOR.RAW_DATA.SERVICENOW_INCIDENTS) AS total_incidents,
    (SELECT COUNT(*) FROM SERVICENOW_CONNECTOR.RAW_DATA.SERVICENOW_CHANGES) AS total_changes,

    -- Health Status
    CASE
        WHEN DATEDIFF(minute, (SELECT MAX(last_sync_timestamp) FROM SERVICENOW_CONNECTOR.CONNECTOR_METADATA.SYNC_STATUS), CURRENT_TIMESTAMP()) > 30
        THEN '⚠️ ALERT: Sync delayed'
        ELSE '✅ OK'
    END AS health_status;

-- Data quality checks
CREATE OR REPLACE VIEW DEV_TRANSFORMATION.SERVICENOW_V2.VW_DATA_QUALITY AS
SELECT
    'Incidents' AS table_name,
    COUNT(*) AS total_records,
    COUNT(DISTINCT incident_id) AS unique_records,
    COUNT(*) - COUNT(DISTINCT incident_id) AS duplicate_count,
    COUNT(CASE WHEN incident_number IS NULL THEN 1 END) AS null_incident_number,
    COUNT(CASE WHEN opened_at IS NULL THEN 1 END) AS null_opened_at,
    ROUND((COUNT(*) - COUNT(CASE WHEN incident_number IS NULL THEN 1 END)) / COUNT(*) * 100, 2) AS completeness_pct
FROM DEV_TRANSFORMATION.SERVICENOW_V2.INCIDENTS
UNION ALL
SELECT
    'Changes' AS table_name,
    COUNT(*) AS total_records,
    COUNT(DISTINCT change_id) AS unique_records,
    COUNT(*) - COUNT(DISTINCT change_id) AS duplicate_count,
    COUNT(CASE WHEN change_number IS NULL THEN 1 END) AS null_change_number,
    COUNT(CASE WHEN planned_start_date IS NULL THEN 1 END) AS null_start_date,
    ROUND((COUNT(*) - COUNT(CASE WHEN change_number IS NULL THEN 1 END)) / COUNT(*) * 100, 2) AS completeness_pct
FROM DEV_TRANSFORMATION.SERVICENOW_V2.CHANGES;
```

#### Update Streamlit Apps

Modify existing Streamlit dashboards to use new connector data:

```python
# Update connection to use new schema
# File: 05_STREAMLIT_APPS/01_ServiceNow_Analytics.py

import streamlit as st
import snowflake.connector

# Updated query to use connector data
query = """
SELECT
    incident_number,
    short_description,
    priority_name,
    state_name,
    category,
    opened_at,
    closed_at,
    hours_to_resolve
FROM DEV_TRANSFORMATION.SERVICENOW_V2.VW_INCIDENTS_CURRENT
WHERE is_security_incident = TRUE
ORDER BY opened_at DESC
LIMIT 100
"""
```

#### Documentation Update

Update API Integrations wiki with connector implementation:

```markdown
## ServiceNow Integration - Native Connector (Production)

**Status**: ✅ LIVE
**Method**: Snowflake Native Connector
**Sync Frequency**: Every 15 minutes (automatic)
**Authentication**: OAuth 2.0 with 90-day refresh token

### Tables Synced:
- SERVICENOW_INCIDENTS (Raw)
- SERVICENOW_CHANGES (Raw)
- SERVICENOW_USERS (Raw)
- SERVICENOW_USER_GROUPS (Raw)
- SERVICENOW_CMDB_CI (Raw)

### Monitoring:
Query `VW_CONNECTOR_HEALTH` for real-time status
```

---

## 📊 Success Metrics

### Week 1 Deliverables:
- [ ] Connector installed and configured
- [ ] OAuth authentication working
- [ ] 7 ServiceNow tables enabled
- [ ] Initial data load completed
- [ ] Data validation passed

### Week 2 Deliverables:
- [ ] Transformation pipeline created
- [ ] Incremental refresh configured (15-min intervals)
- [ ] Monitoring dashboards deployed
- [ ] Streamlit apps updated
- [ ] Documentation updated
- [ ] Metadata repository updated

### Key Performance Indicators:
- **Data Freshness**: < 20 minutes lag
- **Data Quality**: > 95% completeness
- **Sync Success Rate**: > 99%
- **Query Performance**: < 5 seconds for dashboards

---

## 🚨 Risk Mitigation

### Potential Issues & Solutions:

| Risk | Mitigation |
|------|------------|
| **VPN/Firewall blocking** | Verify ServiceNow instance is publicly accessible |
| **OAuth token expiration** | Set refresh token to 90 days, monitor expiration |
| **Schema changes** | Connector auto-detects; test in DEV first |
| **Data volume growth** | Monitor warehouse usage; upgrade if needed |
| **Connector downtime** | Set up email alerts for sync failures |
| **Legacy app compatibility** | Maintain unified view during transition |

---

## 💰 Cost Estimation

### Connector Costs:
- **Connector Fee**: ~$500/month (Snowflake Marketplace)
- **Warehouse Compute**: ~$100/month (SMALL warehouse, 15-min sync)
- **Storage**: ~$23/month (1TB ServiceNow data)
- **Total**: ~$623/month

**vs. Custom Python Solution**:
- **Compute**: ~$150/month
- **Maintenance**: ~$2,000/month (dev time)
- **Total**: ~$2,150/month

**Savings**: ~$1,527/month (~71% reduction)

---

## 📁 Deliverables

### SQL Scripts:
1. **01_servicenow_connector_setup.sql** - Initial setup
2. **02_servicenow_table_enablement.sql** - Enable tables
3. **03_servicenow_transformation.sql** - Transformation logic
4. **04_servicenow_monitoring.sql** - Monitoring views
5. **05_servicenow_metadata_update.sql** - Metadata registry

### Documentation:
1. **ServiceNow Connector Implementation Guide**
2. **Updated API Integrations Wiki**
3. **Runbook for troubleshooting**
4. **Change Management Documentation**

### Dashboards:
1. **Connector Health Dashboard** (Streamlit)
2. **Data Quality Dashboard** (Streamlit)
3. **ServiceNow Analytics Dashboard** (updated)

---

## 👥 Stakeholders & Approvals

### Required Approvals:
- [ ] **ACCOUNTADMIN** - Connector installation
- [ ] **ServiceNow Admin** - OAuth app creation
- [ ] **Security Team** - Network access verification
- [ ] **Data Governance** - Data classification review
- [ ] **Finance** - Budget approval (~$623/month)

### Communication Plan:
- **Kickoff Meeting**: Day 1 (Oct 24)
- **Progress Updates**: Daily standups
- **Demo**: Day 10 (Nov 3)
- **Go-Live**: Day 14 (Nov 7)
- **Post-Implementation Review**: Day 21 (Nov 14)

---

## 🎯 Next Steps (After Week 2)

1. **Decommission Legacy Python Scripts**
   - Archive old extraction scripts
   - Update documentation
   - Remove cron jobs

2. **Expand ServiceNow Coverage**
   - Enable additional tables (security_incident, problem, etc.)
   - Add custom ServiceNow modules

3. **Advanced Analytics**
   - Incident trend analysis
   - MTTR (Mean Time To Resolve) dashboards
   - Predictive analytics for incident volume

4. **Integration with Other Services**
   - Cross-reference incidents with CrowdStrike detections
   - Link changes to Qualys vulnerability scans
   - Correlate with SentinelOne threat alerts

---

**Plan Created**: October 24, 2025
**Target Go-Live**: November 7, 2025
**Project Owner**: Lead Data Engineer - SECURITY_ANALYTICS Project
**Status**: 📋 READY TO BEGIN
