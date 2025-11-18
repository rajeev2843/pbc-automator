import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu # REQUIRED: Install streamlit-option-menu
from database import *
from gemini_ai import *
from utils import *

# 1. CONFIGURATION
st.set_page_config(
    page_title="Smart Audit Room",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize DB & CSS
init_database()
apply_custom_styling()

# Session State
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'user_id' not in st.session_state: st.session_state.user_id = None
if 'role' not in st.session_state: st.session_state.role = None
if 'current_page' not in st.session_state: st.session_state.current_page = "landing"

# ============================================================================
# VIEWS
# ============================================================================

def show_landing_page():
    # Clean, Native Layout
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.markdown("# 📋 Smart Audit Room")
        st.markdown("### The AI-Powered PBC Automation Platform")
        st.markdown("""
        Stop chasing documents via email.  
        **Smart Audit Room** uses AI to generate requirements from Trial Balances, 
        verify uploaded documents, and track audit progress in real-time.
        """)
        
        st.markdown("---")
        
        # Action Buttons
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🚀 Get Started", use_container_width=True):
                st.session_state.current_page = "signup"
                st.rerun()
        with col_b:
            if st.button("🔐 Sign In", type="primary", use_container_width=True):
                st.session_state.current_page = "signin"
                st.rerun()

    with c2:
        # Feature Cards using Native Streamlit containers (No floating boxes)
        with st.container():
            st.info("**🤖 AI Analysis**\n\nUpload a Trial Balance and get an instant, tailored PBC checklist.")
        with st.container():
            st.success("**📄 Smart Verification**\n\nUploaded documents are auto-read and checked against requirements.")
        with st.container():
            st.warning("**⚖️ For CAs & Clients**\n\nA unified workspace for seamless collaboration.")

def show_auth_page(mode="signin"):
    # Center the form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Container with border for visibility
        with st.container(border=True):
            if mode == "signin":
                st.subheader("🔐 Sign In")
                email = st.text_input("Email Address")
                password = st.text_input("Password", type="password")
                
                if st.button("Login", type="primary", use_container_width=True):
                    db = get_session()
                    user = db.query(User).filter(User.email == email).first()
                    db.close()
                    if user and verify_password(password, user.password_hash):
                        login_user(user.user_id, user.role)
                        st.rerun()
                    else:
                        st.error("Invalid Email or Password")
                
                if st.button("Create New Account", use_container_width=True):
                    st.session_state.current_page = "signup"
                    st.rerun()
            
            else: # Signup
                st.subheader("🚀 Create Account")
                
                # Role Selection - Native Radio Button
                role_sel = st.radio("I am a:", ["Client", "Chartered Accountant"], horizontal=True)
                role_enum = UserRole.CA if role_sel == "Chartered Accountant" else UserRole.CLIENT
                
                name = st.text_input("Full Name")
                email = st.text_input("Email Address")
                pw = st.text_input("Password", type="password")
                
                # Conditional Inputs
                if role_enum == UserRole.CA:
                    st.markdown("---")
                    st.caption("CA Details")
                    firm = st.text_input("Firm Name")
                    mem_no = st.text_input("Membership No.")
                    company = None
                    gstin = None
                    code = None
                else:
                    st.markdown("---")
                    st.caption("Business Details")
                    company = st.text_input("Company Name")
                    gstin = st.text_input("GSTIN")
                    code = st.text_input("CA Invite Code (Optional)")
                    firm = None
                    mem_no = None
                
                if st.button("Register", type="primary", use_container_width=True):
                    if not email or not pw or not name:
                        st.error("Please fill required fields")
                    else:
                        # Registration Logic
                        db = get_session()
                        try:
                            if db.query(User).filter(User.email == email).first():
                                st.error("Email exists")
                            else:
                                u = User(email=email, password_hash=hash_password(pw), full_name=name, role=role_enum, company_name=firm if role_enum == UserRole.CA else company)
                                db.add(u)
                                db.flush()
                                
                                if role_enum == UserRole.CA:
                                    p = CAProfile(user_id=u.user_id, firm_name=firm, membership_no=mem_no, invite_code=generate_invite_code())
                                    db.add(p)
                                else:
                                    # Link CA if code provided
                                    ca = db.query(CAProfile).filter(CAProfile.invite_code == code).first() if code else None
                                    cp = ClientProfile(user_id=u.user_id, company_name=company, gstin=gstin, ca_id=ca.ca_id if ca else None)
                                    db.add(cp)
                                
                                db.commit()
                                st.success("Created! Please Login.")
                                st.session_state.current_page = "signin"
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                        finally:
                            db.close()
                
                if st.button("Back to Login", use_container_width=True):
                    st.session_state.current_page = "signin"
                    st.rerun()

def show_ca_dashboard():
    db = get_session()
    user = db.query(User).filter(User.user_id == st.session_state.user_id).first()
    
    # --- SLEEK SIDEBAR WITH OPTION MENU ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
        st.markdown(f"**{user.full_name}**")
        st.caption(f"Invite Code: {user.ca_profile.invite_code}")
        
        selected = option_menu(
            menu_title=None,
            options=["Dashboard", "Start Audit", "Review Docs", "Logout"],
            icons=["speedometer2", "rocket-takeoff", "file-earmark-check", "box-arrow-right"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "orange", "font-size": "18px"}, 
                "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#334155"},
                "nav-link-selected": {"background-color": "#4F46E5"},
            }
        )
    
    # --- MAIN CONTENT ---
    if selected == "Logout":
        logout_user()
        
    elif selected == "Dashboard":
        st.title("Practice Overview")
        clients = len(user.ca_profile.clients)
        audits = len(user.ca_profile.audit_projects)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Clients", clients)
        c2.metric("Active Audits", audits)
        c3.metric("Pending Reviews", "0") # Placeholder
        
        st.divider()
        if not user.ca_profile.clients:
            st.info(f"No clients yet. Give them this invite code: **{user.ca_profile.invite_code}**")

    elif selected == "Start Audit":
        st.subheader("Start New Audit")
        with st.container(border=True):
            clients = user.ca_profile.clients
            if not clients:
                st.warning("Add clients first.")
            else:
                c_names = {c.company_name: c.client_id for c in clients}
                sel_c = st.selectbox("Select Client", list(c_names.keys()))
                proj = st.text_input("Audit Name", "Statutory Audit FY24-25")
                
                # Sample Download
                st.download_button("📥 Download Sample CSV", "Account,Debit,Credit\nSales,0,50000\nRent,12000,0", "sample.csv")
                
                upl = st.file_uploader("Upload Trial Balance")
                if st.button("Generate PBC", type="primary"):
                    if upl:
                        st.success("AI Generating List... (Mock)")
                        # Add logic here
    
    elif selected == "Review Docs":
        st.subheader("Document Review")
        st.info("Select an active audit to review documents.")

    db.close()

