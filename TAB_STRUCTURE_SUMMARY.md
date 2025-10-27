# Tab Structure Analysis - All 18 Apps

**Date**: 2025-10-25
**Purpose**: Understand common patterns and service-specific tabs across all SECURITY_ANALYTICS apps

---

## Quick Summary

| Metric | Value |
|--------|-------|
| **Total Apps Analyzed** | 18 |
| **Most Common Tab Count** | 6 tabs (10 apps) |
| **Most Common Tab** | "Overview" (7 apps, 39%) |
| **Total Unique Tab Names** | 73 different tabs |
| **Core Tabs** | 1 tab in 30%+ of apps |
| **Service-Specific Tabs** | 68 unique tabs |

---

## Tab Distribution

```
4 tabs: ██                  (2 apps)  - Crowdstrike, Tenable
5 tabs: ██                  (2 apps)  - Cisco_AMP, Qualys
6 tabs: ████████████████████ (10 apps) - Ancon, CybelAngel, Intel_Threats, Leviat,
                                         Proofpoint, SentinelOne, Sophos, Splunk,
                                         Symantec, Trellix
7 tabs: ████████            (4 apps)  - BitSight, ServiceNow, Zerofox, Zscaler
```

**Recommendation**: Use **6 tabs** as standard template (covers 56% of apps)

---

## Top 10 Most Common Tabs

| Rank | Tab Name | Usage | Percentage |
|------|----------|-------|------------|
| 1 | Overview | 7/18 | 39% ========== |
| 2 | Trends | 5/18 | 28% ======= |
| 3 | Security Alerts | 4/18 | 22% ====== |
| 4 | OPCO Analysis | 4/18 | 22% ====== |
| 5 | Endpoint Health | 3/18 | 17% ==== |
| 6 | Data Quality | 3/18 | 17% ==== |
| 7 | Threat Analysis | 3/18 | 17% ==== |
| 8 | Executive Dashboard | 3/18 | 17% ==== |
| 9 | User Activity | 2/18 | 11% === |
| 10 | Coverage Overview | 2/18 | 11% === |

---

## All 18 Apps - Complete Tab Breakdown

### EDR Services (5 apps)

#### Trellix (6 tabs)
1. EDR Coverage
2. Agent Health
3. Communication Status
4. AMCore Compliance
5. Security Alerts
6. OPCO Analysis

#### CrowdStrike (4 tabs)
1. Overview
2. Detailed Data
3. Trends
4. Data Quality

#### SentinelOne (6 tabs)
1. Overview
2. Threat Analysis
3. Endpoint Status
4. Trends
5. Threat Hunting
6. Remediation Tracking

#### Sophos (6 tabs)
1. Endpoint Health
2. OS Protection
3. Security Alerts
4. User Activity
5. Trends Analysis
6. Executive Dashboard

#### Symantec (6 tabs)
1. Coverage Overview
2. Endpoint Health
3. High Risk Endpoints
4. Ransomware Protection
5. Threat Analysis
6. OPCO Analysis

---

### SIEM Services (1 app)

#### Splunk (6 tabs)
1. Alert Trends
2. Response Times
3. Resolution Effectiveness
4. Log Coverage
5. Alert Analysis
6. Executive Dashboard

---

### Vulnerability Management (2 apps)

#### Qualys (5 tabs)
1. Vulnerability Analysis
2. Host Compliance
3. Patch Management
4. Scan Coverage
5. Trending & Analytics

#### Tenable (4 tabs)
1. Overview
2. Vulnerability Details
3. Asset Analysis
4. Trends & Metrics

---

### Endpoint Protection (2 apps)

#### Cisco_AMP (5 tabs)
1. Coverage Overview
2. Endpoint Health
3. OS Coverage
4. Version Compliance
5. Trending Analysis

#### Zscaler (7 tabs)
1. Agent Health
2. Threat Analysis
3. Endpoint Risk
4. Coverage & Deployment
5. Security Alerts
6. Threat Trends
7. Executive Dashboard

---

### Identity & Access Management (2 apps)

#### Ancon (6 tabs)
1. Account Compliance
2. Security Alerts
3. Password Analytics
4. User Activity
5. Risk Assessment
6. Settings & Policies

