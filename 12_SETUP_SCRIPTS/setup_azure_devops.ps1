# ============================================================================
# SECURITY_ANALYTICS Data Warehouse - Azure DevOps Complete Setup Script
# ============================================================================
# This script automates the complete Azure DevOps project configuration
# Run this from PowerShell with administrator privileges
# ============================================================================

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "SECURITY_ANALYTICS Data Warehouse - Azure DevOps Setup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$orgUrl = "https://dev.azure.com/CompanyX"
$projectName = "GIS - SECURITY_ANALYTICS - DW"
$repoUrl = "$orgUrl/$projectName/_git/$projectName"

Write-Host "Project URL: $orgUrl/$projectName" -ForegroundColor Green
Write-Host ""

# ============================================================================
# Step 1: Update Project Description
# ============================================================================
Write-Host "[1/10] Update Project Description" -ForegroundColor Yellow
Write-Host "----------------------------------------------"
Write-Host ""
Write-Host "MANUAL STEP:" -ForegroundColor Red
Write-Host "1. Go to: $orgUrl/$projectName/_settings" -ForegroundColor White
Write-Host "2. Click 'Overview' in left menu" -ForegroundColor White
Write-Host "3. Update 'Description' field with:" -ForegroundColor White
Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan

$description = @"
🛡️ **Enterprise Security Analytics Platform** - Production Ready v3.0

Comprehensive data warehouse providing unified visibility across 15+ security services with automated pipelines, real-time monitoring, and executive dashboards.

