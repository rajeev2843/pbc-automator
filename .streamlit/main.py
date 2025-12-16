import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import *
from gemini_ai import *
from utils import *
from tb_mapper import TrialBalanceToPBCMapper  # Import the mapper
import io
import json
from io import BytesIO

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
    # Hero Section
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown('<h1 class="hero-title">Smart Audit Room</h1>', unsafe_allow_html=True)
        st.markdown("""
        <h2 style='color: #BAE6FD; font-weight: 400; margin-bottom: 30px; text-shadow: 0 2px 4px rgba(0,0,0,0.3);'>
        Automate Your PBC Process with AI
        </h2>
        <p style='font-size: 18px; color: #E0F2FE; line-height: 1.8; margin-bottom: 30px; text-shadow: 0 1px 2px rgba(0,0,0,0.2);'>
        Transform your audit workflow with intelligent document management. 
        Generate comprehensive PBC lists from Trial Balance in seconds, 
        track submissions in real-time, and verify documents with AI-powered analysis.
        </p>
        """, unsafe_allow_html=True)
        
        # Buttons
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
        <div style='background: linear-gradient(135deg, #0EA5E9 0%, #06B6D4 50%, #14B8A6 100%); 
                    padding: 40px; border-radius: 20px; text-align: center;
                    box-shadow: 0 8px 30px rgba(6, 182, 212, 0.4);
                    border: 2px solid rgba(94, 234, 212, 0.3);'>
            <div style='font-size: 64px; margin-bottom: 20px;'>📋</div>
            <h3 style='color: white; margin-bottom: 15px; text-shadow: 0 2px 4px rgba(0,0,0,0.2); font-weight: 700;'>Built for CAs</h3>
            <p style='font-size: 16px; font-weight: 600; line-height: 1.6;'>
                <span style='color: #0A1929 !important;'>Designed specifically for Chartered Accountants and their clients to streamline the audit documentation process.</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Features Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center; margin-bottom: 40px; color: #E0F2FE; text-shadow: 0 2px 4px rgba(0,0,0,0.3);'>🌟 Powerful Features</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="icon-large">🤖</div>
            <h3>AI-Powered PBC Generation</h3>
            <p style='line-height: 1.6;'>
            Upload Trial Balance and get a comprehensive, intelligent PBC list 
            in seconds using advanced AI mapping.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="icon-large">📄</div>
            <h3>Smart Document Analysis</h3>
            <p style='line-height: 1.6;'>
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
            <p style='line-height: 1.6;'>
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
            <p style='line-height: 1.6;'>
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
            <p style='line-height: 1.6;'>
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
            <p style='line-height: 1.6;'>
            Save 10+ hours per audit. What took days now takes minutes 
            with intelligent automation.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # How It Works
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center; margin-bottom: 40px; color: #E0F2FE; text-shadow: 0 2px 4px rgba(0,0,0,0.3);'>🔄 How It Works</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(12, 45, 72, 0.9), rgba(12, 74, 110, 0.9)); 
                    padding: 30px; border-radius: 15px; margin-bottom: 20px;
                    border: 2px solid rgba(6, 182, 212, 0.4);
                    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
                    backdrop-filter: blur(10px);'>
            <h3 style='color: #5EEAD4; text-shadow: 0 2px 4px rgba(0,0,0,0.3);'>👨‍💼 For CAs</h3>
            <ol style='line-height: 2; color: #BAE6FD; font-size: 16px; text-shadow: 0 1px 2px rgba(0,0,0,0.2);'>
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
        <div style='background: linear-gradient(135deg, rgba(12, 45, 72, 0.9), rgba(12, 74, 110, 0.9)); 
                    padding: 30px; border-radius: 15px; margin-bottom: 20px;
                    border: 2px solid rgba(20, 184, 166, 0.4);
                    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
                    backdrop-filter: blur(10px);'>
            <h3 style='color: #5EEAD4; text-shadow: 0 2px 4px rgba(0,0,0,0.3);'>🏢 For Clients</h3>
            <ol style='line-height: 2; color: #BAE6FD; font-size: 16px; text-shadow: 0 1px 2px rgba(0,0,0,0.2);'>
                <li>Receive PBC list from your CA</li>
                <li>See exactly what's needed and why</li>
                <li>Upload documents with drag-and-drop</li>
                <li>AI analyzes and confirms completeness</li>
                <li>Get real-time feedback from CA</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    # CTA Section with gap
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #0EA5E9 0%, #06B6D4 50%, #14B8A6 100%); 
                text-align: center; padding: 60px; border-radius: 20px;
                box-shadow: 0 12px 40px rgba(6, 182, 212, 0.5);
                border: 2px solid rgba(94, 234, 212, 0.4);'>
        <h2 style='color: white; font-size: 36px; margin-bottom: 20px; text-shadow: 0 2px 4px rgba(0,0,0,0.2); font-weight: 700;'>
        Ready to Transform Your Audit Process?
        </h2>
        <p style='font-size: 18px; font-weight: 600; margin-bottom: 0; line-height: 1.6;'>
            <span style='color: #0A1929 !important;'>Join forward-thinking CAs who've already automated their PBC workflow</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Gap between card and button
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🎯 Start Free Today", key="cta_button", use_container_width=True):
            st.session_state.current_page = "signup"
            st.rerun()
    
    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; color: #7DD3FC; padding: 20px;'>
        <p style='font-size: 14px; opacity: 0.8;'>
        Built for ICAI Aurathon 2025 | Powered by AI & Machine Learning
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
                firm_registration_no = st.text_input("Firm Registration Number (Optional)", placeholder="e.g., 123456W")
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
        st.markdown(f"<h3 style='color: #E2E8F0;'>👨‍💼 {user.full_name}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #E2E8F0; font-weight: 700; font-size: 16px;'>{ca_profile.firm_name}</p>", unsafe_allow_html=True)
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
            accounting_std = st.selectbox("Accounting Standard *", ["Indian GAAP", "Ind AS"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📊 Upload Trial Balance")
        
        # Sample file downloads
        col_info1, col_info2 = st.columns([2, 2])
        with col_info1:
            st.markdown("Upload Trial Balance to auto-generate PBC list using AI")
        with col_info2:
            # Create sample file
            sample_df = pd.DataFrame({
                'Account Name': ['Cash in Hand', 'Bank - SBI Current Account', 'Sales Revenue', 'Rent Expense', 'Trade Payables'],
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
                pass
        
        tb_file = st.file_uploader(
            "Trial Balance (Excel/CSV)",
            type=['xlsx', 'xls', 'csv'],
            help="Upload Trial Balance with columns: Account Name, Debit, Credit"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
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
                        with st.spinner("🤖 Creating project and generating PBC list with AI Mapper..."):
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
                                total_debit=float(tb_df['Debit'].sum()),
                                total_credit=float(tb_df['Credit'].sum()),
                                account_count=len(tb_df)
                            )
                            db.add(tb_record)
                            
                            # === USE TB MAPPER INSTEAD OF GEMINI ===
                            # Initialize mapper based on audit type
                            mapper_audit_type = "Tax" if audit_type == "Tax Audit" else "Stat"
                            mapper = TrialBalanceToPBCMapper(
                                audit_type=mapper_audit_type,
                                accounting_standard=accounting_std
                            )
                            
                            # Map ledgers to PBC categories
                            mapping_result = mapper.process_trial_balance(
                                df=tb_df,
                                ledger_column='Account Name',
                                debit_column='Debit',
                                credit_column='Credit',
                                threshold=60
                            )
                            
                            # Get summary
                            summary = mapper.generate_pbc_summary(mapping_result)
                            
                            # Group by PBC category and create PBC items
                            pbc_categories = mapping_result[
                                mapping_result['PBC_Category'] != 'UNMAPPED - Manual Review Required'
                            ]['PBC_Category'].unique()
                            
                            pbc_item_number = 1
                            for pbc_category in pbc_categories:
                                # Get ledgers in this category
                                category_ledgers = mapping_result[
                                    mapping_result['PBC_Category'] == pbc_category
                                ]
                                
                                # Calculate total amounts
                                total_debit = category_ledgers['Debit_Amount'].sum() if 'Debit_Amount' in category_ledgers.columns else 0
                                total_credit = category_ledgers['Credit_Amount'].sum() if 'Credit_Amount' in category_ledgers.columns else 0
                                
                                # Generate description based on category
                                description = generate_pbc_description(pbc_category, category_ledgers)
                                why_needed = generate_why_needed(pbc_category)
                                priority = determine_priority(pbc_category, total_debit, total_credit)
                                
                                # Create PBC item
                                pbc_item = PBCItem(
                                    project_id=new_project.project_id,
                                    item_number=pbc_item_number,
                                    category=get_major_category(pbc_category),
                                    item_description=description,
                                    why_needed=why_needed,
                                    priority=priority,
                                    status=PBCStatus.PENDING,
                                    ai_generated=True
                                )
                                db.add(pbc_item)
                                pbc_item_number += 1
                            
                            db.commit()
                            
                            # Show success with summary
                            st.success(f"✅ Project created successfully!")
                            st.balloons()
                            
                            # Show mapping summary
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Ledgers", summary['total_ledgers'])
                            with col2:
                                st.metric("PBC Items Generated", len(pbc_categories))
                            with col3:
                                st.metric("Success Rate", f"{summary['success_rate']}%")
                            
                            st.info(f"✓ {summary['high_confidence']} High Confidence | {summary['medium_confidence']} Medium | {summary['low_confidence']} Need Review")
                            
                            import time
                            time.sleep(3)
                            st.session_state.selected_project = new_project.project_id
                            st.rerun()
                
                except Exception as e:
                    db.rollback()
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())
    
    st.markdown("</div>", unsafe_allow_html=True)


def generate_pbc_description(pbc_category: str, ledgers_df: pd.DataFrame) -> str:
    """Generate PBC description based on category and ledgers"""
    
    ledger_names = ", ".join(ledgers_df['Original_Ledger_Name'].head(3).tolist())
    if len(ledgers_df) > 3:
        ledger_names += f" and {len(ledgers_df) - 3} more"
    
    category_descriptions = {
        "Fixed Assets": f"Fixed asset register with details of {ledger_names}. Include purchase invoices, depreciation schedule, and disposal records.",
        "Bank": f"Bank statements and reconciliations for {ledger_names}. Include bank confirmation letters.",
        "Cash": "Cash book, petty cash records, and cash count certificates as on year-end.",
        "Inventories": f"Stock statement with valuation details for {ledger_names}. Include physical verification reports.",
        "Trade Receivables": f"Debtors list with ageing for {ledger_names}. Include confirmation letters and subsequent collection details.",
        "Trade Payables": f"Creditors list with ageing for {ledger_names}. Include confirmation letters and MSME classification.",
        "Loans": f"Loan agreements, sanction letters, and repayment schedules for {ledger_names}.",
        "GST": "GST returns (GSTR-1, GSTR-3B), GST reconciliation, and ITC working papers.",
        "Sales": "Sales register, invoices, and supporting documents. Include GST reconciliation.",
        "Expenses": f"Expense vouchers and supporting documents for {ledger_names}.",
        "Salary": "Salary sheets, PF/ESI challans, and Form 16 for employees.",
    }
    
    # Match category to description
    for key, desc in category_descriptions.items():
        if key.lower() in pbc_category.lower():
            return desc
    
    # Default description
    return f"Supporting documents and schedules for {pbc_category}. Includes ledger extracts and vouchers."


def generate_why_needed(pbc_category: str) -> str:
    """Generate why needed explanation"""
    
    explanations = {
        "Fixed Assets": "To verify existence, ownership, valuation and completeness of fixed assets as per AS-10/Ind AS 16",
        "Bank": "To confirm existence and accuracy of bank balances and reconcile book balances with bank statements",
        "Cash": "To verify existence of cash and ensure proper controls over cash handling",
        "Inventories": "To verify existence, ownership, condition and valuation of inventory as per AS-2/Ind AS 2",
        "Trade Receivables": "To confirm existence, recoverability and completeness of receivables",
        "Trade Payables": "To verify completeness and accuracy of liabilities and MSME compliance",
        "Loans": "To verify terms, conditions, repayment schedule and compliance with loan covenants",
        "GST": "To verify GST compliance and ensure accurate reporting of input and output tax",
        "Sales": "To verify revenue recognition, cut-off and ensure completeness of sales",
        "Expenses": "To verify nature, authorization and proper accounting of expenses",
        "Salary": "To verify employee costs and compliance with statutory requirements",
    }
    
    for key, explanation in explanations.items():
        if key.lower() in pbc_category.lower():
            return explanation
    
    return f"To verify, validate and ensure proper accounting treatment of {pbc_category}"


def determine_priority(pbc_category: str, debit: float, credit: float) -> str:
    """Determine priority based on category and amounts"""
    
    amount = max(abs(debit), abs(credit))
    
    # High priority categories
    high_priority = ["bank", "cash", "sales", "revenue", "receivable", "payable", "loan", "borrowing"]
    if any(hp in pbc_category.lower() for hp in high_priority):
        return "High"
    
    # High priority for large amounts
    if amount > 1000000:  # > 10 lakhs
        return "High"
    
    # Medium priority
    if amount > 100000:  # > 1 lakh
        return "Medium"
    
    return "Low"


def get_major_category(pbc_category: str) -> str:
    """Get major category for grouping"""
    
    category_lower = pbc_category.lower()
    
    if any(term in category_lower for term in ['fixed asset', 'intangible', 'capital wip', 'ppe']):
        return 'Fixed Assets'
    elif 'inventor' in category_lower or any(term in category_lower for term in ['raw material', 'wip', 'finished', 'stock']):
        return 'Inventories'
    elif 'receivable' in category_lower or 'debtor' in category_lower:
        return 'Trade Receivables'
    elif any(term in category_lower for term in ['cash', 'bank']):
        return 'Cash & Bank'
    elif 'payable' in category_lower or 'creditor' in category_lower:
        return 'Trade Payables'
    elif any(term in category_lower for term in ['share capital', 'equity', 'reserve', 'retained']):
        return 'Equity'
    elif 'borrowing' in category_lower or 'loan' in category_lower:
        return 'Borrowings'
    elif any(term in category_lower for term in ['gst', 'tds', 'tax']):
        return 'Statutory Compliance'
    elif any(term in category_lower for term in ['sales', 'revenue', 'income']):
        return 'Revenue'
    elif any(term in category_lower for term in ['expense', 'cost', 'depreciation']):
        return 'Expenses'
    else:
        return 'Other'


def show_ca_clients(db, ca_profile):
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("# 👥 My Clients")
    st.markdown("---")
    
    clients = db.query(ClientProfile).filter(ClientProfile.ca_id == ca_profile.ca_id).all()
    
    st.markdown(f"### 📊 Total Clients: {len(clients)}")
    
    if not clients:
        st.info("No clients yet. Share your invite code to get started!")
    else:
        for client in clients:
            user = db.query(User).filter(User.user_id == client.user_id).first()
            projects = db.query(AuditProject).filter(AuditProject.client_id == client.client_id).all()
            
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
    
    st.markdown("</div>", unsafe_allow_html=True)


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
# CLIENT DASHBOARD (Keep existing code)
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


# [Keep all other existing client functions unchanged]
# show_client_onboarding, show_client_dashboard_home, show_client_pbc_lists, 
# display_pbc_items_for_client, show_client_settings

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
