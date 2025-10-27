"""
Shared Utilities for SECURITY_ANALYTICS Streamlit Apps
Provides dummy classes for plotly and numpy compatibility in Snowflake Streamlit
"""
import streamlit as st
import pandas as pd
from datetime import datetime

# ============================================================================
# DUMMY CLASSES FOR SNOWFLAKE STREAMLIT COMPATIBILITY
# ============================================================================

class _DummyColors:
    """Dummy plotly.express.colors"""
    sequential = {
        'Blues': ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c', '#08306b'],
        'Reds': ['#fff5f0', '#fee0d2', '#fcbba1', '#fc9272', '#fb6a4a', '#ef3b2c', '#cb181d', '#a50f15', '#67000d'],
        'Greens': ['#f7fcf5', '#e5f5e0', '#c7e9c0', '#a1d99b', '#74c476', '#41ab5d', '#238b45', '#006d2c', '#00441b'],
    }

class _DummyFigure:
    """Dummy plotly figure object"""
    def __init__(self):
        self.data = []
        self.layout = {}

    def update_layout(self, **kwargs):
        self.layout.update(kwargs)
        return self

    def update_traces(self, **kwargs):
        return self

    def add_trace(self, trace):
        self.data.append(trace)
        return self

    def update_xaxes(self, **kwargs):
        return self

    def update_yaxes(self, **kwargs):
        return self

class _DummyTrace:
    """Dummy plotly trace (Bar, Scatter, etc.)"""
    def __init__(self, **kwargs):
        self.params = kwargs

class _DummyGO:
    """Dummy plotly.graph_objects"""
    def Bar(self, **kwargs):
        return _DummyTrace(**kwargs)

    def Scatter(self, **kwargs):
        return _DummyTrace(**kwargs)

    def Pie(self, **kwargs):
        return _DummyTrace(**kwargs)

    def Line(self, **kwargs):
        return _DummyTrace(**kwargs)

    def Indicator(self, **kwargs):
        return _DummyTrace(**kwargs)

    def Figure(self, data=None):
        return _DummyFigure()

class _DummySubplots:
    """Dummy make_subplots function"""
    def __call__(self, **kwargs):
        return _DummyFigure()

class _DummyPlotly:
    """Dummy plotly.express that returns dummy figures"""
    colors = _DummyColors()

    def bar(self, *args, **kwargs):
        return _DummyFigure()

    def line(self, *args, **kwargs):
        return _DummyFigure()

    def scatter(self, *args, **kwargs):
        return _DummyFigure()

    def pie(self, *args, **kwargs):
        return _DummyFigure()

    def area(self, *args, **kwargs):
        return _DummyFigure()

    def histogram(self, *args, **kwargs):
        return _DummyFigure()

    def box(self, *args, **kwargs):
        return _DummyFigure()

