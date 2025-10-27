# SECURITY_ANALYTICS Metrics Feasibility Analysis Report

**Project**: GenericCorp Cyber Performance Metrics Implementation
**Document**: Metrics Dictionary v0.6 Analysis
**Date**: 2025-10-07
**Analyst**: Data Engineering Team
**Status**: Comprehensive Feasibility Assessment

---

## Executive Summary

This report analyzes the **37 cybersecurity metrics** defined in the Metrics Dictionary v0.6 against the current SECURITY_ANALYTICS data warehouse capabilities. The analysis covers the **"Top 13" executive metrics** plus 24 additional operational metrics, evaluating data availability, calculation feasibility, and implementation requirements.

### Quick Findings

| Category | Count | Percentage |
|----------|-------|------------|
| **✅ Fully Feasible (Data Available)** | 9 metrics | 24% |
| **🟡 Partially Feasible (Data Gaps)** | 8 metrics | 22% |
| **🔴 Not Feasible (Missing Data)** | 7 metrics | 19% |
| **⏳ Pending Integration** | 13 metrics | 35% |
| **Total Metrics Analyzed** | **37 metrics** | **100%** |

### Critical Gaps Identified

1. **RSA Archer Integration**: 0% - No GRC data in Snowflake
2. **MetaCompliance Integration**: 0% - No awareness training data
3. **ServiceNow Integration**: 0% - No incident/ticket data
4. **Ransomware Event Tracking**: Missing event classification
5. **Asset Inventory**: Incomplete SOX designation

---

## Table of Contents

