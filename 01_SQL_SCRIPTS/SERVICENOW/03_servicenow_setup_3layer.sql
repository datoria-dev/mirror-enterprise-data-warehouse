-- =====================================================
-- ServiceNow Native Connector - 3-Layer Medallion Setup
-- =====================================================
-- Purpose: Set up ServiceNow schemas within existing DEV_LANDING, DEV_TRANSFORMATION, DEV_REPORTING databases
-- Author: GenericCorp Data Engineering Team
-- Date: 2025-10-24
-- Architecture: Bronze (Landing) → Silver (Transformation) → Gold (Reporting)
-- =====================================================

-- =====================================================
-- LAYER 1: DEV_LANDING (Bronze) - Raw ServiceNow Data
-- =====================================================

USE DATABASE DEV_LANDING;

-- Create schema for raw ServiceNow data
CREATE SCHEMA IF NOT EXISTS SERVICENOW
    DATA_RETENTION_TIME_IN_DAYS = 7
    COMMENT = 'Raw ServiceNow data ingested via Snowflake Native Connector (Bronze Layer)';

-- Grant permissions
GRANT USAGE ON SCHEMA DEV_LANDING.SERVICENOW TO ROLE DEV_DEVELOPER;

-- Create metadata tracking table for connector
CREATE TABLE IF NOT EXISTS DEV_LANDING.SERVICENOW.CONNECTOR_SYNC_LOG (
    sync_id INTEGER AUTOINCREMENT PRIMARY KEY,
    table_name VARCHAR(200),
    sync_type VARCHAR(50),  -- INITIAL_LOAD, INCREMENTAL, FULL_REFRESH
    sync_status VARCHAR(50),  -- SUCCESS, FAILED, IN_PROGRESS
    records_synced INTEGER,
    sync_start_timestamp TIMESTAMP_LTZ,
    sync_end_timestamp TIMESTAMP_LTZ,
    error_message TEXT,
    executed_by VARCHAR(200) DEFAULT CURRENT_USER(),
    COMMENT = 'Tracks ServiceNow connector synchronization runs'
);

-- Create table for ServiceNow connector configuration
CREATE TABLE IF NOT EXISTS DEV_LANDING.SERVICENOW.CONNECTOR_CONFIG (
    config_id INTEGER AUTOINCREMENT PRIMARY KEY,
    table_name VARCHAR(200),
    is_enabled BOOLEAN DEFAULT TRUE,
    sync_frequency_minutes INTEGER DEFAULT 15,
    last_sync_timestamp TIMESTAMP_LTZ,
    incremental_field VARCHAR(200) DEFAULT 'sys_updated_on',
    notes TEXT,
    created_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP,
    COMMENT = 'Configuration for each ServiceNow table being synced'
);

-- Insert initial configuration for 7 priority tables
INSERT INTO DEV_LANDING.SERVICENOW.CONNECTOR_CONFIG
    (table_name, is_enabled, sync_frequency_minutes, notes)
VALUES
    ('incident', TRUE, 15, 'Priority 1: Incident management records'),
    ('change_request', TRUE, 30, 'Priority 1: Change management records'),
    ('problem', TRUE, 30, 'Priority 2: Problem management records'),
    ('cmdb_ci', TRUE, 60, 'Priority 1: Configuration items from CMDB'),
    ('sys_user', TRUE, 240, 'Priority 1: User directory (updates less frequently)'),
    ('sys_user_group', TRUE, 240, 'Priority 2: User groups'),
    ('cmdb_rel_ci', TRUE, 60, 'Priority 2: CMDB relationships');

-- Verify Landing Layer setup
SELECT '✅ DEV_LANDING.SERVICENOW schema created' AS status;

SELECT * FROM DEV_LANDING.SERVICENOW.CONNECTOR_CONFIG
ORDER BY table_name;

-- =====================================================
-- LAYER 2: DEV_TRANSFORMATION (Silver) - Business Logic
-- =====================================================

USE DATABASE DEV_TRANSFORMATION;

-- Create schema for transformed ServiceNow data
CREATE SCHEMA IF NOT EXISTS SERVICENOW
    DATA_RETENTION_TIME_IN_DAYS = 30
    COMMENT = 'Transformed ServiceNow data with business logic applied (Silver Layer)';

