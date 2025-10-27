# Email: DEV_LANDING Schema Creation Privileges

---

**Para**: Snowflake Administrator
**De**: Fuad Oñate
**Asunto**: Request: CREATE SCHEMA Privilege on DEV_LANDING Database for Medallion Architecture
**Fecha**: October 24, 2025
**Prioridad**: Media

---

## Email Body

Hi [Snowflake Admin Name],

I'm writing to request **CREATE SCHEMA** privilege on the **DEV_LANDING** database to properly implement our 3-layer medallion architecture for the SECURITY_ANALYTICS Data Warehouse.

### Current Situation

**What We Have**:
- ✅ CREATE SCHEMA privilege on **DEV_TRANSFORMATION** (working)
- ✅ CREATE SCHEMA privilege on **DEV_REPORTING** (working)
- ❌ **NO** CREATE SCHEMA privilege on **DEV_LANDING** (blocked)

**Current Workaround**:
- We're using **DEV_TRANSFORMATION** as both landing AND transformation layer
- This works but violates data warehouse best practices

### Why We Need This

#### Proper Medallion Architecture

**Ideal 3-Layer Design** (industry standard):

```
Layer 1: DEV_LANDING (Bronze) - Raw data from sources
    ↓
Layer 2: DEV_TRANSFORMATION (Silver) - Business logic applied
    ↓
Layer 3: DEV_REPORTING (Gold) - Analytics and aggregations
```

**Current 2-Layer Workaround** (not ideal):

```
Layer 1+2: DEV_TRANSFORMATION (Bronze + Silver mixed)
    ↓
Layer 3: DEV_REPORTING (Gold)
```

#### Benefits of Proper 3-Layer Architecture

1. **Clear Separation of Concerns**:
   - DEV_LANDING: Raw data only (exact copy from source)
   - DEV_TRANSFORMATION: Business logic and transformations
   - DEV_REPORTING: Analytics and reporting

2. **Better Data Lineage**:
   - Easy to trace data from source → landing → transformation → reporting
   - Audit trail for compliance

3. **Reprocessing Capability**:
   - If transformation logic changes, reprocess from DEV_LANDING
   - No need to re-extract from external APIs (cost savings)

4. **Schema Evolution**:
   - Source schema changes isolated in DEV_LANDING
   - Transformations can adapt without breaking reports

5. **Team Collaboration**:
   - Data Engineers work in DEV_LANDING (extraction)
   - Analytics Engineers work in DEV_TRANSFORMATION (modeling)
   - Business Analysts work in DEV_REPORTING (analysis)

### Specific Privilege Required

```sql
-- Grant CREATE SCHEMA on DEV_LANDING database
GRANT CREATE SCHEMA ON DATABASE DEV_LANDING TO ROLE DEV_DEVELOPER;
```

### How We'll Use DEV_LANDING

#### Planned Schemas (20 Services)

| Schema | Purpose | Data Source | Status |
|--------|---------|-------------|--------|
| **SERVICENOW** | ServiceNow raw tables | Native Connector | Ready |
| **CROWDSTRIKE** | CrowdStrike Falcon raw data | Python API | Planned |
| **PROOFPOINT** | Proofpoint email security | Python API | Planned |
| **SENTINELONE** | SentinelOne EDR raw data | Python API | Planned |
| **TENABLE** | Tenable vulnerability scans | Python API | Planned |
| **CYBELANGEL** | CybelAngel threat intelligence | Python API | Planned |
| ... (15 more) | Other security services | Python API | Planned |

#### Example: ServiceNow Landing Schema

**With CREATE SCHEMA privilege**:
```sql
-- Create landing schema
CREATE SCHEMA DEV_LANDING.SERVICENOW;

-- Raw tables (from Native Connector)
CREATE TABLE DEV_LANDING.SERVICENOW.INCIDENT_RAW (
    _raw_json VARIANT,
    _extracted_timestamp TIMESTAMP_LTZ,
    _source_system VARCHAR(50) DEFAULT 'ServiceNow'
);

CREATE TABLE DEV_LANDING.SERVICENOW.CHANGE_REQUEST_RAW (
    _raw_json VARIANT,
    _extracted_timestamp TIMESTAMP_LTZ,
    _source_system VARCHAR(50) DEFAULT 'ServiceNow'
);

-- ... (5 more tables)
```

