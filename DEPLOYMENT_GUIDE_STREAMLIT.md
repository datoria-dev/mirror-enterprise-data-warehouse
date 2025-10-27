# Streamlit Apps Deployment Guide

**Created**: 2025-10-25
**Purpose**: Complete guide for deploying 18 SECURITY_ANALYTICS Streamlit apps to Snowflake
**Location**: `C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\`

---

## 📋 Overview

This guide covers the automated deployment of 18 Streamlit security analytics applications to Snowflake using SnowSQL and SSO (Okta) authentication.

### Apps to Deploy (18 Total)

**Priority 1 - Critical Apps** (3):
1. Symantec - Endpoint Security Dashboard
2. Trellix - Security Analytics
3. Crowdstrike - Falcon Dashboard

**Priority 2 - Core Security** (4):
4. SentinelOne - Endpoint Protection
5. Sophos - Security Dashboard
6. Qualys - Vulnerability Management
7. Splunk - Security Analytics

**Priority 3 - Extended Security** (6):
8. Proofpoint - Email Security
9. CybelAngel - Digital Risk Protection
10. Zerofox - Digital Risk Protection
11. Zscaler - Cloud Security
12. Cisco_AMP - Malware Protection
13. Intel_Threats - Threat Intelligence

**Priority 4 - Supporting Tools** (5):
14. BitSight - Security Ratings
15. ServiceNow - Security Operations
16. Leviat - Security Analytics
17. Ancon - Security Monitoring
18. Tenable - Vulnerability Management

---

## 🚀 Quick Start (Recommended)

### Step 1: Test SnowSQL Connection

```batch
cd C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV
.\test_snowsql_connection.bat
```

This verifies:
- ✅ SnowSQL is installed
- ✅ SSO (Okta) authentication works
- ✅ Access to DEV_TRANSFORMATION database
- ✅ Access to METADATA schema

### Step 2: Deploy Priority 1 Apps (Test Deployment)

```batch
.\deploy_apps.bat
```

**When prompted, choose option 1**:
- Deploys: Symantec, Trellix, Crowdstrike
- Tests deployment process with 3 critical apps
- Takes ~5-10 minutes

### Step 3: Verify Deployment

```batch
.\verify_apps.bat
```

This shows:
- Which apps are deployed ✓
- Which apps are missing ✗
- Deployment completion percentage

### Step 4: Deploy Remaining Apps

Run `.\deploy_apps.bat` again and choose:
- **Option 2**: Deploy Priority 2 apps (SentinelOne, Sophos, Qualys, Splunk)
- **Option 3**: Deploy Priority 3 apps (Proofpoint, CybelAngel, Zerofox, etc.)
- **Option 4**: Deploy Priority 4 apps (BitSight, ServiceNow, Leviat, etc.)

Or:
- **Option 5**: Deploy ALL remaining apps at once

---

## 📁 File Structure

```
Snowflake_ITSECKPI_Project_DEV/
├── 02_PYTHON_SCRIPTS/
│   ├── deploy_streamlit_apps.py      # Main deployment script
│   └── verify_deployments.py         # Verification script
│
├── 13_STREAMLIT_COMPLETE/            # All apps ready for deployment
│   ├── Symantec/streamlit_app.py
│   ├── Trellix/streamlit_app.py
│   ├── Crowdstrike/streamlit_app.py
│   └── ... (15 more apps)
│
├── deploy_apps.bat                   # Quick deployment runner
├── verify_apps.bat                   # Quick verification runner
├── snowflake_config.json             # Snowflake connection config
└── DEPLOYMENT_GUIDE_STREAMLIT.md     # This file
```

---

## 🔧 Detailed Deployment Process

### Automated Deployment (`deploy_streamlit_apps.py`)

**What it does**:

1. **Loads Configuration** - Reads `snowflake_config.json`
2. **Creates Stage** - Creates `STREAMLIT_APPS_STAGE` in Snowflake (if not exists)
3. **Uploads Apps** - Uploads each `streamlit_app.py` to the stage
4. **Creates Streamlit Apps** - Creates Snowflake Streamlit objects
5. **Generates Logs** - Saves deployment log with results

**For each app**:
```
[Step 1/4] Checking app files...
  ✓ App files found

[Step 2/4] Uploading to Snowflake stage...
  Uploading Symantec/streamlit_app.py...
    ✓ File uploaded successfully

[Step 3/4] Checking for existing Streamlit app...
  Dropping existing app...
  ✓ Ready to create app

[Step 4/4] Creating Streamlit app...
  Creating Streamlit app...
  ✓ Streamlit app created: STREAMLIT_SYMANTEC

