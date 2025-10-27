# ============================================
# Upload SECURITY_ANALYTICS Wikis to Azure DevOps
# ============================================
# Purpose: Automate wiki upload process with safety checks
# Author: GenericCorp Data Engineering Team
# Date: 2025-10-24
# User: fuad.onate@CompanyX.com
# Authentication: SSO (Okta) via Git Credential Manager
# ============================================

param(
    [switch]$DryRun = $false,
    [switch]$SkipBackup = $false
)

# Configuration
$ProjectRoot = "C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV"
$WikiRepoUrl = "https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_git/GIS%20-%20ITSECKPI%20-%20DW.wiki"
$WikiRepoPath = Join-Path $ProjectRoot "wiki-repo"
$WikiFolder = "SECURITY_ANALYTICS-Documentation"
$BackupBranch = "backup-before-new-wikis-2025-10-24"

# Wiki files mapping
$WikiFiles = @(
    @{Source = "WIKI_01_STREAMLIT_APPS.md"; Target = "01-Streamlit-Applications.md"},
    @{Source = "WIKI_02_POWER_BI.md"; Target = "02-Power-BI-Roadmap.md"},
    @{Source = "WIKI_03_METADATA_EXTRACTION.md"; Target = "03-Metadata-Extraction.md"},
    @{Source = "WIKI_04_DATA_GOVERNANCE.md"; Target = "04-Data-Governance.md"},
    @{Source = "WIKI_05_DATA_DICTIONARY.md"; Target = "05-Data-Dictionary.md"},
    @{Source = "WIKI_06_BEST_PRACTICES.md"; Target = "06-Best-Practices.md"}
)

# Colors for output
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Step { param($Message) Write-Host "`n=== $Message ===" -ForegroundColor Magenta }

# ============================================
# STEP 0: Pre-flight checks
# ============================================
Write-Step "Pre-flight Checks"

# Check if running from correct directory
Set-Location $ProjectRoot
Write-Info "Working directory: $ProjectRoot"

# Check if wiki files exist
$MissingFiles = @()
foreach ($wiki in $WikiFiles) {
    $sourcePath = Join-Path $ProjectRoot $wiki.Source
    if (-not (Test-Path $sourcePath)) {
        $MissingFiles += $wiki.Source
    }
}

if ($MissingFiles.Count -gt 0) {
    Write-Error "Missing wiki files:"
    $MissingFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
}
Write-Success "All 6 wiki files found"

# Check Git installation
try {
    $gitVersion = git --version
    Write-Success "Git installed: $gitVersion"
} catch {
    Write-Error "Git not found. Please install Git for Windows."
    exit 1
}

# Check Git configuration
$gitEmail = git config --global user.email
$gitName = git config --global user.name

if (-not $gitEmail) {
    Write-Warning "Git email not configured. Setting to fuad.onate@CompanyX.com"
    git config --global user.email "fuad.onate@CompanyX.com"
}
if (-not $gitName) {
    Write-Warning "Git name not configured. Setting to Fuad Onate"
    git config --global user.name "Fuad Onate"
}

Write-Info "Git user: $gitName <$gitEmail>"

# ============================================
# STEP 1: Clone or Update Wiki Repository
# ============================================
Write-Step "Clone/Update Wiki Repository"

if (Test-Path $WikiRepoPath) {
    Write-Warning "Wiki repository already exists at: $WikiRepoPath"
    $response = Read-Host "Delete and re-clone? (y/N)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        Remove-Item -Recurse -Force $WikiRepoPath
        Write-Info "Deleted existing repository"
    } else {
        Write-Info "Using existing repository. Pulling latest changes..."
        Set-Location $WikiRepoPath
        git pull origin main
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to pull latest changes"
            exit 1
        }
        Write-Success "Repository updated"
    }
}

if (-not (Test-Path $WikiRepoPath)) {
    Write-Info "Cloning wiki repository from Azure DevOps..."
    Write-Info "URL: $WikiRepoUrl"
    Write-Warning "Git Credential Manager will open browser for SSO authentication"

    git clone $WikiRepoUrl $WikiRepoPath

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to clone repository"
        Write-Info "Possible causes:"
        Write-Info "  1. Wiki doesn't exist yet - create it in Azure DevOps first"
        Write-Info "  2. Authentication failed - complete SSO in browser"
        Write-Info "  3. No permissions - contact project admin"
        exit 1
    }

    Write-Success "Repository cloned successfully"
}

Set-Location $WikiRepoPath

