# 🏗️ Data Architecture - SECURITY_ANALYTICS Data Warehouse

## Overview

The SECURITY_ANALYTICS Data Warehouse implements a **3-layer medallion architecture** on Snowflake, optimized for security analytics with 550+ database objects processing 57.7M records across 15 security services.

---

## 📊 Architecture Layers

### Layer 1: DEV_LANDING (Bronze/Raw)
**Purpose**: Raw data ingestion and initial storage
**Objects**: 136 tables, 5 Snowpipes, 3 External Tables
**Records**: 10.6M raw security events
**Pattern**: ELT (Extract-Load-Transform)

### Layer 2: DEV_TRANSFORMATION (Silver/Curated)
**Purpose**: Business logic, data quality, star schema
**Objects**: 104 tables (32 dimensions + 72 facts)
**Records**: 45.9M transformed records
**Pattern**: Star Schema with SCD Type 2

### Layer 3: DEV_REPORTING (Gold/Analytics)
**Purpose**: Analytics-ready views and aggregations
**Objects**: 148 views, 18 materialized tables
**Records**: 1.2M aggregated KPIs
**Pattern**: Denormalized reporting layer

---

## 🎯 3-Layer Architecture Diagram

::: mermaid
graph TB
    subgraph Sources["🌐 External Data Sources"]
        EDR["🛡️ EDR Platforms<br/><small>CrowdStrike, SentinelOne</small>"]
        VM["🔍 Vulnerability Mgmt<br/><small>Qualys, Tenable</small>"]
        AV["🦠 Antivirus<br/><small>Symantec, McAfee, Sophos, etc.</small>"]
        SIEM["📊 SIEM<br/><small>Splunk</small>"]
        TI["🌍 Threat Intel<br/><small>BitSight, CybelAngel, ZeroFox</small>"]
        IAM["👤 Identity Mgmt<br/><small>Ancon, Leviat</small>"]
        SNOW["🎫 ServiceNow<br/><small>CMDB, Incidents, Changes</small>"]
    end

    subgraph Storage["☁️ Cloud Storage"]
        S3["📦 AWS S3"]
        AZURE["📦 Azure Blob"]
    end

    subgraph Landing["🥉 LAYER 1: DEV_LANDING (Raw)"]
        L1_TABLES["📋 136 Tables<br/><small>10.6M Records</small>"]
        L1_PIPES["🚰 5 Snowpipes<br/><small>Real-time Ingestion</small>"]
        L1_EXT["📂 3 External Tables<br/><small>Batch Ingestion</small>"]

        L1_TABLES -.->|Real-time| L1_PIPES
        L1_TABLES -.->|Batch| L1_EXT
    end

    subgraph Transform["🥈 LAYER 2: DEV_TRANSFORMATION (Curated)"]
        direction TB
        L2_DIM["🔷 32 Dimension Tables<br/><small>SCD Type 2</small>"]
        L2_FACT["📊 72 Fact Tables<br/><small>45.9M Records</small>"]
        L2_DQ["✅ Data Quality Framework<br/><small>Constraints + Monitoring</small>"]

        L2_DIM ---|Star Schema| L2_FACT
        L2_DQ -.->|Validates| L2_FACT
    end

    subgraph Report["🥇 LAYER 3: DEV_REPORTING (Analytics)"]
        direction TB
        L3_VIEWS["👁️ 148 Views<br/><small>Business Logic</small>"]
        L3_MAT["📑 18 Materialized Tables<br/><small>1.2M Aggregated KPIs</small>"]
        L3_KPI["📈 Top 13 NIST KPIs<br/><small>Executive Reporting</small>"]

        L3_VIEWS -->|Optimized| L3_MAT
        L3_MAT -->|Feeds| L3_KPI
    end

    subgraph Viz["📊 Visualization Layer"]
        PBI["📊 Power BI<br/><small>Executive Dashboards</small>"]
        STREAMLIT["🎛️ Streamlit<br/><small>12 Data Quality Apps</small>"]
        EXCEL["📈 Excel<br/><small>Ad-hoc Analysis</small>"]
    end

    subgraph Auto["🤖 Automation Layer"]
        TASKS["⏰ 38 Snowflake Tasks<br/><small>Scheduled Orchestration</small>"]
        PROCS["⚙️ 14 Stored Procedures<br/><small>Business Logic</small>"]
        STREAMS["🌊 Snowflake Streams<br/><small>CDC Tracking</small>"]
    end

    EDR & VM & AV & SIEM & TI & IAM & SNOW --> S3 & AZURE
    S3 & AZURE -->|Ingest| L1_PIPES & L1_EXT
    L1_TABLES -->|Transform| L2_DIM & L2_FACT
    L2_DIM & L2_FACT -->|Aggregate| L3_VIEWS
    L3_VIEWS & L3_MAT -->|Connect| PBI & STREAMLIT & EXCEL

    TASKS -.->|Orchestrate| L1_TABLES & L2_FACT & L3_MAT
    PROCS -.->|Execute| L2_FACT
    STREAMS -.->|Track Changes| L2_FACT

    style Landing fill:#CD853F
    style Transform fill:#C0C0C0
    style Report fill:#FFD700
    style Sources fill:#E3F2FD
    style Storage fill:#F3E5F5
    style Viz fill:#E8F5E9
    style Auto fill:#FFF3E0
