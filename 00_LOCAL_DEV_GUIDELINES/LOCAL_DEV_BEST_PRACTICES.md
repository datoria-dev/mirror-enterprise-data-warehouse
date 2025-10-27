# Local Development Best Practices

**IMPORTANT**: These are LOCAL development best practices for Fuad Onate's development work.
These are NOT the same as the project-wide best practices in the Azure DevOps repository.

**Scope**: Local development environment and workflow
**Audience**: Development work (not for general stakeholders)
**Project**: Snowflake SECURITY_ANALYTICS Data Warehouse
**Environment**: DEV
**Last Updated**: 2025-10-25

**Note**: For project-wide best practices that apply to all stakeholders, see WIKI_06_BEST_PRACTICES.md in Azure DevOps.

---

## Local Development Guidelines

### 1. Language Standards

**ALL documentation, code, comments, and communications MUST be in ENGLISH**

- Code comments: English only
- Documentation: English only
- Variable names: English only
- Function names: English only
- Commit messages: English only
- Wiki pages: English only

**Reason**: Professional standard, team collaboration, maintainability

---

### 2. Credential Standards

**ALWAYS use professional credentials:**

**Snowflake** (Official Account Details):
- **Account Identifier**: `GenericCorp-CRH_EDW`
- **Organization**: `GenericCorp`
- **Account Name**: `CRH_EDW`
- **Account URL**: `GenericCorp-CRH_EDW.snowflakecomputing.com`
- **Login Name**: `FUAD.ONATE@CompanyX.COM`
- **Cloud Platform**: `AZURE`
- **Region**: `MW76572` (Account Locator)
- **Edition**: `Business Critical`

**Authentication** (ALWAYS use this method):
- **Authenticator**: `externalbrowser` (Okta SSO via web browser)
- **Method**: SSO authentication through browser
- **Never use**: Password-based authentication

**Default Role & Warehouse**:
- **Primary Role**: `DEV_DEVELOPER` (use this for development)
- **Primary Warehouse**: `DEV_WH` (Medium size)
- **Database**: `DEV_REPORTING`
- **Schema**: `SECURITY_ANALYTICS`

**Available Roles** (for reference):
- `PRD_DEVELOPER` (Production - use with caution)
- `PRD_LOADER` (Production loading)
- `DEV_ANALYST` (Analysis only)
- `QA_DEVELOPER` (QA environment)
- `QA_ANALYST` (QA analysis)

**Available Warehouses**:
- `DEV_WH` (Medium) - Default for development
- `PROD_WH` (Large) - Production workloads
- `QA_WH` (Medium) - QA testing

**Azure DevOps**:
- Organization: `CompanyX`
- Project: `GIS - SECURITY_ANALYTICS - DW`
- Repository: `GIS - SECURITY_ANALYTICS - DW`
- Remote name: `azure`
- User: Professional email

**Never use**:
- Personal credentials
- Test accounts
- Placeholder emails
- Password authentication (always use SSO)

---

### 3. Automation Standards

**ALWAYS create automated scripts for repetitive tasks**

**Requirements for all automation scripts**:

1. **Logging**:
   - Text logs (`.log`) - Human-readable
   - JSON logs (`.json`) - Structured data for analysis
   - SQL scripts (`.sql`) - SQL commands executed
   - CSV files for tabular data

2. **Log Location**:
   - Central folder: `deployment_logs/`, `execution_logs/`, etc.
   - Timestamped filenames: `deployment_20251025_143022.log`
   - Keep logs for analysis and troubleshooting

3. **Error Handling**:
   - Capture all errors
   - Log error details
   - Provide clear error messages
   - Exit codes (0 = success, non-zero = failure)

4. **Progress Tracking**:
   - Real-time progress indicators
   - Counters for batch operations
   - Status messages
   - Summary at completion

**Examples**:
```bash
# Good
.\deploy_apps.bat          # Automated, with logs, progress tracking
.\analyze_logs.bat         # Automated analysis with CSV/JSON output

# Bad
# Manual step-by-step deployment
# No logging or progress tracking
```

---

### 4. Documentation Standards

**ALL code must be well-documented**

**Required documentation**:

1. **Code Comments**:
   - Function docstrings (what it does, parameters, returns)
   - Complex logic explanations
   - TODO comments for future work

2. **README files**:
   - Project overview
   - Setup instructions
   - Usage examples
   - Troubleshooting

3. **Wiki Pages**:
   - Comprehensive guides
   - Architecture documentation
   - Deployment processes
   - Best practices

