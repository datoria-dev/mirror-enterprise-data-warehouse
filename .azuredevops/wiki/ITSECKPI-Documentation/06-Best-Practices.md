# SECURITY_ANALYTICS Data Warehouse - Development Best Practices

## Table of Contents
- [Overview](#overview)
- [SQL Development Standards](#sql-development-standards)
- [Python Development Standards](#python-development-standards)
- [Snowflake Optimization](#snowflake-optimization)
- [Streamlit Application Development](#streamlit-application-development)
- [Security Best Practices](#security-best-practices)
- [Testing & Quality Assurance](#testing--quality-assurance)
- [Version Control & Git Workflow](#version-control--git-workflow)
- [Documentation Standards](#documentation-standards)
- [Deployment & Release Management](#deployment--release-management)
- [Troubleshooting & Debugging](#troubleshooting--debugging)
- [Performance Monitoring](#performance-monitoring)

---

## Overview

This document establishes development standards and best practices for the SECURITY_ANALYTICS Data Warehouse project. Following these guidelines ensures code quality, maintainability, security, and performance across all components.

### Core Principles

1. **Consistency**: Use standardized patterns across all code
2. **Clarity**: Write self-documenting code with clear naming
3. **Security**: Always prioritize data protection and access control
4. **Performance**: Optimize for Snowflake's architecture
5. **Maintainability**: Code should be easy to understand and modify
6. **Automation**: Automate repetitive tasks and testing
7. **Documentation**: Keep documentation current and comprehensive

---

## SQL Development Standards

### Naming Conventions

#### Tables
```sql
-- ✅ CORRECT: Clear, descriptive names with service prefix
CREATE TABLE SENTINELONE_AGENTS (...);
CREATE TABLE QUALYS_HOST_DETECTIONS (...);
CREATE TABLE VW_SERVICE_SUMMARY (...);  -- Views prefixed with VW_

-- ❌ INCORRECT: Ambiguous or abbreviated names
CREATE TABLE S1_AGENTS (...);
CREATE TABLE DETECTIONS (...);
```

**Rules**:
- Use `UPPERCASE_WITH_UNDERSCORES` for table names
- Prefix with service name for source tables
- Use `VW_` prefix for views
- Use descriptive, not abbreviated names

#### Columns
```sql
-- ✅ CORRECT: Clear column names
AGENT_ID, COMPUTER_NAME, LAST_ACTIVE_DATE, IS_ACTIVE

-- ❌ INCORRECT: Ambiguous names
ID, NAME, DATE, FLAG
```

**Rules**:
- Use `UPPERCASE_WITH_UNDERSCORES`
- Include data type hint in name (e.g., `*_DATE`, `*_COUNT`, `IS_*`)
- Avoid single-letter names except in very limited scope
- Be specific: `LAST_ACTIVE_DATE` not just `DATE`

#### Variables & Parameters
```sql
-- ✅ CORRECT: Prefixed with data type indicator
DECLARE
    v_log_id NUMBER;
    v_start_time TIMESTAMP_LTZ := CURRENT_TIMESTAMP();
    v_table_count NUMBER := 0;
    v_result VARCHAR;

-- ❌ INCORRECT: No prefix, unclear purpose
DECLARE
    log NUMBER;
    time TIMESTAMP;
```

**Rules**:
- Use `v_` prefix for variables
- Use `p_` prefix for parameters
- Lowercase with underscores for variables
- Descriptive names indicating purpose

### SQL Formatting

#### SELECT Statements
```sql
-- ✅ CORRECT: Well-formatted, readable
SELECT
    a.AGENT_ID,
    a.COMPUTER_NAME,
    a.LAST_ACTIVE_DATE,
    COUNT(t.THREAT_ID) as THREAT_COUNT,
    MAX(t.CREATED_DATE) as LATEST_THREAT_DATE
FROM SENTINELONE_AGENTS a
LEFT JOIN SENTINELONE_THREATS t
    ON a.AGENT_ID = t.AGENT_ID
WHERE a.IS_ACTIVE = TRUE
  AND a.LAST_ACTIVE_DATE >= DATEADD(day, -30, CURRENT_DATE())
GROUP BY
    a.AGENT_ID,
    a.COMPUTER_NAME,
    a.LAST_ACTIVE_DATE
HAVING COUNT(t.THREAT_ID) > 0
ORDER BY THREAT_COUNT DESC
LIMIT 100;

-- ❌ INCORRECT: Unreadable, single line
SELECT a.AGENT_ID, a.COMPUTER_NAME, COUNT(t.THREAT_ID) as THREAT_COUNT FROM SENTINELONE_AGENTS a LEFT JOIN SENTINELONE_THREATS t ON a.AGENT_ID = t.AGENT_ID WHERE a.IS_ACTIVE = TRUE GROUP BY a.AGENT_ID, a.COMPUTER_NAME ORDER BY THREAT_COUNT DESC;
```

**Rules**:
- One column per line in SELECT clause
- Keywords (SELECT, FROM, WHERE, etc.) on separate lines
- Indent JOIN conditions and WHERE clauses
- Align commas at start or end consistently (prefer trailing)
- Use table aliases (single letter or meaningful abbreviations)

#### INSERT Statements
```sql
-- ✅ CORRECT: Explicit column list, readable values
INSERT INTO PROCEDURE_EXECUTION_LOG (
    PROCEDURE_NAME,
    EXECUTION_START,
    STATUS,
    TABLES_PROCESSED,
    COLUMNS_PROCESSED
) VALUES (
    'SP_REFRESH_METADATA',
    CURRENT_TIMESTAMP(),
    'RUNNING',
    0,
    0
);

-- ❌ INCORRECT: No column list, single line
INSERT INTO PROCEDURE_EXECUTION_LOG VALUES ('SP_REFRESH_METADATA', CURRENT_TIMESTAMP(), 'RUNNING', 0, 0);
```

**Rules**:
- Always specify column list
- One value per line for readability (or logical grouping)
- Align VALUES with INSERT columns

#### CTEs (Common Table Expressions)
```sql
-- ✅ CORRECT: Well-structured CTEs
WITH latest_execution AS (
    SELECT
        TABLES_PROCESSED,
        COLUMNS_PROCESSED,
        EXECUTION_DURATION_SECONDS
    FROM PROCEDURE_EXECUTION_LOG
    WHERE STATUS = 'SUCCESS'
    ORDER BY EXECUTION_START DESC
    LIMIT 1
),
aggregate_stats AS (
    SELECT
        AVG(EXECUTION_DURATION_SECONDS) as AVG_DURATION,
        MIN(EXECUTION_DURATION_SECONDS) as MIN_DURATION,
        MAX(EXECUTION_DURATION_SECONDS) as MAX_DURATION
    FROM PROCEDURE_EXECUTION_LOG
    WHERE STATUS = 'SUCCESS'
)
SELECT
    'Average Duration' as METRIC,
    ROUND(AVG_DURATION, 2) as VALUE,
    'seconds' as UNIT
FROM aggregate_stats
UNION ALL
SELECT
    'Tables Per Second',
    ROUND(TABLES_PROCESSED::FLOAT / NULLIF(EXECUTION_DURATION_SECONDS, 0), 2),
    'tables/sec'
FROM latest_execution;
```

**Rules**:
- Use CTEs for complex queries instead of subqueries
- Give CTEs meaningful names
- Add blank line between CTE definitions
- Comment complex CTEs

### Stored Procedures

#### Structure Template
```sql
CREATE OR REPLACE PROCEDURE SP_PROCEDURE_NAME(
    p_parameter1 VARCHAR,
    p_parameter2 NUMBER
)
RETURNS VARCHAR
LANGUAGE SQL
COMMENT = 'Purpose: Brief description of what this procedure does'
AS
$$
DECLARE
    -- Variables
    v_log_id NUMBER;
    v_start_time TIMESTAMP_LTZ := CURRENT_TIMESTAMP();
    v_row_count NUMBER := 0;
    v_result VARCHAR;
BEGIN
    -- Create execution log entry
    INSERT INTO EXECUTION_LOG (PROCEDURE_NAME, START_TIME, STATUS)
    VALUES ('SP_PROCEDURE_NAME', v_start_time, 'RUNNING')
    RETURNING LOG_ID INTO v_log_id;

    -- Main procedure logic
    -- (Well-commented sections)

    -- Update log as success
    UPDATE EXECUTION_LOG
    SET
        END_TIME = CURRENT_TIMESTAMP(),
        STATUS = 'SUCCESS',
        ROWS_PROCESSED = v_row_count
    WHERE LOG_ID = v_log_id;

    v_result := '✅ Success: Processed ' || v_row_count || ' rows';
    RETURN v_result;

EXCEPTION
    WHEN OTHER THEN
        -- Log failure
        UPDATE EXECUTION_LOG
        SET
            END_TIME = CURRENT_TIMESTAMP(),
            STATUS = 'FAILED',
            ERROR_MESSAGE = SQLERRM
        WHERE LOG_ID = v_log_id;

        RETURN '❌ Failed: ' || SQLERRM;
END;
$$;
```

**Rules**:
- Always include COMMENT describing purpose
- Declare all variables at the top
- Initialize variables when declaring when possible
- Always include exception handling
- Log execution (start, end, status, errors)
- Return meaningful success/failure messages

#### Error Handling
```sql
-- ✅ CORRECT: Comprehensive error handling
BEGIN
    -- Business logic
    INSERT INTO TABLE_REGISTRY (...) VALUES (...);

    v_result := 'Success: ' || SQLROWCOUNT || ' records inserted';
    RETURN v_result;

EXCEPTION
    WHEN STATEMENT_ERROR THEN
        v_error := 'SQL Error: ' || SQLERRM || ' at ' || $$;
        INSERT INTO ERROR_LOG (PROCEDURE_NAME, ERROR_MESSAGE, ERROR_TIME)
        VALUES ('SP_PROCEDURE_NAME', v_error, CURRENT_TIMESTAMP());
        RETURN '❌ ' || v_error;

    WHEN OTHER THEN
        v_error := 'Unexpected Error: ' || SQLERRM;
        INSERT INTO ERROR_LOG (PROCEDURE_NAME, ERROR_MESSAGE, ERROR_TIME)
        VALUES ('SP_PROCEDURE_NAME', v_error, CURRENT_TIMESTAMP());
        RETURN '❌ ' || v_error;
END;
```

### Comments & Documentation

```sql
-- ========================================
-- SECTION: Major section header
-- ========================================

-- Purpose: Single-line comment for simple explanations
SELECT * FROM TABLE;

/*
 * Multi-line comment for complex logic:
 * - Explanation of approach
 * - Why certain decisions were made
 * - Dependencies or prerequisites
 * - Expected behavior
 */
CREATE TABLE COMPLEX_TABLE (...);
```

**Rules**:
- Use section headers for major blocks
- Comment WHY, not WHAT (code should be self-explanatory)
- Document complex business logic
- Explain non-obvious performance optimizations

---

## Python Development Standards

### Code Style (PEP 8)

```python
# ✅ CORRECT: PEP 8 compliant
import sys
import json
from datetime import datetime

import snowflake.connector
import pandas as pd


def connect_to_snowflake(config_file='snowflake_config.json'):
    """
    Establish connection to Snowflake using SSO authentication.

    Args:
        config_file (str): Path to Snowflake configuration JSON file

    Returns:
        snowflake.connector.SnowflakeConnection: Active database connection

    Raises:
        FileNotFoundError: If config file doesn't exist
        ConnectionError: If unable to connect to Snowflake
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        conn = snowflake.connector.connect(**config)
        print(f"✅ Connected to Snowflake as {config['user']}")
        return conn

    except FileNotFoundError:
        print(f"❌ Config file not found: {config_file}")
        raise
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        raise ConnectionError(f"Failed to connect to Snowflake: {str(e)}")


def execute_query(conn, sql, description="Query"):
    """
    Execute SQL query and return results as DataFrame.

    Args:
        conn: Snowflake connection object
        sql (str): SQL query to execute
        description (str): Description for logging

    Returns:
        pd.DataFrame: Query results
    """
    print(f"🔄 {description}...")

    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        df = pd.DataFrame(results, columns=columns)
        print(f"✅ {description} completed: {len(df)} rows")
        return df

    except Exception as e:
        print(f"❌ {description} failed: {str(e)}")
        raise


# ❌ INCORRECT: Poor style
def connecttosnowflake(configfile):
    f=open(configfile)
    config=json.load(f)
    conn=snowflake.connector.connect(**config)
    return conn
```

**Rules**:
- Follow PEP 8 style guide
- Use 4 spaces for indentation (not tabs)
- Max line length: 100 characters (flexible for readability)
- Use snake_case for functions and variables
- Use PascalCase for classes
- Add docstrings to all functions
- Use type hints where beneficial

### Project Structure

```
project_root/
├── 01_SQL_SCRIPTS/
│   ├── DDL/
│   ├── PROCEDURES/
│   └── VIEWS/
├── 02_PYTHON_SCRIPTS/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── snowflake_utils.py     # Reusable Snowflake utilities
│   ├── extract_metadata.py    # Specific scripts
│   └── requirements.txt       # Dependencies
├── 07_STREAMLIT_APPS/
│   └── ServiceName/
│       ├── streamlit_app.py
│       ├── requirements.txt
│       └── README.md
├── snowflake_config.json      # Connection configuration
├── .gitignore
└── README.md
```

### Configuration Management

```python
# ✅ CORRECT: Configuration from JSON file
import json

def load_config(config_file='snowflake_config.json'):
    """Load Snowflake configuration from JSON file."""
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()
conn = snowflake.connector.connect(**config)

# ❌ INCORRECT: Hardcoded credentials
conn = snowflake.connector.connect(
    user='hardcoded.user@example.com',
    password='hardcodedpassword',  # NEVER do this!
    account='ACCOUNT-NAME'
)
```

**Rules**:
- Never hardcode credentials
- Use configuration files (excluded from Git via .gitignore)
- Use environment variables for sensitive data in production
- Validate configuration before use

### Error Handling & Logging

```python
# ✅ CORRECT: Comprehensive error handling
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/execution_{datetime.now():%Y%m%d}.log'),
        logging.StreamHandler()
    ]
)

def process_data(input_file):
    """Process data with comprehensive error handling."""
    try:
        logging.info(f"Processing file: {input_file}")

        # Business logic
        df = pd.read_csv(input_file)
        logging.info(f"Loaded {len(df)} rows")

        # More processing...

        logging.info("✅ Processing completed successfully")
        return df

    except FileNotFoundError:
        logging.error(f"❌ File not found: {input_file}")
        raise

    except pd.errors.EmptyDataError:
        logging.error(f"❌ File is empty: {input_file}")
        raise

    except Exception as e:
        logging.error(f"❌ Unexpected error: {str(e)}", exc_info=True)
        raise

# ❌ INCORRECT: Bare except, no logging
def process_data(input_file):
    try:
        df = pd.read_csv(input_file)
        return df
    except:
        print("Error")
        return None
```

### Windows Console Encoding

```python
# ✅ CORRECT: Handle Windows console encoding for emojis/unicode
import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer,
        encoding='utf-8',
        errors='replace'
    )

print("✅ Success - emoji displays correctly!")
```

**Apply to all Python scripts** that may run on Windows and use unicode/emoji characters.

### Export Results Pattern

```python
# ✅ CORRECT: Standard export pattern
def export_results(df, output_dir, base_filename, description="Results"):
    """
    Export DataFrame to both CSV and JSON formats.

    Args:
        df (pd.DataFrame): Data to export
        output_dir (str): Output directory path
        base_filename (str): Base filename (without extension)
        description (str): Description for logging
    """
    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, f"{base_filename}.csv")
    json_path = os.path.join(output_dir, f"{base_filename}.json")

    # Export CSV
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"📄 {description} exported to CSV: {csv_path}")

    # Export JSON
    df.to_json(json_path, orient='records', indent=2, date_format='iso')
    print(f"📄 {description} exported to JSON: {json_path}")

    return csv_path, json_path
```

---

## Snowflake Optimization

### Query Performance

#### Use Clustering Keys for Large Tables
```sql
-- For large, frequently filtered tables
ALTER TABLE QUALYS_HOST_DETECTIONS
    CLUSTER BY (LAST_FOUND_DATETIME, HOST_ID);

-- Benefits:
-- - Faster queries filtering by LAST_FOUND_DATETIME
-- - Automatic micro-partition organization
-- - Reduced data scanning
```

#### Avoid SELECT *
```sql
-- ✅ CORRECT: Select only needed columns
SELECT
    AGENT_ID,
    COMPUTER_NAME,
    LAST_ACTIVE_DATE
FROM SENTINELONE_AGENTS
WHERE IS_ACTIVE = TRUE;

-- ❌ INCORRECT: Unnecessary data transfer
SELECT * FROM SENTINELONE_AGENTS
WHERE IS_ACTIVE = TRUE;
```

#### Use LIMIT for Exploratory Queries
```sql
-- ✅ CORRECT: Limit results during development
SELECT * FROM LARGE_TABLE
LIMIT 100;

-- ❌ INCORRECT: Full table scan during testing
SELECT * FROM LARGE_TABLE;  -- Could return millions of rows!
```

#### Filter Early in CTEs
```sql
-- ✅ CORRECT: Filter in CTE definition
WITH recent_threats AS (
    SELECT *
    FROM SENTINELONE_THREATS
    WHERE CREATED_DATE >= DATEADD(day, -7, CURRENT_DATE())  -- Filter early
)
SELECT COUNT(*) FROM recent_threats;

-- ❌ INCORRECT: Filter after CTE
WITH all_threats AS (
    SELECT * FROM SENTINELONE_THREATS  -- Loads entire table
)
SELECT COUNT(*)
FROM all_threats
WHERE CREATED_DATE >= DATEADD(day, -7, CURRENT_DATE());  -- Late filter
```

### Table Design

#### Use Appropriate Data Types
```sql
-- ✅ CORRECT: Appropriate data types
CREATE TABLE EXAMPLE (
    AGENT_ID VARCHAR(100),              -- Not VARCHAR(16777216)
    THREAT_COUNT NUMBER(10,0),          -- Not NUMBER(38,0)
    IS_ACTIVE BOOLEAN,                  -- Not VARCHAR
    LAST_ACTIVE_DATE TIMESTAMP_LTZ      -- With timezone
);

-- ❌ INCORRECT: Oversized or wrong types
CREATE TABLE EXAMPLE (
    AGENT_ID VARCHAR(16777216),         -- Way too large
    THREAT_COUNT VARCHAR(50),           -- Should be NUMBER
    IS_ACTIVE VARCHAR(5),               -- Should be BOOLEAN
    LAST_ACTIVE_DATE VARCHAR(100)       -- Should be TIMESTAMP
);
```

#### Use Appropriate Constraints
```sql
-- ✅ CORRECT: Use constraints
CREATE TABLE TABLE_REGISTRY (
    TABLE_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    SERVICE_NAME VARCHAR(100) NOT NULL,
    TABLE_NAME VARCHAR(255) NOT NULL,
    CREATED_DATE TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP() NOT NULL,
    CONSTRAINT UK_SERVICE_TABLE UNIQUE (SERVICE_NAME, TABLE_NAME)
);
```

### Warehouse Sizing

**General Guidelines**:
- **X-Small**: Development, testing, small queries (<1M rows)
- **Small**: Regular analytics, metadata queries (1-10M rows)
- **Medium**: Large aggregations, complex joins (10-100M rows)
- **Large**: Heavy ETL, full data scans (100M+ rows)

**Auto-Suspend & Auto-Resume**:
```sql
-- Configure warehouse for cost optimization
ALTER WAREHOUSE DEV_WH SET
    AUTO_SUSPEND = 300,      -- Suspend after 5 minutes of inactivity
    AUTO_RESUME = TRUE;      -- Resume automatically when queries submitted
```

---

## Streamlit Application Development

### Application Template Structure

```python
"""
Streamlit App Template for SECURITY_ANALYTICS Services

Standard structure for all security service dashboards.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Import common utilities
from snowflake_utils import get_snowflake_connection, safe_query


# ========================================
# PAGE CONFIGURATION
# ========================================

st.set_page_config(
    page_title="ServiceName Dashboard",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ========================================
# SESSION STATE INITIALIZATION
# ========================================

if 'connection' not in st.session_state:
    st.session_state.connection = None


# ========================================
# HELPER FUNCTIONS
# ========================================

@st.cache_data(ttl=600)  # Cache for 10 minutes
def load_data(sql_query, description="data"):
    """Load data from Snowflake with caching."""
    try:
        return safe_query(st.session_state.connection, sql_query, description)
    except Exception as e:
        st.error(f"❌ Failed to load {description}: {str(e)}")
        return pd.DataFrame()


def create_metric_card(label, value, delta=None, delta_color="normal"):
    """Create consistent metric cards."""
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)


# ========================================
# SIDEBAR FILTERS
# ========================================

with st.sidebar:
    st.title("🔒 ServiceName")
    st.markdown("---")

    # Date range filter
    date_range = st.date_input(
        "Date Range",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        max_value=datetime.now()
    )

    # Additional filters...


# ========================================
# MAIN CONTENT
# ========================================

st.title("📊 ServiceName Security Dashboard")

# Tab layout
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "🔍 Detailed Analysis",
    "📈 Trends",
    "📚 Metadata"
])

# TAB 1: OVERVIEW
with tab1:
    st.subheader("Key Metrics")

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        create_metric_card("Total Items", "1,234")
    # More metrics...

# TAB 2-4: Additional tabs...

# ========================================
# FOOTER
# ========================================

st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data refresh: Daily at 2:00 AM EST")
```

### Caching Strategy

```python
# ✅ CORRECT: Cache expensive operations
@st.cache_data(ttl=600)  # 10-minute cache
def load_summary_data():
    """Load summary data (changes infrequently)."""
    sql = "SELECT * FROM SUMMARY_TABLE"
    return safe_query(conn, sql)

@st.cache_data(ttl=60)  # 1-minute cache
def load_realtime_data():
    """Load near-realtime data (changes frequently)."""
    sql = "SELECT * FROM REALTIME_TABLE WHERE DATE = CURRENT_DATE()"
    return safe_query(conn, sql)

# Don't cache user-specific or filtered data
def load_filtered_data(filter_value):
    """Load data based on user filters - no caching."""
    sql = f"SELECT * FROM TABLE WHERE COLUMN = '{filter_value}'"
    return safe_query(conn, sql)
```

### Error Handling in Streamlit

```python
# ✅ CORRECT: User-friendly error messages
try:
    data = load_data(sql_query)
    if data.empty:
        st.warning("⚠️ No data found for the selected filters. Try adjusting your criteria.")
    else:
        st.dataframe(data)
except Exception as e:
    st.error(f"❌ An error occurred while loading data. Please contact support if this persists.")
    with st.expander("Technical Details"):
        st.code(str(e))
```

---

## Security Best Practices

### Authentication

```python
# ✅ CORRECT: SSO authentication
config = {
    "user": "user.email@CompanyX.com",
    "authenticator": "externalbrowser",  # Okta SSO
    "account": "GenericCorp-CRH_EDW",
    "warehouse": "DEV_WH",
    "role": "DEV_DEVELOPER"
}

# ❌ INCORRECT: Password authentication
config = {
    "user": "username",
    "password": "plaintext_password",  # NEVER DO THIS
    "account": "account"
}
```

### Sensitive Data Handling

```sql
-- ✅ CORRECT: Dynamic data masking
CREATE OR REPLACE VIEW VW_USERS_MASKED AS
SELECT
    USER_ID,
    USER_NAME,
    CASE
        WHEN CURRENT_ROLE() IN ('ADMIN', 'DEVELOPER')
        THEN EMAIL_ADDRESS
        ELSE '***MASKED***'
    END as EMAIL_ADDRESS,
    CASE
        WHEN CURRENT_ROLE() IN ('ADMIN', 'DEVELOPER')
        THEN PHONE_NUMBER
        ELSE '***MASKED***'
    END as PHONE_NUMBER
FROM USERS;
```

### Access Control

```sql
-- ✅ CORRECT: Role-based grants
GRANT SELECT ON TABLE SENTINELONE_AGENTS TO ROLE DEV_READER;
GRANT SELECT, INSERT, UPDATE ON TABLE SENTINELONE_AGENTS TO ROLE DEV_WRITER;
GRANT ALL ON TABLE SENTINELONE_AGENTS TO ROLE DEV_DEVELOPER;

-- Document access changes
INSERT INTO ACCESS_AUDIT_LOG (GRANTED_TO, OBJECT_NAME, PRIVILEGE, GRANTED_BY, GRANT_DATE)
VALUES ('DEV_READER', 'SENTINELONE_AGENTS', 'SELECT', CURRENT_USER(), CURRENT_TIMESTAMP());
```

### Git Security

```bash
# .gitignore - ALWAYS exclude sensitive files
snowflake_config.json
*.env
.env
credentials/
secrets/
*.key
*.pem
__pycache__/
*.pyc
.DS_Store
```

---

## Testing & Quality Assurance

### SQL Testing

```sql
-- Test 1: Row count validation
SELECT
    'Row Count Check' as TEST_NAME,
    COUNT(*) as ACTUAL_COUNT,
    CASE
        WHEN COUNT(*) > 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as RESULT
FROM SENTINELONE_AGENTS;

-- Test 2: Data quality check
SELECT
    'Null Check - Required Fields' as TEST_NAME,
    COUNT(*) as NULL_COUNT,
    CASE
        WHEN COUNT(*) = 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as RESULT
FROM SENTINELONE_AGENTS
WHERE AGENT_ID IS NULL
   OR COMPUTER_NAME IS NULL
   OR LAST_ACTIVE_DATE IS NULL;

-- Test 3: Data freshness check
SELECT
    'Data Freshness Check' as TEST_NAME,
    MAX(LAST_ACTIVE_DATE) as LATEST_DATE,
    DATEDIFF(hour, MAX(LAST_ACTIVE_DATE), CURRENT_TIMESTAMP()) as HOURS_OLD,
    CASE
        WHEN DATEDIFF(hour, MAX(LAST_ACTIVE_DATE), CURRENT_TIMESTAMP()) < 30 THEN '✅ PASS'
        ELSE '❌ FAIL - Data is stale'
    END as RESULT
FROM SENTINELONE_AGENTS;
```

### Python Testing

```python
# test_snowflake_utils.py
import pytest
from snowflake_utils import connect_to_snowflake, execute_query

def test_connection():
    """Test Snowflake connection."""
    conn = connect_to_snowflake('snowflake_config.json')
    assert conn is not None
    assert conn.is_closed() == False
    conn.close()

def test_query_execution():
    """Test query execution returns DataFrame."""
    conn = connect_to_snowflake('snowflake_config.json')
    df = execute_query(conn, "SELECT 1 as TEST_COLUMN")
    assert len(df) == 1
    assert 'TEST_COLUMN' in df.columns
    conn.close()

def test_invalid_query():
    """Test error handling for invalid queries."""
    conn = connect_to_snowflake('snowflake_config.json')
    with pytest.raises(Exception):
        execute_query(conn, "SELECT * FROM NONEXISTENT_TABLE")
    conn.close()
```

### Verification Scripts

Create comprehensive verification scripts for major components:

```sql
-- VERIFY_COMPONENT.sql
-- ========================================
-- CHECK 1: Component exists
-- ========================================
SELECT 'Component Exists' as CHECK_NAME,
       COUNT(*) as RESULT,
       CASE WHEN COUNT(*) > 0 THEN '✅ PASS' ELSE '❌ FAIL' END as STATUS
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME = 'COMPONENT_NAME';

-- ========================================
-- CHECK 2: Data quality
-- ========================================
-- Additional checks...
```

---

## Version Control & Git Workflow

### Branch Strategy

```
main (production-ready code)
  ├── develop (integration branch)
  │     ├── feature/metadata-export
  │     ├── feature/new-service-integration
  │     └── feature/streamlit-enhancement
  └── hotfix/critical-bug-fix
```

### Commit Message Format

```bash
# ✅ CORRECT: Descriptive, follows convention
git commit -m "feat: add metadata export functionality for CybelAngel service

- Create CYBELANGEL_COLUMNS_EXPORT table
- Add export query to EXPORT_METADATA_RESULTS.sql
- Update metadata tab in CybelAngel Streamlit app

Resolves #123"

# ❌ INCORRECT: Vague, no context
git commit -m "updates"
git commit -m "fix"
```

**Format**: `<type>: <subject>`

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests passed
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No sensitive data in code
- [ ] All tests pass
```

---

## Documentation Standards

### README Files

Every project/directory should have a README.md:

```markdown
# Component Name

## Overview
Brief description of what this component does

## Prerequisites
- Python 3.9+
- Snowflake account with DEV_DEVELOPER role
- Required packages (see requirements.txt)

## Installation
```bash
pip install -r requirements.txt
```

## Configuration
Create `snowflake_config.json`:
```json
{
  "user": "your.email@CompanyX.com",
  "account": "GenericCorp-CRH_EDW",
  ...
}
```

## Usage
```bash
python script_name.py --argument value
```

## Examples
[Provide common use cases]

## Troubleshooting
[Common issues and solutions]

## Contributing
[How to contribute]

## License
[License information]
```

### Inline Documentation

```sql
-- ========================================
-- TABLE: SENTINELONE_AGENTS
-- Purpose: Store SentinelOne endpoint agent inventory
-- Refresh: Daily at 2:00 AM EST
-- Retention: 90 days in Landing, 2 years in Transformation
-- Owner: Security Operations Team
-- ========================================
CREATE TABLE SENTINELONE_AGENTS (
    AGENT_ID VARCHAR(100) NOT NULL COMMENT 'Unique agent identifier from SentinelOne API',
    COMPUTER_NAME VARCHAR(255) COMMENT 'Endpoint hostname',
    LAST_ACTIVE_DATE TIMESTAMP_LTZ COMMENT 'Last communication timestamp',
    ...
);
```

---

## Deployment & Release Management

### Pre-Deployment Checklist

- [ ] All tests pass
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] No hardcoded credentials
- [ ] Performance tested
- [ ] Rollback plan documented
- [ ] Stakeholders notified

### Deployment Steps

1. **Backup Current State**
```sql
-- Backup table before changes
CREATE TABLE SENTINELONE_AGENTS_BACKUP CLONE SENTINELONE_AGENTS;
```

2. **Deploy in Non-Production First**
```sql
-- Test in DEV environment
USE DATABASE DEV_TRANSFORMATION;
-- Execute changes
```

3. **Verify Deployment**
```bash
python verify_deployment.py
```

4. **Monitor Post-Deployment**
- Check logs for errors
- Verify data quality
- Monitor performance metrics

5. **Document Deployment**
```sql
INSERT INTO DEPLOYMENT_LOG (COMPONENT, VERSION, DEPLOYED_BY, DEPLOY_DATE, STATUS)
VALUES ('METADATA_REPOSITORY', 'v3.0', CURRENT_USER(), CURRENT_TIMESTAMP(), 'SUCCESS');
```

---

## Troubleshooting & Debugging

### Common Issues

#### Issue: Slow Query Performance
```sql
-- Diagnosis: Check query profile
SELECT *
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE QUERY_ID = 'your-query-id';

-- Solutions:
-- 1. Add clustering key
ALTER TABLE LARGE_TABLE CLUSTER BY (DATE_COLUMN);

-- 2. Use result caching
-- Re-run identical query within 24 hours

-- 3. Filter earlier in query
WITH filtered AS (
    SELECT * FROM LARGE_TABLE
    WHERE DATE_COLUMN >= DATEADD(day, -7, CURRENT_DATE())
)
SELECT * FROM filtered;
```

#### Issue: Python Unicode Errors on Windows
```python
# Solution: Add encoding fix at start of script
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
```

#### Issue: Streamlit Connection Timeout
```python
# Solution: Add connection retry logic
import time

def get_connection_with_retry(max_retries=3):
    for attempt in range(max_retries):
        try:
            conn = snowflake.connector.connect(**config)
            return conn
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Connection failed, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
```

### Debugging Tools

**Snowflake**:
- Query Profile: Analyze query performance
- Query History: Review past executions
- EXPLAIN: View query execution plan

```sql
EXPLAIN SELECT * FROM LARGE_TABLE WHERE DATE_COLUMN >= CURRENT_DATE();
```

**Python**:
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use pdb for interactive debugging
import pdb; pdb.set_trace()
```

---

## Performance Monitoring

### Key Metrics to Monitor

#### Snowflake Warehouse Usage
```sql
SELECT
    WAREHOUSE_NAME,
    AVG(AVG_RUNNING) as AVG_QUERIES_RUNNING,
    SUM(CREDITS_USED) as TOTAL_CREDITS,
    AVG(AVG_QUEUED_LOAD) as AVG_QUEUE_DEPTH
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_LOAD_HISTORY
WHERE START_TIME >= DATEADD(day, -7, CURRENT_DATE())
GROUP BY WAREHOUSE_NAME;
```

#### Query Performance Trends
```sql
SELECT
    DATE(START_TIME) as DATE,
    COUNT(*) as QUERY_COUNT,
    AVG(EXECUTION_TIME) / 1000 as AVG_EXECUTION_SECONDS,
    MAX(EXECUTION_TIME) / 1000 as MAX_EXECUTION_SECONDS
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE START_TIME >= DATEADD(day, -30, CURRENT_DATE())
GROUP BY DATE(START_TIME)
ORDER BY DATE DESC;
```

#### Metadata Refresh Performance
```sql
SELECT
    EXECUTION_DATE,
    EXECUTION_DURATION_SECONDS,
    TABLES_PROCESSED,
    COLUMNS_PROCESSED,
    ROUND(TABLES_PROCESSED::FLOAT / EXECUTION_DURATION_SECONDS, 2) as TABLES_PER_SECOND
FROM PROCEDURE_EXECUTION_LOG
WHERE PROCEDURE_NAME = 'SP_REFRESH_METADATA'
  AND STATUS = 'SUCCESS'
ORDER BY EXECUTION_DATE DESC
LIMIT 30;
```

### Alerts & Notifications

Set up monitoring for:
- Failed scheduled tasks
- Queries exceeding performance thresholds
- Data quality issues
- Warehouse credit consumption spikes
- Storage growth anomalies

---

## Appendix

### Related Documentation

- [WIKI_01_STREAMLIT_APPS.md](WIKI_01_STREAMLIT_APPS.md) - Streamlit applications
- [WIKI_02_POWER_BI.md](WIKI_02_POWER_BI.md) - Power BI roadmap
- [WIKI_03_METADATA_EXTRACTION.md](WIKI_03_METADATA_EXTRACTION.md) - Metadata automation
- [WIKI_04_DATA_GOVERNANCE.md](WIKI_04_DATA_GOVERNANCE.md) - Governance framework
- [WIKI_05_DATA_DICTIONARY.md](WIKI_05_DATA_DICTIONARY.md) - Data dictionary

### External Resources

- [Snowflake Best Practices](https://docs.snowflake.com/en/user-guide/best-practices.html)
- [Python PEP 8 Style Guide](https://pep8.org/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Git Best Practices](https://git-scm.com/book/en/v2)

### Code Review Checklist

Use this checklist when reviewing pull requests:

#### Functionality
- [ ] Code accomplishes stated objective
- [ ] Edge cases handled
- [ ] Error handling implemented
- [ ] Tests included and passing

#### Code Quality
- [ ] Follows naming conventions
- [ ] Comments added where needed
- [ ] No code duplication
- [ ] Efficient algorithms used

#### Security
- [ ] No hardcoded credentials
- [ ] Proper access controls
- [ ] Input validation implemented
- [ ] Sensitive data masked

#### Documentation
- [ ] README updated
- [ ] Inline comments adequate
- [ ] API documentation current
- [ ] Examples provided

#### Performance
- [ ] Queries optimized
- [ ] Appropriate caching used
- [ ] Large datasets handled efficiently
- [ ] No unnecessary computations

---

**Document Status**: Production Release v1.0
**Last Updated**: 2025-10-24
**Author**: GenericCorp Data Engineering Team
**Maintained By**: Development Team Lead
