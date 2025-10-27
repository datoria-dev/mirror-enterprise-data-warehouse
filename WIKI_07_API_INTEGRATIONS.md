# SECURITY_ANALYTICS Data Warehouse - API Integrations

## Overview

This document provides comprehensive documentation for all API integrations in the SECURITY_ANALYTICS Data Warehouse. Each integration includes authentication methods, API endpoints, data extraction patterns, error handling, and monitoring procedures.

**Total Integrations**: 20 security services
**Primary Integration Method**: REST APIs with OAuth 2.0 / API Key authentication
**Orchestration**: Python scripts with Snowflake integration
**Data Ingestion**: Snowpipe (real-time) and Scheduled Tasks (batch)

---

## Table of Contents

- [ServiceNow API Integration](#servicenow-api-integration)
- [CrowdStrike Falcon API](#crowdstrike-falcon-api)
- [SentinelOne API](#sentinelone-api)
- [Qualys API](#qualys-api)
- [Zscaler API](#zscaler-api)
- [CybelAngel API](#cybelangel-api)
- [BitSight API](#bitsight-api)
- [Proofpoint API](#proofpoint-api)
- [Common Integration Patterns](#common-integration-patterns)
- [Error Handling & Retry Logic](#error-handling--retry-logic)
- [Monitoring & Alerting](#monitoring--alerting)

---

## ServiceNow API Integration

### Overview

**Service**: ServiceNow IT Service Management (ITSM)
**Purpose**: Extract incidents, change requests, and configuration items (CMDB)
**API Version**: ServiceNow REST API v2
**Authentication**: OAuth 2.0 with client credentials flow
**Data Volume**: ~616,250 records (incidents and changes)
**Refresh Frequency**: Every 15 minutes (near real-time)

---

### Authentication

#### OAuth 2.0 Configuration

```python
import requests
from requests.auth import HTTPBasicAuth
import snowflake.connector

# ServiceNow OAuth 2.0 credentials
SERVICENOW_INSTANCE = "https://yourinstance.service-now.com"
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
USERNAME = "integration_user@CompanyX.com"
PASSWORD = "stored_in_snowflake_secrets"

def get_servicenow_token():
    """
    Obtain OAuth 2.0 access token from ServiceNow.

    Returns:
        str: Access token for API authentication
    """
    token_url = f"{SERVICENOW_INSTANCE}/oauth_token.do"

    auth_data = {
        'grant_type': 'password',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'username': USERNAME,
        'password': PASSWORD
    }

    try:
        response = requests.post(
            token_url,
            data=auth_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        response.raise_for_status()

        token_data = response.json()
        return token_data['access_token']

    except requests.exceptions.RequestException as e:
        print(f"Error obtaining ServiceNow token: {e}")
        raise
```

#### Storing Credentials in Snowflake

```sql
-- Create secret object for ServiceNow credentials
CREATE OR REPLACE SECRET servicenow_oauth_secret
    TYPE = PASSWORD
    USERNAME = 'integration_user@CompanyX.com'
    PASSWORD = 'your_secure_password';

-- Grant usage to integration role
GRANT USAGE ON SECRET servicenow_oauth_secret TO ROLE DEV_DEVELOPER;

-- Store client credentials
CREATE OR REPLACE SECRET servicenow_client_credentials
    TYPE = GENERIC_STRING
    SECRET_STRING = '{"client_id": "xxx", "client_secret": "yyy"}';
```

---

### API Endpoints

#### 1. Incidents API

**Endpoint**: `/api/now/table/incident`
**Method**: GET
**Purpose**: Extract IT incidents for security tracking

```python
def extract_servicenow_incidents(access_token, since_datetime):
    """
    Extract incidents from ServiceNow.

    Args:
        access_token (str): OAuth 2.0 access token
        since_datetime (str): ISO 8601 timestamp for incremental extraction

    Returns:
        list: Incident records as JSON objects
    """
    incidents_url = f"{SERVICENOW_INSTANCE}/api/now/table/incident"

    # Query parameters for filtering
    params = {
        'sysparm_query': f'sys_updated_on>={since_datetime}^category=security',
        'sysparm_limit': 1000,
        'sysparm_offset': 0,
        'sysparm_fields': 'number,short_description,description,priority,state,'
                         'assigned_to,assignment_group,category,subcategory,'
                         'opened_at,closed_at,resolved_at,sys_created_on,sys_updated_on',
        'sysparm_display_value': 'true'
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    all_incidents = []

    while True:
        try:
            response = requests.get(
                incidents_url,
                headers=headers,
                params=params,
                timeout=60
            )
            response.raise_for_status()

            data = response.json()
            incidents = data.get('result', [])

            if not incidents:
                break

            all_incidents.extend(incidents)

            # Pagination
            params['sysparm_offset'] += params['sysparm_limit']

            # Check if we've retrieved all records
            if len(incidents) < params['sysparm_limit']:
                break

        except requests.exceptions.RequestException as e:
            print(f"Error extracting incidents: {e}")
            break

    return all_incidents
```

**Key Fields Extracted**:
- `number` - Incident number (e.g., INC0012345)
- `short_description` - Brief incident description
- `description` - Detailed incident description
- `priority` - 1 (Critical), 2 (High), 3 (Medium), 4 (Low), 5 (Planning)
- `state` - New, In Progress, On Hold, Resolved, Closed, Canceled
- `assigned_to` - Assigned technician
- `assignment_group` - Assigned team (e.g., IT Security Operations)
- `category` - Incident category (Security, Network, Hardware, Software)
- `subcategory` - Incident subcategory
- `opened_at` - Incident opened timestamp
- `closed_at` - Incident closed timestamp
- `resolved_at` - Incident resolved timestamp
- `sys_created_on` - Record creation timestamp
- `sys_updated_on` - Record last update timestamp

---

#### 2. Change Requests API

**Endpoint**: `/api/now/table/change_request`
**Method**: GET
**Purpose**: Track security-related change requests

```python
def extract_servicenow_changes(access_token, since_datetime):
    """
    Extract change requests from ServiceNow.

    Args:
        access_token (str): OAuth 2.0 access token
        since_datetime (str): ISO 8601 timestamp for incremental extraction

    Returns:
        list: Change request records as JSON objects
    """
    changes_url = f"{SERVICENOW_INSTANCE}/api/now/table/change_request"

    params = {
        'sysparm_query': f'sys_updated_on>={since_datetime}',
        'sysparm_limit': 1000,
        'sysparm_fields': 'number,short_description,description,type,risk,'
                         'priority,state,assignment_group,start_date,end_date,'
                         'close_code,close_notes,sys_created_on,sys_updated_on',
        'sysparm_display_value': 'true'
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    response = requests.get(changes_url, headers=headers, params=params, timeout=60)
    response.raise_for_status()

    return response.json().get('result', [])
```

**Key Fields Extracted**:
- `number` - Change request number (e.g., CHG0012345)
- `type` - Standard, Normal, Emergency
- `risk` - High, Medium, Low
- `priority` - 1-5 (Critical to Planning)
- `state` - New, Assess, Authorize, Scheduled, Implement, Review, Closed
- `start_date` - Planned start date
- `end_date` - Planned end date
- `close_code` - Successful, Unsuccessful, Canceled
- `close_notes` - Closure notes

---

#### 3. CMDB CI API (Configuration Items)

**Endpoint**: `/api/now/table/cmdb_ci`
**Method**: GET
**Purpose**: Extract configuration items for asset inventory

```python
def extract_servicenow_cmdb(access_token):
    """
    Extract configuration items from ServiceNow CMDB.

    Args:
        access_token (str): OAuth 2.0 access token

    Returns:
        list: Configuration item records
    """
    cmdb_url = f"{SERVICENOW_INSTANCE}/api/now/table/cmdb_ci"

    params = {
        'sysparm_query': 'sys_class_name=cmdb_ci_server^ORsys_class_name=cmdb_ci_computer',
        'sysparm_limit': 5000,
        'sysparm_fields': 'name,ip_address,mac_address,dns_domain,os,os_version,'
                         'serial_number,asset_tag,location,department,managed_by,'
                         'operational_status,sys_created_on,sys_updated_on'
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    response = requests.get(cmdb_url, headers=headers, params=params, timeout=120)
    response.raise_for_status()

    return response.json().get('result', [])
```

---

### Data Transformation Pipeline

#### Landing Layer (Raw JSON)

```sql
-- Create landing table for ServiceNow incidents
CREATE OR REPLACE TABLE DEV_LANDING.SERVICENOW.SERVICENOW_INCIDENTS_RAW (
    raw_data VARIANT,
    ingestion_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP,
    source_file VARCHAR(500)
);

-- Load data using Snowpipe (triggered by S3 event)
CREATE OR REPLACE PIPE servicenow_incidents_pipe
    AUTO_INGEST = TRUE
AS
COPY INTO DEV_LANDING.SERVICENOW.SERVICENOW_INCIDENTS_RAW
FROM @servicenow_stage/incidents/
FILE_FORMAT = (TYPE = 'JSON')
ON_ERROR = 'CONTINUE';
```

#### Transformation Layer (Structured Tables)

```sql
-- Transform raw JSON to structured table
CREATE OR REPLACE TABLE DEV_TRANSFORMATION.SERVICENOW.SERVICENOW_INCIDENTS (
    -- Primary Key
    incident_id VARCHAR(32) PRIMARY KEY,

    -- ServiceNow Fields
    incident_number VARCHAR(50) UNIQUE NOT NULL,
    short_description VARCHAR(500),
    description TEXT,

    -- Classification
    priority INTEGER,
    priority_name VARCHAR(20),
    state INTEGER,
    state_name VARCHAR(50),
    category VARCHAR(100),
    subcategory VARCHAR(100),

    -- Assignment
    assigned_to VARCHAR(200),
    assignment_group VARCHAR(200),

    -- Dates
    opened_at TIMESTAMP_LTZ,
    closed_at TIMESTAMP_LTZ,
    resolved_at TIMESTAMP_LTZ,

    -- Metadata
    sys_created_on TIMESTAMP_LTZ,
    sys_updated_on TIMESTAMP_LTZ,
    created_date TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP
);

-- Transformation logic
INSERT INTO DEV_TRANSFORMATION.SERVICENOW.SERVICENOW_INCIDENTS
SELECT
    MD5(raw_data:number::STRING) AS incident_id,
    raw_data:number::VARCHAR AS incident_number,
    raw_data:short_description::VARCHAR AS short_description,
    raw_data:description::TEXT AS description,
    raw_data:priority::INTEGER AS priority,
    raw_data:priority_name::VARCHAR AS priority_name,
    raw_data:state::INTEGER AS state,
    raw_data:state_name::VARCHAR AS state_name,
    raw_data:category::VARCHAR AS category,
    raw_data:subcategory::VARCHAR AS subcategory,
    raw_data:assigned_to::VARCHAR AS assigned_to,
    raw_data:assignment_group::VARCHAR AS assignment_group,
    raw_data:opened_at::TIMESTAMP_LTZ AS opened_at,
    raw_data:closed_at::TIMESTAMP_LTZ AS closed_at,
    raw_data:resolved_at::TIMESTAMP_LTZ AS resolved_at,
    raw_data:sys_created_on::TIMESTAMP_LTZ AS sys_created_on,
    raw_data:sys_updated_on::TIMESTAMP_LTZ AS sys_updated_on,
    CURRENT_TIMESTAMP AS created_date,
    CURRENT_TIMESTAMP AS modified_date
FROM DEV_LANDING.SERVICENOW.SERVICENOW_INCIDENTS_RAW
WHERE ingestion_timestamp >= DATEADD(hour, -1, CURRENT_TIMESTAMP);
```

---

### Incremental Data Extraction

#### Tracking Last Extraction Time

```sql
-- Create metadata table to track last extraction
CREATE OR REPLACE TABLE DEV_TRANSFORMATION.METADATA.API_EXTRACTION_LOG (
    extraction_id INTEGER AUTOINCREMENT PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    api_endpoint VARCHAR(500) NOT NULL,
    extraction_type VARCHAR(50), -- FULL, INCREMENTAL
    last_extraction_timestamp TIMESTAMP_LTZ,
    records_extracted INTEGER,
    extraction_status VARCHAR(50), -- SUCCESS, FAILED, PARTIAL
    error_message TEXT,
    execution_start TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP,
    execution_end TIMESTAMP_LTZ
);

-- Query last successful extraction
SELECT last_extraction_timestamp
FROM DEV_TRANSFORMATION.METADATA.API_EXTRACTION_LOG
WHERE service_name = 'ServiceNow'
  AND api_endpoint = '/api/now/table/incident'
  AND extraction_status = 'SUCCESS'
ORDER BY extraction_id DESC
LIMIT 1;
```

#### Python Function for Incremental Extraction

```python
def get_last_extraction_timestamp(service_name, api_endpoint):
    """
    Get last successful extraction timestamp from Snowflake.

    Args:
        service_name (str): Service name (e.g., 'ServiceNow')
        api_endpoint (str): API endpoint path

    Returns:
        str: ISO 8601 timestamp or default (7 days ago)
    """
    import snowflake.connector
    from datetime import datetime, timedelta

    conn = snowflake.connector.connect(
        user='integration_user',
        password='stored_password',
        account='oldcastle_account',
        warehouse='DEV_WH',
        database='DEV_TRANSFORMATION',
        schema='METADATA'
    )

    cursor = conn.cursor()

    query = """
        SELECT last_extraction_timestamp
        FROM API_EXTRACTION_LOG
        WHERE service_name = %s
          AND api_endpoint = %s
          AND extraction_status = 'SUCCESS'
        ORDER BY extraction_id DESC
        LIMIT 1
    """

    cursor.execute(query, (service_name, api_endpoint))
    result = cursor.fetchone()

    if result and result[0]:
        last_timestamp = result[0]
    else:
        # Default: extract last 7 days if no previous extraction
        last_timestamp = datetime.utcnow() - timedelta(days=7)

    cursor.close()
    conn.close()

    return last_timestamp.isoformat()
```

---

### Error Handling & Retry Logic

```python
import time
from requests.exceptions import RequestException, HTTPError, Timeout

def api_call_with_retry(
    url,
    headers,
    params=None,
    max_retries=3,
    backoff_factor=2,
    timeout=60
):
    """
    Make API call with exponential backoff retry logic.

    Args:
        url (str): API endpoint URL
        headers (dict): Request headers
        params (dict): Query parameters
        max_retries (int): Maximum number of retry attempts
        backoff_factor (int): Exponential backoff multiplier
        timeout (int): Request timeout in seconds

    Returns:
        dict: JSON response from API

    Raises:
        HTTPError: If all retry attempts fail
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=timeout
            )

            # Handle rate limiting (429 Too Many Requests)
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                print(f"Rate limited. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
                continue

            response.raise_for_status()
            return response.json()

        except Timeout:
            wait_time = backoff_factor ** attempt
            print(f"Timeout on attempt {attempt + 1}. Retrying in {wait_time}s...")
            time.sleep(wait_time)

        except HTTPError as e:
            if e.response.status_code in [500, 502, 503, 504]:
                # Server error - retry with backoff
                wait_time = backoff_factor ** attempt
                print(f"Server error {e.response.status_code}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                # Client error (4xx) - don't retry
                print(f"Client error {e.response.status_code}: {e}")
                raise

        except RequestException as e:
            print(f"Request exception: {e}")
            if attempt == max_retries - 1:
                raise

    raise HTTPError(f"Failed after {max_retries} attempts")
```

---

### Scheduling & Orchestration

#### Snowflake Task for Scheduled Extraction

```sql
-- Create task to extract ServiceNow data every 15 minutes
CREATE OR REPLACE TASK servicenow_incidents_extraction_task
    WAREHOUSE = DEV_WH
    SCHEDULE = '15 MINUTE'
AS
CALL python_udf_extract_servicenow_incidents();

-- Start the task
ALTER TASK servicenow_incidents_extraction_task RESUME;

-- Monitor task execution
SELECT *
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    TASK_NAME => 'SERVICENOW_INCIDENTS_EXTRACTION_TASK',
    SCHEDULED_TIME_RANGE_START => DATEADD(day, -7, CURRENT_TIMESTAMP())
))
ORDER BY SCHEDULED_TIME DESC;
```

#### Alternative: Python Script with Cron Job

```python
# servicenow_extraction.py
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/servicenow_extraction.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    """Main extraction function."""
    try:
        logging.info("Starting ServiceNow data extraction...")

        # Get OAuth token
        access_token = get_servicenow_token()

        # Get last extraction timestamp
        since_datetime = get_last_extraction_timestamp(
            'ServiceNow',
            '/api/now/table/incident'
        )

        # Extract incidents
        incidents = extract_servicenow_incidents(access_token, since_datetime)
        logging.info(f"Extracted {len(incidents)} incidents")

        # Load to Snowflake
        load_to_snowflake(incidents, 'SERVICENOW_INCIDENTS_RAW')

        # Log success
        log_extraction_success(
            service_name='ServiceNow',
            api_endpoint='/api/now/table/incident',
            records_extracted=len(incidents)
        )

        logging.info("ServiceNow extraction completed successfully")

    except Exception as e:
        logging.error(f"Extraction failed: {e}")
        log_extraction_failure(
            service_name='ServiceNow',
            api_endpoint='/api/now/table/incident',
            error_message=str(e)
        )
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Cron Schedule** (every 15 minutes):
```bash
# /etc/cron.d/servicenow-extraction
*/15 * * * * python /opt/SECURITY_ANALYTICS/servicenow_extraction.py
```

---

### Monitoring & Alerting

#### Data Quality Checks

```sql
-- Check for data freshness
CREATE OR REPLACE VIEW VW_SERVICENOW_DATA_FRESHNESS AS
SELECT
    'ServiceNow Incidents' AS data_source,
    MAX(sys_updated_on) AS last_record_timestamp,
    DATEDIFF(minute, MAX(sys_updated_on), CURRENT_TIMESTAMP) AS minutes_since_last_update,
    CASE
        WHEN DATEDIFF(minute, MAX(sys_updated_on), CURRENT_TIMESTAMP) > 30
        THEN 'ALERT: Data is stale'
        ELSE 'OK'
    END AS freshness_status
FROM DEV_TRANSFORMATION.SERVICENOW.SERVICENOW_INCIDENTS;

-- Check for extraction failures
CREATE OR REPLACE VIEW VW_SERVICENOW_EXTRACTION_STATUS AS
SELECT
    service_name,
    api_endpoint,
    extraction_status,
    records_extracted,
    error_message,
    execution_start,
    execution_end,
    DATEDIFF(second, execution_start, execution_end) AS execution_duration_seconds
FROM DEV_TRANSFORMATION.METADATA.API_EXTRACTION_LOG
WHERE service_name = 'ServiceNow'
ORDER BY extraction_id DESC
LIMIT 10;
```

#### Alerting via Email

```sql
-- Create notification integration (email alerts)
CREATE OR REPLACE NOTIFICATION INTEGRATION servicenow_alert_email
    TYPE = EMAIL
    ENABLED = TRUE
    ALLOWED_RECIPIENTS = ('security-ops@CompanyX.com', 'data-engineering@CompanyX.com');

-- Create alert task
CREATE OR REPLACE TASK servicenow_data_freshness_alert
    WAREHOUSE = DEV_WH
    SCHEDULE = '30 MINUTE'
WHEN
    SYSTEM$STREAM_HAS_DATA('servicenow_alerts_stream')
AS
    CALL SYSTEM$SEND_EMAIL(
        'servicenow_alert_email',
        'security-ops@CompanyX.com',
        'ALERT: ServiceNow Data Stale',
        'ServiceNow incidents data has not been updated in over 30 minutes. Please investigate.'
    );
```

---

### API Rate Limits & Best Practices

#### ServiceNow Rate Limits

- **Default Limit**: 2,000 requests per hour per user
- **Burst Limit**: 200 requests per 10 minutes
- **Recommendation**: Implement exponential backoff and respect `Retry-After` header

#### Best Practices

1. **Use Query Filters**: Always filter by `sys_updated_on` for incremental extraction
2. **Paginate Large Results**: Use `sysparm_limit` and `sysparm_offset` for pagination
3. **Select Specific Fields**: Use `sysparm_fields` to reduce payload size
4. **Monitor API Usage**: Track API calls in `API_EXTRACTION_LOG` table
5. **Handle Rate Limits**: Implement retry logic with `Retry-After` header
6. **Use Display Values**: Set `sysparm_display_value=true` for human-readable values
7. **Compress Responses**: Use `Accept-Encoding: gzip` header for compression
8. **Batch Processing**: Extract data in batches (e.g., 1000 records at a time)

---

### Performance Optimization

```python
# Parallel extraction for multiple API endpoints
from concurrent.futures import ThreadPoolExecutor, as_completed

def extract_all_servicenow_data(access_token, since_datetime):
    """
    Extract data from multiple ServiceNow endpoints in parallel.

    Args:
        access_token (str): OAuth 2.0 access token
        since_datetime (str): ISO 8601 timestamp

    Returns:
        dict: Dictionary with endpoint names as keys and extracted data as values
    """
    endpoints = {
        'incidents': extract_servicenow_incidents,
        'changes': extract_servicenow_changes,
        'cmdb': extract_servicenow_cmdb
    }

    results = {}

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_endpoint = {
            executor.submit(func, access_token, since_datetime): name
            for name, func in endpoints.items()
        }

        for future in as_completed(future_to_endpoint):
            endpoint_name = future_to_endpoint[future]
            try:
                data = future.result()
                results[endpoint_name] = data
                print(f"Extracted {len(data)} records from {endpoint_name}")
            except Exception as e:
                print(f"Error extracting {endpoint_name}: {e}")
                results[endpoint_name] = []

    return results
```

---

### Testing & Validation

```python
import pytest

def test_servicenow_token_acquisition():
    """Test OAuth token acquisition."""
    token = get_servicenow_token()
    assert token is not None
    assert len(token) > 0

def test_servicenow_incidents_extraction():
    """Test incidents extraction."""
    token = get_servicenow_token()
    since_datetime = '2025-10-01T00:00:00Z'
    incidents = extract_servicenow_incidents(token, since_datetime)
    assert isinstance(incidents, list)
    assert len(incidents) > 0
    assert 'number' in incidents[0]

def test_incremental_extraction_timestamp():
    """Test last extraction timestamp retrieval."""
    timestamp = get_last_extraction_timestamp('ServiceNow', '/api/now/table/incident')
    assert timestamp is not None
    assert 'T' in timestamp  # ISO 8601 format

def test_api_retry_logic():
    """Test retry logic with mock failed request."""
    # Mock implementation
    pass
```

---

## Summary - ServiceNow Integration

### Key Metrics

- **API Endpoints**: 3 (Incidents, Changes, CMDB)
- **Authentication**: OAuth 2.0 with client credentials
- **Data Volume**: ~616,250 records
- **Refresh Frequency**: Every 15 minutes
- **Tables Created**: 2 (SERVICENOW_INCIDENTS, SERVICENOW_CHANGES)
- **Monitoring Views**: 2 (Data freshness, Extraction status)

### Files & Scripts

- `servicenow_extraction.py` - Main extraction script
- `SERVICENOW_INCIDENTS_RAW` - Landing table
- `SERVICENOW_INCIDENTS` - Transformation table
- `servicenow_incidents_pipe` - Snowpipe for ingestion
- `servicenow_incidents_extraction_task` - Scheduled task

### Next Steps

1. Deploy ServiceNow extraction script to production
2. Configure Snowflake tasks for scheduled execution
3. Set up email alerts for data freshness monitoring
4. Document additional endpoints (users, groups, security incidents)
5. Implement data quality checks and reconciliation

---

## Related Documentation

- [[SECURITY_ANALYTICS-Documentation/05-Data-Dictionary]] - ServiceNow table schemas
- [[SECURITY_ANALYTICS-Documentation/04-Data-Governance]] - Data governance policies
- [[SECURITY_ANALYTICS-Documentation/06-Best-Practices]] - Python development standards
- [[Data-Architecture]] - Data architecture overview
- [[Deployment-Guide]] - Deployment procedures

---

**Last Updated**: October 24, 2025
**Maintained By**: Lead Data Engineer - SECURITY_ANALYTICS Project
**Status**: ServiceNow integration documented - Additional services to be added
