# Email: Snowflake Connector for ServiceNow - Installation Request (Alternative)

---

**To**: Snowflake Administrator
**From**: Fuad Oñate
**Subject**: Request: Install Snowflake Connector for ServiceNow from Marketplace
**Date**: October 24, 2025
**Priority**: High

**Note**: This is an alternative to the email sent to Steve & Prarbdh. Use this if they are not available.

---

## Email Body

Hi [Snowflake Admin Name],

I hope this email finds you well.

I'm writing to request your assistance with installing the **Snowflake Connector for ServiceNow** from the Snowflake Marketplace for our SECURITY_ANALYTICS Data Warehouse project.

### What's Been Completed

✅ **Infrastructure Ready:**
- Database schemas created: `DEV_TRANSFORMATION.SERVICENOW` and `DEV_REPORTING.SERVICENOW`
- 10 tables configured for raw and transformed ServiceNow data
- 6 analytics views created for reporting
- Configuration metadata pre-loaded for 7 ServiceNow tables
- All code committed and pushed to Azure DevOps

🎯 **Current Status**: Infrastructure 100% complete, ready for connector installation

### What We Need

**Request**: Install "Snowflake Connector for ServiceNow" from Snowflake Marketplace

**Required Privileges**: ACCOUNTADMIN role (only you can perform this installation)

### Installation Details

**Connector Name**: Snowflake Connector for ServiceNow
**Source**: Snowflake Marketplace
**Listing URL**: https://app.snowflake.com/marketplace/listing/GZSTZTP0KL1
**Target Database**: `DEV_TRANSFORMATION`
**Target Schema**: `SERVICENOW`
**Warehouse**: `DEV_WH` (or create dedicated `SERVICENOW_WH`)

### Installation Steps (For Your Reference)

1. **Navigate to Marketplace**:
   - Log into Snowsight as ACCOUNTADMIN
   - Navigate to: **Data Products** → **Marketplace**
   - Search for: **"Snowflake Connector for ServiceNow"**

2. **Install the Connector**:
   - Click **"Get"** → **"Install"**
   - Follow the installation wizard

3. **Configure Target Location**:
   - **Database**: `DEV_TRANSFORMATION`
   - **Schema**: `SERVICENOW`
   - **Warehouse**: `DEV_WH` (current) OR create new `SERVICENOW_WH` (recommended)

4. **Warehouse Configuration** (CRITICAL):
   - ⚠️ **MUST HAVE**: `AUTO_RESUME = TRUE` (mandatory for connector)
   - Recommended size: SMALL
   - AUTO_SUSPEND: 300 seconds (5 minutes)

   If creating new warehouse:
   ```sql
   CREATE WAREHOUSE SERVICENOW_WH
       WAREHOUSE_SIZE = 'SMALL'
       AUTO_SUSPEND = 300
       AUTO_RESUME = TRUE  -- MANDATORY
       INITIALLY_SUSPENDED = FALSE;
   ```

5. **Grant Permissions**:
   - Grant connector usage to `PRD_DEVELOPER` role
   - Grant warehouse usage to `PRD_DEVELOPER` role
   - Grant USAGE on the connector database to `PRD_DEVELOPER` role

### Why This Connector?

**Benefits**:
- **Managed Service**: Snowflake maintains the connector (99.9% SLA)
- **Automatic CDC**: Change Data Capture built-in
- **Cost Effective**: $500/month + compute (~$623 total) vs. $2,150/month custom solution
- **Faster Implementation**: 2 weeks vs. 6+ weeks for custom development
- **ROI**: $18,324 annual savings (71% cost reduction)

**Business Value**:
- Real-time incident tracking and SLA monitoring
- Change management visibility
- CMDB asset inventory analytics
- Automated reporting via Streamlit and Power BI

### Timeline

**Week 1 (Oct 28 - Nov 1)**:
- ✅ **Day 1-2**: Connector installation (your assistance needed)
- 🔄 **Day 3-4**: OAuth configuration (my responsibility)
- 🔄 **Day 5-7**: Table enablement and initial data load

**Week 2 (Nov 4 - Nov 8)**:
- Transformation task creation
- Data quality validation
- Testing and UAT

**Target Go-Live**: November 11, 2025

### Cost Implications

**New Monthly Costs**:
- Snowflake Connector license: **$500/month**
- Warehouse compute (SMALL, 5-min auto-suspend): **~$100/month**
- Storage (estimated 1-5 GB): **~$23/month**
- **Total**: **~$623/month**

**Annual Savings**: $18,324 (vs. custom Python solution)

This has already been budgeted and approved.

### Next Steps After Installation

Once you complete the installation:

1. ✅ You notify me that installation is complete
2. ✅ I configure OAuth credentials (from ServiceNow admin)
3. ✅ I enable the 7 ServiceNow tables
4. ✅ I trigger initial historical data load
5. ✅ I create Snowflake Tasks for automated transformations
6. ✅ I validate data quality and deploy dashboards

### Questions or Concerns?

If you have any questions about:
- **Installation process** or requirements
- **Warehouse sizing** recommendations
- **Security considerations**
- **Network/firewall requirements**
- **Permissions and role structure**

Please don't hesitate to reach out. I'm happy to schedule a quick call to discuss.

---

**Thank you for your support with this critical integration!**

This connector is a key component of our SECURITY_ANALYTICS Data Warehouse initiative and will enable real-time ServiceNow analytics across the organization.

Please let me know your availability this week or if you need any additional information.

Best regards,
**Fuad Oñate**
Data Engineering Team
GenericCorp - CompanyX Infrastructure

📧 fuad.onate@CompanyX.com

---

## SQL Commands for Installation (Copy-Paste Ready)

```sql
-- =====================================================
-- Step 1: Create Warehouse (if needed)
-- =====================================================
CREATE WAREHOUSE IF NOT EXISTS SERVICENOW_WH
    WAREHOUSE_SIZE = 'SMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE  -- MANDATORY
    INITIALLY_SUSPENDED = FALSE;

-- =====================================================
-- Step 2: Grant Permissions After Connector Installation
-- =====================================================
-- Grant usage on connector database
GRANT USAGE ON DATABASE [CONNECTOR_DB_NAME] TO ROLE PRD_DEVELOPER;
GRANT USAGE ON ALL SCHEMAS IN DATABASE [CONNECTOR_DB_NAME] TO ROLE PRD_DEVELOPER;

-- Grant usage on warehouse
GRANT USAGE ON WAREHOUSE SERVICENOW_WH TO ROLE PRD_DEVELOPER;

-- =====================================================
-- Step 3: Verify Installation
-- =====================================================
USE ROLE PRD_DEVELOPER;
USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA SERVICENOW;

SHOW TABLES;
```

---

**Email prepared**: October 24, 2025
**Ready to send**: Yes ✅
**Alternative to**: Email to Steve & Prarbdh
**Priority**: High (blocking Week 1 progress)
