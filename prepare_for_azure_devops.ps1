# ================================================================
# Prepare Repository for Azure DevOps Push
# ================================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Prepare for Azure DevOps Upload" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$repoPath = "C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV"

# Change to repo directory
Set-Location $repoPath

Write-Host "[Step 1/5] Checking Git status..." -ForegroundColor Yellow
Write-Host ""

git status

Write-Host ""
Write-Host "[Step 2/5] Adding all new files..." -ForegroundColor Yellow
Write-Host ""

# Add all untracked files
git add .

Write-Host ""
Write-Host "[Step 3/5] Showing staged changes..." -ForegroundColor Yellow
Write-Host ""

git status

Write-Host ""
Write-Host "[Step 4/5] Review changes before commit..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Files to be committed:" -ForegroundColor Green

git diff --cached --name-only

Write-Host ""
Write-Host "[Step 5/5] Ready to commit and push" -ForegroundColor Yellow
Write-Host ""
Write-Host "To commit and push to Azure DevOps, run:" -ForegroundColor Cyan
Write-Host ""
Write-Host '  git commit -m "feat: add automation scripts for SnowSQL and OneDrive backup"' -ForegroundColor White
Write-Host ""
Write-Host "  git push origin main" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Preparation Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
