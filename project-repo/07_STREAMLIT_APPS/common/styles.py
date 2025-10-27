"""
Common CSS styles for all Streamlit apps

Provides consistent branding and visual design across all SECURITY_ANALYTICS dashboards.
"""

import streamlit as st


def get_color_scheme():
    """
    Get GenericCorp corporate color scheme

    Returns:
        dict: Color scheme with primary, secondary, and accent colors
    """
    return {
        'primary': '#0a3d62',
        'secondary': '#1e5f8e',
        'accent': '#3498db',
        'success': '#27ae60',
        'warning': '#f39c12',
        'error': '#e74c3c',
        'info': '#3498db',
        'bg_light': '#f8f9fa',
        'bg_medium': '#f0f4f8',
        'border': '#e0e4e8',
        'text_muted': '#64748b'
    }


def apply_common_styles():
    """
    Apply common CSS styles to Streamlit app

    This should be called once at the beginning of each app
    after st.set_page_config()
    """
    colors = get_color_scheme()

    st.markdown(f"""
    <style>
        /* Main header styling */
        .main-header {{
            background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%);
            color: white;
            padding: 2.5rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 6px 20px rgba(10, 61, 98, 0.25);
            position: relative;
            overflow: hidden;
        }}

        .main-header::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: repeating-linear-gradient(
                45deg,
                transparent,
                transparent 20px,
                rgba(255,255,255,0.03) 20px,
                rgba(255,255,255,0.03) 40px
            );
        }}

        /* Metric card styling */
        div[data-testid="metric-container"] {{
            background: linear-gradient(to bottom, #ffffff, {colors['bg_light']});
            border: 1px solid {colors['border']};
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(10, 61, 98, 0.08);
            transition: all 0.3s ease;
        }}

        div[data-testid="metric-container"]:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(10, 61, 98, 0.15);
            border-color: {colors['secondary']};
        }}

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 10px;
            background-color: {colors['bg_medium']};
            padding: 0.75rem;
            border-radius: 12px;
            box-shadow: inset 0 2px 4px rgba(10, 61, 98, 0.05);
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: 10px;
            padding: 0.75rem 1.25rem;
            background-color: white;
            border: 1px solid {colors['border']};
            font-weight: 500;
            transition: all 0.2s ease;
        }}

        .stTabs [data-baseweb="tab"]:hover {{
            background-color: #eef3f8;
            border-color: {colors['secondary']};
        }}

        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, {colors['primary']}, {colors['secondary']});
            color: white;
            border-color: {colors['primary']};
            box-shadow: 0 2px 8px rgba(10, 61, 98, 0.2);
        }}

        /* Status badges */
        .status-compliant {{ color: {colors['success']}; font-weight: bold; }}
        .status-warning {{ color: {colors['warning']}; font-weight: bold; }}
        .status-critical {{ color: {colors['error']}; font-weight: bold; }}
        .status-info {{ color: {colors['info']}; font-weight: bold; }}

        /* Risk level badges */
        .risk-critical {{ color: #c0392b; font-weight: bold; }}
        .risk-high {{ color: #e67e22; font-weight: bold; }}
        .risk-medium {{ color: {colors['warning']}; font-weight: bold; }}
        .risk-low {{ color: {colors['info']}; font-weight: bold; }}

        /* KPI cards with gradient borders */
        .kpi-card {{
            background: linear-gradient(to bottom, #ffffff, #fafbfc);
            padding: 25px;
            border-radius: 15px;
            border: 2px solid transparent;
            background-clip: padding-box;
            position: relative;
            text-align: center;
            transition: all 0.3s ease;
        }}

        .kpi-card::before {{
            content: "";
            position: absolute;
            top: 0; right: 0; bottom: 0; left: 0;
            z-index: -1;
            margin: -2px;
            border-radius: inherit;
            background: linear-gradient(135deg, {colors['primary']}, {colors['secondary']}, {colors['accent']});
        }}

        .kpi-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(10, 61, 98, 0.15);
        }}

        .kpi-value {{
            font-size: 2.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, {colors['primary']}, {colors['secondary']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .kpi-label {{
            color: {colors['text_muted']};
            font-size: 0.95rem;
            margin-top: 0.5rem;
            font-weight: 500;
            letter-spacing: 0.5px;
        }}

        /* Section styling */
        h3 {{
            color: {colors['primary']};
            border-bottom: 3px solid transparent;
            border-image: linear-gradient(to right, {colors['primary']}, {colors['secondary']}, transparent) 1;
            padding-bottom: 0.75rem;
            margin-top: 2rem;
            font-weight: 600;
        }}

        /* Button styling */
        .stButton > button {{
            background: linear-gradient(135deg, {colors['primary']}, {colors['secondary']});
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}

        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(10, 61, 98, 0.25);
        }}

        /* Custom info box */
        .stAlert {{
            background-color: #eef3f8;
            border-left: 4px solid {colors['secondary']};
        }}

        /* Data table styling */
        .dataframe {{
            font-size: 0.9rem;
        }}

        .dataframe th {{
            background-color: {colors['bg_medium']};
            color: {colors['primary']};
            font-weight: 600;
        }}
    </style>
    """, unsafe_allow_html=True)


def create_header(title: str, subtitle: str = "", icon: str = "🔐"):
    """
    Create styled header for dashboard

    Args:
        title (str): Dashboard title
        subtitle (str): Optional subtitle
        icon (str): Emoji icon (default: 🔐)
    """
    subtitle_html = f"""
    <p style="text-align: center; margin: 0.75rem 0 0 0; opacity: 0.9; position: relative; z-index: 1; font-size: 1.1rem;">
        {subtitle}
    </p>
    """ if subtitle else ""

    st.markdown(f"""
    <div class="main-header">
        <h1 style="text-align: center; margin: 0; position: relative; z-index: 1;">
            <span style="font-size: 2.5rem;">{icon}</span> {title}
        </h1>
        {subtitle_html}
    </div>
    """, unsafe_allow_html=True)


def create_sidebar_branding(company: str = "GenericCorp", department: str = "Security Dashboard"):
    """
    Create branded sidebar header

    Args:
        company (str): Company name
        department (str): Department or team name
    """
    st.markdown(f"""
    <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #0a3d62, #1e5f8e);
         border-radius: 12px; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(10, 61, 98, 0.2);">
        <h2 style="color: white; margin: 0; font-size: 1.5rem;">🏢 {company}</h2>
        <p style="color: #e8f0f8; font-size: 0.95rem; margin-top: 0.5rem;">{department}</p>
    </div>
    """, unsafe_allow_html=True)
