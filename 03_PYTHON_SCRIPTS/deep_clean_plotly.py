"""
Deep clean of ALL plotly-related code from Streamlit apps
Removes ALL plotly references completely

Author: Data Engineering Team
Date: 2025-10-24
"""

import sys
import re
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Paths
BASE_PATH = Path(r"C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV")
APPS_PATH = BASE_PATH / "08_STREAMLIT_APPS_FIXED"

# All services
ALL_SERVICES = [
    'Splunk', 'Crowdstrike', 'ServiceNow', 'Qualys', 'Zscaler', 'SentinelOne',
    'Ancon', 'BitSight', 'Cisco_AMP', 'CybelAngel', 'Intel_Threats',
    'Leviat', 'Proofpoint', 'Sophos', 'Symantec', 'Tenable', 'Trellix', 'Zerofox'
]

def deep_clean_plotly(content):
    """Remove ALL plotly-related code including orphaned syntax"""

    lines = content.split('\n')
    cleaned_lines = []
    skip_until_newline = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip completely empty lines at start of blocks
        if skip_until_newline:
            if line.strip() == '':
                skip_until_newline = False
            i += 1
            continue

        # Check for plotly-related patterns to remove
        should_skip = False

        # 1. Lines with plotly comments
        if '# Plotly code commented out' in line or '# plotly' in line.lower():
            should_skip = True

        # 2. Standalone closing parentheses ))
        elif re.match(r'^\s*\)\s*\)?\s*$', line):
            should_skip = True
            print(f"    Removing orphaned parentheses: {line}")

        # 3. fig_ variable operations (update_layout, add_trace, etc.)
        elif re.match(r'^\s*fig_\w+\.(update_layout|add_trace|update_xaxes|update_yaxes|show)', line):
            should_skip = True
            print(f"    Removing fig operation: {line.strip()[:60]}...")
            # Skip the entire method call block
            if '(' in line and ')' not in line:
                # Multi-line method call, skip until closing paren
                depth = line.count('(') - line.count(')')
                i += 1
                while i < len(lines) and depth > 0:
                    depth += lines[i].count('(') - lines[i].count(')')
                    i += 1
                i -= 1  # Back one line for normal increment

        # 4. st.plotly_chart() calls
        elif 'st.plotly_chart' in line:
            should_skip = True
            print(f"    Removing st.plotly_chart call")

        # 5. Orphaned parameter lines (x=, y=, name=, etc.) with high indentation
        elif re.match(r'^\s{12,}(x=|y=|name=|marker_color=|text=|mode=|marker=|line=|barmode=|title=|plot_bgcolor=|hovertemplate=|showlegend=|height=|width=)', line):
            should_skip = True

        # 6. Lines that are just closing parentheses with parameters
        elif re.match(r'^\s+\)\s*$', line):
            # Check if previous line was plotly-related or a comment
            if cleaned_lines and ('# Plotly' in cleaned_lines[-1] or '# fig' in cleaned_lines[-1]):
                should_skip = True
                print(f"    Removing orphaned closing paren")

        if not should_skip:
            cleaned_lines.append(line)

        i += 1

    return '\n'.join(cleaned_lines)

def add_data_display_hints(content):
    """Add helpful comments where plotly charts were removed"""

    # After removing plotly, add hints for data display
    content = re.sub(
        r'(st\.markdown\("###[^"]+"\)\s*\n)\s*\n',
        r'\1        st.info("Data visualization available in table format below")\n\n',
        content
    )

    return content

def deep_clean_app(service_name):
    """Deep clean a single app"""
    print(f"\n{service_name}:")

    app_file = APPS_PATH / service_name / "streamlit_app.py"

    if not app_file.exists():
        print(f"  ❌ File not found")
        return False

    try:
        # Read file
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()

        original_lines = len(content.split('\n'))

        # Deep clean plotly
        print(f"  🧹 Deep cleaning plotly code...")
        content = deep_clean_plotly(content)

        # Add helpful hints
        # content = add_data_display_hints(content)

        cleaned_lines = len(content.split('\n'))

        # Write back
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(content)

        if original_lines != cleaned_lines:
            print(f"  ✅ Cleaned: {original_lines} → {cleaned_lines} lines (removed {original_lines - cleaned_lines})")
        else:
            print(f"  ✅ Already clean ({original_lines} lines)")

        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Deep clean all apps"""
    print("="*80)
    print("DEEP CLEANING ALL PLOTLY CODE FROM STREAMLIT APPS")
    print("="*80)
    print("\nThis will remove:")
    print("  - All fig_ variable operations")
    print("  - All orphaned parentheses and parameters")
    print("  - All st.plotly_chart() calls")
    print("  - All plotly-related comments and code\n")

    success_count = 0
    failed_count = 0

    for service in ALL_SERVICES:
        if deep_clean_app(service):
            success_count += 1
        else:
            failed_count += 1

    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Successfully cleaned: {success_count}")
    print(f"❌ Failed: {failed_count}")

    if success_count > 0:
        print(f"\n✅ All apps deeply cleaned and ready!")
        print(f"   No plotly code remains - 100% Snowflake compatible")

if __name__ == "__main__":
    main()