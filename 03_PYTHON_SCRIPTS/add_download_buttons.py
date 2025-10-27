"""
Add download buttons after important dataframes in Streamlit apps
"""
import os
import re
import sys
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def add_download_button(content, app_name):
    """Add download buttons after st.dataframe() calls"""
    lines = content.split('\n')
    new_lines = []
    i = 0
    buttons_added = 0

    while i < len(lines):
        line = lines[i]
        new_lines.append(line)

        # Check if this is a st.dataframe() call
        if 'st.dataframe(' in line and 'use_container_width=True' in line:
            # Check if download button already exists
            if i + 1 < len(lines) and 'st.download_button' in lines[i + 1]:
                i += 1
                continue

            # Try to extract dataframe variable name
            df_match = re.search(r'st\.dataframe\(\s*([a-zA-Z_][a-zA-Z0-9_]*)', line)
            if df_match:
                df_name = df_match.group(1)

                # Determine indentation
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent

                # Add download button code
                download_code = [
                    f"{indent_str}# Download button",
                    f"{indent_str}csv_data = {df_name}.to_csv(index=False).encode('utf-8')",
                    f"{indent_str}st.download_button(",
                    f"{indent_str}    label=\"📥 Download CSV\",",
                    f"{indent_str}    data=csv_data,",
                    f"{indent_str}    file_name=f\"{app_name.lower()}_data_{{datetime.now().strftime('%Y%m%d_%H%M')}}.csv\",",
                    f"{indent_str}    mime=\"text/csv\",",
                    f"{indent_str}    use_container_width=True",
                    f"{indent_str})"
                ]

                new_lines.extend(download_code)
                buttons_added += 1

        i += 1

    return '\n'.join(new_lines), buttons_added

def add_datetime_import(content):
    """Add datetime import if not present"""
    if 'from datetime import datetime' in content:
        return content

    # Add after other imports
    lines = content.split('\n')
    import_idx = 0

    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            import_idx = i

    lines.insert(import_idx + 1, 'from datetime import datetime')
    return '\n'.join(lines)

def process_app(app_path, app_name):
    """Process a single Streamlit app"""
    try:
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add datetime import
        content = add_datetime_import(content)

        # Add download buttons
        new_content, buttons_added = add_download_button(content, app_name)

        if buttons_added > 0:
            with open(app_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ {app_name}: Added {buttons_added} download buttons")
            return True, buttons_added
        else:
            print(f"⚠️  {app_name}: No dataframes found to add buttons")
            return False, 0

    except Exception as e:
        print(f"❌ {app_name}: Error - {str(e)}")
        return False, 0

def main():
    """Process all Streamlit apps"""
    base_dir = "13_STREAMLIT_COMPLETE"

    services = [
        "Ancon", "BitSight", "Cisco_AMP", "Crowdstrike", "CybelAngel",
        "Intel_Threats", "Leviat", "Proofpoint", "Qualys", "SentinelOne",
        "ServiceNow", "Sophos", "Splunk", "Symantec", "Tenable",
        "Trellix", "Zerofox", "Zscaler"
    ]

    total_apps = 0
    total_buttons = 0

    print("=" * 60)
    print("Adding Download Buttons to Streamlit Apps")
    print("=" * 60)

    for service in services:
        app_path = os.path.join(base_dir, service, "streamlit_app.py")
        if os.path.exists(app_path):
            success, buttons = process_app(app_path, service)
            if success:
                total_apps += 1
                total_buttons += buttons

    print("=" * 60)
    print(f"✅ Summary: Added {total_buttons} download buttons to {total_apps} apps")
    print("=" * 60)

if __name__ == "__main__":
    main()
