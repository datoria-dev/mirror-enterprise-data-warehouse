"""
Script to add Metadata tab to existing Streamlit apps

This script automatically adds a metadata browsing tab to Streamlit apps,
allowing users to explore table and column metadata from the Metadata Repository.

Usage:
    python add_metadata_tab.py

Date: 2025-10-24
"""

import os
import re
import sys
import io

# Fix encoding issues for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Services to update (those with exported metadata)
SERVICES = {
    'CybelAngel': 'CYBELANGEL_COLUMNS_EXPORT',
    'Proofpoint': 'PROOFPOINT_COLUMNS_EXPORT',
    'ServiceNow': 'SERVICENOW_COLUMNS_EXPORT',
    'Leviat': 'LEVIAT_COLUMNS_EXPORT',
    'Tenable': 'TENABLE_COLUMNS_EXPORT'
}

METADATA_TAB_TEMPLATE = '''
# ---------------------------------------------------------------------------
# TAB {tab_num}: METADATA
# ---------------------------------------------------------------------------

with tab{tab_num}:
    st.subheader("📚 {service} Data Catalog")

    st.info("""
    This metadata is automatically extracted from the **Metadata Repository** and shows all available tables and columns for {service} data.
    Use this reference to understand data structure, column names, and data types.
    """)

    # Query metadata from METADATA_EXPORTS schema
    metadata_sql = """
        SELECT
            TABLE_NAME,
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE,
            ORDINAL_POSITION,
            FULL_TABLE_NAME
        FROM DEV_TRANSFORMATION.METADATA_EXPORTS.{export_table}
        ORDER BY TABLE_NAME, ORDINAL_POSITION
    """

    metadata = safe_query(metadata_sql, "Failed to load metadata")

    if not metadata.empty:
        # Get unique tables
        tables = metadata['TABLE_NAME'].unique()

        # Table selector
        selected_table = st.selectbox(
            "📋 Select Table",
            options=["All Tables"] + list(tables),
            help="Choose a table to view its columns"
        )

        # Filter by selected table
        if selected_table != "All Tables":
            filtered_metadata = metadata[metadata['TABLE_NAME'] == selected_table]

            st.subheader(f"Columns in {{selected_table}}")

            # Show table details
            table_info = filtered_metadata.iloc[0]
            st.code(table_info['FULL_TABLE_NAME'], language='sql')

            # Column count
            col_count = len(filtered_metadata)
            st.metric("Total Columns", col_count)

            st.markdown("---")

            # Display columns with enhanced formatting
            for idx, row in filtered_metadata.iterrows():
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

                with col1:
                    st.markdown(f"**{{row['COLUMN_NAME']}}**")
                with col2:
                    st.markdown(f"`{{row['DATA_TYPE']}}`")
                with col3:
                    nullable_icon = "✅" if row['IS_NULLABLE'] == 'YES' else "❌"
                    st.markdown(f"Nullable: {{nullable_icon}}")
                with col4:
                    st.markdown(f"Position: {{row['ORDINAL_POSITION']}}")

        else:
            # Show summary of all tables
            st.subheader("All {service} Tables")

            # Group by table
            table_summary = metadata.groupby(['TABLE_NAME', 'FULL_TABLE_NAME']).agg(
                COLUMN_COUNT=('COLUMN_NAME', 'count')
            ).reset_index()

            # Display table cards
            for idx, table in table_summary.iterrows():
                with st.expander(f"📊 {{table['TABLE_NAME']}} ({{table['COLUMN_COUNT']}} columns)"):
                    st.code(table['FULL_TABLE_NAME'], language='sql')

                    # Get columns for this table
                    table_columns = metadata[metadata['TABLE_NAME'] == table['TABLE_NAME']]

                    # Create a clean dataframe for display
                    display_df = table_columns[['COLUMN_NAME', 'DATA_TYPE', 'IS_NULLABLE', 'ORDINAL_POSITION']].copy()
                    display_df.columns = ['Column Name', 'Data Type', 'Nullable', 'Position']

                    st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Search functionality
        st.subheader("🔍 Search Columns")
        search_term = st.text_input("Search for a column name", "")

        if search_term:
            search_results = metadata[
                metadata['COLUMN_NAME'].str.contains(search_term, case=False, na=False)
            ]

            if not search_results.empty:
                st.success(f"Found {{len(search_results)}} columns matching '{{search_term}}'")

                # Display search results
                display_search = search_results[['TABLE_NAME', 'COLUMN_NAME', 'DATA_TYPE', 'FULL_TABLE_NAME']].copy()
                display_search.columns = ['Table', 'Column', 'Data Type', 'Full Table Name']

                st.dataframe(display_search, use_container_width=True, hide_index=True)

                # Export search results
                export_csv(search_results, f"{service_lower}_metadata_search_{{search_term}}")
            else:
                st.warning(f"No columns found matching '{{search_term}}'")

        # Export all metadata
        st.markdown("---")
        export_csv(metadata, "{service_lower}_complete_metadata")

    else:
        st.error("❌ Metadata not available. Please ensure METADATA_EXPORTS.{export_table} table exists.")
        st.info("""
        **How to generate metadata:**
        1. Run the metadata repository script: `EXPORT_METADATA_RESULTS.sql`
        2. This will create the {export_table} table
        3. Refresh this dashboard
        """)
'''

