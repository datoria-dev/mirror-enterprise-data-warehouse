# Production Streamlit Apps - Git Deployment

## Overview

This directory contains **production-ready Streamlit apps** with all dependencies inlined, ready for Git-based deployment to Snowflake.

**Created**: 2025-10-24
**Apps**: 18 security monitoring dashboards
**Status**: ✅ Ready for Git deployment

## Directory Structure

```
08_STREAMLIT_APPS_PROD/
├── Ancon/
│   └── streamlit_app.py         # 1,092 lines
├── BitSight/
│   └── streamlit_app.py         # 848 lines
├── Cisco_AMP/
│   └── streamlit_app.py         # 1,043 lines
├── Crowdstrike/
│   └── streamlit_app.py         # 1,027 lines
├── CybelAngel/
│   └── streamlit_app.py         # 1,593 lines (expanded)
├── Intel_Threats/
│   └── streamlit_app.py         # 901 lines
├── Leviat/
│   └── streamlit_app.py         # 1,486 lines (expanded)
├── Proofpoint/
│   └── streamlit_app.py         # 1,600 lines (expanded)
├── Qualys/
│   └── streamlit_app.py         # 913 lines
├── SentinelOne/
│   └── streamlit_app.py         # 1,507 lines (expanded)
├── ServiceNow/
│   └── streamlit_app.py         # 1,526 lines (expanded)
├── Sophos/
│   └── streamlit_app.py         # 1,005 lines
├── Splunk/
│   └── streamlit_app.py         # 1,031 lines
├── Symantec/
│   └── streamlit_app.py         # 812 lines
├── Tenable/
│   └── streamlit_app.py         # 1,365 lines (expanded)
├── Trellix/
│   └── streamlit_app.py         # 995 lines
├── Zerofox/
│   └── streamlit_app.py         # 886 lines
└── Zscaler/
    └── streamlit_app.py         # 1,067 lines
```

## Key Features

### ✅ Production Ready
- All `common/*` modules inlined
- No external dependencies
- Self-contained Python files
- GenericCorp branding included
- Error handling built-in

### 📊 App Categories

#### Expanded Apps (6) - With Advanced Features
- **Leviat**: IAM monitoring (6 tabs)
- **ServiceNow**: ITSM integration (7 tabs)
- **CybelAngel**: Data leak detection (6 tabs)
- **Proofpoint**: Email security (6 tabs)
- **SentinelOne**: EDR protection (6 tabs)
- **Tenable**: Vulnerability management (6 tabs)

#### Standard Apps (12) - Core Functionality
- All others: 4-5 tabs with essential monitoring

## Deployment Instructions

### Option 1: Git-Based Deployment (Recommended)

#### Step 1: Push to Azure DevOps
```bash
git add 08_STREAMLIT_APPS_PROD/
git commit -m "feat: add production Streamlit apps for Git deployment"
git push azure main
```

#### Step 2: Connect in Snowflake UI

1. **Navigate to Streamlit App**
   ```
   https://app.snowflake.com/GenericCorp/crh_edw/#/streamlit-apps
   ```

2. **For Each App:**
   - Click on the app (e.g., `LEVIAT_APP`)
   - Click "Connect Git Repository" button
   - Enter repository details:
     - **Repository URL**: `https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_git/GIS%20-%20ITSECKPI%20-%20DW`
     - **Branch**: `main`
     - **Path**: `08_STREAMLIT_APPS_PROD/Leviat/streamlit_app.py`
   - Click "Connect"

3. **Verify Connection**
   - App should reload with Git icon
   - Changes in Git auto-deploy

### Option 2: Manual Copy-Paste

1. Open app in Snowflake UI
2. Click "Edit" button
3. Delete existing content
4. Copy content from `08_STREAMLIT_APPS_PROD/{Service}/streamlit_app.py`
5. Paste and Save
6. Run app

## Git Connection URLs

Use these paths when connecting apps to Git:

