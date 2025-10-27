"""
API Integration Architecture Documentation Generator
====================================================
Purpose: Auto-generate architecture diagrams and documentation for each API integration
Output: Markdown files with Mermaid diagrams for Azure DevOps Wiki
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
import json


@dataclass
class APIIntegrationArchitecture:
    """Architecture metadata for an API integration."""
    service_name: str
    api_version: str
    auth_type: str
    base_url: str
    rate_limit_per_hour: int

    # Tables
    landing_tables: List[str]
    transformation_tables: List[str]
    reporting_views: List[str]

    # Endpoints
    endpoints: List[Dict[str, str]]

    # Metrics
    estimated_record_count: int
    refresh_frequency_minutes: int

    # Documentation
    official_docs_url: Optional[str] = None
    notes: Optional[str] = None


class ArchitectureDocumentationGenerator:
    """Generate standardized architecture documentation for API integrations."""

    @staticmethod
    def generate_mermaid_diagram(arch: APIIntegrationArchitecture) -> str:
        """
        Generate Mermaid architecture diagram.

        Args:
            arch: Architecture metadata

        Returns:
            Mermaid diagram as string
        """
        # Landing tables
        landing_nodes = "\n        ".join([
            f'{table}["📋 {table}"]' for table in arch.landing_tables
        ])

        # Transformation tables
        transformation_nodes = "\n        ".join([
            f'{table}["📊 {table}"]' for table in arch.transformation_tables
        ])

        # Reporting views
        reporting_nodes = "\n        ".join([
            f'{view}["👁️ {view}"]' for view in arch.reporting_views
        ])

        diagram = f"""
```mermaid
graph TB
    subgraph External[" 🌐 External Source"]
        API["{arch.service_name} API<br/>v{arch.api_version}<br/>{arch.auth_type}"]
    end

    subgraph Auth["🔐 Authentication"]
        AUTH_MODULE["Authentication Module<br/>{arch.auth_type}<br/>Rate Limit: {arch.rate_limit_per_hour}/hour"]
    end

    subgraph Extract["📥 Extraction Layer"]
        PYTHON["Python Connector<br/>api_connector_base.py<br/>+ {arch.service_name.lower()}_connector.py"]
    end

    subgraph Landing["🥉 Layer 1: DEV_LANDING (Raw)"]
        {landing_nodes}
    end

    subgraph Transform["🥈 Layer 2: DEV_TRANSFORMATION (Curated)"]
        TASK["Snowflake Tasks<br/>MERGE statements<br/>Every {arch.refresh_frequency_minutes} minutes"]
        {transformation_nodes}
    end

    subgraph Report["🥇 Layer 3: DEV_REPORTING (Analytics)"]
        {reporting_nodes}
    end

    subgraph Viz["📊 Visualization"]
        STREAMLIT["Streamlit Dashboards"]
        POWERBI["Power BI Reports"]
    end

    API -->|API Calls| AUTH_MODULE
    AUTH_MODULE -->|Access Token| PYTHON
    PYTHON -->|Load Raw JSON| Landing
    Landing -->|Scheduled Transform| TASK
    TASK -->|Business Logic| Transform
    Transform -->|Aggregate| Report
    Report -->|Connect| STREAMLIT
    Report -->|Connect| POWERBI

    style API fill:#FFE66D
    style AUTH_MODULE fill:#95E1D3
    style PYTHON fill:#A8E6CF
    style Landing fill:#FFAB91
    style TASK fill:#CE93D8
    style Transform fill:#81C784
    style Report fill:#64B5F6
    style STREAMLIT fill:#FF8A65
    style POWERBI fill:#BA68C8
```
"""
        return diagram

    @staticmethod
    def generate_full_documentation(arch: APIIntegrationArchitecture) -> str:
        """
        Generate complete documentation for an API integration.

        Args:
            arch: Architecture metadata

        Returns:
            Markdown documentation
        """
        # Generate Mermaid diagram
        diagram = ArchitectureDocumentationGenerator.generate_mermaid_diagram(arch)

        # Generate endpoint table
        endpoint_table = "| Endpoint | Method | Purpose | Record Type |\n"
        endpoint_table += "|----------|--------|---------|-------------|\n"
        for ep in arch.endpoints:
            endpoint_table += f"| `{ep['path']}` | {ep['method']} | {ep['purpose']} | {ep.get('record_type', 'N/A')} |\n"

        # Generate table inventory
        landing_table_list = "\n".join([f"- `DEV_LANDING.{arch.service_name}.{table}`" for table in arch.landing_tables])
        transformation_table_list = "\n".join([f"- `DEV_TRANSFORMATION.{arch.service_name}.{table}`" for table in arch.transformation_tables])
        reporting_view_list = "\n".join([f"- `DEV_REPORTING.{view}`" for view in arch.reporting_views])

        doc = f"""
