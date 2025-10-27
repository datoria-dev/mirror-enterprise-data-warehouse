-- ============================================================================
-- ENHANCEMENT 3: UNIFIED USER DIMENSION (DIM_USER)
-- ============================================================================
-- Purpose: Create centralized user dimension with SCD Type 2 for historical tracking
-- Author: Data Engineering Team
-- Date: 2025-10-07
-- Estimated Effort: 40 hours
-- ============================================================================

USE ROLE SYSADMIN;
USE WAREHOUSE DEV_WH;
USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA SECURITY_ANALYTICS;

-- ============================================================================
-- SECTION 1: LANDING TABLES FOR SOURCE SYSTEMS
-- ============================================================================

-- Landing: Active Directory Users
CREATE TABLE IF NOT EXISTS DEV_LANDING.SECURITY_ANALYTICS.L_ACTIVE_DIRECTORY_USERS (
    USER_ID VARCHAR(255),
    SAM_ACCOUNT_NAME VARCHAR(255),
    USER_PRINCIPAL_NAME VARCHAR(255),
    EMAIL VARCHAR(255),
    DISPLAY_NAME VARCHAR(255),
    GIVEN_NAME VARCHAR(100),
    SURNAME VARCHAR(100),
    DEPARTMENT VARCHAR(100),
    TITLE VARCHAR(100),
    OFFICE VARCHAR(100),
    PHONE VARCHAR(50),
    MOBILE VARCHAR(50),
    MANAGER_ID VARCHAR(255),
    EMPLOYEE_ID VARCHAR(50),
    IS_ENABLED BOOLEAN,
    ACCOUNT_CREATED_DATE TIMESTAMP,
    LAST_LOGON_DATE TIMESTAMP,
    PASSWORD_LAST_SET TIMESTAMP,
    MEMBER_OF ARRAY,  -- Array of group DNs
    DISTINGUISHED_NAME VARCHAR(500),

    -- Audit
    LOAD_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    SOURCE_FILE VARCHAR(500)
)
COMMENT = 'Landing table for Active Directory user data';

-- Landing: HR System Users
CREATE TABLE IF NOT EXISTS DEV_LANDING.SECURITY_ANALYTICS.L_HR_EMPLOYEES (
    EMPLOYEE_ID VARCHAR(50),
    FIRST_NAME VARCHAR(100),
    LAST_NAME VARCHAR(100),
    EMAIL VARCHAR(255),
    OPCO_CODE VARCHAR(50),
    DIVISION VARCHAR(100),
    DEPARTMENT VARCHAR(100),
    JOB_TITLE VARCHAR(100),
    EMPLOYEE_TYPE VARCHAR(50),  -- 'FTE', 'Contractor', 'Temporary'
    HIRE_DATE DATE,
    TERMINATION_DATE DATE,
    MANAGER_EMPLOYEE_ID VARCHAR(50),
    COST_CENTER VARCHAR(50),
    LOCATION VARCHAR(100),
    IS_ACTIVE BOOLEAN,

    -- Audit
    LOAD_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    SOURCE_FILE VARCHAR(500)
)
COMMENT = 'Landing table for HR employee data';

