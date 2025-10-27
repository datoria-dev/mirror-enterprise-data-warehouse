# Power BI Dashboards - Source & Reference

## 📊 Purpose

This folder contains Power BI dashboards (.pbix files) that serve as data sources, requirements, or reference materials for the SECURITY_ANALYTICS Snowflake project. These dashboards represent existing reporting solutions that inform the design and requirements of the Snowflake data warehouse.

## 🎯 Use Cases

### Requirements Gathering
- Understand existing KPIs and metrics
- Identify required data elements
- Document current visualizations
- Map dashboard fields to Snowflake tables

### Data Model Reference
- Review relationships and joins
- Identify calculated measures (DAX)
- Document aggregation logic
- Understand grain and granularity

### Migration Planning
- Prioritize dashboards for Snowflake migration
- Identify dependencies on source systems
- Plan data pipeline requirements
- Design replacement views in Snowflake

### Quality Assurance
- Validate Snowflake data against Power BI
- Compare metrics before/after migration
- Test report accuracy
- Ensure business continuity

## 📁 Folder Structure

```
08_POWERBI_DASHBOARDS/
├── 01_Executive_Dashboards/    # C-level and executive reports
├── 02_Security_Operations/     # SOC and security team dashboards
├── 03_Compliance/              # Compliance and audit reports
├── 04_Vulnerability_Mgmt/      # Qualys, patch management
├── 05_Endpoint_Security/       # EDR, antivirus dashboards
├── 06_Identity_Access/         # IAM, AD, privileged access
├── 07_SIEM_Analytics/          # Splunk, log analytics
├── 08_Archived/                # Deprecated or legacy dashboards
└── README.md                   # This file
```

## 📋 Dashboard Inventory Template

For each dashboard, document:

| Field | Description |
|-------|-------------|
| **Dashboard Name** | Official name in Power BI |
| **Owner** | Business owner/team |
| **Update Frequency** | Daily, weekly, monthly |
| **Data Sources** | SQL Server, Excel, SharePoint, etc. |
| **Key Metrics** | Top 5 metrics displayed |
| **Users** | Who uses this dashboard |
| **Migration Priority** | High/Medium/Low |
| **Snowflake Views** | Which views will replace this |

## 🔄 Migration Process

### Phase 1: Analysis
1. Extract data model from .pbix file
2. Document DAX measures and calculations
3. Identify source queries and tables
4. Map to Snowflake schema (DEV_REPORTING)

### Phase 2: Design
1. Create equivalent views in Snowflake
2. Replicate DAX logic in SQL
3. Optimize for performance
4. Add proper documentation

### Phase 3: Testing
1. Compare metric values side-by-side
2. Validate calculations match exactly
3. Test edge cases and filters
4. Performance testing

### Phase 4: Deployment
1. Publish new Power BI reports connected to Snowflake
2. User acceptance testing
3. Phased rollout
4. Decommission old dashboards

## 🛠️ Tools & Utilities

### Extract Data Model
Use DAX Studio or Power BI external tools to extract:
- Table schemas
- Relationships
- Measures (DAX code)
- Calculated columns

### Documentation
```powershell
# Export Power BI metadata
Install-Module -Name MicrosoftPowerBIMgmt
Connect-PowerBIServiceAccount
Get-PowerBIReport -WorkspaceId <workspace-id> | Export-Csv "dashboard_inventory.csv"
```

### Compare Metrics
Create comparison queries in Snowflake:
```sql
-- Compare values between Power BI and Snowflake
SELECT
    'Power BI' as SOURCE,
    COUNT(*) as RECORD_COUNT,
    SUM(METRIC_VALUE) as TOTAL_VALUE
FROM POWER_BI_EXTRACT
UNION ALL
SELECT
    'Snowflake' as SOURCE,
    COUNT(*) as RECORD_COUNT,
    SUM(METRIC_VALUE) as TOTAL_VALUE
FROM DEV_REPORTING.SECURITY_ANALYTICS.VW_EQUIVALENT_VIEW;
```

## 📊 Common Dashboard Types

### Executive Dashboards
- **Top 13 ITSEC KPIs**: NIST CSF 2.0 metrics
- **Security Scorecard**: Overall security posture
- **Risk Dashboard**: Enterprise risk view
- **Compliance Overview**: Regulatory compliance status

### Operational Dashboards
- **SOC Dashboard**: Real-time security operations
- **Vulnerability Management**: Patch compliance, CVE tracking
- **Endpoint Health**: Agent status, malware detections
- **Identity & Access**: User accounts, privileged access

