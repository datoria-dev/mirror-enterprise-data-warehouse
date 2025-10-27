# Prompt for Metadata Extraction and ERD Generation from Snowflake

## Objective
Extract all information from the 3 data layers (landing, transformation, and reporting) of the `SECURITY_ANALYTICS` schema in Snowflake and generate complete ERD diagrams with all associated documentation.

## System Context
- **Database**: Snowflake
- **Main Schema**: `SECURITY_ANALYTICS`
- **Data Layers**:
  1. **Landing Layer**: Tables with prefix `L_` or in schema `itseckpi_landing`
  2. **Transformation Layer**: Tables with prefix `T_` or in schema `itseckpi_transform`
  3. **Reporting Layer**: Tables with prefix `R_` or in schema `itseckpi_reporting`

## Required Tasks

### 1. Configuration and Connection
```python
# Configure Snowflake connection using the following credentials:
# (I will provide them when you execute the code)
# - account: [ACCOUNT]
# - user: [USER]
# - password: [PASSWORD]
# - warehouse: [WAREHOUSE]
# - database: [DATABASE]
# - schema: SECURITY_ANALYTICS
```

### 2. Metadata Extraction
Extract the following information for ALL tables in the schema:

#### 2.1 Table Information
```sql
-- For each layer, execute:
SELECT
    TABLE_CATALOG,
    TABLE_SCHEMA,
    TABLE_NAME,
    TABLE_TYPE,
    ROW_COUNT,
    BYTES,
    CREATED,
    LAST_ALTERED,
    COMMENT
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
AND (
    TABLE_NAME LIKE 'L_%'  -- Landing
    OR TABLE_NAME LIKE 'T_%'  -- Transformation
    OR TABLE_NAME LIKE 'R_%'  -- Reporting
)
ORDER BY TABLE_NAME;
```

#### 2.2 Column Information
```sql
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    ORDINAL_POSITION,
    COLUMN_DEFAULT,
    IS_NULLABLE,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    NUMERIC_PRECISION,
    NUMERIC_SCALE,
    COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
ORDER BY TABLE_NAME, ORDINAL_POSITION;
```

#### 2.3 Constraints and Relationships
```sql
-- Primary Keys
SELECT
    tc.TABLE_NAME,
    tc.CONSTRAINT_NAME,
    tc.CONSTRAINT_TYPE,
    kcu.COLUMN_NAME,
    kcu.ORDINAL_POSITION
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
    ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
    AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
WHERE tc.TABLE_SCHEMA = 'SECURITY_ANALYTICS'
    AND tc.CONSTRAINT_TYPE IN ('PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE')
ORDER BY tc.TABLE_NAME, kcu.ORDINAL_POSITION;

-- Foreign Keys and References
SELECT
    tc.TABLE_NAME as SOURCE_TABLE,
    kcu.COLUMN_NAME as SOURCE_COLUMN,
    rc.UNIQUE_CONSTRAINT_NAME,
    rc.REFERENCED_TABLE_NAME,
    rc.REFERENCED_COLUMN_NAME
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
    ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
JOIN INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
    ON tc.CONSTRAINT_NAME = rc.CONSTRAINT_NAME
WHERE tc.TABLE_SCHEMA = 'SECURITY_ANALYTICS'
    AND tc.CONSTRAINT_TYPE = 'FOREIGN KEY';
```

#### 2.4 Views and Dependencies
```sql
-- Identify views and their dependencies
SELECT
    TABLE_NAME as VIEW_NAME,
    VIEW_DEFINITION
FROM INFORMATION_SCHEMA.VIEWS
WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS';
```

### 3. Relationship Analysis
Analyze and detect:
- **Explicit relationships**: Using defined foreign keys
- **Implicit relationships**: Based on naming patterns (e.g., `customer_id` in multiple tables)
- **Cross-layer relationships**: How data flows from Landing → Transformation → Reporting
- **Lookup/dimension tables**: Identify master tables vs. transactional tables

### 4. ERD Diagram Generation

#### 4.1 ERD by Layer
Generate 3 separate diagrams:
1. **Landing Layer ERD**: Only `L_*` tables
2. **Transformation Layer ERD**: Only `T_*` tables
3. **Reporting Layer ERD**: Only `R_*` tables

#### 4.2 Integrated ERD
A master diagram showing data flow between the 3 layers with:
- Different colors per layer (Landing: blue, Transform: yellow, Reporting: green)
- Arrows indicating data flow
- Relationship cardinality (1:1, 1:N, N:M)

