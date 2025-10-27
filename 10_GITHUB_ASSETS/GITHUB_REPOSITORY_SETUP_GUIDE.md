# GitHub Repository Setup Guide
## Complete Instructions for Publishing the SECURITY_ANALYTICS Project

This guide provides step-by-step instructions for setting up and publishing the IT Security KPI Data Warehouse project to GitHub.

---

## Table of Contents
1. [Pre-Publication Checklist](#pre-publication-checklist)
2. [File Preparation](#file-preparation)
3. [Repository Creation](#repository-creation)
4. [Initial Commit](#initial-commit)
5. [Repository Configuration](#repository-configuration)
6. [GitHub Features Setup](#github-features-setup)
7. [Post-Publication Tasks](#post-publication-tasks)
8. [Maintenance](#maintenance)

---

## Pre-Publication Checklist

### Security Review
- [ ] Remove all sensitive credentials from `.env` files
- [ ] Verify `.gitignore` excludes all sensitive data
- [ ] Remove personal information (resumes, profiles)
- [ ] Check for API keys or tokens in code
- [ ] Review SQL scripts for embedded credentials
- [ ] Sanitize logs and query results

### File Organization
- [ ] Verify all required files are present
- [ ] Remove duplicate or obsolete files
- [ ] Organize files into proper directories
- [ ] Update all file paths in documentation
- [ ] Verify all links in README.md work

### Documentation Review
- [ ] README.md is complete and accurate
- [ ] CONTRIBUTING.md has clear guidelines
- [ ] LICENSE is appropriate (MIT recommended)
- [ ] All reports in FINAL_DELIVERABLES are up to date
- [ ] Code comments are clear and professional

### Quality Checks
- [ ] All SQL scripts are tested
- [ ] Python scripts run without errors
- [ ] Streamlit apps load successfully
- [ ] No broken links in documentation
- [ ] No TODO comments in production code

---

## File Preparation

### 1. Rename GitHub Files

The following files were created with `GITHUB_` prefixes and need to be renamed:

```bash
# In the project root directory:

# Rename README
move GITHUB_README.md README.md

# Rename .gitignore
move GITHUB_GITIGNORE.txt .gitignore

# Rename LICENSE
move GITHUB_LICENSE.txt LICENSE

# CONTRIBUTING.md is already correctly named
# (GITHUB_CONTRIBUTING.md → CONTRIBUTING.md)
move GITHUB_CONTRIBUTING.md CONTRIBUTING.md
```

**PowerShell commands:**
```powershell
cd "C:\\Projects\\Snowflake_ITSECKPI_Project"

# Backup existing README if needed
if (Test-Path README.md) { Rename-Item README.md README_OLD.md }

# Rename new files
Rename-Item GITHUB_README.md README.md
Rename-Item GITHUB_GITIGNORE.txt .gitignore
Rename-Item GITHUB_LICENSE.txt LICENSE
Rename-Item GITHUB_CONTRIBUTING.md CONTRIBUTING.md
```

### 2. Remove Sensitive Files

```bash
# Remove personal documents
rm "Fuad O. Resume - Oct 2025.pdf"
rm Profile.pdf

# Remove credentials
rm .env  # (keep .env.example)

# Remove large binary files (if not in .gitignore)
rm 06_SOURCE_DATA/*.pbix
rm 08_POWERBI_DASHBOARDS/**/*.pbix
```

### 3. Verify .gitignore

Test that `.gitignore` properly excludes sensitive files:

```bash
# Check what will be committed
git status --ignored

# Should NOT see:
# - .env files
# - *.pdf (personal docs)
# - *.pbix files
# - Query results (*.json in 05_QUERY_RESULTS)
# - Large Excel files
```

---

## Repository Creation

### Option 1: GitHub Web Interface

1. **Go to GitHub**: https://github.com/new

2. **Repository Settings**:
   - **Name**: `snowflake-SECURITY_ANALYTICS-datawarehouse`
   - **Description**:
     ```
     Enterprise IT Security KPI Data Warehouse on Snowflake with automated ETL,
     real-time dashboards, and NIST CSF 2.0-aligned metrics
     ```
   - **Visibility**:
     - Choose **Private** for internal/sensitive projects
     - Choose **Public** if open-sourcing
   - **Initialize**:
     - **DO NOT** check "Add README" (you already have one)
     - **DO NOT** choose a .gitignore template (you have custom one)
     - **DO NOT** choose a license (you already have LICENSE)

3. **Click**: "Create repository"

### Option 2: GitHub CLI

```bash
# Install GitHub CLI if not already installed
# Windows: winget install GitHub.cli
# Mac: brew install gh

# Authenticate
gh auth login

# Create repository
gh repo create snowflake-SECURITY_ANALYTICS-datawarehouse \
  --private \
  --description "Enterprise IT Security KPI Data Warehouse on Snowflake" \
  --source=. \
  --remote=origin
```

---

## Initial Commit

### 1. Initialize Git (if not already done)

```bash
cd "C:\\Projects\\Snowflake_ITSECKPI_Project"

# Initialize git
git init

# Set default branch to 'main'
git branch -M main
```

### 2. Add Remote Origin

```bash
# Replace YOUR_USERNAME and YOUR_REPO with actual values
git remote add origin https://github.com/YOUR_USERNAME/snowflake-SECURITY_ANALYTICS-datawarehouse.git

# Or use SSH (if configured)
git remote add origin git@github.com:YOUR_USERNAME/snowflake-SECURITY_ANALYTICS-datawarehouse.git

# Verify remote
git remote -v
```

### 3. Stage Files

```bash
# Add all files (respecting .gitignore)
git add .

# Check what will be committed
git status

# Should see:
# - README.md
# - LICENSE
# - CONTRIBUTING.md
# - .gitignore
# - All SQL scripts
# - All Python scripts
# - Documentation files
# - Streamlit apps
# etc.

# Should NOT see:
# - .env files
# - Personal PDFs
# - Large binary files
```

### 4. Create Initial Commit

```bash
git commit -m "feat: initial commit of SECURITY_ANALYTICS data warehouse project

- 3-layer Snowflake data warehouse (550+ objects)
- 52 automation objects (tasks, procedures, functions)
- 12 Streamlit validation dashboards
- Top 13 NIST CSF 2.0-aligned KPIs
- 15 security service integrations
- Complete documentation and implementation guides
- $146K annual ROI with 94% reduction in manual operations"
```

### 5. Push to GitHub

```bash
# Push to main branch
git push -u origin main

# If you get an error about upstream, use:
git push --set-upstream origin main
```

---

## Repository Configuration

### 1. Repository Settings

Go to: `https://github.com/YOUR_USERNAME/snowflake-SECURITY_ANALYTICS-datawarehouse/settings`

#### General Settings
- **Features**:
  - ✅ Enable Issues
  - ✅ Enable Discussions
  - ✅ Enable Projects
  - ✅ Enable Wiki (optional)
  - ❌ Disable Sponsorships (unless applicable)

#### Collaborators and Teams
- Add team members with appropriate permissions:
  - **Admin**: Project leads
  - **Write**: Developers and contributors
  - **Read**: Stakeholders and viewers

#### Branches
- Set `main` as default branch
- Add branch protection rules:
  - ✅ Require pull request reviews (1-2 reviewers)
  - ✅ Require status checks to pass
  - ✅ Require conversation resolution before merging
  - ✅ Require linear history
  - ❌ Allow force pushes
  - ❌ Allow deletions

### 2. Topics/Tags

Add repository topics for discoverability:

```
snowflake, data-warehouse, security, kpi, etl, nist-csf,
cybersecurity, analytics, streamlit, python, sql,
enterprise, automation, data-quality
```

### 3. About Section

- **Website**: Link to documentation or project page
- **Description**:
  ```
  Enterprise IT Security KPI Data Warehouse: Snowflake-based 3-layer
  architecture with automated ETL, 15 security service integrations,
  and NIST CSF 2.0-aligned metrics
  ```

---

## GitHub Features Setup

### 1. Create GitHub Issues Templates

Create `.github/ISSUE_TEMPLATE/` directory:

**Bug Report** (`.github/ISSUE_TEMPLATE/bug_report.md`):
```markdown
---
name: Bug Report
about: Report a bug or issue
title: '[BUG] '
labels: bug
assignees: ''
---

**Description**
A clear description of the bug

**Steps to Reproduce**
1. Execute SQL...
2. Run script...
3. See error...

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- Snowflake Version:
- Python Version:
- OS:

**Logs/Screenshots**
```

**Feature Request** (`.github/ISSUE_TEMPLATE/feature_request.md`):
```markdown
---
name: Feature Request
about: Suggest a new feature or enhancement
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

**Is your feature request related to a problem?**
Description of the problem

**Describe the solution you'd like**
Clear description of the desired feature

**Describe alternatives you've considered**
Alternative solutions

**Additional context**
Any other context or screenshots
```

### 2. Create Pull Request Template

Create `.github/pull_request_template.md`:
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Related Issues
Closes #(issue number)

## Testing Performed
- [ ] Unit tests added/updated
- [ ] Integration tests passed
- [ ] Manual testing completed
- [ ] Documentation updated

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] Any dependent changes have been merged and published

## Screenshots (if applicable)
```

### 3. Create GitHub Actions (Optional)

For automated testing and validation:

Create `.github/workflows/tests.yml`:
```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.13'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest

    - name: Run tests
      run: |
        pytest tests/ -v

    - name: SQL Linting
      run: |
        # Add SQL linting if desired
        echo "SQL validation passed"
```

### 4. Setup GitHub Pages (Optional)

For hosting documentation:

1. Go to Settings → Pages
2. Source: Deploy from branch
3. Branch: `gh-pages` or `main` with `/docs` folder
4. Click Save

---

## Post-Publication Tasks

### 1. Create Release

```bash
# Tag the initial release
git tag -a v1.0.0 -m "Initial release: SECURITY_ANALYTICS Data Warehouse v1.0.0"
git push origin v1.0.0
```

On GitHub:
1. Go to "Releases" → "Create a new release"
2. Tag: `v1.0.0`
3. Title: `v1.0.0 - Initial Release`
4. Description:
```markdown
# SECURITY_ANALYTICS Data Warehouse v1.0.0

Initial public release of the IT Security KPI Data Warehouse project.

## Features
- 3-layer Snowflake architecture (550+ objects)
- 52 automation objects (98.1% deployed)
- 12 Streamlit dashboards
- 15 security service integrations
- Top 13 NIST CSF 2.0 KPIs
- Complete documentation

## Deployment
See [Quick Start](README.md#quick-start) for deployment instructions.

## Known Issues
- Requires ACCOUNTADMIN for Snowpipe setup
- 47 empty tables pending ETL population

## Contributors
- Data Engineering Team
```

### 2. Setup GitHub Projects

Create project boards for tracking work:

**Board 1: Development**
- Columns: Backlog, To Do, In Progress, Review, Done

**Board 2: Roadmap**
- Columns: Q1, Q2, Q3, Q4, Future

### 3. Enable Discussions

1. Go to Settings → Discussions → Enable
2. Create categories:
   - **Announcements**: Project updates
   - **General**: General discussions
   - **Ideas**: Feature requests and suggestions
   - **Q&A**: Questions and answers
   - **Show and Tell**: Showcasing implementations

### 4. Add Repository Badges

Add to top of README.md:
```markdown
[![GitHub release](https://img.shields.io/github/v/release/YOUR_USERNAME/snowflake-SECURITY_ANALYTICS-datawarehouse)](https://github.com/YOUR_USERNAME/snowflake-SECURITY_ANALYTICS-datawarehouse/releases)
[![GitHub issues](https://img.shields.io/github/issues/YOUR_USERNAME/snowflake-SECURITY_ANALYTICS-datawarehouse)](https://github.com/YOUR_USERNAME/snowflake-SECURITY_ANALYTICS-datawarehouse/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/YOUR_USERNAME/snowflake-SECURITY_ANALYTICS-datawarehouse)](https://github.com/YOUR_USERNAME/snowflake-SECURITY_ANALYTICS-datawarehouse/pulls)
[![License](https://img.shields.io/github/license/YOUR_USERNAME/snowflake-SECURITY_ANALYTICS-datawarehouse)](LICENSE)
```

---

## Maintenance

### Regular Tasks

#### Weekly
- Review and respond to issues
- Merge approved pull requests
- Update project boards

#### Monthly
- Review and update documentation
- Check for dependency updates
- Review security advisories

#### Quarterly
- Release new versions with accumulated changes
- Update roadmap
- Review contributor guidelines

### Version Management

Follow **Semantic Versioning** (SemVer):
- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (1.1.0): New features (backward compatible)
- **PATCH** (1.0.1): Bug fixes

### Security

- Enable Dependabot for dependency updates
- Enable security advisories
- Respond to security issues within 48 hours
- Keep sensitive data out of commits (use `.gitignore`)

---

## Verification Checklist

After publishing, verify:

- [ ] Repository is accessible (check permissions)
- [ ] README displays correctly with images/badges
- [ ] Links in README work (especially relative links)
- [ ] .gitignore is working (no sensitive files visible)
- [ ] LICENSE is displayed correctly
- [ ] CONTRIBUTING.md is accessible
- [ ] Issues can be created
- [ ] Pull requests can be submitted
- [ ] GitHub Actions run successfully (if configured)
- [ ] All documentation links work
- [ ] Repository topics are visible
- [ ] Repository shows up in search

---

## Troubleshooting

### Issue: Large files rejected

```bash
# If you accidentally added large files:
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/large/file' \
  --prune-empty --tag-name-filter cat -- --all

# Force push (careful!)
git push origin --force --all
```

Better: Use Git LFS for large files

### Issue: Sensitive data committed

1. Remove from repository:
```bash
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/sensitive/file' \
  --prune-empty --tag-name-filter cat -- --all
```

2. Rotate compromised credentials immediately
3. Update `.gitignore` to prevent recurrence

### Issue: Broken links in documentation

```bash
# Use a link checker
npm install -g markdown-link-check
markdown-link-check README.md
```

---

## Additional Resources

- [GitHub Docs](https://docs.github.com/)
- [Git Book](https://git-scm.com/book/en/v2)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## Support

For questions about repository setup:
- Open an issue in the repository
- Contact the Data Engineering Team
- Refer to GitHub documentation

---

**Last Updated**: October 2025
**Document Version**: 1.0
