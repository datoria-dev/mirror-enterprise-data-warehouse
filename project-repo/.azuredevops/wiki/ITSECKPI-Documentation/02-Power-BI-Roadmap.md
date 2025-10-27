# Wiki: Power BI Implementation - SECURITY_ANALYTICS Data Warehouse

## 📋 Table of Contents
- [Overview](#overview)
- [Current Status](#current-status)
- [Planned Architecture](#planned-architecture)
- [Implementation Roadmap](#implementation-roadmap)
- [Data Model Design](#data-model-design)
- [Report Templates](#report-templates)
- [Security & Access](#security--access)
- [Best Practices](#best-practices)

---

## Overview

### Purpose
This wiki documents the **planned Power BI implementation** for the SECURITY_ANALYTICS Data Warehouse project. Power BI will provide enterprise-level reporting and dashboarding capabilities complementing the existing Streamlit applications.

### Vision
Create a comprehensive Power BI reporting solution that:
- Provides executive-level dashboards
- Enables self-service analytics
- Supports regulatory compliance reporting
- Integrates seamlessly with Snowflake
- Complements Streamlit apps with enterprise features

### Timeline
**Status**: 🟡 **Planned - Not Yet Implemented**
**Target Start**: Q1 2025
**Expected Completion**: Q2 2025

---

## Current Status

### ✅ Completed Prerequisites

1. **Data Warehouse Foundation**
   - ✅ Snowflake Data Warehouse implemented
   - ✅ 180 tables across 20+ security services
   - ✅ Data models (FACT/DIM) created
   - ✅ Metadata Repository operational
   - ✅ Data quality checks in place

2. **Metadata Infrastructure**
   - ✅ TABLE_REGISTRY with 180 tables
   - ✅ COLUMN_METADATA with 2,206 columns
   - ✅ SERVICE_CATALOG with 21 services
   - ✅ Automated metadata refresh

3. **Data Transformation**
   - ✅ Landing layer (raw data)
   - ✅ Transformation layer (dimensional models)
   - ✅ Views for reporting

### ⏳ Pending Items

1. **Power BI Infrastructure**
   - ⏳ Power BI Pro/Premium licenses
   - ⏳ Power BI Gateway setup
   - ⏳ Snowflake connector configuration
   - ⏳ Service accounts creation

2. **Development Environment**
   - ⏳ Power BI Desktop installation
   - ⏳ Development workspace creation
   - ⏳ Version control setup (PBIX files)

3. **Data Access**
   - ⏳ Snowflake reader role creation
   - ⏳ Connection string configuration
   - ⏳ SSO integration (if applicable)

---

## Planned Architecture

### Integration Architecture

```
┌────────────────────────────────────────────────────┐
│              Power BI Service                      │
│  (Enterprise Dashboards & Reports)                 │
└────────────┬───────────────────────────────────────┘
             │
             │ DirectQuery / Import Mode
             │
       ┌─────▼──────┐
       │  PBI Gateway │
       │  (On-premise)│
       └─────┬────────┘
             │
             │ Snowflake ODBC/JDBC
             ▼
┌────────────────────────────────────────────────────┐
│         Snowflake Data Warehouse                   │
├────────────────────────────────────────────────────┤
│  • REPORTING Views (optimized for PBI)             │
│  • DEV_TRANSFORMATION (dimensional models)         │
│  • Aggregated tables for performance               │
└────────────────────────────────────────────────────┘
```

### Connection Options

#### Option 1: DirectQuery (Recommended for Large Datasets)
**Pros**:
- Always real-time data
- No data storage in Power BI
- Leverages Snowflake compute power

**Cons**:
- Requires active connection
- Performance depends on Snowflake
- Limited DAX capabilities

#### Option 2: Import Mode (Recommended for Small Aggregated Data)
**Pros**:
- Fast dashboard performance
- No runtime Snowflake costs
- Full DAX capabilities

**Cons**:
- Scheduled refresh needed
- Data freshness depends on refresh
- Storage in Power BI

#### Option 3: Hybrid (Composite Models)
**Recommended Approach**:
- Import: Dimensional tables (DIM_*)
- DirectQuery: Fact tables (FACT_*)
- Best of both worlds

---

## Implementation Roadmap

### Phase 1: Foundation (Month 1)

#### Week 1-2: Setup & Configuration
- [ ] Procure Power BI licenses
- [ ] Install Power BI Gateway
- [ ] Configure Snowflake connector
- [ ] Create service accounts
- [ ] Set up development workspace

#### Week 3-4: Data Model Development
- [ ] Create semantic model (data model)
- [ ] Define relationships
- [ ] Create calculated columns/measures
- [ ] Optimize for performance
- [ ] Test connections

**Deliverables**:
- ✅ Power BI workspace created
- ✅ Snowflake connection established
- ✅ Base semantic model

---

### Phase 2: Core Dashboards (Month 2-3)

#### Executive Dashboard
**Purpose**: High-level security posture overview

**Metrics**:
- Total threats detected (all services)
- Vulnerability count by severity
- Endpoint compliance rates
- Incident response times
- Service availability

**Visualizations**:
- KPI cards
- Trend charts
- Heatmaps
- Service status indicators

**Data Sources**:
- VW_SERVICE_SUMMARY
- All FACT tables (aggregated)
- PROCEDURE_EXECUTION_LOG

---

#### Service-Level Dashboards (20 Dashboards)

**Template Structure**:
1. **Page 1: Overview**
   - Service health
   - Key metrics
   - Alerts summary

2. **Page 2: Detailed Analysis**
   - Drill-down tables
   - Filters (date, severity, etc.)
   - Detailed charts

3. **Page 3: Trends**
   - Time-series analysis
   - Historical comparisons
   - Forecasting (optional)

**Services** (20 dashboards planned):
- Endpoint Protection: CrowdStrike, SentinelOne, Symantec, etc. (9 dashboards)
- Vulnerability Management: Qualys, Tenable (2 dashboards)
- Threat Intelligence: BitSight, CybelAngel, ZeroFox, Intel_Threats (4 dashboards)
- Identity & Access: Ancon, Leviat (2 dashboards)
- SIEM: Splunk (1 dashboard)
- Cloud Security: Zscaler (1 dashboard)
- Email Security: Proofpoint (1 dashboard)
- Asset Management: ServiceNow (1 dashboard)

---

#### Compliance & Reporting Dashboard
**Purpose**: Regulatory compliance tracking

**Reports**:
- Vulnerability aging report
- Patch compliance
- Endpoint protection coverage
- Access review tracking
- Incident response SLAs

**Export Formats**:
- PDF (scheduled)
- Excel (ad-hoc)
- PowerPoint (executive summary)

---

### Phase 3: Advanced Features (Month 4-5)

#### Features to Implement

1. **Row-Level Security (RLS)**
   - User-based data filtering
   - Department/region restrictions
   - Service-based access control

2. **Data Alerts**
   - Critical threat detection
   - SLA breach notifications
   - Compliance violations
   - Email/Teams notifications

3. **Mobile Optimization**
   - Mobile layouts
   - Touch-friendly interactions
   - Phone app deployment

4. **Integration**
   - Embed in SharePoint
   - Teams integration
   - Email subscriptions
   - Export automation

---

### Phase 4: Optimization & Rollout (Month 6)

#### Performance Optimization
- [ ] Query optimization
- [ ] Aggregation tables
- [ ] Incremental refresh
- [ ] Caching strategies

#### User Training
- [ ] Power BI basic training
- [ ] Dashboard navigation
- [ ] Self-service analytics
- [ ] Best practices

#### Rollout Plan
- [ ] Pilot group (IT Security team)
- [ ] Gather feedback
- [ ] Iterate on dashboards
- [ ] Organization-wide rollout

**Deliverables**:
- ✅ Production-ready dashboards
- ✅ User documentation
- ✅ Training materials
- ✅ Support processes

---

## Data Model Design

### Planned Star Schema

```
           DIM_DATE
               │
               │
        ┌──────┴──────┐
        │             │
   FACT_THREATS   FACT_VULNERABILITIES
        │             │
        ├─────────────┤
        │             │
   DIM_SERVICE   DIM_SEVERITY
        │             │
   DIM_ENDPOINT  DIM_ASSET
```

### Core Tables

#### Fact Tables
```sql
-- Consolidated Threats (from all EDR services)
CREATE OR REPLACE VIEW VW_PBI_FACT_THREATS AS
SELECT
    THREAT_ID,
    DATE_KEY,
    SERVICE_KEY,
    ENDPOINT_KEY,
    THREAT_TYPE,
    SEVERITY,
    STATUS,
    DETECTED_TIMESTAMP,
    RESOLVED_TIMESTAMP,
    RESPONSE_TIME_MINUTES
FROM FACT_CROWDSTRIKE_THREATS
UNION ALL
SELECT ... FROM FACT_SENTINELONE_THREATS
UNION ALL
... -- All threat sources
;

-- Consolidated Vulnerabilities
CREATE OR REPLACE VIEW VW_PBI_FACT_VULNERABILITIES AS
SELECT
    VULN_ID,
    DATE_KEY,
    ASSET_KEY,
    CVE_ID,
    SEVERITY,
    CVSS_SCORE,
    DISCOVERED_DATE,
    REMEDIATION_DATE,
    AGE_DAYS
FROM FACT_QUALYS_VULNERABILITIES
UNION ALL
... -- All vuln sources
;
```

#### Dimension Tables
```sql
-- Date Dimension
CREATE TABLE DIM_DATE (
    DATE_KEY NUMBER PRIMARY KEY,
    FULL_DATE DATE,
    YEAR NUMBER,
    QUARTER NUMBER,
    MONTH NUMBER,
    MONTH_NAME VARCHAR(20),
    WEEK_OF_YEAR NUMBER,
    DAY_OF_MONTH NUMBER,
    DAY_OF_WEEK NUMBER,
    DAY_NAME VARCHAR(20),
    IS_WEEKEND BOOLEAN,
    IS_HOLIDAY BOOLEAN,
    FISCAL_YEAR NUMBER,
    FISCAL_QUARTER NUMBER
);

-- Service Dimension
CREATE TABLE DIM_SERVICE (
    SERVICE_KEY NUMBER PRIMARY KEY,
    SERVICE_NAME VARCHAR(100),
    SERVICE_CATEGORY VARCHAR(100),
    SERVICE_DESCRIPTION TEXT,
    VENDOR VARCHAR(100),
    IS_ACTIVE BOOLEAN
);

-- Severity Dimension
CREATE TABLE DIM_SEVERITY (
    SEVERITY_KEY NUMBER PRIMARY KEY,
    SEVERITY_NAME VARCHAR(20),
    SEVERITY_LEVEL NUMBER,
    SEVERITY_COLOR VARCHAR(20),
    REQUIRES_IMMEDIATE_ACTION BOOLEAN
);
```

### Measures (DAX)

```dax
// Total Threats
Total Threats = COUNT(FACT_THREATS[THREAT_ID])

// Critical Threats
Critical Threats =
CALCULATE(
    [Total Threats],
    DIM_SEVERITY[SEVERITY_NAME] = "Critical"
)

// Average Response Time
Avg Response Time =
AVERAGE(FACT_THREATS[RESPONSE_TIME_MINUTES])

// Threat Trend
Threat Trend =
VAR CurrentPeriodThreats = [Total Threats]
VAR PreviousPeriodThreats =
    CALCULATE(
        [Total Threats],
        DATEADD(DIM_DATE[FULL_DATE], -1, MONTH)
    )
RETURN
    DIVIDE(
        CurrentPeriodThreats - PreviousPeriodThreats,
        PreviousPeriodThreats
    )

// Vulnerability Aging
Avg Vuln Age =
AVERAGE(FACT_VULNERABILITIES[AGE_DAYS])

// Compliance Rate
Endpoint Compliance % =
DIVIDE(
    CALCULATE(
        COUNT(DIM_ENDPOINT[ENDPOINT_ID]),
        DIM_ENDPOINT[IS_COMPLIANT] = TRUE
    ),
    COUNT(DIM_ENDPOINT[ENDPOINT_ID])
)
```

---

## Report Templates

### Template 1: Executive Summary

**Layout**:
```
┌─────────────────────────────────────────────────┐
│  SECURITY_ANALYTICS Security Posture - Executive Summary  │
├──────────┬──────────┬──────────┬───────────────┤
│  Total   │ Critical │ High     │ Medium        │
│ Threats  │ Threats  │ Threats  │ Threats       │
│  1,234   │   45     │   234    │   567         │
├──────────┴──────────┴──────────┴───────────────┤
│                                                 │
│  [Line Chart: Threat Trend (Last 90 Days)]     │
│                                                 │
├─────────────────────┬───────────────────────────┤
│ [Bar Chart:         │ [Donut Chart:            │
│  Threats by Service]│  Threat Status]          │
│                     │                           │
├─────────────────────┴───────────────────────────┤
│  [Table: Top 10 Critical Threats]              │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Filters**:
- Date Range (slicer)
- Service Category (dropdown)
- Severity (checkbox)

---

### Template 2: Service Deep-Dive

**Example: CrowdStrike Dashboard**

```
┌─────────────────────────────────────────────────┐
│         CrowdStrike Threat Analysis             │
├──────────┬──────────┬──────────┬───────────────┤
│  Total   │ Endpoints│ Avg      │ Compliance    │
│Detections│ Protected│ Response │  Rate         │
│  1,234   │  5,678   │  2.5 hrs │  92.3%        │
├──────────┴──────────┴──────────┴───────────────┤
│  [Map: Detections by Geography]                │
│                                                 │
├────────────────────────────────────────────────┤
│  [Stacked Bar: Detections by Type & Severity] │
│                                                 │
├─────────────────────┬───────────────────────────┤
│ [Line: Daily        │ [Table: Recent           │
│  Detection Trend]   │  Detections]             │
│                     │                           │
└─────────────────────┴───────────────────────────┘
```

**Drill-Through**:
- Click endpoint → Endpoint detail page
- Click detection → Detection timeline
- Click threat type → Similar threats

---

### Template 3: Compliance Report

```
┌─────────────────────────────────────────────────┐
│      Vulnerability & Compliance Dashboard       │
├──────────┬──────────┬──────────┬───────────────┤
│  Open    │ Overdue  │ Avg Age  │ Patch         │
│  Vulns   │ Vulns    │ (Days)   │ Compliance    │
│  2,345   │   234    │   45     │  87.5%        │
├──────────┴──────────┴──────────┴───────────────┤
│  [Waterfall Chart: Vuln Aging by Severity]     │
│                                                 │
├────────────────────────────────────────────────┤
│  [Matrix: Vulnerability Count by Service/Sev] │
│                                                 │
├─────────────────────┬───────────────────────────┤
│ [Gantt: SLA         │ [Table: Overdue          │
│  Compliance]        │  Vulnerabilities]        │
│                     │                           │
└─────────────────────┴───────────────────────────┘
```

**Scheduled Exports**:
- Daily: Critical vulnerabilities (PDF to security team)
- Weekly: Compliance summary (PDF to management)
- Monthly: Full report (Excel to compliance team)

---

## Security & Access

### Row-Level Security (RLS)

```dax
// Example RLS Rule: User sees only their region
[Region] = USERPRINCIPALNAME()

// Example: User sees only their managed services
[Service_Owner] = LOOKUPVALUE(
    DIM_USER[Service_Owner],
    DIM_USER[Email],
    USERPRINCIPALNAME()
)
```

### Access Roles

| Role | Access Level | Permissions |
|------|--------------|-------------|
| **Executive** | Read-only | All dashboards, export to PDF/PPT |
| **Security Analyst** | Read-only | Service dashboards, export to Excel |
| **Service Owner** | Read-only | Own service(s) only, filtered by RLS |
| **Data Engineer** | Edit | All dashboards, can modify |
| **Admin** | Full | Workspace management, permissions |

### Workspace Security

```
Power BI Workspace: ITSECKPI_Reporting
├── Admins: Data Engineering Team
├── Members: Security Leadership
├── Contributors: Security Analysts
└── Viewers: All authenticated users
```

---

## Best Practices

### Performance

1. **Use Aggregation Tables**
   ```sql
   CREATE TABLE AGG_DAILY_THREATS AS
   SELECT
       DATE_TRUNC('day', DETECTED_TIMESTAMP) as DATE,
       SERVICE_NAME,
       SEVERITY,
       COUNT(*) as THREAT_COUNT
   FROM FACT_THREATS
   GROUP BY 1, 2, 3;
   ```

2. **Optimize DirectQuery**
   - Add indexes on join columns
   - Use query folding where possible
   - Avoid complex DAX on DirectQuery tables

3. **Implement Incremental Refresh**
   - Import last 6 months
   - DirectQuery for older data
   - Refresh daily

### Design

1. **Consistent Color Palette**
   - Critical: Red (#e74c3c)
   - High: Orange (#e67e22)
   - Medium: Yellow (#f39c12)
   - Low: Blue (#3498db)
   - Info: Gray (#95a5a6)

2. **Standard Layouts**
   - KPIs at top
   - Charts in middle
   - Tables at bottom
   - Filters on left sidebar

3. **Naming Conventions**
   - Dashboards: `SECURITY_ANALYTICS - [Service Name]`
   - Datasets: `DS_ITSECKPI_[Source]`
   - Reports: `RPT_[Category]_[Description]`

### Documentation

1. **Dashboard Metadata**
   - Purpose and audience
   - Data sources
   - Refresh schedule
   - Owner contact

2. **Measure Definitions**
   - Business logic
   - Formula documentation
   - Example calculations

3. **User Guides**
   - Navigation instructions
   - Filter usage
   - Export procedures

---

## Integration with Streamlit

### Complementary Capabilities

| Capability | Streamlit | Power BI |
|------------|-----------|----------|
| **Real-time data** | ✅ Excellent | ⚠️ Depends on refresh |
| **Interactive exploration** | ✅ Very flexible | ✅ Good with slicers |
| **Custom Python analysis** | ✅ Full control | ❌ Limited |
| **Enterprise distribution** | ⚠️ Requires hosting | ✅ Native cloud |
| **Mobile experience** | ⚠️ Basic | ✅ Excellent |
| **Scheduled reports** | ❌ Manual | ✅ Built-in |
| **Governance** | ⚠️ Manual | ✅ Built-in RLS |

### Recommended Usage

**Use Streamlit for**:
- Operational dashboards
- Ad-hoc analysis
- Custom data apps
- Real-time monitoring

**Use Power BI for**:
- Executive reporting
- Scheduled reports
- Mobile access
- Organization-wide distribution
- Compliance reporting

---

## Next Steps

### Immediate Actions (Before Implementation)

1. **Budget Approval**
   - [ ] Power BI licenses (Pro/Premium)
   - [ ] Gateway infrastructure
   - [ ] Training budget

2. **Technical Preparation**
   - [ ] Create reporting views in Snowflake
   - [ ] Set up aggregation tables
   - [ ] Optimize query performance
   - [ ] Document data model

3. **Stakeholder Alignment**
   - [ ] Identify report requirements
   - [ ] Define KPIs
   - [ ] Establish refresh schedules
   - [ ] Plan rollout

### Implementation Kickoff Checklist

- [ ] Licenses procured
- [ ] Development environment ready
- [ ] Snowflake connection tested
- [ ] Initial data model created
- [ ] Project plan approved
- [ ] Team assigned

---

## Support & Resources

### Internal Resources
- **Project Lead**: Data Engineering Manager
- **Power BI SME**: (To be assigned)
- **Snowflake Support**: Data Engineering Team

### External Resources
- [Power BI Documentation](https://docs.microsoft.com/power-bi/)
- [Snowflake Power BI Connector](https://docs.snowflake.com/en/user-guide/powerbi)
- [Power BI Community](https://community.powerbi.com/)

### Training
- Power BI Fundamentals (Microsoft Learn)
- DAX Basics (SQLBI.com)
- Snowflake for BI (Snowflake University)

---

**Wiki Version**: 1.0
**Last Updated**: 2025-10-24
**Author**: GenericCorp Data Engineering Team
**Project**: SECURITY_ANALYTICS Data Warehouse
**Status**: 🟡 Planned - Not Yet Implemented
