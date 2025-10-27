# Splunk SIEM Data Validation Dashboard

## 🔍 Security Information & Event Management Platform

A Streamlit-based data validation dashboard for Splunk SIEM events, security alerts, and log analytics monitoring.

## 📋 Overview

This dashboard provides real-time data quality validation and insights for Splunk SIEM data ingested into Snowflake. Designed for data engineers and security analysts to ensure data completeness, freshness, and quality before formal BI visualization.

### Key Use Cases
- Validate Splunk data pipeline integrity
- Monitor SIEM event ingestion rates
- Analyze security alert patterns
- Assess log source coverage
- Quick ad-hoc security insights

## ✨ Features

### Data Quality Validation
- **Data Freshness**: Last event timestamp and ingestion latency
- **Completeness Checks**: Record counts, null value analysis
- **Source Validation**: Log source coverage and gaps
- **Schema Validation**: Field presence and data type verification

### SIEM Metrics
- **Security Alerts**: Real-time alert counts by severity
- **Event Volume**: Events per second/minute/hour trends
- **Log Sources**: Active vs inactive source monitoring
- **Notable Events**: Security incident tracking

### Interactive Visualizations
- Time-series event volume charts
- Alert severity distribution
- Top sources by event count
- Notable event timelines
- User activity heatmaps
- Threat actor tracking

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
│  └─ VW_SPLUNK_*              │
└────────────┬─────────────────┘
             │
┌────────────▼─────────────────┐
│  DEV_TRANSFORMATION.SECURITY_ANALYTICS │
│  └─ FACT_SPLUNK_EVENTS       │
│  └─ FACT_SECURITY_ALERTS     │
│  └─ DIM_LOG_SOURCE           │
└────────────┬─────────────────┘
             │
┌────────────▼─────────────────┐
│  DEV_LANDING.SECURITY_ANALYTICS        │
│  └─ L_SPLUNK_RAW             │
│  └─ L_SPLUNK_NOTABLE_EVENTS  │
│  └─ L_SPLUNK_SOURCES         │
└──────────────────────────────┘
```

## 📊 Data Sources

### Primary Tables/Views
```sql
-- Landing Layer
DEV_LANDING.SECURITY_ANALYTICS.L_SPLUNK_RAW
DEV_LANDING.SECURITY_ANALYTICS.L_SPLUNK_NOTABLE_EVENTS
DEV_LANDING.SECURITY_ANALYTICS.L_SPLUNK_SOURCES
DEV_LANDING.SECURITY_ANALYTICS.L_SPLUNK_ALERTS

-- Transformation Layer
DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_SPLUNK_EVENTS
DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_SECURITY_ALERTS
DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_LOG_SOURCE
DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_THREAT

-- Reporting Layer
DEV_REPORTING.SECURITY_ANALYTICS.VW_SPLUNK_SUMMARY
DEV_REPORTING.SECURITY_ANALYTICS.VW_SIEM_ALERTS
DEV_REPORTING.SECURITY_ANALYTICS.VW_LOG_SOURCE_HEALTH
```

### Data Refresh Schedule
- **SIEM Events**: Via Snowpipe (< 2 min latency)
- **Notable Events**: Real-time
- **Log Sources**: Every 15 minutes
- **Summary Views**: Every 10 minutes

## 🚀 Deployment

### Snowflake Streamlit (Recommended)

1. **Create Streamlit App in Snowsight**
   ```sql
   USE DATABASE DEV_REPORTING;
   USE SCHEMA SECURITY_ANALYTICS;
   CREATE STREAMLIT ITSEC_SPLUNK_VALIDATION
       ROOT_LOCATION = '@STREAMLIT_APPS/splunk'
       MAIN_FILE = 'streamlit_app.py'
       QUERY_WAREHOUSE = 'DEV_REPORTING_WH';
   ```

2. **Upload Files**
   - Upload `streamlit_app.py` to Snowsight
   - Upload `environment.yml` for dependencies

3. **Grant Access**
   ```sql
   GRANT USAGE ON STREAMLIT ITSEC_SPLUNK_VALIDATION
       TO ROLE DEV_ANALYST;
   ```

### Local Development

```bash
# Install dependencies
conda env create -f environment.yml
conda activate splunk_validation

# Set environment variables
export SNOWFLAKE_ACCOUNT="your_account"
export SNOWFLAKE_USER="your_user"
export SNOWFLAKE_ROLE="DEV_DEVELOPER"
export SNOWFLAKE_WAREHOUSE="DEV_WH"

