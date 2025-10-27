"""
Fix download buttons using @st.cache_data pattern and simplified filenames
This addresses Snowflake Streamlit compatibility issues
"""
import os
import re
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def fix_download_button(content):
    """
    Replace:
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(..., file_name=f"...{datetime.now()}...")

    With:
        @st.cache_data
        def convert_to_csv(df):
            return df.to_csv(index=False).encode('utf-8')
        csv_data = convert_to_csv(df)
        st.download_button(..., file_name="simple_name.csv")
    """
    lines = content.split('\n')
    new_lines = []
    fixed_count = 0
    i = 0

    while i < len(lines):
        line = lines[i]

        # Pattern: csv_data = something.to_csv(index=False).encode('utf-8')
        if 'csv_data' in line and '.to_csv(index=False)' in line and '@st.cache_data' not in ''.join(lines[max(0,i-2):i]):
            # Extract the dataframe expression
            match = re.search(r'csv_data\s*=\s*(.+?)\.to_csv\(index=False\)\.encode', line)
            if match:
                df_expr = match.group(1).strip()
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent

                # Generate unique function name
                func_name = f"convert_to_csv_{fixed_count}"

                # Insert cached function
                new_lines.append(f"{indent_str}@st.cache_data")
                new_lines.append(f"{indent_str}def {func_name}(df):")
                new_lines.append(f"{indent_str}    return df.to_csv(index=False).encode('utf-8')")
                new_lines.append("")
                new_lines.append(f"{indent_str}csv_data = {func_name}({df_expr})")

                fixed_count += 1
                i += 1
                continue

        # Pattern: file_name=f"...{datetime.now()}..."
        if 'file_name=' in line and 'datetime.now()' in line:
            # Simplify to static filename
            # Extract service name if present
            match = re.search(r'file_name=f?"([^_]+)_.*?"', line)
            if match:
                service = match.group(1)
                # Replace with simple static name
                new_line = re.sub(
                    r'file_name=f?"[^"]+datetime\.now\(\)[^"]*"',
                    f'file_name="{service}_data.csv"',
                    line
                )
                new_lines.append(new_line)
                i += 1
                continue

        new_lines.append(line)
        i += 1

    return '\n'.join(new_lines), fixed_count

def process_app(app_path, app_name):
    """Process a single Streamlit app"""
    try:
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Fix download buttons
        new_content, fixed = fix_download_button(content)

        if fixed > 0:
            with open(app_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ {app_name}: Fixed {fixed} download button(s)")
            return True, fixed
        else:
            print(f"⚠️  {app_name}: No download buttons needed fixing")
            return False, 0

    except Exception as e:
        print(f"❌ {app_name}: Error - {str(e)}")
        return False, 0

def main():
    """Process all Streamlit apps with download buttons"""
    base_dir = "13_STREAMLIT_COMPLETE"

    services = [
        "Ancon", "Crowdstrike", "CybelAngel", "Leviat", "Proofpoint",
        "SentinelOne", "ServiceNow", "Sophos", "Splunk", "Zscaler"
    ]

    total_apps = 0
    total_fixes = 0

    print("=" * 60)
    print("Fixing Download Buttons with @st.cache_data Pattern")
    print("=" * 60)

    for service in services:
        app_path = os.path.join(base_dir, service, "streamlit_app.py")
        if os.path.exists(app_path):
            success, fixes = process_app(app_path, service)
            if success:
                total_apps += 1
                total_fixes += fixes

    print("=" * 60)
    print(f"✅ Summary: Fixed {total_fixes} buttons in {total_apps} apps")
    print("=" * 60)

if __name__ == "__main__":
    main()
