# Email: Snowflake TASK Privileges - Automation Required

---

**Para**: Snowflake Administrator
**De**: Fuad Oñate
**Asunto**: Request: CREATE TASK and EXECUTE TASK Privileges for DEV_DEVELOPER Role
**Fecha**: October 24, 2025
**Prioridad**: Alta

---

## Email Body

Hi [Snowflake Admin Name],

Following up on the ServiceNow connector installation request, I'm writing to request additional privileges needed for **task automation** in our SECURITY_ANALYTICS Data Warehouse.

### What We Need

**Request**: Grant **CREATE TASK** and **EXECUTE TASK** privileges to the **DEV_DEVELOPER** role on the **DEV_TRANSFORMATION** database.

### Why We Need This

Once the ServiceNow connector is installed and syncing data, we need to create **Snowflake Tasks** to automate the transformation pipeline:

```
ServiceNow Connector → RAW tables → Snowflake Tasks → Transformed tables → Reporting Views
                                         ↑
                                   Need permission here
```

Without these privileges:
- ❌ We cannot create automated transformation tasks
- ❌ We would need to run transformations manually every 15-30 minutes
- ❌ Risk of stale data in reporting layer
- ❌ Increased operational overhead

### Specific Privileges Required

```sql
-- Grant CREATE TASK privilege
GRANT CREATE TASK ON SCHEMA DEV_TRANSFORMATION.SERVICENOW TO ROLE DEV_DEVELOPER;

-- Grant EXECUTE TASK privilege (to resume/suspend tasks)
GRANT EXECUTE TASK ON ACCOUNT TO ROLE DEV_DEVELOPER;

-- Alternative (if account-level is too broad):
GRANT EXECUTE TASK ON DATABASE DEV_TRANSFORMATION TO ROLE DEV_DEVELOPER;
```

### How We'll Use Tasks

**Example Task** (ServiceNow Incidents Transformation):

```sql
CREATE OR REPLACE TASK DEV_TRANSFORMATION.SERVICENOW.TASK_TRANSFORM_INCIDENTS
  WAREHOUSE = DEV_WH
  SCHEDULE = '15 MINUTE'  -- Run every 15 minutes
  WHEN
    SYSTEM$STREAM_HAS_DATA('INCIDENTS_RAW_STREAM')  -- Only when new data
AS
MERGE INTO DEV_TRANSFORMATION.SERVICENOW.INCIDENTS AS tgt
USING (
    SELECT
        incident_number,
        sys_id,
        short_description,
        state,
        priority,
        assigned_to_user,
        opened_at,
        closed_at,
        sys_updated_on,
        CURRENT_TIMESTAMP() AS _transformed_timestamp
    FROM DEV_TRANSFORMATION.SERVICENOW.INCIDENTS_RAW
    WHERE _extracted_timestamp >= DATEADD(minute, -30, CURRENT_TIMESTAMP())
) AS src
ON tgt.incident_number = src.incident_number
WHEN MATCHED THEN UPDATE SET
    state = src.state,
    priority = src.priority,
    assigned_to_user = src.assigned_to_user,
    closed_at = src.closed_at,
    sys_updated_on = src.sys_updated_on,
    _transformed_timestamp = src._transformed_timestamp
WHEN NOT MATCHED THEN INSERT (
    incident_number, sys_id, short_description, state, priority,
    assigned_to_user, opened_at, closed_at, sys_updated_on,
    _extracted_timestamp, _transformed_timestamp
)
VALUES (
    src.incident_number, src.sys_id, src.short_description, src.state,
    src.priority, src.assigned_to_user, src.opened_at, src.closed_at,
    src.sys_updated_on, src._extracted_timestamp, src._transformed_timestamp
);

-- Resume the task to start automation
ALTER TASK DEV_TRANSFORMATION.SERVICENOW.TASK_TRANSFORM_INCIDENTS RESUME;
```

### Planned Tasks (7 Total)

| Task Name | Purpose | Schedule | Warehouse |
|-----------|---------|----------|-----------|
| TASK_TRANSFORM_INCIDENTS | Transform incident data | Every 15 min | DEV_WH |
| TASK_TRANSFORM_CHANGES | Transform change requests | Every 30 min | DEV_WH |
| TASK_TRANSFORM_PROBLEMS | Transform problems | Every 30 min | DEV_WH |
| TASK_TRANSFORM_CMDB_CI | Transform CMDB items | Every 60 min | DEV_WH |
| TASK_TRANSFORM_USERS | Transform users | Every 4 hours | DEV_WH |
| TASK_TRANSFORM_USER_GROUPS | Transform user groups | Every 4 hours | DEV_WH |
| TASK_TRANSFORM_CMDB_REL | Transform CMDB relationships | Every 60 min | DEV_WH |

### Cost Implications

