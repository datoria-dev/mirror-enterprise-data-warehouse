# Manual Upload Instructions for GitHub DEV Repository

## Status

The Git repository has been prepared locally with all project files, but the `git push` command is experiencing HTTP 408 timeout errors due to repository size (278 files, ~290K lines of code).

## What's Ready

✅ Local repository fully configured and committed
✅ All large files excluded (.pbix, .pptx files)
✅ .gitignore properly configured
✅ All references to development tools removed
✅ 6 commits ready to push:
- 103b5e0: Initial README with architecture diagram
- cb0d10b: Comprehensive enterprise architecture
- 7e6c8b5: Updated architecture diagram
- 99ecb04: Complete project setup
- 9209870: Exclude Power BI files
- 2e85b65: Exclude large files (current)

## Files Excluded (Upload Manually Later)

The following large files have been excluded and should be uploaded manually through GitHub web interface after the main project is uploaded:

- `06_SOURCE_DATA/SecurityMetrics_dev.pbix` (904.80 MB)
- `06_SOURCE_DATA/SecurityMetrics_dev_ZF_NoZS.pbix` (325.31 MB)
- `06_SOURCE_DATA/SecurityMetrics_dev_SnowFlake.pbix` (312.55 MB)
- `06_SOURCE_DATA/GIS Offsite Event - Snowflake.pptx` (~15MB)
- `06_SOURCE_DATA/GIS-Data-Platform.pptx` (~12MB)

## Option 1: GitHub Web Interface Upload (RECOMMENDED)

### Step 1: Access Repository
1. Go to: https://github.com/fos-CompanyX/snowflake-SECURITY_ANALYTICS-datawarehouse-dev
2. Sign in if needed

### Step 2: Upload Folders

You'll need to upload folders in batches. Here's the recommended order:

#### Batch 1: Documentation and Configuration (Small files)
```
01_SQL_SCRIPTS/
02_PYTHON_SCRIPTS/
03_CONFIG/
03_DOCUMENTATION/
README.md
.gitignore
```

**How to upload:**
1. Click "Add file" → "Upload files"
2. Drag the folders from Windows Explorer
3. Scroll down and add commit message: "Initial project structure and documentation"
4. Click "Commit changes"

#### Batch 2: Output and Logs
```
04_OUTPUT/
05_LOGS/
05_QUERY_RESULTS/
```

**Commit message:** "Add output directories and query results"

#### Batch 3: Source Data and Streamlit Apps
```
06_SOURCE_DATA/ (WITHOUT .pbix and .pptx files)
07_STREAMLIT_APPS/
```

**Commit message:** "Add source data and Streamlit applications"

#### Batch 4: Power BI and Remaining Files
```
08_POWERBI_DASHBOARDS/
09_SERVICENOW_INTEGRATION/
10_DATA_DICTIONARY/
99_ARCHIVE/
```

**Commit message:** "Add dashboards, integrations, and archives"

#### Batch 5: Supporting Files
```
UPDATE_GITHUB_INSTRUCTIONS.md
GITHUB_GITIGNORE.txt
GITHUB_README.md
ARCHITECTURE_DIAGRAMS.md
MANUAL_UPLOAD_INSTRUCTIONS.md (this file)
```

**Commit message:** "Add supporting documentation"

### Step 3: Upload Large Files (Optional)

If you need the .pbix and .pptx files in the repository:

1. Use Git LFS (Large File Storage) - requires command line:
```bash
git lfs install
git lfs track "*.pbix"
git lfs track "*.pptx"
git add .gitattributes
git add 06_SOURCE_DATA/*.pbix
git add 06_SOURCE_DATA/*.pptx
git commit -m "Add large files using Git LFS"
git push dev main
```

2. OR store them elsewhere (Local, AWS S3, etc.) and add links to README

## Option 2: GitHub Desktop (GUI Application)

### Install GitHub Desktop
1. Download from: https://desktop.github.com/
2. Install and sign in with your GitHub account

