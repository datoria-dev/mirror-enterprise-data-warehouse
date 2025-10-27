# Automation Scripts Documentation

**Created**: 2025-10-25
**Purpose**: Automated scripts for Snowflake connection testing and OneDrive backup
**Location**: `C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\`

---

## 📋 Overview

This repository contains automation scripts for:

1. **Snowflake Connection Testing** - Automated SSO (Okta) connection tests
2. **OneDrive Backup** - Safe backup and removal of OneDrive folder
3. **Azure DevOps Preparation** - Prepare repository for upload to Azure DevOps

---

## 🚀 Quick Start

### Test Snowflake Connection

```batch
cd C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV
.\test_snowsql_connection.bat
```

This will:
- ✅ Check if SnowSQL is installed
- ✅ Load configuration from `snowflake_config.json`
- ✅ Test SSO connection to Snowflake
- ✅ Verify access to metadata tables
- ✅ Generate connection report

### Backup OneDrive

```batch
cd C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV
.\backup_onedrive.bat
```

This will:
- ✅ Calculate OneDrive folder size
- ✅ Check available disk space
- ✅ Copy all files to backup folder
- ✅ Verify backup integrity
- ✅ Optionally remove OneDrive folder
- ✅ Generate backup log (JSON)

---

## 📁 File Structure

```
Snowflake_ITSECKPI_Project_DEV/
├── 02_PYTHON_SCRIPTS/
│   ├── snowflake_connection_test.py    # SnowSQL connection testing
│   └── onedrive_backup_automation.py   # OneDrive backup automation
│
├── test_snowsql_connection.bat         # Quick SnowSQL test runner
├── backup_onedrive.bat                 # Quick OneDrive backup runner
├── prepare_for_azure_devops.ps1        # Azure DevOps prep script
│
├── snowflake_config.json               # Snowflake connection config
└── README_AUTOMATION_SCRIPTS.md        # This file
```

---

## 🔧 Detailed Documentation

### 1. Snowflake Connection Test (`snowflake_connection_test.py`)

**Purpose**: Automated testing of Snowflake connection with SSO (Okta)

**Features**:
- Checks SnowSQL installation
- Loads configuration from `snowflake_config.json`
- Tests SSO authentication
- Validates metadata table access
- Generates detailed test report

**Configuration** (`snowflake_config.json`):
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

**Usage**:
```python
# Direct Python execution
python 02_PYTHON_SCRIPTS/snowflake_connection_test.py

# Via batch file
.\test_snowsql_connection.bat
```

**Output**:
```
==============================================================
Snowflake Connection Test with SSO (Okta)
==============================================================

[Step 1/3] Checking SnowSQL installation...
✓ SnowSQL installed: Version: 1.3.1

[Step 2/3] Loading configuration...
✓ Configuration loaded from: snowflake_config.json

[Step 3/3] Testing Snowflake connection...
Opening browser for SSO authentication...

✓ Connection successful!

Connection details:
+--------------------------+----------------+---------------------+--------------------+------------------+
| CURRENT_USER()           | CURRENT_ROLE() | CURRENT_WAREHOUSE() | CURRENT_DATABASE() | CURRENT_SCHEMA() |
|--------------------------+----------------+---------------------+--------------------+------------------|
| FUAD.ONATE@CompanyX.COM | DEV_DEVELOPER  | DEV_WH              | DEV_TRANSFORMATION | METADATA         |
+--------------------------+----------------+---------------------+--------------------+------------------+

==============================================================
Testing Metadata Access
==============================================================

[12:34:56] Testing: List tables
✓ List tables - SUCCESS

[12:34:58] Testing: Count TABLE_REGISTRY
✓ Count TABLE_REGISTRY - SUCCESS

[12:35:00] Testing: Count COLUMN_METADATA
✓ Count COLUMN_METADATA - SUCCESS

[12:35:02] Testing: Count SERVICE_CATALOG
✓ Count SERVICE_CATALOG - SUCCESS

==============================================================
Test Summary
==============================================================

Total tests: 5
Passed: 5
Failed: 0

✓ All tests passed! Snowflake connection is ready.
```

**Tests Performed**:
1. SnowSQL installation check
2. Connection with SSO authentication
3. List tables in METADATA schema
4. Count records in TABLE_REGISTRY
5. Count records in COLUMN_METADATA
6. Count records in SERVICE_CATALOG

---

### 2. OneDrive Backup Automation (`onedrive_backup_automation.py`)

**Purpose**: Safely backup all OneDrive content and optionally remove OneDrive folder

**Features**:
- Calculates total size of OneDrive folder
- Checks available disk space
- Copies all files with metadata preservation
- Verifies backup integrity (file count comparison)
- Progress tracking during copy
- Generates JSON log file
- Safe deletion with double confirmation

**Configuration**:
```python
ONEDRIVE_SOURCE = Path(r"C:\Users\fonat\OneDrive")
BACKUP_BASE = Path(r"C:\Users\fonat\Documents")
BACKUP_NAME = f"OneDrive_Backup_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}"
```

**Usage**:
```python
# Direct Python execution
python 02_PYTHON_SCRIPTS/onedrive_backup_automation.py