-- Grant permissions
GRANT USAGE ON SCHEMA DEV_TRANSFORMATION.SERVICENOW TO ROLE DEV_DEVELOPER;

-- Create staging table for incidents (will be populated by transformation task)
CREATE TABLE IF NOT EXISTS DEV_TRANSFORMATION.SERVICENOW.INCIDENTS (
    -- Business Keys
    incident_number VARCHAR(100) PRIMARY KEY,
    sys_id VARCHAR(100) UNIQUE NOT NULL,

    -- Core Fields
    short_description VARCHAR(500),
    description TEXT,
    state VARCHAR(50),
    priority VARCHAR(10),
    severity VARCHAR(10),
    urgency VARCHAR(10),
    impact VARCHAR(10),

    -- Assignment
    assigned_to_user VARCHAR(200),
    assignment_group VARCHAR(200),

    -- Categorization
    category VARCHAR(200),
    subcategory VARCHAR(200),

    -- Timestamps
    opened_at TIMESTAMP_LTZ,
    closed_at TIMESTAMP_LTZ,
    resolved_at TIMESTAMP_LTZ,
    sys_created_on TIMESTAMP_LTZ,
    sys_updated_on TIMESTAMP_LTZ,

    -- Metadata
    _extracted_timestamp TIMESTAMP_LTZ,
    _transformed_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP,
    _source_system VARCHAR(50) DEFAULT 'ServiceNow',

    COMMENT = 'Transformed incident records from ServiceNow'
);

-- Create staging table for changes
CREATE TABLE IF NOT EXISTS DEV_TRANSFORMATION.SERVICENOW.CHANGE_REQUESTS (
    -- Business Keys
    change_number VARCHAR(100) PRIMARY KEY,
    sys_id VARCHAR(100) UNIQUE NOT NULL,

    -- Core Fields
    short_description VARCHAR(500),
    description TEXT,
    state VARCHAR(50),
    type VARCHAR(50),
    risk VARCHAR(10),
    priority VARCHAR(10),

    -- Assignment
    assigned_to_user VARCHAR(200),
    assignment_group VARCHAR(200),

    -- Categorization
    category VARCHAR(200),

    -- Change Windows
    start_date TIMESTAMP_LTZ,
    end_date TIMESTAMP_LTZ,

    -- Timestamps
    opened_at TIMESTAMP_LTZ,
    closed_at TIMESTAMP_LTZ,
    sys_created_on TIMESTAMP_LTZ,
    sys_updated_on TIMESTAMP_LTZ,

    -- Metadata
    _extracted_timestamp TIMESTAMP_LTZ,
    _transformed_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP,
    _source_system VARCHAR(50) DEFAULT 'ServiceNow',

    COMMENT = 'Transformed change request records from ServiceNow'
);

-- Create staging table for users
CREATE TABLE IF NOT EXISTS DEV_TRANSFORMATION.SERVICENOW.USERS (
    -- Business Keys
    user_id VARCHAR(100) PRIMARY KEY,
    sys_id VARCHAR(100) UNIQUE NOT NULL,

    -- Core Fields
    user_name VARCHAR(200),
    first_name VARCHAR(200),
    last_name VARCHAR(200),
    email VARCHAR(300),
    title VARCHAR(200),
    department VARCHAR(200),
    active BOOLEAN,

    -- Timestamps
    sys_created_on TIMESTAMP_LTZ,
    sys_updated_on TIMESTAMP_LTZ,

    -- Metadata
    _extracted_timestamp TIMESTAMP_LTZ,
    _transformed_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP,
    _source_system VARCHAR(50) DEFAULT 'ServiceNow',

    COMMENT = 'Transformed user records from ServiceNow'
);

-- Create staging table for CMDB CIs
CREATE TABLE IF NOT EXISTS DEV_TRANSFORMATION.SERVICENOW.CONFIGURATION_ITEMS (
    -- Business Keys
    ci_sys_id VARCHAR(100) PRIMARY KEY,

    -- Core Fields
    name VARCHAR(500),
    ci_class VARCHAR(200),
    category VARCHAR(200),
    operational_status VARCHAR(50),
    support_group VARCHAR(200),

    -- Ownership
    owned_by VARCHAR(200),
    managed_by VARCHAR(200),

    -- Timestamps
    sys_created_on TIMESTAMP_LTZ,
    sys_updated_on TIMESTAMP_LTZ,

    -- Metadata
    _extracted_timestamp TIMESTAMP_LTZ,
    _transformed_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP,
    _source_system VARCHAR(50) DEFAULT 'ServiceNow',

    COMMENT = 'Transformed configuration items from ServiceNow CMDB'
);

