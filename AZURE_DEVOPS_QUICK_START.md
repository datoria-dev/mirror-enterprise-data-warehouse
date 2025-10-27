# Azure DevOps Quick Start
## 5-Minute Setup for SECURITY_ANALYTICS Repository

---

## Step 1: Create Azure DevOps Project (2 minutes)

### Via Web Portal:
1. Go to: https://dev.azure.com
2. Sign in → Select Organization
3. Click **"+ New project"**
4. Fill in:
   - **Name**: `SECURITY_ANALYTICS-DataWarehouse`
   - **Visibility**: Private
   - **Version control**: Git
5. Click **"Create"**

---

## Step 2: Get Repository URL (30 seconds)

After project creation:
1. Go to **Repos** → **Files**
2. Copy the repository URL (top right)

   Format: `https://dev.azure.com/{org}/{project}/_git/{repo}`

   Example: `https://dev.azure.com/fos-CompanyX/SECURITY_ANALYTICS-DataWarehouse/_git/snowflake-SECURITY_ANALYTICS-datawarehouse`

---

## Step 3: Create Personal Access Token (1 minute)

1. Click profile icon (top right) → **Personal access tokens**
2. Click **"+ New Token"**
3. Settings:
   - **Name**: `SECURITY_ANALYTICS Repo Access`
   - **Expiration**: 90 days
   - **Scopes**: Code (Read & Write)
4. Click **"Create"**
5. **COPY THE TOKEN!** (You can't see it again)

---

## Step 4: Push to Azure DevOps (1.5 minutes)

Open PowerShell:

```powershell
# Navigate to GITHUB_REPO
cd "C:\\Projects\\Snowflake_ITSECKPI_Project\GITHUB_REPO"

# Add Azure DevOps as second remote
# REPLACE WITH YOUR ACTUAL URL FROM STEP 2
git remote add azure https://dev.azure.com/{org}/{project}/_git/{repo}

# Example:
git remote add azure https://dev.azure.com/fos-CompanyX/SECURITY_ANALYTICS-DataWarehouse/_git/snowflake-SECURITY_ANALYTICS-datawarehouse

# Verify remotes
git remote -v

# Push to Azure DevOps
git push -u azure main

# When prompted:
# Username: your.email@company.com
# Password: PASTE YOUR PAT TOKEN FROM STEP 3
```

---

## That's It! 🎉

Your repository is now on Azure DevOps!

**View it at**: `https://dev.azure.com/{org}/{project}/_git/{repo}`

---

## Next Steps (Optional)

### Enable Branch Policies
1. Go to **Project Settings** → **Repositories** → Select repo
2. **Branches** → Click **"..."** on `main` → **Branch policies**
3. Enable:
   - ✅ Require minimum number of reviewers: 1
   - ✅ Check for comment resolution

### Create Work Items
1. Go to **Boards** → **Work Items**
2. Create Epic: "SECURITY_ANALYTICS Data Warehouse"
3. Add Features and Tasks

### Enable Wiki
1. Go to **Overview** → **Wiki**
2. **Publish code as wiki** → Select `/03_DOCUMENTATION`

---

## Syncing Both Repositories

After setup, when you make changes:

```bash
# Make changes and commit
git add .
git commit -m "your message"

# Push to both GitHub and Azure DevOps
git push origin main  # GitHub
git push azure main   # Azure DevOps
```

---

## Common Commands

```bash
# Check which remotes you have
git remote -v

# Remove Azure DevOps remote (if needed)
git remote remove azure

# View branches on Azure DevOps
git branch -r | grep azure

# Pull from Azure DevOps
git pull azure main
```

---

## Troubleshooting

### Authentication Failed?
```bash
# Clear credentials and try again
git credential reject
# Type: protocol=https
# Type: host=dev.azure.com
# Press Enter twice, then Ctrl+D (or Ctrl+Z on Windows)

# Try push again
git push azure main
```

### Repository Already Exists?
If Azure DevOps repo has initial files:
```bash
# Pull and merge first
git pull azure main --allow-unrelated-histories

# Resolve conflicts (keep your versions)
git checkout --ours README.md
git add README.md
git commit -m "chore: merge Azure DevOps initial files"

# Push
git push azure main
```

---

## Need More Details?

See the full guide: [AZURE_DEVOPS_SETUP_GUIDE.md](AZURE_DEVOPS_SETUP_GUIDE.md)

---

**Ready?** Follow the 4 steps above and you'll have your repo on Azure DevOps in 5 minutes! 🚀
