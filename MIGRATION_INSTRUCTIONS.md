# Azure DevOps Migration Instructions

Complete guide for migrating the SECURITY_ANALYTICS Data Warehouse from GitHub to Azure DevOps.

---

## 📋 Pre-Migration Checklist

Before starting the migration, ensure you have:

- [x] Azure DevOps project created: `GIS-SECURITY_ANALYTICS-DW`
- [ ] Azure DevOps Personal Access Token (PAT) with Code (Read & Write) permissions
- [ ] Git installed and configured
- [ ] Current repository backed up
- [ ] All uncommitted changes committed or stashed

---

## 🚀 Quick Migration (Automated)

### Option 1: Use PowerShell Script (Recommended)

```powershell
# Navigate to repository
cd "C:\Projects\Snowflake_ITSECKPI_Project_DEV"

# Run migration script (dry run first)
.\migrate_to_azure_devops.ps1 -DryRun

# Run actual migration
.\migrate_to_azure_devops.ps1

# Script will:
# - Create backup
# - Add Azure DevOps remote
# - Push all branches
# - Verify migration
```

**Duration**: 5-10 minutes

---

## 🔧 Manual Migration (Step by Step)

### Step 1: Prepare Repository

```bash
# Navigate to DEV repository
cd "C:\Projects\Snowflake_ITSECKPI_Project_DEV"

# Check status
git status

# Commit any pending changes
git add .
git commit -m "chore: prepare for Azure DevOps migration"

# Verify clean state
git status
```

### Step 2: Add Azure DevOps Remote

```bash
# Add Azure DevOps as remote named 'azure'
git remote add azure https://dev.azure.com/CompanyX/GIS-SECURITY_ANALYTICS-DW/_git/GIS-SECURITY_ANALYTICS-DW

# Verify remotes
git remote -v

# Should show:
# origin  https://github.com/fos-CompanyX/snowflake-SECURITY_ANALYTICS-datawarehouse.git (fetch)
# origin  https://github.com/fos-CompanyX/snowflake-SECURITY_ANALYTICS-datawarehouse.git (push)
# azure   https://dev.azure.com/CompanyX/GIS-SECURITY_ANALYTICS-DW/_git/GIS-SECURITY_ANALYTICS-DW (fetch)
# azure   https://dev.azure.com/CompanyX/GIS-SECURITY_ANALYTICS-DW/_git/GIS-SECURITY_ANALYTICS-DW (push)
```

### Step 3: Push to Azure DevOps

```bash
# Push main branch to Azure DevOps
git push -u azure main

# You will be prompted for credentials:
# Username: Your Azure DevOps email
# Password: Your Personal Access Token (PAT)
```

**Expected output:**
```
Enumerating objects: 453, done.
Counting objects: 100% (453/453), done.
Delta compression using up to 8 threads
Compressing objects: 100% (320/320), done.
Writing objects: 100% (453/453), 1.25 MiB | 250.00 KiB/s, done.
Total 453 (delta 180), reused 453 (delta 180)
remote: Analyzing objects... (453/453) (100 ms)
remote: Storing packfile... done (250 ms)
To https://dev.azure.com/CompanyX/GIS-SECURITY_ANALYTICS-DW/_git/GIS-SECURITY_ANALYTICS-DW
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'azure'.
```

### Step 4: Verify Migration

```bash
# Fetch from Azure DevOps
git fetch azure

# Compare commits
git log azure/main --oneline -5

# Verify files
git ls-tree -r azure/main --name-only | wc -l
# Should show: 453 files
```

---

## 📦 Post-Migration Configuration

### 1. Update README for Azure DevOps

```bash
# Replace README with Azure DevOps version
Copy-Item AZURE_DEVOPS_README.md README.md -Force

# Commit and push
git add README.md
git commit -m "docs: update README for Azure DevOps"
git push azure main
```

### 2. Set Up Wiki

1. Navigate to Azure DevOps project: https://dev.azure.com/CompanyX/GIS-SECURITY_ANALYTICS-DW
2. Go to **Overview** → **Wiki**
3. Click **Publish code as wiki**
4. Select:
   - **Repository**: GIS-SECURITY_ANALYTICS-DW
   - **Branch**: main
   - **Folder**: /.azuredevops/wiki
   - **Wiki name**: SECURITY_ANALYTICS Data Warehouse Wiki
