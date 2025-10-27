# SECURITY_ANALYTICS Data Warehouse - Data Dictionary

## Table of Contents
- [Overview](#overview)
- [How to Use This Dictionary](#how-to-use-this-dictionary)
- [Service Catalog](#service-catalog)
- [Endpoint Security Services](#endpoint-security-services)
- [Email Security Services](#email-security-services)
- [Vulnerability Management Services](#vulnerability-management-services)
- [Threat Intelligence Services](#threat-intelligence-services)
- [Cloud Security Services](#cloud-security-services)
- [Identity & Access Management Services](#identity--access-management-services)
- [IT Service Management](#it-service-management)
- [Asset Management Services](#asset-management-services)
- [SIEM & Monitoring Services](#siem--monitoring-services)
- [Metadata Repository Tables](#metadata-repository-tables)
- [Common Data Elements](#common-data-elements)
- [Data Types Reference](#data-types-reference)

---

## Overview

This Data Dictionary provides comprehensive documentation for all tables, columns, and data elements in the SECURITY_ANALYTICS Data Warehouse. It serves as the authoritative reference for understanding the structure and meaning of data across 20+ integrated security services.

### Dictionary Statistics

| Metric | Count |
|--------|-------|
| **Total Services** | 20 services |
| **Total Tables** | 180 tables |
| **Total Columns** | 2,206 columns |
| **Data Layers** | 2 (Landing, Transformation) |
| **Total Data Volume** | 32.5M+ rows |

### Data Layers Explained

#### Landing Layer (DEV_LANDING.SECURITY_ANALYTICS)
- **Purpose**: Raw data storage as received from source systems
- **Characteristics**:
  - Minimal transformations
  - Original data types from APIs
  - Historical snapshots with extraction timestamps
  - Retained for 90 days
- **Tables**: 74 tables (41.1%)
- **Naming Convention**: `{SERVICE}_{ENTITY}` (e.g., `SENTINELONE_AGENTS`)

#### Transformation Layer (DEV_TRANSFORMATION.SECURITY_ANALYTICS)
- **Purpose**: Processed, cleansed, and enriched data for analytics
- **Characteristics**:
  - Business logic applied
  - Data quality validations
  - Standardized formats
  - Denormalized for performance
  - Retained for 2 years
- **Tables**: 106 tables (58.9%)
- **Naming Convention**: `{SERVICE}_{ENTITY}_TRANSFORMED` or descriptive names

---

## How to Use This Dictionary

### Finding Information

#### By Service
1. Locate your service in the [Service Catalog](#service-catalog)
2. Navigate to the service-specific section
3. Review table listings and column definitions

#### By Table Name
Use your browser's Find function (Ctrl+F / Cmd+F) to search for specific table names.

#### By Column Name
Search for column names to find all tables containing that field.

### Reading Table Definitions

Each table entry includes:
- **Table Name**: Full Snowflake identifier
- **Layer**: Landing or Transformation
- **Purpose**: Business description
- **Key Columns**: Primary keys and important identifiers
- **Row Count**: Approximate volume (as of last metadata refresh)
- **Refresh Schedule**: How often data is updated
- **Retention**: How long data is kept

### Column Information

Column definitions include:
- **Column Name**: Exact Snowflake identifier
- **Data Type**: Snowflake data type (VARCHAR, NUMBER, TIMESTAMP_LTZ, etc.)
- **Nullable**: Whether NULL values are allowed
- **Description**: Business meaning and usage
- **Sample Values**: Examples (where appropriate)

### Metadata Currency

This dictionary is automatically updated by the metadata extraction process:
- **Refresh Frequency**: Daily at 6:00 AM EST
- **Source**: Snowflake INFORMATION_SCHEMA + manual documentation
- **Last Updated**: See footer timestamp
- **For Live Metadata**: Query `DEV_TRANSFORMATION.METADATA_EXPORTS` tables

---

## Service Catalog

Complete listing of all integrated security services:

| # | Service Name | Category | Tables | Columns | Primary Use Case |
|---|-------------|----------|--------|---------|------------------|
| 1 | [SentinelOne](#sentinelone) | Endpoint Security | 11 | 76 | Endpoint detection and response (EDR) |
| 2 | [CrowdStrike](#crowdstrike) | Endpoint Security | 13 | 89 | Next-gen antivirus and EDR |
| 3 | [Defender](#microsoft-defender) | Endpoint Security | 11 | 67 | Microsoft endpoint protection |
| 4 | [Qualys](#qualys) | Vulnerability Mgmt | 18 | 156 | Vulnerability scanning and assessment |
| 5 | [Tenable](#tenable) | Vulnerability Mgmt | 0 | 0 | Vulnerability management (planned) |
| 6 | [Proofpoint](#proofpoint) | Email Security | 2 | 23 | Email threat protection |
| 7 | [CybelAngel](#cybelangel) | Threat Intelligence | 9 | 112 | Digital risk protection |
| 8 | [ZeroFox](#zerofox) | Threat Intelligence | 9 | 78 | Social media threat monitoring |
| 9 | [Intel_Threats](#intel-threats) | Threat Intelligence | 8 | 94 | Threat intelligence feeds |
| 10 | [BitSight](#bitsight) | Threat Intelligence | 7 | 52 | Security ratings and risk monitoring |
| 11 | [Zscaler](#zscaler) | Cloud Security | 6 | 145 | Cloud security platform |
| 12 | [Splunk](#splunk) | SIEM & Monitoring | 12 | 98 | Security information and event management |
| 13 | [ServiceNow](#servicenow) | ITSM | 2 | 36 | IT service management and ticketing |
| 14 | [Leviat](#leviat) | Asset Management | 15 | 146 | Asset and configuration management |
| 15 | [Symantec](#symantec) | Endpoint Security | 9 | 123 | Endpoint protection and DLP |
| 16 | [Cisco_AMP](#cisco-amp) | Endpoint Security | 13 | 87 | Cisco Advanced Malware Protection |
| 17 | [Trellix](#trellix) | Endpoint Security | 6 | 45 | Unified security platform (McAfee rebranded) |
| 18 | [TrendMicro](#trend-micro) | Endpoint Security | 9 | 76 | Endpoint security and cloud protection |
| 19 | [McAfee](#mcafee) | Endpoint Security | 6 | 43 | Legacy endpoint protection |
| 20 | [Sophos](#sophos) | Endpoint Security | 6 | 42 | Next-gen endpoint protection |
| 21 | [Ancon](#ancon) | Other | 8 | 67 | Custom security analytics |

**Total**: 21 service categories | 180 tables | 2,206 columns

---

## Endpoint Security Services

### SentinelOne

**Purpose**: Autonomous endpoint detection and response (EDR) platform providing real-time threat prevention, detection, and response.

**Category**: Endpoint Security
**Total Tables**: 11 (3 Landing + 8 Transformation)
**Total Columns**: 76 columns
**Data Volume**: ~12,700 rows

#### Tables Overview

| Table Name | Layer | Purpose | Key Columns | Row Count |
|------------|-------|---------|-------------|-----------|
| SENTINELONE_AGENTS | Landing | Raw agent inventory | AGENT_ID, COMPUTER_NAME | ~3,200 |
| SENTINELONE_THREATS | Landing | Raw threat detections | THREAT_ID, CLASSIFICATION | ~8,500 |
| SENTINELONE_ACTIVITIES | Landing | Agent activity logs | ACTIVITY_ID, ACTIVITY_TYPE | ~1,000 |
| SENTINELONE_AGENTS_TRANSFORMED | Transformation | Processed agent data | AGENT_KEY, STATUS | ~3,200 |
| SENTINELONE_THREATS_TRANSFORMED | Transformation | Enriched threat data | THREAT_KEY, SEVERITY | ~8,500 |

#### Key Column Definitions

**SENTINELONE_AGENTS**:
- `AGENT_ID` (VARCHAR) - Unique agent identifier from SentinelOne
- `COMPUTER_NAME` (VARCHAR) - Hostname of the endpoint
- `NETWORK_STATUS` (VARCHAR) - Connection status: Connected, Disconnected, Connecting
- `DOMAIN` (VARCHAR) - Active Directory domain
- `OS_TYPE` (VARCHAR) - Operating system: Windows, Linux, macOS
- `OS_VERSION` (VARCHAR) - Full OS version string
- `AGENT_VERSION` (VARCHAR) - SentinelOne agent version
- `LAST_ACTIVE_DATE` (TIMESTAMP_LTZ) - Last time agent communicated
- `IS_ACTIVE` (BOOLEAN) - Whether agent is currently active
- `SITE_NAME` (VARCHAR) - Organizational site assignment
- `EXTERNAL_IP` (VARCHAR) - Public IP address
- `IP_ADDRESSES` (VARCHAR) - Internal IP addresses (comma-separated)
- `MAC_ADDRESSES` (VARCHAR) - Network adapter MAC addresses
- `THREAT_COUNT` (NUMBER) - Count of threats detected on this endpoint

**SENTINELONE_THREATS**:
- `THREAT_ID` (VARCHAR) - Unique threat identifier
- `AGENT_ID` (VARCHAR) - Foreign key to SENTINELONE_AGENTS
- `THREAT_NAME` (VARCHAR) - Name/description of the threat
- `CLASSIFICATION` (VARCHAR) - Malware, Trojan, Ransomware, etc.
- `CONFIDENCE_LEVEL` (VARCHAR) - Detection confidence: Suspicious, Malicious
- `MITIGATION_STATUS` (VARCHAR) - Active, Mitigated, Quarantined, Removed
- `CREATED_DATE` (TIMESTAMP_LTZ) - When threat was first detected
- `FILE_PATH` (VARCHAR) - Full path to malicious file
- `FILE_HASH_SHA1` (VARCHAR) - SHA1 hash of file
- `FILE_HASH_SHA256` (VARCHAR) - SHA256 hash of file
- `PROCESS_NAME` (VARCHAR) - Name of malicious process
- `SEVERITY` (VARCHAR) - Critical, High, Medium, Low

**Data Refresh**: Daily at 2:00 AM EST
**Retention**: Landing 90 days, Transformation 2 years

---

### CrowdStrike

**Purpose**: Cloud-native endpoint protection platform (EPP) with EDR capabilities.

**Category**: Endpoint Security
**Total Tables**: 13 (5 Landing + 8 Transformation)
**Total Columns**: 89 columns
**Data Volume**: ~7,150 rows

#### Tables Overview

| Table Name | Layer | Purpose | Key Columns | Row Count |
|------------|-------|---------|-------------|-----------|
| CROWDSTRIKE_DETECTIONS | Landing | Raw threat detections | DETECTION_ID | ~5,000 |
| CROWDSTRIKE_HOSTS | Landing | Endpoint inventory | HOST_ID, HOSTNAME | ~2,000 |
| CROWDSTRIKE_INCIDENTS | Landing | Security incidents | INCIDENT_ID | ~150 |

#### Key Column Definitions

**CROWDSTRIKE_HOSTS**:
- `HOST_ID` (VARCHAR) - CrowdStrike unique device identifier
- `HOSTNAME` (VARCHAR) - Device hostname
- `PLATFORM_NAME` (VARCHAR) - Windows, Mac, Linux
- `OS_VERSION` (VARCHAR) - Operating system version
- `SENSOR_VERSION` (VARCHAR) - CrowdStrike Falcon sensor version
- `FIRST_SEEN` (TIMESTAMP_LTZ) - Initial detection date
- `LAST_SEEN` (TIMESTAMP_LTZ) - Last communication with console
- `STATUS` (VARCHAR) - Normal, Contained, Lift_Containment_Pending
- `PREVENTION_POLICY_ID` (VARCHAR) - Assigned prevention policy

**CROWDSTRIKE_DETECTIONS**:
- `DETECTION_ID` (VARCHAR) - Unique detection identifier
- `HOST_ID` (VARCHAR) - Foreign key to CROWDSTRIKE_HOSTS
- `SEVERITY` (NUMBER) - 1-5 severity scale
- `TACTIC` (VARCHAR) - MITRE ATT&CK tactic
- `TECHNIQUE` (VARCHAR) - MITRE ATT&CK technique
- `STATUS` (VARCHAR) - New, In_Progress, True_Positive, False_Positive, Ignored
- `FILENAME` (VARCHAR) - Associated filename
- `FILEPATH` (VARCHAR) - Full file path
- `MD5` (VARCHAR) - MD5 hash
- `SHA256` (VARCHAR) - SHA256 hash
- `CMDLINE` (VARCHAR) - Command line arguments

**Data Refresh**: Daily at 2:30 AM EST
**Retention**: Landing 90 days, Transformation 2 years

---

### Microsoft Defender

**Purpose**: Microsoft's integrated endpoint protection solution for Windows environments.

**Category**: Endpoint Security
**Total Tables**: 11 (4 Landing + 7 Transformation)
**Total Columns**: 67 columns
**Data Volume**: ~26,300 rows

#### Key Column Definitions

**DEFENDER_ALERTS**:
- `ALERT_ID` (VARCHAR) - Unique alert identifier
- `ALERT_CREATION_TIME` (TIMESTAMP_LTZ) - When alert was generated
- `SEVERITY` (VARCHAR) - Informational, Low, Medium, High
- `CATEGORY` (VARCHAR) - Malware, Suspicious_Activity, Credential_Access, etc.
- `DETECTION_SOURCE` (VARCHAR) - Antivirus, EDR, SmartScreen, etc.
- `TITLE` (VARCHAR) - Human-readable alert title
- `DESCRIPTION` (VARCHAR) - Detailed description
- `MACHINE_ID` (VARCHAR) - Device identifier
- `STATUS` (VARCHAR) - New, InProgress, Resolved
- `ASSIGNED_TO` (VARCHAR) - Analyst assigned to investigate

**Data Refresh**: Daily at 3:00 AM EST
**Retention**: Landing 90 days, Transformation 2 years

---

### Qualys

**Purpose**: Comprehensive vulnerability management and policy compliance platform.

**Category**: Vulnerability Management
**Total Tables**: 18 (4 Landing + 14 Transformation)
**Total Columns**: 156 columns
**Data Volume**: ~18.1M rows (largest service by volume)

#### Tables Overview

| Table Name | Layer | Purpose | Key Columns | Row Count |
|------------|-------|---------|-------------|-----------|
| QUALYS_HOST_DETECTIONS | Landing | Vulnerability findings | DETECTION_ID, QID | ~17M |
| QUALYS_HOSTS | Landing | Asset inventory | HOST_ID, IP_ADDRESS | ~50K |
| QUALYS_KB | Landing | Vulnerability knowledge base | QID, TITLE | ~25K |
| QUALYS_ASSET_GROUPS | Landing | Asset groupings | GROUP_ID | ~500 |

#### Key Column Definitions

**QUALYS_HOSTS**:
- `HOST_ID` (NUMBER) - Qualys unique host identifier
- `IP_ADDRESS` (VARCHAR) - Primary IP address
- `TRACKING_METHOD` (VARCHAR) - IP, DNS, NETBIOS
- `DNS_NAME` (VARCHAR) - Fully qualified domain name
- `NETBIOS_NAME` (VARCHAR) - NetBIOS hostname
- `OS` (VARCHAR) - Detected operating system
- `LAST_SCAN_DATETIME` (TIMESTAMP_LTZ) - Most recent scan timestamp
- `LAST_VM_SCANNED_DATE` (TIMESTAMP_LTZ) - Last vulnerability scan
- `LAST_VM_AUTH_SCANNED_DATE` (TIMESTAMP_LTZ) - Last authenticated scan

**QUALYS_HOST_DETECTIONS**:
- `DETECTION_ID` (VARCHAR) - Unique detection record
- `HOST_ID` (NUMBER) - Foreign key to QUALYS_HOSTS
- `QID` (NUMBER) - Qualys vulnerability ID (links to KB)
- `TYPE` (VARCHAR) - Confirmed, Potential, Information
- `SEVERITY` (NUMBER) - 1-5 severity level
- `FIRST_FOUND_DATETIME` (TIMESTAMP_LTZ) - Initial detection
- `LAST_FOUND_DATETIME` (TIMESTAMP_LTZ) - Most recent occurrence
- `TIMES_FOUND` (NUMBER) - Detection count
- `STATUS` (VARCHAR) - Active, Fixed, Re-Opened
- `PORT` (NUMBER) - Affected port number
- `PROTOCOL` (VARCHAR) - TCP, UDP, ICMP

**QUALYS_KB** (Knowledge Base):
- `QID` (NUMBER) - Primary key, vulnerability identifier
- `TITLE` (VARCHAR) - Vulnerability title
- `VULN_TYPE` (VARCHAR) - Vulnerability category
- `SEVERITY_LEVEL` (NUMBER) - Base severity 1-5
- `CVSS_BASE` (NUMBER) - CVSS 2.0 base score
- `CVSS3_BASE` (NUMBER) - CVSS 3.0 base score
- `THREAT_INTELLIGENCE` (VARCHAR) - Threat data
- `CVE_LIST` (VARCHAR) - Associated CVE IDs (comma-separated)
- `SOLUTION` (VARCHAR) - Remediation guidance
- `PUBLISHED_DATETIME` (TIMESTAMP_LTZ) - Publication date
- `PATCHABLE` (BOOLEAN) - Whether patch is available

**Data Refresh**: Daily at 1:00 AM EST
**Retention**: Landing 90 days, Transformation 2 years
**Special Note**: Largest dataset - queries may require filtering by date

---

### Symantec

**Purpose**: Symantec Endpoint Protection and Data Loss Prevention.

**Category**: Endpoint Security
**Total Tables**: 9 (4 Landing + 5 Transformation)
**Total Columns**: 123 columns
**Data Volume**: ~2.6M rows

#### Key Column Definitions

**SYMANTEC_ENDPOINTS**:
- `COMPUTER_ID` (VARCHAR) - Unique device identifier
- `COMPUTER_NAME` (VARCHAR) - Hostname
- `IP_ADDRESS` (VARCHAR) - IP address
- `OS` (VARCHAR) - Operating system
- `PATTERN_VERSION` (VARCHAR) - Antivirus definition version
- `LAST_UPDATE_TIME` (TIMESTAMP_LTZ) - Last definition update
- `ONLINE_STATUS` (VARCHAR) - Online, Offline
- `GROUP_NAME` (VARCHAR) - Management group assignment

**Data Refresh**: Daily at 4:00 AM EST

---

### Cisco AMP

**Purpose**: Cisco Advanced Malware Protection for endpoints.

**Category**: Endpoint Security
**Total Tables**: 13 (7 Landing + 6 Transformation)
**Total Columns**: 87 columns
**Data Volume**: ~63,500 rows

**Data Refresh**: Daily at 4:30 AM EST

---

### Trellix

**Purpose**: Unified security platform (formerly McAfee Enterprise).

**Category**: Endpoint Security
**Total Tables**: 6 (1 Landing + 5 Transformation)
**Total Columns**: 45 columns
**Data Volume**: ~68,500 rows

**Data Refresh**: Daily at 5:00 AM EST

---

### Trend Micro

**Purpose**: Endpoint security and hybrid cloud protection.

**Category**: Endpoint Security
**Total Tables**: 9 (1 Landing + 8 Transformation)
**Total Columns**: 76 columns
**Data Volume**: ~800 rows

**Data Refresh**: Daily at 5:30 AM EST

---

### McAfee

**Purpose**: Legacy McAfee endpoint protection (being migrated to Trellix).

**Category**: Endpoint Security
**Total Tables**: 6 (1 Landing + 5 Transformation)
**Total Columns**: 43 columns
**Data Volume**: ~580 rows

**Data Refresh**: Weekly (being phased out)

---

### Sophos

**Purpose**: Next-generation endpoint protection with synchronized security.

**Category**: Endpoint Security
**Total Tables**: 6 (1 Landing + 5 Transformation)
**Total Columns**: 42 columns
**Data Volume**: ~1,480 rows

**Data Refresh**: Daily at 6:00 AM EST

---

## Email Security Services

### Proofpoint

**Purpose**: Email threat protection, compliance, and data loss prevention.

**Category**: Email Security
**Total Tables**: 2 (2 Landing + 0 Transformation)
**Total Columns**: 23 columns
**Data Volume**: ~207,000 rows

#### Tables Overview

| Table Name | Layer | Purpose | Key Columns | Row Count |
|------------|-------|---------|-------------|-----------|
| PROOFPOINT_MESSAGES | Landing | Email message logs | MESSAGE_ID, SENDER | ~200K |
| PROOFPOINT_CLICKS | Landing | URL click tracking | CLICK_ID, URL | ~7K |

#### Key Column Definitions

**PROOFPOINT_MESSAGES**:
- `MESSAGE_ID` (VARCHAR) - Unique message identifier
- `GUID` (VARCHAR) - Proofpoint global unique ID
- `SENDER` (VARCHAR) - Email sender address
- `RECIPIENT` (VARCHAR) - Email recipient address (may be array)
- `SUBJECT` (VARCHAR) - Email subject line
- `MESSAGE_TIME` (TIMESTAMP_LTZ) - When email was processed
- `THREAT_TYPE` (VARCHAR) - Spam, Phish, Malware, Impostor, etc.
- `CLASSIFICATION` (VARCHAR) - Classification category
- `MODULES_RUN` (VARCHAR) - Detection modules executed
- `MESSAGE_SIZE` (NUMBER) - Size in bytes
- `QUARANTINE_FOLDER` (VARCHAR) - Quarantine location (if applicable)
- `QUARANTINE_RULE` (VARCHAR) - Rule that triggered quarantine
- `POLICY_ROUTES` (VARCHAR) - Applied routing policies
- `SENDER_IP` (VARCHAR) - Originating IP address
- `SPAM_SCORE` (NUMBER) - Calculated spam score
- `PHISH_SCORE` (NUMBER) - Calculated phishing score

**PROOFPOINT_CLICKS**:
- `CLICK_ID` (VARCHAR) - Unique click event identifier
- `MESSAGE_ID` (VARCHAR) - Associated message (FK to MESSAGES)
- `URL` (VARCHAR) - Clicked URL
- `CLICK_TIME` (TIMESTAMP_LTZ) - When URL was clicked
- `USER_AGENT` (VARCHAR) - Browser user agent string
- `SENDER_IP` (VARCHAR) - IP of user who clicked
- `THREAT_URL` (VARCHAR) - Classified threat URL
- `THREAT_STATUS` (VARCHAR) - Active, Cleared
- `CLASSIFICATION` (VARCHAR) - Malware, Phish, Spam

**Data Refresh**: Hourly (most frequent refresh in warehouse)
**Retention**: Landing 90 days
**Special Note**: Transformation layer being developed

---

## Vulnerability Management Services

### Qualys
See [Endpoint Security Services - Qualys](#qualys) for complete details.

### Tenable

**Purpose**: Vulnerability management platform (planned integration).

**Category**: Vulnerability Management
**Total Tables**: 0 (not yet deployed)
**Status**: Infrastructure ready, awaiting data source connection

---

## Threat Intelligence Services

### CybelAngel

**Purpose**: Digital risk protection platform monitoring the surface, deep, and dark web.

**Category**: Threat Intelligence
**Total Tables**: 9 (1 Landing + 8 Transformation)
**Total Columns**: 112 columns
**Data Volume**: ~400 rows

#### Tables Overview

| Table Name | Layer | Purpose | Key Columns | Row Count |
|------------|-------|---------|-------------|-----------|
| CYBELANGEL_REPORTS | Landing | Raw threat intelligence reports | REPORT_ID | ~400 |

#### Key Column Definitions

**CYBELANGEL_REPORTS**:
- `REPORT_ID` (VARCHAR) - Unique report identifier
- `TITLE` (VARCHAR) - Report title
- `SEVERITY` (VARCHAR) - Low, Medium, High, Critical
- `CATEGORY` (VARCHAR) - Data_Leak, Brand_Abuse, Phishing, Credential_Leak, etc.
- `SOURCE` (VARCHAR) - Where threat was detected (Surface Web, Deep Web, Dark Web)
- `DETECTION_DATE` (TIMESTAMP_LTZ) - When threat was detected
- `STATUS` (VARCHAR) - Open, In_Progress, Resolved, False_Positive
- `ASSIGNED_TO` (VARCHAR) - Analyst assigned
- `DESCRIPTION` (VARCHAR) - Detailed description
- `AFFECTED_ASSETS` (VARCHAR) - Assets at risk
- `REMEDIATION_ACTIONS` (VARCHAR) - Recommended actions
- `URL` (VARCHAR) - Source URL (if applicable)
- `TAGS` (VARCHAR) - Classification tags

**Data Refresh**: Daily at 7:00 AM EST
**Retention**: Landing 90 days, Transformation indefinite (threat intelligence archive)

---

### ZeroFox

**Purpose**: Social media and digital threat intelligence.

**Category**: Threat Intelligence
**Total Tables**: 9 (2 Landing + 7 Transformation)
**Total Columns**: 78 columns
**Data Volume**: ~210,000 rows

#### Key Column Definitions

**ZEROFOX_ALERTS**:
- `ALERT_ID` (VARCHAR) - Unique alert identifier
- `ENTITY_TYPE` (VARCHAR) - Brand, Executive, Domain, Social_Account
- `SEVERITY` (VARCHAR) - Low, Medium, High, Critical
- `ALERT_TYPE` (VARCHAR) - Impersonation, Phishing, Data_Leak, Trademark_Infringement
- `NETWORK` (VARCHAR) - Facebook, Twitter, Instagram, LinkedIn, Web, etc.
- `CONTENT_TYPE` (VARCHAR) - Post, Profile, Page, Account, Website
- `PERPETRATOR` (VARCHAR) - Account/user creating the threat
- `ESCALATED` (BOOLEAN) - Whether alert was escalated
- `REVIEWED` (BOOLEAN) - Whether alert was reviewed
- `STATUS` (VARCHAR) - Open, Closed, Takedown_Requested, Takedown_Accepted
- `TIMESTAMP` (TIMESTAMP_LTZ) - Alert creation time

**Data Refresh**: Daily at 7:30 AM EST

---

### Intel_Threats

**Purpose**: Aggregated threat intelligence feeds from multiple sources.

**Category**: Threat Intelligence
**Total Tables**: 8 (2 Landing + 6 Transformation)
**Total Columns**: 94 columns
**Data Volume**: ~2.1M rows

#### Key Column Definitions

**INTEL_THREATS_INDICATORS**:
- `INDICATOR_ID` (VARCHAR) - Unique indicator identifier
- `INDICATOR_TYPE` (VARCHAR) - IP, Domain, URL, FileHash, Email
- `INDICATOR_VALUE` (VARCHAR) - The actual indicator (IP address, hash, etc.)
- `THREAT_TYPE` (VARCHAR) - Malware, Phishing, C2, Botnet, APT
- `CONFIDENCE` (NUMBER) - Confidence score 0-100
- `SEVERITY` (VARCHAR) - Low, Medium, High, Critical
- `FIRST_SEEN` (TIMESTAMP_LTZ) - First observed
- `LAST_SEEN` (TIMESTAMP_LTZ) - Most recently observed
- `SOURCE` (VARCHAR) - Threat feed source
- `TAGS` (VARCHAR) - Classification tags
- `MITRE_TACTICS` (VARCHAR) - MITRE ATT&CK tactics
- `ASSOCIATED_MALWARE` (VARCHAR) - Known malware families

**Data Refresh**: Hourly
**Retention**: Landing 30 days, Transformation 1 year

---

### BitSight

**Purpose**: Third-party security ratings and risk monitoring.

**Category**: Threat Intelligence / Risk Management
**Total Tables**: 7 (1 Landing + 6 Transformation)
**Total Columns**: 52 columns
**Data Volume**: ~2,450 rows

#### Key Column Definitions

**BITSIGHT_COMPANY_RATINGS**:
- `COMPANY_GUID` (VARCHAR) - Unique company identifier
- `COMPANY_NAME` (VARCHAR) - Company name
- `RATING` (NUMBER) - Security rating 250-900 (higher is better)
- `RATING_DATE` (DATE) - Date of rating
- `INDUSTRY` (VARCHAR) - Industry classification
- `RISK_VECTOR_BOTNET` (NUMBER) - Botnet infections score
- `RISK_VECTOR_SPAM` (NUMBER) - Spam propagation score
- `RISK_VECTOR_MALWARE` (NUMBER) - Malware servers score
- `RISK_VECTOR_PATCHING_CADENCE` (NUMBER) - Patch management score
- `RISK_VECTOR_DNSHEALTH` (NUMBER) - DNS health score
- `RISK_VECTOR_SSL` (NUMBER) - SSL configuration score

**Data Refresh**: Weekly
**Retention**: Transformation 3 years (historical trend analysis)

---

## Cloud Security Services

### Zscaler

**Purpose**: Cloud security platform for secure internet and SaaS access.

**Category**: Cloud Security / Secure Web Gateway
**Total Tables**: 6 (1 Landing + 5 Transformation)
**Total Columns**: 145 columns
**Data Volume**: ~9M rows (second largest by volume)

#### Tables Overview

| Table Name | Layer | Purpose | Key Columns | Row Count |
|------------|-------|---------|-------------|-----------|
| ZSCALER_WEB_LOGS | Landing | Web traffic logs | LOG_ID, USER, URL | ~9M |

#### Key Column Definitions

**ZSCALER_WEB_LOGS**:
- `LOG_ID` (VARCHAR) - Unique log entry identifier
- `DATETIME` (TIMESTAMP_LTZ) - Request timestamp
- `USER` (VARCHAR) - Username
- `DEPARTMENT` (VARCHAR) - User department
- `LOCATION` (VARCHAR) - Geographic location
- `URL` (VARCHAR) - Requested URL
- `URL_CATEGORY` (VARCHAR) - Zscaler URL category
- `URL_SUPER_CATEGORY` (VARCHAR) - Top-level category
- `ACTION` (VARCHAR) - Allowed, Blocked, Cautioned
- `THREAT_CATEGORY` (VARCHAR) - If threat detected
- `THREAT_NAME` (VARCHAR) - Specific threat name
- `FILE_TYPE` (VARCHAR) - Downloaded file type
- `BANDWIDTH_THROTTLE` (VARCHAR) - Throttling applied
- `UPLOAD_BYTES` (NUMBER) - Bytes uploaded
- `DOWNLOAD_BYTES` (NUMBER) - Bytes downloaded
- `RESPONSE_CODE` (NUMBER) - HTTP response code
- `REQUEST_METHOD` (VARCHAR) - GET, POST, etc.
- `MALWARE_CLASS` (VARCHAR) - Malware classification
- `DLP_DICTIONARIES` (VARCHAR) - DLP policies triggered

**Data Refresh**: Daily at 8:00 AM EST (processes previous day's logs)
**Retention**: Landing 30 days, Transformation 6 months (high volume)
**Special Note**: Large dataset - always filter by date range in queries

---

## Identity & Access Management Services

### Okta

**Purpose**: Cloud-based identity and access management platform.

**Status**: Planned integration (not yet deployed)
**Tables**: 0

### Azure AD

**Purpose**: Microsoft Azure Active Directory identity services.

**Status**: Planned integration (not yet deployed)
**Tables**: 0

---

## IT Service Management

### ServiceNow

**Purpose**: IT service management, incident tracking, and change management.

**Category**: ITSM
**Total Tables**: 2 (2 Landing + 0 Transformation)
**Total Columns**: 36 columns
**Data Volume**: ~24,650 rows

#### Tables Overview

| Table Name | Layer | Purpose | Key Columns | Row Count |
|------------|-------|---------|-------------|-----------|
| SERVICENOW_INCIDENTS | Landing | IT incidents | SYS_ID, NUMBER | ~20K |
| SERVICENOW_CHANGES | Landing | Change requests | SYS_ID, NUMBER | ~4,650 |

#### Key Column Definitions

**SERVICENOW_INCIDENTS**:
- `SYS_ID` (VARCHAR) - ServiceNow unique system ID (PK)
- `NUMBER` (VARCHAR) - User-friendly incident number (e.g., INC0012345)
- `OPENED_AT` (TIMESTAMP_LTZ) - When incident was created
- `CLOSED_AT` (TIMESTAMP_LTZ) - When incident was resolved
- `SHORT_DESCRIPTION` (VARCHAR) - Brief description
- `DESCRIPTION` (VARCHAR) - Full description
- `STATE` (VARCHAR) - New, In_Progress, Resolved, Closed
- `PRIORITY` (VARCHAR) - 1-Critical, 2-High, 3-Moderate, 4-Low, 5-Planning
- `URGENCY` (VARCHAR) - 1-High, 2-Medium, 3-Low
- `IMPACT` (VARCHAR) - 1-High, 2-Medium, 3-Low
- `CATEGORY` (VARCHAR) - Software, Hardware, Network, Security, etc.
- `SUBCATEGORY` (VARCHAR) - Specific sub-classification
- `ASSIGNED_TO` (VARCHAR) - Current assignee
- `ASSIGNMENT_GROUP` (VARCHAR) - Assigned team
- `CALLER` (VARCHAR) - User who reported incident
- `RESOLUTION_CODE` (VARCHAR) - Resolution category
- `RESOLUTION_NOTES` (VARCHAR) - Resolution description

**SERVICENOW_CHANGES**:
- `SYS_ID` (VARCHAR) - ServiceNow unique system ID (PK)
- `NUMBER` (VARCHAR) - Change request number (e.g., CHG0012345)
- `TYPE` (VARCHAR) - Standard, Normal, Emergency
- `STATE` (VARCHAR) - New, Assess, Authorize, Scheduled, Implement, Review, Closed
- `RISK` (VARCHAR) - High, Moderate, Low
- `IMPACT` (VARCHAR) - 1-High, 2-Medium, 3-Low
- `SHORT_DESCRIPTION` (VARCHAR) - Brief description
- `DESCRIPTION` (VARCHAR) - Full change description
- `JUSTIFICATION` (VARCHAR) - Business justification
- `IMPLEMENTATION_PLAN` (VARCHAR) - How change will be implemented
- `BACKOUT_PLAN` (VARCHAR) - Rollback plan
- `TEST_PLAN` (VARCHAR) - Testing approach
- `REQUESTED_BY` (VARCHAR) - Change requestor
- `ASSIGNED_TO` (VARCHAR) - Change implementer
- `START_DATE` (TIMESTAMP_LTZ) - Scheduled start
- `END_DATE` (TIMESTAMP_LTZ) - Scheduled end

**Data Refresh**: Daily at 9:00 AM EST
**Retention**: Landing 90 days, Transformation planned
**Special Note**: Security incidents are subset - filter by category

---

## Asset Management Services

### Leviat

**Purpose**: Custom asset and configuration management system.

**Category**: Asset Management
**Total Tables**: 15 (8 Landing + 7 Transformation)
**Total Columns**: 146 columns
**Data Volume**: ~3,000 rows (Landing only)

#### Tables Overview

| Table Name | Layer | Purpose | Key Columns | Row Count |
|------------|-------|---------|-------------|-----------|
| LEVIAT_ASSETS | Landing | Asset inventory | ASSET_ID, ASSET_NAME | ~3,000 |

#### Key Column Definitions

**LEVIAT_ASSETS**:
- `ASSET_ID` (VARCHAR) - Unique asset identifier
- `ASSET_NAME` (VARCHAR) - Asset name/description
- `ASSET_TYPE` (VARCHAR) - Server, Workstation, Network_Device, etc.
- `SERIAL_NUMBER` (VARCHAR) - Hardware serial number
- `MANUFACTURER` (VARCHAR) - Hardware manufacturer
- `MODEL` (VARCHAR) - Hardware model
- `LOCATION` (VARCHAR) - Physical location
- `DEPARTMENT` (VARCHAR) - Owning department
- `OWNER` (VARCHAR) - Asset owner
- `STATUS` (VARCHAR) - Active, Inactive, Retired, Disposed
- `PURCHASE_DATE` (DATE) - Acquisition date
- `WARRANTY_EXPIRATION` (DATE) - Warranty end date
- `IP_ADDRESS` (VARCHAR) - Primary IP address
- `MAC_ADDRESS` (VARCHAR) - Primary MAC address
- `HOSTNAME` (VARCHAR) - Network hostname

**Data Refresh**: Daily at 10:00 AM EST
**Retention**: Landing 90 days
**Special Note**: Transformation layer empty - ETL being developed

---

### Ancon

**Purpose**: Custom security analytics and asset tracking.

**Category**: Other / Custom Analytics
**Total Tables**: 8 (2 Landing + 6 Transformation)
**Total Columns**: 67 columns
**Data Volume**: ~2,830 rows

**Data Refresh**: Daily at 10:30 AM EST

---

## SIEM & Monitoring Services

### Splunk

**Purpose**: Security information and event management (SIEM) platform.

**Category**: SIEM & Log Analytics
**Total Tables**: 12 (6 Landing + 6 Transformation)
**Total Columns**: 98 columns
**Data Volume**: ~67,600 rows

#### Tables Overview

| Table Name | Layer | Purpose | Key Columns | Row Count |
|------------|-------|---------|-------------|-----------|
| SPLUNK_NOTABLE_EVENTS | Landing | Security events from correlation searches | EVENT_ID | ~50K |
| SPLUNK_AUTHENTICATION | Landing | Authentication logs | LOG_ID, USER | ~15K |
| SPLUNK_FIREWALL | Landing | Firewall logs | LOG_ID, SOURCE_IP | ~2K |

#### Key Column Definitions

**SPLUNK_NOTABLE_EVENTS**:
- `EVENT_ID` (VARCHAR) - Unique event identifier
- `TIME` (TIMESTAMP_LTZ) - Event timestamp
- `SEARCH_NAME` (VARCHAR) - Correlation search that triggered event
- `SEVERITY` (VARCHAR) - Informational, Low, Medium, High, Critical
- `OWNER` (VARCHAR) - Analyst assigned to investigate
- `STATUS` (VARCHAR) - New, In_Progress, Pending, Resolved, Closed
- `URGENCY` (VARCHAR) - Low, Medium, High, Critical
- `SRC` (VARCHAR) - Source system/IP
- `DEST` (VARCHAR) - Destination system/IP
- `USER` (VARCHAR) - Affected user
- `SIGNATURE` (VARCHAR) - Detection signature/rule
- `CATEGORY` (VARCHAR) - Malware, Intrusion, Policy_Violation, etc.
- `RULE_DESCRIPTION` (VARCHAR) - Why event was notable

**Data Refresh**: Hourly
**Retention**: Landing 7 days, Transformation 90 days

---

## Metadata Repository Tables

The metadata repository stores information about the data warehouse itself. These tables are automatically populated by the metadata extraction process.

### Schema: DEV_TRANSFORMATION.METADATA

#### TABLE_REGISTRY

**Purpose**: Master catalog of all data warehouse tables

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| TABLE_ID | NUMBER | Primary key (auto-increment) |
| SERVICE_NAME | VARCHAR(100) | Service this table belongs to |
| DATABASE_NAME | VARCHAR(100) | DEV_LANDING or DEV_TRANSFORMATION |
| SCHEMA_NAME | VARCHAR(100) | Schema name (usually SECURITY_ANALYTICS) |
| TABLE_NAME | VARCHAR(255) | Table name |
| FULL_TABLE_NAME | VARCHAR(500) | Fully qualified name: DB.SCHEMA.TABLE |
| TABLE_TYPE | VARCHAR(50) | BASE TABLE, VIEW, MATERIALIZED VIEW |
| DATA_LAYER | VARCHAR(50) | Landing or Transformation |
| ROW_COUNT | NUMBER | Approximate row count |
| BYTES | NUMBER | Table size in bytes |
| LAST_ALTERED | TIMESTAMP_LTZ | Last DDL or DML operation |
| CREATED_DATE | TIMESTAMP_LTZ | When metadata record was created |
| LAST_UPDATED | TIMESTAMP_LTZ | When metadata was last refreshed |

**Current Rows**: 180

---

#### COLUMN_METADATA

**Purpose**: Detailed column-level metadata for all tables

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| COLUMN_ID | NUMBER | Primary key (auto-increment) |
| TABLE_ID | NUMBER | Foreign key to TABLE_REGISTRY |
| SERVICE_NAME | VARCHAR(100) | Service this column belongs to |
| TABLE_NAME | VARCHAR(255) | Parent table name |
| COLUMN_NAME | VARCHAR(255) | Column name |
| ORDINAL_POSITION | NUMBER | Column position in table (1-based) |
| DATA_TYPE | VARCHAR(100) | Snowflake data type |
| IS_NULLABLE | VARCHAR(3) | YES or NO |
| CHARACTER_MAXIMUM_LENGTH | NUMBER | Max length for VARCHAR |
| NUMERIC_PRECISION | NUMBER | Precision for NUMBER |
| NUMERIC_SCALE | NUMBER | Scale for NUMBER |
| CREATED_DATE | TIMESTAMP_LTZ | When metadata record was created |
| LAST_UPDATED | TIMESTAMP_LTZ | When metadata was last refreshed |

**Current Rows**: 2,206

---

#### SERVICE_CATALOG

**Purpose**: Master list of all security services

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| SERVICE_ID | NUMBER | Primary key (auto-increment) |
| SERVICE_NAME | VARCHAR(100) | Unique service name |
| SERVICE_CATEGORY | VARCHAR(100) | Endpoint Security, Email Security, etc. |
| DESCRIPTION | VARCHAR(500) | Service description |
| IS_ACTIVE | BOOLEAN | Whether service is currently active |
| CREATED_DATE | TIMESTAMP_LTZ | When service was added |

**Current Rows**: 21

---

#### PROCEDURE_EXECUTION_LOG

**Purpose**: Audit log of metadata refresh executions

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| EXECUTION_ID | NUMBER | Primary key (auto-increment) |
| PROCEDURE_NAME | VARCHAR(255) | SP_REFRESH_METADATA |
| EXECUTION_START | TIMESTAMP_LTZ | When execution started |
| EXECUTION_END | TIMESTAMP_LTZ | When execution completed |
| STATUS | VARCHAR(50) | SUCCESS, FAILED, RUNNING |
| ERROR_MESSAGE | VARCHAR(5000) | Error details (if failed) |
| TABLES_PROCESSED | NUMBER | Count of tables processed |
| COLUMNS_PROCESSED | NUMBER | Count of columns processed |
| ROWS_PROCESSED | NUMBER | Total rows scanned |
| EXECUTION_DURATION_SECONDS | NUMBER | Duration in seconds |

**Retention**: Indefinite (audit trail)

---

## Common Data Elements

### Standard Columns

Many tables share common column patterns:

#### Identifiers
- `*_ID` - Primary key identifiers (VARCHAR or NUMBER)
- `SYS_ID` - System-generated unique ID (typically ServiceNow)
- `GUID` - Globally unique identifier (typically VARCHAR(36))

#### Timestamps
- `CREATED_DATE` / `CREATED_AT` - Record creation timestamp
- `LAST_UPDATED` / `UPDATED_AT` - Last modification timestamp
- `EXTRACTION_TIMESTAMP` - When data was extracted from source (Landing tables)
- `*_DATETIME` - Generic timestamp fields

#### Status & Classification
- `STATUS` - Current state of the record
- `SEVERITY` - Low, Medium, High, Critical
- `PRIORITY` - 1-5 or Low/Medium/High
- `CATEGORY` / `CLASSIFICATION` - Type classification

#### Network & Identity
- `IP_ADDRESS` - IPv4 or IPv6 address
- `MAC_ADDRESS` - Network adapter MAC address
- `HOSTNAME` / `COMPUTER_NAME` - Device hostname
- `USER` / `USERNAME` - User identifier
- `EMAIL` / `EMAIL_ADDRESS` - Email address

#### Hashes
- `MD5` / `FILE_HASH_MD5` - MD5 hash (VARCHAR(32))
- `SHA1` / `FILE_HASH_SHA1` - SHA1 hash (VARCHAR(40))
- `SHA256` / `FILE_HASH_SHA256` - SHA256 hash (VARCHAR(64))

---

## Data Types Reference

### Snowflake Data Types Used

| Data Type | Description | Example Values | Common Usage |
|-----------|-------------|----------------|--------------|
| VARCHAR(n) | Variable-length string | 'SentinelOne', 'example@email.com' | Text fields, identifiers, descriptions |
| NUMBER(p,s) | Numeric with precision/scale | 123, 45.67 | Counts, scores, IDs |
| TIMESTAMP_LTZ | Timestamp with local timezone | 2025-10-24 10:30:00 -0400 | All timestamp fields |
| DATE | Date without time | 2025-10-24 | Birth dates, expiration dates |
| BOOLEAN | True/false | TRUE, FALSE | Flags, yes/no fields |
| VARIANT | Semi-structured (JSON) | {"key": "value"} | API responses, flexible schemas |
| ARRAY | Array of values | ['tag1', 'tag2'] | Lists, multiple values |

### Typical Field Lengths

| Field Type | VARCHAR Length | Notes |
|------------|---------------|-------|
| Email addresses | VARCHAR(255) | Standard length |
| URLs | VARCHAR(2000) | Longer for query parameters |
| Descriptions | VARCHAR(5000) | Variable, may be longer |
| Identifiers | VARCHAR(100) | Sufficient for most IDs |
| Names | VARCHAR(255) | Hostnames, usernames, etc. |
| IP addresses | VARCHAR(45) | IPv6 compatible |
| Hashes (SHA256) | VARCHAR(64) | Fixed length |

---

## Appendix

### Related Documentation

- [WIKI_01_STREAMLIT_APPS.md](WIKI_01_STREAMLIT_APPS.md) - Application catalog
- [WIKI_02_POWER_BI.md](WIKI_02_POWER_BI.md) - Power BI roadmap
- [WIKI_03_METADATA_EXTRACTION.md](WIKI_03_METADATA_EXTRACTION.md) - Metadata automation
- [WIKI_04_DATA_GOVERNANCE.md](WIKI_04_DATA_GOVERNANCE.md) - Governance framework
- [WIKI_06_BEST_PRACTICES.md](WIKI_06_BEST_PRACTICES.md) - Development best practices

### Querying Live Metadata

For the most current metadata, query the metadata repository directly:

```sql
-- All tables for a service
SELECT * FROM DEV_TRANSFORMATION.METADATA.VW_TABLE_CATALOG
WHERE SERVICE_NAME = 'SentinelOne';

-- All columns for a table
SELECT * FROM DEV_TRANSFORMATION.METADATA.VW_COLUMN_CATALOG
WHERE TABLE_NAME = 'SENTINELONE_AGENTS'
ORDER BY ORDINAL_POSITION;

-- Service summary
SELECT * FROM DEV_TRANSFORMATION.METADATA.VW_SERVICE_SUMMARY
ORDER BY TABLE_COUNT DESC;
```

### Dictionary Maintenance

- **Automated Updates**: Table/column metadata updated daily via SP_REFRESH_METADATA
- **Manual Updates**: Business descriptions and documentation maintained by Data Stewards
- **Version Control**: Dictionary changes tracked in Git repository
- **Review Cycle**: Quarterly review by Data Governance Committee

### Contact for Data Dictionary Questions

| Topic | Contact |
|-------|---------|
| Service-Specific Questions | Data Steward for that service (see WIKI_04) |
| Technical Metadata | Data Engineering Team |
| Business Definitions | Service Business Owner |
| General Questions | data.governance@CompanyX.com |

---

**Document Status**: Production Release v1.0
**Last Metadata Refresh**: 2025-10-24 06:00:00 EST
**Total Services Documented**: 20 active + 1 planned
**Total Tables Documented**: 180 tables
**Total Columns Documented**: 2,206 columns
**Author**: GenericCorp Data Engineering Team
**Maintained By**: Data Governance Council & Data Stewards
