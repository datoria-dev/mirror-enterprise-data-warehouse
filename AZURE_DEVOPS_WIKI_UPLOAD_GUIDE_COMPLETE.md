# Azure DevOps Wiki Upload Guide - Complete Edition

## Overview

This guide provides instructions for uploading **all six SECURITY_ANALYTICS Data Warehouse wikis** to Azure DevOps.

---

## Wiki Files Created

Six comprehensive wikis have been created for the Azure DevOps repository:

### 1. WIKI_01_STREAMLIT_APPS.md
**Purpose**: Complete documentation of all Streamlit applications
**Size**: ~30KB
**Contents**:
- 20 Streamlit applications across 6 categories
- Architecture and features
- Metadata tab integration for 6 services
- Deployment guide and troubleshooting

### 2. WIKI_02_POWER_BI.md
**Purpose**: Power BI implementation roadmap and planning
**Size**: ~25KB
**Contents**:
- Future Power BI architecture
- 6-month implementation roadmap
- Data model design with star schema
- Report templates and security plans
- Integration with existing Streamlit apps

### 3. WIKI_03_METADATA_EXTRACTION.md
**Purpose**: Metadata extraction and automation processes
**Size**: ~35KB
**Contents**:
- Centralized metadata extraction system
- Automatic service detection (20+ services)
- Scheduled automation with Snowflake Tasks
- Export processes and application integration
- Monitoring, maintenance, and troubleshooting

### 4. WIKI_04_DATA_GOVERNANCE.md
**Purpose**: Data governance framework and policies
**Size**: ~40KB
**Contents**:
- Governance structure and hierarchy
- Data ownership and stewardship model
- Data quality standards and dimensions
- Security and access control policies
- Data lifecycle management
- Compliance and auditing requirements
- Roles and responsibilities (RACI matrix)

### 5. WIKI_05_DATA_DICTIONARY.md
**Purpose**: Complete data dictionary for all services
**Size**: ~50KB
**Contents**:
- 20 security services documented
- 180 tables with descriptions
- 2,206 columns with definitions
- Common data elements and patterns
- Data types reference
- Metadata repository tables

### 6. WIKI_06_BEST_PRACTICES.md
**Purpose**: Development standards and best practices
**Size**: ~45KB
**Contents**:
- SQL development standards
- Python development standards
- Snowflake optimization techniques
- Streamlit application development
- Security best practices
- Testing and QA standards
- Version control and Git workflow
- Documentation standards
- Deployment and release management
- Troubleshooting and performance monitoring

**Total Documentation**: ~225KB across 6 comprehensive wikis

---

## File Locations

All wiki files are located in:
```
C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\

├── WIKI_01_STREAMLIT_APPS.md
├── WIKI_02_POWER_BI.md
├── WIKI_03_METADATA_EXTRACTION.md
├── WIKI_04_DATA_GOVERNANCE.md
├── WIKI_05_DATA_DICTIONARY.md
└── WIKI_06_BEST_PRACTICES.md
```

---

## Upload Methods

### Method 1: Azure DevOps Web Interface (Recommended)

#### Step 1: Navigate to Wiki
1. Open your Azure DevOps project
2. Go to **Overview** → **Wiki**
3. If no wiki exists, click **Create project wiki**

#### Step 2: Upload Files
1. Click **New page** or **Import**
2. Select **Import from Markdown**
3. Upload each wiki file in order:
   - `WIKI_01_STREAMLIT_APPS.md`
   - `WIKI_02_POWER_BI.md`
   - `WIKI_03_METADATA_EXTRACTION.md`
   - `WIKI_04_DATA_GOVERNANCE.md`
   - `WIKI_05_DATA_DICTIONARY.md`
   - `WIKI_06_BEST_PRACTICES.md`

#### Step 3: Organize Structure
Create folder structure in Azure DevOps wiki:
```
SECURITY_ANALYTICS Data Warehouse/
├── 01 - Streamlit Applications
├── 02 - Power BI Roadmap
├── 03 - Metadata Extraction & Automation
├── 04 - Data Governance Framework
├── 05 - Data Dictionary
└── 06 - Development Best Practices
```

---

### Method 2: Git Commands (For Wiki as Code)

If your Azure DevOps project has wiki configured as a Git repository:

#### Step 1: Clone Wiki Repository
```bash
# Navigate to project directory
cd C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV

# Clone the wiki repository (replace with your actual wiki repo URL)
git clone https://dev.azure.com/YourOrg/YourProject/_git/YourProject.wiki wiki-repo

cd wiki-repo
```