:::

---

## 📋 Layer 1: DEV_LANDING (Bronze/Raw)

### Purpose
- Raw data storage from 15 security services
- Minimal transformation (schema validation only)
- Historical data preservation
- Source of truth for reprocessing

### Object Breakdown
| Object Type | Count | Purpose |
|-------------|-------|---------|
| **Tables** | 136 | Raw data storage |
| **Snowpipes** | 5 | Real-time ingestion (CrowdStrike, Qualys, etc.) |
| **External Tables** | 3 | Batch file ingestion from S3/Azure |
| **Streams** | 8 | CDC for transformation triggers |
| **File Formats** | 4 | JSON, CSV, Parquet parsers |

### Data Volume
- **Total Records**: 10.6M
- **Storage Size**: 180 GB
- **Growth Rate**: ~500K records/month
- **Retention**: 24 months

### Ingestion Patterns
```
Real-time (Snowpipe):
  CrowdStrike → S3 → Snowpipe → LANDING_CROWDSTRIKE_EVENTS
  Qualys → S3 → Snowpipe → LANDING_QUALYS_VULNERABILITIES

Batch (External Tables):
  ServiceNow Daily Export → Azure → External Table → Task Load
  Splunk Logs → S3 → External Table → Task Load
```

---

## 🔄 Layer 2: DEV_TRANSFORMATION (Silver/Curated)

### Purpose
- Apply business rules and logic
- Implement star schema (facts + dimensions)
- Enforce data quality constraints
- Enable SCD Type 2 for historical tracking

### Star Schema Design

#### Dimension Tables (32)
::: mermaid
graph LR
    subgraph "Conformed Dimensions"
        DIM_DATE["📅 DIM_DATE<br/><small>Time Intelligence</small>"]
        DIM_USER["👤 DIM_USER_UNIFIED<br/><small>Consolidated Identity</small>"]
        DIM_DEVICE["💻 DIM_DEVICE<br/><small>Asset Inventory</small>"]
        DIM_SERVICE["🔧 DIM_SECURITY_SERVICE<br/><small>Tool Metadata</small>"]
    end

    subgraph "Security-Specific Dimensions"
        DIM_VULN["🔍 DIM_VULNERABILITY<br/><small>CVE + CVSS</small>"]
        DIM_THREAT["⚠️ DIM_THREAT<br/><small>Attack Vectors</small>"]
        DIM_COMP["✅ DIM_COMPLIANCE<br/><small>Frameworks</small>"]
    end

    style DIM_DATE fill:#BBDEFB
    style DIM_USER fill:#C5E1A5
    style DIM_DEVICE fill:#FFE082
    style DIM_SERVICE fill:#CE93D8
    style DIM_VULN fill:#FFAB91
    style DIM_THREAT fill:#EF9A9A
    style DIM_COMP fill:#A5D6A7
