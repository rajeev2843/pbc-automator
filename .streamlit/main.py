import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import *
from gemini_ai import *
from utils import *
import io

# Initialize database
init_database()

# Page config
st.set_page_config(
    page_title="Smart Audit Room - PBC Automator",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply styling
apply_custom_styling()

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "landing"

# ============================================================================
# LANDING PAGE
# ============================================================================

def show_landing_page():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    # Hero Section
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown('<h1 class="hero-title">Smart Audit Room</h1>', unsafe_allow_html=True)
        st.markdown("""
        <h2 style='color: #6B7280; font-weight: 400; margin-bottom: 30px;'>
        Automate Your PBC Process with AI
        </h2>
        <p style='font-size: 18px; color: #4B5563; line-height: 1.8; margin-bottom: 30px;'>
        Transform your audit workflow with intelligent document management. 
        Generate comprehensive PBC lists from Trial Balance in seconds, 
        track submissions in real-time, and verify documents with AI-powered analysis.
        </p>
        """, unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🚀 Get Started", key="hero_signup", use_container_width=True):
                st.session_state.current_page = "signup"
                st.rerun()
        with col_btn2:
            if st.button("🔐 Sign In", key="hero_signin", use_container_width=True):
                st.session_state.current_page = "signin"
                st.rerun()
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 40px; border-radius: 20px; color: white; text-align: center;'>
            <div style='font-size: 64px; margin-bottom: 20px;'>📋</div>
            <h3 style='color: white; margin-bottom: 15px;'>Built for CAs</h3>
            <p style='font-size: 16px; opacity: 0.95;'>
            Designed specifically for Chartered Accountants and their clients 
            to streamline the audit documentation process.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Features Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center; margin-bottom: 40px;'>🌟 Powerful Features</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="icon-large">🤖</div>
            <h3>AI-Powered PBC Generation</h3>
            <p style='color: #6B7280; line-height: 1.6;'>
            Upload Trial Balance and get a comprehensive, intelligent PBC list 
            in seconds using Google Gemini AI.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="icon-large">📄</div>
            <h3>Smart Document Analysis</h3>
            <p style='color: #6B7280; line-height: 1.6;'>
            AI automatically analyzes uploaded documents, extracts key information, 
            and verifies completeness.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="icon-large">📊</div>
            <h3>Real-time Tracking</h3>
            <p style='color: #6B7280; line-height: 1.6;'>
            Monitor progress with interactive dashboards. Track pending items, 
            submissions, and verifications effortlessly.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# AUTHENTICATION PAGES
# ============================================================================

def show_signup_page():
    st.markdown('<div class="main-card" style="max-width: 600px;">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Create Account</h2>", unsafe_allow_html=True)
    
    role = st.selectbox("I am a:", ["Chartered Accountant", "Client"])
    role_enum = UserRole.CA if role == "Chartered Accountant" else UserRole.CLIENT
    
    full_name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")
    confirm_pass = st.text_input("Confirm Password", type="password")
    
    if role_enum == UserRole.CA:
        firm_name = st.text_input("Firm Name")
        mem_no = st.text_input("Membership Number")
    else:
        company_name = st.text_input("Company Name")
        gstin = st.text_input("GSTIN")
        ca_code = st.text_input("CA Invite Code (Ask your CA)")
    
    if st.button("Sign Up", use_container_width=True):
        if not email or not password or not full_name:
            st.error("Please fill all required fields")
        elif password != confirm_pass:
            st.error("Passwords do not match")
        else:
            db = get_session()
            try:
                # Check existing
                if db.query(User).filter(User.email == email).first():
                    st.error("Email already registered")
                else:
                    user = User(
                        email=email,
                        password_hash=hash_password(password),
                        full_name=full_name,
                        role=role_enum,
                        company_name=firm_name if role_enum == UserRole.CA else company_name
                    )
                    db.add(user)
                    db.flush()
                    
                    if role_enum == UserRole.CA:
                        profile = CAProfile(
                            user_id=user.user_id,
                            firm_name=firm_name,
                            membership_no=mem_no,
                            invite_code=generate_invite_code()
                        )
                        db.add(profile)
                    else:
                        # Link to CA via code
                        ca_profile = db.query(CAProfile).filter(CAProfile.invite_code == ca_code).first()
                        client_profile = ClientProfile(
                            user_id=user.user_id,
                            company_name=company_name,
                            gstin=gstin,
                            ca_id=ca_profile.ca_id if ca_profile else None
                        )
                        db.add(client_profile)
                    
                    db.commit()
                    st.success("Account created! Please sign in.")
                    st.session_state.current_page = "signin"
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
            finally:
                db.close()
                
    if st.button("Already have an account? Sign In", type="secondary", use_container_width=True):
        st.session_state.current_page = "signin"
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_signin_page():
    st.markdown('<div class="main-card" style="max-width: 500px;">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Sign In</h2>", unsafe_allow_html=True)
    
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")
    
    if st.button("Sign In", use_container_width=True):
        db = get_session()
        user = db.query(User).filter(User.email == email).first()
        
        if user and verify_password(password, user.password_hash):
            login_user(user.user_id, user.role)
            st.rerun()
        else:
            st.error("Invalid credentials")
        db.close()
            
    if st.button("Don't have an account? Sign Up", type="secondary", use_container_width=True):
        st.session_state.current_page = "signup"
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# CA DASHBOARD & FEATURES
# ============================================================================

def show_ca_dashboard():
    db = get_session()
    user = db.query(User).filter(User.user_id == st.session_state.user_id).first()
    ca_profile = user.ca_profile
    
    with st.sidebar:
        st.title(f"👨‍💼 {user.full_name}")
        st.caption(f"{ca_profile.firm_name}")
        st.divider()
        
        page = st.radio("Navigation", ["Dashboard", "My Clients", "Create Audit Project", "Review Documents"])
        
        st.divider()
        st.info(f"🔑 Invite Code: **{ca_profile.invite_code}**")
        if st.button("Logout"):
            logout_user()

    if page == "Dashboard":
        st.markdown(f"# 👋 Welcome back, {user.full_name}")
        
        # Stats
        clients_count = len(ca_profile.clients)
        projects = ca_profile.audit_projects
        pending_reviews = sum(1 for p in projects for item in p.pbc_items if item.status == PBCStatus.SUBMITTED)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total Clients</h3>
                <h1>{clients_count}</h1>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);">
                <h3>Active Audits</h3>
                <h1>{len(projects)}</h1>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #10B981 0%, #059669 100%);">
                <h3>Pending Reviews</h3>
                <h1>{pending_reviews}</h1>
            </div>
            """, unsafe_allow_html=True)
        
        st.subheader("Recent Activity")
        # Placeholder for activity feed
        st.info("No recent activity")

    elif page == "Create Audit Project":
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("🚀 Start New Audit")
        
        clients = ca_profile.clients
        if not clients:
            st.warning("No clients found. Share your invite code to add clients.")
        else:
            client_opts = {c.company_name: c.client_id for c in clients}
            selected_client = st.selectbox("Select Client", list(client_opts.keys()))
            
            proj_name = st.text_input("Project Name (e.g., Statutory Audit FY24-25)")
            
            uploaded_tb = st.file_uploader("Upload Trial Balance (Excel/CSV)", type=['xlsx', 'csv'])
            
            if st.button("Generate AI PBC List", use_container_width=True):
                if uploaded_tb and proj_name:
                    with st.spinner("🤖 AI is analyzing Trial Balance & generating PBC list..."):
                        # Process TB
                        if uploaded_tb.name.endswith('.csv'):
                            df = pd.read_csv(uploaded_tb)
                        else:
                            df = pd.read_excel(uploaded_tb)
                        
                        # Save Project
                        new_project = AuditProject(
                            ca_id=ca_profile.ca_id,
                            client_id=client_opts[selected_client],
                            project_name=proj_name,
                            financial_year="2024-25"
                        )
                        db.add(new_project)
                        db.commit()
                        
                        # Call Gemini
                        pbc_items = generate_pbc_from_trial_balance(df)
                        
                        # Save Items
                        for idx, item in enumerate(pbc_items):
                            new_item = PBCItem(
                                project_id=new_project.project_id,
                                item_number=idx+1,
                                category=item['category'],
                                item_description=item['description'],
                                why_needed=item['why_needed'],
                                priority=item['priority'],
                                ai_generated=True
                            )
                            db.add(new_item)
                        db.commit()
                        
                        st.success(f"Created project with {len(pbc_items)} AI-generated requirements!")
                        
        st.markdown("</div>", unsafe_allow_html=True)

    elif page == "Review Documents":
        st.subheader("🔍 Document Review")
        projects = ca_profile.audit_projects
        proj_opts = {p.project_name: p.project_id for p in projects}
        
        sel_proj = st.selectbox("Select Project", list(proj_opts.keys()))
        
        if sel_proj:
            proj = db.query(AuditProject).get(proj_opts[sel_proj])
            
            # Filter pending reviews
            pending_items = [item for item in proj.pbc_items if item.status == PBCStatus.SUBMITTED]
            
            if not pending_items:
                st.success("No pending documents to review!")
            else:
                for item in pending_items:
                    with st.expander(f"{item.category}: {item.item_description}"):
                        doc = item.documents[-1] # Get latest doc
                        st.markdown(f"**Uploaded File:** {doc.filename}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.info(f"🤖 **AI Analysis:**\n\n{doc.ai_analysis}")
                        with col2:
                            if st.button("✅ Approve", key=f"app_{doc.doc_id}"):
                                item.status = PBCStatus.VERIFIED
                                doc.is_verified = True
                                db.commit()
                                st.rerun()
                            
                            if st.button("❌ Reject", key=f"rej_{doc.doc_id}"):
                                item.status = PBCStatus.REJECTED
                                db.commit()
                                st.rerun()

    db.close()

# ============================================================================
# CLIENT DASHBOARD & FEATURES
# ============================================================================

def show_client_dashboard():
    db = get_session()
    user = db.query(User).filter(User.user_id == st.session_state.user_id).first()
    client_profile = user.client_profile
    
    with st.sidebar:
        st.title(f"🏢 {user.company_name}")
        if client_profile.linked_ca:
            st.caption(f"Auditor: {client_profile.linked_ca.firm_name}")
        st.divider()
        
        if st.button("Logout"):
            logout_user()

    # Main Area
    st.markdown(f"## 📂 Audit Workspace")
    
    projects = client_profile.audit_projects
    if not projects:
        st.info("No active audits. Your CA will initiate a project.")
    else:
        proj = projects[-1] # Latest project
        st.markdown(f"### Current Audit: {proj.project_name}")
        
        # Metrics
        total = len(proj.pbc_items)
        completed = sum(1 for i in proj.pbc_items if i.status == PBCStatus.VERIFIED)
        pending = total - completed
        progress = int((completed/total)*100) if total > 0 else 0
        
        st.progress(progress)
        st.caption(f"{progress}% Completed")
        
        # Filter
        filter_status = st.selectbox("Filter Items", ["All", "Pending", "Submitted", "Verified", "Rejected"])
        
        items = proj.pbc_items
        if filter_status != "All":
            items = [i for i in items if i.status.value == filter_status]
            
        for item in items:
            with st.expander(f"{status_badge(item.status.value)} {item.item_description}", expanded=(item.status == PBCStatus.PENDING)):
                st.markdown(f"**Why Needed:** {item.why_needed}")
                st.markdown(f"**Priority:** {priority_badge(item.priority)}", unsafe_allow_html=True)
                
                if item.status in [PBCStatus.PENDING, PBCStatus.REJECTED]:
                    uploaded_file = st.file_uploader(f"Upload Document for Item #{item.item_number}", key=f"up_{item.pbc_id}")
                    
                    if uploaded_file:
                        if st.button("📤 Upload & Analyze", key=f"btn_{item.pbc_id}"):
                            with st.spinner("🤖 AI is analyzing your document..."):
                                # Save file metadata
                                file_bytes = uploaded_file.read()
                                
                                # AI Analysis
                                analysis = analyze_uploaded_document(file_bytes, uploaded_file.name, item.item_description)
                                summary = analysis.get('summary', 'Analysis complete')
                                
                                new_doc = PBCDocument(
                                    pbc_id=item.pbc_id,
                                    filename=uploaded_file.name,
                                    file_size=len(file_bytes),
                                    file_type=uploaded_file.type,
                                    uploaded_by=user.user_id,
                                    ai_analysis=str(summary)
                                )
                                db.add(new_doc)
                                item.status = PBCStatus.SUBMITTED
                                db.commit()
                                st.success("Document uploaded and analyzed!")
                                st.rerun()
                
                elif item.status == PBCStatus.SUBMITTED:
                    st.info("✅ Document uploaded. Waiting for CA review.")
                    if item.documents:
                        st.markdown(f"**AI Analysis:** {item.documents[-1].ai_analysis}")

    db.close()

# ============================================================================
# MAIN ROUTER
# ============================================================================

def main():
    if not st.session_state.authenticated:
        if st.session_state.current_page == "landing":
            show_landing_page()
        elif st.session_state.current_page == "signin":
            show_signin_page()
        elif st.session_state.current_page == "signup":
            show_signup_page()
    else:
        if st.session_state.role == UserRole.CA:
            show_ca_dashboard()
        else:
            show_client_dashboard()

if __name__ == "__main__":
    main()
    
