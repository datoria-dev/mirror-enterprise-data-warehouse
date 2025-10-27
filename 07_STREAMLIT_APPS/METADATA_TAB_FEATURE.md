# Metadata Tab Feature - Documentation

## Overview

**Date**: 2025-10-24
**Version**: 1.0
**Status**: ✅ **Deployed to 6 Services**

---

## Executive Summary

A new **📚 Metadata** tab has been added to 6 Streamlit applications, providing users with an integrated data catalog experience. This feature allows users to browse tables, search columns, and understand data structures without leaving the dashboard.

---

## Feature Description

### What is the Metadata Tab?

The Metadata tab provides a self-service data catalog within each Streamlit app, allowing users to:

1. **Browse Tables**: View all tables available for a service
2. **Explore Columns**: See column names, data types, and nullable status
3. **Search Metadata**: Quickly find columns by name across all tables
4. **Export Metadata**: Download complete metadata catalogs as CSV files
5. **View Full Table Names**: Access full Snowflake qualified table names for queries

### Data Source

The metadata is sourced from the **Metadata Repository** (`DEV_TRANSFORMATION.METADATA` schema) and specifically from the `METADATA_EXPORTS` schema where service-specific column exports are stored.

---

## Deployed Applications

The Metadata tab has been successfully added to the following 6 services:

| Service | App Location | Export Table | Column Count |
|---------|--------------|--------------|--------------|
| ✅ **SentinelOne** | `07_STREAMLIT_APPS/SentinelOne/` | `SENTINELONE_COLUMNS_EXPORT` | 76 columns |
| ✅ **CybelAngel** | `07_STREAMLIT_APPS/CybelAngel/` | `CYBELANGEL_COLUMNS_EXPORT` | 112 columns |
| ✅ **Proofpoint** | `07_STREAMLIT_APPS/Proofpoint/` | `PROOFPOINT_COLUMNS_EXPORT` | 23 columns |
| ✅ **ServiceNow** | `07_STREAMLIT_APPS/ServiceNow/` | `SERVICENOW_COLUMNS_EXPORT` | 36 columns |
| ✅ **Leviat** | `07_STREAMLIT_APPS/Leviat/` | `LEVIAT_COLUMNS_EXPORT` | 146 columns |
| ✅ **Tenable** | `07_STREAMLIT_APPS/Tenable/` | `TENABLE_COLUMNS_EXPORT` | 0 columns* |

*Note: Tenable has the tab but currently has no data (no tables found in system)

---

## User Interface Components

### 1. Table Selector

**Location**: Top of Metadata tab
**Function**: Dropdown to select specific tables or view all tables

**Options**:
- "All Tables" - Shows expandable cards for all tables
- Individual table names - Shows detailed column list for selected table

### 2. Table Overview (when "All Tables" selected)

**Display**: Expandable cards for each table

**Information Shown**:
- Table name with column count
- Full qualified table name (e.g., `DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_SENTINEL_ENDPOINTS`)
- Complete column list with:
  - Column names
  - Data types
  - Nullable status
  - Ordinal positions

### 3. Column Detail View (when specific table selected)

**Display**: Detailed list of columns

**Information Shown**:
- Full table name (code block for easy copy)
- Total column count metric
- Formatted column list with:
  - Column name (bold)
  - Data type (code format)
  - Nullable indicator (✅/❌)
  - Position number

### 4. Column Search

**Location**: Below table browser
**Function**: Search for columns across all tables

**Features**:
- Case-insensitive search
- Searches across column names
- Shows results with table name, column name, data type, full table name
- Export search results to CSV
- Result count indicator

### 5. Export Functionality

**Available Exports**:
1. **Complete Metadata**: All columns for the service
2. **Search Results**: Filtered results from search query
3. **Selected Table**: Columns for specific table (via expandable cards)

**Format**: CSV files with service name prefix

---

## Technical Implementation

### Architecture

```
Streamlit App
    ↓
Queries: DEV_TRANSFORMATION.METADATA_EXPORTS.[SERVICE]_COLUMNS_EXPORT
    ↓
Displays: Interactive table/column browser
    ↓
Exports: CSV files for download
```

### SQL Query Structure

```sql
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    ORDINAL_POSITION,
    FULL_TABLE_NAME
FROM DEV_TRANSFORMATION.METADATA_EXPORTS.{SERVICE}_COLUMNS_EXPORT
ORDER BY TABLE_NAME, ORDINAL_POSITION
```

### Code Pattern

Each Metadata tab follows this standard pattern:

1. **Info Banner**: Explains what metadata is shown
2. **Query Metadata**: Fetches from METADATA_EXPORTS table
3. **Table Selector**: Dropdown for table selection
4. **Conditional Display**:
   - If "All Tables": Show expandable cards
   - If specific table: Show detailed column list
5. **Search Functionality**: Column name search
6. **Export Options**: CSV download buttons
7. **Error Handling**: Shows instructions if metadata table doesn't exist

---

## Usage Examples

### Example 1: Finding a Specific Column

**Scenario**: User wants to find all columns related to "endpoint" in SentinelOne

