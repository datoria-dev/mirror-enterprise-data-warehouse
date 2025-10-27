# Snowflake Connection Reference

**Purpose**: Quick reference for Snowflake account details and connection methods
**Last Updated**: 2025-10-25
**Environment**: Development (DEV)

---

## 🔐 Account Information

### Official Account Details

| Property | Value |
|----------|-------|
| **Account Identifier** | `GenericCorp-CRH_EDW` |
| **Organization** | `GenericCorp` |
| **Account Name** | `CRH_EDW` |
| **Data Sharing Identifier** | `GenericCorp.CRH_EDW` |
| **Account URL** | `GenericCorp-CRH_EDW.snowflakecomputing.com` |
| **Login Name** | `FUAD.ONATE@CompanyX.COM` |
| **Cloud Platform** | `AZURE` |
| **Account Locator** | `MW76572` |
| **Edition** | `Business Critical` |

---

## 🌐 Authentication

### ⚠️ ALWAYS Use SSO Authentication

**Method**: Okta SSO via web browser

**Configuration**:
```json
{
  "user": "fuad.onate@CompanyX.com",
  "authenticator": "externalbrowser",
  "account": "GenericCorp-CRH_EDW"
}
```

**Why SSO?**:
- ✅ More secure (no password storage)
- ✅ Centralized authentication
- ✅ Automatic session management
- ✅ Company policy requirement

**NEVER use**:
- ❌ Password-based authentication
- ❌ Key-pair authentication (unless specifically required)
- ❌ OAuth tokens (unless for automation)

---

## 👤 Roles

### Primary Role (Development)

**Use this for all development work**:
```
DEV_DEVELOPER
```

### Available Roles

| Role | Environment | Purpose | Use When |
|------|-------------|---------|----------|
| `DEV_DEVELOPER` | Development | Primary dev role | Development work ⭐ |
| `DEV_ANALYST` | Development | Read-only analysis | Data exploration |
| `QA_DEVELOPER` | QA | QA testing | QA environment testing |
| `QA_ANALYST` | QA | QA analysis | QA data review |
| `PRD_DEVELOPER` | Production | Prod development | ⚠️ Production changes (caution!) |
| `PRD_LOADER` | Production | Data loading | Production data loads |

**Default Role**: `DEV_DEVELOPER`

---

## 🏭 Warehouses

### Primary Warehouse (Development)

**Use this for development**:
```
DEV_WH (Medium)
```

### Available Warehouses

| Warehouse | Size | Environment | Purpose | Use When |
|-----------|------|-------------|---------|----------|
| `DEV_WH` | Medium | Development | Primary dev work | Development ⭐ |
| `QA_WH` | Medium | QA | QA testing | QA testing |
| `PROD_WH` | Large | Production | Production workloads | Production only |

**Default Warehouse**: `DEV_WH`

---

## 💾 Database & Schema

### Primary Location (Development)

**Database**: `DEV_REPORTING`
**Schema**: `SECURITY_ANALYTICS`

**Full Path**: `DEV_REPORTING.SECURITY_ANALYTICS`

### Typical Objects

**Tables**: Security tool data tables
**Views**: Data views for reporting
**Streamlit Apps**: 18 security dashboards
**Stages**: `STREAMLIT_APPS_STAGE`

---

## 🔌 Connection Methods

### 1. SnowSQL (Command Line)

**Basic Connection**:
```bash
snowsql -a GenericCorp-CRH_EDW -u fuad.onate@CompanyX.com --authenticator externalbrowser
```

**With Context**:
```bash
snowsql -a GenericCorp-CRH_EDW \
  -u fuad.onate@CompanyX.com \
  --authenticator externalbrowser \
  -w DEV_WH \
  -d DEV_REPORTING \
  -s SECURITY_ANALYTICS \
  -r DEV_DEVELOPER
```

**Execute Query**:
```bash
snowsql -a GenericCorp-CRH_EDW \
  -u fuad.onate@CompanyX.com \
  --authenticator externalbrowser \
  -q "SELECT CURRENT_USER();"
```

**Execute SQL File**:
```bash
snowsql -a GenericCorp-CRH_EDW \
  -u fuad.onate@CompanyX.com \
  --authenticator externalbrowser \
  -f script.sql
```

---

### 2. Python (snowflake-connector-python)

**Basic Connection**:
```python
import snowflake.connector

conn = snowflake.connector.connect(
    user='fuad.onate@CompanyX.com',
    authenticator='externalbrowser',
    account='GenericCorp-CRH_EDW',
    warehouse='DEV_WH',
    database='DEV_REPORTING',
    schema='SECURITY_ANALYTICS',
    role='DEV_DEVELOPER'
)

cursor = conn.cursor()
cursor.execute("SELECT CURRENT_USER()")
print(cursor.fetchone())
cursor.close()
conn.close()
```

**Using Configuration File**:
```python
import json
import snowflake.connector

with open('snowflake_config.json') as f:
    config = json.load(f)

conn = snowflake.connector.connect(**config)
```

---

### 3. Snowpark (Python)

