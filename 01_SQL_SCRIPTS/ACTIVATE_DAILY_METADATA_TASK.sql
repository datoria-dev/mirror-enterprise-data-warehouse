/*
================================================================================
Activate Daily Metadata Refresh Task
================================================================================

This script activates the daily scheduled task that refreshes metadata
automatically every day at 6:00 AM EST.

Author: GenericCorp Data Engineering Team
Date: 2025-10-24
================================================================================
*/

USE ROLE DEV_DEVELOPER;
USE WAREHOUSE DEV_WH;
USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA METADATA;

-- ============================================================================
-- STEP 1: Verify Task Exists
-- ============================================================================

SHOW TASKS LIKE 'TASK_DAILY_METADATA_REFRESH';

-- Expected output: One row showing the task details
-- Check the STATE column - should show 'suspended' before activation

-- ============================================================================
-- STEP 2: Resume (Activate) the Task
-- ============================================================================

ALTER TASK TASK_DAILY_METADATA_REFRESH RESUME;

-- ============================================================================
-- STEP 3: Verify Task is Active
-- ============================================================================

SHOW TASKS LIKE 'TASK_DAILY_METADATA_REFRESH';

-- Expected output: STATE column should now show 'started'

-- ============================================================================
-- STEP 4: View Task Details
-- ============================================================================

SELECT
    'TASK_DAILY_METADATA_REFRESH' as TASK_NAME,
    '6:00 AM EST Daily' as SCHEDULE,
    'Refreshes metadata from all SECURITY_ANALYTICS tables' as DESCRIPTION,
    'CALL SP_REFRESH_METADATA()' as ACTION,
    'Check PROCEDURE_EXECUTION_LOG for execution history' as MONITORING
;

-- ============================================================================
-- STEP 5: Check Recent Executions
-- ============================================================================

SELECT
    LOG_ID,
    PROCEDURE_NAME,
    EXECUTION_START,
    EXECUTION_END,
    EXECUTION_DURATION_SECONDS,
    STATUS,
    TABLES_PROCESSED,
    COLUMNS_PROCESSED,
    ROWS_PROCESSED,
    ERROR_MESSAGE
FROM PROCEDURE_EXECUTION_LOG
ORDER BY EXECUTION_START DESC
LIMIT 10;

-- ============================================================================
-- STEP 6: Manual Test Execution (Optional)
-- ============================================================================

-- You can manually test the stored procedure before the scheduled time:
-- CALL SP_REFRESH_METADATA();

-- ============================================================================
-- MONITORING & MAINTENANCE
-- ============================================================================

/*
After activation, the task will run automatically every day at 6:00 AM EST.

To monitor executions:
    SELECT * FROM PROCEDURE_EXECUTION_LOG
    WHERE PROCEDURE_NAME = 'SP_REFRESH_METADATA'
    ORDER BY EXECUTION_START DESC;

To check for failures:
    SELECT * FROM PROCEDURE_EXECUTION_LOG
    WHERE PROCEDURE_NAME = 'SP_REFRESH_METADATA'
      AND STATUS != 'SUCCESS'
    ORDER BY EXECUTION_START DESC;

To pause the task (if needed):
    ALTER TASK TASK_DAILY_METADATA_REFRESH SUSPEND;

To resume the task again:
    ALTER TASK TASK_DAILY_METADATA_REFRESH RESUME;

To modify the schedule:
    ALTER TASK TASK_DAILY_METADATA_REFRESH
    SET SCHEDULE = 'USING CRON 0 8 * * * America/New_York';  -- 8:00 AM EST

Expected Performance:
    - Execution Time: 8-12 seconds
    - Tables Processed: 180
    - Columns Processed: 2,206
    - Success Rate: 100%
*/

-- ============================================================================
-- ALERTING RECOMMENDATIONS
-- ============================================================================

/*
Set up alerts for:

1. Failed Executions:
    CREATE OR REPLACE ALERT ALERT_METADATA_REFRESH_FAILED
    WAREHOUSE = DEV_WH
    SCHEDULE = '60 MINUTE'
    IF (EXISTS (
        SELECT 1 FROM PROCEDURE_EXECUTION_LOG
        WHERE PROCEDURE_NAME = 'SP_REFRESH_METADATA'
          AND STATUS = 'FAILED'
          AND EXECUTION_START >= DATEADD(hour, -1, CURRENT_TIMESTAMP())
    ))
    THEN CALL SYSTEM$SEND_EMAIL(
        'data-engineering@GenericCorp.com',
        'Metadata Refresh Failed',
        'The daily metadata refresh has failed. Check PROCEDURE_EXECUTION_LOG for details.'
    );

2. Long Running Executions:
    Monitor if execution time exceeds 30 seconds

3. No Executions:
    Alert if no execution in last 25 hours (1 hour + 24 hours)
*/

-- ============================================================================
-- VERIFICATION CHECKLIST
-- ============================================================================

SELECT '✅ Task Activation Complete!' as STATUS;

SELECT
    'Verify the following:' as CHECKLIST,
    '1. SHOW TASKS shows STATE = started' as STEP_1,
    '2. Task will run tomorrow at 6:00 AM EST' as STEP_2,
    '3. Monitor PROCEDURE_EXECUTION_LOG daily' as STEP_3,
    '4. Ensure METADATA_EXPORTS tables are refreshed after execution' as STEP_4,
    '5. Streamlit apps will show updated metadata automatically' as STEP_5;

/*
================================================================================
END OF SCRIPT
================================================================================
*/