## {arch.service_name} API Integration

### Overview

**Service**: {arch.service_name}
**API Version**: {arch.api_version}
**Authentication**: {arch.auth_type}
**Base URL**: `{arch.base_url}`
**Rate Limit**: {arch.rate_limit_per_hour} requests/hour
**Data Volume**: ~{arch.estimated_record_count:,} records
**Refresh Frequency**: Every {arch.refresh_frequency_minutes} minutes

---

### Architecture Diagram

{diagram}

---

### Data Flow

#### 1. **Extraction** (Python Script)
- Script: `{arch.service_name.lower()}_connector.py`
- Authentication: {arch.auth_type}
- Incremental loading: Uses `last_extraction_timestamp` from metadata
- Error handling: Exponential backoff with {3} retries

#### 2. **Landing Layer** (DEV_LANDING.{arch.service_name})
- **Pattern**: ELT (Extract-Load-Transform)
- **Storage Format**: Raw JSON in VARIANT column
- **Metadata**: `ingestion_id`, `ingestion_timestamp`, `source_file`, `ingestion_date`
- **Partitioning**: Clustered by `ingestion_date`

**Tables**:
{landing_table_list}

#### 3. **Transformation Layer** (DEV_TRANSFORMATION.{arch.service_name})
- **Pattern**: Star schema (dimensions + facts)
- **Orchestration**: Snowflake Tasks
- **Schedule**: Every {arch.refresh_frequency_minutes} minutes
- **Operation**: MERGE statements for upsert (idempotent)

**Tables**:
{transformation_table_list}

#### 4. **Reporting Layer** (DEV_REPORTING)
- **Pattern**: Denormalized views
- **Purpose**: Analytics-ready aggregations
- **Consumers**: Streamlit dashboards, Power BI reports

**Views**:
{reporting_view_list}

---

### API Endpoints

{endpoint_table}

---

### Authentication

#### {arch.auth_type} Flow

"""

        if arch.auth_type == 'OAuth 2.0':
            doc += """
1. **Request Access Token**:
   ```python
   response = requests.post(
       f"{base_url}/oauth2/token",
       data={
           'client_id': CLIENT_ID,
           'client_secret': CLIENT_SECRET
       }
   )
   access_token = response.json()['access_token']
   ```

2. **Use Access Token**:
   ```python
   headers = {'Authorization': f'Bearer {access_token}'}
   response = requests.get(endpoint, headers=headers)
   ```

3. **Token Expiration**: Tokens typically expire in 30 minutes. Refresh automatically.
"""
        elif arch.auth_type == 'API Key':
            doc += """
1. **Include API Key in Header**:
   ```python
   headers = {'X-API-Key': API_KEY}
   response = requests.get(endpoint, headers=headers)
   ```

2. **Alternative: Query Parameter**:
   ```python
   params = {'api_key': API_KEY}
   response = requests.get(endpoint, params=params)
   ```
"""

        doc += f"""
**Credential Storage**: Snowflake Secrets
```sql
CREATE SECRET {arch.service_name.lower()}_credentials
    TYPE = GENERIC_STRING
    SECRET_STRING = '{{"client_id": "xxx", "client_secret": "yyy"}}';
```

---

### Incremental Extraction

#### Last Extraction Tracking

```sql
-- Query last successful extraction
SELECT last_extraction_timestamp
FROM DEV_TRANSFORMATION.METADATA.API_EXTRACTION_LOG
WHERE service_name = '{arch.service_name}'
  AND extraction_status = 'SUCCESS'
ORDER BY extraction_id DESC
LIMIT 1;
```

#### Python Implementation