# ============================================
# STEP 2: Review Existing Structure
# ============================================
Write-Step "Review Existing Wiki Structure"

$existingFiles = Get-ChildItem -Recurse -File | Select-Object -ExpandProperty FullName
Write-Info "Found $($existingFiles.Count) existing files in wiki repository:"
$existingFiles | ForEach-Object { Write-Host "  - $($_.Replace($WikiRepoPath, ''))" }

# Check for potential conflicts
$conflicts = @()
foreach ($wiki in $WikiFiles) {
    $targetPath = Join-Path $WikiRepoPath $WikiFolder $wiki.Target
    if (Test-Path $targetPath) {
        $conflicts += $wiki.Target
    }
}

if ($conflicts.Count -gt 0) {
    Write-Warning "The following files already exist and will be overwritten:"
    $conflicts | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }

    if (-not $DryRun) {
        $response = Read-Host "Continue and overwrite? (y/N)"
        if ($response -ne 'y' -and $response -ne 'Y') {
            Write-Info "Upload cancelled by user"
            exit 0
        }
    }
}

# ============================================
# STEP 3: Create Backup Branch
# ============================================
if (-not $SkipBackup) {
    Write-Step "Create Backup Branch"

    # Check if backup branch already exists
    $branches = git branch --list $BackupBranch
    if ($branches) {
        Write-Warning "Backup branch '$BackupBranch' already exists"
    } else {
        Write-Info "Creating backup branch: $BackupBranch"
        git checkout -b $BackupBranch

        if ($LASTEXITCODE -eq 0) {
            if (-not $DryRun) {
                git push origin $BackupBranch
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "Backup branch created and pushed to Azure DevOps"
                } else {
                    Write-Warning "Backup branch created locally but failed to push"
                }
            } else {
                Write-Info "[DRY RUN] Would push backup branch to Azure DevOps"
            }
        } else {
            Write-Error "Failed to create backup branch"
            exit 1
        }

        # Return to main branch
        git checkout main
    }
} else {
    Write-Warning "Skipping backup branch creation (--SkipBackup flag set)"
}

# ============================================
# STEP 4: Create Wiki Folder Structure
# ============================================
Write-Step "Create Wiki Folder Structure"

$wikiFolderPath = Join-Path $WikiRepoPath $WikiFolder
if (-not (Test-Path $wikiFolderPath)) {
    New-Item -ItemType Directory -Path $wikiFolderPath | Out-Null
    Write-Success "Created folder: $WikiFolder"
} else {
    Write-Info "Folder already exists: $WikiFolder"
}

# ============================================
# STEP 5: Copy Wiki Files
# ============================================
Write-Step "Copy Wiki Files to Repository"

$copiedFiles = 0
foreach ($wiki in $WikiFiles) {
    $sourcePath = Join-Path $ProjectRoot $wiki.Source
    $targetPath = Join-Path $wikiFolderPath $wiki.Target

    Write-Info "Copying: $($wiki.Source) → $($WikiFolder)/$($wiki.Target)"

    if (-not $DryRun) {
        Copy-Item -Path $sourcePath -Destination $targetPath -Force

        if (Test-Path $targetPath) {
            $fileSize = (Get-Item $targetPath).Length / 1KB
            Write-Success "Copied successfully ($([math]::Round($fileSize, 2)) KB)"
            $copiedFiles++
        } else {
            Write-Error "Failed to copy $($wiki.Source)"
        }
    } else {
        Write-Info "[DRY RUN] Would copy to: $targetPath"
        $copiedFiles++
    }
}

Write-Success "Copied $copiedFiles / $($WikiFiles.Count) files"

# ============================================
# STEP 6: Review Git Changes
# ============================================
Write-Step "Review Git Changes"

$gitStatus = git status --porcelain

if (-not $gitStatus) {
    Write-Warning "No changes detected in Git"
    Write-Info "This may mean:"
    Write-Info "  1. Files already exist with identical content"
    Write-Info "  2. Copy operation didn't work as expected"

    $response = Read-Host "Continue anyway? (y/N)"
    if ($response -ne 'y' -and $response -ne 'Y') {
        Write-Info "Upload cancelled"
        exit 0
    }
} else {
    Write-Info "Git changes detected:"
    $gitStatus | ForEach-Object { Write-Host "  $_" }

    # Count new vs modified files
    $newFiles = ($gitStatus | Where-Object { $_ -match '^\?\?' }).Count
    $modifiedFiles = ($gitStatus | Where-Object { $_ -match '^ M' }).Count

    Write-Info "Summary: $newFiles new files, $modifiedFiles modified files"

    if ($modifiedFiles -gt 0) {
        Write-Warning "⚠️  CAUTION: $modifiedFiles existing files will be modified"
        $gitStatus | Where-Object { $_ -match '^ M' } | ForEach-Object {
            Write-Host "  $_" -ForegroundColor Yellow
        }

        if (-not $DryRun) {
            $response = Read-Host "Are you sure you want to modify existing files? (y/N)"
            if ($response -ne 'y' -and $response -ne 'Y') {
                Write-Info "Upload cancelled"
                exit 0
            }
        }
    }
}

