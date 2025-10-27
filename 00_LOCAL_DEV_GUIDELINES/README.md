# Local Development Guidelines

**Purpose**: Local development reference documentation for Fuad Onate's laptop environment

**Scope**: These guidelines are for LOCAL DEVELOPMENT ONLY and are separate from project-wide documentation in Azure DevOps Wiki.

---

## 📁 Contents

### Core Guidelines

**[LOCAL_DEV_BEST_PRACTICES.md](LOCAL_DEV_BEST_PRACTICES.md)** - Main reference document
- Language standards (always English)
- Credential standards (professional only)
- Automation standards (with CSV/JSON logs)
- Documentation standards
- Version control rules (what to commit/exclude)
- Snowflake-specific best practices
- Security and performance standards
- Quick reference checklists

**⭐ START HERE** when beginning a new session or when context is lost.

**[QUICK_CONNECTION_GUIDE.md](QUICK_CONNECTION_GUIDE.md)** 🔥 ALL platform connections - NEW!
- SnowSQL quick connect commands
- SnowCLI configuration and usage
- Azure DevOps access and links
- Git local repository commands
- GitHub mirror setup
- Python Snowpark connections
- Quick troubleshooting
- Configuration files reference
- Connection test script

**🚀 USE THIS** at the start of every development session to quickly reconnect to all platforms.

**[test_all_connections.py](test_all_connections.py)** - Connection validator script
- Tests SnowSQL, Git, and Snowpark connections
- Validates snowflake_config.json
- Run: `python 00_LOCAL_DEV_GUIDELINES/test_all_connections.py`

**[SNOWFLAKE_CONNECTION_REFERENCE.md](SNOWFLAKE_CONNECTION_REFERENCE.md)** - Detailed Snowflake connection guide
- Official account details (GenericCorp-CRH_EDW)
- SSO authentication (ALWAYS use externalbrowser)
- Roles and warehouses reference
- Connection methods (SnowSQL, Python, Snowpark, Streamlit)
- Troubleshooting common issues
- Configuration templates

**Use this** for Snowflake-specific connection issues or detailed configuration.

---

### Session Documentation

**[SESSION_FINAL_FIXES_SUMMARY.md](SESSION_FINAL_FIXES_SUMMARY.md)**
- Git push analysis results
- np.random fixes for Snowflake Streamlit
- Download button enhancements
- Files modified in latest session
- Deployment instructions

**[SOPHOS_FIXES_COMPLETE.md](SOPHOS_FIXES_COMPLETE.md)**
- Complete technical details of Sophos app fixes
- All np.random replacements (6 fixes)
- Download button configuration
- Deployment instructions
- Verification commands
- Troubleshooting guide

---

## 🚀 Quick Start

### New Session Checklist

Before starting work:
- [ ] Read [LOCAL_DEV_BEST_PRACTICES.md](LOCAL_DEV_BEST_PRACTICES.md)
- [ ] All work in English
- [ ] Using professional credentials (fuad.onate@CompanyX.com)
- [ ] Automation plan with logging (CSV, JSON, .log)
- [ ] Review recent session docs for context

### Common Tasks

**Fix Streamlit Apps**:
```bash
.\fix_apps.bat
```

**Deploy Apps**:
```bash
.\deploy_apps.bat
```

**Deploy Sophos Only** (for testing):
```bash
.\deploy_sophos_fixed.bat
```

**Analyze Logs**:
```bash
.\analyze_logs.bat
```

---

## ⚠️ Important Notes

### DO NOT Commit to Git

This folder (`00_LOCAL_DEV_GUIDELINES/`) should be **excluded from git commits** because:
- Contains local development notes
- Contains session-specific documentation
- Not relevant for other team members or stakeholders

### For Project-Wide Documentation

See Azure DevOps Wiki:
- WIKI_01_STREAMLIT_APPS.md
- WIKI_06_BEST_PRACTICES.md
- WIKI_08_STREAMLIT_DEPLOYMENT.md

---

## 📋 Key Principles

### 1. Language
- **ALL work in English** (code, docs, commits, variables)

### 2. Credentials
- **Always use professional credentials**
- Never commit credentials to git
- Use `snowflake_config.json` (excluded from git)

### 3. Automation
- **Always create automated scripts**
- Always include logging (text, JSON, CSV)
- Always include progress tracking
- Store logs in dedicated folders

### 4. Documentation
- Document as you go
- Update session summaries
- Keep local notes separate from project docs

### 5. Version Control
- **Never commit**:
  - Credentials files
  - Email drafts (EMAIL_*.md)
  - Personal notes
  - Log files
  - Temporary files

---

## 🔄 Workflow

### Standard Development Flow

1. **Review Guidelines** → Read this README + best practices
2. **Plan Work** → Create automation scripts with logging
3. **Implement** → Code in English, use professional standards
4. **Test** → Test in DEV environment
5. **Document** → Update session docs
6. **Commit** → Only commit production-ready code (no emails, no credentials)
7. **Deploy** → Use automated deployment scripts
8. **Verify** → Check logs, test in Snowflake UI

---

## 📞 Contact

**Developer**: Fuad Onate
**Email**: fuad.onate@CompanyX.com
**Environment**: DEV_REPORTING.SECURITY_ANALYTICS
**Account**: GenericCorp-CRH_EDW

---

## 🗂️ Folder Structure

```
00_LOCAL_DEV_GUIDELINES/
├── README.md                            # This file (overview)
├── LOCAL_DEV_BEST_PRACTICES.md          # Core guidelines (START HERE)
├── QUICK_CONNECTION_GUIDE.md            # ALL platform connections (NEW!)
├── test_all_connections.py              # Connection validator script (NEW!)
├── SNOWFLAKE_CONNECTION_REFERENCE.md    # Detailed Snowflake connection guide
├── QUICK_REFERENCE.md                   # Quick reference card
├── SESSION_FINAL_FIXES_SUMMARY.md       # Latest session results
└── SOPHOS_FIXES_COMPLETE.md             # Sophos app technical details
```

---

## 📚 Related Documentation

**In Azure DevOps** (for all stakeholders):
- WIKI_01_STREAMLIT_APPS.md - Streamlit apps overview
- WIKI_06_BEST_PRACTICES.md - Project-wide best practices
- WIKI_08_STREAMLIT_DEPLOYMENT.md - Deployment guide

**In Project Root** (for reference):
- snowflake_config.json.template - Config template
- .gitignore - What to exclude from git
- deploy_apps.bat - Main deployment script
- fix_apps.bat - Fix known issues script

---

**Created**: 2025-10-25
**Last Updated**: 2025-10-25
**Version**: 1.0
**Status**: Active

---

**Note**: This folder is for LOCAL REFERENCE ONLY. Do not include in Azure DevOps commits.
