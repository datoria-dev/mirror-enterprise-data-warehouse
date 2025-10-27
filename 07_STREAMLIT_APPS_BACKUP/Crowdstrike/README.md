# CrowdStrike EDR Data Validation Dashboard

## 🦅 Endpoint Detection & Response Monitoring Platform

A Streamlit-based data validation dashboard for CrowdStrike EDR events, threat detections, and endpoint telemetry monitoring.

## 📋 Overview

This dashboard provides real-time data quality validation and insights for CrowdStrike EDR data ingested into Snowflake. Designed for data engineers and security analysts to ensure data completeness, freshness, and quality before formal BI visualization.

### Key Use Cases
- Validate CrowdStrike data pipeline integrity
- Monitor EDR event ingestion rates
- Analyze threat detection patterns
- Assess endpoint coverage and health
- Quick ad-hoc security insights

## ✨ Features

### Data Quality Validation
- **Data Freshness**: Last ingestion timestamp and latency metrics
- **Completeness Checks**: Record counts, null value analysis
- **Duplicate Detection**: Identify duplicate events or hosts
- **Schema Validation**: Column presence and data type verification

### Security Metrics
- **Threat Detections**: Real-time threat event counts by severity
- **Endpoint Coverage**: Active vs inactive agent status
- **Event Volume**: Hourly/daily event ingestion trends
- **Alert Analysis**: Security alert distribution by type

### Interactive Visualizations
- Time-series event volume charts
- Threat severity distribution (Critical/High/Medium/Low)
- Endpoint status breakdown
- Top hosts by event count
- Detection patterns over time

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
│  └─ VW_CROWDSTRIKE_*         │
└────────────┬─────────────────┘
             │
┌────────────▼─────────────────┐
│  DEV_TRANSFORMATION.SECURITY_ANALYTICS │
│  └─ FACT_EDR                 │
│  └─ DIM_HOST                 │
└────────────┬─────────────────┘
             │
┌────────────▼─────────────────┐
│  DEV_LANDING.SECURITY_ANALYTICS        │
│  └─ L_CROWDSTRIKE_RAW        │
│  └─ L_CROWDSTRIKE_DETECTIONS │
└──────────────────────────────┘
```

## 📊 Data Sources

### Primary Tables/Views
```sql
-- Landing Layer
DEV_LANDING.SECURITY_ANALYTICS.L_CROWDSTRIKE_RAW
DEV_LANDING.SECURITY_ANALYTICS.L_CROWDSTRIKE_DETECTIONS
DEV_LANDING.SECURITY_ANALYTICS.L_CROWDSTRIKE_EVENTS

-- Transformation Layer
DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_EDR
DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST
DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_THREAT

-- Reporting Layer
DEV_REPORTING.SECURITY_ANALYTICS.VW_CROWDSTRIKE_SUMMARY
DEV_REPORTING.SECURITY_ANALYTICS.VW_EDR_THREATS
```

### Data Refresh Schedule
- **Real-time Events**: Via Snowpipe (< 5 min latency)
- **Detections**: Every 15 minutes
- **Host Inventory**: Hourly
- **Summary Views**: Every 30 minutes

## 🚀 Deployment

### Snowflake Streamlit (Recommended)

1. **Create Streamlit App in Snowsight**
   ```sql
   USE DATABASE DEV_REPORTING;
   USE SCHEMA SECURITY_ANALYTICS;
   CREATE STREAMLIT ITSEC_CROWDSTRIKE_VALIDATION
       ROOT_LOCATION = '@STREAMLIT_APPS/crowdstrike'
       MAIN_FILE = 'streamlit_app.py'
       QUERY_WAREHOUSE = 'DEV_REPORTING_WH';
   ```

2. **Upload Files**
   - Upload `streamlit_app.py` to Snowsight
   - Upload `environment.yml` for dependencies

3. **Grant Access**
   ```sql
   GRANT USAGE ON STREAMLIT ITSEC_CROWDSTRIKE_VALIDATION
       TO ROLE DEV_ANALYST;
   ```

### Local Development

```bash
# Install dependencies
conda env create -f environment.yml
conda activate crowdstrike_validation

