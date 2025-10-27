# 🔄 End-to-End Data Flow - Sources to Visualizations

## Overview

This document provides a **comprehensive end-to-end view** of how security data flows from 15 external sources through Snowflake's 3-layer architecture to Power BI dashboards and Streamlit apps, with complete automation and data quality monitoring.

---

## 🌐 Complete Data Flow Diagram

::: mermaid
graph TB
    subgraph Sources["🌐 DATA SOURCES (15 Services)"]
        direction TB
        EDR1[🛡️ CrowdStrike<br/><small>EDR Platform</small>]
        EDR2[🛡️ SentinelOne<br/><small>EDR Platform</small>]
        VM1[🔍 Qualys<br/><small>Vulnerability Mgmt</small>]
        VM2[🔍 Tenable<br/><small>Vulnerability Mgmt</small>]
        AV1[🦠 Symantec<br/><small>Antivirus</small>]
        AV2[🦠 Sophos<br/><small>Antivirus</small>]
        AV3[🦠 Trellix<br/><small>Antivirus</small>]
        SIEM[📊 Splunk<br/><small>SIEM</small>]
        TI1[🌍 BitSight<br/><small>Threat Intel</small>]
        TI2[🌍 ZeroFox<br/><small>Threat Intel</small>]
        TI3[🌍 CybelAngel<br/><small>Threat Intel</small>]
        IAM1[👤 Ancon<br/><small>IAM</small>]
        IAM2[👤 Leviat<br/><small>IAM</small>]
        SNOW[🎫 ServiceNow<br/><small>ITSM</small>]
        EMAIL[📧 Proofpoint<br/><small>Email Security</small>]
    end

    subgraph Extract["📤 EXTRACTION LAYER"]
        direction TB
        API[🔌 API Connectors<br/><small>REST/GraphQL</small>]
        FTP[📁 SFTP/FTP<br/><small>File Transfer</small>]
        SYSLOG[📜 Syslog<br/><small>Event Streaming</small>]
        WEBHOOK[🔔 Webhooks<br/><small>Event Notifications</small>]
    end

    subgraph Storage["☁️ CLOUD STORAGE"]
        direction LR
        S3[📦 AWS S3<br/><small>Primary Storage</small><br/>180 GB]
        AZURE[📦 Azure Blob<br/><small>Secondary Storage</small><br/>120 GB]
    end

    subgraph Ingest["📥 INGESTION LAYER"]
        direction TB
        SP1[🚰 Snowpipe 1<br/><small>CrowdStrike Events</small>]
        SP2[🚰 Snowpipe 2<br/><small>Qualys Scans</small>]
        SP3[🚰 Snowpipe 3<br/><small>BitSight Ratings</small>]
        SP4[🚰 Snowpipe 4<br/><small>Splunk Logs</small>]
        SP5[🚰 Snowpipe 5<br/><small>ServiceNow Tickets</small>]
        EXT1[📂 External Table<br/><small>Batch Files</small>]
        TASK1[⏰ Copy Task<br/><small>Scheduled Loads</small>]
    end

    subgraph Landing["🥉 LAYER 1: DEV_LANDING"]
        direction TB
        L1_META["📋 Metadata<br/><small>136 Tables</small><br/><small>10.6M Records</small>"]
        L1_CROWDSTRIKE[" CrowdStrike Tables"]
        L1_QUALYS[" Qualys Tables"]
        L1_SPLUNK[" Splunk Tables"]
        L1_SERVICENOW[" ServiceNow Tables"]
        L1_OTHERS[" Other Services (11)"]
        L1_META -.-> L1_CROWDSTRIKE & L1_QUALYS & L1_SPLUNK & L1_SERVICENOW & L1_OTHERS
    end

    subgraph Transform["🥈 LAYER 2: DEV_TRANSFORMATION"]
        direction TB
        L2_META["📊 Star Schema<br/><small>104 Tables</small><br/><small>45.9M Records</small>"]
        L2_DIM["🔷 Dimensions (32)<br/><small>User, Device, Date, etc.</small>"]
        L2_FACT["📈 Facts (72)<br/><small>Events, Vulns, Threats</small>"]
        L2_DQ["✅ Data Quality<br/><small>57 PKs + 16 FKs</small>"]
        L2_META -.-> L2_DIM & L2_FACT
        L2_DQ -.->|Validates| L2_FACT
    end

    subgraph Report["🥇 LAYER 3: DEV_REPORTING"]
        direction TB
        L3_META["📊 Analytics Layer<br/><small>166 Objects</small><br/><small>1.2M Aggregated</small>"]
        L3_VIEWS["👁️ Views (148)<br/><small>Business Logic</small>"]
        L3_MAT["📑 Materialized (18)<br/><small>Pre-aggregated KPIs</small>"]
        L3_KPI["📈 NIST KPIs (13)<br/><small>Executive Metrics</small>"]
        L3_META -.-> L3_VIEWS & L3_MAT
        L3_VIEWS & L3_MAT -.-> L3_KPI
    end

    subgraph Viz["📊 VISUALIZATION LAYER"]
        direction TB
        PBI[📊 Power BI<br/><small>Executive Dashboards</small><br/>5 Reports]
        STREAMLIT[🎛️ Streamlit Apps<br/><small>Data Quality Monitoring</small><br/>12 Dashboards]
        EXCEL[📈 Excel<br/><small>Ad-hoc Analysis</small>]
        JUPYTER[📓 Jupyter<br/><small>Data Science</small>]
    end

    subgraph Automation["🤖 AUTOMATION & ORCHESTRATION"]
        direction LR
        TASKS["⏰ 38 Snowflake Tasks<br/><small>Scheduled Jobs</small>"]
        PROCS["⚙️ 14 Stored Procedures<br/><small>Business Logic</small>"]
        STREAMS["🌊 8 Snowflake Streams<br/><small>CDC Tracking</small>"]
        FUNCS["🔧 12 User Functions<br/><small>Calculations</small>"]
    end

    subgraph Monitoring["📡 MONITORING & ALERTS"]
        direction TB
        DQ_VIEWS["✅ 8 DQ Views<br/><small>Quality Metrics</small>"]
        ALERTS["🚨 Email Alerts<br/><small>Failures & Anomalies</small>"]
        DASHBOARDS["📊 Monitoring Dashboards<br/><small>Operational Health</small>"]
    end

    %% Connections
    EDR1 & EDR2 & VM1 & VM2 & AV1 & AV2 & AV3 -->|Extract| API
    SIEM -->|Stream| SYSLOG
    SNOW & TI1 & TI2 & TI3 -->|Pull| FTP
    IAM1 & IAM2 & EMAIL -->|Push| WEBHOOK

    API & FTP & SYSLOG & WEBHOOK -->|Store| S3 & AZURE
    S3 -->|Auto-trigger| SP1 & SP2 & SP3 & SP4 & SP5
    AZURE -->|Batch| EXT1 & TASK1

    SP1 & SP2 & SP3 & SP4 & SP5 & EXT1 & TASK1 -->|Load| L1_META
    L1_CROWDSTRIKE & L1_QUALYS & L1_SPLUNK & L1_SERVICENOW & L1_OTHERS -->|Transform| L2_DIM & L2_FACT

    L2_DIM & L2_FACT -->|Aggregate| L3_VIEWS & L3_MAT
    L3_VIEWS & L3_MAT & L3_KPI -->|Connect| PBI & STREAMLIT & EXCEL & JUPYTER

    TASKS -.->|Orchestrate| L1_META & L2_FACT & L3_MAT
    PROCS -.->|Execute| L2_FACT
    STREAMS -.->|Trigger| TASKS
    FUNCS -.->|Calculate| L2_FACT & L3_VIEWS

    DQ_VIEWS -.->|Monitor| L2_FACT
    ALERTS -.->|Notify| MONITORING
    DASHBOARDS -.->|Display| MONITORING

    %% Styling
    classDef sourceStyle fill:#E3F2FD,stroke:#1976D2,stroke-width:2px
    classDef storageStyle fill:#F3E5F5,stroke:#7B1FA2,stroke-width:2px
    classDef landingStyle fill:#FFF3E0,stroke:#EF6C00,stroke-width:2px
    classDef transformStyle fill:#E8F5E9,stroke:#388E3C,stroke-width:2px
    classDef reportStyle fill:#FFF9C4,stroke:#F57F17,stroke-width:2px
    classDef vizStyle fill:#FCE4EC,stroke:#C2185B,stroke-width:2px
    classDef autoStyle fill:#E0F2F1,stroke:#00897B,stroke-width:2px

    class EDR1,EDR2,VM1,VM2,AV1,AV2,AV3,SIEM,TI1,TI2,TI3,IAM1,IAM2,SNOW,EMAIL sourceStyle
    class S3,AZURE,API,FTP,SYSLOG,WEBHOOK storageStyle
    class L1_META,L1_CROWDSTRIKE,L1_QUALYS,L1_SPLUNK,L1_SERVICENOW,L1_OTHERS,SP1,SP2,SP3,SP4,SP5,EXT1,TASK1 landingStyle
    class L2_META,L2_DIM,L2_FACT,L2_DQ transformStyle
    class L3_META,L3_VIEWS,L3_MAT,L3_KPI reportStyle
    class PBI,STREAMLIT,EXCEL,JUPYTER vizStyle
    class TASKS,PROCS,STREAMS,FUNCS,DQ_VIEWS,ALERTS,DASHBOARDS autoStyle
