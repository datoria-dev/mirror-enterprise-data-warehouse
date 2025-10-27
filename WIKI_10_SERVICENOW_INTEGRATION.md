# ServiceNow Integration - Implementation Guide

**Last Updated**: 2025-10-25
**Status**: Planned for Implementation
**Go-Live Target**: November 11, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Business Value](#business-value)
3. [Integration Architecture](#integration-architecture)
4. [Implementation Plan](#implementation-plan)
5. [Prerequisites](#prerequisites)
6. [Data Model](#data-model)
7. [Automation Objects](#automation-objects)
8. [Testing & Validation](#testing--validation)
9. [Monitoring](#monitoring)
10. [Support & Contacts](#support--contacts)

---

## Overview

### What is ServiceNow Integration?

Integration of ServiceNow ITSM data into the SECURITY_ANALYTICS Data Warehouse using **Snowflake Native Connector** to enable comprehensive security and IT operations analytics.

### Integration Method

**Snowflake Native Connector** (Recommended approach)

**Why This Method**:
- ✅ Seamless integration with existing 3-layer architecture
- ✅ Lower total cost of ownership ($744/year vs ADF $1,196-1,364/year)
- ✅ Faster implementation (1-2 weeks vs 4-6 weeks)
- ✅ Automatic incremental updates
- ✅ Schema evolution support
- ✅ No additional infrastructure required

### Key Data Sources

**ServiceNow Tables** (7 tables):
1. **incident** - IT incidents and service requests
2. **cmdb_ci** - Configuration Management Database (asset inventory)
3. **change_request** - Change management records
4. **problem** - Problem management records
5. **sys_user** - User accounts and directory
6. **sys_user_group** - User groups and teams
7. **cmdb_rel_ci** - CI relationships and dependencies

---

## Business Value

### KPIs Enhanced

| KPI # | KPI Name | ServiceNow Source | Type |
|-------|----------|-------------------|------|
| **1** | Asset Inventory Completeness | cmdb_ci | NEW |
| **6** | Mean Time to Detect (MTTD) | incident | ENHANCED |
| **8** | Mean Time to Respond (MTTR) | incident | NEW |
| **9** | Incident Response Rate | incident | NEW |
| **10** | Mean Time to Recover (MTTR) | incident + problem | NEW |

### Cost Savings

| Item | Annual Cost |
|------|-------------|
| **Snowflake Native Connector** | $744 |
| Azure Data Factory (alternative) | $1,196-1,364 |
| **Savings** | **$452-620/year (38-45%)** |

### Automation Expansion

- **Current Objects**: 52 automation objects
- **After Integration**: 71 automation objects
- **Increase**: +19 objects (36.5%)

---

## Integration Architecture

### Three-Layer Data Flow

```
ServiceNow Instance
(GenericCorp-CompanyX.service-now.com)
        ↓
    Snowflake Native Connector
    (Auto-refresh every 15 min - 4 hours)
        ↓
DEV_LANDING.SECURITY_ANALYTICS
L_SNOW_* (7 landing tables)
        ↓
    ETL Tasks (Incremental SCD Type 2)
        ↓
DEV_TRANSFORMATION.SECURITY_ANALYTICS
DIM_SNOW_* (3 dimension tables)
        ↓
    KPI Stored Procedures
        ↓
DEV_REPORTING.SECURITY_ANALYTICS
TBL_KPI_MASTER
        ↓
Streamlit Apps + Power BI Dashboards
```

### Refresh Frequencies

| Table | Refresh Frequency | Rationale |
|-------|-------------------|-----------|
| incident | Every 15 minutes | Real-time incident tracking |
| change_request | Every 30 minutes | Timely change management |
| problem | Every 30 minutes | Problem tracking |
| cmdb_ci | Every 60 minutes | Asset inventory updates |
| sys_user | Every 4 hours | User directory changes |
| sys_user_group | Every 4 hours | Group membership changes |
| cmdb_rel_ci | Every 60 minutes | Asset relationships |

---

## Implementation Plan

### Timeline: 2-Week Implementation

#### Week 1: Setup & Configuration

**Day 1-2: Prerequisites & Access**
- Obtain Snowflake ACCOUNTADMIN access
- Obtain ServiceNow API credentials
- Install Snowflake Connector for ServiceNow from Marketplace
- Configure OAuth authentication

**Day 3-4: Landing Layer Setup**
- Create landing tables (L_SNOW_*)
- Configure connector sync schedules
- Test initial data load
- Validate data quality

**Day 5: Transformation Layer**
- Create dimension tables (DIM_SNOW_*)
- Deploy stored procedures for ETL
- Create scheduled tasks
- Test incremental loads

#### Week 2: KPIs & Go-Live

**Day 1-2: KPI Development**
- Deploy KPI stored procedures
- Update TBL_KPI_MASTER
- Create monitoring views
- Test calculations

**Day 3-4: Testing & Validation**
- End-to-end testing
- Data quality validation
- Performance testing
- User acceptance testing

**Day 5: Production Deployment**
- Enable all scheduled tasks
- Monitor initial runs
- Document final configuration
- **Go-Live: November 11, 2025**

---

## Prerequisites

### Required Access

#### Snowflake Permissions

**ACCOUNTADMIN role** (for initial setup):
- Install Snowflake Marketplace connector
- Create API integrations
- Grant permissions to DEV_DEVELOPER role

**DEV_DEVELOPER role** (for ongoing development):
- CREATE TABLE on DEV_LANDING.SECURITY_ANALYTICS
- CREATE TABLE on DEV_TRANSFORMATION.SECURITY_ANALYTICS
- CREATE PROCEDURE on DEV_TRANSFORMATION.SECURITY_ANALYTICS
- CREATE TASK on all schemas
- EXECUTE TASK on account

#### ServiceNow Permissions

**Required from ServiceNow Admin**:
- OAuth Client ID and Client Secret
- Service account username and password
- API access to required tables
- Read permissions on incident, cmdb_ci, change_request, problem, sys_user, sys_user_group, cmdb_rel_ci

### Network Requirements

- Outbound HTTPS access from Snowflake to ServiceNow instance
- ServiceNow instance URL: `https://GenericCorp-CompanyX.service-now.com`
- No firewall blocks between Snowflake and ServiceNow
- DNS resolution for ServiceNow domain

---

## Data Model

### Landing Layer Tables

**Schema**: `DEV_LANDING.SECURITY_ANALYTICS`

#### L_SNOW_INCIDENT

**Purpose**: Raw incident data from ServiceNow

**Key Columns**:
- `SYS_ID` (Primary Key)
- `NUMBER` - Incident number (e.g., INC0012345)
- `OPENED_AT` - Incident creation timestamp
- `RESOLVED_AT` - Resolution timestamp
- `STATE` - Current state (New, In Progress, Resolved, Closed)
- `PRIORITY` - Priority (1-Critical to 5-Planning)
- `CATEGORY` - Incident category
- `SUBCATEGORY` - Incident subcategory
- `ASSIGNED_TO` - Assigned user sys_id
- `DESCRIPTION` - Incident description
- `CLOSE_NOTES` - Resolution notes
- `LOAD_TIMESTAMP` - Snowflake load time

#### L_SNOW_CMDB_CI

**Purpose**: Configuration items (assets) from CMDB

**Key Columns**:
- `SYS_ID` (Primary Key)
- `ASSET_TAG` - Physical asset tag
- `NAME` - Asset name
- `IP_ADDRESS` - IP address
- `MAC_ADDRESS` - MAC address
- `HOST_NAME` - Hostname
- `OPERATIONAL_STATUS` - Status (Operational, Non-Operational, etc.)
- `CLASS` - CI class (Server, Workstation, Network Device, etc.)
- `LOCATION` - Physical location
- `DEPARTMENT` - Owning department
- `MANAGED_BY` - Managed by user sys_id
- `INSTALL_DATE` - Installation date
- `LOAD_TIMESTAMP` - Snowflake load time

#### L_SNOW_CHANGE_REQUEST

**Purpose**: Change requests and approvals

**Key Columns**:
- `SYS_ID` (Primary Key)
- `NUMBER` - Change request number (e.g., CHG0012345)
- `REQUESTED_BY` - Requester sys_id
- `ASSIGNED_TO` - Assignee sys_id
- `STATE` - Current state
- `RISK` - Risk assessment (High, Medium, Low)
- `IMPACT` - Impact level
- `PRIORITY` - Priority
- `START_DATE` - Planned start
- `END_DATE` - Planned end
- `DESCRIPTION` - Change description
- `LOAD_TIMESTAMP` - Snowflake load time

### Transformation Layer Tables

**Schema**: `DEV_TRANSFORMATION.SECURITY_ANALYTICS`

#### DIM_SNOW_INCIDENT

**Purpose**: Slowly Changing Dimension (Type 2) for incidents

**Key Columns**:
- `INCIDENT_KEY` (Surrogate Key)
- `SYS_ID` (Natural Key)
- `NUMBER`
- `STATE`
- `PRIORITY`
- `TIME_TO_RESOLVE_HOURS` (Calculated)
- `IS_CURRENT` - Current version flag
- `VALID_FROM` - SCD start date
- `VALID_TO` - SCD end date

#### DIM_SNOW_DEVICE

**Purpose**: Slowly Changing Dimension (Type 2) for assets

**Key Columns**:
- `DEVICE_KEY` (Surrogate Key)
- `SYS_ID` (Natural Key)
- `ASSET_TAG`
- `IP_ADDRESS`
- `HOST_NAME`
- `OPERATIONAL_STATUS`
- `CLASS`
- `IS_CURRENT` - Current version flag
- `VALID_FROM` - SCD start date
- `VALID_TO` - SCD end date

#### DIM_SNOW_CHANGE

**Purpose**: Slowly Changing Dimension (Type 2) for changes

**Key Columns**:
- `CHANGE_KEY` (Surrogate Key)
- `SYS_ID` (Natural Key)
- `NUMBER`
- `STATE`
- `RISK`
- `PLANNED_DURATION_HOURS` (Calculated)
- `IS_CURRENT` - Current version flag
- `VALID_FROM` - SCD start date
- `VALID_TO` - SCD end date

---

## Automation Objects

### Stored Procedures (5 total)

#### ETL Procedures

1. **SP_LOAD_DIM_SNOW_INCIDENT_INCREMENTAL()**
   - Purpose: Load and transform incident data with SCD Type 2
   - Schedule: Every 15 minutes
   - Dependencies: L_SNOW_INCIDENT

2. **SP_LOAD_DIM_SNOW_DEVICE_INCREMENTAL()**
   - Purpose: Load and transform asset data with SCD Type 2
   - Schedule: Every 60 minutes
   - Dependencies: L_SNOW_CMDB_CI

3. **SP_LOAD_DIM_SNOW_CHANGE_INCREMENTAL()**
   - Purpose: Load and transform change data with SCD Type 2
   - Schedule: Every 30 minutes
   - Dependencies: L_SNOW_CHANGE_REQUEST

#### KPI Procedures

4. **SP_CALCULATE_KPI_INCIDENT_MTTR()**
   - Purpose: Calculate Mean Time to Respond
   - Schedule: Daily at 7:00 AM
   - Output: Updates TBL_KPI_MASTER

5. **SP_CALCULATE_KPI_ASSET_INVENTORY()**
   - Purpose: Calculate Asset Inventory Completeness
   - Schedule: Daily at 7:00 AM
   - Output: Updates TBL_KPI_MASTER

### Scheduled Tasks (3 total)

1. **TASK_LOAD_DIM_SNOW_INCIDENT**
   - Schedule: Every 15 minutes at :00, :15, :30, :45
   - Calls: SP_LOAD_DIM_SNOW_INCIDENT_INCREMENTAL()
   - Warehouse: DEV_WH (auto-resume)

2. **TASK_LOAD_DIM_SNOW_DEVICE**
   - Schedule: Every 60 minutes at :00
   - Calls: SP_LOAD_DIM_SNOW_DEVICE_INCREMENTAL()
   - Warehouse: DEV_WH (auto-resume)

3. **TASK_CALCULATE_SERVICENOW_KPIS**
   - Schedule: Daily at 7:00 AM EST
   - Calls: Both KPI procedures
   - Warehouse: DEV_WH (auto-resume)

### Monitoring Views (2 total)

1. **VW_SERVICENOW_INTEGRATION_HEALTH**
   - Purpose: Data freshness and row counts
   - Columns: Table name, last load time, row count, data age

2. **VW_SERVICENOW_KPI_SUMMARY**
   - Purpose: KPI values from ServiceNow data
   - Columns: KPI name, current value, target, status

---

## Testing & Validation

### Pre-Production Testing

**Data Quality Checks**:
```sql
-- Check incident data completeness
SELECT
    COUNT(*) as TOTAL_INCIDENTS,
    COUNT(DISTINCT SYS_ID) as UNIQUE_INCIDENTS,
    COUNT(CASE WHEN RESOLVED_AT IS NULL THEN 1 END) as OPEN_INCIDENTS,
    MIN(OPENED_AT) as EARLIEST_INCIDENT,
    MAX(OPENED_AT) as LATEST_INCIDENT
FROM DEV_LANDING.SECURITY_ANALYTICS.L_SNOW_INCIDENT;

-- Check asset inventory
SELECT
    CLASS,
    OPERATIONAL_STATUS,
    COUNT(*) as ASSET_COUNT
FROM DEV_LANDING.SECURITY_ANALYTICS.L_SNOW_CMDB_CI
GROUP BY CLASS, OPERATIONAL_STATUS
ORDER BY ASSET_COUNT DESC;

-- Validate SCD Type 2 logic
SELECT
    NUMBER,
    STATE,
    IS_CURRENT,
    VALID_FROM,
    VALID_TO
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_SNOW_INCIDENT
WHERE NUMBER = 'INC0012345'  -- Example incident
ORDER BY VALID_FROM DESC;
```

### User Acceptance Testing

**Test Scenarios**:
1. New incident created in ServiceNow appears in landing table within 15 minutes
2. Incident state change triggers new SCD record
3. Asset added to CMDB appears in dimension table
4. KPIs calculate correctly based on ServiceNow data
5. Monitoring views show accurate freshness data

### Performance Testing

**Expected Performance**:
- Landing table refresh: < 2 minutes per table
- ETL procedure execution: < 5 minutes
- KPI calculation: < 10 minutes
- Total daily warehouse usage: < 30 minutes

---

## Monitoring

### Daily Health Checks

**Check Integration Health**:
```sql
SELECT *
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.VW_SERVICENOW_INTEGRATION_HEALTH
WHERE DATA_AGE_HOURS > 2;  -- Alert if data is stale
```

**Check Task Execution**:
```sql
SELECT
    NAME,
    STATE,
    SCHEDULED_TIME,
    NEXT_SCHEDULED_TIME
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE NAME LIKE 'TASK_%SNOW%'
  AND SCHEDULED_TIME >= DATEADD(day, -1, CURRENT_TIMESTAMP())
ORDER BY SCHEDULED_TIME DESC;
```

### Performance Monitoring

**Warehouse Credit Usage**:
```sql
SELECT
    DATE_TRUNC('day', START_TIME) as DATE,
    SUM(CREDITS_USED) as DAILY_CREDITS
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE WAREHOUSE_NAME = 'DEV_WH'
  AND START_TIME >= DATEADD(month, -1, CURRENT_TIMESTAMP())
GROUP BY DATE_TRUNC('day', START_TIME)
ORDER BY DATE DESC;
```

### Alerts

**Configure Alerts For**:
- Task failures
- Data age > 2 hours
- Row count anomalies (>50% variance)
- KPI calculation failures

---

## Support & Contacts

### Stakeholders

**ServiceNow Administrator**: Daragh O'Connor
- Role: Provide API credentials and permissions
- Contact: daragh.oconnor@CompanyX.com

**Snowflake Administrator**: Steve Hyer / Prarbdh Ranjan
- Role: Install Marketplace connector, grant permissions
- Contact: steve.hyer@CompanyX.com, prarbdh.ranjan@CompanyX.com

**Data Engineering**: Fuad Onate
- Role: Implementation and ongoing maintenance
- Contact: fuad.onate@CompanyX.com

### Escalation Path

**Level 1 - Data Issues**:
- Check VW_SERVICENOW_INTEGRATION_HEALTH
- Review TASK_HISTORY for failures
- Contact Data Engineering team

**Level 2 - Connector Issues**:
- Verify Snowflake Marketplace connector status
- Check OAuth credentials
- Contact Snowflake Administrator

**Level 3 - ServiceNow API Issues**:
- Verify ServiceNow instance availability
- Check API credentials validity
- Contact ServiceNow Administrator

---

## Resources

### Documentation

**Internal**:
- **WIKI_05_DATA_DICTIONARY.md** - ServiceNow table definitions (when integrated)
- **WIKI_06_BEST_PRACTICES.md** - Development standards
- **WIKI_09_METADATA_REPOSITORY.md** - Metadata catalog

**External**:
- [Snowflake Connector for ServiceNow](https://other-docs.snowflake.com/en/connectors/servicenow/servicenow-about)
- [ServiceNow Table API](https://docs.servicenow.com/bundle/tokyo-application-development/page/integrate/inbound-rest/concept/c_TableAPI.html)
- [Snowflake Tasks Documentation](https://docs.snowflake.com/en/user-guide/tasks-intro)

### Scripts

**Location**: `01_SQL_SCRIPTS/SERVICENOW/`

1. **01_create_landing_tables.sql** - Landing layer setup
2. **02_create_transformation_tables.sql** - Dimension tables
3. **03_create_etl_procedures.sql** - ETL stored procedures
4. **04_create_kpi_procedures.sql** - KPI calculations
5. **05_create_tasks.sql** - Scheduled tasks
6. **06_create_monitoring_views.sql** - Monitoring views
7. **07_verify_integration.sql** - Validation queries

---

## Project Timeline

### Milestones

| Date | Milestone | Status |
|------|-----------|--------|
| Oct 24, 2025 | Integration design complete | ✅ Complete |
| Oct 25, 2025 | Implementation scripts ready | ✅ Complete |
| Oct 28, 2025 | Snowflake Marketplace connector installed | ⏳ Pending |
| Oct 30, 2025 | ServiceNow credentials obtained | ⏳ Pending |
| Nov 1, 2025 | Landing layer setup complete | ⏳ Pending |
| Nov 5, 2025 | Transformation layer complete | ⏳ Pending |
| Nov 8, 2025 | KPIs deployed and tested | ⏳ Pending |
| **Nov 11, 2025** | **Production Go-Live** | ⏳ **Target** |

### Dependencies

**Critical Path**:
1. Snowflake ACCOUNTADMIN access → Marketplace connector installation
2. ServiceNow API credentials → Connector configuration
3. Landing tables created → ETL procedures deployed
4. ETL procedures tested → Tasks enabled
5. All tasks running → Go-Live

**Risk Mitigation**:
- Backup authentication method prepared (service account)
- Rollback scripts ready
- Phased task enablement (test each before enabling all)

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-10-25 | 1.0 | Initial wiki created for Azure DevOps |
| 2025-10-21 | 0.9 | Implementation guide completed |

---

**Status**: 📋 Ready for Implementation
**Next Action**: Obtain Snowflake ACCOUNTADMIN access and ServiceNow API credentials
**Target Go-Live**: November 11, 2025