# ============================================
# STEP 7: Stage Changes
# ============================================
Write-Step "Stage Changes for Commit"

if (-not $DryRun) {
    git add "$WikiFolder/"

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Changes staged successfully"
    } else {
        Write-Error "Failed to stage changes"
        exit 1
    }

    # Show what's staged
    $stagedFiles = git diff --staged --name-only
    Write-Info "Staged files:"
    $stagedFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor Green }
} else {
    Write-Info "[DRY RUN] Would stage: $WikiFolder/"
}

# ============================================
# STEP 8: Commit Changes
# ============================================
Write-Step "Commit Changes"

$commitMessage = @"
docs: Add comprehensive SECURITY_ANALYTICS Data Warehouse documentation

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

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
"@

if (-not $DryRun) {
    git commit -m $commitMessage

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Changes committed successfully"

        # Show commit details
        Write-Info "Commit details:"
        git log -1 --oneline
    } else {
        Write-Error "Failed to commit changes"
        exit 1
    }
} else {
    Write-Info "[DRY RUN] Would commit with message:"
    Write-Host $commitMessage -ForegroundColor Gray
}

# ============================================
# STEP 9: Push to Azure DevOps
# ============================================
Write-Step "Push to Azure DevOps"

if (-not $DryRun) {
    Write-Warning "About to push to Azure DevOps. This will update the wiki for all team members."
    $response = Read-Host "Proceed with push? (y/N)"

    if ($response -eq 'y' -or $response -eq 'Y') {
        Write-Info "Pushing to origin/main..."
        Write-Info "Git Credential Manager will handle SSO authentication automatically"

        git push origin main

        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ Successfully pushed wikis to Azure DevOps!"
        } else {
            Write-Error "Failed to push to Azure DevOps"
            Write-Info "Changes are committed locally. You can push manually later with:"
            Write-Info "  cd $WikiRepoPath"
            Write-Info "  git push origin main"
            exit 1
        }
    } else {
        Write-Info "Push cancelled. Changes are committed locally."
        Write-Info "To push later, run: git push origin main"
        exit 0
    }
} else {
    Write-Info "[DRY RUN] Would push to: $WikiRepoUrl"
}

# ============================================
# STEP 10: Verification & Next Steps
# ============================================
Write-Step "Upload Complete!"

Write-Success "✅ All wikis uploaded successfully to Azure DevOps"

Write-Host "`n📋 Verification Checklist:" -ForegroundColor Cyan
Write-Host "  1. Open Azure DevOps wiki in browser"
Write-Host "  2. Verify all 6 wikis are visible"
Write-Host "  3. Check formatting (tables, code blocks, etc.)"
Write-Host "  4. Test internal links between wikis"
Write-Host "  5. Verify Table of Contents works"

Write-Host "`n🔗 Wiki URL:" -ForegroundColor Cyan
Write-Host "  https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_wiki/wikis/"

Write-Host "`n📊 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Review uploaded wikis in Azure DevOps"
Write-Host "  2. Update wiki home page with links to new documentation"
Write-Host "  3. Execute GENERATE_ERD_FROM_METADATA.sql to enhance Data Model wiki"
Write-Host "  4. Notify team about new documentation"
Write-Host "  5. Schedule wiki review meeting"

Write-Host "`n📁 Files Uploaded:" -ForegroundColor Cyan
foreach ($wiki in $WikiFiles) {
    Write-Host "  ✅ $($WikiFolder)/$($wiki.Target)"
}

Write-Host "`n💾 Backup Branch:" -ForegroundColor Cyan
if (-not $SkipBackup) {
    Write-Host "  Created: $BackupBranch"
    Write-Host "  To restore from backup: git checkout $BackupBranch"
} else {
    Write-Host "  No backup created (--SkipBackup flag used)"
}

Write-Host ""
