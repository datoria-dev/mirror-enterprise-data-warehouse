# 🚀 Azure DevOps Complete Setup Guide

## Quick Links
- **Project URL**: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW
- **Repository**: GIS - SECURITY_ANALYTICS - DW
- **Branch**: main

---

## ✅ 1. Update Project Description (Overview Summary)

### Current Status
The "About this project" section shows old text with database scope information.

### Action Required
1. Navigate to: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_settings/
2. Click on **"Overview"** in the left sidebar
3. Click the **"Edit"** button next to the project description
4. **Delete the current text completely**
5. **Paste the new description** (see below)
6. Click **"Save"**

### New Project Description (Copy this exactly):

```
Enterprise-grade security analytics platform delivering unified visibility across 15+ security services with 98.1% automation coverage, NIST CSF 2.0 alignment, and real-time monitoring.

✅ 550+ database objects deployed across 3-layer Snowflake architecture
✅ 94% reduction in manual operations (40hrs/week → 2.5hrs/week)
✅ 1,820 hours saved annually - redeployable to high-value security work
✅ 15 security services integrated (CrowdStrike, Qualys, Splunk, Zscaler, etc.)
✅ Top 13 NIST CSF 2.0-aligned executive KPIs
✅ 12 Streamlit dashboards for data quality monitoring
✅ Real-time + batch ETL pipelines with Snowpipe and Snowflake Tasks
✅ 72.3% data quality score with 100% referential integrity
✅ 319ms average query performance

Built for: GenericCorp / CompanyX Infrastructure
Scope: DEV_LANDING → DEV_TRANSFORMATION → DEV_REPORTING
Technology: Snowflake, Python 3.13, Streamlit, Power BI, Azure DevOps
```

---

## 📚 2. Publish Code as Wiki

### Why This Matters
The repository already contains a complete wiki in `.azuredevops/wiki/` folder. Publishing it as a wiki makes it accessible from the Wiki tab in Azure DevOps.

### Action Required

1. Navigate to: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_wiki
2. Click **"Publish code as wiki"** button
3. In the dialog, configure:
   - **Repository**: GIS - SECURITY_ANALYTICS - DW
   - **Branch**: main
   - **Folder**: `.azuredevops/wiki`
   - **Wiki name**: "SECURITY_ANALYTICS Data Warehouse Documentation"
4. Click **"Publish"**

### What This Provides
- ✅ Professional wiki homepage with Quick Stats dashboard
- ✅ Architecture overview and design documentation
- ✅ Deployment guides and troubleshooting
- ✅ Links to security services and KPIs
- ✅ Quick links organized by category

---

## 🔧 3. Configure Repository Settings

### Branch Policies (Recommended for Team Collaboration)

1. Navigate to: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_settings/repositories
2. Click on the **"GIS - SECURITY_ANALYTICS - DW"** repository
3. Click on **"Policies"** tab
4. Click on **"main"** branch
5. Enable the following policies:

#### Required Policies:
- ✅ **Require a minimum number of reviewers**: 1 reviewer
- ✅ **Check for linked work items**: Recommended
- ✅ **Check for comment resolution**: Recommended
- ✅ **Limit merge types**: Squash merge only (keeps history clean)

#### Optional but Recommended:
- **Build validation**: Will configure in step 4
- **Automatically include reviewers**: Add team leads

---

## 🏗️ 4. Set Up CI/CD Pipelines

### Pipeline 1: CI Validation (Code Quality)

1. Navigate to: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_build
2. Click **"New Pipeline"**
3. Select **"Azure Repos Git"**
4. Select **"GIS - SECURITY_ANALYTICS - DW"** repository
5. Select **"Existing Azure Pipelines YAML file"**
6. Choose path: `/.azuredevops/pipelines/ci-validation.yml`
7. Click **"Continue"**
8. Review the pipeline (validates SQL, Python, YAML)
9. Click **"Run"** to test
10. After success, click **"⋮"** → **"Rename"** → Name it: "CI - Code Validation"
11. Click **"⋮"** → **"Triggers"**
12. Enable **"Continuous integration"** trigger for main branch

