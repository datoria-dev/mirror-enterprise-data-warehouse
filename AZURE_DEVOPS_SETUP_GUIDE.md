# Azure DevOps Repository Setup Guide
## Publishing SECURITY_ANALYTICS Data Warehouse to Azure DevOps

This guide provides step-by-step instructions for creating an identical repository in Azure DevOps (Azure Repos).

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Create Azure DevOps Repository](#create-azure-devops-repository)
3. [Push from Existing Git Repository](#push-from-existing-git-repository)
4. [Azure DevOps-Specific Configuration](#azure-devops-specific-configuration)
5. [Azure Pipelines Setup (Optional)](#azure-pipelines-setup-optional)
6. [Wiki and Documentation](#wiki-and-documentation)
7. [Comparison: GitHub vs Azure DevOps](#comparison-github-vs-azure-devops)

---

## Prerequisites

### Required
- ✅ Azure DevOps account (free tier available)
- ✅ Azure DevOps organization created
- ✅ Existing Git repository (we already have GITHUB_REPO)
- ✅ Git installed locally

### Optional
- Azure CLI installed (for command-line operations)
- Visual Studio or VS Code with Azure DevOps extension

---

## Create Azure DevOps Repository

### Option 1: Azure DevOps Web Portal (Recommended)

#### Step 1: Navigate to Azure DevOps
1. Go to: https://dev.azure.com
2. Sign in with your Microsoft/Azure account
3. Select your **Organization** (or create one)

#### Step 2: Create or Select Project
1. Click **"+ New project"** or select existing project
2. Fill in project details:
   - **Project name**: `SECURITY_ANALYTICS-DataWarehouse` or `Snowflake-Security-KPIs`
   - **Description**:
     ```
     Enterprise IT Security KPI Data Warehouse on Snowflake with automated ETL,
     real-time dashboards, and NIST CSF 2.0-aligned metrics
     ```
   - **Visibility**:
     - **Private**: For internal/company use (recommended)
     - **Public**: For open-source projects
   - **Version control**: Git (not TFVC)
   - **Work item process**: Agile (or your preferred process)
3. Click **"Create"**

#### Step 3: Initialize Repository
1. Go to **Repos** → **Files**
2. You'll see an empty repository
3. Note the repository URL (format: `https://dev.azure.com/{org}/{project}/_git/{repo}`)
4. Keep this page open - we'll use it for push instructions

---

## Push from Existing Git Repository

### Method 1: Add Azure DevOps as Second Remote (Recommended)

This keeps both GitHub and Azure DevOps in sync.

```bash
# Navigate to your GITHUB_REPO
cd "C:\\Projects\\Snowflake_ITSECKPI_Project\GITHUB_REPO"

# Add Azure DevOps as a second remote named 'azure'
# Replace {org}, {project}, and {repo} with your values
git remote add azure https://dev.azure.com/{org}/{project}/_git/{repo}

# Example:
# git remote add azure https://dev.azure.com/fos-CompanyX/SECURITY_ANALYTICS-DataWarehouse/_git/snowflake-SECURITY_ANALYTICS-datawarehouse

# Verify remotes
git remote -v
# Should show:
# origin  https://github.com/fos-CompanyX/snowflake-SECURITY_ANALYTICS-datawarehouse.git (fetch)
# origin  https://github.com/fos-CompanyX/snowflake-SECURITY_ANALYTICS-datawarehouse.git (push)
# azure   https://dev.azure.com/{org}/{project}/_git/{repo} (fetch)
# azure   https://dev.azure.com/{org}/{project}/_git/{repo} (push)

# Push to Azure DevOps
git push -u azure main

# If prompted for credentials:
# - Username: Your Azure DevOps email
# - Password: Personal Access Token (PAT) - see below
```

### Method 2: Create Separate Azure DevOps Folder

If you want completely separate repositories:

```bash
# Create new folder for Azure DevOps
cd "C:\\Projects\\Snowflake_ITSECKPI_Project"
New-Item -ItemType Directory -Path "AZURE_DEVOPS_REPO" -Force

# Copy entire GITHUB_REPO to AZURE_DEVOPS_REPO
Copy-Item -Path "GITHUB_REPO\*" -Destination "AZURE_DEVOPS_REPO\" -Recurse -Force

# Navigate to new folder
cd "AZURE_DEVOPS_REPO"

# Remove existing Git history
Remove-Item -Recurse -Force ".git"

# Initialize new Git repository
git init
git branch -M main
git config user.name "Your Name"
git config user.email "your.email@company.com"

# Add all files
git add .
git commit -m "feat: initial commit - SECURITY_ANALYTICS Data Warehouse

- 3-layer Snowflake data warehouse (550+ objects)
- 52 automation objects (98.1% deployed)
- 12 Streamlit dashboards
- 15 security service integrations
- Top 13 NIST CSF 2.0 KPIs
- $146K annual ROI with 94% reduction in manual operations"

# Add Azure DevOps remote
git remote add origin https://dev.azure.com/{org}/{project}/_git/{repo}

# Push to Azure DevOps
git push -u origin main
```

---

## Azure DevOps Authentication

### Creating a Personal Access Token (PAT)

Azure DevOps uses PATs for authentication instead of passwords.

#### Step 1: Create PAT
1. Click your profile icon (top right) → **Personal access tokens**
2. Click **"+ New Token"**
3. Configure:
   - **Name**: `SECURITY_ANALYTICS Repository Access`
   - **Organization**: Select your org
   - **Expiration**: 90 days (or custom)
   - **Scopes**: Select:
     - ✅ **Code** → Read & Write
     - ✅ **Build** → Read & Execute (if using pipelines)
     - ✅ **Work Items** → Read & Write (optional)
4. Click **"Create"**
5. **IMPORTANT**: Copy the token immediately - you can't view it again!

#### Step 2: Use PAT for Git Authentication
```bash
# When prompted for password during git push:
# Username: Your Azure DevOps email
# Password: Paste your PAT token

# Or store credentials (optional)
git config --global credential.helper store
```

### Using Azure CLI (Alternative)

```bash
# Install Azure CLI
# Windows: https://aka.ms/installazurecliwindows
# Or: winget install Microsoft.AzureCLI

# Login to Azure DevOps
az login
az devops configure --defaults organization=https://dev.azure.com/{org} project={project}

# Clone repository using Azure CLI authentication
az repos show --repository snowflake-SECURITY_ANALYTICS-datawarehouse
```

---

## Azure DevOps-Specific Configuration

### 1. Repository Settings

Go to **Project Settings** → **Repositories** → Select your repo:

#### Branch Policies (for main branch)
- **Require a minimum number of reviewers**: 1-2
- **Check for linked work items**: Optional
- **Check for comment resolution**: Recommended
- **Limit merge types**: Squash merge (optional)
- **Build validation**: Add if using Azure Pipelines

#### Security
- Set permissions for users/groups
- Default: Contributors can push, Readers can view

### 2. README and Documentation

Azure DevOps supports the same README.md format:
- Markdown rendering
- Mermaid diagrams (limited support)
- Tables and badges

**Note**: Some GitHub-specific badges won't work. Replace with Azure DevOps equivalents:

```markdown
<!-- GitHub badges -->
[![GitHub release](https://img.shields.io/github/v/release/...)]
[![GitHub issues](https://img.shields.io/github/issues/...)]

<!-- Azure DevOps badges (add from Pipelines if configured) -->
[![Build Status](https://dev.azure.com/{org}/{project}/_apis/build/status/{pipeline})](...)
```

### 3. Work Items and Boards

Azure DevOps has built-in project management:

1. **Boards**: Kanban-style task tracking
2. **Backlogs**: Sprint planning
3. **Work Items**: Issues, Tasks, Bugs, Features

#### Create Initial Work Items:
- **Epic**: SECURITY_ANALYTICS Data Warehouse Implementation
- **Features**:
  - 3-Layer Architecture
  - Security Service Integrations
  - Automation Framework
  - Top 13 KPIs
- **Tasks**: Break down each feature

### 4. Wiki

Azure DevOps has a built-in Wiki feature:

#### Enable Wiki:
1. Go to **Overview** → **Wiki**
2. Click **"Create project wiki"**
3. Options:
   - **Publish code as wiki**: Use `/docs` folder
   - **Create new wiki**: Separate wiki repository

#### Recommended Wiki Structure:
```
📁 Wiki
├── Home.md (Overview)
├── Architecture.md (3-layer design)
├── Deployment-Guide.md (Step-by-step)
├── Security-Services.md (Integration details)
├── KPIs.md (Top 13 metrics)
├── Troubleshooting.md (Common issues)
└── API-Documentation.md (If applicable)
```

---

## Azure Pipelines Setup (Optional)

Azure Pipelines provides CI/CD automation.

### Create Basic Pipeline for SQL Validation

Create `azure-pipelines.yml` in repository root:

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
    - main
    - develop
  paths:
    include:
    - '01_SQL_SCRIPTS/**'
    - '02_PYTHON_SCRIPTS/**'

pool:
  vmImage: 'ubuntu-latest'

variables:
  python.version: '3.13'

stages:
- stage: Validate
  displayName: 'Validate Code'
  jobs:
  - job: ValidatePython
    displayName: 'Validate Python Scripts'
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '$(python.version)'
      displayName: 'Use Python $(python.version)'

    - script: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pylint pytest
      displayName: 'Install dependencies'

    - script: |
        pylint 02_PYTHON_SCRIPTS/*.py --disable=C0114,C0115,C0116 || true
      displayName: 'Lint Python files'

    - script: |
        # Run tests if test files exist
        if [ -d "tests" ]; then
          pytest tests/ -v --junitxml=junit/test-results.xml
        fi
      displayName: 'Run Python tests'

    - task: PublishTestResults@2
      condition: succeededOrFailed()
      inputs:
        testResultsFiles: '**/test-*.xml'
        testRunTitle: 'Python Tests'

  - job: ValidateSQL
    displayName: 'Validate SQL Scripts'
    steps:
    - script: |
        echo "Checking SQL syntax..."
        # Basic SQL file validation
        find 01_SQL_SCRIPTS -name "*.sql" -type f | while read file; do
          if ! grep -q "CREATE\|ALTER\|SELECT" "$file"; then
            echo "Warning: $file may not be a valid SQL file"
          fi
        done
      displayName: 'Basic SQL validation'

- stage: Deploy
  displayName: 'Deploy to Snowflake'
  dependsOn: Validate
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - job: DeployDev
    displayName: 'Deploy to DEV'
    steps:
    - script: |
        echo "Deployment to Snowflake would happen here"
        echo "Using secure service connections and variables"
      displayName: 'Deploy SQL Scripts'
```

### Configure Pipeline:
1. Go to **Pipelines** → **New pipeline**
2. Select **Azure Repos Git**
3. Select your repository
4. Choose **Existing Azure Pipelines YAML file**
5. Select `/azure-pipelines.yml`
6. Review and run

### Add Snowflake Credentials (Secure):
1. Go to **Pipelines** → **Library**
2. Create **Variable Group**: `Snowflake-Credentials`
3. Add variables (mark as secret):
   - `SNOWFLAKE_ACCOUNT`
   - `SNOWFLAKE_USER`
   - `SNOWFLAKE_PASSWORD`
   - `SNOWFLAKE_WAREHOUSE`
   - `SNOWFLAKE_ROLE`

---

## Wiki and Documentation

### Convert README to Wiki Pages

1. **Create Wiki Home Page**:
```markdown
# SECURITY_ANALYTICS Data Warehouse

## Quick Links
- [[Architecture|Architecture]]
- [[Deployment Guide|Deployment-Guide]]
- [[Security Services|Security-Services]]
- [[Top 13 KPIs|KPIs]]

## Overview
[Content from README.md]
```

2. **Copy Documentation**:
- Extract sections from README.md into separate wiki pages
- Add internal links using `[[Page Name]]` syntax
- Upload diagrams to wiki attachments

3. **Add Code References**:
```markdown
See implementation in [DIM_HOST table](/01_SQL_SCRIPTS/02_Base_Implementation?path=ITSECKPI_MODEL_IMPLEMENTATION_CORRECTED.sql&line=125)
```

---

## Comparison: GitHub vs Azure DevOps

| Feature | GitHub | Azure DevOps | Notes |
|---------|--------|--------------|-------|
| **Git Hosting** | ✅ Excellent | ✅ Excellent | Both fully featured |
| **CI/CD** | GitHub Actions | Azure Pipelines | Azure Pipelines more enterprise-focused |
| **Project Management** | Projects (basic) | Boards (advanced) | Azure DevOps has better PM tools |
| **Wiki** | Limited (Pages) | Built-in Wiki | Azure DevOps wiki is superior |
| **Integration** | GitHub ecosystem | Microsoft/Azure | Azure DevOps better for Azure cloud |
| **Pricing** | Free for public | Free for 5 users | Similar pricing models |
| **Authentication** | SSH/HTTPS | PAT/SSH/Azure AD | Azure AD integration is powerful |
| **Artifacts** | Packages | Azure Artifacts | Both support packages |
| **Test Plans** | Not built-in | Built-in | Azure DevOps includes test management |
| **Community** | Large community | Enterprise-focused | GitHub more popular for open-source |

### When to Use Which?

**Use GitHub When**:
- Open-source or public projects
- Want larger developer community
- Prefer GitHub Actions for CI/CD
- Integration with GitHub ecosystem

**Use Azure DevOps When**:
- Enterprise/internal projects
- Already using Microsoft/Azure stack
- Need advanced project management
- Require built-in test management
- Need Azure AD integration

**Use Both** (Mirror):
- Maximum redundancy
- GitHub for external collaboration
- Azure DevOps for internal workflows

---

## Syncing Between GitHub and Azure DevOps

### Automatic Mirroring with Azure Pipelines

Create `mirror-to-github.yml`:

```yaml
# Runs on Azure DevOps, pushes to GitHub
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

steps:
- checkout: self
  persistCredentials: true

- script: |
    git remote add github https://$(GITHUB_PAT)@github.com/fos-CompanyX/snowflake-SECURITY_ANALYTICS-datawarehouse.git
    git push github main --force
  displayName: 'Mirror to GitHub'
```

### Manual Sync Script

Save as `sync-repos.ps1`:

```powershell
# Sync between GitHub and Azure DevOps

$githubRemote = "https://github.com/fos-CompanyX/snowflake-SECURITY_ANALYTICS-datawarehouse.git"
$azureRemote = "https://dev.azure.com/{org}/{project}/_git/{repo}"

# Fetch from both remotes
git fetch origin  # GitHub
git fetch azure   # Azure DevOps

# Push GitHub main to Azure DevOps
git push azure origin/main:main

# Or push Azure DevOps to GitHub
# git push origin azure/main:main

Write-Host "Repositories synced!" -ForegroundColor Green
```

---

## Post-Setup Configuration

### 1. Team Permissions
- **Project Settings** → **Permissions**
- Add team members with appropriate roles:
  - **Readers**: View-only access
  - **Contributors**: Can commit code
  - **Build Administrators**: Can manage pipelines
  - **Project Administrators**: Full control

### 2. Notifications
- **Project Settings** → **Notifications**
- Set up email notifications for:
  - Pull requests
  - Build failures
  - Work item updates

### 3. Service Connections
- **Project Settings** → **Service connections**
- Add connections for:
  - Snowflake (custom connection)
  - Azure subscriptions
  - External services

### 4. Branch Policies
Enable for `main` branch:
- Require pull requests
- Require successful builds
- Require code reviews
- Automatically include reviewers

---

## Quick Start Commands Summary

```bash
# Navigate to repository
cd "C:\\Projects\\Snowflake_ITSECKPI_Project\GITHUB_REPO"

# Add Azure DevOps remote
git remote add azure https://dev.azure.com/{org}/{project}/_git/{repo}

# Push to Azure DevOps
git push -u azure main

# View remotes
git remote -v

# Push to both remotes
git push origin main  # GitHub
git push azure main   # Azure DevOps

# Or push to all remotes at once
git remote set-url --add --push origin https://github.com/fos-CompanyX/snowflake-SECURITY_ANALYTICS-datawarehouse.git
git remote set-url --add --push origin https://dev.azure.com/{org}/{project}/_git/{repo}
git push origin main  # Pushes to both
```

---

## Troubleshooting

### Issue: Authentication Failed
```bash
# Clear credential cache
git credential reject
# Enter: protocol=https
# Enter: host=dev.azure.com
# Press Ctrl+D (or Ctrl+Z on Windows)

# Re-authenticate with PAT
git push azure main
# Enter email and PAT when prompted
```

### Issue: Cannot Push - Repository Not Empty
```bash
# Force push (careful - overwrites remote)
git push azure main --force

# Or pull and merge first
git pull azure main --allow-unrelated-histories
git push azure main
```

### Issue: Large File Warnings
```bash
# Azure DevOps has same file size limits as GitHub
# Use Git LFS for large files
git lfs install
git lfs track "*.pbix"
git lfs track "*.xlsx"
git add .gitattributes
git commit -m "chore: add Git LFS tracking"
git push azure main
```

---

## Resources

### Azure DevOps Documentation
- **Getting Started**: https://docs.microsoft.com/en-us/azure/devops/user-guide/
- **Repos**: https://docs.microsoft.com/en-us/azure/devops/repos/
- **Pipelines**: https://docs.microsoft.com/en-us/azure/devops/pipelines/
- **Boards**: https://docs.microsoft.com/en-us/azure/devops/boards/

### Support
- **Azure DevOps Community**: https://developercommunity.visualstudio.com/
- **Stack Overflow**: Tag `azure-devops`

---

## Checklist

After setup, verify:

- [ ] Repository created in Azure DevOps
- [ ] Code pushed successfully
- [ ] README.md displays correctly
- [ ] Branch policies configured
- [ ] Team permissions set
- [ ] PAT authentication working
- [ ] Wiki pages created (optional)
- [ ] Azure Pipelines configured (optional)
- [ ] Service connections added (if needed)
- [ ] Both GitHub and Azure DevOps in sync

---

**Document Version**: 1.0
**Last Updated**: October 15, 2025
**Status**: Ready for Use

Your SECURITY_ANALYTICS Data Warehouse is now available on both GitHub and Azure DevOps! 🚀
