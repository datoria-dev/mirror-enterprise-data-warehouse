# Manual Wiki Clone with Authentication
# This script helps diagnose and clone the Azure DevOps wiki

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Azure DevOps Wiki Clone Diagnostic" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Project info
$Organization = "CompanyX"
$Project = "GIS - SECURITY_ANALYTICS - DW"
$ProjectEncoded = "GIS%20-%20ITSECKPI%20-%20DW"

Write-Host "Project Information:" -ForegroundColor Yellow
Write-Host "  Organization: $Organization" -ForegroundColor White
Write-Host "  Project: $Project" -ForegroundColor White
Write-Host ""

# Possible wiki repo URLs
$PossibleUrls = @(
    "https://dev.azure.com/$Organization/$ProjectEncoded/_git/$ProjectEncoded.wiki",
    "https://dev.azure.com/$Organization/$Project/_git/$Project.wiki",
    "https://dev.azure.com/$Organization/GIS-SECURITY_ANALYTICS-DW/_git/GIS-SECURITY_ANALYTICS-DW.wiki",
    "https://$Organization@dev.azure.com/$Organization/$ProjectEncoded/_git/$ProjectEncoded.wiki"
)

Write-Host "Trying possible wiki repository URLs..." -ForegroundColor Yellow
Write-Host ""

$SuccessUrl = $null
$AttemptNumber = 0

foreach ($url in $PossibleUrls) {
    $AttemptNumber++
    Write-Host "[$AttemptNumber/$($PossibleUrls.Count)] Testing URL:" -ForegroundColor Cyan
    Write-Host "  $url" -ForegroundColor Gray
    Write-Host ""

    # Try to get remote info without cloning
    $TestResult = git ls-remote $url 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "  SUCCESS! This URL works!" -ForegroundColor Green
        $SuccessUrl = $url
        break
    } else {
        Write-Host "  Failed: $($TestResult | Select-Object -First 1)" -ForegroundColor Red
        Write-Host ""
    }
}

if ($SuccessUrl) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Found working wiki URL!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "URL: $SuccessUrl" -ForegroundColor White
    Write-Host ""
    Write-Host "Remote branches:" -ForegroundColor Yellow
    git ls-remote --heads $SuccessUrl
    Write-Host ""

    $Clone = Read-Host "Clone this repository now? (y/N)"

    if ($Clone -eq 'y' -or $Clone -eq 'Y') {
        $ClonePath = "C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\wiki-repo"

        if (Test-Path $ClonePath) {
            Write-Host ""
            Write-Host "WARNING: Directory already exists: $ClonePath" -ForegroundColor Yellow
            $DeleteExisting = Read-Host "Delete and re-clone? (y/N)"
            if ($DeleteExisting -eq 'y' -or $DeleteExisting -eq 'Y') {
                Remove-Item -Recurse -Force $ClonePath
                Write-Host "Deleted existing directory" -ForegroundColor Green
            } else {
                Write-Host "Cancelled" -ForegroundColor Yellow
                exit 0
            }
        }

        Write-Host ""
        Write-Host "Cloning wiki repository..." -ForegroundColor Cyan
        Write-Host "NOTE: Browser may open for SSO authentication" -ForegroundColor Yellow
        Write-Host ""

        git clone $SuccessUrl $ClonePath

        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "SUCCESS! Wiki cloned successfully!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Repository location: $ClonePath" -ForegroundColor White
            Write-Host ""

            # Show repo contents
            Write-Host "Repository contents:" -ForegroundColor Yellow
            Get-ChildItem -Path $ClonePath -File | ForEach-Object {
                $size = [math]::Round($_.Length / 1KB, 2)
                Write-Host "  - $($_.Name) ($size KB)" -ForegroundColor White
            }

            # Show subfolders
            $folders = Get-ChildItem -Path $ClonePath -Directory
            if ($folders) {
                Write-Host ""
                Write-Host "Subfolders:" -ForegroundColor Yellow
                $folders | ForEach-Object {
                    Write-Host "  - $($_.Name)/" -ForegroundColor White
                }
            }

            Write-Host ""
            Write-Host "Next steps:" -ForegroundColor Cyan
            Write-Host "  1. Review existing wiki files" -ForegroundColor White
            Write-Host "  2. Create SECURITY_ANALYTICS-Documentation folder" -ForegroundColor White
            Write-Host "  3. Copy new wikis" -ForegroundColor White
            Write-Host "  4. Commit and push" -ForegroundColor White
            Write-Host ""
        } else {
            Write-Host ""
            Write-Host "ERROR: Failed to clone repository" -ForegroundColor Red
            Write-Host "Check authentication and permissions" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Could not find working wiki URL" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible reasons:" -ForegroundColor Yellow
    Write-Host "  1. Wiki is a 'Code Wiki' (not a 'Project Wiki')" -ForegroundColor White
    Write-Host "  2. Authentication required (complete SSO first)" -ForegroundColor White
    Write-Host "  3. Wiki name or project name is different" -ForegroundColor White
    Write-Host ""
    Write-Host "Manual steps to find wiki repo URL:" -ForegroundColor Cyan
    Write-Host "  1. Open Azure DevOps wiki in browser" -ForegroundColor White
    Write-Host "  2. Look for 'Clone wiki' or 'More actions' button" -ForegroundColor White
    Write-Host "  3. Copy the Git clone URL" -ForegroundColor White
    Write-Host "  4. Run: git clone [URL] wiki-repo" -ForegroundColor White
    Write-Host ""
    Write-Host "Alternative: Use Azure DevOps web interface" -ForegroundColor Cyan
    Write-Host "  1. Navigate to wiki" -ForegroundColor White
    Write-Host "  2. Click 'New page'" -ForegroundColor White
    Write-Host "  3. Create pages manually or import markdown" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
