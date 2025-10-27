# 🌳 Git Branching Strategy - SECURITY_ANALYTICS Data Warehouse

## 📋 Overview

This project uses a **simplified Git Flow** branching strategy optimized for data warehouse development with clear separation between production and development code.

---

## 🎯 Branch Structure

### 1. **main** - Production Branch 🔒
**Purpose**: Production-ready code only
**Protection**: Highly protected, requires PR + review
**CI/CD**: Deploys to production Snowflake (if configured)
**Who can merge**: Lead Data Engineer only

**Rules**:
- ✅ All code must pass CI pipeline
- ✅ Requires 1+ code review approval
- ✅ Must have linked work items
- ✅ All comments must be resolved
- ❌ NO direct commits allowed
- ❌ NO force push allowed

**Use Cases**:
- Production releases
- Hotfixes (after PR approval)
- Critical security patches

---

### 2. **develop** - Integration Branch 🔄
**Purpose**: Active development and integration
**Protection**: Moderate protection, requires PR
**CI/CD**: Deploys to DEV Snowflake environment
**Who can merge**: Data Engineers

**Rules**:
- ✅ Must pass CI pipeline
- ✅ Code review recommended (not required)
- ✅ Can merge feature branches here
- ⚠️ Direct commits allowed (but discouraged)

**Use Cases**:
- Integration point for features
- Testing combined changes
- Pre-release staging

---

### 3. **feature/** - Feature Development Branches 🚀
**Naming**: `feature/description-of-feature`
**Created from**: `develop`
**Merged into**: `develop`
**Lifespan**: Short-lived (days to weeks)

**Examples**:
```bash
feature/add-zerofox-integration
feature/improve-data-quality-monitoring
feature/create-executive-dashboard
feature/optimize-crowdstrike-pipeline
```

**Workflow**:
```bash
# Create feature branch
git checkout develop
git pull azure develop
git checkout -b feature/add-new-kpi

# Work on feature
git add .
git commit -m "feat: add new security KPI calculation"

# Push and create PR
git push azure feature/add-new-kpi
# Then create PR in Azure DevOps UI: feature/add-new-kpi → develop
```

---

### 4. **bugfix/** - Bug Fix Branches 🐛
**Naming**: `bugfix/description-of-bug`
**Created from**: `develop`
**Merged into**: `develop`
**Lifespan**: Short-lived (hours to days)

**Examples**:
```bash
bugfix/fix-null-handling-in-qualys
bugfix/correct-data-quality-calculation
bugfix/resolve-snowpipe-timeout
```

**Workflow**:
```bash
# Create bugfix branch
git checkout develop
git pull azure develop
git checkout -b bugfix/fix-date-parsing

# Fix the bug
git add .
git commit -m "fix: correct date parsing in Splunk data"

# Push and create PR
git push azure bugfix/fix-date-parsing
# Create PR: bugfix/fix-date-parsing → develop
```

---

### 5. **hotfix/** - Emergency Production Fixes 🚨
**Naming**: `hotfix/description-of-issue`
**Created from**: `main`
**Merged into**: `main` AND `develop`
**Lifespan**: Very short-lived (hours)

**Examples**:
```bash
hotfix/fix-critical-data-loss
hotfix/resolve-authentication-failure
hotfix/patch-security-vulnerability
```

**Workflow** (ONLY for production emergencies):
```bash
# Create hotfix branch from main
git checkout main
git pull azure main
git checkout -b hotfix/fix-critical-issue

# Fix the critical issue
git add .
git commit -m "hotfix: resolve critical authentication issue"

# Push and create PR to main
git push azure hotfix/fix-critical-issue
# Create PR: hotfix/fix-critical-issue → main

# After merge to main, also merge to develop
git checkout develop
git merge main
git push azure develop
```

---

## 🔄 Workflow Diagrams

### Standard Feature Development Flow

