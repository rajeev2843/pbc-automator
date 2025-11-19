import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import *
from gemini_ai import *
from utils import *
import io
import json

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
            <h3>Real-Time Progress Tracking</h3>
            <p style='color: #6B7280; line-height: 1.6;'>
            Monitor submission status with live dashboards. Get instant notifications 
            and automated reminders.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="icon-large">👥</div>
            <h3>Multi-Client Management</h3>
            <p style='color: #6B7280; line-height: 1.6;'>
            CAs can manage multiple clients from one dashboard. 
            Clients only see their own projects.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="icon-large">🔒</div>
            <h3>Secure & Compliant</h3>
            <p style='color: #6B7280; line-height: 1.6;'>
            Bank-grade security with audit trails. All actions logged 
            for compliance and accountability.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="icon-large">⚡</div>
            <h3>Lightning Fast</h3>
            <p style='color: #6B7280; line-height: 1.6;'>
            Save 10+ hours per audit. What took days now takes minutes 
            with intelligent automation.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # How It Works
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center; margin-bottom: 40px;'>🔄 How It Works</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div style='background: #F9FAFB; padding: 30px; border-radius: 15px; margin-bottom: 20px;'>
            <h3 style='color: #6366F1;'>👨‍💼 For CAs</h3>
            <ol style='line-height: 2; color: #4B5563; font-size: 16px;'>
                <li>Create audit project for your client</li>
                <li>Upload Trial Balance (Excel/CSV)</li>
                <li>AI generates comprehensive PBC list</li>
                <li>Review, customize, and assign to client</li>
                <li>Track progress and verify documents</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: #F9FAFB; padding: 30px; border-radius: 15px; margin-bottom: 20px;'>
            <h3 style='color: #8B5CF6;'>🏢 For Clients</h3>
            <ol style='line-height: 2; color: #4B5563; font-size: 16px;'>
                <li>Receive PBC list from your CA</li>
                <li>See exactly what's needed and why</li>
                <li>Upload documents with drag-and-drop</li>
                <li>AI analyzes and confirms completeness</li>
                <li>Get real-time feedback from CA</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # CTA Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="main-card" style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); text-align: center; padding: 60px;'>
        <h2 style='color: white; font-size: 36px; margin-bottom: 20px;'>
        Ready to Transform Your Audit Process?
        </h2>
        <p style='color: white; font-size: 18px; opacity: 0.95; margin-bottom: 30px;'>
        Join forward-thinking CAs who've already automated their PBC workflow
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🎯 Start Free Today", key="cta_button", use_container_width=True):
            st.session_state.current_page = "signup"
            st.rerun()
    
    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; color: white; padding: 20px;'>
        <p style='font-size: 14px; opacity: 0.8;'>
        Built for ICAI Aurathon 2025 | Powered by Google Gemini AI
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# SIGN UP PAGE
# ============================================================================

def show_signup_page():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center; color: #6366F1;'>Create Your Account</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6B7280; margin-bottom: 30px;'>Join Smart Audit Room today</p>", unsafe_allow_html=True)
        
        # Role selection
        role = st.radio(
            "I am a:",
            options=["Chartered Accountant (CA)", "Client"],
            horizontal=True,
            key="signup_role"
        )
        
        is_ca = role == "Chartered Accountant (CA)"
        
        with st.form("signup_form"):
            # Common fields
            full_name = st.text_input("Full Name *", placeholder="Enter your full name")
            email = st.text_input("Email Address *", placeholder="your@email.com")
            password = st.text_input("Password *", type="password", placeholder="Minimum 8 characters")
            password_confirm = st.text_input("Confirm Password *", type="password", placeholder="Re-enter password")
            
            # CA-specific fields
            if is_ca:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**CA Details**")
                firm_name = st.text_input("Firm Name *", placeholder="e.g., ABC & Associates")
                membership_no = st.text_input("ICAI Membership Number *", placeholder="e.g., 123456")
                firm_registration_no = st.text_input("Firm Registration Number (Optional)", placeholder="e.g., 123456W")  # ← ADD THIS LINE
                company_name = None
                gstin = None
            else:
                firm_name = None
                membership_no = None
                firm_registration_no = None
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**Company Details**")
                company_name = st.text_input("Company Name *", placeholder="Your company name")
                gstin = st.text_input("GSTIN (Optional)", placeholder="15-digit GSTIN")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("🚀 Create Account", use_container_width=True)
            
            if submit:
                # Validation
                if not all([full_name, email, password, password_confirm]):
                    st.error("❌ Please fill in all required fields")
                elif password != password_confirm:
                    st.error("❌ Passwords don't match")
                elif len(password) < 8:
                    st.error("❌ Password must be at least 8 characters")
                elif is_ca and not all([firm_name, membership_no]):
                    st.error("❌ Please provide CA details")
                elif not is_ca and not company_name:
                    st.error("❌ Please provide company name")
                else:
                    # Create account
                    db = get_session()
                    try:
                        # Check if email exists
                        existing = db.query(User).filter(User.email == email.lower()).first()
                        if existing:
                            st.error("❌ Email already registered. Please sign in.")
                        else:
                            # Create user
                            new_user = User(
                                email=email.lower(),
                                password_hash=hash_password(password),
                                full_name=full_name,
                                role=UserRole.CA if is_ca else UserRole.CLIENT,
                                company_name=company_name if not is_ca else firm_name
                            )
                            db.add(new_user)
                            db.flush()
                            
                            # Create profile
                            if is_ca:
                                ca_profile = CAProfile(
                                    user_id=new_user.user_id,
                                    firm_name=firm_name,
                                    membership_no=membership_no,
                                    firm_registration_no=firm_registration_no if firm_registration_no else None,
                                    invite_code=generate_invite_code()
                                )
                                db.add(ca_profile)
                            else:
                                client_profile = ClientProfile(
                                    user_id=new_user.user_id,
                                    company_name=company_name,
                                    gstin=gstin if gstin else None
                                )
                                db.add(client_profile)
                            
                            db.commit()
                            
                            st.success("✅ Account created successfully!")
                            st.balloons()
                            st.info("Redirecting to sign in...")
                            
                            import time
                            time.sleep(2)
                            st.session_state.current_page = "signin"
                            st.rerun()
                    
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Error: {str(e)}")
                    finally:
                        db.close()
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_back1, col_back2 = st.columns(2)
        with col_back1:
            if st.button("← Back to Home", key="back_home", use_container_width=True):
                st.session_state.current_page = "landing"
                st.rerun()
        with col_back2:
            if st.button("Already have account? Sign In →", key="goto_signin", use_container_width=True):
                st.session_state.current_page = "signin"
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# SIGN IN PAGE
# ============================================================================