### Clone Repository
1. Open GitHub Desktop
2. File → Clone Repository
3. URL: https://github.com/fos-CompanyX/snowflake-SECURITY_ANALYTICS-datawarehouse-dev.git
4. Local path: Choose a temporary location (not your current project folder)

### Copy Files
1. Copy all files from current project folder:
   `C:\\Projects\\Snowflake_ITSECKPI_Project\`
2. Paste into the cloned repository folder
3. GitHub Desktop will show all changes

### Commit and Push
1. Review changes in GitHub Desktop
2. Add commit message: "Complete project upload"
3. Click "Commit to main"
4. Click "Push origin"

**Note:** This may also timeout, so try uploading in batches:
- Uncheck some files before committing
- Commit and push in smaller groups
- Repeat until all files are uploaded

## Option 3: Try Git Push Again with Compression

You can try one more git push attempt with maximum compression:

```bash
cd "C:\\Projects\\Snowflake_ITSECKPI_Project"

# Set maximum compression
git config http.postBuffer 1048576000
git config pack.compression 9
git config pack.windowMemory 256m
git config pack.packSizeLimit 50m

# Try pushing
git push dev main --force
```

This will:
- Increase HTTP buffer to 1GB
- Use maximum compression
- Limit pack size to 50MB chunks

**Warning:** This may still take 20-30 minutes and might timeout.

## Option 4: Split Repository into Multiple Commits

If you want to use Git but in smaller chunks:

```bash
cd "C:\\Projects\\Snowflake_ITSECKPI_Project"

# Create a new branch for incremental upload
git checkout -b incremental-upload

# Add files in small groups
git add README.md .gitignore
git commit -m "Step 1: Add README and gitignore"
git push dev incremental-upload

git add 01_SQL_SCRIPTS/ 02_PYTHON_SCRIPTS/
git commit -m "Step 2: Add SQL and Python scripts"
git push dev incremental-upload

git add 03_CONFIG/ 03_DOCUMENTATION/
git commit -m "Step 3: Add configuration and documentation"
git push dev incremental-upload

# Continue for each folder...

# When done, merge to main
git checkout main
git merge incremental-upload
git push dev main
```

## Verification After Upload

Once files are uploaded, verify:

1. **Check file count:**
   - Should have approximately 278 files (excluding large .pbix/.pptx)

2. **Verify key folders exist:**
   - ✅ 01_SQL_SCRIPTS/
   - ✅ 02_PYTHON_SCRIPTS/
   - ✅ 07_STREAMLIT_APPS/
   - ✅ 09_SERVICENOW_INTEGRATION/
   - ✅ 10_DATA_DICTIONARY/

3. **Check README renders correctly:**
   - Architecture diagram should display
   - No references to development tools

4. **Verify .gitignore is working:**
   - No .pbix files in repository
   - No .env files
   - No temporary files

## Current Repository Status

**PROD Repository:** https://github.com/fos-CompanyX/snowflake-SECURITY_ANALYTICS-datawarehouse
- Status: Ready (README only)
- Last Update: Architecture diagram added

**DEV Repository:** https://github.com/fos-CompanyX/snowflake-SECURITY_ANALYTICS-datawarehouse-dev
- Status: Awaiting manual upload
- Next Action: Choose upload method above

## Recommendation

For fastest and most reliable upload:

1. **Use GitHub Web Interface** (Option 1) - Upload in 5 batches
2. This avoids timeout issues completely
3. Takes about 30-45 minutes total
4. No technical knowledge needed

For better Git history:

1. **Use GitHub Desktop** (Option 2) - Easier than command line
2. Upload in smaller commits if main push fails
3. Maintains proper Git structure

## Questions?

- GitHub upload limits: 100MB per file, 100 files per web upload
- For files larger than 100MB: Use Git LFS or external storage
- For help: Check GitHub docs at https://docs.github.com/

---

**Document Created:** 2025-10-21
**Purpose:** Manual upload instructions after git push timeout errors
**Files Ready:** 278 files, ~290K lines of code
**Excluded Large Files:** 5 files (1.5GB total)
