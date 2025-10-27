# API Integration Best Practices - SECURITY_ANALYTICS Data Warehouse

## 🏗️ Architecture Decision: Landing vs. Transformation

### ✅ RECOMMENDED: APIs → DEV_LANDING (Raw/Bronze Layer)

**Rationale**: Based on your 3-layer medallion architecture:

```
External APIs
    ↓
DEV_LANDING (Layer 1 - Bronze/Raw)
    • Raw JSON/CSV data
    • Minimal transformation
    • Historical preservation
    ↓
DEV_TRANSFORMATION (Layer 2 - Silver/Curated)
    • Business logic applied
    • Star schema (dimensions + facts)
    • Data quality checks
    ↓
DEV_REPORTING (Layer 3 - Gold/Analytics)
    • Aggregations and KPIs
    • Views for dashboards
```

---

## 📐 Architecture Pattern by API Integration Type

### Pattern 1: Native Connector (e.g., ServiceNow)

```
ServiceNow API
    ↓
Snowflake Native Connector (Managed)
    ↓
SERVICENOW_CONNECTOR.RAW_DATA (Dedicated DB - Landing Equivalent)
    • Raw ServiceNow tables
    • Automatic CDC sync
    ↓
DEV_TRANSFORMATION.SERVICENOW_V2 (Transformation)
    • Business rules applied
    • MERGE statements for updates
    ↓
DEV_REPORTING.VW_SERVICENOW_* (Reporting)
    • Aggregated views
```

**Use When**:
- Native connector available
- High data volume (>100K records)
- Frequent updates (every 15-30 min)
- Mission-critical data

---

### Pattern 2: REST API Custom Integration (e.g., CrowdStrike, SentinelOne)

```
External REST API
    ↓
Python Script (Orchestrator)
    • Authentication (OAuth 2.0/API Key)
    • Pagination handling
    • Error retry logic
    ↓
AWS S3 / Azure Blob (Staging - Optional)
    • Raw JSON files
    • Date-partitioned folders
    ↓
DEV_LANDING.{SERVICE} (Landing Tables)
    • Raw JSON stored in VARIANT column
    • Metadata tracking (ingestion_timestamp, source_file)
    ↓
Snowflake Tasks (Scheduled Transformation)
    ↓
DEV_TRANSFORMATION.{SERVICE} (Transformation)
    • Flatten JSON to structured tables
    • Apply business rules
    ↓
DEV_REPORTING.VW_{SERVICE}_* (Reporting)
```

**Use When**:
- No native connector available
- Medium data volume (10K-100K records)
- Moderate update frequency (hourly/daily)
- Full control over extraction logic needed

---

### Pattern 3: Batch File Integration (e.g., CSV/Excel exports)

```
External System Export
    ↓
AWS S3 / Azure Blob
    • CSV/Excel files
    • Date-partitioned
    ↓
Snowpipe (Auto-ingestion)
    ↓
DEV_LANDING.{SERVICE} (Landing Tables)
    • Raw CSV data
    ↓
DEV_TRANSFORMATION.{SERVICE} (Transformation)
    ↓
DEV_REPORTING (Reporting)
```

**Use When**:
- No API available
- Low update frequency (daily/weekly)
- Simple data structure

---

## 🎯 Best Practices for API Integrations

### 1. ✅ ALWAYS Land Raw Data First (DEV_LANDING)

**Why**:
- **Data lineage**: Full audit trail from source to reporting
- **Reprocessing**: Can rerun transformations without API calls
- **Historical preservation**: Raw data never lost
- **Debugging**: Easy to troubleshoot transformation issues
- **Schema evolution**: Handle API schema changes gracefully