:::

#### Fact Tables (72)
- **FACT_SECURITY_EVENTS** (45M records) - Security event telemetry
- **FACT_VULNERABILITIES** (2.3M records) - Vulnerability scans
- **FACT_INCIDENTS** (125K records) - Security incidents
- **FACT_COMPLIANCE** (890K records) - Compliance checks
- **FACT_THREATS** (450K records) - Threat intelligence
- ... 67 additional fact tables

### Data Quality Framework
| Check Type | Count | Implementation |
|------------|-------|----------------|
| **Primary Keys** | 57 | NOT NULL + UNIQUE constraints |
| **Foreign Keys** | 16 | Referential integrity |
| **Check Constraints** | 24 | Business rule validation |
| **Data Quality Views** | 8 | Real-time monitoring |

### Transformation Logic
```sql
-- Example: Unified User Dimension
CREATE OR REPLACE TABLE DIM_USER_UNIFIED AS
SELECT DISTINCT
    MD5(LOWER(email_address)) AS user_key,
    COALESCE(crowdstrike.username, qualys.user, splunk.user) AS username,
    email_address,
    department,
    location,
    CURRENT_TIMESTAMP AS valid_from,
    '9999-12-31' AS valid_to,  -- SCD Type 2
    TRUE AS is_current
FROM (
    SELECT * FROM LANDING_CROWDSTRIKE_USERS
    UNION ALL
    SELECT * FROM LANDING_QUALYS_USERS
    UNION ALL
    SELECT * FROM LANDING_SPLUNK_USERS
)
QUALIFY ROW_NUMBER() OVER (PARTITION BY email_address ORDER BY last_updated DESC) = 1;
```

---

## 📈 Layer 3: DEV_REPORTING (Gold/Analytics)

### Purpose
- Denormalized views for analytics
- Pre-aggregated KPIs for performance
- Business-friendly naming conventions
- Power BI optimized structures

### Object Types
| Type | Count | Use Case |
|------|-------|----------|
| **Views** | 148 | Real-time business logic |
| **Materialized Views** | 18 | Pre-aggregated KPIs |
| **Secure Views** | 12 | Row-level security |
| **Reporting Procedures** | 10 | Complex calculations |

### Top 13 NIST CSF 2.0 KPIs

::: mermaid
graph TB
    subgraph Identify["🔍 IDENTIFY"]
        KPI1["Asset Coverage %<br/><small>Tracked/Total Devices</small>"]
        KPI2["Security Service Coverage<br/><small>15 Integrated Tools</small>"]
    end

    subgraph Protect["🛡️ PROTECT"]
        KPI3["Patch Compliance %<br/><small>Critical Vulns Patched</small>"]
        KPI4["Antivirus Coverage %<br/><small>Devices Protected</small>"]
    end

    subgraph Detect["🔎 DETECT"]
        KPI5["Mean Time to Detect<br/><small>MTTD - Hours</small>"]
        KPI6["Active Threat Count<br/><small>Current Threats</small>"]
    end

    subgraph Respond["⚡ RESPOND"]
        KPI7["Mean Time to Respond<br/><small>MTTR - Hours</small>"]
        KPI8["Incident Resolution %<br/><small>Closed/Total</small>"]
    end

    subgraph Recover["🔄 RECOVER"]
        KPI9["System Availability %<br/><small>Uptime</small>"]
        KPI10["Backup Success Rate<br/><small>Completed/Scheduled</small>"]
    end

    subgraph Govern["⚖️ GOVERN"]
        KPI11["Policy Compliance %<br/><small>Aligned/Total</small>"]
        KPI12["Security Training %<br/><small>Completed/Required</small>"]
        KPI13["Data Quality Score<br/><small>72.3% Current</small>"]
    end

    style Identify fill:#E3F2FD
    style Protect fill:#C8E6C9
    style Detect fill:#FFF9C4
    style Respond fill:#FFE0B2
    style Recover fill:#F8BBD0
    style Govern fill:#D1C4E9
