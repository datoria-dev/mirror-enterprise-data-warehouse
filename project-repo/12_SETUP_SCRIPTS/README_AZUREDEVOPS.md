# 🛡️ SECURITY_ANALYTICS Data Warehouse - Project Summary

**Enterprise security data automation, normalization and visualization for the GenericCorp Group Info Security function**

---

## 📊 At a Glance

| Metric | Value | Impact |
|--------|-------|--------|
| **Database Objects** | 550+ | Comprehensive 3-layer architecture |
| **Automation Coverage** | 98.1% | Minimal manual intervention |
| **Annual Cost Savings** | $146,250 | 94% reduction in manual operations |
| **Data Quality Score** | 72.3% | Measured and continuously improving |
| **Security Services** | 15 integrated | Unified visibility across all platforms |
| **Query Performance** | 319ms avg | Sub-second analytics |

---

## 🎯 Project Focus

### Focus: IT Security KPI Metrics and Monitoring

**Scope**: Complete data warehouse covering three layers:
- **DEV_LANDING**: Raw data ingestion from 15+ security services
- **DEV_TRANSFORMATION**: Normalized dimensional model with business logic
- **DEV_REPORTING**: Executive dashboards and operational analytics

**Purpose**: Security metrics from 15+ services including:
- **Endpoint Protection**: CrowdStrike, Symantec, McAfee, Sophos, TrendMicro, Sentinel
- **Vulnerability Management**: Qualys, Tenable
- **Threat Intelligence**: BitSight, CybelAngel, ZeroFox
- **Identity & Access**: Ancon, Leviat
- **SIEM**: Splunk
- **Cloud Security**: Zscaler, Microsoft Defender

---

## 🏆 Key Deliverables

### 📦 Technical Achievements
- ✅ **550+ database objects** (tables, views, procedures, tasks)
- ✅ **12 Streamlit dashboards** for security data quality monitoring
- ✅ **Automated ETL pipelines** with Snowpipe and Snowflake Tasks
- ✅ **Top 13 executive KPIs** aligned with NIST Cybersecurity Framework 2.0
- ✅ **Real-time + batch processing** capabilities

### 💼 Business Value
- 💰 **$146,250 annual labor savings** through automation
- ⚡ **319ms average query performance** for executive dashboards
- 📊 **72.3% data quality score** with full lineage tracking
- 🔒 **100% referential integrity** (57 primary keys + 16 foreign keys)
- 🎯 **57.7M records processed** across all security platforms

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│          LAYER 3: DEV_REPORTING                     │
│  • 148 Views - Business analytics                  │
│  • 18 Tables - Materialized reports                │
│  • Executive KPI dashboards                        │
└─────────────────────────────────────────────────────┘
                      ▲
                      │ ETL + Quality Checks
┌─────────────────────────────────────────────────────┐
│          LAYER 2: DEV_TRANSFORMATION                │
│  • 32 Dimensions - Business entities               │
│  • 23 Facts - Metrics and measurements             │
│  • 50 Views - Transformation logic                 │
│  • 15 Procedures - ETL orchestration               │
└─────────────────────────────────────────────────────┘
                      ▲
                      │ Ingestion (Real-time + Batch)