#### Step 2: Copy Wiki Files
```bash
# Create directory structure
mkdir -p "SECURITY_ANALYTICS-Data-Warehouse"

# Copy all wiki files
cp ../WIKI_01_STREAMLIT_APPS.md "SECURITY_ANALYTICS-Data-Warehouse/01-Streamlit-Applications.md"
cp ../WIKI_02_POWER_BI.md "SECURITY_ANALYTICS-Data-Warehouse/02-Power-BI-Roadmap.md"
cp ../WIKI_03_METADATA_EXTRACTION.md "SECURITY_ANALYTICS-Data-Warehouse/03-Metadata-Extraction.md"
cp ../WIKI_04_DATA_GOVERNANCE.md "SECURITY_ANALYTICS-Data-Warehouse/04-Data-Governance.md"
cp ../WIKI_05_DATA_DICTIONARY.md "SECURITY_ANALYTICS-Data-Warehouse/05-Data-Dictionary.md"
cp ../WIKI_06_BEST_PRACTICES.md "SECURITY_ANALYTICS-Data-Warehouse/06-Best-Practices.md"
```

#### Step 3: Commit and Push
```bash
# Stage files
git add .

# Commit
git commit -m "Add SECURITY_ANALYTICS Data Warehouse comprehensive documentation

- Streamlit applications catalog (20 apps)
- Power BI implementation roadmap
- Metadata extraction automation guide
- Data governance framework
- Complete data dictionary (20 services, 180 tables, 2,206 columns)
- Development best practices

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to Azure DevOps
git push origin main
```

---

### Method 3: Azure CLI (Automated)

If you have Azure CLI installed with Azure DevOps extension:

```bash
# Login to Azure DevOps
az login

# Set default organization and project
az devops configure --defaults organization=https://dev.azure.com/YourOrg project=YourProject

# Create all wiki pages
az devops wiki page create \
    --wiki "YourProject.wiki" \
    --path "SECURITY_ANALYTICS-Data-Warehouse/01-Streamlit-Applications" \
    --file-path "WIKI_01_STREAMLIT_APPS.md"

az devops wiki page create \
    --wiki "YourProject.wiki" \
    --path "SECURITY_ANALYTICS-Data-Warehouse/02-Power-BI-Roadmap" \
    --file-path "WIKI_02_POWER_BI.md"

az devops wiki page create \
    --wiki "YourProject.wiki" \
    --path "SECURITY_ANALYTICS-Data-Warehouse/03-Metadata-Extraction" \
    --file-path "WIKI_03_METADATA_EXTRACTION.md"

az devops wiki page create \
    --wiki "YourProject.wiki" \
    --path "SECURITY_ANALYTICS-Data-Warehouse/04-Data-Governance" \
    --file-path "WIKI_04_DATA_GOVERNANCE.md"

az devops wiki page create \
    --wiki "YourProject.wiki" \
    --path "SECURITY_ANALYTICS-Data-Warehouse/05-Data-Dictionary" \
    --file-path "WIKI_05_DATA_DICTIONARY.md"

az devops wiki page create \
    --wiki "YourProject.wiki" \
    --path "SECURITY_ANALYTICS-Data-Warehouse/06-Best-Practices" \
    --file-path "WIKI_06_BEST_PRACTICES.md"
```

---

## Recommended Wiki Structure in Azure DevOps

```
📁 SECURITY_ANALYTICS Data Warehouse
│
├── 📄 Overview (Create a landing page - see template below)
│   ├── Project Description
│   ├── Architecture Diagram
│   └── Quick Links to All Wikis
│
├── 📄 01 - Streamlit Applications
│   ├── Application Catalog (20 apps)
│   ├── Architecture & Features
│   ├── Metadata Integration
│   ├── Deployment Guide
│   └── Troubleshooting
│
├── 📄 02 - Power BI Roadmap
│   ├── Implementation Plan (6 months)
│   ├── Data Model Design
│   ├── Report Templates
│   ├── Security & Access
│   └── Best Practices
│
├── 📄 03 - Metadata Extraction & Automation
│   ├── Architecture Overview
│   ├── Centralized Extraction (SP_REFRESH_METADATA)
│   ├── Service Detection (20+ services)
│   ├── Scheduled Automation
│   ├── Export Processes
│   ├── Application Integration
│   └── Monitoring & Maintenance
│
├── 📄 04 - Data Governance Framework
│   ├── Governance Structure
│   ├── Data Ownership Model
│   ├── Quality Standards
│   ├── Security & Access Control
│   ├── Data Lifecycle Management
│   ├── Compliance & Auditing
│   └── Roles & Responsibilities
│
├── 📄 05 - Data Dictionary
│   ├── Service Catalog (20 services)
│   ├── Endpoint Security Services
│   ├── Email & Cloud Security
│   ├── Vulnerability Management
│   ├── Threat Intelligence
│   ├── ITSM & Asset Management
│   ├── Metadata Repository Tables
│   └── Common Data Elements
│
├── 📄 06 - Development Best Practices
│   ├── SQL Development Standards
│   ├── Python Development Standards
│   ├── Snowflake Optimization
│   ├── Streamlit Development
│   ├── Security Best Practices
│   ├── Testing & QA
│   ├── Version Control Workflow
│   └── Deployment & Monitoring
│
└── 📁 Additional Documentation
    ├── SQL Scripts Reference
    ├── Python Scripts Reference
    ├── Configuration Guide
    └── Support & Contacts
```