# Run locally
streamlit run streamlit_app.py
```

## 🎯 Dashboard Tabs

### Tab 1: Event Ingestion Overview
- Total events ingested (hourly/daily)
- Data freshness indicator
- Ingestion rate (events per second)
- Pipeline latency metrics
- Data quality score

### Tab 2: Security Alerts
- Alert count by severity (Critical/High/Medium/Low)
- Notable events timeline
- Alert type distribution
- Top triggering use cases
- False positive rate

### Tab 3: Log Source Health
- Total active log sources
- Inactive sources (>1 hour no data)
- Source type breakdown
- Top sources by volume
- Coverage gaps by category

### Tab 4: SIEM Analytics
- Search performance metrics
- Index utilization
- Data model acceleration status
- Lookup table freshness
- Correlation search health

### Tab 5: Data Quality Metrics
- Null value analysis by field
- Duplicate event detection
- Timestamp validation
- Field extraction coverage
- Schema drift detection

## 📋 Prerequisites

### Snowflake Access
- Role: `DEV_DEVELOPER` or `DEV_ANALYST`
- Warehouse: `DEV_REPORTING_WH`
- Permissions: SELECT on all Splunk views

### Dependencies (from environment.yml)
- streamlit >= 1.28.0
- snowflake-snowpark-python >= 1.9.0
- pandas >= 2.0.0
- plotly >= 5.17.0
- altair >= 5.0.0

## ⚙️ Configuration

### Date Range Filters
Default: Last 24 hours (configurable via sidebar)

### Event Filters
- By index (main, security, network, etc.)
- By source type (firewall, IDS, proxy, etc.)
- By severity (critical, high, medium, low)
- By host

### Auto-Refresh
Dashboard auto-refreshes every 2 minutes when enabled

### Row Limits
- Summary metrics: No limit
- Event tables: 50,000 rows max
- Export CSVs: 100,000 rows max

## 🔐 Security

### Authentication
- Uses Snowflake session context (no credentials in code)
- Role-based access control via Snowflake
- Audit logging enabled

### Data Handling
- No sensitive data cached locally
- PII masking for user/IP fields
- Encrypted connections only
- Session timeout after 30 minutes

## ⚡ Performance Tips

1. **Narrow time ranges**: Query last 24 hours instead of 7 days
2. **Filter by index**: Focus on security index for faster results
3. **Use source type filters**: Reduce data volume
4. **Warehouse sizing**: Use Medium for large event volumes
5. **Leverage materialized views**: For common aggregations

## 🔧 Troubleshooting

### Common Issues

**No events showing**
- Verify Splunk HEC (HTTP Event Collector) is active
- Check Snowpipe status: `SHOW PIPES LIKE '%SPLUNK%'`
- Review last ingestion: `SELECT MAX(_TIME) FROM L_SPLUNK_RAW`
- Confirm network connectivity to Splunk

**Delayed data ingestion**
- Check Splunk forwarder status
- Review HEC token configuration
- Verify Snowpipe auto-ingest is enabled
- Monitor S3 bucket for new files

**Missing fields in events**
- Verify field extraction rules in Splunk
- Check JSON parsing in Snowflake
- Review VARIANT column expansion
- Confirm sourcetype definitions

**High latency**
- Check Splunk search head load
- Review indexer performance
- Verify Snowpipe compute
- Optimize SQL queries

## 📈 Key Metrics Tracked

### Top 13 ITSEC KPIs (Related)
- **Mean Time to Detect (MTTD)** (KPI #6): Avg hours to detect threats
- **Security Alert Volume** (KPI #7): Daily critical/high alerts

### Additional Metrics
- Events per second (EPS)
- Log source availability
- Alert response time
- Notable event age
- Data retention compliance

## 📞 Support

- **Data Engineering**: For pipeline and data quality issues
- **SOC Team**: For Splunk configuration and alert questions
- **Snowflake Admins**: For access and permission requests

## 📚 Additional Resources

- [Splunk Documentation](https://docs.splunk.com)
- [Splunk HEC Configuration](https://docs.splunk.com/Documentation/Splunk/latest/Data/UsetheHTTPEventCollector)
- [Snowflake Streamlit Documentation](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [SIEM Data Model](../../03_DOCUMENTATION/02_ERD/ERD_DOCUMENTATION.md)

---

**Version**: 1.0.0
**Last Updated**: October 2025
**Maintained by**: GenericCorp Data Engineering Team
**Status**: ✅ Production
