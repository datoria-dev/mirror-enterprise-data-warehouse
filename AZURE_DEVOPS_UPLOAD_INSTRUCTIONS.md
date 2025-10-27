# Azure DevOps Upload Instructions

**Date**: 2025-10-25
**Status**: Ready to Upload

---

## Overview

This guide walks you through uploading the Streamlit deployment documentation and code to Azure DevOps.

---

## Part 1: Push Code to Repository

### Step 1: Run the Push Script

```bash
cd C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV
.\push_to_azure.bat
```

**What it does**:
1. Shows current git status
2. Stages all changes
3. Creates commit with detailed message
4. Pushes to Azure DevOps (azure/main)

**Expected output**:
```
[Step 1/5] Checking git status...
[Step 2/5] Adding all changes...
[Step 3/5] Showing staged files...
[Step 4/5] Creating commit...
[Step 5/5] Pushing to Azure DevOps...

Push Complete!
```

### Alternative: Manual Push

```bash
git add .
git commit -m "feat: add automated Streamlit deployment system"
git push azure main
```

---

## Part 2: Upload to Azure DevOps Wiki

### Step 1: Access Azure DevOps Wiki

1. **Navigate to**:
   ```
   https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/
   ```

2. **Click**: Overview → Wiki (left sidebar)

### Step 2: Check Existing Wiki Structure

Look for existing pages:
- Home
- Streamlit Apps (WIKI_01)
- Power BI (WIKI_02)
- Metadata Extraction (WIKI_03)
- Data Governance (WIKI_04)
- Data Dictionary (WIKI_05)
- Best Practices (WIKI_06)
- API Integrations (WIKI_07)

### Step 3: Add New Wiki Page

**Option A: Create New Page**

1. Click **"New page"** or **"+"** button
2. Name: **"Streamlit Deployment"** or **"08 - Streamlit Deployment"**
3. Copy entire content from: `WIKI_08_STREAMLIT_DEPLOYMENT.md`
4. Paste into editor
5. Click **"Save"**

**Option B: Update Existing Streamlit Apps Page**

If there's already a "Streamlit Apps" page:

1. Open the page
2. Scroll to "Deployment" section
3. Add link to new deployment guide:
   ```markdown
   ## Deployment

   > **📖 Complete Deployment Guide**: See [Streamlit Deployment](Streamlit-Deployment) for detailed instructions.
   ```
4. Create new page "Streamlit Deployment" with WIKI_08 content

### Step 4: Verify Wiki Upload

1. Check the page renders correctly
2. Test all internal links
3. Verify code blocks display properly
4. Check tables format correctly

---

## Part 3: Update Wiki Navigation (Optional)

### Add to Table of Contents

If your Wiki has a sidebar or TOC, add:

```markdown
- [Streamlit Apps](Streamlit-Apps)
  - [Deployment Guide](Streamlit-Deployment)  ← NEW
```

Or

```markdown
08. [Streamlit Deployment](Streamlit-Deployment)
```

---

## Part 4: Share with Team

### Create Announcement

**Email Template**:

```
Subject: New Streamlit Deployment Automation Available

Hi Team,

I've deployed automated deployment tools for our 18 Streamlit applications to Snowflake.

Key Features:
- Single SSO authentication (no multiple browser popups)
- Deploy all 18 apps in ~2 minutes
- Real-time progress tracking
- Comprehensive logging
- Automated issue fixes

Documentation:
- Wiki: [Azure DevOps Wiki Link]
- Quick Start: See README_NEXT_STEPS.md in repo

Location:
- Database: DEV_REPORTING
- Schema: SECURITY_ANALYTICS
- All 18 apps deployed and operational

To deploy apps yourself:
1. Clone repo
2. Run: .\fix_apps.bat
3. Run: .\deploy_apps.bat
4. Run: .\verify_apps.bat

Questions? Contact me!

Best,
Fuad
```

---

## Part 5: Verify Everything Works

### Checklist

**Repository** ✅
- [ ] Code pushed to azure/main
- [ ] All files visible in Azure DevOps
- [ ] Commit message is clear
- [ ] Branch is up to date

**Wiki** ✅
- [ ] WIKI_08 page created
- [ ] Page renders correctly
- [ ] Links work
- [ ] Code blocks formatted
- [ ] Tables display properly

**Documentation** ✅
- [ ] README_NEXT_STEPS.md accessible
- [ ] DEPLOYMENT_GUIDE_STREAMLIT.md accessible
- [ ] All automation scripts documented

**Testing** ✅
- [ ] Can clone repo
- [ ] Can run deployment scripts
- [ ] Can verify deployment
- [ ] Can analyze logs

---

## Troubleshooting

### Issue: Git push fails

**Error**: `Permission denied` or `Authentication failed`

**Solution**:
1. Check you're logged into Azure DevOps
2. Verify you have push permissions
3. Try: `git push azure main --force` (if safe)

### Issue: Wiki page doesn't save

**Error**: `Error saving page`

**Solution**:
1. Copy content to clipboard (don't lose it!)
2. Refresh page
3. Try again
4. If still fails, contact Azure DevOps admin

### Issue: Code blocks don't format

**Problem**: Code appears as plain text

**Solution**:
- Ensure code blocks use triple backticks: \`\`\`
- Specify language: \`\`\`bash or \`\`\`python
- Check for proper indentation

### Issue: Links don't work

**Problem**: Internal links broken

**Solution**:
- Use Azure DevOps Wiki link format
- Example: `[Page Name](Page-Name)` not `[Page Name](page-name)`
- No `.md` extension in Wiki links

---

## Azure DevOps URLs

### Repository
```
https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_git/GIS%20-%20ITSECKPI%20-%20DW
```

### Wiki
```
https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_wiki
```

### Specific Pages (after creation)
```
https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_wiki/wikis/GIS-SECURITY_ANALYTICS-DW.wiki/[Page-ID]
```

---

## Files to Upload to Wiki

### Primary Wiki Page
- **Source**: `WIKI_08_STREAMLIT_DEPLOYMENT.md`
- **Title**: "Streamlit Deployment" or "08 - Streamlit Deployment"
- **Category**: Documentation

### Supporting Docs (Link from Wiki)
- `DEPLOYMENT_GUIDE_STREAMLIT.md` - Detailed guide
- `README_NEXT_STEPS.md` - Quick start
- `README_AUTOMATION_SCRIPTS.md` - Script documentation

---

## After Upload Checklist

- [ ] Code pushed to Azure DevOps
- [ ] Wiki page created and verified
- [ ] Navigation updated (if applicable)
- [ ] Team notified
- [ ] Documentation accessible
- [ ] Scripts tested by another team member
- [ ] Deployment logs reviewed
- [ ] Production deployment planned

---

## Success Metrics

After upload, you should be able to:

✅ **Access** - Anyone can view Wiki page
✅ **Deploy** - Anyone can clone and run deployment
✅ **Verify** - Anyone can check deployment status
✅ **Troubleshoot** - Anyone can analyze logs
✅ **Maintain** - Anyone can update apps

---

## Next Actions

### Today
1. Run `.\push_to_azure.bat`
2. Upload WIKI_08 to Azure DevOps Wiki
3. Verify Wiki page works
4. Send team announcement

### This Week
5. Train team on deployment tools
6. Document production deployment process
7. Create deployment schedule

### This Month
8. Request ACCOUNTADMIN permissions
9. Set up Git integration in Snowflake
10. Create CI/CD pipeline

---

## Contact

**Questions?** Contact Fuad Onate (fuad.onate@CompanyX.com)

**Status**: ✅ Ready to Upload
**Date**: 2025-10-25
