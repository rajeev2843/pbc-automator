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
        
        /* Global Font */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        /* Main Background */
        .stApp {
            background-color: #F8FAFC;
        }
        
        /* --- SIDEBAR STYLING --- */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
            color: white;
        }
        
        /* Sidebar Text Color */
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
            color: #E2E8F0 !important;
        }
        
        /* Sidebar Headers */
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: #FFFFFF !important;
        }
        
        /* --- INPUT VISIBILITY FIX --- */
        /* Force text color to black in all input fields, dropdowns, and selects */
        .stTextInput input, .stSelectbox div, .stNumberInput input {
            color: #1E293B !important;
        }
        
        /* Fix dropdown menu text color (options list) */
        div[data-baseweb="select"] > div {
            color: #1E293B !important;
            background-color: white !important;
        }
        
        /* Fix Dropdown Options Text */
        ul[data-testid="stSelectboxVirtualDropdown"] li {
            color: #1E293B !important;
        }
        
        /* Fix Radio Button Selected Text */
        .stRadio label p {
            color: #1E293B !important; 
            font-size: 16px;
        }
        
        /* --- BUTTON STYLING --- */
        .stButton > button {
            background: linear-gradient(90deg, #4F46E5 0%, #4338CA 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 600;
            transition: all 0.2s;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        .stButton > button:hover {
            background: linear-gradient(90deg, #4338CA 0%, #3730A3 100%);
            box-shadow: 0 6px 8px -1px rgba(0, 0, 0, 0.15);
            transform: translateY(-1px);
        }
        
        /* Secondary Button (Outline) */
        button[kind="secondary"] {
            background: transparent !important;
            border: 2px solid #4F46E5 !important;
            color: #4F46E5 !important;
        }

        /* --- METRIC CARDS --- */
        .metric-card {
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        
        /* Hide Streamlit Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Headers */
        h1, h2, h3 {
            color: #1E293B;
            font-weight: 700;
        }
        
        /* Success/Info Messages */
        .stSuccess, .stInfo, .stWarning, .stError {
            border-radius: 8px;
            border: none;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        </style>
    """, unsafe_allow_html=True)

# --- Helper Functions ---

def status_badge(status):
    colors = {
        "Pending": "#F59E0B",
        "In Progress": "#3B82F6",
        "Submitted": "#10B981",
        "Verified": "#059669",
        "Rejected": "#EF4444"
    }
    color = colors.get(status, "#6B7280")
    return f'<span style="background-color: {color}20; color: {color}; padding: 4px 12px; border-radius: 16px; font-size: 12px; font-weight: 600; border: 1px solid {color}40;">{status}</span>'

def priority_badge(priority):
    colors = {
        "High": "#EF4444",
        "Medium": "#F59E0B",
        "Low": "#10B981"
    }
    color = colors.get(priority, "#6B7280")
    return f'<span style="color: {color}; font-weight: 600;">{priority}</span>'

def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
        