---

## Creating a Landing Page (Recommended)

Create a main `Overview.md` page in Azure DevOps wiki:

```markdown
# SECURITY_ANALYTICS Data Warehouse Documentation

## Welcome

This wiki provides comprehensive documentation for the SECURITY_ANALYTICS Data Warehouse project, covering all aspects from applications to governance, data dictionary, and development standards.

## Quick Navigation

### 📱 Applications & Roadmap
- **[01 - Streamlit Applications](01-Streamlit-Applications)** - 20 interactive analytics applications
- **[02 - Power BI Roadmap](02-Power-BI-Roadmap)** - Future BI implementation plan (6 months)

### 🔧 Technical Documentation
- **[03 - Metadata Extraction](03-Metadata-Extraction)** - Automated metadata management system
- **[05 - Data Dictionary](05-Data-Dictionary)** - Complete catalog of all tables and columns

### 📋 Governance & Standards
- **[04 - Data Governance](04-Data-Governance)** - Governance framework and policies
- **[06 - Best Practices](06-Best-Practices)** - Development standards and guidelines

## Project Statistics

- **Security Services**: 20 integrated services
- **Tables Cataloged**: 180 tables
- **Columns Documented**: 2,206 columns
- **Streamlit Apps**: 20 applications
- **Data Volume**: 32.5M+ rows
- **Daily Automation**: Metadata refresh at 6:00 AM EST

## Key Components

### Data Architecture
```
Source Systems (20+ Security Services)
            ↓
    DEV_LANDING (Raw Data)
            ↓
    DEV_TRANSFORMATION (Processed Data)
            ↓
    Applications (Streamlit, Power BI)
```

### Data Layers
- **DEV_LANDING**: Raw data storage (90-day retention)
- **DEV_TRANSFORMATION**: Processed data (2-year retention)
- **METADATA**: Centralized metadata repository
- **METADATA_EXPORTS**: Application-ready exports

### Applications
- **Streamlit Analytics**: 20 production applications
- **Power BI Reports**: Planned for 2025
- **Metadata Repository**: Automated daily refresh

### Automation
- **SP_REFRESH_METADATA**: Daily metadata extraction (6:00 AM EST)
- **TASK_DAILY_METADATA_REFRESH**: Scheduled task automation
- **Export Processes**: 13 materialized export tables

## Getting Started

### For New Users
1. Review [01 - Streamlit Applications](01-Streamlit-Applications) to access dashboards
2. Consult [05 - Data Dictionary](05-Data-Dictionary) to understand data structures
3. Check [04 - Data Governance](04-Data-Governance) for access procedures

### For Developers
1. Read [06 - Best Practices](06-Best-Practices) for development standards
2. Study [03 - Metadata Extraction](03-Metadata-Extraction) for automation details
3. Review [02 - Power BI Roadmap](02-Power-BI-Roadmap) for future development

### For Data Stewards
1. Understand [04 - Data Governance](04-Data-Governance) framework
2. Maintain [05 - Data Dictionary](05-Data-Dictionary) documentation
3. Monitor metadata via [03 - Metadata Extraction](03-Metadata-Extraction)

## Service Categories

### Endpoint Security (9 services)
SentinelOne, CrowdStrike, Defender, Qualys, Symantec, Cisco AMP, Trellix, Trend Micro, McAfee, Sophos

### Threat Intelligence (4 services)
CybelAngel, ZeroFox, Intel_Threats, BitSight

### Email & Cloud Security (2 services)
Proofpoint, Zscaler

### ITSM & Asset Management (3 services)
ServiceNow, Leviat, Ancon

### SIEM & Monitoring (1 service)
Splunk

### Planned Integrations
Tenable, Okta, Azure AD

## Support

For questions or issues:
- **Data Engineering Team**: IT Data Warehouse Team
- **Application Support**: Analytics Team
- **Governance Questions**: data.governance@CompanyX.com
- **Technical Issues**: IT Service Desk

## Recent Updates

- **2025-10-24**: Complete wiki documentation published
  - 6 comprehensive wikis created
  - 20 services documented
  - 180 tables cataloged
  - 2,206 columns defined
  - Best practices established

---

**Documentation Version**: 1.0
**Last Updated**: 2025-10-24
**Maintained By**: GenericCorp Data Engineering Team
```

