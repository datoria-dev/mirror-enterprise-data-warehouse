# Safe Wiki Upload Process - Azure DevOps

## Overview

This document provides a **safe, step-by-step process** to upload the 6 new wikis to Azure DevOps without overwriting existing content.

**Project**: GIS - SECURITY_ANALYTICS - DW
**Wiki URL**: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_wiki/wikis/

---

## Step 1: Clone the Existing Wiki Repository

First, we'll clone the existing wiki to review its structure and avoid conflicts.

### Commands to Execute

```bash
# Navigate to your working directory
cd C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV

# Clone the wiki repository (Azure DevOps wikis are Git repositories)
git clone https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_git/GIS%20-%20ITSECKPI%20-%20DW.wiki wiki-repo

# Navigate into the cloned repository
cd wiki-repo
```

**Note**: You'll be prompted for Azure DevOps authentication (SSO via browser).

---

## Step 2: Review Existing Wiki Structure

After cloning, review the existing structure to identify:
1. Existing wiki pages and their names
2. Current folder organization
3. Any pages named "Data Model" or similar
4. Files that should NOT be modified

### Commands to Review Structure

```bash
# List all files in the wiki
ls -la

# Show directory tree (if tree command available)
tree /F

# Or use PowerShell
Get-ChildItem -Recurse | Select-Object FullName
```

### What to Look For

**Existing Pages to Preserve**:
- [ ] Home page or landing page
- [ ] Data Model wiki (mentioned by user)
- [ ] Any existing governance documentation
- [ ] Any existing best practices
- [ ] Any existing metadata documentation

**Naming Conflicts**:
- Check if files like "Data-Governance.md", "Best-Practices.md", etc. already exist
- If they exist, we'll need to rename our new wikis or merge content

---

## Step 3: Create a Safe Backup Branch

Before making any changes, create a backup branch.

```bash
# Ensure you're on the main/default branch
git branch

# Create a backup branch from current state
git checkout -b backup-before-new-wikis-2025-10-24

# Push backup to Azure DevOps
git push origin backup-before-new-wikis-2025-10-24

# Return to main branch
git checkout main
```

**Benefit**: If anything goes wrong, you can restore from this backup.

---

## Step 4: Create New Folder Structure

Create a dedicated folder for the new SECURITY_ANALYTICS documentation wikis.

```bash
# Create main folder for new wikis
mkdir "SECURITY_ANALYTICS-Documentation"

# Create subfolder structure (optional)
mkdir "SECURITY_ANALYTICS-Documentation/Applications"
mkdir "SECURITY_ANALYTICS-Documentation/Technical"
mkdir "SECURITY_ANALYTICS-Documentation/Governance"
```

**Recommended Structure**:
```
wiki-repo/
├── (existing wikis - DO NOT MODIFY)
│   ├── Home.md (or whatever exists)
│   ├── Data-Model.md (existing - we'll enhance this)
│   └── ...
│
└── SECURITY_ANALYTICS-Documentation/  (NEW FOLDER)
    ├── 01-Streamlit-Applications.md
    ├── 02-Power-BI-Roadmap.md
    ├── 03-Metadata-Extraction.md
    ├── 04-Data-Governance.md
    ├── 05-Data-Dictionary.md
    └── 06-Best-Practices.md
```

---

## Step 5: Copy New Wikis to Repository

Copy the 6 new wikis to the wiki repository with safe names.

```bash
# Navigate to wiki repo root
cd C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\wiki-repo

# Copy new wikis to SECURITY_ANALYTICS-Documentation folder
cp ../WIKI_01_STREAMLIT_APPS.md "SECURITY_ANALYTICS-Documentation/01-Streamlit-Applications.md"
cp ../WIKI_02_POWER_BI.md "SECURITY_ANALYTICS-Documentation/02-Power-BI-Roadmap.md"
cp ../WIKI_03_METADATA_EXTRACTION.md "SECURITY_ANALYTICS-Documentation/03-Metadata-Extraction.md"
cp ../WIKI_04_DATA_GOVERNANCE.md "SECURITY_ANALYTICS-Documentation/04-Data-Governance.md"
cp ../WIKI_05_DATA_DICTIONARY.md "SECURITY_ANALYTICS-Documentation/05-Data-Dictionary.md"
cp ../WIKI_06_BEST_PRACTICES.md "SECURITY_ANALYTICS-Documentation/06-Best-Practices.md"
```

**Alternative**: If you prefer not to create a subfolder, copy directly to root with unique names:
```bash
cp ../WIKI_01_STREAMLIT_APPS.md "SECURITY_ANALYTICS-Streamlit-Applications.md"
cp ../WIKI_02_POWER_BI.md "SECURITY_ANALYTICS-Power-BI-Roadmap.md"
# etc...
```

---

## Step 6: Review Changes Before Committing