```
main (production)
  │
  │ <- hotfix/* (emergency only)
  │
  ├─────────────────────────────────────>
                                         (release when ready)
develop (integration)
  │
  ├── feature/new-dashboard ────────┐
  │                                   │
  ├── feature/optimize-query ────────┼──> (PR to develop)
  │                                   │
  ├── bugfix/fix-null-values ────────┘
  │
  └─────────────────────────────────>
```

### Release to Production Flow

```
1. Work happens in feature/* branches
2. Features merge to develop via PR
3. Test thoroughly in develop
4. When ready for production:
   develop ──(PR with review)──> main
5. main is tagged with version (v3.1, v3.2, etc.)
```

---

## 📝 Commit Message Convention

Use **Conventional Commits** format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types:
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **refactor**: Code refactoring
- **test**: Adding tests
- **chore**: Maintenance tasks
- **perf**: Performance improvements
- **ci**: CI/CD changes

### Examples:
```bash
feat(qualys): add vulnerability trend analysis view
fix(crowdstrike): correct null handling in device data
docs(wiki): update deployment guide with new steps
refactor(etl): optimize Snowpipe configuration
chore(deps): update snowflake-connector-python to 3.5.0
```

---

## 🛡️ Branch Protection Rules

### Recommended Azure DevOps Branch Policies

#### For **main** branch:

1. **Require a minimum number of reviewers**: 1
   - Require at least 1 approval
   - ✅ Requestors cannot approve their own changes
   - ✅ Reset votes when new commits pushed

2. **Check for linked work items**: Required
   - Every PR must have a work item linked

3. **Check for comment resolution**: Required
   - All comments must be resolved before merge

4. **Limit merge types**:
   - ✅ Squash merge only (keeps history clean)
   - ❌ No fast-forward
   - ❌ No rebase and fast-forward

5. **Build validation**:
   - ✅ Must pass "CI - Code Validation" pipeline
   - ✅ Build expiration: 12 hours

6. **Automatically include reviewers**:
   - Add: Lead Data Engineer (required)
   - Add: Senior Data Engineers (optional)

#### For **develop** branch:

1. **Require a minimum number of reviewers**: 0
   - Reviews recommended but not required
   - Faster iteration for development

2. **Build validation**:
   - ✅ Must pass "CI - Code Validation" pipeline

3. **Limit merge types**:
   - ✅ Allow squash merge
   - ✅ Allow merge commit

---

## 🚀 Quick Reference Commands

### Create Feature Branch
```bash
git checkout develop
git pull azure develop
git checkout -b feature/your-feature-name
# ... work on feature ...
git add .
git commit -m "feat: your feature description"
git push azure feature/your-feature-name
# Create PR in Azure DevOps: feature/your-feature-name → develop
```

### Create Bugfix Branch
```bash
git checkout develop
git pull azure develop
git checkout -b bugfix/your-bug-description
# ... fix the bug ...
git add .
git commit -m "fix: your bug fix description"
git push azure bugfix/your-bug-description
# Create PR in Azure DevOps: bugfix/your-bug-description → develop
```

### Update Your Branch with Latest Develop
```bash
git checkout your-branch-name
git fetch azure
git merge azure/develop
# Resolve conflicts if any
git push azure your-branch-name
```

### Delete Feature Branch After Merge
```bash
# Delete local branch
git branch -d feature/your-feature-name

# Delete remote branch
git push azure --delete feature/your-feature-name
```

---

## 📊 Branch Lifecycle

### Feature Branch Lifecycle

```
Day 1:  Create branch from develop
        ├── Initial implementation
        └── First commit

Day 2:  Continue development
        ├── Add tests
        └── Update documentation

Day 3:  Finalize and PR
        ├── Push to Azure DevOps
        ├── Create Pull Request
        ├── Code review
        ├── Address feedback
        └── Merge to develop

Day 4:  Cleanup
        └── Delete feature branch
```

### Typical Timeline

