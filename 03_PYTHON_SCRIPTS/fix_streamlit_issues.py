"""
Fix 2 critical issues in Streamlit apps:
1. Replace st.experimental_rerun() with st.rerun()
2. Add unique keys to st.download_button()
"""
import os
import re
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def fix_experimental_rerun(content):
    """Replace st.experimental_rerun() with st.rerun()"""
    count = content.count('st.experimental_rerun()')
    content = content.replace(
        'st.experimental_rerun()',
        'st.rerun()'
    )
    # Also update comments
    content = content.replace(
        'experimental_rerun for Snowflake compatibility',
        'Streamlit 1.28+ uses st.rerun()'
    )
    return content, count

def fix_download_button_keys(content, app_name):
    """Add unique keys to download buttons"""
    lines = content.split('\n')
    new_lines = []
    fixed_count = 0
    button_counter = 0

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this is a st.download_button( call
        if 'st.download_button(' in line:
            # Check if it already has a key parameter
            # Look ahead to find the closing parenthesis
            button_block = [line]
            j = i + 1
            paren_count = line.count('(') - line.count(')')

            while j < len(lines) and paren_count > 0:
                button_block.append(lines[j])
                paren_count += lines[j].count('(') - lines[j].count(')')
                j += 1

            # Check if 'key=' is in the button block
            button_text = '\n'.join(button_block)

            if 'key=' not in button_text:
                # Need to add key parameter
                # Find the closing parenthesis line
                closing_line_idx = j - 1
                closing_line = lines[closing_line_idx]

                # Get indentation
                indent = len(closing_line) - len(closing_line.lstrip())
                indent_str = ' ' * indent

                # Generate unique key
                button_counter += 1
                key_name = f"download_{app_name.lower()}_{button_counter}"

                # Insert key parameter before closing parenthesis
                if closing_line.strip() == ')':
                    # Add key on previous line
                    new_lines.extend(button_block[:-1])
                    # Add comma to last parameter if needed
                    if not new_lines[-1].rstrip().endswith(','):
                        new_lines[-1] = new_lines[-1].rstrip() + ','
                    new_lines.append(f'{indent_str}    key="{key_name}"')
                    new_lines.append(closing_line)
                else:
                    # Closing paren is on same line as last param
                    modified_line = closing_line.replace(')', f', key="{key_name}")')
                    new_lines.extend(button_block[:-1])
                    new_lines.append(modified_line)

                fixed_count += 1
                i = j
                continue

        new_lines.append(line)
        i += 1

    return '\n'.join(new_lines), fixed_count

def process_app(app_path, app_name):
    """Process a single Streamlit app"""
    try:
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()

        total_fixes = 0

        # Fix 1: experimental_rerun
        content, rerun_fixes = fix_experimental_rerun(content)
        total_fixes += rerun_fixes

        # Fix 2: download button keys
        content, key_fixes = fix_download_button_keys(content, app_name)
        total_fixes += key_fixes

        if total_fixes > 0:
            with open(app_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ {app_name}: Fixed {rerun_fixes} rerun() + {key_fixes} download keys")
            return True, rerun_fixes, key_fixes
        else:
            print(f"⚠️  {app_name}: No fixes needed")
            return False, 0, 0

    except Exception as e:
        print(f"❌ {app_name}: Error - {str(e)}")
        return False, 0, 0

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
    total_rerun = 0
    total_keys = 0

    print("=" * 60)
    print("Fixing Streamlit Issues: st.rerun() + download keys")
    print("=" * 60)

    for service in services:
        app_path = os.path.join(base_dir, service, "streamlit_app.py")
        if os.path.exists(app_path):
            success, rerun, keys = process_app(app_path, service)
            if success:
                total_apps += 1
                total_rerun += rerun
                total_keys += keys

    print("=" * 60)
    print(f"✅ Summary: Fixed {total_apps} apps")
    print(f"   - st.rerun() fixes: {total_rerun}")
    print(f"   - Download key fixes: {total_keys}")
    print("=" * 60)

if __name__ == "__main__":
    main()
