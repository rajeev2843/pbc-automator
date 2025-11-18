import streamlit as st
import bcrypt
import secrets
from datetime import datetime
from database import *

# Authentication Helpers
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

# --- VISUAL STYLING ---
def apply_custom_styling():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        /* 1. INPUT VISIBILITY FIX (Crucial) */
        .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            background-color: #FFFFFF !important;
            color: #1E293B !important;
            border: 1px solid #94A3B8 !important; /* Visible Grey Border */
            border-radius: 6px !important;
        }
        
        /* Focus state for inputs */
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #4F46E5 !important;
            box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.2) !important;
        }
        
        /* Labels for inputs */
        label {
            color: #1E293B !important;
            font-weight: 600 !important;
            font-size: 14px !important;
        }

        /* 2. BUTTON STYLING */
        .stButton > button {
            width: 100%;
            background-color: #4F46E5;
            color: white;
            border-radius: 6px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }
        .stButton > button:hover {
            background-color: #4338CA;
            color: white;
            border-color: #4338CA;
        }
        /* Secondary Button Style */
        button[kind="secondary"] {
            background-color: white !important;
            color: #4F46E5 !important;
            border: 1px solid #4F46E5 !important;
        }

        /* 3. REMOVE DEFAULT PADDING for cleaner look */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* 4. HIDE STREAMLIT ELEMENTS */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* 5. METRIC CARDS */
        div[data-testid="stMetric"] {
            background-color: white;
            border: 1px solid #E2E8F0;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        }
        
        /* 6. SIDEBAR FIXES */
        section[data-testid="stSidebar"] {
            background-color: #0F172A; /* Dark Navy */
        }
        </style>
    """, unsafe_allow_html=True)

def status_badge(status):
    colors = {
        "Pending": "#F59E0B", "In Progress": "#3B82F6", 
        "Submitted": "#10B981", "Verified": "#059669", "Rejected": "#EF4444"
    }
    c = colors.get(status, "#6B7280")
    return f":{c}[**{status}**]"

def format_file_size(size_bytes):
    if size_bytes < 1024: return f"{size_bytes} B"
    elif size_bytes < 1024**2: return f"{size_bytes/1024:.1f} KB"
    else: return f"{size_bytes/(1024**2):.1f} MB"
        
