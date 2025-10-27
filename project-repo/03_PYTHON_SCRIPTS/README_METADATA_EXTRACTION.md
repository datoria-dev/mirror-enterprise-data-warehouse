# SECURITY_ANALYTICS Metadata and Sample Data Extraction

## Overview

This directory contains scripts for extracting metadata and sample data from Snowflake tables to facilitate Streamlit application development.

## Purpose

When building Streamlit dashboards, you need to understand:
- **Table structures**: Column names, data types, constraints
- **Data content**: Actual values to design filters and visualizations
- **Relationships**: How tables connect for joins

These scripts automate the extraction of this information.

## Available Scripts

### 1. `extract_metadata_and_samples.py` (Full-Featured)

**Best for**: Complete metadata extraction with detailed analysis

**Features**:
- Extracts comprehensive table metadata (columns, types, constraints)
- Exports sample data (first 100 rows per table)
- Generates JSON and Excel reports
- Creates organized CSV files by service
- Automatically categorizes tables by service

**Requirements**:
```bash
pip install snowflake-connector-python pandas openpyxl
```

**Usage**:
```bash
# 1. Update CONFIG dictionary with your credentials
# 2. Run the script
python extract_metadata_and_samples.py
```

**Output Structure**:
```
04_METADATA_SAMPLES/
├── metadata/
│   ├── SentinelOne_FACT_SENTINEL_ENDPOINTS_metadata.json
│   ├── Tenable_FACT_TENABLE_metadata.json
│   └── ...
├── samples/
│   ├── SentinelOne_FACT_SENTINEL_ENDPOINTS_sample.csv
│   ├── Tenable_FACT_TENABLE_sample.csv
│   └── ...
├── reports/
│   ├── metadata_summary_YYYYMMDD_HHMMSS.json
│   ├── metadata_summary_YYYYMMDD_HHMMSS.xlsx
│   └── ...
└── README.md
```

---

### 2. `extract_samples_snowpark.py` (Snowpark Version)

**Best for**: Simplified extraction using Snowpark

**Features**:
- Lighter weight using Snowpark Session
- Faster execution for large datasets
- Easier credential management
- Generates metadata JSON and sample CSVs

**Requirements**:
```bash
pip install snowflake-snowpark-python pandas openpyxl
```

**Usage**:
```bash
# 1. Update connection_parameters in the script
# 2. Run the script
python extract_samples_snowpark.py
```

**Output**: Same structure as full-featured script

---

### 3. `EXTRACT_METADATA_AND_SAMPLES.sql` (SQL-Only)

**Best for**: Running directly in Snowflake Worksheet without Python

**Features**:
- No Python installation required
- Creates views with metadata and samples
- Can be run in Snowflake UI
- Download results as CSV manually

**Usage**:
1. Open Snowflake Worksheet
2. Copy and paste the SQL script
3. Run each section sequentially
4. Download query results as CSV

**Created Views**:
```sql
-- Metadata views
DEV_TRANSFORMATION.SAMPLES.VW_ALL_TABLE_METADATA
DEV_TRANSFORMATION.SAMPLES.VW_SERVICE_SUMMARY
DEV_TRANSFORMATION.SAMPLES.VW_SERVICE_COLUMN_STATS
DEV_TRANSFORMATION.SAMPLES.VW_TABLE_PROFILE_REPORT

-- Sample data views (100 rows each)
DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINELONE_ENDPOINTS
DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_TENABLE_FACT
DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_CYBELANGEL_THREATS
-- ... and more
```

---

## Comparison Matrix

| Feature | Full Python | Snowpark Python | SQL-Only |
|---------|-------------|-----------------|----------|
| **No Python Required** | ❌ | ❌ | ✅ |
| **Automated CSV Export** | ✅ | ✅ | ❌ (manual) |
| **JSON Metadata** | ✅ | ✅ | ❌ |
| **Excel Reports** | ✅ | ✅ | ❌ |
| **Organized by Service** | ✅ | ✅ | ✅ |
| **Execution Speed** | Medium | Fast | Fastest |
| **Ease of Setup** | Medium | Easy | Easiest |

---

## How to Use Extracted Data for Streamlit Development

### Step 1: Review Table Metadata

**Example: SentinelOne_FACT_SENTINEL_ENDPOINTS_metadata.json**
```json
{
  "database": "DEV_TRANSFORMATION",
  "schema": "SECURITY_ANALYTICS",
  "table_name": "FACT_SENTINEL_ENDPOINTS",
  "columns": [
    {
      "name": "EVENT_TIMESTAMP",
      "data_type": "TIMESTAMP_NTZ",
      "nullable": false
    },
    {
      "name": "THREAT_SEVERITY",
      "data_type": "VARCHAR",
      "nullable": true
    },
    {
      "name": "ENDPOINT_NAME",
      "data_type": "VARCHAR",
      "nullable": false
    }
  ],
  "row_count": 125000
}
```

**Use this to**:
- Know exact column names for SQL queries
- Understand data types for proper filtering
- Identify nullable columns
- Estimate dataset size

---

### Step 2: Examine Sample Data

**Example: SentinelOne_FACT_SENTINEL_ENDPOINTS_sample.csv**
```csv
EVENT_TIMESTAMP,THREAT_SEVERITY,ENDPOINT_NAME,THREAT_TYPE
2025-10-20 14:30:00,Critical,LAPTOP-001,Malware
2025-10-20 14:35:00,High,SERVER-042,Ransomware
2025-10-20 14:40:00,Medium,DESKTOP-123,Suspicious
```

