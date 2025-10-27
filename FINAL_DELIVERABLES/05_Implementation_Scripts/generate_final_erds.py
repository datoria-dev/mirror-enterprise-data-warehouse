"""
Generate Final ERD Diagrams for SECURITY_ANALYTICS Data Model
Creates comprehensive Entity Relationship Diagrams for all layers
"""

import snowflake.connector
import os
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables
load_dotenv()

def create_connection():
    """Create Snowflake connection"""
    try:
        conn = snowflake.connector.connect(
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            user=os.getenv('SNOWFLAKE_USER'),
            authenticator='externalbrowser',
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            role=os.getenv('SNOWFLAKE_ROLE')
        )
        return conn
    except Exception as e:
        print(f"[ERROR] Connection failed: {str(e)}")
        return None

def generate_erd_diagrams(conn):
    """Generate ERD diagrams for all layers"""
    cursor = conn.cursor()

    print("\n" + "="*70)
    print("GENERATING ERD DIAGRAMS")
    print("="*70)

    # Set database and schema
    cursor.execute("USE DATABASE DEV_TRANSFORMATION")
    cursor.execute("USE SCHEMA SECURITY_ANALYTICS")

    # Get all tables with their types
    cursor.execute("""
        SELECT
            TABLE_NAME,
            CASE
                WHEN TABLE_NAME LIKE 'DIM_%' THEN 'DIMENSION'
                WHEN TABLE_NAME LIKE 'FACT_%' THEN 'FACT'
                ELSE 'SUPPORTING'
            END AS TABLE_TYPE,
            ROW_COUNT
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
            AND TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_TYPE, TABLE_NAME
    """)

    tables = cursor.fetchall()

    # Get all foreign key relationships
    fk_query = """
        WITH table_constraints AS (
            SELECT DISTINCT
                CONSTRAINT_NAME,
                TABLE_NAME,
                CONSTRAINT_TYPE
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
            WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                AND CONSTRAINT_TYPE = 'FOREIGN KEY'
        )
        SELECT
            tc.TABLE_NAME AS FROM_TABLE,
            'REFERENCES' AS RELATIONSHIP,
            tc.CONSTRAINT_NAME AS TO_TABLE
        FROM table_constraints tc
    """

    # Since we might not have access to KEY_COLUMN_USAGE, we'll use our knowledge
    # of the implemented relationships
    relationships = [
        ('FACT_AV_HEALTH', 'DIM_HOST', 'HOST_ID'),
        ('FACT_AV_HEALTH', 'DIM_AV_PRODUCTS', 'AV_PRODUCT_ID'),
        ('FACT_AV_OPCO', 'DIM_OPCO', 'OPCO_ID'),
        ('FACT_AV_OPCO', 'DIM_AV_PRODUCTS', 'AV_PRODUCT_ID'),
        ('FACT_BITSIGHT_FINDINGS', 'DIM_BITSIGHT_CATEGORIES', 'CATEGORY_ID'),
        ('FACT_BITSIGHT_RISK_VECTORS', 'DIM_BITSIGHT_CATEGORIES', 'CATEGORY_ID'),
        ('FACT_CYBELANGEL_THREATS', 'DIM_CYBELANGEL_ALERTS', 'ALERT_ID'),
        ('FACT_DEFENDER_ENDPOINTS', 'DIM_HOST', 'HOST_ID'),
        ('FACT_FIXED_VULNERABILITIES', 'DIM_QUALYS_VULN', 'VULN_ID'),
        ('FACT_FIXED_VULNERABILITIES', 'DIM_HOST', 'HOST_ID'),
        ('FACT_HOST_ASSETS', 'DIM_HOST', 'HOST_ID'),
        ('FACT_QUALYS', 'DIM_HOST', 'HOST_ID'),
        ('FACT_QUALYS', 'DIM_QUALYS_VULN', 'VULN_ID'),
        ('FACT_REMEDIATION_EVENTS', 'DIM_HOST', 'HOST_ID'),
    ]

    # Generate Main ERD (All Tables)
    print("\n[GENERATING] Complete ERD...")

    dot_content = """digraph ITSECKPI_Complete {
    rankdir=LR;
    node [shape=rectangle, style=filled];

    // Styling
    graph [fontname="Arial", fontsize=12, bgcolor="white"];
    node [fontname="Arial", fontsize=10];
    edge [fontname="Arial", fontsize=9];

    // Title
    labelloc="t";
    label="SECURITY_ANALYTICS Complete Data Model\\nGenerated: """ + datetime.now().strftime('%Y-%m-%d') + """";

    // Subgraphs for different table types
    subgraph cluster_dimensions {
        label="Dimension Tables";
        style=filled;
        color=lightgrey;
        node [fillcolor=lightblue];

"""

    # Add dimension tables
    dim_tables = [t for t in tables if t[0].startswith('DIM_')]
    for table in dim_tables:
        table_name = table[0]
        row_count = table[2] if table[2] else 0
        dot_content += f'        "{table_name}" [label="{table_name}\\n({row_count:,} rows)"];\n'

    dot_content += """    }

    subgraph cluster_facts {
        label="Fact Tables";
        style=filled;
        color=lightgrey;
        node [fillcolor=lightyellow];

"""

    # Add fact tables
    fact_tables = [t for t in tables if t[0].startswith('FACT_')]
    for table in fact_tables:
        table_name = table[0]
        row_count = table[2] if table[2] else 0
        dot_content += f'        "{table_name}" [label="{table_name}\\n({row_count:,} rows)"];\n'

    dot_content += """    }

    subgraph cluster_supporting {
        label="Supporting Tables";
        style=filled;
        color=lightgrey;
        node [fillcolor=lightgreen];

"""

    # Add supporting tables
    other_tables = [t for t in tables if not t[0].startswith('DIM_') and not t[0].startswith('FACT_')]
    for table in other_tables[:20]:  # Limit to first 20 to avoid clutter
        table_name = table[0]
        row_count = table[2] if table[2] else 0
        dot_content += f'        "{table_name}" [label="{table_name}\\n({row_count:,} rows)"];\n'

    dot_content += """    }

    // Relationships
"""

    # Add relationships
    for rel in relationships:
        dot_content += f'    "{rel[0]}" -> "{rel[1]}" [label="{rel[2]}"];\n'

    dot_content += "}"

    # Save complete ERD
    with open("FINAL_DELIVERABLES/02_ERD_Diagrams/ITSECKPI_Complete_ERD.dot", "w") as f:
        f.write(dot_content)
    print("  [SUCCESS] Complete ERD saved")

    # Generate Dimensional Model ERD (DIM and FACT only)
    print("\n[GENERATING] Dimensional Model ERD...")

    dim_dot = """digraph ITSECKPI_Dimensional {
    rankdir=TB;
    node [shape=rectangle, style=filled];

    // Styling
    graph [fontname="Arial", fontsize=14, bgcolor="white", pad="0.5"];
    node [fontname="Arial", fontsize=11];
    edge [fontname="Arial", fontsize=10];

    // Title
    labelloc="t";
    label="SECURITY_ANALYTICS Dimensional Model (Star Schema)\\nGenerated: """ + datetime.now().strftime('%Y-%m-%d') + """";

    // Central fact tables
    subgraph cluster_center {
        label="Fact Tables (Measures)";
        style=filled;
        color=lightgoldenrod;
        node [fillcolor=gold, shape=box3d];

"""

    # Add main fact tables
    main_facts = ['FACT_QUALYS', 'FACT_AV_OPCO', 'FACT_BITSIGHT_FINDINGS',
                  'FACT_CYBELANGEL_THREATS', 'FACT_HOST_ASSETS']
    for table_name in main_facts:
        table_data = next((t for t in fact_tables if t[0] == table_name), None)
        if table_data:
            row_count = table_data[2] if table_data[2] else 0
            dim_dot += f'        "{table_name}" [label="{table_name}\\n{row_count:,} rows"];\n'

    dim_dot += """    }

    // Dimension tables around the edges
"""

    # Add dimension tables with categorization
    security_dims = ['DIM_HOST', 'DIM_QUALYS_VULN', 'DIM_OPCO', 'DIM_AV_PRODUCTS']
    for dim in security_dims:
        table_data = next((t for t in dim_tables if t[0] == dim), None)
        if table_data:
            row_count = table_data[2] if table_data[2] else 0
            dim_dot += f'    "{dim}" [label="{dim}\\n{row_count:,} rows", fillcolor=lightblue];\n'

    # Add relationships in star pattern
    dim_dot += "\n    // Star Schema Relationships\n"
    star_relationships = [
        ('FACT_QUALYS', 'DIM_HOST'),
        ('FACT_QUALYS', 'DIM_QUALYS_VULN'),
        ('FACT_AV_OPCO', 'DIM_OPCO'),
        ('FACT_AV_OPCO', 'DIM_AV_PRODUCTS'),
        ('FACT_BITSIGHT_FINDINGS', 'DIM_BITSIGHT_CATEGORIES'),
        ('FACT_HOST_ASSETS', 'DIM_HOST'),
    ]

    for rel in star_relationships:
        dim_dot += f'    "{rel[1]}" -> "{rel[0]}" [dir=none, style=bold];\n'

    dim_dot += "}"

    # Save dimensional ERD
    with open("FINAL_DELIVERABLES/02_ERD_Diagrams/ITSECKPI_Dimensional_ERD.dot", "w") as f:
        f.write(dim_dot)
    print("  [SUCCESS] Dimensional Model ERD saved")

    # Generate Service-Specific ERD
    print("\n[GENERATING] Service-Specific ERDs...")

    services = {
        'Endpoint_Security': {
            'dims': ['DIM_HOST', 'DIM_CROWDSTRIKE', 'DIM_MCAFEE', 'DIM_SOPHOS',
                    'DIM_SYMANTEC', 'DIM_TRENDMICRO'],
            'facts': ['FACT_AV_HEALTH', 'FACT_DEFENDER_ENDPOINTS']
        },
        'Vulnerability_Management': {
            'dims': ['DIM_QUALYS_HOST', 'DIM_QUALYS_VULN', 'DIM_BITSIGHT_CATEGORIES'],
            'facts': ['FACT_QUALYS', 'FACT_BITSIGHT_FINDINGS', 'FACT_FIXED_VULNERABILITIES']
        },
        'Threat_Intelligence': {
            'dims': ['DIM_CYBELANGEL_ALERTS', 'DIM_ZEROFOX_ALERTS', 'DIM_ZEROFOX_ASSETS',
                    'DIM_THREAT_INTEL', 'DIM_SENTINEL'],
            'facts': ['FACT_CYBELANGEL_THREATS', 'FACT_THREAT_INTEL_EVENTS']
        }
    }

    for service_name, service_tables in services.items():
        service_dot = f"""digraph ITSECKPI_{service_name} {{
    rankdir=LR;
    node [shape=rectangle, style=filled];

    // Title
    labelloc="t";
    label="SECURITY_ANALYTICS - {service_name.replace('_', ' ')}\\nGenerated: {datetime.now().strftime('%Y-%m-%d')}";

    // Dimensions
    subgraph cluster_dims {{
        label="Dimensions";
        style=filled;
        color=lightgrey;
        node [fillcolor=lightblue];

"""
        for dim in service_tables['dims']:
            service_dot += f'        "{dim}";\n'

        service_dot += """    }

    // Facts
    subgraph cluster_facts {
        label="Facts";
        style=filled;
        color=lightgrey;
        node [fillcolor=lightyellow];

"""
        for fact in service_tables['facts']:
            service_dot += f'        "{fact}";\n'

        service_dot += """    }
}"""

        filename = f"FINAL_DELIVERABLES/02_ERD_Diagrams/ITSECKPI_{service_name}_ERD.dot"
        with open(filename, "w") as f:
            f.write(service_dot)
        print(f"  [SUCCESS] {service_name} ERD saved")

    # Create HTML viewer for ERDs
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>SECURITY_ANALYTICS ERD Viewer</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/viz.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/full.render.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .erd-container { border: 1px solid #ccc; padding: 10px; margin: 20px 0; }
        .erd-title { font-weight: bold; margin-bottom: 10px; }
        #graph { text-align: center; }
    </style>
</head>
<body>
    <h1>SECURITY_ANALYTICS Data Model - ERD Diagrams</h1>

    <div class="erd-container">
        <div class="erd-title">Instructions:</div>
        <ol>
            <li>Open the .dot files in a Graphviz viewer</li>
            <li>Or use online tool: https://dreampuf.github.io/GraphvizOnline/</li>
            <li>Copy the .dot file content and paste to view the diagram</li>
        </ol>
    </div>

    <div class="erd-container">
        <div class="erd-title">Available Diagrams:</div>
        <ul>
            <li>ITSECKPI_Complete_ERD.dot - Full data model with all tables</li>
            <li>ITSECKPI_Dimensional_ERD.dot - Star schema view</li>
            <li>ITSECKPI_Endpoint_Security_ERD.dot - Endpoint protection services</li>
            <li>ITSECKPI_Vulnerability_Management_ERD.dot - Vulnerability services</li>
            <li>ITSECKPI_Threat_Intelligence_ERD.dot - Threat intel services</li>
        </ul>
    </div>
</body>
</html>"""

    with open("FINAL_DELIVERABLES/02_ERD_Diagrams/ERD_Viewer.html", "w") as f:
        f.write(html_content)
    print("\n  [SUCCESS] ERD Viewer HTML created")

    print("\n" + "="*70)
    print("ERD GENERATION COMPLETE")
    print("="*70)
    print("\nGenerated files:")
    print("  1. ITSECKPI_Complete_ERD.dot")
    print("  2. ITSECKPI_Dimensional_ERD.dot")
    print("  3. ITSECKPI_Endpoint_Security_ERD.dot")
    print("  4. ITSECKPI_Vulnerability_Management_ERD.dot")
    print("  5. ITSECKPI_Threat_Intelligence_ERD.dot")
    print("  6. ERD_Viewer.html")

    print("\nTo view diagrams:")
    print("  - Open .dot files in Graphviz")
    print("  - Or use: https://dreampuf.github.io/GraphvizOnline/")

    cursor.close()
    return True

def main():
    """Main execution"""
    conn = create_connection()
    if not conn:
        print("[ERROR] Failed to connect to Snowflake")
        return False

    try:
        success = generate_erd_diagrams(conn)
        return success
    except Exception as e:
        print(f"[ERROR] ERD generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)