# SECURITY_ANALYTICS Additional ERD Diagrams
**Detailed Entity Relationship Diagrams by Domain**

---

## Table of Contents
1. [Security Domain ERD](#security-domain-erd)
2. [Vulnerability Management ERD](#vulnerability-management-erd)
3. [Asset & Endpoint Management ERD](#asset--endpoint-management-erd)
4. [Data Quality & Monitoring ERD](#data-quality--monitoring-erd)
5. [Real-Time Threat Detection ERD](#real-time-threat-detection-erd)
6. [ETL & Data Lineage ERD](#etl--data-lineage-erd)

---

## Security Domain ERD

### Complete Security Platform Integration

```mermaid
erDiagram
    %% Core Security Dimensions
    DIM_HOST {
        NUMBER HOST_KEY PK
        TEXT HOST_TRACKING_METHOD
        TEXT HOST_OS
        BOOLEAN INSCOPE
        NUMBER OPCO_ID FK
    }

    DIM_OPCO {
        NUMBER OPCO_ID PK
        VARCHAR OPCO_CODE
        VARCHAR OPCO_NAME
        VARCHAR REGION
        VARCHAR DIVISION
    }

    DIM_USER {
        NUMBER USER_KEY PK
        VARCHAR USER_ID
        VARCHAR EMAIL
        VARCHAR DISPLAY_NAME
        TIMESTAMP VALID_FROM
        TIMESTAMP VALID_TO
        BOOLEAN IS_CURRENT
    }

    %% Endpoint Protection Platforms
    DIM_DEFENDER_ENDPOINTS {
        TEXT DEVICE_ID PK
        TEXT DEVICE_NAME
        TEXT COMPLIANCE
        TEXT DEVICE_STATE
        TEXT PRIMARY_USER_UPN
    }

    DIM_CROWDSTRIKE_ENDPOINTS {
        TEXT HOSTNAME PK
        TEXT AGENT_VERSION
        TEXT STATUS
        TEXT PLATFORM_NAME
    }

    DIM_CISCO_AMP {
        TEXT HOSTNAME PK
        TEXT CONNECTOR_GUID
        TEXT OS_VERSION
        TEXT POLICY_NAME
    }

    DIM_SYMANTEC_ENDPOINTS {
        TEXT COMPUTER_NAME PK
        TEXT AGENT_VERSION
        TEXT LAST_UPDATE
        TEXT GROUP_NAME
    }

    DIM_TRELLIX_ENDPOINTS {
        TEXT HOSTNAME PK
        TEXT AGENT_VERSION
        TEXT TAG
        TEXT OS_TYPE
    }

    DIM_MCAFEE_ENDPOINTS {
        TEXT SYSTEM_NAME PK
        TEXT AGENT_VERSION
        TEXT STATUS
    }

    DIM_SOPHOS_ENDPOINTS {
        TEXT HOSTNAME PK
        TEXT TAMPER_PROTECTION
        TEXT HEALTH_STATUS
    }

    %% External Threat Intelligence
    DIM_CYBELANGEL_ALERTS {
        TEXT ALERT_KEY PK
        TEXT ALERT_TYPE
        TEXT SEVERITY
        TEXT CATEGORY
    }

    DIM_ZEROFOX_ASSETS {
        TEXT ASSET_ID PK
        TEXT ASSET_TYPE
        TEXT NETWORK
        TEXT STATUS
    }

    DIM_BITSIGHT_RISK_VECTORS {
        TEXT RISK_VECTOR_LABEL PK
        TEXT CATEGORY
        NUMBER GRADE
    }

    %% Security Facts
    FACT_EDR {
        NUMBER EDR_KEY PK
        TEXT HOST_ID FK
        TEXT EDR_PLATFORM
        NUMBER THREAT_COUNT
        TIMESTAMP LAST_SEEN_DATE
    }

    FACT_DEFENDER_THREATS {
        NUMBER THREAT_ID PK
        TEXT DEVICE_ID FK
        TEXT THREAT_NAME
        TEXT SEVERITY_LEVEL
        TEXT STATUS
    }

    FACT_CYBELANGEL_THREATS {
        TEXT THREAT_KEY PK
        TEXT ALERT_KEY FK
        TEXT THREAT_TYPE
        TEXT SEVERITY
    }

    FACT_BITSIGHT_FINDINGS {
        TEXT FINDING_KEY PK
        TEXT RISK_VECTOR_ID FK
        TEXT SEVERITY
        TEXT AFFECTS_RATING
    }

    %% Relationships
    DIM_OPCO ||--o{ DIM_HOST : "operates"
    DIM_HOST ||--o{ FACT_EDR : "monitored"
    DIM_DEFENDER_ENDPOINTS ||--o{ FACT_DEFENDER_THREATS : "generates"
    DIM_CYBELANGEL_ALERTS ||--o{ FACT_CYBELANGEL_THREATS : "triggers"
    DIM_BITSIGHT_RISK_VECTORS ||--o{ FACT_BITSIGHT_FINDINGS : "identified_in"
```

---

## Vulnerability Management ERD

### Qualys Vulnerability Scanning Architecture

```mermaid
erDiagram
    DIM_HOST {
        NUMBER HOST_KEY PK
        TEXT HOST_TRACKING_METHOD
        TEXT HOST_OS
        BOOLEAN INSCOPE
        TIMESTAMP LAST_SCAN_DATE
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

    DIM_VULNERABILITY {
        TEXT CVE_ID PK
        TEXT TITLE
        TEXT DESCRIPTION
        NUMBER CVSS_V3_SCORE
        TEXT SEVERITY_RATING
        TIMESTAMP PUBLISHED_DATE
    }

    DIM_QUALYS_SEVERITY {
        NUMBER SEVERITY_LEVEL PK
        TEXT SEVERITY_NAME
        TEXT COLOR_CODE
        NUMBER MIN_CVSS
        NUMBER MAX_CVSS
    }

    DIM_FIXED_VULNERABILITIES {
        NUMBER QID PK
        TEXT TITLE
        TEXT SEVERITY
        TIMESTAMP FIXED_DATE
        TEXT FIXED_METHOD
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

    FACT_QUALYS_HOST_SCANS {
        TEXT HOST_ID FK
        TIMESTAMP SCAN_DATE
        NUMBER CRITICAL_COUNT
        NUMBER HIGH_COUNT
        NUMBER MEDIUM_COUNT
        NUMBER LOW_COUNT
        NUMBER TOTAL_VULNS
    }

    FACT_REMEDIATION_EVENTS {
        NUMBER EVENT_ID PK
        NUMBER HOST_ID FK
        NUMBER VULNERABILITY_ID FK
        TIMESTAMP DETECTION_DATE
        TIMESTAMP REMEDIATION_DATE
        NUMBER DAYS_TO_REMEDIATE
        TEXT REMEDIATION_METHOD
        TEXT ASSIGNED_TO
    }

    DIM_HOST ||--o{ FACT_QUALYS : "scanned"
    DIM_QUALYS_VULNERABILITIES ||--o{ FACT_QUALYS : "found_as"
    DIM_VULNERABILITY ||--o{ FACT_QUALYS : "identified_as"
    DIM_HOST ||--o{ FACT_QUALYS_HOST_SCANS : "scan_results"
    DIM_HOST ||--o{ FACT_REMEDIATION_EVENTS : "remediated_on"
    DIM_QUALYS_VULNERABILITIES ||--o{ FACT_REMEDIATION_EVENTS : "vulnerability_fixed"
    DIM_QUALYS_SEVERITY ||--o{ FACT_QUALYS : "categorized_as"
```

---

## Asset & Endpoint Management ERD

### IT Asset Inventory & Tracking

```mermaid
erDiagram
    DIM_OPCO {
        NUMBER OPCO_ID PK
        VARCHAR OPCO_CODE
        VARCHAR OPCO_NAME
        VARCHAR REGION
        VARCHAR DIVISION
        VARCHAR COUNTRY
    }

    DIM_HOST {
        NUMBER HOST_KEY PK
        TEXT HOST_TRACKING_METHOD
        TEXT HOST_OS
        BOOLEAN INSCOPE
        NUMBER OPCO_ID FK
        TEXT PRIMARY_USER_ID FK
    }

    DIM_HARDWARE_INVENTORY {
        TEXT COMPUTER_NAME PK
        TEXT MANUFACTURER
        TEXT MODEL
        TEXT SERIAL_NUMBER
        TEXT PROCESSOR
        NUMBER RAM_GB
        NUMBER STORAGE_GB
        TEXT OPERATING_SYSTEM
        TIMESTAMP PURCHASE_DATE
        TIMESTAMP WARRANTY_EXPIRY
        TEXT ASSET_TAG
        TEXT LOCATION
        TEXT DEPARTMENT
        TEXT OWNER
    }

    DIM_SNOW_DEVICES {
        TEXT COMPUTER_NAME PK
        TEXT SYS_ID
        TEXT ASSET_TAG
        TEXT SERIAL_NUMBER
        TEXT MODEL_CATEGORY
        TEXT MANUFACTURER
        TEXT ASSIGNMENT_GROUP
        TEXT ASSIGNED_TO
        TEXT LOCATION
        TEXT DEPARTMENT
    }

    DIM_ANCON_USERS {
        TEXT USERNAME PK
        TEXT EMAIL_ADDRESS
        TEXT DISPLAY_NAME
        TEXT FIRST_NAME
        TEXT LAST_NAME
        BOOLEAN DISABLED
        TIMESTAMP LAST_LOGON_DATE
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

    FACT_SENTINEL_ENDPOINTS {
        TEXT ENDPOINT_NAME PK
        TEXT DEVICE_ID FK
        TEXT AGENT_VERSION
        TEXT CONNECTION_STATUS
        TEXT POLICY_NAME
        TIMESTAMP LAST_CONNECTED
    }

    DIM_OPCO ||--o{ DIM_HOST : "owns"
    DIM_HOST ||--o{ DIM_HARDWARE_INVENTORY : "hardware_details"
    DIM_HOST ||--o{ DIM_SNOW_DEVICES : "cmdb_record"
    DIM_USER ||--o{ DIM_HOST : "primary_user"
    DIM_ANCON_USERS ||--o{ DIM_USER : "source_user"
    DIM_HOST ||--o{ FACT_SENTINEL_ENDPOINTS : "agent_installed"
```

---

## Data Quality & Monitoring ERD

### Data Quality Framework Architecture

```mermaid
erDiagram
    DATA_QUALITY_SCORECARD {
        NUMBER SCORECARD_ID PK
        TEXT TABLE_NAME
        DATE SCORECARD_DATE
        NUMBER COMPLETENESS_SCORE
        NUMBER ACCURACY_SCORE
        NUMBER CONSISTENCY_SCORE
        NUMBER TIMELINESS_SCORE
        NUMBER OVERALL_SCORE
        NUMBER TOTAL_ROWS
        NUMBER NULL_COUNT
        NUMBER DUPLICATE_COUNT
        NUMBER ORPHANED_COUNT
    }

    TBL_DATA_QUALITY_METRICS {
        NUMBER METRIC_ID PK
        TEXT TABLE_NAME
        TEXT METRIC_NAME
        NUMBER METRIC_VALUE
        TEXT STATUS
        TIMESTAMP CALCULATED_AT
    }

    DATA_QUALITY_RULES {
        NUMBER RULE_ID PK
        TEXT TABLE_NAME
        TEXT COLUMN_NAME
        TEXT RULE_TYPE
        TEXT RULE_DEFINITION
        TEXT SEVERITY
        BOOLEAN IS_ACTIVE
    }

    BUSINESS_RULE_VIOLATIONS {
        NUMBER VIOLATION_ID PK
        NUMBER RULE_ID FK
        TEXT TABLE_NAME
        TEXT RECORD_ID
        TEXT VIOLATION_DESCRIPTION
        TIMESTAMP DETECTED_AT
        TEXT STATUS
    }

    ETL_PIPELINE_LOG {
        NUMBER LOG_ID PK
        TEXT PIPELINE_NAME
        TEXT SOURCE_TABLE
        TEXT TARGET_TABLE
        NUMBER ROWS_PROCESSED
        TEXT STATUS
        TEXT ERROR_MESSAGE
        TIMESTAMP CREATED_AT
    }

    ETL_ERROR_LOG {
        NUMBER ERROR_ID PK
        NUMBER PIPELINE_ID FK
        TEXT ERROR_TYPE
        TEXT ERROR_MESSAGE
        TEXT ERROR_DETAILS
        TIMESTAMP ERROR_TIMESTAMP
    }

    PERFORMANCE_BENCHMARKS {
        NUMBER BENCHMARK_ID PK
        TEXT BENCHMARK_NAME
        TEXT QUERY_TEXT
        NUMBER EXECUTION_TIME_MS
        NUMBER ROWS_RETURNED
        TEXT WAREHOUSE_SIZE
        TIMESTAMP EXECUTED_AT
    }

    DATA_QUALITY_RULES ||--o{ BUSINESS_RULE_VIOLATIONS : "validates"
    ETL_PIPELINE_LOG ||--o{ ETL_ERROR_LOG : "errors"
```

---

## Real-Time Threat Detection ERD

### Near Real-Time Security Event Processing

```mermaid
erDiagram
    %% Landing - Real-time ingestion
    L_EDR_THREATS_REALTIME {
        TEXT THREAT_ID PK
        TEXT HOST_ID
        TEXT THREAT_NAME
        TEXT SEVERITY
        TEXT EDR_PLATFORM
        TIMESTAMP DETECTED_AT
        TEXT STATUS
        TEXT RESPONSE_ACTION
    }

    L_CRITICAL_VULNS_REALTIME {
        TEXT VULN_ID PK
        TEXT HOST_ID
        TEXT CVE_ID
        NUMBER CVSS_SCORE
        TEXT SEVERITY
        TIMESTAMP DISCOVERED_AT
        TEXT EXPLOIT_AVAILABLE
    }

    %% Transformation - Business logic
    FACT_EDR {
        NUMBER EDR_KEY PK
        NUMBER DATE_KEY FK
        TEXT HOST_ID FK
        TEXT ENDPOINT_ID FK
        TEXT EDR_PLATFORM
        TEXT AGENT_STATUS
        NUMBER THREAT_COUNT
        TIMESTAMP LAST_SEEN_DATE
    }

    DIM_HOST {
        NUMBER HOST_KEY PK
        TEXT HOST_OS
        NUMBER OPCO_ID FK
    }

    DIM_DATES {
        TIMESTAMP DATE PK
        NUMBER YEAR
        NUMBER QUARTER
        TEXT MONTH_NAME
    }

    %% Reporting - Real-time dashboards
    VW_REALTIME_THREAT_ALERTS {
        TEXT THREAT_ID
        TEXT HOST_NAME
        TEXT THREAT_NAME
        TEXT SEVERITY
        TEXT OPCO_NAME
        TIMESTAMP DETECTED_AT
        TEXT STATUS
    }

    VW_CRITICAL_VULNS_DASHBOARD {
        TEXT VULN_ID
        TEXT HOST_NAME
        TEXT CVE_ID
        NUMBER CVSS_SCORE
        TEXT OPCO_NAME
        TIMESTAMP DISCOVERED_AT
        NUMBER HOURS_OPEN
    }

    %% Data flow
    L_EDR_THREATS_REALTIME -.->|Snowpipe Continuous| FACT_EDR
    L_CRITICAL_VULNS_REALTIME -.->|Snowpipe Continuous| FACT_EDR
    FACT_EDR --> VW_REALTIME_THREAT_ALERTS
    FACT_EDR --> VW_CRITICAL_VULNS_DASHBOARD
    DIM_HOST --> VW_REALTIME_THREAT_ALERTS
    DIM_HOST --> VW_CRITICAL_VULNS_DASHBOARD
```

---

## ETL & Data Lineage ERD

### Complete Data Lineage Tracking

```mermaid
erDiagram
    DATA_LINEAGE_CATALOG {
        NUMBER LINEAGE_ID PK
        TEXT SOURCE_DATABASE
        TEXT SOURCE_SCHEMA
        TEXT SOURCE_TABLE
        TEXT TARGET_DATABASE
        TEXT TARGET_SCHEMA
        TEXT TARGET_TABLE
        TEXT TRANSFORMATION_LOGIC
        TEXT ETL_PROCEDURE
        TEXT UPDATE_FREQUENCY
        TEXT DATA_OWNER
        TIMESTAMP LAST_UPDATED
    }

    ETL_PIPELINE_LOG {
        NUMBER LOG_ID PK
        TEXT PIPELINE_NAME
        TEXT SOURCE_TABLE
        TEXT TARGET_TABLE
        NUMBER ROWS_PROCESSED
        TEXT STATUS
        TIMESTAMP CREATED_AT
    }

    ETL_ORCHESTRATION_LOG {
        NUMBER ORCHESTRATION_ID PK
        TEXT ORCHESTRATION_NAME
        TEXT PIPELINE_SEQUENCE
        TIMESTAMP START_TIME
        TIMESTAMP END_TIME
        TEXT STATUS
    }

    DATA_DICTIONARY {
        NUMBER DICT_ID PK
        TEXT TABLE_NAME
        TEXT COLUMN_NAME
        TEXT DATA_TYPE
        TEXT BUSINESS_NAME
        TEXT DESCRIPTION
        BOOLEAN IS_PK
        BOOLEAN IS_FK
        TEXT FK_REFERENCES
        TEXT SAMPLE_VALUES
    }

    %% Transformation Procedures
    SP_POPULATE_FACT_TABLES {
        TEXT PROCEDURE_NAME PK
        TEXT LOGIC "Populates all fact tables from landing"
    }

    SP_REFRESH_DIMENSIONS {
        TEXT PROCEDURE_NAME PK
        TEXT LOGIC "Refreshes dimension tables with SCD"
    }

    SP_CALCULATE_DATA_QUALITY_SCORE {
        TEXT PROCEDURE_NAME PK
        TEXT LOGIC "Calculates DQ scores for all tables"
    }

    %% Scheduled Tasks
    TASK_DAILY_HEALTH_CHECK {
        TEXT TASK_NAME PK
        TEXT SCHEDULE "Daily at 6 AM"
        TEXT WAREHOUSE "DEV_WH"
    }

    TASK_DATA_QUALITY_MONITOR {
        TEXT TASK_NAME PK
        TEXT SCHEDULE "Every 4 hours"
        TEXT WAREHOUSE "DEV_WH"
    }

    DATA_LINEAGE_CATALOG ||--o{ ETL_PIPELINE_LOG : "tracks_execution"
    ETL_ORCHESTRATION_LOG ||--o{ ETL_PIPELINE_LOG : "orchestrates"
    TASK_DAILY_HEALTH_CHECK -.->|calls| SP_POPULATE_FACT_TABLES
    TASK_DATA_QUALITY_MONITOR -.->|calls| SP_CALCULATE_DATA_QUALITY_SCORE
```

---

## Power BI Integration ERD

### Semantic Layer for Executive Dashboards

```mermaid
erDiagram
    %% Core Star Schema for Power BI
    VW_POWERBI_EXECUTIVE_DASHBOARD {
        TIMESTAMP Date PK
        NUMBER Year
        NUMBER Quarter
        TEXT Month_Name
        TEXT Operating_Company
        TEXT Region
        TEXT Division
        NUMBER EDR_Coverage_Pct
        NUMBER Vulnerability_Count
        NUMBER Critical_Vulns
        NUMBER Threat_Count
        NUMBER Assets_Total
        NUMBER Assets_Compliant
    }

    DIM_DATES {
        TIMESTAMP DATE PK
        NUMBER YEAR
        NUMBER QUARTER
        TEXT MONTH_NAME
    }

    DIM_OPCO {
        NUMBER OPCO_ID PK
        VARCHAR OPCO_NAME
        VARCHAR REGION
        VARCHAR DIVISION
    }

    DIM_HOST {
        NUMBER HOST_KEY PK
        NUMBER OPCO_ID FK
    }

    FACT_EDR {
        NUMBER EDR_KEY PK
        NUMBER DATE_KEY FK
        TEXT HOST_ID FK
        NUMBER THREAT_COUNT
    }

    FACT_QUALYS {
        NUMBER QUALYS_KEY PK
        NUMBER DATE_KEY FK
        TEXT HOST_ID FK
        NUMBER QID FK
    }

    TBL_KPI_MASTER {
        NUMBER KPI_ID PK
        TEXT KPI_NAME
        TEXT KPI_CATEGORY
        TEXT CALCULATION_LOGIC
        TEXT OWNER
    }

    %% Power BI Aggregations
    VW_EXECUTIVE_KPI_DASHBOARD {
        TEXT OPCO_NAME
        TEXT REGION
        NUMBER TOTAL_HOSTS
        NUMBER HOSTS_WITH_THREATS
        NUMBER TOTAL_THREATS
        NUMBER THREAT_PERCENTAGE
    }

    VW_SECURITY_POSTURE_SUMMARY {
        TEXT OPCO_NAME
        TEXT REGION
        NUMBER TOTAL_ASSETS
        NUMBER EDR_DEPLOYMENTS
        NUMBER TOTAL_THREATS_DETECTED
        NUMBER DAYS_SINCE_LAST_SCAN
    }

    DIM_DATES --> VW_POWERBI_EXECUTIVE_DASHBOARD
    DIM_OPCO --> VW_POWERBI_EXECUTIVE_DASHBOARD
    DIM_HOST --> VW_POWERBI_EXECUTIVE_DASHBOARD
    FACT_EDR --> VW_POWERBI_EXECUTIVE_DASHBOARD
    FACT_QUALYS --> VW_POWERBI_EXECUTIVE_DASHBOARD
    TBL_KPI_MASTER -.->|defines| VW_EXECUTIVE_KPI_DASHBOARD
```

---

## Business Intelligence Views Hierarchy

```mermaid
graph TB
    subgraph "Executive Layer - Power BI"
        PBI[VW_POWERBI_EXECUTIVE_DASHBOARD<br/>2,862 rows]
        EXEC[VW_EXECUTIVE_KPI_DASHBOARD<br/>1,098 rows]
        SEC[VW_SECURITY_POSTURE_SUMMARY<br/>3 OpCos]
    end

    subgraph "Operational Layer - Analytics"
        COV[VW_AGENT_COVERAGE<br/>Coverage Metrics]
        EDR[VW_EDR_COVERAGE<br/>EDR Status]
        VULN[VW_VULNERABILITY_TRENDS<br/>Trend Analysis]
        COMP[VW_COMPLIANCE_STATUS<br/>Compliance]
    end

    subgraph "Technical Layer - Deep Dive"
        DETAIL1[VW_HOST_VULNERABILITY_DETAIL<br/>Granular Data]
        DETAIL2[VW_ENDPOINT_HEALTH_DETAIL<br/>Health Metrics]
        DETAIL3[VW_THREAT_INVESTIGATION<br/>Forensics]
    end

    subgraph "Data Layer - Star Schema"
        DIM[32 Dimension Tables]
        FACT[23 Fact Tables]
    end

    DIM --> DETAIL1
    DIM --> DETAIL2
    DIM --> DETAIL3
    FACT --> DETAIL1
    FACT --> DETAIL2
    FACT --> DETAIL3

    DETAIL1 --> COV
    DETAIL1 --> EDR
    DETAIL2 --> VULN
    DETAIL3 --> COMP

    COV --> PBI
    EDR --> PBI
    VULN --> EXEC
    COMP --> SEC

    style PBI fill:#99ff99
    style EXEC fill:#99ff99
    style SEC fill:#99ff99
    style DIM fill:#ccccff
    style FACT fill:#ffcccc
```

---

## Dimensional Hierarchy Diagrams

### Geographic & Organizational Hierarchy

```mermaid
graph TD
    CORP[Corporate<br/>GenericCorp Group]

    CORP --> NA[North America]
    CORP --> EU[Europe]
    CORP --> APAC[Asia Pacific]

    NA --> NAOPCO1[North America OpCo<br/>OPCO_001]
    EU --> EUOPCO1[Europe OpCo<br/>OPCO_002]
    APAC --> APOPCO1[APAC OpCo<br/>OPCO_003]

    NAOPCO1 --> DIV1[IT Security Division]
    EUOPCO1 --> DIV2[IT Security Division]
    APOPCO1 --> DIV3[IT Security Division]

    DIV1 --> HOSTS1[1,662 Hosts]
    DIV2 --> HOSTS2[Hosts]
    DIV3 --> HOSTS3[Hosts]

    HOSTS1 --> USERS1[995 Users]
    HOSTS1 --> ENDPOINTS1[8,210 Endpoints]
    HOSTS1 --> ASSETS1[21,997 Assets]

    style CORP fill:#ff9999
    style NA fill:#99ccff
    style EU fill:#99ccff
    style APAC fill:#99ccff
    style NAOPCO1 fill:#99ff99
    style HOSTS1 fill:#ffcc99
```

### Time Dimension Hierarchy

```mermaid
graph TD
    DIM_DATES[DIM_DATES<br/>10,000 rows]

    DIM_DATES --> YEAR[Year<br/>2000-2027]
    YEAR --> QUARTER[Quarter<br/>Q1, Q2, Q3, Q4]
    QUARTER --> MONTH[Month<br/>January-December]
    MONTH --> DAY[Day<br/>1-31]

    DAY --> DOW[Day of Week<br/>Monday-Sunday]
    MONTH --> WOY[Week of Year<br/>1-52]

    style DIM_DATES fill:#ccccff
    style YEAR fill:#99ccff
    style QUARTER fill:#99ccff
    style MONTH fill:#99ccff
    style DAY fill:#99ccff
```

---

**Document Version:** 1.0
**Created:** October 7, 2025
**Purpose:** Detailed ERD diagrams for specific domains within SECURITY_ANALYTICS Data Warehouse