---

## Post-Upload Checklist

After uploading wikis to Azure DevOps:

- [ ] Verify all six wiki pages are accessible
- [ ] Check that internal links work correctly (cross-references between wikis)
- [ ] Confirm code blocks and tables render properly
- [ ] Test table of contents navigation within each wiki
- [ ] Verify SQL and Python code syntax highlighting
- [ ] Set appropriate page permissions (read access for all, edit for stewards)
- [ ] Add tags/labels for searchability:
  - `data-warehouse`, `SECURITY_ANALYTICS`, `security`, `metadata`, `governance`, `streamlit`
- [ ] Link wikis from project README or homepage
- [ ] Create bookmarks for frequently accessed sections
- [ ] Notify team members of new documentation via email/Teams
- [ ] Schedule wiki review meeting with stakeholders

---

## Maintenance

### Updating Wikis

When project changes occur:

1. **Update local markdown files** first in your working directory
2. **Test changes** locally (preview markdown rendering)
3. **Upload updated versions** to Azure DevOps
4. **Update version history** in wiki footer
5. **Notify stakeholders** of significant changes

### Update Frequency by Wiki

| Wiki | Update Frequency | Owner |
|------|-----------------|-------|
| 01 - Streamlit Apps | After new app deployments | Development Team |
| 02 - Power BI Roadmap | Quarterly | BI Team Lead |
| 03 - Metadata Extraction | After automation changes | Data Engineering |
| 04 - Data Governance | Quarterly or as policies change | Governance Council |
| 05 - Data Dictionary | Monthly (automated metadata) | Data Stewards |
| 06 - Best Practices | As standards evolve | Technical Lead |

### Regular Reviews

- **Monthly**: Review Data Dictionary for accuracy (auto-updated metadata)
- **Quarterly**: Review all wikis for accuracy and updates
- **After Major Changes**: Update relevant wikis immediately
- **Annual**: Comprehensive review of all documentation

---

## Troubleshooting

### Images Not Displaying

If you include images in wikis:
1. Store images in Azure DevOps repository under `/.attachments/`
2. Use relative paths: `![Alt text](/.attachments/image.png)`
3. Or use absolute URLs to publicly accessible images
4. Ensure image files are <1MB for performance

### Broken Links

**Internal Wiki Links**:
- Use relative links: `[Page Title](Page-Name)`
- Azure DevOps automatically creates page anchors from headers
- Format: `[Link Text](#header-name)` for same-page links
- Format: `[Link Text](Other-Wiki-Page#header-name)` for cross-page links

**External Links**:
- Use full URLs: `[Link Text](https://example.com)`
- Test all external links before publishing

### Formatting Issues

- **Tables**: Keep tables under 10 columns for readability
- **Code Blocks**: Use triple backticks with language identifier:
  ```sql
  SELECT * FROM TABLE;
  ```
- **Line Length**: Keep lines under 120 characters in markdown source
- **Special Characters**: Escape with backslash: `\*`, `\_`, `\#`

### Upload Errors

**"File Too Large"**:
- Azure DevOps wiki pages have a 1MB limit
- Split large wikis into multiple pages
- Consider linking to external documentation for very large content

**"Permission Denied"**:
- Ensure you have Wiki Contributor permissions
- Contact project administrator to grant access

**"Merge Conflict"**:
- Someone else edited the wiki simultaneously
- Refresh page and re-apply your changes
- Use Git method for better conflict resolution

---

## Additional Resources

- [Azure DevOps Wiki Documentation](https://learn.microsoft.com/en-us/azure/devops/project/wiki/)
- [Markdown Syntax Guide](https://www.markdownguide.org/)
- [Azure DevOps Best Practices](https://learn.microsoft.com/en-us/azure/devops/organizations/)
- [Snowflake Documentation](https://docs.snowflake.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

## Summary

You have created **6 comprehensive wikis** totaling **~225KB** of documentation:

1. ✅ **Streamlit Applications** (30KB) - Application catalog
2. ✅ **Power BI Roadmap** (25KB) - Implementation plan
3. ✅ **Metadata Extraction** (35KB) - Automation system
4. ✅ **Data Governance** (40KB) - Governance framework
5. ✅ **Data Dictionary** (50KB) - Complete data catalog
6. ✅ **Best Practices** (45KB) - Development standards

**Next Step**: Upload to Azure DevOps using one of the three methods above (Web Interface recommended for ease of use).

---

**Document Created**: 2025-10-24
**Author**: GenericCorp Data Engineering Team
**Purpose**: Complete guide for uploading all SECURITY_ANALYTICS Data Warehouse wikis to Azure DevOps
**Status**: Ready for Upload
