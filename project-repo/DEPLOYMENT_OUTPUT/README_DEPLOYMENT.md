# Streamlit Apps Deployment Guide

## Overview

This directory contains **18 deployment-ready Streamlit apps** for the SECURITY_ANALYTICS Data Warehouse project. All apps have been processed with the automated deployment script and are ready to be deployed to Snowflake.

**Generated Date**: 2025-10-24
**Script Used**: `03_PYTHON_SCRIPTS/deploy_streamlit_apps.py`
**Target Environment**: DEV_REPORTING.SECURITY_ANALYTICS
**Deployment Status**: ✅ 100% prepared (18/18 apps)

---

## 📁 Generated Files

### Inlined Streamlit Apps (18 files)

| Service | File | Size | Original | Inlined | Common Modules |
|---------|------|------|----------|---------|----------------|
| Ancon | `Ancon_streamlit_app_inlined.py` | 40KB | 1,092 lines | 1,092 lines | No |
| BitSight | `BitSight_streamlit_app_inlined.py` | 34KB | 848 lines | 848 lines | No |
| Cisco_AMP | `Cisco_AMP_streamlit_app_inlined.py` | 39KB | 1,043 lines | 1,043 lines | No |
| Crowdstrike | `Crowdstrike_streamlit_app_inlined.py` | 37KB | 1,027 lines | 1,027 lines | No |
| **CybelAngel** | `CybelAngel_streamlit_app_inlined.py` | 53KB | 840 lines | 1,593 lines | ✅ Yes (+753) |
| Intel_Threats | `Intel_Threats_streamlit_app_inlined.py` | 33KB | 901 lines | 901 lines | No |
| **Leviat** | `Leviat_streamlit_app_inlined.py` | 50KB | 733 lines | 1,486 lines | ✅ Yes (+753) |
| **Proofpoint** | `Proofpoint_streamlit_app_inlined.py` | 54KB | 847 lines | 1,600 lines | ✅ Yes (+753) |
| Qualys | `Qualys_streamlit_app_inlined.py` | 33KB | 913 lines | 913 lines | No |
| **SentinelOne** | `SentinelOne_streamlit_app_inlined.py` | 51KB | 754 lines | 1,507 lines | ✅ Yes (+753) |
| **ServiceNow** | `ServiceNow_streamlit_app_inlined.py` | 50KB | 773 lines | 1,526 lines | ✅ Yes (+753) |
| Sophos | `Sophos_streamlit_app_inlined.py` | 37KB | 1,005 lines | 1,005 lines | No |
| Splunk | `Splunk_streamlit_app_inlined.py` | 41KB | 1,031 lines | 1,031 lines | No |
| Symantec | `Symantec_streamlit_app_inlined.py` | 28KB | 812 lines | 812 lines | No |
| **Tenable** | `Tenable_streamlit_app_inlined.py` | 43KB | 612 lines | 1,365 lines | ✅ Yes (+753) |
| Trellix | `Trellix_streamlit_app_inlined.py` | 36KB | 995 lines | 995 lines | No |
| Zerofox | `Zerofox_streamlit_app_inlined.py` | 32KB | 886 lines | 886 lines | No |
| Zscaler | `Zscaler_streamlit_app_inlined.py` | 42KB | 1,067 lines | 1,067 lines | No |

**Note**: Apps marked with ✅ have had `common/*` modules inlined to make them Snowflake-compatible.

---

## 🚀 Deployment Options

### Option 1: Snowflake UI (Recommended for Quick Testing)

**Best for**: Quick testing, single app deployment

#### Steps:

1. **Open Snowflake UI**
   - Navigate to: https://app.snowflake.com/GenericCorp/crh_edw/
   - Login with your SSO credentials

2. **Navigate to Streamlit**
   - Click on "Data" in the left menu
   - Click on "Streamlit" tab

3. **Create New App**
   - Click "+ Streamlit App" button
   - Configure settings:
     - **App Name**: `{SERVICE}_APP` (e.g., `LEVIAT_APP`)
     - **Location**: `DEV_REPORTING.SECURITY_ANALYTICS`
     - **Warehouse**: `DEV_WH`

4. **Copy Inlined Code**
   - Open the corresponding `{Service}_streamlit_app_inlined.py` file
   - Copy all contents (Ctrl+A, Ctrl+C)
   - Paste into Snowflake editor
   - Click "Run" to test

