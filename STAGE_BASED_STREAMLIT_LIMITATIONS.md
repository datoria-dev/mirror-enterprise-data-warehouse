# Stage-Based Streamlit Apps - Limitations Discovered

## Context
During refactoring attempt to eliminate duplicate code across 18 Streamlit apps.

## Goal (Failed)
- Create shared `utils.py` and `database.py` files
- Import these files from individual `streamlit_app.py` files
- Reduce 2,700 lines of duplicate code across all apps

## What We Tried

### Attempt 1: Import local .py files from Stage
```python
# streamlit_app.py
from utils import px, go, make_subplots, np
from database import get_session, safe_query
```

**Files uploaded to Stage:**
- `utils.py` (10,864 bytes) - Dummy classes for plotly/numpy
- `database.py` (10,000 bytes) - Database utility functions
- `streamlit_app.py` (refactored with imports)

**Result:** ❌ **FAILED**

**Error:**
```
Something went wrong
An error occurred while loading the app. Error:
Python Interpreter Error: TypeError: bad argument type for built-in operation
```

## Root Cause

**Snowflake Stage-based Streamlit apps CANNOT import local .py files from the same Stage.**

### Why This Happens:

1. **Stage-based apps** (created with `ROOT_LOCATION = '@STAGE/folder/'`) use:
   - Files stored in a Snowflake Stage
   - Snowflake's Python interpreter in a sandboxed environment
   - **No support for relative imports** from Stage files

2. **Only imports allowed:**
   - Standard Python libraries
   - Packages declared in `environment.yml` (from PyPI/Conda/Snowflake Anaconda channel)
   - Snowflake-specific packages (snowflake.snowpark, etc.)

3. **Cannot import:**
   - ❌ Local `.py` files in the same Stage folder
   - ❌ Relative imports (`from utils import ...`)
   - ❌ Custom modules not packaged as proper Python packages

## Comparison: Stage-based vs Native

| Feature | Stage-based | Native (UI-editable) |
|---------|-------------|----------------------|
| **Multiple .py files** | ❌ No | ✅ Yes |
| **Import local files** | ❌ No | ✅ Yes |
| **Edit in UI** | ❌ No | ✅ Yes |
| **CI/CD friendly** | ✅ Yes | ❌ No |
| **Version control** | ✅ Yes | ⚠️ Manual |
| **File visibility in UI** | ⚠️ Partial | ✅ Full |
| **Deployment method** | PUT command | UI upload |

## Workarounds (Evaluated)

### ❌ Option 1: Create Python package and add to environment.yml
**Why rejected:**
- Requires packaging utils/database as a proper Python package
- Must publish to PyPI, Conda, or Snowflake Anaconda channel
- Overhead for internal utilities
- Version management complexity

### ❌ Option 2: Migrate to Native Streamlit apps
**Why rejected:**
- Loses CI/CD benefits
- Must recreate all 18 apps in UI
- Harder to version control
- Not suitable for production deployments

### ✅ Option 3: Keep duplicate code (ACCEPTED)
**Why accepted:**
- Works with current Stage-based infrastructure
- No breaking changes
- Maintains CI/CD workflow
- Code is stable and doesn't change frequently
- **Trade-off:** 2,700 lines of duplication across 18 apps is acceptable

## Lessons Learned

1. **Snowflake Stage-based Streamlit apps are single-file only**
   - All code must be in `streamlit_app.py`
   - Cannot split into modules

2. **Duplicate code is acceptable for Stage-based apps**
   - Better to have working, maintainable single files
   - Than to fight platform limitations

3. **Choose deployment method based on needs:**
   - **Stage-based:** Production apps, CI/CD, automated deployments
   - **Native:** Development/testing, quick prototypes, apps needing multiple files

## Final Architecture

### What We're Using:
```
STREAMLIT_APPS_STAGE/
├── Sophos/
│   ├── streamlit_app.py    (42KB - includes all dummy classes)
│   └── environment.yml      (128B)
├── Trellix/
│   ├── streamlit_app.py    (40KB - includes all dummy classes)
│   └── environment.yml
└── ... (16 more apps)
```

### What We Attempted (Doesn't Work):
```
STREAMLIT_APPS_STAGE/
├── Sophos/
│   ├── streamlit_app.py    (38KB - imports from utils/database) ❌
│   ├── utils.py            (10KB - dummy classes) ❌
│   ├── database.py         (10KB - DB functions) ❌
│   └── environment.yml
```

## Recommendations

1. **For current project:** Continue with Stage-based single-file apps
2. **For future projects needing modularity:** Consider Native Streamlit apps
3. **For shared code:** Use Snowflake Snowpark stored procedures or UDFs instead
4. **Documentation:** Keep dummy classes well-commented for maintainability

## References

- Snowflake Documentation: [Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- Date discovered: October 27, 2025
- Apps affected: All 18 SECURITY_ANALYTICS Streamlit apps

## Files Created (Can Be Deleted)

These files were created during the refactoring attempt and are **NOT USED**:

- ✅ DELETE: `utils.py` (root directory)
- ✅ DELETE: `database.py` (root directory)
- ✅ DELETE: `upload_shared_files.sql`
- ✅ DELETE: `upload_shared_files.bat`
- ✅ DELETE: `upload_shared_files_no_compress.sql`
- ⚠️ KEEP: This documentation file for reference

**Cleanup commands:**
```bash
rm utils.py
rm database.py
rm upload_shared_files.sql
rm upload_shared_files.bat
rm upload_shared_files_no_compress.sql
```

Also cleanup Stage files (utils.py and database.py from all 18 app folders) if desired.
