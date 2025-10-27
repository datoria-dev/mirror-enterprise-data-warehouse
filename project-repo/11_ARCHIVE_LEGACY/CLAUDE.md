# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Snowflake data model documentation and ERD generation tool for the SECURITY_ANALYTICS (IT Security KPI) system. The project analyzes and visualizes data structures across three Snowflake schemas: DEV_LANDING, DEV_TRANSFORMATION, and DEV_REPORTING.

## Key Commands

### Setup and Dependencies
```bash
# Install required packages
pip install -r requirements.txt
# Note: Also install openpyxl if using Excel export features
pip install openpyxl

# Configure Snowflake credentials
cp .env.example .env
# Edit .env with your Snowflake credentials
```

### Running the Scripts
```bash
# Generate ERD with .env configuration
python snowflake_erd_generator.py

# Generate ERD with interactive credential input
python generate_erd_interactive.py

# Generate ERD with example/mock data (no Snowflake connection needed)
python generate_erd_example.py

# Process exported CSV results from Snowflake
python process_snowflake_results.py

# Export metadata to multiple formats (Excel, JSON, Markdown)
python export_snowflake_metadata.py
```

### SQL Analysis
The main analysis queries are in `ITSECKPI_DataModel_Analysis.sql` with 13 sections:
1. Object inventory and counts
2. Table structures and metadata
3. Column details and data types
4. Primary and foreign key relationships
5. Data quality statistics
6. View and procedure dependencies
7. User privileges and roles
8. Tasks and pipelines
9. Data volume metrics
10. Performance indicators
11. Documentation extraction
12. Recommendations
13. Export formats

Execute these queries directly in Snowflake or Snowsight.

## Architecture

### Data Flow
1. **DEV_LANDING** (Raw Data Layer - Orange #FF9933)
   - Ingests raw KPI metrics, system events, and performance data
   - Tables: RAW_KPI_METRICS, RAW_SYSTEM_EVENTS, RAW_PERFORMANCE_DATA

2. **DEV_TRANSFORMATION** (Star Schema Layer - Blue #3399FF)
   - Dimensional modeling with fact and dimension tables
   - Facts: FACT_KPI_MEASUREMENTS
   - Dimensions: DIM_KPI, DIM_SYSTEM, DIM_DATE

3. **DEV_REPORTING** (Reporting Layer - Green #33CC33)
   - Views and aggregations for dashboards and reports
   - Views: VW_KPI_DASHBOARD, VW_SYSTEM_PERFORMANCE

### Script Architecture
- **snowflake_erd_generator.py**: Main production script using .env configuration
- **generate_erd_interactive.py**: Development version with credential prompts
- **generate_erd_example.py**: Demo version with mock data, no Snowflake required
- **process_snowflake_results.py**: Processes CSV exports from Snowflake queries
- **export_snowflake_metadata.py**: Multi-format export utility (Excel, JSON, Markdown)

### Output Files
- `snowflake_itseckpi_erd.dot`: Graphviz source for diagram generation
- `snowflake_itseckpi_viewer.html`: Interactive HTML visualization
- `snowflake_itseckpi_report.md`: Markdown documentation report
- Generated images: SVG/PNG format ERD diagrams

## Important Considerations

### Snowflake Connection
All scripts except `generate_erd_example.py` and `generate_erd_simple.py` require valid Snowflake credentials. Configure these via:
- `.env` file (copy from `.env.example`)
- Interactive prompts (for interactive scripts)
- Environment variables: SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_WAREHOUSE, SNOWFLAKE_ROLE

### Color Coding Convention
- Orange (#FF9933): Landing/Raw layer objects
- Blue (#3399FF): Transformation/Star schema objects
- Green (#33CC33): Reporting/View layer objects
- Gray (#999999): External/system objects

### Missing Dependencies
The `requirements.txt` file is missing `openpyxl` which is needed for Excel export functionality in `export_snowflake_metadata.py`. Install it separately if needed.

### Database Permissions
Scripts require appropriate Snowflake permissions to:
- Access INFORMATION_SCHEMA views
- Read table metadata and statistics
- Query system tables for relationships and dependencies

### Performance Notes
- Large schemas may take time to process
- Consider using `generate_erd_simple.py` for quick local testing
- HTML viewer provides interactive navigation for complex diagrams