| Branch Type | Typical Lifespan | Max Recommended |
|-------------|------------------|-----------------|
| feature/*   | 2-5 days | 2 weeks |
| bugfix/*    | 1-2 days | 1 week |
| hotfix/*    | 1-4 hours | 1 day |

---

## 🎯 Best Practices

### ✅ DO:

1. **Create branch for every change**
   - Even small changes should have a branch
   - Makes code review easier

2. **Keep branches short-lived**
   - Merge within a few days
   - Reduces merge conflicts

3. **Pull latest develop before creating branch**
   ```bash
   git checkout develop
   git pull azure develop
   git checkout -b feature/new-thing
   ```

4. **Write descriptive branch names**
   - Good: `feature/add-bitsight-integration`
   - Bad: `fix-bug`, `update`, `temp`

5. **Use Pull Requests for everything**
   - Even for develop → main
   - Provides audit trail

6. **Link work items to PRs**
   - Helps track what was implemented
   - Required for main branch

7. **Keep commits focused**
   - One logical change per commit
   - Easier to review and revert

### ❌ DON'T:

1. **Never commit directly to main**
   - Always use PR process
   - Exception: Initial setup (already done)

2. **Avoid long-lived feature branches**
   - Causes merge hell
   - Hard to review large PRs

3. **Don't push broken code to develop**
   - Test locally first
   - CI should pass

4. **Avoid mixing concerns in one branch**
   - Don't fix bugs in feature branches
   - Keep changes focused

5. **Don't force push to shared branches**
   - Only force push to your own feature branch if needed
   - Never force push to main or develop

---

## 🔧 Setting Up Branch Policies in Azure DevOps

### Step-by-Step Guide

1. **Navigate to Branch Policies**
   ```
   https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/_settings/repositories
   → Select "GIS - SECURITY_ANALYTICS - DW" repository
   → Click "Policies" tab
   → Click on "main" branch
   ```

2. **Enable Required Policies**
   - ✅ Require a minimum number of reviewers: 1
   - ✅ Check for linked work items
   - ✅ Check for comment resolution
   - ✅ Build validation: Select "CI - Code Validation"

3. **Configure Merge Options**
   - ✅ Squash merge
   - ❌ Uncheck other merge types

4. **Repeat for develop branch** (with relaxed rules)

---

## 📈 Monitoring and Metrics

### Useful Queries in Azure DevOps

**Active Feature Branches**:
```
Branches where:
- Name starts with "feature/"
- Last commit within 7 days
- Not merged
```

**Stale Branches (Need Cleanup)**:
```
Branches where:
- Not main or develop
- Last commit > 30 days ago
- Not merged
```

**PR Metrics**:
- Average time to merge
- Number of comments per PR
- Build success rate

---

## 🎓 Training Resources

### For New Team Members

1. **Read this document** (15 minutes)
2. **Watch**: [Git Branching Strategies](https://www.youtube.com/watch?v=aJnFGMclhU8) (10 minutes)
3. **Practice**: Create a feature branch and PR
4. **Reference**: [Azure DevOps Pull Requests](https://docs.microsoft.com/en-us/azure/devops/repos/git/pull-requests)

### Quick Start Checklist for New Developers

- [ ] Clone repository
- [ ] Checkout develop branch
- [ ] Create feature branch for first task
- [ ] Make changes and commit
- [ ] Push branch to Azure DevOps
- [ ] Create Pull Request to develop
- [ ] Request code review
- [ ] Address feedback
- [ ] Merge after approval
- [ ] Delete feature branch

---

## 📞 Questions?

If you're unsure about:
- Which branch to create from?
- Where to merge your changes?
- How to handle merge conflicts?

**Contact**: Lead Data Engineer - SECURITY_ANALYTICS Project

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Oct 23, 2025 | Initial branching strategy |

---

**Last Updated**: October 23, 2025
**Status**: Active and enforced