:::

---

## 📊 Data Flow by Layer

### 1. Data Sources → Cloud Storage (Extraction)

::: mermaid
sequenceDiagram
    participant CrowdStrike as 🛡️ CrowdStrike
    participant Qualys as 🔍 Qualys
    participant Splunk as 📊 Splunk
    participant API as 🔌 API Connector
    participant S3 as 📦 AWS S3
    participant EventBridge as ⚡ S3 Event

    Note over CrowdStrike,S3: Real-time EDR Events
    CrowdStrike->>API: REST API Call (every 15 min)
    API->>API: Transform to JSON
    API->>S3: PUT /crowdstrike/events/{timestamp}.json
    S3->>EventBridge: S3 Event Notification

    Note over Qualys,S3: Scheduled Vulnerability Scans
    Qualys->>API: API Call (daily @ 2 AM)
    API->>API: Parse XML Response
    API->>S3: PUT /qualys/scans/{date}.csv

    Note over Splunk,S3: SIEM Log Streaming
    Splunk->>S3: Syslog Forward (continuous)
    S3->>EventBridge: Batched Events
:::

**Extraction Frequency**:
| Source | Method | Frequency | Format | Avg Size |
|--------|--------|-----------|--------|----------|
| CrowdStrike | API | Every 15 min | JSON | 5 MB |
| Qualys | API | Daily @ 2 AM | CSV | 50 MB |
| Splunk | Syslog | Continuous | JSON | 100 MB/day |
| BitSight | API | Daily @ 3 AM | JSON | 2 MB |
| ServiceNow | Export | Daily @ 1 AM | CSV | 20 MB |

