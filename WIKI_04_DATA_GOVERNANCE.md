# SECURITY_ANALYTICS Data Warehouse - Data Governance Framework

## Table of Contents
- [Overview](#overview)
- [Governance Structure](#governance-structure)
- [Data Ownership](#data-ownership)
- [Data Quality Standards](#data-quality-standards)
- [Security & Access Control](#security--access-control)
- [Data Lifecycle Management](#data-lifecycle-management)
- [Compliance & Auditing](#compliance--auditing)
- [Metadata Management](#metadata-management)
- [Change Management](#change-management)
- [Monitoring & Reporting](#monitoring--reporting)
- [Roles & Responsibilities](#roles--responsibilities)

---

## Overview

The SECURITY_ANALYTICS Data Warehouse Data Governance Framework establishes policies, procedures, and standards for managing data assets across the organization. This framework ensures data quality, security, compliance, and proper lifecycle management for all security service data.

### Governance Objectives

1. **Data Quality**: Ensure accuracy, completeness, and consistency of data
2. **Data Security**: Protect sensitive security data from unauthorized access
3. **Compliance**: Meet regulatory and organizational requirements
4. **Accessibility**: Enable authorized users to access data efficiently
5. **Accountability**: Establish clear ownership and responsibilities
6. **Sustainability**: Maintain data assets throughout their lifecycle

### Scope

This governance framework applies to:
- All data in DEV_LANDING and DEV_TRANSFORMATION databases
- 20+ integrated security services (SentinelOne, CybelAngel, Qualys, etc.)
- 180+ cataloged tables and 2,206+ columns
- Streamlit applications and future Power BI reports
- Metadata repository and automation processes

---

## Governance Structure

### Governance Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│             DATA GOVERNANCE COUNCIL                      │
│  (Strategic oversight, policy approval, escalations)    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│          DATA GOVERNANCE STEERING COMMITTEE              │
│   (Tactical planning, standards, cross-functional)      │
└─────────────────────────────────────────────────────────┘
                         ↓
        ┌────────────────┴────────────────┐
        ↓                                  ↓
┌──────────────────┐           ┌──────────────────────┐
│  DATA STEWARDS   │           │   TECHNICAL TEAMS    │
│  (Domain owners) │           │  (Implementation)    │
└──────────────────┘           └──────────────────────┘
        ↓                                  ↓
┌─────────────────────────────────────────────────────────┐
│                   DATA CONSUMERS                         │
│        (Analysts, Security Teams, Management)           │
└─────────────────────────────────────────────────────────┘
```

### Governance Bodies

#### Data Governance Council
- **Purpose**: Strategic oversight and policy approval
- **Membership**: IT Leadership, Security Leadership, Compliance
- **Frequency**: Quarterly
- **Responsibilities**:
  - Approve governance policies and standards
  - Resolve escalated data issues
  - Allocate resources for governance initiatives
  - Review compliance status

#### Data Governance Steering Committee
- **Purpose**: Tactical planning and coordination
- **Membership**: Data Engineering Lead, Security Architects, Data Stewards
- **Frequency**: Monthly
- **Responsibilities**:
  - Define and maintain data standards
  - Coordinate cross-functional data initiatives
  - Monitor data quality metrics
  - Manage metadata and data catalog

#### Data Stewards
- **Purpose**: Domain-specific data ownership
- **Assignment**: One steward per security service category
- **Responsibilities**:
  - Validate data quality for assigned services
  - Document business definitions and rules
  - Approve access requests
  - Escalate data issues

---

## Data Ownership

### Ownership Model

Each security service has designated ownership at three levels:

#### Business Owner
- **Role**: Defines business requirements and use cases
- **Responsibilities**:
  - Define data requirements
  - Approve major changes
  - Validate business rules
  - Prioritize enhancements

#### Data Steward
- **Role**: Ensures data quality and metadata accuracy
- **Responsibilities**:
  - Monitor data quality
  - Document metadata
  - Validate transformations
  - Approve access requests

#### Technical Owner
- **Role**: Implements and maintains data pipelines
- **Responsibilities**:
  - Develop and maintain ETL/ELT processes
  - Ensure technical data quality
  - Implement security controls
  - Troubleshoot technical issues

### Service Ownership Matrix

| Service Category | Example Services | Business Owner | Data Steward | Technical Owner |
|-----------------|------------------|----------------|--------------|-----------------|
| Endpoint Security | SentinelOne, CrowdStrike | Security Operations | Security Data Steward | Data Engineering Team |
| Email Security | Proofpoint, Mimecast | Email Security Team | Email Steward | Data Engineering Team |
| Vulnerability Mgmt | Qualys, Tenable | Vulnerability Mgmt | Vuln Steward | Data Engineering Team |
| Threat Intelligence | CybelAngel | Threat Intel Team | Threat Steward | Data Engineering Team |
| ITSM | ServiceNow | IT Service Mgmt | ITSM Steward | Data Engineering Team |
| Identity & Access | Okta, Azure AD | Identity Team | IAM Steward | Data Engineering Team |

### Ownership Responsibilities

#### For New Data Sources
1. Business Owner identifies need and requirements
2. Data Steward documents metadata and business rules
3. Technical Owner implements data pipeline
4. All three approve production deployment

#### For Existing Data
1. Business Owner validates ongoing relevance
2. Data Steward monitors quality and updates metadata
3. Technical Owner maintains pipelines and performance

---

## Data Quality Standards

### Data Quality Dimensions

#### 1. Accuracy
- **Definition**: Data correctly represents the real-world entity
- **Measurement**: % of records matching source system validation
- **Target**: ≥99% accuracy for critical fields
- **Validation**: Automated checks against source APIs

#### 2. Completeness
- **Definition**: All required data is present
- **Measurement**: % of required fields populated
- **Target**: ≥95% completeness for mandatory fields
- **Validation**: NULL checks, record count reconciliation

#### 3. Consistency
- **Definition**: Data is consistent across tables and time
- **Measurement**: % of records passing cross-table validation
- **Target**: ≥98% consistency across related tables
- **Validation**: Foreign key checks, cross-reference validation

#### 4. Timeliness
- **Definition**: Data is up-to-date and available when needed
- **Measurement**: Time lag between source update and warehouse availability
- **Target**: Daily refreshes complete by 8:00 AM EST
- **Validation**: Refresh timestamp checks

#### 5. Validity
- **Definition**: Data conforms to defined formats and ranges
- **Measurement**: % of records passing format validation
- **Target**: 100% validity for structured fields
- **Validation**: Data type checks, regex patterns, range validation

#### 6. Uniqueness
- **Definition**: No unintended duplicate records
- **Measurement**: % of records with unique identifiers
- **Target**: 100% uniqueness for primary keys
- **Validation**: Duplicate detection queries

### Data Quality Rules Implementation

Stored in `DATA_QUALITY_RULES` table:

```sql
-- Example quality rules
INSERT INTO DATA_QUALITY_RULES (SERVICE_NAME, TABLE_NAME, RULE_TYPE, RULE_DEFINITION)
VALUES
    -- Completeness checks
    ('SentinelOne', 'SENTINELONE_AGENTS', 'NOT_NULL',
     'AGENT_ID, COMPUTER_NAME, LAST_ACTIVE_DATE must not be null'),

    -- Validity checks
    ('Proofpoint', 'PROOFPOINT_MESSAGES', 'FORMAT',
     'EMAIL_ADDRESS must match regex: ^[\\w.-]+@[\\w.-]+\\.\\w+$'),

    -- Range checks
    ('Qualys', 'QUALYS_VULNERABILITIES', 'RANGE',
     'SEVERITY must be between 1 and 5'),

    -- Uniqueness checks
    ('CybelAngel', 'CYBELANGEL_ASSETS', 'UNIQUE',
     'ASSET_ID must be unique per extraction date'),

    -- Consistency checks
    ('ServiceNow', 'SNOW_INCIDENTS', 'CONSISTENCY',
     'ASSIGNED_TO must exist in SNOW_USERS table');
```

### Quality Monitoring Queries

```sql
-- Daily quality check summary
CREATE OR REPLACE VIEW VW_DAILY_QUALITY_SUMMARY AS
SELECT
    SERVICE_NAME,
    TABLE_NAME,
    COUNT(*) as TOTAL_RECORDS,
    SUM(CASE WHEN quality_check_passed = TRUE THEN 1 ELSE 0 END) as PASSED_RECORDS,
    ROUND(100.0 * SUM(CASE WHEN quality_check_passed = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) as PASS_RATE,
    CURRENT_DATE as CHECK_DATE
FROM TABLE_QUALITY_CHECKS
GROUP BY SERVICE_NAME, TABLE_NAME;

-- Quality issues by service
SELECT
    SERVICE_NAME,
    COUNT(*) as ISSUE_COUNT,
    ARRAY_AGG(DISTINCT ISSUE_TYPE) as ISSUE_TYPES
FROM DATA_QUALITY_ISSUES
WHERE RESOLUTION_STATUS = 'Open'
GROUP BY SERVICE_NAME
ORDER BY ISSUE_COUNT DESC;
```

---

## Security & Access Control

### Security Principles

1. **Least Privilege**: Users granted minimum access required
2. **Role-Based Access Control (RBAC)**: Access via roles, not individual users
3. **Separation of Duties**: Read/write/admin privileges separated
4. **Audit Trail**: All access logged and monitored
5. **Data Masking**: Sensitive data masked for non-privileged users

### Snowflake Role Hierarchy

```
ACCOUNTADMIN (Emergency only)
    ↓
SYSADMIN (System administration)
    ↓
┌──────────────┴───────────────┐
↓                              ↓
DEV_DEVELOPER                  PROD_DEVELOPER
(Development access)           (Production access)
    ↓                              ↓
┌───┴───┐                      ┌───┴───┐
↓       ↓                      ↓       ↓
DEV_READER  DEV_WRITER        PROD_READER  PROD_WRITER
(Read-only) (Read/Write)      (Read-only)  (Read/Write)
```

### Access Control Matrix

| Role | DEV_LANDING | DEV_TRANSFORMATION | METADATA | METADATA_EXPORTS | Warehouses |
|------|-------------|-------------------|----------|------------------|------------|
| DEV_READER | SELECT | SELECT | SELECT | SELECT | USAGE (DEV_WH) |
| DEV_WRITER | SELECT, INSERT | SELECT, INSERT, UPDATE | SELECT | SELECT | USAGE (DEV_WH) |
| DEV_DEVELOPER | ALL | ALL | ALL | ALL | ALL (DEV_WH) |
| PROD_READER | - | SELECT | SELECT | SELECT | USAGE (PROD_WH) |
| PROD_DEVELOPER | - | ALL | ALL | ALL | ALL (PROD_WH) |

### Data Classification

#### Classification Levels

| Level | Description | Examples | Access Control |
|-------|-------------|----------|----------------|
| **Public** | Non-sensitive, publicly available | Service names, categories | All authenticated users |
| **Internal** | Internal use, not sensitive | Aggregated statistics | All employees |
| **Confidential** | Sensitive business data | Vulnerability details, asset lists | Role-based, need-to-know |
| **Restricted** | Highly sensitive | Personal data, credentials | Explicit approval required |

#### Sensitive Data Handling

```sql
-- Example: Dynamic data masking for sensitive columns
CREATE OR REPLACE VIEW VW_SENTINELONE_AGENTS_MASKED AS
SELECT
    AGENT_ID,
    COMPUTER_NAME,
    CASE
        WHEN CURRENT_ROLE() IN ('DEV_DEVELOPER', 'PROD_DEVELOPER')
        THEN IP_ADDRESS
        ELSE '***MASKED***'
    END as IP_ADDRESS,
    CASE
        WHEN CURRENT_ROLE() IN ('DEV_DEVELOPER', 'PROD_DEVELOPER')
        THEN MAC_ADDRESS
        ELSE '***MASKED***'
    END as MAC_ADDRESS,
    OS_TYPE,
    LAST_ACTIVE_DATE
FROM SENTINELONE_AGENTS;
```

### SSO Integration (Okta)

All users authenticate via SSO:

```json
{
  "authenticator": "externalbrowser",
  "account": "GenericCorp-CRH_EDW",
  "user": "user.email@CompanyX.com"
}
```

**Benefits**:
- Single sign-on experience
- Centralized user management
- Multi-factor authentication (MFA)
- Automatic user provisioning/deprovisioning

### Access Request Process

1. **Request Submission**: User submits access request via IT Service Portal
2. **Business Justification**: Manager approves business need
3. **Data Steward Review**: Data steward validates appropriateness
4. **Technical Implementation**: IT grants role-based access
5. **Notification**: User notified of access grant
6. **Periodic Review**: Access reviewed quarterly

---

## Data Lifecycle Management

### Lifecycle Stages

```
┌─────────────────────────────────────────────────────────┐
│                    DATA LIFECYCLE                        │
└─────────────────────────────────────────────────────────┘

1. ACQUISITION
   ├── Source identification
   ├── Integration planning
   └── Initial ingestion
        ↓
2. STORAGE (Landing Layer)
   ├── Raw data storage (DEV_LANDING)
   ├── Data validation
   └── Quality checks
        ↓
3. TRANSFORMATION (Transformation Layer)
   ├── Data cleansing
   ├── Business logic application
   └── Enrichment (DEV_TRANSFORMATION)
        ↓
4. CONSUMPTION
   ├── Streamlit applications
   ├── Power BI reports
   └── Ad-hoc analysis
        ↓
5. ARCHIVAL
   ├── Historical data preservation
   ├── Compliance retention
   └── Storage optimization
        ↓
6. DELETION (After retention period)
   ├── Secure deletion
   ├── Audit logging
   └── Compliance verification
```

### Retention Policies

| Data Type | Retention Period | Storage Location | Archive Policy |
|-----------|-----------------|------------------|----------------|
| Raw Landing Data | 90 days | DEV_LANDING | Move to archive after 90 days |
| Transformed Data | 2 years | DEV_TRANSFORMATION | Compress after 1 year |
| Aggregated Reports | 5 years | METADATA_EXPORTS | No archival |
| Audit Logs | 7 years | AUDIT_SCHEMA | Archive after 2 years |
| Metadata | Indefinite | METADATA | No deletion |

### Data Archival Process

```sql
-- Example: Archive old landing data
CREATE OR REPLACE PROCEDURE SP_ARCHIVE_LANDING_DATA(
    p_service_name VARCHAR,
    p_days_to_retain NUMBER
)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
    -- Move data to archive schema
    INSERT INTO ARCHIVE.LANDING_HISTORICAL
    SELECT *, CURRENT_TIMESTAMP() as ARCHIVED_DATE
    FROM DEV_LANDING.SECURITY_ANALYTICS.SERVICE_TABLE
    WHERE EXTRACTION_DATE < DATEADD(day, -p_days_to_retain, CURRENT_DATE());

    -- Delete from active landing
    DELETE FROM DEV_LANDING.SECURITY_ANALYTICS.SERVICE_TABLE
    WHERE EXTRACTION_DATE < DATEADD(day, -p_days_to_retain, CURRENT_DATE());

    RETURN 'Archived ' || SQLROWCOUNT || ' records for ' || p_service_name;
END;
$$;
```

### Time Travel & Fail-Safe

Snowflake features used for data protection:

- **Time Travel**: 90 days for data recovery (Enterprise Edition)
- **Fail-Safe**: Additional 7 days for Snowflake recovery
- **Cloning**: Zero-copy clones for testing and analysis

```sql
-- Restore accidentally deleted data (within 90 days)
CREATE TABLE SENTINELONE_AGENTS_RESTORED CLONE SENTINELONE_AGENTS
    AT(TIMESTAMP => '2025-10-20 10:00:00'::TIMESTAMP);

-- Query historical data
SELECT * FROM SENTINELONE_AGENTS
    AT(OFFSET => -3600); -- 1 hour ago
```

---

## Compliance & Auditing

### Regulatory Requirements

#### GDPR (General Data Protection Regulation)
- **Applicability**: European employee data
- **Requirements**:
  - Right to be forgotten
  - Data portability
  - Consent management
  - Breach notification (72 hours)

#### SOX (Sarbanes-Oxley)
- **Applicability**: Financial controls
- **Requirements**:
  - Audit trails for all changes
  - Separation of duties
  - Change management documentation

#### CCPA (California Consumer Privacy Act)
- **Applicability**: California resident data
- **Requirements**:
  - Data inventory
  - Opt-out mechanisms
  - Data sale disclosure

### Audit Logging

All data access and modifications are logged:

```sql
-- Create audit log table
CREATE TABLE AUDIT_LOG (
    AUDIT_ID NUMBER AUTOINCREMENT,
    EVENT_TIMESTAMP TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    USER_NAME VARCHAR(255),
    ROLE_NAME VARCHAR(255),
    EVENT_TYPE VARCHAR(100), -- SELECT, INSERT, UPDATE, DELETE, GRANT, REVOKE
    OBJECT_TYPE VARCHAR(100), -- TABLE, VIEW, PROCEDURE, TASK
    OBJECT_NAME VARCHAR(500),
    SQL_TEXT VARCHAR(16000),
    ROWS_AFFECTED NUMBER,
    EXECUTION_STATUS VARCHAR(50),
    ERROR_MESSAGE VARCHAR(5000),
    CLIENT_IP VARCHAR(100),
    SESSION_ID VARCHAR(255),
    PRIMARY KEY (AUDIT_ID)
);

-- Populate from Snowflake QUERY_HISTORY
INSERT INTO AUDIT_LOG (
    EVENT_TIMESTAMP, USER_NAME, ROLE_NAME, EVENT_TYPE,
    OBJECT_NAME, SQL_TEXT, ROWS_AFFECTED, EXECUTION_STATUS
)
SELECT
    START_TIME,
    USER_NAME,
    ROLE_NAME,
    QUERY_TYPE,
    CONCAT(DATABASE_NAME, '.', SCHEMA_NAME, '.', QUERY_TAG),
    QUERY_TEXT,
    ROWS_PRODUCED,
    EXECUTION_STATUS
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE START_TIME > DATEADD(hour, -24, CURRENT_TIMESTAMP());
```

### Compliance Reporting

```sql
-- User access report
SELECT
    USER_NAME,
    ROLE_NAME,
    COUNT(*) as QUERY_COUNT,
    MIN(EVENT_TIMESTAMP) as FIRST_ACCESS,
    MAX(EVENT_TIMESTAMP) as LAST_ACCESS,
    ARRAY_AGG(DISTINCT OBJECT_NAME) as ACCESSED_OBJECTS
FROM AUDIT_LOG
WHERE EVENT_TIMESTAMP >= DATEADD(day, -30, CURRENT_DATE())
GROUP BY USER_NAME, ROLE_NAME
ORDER BY QUERY_COUNT DESC;

-- Data modification audit
SELECT
    DATE(EVENT_TIMESTAMP) as MODIFICATION_DATE,
    EVENT_TYPE,
    OBJECT_NAME,
    USER_NAME,
    SUM(ROWS_AFFECTED) as TOTAL_ROWS_MODIFIED
FROM AUDIT_LOG
WHERE EVENT_TYPE IN ('INSERT', 'UPDATE', 'DELETE')
  AND EVENT_TIMESTAMP >= DATEADD(day, -7, CURRENT_DATE())
GROUP BY DATE(EVENT_TIMESTAMP), EVENT_TYPE, OBJECT_NAME, USER_NAME
ORDER BY MODIFICATION_DATE DESC, TOTAL_ROWS_MODIFIED DESC;
```

### Privacy Controls

```sql
-- Implement right to be forgotten (GDPR)
CREATE OR REPLACE PROCEDURE SP_DELETE_PERSONAL_DATA(
    p_user_identifier VARCHAR
)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
DECLARE
    v_tables_processed NUMBER := 0;
    v_rows_deleted NUMBER := 0;
BEGIN
    -- Log deletion request
    INSERT INTO PRIVACY_REQUESTS (REQUEST_TYPE, USER_IDENTIFIER, REQUEST_DATE)
    VALUES ('RIGHT_TO_BE_FORGOTTEN', p_user_identifier, CURRENT_TIMESTAMP());

    -- Delete from all relevant tables
    -- (This is a template - customize per table)
    DELETE FROM OKTA_USERS WHERE USER_EMAIL = p_user_identifier;
    v_rows_deleted := v_rows_deleted + SQLROWCOUNT;

    DELETE FROM AZURE_AD_USERS WHERE USER_PRINCIPAL_NAME = p_user_identifier;
    v_rows_deleted := v_rows_deleted + SQLROWCOUNT;

    -- Update request log
    UPDATE PRIVACY_REQUESTS
    SET COMPLETION_DATE = CURRENT_TIMESTAMP(),
        ROWS_AFFECTED = v_rows_deleted,
        STATUS = 'COMPLETED'
    WHERE USER_IDENTIFIER = p_user_identifier
      AND REQUEST_TYPE = 'RIGHT_TO_BE_FORGOTTEN'
      AND COMPLETION_DATE IS NULL;

    RETURN 'Deleted ' || v_rows_deleted || ' records for ' || p_user_identifier;
END;
$$;
```

---

## Metadata Management

### Metadata Strategy

The SECURITY_ANALYTICS Data Warehouse uses a **centralized metadata repository** to maintain comprehensive documentation of all data assets.

#### Metadata Types

1. **Technical Metadata**
   - Table and column names
   - Data types and constraints
   - Database schemas and relationships
   - Storage statistics (row counts, sizes)

2. **Business Metadata**
   - Business definitions and descriptions
   - Data ownership information
   - Business rules and calculations
   - Data lineage and transformations

3. **Operational Metadata**
   - Refresh schedules and timestamps
   - Data quality metrics
   - Performance statistics
   - Error logs and issues

#### Metadata Repository Components

Managed via automated extraction (see [WIKI_03_METADATA_EXTRACTION.md](WIKI_03_METADATA_EXTRACTION.md)):

- **SP_REFRESH_METADATA()**: Daily extraction procedure
- **TABLE_REGISTRY**: 180 tables cataloged
- **COLUMN_METADATA**: 2,206 columns documented
- **SERVICE_CATALOG**: 21 security services
- **PROCEDURE_EXECUTION_LOG**: Audit trail
- **TASK_DAILY_METADATA_REFRESH**: Daily automation

#### Metadata Quality Standards

- **Completeness**: All tables/columns documented
- **Accuracy**: Metadata updated daily from source
- **Currency**: Refresh within 24 hours of schema changes
- **Accessibility**: Available via views and exports
- **Consistency**: Standardized naming conventions

---

## Change Management

### Change Control Process

```
┌─────────────────────────────────────────────────────────┐
│              CHANGE MANAGEMENT WORKFLOW                  │
└─────────────────────────────────────────────────────────┘

1. REQUEST
   ├── Submit change request
   ├── Business justification
   └── Impact assessment
        ↓
2. REVIEW
   ├── Technical feasibility
   ├── Data steward approval
   └── Security review
        ↓
3. PLANNING
   ├── Design solution
   ├── Develop code
   └── Create test plan
        ↓
4. TESTING
   ├── Unit testing
   ├── Integration testing
   └── User acceptance testing (UAT)
        ↓
5. APPROVAL
   ├── Change Advisory Board (CAB)
   ├── Deployment approval
   └── Rollback plan confirmation
        ↓
6. DEPLOYMENT
   ├── Execute deployment
   ├── Verify success
   └── Document changes
        ↓
7. POST-DEPLOYMENT
   ├── Monitor performance
   ├── Validate data quality
   └── User communication
```

### Change Categories

#### Standard Changes (Pre-Approved)
- Adding new columns to existing tables
- Creating new views
- Updating metadata descriptions
- Minor bug fixes

**Approval**: Technical Owner approval only
**Timeline**: 1-2 days

#### Normal Changes
- Schema modifications
- New table creation
- Stored procedure changes
- Access control updates

**Approval**: Data Steward + CAB approval
**Timeline**: 5-10 days

#### Emergency Changes
- Production outages
- Security vulnerabilities
- Data quality critical issues

**Approval**: Emergency CAB (expedited)
**Timeline**: Same-day

### Git-Based Version Control

All SQL scripts and code maintained in Git:

```bash
# Repository structure
Snowflake_ITSECKPI_Project_DEV/
├── 01_SQL_SCRIPTS/
│   ├── DDL/                    # Data Definition Language
│   ├── DML/                    # Data Manipulation Language
│   ├── PROCEDURES/             # Stored procedures
│   └── VIEWS/                  # View definitions
├── 02_PYTHON_SCRIPTS/
│   ├── extraction/             # Data extraction scripts
│   ├── transformation/         # Transformation logic
│   └── utilities/              # Utility scripts
└── 07_STREAMLIT_APPS/
    ├── SentinelOne/
    ├── CybelAngel/
    └── ...
```

**Branching Strategy**:
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: Individual features
- `hotfix/*`: Emergency fixes

### Change Documentation

```sql
-- Document all schema changes
CREATE TABLE SCHEMA_CHANGE_LOG (
    CHANGE_ID NUMBER AUTOINCREMENT,
    CHANGE_DATE TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CHANGE_TYPE VARCHAR(100), -- CREATE, ALTER, DROP, GRANT
    OBJECT_TYPE VARCHAR(100),
    OBJECT_NAME VARCHAR(500),
    CHANGE_DESCRIPTION VARCHAR(5000),
    CHANGED_BY VARCHAR(255),
    APPROVED_BY VARCHAR(255),
    TICKET_NUMBER VARCHAR(100),
    ROLLBACK_SCRIPT VARCHAR(16000),
    PRIMARY KEY (CHANGE_ID)
);
```

---

## Monitoring & Reporting

### Key Performance Indicators (KPIs)

#### Data Quality KPIs
- **Completeness Rate**: ≥95% target
- **Accuracy Rate**: ≥99% target
- **Timeliness**: 100% daily refreshes on time
- **Data Quality Issues**: <5 open critical issues

#### Operational KPIs
- **Availability**: ≥99.5% uptime
- **Performance**: Query response <5 seconds (p95)
- **Refresh Duration**: Metadata refresh <10 seconds
- **Failed Jobs**: <1% failure rate

#### Governance KPIs
- **Metadata Coverage**: 100% of tables documented
- **Access Reviews**: 100% completed quarterly
- **Policy Compliance**: ≥95% compliance rate
- **Training Completion**: 100% of users trained

### Monitoring Dashboards

#### Daily Operations Dashboard
```sql
-- Daily refresh status
SELECT
    SERVICE_NAME,
    MAX(LAST_ALTERED) as LAST_REFRESH,
    DATEDIFF(hour, MAX(LAST_ALTERED), CURRENT_TIMESTAMP()) as HOURS_SINCE_REFRESH,
    CASE
        WHEN DATEDIFF(hour, MAX(LAST_ALTERED), CURRENT_TIMESTAMP()) > 30 THEN '🔴 Overdue'
        WHEN DATEDIFF(hour, MAX(LAST_ALTERED), CURRENT_TIMESTAMP()) > 24 THEN '🟡 Warning'
        ELSE '🟢 Current'
    END as STATUS
FROM TABLE_REGISTRY
GROUP BY SERVICE_NAME
ORDER BY HOURS_SINCE_REFRESH DESC;
```

#### Data Quality Dashboard
```sql
-- Quality metrics summary
SELECT
    DATE(CHECK_DATE) as DATE,
    AVG(PASS_RATE) as AVG_QUALITY_SCORE,
    MIN(PASS_RATE) as WORST_QUALITY,
    COUNT(DISTINCT SERVICE_NAME) as SERVICES_CHECKED
FROM VW_DAILY_QUALITY_SUMMARY
WHERE CHECK_DATE >= DATEADD(day, -30, CURRENT_DATE())
GROUP BY DATE(CHECK_DATE)
ORDER BY DATE DESC;
```

### Alerts & Notifications

**Critical Alerts** (Immediate notification):
- Daily refresh failures
- Data quality <90%
- Security breaches
- Compliance violations

**Warning Alerts** (Next-day review):
- Data quality 90-95%
- Refresh delays >2 hours
- Unusual access patterns

**Informational** (Weekly digest):
- Performance trends
- Usage statistics
- Metadata updates

---

## Roles & Responsibilities

### RACI Matrix

**R** = Responsible | **A** = Accountable | **C** = Consulted | **I** = Informed

| Activity | Data Governance Council | Steering Committee | Data Stewards | Technical Team | End Users |
|----------|------------------------|-------------------|---------------|----------------|-----------|
| Policy Definition | A | R | C | C | I |
| Standards Development | C | A | R | R | I |
| Data Quality Monitoring | I | C | A | R | I |
| Access Control | A | C | R | R | I |
| Metadata Management | I | C | A | R | I |
| Technical Implementation | I | C | C | A/R | I |
| Compliance Reporting | A | R | C | C | I |
| Issue Resolution | A | C | R | R | I |
| Change Approval | A | R | C | C | I |
| User Training | I | C | R | R | R |

### Training Requirements

#### New User Onboarding
- **Duration**: 2 hours
- **Content**: Data warehouse overview, access procedures, security policies
- **Frequency**: Upon hiring/role change
- **Delivery**: Virtual training session

#### Data Steward Certification
- **Duration**: 8 hours
- **Content**: Governance framework, quality standards, metadata management
- **Frequency**: Annual recertification
- **Delivery**: Instructor-led workshop

#### Technical Team Training
- **Duration**: 16 hours
- **Content**: Snowflake best practices, SQL optimization, security implementation
- **Frequency**: Quarterly updates
- **Delivery**: Hands-on labs

---

## Appendix

### Related Documentation

- [WIKI_01_STREAMLIT_APPS.md](WIKI_01_STREAMLIT_APPS.md) - Application catalog
- [WIKI_02_POWER_BI.md](WIKI_02_POWER_BI.md) - Power BI roadmap
- [WIKI_03_METADATA_EXTRACTION.md](WIKI_03_METADATA_EXTRACTION.md) - Metadata automation
- [WIKI_05_DATA_DICTIONARY.md](WIKI_05_DATA_DICTIONARY.md) - Complete data dictionary
- [WIKI_06_BEST_PRACTICES.md](WIKI_06_BEST_PRACTICES.md) - Development best practices

### Governance Templates

#### Access Request Template
```
REQUEST DETAILS:
- Requestor Name:
- Business Justification:
- Required Access Level: [Reader/Writer/Developer]
- Services/Tables Needed:
- Duration: [Permanent/Temporary - End Date]

APPROVALS:
- Manager Approval: [Pending/Approved]
- Data Steward Approval: [Pending/Approved]
- IT Implementation: [Pending/Completed]
```

#### Data Quality Issue Template
```
ISSUE DETAILS:
- Issue ID:
- Service/Table:
- Issue Type: [Completeness/Accuracy/Timeliness/Other]
- Severity: [Critical/High/Medium/Low]
- Description:
- Identified By:
- Identified Date:

RESOLUTION:
- Assigned To:
- Root Cause:
- Resolution Steps:
- Resolved Date:
- Validation:
```

### Contact Information

| Role | Department | Email |
|------|-----------|-------|
| Data Governance Lead | IT Data Engineering | data.governance@CompanyX.com |
| Security Data Steward | Security Operations | security.steward@CompanyX.com |
| Compliance Officer | Legal & Compliance | compliance@CompanyX.com |
| Technical Support | IT Service Desk | itservicedesk@CompanyX.com |

---

**Document Status**: Production Release v1.0
**Last Updated**: 2025-10-24
**Author**: GenericCorp Data Engineering Team
**Maintained By**: Data Governance Council