| App | Git Path |
|-----|----------|
| ANCON_APP | `08_STREAMLIT_APPS_PROD/Ancon/streamlit_app.py` |
| BITSIGHT_APP | `08_STREAMLIT_APPS_PROD/BitSight/streamlit_app.py` |
| CISCO_AMP_APP | `08_STREAMLIT_APPS_PROD/Cisco_AMP/streamlit_app.py` |
| CROWDSTRIKE_APP | `08_STREAMLIT_APPS_PROD/Crowdstrike/streamlit_app.py` |
| CYBELANGEL_APP | `08_STREAMLIT_APPS_PROD/CybelAngel/streamlit_app.py` |
| INTEL_THREATS_APP | `08_STREAMLIT_APPS_PROD/Intel_Threats/streamlit_app.py` |
| LEVIAT_APP | `08_STREAMLIT_APPS_PROD/Leviat/streamlit_app.py` |
| PROOFPOINT_APP | `08_STREAMLIT_APPS_PROD/Proofpoint/streamlit_app.py` |
| QUALYS_APP | `08_STREAMLIT_APPS_PROD/Qualys/streamlit_app.py` |
| SENTINELONE_APP | `08_STREAMLIT_APPS_PROD/SentinelOne/streamlit_app.py` |
| SERVICENOW_APP | `08_STREAMLIT_APPS_PROD/ServiceNow/streamlit_app.py` |
| SOPHOS_APP | `08_STREAMLIT_APPS_PROD/Sophos/streamlit_app.py` |
| SPLUNK_APP | `08_STREAMLIT_APPS_PROD/Splunk/streamlit_app.py` |
| SYMANTEC_APP | `08_STREAMLIT_APPS_PROD/Symantec/streamlit_app.py` |
| TENABLE_APP | `08_STREAMLIT_APPS_PROD/Tenable/streamlit_app.py` |
| TRELLIX_APP | `08_STREAMLIT_APPS_PROD/Trellix/streamlit_app.py` |
| ZEROFOX_APP | `08_STREAMLIT_APPS_PROD/Zerofox/streamlit_app.py` |
| ZSCALER_APP | `08_STREAMLIT_APPS_PROD/Zscaler/streamlit_app.py` |

## Benefits of Git Deployment

### ✅ Version Control
- Track all changes
- Rollback capability
- Blame/history tracking

### 🔄 CI/CD Integration
- Automatic deployment on push
- Branch protection
- Pull request reviews

### 🛡️ Security
- No credential management
- Audit trail
- Access control via Git

### 🚀 Developer Experience
- Edit in VS Code
- Use Snowflake extension
- Local testing possible

## Testing

### Quick Test URLs
After Git connection, test apps at:

- https://app.snowflake.com/GenericCorp/crh_edw/#/streamlit-apps/DEV_REPORTING.SECURITY_ANALYTICS.LEVIAT_APP
- https://app.snowflake.com/GenericCorp/crh_edw/#/streamlit-apps/DEV_REPORTING.SECURITY_ANALYTICS.SERVICENOW_APP
- https://app.snowflake.com/GenericCorp/crh_edw/#/streamlit-apps/DEV_REPORTING.SECURITY_ANALYTICS.PROOFPOINT_APP

### Validation Checklist
- [ ] App loads without errors
- [ ] Data queries execute
- [ ] Filters work correctly
- [ ] Charts render properly
- [ ] Export CSV functions
- [ ] GenericCorp branding displays

## Troubleshooting

### Common Issues

#### "Script execution error"
- **Cause**: File path incorrect in Git connection
- **Fix**: Verify path starts with `08_STREAMLIT_APPS_PROD/`

#### "Module not found"
- **Cause**: Common modules not inlined
- **Fix**: Use files from this directory, not `07_STREAMLIT_APPS/`

#### "Permission denied"
- **Cause**: Git repository access
- **Fix**: Check Azure DevOps permissions

## Maintenance

### Updating Apps
1. Edit file in `08_STREAMLIT_APPS_PROD/{Service}/streamlit_app.py`
2. Commit and push to Azure DevOps
3. Apps auto-update if Git-connected

### Adding New Apps
1. Create new directory: `08_STREAMLIT_APPS_PROD/{NewService}/`
2. Add `streamlit_app.py` with inlined code
3. Push to Git
4. Create new Streamlit app in Snowflake
5. Connect to Git repository

## Contact

**Team**: Data Engineering
**Email**: FUAD.ONATE@CompanyX.COM
**Repository**: Azure DevOps - GIS SECURITY_ANALYTICS DW

---

*Last Updated: 2025-10-24*