**Document location hierarchy**:
1. Code comments (inline)
2. README files (in directories)
3. Wiki pages (Azure DevOps Wiki)
4. Architecture docs (separate documents)

---

### 5. Version Control Standards

**What to COMMIT to repository**:

✅ **Include**:
- Source code (.py, .sql, .yml)
- Configuration templates (.template, .example)
- Documentation (.md)
- Automation scripts (.bat, .ps1, .sh)
- Requirements files (requirements.txt, environment.yml)
- README files

❌ **Never commit**:
- Credentials files (`snowflake_config.json`, `.env`)
- Secrets or API keys
- Email templates (drafts for internal communication)
- Personal notes
- Temporary files (`.tmp`, `.bak`)
- Log files (keep locally only)
- Large data files (use .gitignore)
- OneDrive or cloud sync files

**Always use `.gitignore`**:
```
# Credentials
snowflake_config.json
.env
credentials.json

# Logs
*.log
deployment_logs/
execution_logs/

# Temporary
*.tmp
*.bak
~$*

# Email drafts
EMAIL_DRAFT_*.md
```

---

### 6. Snowflake-Specific Best Practices

**Environment Structure**:

**DEV Environment**:
- Database: `DEV_REPORTING`
- Schema: `SECURITY_ANALYTICS`
- Warehouse: `DEV_WH`
- Role: `DEV_DEVELOPER`

**Streamlit Apps**:
- Location: `DEV_REPORTING.SECURITY_ANALYTICS`
- Stage: `STREAMLIT_APPS_STAGE`
- Naming: `STREAMLIT_<APP_NAME>`
- Files: Both `.py` and `.yml` required

**Compatibility Notes**:
- Snowflake Streamlit has limited numpy support
- Use Python's `random` module instead of `np.random`
- Use `random.gauss(0, 1)` instead of `np.random.randn()`
- Always test in Snowflake environment before deployment

---

### 7. Code Quality Standards

**Python Code**:
- PEP 8 compliance
- Type hints where applicable
- Error handling (try/except)
- Logging statements
- Clear variable names

**SQL Code**:
- Uppercase keywords (SELECT, FROM, WHERE)
- Proper indentation
- Comments for complex queries
- Avoid hardcoded values (use variables)

**Batch/PowerShell Scripts**:
- Clear echo messages
- Error checking
- Pause for user confirmation when needed
- Help text at the top

---

### 8. Testing Standards

**Before committing code**:

1. **Functional Testing**:
   - Test all main functionality
   - Test error cases
   - Test with sample data

2. **Deployment Testing**:
   - Test in DEV environment
   - Verify deployment logs
   - Check Snowflake UI

3. **Documentation Testing**:
   - Verify links work
   - Check code examples
   - Ensure commands are correct

**Test Evidence**:
- Save test results to files
- Document test cases
- Include in deployment logs

---

### 9. Communication Standards

**DO NOT mention in documentation**:
- AI tools or assistants
- Specific AI model names
- "Generated by..." statements
- Implementation tools used

**Instead, focus on**:
- Technical implementation
- Business value
- User benefits
- Deployment process

**Example**:

❌ **Bad**:
```
This code was generated using an AI assistant to help automate...
```

✅ **Good**:
```
This automated deployment system streamlines the deployment of 18 Streamlit applications...
```

---

### 10. Deployment Standards

**Deployment Process**:

1. **Pre-deployment**:
   - Fix known issues (run `fix_apps.bat`)
   - Review changes
   - Test locally if possible

2. **Deployment**:
   - Use automated deployment scripts
   - Single SSO authentication
   - Monitor progress
   - Capture logs

3. **Post-deployment**:
   - Verify deployment
   - Test functionality
   - Analyze logs
   - Document any issues

**Deployment Checklist**:
- [ ] Code reviewed
- [ ] Issues fixed
- [ ] Documentation updated
- [ ] Logs enabled
- [ ] Deployment script tested
- [ ] Verification plan ready

---

### 11. File Organization

**Project Structure**:
```
Snowflake_ITSECKPI_Project_DEV/
├── 01_SQL_SCRIPTS/          # SQL scripts
├── 02_PYTHON_SCRIPTS/       # Python automation
├── 03_PYTHON_SCRIPTS/       # Additional Python tools
├── 07_STREAMLIT_APPS/       # Working Streamlit apps
├── 13_STREAMLIT_COMPLETE/   # Production-ready apps
├── deployment_logs/         # Deployment logs (not in git)
├── WIKI_*.md               # Wiki documentation
├── README*.md              # Documentation
├── *.bat                   # Automation scripts
├── snowflake_config.json.template  # Config template
├── .gitignore              # Git ignore rules
└── PROJECT_BEST_PRACTICES.md  # This file
```

