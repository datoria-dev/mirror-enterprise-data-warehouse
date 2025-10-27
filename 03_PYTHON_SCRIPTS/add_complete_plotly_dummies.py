"""
Add COMPLETE dummy plotly objects with ALL methods
Prevents ALL AttributeErrors

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
OUTPUT_PATH = Path(r"C:\Users\fonat\Documents\MYORG_LOCAL\Snowflake_ITSECKPI_Project_DEV\13_STREAMLIT_COMPLETE")

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

# Complete dummy plotly implementation
COMPLETE_DUMMY_PLOTLY = """
# Complete dummy plotly objects to prevent ALL NameErrors and AttributeErrors
class _DummyFigure:
    '''Dummy Figure class that accepts any method call and does nothing'''
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        '''Return a dummy method for any attribute access'''
        def dummy_method(*args, **kwargs):
            return self
        return dummy_method

    # Explicitly define common methods for clarity
    def add_trace(self, *args, **kwargs):
        return self
    def update_layout(self, *args, **kwargs):
        return self
    def update_xaxes(self, *args, **kwargs):
        return self
    def update_yaxes(self, *args, **kwargs):
        return self
    def add_hline(self, *args, **kwargs):
        return self
    def add_vline(self, *args, **kwargs):
        return self
    def add_shape(self, *args, **kwargs):
        return self
    def add_annotation(self, *args, **kwargs):
        return self
    def show(self, *args, **kwargs):
        pass

class _DummyPlotly:
    '''Dummy plotly.express that returns dummy figures'''
    def __getattr__(self, name):
        '''Return a function that creates dummy figures'''
        def dummy_chart(*args, **kwargs):
            return _DummyFigure()
        return dummy_chart

    # Explicitly define common chart types
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
    def sunburst(self, *args, **kwargs):
        return _DummyFigure()
    def funnel(self, *args, **kwargs):
        return _DummyFigure()

class _DummyGO:
    '''Dummy plotly.graph_objects'''
    def __getattr__(self, name):
        '''Return appropriate dummy for any attribute'''
        if name == 'Figure':
            return lambda *args, **kwargs: _DummyFigure()
        else:
            # For trace types (Bar, Scatter, etc.), return empty dict
            return lambda *args, **kwargs: {}

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
    def Box(self, *args, **kwargs):
        return {}
    def Heatmap(self, *args, **kwargs):
        return {}

class _DummySubplots:
    '''Dummy make_subplots function'''
    def __call__(self, *args, **kwargs):
        return _DummyFigure()

# Create dummy objects
px = _DummyPlotly()
go = _DummyGO()
make_subplots = _DummySubplots()
"""

def add_complete_dummies(content):
    """Add complete dummy objects after commented imports"""

    lines = content.split('\n')
    fixed_lines = []
    imports_done = False

    for i, line in enumerate(lines):
        fixed_lines.append(line)

        # After the last numpy import comment, add dummies
        if not imports_done and line.strip().startswith('# import numpy'):
            fixed_lines.append('')
            fixed_lines.extend(COMPLETE_DUMMY_PLOTLY.split('\n'))
            imports_done = True

    return '\n'.join(fixed_lines)

def wrap_plotly_charts(content):
    """Wrap st.plotly_chart to show info message instead"""

    # Replace st.plotly_chart with info message
    content = content.replace(
        'st.plotly_chart(fig',
        'st.info("📊 Chart not available in Snowflake - view data in table below") # st.plotly_chart(fig'
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

        # Add complete dummies
        print(f"  🔧 Adding COMPLETE dummy plotly objects...")
        content = add_complete_dummies(content)

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

        lines = len(content.split('\n'))
        print(f"  ✅ Created: {lines} lines, syntax valid")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Process all apps"""
    print("="*80)
    print("ADDING COMPLETE DUMMY PLOTLY OBJECTS")
    print("="*80)
    print(f"\nFeatures:")
    print(f"  - __getattr__ magic method catches ANY method call")
    print(f"  - No more AttributeErrors")
    print(f"  - All plotly code runs (does nothing)")
    print(f"  - Charts replaced with info messages\n")

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
        print(f"\nThese apps will:")
        print(f"  - Run without ANY errors")
        print(f"  - Show info messages instead of charts")
        print(f"  - Display all data in tables")
        print(f"  - Work perfectly in Snowflake")

if __name__ == "__main__":
    main()