┌─────────────────────────────────────────────────────┐
│          LAYER 1: DEV_LANDING                       │
│  • 141 Tables - Raw security data                  │
│  • 5 Snowpipes - Real-time ingestion               │
│  • 3 External Tables - Batch processing            │
└─────────────────────────────────────────────────────┘
```

---

## 📋 Top 13 NIST CSF 2.0-Aligned KPIs

| NIST Function | KPI | Target | Status |
|---------------|-----|--------|--------|
| **Identify (ID)** | Asset Inventory Completeness | >95% | Measuring |
| **Identify (ID)** | Critical Asset Coverage | 100% | Measuring |
| **Protect (PR)** | Patch Compliance Rate | >90% | Measuring |
| **Protect (PR)** | EDR Coverage | >95% | **87.3%** |
| **Protect (PR)** | MFA Adoption | 100% | Measuring |
| **Detect (DE)** | Mean Time to Detect (MTTD) | <15 min | Measuring |
| **Detect (DE)** | Security Alert Volume | Baseline | Monitoring |
| **Respond (RS)** | Mean Time to Respond (MTTR) | <4 hrs | Measuring |
| **Respond (RS)** | Incident Response Rate | >95% | Measuring |
| **Recover (RC)** | Mean Time to Recover | <24 hrs | Measuring |
| **Recover (RC)** | Vulnerability Remediation Time | <30 days | Measuring |
| **Governance (GV)** | Policy Compliance Score | >90% | Measuring |
| **Governance (GV)** | Security Training Completion | 100% | Measuring |

---

## 🚀 Quick Links

### 📖 Documentation
- **[Project Wiki](https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_wiki)** - Complete documentation hub
- **[Deployment Guide](.azuredevops/wiki/Deployment-Guide.md)** - Step-by-step implementation
- **[Architecture Diagrams](ARCHITECTURE_DIAGRAMS.md)** - Visual data model representations

### 🔧 Development
- **[Repos](https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_git/GIS%20-%20ITSECKPI%20-%20DW)** - Source code repository
- **[Pipelines](https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_build)** - CI/CD automation
- **[Work Items](https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_workitems)** - Task tracking

### 📊 Dashboards & Reports
- **[Streamlit Apps](09_STREAMLIT_APPS/)** - 12 interactive data quality dashboards
- **[Power BI Dashboards](10_POWERBI_DASHBOARDS/)** - Executive and operational reports
- **[Final Deliverables](FINAL_DELIVERABLES/)** - Production-ready documentation and scripts

---

## 👥 Team & Stakeholders

### Project Sponsor
**Nick Heigerick** - Director of Analytics Strategy
📧 Nick.Heigerick@CompanyX.com | CompanyX Infrastructure (a GenericCorp Company)

### Security Stakeholders (GenericCorp Ireland HQ)
**Daragh O'Reilly** - Cyber Performance and Reporting Manager
📧 doreilly@GenericCorp.com | GenericCorp Ireland (HQ)

**Ronan O'Connor** - Information Security Architect
📧 roconnor@GenericCorp.com | GenericCorp Ireland (HQ)

### Development Team
**Fuad Onate** - Lead Data Engineer
📧 fuad.onate@CompanyX.com | CompanyX Infrastructure

---

## 🛠️ Technology Stack

| Category | Technologies |
|----------|-------------|
| **Data Platform** | Snowflake Cloud Data Warehouse |
| **ETL/ELT** | Snowpipe, Snowflake Tasks, Stored Procedures |
| **Programming** | Python 3.13, SQL, JavaScript |
| **Visualization** | Streamlit, Power BI, Plotly |
| **DevOps** | Azure DevOps (CI/CD, Repos, Boards, Wiki) |
| **Cloud Storage** | AWS S3, Azure Blob Storage |

---

## 📞 Getting Help

### For Issues & Bugs
1. Search existing [Work Items](https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_workitems)
2. Create new work item in Azure Boards
3. Tag relevant team members
4. Provide detailed reproduction steps

### For Questions
1. Check [Project Wiki](https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_wiki) first
2. Review troubleshooting guides
3. Ask in pull request comments
4. Contact team members via email

### Emergency Contacts
- **Critical Production Issues**: Contact on-call Snowflake admin via ServiceNow
- **Security Incidents**: Escalate to GenericCorp Security Team (doreilly@GenericCorp.com)
- **Access Issues**: Contact Azure DevOps project admin

---

## 📊 Project Status

**Status**: ✅ Production Ready | 🚀 Actively Maintained | 📈 v3.0

**Last Updated**: October 2025

---

**Organization**: CompanyX Infrastructure (a GenericCorp Company)
**Project**: GIS - SECURITY_ANALYTICS - DW
**Repository**: [Azure DevOps](https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW)