---

### 2. Cloud Storage → Snowflake Landing (Ingestion)

::: mermaid
sequenceDiagram
    participant S3 as 📦 S3 Bucket
    participant SNS as 📢 SNS Topic
    participant Snowpipe as 🚰 Snowpipe
    participant Stage as 📂 Snowflake Stage
    participant Landing as 🥉 Landing Table
    participant Stream as 🌊 Snowflake Stream

    S3->>SNS: File uploaded event
    SNS->>Snowpipe: Trigger notification
    Snowpipe->>Stage: Reference external file
    Snowpipe->>Landing: COPY INTO (auto-ingest)
    Note over Snowpipe,Landing: <5 min latency
    Landing->>Stream: Capture INSERT (CDC)
    Stream-->>Task: Trigger transformation
:::

**Snowpipe Configuration**:
```sql
-- Example: CrowdStrike Snowpipe
CREATE OR REPLACE PIPE PIPE_CROWDSTRIKE_EVENTS
AUTO_INGEST = TRUE
AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:xxx:snowflake-s3-events'
AS
COPY INTO LANDING_CROWDSTRIKE_EVENTS
FROM @STAGE_S3_CROWDSTRIKE
FILE_FORMAT = (TYPE = JSON, STRIP_OUTER_ARRAY = TRUE)
ON_ERROR = CONTINUE;

-- Auto-resume on file arrival
ALTER PIPE PIPE_CROWDSTRIKE_EVENTS REFRESH;
:::

**Ingestion SLAs**:
- **Real-time (Snowpipe)**: < 5 minutes
- **Batch (Tasks)**: < 15 minutes
- **Availability**: 99.9%

---

### 3. Landing → Transformation (Business Logic)

::: mermaid
sequenceDiagram
    participant Landing as 🥉 Landing
    participant Stream as 🌊 Stream
    participant Task as ⏰ Task
    participant Proc as ⚙️ Stored Proc
    participant Dim as 🔷 Dimension
    participant Fact as 📊 Fact
    participant DQ as ✅ Data Quality

    Landing->>Stream: INSERT detected
    Stream->>Task: WHEN SYSTEM$STREAM_HAS_DATA
    Task->>Proc: CALL transform_security_events()
    Proc->>Dim: MERGE INTO DIM_USER_UNIFIED (SCD Type 2)
    Proc->>Dim: MERGE INTO DIM_DEVICE
    Proc->>Fact: INSERT INTO FACT_SECURITY_EVENTS
    Fact->>DQ: Trigger constraint checks
    DQ-->>Proc: Validation result
    alt Validation Success
        Proc->>Task: COMMIT
    else Validation Failure
        Proc->>Task: ROLLBACK + Alert
    end
:::

**Transformation Logic**:
```sql
-- Example: Transform security events
CREATE OR REPLACE PROCEDURE transform_security_events()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
    -- Update dimensions (SCD Type 2)
    MERGE INTO DIM_USER_UNIFIED AS target
    USING (
        SELECT DISTINCT
            MD5(LOWER(email)) AS user_key,
            username,
            email,
            department
        FROM STREAM_LANDING_EVENTS
    ) AS source
    ON target.user_key = source.user_key AND target.is_current = TRUE
    WHEN MATCHED AND (target.department <> source.department) THEN
        UPDATE SET
            valid_to = CURRENT_TIMESTAMP,
            is_current = FALSE
    WHEN NOT MATCHED THEN
        INSERT (user_key, username, email, department, valid_from, is_current)
        VALUES (source.user_key, source.username, source.email, source.department, CURRENT_TIMESTAMP, TRUE);

    -- Insert facts
    INSERT INTO FACT_SECURITY_EVENTS (
        event_date_key, user_key, device_key, service_key,
        event_timestamp, event_type, severity, event_count
    )
    SELECT
        TO_NUMBER(TO_CHAR(event_time, 'YYYYMMDD')) AS event_date_key,
        MD5(LOWER(email)) AS user_key,
        MD5(LOWER(hostname)) AS device_key,
        (SELECT service_key FROM DIM_SECURITY_SERVICE WHERE service_name = 'CrowdStrike') AS service_key,
        event_time,
        event_type,
        severity,
        1 AS event_count
    FROM STREAM_LANDING_EVENTS;

    RETURN 'Transformed ' || (SELECT COUNT(*) FROM STREAM_LANDING_EVENTS) || ' events';
