-- =====================================================
-- ServiceNow Setup - Final (Working with permissions)
-- =====================================================

USE DATABASE DEV_TRANSFORMATION;

USE SCHEMA SERVICENOW;

-- Table 1: Incidents Raw
CREATE TABLE IF NOT EXISTS INCIDENTS_RAW (
    incident_number VARCHAR(100),
    sys_id VARCHAR(100),
    short_description VARCHAR(500),
    description TEXT,
    state VARCHAR(50),
    priority VARCHAR(10),
    severity VARCHAR(10),
    urgency VARCHAR(10),
    impact VARCHAR(10),
    assigned_to_user VARCHAR(200),
    assignment_group VARCHAR(200),
    category VARCHAR(200),
    subcategory VARCHAR(200),
    opened_at TIMESTAMP_LTZ,
    closed_at TIMESTAMP_LTZ,
    resolved_at TIMESTAMP_LTZ,
    sys_created_on TIMESTAMP_LTZ,
    sys_updated_on TIMESTAMP_LTZ,
    _extracted_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP,
    _raw_data VARIANT
);

-- Table 2: Change Requests Raw
CREATE TABLE IF NOT EXISTS CHANGE_REQUESTS_RAW (
    change_number VARCHAR(100),
    sys_id VARCHAR(100),
    short_description VARCHAR(500),
    description TEXT,
    state VARCHAR(50),
    type VARCHAR(50),
    risk VARCHAR(10),
    priority VARCHAR(10),
    assigned_to_user VARCHAR(200),
    assignment_group VARCHAR(200),
    category VARCHAR(200),
    start_date TIMESTAMP_LTZ,
    end_date TIMESTAMP_LTZ,
    opened_at TIMESTAMP_LTZ,
    closed_at TIMESTAMP_LTZ,
    sys_created_on TIMESTAMP_LTZ,
    sys_updated_on TIMESTAMP_LTZ,
    _extracted_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP,
    _raw_data VARIANT
);

-- Table 3: Users Raw
CREATE TABLE IF NOT EXISTS USERS_RAW (
    user_id VARCHAR(100),
    sys_id VARCHAR(100),
    user_name VARCHAR(200),
    first_name VARCHAR(200),
    last_name VARCHAR(200),
    email VARCHAR(300),
    title VARCHAR(200),
    department VARCHAR(200),
    active BOOLEAN,
    sys_created_on TIMESTAMP_LTZ,
    sys_updated_on TIMESTAMP_LTZ,
    _extracted_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP,
    _raw_data VARIANT
);

-- Table 4: Configuration Items Raw
CREATE TABLE IF NOT EXISTS CONFIGURATION_ITEMS_RAW (
    ci_sys_id VARCHAR(100),
    name VARCHAR(500),
    ci_class VARCHAR(200),
    category VARCHAR(200),
    operational_status VARCHAR(50),
    support_group VARCHAR(200),
    owned_by VARCHAR(200),
    managed_by VARCHAR(200),
    sys_created_on TIMESTAMP_LTZ,
    sys_updated_on TIMESTAMP_LTZ,
    _extracted_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP,
    _raw_data VARIANT
);

-- Table 5: Incidents Transformed
CREATE TABLE IF NOT EXISTS INCIDENTS (
    incident_number VARCHAR(100) PRIMARY KEY,
    sys_id VARCHAR(100) UNIQUE NOT NULL,
    short_description VARCHAR(500),
    description TEXT,
    state VARCHAR(50),
    priority VARCHAR(10),
    severity VARCHAR(10),
    urgency VARCHAR(10),
    impact VARCHAR(10),
    assigned_to_user VARCHAR(200),
    assignment_group VARCHAR(200),
    category VARCHAR(200),
    subcategory VARCHAR(200),
    opened_at TIMESTAMP_LTZ,
    closed_at TIMESTAMP_LTZ,
    resolved_at TIMESTAMP_LTZ,
    sys_created_on TIMESTAMP_LTZ,
    sys_updated_on TIMESTAMP_LTZ,
    _extracted_timestamp TIMESTAMP_LTZ,
    _transformed_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP,
    _source_system VARCHAR(50) DEFAULT 'ServiceNow'
);

