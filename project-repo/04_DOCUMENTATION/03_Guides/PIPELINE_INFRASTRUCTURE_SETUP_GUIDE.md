# Data Pipeline Infrastructure Setup Guide
## SECURITY_ANALYTICS Snowflake Data Warehouse

**Author:** Data Engineering Team
**Date:** 2025-10-07
**Version:** 1.0

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [AWS S3 Configuration](#aws-s3-configuration)
4. [Azure Blob Storage Configuration](#azure-blob-storage-configuration)
5. [Snowflake Deployment](#snowflake-deployment)
6. [Snowpipe Event Notification Setup](#snowpipe-event-notification-setup)
7. [Task Activation](#task-activation)
8. [Monitoring and Validation](#monitoring-and-validation)
9. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

The SECURITY_ANALYTICS data pipeline uses a **hybrid ingestion architecture**:

### Real-Time Ingestion (Snowpipe)
- **CrowdStrike EDR** → S3 → Snowpipe → L_CROWDSTRIKE_RAW
- **SentinelOne** → S3 → Snowpipe → L_SENTINELONE_RAW
- **Qualys Scans** → S3 → Snowpipe → L_QUALYS_SCANS_RAW
- **Proofpoint Logs** → Azure Blob → Snowpipe → L_PROOFPOINT_RAW
- **Splunk Alerts** → S3 → Snowpipe → L_SPLUNK_ALERTS_RAW

### Batch Ingestion (External Tables + Tasks)
- **ServiceNow Incidents** → S3 → External Table → Daily Task
- **RSA Archer GRC** → S3 → External Table → Daily Task
- **MetaCompliance** → S3 → External Table → Daily Task

### Processing Layer
- **Streams** → Track changes in landing tables (CDC)
- **Tasks** → Scheduled/event-driven transformations
- **Stored Procedures** → Business logic execution

---

## Prerequisites

### Snowflake Requirements

✅ **Role Privileges:**
- `ACCOUNTADMIN` role (for Storage Integrations and Task execution)
- `DEV_DEVELOPER` role (for object creation)

✅ **Warehouse:**
- `DEV_WH` warehouse with AUTO_SUSPEND and AUTO_RESUME enabled

✅ **Databases:**
- `DEV_LANDING` - Raw data landing zone
- `DEV_TRANSFORMATION` - Business logic and star schema
- `DEV_REPORTING` - Power BI semantic layer

### Cloud Provider Requirements

✅ **AWS Account:**
- S3 buckets for data sources
- IAM roles for Snowflake access
- SNS topics for event notifications

✅ **Azure Account (if using Azure Blob):**
- Azure Storage Account
- Service Principal for Snowflake
- Event Grid for notifications

### Data Source Requirements

✅ **EDR Platforms:**
- API keys for CrowdStrike, SentinelOne, Defender
- Export configurations to S3/Azure Blob

✅ **Vulnerability Management:**
- Qualys API access
- Scheduled export jobs

✅ **Email Security:**
- Proofpoint log aggregation enabled
- Azure Blob export configured

---

## AWS S3 Configuration

### Step 1: Create S3 Buckets

```bash
# Create buckets for each data source
aws s3 mb s3://GenericCorp-security-data --region us-east-1

# Create folder structure
aws s3api put-object --bucket GenericCorp-security-data --key edr/crowdstrike/
aws s3api put-object --bucket GenericCorp-security-data --key edr/sentinelone/
aws s3api put-object --bucket GenericCorp-security-data --key edr/defender/
aws s3api put-object --bucket GenericCorp-security-data --key edr/cisco-amp/
aws s3api put-object --bucket GenericCorp-security-data --key qualys/scans/
aws s3api put-object --bucket GenericCorp-security-data --key qualys/agents/
aws s3api put-object --bucket GenericCorp-security-data --key splunk/alerts/
aws s3api put-object --bucket GenericCorp-security-data --key servicenow/incidents/
aws s3api put-object --bucket GenericCorp-security-data --key archer/exports/
aws s3api put-object --bucket GenericCorp-security-data --key metacompliance/training/
```

### Step 2: Create IAM Role for Snowflake

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:user/snowflake-user"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "SNOWFLAKE_EXTERNAL_ID"
        }
      }
    }
  ]
}
```

**IAM Policy for S3 Access:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:GetObjectVersion",
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": [
        "arn:aws:s3:::GenericCorp-security-data",
        "arn:aws:s3:::GenericCorp-security-data/*"
      ]
    }
  ]
}
```

### Step 3: Configure S3 Event Notifications (for Snowpipe)

```bash
# Create SNS topic for Snowpipe notifications
aws sns create-topic --name snowpipe-crowdstrike --region us-east-1

# Configure S3 bucket notification
aws s3api put-bucket-notification-configuration \
  --bucket GenericCorp-security-data \
  --notification-configuration file://s3-notification-config.json
```

**s3-notification-config.json:**

```json
{
  "TopicConfigurations": [
    {
      "TopicArn": "arn:aws:sns:us-east-1:123456789012:snowpipe-crowdstrike",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "prefix",
              "Value": "edr/crowdstrike/"
            },
            {
              "Name": "suffix",
              "Value": ".json"
            }
          ]
        }
      }
    }
  ]
}
```

### Step 4: Subscribe Snowpipe to SNS Topic

After creating the Snowpipe in Snowflake, get the SQS queue ARN:

```sql
-- In Snowflake
DESC PIPE PIPE_CROWDSTRIKE_EDR;
-- Copy the notification_channel value (SQS queue ARN)
```

Subscribe SNS topic to Snowflake SQS queue:

```bash
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:snowpipe-crowdstrike \
  --protocol sqs \
  --notification-endpoint <SNOWFLAKE_SQS_ARN>
```

---

## Azure Blob Storage Configuration

### Step 1: Create Storage Account

```bash
# Create resource group
az group create --name GenericCorp-security-rg --location eastus

# Create storage account
az storage account create \
  --name crhsecuritydata \
  --resource-group GenericCorp-security-rg \
  --location eastus \
  --sku Standard_LRS \
  --kind StorageV2

# Create container for Proofpoint
az storage container create \
  --name proofpoint \
  --account-name crhsecuritydata
```

### Step 2: Create Service Principal for Snowflake

```bash
# Create service principal
az ad sp create-for-rbac \
  --name snowflake-integration \
  --role "Storage Blob Data Contributor" \
  --scopes /subscriptions/{subscription-id}/resourceGroups/GenericCorp-security-rg

# Output will include:
# - appId (Application ID)
# - password (Client Secret)
# - tenant (Tenant ID)
```

### Step 3: Grant Snowflake Access to Storage

```sql
-- In Snowflake, create storage integration
CREATE OR REPLACE STORAGE INTEGRATION AZURE_EMAIL_INTEGRATION
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = AZURE
  ENABLED = TRUE
  AZURE_TENANT_ID = '<your-tenant-id>'
  STORAGE_ALLOWED_LOCATIONS = (
    'azure://crhsecuritydata.blob.core.windows.net/proofpoint/'
  );

-- Get the Azure consent URL
DESC STORAGE INTEGRATION AZURE_EMAIL_INTEGRATION;
-- Copy AZURE_CONSENT_URL and open in browser to grant permissions
```

### Step 4: Configure Event Grid (for Snowpipe)

```bash
# Create Event Grid subscription for Snowpipe
az eventgrid event-subscription create \
  --name snowpipe-proofpoint \
  --source-resource-id /subscriptions/{subscription-id}/resourceGroups/GenericCorp-security-rg/providers/Microsoft.Storage/storageAccounts/crhsecuritydata \
  --endpoint <SNOWFLAKE_NOTIFICATION_ENDPOINT> \
  --endpoint-type webhook \
  --included-event-types Microsoft.Storage.BlobCreated
```

---

## Snowflake Deployment

### Step 1: Execute Pipeline Architecture SQL

**Option A: Using Python Script (Recommended)**

```bash
cd C:\\Projects\\Snowflake_ITSECKPI_Project

python execute_pipeline_deployment.py
```

The script will:
- Parse all SQL statements intelligently
- Execute them in order
- Handle procedures and tasks correctly
- Save detailed results to JSON

**Option B: Manual Execution in Snowflake**

1. Open [DATA_PIPELINE_ARCHITECTURE.sql](DATA_PIPELINE_ARCHITECTURE.sql)
2. Execute sections 1-6 first (Storage Integrations, Stages, Tables, Snowpipes, Streams)
3. Execute section 7 (Transformation Procedures)
4. Execute section 8 (Task DAG) - but DO NOT resume tasks yet
5. Execute section 9 (Monitoring)

### Step 2: Update Storage Integration ARNs

After creating storage integrations, get the IAM user ARN:

```sql
DESC STORAGE INTEGRATION S3_EDR_INTEGRATION;
-- Copy STORAGE_AWS_IAM_USER_ARN and STORAGE_AWS_EXTERNAL_ID
```

Update your AWS IAM Trust Policy with the correct ARN and External ID.

### Step 3: Verify Object Creation

```sql
-- Check storage integrations
SHOW INTEGRATIONS;

-- Check file formats
SHOW FILE FORMATS IN SCHEMA DEV_LANDING.SECURITY_ANALYTICS;

-- Check stages
SHOW STAGES IN SCHEMA DEV_LANDING.SECURITY_ANALYTICS;

-- Check pipes
SHOW PIPES IN SCHEMA DEV_LANDING.SECURITY_ANALYTICS;

-- Check streams
SHOW STREAMS IN SCHEMA DEV_LANDING.SECURITY_ANALYTICS;

-- Check tasks
SHOW TASKS IN SCHEMA DEV_TRANSFORMATION.SECURITY_ANALYTICS;
```

---

## Snowpipe Event Notification Setup

### Verification Steps

1. **Upload Test File to S3**

```bash
# Create test JSON file
echo '{"detection_id": "test-001", "device_id": "HOST-001", "created_timestamp": "2025-10-07T10:00:00Z", "behavior": "Malware Detection", "severity": "High", "file_path": "/tmp/test.exe", "process_name": "test.exe"}' > test-crowdstrike.json

# Upload to S3
aws s3 cp test-crowdstrike.json s3://GenericCorp-security-data/edr/crowdstrike/
```

2. **Check Snowpipe Status**

```sql
-- View pipe history
SELECT *
FROM TABLE(INFORMATION_SCHEMA.PIPE_USAGE_HISTORY(
  PIPE_NAME => 'PIPE_CROWDSTRIKE_EDR',
  DATE_RANGE_START => DATEADD('hour', -1, CURRENT_TIMESTAMP())
));

-- Check for errors
SELECT *
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
  TABLE_NAME => 'L_CROWDSTRIKE_RAW',
  START_TIME => DATEADD('hour', -1, CURRENT_TIMESTAMP())
));

-- Verify data landed
SELECT COUNT(*) FROM DEV_LANDING.SECURITY_ANALYTICS.L_CROWDSTRIKE_RAW;
```

3. **Manual Refresh (if auto-ingest not working)**

```sql
-- Manually trigger pipe
ALTER PIPE PIPE_CROWDSTRIKE_EDR REFRESH;

-- Check refresh history
SELECT SYSTEM$PIPE_STATUS('PIPE_CROWDSTRIKE_EDR');
```

---

## Task Activation

### Prerequisites

✅ **Required Privileges:**
- `EXECUTE TASK` privilege on the account
- `ACCOUNTADMIN` role or custom role with task execution rights

### Activation Steps

**⚠ IMPORTANT:** Tasks must be resumed in **reverse dependency order** (children first, root last).

```sql
-- Switch to ACCOUNTADMIN role
USE ROLE ACCOUNTADMIN;

-- Resume child tasks first
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_REFRESH_POWERBI_VIEWS RESUME;
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_CALCULATE_TOP13_METRICS RESUME;
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_INGEST_METACOMPLIANCE RESUME;
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_INGEST_ARCHER RESUME;
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_INGEST_SERVICENOW RESUME;

-- Resume stream-triggered tasks
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_TRANSFORM_QUALYS RESUME;
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_TRANSFORM_SENTINELONE RESUME;
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_TRANSFORM_CROWDSTRIKE RESUME;

-- Resume monitoring tasks
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_WEEKLY_HEALTH_CHECK RESUME;
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_MONITORING_HEALTH_CHECK RESUME;

-- Resume root task LAST
ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_ROOT_DAILY_ORCHESTRATION RESUME;
```

### Verification

```sql
-- Check all tasks are running
SELECT
    NAME,
    STATE,
    SCHEDULE,
    WAREHOUSE,
    PREDECESSORS
FROM INFORMATION_SCHEMA.TASKS
WHERE DATABASE_NAME = 'DEV_TRANSFORMATION'
AND SCHEMA_NAME = 'SECURITY_ANALYTICS'
ORDER BY NAME;

-- All STATE values should be 'started'
```

---

## Monitoring and Validation

### 1. Snowpipe Monitoring

```sql
-- Check pipe status for last 24 hours
SELECT
    PIPE_NAME,
    FILES_LOADED,
    ROWS_LOADED,
    ERROR_COUNT,
    LAST_LOAD_TIME
FROM TABLE(INFORMATION_SCHEMA.PIPE_USAGE_HISTORY(
    DATE_RANGE_START => DATEADD('day', -1, CURRENT_TIMESTAMP())
))
ORDER BY PIPE_NAME, LAST_LOAD_TIME DESC;

-- Check for copy errors
SELECT
    TABLE_NAME,
    FILE_NAME,
    STATUS,
    ERROR_MESSAGE,
    FIRST_ERROR_LINE_NUMBER
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
    TABLE_NAME => 'DEV_LANDING.SECURITY_ANALYTICS.L_CROWDSTRIKE_RAW',
    START_TIME => DATEADD('day', -1, CURRENT_TIMESTAMP())
))
WHERE STATUS = 'LOAD_FAILED';
```

### 2. Stream Monitoring

```sql
-- Check stream lag and offset
SELECT
    TABLE_NAME AS STREAM_NAME,
    SYSTEM$STREAM_HAS_DATA(TABLE_NAME) AS HAS_DATA,
    BYTES,
    ROWS
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
AND TABLE_TYPE = 'STREAM'
AND TABLE_CATALOG = 'DEV_LANDING';
```

### 3. Task Monitoring

```sql
-- Check task execution history (last 7 days)
SELECT
    NAME,
    STATE,
    COMPLETED_TIME,
    SCHEDULED_TIME,
    QUERY_START_TIME,
    ERROR_CODE,
    ERROR_MESSAGE
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    SCHEDULED_TIME_RANGE_START => DATEADD('day', -7, CURRENT_TIMESTAMP())
))
WHERE DATABASE_NAME = 'DEV_TRANSFORMATION'
AND SCHEMA_NAME = 'SECURITY_ANALYTICS'
ORDER BY COMPLETED_TIME DESC;

-- Check for failed tasks
SELECT
    NAME,
    COMPLETED_TIME,
    ERROR_CODE,
    ERROR_MESSAGE
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    SCHEDULED_TIME_RANGE_START => DATEADD('day', -1, CURRENT_TIMESTAMP())
))
WHERE STATE = 'FAILED'
ORDER BY COMPLETED_TIME DESC;
```

### 4. Data Quality Checks

```sql
-- Check landing table row counts
SELECT
    'L_CROWDSTRIKE_RAW' AS TABLE_NAME,
    COUNT(*) AS ROW_COUNT,
    MAX(INGESTION_TIMESTAMP) AS LAST_INGESTION
FROM DEV_LANDING.SECURITY_ANALYTICS.L_CROWDSTRIKE_RAW
UNION ALL
SELECT
    'L_SENTINELONE_RAW',
    COUNT(*),
    MAX(INGESTION_TIMESTAMP)
FROM DEV_LANDING.SECURITY_ANALYTICS.L_SENTINELONE_RAW
UNION ALL
SELECT
    'L_QUALYS_SCANS_RAW',
    COUNT(*),
    MAX(INGESTION_TIMESTAMP)
FROM DEV_LANDING.SECURITY_ANALYTICS.L_QUALYS_SCANS_RAW
UNION ALL
SELECT
    'L_PROOFPOINT_RAW',
    COUNT(*),
    MAX(INGESTION_TIMESTAMP)
FROM DEV_LANDING.SECURITY_ANALYTICS.L_PROOFPOINT_RAW
UNION ALL
SELECT
    'L_SPLUNK_ALERTS_RAW',
    COUNT(*),
    MAX(INGESTION_TIMESTAMP)
FROM DEV_LANDING.SECURITY_ANALYTICS.L_SPLUNK_ALERTS_RAW;

-- Check transformation table row counts
SELECT
    'FACT_EDR' AS TABLE_NAME,
    COUNT(*) AS ROW_COUNT
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_EDR
UNION ALL
SELECT
    'FACT_QUALYS',
    COUNT(*)
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_QUALYS;
```

### 5. Pipeline Health Dashboard

```sql
-- Query monitoring table
SELECT
    CHECK_TIMESTAMP,
    PIPELINE_NAME,
    PIPELINE_TYPE,
    STATUS,
    ROWS_PROCESSED,
    LAG_MINUTES,
    ERROR_MESSAGE
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.TBL_PIPELINE_MONITORING
ORDER BY CHECK_TIMESTAMP DESC
LIMIT 100;

-- Pipeline health summary
SELECT
    PIPELINE_TYPE,
    STATUS,
    COUNT(*) AS COUNT
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.TBL_PIPELINE_MONITORING
WHERE CHECK_TIMESTAMP >= DATEADD('day', -1, CURRENT_TIMESTAMP())
GROUP BY PIPELINE_TYPE, STATUS
ORDER BY PIPELINE_TYPE, STATUS;
```

---

## Troubleshooting

### Issue 1: Snowpipe Not Loading Files

**Symptoms:**
- Files in S3 but not appearing in Snowflake
- `PIPE_USAGE_HISTORY` shows 0 files loaded

**Solutions:**

1. **Check SNS Topic Subscription:**
```sql
DESC PIPE PIPE_CROWDSTRIKE_EDR;
-- Verify notification_channel matches SNS subscription
```

2. **Verify S3 Event Notifications:**
```bash
aws s3api get-bucket-notification-configuration --bucket GenericCorp-security-data
```

3. **Check IAM Permissions:**
```bash
# Test S3 access with Snowflake IAM user
aws s3 ls s3://GenericCorp-security-data/edr/crowdstrike/ \
  --profile snowflake-integration
```

4. **Manual Refresh:**
```sql
ALTER PIPE PIPE_CROWDSTRIKE_EDR REFRESH;
```

### Issue 2: Tasks Not Executing

**Symptoms:**
- Task state is 'started' but no executions in history
- Stream has data but task not triggered

**Solutions:**

1. **Check Task State:**
```sql
SHOW TASKS IN SCHEMA DEV_TRANSFORMATION.SECURITY_ANALYTICS;
-- Ensure STATE = 'started'
```

2. **Verify WHEN Condition:**
```sql
-- Check if stream has data
SELECT SYSTEM$STREAM_HAS_DATA('DEV_LANDING.SECURITY_ANALYTICS.STREAM_CROWDSTRIKE_NEW');
-- Should return TRUE if task should run
```

3. **Check Warehouse:**
```sql
-- Ensure warehouse exists and has credits
SHOW WAREHOUSES LIKE 'DEV_WH';
```

4. **Force Task Execution:**
```sql
EXECUTE TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_TRANSFORM_CROWDSTRIKE;
```

### Issue 3: External Tables Not Refreshing

**Symptoms:**
- New files in S3 but external table shows old data
- AUTO_REFRESH not working

**Solutions:**

1. **Manual Refresh:**
```sql
ALTER EXTERNAL TABLE EXT_SERVICENOW_INCIDENTS REFRESH;
```

2. **Check Metadata:**
```sql
SELECT * FROM TABLE(
  INFORMATION_SCHEMA.EXTERNAL_TABLE_FILE_REGISTRATION_HISTORY(
    TABLE_NAME => 'EXT_SERVICENOW_INCIDENTS',
    START_TIME => DATEADD('day', -1, CURRENT_TIMESTAMP())
  )
);
```

3. **Verify Stage:**
```sql
LIST @STG_SERVICENOW_EXPORTS;
```

### Issue 4: Stream Lag

**Symptoms:**
- Stream offset is very high
- Task executions timing out

**Solutions:**

1. **Check Stream Offset:**
```sql
SELECT SYSTEM$STREAM_GET_TABLE_TIMESTAMP('STREAM_CROWDSTRIKE_NEW');
```

2. **Increase Task Frequency:**
```sql
ALTER TASK TASK_TRANSFORM_CROWDSTRIKE SET SCHEDULE = '5 MINUTE';
```

3. **Increase Warehouse Size:**
```sql
ALTER TASK TASK_TRANSFORM_CROWDSTRIKE SET WAREHOUSE = 'LARGE_WH';
```

4. **Reset Stream (CAUTION - data loss):**
```sql
-- Only use if stream is unrecoverably behind
CREATE OR REPLACE STREAM STREAM_CROWDSTRIKE_NEW
  ON TABLE L_CROWDSTRIKE_RAW;
```

### Issue 5: Performance Issues

**Symptoms:**
- Tasks taking too long
- High credit consumption

**Solutions:**

1. **Add Clustering Keys:**
```sql
ALTER TABLE L_CROWDSTRIKE_RAW
  CLUSTER BY (TO_DATE(INGESTION_TIMESTAMP));
```

2. **Optimize Transformations:**
```sql
-- Use incremental processing via streams
-- Avoid full table scans
```

3. **Use Materialized Views:**
```sql
CREATE MATERIALIZED VIEW MV_DAILY_EDR_SUMMARY AS
SELECT
    TO_DATE(DETECTION_TIME) AS DETECTION_DATE,
    SEVERITY,
    COUNT(*) AS EVENT_COUNT
FROM FACT_EDR
GROUP BY 1, 2;
```

---

## Cost Optimization

### 1. Auto-Suspend Warehouses

```sql
ALTER WAREHOUSE DEV_WH SET
    AUTO_SUSPEND = 60  -- Suspend after 1 minute of inactivity
    AUTO_RESUME = TRUE;
```

### 2. Use Appropriate Warehouse Sizes

```sql
-- For frequent small tasks
ALTER TASK TASK_MONITORING_HEALTH_CHECK SET WAREHOUSE = 'XSMALL_WH';

-- For heavy transformations
ALTER TASK TASK_CALCULATE_TOP13_METRICS SET WAREHOUSE = 'MEDIUM_WH';
```

### 3. Optimize Task Schedules

```sql
-- Run expensive tasks during off-peak hours
ALTER TASK TASK_WEEKLY_HEALTH_CHECK
  SET SCHEDULE = 'USING CRON 0 6 * * SUN America/New_York';
```

### 4. Monitor Credit Usage

```sql
-- Warehouse credit usage by day
SELECT
    TO_DATE(START_TIME) AS DATE,
    WAREHOUSE_NAME,
    SUM(CREDITS_USED) AS TOTAL_CREDITS
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE START_TIME >= DATEADD('day', -30, CURRENT_DATE())
GROUP BY 1, 2
ORDER BY 1 DESC, 3 DESC;
```

---

## Security Best Practices

### 1. Rotate Credentials Regularly

```sql
-- Recreate storage integrations with new credentials quarterly
-- Update IAM roles and service principals
```

### 2. Use Separate Roles for Different Functions

```sql
-- Grant minimal privileges
GRANT USAGE ON WAREHOUSE DEV_WH TO ROLE DATA_ENGINEER;
GRANT SELECT ON ALL TABLES IN SCHEMA DEV_REPORTING.SECURITY_ANALYTICS TO ROLE POWERBI_READER;
```

### 3. Enable MFA for ACCOUNTADMIN

```sql
-- Require MFA for privileged operations
-- Configure in Snowflake account settings
```

### 4. Audit Pipeline Activity

```sql
-- Query audit logs
SELECT
    USER_NAME,
    QUERY_TEXT,
    EXECUTION_STATUS,
    START_TIME
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE QUERY_TEXT ILIKE '%PIPE%'
OR QUERY_TEXT ILIKE '%TASK%'
ORDER BY START_TIME DESC
LIMIT 100;
```

---

## Next Steps

✅ **Phase 1: Foundation (Complete)**
- Storage integrations configured
- Snowpipes deployed
- Streams created
- Tasks defined

✅ **Phase 2: Activation (In Progress)**
- [ ] Configure S3/Azure event notifications
- [ ] Resume tasks
- [ ] Validate data flow
- [ ] Monitor for 48 hours

⏭ **Phase 3: Optimization (Upcoming)**
- [ ] Tune task schedules based on actual load
- [ ] Implement clustering on high-volume tables
- [ ] Create materialized views for dashboards
- [ ] Set up alerting for pipeline failures

⏭ **Phase 4: Production Readiness**
- [ ] Disaster recovery testing
- [ ] Runbook documentation
- [ ] On-call rotation setup
- [ ] SLA definition and monitoring

---

## Support and Documentation

- **Snowflake Documentation:** https://docs.snowflake.com/
- **Snowpipe Guide:** https://docs.snowflake.com/en/user-guide/data-load-snowpipe
- **Tasks Guide:** https://docs.snowflake.com/en/user-guide/tasks-intro
- **Streams Guide:** https://docs.snowflake.com/en/user-guide/streams

---

**End of Infrastructure Setup Guide**