**Current workaround** (mixing layers):
```sql
-- Everything in DEV_TRANSFORMATION (not ideal)
CREATE TABLE DEV_TRANSFORMATION.SERVICENOW.INCIDENT_RAW (...);
CREATE TABLE DEV_TRANSFORMATION.SERVICENOW.INCIDENTS (...);  -- Mixed!
```

### Data Flow with Proper 3-Layer Architecture

#### Layer 1: DEV_LANDING (Raw Data)
```sql
-- SERVICENOW schema
DEV_LANDING.SERVICENOW.INCIDENT_RAW
DEV_LANDING.SERVICENOW.CHANGE_REQUEST_RAW
DEV_LANDING.SERVICENOW.USERS_RAW
...
```

#### Layer 2: DEV_TRANSFORMATION (Business Logic)
```sql
-- SERVICENOW schema
DEV_TRANSFORMATION.SERVICENOW.INCIDENTS  -- Cleaned, validated
DEV_TRANSFORMATION.SERVICENOW.CHANGE_REQUESTS  -- With lookups
DEV_TRANSFORMATION.SERVICENOW.USERS  -- Deduplicated
...
```

#### Layer 3: DEV_REPORTING (Analytics)
```sql
-- SERVICENOW schema
DEV_REPORTING.SERVICENOW.VW_ACTIVE_INCIDENTS
DEV_REPORTING.SERVICENOW.VW_INCIDENT_METRICS
DEV_REPORTING.SERVICENOW.VW_CHANGE_CALENDAR
...
```

### Migration Plan (If Approved)

**Week 1**:
1. Receive CREATE SCHEMA privilege on DEV_LANDING
2. Create DEV_LANDING.SERVICENOW schema
3. Migrate existing *_RAW tables from DEV_TRANSFORMATION to DEV_LANDING
4. Update ServiceNow connector to point to DEV_LANDING
5. Update transformation tasks to read from DEV_LANDING

**Week 2**:
6. Validate data flow (Landing → Transformation → Reporting)
7. Update documentation and diagrams
8. Apply same pattern to other 19 services

### Cost Implications

**Storage Cost**: Negligible
- Raw data already stored (just moving location)
- Retention: 7 days in DEV_LANDING (same as current)
- Estimated increase: $0/month

**Compute Cost**: None
- No additional queries or transformations
- Same warehouse usage

**Operational Cost**: Savings
- ✅ Better organization (less confusion)
- ✅ Easier debugging (clear lineage)
- ✅ Reduced reprocessing costs (no re-extraction from APIs)

### Alternative (If Privilege Cannot Be Granted)

If CREATE SCHEMA on DEV_LANDING cannot be granted:

**Option 1**: Admin creates schemas for us
- Admin creates DEV_LANDING.SERVICENOW (and 19 others)
- Admin grants USAGE and CREATE TABLE to DEV_DEVELOPER
- We manage tables within pre-created schemas

**Option 2**: Continue with current workaround
- Keep using DEV_TRANSFORMATION as landing layer
- Accept non-ideal architecture
- Document decision for future reference

**Recommendation**: Option 1 if CREATE SCHEMA cannot be granted to role.

### Security Considerations

**Scope of Privilege**:
- CREATE SCHEMA: Limited to DEV_LANDING database only
- No impact on other databases (DEV_TRANSFORMATION, DEV_REPORTING, PROD_*)
- Schemas created by DEV_DEVELOPER are owned by DEV_DEVELOPER

**Schema Naming Convention**:
- All schemas named after source system (SERVICENOW, CROWDSTRIKE, etc.)
- Consistent with DEV_TRANSFORMATION and DEV_REPORTING
- Clear and auditable

### Verification After Granting

Once privilege is granted, I'll verify with:

