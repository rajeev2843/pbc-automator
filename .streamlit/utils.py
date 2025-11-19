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
        
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 0;
        }
        
        .stApp {
            background: transparent;
        }
        
        [data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
        }
        
        .main-card {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            margin: 20px auto;
            max-width: 1200px;
        }
        
        .stButton > button {
            background: linear-gradient(90deg, #6366F1 0%, #8B5CF6 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 14px 28px;
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        
        .status-badge {
            padding: 6px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 13px;
            display: inline-block;
        }
        
        .status-pending {
            background: #FEF3C7;
            color: #92400E;
        }
        
        .status-progress {
            background: #DBEAFE;
            color: #1E40AF;
        }
        
        .status-submitted {
            background: #D1FAE5;
            color: #065F46;
        }
        
        .status-verified {
            background: #D1FAE5;
            color: #065F46;
            border: 2px solid #10B981;
        }
        
        .status-rejected {
            background: #FEE2E2;
            color: #991B1B;
        }
        
        .pbc-item-card {
            background: white;
            border: 2px solid #E5E7EB;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }
        
        .pbc-item-card:hover {
            border-color: #6366F1;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
        }
        
        .priority-high {
            border-left: 5px solid #EF4444;
        }
        
        .priority-medium {
            border-left: 5px solid #F59E0B;
        }
        
        .priority-low {
            border-left: 5px solid #10B981;
        }
        
        .stTextInput > div > div > input,
        .stTextArea textarea,
        .stSelectbox > div > div {
            border-radius: 10px;
            border: 2px solid #E5E7EB;
            padding: 12px;
            font-size: 15px;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea textarea:focus {
            border-color: #6366F1;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }
        
        .upload-zone {
            border: 3px dashed #6366F1;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            background: #F9FAFB;
            transition: all 0.3s ease;
        }
        
        .upload-zone:hover {
            background: #F3F4F6;
            border-color: #8B5CF6;
        }
        
        h1, h2, h3 {
            color: #1F2937;
        }
        
        .hero-title {
            font-size: 48px;
            font-weight: 700;
            background: linear-gradient(90deg, #6366F1, #8B5CF6, #EC4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
        }
        
        .feature-card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
            text-align: center;
            transition: transform 0.3s ease;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
        }
        
        .icon-large {
            font-size: 48px;
            margin-bottom: 15px;
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #6366F1, #8B5CF6);
        }
        
        .doc-preview {
            background: #F9FAFB;
            border: 1px solid #E5E7EB;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
        }
        
        .ai-analysis-box {
            background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
            border-left: 4px solid #6366F1;
            padding: 20px;
            border-radius: 10px;
            margin: 15px 0;
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
