# Deployment Guide

Complete step-by-step guide for deploying the SECURITY_ANALYTICS Data Warehouse to Snowflake.

[[← Back to Home|Home]]

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Deployment Steps](#deployment-steps)
4. [Post-Deployment Validation](#post-deployment-validation)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Access

- ✅ Snowflake account with **ACCOUNTADMIN** privileges (for initial setup)
- ✅ Snowflake account with **SYSADMIN** role (for ongoing deployments)
- ✅ Azure DevOps access (Contributor or higher)
- ✅ Python 3.13 or higher installed locally

### Required Tools

```bash
# Python
python --version  # Should be 3.13+

# Git
git --version

# Snowflake CLI (optional but recommended)
snowsql --version
```

### Snowflake Prerequisites

Before deployment, ensure the following exist in your Snowflake account:

1. **Warehouses**: `DEV_WH` (X-Small), `REPORTING_WH` (Small)
2. **Databases**: `DEV_LANDING`, `DEV_TRANSFORMATION`, `DEV_REPORTING`
3. **Role**: `SECURITY_ANALYTICS` with appropriate grants
4. **User**: Service account for automation

---

## Environment Setup

### Step 1: Clone Repository

```bash
# Clone from Azure DevOps
git clone https://dev.azure.com/CompanyX/GIS-SECURITY_ANALYTICS-DW/_git/GIS-SECURITY_ANALYTICS-DW
cd GIS-SECURITY_ANALYTICS-DW
```

### Step 2: Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Snowflake Connection

```bash
# Copy environment template
cp .env.example .env
```

Edit `.env` file:

```bash
# Snowflake Connection
SNOWFLAKE_ACCOUNT=your_account.region
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=DEV_WH
SNOWFLAKE_ROLE=SECURITY_ANALYTICS
SNOWFLAKE_DATABASE=DEV_LANDING

# Optional
SNOWFLAKE_SCHEMA=SECURITY_ANALYTICS
```

### Step 4: Test Connection

```bash
python 02_PYTHON_SCRIPTS/test_connection.py
```

Expected output:
```
✓ Connected to Snowflake successfully
  Account: your_account
  User: your_username
  Role: SECURITY_ANALYTICS
  Warehouse: DEV_WH
```

---

## Deployment Steps

### Phase 1: Prerequisites Check (5 minutes)

**Script**: `01_SQL_SCRIPTS/01_Prerequisites/00_PREREQUISITES_CHECK.sql`

```bash
# Using SnowSQL
snowsql -f 01_SQL_SCRIPTS/01_Prerequisites/00_PREREQUISITES_CHECK.sql

# OR using Python
python 02_PYTHON_SCRIPTS/execute_pipeline_deployment.py --script prerequisites
```

**What it does**:
- Verifies warehouses exist
- Checks database permissions
- Validates role grants
- Confirms schema structure

**Expected Result**: All checks pass ✅

---

### Phase 2: Base Implementation (30-45 minutes)

Deploy core data model (dimensions + facts).

#### Step 2.1: Core Data Model

**Script**: `01_SQL_SCRIPTS/02_Base_Implementation/ITSECKPI_MODEL_IMPLEMENTATION_CORRECTED.sql`

```bash
snowsql -f 01_SQL_SCRIPTS/02_Base_Implementation/ITSECKPI_MODEL_IMPLEMENTATION_CORRECTED.sql
```

**Creates**:
- 32 Dimension tables (DIM_*)
- 23 Fact tables (FACT_*)
- Primary keys and constraints

**Duration**: ~25 minutes

#### Step 2.2: Advanced Features

**Script**: `01_SQL_SCRIPTS/02_Base_Implementation/ADVANCED_IMPLEMENTATION_CORRECTED.sql`

```bash
snowsql -f 01_SQL_SCRIPTS/02_Base_Implementation/ADVANCED_IMPLEMENTATION_CORRECTED.sql
```

**Creates**:
- SCD Type 2 implementation
- Foreign key relationships
- Indexes and clustering keys
- Data quality constraints

**Duration**: ~15 minutes

---

### Phase 3: Top 13 Executive Metrics (20-30 minutes)

**Script**: `01_SQL_SCRIPTS/03_Enhancements/EXECUTE_4_ENHANCEMENTS_WORKING.sql`

```bash
snowsql -f 01_SQL_SCRIPTS/03_Enhancements/EXECUTE_4_ENHANCEMENTS_WORKING.sql
```

**Creates**:
- KPI calculation views
- Monitoring dashboards
- Data quality framework
- Lineage tracking

**Duration**: ~25 minutes

---

### Phase 4: Automation Framework (15-20 minutes)

**Script**: `FINAL_DELIVERABLES/04_SQL_Scripts/COMPLETE_AUTOMATION_FRAMEWORK.sql`

```bash
snowsql -f FINAL_DELIVERABLES/04_SQL_Scripts/COMPLETE_AUTOMATION_FRAMEWORK.sql
```

**Creates**:
- 19 Stored Procedures
- 21 Functions
- 12 Scheduled Tasks (suspended state)

**Duration**: ~18 minutes

**Note**: Tasks are created in SUSPENDED state - they will NOT run automatically yet.

---

### Phase 5: Task Activation (ACCOUNTADMIN Required)

⚠️ **WARNING**: This step requires **ACCOUNTADMIN** privileges.

**Script**: `FINAL_DELIVERABLES/04_SQL_Scripts/activate_tasks_admin.sql`

```bash
# Switch to ACCOUNTADMIN role first
snowsql -f FINAL_DELIVERABLES/04_SQL_Scripts/activate_tasks_admin.sql
```

**What it does**:
- Activates all 12 scheduled tasks
- Sets up task dependencies
- Configures execution schedules

**Duration**: ~5 minutes

**Verification**:
```sql
-- Check task status
SELECT
    name,
    state,
    schedule,
    next_scheduled_time
FROM INFORMATION_SCHEMA.TASK_HISTORY
WHERE database_name = 'DEV_TRANSFORMATION'
ORDER BY name;
```

---

### Phase 6: ServiceNow Integration (Optional)

If integrating with ServiceNow CMDB:

**Script**: `01_SQL_SCRIPTS/03_Enhancements/SERVICENOW_INTEGRATION_IMPLEMENTATION.sql`

```bash
snowsql -f 01_SQL_SCRIPTS/03_Enhancements/SERVICENOW_INTEGRATION_IMPLEMENTATION.sql
```

**Creates**:
- 6 Landing tables for ServiceNow data
- 3 ServiceNow dimensions
- 5 ETL procedures
- 3 Scheduled tasks

**Duration**: ~40 minutes

---

## Post-Deployment Validation

### Validation Step 1: Object Count

```sql
-- Count objects by layer
SELECT
    table_catalog AS database,
    COUNT(*) AS object_count
FROM INFORMATION_SCHEMA.TABLES
WHERE table_schema = 'SECURITY_ANALYTICS'
GROUP BY table_catalog
ORDER BY table_catalog;
```

**Expected Results**:
- DEV_LANDING: 141 tables
- DEV_TRANSFORMATION: 55 tables, 32 dimensions, 23 facts
- DEV_REPORTING: 148 views, 18 tables

### Validation Step 2: Task Status

```sql
-- Verify tasks are running
SELECT
    name,
    state,
    schedule,
    last_run_at,
    last_run_status
FROM DEV_TRANSFORMATION.INFORMATION_SCHEMA.TASKS
ORDER BY name;
```

**Expected**: All tasks show `state = STARTED`

### Validation Step 3: Data Quality Score

```sql
-- Check data quality metrics
SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_DATA_QUALITY_SUMMARY
ORDER BY quality_score DESC;
```

**Expected**: Overall quality score > 70%

### Validation Step 4: Sample Query

```sql
-- Test a KPI query
SELECT
    metric_name,
    metric_value,
    target_value,
    status
FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_TOP13_KPI_SUMMARY
WHERE metric_category = 'Protect'
ORDER BY metric_name;
```

**Expected**: Returns 3 metrics (Patch Compliance, EDR Coverage, MFA Adoption)

---

## Deployment Checklist

Use this checklist to track deployment progress:

- [ ] Prerequisites verified
- [ ] Python environment configured
- [ ] Snowflake connection tested
- [ ] Base implementation deployed (Phase 2.1)
- [ ] Advanced features deployed (Phase 2.2)
- [ ] Top 13 KPIs deployed (Phase 3)
- [ ] Automation framework deployed (Phase 4)
- [ ] Tasks activated (Phase 5)
- [ ] ServiceNow integration deployed (Phase 6 - optional)
- [ ] Object count validation passed
- [ ] Task status validation passed
- [ ] Data quality validation passed
- [ ] Sample queries tested
- [ ] Documentation updated
- [ ] Team notified

---

## Rollback Procedures

### Emergency Rollback

If deployment fails critically:

```sql
-- Suspend all tasks immediately
USE ROLE ACCOUNTADMIN;
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_LOAD_DIMENSIONS SUSPEND;
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_LOAD_FACTS SUSPEND;
-- ... suspend all other tasks

-- Drop failed objects (example)
DROP TABLE IF EXISTS DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_PROBLEMATIC_TABLE;
```

### Partial Rollback

To rollback specific phase:

```bash
# Restore from backup (if available)
snowsql -f backup/restore_point_YYYYMMDD.sql
```

---

## Deployment Times Summary

| Phase | Duration | Role Required |
|-------|----------|---------------|
| Prerequisites | 5 min | SYSADMIN |
| Base Implementation | 40 min | SYSADMIN |
| Top 13 KPIs | 25 min | SYSADMIN |
| Automation Framework | 18 min | SYSADMIN |
| Task Activation | 5 min | **ACCOUNTADMIN** |
| ServiceNow (optional) | 40 min | SYSADMIN |
| **Total** | **2-2.5 hours** | |

---

## Next Steps After Deployment

1. **Monitor Task Execution** (24-48 hours)
   - Check `INFORMATION_SCHEMA.TASK_HISTORY`
   - Review error logs in `ETL_PIPELINE_LOG`

2. **Set Up Streamlit Dashboards**
   - Deploy apps from `07_STREAMLIT_APPS/`
   - Configure Streamlit secrets

3. **Configure Power BI**
   - Connect to `DEV_REPORTING` views
   - Import dashboard templates from `10_POWERBI_DASHBOARDS/`

4. **User Training**
   - Schedule team walkthrough
   - Share documentation wiki
   - Set up access controls

5. **Ongoing Maintenance**
   - Weekly data quality reviews
   - Monthly performance tuning
   - Quarterly KPI review with stakeholders

---

## Support

For deployment issues:

1. **Check**: [[Troubleshooting|Troubleshooting]] wiki page
2. **Search**: Azure DevOps work items for similar issues
3. **Create**: New work item with `deployment` tag
4. **Escalate**: Tag project owner if critical

---

[[← Back to Home|Home]] | [[Next: Troubleshooting →|Troubleshooting]]
