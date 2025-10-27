# Qualys Vulnerability Management Dashboard

## 🛡️ Vulnerability Scanning & Assessment Platform

A Streamlit-based data validation dashboard for Qualys vulnerability scan data, asset inventory, and patch compliance monitoring.

## 📋 Overview

This dashboard provides real-time data quality validation and insights for Qualys vulnerability management data ingested into Snowflake. Designed for data engineers and security analysts to ensure data completeness, freshness, and quality before formal BI visualization.

### Key Use Cases
- Validate Qualys data pipeline integrity
- Monitor vulnerability scan coverage
- Analyze critical CVE trends
- Assess patch compliance rates
- Quick ad-hoc vulnerability insights

## ✨ Features

### Data Quality Validation
- **Data Freshness**: Last scan timestamp and data latency metrics
- **Completeness Checks**: Record counts, null value analysis
- **Duplicate Detection**: Identify duplicate vulnerabilities or assets
- **Schema Validation**: Column presence and data type verification

### Vulnerability Metrics
- **Critical CVEs**: High-severity vulnerability counts
- **Asset Coverage**: Scanned vs unscanned asset ratios
- **Scan Frequency**: Asset scan recency analysis
- **Compliance Status**: Patch compliance by severity

### Interactive Visualizations
- Time-series vulnerability trends
- Severity distribution (Critical/High/Medium/Low/Info)
- Top vulnerable assets
- CVE age analysis
- Patch compliance gauges
- CVSS score distributions

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
│  └─ VW_QUALYS_*              │
└────────────┬─────────────────┘
             │
┌────────────▼─────────────────┐
│  DEV_TRANSFORMATION.SECURITY_ANALYTICS │
│  └─ FACT_QUALYS              │
│  └─ FACT_VULNERABILITY       │
│  └─ DIM_HOST                 │
│  └─ DIM_CVE                  │
└────────────┬─────────────────┘
             │
┌────────────▼─────────────────┐
│  DEV_LANDING.SECURITY_ANALYTICS        │
│  └─ L_QUALYS_VULNS           │
│  └─ L_QUALYS_HOSTS           │
│  └─ L_QUALYS_SCANS           │
└──────────────────────────────┘
```

## 📊 Data Sources

### Primary Tables/Views
```sql
-- Landing Layer
DEV_LANDING.SECURITY_ANALYTICS.L_QUALYS_VULNS
DEV_LANDING.SECURITY_ANALYTICS.L_QUALYS_HOSTS
DEV_LANDING.SECURITY_ANALYTICS.L_QUALYS_SCANS
DEV_LANDING.SECURITY_ANALYTICS.L_QUALYS_KB

-- Transformation Layer
DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_QUALYS
DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_VULNERABILITY
DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST
DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_CVE

-- Reporting Layer
DEV_REPORTING.SECURITY_ANALYTICS.VW_QUALYS_SUMMARY
DEV_REPORTING.SECURITY_ANALYTICS.VW_VULNERABILITY_TRENDS
DEV_REPORTING.SECURITY_ANALYTICS.VW_PATCH_COMPLIANCE
```

### Data Refresh Schedule
- **Vulnerability Scans**: Via Snowpipe (real-time)
- **Host Inventory**: Every 4 hours
- **KB Articles**: Daily at 2 AM
- **Summary Views**: Every 30 minutes

## 🚀 Deployment

### Snowflake Streamlit (Recommended)

1. **Create Streamlit App in Snowsight**
   ```sql
   USE DATABASE DEV_REPORTING;
   USE SCHEMA SECURITY_ANALYTICS;
   CREATE STREAMLIT ITSEC_QUALYS_VALIDATION
       ROOT_LOCATION = '@STREAMLIT_APPS/qualys'
       MAIN_FILE = 'streamlit_app.py'
       QUERY_WAREHOUSE = 'DEV_REPORTING_WH';
   ```

2. **Upload Files**
   - Upload `streamlit_app.py` to Snowsight
   - Upload `environment.yml` for dependencies

3. **Grant Access**
   ```sql
   GRANT USAGE ON STREAMLIT ITSEC_QUALYS_VALIDATION
       TO ROLE DEV_ANALYST;
   ```

### Local Development

```bash
# Install dependencies
conda env create -f environment.yml
conda activate qualys_validation