-- Verify Transformation Layer setup
SELECT '✅ DEV_TRANSFORMATION.SERVICENOW schema created' AS status;

SHOW TABLES IN SCHEMA DEV_TRANSFORMATION.SERVICENOW;

-- =====================================================
-- LAYER 3: DEV_REPORTING (Gold) - Analytics Views
-- =====================================================

USE DATABASE DEV_REPORTING;

-- Create schema for ServiceNow reporting views
CREATE SCHEMA IF NOT EXISTS SERVICENOW
    COMMENT = 'ServiceNow analytics and reporting views (Gold Layer)';

-- Grant permissions
GRANT USAGE ON SCHEMA DEV_REPORTING.SERVICENOW TO ROLE DEV_DEVELOPER;

-- View 1: Active Incidents Summary
CREATE OR REPLACE VIEW DEV_REPORTING.SERVICENOW.VW_ACTIVE_INCIDENTS AS
SELECT
    incident_number,
    short_description,
    state,
    priority,
    severity,
    assigned_to_user,
    assignment_group,
    category,
    subcategory,
    opened_at,
    DATEDIFF(day, opened_at, CURRENT_TIMESTAMP()) AS days_open,
    sys_updated_on AS last_updated
FROM DEV_TRANSFORMATION.SERVICENOW.INCIDENTS
WHERE state NOT IN ('Closed', 'Resolved', 'Cancelled')
ORDER BY priority, opened_at;

-- View 2: Incident Metrics by Priority
CREATE OR REPLACE VIEW DEV_REPORTING.SERVICENOW.VW_INCIDENT_METRICS_BY_PRIORITY AS
SELECT
    priority,
    COUNT(*) AS total_incidents,
    COUNT(CASE WHEN state NOT IN ('Closed', 'Resolved', 'Cancelled') THEN 1 END) AS active_incidents,
    COUNT(CASE WHEN state IN ('Closed', 'Resolved') THEN 1 END) AS closed_incidents,
    AVG(DATEDIFF(hour, opened_at, COALESCE(closed_at, CURRENT_TIMESTAMP()))) AS avg_resolution_hours,
    MAX(DATEDIFF(hour, opened_at, COALESCE(closed_at, CURRENT_TIMESTAMP()))) AS max_resolution_hours
FROM DEV_TRANSFORMATION.SERVICENOW.INCIDENTS
GROUP BY priority
ORDER BY priority;

-- View 3: Change Request Calendar
CREATE OR REPLACE VIEW DEV_REPORTING.SERVICENOW.VW_CHANGE_CALENDAR AS
SELECT
    change_number,
    short_description,
    type,
    state,
    risk,
    priority,
    assigned_to_user,
    start_date,
    end_date,
    DATEDIFF(hour, start_date, end_date) AS duration_hours
FROM DEV_TRANSFORMATION.SERVICENOW.CHANGE_REQUESTS
WHERE state NOT IN ('Closed', 'Cancelled')
  AND start_date >= CURRENT_DATE()
ORDER BY start_date;

-- View 4: CMDB Asset Inventory
CREATE OR REPLACE VIEW DEV_REPORTING.SERVICENOW.VW_CMDB_INVENTORY AS
SELECT
    ci_class,
    category,
    operational_status,
    COUNT(*) AS total_assets,
    COUNT(CASE WHEN operational_status = 'Operational' THEN 1 END) AS operational_count,
    COUNT(CASE WHEN operational_status IN ('Non-Operational', 'Retired') THEN 1 END) AS inactive_count
FROM DEV_TRANSFORMATION.SERVICENOW.CONFIGURATION_ITEMS
GROUP BY ci_class, category, operational_status
ORDER BY ci_class, category;

-- View 5: User Activity Summary
CREATE OR REPLACE VIEW DEV_REPORTING.SERVICENOW.VW_USER_ACTIVITY AS
SELECT
    u.user_name,
    u.email,
    u.department,
    COUNT(DISTINCT i.incident_number) AS assigned_incidents,
    COUNT(DISTINCT c.change_number) AS assigned_changes,
    u.active AS user_active
