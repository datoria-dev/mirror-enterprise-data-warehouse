# Snowflake Streamlit Limitations

**Official Source**: https://docs.snowflake.com/en/developer-guide/streamlit/limitations
**Environment**: Snowflake Streamlit in Snowflake (SiS)
**Last Updated**: 2025-10-25
**Last Verified**: 2025-10-25

---

## ⚠️ Critical Limitations

### 1. STAGE GET Errors - Missing Database Context ⚡ NEW

**Issue**: Streamlit apps may throw STAGE GET errors if database context is not set

**Error Message**:
```
Could not read/write file. Error: 090105: Cannot perform STAGE GET.
This session does not have a current database. Call 'USE DATABASE;'
or use a qualified name.
```

**Cause**:
- Streamlit internally uses stages for caching and temporary storage
- If no database/schema context is set, these operations fail
- Happens even if your app doesn't explicitly use stages

**Solution**: Set database context immediately after getting session

**Required Code**:
```python
from snowflake.snowpark.context import get_active_session

# Get session
session = get_active_session()

# Set database context to avoid STAGE GET errors
try:
    session.sql("USE DATABASE DEV_REPORTING").collect()
    session.sql("USE SCHEMA SECURITY_ANALYTICS").collect()
except Exception as e:
    st.warning(f"Could not set database context: {e}")

# Rest of your app...
```

**When This Occurs**:
- On app startup
- When using @st.cache_data
- When downloading files
- When Streamlit needs temporary storage

**Always include this fix** at the top of every Streamlit app in Snowflake!

---

### 2. numpy.random Module NOT SUPPORTED

**Issue**: Most `np.random.*` functions do NOT work in Snowflake Streamlit

**Error Example**:
```python
AttributeError: 'function' object has no attribute 'standard_normal'
AttributeError: 'function' object has no attribute 'randn'
AttributeError: 'function' object has no attribute 'poisson'
```

**Functions That DON'T Work**:
- ❌ `np.random.randn()`
- ❌ `np.random.standard_normal()`
- ❌ `np.random.poisson()`
- ❌ `np.random.uniform()`
- ❌ `np.random.randint()`
- ❌ Most other `np.random.*` functions

**Solution**: Use Python's built-in `random` module instead

**Replacement Examples**:

```python
import random

# Normal distribution
# Before (doesn't work):
data = np.random.randn(100)
data = np.random.standard_normal(100)

# After (works):
data = [random.gauss(0, 1) for _ in range(100)]

# Poisson distribution
# Before (doesn't work):
data = np.random.poisson(5, 100)

# After (works - exponential approximation):
data = [int(random.expovariate(1/5)) if 5 > 0 else 0 for _ in range(100)]

# Uniform distribution
# Before (doesn't work):
data = np.random.uniform(0, 10, 100)

# After (works):
data = [random.uniform(0, 10) for _ in range(100)]

# Random integers
# Before (doesn't work):
data = np.random.randint(0, 100, size=50)

# After (works):
data = [random.randint(0, 99) for _ in range(50)]  # Note: numpy high is exclusive, Python is inclusive
```

**Why This Happens**:
- Snowflake Streamlit runs in a sandboxed environment
- Limited numpy functionality for security/performance
- Python standard library has full support

---

### 2. Download Button Browser Compatibility Issues

**Issue**: st.download_button may not work on Windows with Chrome/Edge browsers

**Reported**: May 2025, Streamlit version 1.45.0

**Symptoms**:
- Button appears but doesn't download
- Downloads `.htm` file instead of `.csv`
- No error in console

**Workarounds**:
1. Use Firefox browser
2. Wait for Streamlit bug fix
3. Implement alternative download method

**Correct Implementation** (code is correct, browser issue):
```python
@st.cache_data
def convert_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv_data = convert_to_csv(dataframe)
st.download_button(
    label="Download CSV",
    data=csv_data,
    file_name="data.csv",
    mime="text/csv",               # Required
    key="download_unique_key"      # Required for Snowflake
)
```

**Reference**: Streamlit Community Forum Issue #113611

---

### 3. Content Security Policy (CSP) Restrictions

**Issue**: Restricted resource loading from external sources

**Impact**:
- Cannot load external JavaScript
- Cannot load external CSS
- Cannot load images from arbitrary URLs
- Limited iframe support

**Workaround**:
- Host resources in Snowflake stage
- Use Snowflake-approved CDNs
- Embed data directly in app

---

### 4. Custom Components Limitations

**Issue**: Custom components cannot call external services

**Restrictions**:
- No external API calls from custom components
- Must use Snowflake-provided components only
- Limited custom component support

**Workaround**:
- Use Snowflake's built-in components
- Make API calls from Python backend, not frontend

---

### 5. Data Display Limits

**Issue**: 32 MB message size limit between backend and frontend

**Impact**:
- Large dataframes may fail to render
- Charts with too many data points may fail
- Memory-intensive operations may timeout

**Workarounds**:
- Paginate large datasets
- Aggregate data before display
- Use `st.cache_data` to reduce recomputation
- Limit initial data load