def show_client_dashboard():
    db = get_session()
    user = db.query(User).filter(User.user_id == st.session_state.user_id).first()
    
    with st.sidebar:
        st.markdown(f"### {user.company_name}")
        
        selected = option_menu(
            menu_title=None,
            options=["My Audits", "Upload Docs", "Logout"],
            icons=["folder", "cloud-upload", "box-arrow-right"],
            default_index=0,
             styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#334155"},
                "nav-link-selected": {"background-color": "#4F46E5"},
            }
        )

    if selected == "Logout":
        logout_user()
    
    elif selected == "My Audits":
        st.title("Audit Workspace")
        projects = user.client_profile.audit_projects
        if not projects:
            st.info("No active audits started by your CA.")
        else:
            for p in projects:
                with st.expander(f"{p.project_name} ({p.financial_year})"):
                    st.write("Audit details here...")

    db.close()

# ============================================================================
# MAIN CONTROLLER
# ============================================================================

def main():
    if not st.session_state.authenticated:
        if st.session_state.current_page == "landing":
            show_landing_page()
        elif st.session_state.current_page in ["signin", "signup"]:
            show_auth_page(st.session_state.current_page)
    else:
        if st.session_state.role == UserRole.CA:
            show_ca_dashboard()
        else:
            show_client_dashboard()

if __name__ == "__main__":
    main()
                    
