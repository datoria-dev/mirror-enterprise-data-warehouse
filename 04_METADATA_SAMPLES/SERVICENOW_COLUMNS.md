# ServiceNow - Available Columns

**Table:** `DEV_LANDING.SECURITY_ANALYTICS.SNOW`
**Row Count:** 24,650 rows
**Last Updated:** 2025-10-24

## Column List

Based on the sample data extracted, the SNOW table contains the following columns:

1. `COMPUTER_NAME` - Text - Computer hostname
2. `MANUFACTURER` - Text - Hardware manufacturer (Dell Inc., VMware, Lenovo, Microsoft)
3. `MODEL` - Text - Device model
4. `BIOS_SERIAL_NUMBER` - Text - BIOS serial number
5. `COMPUTERTYPES` - Text - Type classification (Desktop, Notebook, Virtual Server, Virtual Workstation)
6. `COMPUTERENVIRONMENT` - Text - Environment classification
7. `COMPUTERLOCATION` - Text - Physical location
8. `COMPUTERCLASSIFICATION` - Text - Security/business classification
9. `COMPUTERINSCOPE` - Text - In scope indicator
10. `PROCESSOR_TYPE` - Text - CPU model
11. `PROCESSORS` - Number - Number of physical processors
12. `PROCESSOR_CORES` - Number - Total CPU cores
13. `LOGICAL_PROCESSORS` - Number - Logical processors (with hyperthreading)
14. `OPERATING_SYSTEM` - Text - OS name and version
15. `DOMAIN_NAME` - Text - Active Directory domain
16. `OSPRODUCTKEY` - Text - Windows product key
17. `OSLICENSEKEY` - Text - Windows license key
18. `IAASLICENSEDOS` - Boolean - IaaS licensed indicator
19. `ORGANISATION` - Text - Organization/Business unit
20. `MOST_FREQUENT_USER` - Text - Primary user (DOMAIN\username format)
21. `LAST_SCANNED` - Date - Last inventory scan date (format: DD/MM/YYYY)
22. `STATUS` - Text - Device status (Active, Inactive, etc.)
23. `CLIENT_VERSION` - Text - Agent version
24. `CLIENT_CONFIGURATION` - Text - Agent configuration name
25. `MSIVERSION` - Text - MSI package version

## Sample Values

### Computer Types
- Desktop
- Notebook
- Virtual Server
- Virtual Workstation

### Manufacturers
- Dell Inc.
- VMware, Inc.
- LENOVO
- Microsoft Corporation

### Operating Systems
- Windows 10 Pro
- Windows 11 Pro
- Windows 10 Pro for Workstations
- SUSE LINUX Enterprise Server 12 for SAP Applications (Linux)

### Domains
- USER
- JBRINEY
- ROM01
- NETHERLANDS
- null (some computers)

### Status Values
- Active

## Useful Queries for Streamlit App

### 1. Recent Active Computers
```sql
SELECT
    COMPUTER_NAME,
    MANUFACTURER,
    MODEL,
    OPERATING_SYSTEM,
    MOST_FREQUENT_USER,
    LAST_SCANNED,
    STATUS
FROM DEV_LANDING.SECURITY_ANALYTICS.SNOW
WHERE STATUS = 'Active'
  AND TRY_TO_DATE(LAST_SCANNED, 'DD/MM/YYYY') >= DATEADD(day, -30, CURRENT_DATE())
ORDER BY TRY_TO_DATE(LAST_SCANNED, 'DD/MM/YYYY') DESC
LIMIT 100;
```

### 2. Computers by Type
```sql
SELECT
    COMPUTERTYPES,
    COUNT(*) as COUNT,
    COUNT(DISTINCT MANUFACTURER) as UNIQUE_MANUFACTURERS
FROM DEV_LANDING.SECURITY_ANALYTICS.SNOW
WHERE STATUS = 'Active'
GROUP BY COMPUTERTYPES
ORDER BY COUNT DESC;
```