FROM DEV_TRANSFORMATION.SERVICENOW.USERS u
LEFT JOIN DEV_TRANSFORMATION.SERVICENOW.INCIDENTS i
    ON u.user_name = i.assigned_to_user
LEFT JOIN DEV_TRANSFORMATION.SERVICENOW.CHANGE_REQUESTS c
    ON u.user_name = c.assigned_to_user
WHERE u.active = TRUE
GROUP BY u.user_name, u.email, u.department, u.active
ORDER BY assigned_incidents DESC;

-- Verify Reporting Layer setup
SELECT '✅ DEV_REPORTING.SERVICENOW schema created' AS status;

SHOW VIEWS IN SCHEMA DEV_REPORTING.SERVICENOW;

-- =====================================================
-- VERIFICATION SUMMARY
-- =====================================================

-- Summary of created objects
SELECT 'Bronze Layer' AS layer, 'DEV_LANDING.SERVICENOW' AS schema_name,
       '2 tables (CONNECTOR_SYNC_LOG, CONNECTOR_CONFIG)' AS objects,
       '7 ServiceNow tables to be created by Native Connector' AS notes
UNION ALL
SELECT 'Silver Layer' AS layer, 'DEV_TRANSFORMATION.SERVICENOW' AS schema_name,
       '4 tables (INCIDENTS, CHANGE_REQUESTS, USERS, CONFIGURATION_ITEMS)' AS objects,
       'Business logic and transformations' AS notes
UNION ALL
SELECT 'Gold Layer' AS layer, 'DEV_REPORTING.SERVICENOW' AS schema_name,
       '5 views (VW_ACTIVE_INCIDENTS, VW_INCIDENT_METRICS_BY_PRIORITY, etc.)' AS objects,
       'Analytics and reporting' AS notes;

-- =====================================================
-- NEXT STEPS (MANUAL)
-- =====================================================

/*
📋 NATIVE CONNECTOR SETUP CHECKLIST:

Since we don't have ACCOUNTADMIN privileges, we need to request administrator assistance:

STEP 1: Contact Snowflake Administrator
[ ] Request installation of "Snowflake Connector for ServiceNow" from Marketplace
[ ] Provide target location: DEV_LANDING.SERVICENOW schema
[ ] Provide warehouse to use: Existing DEV_WH (or specify another)

STEP 2: ServiceNow OAuth Configuration
[ ] Create OAuth application in ServiceNow
[ ] Obtain credentials:
    - Client ID
    - Client Secret
    - Username
    - Password
[ ] Provide to admin for connector configuration

STEP 3: Table Enablement (via Admin)
[ ] Enable these 7 tables in connector:
    1. incident
    2. change_request
    3. problem
    4. cmdb_ci
    5. sys_user
    6. sys_user_group
    7. cmdb_rel_ci

STEP 4: Create Transformation Tasks (DEV_DEVELOPER can do this)
[ ] Create Snowflake Tasks to transform data from Landing → Transformation
[ ] Schedule: Every 15 minutes (aligned with connector sync)
[ ] Use MERGE statements for idempotency

STEP 5: Validate Data Flow
[ ] Verify data appears in DEV_LANDING.SERVICENOW.* tables
[ ] Verify transformations populate DEV_TRANSFORMATION.SERVICENOW.* tables
[ ] Verify reporting views in DEV_REPORTING.SERVICENOW.* show correct data

═══════════════════════════════════════════════════════════════════════════════

⚠️  IMPORTANT: Native Connector Limitation

The Snowflake Native Connector for ServiceNow can ONLY sync data to tables it creates.
We CANNOT use it to sync directly into our 3-layer architecture.

REVISED APPROACH:
1. Connector syncs to DEV_LANDING.SERVICENOW.{TABLE}_RAW (connector-managed tables)
2. Snowflake Task copies from _RAW tables → DEV_TRANSFORMATION.SERVICENOW.{TABLE}
3. Views in DEV_REPORTING.SERVICENOW.VW_* query transformation layer

This maintains the connector's CDC (Change Data Capture) while fitting our architecture.
*/

SELECT '✅ Setup complete! See script comments for next steps.' AS final_status;
