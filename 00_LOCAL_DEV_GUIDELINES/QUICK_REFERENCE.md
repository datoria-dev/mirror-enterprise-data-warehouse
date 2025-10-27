# Quick Reference Guide

**Purpose**: Fast lookup for common situations

---

## 🚨 Emergency - Session Lost / New Chat

**READ FIRST**: [LOCAL_DEV_BEST_PRACTICES.md](LOCAL_DEV_BEST_PRACTICES.md)

**Key Points**:
1. ✅ All work in English
2. ✅ Use fuad.onate@CompanyX.com credentials
3. ✅ Always automate with CSV/JSON logs
4. ✅ Never commit: emails, credentials, personal notes
5. ✅ Never mention AI tools in documentation

---

## 📖 Which Document to Read?

### Starting New Session or Context Lost
→ **[README.md](README.md)** - Overview of this folder
→ **[LOCAL_DEV_BEST_PRACTICES.md](LOCAL_DEV_BEST_PRACTICES.md)** - Complete guidelines

### Want to Know What Was Done Last
→ **[SESSION_FINAL_FIXES_SUMMARY.md](SESSION_FINAL_FIXES_SUMMARY.md)** - Latest session results

### Working on Sophos App Issues
→ **[SOPHOS_FIXES_COMPLETE.md](SOPHOS_FIXES_COMPLETE.md)** - Technical details and fixes

### Need Quick Commands
→ This file (QUICK_REFERENCE.md) - See below ⬇️

---

## ⚡ Common Commands

### Fix Issues in Streamlit Apps
```bash
.\fix_apps.bat
```
Fixes:
- np.random.* → Python random module
- Download buttons (adds key + mime)

### Deploy All 18 Apps
```bash
.\deploy_apps.bat
```

### Deploy Sophos Only (for testing)
```bash
.\deploy_sophos_fixed.bat
```

### Analyze Deployment Logs
```bash
.\analyze_logs.bat
```

### Check What's in Snowflake Stage
```bash
python 02_PYTHON_SCRIPTS\check_snowflake_stage.py
```

---

## 🔍 Quick Checks

### Verify No np.random Calls Remain
```bash
grep -r "np\.random" "13_STREAMLIT_COMPLETE/*/streamlit_app.py"
```
Should return empty (or only files not yet fixed)

### Check Git Status
```bash
git status
```

### See What's Excluded from Git
```bash
cat .gitignore
```

---

## 🐛 Troubleshooting

### App Shows np.random Error
**Problem**: Old version deployed in Snowflake
**Solution**:
1. Run `.\fix_apps.bat`
2. Run `.\deploy_apps.bat`
3. Refresh Snowflake UI (Ctrl+F5)

### Download Button Not Working
**Problem**: Browser bug (Windows + Chrome/Edge)
**Solution**: Try Firefox browser
**Note**: Code is correct, it's a known browser issue

### Can't Connect to Snowflake
**Check**:
1. Okta credentials valid?
2. VPN connected?
3. DEV_DEVELOPER role assigned?

---

## 📁 Important Files

### Configuration
- `snowflake_config.json` - Snowflake connection (excluded from git)
- `.gitignore` - What to exclude from commits

### Main Scripts
- `fix_apps.bat` - Fix all known issues
- `deploy_apps.bat` - Deploy all apps
- `deploy_sophos_fixed.bat` - Deploy Sophos only

### Directories
- `13_STREAMLIT_COMPLETE/` - Production-ready apps
- `02_PYTHON_SCRIPTS/` - Automation scripts
- `deployment_logs/` - Deployment logs (excluded from git)
- `00_LOCAL_DEV_GUIDELINES/` - This folder (excluded from git)

---

## ✅ Pre-Commit Checklist

Before `git commit`:
- [ ] No credentials in code
- [ ] No EMAIL_*.md files
- [ ] No SESSION_*.md files
- [ ] No deployment logs
- [ ] All work in English
- [ ] Code tested

---

## 🎯 Current Known Issues

### Snowflake Streamlit Limitations
**Issue**: np.random.* functions don't work
**Fix**: Use Python's `random` module instead
**Status**: Fix script available (`fix_apps.bat`)

### Download Buttons on Windows
**Issue**: Chrome/Edge download .htm instead of .csv
**Cause**: Browser bug (May 2025, Streamlit 1.45.0)
**Workaround**: Use Firefox
**Status**: Code is correct, waiting for browser/Streamlit fix

---

## 📞 Key Information

**Snowflake Account**:
- **Account**: `GenericCorp-CRH_EDW`
- **Organization**: `GenericCorp`
- **URL**: `GenericCorp-CRH_EDW.snowflakecomputing.com`
- **Login**: `FUAD.ONATE@CompanyX.COM`
- **Auth**: `externalbrowser` (Okta SSO via browser) ⚠️ ALWAYS USE THIS
- **Cloud**: AZURE
- **Edition**: Business Critical

**Default Settings**:
- **Role**: `DEV_DEVELOPER` (primary for development)
- **Warehouse**: `DEV_WH` (Medium)
- **Database**: `DEV_REPORTING`
- **Schema**: `SECURITY_ANALYTICS`

**Azure DevOps**:
- Organization: `CompanyX`
- Project: `GIS - SECURITY_ANALYTICS - DW`
- Remote: `azure`

---

## 🚀 Standard Workflow

1. **Fix** → `.\fix_apps.bat`
2. **Deploy** → `.\deploy_apps.bat`
3. **Verify** → Check Snowflake UI
4. **Test** → Add/remove filters, download CSV
5. **Document** → Update session notes
6. **Commit** → Only production code (no emails/credentials)

---

**Last Updated**: 2025-10-25
**Version**: 1.0

**Note**: Keep this folder updated as new patterns emerge.
