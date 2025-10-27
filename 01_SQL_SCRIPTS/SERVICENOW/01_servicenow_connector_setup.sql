-- =====================================================
-- ServiceNow Native Connector - Initial Setup
-- =====================================================
-- Purpose: Set up database, schemas, and warehouse for ServiceNow connector
-- Author: GenericCorp Data Engineering Team
-- Date: 2025-10-24
-- Reference: https://docs.snowflake.com/en/connectors/servicenow/about
-- =====================================================

-- Switch to ACCOUNTADMIN role (required for connector installation)
USE ROLE ACCOUNTADMIN;

-- =====================================================
-- STEP 1: Create Database for ServiceNow Data
-- =====================================================

CREATE DATABASE IF NOT EXISTS SERVICENOW_CONNECTOR
    DATA_RETENTION_TIME_IN_DAYS = 7
    COMMENT = 'ServiceNow data ingested via Snowflake Native Connector - Production';

GRANT OWNERSHIP ON DATABASE SERVICENOW_CONNECTOR TO ROLE SYSADMIN;
USE DATABASE SERVICENOW_CONNECTOR;

-- =====================================================
-- STEP 2: Create Schemas
-- =====================================================

-- Schema for raw ServiceNow data (synced by connector)
CREATE SCHEMA IF NOT EXISTS RAW_DATA
    DATA_RETENTION_TIME_IN_DAYS = 7
    COMMENT = 'Raw ServiceNow tables synced by native connector';

-- Schema for connector metadata and configuration
CREATE SCHEMA IF NOT EXISTS CONNECTOR_METADATA
    DATA_RETENTION_TIME_IN_DAYS = 30
    COMMENT = 'Connector configuration, sync status, and metadata';

-- Grant permissions
GRANT USAGE ON SCHEMA RAW_DATA TO ROLE DEV_DEVELOPER;
GRANT USAGE ON SCHEMA RAW_DATA TO ROLE DEV_READER;
GRANT USAGE ON SCHEMA CONNECTOR_METADATA TO ROLE DEV_DEVELOPER;

-- =====================================================
-- STEP 3: Create Dedicated Warehouse for Connector
-- =====================================================

CREATE WAREHOUSE IF NOT EXISTS SERVICENOW_WH
    WAREHOUSE_SIZE = 'SMALL'
    AUTO_SUSPEND = 300  -- 5 minutes (default)
    AUTO_RESUME = TRUE  -- MANDATORY for connector to function
    INITIALLY_SUSPENDED = FALSE
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 1
    SCALING_POLICY = 'STANDARD'
    COMMENT = 'Dedicated warehouse for ServiceNow connector background ingestion';

-- Grant usage to roles
GRANT USAGE ON WAREHOUSE SERVICENOW_WH TO ROLE DEV_DEVELOPER;
GRANT USAGE ON WAREHOUSE SERVICENOW_WH TO ROLE DEV_READER;
GRANT OPERATE ON WAREHOUSE SERVICENOW_WH TO ROLE SYSADMIN;

-- =====================================================
-- STEP 4: Verify Configuration
-- =====================================================

-- Check database exists
SELECT
    database_name,
    database_owner,
    retention_time,
    comment
FROM INFORMATION_SCHEMA.DATABASES
WHERE database_name = 'SERVICENOW_CONNECTOR';

-- Check schemas exist
SELECT
    schema_name,
    schema_owner,
    retention_time,
    comment
FROM INFORMATION_SCHEMA.SCHEMATA
WHERE schema_name IN ('RAW_DATA', 'CONNECTOR_METADATA');

-- Check warehouse configuration
SHOW WAREHOUSES LIKE 'SERVICENOW_WH';

-- Verify AUTO_RESUME is TRUE (required)
SELECT
    "name" AS warehouse_name,
    "size" AS warehouse_size,
    "auto_resume" AS auto_resume,
    "auto_suspend" AS auto_suspend
FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))
WHERE "name" = 'SERVICENOW_WH';

-- =====================================================
-- STEP 5: Create Tracking Tables (Pre-Connector)
-- =====================================================

USE SCHEMA CONNECTOR_METADATA;

-- Table to track connector installation
CREATE TABLE IF NOT EXISTS CONNECTOR_INSTALLATION_LOG (
    log_id INTEGER AUTOINCREMENT PRIMARY KEY,
    installation_step VARCHAR(200),
    step_status VARCHAR(50),  -- SUCCESS, FAILED, IN_PROGRESS
    execution_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP,
    executed_by VARCHAR(200) DEFAULT CURRENT_USER(),
    notes TEXT
);

-- Log this setup
INSERT INTO CONNECTOR_INSTALLATION_LOG (installation_step, step_status, notes)
VALUES
    ('Database Creation', 'SUCCESS', 'Created SERVICENOW_CONNECTOR database'),
    ('Schema Creation', 'SUCCESS', 'Created RAW_DATA and CONNECTOR_METADATA schemas'),
    ('Warehouse Creation', 'SUCCESS', 'Created SERVICENOW_WH with AUTO_RESUME enabled'),
    ('Permissions', 'SUCCESS', 'Granted permissions to DEV_DEVELOPER and DEV_READER roles');

-- =====================================================
-- STEP 6: Prepare for Marketplace Installation
-- =====================================================

-- Note: Next steps must be done via Snowsight UI:
-- 1. Navigate to: Data Products > Marketplace
-- 2. Search for: "Snowflake Connector for ServiceNow"
-- 3. Click "Get" then "Install"
-- 4. Follow installation wizard:
--    - Select database: SERVICENOW_CONNECTOR
--    - Select warehouse: SERVICENOW_WH
--    - Grant necessary privileges

SELECT '✅ Setup complete! Next: Install connector via Snowflake Marketplace' AS next_step;

-- =====================================================
-- VERIFICATION CHECKLIST
-- =====================================================

/*
PRE-INSTALLATION CHECKLIST:
[ ] Database SERVICENOW_CONNECTOR created
[ ] Schemas RAW_DATA and CONNECTOR_METADATA created
[ ] Warehouse SERVICENOW_WH created with AUTO_RESUME = TRUE
[ ] Permissions granted to DEV_DEVELOPER and DEV_READER roles
[ ] ServiceNow instance is publicly accessible (not behind VPN)
[ ] ServiceNow OAuth application credentials ready:
    - Client ID: __________________________
    - Client Secret: ______________________
    - Username: ___________________________
    - Password: ___________________________
[ ] User has ACCOUNTADMIN role for Marketplace installation

READY TO PROCEED TO MARKETPLACE INSTALLATION: [ ]
*/
