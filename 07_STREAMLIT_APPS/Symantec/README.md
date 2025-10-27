# Symantec Endpoint Protection Dashboard

## 🛡️ Endpoint Security & Antivirus Platform

A Streamlit-based data validation dashboard for Symantec Endpoint Protection (SEP) events, malware detections, and endpoint health monitoring.

## 📋 Overview

This dashboard provides real-time data quality validation and insights for Symantec Endpoint Protection data ingested into Snowflake. Designed for data engineers and security analysts to ensure data completeness, freshness, and quality before formal BI visualization.

### Key Use Cases
- Validate Symantec data pipeline integrity
- Monitor endpoint protection coverage
- Analyze malware detection patterns
- Assess endpoint health and compliance
- Quick ad-hoc security insights

## ✨ Features

### Data Quality Validation
- **Data Freshness**: Last event timestamp and ingestion latency
- **Completeness Checks**: Record counts, null value analysis
- **Duplicate Detection**: Identify duplicate detections or events
- **Schema Validation**: Column presence and data type verification

### Endpoint Security Metrics
- **Malware Detections**: Real-time virus and threat counts
- **Endpoint Coverage**: Protected vs unprotected endpoints
- **Definition Updates**: Antivirus signature freshness
- **Scan Status**: Last scan timestamp per endpoint

### Interactive Visualizations
- Time-series detection trends
- Threat type distribution
- Endpoint status breakdown
- Definition age analysis
- Top infected hosts
- Scan coverage gauges

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
│  └─ VW_SYMANTEC_*            │
└────────────┬─────────────────┘
             │
┌────────────▼─────────────────┐
│  DEV_TRANSFORMATION.SECURITY_ANALYTICS │
│  └─ FACT_SYMANTEC_EVENTS     │
│  └─ FACT_MALWARE_DETECTIONS  │
│  └─ DIM_HOST                 │
│  └─ DIM_THREAT               │
└────────────┬─────────────────┘
             │
┌────────────▼─────────────────┐
│  DEV_LANDING.SECURITY_ANALYTICS        │
│  └─ L_SYMANTEC_RAW           │
│  └─ L_SYMANTEC_DETECTIONS    │
│  └─ L_SYMANTEC_SCANS         │
└──────────────────────────────┘
```

## 📊 Data Sources

### Primary Tables/Views
```sql
-- Landing Layer
DEV_LANDING.SECURITY_ANALYTICS.L_SYMANTEC_RAW
DEV_LANDING.SECURITY_ANALYTICS.L_SYMANTEC_DETECTIONS
DEV_LANDING.SECURITY_ANALYTICS.L_SYMANTEC_SCANS
DEV_LANDING.SECURITY_ANALYTICS.L_SYMANTEC_CLIENTS

-- Transformation Layer
DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_SYMANTEC_EVENTS
DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_MALWARE_DETECTIONS
DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST
DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_THREAT

-- Reporting Layer
DEV_REPORTING.SECURITY_ANALYTICS.VW_SYMANTEC_SUMMARY
DEV_REPORTING.SECURITY_ANALYTICS.VW_ENDPOINT_PROTECTION_STATUS
DEV_REPORTING.SECURITY_ANALYTICS.VW_MALWARE_TRENDS
```

### Data Refresh Schedule
- **Protection Events**: Via Snowpipe (< 5 min latency)
- **Malware Detections**: Real-time
- **Client Status**: Every 30 minutes
- **Scan Results**: Every 1 hour
- **Summary Views**: Every 15 minutes

## 🚀 Deployment

### Snowflake Streamlit (Recommended)

1. **Create Streamlit App in Snowsight**
   ```sql
   USE DATABASE DEV_REPORTING;
   USE SCHEMA SECURITY_ANALYTICS;
   CREATE STREAMLIT ITSEC_SYMANTEC_VALIDATION
       ROOT_LOCATION = '@STREAMLIT_APPS/symantec'
       MAIN_FILE = 'streamlit_app.py'
       QUERY_WAREHOUSE = 'DEV_REPORTING_WH';
   ```

2. **Upload Files**
   - Upload `streamlit_app.py` to Snowsight
   - Upload `environment.yml` for dependencies

3. **Grant Access**
   ```sql
   GRANT USAGE ON STREAMLIT ITSEC_SYMANTEC_VALIDATION
       TO ROLE DEV_ANALYST;
   ```

### Local Development

```bash
# Install dependencies
conda env create -f environment.yml
conda activate symantec_validation

# Set environment variables
export SNOWFLAKE_ACCOUNT="your_account"
export SNOWFLAKE_USER="your_user"
export SNOWFLAKE_ROLE="DEV_DEVELOPER"
export SNOWFLAKE_WAREHOUSE="DEV_WH"

