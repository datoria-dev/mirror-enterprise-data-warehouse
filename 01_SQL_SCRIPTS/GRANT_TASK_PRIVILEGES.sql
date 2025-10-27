/*
================================================================================
Grant Task Execution Privileges
================================================================================

This script grants the necessary privileges to execute tasks.

⚠️ IMPORTANT: This must be executed by a user with ACCOUNTADMIN role

Author: GenericCorp Data Engineering Team
Date: 2025-10-24
================================================================================
*/

-- ============================================================================
-- STEP 1: Switch to ACCOUNTADMIN role
-- ============================================================================

USE ROLE ACCOUNTADMIN;

-- ============================================================================
-- STEP 2: Grant EXECUTE TASK privilege to DEV_DEVELOPER role
-- ============================================================================

GRANT EXECUTE TASK ON ACCOUNT TO ROLE DEV_DEVELOPER;

-- ============================================================================
-- STEP 3: Grant EXECUTE MANAGED TASK privilege (for serverless tasks)
-- ============================================================================

GRANT EXECUTE MANAGED TASK ON ACCOUNT TO ROLE DEV_DEVELOPER;

-- ============================================================================
-- STEP 4: Verify grants
-- ============================================================================

SHOW GRANTS TO ROLE DEV_DEVELOPER;

-- ============================================================================
-- STEP 5: Switch back to DEV_DEVELOPER role
-- ============================================================================

USE ROLE DEV_DEVELOPER;
USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA METADATA;

-- ============================================================================
-- STEP 6: Now activate the task
-- ============================================================================

ALTER TASK TASK_DAILY_METADATA_REFRESH RESUME;

-- ============================================================================
-- STEP 7: Verify task is running
-- ============================================================================

SHOW TASKS LIKE 'TASK_DAILY_METADATA_REFRESH';

-- Expected: STATE column should show 'started'

SELECT
    '✅ Task is now active!' as STATUS,
    'Will run daily at 6:00 AM EST (2:00 AM UTC)' as SCHEDULE,
    'Monitor PROCEDURE_EXECUTION_LOG for execution history' as MONITORING;

/*
================================================================================
TROUBLESHOOTING
================================================================================

If you still get permission errors:

1. Verify you have ACCOUNTADMIN role:
   SHOW GRANTS TO USER <your_username>;

2. Check if privileges were granted:
   SHOW GRANTS TO ROLE DEV_DEVELOPER;

3. Verify task ownership:
   SHOW TASKS LIKE 'TASK_DAILY_METADATA_REFRESH';
   -- Check the 'owner' column

4. If task was created by different role, change ownership:
   GRANT OWNERSHIP ON TASK TASK_DAILY_METADATA_REFRESH TO ROLE DEV_DEVELOPER;

5. Alternative: Use a service role with task privileges
   CREATE ROLE IF NOT EXISTS TASK_EXECUTOR;
   GRANT EXECUTE TASK ON ACCOUNT TO ROLE TASK_EXECUTOR;
   GRANT ROLE TASK_EXECUTOR TO ROLE DEV_DEVELOPER;

================================================================================
*/
