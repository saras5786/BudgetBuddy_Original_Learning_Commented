# High-Performance Light Theme Styles with Dynamic Tab Transitions and Smooth Hover Animations

import streamlit as st

TAB_THEMES = {
    "Dashboard": {
        "gradient": "linear-gradient(135deg, #f0f7ff 0%, #e0f2fe 35%, #f8fafc 70%, #eff6ff 100%)",
        "accent": "#2563eb",
        "border": "rgba(37, 99, 235, 0.2)"
    },
    "Budget Planner": {
        "gradient": "linear-gradient(135deg, #f0fdf4 0%, #dcfce7 35%, #f8fafc 70%, #ecfdf5 100%)",
        "accent": "#10b981",
        "border": "rgba(16, 185, 129, 0.2)"
    },
    "Add Expense": {
        "gradient": "linear-gradient(135deg, #fffbeb 0%, #fef3c7 35%, #f8fafc 70%, #fef2f2 100%)",
        "accent": "#f59e0b",
        "border": "rgba(245, 158, 11, 0.2)"
    },
    "Expense History": {
        "gradient": "linear-gradient(135deg, #faf5ff 0%, #f3e8ff 35%, #f8fafc 70%, #ede9fe 100%)",
        "accent": "#8b5cf6",
        "border": "rgba(139, 92, 246, 0.2)"
    },
    "Dataset Analyzer": {
        "gradient": "linear-gradient(135deg, #eef2ff 0%, #e0e7ff 35%, #fdf2f8 70%, #f5f3ff 100%)",
        "accent": "#6366f1",
        "border": "rgba(99, 102, 241, 0.2)"
    },
    "Profile": {
        "gradient": "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 35%, #fefce8 70%, #f1f5f9 100%)",
        "accent": "#64748b",
        "border": "rgba(100, 116, 139, 0.2)"
    }
}


def apply_custom_styles(active_tab="Dashboard"):
    theme = TAB_THEMES.get(active_tab, TAB_THEMES["Dashboard"])
    bg_gradient = theme["gradient"]
    accent = theme["accent"]

    css = f"""
    <style>
    /* Dynamic Tab-Adaptive Background with Smooth Transition */
    .stApp {{
        background: {bg_gradient} !important;
        background-attachment: fixed !important;
        transition: background 0.6s ease-in-out !important;
        color: #0f172a !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
    }}

    /* Metric Cards with Smooth GPU-Accelerated Hover */
    div[data-testid="stMetric"] {{
        background: rgba(255, 255, 255, 0.94) !important;
        border: 1px solid rgba(226, 232, 240, 0.9) !important;
        border-radius: 12px !important;
        padding: 1rem 1.2rem !important;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03) !important;
        transition: transform 0.22s cubic-bezier(0.34, 1.56, 0.64, 1),
                    box-shadow 0.22s ease,
                    border-color 0.22s ease !important;
        will-change: transform, box-shadow;
    }}

    div[data-testid="stMetric"]:hover {{
        transform: translateY(-4px) scale(1.01) !important;
        box-shadow: 0 12px 24px -3px rgba(37, 99, 235, 0.12) !important;
        border-color: {accent} !important;
    }}

    div[data-testid="stMetricLabel"] {{
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: #64748b !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
    }}

    div[data-testid="stMetricValue"] {{
        font-size: 1.55rem !important;
        font-weight: 700 !important;
        color: #0f172a !important;
    }}

    /* Generic Glass Cards */
    .glass-card {{
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid rgba(226, 232, 240, 0.9);
        border-radius: 12px;
        padding: 1.25rem 1.4rem;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
        transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
        margin-bottom: 1rem;
    }}

    .glass-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 10px 22px -3px rgba(37, 99, 235, 0.10);
        border-color: {accent};
    }}

    /* Plotly Chart Containers */
    div[data-testid="stPlotlyChart"] {{
        background: rgba(255, 255, 255, 0.94) !important;
        border: 1px solid rgba(226, 232, 240, 0.9) !important;
        border-radius: 12px !important;
        padding: 0.75rem !important;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03) !important;
        transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease !important;
    }}

    div[data-testid="stPlotlyChart"]:hover {{
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 22px -3px rgba(37, 99, 235, 0.08) !important;
        border-color: {accent} !important;
    }}

    /* Buttons */
    .stButton > button {{
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.45rem 1.2rem !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease !important;
        border: 1px solid rgba(203, 213, 225, 0.9) !important;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px -2px rgba(37, 99, 235, 0.18) !important;
        border-color: {accent} !important;
    }}

    /* Sidebar Navigation Items with Interactive Hover Shift */
    section[data-testid="stSidebar"] {{
        background: rgba(255, 255, 255, 0.88) !important;
        border-right: 1px solid rgba(226, 232, 240, 0.9) !important;
    }}

    div[data-testid="stRadio"] > div[role="radiogroup"] > label {{
        background: rgba(255, 255, 255, 0.75) !important;
        border: 1px solid rgba(226, 232, 240, 0.85) !important;
        border-radius: 8px !important;
        padding: 0.5rem 0.85rem !important;
        margin-bottom: 0.35rem !important;
        transition: transform 0.18s ease, background-color 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease !important;
        cursor: pointer !important;
    }}

    div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {{
        transform: translateX(4px) !important;
        background: rgba(255, 255, 255, 1.0) !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.12) !important;
        border-color: {accent} !important;
    }}

    /* Dataframe styling */
    div[data-testid="stDataFrame"] {{
        background: rgba(255, 255, 255, 0.95) !important;
        border: 1px solid rgba(226, 232, 240, 0.9) !important;
        border-radius: 10px !important;
    }}

    /* Clean Headers */
    h1, h2, h3, h4 {{
        color: #0f172a !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em !important;
    }}

    /* Tabs styling */
    button[data-baseweb="tab"] {{
        font-weight: 600 !important;
        border-radius: 6px !important;
        padding: 0.45rem 0.9rem !important;
        transition: all 0.18s ease !important;
    }}

    button[data-baseweb="tab"]:hover {{
        background: rgba(239, 246, 255, 0.9) !important;
        color: {accent} !important;
    }}

    /* Progress bars */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, {accent}, #06b6d4) !important;
        border-radius: 9999px !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
