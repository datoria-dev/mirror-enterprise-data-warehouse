# ZeroFox External Threat Intelligence Dashboard

## 🌐 Digital Risk & External Threat Protection Platform

A Streamlit-based data validation dashboard for ZeroFox external threat intelligence, brand protection, and social media threat monitoring.

## 📋 Overview

This dashboard provides real-time data quality validation and insights for ZeroFox external threat data ingested into Snowflake. Designed for data engineers and threat analysts to ensure data completeness, freshness, and quality before formal BI visualization.

### Key Use Cases
- Validate ZeroFox data pipeline integrity
- Monitor external threat landscape
- Analyze brand impersonation attempts
- Assess social media security risks
- Quick ad-hoc threat hunting insights

## ✨ Features

### Data Quality Validation
- **Data Freshness**: Last alert timestamp and ingestion latency
- **Completeness Checks**: Record counts, null value analysis
- **Duplicate Detection**: Identify duplicate alerts or entities
- **Schema Validation**: Column presence and data type verification

### External Threat Metrics
- **Alert Volume**: Real-time threat alert counts by severity
- **Threat Types**: Phishing, impersonation, data leakage, etc.
- **Platform Coverage**: Social media, dark web, domains
- **Takedown Status**: Requested, in-progress, completed

### Interactive Visualizations
- Time-series alert trends
- Threat severity distribution
- Platform breakdown (Twitter, Facebook, LinkedIn, etc.)
- Takedown effectiveness metrics
- Brand impersonation timeline
- Dark web mention tracking

## 🏗️ Architecture

```
┌─────────────────────────────────┐
│    Streamlit Dashboard          │
│    (streamlit_app.py)           │
└────────────┬────────────────────┘
             │
    ┌────────▼────────┐
    │  Snowpark APIs  │
    └────────┬────────┘
             │
┌────────────▼─────────────────┐
│  DEV_REPORTING.SECURITY_ANALYTICS      │
│  └─ VW_ZEROFOX_*             │
└────────────┬─────────────────┘
             │
┌────────────▼─────────────────┐
│  DEV_TRANSFORMATION.SECURITY_ANALYTICS │
│  └─ FACT_ZEROFOX_ALERTS      │
│  └─ FACT_EXTERNAL_THREATS    │
│  └─ DIM_THREAT_PLATFORM      │
│  └─ DIM_THREAT_ACTOR         │
└────────────┬─────────────────┘
             │
┌────────────▼─────────────────┐
│  DEV_LANDING.SECURITY_ANALYTICS        │
│  └─ L_ZEROFOX_ALERTS         │
│  └─ L_ZEROFOX_ENTITIES       │
│  └─ L_ZEROFOX_TAKEDOWNS      │
└──────────────────────────────┘
```

## 📊 Data Sources

### Primary Tables/Views
```sql
-- Landing Layer
DEV_LANDING.SECURITY_ANALYTICS.L_ZEROFOX_ALERTS
DEV_LANDING.SECURITY_ANALYTICS.L_ZEROFOX_ENTITIES
DEV_LANDING.SECURITY_ANALYTICS.L_ZEROFOX_TAKEDOWNS
DEV_LANDING.SECURITY_ANALYTICS.L_ZEROFOX_DOMAINS

-- Transformation Layer
DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_ZEROFOX_ALERTS
DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_EXTERNAL_THREATS
DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_THREAT_PLATFORM
DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_THREAT_ACTOR

-- Reporting Layer
DEV_REPORTING.SECURITY_ANALYTICS.VW_ZEROFOX_SUMMARY
DEV_REPORTING.SECURITY_ANALYTICS.VW_EXTERNAL_THREATS
DEV_REPORTING.SECURITY_ANALYTICS.VW_TAKEDOWN_TRACKING
```

### Monitored Platforms
- **Social Media**: Twitter/X, Facebook, Instagram, LinkedIn, TikTok
- **Domains**: Typosquatting, malicious domains, phishing sites
- **Dark Web**: Forums, marketplaces, paste sites
- **App Stores**: iOS App Store, Google Play
- **Code Repositories**: GitHub, GitLab, Pastebin

### Data Refresh Schedule
- **Alerts**: Via Snowpipe (< 5 min latency)
- **Entity Updates**: Every 15 minutes
- **Takedown Status**: Every 30 minutes
- **Summary Views**: Every 10 minutes

## 🚀 Deployment

### Snowflake Streamlit (Recommended)

1. **Create Streamlit App in Snowsight**
   ```sql
   USE DATABASE DEV_REPORTING;
   USE SCHEMA SECURITY_ANALYTICS;
   CREATE STREAMLIT ITSEC_ZEROFOX_VALIDATION
       ROOT_LOCATION = '@STREAMLIT_APPS/zerofox'
       MAIN_FILE = 'streamlit_app.py'
       QUERY_WAREHOUSE = 'DEV_REPORTING_WH';
   ```

2. **Upload Files**
   - Upload `streamlit_app.py` to Snowsight
   - Upload `environment.yml` for dependencies

3. **Grant Access**
   ```sql
   GRANT USAGE ON STREAMLIT ITSEC_ZEROFOX_VALIDATION
       TO ROLE DEV_ANALYST;
   ```

### Local Development

