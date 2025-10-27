# Upload SECURITY_ANALYTICS Wikis to Azure DevOps - Simple Version
# User: fuad.onate@CompanyX.com
# Authentication: SSO (Okta) via Git Credential Manager

param(
    [switch]$DryRun = $false
)

# Configuration
$ProjectRoot = "C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV"
$WikiRepoUrl = "https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_git/GIS%20-%20ITSECKPI%20-%20DW.wiki"
$WikiRepoPath = Join-Path $ProjectRoot "wiki-repo"
$WikiFolder = "SECURITY_ANALYTICS-Documentation"

# Wiki files mapping
$WikiFiles = @(
    @{Source = "WIKI_01_STREAMLIT_APPS.md"; Target = "01-Streamlit-Applications.md"},
    @{Source = "WIKI_02_POWER_BI.md"; Target = "02-Power-BI-Roadmap.md"},
    @{Source = "WIKI_03_METADATA_EXTRACTION.md"; Target = "03-Metadata-Extraction.md"},
    @{Source = "WIKI_04_DATA_GOVERNANCE.md"; Target = "04-Data-Governance.md"},
    @{Source = "WIKI_05_DATA_DICTIONARY.md"; Target = "05-Data-Dictionary.md"},
    @{Source = "WIKI_06_BEST_PRACTICES.md"; Target = "06-Best-Practices.md"}
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "Upload SECURITY_ANALYTICS Wikis to Azure DevOps" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

if ($DryRun) {
    Write-Host "[DRY RUN MODE - No changes will be made]" -ForegroundColor Yellow
    Write-Host ""
}

# Check if running from correct directory
Set-Location $ProjectRoot
Write-Host "Working directory: $ProjectRoot" -ForegroundColor Cyan

# Check if wiki files exist
Write-Host ""
Write-Host "Checking wiki files..." -ForegroundColor Cyan
$AllFilesExist = $true
foreach ($wiki in $WikiFiles) {
    $sourcePath = Join-Path $ProjectRoot $wiki.Source
    if (Test-Path $sourcePath) {
        Write-Host "  [OK] $($wiki.Source)" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $($wiki.Source)" -ForegroundColor Red
        $AllFilesExist = $false
    }
}

if (-not $AllFilesExist) {
    Write-Host ""
    Write-Host "ERROR: Some wiki files are missing. Cannot continue." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "All 6 wiki files found successfully!" -ForegroundColor Green

# Check Git configuration
Write-Host ""
Write-Host "Checking Git configuration..." -ForegroundColor Cyan

try {
    $gitVersion = git --version
    Write-Host "  Git version: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Git not found. Please install Git for Windows." -ForegroundColor Red
    exit 1
}

$gitEmail = git config --global user.email
$gitName = git config --global user.name

if (-not $gitEmail) {
    Write-Host "  Setting Git email to: fuad.onate@CompanyX.com" -ForegroundColor Yellow
    git config --global user.email "fuad.onate@CompanyX.com"
    $gitEmail = "fuad.onate@CompanyX.com"
}

if (-not $gitName) {
    Write-Host "  Setting Git name to: Fuad Onate" -ForegroundColor Yellow
    git config --global user.name "Fuad Onate"
    $gitName = "Fuad Onate"
}

Write-Host "  Git user: $gitName" -ForegroundColor Green
Write-Host "  Git email: $gitEmail" -ForegroundColor Green

# Clone or update repository
Write-Host ""
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "Cloning Wiki Repository" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

if (Test-Path $WikiRepoPath) {
    Write-Host "Wiki repository already exists at: $WikiRepoPath" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Cyan
    Write-Host "  1. Delete and re-clone (recommended for clean start)"
    Write-Host "  2. Use existing and pull latest changes"
    Write-Host ""
    $choice = Read-Host "Enter choice (1 or 2)"

    if ($choice -eq "1") {
        Write-Host "Deleting existing repository..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force $WikiRepoPath
        Write-Host "Deleted successfully" -ForegroundColor Green
    } elseif ($choice -eq "2") {
        Write-Host "Using existing repository. Pulling latest changes..." -ForegroundColor Cyan
        Set-Location $WikiRepoPath
        git pull origin main
        if ($LASTEXITCODE -ne 0) {
            Write-Host "WARNING: Failed to pull latest changes" -ForegroundColor Yellow
        } else {
            Write-Host "Repository updated successfully" -ForegroundColor Green
        }
    } else {
        Write-Host "Invalid choice. Exiting." -ForegroundColor Red
        exit 1
    }
}

if (-not (Test-Path $WikiRepoPath)) {
    Write-Host "Cloning wiki repository..." -ForegroundColor Cyan
    Write-Host "URL: $WikiRepoUrl" -ForegroundColor Gray
    Write-Host ""
    Write-Host "NOTE: Git Credential Manager will open browser for SSO authentication" -ForegroundColor Yellow
    Write-Host "      Please complete login with fuad.onate@CompanyX.com" -ForegroundColor Yellow
    Write-Host ""

    git clone $WikiRepoUrl $WikiRepoPath

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: Failed to clone repository" -ForegroundColor Red
        Write-Host ""
        Write-Host "Possible causes:" -ForegroundColor Yellow
        Write-Host "  1. Wiki does not exist yet - create it in Azure DevOps first" -ForegroundColor Yellow
        Write-Host "  2. Authentication failed - complete SSO in browser" -ForegroundColor Yellow
        Write-Host "  3. No permissions - contact project admin" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "To create wiki: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_wiki/wikis/" -ForegroundColor Cyan
        exit 1
    }

    Write-Host ""
    Write-Host "Repository cloned successfully!" -ForegroundColor Green
}

Set-Location $WikiRepoPath

# Review existing structure
Write-Host ""
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "Review Existing Wiki Structure" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

$existingFiles = Get-ChildItem -Recurse -File | Select-Object -ExpandProperty Name
Write-Host "Found $($existingFiles.Count) existing files in wiki repository" -ForegroundColor Cyan

if ($existingFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "Existing files:" -ForegroundColor Gray
    $existingFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
}

# Create backup branch
Write-Host ""
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "Create Backup Branch" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

$BackupBranch = "backup-before-new-wikis-2025-10-24"
$branches = git branch --list $BackupBranch

if ($branches) {
    Write-Host "Backup branch '$BackupBranch' already exists" -ForegroundColor Yellow
} else {
    Write-Host "Creating backup branch: $BackupBranch" -ForegroundColor Cyan

    if (-not $DryRun) {
        git checkout -b $BackupBranch
        if ($LASTEXITCODE -eq 0) {
            git push origin $BackupBranch
            if ($LASTEXITCODE -eq 0) {
                Write-Host "Backup branch created and pushed successfully!" -ForegroundColor Green
            } else {
                Write-Host "WARNING: Backup branch created locally but failed to push" -ForegroundColor Yellow
            }
        }
        git checkout main
    } else {
        Write-Host "[DRY RUN] Would create backup branch" -ForegroundColor Gray
    }
}

# Create wiki folder
Write-Host ""
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "Create Wiki Folder" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

$wikiFolderPath = Join-Path $WikiRepoPath $WikiFolder

if (-not (Test-Path $wikiFolderPath)) {
    if (-not $DryRun) {
        New-Item -ItemType Directory -Path $wikiFolderPath | Out-Null
        Write-Host "Created folder: $WikiFolder" -ForegroundColor Green
    } else {
        Write-Host "[DRY RUN] Would create folder: $WikiFolder" -ForegroundColor Gray
    }
} else {
    Write-Host "Folder already exists: $WikiFolder" -ForegroundColor Yellow
}

# Copy wiki files
Write-Host ""
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "Copy Wiki Files" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

$copiedCount = 0
foreach ($wiki in $WikiFiles) {
    $sourcePath = Join-Path $ProjectRoot $wiki.Source
    $targetPath = Join-Path $wikiFolderPath $wiki.Target

    Write-Host "Copying: $($wiki.Source) -> $($wiki.Target)" -ForegroundColor Cyan

    if (-not $DryRun) {
        Copy-Item -Path $sourcePath -Destination $targetPath -Force
        if (Test-Path $targetPath) {
            $fileSize = [math]::Round((Get-Item $targetPath).Length / 1KB, 2)
            Write-Host "  Copied successfully ($fileSize KB)" -ForegroundColor Green
            $copiedCount++
        } else {
            Write-Host "  ERROR: Failed to copy" -ForegroundColor Red
        }
    } else {
        Write-Host "  [DRY RUN] Would copy to: $targetPath" -ForegroundColor Gray
        $copiedCount++
    }
}

Write-Host ""
Write-Host "Copied $copiedCount / $($WikiFiles.Count) files" -ForegroundColor Green

# Review Git changes
Write-Host ""
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "Review Git Changes" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

if (-not $DryRun) {
    $gitStatus = git status --porcelain

    if (-not $gitStatus) {
        Write-Host "WARNING: No changes detected in Git" -ForegroundColor Yellow
        Write-Host "Files may already exist with identical content" -ForegroundColor Yellow
    } else {
        Write-Host "Git changes detected:" -ForegroundColor Cyan
        $gitStatus | ForEach-Object { Write-Host "  $_" }

        $newFiles = ($gitStatus | Where-Object { $_ -match '^\?\?' }).Count
        $modifiedFiles = ($gitStatus | Where-Object { $_ -match '^ M' }).Count

        Write-Host ""
        Write-Host "Summary: $newFiles new files, $modifiedFiles modified files" -ForegroundColor Cyan

        if ($modifiedFiles -gt 0) {
            Write-Host ""
            Write-Host "WARNING: $modifiedFiles existing files will be modified:" -ForegroundColor Yellow
            $gitStatus | Where-Object { $_ -match '^ M' } | ForEach-Object {
                Write-Host "  $_" -ForegroundColor Yellow
            }
        }
    }

    # Stage changes
    Write-Host ""
    Write-Host "Staging changes..." -ForegroundColor Cyan
    git add "$WikiFolder/"

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Changes staged successfully" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Failed to stage changes" -ForegroundColor Red
        exit 1
    }

    # Commit
    Write-Host ""
    Write-Host "Committing changes..." -ForegroundColor Cyan

    $commitMessage = "docs: Add comprehensive SECURITY_ANALYTICS Data Warehouse documentation`n`nAdd 6 new wiki pages with complete project documentation.`n`nGenerated with Claude Code"

    git commit -m $commitMessage

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Changes committed successfully!" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Failed to commit changes" -ForegroundColor Red
        exit 1
    }

    # Push
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host "Push to Azure DevOps" -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "About to push wikis to Azure DevOps." -ForegroundColor Yellow
    Write-Host "This will update the wiki for all team members." -ForegroundColor Yellow
    Write-Host ""
    $confirm = Read-Host "Proceed with push? (y/N)"

    if ($confirm -eq 'y' -or $confirm -eq 'Y') {
        Write-Host ""
        Write-Host "Pushing to Azure DevOps..." -ForegroundColor Cyan
        git push origin main

        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "SUCCESS! Wikis uploaded to Azure DevOps" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "Wiki URL: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_wiki/wikis/" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Next steps:" -ForegroundColor Cyan
            Write-Host "  1. Verify wikis in Azure DevOps web interface" -ForegroundColor White
            Write-Host "  2. Check formatting and links" -ForegroundColor White
            Write-Host "  3. Update wiki home page with links" -ForegroundColor White
            Write-Host "  4. Execute GENERATE_ERD_FROM_METADATA.sql for Data Model wiki" -ForegroundColor White
            Write-Host ""
        } else {
            Write-Host ""
            Write-Host "ERROR: Failed to push to Azure DevOps" -ForegroundColor Red
            Write-Host "Changes are committed locally. You can push manually later." -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host ""
        Write-Host "Push cancelled by user" -ForegroundColor Yellow
        Write-Host "Changes are committed locally but not pushed" -ForegroundColor Yellow
        Write-Host "To push later: cd $WikiRepoPath; git push origin main" -ForegroundColor Cyan
    }
} else {
    Write-Host "[DRY RUN] Would stage, commit, and push changes" -ForegroundColor Gray
    Write-Host ""
    Write-Host "DRY RUN COMPLETE - No actual changes were made" -ForegroundColor Green
}

Write-Host ""
