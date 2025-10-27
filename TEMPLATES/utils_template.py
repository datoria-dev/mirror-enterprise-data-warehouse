"""
Shared Utilities for SECURITY_ANALYTICS Streamlit Apps
==============================================

This module contains reusable utility classes and functions used across
all SECURITY_ANALYTICS Streamlit applications in Snowflake.

Usage:
    from utils import _DummyPlotly, _DummyNumpy, export_csv, format_number

Author: SECURITY_ANALYTICS Team
Date: 2025-10-27
Version: 1.0
"""

import streamlit as st
import pandas as pd
from datetime import datetime


# =============================================================================
# Dummy Classes for Snowflake Streamlit Compatibility
# =============================================================================
# Snowflake Streamlit doesn't have plotly or numpy available.
# These dummy classes prevent NameError and AttributeError exceptions
# while maintaining code compatibility with local development.
# =============================================================================

class _DummyColors:
    """Dummy color palettes for plotly compatibility"""

    class sequential:
        Reds = ['#fee5d9', '#fcae91', '#fb6a4a', '#de2d26', '#a50f15']
        Blues = ['#eff3ff', '#bdd7e7', '#6baed6', '#3182bd', '#08519c']
        Greens = ['#edf8e9', '#bae4b3', '#74c476', '#31a354', '#006d2c']
        RdYlGn = ['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641']
        Oranges = ['#feedde', '#fdd0a2', '#fdae6b', '#fd8d3c', '#e6550d']
        Purples = ['#f2f0f7', '#dadaeb', '#bcbddc', '#9e9ac8', '#756bb1']

    class diverging:
        RdYlGn = ['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641']
        RdBu = ['#ca0020', '#f4a582', '#f7f7f7', '#92c5de', '#0571b0']
        Spectral = ['#d53e4f', '#fc8d59', '#fee08b', '#e6f598', '#99d594', '#3288bd']


class _DummyNumpy:
    """Dummy numpy replacement for Snowflake Streamlit"""

    # Constants
    inf = float('inf')
    pi = 3.14159265359
    e = 2.71828182846

    def round(self, *args, **kwargs):
        """Dummy round function - returns input as-is"""
        if args:
            return args[0]
        return None

    def array(self, *args, **kwargs):
        """Dummy array function - returns input as-is"""
        if args:
            return args[0]
        return []

    def arange(self, *args, **kwargs):
        """Dummy arange - returns range as list"""
        if len(args) == 1:
            return list(range(args[0]))
        elif len(args) == 2:
            return list(range(args[0], args[1]))
        elif len(args) == 3:
            return list(range(args[0], args[1], args[2]))
        return []

    def linspace(self, start, stop, num=50):
        """Dummy linspace - basic implementation"""
        if num == 1:
            return [start]
        step = (stop - start) / (num - 1)
        return [start + step * i for i in range(num)]

    def sum(self, *args, **kwargs):
        """Dummy sum"""
        if args and hasattr(args[0], '__iter__'):
            return sum(args[0])
        return 0

    def mean(self, *args, **kwargs):
        """Dummy mean"""
        if args and hasattr(args[0], '__iter__'):
            vals = list(args[0])
            return sum(vals) / len(vals) if vals else 0
        return 0

    def __getattr__(self, name):
        """Return dummy function for any numpy method not explicitly defined"""
        def dummy_func(*args, **kwargs):
            if args:
                return args[0]
            return None
        return dummy_func


class _DummyFigure:
    """Dummy Figure class that accepts any method call and does nothing"""

    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        """Return a dummy method for any attribute access"""
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
    """Dummy plotly.express that returns dummy figures"""

    colors = _DummyColors()

    def __getattr__(self, name):
        """Return a function that creates dummy figures"""
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
    """Dummy plotly.graph_objects"""

    def __getattr__(self, name):
        """Return appropriate dummy for any attribute"""
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
    """Dummy make_subplots function"""

    def __call__(self, *args, **kwargs):
        return _DummyFigure()


# =============================================================================
# Common Utility Functions
# =============================================================================