#### Leviat (6 tabs)
1. Overview
2. User Management
3. Security Events
4. Trends
5. Access Analysis
6. Risk Indicators

---

### Email Security (1 app)

#### Proofpoint (6 tabs)
1. Overview
2. Email Threats
3. User Risk Analysis
4. Trends
5. Phishing Campaign Analysis
6. Response Performance

---

### Threat Intelligence (2 apps)

#### CybelAngel (6 tabs)
1. Overview
2. Threat Details
3. Trends
4. Source Analysis
5. Data Leak Analysis
6. Response Metrics

#### Intel_Threats (6 tabs)
1. Asset Performance
2. Data Quality
3. Source Analysis
4. Takedown Effectiveness
5. Monthly Trends
6. OPCO Analysis

---

### Digital Risk Protection (1 app)

#### Zerofox (7 tabs)
1. Asset Exposure
2. Domain Protection
3. Alert Trends
4. Threat Actors
5. Response Performance
6. OPCO Analysis
7. Data Quality

---

### Risk Management (1 app)

#### BitSight (7 tabs)
1. Critical Findings
2. Risk Compliance
3. Risk Trends
4. Risk Vector Analysis
5. Vendor Risk
6. Security Posture
7. Remediation Pipeline

---

### ITSM (1 app)

#### ServiceNow (7 tabs)
1. Overview
2. Incidents
3. Changes
4. CMDB Assets
5. KPIs
6. SLA Compliance
7. Trends & Analytics

---

## Common Tab Categories

### Category 1: Overview & Summary (7 apps use "Overview")
**Purpose**: High-level dashboard with key metrics
**Typical Content**:
- Asset distribution
- Compliance metrics
- Critical findings summary
- OPCO breakdown

**Services using**: CrowdStrike, CybelAngel, Leviat, Proofpoint, SentinelOne, Tenable, ServiceNow

---

### Category 2: Trends & Analytics (5 apps)
**Purpose**: Historical analysis and trending
**Typical Content**:
- Time-series charts
- Period-over-period comparisons
- Trending KPIs
- Forecast data

**Services using**: CrowdStrike, CybelAngel, Leviat, Tenable, ServiceNow

---

### Category 3: Security Alerts (4 apps)
**Purpose**: Active alerts and incidents
**Typical Content**:
- Alert volumes by severity
- Active vs resolved alerts
- Response times
- Alert aging

**Services using**: Ancon, Sophos, Trellix, Zscaler

---

### Category 4: OPCO Analysis (4 apps)
**Purpose**: Organization-level performance
**Typical Content**:
- OPCO comparison
- Coverage by OPCO
- Compliance by OPCO
- Issues by OPCO

**Services using**: Intel_Threats, Symantec, Trellix, Zerofox

---

### Category 5: Health & Status (6 apps use variations)
**Purpose**: Asset/endpoint health monitoring
**Tab Names**: "Endpoint Health", "Agent Health", "Endpoint Status"
**Typical Content**:
- Active vs inactive assets
- Health scores
- OS versions
- Update compliance

**Services using**: Cisco_AMP, Sophos, Symantec, Trellix, SentinelOne, Zscaler

---

### Category 6: Threat Analysis (3 apps)
**Purpose**: Threat intelligence and analysis
**Typical Content**:
- Threat types
- Threat actors
- Attack vectors
- Threat trends

**Services using**: SentinelOne, Symantec, Zscaler

---

### Category 7: Data Quality (3 apps)
**Purpose**: Data completeness and quality metrics
**Typical Content**:
- Data coverage
- Missing data
- Data freshness
- Source reliability

**Services using**: CrowdStrike, Intel_Threats, Zerofox

---

### Category 8: Executive Dashboard/Report (3 apps)
**Purpose**: C-level summary reporting
**Typical Content**:
- Executive summary
- Key recommendations
- Strategic metrics
- Exportable reports

**Services using**: Sophos, Splunk, Zscaler

---

## Recommended Template Structure

Based on this analysis, the recommended template should have **6 tabs**:

### Standard 6-Tab Template

