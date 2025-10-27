# Quick Connection Guide - All Platforms

**Purpose**: Quick reference for connecting to all platforms used in development
**Audience**: Development sessions (for quick reconnection)
**Last Updated**: 2025-10-25

---

## Table of Contents

1. [Snowflake (SnowSQL)](#snowflake-snowsql)
2. [Snowflake (SnowCLI)](#snowflake-snowcli)
3. [Azure DevOps](#azure-devops)
4. [Git (Local Repository)](#git-local-repository)
5. [GitHub (Mirror)](#github-mirror)
6. [Python Snowpark](#python-snowpark)
7. [Quick Troubleshooting](#quick-troubleshooting)

---

## Snowflake (SnowSQL)

### Quick Connect

```bash
# Standard connection (SSO with Okta)
snowsql -a GenericCorp-CRH_EDW -u fuad.onate@CompanyX.com --authenticator externalbrowser -w DEV_WH -d DEV_REPORTING -s SECURITY_ANALYTICS -r DEV_DEVELOPER

# With query
snowsql -a GenericCorp-CRH_EDW -u fuad.onate@CompanyX.com --authenticator externalbrowser -w DEV_WH -d DEV_REPORTING -s SECURITY_ANALYTICS -r DEV_DEVELOPER -q "SHOW TABLES;"

# Execute SQL file
snowsql -a GenericCorp-CRH_EDW -u fuad.onate@CompanyX.com --authenticator externalbrowser -w DEV_WH -d DEV_REPORTING -s SECURITY_ANALYTICS -r DEV_DEVELOPER -f script.sql
```

### Connection Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `-a` | `GenericCorp-CRH_EDW` | Account identifier |
| `-u` | `fuad.onate@CompanyX.com` | Username |
| `--authenticator` | `externalbrowser` | SSO via Okta (ALWAYS use this) |
| `-w` | `DEV_WH` | Warehouse (Medium size) |
| `-d` | `DEV_REPORTING` | Database |
| `-s` | `SECURITY_ANALYTICS` | Schema |
| `-r` | `DEV_DEVELOPER` | Role |
| `-q` | `"SQL QUERY"` | Execute query |
| `-f` | `script.sql` | Execute SQL file |

### Environment Variables (Optional)

```bash
# Set in Windows
set SNOWSQL_ACCOUNT=GenericCorp-CRH_EDW
set SNOWSQL_USER=fuad.onate@CompanyX.com
set SNOWSQL_AUTHENTICATOR=externalbrowser
set SNOWSQL_WAREHOUSE=DEV_WH
set SNOWSQL_DATABASE=DEV_REPORTING
set SNOWSQL_SCHEMA=SECURITY_ANALYTICS
set SNOWSQL_ROLE=DEV_DEVELOPER

# Then connect simply
snowsql
```

### Common Commands

```bash
# List Streamlit apps
snowsql -a GenericCorp-CRH_EDW -u fuad.onate@CompanyX.com --authenticator externalbrowser -w DEV_WH -d DEV_REPORTING -s SECURITY_ANALYTICS -r DEV_DEVELOPER -q "SHOW STREAMLITS IN SCHEMA DEV_REPORTING.SECURITY_ANALYTICS;"

# Check stage files
snowsql -a GenericCorp-CRH_EDW -u fuad.onate@CompanyX.com --authenticator externalbrowser -w DEV_WH -d DEV_REPORTING -s SECURITY_ANALYTICS -r DEV_DEVELOPER -q "LIST @STREAMLIT_APPS_STAGE;"

# Check tasks
snowsql -a GenericCorp-CRH_EDW -u fuad.onate@CompanyX.com --authenticator externalbrowser -w DEV_WH -d DEV_TRANSFORMATION -s METADATA -r DEV_DEVELOPER -q "SHOW TASKS;"
```

---

## Snowflake (SnowCLI)

### Installation

```bash
# Install via pip
pip install snowflake-cli

# Verify installation
snow --version
```

### Quick Connect

```bash
# Configure connection (one-time setup)
snow connection add
# Enter details when prompted:
# - Connection name: crh_dev
# - Account: GenericCorp-CRH_EDW
# - User: fuad.onate@CompanyX.com
# - Authenticator: externalbrowser
# - Warehouse: DEV_WH
# - Database: DEV_REPORTING
# - Schema: SECURITY_ANALYTICS
# - Role: DEV_DEVELOPER

# Use connection
snow connection test --connection crh_dev

# Execute SQL
snow sql -q "SHOW TABLES;" --connection crh_dev
```

### Common Commands

```bash
# List connections
snow connection list

# Execute SQL file
snow sql -f script.sql --connection crh_dev

# Deploy Streamlit app
snow streamlit deploy --connection crh_dev

# List Streamlit apps
snow streamlit list --connection crh_dev
```

---

## Azure DevOps

### Web Access

**URL**: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW

**Organization**: `CompanyX`
**Project**: `GIS - SECURITY_ANALYTICS - DW`
**Repository**: `GIS - SECURITY_ANALYTICS - DW`

### Quick Links

- **Repository**: https://dev.azure.com/CompanyX/_git/GIS%20-%20ITSECKPI%20-%20DW
- **Wiki**: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_wiki/wikis/
- **Boards**: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_boards
- **Pipelines**: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_build

### Azure CLI

```bash
# Login
az login

# Set default organization and project
az devops configure --defaults organization=https://dev.azure.com/CompanyX project="GIS - SECURITY_ANALYTICS - DW"

# List repositories
az repos list

# Create work item
az boards work-item create --title "Task title" --type "Task"
```

---

## Git (Local Repository)

### Repository Location

```
C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\project-repo\
```

### Quick Commands

```bash
# Navigate to repo
cd C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\project-repo

# Check status
git status

# Check remotes
git remote -v

# Pull latest changes
git pull origin main

# Add files
git add .

# Commit
git commit -m "commit message"

# Push to Azure DevOps
git push origin main
```

### Remote Configuration

```bash
# View remotes
git remote -v

# Output:
# origin  https://dev.azure.com/CompanyX/_git/GIS%20-%20ITSECKPI%20-%20DW (fetch)
# origin  https://dev.azure.com/CompanyX/_git/GIS%20-%20ITSECKPI%20-%20DW (push)

# Add remote (if needed)
git remote add origin https://dev.azure.com/CompanyX/_git/GIS%20-%20ITSECKPI%20-%20DW
```

### Git Authentication

**Method**: SSO via web browser (automatic)

When pushing/pulling, browser will open for Okta authentication.

### Common Workflows

#### Push Changes to Azure DevOps

```bash
cd project-repo
git status
git add .
git commit -m "descriptive message

Co-Authored-By: Fuad Onate <fuad.onate@CompanyX.com>"
git push origin main
```

#### Pull Latest Changes

```bash
cd project-repo
git pull origin main
```

#### Create Branch

```bash
git checkout -b feature/new-feature
git push origin feature/new-feature
```

---

## GitHub (Mirror)

### Repository

**URL**: https://github.com/fos-CompanyX/snowflake-SECURITY_ANALYTICS-datawarehouse-dev

**Organization**: `fos-CompanyX`
**Repository**: `snowflake-SECURITY_ANALYTICS-datawarehouse-dev`

### Quick Commands

```bash
# Add GitHub remote (if not already added)
git remote add github https://github.com/fos-CompanyX/snowflake-SECURITY_ANALYTICS-datawarehouse-dev.git

# View remotes
git remote -v

# Push to GitHub
git push github main

# Pull from GitHub
git pull github main
```

### GitHub Authentication

**Method**: Personal Access Token (PAT) or SSH key

**Setup PAT**:
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` scope
3. Save token securely
4. Use token as password when prompted

**Setup SSH** (recommended):
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "fuad.onate@CompanyX.com"

# Add key to SSH agent
ssh-add ~/.ssh/id_ed25519

# Add public key to GitHub
# Copy contents of ~/.ssh/id_ed25519.pub
# GitHub → Settings → SSH keys → Add SSH key

# Test connection
ssh -T git@github.com
```

---

## Python Snowpark

### Quick Connect

```python
from snowflake.snowpark import Session

# Connection parameters
connection_parameters = {
    "account": "GenericCorp-CRH_EDW",
    "user": "fuad.onate@CompanyX.com",
    "authenticator": "externalbrowser",  # SSO with Okta
    "warehouse": "DEV_WH",
    "database": "DEV_REPORTING",
    "schema": "SECURITY_ANALYTICS",
    "role": "DEV_DEVELOPER"
}

# Create session
session = Session.builder.configs(connection_parameters).create()

# Test connection
print(session.sql("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE()").collect())

# Query example
df = session.sql("SELECT * FROM TABLE_REGISTRY LIMIT 10").to_pandas()
print(df)

# Close session
session.close()
```

### Using snowflake_config.json

```python
import json
from snowflake.snowpark import Session

# Load config
with open("snowflake_config.json", "r") as f:
    config = json.load(f)

# Create session
session = Session.builder.configs(config).create()

# Use session
result = session.sql("SHOW TABLES").collect()

# Close
session.close()
```

### Common Operations

```python
# Execute SQL
df = session.sql("SELECT * FROM MY_TABLE").to_pandas()

# Write DataFrame to Snowflake
df.to_snowflake("MY_TABLE", mode="overwrite")

# Call stored procedure
session.call("SP_REFRESH_METADATA")

# List tables
tables = session.sql("SHOW TABLES").collect()

# Create table from DataFrame
session.create_dataframe(df).write.save_as_table("NEW_TABLE")
```

---

## Quick Troubleshooting

### Snowflake Connection Issues

**Problem**: "Authentication failed"
```bash
# Solution: Ensure using externalbrowser authenticator
snowsql -a GenericCorp-CRH_EDW -u fuad.onate@CompanyX.com --authenticator externalbrowser -w DEV_WH
```

**Problem**: "Role not found"
```bash
# Solution: Verify role name (check available roles)
snowsql -a GenericCorp-CRH_EDW -u fuad.onate@CompanyX.com --authenticator externalbrowser -q "SHOW ROLES;"
```

**Problem**: "Warehouse suspended"
```bash
# Solution: Warehouse will auto-resume, or manually resume
snowsql -a GenericCorp-CRH_EDW -u fuad.onate@CompanyX.com --authenticator externalbrowser -q "ALTER WAREHOUSE DEV_WH RESUME;"
```

### Git Connection Issues

**Problem**: "fatal: 'azure' does not appear to be a git repository"
```bash
# Solution: Remote is named 'origin' not 'azure'
git remote -v
git push origin main
```

**Problem**: "Authentication failed"
```bash
# Solution: Browser should open for SSO - allow popups
# Or check credentials
git config --list
```

**Problem**: "Merge conflict"
```bash
# Solution: Pull first, then resolve conflicts
git pull origin main
# Resolve conflicts in files
git add .
git commit -m "resolve merge conflicts"
git push origin main
```

### Python Snowpark Issues

**Problem**: "ModuleNotFoundError: No module named 'snowflake.snowpark'"
```bash
# Solution: Install Snowpark
pip install snowflake-snowpark-python
```

**Problem**: "Browser not opening for SSO"
```bash
# Solution: Check firewall/antivirus settings
# Or manually copy URL from error message
```

**Problem**: "Session timeout"
```python
# Solution: Recreate session
session = Session.builder.configs(connection_parameters).create()
```

---

## Configuration Files Reference

### snowflake_config.json

**Location**: `C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\snowflake_config.json`

**Template**:
```json
{
  "account": "GenericCorp-CRH_EDW",
  "user": "fuad.onate@CompanyX.com",
  "authenticator": "externalbrowser",
  "warehouse": "DEV_WH",
  "database": "DEV_REPORTING",
  "schema": "SECURITY_ANALYTICS",
  "role": "DEV_DEVELOPER"
}
```

**IMPORTANT**: This file is in `.gitignore` - never commit it!

### .gitignore

**Location**: `C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\.gitignore`

**Must Include**:
```
# Credentials
snowflake_config.json
.env
credentials.json

# Logs
*.log
deployment_logs/
execution_logs/

# Temporary
*.tmp
*.bak
~$*

# Python
__pycache__/
*.pyc
.venv/
venv/

# Email drafts
EMAIL_DRAFT_*.md
EMAIL_*.md

# Local dev guidelines (keep local only)
00_LOCAL_DEV_GUIDELINES/
```

---

## Environment-Specific Settings

### DEV Environment

| Setting | Value |
|---------|-------|
| Account | GenericCorp-CRH_EDW |
| Database | DEV_REPORTING |
| Schema | SECURITY_ANALYTICS |
| Warehouse | DEV_WH |
| Role | DEV_DEVELOPER |

### PROD Environment

| Setting | Value |
|---------|-------|
| Account | GenericCorp-CRH_EDW |
| Database | PRD_REPORTING |
| Schema | SECURITY_ANALYTICS |
| Warehouse | PRD_WH |
| Role | PRD_DEVELOPER |

**IMPORTANT**: Always double-check environment before executing!

---

## Quick Command Cheatsheet

### Most Common Commands

```bash
# Snowflake - Show Streamlit apps
snowsql -a GenericCorp-CRH_EDW -u fuad.onate@CompanyX.com --authenticator externalbrowser -w DEV_WH -d DEV_REPORTING -s SECURITY_ANALYTICS -r DEV_DEVELOPER -q "SHOW STREAMLITS;"

# Git - Push changes
cd project-repo && git add . && git commit -m "message" && git push origin main

# Python - Run deployment script
python 02_PYTHON_SCRIPTS/deploy_with_progress.py

# Check Snowflake connection
snowsql -a GenericCorp-CRH_EDW -u fuad.onate@CompanyX.com --authenticator externalbrowser -q "SELECT CURRENT_USER(), CURRENT_ROLE();"
```

### Aliases (Optional - for faster access)

Create file: `C:\Users\fonat\.bash_aliases` or add to `.bashrc`:

```bash
# Snowflake aliases
alias snow-dev='snowsql -a GenericCorp-CRH_EDW -u fuad.onate@CompanyX.com --authenticator externalbrowser -w DEV_WH -d DEV_REPORTING -s SECURITY_ANALYTICS -r DEV_DEVELOPER'
alias snow-tables='snow-dev -q "SHOW TABLES;"'
alias snow-apps='snow-dev -q "SHOW STREAMLITS;"'

# Git aliases
alias gst='git status'
alias gaa='git add .'
alias gcm='git commit -m'
alias gpo='git push origin main'

# Project aliases
alias cdproj='cd C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV'
alias cdrepo='cd C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\project-repo'
```

---

## Testing Connections

### Quick Connection Test Script

**File**: `00_LOCAL_DEV_GUIDELINES/test_all_connections.py`

```python
import subprocess
import sys

def test_snowsql():
    """Test SnowSQL connection"""
    print("\n[1/3] Testing SnowSQL connection...")
    try:
        result = subprocess.run([
            "snowsql",
            "-a", "GenericCorp-CRH_EDW",
            "-u", "fuad.onate@CompanyX.com",
            "--authenticator", "externalbrowser",
            "-q", "SELECT CURRENT_USER();"
        ], capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print("✅ SnowSQL connection successful")
            return True
        else:
            print("❌ SnowSQL connection failed")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ SnowSQL error: {e}")
        return False

def test_git():
    """Test Git connection"""
    print("\n[2/3] Testing Git connection...")
    try:
        result = subprocess.run([
            "git", "remote", "-v"
        ], capture_output=True, text=True)

        if "dev.azure.com" in result.stdout:
            print("✅ Git configured for Azure DevOps")
            return True
        else:
            print("❌ Git remote not configured")
            return False
    except Exception as e:
        print(f"❌ Git error: {e}")
        return False

def test_snowpark():
    """Test Snowpark connection"""
    print("\n[3/3] Testing Python Snowpark...")
    try:
        from snowflake.snowpark import Session

        connection_parameters = {
            "account": "GenericCorp-CRH_EDW",
            "user": "fuad.onate@CompanyX.com",
            "authenticator": "externalbrowser",
            "warehouse": "DEV_WH",
            "database": "DEV_REPORTING",
            "schema": "SECURITY_ANALYTICS",
            "role": "DEV_DEVELOPER"
        }

        session = Session.builder.configs(connection_parameters).create()
        result = session.sql("SELECT CURRENT_USER()").collect()
        session.close()

        print("✅ Snowpark connection successful")
        return True
    except Exception as e:
        print(f"❌ Snowpark error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("CONNECTION TESTS")
    print("=" * 60)

    results = []
    results.append(test_snowsql())
    results.append(test_git())
    results.append(test_snowpark())

    print("\n" + "=" * 60)
    print(f"RESULTS: {sum(results)}/3 connections successful")
    print("=" * 60)

    if all(results):
        print("✅ All connections working!")
        sys.exit(0)
    else:
        print("❌ Some connections failed - check errors above")
        sys.exit(1)
```

**Run Test**:
```bash
python 00_LOCAL_DEV_GUIDELINES/test_all_connections.py
```

---

## Notes for Future Sessions

### Session Start Checklist

- [ ] Review this file (`QUICK_CONNECTION_GUIDE.md`)
- [ ] Review `LOCAL_DEV_BEST_PRACTICES.md`
- [ ] Test Snowflake connection
- [ ] Check Git status
- [ ] Pull latest changes from Azure DevOps

### Session End Checklist

- [ ] Commit all changes to Git
- [ ] Push to Azure DevOps
- [ ] Update session documentation
- [ ] No credentials in committed files

---

**Created**: 2025-10-25
**Author**: Fuad Onate
**Purpose**: Quick reference for all platform connections
**Status**: Active - Keep updated
**Location**: `00_LOCAL_DEV_GUIDELINES/QUICK_CONNECTION_GUIDE.md`