**CRITICAL STEP**: Review what will be committed to ensure no existing files are modified.

```bash
# Show status of changes
git status

# Expected output should show ONLY:
# - New files in SECURITY_ANALYTICS-Documentation/
# - NO modifications to existing files

# Review differences (should only show new file additions)
git diff --staged
```

**Safety Check**:
- ✅ Only new files appear in `git status`
- ✅ No existing files show as "modified"
- ✅ File names don't conflict with existing wikis
- ❌ If existing files show as modified, STOP and investigate

---

## Step 7: Stage New Files

Add only the new files to Git staging area.

```bash
# Add the new folder and all its contents
git add SECURITY_ANALYTICS-Documentation/

# Verify what's staged
git status

# Expected: 6 new files ready to commit
```

---

## Step 8: Create Descriptive Commit

Create a comprehensive commit message.

```bash
git commit -m "docs: Add comprehensive SECURITY_ANALYTICS Data Warehouse documentation

Add 6 new wiki pages documenting the SECURITY_ANALYTICS Data Warehouse project:

1. Streamlit Applications - Complete catalog of 20 analytics applications
2. Power BI Roadmap - Implementation plan for BI platform (6 months)
3. Metadata Extraction - Automated metadata management system
4. Data Governance - Governance framework and policies
5. Data Dictionary - Complete catalog (20 services, 180 tables, 2,206 columns)
6. Best Practices - Development standards and guidelines

Key Features:
- Complete documentation for 20 integrated security services
- Metadata repository automation (SP_REFRESH_METADATA)
- Daily scheduled metadata refresh
- Comprehensive data governance framework
- SQL and Python development standards

All documentation written in English per project standards.

Related Work:
- Metadata repository infrastructure deployed
- Export tables created (13 export tables)
- Streamlit metadata tabs integrated (6 services)

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Step 9: Review Commit Before Pushing

**FINAL SAFETY CHECK**: Review the commit before pushing to Azure DevOps.

```bash
# Show commit details
git show HEAD

# Show list of files in commit
git show --name-only HEAD

# Show commit log
git log -1
```

**Verify**:
- ✅ Commit message is descriptive
- ✅ Only 6 new files in commit
- ✅ No existing files modified
- ✅ File paths are correct

---

## Step 10: Push to Azure DevOps

Push the new wikis to Azure DevOps.

```bash
# Push to main branch
git push origin main

# Or if your default branch is named differently:
# git push origin master
# git push origin develop
```

**Expected Output**:
```
Enumerating objects: 8, done.
Counting objects: 100% (8/8), done.
Delta compression using up to 8 threads
Compressing objects: 100% (6/6), done.
Writing objects: 100% (7/7), 225.00 KiB | 15.00 MiB/s, done.
Total 7 (delta 1), reused 0 (delta 0)
To https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_git/GIS%20-%20ITSECKPI%20-%20DW.wiki
   abc1234..def5678  main -> main
```

---

## Step 11: Verify Upload in Azure DevOps

After pushing, verify the wikis appear correctly in Azure DevOps.

### Verification Steps

1. **Open Azure DevOps Wiki**:
   - Navigate to: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_wiki/wikis/

2. **Check New Pages Appear**:
   - [ ] SECURITY_ANALYTICS-Documentation folder visible
   - [ ] All 6 wikis present
   - [ ] Formatting renders correctly
   - [ ] Tables display properly
   - [ ] Code blocks have syntax highlighting

3. **Check Existing Pages Unchanged**:
   - [ ] Existing wikis still accessible
   - [ ] No content lost or modified
   - [ ] Links still work

4. **Test Navigation**:
   - [ ] Table of contents works in each wiki
   - [ ] Cross-references between wikis work
   - [ ] External links work

---

## Step 12: Create Landing Page Links (Optional)

If the existing wiki home page should link to the new documentation, create a pull request or update.

### Option A: Direct Update
```bash
# Edit the existing Home.md or landing page
code Home.md  # or whatever editor you use

# Add links to new wikis:
```

Add this section to the existing home page:
```markdown
## SECURITY_ANALYTICS Data Warehouse Documentation

Comprehensive documentation for the SECURITY_ANALYTICS Data Warehouse project:

- **[Streamlit Applications](SECURITY_ANALYTICS-Documentation/01-Streamlit-Applications)** - 20 analytics applications
- **[Power BI Roadmap](SECURITY_ANALYTICS-Documentation/02-Power-BI-Roadmap)** - BI implementation plan
- **[Metadata Extraction](SECURITY_ANALYTICS-Documentation/03-Metadata-Extraction)** - Automated metadata management
- **[Data Governance](SECURITY_ANALYTICS-Documentation/04-Data-Governance)** - Governance framework
- **[Data Dictionary](SECURITY_ANALYTICS-Documentation/05-Data-Dictionary)** - Complete data catalog
- **[Best Practices](SECURITY_ANALYTICS-Documentation/06-Best-Practices)** - Development standards
```

Then commit and push:
```bash
git add Home.md
git commit -m "docs: Add links to new SECURITY_ANALYTICS documentation"
git push origin main
```

### Option B: Create Pull Request (Safer for Team Review)
```bash
# Create feature branch
git checkout -b add-SECURITY_ANALYTICS-docs-links