```bash
# Install dependencies
conda env create -f environment.yml
conda activate zerofox_validation

# Set environment variables
export SNOWFLAKE_ACCOUNT="your_account"
export SNOWFLAKE_USER="your_user"
export SNOWFLAKE_ROLE="DEV_DEVELOPER"
export SNOWFLAKE_WAREHOUSE="DEV_WH"

# Run locally
streamlit run streamlit_app.py
```

## 🎯 Dashboard Tabs

### Tab 1: Alert Overview
- Total alerts by severity (Critical/High/Medium/Low)
- New alerts (last 24 hours)
- Alert type distribution
- Platform breakdown
- Data freshness indicator

### Tab 2: Brand Protection
- Impersonation attempts
- Typosquatted domains
- Fake social media accounts
- Brand mention sentiment analysis
- Takedown success rate

### Tab 3: Phishing & Scams
- Phishing campaigns targeting organization
- Malicious domains using brand
- Email impersonation attempts
- SMS/smishing attacks
- Credential harvesting sites

### Tab 4: Data Leakage
- Exposed credentials on dark web
- Code leaks on GitHub/Pastebin
- Sensitive document exposure
- Employee PII in breaches
- Customer data mentions

### Tab 5: Takedown Tracking
- Takedown requests by status
- Time to takedown metrics
- Platform response times
- Recurring threat actors
- Takedown success rates by platform

### Tab 6: Data Quality Metrics
- Row counts by table
- API rate limit status
- Pipeline latency
- Duplicate detection results
- Schema validation status

## 📋 Prerequisites

### Snowflake Access
- Role: `DEV_DEVELOPER` or `DEV_ANALYST`
- Warehouse: `DEV_REPORTING_WH`
- Permissions: SELECT on all ZeroFox views

### Dependencies (from environment.yml)
- streamlit >= 1.28.0
- snowflake-snowpark-python >= 1.9.0
- pandas >= 2.0.0
- plotly >= 5.17.0
- altair >= 5.0.0

## ⚙️ Configuration

### Date Range Filters
Default: Last 30 days (configurable via sidebar)

### Severity Filters
- Critical
- High
- Medium
- Low
- Informational

### Platform Filters
- Social Media
- Domains
- Dark Web
- App Stores
- Code Repositories
- Email

### Alert Type Filters
- Impersonation
- Phishing
- Data Leakage
- Brand Abuse
- Executive Threats
- Malware Distribution

### Auto-Refresh
Dashboard auto-refreshes every 10 minutes when enabled

## 🔐 Security

### Authentication
- Uses Snowflake session context (no credentials in code)
- Role-based access control via Snowflake
- Audit logging enabled

### Data Handling
- Sensitive data redaction available
- PII masking for exposed credentials
- TLP (Traffic Light Protocol) enforcement
- Encrypted connections only

### Access Controls
- Alert details restricted by role
- Sensitive takedown info limited to security team
- Audit trail for all searches

## ⚡ Performance Tips

1. **Filter by platform**: Focus on specific threat vectors
2. **Use date ranges**: Last 30 days for optimal performance
3. **Filter by severity**: Critical/High for faster results
4. **Warehouse sizing**: Use X-Small for summary queries
5. **Leverage views**: Pre-aggregated threat summaries

## 🔧 Troubleshooting

### Common Issues

**No alerts showing**
- Verify ZeroFox API connectivity
- Check API credentials and permissions
- Review Snowpipe status: `SHOW PIPES LIKE '%ZEROFOX%'`
- Confirm last ingestion: `SELECT MAX(ALERT_TIMESTAMP) FROM L_ZEROFOX_ALERTS`

**Delayed alert ingestion**
- Check ZeroFox webhook configuration
- Verify S3 bucket permissions
- Review Snowpipe auto-ingest status
- Monitor API rate limits

**Missing platform data**
- Verify platform monitoring is enabled in ZeroFox
- Check platform-specific API access
- Review entity extraction logic
- Confirm platform scope settings

**Takedown status not updating**
- Verify status webhook is configured
- Check takedown API polling schedule
- Review status mapping logic
- Confirm platform integration health

## 📈 Key Metrics Tracked

### External Threat Effectiveness
- Alert-to-takedown time
- Takedown success rate by platform
- Recurring threat actor identification
- False positive rate

### Brand Protection
- Impersonation attempts blocked
- Malicious domains taken down
- Fake accounts removed
- Sentiment trend analysis

### Data Exposure
- Credentials exposed and rotated
- Code leak detection time
- Document exposure remediation
- Employee risk score

## 📞 Support

- **Data Engineering**: For pipeline and data quality issues
- **Threat Intelligence Team**: For ZeroFox configuration and analysis
- **Legal/Compliance**: For takedown requests and procedures
- **Snowflake Admins**: For access and permission requests

## 📚 Additional Resources

- [ZeroFox Platform Documentation](https://www.zerofox.com/resources/)
- [ZeroFox API Reference](https://api.zerofox.com/docs/)
- [Digital Risk Protection Best Practices](https://www.zerofox.com/blog/)
- [Snowflake Streamlit Documentation](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [External Threat Data Model](../../03_DOCUMENTATION/02_ERD/ERD_DOCUMENTATION.md)

---

**Version**: 1.0.0
**Last Updated**: October 2025
**Maintained by**: GenericCorp Data Engineering Team
**Status**: ✅ Production