END;
$$;
:::

---

### 4. Transformation → Reporting (Aggregation)

::: mermaid
graph TB
    subgraph Transform["🥈 Transformation Layer"]
        FACT_EVENTS["📊 FACT_SECURITY_EVENTS<br/>45.2M records"]
        FACT_VULNS["🔍 FACT_VULNERABILITIES<br/>2.3M records"]
        DIM_DATE["📅 DIM_DATE"]
        DIM_USER["👤 DIM_USER"]
        DIM_DEVICE["💻 DIM_DEVICE"]
    end

    subgraph Report["🥇 Reporting Layer"]
        VW_EXEC["👁️ VW_EXECUTIVE_SUMMARY<br/>(Monthly KPIs)"]
        VW_VULN["👁️ VW_VULNERABILITY_TRENDS<br/>(Top CVEs)"]
        VW_COMPLIANCE["👁️ VW_COMPLIANCE_SCORECARD<br/>(NIST CSF)"]
        MAT_KPI["📑 MAT_VW_TOP13_KPIS<br/>(Materialized)"]
    end

    FACT_EVENTS & DIM_DATE & DIM_USER --> VW_EXEC
    FACT_VULNS & DIM_DEVICE & DIM_DATE --> VW_VULN
    FACT_EVENTS & FACT_VULNS --> VW_COMPLIANCE
    VW_EXEC & VW_VULN & VW_COMPLIANCE --> MAT_KPI