# Set environment variables
export SNOWFLAKE_ACCOUNT="your_account"
export SNOWFLAKE_USER="your_user"
export SNOWFLAKE_ROLE="DEV_DEVELOPER"
export SNOWFLAKE_WAREHOUSE="DEV_WH"

# Run locally
streamlit run streamlit_app.py
```

## 🎯 Dashboard Tabs

### Tab 1: Vulnerability Overview
- Total vulnerabilities by severity
- Critical CVE count and trends
- Data freshness indicator
- Null value percentages
- Top 10 most common vulnerabilities

### Tab 2: Asset Coverage
- Total assets scanned
- Scan recency distribution
- Assets missing recent scans (>30 days)
- Asset breakdown by OS/platform
- Coverage gaps by business unit

### Tab 3: Patch Compliance
- Overall compliance rate
- Compliance by severity level
- Time-to-patch metrics (SLA tracking)
- Overdue patches by criticality
- Compliance trends (30/60/90 days)

### Tab 4: CVE Analysis
- CVE age distribution
- CVSS score breakdown
- EPSS (Exploit Prediction) scores
- Known exploited vulnerabilities
- CISA KEV catalog matches

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
- Permissions: SELECT on all Qualys views

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
- Critical (CVSS 9.0-10.0)
- High (CVSS 7.0-8.9)
- Medium (CVSS 4.0-6.9)
- Low (CVSS 0.1-3.9)
- Informational

### Auto-Refresh
Dashboard auto-refreshes every 10 minutes when enabled

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
- IP address masking option
- Encrypted connections only

## ⚡ Performance Tips

1. **Use date filters**: Avoid querying all historical scans
2. **Filter by severity**: Focus on Critical/High for faster results
3. **Warehouse sizing**: Use Small warehouse for large datasets
4. **Materialized views**: Leverage pre-aggregated vulnerability summaries

## 🔧 Troubleshooting

### Common Issues

**No vulnerability data showing**
- Verify Qualys API connector is active
- Check last scan: `SELECT MAX(SCAN_DATE) FROM L_QUALYS_SCANS`
- Confirm Snowpipe is running: `SHOW PIPES LIKE '%QUALYS%'`

**Outdated scan data**
- Review Qualys scan schedule
- Check API rate limits
- Verify Snowpipe auto-ingest

**Slow dashboard performance**
- Reduce date range to last 30 days
- Apply severity filters (Critical/High only)
- Check warehouse size and query history

**Missing CVE details**
- Confirm KB article sync is running
- Verify NVD data feed is current
- Check DIM_CVE population

## 📈 Key Metrics Tracked

### Top 13 ITSEC KPIs (Related)
- **Patch Compliance Rate** (KPI #3): % systems with latest patches
- **Vulnerability Remediation Time** (KPI #11): Avg days to fix critical CVEs

### Additional Metrics
- Scan coverage percentage
- Mean time to detect (MTTD) for new CVEs
- Mean time to patch (MTTP)
- Risk score by asset
- Exploitability index

## 📞 Support

- **Data Engineering**: For pipeline and data quality issues
- **Vulnerability Management Team**: For Qualys scanning questions
- **Snowflake Admins**: For access and permission requests

## 📚 Additional Resources

- [Qualys API Documentation](https://www.qualys.com/docs/qualys-api-vmpc-user-guide.pdf)
- [NIST NVD Database](https://nvd.nist.gov/)
- [CISA KEV Catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)
- [Snowflake Streamlit Documentation](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [Vulnerability Data Model](../../03_DOCUMENTATION/02_ERD/ERD_DOCUMENTATION.md)

---

**Version**: 1.0.0
**Last Updated**: October 2025
**Maintained by**: GenericCorp Data Engineering Team
**Status**: ✅ Production