-- Table 6: Change Requests Transformed
CREATE TABLE IF NOT EXISTS CHANGE_REQUESTS (
    change_number VARCHAR(100) PRIMARY KEY,
    sys_id VARCHAR(100) UNIQUE NOT NULL,
    short_description VARCHAR(500),
    description TEXT,
    state VARCHAR(50),
    type VARCHAR(50),
    risk VARCHAR(10),
    priority VARCHAR(10),
    assigned_to_user VARCHAR(200),
    assignment_group VARCHAR(200),
    category VARCHAR(200),
    start_date TIMESTAMP_LTZ,
    end_date TIMESTAMP_LTZ,
    opened_at TIMESTAMP_LTZ,
    closed_at TIMESTAMP_LTZ,
    sys_created_on TIMESTAMP_LTZ,
    sys_updated_on TIMESTAMP_LTZ,
    _extracted_timestamp TIMESTAMP_LTZ,
    _transformed_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP,
    _source_system VARCHAR(50) DEFAULT 'ServiceNow'
);

-- Table 7: Users Transformed
CREATE TABLE IF NOT EXISTS USERS (
    user_id VARCHAR(100) PRIMARY KEY,
    sys_id VARCHAR(100) UNIQUE NOT NULL,
    user_name VARCHAR(200),
    first_name VARCHAR(200),
    last_name VARCHAR(200),
    email VARCHAR(300),
    title VARCHAR(200),
    department VARCHAR(200),
    active BOOLEAN,
    sys_created_on TIMESTAMP_LTZ,
    sys_updated_on TIMESTAMP_LTZ,
    _extracted_timestamp TIMESTAMP_LTZ,
    _transformed_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP,
    _source_system VARCHAR(50) DEFAULT 'ServiceNow'
);

-- Table 8: Configuration Items Transformed
CREATE TABLE IF NOT EXISTS CONFIGURATION_ITEMS (
    ci_sys_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(500),
    ci_class VARCHAR(200),
    category VARCHAR(200),
    operational_status VARCHAR(50),
    support_group VARCHAR(200),
    owned_by VARCHAR(200),
    managed_by VARCHAR(200),
    sys_created_on TIMESTAMP_LTZ,
    sys_updated_on TIMESTAMP_LTZ,
    _extracted_timestamp TIMESTAMP_LTZ,
    _transformed_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP,
    _source_system VARCHAR(50) DEFAULT 'ServiceNow'
);

-- Table 9: Connector Sync Log
CREATE TABLE IF NOT EXISTS CONNECTOR_SYNC_LOG (
    sync_id INTEGER AUTOINCREMENT PRIMARY KEY,
    table_name VARCHAR(200),
    sync_type VARCHAR(50),
    sync_status VARCHAR(50),
    records_synced INTEGER,
    sync_start_timestamp TIMESTAMP_LTZ,
    sync_end_timestamp TIMESTAMP_LTZ,
    error_message TEXT,
    executed_by VARCHAR(200) DEFAULT CURRENT_USER()
);

-- Table 10: Connector Config
CREATE TABLE IF NOT EXISTS CONNECTOR_CONFIG (
    config_id INTEGER AUTOINCREMENT PRIMARY KEY,
    table_name VARCHAR(200),
    is_enabled BOOLEAN DEFAULT TRUE,
    sync_frequency_minutes INTEGER DEFAULT 15,
    last_sync_timestamp TIMESTAMP_LTZ,
    incremental_field VARCHAR(200) DEFAULT 'sys_updated_on',
    notes TEXT,
    created_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP
);