# Run locally
streamlit run streamlit_app.py
```

## 🎯 Dashboard Tabs

### Tab 1: Endpoint Protection Overview
- Total protected endpoints
- Client version distribution
- Definition age analysis
- Online vs offline endpoints
- Data freshness indicator

### Tab 2: Malware Detections
- Detection count by type (virus, trojan, spyware, etc.)
- Detection timeline (hourly/daily)
- Top detected threats
- Action taken (cleaned, quarantined, deleted)
- Reinfection tracking

### Tab 3: Scan Status
- Scan completion rate
- Last scan age distribution
- Scan type breakdown (full, quick, custom)
- Endpoints missing scans (>7 days)
- Scan error analysis

### Tab 4: Client Health
- Client connectivity status
- Definition version compliance
- Auto-Protect status
- Tamper Protection status
- Policy compliance rate

### Tab 5: Data Quality Metrics
- Row counts by table
- Data pipeline latency
- Snowpipe performance
- Duplicate detection results
- Schema validation status

## 📋 Prerequisites

### Snowflake Access
- Role: `DEV_DEVELOPER` or `DEV_ANALYST`
- Warehouse: `DEV_REPORTING_WH`
- Permissions: SELECT on all Symantec views

### Dependencies (from environment.yml)
- streamlit >= 1.28.0
- snowflake-snowpark-python >= 1.9.0
- pandas >= 2.0.0
- plotly >= 5.17.0
- altair >= 5.0.0

## ⚙️ Configuration

### Date Range Filters
Default: Last 7 days (configurable via sidebar)

### Threat Type Filters
- Virus
- Trojan
- Worm
- Spyware
- Adware
- Potentially Unwanted Application (PUA)
- Heuristic detection

### Action Filters
- Cleaned
- Quarantined
- Deleted
- Left alone
- Failed to clean

### Auto-Refresh
Dashboard auto-refreshes every 5 minutes when enabled

### Row Limits
- Summary metrics: No limit
- Detection tables: 10,000 rows max
- Export CSVs: 50,000 rows max

## 🔐 Security

### Authentication
- Uses Snowflake session context (no credentials in code)
- Role-based access control via Snowflake
- Audit logging enabled

### Data Handling
- No sensitive data cached locally
- Hostname masking option
- Encrypted connections only

## ⚡ Performance Tips

1. **Use date filters**: Avoid querying all historical detections
2. **Filter by threat type**: Focus on specific malware families
3. **Warehouse sizing**: Use X-Small for most queries
4. **Materialized views**: Leverage pre-aggregated endpoint summaries

## 🔧 Troubleshooting

### Common Issues

**No detection data showing**
- Verify SEPM (Symantec Endpoint Protection Manager) connectivity
- Check Snowpipe status: `SHOW PIPES LIKE '%SYMANTEC%'`
- Review last event: `SELECT MAX(EVENT_TIMESTAMP) FROM L_SYMANTEC_RAW`
- Confirm database replication is active

**Outdated client status**
- Check SEPM export schedule
- Verify API credentials
- Review client check-in frequency
- Confirm Snowpipe auto-ingest

**Missing scan results**
- Verify scan schedules in SEPM
- Check client connectivity
- Review scan task status
- Confirm result reporting is enabled

**Slow dashboard performance**
- Reduce date range to last 7 days
- Apply threat type filters
- Check warehouse size
- Review query execution plans

## 📈 Key Metrics Tracked

### Top 13 ITSEC KPIs (Related)
- **EDR Coverage** (KPI #4): % endpoints with active protection

### Additional Metrics
- Definition age compliance (% < 7 days old)
- Scan completion rate
- Mean time to remediate (MTTR) for detections
- Client connectivity rate
- Policy compliance percentage

## 📞 Support

- **Data Engineering**: For pipeline and data quality issues
- **Endpoint Security Team**: For Symantec configuration questions
- **Snowflake Admins**: For access and permission requests

## 📚 Additional Resources

- [Symantec Endpoint Protection Documentation](https://techdocs.broadcom.com/us/en/symantec-security-software/endpoint-security-and-management/endpoint-protection/all.html)
- [SEPM Database Schema](https://knowledge.broadcom.com/external/article?articleId=170957)
- [Snowflake Streamlit Documentation](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [Endpoint Protection Data Model](../../03_DOCUMENTATION/02_ERD/ERD_DOCUMENTATION.md)

---

**Version**: 1.0.0
**Last Updated**: October 2025
**Maintained by**: GenericCorp Data Engineering Team
**Status**: ✅ Production