### 3. Computers by Manufacturer
```sql
SELECT
    MANUFACTURER,
    COMPUTERTYPES,
    COUNT(*) as COUNT
FROM DEV_LANDING.SECURITY_ANALYTICS.SNOW
WHERE STATUS = 'Active'
GROUP BY MANUFACTURER, COMPUTERTYPES
ORDER BY MANUFACTURER, COUNT DESC;
```

### 4. Operating System Distribution
```sql
SELECT
    OPERATING_SYSTEM,
    COUNT(*) as COUNT,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as PERCENTAGE
FROM DEV_LANDING.SECURITY_ANALYTICS.SNOW
WHERE STATUS = 'Active'
GROUP BY OPERATING_SYSTEM
ORDER BY COUNT DESC;
```

### 5. Computers by Organization
```sql
SELECT
    ORGANISATION,
    COUNT(*) as TOTAL_COMPUTERS,
    COUNT(DISTINCT COMPUTERTYPES) as DEVICE_TYPES
FROM DEV_LANDING.SECURITY_ANALYTICS.SNOW
WHERE STATUS = 'Active'
GROUP BY ORGANISATION
ORDER BY TOTAL_COMPUTERS DESC;
```

### 6. Client Version Distribution
```sql
SELECT
    CLIENT_VERSION,
    COUNT(*) as COUNT
FROM DEV_LANDING.SECURITY_ANALYTICS.SNOW
WHERE STATUS = 'Active'
  AND CLIENT_VERSION IS NOT NULL
GROUP BY CLIENT_VERSION
ORDER BY COUNT DESC;
```

### 7. Outdated Scans (Not scanned in last 30 days)
```sql
SELECT
    COMPUTER_NAME,
    MANUFACTURER,
    MODEL,
    LAST_SCANNED,
    DATEDIFF(day, TRY_TO_DATE(LAST_SCANNED, 'DD/MM/YYYY'), CURRENT_DATE()) as DAYS_SINCE_SCAN
FROM DEV_LANDING.SECURITY_ANALYTICS.SNOW
WHERE STATUS = 'Active'
  AND TRY_TO_DATE(LAST_SCANNED, 'DD/MM/YYYY') < DATEADD(day, -30, CURRENT_DATE())
ORDER BY TRY_TO_DATE(LAST_SCANNED, 'DD/MM/YYYY') ASC
LIMIT 100;
```

## Important Notes

1. **Date Format:** `LAST_SCANNED` is stored as text in format 'DD/MM/YYYY', use `TRY_TO_DATE(LAST_SCANNED, 'DD/MM/YYYY')` to convert
2. **Null Values:** Some fields like `COMPUTERLOCATION`, `COMPUTERENVIRONMENT`, `MSIVERSION` have many null values
3. **User Format:** `MOST_FREQUENT_USER` is in format 'DOMAIN\username' or null
4. **Boolean Values:** `IAASLICENSEDOS` appears to be stored as text 'true'/'false'

## Streamlit App Suggestions

### Key Metrics to Display
1. Total Active Computers
2. Computers by Type (Desktop vs Notebook vs Virtual)
3. Computers by Manufacturer
4. OS Distribution (Windows 10 vs 11)
5. Computers not scanned recently (outdated inventory)
6. Client Version compliance

### Filters to Provide
- Computer Type (Desktop, Notebook, Virtual Server, Virtual Workstation)
- Manufacturer
- Operating System
- Organization
- Status
- Date Range (Last Scanned)

### Visualizations
- Pie chart: Computer Types distribution
- Bar chart: Top manufacturers
- Bar chart: OS distribution
- Timeline: Scans over time
- Table: Detailed computer list

---

**Source:** `DEV_LANDING.SECURITY_ANALYTICS.SNOW`
**Sample Size:** 100 rows
**Total Rows:** 24,650