-- Landing: Privileged Access Management (PAM)
CREATE TABLE IF NOT EXISTS DEV_LANDING.SECURITY_ANALYTICS.L_PRIVILEGED_USERS (
    USER_ID VARCHAR(255),
    EMAIL VARCHAR(255),
    IS_DOMAIN_ADMIN BOOLEAN,
    IS_LOCAL_ADMIN BOOLEAN,
    IS_DATABASE_ADMIN BOOLEAN,
    IS_CLOUD_ADMIN BOOLEAN,
    PRIVILEGED_GROUPS ARRAY,
    LAST_PRIVILEGE_REVIEW_DATE DATE,

    -- Audit
    LOAD_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'Landing table for privileged user access data';

-- ============================================================================
-- SECTION 2: UNIFIED USER DIMENSION (SCD TYPE 2)
-- ============================================================================

CREATE TABLE IF NOT EXISTS DIM_USER (
    USER_KEY NUMBER AUTOINCREMENT PRIMARY KEY,
    USER_ID VARCHAR(255) NOT NULL,  -- Business key (from AD)

    -- Identity
    EMAIL VARCHAR(255),
    USERNAME VARCHAR(255),
    DISPLAY_NAME VARCHAR(255),
    FIRST_NAME VARCHAR(100),
    LAST_NAME VARCHAR(100),

    -- Organizational (from HR)
    EMPLOYEE_ID VARCHAR(50),
    OPCO_ID NUMBER,
    DIVISION VARCHAR(100),
    DEPARTMENT VARCHAR(100),
    JOB_TITLE VARCHAR(100),
    EMPLOYEE_TYPE VARCHAR(50),  -- 'FTE', 'Contractor', 'Vendor', 'Temporary'
    MANAGER_USER_ID VARCHAR(255),
    COST_CENTER VARCHAR(50),
    LOCATION VARCHAR(100),

    -- Status
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    HIRE_DATE DATE,
    TERMINATION_DATE DATE,
    LAST_LOGON_DATE TIMESTAMP,
    ACCOUNT_CREATED_DATE TIMESTAMP,
    PASSWORD_LAST_SET TIMESTAMP,

    -- Security & Access
    IS_PRIVILEGED_USER BOOLEAN DEFAULT FALSE,
    IS_DOMAIN_ADMIN BOOLEAN DEFAULT FALSE,
    IS_LOCAL_ADMIN BOOLEAN DEFAULT FALSE,
    IS_DATABASE_ADMIN BOOLEAN DEFAULT FALSE,
    IS_CLOUD_ADMIN BOOLEAN DEFAULT FALSE,
    REQUIRES_MFA BOOLEAN DEFAULT TRUE,
    PRIVILEGED_GROUPS ARRAY,
    AD_GROUPS ARRAY,
    LAST_PRIVILEGE_REVIEW_DATE DATE,

    -- Data Quality
    DATA_SOURCE VARCHAR(50),  -- 'Active Directory', 'HR System', 'Manual'
    SOURCE_SYSTEM_COUNT NUMBER,  -- How many systems this user appears in (1-3)
    HAS_AD_ACCOUNT BOOLEAN,
    HAS_HR_RECORD BOOLEAN,
    IS_ORPHANED BOOLEAN,  -- User in AD but not in HR (potential issue)

    -- SCD Type 2 Tracking
    VALID_FROM TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    VALID_TO TIMESTAMP DEFAULT TO_TIMESTAMP('9999-12-31 23:59:59'),
    IS_CURRENT BOOLEAN DEFAULT TRUE,
    ROW_HASH VARCHAR(64),  -- Hash for change detection

    -- Audit
    CREATED_BY VARCHAR(100) DEFAULT CURRENT_USER(),
    CREATED_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_BY VARCHAR(100),
    UPDATED_DATE TIMESTAMP,

    -- Foreign Keys
    CONSTRAINT FK_USER_OPCO FOREIGN KEY (OPCO_ID)
        REFERENCES DIM_OPCO(OPCO_ID) NOT RELY,

    -- Unique constraint on current records
    CONSTRAINT UK_USER_CURRENT UNIQUE (USER_ID, IS_CURRENT) NOT ENFORCED
)
COMMENT = 'Unified user dimension with SCD Type 2 - Combines AD, HR, and PAM data';

-- Clustering for performance
ALTER TABLE DIM_USER CLUSTER BY (IS_CURRENT, OPCO_ID, USER_ID);

-- ============================================================================
-- SECTION 3: HELPER FUNCTIONS
-- ============================================================================

-- Function to generate row hash for change detection
CREATE OR REPLACE FUNCTION FN_USER_ROW_HASH(
    email VARCHAR,
    display_name VARCHAR,
    department VARCHAR,
    job_title VARCHAR,
    is_active BOOLEAN,
    is_privileged BOOLEAN
)
RETURNS VARCHAR
COMMENT = 'Generates MD5 hash of user attributes for SCD Type 2 change detection'
AS
$$
    SHA2(
        CONCAT(
            COALESCE(email, ''),
            '|',
            COALESCE(display_name, ''),
            '|',
            COALESCE(department, ''),
            '|',
            COALESCE(job_title, ''),
            '|',
            COALESCE(is_active::VARCHAR, 'NULL'),
            '|',
            COALESCE(is_privileged::VARCHAR, 'NULL')
        )
    )
$$;

-- ============================================================================
-- SECTION 4: STAGING VIEW - UNIFIED USER DATA
-- ============================================================================

CREATE OR REPLACE VIEW VW_STG_UNIFIED_USER
COMMENT = 'Staging view combining AD, HR, and PAM data'
AS
WITH ad_users AS (
    SELECT
        USER_ID,
        EMAIL,
        SAM_ACCOUNT_NAME as USERNAME,
        DISPLAY_NAME,
        GIVEN_NAME as FIRST_NAME,
        SURNAME as LAST_NAME,
        DEPARTMENT,
        TITLE as JOB_TITLE,
        MANAGER_ID,
        IS_ENABLED as IS_ACTIVE,
        ACCOUNT_CREATED_DATE,
        LAST_LOGON_DATE,
        PASSWORD_LAST_SET,
        MEMBER_OF as AD_GROUPS,
        LOAD_TIMESTAMP
    FROM DEV_LANDING.SECURITY_ANALYTICS.L_ACTIVE_DIRECTORY_USERS
    WHERE LOAD_TIMESTAMP >= DATEADD('day', -1, CURRENT_TIMESTAMP())  -- Last 24 hours
),
hr_users AS (
    SELECT
        EMPLOYEE_ID,
        EMAIL,
        FIRST_NAME,
        LAST_NAME,
        OPCO_CODE,
        DIVISION,
        DEPARTMENT,
        JOB_TITLE,
        EMPLOYEE_TYPE,
        HIRE_DATE,
        TERMINATION_DATE,
        MANAGER_EMPLOYEE_ID,
        COST_CENTER,
        LOCATION,
        IS_ACTIVE,
        LOAD_TIMESTAMP
    FROM DEV_LANDING.SECURITY_ANALYTICS.L_HR_EMPLOYEES
    WHERE LOAD_TIMESTAMP >= DATEADD('day', -1, CURRENT_TIMESTAMP())
),
pam_users AS (
    SELECT
        USER_ID,
        EMAIL,
        IS_DOMAIN_ADMIN,
        IS_LOCAL_ADMIN,
        IS_DATABASE_ADMIN,
        IS_CLOUD_ADMIN,
        PRIVILEGED_GROUPS,
        LAST_PRIVILEGE_REVIEW_DATE
    FROM DEV_LANDING.SECURITY_ANALYTICS.L_PRIVILEGED_USERS
    WHERE LOAD_TIMESTAMP >= DATEADD('day', -1, CURRENT_TIMESTAMP())
)
SELECT
    -- Primary identifier
    COALESCE(ad.USER_ID, hr.EMPLOYEE_ID) as USER_ID,

    -- Identity
    COALESCE(ad.EMAIL, hr.EMAIL) as EMAIL,
    ad.USERNAME,
    COALESCE(ad.DISPLAY_NAME, CONCAT(hr.FIRST_NAME, ' ', hr.LAST_NAME)) as DISPLAY_NAME,
    COALESCE(ad.FIRST_NAME, hr.FIRST_NAME) as FIRST_NAME,
    COALESCE(ad.LAST_NAME, hr.LAST_NAME) as LAST_NAME,

    -- Organizational (prioritize HR data)
    hr.EMPLOYEE_ID,
    o.OPCO_ID,
    hr.DIVISION,
    COALESCE(hr.DEPARTMENT, ad.DEPARTMENT) as DEPARTMENT,
    COALESCE(hr.JOB_TITLE, ad.JOB_TITLE) as JOB_TITLE,
    hr.EMPLOYEE_TYPE,
    COALESCE(ad.MANAGER_ID, hr.MANAGER_EMPLOYEE_ID) as MANAGER_USER_ID,
    hr.COST_CENTER,
    hr.LOCATION,

    -- Status
    COALESCE(ad.IS_ACTIVE, hr.IS_ACTIVE, FALSE) as IS_ACTIVE,
    hr.HIRE_DATE,
    hr.TERMINATION_DATE,
    ad.LAST_LOGON_DATE,
    ad.ACCOUNT_CREATED_DATE,
    ad.PASSWORD_LAST_SET,

    -- Security
    CASE
        WHEN pam.IS_DOMAIN_ADMIN OR pam.IS_LOCAL_ADMIN OR pam.IS_DATABASE_ADMIN OR pam.IS_CLOUD_ADMIN
        THEN TRUE
        ELSE FALSE
    END as IS_PRIVILEGED_USER,
    pam.IS_DOMAIN_ADMIN,
    pam.IS_LOCAL_ADMIN,
    pam.IS_DATABASE_ADMIN,
    pam.IS_CLOUD_ADMIN,
    pam.PRIVILEGED_GROUPS,
    ad.AD_GROUPS,
    pam.LAST_PRIVILEGE_REVIEW_DATE,

    -- Data Quality
    CASE
        WHEN ad.USER_ID IS NOT NULL AND hr.EMPLOYEE_ID IS NOT NULL THEN 'AD + HR'
        WHEN ad.USER_ID IS NOT NULL THEN 'Active Directory'
        WHEN hr.EMPLOYEE_ID IS NOT NULL THEN 'HR System'
        ELSE 'Unknown'
    END as DATA_SOURCE,
    (CASE WHEN ad.USER_ID IS NOT NULL THEN 1 ELSE 0 END +
     CASE WHEN hr.EMPLOYEE_ID IS NOT NULL THEN 1 ELSE 0 END +
     CASE WHEN pam.USER_ID IS NOT NULL THEN 1 ELSE 0 END) as SOURCE_SYSTEM_COUNT,
    ad.USER_ID IS NOT NULL as HAS_AD_ACCOUNT,
    hr.EMPLOYEE_ID IS NOT NULL as HAS_HR_RECORD,
    (ad.USER_ID IS NOT NULL AND hr.EMPLOYEE_ID IS NULL) as IS_ORPHANED,

    -- Row hash for change detection
    FN_USER_ROW_HASH(
        COALESCE(ad.EMAIL, hr.EMAIL),
        COALESCE(ad.DISPLAY_NAME, CONCAT(hr.FIRST_NAME, ' ', hr.LAST_NAME)),
        COALESCE(hr.DEPARTMENT, ad.DEPARTMENT),
        COALESCE(hr.JOB_TITLE, ad.JOB_TITLE),
        COALESCE(ad.IS_ACTIVE, hr.IS_ACTIVE, FALSE),
        CASE WHEN pam.IS_DOMAIN_ADMIN OR pam.IS_LOCAL_ADMIN THEN TRUE ELSE FALSE END
    ) as ROW_HASH

FROM ad_users ad
FULL OUTER JOIN hr_users hr ON ad.EMAIL = hr.EMAIL
LEFT JOIN pam_users pam ON COALESCE(ad.USER_ID, hr.EMPLOYEE_ID) = pam.USER_ID
LEFT JOIN DIM_OPCO o ON hr.OPCO_CODE = o.OPCO_CODE;

-- ============================================================================
-- SECTION 5: SCD TYPE 2 LOAD PROCEDURE
-- ============================================================================

CREATE OR REPLACE PROCEDURE SP_LOAD_DIM_USER()
RETURNS VARCHAR
LANGUAGE SQL
COMMENT = 'Loads DIM_USER with SCD Type 2 logic - Handles inserts, updates, and historical tracking'
AS
$$
DECLARE
    inserted_count NUMBER DEFAULT 0;
    updated_count NUMBER DEFAULT 0;
    expired_count NUMBER DEFAULT 0;
BEGIN
    -- STEP 1: Expire changed records (SCD Type 2)
    UPDATE DIM_USER tgt
    SET
        IS_CURRENT = FALSE,
        VALID_TO = CURRENT_TIMESTAMP(),
        UPDATED_BY = CURRENT_USER(),
        UPDATED_DATE = CURRENT_TIMESTAMP()
    WHERE tgt.IS_CURRENT = TRUE
      AND EXISTS (
          SELECT 1
          FROM VW_STG_UNIFIED_USER src
          WHERE src.USER_ID = tgt.USER_ID
            AND src.ROW_HASH != tgt.ROW_HASH  -- Change detected
      );

    SET expired_count = SQLROWCOUNT;

    -- STEP 2: Insert new versions of changed records
    INSERT INTO DIM_USER (
        USER_ID, EMAIL, USERNAME, DISPLAY_NAME, FIRST_NAME, LAST_NAME,
        EMPLOYEE_ID, OPCO_ID, DIVISION, DEPARTMENT, JOB_TITLE, EMPLOYEE_TYPE,
        MANAGER_USER_ID, COST_CENTER, LOCATION,
        IS_ACTIVE, HIRE_DATE, TERMINATION_DATE, LAST_LOGON_DATE,
        ACCOUNT_CREATED_DATE, PASSWORD_LAST_SET,
        IS_PRIVILEGED_USER, IS_DOMAIN_ADMIN, IS_LOCAL_ADMIN, IS_DATABASE_ADMIN, IS_CLOUD_ADMIN,
        REQUIRES_MFA, PRIVILEGED_GROUPS, AD_GROUPS, LAST_PRIVILEGE_REVIEW_DATE,
        DATA_SOURCE, SOURCE_SYSTEM_COUNT, HAS_AD_ACCOUNT, HAS_HR_RECORD, IS_ORPHANED,
        VALID_FROM, VALID_TO, IS_CURRENT, ROW_HASH,
        CREATED_BY, CREATED_DATE
    )
    SELECT
        src.USER_ID, src.EMAIL, src.USERNAME, src.DISPLAY_NAME, src.FIRST_NAME, src.LAST_NAME,
        src.EMPLOYEE_ID, src.OPCO_ID, src.DIVISION, src.DEPARTMENT, src.JOB_TITLE, src.EMPLOYEE_TYPE,
        src.MANAGER_USER_ID, src.COST_CENTER, src.LOCATION,
        src.IS_ACTIVE, src.HIRE_DATE, src.TERMINATION_DATE, src.LAST_LOGON_DATE,
        src.ACCOUNT_CREATED_DATE, src.PASSWORD_LAST_SET,
        src.IS_PRIVILEGED_USER, src.IS_DOMAIN_ADMIN, src.IS_LOCAL_ADMIN, src.IS_DATABASE_ADMIN, src.IS_CLOUD_ADMIN,
        TRUE as REQUIRES_MFA,
        src.PRIVILEGED_GROUPS, src.AD_GROUPS, src.LAST_PRIVILEGE_REVIEW_DATE,
        src.DATA_SOURCE, src.SOURCE_SYSTEM_COUNT, src.HAS_AD_ACCOUNT, src.HAS_HR_RECORD, src.IS_ORPHANED,
        CURRENT_TIMESTAMP() as VALID_FROM,
        TO_TIMESTAMP('9999-12-31 23:59:59') as VALID_TO,
        TRUE as IS_CURRENT,
        src.ROW_HASH,
        CURRENT_USER(),
        CURRENT_TIMESTAMP()
    FROM VW_STG_UNIFIED_USER src
    WHERE EXISTS (
        SELECT 1
        FROM DIM_USER tgt
        WHERE tgt.USER_ID = src.USER_ID
          AND tgt.IS_CURRENT = FALSE
          AND tgt.VALID_TO = CURRENT_TIMESTAMP()  -- Just expired
    );

    SET updated_count = SQLROWCOUNT;

    -- STEP 3: Insert new users (never seen before)
    INSERT INTO DIM_USER (
        USER_ID, EMAIL, USERNAME, DISPLAY_NAME, FIRST_NAME, LAST_NAME,
        EMPLOYEE_ID, OPCO_ID, DIVISION, DEPARTMENT, JOB_TITLE, EMPLOYEE_TYPE,
        MANAGER_USER_ID, COST_CENTER, LOCATION,
        IS_ACTIVE, HIRE_DATE, TERMINATION_DATE, LAST_LOGON_DATE,
        ACCOUNT_CREATED_DATE, PASSWORD_LAST_SET,
        IS_PRIVILEGED_USER, IS_DOMAIN_ADMIN, IS_LOCAL_ADMIN, IS_DATABASE_ADMIN, IS_CLOUD_ADMIN,
        REQUIRES_MFA, PRIVILEGED_GROUPS, AD_GROUPS, LAST_PRIVILEGE_REVIEW_DATE,
        DATA_SOURCE, SOURCE_SYSTEM_COUNT, HAS_AD_ACCOUNT, HAS_HR_RECORD, IS_ORPHANED,
        VALID_FROM, VALID_TO, IS_CURRENT, ROW_HASH,
        CREATED_BY, CREATED_DATE
    )
    SELECT
        src.USER_ID, src.EMAIL, src.USERNAME, src.DISPLAY_NAME, src.FIRST_NAME, src.LAST_NAME,
        src.EMPLOYEE_ID, src.OPCO_ID, src.DIVISION, src.DEPARTMENT, src.JOB_TITLE, src.EMPLOYEE_TYPE,
        src.MANAGER_USER_ID, src.COST_CENTER, src.LOCATION,
        src.IS_ACTIVE, src.HIRE_DATE, src.TERMINATION_DATE, src.LAST_LOGON_DATE,
        src.ACCOUNT_CREATED_DATE, src.PASSWORD_LAST_SET,
        src.IS_PRIVILEGED_USER, src.IS_DOMAIN_ADMIN, src.IS_LOCAL_ADMIN, src.IS_DATABASE_ADMIN, src.IS_CLOUD_ADMIN,
        TRUE,
        src.PRIVILEGED_GROUPS, src.AD_GROUPS, src.LAST_PRIVILEGE_REVIEW_DATE,
        src.DATA_SOURCE, src.SOURCE_SYSTEM_COUNT, src.HAS_AD_ACCOUNT, src.HAS_HR_RECORD, src.IS_ORPHANED,
        CURRENT_TIMESTAMP(),
        TO_TIMESTAMP('9999-12-31 23:59:59'),
        TRUE,
        src.ROW_HASH,
        CURRENT_USER(),
        CURRENT_TIMESTAMP()
    FROM VW_STG_UNIFIED_USER src
    WHERE NOT EXISTS (
        SELECT 1
        FROM DIM_USER tgt
        WHERE tgt.USER_ID = src.USER_ID
    );

    SET inserted_count = SQLROWCOUNT;

    RETURN 'DIM_USER load complete: ' || :inserted_count || ' new users, ' ||
           :updated_count || ' updated, ' || :expired_count || ' expired';
END;
$$;

-- ============================================================================
-- SECTION 6: REPORTING VIEWS
-- ============================================================================

-- View: Current Active Users
CREATE OR REPLACE VIEW VW_CURRENT_USERS
COMMENT = 'Current snapshot of all active users'
AS
SELECT
    USER_KEY,
    USER_ID,
    EMAIL,
    DISPLAY_NAME,
    DEPARTMENT,
    JOB_TITLE,
    EMPLOYEE_TYPE,
    IS_PRIVILEGED_USER,
    IS_ACTIVE,
    OPCO_ID,
    LAST_LOGON_DATE
FROM DIM_USER
WHERE IS_CURRENT = TRUE
  AND IS_ACTIVE = TRUE;

-- View: Privileged Users Report
CREATE OR REPLACE VIEW VW_PRIVILEGED_USERS
COMMENT = 'All privileged users with their access levels'
AS
SELECT
    u.USER_ID,
    u.EMAIL,
    u.DISPLAY_NAME,
    u.DEPARTMENT,
    u.JOB_TITLE,
    u.IS_DOMAIN_ADMIN,
    u.IS_LOCAL_ADMIN,
    u.IS_DATABASE_ADMIN,
    u.IS_CLOUD_ADMIN,
    u.PRIVILEGED_GROUPS,
    u.LAST_PRIVILEGE_REVIEW_DATE,
    DATEDIFF('day', u.LAST_PRIVILEGE_REVIEW_DATE, CURRENT_DATE()) as DAYS_SINCE_LAST_REVIEW,
    CASE
        WHEN DAYS_SINCE_LAST_REVIEW > 90 THEN '🔴 Overdue'
        WHEN DAYS_SINCE_LAST_REVIEW > 60 THEN '🟡 Due Soon'
        ELSE '🟢 Current'
    END as REVIEW_STATUS
FROM DIM_USER u
WHERE u.IS_CURRENT = TRUE
  AND u.IS_PRIVILEGED_USER = TRUE;

-- View: Orphaned Accounts
CREATE OR REPLACE VIEW VW_ORPHANED_ACCOUNTS
COMMENT = 'AD accounts without HR records - Potential security risk'
AS
SELECT
    USER_ID,
    EMAIL,
    DISPLAY_NAME,
    DEPARTMENT,
    LAST_LOGON_DATE,
    DATEDIFF('day', LAST_LOGON_DATE, CURRENT_DATE()) as DAYS_SINCE_LAST_LOGON,
    IS_PRIVILEGED_USER,
    ACCOUNT_CREATED_DATE
FROM DIM_USER
WHERE IS_CURRENT = TRUE
  AND IS_ORPHANED = TRUE
ORDER BY IS_PRIVILEGED_USER DESC, DAYS_SINCE_LAST_LOGON DESC;

-- ============================================================================
-- SECTION 7: AUTOMATED REFRESH TASK
-- ============================================================================

CREATE OR REPLACE TASK TASK_LOAD_DIM_USER
    WAREHOUSE = DEV_WH
    SCHEDULE = 'USING CRON 0 2 * * * UTC'  -- Daily at 2:00 AM UTC
    COMMENT = 'Daily load of DIM_USER with SCD Type 2'
AS
    CALL SP_LOAD_DIM_USER();

-- Enable task
ALTER TASK TASK_LOAD_DIM_USER RESUME;

-- ============================================================================
-- SECTION 8: TESTING AND VALIDATION
-- ============================================================================

-- Test 1: Load sample data to landing tables (SAMPLE DATA - Replace with actual data loads)
/*
INSERT INTO DEV_LANDING.SECURITY_ANALYTICS.L_ACTIVE_DIRECTORY_USERS
(USER_ID, EMAIL, SAM_ACCOUNT_NAME, DISPLAY_NAME, GIVEN_NAME, SURNAME, DEPARTMENT, TITLE, IS_ENABLED)
VALUES
    ('AD001', 'john.doe@GenericCorp.com', 'jdoe', 'John Doe', 'John', 'Doe', 'IT Security', 'Security Analyst', TRUE),
    ('AD002', 'jane.smith@GenericCorp.com', 'jsmith', 'Jane Smith', 'Jane', 'Smith', 'IT Operations', 'IT Manager', TRUE);
*/

-- Test 2: Run load procedure
CALL SP_LOAD_DIM_USER();

-- Test 3: Query current users
SELECT COUNT(*) as TOTAL_CURRENT_USERS FROM VW_CURRENT_USERS;

-- Test 4: Check SCD Type 2 history
SELECT
    USER_ID,
    EMAIL,
    DISPLAY_NAME,
    DEPARTMENT,
    VALID_FROM,
    VALID_TO,
    IS_CURRENT
FROM DIM_USER
WHERE USER_ID = 'AD001'
ORDER BY VALID_FROM;

-- Test 5: Privileged users
SELECT * FROM VW_PRIVILEGED_USERS;

-- Test 6: Orphaned accounts
SELECT * FROM VW_ORPHANED_ACCOUNTS;

-- ============================================================================
-- SUCCESS METRICS
-- ============================================================================
-- ✅ Unified user dimension created with SCD Type 2
-- ✅ Multi-source integration (AD + HR + PAM)
-- ✅ Change detection with row hashing
-- ✅ Orphaned account identification
-- ✅ Privileged user tracking
-- ✅ Daily automated refresh
-- ✅ Reporting views for security analytics
-- ============================================================================