:::

**Materialized View Example**:
```sql
CREATE OR REPLACE MATERIALIZED VIEW MAT_VW_EXECUTIVE_SUMMARY AS
SELECT
    d.year,
    d.month_name,
    COUNT(DISTINCT e.device_key) AS total_devices,
    COUNT(DISTINCT e.user_key) AS total_users,
    SUM(e.event_count) AS total_events,
    COUNT(DISTINCT CASE WHEN e.severity = 'Critical' THEN e.event_key END) AS critical_events,
    ROUND(AVG(CASE WHEN e.status = 'Resolved' THEN DATEDIFF(hour, e.detected_at, e.resolved_at) END), 2) AS avg_mttr_hours,
    ROUND(COUNT(DISTINCT v.device_key) * 100.0 / COUNT(DISTINCT e.device_key), 2) AS vulnerability_coverage_pct
FROM FACT_SECURITY_EVENTS e
JOIN DIM_DATE d ON e.event_date_key = d.date_key
LEFT JOIN FACT_VULNERABILITIES v ON e.device_key = v.device_key AND v.finding_status = 'Open'
GROUP BY d.year, d.month_name;

-- Refresh every hour
ALTER MATERIALIZED VIEW MAT_VW_EXECUTIVE_SUMMARY SET WAREHOUSE = REPORTING_WH;
:::

---

### 5. Reporting → Visualizations (Consumption)

#### Power BI Connection

::: mermaid
graph LR
    subgraph Snowflake["❄️ Snowflake"]
        REPORT[🥇 Reporting Layer<br/>148 Views + 18 Mat Views]
    end

    subgraph PowerBI["📊 Power BI"]
        GATEWAY[🔌 Gateway<br/>On-Premises]
        DATASET1[📊 Dataset: Executive<br/>DirectQuery]
        DATASET2[📊 Dataset: Compliance<br/>Import]
        DASHBOARD1[📱 Dashboard: Security Overview]
        DASHBOARD2[📱 Dashboard: Vulnerability Mgmt]
        DASHBOARD3[📱 Dashboard: NIST CSF Scorecard]
    end

    REPORT -->|ODBC/SSO| GATEWAY
    GATEWAY --> DATASET1 & DATASET2
    DATASET1 --> DASHBOARD1 & DASHBOARD3
    DATASET2 --> DASHBOARD2
:::

**Power BI Refresh Schedule**:
| Dataset | Mode | Refresh Frequency | Rows | Refresh Duration |
|---------|------|-------------------|------|------------------|
| Executive Summary | DirectQuery | Real-time | 1.2M | N/A |
| Vulnerability Trends | Import | Every 30 min | 450K | 45 sec |
| Compliance Scorecard | Import | Every 2 hours | 125K | 20 sec |
| Threat Intelligence | DirectQuery | Real-time | 890K | N/A |
| User Analytics | Import | Daily @ 6 AM | 8.5K | 10 sec |

#### Streamlit Apps

```python
# Example: Streamlit Data Quality Dashboard
import streamlit as st
import snowflake.connector

