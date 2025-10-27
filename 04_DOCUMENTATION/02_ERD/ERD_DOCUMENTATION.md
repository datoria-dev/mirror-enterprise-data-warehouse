# SECURITY_ANALYTICS Data Warehouse - Entity Relationship Diagrams (ERD)
**Date:** October 7, 2025
**Architecture:** 3-Layer Cloud Data Warehouse (Azure Snowflake)
**Environment:** DEV (Development)

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Object Inventory Summary](#object-inventory-summary)
3. [Layer 1: DEV_LANDING (Landing Zone)](#layer-1-dev_landing)
4. [Layer 2: DEV_TRANSFORMATION (Star Schema)](#layer-2-dev_transformation)
5. [Layer 3: DEV_REPORTING (Analytics)](#layer-3-dev_reporting)
6. [Cross-Layer Data Flow](#cross-layer-data-flow)
7. [Key Relationships & Star Schema](#key-relationships--star-schema)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SECURITY_ANALYTICS 3-LAYER ARCHITECTURE                     │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │   Data Sources   │
    │  (15+ Systems)   │
    └────────┬─────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────────┐
│  LAYER 1: DEV_LANDING.SECURITY_ANALYTICS                                     │
│  Purpose: Raw data ingestion, minimal transformation               │
│  Objects: 141 Tables, 11 Views                                     │
│  Pattern: L_* prefix (Landing tables)                              │
│  Data: Raw JSON, CSV, API responses                                │
└────────────────────┬───────────────────────────────────────────────┘
                     │ ETL Pipelines (n8n, Python, SQL)
                     ▼
┌────────────────────────────────────────────────────────────────────┐
│  LAYER 2: DEV_TRANSFORMATION.SECURITY_ANALYTICS                              │
│  Purpose: Business logic, data modeling, star schema               │
│  Objects: 32 Dimensions, 23 Facts, 62 Other Tables                │
│           50+ Views, 15 Procedures, 2 Tasks                        │
│  Pattern: DIM_* (Dimensions), FACT_* (Facts)                       │
│  Data: Cleaned, conformed, business rules applied                  │
└────────────────────┬───────────────────────────────────────────────┘
                     │ Aggregation & Analytics
                     ▼
┌────────────────────────────────────────────────────────────────────┐
│  LAYER 3: DEV_REPORTING.SECURITY_ANALYTICS                                   │
│  Purpose: Analytics-ready datasets, KPIs, dashboards               │
│  Objects: 18 Tables, 148 Views, 10 Procedures                     │
│  Pattern: VW_* (Views), TBL_* (KPI tables)                         │
│  Consumers: Power BI, Tableau, Ad-hoc queries                      │
└────────────────────────────────────────────────────────────────────┘
```

---

## Object Inventory Summary

### Layer 1: DEV_LANDING
| Object Type | Count | Purpose |
|-------------|-------|---------|
| Tables | 141 | Raw data from 15+ security platforms |
| Views | 11 | Consolidated raw data views |
| **Total** | **152** | Landing zone objects |

**Key Tables:**
- `L_EDR_THREATS_REALTIME` - Real-time EDR threat feed
- `L_CRITICAL_VULNS_REALTIME` - Critical vulnerability feed
- `AD_COMPUTERS_*` - Active Directory computer inventories
- `QUALYS_*` - Vulnerability scan results
- `CROWDSTRIKE_*` - Endpoint protection data

---

### Layer 2: DEV_TRANSFORMATION
| Object Type | Count | Purpose |
|-------------|-------|---------|
| Dimension Tables | 32 | Master data (DIM_*) |
| Fact Tables | 23 | Transactional/event data (FACT_*) |
| Support Tables | 62 | ETL logs, lookups, staging |
| Views | 50+ | Business logic views |
| Procedures | 15 | ETL automation |
| Tasks | 2 | Scheduled jobs |
| **Total** | **184+** | Transformation objects |

**Star Schema Components:**

**Core Dimensions (32):**
- `DIM_OPCO` (3 rows) - Operating Companies
- `DIM_HOST` (1,662 rows) - All IT assets
- `DIM_DATES` (10,000 rows) - Date dimension
- `DIM_USER` (1 row) - Unified user dimension (SCD Type 2)
- `DIM_ANCON_USERS` (995 rows) - AD users
- `DIM_DEFENDER_ENDPOINTS` (8,210 rows) - Microsoft Defender endpoints
- `DIM_CROWDSTRIKE_ENDPOINTS` (3,609 rows) - CrowdStrike hosts
- `DIM_CISCO_AMP` (4,948 rows) - Cisco AMP devices
- `DIM_HARDWARE_INVENTORY` (21,997 rows) - Hardware assets
- `DIM_QUALYS_VULNERABILITIES` (210,435 rows) - Known vulnerabilities
- `DIM_VULNERABILITY` (631,305 rows) - All CVEs
- ...and 21 more dimension tables

**Core Facts (23):**
- `FACT_EDR` (20 rows) - EDR coverage metrics
- `FACT_QUALYS` (20 rows) - Vulnerability scan facts
- `FACT_REMEDIATION_EVENTS` - Vulnerability remediation tracking
- `FACT_DEFENDER_THREATS` - Microsoft Defender detections
- `FACT_CYBELANGEL_THREATS` - External threat intelligence
- `FACT_AV_HEALTH` (107 rows) - Antivirus health status
- `FACT_BITSIGHT_FINDINGS` (1,219 rows) - External security posture
- ...and 16 more fact tables

**Stored Procedures (15):**
- `SP_CALCULATE_DATA_QUALITY_SCORE` - DQ automation
- `SP_REFRESH_DIMENSIONS` - Dimension updates
- `SP_POPULATE_FACT_TABLES` - Fact table loads
- ...and 12 more procedures

**Scheduled Tasks (2):**
- `TASK_DAILY_HEALTH_CHECK` - Daily data health monitoring
- `TASK_DATA_QUALITY_MONITOR` - 4-hourly DQ checks

---

### Layer 3: DEV_REPORTING
| Object Type | Count | Purpose |
|-------------|-------|---------|
| Tables | 18 | KPI aggregations, BOL tables |
| Views | 148 | Analytics-ready views |
| Procedures | 10 | Reporting automation |
| **Total** | **176** | Reporting objects |

**Key Views (148 total):**

**Executive Dashboards:**
- `VW_POWERBI_EXECUTIVE_DASHBOARD` (2,862 rows) - Power BI semantic layer
- `VW_EXECUTIVE_KPI_DASHBOARD` (1,098 rows) - Executive KPIs
- `VW_SECURITY_POSTURE_SUMMARY` (3 rows) - Security posture by OpCo

**Data Quality & Monitoring:**
- `VW_QUALITY_ALERTS` - DQ alerts
- `VW_QUALITY_SCORE_TREND` - 30-day DQ trends
- `VW_ETL_PIPELINE_STATUS` (117 runs) - ETL monitoring
- `VW_ETL_ERRORS` - ETL failure tracking

**Performance & Metadata:**
- `VW_QUERY_PERFORMANCE` - Query execution tracking
- `VW_DATA_DICTIONARY` (15 entries) - Metadata catalog
- `VW_DATA_LINEAGE` (10 entries) - Data lineage mapping

**Security Analytics:**
- `VW_AGENT_COVERAGE` - Security agent deployment
- `VW_EDR_COVERAGE` - EDR coverage metrics
- `VW_VULNERABILITY_TRENDS` - Vulnerability trending
- ...and 135+ more analytical views

**Stored Procedures (10):**
- `SP_CALCULATE_DATA_QUALITY` - DQ calculation engine
- `EXTRACT_VIEWS_WITH_SAMPLES` - Metadata extraction
- ...and 8 more reporting procedures

---

## Layer 1: DEV_LANDING

### ERD: Landing Zone Architecture

```mermaid
graph TB
    subgraph "DEV_LANDING.SECURITY_ANALYTICS - Raw Data Ingestion Layer"
        subgraph "Security Platforms"
            L1[L_EDR_THREATS_REALTIME]
            L2[L_CRITICAL_VULNS_REALTIME]
        end

        subgraph "Active Directory Sources"
            AD1[AD_COMPUTERS_ALUNGRIFFITHS]
            AD2[AD_COMPUTERS_ANCON]
            AD3[AD_COMPUTERS_OTHER_OPCOS]
        end

        subgraph "Vulnerability Management"
            Q1[QUALYS_SCANS]
            Q2[QUALYS_VULNERABILITIES]
            Q3[QUALYS_HOST_DATA]
        end

        subgraph "Endpoint Protection"
            CS1[CROWDSTRIKE_HOSTS]
            CS2[CROWDSTRIKE_DETECTIONS]
            DEF1[DEFENDER_ENDPOINTS]
            DEF2[DEFENDER_THREATS]
        end

        subgraph "Asset Management"
            SNOW1[SERVICENOW_CMDB]
            INV1[HARDWARE_INVENTORY]
        end

        subgraph "External Threat Intel"
            CA1[CYBELANGEL_ALERTS]
            BS1[BITSIGHT_FINDINGS]
            ZF1[ZEROFOX_ALERTS]
        end

        subgraph "Consolidated Views"
            V1[QUALYS_CONSOLIDATED]
            V2[AD_USERS_CONSOLIDATED]
        end
    end

    style L1 fill:#ff9999
    style L2 fill:#ff9999
    style V1 fill:#99ccff
    style V2 fill:#99ccff
```

**Landing Zone Characteristics:**
- **141 Tables** containing raw, unprocessed data
- **11 Views** providing consolidated access to raw data
- **Data Sources:** 15+ security platforms (EDR, SIEM, VM, IAM, etc.)
- **Update Frequency:** Real-time (Snowpipe), Hourly, Daily
- **Data Format:** JSON, CSV, Parquet
- **Retention:** Full history maintained
- **Schema:** Source system schema preserved

---

## Layer 2: DEV_TRANSFORMATION

### ERD: Star Schema Core

This is the **business logic layer** implementing a **star schema** with dimensional modeling.

```mermaid
erDiagram
    %% Core Dimensions
    DIM_OPCO {
        NUMBER OPCO_ID PK
        VARCHAR OPCO_CODE
        VARCHAR OPCO_NAME
        VARCHAR REGION
        VARCHAR DIVISION
        VARCHAR COUNTRY
        TIMESTAMP DW_LOAD_DATE
        TIMESTAMP DW_UPDATE_DATE
    }

    DIM_HOST {
        NUMBER HOST_KEY PK
        TEXT HOST_TRACKING_METHOD
        TEXT HOST_OS
        BOOLEAN INSCOPE
        TIMESTAMP LAST_SCAN_DATE
        TIMESTAMP DW_LOAD_DATE
        NUMBER OPCO_ID FK
        TEXT PRIMARY_USER_ID
    }

    DIM_DATES {
        TIMESTAMP DATE PK
        NUMBER DAY_OF_WEEK
        TEXT DAY_NAME
        NUMBER MONTH_NUM
        TEXT MONTH_NAME
        NUMBER YEAR
        NUMBER QUARTER
        NUMBER WEEK_OF_YEAR
    }

    DIM_USER {
        NUMBER USER_KEY PK
        VARCHAR USER_ID
        VARCHAR EMAIL
        VARCHAR DISPLAY_NAME
        VARCHAR DEPARTMENT
        TIMESTAMP VALID_FROM
        TIMESTAMP VALID_TO
        BOOLEAN IS_CURRENT
    }

    %% Security Dimensions
    DIM_ANCON_USERS {
        TEXT USERNAME PK
        TEXT DISTINGUISHED_NAME PK
        TEXT EMAIL_ADDRESS
        TEXT NAME
        TEXT FIRST_NAME
        TEXT LAST_NAME
        BOOLEAN DISABLED
        TIMESTAMP EXPIRATION_DATE
        TIMESTAMP LAST_LOGON_DATE
    }

    DIM_DEFENDER_ENDPOINTS {
        TEXT DEVICE_ID PK
        TEXT DEVICE_NAME
        TEXT MANAGED_BY
        TEXT OWNERSHIP
        TEXT COMPLIANCE
        TEXT OPERATING_SYSTEM
        TEXT OS_VERSION
        TEXT DEVICE_STATE
        TEXT PRIMARY_USER_UPN
        TIMESTAMP LAST_STATUS_UPDATE
    }

    DIM_CROWDSTRIKE_ENDPOINTS {
        TEXT HOSTNAME PK
        TEXT AGENT_VERSION
        TEXT OS_VERSION
        TEXT PLATFORM_NAME
        TEXT STATUS
        TIMESTAMP LAST_SEEN
        TEXT TAGS
    }

    DIM_QUALYS_VULNERABILITIES {
        NUMBER QID PK
        TEXT TITLE
        TEXT SEVERITY
        NUMBER CVSS_BASE
        TEXT THREAT
        TEXT IMPACT
        TEXT SOLUTION
        TIMESTAMP PUBLISHED_DATE
    }

    DIM_CYBELANGEL_ALERTS {
        TEXT ALERT_KEY PK
        TEXT ALERT_TYPE
        TEXT SEVERITY
        TEXT CATEGORY
        TEXT SOURCE
        TIMESTAMP DETECTION_DATE
        TEXT STATUS
    }

    %% Core Facts
    FACT_EDR {
        NUMBER EDR_KEY PK
        NUMBER DATE_KEY FK
        TEXT HOST_ID FK
        TEXT ENDPOINT_ID FK
        TEXT EDR_PLATFORM
        TEXT AGENT_VERSION
        TEXT AGENT_STATUS
        TIMESTAMP LAST_SEEN_DATE
        NUMBER THREAT_COUNT
        TIMESTAMP LOAD_TIMESTAMP
    }

    FACT_QUALYS {
        NUMBER QUALYS_KEY PK
        NUMBER DATE_KEY FK
        TEXT HOST_ID FK
        NUMBER QID FK
        TEXT SEVERITY
        TEXT STATUS
        TIMESTAMP FIRST_DETECTED
        TIMESTAMP LAST_DETECTED
        NUMBER DAYS_OPEN
        TEXT REMEDIATION_STATUS
    }

    FACT_REMEDIATION_EVENTS {
        NUMBER EVENT_ID PK
        NUMBER HOST_ID FK
        NUMBER VULNERABILITY_ID FK
        TIMESTAMP DETECTION_DATE FK
        TIMESTAMP REMEDIATION_DATE
        NUMBER DAYS_TO_REMEDIATE
        TEXT REMEDIATION_METHOD
        TEXT ASSIGNED_TO
    }

    FACT_DEFENDER_THREATS {
        NUMBER THREAT_ID PK
        TEXT DEVICE_ID FK
        TIMESTAMP DETECTION_TIME FK
        TEXT THREAT_NAME
        TEXT SEVERITY_LEVEL
        TEXT STATUS
        TEXT REMEDIATION_ACTION
    }

    FACT_CYBELANGEL_THREATS {
        TEXT THREAT_KEY PK
        TEXT ALERT_KEY FK
        TIMESTAMP DETECTION_DATE FK
        TEXT THREAT_TYPE
        TEXT SEVERITY
        TEXT SOURCE_URL
        TEXT AFFECTED_ASSET
        TEXT STATUS
        TEXT ASSIGNED_TO
    }

    FACT_AV_HEALTH {
        TEXT OPCO_NAME FK
        TEXT PRODUCT_NAME
        NUMBER TOTAL_MACHINES
        NUMBER ACTIVE_MACHINES
        NUMBER INACTIVE_MACHINES
        TIMESTAMP SNAPSHOT_DATE FK
    }

    %% Relationships
    DIM_OPCO ||--o{ DIM_HOST : "operates"
    DIM_HOST ||--o{ FACT_EDR : "monitored_by"
    DIM_HOST ||--o{ FACT_QUALYS : "scanned"
    DIM_HOST ||--o{ FACT_REMEDIATION_EVENTS : "remediated_on"

    DIM_DATES ||--o{ FACT_EDR : "recorded_on"
    DIM_DATES ||--o{ FACT_QUALYS : "detected_on"
    DIM_DATES ||--o{ FACT_REMEDIATION_EVENTS : "remediated_on"
    DIM_DATES ||--o{ FACT_DEFENDER_THREATS : "detected_on"
    DIM_DATES ||--o{ FACT_CYBELANGEL_THREATS : "detected_on"
    DIM_DATES ||--o{ FACT_AV_HEALTH : "snapshot_date"

    DIM_DEFENDER_ENDPOINTS ||--o{ FACT_DEFENDER_THREATS : "generates"
    DIM_CYBELANGEL_ALERTS ||--o{ FACT_CYBELANGEL_THREATS : "triggers"
    DIM_QUALYS_VULNERABILITIES ||--o{ FACT_QUALYS : "identified_as"
```

### Transformation Layer Details

**32 Dimension Tables:**
1. DIM_OPCO - Operating Companies (3 rows)
2. DIM_HOST - IT Assets (1,662 rows)
3. DIM_DATES - Date Dimension (10,000 rows)
4. DIM_USER - Unified Users (1 row, SCD Type 2)
5. DIM_ANCON_USERS - AD Users (995 rows)
6. DIM_DEFENDER_ENDPOINTS - Microsoft Defender (8,210 rows)
7. DIM_CROWDSTRIKE_ENDPOINTS - CrowdStrike (3,609 rows)
8. DIM_CISCO_AMP - Cisco AMP (4,948 rows)
9. DIM_QUALYS_VULNERABILITIES - CVE Database (210,435 rows)
10. DIM_VULNERABILITY - All Vulnerabilities (631,305 rows)
11. DIM_HARDWARE_INVENTORY - Hardware Assets (21,997 rows)
12. DIM_CYBELANGEL_ALERTS - External Threats (196 rows)
13. DIM_BITSIGHT_RISK_VECTORS - Risk Metrics (7 rows)
14. DIM_FARRANS_ENDPOINTS - Farrans Security (741 rows)
15. DIM_FIXED_VULNERABILITIES - Remediated CVEs (56,345 rows)
16. DIM_SNOW_DEVICES - ServiceNow CMDB (0 rows)
17. DIM_MCAFEE_ENDPOINTS - McAfee Security (292 rows)
18. DIM_SOPHOS_ENDPOINTS - Sophos Security (741 rows)
19. DIM_SYMANTEC_ENDPOINTS - Symantec Security (22,571 rows)
20. DIM_TRELLIX_ENDPOINTS - Trellix Security (34,235 rows)
21. DIM_ZSCALER_ENDPOINTS - Zscaler Security (24,984 rows)
22. DIM_ZEROFOX_ASSETS - ZeroFox Assets (121 rows)
23. DIM_SPLUNK_HOSTS - Splunk Monitoring (4,913 rows)
24. DIM_AV_OPCO - AV by OpCo (108 rows)
25. DIM_SENTINEL_VERSIONS - Sentinel Versions (38 rows)
26. DIM_CROWDSTRIKE_VERSIONS - CrowdStrike Versions (13 rows)
27. DIM_TRENDMICRO_VERSIONS - TrendMicro Versions (6 rows)
28. DIM_QUALYS_SEVERITY - Severity Levels (5 rows)
29. DIM_CLOSE_CODE_MAPPING - Incident Codes (6 rows)
30. DIM_LEVIAT_USERS - Leviat Users (0 rows)
31. DIM_LEVIAT_LIST_USERS - Leviat Lists (0 rows)
32. DIM_HOST_ASSETS - Host Asset Mapping (0 rows)

**23 Fact Tables:**
1. FACT_EDR - EDR Metrics (20 rows)
2. FACT_QUALYS - Vulnerability Scans (20 rows)
3. FACT_REMEDIATION_EVENTS - Remediation Tracking
4. FACT_DEFENDER_THREATS - Defender Detections (1 row)
5. FACT_CYBELANGEL_THREATS - External Threats (0 rows)
6. FACT_AV_HEALTH - Antivirus Health (107 rows)
7. FACT_BITSIGHT_FINDINGS - Security Posture (1,219 rows)
8. FACT_FARRANS_HEALTH - Farrans Monitoring (741 rows)
9. FACT_SENTINEL_ENDPOINTS - Sentinel Agents
10. FACT_QUALYS_HOST_SCANS - Host Scan Results
11. FACT_INCIDENTS - Security Incidents (0 rows)
12. FACT_LEVIAT_SECURITY_EVENTS - Leviat Events (0 rows)
13. ...and 11 more fact tables

**Primary Keys:** 72 tables with PKs
**Foreign Keys:** 17 FKs across 14 tables
**Constraints:** 2 Unique constraints

---

## Layer 3: DEV_REPORTING

### ERD: Analytics & Reporting Layer

```mermaid
graph TB
    subgraph "DEV_REPORTING.SECURITY_ANALYTICS - Analytics Layer"
        subgraph "Executive Dashboards"
            PBI[VW_POWERBI_EXECUTIVE_DASHBOARD<br/>2,862 rows<br/>Power BI Semantic Layer]
            EXEC[VW_EXECUTIVE_KPI_DASHBOARD<br/>1,098 rows<br/>Executive KPIs]
            SEC[VW_SECURITY_POSTURE_SUMMARY<br/>3 OpCos<br/>Security Posture]
        end

        subgraph "Data Quality Views"
            DQ1[VW_QUALITY_ALERTS<br/>DQ Alerts]
            DQ2[VW_QUALITY_SCORE_TREND<br/>30-day Trends]
            DQ3[TBL_DATA_QUALITY_METRICS<br/>7 Metrics]
        end

        subgraph "ETL Monitoring"
            ETL1[VW_ETL_PIPELINE_STATUS<br/>117 Runs]
            ETL2[VW_ETL_ERRORS<br/>Failure Tracking]
            ETL3[ETL_PIPELINE_LOG<br/>Audit Trail]
        end

        subgraph "Performance Analytics"
            PERF1[VW_QUERY_PERFORMANCE<br/>Query History]
            PERF2[VW_PERFORMANCE_COMPARISON<br/>Benchmarks]
            PERF3[PERFORMANCE_BENCHMARKS<br/>Metrics Storage]
        end

        subgraph "Metadata & Governance"
            META1[VW_DATA_DICTIONARY<br/>15 Entries]
            META2[VW_DATA_LINEAGE<br/>10 Flows]
            META3[DATA_DICTIONARY<br/>Catalog]
            META4[DATA_LINEAGE_CATALOG<br/>Lineage Store]
        end

        subgraph "Security Analytics Views (135+)"
            SA1[VW_AGENT_COVERAGE<br/>Agent Deployment]
            SA2[VW_EDR_COVERAGE<br/>EDR Metrics]
            SA3[VW_VULNERABILITY_TRENDS<br/>Vuln Trends]
            SA4[VW_COMPLIANCE_STATUS<br/>Compliance]
            SA5[VW_THREAT_INTELLIGENCE<br/>Threat Intel]
            SA6[... 130+ more views]
        end

        subgraph "KPI Tables"
            KPI1[TBL_KPI_MASTER<br/>3 KPI Definitions]
            KPI2[BOL_CROWDSTRIKE<br/>1,203 rows]
            KPI3[BOL_* Tables<br/>15+ BOL tables]
        end

        subgraph "Stored Procedures"
            SP1[SP_CALCULATE_DATA_QUALITY<br/>DQ Engine]
            SP2[EXTRACT_VIEWS_WITH_SAMPLES<br/>Metadata Extractor]
            SP3[... 8 more procedures]
        end
    end

    PBI --> EXEC
    EXEC --> SEC
    DQ1 --> DQ3
    ETL1 --> ETL3
    META1 --> META3
    META2 --> META4

    style PBI fill:#99ff99
    style EXEC fill:#99ff99
    style SEC fill:#99ff99
    style DQ3 fill:#ffcc99
    style ETL3 fill:#ffcc99
    style META3 fill:#ccccff
    style META4 fill:#ccccff
```

### Reporting Layer Details

**18 Tables:**
- TBL_DATA_QUALITY_METRICS - DQ metrics storage
- TBL_KPI_MASTER - KPI definitions (3 rows)
- DATA_DICTIONARY - Metadata catalog (15 entries)
- DATA_LINEAGE_CATALOG - Lineage tracking (10 entries)
- DATA_QUALITY_SCORECARD - Historical DQ scores
- ETL_PIPELINE_LOG - ETL execution history (117 runs)
- PERFORMANCE_BENCHMARKS - Query benchmarks
- BOL_CROWDSTRIKE - CrowdStrike BOL (1,203 rows)
- ...and 10 more BOL and framework tables

**148 Views** organized by purpose:
1. **Executive (3):** POWERBI, KPI, Security Posture
2. **Data Quality (10+):** Alerts, trends, completeness
3. **ETL Monitoring (5+):** Status, errors, lineage
4. **Performance (5+):** Query tracking, benchmarks
5. **Security Analytics (125+):** Coverage, vulnerabilities, threats, compliance

**10 Stored Procedures:**
- SP_CALCULATE_DATA_QUALITY() - Data quality calculation
- EXTRACT_VIEWS_WITH_SAMPLES() - Metadata extraction
- ...and 8 more reporting automation procedures

---

## Cross-Layer Data Flow

### Complete Data Lineage

```mermaid
graph LR
    subgraph "Source Systems"
        SRC1[CrowdStrike API]
        SRC2[Qualys Scanner]
        SRC3[Active Directory]
        SRC4[ServiceNow CMDB]
        SRC5[Microsoft Defender]
        SRC6[CybelAngel]
        SRC7[15+ Other Sources]
    end

    subgraph "DEV_LANDING"
        L1[L_CROWDSTRIKE_HOSTS]
        L2[L_QUALYS_SCANS]
        L3[AD_COMPUTERS_*]
        L4[SERVICENOW_CMDB]
        L5[L_EDR_THREATS_REALTIME]
    end

    subgraph "DEV_TRANSFORMATION"
        T1[DIM_HOST]
        T2[DIM_QUALYS_VULNERABILITIES]
        T3[DIM_USER]
        T4[FACT_EDR]
        T5[FACT_QUALYS]
        T6[DIM_OPCO]
    end

    subgraph "DEV_REPORTING"
        R1[VW_POWERBI_EXECUTIVE_DASHBOARD]
        R2[VW_EXECUTIVE_KPI_DASHBOARD]
        R3[VW_SECURITY_POSTURE_SUMMARY]
        R4[TBL_DATA_QUALITY_METRICS]
    end

    SRC1 --> L1
    SRC2 --> L2
    SRC3 --> L3
    SRC4 --> L4
    SRC5 --> L5

    L1 -->|Merge CrowdStrike endpoints<br/>Daily| T1
    L2 -->|Parse vulnerabilities<br/>Daily| T2
    L3 -->|Extract users<br/>SCD Type 2| T3
    L5 -->|Aggregate threats<br/>Real-time| T4
    L2 -->|Transform scans<br/>Daily| T5

    T1 --> R1
    T2 --> R1
    T3 --> R1
    T4 --> R1
    T5 --> R1
    T6 --> R1

    T1 --> R2
    T4 --> R2
    T6 --> R2

    T1 --> R3
    T4 --> R3
    T6 --> R3

    T1 --> R4
    T2 --> R4

    style L1 fill:#ffcccc
    style L2 fill:#ffcccc
    style L3 fill:#ffcccc
    style L4 fill:#ffcccc
    style L5 fill:#ffcccc

    style T1 fill:#ccffcc
    style T2 fill:#ccffcc
    style T3 fill:#ccffcc
    style T4 fill:#ccffcc
    style T5 fill:#ccffcc
    style T6 fill:#ccffcc

    style R1 fill:#ccccff
    style R2 fill:#ccccff
    style R3 fill:#ccccff
    style R4 fill:#ccccff
```

### Data Lineage Catalog (10 Entries)

| Source | Target | Transformation | Frequency |
|--------|--------|----------------|-----------|
| DEV_LANDING.L_CROWDSTRIKE_HOSTS | DEV_TRANSFORMATION.DIM_HOST | Merge CrowdStrike endpoints | Daily |
| DEV_LANDING.L_QUALYS_SCANS | DEV_TRANSFORMATION.DIM_QUALYS_VULNERABILITIES | Parse vulnerability data | Daily |
| DEV_LANDING.AD_COMPUTERS | DEV_TRANSFORMATION.DIM_USER | SCD Type 2 merge from AD | Daily |
| DEV_LANDING.L_PAM_USERS | DEV_TRANSFORMATION.DIM_USER | SCD Type 2 merge from PAM | Daily |
| DEV_LANDING.L_EDR_THREATS_REALTIME | DEV_TRANSFORMATION.FACT_EDR | Aggregate threat counts | Real-time |
| DEV_TRANSFORMATION.DIM_HOST | DEV_REPORTING.VW_POWERBI_EXECUTIVE_DASHBOARD | Join with facts for KPIs | On-demand |
| DEV_TRANSFORMATION.DIM_OPCO | DEV_REPORTING.VW_SECURITY_POSTURE_SUMMARY | Aggregate by OpCo | On-demand |
| DEV_TRANSFORMATION.FACT_EDR | DEV_REPORTING.VW_EXECUTIVE_KPI_DASHBOARD | Calculate threat percentages | On-demand |
| DEV_TRANSFORMATION.FACT_QUALYS | DEV_REPORTING.VW_VULNERABILITY_TRENDS | Trend analysis over time | On-demand |
| DEV_TRANSFORMATION.* | DEV_REPORTING.TBL_DATA_QUALITY_METRICS | Calculate DQ scores | 4-hourly |

---

## Key Relationships & Star Schema

### Core Star Schema Pattern

```mermaid
erDiagram
    %% Central Fact Table
    FACT_EDR {
        NUMBER EDR_KEY PK "Surrogate Key"
        NUMBER DATE_KEY FK "→ DIM_DATES"
        TEXT HOST_ID FK "→ DIM_HOST"
        TEXT ENDPOINT_ID FK "→ DIM_DEFENDER_ENDPOINTS"
        TEXT EDR_PLATFORM "CrowdStrike, Defender, etc"
        TEXT AGENT_VERSION "Agent version number"
        NUMBER THREAT_COUNT "Detected threats"
    }

    %% Dimensions
    DIM_DATES {
        TIMESTAMP DATE PK
        NUMBER YEAR "Calendar year"
        NUMBER QUARTER "Q1-Q4"
        TEXT MONTH_NAME "January-December"
        TEXT DAY_NAME "Monday-Sunday"
    }

    DIM_HOST {
        NUMBER HOST_KEY PK
        TEXT HOST_OS "Operating system"
        BOOLEAN INSCOPE "In scope for compliance"
        NUMBER OPCO_ID FK "→ DIM_OPCO"
        TEXT PRIMARY_USER_ID "Primary user"
    }

    DIM_OPCO {
        NUMBER OPCO_ID PK
        VARCHAR OPCO_CODE "OPCO_001, etc"
        VARCHAR OPCO_NAME "North America OpCo"
        VARCHAR REGION "North America, Europe, APAC"
        VARCHAR DIVISION "IT Security"
    }

    DIM_DEFENDER_ENDPOINTS {
        TEXT DEVICE_ID PK
        TEXT DEVICE_NAME "Hostname"
        TEXT COMPLIANCE "Compliant, Non-compliant"
        TEXT DEVICE_STATE "Active, Inactive"
    }

    %% Star Schema Relationships
    DIM_DATES ||--o{ FACT_EDR : "date_dimension"
    DIM_HOST ||--o{ FACT_EDR : "host_dimension"
    DIM_DEFENDER_ENDPOINTS ||--o{ FACT_EDR : "endpoint_dimension"
    DIM_OPCO ||--o{ DIM_HOST : "opco_hierarchy"
```

### Relationship Types

**One-to-Many (1:M):**
- DIM_OPCO → DIM_HOST (one OpCo has many hosts)
- DIM_HOST → FACT_EDR (one host generates many EDR events)
- DIM_DATES → FACT_* (one date has many facts)

**Many-to-Many (M:N) - Resolved via Bridge Tables:**
- DIM_USER ←→ DIM_HOST (via user-host assignment table)
- DIM_QUALYS_VULNERABILITIES ←→ DIM_HOST (via FACT_QUALYS)

**Hierarchies:**
- DIM_OPCO: Country → Region → Division → OpCo
- DIM_DATES: Year → Quarter → Month → Day
- DIM_HOST: OpCo → Region → Host

---

## Data Model Characteristics

### SCD Type 2 Implementation
**DIM_USER** implements Slowly Changing Dimension Type 2:
- `USER_KEY` - Surrogate key (changes with each version)
- `USER_ID` - Natural key (stays the same)
- `VALID_FROM` - Record start date
- `VALID_TO` - Record end date
- `IS_CURRENT` - Current version flag

### Grain Definitions

**FACT_EDR:**
- Grain: One row per host per EDR platform per day
- Dimensions: Date, Host, Endpoint, Platform

**FACT_QUALYS:**
- Grain: One row per vulnerability per host per scan
- Dimensions: Date, Host, Vulnerability (QID)

**FACT_REMEDIATION_EVENTS:**
- Grain: One row per vulnerability remediation event
- Dimensions: Detection Date, Remediation Date, Host, Vulnerability

---

## Data Volumes & Growth

| Layer | Tables | Views | Procedures | Total Objects | Data Size |
|-------|--------|-------|------------|---------------|-----------|
| Landing | 141 | 11 | 0 | 152 | ~500 MB |
| Transformation | 117 | 50+ | 15 | 184+ | ~25 GB |
| Reporting | 18 | 148 | 10 | 176 | ~2 GB |
| **TOTAL** | **276** | **209+** | **25** | **512+** | **~28 GB** |

**Growth Projections:**
- Daily growth: ~100 MB/day (landing layer)
- Monthly growth: ~3 GB/month (transformation layer)
- Annual retention: 3 years (7.3 TB projected at year 3)

---

## Documentation Generation Date
**Created:** October 7, 2025
**Last Updated:** October 7, 2025
**Version:** 1.0
**Author:** Fuad Onate - GenericCorp Data Engineering Team
**Status:** Production-Ready Documentation