```sql
-- Check privilege
SHOW GRANTS TO ROLE DEV_DEVELOPER;

-- Test schema creation
CREATE SCHEMA DEV_LANDING.TEST_SCHEMA;

-- If successful
DROP SCHEMA DEV_LANDING.TEST_SCHEMA;

-- Create production schema
CREATE SCHEMA DEV_LANDING.SERVICENOW
    DATA_RETENTION_TIME_IN_DAYS = 7
    COMMENT = 'Raw ServiceNow data from Native Connector (Bronze Layer)';
```

### Questions or Concerns?

If you have questions about:
- **Data governance** for landing layer
- **Naming conventions** for schemas
- **Retention policies** (currently 7 days)
- **Alternative approaches** (admin-created schemas)

Please let me know. I'm happy to discuss or provide additional details.

---

**Thank you for considering this request!**

This privilege will enable us to follow data warehouse best practices and set up a scalable foundation for all 20 API integrations.

**Priority**: Medium (we have a workaround, but proper architecture is preferred)

Best regards,
**Fuad Oñate**
Data Engineering Team
GenericCorp - CompanyX Infrastructure

📧 fuad.onate@CompanyX.com

---

## SQL Commands for Admin (Copy-Paste Ready)

```sql
-- =====================================================
-- Grant CREATE SCHEMA privilege on DEV_LANDING
-- =====================================================
GRANT CREATE SCHEMA ON DATABASE DEV_LANDING TO ROLE DEV_DEVELOPER;

-- =====================================================
-- Verify privilege granted
-- =====================================================
SHOW GRANTS TO ROLE DEV_DEVELOPER;

-- =====================================================
-- Test (optional - admin can run this)
-- =====================================================
USE ROLE DEV_DEVELOPER;

CREATE SCHEMA DEV_LANDING.TEST_SCHEMA
    COMMENT = 'Test schema creation permission';

-- If successful, cleanup
DROP SCHEMA IF EXISTS DEV_LANDING.TEST_SCHEMA;
```

---

## Alternative: Admin Creates Schemas (If CREATE SCHEMA Cannot Be Granted)

If you cannot grant CREATE SCHEMA, you can create the schemas and grant us table-level privileges:

```sql
-- =====================================================
-- Option: Admin creates schemas for us
-- =====================================================
USE ROLE SYSADMIN;  -- Or ACCOUNTADMIN

-- Create schemas for 20 services
CREATE SCHEMA DEV_LANDING.SERVICENOW
    DATA_RETENTION_TIME_IN_DAYS = 7
    COMMENT = 'ServiceNow raw data (Bronze Layer)';

CREATE SCHEMA DEV_LANDING.CROWDSTRIKE
    DATA_RETENTION_TIME_IN_DAYS = 7
    COMMENT = 'CrowdStrike Falcon raw data (Bronze Layer)';

CREATE SCHEMA DEV_LANDING.PROOFPOINT
    DATA_RETENTION_TIME_IN_DAYS = 7
    COMMENT = 'Proofpoint raw data (Bronze Layer)';

-- ... (17 more schemas)

-- Grant table-level privileges to DEV_DEVELOPER
GRANT USAGE ON SCHEMA DEV_LANDING.SERVICENOW TO ROLE DEV_DEVELOPER;
GRANT CREATE TABLE ON SCHEMA DEV_LANDING.SERVICENOW TO ROLE DEV_DEVELOPER;
GRANT CREATE VIEW ON SCHEMA DEV_LANDING.SERVICENOW TO ROLE DEV_DEVELOPER;

-- Repeat for all 20 schemas
-- ... (19 more grants)
```

---

## Post-Grant Checklist

After privilege is granted (or schemas are created):

- [ ] Verify CREATE SCHEMA privilege (or USAGE + CREATE TABLE)
- [ ] Create DEV_LANDING.SERVICENOW schema
- [ ] Migrate *_RAW tables from DEV_TRANSFORMATION to DEV_LANDING
- [ ] Update ServiceNow connector configuration
- [ ] Update transformation tasks to read from DEV_LANDING
- [ ] Validate end-to-end data flow
- [ ] Update documentation and architecture diagrams
- [ ] Apply pattern to remaining 19 services

---

**Email prepared**: October 24, 2025
**Ready to send**: Yes ✅
**Priority**: Medium (not blocking, but improves architecture)
**Workaround Available**: Yes (current 2-layer approach works)
