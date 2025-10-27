# Threat Intelligence Data Validation Dashboard

## 🎯 Cyber Threat Intelligence Platform

A Streamlit-based data validation dashboard for threat intelligence feeds, indicators of compromise (IOCs), and threat actor tracking.

## 📋 Overview

This dashboard provides real-time data quality validation and insights for threat intelligence data aggregated from multiple sources into Snowflake. Designed for data engineers and threat analysts to ensure data completeness, freshness, and quality before formal BI visualization.

### Key Use Cases
- Validate threat intelligence pipeline integrity
- Monitor IOC feed freshness and coverage
- Analyze threat actor campaigns
- Assess intelligence source reliability
- Quick ad-hoc threat hunting insights

## ✨ Features

### Data Quality Validation
- **Feed Freshness**: Last update timestamp per intelligence source
- **Completeness Checks**: IOC counts, missing field analysis
- **Duplicate Detection**: Identify duplicate indicators across feeds
- **Source Validation**: Feed health and reliability scoring

### Threat Intelligence Metrics
- **IOC Counts**: By type (IP, domain, hash, URL, email)
- **Threat Actors**: Active campaigns and TTPs
- **MITRE ATT&CK**: Technique and tactic mapping
- **Confidence Scores**: Intelligence reliability assessment

### Interactive Visualizations
- IOC type distribution
- Threat actor activity timeline
- Confidence score distribution
- MITRE ATT&CK heatmap
- Geographic threat distribution
- TLP (Traffic Light Protocol) breakdown

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
│  └─ VW_THREAT_INTEL_*        │
└────────────┬─────────────────┘
             │
┌────────────▼─────────────────┐
│  DEV_TRANSFORMATION.SECURITY_ANALYTICS │
│  └─ FACT_THREAT_INTEL        │
│  └─ DIM_THREAT_ACTOR         │
│  └─ DIM_IOC                  │
│  └─ DIM_MITRE_ATTACK         │
└────────────┬─────────────────┘
             │
┌────────────▼─────────────────┐
│  DEV_LANDING.SECURITY_ANALYTICS        │
│  └─ L_THREAT_INTEL_FEEDS     │
│  └─ L_IOC_INDICATORS         │
│  └─ L_THREAT_ACTORS          │
│  └─ L_MITRE_ATTACK_DATA      │
└──────────────────────────────┘
```

## 📊 Data Sources

### Primary Tables/Views
```sql
-- Landing Layer
DEV_LANDING.SECURITY_ANALYTICS.L_THREAT_INTEL_FEEDS
DEV_LANDING.SECURITY_ANALYTICS.L_IOC_INDICATORS
DEV_LANDING.SECURITY_ANALYTICS.L_THREAT_ACTORS
DEV_LANDING.SECURITY_ANALYTICS.L_MITRE_ATTACK_DATA

-- Transformation Layer
DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_THREAT_INTEL
DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_THREAT_ACTOR
DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_IOC
DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_MITRE_ATTACK

-- Reporting Layer
DEV_REPORTING.SECURITY_ANALYTICS.VW_THREAT_INTEL_SUMMARY
DEV_REPORTING.SECURITY_ANALYTICS.VW_IOC_ANALYSIS
DEV_REPORTING.SECURITY_ANALYTICS.VW_THREAT_ACTOR_TRACKING
```

### Threat Intelligence Sources
- **Commercial Feeds**: Recorded Future, Mandiant, CrowdStrike Intel
- **Open Source**: AlienVault OTX, MISP, Abuse.ch
- **Government**: CISA, FBI InfraGard, MS-ISAC
- **Industry**: FS-ISAC, H-ISAC (sector-specific)

### Data Refresh Schedule
- **Real-time Feeds**: Via Snowpipe (< 5 min latency)
- **Daily Feeds**: Batch at 3 AM UTC
- **Weekly Reports**: Sundays at midnight
- **MITRE ATT&CK**: Quarterly updates

## 🚀 Deployment

### Snowflake Streamlit (Recommended)

1. **Create Streamlit App in Snowsight**
   ```sql
   USE DATABASE DEV_REPORTING;
   USE SCHEMA SECURITY_ANALYTICS;
   CREATE STREAMLIT ITSEC_THREAT_INTEL_VALIDATION
       ROOT_LOCATION = '@STREAMLIT_APPS/intel_threats'
       MAIN_FILE = 'streamlit_app.py'
       QUERY_WAREHOUSE = 'DEV_REPORTING_WH';
   ```

2. **Upload Files**
   - Upload `streamlit_app.py` to Snowsight
   - Upload `environment.yml` for dependencies

3. **Grant Access**
   ```sql
   GRANT USAGE ON STREAMLIT ITSEC_THREAT_INTEL_VALIDATION
       TO ROLE DEV_ANALYST;
   ```

### Local Development

```bash
# Install dependencies
conda env create -f environment.yml
conda activate intel_threats_validation