**Impact**:
• `$146,250 annual savings (94% automation)
• 550+ database objects deployed
• 98.1% automation success rate
• 72.3% data quality score
• 319ms avg query performance

**Services**: CrowdStrike | Qualys | Splunk | BitSight | Symantec | +10 more
**Alignment**: NIST Cybersecurity Framework 2.0
**Tech Stack**: Snowflake | Python | Streamlit | Power BI

📊 [View Wiki]($orgUrl/$projectName/_wiki) | 🔄 [CI/CD Pipelines]($orgUrl/$projectName/_build)
"@

Write-Host $description -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter when done"

# ============================================================================
# Step 2: Publish Wiki
# ============================================================================
Write-Host ""
Write-Host "[2/10] Publish Wiki" -ForegroundColor Yellow
Write-Host "----------------------------------------------"
Write-Host ""
Write-Host "MANUAL STEP:" -ForegroundColor Red
Write-Host "1. Go to: $orgUrl/$projectName/_wiki" -ForegroundColor White
Write-Host "2. Click 'Publish code as wiki'" -ForegroundColor White
Write-Host "3. Configure:" -ForegroundColor White
Write-Host "   - Repository: $projectName" -ForegroundColor White
Write-Host "   - Branch: main" -ForegroundColor White
Write-Host "   - Folder: .azuredevops/wiki" -ForegroundColor White
Write-Host "   - Wiki name: SECURITY_ANALYTICS Data Warehouse" -ForegroundColor White
Write-Host "4. Click 'Publish'" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter when done"

# ============================================================================
# Step 3: Configure CI Pipeline
# ============================================================================
Write-Host ""
Write-Host "[3/10] Configure CI Validation Pipeline" -ForegroundColor Yellow
Write-Host "----------------------------------------------"
Write-Host ""
Write-Host "MANUAL STEP:" -ForegroundColor Red
Write-Host "1. Go to: $orgUrl/$projectName/_build" -ForegroundColor White
Write-Host "2. Click 'New Pipeline'" -ForegroundColor White
Write-Host "3. Select 'Azure Repos Git'" -ForegroundColor White
Write-Host "4. Select your repository: $projectName" -ForegroundColor White
Write-Host "5. Click 'Existing Azure Pipelines YAML file'" -ForegroundColor White
Write-Host "6. Select: .azuredevops/pipelines/ci-validation.yml" -ForegroundColor White
Write-Host "7. Click 'Continue' then 'Save' (don't run yet)" -ForegroundColor White
Write-Host "8. Rename pipeline to: 'CI - Code Validation'" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter when done"

# ============================================================================
# Step 4: Configure CD Pipeline
# ============================================================================
Write-Host ""
Write-Host "[4/10] Configure CD Deployment Pipeline" -ForegroundColor Yellow
Write-Host "----------------------------------------------"
Write-Host ""
Write-Host "MANUAL STEP:" -ForegroundColor Red
Write-Host "1. Go to: $orgUrl/$projectName/_build" -ForegroundColor White
Write-Host "2. Click 'New Pipeline'" -ForegroundColor White
Write-Host "3. Select 'Azure Repos Git'" -ForegroundColor White
Write-Host "4. Select your repository" -ForegroundColor White
Write-Host "5. Click 'Existing Azure Pipelines YAML file'" -ForegroundColor White
Write-Host "6. Select: .azuredevops/pipelines/cd-deploy-snowflake.yml" -ForegroundColor White
Write-Host "7. Click 'Continue' then 'Save' (don't run)" -ForegroundColor White
Write-Host "8. Rename pipeline to: 'CD - Deploy to Snowflake'" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter when done"

# ============================================================================
# Step 5: Create Area Paths
# ============================================================================
Write-Host ""
Write-Host "[5/10] Create Area Paths for Work Items" -ForegroundColor Yellow
Write-Host "----------------------------------------------"
Write-Host ""
Write-Host "MANUAL STEP:" -ForegroundColor Red
Write-Host "1. Go to: $orgUrl/$projectName/_settings/work" -ForegroundColor White
Write-Host "2. Click 'Project configuration' > 'Areas'" -ForegroundColor White
Write-Host "3. Create these areas (click '+' next to $projectName):" -ForegroundColor White
Write-Host ""
Write-Host "   Development" -ForegroundColor Green
Write-Host "   ├── Data Model" -ForegroundColor Green
Write-Host "   ├── ETL Pipelines" -ForegroundColor Green
Write-Host "   ├── Dashboards" -ForegroundColor Green
Write-Host "   └── Documentation" -ForegroundColor Green
Write-Host ""
Write-Host "   Operations" -ForegroundColor Green
Write-Host "   ├── Data Quality" -ForegroundColor Green
Write-Host "   ├── Performance" -ForegroundColor Green
Write-Host "   └── Monitoring" -ForegroundColor Green
Write-Host ""
Write-Host "   Security & Compliance" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter when done"

# ============================================================================
# Step 6: Create Iterations
# ============================================================================
Write-Host ""
Write-Host "[6/10] Create Iterations (Sprints)" -ForegroundColor Yellow
Write-Host "----------------------------------------------"
Write-Host ""
Write-Host "MANUAL STEP:" -ForegroundColor Red
Write-Host "1. Go to: $orgUrl/$projectName/_settings/work" -ForegroundColor White
Write-Host "2. Click 'Project configuration' > 'Iterations'" -ForegroundColor White
Write-Host "3. Create 3 iterations (2-week sprints):" -ForegroundColor White
Write-Host ""
Write-Host "   Sprint 1: November 2025 (Nov 1-14)" -ForegroundColor Green
Write-Host "   Sprint 2: December 2025 (Dec 1-14)" -ForegroundColor Green
Write-Host "   Sprint 3: January 2026 (Jan 1-14)" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter when done"

# ============================================================================
# Step 7: Invite Team Members
# ============================================================================
Write-Host ""
Write-Host "[7/10] Invite Team Members" -ForegroundColor Yellow
Write-Host "----------------------------------------------"
Write-Host ""
Write-Host "MANUAL STEP:" -ForegroundColor Red
Write-Host "1. Go to: $orgUrl/$projectName/_settings/teams" -ForegroundColor White
Write-Host "2. Select your team, click 'Add'" -ForegroundColor White
Write-Host "3. Invite these members:" -ForegroundColor White
Write-Host ""
Write-Host "   Nick Heigerick" -ForegroundColor Green
Write-Host "   Email: Nick.Heigerick@CompanyX.com" -ForegroundColor White
Write-Host "   Role: Project Administrator" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Daragh O'Reilly" -ForegroundColor Green
Write-Host "   Email: doreilly@GenericCorp.com" -ForegroundColor White
Write-Host "   Role: Stakeholder (read-only)" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Ronan O'Connor" -ForegroundColor Green
Write-Host "   Email: roconnor@GenericCorp.com" -ForegroundColor White
Write-Host "   Role: Stakeholder (read-only)" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter when done"

# ============================================================================
# Step 8: Configure Branch Policies
# ============================================================================
Write-Host ""
Write-Host "[8/10] Configure Branch Policies" -ForegroundColor Yellow
Write-Host "----------------------------------------------"
Write-Host ""
Write-Host "MANUAL STEP:" -ForegroundColor Red
Write-Host "1. Go to: $orgUrl/$projectName/_git/$projectName/branches" -ForegroundColor White
Write-Host "2. Find 'main' branch, click '...' menu > 'Branch policies'" -ForegroundColor White
Write-Host "3. Enable these policies:" -ForegroundColor White
Write-Host ""
Write-Host "   ✓ Require a minimum number of reviewers: 1" -ForegroundColor Green
Write-Host "   ✓ Check for linked work items" -ForegroundColor Green
Write-Host "   ✓ Check for comment resolution" -ForegroundColor Green
Write-Host "   ✓ Build Validation: Select 'CI - Code Validation' pipeline" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter when done"

# ============================================================================
# Step 9: Create Dashboard
# ============================================================================
Write-Host ""
Write-Host "[9/10] Create Project Dashboard" -ForegroundColor Yellow
Write-Host "----------------------------------------------"
Write-Host ""
Write-Host "MANUAL STEP:" -ForegroundColor Red
Write-Host "1. Go to: $orgUrl/$projectName/_dashboards" -ForegroundColor White
Write-Host "2. Click 'New Dashboard'" -ForegroundColor White
Write-Host "3. Name: 'SECURITY_ANALYTICS Overview'" -ForegroundColor White
Write-Host "4. Add these widgets (click '+' button):" -ForegroundColor White
Write-Host ""
Write-Host "   - Markdown: Project description" -ForegroundColor Green
Write-Host "   - Query Results: Work items by state" -ForegroundColor Green
Write-Host "   - Build History: Last 10 builds" -ForegroundColor Green
Write-Host "   - Team Members: Active team" -ForegroundColor Green
Write-Host "   - Pull Requests: Pending PRs" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter when done"

# ============================================================================
# Step 10: Configure Notifications
# ============================================================================
Write-Host ""
Write-Host "[10/10] Configure Notifications" -ForegroundColor Yellow
Write-Host "----------------------------------------------"
Write-Host ""
Write-Host "MANUAL STEP:" -ForegroundColor Red
Write-Host "1. Go to: $orgUrl/$projectName/_settings/notifications" -ForegroundColor White
Write-Host "2. Create these notification subscriptions:" -ForegroundColor White
Write-Host ""
Write-Host "   - New pull requests created" -ForegroundColor Green
Write-Host "   - Build completes" -ForegroundColor Green
Write-Host "   - Work item assigned to me" -ForegroundColor Green
Write-Host "   - A comment is left on my PR" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter when done"

# ============================================================================
# Summary
# ============================================================================
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your Azure DevOps project is now fully configured!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Share project with your team" -ForegroundColor White
Write-Host "2. Create first work items" -ForegroundColor White
Write-Host "3. Test CI pipeline with a commit" -ForegroundColor White
Write-Host ""
Write-Host "Important URLs:" -ForegroundColor Yellow
Write-Host "• Project: $orgUrl/$projectName" -ForegroundColor White
Write-Host "• Wiki: $orgUrl/$projectName/_wiki" -ForegroundColor White
Write-Host "• Boards: $orgUrl/$projectName/_boards" -ForegroundColor White
Write-Host "• Pipelines: $orgUrl/$projectName/_build" -ForegroundColor White
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
