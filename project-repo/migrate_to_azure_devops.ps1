# =============================================
# Azure DevOps Migration Script
# SECURITY_ANALYTICS Data Warehouse - GitHub to Azure DevOps
# =============================================

param(
    [string]$AzureDevOpsOrg = "CompanyX",
    [string]$AzureDevOpsProject = "GIS-SECURITY_ANALYTICS-DW",
    [string]$AzureDevOpsRepo = "GIS-SECURITY_ANALYTICS-DW",
    [switch]$DryRun,
    [switch]$Force
)

# Script configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

# Colors for output
function Write-Success { param($Message) Write-Host "✓ $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "ℹ $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠ $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "✗ $Message" -ForegroundColor Red }
function Write-Header { param($Message) Write-Host "`n========================================" -ForegroundColor Magenta; Write-Host "$Message" -ForegroundColor Magenta; Write-Host "========================================`n" -ForegroundColor Magenta }

Write-Header "SECURITY_ANALYTICS Data Warehouse - Azure DevOps Migration"

# Get current location
$scriptPath = $PSScriptRoot
if (-not $scriptPath) {
    $scriptPath = Get-Location
}

Write-Info "Script location: $scriptPath"
Write-Info "Azure DevOps Org: $AzureDevOpsOrg"
Write-Info "Azure DevOps Project: $AzureDevOpsProject"
Write-Info "Repository: $AzureDevOpsRepo"

if ($DryRun) {
    Write-Warning "DRY RUN MODE - No changes will be made"
}

# =============================================
# Step 1: Pre-flight Checks
# =============================================

Write-Header "Step 1: Pre-flight Checks"

# Check if Git is installed
Write-Info "Checking Git installation..."
try {
    $gitVersion = git --version
    Write-Success "Git installed: $gitVersion"
} catch {
    Write-Error "Git is not installed. Please install Git first."
    exit 1
}

# Check if we're in a Git repository
Write-Info "Checking if directory is a Git repository..."
if (-not (Test-Path ".git")) {
    Write-Error "Current directory is not a Git repository"
    exit 1
}
Write-Success "Git repository detected"

# Check Git status
Write-Info "Checking Git status..."
$gitStatus = git status --porcelain
if ($gitStatus -and -not $Force) {
    Write-Warning "Repository has uncommitted changes:"
    git status --short
    Write-Warning "Please commit or stash changes before migration"
    Write-Info "Use -Force to override this check"
    exit 1
}
Write-Success "Working directory is clean"

# Check current branch
$currentBranch = git branch --show-current
Write-Info "Current branch: $currentBranch"

# =============================================
# Step 2: Backup Current State
# =============================================

Write-Header "Step 2: Backup Current State"

$backupDir = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Write-Info "Creating backup in: $backupDir"

if (-not $DryRun) {
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

    # Backup .git directory
    Write-Info "Backing up .git directory..."
    Copy-Item -Path ".git" -Destination "$backupDir\.git" -Recurse -Force

    # Create backup info file
    @"
Backup Information
==================
Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Branch: $currentBranch
Commit: $(git rev-parse HEAD)
Status: $(if ($gitStatus) { "Uncommitted changes" } else { "Clean" })

Git Remotes:
$(git remote -v)
"@ | Out-File "$backupDir\backup_info.txt"

    Write-Success "Backup created successfully"
} else {
    Write-Info "[DRY RUN] Would create backup in: $backupDir"
}

# =============================================
# Step 3: Add Azure DevOps Remote
# =============================================

Write-Header "Step 3: Configure Azure DevOps Remote"

$azureDevOpsUrl = "https://dev.azure.com/$AzureDevOpsOrg/$AzureDevOpsProject/_git/$AzureDevOpsRepo"
Write-Info "Azure DevOps URL: $azureDevOpsUrl"

# Check if 'azure' remote already exists
$existingRemotes = git remote
if ($existingRemotes -contains "azure") {
    Write-Warning "Remote 'azure' already exists"
    $currentAzureUrl = git remote get-url azure
    Write-Info "Current Azure URL: $currentAzureUrl"

    if ($currentAzureUrl -ne $azureDevOpsUrl) {
        Write-Warning "Azure remote URL is different. Updating..."
        if (-not $DryRun) {
            git remote set-url azure $azureDevOpsUrl
            Write-Success "Azure remote URL updated"
        } else {
            Write-Info "[DRY RUN] Would update Azure remote URL"
        }
    } else {
        Write-Success "Azure remote is already configured correctly"
    }
} else {
    Write-Info "Adding 'azure' remote..."
    if (-not $DryRun) {
        git remote add azure $azureDevOpsUrl
        Write-Success "Azure remote added successfully"
    } else {
        Write-Info "[DRY RUN] Would add remote: azure -> $azureDevOpsUrl"
    }
}

# Display all remotes
Write-Info "Current Git remotes:"
git remote -v

# =============================================
# Step 4: Prepare for Push
# =============================================

Write-Header "Step 4: Prepare for Push"

# Check if there are any commits to push
$commitCount = git rev-list --count $currentBranch 2>$null
if ($commitCount -eq $null -or $commitCount -eq 0) {
    Write-Warning "No commits found on current branch"
} else {
    Write-Info "Total commits on $currentBranch : $commitCount"
}

# List all branches
Write-Info "Local branches:"
git branch -a