✓ Symantec deployed successfully in 12.3s
```

---

## 🎯 Deployment Options

### Option 1: Priority-Based Deployment (Recommended)

Deploy apps in stages based on priority:

**Priority 1 First** (3 apps, ~10 min):
```batch
.\deploy_apps.bat
# Choose option 1
```

**Then Priority 2** (4 apps, ~12 min):
```batch
.\deploy_apps.bat
# Choose option 2
```

**Then Priority 3** (6 apps, ~15 min):
```batch
.\deploy_apps.bat
# Choose option 3
```

**Finally Priority 4** (5 apps, ~12 min):
```batch
.\deploy_apps.bat
# Choose option 4
```

### Option 2: Deploy All at Once

Deploy all 18 apps in one batch (~45 min):
```batch
.\deploy_apps.bat
# Choose option 5
```

---

## 📊 Deployment Logs

Each deployment creates a detailed JSON log:

**Location**: `deployment_log_YYYYMMDD_HHMMSS.json`

**Example**:
```json
{
  "timestamp": "2025-10-25T14:30:22.123456",
  "total_apps": 3,
  "successful": 3,
  "failed": 0,
  "deployments": [
    {
      "app_name": "Symantec",
      "start_time": "2025-10-25T14:30:25.000000",
      "end_time": "2025-10-25T14:30:37.300000",
      "duration_seconds": 12.3,
      "success": true,
      "steps": {
        "check_files": true,
        "upload": true,
        "drop_existing": true,
        "create_app": true
      },
      "error": null
    },
    ...
  ]
}
```

---

## ✅ Verification Process

### Manual Verification (Snowflake Web UI)

1. **Login to Snowflake**:
   - Account: GenericCorp-CRH_EDW
   - User: fuad.onate@CompanyX.com
   - Authentication: SSO (Okta)

2. **Navigate to Streamlit Apps**:
   - Left menu → Data → Streamlit
   - Database: DEV_TRANSFORMATION
   - Schema: METADATA

3. **Check Deployed Apps**:
   - Look for apps named: `STREAMLIT_SYMANTEC`, `STREAMLIT_TRELLIX`, etc.
   - Click to open and test functionality

### Automated Verification

```batch
.\verify_apps.bat
```

**Output**:
```
==============================================================
STREAMLIT APPS DEPLOYMENT VERIFICATION
==============================================================

[Loading Configuration]
✓ Configuration loaded
  Database: DEV_TRANSFORMATION
  Schema: METADATA

[Checking Deployed Apps]
✓ Found 18 deployed Streamlit apps

==============================================================
DEPLOYMENT STATUS
==============================================================
  ✓ SYMANTEC
  ✓ TRELLIX
  ✓ CROWDSTRIKE
  ✓ SENTINELONE
  ✓ SOPHOS
  ✓ QUALYS
  ✓ SPLUNK
  ✓ PROOFPOINT
  ✓ CYBELANGEL
  ✓ ZEROFOX
  ✓ ZSCALER
  ✓ CISCO_AMP
  ✓ BITSIGHT
  ✓ INTEL_THREATS
  ✓ SERVICENOW
  ✓ LEVIAT
  ✓ ANCON
  ✓ TENABLE

==============================================================
SUMMARY
==============================================================

Expected apps: 18
Deployed: 18 ✓
Missing: 0 ✗

Deployment completion: 100.0%

✓ All apps successfully deployed!
```

---

## 🧪 Testing Deployed Apps

### Test Checklist (For Each App)

1. **App Opens**:
   - Navigate to app in Snowflake
   - Click to open
   - ✓ App loads without errors

2. **Tabs Work**:
   - Click through all tabs
   - ✓ Each tab displays content
   - ✓ No errors in console

3. **Download Buttons** (if applicable):
   - Click "Download CSV" buttons
   - ✓ CSV file downloads
   - ✓ File contains data

4. **Alert Thresholds** (if applicable):
   - Check for colored alerts (error, warning, success)
   - ✓ Alerts display with correct colors
   - ✓ Thresholds trigger appropriately

5. **Refresh Button**:
   - Click "Refresh Now" button
   - ✓ App refreshes without `st.experimental_rerun` error

### Apps with Special Features

**Apps with Download Buttons** (11 total):
- Symantec (3 buttons)
- Crowdstrike (7 buttons)
- Leviat (7 buttons)
- ServiceNow (4 buttons)
- CybelAngel, Proofpoint, SentinelOne, Splunk, Zscaler (2 each)
- Ancon, Sophos (1 each)

**Apps with Alert Thresholds** (8 total):
- Symantec (2 alerts)
- Crowdstrike (4 alerts)
- Leviat (4 alerts)
- ServiceNow (4 alerts)
- CybelAngel, Proofpoint, SentinelOne, Splunk (2 each)

---

## 🔍 Troubleshooting

### Issue: "SnowSQL not found"

**Error**:
```
SnowSQL not found at: C:\Program Files\Snowflake SnowSQL\snowsql.exe
```

**Solution**:
```batch
# Run as Administrator
.\reinstall_snowsql.bat
```

---

### Issue: "SSO authentication failed"

**Error**:
```
Connection timeout - SSO authentication may have failed
```

**Solution**:
1. Ensure browser opens for Okta login
2. Complete Okta authentication
3. Check network connection
4. Retry deployment

---

### Issue: "Upload failed"

**Error**:
```
✗ Upload failed: Access denied
```

**Solution**:
1. Check Snowflake permissions:
   - Role: DEV_DEVELOPER
   - Can create stages and Streamlit apps
2. Request permissions from Snowflake admin if needed

---

### Issue: "App already exists"

**Error**:
```
CREATE STREAMLIT failed: Object already exists
```

**Solution**:
The deployment script automatically drops existing apps. If error persists:

```sql
-- Manually drop the app in Snowflake
DROP STREAMLIT STREAMLIT_SYMANTEC;

