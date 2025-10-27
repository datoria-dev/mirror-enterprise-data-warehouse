# Azure DevOps Wiki Integration Plan

## Current Wiki Structure

Based on the screenshot, the wiki already has:
- ✅ Deployment Guide
- ✅ Home
- ✅ Data Architecture
- ✅ **Data Model** (target for ERD enhancement)
- ✅ End to End Flow

**Wiki Name**: SECURITY_ANALYTICS Data Warehouse Documentation
**Branch**: main

---

## Integration Strategy

### Option 1: Create Subfolder for New Documentation (RECOMMENDED)

Add our 6 new wikis under a dedicated folder without touching existing pages.

**Proposed Structure**:
```
SECURITY_ANALYTICS Data Warehouse Documentation (wiki repo)
│
├── Deployment-Guide.md (existing - DO NOT MODIFY)
├── Home.md (existing - we'll UPDATE with links)
├── Data-Architecture.md (existing - DO NOT MODIFY)
├── Data-Model.md (existing - we'll ENHANCE later with ERD)
├── End-to-End-Flow.md (existing - DO NOT MODIFY)
│
└── SECURITY_ANALYTICS-Documentation/ (NEW FOLDER)
    ├── 01-Streamlit-Applications.md
    ├── 02-Power-BI-Roadmap.md
    ├── 03-Metadata-Extraction.md
    ├── 04-Data-Governance.md
    ├── 05-Data-Dictionary.md
    └── 06-Best-Practices.md
```

**Pros**:
- ✅ No risk of overwriting existing content
- ✅ Clear separation between existing and new docs
- ✅ Easy to navigate
- ✅ Can link from Home page

**Cons**:
- None significant

---

### Option 2: Integrate at Root Level with Unique Names

Add wikis directly at root level with unique prefixes.

**Structure**:
```
├── Deployment-Guide.md (existing)
├── Home.md (existing)
├── Data-Architecture.md (existing)
├── Data-Model.md (existing)
├── End-to-End-Flow.md (existing)
├── SECURITY_ANALYTICS-Streamlit-Applications.md (new)
├── SECURITY_ANALYTICS-Power-BI-Roadmap.md (new)
├── SECURITY_ANALYTICS-Metadata-Extraction.md (new)
├── SECURITY_ANALYTICS-Data-Governance.md (new)
├── SECURITY_ANALYTICS-Data-Dictionary.md (new)
└── SECURITY_ANALYTICS-Best-Practices.md (new)
```

**Pros**:
- All pages at same level
- Easy to find with prefix

**Cons**:
- ⚠️ Root level gets crowded
- Less organized

---

## RECOMMENDED: Option 1 with Home Page Update

### Step 1: Clone the Wiki Repository

The wiki repository URL should be:
```
https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_git/GIS%20-%20ITSECKPI%20-%20DW.wiki
```

### Step 2: Review Existing Files

After cloning, you'll see the actual file names (they might be different from display names).

Common patterns:
- Display: "Deployment Guide" → File: `Deployment-Guide.md` or `Deployment_Guide.md`
- Display: "Data Model" → File: `Data-Model.md` or `Data_Model.md`

### Step 3: Create SECURITY_ANALYTICS-Documentation Folder

```bash
cd wiki-repo
mkdir SECURITY_ANALYTICS-Documentation
```

### Step 4: Copy Our 6 Wikis

```powershell
Copy-Item "..\WIKI_01_STREAMLIT_APPS.md" -Destination "SECURITY_ANALYTICS-Documentation\01-Streamlit-Applications.md"
Copy-Item "..\WIKI_02_POWER_BI.md" -Destination "SECURITY_ANALYTICS-Documentation\02-Power-BI-Roadmap.md"
Copy-Item "..\WIKI_03_METADATA_EXTRACTION.md" -Destination "SECURITY_ANALYTICS-Documentation\03-Metadata-Extraction.md"
Copy-Item "..\WIKI_04_DATA_GOVERNANCE.md" -Destination "SECURITY_ANALYTICS-Documentation\04-Data-Governance.md"
Copy-Item "..\WIKI_05_DATA_DICTIONARY.md" -Destination "SECURITY_ANALYTICS-Documentation\05-Data-Dictionary.md"
Copy-Item "..\WIKI_06_BEST_PRACTICES.md" -Destination "SECURITY_ANALYTICS-Documentation\06-Best-Practices.md"
```

### Step 5: Update Home Page (Optional but Recommended)