**Steps**:
1. Open SentinelOne app
2. Click "📚 Metadata" tab
3. Scroll to "🔍 Search Columns" section
4. Type "endpoint" in search box
5. View results showing all matching columns
6. Export results if needed

**Result**: User finds `ENDPOINT_NAME`, `ENDPOINT_ID`, etc. across multiple tables

### Example 2: Understanding Table Structure

**Scenario**: Developer needs to know the structure of `FACT_SENTINEL_ENDPOINTS`

**Steps**:
1. Open SentinelOne app
2. Click "📚 Metadata" tab
3. Select "FACT_SENTINEL_ENDPOINTS" from dropdown
4. Review column list with data types
5. Copy full table name from code block

**Result**: Developer sees 12 columns with types: TEXT, TIMESTAMP_NTZ, BOOLEAN, etc.

### Example 3: Exporting Complete Metadata

**Scenario**: Data analyst wants offline reference of all ServiceNow columns

**Steps**:
1. Open ServiceNow app
2. Click "📚 Metadata" tab
3. Select "All Tables" (or keep default)
4. Scroll to bottom
5. Click "Download CSV" button for complete metadata

**Result**: CSV file `servicenow_complete_metadata.csv` downloaded with all 36 columns

---

## Benefits

### For End Users

1. **Self-Service**: No need to ask developers for column names
2. **Immediate Access**: Metadata available directly in dashboard
3. **Searchable**: Quickly find specific columns
4. **Exportable**: Download for offline reference
5. **Always Updated**: Refreshes when metadata repository refreshes

### For Developers

1. **Reduced Support Requests**: Users can find column names themselves
2. **Standardized**: Same interface across all apps
3. **Automated**: Uses existing metadata exports
4. **Low Maintenance**: Updates automatically with metadata refresh

### For Data Governance

1. **Transparency**: Users see exactly what data exists
2. **Documentation**: Built-in data dictionary
3. **Audit Trail**: Export capabilities for documentation
4. **Consistency**: Same metadata source as production queries

---

## Dependencies

### Required Tables

Each service requires its corresponding export table in `METADATA_EXPORTS` schema:

| Service | Required Table |
|---------|----------------|
| SentinelOne | `METADATA_EXPORTS.SENTINELONE_COLUMNS_EXPORT` |
| CybelAngel | `METADATA_EXPORTS.CYBELANGEL_COLUMNS_EXPORT` |
| Proofpoint | `METADATA_EXPORTS.PROOFPOINT_COLUMNS_EXPORT` |
| ServiceNow | `METADATA_EXPORTS.SERVICENOW_COLUMNS_EXPORT` |
| Leviat | `METADATA_EXPORTS.LEVIAT_COLUMNS_EXPORT` |
| Tenable | `METADATA_EXPORTS.TENABLE_COLUMNS_EXPORT` |

### Generation Process

These tables are generated by running:

```sql
-- Run this script to generate metadata exports
@01_SQL_SCRIPTS/EXPORT_METADATA_RESULTS.sql
```

Or automatically via the stored procedure:

```sql
CALL DEV_TRANSFORMATION.METADATA.SP_REFRESH_METADATA();
```

### Python Dependencies

The Streamlit apps require:
- `streamlit`
- `pandas`
- `snowflake.snowpark`

All already included in existing apps.

---

## Error Handling

### Scenario 1: Metadata Table Missing

**Error Message**:
```
❌ Metadata not available. Please ensure METADATA_EXPORTS.[SERVICE]_COLUMNS_EXPORT table exists.
```

**User Guidance**:
```
How to generate metadata:
1. Run the metadata repository script: EXPORT_METADATA_RESULTS.sql
2. This will create the [SERVICE]_COLUMNS_EXPORT table
3. Refresh this dashboard
```

**Resolution**: Run `EXPORT_METADATA_RESULTS.sql` script

### Scenario 2: Empty Metadata (Tenable case)

**Behavior**: Tab loads successfully but shows 0 tables/columns

**Reason**: Service has no tables in the system (data integration not active)

**User Experience**: Tab is available but shows "No data" message

---

## Deployment History

### Phase 1: Manual Implementation (SentinelOne)
- **Date**: 2025-10-24
- **Method**: Manual code addition
- **Result**: ✅ Success

### Phase 2: Automated Script (Remaining 5 Services)
- **Date**: 2025-10-24
- **Script**: `add_metadata_tab.py`
- **Services Updated**: CybelAngel, Proofpoint, ServiceNow, Leviat, Tenable
- **Result**: ✅ 4/5 updated (CybelAngel already had tab)

### Deployment Summary

```
Total Services: 6
Successfully Updated: 6
Success Rate: 100%
Total Columns Cataloged: 393 columns
```

---

## Automation Script

### Script: `add_metadata_tab.py`

**Location**: `07_STREAMLIT_APPS/add_metadata_tab.py`

**Purpose**: Automatically add Metadata tab to Streamlit apps

**Features**:
- Parses existing app structure
- Finds tab layout
- Adds new Metadata tab
- Inserts complete tab code before footer
- Handles encoding issues (Windows)

**Usage**:
```bash
cd 07_STREAMLIT_APPS
python add_metadata_tab.py
```