def show_signin_page():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center; color: #6366F1;'>Welcome Back</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6B7280; margin-bottom: 30px;'>Sign in to continue</p>", unsafe_allow_html=True)
        
        with st.form("signin_form"):
            email = st.text_input("Email Address", placeholder="your@email.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("🔐 Sign In", use_container_width=True)
            
            if submit:
                if not email or not password:
                    st.error("❌ Please enter both email and password")
                else:
                    db = get_session()
                    try:
                        user = db.query(User).filter(User.email == email.lower()).first()
                        
                        if not user:
                            st.error("❌ Account not found. Please sign up first.")
                        elif not verify_password(password, user.password_hash):
                            st.error("❌ Incorrect password")
                        elif not user.is_active:
                            st.error("❌ Account is deactivated. Contact support.")
                        else:
                            # Successful login
                            login_user(user.user_id, user.role.value)
                            st.success(f"✅ Welcome back, {user.full_name}!")
                            
                            import time
                            time.sleep(1)
                            st.rerun()
                    
                    except Exception as e:
                        st.error(f"❌ Login error: {str(e)}")
                    finally:
                        db.close()
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_back1, col_back2 = st.columns(2)
        with col_back1:
            if st.button("← Back to Home", key="back_home_signin", use_container_width=True):
                st.session_state.current_page = "landing"
                st.rerun()
        with col_back2:
            if st.button("Don't have account? Sign Up →", key="goto_signup", use_container_width=True):
                st.session_state.current_page = "signup"
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# CA DASHBOARD
# ============================================================================

def show_ca_dashboard():
    db = get_session()
    
    # Get CA profile
    user = db.query(User).filter(User.user_id == st.session_state.user_id).first()
    ca_profile = db.query(CAProfile).filter(CAProfile.user_id == st.session_state.user_id).first()
    
    if not ca_profile:
        st.error("CA Profile not found")
        db.close()
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👨‍💼 {user.full_name}")
        st.markdown(f"**{ca_profile.firm_name}**")
        st.markdown(f"**ICAI Membership:** {ca_profile.membership_no}")
    if hasattr(ca_profile, 'firm_registration_no') and ca_profile.firm_registration_no:
        st.markdown(f"**Firm Registration:** {ca_profile.firm_registration_no}")
    
    # Invite Code in sidebar
    with st.expander("🔗 Your Invite Code"):
        st.code(ca_profile.invite_code, language=None)
        if st.button("📋 Copy Code", key="copy_invite_sidebar", use_container_width=True):
            st.toast("✅ Copied to clipboard!")
    
    st.divider()
    
    menu = st.radio(
        "Navigation",
        ["📊 Dashboard", "📁 Projects", "➕ New Project", "👥 My Clients", "⚙️ Settings"],
        label_visibility="collapsed"
    )
        
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        logout_user()
    
    # Main content based on menu
    if menu == "📊 Dashboard":
        show_ca_dashboard_home(db, ca_profile)
    elif menu == "📁 Projects":
        show_ca_projects(db, ca_profile)
    elif menu == "➕ New Project":
        show_ca_new_project(db, ca_profile)
    elif menu == "👥 My Clients":
        show_ca_clients(db, ca_profile)
    elif menu == "⚙️ Settings":
        show_ca_settings(db, ca_profile)
    
    db.close()

def show_ca_dashboard_home(db, ca_profile):
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("# 📊 Dashboard")
    st.markdown("---")
    
    # Get statistics
    projects = db.query(AuditProject).filter(AuditProject.ca_id == ca_profile.ca_id).all()
    clients = db.query(ClientProfile).filter(ClientProfile.ca_id == ca_profile.ca_id).all()
    
    active_projects = [p for p in projects if p.status == "Active"]
    
    total_pbc_items = 0
    completed_pbc_items = 0
    for project in active_projects:
        pbc_items = db.query(PBCItem).filter(PBCItem.project_id == project.project_id).all()
        total_pbc_items += len(pbc_items)
        completed_pbc_items += sum(1 for item in pbc_items if item.status == PBCStatus.VERIFIED)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style='font-size: 40px; margin-bottom: 10px;'>👥</div>
            <div style='font-size: 32px; font-weight: 700;'>{}</div>
            <div style='opacity: 0.9; margin-top: 5px;'>Total Clients</div>
        </div>
        """.format(len(clients)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style='font-size: 40px; margin-bottom: 10px;'>📁</div>
            <div style='font-size: 32px; font-weight: 700;'>{}</div>
            <div style='opacity: 0.9; margin-top: 5px;'>Active Projects</div>
        </div>
        """.format(len(active_projects)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style='font-size: 40px; margin-bottom: 10px;'>📋</div>
            <div style='font-size: 32px; font-weight: 700;'>{}</div>
            <div style='opacity: 0.9; margin-top: 5px;'>Total PBC Items</div>
        </div>
        """.format(total_pbc_items), unsafe_allow_html=True)
    
    with col4:
        completion_rate = int((completed_pbc_items / total_pbc_items * 100)) if total_pbc_items > 0 else 0
        st.markdown("""
        <div class="metric-card">
            <div style='font-size: 40px; margin-bottom: 10px;'>✅</div>
            <div style='font-size: 32px; font-weight: 700;'>{}%</div>
            <div style='opacity: 0.9; margin-top: 5px;'>Completion Rate</div>
        </div>
        """.format(completion_rate), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Recent projects
    st.markdown("### 📁 Recent Projects")
    
    if not projects:
        st.info("No projects yet. Create your first project to get started!")
    else:
        for project in projects[:5]:
            client = db.query(ClientProfile).filter(ClientProfile.client_id == project.client_id).first()
            pbc_items = db.query(PBCItem).filter(PBCItem.project_id == project.project_id).all()
            completed = sum(1 for item in pbc_items if item.status == PBCStatus.VERIFIED)
            total = len(pbc_items)
            progress = int((completed / total * 100)) if total > 0 else 0
            
            with st.expander(f"📂 {project.project_name} - {client.company_name if client else 'Unknown'}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Financial Year:** {project.financial_year}")
                    st.markdown(f"**Audit Type:** {project.audit_type}")
                    st.markdown(f"**Status:** {status_badge(project.status)}", unsafe_allow_html=True)
                    st.markdown(f"**Progress:** {completed}/{total} PBC items completed")
                    st.progress(progress / 100)
                
                with col2:
                    if st.button("View Details", key=f"view_{project.project_id}"):
                        st.session_state.selected_project = project.project_id
                        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_ca_projects(db, ca_profile):
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("# 📁 All Projects")
    st.markdown("---")
    
    projects = db.query(AuditProject).filter(AuditProject.ca_id == ca_profile.ca_id).all()
    
    if not projects:
        st.info("No projects yet. Create your first project!")
        if st.button("➕ Create New Project"):
            st.session_state.current_page = "new_project"
            st.rerun()
    else:
        # Filter
        col1, col2 = st.columns([3, 1])
        with col1:
            search = st.text_input("🔍 Search projects", placeholder="Search by project name or client...")
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Completed", "Archived"])
        
        # Display projects
        filtered_projects = projects
        if status_filter != "All":
            filtered_projects = [p for p in projects if p.status == status_filter]
        if search:
            filtered_projects = [p for p in filtered_projects if search.lower() in p.project_name.lower()]
        
        for project in filtered_projects:
            client = db.query(ClientProfile).filter(ClientProfile.client_id == project.client_id).first()
            pbc_items = db.query(PBCItem).filter(PBCItem.project_id == project.project_id).all()
            completed = sum(1 for item in pbc_items if item.status == PBCStatus.VERIFIED)
            total = len(pbc_items)
            
            st.markdown(f"""
            <div class="pbc-item-card">
                <h3>{project.project_name}</h3>
                <p><strong>Client:</strong> {client.company_name if client else 'Unknown'}</p>
                <p><strong>FY:</strong> {project.financial_year} | <strong>Type:</strong> {project.audit_type}</p>
                <p>{status_badge(project.status)}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.progress(completed / total if total > 0 else 0, text=f"{completed}/{total} PBC items")
            with col2:
                st.markdown(f"Created: {project.created_at.strftime('%d %b %Y')}")
            with col3:
                if st.button("Open →", key=f"open_{project.project_id}"):
                    st.session_state.selected_project = project.project_id
                    st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_ca_new_project(db, ca_profile):
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("# ➕ Create New Audit Project")
    st.markdown("---")
    
    # Get clients
    clients = db.query(ClientProfile).filter(ClientProfile.ca_id == ca_profile.ca_id).all()
    
    if not clients:
        st.warning("⚠️ You don't have any clients yet. Clients must sign up and link to your firm using your invite code.")
        st.info(f"**Your Invite Code:** `{ca_profile.invite_code}`")
        st.markdown("Share this code with your clients during their signup process.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    with st.form("new_project_form"):
        st.markdown("### 📋 Project Details")
        
        # Client selection
        client_options = {f"{c.company_name} ({c.gstin or 'No GSTIN'})": c.client_id for c in clients}
        selected_client_name = st.selectbox("Select Client *", options=list(client_options.keys()))
        selected_client_id = client_options[selected_client_name]
        
        col1, col2 = st.columns(2)
        with col1:
            project_name = st.text_input("Project Name *", placeholder="e.g., Statutory Audit FY 2024-25")
            audit_type = st.selectbox("Audit Type *", ["Statutory Audit", "Tax Audit", "Internal Audit", "GST Audit", "Stock Audit"])
        with col2:
            financial_year = st.text_input("Financial Year *", placeholder="e.g., 2024-25")
        
        st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 📊 Upload Trial Balance")

# ADD THIS SECTION:
col_info1, col_info2 = st.columns([3, 1])
with col_info1:
    st.markdown("Upload Trial Balance to auto-generate PBC list using AI")
with col_info2:
    # Create sample file
    sample_df = pd.DataFrame({
        'Account Name': ['Cash in Hand', 'Bank - SBI', 'Sales Revenue', 'Rent Expense', 'Trade Payables'],
        'Debit': [50000, 250000, 0, 35000, 0],
        'Credit': [0, 0, 500000, 0, 75000]
    })
    
    # CSV download
    csv = sample_df.to_csv(index=False)
    st.download_button(
        label="📥 Sample CSV",
        data=csv,
        file_name="sample_trial_balance.csv",
        mime="text/csv",
        use_container_width=True,
        key="download_sample_csv"
    )

# Excel download
try:
    from io import BytesIO
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        sample_df.to_excel(writer, index=False, sheet_name='Trial Balance')
    excel_data = buffer.getvalue()
    
    st.download_button(
        label="📥 Sample Excel",
        data=excel_data,
        file_name="sample_trial_balance.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        key="download_sample_excel"
    )
except:
    pass  # If openpyxl not available, skip Excel download

tb_file = st.file_uploader(
            "Trial Balance (Excel/CSV)",
            type=['xlsx', 'xls', 'csv'],
            help="Upload Trial Balance with columns: Account Name, Debit, Credit"
        )
        
    

def show_ca_clients(db, ca_profile):
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("# 👥 My Clients")
    st.markdown("---")
    
    clients = db.query(ClientProfile).filter(st.markdown("<br>", unsafe_allow_html=True)
    submit = st.form_submit_button("🚀 Create Project & Generate PBC", use_container_width=True)
        
        if submit:
            if not all([project_name, financial_year, tb_file]):
                st.error("❌ Please fill all required fields and upload Trial Balance")
            else:
                try:
                    # Read Trial Balance
                    if tb_file.name.endswith('.csv'):
                        tb_df = pd.read_csv(tb_file)
                    else:
                        tb_df = pd.read_excel(tb_file)
                    
                    # Validate columns
                    required_cols = ['Account Name', 'Debit', 'Credit']
                    if not all(col in tb_df.columns for col in required_cols):
                        st.error(f"❌ Trial Balance must have columns: {', '.join(required_cols)}")
                    else:
                        with st.spinner("🤖 Creating project and generating PBC list with AI..."):
                            # Create project
                            new_project = AuditProject(
                                ca_id=ca_profile.ca_id,
                                client_id=selected_client_id,
                                project_name=project_name,
                                financial_year=financial_year,
                                audit_type=audit_type,
                                status="Active"
                            )
                            db.add(new_project)
                            db.flush()
                            
                            # Save Trial Balance
                            tb_record = TrialBalance(
                                project_id=new_project.project_id,
                                filename=tb_file.name,
                                total_debit=tb_df['Debit'].sum(),
                                total_credit=tb_df['Credit'].sum(),
                                account_count=len(tb_df)
                            )
                            db.add(tb_record)
                            
                            # Generate PBC list using Gemini AI
                            pbc_items = generate_pbc_from_trial_balance(tb_df, audit_type, financial_year)
                            
                            # Save PBC items
                            for idx, item in enumerate(pbc_items, 1):
                                pbc_item = PBCItem(
                                    project_id=new_project.project_id,
                                    item_number=idx,
                                    category=item.get('category', 'General'),
                                    item_description=item.get('description', ''),
                                    why_needed=item.get('why_needed', ''),
                                    priority=item.get('priority', 'Medium'),
                                    status=PBCStatus.PENDING,
                                    ai_generated=True
                                )
                                db.add(pbc_item)
                            
                            db.commit()
                            
                            st.success(f"✅ Project created successfully with {len(pbc_items)} PBC items!")
                            st.balloons()
                            
                            import time
                            time.sleep(2)
                            st.session_state.selected_project = new_project.project_id
                            st.rerun()
                
                except Exception as e:
                    db.rollback()
                    st.error(f"❌ Error: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    ClientProfile.ca_id == ca_profile.ca_id).all()
    
    # Invite code section
    st.markdown("### 🔗 Your Invite Code")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.code(ca_profile.invite_code, language=None)
    with col2:
        if st.button("📋 Copy", use_container_width=True):
            st.success("Copied to clipboard!")
    
    st.info("Share this code with clients during their signup. They'll be automatically linked to your firm.")
    
    st.markdown("---")
    st.markdown(f"### 📊 Total Clients: {len(clients)}")
    
    if not clients:
        st.info("No clients yet. Share your invite code to get started!")
    else:
        ```python
        for client in clients:
            user = db.query(User).filter(User.user_id == client.user_id).first()
            projects = db.query(AuditProject).filter(AuditProject.client_id == client.client_id).all()
    
            # Use container instead of expander to avoid text overlap
            st.markdown(f"""
            <div class="pbc-item-card">
                <h3>🏢 {client.company_name}</h3>
            </div>
            """, unsafe_allow_html=True)
     
            col1, col2 = st.columns(2)
    
            with col1:
                st.markdown(f"**Contact:** {user.full_name if user else 'N/A'}")
                st.markdown(f"**Email:** {user.email if user else 'N/A'}")
                st.markdown(f"**GSTIN:** {client.gstin or 'Not provided'}")
    
            with col2:
                st.markdown(f"**Total Projects:** {len(projects)}")
                active_projects = [p for p in projects if p.status == "Active"]
                st.markdown(f"**Active Projects:** {len(active_projects)}")
                st.markdown(f"**Joined:** {user.created_at.strftime('%d %b %Y') if user else 'N/A'}")
    
            if projects:
                with st.expander("📂 View Recent Projects"):
                    for project in projects[:5]:
                        st.markdown(f"• **{project.project_name}** ({project.financial_year}) - {project.status}")
    
            st.markdown("<br>", unsafe_allow_html=True)

def show_ca_settings(db, ca_profile):
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("# ⚙️ Settings")
    st.markdown("---")
    
    user = db.query(User).filter(User.user_id == st.session_state.user_id).first()
    
    tab1, tab2 = st.tabs(["Profile", "Security"])
    
    with tab1:
        st.markdown("### 👤 Profile Information")
        with st.form("profile_form"):
            full_name = st.text_input("Full Name", value=user.full_name)
            firm_name = st.text_input("Firm Name", value=ca_profile.firm_name)
            membership_no = st.text_input("Membership Number", value=ca_profile.membership_no, disabled=True)
            
            if st.form_submit_button("💾 Save Changes"):
                try:
                    user.full_name = full_name
                    ca_profile.firm_name = firm_name
                    db.commit()
                    st.success("✅ Profile updated successfully!")
                except Exception as e:
                    db.rollback()
                    st.error(f"❌ Error: {str(e)}")
    
    with tab2:
        st.markdown("### 🔒 Security")
        with st.form("password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("🔑 Change Password"):
                if not verify_password(current_password, user.password_hash):
                    st.error("❌ Current password is incorrect")
                elif new_password != confirm_password:
                    st.error("❌ New passwords don't match")
                elif len(new_password) < 8:
                    st.error("❌ Password must be at least 8 characters")
                else:
                    try:
                        user.password_hash = hash_password(new_password)
                        db.commit()
                        st.success("✅ Password changed successfully!")
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Error: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# CLIENT DASHBOARD
# ============================================================================

def show_client_dashboard():
    db = get_session()
    
    # Get client profile
    user = db.query(User).filter(User.user_id == st.session_state.user_id).first()
    client_profile = db.query(ClientProfile).filter(ClientProfile.user_id == st.session_state.user_id).first()
    
    if not client_profile:
        st.error("Client Profile not found")
        db.close()
        return
    
    # Check if linked to CA
    if not client_profile.ca_id:
        show_client_onboarding(db, client_profile)
        db.close()
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 🏢 {client_profile.company_name}")
        st.markdown(f"**{user.full_name}**")
        
        ca = db.query(CAProfile).filter(CAProfile.ca_id == client_profile.ca_id).first()
        if ca:
            st.markdown(f"**CA Firm:** {ca.firm_name}")
        
        st.divider()
        
        menu = st.radio(
            "Navigation",
            ["📊 Dashboard", "📋 My PBC Lists", "⚙️ Settings"],
            label_visibility="collapsed"
        )
        
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
    
    # Main content
    if menu == "📊 Dashboard":
        show_client_dashboard_home(db, client_profile)
    elif menu == "📋 My PBC Lists":
        show_client_pbc_lists(db, client_profile)
    elif menu == "⚙️ Settings":
        show_client_settings(db, client_profile)
    
    db.close()

def show_client_onboarding(db, client_profile):
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("# 🎯 Link to Your CA")
    st.markdown("---")
    
    st.info("To access PBC lists and submit documents, you need to link your account to your Chartered Accountant.")
    
    st.markdown("### Enter CA Invite Code")
    st.markdown("Your CA will provide you with an invite code. Enter it below to link your account.")
    
    with st.form("link_ca_form"):
        invite_code = st.text_input("CA Invite Code", placeholder="e.g., CA-A1B2C3D4")
        
        submit = st.form_submit_button("🔗 Link to CA", use_container_width=True)
        
        if submit:
            if not invite_code:
                st.error("❌ Please enter an invite code")
            else:
                ca = db.query(CAProfile).filter(CAProfile.invite_code == invite_code.upper()).first()
                
                if not ca:
                    st.error("❌ Invalid invite code. Please check and try again.")
                else:
                    try:
                        client_profile.ca_id = ca.ca_id
                        db.commit()
                        
                        st.success(f"✅ Successfully linked to {ca.firm_name}!")
                        st.balloons()
                        
                        import time
                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Error: {str(e)}")
    
    st.markdown("---")
    st.markdown("**Don't have an invite code?**")
    st.markdown("Contact your CA and ask them to share their invite code with you.")
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_client_dashboard_home(db, client_profile):
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("# 📊 Dashboard")
    st.markdown("---")
    
    # Get projects
    projects = db.query(AuditProject).filter(AuditProject.client_id == client_profile.client_id).all()
    
    # Calculate statistics
    total_pbc = 0
    pending_pbc = 0
    in_progress_pbc = 0
    completed_pbc = 0
    
    for project in projects:
        pbc_items = db.query(PBCItem).filter(PBCItem.project_id == project.project_id).all()
        total_pbc += len(pbc_items)
        pending_pbc += sum(1 for item in pbc_items if item.status == PBCStatus.PENDING)
        in_progress_pbc += sum(1 for item in pbc_items if item.status == PBCStatus.IN_PROGRESS)
        completed_pbc += sum(1 for item in pbc_items if item.status == PBCStatus.VERIFIED)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style='font-size: 40px; margin-bottom: 10px;'>📁</div>
            <div style='font-size: 32px; font-weight: 700;'>{}</div>
            <div style='opacity: 0.9; margin-top: 5px;'>Active Projects</div>
        </div>
        """.format(len([p for p in projects if p.status == "Active"])), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style='font-size: 40px; margin-bottom: 10px;'>⏳</div>
            <div style='font-size: 32px; font-weight: 700;'>{}</div>
            <div style='opacity: 0.9; margin-top: 5px;'>Pending Items</div>
        </div>
        """.format(pending_pbc), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style='font-size: 40px; margin-bottom: 10px;'>📤</div>
            <div style='font-size: 32px; font-weight: 700;'>{}</div>
            <div style='opacity: 0.9; margin-top: 5px;'>In Progress</div>
        </div>
        """.format(in_progress_pbc), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div style='font-size: 40px; margin-bottom: 10px;'>✅</div>
            <div style='font-size: 32px; font-weight: 700;'>{}</div>
            <div style='opacity: 0.9; margin-top: 5px;'>Completed</div>
        </div>
        """.format(completed_pbc), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Projects overview
    st.markdown("### 📂 Your Projects")
    
    if not projects:
        st.info("No projects yet. Your CA will create projects and assign PBC lists to you.")
    else:
        for project in projects:
            ca = db.query(CAProfile).filter(CAProfile.ca_id == project.ca_id).first()
            pbc_items = db.query(PBCItem).filter(PBCItem.project_id == project.project_id).all()
            completed = sum(1 for item in pbc_items if item.status == PBCStatus.VERIFIED)
            total = len(pbc_items)
            progress = int((completed / total * 100)) if total > 0 else 0
            
            with st.expander(f"📂 {project.project_name}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**CA Firm:** {ca.firm_name if ca else 'N/A'}")
                    st.markdown(f"**Financial Year:** {project.financial_year}")
                    st.markdown(f"**Audit Type:** {project.audit_type}")
                    st.markdown(f"**Status:** {status_badge(project.status)}", unsafe_allow_html=True)
                    st.markdown(f"**Your Progress:** {completed}/{total} items completed")
                    st.progress(progress / 100)
                
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("View PBC List →", key=f"view_pbc_{project.project_id}"):
                        st.session_state.selected_client_project = project.project_id
                        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_client_pbc_lists(db, client_profile):
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    # Project selection
    projects = db.query(AuditProject).filter(AuditProject.client_id == client_profile.client_id).all()
    
    if not projects:
        st.info("No projects available. Your CA will create projects for you.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    project_options = {f"{p.project_name} ({p.financial_year})": p.project_id for p in projects}
    selected_project_name = st.selectbox("Select Project", options=list(project_options.keys()))
    selected_project_id = project_options[selected_project_name]
    
    project = db.query(AuditProject).filter(AuditProject.project_id == selected_project_id).first()
    
    st.markdown(f"# 📋 PBC List: {project.project_name}")
    st.markdown("---")
    
    # Get PBC items
    pbc_items = db.query(PBCItem).filter(PBCItem.project_id == selected_project_id).order_by(PBCItem.item_number).all()
    
    # Progress overview
    completed = sum(1 for item in pbc_items if item.status == PBCStatus.VERIFIED)
    total = len(pbc_items)
    progress = int((completed / total * 100)) if total > 0 else 0
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(progress / 100, text=f"Overall Progress: {completed}/{total} items completed ({progress}%)")
    with col2:
        if progress == 100:
            st.success("🎉 All Done!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Filter tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 All Items", "⏳ Pending", "📤 In Progress", "✅ Completed"])
    
    with tab1:
        display_pbc_items_for_client(db, pbc_items, None)
    
    with tab2:
        pending_items = [item for item in pbc_items if item.status == PBCStatus.PENDING]
        display_pbc_items_for_client(db, pending_items, PBCStatus.PENDING)
    
    with tab3:
        in_progress_items = [item for item in pbc_items if item.status == PBCStatus.IN_PROGRESS]
        display_pbc_items_for_client(db, in_progress_items, PBCStatus.IN_PROGRESS)
    
    with tab4:
        completed_items = [item for item in pbc_items if item.status in [PBCStatus.SUBMITTED, PBCStatus.VERIFIED]]
        display_pbc_items_for_client(db, completed_items, None)
    
    st.markdown("</div>", unsafe_allow_html=True)

def display_pbc_items_for_client(db, pbc_items, filter_status):
    if not pbc_items:
        st.info("No items in this category.")
        return
    
    for item in pbc_items:
        priority_class = f"priority-{item.priority.lower()}"
        
        with st.container():
            st.markdown(f'<div class="pbc-item-card {priority_class}">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"### {item.item_number}. {item.item_description}")
                st.markdown(f"**Category:** {item.category} | **Priority:** {priority_badge(item.priority)}", unsafe_allow_html=True)
                st.markdown(f"**Why Needed:** {item.why_needed}")
                st.markdown(f"**Status:** {status_badge(item.status.value)}", unsafe_allow_html=True)
            
            with col2:
                if item.status in [PBCStatus.PENDING, PBCStatus.IN_PROGRESS]:
                    if st.button("📤 Upload", key=f"upload_btn_{item.pbc_id}"):
                        st.session_state.upload_pbc_id = item.pbc_id
                        st.rerun()
            
            # Show existing documents
            documents = db.query(PBCDocument).filter(PBCDocument.pbc_id == item.pbc_id).all()
            
            if documents:
                st.markdown("**📎 Uploaded Documents:**")
                for doc in documents:
                    uploader = db.query(User).filter(User.user_id == doc.uploaded_by).first()
                    
                    col_doc1, col_doc2, col_doc3 = st.columns([3, 1, 1])
                    with col_doc1:
                        st.markdown(f"- {doc.filename} ({format_file_size(doc.file_size)})")
                        st.caption(f"Uploaded by {uploader.full_name if uploader else 'Unknown'} on {doc.uploaded_at.strftime('%d %b %Y, %H:%M')}")
                    with col_doc2:
                        if doc.is_verified:
                            st.success("✅ Verified")
                        else:
                            st.warning("⏳ Pending Review")
                    with col_doc3:
                        pass  # Could add download button here
                    
                    # Show AI analysis if available
                    if doc.ai_analysis:
                        with st.expander("🤖 AI Analysis"):
                            try:
                                analysis = json.loads(doc.ai_analysis)
                                st.markdown(f"**Document Type:** {analysis.get('document_type', 'Unknown')}")
                                st.markdown(f"**Relevance Score:** {analysis.get('relevance_score', 0)}/100")
                                st.markdown(f"**Recommendation:** {analysis.get('recommendation', 'N/A')}")
                                if analysis.get('key_info'):
                                    st.markdown("**Key Information Found:**")
                                    for info in analysis.get('key_info', []):
                                        st.markdown(f"- {info}")
                            except:
                                st.markdown(doc.ai_analysis)
            
            # Upload interface
            if hasattr(st.session_state, 'upload_pbc_id') and st.session_state.upload_pbc_id == item.pbc_id:
                st.markdown("---")
                st.markdown("### 📤 Upload Documents")
                
                uploaded_files = st.file_uploader(
                    "Select files to upload (PDF, Excel, Word, Images)",
                    type=['pdf', 'xlsx', 'xls', 'docx', 'doc', 'jpg', 'jpeg', 'png'],
                    accept_multiple_files=True,
                    key=f"uploader_{item.pbc_id}"
                )
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("✅ Submit Documents", key=f"submit_{item.pbc_id}"):
                        if not uploaded_files:
                            st.error("❌ Please select at least one file")
                        else:
                            with st.spinner("🤖 Uploading and analyzing with AI..."):
                                try:
                                    for uploaded_file in uploaded_files:
                                        file_bytes = uploaded_file.read()
                                        
                                        # Analyze with AI
                                        ai_analysis = analyze_uploaded_document(
                                            file_bytes,
                                            uploaded_file.name,
                                            item.item_description
                                        )
                                        
                                        # Save document
                                        new_doc = PBCDocument(
                                            pbc_id=item.pbc_id,
                                            filename=uploaded_file.name,
                                            file_size=len(file_bytes),
                                            file_type=uploaded_file.type,
                                            uploaded_by=st.session_state.user_id,
                                            ai_analysis=json.dumps(ai_analysis)
                                        )
                                        db.add(new_doc)
                                    
                                    # Update PBC status
                                    if item.status == PBCStatus.PENDING:
                                        item.status = PBCStatus.IN_PROGRESS
                                    elif item.status == PBCStatus.IN_PROGRESS:
                                        item.status = PBCStatus.SUBMITTED
                                    
                                    item.updated_at = datetime.utcnow()
                                    
                                    db.commit()
                                    
                                    st.success(f"✅ {len(uploaded_files)} document(s) uploaded and analyzed!")
                                    st.balloons()
                                    
                                    del st.session_state.upload_pbc_id
                                    
                                    import time
                                    time.sleep(2)
                                    st.rerun()
                                
                                except Exception as e:
                                    db.rollback()
                                    st.error(f"❌ Error: {str(e)}")
                
                with col_btn2:
                    if st.button("❌ Cancel", key=f"cancel_{item.pbc_id}"):
                        del st.session_state.upload_pbc_id
                        st.rerun()
            
            # Comments section
            comments = db.query(PBCComment).filter(PBCComment.pbc_id == item.pbc_id).order_by(PBCComment.created_at.desc()).all()
            
            if comments:
                with st.expander(f"💬 Comments ({len(comments)})"):
                    for comment in comments:
                        commenter = db.query(User).filter(User.user_id == comment.user_id).first()
                        st.markdown(f"**{commenter.full_name if commenter else 'Unknown'}** • {comment.created_at.strftime('%d %b, %H:%M')}")
                        st.markdown(comment.comment_text)
                        st.markdown("---")
            
            # Add comment
            with st.expander("💬 Add Comment"):
                comment_text = st.text_area("Your comment", key=f"comment_{item.pbc_id}", placeholder="Ask a question or provide additional information...")
                if st.button("Send Comment", key=f"send_comment_{item.pbc_id}"):
                    if comment_text:
                        new_comment = PBCComment(
                            pbc_id=item.pbc_id,
                            user_id=st.session_state.user_id,
                            comment_text=comment_text
                        )
                        db.add(new_comment)
                        db.commit()
                        st.success("✅ Comment added!")
                        st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

def show_client_settings(db, client_profile):
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("# ⚙️ Settings")
    st.markdown("---")
    
    user = db.query(User).filter(User.user_id == st.session_state.user_id).first()
    
    tab1, tab2 = st.tabs(["Company Profile", "Security"])
    
    with tab1:
        st.markdown("### 🏢 Company Information")
        with st.form("company_form"):
            company_name = st.text_input("Company Name", value=client_profile.company_name)
            gstin = st.text_input("GSTIN", value=client_profile.gstin or "")
            full_name = st.text_input("Your Name", value=user.full_name)
            
            if st.form_submit_button("💾 Save Changes"):
                try:
                    client_profile.company_name = company_name
                    client_profile.gstin = gstin if gstin else None
                    user.full_name = full_name
                    db.commit()
                    st.success("✅ Profile updated successfully!")
                except Exception as e:
                    db.rollback()
                    st.error(f"❌ Error: {str(e)}")
        
        st.markdown("---")
        st.markdown("### 🔗 Linked CA")
        ca = db.query(CAProfile).filter(CAProfile.ca_id == client_profile.ca_id).first()
        if ca:
            st.info(f"**CA Firm:** {ca.firm_name}\n\n**Membership No:** {ca.membership_no}")
        else:
            st.warning("Not linked to any CA yet")
    
    with tab2:
        st.markdown("### 🔒 Security")
        with st.form("client_password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("🔑 Change Password"):
                if not verify_password(current_password, user.password_hash):
                    st.error("❌ Current password is incorrect")
                elif new_password != confirm_password:
                    st.error("❌ New passwords don't match")
                elif len(new_password) < 8:
                    st.error("❌ Password must be at least 8 characters")
                else:
                    try:
                        user.password_hash = hash_password(new_password)
                        db.commit()
                        st.success("✅ Password changed successfully!")
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Error: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# MAIN APPLICATION ROUTER
# ============================================================================

def main():
    # Route based on authentication state
    if not st.session_state.authenticated:
        # Public pages
        if st.session_state.current_page == "landing":
            show_landing_page()
        elif st.session_state.current_page == "signup":
            show_signup_page()
        elif st.session_state.current_page == "signin":
            show_signin_page()
    else:
        # Authenticated pages
        if st.session_state.role == "ca":
            show_ca_dashboard()
        elif st.session_state.role == "client":
            show_client_dashboard()

if __name__ == "__main__":
    main()
