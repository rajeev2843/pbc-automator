import streamlit as st
import bcrypt
import secrets
from datetime import datetime, timedelta
import pandas as pd
from database import *

# Authentication
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_invite_code():
    return f"CA-{secrets.token_hex(4).upper()}"

def login_user(user_id, role):
    st.session_state.user_id = user_id
    st.session_state.role = role
    st.session_state.authenticated = True

def logout_user():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Custom CSS
def apply_custom_styling():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Inter', sans-serif !important;
        }
        
        /* CRITICAL FIX: Hide keyboard_arrow text completely */
        button[kind="header"] {
            display: none !important;
        }
        
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        
        .css-1dp5vir {
            display: none !important;
        }
        
        /* Hide any element containing "keyboard" text */
        *:contains("keyboard") {
            display: none !important;
        }
        
        /* Main app background - dark navy blue */
        .main {
            background: linear-gradient(135deg, #0A0E27 0%, #141B3D 100%);
            padding: 0;
        }
        
        .stApp {
            background: linear-gradient(135deg, #0A0E27 0%, #141B3D 100%);
        }
        
        /* Remove any white/light background containers */
        .element-container {
            background: transparent !important;
        }
        
        .stMarkdown {
            background: transparent !important;
        }
        
        /* Sidebar - dark navy */
        [data-testid="stSidebar"] {
            background: #141B3D !important;
            border-right: 1px solid #1E293B;
        }
        
        [data-testid="stSidebar"] > div:first-child {
            background: #141B3D !important;
        }
        
        /* Disable sidebar drag to expand */
        [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {
            pointer-events: none !important;
        }
        
        /* Sidebar text colors */
        [data-testid="stSidebar"] * {
            color: #E2E8F0 !important;
        }
        
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] div {
            color: #E2E8F0 !important;
        }
        
        /* CRITICAL: Remove ALL radio button circles */
        [data-testid="stSidebar"] .row-widget.stRadio > div > label > div:first-child {
            display: none !important;
            width: 0 !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        [data-testid="stSidebar"] .row-widget.stRadio > div > label > div[data-testid="stMarkdownContainer"] {
            margin-left: 0 !important;
            padding-left: 0 !important;
        }
        
        /* Radio buttons - remove circles everywhere */
        input[type="radio"] {
            display: none !important;
        }
        
        .row-widget.stRadio > div > label > div:first-child {
            display: none !important;
        }
        
        /* Sidebar navigation styling */
        [data-testid="stSidebar"] .row-widget.stRadio > div {
            gap: 0px;
            flex-direction: column;
        }
        
        [data-testid="stSidebar"] .row-widget.stRadio > div > label {
            background: transparent !important;
            padding: 14px 20px !important;
            border-radius: 8px !important;
            cursor: pointer;
            transition: all 0.2s;
            border: none !important;
            font-weight: 500 !important;
            margin-bottom: 6px;
            border-left: 3px solid transparent !important;
        }
        
        [data-testid="stSidebar"] .row-widget.stRadio > div > label:hover {
            background: rgba(99, 102, 241, 0.15) !important;
            border-left: 3px solid #6366F1 !important;
        }
        
        /* Active sidebar item - BOLD and UNDERLINED */
        [data-testid="stSidebar"] .row-widget.stRadio > div > label[data-checked="true"] {
            background: rgba(99, 102, 241, 0.25) !important;
            font-weight: 700 !important;
            border-left: 3px solid #6366F1 !important;
        }
        
        [data-testid="stSidebar"] .row-widget.stRadio > div > label[data-checked="true"] p {
            font-weight: 700 !important;
            text-decoration: underline;
            text-decoration-color: #6366F1;
            text-decoration-thickness: 2px;
            text-underline-offset: 4px;
        }
        
        /* Main content cards */
        .main-card {
            background: transparent !important;
            border-radius: 16px;
            padding: 40px;
            margin: 20px auto;
            max-width: 1200px;
        }
        
        /* Text colors - light on dark */
        h1, h2, h3, h4, h5, h6 {
            color: #E2E8F0 !important;
        }
        
        p, span, div, label, li {
            color: #CBD5E1 !important;
        }
        
        /* Buttons - vibrant blue gradient */
        .stButton > button {
            background: linear-gradient(90deg, #6366F1 0%, #8B5CF6 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 14px 28px !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6) !important;
        }
        
        /* Metric cards - clickable with pointer */
        .metric-card {
            background: linear-gradient(135deg, #1E40AF 0%, #7C3AED 100%);
            color: white !important;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
            margin-bottom: 20px;
            border: 1px solid rgba(99, 102, 241, 0.3);
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5);
        }
        
        .metric-card * {
            color: white !important;
        }
        
        /* Status badges */
        .status-badge {
            padding: 6px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 13px;
            display: inline-block;
        }
        
        .status-pending {
            background: #FEF3C7;
            color: #92400E !important;
        }
        
        .status-progress {
            background: #DBEAFE;
            color: #1E40AF !important;
        }
        
        .status-submitted {
            background: #D1FAE5;
            color: #065F46 !important;
        }
        
        .status-verified {
            background: #D1FAE5;
            color: #065F46 !important;
            border: 2px solid #10B981;
        }
        
        .status-rejected {
            background: #FEE2E2;
            color: #991B1B !important;
        }
        
        /* PBC item cards */
        .pbc-item-card {
            background: #1E293B;
            border: 2px solid #334155;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }
        
        .pbc-item-card:hover {
            border-color: #6366F1;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }
        
        .pbc-item-card h3 {
            color: #E2E8F0 !important;
            margin-bottom: 10px;
        }
        
        .pbc-item-card p {
            color: #CBD5E1 !important;
        }
        
        .priority-high {
            border-left: 5px solid #EF4444 !important;
        }
        
        .priority-medium {
            border-left: 5px solid #F59E0B !important;
        }
        
        .priority-low {
            border-left: 5px solid #10B981 !important;
        }
        
        /* Input fields - dark with blue focus */
        .stTextInput > div > div > input,
        .stTextArea textarea {
            background: #1E293B !important;
            color: #E2E8F0 !important;
            border-radius: 10px !important;
            border: 2px solid #334155 !important;
            padding: 12px !important;
            font-size: 15px !important;
        }
        
        .stTextInput > div > div > input::placeholder,
        .stTextArea textarea::placeholder {
            color: #64748B !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea textarea:focus {
            border-color: #6366F1 !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
            outline: none !important;
        }
        
        /* CRITICAL FIX: Dropdowns with visible text */
        .stSelectbox > div > div {
            background: #1E293B !important;
            color: #E2E8F0 !important;
            border-radius: 10px !important;
            border: 2px solid #334155 !important;
        }
        
        .stSelectbox [data-baseweb="select"] > div {
            background: #1E293B !important;
            color: #E2E8F0 !important;
            border-color: #334155 !important;
        }
        
        .stSelectbox [data-baseweb="select"] > div:hover {
            border-color: #6366F1 !important;
        }
        
        /* Dropdown selected text - MUST BE VISIBLE */
        .stSelectbox [data-baseweb="select"] span {
            color: #E2E8F0 !important;
        }
        
        .stSelectbox input {
            color: #E2E8F0 !important;
        }
        
        /* Dropdown menu options */
        [data-baseweb="popover"] {
            background: #1E293B !important;
        }
        
        [data-baseweb="menu"] {
            background: #1E293B !important;
            border: 1px solid #334155 !important;
        }
        
        [role="option"] {
            background: #1E293B !important;
            color: #E2E8F0 !important;
            padding: 12px !important;
        }
        
        [role="option"]:hover {
            background: #334155 !important;
        }
        
        [aria-selected="true"] {
            background: #475569 !important;
            color: #E2E8F0 !important;
        }
        
        /* Upload zone */
        .upload-zone {
            border: 3px dashed #6366F1;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            background: #1E293B;
            transition: all 0.3s ease;
        }
        
        .upload-zone:hover {
            background: #334155;
            border-color: #8B5CF6;
        }
        
        /* Hero title gradient */
        .hero-title {
            font-size: 48px;
            font-weight: 700;
            background: linear-gradient(90deg, #6366F1, #8B5CF6, #EC4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 20px;
        }
        
        /* Feature cards */
        .feature-card {
            background: #1E293B;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            text-align: center;
            transition: transform 0.3s ease;
            border: 1px solid #334155;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            border-color: #6366F1;
        }
        
        .feature-card h3 {
            color: #E2E8F0 !important;
        }
        
        .feature-card p {
            color: #94A3B8 !important;
        }
        
        .icon-large {
            font-size: 48px;
            margin-bottom: 15px;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Progress bars */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #6366F1, #8B5CF6) !important;
        }
        
        /* Expanders */
        .streamlit-expanderHeader {
            background: #1E293B !important;
            border-radius: 8px !important;
            color: #E2E8F0 !important;
            border: 1px solid #334155 !important;
        }
        
        .streamlit-expanderHeader:hover {
            border-color: #6366F1 !important;
        }
        
        .streamlit-expanderContent {
            background: #1E293B !important;
            border: 1px solid #334155 !important;
            border-top: none !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background: #1E293B;
            border-radius: 8px;
            padding: 4px;
            gap: 4px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            color: #94A3B8 !important;
            border-radius: 6px;
            padding: 12px 24px;
            font-weight: 500;
            border: none;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: #334155;
            color: #E2E8F0 !important;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(90deg, #6366F1, #8B5CF6) !important;
            color: white !important;
        }
        
        /* AI analysis box */
        .ai-analysis-box {
            background: linear-gradient(135deg, #1E3A8A 0%, #6366F1 100%);
            border-left: 4px solid #8B5CF6;
            padding: 20px;
            border-radius: 10px;
            margin: 15px 0;
        }
        
        .ai-analysis-box * {
            color: white !important;
        }
        
        /* Divider */
        hr {
            border-color: #334155 !important;
            margin: 20px 0;
        }
        
        /* File uploader */
        [data-testid="stFileUploader"] {
            background: #1E293B;
            border: 2px dashed #6366F1;
            border-radius: 12px;
            padding: 20px;
        }
        
        [data-testid="stFileUploader"] label {
            color: #E2E8F0 !important;
        }
        
        [data-testid="stFileUploader"] section {
            border: none !important;
        }
        
        /* Code blocks */
        code {
            background: #1E293B !important;
            color: #6366F1 !important;
            padding: 4px 8px;
            border-radius: 4px;
            border: 1px solid #334155;
        }
        
        pre {
            background: #1E293B !important;
            border: 1px solid #334155 !important;
            border-radius: 8px;
        }
        
        /* Success/Error/Warning/Info messages */
        .stSuccess {
            background: #1E293B !important;
            border-left: 4px solid #10B981 !important;
            color: #E2E8F0 !important;
        }
        
        .stError {
            background: #1E293B !important;
            border-left: 4px solid #EF4444 !important;
            color: #E2E8F0 !important;
        }
        
        .stWarning {
            background: #1E293B !important;
            border-left: 4px solid #F59E0B !important;
            color: #E2E8F0 !important;
        }
        
        .stInfo {
            background: #1E293B !important;
            border-left: 4px solid #6366F1 !important;
            color: #E2E8F0 !important;
        }
        
        </style>
    """, unsafe_allow_html=True)

def status_badge(status):
    status_map = {
        "Pending": "status-pending",
        "In Progress": "status-progress",
        "Submitted": "status-submitted",
        "Verified": "status-verified",
        "Rejected": "status-rejected"
    }
    css_class = status_map.get(status, "status-pending")
    return f'<span class="status-badge {css_class}">{status}</span>'

def priority_badge(priority):
    colors = {
        "High": "#EF4444",
        "Medium": "#F59E0B",
        "Low": "#10B981"
    }
    color = colors.get(priority, "#6B7280")
    return f'<span style="background: {color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">{priority}</span>'

def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def calculate_completion_percentage(pbc_items):
    if not pbc_items:
        return 0
    verified = sum(1 for item in pbc_items if item.status == PBCStatus.VERIFIED)
    return int((verified / len(pbc_items)) * 100)
