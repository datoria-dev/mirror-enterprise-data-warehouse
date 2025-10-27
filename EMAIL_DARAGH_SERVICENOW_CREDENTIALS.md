# Email: ServiceNow OAuth Credentials Request

---

**To**: Daragh O'Connor
**From**: Fuad Oñate
**Subject**: ServiceNow API Integration - OAuth Credentials Required for Snowflake Connector
**Date**: October 24, 2025
**Priority**: High

---

## Email Body

Hi Daragh,

I hope this email finds you well.

I'm writing to request your assistance with the **ServiceNow API integration** for our SECURITY_ANALYTICS Data Warehouse project. We've successfully completed the infrastructure setup in Snowflake and are now ready to proceed with the connector installation.

### Current Status

✅ **Completed:**
- Snowflake database schemas created (DEV_TRANSFORMATION.SERVICENOW and DEV_REPORTING.SERVICENOW)
- 10 tables configured for raw and transformed data
- 6 analytics views created for reporting
- Pre-configured 7 ServiceNow tables for synchronization (incidents, change requests, problems, CMDB CIs, users, user groups, CMDB relationships)

🔴 **Pending:**
- Installation of "Snowflake Connector for ServiceNow" from Marketplace (in progress with Steve & Prarbdh)
- **ServiceNow OAuth credentials** (your assistance needed)

### What We Need from ServiceNow

To complete the integration, we need an **OAuth application** created in our ServiceNow instance with the following credentials:

1. **Client ID**
2. **Client Secret**
3. **ServiceNow Username** (service account with read access to the 7 tables)
4. **ServiceNow Password**

### ServiceNow Tables to Be Synchronized

The OAuth application will need **read-only access** to the following tables:

| ServiceNow Table | Description | Sync Frequency |
|------------------|-------------|----------------|
| `incident` | Incident management records | Every 15 minutes |
| `change_request` | Change management records | Every 30 minutes |
| `problem` | Problem management records | Every 30 minutes |
| `cmdb_ci` | CMDB configuration items | Every 60 minutes |
| `sys_user` | User directory | Every 4 hours |
| `sys_user_group` | User groups | Every 4 hours |
| `cmdb_rel_ci` | CMDB relationships | Every 60 minutes |

### OAuth Configuration Requirements

**Application Type**: OAuth 2.0 Client Credentials Flow
**Grant Type**: Client Credentials
**Permissions**: Read-only access to the 7 tables listed above
**Scopes**: (as per ServiceNow's OAuth configuration)

### Security Considerations

- The credentials will be stored securely in **Snowflake Secrets** (never hardcoded)
- All data transmission will use HTTPS encryption
- Only **read-only access** is required (no write permissions)
- The service account should have **minimum necessary privileges**
- OAuth tokens will be automatically refreshed by Snowflake connector

### Timeline

**Target Dates:**
- **Week 1 (Oct 28-Nov 1)**: Receive OAuth credentials and install Snowflake connector
- **Week 2 (Nov 4-8)**: Enable tables, initial data load, and testing
- **Target Go-Live**: November 11, 2025

### Benefits of This Integration

This integration will provide:
- **Real-time incident tracking** and SLA monitoring
- **Change management visibility** across the organization
- **CMDB asset inventory** analytics
- **Automated reporting** via Streamlit dashboards and Power BI
- **Cost savings**: ~$18,324/year vs. custom Python solution (71% reduction)

### Next Steps

Once you provide the OAuth credentials:

1. I'll coordinate with the Snowflake administrator to configure the connector
2. Configure the OAuth authentication in Snowflake
3. Enable the 7 tables and trigger initial historical load
4. Validate data quality and create automated Snowflake Tasks for transformations
5. Deploy Streamlit dashboard for ServiceNow analytics

### Questions or Concerns?

If you have any questions about:
- **Security requirements** for the OAuth application
- **Specific permissions** needed for the service account
- **Network access** (firewall rules, IP whitelisting, etc.)
- **Data governance** or **compliance** considerations

Please don't hesitate to reach out. I'm happy to schedule a quick call to discuss any concerns.

### Supporting Documentation

I've prepared comprehensive documentation for this integration:
- **Executive Summary** (business case and ROI)
- **Technical Implementation Plan** (2-week roadmap)
- **Architecture Diagrams** (data flow and medallion structure)
- **Security & Compliance** considerations

I can share these documents if helpful for your review or approval process.

---

**Thank you for your support with this integration!**

Looking forward to your response.

Best regards,
**Fuad Oñate**
Data Engineering Team
GenericCorp - CompanyX Infrastructure

📧 fuad.onate@CompanyX.com

---

## ServiceNow OAuth Application Setup Guide (For Reference)

If you need guidance on creating the OAuth application in ServiceNow:

### Step 1: Create OAuth Application
1. Log into ServiceNow as admin
2. Navigate to: **System OAuth** → **Application Registry**
3. Click **New** → **Create an OAuth API endpoint for external clients**

### Step 2: Configure Application
- **Name**: Snowflake Data Warehouse Integration
- **Client ID**: (auto-generated - provide to me)
- **Client Secret**: (auto-generated - provide to me)
- **Refresh Token Lifespan**: 86400 seconds (24 hours)
- **Access Token Lifespan**: 3600 seconds (1 hour)

### Step 3: Create Service Account
- **Username**: snowflake_service_account (or similar)
- **Password**: (secure password - provide to me)
- **Role**: Read-only access to 7 tables
- **Active**: Yes

### Step 4: Grant Permissions
Grant the service account read-only access to:
- incident (table)
- change_request (table)
- problem (table)
- cmdb_ci (table)
- sys_user (table)
- sys_user_group (table)
- cmdb_rel_ci (table)

---

## What I'll Do With These Credentials

Once received, I will:

1. **Store Securely**: Create Snowflake Secret to store credentials
   ```sql
   CREATE SECRET DEV_TRANSFORMATION.SERVICENOW.SERVICENOW_OAUTH
     TYPE = PASSWORD
     USERNAME = '[service_account_username]'
     PASSWORD = '[service_account_password]';
   ```

2. **Configure Connector**: Link OAuth credentials to Snowflake connector

3. **Enable Tables**: Configure 7 tables for synchronization

4. **Initial Load**: Trigger historical data load (last 90 days)

5. **Validate**: Verify data quality and completeness

6. **Automate**: Create Snowflake Tasks for ongoing transformations

---

**Email prepared**: October 24, 2025
**Ready to send**: Yes ✅
**Priority**: High (blocking Week 1 progress)