### What CI Pipeline Does:
- ✅ Validates SQL syntax
- ✅ Lints Python code
- ✅ Checks YAML formatting
- ✅ Runs basic security checks
- ✅ Validates documentation links

### Pipeline 2: CD Deployment (Snowflake)

1. Click **"New Pipeline"** again
2. Select **"Azure Repos Git"**
3. Select **"GIS - SECURITY_ANALYTICS - DW"** repository
4. Select **"Existing Azure Pipelines YAML file"**
5. Choose path: `/.azuredevops/pipelines/cd-deploy-snowflake.yml`
6. Click **"Continue"**
7. **STOP!** Do not run yet - requires Snowflake credentials
8. Click **"⋮"** → **"Rename"** → Name it: "CD - Deploy to Snowflake"

### Configure Snowflake Credentials (Required):

1. Navigate to: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_settings/
2. Click **"Service connections"** under Pipelines
3. Click **"New service connection"**
4. Search for **"Generic"** service connection
5. Configure:
   - **Server URL**: `https://GenericCorp.snowflakecomputing.com`
   - **Username**: Your Snowflake username
   - **Password/Token**: Your Snowflake password or token
   - **Service connection name**: `SnowflakeConnection`
6. Check **"Grant access permission to all pipelines"**
7. Click **"Save"**

### Create Variable Group for Snowflake:

1. Navigate to: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_library
2. Click **"+ Variable group"**
3. Name it: `Snowflake-Credentials`
4. Add variables:
   - `SNOWFLAKE_ACCOUNT`: `GenericCorp`
   - `SNOWFLAKE_USER`: (your username)
   - `SNOWFLAKE_PASSWORD`: (your password) - **Click lock icon to make secret!**
   - `SNOWFLAKE_ROLE`: `SECURITY_ANALYTICS`
   - `SNOWFLAKE_WAREHOUSE`: `DEV_WH`
   - `SNOWFLAKE_DATABASE`: `DEV_LANDING`
5. Click **"Save"**

### Now You Can Run CD Pipeline:
1. Go back to Pipelines
2. Select "CD - Deploy to Snowflake"
3. Click **"Run pipeline"**
4. Test on a branch first before main

---

## 📋 5. Set Up Work Items and Boards

### Create Areas for Organization

1. Navigate to: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_settings/work
2. Click on **"Project configuration"** → **"Areas"**
3. Create the following areas:
   - **Data Engineering** (for ETL, pipelines, Snowflake work)
   - **Data Quality** (for monitoring, validation, testing)
   - **Dashboards** (for Streamlit, Power BI development)
   - **Security Services** (for integrations with CrowdStrike, Qualys, etc.)
   - **Documentation** (for wiki, guides, reports)
   - **Infrastructure** (for DevOps, CI/CD, automation)

### Create Iterations (Sprints)

