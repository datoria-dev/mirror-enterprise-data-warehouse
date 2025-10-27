"""
Shared components library for Streamlit apps

This module provides common utilities, styles, and functions
used across all SECURITY_ANALYTICS Streamlit validation dashboards.
"""

__version__ = "1.0.0"
__author__ = "GenericCorp Data Engineering Team"

from .styles import apply_common_styles, get_color_scheme
from .utils import safe_query, export_csv, show_data_freshness, query_with_metrics
from .validators import validate_environment, check_required_views

__all__ = [
    'apply_common_styles',
    'get_color_scheme',
    'safe_query',
    'export_csv',
    'show_data_freshness',
    'query_with_metrics',
    'validate_environment',
    'check_required_views'
]