5. **Add environment.yml** (if needed)
   - Click "+" to add a file
   - Name it `environment.yml`
   - Copy from `07_STREAMLIT_APPS/{Service}/environment.yml`

6. **Deploy**
   - Click "Deploy" button
   - Wait for deployment to complete (~30 seconds)
   - Access your app at the generated URL

#### Example URLs:
```
https://app.snowflake.com/GenericCorp/crh_edw/#/streamlit-apps/DEV_REPORTING.SECURITY_ANALYTICS.LEVIAT_APP
https://app.snowflake.com/GenericCorp/crh_edw/#/streamlit-apps/DEV_REPORTING.SECURITY_ANALYTICS.PROOFPOINT_APP
```

---

### Option 2: Bulk Deployment with SnowSQL

**Best for**: Deploying all 18 apps at once, production deployments

#### Prerequisites:
```bash
# Install SnowSQL
# Download from: https://docs.snowflake.com/en/user-guide/snowsql-install-config

# Configure connection
snowsql --accountname mw76572.east-us-2.azure \
        --username FUAD.ONATE@CompanyX.COM \
        --authenticator externalbrowser
```

#### Deployment Script:

Create a file `deploy_all_apps.sql`:

```sql
-- Create stage for Streamlit files
CREATE STAGE IF NOT EXISTS DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_STAGE
  COMMENT = 'Storage for Streamlit app files';

-- Upload all inlined files (run from DEPLOYMENT_OUTPUT/ directory)
-- Note: Run these PUT commands from SnowSQL, not SQL worksheet
PUT file://Leviat_streamlit_app_inlined.py @DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_STAGE/Leviat/streamlit_app.py AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://Proofpoint_streamlit_app_inlined.py @DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_STAGE/Proofpoint/streamlit_app.py AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
-- ... (repeat for all 18 apps)

-- Create Streamlit apps
CREATE OR REPLACE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.LEVIAT_APP
  ROOT_LOCATION = '@DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_STAGE/Leviat'
  MAIN_FILE = 'streamlit_app.py'
  QUERY_WAREHOUSE = 'DEV_WH'
  COMMENT = 'SECURITY_ANALYTICS validation dashboard for Leviat - IAM monitoring';

CREATE OR REPLACE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.PROOFPOINT_APP
  ROOT_LOCATION = '@DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_STAGE/Proofpoint'
  MAIN_FILE = 'streamlit_app.py'
  QUERY_WAREHOUSE = 'DEV_WH'
  COMMENT = 'SECURITY_ANALYTICS validation dashboard for Proofpoint - Email security';

-- ... (repeat for all 18 apps)
```

#### Run Deployment:
```bash
# Change to deployment directory
cd DEPLOYMENT_OUTPUT/

# Execute deployment script
snowsql -f deploy_all_apps.sql
```

---

### Option 3: Python API Deployment (Future Enhancement)

The `deploy_streamlit_apps.py` script currently generates inlined files. Full automation would require:

1. **Snowflake Python API** for CREATE STREAMLIT
2. **File upload via stage** using Python
3. **Verification and health checks**

This is a future enhancement - for now, use Options 1 or 2.

---

## 🔍 Verification

### Check Deployed Apps

```sql
-- List all Streamlit apps in SECURITY_ANALYTICS
SHOW STREAMLITS IN SCHEMA DEV_REPORTING.SECURITY_ANALYTICS;

-- Check specific app details
DESCRIBE STREAMLIT DEV_REPORTING.SECURITY_ANALYTICS.LEVIAT_APP;

-- View app URL
SELECT
    NAME,
    DATABASE_NAME || '.' || SCHEMA_NAME AS LOCATION,
    'https://app.snowflake.com/' ||
    CURRENT_ACCOUNT_NAME() || '/#/streamlit-apps/' ||
    DATABASE_NAME || '.' || SCHEMA_NAME || '.' || NAME AS URL
FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()));
```

### Test App Functionality

1. Click on the app URL
2. Verify that:
   - ✅ App loads without errors
   - ✅ Common styles are applied (GenericCorp branding)
   - ✅ Data queries execute successfully
   - ✅ Filters and date ranges work
   - ✅ Export CSV buttons function
   - ✅ Charts and visualizations render

---

## 📊 Deployment Results

### Test Runs

| Run | Timestamp | Services | Success | Failed | Rate |
|-----|-----------|----------|---------|--------|------|
| 1 | 2025-10-24 20:01:29 | 1 (Leviat) | 1 | 0 | 100% |
| 2 | 2025-10-24 20:02:18 | 1 (Leviat) | 1 | 0 | 100% |
| 3 | 2025-10-24 20:02:46 | 18 (All) | 18 | 0 | 100% |