**Example**:
```python
# Bad - may exceed limit
st.dataframe(huge_dataframe)  # 100,000+ rows

# Good - paginated
page_size = 1000
page = st.slider("Page", 1, len(df)//page_size)
st.dataframe(df[(page-1)*page_size:page*page_size])
```

---

### 6. File Upload Size Limit

**Issue**: 200 MB maximum per file for `st.file_uploader`

**Workaround**:
- Use Snowflake stages for large files
- Split files if needed
- Use streaming upload

---

### 7. Session Caching Limitations

**Issue**: Cache only persists within a single session

**Impact**:
- `@st.cache_data` cleared when session ends
- No cross-session caching
- No persistent storage in cache

**Workaround**:
- Use Snowflake tables for persistent data
- Use Snowflake stages for file storage
- Re-compute on session restart

---

### 8. Unsupported Streamlit Features

**Components NOT Supported**:
- ❌ `st.bokeh_chart`
- ❌ `st.toast` (notification)
- ❌ `st.balloons` (animation)
- ❌ Some experimental features

**Use Instead**:
- ✅ `st.plotly_chart` (instead of bokeh)
- ✅ `st.success/st.info/st.warning` (instead of toast)
- ✅ `st.snow` (works, balloons don't)

---

### 9. Package Version Constraints

**Issue**: Limited control over package versions

**Impact**:
- Cannot always use latest packages
- Some packages not available
- Version conflicts possible

**Best Practice**:
- Test in Snowflake environment first
- Use environment.yml for dependencies
- Stick to Snowflake-approved packages

**Example environment.yml**:
```yaml
name: streamlit
channels:
  - snowflake
dependencies:
  - python=3.8
  - snowflake-snowpark-python
  - pandas
  - plotly
  - streamlit
```

---

### 10. Authentication & Permissions

**Issue**: Must respect Snowflake RBAC

**Impact**:
- Users see data based on their role
- Cannot bypass Snowflake security
- Some operations require specific privileges

**Best Practice**:
- Check user permissions in app
- Provide clear error messages
- Document required roles

---

## 🔧 Common Workarounds

### Replace numpy.random Entirely

**Create utility module**:
```python
# utils/random_compatible.py
import random

def randn(size):
    """Snowflake-compatible normal distribution"""
    return [random.gauss(0, 1) for _ in range(size)]

def poisson(lam, size):
    """Snowflake-compatible Poisson approximation"""
    return [int(random.expovariate(1/lam)) if lam > 0 else 0 for _ in range(size)]

def uniform(low, high, size):
    """Snowflake-compatible uniform distribution"""
    return [random.uniform(low, high) for _ in range(size)]

def randint(low, high, size):
    """Snowflake-compatible random integers"""
    return [random.randint(low, high-1) for _ in range(size)]
```

**Usage**:
```python
from utils.random_compatible import randn, poisson

# Now works in Snowflake
data = randn(100)
counts = poisson(5, 50)
```

---

## 📋 Pre-Deployment Checklist

Before deploying to Snowflake Streamlit:

- [ ] No `np.random.*` calls (use Python `random` instead)
- [ ] Download buttons have `key` and `mime` parameters
- [ ] No external resource loading
- [ ] No unsupported Streamlit features (bokeh, toast, balloons)
- [ ] Dataframe sizes < 32 MB
- [ ] File uploads < 200 MB
- [ ] All packages in environment.yml
- [ ] Tested in Snowflake environment
- [ ] Proper error handling for permissions
- [ ] Cache strategy implemented

---

## 🧪 Testing Strategy

### Local Testing (Limited)
```python
# Test locally with Streamlit
streamlit run app.py
```
**Limitations**: Won't catch Snowflake-specific issues

### Snowflake DEV Testing (Recommended)
```python
# Deploy to DEV environment first
# Test all functionality
# Check browser compatibility
# Verify with different roles
```

### Production Deployment
```python
# Only after successful DEV testing
# Monitor for errors
# Check user feedback
```

---

## 📚 Additional Resources

**Official Documentation**:
- Streamlit in Snowflake: https://docs.snowflake.com/en/developer-guide/streamlit/
- Limitations: https://docs.snowflake.com/en/developer-guide/streamlit/limitations
- Troubleshooting: https://docs.snowflake.com/en/developer-guide/streamlit/troubleshooting

**Community Resources**:
- Streamlit Forum: https://discuss.streamlit.io/
- Known Issues: Search for "Snowflake" tag

---

## 📝 Version History

| Date | Version | Notes |
|------|---------|-------|
| 2025-10-25 | 1.0 | Initial documentation based on discovered issues |
| | | - numpy.random limitations |
| | | - Download button browser issues |
| | | - Workarounds documented |

---

**Maintainer**: Fuad Onate (fuad.onate@CompanyX.com)
**Last Review**: 2025-10-25
**Next Review**: 2025-11-25 or when new issues discovered

---

## 🚨 Report New Issues

When you discover new limitations:

1. Document the error message
2. Note the Streamlit version
3. Identify the workaround (if any)
4. Update this document
5. Update project wikis
6. Notify team
