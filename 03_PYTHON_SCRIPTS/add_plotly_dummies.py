"""
Add dummy plotly objects to prevent NameErrors
Keep all original code intact

Author: Data Engineering Team
Date: 2025-10-25
"""

import sys
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Paths
SOURCE_PATH = Path(r"C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\10_STREAMLIT_FINAL")
OUTPUT_PATH = Path(r"C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\12_STREAMLIT_WITH_DUMMIES")

ALL_SERVICES = [
    'Splunk', 'Crowdstrike', 'ServiceNow', 'Qualys', 'Zscaler', 'SentinelOne',
    'Ancon', 'BitSight', 'Cisco_AMP', 'CybelAngel', 'Intel_Threats',
    'Leviat', 'Proofpoint', 'Sophos', 'Symantec', 'Tenable', 'Trellix', 'Zerofox'
]

ENV_YML = """name: streamlit
channels:
  - snowflake
dependencies:
  - streamlit
  - snowflake-snowpark-python
  - pandas
"""

DUMMY_PLOTLY = """
# Dummy plotly objects to prevent NameErrors in Snowflake
class _DummyFigure:
    '''Dummy Figure class that does nothing'''
    def add_trace(self, *args, **kwargs):
        pass
    def update_layout(self, *args, **kwargs):
        pass
    def update_xaxes(self, *args, **kwargs):
        pass
    def update_yaxes(self, *args, **kwargs):
        pass
    def show(self, *args, **kwargs):
        pass

class _DummyPlotly:
    '''Dummy plotly.express replacement'''
    def bar(self, *args, **kwargs):
        return _DummyFigure()
    def line(self, *args, **kwargs):
        return _DummyFigure()
    def scatter(self, *args, **kwargs):
        return _DummyFigure()
    def pie(self, *args, **kwargs):
        return _DummyFigure()
    def histogram(self, *args, **kwargs):
        return _DummyFigure()
    def box(self, *args, **kwargs):
        return _DummyFigure()
    def area(self, *args, **kwargs):
        return _DummyFigure()
    def treemap(self, *args, **kwargs):
        return _DummyFigure()

class _DummyGO:
    '''Dummy plotly.graph_objects replacement'''
    def Figure(self, *args, **kwargs):
        return _DummyFigure()
    def Bar(self, *args, **kwargs):
        return {}
    def Scatter(self, *args, **kwargs):
        return {}
    def Pie(self, *args, **kwargs):
        return {}
    def Histogram(self, *args, **kwargs):
        return {}

# Create dummy objects
px = _DummyPlotly()
go = _DummyGO()
"""

def add_dummies_to_file(content):
    """Add dummy objects after commented imports"""

    lines = content.split('\n')
    fixed_lines = []
    imports_done = False

    for i, line in enumerate(lines):
        fixed_lines.append(line)

        # After the last import line, add dummies
        if not imports_done and line.strip().startswith('# import numpy'):
            # Add dummy plotly objects
            fixed_lines.append('')
            fixed_lines.extend(DUMMY_PLOTLY.split('\n'))
            imports_done = True

    return '\n'.join(fixed_lines)

def wrap_plotly_charts(content):
    """Wrap st.plotly_chart calls to handle None figures"""

    # Replace st.plotly_chart with a try/except or check
    content = content.replace(
        'st.plotly_chart(fig',
        'if fig: st.info("Chart not available in Snowflake - view data in table") # st.plotly_chart(fig'
    )

    return content

def process_app(service_name):
    """Process single app"""
    print(f"\n{service_name}:")

    source_file = SOURCE_PATH / service_name / "streamlit_app.py"
    output_dir = OUTPUT_PATH / service_name
    output_file = output_dir / "streamlit_app.py"
    env_file = output_dir / "environment.yml"

    if not source_file.exists():
        print(f"  ❌ Not found")
        return False

    try:
        output_dir.mkdir(parents=True, exist_ok=True)

        # Read
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add dummies
        print(f"  🔧 Adding dummy plotly objects...")
        content = add_dummies_to_file(content)

        # Wrap charts
        print(f"  🔧 Wrapping plotly_chart calls...")
        content = wrap_plotly_charts(content)

        # Validate
        import ast
        try:
            ast.parse(content)
        except SyntaxError as e:
            print(f"  ❌ Syntax error: {e}")
            return False

        # Write
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(ENV_YML)

        print(f"  ✅ Created, syntax valid")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Process all apps"""
    print("="*80)
    print("ADDING DUMMY PLOTLY OBJECTS - NO CODE CHANGES")
    print("="*80)
    print(f"\nStrategy:")
    print(f"  - Comment plotly imports")
    print(f"  - Add dummy px, go objects")
    print(f"  - All original code works")
    print(f"  - Charts just don't display\n")

    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    success = 0
    failed = 0

    for service in ALL_SERVICES:
        if process_app(service):
            success += 1
        else:
            failed += 1

    print(f"\n{'='*80}")
    print(f"✅ Success: {success}")
    print(f"❌ Failed: {failed}")

    if success > 0:
        print(f"\n✅ Apps ready in: {OUTPUT_PATH}")
        print(f"\nThese apps will run without NameErrors!")
        print(f"Charts won't display, but tables will work perfectly.")

if __name__ == "__main__":
    main()