```python
# Get last extraction timestamp
last_timestamp = connector.get_last_extraction_timestamp('/api/endpoint')

# Extract only new/updated records
params = {{
    'since': last_timestamp.isoformat(),
    'limit': 1000
}}
data = connector.extract_data('/api/endpoint', params)

# Load to landing
connector.load_to_landing('{arch.landing_tables[0] if arch.landing_tables else "TABLE_NAME"}_RAW', data)
```

---

### Transformation Pipeline

#### Snowflake Task Configuration

```sql
-- Create transformation task
CREATE OR REPLACE TASK {arch.service_name.lower()}_transformation_task
    WAREHOUSE = DEV_WH
    SCHEDULE = '{arch.refresh_frequency_minutes} MINUTE'
AS
    MERGE INTO DEV_TRANSFORMATION.{arch.service_name}.{arch.transformation_tables[0] if arch.transformation_tables else "TABLE_NAME"} tgt
    USING (
        SELECT
            raw_data:id::VARCHAR AS record_id,
            raw_data:name::VARCHAR AS name,
            TRY_CAST(raw_data:timestamp::VARCHAR AS TIMESTAMP_LTZ) AS timestamp,
            -- Add more fields
        FROM DEV_LANDING.{arch.service_name}.{arch.landing_tables[0] if arch.landing_tables else "TABLE_NAME"}_RAW
        WHERE ingestion_timestamp >= DATEADD(minute, -{arch.refresh_frequency_minutes + 5}, CURRENT_TIMESTAMP())
    ) src
    ON tgt.record_id = src.record_id
    WHEN MATCHED THEN
        UPDATE SET
            tgt.name = src.name,
            tgt.timestamp = src.timestamp,
            tgt.modified_date = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN
        INSERT (record_id, name, timestamp, created_date, modified_date)
        VALUES (src.record_id, src.name, src.timestamp, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

-- Enable task
ALTER TASK {arch.service_name.lower()}_transformation_task RESUME;
```

---

### Monitoring

#### Health Check View

```sql
CREATE OR REPLACE VIEW DEV_REPORTING.VW_{arch.service_name.upper()}_INTEGRATION_HEALTH AS
SELECT
    '{arch.service_name}' AS service_name,
    MAX(execution_end) AS last_successful_run,
    DATEDIFF(minute, MAX(execution_end), CURRENT_TIMESTAMP()) AS minutes_since_last_run,
    SUM(records_extracted) AS total_records_last_24h,
    ROUND(AVG(CASE WHEN extraction_status = 'SUCCESS' THEN 100 ELSE 0 END), 2) AS success_rate_pct,
    CASE
        WHEN DATEDIFF(minute, MAX(execution_end), CURRENT_TIMESTAMP()) > {arch.refresh_frequency_minutes * 2}
        THEN '🔴 CRITICAL: No data in {arch.refresh_frequency_minutes * 2}+ minutes'
        WHEN DATEDIFF(minute, MAX(execution_end), CURRENT_TIMESTAMP()) > {arch.refresh_frequency_minutes}
        THEN '🟡 WARNING: No data in {arch.refresh_frequency_minutes}+ minutes'
        ELSE '🟢 OK'
    END AS health_status
FROM DEV_TRANSFORMATION.METADATA.API_EXTRACTION_LOG
WHERE service_name = '{arch.service_name}'
  AND execution_start >= CURRENT_DATE - 1;
```

---

### Usage Example

#### Python Script

```python
from {arch.service_name.lower()}_connector import {arch.service_name}Connector

# Configuration
config = {{
    'client_id': 'your_client_id',
    'client_secret': 'your_client_secret'
}}

snowflake_config = {{
    'user': 'your_user',
    'password': 'your_password',
    'account': 'your_account',
    'warehouse': 'DEV_WH'
}}

# Run extraction
with {arch.service_name}Connector(
    client_id=config['client_id'],
    client_secret=config['client_secret'],
    snowflake_config=snowflake_config
) as connector:
    metadata = connector.run_incremental_extraction('/api/endpoint')
    print(f"Status: {{metadata.extraction_status}}")
    print(f"Records: {{metadata.records_extracted}}")
```

---

### Troubleshooting

#### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Authentication Failure | Invalid credentials | Verify API key/client credentials in Snowflake Secrets |
| Rate Limiting (429) | Too many requests | Script has automatic retry with backoff |
| Timeout Errors | Slow API response | Increase `timeout_seconds` in config |
| No Data Extracted | Incorrect filter | Check `since` timestamp and API filter syntax |
| Duplicate Records | Missing idempotency | Ensure MERGE statement uses unique key |

#### Debug Queries

```sql
-- Check last 10 extractions
SELECT *
FROM DEV_TRANSFORMATION.METADATA.API_EXTRACTION_LOG
WHERE service_name = '{arch.service_name}'
ORDER BY extraction_id DESC
LIMIT 10;

-- Check landing data freshness
SELECT
    COUNT(*) AS total_records,
    MAX(ingestion_timestamp) AS last_ingestion,
    DATEDIFF(minute, MAX(ingestion_timestamp), CURRENT_TIMESTAMP()) AS minutes_ago
FROM DEV_LANDING.{arch.service_name}.{arch.landing_tables[0] if arch.landing_tables else "TABLE_NAME"}_RAW;

-- Check transformation data
SELECT
    COUNT(*) AS total_records,
    MIN(created_date) AS oldest_record,
    MAX(modified_date) AS last_update
FROM DEV_TRANSFORMATION.{arch.service_name}.{arch.transformation_tables[0] if arch.transformation_tables else "TABLE_NAME"};
```

---

### Related Documentation

- [[SECURITY_ANALYTICS-Documentation/05-Data-Dictionary]] - Complete column definitions
- [[SECURITY_ANALYTICS-Documentation/06-Best-Practices]] - Development standards
- [[Data-Architecture]] - 3-layer architecture overview
- [[Data-Model]] - Star schema design
"""

        if arch.official_docs_url:
            doc += f"- **Official API Documentation**: {arch.official_docs_url}\n"

        if arch.notes:
            doc += f"\n---\n\n### Additional Notes\n\n{arch.notes}\n"

        doc += f"""
---

**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
**Status**: Production
**Maintained By**: GenericCorp Data Engineering Team - SECURITY_ANALYTICS Project
"""

        return doc


# Example usage: Generate documentation for CrowdStrike
if __name__ == "__main__":
    crowdstrike_arch = APIIntegrationArchitecture(
        service_name="CrowdStrike",
        api_version="v1",
        auth_type="OAuth 2.0",
        base_url="https://api.crowdstrike.com",
        rate_limit_per_hour=5000,
        landing_tables=[
            "DETECTIONS_RAW",
            "DEVICES_RAW",
            "INCIDENTS_RAW"
        ],
        transformation_tables=[
            "DETECTIONS",
            "DEVICES",
            "INCIDENTS"
        ],
        reporting_views=[
            "VW_CROWDSTRIKE_DETECTIONS_SUMMARY",
            "VW_CROWDSTRIKE_DEVICE_INVENTORY",
            "VW_CROWDSTRIKE_INCIDENT_TRENDS"
        ],
        endpoints=[
            {
                "path": "/detects/queries/detects/v1",
                "method": "GET",
                "purpose": "Query detection IDs",
                "record_type": "Detection IDs"
            },
            {
                "path": "/detects/entities/summaries/GET/v1",
                "method": "POST",
                "purpose": "Get detection details",
                "record_type": "Detection Details"
            },
            {
                "path": "/devices/queries/devices/v1",
                "method": "GET",
                "purpose": "Query device IDs",
                "record_type": "Device IDs"
            },
            {
                "path": "/devices/entities/devices/v1",
                "method": "GET",
                "purpose": "Get device details",
                "record_type": "Device Details"
            }
        ],
        estimated_record_count=250000,
        refresh_frequency_minutes=15,
        official_docs_url="https://falcon.crowdstrike.com/documentation/",
        notes="CrowdStrike uses a two-step process: first query for IDs, then retrieve details in batches of 100."
    )

    # Generate documentation
    generator = ArchitectureDocumentationGenerator()
    documentation = generator.generate_full_documentation(crowdstrike_arch)

    # Save to file
    with open("CROWDSTRIKE_ARCHITECTURE.md", "w", encoding="utf-8") as f:
        f.write(documentation)

    print("✅ Documentation generated: CROWDSTRIKE_ARCHITECTURE.md")
