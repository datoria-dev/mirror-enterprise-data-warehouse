# Azure DevOps Wiki Upload Guide

## Overview

This guide provides instructions for uploading the three SECURITY_ANALYTICS Data Warehouse wikis to Azure DevOps.

---

## Wiki Files Created

Three comprehensive wikis have been created for the Azure DevOps repository:

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

---

## File Locations

All wiki files are located in:
```
C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\

├── WIKI_01_STREAMLIT_APPS.md
├── WIKI_02_POWER_BI.md
└── WIKI_03_METADATA_EXTRACTION.md
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
3. Upload each wiki file:
   - `WIKI_01_STREAMLIT_APPS.md`
   - `WIKI_02_POWER_BI.md`
   - `WIKI_03_METADATA_EXTRACTION.md`

#### Step 3: Organize Structure
Create folder structure in Azure DevOps wiki:
```
SECURITY_ANALYTICS Data Warehouse/
├── 01 - Streamlit Applications
├── 02 - Power BI Roadmap
└── 03 - Metadata Extraction & Automation
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

# Copy wiki files
cp ../WIKI_01_STREAMLIT_APPS.md "SECURITY_ANALYTICS-Data-Warehouse/01-Streamlit-Applications.md"
cp ../WIKI_02_POWER_BI.md "SECURITY_ANALYTICS-Data-Warehouse/02-Power-BI-Roadmap.md"
cp ../WIKI_03_METADATA_EXTRACTION.md "SECURITY_ANALYTICS-Data-Warehouse/03-Metadata-Extraction.md"
```

#### Step 3: Commit and Push
```bash
# Stage files
git add .

# Commit
git commit -m "Add SECURITY_ANALYTICS Data Warehouse documentation wikis

- Streamlit applications catalog (20 apps)
- Power BI implementation roadmap
- Metadata extraction automation guide"

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

# Create wiki pages
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
```

---

## Recommended Wiki Structure in Azure DevOps

```
📁 SECURITY_ANALYTICS Data Warehouse
│
├── 📄 Overview (Create a landing page)
│   ├── Project Description
│   ├── Architecture Diagram
│   └── Quick Links
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
│   ├── Centralized Extraction
│   ├── Service Detection (20+ services)
│   ├── Scheduled Automation
│   ├── Export Processes
│   ├── Application Integration
│   └── Monitoring & Maintenance
│
└── 📁 Additional Documentation
    ├── SQL Scripts Reference
    ├── Python Scripts Reference
    ├── Configuration Guide
    └── Support & Contacts
```

---

## Creating a Landing Page (Optional)

Create a main `Overview.md` page in Azure DevOps wiki:

```markdown
# SECURITY_ANALYTICS Data Warehouse Documentation

## Welcome

This wiki provides comprehensive documentation for the SECURITY_ANALYTICS Data Warehouse project, including Streamlit applications, Power BI roadmap, and metadata extraction automation.

## Quick Navigation

- **[Streamlit Applications](01-Streamlit-Applications)** - 20 interactive analytics applications
- **[Power BI Roadmap](02-Power-BI-Roadmap)** - Future BI implementation plan
- **[Metadata Extraction](03-Metadata-Extraction)** - Automated metadata management

## Project Statistics

- **Security Services**: 20+ integrated services
- **Tables Cataloged**: 180 tables
- **Columns Documented**: 2,206 columns
- **Streamlit Apps**: 20 applications
- **Daily Automation**: Metadata refresh at 6:00 AM EST

## Key Components

### Data Sources
- DEV_LANDING (Raw data)
- DEV_TRANSFORMATION (Processed data)

### Applications
- Streamlit Analytics (Production)
- Power BI Reports (Planned)

### Automation
- Daily metadata extraction
- Scheduled exports
- Application integration

## Getting Started

1. Review the [Streamlit Applications](01-Streamlit-Applications) guide
2. Explore the [Metadata Extraction](03-Metadata-Extraction) automation
3. Check the [Power BI Roadmap](02-Power-BI-Roadmap) for future plans

## Support

For questions or issues, contact:
- **Data Engineering Team**: IT Data Warehouse Team
- **Application Support**: Analytics Team
```

---

## Post-Upload Checklist

After uploading wikis to Azure DevOps:

- [ ] Verify all three wiki pages are accessible
- [ ] Check that internal links work correctly
- [ ] Confirm code blocks and tables render properly
- [ ] Test table of contents navigation
- [ ] Set appropriate page permissions
- [ ] Add tags/labels for searchability
- [ ] Link wikis from project README or homepage
- [ ] Notify team members of new documentation

---

## Maintenance

### Updating Wikis

When project changes occur:

1. **Update local markdown files** first
2. **Test changes** locally
3. **Upload updated versions** to Azure DevOps
4. **Update version history** in wiki footer

### Regular Reviews

- **Monthly**: Review for accuracy and updates
- **Quarterly**: Major revisions based on project evolution
- **After deployments**: Update with new features/changes

---

## Troubleshooting

### Images Not Displaying

If you include images in wikis:
1. Store images in Azure DevOps repository
2. Use relative paths: `![Alt text](/.attachments/image.png)`
3. Or use absolute URLs to publicly accessible images

### Broken Links

- Use relative links for internal wiki pages: `[Page Title](Page-Name)`
- Azure DevOps automatically creates page anchors from headers

### Formatting Issues

- Preview markdown locally before uploading
- Use Azure DevOps markdown preview feature
- Check that tables don't exceed page width

---

## Additional Resources

- [Azure DevOps Wiki Documentation](https://learn.microsoft.com/en-us/azure/devops/project/wiki/)
- [Markdown Syntax Guide](https://www.markdownguide.org/)
- [Azure DevOps Best Practices](https://learn.microsoft.com/en-us/azure/devops/organizations/)

---

**Document Created**: 2025-10-24
**Author**: GenericCorp Data Engineering Team
**Purpose**: Guide for uploading SECURITY_ANALYTICS wikis to Azure DevOps