:::

### Performance Optimization
```sql
-- Materialized view for executive dashboard
CREATE OR REPLACE MATERIALIZED VIEW RPT_EXECUTIVE_SUMMARY AS
SELECT
    DATE_TRUNC('month', event_date) AS month,
    COUNT(DISTINCT device_id) AS total_devices,
    COUNT(DISTINCT CASE WHEN has_av = TRUE THEN device_id END) AS protected_devices,
    COUNT(DISTINCT CASE WHEN has_critical_vuln = TRUE THEN device_id END) AS vulnerable_devices,
    AVG(mttr_hours) AS avg_mttr,
    AVG(mttd_hours) AS avg_mttd,
    SUM(security_incidents) AS total_incidents,
    AVG(data_quality_score) AS avg_data_quality
FROM FACT_SECURITY_EVENTS
GROUP BY 1;

-- Auto-refresh every hour
ALTER MATERIALIZED VIEW RPT_EXECUTIVE_SUMMARY SET WAREHOUSE = REPORTING_WH;
```

---

## 🔄 Data Flow Architecture

### End-to-End Flow

::: mermaid
sequenceDiagram
    participant Sources as 🌐 Sources
    participant S3 as ☁️ S3/Azure
    participant Snowpipe as 🚰 Snowpipe
    participant Landing as 🥉 Landing
    participant Stream as 🌊 Stream
    participant Task as ⏰ Task
    participant Transform as 🥈 Transform
    participant Report as 🥇 Report
    participant PowerBI as 📊 Power BI

    Sources->>S3: Upload CSV/JSON<br/>(every 15 min)
    S3->>Snowpipe: Trigger on file arrival
    Snowpipe->>Landing: COPY INTO (real-time)
    Landing->>Stream: CDC capture
    Stream->>Task: Trigger on new data
    Task->>Transform: Execute transformation
    Transform->>Transform: Apply business rules
    Transform->>Report: Materialize KPIs
    PowerBI->>Report: Query via ODBC<br/>(every 30 min)
    Note over PowerBI: Dashboard refresh
:::

### Latency Targets
| Layer | Latency | Refresh Frequency |
|-------|---------|-------------------|
| Landing → Transform | < 5 minutes | Real-time (Streams) |
| Transform → Report | < 10 minutes | Scheduled (Tasks) |
| Report → Power BI | < 30 minutes | Power BI refresh |
| **End-to-End** | **< 45 minutes** | **Near real-time** |

---

## 🤖 Automation Framework

### Orchestration with Snowflake Tasks

::: mermaid
graph TB
    ROOT["🕐 ROOT_TASK<br/><small>Every 15 min</small>"]

    subgraph "Landing Tasks"
        T1["📥 LOAD_CROWDSTRIKE"]
        T2["📥 LOAD_QUALYS"]
        T3["📥 LOAD_SPLUNK"]
    end

    subgraph "Transformation Tasks"
        T4["🔄 TRANSFORM_USERS"]
        T5["🔄 TRANSFORM_DEVICES"]
        T6["🔄 TRANSFORM_EVENTS"]
    end

    subgraph "Reporting Tasks"
        T7["📊 MATERIALIZE_KPIS"]
        T8["📊 UPDATE_DASHBOARDS"]
    end

    subgraph "Quality Tasks"
        T9["✅ RUN_DQ_CHECKS"]
        T10["🚨 SEND_ALERTS"]
    end

    ROOT --> T1 & T2 & T3
    T1 & T2 & T3 --> T4 & T5 & T6
    T4 & T5 & T6 --> T7 & T8
    T7 & T8 --> T9
    T9 --> T10

    style ROOT fill:#4CAF50
    style T1 fill:#FFB74D
    style T2 fill:#FFB74D
    style T3 fill:#FFB74D
    style T4 fill:#64B5F6
    style T5 fill:#64B5F6
    style T6 fill:#64B5F6
    style T7 fill:#BA68C8
    style T8 fill:#BA68C8
    style T9 fill:#4DB6AC
    style T10 fill:#E57373