# Via batch file
.\backup_onedrive.bat
```

**Output Example**:
```
==============================================================
OneDrive Backup and Removal Automation
==============================================================

[Step 1/6] Checking source folder...
✓ Source folder found: C:\Users\fonat\OneDrive

[Step 2/6] Calculating source size...
Calculating source folder size...

Source folder statistics:
  Files: 15,847
  Folders: 2,156
  Total size: 4.23 GB

[Step 3/6] Checking disk space...
Checking available disk space...
  Drive: C:\
  Free space: 125.67 GB
  Required: 4.23 GB
✓ Sufficient disk space available

[Step 4/6] Creating backup...
Creating backup folder: C:\Users\fonat\Documents\OneDrive_Backup_2025-10-25_143022
✓ Backup folder created

Copying files (this may take several minutes)...
------------------------------------------------------------
  Copied 100 files... (45.12 MB)
  Copied 200 files... (98.45 MB)
  ...
  Copied 15,800 files... (4.20 GB)
------------------------------------------------------------

✓ Backup completed!
  Files copied: 15,847
  Folders copied: 2,156
  Total size: 4.23 GB

[Step 5/6] Verifying backup...
Verifying backup integrity...
  Source files: 15,847
  Backup files: 15,847
✓ File counts match! Backup is complete.

✓ Backup log saved: C:\Users\fonat\Documents\OneDrive_Backup_2025-10-25_143022_log.json

[Step 6/6] OneDrive folder removal...

==============================================================
WARNING: About to DELETE OneDrive folder!
==============================================================

Folder to delete: C:\Users\fonat\OneDrive
Backup location: C:\Users\fonat\Documents\OneDrive_Backup_2025-10-25_143022

Are you ABSOLUTELY SURE you want to delete? (yes/no): yes

Deleting OneDrive folder...
✓ OneDrive folder deleted successfully!

==============================================================
Backup Complete!
==============================================================

Backup location: C:\Users\fonat\Documents\OneDrive_Backup_2025-10-25_143022
Log file: C:\Users\fonat\Documents\OneDrive_Backup_2025-10-25_143022_log.json

Files backed up: 15,847
Total size: 4.23 GB
```

**Backup Log** (`OneDrive_Backup_2025-10-25_143022_log.json`):
```json
{
  "start_time": "2025-10-25T14:30:22.123456",
  "end_time": "2025-10-25T14:45:18.654321",
  "source": "C:\\Users\\fonat\\OneDrive",
  "backup": "C:\\Users\\fonat\\Documents\\OneDrive_Backup_2025-10-25_143022",
  "files_copied": 15847,
  "folders_copied": 2156,
  "total_size_bytes": 4543210567,
  "errors": []
}
```

**Safety Features**:
- ✅ Source existence check
- ✅ Disk space verification (with 10% buffer)
- ✅ Progress tracking
- ✅ Error handling for locked files
- ✅ File count verification
- ✅ Double confirmation before deletion
- ✅ Detailed error logging

---

### 3. Azure DevOps Preparation (`prepare_for_azure_devops.ps1`)

**Purpose**: Prepare repository for upload to Azure DevOps Repos

**Features**:
- Shows current git status
- Stages all new files
- Shows what will be committed
- Provides commit command with conventional commit message
- Provides push command

**Usage**:
```powershell
cd C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV
.\prepare_for_azure_devops.ps1
```

**Output**:
```
========================================
Prepare for Azure DevOps Upload
========================================

[Step 1/5] Checking Git status...

On branch main
Untracked files:
  02_PYTHON_SCRIPTS/snowflake_connection_test.py
  02_PYTHON_SCRIPTS/onedrive_backup_automation.py
  test_snowsql_connection.bat
  backup_onedrive.bat
  ...

[Step 2/5] Adding all new files...

[Step 3/5] Showing staged changes...

On branch main
Changes to be committed:
  new file:   02_PYTHON_SCRIPTS/snowflake_connection_test.py
  new file:   02_PYTHON_SCRIPTS/onedrive_backup_automation.py
  ...

[Step 4/5] Review changes before commit...

Files to be committed:
02_PYTHON_SCRIPTS/snowflake_connection_test.py
02_PYTHON_SCRIPTS/onedrive_backup_automation.py
test_snowsql_connection.bat
backup_onedrive.bat
prepare_for_azure_devops.ps1

[Step 5/5] Ready to commit and push

To commit and push to Azure DevOps, run:

  git commit -m "feat: add automation scripts for SnowSQL and OneDrive backup"

  git push origin main

========================================
Preparation Complete
========================================
```

---

## 🎯 Use Cases

### Daily Development Workflow

**Morning Setup**:
```batch
# Test Snowflake connection
.\test_snowsql_connection.bat
```

**Before Deploying Apps**:
```batch
# Verify metadata access
.\test_snowsql_connection.bat
```

**End of Day**:
```powershell
# Prepare for Azure DevOps push
.\prepare_for_azure_devops.ps1