```
Tab 1: Overview (Core - 39% of apps)
├── Executive metrics
├── Asset distribution
└── Compliance summary

Tab 2: Trends (Common - 28% of apps)
├── Time-series data
├── Historical analysis
└── Period comparisons

Tab 3: Security Alerts (Common - 22% of apps)
├── Alert volumes
├── Severity breakdown
└── Response metrics

Tab 4: OPCO Analysis (Common - 22% of apps)
├── OPCO comparison
├── Coverage by OPCO
└── Performance by OPCO

Tab 5: [Service-Specific Analysis]
├── Customized for service type
├── E.g., "Vulnerability Analysis", "Email Threats", "Asset Performance"
└── Service-specific KPIs

Tab 6: Executive Report (Common - 17% of apps)
├── Summary report
├── Recommendations
└── Export functionality
```

---

## Service Type Recommendations

### EDR Services
**Recommended Tabs** (6):
1. Coverage Overview
2. Agent/Endpoint Health
3. Security Alerts
4. Threat Analysis
5. OPCO Analysis
6. Executive Dashboard

**Example**: Trellix, SentinelOne, Sophos

---

### SIEM Services
**Recommended Tabs** (6):
1. Alert Trends
2. Response Times
3. Resolution Effectiveness
4. Log Coverage
5. Alert Analysis
6. Executive Dashboard

**Example**: Splunk

---

### Vulnerability Management
**Recommended Tabs** (5-6):
1. Overview
2. Vulnerability Analysis
3. Host Compliance
4. Patch Management
5. Scan Coverage
6. Trending & Analytics (optional)

**Example**: Qualys, Tenable

---

### Identity & Access Management
**Recommended Tabs** (6):
1. Overview
2. Account/User Management
3. Security Events/Alerts
4. Access Analysis
5. Risk Assessment
6. Trends

**Example**: Ancon, Leviat

---

### Risk Management
**Recommended Tabs** (6-7):
1. Overview/Critical Findings
2. Risk Compliance
3. Risk Trends
4. Risk Analysis
5. Vendor Risk (if applicable)
6. Remediation Pipeline
7. Security Posture (optional)

**Example**: BitSight

---

## Key Insights

### 1. Standardization Opportunities
- **39% of apps** use "Overview" → Should be standard Tab 1
- **28% of apps** use "Trends" → Should be standard Tab 2
- **22% of apps** use "OPCO Analysis" → Should be standard for multi-OPCO services

### 2. Service-Specific Patterns
- **EDR services** focus on: Coverage, Health, Alerts
- **VM services** focus on: Vulnerabilities, Compliance, Patches
- **IAM services** focus on: Users, Access, Risk
- **Risk services** focus on: Findings, Compliance, Remediation

### 3. Flexibility Needed
- **68 unique tabs** show high customization
- Only **1 tab** (Overview) appears in >30% of apps
- Template must allow easy customization

### 4. Optimal Tab Count
- **6 tabs** is ideal (used by 56% of apps)
- Allows for:
  - 3 standard tabs (Overview, Trends, OPCO)
  - 2-3 service-specific tabs
  - 1 executive/report tab

---

## Template Files Created

1. **[STREAMLIT_APP_TEMPLATE.py](STREAMLIT_APP_TEMPLATE.py)**
   - Complete working template
   - 6 standard tabs
   - Fully customizable
   - Production-ready with dummy objects

2. **[STREAMLIT_TEMPLATE_GUIDE.md](STREAMLIT_TEMPLATE_GUIDE.md)**
   - Comprehensive guide
   - Customization instructions
   - Best practices
   - Examples by service type

3. **[TAB_STRUCTURE_SUMMARY.md](TAB_STRUCTURE_SUMMARY.md)** (this file)
   - Analysis results
   - Tab patterns
   - Recommendations

---

## Next Steps

1. ✅ Use template for new services
2. ✅ Standardize existing apps (optional)
3. ✅ Customize tabs per service type
4. ✅ Deploy to Snowflake
5. ✅ Collect user feedback
6. ✅ Iterate on template

---

**Last Updated**: 2025-10-25
**Analysis Based On**: 18 production apps in `13_STREAMLIT_COMPLETE/`
**Status**: Complete
