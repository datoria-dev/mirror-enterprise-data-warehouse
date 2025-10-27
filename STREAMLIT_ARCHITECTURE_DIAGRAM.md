# Streamlit Apps - Architecture & Data Flow Diagrams

**Last Updated**: 2025-10-25
**Total Apps**: 18 Streamlit applications
**Environment**: DEV_REPORTING.SECURITY_ANALYTICS

---

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Data Flow Diagram](#data-flow-diagram)
3. [App Categories](#app-categories)
4. [Technical Stack](#technical-stack)
5. [Deployment Architecture](#deployment-architecture)
6. [Integration Points](#integration-points)

---

## High-Level Architecture

```mermaid
graph TB
    subgraph "Data Sources"
        A1[Security Services APIs]
        A2[SIEM Logs]
        A3[Vulnerability Scanners]
        A4[ITSM Systems]
    end

    subgraph "Snowflake Data Warehouse"
        B1[DEV_LANDING<br/>Raw Data]
        B2[DEV_TRANSFORMATION<br/>Processed Data]
        B3[METADATA<br/>Data Catalog]
    end

    subgraph "Streamlit Apps - DEV_REPORTING.SECURITY_ANALYTICS"
        C1[Endpoint Security<br/>9 Apps]
        C2[Threat Intelligence<br/>4 Apps]
        C3[Vulnerability Mgmt<br/>2 Apps]
        C4[Operations<br/>3 Apps]
    end

    subgraph "Users"
        D1[Security Analysts]
        D2[IT Operations]
        D3[Management]
    end

    A1 --> B1
    A2 --> B1
    A3 --> B1
    A4 --> B1

    B1 --> B2
    B2 --> B3
    B2 --> C1
    B2 --> C2
    B2 --> C3
    B2 --> C4

    C1 --> D1
    C2 --> D1
    C3 --> D2
    C4 --> D1
    C1 --> D3
    C2 --> D3
    C3 --> D3
    C4 --> D3
```

---

## Data Flow Diagram

### Detailed Data Flow

```mermaid
flowchart LR
    subgraph "Layer 1: Data Ingestion"
        L1A[API Connectors]
        L1B[File Uploads]
        L1C[Snowpipe]
        L1D[Scheduled Tasks]
    end

    subgraph "Layer 2: Data Storage"
        L2A[(DEV_LANDING<br/>74 Tables)]
        L2B[(DEV_TRANSFORMATION<br/>106 Tables)]
        L2C[(METADATA<br/>6 Tables)]
    end

    subgraph "Layer 3: Data Processing"
        L3A[ETL Procedures<br/>15 SPs]
        L3B[Metadata Refresh<br/>SP_REFRESH_METADATA]
        L3C[Export Tables<br/>33 Exports]
    end

    subgraph "Layer 4: Streamlit Apps"
        L4A[Symantec]
        L4B[CrowdStrike]
        L4C[SentinelOne]
        L4D[Qualys]
        L4E[+ 14 More Apps]
    end

    subgraph "Layer 5: User Interface"
        L5A[Web Browser<br/>Snowflake UI]
        L5B[Mobile Device]
    end

    L1A --> L2A
    L1B --> L2A
    L1C --> L2A
    L1D --> L2A

    L2A --> L3A
    L3A --> L2B
    L2B --> L3B
    L3B --> L2C
    L2B --> L3C
    L2C --> L3C

    L3C --> L4A
    L3C --> L4B
    L3C --> L4C
    L3C --> L4D
    L3C --> L4E

    L4A --> L5A
    L4B --> L5A
    L4C --> L5A
    L4D --> L5A
    L4E --> L5A
    L4A --> L5B
    L4B --> L5B
```

---

## App Categories

### 1. Endpoint Security (9 Apps)

```mermaid
graph LR
    subgraph "Endpoint Security Apps"
        E1[Symantec<br/>Antivirus]
        E2[CrowdStrike<br/>EDR]
        E3[SentinelOne<br/>EDR]
        E4[Sophos<br/>Endpoint]
        E5[Trellix<br/>Analytics]
        E6[Cisco AMP<br/>Malware]
        E7[Defender<br/>Endpoint]
        E8[McAfee<br/>Antivirus]
        E9[Trend Micro<br/>Security]
    end

    subgraph "Data Sources"
        DS[(DEV_TRANSFORMATION<br/>Endpoint Tables)]
    end

    DS --> E1
    DS --> E2
    DS --> E3
    DS --> E4
    DS --> E5
    DS --> E6
    DS --> E7
    DS --> E8
    DS --> E9

    E1 --> U[Users]
    E2 --> U
    E3 --> U
    E4 --> U
    E5 --> U
    E6 --> U
    E7 --> U
    E8 --> U
    E9 --> U
```

### 2. Threat Intelligence (4 Apps)

```mermaid
graph LR
    subgraph "Threat Intelligence Apps"
        T1[CybelAngel<br/>Digital Risk]
        T2[ZeroFox<br/>Digital Risk]
        T3[Intel Threats<br/>Threat Intel]
        T4[BitSight<br/>Security Ratings]
    end

    subgraph "Data Sources"
        DS[(DEV_TRANSFORMATION<br/>Threat Tables)]
    end

    DS --> T1
    DS --> T2
    DS --> T3
    DS --> T4

    T1 --> U[Security Analysts]
    T2 --> U
    T3 --> U
    T4 --> U
```

### 3. Vulnerability Management (2 Apps)

```mermaid
graph LR
    subgraph "Vulnerability Mgmt Apps"
        V1[Qualys<br/>VM Scanner]
        V2[Tenable<br/>VM Platform]
    end

    subgraph "Data Sources"
        DS[(DEV_TRANSFORMATION<br/>Vulnerability Tables)]
    end

    DS --> V1
    DS --> V2

    V1 --> U[IT Operations]
    V2 --> U
```

### 4. Operations & SIEM (3 Apps)

```mermaid
graph LR
    subgraph "Operations Apps"
        O1[ServiceNow<br/>ITSM]
        O2[Leviat<br/>Asset Mgmt]
        O3[Ancon<br/>Monitoring]
    end

    subgraph "SIEM Apps"
        S1[Splunk<br/>Security Analytics]
    end

    subgraph "Cloud Security Apps"
        C1[Zscaler<br/>Cloud Gateway]
        C2[Proofpoint<br/>Email Security]
    end

    subgraph "Data Sources"
        DS[(DEV_TRANSFORMATION<br/>Operations Tables)]
    end

    DS --> O1
    DS --> O2
    DS --> O3
    DS --> S1
    DS --> C1
    DS --> C2

    O1 --> U[Users]
    O2 --> U
    O3 --> U
    S1 --> U
    C1 --> U
    C2 --> U
```

---

## Technical Stack

### App Components

```mermaid
graph TD
    subgraph "Streamlit App Structure"
        A[streamlit_app.py<br/>Main Application]
        B[environment.yml<br/>Dependencies]
    end

    subgraph "Python Libraries"
        C[streamlit<br/>Web Framework]
        D[snowflake-snowpark-python<br/>Database Access]
        E[pandas<br/>Data Manipulation]
        F[plotly<br/>Visualization]
    end

    subgraph "Snowflake Resources"
        G[Snowpark Session<br/>Connection]
        H[SQL Queries<br/>Data Retrieval]
        I[DEV_WH<br/>Warehouse]
    end

    A --> C
    A --> D
    A --> E
    A --> F

    D --> G
    G --> H
    H --> I

    I --> J[(DEV_REPORTING.SECURITY_ANALYTICS<br/>Tables & Views)]
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Streamlit | Web UI framework |
| **Backend** | Python 3.9+ | Application logic |
| **Database** | Snowflake | Data warehouse |
| **Connection** | Snowpark | Python-Snowflake integration |
| **Visualization** | Plotly | Interactive charts |
| **Data Processing** | Pandas | DataFrame operations |
| **Deployment** | SnowSQL | App deployment tool |
| **Authentication** | Okta SSO | Single sign-on |

---

## Deployment Architecture

### Deployment Flow

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Local as Local Files
    participant SnowSQL as SnowSQL CLI
    participant Stage as Snowflake Stage
    participant SF as Snowflake
    participant User as End User

    Dev->>Local: Edit streamlit_app.py
    Dev->>Local: Update environment.yml
    Dev->>SnowSQL: Run deploy script
    SnowSQL->>Stage: Upload files to @STREAMLIT_APPS_STAGE
    SnowSQL->>SF: CREATE STREAMLIT command
    SF->>Stage: Reference stage files
    SF->>SF: Create app in DEV_REPORTING.SECURITY_ANALYTICS
    User->>SF: Access via Snowflake UI
    SF->>User: Render Streamlit app
```

### Stage Structure

```mermaid
graph TB
    subgraph "Snowflake Stage"
        S[@STREAMLIT_APPS_STAGE]

        subgraph "App Folders"
            A1[Symantec/]
            A2[CrowdStrike/]
            A3[SentinelOne/]
            A4[Qualys/]
            A5[... 14 more]
        end

        subgraph "Files per App"
            F1[streamlit_app.py]
            F2[environment.yml]
        end
    end

    S --> A1
    S --> A2
    S --> A3
    S --> A4
    S --> A5

    A1 --> F1
    A1 --> F2
```

### Deployed Apps Location

```
DEV_REPORTING.SECURITY_ANALYTICS
├── STREAMLIT_SYMANTEC
├── STREAMLIT_CROWDSTRIKE
├── STREAMLIT_SENTINELONE
├── STREAMLIT_SOPHOS
├── STREAMLIT_QUALYS
├── STREAMLIT_SPLUNK
├── STREAMLIT_PROOFPOINT
├── STREAMLIT_CYBELANGEL
├── STREAMLIT_ZEROFOX
├── STREAMLIT_ZSCALER
├── STREAMLIT_CISCO_AMP
├── STREAMLIT_INTEL_THREATS
├── STREAMLIT_BITSIGHT
├── STREAMLIT_SERVICENOW
├── STREAMLIT_LEVIAT
├── STREAMLIT_ANCON
├── STREAMLIT_TENABLE
└── STREAMLIT_TRELLIX
```

---

## Integration Points

### Data Sources Integration

```mermaid
graph LR
    subgraph "External Systems"
        E1[CrowdStrike API]
        E2[Qualys API]
        E3[Splunk Forwarder]
        E4[ServiceNow API]
        E5[BitSight API]
        E6[+ 13 More APIs]
    end

    subgraph "Ingestion Layer"
        I1[Snowpipe<br/>Real-time]
        I2[Tasks<br/>Scheduled]
        I3[External Tables<br/>Batch]
    end

    subgraph "Storage Layer"
        S1[(DEV_LANDING)]
        S2[(DEV_TRANSFORMATION)]
    end

    subgraph "App Layer"
        A1[18 Streamlit Apps]
    end

    E1 --> I1
    E2 --> I2
    E3 --> I1
    E4 --> I2
    E5 --> I2
    E6 --> I3

    I1 --> S1
    I2 --> S1
    I3 --> S1

    S1 --> S2
    S2 --> A1
```

### Metadata Integration

```mermaid
graph TB
    subgraph "Metadata System"
        M1[SP_REFRESH_METADATA<br/>Daily at 6:00 AM]
        M2[(TABLE_REGISTRY<br/>180 Tables)]
        M3[(COLUMN_METADATA<br/>2,206 Columns)]
        M4[(33 Export Tables)]
    end

    subgraph "Apps with Metadata Tab"
        A1[SentinelOne]
        A2[CybelAngel]
        A3[Proofpoint]
        A4[ServiceNow]
        A5[Leviat]
        A6[Tenable]
    end

    M1 --> M2
    M1 --> M3
    M2 --> M4
    M3 --> M4

    M4 --> A1
    M4 --> A2
    M4 --> A3
    M4 --> A4
    M4 --> A5
    M4 --> A6
```

---

## App Features Matrix

### Common Features Across Apps

| Feature | Apps Count | Examples |
|---------|------------|----------|
| **Overview Dashboard** | 18/18 | All apps |
| **KPI Metrics** | 18/18 | All apps |
| **Data Tables** | 18/18 | All apps |
| **Filters (Date Range)** | 18/18 | All apps |
| **Filters (Categories)** | 16/18 | Most apps |
| **Download CSV** | 11/18 | Symantec, CrowdStrike, Leviat, etc. |
| **Alert Thresholds** | 8/18 | Symantec, CrowdStrike, Leviat, ServiceNow |
| **Metadata Tab** | 6/18 | SentinelOne, CybelAngel, Proofpoint, ServiceNow, Leviat, Tenable |
| **Multiple Charts** | 18/18 | All apps |
| **Refresh Button** | 18/18 | All apps |

### App-Specific Features

```mermaid
graph TB
    subgraph "Standard Features - All Apps"
        F1[Overview Dashboard]
        F2[KPI Metrics]
        F3[Data Tables]
        F4[Date Filters]
        F5[Charts & Graphs]
    end

    subgraph "Advanced Features - Some Apps"
        A1[CSV Download<br/>11 apps]
        A2[Alert Thresholds<br/>8 apps]
        A3[Metadata Tab<br/>6 apps]
        A4[Multiple Tabs<br/>16 apps]
    end

    F1 --> App[18 Apps]
    F2 --> App
    F3 --> App
    F4 --> App
    F5 --> App

    App --> A1
    App --> A2
    App --> A3
    App --> A4
```

---

## Performance Architecture

### Query Performance

```mermaid
graph LR
    subgraph "App Layer"
        A[Streamlit App]
    end

    subgraph "Snowflake Layer"
        S1[Snowpark Session]
        S2[Query Optimization]
        S3[Result Cache]
        S4[Virtual Warehouse<br/>DEV_WH]
    end

    subgraph "Data Layer"
        D1[(Views<br/>Optimized)]
        D2[(Tables<br/>Indexed)]
    end

    A --> S1
    S1 --> S2
    S2 --> S3
    S3 --> S4
    S4 --> D1
    S4 --> D2

    D1 --> R[Results]
    D2 --> R
    S3 --> R
```

### Caching Strategy

| Level | Type | Duration | Benefit |
|-------|------|----------|---------|
| **Browser** | Session cache | Session | Fast page navigation |
| **Streamlit** | st.cache_data | Until refresh | Avoid recomputation |
| **Snowflake** | Result cache | 24 hours | Instant repeated queries |
| **Warehouse** | Auto-suspend | 60 seconds | Cost optimization |

---

## Security Architecture

### Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Snowflake
    participant Okta
    participant App

    User->>Browser: Access Streamlit app URL
    Browser->>Snowflake: Request app
    Snowflake->>Okta: Redirect for SSO
    Okta->>User: Show login page
    User->>Okta: Enter credentials + MFA
    Okta->>Snowflake: Return SAML token
    Snowflake->>App: Create Snowpark session
    App->>User: Render application
```

### Access Control

```mermaid
graph TB
    subgraph "Authentication"
        A1[Okta SSO]
        A2[MFA Required]
    end

    subgraph "Authorization"
        B1[Snowflake Roles]
        B2[DEV_DEVELOPER<br/>Development]
        B3[DEV_ANALYST<br/>Read-only]
    end

    subgraph "Data Access"
        C1[Row-Level Security]
        C2[Column Masking]
        C3[View-Based Access]
    end

    subgraph "Streamlit Apps"
        D[18 Apps]
    end

    A1 --> B1
    A2 --> B1
    B1 --> B2
    B1 --> B3

    B2 --> C1
    B3 --> C1
    C1 --> C2
    C2 --> C3

    C3 --> D
```

---

## Monitoring & Maintenance

### Monitoring Architecture

```mermaid
graph TB
    subgraph "Monitoring Points"
        M1[App Availability]
        M2[Query Performance]
        M3[Error Logs]
        M4[Warehouse Usage]
        M5[User Activity]
    end

    subgraph "Data Collection"
        D1[Snowflake Query History]
        D2[Warehouse Metering]
        D3[Task Execution Log]
    end

    subgraph "Alerting"
        A1[Performance Alerts]
        A2[Error Alerts]
        A3[Usage Alerts]
    end

    M1 --> D1
    M2 --> D1
    M3 --> D1
    M4 --> D2
    M5 --> D1

    D1 --> A1
    D1 --> A2
    D2 --> A3
    D3 --> A2
```

---

## Future Enhancements

### Planned Architecture Improvements

```mermaid
graph LR
    subgraph "Current State"
        C1[18 Streamlit Apps]
        C2[Manual Deployment]
        C3[DEV Environment]
    end

    subgraph "Planned Improvements"
        P1[Power BI Integration]
        P2[CI/CD Pipeline]
        P3[PROD Environment]
        P4[Mobile Optimization]
        P5[Advanced Analytics]
    end

    C1 --> P1
    C2 --> P2
    C3 --> P3
    C1 --> P4
    C1 --> P5
```

---

## Summary Statistics

### Deployment Stats

| Metric | Value |
|--------|-------|
| Total Apps | 18 |
| Total Lines of Code | ~18,000 lines |
| Average App Size | ~1,000 lines |
| Deployment Time | ~2 minutes (all apps) |
| Stage Storage | ~2 MB |
| Supported Services | 20+ security services |

### Usage Stats

| Metric | Value |
|--------|-------|
| Database | DEV_REPORTING |
| Schema | SECURITY_ANALYTICS |
| Warehouse | DEV_WH (Medium) |
| Tables Accessed | 180 tables |
| Columns Used | 2,206 columns |
| Daily Queries | ~1,000 queries |

---

**Document Created**: 2025-10-25
**Status**: Production
**Maintained By**: Data Engineering Team
**Related Wikis**: WIKI_01, WIKI_08