**Anti-Pattern (DON'T DO)**:
```python
# ❌ BAD: Transform during extraction
data = api.get_incidents()
transformed = transform_incidents(data)  # Business logic during extraction
snowflake.insert(transformed)  # Goes directly to TRANSFORMATION layer
```

**Correct Pattern (DO THIS)**:
```python
# ✅ GOOD: Land raw, transform separately
raw_data = api.get_incidents()
snowflake.insert_raw(raw_data)  # DEV_LANDING
# Transformation happens later via Snowflake Task
```

---

### 2. ✅ Use VARIANT Column for JSON Storage

**Landing Table Design**:
```sql
CREATE TABLE DEV_LANDING.{SERVICE}.{TABLE}_RAW (
    -- Metadata
    ingestion_id VARCHAR(32) DEFAULT UUID_STRING(),
    ingestion_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    source_file VARCHAR(500),

    -- Raw data (entire JSON payload)
    raw_data VARIANT NOT NULL,

    -- Partition key (for performance)
    ingestion_date DATE DEFAULT CURRENT_DATE(),

    -- Primary key
    PRIMARY KEY (ingestion_id)
)
CLUSTER BY (ingestion_date);
```

**Benefits**:
- Schema-agnostic (API changes don't break landing)
- Fast ingestion (no transformation overhead)
- Full JSON preserved (nested objects, arrays)
- Easy to query with JSON path: `raw_data:field::TYPE`

---

### 3. ✅ Implement Incremental Extraction

**Tracking Table**:
```sql
CREATE TABLE DEV_TRANSFORMATION.METADATA.API_EXTRACTION_LOG (
    extraction_id INTEGER AUTOINCREMENT PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    api_endpoint VARCHAR(500) NOT NULL,
    extraction_type VARCHAR(50), -- FULL, INCREMENTAL
    last_extraction_timestamp TIMESTAMP_LTZ,
    records_extracted INTEGER,
    extraction_status VARCHAR(50), -- SUCCESS, FAILED, PARTIAL
    error_message TEXT,
    execution_start TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    execution_end TIMESTAMP_LTZ
);
```

**Python Implementation**:
```python
def get_last_extraction_timestamp(service, endpoint):
    query = """
        SELECT last_extraction_timestamp
        FROM DEV_TRANSFORMATION.METADATA.API_EXTRACTION_LOG
        WHERE service_name = %s
          AND api_endpoint = %s
          AND extraction_status = 'SUCCESS'
        ORDER BY extraction_id DESC
        LIMIT 1
    """
    result = snowflake.execute(query, (service, endpoint))
    return result[0][0] if result else datetime.now() - timedelta(days=7)
```

---

### 4. ✅ Implement Idempotency

**Use Unique Keys**:
```sql
-- Transformation with MERGE for idempotency
MERGE INTO DEV_TRANSFORMATION.CROWDSTRIKE.DETECTIONS tgt
USING (
    SELECT
        raw_data:detection_id::VARCHAR AS detection_id,
        raw_data:device_id::VARCHAR AS device_id,
        raw_data:severity::VARCHAR AS severity,
        TRY_CAST(raw_data:timestamp::VARCHAR AS TIMESTAMP_LTZ) AS detection_time
    FROM DEV_LANDING.CROWDSTRIKE.DETECTIONS_RAW
    WHERE ingestion_date >= CURRENT_DATE - 1
) src
ON tgt.detection_id = src.detection_id
WHEN MATCHED THEN
    UPDATE SET
        tgt.severity = src.severity,
        tgt.detection_time = src.detection_time,
        tgt.modified_date = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN
    INSERT (detection_id, device_id, severity, detection_time, created_date)
    VALUES (src.detection_id, src.device_id, src.severity, src.detection_time, CURRENT_TIMESTAMP());
```

**Benefits**:
- Rerunnable without duplicates
- Handles late-arriving data
- Updates changed records

---

### 5. ✅ Error Handling & Retry Logic

**Exponential Backoff**:
```python
import time
from requests.exceptions import RequestException

def api_call_with_retry(url, headers, max_retries=3, backoff_factor=2):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=60)

            # Rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                time.sleep(retry_after)
                continue

            response.raise_for_status()
            return response.json()

        except RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait_time = backoff_factor ** attempt
            time.sleep(wait_time)
```

---

### 6. ✅ Authentication Best Practices

**Store Credentials in Snowflake Secrets**:
```sql
-- OAuth credentials
CREATE SECRET oauth_credentials
    TYPE = GENERIC_STRING
    SECRET_STRING = '{"client_id": "xxx", "client_secret": "yyy"}';

-- API key
CREATE SECRET api_key_secret
    TYPE = PASSWORD
    USERNAME = 'api_user'
    PASSWORD = 'api_key_value';

-- Grant usage
GRANT USAGE ON SECRET oauth_credentials TO ROLE DEV_DEVELOPER;
```

**Never Hardcode**:
```python
# ❌ BAD
API_KEY = "hardcoded_key_in_code"

# ✅ GOOD
def get_api_key():
    query = "SELECT SYSTEM$GET_SECRET('api_key_secret')"
    result = snowflake.execute(query)
    return result[0][0]
```

---

### 7. ✅ Monitoring & Alerting

**Data Quality Monitoring**:
```sql
CREATE VIEW DEV_REPORTING.VW_API_INTEGRATION_HEALTH AS
SELECT
    service_name,
    api_endpoint,
    MAX(execution_end) AS last_successful_run,
    DATEDIFF(minute, MAX(execution_end), CURRENT_TIMESTAMP()) AS minutes_since_last_run,
    SUM(CASE WHEN extraction_status = 'SUCCESS' THEN 1 ELSE 0 END) AS successful_runs,
    SUM(CASE WHEN extraction_status = 'FAILED' THEN 1 ELSE 0 END) AS failed_runs,
    ROUND(successful_runs / (successful_runs + failed_runs) * 100, 2) AS success_rate_pct,
    CASE
        WHEN minutes_since_last_run > 120 THEN '🔴 CRITICAL: No data in 2+ hours'
        WHEN minutes_since_last_run > 60 THEN '🟡 WARNING: No data in 1+ hour'
        ELSE '🟢 OK'
    END AS health_status
FROM DEV_TRANSFORMATION.METADATA.API_EXTRACTION_LOG
WHERE execution_start >= CURRENT_DATE - 7
GROUP BY service_name, api_endpoint;
```

---

### 8. ✅ Partition and Cluster Tables

**Landing Tables**:
```sql
-- Partition by ingestion date for performance
CREATE TABLE DEV_LANDING.CROWDSTRIKE.DETECTIONS_RAW (
    ingestion_id VARCHAR(32),
    raw_data VARIANT,
    ingestion_date DATE DEFAULT CURRENT_DATE()
)
CLUSTER BY (ingestion_date);  -- Micro-partitions by date
```

**Transformation Tables**:
```sql
-- Cluster by frequently filtered columns
CREATE TABLE DEV_TRANSFORMATION.CROWDSTRIKE.DETECTIONS (
    detection_id VARCHAR(50) PRIMARY KEY,
    device_id VARCHAR(50),
    detection_time TIMESTAMP_LTZ,
    severity VARCHAR(20)
)
CLUSTER BY (detection_time, severity);  -- Optimize queries by time and severity
```

---

### 9. ✅ Documentation Standards

**Document Each Integration**:
```markdown
## {Service} API Integration

### Overview
- **Service**: CrowdStrike Falcon
- **API Version**: v2
- **Authentication**: OAuth 2.0
- **Base URL**: https://api.crowdstrike.com
- **Rate Limit**: 5,000 requests/hour
- **Data Volume**: ~250K records

### Architecture
[Diagram here]

### Tables
- **Landing**: DEV_LANDING.CROWDSTRIKE.DETECTIONS_RAW
- **Transformation**: DEV_TRANSFORMATION.CROWDSTRIKE.DETECTIONS
- **Reporting**: DEV_REPORTING.VW_CROWDSTRIKE_DETECTIONS

### Endpoints
1. **/detects/queries/detects/v1** - Detection IDs
2. **/detects/entities/summaries/GET/v1** - Detection details

### Scheduling
- **Frequency**: Every 15 minutes
- **Method**: Snowflake Task
- **Window**: Last 20 minutes (incremental)

### Monitoring
- **Health Check**: VW_API_INTEGRATION_HEALTH
- **Alert Threshold**: 2 hours no data
```

---

### 10. ✅ Testing Strategy

**Unit Tests**:
```python
import pytest

def test_api_authentication():
    token = get_oauth_token()
    assert token is not None
    assert len(token) > 0

def test_api_extraction():
    data = extract_crowdstrike_detections(since='2025-01-01')
    assert isinstance(data, list)
    assert len(data) > 0
    assert 'detection_id' in data[0]

def test_incremental_extraction():
    timestamp = get_last_extraction_timestamp('CrowdStrike', '/detects')
    assert timestamp is not None
    assert isinstance(timestamp, datetime)
```

---

## 📊 Summary: Data Flow Decision Matrix

| Scenario | Destination | Why |
|----------|-------------|-----|
| **Initial API response** | DEV_LANDING | Raw preservation, audit trail |
| **JSON parsing** | DEV_LANDING | Store full VARIANT |
| **Business logic** | DEV_TRANSFORMATION | Star schema, quality checks |
| **Type casting** | DEV_TRANSFORMATION | Convert JSON strings to proper types |
| **Joins & enrichment** | DEV_TRANSFORMATION | Combine multiple sources |
| **Aggregations** | DEV_REPORTING | Pre-calculated KPIs |
| **Dashboard queries** | DEV_REPORTING | Optimized views |

---

## 🚫 Anti-Patterns to Avoid

### ❌ DON'T: Transform During Extraction
```python
# Bad: Business logic in extraction script
for record in api_response:
    record['severity_numeric'] = severity_map[record['severity']]  # ❌
    record['detection_date'] = parse_date(record['timestamp'])  # ❌
```

### ❌ DON'T: Skip Landing Layer
```python
# Bad: Direct to transformation
api_data = api.get_data()
insert_to_transformation_layer(api_data)  # ❌ No raw data preserved
```

### ❌ DON'T: Store Credentials in Code
```python
# Bad: Hardcoded secrets
API_KEY = "sk-1234567890abcdef"  # ❌ Security risk
```

### ❌ DON'T: Ignore Failures Silently
```python
# Bad: Silent failures
try:
    api.extract()
except Exception:
    pass  # ❌ No logging, no alerting
```

### ❌ DON'T: Load Full Snapshots Every Time
```python
# Bad: No incremental logic
data = api.get_all_records()  # ❌ Always pulls everything
```

---

## ✅ Recommended Pattern: Standard API Integration

```python
# 1. Extract (minimal transformation)
raw_data = api.get_data(since=last_extraction)

# 2. Load to Landing (preserve raw)
load_to_landing(raw_data, table='DEV_LANDING.SERVICE.TABLE_RAW')

# 3. Log extraction
log_extraction_success(service='ServiceName', records=len(raw_data))

# 4. Transformation happens separately (Snowflake Task)
# See SQL transformation scripts
```

---

**Best Practice**: Follow the **ELT pattern** (Extract-Load-Transform), not ETL
- **Extract**: Get raw data from API
- **Load**: Store in DEV_LANDING (no transformation)
- **Transform**: Apply business logic in DEV_TRANSFORMATION (SQL-based)

This aligns with your medallion architecture and Snowflake best practices.