```python
from snowflake.snowpark import Session

connection_parameters = {
    "user": "fuad.onate@CompanyX.com",
    "authenticator": "externalbrowser",
    "account": "GenericCorp-CRH_EDW",
    "warehouse": "DEV_WH",
    "database": "DEV_REPORTING",
    "schema": "SECURITY_ANALYTICS",
    "role": "DEV_DEVELOPER"
}

session = Session.builder.configs(connection_parameters).create()

# Use session
df = session.sql("SELECT CURRENT_USER()").collect()
print(df)

session.close()
```

---

### 4. Streamlit in Snowflake

**Within Streamlit App**:
```python
from snowflake.snowpark.context import get_active_session

# Get session (already authenticated)
session = get_active_session()

# Set context (ALWAYS do this to avoid STAGE GET errors)
try:
    session.sql("USE DATABASE DEV_REPORTING").collect()
    session.sql("USE SCHEMA SECURITY_ANALYTICS").collect()
except Exception as e:
    st.warning(f"Could not set database context: {e}")

# Use session
df = session.sql("SELECT * FROM my_table").to_pandas()
```

---

## 🔍 Verification Commands

### Test Connection
```sql
SELECT CURRENT_USER();
SELECT CURRENT_ROLE();
SELECT CURRENT_WAREHOUSE();
SELECT CURRENT_DATABASE();
SELECT CURRENT_SCHEMA();
```

### Check Context
```sql
SELECT
    CURRENT_USER() AS USER,
    CURRENT_ROLE() AS ROLE,
    CURRENT_WAREHOUSE() AS WAREHOUSE,
    CURRENT_DATABASE() AS DATABASE,
    CURRENT_SCHEMA() AS SCHEMA,
    CURRENT_TIMESTAMP() AS TIMESTAMP;
```

### List Available Roles
```sql
SHOW ROLES;
```

### List Available Warehouses
```sql
SHOW WAREHOUSES;
```

### List Databases
```sql
SHOW DATABASES;
```

---

## 🛠️ Common Tasks

### Switch Role
```sql
USE ROLE DEV_DEVELOPER;
```

### Switch Warehouse
```sql
USE WAREHOUSE DEV_WH;
```

### Switch Database/Schema
```sql
USE DATABASE DEV_REPORTING;
USE SCHEMA SECURITY_ANALYTICS;
```

### Query Table
```sql
SELECT * FROM DEV_REPORTING.SECURITY_ANALYTICS.my_table LIMIT 10;
```

### List Streamlit Apps
```sql
SHOW STREAMLITS IN SCHEMA DEV_REPORTING.SECURITY_ANALYTICS;
```

### Check Stage Contents
```sql
LIST @DEV_REPORTING.SECURITY_ANALYTICS.STREAMLIT_APPS_STAGE;
```

---

## 🚨 Troubleshooting

### Issue: "This session does not have a current database"

**Solution**: Set database context
```sql
USE DATABASE DEV_REPORTING;
USE SCHEMA SECURITY_ANALYTICS;
```

Or in Python:
```python
session.sql("USE DATABASE DEV_REPORTING").collect()
session.sql("USE SCHEMA SECURITY_ANALYTICS").collect()
```

### Issue: Browser doesn't open for SSO

**Solutions**:
1. Check if browser is set as default
2. Try manual URL: Go to Snowflake UI and copy SSO URL
3. Check firewall/proxy settings
4. Contact IT if SSO not working

### Issue: "Role not available"

**Solution**: Check available roles
```sql
SHOW ROLES;
```

Request role access from Snowflake admin if needed.

### Issue: "Warehouse not available"

**Solution**: Check available warehouses
```sql
SHOW WAREHOUSES;
```

Or use different warehouse:
```sql
USE WAREHOUSE QA_WH;  -- Fallback if DEV_WH not available
```

---

## 📝 Configuration File Template

**File**: `snowflake_config.json` (excluded from git)

```json
{
  "user": "fuad.onate@CompanyX.com",
  "authenticator": "externalbrowser",
  "account": "GenericCorp-CRH_EDW",
  "warehouse": "DEV_WH",
  "database": "DEV_REPORTING",
  "schema": "SECURITY_ANALYTICS",
  "role": "DEV_DEVELOPER"
}
```

**IMPORTANT**: This file is in `.gitignore` - never commit to repository!

---

## 🔒 Security Best Practices

1. **ALWAYS use SSO authentication** (`externalbrowser`)
2. **NEVER commit credentials** to git
3. **Use DEV environment** for testing
4. **Use appropriate role** for task (don't use PRD roles unnecessarily)
5. **Close connections** when done
6. **Use least privilege** principle

---

## 📞 Support

**Snowflake Admin Contact**: (Request through IT)
**Azure DevOps**: CompanyX/GIS - SECURITY_ANALYTICS - DW
**Documentation**: See `technical-reference/Snowflake/` for detailed docs

---

**Last Updated**: 2025-10-25
**Maintainer**: Fuad Onate (fuad.onate@CompanyX.com)
**Version**: 1.0