# Make changes to Home.md
# ... edit file ...

# Commit and push
git add Home.md
git commit -m "docs: Add navigation links to SECURITY_ANALYTICS documentation"
git push origin add-SECURITY_ANALYTICS-docs-links

# Create PR in Azure DevOps web UI
```

---

## Rollback Instructions (If Needed)

If something goes wrong, you can rollback to the backup.

### Option 1: Revert to Backup Branch
```bash
# Switch to backup branch
git checkout backup-before-new-wikis-2025-10-24

# Force push to main (CAREFUL!)
git push origin backup-before-new-wikis-2025-10-24:main --force
```

### Option 2: Revert Last Commit
```bash
# Undo last commit but keep files
git reset --soft HEAD~1

# Or undo last commit and delete files
git reset --hard HEAD~1

# Force push to remote
git push origin main --force
```

### Option 3: Delete Specific Files
```bash
# Remove specific files
git rm SECURITY_ANALYTICS-Documentation/01-Streamlit-Applications.md
# ... remove others ...

# Commit deletion
git commit -m "docs: Remove SECURITY_ANALYTICS documentation (rollback)"

# Push
git push origin main
```

---

## Troubleshooting

### Issue: "Permission Denied" When Pushing

**Solution**:
```bash
# Verify you have contributor access
# Check with team lead or admin

# Ensure you're authenticated
git config --global user.email "fuad.onate@CompanyX.com"
git config --global user.name "Fuad Onate"
```

### Issue: "Conflict with Existing File"

**Solution**:
```bash
# If file names conflict, rename your files:
mv SECURITY_ANALYTICS-Documentation/04-Data-Governance.md SECURITY_ANALYTICS-Documentation/04-SECURITY_ANALYTICS-Data-Governance.md

# Then commit with new name
git add .
git commit -m "docs: Rename to avoid conflict"
```

### Issue: "Wiki Formatting Broken"

**Solution**:
- Check that markdown files use Azure DevOps compatible syntax
- Azure DevOps wikis may not support all GitHub markdown features
- Test with a single wiki first before uploading all 6

### Issue: "Links Between Wikis Don't Work"

**Solution**:
- Update relative links to match Azure DevOps wiki path structure
- Use format: `[Link Text](Page-Name)` for same-level pages
- Use format: `[Link Text](Folder/Page-Name)` for pages in folders

---

## Post-Upload Tasks

After successful upload:

### Documentation
- [ ] Update project README with links to new wikis
- [ ] Notify team via email/Teams about new documentation
- [ ] Schedule wiki review meeting

### Maintenance
- [ ] Set up monthly wiki review calendar reminder
- [ ] Assign wiki owners (Data Stewards, Tech Leads)
- [ ] Create process for wiki updates

### Enhancement
- [ ] Update "Data Model" wiki with ERD improvements (see next section)
- [ ] Add any missing screenshots or diagrams
- [ ] Create video walkthroughs if needed

---

## Next Step: Enhance Data Model Wiki with Metadata

**You asked**: "el nuevo proceso que hemos creado para tener todos los metadatos del DW, podria ayudarnos a mejorar entonces el Entity Relationship Diagram (ERD) del Wiki 'Data Model' cierto?"

**Answer**: ¡Absolutamente! The metadata repository can dramatically improve the Data Model ERD.

### How Metadata Repository Helps ERD

1. **Automated ERD Generation**:
   - Query TABLE_REGISTRY for all tables
   - Query COLUMN_METADATA for all columns and data types
   - Automatically generate ERD from live metadata

2. **Always Up-to-Date**:
   - ERD reflects current schema (updated daily)
   - No manual updates needed when tables change
   - Automatic detection of new tables/columns

3. **Service-Based Organization**:
   - ERDs grouped by service (SentinelOne, CybelAngel, etc.)
   - Clear visual separation of Landing vs Transformation layers
   - Relationship mapping between layers

### We'll Create This in Next Steps

I'll help you:
1. First upload the 6 wikis safely
2. Review existing "Data Model" wiki
3. Generate enhanced ERD using metadata repository
4. Update "Data Model" wiki with new ERD

---

**Document Created**: 2025-10-24
**Purpose**: Safe, step-by-step process to upload wikis to Azure DevOps without conflicts
**Status**: Ready to execute
**Next Action**: Execute Step 1 (Clone wiki repository)