-- Then re-run deployment
.\deploy_apps.bat
```

---

### Issue: "Some apps failed to deploy"

**Check deployment log**:
```
deployment_log_YYYYMMDD_HHMMSS.json
```

**Look for**:
- `"success": false`
- `"error"` field contains reason

**Common errors**:
- Permission denied → Request Snowflake permissions
- Upload timeout → Check network connection, retry
- Invalid file → Verify `streamlit_app.py` exists and is valid

---

## 🎛️ Configuration

### Snowflake Connection (`snowflake_config.json`)

```json
{
  "user": "fuad.onate@CompanyX.com",
  "authenticator": "externalbrowser",
  "account": "GenericCorp-CRH_EDW",
  "warehouse": "DEV_WH",
  "database": "DEV_TRANSFORMATION",
  "schema": "METADATA",
  "role": "DEV_DEVELOPER"
}
```

**Change these if deploying to different environment**:
- `database`: Target database
- `schema`: Target schema
- `warehouse`: Compute warehouse to use
- `role`: Snowflake role with permissions

---

## 📝 Best Practices

### Pre-Deployment

✅ **DO**:
- Test SnowSQL connection first
- Start with Priority 1 apps (test with small batch)
- Verify one app works before deploying all
- Keep deployment logs for troubleshooting

❌ **DON'T**:
- Deploy all apps without testing one first
- Skip connection verification
- Ignore deployment errors
- Delete deployment logs

### During Deployment

✅ **DO**:
- Monitor progress in console
- Keep browser open for SSO re-authentication
- Wait for each deployment to complete
- Check deployment log for errors

❌ **DON'T**:
- Close terminal during deployment
- Cancel SSO authentication
- Deploy duplicate apps simultaneously

### Post-Deployment

✅ **DO**:
- Run verification script
- Test each app in Snowflake UI
- Test download buttons and alerts
- Document any issues

❌ **DON'T**:
- Assume all apps work without testing
- Skip verification
- Ignore failed deployments

---

## 🚀 Complete Deployment Workflow

### Day 1: Initial Deployment (Priority 1)

**Morning**:
```batch
# Test connection
.\test_snowsql_connection.bat
```

**Mid-morning**:
```batch
# Deploy Priority 1 apps (Symantec, Trellix, Crowdstrike)
.\deploy_apps.bat
# Choose option 1
```

**Afternoon**:
```batch
# Verify deployment
.\verify_apps.bat

# Test apps in Snowflake UI
# - Open each app
# - Test download buttons
# - Test alerts
# - Test refresh
```

### Day 2: Expand Deployment (Priorities 2-4)

**Morning**:
```batch
# Deploy Priority 2 apps
.\deploy_apps.bat
# Choose option 2

# Verify
.\verify_apps.bat
```

**Afternoon**:
```batch
# Deploy Priority 3 apps
.\deploy_apps.bat
# Choose option 3

# Deploy Priority 4 apps
.\deploy_apps.bat
# Choose option 4

# Final verification
.\verify_apps.bat
```

**End of Day**:
- Review deployment logs
- Test all 18 apps
- Document any issues
- Push to Azure DevOps

---

## 📊 Expected Timeline

### Individual App Deployment
- Check files: ~1 second
- Upload to stage: ~3-5 seconds
- Create app: ~5-8 seconds
- **Total per app**: ~10-15 seconds

### Batch Deployment Times
- **Priority 1** (3 apps): ~5 minutes
- **Priority 2** (4 apps): ~10 minutes
- **Priority 3** (6 apps): ~15 minutes
- **Priority 4** (5 apps): ~12 minutes
- **All 18 apps**: ~45 minutes (if deployed together)

**Note**: Times include SSO authentication pauses between apps

---

## 🔗 Related Documentation

- [README_AUTOMATION_SCRIPTS.md](README_AUTOMATION_SCRIPTS.md) - Automation scripts overview
- [snowflake_config.json](snowflake_config.json) - Connection configuration
- Deployment logs: `deployment_log_*.json`

---

## 📞 Support

### Common Commands

**Test connection**:
```batch
.\test_snowsql_connection.bat
```

**Deploy apps**:
```batch
.\deploy_apps.bat
```

**Verify deployment**:
```batch
.\verify_apps.bat
```

**Check SnowSQL version**:
```batch
snowsql --version
```

### Getting Help

**For deployment issues**:
1. Check deployment log: `deployment_log_*.json`
2. Run verification: `.\verify_apps.bat`
3. Check Snowflake permissions
4. Review error messages in console

**For app issues**:
1. Open app in Snowflake UI
2. Check browser console for errors
3. Test download buttons manually
4. Check data source connectivity

---

**Version**: 1.0
**Last Updated**: 2025-10-25
**Maintained By**: Fuad Onate