**Naming Conventions**:
- Scripts: `verb_noun.py` (e.g., `deploy_apps.py`)
- Batch files: `verb_noun.bat` (e.g., `deploy_apps.bat`)
- Documentation: `SCREAMING_SNAKE_CASE.md` (e.g., `DEPLOYMENT_GUIDE.md`)
- Wiki pages: `WIKI_##_TITLE.md` (e.g., `WIKI_08_STREAMLIT_DEPLOYMENT.md`)

---

### 12. Troubleshooting Standards

**When encountering issues**:

1. **Capture Evidence**:
   - Error messages (full text)
   - Screenshots
   - Log files
   - Environment details

2. **Document the Issue**:
   - What happened
   - Expected behavior
   - Steps to reproduce
   - Environment info

3. **Document the Solution**:
   - Root cause
   - Fix applied
   - Verification steps
   - Prevention measures

**Create Issue Reports**:
- File: `ISSUE_<NAME>_<DATE>.md`
- Include all evidence
- Document resolution
- Update relevant documentation

---

### 13. Security Standards

**Credential Management**:
- Never hardcode credentials
- Use config files (excluded from git)
- Use environment variables when appropriate
- Use SSO when available

**Snowflake Security**:
- Always use assigned role (DEV_DEVELOPER)
- Never request unnecessary permissions
- Use appropriate warehouse for workload
- Follow least privilege principle

**Data Security**:
- No PII in logs
- No sensitive data in documentation
- Sanitize examples and screenshots
- Follow company data policies

---

### 14. Performance Standards

**Optimization Guidelines**:

1. **Snowflake Queries**:
   - Use appropriate warehouse size
   - Limit result sets
   - Use caching when applicable
   - Monitor query performance

2. **Python Scripts**:
   - Use batch operations
   - Minimize API calls
   - Use single SSO sessions
   - Implement progress tracking

3. **Deployment**:
   - Single session for multiple operations
   - Parallel processing where safe
   - Batch file uploads
   - Monitor execution time

---

### 15. Maintenance Standards

**Regular Maintenance Tasks**:

1. **Weekly**:
   - Review logs
   - Check app status
   - Update documentation if needed

2. **Monthly**:
   - Review and clean old logs
   - Update dependencies
   - Review and update Wiki pages
   - Archive completed projects

3. **Quarterly**:
   - Review all automation scripts
   - Update best practices
   - Security review
   - Performance optimization

---

## Quick Reference Checklist

**Before starting new work**:
- [ ] All work in English
- [ ] Using professional credentials
- [ ] Automation plan ready
- [ ] Logging configured
- [ ] Documentation plan ready

**Before committing code**:
- [ ] Code tested
- [ ] No credentials in code
- [ ] Documentation updated
- [ ] No email drafts or personal notes
- [ ] .gitignore updated if needed

**Before deploying**:
- [ ] DEV environment confirmed
- [ ] Deployment script tested
- [ ] Logs enabled
- [ ] Verification plan ready
- [ ] Rollback plan ready

**After deploying**:
- [ ] Deployment verified
- [ ] Logs analyzed
- [ ] Documentation updated
- [ ] Team notified if needed
- [ ] Issues documented

---

## Contact and Support

**Project Owner**: Fuad Onate
**Email**: fuad.onate@CompanyX.com
**Environment**: DEV
**Database**: DEV_REPORTING
**Schema**: SECURITY_ANALYTICS

**Resources**:
- Azure DevOps: https://dev.azure.com/CompanyX/GIS%20-%20ITSECKPI%20-%20DW/
- Snowflake: GenericCorp-CRH_EDW account
- Wiki: See WIKI_*.md files in project root

---

---

### 16. Wiki Documentation Standards

**Azure DevOps Wiki Best Practices**:

**Mermaid Diagram Syntax**:
- Azure DevOps uses `:::mermaid` NOT ` ```mermaid`
- Always close with `:::` NOT ` ````
- Test diagrams render correctly in Azure DevOps UI

**Diagram Simplicity Guidelines**:
- **Maximum nodes per diagram**: 8-10 nodes
- **Avoid**: Nested subgraphs, complex relationships, overlapping elements
- **Prefer**: Linear flows (LR or TD), simple decision nodes, clear colors
- **Goal**: User should understand in < 30 seconds