# Commit and push
git commit -m "feat: your changes here"
git push origin main
```

### One-Time Setup Tasks

**Remove OneDrive**:
```batch
# Backup and remove OneDrive
.\backup_onedrive.bat
```

**After OneDrive Removal**:
- ✅ All files backed up to `Documents\OneDrive_Backup_YYYY-MM-DD_HHMMSS\`
- ✅ OneDrive folder deleted
- ✅ Backup log saved as JSON
- ✅ No more cloud sync conflicts with Git repos

---

## 📊 Integration with Azure DevOps

### Recommended Workflow

1. **Work Locally** (in `MYORG_LOCAL\`)
   ```batch
   cd C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV
   ```

2. **Make Changes** (edit files, create scripts, etc.)

3. **Test** (run automated tests)
   ```batch
   .\test_snowsql_connection.bat
   ```

4. **Prepare** (stage all changes)
   ```powershell
   .\prepare_for_azure_devops.ps1
   ```

5. **Commit** (with conventional commit message)
   ```bash
   git commit -m "feat: add new feature"
   # or
   git commit -m "fix: resolve connection issue"
   # or
   git commit -m "docs: update documentation"
   ```

6. **Push** (to Azure DevOps)
   ```bash
   git push origin main
   ```

### Conventional Commit Messages

Use these prefixes for commits:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

---

## 🔍 Troubleshooting

### SnowSQL Connection Issues

**Problem**: "SnowSQL not found"
```
✗ SnowSQL not found at: C:\Program Files\Snowflake SnowSQL\snowsql.exe
```

**Solution**:
```batch
# Run as Administrator
.\reinstall_snowsql.bat
```

---

**Problem**: "Connection timeout"
```
ERROR: Connection timeout - SSO authentication may have failed
```

**Solution**:
1. Check that browser opened for SSO
2. Complete Okta authentication
3. Check network connection
4. Retry: `.\test_snowsql_connection.bat`

---

### OneDrive Backup Issues

**Problem**: "Not enough disk space"
```
✗ Not enough disk space!
Drive: C:\
Free space: 2.15 GB
Required: 4.23 GB
```

**Solution**:
1. Free up disk space (delete temp files, empty recycle bin)
2. Change backup location to different drive
3. Retry: `.\backup_onedrive.bat`

---

**Problem**: "File counts don't match"
```
⚠ File counts don't match!
Source files: 15,847
Backup files: 15,820
Missing: 27 files
```

**Solution**:
1. Check backup log for errors: `OneDrive_Backup_*_log.json`
2. Manually copy missing files
3. Re-run verification
4. If acceptable, proceed with deletion

---

**Problem**: "Failed to delete OneDrive folder"
```
✗ Failed to delete OneDrive folder: Access denied
```

**Solution**:
1. Close all programs (File Explorer, editors, etc.)
2. Run script as Administrator
3. Manually delete folder in File Explorer
4. Check backup is safe first!

---

## 📝 Best Practices

### Git Repository Management

✅ **DO**:
- Keep repos in local folders (`C:\Users\fonat\Documents\MYORG_LOCAL\`)
- Commit frequently with meaningful messages
- Test before committing
- Use conventional commit messages
- Push to Azure DevOps regularly

❌ **DON'T**:
- Store repos in OneDrive/Dropbox (causes sync conflicts)
- Commit without testing
- Use vague commit messages ("fixes", "updates")
- Leave large uncommitted changes

### Snowflake Connection

✅ **DO**:
- Test connection daily
- Use SSO (Okta) authentication
- Keep `snowflake_config.json` updated
- Monitor metadata table counts

❌ **DON'T**:
- Hardcode credentials in scripts
- Share `snowflake_config.json` publicly
- Skip connection tests before deployment

### Backup Strategy

✅ **DO**:
- Backup before major changes
- Verify backup integrity
- Keep backup logs
- Store backups on separate drive (optional)

❌ **DON'T**:
- Delete source before verifying backup
- Skip disk space check
- Ignore backup errors

---

## 🚀 Next Steps

After setting up these automation scripts:

1. **Test SnowSQL Connection**:
   ```batch
   .\test_snowsql_connection.bat
   ```

2. **Backup OneDrive** (if needed):
   ```batch
   .\backup_onedrive.bat
   ```

3. **Commit to Azure DevOps**:
   ```powershell
   .\prepare_for_azure_devops.ps1
   git commit -m "feat: add automation scripts"
   git push origin main
   ```

4. **Deploy Streamlit Apps** (from previous session):
   - 18 apps ready in `13_STREAMLIT_COMPLETE\`
   - All fixes applied (download buttons, alerts, st.rerun)
   - Use deployment scripts in `03_PYTHON_SCRIPTS\`

---

## 📞 Support

For issues or questions:
- Check troubleshooting section above
- Review log files (JSON format)
- Test connections with `.\test_snowsql_connection.bat`

---

**Version**: 1.0
**Last Updated**: 2025-10-25
**Maintained By**: Fuad Onate