:::

### Task Execution Stats
- **Total Tasks**: 38 scheduled tasks
- **Success Rate**: 98.1%
- **Average Duration**: 45 seconds
- **Daily Executions**: 96 runs (every 15 min)
- **Compute Cost**: ~$2.50/day

---

## 📊 Storage & Performance Metrics

### Current State (as of Oct 2025)

| Metric | Landing | Transformation | Reporting | Total |
|--------|---------|----------------|-----------|-------|
| **Tables** | 136 | 104 | 18 | 258 |
| **Views** | 0 | 0 | 148 | 148 |
| **Records** | 10.6M | 45.9M | 1.2M | 57.7M |
| **Storage** | 180 GB | 245 GB | 25 GB | 450 GB |
| **Growth** | +500K/mo | +2M/mo | +50K/mo | +2.5M/mo |

### Query Performance
- **Average Query Time**: 319ms
- **P95 Query Time**: 850ms
- **P99 Query Time**: 1.8s
- **Cache Hit Rate**: 87%

### Warehouse Sizing
```sql
-- DEV_WH (Development)
Size: X-Small (1 credit/hour)
Usage: 8 hours/day
Auto-suspend: 1 minute
Cost: ~$45/month

-- REPORTING_WH (Analytics)
Size: Small (2 credits/hour)
Usage: 2 hours/day
Auto-suspend: 1 minute
Cost: ~$30/month
```

---

## 🔒 Security & Governance

### Row-Level Security
```sql
-- Example: Restrict data by region
CREATE OR REPLACE SECURE VIEW VW_INCIDENTS_REGIONAL AS
SELECT *
FROM FACT_INCIDENTS
WHERE region = CURRENT_USER_REGION() -- UDF based on user context
WITH CHECK OPTION;
```

### Column Masking
```sql
-- Mask PII for non-privileged users
CREATE OR REPLACE MASKING POLICY MASK_EMAIL AS (val STRING)
RETURNS STRING ->
    CASE
        WHEN CURRENT_ROLE() IN ('DATA_ENGINEER', 'SECURITY_ADMIN') THEN val
        ELSE REGEXP_REPLACE(val, '.+@', '***@')
    END;

ALTER TABLE DIM_USER_UNIFIED
    MODIFY COLUMN email_address
    SET MASKING POLICY MASK_EMAIL;
```

---

## 📈 Future Enhancements

### Planned Improvements (Q1 2026)
1. **Implement Iceberg Tables** - For better time-travel and schema evolution
2. **Add dbt for Transformation** - Version-controlled SQL transformations
3. **Real-time Streaming** - Snowflake Streams + Tasks for <1 min latency
4. **ML/AI Integration** - Anomaly detection with Snowflake ML
5. **Cost Optimization** - Implement clustering keys, materialized views optimization

---

## 📚 Related Documentation

- [[Data-Model]] - Detailed ERD and schema documentation
- [[End-to-End-Flow]] - Source to visualization data flow
- [[Deployment-Guide]] - How to deploy architecture components
- [[Performance-Tuning]] - Optimization best practices

---

**Last Updated**: October 23, 2025
**Maintained By**: Lead Data Engineer - SECURITY_ANALYTICS Project