# =============================================
# Step 5: Push to Azure DevOps
# =============================================

Write-Header "Step 5: Push to Azure DevOps"

if (-not $DryRun) {
    Write-Info "Pushing to Azure DevOps..."
    Write-Warning "You may be prompted for Azure DevOps credentials"
    Write-Info "Use your Personal Access Token (PAT) as the password"

    try {
        # Push main branch
        Write-Info "Pushing main branch..."
        git push -u azure main --verbose
        Write-Success "Main branch pushed successfully"

        # Push other branches if they exist
        $otherBranches = git branch | Where-Object { $_ -notmatch '\*' -and $_ -notmatch 'main' }
        if ($otherBranches) {
            Write-Info "Found additional branches to push:"
            $otherBranches | ForEach-Object {
                $branch = $_.Trim()
                Write-Info "  - $branch"
            }

            $pushOthers = Read-Host "Push other branches? (y/n)"
            if ($pushOthers -eq 'y') {
                $otherBranches | ForEach-Object {
                    $branch = $_.Trim()
                    Write-Info "Pushing $branch..."
                    git push azure $branch
                }
                Write-Success "All branches pushed"
            }
        }

        # Push tags
        $tags = git tag
        if ($tags) {
            Write-Info "Found tags to push"
            $pushTags = Read-Host "Push tags? (y/n)"
            if ($pushTags -eq 'y') {
                git push azure --tags
                Write-Success "Tags pushed"
            }
        }

    } catch {
        Write-Error "Failed to push to Azure DevOps: $_"
        Write-Warning "Common issues:"
        Write-Warning "  1. Invalid Personal Access Token (PAT)"
        Write-Warning "  2. Insufficient permissions"
        Write-Warning "  3. Repository not empty (use --force if intentional)"
        Write-Info "Check your Azure DevOps credentials and try again"
        exit 1
    }
} else {
    Write-Info "[DRY RUN] Would push to: $azureDevOpsUrl"
    Write-Info "[DRY RUN] Branches to push: main"
}

# =============================================
# Step 6: Verify Migration
# =============================================

Write-Header "Step 6: Verify Migration"

if (-not $DryRun) {
    Write-Info "Fetching from Azure DevOps to verify..."
    git fetch azure

    # Compare local and remote
    $localCommit = git rev-parse main
    $remoteCommit = git rev-parse azure/main 2>$null

    if ($localCommit -eq $remoteCommit) {
        Write-Success "Migration verified successfully!"
        Write-Info "Local and remote commits match: $localCommit"
    } else {
        Write-Warning "Local and remote commits differ"
        Write-Info "Local: $localCommit"
        Write-Info "Remote: $remoteCommit"
    }
} else {
    Write-Info "[DRY RUN] Would verify migration"
}

# =============================================
# Step 7: Next Steps
# =============================================

Write-Header "Migration Complete!"

Write-Success "Repository successfully migrated to Azure DevOps"
Write-Info "Azure DevOps URL: https://dev.azure.com/$AzureDevOpsOrg/$AzureDevOpsProject/_git/$AzureDevOpsRepo"

Write-Host "`n" -NoNewline
Write-Header "Next Steps"

Write-Host "1. " -NoNewline -ForegroundColor Yellow
Write-Host "Visit Azure DevOps repository and verify files"
Write-Host "   https://dev.azure.com/$AzureDevOpsOrg/$AzureDevOpsProject/_git/$AzureDevOpsRepo`n"

Write-Host "2. " -NoNewline -ForegroundColor Yellow
Write-Host "Replace README.md with Azure DevOps version:"
Write-Host "   Copy-Item AZURE_DEVOPS_README.md README.md -Force`n"

Write-Host "3. " -NoNewline -ForegroundColor Yellow
Write-Host "Set up Wiki in Azure DevOps"
Write-Host "   - Navigate to Wiki in Azure DevOps"
Write-Host "   - Publish code as wiki"
Write-Host "   - Select .azuredevops/wiki folder`n"

Write-Host "4. " -NoNewline -ForegroundColor Yellow
Write-Host "Configure CI/CD Pipelines"
Write-Host "   - Pipelines > New Pipeline"
Write-Host "   - Select: .azuredevops/pipelines/ci-validation.yml`n"

Write-Host "5. " -NoNewline -ForegroundColor Yellow
Write-Host "Set up Branch Policies"
Write-Host "   - Project Settings > Repositories"
Write-Host "   - Branch Policies for main branch`n"

Write-Host "6. " -NoNewline -ForegroundColor Yellow
Write-Host "Create Work Items"
Write-Host "   - Boards > Work Items"
Write-Host "   - Import from template (if available)`n"

Write-Host "7. " -NoNewline -ForegroundColor Yellow
Write-Host "Configure Variable Groups"
Write-Host "   - Pipelines > Library"
Write-Host "   - Create: Snowflake-DEV-Credentials"
Write-Host "   - Create: Snowflake-PRD-Credentials`n"

Write-Host "`n"
Write-Header "Backup Information"
Write-Info "Backup location: $backupDir"
Write-Info "Backup includes .git directory and state information"
Write-Warning "Keep this backup until migration is fully verified"

Write-Host "`n"
Write-Host "Migration script completed successfully!" -ForegroundColor Green
Write-Host "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
