# Streamlit Apps Deployment Guide

**Last Updated**: 2025-10-25
**Author**: Fuad Onate
**Environment**: DEV_REPORTING.SECURITY_ANALYTICS

---

## Table of Contents

1. [Overview](#overview)
2. [File Locations in Snowflake](#file-locations-in-snowflake)
3. [Deployment Process](#deployment-process)
4. [Known Issues & Fixes](#known-issues--fixes)
5. [Testing & Verification](#testing--verification)
6. [Troubleshooting](#troubleshooting)
7. [Azure DevOps Integration](#azure-devops-integration)

---

## Overview

### Deployed Applications (18 Total)

All Streamlit apps are deployed to:
- **Database**: `DEV_REPORTING`
- **Schema**: `SECURITY_ANALYTICS`
- **Stage**: `STREAMLIT_APPS_STAGE`

#### Priority 1 - Critical Apps (3)
1. **Symantec** - Endpoint Security Dashboard
2. **Trellix** - Security Analytics
3. **Crowdstrike** - Falcon Dashboard

#### Priority 2 - Core Security (4)
4. **SentinelOne** - Endpoint Protection
5. **Sophos** - Security Dashboard
6. **Qualys** - Vulnerability Management
7. **Splunk** - Security Analytics

#### Priority 3 - Extended Security (6)
8. **Proofpoint** - Email Security
9. **CybelAngel** - Digital Risk Protection
10. **Zerofox** - Digital Risk Protection
11. **Zscaler** - Cloud Security
12. **Cisco_AMP** - Malware Protection
13. **Intel_Threats** - Threat Intelligence

#### Priority 4 - Supporting Tools (5)
14. **BitSight** - Security Ratings
15. **ServiceNow** - Security Operations
16. **Leviat** - Security Analytics
17. **Ancon** - Security Monitoring
18. **Tenable** - Vulnerability Management

---

## File Locations in Snowflake

### Stage Structure

```
@DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_APPS_STAGE/
├── Symantec/
│   ├── streamlit_app.py
│   └── environment.yml
├── Trellix/
│   ├── streamlit_app.py
│   └── environment.yml
├── Crowdstrike/
│   ├── streamlit_app.py
│   └── environment.yml
... (for all 18 apps)
```

### How to View Files in Snowflake UI

1. Login to Snowflake: https://app.snowflake.com
2. Navigate to: **Data** → **Databases**
3. Select: **DEV_REPORTING** → **SECURITY_ANALYTICS** → **Stages**
4. Open: **STREAMLIT_APPS_STAGE**
5. Browse folders by app name

### Check Files via SnowSQL

```sql
-- List all files
LIST @STREAMLIT_APPS_STAGE;

-- List files for specific app
LIST @STREAMLIT_APPS_STAGE/Symantec/;

-- Show stage details
SHOW STAGES LIKE 'STREAMLIT_APPS_STAGE';
```

### Automated Check

```bash
cd C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV
.\check_stage.bat
```

---

## Deployment Process

### Prerequisites

- ✅ SnowSQL installed
- ✅ SSO (Okta) authentication configured
- ✅ Access to DEV_REPORTING database
- ✅ DEV_DEVELOPER role permissions

### Deployment Steps

#### Step 1: Fix Known Issues

```bash
.\fix_apps.bat
```

This fixes:
- `np.random.randn()` → `np.random.standard_normal()` (Snowflake compatibility)
- Download button missing `key` parameters

#### Step 2: Deploy Apps

```bash
.\deploy_apps.bat
```

**Options**:
1. Deploy Priority 1 (3 apps) - Recommended for testing
2. Deploy Priority 2 (4 apps)
3. Deploy Priority 3 (6 apps)
4. Deploy Priority 4 (5 apps)
5. Deploy ALL apps (18 total) - Recommended after testing

**What happens**:
- ⏳ Single SSO authentication (browser opens once)
- 📤 Uploads both `streamlit_app.py` and `environment.yml`
- 🔄 Drops existing app (if exists)
- ✨ Creates new Streamlit app
- 📊 Real-time progress counter
- 📁 Generates deployment logs

**Duration**:
- Priority 1 (3 apps): ~30 seconds
- All apps (18 total): ~2 minutes

#### Step 3: Verify Deployment

```bash
.\verify_apps.bat
```

Shows:
- ✓ Which apps are deployed
- ✗ Which apps are missing
- Deployment completion percentage

#### Step 4: Analyze Logs

```bash
.\analyze_logs.bat
```

**Options**:
1. Analyze latest deployment
2. Compare multiple deployments
3. Export summary to markdown
4. Show all log files

---

## Known Issues & Fixes

### Issue 1: `np.random.randn()` AttributeError

**Error**:
```python
AttributeError: 'function' object has no attribute 'randn'
Traceback:
File "/tmp/appRoot/streamlit_app.py", line 943, in <module>
    'Protection %': 85 + np.random.randn(30) * 2
```

**Cause**: Snowflake Streamlit doesn't support `numpy.random.randn()`

**Fix**: Replace with `np.random.standard_normal()`

```python
# Before (causes error)
np.random.randn(30)

# After (works in Snowflake)
np.random.standard_normal(30)
```

**Automated Fix**:
```bash
.\fix_apps.bat
```

### Issue 2: Download Buttons Not Working

**Symptom**: Button appears but doesn't download CSV file

**Cause**: Missing unique `key` parameter required by Snowflake

**Fix**: Add unique key to each download button

```python
# Before (doesn't work)
st.download_button(
    label="Download CSV",
    data=csv_data,
    file_name="data.csv"
)

# After (works)
st.download_button(
    label="Download CSV",
    data=csv_data,
    file_name="data.csv",
    key="download_symantec_coverage_btn"  # ← Added unique key
)
```

**Automated Fix**:
```bash
.\fix_apps.bat
```

### Issue 3: Refresh Button Errors

**Error**: `st.experimental_rerun()` not found

**Fix**: Already applied - using `st.rerun()` instead

---

## Testing & Verification

### Manual Testing in Snowflake UI

1. **Access Apps**:
   - Login: https://app.snowflake.com
   - Navigate: **Data** → **Streamlit**
   - Database: **DEV_REPORTING**
   - Schema: **SECURITY_ANALYTICS**

2. **Test Each App**:
   - ✓ App loads without errors
   - ✓ Tabs navigate correctly
   - ✓ Filters work properly
   - ✓ Refresh button works (no `np.random` error)
   - ✓ Download buttons download CSV files
   - ✓ Alert thresholds display with correct colors

3. **Test Download Buttons** (11 apps have them):
   - Symantec (3 download buttons)
   - Crowdstrike (7 download buttons)
   - Leviat (7 download buttons)
   - ServiceNow (4 download buttons)
   - Other apps (1-2 download buttons each)

4. **Test Alert Thresholds** (8 apps have them):
   - Symantec (2 alerts)
   - Crowdstrike (4 alerts)
   - Leviat (4 alerts)
   - ServiceNow (4 alerts)
   - Others (2 alerts each)

### Automated Verification

```bash
# Verify deployment status
.\verify_apps.bat

# Check stage files
.\check_stage.bat

# Analyze deployment logs
.\analyze_logs.bat
```

---

## Troubleshooting

### Problem: App has syntax errors after deployment

**Check**: Did you run the fix script before deploying?

**Solution**:
```bash
.\fix_apps.bat
.\deploy_apps.bat  # Redeploy
```

### Problem: Download button appears but doesn't download

**Cause**: Missing unique `key` parameter

**Solution**:
```bash
.\fix_apps.bat  # Adds keys to all download buttons
.\deploy_apps.bat  # Redeploy
```

### Problem: `np.random.randn()` error when using filters

**Cause**: Snowflake doesn't support this numpy function

**Solution**:
```bash
.\fix_apps.bat  # Replaces with standard_normal()
.\deploy_apps.bat  # Redeploy
```

### Problem: Multiple SSO authentication prompts

**Cause**: Using old deployment script

**Solution**: Use the enhanced script (already configured):
```bash
.\deploy_apps.bat  # Uses single SSO session
```

### Problem: Can't find files in Snowflake stage

**Check**:
```bash
.\check_stage.bat
```

Or in Snowflake UI:
```sql
LIST @STREAMLIT_APPS_STAGE;
LIST @STREAMLIT_APPS_STAGE/Symantec/;
```

---

## Azure DevOps Integration

### Repository Information

**Azure DevOps**:
- Organization: `CompanyX`
- Project: `GIS - SECURITY_ANALYTICS - DW`
- Repository: `GIS - SECURITY_ANALYTICS - DW`
- URL: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_git/GIS%20-%20ITSECKPI%20-%20DW

**GitHub Mirror** (if configured):
- Repository: `fos-CompanyX/snowflake-SECURITY_ANALYTICS-datawarehouse-dev`
- URL: https://github.com/fos-CompanyX/snowflake-SECURITY_ANALYTICS-datawarehouse-dev

### Push to Azure DevOps

```bash
# Add changes
git add .

# Commit
git commit -m "docs: add Streamlit deployment guide and automation scripts"

# Push to Azure DevOps
git push azure main
```

### Upload to Wiki

The Azure DevOps project has a Wiki for documentation.

**Manual Upload**:
1. Navigate to Wiki in Azure DevOps
2. Create new page: "Streamlit Deployment"
3. Copy content from `WIKI_08_STREAMLIT_DEPLOYMENT.md`
4. Save and publish

**Automated Upload** (if configured):
```bash
# See: AZURE_DEVOPS_WIKI_UPLOAD_GUIDE.md
.\upload_wiki.ps1
```

---

## Deployment Logs

All deployments are logged in: `deployment_logs/`

**Files generated per deployment**:
- `deployment_YYYYMMDD_HHMMSS.log` - Human-readable log
- `deployment_YYYYMMDD_HHMMSS.json` - Structured data
- `deployment_YYYYMMDD_HHMMSS.sql` - SQL script executed

**Log Analysis**:
```bash
.\analyze_logs.bat
```

**Options**:
1. Analyze latest - Detailed breakdown
2. Compare multiple - Compare last 5 deployments
3. Export summary - Creates markdown summary
4. Show all logs - Lists all log files

---

## Quick Reference

### Commands

| Command | Description |
|---------|-------------|
| `.\fix_apps.bat` | Fix known issues in apps |
| `.\deploy_apps.bat` | Deploy apps to Snowflake |
| `.\verify_apps.bat` | Verify deployment status |
| `.\check_stage.bat` | Check stage files in Snowflake |
| `.\analyze_logs.bat` | Analyze deployment logs |

### File Locations

| Location | Purpose |
|----------|---------|
| `13_STREAMLIT_COMPLETE/` | Source code (local) |
| `@STREAMLIT_APPS_STAGE/` | Uploaded files (Snowflake) |
| `DEV_REPORTING.SECURITY_ANALYTICS` | Deployed apps (Snowflake) |
| `deployment_logs/` | Deployment logs (local) |

### Snowflake Locations

| Resource | Path |
|----------|------|
| Database | `DEV_REPORTING` |
| Schema | `SECURITY_ANALYTICS` |
| Stage | `STREAMLIT_APPS_STAGE` |
| Apps | `STREAMLIT_<APP_NAME>` |

---

## Contact & Support

**Data Engineer**: Fuad Onate (fuad.onate@CompanyX.com)

**For Issues**:
1. Check deployment logs: `.\analyze_logs.bat`
2. Review this guide's troubleshooting section
3. Contact data engineering team

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-10-25 | 1.0 | Initial deployment guide |

---

**Note**: This guide is for DEV environment. Production deployment process may differ and require additional approvals.
