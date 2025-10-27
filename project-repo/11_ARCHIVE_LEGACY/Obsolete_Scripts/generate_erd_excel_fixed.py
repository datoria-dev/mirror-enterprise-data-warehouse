"""
Generate Excel file with ERD documentation from Snowflake metadata
Fixed version with proper data extraction and encoding
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

# Force UTF-8 encoding for console output
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Read the latest metadata extraction results
results_dir = Path('QUERY_RESULTS')
metadata_files = sorted(results_dir.glob('results_EXTRACT_COMPLETE_ERD_METADATA_*.json'))

if not metadata_files:
    print("ERROR: No metadata files found!")
    sys.exit(1)

latest_file = metadata_files[-1]
print(f"Reading metadata from: {latest_file}")

with open(latest_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total statements in JSON: {len(data['statements'])}")

# Create Excel workbook
wb = Workbook()
wb.remove(wb.active)  # Remove default sheet

# Styles
header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
header_font = Font(color="FFFFFF", bold=True, size=11)
subheader_fill = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")
subheader_font = Font(bold=True, size=10)
border = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)

def style_header(ws, row=1, cols=None):
    """Apply header styling to a row"""
    if cols is None:
        cols = ws.max_column
    for col in range(1, cols + 1):
        cell = ws.cell(row=row, column=col)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = border

def auto_size_columns(ws, max_width=60):
    """Auto-size columns based on content with max width"""
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if cell.value:
                    cell_len = len(str(cell.value))
                    if cell_len > max_length:
                        max_length = cell_len
            except:
                pass
        adjusted_width = min(max_length + 2, max_width)
        ws.column_dimensions[column_letter].width = adjusted_width

def find_statement_by_keyword(statements, keyword):
    """Find statement containing specific keyword in SQL"""
    for stmt in statements:
        if keyword in stmt.get('sql', ''):
            return stmt
    return None

def find_statement_by_num(statements, num):
    """Find statement by number"""
    for stmt in statements:
        if stmt.get('num') == num:
            return stmt
    return None

# ============================================================================
# SHEET 1: Summary
# ============================================================================
print("\nCreating Sheet 1: Architecture Summary...")
ws_summary = wb.create_sheet("Architecture Summary")

summary_data = [
    ["SECURITY_ANALYTICS Data Warehouse - Architecture Summary"],
    ["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
    ["Environment:", "DEV (Development)"],
    ["Cloud Platform:", "Microsoft Azure Snowflake"],
    ["Account:", "mw76572.east-us-2.azure"],
    [""],
    ["Layer", "Tables", "Views", "Procedures", "Total Objects"],
    ["DEV_LANDING", "141", "11", "0", "152"],
    ["DEV_TRANSFORMATION", "117", "50+", "15", "184+"],
    ["DEV_REPORTING", "18", "148", "10", "176"],
    ["TOTAL", "276", "209+", "25", "512+"],
    [""],
    ["Key Metrics", "Value"],
    ["Primary Keys", "72"],
    ["Foreign Keys", "17"],
    ["Documented Tables", "45"],
    ["Data Size (approx)", "~28 GB"],
    ["Dimension Tables", "32"],
    ["Fact Tables", "23"],
]

for row_idx, row_data in enumerate(summary_data, 1):
    for col_idx, value in enumerate(row_data, 1):
        cell = ws_summary.cell(row=row_idx, column=col_idx, value=value)
        if row_idx == 1:
            cell.font = Font(bold=True, size=14, color="366092")
        elif row_idx in [7, 13]:
            cell.font = subheader_font
            cell.fill = subheader_fill

style_header(ws_summary, 7, 5)
style_header(ws_summary, 13, 2)
auto_size_columns(ws_summary)

# ============================================================================
# SHEET 2: Layer 1 - Landing Tables
# ============================================================================
print("Creating Sheet 2: Layer 1 - Landing...")
ws_landing = wb.create_sheet("Layer 1 - Landing")

# Find landing tables - statement #8
stmt_landing = find_statement_by_num(data['statements'], 8)
landing_tables = []

if stmt_landing and stmt_landing.get('success'):
    for row in stmt_landing.get('rows', []):
        landing_tables.append([
            row.get('OBJECT_NAME', ''),
            row.get('ROW_COUNT', '0'),
            row.get('SIZE_MB', '0'),
            row.get('COMMENT', '') or ''
        ])
    print(f"  Found {len(landing_tables)} landing tables")
else:
    print("  WARNING: Landing tables statement not found or failed")

ws_landing.append(["Landing Zone Tables (DEV_LANDING.SECURITY_ANALYTICS)"])
ws_landing.append([])
ws_landing.append(["Table Name", "Row Count", "Size (MB)", "Description"])

for table in landing_tables:
    ws_landing.append(table)

ws_landing.cell(1, 1).font = Font(bold=True, size=14, color="366092")
style_header(ws_landing, 3, 4)
auto_size_columns(ws_landing)

# ============================================================================
# SHEET 3: Layer 1 - Landing Views
# ============================================================================
print("Creating Sheet 3: Layer 1 - Landing Views...")
ws_landing_views = wb.create_sheet("Layer 1 - Landing Views")

# Find landing views - statement #10
stmt_landing_views = find_statement_by_num(data['statements'], 10)
landing_views = []

if stmt_landing_views and stmt_landing_views.get('success'):
    for row in stmt_landing_views.get('rows', []):
        landing_views.append([
            row.get('OBJECT_NAME', ''),
            row.get('COMMENT', '') or ''
        ])
    print(f"  Found {len(landing_views)} landing views")

ws_landing_views.append(["Landing Views (DEV_LANDING.SECURITY_ANALYTICS)"])
ws_landing_views.append([])
ws_landing_views.append(["View Name", "Description"])

for view in landing_views:
    ws_landing_views.append(view)

ws_landing_views.cell(1, 1).font = Font(bold=True, size=14, color="366092")
style_header(ws_landing_views, 3, 2)
auto_size_columns(ws_landing_views)

# ============================================================================
# SHEET 4: Layer 2 - Dimensions
# ============================================================================
print("Creating Sheet 4: Layer 2 - Dimensions...")
ws_dimensions = wb.create_sheet("Layer 2 - Dimensions")

# Find dimensions - statement #14
stmt_dims = find_statement_by_num(data['statements'], 14)
dimensions = []

if stmt_dims and stmt_dims.get('success'):
    for row in stmt_dims.get('rows', []):
        dimensions.append([
            row.get('OBJECT_NAME', ''),
            row.get('ROW_COUNT', '0'),
            row.get('SIZE_MB', '0'),
            row.get('COMMENT', '') or ''
        ])
    print(f"  Found {len(dimensions)} dimension tables")

ws_dimensions.append(["Dimension Tables (DEV_TRANSFORMATION.SECURITY_ANALYTICS)"])
ws_dimensions.append([])
ws_dimensions.append(["Dimension Name", "Row Count", "Size (MB)", "Description"])

for dim in sorted(dimensions, key=lambda x: x[0]):  # Sort alphabetically
    ws_dimensions.append(dim)

ws_dimensions.cell(1, 1).font = Font(bold=True, size=14, color="366092")
style_header(ws_dimensions, 3, 4)
auto_size_columns(ws_dimensions)

# ============================================================================
# SHEET 5: Layer 2 - Facts
# ============================================================================
print("Creating Sheet 5: Layer 2 - Facts...")
ws_facts = wb.create_sheet("Layer 2 - Facts")

# Find facts - statement #16
stmt_facts = find_statement_by_num(data['statements'], 16)
facts = []

if stmt_facts and stmt_facts.get('success'):
    for row in stmt_facts.get('rows', []):
        facts.append([
            row.get('OBJECT_NAME', ''),
            row.get('ROW_COUNT', '0'),
            row.get('SIZE_MB', '0'),
            row.get('COMMENT', '') or ''
        ])
    print(f"  Found {len(facts)} fact tables")

ws_facts.append(["Fact Tables (DEV_TRANSFORMATION.SECURITY_ANALYTICS)"])
ws_facts.append([])
ws_facts.append(["Fact Name", "Row Count", "Size (MB)", "Description"])

for fact in sorted(facts, key=lambda x: x[0]):
    ws_facts.append(fact)

ws_facts.cell(1, 1).font = Font(bold=True, size=14, color="366092")
style_header(ws_facts, 3, 4)
auto_size_columns(ws_facts)

# ============================================================================
# SHEET 6: Layer 2 - Other Tables
# ============================================================================
print("Creating Sheet 6: Layer 2 - Other Tables...")
ws_other = wb.create_sheet("Layer 2 - Other Tables")

# Find other tables - statement #18
stmt_other = find_statement_by_num(data['statements'], 18)
other_tables = []

if stmt_other and stmt_other.get('success'):
    for row in stmt_other.get('rows', []):
        other_tables.append([
            row.get('OBJECT_NAME', ''),
            row.get('ROW_COUNT', '0'),
            row.get('SIZE_MB', '0'),
            row.get('COMMENT', '') or ''
        ])
    print(f"  Found {len(other_tables)} other tables")

ws_other.append(["Support Tables (DEV_TRANSFORMATION.SECURITY_ANALYTICS)"])
ws_other.append([])
ws_other.append(["Table Name", "Row Count", "Size (MB)", "Description"])

for table in sorted(other_tables, key=lambda x: x[0]):
    ws_other.append(table)

ws_other.cell(1, 1).font = Font(bold=True, size=14, color="366092")
style_header(ws_other, 3, 4)
auto_size_columns(ws_other)

# ============================================================================
# SHEET 7: Layer 2 - Views
# ============================================================================
print("Creating Sheet 7: Layer 2 - Transformation Views...")
ws_trans_views = wb.create_sheet("Layer 2 - Views")

# Find transformation views - statement #20
stmt_trans_views = find_statement_by_num(data['statements'], 20)
trans_views = []

if stmt_trans_views and stmt_trans_views.get('success'):
    for row in stmt_trans_views.get('rows', []):
        trans_views.append([
            row.get('OBJECT_NAME', ''),
            row.get('COMMENT', '') or ''
        ])
    print(f"  Found {len(trans_views)} transformation views")

ws_trans_views.append(["Transformation Views (DEV_TRANSFORMATION.SECURITY_ANALYTICS)"])
ws_trans_views.append([])
ws_trans_views.append(["View Name", "Description"])

for view in sorted(trans_views, key=lambda x: x[0]):
    ws_trans_views.append(view)

ws_trans_views.cell(1, 1).font = Font(bold=True, size=14, color="366092")
style_header(ws_trans_views, 3, 2)
auto_size_columns(ws_trans_views)

# ============================================================================
# SHEET 8: Layer 2 - Procedures
# ============================================================================
print("Creating Sheet 8: Layer 2 - Stored Procedures...")
ws_procedures = wb.create_sheet("Layer 2 - Procedures")

# Find procedures - statement #22
stmt_procs = find_statement_by_num(data['statements'], 22)
procedures = []

if stmt_procs and stmt_procs.get('success'):
    for row in stmt_procs.get('rows', []):
        procedures.append([
            row.get('OBJECT_NAME', ''),
            row.get('ARGUMENT_SIGNATURE', ''),
            row.get('PROCEDURE_LANGUAGE', '')
        ])
    print(f"  Found {len(procedures)} stored procedures")

ws_procedures.append(["Stored Procedures (DEV_TRANSFORMATION.SECURITY_ANALYTICS)"])
ws_procedures.append([])
ws_procedures.append(["Procedure Name", "Arguments", "Language"])

for proc in sorted(procedures, key=lambda x: x[0]):
    ws_procedures.append(proc)

ws_procedures.cell(1, 1).font = Font(bold=True, size=14, color="366092")
style_header(ws_procedures, 3, 3)
auto_size_columns(ws_procedures)

# ============================================================================
# SHEET 9: Layer 3 - Reporting Tables
# ============================================================================
print("Creating Sheet 9: Layer 3 - Reporting Tables...")
ws_rep_tables = wb.create_sheet("Layer 3 - Tables")

# Find reporting tables - statement #28
stmt_rep_tables = find_statement_by_num(data['statements'], 28)
rep_tables = []

if stmt_rep_tables and stmt_rep_tables.get('success'):
    for row in stmt_rep_tables.get('rows', []):
        rep_tables.append([
            row.get('OBJECT_NAME', ''),
            row.get('ROW_COUNT', '0'),
            row.get('SIZE_MB', '0'),
            row.get('COMMENT', '') or ''
        ])
    print(f"  Found {len(rep_tables)} reporting tables")

ws_rep_tables.append(["Reporting Tables (DEV_REPORTING.SECURITY_ANALYTICS)"])
ws_rep_tables.append([])
ws_rep_tables.append(["Table Name", "Row Count", "Size (MB)", "Description"])

for table in sorted(rep_tables, key=lambda x: x[0]):
    ws_rep_tables.append(table)

ws_rep_tables.cell(1, 1).font = Font(bold=True, size=14, color="366092")
style_header(ws_rep_tables, 3, 4)
auto_size_columns(ws_rep_tables)

# ============================================================================
# SHEET 10: Layer 3 - Reporting Views (All parts combined)
# ============================================================================
print("Creating Sheet 10: Layer 3 - Reporting Views...")
ws_rep_views = wb.create_sheet("Layer 3 - Views")

# Find reporting views - statements #30, #32, #34
all_rep_views = []

for stmt_num in [30, 32, 34]:
    stmt = find_statement_by_num(data['statements'], stmt_num)
    if stmt and stmt.get('success'):
        for row in stmt.get('rows', []):
            all_rep_views.append([
                row.get('OBJECT_NAME', ''),
                row.get('COMMENT', '') or ''
            ])

print(f"  Found {len(all_rep_views)} reporting views")

ws_rep_views.append(["Reporting Views (DEV_REPORTING.SECURITY_ANALYTICS)"])
ws_rep_views.append([])
ws_rep_views.append(["View Name", "Description"])

for view in sorted(all_rep_views, key=lambda x: x[0]):
    ws_rep_views.append(view)

ws_rep_views.cell(1, 1).font = Font(bold=True, size=14, color="366092")
style_header(ws_rep_views, 3, 2)
auto_size_columns(ws_rep_views)

# ============================================================================
# SHEET 11: Layer 3 - Reporting Procedures
# ============================================================================
print("Creating Sheet 11: Layer 3 - Reporting Procedures...")
ws_rep_procs = wb.create_sheet("Layer 3 - Procedures")

# Find reporting procedures - statement #36
stmt_rep_procs = find_statement_by_num(data['statements'], 36)
rep_procs = []

if stmt_rep_procs and stmt_rep_procs.get('success'):
    for row in stmt_rep_procs.get('rows', []):
        rep_procs.append([
            row.get('OBJECT_NAME', ''),
            row.get('ARGUMENT_SIGNATURE', ''),
            row.get('PROCEDURE_LANGUAGE', '')
        ])
    print(f"  Found {len(rep_procs)} reporting procedures")

ws_rep_procs.append(["Reporting Procedures (DEV_REPORTING.SECURITY_ANALYTICS)"])
ws_rep_procs.append([])
ws_rep_procs.append(["Procedure Name", "Arguments", "Language"])

for proc in sorted(rep_procs, key=lambda x: x[0]):
    ws_rep_procs.append(proc)

ws_rep_procs.cell(1, 1).font = Font(bold=True, size=14, color="366092")
style_header(ws_rep_procs, 3, 3)
auto_size_columns(ws_rep_procs)

# ============================================================================
# SHEET 12: Key Dimension - DIM_OPCO
# ============================================================================
print("Creating Sheet 12: Key Dimension - DIM_OPCO...")
ws_dim_opco = wb.create_sheet("DIM_OPCO Structure")

# Find DIM_OPCO structure - statement #40
stmt_opco = find_statement_by_num(data['statements'], 40)

ws_dim_opco.append(["DIM_OPCO - Operating Company Dimension"])
ws_dim_opco.append([])
ws_dim_opco.append(["Column Name", "Data Type", "Nullable", "Description"])

if stmt_opco and stmt_opco.get('success'):
    descriptions = {
        'OPCO_ID': 'Primary Key - Unique operating company identifier',
        'OPCO_CODE': 'Short code (e.g., OPCO_001)',
        'OPCO_NAME': 'Full operating company name',
        'REGION': 'Geographic region (North America, Europe, APAC)',
        'DIVISION': 'Business division (IT Security)',
        'COUNTRY': 'Country location',
        'DW_LOAD_DATE': 'Data warehouse load timestamp',
        'DW_UPDATE_DATE': 'Last update timestamp'
    }

    for row in stmt_opco.get('rows', []):
        col_name = row.get('COLUMN_NAME', '')
        ws_dim_opco.append([
            col_name,
            row.get('DATA_TYPE', ''),
            row.get('IS_NULLABLE', ''),
            descriptions.get(col_name, '')
        ])

ws_dim_opco.cell(1, 1).font = Font(bold=True, size=14, color="366092")
style_header(ws_dim_opco, 3, 4)
auto_size_columns(ws_dim_opco)

# ============================================================================
# SHEET 13: Key Dimension - DIM_HOST
# ============================================================================
print("Creating Sheet 13: Key Dimension - DIM_HOST...")
ws_dim_host = wb.create_sheet("DIM_HOST Structure")

# Find DIM_HOST structure - statement #42
stmt_host = find_statement_by_num(data['statements'], 42)

ws_dim_host.append(["DIM_HOST - IT Asset/Host Dimension"])
ws_dim_host.append([])
ws_dim_host.append(["Column Name", "Data Type", "Nullable", "Description"])

if stmt_host and stmt_host.get('success'):
    descriptions = {
        'HOST_KEY': 'Primary Key - Surrogate key for host',
        'HOST_TRACKING_METHOD': 'Method used to track host (IP, DNS, NetBIOS)',
        'HOST_OS': 'Operating system',
        'INSCOPE': 'In scope for security compliance (TRUE/FALSE)',
        'LAST_SCAN_DATE': 'Last vulnerability scan date',
        'DW_LOAD_DATE': 'Data warehouse load timestamp',
        'OPCO_ID': 'Foreign Key to DIM_OPCO',
        'PRIMARY_USER_ID': 'Primary user of this host'
    }

    for row in stmt_host.get('rows', []):
        col_name = row.get('COLUMN_NAME', '')
        ws_dim_host.append([
            col_name,
            row.get('DATA_TYPE', ''),
            row.get('IS_NULLABLE', ''),
            descriptions.get(col_name, '')
        ])

ws_dim_host.cell(1, 1).font = Font(bold=True, size=14, color="366092")
style_header(ws_dim_host, 3, 4)
auto_size_columns(ws_dim_host)

# ============================================================================
# SHEET 14: Key Dimension - DIM_DATES
# ============================================================================
print("Creating Sheet 14: Key Dimension - DIM_DATES...")
ws_dim_dates = wb.create_sheet("DIM_DATES Structure")

# Find DIM_DATES structure - statement #44
stmt_dates = find_statement_by_num(data['statements'], 44)

ws_dim_dates.append(["DIM_DATES - Time Dimension"])
ws_dim_dates.append([])
ws_dim_dates.append(["Column Name", "Data Type", "Nullable", "Description"])

if stmt_dates and stmt_dates.get('success'):
    descriptions = {
        'DATE': 'Primary Key - Date value',
        'DAY_OF_WEEK': 'Day of week number (0-6)',
        'DAY_NAME': 'Day name (Monday-Sunday)',
        'MONTH_NUM': 'Month number (1-12)',
        'MONTH_NAME': 'Month name (January-December)',
        'YEAR': 'Calendar year',
        'QUARTER': 'Calendar quarter (1-4)',
        'WEEK_OF_YEAR': 'Week of year (1-52)'
    }

    for row in stmt_dates.get('rows', []):
        col_name = row.get('COLUMN_NAME', '')
        ws_dim_dates.append([
            col_name,
            row.get('DATA_TYPE', ''),
            row.get('IS_NULLABLE', ''),
            descriptions.get(col_name, '')
        ])

ws_dim_dates.cell(1, 1).font = Font(bold=True, size=14, color="366092")
style_header(ws_dim_dates, 3, 4)
auto_size_columns(ws_dim_dates)

# ============================================================================
# SHEET 15: Key Dimension - DIM_USER
# ============================================================================
print("Creating Sheet 15: Key Dimension - DIM_USER...")
ws_dim_user = wb.create_sheet("DIM_USER Structure")

# Find DIM_USER structure - statement #46
stmt_user = find_statement_by_num(data['statements'], 46)

ws_dim_user.append(["DIM_USER - Unified User Dimension (SCD Type 2)"])
ws_dim_user.append([])
ws_dim_user.append(["Column Name", "Data Type", "Nullable", "Description"])

if stmt_user and stmt_user.get('success'):
    descriptions = {
        'USER_KEY': 'Primary Key - Surrogate key (changes with each version)',
        'USER_ID': 'Natural key - User identifier from source',
        'EMAIL': 'User email address',
        'DISPLAY_NAME': 'Full display name',
        'DEPARTMENT': 'Department/organizational unit',
        'VALID_FROM': 'SCD Type 2 - Valid from date',
        'VALID_TO': 'SCD Type 2 - Valid to date',
        'IS_CURRENT': 'SCD Type 2 - Current version flag'
    }

    for row in stmt_user.get('rows', []):
        col_name = row.get('COLUMN_NAME', '')
        ws_dim_user.append([
            col_name,
            row.get('DATA_TYPE', ''),
            row.get('IS_NULLABLE', ''),
            descriptions.get(col_name, '')
        ])

ws_dim_user.cell(1, 1).font = Font(bold=True, size=14, color="366092")
style_header(ws_dim_user, 3, 4)
auto_size_columns(ws_dim_user)

# ============================================================================
# SHEET 16: Key Fact - FACT_EDR
# ============================================================================
print("Creating Sheet 16: Key Fact - FACT_EDR...")
ws_fact_edr = wb.create_sheet("FACT_EDR Structure")

# Find FACT_EDR structure - statement #48
stmt_edr = find_statement_by_num(data['statements'], 48)

ws_fact_edr.append(["FACT_EDR - Endpoint Detection & Response Metrics"])
ws_fact_edr.append(["Grain: One row per host per EDR platform per day"])
ws_fact_edr.append([])
ws_fact_edr.append(["Column Name", "Data Type", "Nullable", "Description"])

if stmt_edr and stmt_edr.get('success'):
    descriptions = {
        'EDR_KEY': 'Primary Key - Surrogate key',
        'DATE_KEY': 'Foreign Key to DIM_DATES',
        'HOST_ID': 'Foreign Key to DIM_HOST',
        'ENDPOINT_ID': 'Foreign Key to DIM_DEFENDER_ENDPOINTS',
        'EDR_PLATFORM': 'EDR platform (CrowdStrike, Defender, etc.)',
        'AGENT_VERSION': 'EDR agent version',
        'AGENT_STATUS': 'Agent status (Active, Inactive)',
        'LAST_SEEN_DATE': 'Last communication with agent',
        'THREAT_COUNT': 'Number of threats detected',
        'LOAD_TIMESTAMP': 'Load timestamp'
    }

    for row in stmt_edr.get('rows', []):
        col_name = row.get('COLUMN_NAME', '')
        ws_fact_edr.append([
            col_name,
            row.get('DATA_TYPE', ''),
            row.get('IS_NULLABLE', ''),
            descriptions.get(col_name, '')
        ])

ws_fact_edr.cell(1, 1).font = Font(bold=True, size=14, color="366092")
ws_fact_edr.cell(2, 1).font = Font(italic=True, size=10, color="0066CC")
style_header(ws_fact_edr, 4, 4)
auto_size_columns(ws_fact_edr)

# ============================================================================
# SHEET 17: Key Fact - FACT_QUALYS
# ============================================================================
print("Creating Sheet 17: Key Fact - FACT_QUALYS...")
ws_fact_qualys = wb.create_sheet("FACT_QUALYS Structure")

# Find FACT_QUALYS structure - statement #50
stmt_qualys = find_statement_by_num(data['statements'], 50)

ws_fact_qualys.append(["FACT_QUALYS - Vulnerability Scan Facts"])
ws_fact_qualys.append(["Grain: One row per vulnerability per host per scan"])
ws_fact_qualys.append([])
ws_fact_qualys.append(["Column Name", "Data Type", "Nullable", "Description"])

if stmt_qualys and stmt_qualys.get('success'):
    descriptions = {
        'QUALYS_KEY': 'Primary Key - Surrogate key',
        'DATE_KEY': 'Foreign Key to DIM_DATES',
        'HOST_ID': 'Foreign Key to DIM_HOST',
        'QID': 'Foreign Key to DIM_QUALYS_VULNERABILITIES',
        'SEVERITY': 'Vulnerability severity (Critical, High, Medium, Low)',
        'STATUS': 'Vulnerability status',
        'FIRST_DETECTED': 'First detection date',
        'LAST_DETECTED': 'Last detection date',
        'DAYS_OPEN': 'Days vulnerability has been open',
        'REMEDIATION_STATUS': 'Remediation status',
        'REMEDIATION_DATE': 'Date remediated',
        'ASSIGNED_TO': 'Assigned for remediation',
        'CVSS_SCORE': 'CVSS score',
        'CVE_ID': 'CVE identifier',
        'EXPLOITABLE': 'Exploitable flag',
        'PATCH_AVAILABLE': 'Patch availability',
        'LOAD_TIMESTAMP': 'Load timestamp'
    }

    for row in stmt_qualys.get('rows', []):
        col_name = row.get('COLUMN_NAME', '')
        ws_fact_qualys.append([
            col_name,
            row.get('DATA_TYPE', ''),
            row.get('IS_NULLABLE', ''),
            descriptions.get(col_name, '')
        ])

ws_fact_qualys.cell(1, 1).font = Font(bold=True, size=14, color="366092")
ws_fact_qualys.cell(2, 1).font = Font(italic=True, size=10, color="0066CC")
style_header(ws_fact_qualys, 4, 4)
auto_size_columns(ws_fact_qualys)

# ============================================================================
# SHEET 18: Primary Keys
# ============================================================================
print("Creating Sheet 18: Primary Keys...")
ws_pks = wb.create_sheet("Primary Keys")

# Find PKs - statement #52
stmt_pks = find_statement_by_num(data['statements'], 52)
pks = []

if stmt_pks and stmt_pks.get('success'):
    for row in stmt_pks.get('rows', []):
        pks.append([
            row.get('TABLE_NAME', ''),
            row.get('PK_NAME', '')
        ])
    print(f"  Found {len(pks)} primary keys")

ws_pks.append(["Primary Keys (DEV_TRANSFORMATION.SECURITY_ANALYTICS)"])
ws_pks.append([])
ws_pks.append(["Table Name", "Constraint Name"])

for pk in sorted(pks, key=lambda x: x[0]):
    ws_pks.append(pk)

ws_pks.cell(1, 1).font = Font(bold=True, size=14, color="366092")
style_header(ws_pks, 3, 2)
auto_size_columns(ws_pks)

# ============================================================================
# SHEET 19: Foreign Keys
# ============================================================================
print("Creating Sheet 19: Foreign Keys...")
ws_fks = wb.create_sheet("Foreign Keys")

# Find FKs - statement #54
stmt_fks = find_statement_by_num(data['statements'], 54)
fks = []

if stmt_fks and stmt_fks.get('success'):
    for row in stmt_fks.get('rows', []):
        fks.append([
            row.get('TABLE_NAME', ''),
            row.get('FK_NAME', '')
        ])
    print(f"  Found {len(fks)} foreign keys")

ws_fks.append(["Foreign Keys (DEV_TRANSFORMATION.SECURITY_ANALYTICS)"])
ws_fks.append([])
ws_fks.append(["Table Name", "Constraint Name"])

for fk in sorted(fks, key=lambda x: x[0]):
    ws_fks.append(fk)

ws_fks.cell(1, 1).font = Font(bold=True, size=14, color="366092")
style_header(ws_fks, 3, 2)
auto_size_columns(ws_fks)

# ============================================================================
# SHEET 20: Data Lineage
# ============================================================================
print("Creating Sheet 20: Data Lineage...")
ws_lineage = wb.create_sheet("Data Lineage")

ws_lineage.append(["Data Lineage Catalog - Cross-Layer Data Flow"])
ws_lineage.append([])
ws_lineage.append(["Source DB", "Source Schema", "Source Table", "Target DB", "Target Schema", "Target Table", "Transformation Logic", "Update Frequency"])

# Key lineage flows documented
lineage_data = [
    ["DEV_LANDING", "SECURITY_ANALYTICS", "L_CROWDSTRIKE_HOSTS", "DEV_TRANSFORMATION", "SECURITY_ANALYTICS", "DIM_HOST", "Merge CrowdStrike endpoints", "Daily"],
    ["DEV_LANDING", "SECURITY_ANALYTICS", "L_QUALYS_SCANS", "DEV_TRANSFORMATION", "SECURITY_ANALYTICS", "DIM_QUALYS_VULNERABILITIES", "Parse vulnerability data", "Daily"],
    ["DEV_LANDING", "SECURITY_ANALYTICS", "AD_COMPUTERS_*", "DEV_TRANSFORMATION", "SECURITY_ANALYTICS", "DIM_USER", "SCD Type 2 merge from AD", "Daily"],
    ["DEV_LANDING", "SECURITY_ANALYTICS", "L_PAM_USERS", "DEV_TRANSFORMATION", "SECURITY_ANALYTICS", "DIM_USER", "SCD Type 2 merge from PAM", "Daily"],
    ["DEV_LANDING", "SECURITY_ANALYTICS", "L_EDR_THREATS_REALTIME", "DEV_TRANSFORMATION", "SECURITY_ANALYTICS", "FACT_EDR", "Aggregate threat counts by host", "Real-time (Snowpipe)"],
    ["DEV_LANDING", "SECURITY_ANALYTICS", "L_CRITICAL_VULNS_REALTIME", "DEV_TRANSFORMATION", "SECURITY_ANALYTICS", "FACT_QUALYS", "Parse critical vulnerabilities", "Real-time (Snowpipe)"],
    ["DEV_TRANSFORMATION", "SECURITY_ANALYTICS", "DIM_HOST", "DEV_REPORTING", "SECURITY_ANALYTICS", "VW_POWERBI_EXECUTIVE_DASHBOARD", "Join with facts for KPIs", "On-demand"],
    ["DEV_TRANSFORMATION", "SECURITY_ANALYTICS", "DIM_OPCO", "DEV_REPORTING", "SECURITY_ANALYTICS", "VW_SECURITY_POSTURE_SUMMARY", "Aggregate by OpCo", "On-demand"],
    ["DEV_TRANSFORMATION", "SECURITY_ANALYTICS", "FACT_EDR", "DEV_REPORTING", "SECURITY_ANALYTICS", "VW_EXECUTIVE_KPI_DASHBOARD", "Calculate threat percentages", "On-demand"],
    ["DEV_TRANSFORMATION", "SECURITY_ANALYTICS", "FACT_QUALYS", "DEV_REPORTING", "SECURITY_ANALYTICS", "VW_VULNERABILITY_TRENDS", "Trend analysis over time", "On-demand"],
]

for row in lineage_data:
    ws_lineage.append(row)

ws_lineage.cell(1, 1).font = Font(bold=True, size=14, color="366092")
style_header(ws_lineage, 3, 8)
auto_size_columns(ws_lineage, max_width=50)

# Save workbook
output_file = f'ITSECKPI_ERD_Documentation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
wb.save(output_file)

print(f"\n" + "="*60)
print(f"SUCCESS: Excel file created: {output_file}")
print("="*60)
print(f"\nSheets created ({len(wb.sheetnames)}):")
for i, sheet_name in enumerate(wb.sheetnames, 1):
    print(f"  {i:2}. {sheet_name}")

print(f"\nSummary:")
print(f"  - Landing Tables: {len(landing_tables)}")
print(f"  - Landing Views: {len(landing_views)}")
print(f"  - Dimensions: {len(dimensions)}")
print(f"  - Facts: {len(facts)}")
print(f"  - Other Tables: {len(other_tables)}")
print(f"  - Transformation Views: {len(trans_views)}")
print(f"  - Transformation Procedures: {len(procedures)}")
print(f"  - Reporting Tables: {len(rep_tables)}")
print(f"  - Reporting Views: {len(all_rep_views)}")
print(f"  - Reporting Procedures: {len(rep_procs)}")
print(f"  - Primary Keys: {len(pks)}")
print(f"  - Foreign Keys: {len(fks)}")
print(f"\nFile saved successfully!")
