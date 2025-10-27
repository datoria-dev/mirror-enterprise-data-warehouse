# 📊 Data Model (ERD) - SECURITY_ANALYTICS Data Warehouse

## Overview

This document provides the **Entity Relationship Diagram (ERD)** and detailed schema documentation for the SECURITY_ANALYTICS Data Warehouse. The data model implements a **star schema** design with 32 dimension tables and 72 fact tables, enforcing referential integrity with 57 primary keys and 16 foreign keys.

---

## 🌟 Star Schema Overview

::: mermaid
erDiagram
    DIM_DATE ||--o{ FACT_SECURITY_EVENTS : "event_date_key"
    DIM_USER_UNIFIED ||--o{ FACT_SECURITY_EVENTS : "user_key"
    DIM_DEVICE ||--o{ FACT_SECURITY_EVENTS : "device_key"
    DIM_SECURITY_SERVICE ||--o{ FACT_SECURITY_EVENTS : "service_key"
    DIM_VULNERABILITY ||--o{ FACT_VULNERABILITIES : "vuln_key"
    DIM_DEVICE ||--o{ FACT_VULNERABILITIES : "device_key"
    DIM_DATE ||--o{ FACT_VULNERABILITIES : "scan_date_key"
    DIM_THREAT ||--o{ FACT_THREATS : "threat_key"
    DIM_DATE ||--o{ FACT_THREATS : "detection_date_key"

    DIM_DATE {
        INTEGER date_key PK
        DATE calendar_date UK
        INTEGER year
        INTEGER quarter
        INTEGER month
        INTEGER week
        STRING day_of_week
        BOOLEAN is_weekend
        BOOLEAN is_holiday
    }

    DIM_USER_UNIFIED {
        STRING user_key PK
        STRING username
        STRING email_address
        STRING department
        STRING location
        STRING job_title
        TIMESTAMP valid_from
        TIMESTAMP valid_to
        BOOLEAN is_current
    }

    DIM_DEVICE {
        STRING device_key PK
        STRING hostname
        STRING ip_address
        STRING mac_address
        STRING os_type
        STRING os_version
        STRING device_type
        STRING location
        BOOLEAN is_active
    }

    DIM_SECURITY_SERVICE {
        INTEGER service_key PK
        STRING service_name
        STRING service_category
        STRING vendor
        STRING description
        TIMESTAMP onboarded_date
    }

    DIM_VULNERABILITY {
        STRING vuln_key PK
        STRING cve_id UK
        STRING title
        FLOAT cvss_score
        STRING severity
        STRING description
        DATE published_date
        DATE last_modified_date
    }

    DIM_THREAT {
        STRING threat_key PK
        STRING threat_type
        STRING threat_family
        STRING attack_vector
        STRING description
        STRING severity
    }

    FACT_SECURITY_EVENTS {
        INTEGER event_key PK
        INTEGER date_key FK
        STRING user_key FK
        STRING device_key FK
        INTEGER service_key FK
        TIMESTAMP event_timestamp
        STRING event_type
        STRING severity
        STRING status
        STRING description
        INTEGER event_count
    }

    FACT_VULNERABILITIES {
        INTEGER vuln_fact_key PK
        INTEGER scan_date_key FK
        STRING device_key FK
        STRING vuln_key FK
        INTEGER days_open
        STRING remediation_status
        DATE last_scan_date
        BOOLEAN is_exploitable
    }

    FACT_THREATS {
        INTEGER threat_fact_key PK
        INTEGER detection_date_key FK
        STRING threat_key FK
        STRING device_key FK
        INTEGER threat_count
        STRING mitigation_status
        TIMESTAMP first_detected
        TIMESTAMP last_detected
    }
:::

---

## 📐 Dimension Tables (32 Total)

### Core Conformed Dimensions

#### 1. DIM_DATE (Time Intelligence)
```sql
CREATE OR REPLACE TABLE DIM_DATE (
    -- Primary Key
    date_key INTEGER PRIMARY KEY,

    -- Calendar Attributes
    calendar_date DATE UNIQUE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20),
    week INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_of_week_name VARCHAR(20),
    day_of_year INTEGER NOT NULL,

    -- Fiscal Attributes
    fiscal_year INTEGER,
    fiscal_quarter INTEGER,
    fiscal_month INTEGER,

    -- Flags
    is_weekend BOOLEAN DEFAULT FALSE,
    is_holiday BOOLEAN DEFAULT FALSE,
    is_business_day BOOLEAN DEFAULT TRUE,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rows: 1,826 (5 years: 2020-2025)
-- Pre-populated for reporting performance
```

#### 2. DIM_USER_UNIFIED (Consolidated Identity)
```sql
CREATE OR REPLACE TABLE DIM_USER_UNIFIED (
    -- Primary Key
    user_key VARCHAR(32) PRIMARY KEY,  -- MD5 hash of email

    -- User Attributes
    username VARCHAR(100) NOT NULL,
    email_address VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    department VARCHAR(100),
    location VARCHAR(100),
    job_title VARCHAR(150),
    employee_id VARCHAR(50),

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    account_status VARCHAR(50),

    -- SCD Type 2 Attributes
    valid_from TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valid_to TIMESTAMP NOT NULL DEFAULT '9999-12-31 23:59:59',
    is_current BOOLEAN DEFAULT TRUE,

    -- Source Tracking
    source_systems ARRAY,  -- ['CrowdStrike', 'Okta', 'Qualys']
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rows: 8,542 unique users
-- Consolidated from 15 security services
-- SCD Type 2 for historical tracking
```

#### 3. DIM_DEVICE (Asset Inventory)
```sql
CREATE OR REPLACE TABLE DIM_DEVICE (
    -- Primary Key
    device_key VARCHAR(32) PRIMARY KEY,  -- MD5 hash of hostname

    -- Device Identification
    hostname VARCHAR(255) NOT NULL,
    fqdn VARCHAR(500),
    ip_address VARCHAR(45),
    mac_address VARCHAR(17),
    device_serial VARCHAR(100),

    -- Device Attributes
    device_type VARCHAR(50),  -- Server, Workstation, Mobile, etc.
    os_type VARCHAR(50),      -- Windows, Linux, macOS, etc.
    os_version VARCHAR(100),
    os_build VARCHAR(50),

    -- Location & Ownership
    location VARCHAR(100),
    site_code VARCHAR(20),
    department VARCHAR(100),
    owner_email VARCHAR(255),

    -- Security Posture
    has_antivirus BOOLEAN DEFAULT FALSE,
    has_edr BOOLEAN DEFAULT FALSE,
    is_managed BOOLEAN DEFAULT FALSE,
    last_scan_date TIMESTAMP,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    decommissioned_date TIMESTAMP,

    -- Metadata
    first_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rows: 12,453 devices
-- Updated from CrowdStrike, Qualys, Splunk
```

#### 4. DIM_SECURITY_SERVICE (Tool Metadata)
```sql
CREATE OR REPLACE TABLE DIM_SECURITY_SERVICE (
    -- Primary Key
    service_key INTEGER AUTOINCREMENT PRIMARY KEY,

    -- Service Attributes
    service_name VARCHAR(100) NOT NULL UNIQUE,
    service_category VARCHAR(50),  -- EDR, VM, AV, SIEM, TI, IAM
    vendor VARCHAR(100),
    description TEXT,

    -- Integration Details
    api_endpoint VARCHAR(500),
    data_format VARCHAR(20),  -- JSON, CSV, XML
    ingestion_method VARCHAR(50),  -- Snowpipe, Batch, API

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    onboarded_date DATE NOT NULL,
    last_data_received TIMESTAMP,

    -- SLA Metrics
    expected_frequency_minutes INTEGER,
    data_quality_score FLOAT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rows: 15 security services
-- Maps to external data sources
```

---

### Security-Specific Dimensions

#### 5. DIM_VULNERABILITY (CVE + CVSS)
```sql
CREATE OR REPLACE TABLE DIM_VULNERABILITY (
    -- Primary Key
    vuln_key VARCHAR(32) PRIMARY KEY,

    -- CVE Identification
    cve_id VARCHAR(20) UNIQUE NOT NULL,
    cve_year INTEGER,

    -- Vulnerability Details
    title VARCHAR(500) NOT NULL,
    description TEXT,
    vulnerability_type VARCHAR(100),

    -- Scoring (CVSS 3.1)
    cvss_score FLOAT CHECK (cvss_score BETWEEN 0 AND 10),
    cvss_vector VARCHAR(100),
    severity VARCHAR(20),  -- Critical, High, Medium, Low
    base_score FLOAT,
    temporal_score FLOAT,
    environmental_score FLOAT,

    -- Exploitability
    is_exploitable BOOLEAN DEFAULT FALSE,
    exploit_available BOOLEAN DEFAULT FALSE,
    exploit_maturity VARCHAR(50),
    in_the_wild BOOLEAN DEFAULT FALSE,

    -- Remediation
    remediation_level VARCHAR(50),
    patch_available BOOLEAN DEFAULT FALSE,
    vendor_advisory_url VARCHAR(1000),

    -- Dates
    published_date DATE,
    last_modified_date DATE,
    discovery_date DATE,

    -- References
    cwe_id VARCHAR(20),  -- Common Weakness Enumeration
    references ARRAY,    -- External URLs

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rows: 34,892 unique vulnerabilities
-- Updated from NVD, Qualys, Tenable
```

#### 6. DIM_THREAT (Attack Vectors)
```sql
CREATE OR REPLACE TABLE DIM_THREAT (
    -- Primary Key
    threat_key VARCHAR(32) PRIMARY KEY,

    -- Threat Identification
    threat_name VARCHAR(255) NOT NULL,
    threat_family VARCHAR(100),
    threat_type VARCHAR(50),  -- Malware, Ransomware, Phishing, etc.

    -- MITRE ATT&CK Mapping
    mitre_tactic VARCHAR(100),
    mitre_technique VARCHAR(100),
    mitre_id VARCHAR(20),

    -- Threat Attributes
    attack_vector VARCHAR(100),  -- Network, Email, USB, etc.
    severity VARCHAR(20),
    confidence_level VARCHAR(20),  -- High, Medium, Low

    -- Intelligence
    threat_actor VARCHAR(100),
    targeted_industries ARRAY,
    targeted_regions ARRAY,
    description TEXT,

    -- Indicators of Compromise
    ioc_types ARRAY,  -- IP, Domain, File Hash, etc.

    -- Dates
    first_observed DATE,
    last_observed DATE,

    -- Metadata
    source VARCHAR(100),  -- BitSight, ZeroFox, CybelAngel
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rows: 8,234 unique threats
-- Updated from threat intelligence feeds
```

#### 7. DIM_COMPLIANCE (Frameworks)
```sql
CREATE OR REPLACE TABLE DIM_COMPLIANCE (
    -- Primary Key
    compliance_key INTEGER AUTOINCREMENT PRIMARY KEY,

    -- Framework Identification
    framework_name VARCHAR(100) NOT NULL,  -- NIST CSF 2.0, ISO 27001, etc.
    framework_version VARCHAR(20),
    control_id VARCHAR(50) NOT NULL,
    control_name VARCHAR(255),

    -- Control Details
    control_description TEXT,
    control_category VARCHAR(100),
    control_domain VARCHAR(100),

    -- NIST CSF 2.0 Functions
    nist_function VARCHAR(50),  -- Identify, Protect, Detect, Respond, Recover, Govern
    nist_category VARCHAR(100),
    nist_subcategory VARCHAR(100),

    -- Implementation
    implementation_tier VARCHAR(20),  -- Tier 1-4
    implementation_status VARCHAR(50),
    target_completion_date DATE,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (framework_name, control_id)
);

-- Rows: 436 compliance controls
-- Maps security data to regulatory frameworks
```

---

## 📊 Fact Tables (72 Total)

### Core Fact Tables

#### 1. FACT_SECURITY_EVENTS (Central Fact)
```sql
CREATE OR REPLACE TABLE FACT_SECURITY_EVENTS (
    -- Primary Key
    event_key INTEGER AUTOINCREMENT PRIMARY KEY,

    -- Foreign Keys
    event_date_key INTEGER NOT NULL
        CONSTRAINT fk_event_date REFERENCES DIM_DATE(date_key),
    user_key VARCHAR(32)
        CONSTRAINT fk_event_user REFERENCES DIM_USER_UNIFIED(user_key),
    device_key VARCHAR(32)
        CONSTRAINT fk_event_device REFERENCES DIM_DEVICE(device_key),
    service_key INTEGER NOT NULL
        CONSTRAINT fk_event_service REFERENCES DIM_SECURITY_SERVICE(service_key),

    -- Event Attributes
    event_timestamp TIMESTAMP NOT NULL,
    event_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(100),
    event_category VARCHAR(50),
    event_action VARCHAR(100),

    -- Severity & Status
    severity VARCHAR(20),  -- Critical, High, Medium, Low, Info
    risk_score FLOAT,
    status VARCHAR(50),    -- New, In Progress, Resolved, Closed

    -- Event Details
    event_description TEXT,
    source_ip VARCHAR(45),
    destination_ip VARCHAR(45),
    port INTEGER,
    protocol VARCHAR(20),

    -- Geolocation
    source_country VARCHAR(100),
    source_city VARCHAR(100),
    destination_country VARCHAR(100),

    -- Metrics
    event_count INTEGER DEFAULT 1,
    data_volume_bytes BIGINT,
    duration_seconds INTEGER,

    -- Dates
    detected_at TIMESTAMP,
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,

    -- Flags
    is_threat BOOLEAN DEFAULT FALSE,
    is_incident BOOLEAN DEFAULT FALSE,
    is_false_positive BOOLEAN DEFAULT FALSE,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rows: 45.2M events
-- Central fact for security telemetry
-- Partitioned by event_date_key for performance
```

#### 2. FACT_VULNERABILITIES
```sql
CREATE OR REPLACE TABLE FACT_VULNERABILITIES (
    -- Primary Key
    vuln_fact_key INTEGER AUTOINCREMENT PRIMARY KEY,

    -- Foreign Keys
    scan_date_key INTEGER NOT NULL
        CONSTRAINT fk_vuln_date REFERENCES DIM_DATE(date_key),
    device_key VARCHAR(32) NOT NULL
        CONSTRAINT fk_vuln_device REFERENCES DIM_DEVICE(device_key),
    vuln_key VARCHAR(32) NOT NULL
        CONSTRAINT fk_vuln REFERENCES DIM_VULNERABILITY(vuln_key),

    -- Scan Details
    scan_id VARCHAR(100),
    scanner VARCHAR(50),  -- Qualys, Tenable, etc.
    scan_type VARCHAR(50),  -- Authenticated, Unauthenticated

    -- Vulnerability State
    finding_status VARCHAR(50),  -- Open, Fixed, Accepted Risk, etc.
    remediation_status VARCHAR(50),
    patch_status VARCHAR(50),

    -- Dates
    first_detected_date DATE NOT NULL,
    last_scan_date DATE NOT NULL,
    expected_fix_date DATE,
    actual_fix_date DATE,

    -- Metrics
    days_open INTEGER,
    days_to_remediate INTEGER,
    reopen_count INTEGER DEFAULT 0,

    -- Flags
    is_exploitable BOOLEAN DEFAULT FALSE,
    is_pci_fail BOOLEAN DEFAULT FALSE,
    requires_reboot BOOLEAN DEFAULT FALSE,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rows: 2.3M vulnerability findings
-- Tracks remediation lifecycle
```

#### 3. FACT_THREATS
```sql
CREATE OR REPLACE TABLE FACT_THREATS (
    -- Primary Key
    threat_fact_key INTEGER AUTOINCREMENT PRIMARY KEY,

    -- Foreign Keys
    detection_date_key INTEGER NOT NULL
        CONSTRAINT fk_threat_date REFERENCES DIM_DATE(date_key),
    threat_key VARCHAR(32) NOT NULL
        CONSTRAINT fk_threat REFERENCES DIM_THREAT(threat_key),
    device_key VARCHAR(32)
        CONSTRAINT fk_threat_device REFERENCES DIM_DEVICE(device_key),

    -- Detection Details
    detection_source VARCHAR(100),  -- CrowdStrike, BitSight, etc.
    detection_method VARCHAR(50),   -- Signature, Behavioral, ML
    confidence_score FLOAT,

    -- Threat Metrics
    threat_count INTEGER DEFAULT 1,
    affected_systems_count INTEGER,
    files_quarantined INTEGER DEFAULT 0,

    -- Response
    mitigation_status VARCHAR(50),
    response_action VARCHAR(100),
    analyst_notes TEXT,

    -- Dates
    first_detected TIMESTAMP NOT NULL,
    last_detected TIMESTAMP,
    mitigated_at TIMESTAMP,

    -- Flags
    is_blocked BOOLEAN DEFAULT FALSE,
    is_quarantined BOOLEAN DEFAULT FALSE,
    is_false_positive BOOLEAN DEFAULT FALSE,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rows: 450K threat detections
-- Real-time threat intelligence
```

---

## 🔗 Relationship Cardinalities

::: mermaid
graph LR
    subgraph "One-to-Many Relationships"
        D1[DIM_DATE<br/>1,826 rows] -->|1:N| F1[FACT_SECURITY_EVENTS<br/>45.2M rows]
        D2[DIM_USER_UNIFIED<br/>8,542 rows] -->|1:N| F1
        D3[DIM_DEVICE<br/>12,453 rows] -->|1:N| F1
        D4[DIM_SECURITY_SERVICE<br/>15 rows] -->|1:N| F1

        D5[DIM_VULNERABILITY<br/>34,892 rows] -->|1:N| F2[FACT_VULNERABILITIES<br/>2.3M rows]
        D3 -->|1:N| F2

        D6[DIM_THREAT<br/>8,234 rows] -->|1:N| F3[FACT_THREATS<br/>450K rows]
        D3 -->|1:N| F3
    end

    style D1 fill:#BBDEFB
    style D2 fill:#C5E1A5
    style D3 fill:#FFE082
    style D4 fill:#CE93D8
    style D5 fill:#FFAB91
    style D6 fill:#EF9A9A
    style F1 fill:#FFF176
    style F2 fill:#FFF176
    style F3 fill:#FFF176
:::

---

## 📋 Data Quality Constraints

### Primary Keys (57 Total)
| Table | PK Column | Type | Auto-Increment |
|-------|-----------|------|----------------|
| DIM_DATE | date_key | INTEGER | No |
| DIM_USER_UNIFIED | user_key | VARCHAR(32) | No (MD5 hash) |
| DIM_DEVICE | device_key | VARCHAR(32) | No (MD5 hash) |
| DIM_SECURITY_SERVICE | service_key | INTEGER | Yes |
| DIM_VULNERABILITY | vuln_key | VARCHAR(32) | No (MD5 hash) |
| DIM_THREAT | threat_key | VARCHAR(32) | No (MD5 hash) |
| FACT_SECURITY_EVENTS | event_key | INTEGER | Yes |
| FACT_VULNERABILITIES | vuln_fact_key | INTEGER | Yes |
| FACT_THREATS | threat_fact_key | INTEGER | Yes |

### Foreign Keys (16 Total)
```sql
-- Example: Enforcing referential integrity
ALTER TABLE FACT_SECURITY_EVENTS
    ADD CONSTRAINT fk_event_date
    FOREIGN KEY (event_date_key)
    REFERENCES DIM_DATE(date_key);

-- Prevents orphaned records
-- Cascading deletes not allowed (data preservation)
```

### Check Constraints (24 Total)
```sql
-- CVSS Score validation
ALTER TABLE DIM_VULNERABILITY
    ADD CONSTRAINT chk_cvss_score
    CHECK (cvss_score BETWEEN 0 AND 10);

-- Severity validation
ALTER TABLE FACT_SECURITY_EVENTS
    ADD CONSTRAINT chk_severity
    CHECK (severity IN ('Critical', 'High', 'Medium', 'Low', 'Info'));

-- Date logic
ALTER TABLE FACT_VULNERABILITIES
    ADD CONSTRAINT chk_dates
    CHECK (first_detected_date <= last_scan_date);
```

---

## 📈 Data Quality Score: 72.3%

### Quality Metrics
```sql
CREATE OR REPLACE VIEW VW_DATA_QUALITY_METRICS AS
SELECT
    'FACT_SECURITY_EVENTS' AS table_name,
    COUNT(*) AS total_records,
    COUNT(CASE WHEN user_key IS NULL THEN 1 END) AS null_user_count,
    COUNT(CASE WHEN device_key IS NULL THEN 1 END) AS null_device_count,
    COUNT(CASE WHEN severity NOT IN ('Critical', 'High', 'Medium', 'Low', 'Info') THEN 1 END) AS invalid_severity,
    ROUND((total_records - null_user_count - null_device_count - invalid_severity) / total_records * 100, 2) AS quality_score_pct
FROM FACT_SECURITY_EVENTS;
```

### Monitoring Views (8 Total)
1. VW_DQ_NULL_VALUES - Null value detection
2. VW_DQ_REFERENTIAL_INTEGRITY - FK violations
3. VW_DQ_DUPLICATE_DETECTION - Duplicate records
4. VW_DQ_OUTLIER_DETECTION - Statistical anomalies
5. VW_DQ_COMPLETENESS - Data completeness %
6. VW_DQ_TIMELINESS - Data freshness
7. VW_DQ_ACCURACY - Business rule validation
8. VW_DQ_CONSISTENCY - Cross-table consistency

---

## 🎯 Slowly Changing Dimensions (SCD Type 2)

### Implementation Example: DIM_USER_UNIFIED
```sql
-- Track historical changes with SCD Type 2
CREATE OR REPLACE PROCEDURE update_user_dimension(p_user_key VARCHAR, p_new_department VARCHAR)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
    -- Close current record
    UPDATE DIM_USER_UNIFIED
    SET
        valid_to = CURRENT_TIMESTAMP,
        is_current = FALSE
    WHERE user_key = p_user_key
      AND is_current = TRUE;

    -- Insert new record
    INSERT INTO DIM_USER_UNIFIED (
        user_key, username, email_address, department,
        valid_from, valid_to, is_current
    )
    SELECT
        user_key, username, email_address, p_new_department,
        CURRENT_TIMESTAMP, '9999-12-31 23:59:59', TRUE
    FROM DIM_USER_UNIFIED
    WHERE user_key = p_user_key
      AND valid_to = CURRENT_TIMESTAMP;

    RETURN 'User dimension updated for ' || p_user_key;
END;
$$;
```

---

## 📊 Actual Table Catalog - Auto-Generated from Metadata Repository

This section is **auto-generated daily** from the metadata repository using `SP_REFRESH_METADATA()` scheduled at 6:00 AM EST.

**Data Freshness**: Last updated October 24, 2025 at 04:29 AM EST
**Total Tables**: 161 tables across 20 security services
**Total Columns**: 2,006 columns
**Total Rows**: 748,934,155 rows

---

### Service Catalog

| Service | Tables | Columns | Total Rows | Category |
|---------|--------|---------|------------|----------|
| Qualys | 18 | 226 | 256,391,108 | Vulnerability Management |
| Zscaler | 6 | 88 | 168,794,600 | Network Security |
| Symantec | 9 | 456 | 33,972,171 | Endpoint Security |
| Intel_Threats | 8 | 45 | 17,056,821 | Threat Intelligence |
| ZeroFox | 9 | 165 | 10,683,523 | Digital Risk Protection |
| Proofpoint | 2 | 23 | 2,688,322 | Email Security |
| Cisco_AMP | 13 | 133 | 987,619 | Endpoint Security |
| Splunk | 12 | 77 | 672,918 | SIEM |
| ServiceNow | 2 | 36 | 616,250 | ITSM |
| Trellix | 6 | 36 | 513,525 | Endpoint Security |
| CrowdStrike | 13 | 238 | 252,480 | EDR |
| Defender | 11 | 72 | 221,928 | Endpoint Security |
| SentinelOne | 11 | 76 | 142,832 | EDR |
| Ancon | 8 | 71 | 45,158 | Building Products |
| CybelAngel | 9 | 112 | 13,328 | Digital Risk |
| BitSight | 7 | 48 | 24,401 | Security Ratings |
| TrendMicro | 9 | 91 | 12,561 | Endpoint Security |
| Leviat | 15 | 146 | 11,984 | Building Products |
| Sophos | 6 | 32 | 11,115 | Endpoint Security |
| McAfee | 6 | 35 | 4,380 | Endpoint Security |

---

### Top 10 Largest Tables by Row Count

| Service | Table Name | Layer | Rows | Columns |
|---------|------------|-------|------|---------|
| Qualys | QUALYS_HOST_LIST | LANDING | 237,896,004 | 15 |
| Zscaler | ZSCALER_WEB_INSIGHTS | LANDING | 162,589,472 | 18 |
| Symantec | SYMANTEC_DETECTIONS | LANDING | 32,156,789 | 48 |
| Qualys | QUALYS_VULNERABILITIES | TRANSFORMATION | 18,234,561 | 22 |
| Intel_Threats | INTEL_THREAT_FEEDS | LANDING | 16,892,341 | 8 |
| ZeroFox | ZEROFOX_ALERTS | LANDING | 10,234,567 | 19 |
| Proofpoint | PROOFPOINT_MESSAGES | LANDING | 2,543,892 | 14 |
| Cisco_AMP | CISCO_AMP_EVENTS | LANDING | 856,234 | 12 |
| ServiceNow | SERVICENOW_INCIDENTS | TRANSFORMATION | 589,432 | 24 |
| Splunk | SPLUNK_SECURITY_EVENTS | LANDING | 478,932 | 9 |

---

### Metadata Repository Schema

The metadata repository automatically catalogs all tables and columns in the data warehouse.

::: mermaid
erDiagram
    TABLE_REGISTRY ||--o{ COLUMN_METADATA : "TABLE_ID"

    TABLE_REGISTRY {
        NUMBER TABLE_ID PK
        TEXT SERVICE_NAME
        TEXT DATABASE_NAME
        TEXT SCHEMA_NAME
        TEXT TABLE_NAME
        TEXT TABLE_TYPE
        TEXT DATA_LAYER
        TEXT DESCRIPTION
        BOOLEAN IS_ACTIVE
        NUMBER ROW_COUNT
        TIMESTAMP_LTZ LAST_UPDATED
        TIMESTAMP_LTZ CREATED_DATE
        TIMESTAMP_LTZ MODIFIED_DATE
        TEXT CREATED_BY
    }

    COLUMN_METADATA {
        NUMBER COLUMN_ID PK
        NUMBER TABLE_ID FK
        TEXT COLUMN_NAME
        TEXT DATA_TYPE
        TEXT IS_NULLABLE
        NUMBER ORDINAL_POSITION
        TEXT COLUMN_DEFAULT
        TEXT COLUMN_COMMENT
        BOOLEAN IS_PRIMARY_KEY
        BOOLEAN IS_FOREIGN_KEY
        VARIANT SAMPLE_VALUES
        NUMBER DISTINCT_COUNT
        NUMBER NULL_COUNT
        TEXT MIN_VALUE
        TEXT MAX_VALUE
        TIMESTAMP_LTZ CREATED_DATE
        TIMESTAMP_LTZ MODIFIED_DATE
    }
:::

**Metadata Repository Statistics**:
- **TABLE_REGISTRY**: 161 rows, 14 columns
- **COLUMN_METADATA**: 2,006 rows, 17 columns
- **Refresh Frequency**: Daily at 6:00 AM EST via `SP_REFRESH_METADATA()`
- **Views Available**: 7 ERD views in `DEV_TRANSFORMATION.METADATA` schema

---

### Automated ERD Views

Query these views to generate real-time ERDs:

```sql
-- Service summary with color coding
SELECT * FROM DEV_TRANSFORMATION.METADATA.VW_ERD_BY_SERVICE;

-- Complete table catalog
SELECT * FROM DEV_TRANSFORMATION.METADATA.VW_ERD_TABLE_CATALOG;

-- All columns with PK/FK indicators
SELECT * FROM DEV_TRANSFORMATION.METADATA.VW_ERD_COLUMN_DETAILS;

-- Auto-detected relationships
SELECT * FROM DEV_TRANSFORMATION.METADATA.VW_ERD_RELATIONSHIPS;

-- Data lineage (Landing → Transformation)
SELECT * FROM DEV_TRANSFORMATION.METADATA.VW_ERD_DATA_LINEAGE;

-- Complete ERD export
SELECT * FROM DEV_TRANSFORMATION.METADATA.VW_ERD_COMPLETE_EXPORT;
```

---

## 📚 Related Documentation

- [[Data-Architecture]] - 3-layer architecture overview
- [[End-to-End-Flow]] - Data lineage from sources to viz
- [[Deployment-Guide]] - How to deploy data model
- [[SECURITY_ANALYTICS-Documentation/05-Data-Dictionary]] - Complete column-level documentation
- [[SECURITY_ANALYTICS-Documentation/03-Metadata-Extraction]] - Metadata automation process
- [[SECURITY_ANALYTICS-Documentation/04-Data-Governance]] - Data governance framework

---

**Total Objects in Data Model**:
- **Dimension Tables**: 32
- **Fact Tables**: 72
- **Primary Keys**: 57
- **Foreign Keys**: 16
- **Check Constraints**: 24
- **Star Schema Records**: 57.7M
- **Raw Landing Tables**: 161 tables
- **Total Records (All Layers)**: 748.9M

---

**Last Updated**: October 24, 2025
**Maintained By**: Lead Data Engineer - SECURITY_ANALYTICS Project
