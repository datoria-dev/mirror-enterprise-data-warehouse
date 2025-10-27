# Wiki: Streamlit Apps - SECURITY_ANALYTICS Data Warehouse

## 📋 Table of Contents
- [Overview](#overview)
- [Available Applications](#available-applications)
- [Architecture](#architecture)
- [Features](#features)
- [Metadata Integration](#metadata-integration)
- [Deployment](#deployment)
- [User Guide](#user-guide)
- [Maintenance](#maintenance)

---

## Overview

### Purpose
The SECURITY_ANALYTICS Data Warehouse includes a suite of **Streamlit applications** that provide interactive dashboards for security data analysis and monitoring across 20+ security services.

### Key Statistics
- **Total Apps**: 20 applications
- **Services Covered**: 20 security services (Endpoint Protection, Threat Intelligence, SIEM, etc.)
- **Data Sources**: Snowflake Data Warehouse (DEV_LANDING, DEV_TRANSFORMATION schemas)
- **Authentication**: Snowflake SSO (Okta integration)
- **Technology Stack**: Python, Streamlit, Snowflake Snowpark, Plotly

---

## Available Applications

### Endpoint Protection (9 Apps)

| App | Service | Description | Data Layer | Status |
|-----|---------|-------------|------------|--------|
| 🛡️ **SentinelOne** | SentinelOne EDR | Endpoint Detection & Response monitoring | Transformation | ✅ Active |
| 🦅 **CrowdStrike** | CrowdStrike Falcon | EDR threat analysis and endpoint status | Transformation | ✅ Active |
| 🔒 **Symantec** | Symantec EP | Antivirus and endpoint protection | Transformation | ✅ Active |
| 🛡️ **McAfee** | McAfee | Endpoint security and threat protection | Transformation | ✅ Active |
| 🔐 **Sophos** | Sophos | Endpoint protection and EDR | Transformation | ✅ Active |
| 🦠 **TrendMicro** | Trend Micro | Threat protection and endpoint security | Transformation | ✅ Active |
| 🛡️ **Defender** | Microsoft Defender | Endpoint security | Transformation | ✅ Active |
| 🔥 **Trellix** | Trellix | EDR and threat detection | Transformation | ✅ Active |
| 🔒 **Cisco AMP** | Cisco AMP | Advanced malware protection | Transformation | ✅ Active |

### Vulnerability Management (2 Apps)

| App | Service | Description | Data Layer | Status |
|-----|---------|-------------|------------|--------|
| 🔍 **Qualys** | Qualys | Vulnerability scanning and assessment | Transformation | ✅ Active |
| 🎯 **Tenable** | Tenable | Vulnerability assessment | Transformation | ⚠️ No Data |

### Threat Intelligence (4 Apps)

| App | Service | Description | Data Layer | Status |
|-----|---------|-------------|------------|--------|
| 📊 **BitSight** | BitSight | Security posture rating | Transformation | ✅ Active |
| 🕵️ **CybelAngel** | CybelAngel | Cyber threat intelligence | Transformation | ✅ Active |
| 🦊 **ZeroFox** | ZeroFox | External threat monitoring | Transformation | ✅ Active |
| 🧠 **Intel_Threats** | Intel Threats | Aggregated threat intelligence | Transformation | ✅ Active |

### Identity & Access Management (2 Apps)

| App | Service | Description | Data Layer | Status |
|-----|---------|-------------|------------|--------|
| 👤 **Ancon** | Ancon | Identity and access management | Transformation | ✅ Active |
| 🔑 **Leviat** | Leviat | Privileged access monitoring | Transformation | ✅ Active |

### SIEM (1 App)

| App | Service | Description | Data Layer | Status |
|-----|---------|-------------|------------|--------|
| 📡 **Splunk** | Splunk | Security Information & Event Management | Transformation | ✅ Active |

### Cloud Security (1 App)

| App | Service | Description | Data Layer | Status |
|-----|---------|-------------|------------|--------|
| ☁️ **Zscaler** | Zscaler | Secure web gateway and cloud security | Transformation | ✅ Active |

### Email Security (1 App)

| App | Service | Description | Data Layer | Status |
|-----|---------|-------------|------------|--------|
| 📧 **Proofpoint** | Proofpoint | Email security and threat protection | Transformation | ✅ Active |

### Asset Management (1 App)

| App | Service | Description | Data Layer | Status |
|-----|---------|-------------|------------|--------|
| 🎫 **ServiceNow** | ServiceNow | IT Service Management & asset inventory | Transformation | ✅ Active |

---

## Architecture

### Complete Data Flow Architecture

:::mermaid
flowchart LR
    A[Security Services APIs<br/>20+ Sources] --> B[Data Ingestion<br/>S3/SFTP/APIs]
    B --> C[Snowflake Landing<br/>DEV_LANDING]
    C --> D[Transformation<br/>DEV_TRANSFORMATION]
    D --> E[Reporting<br/>DEV_REPORTING.SECURITY_ANALYTICS]
    E --> F[18 Streamlit Apps<br/>Stage-Based]
    F --> G[End Users<br/>SSO Authenticated]

    style A fill:#e1f5ff,stroke:#0078d4,stroke-width:2px
    style C fill:#fff4e6,stroke:#ff9800,stroke-width:2px
    style D fill:#e8f5e9,stroke:#4caf50,stroke-width:2px
    style E fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px
    style F fill:#fff3e0,stroke:#ff6f00,stroke-width:2px
    style G fill:#e0f2f1,stroke:#009688,stroke-width:2px
:::

### Technical Architecture - Streamlit Apps

:::mermaid
flowchart TD
    U[User Browser] -->|HTTPS + SSO| A[Streamlit App<br/>streamlit_app.py]
    A -->|Check Cache| C{Cache Hit?<br/>5 min TTL}
    C -->|Yes| A
    C -->|No| S[Snowpark<br/>Connection]
    S -->|SQL Query| W[DEV_WH<br/>Warehouse]
    W -->|Results| D[(SECURITY_ANALYTICS<br/>Schema)]
    D -->|Data| A
    A -->|Process| P[Pandas +<br/>DummyNumpy]
    P -->|Render| A
    A -->|Display| U

    style A fill:#fff3e0,stroke:#ff6f00,stroke-width:3px
    style C fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    style D fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px
    style W fill:#e8f5e9,stroke:#4caf50,stroke-width:2px
:::

### Data Flow Sequence (User Interaction)

:::mermaid
sequenceDiagram
    actor User
    participant App as Streamlit App
    participant Auth as Okta SSO
    participant DB as Snowflake DB

    User->>App: Access Dashboard
    App->>Auth: Authenticate
    Auth-->>App: Token
    App->>App: Check Cache (5 min)
    alt Cache Miss
        App->>DB: Query Data
        DB-->>App: Results
        App->>App: Cache Results
    end
    App-->>User: Display Dashboard
    User->>App: Apply Filters
    App->>App: Process Data
    App-->>User: Update View
:::

### Deployment Architecture

:::mermaid
flowchart LR
    A[Local Dev<br/>VS Code] -->|git push| B[Azure DevOps<br/>Repository]
    B -->|snowsql PUT| C[Snowflake Stage<br/>STREAMLIT_APPS_STAGE]
    C -->|CREATE STREAMLIT| D[Streamlit Objects<br/>18 Apps]
    D -->|GRANT USAGE| E[Roles<br/>DEV_DEVELOPER]
    E -->|Access| F[End Users<br/>SSO Auth]

    style A fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    style B fill:#e1f5ff,stroke:#0078d4,stroke-width:2px
    style C fill:#fff4e6,stroke:#ff9800,stroke-width:2px
    style D fill:#fff3e0,stroke:#ff6f00,stroke-width:2px
    style F fill:#e0f2f1,stroke:#009688,stroke-width:2px
:::

### Application Structure

```
13_STREAMLIT_COMPLETE/
├── Sophos/                        # Endpoint Protection Apps
│   ├── streamlit_app.py           # Main app (self-contained)
│   └── environment.yml            # Snowflake dependencies
├── CrowdStrike/
│   ├── streamlit_app.py
│   └── environment.yml
├── SentinelOne/
│   ├── streamlit_app.py
│   └── environment.yml
├── Trellix/
│   ├── streamlit_app.py
│   └── environment.yml
├── Qualys/                        # Vulnerability Management Apps
│   ├── streamlit_app.py
│   └── environment.yml
├── Tenable/
│   ├── streamlit_app.py
│   └── environment.yml
├── BitSight/                      # Threat Intelligence Apps
│   ├── streamlit_app.py
│   └── environment.yml
├── ZeroFox/
│   ├── streamlit_app.py
│   └── environment.yml
├── CybelAngel/
│   ├── streamlit_app.py
│   └── environment.yml
├── Intel_Threats/
│   ├── streamlit_app.py
│   └── environment.yml
├── Splunk/                        # SIEM Apps
│   ├── streamlit_app.py
│   └── environment.yml
├── Zscaler/                       # Cloud Security Apps
│   ├── streamlit_app.py
│   └── environment.yml
├── Proofpoint/                    # Email Security Apps
│   ├── streamlit_app.py
│   └── environment.yml
├── Ancon/                         # IAM Apps
│   ├── streamlit_app.py
│   └── environment.yml
├── Leviat/
│   ├── streamlit_app.py
│   └── environment.yml
├── ServiceNow/                    # Asset Management Apps
│   ├── streamlit_app.py
│   └── environment.yml
├── Symantec/                      # Additional Endpoint Apps
│   ├── streamlit_app.py
│   └── environment.yml
└── Cisco_AMP/
    ├── streamlit_app.py
    └── environment.yml

Note: Each streamlit_app.py is self-contained (includes all code)
      because Stage-based Streamlit apps cannot import local .py files
```

### Key Architecture Decisions

#### 1. Stage-Based Deployment
- **Decision**: Use Snowflake Stage storage for app files
- **Reason**: Native Snowflake integration, SSO support, no external hosting
- **Trade-off**: Cannot share code via imports (all code must be in streamlit_app.py)

#### 2. Self-Contained Apps
- **Decision**: Each app contains all code (no shared modules)
- **Reason**: Stage-based apps cannot import local .py files from Stage
- **Impact**: ~2,700 lines of duplicate code across 18 apps (_DummyNumpy, _DummyPlotly classes)
- **Documentation**: See STAGE_BASED_STREAMLIT_LIMITATIONS.md

#### 3. Dummy Library Classes
- **Decision**: Implement _DummyNumpy and _DummyPlotly replacement classes
- **Reason**: numpy and plotly not available in Snowflake Streamlit environment
- **Implementation**: Use Python stdlib (random, math) + pandas for data operations

#### 4. 5-Minute Caching
- **Decision**: Cache query results for 5 minutes
- **Reason**: Balance between data freshness and query performance
- **Implementation**: Streamlit @st.cache_data decorator

#### 5. Metadata Integration
- **Decision**: Add metadata browsing tab to apps
- **Reason**: Help users discover table/column names for custom queries
- **Data Source**: DEV_TRANSFORMATION.METADATA_EXPORTS schema

---

## Features

### Standard Features (All Apps)

#### 1. **Multi-Tab Interface**
Each app includes 4-5 tabs:
- **📊 Overview**: Key metrics and summary statistics
- **📋 Detailed Data**: Searchable, filterable data tables
- **📈 Trends**: Time-series analysis and visualizations
- **📚 Metadata**: Data catalog with table/column browser (NEW!)
- *Service-specific tabs*: Varies by app

#### 2. **Interactive Filters**
- **Time Period**: Last 7/30/90 days, custom ranges
- **Severity Levels**: Critical, High, Medium, Low
- **Service-Specific**: Versions, statuses, categories, etc.

#### 3. **Data Visualization**
- **Plotly Charts**: Interactive charts (bar, line, pie, area)
- **Metrics Cards**: KPI displays with trends
- **Data Tables**: Sortable, searchable tables
- **Drill-Down**: Click to explore details

#### 4. **Export Capabilities**
- **CSV Export**: Download filtered data
- **Metadata Export**: Download complete data catalogs
- **Search Results**: Export filtered search results

#### 5. **Real-Time Data**
- **5-Minute Cache**: Fresh data every 5 minutes
- **Data Freshness Indicator**: Last update timestamp
- **Refresh Button**: Manual refresh option

### NEW: Metadata Integration

#### Metadata Tab Features (6 Apps)
Apps with integrated metadata browsing:
- ✅ SentinelOne (76 columns)
- ✅ CybelAngel (112 columns)
- ✅ Proofpoint (23 columns)
- ✅ ServiceNow (36 columns)
- ✅ Leviat (146 columns)
- ✅ Tenable (0 columns - no data)

**Capabilities**:
1. **Table Browser**: View all tables for the service
2. **Column Explorer**: See column names, data types, nullable status
3. **Column Search**: Find columns by name across all tables
4. **Copy Table Names**: Full qualified table names for queries
5. **Export Metadata**: Download complete metadata catalogs

**Data Source**: `DEV_TRANSFORMATION.METADATA_EXPORTS` schema

---

## Deployment

### Prerequisites
- Snowflake account with SSO (Okta) configured
- Python 3.8+
- Streamlit
- Snowflake Snowpark

### Installation

```bash
# 1. Clone repository
git clone <azure-devops-repo>
cd 07_STREAMLIT_APPS

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure Snowflake connection
# Edit snowflake_config.json with your credentials

# 4. Run app locally
streamlit run SentinelOne/streamlit_app.py

# 5. Deploy to Snowflake (Streamlit in Snowflake)
# Upload apps via Snowflake UI or CLI
```

### Snowflake Deployment

```sql
-- Create Streamlit app in Snowflake
CREATE STREAMLIT DEV_TRANSFORMATION.SECURITY_ANALYTICS.SENTINELONE_DASHBOARD
  FROM '07_STREAMLIT_APPS/SentinelOne'
  MAIN_FILE = 'streamlit_app.py'
  QUERY_WAREHOUSE = DEV_WH;

-- Grant access
GRANT USAGE ON STREAMLIT SENTINELONE_DASHBOARD TO ROLE DEV_USER;
```

---

## User Guide

### Accessing Apps

1. **Via Snowflake UI**:
   - Log in to Snowflake
   - Navigate to Apps > Streamlit
   - Select desired dashboard

2. **Via Direct URL** (if published):
   - `https://<your-org>.snowflakecomputing.com/apps/<app-name>`

### Using the Apps

#### Example: SentinelOne Dashboard

**Step 1: Select Time Period**
```
Sidebar > Time Period: Last 7 Days
```

**Step 2: Filter by Severity**
```
Sidebar > Threat Severity: Critical, High
```

**Step 3: View Overview**
```
Tab: Overview
- Total Threats: 1,234
- Active Endpoints: 5,678
- Critical Threats: 45
- Agent Compliance: 92.3%
```

**Step 4: Analyze Trends**
```
Tab: Trends
- Daily threat detections chart
- Mitigation actions over time
```

**Step 5: Export Data**
```
Tab: Detailed Data
- Filter/search as needed
- Click "Download CSV"
```

**Step 6: Browse Metadata** (NEW!)
```
Tab: Metadata
- Select table: FACT_SENTINEL_ENDPOINTS
- View 12 columns with data types
- Search for "endpoint" columns
- Export metadata catalog
```

### Common Tasks

#### Task 1: Find Critical Threats
```
1. Open relevant app (e.g., CrowdStrike)
2. Set Time Period: Last 30 Days
3. Filter: Severity = Critical
4. Tab: Detailed Data
5. Review threat list
6. Export to CSV for review
```

#### Task 2: Check Endpoint Compliance
```
1. Open endpoint protection app
2. Tab: Endpoint Status
3. Review agent version distribution
4. Identify outdated endpoints
5. Export non-compliant list
```

#### Task 3: Find Column Names for Queries
```
1. Open app with metadata tab
2. Tab: Metadata
3. Search: "threat" OR browse tables
4. Copy full table name
5. Use in custom SQL queries
```

---

## Maintenance

### Regular Tasks

#### Daily
- ✅ Monitor app performance
- ✅ Check data freshness
- ✅ Review user feedback

#### Weekly
- ✅ Verify all apps are accessible
- ✅ Check for Streamlit updates
- ✅ Review usage metrics

#### Monthly
- ✅ Update dependencies
- ✅ Review and optimize queries
- ✅ Add new features based on feedback

### Troubleshooting

#### Issue 1: App Won't Load
**Solution**:
```
1. Check Snowflake connection
2. Verify SSO authentication
3. Check warehouse is running
4. Review app logs
```

#### Issue 2: Data Not Showing
**Solution**:
```
1. Verify underlying tables exist
2. Check data refresh jobs ran
3. Review table permissions
4. Check filter settings
```

#### Issue 3: Metadata Tab Empty
**Solution**:
```
1. Run EXPORT_METADATA_RESULTS.sql
2. Verify METADATA_EXPORTS table exists
3. Check metadata refresh job
4. Refresh browser
```

### Updating Apps

```bash
# 1. Update code locally
git pull origin main

# 2. Test locally
streamlit run <app>/streamlit_app.py

# 3. Deploy to Snowflake
# Re-upload via Snowflake UI

# 4. Verify deployment
# Access app in Snowflake
```

---

## Performance Optimization

### Best Practices

1. **Query Optimization**
   - Use materialized views for complex queries
   - Add WHERE clauses to limit data
   - Use appropriate indexes

2. **Caching**
   - Enable Streamlit caching (@st.cache_data)
   - Set appropriate cache TTL (5 minutes)
   - Cache expensive computations

3. **Data Loading**
   - Load only necessary columns
   - Use LIMIT for preview queries
   - Implement pagination for large datasets

4. **Warehouse Management**
   - Use appropriate warehouse size
   - Auto-suspend when idle
   - Monitor warehouse usage

---

## Future Enhancements

### Planned Features

1. **Enhanced Metadata**
   - Column descriptions
   - Sample data preview
   - Data lineage visualization

2. **Advanced Analytics**
   - Predictive threat modeling
   - Anomaly detection
   - Correlation analysis

3. **Collaboration**
   - Shared filters/bookmarks
   - Annotations on charts
   - Report scheduling

4. **Integration**
   - Power BI integration
   - Slack notifications
   - Email alerts

---

## Support

### Resources
- **Documentation**: See project README files
- **Training**: Internal Streamlit workshop sessions
- **Support Email**: data-engineering@GenericCorp.com

### Feedback
Please submit feedback and feature requests via:
- Azure DevOps work items
- Email to data engineering team
- Internal Slack channel: #data-engineering

---

## Appendix

### App-Specific Details

#### SentinelOne Dashboard
- **Tables Used**: FACT_SENTINEL_ENDPOINTS, DIM_SENTINEL_VERSIONS
- **Key Metrics**: Threats, Endpoints, Agent Compliance
- **Special Features**: Mitigation action tracking

#### Qualys Dashboard
- **Tables Used**: FACT_QUALYS_VULNERABILITIES, DIM_QUALYS_ASSETS
- **Key Metrics**: Vulnerabilities, Assets, Risk Scores
- **Special Features**: Vulnerability aging analysis

#### CrowdStrike Dashboard
- **Tables Used**: FACT_CROWDSTRIKE_DETECTIONS
- **Key Metrics**: Detections, Endpoints, Incident Response
- **Special Features**: Real-time detection feed

*See individual app documentation for complete details*

---

**Wiki Version**: 1.0
**Last Updated**: 2025-10-24
**Author**: GenericCorp Data Engineering Team
**Project**: SECURITY_ANALYTICS Data Warehouse