# Set environment variables
export SNOWFLAKE_ACCOUNT="your_account"
export SNOWFLAKE_USER="your_user"
export SNOWFLAKE_ROLE="DEV_DEVELOPER"
export SNOWFLAKE_WAREHOUSE="DEV_WH"

# Run locally
streamlit run streamlit_app.py
```

## 🎯 Dashboard Tabs

### Tab 1: Data Quality Overview
- Total records ingested (7/30 days)
- Data freshness indicator
- Null value percentages
- Duplicate detection results
- Schema validation status

### Tab 2: Event Analysis
- Event volume time-series (hourly/daily)
- Event type distribution
- Top processes by event count
- Network connection analysis
- File operation trends

### Tab 3: Threat Detection
- Detection count by severity
- MITRE ATT&CK technique mapping
- Top threat indicators
- Detection timeline
- False positive rate

### Tab 4: Endpoint Coverage
- Total endpoints with active agents
- Agent version distribution
- OS platform breakdown
- Inactive agent alerts
- Coverage gaps by business unit

### Tab 5: Performance Metrics
- Query execution times
- Data pipeline latency
- Snowpipe performance
- Warehouse credit usage
- Row processing rates

## 📋 Prerequisites

### Snowflake Access
- Role: `DEV_DEVELOPER` or `DEV_ANALYST`
- Warehouse: `DEV_REPORTING_WH`
- Permissions: SELECT on all CrowdStrike views

### Dependencies (from environment.yml)
- streamlit >= 1.28.0
- snowflake-snowpark-python >= 1.9.0
- pandas >= 2.0.0
- plotly >= 5.17.0
- altair >= 5.0.0

## ⚙️ Configuration

### Date Range Filters
Default: Last 7 days (configurable via sidebar)

### Auto-Refresh
Dashboard auto-refreshes every 5 minutes when enabled

### Row Limits
- Summary metrics: No limit
- Detailed tables: 10,000 rows max
- Export CSVs: 50,000 rows max

## 🔐 Security

### Authentication
- Uses Snowflake session context (no credentials in code)
- Role-based access control via Snowflake
- Audit logging enabled

### Data Handling
- No sensitive data cached locally
- PII masking for user fields
- Encrypted connections only

## ⚡ Performance Tips

1. **Use date filters**: Avoid querying all historical data
2. **Enable caching**: Leverage `@st.cache_data` for expensive queries
3. **Warehouse sizing**: Use X-Small for most queries
4. **Materialized views**: Leverage pre-aggregated data

## 🔧 Troubleshooting

### Common Issues

**No data showing**
- Verify Snowpipe is running: `SHOW PIPES LIKE '%CROWDSTRIKE%'`
- Check last ingestion: `SELECT MAX(INGESTION_TIMESTAMP) FROM L_CROWDSTRIKE_RAW`
- Review query history for errors

**Slow performance**
- Reduce date range
- Check warehouse size
- Review query execution plan
- Consider adding filters

**Permission errors**
- Confirm role has SELECT privileges
- Verify warehouse access
- Check database/schema grants

## 📞 Support

- **Data Engineering**: For pipeline and data quality issues
- **Security Team**: For CrowdStrike API and detection questions
- **Snowflake Admins**: For access and permission requests

## 📚 Additional Resources

- [CrowdStrike Falcon API Documentation](https://falcon.crowdstrike.com/documentation)
- [Snowflake Streamlit Documentation](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [EDR Data Model](../../03_DOCUMENTATION/02_ERD/ERD_DOCUMENTATION.md)

---

**Version**: 1.0.0
**Last Updated**: October 2025
**Maintained by**: GenericCorp Data Engineering Team
**Status**: ✅ Production
