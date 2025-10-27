# 🌳 Quick Branch Reference - SECURITY_ANALYTICS

## Current Branches

| Branch | Purpose | Protection | Deploy To | Who Can Merge |
|--------|---------|------------|-----------|---------------|
| **main** | Production code | 🔒 High | PROD Snowflake | Lead Engineer only |
| **develop** | Active development | 🔐 Medium | DEV Snowflake | Data Engineers |
| **feature/** | New features | None | - | Creator |
| **bugfix/** | Bug fixes | None | - | Creator |
| **hotfix/** | Emergency fixes | None | PROD (urgent) | Lead Engineer |

---

## 🚀 Quick Commands

### Start New Feature
```bash
git checkout develop
git pull azure develop
git checkout -b feature/your-feature-name
```

### Push Feature and Create PR
```bash
git add .
git commit -m "feat: description"
git push azure feature/your-feature-name
# Then create PR in Azure DevOps: feature/xxx → develop
```

### Update Your Branch
```bash
git fetch azure
git merge azure/develop
```

### After PR Merged
```bash
git checkout develop
git pull azure develop
git branch -d feature/your-feature-name
```

---

## 📋 Branch Naming

| Type | Format | Example |
|------|--------|---------|
| Feature | `feature/description` | `feature/add-zerofox-kpi` |
| Bug Fix | `bugfix/description` | `bugfix/fix-null-dates` |
| Hotfix | `hotfix/description` | `hotfix/auth-failure` |

---

## ✅ Commit Message Format

```
<type>: <description>

Types:
- feat     (new feature)
- fix      (bug fix)
- docs     (documentation)
- refactor (code refactoring)
- chore    (maintenance)
```

**Examples**:
- `feat: add Qualys vulnerability trending`
- `fix: correct null handling in Crowdstrike data`
- `docs: update deployment guide`

---

## 🔄 Typical Workflow

```
1. Create feature branch from develop
   └─> Work locally

2. Commit and push
   └─> CI pipeline runs automatically

3. Create Pull Request
   └─> Request code review

4. Address feedback
   └─> Push additional commits

5. PR approved and merged
   └─> Feature now in develop

6. When ready for production
   └─> Create PR: develop → main
```

---

## 🛡️ Protection Rules

### main branch:
- ✅ Requires 1 code review
- ✅ Must pass CI pipeline
- ✅ Must have work item linked
- ❌ NO direct commits
- ❌ NO force push

### develop branch:
- ✅ Must pass CI pipeline
- ⚠️ Direct commits allowed (but use PRs)

---

## 📞 Need Help?

See full documentation: **BRANCHING_STRATEGY.md**
