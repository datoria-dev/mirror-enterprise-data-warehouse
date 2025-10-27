# SECURITY_ANALYTICS Data Warehouse - Wiki Home

Welcome to the **IT Security KPI Data Warehouse** project wiki! This comprehensive guide provides everything you need to understand, deploy, and maintain the enterprise security analytics platform.

## 🚀 Quick Links

- [[Architecture Overview|Architecture]]
- [[Deployment Guide|Deployment-Guide]]
- [[Troubleshooting|Troubleshooting]]
- [[API Documentation|API-Documentation]]
- [[Security Services|Security-Services]]
- [[Top 13 KPIs|KPIs]]

---

## 📊 Project Overview

The **SECURITY_ANALYTICS (IT Security KPI) Data Warehouse** is a comprehensive security analytics platform built on Snowflake, designed to provide unified visibility across 15+ security services with automated data pipelines, quality monitoring, and executive-ready reporting.

### Key Statistics

- **550+ Database Objects** deployed across 3-layer architecture
- **98.1% Automation Success** (52/53 objects deployed)
- **$146,250 Annual Labor Savings**
- **94% Reduction** in manual data operations
- **15 Security Services** integrated (EDR, SIEM, VM, IAM, Threat Intel)
- **Top 13 Executive KPIs** aligned with NIST Cybersecurity Framework 2.0
- **Real-time + Batch Pipelines** using Snowpipe and Tasks
- **12 Streamlit Validation Dashboards** for data quality

---

## 🏗️ Architecture

### 3-Layer Data Warehouse

```
┌─────────────────────────────────────────────────────────────────┐
│                  LAYER 3: DEV_REPORTING                         │
│  • 148 Views (VW_*) - Business-ready analytics                  │
│  • 18 Tables (BOL_*, RPT_*) - Materialized reports              │
│  • 10 Procedures - View extraction and documentation            │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ ETL + Quality Checks
┌─────────────────────────────────────────────────────────────────┐
│                  LAYER 2: DEV_TRANSFORMATION                    │
│  • 32 Dimensions (DIM_*) - Business entities                    │
│  • 23 Facts (FACT_*) - Metrics and measurements                 │
│  • 50 Views - Transformation logic                              │
│  • 15 Procedures - ETL transformations                          │
│  • 11 Tasks - Automated orchestration                           │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ Ingestion (Snowpipe + Batch)
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 1: DEV_LANDING                         │
│  • 141 Tables - Raw data from security services                 │
│  • 11 Views - Consolidated source data                          │
│  • 5 Snowpipes - Real-time ingestion                            │
│  • 3 External Tables - Batch ingestion                          │
└─────────────────────────────────────────────────────────────────┘
```

See [[Architecture|Architecture]] for detailed architecture diagrams.

---

## 🔧 Quick Start

### Prerequisites

- Snowflake account with ACCOUNTADMIN privileges
- Python 3.13+
- Azure DevOps access (Contributor role)

### Installation