**Example - Good Diagram**:
```mermaid
:::mermaid
flowchart LR
    A[Step 1] --> B[Step 2] --> C[Step 3] --> D[Result]
    style A fill:#e3f2fd
    style D fill:#e8f5e9
:::
```

**Example - Bad Diagram**:
```mermaid
:::mermaid
graph TB
    subgraph "Complex Layer 1"
        subgraph "Nested Layer 2"
            A1 & A2 & A3 --> B1 & B2
        end
    end
    # Too many nodes, nested subgraphs, difficult to read
:::
```

**Color Coding Standards**:
- Use consistent color schemes across diagrams
- Medallion Architecture:
  - Bronze/Landing: `#CD853F` (tan/brown)
  - Silver/Transform: `#C0C0C0` (silver)
  - Gold/Reporting: `#FFD700` (gold)
- Data Flow:
  - Sources: `#e1f5ff` (light blue)
  - Processing: `#e8f5e9` (light green)
  - Output: `#e0f2f1` (light teal)

**Wiki Image Support**:
- Preferred: Mermaid diagrams (editable, version controlled)
- Alternative: PNG/SVG in `.azuredevops/wiki/images/` folder
- Syntax: `![Diagram](/.azuredevops/wiki/images/diagram.png)`

---

### 17. Streamlit Apps - Snowflake Limitations

**CRITICAL: Stage-Based Streamlit Constraints**:

**Cannot Import Local Modules**:
- Stage-based apps CANNOT import other .py files from Stage
- Each `streamlit_app.py` must be self-contained
- Do NOT create shared `utils.py` or `database.py` files

**Library Limitations**:
- `numpy` has limited functionality in Snowflake Streamlit
- `plotly` may have limitations
- Solution: Create `_DummyNumpy` and `_DummyPlotly` replacement classes

**DummyNumpy Implementation Pattern**:
```python
class _DummyNumpy:
    inf = float('inf')

    class random:
        @staticmethod
        def standard_normal(size=None):
            import random as py_random
            if size is None:
                return py_random.gauss(0, 1)
            return [py_random.gauss(0, 1) for _ in range(size)]

        @staticmethod
        def poisson(lam=1.0, size=None):
            # Use Gaussian approximation for large lambda
            import random as py_random
            import math
            if size is None:
                return max(0, int(py_random.gauss(lam, math.sqrt(lam))))
            return [max(0, int(py_random.gauss(lam, math.sqrt(lam))))
                    for _ in range(size)]

    def arange(self, *args):
        if len(args) == 1:
            return list(range(int(args[0])))
        elif len(args) == 2:
            return list(range(int(args[0]), int(args[1])))
        return list(range(int(args[0]), int(args[1]), int(args[2])))

# Use pandas Series for arithmetic operations
random_data = pd.Series(np.random.standard_normal(30))
result = 100 + random_data * 5  # Works with Series
```

**Deployment Requirements**:
- File structure: Each app folder needs `streamlit_app.py` + `environment.yml`
- Upload to: `STREAMLIT_APPS_STAGE` via snowsql PUT command
- Create object: `CREATE OR REPLACE STREAMLIT` statement
- Force refresh: Always use `CREATE OR REPLACE` to reload code changes

**Testing Protocol**:
1. Test locally first (if possible)
2. Upload to Stage
3. Create/Replace Streamlit object
4. Test in Snowflake UI
5. Check for runtime errors
6. Verify all features work

**Documentation Reference**:
- See: `STAGE_BASED_STREAMLIT_LIMITATIONS.md`
- See: Session summaries with numpy fixes

---

### 18. Automation Script Standards

**Script Requirements**:

**Logging Functions**:
```python
import datetime
from pathlib import Path

# Setup logging
LOG_DIR = Path("deployment_logs")
LOG_DIR.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = LOG_DIR / f"operation_{timestamp}.log"

def log(message):
    """Log to both console and file"""
    print(message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{message}\n")
```

**Error Handling Pattern**:
```python
def safe_operation(item):
    try:
        # Perform operation
        result = perform_task(item)
        log(f"✓ Success: {item}")
        return True
    except Exception as e:
        log(f"✗ Error: {item} - {str(e)}")
        return False
```

**Progress Tracking**:
```python
total = len(items)
successful = 0
failed = 0

for i, item in enumerate(items, 1):
    log(f"[{i}/{total}] Processing {item}...")
    if process_item(item):
        successful += 1
    else:
        failed += 1

log(f"\nSummary: {successful} successful, {failed} failed out of {total}")
```