def export_csv(df: pd.DataFrame, filename: str = "export", key_suffix: str = None):
    """
    Add CSV export button for a dataframe with unique key

    Args:
        df: DataFrame to export
        filename: Base filename without extension
        key_suffix: Optional suffix for button key (for multiple buttons)

    Returns:
        None (displays download button in Streamlit)
    """
    if df.empty:
        return

    csv = df.to_csv(index=False).encode('utf-8')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Generate unique key
    if key_suffix:
        button_key = f"download_{filename}_{key_suffix}_{timestamp}"
    else:
        button_key = f"download_{filename}_{timestamp}"

    st.download_button(
        label=f"📥 Download {filename}.csv",
        data=csv,
        file_name=f"{filename}_{timestamp}.csv",
        mime="text/csv",
        key=button_key
    )


def format_number(number, decimals=2, prefix="", suffix=""):
    """
    Format number with thousand separators and optional prefix/suffix

    Args:
        number: Number to format
        decimals: Number of decimal places
        prefix: String to add before number (e.g., "$")
        suffix: String to add after number (e.g., "%")

    Returns:
        Formatted string

    Examples:
        >>> format_number(1234567.89)
        '1,234,567.89'
        >>> format_number(0.1234, decimals=2, suffix="%")
        '0.12%'
        >>> format_number(1000000, decimals=0, prefix="$")
        '$1,000,000'
    """
    try:
        formatted = f"{float(number):,.{decimals}f}"
        return f"{prefix}{formatted}{suffix}"
    except (ValueError, TypeError):
        return str(number)


def calculate_percentage(part, total, decimals=1):
    """
    Calculate percentage with handling for zero division

    Args:
        part: Numerator
        total: Denominator
        decimals: Number of decimal places

    Returns:
        Percentage as float, or 0.0 if total is zero

    Examples:
        >>> calculate_percentage(25, 100)
        25.0
        >>> calculate_percentage(1, 3, decimals=2)
        33.33
        >>> calculate_percentage(10, 0)
        0.0
    """
    try:
        if total == 0:
            return 0.0
        return round((float(part) / float(total)) * 100, decimals)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0.0


def truncate_text(text, max_length=50, suffix="..."):
    """
    Truncate text to maximum length with ellipsis

    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: String to add if truncated

    Returns:
        Truncated string

    Examples:
        >>> truncate_text("This is a very long text", max_length=10)
        'This is...'
    """
    text_str = str(text)
    if len(text_str) <= max_length:
        return text_str
    return text_str[:max_length - len(suffix)] + suffix


def safe_divide(numerator, denominator, default=0):
    """
    Safely divide two numbers with handling for zero division

    Args:
        numerator: Number to divide
        denominator: Number to divide by
        default: Value to return if division fails

    Returns:
        Division result or default value

    Examples:
        >>> safe_divide(10, 2)
        5.0
        >>> safe_divide(10, 0)
        0
        >>> safe_divide(10, 0, default=None)
        None
    """
    try:
        if denominator == 0:
            return default
        return float(numerator) / float(denominator)
    except (ValueError, TypeError):
        return default


def format_date(date_value, format_string="%Y-%m-%d"):
    """
    Format date value to string

    Args:
        date_value: Date value (string, datetime, or pandas Timestamp)
        format_string: strftime format string

    Returns:
        Formatted date string or original value if conversion fails

    Examples:
        >>> format_date(datetime(2025, 10, 27))
        '2025-10-27'
        >>> format_date('2025-10-27', format_string="%B %d, %Y")
        'October 27, 2025'
    """
    try:
        if isinstance(date_value, str):
            # Try to parse string to datetime
            date_obj = pd.to_datetime(date_value)
        else:
            date_obj = date_value

        return date_obj.strftime(format_string)
    except:
        return str(date_value)


# =============================================================================
# Create dummy objects for use in apps
# =============================================================================

# These can be imported directly: from utils import px, go, make_subplots, np
px = _DummyPlotly()
go = _DummyGO()
make_subplots = _DummySubplots()
np = _DummyNumpy()


# =============================================================================
# Module metadata
# =============================================================================

__version__ = "1.0.0"
__author__ = "SECURITY_ANALYTICS Team"
__all__ = [
    'px', 'go', 'make_subplots', 'np',
    '_DummyPlotly', '_DummyGO', '_DummyNumpy', '_DummyFigure',
    'export_csv', 'format_number', 'calculate_percentage',
    'truncate_text', 'safe_divide', 'format_date'
]