1. [Top 13 Executive Metrics - Detailed Analysis](#top-13-executive-metrics)
2. [Additional 24 Operational Metrics](#additional-operational-metrics)
3. [Data Availability Matrix](#data-availability-matrix)
4. [Implementation Roadmap](#implementation-roadmap)
5. [Data Quality Considerations](#data-quality-considerations)
6. [Best Practices & Recommendations](#best-practices-recommendations)
7. [SQL Implementation Examples](#sql-implementation-examples)

---

## Top 13 Executive Metrics - Detailed Analysis

### Metric #1: Cyber-Maturity Score

**NIST CSF**: GV.IM (Govern – Improve)
**Target**: ≥ Level 3 (≥ L4 for Govern)
**Primary Data Source**: RSA Archer › Maturity Module

#### Current Status: 🔴 **NOT FEASIBLE**

**Data Availability**:
- ❌ RSA Archer not integrated with Snowflake
- ❌ No maturity assessment tables exist
- ❌ No historical maturity scores

**What's Needed**:
1. **RSA Archer ETL Pipeline**:
   - Extract maturity assessment data from Archer API
   - Create landing table: `L_ARCHER_MATURITY_ASSESSMENTS`
   - Create transformation table: `DIM_MATURITY_SCORE`

2. **Required Data Fields**:
   ```sql
   -- Minimum required fields
   - ASSESSMENT_ID
   - ASSESSMENT_DATE
   - BUSINESS_UNIT (Division/OpCo)
   - NIST_FUNCTION (Govern, Identify, Protect, Detect, Respond, Recover)
   - MATURITY_LEVEL (0-5 scale)
   - CONTROL_CATEGORY
   - ASSESSOR_NAME
   ```

3. **Calculation Logic**:
   ```sql
   -- Pseudo-code for Cyber-Maturity Score
   SELECT
       AVG(MATURITY_LEVEL) as OVERALL_MATURITY_SCORE,
       ASSESSMENT_DATE,
       BUSINESS_UNIT
   FROM DIM_MATURITY_SCORE
   WHERE ASSESSMENT_DATE >= DATEADD(month, -12, CURRENT_DATE())
   GROUP BY ASSESSMENT_DATE, BUSINESS_UNIT;
   ```

**Estimated Implementation**:
- **Effort**: 40 hours
- **Dependencies**: Archer API access, authentication credentials
- **Priority**: HIGH (Executive KPI #1)

---

### Metric #2: Policy-Exception Rate

**NIST CSF**: GV.PO (Govern – Policy)
**Target**: < 10% open
**Primary Data Source**: RSA Archer › Policy Exceptions

#### Current Status: 🔴 **NOT FEASIBLE**

**Data Availability**:
- ❌ RSA Archer not integrated
- ❌ No policy exception tracking in Snowflake
- ❌ No policy inventory

**What's Needed**:
1. **Archer Policy Module Integration**:
   ```sql
   -- Required tables
   L_ARCHER_POLICIES
   L_ARCHER_POLICY_EXCEPTIONS

   -- Transformation layer
   DIM_POLICY
   FACT_POLICY_EXCEPTIONS
   ```

2. **Required Data Fields**:
   - POLICY_ID, POLICY_NAME, POLICY_CATEGORY
   - EXCEPTION_ID, EXCEPTION_STATUS (Open/Closed)
   - EXCEPTION_REASON, BUSINESS_JUSTIFICATION
   - EXCEPTION_START_DATE, EXCEPTION_EXPIRY_DATE
   - APPROVER, RISK_RATING

3. **Calculation**:
   ```sql
   SELECT
       COUNT(CASE WHEN STATUS = 'Open' THEN 1 END) * 100.0 /
       COUNT(DISTINCT POLICY_ID) as EXCEPTION_RATE_PCT
   FROM FACT_POLICY_EXCEPTIONS
   WHERE EXCEPTION_DATE = CURRENT_DATE();
   ```

**Estimated Implementation**: 32 hours

---

### Metric #3: Third-Party Risk Score

**NIST CSF**: ID.RA (Identify – Risk Assessment)
**Target**: ≤ "Medium"
**Primary Data Source**: RSA Archer › TPRM + BitSight

#### Current Status: 🟡 **PARTIALLY FEASIBLE**

**Data Availability**:
- ✅ **BitSight data EXISTS** in Snowflake (DIM_BITSIGHT_CATEGORIES, FACT_BITSIGHT_FINDINGS)
- ❌ RSA Archer TPRM not integrated
- ⚠️ Vendor criticality classification missing

**What's Available NOW**:
```sql
-- Current BitSight data
SELECT
    COMPANY_NAME,
    RATING,  -- A, B, C, D, F
    RATING_DATE,
    INDUSTRY,
    RISK_VECTORS
FROM FACT_BITSIGHT_FINDINGS
ORDER BY RATING_DATE DESC;
```

**What's Missing**:
1. **Vendor Criticality Classification**: Which vendors are "critical"?
2. **Archer TPRM Data**: Internal risk assessments
3. **Vendor-to-OpCo Mapping**: Which vendors serve which business units?

**Workaround - Interim Solution**:
```sql
-- Use BitSight as primary source until Archer is integrated
CREATE OR REPLACE VIEW VW_THIRD_PARTY_RISK AS
SELECT
    COMPANY_NAME as VENDOR_NAME,
    CASE
        WHEN RATING IN ('D', 'F') THEN 'High'
        WHEN RATING = 'C' THEN 'Medium'
        WHEN RATING IN ('A', 'B') THEN 'Low'
    END as RISK_LEVEL,
    RATING as BITSIGHT_RATING,
    RATING_DATE,
    -- Placeholder for criticality until Archer data available
    NULL as VENDOR_CRITICALITY
FROM FACT_BITSIGHT_FINDINGS
WHERE RATING_DATE = (SELECT MAX(RATING_DATE) FROM FACT_BITSIGHT_FINDINGS);
```

**Full Implementation Needs**:
- Archer TPRM integration (vendor assessments, contracts, SLAs)
- Vendor criticality master data
- Vendor spend/revenue data for business context

**Estimated Implementation**:
- Interim (BitSight only): 8 hours ✅ CAN START NOW
- Full (Archer + BitSight): 48 hours

---

### Metric #4: Days Since Last Ransomware

**NIST CSF**: ID.RM (Identify – Risk Management)
**Target**: Track only
**Primary Data Source**: EDR tools + ServiceNow incidents

#### Current Status: 🟡 **PARTIALLY FEASIBLE**

**Data Availability**:
- ✅ EDR threat data EXISTS (SYMANTEC_THREATS, CROWDSTRIKE, TRELLIX, TREND_MICRO, DEFENDER)
- ❌ ServiceNow incident data NOT integrated
- ⚠️ **CRITICAL GAP**: No "Ransomware" classification in threat tables

**Current Threat Data Structure**:
```sql
-- What we have now
SYMANTEC_THREATS (
    THREAT_ID,
    THREAT_NAME,  -- Generic names like "Trojan.Gen", not "Ransomware"
    ENDPOINT_ID,
    DETECTION_TIME,
    THREAT_SEVERITY,
    STATUS  -- Quarantined, Removed, Active
)
```

**What's Missing**:
1. **Ransomware Classification**: Need to map threat signatures to ransomware families
2. **Confirmed vs. Detected**: Detection ≠ Actual infection
3. **ServiceNow Incident Tagging**: Manual incident classification

**Interim Solution**:
```sql
-- Use threat name pattern matching (NOT RELIABLE)
CREATE OR REPLACE VIEW VW_RANSOMWARE_EVENTS AS
SELECT
    THREAT_ID,
    THREAT_NAME,
    ENDPOINT_ID,
    DETECTION_TIME,
    'EDR_DETECTION' as EVENT_TYPE,
    CASE
        WHEN UPPER(THREAT_NAME) LIKE '%RANSOM%' THEN TRUE
        WHEN UPPER(THREAT_NAME) LIKE '%CRYPTO%' THEN TRUE
        WHEN UPPER(THREAT_NAME) LIKE '%LOCKER%' THEN TRUE
        WHEN UPPER(THREAT_NAME) IN ('WANNACRY', 'RYUK', 'MAZE', 'REVIL') THEN TRUE
        ELSE FALSE
    END as IS_RANSOMWARE
FROM (
    SELECT * FROM SYMANTEC_THREATS
    UNION ALL
    SELECT * FROM CROWDSTRIKE
    UNION ALL
    SELECT * FROM TRELLIX
    -- ... other EDR sources
)
WHERE IS_RANSOMWARE = TRUE;

-- Calculate Days Since Last Ransomware
SELECT
    DATEDIFF('day', MAX(DETECTION_TIME), CURRENT_DATE()) as DAYS_SINCE_LAST_RANSOMWARE,
    MAX(DETECTION_TIME) as LAST_RANSOMWARE_DATE,
    COUNT(*) as TOTAL_RANSOMWARE_EVENTS_LAST_12M
FROM VW_RANSOMWARE_EVENTS
WHERE DETECTION_TIME >= DATEADD(month, -12, CURRENT_DATE());
```

**Recommended Approach**:
1. **Short-term**: Implement pattern matching with known ransomware families
2. **Medium-term**: Integrate ServiceNow for confirmed incidents
3. **Long-term**: Implement threat intelligence feed for real-time ransomware classification

**Estimated Implementation**:
- Interim (pattern matching): 16 hours ⚠️ **LOW ACCURACY**
- Full (ServiceNow + Threat Intel): 56 hours

---

### Metric #5: EDR Coverage – All Systems

**NIST CSF**: PR.PT (Protect – Technology)
**Target**: ≥ 98%
**Primary Data Source**: Cisco AMP, SentinelOne, Trellix, Trend Micro, Symantec, Defender, CrowdStrike

#### Current Status: ✅ **FULLY FEASIBLE**

**Data Availability**:
- ✅ EDR agent data EXISTS across 7 platforms
- ✅ Tables: CISCO_AMP, SENTINELONE, TRELLIX, SYMANTEC_THREATS, DEFENDER, CROWDSTRIKE, TREND_MICRO
- ⚠️ **GAP**: Missing complete asset inventory (denominator)

**Current Capability**:
```sql
-- Numerator: Assets with EDR (EXISTS)
SELECT COUNT(DISTINCT ENDPOINT_ID) as EDR_PROTECTED_ASSETS
FROM (
    SELECT ENDPOINT_ID FROM CISCO_AMP WHERE AGENT_STATUS = 'Healthy'
    UNION
    SELECT ENDPOINT_ID FROM SENTINELONE WHERE AGENT_STATUS = 'Active'
    UNION
    SELECT ENDPOINT_ID FROM TRELLIX WHERE AGENT_STATUS = 'Online'
    UNION
    SELECT ENDPOINT_ID FROM TREND_MICRO WHERE AGENT_STATUS = 'Normal'
    UNION
    SELECT ENDPOINT_ID FROM SYMANTEC_THREATS WHERE AGENT_STATUS = 'Enabled'
    UNION
    SELECT DEVICE_ID FROM DEFENDER WHERE STATUS = 'Protected'
    UNION
    SELECT ENDPOINT_ID FROM CROWDSTRIKE WHERE STATUS = 'Normal'
);

-- Denominator: Total Assets (MISSING - CRITICAL GAP)
-- Need: Complete asset inventory (CMDB, AD, Network Discovery)
```

**What's Missing**:
1. **Complete Asset Inventory**:
   - Need master list of ALL endpoints (servers + workstations)
   - Source: CMDB, Active Directory, Network Discovery (Qualys?)

2. **Asset Metadata**:
   - OS type (Windows, Linux, macOS)
   - Device type (Server, Workstation, Laptop, VDI)
   - Business criticality
   - OpCo/Division ownership

**Workaround - Calculate Against Qualys Inventory**:
```sql
-- Use Qualys as proxy for total asset count
CREATE OR REPLACE VIEW VW_EDR_COVERAGE AS
WITH total_assets AS (
    SELECT COUNT(DISTINCT HOST_ID) as TOTAL_HOSTS
    FROM DIM_HOST
    WHERE LAST_SEEN_DATE >= DATEADD('day', -30, CURRENT_DATE())
),
edr_protected AS (
    SELECT COUNT(DISTINCT ENDPOINT_ID) as PROTECTED_HOSTS
    FROM (
        -- Union all EDR sources
        SELECT ENDPOINT_ID FROM CISCO_AMP WHERE AGENT_STATUS = 'Healthy'
        UNION
        SELECT ENDPOINT_ID FROM CROWDSTRIKE WHERE STATUS = 'Normal'
        -- ... other sources
    )
)
SELECT
    e.PROTECTED_HOSTS,
    t.TOTAL_HOSTS,
    ROUND(e.PROTECTED_HOSTS * 100.0 / NULLIF(t.TOTAL_HOSTS, 0), 2) as EDR_COVERAGE_PCT,
    CASE
        WHEN EDR_COVERAGE_PCT >= 98 THEN '✅ Target Met'
        WHEN EDR_COVERAGE_PCT >= 95 THEN '⚠️ Near Target'
        ELSE '🔴 Below Target'
    END as STATUS
FROM edr_protected e, total_assets t;
```

**Estimated Implementation**:
- Current (using Qualys as baseline): 12 hours ✅ **CAN IMPLEMENT NOW**
- Full (with proper CMDB): 24 hours (requires CMDB integration)

---

### Metric #6: Vuln-Scan Coverage & Agent Health

**NIST CSF**: PR.IP (Protect – Improvements)
**Target**: ≥ 95% scanned, ≤ 2% unhealthy
**Primary Data Source**: Qualys

#### Current Status: ✅ **FULLY FEASIBLE**

**Data Availability**:
- ✅ Qualys scan data EXISTS (QUALYS_KB, QUALYS_OS)
- ✅ Agent health status available
- ✅ Historical scan data available

**Implementation**:
```sql
CREATE OR REPLACE VIEW VW_VULN_SCAN_COVERAGE AS
WITH scan_coverage AS (
    SELECT
        COUNT(DISTINCT HOST_ID) as SCANNED_HOSTS,
        COUNT(DISTINCT CASE WHEN LAST_SCAN_DATE >= DATEADD('day', -30, CURRENT_DATE())
              THEN HOST_ID END) as RECENTLY_SCANNED
    FROM QUALYS_OS
),
agent_health AS (
    SELECT
        COUNT(*) as TOTAL_AGENTS,
        COUNT(CASE WHEN AGENT_STATUS != 'Healthy' THEN 1 END) as UNHEALTHY_AGENTS
    FROM QUALYS_OS
    WHERE AGENT_INSTALLED = TRUE
),
total_assets AS (
    SELECT COUNT(DISTINCT HOST_ID) as TOTAL_HOSTS
    FROM DIM_HOST
)
SELECT
    sc.RECENTLY_SCANNED,
    ta.TOTAL_HOSTS,
    ROUND(sc.RECENTLY_SCANNED * 100.0 / ta.TOTAL_HOSTS, 2) as SCAN_COVERAGE_PCT,
    ah.UNHEALTHY_AGENTS,
    ah.TOTAL_AGENTS,
    ROUND(ah.UNHEALTHY_AGENTS * 100.0 / ah.TOTAL_AGENTS, 2) as UNHEALTHY_AGENT_PCT,
    CASE
        WHEN SCAN_COVERAGE_PCT >= 95 AND UNHEALTHY_AGENT_PCT <= 2 THEN '✅ Target Met'
        WHEN SCAN_COVERAGE_PCT >= 90 OR UNHEALTHY_AGENT_PCT <= 5 THEN '⚠️ Near Target'
        ELSE '🔴 Below Target'
    END as STATUS
FROM scan_coverage sc, agent_health ah, total_assets ta;
```

**Data Quality Checks Needed**:
1. Validate scan dates are recent (< 30 days)
2. Check for duplicate HOST_IDs
3. Verify agent status values are standardized

**Estimated Implementation**: 8 hours ✅ **READY TO IMPLEMENT**

---

### Metric #7: Email-Sending Domain Security

**NIST CSF**: PR.DS (Protect – Data Security)
**Target**: ≥ 95% compliant
**Primary Data Source**: Proofpoint message-header logs

#### Current Status: ✅ **FULLY FEASIBLE**

**Data Availability**:
- ✅ Proofpoint data EXISTS (PROOFPOINT_MESSAGE_LOGS)
- ✅ Email headers with SPF, DKIM, DMARC available
- ✅ Sending domain information captured

**Implementation**:
```sql
CREATE OR REPLACE VIEW VW_EMAIL_DOMAIN_SECURITY AS
WITH domain_compliance AS (
    SELECT
        SENDING_DOMAIN,
        COUNT(*) as TOTAL_EMAILS,
        -- SPF Check
        COUNT(CASE WHEN SPF_RESULT = 'pass' THEN 1 END) as SPF_PASS_COUNT,
        -- DKIM Check
        COUNT(CASE WHEN DKIM_RESULT = 'pass' THEN 1 END) as DKIM_PASS_COUNT,
        -- DMARC Check (must be quarantine or reject)
        COUNT(CASE WHEN DMARC_POLICY IN ('quarantine', 'reject') THEN 1 END) as DMARC_COMPLIANT_COUNT
    FROM PROOFPOINT_MESSAGE_LOGS
    WHERE MESSAGE_DATE >= DATEADD('day', -30, CURRENT_DATE())
        AND SENDING_DOMAIN LIKE '%.GenericCorp.com'  -- GenericCorp domains only
    GROUP BY SENDING_DOMAIN
),
domain_status AS (
    SELECT
        SENDING_DOMAIN,
        TOTAL_EMAILS,
        CASE
            WHEN SPF_PASS_COUNT * 100.0 / TOTAL_EMAILS >= 95
                AND DMARC_COMPLIANT_COUNT * 100.0 / TOTAL_EMAILS >= 95
            THEN TRUE
            ELSE FALSE
        END as IS_COMPLIANT
    FROM domain_compliance
)
SELECT
    COUNT(*) as TOTAL_DOMAINS,
    COUNT(CASE WHEN IS_COMPLIANT THEN 1 END) as COMPLIANT_DOMAINS,
    ROUND(COUNT(CASE WHEN IS_COMPLIANT THEN 1 END) * 100.0 / COUNT(*), 2) as COMPLIANCE_PCT,
    CASE
        WHEN COMPLIANCE_PCT >= 95 THEN '✅ Target Met'
        WHEN COMPLIANCE_PCT >= 90 THEN '⚠️ Near Target'
        ELSE '🔴 Below Target'
    END as STATUS
FROM domain_status;
```

**Estimated Implementation**: 12 hours ✅ **READY TO IMPLEMENT**

---

### Metric #8: Phishing-Simulation Click Rate

**NIST CSF**: DE.AE (Detect – Awareness & Engagement)
**Target**: < 5%
**Primary Data Source**: MetaCompliance › Phish Simulation Campaigns

#### Current Status: 🔴 **NOT FEASIBLE**

**Data Availability**:
- ❌ MetaCompliance not integrated with Snowflake
- ❌ No phishing simulation campaign data
- ❌ No user click tracking

**What's Needed**:
1. **MetaCompliance API Integration**:
   ```sql
   -- Required tables
   L_METACOMPLIANCE_CAMPAIGNS
   L_METACOMPLIANCE_CAMPAIGN_RESULTS

   -- Transformation
   DIM_PHISHING_CAMPAIGN
   FACT_PHISHING_SIMULATION_RESULTS
   ```

2. **Required Data Fields**:
   - CAMPAIGN_ID, CAMPAIGN_NAME, CAMPAIGN_START_DATE, CAMPAIGN_END_DATE
   - USER_ID, USER_EMAIL, USER_DEPARTMENT, USER_OPCO
   - EMAIL_SENT_TIMESTAMP
   - LINK_CLICKED (Boolean)
   - CREDENTIALS_ENTERED (Boolean)
   - REPORTED_AS_PHISH (Boolean)

3. **Calculation**:
   ```sql
   SELECT
       CAMPAIGN_NAME,
       COUNT(*) as EMAILS_SENT,
       COUNT(CASE WHEN LINK_CLICKED THEN 1 END) as CLICKS,
       ROUND(COUNT(CASE WHEN LINK_CLICKED THEN 1 END) * 100.0 / COUNT(*), 2) as CLICK_RATE_PCT,
       CASE
           WHEN CLICK_RATE_PCT < 5 THEN '✅ Target Met'
           WHEN CLICK_RATE_PCT < 10 THEN '⚠️ Near Target'
           ELSE '🔴 High Risk'
       END as RISK_LEVEL
   FROM FACT_PHISHING_SIMULATION_RESULTS
   WHERE CAMPAIGN_START_DATE >= DATEADD('month', -1, CURRENT_DATE())
   GROUP BY CAMPAIGN_NAME;
   ```

**Estimated Implementation**: 40 hours (includes MetaCompliance API integration)

---

### Metric #9: Mean Time to Escalate Malicious Email (MTTE)

**NIST CSF**: DE.DP (Detect – Processes)
**Target**: ↓ trend (minutes)
**Primary Data Source**: Proofpoint + ServiceNow ticket timestamps

#### Current Status: 🟡 **PARTIALLY FEASIBLE**

**Data Availability**:
- ✅ Proofpoint message logs EXISTS
- ❌ ServiceNow ticket data NOT integrated
- ⚠️ **CRITICAL**: Cannot calculate time difference without both timestamps

**Current Data**:
```sql
-- Proofpoint: Email receipt/detection time (EXISTS)
SELECT
    MESSAGE_ID,
    RECEIVED_TIME,  -- When email arrived
    THREAT_DETECTED_TIME,  -- When Proofpoint flagged as malicious
    THREAT_CATEGORY,
    THREAT_SCORE
FROM PROOFPOINT_MESSAGE_LOGS
WHERE THREAT_SCORE >= 80;  -- High threat threshold
```

**What's Missing**:
```sql
-- ServiceNow: Escalation time (MISSING)
L_SERVICENOW_INCIDENTS (
    INCIDENT_ID,
    INCIDENT_NUMBER,
    CREATED_TIMESTAMP,  -- When ticket was opened in ServiceNow
    CATEGORY,
    SUBCATEGORY,
    RELATED_EMAIL_ID  -- Link to Proofpoint MESSAGE_ID
)
```

**Interim Workaround**:
```sql
-- Calculate detection time within Proofpoint only (NOT full MTTE)
CREATE OR REPLACE VIEW VW_EMAIL_DETECTION_TIME AS
SELECT
    DATE_TRUNC('month', RECEIVED_TIME) as MONTH,
    AVG(DATEDIFF('minute', RECEIVED_TIME, THREAT_DETECTED_TIME)) as AVG_DETECTION_MINUTES,
    MEDIAN(DATEDIFF('minute', RECEIVED_TIME, THREAT_DETECTED_TIME)) as MEDIAN_DETECTION_MINUTES,
    MAX(DATEDIFF('minute', RECEIVED_TIME, THREAT_DETECTED_TIME)) as MAX_DETECTION_MINUTES,
    COUNT(*) as TOTAL_MALICIOUS_EMAILS
FROM PROOFPOINT_MESSAGE_LOGS
WHERE THREAT_SCORE >= 80
    AND RECEIVED_TIME >= DATEADD('month', -6, CURRENT_DATE())
GROUP BY DATE_TRUNC('month', RECEIVED_TIME)
ORDER BY MONTH DESC;
```

**Full Implementation Needs**:
- ServiceNow integration for complete escalation tracking
- Correlation logic between Proofpoint MESSAGE_ID and ServiceNow INCIDENT_ID

**Estimated Implementation**:
- Interim (Proofpoint only): 12 hours ✅
- Full (with ServiceNow): 48 hours

---

### Metric #10: Log-Source Coverage for SIEM

**NIST CSF**: DE.CM (Detect – Continuous Monitoring)
**Target**: ≥ 95% required sources
**Primary Data Source**: Splunk / Microsoft Sentinel feed status

#### Current Status: 🟡 **PARTIALLY FEASIBLE**

**Data Availability**:
- ✅ Splunk data EXISTS (SPLUNK_ALERTS)
- ⚠️ **GAP**: No comprehensive log source inventory
- ⚠️ **GAP**: No "required sources" policy table

**Current Data**:
```sql
-- What we have: Splunk alerts (not log source coverage)
SELECT
    SOURCE_TYPE,
    COUNT(*) as ALERT_COUNT,
    MAX(EVENT_TIME) as LAST_EVENT_TIME
FROM SPLUNK_ALERTS
GROUP BY SOURCE_TYPE;
```

**What's Needed**:
1. **Policy-Driven Required Sources List**:
   ```sql
   CREATE TABLE CFG_REQUIRED_LOG_SOURCES (
       SOURCE_ID NUMBER,
       SOURCE_NAME VARCHAR,
       SOURCE_TYPE VARCHAR,  -- Firewall, IDS, EDR, AD, etc.
       BUSINESS_CRITICALITY VARCHAR,  -- Critical, High, Medium
       REQUIRED_FOR_COMPLIANCE BOOLEAN,
       OPCO VARCHAR,
       EXPECTED_LOG_VOLUME_PER_DAY NUMBER
   );
   ```

2. **SIEM Feed Status Monitoring**:
   ```sql
   CREATE TABLE SIEM_LOG_SOURCE_STATUS (
       SOURCE_ID NUMBER,
       SOURCE_NAME VARCHAR,
       LAST_LOG_RECEIVED TIMESTAMP,
       LOGS_RECEIVED_LAST_HOUR NUMBER,
       STATUS VARCHAR,  -- Active, Inactive, Degraded
       HEALTH_CHECK_TIME TIMESTAMP
   );
   ```

3. **Coverage Calculation**:
   ```sql
   CREATE OR REPLACE VIEW VW_SIEM_LOG_SOURCE_COVERAGE AS
   WITH required_sources AS (
       SELECT COUNT(*) as REQUIRED_COUNT
       FROM CFG_REQUIRED_LOG_SOURCES
   ),
   active_sources AS (
       SELECT COUNT(*) as ACTIVE_COUNT
       FROM SIEM_LOG_SOURCE_STATUS
       WHERE STATUS = 'Active'
           AND LAST_LOG_RECEIVED >= DATEADD('hour', -1, CURRENT_TIMESTAMP())
   )
   SELECT
       a.ACTIVE_COUNT,
       r.REQUIRED_COUNT,
       ROUND(a.ACTIVE_COUNT * 100.0 / r.REQUIRED_COUNT, 2) as COVERAGE_PCT,
       CASE
           WHEN COVERAGE_PCT >= 95 THEN '✅ Target Met'
           WHEN COVERAGE_PCT >= 90 THEN '⚠️ Near Target'
           ELSE '🔴 Critical Gap'
       END as STATUS
   FROM active_sources a, required_sources r;
   ```

**Estimated Implementation**:
- Configuration table creation: 16 hours
- SIEM integration for status monitoring: 40 hours
- Total: 56 hours

---

### Metric #11: SOC Ticket Response within SLA

**NIST CSF**: RS.MI (Respond – Mitigation)
**Target**: ≥ 98% on-time
**Primary Data Source**: ServiceNow global incident queue

#### Current Status: 🔴 **NOT FEASIBLE**

**Data Availability**:
- ❌ ServiceNow not integrated with Snowflake
- ❌ No incident queue data
- ❌ No SLA tracking

**What's Needed**:
1. **ServiceNow Integration**:
   ```sql
   -- Required tables
   L_SERVICENOW_INCIDENTS
   L_SERVICENOW_SLA_DEFINITIONS

   -- Transformation
   FACT_SOC_TICKET_SLA_PERFORMANCE
   ```

2. **Required Data Fields**:
   ```sql
   INCIDENT_ID, INCIDENT_NUMBER, SHORT_DESCRIPTION
   PRIORITY (P1, P2, P3, P4)
   ASSIGNMENT_GROUP (SOC, Security Engineering, etc.)
   OPENED_AT, ASSIGNED_AT, RESPONDED_AT, RESOLVED_AT
   SLA_DUE_TIME, SLA_MET (Boolean)
   RESPONSE_TIME_MINUTES, RESOLUTION_TIME_HOURS
   ```

3. **Calculation**:
   ```sql
   SELECT
       PRIORITY,
       COUNT(*) as TOTAL_TICKETS,
       COUNT(CASE WHEN SLA_MET THEN 1 END) as SLA_MET_COUNT,
       ROUND(COUNT(CASE WHEN SLA_MET THEN 1 END) * 100.0 / COUNT(*), 2) as SLA_COMPLIANCE_PCT,
       AVG(RESPONSE_TIME_MINUTES) as AVG_RESPONSE_MINUTES
   FROM FACT_SOC_TICKET_SLA_PERFORMANCE
   WHERE OPENED_AT >= DATEADD('month', -1, CURRENT_DATE())
       AND ASSIGNMENT_GROUP = 'SOC'
   GROUP BY PRIORITY;
   ```

**Estimated Implementation**: 48 hours (requires ServiceNow API integration)

---

### Metric #12: Incident-Response Effort (hrs & £/month)

**NIST CSF**: RS.RP (Respond – Planning)
**Target**: Track trend
**Primary Data Source**: ServiceNow labor-hour & cost fields

#### Current Status: 🔴 **NOT FEASIBLE**

**Data Availability**:
- ❌ ServiceNow not integrated
- ❌ No labor hour tracking
- ❌ No cost model data

**What's Needed**:
1. **ServiceNow Time Tracking**:
   ```sql
   L_SERVICENOW_TIME_ENTRIES (
       TIME_ENTRY_ID,
       INCIDENT_ID,
       USER_ID,
       TIME_SPENT_HOURS,
       TIME_ENTRY_DATE,
       WORK_NOTES
   )
   ```

2. **Cost Model**:
   ```sql
   CFG_RESOURCE_COST_RATES (
       RESOURCE_ROLE VARCHAR,  -- SOC Analyst, Sr. Analyst, Manager
       HOURLY_RATE_USD NUMBER,
       HOURLY_RATE_EUR NUMBER,
       HOURLY_RATE_GBP NUMBER
   )
   ```

3. **Calculation**:
   ```sql
   SELECT
       DATE_TRUNC('month', i.OPENED_AT) as MONTH,
       SUM(te.TIME_SPENT_HOURS) as TOTAL_HOURS,
       SUM(te.TIME_SPENT_HOURS * cr.HOURLY_RATE_USD) as TOTAL_COST_USD,
       SUM(te.TIME_SPENT_HOURS * cr.HOURLY_RATE_GBP) as TOTAL_COST_GBP,
       COUNT(DISTINCT i.INCIDENT_ID) as INCIDENT_COUNT,
       AVG(te.TIME_SPENT_HOURS) as AVG_HOURS_PER_INCIDENT
   FROM L_SERVICENOW_INCIDENTS i
   JOIN L_SERVICENOW_TIME_ENTRIES te ON i.INCIDENT_ID = te.INCIDENT_ID
   JOIN CFG_RESOURCE_COST_RATES cr ON te.USER_ROLE = cr.RESOURCE_ROLE
   WHERE i.OPENED_AT >= DATEADD('month', -12, CURRENT_DATE())
   GROUP BY DATE_TRUNC('month', i.OPENED_AT)
   ORDER BY MONTH DESC;
   ```

**Estimated Implementation**: 56 hours (requires ServiceNow + cost model)

---

### Metric #13: Security-Awareness Completion Rate

**NIST CSF**: DE.AE (Detect – Awareness & Engagement)
**Target**: ≥ 95% staff completed annual CBT
**Primary Data Source**: MetaCompliance › CBT & Policy Acknowledgement

#### Current Status: 🔴 **NOT FEASIBLE**

**Data Availability**:
- ❌ MetaCompliance not integrated
- ❌ No training completion data
- ❌ No employee roster in Snowflake

**What's Needed**:
1. **MetaCompliance Integration**:
   ```sql
   L_METACOMPLIANCE_USERS
   L_METACOMPLIANCE_COURSES
   L_METACOMPLIANCE_COURSE_COMPLETIONS
   L_METACOMPLIANCE_POLICY_ACKNOWLEDGEMENTS
   ```

2. **HR Roster** (Denominator):
   ```sql
   DIM_EMPLOYEE (
       EMPLOYEE_ID,
       EMAIL,
       FULL_NAME,
       DEPARTMENT,
       OPCO,
       HIRE_DATE,
       EMPLOYMENT_STATUS,  -- Active, Inactive
       REQUIRES_CBT BOOLEAN
   )
   ```

3. **Calculation**:
   ```sql
   WITH employees_requiring_training AS (
       SELECT COUNT(*) as REQUIRED_COUNT
       FROM DIM_EMPLOYEE
       WHERE EMPLOYMENT_STATUS = 'Active'
           AND REQUIRES_CBT = TRUE
   ),
   completed_training AS (
       SELECT COUNT(DISTINCT USER_ID) as COMPLETED_COUNT
       FROM L_METACOMPLIANCE_COURSE_COMPLETIONS
       WHERE COURSE_TYPE = 'Annual Security Awareness'
           AND COMPLETION_DATE >= DATEADD('year', -1, CURRENT_DATE())
   )
   SELECT
       c.COMPLETED_COUNT,
       r.REQUIRED_COUNT,
       ROUND(c.COMPLETED_COUNT * 100.0 / r.REQUIRED_COUNT, 2) as COMPLETION_RATE_PCT,
       CASE
           WHEN COMPLETION_RATE_PCT >= 95 THEN '✅ Target Met'
           WHEN COMPLETION_RATE_PCT >= 90 THEN '⚠️ Near Target'
           ELSE '🔴 Below Target'
       END as STATUS
   FROM completed_training c, employees_requiring_training r;
   ```

**Estimated Implementation**: 48 hours (requires MetaCompliance + HR data integration)

---

## Summary: Top 13 Metrics Feasibility

| # | Metric Name | Status | Can Implement Now? | Priority |
|---|-------------|--------|-------------------|----------|
| 1 | Cyber-Maturity Score | 🔴 Not Feasible | ❌ No (Archer needed) | HIGH |
| 2 | Policy-Exception Rate | 🔴 Not Feasible | ❌ No (Archer needed) | HIGH |
| 3 | Third-Party Risk Score | 🟡 Partial | ⚠️ BitSight only | HIGH |
| 4 | Days Since Last Ransomware | 🟡 Partial | ⚠️ Low accuracy | MEDIUM |
| 5 | EDR Coverage – All Systems | ✅ Feasible | ✅ Yes (with caveats) | HIGH |
| 6 | Vuln-Scan Coverage & Agent Health | ✅ Feasible | ✅ Yes | HIGH |
| 7 | Email-Sending Domain Security | ✅ Feasible | ✅ Yes | MEDIUM |
| 8 | Phishing-Simulation Click Rate | 🔴 Not Feasible | ❌ No (MetaCompliance) | HIGH |
| 9 | MTTE – Malicious Email | 🟡 Partial | ⚠️ Detection only | MEDIUM |
| 10 | Log-Source Coverage for SIEM | 🟡 Partial | ⚠️ Needs config | MEDIUM |
| 11 | SOC Ticket Response within SLA | 🔴 Not Feasible | ❌ No (ServiceNow) | HIGH |
| 12 | Incident-Response Effort | 🔴 Not Feasible | ❌ No (ServiceNow) | MEDIUM |
| 13 | Security-Awareness Completion | 🔴 Not Feasible | ❌ No (MetaCompliance) | HIGH |

**Immediate Wins (Can Implement Now)**:
- ✅ Metric #5: EDR Coverage
- ✅ Metric #6: Vuln-Scan Coverage & Agent Health
- ✅ Metric #7: Email-Sending Domain Security

**Quick Wins (Interim Solutions)**:
- ⚠️ Metric #3: Third-Party Risk (BitSight only)
- ⚠️ Metric #9: Email Detection Time (not full MTTE)

---

## Additional 24 Operational Metrics

### Summary Analysis

I've analyzed all 37 metrics from the dictionary. Here's the breakdown by data feasibility:

#### ✅ **Fully Feasible Metrics (9 total)**:

| # | Metric Name | Service | Implementation Effort |
|---|-------------|---------|----------------------|
| 2 | Deploy EDR Agents - All Systems | EDR | 16 hours |
| 3 | Deploy EDR Agents - SOX Systems | EDR | 16 hours |
| 4 | Maintain EDR Agent Health - All | EDR | 12 hours |
| 5 | Maintain EDR Agent Health - SOX | EDR | 12 hours |
| 6 | Vuln-Scan Coverage & Agent Health | Qualys | 8 hours |
| 10 | Deploy network-based vuln scans | Qualys | 12 hours |
| 11 | Deploy Vuln Scanning Agents - All | Qualys | 16 hours |
| 12 | Deploy Vuln Scanning Agents - SOX | Qualys | 16 hours |
| 13 | Maintain network-based vuln scans | Qualys | 8 hours |

**Total Implementation for "Green Light" Metrics**: ~116 hours (≈ 3 weeks)

#### 🟡 **Partially Feasible (Workarounds Available) - 8 metrics**:

| # | Metric Name | Service | What's Missing | Workaround |
|---|-------------|---------|----------------|------------|
| 9 | Email Domain Security Config | Proofpoint | Domain inventory | Use Proofpoint logs |
| 14 | Maintain Vuln Scanning Agent Health - All | Qualys | Agent health API | Use last scan date |
| 15 | Maintain Vuln Scanning Agent Health - SOX | Qualys | SOX designation | Manual tagging |
| 28 | Deploy Secure Web Proxy - All | Zscaler | Zscaler integration | Pending |
| 29 | Deploy Secure Web Proxy - SOX | Zscaler | Zscaler integration | Pending |
| 30 | Maintain Zscaler Health - All | Zscaler | Zscaler integration | Pending |
| 31 | Maintain Zscaler Health - SOX | Zscaler | Zscaler integration | Pending |
| 32 | Days since last incident | ServiceNow | Incident data | Manual tracking |

#### 🔴 **Not Feasible (Missing Data Sources) - 20 metrics**:

**ServiceNow-Dependent (7 metrics)**:
- #17: Security Engineering support request response
- #18: Tickets worked
- #19: Timely triage of issue tickets
- #20: Security Engineering support request resolution
- #21: Security Operations ticket response
- #22: Security Operations ticket update frequency
- #33-37: Days since last BEC/Fraud/Ransomware/Extortion events

**RSA Archer-Dependent (2 metrics)**:
- #1: Cyber-Maturity Score
- #2: Policy-Exception Rate

**MetaCompliance-Dependent (2 metrics)**:
- #8: Phishing-Simulation Click Rate
- #13: Security-Awareness Completion Rate

**Splunk/SIEM-Dependent (5 metrics)**:
- #23: New SIEM rules
- #24: Regularly tune SIEM
- #25: Deploy SIEM log collectors
- #26: Enable security logging
- #27: Maintain SIEM log collector health

**Other Systems (4 metrics)**:
- #16: ReliaQuest Tuning activities (ReliaQuest)
- #28-31: Zscaler metrics (Zscaler not integrated)

---

## Data Availability Matrix

### Current Data Sources in Snowflake

| Data Source | Integration Status | Tables Available | Metrics Enabled |
|-------------|-------------------|------------------|-----------------|
| **Qualys** | ✅ INTEGRATED | QUALYS_KB, QUALYS_OS | #6, 10-15 |
| **EDR Tools** | ✅ INTEGRATED | 7 platforms | #2-5 |
| **Proofpoint** | ✅ INTEGRATED | PROOFPOINT_MESSAGE_LOGS | #7, 9 |
| **BitSight** | ✅ INTEGRATED | BITSIGHT_* tables | #3 (partial) |
| **Splunk** | 🟡 PARTIAL | SPLUNK_ALERTS | #10, 23-27 (partial) |
| **RSA Archer** | ❌ NOT INTEGRATED | None | #1, 2, 3 (blocked) |
| **ServiceNow** | ❌ NOT INTEGRATED | None | #11, 12, 17-22, 32-37 (blocked) |
| **MetaCompliance** | ❌ NOT INTEGRATED | None | #8, 13 (blocked) |
| **Zscaler** | ❌ NOT INTEGRATED | None | #28-31 (blocked) |
| **ReliaQuest** | ❌ NOT INTEGRATED | None | #16 (blocked) |

### Integration Priorities

**Priority 1 - CRITICAL (Blocks Top 13 Metrics)**:
1. **RSA Archer** → Blocks metrics #1, 2, 3
2. **ServiceNow** → Blocks metrics #11, 12
3. **MetaCompliance** → Blocks metrics #8, 13

**Priority 2 - HIGH (Operational Metrics)**:
4. **Zscaler** → Blocks metrics #28-31
5. **Splunk Enhancement** → Incomplete for metrics #23-27

**Priority 3 - MEDIUM**:
6. **ReliaQuest** → Blocks metric #16

---

## Implementation Roadmap

### Phase 1: Quick Wins (2-4 weeks)

**Objective**: Deliver 9 operational metrics using existing data

**Metrics to Implement**:
- ✅ EDR Coverage & Health (Metrics #2-5)
- ✅ Vulnerability Scanning Coverage & Health (Metrics #6, 10-15)
- ✅ Email Domain Security (Metric #7)

**Deliverables**:
1. **SQL Views**:
   ```sql
   VW_EDR_COVERAGE_ALL_SYSTEMS
   VW_EDR_COVERAGE_SOX_SYSTEMS
   VW_EDR_AGENT_HEALTH
   VW_VULN_SCAN_COVERAGE
   VW_VULN_AGENT_HEALTH
   VW_EMAIL_DOMAIN_SECURITY
   ```

2. **KPI Tables** (REPORTING Layer):
   ```sql
   TBL_KPI_EDR_COVERAGE
   TBL_KPI_VULN_SCAN_COVERAGE
   TBL_KPI_EMAIL_SECURITY
   ```

3. **Automated Refresh** (Daily via Tasks):
   ```sql
   TASK_CALCULATE_EDR_KPIS
   TASK_CALCULATE_VULN_KPIS
   TASK_CALCULATE_EMAIL_KPIS
   ```

**Estimated Effort**: 116 hours (≈ 3 weeks, 1 developer)

---

### Phase 2: Critical Integrations (8-12 weeks)

**Objective**: Integrate RSA Archer, ServiceNow, MetaCompliance

#### 2.1 RSA Archer Integration (4 weeks)

**Metrics Enabled**: #1 (Maturity), #2 (Policy Exceptions), #3 (TPRM - complete)

**Tasks**:
1. **API Discovery & Authentication** (1 week)
   - Archer REST API access
   - Service account creation
   - API token generation

2. **Data Model Design** (1 week)
   ```sql
   -- LANDING Layer
   CREATE TABLE L_ARCHER_MATURITY_ASSESSMENTS (...);
   CREATE TABLE L_ARCHER_POLICY_EXCEPTIONS (...);
   CREATE TABLE L_ARCHER_TPRM_VENDORS (...);

   -- TRANSFORMATION Layer
   CREATE TABLE DIM_MATURITY_SCORE (...);
   CREATE TABLE FACT_POLICY_EXCEPTIONS (...);
   CREATE TABLE DIM_VENDOR (...);
   CREATE TABLE FACT_VENDOR_RISK_ASSESSMENT (...);
   ```

3. **ETL Development** (1.5 weeks)
   - Python extraction scripts
   - Data validation & transformation
   - Incremental load logic

4. **Testing & Validation** (0.5 weeks)
   - Data reconciliation
   - Historical data backfill

**Estimated Effort**: 160 hours

#### 2.2 ServiceNow Integration (4 weeks)

**Metrics Enabled**: #11 (SOC Tickets), #12 (Incident Response Effort), #17-22, #32-37

**Tasks**:
1. **ServiceNow API Setup** (1 week)
   - REST API configuration
   - Authentication (OAuth 2.0)
   - Query optimization

2. **Data Model Design** (1 week)
   ```sql
   -- LANDING Layer
   CREATE TABLE L_SERVICENOW_INCIDENTS (...);
   CREATE TABLE L_SERVICENOW_TIME_ENTRIES (...);
   CREATE TABLE L_SERVICENOW_SLA_DEFINITIONS (...);

   -- TRANSFORMATION Layer
   CREATE TABLE FACT_SOC_TICKET_SLA_PERFORMANCE (...);
   CREATE TABLE FACT_INCIDENT_RESPONSE_EFFORT (...);
   ```

3. **ETL Development** (1.5 weeks)
   - Incident extraction
   - SLA calculation logic
   - Cost model integration

4. **Testing & Dashboard Creation** (0.5 weeks)

**Estimated Effort**: 160 hours

#### 2.3 MetaCompliance Integration (2 weeks)

**Metrics Enabled**: #8 (Phishing Click Rate), #13 (Awareness Training)

**Tasks**:
1. **API Integration** (0.5 weeks)
2. **Data Model** (0.5 weeks)
   ```sql
   L_METACOMPLIANCE_CAMPAIGNS
   L_METACOMPLIANCE_COURSE_COMPLETIONS
   FACT_PHISHING_SIMULATION_RESULTS
   FACT_TRAINING_COMPLIANCE
   ```
3. **ETL Development** (0.5 weeks)
4. **Testing** (0.5 weeks)

**Estimated Effort**: 80 hours

**Phase 2 Total Effort**: 400 hours (≈ 10 weeks, 1 developer)

---

### Phase 3: Advanced Metrics (4-6 weeks)

**Objective**: Complete remaining metrics and enhancements

#### 3.1 Zscaler Integration (3 weeks)

**Metrics**: #28-31 (Secure Web Proxy coverage & health)

**Estimated Effort**: 120 hours

#### 3.2 Enhanced SIEM Integration (2 weeks)

**Metrics**: #23-27 (SIEM tuning, log collectors, security logging)

**Estimated Effort**: 80 hours

#### 3.3 ReliaQuest Integration (1 week)

**Metric**: #16 (Tuning activities)

**Estimated Effort**: 40 hours

**Phase 3 Total Effort**: 240 hours (≈ 6 weeks, 1 developer)

---

### Total Implementation Timeline

| Phase | Duration | Effort (hours) | Metrics Delivered | Cumulative % |
|-------|----------|----------------|-------------------|--------------|
| **Phase 1** | 3 weeks | 116 | 9 metrics | 24% |
| **Phase 2** | 10 weeks | 400 | 20 metrics (cumulative: 29) | 78% |
| **Phase 3** | 6 weeks | 240 | 8 metrics (cumulative: 37) | 100% |
| **TOTAL** | **19 weeks** | **756 hours** | **37 metrics** | **100%** |

**Resource Requirements**: 1 FTE Data Engineer for ~5 months

---

## Data Quality Considerations

### 1. Data Completeness

**Critical Gaps**:

#### Gap 1: Asset Inventory Completeness
**Problem**: No single source of truth for total asset count (denominator for coverage metrics)

**Impact**: Metrics #2-5, 11-12, 28-29 cannot calculate accurate percentages

**Solution**:
```sql
-- Create unified asset inventory
CREATE OR REPLACE VIEW VW_MASTER_ASSET_INVENTORY AS
SELECT
    COALESCE(q.HOST_ID, e.ENDPOINT_ID, ad.COMPUTER_NAME) as ASSET_ID,
    COALESCE(q.HOSTNAME, e.HOSTNAME, ad.COMPUTER_NAME) as HOSTNAME,
    COALESCE(q.IP_ADDRESS, e.IP_ADDRESS) as IP_ADDRESS,
    CASE
        WHEN q.HOST_ID IS NOT NULL THEN 'Qualys'
        WHEN e.ENDPOINT_ID IS NOT NULL THEN 'EDR'
        WHEN ad.COMPUTER_NAME IS NOT NULL THEN 'Active Directory'
    END as SOURCE,
    CASE
        WHEN q.OS LIKE '%Server%' OR ad.OS LIKE '%Server%' THEN 'Server'
        ELSE 'Workstation'
    END as DEVICE_TYPE,
    MAX(COALESCE(q.LAST_SEEN_DATE, e.LAST_SEEN_DATE, ad.LAST_LOGON_DATE)) as LAST_SEEN_DATE
FROM DIM_HOST q
FULL OUTER JOIN (
    SELECT ENDPOINT_ID, HOSTNAME, IP_ADDRESS, LAST_SEEN_DATE FROM CISCO_AMP
    UNION ALL
    SELECT ENDPOINT_ID, HOSTNAME, IP_ADDRESS, LAST_SEEN_DATE FROM CROWDSTRIKE
    -- ... other EDR sources
) e ON q.HOST_ID = e.ENDPOINT_ID
FULL OUTER JOIN ACTIVE_DIRECTORY_COMPUTERS ad  -- IF AVAILABLE
    ON q.HOSTNAME = ad.COMPUTER_NAME
WHERE LAST_SEEN_DATE >= DATEADD('day', -90, CURRENT_DATE())  -- Active in last 90 days
GROUP BY 1,2,3,4,5;
```

**Action Items**:
1. ☐ Integrate Active Directory computer inventory
2. ☐ Integrate CMDB (Configuration Management Database) if available
3. ☐ Implement asset reconciliation process
4. ☐ Define "active asset" criteria (last seen < X days)

---

#### Gap 2: SOX System Designation
**Problem**: No SOX flag on assets (required for metrics #3, 5, 12, 15, 29, 31)

**Impact**: Cannot separate SOX vs. non-SOX metrics

**Solution**:
```sql
-- Create SOX designation table
CREATE TABLE CFG_SOX_SYSTEMS (
    ASSET_ID VARCHAR,
    HOSTNAME VARCHAR,
    IS_SOX_IN_SCOPE BOOLEAN,
    SOX_CONTROL_IDS VARCHAR,  -- e.g., "ITGC-01, ITGC-05"
    BUSINESS_JUSTIFICATION VARCHAR,
    DESIGNATED_DATE DATE,
    REVIEWED_DATE DATE,
    REVIEWER_NAME VARCHAR
);

-- Apply SOX flag to metrics
ALTER VIEW VW_EDR_COVERAGE ADD COLUMN IS_SOX_IN_SCOPE BOOLEAN;
```

**Action Items**:
1. ☐ Obtain SOX-scoped systems list from Compliance team
2. ☐ Create SOX designation table
3. ☐ Implement annual review process for SOX scope

---

#### Gap 3: Ransomware Event Classification
**Problem**: Threat names don't clearly identify ransomware (metric #4, 36)

**Impact**: "Days Since Last Ransomware" metric has low accuracy

**Solution**:
```sql
-- Create ransomware signature mapping table
CREATE TABLE CFG_RANSOMWARE_SIGNATURES (
    SIGNATURE_ID NUMBER,
    THREAT_NAME VARCHAR,
    RANSOMWARE_FAMILY VARCHAR,  -- WannaCry, Ryuk, Maze, etc.
    SEVERITY_OVERRIDE VARCHAR,
    ADDED_DATE DATE,
    SOURCE VARCHAR  -- Threat Intel Feed, Manual, EDR Vendor
);

-- Populate with known ransomware patterns
INSERT INTO CFG_RANSOMWARE_SIGNATURES VALUES
(1, 'Trojan.Ransom%', 'Generic Ransomware', 'CRITICAL', CURRENT_DATE(), 'Manual'),
(2, '%WannaCry%', 'WannaCry', 'CRITICAL', CURRENT_DATE(), 'Threat Intel'),
(3, '%Ryuk%', 'Ryuk', 'CRITICAL', CURRENT_DATE(), 'Threat Intel'),
(4, '%Maze%', 'Maze', 'CRITICAL', CURRENT_DATE(), 'Threat Intel'),
(5, '%REvil%', 'REvil/Sodinokibi', 'CRITICAL', CURRENT_DATE(), 'Threat Intel');

-- Apply classification to threat detection
CREATE VIEW VW_RANSOMWARE_EVENTS_CLASSIFIED AS
SELECT
    t.*,
    r.RANSOMWARE_FAMILY,
    CASE
        WHEN r.RANSOMWARE_FAMILY IS NOT NULL THEN TRUE
        ELSE FALSE
    END as IS_CONFIRMED_RANSOMWARE
FROM (
    SELECT * FROM SYMANTEC_THREATS
    UNION ALL
    SELECT * FROM CROWDSTRIKE
    -- ... other EDR sources
) t
LEFT JOIN CFG_RANSOMWARE_SIGNATURES r
    ON t.THREAT_NAME LIKE r.THREAT_NAME;
```

**Action Items**:
1. ☐ Subscribe to threat intelligence feed (MITRE ATT&CK, CISA)
2. ☐ Create ransomware signature database
3. ☐ Implement weekly threat intelligence updates
4. ☐ Partner with SOC for manual validation

---

### 2. Data Accuracy

#### Issue 1: Duplicate Host Records
**Problem**: Same physical host may appear in multiple systems with different IDs

**Detection**:
```sql
-- Find potential duplicates by hostname/IP
SELECT
    HOSTNAME,
    IP_ADDRESS,
    COUNT(*) as OCCURRENCE_COUNT,
    LISTAGG(DISTINCT SOURCE, ', ') as SOURCES
FROM VW_MASTER_ASSET_INVENTORY
GROUP BY HOSTNAME, IP_ADDRESS
HAVING COUNT(*) > 1
ORDER BY OCCURRENCE_COUNT DESC;
```

**Solution**: Implement master data management (MDM) with golden record logic

---

#### Issue 2: Stale Data
**Problem**: "Last seen" dates may be outdated for inactive systems

**Detection**:
```sql
-- Identify stale assets
SELECT
    SOURCE,
    COUNT(*) as TOTAL_ASSETS,
    COUNT(CASE WHEN LAST_SEEN_DATE < DATEADD('day', -30, CURRENT_DATE()) THEN 1 END) as STALE_30_DAYS,
    COUNT(CASE WHEN LAST_SEEN_DATE < DATEADD('day', -90, CURRENT_DATE()) THEN 1 END) as STALE_90_DAYS
FROM VW_MASTER_ASSET_INVENTORY
GROUP BY SOURCE;
```

**Action Items**:
1. ☐ Define data freshness SLA (e.g., assets must report within 7 days)
2. ☐ Implement automated data quality alerts
3. ☐ Create quarterly asset cleanup process

---

### 3. Data Consistency

#### Issue 1: Agent Status Values Not Standardized
**Problem**: Different EDR tools use different status terminology

**Examples**:
- Qualys: "Healthy" vs. "Unhealthy"
- CrowdStrike: "Normal" vs. "Reduced Functionality"
- Symantec: "Enabled" vs. "Disabled"

**Solution**:
```sql
-- Create standardized agent status mapping
CREATE TABLE CFG_AGENT_STATUS_MAPPING (
    SOURCE_SYSTEM VARCHAR,
    ORIGINAL_STATUS VARCHAR,
    STANDARDIZED_STATUS VARCHAR,  -- Healthy, Degraded, Offline, Unknown
    RISK_LEVEL VARCHAR  -- OK, Warning, Critical
);

-- Apply standardization in transformation layer
CREATE VIEW VW_EDR_AGENT_STATUS_STANDARDIZED AS
SELECT
    e.ENDPOINT_ID,
    e.HOSTNAME,
    e.SOURCE_SYSTEM,
    e.AGENT_STATUS as ORIGINAL_STATUS,
    m.STANDARDIZED_STATUS,
    m.RISK_LEVEL
FROM (
    SELECT 'Qualys' as SOURCE_SYSTEM, * FROM QUALYS_OS
    UNION ALL
    SELECT 'CrowdStrike', * FROM CROWDSTRIKE
    -- ... other sources
) e
LEFT JOIN CFG_AGENT_STATUS_MAPPING m
    ON e.SOURCE_SYSTEM = m.SOURCE_SYSTEM
    AND e.AGENT_STATUS = m.ORIGINAL_STATUS;
```

---

### 4. Data Quality Monitoring

**Recommended Data Quality Checks**:

```sql
-- Create automated DQ monitoring
CREATE OR REPLACE PROCEDURE SP_MONITOR_METRICS_DATA_QUALITY()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
    -- Check 1: Null values in critical fields
    INSERT INTO DQ_METRICS_QUALITY_LOG
    SELECT
        CURRENT_TIMESTAMP() as CHECK_TIME,
        'EDR_COVERAGE' as METRIC_NAME,
        'NULL_CHECK' as CHECK_TYPE,
        COUNT(*) as ISSUE_COUNT,
        CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END as STATUS
    FROM VW_MASTER_ASSET_INVENTORY
    WHERE HOSTNAME IS NULL OR IP_ADDRESS IS NULL;

    -- Check 2: Duplicate records
    INSERT INTO DQ_METRICS_QUALITY_LOG
    SELECT
        CURRENT_TIMESTAMP(),
        'EDR_COVERAGE',
        'DUPLICATE_CHECK',
        COUNT(*),
        CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'WARNING' END
    FROM (
        SELECT HOSTNAME, COUNT(*) as CNT
        FROM VW_MASTER_ASSET_INVENTORY
        GROUP BY HOSTNAME
        HAVING CNT > 1
    );

    -- Check 3: Data freshness
    INSERT INTO DQ_METRICS_QUALITY_LOG
    SELECT
        CURRENT_TIMESTAMP(),
        'EDR_COVERAGE',
        'FRESHNESS_CHECK',
        COUNT(*),
        CASE WHEN COUNT(*) / TOTAL_COUNT < 0.05 THEN 'PASS' ELSE 'WARNING' END
    FROM VW_MASTER_ASSET_INVENTORY
    WHERE LAST_SEEN_DATE < DATEADD('day', -7, CURRENT_DATE())
    CROSS JOIN (SELECT COUNT(*) as TOTAL_COUNT FROM VW_MASTER_ASSET_INVENTORY);

    RETURN 'Data quality checks completed';
END;
$$;

-- Schedule DQ checks to run daily
CREATE TASK TASK_DAILY_DQ_CHECKS
    WAREHOUSE = DEV_WH
    SCHEDULE = 'USING CRON 0 6 * * * UTC'
AS
    CALL SP_MONITOR_METRICS_DATA_QUALITY();
```

---

## Best Practices & Recommendations

### 1. Metric Calculation Best Practices

#### ✅ DO:

1. **Use Snapshot Tables for Point-in-Time Metrics**:
   ```sql
   -- Store daily snapshots for trending
   CREATE TABLE SNAPSHOT_DAILY_EDR_COVERAGE (
       SNAPSHOT_DATE DATE,
       TOTAL_ASSETS NUMBER,
       EDR_PROTECTED NUMBER,
       COVERAGE_PCT FLOAT,
       PRIMARY KEY (SNAPSHOT_DATE)
   );

   -- Populate via daily task
   INSERT INTO SNAPSHOT_DAILY_EDR_COVERAGE
   SELECT
       CURRENT_DATE(),
       COUNT(*) as TOTAL_ASSETS,
       COUNT(CASE WHEN HAS_EDR THEN 1 END) as EDR_PROTECTED,
       EDR_PROTECTED * 100.0 / TOTAL_ASSETS
   FROM VW_MASTER_ASSET_INVENTORY;
   ```

2. **Implement Metric Versioning**:
   ```sql
   -- Track metric definition changes
   CREATE TABLE CFG_METRIC_DEFINITIONS (
       METRIC_ID NUMBER,
       METRIC_NAME VARCHAR,
       METRIC_VERSION NUMBER,  -- Increment when calculation changes
       CALCULATION_LOGIC VARCHAR(4000),
       EFFECTIVE_FROM DATE,
       EFFECTIVE_TO DATE,
       CHANGE_REASON VARCHAR
   );
   ```

3. **Add Data Quality Flags**:
   ```sql
   -- Include confidence scores
   SELECT
       METRIC_NAME,
       METRIC_VALUE,
       DATA_QUALITY_SCORE,  -- 0-100 based on completeness, accuracy, freshness
       CASE
           WHEN DATA_QUALITY_SCORE >= 95 THEN '🟢 High Confidence'
           WHEN DATA_QUALITY_SCORE >= 80 THEN '🟡 Medium Confidence'
           ELSE '🔴 Low Confidence'
       END as CONFIDENCE_LEVEL,
       DATA_QUALITY_ISSUES  -- List of issues affecting the metric
   FROM TBL_KPI_MASTER;
   ```

4. **Implement Threshold Alerting**:
   ```sql
   -- Automated threshold violation detection
   CREATE PROCEDURE SP_CHECK_METRIC_THRESHOLDS()
   AS
   $$
   BEGIN
       -- Check for violations
       INSERT INTO ALERT_METRIC_THRESHOLD_VIOLATIONS
       SELECT
           CURRENT_TIMESTAMP() as ALERT_TIME,
           METRIC_NAME,
           METRIC_VALUE,
           TARGET_THRESHOLD,
           (METRIC_VALUE - TARGET_THRESHOLD) as DEVIATION,
           'THRESHOLD_BREACH' as ALERT_TYPE
       FROM TBL_KPI_MASTER
       WHERE METRIC_VALUE < TARGET_THRESHOLD  -- For "greater than" targets
          OR METRIC_VALUE > TARGET_THRESHOLD  -- For "less than" targets
          AND ALERT_ENABLED = TRUE;
   END;
   $$;
   ```

---

#### ❌ DON'T:

1. **Don't Hardcode Values**:
   ```sql
   -- BAD: Hardcoded threshold
   SELECT
       CASE WHEN EDR_COVERAGE_PCT >= 98 THEN 'Pass' ELSE 'Fail' END
   FROM METRICS;

   -- GOOD: Reference configuration table
   SELECT
       CASE WHEN EDR_COVERAGE_PCT >= t.TARGET_VALUE THEN 'Pass' ELSE 'Fail' END
   FROM METRICS m
   JOIN CFG_METRIC_TARGETS t ON m.METRIC_ID = t.METRIC_ID;
   ```

2. **Don't Mix Timeframes**:
   ```sql
   -- BAD: Inconsistent time windows
   SELECT
       (SELECT COUNT(*) FROM EDR WHERE LAST_SEEN >= CURRENT_DATE() - 7) as EDR_7_DAYS,
       (SELECT COUNT(*) FROM QUALYS WHERE LAST_SCAN >= CURRENT_DATE() - 30) as QUALYS_30_DAYS;

   -- GOOD: Consistent time windows with parameters
   SELECT
       (SELECT COUNT(*) FROM EDR WHERE LAST_SEEN >= :REFERENCE_DATE) as EDR_COUNT,
       (SELECT COUNT(*) FROM QUALYS WHERE LAST_SCAN >= :REFERENCE_DATE) as QUALYS_COUNT;
   ```

3. **Don't Calculate on the Fly in Dashboards**:
   ```sql
   -- BAD: Complex calculation in BI tool query
   -- (causes performance issues and inconsistent results)

   -- GOOD: Pre-calculate and store in KPI table
   CREATE TABLE TBL_KPI_EDR_COVERAGE (
       CALCULATION_DATE DATE,
       METRIC_VALUE FLOAT,
       TARGET_VALUE FLOAT,
       STATUS VARCHAR,
       LAST_REFRESHED TIMESTAMP
   );
   ```

---

### 2. NIST CSF Alignment Best Practices

**Map Every Metric to NIST CSF 2.0**:

```sql
-- Create NIST CSF mapping table
CREATE TABLE CFG_METRIC_NIST_MAPPING (
    METRIC_ID NUMBER,
    METRIC_NAME VARCHAR,
    NIST_FUNCTION VARCHAR,  -- Govern, Identify, Protect, Detect, Respond, Recover
    NIST_CATEGORY VARCHAR,  -- e.g., "GV.IM", "PR.PT", "DE.CM"
    NIST_SUBCATEGORY VARCHAR,  -- Detailed subcategory
    NIST_DESCRIPTION VARCHAR
);

-- Example mappings from the metrics dictionary
INSERT INTO CFG_METRIC_NIST_MAPPING VALUES
(1, 'Cyber-Maturity Score', 'Govern', 'GV.IM', 'GV.IM-03', 'Cybersecurity improvement priorities are established'),
(5, 'EDR Coverage - All Systems', 'Protect', 'PR.PT', 'PR.PT-07', 'Protective technology is configured'),
(6, 'Vuln-Scan Coverage & Agent Health', 'Protect', 'PR.IP', 'PR.IP-05', 'Vulnerability identification is performed'),
(11, 'SOC Ticket Response within SLA', 'Respond', 'RS.MI', 'RS.MI-02', 'Incidents are mitigated');

-- Use in reporting
SELECT
    m.METRIC_NAME,
    m.METRIC_VALUE,
    n.NIST_FUNCTION,
    n.NIST_CATEGORY,
    CASE
        WHEN m.METRIC_VALUE >= m.TARGET_VALUE THEN '✅ Compliant'
        ELSE '❌ Gap'
    END as COMPLIANCE_STATUS
FROM TBL_KPI_MASTER m
JOIN CFG_METRIC_NIST_MAPPING n ON m.METRIC_ID = n.METRIC_ID
ORDER BY n.NIST_FUNCTION, n.NIST_CATEGORY;
```

**NIST CSF Dashboard Example**:
```sql
-- Executive NIST CSF scorecard
CREATE VIEW VW_NIST_CSF_SCORECARD AS
SELECT
    NIST_FUNCTION,
    COUNT(*) as TOTAL_METRICS,
    COUNT(CASE WHEN METRIC_VALUE >= TARGET_VALUE THEN 1 END) as COMPLIANT_METRICS,
    ROUND(COMPLIANT_METRICS * 100.0 / TOTAL_METRICS, 1) as COMPLIANCE_PCT,
    CASE
        WHEN COMPLIANCE_PCT >= 95 THEN '🟢 Excellent'
        WHEN COMPLIANCE_PCT >= 80 THEN '🟡 Good'
        WHEN COMPLIANCE_PCT >= 60 THEN '🟠 Fair'
        ELSE '🔴 Poor'
    END as MATURITY_LEVEL
FROM TBL_KPI_MASTER m
JOIN CFG_METRIC_NIST_MAPPING n ON m.METRIC_ID = n.METRIC_ID
WHERE m.CALCULATION_DATE = CURRENT_DATE()
GROUP BY NIST_FUNCTION
ORDER BY NIST_FUNCTION;
```

---

### 3. Metric Governance

**Establish Metric Ownership**:

```sql
-- Create metric ownership table
CREATE TABLE CFG_METRIC_OWNERSHIP (
    METRIC_ID NUMBER,
    METRIC_NAME VARCHAR,
    OWNER_TEAM VARCHAR,  -- GRC Team, SecOps, Awareness Team, etc.
    OWNER_NAME VARCHAR,
    OWNER_EMAIL VARCHAR,
    REVIEWER_NAME VARCHAR,
    REVIEW_FREQUENCY VARCHAR,  -- Monthly, Quarterly, Annual
    LAST_REVIEW_DATE DATE,
    NEXT_REVIEW_DATE DATE,
    JIRA_BACKLOG_ID VARCHAR
);

-- Example from metrics dictionary
INSERT INTO CFG_METRIC_OWNERSHIP VALUES
(1, 'Cyber-Maturity Score', 'GRC Team', 'TBD', 'grc@GenericCorp.com', 'CISO', 'Quarterly', '2025-06-30', '2025-09-30', 'CYBER-1234'),
(5, 'EDR Coverage - All Systems', 'SecOps', 'TBD', 'secops@GenericCorp.com', 'Sr. Manager SecOps', 'Monthly', '2025-06-30', '2025-07-30', 'CYBER-2002'),
(13, 'Security-Awareness Completion Rate', 'Awareness Team', 'TBD', 'awareness@GenericCorp.com', 'Training Manager', 'Monthly', '2025-06-30', '2025-07-30', 'CYBER-3002');
```

**Implement Change Control**:

```sql
-- Track metric calculation changes
CREATE TABLE AUDIT_METRIC_CHANGES (
    CHANGE_ID NUMBER AUTOINCREMENT,
    METRIC_ID NUMBER,
    CHANGE_TYPE VARCHAR,  -- Calculation, Threshold, Data Source
    OLD_VALUE VARCHAR,
    NEW_VALUE VARCHAR,
    CHANGE_REASON VARCHAR,
    CHANGED_BY VARCHAR,
    CHANGED_DATE TIMESTAMP,
    APPROVED_BY VARCHAR,
    APPROVAL_DATE TIMESTAMP
);
```

---

### 4. Documentation Standards

**Every Metric Should Have**:

1. **Business Definition** (Plain English)
2. **Technical Definition** (SQL pseudo-code)
3. **Data Sources** (Tables and columns)
4. **Calculation Frequency** (Hourly, Daily, Weekly, etc.)
5. **Target/Threshold** (With rationale)
6. **Owner & Reviewer**
7. **Data Quality Requirements**
8. **Known Limitations**

**Example Documentation Template**:
```markdown
## Metric: EDR Coverage - All Systems

### Business Definition
Percentage of in-scope IT assets (servers and workstations) that have an active and healthy Endpoint Detection and Response (EDR) agent installed.

### Why This Matters
Measures the organization's ability to detect and respond to endpoint-based threats. Low coverage indicates blind spots where malware could execute undetected.

### Technical Definition
```sql
SELECT
    COUNT(DISTINCT ENDPOINT_ID) /
    COUNT(DISTINCT HOST_ID) * 100.0 as EDR_COVERAGE_PCT
FROM ASSET_INVENTORY
WHERE ASSET_TYPE IN ('Server', 'Workstation')
    AND LAST_SEEN_DATE >= CURRENT_DATE() - 30;
```

### Data Sources
- **Primary**: DEV_TRANSFORMATION.SECURITY_ANALYTICS.VW_MASTER_ASSET_INVENTORY
- **Supporting**:
  - CISCO_AMP, CROWDSTRIKE, SENTINELONE (EDR platforms)
  - DIM_HOST (Asset inventory)

### Calculation Frequency
Daily @ 02:00 UTC

### Target
≥ 98% of active assets must have EDR coverage

### Rationale for Target
- Industry best practice: 95%+
- GenericCorp elevated to 98% due to regulatory requirements (SOX, GDPR)
- 2% allowance for edge cases (air-gapped systems, legacy equipment)

### Owner
- **Primary**: SecOps Team
- **Reviewer**: Sr. Manager, Security Operations
- **Escalation**: CISO (if < 90%)

### Data Quality Requirements
- Asset inventory must be complete (validated against CMDB quarterly)
- "Last seen" date must be < 30 days for asset to be considered "active"
- EDR agent status must be standardized across platforms

### Known Limitations
1. Does not account for EDR bypass techniques
2. "Healthy" status doesn't guarantee threat detection capability
3. Asset inventory may have lag in decommissioned systems

### Related Metrics
- #4: Maintain EDR Agent Health - All Systems
- #6: Vuln-Scan Coverage & Agent Health
```

---

## SQL Implementation Examples

### Example 1: Complete Implementation for Metric #5 (EDR Coverage)

```sql
-- ============================================================================
-- METRIC #5: EDR COVERAGE - ALL SYSTEMS
-- Target: ≥ 98% of active assets
-- NIST CSF: PR.PT-07
-- ============================================================================

-- STEP 1: Create Master Asset Inventory View
-- ============================================================================
CREATE OR REPLACE VIEW VW_MASTER_ASSET_INVENTORY AS
SELECT
    COALESCE(h.HOST_ID, e.ENDPOINT_ID) as ASSET_ID,
    COALESCE(h.HOSTNAME, e.HOSTNAME) as HOSTNAME,
    COALESCE(h.IP_ADDRESS, e.IP_ADDRESS) as IP_ADDRESS,
    CASE
        WHEN h.OS LIKE '%Server%' THEN 'Server'
        WHEN h.OS LIKE '%Windows%' AND h.OS NOT LIKE '%Server%' THEN 'Workstation'
        WHEN h.OS LIKE '%macOS%' THEN 'Workstation'
        WHEN h.OS LIKE '%Linux%' THEN 'Server'  -- Adjust based on your environment
        ELSE 'Unknown'
    END as DEVICE_TYPE,
    h.OPCO_ID,
    h.LAST_SEEN_DATE,
    DATEDIFF('day', h.LAST_SEEN_DATE, CURRENT_DATE()) as DAYS_SINCE_LAST_SEEN,
    CASE
        WHEN DAYS_SINCE_LAST_SEEN <= 30 THEN TRUE
        ELSE FALSE
    END as IS_ACTIVE
FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_HOST h
FULL OUTER JOIN (
    -- Union all EDR sources
    SELECT ENDPOINT_ID, HOSTNAME, IP_ADDRESS, LAST_SEEN_DATE, 'CISCO_AMP' as EDR_SOURCE
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.CISCO_AMP
    WHERE AGENT_STATUS IN ('Healthy', 'Active')

    UNION ALL

    SELECT ENDPOINT_ID, HOSTNAME, IP_ADDRESS, LAST_SEEN_DATE, 'SENTINELONE'
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.SENTINELONE
    WHERE AGENT_STATUS = 'Active'

    UNION ALL

    SELECT ENDPOINT_ID, HOSTNAME, IP_ADDRESS, LAST_SEEN_DATE, 'TRELLIX'
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.TRELLIX
    WHERE AGENT_STATUS = 'Online'

    UNION ALL

    SELECT ENDPOINT_ID, HOSTNAME, IP_ADDRESS, LAST_SEEN_DATE, 'TREND_MICRO'
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.TREND_MICRO
    WHERE AGENT_STATUS = 'Normal'

    UNION ALL

    SELECT ENDPOINT_ID, HOSTNAME, IP_ADDRESS, LAST_SEEN_DATE, 'SYMANTEC_THREATS'
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.SYMANTEC_THREATS
    WHERE AGENT_STATUS = 'Enabled'

    UNION ALL

    SELECT DEVICE_ID, HOSTNAME, IP_ADDRESS, LAST_SEEN_DATE, 'DEFENDER'
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.DEFENDER
    WHERE STATUS = 'Protected'

    UNION ALL

    SELECT ENDPOINT_ID, HOSTNAME, IP_ADDRESS, LAST_SEEN_DATE, 'CROWDSTRIKE'
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.CROWDSTRIKE
    WHERE STATUS = 'Normal'
) e ON h.HOST_ID = e.ENDPOINT_ID;

-- STEP 2: Create EDR Coverage Calculation View
-- ============================================================================
CREATE OR REPLACE VIEW VW_EDR_COVERAGE_ALL_SYSTEMS AS
WITH asset_counts AS (
    SELECT
        COUNT(*) as TOTAL_ASSETS,
        COUNT(CASE WHEN IS_ACTIVE THEN 1 END) as ACTIVE_ASSETS,
        COUNT(CASE WHEN EDR_SOURCE IS NOT NULL AND IS_ACTIVE THEN 1 END) as EDR_PROTECTED_ASSETS
    FROM VW_MASTER_ASSET_INVENTORY
),
coverage_by_device_type AS (
    SELECT
        DEVICE_TYPE,
        COUNT(*) as TOTAL,
        COUNT(CASE WHEN EDR_SOURCE IS NOT NULL THEN 1 END) as PROTECTED,
        ROUND(PROTECTED * 100.0 / NULLIF(TOTAL, 0), 2) as COVERAGE_PCT
    FROM VW_MASTER_ASSET_INVENTORY
    WHERE IS_ACTIVE = TRUE
    GROUP BY DEVICE_TYPE
),
coverage_by_opco AS (
    SELECT
        o.OPCO_NAME,
        COUNT(*) as TOTAL,
        COUNT(CASE WHEN a.EDR_SOURCE IS NOT NULL THEN 1 END) as PROTECTED,
        ROUND(PROTECTED * 100.0 / NULLIF(TOTAL, 0), 2) as COVERAGE_PCT
    FROM VW_MASTER_ASSET_INVENTORY a
    LEFT JOIN DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_OPCO o ON a.OPCO_ID = o.OPCO_ID
    WHERE a.IS_ACTIVE = TRUE
    GROUP BY o.OPCO_NAME
)
SELECT
    -- Overall metrics
    ac.ACTIVE_ASSETS as TOTAL_ACTIVE_ASSETS,
    ac.EDR_PROTECTED_ASSETS,
    ROUND(ac.EDR_PROTECTED_ASSETS * 100.0 / NULLIF(ac.ACTIVE_ASSETS, 0), 2) as OVERALL_COVERAGE_PCT,

    -- Target comparison
    98.0 as TARGET_PCT,
    CASE
        WHEN OVERALL_COVERAGE_PCT >= 98 THEN '✅ Target Met'
        WHEN OVERALL_COVERAGE_PCT >= 95 THEN '⚠️ Near Target'
        WHEN OVERALL_COVERAGE_PCT >= 90 THEN '🟠 Below Target'
        ELSE '🔴 Critical Gap'
    END as STATUS,

    ROUND(98.0 - OVERALL_COVERAGE_PCT, 2) as GAP_TO_TARGET_PCT,
    CEILING((98.0 - OVERALL_COVERAGE_PCT) * ac.ACTIVE_ASSETS / 100.0) as ASSETS_NEEDED_FOR_TARGET,

    -- Breakdowns
    (SELECT ARRAY_AGG(OBJECT_CONSTRUCT('device_type', DEVICE_TYPE, 'coverage', COVERAGE_PCT))
     FROM coverage_by_device_type) as COVERAGE_BY_DEVICE_TYPE,

    (SELECT ARRAY_AGG(OBJECT_CONSTRUCT('opco', OPCO_NAME, 'coverage', COVERAGE_PCT))
     FROM coverage_by_opco) as COVERAGE_BY_OPCO,

    CURRENT_TIMESTAMP() as CALCULATED_AT
FROM asset_counts ac;

-- STEP 3: Create KPI Table for Historical Tracking
-- ============================================================================
CREATE TABLE IF NOT EXISTS DEV_REPORTING.SECURITY_ANALYTICS.TBL_KPI_EDR_COVERAGE (
    SNAPSHOT_DATE DATE,
    TOTAL_ACTIVE_ASSETS NUMBER,
    EDR_PROTECTED_ASSETS NUMBER,
    COVERAGE_PCT FLOAT,
    TARGET_PCT FLOAT,
    STATUS VARCHAR,
    GAP_TO_TARGET_PCT FLOAT,
    ASSETS_NEEDED_FOR_TARGET NUMBER,
    COVERAGE_BY_DEVICE_TYPE VARIANT,
    COVERAGE_BY_OPCO VARIANT,
    CALCULATED_AT TIMESTAMP,
    PRIMARY KEY (SNAPSHOT_DATE)
);

-- STEP 4: Create Stored Procedure to Calculate and Store
-- ============================================================================
CREATE OR REPLACE PROCEDURE DEV_TRANSFORMATION.SECURITY_ANALYTICS.SP_CALCULATE_KPI_EDR_COVERAGE()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
    -- Insert today's snapshot
    INSERT INTO DEV_REPORTING.SECURITY_ANALYTICS.TBL_KPI_EDR_COVERAGE
    SELECT
        CURRENT_DATE() as SNAPSHOT_DATE,
        TOTAL_ACTIVE_ASSETS,
        EDR_PROTECTED_ASSETS,
        OVERALL_COVERAGE_PCT,
        TARGET_PCT,
        STATUS,
        GAP_TO_TARGET_PCT,
        ASSETS_NEEDED_FOR_TARGET,
        COVERAGE_BY_DEVICE_TYPE,
        COVERAGE_BY_OPCO,
        CALCULATED_AT
    FROM VW_EDR_COVERAGE_ALL_SYSTEMS;

    RETURN 'EDR Coverage KPI calculated successfully for ' || CURRENT_DATE();
END;
$$;

-- STEP 5: Create Scheduled Task for Daily Calculation
-- ============================================================================
CREATE OR REPLACE TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_CALCULATE_EDR_COVERAGE
    WAREHOUSE = DEV_WH
    SCHEDULE = 'USING CRON 0 2 * * * UTC'  -- Daily at 2:00 AM UTC
    COMMENT = 'Calculate EDR Coverage KPI (Metric #5) - Daily'
AS
    CALL DEV_TRANSFORMATION.SECURITY_ANALYTICS.SP_CALCULATE_KPI_EDR_COVERAGE();

-- STEP 6: Activate Task (run as ACCOUNTADMIN)
-- ============================================================================
-- USE ROLE ACCOUNTADMIN;
-- ALTER TASK DEV_TRANSFORMATION.SECURITY_ANALYTICS.TASK_CALCULATE_EDR_COVERAGE RESUME;

-- STEP 7: Create Trend Analysis View
-- ============================================================================
CREATE OR REPLACE VIEW VW_EDR_COVERAGE_TREND AS
SELECT
    SNAPSHOT_DATE,
    COVERAGE_PCT,
    TARGET_PCT,
    STATUS,
    COVERAGE_PCT - LAG(COVERAGE_PCT, 1) OVER (ORDER BY SNAPSHOT_DATE) as CHANGE_FROM_YESTERDAY,
    COVERAGE_PCT - LAG(COVERAGE_PCT, 7) OVER (ORDER BY SNAPSHOT_DATE) as CHANGE_FROM_LAST_WEEK,
    COVERAGE_PCT - LAG(COVERAGE_PCT, 30) OVER (ORDER BY SNAPSHOT_DATE) as CHANGE_FROM_LAST_MONTH,
    CASE
        WHEN CHANGE_FROM_YESTERDAY > 0 THEN '📈 Improving'
        WHEN CHANGE_FROM_YESTERDAY < 0 THEN '📉 Declining'
        ELSE '➡️ Stable'
    END as TREND
FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_KPI_EDR_COVERAGE
WHERE SNAPSHOT_DATE >= DATEADD('day', -90, CURRENT_DATE())
ORDER BY SNAPSHOT_DATE DESC;

-- STEP 8: Create Alert Logic for Threshold Violations
-- ============================================================================
CREATE OR REPLACE PROCEDURE DEV_TRANSFORMATION.SECURITY_ANALYTICS.SP_ALERT_EDR_COVERAGE_THRESHOLD()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
    -- Check if coverage dropped below warning threshold (95%)
    INSERT INTO DEV_TRANSFORMATION.SECURITY_ANALYTICS.ALERT_METRIC_VIOLATIONS
    SELECT
        CURRENT_TIMESTAMP() as ALERT_TIME,
        'EDR_COVERAGE_ALL_SYSTEMS' as METRIC_NAME,
        COVERAGE_PCT as CURRENT_VALUE,
        95.0 as WARNING_THRESHOLD,
        98.0 as TARGET_THRESHOLD,
        'WARNING' as SEVERITY,
        'EDR coverage dropped below 95%. Current: ' || ROUND(COVERAGE_PCT, 2) || '%' as ALERT_MESSAGE,
        FALSE as ACKNOWLEDGED
    FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_KPI_EDR_COVERAGE
    WHERE SNAPSHOT_DATE = CURRENT_DATE()
        AND COVERAGE_PCT < 95.0;

    -- Check if coverage dropped below critical threshold (90%)
    INSERT INTO DEV_TRANSFORMATION.SECURITY_ANALYTICS.ALERT_METRIC_VIOLATIONS
    SELECT
        CURRENT_TIMESTAMP(),
        'EDR_COVERAGE_ALL_SYSTEMS',
        COVERAGE_PCT,
        90.0,
        98.0,
        'CRITICAL',
        'CRITICAL: EDR coverage dropped below 90%. Current: ' || ROUND(COVERAGE_PCT, 2) || '%. Immediate action required.',
        FALSE
    FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_KPI_EDR_COVERAGE
    WHERE SNAPSHOT_DATE = CURRENT_DATE()
        AND COVERAGE_PCT < 90.0;

    RETURN 'EDR Coverage threshold checks completed';
END;
$$;

-- STEP 9: Data Quality Validation
-- ============================================================================
CREATE OR REPLACE VIEW VW_EDR_COVERAGE_DATA_QUALITY AS
WITH dq_checks AS (
    SELECT
        'Asset Count Validation' as CHECK_NAME,
        CASE
            WHEN TOTAL_ACTIVE_ASSETS > 0 THEN 'PASS'
            ELSE 'FAIL - No active assets found'
        END as CHECK_STATUS,
        TOTAL_ACTIVE_ASSETS as CHECK_VALUE
    FROM VW_EDR_COVERAGE_ALL_SYSTEMS

    UNION ALL

    SELECT
        'Null Hostname Check',
        CASE
            WHEN COUNT(*) = 0 THEN 'PASS'
            ELSE 'WARNING - ' || COUNT(*) || ' assets with null hostname'
        END,
        COUNT(*)
    FROM VW_MASTER_ASSET_INVENTORY
    WHERE HOSTNAME IS NULL AND IS_ACTIVE = TRUE

    UNION ALL

    SELECT
        'Duplicate Asset Check',
        CASE
            WHEN COUNT(*) = 0 THEN 'PASS'
            ELSE 'WARNING - ' || COUNT(*) || ' duplicate hostnames found'
        END,
        COUNT(*)
    FROM (
        SELECT HOSTNAME, COUNT(*) as CNT
        FROM VW_MASTER_ASSET_INVENTORY
        WHERE IS_ACTIVE = TRUE
        GROUP BY HOSTNAME
        HAVING CNT > 1
    )

    UNION ALL

    SELECT
        'Stale Data Check',
        CASE
            WHEN COUNT(*) * 100.0 / TOTAL < 5 THEN 'PASS'
            ELSE 'WARNING - ' || ROUND(COUNT(*) * 100.0 / TOTAL, 1) || '% assets not seen in 7 days'
        END,
        COUNT(*)
    FROM VW_MASTER_ASSET_INVENTORY
    WHERE DAYS_SINCE_LAST_SEEN > 7 AND DAYS_SINCE_LAST_SEEN <= 30
    CROSS JOIN (SELECT COUNT(*) as TOTAL FROM VW_MASTER_ASSET_INVENTORY WHERE IS_ACTIVE = TRUE)
)
SELECT
    CHECK_NAME,
    CHECK_STATUS,
    CHECK_VALUE,
    CASE
        WHEN CHECK_STATUS LIKE 'PASS%' THEN '✅'
        WHEN CHECK_STATUS LIKE 'WARNING%' THEN '⚠️'
        ELSE '❌'
    END as STATUS_ICON,
    CURRENT_TIMESTAMP() as CHECKED_AT
FROM dq_checks;

-- STEP 10: Executive Summary Query
-- ============================================================================
CREATE OR REPLACE VIEW VW_EDR_COVERAGE_EXECUTIVE_SUMMARY AS
SELECT
    'EDR Coverage - All Systems' as METRIC_NAME,
    'PR.PT-07' as NIST_CSF_CATEGORY,
    ROUND(COVERAGE_PCT, 1) || '%' as CURRENT_VALUE,
    '≥ 98%' as TARGET,
    STATUS,
    CASE
        WHEN COVERAGE_PCT >= TARGET_PCT THEN '✅ Compliant'
        ELSE '❌ Non-Compliant'
    END as COMPLIANCE_STATUS,
    ASSETS_NEEDED_FOR_TARGET as ASSETS_TO_REMEDIATE,
    'SecOps Team' as OWNER,
    'Daily' as REPORTING_CADENCE,
    CALCULATED_AT as LAST_UPDATED
FROM DEV_REPORTING.SECURITY_ANALYTICS.TBL_KPI_EDR_COVERAGE
WHERE SNAPSHOT_DATE = CURRENT_DATE();
```

---

## Conclusion & Next Steps

### Critical Success Factors

1. **Integration Priority**: Focus on Archer, ServiceNow, MetaCompliance first
2. **Data Quality**: Establish asset inventory single source of truth
3. **Metric Governance**: Assign clear ownership and review processes
4. **Automation**: Automate all metric calculations via scheduled tasks
5. **Transparency**: Include data quality indicators with every metric

### Recommended Next Steps

**Week 1-2**:
1. ☐ Review and approve this feasibility analysis
2. ☐ Prioritize metric implementation (confirm Top 13)
3. ☐ Obtain API access for Archer, ServiceNow, MetaCompliance
4. ☐ Implement Quick Win metrics (#5, 6, 7)

**Week 3-4**:
5. ☐ Complete Phase 1: Deploy 9 operational metrics
6. ☐ Create executive dashboard for Quick Wins
7. ☐ Start Archer integration (Phase 2)

**Month 2-4**:
8. ☐ Complete Phase 2: RSA Archer, ServiceNow, MetaCompliance
9. ☐ Deliver Top 13 executive metrics
10. ☐ Establish metric governance process

**Month 5-6**:
11. ☐ Complete Phase 3: Advanced metrics
12. ☐ Achieve 100% metric coverage (37/37)
13. ☐ Implement continuous improvement process

---

## Appendix: Metric Status Summary Table

| # | Metric Name | Status | Data Source | Integration Needed | Effort (hrs) | Priority |
|---|-------------|--------|-------------|-------------------|--------------|----------|
| 1 | Cyber-Maturity Score | 🔴 | Archer | Yes | 40 | HIGH |
| 2 | Policy-Exception Rate | 🔴 | Archer | Yes | 32 | HIGH |
| 3 | Third-Party Risk Score | 🟡 | Archer+BitSight | Partial | 48 | HIGH |
| 4 | Days Since Last Ransomware | 🟡 | EDR+ServiceNow | Partial | 56 | MEDIUM |
| 5 | EDR Coverage - All | ✅ | EDR Tools | No | 12 | HIGH |
| 6 | Vuln-Scan Coverage & Health | ✅ | Qualys | No | 8 | HIGH |
| 7 | Email Domain Security | ✅ | Proofpoint | No | 12 | MEDIUM |
| 8 | Phishing Click Rate | 🔴 | MetaCompliance | Yes | 40 | HIGH |
| 9 | MTTE - Malicious Email | 🟡 | Proofpoint+ServiceNow | Partial | 48 | MEDIUM |
| 10 | SIEM Log-Source Coverage | 🟡 | Splunk | Partial | 56 | MEDIUM |
| 11 | SOC Ticket Response SLA | 🔴 | ServiceNow | Yes | 48 | HIGH |
| 12 | Incident Response Effort | 🔴 | ServiceNow | Yes | 56 | MEDIUM |
| 13 | Security Awareness Completion | 🔴 | MetaCompliance | Yes | 48 | HIGH |
| ... | (Remaining 24 metrics) | ... | ... | ... | ... | ... |

**Total Estimated Effort**: ~756 hours (≈ 19 weeks, 1 FTE)

---

**Document Status**: DRAFT FOR REVIEW
**Next Review Date**: TBD
**Approval Required**: Data Architecture Team, CyberSec SECURITY_ANALYTICS Team

**END OF REPORT**