Add a new section to `Home.md` linking to the new documentation:

```markdown
## SECURITY_ANALYTICS Data Warehouse - Comprehensive Documentation

Complete documentation for data warehouse operations, governance, and development:

### 📱 Applications & Roadmap
- **[Streamlit Applications](SECURITY_ANALYTICS-Documentation/01-Streamlit-Applications)** - 20 interactive analytics dashboards
- **[Power BI Roadmap](SECURITY_ANALYTICS-Documentation/02-Power-BI-Roadmap)** - Business intelligence implementation plan

### 🔧 Technical Documentation
- **[Metadata Extraction](SECURITY_ANALYTICS-Documentation/03-Metadata-Extraction)** - Automated metadata management system
- **[Data Dictionary](SECURITY_ANALYTICS-Documentation/05-Data-Dictionary)** - Complete data catalog (20 services, 180 tables)

### 📋 Governance & Standards
- **[Data Governance](SECURITY_ANALYTICS-Documentation/04-Data-Governance)** - Governance framework and policies
- **[Best Practices](SECURITY_ANALYTICS-Documentation/06-Best-Practices)** - Development standards and guidelines

---
```

### Step 6: Commit and Push

```bash
git add SECURITY_ANALYTICS-Documentation/
git add Home.md  # if you updated it
git commit -m "docs: Add comprehensive SECURITY_ANALYTICS documentation

Add 6 new wiki pages with complete documentation for data warehouse"
git push origin main
```

---

## Data Model Wiki Enhancement Plan

Once the new wikis are uploaded, we'll enhance the existing **Data Model** wiki with auto-generated ERDs.

### Current Data Model Wiki

Based on the navigation, there's already a "Data Model" page. We need to:
1. Review its current content (don't overwrite)
2. Add new sections with auto-generated ERDs
3. Use metadata repository data

### ERD Enhancement Steps

1. **Execute GENERATE_ERD_FROM_METADATA.sql**
   ```bash
   python run_sql_script.py --script 01_SQL_SCRIPTS/GENERATE_ERD_FROM_METADATA.sql
   ```

2. **Generate ERD visualizations** from exported data
   - Use Mermaid syntax (Azure DevOps supports it)
   - Or use dbdiagram.io / draw.io

3. **Add new section to Data-Model.md**:
   ```markdown
   ## Automated Entity Relationship Diagrams

   Generated from metadata repository (updated daily at 6:00 AM EST).

   ### Metadata Repository ERD
   [ERD diagram here]

   ### Service-Specific ERDs

   #### SentinelOne
   [ERD diagram here]

   #### CybelAngel
   [ERD diagram here]

   [etc...]
   ```

4. **Commit and push** the enhanced Data Model

---

## Updated PowerShell Script Configuration

The script needs to be updated to handle existing files properly.

**Key Changes**:
1. ✅ Don't fail if wiki repo already exists
2. ✅ Create SECURITY_ANALYTICS-Documentation subfolder
3. ✅ Copy only our 6 wikis to subfolder
4. ✅ Optionally update Home.md with links
5. ✅ Preserve all existing files

---

## Execution Plan

### Phase 1: Upload New Wikis (TODAY)
1. Run updated script to clone existing wiki repo
2. Review existing files (take inventory)
3. Create SECURITY_ANALYTICS-Documentation folder
4. Copy 6 new wikis
5. Optionally update Home.md
6. Commit and push

### Phase 2: Enhance Data Model Wiki (AFTER PHASE 1)
1. Execute GENERATE_ERD_FROM_METADATA.sql
2. Export ERD data
3. Generate visual ERDs
4. Clone wiki repo again
5. Update Data-Model.md with new ERD section
6. Commit and push

---

## Safety Checklist

Before pushing:
- [ ] Backup branch created
- [ ] Only SECURITY_ANALYTICS-Documentation folder has new files
- [ ] No existing files modified (except optionally Home.md)
- [ ] Git status shows only expected changes
- [ ] Dry run completed successfully

---

## Next Action

Execute the updated script:
```powershell
powershell.exe -ExecutionPolicy Bypass -File ".\upload_wikis_simple.ps1"
```

The script should now:
1. Clone successfully (repo exists)
2. Show existing files
3. Create new subfolder
4. Copy 6 wikis
5. Ask for confirmation before pushing

---

**Document Created**: 2025-10-24
**Status**: Ready to execute
**Risk Level**: Low (adding new folder, not modifying existing)