**Backup Before Modification**:
```python
import shutil
from pathlib import Path

def create_backup(file_path):
    """Create timestamped backup before modifying"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"backups/backup_{timestamp}")
    backup_dir.mkdir(parents=True, exist_ok=True)

    backup_path = backup_dir / file_path.name
    shutil.copy2(file_path, backup_path)
    log(f"Backup created: {backup_path}")
    return backup_path
```

**Common Mistakes to Avoid**:
- ❌ `log()` without message parameter
- ❌ Modifying files without backups
- ❌ No error handling in loops
- ❌ Unicode issues in Windows console (use `.encode('ascii', 'ignore')`)
- ❌ Hardcoded paths (use Path objects)
- ❌ No progress indicators for long operations

---

### 19. Git Workflow Standards

**Commit Message Format**:
```
<type>: <short description>

<detailed description>

## Changes Made
- Bullet point 1
- Bullet point 2

## Impact
- What changed
- Why it matters

Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Commit Types**:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `refactor:` - Code restructuring without functionality change
- `chore:` - Maintenance tasks
- `test:` - Adding/updating tests

**Branch Strategy**:
- Main branch: `main`
- Always work on `main` for DEV environment
- Use feature branches for major changes: `feature/description`
- Pull before push to avoid conflicts

**Pre-Commit Checklist**:
```bash
# 1. Check status
git status

# 2. Review changes
git diff

# 3. Stage specific files
git add path/to/file.py

# 4. Commit with message
git commit -m "feat: add new feature"

# 5. Pull latest
git pull azure main

# 6. Resolve conflicts if any
# Edit files, then:
git add resolved_file.py
git commit

# 7. Push to remote
git push azure main
```

**Merge Conflict Resolution**:
- Prefer `--ours` for local changes when appropriate
- Use `--theirs` for remote changes (like .gitignore updates)
- Abort merge if unsure: `git merge --abort`
- Stash local changes: `git stash` before pulling

---

### 20. Troubleshooting Common Issues

**Issue: Mermaid Diagrams Not Rendering in Azure DevOps**
- **Problem**: Using ` ```mermaid` syntax
- **Solution**: Use `:::mermaid` and close with `:::`
- **Verification**: Check in Azure DevOps UI

**Issue: Streamlit App Shows "Cannot Import Module"**
- **Problem**: Trying to import local .py files from Stage
- **Solution**: Make `streamlit_app.py` self-contained
- **Documentation**: See `STAGE_BASED_STREAMLIT_LIMITATIONS.md`

**Issue: numpy AttributeError in Streamlit**
- **Problem**: Missing numpy methods in Snowflake environment
- **Solution**: Implement `_DummyNumpy` class with required methods
- **Pattern**: Use Python stdlib (`random`, `math`) + pandas

**Issue: TypeError with List Arithmetic**
- **Problem**: `85 + [list] * 2` doesn't work
- **Solution**: Convert to pandas Series first
- **Example**: `pd.Series(np.random.standard_normal(30))`

**Issue: Git Push Rejected (Remote Has Changes)**
- **Problem**: Someone else pushed to main
- **Solution**:
  ```bash
  git stash                    # Save local changes
  git pull azure main          # Get remote changes
  git stash pop                # Restore local changes
  # Resolve conflicts if any
  git push azure main          # Push
  ```

**Issue: Snowflake SSO Authentication Fails**
- **Problem**: Missing `--authenticator externalbrowser` parameter
- **Solution**: Always use full snowsql command:
  ```bash
  snowsql -a GenericCorp-CRH_EDW -u fuad.onate@CompanyX.com \
          --authenticator externalbrowser \
          -w DEV_WH -d DEV_REPORTING -s SECURITY_ANALYTICS -r DEV_DEVELOPER
  ```

**Issue: Python Script Unicode Error on Windows**
- **Problem**: Emojis or special chars in console output
- **Solution**: Strip non-ASCII before printing:
  ```python
  console_msg = message.encode('ascii', 'ignore').decode('ascii')
  print(console_msg)
  ```

---

**Version**: 2.0
**Last Updated**: 2025-10-27
**Status**: Active

---

## Notes for New Chat Sessions

**When starting a new chat or using compact/summary**:

1. Reference this file first
2. Follow all guidelines listed here
3. Maintain consistency with existing work
4. Update this file if new best practices emerge
5. Always work in English
6. Always use professional credentials
7. Always create automated, logged processes
8. Remember Stage-based Streamlit limitations
9. Use simplified Mermaid diagrams with `:::mermaid` syntax
10. Create backups before modifying files