# Connect to Snowflake
conn = snowflake.connector.connect(
    user='ITSECKPI_USER',
    authenticator='externalbrowser',  # SSO
    account='GenericCorp',
    warehouse='REPORTING_WH',
    database='DEV_REPORTING',
    schema='PUBLIC'
)

# Query DQ metrics
dq_metrics = conn.cursor().execute("""
    SELECT
        table_name,
        total_records,
        null_count,
        duplicate_count,
        quality_score_pct
    FROM VW_DATA_QUALITY_METRICS
    ORDER BY quality_score_pct ASC
""").fetchall()

# Display dashboard
st.title("🎯 Data Quality Monitoring")
st.metric("Overall DQ Score", "72.3%", delta="+2.1%")

# Charts
st.bar_chart(dq_metrics)
:::

---

## ⏱️ End-to-End Latency

### Latency Breakdown

::: mermaid
gantt
    title Data Flow Timeline (Real-time Path)
    dateFormat HH:mm
    axisFormat %H:%M

    section Source
    CrowdStrike Event Generated    :milestone, m1, 00:00, 0m

    section Extract
    API Call & Transform           :a1, 00:00, 2m

    section Storage
    Upload to S3                   :a2, after a1, 1m
    S3 Event Notification          :a3, after a2, 30s

    section Ingest
    Snowpipe Trigger               :a4, after a3, 1m
    COPY INTO Landing              :a5, after a4, 2m

    section Transform
    Stream Detects Change          :a6, after a5, 30s
    Task Execution                 :a7, after a6, 3m

    section Report
    Materialized View Refresh      :a8, after a7, 2m

    section Viz
    Power BI Dashboard Update      :a9, after a8, 30m

    section Total
    End-to-End Complete            :milestone, m2, after a9, 0m
:::

**Total Latency**:
- **Real-time Path** (CrowdStrike → Power BI): **42 minutes**
- **Batch Path** (ServiceNow → Power BI): **2-4 hours**
- **Critical Alerts** (Security Events): **< 5 minutes**

---

## 🔄 Automation & Orchestration

### Task Dependency Graph

::: mermaid
graph TB
    START[🕐 ROOT_TASK<br/>Every 15 min] --> L1

    subgraph L1["Landing Tasks"]
        T1["📥 LOAD_CROWDSTRIKE<br/>2 min"]
        T2["📥 LOAD_QUALYS<br/>3 min"]
        T3["📥 LOAD_SPLUNK<br/>1 min"]
    end

    L1 --> T4

    subgraph L2["Transform Tasks"]
        T4["🔄 TRANSFORM_USERS<br/>SCD Type 2<br/>4 min"]
        T5["🔄 TRANSFORM_DEVICES<br/>3 min"]
        T6["🔄 TRANSFORM_EVENTS<br/>5 min"]
    end

    L2 --> L3

    subgraph L3["Reporting Tasks"]
        T7["📊 REFRESH_EXEC_VIEW<br/>2 min"]
        T8["📊 REFRESH_VULN_VIEW<br/>2 min"]
        T9["📊 MATERIALIZE_KPIS<br/>3 min"]
    end

    L3 --> DQ

    subgraph DQ["Quality Tasks"]
        T10["✅ RUN_DQ_CHECKS<br/>1 min"]
        T11["📧 SEND_DQ_ALERTS<br/>30 sec"]
    end

    START -.->|Success| T1 & T2 & T3
    T1 & T2 & T3 -.->|Success| T4 & T5
    T4 & T5 -.->|Success| T6
    T6 -.->|Success| T7 & T8
    T7 & T8 -.->|Success| T9
    T9 -.->|Success| T10
    T10 -.->|Failure| T11

    style START fill:#4CAF50
    style T1 fill:#FFB74D
    style T2 fill:#FFB74D
    style T3 fill:#FFB74D
    style T4 fill:#64B5F6
    style T5 fill:#64B5F6
    style T6 fill:#64B5F6
    style T7 fill:#BA68C8
    style T8 fill:#BA68C8
    style T9 fill:#BA68C8
    style T10 fill:#4DB6AC
    style T11 fill:#E57373