5. Click **Publish**

**Verification**: Navigate to Wiki and verify Home page loads

### 3. Configure CI/CD Pipelines

#### Create CI Validation Pipeline

1. Go to **Pipelines** → **New pipeline**
2. Select **Azure Repos Git**
3. Select **GIS-SECURITY_ANALYTICS-DW** repository
4. Choose **Existing Azure Pipelines YAML file**
5. Select `/.azuredevops/pipelines/ci-validation.yml`
6. Click **Run**

**Expected**: Pipeline runs and validates Python, SQL, and documentation

#### Create CD Deployment Pipeline

1. Go to **Pipelines** → **New pipeline**
2. Select **Azure Repos Git**
3. Select **GIS-SECURITY_ANALYTICS-DW** repository
4. Choose **Existing Azure Pipelines YAML file**
5. Select `/.azuredevops/pipelines/cd-deploy-snowflake.yml`
6. Click **Save** (don't run yet - requires Snowflake credentials)

### 4. Set Up Variable Groups

1. Go to **Pipelines** → **Library**
2. Click **+ Variable group**
3. Create **Snowflake-DEV-Credentials**:
   - Name: `Snowflake-DEV-Credentials`
   - Variables:
     - `SNOWFLAKE_ACCOUNT`: your-account.region
     - `SNOWFLAKE_USER`: your-username
     - `SNOWFLAKE_PASSWORD`: (mark as secret) 🔒
     - `SNOWFLAKE_WAREHOUSE`: DEV_WH
     - `SNOWFLAKE_ROLE`: SECURITY_ANALYTICS
4. Repeat for **Snowflake-PRD-Credentials**

### 5. Configure Branch Policies

1. Go to **Project Settings** → **Repositories**
2. Select **GIS-SECURITY_ANALYTICS-DW**
3. Go to **Branches**
4. Click **...** next to **main** → **Branch policies**
5. Enable:
   - ✅ **Require a minimum number of reviewers**: 1
   - ✅ **Check for linked work items**
   - ✅ **Check for comment resolution**
   - ✅ **Build validation**: Select CI Validation pipeline
6. Click **Save**

### 6. Import Work Items

1. Go to **Boards** → **Work Items**
2. Click **Import Work Items** (or use Excel)
3. Select `.azuredevops/work-items-template.csv`
4. Map columns:
   - Work Item Type → Work Item Type
   - Title → Title
   - State → State
   - Priority → Priority
   - Description → Description
   - Tags → Tags
5. Click **Import**

**Expected**: 50+ work items created across Epic, Features, User Stories, Tasks, and Bugs

### 7. Set Up Boards

1. Go to **Boards** → **Boards**
2. Configure columns:
   - New → Active → Resolved → Closed
3. Configure swimlanes:
   - Expedite
   - By Priority
4. Add custom fields if needed

---

## 🔍 Verification Checklist

After migration, verify the following:

### Repository
- [ ] All 453 files present in Azure DevOps
- [ ] README.md displays correctly
- [ ] All branches pushed (main + any feature branches)
- [ ] Git history intact (all commits present)
- [ ] .gitignore working (no sensitive files)

### Wiki
- [ ] Wiki published from `.azuredevops/wiki`
- [ ] Home page loads correctly
- [ ] All wiki pages accessible
- [ ] Internal links working
- [ ] Code references functional

### Pipelines
- [ ] CI Validation pipeline created
- [ ] CD Deployment pipeline created
- [ ] CI pipeline runs successfully on commit
- [ ] Variable groups configured
- [ ] Service connections set up (if applicable)

### Boards
- [ ] Work items imported
- [ ] Epic created with features
- [ ] User stories linked to features
- [ ] Tasks created
- [ ] Tags applied correctly
- [ ] Board columns configured

### Settings
- [ ] Branch policies enabled on main
- [ ] Required reviewers configured
- [ ] Build validation enabled
- [ ] Team permissions set
- [ ] Notifications configured

---

## 🆘 Troubleshooting

### Issue: Authentication Failed

**Error**: `remote: TF401019: The Git repository with name or identifier GIS-SECURITY_ANALYTICS-DW does not exist`

**Solution**:
1. Verify Azure DevOps organization and project names
2. Check Personal Access Token (PAT) is valid
3. Ensure PAT has Code (Read & Write) permissions
4. Try using full URL with PAT embedded (temporarily):
   ```bash
   git remote set-url azure https://YOUR_PAT@dev.azure.com/CompanyX/GIS-SECURITY_ANALYTICS-DW/_git/GIS-SECURITY_ANALYTICS-DW
   ```

### Issue: Repository Not Empty

**Error**: `! [rejected] main -> main (non-fast-forward)`

**Solution**:
1. If Azure DevOps repo has initial files (README, .gitignore):
   ```bash
   git pull azure main --allow-unrelated-histories
   git push azure main
   ```
2. Or force push (only if you're sure):
   ```bash
   git push azure main --force
   ```

### Issue: Large Files Rejected

**Error**: `remote: error: File too large`

**Solution**:
1. Check for large files:
   ```bash
   git ls-files | xargs -I{} bash -c 'echo $(git cat-file -s {}) {}' | sort -rn | head -20
   ```
2. Remove large files or use Git LFS:
   ```bash
   git lfs install
   git lfs track "*.pbix"
   git lfs track "*.xlsx"
   git add .gitattributes
   git commit -m "chore: add Git LFS tracking"
   ```

### Issue: Wiki Not Publishing

**Error**: Wiki pages not showing in Azure DevOps

**Solution**:
1. Verify `.azuredevops/wiki` folder exists in repository
2. Check `Home.md` exists in wiki folder
3. Ensure wiki is published from correct branch (main)
4. Verify file naming (must be `.md` extension)
5. Check permissions (must have Contributor access)

---

## 📞 Support

### Getting Help

- **Azure DevOps Issues**: Check Azure DevOps documentation
- **Migration Issues**: Review this guide and troubleshooting section
- **Project Issues**: Create work item in Azure Boards

### Useful Links

- **Azure DevOps Project**: https://dev.azure.com/CompanyX/GIS-SECURITY_ANALYTICS-DW
- **Azure DevOps Docs**: https://docs.microsoft.com/en-us/azure/devops/
- **Git Documentation**: https://git-scm.com/doc

---

## 📊 Migration Summary

### What Was Migrated

| Item | Count | Status |
|------|-------|--------|
| **Files** | 453 | ✅ Migrated |
| **SQL Scripts** | 18 | ✅ Migrated |
| **Python Scripts** | 8+ | ✅ Migrated |
| **Streamlit Apps** | 12 | ✅ Migrated |
| **Documentation** | 50+ .md files | ✅ Migrated |
| **Git Commits** | All history | ✅ Migrated |
| **Branches** | main + others | ✅ Migrated |

### What Was Created

| Item | Description | Location |
|------|-------------|----------|
| **Azure DevOps Remote** | Git remote for Azure DevOps | `.git/config` |
| **CI Pipeline** | Code validation pipeline | `.azuredevops/pipelines/ci-validation.yml` |
| **CD Pipeline** | Snowflake deployment pipeline | `.azuredevops/pipelines/cd-deploy-snowflake.yml` |
| **Wiki** | Project documentation | `.azuredevops/wiki/` |
| **Work Items** | Project backlog | `.azuredevops/work-items-template.csv` |
| **README** | Azure DevOps-optimized README | `AZURE_DEVOPS_README.md` |

---

## 🎉 Next Steps After Migration

1. **Team Onboarding**
   - Share Azure DevOps project URL with team
   - Grant appropriate permissions (Contributor, Reader, etc.)
   - Schedule walkthrough of Wiki and Boards

2. **Start Using Azure DevOps**
   - Create feature branches from `main`
   - Use pull requests for code reviews
   - Link commits to work items
   - Track progress in Boards

3. **Set Up Automated Deployments**
   - Configure Snowflake service connections
   - Test CD pipeline in DEV environment
   - Set up approval gates for PRD deployments
   - Schedule regular deployments

4. **Ongoing Maintenance**
   - Keep Wiki updated
   - Update work items as features complete
   - Monitor pipeline runs
   - Review and update branch policies

---

**Migration completed successfully!** 🚀

Repository is now live at:
https://dev.azure.com/CompanyX/GIS-SECURITY_ANALYTICS-DW/_git/GIS-SECURITY_ANALYTICS-DW

---

**Last Updated**: October 23, 2025
**Version**: 1.0
