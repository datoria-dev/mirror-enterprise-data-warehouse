# Streamlit Apps for Data Validation

This folder contains Streamlit applications deployed in Snowflake for quick data validation, quality checks, and rapid insights. These apps are designed as lightweight dashboards for data engineers and analysts to validate data without requiring full BI tool deployments.

## Purpose

- **Data Validation**: Quick checks on data quality and completeness
- **Rapid Insights**: Simple dashboards for immediate analysis
- **Quality Assurance**: Pre-BI validation before formal visualization development
- **Ad-hoc Analysis**: Fast exploration of security data from multiple sources

## Available Apps

### Security Tools (18 Apps)

#### SIEM & Monitoring (2 Apps)
1. **[Splunk](Splunk/)** - SIEM data validation and event analysis
2. **[Intel_Threats](Intel_Threats/)** - Threat intelligence aggregation

#### Endpoint Protection (6 Apps)
3. **[Crowdstrike](Crowdstrike/)** - EDR event validation
4. **[SentinelOne](SentinelOne/)** - Endpoint detection and response
5. **[Sophos](Sophos/)** - Endpoint protection validation
6. **[Symantec](Symantec/)** - Endpoint security data
7. **[Trellix](Trellix/)** - EDR and threat detection data
8. **[Cisco_AMP](Cisco_AMP/)** - Advanced malware protection data

#### External Threats & Risk (3 Apps)
9. **[CybelAngel](CybelAngel/)** - External threat monitoring and data leak detection
10. **[Zerofox](Zerofox/)** - Digital risk protection and external intelligence
11. **[BitSight](BitSight/)** - Security ratings and risk metrics

#### Vulnerability Management (2 Apps)
12. **[Qualys](Qualys/)** - Vulnerability management validation
13. **[Tenable](Tenable/)** - Vulnerability scanning and assessment

#### Email Security (1 App)
14. **[Proofpoint](Proofpoint/)** - Email threat detection and protection

#### Cloud & Network Security (1 App)
15. **[Zscaler](Zscaler/)** - Cloud security and web gateway metrics

#### Identity & Access Management (2 Apps)
16. **[Leviat](Leviat/)** - IAM platform monitoring
17. **[ServiceNow](ServiceNow/)** - ITSM and CMDB management

#### Security Analytics (1 App)
18. **[Ancon](Ancon/)** - Security analytics validation

## App Structure

Each app folder contains:

```
AppName/
├── streamlit_app.py    # Main Streamlit application code
├── README.md           # App-specific documentation
└── environment.yml     # Snowflake environment dependencies
```

## Deployment

### Prerequisites
- Snowflake account with Streamlit enabled
- DEV_DEVELOPER or higher role
- Access to DEV_LANDING, DEV_TRANSFORMATION, DEV_REPORTING databases

### Deploy to Snowflake

1. **Via Snowsight UI**:
   - Navigate to Streamlit section in Snowsight
   - Click "Create Streamlit App"
   - Copy content from `streamlit_app.py`
   - Upload `environment.yml` for dependencies
   - Deploy to DEV_REPORTING database

2. **Via SnowCLI** (if available):
   ```bash
   snow streamlit deploy --name APP_NAME --file streamlit_app.py
   ```

### Naming Convention

Apps should be named following this pattern:
```
ITSEC_[SOURCE]_VALIDATION
```

Examples:
- `ITSEC_SPLUNK_VALIDATION`
- `ITSEC_CROWDSTRIKE_VALIDATION`
- `ITSEC_QUALYS_VALIDATION`

## Common Features

All apps typically include:

- **Data Quality Metrics**: Row counts, null checks, duplicate detection
- **Freshness Indicators**: Last load timestamp, data latency
- **Completeness Checks**: Coverage across expected fields
- **Quick Statistics**: Min/max/avg for key metrics
- **Trend Visualizations**: Simple time-series charts
- **Filter Controls**: Date range, severity, status filters
- **Export Options**: Download results as CSV

## Best Practices

### Performance
- Use `@st.cache_data` for expensive queries
- Limit default date ranges (last 7-30 days)
- Implement row limits for large datasets (10K-50K max)
- Use aggregated views where possible

### Security
- Never hardcode credentials in apps
- Use Snowflake session context for authentication
- Restrict app access via Snowflake roles
- Log sensitive queries for audit

### Code Quality
- Add docstrings to all functions
- Use type hints for parameters
- Include error handling for queries
- Provide user-friendly error messages

### User Experience
- Add app description in sidebar
- Include refresh timestamp
- Show query execution time
- Provide help tooltips for metrics

## Example App Template

```python
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# App configuration
st.set_page_config(
    page_title="ITSEC Data Validation",
    page_icon="🔒",
    layout="wide"
)

# Title and description
st.title("🔒 [SOURCE] Data Validation Dashboard")
st.markdown("Quick data quality checks and validation metrics")

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    date_range = st.date_input(
        "Date Range",
        value=(datetime.now() - timedelta(days=7), datetime.now())
    )

# Main content
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Records", "1.2M", "+5%")

with col2:
    st.metric("Data Freshness", "2 hours", "-1h")

with col3:
    st.metric("Quality Score", "98%", "+2%")

# Data quality checks
st.subheader("Data Quality Metrics")

# Your validation logic here
df = session.sql("""
    SELECT
        COUNT(*) as total_records,
        COUNT(DISTINCT field_id) as unique_ids,
        SUM(CASE WHEN field IS NULL THEN 1 ELSE 0 END) as null_count
    FROM DEV_LANDING.SECURITY_ANALYTICS.L_SOURCE_TABLE
    WHERE DATE >= DATEADD(day, -7, CURRENT_DATE())
""").to_pandas()

st.dataframe(df)

# Footer
st.markdown("---")
st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
```

## Updating Apps

When modifying an existing app:

1. Test changes locally first (if possible with Streamlit OSS)
2. Update version number in README.md
3. Document changes in app-specific changelog
4. Deploy to Snowflake development environment
5. Validate functionality before promoting to production

## Troubleshooting

### Common Issues

**App won't load**
- Check environment.yml dependencies
- Verify database/schema permissions
- Review Snowflake query history for errors

**Slow performance**
- Add caching decorators
- Reduce default date ranges
- Optimize SQL queries
- Use materialized views

**Permission errors**
- Confirm role has SELECT on required tables
- Check warehouse access
- Verify schema grants

## Support

For issues or feature requests:
- Data Engineering team for app development
- Snowflake admins for deployment issues
- Security teams for data source questions

---

## Version History

### v2.0 (Current - 2025-10-24)
- Expanded to 18 security tool validation apps
- Added 6 new services: CybelAngel, Leviat, Proofpoint, SentinelOne, ServiceNow, Tenable
- Implemented modular architecture with common components
- Enhanced apps with advanced analytics and risk indicators
- Organized apps by security category

### v1.0 (2025-10-08)
- Initial deployment of 12 security tool validation apps
- Standard template established
- Common patterns documented

---

**Last Updated**: 2025-10-24
**Maintained By**: Data Engineering Team
**Environment**: Snowflake Streamlit in DEV_REPORTING
**Total Apps**: 18 Security Tools