### Analytical Dashboards
- **Threat Intelligence**: IOCs, threat actors
- **Incident Analysis**: MTTR, MTTD, incident trends
- **Asset Inventory**: Device compliance, coverage gaps
- **Trend Analysis**: Historical security metrics

## 🔐 Security & Access

### Sensitive Data
- Power BI files may contain sensitive data
- Do not commit .pbix files to public repositories
- Store in secure locations only
- Remove data before sharing for documentation

### Access Control
- Limit access to authorized personnel
- Use role-based permissions
- Audit who accesses dashboard files
- Encrypt files at rest

## 📈 Metrics Mapping

### Example: Patch Compliance Dashboard

| Power BI Metric | DAX Formula | Snowflake View | SQL Logic |
|-----------------|-------------|----------------|-----------|
| Patch Compliance Rate | `DIVIDE([Compliant], [Total])` | `VW_PATCH_COMPLIANCE` | `COMPLIANT_HOSTS / TOTAL_HOSTS` |
| Critical Patches Missing | `COUNTROWS(FILTER(...))` | `VW_CRITICAL_PATCHES` | `COUNT(*) WHERE SEVERITY='CRITICAL' AND STATUS='MISSING'` |
| Mean Time to Patch | `AVERAGE([Days_to_Patch])` | `VW_PATCH_METRICS` | `AVG(DATEDIFF(day, PUBLISHED_DATE, PATCHED_DATE))` |

## 🔧 Troubleshooting

### Cannot Open .pbix File
- Ensure Power BI Desktop is installed
- Check file is not corrupted
- Verify file permissions
- Try "Recover Unsaved Files" in Power BI

### Data Sources Not Loading
- Update data source credentials
- Check connection strings
- Verify source system availability
- Review gateway configuration (if applicable)

### Performance Issues
- Large .pbix files (>100MB)
- Too many visuals on one page
- Inefficient DAX measures
- Missing aggregations

## 📚 References

### Power BI Documentation
- [Power BI Desktop](https://powerbi.microsoft.com/desktop/)
- [DAX Reference](https://dax.guide/)
- [Best Practices](https://docs.microsoft.com/en-us/power-bi/guidance/)

### Migration Resources
- [Power BI to Snowflake Migration Guide](https://www.snowflake.com/blog/power-bi-snowflake-integration/)
- [Snowflake Connector for Power BI](https://docs.snowflake.com/en/user-guide/ecosystem-powerbi)
- [Performance Optimization](https://docs.snowflake.com/en/user-guide/ui-snowsight-visualizations-powerbi)

### Internal Documentation
- [ERD Documentation](../03_DOCUMENTATION/02_ERD/ERD_DOCUMENTATION.md)
- [Reporting Views](../01_SQL_SCRIPTS/02_Base_Implementation/)
- [Top 13 Metrics](../01_SQL_SCRIPTS/03_Enhancements/EXECUTE_4_ENHANCEMENTS_WORKING.sql)

## 📝 Change Log

### Recommended Practices
1. **Version Control**: Name files with version numbers (v1.0, v2.0)
2. **Backup**: Keep copies before major changes
3. **Documentation**: Update README when adding new dashboards
4. **Testing**: Test before distributing to users

### File Naming Convention
```
[Category]_[Dashboard_Name]_v[Version]_[Date].pbix

Examples:
- Executive_Top13_KPIs_v1.2_20251008.pbix
- SOC_RealTime_Alerts_v2.0_20251001.pbix
- Compliance_Audit_Report_v1.0_20250915.pbix
```

## 🤝 Support

### Questions About Dashboards
- **Business Questions**: Contact dashboard owner
- **Technical Issues**: Contact BI team
- **Data Quality**: Contact data engineering team

### Migration Support
- **Snowflake Design**: Data engineering team
- **Power BI Development**: BI team
- **Testing & Validation**: QA team

---

## 📊 Quick Start

### Add a New Dashboard

1. **Copy .pbix file** to appropriate subfolder
2. **Document in README** (this file)
3. **Extract metadata** using DAX Studio
4. **Map to Snowflake** tables/views
5. **Create migration ticket** if needed

### Review Existing Dashboard

1. Open .pbix in Power BI Desktop
2. Review data model (Model view)
3. Document measures (DAX formulas)
4. Identify data sources
5. Compare with Snowflake schema

---

**Last Updated**: 2025-10-08
**Maintained By**: GenericCorp Data Engineering & BI Teams
**Status**: Active - Reference Material
