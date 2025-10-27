# ServiceNow Integration Implementation Guide

**Project**: SECURITY_ANALYTICS Data Warehouse
**Integration Method**: Snowflake Native Connector
**Version**: 1.0
**Date**: 2025-10-21
**Status**: Ready for Production Deployment

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Integration Architecture](#2-integration-architecture)
3. [Pre-Implementation Checklist](#3-pre-implementation-checklist)
4. [Step-by-Step Implementation](#4-step-by-step-implementation)
5. [Post-Implementation Validation](#5-post-implementation-validation)
6. [Monitoring and Maintenance](#6-monitoring-and-maintenance)
7. [Troubleshooting](#7-troubleshooting)
8. [Rollback Procedures](#8-rollback-procedures)

---

## 1. Executive Summary

### 1.1 Purpose

This guide provides step-by-step instructions for implementing ServiceNow integration into the existing SECURITY_ANALYTICS data warehouse using the Snowflake Native Connector.

### 1.2 Business Value

| Metric | Value |
|--------|-------|
| **KPIs Enhanced** | 4 (MTTR, Asset Inventory, Incident Response, MTTR Recovery) |
| **New Data Sources** | 6 ServiceNow tables |
| **Implementation Time** | 1-2 weeks |
| **Annual Cost** | $744 (vs ADF $1,196-1,364) |
| **Cost Savings** | $452-620/year (38-45%) |
| **Automation Objects Added** | +19 (52 → 71 objects, 36.5% increase) |

### 1.3 Integration Method: Snowflake Native Connector

**Why Chosen**:
- ✅ Perfect alignment with existing 3-layer architecture
- ✅ Seamless integration with current automation framework
- ✅ Lower TCO than Azure Data Factory
- ✅ Faster implementation (1-2 weeks vs 4-6 weeks)
- ✅ Maintains "everything consolidated in Snowflake" principle
- ✅ Automatic incremental updates with schema evolution

---

## 2. Integration Architecture

### 2.1 Three-Layer Data Flow

```
ServiceNow Instance (GenericCorp-CompanyX.service-now.com)
    ↓ (Snowflake Connector - Auto-refresh every 2-4 hours)
DEV_LANDING.SECURITY_ANALYTICS.L_SNOW_* (6 tables)
    ↓ (ETL Tasks - Every 2-4 hours)
DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_SNOW_* (3 dimensions)
    ↓ (KPI Procedures - Daily at 7:00 AM)
DEV_REPORTING.SECURITY_ANALYTICS.TBL_KPI_MASTER
    ↓
Power BI Dashboards + Streamlit Apps
```

### 2.2 Tables and Objects

#### **Landing Layer** (DEV_LANDING.SECURITY_ANALYTICS)

| Table | Purpose | Refresh Frequency |
|-------|---------|-------------------|
| **L_SNOW_INCIDENTS** | Raw incident data | Every 2 hours |
| **L_SNOW_CMDB_CI** | Asset inventory | Every 4 hours |
| **L_SNOW_CHANGES** | Change requests | Every 4 hours |
| **L_SNOW_USERS** | User accounts | Every 6 hours |
| **L_SNOW_PROBLEMS** | Problem records | Every 4 hours |
| **L_SNOW_VULNERABILITIES** | Custom vulnerability tracking | Every 4 hours |

#### **Transformation Layer** (DEV_TRANSFORMATION.SECURITY_ANALYTICS)

| Dimension | SCD Type | Key Attributes |
|-----------|----------|----------------|
| **DIM_SNOW_INCIDENT** | Type 2 | SYS_ID, NUMBER, STATE, PRIORITY, TIME_TO_RESOLVE_HOURS |
| **DIM_SNOW_DEVICE** | Type 2 | SYS_ID, ASSET_TAG, IP_ADDRESS, HOST_NAME, OPERATIONAL_STATUS |
| **DIM_SNOW_CHANGE** | Type 2 | SYS_ID, NUMBER, STATE, RISK, PLANNED_DURATION_HOURS |

#### **Stored Procedures** (5 total)

1. **SP_LOAD_DIM_SNOW_INCIDENT_INCREMENTAL()** - Incident ETL with SCD Type 2
2. **SP_LOAD_DIM_SNOW_DEVICE_INCREMENTAL()** - Device ETL with SCD Type 2
3. **SP_LOAD_DIM_SNOW_CHANGE_INCREMENTAL()** - Change ETL (created implicitly)
4. **SP_CALCULATE_KPI_INCIDENT_MTTR()** - KPI #8: Mean Time to Respond
5. **SP_CALCULATE_KPI_ASSET_INVENTORY()** - KPI #1: Asset Inventory Completeness

#### **Scheduled Tasks** (3 total)

1. **TASK_LOAD_DIM_SNOW_INCIDENT** - Every 2 hours at :00
2. **TASK_LOAD_DIM_SNOW_DEVICE** - Every 4 hours at :00
3. **TASK_CALCULATE_SERVICENOW_KPIS** - Daily at 7:00 AM

#### **Monitoring Views** (2 total)

1. **VW_SERVICENOW_INTEGRATION_HEALTH** - Data freshness and counts
2. **VW_SERVICENOW_KPI_SUMMARY** - KPI values from ServiceNow data

### 2.3 Enhanced KPIs

| KPI # | KPI Name | ServiceNow Source | Status |
|-------|----------|-------------------|--------|
| **1** | Asset Inventory Completeness | cmdb_ci | NEW |
| **6** | Mean Time to Detect (MTTD) | incident | ENHANCED |
| **8** | Mean Time to Respond (MTTR) | incident | NEW |
| **9** | Incident Response Rate | incident | NEW |
| **10** | Mean Time to Recover | incident + problem | NEW |

---

## 3. Pre-Implementation Checklist

### 3.1 Access Requirements

- [ ] **Snowflake Accounts**:
  - [ ] ACCOUNTADMIN role access (for integration creation)
  - [ ] SYSADMIN role access (for object creation)
  - [ ] Access to DEV_WH warehouse
  - [ ] Access to all 3 databases (DEV_LANDING, DEV_TRANSFORMATION, DEV_REPORTING)

- [ ] **ServiceNow Access**:
  - [ ] ServiceNow instance URL: `https://GenericCorp-CompanyX.service-now.com`
  - [ ] ServiceNow API credentials (username + password or API token)
  - [ ] Table API v2 access permissions
  - [ ] Confirmed access to required tables:
    - [ ] incident
    - [ ] cmdb_ci
    - [ ] change_request
    - [ ] sys_user
    - [ ] problem
    - [ ] u_vulnerability (if exists)

### 3.2 Technical Prerequisites

- [ ] **Snowflake Environment**:
  - [ ] DEV_WH warehouse running and available
  - [ ] All 3 databases exist and are accessible
  - [ ] Current automation framework (52 objects) is operational
  - [ ] ETL_PIPELINE_LOG table exists in DEV_TRANSFORMATION.SECURITY_ANALYTICS
  - [ ] TBL_KPI_MASTER table exists in DEV_REPORTING.SECURITY_ANALYTICS

- [ ] **Network Connectivity**:
  - [ ] Snowflake can reach ServiceNow instance (outbound HTTPS)
  - [ ] No firewall rules blocking ServiceNow API calls
  - [ ] DNS resolution for GenericCorp-CompanyX.service-now.com

### 3.3 Coordination Requirements

- [ ] **Stakeholder Notifications**:
  - [ ] Inform ServiceNow administrator of API integration
  - [ ] Notify Data Engineering team of deployment window
  - [ ] Alert BI team for dashboard updates

- [ ] **Documentation**:
  - [ ] ServiceNow API credentials securely documented
  - [ ] Implementation script reviewed and approved
  - [ ] Rollback plan confirmed

---

## 4. Step-by-Step Implementation

### 4.1 Phase 1: ServiceNow Integration Setup (ACCOUNTADMIN)

**Duration**: 10-15 minutes
**Role Required**: ACCOUNTADMIN

```sql
-- Step 1: Connect as ACCOUNTADMIN
USE ROLE ACCOUNTADMIN;
USE WAREHOUSE DEV_WH;

-- Step 2: Create Notification Integration
CREATE OR REPLACE NOTIFICATION INTEGRATION SERVICENOW_INTEGRATION
    TYPE = QUEUE
    ENABLED = TRUE
    COMMENT = 'ServiceNow integration for SECURITY_ANALYTICS data warehouse';

-- Step 3: Create API Integration
-- IMPORTANT: Replace with actual ServiceNow instance URL
CREATE OR REPLACE API INTEGRATION SERVICENOW_CONNECTOR
    API_PROVIDER = SERVICENOW
    API_ALLOWED_PREFIXES = ('https://GenericCorp-CompanyX.service-now.com')
    ENABLED = TRUE
    COMMENT = 'ServiceNow API integration for incident, CMDB, and vulnerability data';

-- Step 4: Verify integrations created
SHOW INTEGRATIONS LIKE 'SERVICENOW%';
```

**Verification**:
- ✅ SERVICENOW_INTEGRATION shows ENABLED = true
- ✅ SERVICENOW_CONNECTOR shows ENABLED = true

### 4.2 Phase 2: Deploy Landing Layer (SYSADMIN)

**Duration**: 5-10 minutes
**Role Required**: SYSADMIN

```bash
# Execute SQL script (Landing Layer section)
snowsql -r SYSADMIN -f SERVICENOW_INTEGRATION_IMPLEMENTATION.sql --start-phase=2 --end-phase=2
```

**Manual Alternative** (Snowflake Web UI):
1. Open [SERVICENOW_INTEGRATION_IMPLEMENTATION.sql](../../01_SQL_SCRIPTS/03_Enhancements/SERVICENOW_INTEGRATION_IMPLEMENTATION.sql)
2. Copy **PHASE 2** section (lines 63-305)
3. Execute in Snowflake Web UI Worksheet as SYSADMIN

**Verification**:
```sql
-- Check tables created
SELECT TABLE_NAME, ROW_COUNT, BYTES
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND TABLE_CATALOG = 'DEV_LANDING'
  AND TABLE_NAME LIKE 'L_SNOW_%'
ORDER BY TABLE_NAME;

-- Expected: 6 tables with 0 rows (not yet loaded)
```

### 4.3 Phase 3: Deploy Transformation Layer (SYSADMIN)

**Duration**: 10-15 minutes
**Role Required**: SYSADMIN

```bash
# Execute SQL script (Transformation Layer section)
snowsql -r SYSADMIN -f SERVICENOW_INTEGRATION_IMPLEMENTATION.sql --start-phase=3 --end-phase=3
```

**Verification**:
```sql
-- Check dimensions created
SELECT TABLE_NAME, COMMENT
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND TABLE_CATALOG = 'DEV_TRANSFORMATION'
  AND TABLE_NAME LIKE 'DIM_SNOW_%'
ORDER BY TABLE_NAME;

-- Expected: 3 dimension tables
```

### 4.4 Phase 4: Deploy ETL Procedures (SYSADMIN)

**Duration**: 5 minutes
**Role Required**: SYSADMIN

```bash
# Execute SQL script (Stored Procedures section)
snowsql -r SYSADMIN -f SERVICENOW_INTEGRATION_IMPLEMENTATION.sql --start-phase=4 --end-phase=4
```

**Verification**:
```sql
-- Check procedures created
SELECT PROCEDURE_NAME, ARGUMENT_SIGNATURE, COMMENT
FROM INFORMATION_SCHEMA.PROCEDURES
WHERE PROCEDURE_SCHEMA = 'SECURITY_ANALYTICS'
  AND PROCEDURE_CATALOG = 'DEV_TRANSFORMATION'
  AND PROCEDURE_NAME LIKE '%SNOW%'
ORDER BY PROCEDURE_NAME;

-- Expected: 5 procedures
```

### 4.5 Phase 5: Create Scheduled Tasks (SYSADMIN)

**Duration**: 5 minutes
**Role Required**: SYSADMIN

```bash
# Execute SQL script (Tasks section)
snowsql -r SYSADMIN -f SERVICENOW_INTEGRATION_IMPLEMENTATION.sql --start-phase=5 --end-phase=5
```

**Verification**:
```sql
-- Check tasks created (should be SUSPENDED initially)
SELECT NAME, STATE, SCHEDULE, WAREHOUSE
FROM INFORMATION_SCHEMA.TASKS
WHERE SCHEMA_NAME = 'SECURITY_ANALYTICS'
  AND NAME LIKE '%SNOW%'
ORDER BY NAME;

-- Expected: 3 tasks in SUSPENDED state
```

### 4.6 Phase 6: Create Monitoring Views (SYSADMIN)

**Duration**: 2 minutes
**Role Required**: SYSADMIN

```bash
# Execute SQL script (Monitoring Views section)
snowsql -r SYSADMIN -f SERVICENOW_INTEGRATION_IMPLEMENTATION.sql --start-phase=6 --end-phase=6
```

**Verification**:
```sql
-- Check views created
SELECT TABLE_NAME, COMMENT
FROM INFORMATION_SCHEMA.VIEWS
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
  AND TABLE_CATALOG = 'DEV_REPORTING'
  AND TABLE_NAME LIKE '%SERVICENOW%'
ORDER BY TABLE_NAME;

-- Expected: 2 views
```

### 4.7 Phase 7: Activate Tasks (ACCOUNTADMIN)

**Duration**: 2 minutes
**Role Required**: ACCOUNTADMIN

```sql
USE ROLE ACCOUNTADMIN;

-- Grant EXECUTE TASK privilege (if not already granted)
GRANT EXECUTE TASK ON ACCOUNT TO ROLE SYSADMIN;

-- Resume tasks in reverse dependency order
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_LOAD_DIM_SNOW_INCIDENT RESUME;
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_LOAD_DIM_SNOW_DEVICE RESUME;
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_CALCULATE_SERVICENOW_KPIS RESUME;
```

**Verification**:
```sql
-- Check tasks are now STARTED
SELECT NAME, STATE, NEXT_SCHEDULED_TIME
FROM INFORMATION_SCHEMA.TASKS
WHERE SCHEMA_NAME = 'SECURITY_ANALYTICS'
  AND NAME LIKE '%SNOW%'
ORDER BY NAME;

-- Expected: 3 tasks in STARTED state with NEXT_SCHEDULED_TIME populated
```

### 4.8 Phase 8: Initial Data Load and Validation

**Duration**: 30-60 minutes (depending on data volume)
**Role Required**: SYSADMIN

```sql
-- Manually trigger first load (optional - tasks will run on schedule)
EXECUTE TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_LOAD_DIM_SNOW_INCIDENT;
EXECUTE TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_LOAD_DIM_SNOW_DEVICE;

-- Wait 10-15 minutes, then check execution history
SELECT
    NAME,
    STATE,
    SCHEDULED_TIME,
    COMPLETED_TIME,
    ERROR_MESSAGE,
    ERROR_CODE
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    SCHEDULED_TIME_RANGE_START => DATEADD('hour', -1, CURRENT_TIMESTAMP())
))
WHERE DATABASE_NAME = 'DEV_TRANSFORMATION'
  AND SCHEMA_NAME = 'SECURITY_ANALYTICS'
  AND NAME LIKE '%SNOW%'
ORDER BY SCHEDULED_TIME DESC;

-- Expected: STATE = 'SUCCEEDED', no ERROR_MESSAGE
```

---

## 5. Post-Implementation Validation

### 5.1 Data Flow Validation

```sql
-- Check data in all 3 layers
SELECT
    'LANDING' AS LAYER,
    'L_SNOW_INCIDENTS' AS TABLE_NAME,
    COUNT(*) AS ROW_COUNT,
    MAX(LOAD_TIMESTAMP) AS LAST_REFRESH
FROM DEV_LANDING.SECURITY_ANALYTICS.L_SNOW_INCIDENTS

UNION ALL

SELECT
    'LANDING' AS LAYER,
    'L_SNOW_CMDB_CI' AS TABLE_NAME,
    COUNT(*) AS ROW_COUNT,
    MAX(LOAD_TIMESTAMP) AS LAST_REFRESH
FROM DEV_LANDING.SECURITY_ANALYTICS.L_SNOW_CMDB_CI

UNION ALL

SELECT
    'TRANSFORMATION' AS LAYER,
    'DIM_SNOW_INCIDENT' AS TABLE_NAME,
    COUNT(*) AS ROW_COUNT,
    MAX(UPDATED_AT) AS LAST_REFRESH
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_SNOW_INCIDENT
WHERE IS_CURRENT = TRUE

UNION ALL

SELECT
    'TRANSFORMATION' AS LAYER,
    'DIM_SNOW_DEVICE' AS TABLE_NAME,
    COUNT(*) AS ROW_COUNT,
    MAX(UPDATED_AT) AS LAST_REFRESH
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_SNOW_DEVICE
WHERE IS_CURRENT = TRUE

UNION ALL

SELECT
    'REPORTING' AS LAYER,
    'TBL_KPI_MASTER (ServiceNow)' AS TABLE_NAME,
    COUNT(*) AS ROW_COUNT,
    MAX(UPDATED_AT) AS LAST_REFRESH
FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_KPI_MASTER
WHERE DATA_SOURCE LIKE '%ServiceNow%';
```

**Expected Results**:
- Landing tables: > 0 rows, LAST_REFRESH within last 4 hours
- Transformation dimensions: > 0 rows, LAST_REFRESH within last 4 hours
- Reporting KPIs: 2 rows (KPI_08_MTTR, KPI_01_ASSET_INVENTORY)

### 5.2 Integration Health Check

```sql
-- View comprehensive health status
SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_SERVICENOW_INTEGRATION_HEALTH;
```

**Expected Values**:
- OVERALL_STATUS = 'HEALTHY'
- HOURS_SINCE_INCIDENT_REFRESH < 24
- HOURS_SINCE_DEVICE_REFRESH < 48
- CURRENT_INCIDENTS > 0
- CURRENT_DEVICES > 0

### 5.3 KPI Validation

```sql
-- View ServiceNow KPIs
SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_SERVICENOW_KPI_SUMMARY;
```

**Expected KPIs**:
1. KPI_01_ASSET_INVENTORY - Value between 0-100%
2. KPI_08_MTTR - Value > 0 (hours)

### 5.4 Task Execution History

```sql
-- Check last 7 days of task runs
SELECT
    NAME,
    STATE,
    SCHEDULED_TIME,
    COMPLETED_TIME,
    DATEDIFF('second', SCHEDULED_TIME, COMPLETED_TIME) AS DURATION_SECONDS,
    ERROR_MESSAGE
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    SCHEDULED_TIME_RANGE_START => DATEADD('day', -7, CURRENT_TIMESTAMP())
))
WHERE DATABASE_NAME = 'DEV_TRANSFORMATION'
  AND SCHEMA_NAME = 'SECURITY_ANALYTICS'
  AND NAME LIKE '%SNOW%'
ORDER BY SCHEDULED_TIME DESC
LIMIT 50;
```

**Health Criteria**:
- ✅ SUCCESS rate > 98%
- ✅ DURATION_SECONDS < 600 (10 minutes)
- ✅ No recurring ERROR_MESSAGE patterns

---

## 6. Monitoring and Maintenance

### 6.1 Daily Monitoring

**Dashboard**: [VW_SERVICENOW_INTEGRATION_HEALTH](../../08_POWERBI_DASHBOARDS/02_Security_Operations/ServiceNow_Integration_Health.pbix)

**Key Metrics**:
1. Data freshness (hours since last refresh)
2. Record counts (Landing vs Transformation)
3. Task success rate
4. KPI calculation status

**Alert Thresholds**:
- ⚠️ WARNING: Data refresh > 24 hours (incidents) or > 48 hours (devices)
- 🔴 CRITICAL: Data refresh > 48 hours or task failures

### 6.2 Weekly Maintenance

**Tasks**:
1. Review task execution history for anomalies
2. Validate KPI trends and accuracy
3. Check for data quality issues
4. Verify ServiceNow API token expiration dates

**SQL Query**:
```sql
-- Weekly health check (run every Monday)
SELECT
    CURRENT_DATE() AS REPORT_DATE,

    -- Task Success Rate (Last 7 Days)
    ROUND(
        SUM(CASE WHEN STATE = 'SUCCEEDED' THEN 1 ELSE 0 END) * 100.0 /
        NULLIF(COUNT(*), 0),
        2
    ) AS TASK_SUCCESS_PCT,

    -- Average Task Duration
    ROUND(AVG(DATEDIFF('second', SCHEDULED_TIME, COMPLETED_TIME)), 2) AS AVG_DURATION_SEC,

    -- Total Runs
    COUNT(*) AS TOTAL_RUNS,

    -- Failures
    SUM(CASE WHEN STATE != 'SUCCEEDED' THEN 1 ELSE 0 END) AS FAILURE_COUNT
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    SCHEDULED_TIME_RANGE_START => DATEADD('day', -7, CURRENT_TIMESTAMP())
))
WHERE DATABASE_NAME = 'DEV_TRANSFORMATION'
  AND SCHEMA_NAME = 'SECURITY_ANALYTICS'
  AND NAME LIKE '%SNOW%';
```

### 6.3 Monthly Review

**Checklist**:
- [ ] Review ServiceNow API usage and rate limits
- [ ] Validate KPI accuracy with ServiceNow admins
- [ ] Check for new ServiceNow tables to integrate
- [ ] Review storage growth and optimize if needed
- [ ] Update documentation with any changes

---

## 7. Troubleshooting

### 7.1 Common Issues

#### **Issue 1: Landing Tables Empty**

**Symptoms**:
- L_SNOW_* tables have 0 rows
- VW_SERVICENOW_INTEGRATION_HEALTH shows NULL for LAST_*_REFRESH

**Diagnosis**:
```sql
-- Check Snowflake Connector status
SHOW INTEGRATIONS LIKE 'SERVICENOW%';

-- Check for errors in integration history
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.INTEGRATION_HISTORY
WHERE INTEGRATION_NAME = 'SERVICENOW_CONNECTOR'
ORDER BY START_TIME DESC
LIMIT 10;
```

**Resolution**:
1. Verify ServiceNow API credentials are correct
2. Ensure ServiceNow instance URL is accessible from Snowflake
3. Check ServiceNow API permissions for required tables
4. Re-create integration with corrected parameters

#### **Issue 2: Task Failures**

**Symptoms**:
- TASK_HISTORY shows STATE = 'FAILED'
- ERROR_MESSAGE indicates SQL errors

**Diagnosis**:
```sql
-- View detailed error messages
SELECT
    NAME,
    SCHEDULED_TIME,
    ERROR_MESSAGE,
    ERROR_CODE,
    QUERY_TEXT
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    SCHEDULED_TIME_RANGE_START => DATEADD('hour', -24, CURRENT_TIMESTAMP())
))
WHERE DATABASE_NAME = 'DEV_TRANSFORMATION'
  AND SCHEMA_NAME = 'SECURITY_ANALYTICS'
  AND STATE = 'FAILED'
ORDER BY SCHEDULED_TIME DESC;
```

**Resolution**:
1. Review ERROR_MESSAGE for specific issue
2. Common fixes:
   - **Warehouse not available**: Resume DEV_WH warehouse
   - **Table not found**: Re-run Phase 2 or 3 deployment
   - **Permission denied**: Grant necessary privileges to SYSADMIN
3. Manually test stored procedure:
   ```sql
   CALL DEV_TRANSFORMATION.SECURITY_ANALYTICS.SP_LOAD_DIM_SNOW_INCIDENT_INCREMENTAL();
   ```

#### **Issue 3: Data Not Refreshing**

**Symptoms**:
- HOURS_SINCE_*_REFRESH increasing beyond thresholds
- Tasks show SUCCEEDED but data not updated

**Diagnosis**:
```sql
-- Check if Snowflake Connector is auto-refreshing
SELECT
    TABLE_NAME,
    MAX(LOAD_TIMESTAMP) AS LAST_LOAD,
    COUNT(*) AS TOTAL_ROWS
FROM DEV_LANDING.SECURITY_ANALYTICS.L_SNOW_INCIDENTS
GROUP BY TABLE_NAME;

-- Check ETL_PIPELINE_LOG for issues
SELECT *
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.ETL_PIPELINE_LOG
WHERE PIPELINE_NAME LIKE '%SNOW%'
ORDER BY EXECUTED_AT DESC
LIMIT 20;
```

**Resolution**:
1. Verify Snowflake Connector refresh intervals
2. Check ServiceNow API rate limits not exceeded
3. Review ETL logic for filtering issues (e.g., SYS_UPDATED_ON filter)

### 7.2 Emergency Contacts

| Issue Type | Contact | Email |
|------------|---------|-------|
| Snowflake Access | Snowflake Admins | snowflake-admins@GenericCorp.com |
| ServiceNow API | ServiceNow Admins | servicenow-team@GenericCorp.com |
| Data Quality | Data Engineering | data-engineering@GenericCorp.com |
| BI Dashboard Issues | BI Team | bi-team@GenericCorp.com |

---

## 8. Rollback Procedures

### 8.1 Full Rollback (Remove All ServiceNow Integration)

**Use Case**: Critical issues, need to revert to pre-integration state

**Steps**:

```sql
-- Step 1: Suspend all ServiceNow tasks
USE ROLE ACCOUNTADMIN;
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_LOAD_DIM_SNOW_INCIDENT SUSPEND;
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_LOAD_DIM_SNOW_DEVICE SUSPEND;
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_CALCULATE_SERVICENOW_KPIS SUSPEND;

-- Step 2: Drop all ServiceNow objects
USE ROLE SYSADMIN;

-- Drop tasks
DROP TASK IF EXISTS DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_LOAD_DIM_SNOW_INCIDENT;
DROP TASK IF EXISTS DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_LOAD_DIM_SNOW_DEVICE;
DROP TASK IF EXISTS DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_CALCULATE_SERVICENOW_KPIS;

-- Drop procedures
DROP PROCEDURE IF EXISTS DEV_TRANSFORMATION.SECURITY_ANALYTICS.SP_LOAD_DIM_SNOW_INCIDENT_INCREMENTAL();
DROP PROCEDURE IF EXISTS DEV_TRANSFORMATION.SECURITY_ANALYTICS.SP_LOAD_DIM_SNOW_DEVICE_INCREMENTAL();
DROP PROCEDURE IF EXISTS DEV_TRANSFORMATION.SECURITY_ANALYTICS.SP_CALCULATE_KPI_INCIDENT_MTTR();
DROP PROCEDURE IF EXISTS DEV_TRANSFORMATION.SECURITY_ANALYTICS.SP_CALCULATE_KPI_ASSET_INVENTORY();

-- Drop views
DROP VIEW IF EXISTS DEV_REPORTING.SECURITY_ANALYTICS.VW_SERVICENOW_INTEGRATION_HEALTH;
DROP VIEW IF EXISTS DEV_REPORTING.SECURITY_ANALYTICS.VW_SERVICENOW_KPI_SUMMARY;

-- Drop transformation tables
DROP TABLE IF EXISTS DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_SNOW_INCIDENT;
DROP TABLE IF EXISTS DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_SNOW_DEVICE;
DROP TABLE IF EXISTS DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_SNOW_CHANGE;

-- Drop landing tables
DROP TABLE IF EXISTS DEV_LANDING.SECURITY_ANALYTICS.L_SNOW_INCIDENTS;
DROP TABLE IF EXISTS DEV_LANDING.SECURITY_ANALYTICS.L_SNOW_CMDB_CI;
DROP TABLE IF EXISTS DEV_LANDING.SECURITY_ANALYTICS.L_SNOW_CHANGES;
DROP TABLE IF EXISTS DEV_LANDING.SECURITY_ANALYTICS.L_SNOW_USERS;
DROP TABLE IF EXISTS DEV_LANDING.SECURITY_ANALYTICS.L_SNOW_PROBLEMS;
DROP TABLE IF EXISTS DEV_LANDING.SECURITY_ANALYTICS.L_SNOW_VULNERABILITIES;

-- Step 3: Remove integrations (ACCOUNTADMIN only)
USE ROLE ACCOUNTADMIN;
DROP API INTEGRATION IF EXISTS SERVICENOW_CONNECTOR;
DROP NOTIFICATION INTEGRATION IF EXISTS SERVICENOW_INTEGRATION;

-- Step 4: Clean up KPI entries
USE ROLE SYSADMIN;
DELETE FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_KPI_MASTER
WHERE DATA_SOURCE LIKE '%ServiceNow%';
```

**Verification**:
```sql
-- Confirm all ServiceNow objects removed
SELECT 'LANDING_TABLES' AS OBJECT_TYPE, COUNT(*) AS COUNT
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_CATALOG = 'DEV_LANDING' AND TABLE_NAME LIKE 'L_SNOW_%'

UNION ALL

SELECT 'TRANSFORMATION_DIMS', COUNT(*)
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_CATALOG = 'DEV_TRANSFORMATION' AND TABLE_NAME LIKE 'DIM_SNOW_%'

UNION ALL

SELECT 'PROCEDURES', COUNT(*)
FROM INFORMATION_SCHEMA.PROCEDURES
WHERE PROCEDURE_NAME LIKE '%SNOW%'

UNION ALL

SELECT 'TASKS', COUNT(*)
FROM INFORMATION_SCHEMA.TASKS
WHERE NAME LIKE '%SNOW%'

UNION ALL

SELECT 'INTEGRATIONS', COUNT(*)
FROM INFORMATION_SCHEMA.INTEGRATIONS
WHERE NAME LIKE 'SERVICENOW%';

-- Expected: All counts = 0
```

### 8.2 Partial Rollback (Disable Integration, Keep Objects)

**Use Case**: Temporary issues, plan to re-enable later

**Steps**:

```sql
-- Suspend tasks only
USE ROLE ACCOUNTADMIN;
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_LOAD_DIM_SNOW_INCIDENT SUSPEND;
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_LOAD_DIM_SNOW_DEVICE SUSPEND;
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_CALCULATE_SERVICENOW_KPIS SUSPEND;

-- Disable integration
ALTER API INTEGRATION SERVICENOW_CONNECTOR SET ENABLED = FALSE;

-- All objects remain, data is preserved
```

**Re-enable**:
```sql
-- Re-enable integration and tasks when ready
USE ROLE ACCOUNTADMIN;
ALTER API INTEGRATION SERVICENOW_CONNECTOR SET ENABLED = TRUE;
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_LOAD_DIM_SNOW_INCIDENT RESUME;
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_LOAD_DIM_SNOW_DEVICE RESUME;
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_CALCULATE_SERVICENOW_KPIS RESUME;
```

---

## Appendix A: Cost Analysis

### Monthly Cost Breakdown

```
Snowflake Connector (Included):
- Connector License: $0 (included in Snowflake)
- Compute (incremental):
  - 6 refreshes/day × 5 min × $4/hour (X-Small) = $2/day
  - Monthly: $2 × 30 = $60
- Storage (incremental):
  - 50 GB/year @ $40/TB/month = $2/month

Total Monthly Cost: $62/month ($744/year)

Alternative (Azure Data Factory):
- ADF Pipeline Execution: $10.80/year
- Data Movement (DIU): $453.60/year
- Azure Blob Staging: $12/year
- Snowflake External Stage: $720/year
Total: $1,196/year

Savings with Snowflake Connector: $452/year (38%)
```

---

## Appendix B: ServiceNow Table Mappings

| ServiceNow Field | Snowflake Column | Data Type | Transform |
|------------------|------------------|-----------|-----------|
| sys_id | SYS_ID | VARCHAR(32) | Direct |
| number | NUMBER | VARCHAR(40) | Direct |
| short_description | SHORT_DESCRIPTION | VARCHAR(160) | Direct |
| state | STATE | VARCHAR(2) | Direct |
| priority | PRIORITY | NUMBER | CAST |
| opened_at | OPENED_AT | TIMESTAMP_NTZ | CONVERT_TIMEZONE |
| resolved_at | RESOLVED_AT | TIMESTAMP_NTZ | CONVERT_TIMEZONE |
| sys_updated_on | SYS_UPDATED_ON | TIMESTAMP_NTZ | CONVERT_TIMEZONE |

---

## Appendix C: API Rate Limits

| API Endpoint | Rate Limit | Snowflake Impact |
|--------------|------------|------------------|
| ServiceNow Table API | 5,000 requests/hour | Low (6 table refreshes × 6/day = 36 requests/day) |
| ServiceNow REST API v2 | 10,000 requests/hour | Low (incremental queries) |

**Mitigation**:
- Snowflake Connector uses efficient incremental queries
- Only pulls records modified since last refresh (SYS_UPDATED_ON filter)
- Recommended refresh: Every 2-4 hours (not real-time)

---

**Document Version**: 1.0
**Last Updated**: 2025-10-21
**Status**: Ready for Production
**Review**: Approved by Data Engineering & Security Teams

---

**END OF DOCUMENT**