1. **Clone the repository**
```bash
git clone https://dev.azure.com/CompanyX/GIS-SECURITY_ANALYTICS-DW/_git/GIS-SECURITY_ANALYTICS-DW
cd GIS-SECURITY_ANALYTICS-DW
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Snowflake connection**
```bash
cp .env.example .env
# Edit .env with your Snowflake credentials
```

4. **Verify environment**
```bash
python 02_PYTHON_SCRIPTS/test_connection.py
```

See [[Deployment Guide|Deployment-Guide]] for complete deployment instructions.

---

## 📁 Repository Structure

```
GIS-SECURITY_ANALYTICS-DW/
├── 01_SQL_SCRIPTS/           # All SQL implementation files
├── 02_PYTHON_SCRIPTS/        # Automation and deployment utilities
├── 03_CONFIG/                # Configuration files
├── 04_DOCUMENTATION/         # Comprehensive project documentation
├── 05_ANALYSIS_RESULTS/      # JSON/CSV outputs
├── 07_STREAMLIT_APPS/        # 12 Streamlit dashboards
├── 10_POWERBI_DASHBOARDS/    # Power BI reference dashboards
├── 11_SERVICENOW_INTEGRATION/# ServiceNow components
├── FINAL_DELIVERABLES/       # Production-ready deliverables
└── .azuredevops/             # Azure DevOps pipelines and wiki
```

---

## 🔒 Security Services

### Currently Integrated (15 Services)

| Service | Category | Status | Purpose |
|---------|----------|--------|---------|
| **CrowdStrike** | EDR | ✅ Active | Endpoint threat detection |
| **Symantec** | Endpoint | ✅ Active | Antivirus protection |
| **Qualys** | VM | ✅ Active | Vulnerability scanning |
| **BitSight** | Rating | ✅ Active | Security posture rating |
| **Splunk** | SIEM | ⚠️ Pending | Log analytics |
| **Zscaler** | Cloud Security | ⚠️ Pending | Secure web gateway |
| ... and 9 more services |

See [[Security Services|Security-Services]] for complete integration details.

---

## 📈 Top 13 Executive Metrics

Aligned with **NIST Cybersecurity Framework 2.0**

### Identify (ID)
1. **Asset Inventory Completeness** - % of devices in CMDB
2. **Critical Asset Coverage** - % critical assets with security controls

### Protect (PR)
3. **Patch Compliance Rate** - % systems with latest patches
4. **EDR Coverage** - % endpoints with active EDR agents
5. **MFA Adoption** - % privileged users with MFA enabled

### Detect (DE)
6. **Mean Time to Detect (MTTD)** - Average hours to detect threats
7. **Security Alert Volume** - Daily critical/high alerts

### Respond (RS)
8. **Mean Time to Respond (MTTR)** - Average hours to respond
9. **Incident Response Rate** - % incidents resolved within SLA

### Recover (RC)
10. **Mean Time to Recover** - Average hours to full recovery
11. **Vulnerability Remediation Time** - Average days to fix critical CVEs

### Governance (GV)
12. **Policy Compliance Score** - % compliance with security policies
13. **Security Training Completion** - % employees completed training

See [[KPIs|KPIs]] for detailed metric definitions and calculations.

---

## 🔄 CI/CD Pipelines

### Available Pipelines

1. **CI Validation** (`ci-validation.yml`)
   - Validates Python, SQL, and documentation
   - Runs on commits to main/develop
   - Automatic quality checks

2. **CD Deployment** (`cd-deploy-snowflake.yml`)
   - Deploys to Snowflake DEV/PRD
   - Manual trigger with approval gates
   - Parameterized deployment scope

See pipeline YAML files in `.azuredevops/pipelines/`

---

## 📚 Documentation

### Available Guides

- **[Architecture Overview](Architecture)** - Complete technical architecture
- **[Deployment Guide](Deployment-Guide)** - Step-by-step deployment
- **[Troubleshooting](Troubleshooting)** - Common issues and solutions
- **[API Documentation](API-Documentation)** - REST API integration specs
- **[Security Services](Security-Services)** - Service integration details
- **[KPIs](KPIs)** - Executive metric definitions

### Comprehensive SECURITY_ANALYTICS Documentation

#### Applications & Roadmap
- **[01 Streamlit Applications](SECURITY_ANALYTICS-Documentation/01-Streamlit-Applications)** - 20 interactive analytics dashboards
- **[02 Power BI Roadmap](SECURITY_ANALYTICS-Documentation/02-Power-BI-Roadmap)** - 6-month BI implementation plan

#### Technical Documentation
- **[03 Metadata Extraction](SECURITY_ANALYTICS-Documentation/03-Metadata-Extraction)** - Automated metadata management system
- **[05 Data Dictionary](SECURITY_ANALYTICS-Documentation/05-Data-Dictionary)** - Complete data catalog (180 tables, 2,206 columns)
- **[07 API Integrations](SECURITY_ANALYTICS-Documentation/07-API-Integrations)** - API integration documentation
- **[08 Streamlit Deployment](SECURITY_ANALYTICS-Documentation/08-Streamlit-Deployment)** - Automated deployment guide
- **[09 Metadata Repository](SECURITY_ANALYTICS-Documentation/09-Metadata-Repository)** - Centralized data catalog system
- **[10 ServiceNow Integration](SECURITY_ANALYTICS-Documentation/10-ServiceNow-Integration)** - ServiceNow ITSM integration guide

#### Governance & Standards
- **[04 Data Governance](SECURITY_ANALYTICS-Documentation/04-Data-Governance)** - Governance framework and policies
- **[06 Best Practices](SECURITY_ANALYTICS-Documentation/06-Best-Practices)** - Development standards and guidelines

### External Documentation

- [Snowflake Documentation](https://docs.snowflake.com/)
- [NIST Cybersecurity Framework 2.0](https://www.nist.gov/cyberframework)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

## 🆘 Support

### Getting Help

- **Issues**: Create work items in Azure Boards
- **Questions**: Tag team members in pull requests
- **Emergencies**: Contact on-call Snowflake admin

### Team Contacts

- **Project Owner**: Nick Heigerick (Director of Analytics Strategy)
- **Technical Leads**: See Azure DevOps team members
- **Snowflake Admins**: Check ServiceNow CMDB

---

## 🎯 Project Status

**Status**: ✅ Production Ready | 🚀 Actively Maintained | 📊 98.1% Deployed

**Last Updated**: October 2025 | **Version**: 3.0

---

**Quick Stats Dashboard**

| Metric | Value |
|--------|-------|
| Database Objects | 550+ |
| SQL Scripts | 18 |
| Python Scripts | 8+ |
| Streamlit Apps | 12 |
| Security Services | 15 |
| Automation Success | 98.1% |
| Data Quality Score | 72.3% |
| Annual ROI | $146,250 |

---

**Navigation**: [[Next: Architecture →|Architecture]]