#### 4.3 Output Formats
Generate ERDs in the following formats:
1. **Mermaid**: For Markdown visualization
2. **PlantUML**: For technical documentation
3. **DBML**: For dbdiagram.io
4. **Python (diagrams)**: Using the `diagrams` library to generate PNG/SVG
5. **Draw.io XML**: For later editing

### 5. Documentation

#### 5.1 Excel with Metadata
Create an Excel file (`snowflake_erd_analysis.xlsx`) with the following sheets:
1. **Overview**: Statistical summary of each layer
2. **Tables**: Complete list of tables with metadata
3. **Columns**: All columns with data types and descriptions
4. **Relationships**: Matrix of relationships between tables
5. **Data Lineage**: Data flow between layers
6. **Issues**: Problems found (orphan tables, unused columns, etc.)

#### 5.2 Markdown Documentation
Generate a `database_documentation.md` file with:
```markdown
# SECURITY_ANALYTICS Schema Documentation

## 1. Executive Summary
- Total tables per layer
- Data volume
- Relationship complexity

## 2. Landing Layer
### 2.1 Purpose
### 2.2 Tables
[Detailed list of each table with description]
### 2.3 ERD
[Mermaid Diagram]

## 3. Transformation Layer
[Similar structure]

## 4. Reporting Layer
[Similar structure]

## 5. Data Lineage
[Flow diagram between layers]

## 6. Data Dictionary
[Table with all important columns]

## 7. Identified Business Rules
[Based on constraints and patterns]

## 8. Optimization Recommendations
[Suggestions based on analysis]
```

### 6. Validation and Quality Checks

Perform the following validations:
1. **Referential integrity**: Verify that all FKs point to valid PKs
2. **Orphan tables**: Identify tables without relationships
3. **Unused columns**: Detect columns that might be obsolete
4. **Naming inconsistencies**: Report deviations from naming standard
5. **Duplicate data**: Identify possible redundancies between layers

### 7. Automation Script

Create a complete Python script that:
1. Connects to Snowflake
2. Extracts all metadata
3. Generates all ERD diagrams
4. Creates documentation
5. Exports everything to an organized folder:
```
snowflake_erd_output/
├── diagrams/
│   ├── landing_layer.png
│   ├── transformation_layer.png
│   ├── reporting_layer.png
│   ├── full_schema.png
│   └── data_flow.png
├── documentation/
│   ├── database_documentation.md
│   └── snowflake_erd_analysis.xlsx
├── scripts/
│   ├── mermaid_diagrams.md
│   ├── plantuml_diagrams.puml
│   └── dbml_schema.dbml
└── logs/
    └── extraction_log.txt
```

## Example Code to Get Started

```python
import snowflake.connector
import pandas as pd
import networkx as nx
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extraction_log.txt'),
        logging.StreamHandler()
    ]
)

class SnowflakeERDExtractor:
    def __init__(self, connection_params):
        self.conn = snowflake.connector.connect(**connection_params)
        self.cursor = self.conn.cursor()
        self.metadata = {}

    def extract_all_metadata(self):
        """Extract all schema metadata"""
        logging.info("Starting metadata extraction...")
        # Implement extraction here

    def generate_erd_diagrams(self):
        """Generate all ERD diagrams"""
        logging.info("Generating ERD diagrams...")
        # Implement generation here

    def create_documentation(self):
        """Create all documentation"""
        logging.info("Creating documentation...")
        # Implement documentation here

# Use the extractor
if __name__ == "__main__":
    # Request credentials securely
    connection_params = {
        'account': input("Snowflake Account: "),
        'user': input("Username: "),
        'password': getpass.getpass("Password: "),
        'warehouse': input("Warehouse: "),
        'database': input("Database: "),
        'schema': 'SECURITY_ANALYTICS'
    }

    extractor = SnowflakeERDExtractor(connection_params)
    extractor.extract_all_metadata()
    extractor.generate_erd_diagrams()
    extractor.create_documentation()
```

## Additional Considerations

1. **Performance**: For large schemas, implement pagination and batch processing
2. **Security**: Don't hardcode credentials, use environment variables or secrets
3. **Versioning**: Include timestamp in all generated files
4. **Incremental**: Capability to update only changes since last execution
5. **Notifications**: Send summary by email or Slack when complete

## Expected Output

Upon completion, you should have:
- ✅ High-quality visual ERD diagrams for each layer
- ✅ Complete documentation in Markdown and Excel
- ✅ Reusable scripts for future updates
- ✅ Data quality analysis and recommendations
- ✅ Complete map of data flow between layers

---

**Note**: Make sure you have the following libraries installed:
```bash
pip install snowflake-connector-python pandas openpyxl networkx matplotlib graphviz diagrams pillow XlsxWriter
```
