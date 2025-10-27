# SECURITY_ANALYTICS Enhancement Implementation Plan

**Project**: Post-Presentation Enhancements
**Date**: 2025-10-07
**Status**: Design & Implementation Phase
**Priority**: HIGH - Executive Visibility Requirements

---

## Executive Summary

Based on the GIS Offsite presentation analysis, we've identified **4 critical enhancements** needed to deliver the full executive vision for Snowflake-powered cyber performance reporting.

### Enhancement Overview

| # | Enhancement | Business Value | Technical Complexity | Estimated Effort |
|---|-------------|----------------|---------------------|------------------|
| 1 | **Power BI Integration Layer** | Executive dashboards | Medium | 48 hours |
| 2 | **Near Real-Time Capabilities** | Operational responsiveness | High | 64 hours |
| 3 | **Unified User Dimension** | User-centric analytics | Medium | 40 hours |
| 4 | **Data Quality Dashboard** | Trust & transparency | Low | 28 hours |
| **TOTAL** | **4 Enhancements** | **Complete executive vision** | - | **180 hours** |

**Timeline**: 4-6 weeks (1 FTE)

---

## Table of Contents

1. [Enhancement 1: Power BI Integration Layer](#enhancement-1-power-bi-integration-layer)
2. [Enhancement 2: Near Real-Time Capabilities](#enhancement-2-near-real-time-capabilities)
3. [Enhancement 3: Unified User Dimension](#enhancement-3-unified-user-dimension)
4. [Enhancement 4: Data Quality Dashboard](#enhancement-4-data-quality-dashboard)
5. [Implementation Sequence](#implementation-sequence)
6. [Testing & Validation](#testing--validation)

---

## Enhancement 1: Power BI Integration Layer

### Business Context

**From Presentation**: "One Platform => Different Views for Different Audiences" (Slide 6)
- CIO(s) need executive dashboards
- Analysts need operational views
- Tool: Power BI

**Current Gap**: No Power BI-optimized data model exists

### Objectives

1. Create **semantic layer** with business-friendly field names
2. Implement **row-level security** for OpCo/Division filtering
3. Optimize for **performance** (aggregated tables, materialized views)
4. Support **two dashboard types**: Executive + Operational

---

### 1.1 Semantic Layer Views

**Purpose**: Translate technical tables into business-friendly views for Power BI

#### Executive Dashboard View

```sql
-- ============================================================================
-- POWER BI SEMANTIC LAYER: EXECUTIVE DASHBOARD
-- Purpose: High-level KPIs for C-Level executives
-- Refresh: Daily (after KPI calculation tasks)
-- ============================================================================

CREATE OR REPLACE VIEW DEV_REPORTING.SECURITY_ANALYTICS.VW_POWERBI_EXECUTIVE_DASHBOARD AS
WITH latest_kpis AS (
    SELECT
        -- Time Dimension (for slicers and trending)
        d.FULL_DATE as "Date",
        d.YEAR as "Year",
        d.QUARTER as "Quarter",
        d.MONTH_NAME as "Month",
        d.WEEK_OF_YEAR as "Week",

        -- Organizational Dimension (for filtering by region/division)
        o.OPCO_NAME as "Operating Company",
        o.REGION as "Region",
        o.COUNTRY as "Country",
        o.BUSINESS_UNIT as "Business Unit",
        o.DIVISION as "Division",

        -- Top 13 Executive Metrics (from Metrics Dictionary)
        -- Metric #1: Cyber-Maturity Score
        COALESCE(m.CYBER_MATURITY_SCORE, 0) as "Cyber Maturity Score",
        CASE
            WHEN m.CYBER_MATURITY_SCORE >= 4 THEN 'Excellent'
            WHEN m.CYBER_MATURITY_SCORE >= 3 THEN 'Good'
            WHEN m.CYBER_MATURITY_SCORE >= 2 THEN 'Fair'
            ELSE 'Poor'
        END as "Maturity Rating",

        -- Metric #5: EDR Coverage
        COALESCE(m.EDR_COVERAGE_PCT, 0) as "EDR Coverage %",
        CASE
            WHEN m.EDR_COVERAGE_PCT >= 98 THEN 'Target Met'
            WHEN m.EDR_COVERAGE_PCT >= 95 THEN 'Near Target'
            ELSE 'Below Target'
        END as "EDR Status",

        -- Metric #6: Vulnerability Scan Coverage
        COALESCE(m.VULN_SCAN_COVERAGE_PCT, 0) as "Vulnerability Scan Coverage %",
        COALESCE(m.VULN_AGENT_HEALTH_PCT, 100) as "Scan Agent Health %",

        -- Metric #7: Email Security
        COALESCE(m.EMAIL_DOMAIN_SECURITY_PCT, 0) as "Email Domain Security %",

        -- Metric #8: Phishing Click Rate
        COALESCE(m.PHISHING_CLICK_RATE_PCT, 0) as "Phishing Click Rate %",
        CASE
            WHEN m.PHISHING_CLICK_RATE_PCT < 5 THEN 'Low Risk'
            WHEN m.PHISHING_CLICK_RATE_PCT < 10 THEN 'Medium Risk'
            ELSE 'High Risk'
        END as "Phishing Risk Level",

        -- Metric #11: SOC Ticket SLA Compliance
        COALESCE(m.SOC_TICKET_SLA_PCT, 0) as "SOC Ticket SLA %",

        -- Composite: Overall Security Health Index (0-100)
        ROUND(
            (COALESCE(m.EDR_COVERAGE_PCT, 0) * 0.20) +
            (COALESCE(m.VULN_SCAN_COVERAGE_PCT, 0) * 0.20) +
            ((100 - COALESCE(m.PHISHING_CLICK_RATE_PCT, 0)) * 0.15) +
            (COALESCE(m.EMAIL_DOMAIN_SECURITY_PCT, 0) * 0.15) +
            (COALESCE(m.SOC_TICKET_SLA_PCT, 0) * 0.15) +
            (COALESCE(m.CYBER_MATURITY_SCORE, 0) * 20 * 0.15),
        2) as "Overall Security Health Score",

        CASE
            WHEN "Overall Security Health Score" >= 90 THEN 'Excellent'
            WHEN "Overall Security Health Score" >= 75 THEN 'Good'
            WHEN "Overall Security Health Score" >= 60 THEN 'Fair'
            ELSE 'Poor'
        END as "Security Health Rating",

        -- Trend Indicators (vs. previous period)
        LAG(m.EDR_COVERAGE_PCT, 1) OVER (
            PARTITION BY o.OPCO_ID
            ORDER BY d.FULL_DATE
        ) as "EDR Coverage % (Previous)",

        ROUND(m.EDR_COVERAGE_PCT - "EDR Coverage % (Previous)", 2) as "EDR Coverage Change",

        CASE
            WHEN "EDR Coverage Change" > 0 THEN 'Improving'
            WHEN "EDR Coverage Change" < 0 THEN 'Declining'
            ELSE 'Stable'
        END as "EDR Coverage Trend",

        -- Data Quality Indicators
        COALESCE(m.DATA_QUALITY_SCORE, 0) as "Data Quality Score",
        m.LAST_REFRESHED as "Last Data Update",
        DATEDIFF('hour', m.LAST_REFRESHED, CURRENT_TIMESTAMP()) as "Hours Since Update"

    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_DATES d
    CROSS JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_OPCO o
    LEFT JOIN DEV_REPORTING.SECURITY_ANALYTICS.TBL_KPI_MASTER m
        ON d.DATE_KEY = m.DATE_KEY
        AND o.OPCO_ID = m.OPCO_ID

    WHERE d.FULL_DATE >= DATEADD('year', -2, CURRENT_DATE())  -- 2 years history
)
SELECT * FROM latest_kpis
WHERE "Date" IS NOT NULL;

-- Grant access to Power BI service account
GRANT SELECT ON DEV_REPORTING.SECURITY_ANALYTICS.VW_POWERBI_EXECUTIVE_DASHBOARD TO ROLE POWERBI_READER;
```

#### Operational Dashboard View

```sql
-- ============================================================================
-- POWER BI SEMANTIC LAYER: OPERATIONAL DASHBOARD
-- Purpose: Detailed drill-down for security analysts
-- Refresh: Hourly
-- ============================================================================

CREATE OR REPLACE VIEW DEV_REPORTING.SECURITY_ANALYTICS.VW_POWERBI_OPERATIONAL_DASHBOARD AS
SELECT
    -- Time & Organization
    d.FULL_DATE as "Date",
    d.YEAR as "Year",
    d.MONTH_NAME as "Month",
    o.OPCO_NAME as "Operating Company",

    -- Asset Details
    h.HOSTNAME as "Host Name",
    h.IP_ADDRESS as "IP Address",
    h.OS as "Operating System",
    CASE
        WHEN h.OS LIKE '%Server%' THEN 'Server'
        WHEN h.OS LIKE '%Windows%' THEN 'Workstation'
        WHEN h.OS LIKE '%macOS%' THEN 'Workstation'
        WHEN h.OS LIKE '%Linux%' THEN 'Server'
        ELSE 'Other'
    END as "Device Type",

    -- EDR Status
    CASE
        WHEN edr.ENDPOINT_ID IS NOT NULL THEN 'Protected'
        ELSE 'Unprotected'
    END as "EDR Protection Status",
    edr.EDR_VENDOR as "EDR Vendor",
    edr.AGENT_VERSION as "EDR Agent Version",
    edr.AGENT_STATUS as "EDR Agent Status",
    edr.LAST_SEEN_DATE as "EDR Last Seen",

    -- Vulnerability Status
    v.CRITICAL_VULNS as "Critical Vulnerabilities",
    v.HIGH_VULNS as "High Vulnerabilities",
    v.MEDIUM_VULNS as "Medium Vulnerabilities",
    v.LOW_VULNS as "Low Vulnerabilities",
    v.TOTAL_VULNS as "Total Vulnerabilities",
    v.OLDEST_VULN_DAYS as "Oldest Vulnerability (Days)",

    -- Qualys Scan Status
    q.LAST_SCAN_DATE as "Last Vulnerability Scan",
    DATEDIFF('day', q.LAST_SCAN_DATE, CURRENT_DATE()) as "Days Since Last Scan",
    q.AGENT_STATUS as "Qualys Agent Status",

    -- Email Security (if applicable)
    e.PHISHING_EMAILS_REPORTED as "Phishing Emails Reported",
    e.MALICIOUS_EMAILS_BLOCKED as "Malicious Emails Blocked",

    -- SOC Tickets
    t.OPEN_TICKETS as "Open Security Tickets",
    t.OVERDUE_TICKETS as "Overdue Tickets",
    t.AVG_RESOLUTION_TIME_HOURS as "Avg Resolution Time (Hours)",

    -- Risk Score (composite)
    CASE
        WHEN v.CRITICAL_VULNS > 10 THEN 'Critical Risk'
        WHEN v.CRITICAL_VULNS > 5 THEN 'High Risk'
        WHEN v.CRITICAL_VULNS > 0 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END as "Risk Level"

FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_DATES d
CROSS JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_OPCO o
LEFT JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST h ON o.OPCO_ID = h.OPCO_ID
LEFT JOIN (
    -- Union all EDR sources
    SELECT ENDPOINT_ID, 'CrowdStrike' as EDR_VENDOR, AGENT_VERSION, AGENT_STATUS, LAST_SEEN_DATE
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.CROWDSTRIKE
    UNION ALL
    SELECT ENDPOINT_ID, 'Sentinel One', AGENT_VERSION, AGENT_STATUS, LAST_SEEN_DATE
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.SENTINELONE
    -- ... other EDR sources
) edr ON h.HOST_ID = edr.ENDPOINT_ID
LEFT JOIN (
    -- Vulnerability summary by host
    SELECT
        HOST_ID,
        COUNT(CASE WHEN SEVERITY = 'CRITICAL' THEN 1 END) as CRITICAL_VULNS,
        COUNT(CASE WHEN SEVERITY = 'HIGH' THEN 1 END) as HIGH_VULNS,
        COUNT(CASE WHEN SEVERITY = 'MEDIUM' THEN 1 END) as MEDIUM_VULNS,
        COUNT(CASE WHEN SEVERITY = 'LOW' THEN 1 END) as LOW_VULNS,
        COUNT(*) as TOTAL_VULNS,
        MAX(DATEDIFF('day', FIRST_DETECTED_DATE, CURRENT_DATE())) as OLDEST_VULN_DAYS
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_QUALYS
    WHERE STATUS = 'Open'
    GROUP BY HOST_ID
) v ON h.HOST_ID = v.HOST_ID
LEFT JOIN (
    -- Qualys scan status
    SELECT
        HOST_ID,
        MAX(LAST_SCAN_DATE) as LAST_SCAN_DATE,
        MAX(AGENT_STATUS) as AGENT_STATUS
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.QUALYS_OS
    GROUP BY HOST_ID
) q ON h.HOST_ID = q.HOST_ID
LEFT JOIN (
    -- Email security metrics (placeholder - needs Proofpoint integration)
    SELECT
        OPCO_ID,
        DATE_KEY,
        COUNT(*) as PHISHING_EMAILS_REPORTED,
        COUNT(CASE WHEN ACTION = 'Blocked' THEN 1 END) as MALICIOUS_EMAILS_BLOCKED
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.PROOFPOINT_MESSAGE_LOGS
    WHERE THREAT_SCORE > 80
    GROUP BY OPCO_ID, DATE_KEY
) e ON o.OPCO_ID = e.OPCO_ID AND d.DATE_KEY = e.DATE_KEY
LEFT JOIN (
    -- SOC ticket summary (placeholder - needs ServiceNow)
    SELECT
        OPCO_ID,
        DATE_KEY,
        COUNT(CASE WHEN STATUS = 'Open' THEN 1 END) as OPEN_TICKETS,
        COUNT(CASE WHEN STATUS = 'Open' AND DUE_DATE < CURRENT_DATE() THEN 1 END) as OVERDUE_TICKETS,
        AVG(RESOLUTION_TIME_HOURS) as AVG_RESOLUTION_TIME_HOURS
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_SOC_TICKETS  -- To be created
    GROUP BY OPCO_ID, DATE_KEY
) t ON o.OPCO_ID = t.OPCO_ID AND d.DATE_KEY = t.DATE_KEY

WHERE d.FULL_DATE >= DATEADD('month', -6, CURRENT_DATE());  -- 6 months for operational
```

---

### 1.2 Row-Level Security (RLS)

**Purpose**: Ensure users only see data for their OpCo/Division

```sql
-- ============================================================================
-- ROW-LEVEL SECURITY FOR POWER BI
-- Purpose: Filter data by user's OpCo/Division assignment
-- ============================================================================

-- Step 1: Create user-to-OpCo mapping table
CREATE TABLE DEV_REPORTING.SECURITY_ANALYTICS.CFG_POWERBI_USER_ACCESS (
    USER_EMAIL VARCHAR PRIMARY KEY,
    ALLOWED_OPCO_IDS ARRAY,  -- Array of OPCO_IDs user can access
    ALLOWED_DIVISIONS ARRAY,
    ACCESS_LEVEL VARCHAR,  -- 'GLOBAL', 'DIVISION', 'OPCO'
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    GRANTED_DATE DATE,
    GRANTED_BY VARCHAR
);

-- Step 2: Insert user access mappings
INSERT INTO DEV_REPORTING.SECURITY_ANALYTICS.CFG_POWERBI_USER_ACCESS VALUES
-- Global access (CISO, executives)
('ciso@GenericCorp.com', NULL, NULL, 'GLOBAL', TRUE, CURRENT_DATE(), 'SYSTEM'),
('cfo@GenericCorp.com', NULL, NULL, 'GLOBAL', TRUE, CURRENT_DATE(), 'SYSTEM'),

-- Division-level access
('division.head.americas@GenericCorp.com', NULL, ARRAY_CONSTRUCT('Americas'), 'DIVISION', TRUE, CURRENT_DATE(), 'SYSTEM'),
('division.head.europe@GenericCorp.com', NULL, ARRAY_CONSTRUCT('Europe'), 'DIVISION', TRUE, CURRENT_DATE(), 'SYSTEM'),

-- OpCo-level access
('opco.manager.1@GenericCorp.com', ARRAY_CONSTRUCT(101, 102, 103), NULL, 'OPCO', TRUE, CURRENT_DATE(), 'SYSTEM');

-- Step 3: Create RLS function
CREATE OR REPLACE FUNCTION DEV_REPORTING.SECURITY_ANALYTICS.FN_POWERBI_RLS_FILTER(
    user_email VARCHAR,
    opco_id NUMBER,
    division VARCHAR
)
RETURNS BOOLEAN
AS
$$
    SELECT
        CASE
            -- Global access users can see everything
            WHEN (
                SELECT ACCESS_LEVEL
                FROM DEV_REPORTING.SECURITY_ANALYTICS.CFG_POWERBI_USER_ACCESS
                WHERE USER_EMAIL = user_email AND IS_ACTIVE = TRUE
            ) = 'GLOBAL' THEN TRUE

            -- Division-level users can see their division
            WHEN (
                SELECT ACCESS_LEVEL
                FROM DEV_REPORTING.SECURITY_ANALYTICS.CFG_POWERBI_USER_ACCESS
                WHERE USER_EMAIL = user_email AND IS_ACTIVE = TRUE
            ) = 'DIVISION'
            AND division IN (
                SELECT VALUE
                FROM DEV_REPORTING.SECURITY_ANALYTICS.CFG_POWERBI_USER_ACCESS,
                LATERAL FLATTEN(INPUT => ALLOWED_DIVISIONS)
                WHERE USER_EMAIL = user_email
            ) THEN TRUE

            -- OpCo-level users can see their OpCos
            WHEN (
                SELECT ACCESS_LEVEL
                FROM DEV_REPORTING.SECURITY_ANALYTICS.CFG_POWERBI_USER_ACCESS
                WHERE USER_EMAIL = user_email AND IS_ACTIVE = TRUE
            ) = 'OPCO'
            AND opco_id IN (
                SELECT VALUE
                FROM DEV_REPORTING.SECURITY_ANALYTICS.CFG_POWERBI_USER_ACCESS,
                LATERAL FLATTEN(INPUT => ALLOWED_OPCO_IDS)
                WHERE USER_EMAIL = user_email
            ) THEN TRUE

            -- Default: no access
            ELSE FALSE
        END
$$;

-- Step 4: Apply RLS to Power BI views
CREATE OR REPLACE SECURE VIEW DEV_REPORTING.SECURITY_ANALYTICS.VW_POWERBI_EXECUTIVE_DASHBOARD_RLS AS
SELECT *
FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_POWERBI_EXECUTIVE_DASHBOARD
WHERE DEV_REPORTING.SECURITY_ANALYTICS.FN_POWERBI_RLS_FILTER(
    CURRENT_USER(),  -- Power BI passes authenticated user email
    (SELECT OPCO_ID FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_OPCO WHERE OPCO_NAME = "Operating Company"),
    "Division"
) = TRUE;

-- Grant to Power BI role
GRANT SELECT ON DEV_REPORTING.SECURITY_ANALYTICS.VW_POWERBI_EXECUTIVE_DASHBOARD_RLS TO ROLE POWERBI_READER;
```

---

### 1.3 Aggregated Tables for Performance

**Purpose**: Pre-aggregate data for faster Power BI performance

```sql
-- ============================================================================
-- AGGREGATED TABLES FOR POWER BI PERFORMANCE
-- Purpose: Reduce query time for large datasets
-- ============================================================================

-- Daily aggregations by OpCo
CREATE TABLE DEV_REPORTING.SECURITY_ANALYTICS.TBL_POWERBI_DAILY_AGGREGATES (
    AGG_DATE DATE,
    OPCO_ID NUMBER,
    OPCO_NAME VARCHAR,
    DIVISION VARCHAR,
    REGION VARCHAR,

    -- Pre-calculated metrics
    TOTAL_ASSETS NUMBER,
    EDR_PROTECTED_ASSETS NUMBER,
    EDR_COVERAGE_PCT FLOAT,

    TOTAL_CRITICAL_VULNS NUMBER,
    TOTAL_HIGH_VULNS NUMBER,
    AVG_VULN_AGE_DAYS FLOAT,

    PHISHING_EMAILS_COUNT NUMBER,
    PHISHING_CLICK_RATE_PCT FLOAT,

    SOC_TICKETS_OPENED NUMBER,
    SOC_TICKETS_RESOLVED NUMBER,
    SOC_TICKETS_SLA_MET_PCT FLOAT,

    OVERALL_SECURITY_HEALTH_SCORE FLOAT,

    CALCULATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),

    PRIMARY KEY (AGG_DATE, OPCO_ID)
);

-- Populate aggregates (run daily via task)
CREATE OR REPLACE PROCEDURE DEV_REPORTING.SECURITY_ANALYTICS.SP_POPULATE_POWERBI_AGGREGATES()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
    -- Delete existing data for today
    DELETE FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_POWERBI_DAILY_AGGREGATES
    WHERE AGG_DATE = CURRENT_DATE();

    -- Insert fresh aggregates
    INSERT INTO DEV_REPORTING.SECURITY_ANALYTICS.TBL_POWERBI_DAILY_AGGREGATES
    SELECT
        CURRENT_DATE() as AGG_DATE,
        o.OPCO_ID,
        o.OPCO_NAME,
        o.DIVISION,
        o.REGION,

        -- Assets
        COUNT(DISTINCT h.HOST_ID) as TOTAL_ASSETS,
        COUNT(DISTINCT CASE WHEN edr.ENDPOINT_ID IS NOT NULL THEN h.HOST_ID END) as EDR_PROTECTED_ASSETS,
        ROUND(EDR_PROTECTED_ASSETS * 100.0 / NULLIF(TOTAL_ASSETS, 0), 2) as EDR_COVERAGE_PCT,

        -- Vulnerabilities
        COUNT(CASE WHEN v.SEVERITY = 'CRITICAL' AND v.STATUS = 'Open' THEN 1 END) as TOTAL_CRITICAL_VULNS,
        COUNT(CASE WHEN v.SEVERITY = 'HIGH' AND v.STATUS = 'Open' THEN 1 END) as TOTAL_HIGH_VULNS,
        AVG(DATEDIFF('day', v.FIRST_DETECTED_DATE, CURRENT_DATE())) as AVG_VULN_AGE_DAYS,

        -- Phishing (placeholder)
        0 as PHISHING_EMAILS_COUNT,
        0 as PHISHING_CLICK_RATE_PCT,

        -- SOC Tickets (placeholder)
        0 as SOC_TICKETS_OPENED,
        0 as SOC_TICKETS_RESOLVED,
        0 as SOC_TICKETS_SLA_MET_PCT,

        -- Overall health score
        ROUND(EDR_COVERAGE_PCT * 0.5 + (100 - AVG_VULN_AGE_DAYS/10) * 0.5, 2) as OVERALL_SECURITY_HEALTH_SCORE,

        CURRENT_TIMESTAMP()

    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_OPCO o
    LEFT JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST h ON o.OPCO_ID = h.OPCO_ID
    LEFT JOIN (
        SELECT ENDPOINT_ID FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.CROWDSTRIKE WHERE AGENT_STATUS = 'Normal'
        UNION
        SELECT ENDPOINT_ID FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.SENTINELONE WHERE AGENT_STATUS = 'Active'
        -- ... other EDR sources
    ) edr ON h.HOST_ID = edr.ENDPOINT_ID
    LEFT JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_QUALYS v ON h.HOST_ID = v.HOST_ID

    GROUP BY o.OPCO_ID, o.OPCO_NAME, o.DIVISION, o.REGION;

    RETURN 'Power BI aggregates populated for ' || CURRENT_DATE();
END;
$$;

-- Schedule daily aggregation
CREATE TASK DEV_REPORTING.SECURITY_ANALYTICS.TASK_POPULATE_POWERBI_AGGREGATES
    WAREHOUSE = DEV_WH
    SCHEDULE = 'USING CRON 0 7 * * * UTC'  -- 7:00 AM UTC (after KPI calculations)
    COMMENT = 'Populate Power BI aggregated tables for performance'
AS
    CALL DEV_REPORTING.SECURITY_ANALYTICS.SP_POPULATE_POWERBI_AGGREGATES();
```

---

### 1.4 Power BI Connection Configuration

**Connection String**:
```
Server: crh_account.snowflakecomputing.com
Database: DEV_REPORTING
Schema: SECURITY_ANALYTICS
Warehouse: DEV_WH
Role: POWERBI_READER
Authentication: Azure AD (SSO recommended) or Username/Password
```

**Refresh Schedule**:
- **Executive Dashboard**: Daily @ 8:00 AM UTC
- **Operational Dashboard**: Every 4 hours

**Performance Optimization**:
- Use **Import Mode** for aggregated tables (TBL_POWERBI_DAILY_AGGREGATES)
- Use **DirectQuery** for real-time operational views (optional)
- Enable **incremental refresh** for date ranges

---

## Enhancement 2: Near Real-Time Capabilities

### Business Context

**From Presentation**: "Near Real-Time Insights: Quick issue spotting and response"

**Current State**: Batch processing (daily/hourly tasks)
**Target State**: Near real-time ingestion and monitoring for critical events

### 2.1 Snowpipe Implementation

**Purpose**: Auto-ingest critical security events as they arrive

```sql
-- ============================================================================
-- SNOWPIPE: REAL-TIME EDR THREAT INGESTION
-- Purpose: Automatically ingest EDR threats as files land in S3/Azure
-- ============================================================================

-- Step 1: Create stage for incoming EDR threat files
CREATE STAGE IF NOT EXISTS DEV_LANDING.SECURITY_ANALYTICS.STAGE_EDR_THREATS_REALTIME
    URL = 's3://GenericCorp-security-data/edr-threats/'  -- Replace with actual S3/Azure path
    CREDENTIALS = (AWS_KEY_ID = 'xxx' AWS_SECRET_KEY = 'xxx')  -- Or use IAM role
    FILE_FORMAT = (
        TYPE = JSON
        STRIP_OUTER_ARRAY = TRUE
        DATE_FORMAT = 'AUTO'
        TIMESTAMP_FORMAT = 'AUTO'
    );

-- Step 2: Create real-time landing table
CREATE TABLE IF NOT EXISTS DEV_LANDING.SECURITY_ANALYTICS.L_EDR_THREATS_REALTIME (
    THREAT_ID VARCHAR,
    ENDPOINT_ID VARCHAR,
    THREAT_NAME VARCHAR,
    THREAT_TYPE VARCHAR,
    SEVERITY VARCHAR,
    DETECTION_TIME TIMESTAMP,
    SOURCE_SYSTEM VARCHAR,
    RAW_JSON VARIANT,
    INGESTED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Step 3: Create Snowpipe for auto-ingestion
CREATE PIPE DEV_LANDING.SECURITY_ANALYTICS.PIPE_EDR_THREATS_REALTIME
    AUTO_INGEST = TRUE
    COMMENT = 'Auto-ingest EDR threats for near real-time monitoring'
AS
COPY INTO DEV_LANDING.SECURITY_ANALYTICS.L_EDR_THREATS_REALTIME (
    THREAT_ID,
    ENDPOINT_ID,
    THREAT_NAME,
    THREAT_TYPE,
    SEVERITY,
    DETECTION_TIME,
    SOURCE_SYSTEM,
    RAW_JSON
)
FROM (
    SELECT
        $1:threat_id::VARCHAR,
        $1:endpoint_id::VARCHAR,
        $1:threat_name::VARCHAR,
        $1:threat_type::VARCHAR,
        $1:severity::VARCHAR,
        $1:detection_time::TIMESTAMP,
        $1:source::VARCHAR,
        $1
    FROM @DEV_LANDING.SECURITY_ANALYTICS.STAGE_EDR_THREATS_REALTIME
)
FILE_FORMAT = (TYPE = JSON);

-- Step 4: Show pipe status and notification channel
SHOW PIPES LIKE 'PIPE_EDR_THREATS_REALTIME';
-- Copy the notification_channel (SQS queue ARN or Event Grid) and configure in S3/Azure
```

**Configuration in AWS S3**:
1. Go to S3 bucket properties
2. Create Event Notification
3. Set event type: "All object create events"
4. Set destination: SQS queue (use notification_channel from SHOW PIPES)

---

### 2.2 Real-Time Monitoring Views

**Purpose**: Query data from the last 15 minutes for operational dashboards

```sql
-- ============================================================================
-- REAL-TIME THREAT MONITORING VIEW
-- Purpose: Show threats detected in last 15 minutes
-- ============================================================================

CREATE OR REPLACE VIEW DEV_REPORTING.SECURITY_ANALYTICS.VW_REALTIME_THREATS_LAST_15MIN AS
SELECT
    t.THREAT_ID,
    t.ENDPOINT_ID,
    h.HOSTNAME,
    h.IP_ADDRESS,
    h.OPCO_ID,
    o.OPCO_NAME,
    t.THREAT_NAME,
    t.THREAT_TYPE,
    t.SEVERITY,
    t.DETECTION_TIME,
    t.SOURCE_SYSTEM,
    DATEDIFF('minute', t.DETECTION_TIME, CURRENT_TIMESTAMP()) as MINUTES_AGO,

    -- Risk scoring
    CASE
        WHEN t.SEVERITY = 'CRITICAL' THEN 100
        WHEN t.SEVERITY = 'HIGH' THEN 75
        WHEN t.SEVERITY = 'MEDIUM' THEN 50
        WHEN t.SEVERITY = 'LOW' THEN 25
        ELSE 10
    END as RISK_SCORE,

    -- Action status (placeholder - would link to response system)
    'NEW' as ACTION_STATUS,
    NULL as ASSIGNED_TO,
    NULL as INCIDENT_ID

FROM DEV_LANDING.SECURITY_ANALYTICS.L_EDR_THREATS_REALTIME t
LEFT JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST h ON t.ENDPOINT_ID = h.HOST_ID
LEFT JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_OPCO o ON h.OPCO_ID = o.OPCO_ID

WHERE t.DETECTION_TIME >= DATEADD('minute', -15, CURRENT_TIMESTAMP())

ORDER BY t.DETECTION_TIME DESC, RISK_SCORE DESC;

-- Grant access
GRANT SELECT ON DEV_REPORTING.SECURITY_ANALYTICS.VW_REALTIME_THREATS_LAST_15MIN TO ROLE ANALYST;
```

```sql
-- ============================================================================
-- REAL-TIME VULNERABILITY SCAN COMPLETIONS
-- Purpose: Show scans completed in last hour
-- ============================================================================

CREATE OR REPLACE VIEW DEV_REPORTING.SECURITY_ANALYTICS.VW_REALTIME_SCANS_LAST_HOUR AS
SELECT
    HOST_ID,
    HOSTNAME,
    SCAN_TYPE,
    SCAN_START_TIME,
    SCAN_END_TIME,
    DATEDIFF('minute', SCAN_START_TIME, SCAN_END_TIME) as SCAN_DURATION_MINUTES,
    VULNERABILITIES_FOUND,
    SCAN_STATUS,
    DATEDIFF('minute', SCAN_END_TIME, CURRENT_TIMESTAMP()) as MINUTES_AGO

FROM DEV_LANDING.SECURITY_ANALYTICS.L_QUALYS_SCAN_RESULTS

WHERE SCAN_END_TIME >= DATEADD('hour', -1, CURRENT_TIMESTAMP())
    AND SCAN_STATUS = 'COMPLETED'

ORDER BY SCAN_END_TIME DESC;
```

---

### 2.3 Stream Processing for Change Data Capture

**Purpose**: Track changes to critical tables for audit and alerting

```sql
-- ============================================================================
-- SNOWFLAKE STREAMS: CHANGE DATA CAPTURE
-- Purpose: Track changes to vulnerability status for alerting
-- ============================================================================

-- Create stream on FACT_QUALYS to detect new critical vulnerabilities
CREATE STREAM DEV_TRANSFORMATION.SECURITY_ANALYTICS.STREAM_NEW_CRITICAL_VULNS
    ON TABLE DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_QUALYS
    COMMENT = 'Capture new critical vulnerabilities for real-time alerting';

-- Create processing task to act on stream data
CREATE TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_PROCESS_NEW_CRITICAL_VULNS
    WAREHOUSE = DEV_WH
    SCHEDULE = '5 MINUTE'  -- Check every 5 minutes
    WHEN SYSTEM$STREAM_HAS_DATA('DEV_TRANSFORMATION.SECURITY_ANALYTICS.STREAM_NEW_CRITICAL_VULNS')
AS
INSERT INTO DEV_REPORTING.SECURITY_ANALYTICS.ALERT_NEW_CRITICAL_VULNERABILITIES
SELECT
    CURRENT_TIMESTAMP() as ALERT_TIME,
    s.HOST_ID,
    h.HOSTNAME,
    h.OPCO_ID,
    o.OPCO_NAME,
    s.VULN_ID,
    v.VULN_TITLE,
    s.SEVERITY,
    s.CVSS_SCORE,
    s.FIRST_DETECTED_DATE,
    'NEW_CRITICAL_VULN' as ALERT_TYPE,
    FALSE as ACKNOWLEDGED
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.STREAM_NEW_CRITICAL_VULNS s
LEFT JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST h ON s.HOST_ID = h.HOST_ID
LEFT JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_OPCO o ON h.OPCO_ID = o.OPCO_ID
LEFT JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_QUALYS_VULN v ON s.VULN_ID = v.VULN_ID
WHERE s.METADATA$ACTION = 'INSERT'  -- Only new rows
    AND s.SEVERITY = 'CRITICAL';

-- Create alert table if not exists
CREATE TABLE IF NOT EXISTS DEV_REPORTING.SECURITY_ANALYTICS.ALERT_NEW_CRITICAL_VULNERABILITIES (
    ALERT_TIME TIMESTAMP,
    HOST_ID VARCHAR,
    HOSTNAME VARCHAR,
    OPCO_ID NUMBER,
    OPCO_NAME VARCHAR,
    VULN_ID VARCHAR,
    VULN_TITLE VARCHAR,
    SEVERITY VARCHAR,
    CVSS_SCORE FLOAT,
    FIRST_DETECTED_DATE DATE,
    ALERT_TYPE VARCHAR,
    ACKNOWLEDGED BOOLEAN,
    ACKNOWLEDGED_BY VARCHAR,
    ACKNOWLEDGED_AT TIMESTAMP
);
```

---

## Enhancement 3: Unified User Dimension

### Business Context

**From Presentation**: "Common Data Model: Link entities like users and devices"

**Current Gap**: No centralized DIM_USER table; only ANCON_USERS exists

### 3.1 Unified User Dimension Design

```sql
-- ============================================================================
-- DIM_USER: UNIFIED USER DIMENSION
-- Purpose: Central repository for all user/identity data
-- Type: SCD Type 2 (track history)
-- ============================================================================

CREATE TABLE DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_USER (
    -- Surrogate key
    USER_KEY NUMBER AUTOINCREMENT PRIMARY KEY,

    -- Natural key
    USER_ID VARCHAR NOT NULL,  -- Unique identifier (email or employee ID)
    EMAIL VARCHAR,
    ALTERNATE_EMAIL VARCHAR,

    -- Personal information
    FULL_NAME VARCHAR,
    FIRST_NAME VARCHAR,
    LAST_NAME VARCHAR,
    DISPLAY_NAME VARCHAR,

    -- Organizational attributes
    OPCO_ID NUMBER,
    DEPARTMENT VARCHAR,
    JOB_TITLE VARCHAR,
    MANAGER_EMAIL VARCHAR,
    EMPLOYEE_TYPE VARCHAR,  -- 'FTE', 'Contractor', 'Vendor', 'Service Account'

    -- Employment status
    IS_ACTIVE BOOLEAN,
    HIRE_DATE DATE,
    TERMINATION_DATE DATE,
    LAST_LOGON_DATE TIMESTAMP,

    -- Security attributes
    IS_PRIVILEGED_USER BOOLEAN,  -- Admin, root, etc.
    IS_SERVICE_ACCOUNT BOOLEAN,
    REQUIRES_MFA BOOLEAN DEFAULT TRUE,
    REQUIRES_SECURITY_TRAINING BOOLEAN DEFAULT TRUE,

    -- SCD Type 2 fields
    VALID_FROM TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    VALID_TO TIMESTAMP DEFAULT TO_TIMESTAMP('9999-12-31'),
    IS_CURRENT BOOLEAN DEFAULT TRUE,

    -- Audit fields
    SOURCE_SYSTEM VARCHAR,  -- 'Active Directory', 'HR System', 'ANCON', etc.
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),

    -- Constraints
    CONSTRAINT FK_USER_OPCO FOREIGN KEY (OPCO_ID)
        REFERENCES DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_OPCO(OPCO_ID) RELY,

    CONSTRAINT UQ_USER_CURRENT UNIQUE (USER_ID, IS_CURRENT)
);

-- Indexes for performance
CREATE INDEX IDX_USER_EMAIL ON DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_USER(EMAIL);
CREATE INDEX IDX_USER_OPCO ON DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_USER(OPCO_ID);
CREATE INDEX IDX_USER_ACTIVE ON DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_USER(IS_ACTIVE, IS_CURRENT);
```

---

### 3.2 Data Source Integration

**Sources to integrate**:
1. Active Directory (primary source)
2. HR System (employment data)
3. ANCON_USERS (existing)
4. MetaCompliance (training status)
5. ServiceNow (incident assignees)

```sql
-- ============================================================================
-- LANDING TABLES FOR USER DATA SOURCES
-- ============================================================================

-- 1. Active Directory users
CREATE TABLE DEV_LANDING.SECURITY_ANALYTICS.L_ACTIVE_DIRECTORY_USERS (
    SAMACCOUNTNAME VARCHAR,
    USER_PRINCIPAL_NAME VARCHAR,
    DISTINGUISHED_NAME VARCHAR,
    DISPLAY_NAME VARCHAR,
    GIVEN_NAME VARCHAR,
    SURNAME VARCHAR,
    EMAIL VARCHAR,
    DEPARTMENT VARCHAR,
    TITLE VARCHAR,
    MANAGER_DN VARCHAR,
    ENABLED BOOLEAN,
    LAST_LOGON_DATE TIMESTAMP,
    WHEN_CREATED TIMESTAMP,
    LOAD_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- 2. HR System (employment data)
CREATE TABLE DEV_LANDING.SECURITY_ANALYTICS.L_HR_EMPLOYEES (
    EMPLOYEE_ID VARCHAR,
    EMAIL VARCHAR,
    FULL_NAME VARCHAR,
    OPCO_CODE VARCHAR,
    DEPARTMENT VARCHAR,
    JOB_TITLE VARCHAR,
    MANAGER_EMAIL VARCHAR,
    EMPLOYEE_TYPE VARCHAR,
    HIRE_DATE DATE,
    TERMINATION_DATE DATE,
    IS_ACTIVE BOOLEAN,
    LOAD_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

---

### 3.3 User Dimension Load Procedure

```sql
-- ============================================================================
-- SP_LOAD_DIM_USER: Populate unified user dimension
-- Purpose: Merge data from multiple sources into DIM_USER
-- Type: SCD Type 2 implementation
-- ============================================================================

CREATE OR REPLACE PROCEDURE DEV_TRANSFORMATION.SECURITY_ANALYTICS.SP_LOAD_DIM_USER()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
    -- Stage 1: Merge Active Directory users
    MERGE INTO DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_USER tgt
    USING (
        SELECT DISTINCT
            USER_PRINCIPAL_NAME as USER_ID,
            EMAIL,
            NULL as ALTERNATE_EMAIL,
            DISPLAY_NAME as FULL_NAME,
            GIVEN_NAME as FIRST_NAME,
            SURNAME as LAST_NAME,
            DISPLAY_NAME,
            NULL as OPCO_ID,  -- Will be enriched from HR
            DEPARTMENT,
            TITLE as JOB_TITLE,
            NULL as MANAGER_EMAIL,  -- Will resolve from MANAGER_DN
            'FTE' as EMPLOYEE_TYPE,
            ENABLED as IS_ACTIVE,
            NULL as HIRE_DATE,
            NULL as TERMINATION_DATE,
            LAST_LOGON_DATE,
            FALSE as IS_PRIVILEGED_USER,  -- Will be identified separately
            FALSE as IS_SERVICE_ACCOUNT,
            TRUE as REQUIRES_MFA,
            TRUE as REQUIRES_SECURITY_TRAINING,
            'Active Directory' as SOURCE_SYSTEM
        FROM DEV_LANDING.SECURITY_ANALYTICS.L_ACTIVE_DIRECTORY_USERS
        WHERE LOAD_TIMESTAMP >= DATEADD('day', -1, CURRENT_TIMESTAMP())
    ) src
    ON tgt.USER_ID = src.USER_ID AND tgt.IS_CURRENT = TRUE
    WHEN MATCHED AND (
        tgt.FULL_NAME != src.FULL_NAME OR
        tgt.DEPARTMENT != src.DEPARTMENT OR
        tgt.IS_ACTIVE != src.IS_ACTIVE
    ) THEN UPDATE SET
        tgt.IS_CURRENT = FALSE,
        tgt.VALID_TO = CURRENT_TIMESTAMP(),
        tgt.UPDATED_AT = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN INSERT (
        USER_ID, EMAIL, ALTERNATE_EMAIL, FULL_NAME, FIRST_NAME, LAST_NAME,
        DISPLAY_NAME, OPCO_ID, DEPARTMENT, JOB_TITLE, MANAGER_EMAIL,
        EMPLOYEE_TYPE, IS_ACTIVE, HIRE_DATE, TERMINATION_DATE, LAST_LOGON_DATE,
        IS_PRIVILEGED_USER, IS_SERVICE_ACCOUNT, REQUIRES_MFA, REQUIRES_SECURITY_TRAINING,
        SOURCE_SYSTEM, IS_CURRENT, VALID_FROM
    ) VALUES (
        src.USER_ID, src.EMAIL, src.ALTERNATE_EMAIL, src.FULL_NAME, src.FIRST_NAME, src.LAST_NAME,
        src.DISPLAY_NAME, src.OPCO_ID, src.DEPARTMENT, src.JOB_TITLE, src.MANAGER_EMAIL,
        src.EMPLOYEE_TYPE, src.IS_ACTIVE, src.HIRE_DATE, src.TERMINATION_DATE, src.LAST_LOGON_DATE,
        src.IS_PRIVILEGED_USER, src.IS_SERVICE_ACCOUNT, src.REQUIRES_MFA, src.REQUIRES_SECURITY_TRAINING,
        src.SOURCE_SYSTEM, TRUE, CURRENT_TIMESTAMP()
    );

    -- Stage 2: Enrich with HR data (OpCo, hire date, etc.)
    UPDATE DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_USER u
    SET
        u.OPCO_ID = (
            SELECT o.OPCO_ID
            FROM DEV_LANDING.SECURITY_ANALYTICS.L_HR_EMPLOYEES hr
            JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_OPCO o ON hr.OPCO_CODE = o.OPCO_CODE
            WHERE hr.EMAIL = u.EMAIL
            LIMIT 1
        ),
        u.HIRE_DATE = (
            SELECT hr.HIRE_DATE
            FROM DEV_LANDING.SECURITY_ANALYTICS.L_HR_EMPLOYEES hr
            WHERE hr.EMAIL = u.EMAIL
            LIMIT 1
        ),
        u.TERMINATION_DATE = (
            SELECT hr.TERMINATION_DATE
            FROM DEV_LANDING.SECURITY_ANALYTICS.L_HR_EMPLOYEES hr
            WHERE hr.EMAIL = u.EMAIL
            LIMIT 1
        ),
        u.UPDATED_AT = CURRENT_TIMESTAMP()
    WHERE u.IS_CURRENT = TRUE
        AND u.OPCO_ID IS NULL;

    RETURN 'DIM_USER loaded successfully. Rows updated: ' || SQLROWCOUNT;
END;
$$;

-- Schedule user dimension load
CREATE TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_LOAD_DIM_USER
    WAREHOUSE = DEV_WH
    SCHEDULE = 'USING CRON 0 3 * * * UTC'  -- Daily at 3:00 AM UTC
    COMMENT = 'Load unified user dimension from AD and HR sources'
AS
    CALL DEV_TRANSFORMATION.SECURITY_ANALYTICS.SP_LOAD_DIM_USER();
```

---

## Enhancement 4: Data Quality Dashboard

### Business Context

**From Presentation**: "One Platform | Trusted Data | Executive Insight"

**Requirement**: Transparency into data quality to build trust in metrics

### 4.1 Data Quality Metrics Framework

```sql
-- ============================================================================
-- DATA QUALITY METRICS TABLE
-- Purpose: Store data quality scores and issues
-- ============================================================================

CREATE TABLE DEV_TRANSFORMATION.SECURITY_ANALYTICS.DQ_METRICS (
    METRIC_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    TABLE_NAME VARCHAR,
    METRIC_NAME VARCHAR,  -- 'completeness', 'accuracy', 'freshness', 'consistency'
    METRIC_VALUE FLOAT,  -- Score 0-100
    THRESHOLD FLOAT,  -- Minimum acceptable value
    STATUS VARCHAR,  -- 'PASS', 'WARNING', 'FAIL'
    ISSUE_COUNT NUMBER,
    ISSUE_DETAILS VARIANT,  -- JSON with specific issues
    MEASURED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    MEASURED_BY VARCHAR DEFAULT CURRENT_USER()
);

-- Create index for fast querying
CREATE INDEX IDX_DQ_TABLE ON DEV_TRANSFORMATION.SECURITY_ANALYTICS.DQ_METRICS(TABLE_NAME, MEASURED_AT);
```

---

### 4.2 Data Quality Calculation Procedure

```sql
-- ============================================================================
-- SP_CALCULATE_DATA_QUALITY_METRICS
-- Purpose: Calculate comprehensive DQ scores for all tables
-- ============================================================================

CREATE OR REPLACE PROCEDURE DEV_TRANSFORMATION.SECURITY_ANALYTICS.SP_CALCULATE_DATA_QUALITY_METRICS()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
    -- Clear today's metrics
    DELETE FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DQ_METRICS
    WHERE DATE(MEASURED_AT) = CURRENT_DATE();

    -- ==============================================================
    -- COMPLETENESS CHECK: % of non-null values in critical columns
    -- ==============================================================

    -- DIM_HOST completeness
    INSERT INTO DEV_TRANSFORMATION.SECURITY_ANALYTICS.DQ_METRICS (
        TABLE_NAME, METRIC_NAME, METRIC_VALUE, THRESHOLD, STATUS, ISSUE_COUNT
    )
    SELECT
        'DIM_HOST' as TABLE_NAME,
        'completeness' as METRIC_NAME,
        ROUND(
            (COUNT(*) - COUNT(CASE WHEN HOSTNAME IS NULL THEN 1 END)) * 100.0 / COUNT(*),
        2) as METRIC_VALUE,
        95.0 as THRESHOLD,
        CASE
            WHEN METRIC_VALUE >= 95 THEN 'PASS'
            WHEN METRIC_VALUE >= 90 THEN 'WARNING'
            ELSE 'FAIL'
        END as STATUS,
        COUNT(CASE WHEN HOSTNAME IS NULL THEN 1 END) as ISSUE_COUNT
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST
    WHERE IS_CURRENT = TRUE;

    -- ==============================================================
    -- ACCURACY CHECK: % of valid values (business rules)
    -- ==============================================================

    -- IP address format validation
    INSERT INTO DEV_TRANSFORMATION.SECURITY_ANALYTICS.DQ_METRICS (
        TABLE_NAME, METRIC_NAME, METRIC_VALUE, THRESHOLD, STATUS, ISSUE_COUNT
    )
    SELECT
        'DIM_HOST',
        'accuracy',
        ROUND(
            COUNT(CASE
                WHEN REGEXP_LIKE(IP_ADDRESS, '^[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}$')
                THEN 1
            END) * 100.0 / COUNT(*),
        2),
        98.0,
        CASE
            WHEN METRIC_VALUE >= 98 THEN 'PASS'
            WHEN METRIC_VALUE >= 95 THEN 'WARNING'
            ELSE 'FAIL'
        END,
        COUNT(CASE
            WHEN NOT REGEXP_LIKE(IP_ADDRESS, '^[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}$')
            THEN 1
        END)
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST
    WHERE IS_CURRENT = TRUE AND IP_ADDRESS IS NOT NULL;

    -- ==============================================================
    -- FRESHNESS CHECK: Hours since last update
    -- ==============================================================

    -- EDR data freshness
    INSERT INTO DEV_TRANSFORMATION.SECURITY_ANALYTICS.DQ_METRICS (
        TABLE_NAME, METRIC_NAME, METRIC_VALUE, THRESHOLD, STATUS, ISSUE_COUNT
    )
    SELECT
        'CROWDSTRIKE',
        'freshness',
        24 - DATEDIFF('hour', MAX(LAST_SEEN_DATE), CURRENT_TIMESTAMP()),  -- Convert to score: 24-hours_old
        12.0,  -- Threshold: data should be < 12 hours old
        CASE
            WHEN METRIC_VALUE >= 12 THEN 'PASS'
            WHEN METRIC_VALUE >= 6 THEN 'WARNING'
            ELSE 'FAIL'
        END,
        COUNT(CASE WHEN DATEDIFF('hour', LAST_SEEN_DATE, CURRENT_TIMESTAMP()) > 24 THEN 1 END)
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.CROWDSTRIKE;

    -- ==============================================================
    -- CONSISTENCY CHECK: Duplicate records
    -- ==============================================================

    INSERT INTO DEV_TRANSFORMATION.SECURITY_ANALYTICS.DQ_METRICS (
        TABLE_NAME, METRIC_NAME, METRIC_VALUE, THRESHOLD, STATUS, ISSUE_COUNT
    )
    WITH duplicates AS (
        SELECT HOSTNAME, COUNT(*) as CNT
        FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST
        WHERE IS_CURRENT = TRUE
        GROUP BY HOSTNAME
        HAVING CNT > 1
    )
    SELECT
        'DIM_HOST',
        'consistency',
        100 - (SELECT COUNT(*) FROM duplicates) * 100.0 / (SELECT COUNT(*) FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST WHERE IS_CURRENT = TRUE),
        99.0,
        CASE
            WHEN METRIC_VALUE >= 99 THEN 'PASS'
            WHEN METRIC_VALUE >= 95 THEN 'WARNING'
            ELSE 'FAIL'
        END,
        (SELECT COUNT(*) FROM duplicates);

    -- ==============================================================
    -- REFERENTIAL INTEGRITY CHECK: Orphaned records
    -- ==============================================================

    INSERT INTO DEV_TRANSFORMATION.SECURITY_ANALYTICS.DQ_METRICS (
        TABLE_NAME, METRIC_NAME, METRIC_VALUE, THRESHOLD, STATUS, ISSUE_COUNT
    )
    SELECT
        'FACT_QUALYS',
        'referential_integrity',
        ROUND(
            (COUNT(*) - COUNT(CASE WHEN h.HOST_ID IS NULL THEN 1 END)) * 100.0 / COUNT(*),
        2),
        100.0,
        CASE
            WHEN METRIC_VALUE = 100 THEN 'PASS'
            WHEN METRIC_VALUE >= 98 THEN 'WARNING'
            ELSE 'FAIL'
        END,
        COUNT(CASE WHEN h.HOST_ID IS NULL THEN 1 END)
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_QUALYS f
    LEFT JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST h ON f.HOST_ID = h.HOST_ID;

    RETURN 'Data quality metrics calculated for ' || CURRENT_DATE();
END;
$$;

-- Schedule DQ calculation
CREATE TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_CALCULATE_DQ_METRICS
    WAREHOUSE = DEV_WH
    SCHEDULE = 'USING CRON 0 6 * * * UTC'  -- Daily at 6:00 AM UTC
    COMMENT = 'Calculate data quality metrics for all tables'
AS
    CALL DEV_TRANSFORMATION.SECURITY_ANALYTICS.SP_CALCULATE_DATA_QUALITY_METRICS();
```

---

### 4.3 Data Quality Dashboard View

```sql
-- ============================================================================
-- DATA QUALITY DASHBOARD VIEW (for Power BI)
-- ============================================================================

CREATE OR REPLACE VIEW DEV_REPORTING.SECURITY_ANALYTICS.VW_DATA_QUALITY_DASHBOARD AS
WITH latest_metrics AS (
    SELECT
        TABLE_NAME,
        METRIC_NAME,
        METRIC_VALUE,
        THRESHOLD,
        STATUS,
        ISSUE_COUNT,
        MEASURED_AT,
        ROW_NUMBER() OVER (PARTITION BY TABLE_NAME, METRIC_NAME ORDER BY MEASURED_AT DESC) as RN
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DQ_METRICS
    WHERE MEASURED_AT >= DATEADD('day', -7, CURRENT_DATE())
),
current_metrics AS (
    SELECT * FROM latest_metrics WHERE RN = 1
),
summary_by_table AS (
    SELECT
        TABLE_NAME,
        AVG(METRIC_VALUE) as OVERALL_DQ_SCORE,
        COUNT(CASE WHEN STATUS = 'PASS' THEN 1 END) as PASS_COUNT,
        COUNT(CASE WHEN STATUS = 'WARNING' THEN 1 END) as WARNING_COUNT,
        COUNT(CASE WHEN STATUS = 'FAIL' THEN 1 END) as FAIL_COUNT,
        SUM(ISSUE_COUNT) as TOTAL_ISSUES
    FROM current_metrics
    GROUP BY TABLE_NAME
)
SELECT
    -- Table information
    cm.TABLE_NAME as "Table Name",

    -- Individual metrics
    MAX(CASE WHEN cm.METRIC_NAME = 'completeness' THEN cm.METRIC_VALUE END) as "Completeness Score",
    MAX(CASE WHEN cm.METRIC_NAME = 'accuracy' THEN cm.METRIC_VALUE END) as "Accuracy Score",
    MAX(CASE WHEN cm.METRIC_NAME = 'freshness' THEN cm.METRIC_VALUE END) as "Freshness Score",
    MAX(CASE WHEN cm.METRIC_NAME = 'consistency' THEN cm.METRIC_VALUE END) as "Consistency Score",
    MAX(CASE WHEN cm.METRIC_NAME = 'referential_integrity' THEN cm.METRIC_VALUE END) as "Integrity Score",

    -- Overall score
    st.OVERALL_DQ_SCORE as "Overall Data Quality Score",

    -- Status breakdown
    st.PASS_COUNT as "Checks Passed",
    st.WARNING_COUNT as "Warnings",
    st.FAIL_COUNT as "Failures",
    st.TOTAL_ISSUES as "Total Issues",

    -- Rating
    CASE
        WHEN st.OVERALL_DQ_SCORE >= 95 THEN '🟢 Excellent'
        WHEN st.OVERALL_DQ_SCORE >= 85 THEN '🟡 Good'
        WHEN st.OVERALL_DQ_SCORE >= 70 THEN '🟠 Fair'
        ELSE '🔴 Poor'
    END as "Quality Rating",

    -- Last measured
    MAX(cm.MEASURED_AT) as "Last Measured"

FROM current_metrics cm
JOIN summary_by_table st ON cm.TABLE_NAME = st.TABLE_NAME

GROUP BY cm.TABLE_NAME, st.OVERALL_DQ_SCORE, st.PASS_COUNT, st.WARNING_COUNT, st.FAIL_COUNT, st.TOTAL_ISSUES

ORDER BY st.OVERALL_DQ_SCORE ASC;  -- Show worst quality first
```

---

### 4.4 Add DQ Score to KPI Views

```sql
-- ============================================================================
-- ENHANCE KPI VIEWS WITH DATA QUALITY INDICATORS
-- ============================================================================

ALTER VIEW DEV_REPORTING.SECURITY_ANALYTICS.VW_POWERBI_EXECUTIVE_DASHBOARD AS
SELECT
    -- ... existing columns ...

    -- Add Data Quality Score
    dq.OVERALL_DQ_SCORE as "Data Quality Score",
    CASE
        WHEN dq.OVERALL_DQ_SCORE >= 95 THEN '🟢 High Confidence'
        WHEN dq.OVERALL_DQ_SCORE >= 80 THEN '🟡 Medium Confidence'
        ELSE '🔴 Low Confidence'
    END as "Data Confidence Level",

    -- Data freshness
    DATEDIFF('hour', kpi.LAST_REFRESHED, CURRENT_TIMESTAMP()) as "Hours Since Update",
    CASE
        WHEN "Hours Since Update" <= 12 THEN '🟢 Fresh'
        WHEN "Hours Since Update" <= 24 THEN '🟡 Acceptable'
        ELSE '🔴 Stale'
    END as "Data Freshness Status"

FROM ... -- existing query
LEFT JOIN (
    SELECT
        AVG(METRIC_VALUE) as OVERALL_DQ_SCORE
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DQ_METRICS
    WHERE MEASURED_AT >= DATEADD('day', -1, CURRENT_DATE())
) dq;
```

---

## Implementation Sequence

### Phase 1: Power BI Integration (Week 1-2)

**Priority**: HIGH - Executive visibility

**Tasks**:
1. ☐ Create semantic layer views (8 hours)
   - VW_POWERBI_EXECUTIVE_DASHBOARD
   - VW_POWERBI_OPERATIONAL_DASHBOARD

2. ☐ Implement row-level security (8 hours)
   - CFG_POWERBI_USER_ACCESS table
   - FN_POWERBI_RLS_FILTER function
   - Secure views with RLS

3. ☐ Create aggregated tables (16 hours)
   - TBL_POWERBI_DAILY_AGGREGATES
   - SP_POPULATE_POWERBI_AGGREGATES
   - TASK_POPULATE_POWERBI_AGGREGATES

4. ☐ Power BI connection setup (8 hours)
   - Create POWERBI_READER role
   - Configure connection string
   - Test data access

5. ☐ Build initial dashboards (8 hours)
   - Executive dashboard (Top 13 KPIs)
   - Operational dashboard (asset details)

**Total Effort**: 48 hours

---

### Phase 2: Data Quality Framework (Week 2-3)

**Priority**: HIGH - Trust in data

**Tasks**:
1. ☐ Create DQ metrics table (4 hours)
2. ☐ Implement DQ calculation procedure (16 hours)
   - Completeness checks
   - Accuracy checks
   - Freshness checks
   - Consistency checks
   - Referential integrity checks

3. ☐ Create DQ dashboard view (4 hours)
4. ☐ Enhance KPI views with DQ indicators (4 hours)

**Total Effort**: 28 hours

---

### Phase 3: Unified User Dimension (Week 3-4)

**Priority**: MEDIUM - User analytics

**Tasks**:
1. ☐ Design DIM_USER schema (4 hours)
2. ☐ Create landing tables (4 hours)
   - L_ACTIVE_DIRECTORY_USERS
   - L_HR_EMPLOYEES

3. ☐ Implement load procedure (20 hours)
   - SP_LOAD_DIM_USER
   - SCD Type 2 logic
   - Multi-source merge

4. ☐ Create user analytics views (8 hours)
5. ☐ Testing and validation (4 hours)

**Total Effort**: 40 hours

---

### Phase 4: Near Real-Time Capabilities (Week 4-6)

**Priority**: MEDIUM - Operational responsiveness

**Tasks**:
1. ☐ Set up Snowpipe (16 hours)
   - Create stages
   - Create pipes
   - Configure S3/Azure notifications

2. ☐ Create real-time landing tables (8 hours)
3. ☐ Build real-time monitoring views (16 hours)
   - VW_REALTIME_THREATS_LAST_15MIN
   - VW_REALTIME_SCANS_LAST_HOUR

4. ☐ Implement stream processing (16 hours)
   - STREAM_NEW_CRITICAL_VULNS
   - TASK_PROCESS_NEW_CRITICAL_VULNS

5. ☐ Testing and validation (8 hours)

**Total Effort**: 64 hours

---

## Testing & Validation

### Test Plan

#### 1. Power BI Integration Tests

```sql
-- Test 1: Verify semantic layer view
SELECT COUNT(*) FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_POWERBI_EXECUTIVE_DASHBOARD;
-- Expected: Rows > 0

-- Test 2: Verify RLS function
SELECT DEV_REPORTING.SECURITY_ANALYTICS.FN_POWERBI_RLS_FILTER(
    'ciso@GenericCorp.com',  -- Global access user
    101,  -- Any OPCO
    'Americas'  -- Any division
);
-- Expected: TRUE

-- Test 3: Check aggregated table performance
SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_POWERBI_DAILY_AGGREGATES
WHERE AGG_DATE = CURRENT_DATE();
-- Expected: Rows for each OPCO

-- Test 4: Verify Power BI role permissions
SHOW GRANTS TO ROLE POWERBI_READER;
-- Expected: SELECT on all Power BI views
```

#### 2. Data Quality Tests

```sql
-- Test 1: Verify DQ metrics calculated
SELECT * FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DQ_METRICS
WHERE DATE(MEASURED_AT) = CURRENT_DATE();
-- Expected: Metrics for all tables

-- Test 2: Check DQ dashboard view
SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_DATA_QUALITY_DASHBOARD;
-- Expected: Summary for each table

-- Test 3: Validate thresholds
SELECT
    TABLE_NAME,
    METRIC_NAME,
    METRIC_VALUE,
    THRESHOLD,
    STATUS
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DQ_METRICS
WHERE STATUS = 'FAIL';
-- Expected: Review failures
```

#### 3. User Dimension Tests

```sql
-- Test 1: Verify user count
SELECT COUNT(*) FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_USER WHERE IS_CURRENT = TRUE;
-- Expected: Matches AD user count

-- Test 2: Check SCD Type 2 history
SELECT
    USER_ID,
    COUNT(*) as VERSION_COUNT
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_USER
GROUP BY USER_ID
HAVING COUNT(*) > 1;
-- Expected: Users with multiple versions (history)

-- Test 3: Validate OpCo enrichment
SELECT
    COUNT(*) as TOTAL_USERS,
    COUNT(OPCO_ID) as USERS_WITH_OPCO,
    ROUND(COUNT(OPCO_ID) * 100.0 / COUNT(*), 2) as OPCO_COVERAGE_PCT
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_USER
WHERE IS_CURRENT = TRUE;
-- Expected: OPCO_COVERAGE_PCT > 95%
```

#### 4. Real-Time Capabilities Tests

```sql
-- Test 1: Check Snowpipe status
SHOW PIPES LIKE 'PIPE_EDR_THREATS_REALTIME';
-- Expected: executionState = 'RUNNING'

-- Test 2: Verify real-time data
SELECT COUNT(*) FROM DEV_LANDING.SECURITY_ANALYTICS.L_EDR_THREATS_REALTIME
WHERE INGESTED_AT >= DATEADD('hour', -1, CURRENT_TIMESTAMP());
-- Expected: Recent data exists

-- Test 3: Check stream processing
SELECT SYSTEM$STREAM_HAS_DATA('DEV_TRANSFORMATION.SECURITY_ANALYTICS.STREAM_NEW_CRITICAL_VULNS');
-- Expected: TRUE or FALSE (depends on new data)
```

---

## Success Criteria

### Enhancement 1: Power BI Integration
- ✅ Executive dashboard displays all Top 13 KPIs
- ✅ Operational dashboard shows asset-level details
- ✅ RLS correctly filters data by user's OpCo
- ✅ Aggregated tables reduce query time to < 5 seconds
- ✅ Dashboards refresh successfully on schedule

### Enhancement 2: Near Real-Time
- ✅ Snowpipe ingests files within 1 minute of arrival
- ✅ Real-time views show data from last 15 minutes
- ✅ Stream processing detects new critical vulns within 5 minutes
- ✅ No data loss during ingestion

### Enhancement 3: Unified User Dimension
- ✅ DIM_USER contains >95% of AD users
- ✅ OpCo enrichment covers >95% of users
- ✅ SCD Type 2 tracks user history correctly
- ✅ Load procedure runs daily without errors

### Enhancement 4: Data Quality Dashboard
- ✅ DQ metrics calculated for all critical tables
- ✅ DQ scores visible in all KPI views
- ✅ Data quality dashboard accessible in Power BI
- ✅ Issues identified and tracked for resolution

---

## Deployment Checklist

### Pre-Deployment
- [ ] Review all SQL scripts for errors
- [ ] Backup existing database state
- [ ] Obtain Power BI service account credentials
- [ ] Validate S3/Azure bucket access for Snowpipe
- [ ] Test AD and HR data extracts

### Deployment (Sequence Matters!)
1. [ ] Deploy Power BI Integration (Phase 1)
   - Create views
   - Create RLS function
   - Create aggregated tables
   - Grant permissions

2. [ ] Deploy Data Quality Framework (Phase 2)
   - Create DQ tables
   - Deploy DQ procedures
   - Schedule DQ tasks

3. [ ] Deploy Unified User Dimension (Phase 3)
   - Create DIM_USER table
   - Create landing tables
   - Deploy load procedure
   - Schedule user load task

4. [ ] Deploy Near Real-Time (Phase 4)
   - Create Snowpipe
   - Configure external notifications
   - Create streams
   - Deploy stream processing tasks

### Post-Deployment
- [ ] Run all test scripts
- [ ] Validate data in Power BI
- [ ] Monitor task execution for 48 hours
- [ ] Document any issues
- [ ] Train users on new dashboards

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Power BI performance issues | HIGH | Use aggregated tables, implement caching |
| RLS incorrectly filters data | HIGH | Comprehensive testing with multiple user roles |
| Snowpipe fails to ingest | MEDIUM | Configure monitoring alerts, implement retry logic |
| AD/HR integration unavailable | MEDIUM | Use existing ANCON_USERS as fallback |
| DQ checks impact performance | LOW | Run during off-peak hours (6:00 AM UTC) |

---

## Maintenance

### Daily Tasks (Automated)
- TBL_POWERBI_DAILY_AGGREGATES refresh @ 7:00 AM
- DQ_METRICS calculation @ 6:00 AM
- DIM_USER load @ 3:00 AM

### Weekly Tasks (Manual)
- Review DQ dashboard for trends
- Check Snowpipe ingestion logs
- Validate Power BI dashboard performance

### Monthly Tasks (Manual)
- Review and update RLS user access mappings
- Optimize slow-performing queries
- Archive old DQ metrics data

---

**Document Status**: IMPLEMENTATION READY
**Estimated Total Effort**: 180 hours (≈ 4-6 weeks, 1 FTE)
**Expected Completion**: 6 weeks from start

**END OF IMPLEMENTATION PLAN**