class _DummyNumpy:
    """Dummy numpy replacement for Snowflake Streamlit"""
    inf = float('inf')
    pi = 3.14159265359
    e = 2.71828182846

    def round(self, value, decimals=0):
        """Round values"""
        if isinstance(value, (list, tuple)):
            return [round(v, decimals) for v in value]
        return round(value, decimals) if value is not None else None

    def array(self, data):
        """Return data as-is (list or pandas series)"""
        return data

    def arange(self, start, stop=None, step=1):
        """Generate range of numbers"""
        if stop is None:
            stop = start
            start = 0
        return list(range(int(start), int(stop), int(step)))

    def linspace(self, start, stop, num=50):
        """Generate evenly spaced numbers"""
        if num == 1:
            return [start]
        step = (stop - start) / (num - 1)
        return [start + step * i for i in range(num)]

    def mean(self, data):
        """Calculate mean"""
        if not data:
            return None
        return sum(data) / len(data)

    def median(self, data):
        """Calculate median"""
        if not data:
            return None
        sorted_data = sorted(data)
        n = len(sorted_data)
        if n % 2 == 0:
            return (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
        return sorted_data[n//2]

    def std(self, data):
        """Calculate standard deviation"""
        if not data:
            return None
        mean_val = self.mean(data)
        variance = sum((x - mean_val) ** 2 for x in data) / len(data)
        return variance ** 0.5

    def sum(self, data):
        """Sum values"""
        return sum(data) if data else 0

    def min(self, data):
        """Minimum value"""
        return min(data) if data else None

    def max(self, data):
        """Maximum value"""
        return max(data) if data else None

    class random:
        """Dummy numpy.random"""
        @staticmethod
        def randint(low, high=None, size=None):
            """Generate random integers"""
            import random
            if high is None:
                high = low
                low = 0
            if size is None:
                return random.randint(low, high - 1)
            return [random.randint(low, high - 1) for _ in range(size)]

        @staticmethod
        def rand(*args):
            """Generate random floats"""
            import random
            if not args:
                return random.random()
            if len(args) == 1:
                return [random.random() for _ in range(args[0])]
            # For multi-dimensional, return flat list
            size = 1
            for dim in args:
                size *= dim
            return [random.random() for _ in range(size)]

        @staticmethod
        def choice(data, size=None):
            """Random choice from data"""
            import random
            if size is None:
                return random.choice(data)
            return [random.choice(data) for _ in range(size)]

# Create global dummy objects for use in apps
px = _DummyPlotly()
go = _DummyGO()
make_subplots = _DummySubplots()
np = _DummyNumpy()

# ============================================================================
# COMMON UTILITY FUNCTIONS
# ============================================================================

def export_csv(df: pd.DataFrame, filename: str = "export", key_suffix: str = None):
    """
    Add CSV export button with unique key

    Args:
        df: DataFrame to export
        filename: Base filename (without extension)
        key_suffix: Optional suffix for button key to ensure uniqueness
    """
    if df.empty:
        return

    csv = df.to_csv(index=False).encode('utf-8')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    download_filename = f"{filename}_{timestamp}.csv"

    button_key = f"download_{filename}"
    if key_suffix:
        button_key = f"{button_key}_{key_suffix}"

    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=download_filename,
        mime="text/csv",
        key=button_key
    )

def format_large_number(num):
    """Format large numbers with K, M, B suffixes"""
    if num is None or pd.isna(num):
        return "0"

    num = float(num)

    if abs(num) >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    elif abs(num) >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif abs(num) >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return f"{num:.0f}"

def display_metric_card(col, label: str, value, delta=None, delta_color="normal"):
    """
    Display a metric in a styled card

    Args:
        col: Streamlit column object
        label: Metric label
        value: Metric value
        delta: Optional delta value (change/trend)
        delta_color: "normal", "inverse", or "off"
    """
    with col:
        st.metric(
            label=label,
            value=value,
            delta=delta,
            delta_color=delta_color
        )

def safe_percentage(numerator, denominator, decimals=1):
    """
    Calculate percentage safely (handles division by zero)

    Args:
        numerator: Top number
        denominator: Bottom number
        decimals: Decimal places to round to

    Returns:
        Float percentage or 0 if denominator is zero
    """
    if denominator == 0 or denominator is None:
        return 0.0
    return round((numerator / denominator) * 100, decimals)

def create_severity_badge(severity: str) -> str:
    """
    Create HTML badge for severity levels

    Args:
        severity: Severity level (Critical, High, Medium, Low, Info)

    Returns:
        HTML string with colored badge
    """
    severity_upper = str(severity).upper()

    colors = {
        'CRITICAL': '#8B0000',  # Dark red
        'HIGH': '#DC143C',      # Crimson
        'MEDIUM': '#FF8C00',    # Dark orange
        'LOW': '#FFD700',       # Gold
        'INFO': '#4682B4',      # Steel blue
        'UNKNOWN': '#808080'    # Gray
    }

    color = colors.get(severity_upper, colors['UNKNOWN'])

    return f'<span style="background-color: {color}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 0.85em;">{severity_upper}</span>'

def create_status_badge(status: str) -> str:
    """
    Create HTML badge for status

    Args:
        status: Status text (Active, Resolved, Pending, etc.)

    Returns:
        HTML string with colored badge
    """
    status_upper = str(status).upper()

    colors = {
        'ACTIVE': '#DC143C',    # Red
        'RESOLVED': '#228B22',  # Green
        'PENDING': '#FF8C00',   # Orange
        'CLOSED': '#4682B4',    # Blue
        'OPEN': '#DC143C',      # Red
        'IN PROGRESS': '#FF8C00' # Orange
    }

    color = colors.get(status_upper, '#808080')  # Default gray

    return f'<span style="background-color: {color}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 0.85em;">{status_upper}</span>'

def apply_dataframe_styling(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply consistent styling to dataframes for display

    Args:
        df: DataFrame to style

    Returns:
        Styled DataFrame
    """
    if df.empty:
        return df

    # Remove index for cleaner display
    return df.reset_index(drop=True)

def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Truncate text with ellipsis

    Args:
        text: Text to truncate
        max_length: Maximum length before truncation

    Returns:
        Truncated text with ... if needed
    """
    if text is None:
        return ""

    text_str = str(text)
    if len(text_str) <= max_length:
        return text_str

    return text_str[:max_length - 3] + "..."
