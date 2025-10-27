@echo off
REM ================================================================
REM Push Changes to Azure DevOps
REM ================================================================

cd /d "%~dp0"

echo.
echo ========================================
echo Push to Azure DevOps
echo ========================================
echo.

echo [Step 1/5] Checking git status...
echo.
git status

echo.
echo [Step 2/5] Adding all changes...
echo.
git add .

echo.
echo [Step 3/5] Showing staged files...
echo.
git status

echo.
echo [Step 4/5] Creating commit...
echo.
echo Commit message:
echo feat: add automated Streamlit deployment system with comprehensive logging
echo.

git commit -m "feat: add automated Streamlit deployment system with comprehensive logging" -m "- Add automated deployment scripts for 18 Streamlit apps" -m "- Implement single SSO authentication (no multiple popups)" -m "- Add real-time progress tracking with animated counter" -m "- Create comprehensive logging system (text, JSON, SQL)" -m "- Fix np.random.randn() compatibility issues" -m "- Fix download button functionality" -m "- Add deployment verification and stage checking tools" -m "- Create WIKI_08_STREAMLIT_DEPLOYMENT.md" -m "- Update WIKI_01 with deployment automation section" -m "" -m "Deployment Results:" -m "- 18/18 apps deployed successfully" -m "- Database: DEV_REPORTING" -m "- Schema: SECURITY_ANALYTICS" -m "- Status: All apps operational"

echo.
echo [Step 5/5] Pushing to Azure DevOps...
echo.

git push azure main

echo.
echo ========================================
echo Push Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Upload WIKI_08_STREAMLIT_DEPLOYMENT.md to Azure DevOps Wiki
echo 2. Share deployment guide with team
echo.
pause