1. Click on **"Iterations"**
2. Create sprints (2-week cycles recommended):
   - Sprint 1: (Today's date) to (Today + 14 days)
   - Sprint 2: (Sprint 1 end + 1 day) to (Sprint 1 end + 15 days)
   - Continue for 6 sprints (3 months ahead)

### Import Template Work Items (Optional)

1. Navigate to: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_workitems
2. Click **"Import work items"** (or manually create)
3. The file `.azuredevops/work-items-template.csv` contains template tasks
4. You can import or create manually

---

## 🎨 6. Customize Dashboard

### Create Project Dashboard

1. Navigate to: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_dashboards
2. Click **"New Dashboard"**
3. Name it: "SECURITY_ANALYTICS - Project Overview"
4. Click **"Add Widget"**

### Recommended Widgets:

1. **Markdown Widget** - Project Quick Stats
   - Copy content from README.md Quick Stats table
   - Shows: 550+ objects, 98.1% automation, 94% reduction, etc.

2. **Build History** - CI Pipeline Status
   - Select the "CI - Code Validation" pipeline
   - Shows recent build results

3. **Work Items Query** - Sprint Progress
   - Create query: All work items in current sprint
   - Group by: State (To Do, In Progress, Done)

4. **Deployment Status** - CD Pipeline
   - Select "CD - Deploy to Snowflake" pipeline
   - Shows deployment history

5. **Pull Requests** - Code Review Status
   - Shows active PRs needing review

6. **Repository Stats** - Commit Activity
   - Shows recent commits and contributors

---

## 👥 7. Invite Team Members

### Add Team Members

1. Navigate to: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_settings/teams
2. Click **"Add"** button
3. Enter email addresses of team members:
   - Data Engineers
   - Security Analysts
   - Stakeholders (read-only access)

### Assign Permissions

**For Data Engineers** (Contributor access):
- Can create branches, commits, PRs
- Can run pipelines
- Can create/edit work items

**For Security Analysts** (Contributor access):
- Can review dashboards
- Can create work items for new requirements
- Can comment on PRs

**For Stakeholders** (Stakeholder access - FREE):
- Read-only access to repos
- Can view dashboards
- Can view work items

---

## 📧 8. Notification Settings

### Configure Email Notifications

1. Navigate to: https://dev.azure.com/CompanyX/_usersSettings/notifications
2. Enable notifications for:
   - ✅ Pull request created
   - ✅ Build completed (failures only)
   - ✅ Work item assigned to me
   - ✅ Deployment failed

---

## 🎯 9. Verification Checklist

After completing setup, verify:

- [ ] Project description updated with new professional text
- [ ] Wiki published from `.azuredevops/wiki` folder
- [ ] CI pipeline running on commits
- [ ] CD pipeline configured (credentials set up)
- [ ] Branch policies enabled on main
- [ ] Work item areas created
- [ ] Iterations/sprints configured
- [ ] Dashboard created with widgets
- [ ] Team members invited
- [ ] Notifications configured

---

## 🚀 10. Share With Team

### Email Template for Team Announcement

**Subject**: 🚀 SECURITY_ANALYTICS Data Warehouse - Now on Azure DevOps!

**Body**:

Hi Team,

I'm excited to announce that the SECURITY_ANALYTICS Data Warehouse project is now fully migrated to Azure DevOps with enterprise-grade collaboration features!

**🔗 Quick Access**
- Project: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW
- Wiki: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_wiki
- Boards: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_boards

**📊 Project Highlights**
✅ 550+ database objects deployed
✅ 98.1% automation coverage
✅ 94% reduction in manual operations (1,820 hours saved annually)
✅ 15 security services integrated
✅ 72.3% data quality score with 100% referential integrity

**📚 Documentation**
The complete wiki includes:
- Architecture overview and data model
- Deployment guides
- API documentation
- Troubleshooting guides

**🎯 Next Steps for Team Members**
1. Accept Azure DevOps invitation
2. Review the Wiki for project overview
3. Check out the dashboard for current status
4. Familiarize yourself with the repository structure

**🤝 Collaboration**
- All code changes require PR review (1 reviewer minimum)
- CI pipeline validates code automatically
- CD pipeline deploys to Snowflake after approval

Questions? Check the Wiki or reach out to me directly!

Best regards,
[Your Name]
Lead Data Engineer - SECURITY_ANALYTICS

---

## 📋 Additional Resources

### Azure DevOps Documentation
- [Azure Repos Git Tutorial](https://docs.microsoft.com/en-us/azure/devops/repos/git/gitworkflow)
- [Azure Pipelines Documentation](https://docs.microsoft.com/en-us/azure/devops/pipelines/)
- [Azure Boards Guide](https://docs.microsoft.com/en-us/azure/devops/boards/)

### Project-Specific Files
- Repository README: `/README.md`
- Architecture Diagrams: `/ARCHITECTURE_DIAGRAMS.md`
- Folder Structure: `/FOLDER_STRUCTURE.md`
- Quick Start Guide: `/AZURE_DEVOPS_QUICK_START.md`

---

**Last Updated**: October 23, 2025
**Maintained By**: Lead Data Engineer - SECURITY_ANALYTICS Project