**Final Result**: ✅ All 18 apps prepared successfully

Detailed results are available in:
- `deployment_results_20251024_200129.json`
- `deployment_results_20251024_200218.json`
- `deployment_results_20251024_200246.json`

---

## 🎯 Recommended Deployment Order

### Phase 1: Critical Apps (Deploy First - 30 mins)
1. **Splunk** - SIEM monitoring
2. **Crowdstrike** - EDR threats
3. **ServiceNow** - ITSM tickets
4. **Qualys** - Vulnerability scanning
5. **Zscaler** - Cloud security

### Phase 2: Expanded Apps (Deploy Next - 45 mins)
6. **Leviat** - IAM monitoring (6 tabs)
7. **Proofpoint** - Email security (6 tabs)
8. **SentinelOne** - Endpoint protection (6 tabs)
9. **CybelAngel** - External threats (6 tabs)
10. **BitSight** - Security ratings (7 tabs)
11. **Tenable** - Vuln management (6 tabs)

### Phase 3: Remaining Apps (Deploy Last - 30 mins)
12. **Sophos** - Endpoint protection
13. **Trellix** - EDR
14. **Symantec** - Antivirus
15. **Cisco_AMP** - Malware protection
16. **Zerofox** - Digital risk
17. **Intel_Threats** - Threat intel
18. **Ancon** - Security analytics

**Total Estimated Time**: ~2 hours for all 18 apps via UI

---

## ❓ Troubleshooting

### Common Issues

#### Issue 1: Import Errors
**Error**: `ModuleNotFoundError: No module named 'common'`
**Solution**: Ensure you're using the `*_inlined.py` files, not the originals from `07_STREAMLIT_APPS/`

#### Issue 2: Connection Errors
**Error**: `Session does not exist`
**Solution**: Apps must run in Snowflake environment. Test queries:
```python
session = get_active_session()
```

#### Issue 3: Missing Tables/Views
**Error**: `Object does not exist: DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_*`
**Solution**: Run prerequisite scripts:
```bash
cd 01_SQL_SCRIPTS
snowsql -f 01_Prerequisites/00_PREREQUISITES_CHECK.sql
```

#### Issue 4: Warehouse Not Found
**Error**: `Warehouse 'DEV_WH' does not exist`
**Solution**: Create warehouse or update app to use existing one:
```sql
CREATE WAREHOUSE IF NOT EXISTS DEV_WH
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE;
```

---

## 📚 Additional Resources

- **Snowflake Streamlit Docs**: https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit
- **Common Modules README**: `07_STREAMLIT_APPS/common/README.md`
- **Deployment Script**: `03_PYTHON_SCRIPTS/deploy_streamlit_apps.py`
- **Original Apps**: `07_STREAMLIT_APPS/{Service}/streamlit_app.py`

---

## 🔄 Updating Apps

When you make changes to the original apps in `07_STREAMLIT_APPS/`:

1. **Regenerate inlined files**:
   ```bash
   cd 03_PYTHON_SCRIPTS
   python deploy_streamlit_apps.py --services Leviat ServiceNow
   ```

2. **Redeploy to Snowflake**:
   - Option A: Copy/paste new inlined code in Snowflake UI
   - Option B: Re-run SnowSQL PUT + CREATE STREAMLIT

3. **Commit changes**:
   ```bash
   git add DEPLOYMENT_OUTPUT/
   git commit -m "chore: update inlined Streamlit apps"
   git push
   ```

---

## ✅ Deployment Checklist

- [ ] All 18 inlined files reviewed
- [ ] Snowflake connection tested (SSO works)
- [ ] DEV_REPORTING.SECURITY_ANALYTICS schema exists
- [ ] DEV_WH warehouse is available
- [ ] Required tables/views exist (run prerequisites)
- [ ] Phase 1 apps deployed (5 critical apps)
- [ ] Phase 2 apps deployed (6 expanded apps)
- [ ] Phase 3 apps deployed (7 remaining apps)
- [ ] All apps tested and functional
- [ ] App URLs documented
- [ ] Stakeholders notified

---

**Deployment Prepared By**: Data Engineering Team
**Automation Script**: Claude Code
**Date**: 2025-10-24
**Contact**: FUAD.ONATE@CompanyX.COM