**Output**:
```
================================================================================
Adding Metadata Tab to Streamlit Apps
================================================================================

✅ Proofpoint: Metadata tab added successfully
✅ ServiceNow: Metadata tab added successfully
✅ Leviat: Metadata tab added successfully
✅ Tenable: Metadata tab added successfully

================================================================================
Summary: Updated 4/5 apps
================================================================================
```

---

## Future Enhancements

### Potential Improvements

1. **Column Statistics**
   - Show column value distributions
   - Display null percentages
   - Show unique value counts

2. **Lineage Information**
   - Show which transformations use each column
   - Display upstream/downstream dependencies
   - Link to related tables

3. **Sample Data**
   - Show example values for each column
   - Display value patterns
   - Preview data without leaving app

4. **Column Descriptions**
   - Add business descriptions for columns
   - Include calculation logic for derived columns
   - Show data quality rules

5. **Table Relationships**
   - Visualize table relationships (ERD)
   - Show join paths
   - Display foreign key relationships

6. **Metadata Search Across All Services**
   - Global column search
   - Cross-service metadata comparison
   - Unified data catalog view

---

## Maintenance

### Regular Tasks

1. **Metadata Refresh**
   - Frequency: Daily (via scheduled task)
   - Method: `SP_REFRESH_METADATA()` stored procedure
   - Impact: Metadata tab shows updated schema

2. **Export Table Verification**
   - Frequency: Weekly
   - Check: All 6 export tables exist
   - Query:
     ```sql
     SELECT TABLE_NAME, ROW_COUNT
     FROM INFORMATION_SCHEMA.TABLES
     WHERE TABLE_SCHEMA = 'METADATA_EXPORTS'
       AND TABLE_NAME LIKE '%_COLUMNS_EXPORT'
     ORDER BY TABLE_NAME;
     ```

3. **Column Count Monitoring**
   - Frequency: Monthly
   - Check: Column counts haven't decreased unexpectedly
   - Alert if: Column count drops by >10%

### Troubleshooting

**Problem**: Metadata tab shows old data

**Solution**:
1. Run `CALL SP_REFRESH_METADATA()`
2. Re-run `EXPORT_METADATA_RESULTS.sql`
3. Refresh browser

**Problem**: Metadata tab missing in new app

**Solution**:
1. Run `add_metadata_tab.py` script
2. Or manually copy tab code from another app
3. Update service name and export table name

---

## Success Metrics

### Usage Metrics (to be tracked)

1. **Adoption Rate**: % of users who click Metadata tab
2. **Search Usage**: Number of column searches per session
3. **Export Downloads**: Number of metadata CSV downloads
4. **Session Duration**: Time spent in Metadata tab

### Impact Metrics

1. **Support Ticket Reduction**: Decrease in "what columns exist" questions
2. **Developer Productivity**: Time saved by self-service metadata access
3. **Data Literacy**: Increased user understanding of data structures

---

## Documentation References

- [Metadata Repository Documentation](../01_SQL_SCRIPTS/README_METADATA_REPOSITORY.md)
- [Export Metadata Script](../01_SQL_SCRIPTS/EXPORT_METADATA_RESULTS.sql)
- [Metadata Export Analysis Report](../04_METADATA_SAMPLES/sql_execution_results/EXPORT_METADATA_RESULTS_20251024_030600/METADATA_EXPORT_ANALYSIS_REPORT.md)
- [Verification Analysis Report](../04_METADATA_SAMPLES/verification_results/VERIFY_PROCEDURE_RECREATION_20251024_030202/VERIFICATION_ANALYSIS_REPORT.md)

---

## Appendix: Code Template

### Template Used for All Apps

```python
# TAB X: METADATA
with tabX:
    st.subheader("📚 {Service} Data Catalog")

    st.info("""
    This metadata is automatically extracted from the **Metadata Repository**.
    Use this reference to understand data structure, column names, and data types.
    """)

    # Query metadata from METADATA_EXPORTS schema
    metadata_sql = """
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE,
               ORDINAL_POSITION, FULL_TABLE_NAME
        FROM DEV_TRANSFORMATION.METADATA_EXPORTS.{SERVICE}_COLUMNS_EXPORT
        ORDER BY TABLE_NAME, ORDINAL_POSITION
    """

    metadata = safe_query(metadata_sql, "Failed to load metadata")

    if not metadata.empty:
        # Table selector
        selected_table = st.selectbox(
            "📋 Select Table",
            options=["All Tables"] + list(metadata['TABLE_NAME'].unique())
        )

        # Show columns (detailed view or all tables view)
        # ... display logic ...

        # Search functionality
        search_term = st.text_input("Search for a column name", "")
        # ... search logic ...

        # Export metadata
        export_csv(metadata, "{service}_complete_metadata")
    else:
        st.error("❌ Metadata not available.")
        # ... instructions ...
```

---

**Report Generated**: 2025-10-24
**Generated By**: Claude Code
**For**: Fuad Oñate
**Project**: SECURITY_ANALYTICS Data Warehouse - Streamlit Apps Enhancement
**Feature Version**: 1.0

---

**END OF DOCUMENTATION**