def add_metadata_tab_to_app(service_dir, service_name, export_table):
    """Add metadata tab to a Streamlit app"""

    app_file = os.path.join(service_dir, 'streamlit_app.py')

    if not os.path.exists(app_file):
        print(f"❌ App file not found: {app_file}")
        return False

    # Read the file
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if metadata tab already exists
    if '"📚 Metadata"' in content or "'📚 Metadata'" in content:
        print(f"⚠️  {service_name}: Metadata tab already exists, skipping")
        return False

    # Find the tab layout line
    tab_pattern = r'(tab\d+(?:,\s*tab\d+)*)\s*=\s*st\.tabs\(\[(.*?)\]\)'
    match = re.search(tab_pattern, content, re.DOTALL)

    if not match:
        print(f"❌ {service_name}: Could not find tab layout")
        return False

    old_tabs = match.group(1)
    tab_names = match.group(2)

    # Count existing tabs
    tab_count = len(old_tabs.split(','))
    new_tab_num = tab_count + 1

    # Create new tab variable name
    new_tabs = old_tabs + f", tab{new_tab_num}"
    new_tab_names = tab_names + ',\n    "📚 Metadata"'

    # Replace tab layout
    old_line = f"{old_tabs} = st.tabs([{tab_names}])"
    new_line = f"{new_tabs} = st.tabs([{new_tab_names}])"

    content = content.replace(old_line, new_line)

    # Find the FOOTER section
    footer_pattern = r'(# ={70,}\n# FOOTER\n# ={70,})'
    footer_match = re.search(footer_pattern, content)

    if not footer_match:
        print(f"❌ {service_name}: Could not find FOOTER section")
        return False

    # Generate metadata tab code
    service_lower = service_name.lower()
    metadata_code = METADATA_TAB_TEMPLATE.format(
        tab_num=new_tab_num,
        service=service_name,
        export_table=export_table,
        service_lower=service_lower
    )

    # Insert before FOOTER
    footer_start = footer_match.start()
    content = content[:footer_start] + metadata_code + '\n' + content[footer_start:]

    # Write back to file
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ {service_name}: Metadata tab added successfully")
    return True

def main():
    """Main function to update all apps"""

    print("=" * 80)
    print("Adding Metadata Tab to Streamlit Apps")
    print("=" * 80)
    print()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    updated_count = 0

    for service_name, export_table in SERVICES.items():
        service_dir = os.path.join(base_dir, service_name)

        if not os.path.exists(service_dir):
            print(f"⚠️  {service_name}: Directory not found, skipping")
            continue

        if add_metadata_tab_to_app(service_dir, service_name, export_table):
            updated_count += 1

    print()
    print("=" * 80)
    print(f"Summary: Updated {updated_count}/{len(SERVICES)} apps")
    print("=" * 80)

    if updated_count > 0:
        print("\n✅ Metadata tabs successfully added!")
        print("\n📋 Next steps:")
        print("   1. Review the updated apps")
        print("   2. Test the Metadata tab in each app")
        print("   3. Ensure METADATA_EXPORTS tables exist in Snowflake")
    else:
        print("\n⚠️  No apps were updated. Check if they already have Metadata tabs.")

if __name__ == "__main__":
    main()