**Warehouse Compute** (SMALL warehouse):
- 7 tasks × average 10 seconds execution = ~70 seconds total per cycle
- Worst case: 15-min cycle = 96 cycles/day = ~6,720 seconds = 1.87 hours/day
- Monthly: ~56 hours × $2/hour = **~$112/month** (already budgeted)

**Benefits**:
- ✅ Automated transformations (no manual intervention)
- ✅ Near real-time data in reporting layer
- ✅ Reduced operational overhead
- ✅ Consistent data quality (no human error)

### Security Considerations

**Scope of Privileges**:
- CREATE TASK: Limited to DEV_TRANSFORMATION database/schema
- EXECUTE TASK: Limited to tasks created by DEV_DEVELOPER role
- Tasks run under DEV_DEVELOPER role (no privilege escalation)
- All tasks use DEV_WH warehouse (cost control)

**Task Monitoring**:
```sql
-- We can monitor task execution
SELECT *
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE name = 'TASK_TRANSFORM_INCIDENTS'
ORDER BY scheduled_time DESC
LIMIT 10;
```

### Timeline

**Week 1 (After Connector Installation)**:
- Day 5-6: Create 7 transformation tasks (need CREATE TASK privilege)
- Day 7: Resume tasks and validate automation (need EXECUTE TASK privilege)

**Week 2**:
- Monitor task execution
- Optimize schedules based on data volume
- Create additional tasks if needed

### Alternative (If Privileges Cannot Be Granted)

If CREATE TASK cannot be granted, we would need to:
1. ❌ Run transformations manually via Python scripts
2. ❌ Set up external cron jobs (less integrated)
3. ❌ Higher operational overhead
4. ⚠️ Increased risk of human error

**Not Recommended**: Tasks are the standard Snowflake pattern for automation.

### Verification After Granting

Once privileges are granted, I'll verify with:

```sql
-- Check privileges
SHOW GRANTS TO ROLE DEV_DEVELOPER;

-- Test task creation
CREATE OR REPLACE TASK DEV_TRANSFORMATION.SERVICENOW.TEST_TASK
  WAREHOUSE = DEV_WH
  SCHEDULE = '1440 MINUTE'  -- Daily
AS
SELECT 'Test task creation permission';

-- If successful, clean up
DROP TASK DEV_TRANSFORMATION.SERVICENOW.TEST_TASK;
```

### Questions or Concerns?

If you have questions about:
- **Security implications** of EXECUTE TASK privilege
- **Cost control** for task execution
- **Alternative scoping** (database vs. account level)
- **Task governance** (approval process for new tasks)

Please let me know. I'm happy to discuss or provide additional justification.

---

**Thank you for your support!**

This automation is critical for the success of our ServiceNow integration and will set the foundation for all future API integrations (19 additional services planned).

Best regards,
**Fuad Oñate**
Data Engineering Team
GenericCorp - CompanyX Infrastructure

📧 fuad.onate@CompanyX.com

---

## SQL Commands for Admin (Copy-Paste Ready)

```sql
-- =====================================================
-- Grant CREATE TASK privilege
-- =====================================================
GRANT CREATE TASK ON SCHEMA DEV_TRANSFORMATION.SERVICENOW TO ROLE DEV_DEVELOPER;

-- If needed for other schemas:
-- GRANT CREATE TASK ON DATABASE DEV_TRANSFORMATION TO ROLE DEV_DEVELOPER;

-- =====================================================
-- Grant EXECUTE TASK privilege
-- =====================================================
-- Option 1: Account-level (broadest, most flexible)
GRANT EXECUTE TASK ON ACCOUNT TO ROLE DEV_DEVELOPER;

-- Option 2: Database-level (more restrictive)
-- GRANT EXECUTE TASK ON DATABASE DEV_TRANSFORMATION TO ROLE DEV_DEVELOPER;

-- =====================================================
-- Verify privileges granted
-- =====================================================
SHOW GRANTS TO ROLE DEV_DEVELOPER;

-- =====================================================
-- Test (optional - admin can run this)
-- =====================================================
USE ROLE DEV_DEVELOPER;
USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA SERVICENOW;

CREATE OR REPLACE TASK TEST_TASK_PERMISSION
  WAREHOUSE = DEV_WH
  SCHEDULE = '1440 MINUTE'
AS
SELECT 'Permission test successful';

-- If successful, cleanup
DROP TASK IF EXISTS TEST_TASK_PERMISSION;
```

---

## Post-Grant Checklist

After privileges are granted, I will:

- [ ] Verify CREATE TASK privilege with test task
- [ ] Verify EXECUTE TASK privilege (resume/suspend)
- [ ] Create 7 production tasks for ServiceNow transformations
- [ ] Monitor task execution and costs
- [ ] Document task maintenance procedures
- [ ] Set up alerts for task failures

---

**Email prepared**: October 24, 2025
**Ready to send**: Yes ✅
**Dependencies**: ServiceNow connector installation (previous request)