# Set environment variables
export SNOWFLAKE_ACCOUNT="your_account"
export SNOWFLAKE_USER="your_user"
export SNOWFLAKE_ROLE="DEV_DEVELOPER"
export SNOWFLAKE_WAREHOUSE="DEV_WH"

# Run locally
streamlit run streamlit_app.py
```

## 🎯 Dashboard Tabs

### Tab 1: IOC Overview
- Total IOCs by type (IP, domain, hash, URL, email)
- New IOCs (last 24 hours)
- Feed freshness status
- Confidence score distribution
- TLP classification breakdown

### Tab 2: Threat Actor Tracking
- Active threat actors (campaigns in last 90 days)
- Threat actor TTPs (Tactics, Techniques, Procedures)
- Targeted industries
- Geographic attribution
- Motivation analysis (financial, espionage, hacktivism)

### Tab 3: MITRE ATT&CK Mapping
- Technique coverage heatmap
- Tactic distribution
- Top 10 observed techniques
- Detection coverage gaps
- Sub-technique analysis

### Tab 4: Feed Health & Quality
- Feed status (active/inactive)
- Update frequency compliance
- Data quality scores by source
- False positive rates
- Source reliability rankings

### Tab 5: Threat Hunting
- IOC search and pivot
- Timeline of related indicators
- Enrichment data lookup
- Cross-reference with internal detections
- Export IOCs for blocking

## 📋 Prerequisites

### Snowflake Access
- Role: `DEV_DEVELOPER` or `DEV_ANALYST`
- Warehouse: `DEV_REPORTING_WH`
- Permissions: SELECT on all threat intel views

### Dependencies (from environment.yml)
- streamlit >= 1.28.0
- snowflake-snowpark-python >= 1.9.0
- pandas >= 2.0.0
- plotly >= 5.17.0
- altair >= 5.0.0

## ⚙️ Configuration

### Date Range Filters
Default: Last 30 days (configurable via sidebar)

### IOC Type Filters
- IPv4 addresses
- IPv6 addresses
- Domain names
- URLs
- File hashes (MD5, SHA1, SHA256)
- Email addresses
- CVE identifiers

### Confidence Filters
- High (80-100)
- Medium (50-79)
- Low (0-49)

### TLP Classification
- TLP:RED (Confidential)
- TLP:AMBER (Limited distribution)
- TLP:GREEN (Community)
- TLP:WHITE (Public)

### Auto-Refresh
Dashboard auto-refreshes every 15 minutes when enabled

## 🔐 Security

### Authentication
- Uses Snowflake session context (no credentials in code)
- Role-based access control via Snowflake
- Audit logging for all queries

### Data Handling
- TLP restrictions enforced
- No IOCs cached locally
- Encrypted connections only
- Export controls for sensitive intel

### Access Controls
- TLP:RED visible to SOC analysts only
- TLP:AMBER limited to security team
- Audit trail for IOC searches

## ⚡ Performance Tips

1. **Filter by IOC type**: Focus on specific indicator types
2. **Use date ranges**: Last 30 days for most analysis
3. **Filter by confidence**: High confidence only for faster queries
4. **Warehouse sizing**: Use Small for large IOC datasets
5. **Leverage views**: Pre-aggregated threat summaries

## 🔧 Troubleshooting

### Common Issues

**Missing IOC updates**
- Check feed API connectivity
- Verify API keys/tokens are valid
- Review Snowpipe status for feeds
- Confirm feed provider is operational

**Outdated MITRE ATT&CK data**
- Verify quarterly refresh schedule
- Check MITRE ATT&CK GitHub repo for updates
- Review transformation logic for new techniques

**Low confidence scores**
- Review source reliability weights
- Check for missing enrichment data
- Verify correlation logic
- Confirm validation rules

**Duplicate IOCs across feeds**
- Review deduplication logic
- Check source priority rankings
- Verify indicator normalization
- Confirm merge rules

## 📈 Key Metrics Tracked

### Intelligence Effectiveness
- IOC detection rate (% matched in internal logs)
- Time-to-block (IOC published → blocked)
- False positive rate
- Threat actor prediction accuracy

### Feed Performance
- Update frequency compliance
- Data completeness score
- Unique IOCs per feed
- Source reliability score

## 📞 Support

- **Data Engineering**: For pipeline and data quality issues
- **Threat Intelligence Team**: For feed configuration and analysis questions
- **Snowflake Admins**: For access and permission requests

## 📚 Additional Resources

- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [STIX/TAXII Standards](https://oasis-open.github.io/cti-documentation/)
- [TLP Protocol](https://www.cisa.gov/news-events/news/traffic-light-protocol-tlp-definitions-and-usage)
- [Snowflake Streamlit Documentation](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [Threat Intelligence Data Model](../../03_DOCUMENTATION/02_ERD/ERD_DOCUMENTATION.md)

---

**Version**: 1.0.0
**Last Updated**: October 2025
**Maintained by**: GenericCorp Data Engineering Team
**Status**: ✅ Production