**Use this to**:
- Design appropriate filters (severity levels, threat types)
- Create sample visualizations
- Understand actual data formats
- Identify data quality issues

---

### Step 3: Build Streamlit Queries

**Before Extraction** (guessing):
```python
# You might guess column names
query = "SELECT severity, count(*) FROM table WHERE date > ..."
# ERROR: column "severity" doesn't exist
```

**After Extraction** (accurate):
```python
# You know the exact column names from metadata
query = f"""
    SELECT
        THREAT_SEVERITY,  -- Exact column name from metadata
        COUNT(*) as THREAT_COUNT
    FROM DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_SENTINEL_ENDPOINTS
    WHERE EVENT_TIMESTAMP >= DATEADD(day, -{days}, CURRENT_DATE())
      AND THREAT_SEVERITY IN ('Critical', 'High')  -- Values from sample data
    GROUP BY THREAT_SEVERITY
"""
```

---

### Step 4: Update Streamlit App

**Use metadata to populate filters**:
```python
# From sample data, you know the actual severity values
severity_filter = st.multiselect(
    "Threat Severity",
    ['Critical', 'High', 'Medium', 'Low'],  # Actual values from CSV
    default=['Critical', 'High']
)
```

**Use correct data types for columns**:
```python
# Metadata shows EVENT_TIMESTAMP is TIMESTAMP_NTZ
st.dataframe(
    details_data,
    column_config={
        "EVENT_TIMESTAMP": st.column_config.DatetimeColumn(
            "Event Time",
            format="YYYY-MM-DD HH:mm:ss"
        ),
        "THREAT_SEVERITY": st.column_config.TextColumn(
            "Severity",
            width="medium"
        )
    }
)
```

---

## Workflow Example

### Complete Development Workflow

```bash
# Step 1: Extract metadata and samples
python extract_samples_snowpark.py

# Step 2: Review outputs
cd 04_METADATA_SAMPLES
ls samples/  # Check sample CSVs
ls metadata/ # Check metadata JSONs

# Step 3: Open sample CSV in Excel/Pandas
# Examine actual data values, understand structure

# Step 4: Review metadata JSON
# Note column names, data types, row counts

# Step 5: Update Streamlit app
# Use template + metadata + samples to build queries

# Step 6: Test Streamlit app
streamlit run 07_STREAMLIT_APPS/SentinelOne/streamlit_app.py

# Step 7: Iterate
# If queries fail, check metadata for correct column names
# If filters don't match, check samples for actual values
```

---

## Tips and Best Practices

### 1. **Check Data Before Building**
Always review sample data before writing Streamlit queries. Don't guess column names or data formats.

### 2. **Understand Data Types**
- `TIMESTAMP_NTZ` → Use date range filters
- `VARCHAR` → Use text search and multiselect
- `NUMBER` → Use sliders and numeric comparisons
- `VARIANT` → Use JSON parsing functions

### 3. **Handle Empty Tables**
Some services may have 0 rows (like Leviat). The metadata will show this:
```json
{
  "row_count": 0,
  "columns": [...]
}
```

Build your Streamlit app to handle empty data gracefully:
```python
if not data.empty:
    st.dataframe(data)
else:
    st.warning("No data available for this service")
```

### 4. **Use Sample Data for Testing**
Before querying full tables, test with sample views:
```sql
-- Test query with 100-row sample
SELECT * FROM DEV_TRANSFORMATION.SAMPLES.VW_SAMPLE_SENTINELONE_ENDPOINTS
WHERE THREAT_SEVERITY = 'Critical'
```

### 5. **Document Assumptions**
If sample data shows certain patterns, document them:
```python
# Based on sample data extraction (2025-10-23):
# - THREAT_SEVERITY values: Critical, High, Medium, Low
# - EVENT_TIMESTAMP range: Last 90 days
# - Average row count: 125,000 rows
```

---

## Troubleshooting

### Issue: "Access Denied" Error
**Solution**: Ensure your role has SELECT privileges on all tables
```sql
USE ROLE SECURITY_ANALYTICS;
GRANT SELECT ON ALL TABLES IN SCHEMA DEV_LANDING.SECURITY_ANALYTICS TO ROLE SECURITY_ANALYTICS;
GRANT SELECT ON ALL TABLES IN SCHEMA DEV_TRANSFORMATION.SECURITY_ANALYTICS TO ROLE SECURITY_ANALYTICS;
```

### Issue: "Table Not Found" Error
**Solution**: Check if table exists in SERVICE_TABLES mapping. Update script if table names have changed.

### Issue: Sample Data is Empty
**Solution**: Table might have 0 rows. Check metadata JSON for `row_count`. This is normal for new services like Leviat.

### Issue: Python Dependencies Missing
**Solution**: Install required packages
```bash
pip install snowflake-connector-python snowflake-snowpark-python pandas openpyxl
```

---

## Next Steps After Extraction

1. **Review all CSVs** in `04_METADATA_SAMPLES/samples/`
2. **Check metadata JSONs** for column names and types
3. **Update Streamlit apps** with correct queries
4. **Test queries** in Snowflake Worksheet first
5. **Run Streamlit apps** and validate results
6. **Iterate** based on actual data patterns

---

## Additional Resources

- **Streamlit Documentation**: https://docs.streamlit.io/
- **Snowflake SQL Reference**: https://docs.snowflake.com/en/sql-reference
- **Pandas DataFrame Guide**: https://pandas.pydata.org/docs/
- **Project Template**: `07_STREAMLIT_APPS/templates/streamlit_app_template.py`

---

**Questions?** Contact GenericCorp Data Engineering Team

**Last Updated**: October 2025
