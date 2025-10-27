# Email: ServiceNow Connector - Marketplace Installation Request

---

**To**: Steve Hyer, Prarbdh Ranjan
**From**: Fuad Oñate
**Subject**: Snowflake Marketplace - ServiceNow Connector Installation Request (Account MW76572)
**Date**: October 24, 2025
**Priority**: High

---

## Email Body

Hi Steve and Prarbdh,

I hope this email finds you well.

I've submitted a marketplace installation request for the **Snowflake Connector for ServiceNow** (Listing ID: GZSTZTP0KL1) in our Snowflake account **MW76572**, but I lack the required privileges to complete the installation.

### Marketplace Request Details

**Data Product**: [Snowflake Connector for ServiceNow](https://app.snowflake.com/marketplace/listing/GZSTZTP0KL1)
**Requestor**: Fuad Oñate (fuad.onate@CompanyX.com)
**User Name**: FUAD.ONATE@CompanyX.COM
**Role Name**: PRD_DEVELOPER
**Account**: MW76572

### What I Need

I would appreciate your help with one of the following options:

**Option 1** (Preferred): Grant me the required privileges
```sql
-- Required privileges for marketplace installation
GRANT IMPORT SHARE TO ROLE PRD_DEVELOPER;
GRANT CREATE DATABASE TO ROLE PRD_DEVELOPER;
```

**Option 2**: Install the data product for me
- Install "Snowflake Connector for ServiceNow" from Marketplace
- Target Database: `DEV_TRANSFORMATION`
- Target Schema: `SERVICENOW`
- Warehouse: `DEV_WH` (or create dedicated `SERVICENOW_WH` with AUTO_RESUME = TRUE)
- Grant USAGE privileges to `PRD_DEVELOPER` role on the created database

### Installation Configuration

**Target Setup**:
- **Database**: DEV_TRANSFORMATION (existing)
- **Schema**: SERVICENOW (already created with 10 tables)
- **Warehouse**: DEV_WH (existing) or create SERVICENOW_WH
  - ⚠️ **CRITICAL**: Warehouse MUST have `AUTO_RESUME = TRUE` for connector to function

**If creating dedicated warehouse**:
```sql
CREATE WAREHOUSE SERVICENOW_WH
    WAREHOUSE_SIZE = 'SMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE  -- MANDATORY for connector
    INITIALLY_SUSPENDED = FALSE;

GRANT USAGE ON WAREHOUSE SERVICENOW_WH TO ROLE PRD_DEVELOPER;
```

### Project Context

This connector is part of our **SECURITY_ANALYTICS Data Warehouse** initiative to integrate ServiceNow incident, change, and CMDB data into Snowflake for analytics and reporting.

**Infrastructure Readiness**:
- ✅ DEV_TRANSFORMATION.SERVICENOW schema created (10 tables)
- ✅ DEV_REPORTING.SERVICENOW schema created (6 analytics views)
- ✅ Configuration pre-loaded for 7 ServiceNow tables
- ⏳ Awaiting connector installation to begin data sync

**Timeline**:
- **Week 1 (Oct 28 - Nov 1)**: Connector installation and OAuth configuration
- **Week 2 (Nov 4 - Nov 8)**: Data validation and testing
- **Target Go-Live**: November 11, 2025

### Business Value

**Benefits**:
- Real-time incident tracking and SLA monitoring
- Change management visibility across organization
- CMDB asset inventory analytics
- Automated reporting via Streamlit dashboards and Power BI

**Cost Savings**:
- **$18,324/year** vs. custom Python solution (71% reduction)
- Managed service with 99.9% SLA (no maintenance overhead)

**Monthly Cost**:
- Connector license: $500/month
- Warehouse compute: ~$100/month
- Storage: ~$23/month
- **Total**: ~$623/month (already budgeted)

### Next Steps After Installation

Once the connector is installed:
1. I'll configure OAuth authentication with ServiceNow (credentials from Daragh)
2. Enable 7 ServiceNow tables (incidents, change requests, problems, CMDB CIs, users, user groups, CMDB relationships)
3. Trigger initial historical data load
4. Create Snowflake Tasks for automated transformations
5. Validate data quality and deploy dashboards

### Supporting Documentation

I've prepared comprehensive documentation for this integration:
- **Technical Setup Guide**: Complete infrastructure documentation
- **2-Week Implementation Plan**: Day-by-day roadmap
- **Executive Summary**: Business case and ROI analysis
- **Architecture Diagrams**: 3-layer medallion data flow

Available in our Azure DevOps repository if you'd like to review.

### Questions or Concerns?

If you have any questions about:
- **Security requirements** for the connector
- **Data governance** considerations
- **Cost implications** or budget approval
- **Network/firewall requirements**
- **Alternative approaches**

Please don't hesitate to reach out. I'm happy to schedule a call to discuss in detail.

---

**Thank you for your support with this integration!**

This connector is a critical component of our SECURITY_ANALYTICS Data Warehouse and will enable real-time ServiceNow analytics across the organization.

Please let me know which option works best for you, or if you need any additional information.

Best regards,
**Fuad Oñate**
Data Engineering Team
GenericCorp - CompanyX Infrastructure

📧 fuad.onate@CompanyX.com
📞 [Your phone number]

---

## Marketplace Listing Details

**Product Name**: Snowflake Connector for ServiceNow
**Provider**: Snowflake Inc.
**Listing URL**: https://app.snowflake.com/marketplace/listing/GZSTZTP0KL1
**Documentation**: https://docs.snowflake.com/en/connectors/servicenow/about

**Key Features**:
- Native integration with ServiceNow REST API
- Automatic incremental data sync (Change Data Capture)
- OAuth 2.0 authentication
- Configurable sync schedules (15 min - 24 hours)
- Support for 100+ ServiceNow tables
- Managed by Snowflake (no maintenance required)

---

## SQL Commands for Installation (Option 2)

If you choose to install the connector for me, here are the exact steps:

### Step 1: Install from Marketplace
```sql
-- Navigate to Snowflake Marketplace in Snowsight
-- Search for "Snowflake Connector for ServiceNow"
-- Click "Get" -> "Install"
-- Follow installation wizard
```

### Step 2: Configure Target
- Database: `DEV_TRANSFORMATION`
- Schema: `SERVICENOW`
- Warehouse: `DEV_WH` (or new `SERVICENOW_WH`)

### Step 3: Grant Permissions
```sql
-- Grant usage on connector database to my role
GRANT USAGE ON DATABASE DEV_TRANSFORMATION TO ROLE PRD_DEVELOPER;
GRANT USAGE ON SCHEMA DEV_TRANSFORMATION.SERVICENOW TO ROLE PRD_DEVELOPER;
GRANT USAGE ON WAREHOUSE DEV_WH TO ROLE PRD_DEVELOPER;

-- Grant privileges to manage connector
GRANT ALL ON SCHEMA DEV_TRANSFORMATION.SERVICENOW TO ROLE PRD_DEVELOPER;
```

### Step 4: Verify Installation
```sql
-- Check connector is installed
SHOW SHARES;

-- Verify schema access
USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA SERVICENOW;
SHOW TABLES;
```

---

## Alternative: Grant Me Marketplace Privileges

If you prefer to grant me the privileges to install it myself:

```sql
-- Grant IMPORT SHARE privilege (for marketplace installations)
GRANT IMPORT SHARE TO ROLE PRD_DEVELOPER;

-- Grant CREATE DATABASE privilege (if connector needs dedicated DB)
GRANT CREATE DATABASE ON ACCOUNT TO ROLE PRD_DEVELOPER;

-- Optional: Grant MANAGE EVENT SHARING (for connector management)
GRANT MANAGE EVENT SHARING ON ACCOUNT TO ROLE PRD_DEVELOPER;
```

**Note**: These are account-level privileges. If this is too broad, Option 2 (you install for me) is perfectly fine.

---

## Verification After Installation

After installation is complete, I'll verify with:

```sql
-- Check connector is accessible
USE DATABASE DEV_TRANSFORMATION;
USE SCHEMA SERVICENOW;

-- Verify tables created by connector
SHOW TABLES;

-- Test connector configuration
SELECT * FROM SERVICENOW_CONNECTOR_CONFIG LIMIT 1;
```

---

**Email prepared**: October 24, 2025
**Ready to send**: Yes ✅
**Marketplace Request ID**: Submitted via Snowsight
**Urgency**: High (blocking Week 1 implementation)