-- Insert configuration
INSERT INTO CONNECTOR_CONFIG (table_name, is_enabled, sync_frequency_minutes, notes)
VALUES
    ('incident', TRUE, 15, 'Priority 1: Incident management'),
    ('change_request', TRUE, 30, 'Priority 1: Change management'),
    ('problem', TRUE, 30, 'Priority 2: Problem management'),
    ('cmdb_ci', TRUE, 60, 'Priority 1: CMDB items'),
    ('sys_user', TRUE, 240, 'Priority 1: Users'),
    ('sys_user_group', TRUE, 240, 'Priority 2: User groups'),
    ('cmdb_rel_ci', TRUE, 60, 'Priority 2: CMDB relationships');

-- Verify tables
SHOW TABLES IN SCHEMA DEV_TRANSFORMATION.SERVICENOW;

SELECT '✅ DEV_TRANSFORMATION.SERVICENOW setup complete' AS status;

-- Switch to Reporting
USE DATABASE DEV_REPORTING;

USE SCHEMA SERVICENOW;

-- View 1: Active Incidents
CREATE OR REPLACE VIEW VW_ACTIVE_INCIDENTS AS
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

-- View 2: Incident Metrics
CREATE OR REPLACE VIEW VW_INCIDENT_METRICS_BY_PRIORITY AS
SELECT
    priority,
    COUNT(*) AS total_incidents,
    COUNT(CASE WHEN state NOT IN ('Closed', 'Resolved', 'Cancelled') THEN 1 END) AS active_incidents,
    COUNT(CASE WHEN state IN ('Closed', 'Resolved') THEN 1 END) AS closed_incidents,
    AVG(DATEDIFF(hour, opened_at, COALESCE(closed_at, CURRENT_TIMESTAMP()))) AS avg_resolution_hours
FROM DEV_TRANSFORMATION.SERVICENOW.INCIDENTS
GROUP BY priority
ORDER BY priority;

-- View 3: Change Calendar
CREATE OR REPLACE VIEW VW_CHANGE_CALENDAR AS
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

-- View 4: CMDB Inventory
CREATE OR REPLACE VIEW VW_CMDB_INVENTORY AS
SELECT
    ci_class,
    category,
    operational_status,
    COUNT(*) AS total_assets,
    COUNT(CASE WHEN operational_status = 'Operational' THEN 1 END) AS operational_count
FROM DEV_TRANSFORMATION.SERVICENOW.CONFIGURATION_ITEMS
GROUP BY ci_class, category, operational_status
ORDER BY ci_class, category;

-- View 5: User Activity
CREATE OR REPLACE VIEW VW_USER_ACTIVITY AS
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

-- View 6: Daily Incident Trend
CREATE OR REPLACE VIEW VW_DAILY_INCIDENT_TREND AS
SELECT
    DATE(opened_at) AS incident_date,
    COUNT(*) AS total_opened,
    COUNT(CASE WHEN priority = '1' THEN 1 END) AS p1_incidents,
    COUNT(CASE WHEN priority = '2' THEN 1 END) AS p2_incidents,
    COUNT(CASE WHEN priority = '3' THEN 1 END) AS p3_incidents
FROM DEV_TRANSFORMATION.SERVICENOW.INCIDENTS
WHERE opened_at >= DATEADD(day, -30, CURRENT_DATE())
GROUP BY DATE(opened_at)
ORDER BY incident_date DESC;

-- Verify views
SHOW VIEWS IN SCHEMA DEV_REPORTING.SERVICENOW;

SELECT '✅ DEV_REPORTING.SERVICENOW setup complete' AS status;

-- Final summary
SELECT 'ServiceNow Setup' AS component, 'Complete' AS status
UNION ALL
SELECT 'DEV_TRANSFORMATION.SERVICENOW' AS component,
       (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
        WHERE table_schema = 'SERVICENOW'
        AND table_catalog = 'DEV_TRANSFORMATION')::VARCHAR || ' tables' AS status
UNION ALL
SELECT 'DEV_REPORTING.SERVICENOW' AS component,
       (SELECT COUNT(*) FROM INFORMATION_SCHEMA.VIEWS
        WHERE table_schema = 'SERVICENOW'
        AND table_catalog = 'DEV_REPORTING')::VARCHAR || ' views' AS status;

SELECT '✅ Setup complete!' AS final_status;