:::

**Total Automation**: 38 tasks, 98.1% success rate

---

## 📊 Data Volume & Growth

### Current State (Oct 2025)

| Layer | Objects | Records | Storage | Monthly Growth |
|-------|---------|---------|---------|----------------|
| **Landing** | 136 tables | 10.6M | 180 GB | +500K records |
| **Transformation** | 104 tables | 45.9M | 245 GB | +2M records |
| **Reporting** | 166 views | 1.2M | 25 GB | +50K records |
| **Total** | 406 objects | **57.7M** | **450 GB** | **+2.5M/mo** |

### 12-Month Projection

::: mermaid
xychart-beta
    title "Data Volume Growth Forecast"
    x-axis [Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec]
    y-axis "Records (Millions)" 0 --> 100
    line [57.7, 60.2, 62.7, 65.2, 67.7, 70.2, 72.7, 75.2, 77.7, 80.2, 82.7, 85.2]
:::

**Storage Cost Projection**:
- Current: $18/month (450 GB @ $40/TB)
- 12 months: $34/month (850 GB)
- Optimization: Clustering + compression = -30%

---

## 🎯 NIST CSF 2.0 KPI Traceability

### Source-to-KPI Mapping

::: mermaid
graph LR
    subgraph Sources["🌐 Sources"]
        CS[CrowdStrike]
        Q[Qualys]
        BS[BitSight]
    end

    subgraph Facts["📊 Facts"]
        FE[FACT_EVENTS]
        FV[FACT_VULNS]
        FT[FACT_THREATS]
    end

    subgraph KPIs["📈 Top 13 KPIs"]
        K1[MTTD]
        K2[MTTR]
        K3[Patch %]
        K4[Threat Count]
        K5[DQ Score]
    end

    CS --> FE
    Q --> FV
    BS --> FT

    FE --> K1 & K2 & K5
    FV --> K3
    FT --> K4

    style CS fill:#FFB74D
    style Q fill:#64B5F6
    style BS fill:#BA68C8
    style FE fill:#FFF176
    style FV fill:#FFF176
    style FT fill:#FFF176
    style K1 fill:#4CAF50
    style K2 fill:#4CAF50
    style K3 fill:#4CAF50
    style K4 fill:#4CAF50
    style K5 fill:#4CAF50
:::

**KPI Calculation Examples**:
```sql
-- KPI 1: Mean Time to Detect (MTTD)
SELECT
    AVG(DATEDIFF(hour, event_timestamp, detected_at)) AS mttd_hours
FROM FACT_SECURITY_EVENTS
WHERE event_type = 'Threat'
  AND detected_at IS NOT NULL;

-- KPI 2: Patch Compliance %
SELECT
    ROUND(COUNT(CASE WHEN patch_status = 'Patched' THEN 1 END) * 100.0 / COUNT(*), 2) AS patch_compliance_pct
FROM FACT_VULNERABILITIES
WHERE severity IN ('Critical', 'High');
:::

---

## 📚 Related Documentation

- [[Data-Architecture]] - 3-layer architecture details
- [[Data-Model]] - ERD and schema documentation
- [[Deployment-Guide]] - Setup instructions
- [[Performance-Tuning]] - Optimization guides

---

**Data Journey Summary**:
```
15 Sources → API/SFTP → S3/Azure → Snowpipe/Tasks → Landing (10.6M)
  → Transform (45.9M) → Reporting (1.2M) → Power BI/Streamlit
  → Stakeholders & Analysts
```

**End-to-End Latency**: 42 minutes (real-time) | 2-4 hours (batch)
**Automation Coverage**: 98.1% | **Data Quality Score**: 72.3%

---

**Last Updated**: October 23, 2025
**Maintained By**: Lead Data Engineer - SECURITY_ANALYTICS Project
