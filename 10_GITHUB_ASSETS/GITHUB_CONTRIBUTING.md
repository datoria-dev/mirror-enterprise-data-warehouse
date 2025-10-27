# Contributing to IT Security KPI Data Warehouse

Thank you for your interest in contributing to the SECURITY_ANALYTICS Data Warehouse project! This document provides guidelines and best practices for contributing to the project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

---

## Code of Conduct

### Our Commitment
We are committed to providing a welcoming and inclusive environment for all contributors. We expect everyone to:

- Be respectful and professional
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior
- Harassment, discrimination, or offensive comments
- Personal attacks or trolling
- Publishing others' private information
- Any conduct that would be inappropriate in a professional setting

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:

1. **Snowflake Account**: Access to a Snowflake instance for testing
2. **Python 3.13+**: Latest Python version installed
3. **Git**: Version control system
4. **Code Editor**: VSCode, PyCharm, or similar
5. **SnowSQL** (optional): Command-line client for Snowflake

### Setting Up Your Development Environment

1. **Fork the repository**
```bash
# Navigate to GitHub and fork the repository
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/snowflake-SECURITY_ANALYTICS-project.git
cd snowflake-SECURITY_ANALYTICS-project
```

2. **Create a virtual environment**
```bash
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

4. **Configure Snowflake connection**
```bash
cp .env.example .env
# Edit .env with your Snowflake credentials
```

5. **Verify setup**
```bash
python 02_PYTHON_SCRIPTS/test_connection.py
```

---

## Development Workflow

### Branching Strategy

We follow the **Git Flow** branching model:

- **`main`**: Production-ready code
- **`develop`**: Integration branch for features
- **`feature/*`**: New features or enhancements
- **`bugfix/*`**: Bug fixes
- **`hotfix/*`**: Urgent production fixes
- **`release/*`**: Release preparation

### Creating a Feature Branch

```bash
# Update your local develop branch
git checkout develop
git pull origin develop

# Create a new feature branch
git checkout -b feature/your-feature-name

# Example:
git checkout -b feature/add-tenable-integration
```

### Making Changes

1. **Write Clean Code**: Follow coding standards (see below)
2. **Test Thoroughly**: Run all tests before committing
3. **Document Changes**: Update documentation as needed
4. **Commit Regularly**: Use clear, descriptive commit messages

### Commit Message Guidelines

Follow the **Conventional Commits** specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```bash
feat(crowdstrike): add EDR coverage monitoring dashboard

- Added VW_CROWDSTRIKE_COVERAGE view
- Implemented Streamlit dashboard with KPI metrics
- Added automated freshness checks

Closes #123

---

fix(qualys): resolve vulnerability count discrepancy

Fixed SQL query in SP_RECONCILE_QUALYS to correctly
handle deduplicated vulnerability records.

Fixes #456
```

---

## Coding Standards

### SQL Standards

#### Naming Conventions
```sql
-- Tables: Uppercase with underscores
DIM_HOST, FACT_QUALYS, STG_CROWDSTRIKE_ENDPOINTS

-- Views: VW_ prefix
VW_MASTER_CONTROL_PANEL, VW_DATA_QUALITY_MONITORING

-- Stored Procedures: SP_ prefix
SP_LOAD_DIM_HOST_INCREMENTAL, SP_RECONCILE_ALL_SOURCES

-- Functions: FN_ prefix (scalar), TVF_ prefix (table-valued)
FN_GET_SEVERITY_LEVEL, TVF_GET_KPI_TREND

-- Tasks: TASK_ prefix
TASK_LOAD_DIM_HOST, TASK_CALCULATE_KPIS
```

#### Formatting
```sql
-- Use uppercase for SQL keywords
-- Use consistent indentation (4 spaces)
-- Add comments for complex logic

CREATE OR REPLACE TABLE DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST (
    HOST_ID NUMBER PRIMARY KEY,
    HOSTNAME VARCHAR(255) NOT NULL,
    IP_ADDRESS VARCHAR(50),
    OPERATING_SYSTEM VARCHAR(100),
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Index frequently queried columns
CREATE INDEX IDX_HOST_HOSTNAME ON DIM_HOST(HOSTNAME);
```

#### Best Practices
- Use `RELY` constraints for query optimization
- Implement proper error handling in stored procedures
- Use transactions for multi-step operations
- Add meaningful comments for complex queries
- Avoid `SELECT *` in production code
- Use parameterized queries to prevent SQL injection

### Python Standards

#### Style Guide: PEP 8

```python
# Use snake_case for functions and variables
def load_dimension_table(table_name: str, incremental: bool = True):
    """
    Load dimension table from landing to transformation layer.

    Args:
        table_name: Name of the dimension table
        incremental: Whether to perform incremental load

    Returns:
        Number of rows loaded

    Raises:
        snowflake.connector.errors.ProgrammingError: If SQL fails
    """
    pass

# Use type hints
def calculate_quality_score(
    table_name: str,
    check_nulls: bool = True
) -> float:
    pass

# Constants in UPPERCASE
DATABASE_NAME = "DEV_TRANSFORMATION"
SCHEMA_NAME = "SECURITY_ANALYTICS"
MAX_RETRIES = 3
```

#### Code Organization
```python
# Standard library imports
import os
import sys
from datetime import datetime, timedelta

# Third-party imports
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv

# Local imports
from utils.snowflake_helpers import get_connection
from config import DATABASES, SCHEMA_NAME
```

#### Error Handling
```python
import logging

logger = logging.getLogger(__name__)

def execute_query(sql: str) -> pd.DataFrame:
    """Execute SQL query with proper error handling."""
    try:
        conn = get_connection()
        df = pd.read_sql(sql, conn)
        logger.info(f"Query executed successfully: {len(df)} rows returned")
        return df

    except snowflake.connector.errors.ProgrammingError as e:
        logger.error(f"SQL execution failed: {e}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

    finally:
        if conn:
            conn.close()
```

#### Documentation
- Use docstrings for all functions and classes
- Follow Google or NumPy docstring format
- Include examples in docstrings for complex functions

### Streamlit Standards

```python
import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

# Page configuration at top
st.set_page_config(
    page_title="Service Name Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# Use caching for database queries
@st.cache_data(ttl=300)
def load_coverage_data(days_back: int) -> pd.DataFrame:
    """Load coverage metrics with caching."""
    session = get_active_session()
    sql = f"""
        SELECT * FROM VW_COVERAGE
        WHERE REPORT_DATE >= DATEADD(day, -{days_back}, CURRENT_DATE())
    """
    return session.sql(sql).to_pandas()

# Consistent layout structure
st.title("Dashboard Title")
st.markdown("Description")

# Sidebar for filters
with st.sidebar:
    st.header("Filters")
    date_range = st.selectbox("Time Period", ["Last 7 Days", "Last 30 Days"])

# Tabs for organization
tab1, tab2, tab3 = st.tabs(["Overview", "Details", "Quality"])

with tab1:
    # Metrics in columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total", "1,234", "+5%")
```

---

## Testing Guidelines

### SQL Testing

#### Unit Tests
```sql
-- Test stored procedure
CALL DEV_TRANSFORMATION.SECURITY_ANALYTICS.SP_LOAD_DIM_HOST_INCREMENTAL();

-- Verify results
SELECT COUNT(*) as ROW_COUNT,
       MAX(UPDATED_AT) as LAST_UPDATE
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST;
```

#### Integration Tests
```sql
-- Test complete ETL pipeline
EXECUTE TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_LOAD_DIM_HOST;

-- Wait for task completion
SELECT *
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    TASK_NAME => 'TASK_LOAD_DIM_HOST',
    SCHEDULED_TIME_RANGE_START => DATEADD('hour', -1, CURRENT_TIMESTAMP())
));
```

### Python Testing

Use **pytest** for Python tests:

```python
# tests/test_snowflake_connection.py
import pytest
from utils.snowflake_helpers import get_connection

def test_connection():
    """Test Snowflake connection."""
    conn = get_connection()
    assert conn is not None
    assert conn.is_closed() == False
    conn.close()

def test_query_execution():
    """Test query execution."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT CURRENT_VERSION()")
    result = cursor.fetchone()
    assert result is not None
    cursor.close()
    conn.close()
```

Run tests:
```bash
pytest tests/ -v
pytest tests/test_snowflake_connection.py::test_connection
```

### Data Quality Tests

```sql
-- Test constraint enforcement
CREATE OR REPLACE PROCEDURE TEST_DATA_QUALITY()
RETURNS STRING
LANGUAGE SQL
AS
$$
BEGIN
    -- Test 1: Primary key uniqueness
    LET duplicate_count := (
        SELECT COUNT(*) - COUNT(DISTINCT HOST_ID)
        FROM DIM_HOST
    );

    IF (duplicate_count > 0) THEN
        RETURN 'FAIL: Duplicate primary keys found';
    END IF;

    -- Test 2: Foreign key validity
    LET invalid_fk_count := (
        SELECT COUNT(*)
        FROM FACT_QUALYS f
        LEFT JOIN DIM_HOST d ON f.HOST_ID = d.HOST_ID
        WHERE d.HOST_ID IS NULL
    );

    IF (invalid_fk_count > 0) THEN
        RETURN 'FAIL: Invalid foreign keys found';
    END IF;

    RETURN 'PASS: All data quality tests passed';
END;
$$;
```

---

## Documentation

### Code Documentation

- **SQL Scripts**: Add header comments explaining purpose, author, dependencies
- **Python Modules**: Use docstrings with type hints
- **Configuration**: Document all environment variables and settings

### Documentation Updates

When adding new features, update:

1. **README.md**: If it affects setup or usage
2. **FINAL_DELIVERABLES/01_Reports/**: Technical documentation
3. **Inline Comments**: For complex logic
4. **Data Dictionary**: If adding/modifying tables
5. **ERD Diagrams**: If changing data model

### Documentation Format

Use **Markdown** for all documentation:

```markdown
# Feature: CrowdStrike Integration

## Overview
Brief description of the feature

## Architecture
Technical details and design decisions

## Usage
```sql
-- Example SQL query
SELECT * FROM VW_CROWDSTRIKE_COVERAGE;
```

## Dependencies
- DIM_HOST table
- SP_RECONCILE_CROWDSTRIKE procedure
```

---

## Pull Request Process

### Before Submitting

1. **Update from develop**
```bash
git checkout develop
git pull origin develop
git checkout feature/your-feature
git merge develop
```

2. **Run all tests**
```bash
pytest tests/
```

3. **Update documentation**

4. **Commit and push**
```bash
git add .
git commit -m "feat(scope): description"
git push origin feature/your-feature
```

### Submitting a Pull Request

1. **Go to GitHub** and create a Pull Request
2. **Fill in the PR template**:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## Testing Performed
- [ ] Unit tests added/updated
- [ ] Integration tests passed
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally
```

3. **Request review** from maintainers
4. **Address feedback** promptly
5. **Wait for approval** and merge

### PR Review Criteria

Reviewers will check:
- Code quality and style compliance
- Test coverage and passing tests
- Documentation completeness
- No breaking changes (or properly documented)
- Performance implications
- Security considerations

---

## Issue Reporting

### Before Creating an Issue

1. **Search existing issues** to avoid duplicates
2. **Reproduce the bug** consistently
3. **Gather relevant information** (logs, screenshots, versions)

### Issue Template

```markdown
**Issue Type**: Bug / Feature Request / Enhancement

**Description**
Clear description of the issue or feature

**Steps to Reproduce** (for bugs)
1. Execute SQL script X
2. Run procedure Y
3. Observe error Z

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- Snowflake Version: X.X.X
- Python Version: 3.13.0
- OS: Windows 11 / macOS / Linux

**Logs/Screenshots**
```sql
-- Error message or log output
```

**Possible Solution** (optional)
Any ideas on how to fix

**Additional Context**
Any other relevant information
```

---

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Requests**: Code contributions

### Getting Help

- Check [documentation](FINAL_DELIVERABLES/) first
- Search [existing issues](https://github.com/YOUR_ORG/snowflake-SECURITY_ANALYTICS-project/issues)
- Ask in [GitHub Discussions](https://github.com/YOUR_ORG/snowflake-SECURITY_ANALYTICS-project/discussions)

---

## Recognition

Contributors will be recognized in:
- README.md acknowledgments section
- Release notes for significant contributions
- GitHub contributors page

---

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.

---

Thank you for contributing to the IT Security KPI Data Warehouse project! 🎉

**Questions?** Open a discussion on GitHub or contact the maintainers.

---

**Last Updated**: October 2025
