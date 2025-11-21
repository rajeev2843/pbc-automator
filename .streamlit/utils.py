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

# Custom CSS - Ocean Theme
def apply_custom_styling():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Inter', sans-serif !important;
        }
        
        /* CRITICAL FIX: Hide keyboard_arrow text */
        button[kind="header"] {
            display: none !important;
        }
        
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        
        /* Main app background - Deep Ocean with gradient */
        .main {
            background: linear-gradient(135deg, #0A1929 0%, #0C2D48 50%, #0C4A6E 100%);
            padding: 0;
            min-height: 100vh;
        }
        
        .stApp {
            background: linear-gradient(135deg, #0A1929 0%, #0C2D48 50%, #0C4A6E 100%);
        }
        
        /* Remove white containers */
        .element-container {
            background: transparent !important;
        }
        
        .stMarkdown {
            background: transparent !important;
        }
        
        /* Sidebar - Ocean Blue gradient */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0C2D48 0%, #0C4A6E 100%) !important;
            border-right: 2px solid #06B6D4;
        }
        
        [data-testid="stSidebar"] > div:first-child {
            background: transparent !important;
        }
        
        /* Sidebar text - always visible */
        [data-testid="stSidebar"] * {
            color: #E0F2FE !important;
        }
        
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {
            color: #E0F2FE !important;
        }
        
        /* Remove ALL radio circles */
        input[type="radio"] {
            display: none !important;
        }
        
        [data-testid="stSidebar"] .row-widget.stRadio > div > label > div:first-child {
            display: none !important;
            width: 0 !important;
            height: 0 !important;
        }
        
        /* Sidebar navigation */
        [data-testid="stSidebar"] .row-widget.stRadio > div {
            gap: 0px;
            flex-direction: column;
        }
        
        [data-testid="stSidebar"] .row-widget.stRadio > div > label {
            background: transparent !important;
            padding: 14px 20px !important;
            border-radius: 10px !important;
            cursor: pointer;
            transition: all 0.3s ease;
            border: none !important;
            font-weight: 500 !important;
            margin-bottom: 6px;
            border-left: 3px solid transparent !important;
        }
        
        [data-testid="stSidebar"] .row-widget.stRadio > div > label:hover {
            background: rgba(6, 182, 212, 0.2) !important;
            border-left: 3px solid #06B6D4 !important;
        }
        
        /* Active navigation - bold & underlined */
        [data-testid="stSidebar"] .row-widget.stRadio > div > label[data-checked="true"] {
            background: linear-gradient(90deg, rgba(6, 182, 212, 0.3), rgba(20, 184, 166, 0.3)) !important;
            font-weight: 700 !important;
            border-left: 3px solid #14B8A6 !important;
        }
        
        [data-testid="stSidebar"] .row-widget.stRadio > div > label[data-checked="true"] p {
            font-weight: 700 !important;
            text-decoration: underline;
            text-decoration-color: #5EEAD4;
            text-decoration-thickness: 2px;
            text-underline-offset: 4px;
        }
        
        /* Main content cards - transparent with aqua glow */
        .main-card {
            background: rgba(12, 45, 72, 0.6) !important;
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            margin: 20px auto;
            max-width: 1200px;
            border: 1px solid rgba(6, 182, 212, 0.3);
            box-shadow: 0 8px 32px rgba(6, 182, 212, 0.15);
        }
        
        /* Text colors - HIGHLY VISIBLE on dark ocean */
        h1, h2, h3, h4, h5, h6 {
            color: #E0F2FE !important;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        p, span, div, label, li {
            color: #BAE6FD !important;
        }
        
        /* Buttons - Ocean gradient with glow */
        .stButton > button {
            background: linear-gradient(135deg, #0EA5E9 0%, #06B6D4 50%, #14B8A6 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 14px 28px !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 20px rgba(6, 182, 212, 0.4) !important;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 30px rgba(6, 182, 212, 0.6) !important;
            background: linear-gradient(135deg, #38BDF8 0%, #0EA5E9 50%, #06B6D4 100%) !important;
        }
        
        /* Metric cards - Aqua gradient */
        .metric-card {
            background: linear-gradient(135deg, #0EA5E9 0%, #06B6D4 50%, #14B8A6 100%);
            color: white !important;
            padding: 28px;
            border-radius: 16px;
            box-shadow: 0 8px 25px rgba(6, 182, 212, 0.4);
            margin-bottom: 20px;
            border: 2px solid rgba(94, 234, 212, 0.3);
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 12px 35px rgba(6, 182, 212, 0.6);
            border-color: #5EEAD4;
        }
        
        .metric-card * {
            color: white !important;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        /* Status badges */
        .status-badge {
            padding: 6px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 13px;
            display: inline-block;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
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
        
        /* PBC item cards - Ocean themed */
        .pbc-item-card {
            background: rgba(12, 45, 72, 0.8);
            backdrop-filter: blur(10px);
            border: 2px solid rgba(6, 182, 212, 0.3);
            border-radius: 14px;
            padding: 22px;
            margin-bottom: 16px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        
        .pbc-item-card:hover {
            border-color: #06B6D4;
            box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4);
            transform: translateX(5px);
        }
        
        .pbc-item-card h3 {
            color: #E0F2FE !important;
            margin-bottom: 12px;
        }
        
        .pbc-item-card p {
            color: #BAE6FD !important;
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
        
        /* Input fields - Ocean themed */
        .stTextInput > div > div > input,
        .stTextArea textarea {
            background: rgba(12, 45, 72, 0.9) !important;
            color: #E0F2FE !important;
            border-radius: 10px !important;
            border: 2px solid rgba(6, 182, 212, 0.4) !important;
            padding: 12px !important;
            font-size: 15px !important;
        }
        
        .stTextInput > div > div > input::placeholder,
        .stTextArea textarea::placeholder {
            color: #7DD3FC !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea textarea:focus {
            border-color: #06B6D4 !important;
            box-shadow: 0 0 0 4px rgba(6, 182, 212, 0.2) !important;
            outline: none !important;
        }
        
        /* Dropdowns - VISIBLE text */
        .stSelectbox > div > div {
            background: rgba(12, 45, 72, 0.9) !important;
            color: #E0F2FE !important;
            border-radius: 10px !important;
            border: 2px solid rgba(6, 182, 212, 0.4) !important;
        }
        
        .stSelectbox [data-baseweb="select"] > div {
            background: rgba(12, 45, 72, 0.9) !important;
            color: #E0F2FE !important;
            border-color: rgba(6, 182, 212, 0.4) !important;
        }
        
        .stSelectbox [data-baseweb="select"] span {
            color: #E0F2FE !important;
        }
        
        .stSelectbox input {
            color: #E0F2FE !important;
        }
        
        /* Dropdown options */
        [data-baseweb="popover"] {
            background: rgba(12, 45, 72, 0.95) !important;
            backdrop-filter: blur(10px);
        }
        
        [data-baseweb="menu"] {
            background: rgba(12, 45, 72, 0.95) !important;
            border: 2px solid rgba(6, 182, 212, 0.5) !important;
        }
        
        [role="option"] {
            background: transparent !important;
            color: #E0F2FE !important;
            padding: 12px !important;
        }
        
        [role="option"]:hover {
            background: rgba(6, 182, 212, 0.3) !important;
        }
        
        [aria-selected="true"] {
            background: rgba(6, 182, 212, 0.4) !important;
            color: white !important;
        }
        
        /* Hero title - Ocean gradient */
        .hero-title {
            font-size: 56px;
            font-weight: 800;
            background: linear-gradient(135deg, #0EA5E9, #06B6D4, #14B8A6, #5EEAD4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 20px;
            text-shadow: 0 4px 8px rgba(6, 182, 212, 0.3);
            letter-spacing: -1px;
        }
        
        /* Feature cards - Glassmorphism ocean */
        .feature-card {
            background: rgba(12, 45, 72, 0.7);
            backdrop-filter: blur(10px);
            padding: 32px;
            border-radius: 16px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
            text-align: center;
            transition: all 0.3s ease;
            border: 2px solid rgba(6, 182, 212, 0.3);
        }
        
        .feature-card:hover {
            transform: translateY(-8px);
            border-color: #06B6D4;
            box-shadow: 0 12px 30px rgba(6, 182, 212, 0.4);
        }
        
        .feature-card h3 {
            color: #E0F2FE !important;
        }
        
        .feature-card p {
            color: #BAE6FD !important;
        }
        
        .icon-large {
            font-size: 52px;
            margin-bottom: 16px;
            filter: drop-shadow(0 4px 8px rgba(6, 182, 212, 0.3));
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Progress bars - Aqua gradient */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #0EA5E9, #06B6D4, #14B8A6) !important;
        }
        
        /* Expanders */
        .streamlit-expanderHeader {
            background: rgba(12, 45, 72, 0.8) !important;
            backdrop-filter: blur(10px);
            border-radius: 10px !important;
            color: #E0F2FE !important;
            border: 2px solid rgba(6, 182, 212, 0.3) !important;
        }
        
        .streamlit-expanderHeader:hover {
            border-color: #06B6D4 !important;
            background: rgba(12, 45, 72, 0.9) !important;
        }
        
        .streamlit-expanderContent {
            background: rgba(12, 45, 72, 0.8) !important;
            border: 2px solid rgba(6, 182, 212, 0.3) !important;
            border-top: none !important;
        }
        
        /* Tabs - Ocean themed */
        .stTabs [data-baseweb="tab-list"] {
            background: rgba(12, 45, 72, 0.8);
            border-radius: 10px;
            padding: 6px;
            gap: 6px;
            border: 1px solid rgba(6, 182, 212, 0.3);
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            color: #7DD3FC !important;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 500;
            border: none;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(6, 182, 212, 0.2);
            color: #E0F2FE !important;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(90deg, #0EA5E9, #06B6D4) !important;
            color: white !important;
        }
        
        /* File uploader */
        [data-testid="stFileUploader"] {
            background: rgba(12, 45, 72, 0.8);
            border: 3px dashed #06B6D4;
            border-radius: 14px;
            padding: 24px;
        }
        
        [data-testid="stFileUploader"]:hover {
            border-color: #14B8A6;
            background: rgba(12, 45, 72, 0.9);
        }
        
        [data-testid="stFileUploader"] label {
            color: #E0F2FE !important;
        }
        
        /* Code blocks */
        code {
            background: rgba(12, 45, 72, 0.9) !important;
            color: #5EEAD4 !important;
            padding: 6px 10px;
            border-radius: 6px;
            border: 1px solid rgba(6, 182, 212, 0.4);
        }
        
        pre {
            background: rgba(12, 45, 72, 0.9) !important;
            border: 2px solid rgba(6, 182, 212, 0.4) !important;
            border-radius: 10px;
        }
        
        /* Messages */
        .stSuccess {
            background: rgba(16, 185, 129, 0.2) !important;
            border-left: 4px solid #10B981 !important;
            color: #D1FAE5 !important;
            backdrop-filter: blur(10px);
        }
        
        .stError {
            background: rgba(239, 68, 68, 0.2) !important;
            border-left: 4px solid #EF4444 !important;
            color: #FEE2E2 !important;
            backdrop-filter: blur(10px);
        }
        
        .stWarning {
            background: rgba(245, 158, 11, 0.2) !important;
            border-left: 4px solid #F59E0B !important;
            color: #FEF3C7 !important;
            backdrop-filter: blur(10px);
        }
        
        .stInfo {
            background: rgba(6, 182, 212, 0.2) !important;
            border-left: 4px solid #06B6D4 !important;
            color: #E0F2FE !important;
            backdrop-filter: blur(10px);
        }
        
        /* Divider */
        hr {
            border-color: rgba(6, 182, 212, 0.3) !important;
            margin: 24px 0;
        }
        
        /* Hero buttons with dark text */
        .stButton > button[key="hero_signup"],
        .stButton > button[key="hero_signin"],
        .stButton > button[key="cta_button"] {
            background: linear-gradient(135deg, #0EA5E9 0%, #06B6D4 50%, #14B8A6 100%) !important;
            color: #0A1929 !important;
            font-weight: 700 !important;
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
